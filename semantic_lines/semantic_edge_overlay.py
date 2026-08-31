"""First interactive consumer for :mod:`semantic_edges`.

This intentionally small overlay proves the semantic-edge pipeline in the
active 3D viewport.  It projects candidates into screen space and batches
them for GPU drawing.  Visibility/hidden-line splitting is deliberately not
part of this first slice: every selected semantic edge is drawn.
"""

from __future__ import annotations

from dataclasses import dataclass
import time

import bpy
import gpu
from bpy.props import (BoolProperty, EnumProperty, FloatProperty,
                       FloatVectorProperty, IntProperty)
from mathutils import Vector
from bpy_extras import view3d_utils
from gpu_extras.batch import batch_for_shader

try:  # Allows the Blender-headless tests to import this module directly.
    from . import semantic_edges
except ImportError:
    import semantic_edges


TEST_COLLECTION_NAME = "HB Semantic Edge Tests"
# Screen-space, muted technical-ink styling.  POLYLINE_UNIFORM_COLOR keeps
# this thickness stable when zooming and rasterizes considerably more cleanly
# than the legacy GPU line-width state.
OVERLAY_COLOR = (0.12, 0.19, 0.25, 0.92)
OVERLAY_LINE_WIDTH = 1.25
HIDDEN_COLOR = (0.12, 0.19, 0.25, 0.48)
HIDDEN_LINE_WIDTH = 0.9
HIDDEN_DASH_LENGTH = 5.0
HIDDEN_GAP_LENGTH = 4.0
ALIGNED_LINE_TOLERANCE = 1.0
ALIGNED_COVERAGE_TOLERANCE = 0.02

VISIBLE = 'VISIBLE'
HIDDEN = 'HIDDEN'

_draw_handle = None
_projection_cache = {'key': None, 'segments': ()}
_viewport_performance = {'backend': 'Waiting for redraw', 'edges': 0, 'samples': 0}
_navigation_preview = {
    'view_key': None,
    'last_change': 0.0,
    'settled': True,
    'timer_pending': False,
}
# Extraction is independent of the viewport.  Keeping the world-space edge
# list means orbiting, panning, and zooming do not repeatedly walk every mesh
# topology in a furnished scene.
_semantic_edge_cache = {'scene_pointer': None, 'by_object': {}}

SCREEN_CULL_MARGIN = 2.0
VISIBILITY_PIXELS_PER_SAMPLE = 96.0
VISIBILITY_MIN_SAMPLES = 3
HIDDEN_INDEX_CELL_SIZE = 128.0
NAVIGATION_SETTLE_SECONDS = 0.18


@dataclass(frozen=True)
class ProjectedEdgeSegment:
    """A screen-space portion of a semantic edge and its visibility."""

    source_edge_uid: str
    start: tuple[float, float]
    end: tuple[float, float]
    visibility: str


def _redraw_viewports(_self=None, _context=None):
    """Request a redraw after an overlay setting changes."""
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()


def _invalidate_projection_cache(_scene=None, _depsgraph=None):
    _projection_cache['key'] = None
    _projection_cache['segments'] = ()


def _finish_navigation_preview():
    """Request full hidden-line work only after viewport motion has stopped."""
    state = _navigation_preview
    if time.monotonic() - state['last_change'] < NAVIGATION_SETTLE_SECONDS:
        return NAVIGATION_SETTLE_SECONDS
    state['settled'] = True
    state['timer_pending'] = False
    _invalidate_projection_cache()
    _redraw_viewports()
    return None


def _navigation_is_active(region, region_3d):
    """Track changing view matrices and defer expensive hidden-line solving."""
    state = _navigation_preview
    view_key = (region.as_pointer(),
                tuple(round(value, 7) for row in region_3d.perspective_matrix
                      for value in row))
    if state['view_key'] == view_key:
        return not state['settled']
    state['view_key'] = view_key
    state['last_change'] = time.monotonic()
    state['settled'] = False
    if not state['timer_pending']:
        state['timer_pending'] = True
        bpy.app.timers.register(_finish_navigation_preview,
                                first_interval=NAVIGATION_SETTLE_SECONDS)
    return True


