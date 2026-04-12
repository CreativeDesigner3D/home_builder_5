import bpy
import bmesh
import math
import os
import gpu
import blf
from mathutils import Vector
from mathutils.geometry import intersect_line_plane
from bpy_extras import view3d_utils
from gpu_extras.batch import batch_for_shader
from .. import hb_types, hb_snap, hb_placement, units

# Wall Miter Angle Calculation
def calculate_wall_miter_angles(wall_obj):
    """
    Calculate and set the miter angles for a wall based on connected walls.
    Uses the GeoNodeWall.get_connected_wall() method to find connections.
    
    The miter angle formula:
    - turn_angle = connected_wall_rotation - this_wall_rotation (normalized to -180° to 180°)
    - For the RIGHT end (end of wall): right_angle = -turn_angle / 2
    - For the LEFT end (start of wall): left_angle = turn_angle / 2
    """
    import math
    
    wall = hb_types.GeoNodeWall(wall_obj)
    this_rot = wall_obj.rotation_euler.z
    
    # Get connected wall on the left (at our START)
    left_wall = wall.get_connected_wall('left')
    if left_wall:
        prev_rot = left_wall.obj.rotation_euler.z
        turn = this_rot - prev_rot
        # Normalize turn angle to -pi to pi
        while turn > math.pi: turn -= 2 * math.pi
        while turn < -math.pi: turn += 2 * math.pi
        
        left_angle = turn / 2
        wall.set_input('Left Angle', left_angle)
    else:
        wall.set_input('Left Angle', 0)
    
    # Get connected wall on the right (at our END)
    right_wall = wall.get_connected_wall('right')
    if right_wall:
        next_rot = right_wall.obj.rotation_euler.z
        turn = next_rot - this_rot
        # Normalize turn angle to -pi to pi
        while turn > math.pi: turn -= 2 * math.pi
        while turn < -math.pi: turn += 2 * math.pi
        
        right_angle = -turn / 2
        wall.set_input('Right Angle', right_angle)
    else:
        wall.set_input('Right Angle', 0)


def update_all_wall_miters():
    """Update miter angles for all walls in the scene."""
    for obj in bpy.data.objects:
        if 'IS_WALL_BP' in obj:
            calculate_wall_miter_angles(obj)


def update_connected_wall_miters(wall_obj):
    """Update miter angles for a wall and all walls connected to it."""
    wall = hb_types.GeoNodeWall(wall_obj)

    # Update this wall
    calculate_wall_miter_angles(wall_obj)

    # Update connected wall on the left
    left_wall = wall.get_connected_wall('left')
    if left_wall:
        calculate_wall_miter_angles(left_wall.obj)

    # Update connected wall on the right
    right_wall = wall.get_connected_wall('right')
    if right_wall:
        calculate_wall_miter_angles(right_wall.obj)

# Room Lighting Helpers
def point_in_polygon(point, polygon):
    """Ray casting algorithm to check if point is inside polygon."""
    x, y = point.x, point.y
    n = len(polygon)
    inside = False
    
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i].x, polygon[i].y
        xj, yj = polygon[j].x, polygon[j].y
        
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    
    return inside
  
def get_wall_endpoints(wall_obj):
    """Get the start and end points of a wall in world coordinates."""
    
    world_matrix = wall_obj.matrix_world
    start = world_matrix.translation.copy()
    
    rot_z = wall_obj.matrix_world.to_euler().z
    
    # Find obj_x child to get wall length
    length = 0
    for child in wall_obj.children:
        if 'obj_x' in child.name.lower():
            length = child.location.x
            break
    
    direction = Vector((math.cos(rot_z), math.sin(rot_z), 0))
    end = start + direction * length
    
    return start.to_2d(), end.to_2d()

def find_wall_chains():
    """Find connected chains of walls in the current scene, returning list of ordered wall objects.
    
    Handles both open chains (interior walls) and closed loops (room perimeters).
    Supports junction points where multiple walls share the same start/end location.
    Closed loops are detected first so interior branches don't steal perimeter walls.
    """
    walls = [obj for obj in bpy.context.scene.objects if obj.get('IS_WALL_BP')]
    
    if not walls:
        return []
    
    wall_data = {}
    for wall in walls:
        start, end = get_wall_endpoints(wall)
        wall_data[wall.name] = {'obj': wall, 'start': start, 'end': end}
    
    tolerance = 0.01
    
    # Build adjacency lists — each wall can have multiple successors
    connections = {}
    for name1, data1 in wall_data.items():
        succs = []
        for name2, data2 in wall_data.items():
            if name1 != name2 and (data1['end'] - data2['start']).length < tolerance:
                succs.append(name2)
        connections[name1] = succs
    
    chains = []
    used = set()
    
    # --- First pass: find closed loops ---
    # Try each wall as a potential loop start. Interior branches won't form loops,
    # so only true perimeters (and closed interior rooms) get claimed here.
    for name in wall_data:
        if name in used:
            continue
        
        chain = []
        current = name
        trace_visited = set()
        is_loop = False
        
        while current and current not in trace_visited and current not in used:
            trace_visited.add(current)
            chain.append(current)
            all_succs = connections.get(current, [])
            
            # Check if any successor closes the loop back to the start
            if name in all_succs and len(chain) > 2:
                is_loop = True
                break
            
            # Pick an unused successor (not visited in this trace, not globally used)
            next_succs = [s for s in all_succs if s not in trace_visited and s not in used]
            current = next_succs[0] if next_succs else None
        
        if is_loop:
            used.update(chain)
            chains.append([wall_data[n]['obj'] for n in chain])
    
    # --- Second pass: trace remaining walls as open chains ---
    has_predecessor = set()
    for succs in connections.values():
        has_predecessor.update(succs)
    start_walls = [name for name in wall_data if name not in has_predecessor and name not in used]
    
    def trace_open_chain(start_name):
        chain = []
        current = start_name
        while current and current not in used:
            used.add(current)
            chain.append(wall_data[current]['obj'])
            unused_succs = [s for s in connections.get(current, []) if s not in used]
            current = unused_succs[0] if unused_succs else None
        return chain
    
    for start_name in start_walls:
        if start_name not in used:
            chain = trace_open_chain(start_name)
            if chain:
                chains.append(chain)
    
    # Third pass: pick up any remaining isolated walls
    for name in wall_data:
        if name not in used:
            chain = trace_open_chain(name)
            if chain:
                chains.append(chain)
    
    return chains

def get_room_boundary_points(wall_chain):
    """Extract boundary points from a chain of walls."""

    points = []
    
    for wall in wall_chain:
        start, end = get_wall_endpoints(wall)
        if not points or (Vector(points[-1]) - Vector((start.x, start.y, 0))).length > 0.01:
            points.append(Vector((start.x, start.y, 0)))
    
    if wall_chain:
        start, end = get_wall_endpoints(wall_chain[-1])
        points.append(Vector((end.x, end.y, 0)))
    
    return points

def is_closed_loop(points, tolerance=0.01):
    """Check if the points form a closed loop."""
    if len(points) < 3:
        return False
    return (points[0] - points[-1]).length < tolerance
    




def _draw_dim_text(x, y, text, color):
    """Draw centered text at screen position."""
    font_id = 0
    blf.size(font_id, 13)
    blf.color(font_id, *color)
    w, h = blf.dimensions(font_id, text)
    blf.position(font_id, x - w / 2, y - h / 2, 0)
    blf.draw(font_id, text)


def _draw_wall_length_dim(op):
    """GPU draw callback: renders the live wall length dimension while
    drawing walls. Reads state from the operator each frame.

    Replaces the legacy GeoNodeDimension scene-object approach used during
    wall draw, mirroring the door/window placement dimension pattern.
    """
    if not getattr(op, '_wall_dim_visible', False):
        return
    wall = getattr(op, 'current_wall', None)
    if wall is None:
        return
    try:
        wall_obj = wall.obj
        if wall_obj is None or wall_obj.name not in bpy.data.objects:
            return
    except (ReferenceError, AttributeError):
        return

    try:
        length = wall.get_input('Length')
        height = wall.get_input('Height')
    except Exception:
        return

    if length is None or length < 0.001:
        return

    context = bpy.context
    region = context.region
    rv3d = context.region_data
    if region is None or rv3d is None:
        return

    # Wall local axes in world space (length runs along local +X)
    wm = wall_obj.matrix_world
    wall_dir = Vector((wm[0][0], wm[1][0], wm[2][0]))
    if wall_dir.length < 1e-6:
        return
    wall_dir.normalize()

    # Z position: just above the top of the wall (matches legacy 1" offset)
    base_z = wm[2][3] + (height or 0) + units.inch(1)

    origin_2d = Vector((wm[0][3], wm[1][3], base_z))
    end_2d = origin_2d + wall_dir * length

    s_start = view3d_utils.location_3d_to_region_2d(region, rv3d, origin_2d)
    s_end = view3d_utils.location_3d_to_region_2d(region, rv3d, end_2d)
    if s_start is None or s_end is None:
        return

    seg = s_end - s_start
    if seg.length < 2:
        return
    seg_dir = seg.normalized()
    # Perpendicular in screen space — push dim outward (away from wall body)
    offset_dir = Vector((-seg_dir.y, seg_dir.x))

    # Flip offset_dir so it points away from the wall's body. Use a sample
    # point on the wall's centerline to decide which side is "inside".
    wall_mid_world = Vector((wm[0][3], wm[1][3], wm[2][3] + (height or 0) / 2))
    wall_mid_screen = view3d_utils.location_3d_to_region_2d(region, rv3d, wall_mid_world)
    if wall_mid_screen is not None:
        seg_mid = (s_start + s_end) / 2
        if (wall_mid_screen - seg_mid).dot(offset_dir) > 0:
            offset_dir = -offset_dir

    offset_px = 20
    tick_half = 5
    dim_color = (0.0, 0.85, 1.0, 0.85)
    leader_color = (0.0, 0.85, 1.0, 0.3)

    a = s_start + offset_dir * offset_px
    b = s_end + offset_dir * offset_px
    tick_dir = Vector((-offset_dir.y, offset_dir.x))

    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    gpu.state.blend_set('ALPHA')
    shader.bind()

    # Leader lines
    gpu.state.line_width_set(1.0)
    shader.uniform_float("color", leader_color)
    for fp, dp in [(s_start, a), (s_end, b)]:
        batch = batch_for_shader(shader, 'LINES', {"pos": [(fp.x, fp.y), (dp.x, dp.y)]})
        batch.draw(shader)

    # Dim line
    gpu.state.line_width_set(1.5)
    shader.uniform_float("color", dim_color)
    batch = batch_for_shader(shader, 'LINES', {"pos": [(a.x, a.y), (b.x, b.y)]})
    batch.draw(shader)

    # Tick marks
    for p in (a, b):
        t1 = p + tick_dir * tick_half
        t2 = p - tick_dir * tick_half
        batch = batch_for_shader(shader, 'LINES', {"pos": [(t1.x, t1.y), (t2.x, t2.y)]})
        batch.draw(shader)

    # Text label
    mid = (a + b) / 2 + offset_dir * 12
    text = units.unit_to_string(context.scene.unit_settings, length)
    _draw_dim_text(mid.x, mid.y, text, dim_color)

    gpu.state.line_width_set(1.0)
    gpu.state.blend_set('NONE')


def _draw_wall_snap_dimensions(region, wall_obj, snap_point_3d, face,
                               drawing_gap=0, gap_direction=0):
    """
    Draw left/right dimension lines along the wall face from the snap point.
    Shows the distance from the snap point to each end of the wall,
    with a visible gap for the drawing wall's thickness.
    
    Args:
        drawing_gap: Width of the drawing wall projected onto the target face (meters).
        gap_direction: Signed float indicating which direction along the target face
                       the wall body extends from the snap point.
                       > 0: gap extends in target wall's +X direction from snap point
                       < 0: gap extends in target wall's -X direction from snap point
                       == 0: gap centered on snap point (fallback when direction unknown)
    """
    from bpy_extras import view3d_utils

    wall = hb_types.GeoNodeWall(wall_obj)
    wall_length = wall.get_input('Length')
    wall_thickness = wall.get_input('Thickness')

    wm = wall_obj.matrix_world
    wall_dir = Vector((wm[0][0], wm[1][0])).normalized()
    wall_perp = Vector((wm[0][1], wm[1][1])).normalized()
    wall_origin = Vector((wm[0][3], wm[1][3]))

    face_offset = 0 if face == 'back' else wall_thickness
    face_base = wall_origin + wall_perp * face_offset

    # Snap point projected onto face line
    snap_2d_pos = Vector((snap_point_3d.x, snap_point_3d.y))
    to_snap = snap_2d_pos - face_base
    local_along = max(0, min(wall_length, to_snap.dot(wall_dir)))

    # Compute gap edges based on direction
    if gap_direction > 0:
        # Wall body extends in +along direction from snap point
        gap_left = local_along
        gap_right = min(wall_length, local_along + drawing_gap)
    elif gap_direction < 0:
        # Wall body extends in -along direction from snap point
        gap_left = max(0, local_along - drawing_gap)
        gap_right = local_along
    else:
        # Unknown direction — center the gap
        half_gap = drawing_gap / 2
        gap_left = max(0, local_along - half_gap)
        gap_right = min(wall_length, local_along + half_gap)

    left_dist = gap_left
    right_dist = wall_length - gap_right

    # 3D points on the face
    face_start_3d = Vector((*face_base, 0))
    face_end_3d = Vector((*(face_base + wall_dir * wall_length), 0))
    gap_left_3d = Vector((*(face_base + wall_dir * gap_left), 0))
    gap_right_3d = Vector((*(face_base + wall_dir * gap_right), 0))

    # Project to screen
    l2d = view3d_utils.location_3d_to_region_2d(region, region.data, face_start_3d)
    r2d = view3d_utils.location_3d_to_region_2d(region, region.data, face_end_3d)
    gl2d = view3d_utils.location_3d_to_region_2d(region, region.data, gap_left_3d)
    gr2d = view3d_utils.location_3d_to_region_2d(region, region.data, gap_right_3d)

    if not l2d or not r2d or not gl2d or not gr2d:
        return

    # Face direction in screen space
    face_vec = r2d - l2d
    if face_vec.length < 2:
        return
    face_dir_n = face_vec.normalized()

    # Offset direction: perpendicular to face, pointing away from wall body
    offset_dir = Vector((-face_dir_n.y, face_dir_n.x))
    wall_mid_3d = Vector((*(wall_origin + wall_perp * (wall_thickness / 2)), 0))
    wall_mid_2d = view3d_utils.location_3d_to_region_2d(region, region.data, wall_mid_3d)
    if wall_mid_2d:
        snap_2d = (gl2d + gr2d) / 2
        if (wall_mid_2d - snap_2d).dot(offset_dir) > 0:
            offset_dir = -offset_dir

    offset_px = 20
    tick_half = 5
    dim_color = (0.0, 0.85, 1.0, 0.85)
    leader_color = (0.0, 0.85, 1.0, 0.3)
    gap_color = (1.0, 0.6, 0.0, 0.6)

    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    tick_dir = Vector((-offset_dir.y, offset_dir.x))

    unit_settings = bpy.context.scene.unit_settings

    # Draw left and right dimension segments
    for dist, p_from, p_to in [(left_dist, gl2d, l2d), (right_dist, gr2d, r2d)]:
        if dist < 0.005:
            continue

        a = p_from + offset_dir * offset_px
        b = p_to + offset_dir * offset_px

        shader.bind()

        # Leader lines
        gpu.state.line_width_set(1.0)
        shader.uniform_float("color", leader_color)
        for fp, dp in [(p_from, a), (p_to, b)]:
            batch = batch_for_shader(shader, 'LINES', {"pos": [(fp.x, fp.y), (dp.x, dp.y)]})
            batch.draw(shader)

        # Dimension line
        gpu.state.line_width_set(1.5)
        shader.uniform_float("color", dim_color)
        batch = batch_for_shader(shader, 'LINES', {"pos": [(a.x, a.y), (b.x, b.y)]})
        batch.draw(shader)

        # Tick marks
        for p in [a, b]:
            t1 = p + tick_dir * tick_half
            t2 = p - tick_dir * tick_half
            batch = batch_for_shader(shader, 'LINES', {"pos": [(t1.x, t1.y), (t2.x, t2.y)]})
            batch.draw(shader)

        # Text label
        mid = (a + b) / 2 + offset_dir * 12
        text = units.unit_to_string(unit_settings, dist)
        _draw_dim_text(mid.x, mid.y, text, dim_color)

    # Draw gap indicator (wall thickness zone)
    if drawing_gap > 0.005:
        ga = gl2d + offset_dir * offset_px
        gb = gr2d + offset_dir * offset_px

        shader.bind()

        # Gap line (thicker, orange)
        gpu.state.line_width_set(3.0)
        shader.uniform_float("color", gap_color)
        batch = batch_for_shader(shader, 'LINES', {"pos": [(ga.x, ga.y), (gb.x, gb.y)]})
        batch.draw(shader)

        # Leader lines for gap edges
        gpu.state.line_width_set(1.0)
        shader.uniform_float("color", (1.0, 0.6, 0.0, 0.3))
        for fp, dp in [(gl2d, ga), (gr2d, gb)]:
            batch = batch_for_shader(shader, 'LINES', {"pos": [(fp.x, fp.y), (dp.x, dp.y)]})
            batch.draw(shader)

        # Gap dimension text
        gap_mid = (ga + gb) / 2 + offset_dir * 12
        gap_text = units.unit_to_string(unit_settings, drawing_gap)
        _draw_dim_text(gap_mid.x, gap_mid.y, gap_text, gap_color)

    gpu.state.line_width_set(1.0)


