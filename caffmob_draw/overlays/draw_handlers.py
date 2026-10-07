"""
Blender to Mob Overlay System
GPU-based visual overlays for grid, insertion planes, dimensions, and construction aids.
"""

import bpy  # type: ignore
import gpu  # type: ignore
import blf  # type: ignore
from gpu_extras.batch import batch_for_shader  # type: ignore
from mathutils import Vector  # type: ignore
from bpy_extras.view3d_utils import location_3d_to_region_2d  # type: ignore
from ..data import units


# Module-level draw handler references
_grid_handler = None


# ---------------------------------------------------------------------------
# Grid Overlay — Dotted grid on the floor for snapping reference
# ---------------------------------------------------------------------------

def draw_grid_overlay():
    context = bpy.context
    scene = context.scene

    if not hasattr(scene, 'btm_settings'):
        return

    settings = scene.btm_settings
    if not settings.show_grid:
        return

    # Find the floor object to determine grid bounds
    floor_obj = None
    for obj in scene.objects:
        if hasattr(obj, 'btm_plane') and obj.btm_plane.object_kind == 'FLOOR':
            floor_obj = obj
            break

    # Determine grid bounds
    if floor_obj and floor_obj.type == 'MESH' and floor_obj.data.vertices:
        verts = [floor_obj.matrix_world @ v.co for v in floor_obj.data.vertices]
        min_x = min(v.x for v in verts) - 0.1
        max_x = max(v.x for v in verts) + 0.1
        min_y = min(v.y for v in verts) - 0.1
        max_y = max(v.y for v in verts) + 0.1
    else:
        min_x, max_x = -5.0, 5.0
        min_y, max_y = -5.0, 5.0

    # Spacing is stored natively in meters
    spacing_x = settings.grid_spacing_x
    spacing_y = settings.grid_spacing_y

    if spacing_x <= 0 or spacing_y <= 0:
        return

    # Generate grid points
    points = []
    x = min_x
    while x <= max_x:
        y = min_y
        while y <= max_y:
            points.append(Vector((x, y, 0.001)))  # Slightly above floor
            y += spacing_y
        x += spacing_x

    if not points:
        return

    # Draw points
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    gpu.state.blend_set('ALPHA')
    gpu.state.point_size_set(3.0)

    batch = batch_for_shader(shader, 'POINTS', {"pos": points})
    shader.bind()
    shader.uniform_float("color", (0.5, 0.5, 0.5, 0.35))
    batch.draw(shader)

    gpu.state.point_size_set(1.0)
    gpu.state.blend_set('NONE')


# ---------------------------------------------------------------------------
# Grid Lines Overlay
# ---------------------------------------------------------------------------

def draw_grid_lines():
    context = bpy.context
    scene = context.scene

    if not hasattr(scene, 'btm_settings'):
        return

    settings = scene.btm_settings
    if not settings.show_grid:
        return

    # Find the floor object
    floor_obj = None
    for obj in scene.objects:
        if hasattr(obj, 'btm_plane') and obj.btm_plane.object_kind == 'FLOOR':
            floor_obj = obj
            break

    # Grid bounds
    if floor_obj and floor_obj.type == 'MESH' and floor_obj.data.vertices:
        verts = [floor_obj.matrix_world @ v.co for v in floor_obj.data.vertices]
        min_x = min(v.x for v in verts)
        max_x = max(v.x for v in verts)
        min_y = min(v.y for v in verts)
        max_y = max(v.y for v in verts)
    else:
        min_x, max_x = -5.0, 5.0
        min_y, max_y = -5.0, 5.0

    spacing_x = settings.grid_spacing_x
    spacing_y = settings.grid_spacing_y

    if spacing_x <= 0 or spacing_y <= 0:
        return

    z = 0.0005  # Slightly above floor

    # Generate horizontal and vertical line pairs
    line_verts = []

    # Vertical lines
    x = min_x
    while x <= max_x:
        line_verts.append(Vector((x, min_y, z)))
        line_verts.append(Vector((x, max_y, z)))
        x += spacing_x

    # Horizontal lines
    y = min_y
    while y <= max_y:
        line_verts.append(Vector((min_x, y, z)))
        line_verts.append(Vector((max_x, y, z)))
        y += spacing_y

    if not line_verts:
        return

    # Draw lines
    region = bpy.context.region
    shader = gpu.shader.from_builtin('POLYLINE_UNIFORM_COLOR')
    gpu.state.blend_set('ALPHA')

    batch = batch_for_shader(shader, 'LINES', {"pos": line_verts})
    shader.bind()
    shader.uniform_float("color", (0.4, 0.45, 0.5, 0.15))
    shader.uniform_float("lineWidth", 1.0)
    shader.uniform_float("viewportSize", (region.width, region.height))
    batch.draw(shader)

    gpu.state.blend_set('NONE')