def _invalidate_semantic_edge_cache(_scene=None, _depsgraph=None):
    """Discard extracted edges only when evaluated mesh content changes."""
    _invalidate_projection_cache()
    _semantic_edge_cache['scene_pointer'] = None
    _semantic_edge_cache['by_object'] = {}


def _depsgraph_update_post(_scene, depsgraph):
    """Avoid cache churn from unrelated Blender dependency-graph updates."""
    for update in depsgraph.updates:
        updated_id = update.id
        if isinstance(updated_id, bpy.types.Mesh):
            _invalidate_semantic_edge_cache()
            return
        if isinstance(updated_id, bpy.types.Object) and updated_id.type == 'MESH':
            _invalidate_semantic_edge_cache()
            return
        # Collection visibility can change which mesh objects are candidates.
        if isinstance(updated_id, bpy.types.Collection):
            _invalidate_semantic_edge_cache()
            return


def line_color(scene):
    """The user-selected technical-ink color, with a safe module fallback."""
    return tuple(getattr(scene, 'hb_semantic_edge_line_color', OVERLAY_COLOR))


def hidden_line_color(color):
    """Keep hidden lines visually subordinate while preserving hue."""
    hidden_alpha_ratio = HIDDEN_COLOR[3] / OVERLAY_COLOR[3]
    return (color[0], color[1], color[2], color[3] * hidden_alpha_ratio)


def viewport_line_width(scene):
    return (getattr(scene, 'hb_semantic_edge_line_weight', OVERLAY_LINE_WIDTH)
            * getattr(scene, 'hb_semantic_edge_viewport_weight_multiplier', 1.0))


def render_line_width(scene):
    return (getattr(scene, 'hb_semantic_edge_line_weight', OVERLAY_LINE_WIDTH)
            * getattr(scene, 'hb_semantic_edge_render_weight_multiplier', 1.25))


def hidden_line_width(visible_width):
    return visible_width * (HIDDEN_LINE_WIDTH / OVERLAY_LINE_WIDTH)


def _overlay_candidates(context):
    selected_only = context.scene.hb_semantic_edges_selected_only
    selected = set(context.selected_objects) if selected_only else None
    return [obj for obj in context.scene.objects
            if obj.type == 'MESH'
            and obj.visible_get(view_layer=context.view_layer)
            and (selected is None or obj in selected)]


def _cached_semantic_edges(context, depsgraph):
    """Return extracted edge lists for the current candidates without rebuilds."""
    cache = _semantic_edge_cache
    scene_pointer = context.scene.as_pointer()
    if cache['scene_pointer'] != scene_pointer:
        cache['scene_pointer'] = scene_pointer
        cache['by_object'] = {}
    edge_lists = []
    for obj in _overlay_candidates(context):
        object_pointer = obj.as_pointer()
        edges = cache['by_object'].get(object_pointer)
        if edges is None:
            edges = tuple(semantic_edges.extract_semantic_edges(obj, depsgraph))
            cache['by_object'][object_pointer] = edges
        edge_lists.append(edges)
    return edge_lists


def visibility_runs(samples):
    """Turn ordered samples into visible/hidden parameter intervals.

    A visibility change between the first two or final two samples is snapped
    to the edge endpoint. At a model corner the endpoint sample commonly sees
    its own adjacent face while the next sample is genuinely occluded;
    midpoint splitting would otherwise let the solid line overrun the corner.
    """
    if not samples:
        return ()
    if len(samples) == 1:
        return ((0.0, 1.0, VISIBLE if samples[0] else HIDDEN),)
    runs, state, start = [], samples[0], 0.0
    last_index = len(samples) - 1
    for index in range(1, len(samples)):
        if samples[index] == state:
            continue
        if index == 1:
            boundary = 0.0
        elif index == last_index:
            boundary = 1.0
        else:
            boundary = (index - 0.5) / last_index
        if boundary > start:
            runs.append((start, boundary, VISIBLE if state else HIDDEN))
        state, start = samples[index], boundary
    if start < 1.0:
        runs.append((start, 1.0, VISIBLE if state else HIDDEN))
    return tuple(runs)


