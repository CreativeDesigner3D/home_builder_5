"""Render-camera consumer for Home Builder semantic edges.

The viewport overlay cannot appear in an F12 render.  This module projects
the same semantic edges through the render camera, classifies sampled
visibility, rasterizes a transparent supersampled Pillow image, and inserts
that image above the existing compositor result.
"""

from __future__ import annotations

import os
import tempfile

import bpy
from bpy.app.handlers import persistent
from bpy.props import BoolProperty, EnumProperty, IntProperty
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

try:
    from . import semantic_edges, semantic_edge_overlay
except ImportError:  # Direct Blender-headless test imports.
    import semantic_edges
    import semantic_edge_overlay


LINE_IMAGE_NAME = 'HB Semantic Line Pass'
IMAGE_NODE_NAME = 'HB Semantic Lines Image'
COMPOSITE_NODE_NAME = 'HB Semantic Lines Composite'


def _render_candidates(scene):
    view_layer = bpy.context.view_layer
    return [obj for obj in scene.objects
            if obj.type == 'MESH'
            and not obj.hide_render
            and obj.visible_get(view_layer=view_layer)]


def _world_point_at(edge, t):
    return tuple(edge.start[i] + (edge.end[i] - edge.start[i]) * t
                 for i in range(3))


def _camera_ray(camera, target):
    """Return (origin, direction, distance) for a render-camera sample."""
    target = Vector(target)
    matrix = camera.matrix_world
    if camera.data.type == 'ORTHO':
        local = matrix.inverted() @ target
        origin = matrix @ Vector((local.x, local.y, 0.0))
        direction = -(matrix.to_3x3() @ Vector((0.0, 0.0, 1.0))).normalized()
        distance = (target - origin).dot(direction)
    else:
        origin = matrix.translation
        offset = target - origin
        distance = offset.length
        direction = offset.normalized() if distance else Vector((0.0, 0.0, -1.0))
    return origin, direction, distance


def _sample_is_visible(scene, depsgraph, camera, target, tolerance):
    origin, direction, target_distance = _camera_ray(camera, target)
    if target_distance <= tolerance:
        return False
    hit, location, _normal, _face_index, _object, _matrix = scene.ray_cast(
        depsgraph, origin, direction, distance=target_distance + tolerance)
    if not hit:
        return True
    return (location - origin).length >= target_distance - tolerance


def _visibility_runs(scene, depsgraph, camera, edge, sample_count):
    length = (Vector(edge.end) - Vector(edge.start)).length
    tolerance = max(1.0e-5, length * 1.0e-5)
    samples = [_sample_is_visible(
        scene, depsgraph, camera,
        _world_point_at(edge, index / (sample_count - 1)), tolerance)
        for index in range(sample_count)]
    return semantic_edge_overlay.visibility_runs(samples)


def _image_point(scene, camera, point, width, height):
    ndc = world_to_camera_view(scene, camera, Vector(point))
    if ndc.z < 0.0 or not (-0.02 <= ndc.x <= 1.02 and -0.02 <= ndc.y <= 1.02):
        return None
    return (ndc.x * width, (1.0 - ndc.y) * height)


def camera_projected_segments(scene):
    """Return projected semantic segments for the active render camera."""
    camera = scene.camera
    if camera is None:
        return ()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    width = max(1, round(scene.render.resolution_x * scene.render.resolution_percentage / 100))
    height = max(1, round(scene.render.resolution_y * scene.render.resolution_percentage / 100))
    mode = scene.hb_semantic_render_mode
    segments = []
    for obj in _render_candidates(scene):
        for edge in semantic_edges.extract_semantic_edges(obj, depsgraph):
            runs = ((0.0, 1.0, semantic_edge_overlay.VISIBLE),) if mode == 'ALL' else \
                _visibility_runs(scene, depsgraph, camera, edge,
                                 scene.hb_semantic_render_sample_count)
            for start_t, end_t, visibility in runs:
                if mode == 'VISIBLE_ONLY' and visibility == semantic_edge_overlay.HIDDEN:
                    continue
                start = _image_point(scene, camera, _world_point_at(edge, start_t), width, height)
                end = _image_point(scene, camera, _world_point_at(edge, end_t), width, height)
                if start is not None and end is not None:
                    segments.append(semantic_edge_overlay.ProjectedEdgeSegment(
                        edge.uid, start, end, visibility))
    if mode == 'TECHNICAL' and scene.hb_semantic_render_suppress_aligned_hidden:
        segments = semantic_edge_overlay.suppress_aligned_hidden_segments(segments)
    return tuple(segments)