# ---------------------------------------------------------------------------
# Insertion Plane Highlight
# ---------------------------------------------------------------------------

def draw_insertion_plane_highlight():
    context = bpy.context
    scene = context.scene

    if not hasattr(scene, 'btm_settings'):
        return

    settings = scene.btm_settings
    if not settings.show_insertion_plane:
        return

    # Highlight the active object if it's a valid insertion plane
    obj = context.active_object
    if obj is None or not hasattr(obj, 'btm_plane'):
        return

    kind = obj.btm_plane.object_kind
    if kind not in ('WALL', 'FLOOR', 'MODULE', 'GEOMETRY'):
        return

    if obj.type != 'MESH' or not obj.data.vertices:
        return

    # Get object's bottom face vertices in world space
    verts = [obj.matrix_world @ v.co for v in obj.data.vertices]

    if len(verts) < 3:
        return

    # Use a simple TRI_FAN
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    gpu.state.blend_set('ALPHA')
    gpu.state.depth_test_set('LESS_EQUAL')

    batch = batch_for_shader(shader, 'TRI_FAN', {"pos": verts[:8]})
    shader.bind()

    # Yellow semitransparent
    shader.uniform_float("color", (1.0, 0.9, 0.2, 0.12))
    batch.draw(shader)

    gpu.state.blend_set('NONE')
    gpu.state.depth_test_set('NONE')


# ---------------------------------------------------------------------------
# Dimension Labels
# ---------------------------------------------------------------------------

def draw_dimension_labels():
    context = bpy.context
    scene = context.scene

    if not hasattr(scene, 'btm_settings'):
        return

    settings = scene.btm_settings
    if not settings.show_dimensions:
        return

    region = context.region
    rv3d = context.region_data
    if not region or not rv3d:
        return

    # Draw dimension indicators for wall objects
    for obj in scene.objects:
        if not hasattr(obj, 'btm_plane') or obj.btm_plane.object_kind != 'WALL':
            continue
        if obj.type != 'MESH' or not obj.data.vertices:
            continue

        # Get bottom edge vertices
        verts = [obj.matrix_world @ v.co for v in obj.data.vertices]
        min_z = min(v.z for v in verts)
        bottom_verts = [v for v in verts if abs(v.z - min_z) < 0.01]

        if len(bottom_verts) < 2:
            continue

        # Draw lines between pairs of bottom vertices
        shader = gpu.shader.from_builtin('POLYLINE_UNIFORM_COLOR')
        gpu.state.blend_set('ALPHA')

        line_verts = []
        for i in range(0, len(bottom_verts) - 1, 2):
            p1 = bottom_verts[i]
            p2 = bottom_verts[i + 1] if i + 1 < len(bottom_verts) else bottom_verts[0]
            # Offset slightly below floor for dimension line
            line_verts.append(Vector((p1.x, p1.y, 0.001)))
            line_verts.append(Vector((p2.x, p2.y, 0.001)))

        if line_verts:
            batch = batch_for_shader(shader, 'LINES', {"pos": line_verts})
            shader.bind()
            shader.uniform_float("color", (0.0, 0.6, 1.0, 0.5))
            shader.uniform_float("lineWidth", 1.5)
            shader.uniform_float("viewportSize", (region.width, region.height))
            batch.draw(shader)

        # Draw text labels
        font_id = 0
        blf.size(font_id, 14)

        for i in range(0, len(bottom_verts) - 1, 2):
            p1 = bottom_verts[i]
            p2 = bottom_verts[i + 1] if i + 1 < len(bottom_verts) else bottom_verts[0]
            midpoint = p1 + (p2 - p1) * 0.5
            midpoint.z = 0.05

            co_2d = location_3d_to_region_2d(region, rv3d, midpoint)
            if co_2d:
                length_str = units.format_value((p2 - p1).length, scene)

                # Shadow
                blf.color(font_id, 0.0, 0.0, 0.0, 0.9)
                blf.position(font_id, co_2d.x + 1, co_2d.y - 1, 0)
                blf.draw(font_id, length_str)

                # Main text
                blf.color(font_id, 0.0, 0.8, 1.0, 1.0)
                blf.position(font_id, co_2d.x, co_2d.y, 0)
                blf.draw(font_id, length_str)

        gpu.state.blend_set('NONE')


# ---------------------------------------------------------------------------
# Combined draw callback
# ---------------------------------------------------------------------------

def _draw_all_overlays():
    try:
        draw_grid_overlay()
        draw_grid_lines()
        draw_insertion_plane_highlight()
        draw_dimension_labels()
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

def register():
    global _grid_handler
    _grid_handler = bpy.types.SpaceView3D.draw_handler_add(
        _draw_all_overlays, (), 'WINDOW', 'POST_VIEW'
    )


def unregister():
    global _grid_handler
    if _grid_handler is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_grid_handler, 'WINDOW')
        _grid_handler = None