def _draw_snap_point(x, y, color, radius, cross_size, diamond=False):
    """Draw a snap crosshair + circle at screen position (x, y)."""
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')

    # --- Outer circle ---
    gpu.state.line_width_set(2.0)
    segments = 32
    circle_verts = []
    for i in range(segments + 1):
        a = 2 * math.pi * i / segments
        circle_verts.append((x + radius * math.cos(a), y + radius * math.sin(a)))

    shader.bind()
    shader.uniform_float("color", color)
    batch = batch_for_shader(shader, 'LINE_STRIP', {"pos": circle_verts})
    batch.draw(shader)

    # --- Crosshair ---
    cross_verts = [
        (x - cross_size, y), (x + cross_size, y),
        (x, y - cross_size), (x, y + cross_size),
    ]
    batch = batch_for_shader(shader, 'LINES', {"pos": cross_verts})
    batch.draw(shader)

    # --- Diamond indicator for surface snap ---
    if diamond:
        diamond_y = y + radius + 8
        diamond_size = 4
        diamond_verts = [
            (x, diamond_y + diamond_size),
            (x + diamond_size, diamond_y),
            (x, diamond_y - diamond_size),
            (x - diamond_size, diamond_y),
            (x, diamond_y + diamond_size),
        ]
        shader.uniform_float("color", color)
        batch = batch_for_shader(shader, 'LINE_STRIP', {"pos": diamond_verts})
        batch.draw(shader)

    gpu.state.line_width_set(1.0)


def _draw_track_indicators(op, region, context):
    """Draw acquired track points, hover candidate, and active track lines."""
    import time
    rv3d = region.data
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')

    tp_color = (1.0, 0.55, 0.0, 0.95)        # orange for acquired track points
    tp_line_color = (1.0, 0.55, 0.0, 0.7)    # dashed tracking line
    hover_color = (1.0, 0.55, 0.0, 0.55)     # pending hover

    # Draw acquired track points as orange "+" markers
    for tp in op.track_points:
        scr = view3d_utils.location_3d_to_region_2d(region, rv3d, tp)
        if scr is None:
            continue
        size = 7
        verts = [
            (scr.x - size, scr.y), (scr.x + size, scr.y),
            (scr.x, scr.y - size), (scr.x, scr.y + size),
        ]
        gpu.state.line_width_set(2.0)
        shader.bind()
        shader.uniform_float("color", tp_color)
        batch = batch_for_shader(shader, 'LINES', {"pos": verts})
        batch.draw(shader)
        # Small square outline around the + so it reads as distinct from snap crosshairs
        s = 9
        sq = [
            (scr.x - s, scr.y - s), (scr.x + s, scr.y - s),
            (scr.x + s, scr.y + s), (scr.x - s, scr.y + s),
            (scr.x - s, scr.y - s),
        ]
        batch = batch_for_shader(shader, 'LINE_STRIP', {"pos": sq})
        batch.draw(shader)

    # Draw hover candidate with dwell-progress arc
    if op._hover_candidate is not None and op._hover_start_time > 0.0:
        scr = view3d_utils.location_3d_to_region_2d(region, rv3d, op._hover_candidate)
        if scr is not None:
            elapsed = time.time() - op._hover_start_time
            progress = max(0.0, min(1.0, elapsed / op._hover_dwell))
            # Full ring (faint)
            segs = 24
            ring = []
            for i in range(segs + 1):
                a = 2 * math.pi * i / segs
                ring.append((scr.x + 10 * math.cos(a), scr.y + 10 * math.sin(a)))
            gpu.state.line_width_set(1.5)
            shader.bind()
            shader.uniform_float("color", (1.0, 0.55, 0.0, 0.3))
            batch = batch_for_shader(shader, 'LINE_STRIP', {"pos": ring})
            batch.draw(shader)
            # Progress arc (bright, from top, clockwise)
            arc_segs = max(2, int(segs * progress))
            arc = []
            for i in range(arc_segs + 1):
                a = -math.pi / 2 + 2 * math.pi * (i / segs)
                arc.append((scr.x + 10 * math.cos(a), scr.y + 10 * math.sin(a)))
            gpu.state.line_width_set(2.5)
            shader.uniform_float("color", hover_color)
            batch = batch_for_shader(shader, 'LINE_STRIP', {"pos": arc})
            batch.draw(shader)

    # Draw dashed lines for active track axes (axis-aligned, fixed in world space)
    if op._active_track_lines:
        gpu.state.line_width_set(1.5)
        for tp, axis in op._active_track_lines:
            # Build two world points far apart along the relevant world axis
            # axis 'x' = vertical line of constant world X (varies in Y)
            # axis 'y' = horizontal line of constant world Y (varies in X)
            extent = 1000.0  # meters - far enough to cover any view
            if axis == 'x':
                wp1 = Vector((tp.x, tp.y - extent, 0))
                wp2 = Vector((tp.x, tp.y + extent, 0))
            else:
                wp1 = Vector((tp.x - extent, tp.y, 0))
                wp2 = Vector((tp.x + extent, tp.y, 0))
            sp1 = view3d_utils.location_3d_to_region_2d(region, rv3d, wp1)
            sp2 = view3d_utils.location_3d_to_region_2d(region, rv3d, wp2)
            if sp1 is None or sp2 is None:
                continue
            p1 = Vector((sp1.x, sp1.y))
            p2 = Vector((sp2.x, sp2.y))
            direction = p2 - p1
            if direction.length < 1:
                continue
            direction.normalize()
            total = (p2 - p1).length
            # Build dashed segments along the projected line
            dash = 8
            gap = 5
            step = dash + gap
            verts = []
            d = 0.0
            while d < total:
                a = p1 + direction * d
                b = p1 + direction * min(d + dash, total)
                verts.append((a.x, a.y))
                verts.append((b.x, b.y))
                d += step
            shader.bind()
            shader.uniform_float("color", tp_line_color)
            batch = batch_for_shader(shader, 'LINES', {"pos": verts})
            batch.draw(shader)

    gpu.state.line_width_set(1.0)


def draw_wall_snap_indicator(op, context):
    """GPU draw callback: renders snap indicators during wall drawing."""
    region = op.region
    if region is None:
        return

    from bpy_extras import view3d_utils

    gpu.state.blend_set('ALPHA')

    if not op.has_start_point:
        # --- Phase 1: Before first point, show indicator at cursor ---
        if op.snap_wall and (op.snap_endpoint or op.snap_surface):
            # Snap active — draw indicator at the snap location
            snap_pos = op.snap_location if op.snap_location else op.hit_location
            if snap_pos is None:
                gpu.state.blend_set('NONE')
                return
            loc_2d = view3d_utils.location_3d_to_region_2d(
                region, region.data, Vector(snap_pos))
            if loc_2d is None:
                gpu.state.blend_set('NONE')
                return
            color = (0.0, 1.0, 0.4, 0.9)
            _draw_snap_point(loc_2d.x, loc_2d.y, color, 12, 8,
                             diamond=bool(op.snap_surface))
            # Draw left/right dimensions along the target wall face
            if op.snap_surface and op.snap_location:
                # Gap = drawing wall thickness
                # Direction based on which face: back face means the
                # wall body (thickness) extends in the target wall's
                # +Y direction, which projects as +X along the face.
                # Front face is the opposite.
                draw_thickness = context.scene.home_builder.wall_thickness
                p1_gap_dir = 1.0 if op.snap_surface == 'back' else -1.0
                _draw_wall_snap_dimensions(
                    region, op.snap_wall,
                    Vector(op.snap_location), op.snap_surface,
                    drawing_gap=draw_thickness, gap_direction=p1_gap_dir)
        else:
            # No snap — draw indicator at cursor position directly.
            # Using mouse_pos avoids the XY jump that occurs when the
            # raycast alternates between hitting the wall top face and
            # the floor in a slightly tilted plan view.
            if op.mouse_pos:
                _draw_snap_point(op.mouse_pos.x, op.mouse_pos.y,
                                 (1.0, 1.0, 1.0, 0.7), 8, 6)

    else:
        # --- Phase 2: During drawing, show indicator at wall endpoint ---
        if op.current_wall is None or op.start_point is None:
            gpu.state.blend_set('NONE')
            return

        wall_length = op.current_wall.get_input('Length')
        angle = op.current_wall.obj.rotation_euler.z
        end_3d = Vector((
            op.start_point.x + math.cos(angle) * wall_length,
            op.start_point.y + math.sin(angle) * wall_length,
            0,
        ))

        end_2d = view3d_utils.location_3d_to_region_2d(
            region, region.data, end_3d)
        if end_2d is None:
            gpu.state.blend_set('NONE')
            return

        if op.close_snap_active:
            # Closing the room - bright green diamond at the start point
            color = (0.2, 1.0, 0.2, 0.95)
            _draw_snap_point(end_2d.x, end_2d.y, color, 14, 9, diamond=True)
        elif op.end_snap_wall:
            color = (0.0, 1.0, 0.4, 0.9)
            _draw_snap_point(end_2d.x, end_2d.y, color, 12, 8, diamond=True)
            # Draw left/right dimensions along the target wall face
            # Compute gap: drawing wall thickness projected onto target face
            draw_thickness = op.current_wall.get_input('Thickness')
            draw_angle = op.current_wall.obj.rotation_euler.z
            draw_perp = Vector((-math.sin(draw_angle), math.cos(draw_angle)))
            tw = op.end_snap_wall.matrix_world
            target_dir = Vector((tw[0][0], tw[1][0])).normalized()
            proj = draw_perp.dot(target_dir)
            gap = abs(proj) * draw_thickness
            gap_dir = 1.0 if proj > 0 else (-1.0 if proj < 0 else 0)
            _draw_wall_snap_dimensions(
                region, op.end_snap_wall, end_3d, op.end_snap_face,
                drawing_gap=gap, gap_direction=gap_dir)
        else:
            _draw_snap_point(end_2d.x, end_2d.y, (1.0, 1.0, 1.0, 0.7), 8, 6)

    # Track indicators (acquired points, hover candidate, active axis lines)
    _draw_track_indicators(op, region, context)

    gpu.state.blend_set('NONE')