def dashed_screen_segments(start, end, dash_length=HIDDEN_DASH_LENGTH,
                           gap_length=HIDDEN_GAP_LENGTH):
    """Create deterministic dash segments in viewport pixels."""
    dx, dy = end[0] - start[0], end[1] - start[1]
    length = (dx * dx + dy * dy) ** 0.5
    if length <= 1.0e-6:
        return ()
    ux, uy = dx / length, dy / length
    out, position = [], 0.0
    while position < length:
        dash_end = min(position + dash_length, length)
        out.append(((start[0] + ux * position, start[1] + uy * position),
                    (start[0] + ux * dash_end, start[1] + uy * dash_end)))
        position = dash_end + gap_length
    return tuple(out)


def hidden_segment_is_covered(hidden, visible_segments,
                              line_tolerance=ALIGNED_LINE_TOLERANCE):
    """True if visible collinear segments cover all of a hidden segment.

    This is a screen-space drafting cleanup rule.  It only suppresses an
    already-hidden segment, so a nearby parallel line or visible model detail
    is never removed merely because it sits close to another line.
    """
    ax, ay = hidden.start
    bx, by = hidden.end
    dx, dy = bx - ax, by - ay
    length_sq = dx * dx + dy * dy
    if length_sq <= 1.0e-6:
        return True
    length = length_sq ** 0.5
    intervals = []
    for visible in visible_segments:
        if visible.source_edge_uid == hidden.source_edge_uid:
            continue
        vx0, vy0 = visible.start
        vx1, vy1 = visible.end
        # Perpendicular distance of both endpoints from hidden's supporting
        # line.  The threshold is in pixels and matches visual alignment.
        distance0 = abs((vx0 - ax) * dy - (vy0 - ay) * dx) / length
        distance1 = abs((vx1 - ax) * dy - (vy1 - ay) * dx) / length
        if max(distance0, distance1) > line_tolerance:
            continue
        t0 = ((vx0 - ax) * dx + (vy0 - ay) * dy) / length_sq
        t1 = ((vx1 - ax) * dx + (vy1 - ay) * dy) / length_sq
        start, end = max(0.0, min(t0, t1)), min(1.0, max(t0, t1))
        if end > start:
            intervals.append((start, end))
    if not intervals:
        return False

    intervals.sort()
    covered_start, covered_end = intervals[0]
    if covered_start > ALIGNED_COVERAGE_TOLERANCE:
        return False
    for start, end in intervals[1:]:
        if start > covered_end + ALIGNED_COVERAGE_TOLERANCE:
            return False
        covered_end = max(covered_end, end)
    return covered_end >= 1.0 - ALIGNED_COVERAGE_TOLERANCE