def _rgba(color):
    return tuple(round(component * 255) for component in color)


def render_semantic_line_image(scene):
    """Build, pack, and return the current scene's transparent line image."""
    try:
        from PIL import Image, ImageDraw
    except ImportError as error:
        raise RuntimeError('Pillow is required for semantic render lines') from error

    width = max(1, round(scene.render.resolution_x * scene.render.resolution_percentage / 100))
    height = max(1, round(scene.render.resolution_y * scene.render.resolution_percentage / 100))
    supersample = scene.hb_semantic_render_supersample
    image = Image.new('RGBA', (width * supersample, height * supersample), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    segments = camera_projected_segments(scene)

    def scaled(point):
        return (round(point[0] * supersample), round(point[1] * supersample))

    for segment in segments:
        if segment.visibility == semantic_edge_overlay.HIDDEN:
            pieces = semantic_edge_overlay.dashed_screen_segments(segment.start, segment.end)
            color, line_width = (
                semantic_edge_overlay.hidden_line_color(
                    semantic_edge_overlay.line_color(scene)),
                semantic_edge_overlay.hidden_line_width(
                    semantic_edge_overlay.render_line_width(scene)))
        else:
            pieces = ((segment.start, segment.end),)
            color, line_width = (semantic_edge_overlay.line_color(scene),
                                 semantic_edge_overlay.render_line_width(scene))
        for start, end in pieces:
            draw.line((scaled(start), scaled(end)), fill=_rgba(color),
                      width=max(1, round(line_width * supersample)))

    if supersample > 1:
        image = image.resize((width, height), Image.Resampling.LANCZOS)

    old = bpy.data.images.get(LINE_IMAGE_NAME)
    if old is not None:
        bpy.data.images.remove(old)
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp:
        path = temp.name
    try:
        image.save(path, 'PNG')
        result = bpy.data.images.load(path, check_existing=False)
        result.name = LINE_IMAGE_NAME
        result.pack()
        # Blender 5.2 renamed the former display-transform option; line PNGs
        # are conventional display-referred RGBA imagery.
        result.colorspace_settings.name = 'sRGB'
        return result
    finally:
        if os.path.exists(path):
            os.remove(path)


def _compositor_tree(scene):
    tree = scene.compositing_node_group
    if tree is None:
        tree = bpy.data.node_groups.new(f'{scene.name}_Compositor', 'CompositorNodeTree')
        tree.interface.new_socket(name='Image', in_out='OUTPUT', socket_type='NodeSocketColor')
        scene.compositing_node_group = tree
    return tree


def composite_semantic_line_image(scene, image):
    """Insert or update the semantic line layer above the compositor output."""
    tree = _compositor_tree(scene)
    nodes, links = tree.nodes, tree.links
    image_node = nodes.get(IMAGE_NODE_NAME)
    if image_node is None:
        image_node = nodes.new('CompositorNodeImage')
        image_node.name = IMAGE_NODE_NAME
        image_node.label = 'Semantic Lines'
        image_node.location = (250, -150)
    image_node.image = image

    alpha_over = nodes.get(COMPOSITE_NODE_NAME)
    if alpha_over is None:
        output = next((node for node in nodes if node.type == 'GROUP_OUTPUT'), None)
        if output is None:
            output = nodes.new('NodeGroupOutput')
            output.location = (600, 200)
        render_layers = next((node for node in nodes if node.type == 'R_LAYERS'), None)
        if render_layers is None:
            render_layers = nodes.new('CompositorNodeRLayers')
            render_layers.location = (0, 200)
        alpha_over = nodes.new('CompositorNodeAlphaOver')
        alpha_over.name = COMPOSITE_NODE_NAME
        alpha_over.label = 'Semantic Lines Composite'
        alpha_over.location = (450, 200)
        output_input = output.inputs[0]
        existing = output_input.links[0].from_socket if output_input.links else render_layers.outputs['Image']
        links.new(existing, alpha_over.inputs[0])
        links.new(image_node.outputs['Image'], alpha_over.inputs[1])
        links.new(alpha_over.outputs[0], output_input)
    scene.render.use_compositing = True


@persistent
def prepare_semantic_render_lines(scene, _depsgraph=None):
    """Refresh the pass immediately before F12 / layout renders begin."""
    if not getattr(scene, 'hb_semantic_render_enabled', False) or scene.camera is None:
        return
    try:
        composite_semantic_line_image(scene, render_semantic_line_image(scene))
    except Exception as error:
        print(f'Home Builder semantic line render skipped: {error}')


class HOME_BUILDER_OT_prepare_semantic_line_render(bpy.types.Operator):
    bl_idname = 'home_builder.prepare_semantic_line_render'
    bl_label = 'Prepare Semantic Line Pass'
    bl_description = 'Generate and composite semantic lines for the active render camera'

    def execute(self, context):
        if context.scene.camera is None:
            self.report({'ERROR'}, 'The scene needs an active camera')
            return {'CANCELLED'}
        try:
            composite_semantic_line_image(context.scene, render_semantic_line_image(context.scene))
        except RuntimeError as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        self.report({'INFO'}, 'Semantic line pass prepared for rendering')
        return {'FINISHED'}


class HOME_BUILDER_PT_semantic_line_render(bpy.types.Panel):
    bl_label = 'Line Rendering'
    bl_idname = 'HOME_BUILDER_PT_semantic_line_render'
    bl_parent_id = 'HOME_BUILDER_PT_semantic_edges'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Home Builder'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.prop(scene, 'hb_semantic_render_enabled', text='Render Semantic Lines')
        layout.prop(scene, 'hb_semantic_render_mode', text='Visibility')
        if scene.hb_semantic_render_mode != 'ALL':
            layout.prop(scene, 'hb_semantic_render_sample_count', text='Visibility Samples')
        if scene.hb_semantic_render_mode == 'TECHNICAL':
            layout.prop(scene, 'hb_semantic_render_suppress_aligned_hidden',
                        text='Suppress Aligned Hidden Lines')
        layout.prop(scene, 'hb_semantic_render_supersample', text='Supersample')
        layout.prop(scene, 'hb_semantic_edge_render_weight_multiplier',
                    text='Render Weight')
        layout.operator(HOME_BUILDER_OT_prepare_semantic_line_render.bl_idname,
                        icon='RENDER_STILL')


_classes = (HOME_BUILDER_OT_prepare_semantic_line_render,
            HOME_BUILDER_PT_semantic_line_render)


def register():
    bpy.types.Scene.hb_semantic_render_enabled = BoolProperty(
        name='Render Semantic Lines', default=False)
    bpy.types.Scene.hb_semantic_render_mode = EnumProperty(
        name='Semantic Render Visibility',
        items=(
            ('ALL', 'All', 'Render every semantic edge'),
            ('VISIBLE_ONLY', 'Visible Only', 'Omit occluded edge portions'),
            ('TECHNICAL', 'Technical', 'Render hidden portions as dashed lines'),
        ), default='TECHNICAL')
    bpy.types.Scene.hb_semantic_render_sample_count = IntProperty(
        name='Render Visibility Samples', default=17, min=3, max=65)
    bpy.types.Scene.hb_semantic_render_suppress_aligned_hidden = BoolProperty(
        name='Suppress Aligned Hidden Lines', default=True)
    bpy.types.Scene.hb_semantic_render_supersample = IntProperty(
        name='Render Supersample', default=2, min=1, max=4)
    for cls in _classes:
        bpy.utils.register_class(cls)
    if prepare_semantic_render_lines not in bpy.app.handlers.render_pre:
        bpy.app.handlers.render_pre.append(prepare_semantic_render_lines)


def unregister():
    if prepare_semantic_render_lines in bpy.app.handlers.render_pre:
        bpy.app.handlers.render_pre.remove(prepare_semantic_render_lines)
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.hb_semantic_render_enabled
    del bpy.types.Scene.hb_semantic_render_mode
    del bpy.types.Scene.hb_semantic_render_sample_count
    del bpy.types.Scene.hb_semantic_render_suppress_aligned_hidden
    del bpy.types.Scene.hb_semantic_render_supersample