class home_builder_walls_OT_draw_walls(bpy.types.Operator, hb_placement.PlacementMixin):
    bl_idname = "home_builder_walls.draw_walls"
    bl_label = "Draw Walls"
    bl_description = "Enter Draw Walls Mode. Click to place points, type for exact length, Escape to cancel"
    bl_options = {'UNDO'}

    # Wall-specific state
    current_wall = None
    previous_wall = None
    start_point: Vector = None
    dim = None
    
    # Track if we've placed the first point
    has_start_point: bool = False
    
    # Free rotation mode (Alt toggles, snaps to 15° increments)
    free_rotation: bool = False
    
    # Endpoint snapping state
    snap_wall = None  # Wall we're snapping to
    snap_endpoint = None  # 'start' or 'end'
    snap_surface = None  # 'front' or 'back' for surface snapping
    snap_location = None  # Snap location for surface snapping
    highlighted_wall = None  # Currently highlighted wall object

    def get_default_typing_target(self):
        """When user starts typing, they're entering wall length."""
        return hb_placement.TypingTarget.LENGTH

    def find_nearby_wall_endpoint(self, context, threshold=0.15):
        """
        Find if mouse is near any existing wall endpoint.
        
        Args:
            context: Blender context
            threshold: Distance threshold in meters
            
        Returns:
            Tuple of (wall_obj, endpoint_type, endpoint_location) or (None, None, None)
            endpoint_type is 'start' or 'end'
        """
        if not self.hit_location:
            return None, None, None
        
        mouse_loc = Vector((self.hit_location[0], self.hit_location[1], 0))
        
        best_wall = None
        best_endpoint = None
        best_location = None
        best_distance = threshold
        
        for obj in context.view_layer.objects:
            if 'IS_WALL_BP' not in obj:
                continue
            # Skip the current wall being drawn
            if self.current_wall and obj == self.current_wall.obj:
                continue
            # Skip the previously drawn wall
            if self.previous_wall and obj == self.previous_wall.obj:
                continue
            
            # Get wall endpoints
            start, end = get_wall_endpoints(obj)
            start_3d = Vector((start.x, start.y, 0))
            end_3d = Vector((end.x, end.y, 0))
            
            # Check start point
            dist_start = (mouse_loc - start_3d).length
            if dist_start < best_distance:
                best_distance = dist_start
                best_wall = obj
                best_endpoint = 'start'
                best_location = start_3d
            
            # Check end point
            dist_end = (mouse_loc - end_3d).length
            if dist_end < best_distance:
                best_distance = dist_end
                best_wall = obj
                best_endpoint = 'end'
                best_location = end_3d
        
        return best_wall, best_endpoint, best_location

    def highlight_wall(self, wall_obj, highlight=True):
        """Highlight or unhighlight a wall."""
        if wall_obj is None:
            return
        
        # Check if object is still valid and in the view layer
        try:
            if wall_obj.name not in bpy.context.view_layer.objects:
                return
        except ReferenceError:
            return
        
        if highlight:
            # Store original color and set highlight color
            if 'original_color' not in wall_obj:
                wall_obj['original_color'] = list(wall_obj.color)
            wall_obj.color = (0.0, 1.0, 0.5, 1.0)  # Green highlight
            wall_obj.select_set(True)
        else:
            # Restore original color
            if 'original_color' in wall_obj:
                wall_obj.color = wall_obj['original_color']
                del wall_obj['original_color']
            wall_obj.select_set(False)

    def clear_wall_highlight(self):
        """Clear any highlighted wall."""
        if self.highlighted_wall:
            try:
                # Check if object is still valid before trying to unhighlight
                if self.highlighted_wall.name in bpy.context.view_layer.objects:
                    self.highlight_wall(self.highlighted_wall, highlight=False)
            except ReferenceError:
                pass
            self.highlighted_wall = None
        self.snap_wall = None
        self.snap_endpoint = None
        self.snap_surface = None
        self.snap_location = None

    def is_top_view(self, context):
        """Check if we're looking from above (top-ish view)."""
        view_matrix = context.region_data.view_matrix
        # Get the view direction (negative Z of view matrix = looking direction)
        view_dir = Vector((view_matrix[2][0], view_matrix[2][1], view_matrix[2][2]))
        # If view direction is mostly vertical (looking down), we're in top view
        # Check if the Z component dominates
        return abs(view_dir.z) > 0.7

    def find_wall_surface_snap_2d(self, context, threshold=0.15):
        """
        2D proximity-based wall surface detection for top view.
        Uses local-space projection with hysteresis to prevent face flicker.

        Instead of relying on hit_location (which comes from a raycast and
        shifts with view tilt depending on whether it hit the wall top face
        or the floor), we project the mouse cursor directly onto z=0 using
        the view ray.  This gives a stable, consistent XY every frame.

        Wall origin is at back face (local Y=0), front face is at Y=thickness.

        Returns:
            Tuple of (wall_obj, snap_location, face) or (None, None, None)
        """
        # Project cursor onto z=0 for a stable 2D position regardless
        # of what the raycast happened to hit (wall top vs floor).
        origin = view3d_utils.region_2d_to_origin_3d(
            self.region, self.region.data, self.mouse_pos)
        direction = view3d_utils.region_2d_to_vector_3d(
            self.region, self.region.data, self.mouse_pos)
        co = intersect_line_plane(
            origin, origin + direction, Vector((0, 0, 0)), Vector((0, 0, 1)))
        if co is None:
            return None, None, None

        mouse_2d = Vector((co.x, co.y))

        best_wall = None
        best_location = None
        best_face = None
        best_distance = threshold

        for obj in context.view_layer.objects:
            if 'IS_WALL_BP' not in obj:
                continue
            if self.current_wall and obj == self.current_wall.obj:
                continue
            if self.previous_wall and obj == self.previous_wall.obj:
                continue

            wall = hb_types.GeoNodeWall(obj)
            # Skip walls whose geo node modifier has been applied/removed -
            # they are no longer parametric and cannot report Length/Thickness.
            if not wall.has_modifier():
                continue
            wall_length = wall.get_input('Length')
            wall_thickness = wall.get_input('Thickness')

            world_matrix = obj.matrix_world

            # Wall axes in world space
            wall_dir = Vector((world_matrix[0][0], world_matrix[1][0])).normalized()
            wall_perp = Vector((world_matrix[0][1], world_matrix[1][1])).normalized()
            wall_origin = Vector((world_matrix[0][3], world_matrix[1][3]))

            # Project mouse into wall's local 2D space
            to_mouse = mouse_2d - wall_origin
            local_along = to_mouse.dot(wall_dir)
            local_perp = to_mouse.dot(wall_perp)

            # Check if cursor is alongside the wall (with threshold margin)
            if local_along < -threshold or local_along > wall_length + threshold:
                continue

            # Determine perpendicular distance to each face
            dist_to_back = abs(local_perp)
            dist_to_front = abs(local_perp - wall_thickness)

            # Hysteresis: if we were already snapped to a face on this wall,
            # keep the current face unless cursor clearly crosses to the
            # other side.  Applied even when the cursor is just outside the
            # wall boundary so that thin-wall edge jitter doesn't reset it.
            inside_wall = 0 <= local_perp <= wall_thickness

            if (self._last_surface_wall == obj
                    and self._last_surface_face is not None):
                if local_perp < 0:
                    face = 'back'
                elif local_perp > wall_thickness:
                    face = 'front'
                elif self._last_surface_face == 'back':
                    if local_perp > wall_thickness * 0.7:
                        face = 'front'
                    else:
                        face = 'back'
                else:
                    if local_perp < wall_thickness * 0.3:
                        face = 'back'
                    else:
                        face = 'front'
            else:
                # No hysteresis — pick nearest face
                if dist_to_back <= dist_to_front:
                    face = 'back'
                else:
                    face = 'front'

            face_offset = 0 if face == 'back' else wall_thickness
            perp_dist = dist_to_back if face == 'back' else dist_to_front

            # Skip if too far from the nearest face
            if perp_dist > threshold:
                if not inside_wall:
                    continue
                # Inside the wall — perp_dist to chosen face may exceed threshold
                # but we still want to snap
                perp_dist = min(dist_to_back, dist_to_front)

            # Snap point: clamp along-position to wall extent, project onto face
            clamped_along = max(0, min(wall_length, local_along))
            snap_world = wall_origin + wall_dir * clamped_along + wall_perp * face_offset

            if perp_dist < best_distance:
                best_distance = perp_dist
                best_wall = obj
                best_location = Vector((snap_world.x, snap_world.y, 0))
                best_face = face

        # Update hysteresis state only when a wall is found.
        # Keeping stale state on a missed frame prevents a single bad
        # raycast from resetting face memory.
        if best_wall is not None:
            self._last_surface_wall = best_wall
            self._last_surface_face = best_face

        return best_wall, best_location, best_face


    def find_wall_surface_snap(self, context):
        """
        Find if mouse is over/near a wall surface.
        Uses raycast in perspective/side views, 2D proximity in top view.
        
        Returns:
            Tuple of (wall_obj, snap_location, face) or (None, None, None)
            face is 'front' or 'back'
        """
        # In top view, use 2D proximity detection
        if self.is_top_view(context):
            return self.find_wall_surface_snap_2d(context)
        
        # Otherwise use raycast-based detection
        if not self.hit_object or not self.hit_location:
            return None, None, None
        
        # Check if we hit a wall (could be the wall itself or a child)
        wall_obj = None
        check_obj = self.hit_object
        while check_obj:
            if 'IS_WALL_BP' in check_obj:
                wall_obj = check_obj
                break
            check_obj = check_obj.parent
        
        if not wall_obj:
            return None, None, None
        
        # Skip the current wall being drawn
        if self.current_wall and wall_obj == self.current_wall.obj:
            return None, None, None
        # Skip the previously drawn wall
        if self.previous_wall and wall_obj == self.previous_wall.obj:
            return None, None, None
        
        wall = hb_types.GeoNodeWall(wall_obj)
        # The wall may have had its geo node modifier applied (baked to mesh).
        # Without the modifier we can't query Length/Thickness, so bail out
        # and let the caller treat it as a non-snap target.
        if not wall.has_modifier():
            return None, None, None
        wall_length = wall.get_input('Length')
        wall_thickness = wall.get_input('Thickness')
        
        # Transform hit position to wall's local space
        world_matrix = wall_obj.matrix_world
        local_matrix = world_matrix.inverted()
        local_hit = local_matrix @ Vector((self.hit_location[0], self.hit_location[1], self.hit_location[2]))
        
        # Clamp X position to wall length
        snap_x = max(0, min(wall_length, local_hit.x))
        
        # Determine which face based on local Y
        if local_hit.y >= 0:
            face = 'front'
        else:
            face = 'back'
        
        # Keep the Y from the hit (it's on the surface), set Z to 0
        local_snap = Vector((snap_x, local_hit.y, 0))
        world_snap = world_matrix @ local_snap
        
        return wall_obj, Vector((world_snap.x, world_snap.y, 0)), face


    def find_end_wall_snap(self, context, threshold=0.15):
        """
        Check if the current wall's endpoint is near or would cross an existing wall face.
        Snaps the wall length so it ends cleanly at the front or back face.
        
        When the wall would pass through both faces of an existing wall,
        snaps to the FIRST face hit (smallest t) so the wall stops at the
        near side rather than punching through.

        Returns:
            (snap_length, wall_obj, face) or (None, None, None)
        """
        if not self.current_wall or not self.has_start_point:
            return None, None, None

        wall_length = self.current_wall.get_input('Length')
        if wall_length < 0.01:
            return None, None, None

        angle = self.current_wall.obj.rotation_euler.z
        wd = Vector((math.cos(angle), math.sin(angle)))
        wp = Vector((self.start_point.x, self.start_point.y))

        best_t = None
        best_wall = None
        best_face = None
        best_score = float('inf')

        for obj in context.view_layer.objects:
            if 'IS_WALL_BP' not in obj:
                continue
            if obj == self.current_wall.obj:
                continue
            if self.previous_wall and obj == self.previous_wall.obj:
                continue

            ew = hb_types.GeoNodeWall(obj)
            if not ew.has_modifier():
                continue
            el = ew.get_input('Length')
            et = ew.get_input('Thickness')

            wm = obj.matrix_world
            ed = Vector((wm[0][0], wm[1][0])).normalized()
            ep = Vector((wm[0][1], wm[1][1])).normalized()
            eo = Vector((wm[0][3], wm[1][3]))

            # Collect valid face hits for this wall, then pick the best
            wall_hits = []

            for face, offset in [('back', 0), ('front', et)]:
                fs = eo + ep * offset
                fd = ed

                denom = wd.x * fd.y - wd.y * fd.x

                if abs(denom) < 1e-10:
                    # Parallel - check endpoint proximity to face line
                    end_pt = wp + wd * wall_length
                    to_end = end_pt - fs
                    s = to_end.dot(fd)
                    if 0 <= s <= el:
                        closest = fs + fd * s
                        dist = (end_pt - closest).length
                        if dist < threshold:
                            snap_t = (closest - wp).dot(wd)
                            if snap_t > 0.01:
                                wall_hits.append((snap_t, face, dist))
                    continue

                diff = fs - wp
                t = (diff.x * fd.y - diff.y * fd.x) / denom
                s = (diff.x * wd.y - diff.y * wd.x) / denom

                if t < 0.01:
                    continue
                if s < -0.01 or s > el + 0.01:
                    continue

                dist_to_end = abs(t - wall_length)

                if dist_to_end < threshold or t < wall_length:
                    wall_hits.append((t, face, dist_to_end))

            if not wall_hits:
                continue

            # Pick the first face the wall would hit (smallest t)
            wall_hits.sort(key=lambda h: h[0])
            hit_t, hit_face, hit_dist = wall_hits[0]

            # Score across all walls: prefer closest to current endpoint,
            # but strongly prefer any crossing (t < wall_length)
            if hit_t < wall_length:
                score = -1000 + hit_t  # Crossings always win, prefer earliest
            else:
                score = hit_dist

            if score < best_score:
                best_score = score
                best_t = hit_t
                best_wall = obj
                best_face = hit_face

        return best_t, best_wall, best_face

    def find_chain_start(self, wall_obj):
        """Trace back through wall chain to find the first wall and count walls.
        
        Returns:
            Tuple of (first_wall_obj, wall_count) or (None, 0)
        """
        visited = set()
        current = hb_types.GeoNodeWall(wall_obj)
        count = 1
        
        while True:
            visited.add(current.obj.name)
            left_wall = current.get_connected_wall('left')
            if left_wall and left_wall.obj.name not in visited:
                current = left_wall
                count += 1
            else:
                break
        
        return current, count

    def connect_to_existing_wall(self, wall_obj, endpoint):
        """
        Connect current wall to an existing wall's endpoint and set up for continued drawing.
        
        Args:
            wall_obj: The existing wall to connect to
            endpoint: 'start' or 'end' - which endpoint to connect to
        """
        existing_wall = hb_types.GeoNodeWall(wall_obj)
        
        # Get the endpoint location
        start, end = get_wall_endpoints(wall_obj)
        
        if endpoint == 'end':
            # Connect to end of existing wall - our wall starts there
            connect_location = Vector((end.x, end.y, 0))
            # Set previous_wall so our wall connects properly
            self.previous_wall = existing_wall
            # Use constraint to connect
            self.current_wall.connect_to_wall(existing_wall)
            
            # Trace chain to find first wall for room closing
            first_wall_geonode, chain_count = self.find_chain_start(wall_obj)
            if chain_count >= 2:
                self.first_wall = first_wall_geonode
                self.confirmed_wall_count = chain_count
                # Seed first_start_point from the first wall's actual origin so
                # close-on-click works the same as the C key after a continue.
                fl = first_wall_geonode.obj.location
                self.first_start_point = Vector((fl.x, fl.y, 0))
        else:
            # Connect to start of existing wall
            connect_location = Vector((start.x, start.y, 0))
            # Position our wall at the start point
            self.current_wall.obj.location = connect_location
        
        self.start_point = connect_location
        self.has_start_point = True

    def on_typed_value_changed(self):
        """Update dimension display as user types."""
        if self.typed_value:
            parsed = self.parse_typed_distance()
            if parsed is not None and self.current_wall:
                self.current_wall.set_input('Length', parsed)
                self.update_dimension(bpy.context)
        self.update_header(bpy.context)

    def apply_typed_value(self):
        """Apply typed length and advance to next wall."""
        parsed = self.parse_typed_distance()
        if parsed is not None and self.current_wall:
            self.current_wall.set_input('Length', parsed)
            self.update_dimension(bpy.context)
            # Confirm this wall and start next
            self.confirm_current_wall()
        self.stop_typing()

    def create_wall(self, context):
        """Create a new wall segment based on wall_type setting."""
        props = context.scene.home_builder
        wall_type = props.wall_type

        # Determine height based on wall type
        if wall_type in {'Exterior', 'Interior'}:
            height = props.ceiling_height
        elif wall_type == 'Half':
            height = props.half_wall_height
        else:  # Fake
            height = props.fake_wall_height

        # Determine thickness based on wall type
        if wall_type == 'Exterior':
            thickness = props.exterior_wall_thickness
        elif wall_type in {'Interior', 'Half'}:
            thickness = props.interior_wall_thickness
        else:  # Fake — thin decorative panel
            thickness = units.inch(0.75)

        self.current_wall = hb_types.GeoNodeWall()
        self.current_wall.create("Wall")
        self.current_wall.set_input('Thickness', thickness)
        self.current_wall.set_input('Height', height)

        # Tag with wall type for identification
        self.current_wall.obj['WALL_TYPE'] = wall_type
        if wall_type == 'Half':
            self.current_wall.obj['IS_HALF_WALL'] = True
        elif wall_type == 'Fake':
            self.current_wall.obj['IS_FAKE_WALL'] = True
        
        # Register for cleanup on cancel
        self.register_placement_object(self.current_wall.obj)
        for child in self.current_wall.obj.children:
            self.register_placement_object(child)
        
        if self.previous_wall:
            self.current_wall.connect_to_wall(self.previous_wall)

    def create_dimension(self):
        """Register the GPU draw handler that renders the live wall length
        dimension. Replaces the legacy GeoNodeDimension scene-object approach."""
        self._wall_dim_visible = False
        if getattr(self, '_wall_dim_handle', None) is None:
            self._wall_dim_handle = bpy.types.SpaceView3D.draw_handler_add(
                _draw_wall_length_dim, (self,), 'WINDOW', 'POST_PIXEL')

    def _remove_dim_handler(self):
        """Remove the wall length dimension GPU draw handler."""
        if getattr(self, '_wall_dim_handle', None) is not None:
            try:
                bpy.types.SpaceView3D.draw_handler_remove(self._wall_dim_handle, 'WINDOW')
            except (ValueError, RuntimeError):
                pass
            self._wall_dim_handle = None
        self._wall_dim_visible = False

    def get_view_distance(self, context):
        """Get the current view distance for scaling UI elements."""
        try:
            for area in context.screen.areas:
                if area.type == 'VIEW_3D':
                    for space in area.spaces:
                        if space.type == 'VIEW_3D':
                            return space.region_3d.view_distance
        except:
            pass
        return 10.0  # Default fallback

    def update_dimension(self, context=None):
        """Mark the wall length dimension visible. The GPU draw handler
        reads live length/height from self.current_wall every frame, so
        there is no per-update state to push here."""
        if self.current_wall is not None:
            self._wall_dim_visible = True

    # ========== Wall Tracking ==========
    
    def find_nearby_endpoint_for_tracking(self, context, threshold=0.15):
        """Find a nearby wall endpoint for track point acquisition.
        
        Like find_nearby_wall_endpoint but only skips the current wall being
        drawn so we can track off the previously drawn wall too.
        """
        if not self.hit_location:
            return None
        mouse_loc = Vector((self.hit_location[0], self.hit_location[1], 0))
        best_loc = None
        best_dist = threshold
        for obj in context.view_layer.objects:
            if 'IS_WALL_BP' not in obj:
                continue
            if self.current_wall and obj == self.current_wall.obj:
                continue
            start, end = get_wall_endpoints(obj)
            for pt in (start, end):
                pt_3d = Vector((pt.x, pt.y, 0))
                d = (mouse_loc - pt_3d).length
                if d < best_dist:
                    best_dist = d
                    best_loc = pt_3d
        return best_loc
    
    def find_existing_track_point_at(self, loc, eps=0.01):
        """Return an existing track point near loc, or None."""
        if loc is None:
            return None
        for tp in self.track_points:
            if (tp - loc).length < eps:
                return tp
        return None
    
    def update_track_hover(self, context):
        """Detect dwell-based track point acquisition.
        
        Called every modal event. If the cursor stays on an endpoint that
        is not already a track point for self._hover_dwell seconds, that
        endpoint is promoted to a track point.
        """
        import time
        now = time.time()
        candidate = self.find_nearby_endpoint_for_tracking(context)
        if candidate is None:
            self._hover_candidate = None
            self._hover_start_time = 0.0
            return
        if self.find_existing_track_point_at(candidate) is not None:
            # Already acquired - clear hover so we don't try to re-add
            self._hover_candidate = None
            self._hover_start_time = 0.0
            return
        if self._hover_candidate is None or (self._hover_candidate - candidate).length > 0.001:
            self._hover_candidate = candidate.copy()
            self._hover_start_time = now
            return
        if now - self._hover_start_time >= self._hover_dwell:
            self.track_points.append(candidate.copy())
            self._hover_candidate = None
            self._hover_start_time = 0.0
    
    def acquire_or_remove_track_point_at_cursor(self, context):
        """T key handler: acquire endpoint at cursor, or remove if already a track point."""
        candidate = self.find_nearby_endpoint_for_tracking(context)
        if candidate is None:
            return False
        existing = self.find_existing_track_point_at(candidate)
        if existing is not None:
            self.track_points.remove(existing)
        else:
            self.track_points.append(candidate.copy())
        self._hover_candidate = None
        self._hover_start_time = 0.0
        return True
    
    def apply_track_snap_to_position(self, context, world_pos):
        """Apply tracking to a world position.
        
        Returns (new_pos, snapped_axes) where snapped_axes is a list of
        (track_point, 'x'|'y') tuples describing what was snapped.
        """
        if not self.track_points or self.region is None or self.mouse_pos is None:
            return Vector(world_pos), []
        region = self.region
        rv3d = region.data
        mouse2d = Vector((self.mouse_pos.x, self.mouse_pos.y))
        threshold = self._track_pixel_threshold
        
        best_x = None
        best_y = None
        for tp in self.track_points:
            # Vertical line through tp.x: closest point at (tp.x, world_pos.y, 0)
            cp = Vector((tp.x, world_pos.y, 0))
            scr = view3d_utils.location_3d_to_region_2d(region, rv3d, cp)
            if scr is not None:
                d = (mouse2d - scr).length
                if d < threshold and (best_x is None or d < best_x[0]):
                    best_x = (d, tp)
            # Horizontal line through tp.y
            cp = Vector((world_pos.x, tp.y, 0))
            scr = view3d_utils.location_3d_to_region_2d(region, rv3d, cp)
            if scr is not None:
                d = (mouse2d - scr).length
                if d < threshold and (best_y is None or d < best_y[0]):
                    best_y = (d, tp)
        
        new_pos = Vector(world_pos)
        snapped_axes = []
        if best_x is not None:
            new_pos.x = best_x[1].x
            snapped_axes.append((best_x[1], 'x'))
        if best_y is not None:
            new_pos.y = best_y[1].y
            snapped_axes.append((best_y[1], 'y'))
        return new_pos, snapped_axes
    
    def clear_track_points(self):
        """Clear all acquired track points and hover state."""
        self.track_points = []
        self._hover_candidate = None
        self._hover_start_time = 0.0
        self._active_track_lines = []
    
    def _remove_track_timer(self, context):
        """Remove the modal timer used for dwell detection."""
        if getattr(self, '_track_timer', None) is not None:
            try:
                context.window_manager.event_timer_remove(self._track_timer)
            except Exception:
                pass
            self._track_timer = None
    
    # ========== End Wall Tracking ==========
    
    def set_wall_position_from_mouse(self):
        """Update wall position/rotation based on mouse location."""
        # Apply track snapping to cursor (skipped if a higher-priority snap is active)
        higher_priority_snap = bool(self.snap_wall and (self.snap_endpoint or self.snap_surface))
        if self.hit_location and not higher_priority_snap:
            eff_vec, axes = self.apply_track_snap_to_position(
                bpy.context, Vector(self.hit_location))
            self._active_track_lines = axes
        else:
            eff_vec = Vector(self.hit_location) if self.hit_location else None
            self._active_track_lines = []
        track_active = bool(self._active_track_lines)

        if not self.has_start_point:
            # First point - move wall origin
            if eff_vec is not None:
                if higher_priority_snap:
                    # Use exact snap position (no grid snap) for wall face/endpoint snaps
                    self.current_wall.obj.location = Vector(self.hit_location)
                elif track_active:
                    # Track snap - use exact tracked position, no grid snap
                    self.current_wall.obj.location = eff_vec
                else:
                    snapped_loc = hb_snap.snap_vector_to_grid(eff_vec, fine=self.fine_snap)
                    self.current_wall.obj.location = snapped_loc
        else:
            # Drawing length - calculate from start point
            if eff_vec is None:
                return

            # Close-room snap: if cursor is near the first wall's start point
            # and we have 2+ confirmed walls, snap the end of this wall to it
            # and arm close-on-click.
            self.close_snap_active = False
            if (self.first_start_point is not None
                    and self.confirmed_wall_count >= 2
                    and self.first_wall is not None):
                close_threshold = 0.15
                d = (Vector((eff_vec.x, eff_vec.y, 0))
                     - Vector((self.first_start_point.x, self.first_start_point.y, 0))).length
                if d < close_threshold:
                    cx = self.first_start_point.x - self.start_point[0]
                    cy = self.first_start_point.y - self.start_point[1]
                    close_len = math.sqrt(cx * cx + cy * cy)
                    if close_len > 0.001:
                        self.current_wall.obj.rotation_euler.z = math.atan2(cy, cx)
                        self.current_wall.set_input('Length', close_len)
                        self.close_snap_active = True
                        # Clear any face-snap state so close takes priority
                        if self.end_snap_wall:
                            self.end_snap_wall = None
                            self.end_snap_face = None
                            self.clear_wall_highlight()
                        self.update_dimension(bpy.context)
                        return

            x = eff_vec.x - self.start_point[0]
            y = eff_vec.y - self.start_point[1]
            
            if self.free_rotation:
                # Free rotation mode - snap to 15° increments
                angle = math.atan2(y, x)
                snap_angle = round(math.degrees(angle) / 15) * 15
                self.current_wall.obj.rotation_euler.z = math.radians(snap_angle)
                length = math.sqrt(x * x + y * y)
                if track_active:
                    self.current_wall.set_input('Length', length)
                else:
                    self.current_wall.set_input('Length', hb_snap.snap_value_to_grid(length, fine=self.fine_snap))
            else:
                # Default mode - snap to orthogonal (90°) directions
                if abs(x) > abs(y):
                    if x > 0:
                        self.current_wall.obj.rotation_euler.z = math.radians(0)
                    else:
                        self.current_wall.obj.rotation_euler.z = math.radians(180)
                    if track_active:
                        self.current_wall.set_input('Length', abs(x))
                    else:
                        self.current_wall.set_input('Length', hb_snap.snap_value_to_grid(abs(x), fine=self.fine_snap))
                else:
                    if y > 0:
                        self.current_wall.obj.rotation_euler.z = math.radians(90)
                    else:
                        self.current_wall.obj.rotation_euler.z = math.radians(-90)
                    if track_active:
                        self.current_wall.set_input('Length', abs(y))
                    else:
                        self.current_wall.set_input('Length', hb_snap.snap_value_to_grid(abs(y), fine=self.fine_snap))

            # Check for end snap to existing wall faces
            snap_len, snap_wall_obj, snap_face = self.find_end_wall_snap(bpy.context)
            if snap_len is not None:
                self.current_wall.set_input('Length', snap_len)
                self.end_snap_wall = snap_wall_obj
                self.end_snap_face = snap_face
                # Highlight the target wall
                if snap_wall_obj != self.highlighted_wall:
                    self.clear_wall_highlight()
                    self.highlight_wall(snap_wall_obj, highlight=True)
                    self.highlighted_wall = snap_wall_obj
            else:
                if self.end_snap_wall:
                    self.end_snap_wall = None
                    self.end_snap_face = None
                    self.clear_wall_highlight()

            self.update_dimension(bpy.context)

    def close_room(self, context):
        """Close the room by connecting the current wall back to the first wall."""
        closing_wall = self.current_wall
        first_wall = self.first_wall
        
        # Calculate angle and distance to first wall's origin
        first_loc = first_wall.obj.location
        dx = first_loc.x - self.start_point.x
        dy = first_loc.y - self.start_point.y
        closing_length = math.sqrt(dx * dx + dy * dy)
        
        if closing_length < 0.01:
            return
        
        closing_angle = math.atan2(dy, dx)
        closing_wall.obj.rotation_euler.z = closing_angle
        closing_wall.set_input('Length', closing_length)
        
        # Connect closing wall's end to first wall
        closing_wall.obj_x.home_builder.connected_object = first_wall.obj
        
        context.view_layer.update()
        
        # Update miter angles for previous wall and closing wall's left side
        calculate_wall_miter_angles(closing_wall.obj)
        calculate_wall_miter_angles(self.previous_wall.obj)
        
        # Set miter angles between closing wall's end and first wall's start
        closing_rot = closing_wall.obj.rotation_euler.z
        first_rot = first_wall.obj.rotation_euler.z
        turn = first_rot - closing_rot
        while turn > math.pi: turn -= 2 * math.pi
        while turn < -math.pi: turn += 2 * math.pi
        closing_wall.set_input('Right Angle', -turn / 2)
        first_wall.set_input('Left Angle', turn / 2)
        
        # Remove closing wall from cancel list (it's confirmed)
        if closing_wall.obj in self.placement_objects:
            self.placement_objects.remove(closing_wall.obj)
        for child in closing_wall.obj.children:
            if child in self.placement_objects:
                self.placement_objects.remove(child)
        
        # Hide the live wall length dimension — the room is closed
        self._wall_dim_visible = False

    def confirm_current_wall(self):
        """Finalize current wall and prepare for next."""
        # Capture the very first start point (before it gets updated)
        if self.first_start_point is None:
            self.first_start_point = self.start_point.copy()
        
        # Update start point to end of current wall
        wall_length = self.current_wall.get_input('Length')
        angle = self.current_wall.obj.rotation_euler.z
        
        self.start_point = Vector((
            self.start_point.x + math.cos(angle) * wall_length,
            self.start_point.y + math.sin(angle) * wall_length,
            0
        ))
        
        # Current wall becomes previous, remove from cancel list (it's confirmed)
        if self.current_wall.obj in self.placement_objects:
            self.placement_objects.remove(self.current_wall.obj)
        # Also remove the wall's obj_x object from cancel list
        for child in self.current_wall.obj.children:
            if 'obj_x' in child and child in self.placement_objects:
                self.placement_objects.remove(child)

        # Update miter angles for this wall and connected walls
        update_connected_wall_miters(self.current_wall.obj)

        self.confirmed_wall_count += 1
        if self.confirmed_wall_count == 1:
            self.first_wall = self.current_wall
        self.previous_wall = self.current_wall

        # Auto-clear track points after each wall is confirmed
        self.clear_track_points()

        self.create_wall(bpy.context)

    def _show_wall_objects(self):
        """Show the wall after first point is placed and enable the live
        length dimension."""
        self.current_wall.obj.hide_set(False)
        for child in self.current_wall.obj.children:
            child.hide_set(False)
        self._wall_dim_visible = True

    def _remove_snap_indicator(self):
        """Remove the snap indicator draw handler if still active."""
        if self._snap_draw_handle:
            bpy.types.SpaceView3D.draw_handler_remove(self._snap_draw_handle, 'WINDOW')
            self._snap_draw_handle = None

    def update_header(self, context):
        """Update header text with instructions and current value."""
        if self.placement_state == hb_placement.PlacementState.TYPING:
            text = f"Wall Length: {self.typed_value}_ | Enter to confirm | Esc to cancel typing"
        elif self.has_start_point:
            length = self.current_wall.get_input('Length')
            length_str = units.unit_to_string(context.scene.unit_settings, length)
            angle_deg = round(math.degrees(self.current_wall.obj.rotation_euler.z))
            rotation_mode = "Free (15°)" if self.free_rotation else "Ortho (90°)"
            close_hint = " | C: close room (or click start)" if self.confirmed_wall_count >= 2 and self.first_wall is not None else ""
            snap_hint = f" [Snap: {self.end_snap_face} face]" if self.end_snap_wall else ""
            if self.close_snap_active:
                snap_hint = " [CLOSE]"
            fine_hint = " [Fine: 1/16\"]" if self.fine_snap else ""
            tp_count = len(self.track_points)
            track_hint = f" [Track: {tp_count}]" if tp_count else ""
            if self._active_track_lines:
                track_hint += " [TRACKING]"
            text = f"Length: {length_str} | Angle: {angle_deg}°{snap_hint}{fine_hint}{track_hint} | {rotation_mode} | Shift: fine | Alt: rotation | T: track | Click to place{close_hint}"
        else:
            tp_count = len(self.track_points)
            track_hint = f" [Track: {tp_count}]" if tp_count else ""
            if self._active_track_lines:
                track_hint += " [TRACKING]"
            if self.snap_wall and self.snap_endpoint:
                text = f"Click to connect to wall endpoint{track_hint} | T: track | Esc to cancel"
            elif self.snap_wall and self.snap_surface:
                text = f"Click to start on wall ({self.snap_surface} face){track_hint} | T: track | Esc to cancel"
            else:
                text = f"Click to place first point{track_hint} | T: track point (hover 0.5s or press T) | Esc to cancel"
        
        hb_placement.draw_header_text(context, text)

    def execute(self, context):
        # Initialize placement mixin
        self.init_placement(context)
        
        # Reset wall-specific state
        self.current_wall = None
        self.previous_wall = None
        self.start_point = None
        self.has_start_point = False
        self._wall_dim_handle = None
        self._wall_dim_visible = False
        self.free_rotation = False
        self.first_start_point = None
        self.first_wall = None
        self.confirmed_wall_count = 0
        
        # Reset endpoint snapping state
        self.snap_wall = None
        self.snap_endpoint = None
        self.snap_surface = None
        self.snap_location = None
        self.highlighted_wall = None
        
        # End-of-wall snap state (during drawing)
        self.end_snap_wall = None
        self.end_snap_face = None
        
        # Surface snap hysteresis (prevents face flicker in top view)
        self._last_surface_wall = None
        self._last_surface_face = None
        
        # Fine snap mode (Shift held = 1/16" imperial, 1mm metric)
        self.fine_snap = False

        # Draw handler for snap indicator
        self._snap_draw_handle = None

        # Create initial objects
        self.create_dimension()
        self.create_wall(context)

        # Hide wall until first point is placed (dim handler is gated
        # by self._wall_dim_visible, which starts False)
        self.current_wall.obj.hide_set(True)
        for child in self.current_wall.obj.children:
            child.hide_set(True)

        # Add GPU draw handler for snap indicator
        self._snap_draw_handle = bpy.types.SpaceView3D.draw_handler_add(
            draw_wall_snap_indicator, (self, context), 'WINDOW', 'POST_PIXEL')

        # Close-room snap state (active when cursor is near first wall's start point)
        self.close_snap_active = False

        # Wall tracking state (object snap tracking)
        self.track_points = []
        self._hover_candidate = None
        self._hover_start_time = 0.0
        self._hover_dwell = 0.5
        self._track_pixel_threshold = 8
        self._active_track_lines = []
        # Timer for dwell detection (fires even when mouse is still)
        self._track_timer = context.window_manager.event_timer_add(
            0.05, window=context.window)

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        context.window.cursor_set('CROSSHAIR')

        # Skip intermediate mouse moves
        if event.type == "INBETWEEN_MOUSEMOVE":
            return {'RUNNING_MODAL'}

        # Let mixin handle typing events first
        if self.handle_typing_event(event):
            self.update_header(context)
            return {'RUNNING_MODAL'}

        # Update snap (hide current wall during raycast so it does not
        # block hits on the geometry behind it)
        self.current_wall.obj.hide_set(True)
        for child in self.current_wall.obj.children:
            child.hide_set(True)
        self.update_snap(context, event)
        # Only unhide after first point is placed
        if self.has_start_point:
            self.current_wall.obj.hide_set(False)
            for child in self.current_wall.obj.children:
                child.hide_set(False)

        # Check for nearby wall endpoints or surfaces (only before first point placed)
        if not self.has_start_point:
            # First check for endpoint snap (higher priority)
            snap_wall, snap_endpoint, snap_location = self.find_nearby_wall_endpoint(context)
            
            if snap_wall:
                # Endpoint snap found
                if snap_wall != self.highlighted_wall:
                    self.clear_wall_highlight()
                    self.highlight_wall(snap_wall, highlight=True)
                    self.highlighted_wall = snap_wall
                
                self.snap_wall = snap_wall
                self.snap_endpoint = snap_endpoint
                self.snap_surface = None
                self.snap_location = snap_location
                self.hit_location = snap_location
            else:
                # No endpoint - check for wall surface snap
                surface_wall, surface_location, surface_face = self.find_wall_surface_snap(context)
                
                if surface_wall:
                    # Surface snap found
                    if surface_wall != self.highlighted_wall:
                        self.clear_wall_highlight()
                        self.highlight_wall(surface_wall, highlight=True)
                        self.highlighted_wall = surface_wall
                    
                    self.snap_wall = surface_wall
                    self.snap_endpoint = None
                    self.snap_surface = surface_face
                    self.snap_location = surface_location
                    self.hit_location = surface_location
                else:
                    # No snap - clear any highlighting and stale snap state
                    if self.highlighted_wall:
                        self.clear_wall_highlight()
                    self.snap_wall = None
                    self.snap_endpoint = None
                    self.snap_surface = None
                    self.snap_location = None

        # Track shift state for fine snap
        self.fine_snap = event.shift

        # Update wall tracking hover/dwell detection
        self.update_track_hover(context)

        # Update position if not typing
        if self.placement_state != hb_placement.PlacementState.TYPING:
            self.set_wall_position_from_mouse()

        self.update_header(context)

        # Left click - place point
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if not self.has_start_point:
                # Check if we're snapping to an existing wall endpoint
                if self.snap_wall and self.snap_endpoint:
                    self.connect_to_existing_wall(self.snap_wall, self.snap_endpoint)
                    self.clear_wall_highlight()
                    self._show_wall_objects()
                elif self.snap_wall and self.snap_surface:
                    # Snapping to wall surface - use exact snap location
                    snap_loc = Vector(self.snap_location)
                    self.start_point = snap_loc
                    self.current_wall.obj.location = snap_loc  # Ensure position matches
                    self.has_start_point = True
                    self.clear_wall_highlight()
                    self._show_wall_objects()
                else:
                    # Set first point normally (snapped to grid)
                    self.start_point = hb_snap.snap_vector_to_grid(Vector(self.hit_location), fine=self.fine_snap)
                    self.has_start_point = True
                    self._show_wall_objects()
            else:
                # If close-snap is active, close the room instead of confirming
                if self.close_snap_active and self.confirmed_wall_count >= 2 and self.first_wall is not None:
                    self.close_room(context)
                    self.clear_wall_highlight()
                    self._remove_snap_indicator()
                    self._remove_dim_handler()
                    self._remove_track_timer(context)
                    hb_placement.clear_header_text(context)
                    return {'FINISHED'}
                # Confirm wall and start next
                self.confirm_current_wall()
            return {'RUNNING_MODAL'}

        # Right click - finish drawing
        if event.type == 'RIGHTMOUSE' and event.value == 'PRESS':
            # Clear any wall highlight
            self.clear_wall_highlight()
            self._remove_snap_indicator()
            self._remove_dim_handler()
            self._remove_track_timer(context)
            # Remove current unfinished wall
            self.cancel_placement(context)
            hb_placement.clear_header_text(context)
            return {'FINISHED'}

        # Escape - cancel everything
        if event.type == 'ESC' and event.value == 'PRESS':
            # Clear any wall highlight
            self.clear_wall_highlight()
            self._remove_snap_indicator()
            self._remove_dim_handler()
            self._remove_track_timer(context)
            self.cancel_placement(context)
            hb_placement.clear_header_text(context)
            return {'CANCELLED'}

        # C key - close room (requires 2+ confirmed walls)
        if event.type == 'C' and event.value == 'PRESS' and self.has_start_point:
            if self.confirmed_wall_count >= 2 and self.first_wall is not None:
                self.close_room(context)
                self.clear_wall_highlight()
                self._remove_snap_indicator()
                self._remove_dim_handler()
                self._remove_track_timer(context)
                hb_placement.clear_header_text(context)
                return {'FINISHED'}
            return {'RUNNING_MODAL'}

        # T key - acquire/remove track point at cursor
        if event.type == 'T' and event.value == 'PRESS':
            if self.placement_state != hb_placement.PlacementState.TYPING:
                self.acquire_or_remove_track_point_at_cursor(context)
                return {'RUNNING_MODAL'}

        # Alt key toggles free rotation mode
        if event.type == 'LEFT_ALT' and event.value == 'PRESS':
            self.free_rotation = not self.free_rotation
            self.update_header(context)
            return {'RUNNING_MODAL'}

        # Pass through navigation events
        if hb_snap.event_is_pass_through(event):
            return {'PASS_THROUGH'}

        return {'RUNNING_MODAL'}