def _segment_grid_cells(segment, cell_size=HIDDEN_INDEX_CELL_SIZE):
    """Yield conservative screen-space grid cells occupied by a segment."""
    min_x = min(segment.start[0], segment.end[0])
    max_x = max(segment.start[0], segment.end[0])
    min_y = min(segment.start[1], segment.end[1])
    max_y = max(segment.start[1], segment.end[1])
    start_x = int(min_x // cell_size)
    end_x = int(max_x // cell_size)
    start_y = int(min_y // cell_size)
    end_y = int(max_y // cell_size)
    for x in range(start_x, end_x + 1):
        for y in range(start_y, end_y + 1):
            yield (x, y)


def suppress_aligned_hidden_segments(segments):
    """Drop hidden segments fully coincident with visible technical lines."""
    visible = [segment for segment in segments if segment.visibility == VISIBLE]
    # The original drafting rule compared every hidden segment with every
    # visible segment.  A coarse spatial index preserves the rule while
    # making large cabinet/room scenes scale with nearby lines instead of all
    # lines in the viewport.
    visible_index = {}
    for segment in visible:
        for cell in _segment_grid_cells(segment):
            visible_index.setdefault(cell, []).append(segment)

    def nearby_visible(segment):
        nearby, seen = [], set()
        for cell in _segment_grid_cells(segment):
            for candidate in visible_index.get(cell, ()):
                pointer = id(candidate)
                if pointer not in seen:
                    seen.add(pointer)
                    nearby.append(candidate)
        return nearby

    return tuple(segment for segment in segments
                 if segment.visibility != HIDDEN
                 or not hidden_segment_is_covered(segment, nearby_visible(segment)))


def _world_point_at(edge, t):
    return tuple(edge.start[i] + (edge.end[i] - edge.start[i]) * t
                 for i in range(3))


def _orthographic_view_ray(region_3d, target, clip_end):
    """Construct a stable parallel viewport ray through ``target``.

    ``region_2d_to_origin_3d`` is intentionally depth-dependent for some
    orthographic region configurations.  Starting a long way behind the
    target on the actual view vector keeps every isometric sample on the
    same parallel ray and matches the render-camera implementation.
    """
    direction = (region_3d.view_matrix.inverted().to_3x3()
                 @ Vector((0.0, 0.0, -1.0))).normalized()
    origin = Vector(target) - direction * max(clip_end, 1.0)
    return origin, direction, max(clip_end, 1.0)


def _sample_is_visible(context, region, region_3d, target, tolerance):
    """True when the sample is the first surface along its viewport ray."""
    target = Vector(target)
    if region_3d.is_perspective:
        screen = view3d_utils.location_3d_to_region_2d(region, region_3d, target)
        if screen is None:
            return None
        origin = view3d_utils.region_2d_to_origin_3d(region, region_3d, screen)
        direction = view3d_utils.region_2d_to_vector_3d(region, region_3d, screen)
        target_distance = (target - origin).length
    else:
        clip_end = getattr(context.space_data, 'clip_end', 1000.0)
        origin, direction, target_distance = _orthographic_view_ray(
            region_3d, target, clip_end)
    hit, location, _normal, _face_index, _object, _matrix = context.scene.ray_cast(
        context.evaluated_depsgraph_get(), origin, direction,
        distance=target_distance + tolerance)
    if not hit:
        return True
    # Adjacent faces can be hit at the same depth as their edge.  They are
    # not occluders; only a surface materially closer to the camera hides it.
    return (location - origin).length >= target_distance - tolerance


def _edge_visibility_runs(context, region, region_3d, edge, sample_count):
    length = (Vector(edge.end) - Vector(edge.start)).length
    tolerance = max(1.0e-5, length * 1.0e-5)
    samples = []
    for index in range(sample_count):
        target = _world_point_at(edge, index / (sample_count - 1))
        result = _sample_is_visible(context, region, region_3d, target, tolerance)
        samples.append(True if result is None else result)
    return visibility_runs(samples)


def _segment_intersects_region(start, end, region, margin=SCREEN_CULL_MARGIN):
    """Conservative screen-space rejection for edges outside the viewport."""
    return not (max(start.x, end.x) < -margin
                or min(start.x, end.x) > region.width + margin
                or max(start.y, end.y) < -margin
                or min(start.y, end.y) > region.height + margin)


def visibility_sample_count(max_samples, start, end):
    """Scale hidden-line samples to the edge's visible pixel length.

    The UI value remains a quality ceiling.  Short projected edges cannot
    visually benefit from seventeen samples, while long drawing edges retain
    the higher precision needed for useful hidden-line transitions.
    """
    pixel_length = ((end.x - start.x) ** 2 + (end.y - start.y) ** 2) ** 0.5
    needed = int(pixel_length / VISIBILITY_PIXELS_PER_SAMPLE) + 2
    return max(VISIBILITY_MIN_SAMPLES, min(max_samples, needed))


def _projection_cache_key(context, region, region_3d):
    selected = tuple(sorted(obj.name for obj in context.selected_objects)) \
        if context.scene.hb_semantic_edges_selected_only else ()
    return (context.scene.as_pointer(), region.width, region.height,
            context.scene.hb_semantic_edge_visibility_mode,
            context.scene.hb_semantic_edge_sample_count,
            context.scene.hb_semantic_edges_suppress_aligned_hidden,
            context.scene.hb_semantic_edges_selected_only, selected,
            tuple(round(value, 7) for row in region_3d.perspective_matrix
                  for value in row))


def projected_segments(context, region, region_3d):
    """Project semantic edges and, on demand, classify sampled visibility."""
    key = _projection_cache_key(context, region, region_3d)
    if _projection_cache['key'] == key:
        return _projection_cache['segments']

    depsgraph = context.evaluated_depsgraph_get()
    mode = context.scene.hb_semantic_edge_visibility_mode
    navigation_preview = _navigation_is_active(region, region_3d)
    effective_mode = 'ALL' if navigation_preview else mode
    segments = []
    candidates = []
    for edges in _cached_semantic_edges(context, depsgraph):
        for edge in edges:
            edge_start = view3d_utils.location_3d_to_region_2d(
                region, region_3d, edge.start)
            edge_end = view3d_utils.location_3d_to_region_2d(
                region, region_3d, edge.end)
            if (edge_start is None or edge_end is None
                    or not _segment_intersects_region(edge_start, edge_end, region)):
                continue
            sample_count = visibility_sample_count(
                context.scene.hb_semantic_edge_sample_count, edge_start, edge_end)
            candidates.append((edge, sample_count))

    total_samples = sum(sample_count for _edge, sample_count in candidates)
    _viewport_performance['edges'] = len(candidates)
    _viewport_performance['samples'] = total_samples
    _viewport_performance['backend'] = (
        'Navigation preview' if navigation_preview else
        ('No visibility pass' if mode == 'ALL' else 'Ray-cast quality pass'))
    for edge, sample_count in candidates:
        runs = ((0.0, 1.0, VISIBLE),) if effective_mode == 'ALL' else \
            _edge_visibility_runs(context, region, region_3d, edge,
                                  sample_count)
        for start_t, end_t, visibility in runs:
            if effective_mode == 'VISIBLE_ONLY' and visibility == HIDDEN:
                continue
            start = view3d_utils.location_3d_to_region_2d(
                region, region_3d, _world_point_at(edge, start_t))
            end = view3d_utils.location_3d_to_region_2d(
                region, region_3d, _world_point_at(edge, end_t))
            if start is not None and end is not None:
                segments.append(ProjectedEdgeSegment(
                    edge.uid, (start.x, start.y), (end.x, end.y), visibility))
    if (effective_mode == 'TECHNICAL'
            and context.scene.hb_semantic_edges_suppress_aligned_hidden):
        segments = suppress_aligned_hidden_segments(segments)
    _projection_cache['key'] = key
    _projection_cache['segments'] = tuple(segments)
    return _projection_cache['segments']


def _draw_line_batch(shader, vertices, region, color, width):
    if not vertices:
        return
    shader.uniform_float('color', color)
    shader.uniform_float('viewportSize', (region.width, region.height))
    shader.uniform_float('lineWidth', width)
    batch_for_shader(shader, 'LINES', {'pos': vertices}).draw(shader)


def _draw_overlay():
    context = bpy.context
    if not getattr(context.scene, 'hb_show_semantic_edges', False):
        return
    area = context.area
    if area is None or area.type != 'VIEW_3D':
        return
    region = next((item for item in area.regions if item.type == 'WINDOW'), None)
    region_3d = context.space_data.region_3d
    if region is None or region_3d is None:
        return

    segments = projected_segments(context, region, region_3d)
    if not segments:
        return
    shader = gpu.shader.from_builtin('POLYLINE_UNIFORM_COLOR')
    previous_blend = gpu.state.blend_get()
    gpu.state.blend_set('ALPHA')
    try:
        shader.bind()
        visible_vertices = [point for segment in segments
                            if segment.visibility == VISIBLE
                            for point in (segment.start, segment.end)]
        color = line_color(context.scene)
        _draw_line_batch(shader, visible_vertices, region, color,
                         viewport_line_width(context.scene))
        hidden_vertices = [point for segment in segments
                           if segment.visibility == HIDDEN
                           for dash in dashed_screen_segments(segment.start, segment.end)
                           for point in dash]
        _draw_line_batch(shader, hidden_vertices, region, hidden_line_color(color),
                         hidden_line_width(viewport_line_width(context.scene)))
    finally:
        gpu.state.blend_set(previous_blend)


def create_semantic_edge_test_objects(context):
    """Create an inspectable set of mesh cases for the initial overlay."""
    collection = bpy.data.collections.new(TEST_COLLECTION_NAME)
    context.scene.collection.children.link(collection)

    def add_mesh(name, vertices, faces, location):
        mesh = bpy.data.meshes.new(name)
        mesh.from_pydata(vertices, [], faces)
        mesh.update()
        obj = bpy.data.objects.new(name, mesh)
        obj.location = location
        collection.objects.link(obj)
        return obj

    box = add_mesh(
        'Semantic Test - Box',
        [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0),
         (0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)],
        [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
         (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)],
        (0, 0, 0))
    panel = add_mesh(
        'Semantic Test - Triangulated Panel',
        [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)],
        [(0, 1, 2), (0, 2, 3)], (2, 0, 0))
    fold = add_mesh(
        'Semantic Test - Sharp Fold',
        [(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)],
        [(0, 1, 2), (0, 3, 1)], (4, 0, 0))
    marked = add_mesh(
        'Semantic Test - Marked Edge',
        [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)],
        [(0, 1, 2), (0, 2, 3)], (6, 0, 0))
    attribute = marked.data.attributes.new(semantic_edges.USER_MARKED_ATTRIBUTE,
                                           'BOOLEAN', 'EDGE')
    diagonal = next(edge for edge in marked.data.edges
                    if tuple(sorted(edge.vertices[:])) == (0, 2))
    attribute.data[diagonal.index].value = True

    bpy.ops.object.select_all(action='DESELECT')
    for obj in (box, panel, fold, marked):
        obj.select_set(True)
    context.view_layer.objects.active = box
    # The properties exist when the add-on is registered.  Keeping the
    # factory independent lets the headless semantic-edge tests import it
    # directly without registering the entire Home Builder add-on.
    if hasattr(context.scene, 'hb_show_semantic_edges'):
        context.scene.hb_show_semantic_edges = True
    if hasattr(context.scene, 'hb_semantic_edges_selected_only'):
        context.scene.hb_semantic_edges_selected_only = False
    if hasattr(context.scene, 'hb_semantic_edge_visibility_mode'):
        context.scene.hb_semantic_edge_visibility_mode = 'TECHNICAL'
    _redraw_viewports()
    return (box, panel, fold, marked)


class HOME_BUILDER_OT_create_semantic_edge_test_scene(bpy.types.Operator):
    bl_idname = 'home_builder.create_semantic_edge_test_scene'
    bl_label = 'Create Semantic Edge Test Objects'
    bl_description = 'Create meshes for checking semantic edge extraction'
    bl_options = {'UNDO'}

    def execute(self, context):
        create_semantic_edge_test_objects(context)
        self.report({'INFO'}, 'Created semantic-edge test objects')
        return {'FINISHED'}


class HOME_BUILDER_PT_semantic_edges(bpy.types.Panel):
    """Parent panel for all semantic-edge controls and future consumers."""
    bl_label = 'Semantic Edges (Experimental)'
    bl_idname = 'HOME_BUILDER_PT_semantic_edges'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Home Builder'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        self.layout.label(text='Opt-in technical-line alternative', icon='INFO')


class HOME_BUILDER_PT_semantic_edge_control(bpy.types.Panel):
    bl_label = 'Edge Control'
    bl_idname = 'HOME_BUILDER_PT_semantic_edge_control'
    bl_parent_id = 'HOME_BUILDER_PT_semantic_edges'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Home Builder'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, 'hb_show_semantic_edges', text='Show Overlay')
        layout.prop(context.scene, 'hb_semantic_edge_line_color', text='Line Color')
        layout.prop(context.scene, 'hb_semantic_edge_line_weight', text='Line Weight')
        layout.prop(context.scene, 'hb_semantic_edge_viewport_weight_multiplier',
                    text='Viewport Weight')
        layout.prop(context.scene, 'hb_semantic_edges_selected_only',
                    text='Selected Objects Only')
        layout.prop(context.scene, 'hb_semantic_edge_visibility_mode',
                    text='Visibility')
        if context.scene.hb_semantic_edge_visibility_mode != 'ALL':
            layout.prop(context.scene, 'hb_semantic_edge_sample_count',
                        text='Visibility Samples')
        if context.scene.hb_semantic_edge_visibility_mode == 'TECHNICAL':
            layout.prop(context.scene, 'hb_semantic_edges_suppress_aligned_hidden',
                        text='Suppress Aligned Hidden Lines')
        layout.separator()
        layout.label(text='Viewport: {}'.format(_viewport_performance['backend']),
                     icon='TIME')
        layout.label(text='{} on-screen edges / {} samples'.format(
            _viewport_performance['edges'], _viewport_performance['samples']))
        layout.operator(HOME_BUILDER_OT_create_semantic_edge_test_scene.bl_idname,
                        icon='MESH_CUBE')
        layout.label(text='Sampled visibility; exact splitting comes later.', icon='INFO')


_classes = (
    HOME_BUILDER_OT_create_semantic_edge_test_scene,
    HOME_BUILDER_PT_semantic_edges,
    HOME_BUILDER_PT_semantic_edge_control,
)


def register():
    global _draw_handle
    bpy.types.Scene.hb_show_semantic_edges = BoolProperty(
        name='Show Semantic Edges', default=False, update=_redraw_viewports)
    bpy.types.Scene.hb_semantic_edges_selected_only = BoolProperty(
        name='Selected Objects Only', default=False, update=_redraw_viewports)
    bpy.types.Scene.hb_semantic_edge_line_color = FloatVectorProperty(
        name='Semantic Edge Line Color', size=4, subtype='COLOR',
        default=OVERLAY_COLOR, min=0.0, max=1.0, update=_redraw_viewports)
    bpy.types.Scene.hb_semantic_edge_line_weight = FloatProperty(
        name='Semantic Edge Line Weight', default=OVERLAY_LINE_WIDTH,
        min=0.25, max=8.0, description='Base technical line width in pixels',
        update=_redraw_viewports)
    bpy.types.Scene.hb_semantic_edge_viewport_weight_multiplier = FloatProperty(
        name='Viewport Line Weight Multiplier', default=1.0,
        min=0.25, max=4.0,
        description='Viewport-specific adjustment of the shared line weight',
        update=_redraw_viewports)
    bpy.types.Scene.hb_semantic_edge_render_weight_multiplier = FloatProperty(
        name='Render Line Weight Multiplier', default=1.25,
        min=0.25, max=4.0,
        description='Render-specific adjustment after supersampling',
        update=_redraw_viewports)
    bpy.types.Scene.hb_semantic_edge_visibility_mode = EnumProperty(
        name='Semantic Edge Visibility',
        items=(
            ('ALL', 'All', 'Draw every semantic edge'),
            ('VISIBLE_ONLY', 'Visible Only', 'Hide occluded edge portions'),
            ('TECHNICAL', 'Technical', 'Draw occluded portions as dashed lines'),
        ),
        default='TECHNICAL', update=_redraw_viewports)
    bpy.types.Scene.hb_semantic_edge_sample_count = IntProperty(
        name='Visibility Samples', default=17, min=3, max=65,
        description='Ray samples per edge for the initial hidden-line pass',
        update=_redraw_viewports)
    bpy.types.Scene.hb_semantic_edges_suppress_aligned_hidden = BoolProperty(
        name='Suppress Aligned Hidden Lines', default=True,
        description='Remove hidden lines fully covered by visible collinear lines',
        update=_redraw_viewports)
    for cls in _classes:
        bpy.utils.register_class(cls)
    _draw_handle = bpy.types.SpaceView3D.draw_handler_add(
        _draw_overlay, (), 'WINDOW', 'POST_PIXEL')
    if _depsgraph_update_post not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(_depsgraph_update_post)


def unregister():
    global _draw_handle
    if _draw_handle is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_draw_handle, 'WINDOW')
        _draw_handle = None
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.hb_show_semantic_edges
    del bpy.types.Scene.hb_semantic_edges_selected_only
    del bpy.types.Scene.hb_semantic_edge_line_color
    del bpy.types.Scene.hb_semantic_edge_line_weight
    del bpy.types.Scene.hb_semantic_edge_viewport_weight_multiplier
    del bpy.types.Scene.hb_semantic_edge_render_weight_multiplier
    del bpy.types.Scene.hb_semantic_edge_visibility_mode
    del bpy.types.Scene.hb_semantic_edge_sample_count
    del bpy.types.Scene.hb_semantic_edges_suppress_aligned_hidden
    if _depsgraph_update_post in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(_depsgraph_update_post)
    _invalidate_semantic_edge_cache()