class home_builder_walls_OT_wall_prompts(bpy.types.Operator):
    bl_idname = "home_builder_walls.wall_prompts"
    bl_label = "Wall Prompts"
    bl_description = "This shows the prompts for the selected wall"

    wall: hb_types.GeoNodeWall = None
    previous_rotation: float = 0.0

    wall_length: bpy.props.FloatProperty(name="Width",unit='LENGTH',precision=6)# type: ignore
    wall_height: bpy.props.FloatProperty(name="Height",unit='LENGTH',precision=6)# type: ignore
    wall_thickness: bpy.props.FloatProperty(name="Depth",unit='LENGTH',precision=6)# type: ignore

    @classmethod
    def poll(cls, context):
        return context.object and 'IS_WALL_BP' in context.object

    def check(self, context):
        self.wall.set_input('Length', self.wall_length)
        self.wall.set_input('Height', self.wall_height)
        self.wall.set_input('Thickness', self.wall_thickness)
        calculate_wall_miter_angles(self.wall.obj)
        left_wall = self.wall.get_connected_wall('left')
        if left_wall:
            calculate_wall_miter_angles(left_wall.obj)
        
        right_wall = self.wall.get_connected_wall('right')
        if right_wall:
            calculate_wall_miter_angles(right_wall.obj)        
        return True

    def invoke(self, context, event):
        self.wall = hb_types.GeoNodeWall(context.object)
        self.wall_length = self.wall.get_input('Length')
        self.wall_height = self.wall.get_input('Height')
        self.wall_thickness = self.wall.get_input('Thickness')
        self.previous_rotation = self.wall.obj.rotation_euler.z
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def execute(self, context):
        return {'FINISHED'}

    def get_first_wall_bp(self,context,obj):
        if len(obj.constraints) > 0:
            bp = obj.constraints[0].target.parent
            return self.get_first_wall_bp(context,bp)
        else:
            return obj   

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        row = box.row()
        
        col = row.column(align=True)
        row1 = col.row(align=True)
        row1.label(text='Length:')
        row1.prop(self, 'wall_length', text="")
        
        row1 = col.row(align=True)
        row1.label(text='Height:')
        row1.prop(self, 'wall_height', text="")      

        row1 = col.row(align=True)
        row1.label(text='Thickness:')
        row1.prop(self, 'wall_thickness', text="") 

        if len(self.wall.obj.constraints) > 0:
            first_wall = self.get_first_wall_bp(context,self.wall.obj)
            col = row.column(align=True)
            col.label(text="Location X:")
            col.label(text="Location Y:")
            col.label(text="Location Z:")
        
            col = row.column(align=True)
            col.prop(first_wall,'location',text="")            
        else:
            col = row.column(align=True)
            col.label(text="Location X:")
            col.label(text="Location Y:")
            col.label(text="Location Z:")
        
            col = row.column(align=True)
            col.prop(self.wall.obj,'location',text="")
        
        row = box.row()
        row.label(text='Rotation Z:')
        row.prop(self.wall.obj,'rotation_euler',index=2,text="")  


class home_builder_walls_OT_add_floor(bpy.types.Operator):
    bl_idname = "home_builder_walls.add_floor"
    bl_label = "Add Floor"
    bl_description = "This will add a floor to the room based on the wall layout"
    bl_options = {'UNDO'}

    def create_floor_mesh(self,name, points):
        """Create a floor mesh from boundary points with thickness for boolean support."""
        
        mesh = bpy.data.meshes.new(name)
        obj = bpy.data.objects.new(name, mesh)
        
        bpy.context.collection.objects.link(obj)
        
        bm = bmesh.new()
        
        # If closed loop, remove duplicate closing point
        closed = is_closed_loop(points)
        if closed:
            points = points[:-1]
        
        # Add vertices at Z=0 (top surface)
        verts = [bm.verts.new(p) for p in points]
        bm.verts.ensure_lookup_table()
        
        # Create boundary edges
        edges = []
        for i in range(len(verts)):
            next_i = (i + 1) % len(verts)
            edge = bm.edges.new((verts[i], verts[next_i]))
            edges.append(edge)
        
        # Fill to create faces (handles non-convex shapes)
        bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=edges)
        
        # Ensure all normals point upward (+Z) for consistent floor orientation
        bm.normal_update()
        for face in bm.faces:
            if face.normal.z < 0:
                face.normal_flip()
        
        # Extrude downward to give the floor thickness (needed for boolean cuts)
        floor_thickness = 0.01  # 10mm / ~3/8"
        top_faces = list(bm.faces)
        extrude_result = bmesh.ops.extrude_face_region(bm, geom=top_faces)
        extruded_verts = [g for g in extrude_result['geom'] if isinstance(g, bmesh.types.BMVert)]
        bmesh.ops.translate(bm, verts=extruded_verts, vec=Vector((0, 0, -floor_thickness)))
        
        # Recalculate normals outward on the solid
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        bm.normal_update()

        # UV unwrap - planar projection from top down (X,Y -> U,V)
        uv_layer = bm.loops.layers.uv.new("UVMap")
        for face in bm.faces:
            for loop in face.loops:
                loop[uv_layer].uv = (loop.vert.co.x, loop.vert.co.y)
        
        bm.to_mesh(mesh)
        bm.free()
        
        return obj      

    def execute(self, context):
        chains = find_wall_chains()
        
        if not chains:
            self.report({'WARNING'}, "No connected walls found")
            return {'CANCELLED'}
        
        # Separate closed loops from open chains
        closed_chains = []
        open_chains = []
        for chain in chains:
            points = get_room_boundary_points(chain)
            if len(points) >= 3 and is_closed_loop(points):
                closed_chains.append((chain, points))
            else:
                open_chains.append(chain)
        
        floors_created = 0
        
        if closed_chains:
            # Closed loops exist — use only those (open chains are interior walls)
            for chain, points in closed_chains:
                name = "Floor" if floors_created == 0 else f"Floor.{floors_created:03d}"
                floor_obj = self.create_floor_mesh(name, points)
                floor_obj['IS_FLOOR_BP'] = True
                floors_created += 1
        else:
            # No closed loops — create bounding box floors from open chains
            for chain in open_chains:
                all_points = []
                for wall in chain:
                    start, end = get_wall_endpoints(wall)
                    all_points.append(Vector((start.x, start.y, 0)))
                    all_points.append(Vector((end.x, end.y, 0)))
                
                if len(all_points) < 2:
                    continue
                
                min_x = min(p.x for p in all_points)
                max_x = max(p.x for p in all_points)
                min_y = min(p.y for p in all_points)
                max_y = max(p.y for p in all_points)
                
                # Ensure valid rectangle (not a line)
                if abs(max_x - min_x) < 0.01:
                    max_x = min_x + 3.0
                if abs(max_y - min_y) < 0.01:
                    max_y = min_y + 3.0
                
                points = [
                    Vector((min_x, min_y, 0)),
                    Vector((max_x, min_y, 0)),
                    Vector((max_x, max_y, 0)),
                    Vector((min_x, max_y, 0)),
                    Vector((min_x, min_y, 0)),
                ]
                
                name = "Floor" if floors_created == 0 else f"Floor.{floors_created:03d}"
                floor_obj = self.create_floor_mesh(name, points)
                floor_obj['IS_FLOOR_BP'] = True
                floors_created += 1
        
        if floors_created > 0:
            self.report({'INFO'}, f"Created {floors_created} floor(s)")
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Could not create floor - insufficient wall data")
            return {'CANCELLED'}



class home_builder_walls_OT_add_ceiling(bpy.types.Operator):
    bl_idname = "home_builder_walls.add_ceiling"
    bl_label = "Add Ceiling"
    bl_description = "This will add a ceiling to the room based on the wall layout"
    bl_options = {'UNDO'}

    def create_ceiling_mesh(self, name, points, height):
        """Create a ceiling mesh from boundary points at the given height."""
        mesh = bpy.data.meshes.new(name)
        obj = bpy.data.objects.new(name, mesh)

        bpy.context.collection.objects.link(obj)

        bm = bmesh.new()

        # If closed loop, remove duplicate closing point
        closed = is_closed_loop(points)
        if closed:
            points = points[:-1]

        # Add vertices at ceiling height
        verts = [bm.verts.new(Vector((p.x, p.y, height))) for p in points]
        bm.verts.ensure_lookup_table()

        # Create boundary edges
        edges = []
        for i in range(len(verts)):
            next_i = (i + 1) % len(verts)
            edge = bm.edges.new((verts[i], verts[next_i]))
            edges.append(edge)

        # Fill to create faces
        bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=edges)

        # Flip normals so they face downward (into the room)
        bmesh.ops.reverse_faces(bm, faces=bm.faces[:])

        # UV unwrap - planar projection from top down (X,Y -> U,V)
        uv_layer = bm.loops.layers.uv.new("UVMap")
        for face in bm.faces:
            for loop in face.loops:
                loop[uv_layer].uv = (loop.vert.co.x, loop.vert.co.y)

        bm.to_mesh(mesh)
        bm.free()

        return obj

    def execute(self, context):
        props = context.scene.home_builder
        ceiling_height = props.ceiling_height

        chains = find_wall_chains()

        if not chains:
            self.report({'WARNING'}, "No connected walls found")
            return {'CANCELLED'}

        # Separate closed loops from open chains
        closed_chains = []
        open_chains = []
        for chain in chains:
            points = get_room_boundary_points(chain)
            if len(points) >= 3 and is_closed_loop(points):
                closed_chains.append((chain, points))
            else:
                open_chains.append(chain)
        
        ceilings_created = 0
        
        if closed_chains:
            for chain, points in closed_chains:
                wall = hb_types.GeoNodeWall(chain[0])
                chain_height = wall.get_input('Height')
                if chain_height is None or chain_height == 0:
                    chain_height = ceiling_height

                name = "Ceiling" if ceilings_created == 0 else f"Ceiling.{ceilings_created:03d}"
                ceiling_obj = self.create_ceiling_mesh(name, points, chain_height)
                ceiling_obj['IS_CEILING_BP'] = True
                ceilings_created += 1
        else:
            for chain in open_chains:
                all_points = []
                for w in chain:
                    start, end = get_wall_endpoints(w)
                    all_points.append(Vector((start.x, start.y, 0)))
                    all_points.append(Vector((end.x, end.y, 0)))
                
                if len(all_points) < 2:
                    continue
                
                min_x = min(p.x for p in all_points)
                max_x = max(p.x for p in all_points)
                min_y = min(p.y for p in all_points)
                max_y = max(p.y for p in all_points)
                
                if abs(max_x - min_x) < 0.01:
                    max_x = min_x + 3.0
                if abs(max_y - min_y) < 0.01:
                    max_y = min_y + 3.0
                
                points = [
                    Vector((min_x, min_y, 0)),
                    Vector((max_x, min_y, 0)),
                    Vector((max_x, max_y, 0)),
                    Vector((min_x, max_y, 0)),
                    Vector((min_x, min_y, 0)),
                ]

                wall = hb_types.GeoNodeWall(chain[0])
                chain_height = wall.get_input('Height')
                if chain_height is None or chain_height == 0:
                    chain_height = ceiling_height

                name = "Ceiling" if ceilings_created == 0 else f"Ceiling.{ceilings_created:03d}"
                ceiling_obj = self.create_ceiling_mesh(name, points, chain_height)
                ceiling_obj['IS_CEILING_BP'] = True
                ceilings_created += 1

        if ceilings_created > 0:
            self.report({'INFO'}, f"Created {ceilings_created} ceiling(s)")
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Could not create ceiling - insufficient wall data")
            return {'CANCELLED'}


class home_builder_walls_OT_add_room_lights(bpy.types.Operator):
    bl_idname = "home_builder_walls.add_room_lights"
    bl_label = "Add Room Lights"
    bl_description = "Add ceiling lights to the room based on room size"
    bl_options = {'UNDO'}

    light_spacing: bpy.props.FloatProperty(
        name="Light Spacing",
        description="Minimum spacing between lights",
        default=1.2192,  # 4 feet in meters
        min=0.3,
        max=3.0,
        unit='LENGTH'
    )  # type: ignore

    edge_offset: bpy.props.FloatProperty(
        name="Edge Offset",
        description="Distance from walls to lights",
        default=0.6096,  # 2 feet in meters
        min=0.15,
        max=1.5,
        unit='LENGTH'
    )  # type: ignore

    light_power: bpy.props.FloatProperty(
        name="Light Power",
        description="Power of each light in watts",
        default=200.0,
        min=10.0,
        max=2000.0,
        unit='POWER'
    )  # type: ignore

    light_temperature: bpy.props.FloatProperty(
        name="Color Temperature",
        description="Light color temperature in Kelvin",
        default=3000.0,
        min=2000.0,
        max=6500.0
    )  # type: ignore

    ceiling_offset: bpy.props.FloatProperty(
        name="Ceiling Offset", 
        description="Distance below ceiling to place lights",
        default=0.0254,  # 1 inch
        min=0.0,
        max=0.3,
        unit='LENGTH'
    )  # type: ignore

    def calculate_light_grid(self,boundary_points, min_spacing=1.2, edge_offset=0.6):
        """
        Calculate optimal light positions for a room.
        
        Args:
            boundary_points: List of 2D vectors defining room boundary
            min_spacing: Minimum spacing between lights in meters
            edge_offset: Distance from walls in meters
        
        Returns:
            List of 2D Vector positions for lights
        """

        xs = [p.x for p in boundary_points]
        ys = [p.y for p in boundary_points]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        width = max_x - min_x
        depth = max_y - min_y
        
        usable_width = width - (2 * edge_offset)
        usable_depth = depth - (2 * edge_offset)
        
        # Ensure at least 1 light
        num_x = max(1, int(usable_width / min_spacing) + 1)
        num_y = max(1, int(usable_depth / min_spacing) + 1)
        
        spacing_x = usable_width / max(1, num_x - 1) if num_x > 1 else 0
        spacing_y = usable_depth / max(1, num_y - 1) if num_y > 1 else 0
        
        positions = []
        start_x = min_x + edge_offset
        start_y = min_y + edge_offset
        
        for i in range(num_x):
            for j in range(num_y):
                if num_x == 1:
                    x = (min_x + max_x) / 2
                else:
                    x = start_x + i * spacing_x
                
                if num_y == 1:
                    y = (min_y + max_y) / 2
                else:
                    y = start_y + j * spacing_y
                
                pos = Vector((x, y))
                if point_in_polygon(pos, boundary_points):
                    positions.append(pos)
        
        return positions

    def kelvin_to_rgb(self,temperature):
        """Convert color temperature in Kelvin to RGB values."""
        # Attempt approximation of blackbody radiation curve
        temp = temperature / 100.0
        
        # Red
        if temp <= 66:
            red = 255
        else:
            red = temp - 60
            red = 329.698727446 * (red ** -0.1332047592)
            red = max(0, min(255, red))
        
        # Green
        if temp <= 66:
            green = temp
            green = 99.4708025861 * math.log(green) - 161.1195681661
        else:
            green = temp - 60
            green = 288.1221695283 * (green ** -0.0755148492)
        green = max(0, min(255, green))
        
        # Blue
        if temp >= 66:
            blue = 255
        elif temp <= 19:
            blue = 0
        else:
            blue = temp - 10
            blue = 138.5177312231 * math.log(blue) - 305.0447927307
            blue = max(0, min(255, blue))
        
        return (red / 255.0, green / 255.0, blue / 255.0)


    def create_room_lights(self,light_positions, height, light_power=200, light_temperature=3000):
        """
        Create point lights at the specified positions.
        
        Args:
            light_positions: List of 2D Vector positions
            height: Z height for lights
            light_power: Power in watts
            light_temperature: Color temperature in Kelvin
        
        Returns:
            List of created light objects
        """

        lights = []
        
        # Create or get scene-specific collection for lights
        scene = bpy.context.scene
        light_collection_name = f"{scene.name} - Lights"
        if light_collection_name not in bpy.data.collections:
            light_collection = bpy.data.collections.new(light_collection_name)
            scene.collection.children.link(light_collection)
        else:
            light_collection = bpy.data.collections[light_collection_name]
            # Ensure it's linked to the current scene
            if light_collection.name not in scene.collection.children:
                scene.collection.children.link(light_collection)
        
        # Get color from temperature
        color = self.kelvin_to_rgb(light_temperature)
        
        for i, pos in enumerate(light_positions):
            # Create light data
            light_data = bpy.data.lights.new(name=f"Room_Light_{i:03d}", type='POINT')
            light_data.energy = light_power
            light_data.shadow_soft_size = 0.1  # Soft shadows
            light_data.color = color
            
            # Create light object
            light_obj = bpy.data.objects.new(name=f"Room_Light_{i:03d}", object_data=light_data)
            light_obj.location = (pos.x, pos.y, height)
            
            # Link to collection
            light_collection.objects.link(light_obj)
            
            # Mark as room light
            light_obj['IS_ROOM_LIGHT'] = True
            
            lights.append(light_obj)
        
        return lights

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=350)

    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        box.label(text="Light Placement", icon='LIGHT')
        col = box.column(align=True)
        col.prop(self, 'light_spacing')
        col.prop(self, 'edge_offset')
        
        box = layout.box()
        box.label(text="Light Properties", icon='OUTLINER_OB_LIGHT')
        col = box.column(align=True)
        col.prop(self, 'light_power')
        col.prop(self, 'light_temperature')
        col.prop(self, 'ceiling_offset')

    def execute(self, context):
        chains = find_wall_chains()
        
        if not chains:
            self.report({'WARNING'}, "No connected walls found")
            return {'CANCELLED'}
        
        # Separate closed loops from open chains
        closed_chains = []
        open_chains = []
        for chain in chains:
            points = get_room_boundary_points(chain)
            if len(points) >= 3 and is_closed_loop(points):
                closed_chains.append((chain, points))
            else:
                open_chains.append(chain)
        
        # Use closed loops if available, otherwise fall back to bounding boxes
        use_chains = []
        if closed_chains:
            use_chains = [(chain, points) for chain, points in closed_chains]
        else:
            for chain in open_chains:
                all_points = []
                for w in chain:
                    start, end = get_wall_endpoints(w)
                    all_points.append(Vector((start.x, start.y, 0)))
                    all_points.append(Vector((end.x, end.y, 0)))
                if len(all_points) < 2:
                    continue
                min_x = min(p.x for p in all_points)
                max_x = max(p.x for p in all_points)
                min_y = min(p.y for p in all_points)
                max_y = max(p.y for p in all_points)
                if abs(max_x - min_x) < 0.01:
                    max_x = min_x + 3.0
                if abs(max_y - min_y) < 0.01:
                    max_y = min_y + 3.0
                points = [
                    Vector((min_x, min_y, 0)),
                    Vector((max_x, min_y, 0)),
                    Vector((max_x, max_y, 0)),
                    Vector((min_x, max_y, 0)),
                    Vector((min_x, min_y, 0)),
                ]
                use_chains.append((chain, points))
        
        total_lights = 0
        
        for chain, points in use_chains:
            
            # Get ceiling height from first wall in chain
            wall = hb_types.GeoNodeWall(chain[0])
            ceiling_height = wall.get_input('Height')
            
            # Calculate light positions
            light_positions = self.calculate_light_grid(
                points, 
                min_spacing=self.light_spacing, 
                edge_offset=self.edge_offset
            )
            
            if not light_positions:
                continue
            
            # Create lights
            lights = self.create_room_lights(
                light_positions,
                height=ceiling_height - self.ceiling_offset,
                light_power=self.light_power,
                light_temperature=self.light_temperature
            )
            
            total_lights += len(lights)
        
        if total_lights > 0:
            self.report({'INFO'}, f"Created {total_lights} light(s)")
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "No closed wall loops found for light placement")
            return {'CANCELLED'}



class home_builder_walls_OT_delete_room_lights(bpy.types.Operator):
    bl_idname = "home_builder_walls.delete_room_lights"
    bl_label = "Delete All Room Lights"
    bl_description = "Remove all room lights from the scene"
    bl_options = {'UNDO'}

    def execute(self, context):
        light_objects = [obj for obj in context.scene.objects if obj.get('IS_ROOM_LIGHT')]

        if not light_objects:
            self.report({'WARNING'}, "No room lights found")
            return {'CANCELLED'}

        count = len(light_objects)
        for obj in light_objects:
            light_data = obj.data
            bpy.data.objects.remove(obj, do_unlink=True)
            if light_data and light_data.users == 0:
                bpy.data.lights.remove(light_data)

        # Remove empty lights collection (check both old and new naming)
        scene = context.scene
        for col_name in [f"{scene.name} - Lights", "Room Lights"]:
            if col_name in bpy.data.collections:
                col = bpy.data.collections[col_name]
                if len(col.objects) == 0:
                    if col.name in scene.collection.children:
                        scene.collection.children.unlink(col)
                    bpy.data.collections.remove(col)

        self.report({'INFO'}, f"Deleted {count} room light(s)")
        return {'FINISHED'}


class home_builder_walls_OT_update_room_lights(bpy.types.Operator):
    bl_idname = "home_builder_walls.update_room_lights"
    bl_label = "Update Room Lights"
    bl_description = "Update properties of all room lights"
    bl_options = {'UNDO'}

    light_power: bpy.props.FloatProperty(
        name="Light Power",
        description="Power of each light in watts",
        default=200.0,
        min=10.0,
        max=2000.0,
        unit='POWER'
    )  # type: ignore

    light_temperature: bpy.props.FloatProperty(
        name="Color Temperature",
        description="Light color temperature in Kelvin",
        default=3000.0,
        min=2000.0,
        max=6500.0
    )  # type: ignore

    light_radius: bpy.props.FloatProperty(
        name="Shadow Softness",
        description="Light source radius for shadow softness",
        default=0.1,
        min=0.0,
        max=1.0,
        unit='LENGTH'
    )  # type: ignore

    def kelvin_to_rgb(self, temperature):
        temp = temperature / 100.0
        if temp <= 66:
            red = 255
        else:
            red = temp - 60
            red = 329.698727446 * (red ** -0.1332047592)
            red = max(0, min(255, red))
        if temp <= 66:
            green = temp
            green = 99.4708025861 * math.log(green) - 161.1195681661
        else:
            green = temp - 60
            green = 288.1221695283 * (green ** -0.0755148492)
        green = max(0, min(255, green))
        if temp >= 66:
            blue = 255
        elif temp <= 19:
            blue = 0
        else:
            blue = temp - 10
            blue = 138.5177312231 * math.log(blue) - 305.0447927307
            blue = max(0, min(255, blue))
        return (red / 255.0, green / 255.0, blue / 255.0)

    def invoke(self, context, event):
        # Initialize from existing lights
        light_objects = [obj for obj in context.scene.objects if obj.get('IS_ROOM_LIGHT')]
        if not light_objects:
            self.report({'WARNING'}, "No room lights found")
            return {'CANCELLED'}

        # Read current values from first light
        first_light = light_objects[0].data
        self.light_power = first_light.energy
        self.light_radius = first_light.shadow_soft_size

        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=350)

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="Light Properties", icon='OUTLINER_OB_LIGHT')
        col = box.column(align=True)
        col.prop(self, 'light_power')
        col.prop(self, 'light_temperature')
        col.prop(self, 'light_radius')

    def execute(self, context):
        light_objects = [obj for obj in context.scene.objects if obj.get('IS_ROOM_LIGHT')]

        if not light_objects:
            self.report({'WARNING'}, "No room lights found")
            return {'CANCELLED'}

        color = self.kelvin_to_rgb(self.light_temperature)

        for obj in light_objects:
            obj.data.energy = self.light_power
            obj.data.color = color
            obj.data.shadow_soft_size = self.light_radius

        self.report({'INFO'}, f"Updated {len(light_objects)} room light(s)")
        return {'FINISHED'}


class home_builder_walls_OT_update_wall_height(bpy.types.Operator):
    bl_idname = "home_builder_walls.update_wall_height"
    bl_label = "Update Wall Height"
    bl_description = "Update wall heights for walls matching the current wall type"

    def execute(self, context):
        props = context.scene.home_builder
        wall_type = props.wall_type
        count = 0

        for obj in context.scene.objects:
            if 'IS_WALL_BP' not in obj:
                continue

            # Match walls by their stored type (fall back to Exterior for untagged walls)
            obj_type = obj.get('WALL_TYPE', 'Exterior')
            if obj_type != wall_type:
                continue

            wall = hb_types.GeoNodeWall(obj)
            if not wall.has_modifier():
                continue
            if wall_type in {'Exterior', 'Interior'}:
                wall.set_input('Height', props.ceiling_height)
            elif wall_type == 'Half':
                wall.set_input('Height', props.half_wall_height)
            elif wall_type == 'Fake':
                wall.set_input('Height', props.fake_wall_height)
            count += 1

        self.report({'INFO'}, f"Updated height on {count} {wall_type} wall(s)")
        return {'FINISHED'}


class home_builder_walls_OT_update_wall_thickness(bpy.types.Operator):
    bl_idname = "home_builder_walls.update_wall_thickness"
    bl_label = "Update Wall Thickness"
    bl_description = "Update wall thickness for walls matching the current wall type"

    def execute(self, context):
        props = context.scene.home_builder
        wall_type = props.wall_type
        count = 0

        for obj in context.scene.objects:
            if 'IS_WALL_BP' not in obj:
                continue

            obj_type = obj.get('WALL_TYPE', 'Exterior')
            if obj_type != wall_type:
                continue

            wall = hb_types.GeoNodeWall(obj)
            if not wall.has_modifier():
                continue
            if wall_type == 'Exterior':
                wall.set_input('Thickness', props.exterior_wall_thickness)
            elif wall_type in {'Interior', 'Half'}:
                wall.set_input('Thickness', props.interior_wall_thickness)
            elif wall_type == 'Fake':
                wall.set_input('Thickness', units.inch(0.75))
            count += 1

        self.report({'INFO'}, f"Updated thickness on {count} {wall_type} wall(s)")
        return {'FINISHED'}



class home_builder_walls_OT_update_wall_miters(bpy.types.Operator):
    """Update miter angles for all walls based on their connections"""
    bl_idname = "home_builder_walls.update_wall_miters"
    bl_label = "Update Wall Miters"
    bl_options = {'UNDO'}

    def execute(self, context):
        update_all_wall_miters()
        self.report({'INFO'}, "Updated wall miter angles")
        return {'FINISHED'}




class home_builder_walls_OT_setup_world_lighting(bpy.types.Operator):
    bl_idname = "home_builder_walls.setup_world_lighting"
    bl_label = "Setup World Lighting"
    bl_description = "Setup world environment lighting using HDRI or Sky texture"
    bl_options = {'REGISTER', 'UNDO'}
    
    lighting_type: bpy.props.EnumProperty(
        name="Lighting Type",
        items=[
            ('HDRI', 'HDRI Environment', 'Use an HDRI image for environment lighting'),
            ('SKY', 'Sky Texture', 'Use a procedural sky texture'),
        ],
        default='HDRI'
    )  # type: ignore
    
    hdri_choice: bpy.props.EnumProperty(
        name="HDRI",
        items=[
            ('studio.exr', 'Studio', 'Clean studio lighting'),
            ('interior.exr', 'Interior', 'Interior room lighting'),
            ('courtyard.exr', 'Courtyard', 'Outdoor courtyard'),
            ('forest.exr', 'Forest', 'Forest environment'),
            ('city.exr', 'City', 'Urban environment'),
            ('sunrise.exr', 'Sunrise', 'Warm sunrise lighting'),
            ('sunset.exr', 'Sunset', 'Golden sunset lighting'),
            ('night.exr', 'Night', 'Night time lighting'),
        ],
        default='studio.exr'
    )  # type: ignore
    
    hdri_strength: bpy.props.FloatProperty(
        name="Strength",
        description="Brightness of the environment",
        default=1.0,
        min=0.0,
        max=10.0
    )  # type: ignore
    
    hdri_rotation: bpy.props.FloatProperty(
        name="Rotation",
        description="Rotate the environment horizontally",
        default=0.0,
        min=0.0,
        max=360.0,
        subtype='ANGLE'
    )  # type: ignore
    
    # Sky texture options
    sky_type: bpy.props.EnumProperty(
        name="Sky Type",
        items=[
            ('PREETHAM', 'Preetham', 'Simple sky model'),
            ('HOSEK_WILKIE', 'Hosek/Wilkie', 'More accurate sky model'),
            ('SINGLE_SCATTERING', 'Single Scattering', 'Realistic atmospheric scattering'),
            ('MULTIPLE_SCATTERING', 'Multiple Scattering', 'Most realistic atmospheric scattering'),
        ],
        default='MULTIPLE_SCATTERING'
    )  # type: ignore
    
    sun_elevation: bpy.props.FloatProperty(
        name="Sun Elevation",
        description="Angle of the sun above the horizon",
        default=0.7854,  # 45 degrees
        min=0.0,
        max=1.5708,  # 90 degrees
        subtype='ANGLE'
    )  # type: ignore
    
    sun_rotation: bpy.props.FloatProperty(
        name="Sun Rotation",
        description="Horizontal rotation of the sun",
        default=0.0,
        min=0.0,
        max=6.2832,  # 360 degrees
        subtype='ANGLE'
    )  # type: ignore
    
    sky_strength: bpy.props.FloatProperty(
        name="Strength",
        description="Brightness of the sky",
        default=1.0,
        min=0.0,
        max=10.0
    )  # type: ignore

    def get_hdri_path(self):
        """Get path to Blender's bundled HDRI files"""
        blender_dir = os.path.dirname(bpy.app.binary_path)
        version = f"{bpy.app.version[0]}.{bpy.app.version[1]}"
        hdri_path = os.path.join(blender_dir, version, "datafiles", "studiolights", "world")
        return hdri_path

    def setup_hdri(self, context):
        """Setup HDRI environment lighting"""
        world = context.scene.world
        if not world:
            world = bpy.data.worlds.new("World")
            context.scene.world = world
        
        world.use_nodes = True
        nodes = world.node_tree.nodes
        links = world.node_tree.links
        
        # Clear existing nodes
        nodes.clear()
        
        # Create nodes
        output = nodes.new(type='ShaderNodeOutputWorld')
        output.location = (400, 0)
        
        background = nodes.new(type='ShaderNodeBackground')
        background.location = (200, 0)
        background.inputs['Strength'].default_value = self.hdri_strength
        
        env_tex = nodes.new(type='ShaderNodeTexEnvironment')
        env_tex.location = (-200, 0)
        
        tex_coord = nodes.new(type='ShaderNodeTexCoord')
        tex_coord.location = (-600, 0)
        
        mapping = nodes.new(type='ShaderNodeMapping')
        mapping.location = (-400, 0)
        mapping.inputs['Rotation'].default_value[2] = self.hdri_rotation
        
        # Load HDRI image
        hdri_path = os.path.join(self.get_hdri_path(), self.hdri_choice)
        if os.path.exists(hdri_path):
            img = bpy.data.images.load(hdri_path, check_existing=True)
            env_tex.image = img
        else:
            self.report({'WARNING'}, f"HDRI file not found: {hdri_path}")
            return False
        
        # Connect nodes
        links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
        links.new(mapping.outputs['Vector'], env_tex.inputs['Vector'])
        links.new(env_tex.outputs['Color'], background.inputs['Color'])
        links.new(background.outputs['Background'], output.inputs['Surface'])
        
        return True

    def setup_sky(self, context):
        """Setup procedural sky texture"""
        world = context.scene.world
        if not world:
            world = bpy.data.worlds.new("World")
            context.scene.world = world
        
        world.use_nodes = True
        nodes = world.node_tree.nodes
        links = world.node_tree.links
        
        # Clear existing nodes
        nodes.clear()
        
        # Create nodes
        output = nodes.new(type='ShaderNodeOutputWorld')
        output.location = (400, 0)
        
        background = nodes.new(type='ShaderNodeBackground')
        background.location = (200, 0)
        background.inputs['Strength'].default_value = self.sky_strength
        
        sky_tex = nodes.new(type='ShaderNodeTexSky')
        sky_tex.location = (-100, 0)
        sky_tex.sky_type = self.sky_type
        sky_tex.sun_elevation = self.sun_elevation
        sky_tex.sun_rotation = self.sun_rotation
        
        # Connect nodes
        links.new(sky_tex.outputs['Color'], background.inputs['Color'])
        links.new(background.outputs['Background'], output.inputs['Surface'])
        
        return True

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=350)

    def draw(self, context):
        layout = self.layout
        
        layout.prop(self, "lighting_type", expand=True)
        
        layout.separator()
        
        if self.lighting_type == 'HDRI':
            box = layout.box()
            box.label(text="HDRI Settings", icon='WORLD')
            col = box.column(align=True)
            col.prop(self, "hdri_choice", text="Environment")
            col.prop(self, "hdri_strength")
            col.prop(self, "hdri_rotation")
        else:
            box = layout.box()
            box.label(text="Sky Settings", icon='LIGHT_SUN')
            col = box.column(align=True)
            col.prop(self, "sky_type")
            col.prop(self, "sun_elevation")
            col.prop(self, "sun_rotation")
            col.prop(self, "sky_strength")

    def execute(self, context):
        if self.lighting_type == 'HDRI':
            if self.setup_hdri(context):
                self.report({'INFO'}, f"Setup HDRI environment: {self.hdri_choice}")
            else:
                return {'CANCELLED'}
        else:
            if self.setup_sky(context):
                self.report({'INFO'}, f"Setup {self.sky_type} sky texture")
            else:
                return {'CANCELLED'}
        
        return {'FINISHED'}


class home_builder_walls_OT_apply_wall_material(bpy.types.Operator):
    bl_idname = "home_builder_walls.apply_wall_material"
    bl_label = "Apply Wall Material"
    bl_description = "Apply the wall material to all walls in the scene"
    bl_options = {'UNDO'}

    def execute(self, context):
        props = context.scene.home_builder
        mat = props.wall_material
        if not mat:
            self.report({'WARNING'}, "No wall material selected")
            return {'CANCELLED'}
        
        material_inputs = [
            'Top Surface', 'Bottom Surface',
            'Inside Face', 'Outside Face',
            'Left Edge', 'Right Edge',
        ]
        wall_count = 0
        for obj in context.scene.objects:
            if obj.get('IS_WALL_BP'):
                wall = hb_types.GeoNodeWall(obj)
                for input_name in material_inputs:
                    wall.set_input(input_name, mat)
                wall_count += 1
        
        self.report({'INFO'}, f"Applied material to {wall_count} wall(s)")
        return {'FINISHED'}




class home_builder_walls_OT_delete_wall(bpy.types.Operator):
    """Delete selected walls and properly disconnect from adjacent walls"""
    bl_idname = "home_builder_walls.delete_wall"
    bl_label = "Delete Wall"
    bl_description = "Delete the selected wall(s), removing all children and disconnecting from adjacent walls"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        for obj in context.selected_objects:
            if obj.get('IS_WALL_BP'):
                return True
            if obj.parent and obj.parent.get('IS_WALL_BP'):
                return True
        obj = context.active_object
        if obj and obj.get('IS_WALL_BP'):
            return True
        if obj and obj.parent and obj.parent.get('IS_WALL_BP'):
            return True
        return False

    def get_wall_bp(self, obj):
        """Get the wall base point object."""
        if obj.get('IS_WALL_BP'):
            return obj
        if obj.parent and obj.parent.get('IS_WALL_BP'):
            return obj.parent
        return None

    def collect_selected_wall_bps(self, context):
        """Return a list of unique wall BP objects from the current selection."""
        wall_bps = []
        seen = set()
        sources = list(context.selected_objects)
        if context.active_object and context.active_object not in sources:
            sources.append(context.active_object)
        for obj in sources:
            wall_bp = self.get_wall_bp(obj)
            if wall_bp is not None and wall_bp.name not in seen:
                seen.add(wall_bp.name)
                wall_bps.append(wall_bp)
        return wall_bps

    def _delete_single_wall(self, wall_bp):
        """Delete one wall, disconnect neighbors, and return (left, right)
        adjacent walls (which may have been deleted earlier in the batch)."""
        wall = hb_types.GeoNodeWall(wall_bp)

        # Find connected walls before we start deleting
        left_wall = wall.get_connected_wall('left')
        right_wall = wall.get_connected_wall('right')

        # Handle right wall (next wall constrained to our obj_x)
        if right_wall:
            # Store world location before removing constraint
            right_world_loc = right_wall.obj.matrix_world.translation.copy()

            # Remove the COPY_LOCATION constraint from right wall
            for con in right_wall.obj.constraints:
                if con.type == 'COPY_LOCATION' and con.target == wall.obj_x:
                    right_wall.obj.constraints.remove(con)
                    break

            # Set location to stored world location
            right_wall.obj.location = right_world_loc

        # Handle left wall (our wall is constrained to left wall's obj_x)
        if left_wall:
            # Clear the connected_object reference on the left wall's obj_x
            if left_wall.obj_x:
                left_wall.obj_x.home_builder.connected_object = None

        # Collect all objects to delete (wall bp + all children recursively)
        objects_to_delete = set()
        objects_to_delete.add(wall_bp)
        for child in wall_bp.children_recursive:
            objects_to_delete.add(child)

        # Delete all collected objects
        for obj in objects_to_delete:
            bpy.data.objects.remove(obj, do_unlink=True)

        return left_wall, right_wall

    def execute(self, context):
        wall_bps = self.collect_selected_wall_bps(context)
        if not wall_bps:
            self.report({'WARNING'}, "No wall selected")
            return {'CANCELLED'}

        # Snapshot the names of walls slated for deletion so we can avoid
        # recomputing miters on neighbors that are also being deleted.
        deleting_names = {wbp.name for wbp in wall_bps}
        neighbors_to_remiter = set()

        # Deselect all once before deleting so per-wall ops do not fight selection
        bpy.ops.object.select_all(action='DESELECT')

        deleted_count = 0
        for wall_bp in wall_bps:
            # Wall may have been removed indirectly (shouldn't happen for top-level
            # wall BPs, but be defensive).
            if wall_bp.name not in bpy.data.objects:
                continue
            left_wall, right_wall = self._delete_single_wall(wall_bp)
            deleted_count += 1
            for nb in (left_wall, right_wall):
                if nb is None:
                    continue
                if nb.obj.name in deleting_names:
                    continue
                if nb.obj.name in bpy.data.objects:
                    neighbors_to_remiter.add(nb.obj.name)

        # Update miter angles on surviving neighbors
        for name in neighbors_to_remiter:
            obj = bpy.data.objects.get(name)
            if obj is not None:
                calculate_wall_miter_angles(obj)

        if deleted_count == 1:
            self.report({'INFO'}, "Wall deleted")
        else:
            self.report({'INFO'}, f"{deleted_count} walls deleted")
        return {'FINISHED'}



class home_builder_walls_OT_hide_wall(bpy.types.Operator):
    """Hide the selected wall and all its children"""
    bl_idname = "home_builder_walls.hide_wall"
    bl_label = "Hide Wall"
    bl_description = "Hide the selected wall and all of its children"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj and obj.get('IS_WALL_BP'):
            return True
        if obj and obj.parent and obj.parent.get('IS_WALL_BP'):
            return True
        return False

    def execute(self, context):
        wall_bps = set()
        for obj in context.selected_objects:
            if obj.get('IS_WALL_BP'):
                wall_bps.add(obj)
            elif obj.parent and obj.parent.get('IS_WALL_BP'):
                wall_bps.add(obj.parent)

        for wall_bp in wall_bps:
            wall_bp.hide_set(True)
            wall_bp.hide_viewport = True
            for child in wall_bp.children_recursive:
                child.hide_set(True)
                child.hide_viewport = True

        self.report({'INFO'}, f"{len(wall_bps)} wall(s) hidden")
        return {'FINISHED'}


class home_builder_walls_OT_show_all_walls(bpy.types.Operator):
    """Show all hidden walls in the scene"""
    bl_idname = "home_builder_walls.show_all_walls"
    bl_label = "Show All Walls"
    bl_description = "Unhide all hidden walls and their children"
    bl_options = {'UNDO'}

    def execute(self, context):
        count = 0
        for obj in context.scene.objects:
            if obj.get('IS_WALL_BP') and (obj.hide_get() or obj.hide_viewport):
                obj.hide_set(False)
                obj.hide_viewport = False
                for child in obj.children_recursive:
                    child.hide_set(False)
                    child.hide_viewport = False
                count += 1

        if count > 0:
            self.report({'INFO'}, f"Restored {count} hidden wall(s)")
        else:
            self.report({'INFO'}, "No hidden walls found")
        return {'FINISHED'}



class home_builder_walls_OT_isolate_selected_walls(bpy.types.Operator):
    """Isolate selected walls by hiding all other walls"""
    bl_idname = "home_builder_walls.isolate_selected_walls"
    bl_label = "Isolate Selected Walls"
    bl_description = "Hide all walls except the selected ones"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj and obj.get('IS_WALL_BP'):
            return True
        if obj and obj.parent and obj.parent.get('IS_WALL_BP'):
            return True
        return False

    def execute(self, context):
        selected_wall_bps = set()
        for obj in context.selected_objects:
            if obj.get('IS_WALL_BP'):
                selected_wall_bps.add(obj)
            elif obj.parent and obj.parent.get('IS_WALL_BP'):
                selected_wall_bps.add(obj.parent)

        hidden_count = 0
        for obj in context.scene.objects:
            if obj.get('IS_WALL_BP') and obj not in selected_wall_bps:
                obj.hide_set(True)
                obj.hide_viewport = True
                for child in obj.children_recursive:
                    child.hide_set(True)
                    child.hide_viewport = True
                hidden_count += 1

        self.report({'INFO'}, f"Isolated {len(selected_wall_bps)} wall(s), hid {hidden_count} other(s)")
        return {'FINISHED'}



# =============================================================================
# FLOOR CUTTER
# =============================================================================

def draw_floor_cutter_preview(op, context):
    """GPU draw callback: renders the polygon preview during floor cutter drawing."""
    region = op.region
    if region is None:
        return

    from bpy_extras import view3d_utils

    gpu.state.blend_set('ALPHA')
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    shader.bind()

    confirmed = op.confirmed_points
    cursor_3d = op.cursor_point

    if not confirmed and cursor_3d is None:
        gpu.state.blend_set('NONE')
        return

    # Convert 3D points to 2D screen coords
    pts_2d = []
    for p in confirmed:
        s = view3d_utils.location_3d_to_region_2d(region, region.data, p)
        if s:
            pts_2d.append(s)
        else:
            pts_2d.append(Vector((0, 0)))

    cursor_2d = None
    if cursor_3d is not None:
        cursor_2d = view3d_utils.location_3d_to_region_2d(region, region.data, cursor_3d)

    # --- Draw filled polygon preview (translucent) ---
    if len(pts_2d) >= 3:
        # Simple triangle fan from first vertex
        tri_verts = []
        for i in range(1, len(pts_2d) - 1):
            tri_verts.extend([(pts_2d[0].x, pts_2d[0].y),
                              (pts_2d[i].x, pts_2d[i].y),
                              (pts_2d[i+1].x, pts_2d[i+1].y)])
        if tri_verts:
            shader.uniform_float("color", (1.0, 0.2, 0.2, 0.15))
            batch = batch_for_shader(shader, 'TRIS', {"pos": tri_verts})
            batch.draw(shader)

    # --- Draw confirmed edges (solid red) ---
    gpu.state.line_width_set(2.0)
    if len(pts_2d) >= 2:
        edge_verts = []
        for i in range(len(pts_2d) - 1):
            edge_verts.append((pts_2d[i].x, pts_2d[i].y))
            edge_verts.append((pts_2d[i+1].x, pts_2d[i+1].y))
        shader.uniform_float("color", (1.0, 0.3, 0.3, 0.9))
        batch = batch_for_shader(shader, 'LINES', {"pos": edge_verts})
        batch.draw(shader)

    # --- Draw line from last confirmed point to cursor (dashed feel via color) ---
    if pts_2d and cursor_2d:
        last = pts_2d[-1]
        shader.uniform_float("color", (1.0, 0.5, 0.5, 0.7))
        batch = batch_for_shader(shader, 'LINES', {
            "pos": [(last.x, last.y), (cursor_2d.x, cursor_2d.y)]
        })
        batch.draw(shader)

    # --- Draw closing line from cursor back to first point (if 3+ points) ---
    if len(pts_2d) >= 2 and cursor_2d:
        first = pts_2d[0]
        shader.uniform_float("color", (1.0, 0.5, 0.5, 0.4))
        batch = batch_for_shader(shader, 'LINES', {
            "pos": [(cursor_2d.x, cursor_2d.y), (first.x, first.y)]
        })
        batch.draw(shader)

    # --- Draw vertex dots ---
    gpu.state.point_size_set(8.0)
    if pts_2d:
        dot_verts = [(p.x, p.y) for p in pts_2d]
        shader.uniform_float("color", (1.0, 1.0, 1.0, 1.0))
        batch = batch_for_shader(shader, 'POINTS', {"pos": dot_verts})
        batch.draw(shader)

    # --- First point highlight (green) for close-loop snapping ---
    if len(pts_2d) >= 3 and cursor_2d and op.close_snap:
        first = pts_2d[0]
        _draw_snap_point(first.x, first.y, (0.0, 1.0, 0.4, 0.9), 14, 10)

    # --- Cursor dot ---
    if cursor_2d:
        shader.bind()
        gpu.state.point_size_set(6.0)
        shader.uniform_float("color", (1.0, 1.0, 0.0, 0.9))
        batch = batch_for_shader(shader, 'POINTS', {"pos": [(cursor_2d.x, cursor_2d.y)]})
        batch.draw(shader)

    gpu.state.point_size_set(1.0)
    gpu.state.line_width_set(1.0)
    gpu.state.blend_set('NONE')


class home_builder_walls_OT_draw_floor_cutter(bpy.types.Operator, hb_placement.PlacementMixin):
    bl_idname = "home_builder_walls.draw_floor_cutter"
    bl_label = "Draw Floor Cutter"
    bl_description = "Draw a polygon shape to cut a hole in the floor (stairwells, pass-throughs, etc.)"
    bl_options = {'UNDO'}

    # State
    confirmed_points: list = None   # 3D points already clicked
    cursor_point: Vector = None     # Live 3D cursor position
    floor_obj: bpy.types.Object = None
    close_snap: bool = False        # True when cursor is near first point
    _draw_handle = None

    CLOSE_THRESHOLD = 0.15  # Meters — snap-to-close distance

    @classmethod
    def poll(cls, context):
        # Need at least one floor in scene
        for obj in context.scene.objects:
            if obj.get('IS_FLOOR_BP'):
                return True
        return False

    def find_target_floor(self, context):
        """Find the floor to cut. Prefer selected, else first found."""
        # Check active/selected first
        if context.object and context.object.get('IS_FLOOR_BP'):
            return context.object
        for obj in context.selected_objects:
            if obj.get('IS_FLOOR_BP'):
                return obj
        # Fallback: first floor in scene
        for obj in context.scene.objects:
            if obj.get('IS_FLOOR_BP'):
                return obj
        return None

    def get_floor_plane_point(self, context):
        """Project the current mouse position onto the floor plane (Z=0)."""
        if self.region is None:
            return None
        coord = (self.mouse_pos.x, self.mouse_pos.y)
        rv3d = self.region.data
        origin = view3d_utils.region_2d_to_origin_3d(self.region, rv3d, coord)
        direction = view3d_utils.region_2d_to_vector_3d(self.region, rv3d, coord)
        # Intersect with Z=0 plane
        point = intersect_line_plane(origin, origin + direction, Vector((0, 0, 0)), Vector((0, 0, 1)))
        return point

    def check_close_snap(self):
        """Check if cursor is close enough to first point to close the polygon."""
        if len(self.confirmed_points) < 3 or self.cursor_point is None:
            self.close_snap = False
            return
        first = self.confirmed_points[0]
        dist = (Vector((self.cursor_point.x, self.cursor_point.y, 0))
                - Vector((first.x, first.y, 0))).length
        self.close_snap = dist < self.CLOSE_THRESHOLD

    def create_cutter_mesh(self, context, points):
        """Create a cutter object from confirmed polygon points, extruded on Z."""
        mesh = bpy.data.meshes.new("Floor_Cutter")
        obj = bpy.data.objects.new("Floor_Cutter", mesh)
        context.collection.objects.link(obj)

        bm = bmesh.new()

        # Bottom verts at Z = -0.1
        bottom_verts = []
        for p in points:
            v = bm.verts.new(Vector((p.x, p.y, -0.1)))
            bottom_verts.append(v)
        bm.verts.ensure_lookup_table()

        # Top verts at Z = +0.1
        top_verts = []
        for p in points:
            v = bm.verts.new(Vector((p.x, p.y, 0.1)))
            top_verts.append(v)
        bm.verts.ensure_lookup_table()

        n = len(points)

        # Bottom face (reversed winding for outward normals)
        bm.faces.new(list(reversed(bottom_verts)))

        # Top face
        bm.faces.new(top_verts)

        # Side faces
        for i in range(n):
            ni = (i + 1) % n
            bm.faces.new([bottom_verts[i], bottom_verts[ni],
                          top_verts[ni], top_verts[i]])

        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        bm.normal_update()
        bm.to_mesh(mesh)
        bm.free()

        # Tag the cutter
        obj['IS_CUTTING_OBJ'] = True
        obj['IS_FLOOR_CUTTER'] = True
        obj.display_type = 'WIRE'
        obj.hide_render = True

        return obj

    def add_boolean_to_floor(self, floor_obj, cutter_obj):
        """Add a boolean DIFFERENCE modifier to the floor."""
        mod_name = f"Cut - {cutter_obj.name}"
        mod = floor_obj.modifiers.new(name=mod_name, type='BOOLEAN')
        mod.operation = 'DIFFERENCE'
        mod.object = cutter_obj
        mod.solver = 'EXACT'
        return mod

    def finish(self, context):
        """Close polygon, create cutter, apply boolean, clean up."""
        # Remove draw handler
        if self._draw_handle:
            bpy.types.SpaceView3D.draw_handler_remove(self._draw_handle, 'WINDOW')
            self._draw_handle = None

        hb_placement.clear_header_text(context)
        context.window.cursor_set('DEFAULT')

        if len(self.confirmed_points) < 3:
            self.report({'WARNING'}, "Need at least 3 points to create a cutter")
            return {'CANCELLED'}

        cutter = self.create_cutter_mesh(context, self.confirmed_points)
        self.add_boolean_to_floor(self.floor_obj, cutter)

        # Parent cutter to the floor so they stay linked
        cutter.parent = self.floor_obj

        self.report({'INFO'}, f"Created floor cutter with {len(self.confirmed_points)} points")
        return {'FINISHED'}

    def cancel(self, context):
        """Clean up on cancel."""
        if self._draw_handle:
            bpy.types.SpaceView3D.draw_handler_remove(self._draw_handle, 'WINDOW')
            self._draw_handle = None
        hb_placement.clear_header_text(context)
        context.window.cursor_set('DEFAULT')

    def update_header(self, context):
        n = len(self.confirmed_points)
        parts = []
        if n == 0:
            parts.append("Click to place first point")
        elif n < 3:
            parts.append(f"{n} point(s) — click to add more (need {3 - n} more minimum)")
        else:
            close_text = " [CLOSE SNAP]" if self.close_snap else ""
            parts.append(f"{n} points — click to add, Enter to finish{close_text}")
        parts.append("Backspace: undo point | Esc: cancel")
        hb_placement.draw_header_text(context, " | ".join(parts))

    def execute(self, context):
        self.init_placement(context)

        self.confirmed_points = []
        self.cursor_point = None
        self.close_snap = False

        self.floor_obj = self.find_target_floor(context)
        if not self.floor_obj:
            self.report({'WARNING'}, "No floor found in scene")
            return {'CANCELLED'}

        # Add GPU draw handler
        self._draw_handle = bpy.types.SpaceView3D.draw_handler_add(
            draw_floor_cutter_preview, (self, context), 'WINDOW', 'POST_PIXEL')

        context.window_manager.modal_handler_add(self)
        self.update_header(context)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        context.window.cursor_set('CROSSHAIR')

        if event.type == "INBETWEEN_MOUSEMOVE":
            return {'RUNNING_MODAL'}

        # Navigation pass-through
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}

        # Update snap / cursor position
        self.update_snap(context, event)
        self.cursor_point = self.get_floor_plane_point(context)
        self.check_close_snap()

        # Redraw viewport for GPU overlay
        if context.area:
            context.area.tag_redraw()

        # --- Left click: place a point ---
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if self.cursor_point is None:
                return {'RUNNING_MODAL'}

            # If snapping to close and we have 3+ points, finish
            if self.close_snap and len(self.confirmed_points) >= 3:
                return self.finish(context)

            self.confirmed_points.append(self.cursor_point.copy())
            self.update_header(context)
            return {'RUNNING_MODAL'}

        # --- Enter: finish (if enough points) ---
        if event.type in {'RET', 'NUMPAD_ENTER'} and event.value == 'PRESS':
            if len(self.confirmed_points) >= 3:
                return self.finish(context)
            else:
                self.report({'WARNING'}, f"Need at least 3 points (have {len(self.confirmed_points)})")
                return {'RUNNING_MODAL'}

        # --- Backspace: remove last point ---
        if event.type == 'BACK_SPACE' and event.value == 'PRESS':
            if self.confirmed_points:
                self.confirmed_points.pop()
                self.update_header(context)
            return {'RUNNING_MODAL'}

        # --- Escape / Right-click: cancel ---
        if event.type in {'RIGHTMOUSE', 'ESC'} and event.value == 'PRESS':
            self.cancel(context)
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}




# =============================================================================
# WALL CUTTER
# =============================================================================

def draw_wall_cutter_preview(op, context):
    """GPU draw callback: renders the rectangle preview during wall cutter drawing."""
    region = op.region
    if region is None:
        return

    from bpy_extras import view3d_utils

    gpu.state.blend_set('ALPHA')
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    shader.bind()

    first_3d = op.first_point
    cursor_3d = op.cursor_point

    if first_3d is None:
        # Just draw the cursor dot if we have one
        if cursor_3d is not None:
            cursor_2d = view3d_utils.location_3d_to_region_2d(region, region.data, cursor_3d)
            if cursor_2d:
                gpu.state.point_size_set(8.0)
                shader.uniform_float("color", (1.0, 1.0, 0.0, 0.9))
                batch = batch_for_shader(shader, 'POINTS', {"pos": [(cursor_2d.x, cursor_2d.y)]})
                batch.draw(shader)
                gpu.state.point_size_set(1.0)
        gpu.state.blend_set('NONE')
        return

    if cursor_3d is None:
        gpu.state.blend_set('NONE')
        return

    # We have first_point and cursor — compute the 4 corners of the rectangle
    # in world space on the wall plane
    wall_obj = op.target_wall
    if wall_obj is None:
        gpu.state.blend_set('NONE')
        return

    wall_matrix = wall_obj.matrix_world
    wall_matrix_inv = wall_matrix.inverted()

    # Convert to wall-local space
    local_first = wall_matrix_inv @ first_3d
    local_cursor = wall_matrix_inv @ cursor_3d

    # Rectangle corners in wall-local space (X = along wall, Z = height)
    min_x = min(local_first.x, local_cursor.x)
    max_x = max(local_first.x, local_cursor.x)
    min_z = min(local_first.z, local_cursor.z)
    max_z = max(local_first.z, local_cursor.z)

    # 4 corners on the wall face (Y=0)
    corners_local = [
        Vector((min_x, 0, min_z)),
        Vector((max_x, 0, min_z)),
        Vector((max_x, 0, max_z)),
        Vector((min_x, 0, max_z)),
    ]

    corners_world = [wall_matrix @ c for c in corners_local]
    corners_2d = []
    for c in corners_world:
        s = view3d_utils.location_3d_to_region_2d(region, region.data, c)
        if s:
            corners_2d.append(s)
        else:
            corners_2d.append(Vector((0, 0)))

    if len(corners_2d) < 4:
        gpu.state.blend_set('NONE')
        return

    # Draw filled rectangle (two triangles)
    tri_verts = [
        (corners_2d[0].x, corners_2d[0].y),
        (corners_2d[1].x, corners_2d[1].y),
        (corners_2d[2].x, corners_2d[2].y),
        (corners_2d[0].x, corners_2d[0].y),
        (corners_2d[2].x, corners_2d[2].y),
        (corners_2d[3].x, corners_2d[3].y),
    ]
    shader.uniform_float("color", (1.0, 0.2, 0.2, 0.2))
    batch = batch_for_shader(shader, 'TRIS', {"pos": tri_verts})
    batch.draw(shader)

    # Draw rectangle outline
    gpu.state.line_width_set(2.0)
    edge_verts = []
    for i in range(4):
        ni = (i + 1) % 4
        edge_verts.append((corners_2d[i].x, corners_2d[i].y))
        edge_verts.append((corners_2d[ni].x, corners_2d[ni].y))
    shader.uniform_float("color", (1.0, 0.3, 0.3, 0.9))
    batch = batch_for_shader(shader, 'LINES', {"pos": edge_verts})
    batch.draw(shader)

    # Draw corner dots
    gpu.state.point_size_set(8.0)
    dot_verts = [(c.x, c.y) for c in corners_2d]
    shader.uniform_float("color", (1.0, 1.0, 1.0, 1.0))
    batch = batch_for_shader(shader, 'POINTS', {"pos": dot_verts})
    batch.draw(shader)

    # Draw first point highlight (green)
    first_2d = view3d_utils.location_3d_to_region_2d(region, region.data, first_3d)
    if first_2d:
        gpu.state.point_size_set(10.0)
        shader.uniform_float("color", (0.0, 1.0, 0.4, 0.9))
        batch = batch_for_shader(shader, 'POINTS', {"pos": [(first_2d.x, first_2d.y)]})
        batch.draw(shader)

    gpu.state.point_size_set(1.0)
    gpu.state.line_width_set(1.0)
    gpu.state.blend_set('NONE')


class home_builder_walls_OT_draw_wall_cutter(bpy.types.Operator, hb_placement.PlacementMixin):
    bl_idname = "home_builder_walls.draw_wall_cutter"
    bl_label = "Draw Wall Cutter"
    bl_description = "Click two points on a wall to cut a rectangular hole through it"
    bl_options = {'UNDO'}

    # State
    first_point: Vector = None      # First 3D corner (world space)
    cursor_point: Vector = None     # Live 3D cursor position (world space)
    target_wall: bpy.types.Object = None
    _draw_handle = None

    @classmethod
    def poll(cls, context):
        for obj in context.scene.objects:
            if obj.get('IS_WALL_BP'):
                return True
        return False

    def get_wall_hit(self, context):
        """Raycast from mouse to find a wall and the hit point."""
        if self.region is None:
            return None, None
        coord = (self.mouse_pos.x, self.mouse_pos.y)
        rv3d = self.region.data
        origin = view3d_utils.region_2d_to_origin_3d(self.region, rv3d, coord)
        direction = view3d_utils.region_2d_to_vector_3d(self.region, rv3d, coord)

        # Use scene raycast
        depsgraph = context.evaluated_depsgraph_get()
        result, location, normal, index, obj, matrix = context.scene.ray_cast(
            depsgraph, origin, direction)

        if result and obj:
            # Walk up parent chain to find wall base point
            check_obj = obj
            while check_obj:
                if check_obj.get('IS_WALL_BP'):
                    return check_obj, location
                check_obj = check_obj.parent

        return None, None

    def get_wall_plane_point(self, context, wall_obj):
        """Project mouse onto the wall's front face plane (local Y=0)."""
        if self.region is None:
            return None
        coord = (self.mouse_pos.x, self.mouse_pos.y)
        rv3d = self.region.data
        origin = view3d_utils.region_2d_to_origin_3d(self.region, rv3d, coord)
        direction = view3d_utils.region_2d_to_vector_3d(self.region, rv3d, coord)

        # Wall plane: passes through wall origin, normal is wall's local +Y in world space
        wall_matrix = wall_obj.matrix_world
        plane_point = wall_matrix @ Vector((0, 0, 0))
        plane_normal = (wall_matrix @ Vector((0, 1, 0)) - plane_point).normalized()

        point = intersect_line_plane(origin, origin + direction, plane_point, plane_normal)
        return point

    def create_wall_cutter(self, context, wall_obj, p1, p2):
        """Create a cube cutter from two corner points, extending through the wall."""
        wall = hb_types.GeoNodeWall(wall_obj)
        wall_thickness = wall.get_input('Thickness')
        wall_matrix = wall_obj.matrix_world
        wall_matrix_inv = wall_matrix.inverted()

        # Convert to wall-local coordinates
        local_p1 = wall_matrix_inv @ p1
        local_p2 = wall_matrix_inv @ p2

        # Rectangle bounds on wall face
        min_x = min(local_p1.x, local_p2.x)
        max_x = max(local_p1.x, local_p2.x)
        min_z = min(local_p1.z, local_p2.z)
        max_z = max(local_p1.z, local_p2.z)

        # Extend through wall thickness with margin
        margin = 0.01  # 1cm overshoot
        min_y = -margin
        max_y = wall_thickness + margin

        # Create cube mesh in wall-local space
        mesh = bpy.data.meshes.new("Wall_Cutter")
        obj = bpy.data.objects.new("Wall_Cutter", mesh)
        context.collection.objects.link(obj)

        bm = bmesh.new()

        # 8 cube vertices
        verts = [
            bm.verts.new(Vector((min_x, min_y, min_z))),  # 0: front-bottom-left
            bm.verts.new(Vector((max_x, min_y, min_z))),  # 1: front-bottom-right
            bm.verts.new(Vector((max_x, max_y, min_z))),  # 2: back-bottom-right
            bm.verts.new(Vector((min_x, max_y, min_z))),  # 3: back-bottom-left
            bm.verts.new(Vector((min_x, min_y, max_z))),  # 4: front-top-left
            bm.verts.new(Vector((max_x, min_y, max_z))),  # 5: front-top-right
            bm.verts.new(Vector((max_x, max_y, max_z))),  # 6: back-top-right
            bm.verts.new(Vector((min_x, max_y, max_z))),  # 7: back-top-left
        ]
        bm.verts.ensure_lookup_table()

        # 6 faces
        bm.faces.new([verts[0], verts[3], verts[2], verts[1]])  # bottom
        bm.faces.new([verts[4], verts[5], verts[6], verts[7]])  # top
        bm.faces.new([verts[0], verts[1], verts[5], verts[4]])  # front
        bm.faces.new([verts[2], verts[3], verts[7], verts[6]])  # back
        bm.faces.new([verts[0], verts[4], verts[7], verts[3]])  # left
        bm.faces.new([verts[1], verts[2], verts[6], verts[5]])  # right

        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        bm.normal_update()
        bm.to_mesh(mesh)
        bm.free()

        # Position the cutter in world space: parent to wall so it stays aligned
        obj.parent = wall_obj
        obj.matrix_parent_inverse.identity()

        # Tag the cutter
        obj['IS_CUTTING_OBJ'] = True
        obj['IS_WALL_CUTTER'] = True
        obj.display_type = 'WIRE'
        obj.hide_render = True

        return obj

    def add_boolean_to_wall(self, wall_obj, cutter_obj):
        """Add a boolean DIFFERENCE modifier to the wall's mesh children."""
        wall = hb_types.GeoNodeWall(wall_obj)
        mod_name = f"Cut - {cutter_obj.name}"
        mod = wall_obj.modifiers.new(name=mod_name, type='BOOLEAN')
        mod.operation = 'DIFFERENCE'
        mod.object = cutter_obj
        mod.solver = 'EXACT'
        return mod

    def finish(self, context):
        """Create cutter cube, apply boolean, clean up."""
        if self._draw_handle:
            bpy.types.SpaceView3D.draw_handler_remove(self._draw_handle, 'WINDOW')
            self._draw_handle = None

        hb_placement.clear_header_text(context)
        context.window.cursor_set('DEFAULT')

        if self.first_point is None or self.cursor_point is None:
            self.report({'WARNING'}, "Need two points to create a wall cutter")
            return {'CANCELLED'}

        cutter = self.create_wall_cutter(context, self.target_wall, self.first_point, self.cursor_point)
        self.add_boolean_to_wall(self.target_wall, cutter)

        self.report({'INFO'}, f"Created wall cutter on {self.target_wall.name}")
        return {'FINISHED'}

    def cancel_op(self, context):
        """Clean up on cancel."""
        if self._draw_handle:
            bpy.types.SpaceView3D.draw_handler_remove(self._draw_handle, 'WINDOW')
            self._draw_handle = None
        hb_placement.clear_header_text(context)
        context.window.cursor_set('DEFAULT')

    def update_header(self, context):
        parts = []
        if self.first_point is None:
            parts.append("Click on a wall to place first corner")
        else:
            parts.append(f"Click to place second corner on {self.target_wall.name}")
        parts.append("Esc: cancel")
        hb_placement.draw_header_text(context, " | ".join(parts))

    def execute(self, context):
        self.init_placement(context)

        self.first_point = None
        self.cursor_point = None
        self.target_wall = None

        # Add GPU draw handler
        self._draw_handle = bpy.types.SpaceView3D.draw_handler_add(
            draw_wall_cutter_preview, (self, context), 'WINDOW', 'POST_PIXEL')

        context.window_manager.modal_handler_add(self)
        self.update_header(context)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        context.window.cursor_set('CROSSHAIR')

        if event.type == "INBETWEEN_MOUSEMOVE":
            return {'RUNNING_MODAL'}

        # Navigation pass-through
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}

        # Update snap / cursor position
        self.update_snap(context, event)

        # Update cursor position based on state
        if self.first_point is None:
            # Before first click — raycast to walls
            wall_obj, hit_point = self.get_wall_hit(context)
            if wall_obj and hit_point:
                self.cursor_point = hit_point
                self.target_wall = wall_obj
            else:
                self.cursor_point = None
        else:
            # After first click — project onto the same wall's plane
            point = self.get_wall_plane_point(context, self.target_wall)
            if point:
                self.cursor_point = point

        # Redraw viewport
        if context.area:
            context.area.tag_redraw()

        # --- Left click ---
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if self.first_point is None:
                # First click: need a wall hit
                if self.cursor_point is None or self.target_wall is None:
                    return {'RUNNING_MODAL'}
                self.first_point = self.cursor_point.copy()
                self.update_header(context)
                return {'RUNNING_MODAL'}
            else:
                # Second click: finish
                if self.cursor_point is None:
                    return {'RUNNING_MODAL'}
                return self.finish(context)

        # --- Escape / Right-click: cancel ---
        if event.type in {'RIGHTMOUSE', 'ESC'} and event.value == 'PRESS':
            self.cancel_op(context)
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

classes = (
    home_builder_walls_OT_hide_wall,
    home_builder_walls_OT_show_all_walls,
    home_builder_walls_OT_isolate_selected_walls,
    home_builder_walls_OT_delete_wall,
    home_builder_walls_OT_draw_walls,
    home_builder_walls_OT_wall_prompts,
    home_builder_walls_OT_add_floor,
    home_builder_walls_OT_draw_floor_cutter,
    home_builder_walls_OT_draw_wall_cutter,
    home_builder_walls_OT_add_ceiling,
    home_builder_walls_OT_add_room_lights,
    home_builder_walls_OT_setup_world_lighting,
    home_builder_walls_OT_delete_room_lights,
    home_builder_walls_OT_update_room_lights,
    home_builder_walls_OT_update_wall_height,
    home_builder_walls_OT_update_wall_thickness,
    home_builder_walls_OT_update_wall_miters,
    home_builder_walls_OT_apply_wall_material,
)

register, unregister = bpy.utils.register_classes_factory(classes)