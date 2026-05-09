"""Modal placement operator for face frame cabinets.

Drags a wireframe preview cage around the scene during placement; the
real cabinet is built only on commit, so cancel cleanly removes the
preview without leaving construction debris.

Behaviors:
  * Cursor follows mouse; wall is detected by raycast, with a fallback
    to nearest-wall-by-floor-projection so a missed raycast at a
    grazing angle doesn't unstick from the wall (prevents flicker).
  * Front/back side decision uses hysteresis - a 1" tolerance band
    around the wall centerline before flipping sides. Without this,
    sub-pixel cursor wobble at the wall surface flickers between front
    and back placement.
  * On a wall: cabinet width = available gap (between neighbors and
    wall ends), parented to wall, slid along its X axis. Bay quantity
    auto-fits the gap unless the user has overridden it via arrow keys.
  * Off a wall: cabinet width = scene's default_cabinet_width, bay
    quantity stays at the user's last value.
  * Up/down arrows: manually adjust bay quantity (1-10).
  * Click commits, Esc/right-click cancels.

The cage uses Mirror Y on its GeoNodeCage input. Default cage extends
+Y from origin, but face-frame cabinets extend -Y from origin (origin
at the back face). Mirror Y flips the cage to extend -Y too, so cage
position == cabinet position with no offset gymnastics.

The cage is flagged HB_CURRENT_DRAW_OBJ so hb_snap raycasts skip it
(prevents self-snap).
"""

import bpy
from .... import units
import math
from mathutils import Vector, Matrix
from mathutils.geometry import intersect_line_plane, intersect_point_line
from bpy_extras import view3d_utils

from .. import types_face_frame
from .. import types_face_frame_corner
from .. import bay_presets
from . import ops_cabinet
from .... import hb_placement, hb_types, units


_TARGET_BAY_WIDTH = units.inch(18.0)
_BAY_QTY_MIN = 1
_BAY_QTY_MAX = 10

# Hysteresis band for front/back side detection. Cursor must cross the
# wall centerline by this distance before the side flips. Without it,
# a cursor pressed against the wall surface flickers between sides
# every frame (each tiny mouse jitter changes which side of the wall
# centerline the cursor is on).
_FRONT_BACK_HYSTERESIS = units.inch(1.0)

# Plan-view detection threshold. abs(view_z) > 0.7 means the camera is
# looking mostly down, so we should project the cursor onto the floor
# plane to decide front/back side rather than using raycast hit Y
# directly. (In plan view, the raycast usually hits the wall's top
# face, not its front/back faces.)
_PLAN_VIEW_THRESHOLD = 0.7

# Wall snap distance for the floor-projection fallback. If the cursor
# (projected onto the floor plane) is within this distance of any
# wall's centerline, that wall is selected even if the raycast missed.
_WALL_SNAP_DISTANCE = units.inch(6.0)


def _find_wall_root(obj):
    """Walk obj's parent chain to the nearest object tagged IS_WALL_BP.

    Raycasts often land on a child mesh of the wall (cage geometry,
    decoration parts) rather than the wall root itself, so we walk up.
    """
    current = obj
    while current is not None:
        if 'IS_WALL_BP' in current:
            return current
        current = current.parent
    return None


def _cabinet_type_for_name(cabinet_name):
    """Map a library cabinet name to its cabinet_type code.

    Mirrors types_face_frame.get_cabinet_class's dispatch logic so the
    preview cage's dimensions match what cabinet.create() will build.
    """
    if cabinet_name == 'Panel':
        return 'PANEL'
    if 'Upper' in cabinet_name:
        return 'UPPER'
    if 'Tall' in cabinet_name or 'Refrigerator Cabinet' in cabinet_name:
        return 'TALL'
    return 'BASE'


def _cage_dimensions(scene_props, cabinet_type):
    """Return (depth, height) per the relevant scene defaults. Panel
    uses fixed defaults rather than scene props - it's a fixed library
    size, not a configurable cabinet class.
    """
    if cabinet_type == 'PANEL':
        return (units.inch(0.75), units.inch(30.0))
    if cabinet_type == 'UPPER':
        return (scene_props.upper_cabinet_depth,
                scene_props.upper_cabinet_height)
    if cabinet_type == 'TALL':
        return (scene_props.tall_cabinet_depth,
                scene_props.tall_cabinet_height)
    return (scene_props.base_cabinet_depth,
            scene_props.base_cabinet_height)


def _appliance_dimensions(scene_props, appliance_name):
    """Return (width, height, depth) for an appliance preview cage and
    final placement. Falls back to the appliance class's class-level
    defaults when no scene-prop override exists for that field.

    Range Hood is the special case: its height fills from its mount Z
    up to the scene ceiling so the hood reads as a duct enclosure. If
    the ceiling sits at or below the mount Z (mis-configured scene),
    the class default keeps it visible at a sane size.
    """
    cls = types_face_frame.APPLIANCE_NAME_DISPATCH.get(appliance_name)
    if cls is None:
        return (units.inch(24), units.inch(34), units.inch(24))
    if appliance_name == "Dishwasher":
        return (scene_props.dishwasher_width, cls.height, cls.depth)
    if appliance_name == "Range":
        return (scene_props.range_width, cls.height, cls.depth)
    if appliance_name == "Standalone Refrigerator":
        return (scene_props.refrigerator_cabinet_width,
                scene_props.refrigerator_height, cls.depth)
    if appliance_name == "Range Hood":
        ceiling = bpy.context.scene.home_builder.ceiling_height
        mount_z = _appliance_z_location(scene_props, appliance_name)
        height = max(ceiling - mount_z, cls.height)
        return (cls.width, height, cls.depth)
    return (cls.width, cls.height, cls.depth)


def _appliance_z_location(scene_props, appliance_name):
    """Return the cage Z origin for an appliance.

    Range Hood mounts at the upper-cabinet base height (same Z as wall
    cabinets) so it reads as the bay above the range. Everything else
    sits on the floor (Z=0); the operator's invoke uses cursor Z for
    the floor case so the user can rough in shelf/island placements.
    """
    if appliance_name == "Range Hood":
        return scene_props.default_wall_cabinet_location
    return None  # caller falls back to cursor / hit Z


def _find_center_snap(hit_object, wall, kinds, cab_z_range):
    """Walk up from hit_object looking for a center-snap target.

    Used by placement to anchor a cabinet/appliance horizontally on
    a window (base cabinet under window) or on an existing product
    (range hood above a cabinet bay or cabinet body).

    kinds is a set; any of:
      'WINDOW'   - IS_WINDOW_BP wrapper; finds its child geo cage,
                   honors a height-collision check so an upper cabinet
                   doesn't try to center on a window it would hit.
      'BAY'      - IS_FACE_FRAME_BAY_CAGE; matches when the hit is on
                   a door / drawer front whose parent chain runs through
                   the bay. More-specific match than CABINET, so checked
                   first within the same parent-walk iteration.
      'PRODUCT'  - IS_FACE_FRAME_CABINET_CAGE / IS_FRAMELESS_CABINET_CAGE
                   / IS_APPLIANCE. Matches when no bay is in the chain
                   (cursor on a stile / carcass / appliance shell).

    cab_z_range is the (z_start, z_end) wall-local bounds of the
    object being placed. Used only for the WINDOW height-collision
    check; other kinds skip it (the hood mounts above floor products
    by construction).

    Returns (center_x, kind, width) in wall-local coordinates, or
    (None, None, None) when no qualifying target is found.
    """
    if hit_object is None or wall is None:
        return None, None, None

    cab_z_start, cab_z_end = cab_z_range
    target_obj = None
    target_kind = None

    current = hit_object
    while current is not None and current is not wall:
        # Bay cage is checked before product so a hit on a door
        # front (whose chain runs door -> pivot -> opening -> bay
        # -> cabinet root) returns the bay rather than the whole
        # cabinet.
        if 'BAY' in kinds and current.get('IS_FACE_FRAME_BAY_CAGE'):
            target_obj = current
            target_kind = 'BAY'
            break
        if 'PRODUCT' in kinds:
            if (current.get('IS_FACE_FRAME_CABINET_CAGE')
                    or current.get('IS_FRAMELESS_CABINET_CAGE')
                    or current.get('IS_APPLIANCE')):
                target_obj = current
                target_kind = 'PRODUCT'
                break
        if 'WINDOW' in kinds and current.get('IS_WINDOW_BP'):
            # Window may be a single object marked both IS_WINDOW_BP
            # and IS_GEONODE_CAGE (current convention) or a wrapper
            # whose IS_GEONODE_CAGE child carries the dimensions
            # (older window builds). Probe self first, then children.
            if current.get('IS_GEONODE_CAGE'):
                target_obj = current
                target_kind = 'WINDOW'
                break
            for child in current.children:
                if child.get('IS_GEONODE_CAGE'):
                    target_obj = child
                    target_kind = 'WINDOW'
                    break
            if target_obj is not None:
                break
        current = current.parent

    if target_obj is None:
        return None, None, None

    # Compute the target's width using whichever accessor fits its kind.
    try:
        if target_kind == 'PRODUCT' and target_obj.get('IS_FACE_FRAME_CABINET_CAGE'):
            tgt_width = target_obj.face_frame_cabinet.width
        elif target_kind == 'PRODUCT' and target_obj.get('IS_FRAMELESS_CABINET_CAGE'):
            # Frameless cabinets are GeoNodeCage with an array modifier;
            # total width = cell width * count.
            cage = hb_types.GeoNodeObject(target_obj)
            cell_w = cage.get_input('Dim X')
            count = 1
            for mod in target_obj.modifiers:
                if mod.type == 'ARRAY':
                    count = mod.count
                    break
            tgt_width = cell_w * count
        else:
            cage = hb_types.GeoNodeObject(target_obj)
            tgt_width = cage.get_input('Dim X')
    except Exception:
        return None, None, None

    if tgt_width is None or tgt_width <= 0.0:
        return None, None, None

    # Wall-local X bounds via matrix_world. Two corners of the cage
    # at local (0,0,0) and (width,0,0) map to wall-local (x0,_,_)
    # and (x1,_,_); back-side rotation flips x0 > x1, hence min/max.
    wall_inv = wall.matrix_world.inverted()
    p0 = wall_inv @ (target_obj.matrix_world @ Vector((0.0, 0.0, 0.0)))
    p1 = wall_inv @ (target_obj.matrix_world @ Vector((tgt_width, 0.0, 0.0)))
    tgt_x_min = min(p0.x, p1.x)
    tgt_x_max = max(p0.x, p1.x)

    if target_kind == 'WINDOW':
        try:
            tgt_height = hb_types.GeoNodeObject(target_obj).get_input('Dim Z')
        except Exception:
            return None, None, None
        # Window cages are wall-parented, so location.z is wall-local
        # and matches the cabinet's wall-local Z directly.
        # Tolerance is needed because Blender stores location in float32:
        # a window resting at 36" reports 0.9143999814987183m while a
        # 36"-tall cabinet's computed top is 0.9144m exactly. Touching
        # ranges shouldn't count as colliding.
        eps = units.inch(0.0625)
        tgt_z_start = target_obj.location.z
        tgt_z_end = tgt_z_start + tgt_height
        if cab_z_start + eps < tgt_z_end and tgt_z_start + eps < cab_z_end:
            return None, None, None

    center_x = (tgt_x_min + tgt_x_max) / 2.0
    return center_x, target_kind, (tgt_x_max - tgt_x_min)


def _auto_bay_qty(cabinet_width):
    """Pick a bay quantity that gives ~_TARGET_BAY_WIDTH per bay."""
    qty = round(cabinet_width / _TARGET_BAY_WIDTH)
    return max(_BAY_QTY_MIN, min(qty, _BAY_QTY_MAX))


def _detect_wall(op, context):
    """Find a wall via raycast or floor-projection fallback.

    Returns the wall object or None. May update op.hit_location to a
    projected floor point if the fallback path is used.

    The fallback exists so cursor flicker on wall surfaces (which
    causes raycasts to occasionally miss the wall) doesn't kick the
    cabinet off the wall mid-placement.
    """
    if op.hit_object is not None:
        wall = _find_wall_root(op.hit_object)
        if wall is not None:
            return wall
    return _find_nearest_wall_from_cursor(op, context)


def _find_nearest_wall_from_cursor(op, context):
    """Project cursor onto floor plane and find nearest wall within snap.

    Side effect: updates op.hit_location to the projected floor point
    on the wall so downstream positioning math still has a valid
    world-space point even though the raycast missed.
    """
    region = op.region
    if region is None:
        return None
    rv3d = region.data
    if rv3d is None:
        return None

    view_origin = view3d_utils.region_2d_to_origin_3d(
        region, rv3d, op.mouse_pos)
    view_dir = view3d_utils.region_2d_to_vector_3d(
        region, rv3d, op.mouse_pos)
    floor_point = intersect_line_plane(
        view_origin,
        view_origin + view_dir * 10000,
        Vector((0, 0, 0)),
        Vector((0, 0, 1)),
    )
    if not floor_point:
        return None

    cursor_2d = Vector((floor_point.x, floor_point.y))
    nearest_wall = None
    nearest_distance = _WALL_SNAP_DISTANCE

    for obj in context.scene.objects:
        if 'IS_WALL_BP' not in obj:
            continue
        try:
            wall = hb_types.GeoNodeWall(obj)
            if not wall.has_modifier():
                continue
            wall_length = wall.get_input('Length')
            wall_thickness = wall.get_input('Thickness')
        except Exception:
            continue

        wall_matrix = obj.matrix_world
        local_start = Vector((0, wall_thickness / 2, 0))
        local_end = Vector((wall_length, wall_thickness / 2, 0))
        world_start = wall_matrix @ local_start
        world_end = wall_matrix @ local_end
        start_2d = Vector((world_start.x, world_start.y))
        end_2d = Vector((world_end.x, world_end.y))

        closest, percent = intersect_point_line(
            cursor_2d, start_2d, end_2d)
        closest_2d = Vector(closest[:2])
        if percent < 0:
            closest_2d = start_2d
        elif percent > 1:
            closest_2d = end_2d

        distance = (cursor_2d - closest_2d).length
        if distance < nearest_distance and 0 <= percent <= 1:
            nearest_distance = distance
            nearest_wall = obj
            # Update hit_location so downstream code has a valid
            # world-space point on/near the wall to work with.
            op.hit_location = Vector(
                (floor_point.x, floor_point.y, 0))

    return nearest_wall


def _is_corner_cabinet(obj):
    """Return True if `obj` is a face frame corner cabinet root.

    Detected by the face_frame_cabinet PropertyGroup's corner_type
    being anything other than 'NONE' (e.g., 'PIE_CUT', 'DIAGONAL',
    'INSIDE_CORNER'). Returns False for regular cabinets, frameless
    cabinets, and any object without the PropertyGroup.
    """
    ff = getattr(obj, 'face_frame_cabinet', None)
    if ff is None:
        return False
    return getattr(ff, 'corner_type', 'NONE') != 'NONE'


def _compute_corner_left_snap_transform(snap_obj, new_object_width):
    """LEFT-snap transform for a face frame corner cabinet.

    A corner cabinet is L-shaped: its "left arm" runs the full
    depth of the cabinet (Dim Y) along the perpendicular wall (the
    one the corner cabinet's parent wall meets at the room corner).
    The face_frame_cabinet.left_depth value is the *thickness* of
    the left arm (perpendicular to its length axis), not its length;
    the length is the cabinet's overall depth.

    Continuing a cabinet run "to the left" of a corner cabinet means
    continuing along the perpendicular wall - which requires the new
    cabinet to be rotated 90 CCW relative to the corner cabinet so
    its back faces the perpendicular wall, and offset so its right
    edge lands at the end of the left arm.

    Math in the corner cabinet's local frame:
      - Origin at (0, -(corner_depth + new_object_width), 0).
        After +90 CCW rotation, the new cabinet's local +X axis
        maps to corner-local +Y direction, so its right edge
        (local x = new_object_width) lands at corner-local
        y = -corner_depth - the end of the left arm.
      - Rotation: corner's Z rotation + pi/2

    Returns (Vector, Euler) world-space, or None if corner depth
    isn't readable.
    """
    ff = getattr(snap_obj, 'face_frame_cabinet', None)
    if ff is None:
        return None
    try:
        corner_depth = ff.depth
    except AttributeError:
        return None

    local_offset = Vector((0, -(corner_depth + new_object_width), 0))
    rot_z = snap_obj.rotation_euler.z
    world_offset = Matrix.Rotation(rot_z, 4, 'Z') @ local_offset
    new_loc = snap_obj.location + world_offset

    new_rot = snap_obj.rotation_euler.copy()
    new_rot.z = new_rot.z + math.pi / 2
    return (new_loc, new_rot)


def _try_auto_merge_with_neighbor(context, cab_obj):
    """If a compatible face-frame cabinet sits abutting cab_obj on the
    same wall, merge cab_obj into it and return the surviving anchor.
    Returns None when no merge happens.

    "Compatible" is everything merge_cabinets pre-flights: same parent,
    same height / depth / Z, abutting within tolerance, no corner type.
    Prefers the left neighbor when both sides are compatible.
    """
    parent = cab_obj.parent
    if parent is None:
        return None

    # Tall and refrigerator cabinets (both cabinet_type='TALL') don't
    # auto-merge - heights are visually distinct so adjacent placement
    # is usually intentional, not a join. Manual join via the
    # right-click menu still works.
    if cab_obj.face_frame_cabinet.cabinet_type == 'TALL':
        return None

    # Force a depsgraph update so cab_obj.matrix_world reflects the
    # parent + location assignments _finalize just made. Without this,
    # the Z-match check in merge_cabinets sees a stale world Z (often
    # the cabinet's pre-parenting world origin) and rejects what should
    # be a valid auto-merge. Surfaces on uppers where wall-local Z is
    # non-zero; bases sit at Z=0 so the staleness happens to match.
    context.view_layer.update()

    cab_x = cab_obj.location.x
    cab_w = cab_obj.face_frame_cabinet.width
    eps = 1e-4

    left_neighbor = None
    right_neighbor = None
    for sib in parent.children:
        if sib is cab_obj:
            continue
        if not sib.get(types_face_frame.TAG_CABINET_CAGE):
            continue
        if sib.face_frame_cabinet.cabinet_type == 'TALL':
            continue
        sib_x = sib.location.x
        sib_w = sib.face_frame_cabinet.width
        # Pick the closest neighbor on each side. The merge primitive
        # itself enforces the abutment tolerance; here we just sort
        # roughly into "to the left" vs "to the right" buckets.
        if sib_x + sib_w <= cab_x + eps:
            if left_neighbor is None or sib_x > left_neighbor.location.x:
                left_neighbor = sib
        elif sib_x >= cab_x + cab_w - eps:
            if right_neighbor is None or sib_x < right_neighbor.location.x:
                right_neighbor = sib

    if left_neighbor is not None:
        if types_face_frame.merge_cabinets(left_neighbor, cab_obj, 'RIGHT'):
            return left_neighbor
    if right_neighbor is not None:
        if types_face_frame.merge_cabinets(right_neighbor, cab_obj, 'LEFT'):
            return right_neighbor
    return None




def _wall_corner_angle_deg(wall_a_obj, wall_b_obj):
    """Unsigned angle (degrees) between two walls' length axes (their
    local +X axes in world space). Returns 0 for parallel walls and 90
    for perpendicular ones - used to confirm a corner is square enough
    for blind setup.
    """
    a_axis = wall_a_obj.matrix_world.to_3x3() @ Vector((1.0, 0.0, 0.0))
    b_axis = wall_b_obj.matrix_world.to_3x3() @ Vector((1.0, 0.0, 0.0))
    a_axis.z = 0.0
    b_axis.z = 0.0
    if a_axis.length < 1e-8 or b_axis.length < 1e-8:
        return 0.0
    a_axis.normalize()
    b_axis.normalize()
    cos = max(-1.0, min(1.0, a_axis.dot(b_axis)))
    return math.degrees(math.acos(cos))


def _max_intrusion_neighbor(adj_wall_obj, our_wall_obj, side):
    """Find the cabinet child on adj_wall_obj whose footprint reaches
    farthest into our_wall_obj's bounds at the requested end ('left'
    or 'right'). Returns (cabinet_obj, intrusion_distance) or None.
    """
    our_wall = hb_types.GeoNodeWall(our_wall_obj)
    our_length = our_wall.get_input('Length')
    our_inv = our_wall_obj.matrix_world.inverted()

    best_obj = None
    best_intrusion = 0.0

    for child in adj_wall_obj.children:
        if child.get('obj_x') or child.get('IS_2D_ANNOTATION'):
            continue
        if not any(m in child for m in hb_placement.CABINET_MARKERS):
            continue
        try:
            geo = hb_types.GeoNodeObject(child)
            child_w = geo.get_input('Dim X')
            child_d = geo.get_input('Dim Y')
        except Exception:
            continue
        local_corners = [
            Vector((0.0, 0.0, 0.0)),
            Vector((child_w, 0.0, 0.0)),
            Vector((0.0, -child_d, 0.0)),
            Vector((child_w, -child_d, 0.0)),
        ]
        corners_our = [our_inv @ (child.matrix_world @ c) for c in local_corners]
        if side == 'left':
            intrusion = max((c.x for c in corners_our if c.x > 0), default=0.0)
        else:
            intrusion = max(
                (our_length - c.x for c in corners_our if c.x < our_length),
                default=0.0,
            )
        if intrusion > best_intrusion:
            best_intrusion = intrusion
            best_obj = child
    if best_obj is None:
        return None
    return (best_obj, best_intrusion)


def _neighbor_blind_side(neighbor_obj, corner_world_pos):
    """Which end of neighbor_obj sits closer to the corner world point.
    Returns 'LEFT' (neighbor's local x=0 end is at corner) or 'RIGHT'
    (neighbor's local x=width end is at corner). Used to decide which
    side of the neighbor becomes the blind end.
    """
    try:
        width = neighbor_obj.face_frame_cabinet.width
    except AttributeError:
        # Fallback for non-face-frame cabinets (shouldn't reach here, but
        # don't blow up if it does).
        try:
            width = hb_types.GeoNodeObject(neighbor_obj).get_input('Dim X')
        except Exception:
            return 'LEFT'
    left_world = neighbor_obj.matrix_world.translation
    right_world = neighbor_obj.matrix_world @ Vector((width, 0.0, 0.0))
    d_left = (left_world.xy - corner_world_pos.xy).length
    d_right = (right_world.xy - corner_world_pos.xy).length
    return 'LEFT' if d_left <= d_right else 'RIGHT'


def _detect_blind_corner_neighbor(cab_obj):
    """If cab_obj sits at a 90-degree wall corner with a perpendicular
    face-frame cabinet at the corner, return the neighbor and which
    side of the NEIGHBOR becomes blind ('LEFT' or 'RIGHT'). Returns
    None when no qualifying neighbor.

    Two qualifying geometric cases per connected-wall direction:
      (a) Our cabinet's near-end edge sits at the wall corner end
          (within 1"). This is the cabinet whose body extends across
          the corner.
      (b) Our cabinet's far-end edge meets the neighbor's intrusion
          boundary on this wall (within 1"). This is the cabinet
          placed against the corner cabinet's body.
    """
    wall = cab_obj.parent
    if wall is None or 'IS_WALL_BP' not in wall:
        return None
    try:
        wall_geo = hb_types.GeoNodeWall(wall)
        wall_length = wall_geo.get_input('Length')
    except Exception:
        return None

    cab_props = cab_obj.face_frame_cabinet
    cab_left = cab_obj.location.x
    cab_right = cab_left + cab_props.width

    EDGE_TOL = units.inch(1.0)
    ANGLE_TOL_DEG = 5.0

    for direction in ('left', 'right'):
        adj_node = wall_geo.get_connected_wall(direction=direction)
        if adj_node is None:
            continue
        result = _max_intrusion_neighbor(adj_node.obj, wall, direction)
        if result is None:
            continue
        neighbor, intrusion = result
        if 'IS_FACE_FRAME_CABINET_CAGE' not in neighbor:
            continue

        angle_deg = _wall_corner_angle_deg(wall, adj_node.obj)
        if abs(angle_deg - 90.0) > ANGLE_TOL_DEG:
            continue

        # Case (a): our edge at the wall corner end.
        # Case (b): our far edge at the intrusion boundary.
        if direction == 'left':
            qualifies = (cab_left <= EDGE_TOL
                         or abs(cab_left - intrusion) <= EDGE_TOL)
        else:
            qualifies = (cab_right >= wall_length - EDGE_TOL
                         or abs(cab_right - (wall_length - intrusion)) <= EDGE_TOL)
        if not qualifies:
            continue

        # Corner world position: meeting point of our wall and adj wall.
        if direction == 'left':
            corner_world = wall.matrix_world.translation
        else:
            corner_world = wall.matrix_world @ Vector((wall_length, 0.0, 0.0))

        blind_side = _neighbor_blind_side(neighbor, corner_world)
        return (neighbor, blind_side)
    return None


def _align_base_tall_toe_kick(cab_obj):
    """Align toe-kick face position between abutting BASE and TALL
    neighbors on the same parent wall.

    Tall cabinets are deeper than bases (default 25.5" vs 24"). With a
    common toe_kick_setback the tall's recessed kick face sits 1.5"
    further back than the base's, breaking the visual line of the toe
    kick run when they're placed side by side. Increasing the deeper
    cabinet's setback by the depth difference brings its kick face
    forward to the same world-Y as the shallower neighbor's.

    Only fires when both cabinets use NOTCH toe kicks. FLUSH has no
    setback and FLOATING uses a separate base assembly whose alignment
    is handled differently. Adjustment is one-shot at placement; later
    independent edits to either cabinet are not tracked.
    """
    parent = cab_obj.parent
    if parent is None:
        return

    cab_props = cab_obj.face_frame_cabinet
    if cab_props.toe_kick_type != 'NOTCH':
        return
    cab_type = cab_props.cabinet_type
    if cab_type not in ('BASE', 'TALL'):
        return

    cab_x = cab_obj.location.x
    cab_w = cab_props.width
    cab_d = cab_props.depth
    eps = 1e-4

    # Collect immediate left/right abutting siblings of the opposite
    # type with NOTCH toe kicks.
    other_type = 'TALL' if cab_type == 'BASE' else 'BASE'
    neighbors = []
    for sib in parent.children:
        if sib is cab_obj:
            continue
        if not sib.get(types_face_frame.TAG_CABINET_CAGE):
            continue
        sib_props = sib.face_frame_cabinet
        if sib_props.cabinet_type != other_type:
            continue
        if sib_props.toe_kick_type != 'NOTCH':
            continue
        sib_x = sib.location.x
        sib_w = sib_props.width
        if abs(sib_x + sib_w - cab_x) < eps or \
           abs(sib_x - (cab_x + cab_w)) < eps:
            neighbors.append(sib)

    if not neighbors:
        return

    # When cab_obj is the deeper one (TALL), accumulate the max required
    # setback across abutting shallower neighbors and apply once. When
    # cab_obj is the shallower one (BASE), each abutting deeper neighbor
    # gets its own setback adjusted to match cab_obj.
    cab_target_setback = None
    for nb in neighbors:
        nb_props = nb.face_frame_cabinet
        nb_d = nb_props.depth
        if abs(nb_d - cab_d) < eps:
            continue
        if cab_d > nb_d:
            target = nb_props.toe_kick_setback + (cab_d - nb_d)
            if cab_target_setback is None or target > cab_target_setback:
                cab_target_setback = target
        else:
            target = cab_props.toe_kick_setback + (nb_d - cab_d)
            if abs(nb_props.toe_kick_setback - target) > eps:
                nb_props.toe_kick_setback = target

    if cab_target_setback is not None and \
       abs(cab_props.toe_kick_setback - cab_target_setback) > eps:
        cab_props.toe_kick_setback = cab_target_setback


class hb_face_frame_OT_place_cabinet(bpy.types.Operator,
                                     hb_placement.PlacementMixin):
    """Modal: cursor drags a face-frame preview cage, click to commit."""
    bl_idname = "hb_face_frame.place_cabinet"
    bl_label = "Place Face Frame Cabinet"
    bl_description = (
        "Place a face frame cabinet on a wall or on the floor. "
        "Up/Down arrows adjust bay quantity, Left/Right arrows set "
        "gap offset, W or numbers type width, Esc cancels."
    )
    bl_options = {'REGISTER', 'UNDO'}

    cabinet_name: bpy.props.StringProperty(
        name="Cabinet Name",
        description="Face frame cabinet type to place",
        default="",
    )  # type: ignore

    bay_qty: bpy.props.IntProperty(
        name="Bay Quantity",
        description="Number of bays (1-10)",
        default=1, min=_BAY_QTY_MIN, max=_BAY_QTY_MAX,
    )  # type: ignore

    # Live state during modal session. Reset on FINISHED/CANCELLED.
    _preview_cage = None
    _array_modifier = None
    _cabinet_width: float = 0.0     # total cabinet width (m)
    _auto_bay_qty: bool = True      # True until user presses arrow keys
    _place_on_front: bool = True    # which side of the wall
    _fill_mode: bool = True         # False after the user types a width
    _single_placement: bool = False # True for cabinets that don't fill or tile (e.g., Sink)
    _gap_snap = None                # None | 'LEFT' | 'CENTER' | 'RIGHT' gap-position snap
    _center_snap_state = None       # None | 'WINDOW' - cursor-over-target snap
    _fill_mode_before_center_snap: bool = False   # tracks transient fill->non-fill flip
    _cabinet_snap_side = None       # None | 'LEFT' | 'RIGHT' off-wall cabinet-to-cabinet snap

    # Gap-relative offset state. None means "not set"; the cabinet
    # follows the cursor and auto-snaps to gap edges/center as before.
    # Once typed, the cabinet locks to that offset relative to the
    # wall gap detected at the moment of commit.
    _left_offset: float = None
    _right_offset: float = None
    _gap_left_boundary: float = 0.0
    _gap_right_boundary: float = 0.0
    _gap_wall = None                # wall the gap was measured against
    _position_locked: bool = False  # True while an offset is in effect

    # ---------------- invoke / modal ----------------

    def invoke(self, context, event):
        if not self.cabinet_name:
            self.report({'WARNING'}, "No cabinet name supplied")
            return {'CANCELLED'}
        if types_face_frame.get_cabinet_class(self.cabinet_name) is None:
            self.report({'WARNING'},
                        f"Unknown cabinet name: {self.cabinet_name}")
            return {'CANCELLED'}

        scene_props = context.scene.hb_face_frame
        self._place_on_front = True
        cls = types_face_frame.get_cabinet_class(self.cabinet_name)
        # cls() does no Blender-side work - it just runs the Python
        # __init__ to capture default_width from scene props for
        # subclasses like SinkFaceFrameCabinet.
        cls_inst = cls()
        self._single_placement = bool(getattr(cls_inst, 'single_placement', False))
        if self._single_placement:
            self._cabinet_width = cls_inst.default_width
            self._auto_bay_qty = False
            self._fill_mode = False
            self.bay_qty = 1
        else:
            self._cabinet_width = scene_props.default_cabinet_width
            self._auto_bay_qty = True
            self._fill_mode = True

        try:
            self._create_preview_cage(context)
        except Exception as e:
            self.report({'ERROR'}, f"Preview creation failed: {e}")
            return {'CANCELLED'}

        # Initial position: 3D cursor (XY); Z follows cabinet_type
        cage_obj = self._preview_cage.obj
        cursor_loc = context.scene.cursor.location
        cage_obj.location.x = cursor_loc.x
        cage_obj.location.y = cursor_loc.y
        cabinet_type = _cabinet_type_for_name(self.cabinet_name)
        if cabinet_type == 'UPPER':
            cage_obj.location.z = scene_props.default_wall_cabinet_location
        else:
            cage_obj.location.z = cursor_loc.z

        self.init_placement(context)
        if self.region is None:
            self._delete_preview()
            self.report({'WARNING'}, "No 3D viewport available")
            return {'CANCELLED'}
        self.register_placement_object(cage_obj)

        # Screen-space dimension feedback during the modal. Specs are
        # rebuilt by _position_on_wall / _position_free; the draw
        # handler reads self._placement_dim_specs each frame.
        self.add_placement_dim_handler(context)

        context.window_manager.modal_handler_add(self)
        self._update_header(context)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if self._preview_cage is None:
            return self._cancel(context)

        # Pass through viewport navigation. Numpad digit keys are
        # intentionally NOT in this list - they're needed for typed
        # input (the mixin's NUMBER_KEYS dict maps NUMPAD_0..9 to
        # digits). Sacrificing the numpad-view shortcuts during
        # placement is acceptable; orbit/pan/zoom still work via
        # middle mouse + wheel.
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}

        # While typing, route input through the mixin's typing handler
        # FIRST. It owns ESC (cancel typing) and ENTER (commit width)
        # in this state - we mustn't let our own ESC handler eat the
        # event and cancel the whole modal.
        if self.placement_state == hb_placement.PlacementState.TYPING:
            if self.handle_typing_event(event):
                self._update_header(context)
                return {'RUNNING_MODAL'}

        # 'W' key starts typing width explicitly. Matches the frameless
        # convention. Number keys also start typing (via mixin auto-
        # start) but default to WIDTH because get_default_typing_target
        # returns WIDTH below.
        if (event.type == 'W' and event.value == 'PRESS'
                and self.placement_state == hb_placement.PlacementState.PLACING):
            self.start_typing(hb_placement.TypingTarget.WIDTH)
            self._update_header(context)
            return {'RUNNING_MODAL'}

        # Mixin handles number keys (auto-starts typing).
        if (event.type in hb_placement.NUMBER_KEYS
                and event.value == 'PRESS'
                and self.placement_state == hb_placement.PlacementState.PLACING):
            if self.handle_typing_event(event):
                self._update_header(context)
                return {'RUNNING_MODAL'}

        if event.type in {'ESC', 'RIGHTMOUSE'} and event.value == 'PRESS':
            return self._cancel(context)

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            return self._finalize(context)

        if event.type == 'UP_ARROW' and event.value == 'PRESS':
            if self._single_placement:
                return {'RUNNING_MODAL'}
            new_qty = min(self.bay_qty + 1, _BAY_QTY_MAX)
            if new_qty != self.bay_qty:
                self.bay_qty = new_qty
                self._auto_bay_qty = False
                self._update_cage()
                self._update_header(context)
            return {'RUNNING_MODAL'}

        if event.type == 'DOWN_ARROW' and event.value == 'PRESS':
            if self._single_placement:
                return {'RUNNING_MODAL'}
            new_qty = max(self.bay_qty - 1, _BAY_QTY_MIN)
            if new_qty != self.bay_qty:
                self.bay_qty = new_qty
                self._auto_bay_qty = False
                self._update_cage()
                self._update_header(context)
            return {'RUNNING_MODAL'}

        # Left/right arrows: type a gap-edge offset. Only meaningful
        # when a wall (and therefore a gap) is in play - off-wall the
        # arrows do nothing.
        if event.type == 'LEFT_ARROW' and event.value == 'PRESS':
            if self._gap_wall is not None:
                self._handle_offset_arrow(context, side='LEFT')
            return {'RUNNING_MODAL'}

        if event.type == 'RIGHT_ARROW' and event.value == 'PRESS':
            if self._gap_wall is not None:
                self._handle_offset_arrow(context, side='RIGHT')
            return {'RUNNING_MODAL'}

        if event.type == 'MOUSEMOVE':
            # While typing an offset, freeze positioning entirely -
            # the live preview drives the cage from on_typed_value_changed
            # and a re-snap here would clobber it.
            if (self.placement_state == hb_placement.PlacementState.TYPING
                    and self.typing_target in (
                        hb_placement.TypingTarget.OFFSET_X,
                        hb_placement.TypingTarget.OFFSET_RIGHT)):
                return {'RUNNING_MODAL'}

            # Hide the cage during the raycast so the ray passes through
            # to the wall/floor behind it. HB_CURRENT_DRAW_OBJ filters
            # the cage out of the snap result, but it doesn't stop the
            # ray from hitting the cage's mesh - which forces the
            # radial fallback search to return wall hits at random
            # offset angles, flickering the position. Hiding the cage
            # avoids that entirely. (Frameless uses the same pattern.)
            cage_obj = self._preview_cage.obj
            cage_obj.hide_set(True)
            try:
                self.update_snap(context, event)
            finally:
                cage_obj.hide_set(False)
            self._position_from_hit(context)

        return {'RUNNING_MODAL'}

    # ---------------- preview cage ----------------

    def _create_preview_cage(self, context):
        """Build the wireframe cage matching face-frame cabinet conventions.

        Mirror Y = True flips the cage to extend in -Y direction from
        origin, matching how face-frame cabinets are built (origin at
        the back face, geometry extending into the room).

        HB_CURRENT_DRAW_OBJ excludes the cage from hb_snap raycasts so
        the cursor can't catch on the cage and trigger self-snap.
        """
        scene_props = context.scene.hb_face_frame
        cabinet_type = _cabinet_type_for_name(self.cabinet_name)
        depth, height = _cage_dimensions(scene_props, cabinet_type)
        cabinet_width = scene_props.default_cabinet_width

        cage = hb_types.GeoNodeCage()
        cage.create('FaceFramePlacementPreview')
        cage.set_input('Dim X', cabinet_width / max(self.bay_qty, 1))
        cage.set_input('Dim Y', depth)
        cage.set_input('Dim Z', height)
        cage.set_input('Mirror Y', True)

        mod = cage.obj.modifiers.new(name='BayQty', type='ARRAY')
        mod.use_relative_offset = True
        mod.relative_offset_displace = (1, 0, 0)
        mod.use_constant_offset = False
        mod.count = self.bay_qty

        cage.obj.display_type = 'WIRE'
        cage.obj.show_in_front = True
        cage.obj['HB_CURRENT_DRAW_OBJ'] = True

        self._preview_cage = cage
        self._array_modifier = mod

    def _update_cage(self):
        if self._preview_cage is None:
            return
        cell_width = self._cabinet_width / max(self.bay_qty, 1)
        self._preview_cage.set_input('Dim X', cell_width)
        if self._array_modifier is not None:
            self._array_modifier.count = self.bay_qty

    # ---------------- typed input ----------------
    #
    # The PlacementMixin owns the typing state machine (typed_value
    # buffer, ENTER/ESC/BACKSPACE, NUMBER_KEYS auto-start). We just
    # provide the three integration points it expects subclasses to
    # override:
    #
    #   get_default_typing_target  - which TypingTarget number keys
    #                                 should default to (WIDTH for us)
    #   on_typed_value_changed     - live preview as user types
    #   apply_typed_value          - commit on ENTER

    def get_default_typing_target(self):
        return hb_placement.TypingTarget.WIDTH

    def on_typed_value_changed(self):
        """Live preview: parse typed_value and update cage every keystroke.

        Width: resize cage in place. Offsets: temporarily apply the
        offset, reposition, then restore the stored value - the offset
        is only committed on Enter (apply_typed_value).

        Errors are silent (incomplete typing like "5'" briefly fails to
        parse, which is fine - we just skip live preview until the
        value parses).
        """
        if not self.typed_value:
            return
        parsed = self.parse_typed_distance()
        if parsed is None:
            return

        if self.typing_target == hb_placement.TypingTarget.WIDTH:
            if parsed > 0:
                self._apply_width(parsed, fill_mode=False)
                # User committed to a width - don't auto-restore fill
                # mode if they later leave a center snap.
                self._fill_mode_before_center_snap = False
            return

        if self.typing_target == hb_placement.TypingTarget.OFFSET_X:
            if parsed < 0 or self._gap_wall is None:
                return
            old_val = self._left_offset
            self._left_offset = parsed
            self._reposition_with_offsets(bpy.context)
            self._left_offset = old_val
            return

        if self.typing_target == hb_placement.TypingTarget.OFFSET_RIGHT:
            if parsed < 0 or self._gap_wall is None:
                return
            old_val = self._right_offset
            self._right_offset = parsed
            self._reposition_with_offsets(bpy.context)
            self._right_offset = old_val
            return

    def apply_typed_value(self):
        """Commit the typed value on ENTER.

        WIDTH disables fill mode and resizes the cage. OFFSET_X /
        OFFSET_RIGHT lock the cabinet to that offset from the gap edge
        and clear any active edge/center snap (the explicit offset
        wins over snap heuristics).
        """
        parsed = self.parse_typed_distance()

        if self.typing_target == hb_placement.TypingTarget.WIDTH:
            if parsed is not None and parsed > 0:
                self._apply_width(parsed, fill_mode=False)
                self._fill_mode_before_center_snap = False

        elif self.typing_target == hb_placement.TypingTarget.OFFSET_X:
            if parsed is not None and parsed >= 0 and self._gap_wall is not None:
                self._left_offset = parsed
                self._gap_snap = None
                self._position_locked = True
                self._reposition_with_offsets(bpy.context)

        elif self.typing_target == hb_placement.TypingTarget.OFFSET_RIGHT:
            if parsed is not None and parsed >= 0 and self._gap_wall is not None:
                self._right_offset = parsed
                self._gap_snap = None
                self._position_locked = True
                self._reposition_with_offsets(bpy.context)

        self.stop_typing()

    def _apply_width(self, width, fill_mode):
        """Set cabinet width and refresh derived state.

        fill_mode=False is the typed-width path: width comes from the
        user, not from a wall gap, so we shouldn't let the next
        wall-hover overwrite it.

        fill_mode=True is the auto-fill path: width comes from the
        wall gap and changes naturally as the cursor moves.
        """
        if self._single_placement:
            fill_mode = False
        if abs(width - self._cabinet_width) < 1e-5 and fill_mode == self._fill_mode:
            return
        self._cabinet_width = width
        self._fill_mode = fill_mode
        if self._auto_bay_qty:
            new_qty = _auto_bay_qty(self._cabinet_width)
            if new_qty != self.bay_qty:
                self.bay_qty = new_qty
        self._update_cage()

        # Typed-width path: position and dim overlay haven't run since
        # the last MOUSEMOVE, so the cage just resized in place. Re-
        # run positioning against the cached hit so the preview
        # reflects the new width immediately. Fill mode is invoked
        # from inside _position_on_wall - skipping the re-run there
        # avoids redundant work (the caller is about to set position
        # itself).
        if not fill_mode and self.hit_location is not None:
            self._position_from_hit(bpy.context)

    def _update_header(self, context):
        bay_label = f"{self.bay_qty} bay" + ("" if self.bay_qty == 1 else "s")
        mode = "auto" if self._auto_bay_qty else "manual"
        side = "front" if self._place_on_front else "back"
        width_in = self._cabinet_width * 39.37008

        # When the user is typing, show the live buffer prominently so
        # they can see what they've entered. Label which value is
        # being typed so left/right offsets aren't ambiguous.
        if self.placement_state == hb_placement.PlacementState.TYPING:
            typed = self.get_typed_display_string()
            label = {
                hb_placement.TypingTarget.WIDTH: "Width",
                hb_placement.TypingTarget.OFFSET_X: "Offset (←)",
                hb_placement.TypingTarget.OFFSET_RIGHT: "Offset (→)",
            }.get(self.typing_target, "Value")
            hb_placement.draw_header_text(
                context,
                f"{self.cabinet_name}  -  {label}: {typed}  -  "
                "Enter: apply   ←/→: switch offset   "
                "Esc: cancel typing   Backspace: delete"
            )
        else:
            offset_hint = ""
            if self._left_offset is not None:
                offset_hint += (
                    f"  L:{units.unit_to_string(context.scene.unit_settings, self._left_offset)}"
                )
            if self._right_offset is not None:
                offset_hint += (
                    f"  R:{units.unit_to_string(context.scene.unit_settings, self._right_offset)}"
                )
            hb_placement.draw_header_text(
                context,
                f"{self.cabinet_name}  -  {bay_label} ({mode})  -  "
                f"width: {width_in:.1f}\"  -  side: {side}{offset_hint}  -  "
                "W/numbers: width   Up/Down: bays   "
                "←/→: gap offset   "
                "Click: place   Esc: cancel"
            )

    # ---------------- wall detection ----------------

    def _update_place_on_front(self, context, wall, local_hit_y, wall_thickness):
        """Decide which side of the wall the cursor is on, with hysteresis.

        Plan view: project cursor onto floor and use floor_point.y in
        wall-local space (raycasts in plan view often hit the wall's
        top face, where Y has no front/back signal).

        3D view: use the raycast hit's wall-local Y directly.

        Hysteresis prevents flicker: cursor must cross the wall
        centerline by _FRONT_BACK_HYSTERESIS before the side flips.
        """
        wall_center_y = wall_thickness / 2.0

        region = self.region
        rv3d = region.data if region is not None else None
        if rv3d is None:
            return

        view_matrix = rv3d.view_matrix
        view_z = view_matrix[2][2]
        is_plan_view = abs(view_z) > _PLAN_VIEW_THRESHOLD

        if is_plan_view:
            view_origin = view3d_utils.region_2d_to_origin_3d(
                region, rv3d, self.mouse_pos)
            view_dir = view3d_utils.region_2d_to_vector_3d(
                region, rv3d, self.mouse_pos)
            floor_point = intersect_line_plane(
                view_origin,
                view_origin + view_dir * 10000,
                Vector((0, 0, 0)),
                Vector((0, 0, 1)),
            )
            if floor_point is None:
                cursor_y = local_hit_y
            else:
                local_cursor = wall.matrix_world.inverted() @ floor_point
                cursor_y = local_cursor.y
        else:
            cursor_y = local_hit_y

        if cursor_y < wall_center_y - _FRONT_BACK_HYSTERESIS:
            self._place_on_front = True
        elif cursor_y > wall_center_y + _FRONT_BACK_HYSTERESIS:
            self._place_on_front = False
        # else: cursor is inside the hysteresis band - keep current side

    # ---------------- positioning ----------------

    def _position_from_hit(self, context):
        if self.hit_location is None:
            # No raycast hit and no fallback could even start - keep
            # cage where it is (don't jump to a stale or zero location).
            return

        wall = _detect_wall(self, context)
        if wall is not None:
            self._position_on_wall(context, wall)
        else:
            self._position_free(context)

    def _position_on_wall(self, context, wall):
        """Parent the cage to the wall and fill the available gap.

        Width auto-grows to fill the gap between the cabinet's neighbors
        on this wall. Bay quantity auto-fits the new width unless the
        user has manually locked it via arrow keys.

        Side handling:
          * Front: cage local y=0, no rotation.
          * Back: cage local y=wall_thickness, rotation=pi around Z,
            x offset by total cabinet width (because the rotation
            around the cabinet origin shifts the geometry).
        """
        cage_obj = self._preview_cage.obj

        # Fetch wall geometry
        try:
            wall_geo = hb_types.GeoNodeWall(wall)
            wall_thickness = wall_geo.get_input('Thickness')
        except Exception:
            wall_thickness = 0.0

        if cage_obj.parent is not wall:
            cage_obj.parent = wall
            cage_obj.matrix_parent_inverse.identity()

        # Cursor in wall-local coordinates
        local_hit = wall.matrix_world.inverted() @ self.hit_location
        cursor_x = local_hit.x

        # Decide which side (with hysteresis)
        self._update_place_on_front(context, wall, local_hit.y, wall_thickness)

        # Find the gap at this cursor X using the side-aware lookup:
        # only same-side cabinets count, vertical overlap is required
        # (so a base cabinet doesn't block placement of an upper above
        # it), doors and windows count for both sides. snap_x snaps to
        # the nearest gap edge when the cursor is close, otherwise
        # centers the cabinet on the cursor.
        cabinet_height = self._preview_cage.get_input('Dim Z')
        cabinet_depth = self._preview_cage.get_input('Dim Y')
        try:
            result = self.find_placement_gap_by_side(
                wall, cursor_x, self._cabinet_width,
                self._place_on_front, wall_thickness,
                object_z_start=cage_obj.location.z,
                object_height=cabinet_height,
                object_depth=cabinet_depth,
                exclude_obj=cage_obj,
            )
        except Exception:
            result = (None, None, None)
        gap_start, gap_end, snap_x = result
        # Non-parametric (applied) wall returns None tuple - fall back
        # to treating the wall as one open span.
        if gap_start is None:
            gap_start = 0.0
            gap_end = wall_geo.get_input('Length')
            snap_x = max(gap_start, cursor_x - self._cabinet_width / 2)

        gap_width = max(gap_end - gap_start, units.inch(1.0))

        # Snapshot the gap so offset typing can re-derive placement
        # without re-detecting the gap. Tracked on self so a subsequent
        # MOUSEMOVE-driven call refreshes the boundaries naturally
        # while the cabinet is still cursor-following (no lock yet).
        self._gap_left_boundary = gap_start
        self._gap_right_boundary = gap_end
        self._gap_wall = wall

        # If the user has typed an offset, hand off to the offset path.
        # The offset positioning ignores cursor-based snap entirely.
        if self._left_offset is not None or self._right_offset is not None:
            self._gap_snap = None
            self._reposition_with_offsets(context)
            return

        # Snap to gap edges or center with a fixed-floor tolerance
        # (so narrow cabinets still get a usable zone) and a small
        # hysteresis band that widens the release threshold once
        # snapped, so movement at the boundary doesn't pop in and
        # out. Disabled in fill mode - that mode pins the cabinet
        # to gap_start by definition. Corner snap takes priority
        # over center when their zones overlap (rare, only in narrow
        # gaps).
        engage_corner = max(self._cabinet_width / 2, units.inch(6.0))
        release_corner = engage_corner + units.inch(1.0)
        engage_center = units.inch(4.0)
        release_center = engage_center + units.inch(1.0)

        left_thresh = release_corner if self._gap_snap == 'LEFT' else engage_corner
        right_thresh = release_corner if self._gap_snap == 'RIGHT' else engage_corner
        center_thresh = release_center if self._gap_snap == 'CENTER' else engage_center

        near_left = (cursor_x - gap_start) < left_thresh
        near_right = (gap_end - cursor_x) < right_thresh
        gap_center = (gap_start + gap_end) / 2
        # Center snap only meaningful when cabinet actually fits with
        # room to spare; otherwise centered placement equals left
        # placement and the snap state would be misleading.
        near_center = (
            abs(cursor_x - gap_center) < center_thresh
            and self._cabinet_width < gap_width
        )

        if self._fill_mode:
            self._gap_snap = None
        elif near_left and near_right:
            # Cursor near both ends in a narrow gap - pick the closer.
            self._gap_snap = (
                'LEFT' if (cursor_x - gap_start) < (gap_end - cursor_x)
                else 'RIGHT'
            )
        elif near_left:
            self._gap_snap = 'LEFT'
        elif near_right:
            self._gap_snap = 'RIGHT'
        elif near_center:
            self._gap_snap = 'CENTER'
        else:
            self._gap_snap = None

        # Center-on-window snap. In fill mode, engaging the snap
        # transitions the cabinet to non-fill at the scene's default
        # width so the centering has a useful effect (a gap-wide
        # cabinet "centered on a window" would still span the gap).
        # Releasing the snap restores fill mode automatically via the
        # _fill_mode_before_center_snap tracker.
        cab_z_start = cage_obj.location.z
        cab_z_end = cab_z_start + cabinet_height
        cs_x, cs_kind, _cs_w = _find_center_snap(
            self.hit_object, wall, {'WINDOW'},
            (cab_z_start, cab_z_end),
        )
        center_snap_x = None
        if cs_kind is not None:
            if self._fill_mode:
                # Transition: remember we were filling, switch to a
                # typed-width-equivalent state at the scene default.
                self._fill_mode_before_center_snap = True
                scene_props = context.scene.hb_face_frame
                self._apply_width(scene_props.default_cabinet_width,
                                  fill_mode=False)
                # _apply_width updated cabinet_width in place. Refresh
                # our local copy so positioning math sees the new value.
                cabinet_width = self._cabinet_width
                gap_width = max(gap_end - gap_start, units.inch(1.0))
            self._center_snap_state = cs_kind
            center_snap_x = cs_x
            self._gap_snap = None
        else:
            # Snap released. If we entered the snap from fill mode,
            # restore fill mode so the cabinet resumes filling the gap.
            if self._fill_mode_before_center_snap:
                self._fill_mode_before_center_snap = False
                self._apply_width(gap_width, fill_mode=True)
                cabinet_width = self._cabinet_width
            self._center_snap_state = None

        # In fill mode, cabinet width follows the gap. With typed width
        # (fill_mode=False), the user controls the width; gap snap
        # forces the cabinet flush to the chosen end or centered in
        # the gap, otherwise we clamp the cursor-centered position
        # into the gap. Center snap (cursor over a window) takes
        # precedence over both the gap snap and the cursor position.
        if self._fill_mode:
            self._apply_width(gap_width, fill_mode=True)
            placement_x = gap_start
            cabinet_width = gap_width
        else:
            cabinet_width = min(self._cabinet_width, gap_width)
            if center_snap_x is not None:
                # Center cabinet on the snap target, clamped into gap.
                ideal_x = center_snap_x - cabinet_width / 2
                placement_x = max(gap_start, min(ideal_x, gap_end - cabinet_width))
            elif self._gap_snap == 'LEFT':
                placement_x = gap_start
            elif self._gap_snap == 'RIGHT':
                placement_x = gap_end - cabinet_width
            elif self._gap_snap == 'CENTER':
                placement_x = gap_start + (gap_width - cabinet_width) / 2
            else:
                placement_x = max(gap_start, min(snap_x, gap_end - cabinet_width))

        # Position based on which side. The Mirror Y cage extends in -Y
        # from origin (front-side convention). For back-side placement,
        # rotate 180 around Z (cage now extends +Y from origin) and
        # offset Y by wall_thickness. The X offset accounts for the
        # rotation around origin shifting the geometry by total width.
        if self._place_on_front:
            cage_obj.location.x = placement_x
            cage_obj.location.y = 0
            cage_obj.rotation_euler = (0, 0, 0)
        else:
            cage_obj.location.x = placement_x + cabinet_width
            cage_obj.location.y = wall_thickness
            cage_obj.rotation_euler = (0, 0, math.pi)

        # Refresh the GPU dimension overlay
        self._placement_dim_specs = self._build_dim_specs_on_wall(
            context, wall, wall_thickness,
            gap_start, gap_end, placement_x, cabinet_width,
        )
        if context.area is not None:
            context.area.tag_redraw()

    def _position_free(self, context):
        """Drop the cage at the world hit point, snapping flush to an
        existing off-wall cabinet's edge if the cursor is over one.
        """
        # Going off-wall releases any offset lock - the gap reference
        # is gone, so the cabinet returns to cursor-following.
        if self._gap_wall is not None or self._position_locked:
            self._gap_wall = None
            self._left_offset = None
            self._right_offset = None
            self._position_locked = False
        # Center snap is wall-bound; clear it whenever we go off-wall.
        self._center_snap_state = None

        cage_obj = self._preview_cage.obj

        # Cabinet-to-cabinet snap detection. detect_cabinet_snap_target
        # walks via find_cabinet_bp, which terminates the parent chain
        # at IS_WALL_BP - so wall-parented cabinets aren't returned as
        # snap targets when the hit is on a deep child part.
        snap_target, snap_side = self.detect_cabinet_snap_target(
            self.hit_object, self.hit_location)
        if snap_target is cage_obj:
            snap_target = None
            snap_side = None
        self._cabinet_snap_side = snap_side

        # Detach from any wall parent before repositioning
        if cage_obj.parent is not None:
            world = cage_obj.matrix_world.copy()
            cage_obj.parent = None
            cage_obj.matrix_world = world

        # In fill mode, off-wall placement returns the cage to the
        # scene default width. With a typed width, the user's value
        # sticks and we don't touch _cabinet_width.
        if self._fill_mode:
            scene_props = context.scene.hb_face_frame
            default_w = scene_props.default_cabinet_width
            self._apply_width(default_w, fill_mode=True)
            self._update_header(context)

        cabinet_type = _cabinet_type_for_name(self.cabinet_name)

        snap_result = None
        if snap_target is not None and snap_side is not None:
            if _is_corner_cabinet(snap_target) and snap_side == 'LEFT':
                # Corner cabinets need special LEFT-snap geometry: the
                # new cabinet pivots 90 CCW onto the perpendicular wall
                # and aligns with the corner's left_depth, not its
                # bounding-box left face.
                snap_result = _compute_corner_left_snap_transform(
                    snap_target, self._cabinet_width)
            else:
                snap_result = self.compute_cabinet_snap_transform(
                    snap_target, snap_side, self._cabinet_width)

        if snap_result is not None:
            new_loc, new_rot = snap_result
            cage_obj.location = new_loc
            cage_obj.rotation_euler = new_rot
            # Z override: uppers go to scene default; others inherit
            # the snap target's Z so a row stays at one height.
            if cabinet_type == 'UPPER':
                scene_props = context.scene.hb_face_frame
                cage_obj.location.z = scene_props.default_wall_cabinet_location
            else:
                cage_obj.location.z = snap_target.location.z
        else:
            self._cabinet_snap_side = None
            cage_obj.location.x = self.hit_location.x
            cage_obj.location.y = self.hit_location.y
            if cabinet_type != 'UPPER':
                cage_obj.location.z = self.hit_location.z
            cage_obj.rotation_euler = (0, 0, 0)

        self._placement_dim_specs = self._build_dim_specs_free(context)
        if context.area is not None:
            context.area.tag_redraw()

    # ---------------- offset-driven positioning ----------------

    def _handle_offset_arrow(self, context, side):
        """Start (or switch) typing a gap-edge offset.

        Front-side: LEFT arrow types the left offset, RIGHT the right.
        Back-side: meanings flip because the wall is rotated 180 from
        the user's point of view - the leftmost cabinet edge is on the
        viewer's right.

        Switching sides mid-typing commits the in-flight value before
        flipping the target so partial input isn't lost.
        """
        if (side == 'LEFT') == self._place_on_front:
            target = hb_placement.TypingTarget.OFFSET_X
        else:
            target = hb_placement.TypingTarget.OFFSET_RIGHT

        if self.placement_state == hb_placement.PlacementState.TYPING:
            if self.typed_value:
                # Commit the current side's value, then keep typing on
                # the new side (apply_typed_value calls stop_typing,
                # which on_typed_value_changed expects we re-enter).
                self.apply_typed_value()
            self.placement_state = hb_placement.PlacementState.TYPING
            self.typed_value = ""
            self.typing_target = target
        else:
            self.start_typing(target)

        self._update_header(context)

    def _reposition_with_offsets(self, context):
        """Place the cage using the stored gap and the active offsets.

        Each offset pins the corresponding cabinet edge: left_offset
        anchors the cabinet's left edge to gap_left + offset; right_offset
        anchors the cabinet's right edge to gap_right - offset. With both
        set, both edges are pinned and the cabinet width is derived.

        In fill mode without both offsets, the cabinet fills whatever the
        offset leaves of the gap (one edge pinned, the other at the gap
        boundary). With a typed width, the cabinet keeps its width and
        slides so the pinned edge is at the offset position - this is
        what avoids the "jump to gap_left when right-typing" behavior of
        a naive shrink-from-left implementation.
        """
        wall = self._gap_wall
        if wall is None or self._preview_cage is None:
            return

        cage_obj = self._preview_cage.obj
        try:
            wall_geo = hb_types.GeoNodeWall(wall)
            wall_thickness = wall_geo.get_input('Thickness')
        except Exception:
            wall_thickness = 0.0

        full_left = self._gap_left_boundary
        full_right = self._gap_right_boundary
        has_left = self._left_offset is not None
        has_right = self._right_offset is not None
        min_w = units.inch(1.0)

        if has_left and has_right:
            cab_left = full_left + self._left_offset
            cab_right = full_right - self._right_offset
            cabinet_width = max(cab_right - cab_left, min_w)
            placement_x = cab_left
        elif has_left:
            placement_x = full_left + self._left_offset
            available = max(full_right - placement_x, min_w)
            if self._fill_mode:
                cabinet_width = available
            else:
                cabinet_width = max(min(self._cabinet_width, available), min_w)
        else:  # has_right
            cab_right = full_right - self._right_offset
            available = max(cab_right - full_left, min_w)
            if self._fill_mode:
                cabinet_width = available
                placement_x = full_left
            else:
                cabinet_width = max(min(self._cabinet_width, available), min_w)
                placement_x = cab_right - cabinet_width

        # Resize the cage. _apply_width is the right hook in fill mode
        # (it preserves _fill_mode=True). In non-fill mode we update
        # cage geometry inline so we don't trip _apply_width's typed-
        # width re-position path - we're already positioning here.
        if self._fill_mode:
            self._apply_width(cabinet_width, fill_mode=True)
        elif abs(cabinet_width - self._cabinet_width) > 1e-5:
            self._cabinet_width = cabinet_width
            if self._auto_bay_qty:
                new_qty = _auto_bay_qty(cabinet_width)
                if new_qty != self.bay_qty:
                    self.bay_qty = new_qty
            self._update_cage()

        if self._place_on_front:
            cage_obj.location.x = placement_x
            cage_obj.location.y = 0
            cage_obj.rotation_euler = (0, 0, 0)
        else:
            cage_obj.location.x = placement_x + cabinet_width
            cage_obj.location.y = wall_thickness
            cage_obj.rotation_euler = (0, 0, math.pi)

        self._placement_dim_specs = self._build_dim_specs_on_wall(
            context, wall, wall_thickness,
            self._gap_left_boundary, self._gap_right_boundary,
            placement_x, cabinet_width,
        )
        if context.area is not None:
            context.area.tag_redraw()

    # ---------------- placement dimensions ----------------

    def _build_dim_specs_on_wall(self, context, wall, wall_thickness,
                                 gap_start, gap_end,
                                 placement_x, cabinet_width):
        """Build placement-dim specs for the wall case.

        Coordinates are wall-local (cage is wall-parented); the wall
        matrix maps each endpoint into world space for the drawer.
        Total-width dim sits 4" above the cabinet top; left/right
        offset dims sit 8" above to keep them clear of the total.
        """
        cage_obj = self._preview_cage.obj
        cabinet_height = self._preview_cage.get_input('Dim Z')
        z_top = cage_obj.location.z + cabinet_height
        z_total = z_top + units.inch(4.0)
        z_offset = z_top + units.inch(8.0)

        # Inset toward the room so the dim line is visible from a
        # typical 3D camera angle (otherwise it sits flush with the
        # wall surface and z-fights).
        if self._place_on_front:
            y_dim = -units.inch(2.0)
        else:
            y_dim = wall_thickness + units.inch(2.0)

        wm = wall.matrix_world
        unit_settings = context.scene.unit_settings
        specs = []

        # Total width - tinted green whenever a snap is active so the
        # user has a clear "this is locked" signal. Either gap snap
        # or center snap (over a window) qualifies. Offset dims go
        # green only for CENTER gap-snap (where their equality IS
        # the snap) and for window snap (the L/R distances are the
        # geometric balance the snap is producing).
        snap_green = (0.30, 0.95, 0.40, 1.0)
        any_snap = self._gap_snap or self._center_snap_state
        total_color = snap_green if any_snap else None
        balanced = (self._gap_snap == 'CENTER') or bool(self._center_snap_state)
        offset_color = snap_green if balanced else None
        s = wm @ Vector((placement_x, y_dim, z_total))
        e = wm @ Vector((placement_x + cabinet_width, y_dim, z_total))
        specs.append(hb_placement.PlacementDimSpec(
            s, e,
            units.unit_to_string(unit_settings, cabinet_width),
            total_color,
        ))

        # Left offset (only if there's room worth annotating)
        left_offset = placement_x - gap_start
        if left_offset > units.inch(0.5):
            s = wm @ Vector((gap_start, y_dim, z_offset))
            e = wm @ Vector((placement_x, y_dim, z_offset))
            specs.append(hb_placement.PlacementDimSpec(
                s, e, units.unit_to_string(unit_settings, left_offset),
                offset_color,
            ))

        # Right offset
        right_offset = gap_end - (placement_x + cabinet_width)
        if right_offset > units.inch(0.5):
            s = wm @ Vector((placement_x + cabinet_width, y_dim, z_offset))
            e = wm @ Vector((gap_end, y_dim, z_offset))
            specs.append(hb_placement.PlacementDimSpec(
                s, e, units.unit_to_string(unit_settings, right_offset),
                offset_color,
            ))

        return specs

    def _build_dim_specs_free(self, context):
        """Build placement-dim specs for off-wall placement.

        Off-wall there's no gap to annotate - just the total width
        above the cabinet. Tinted green when cabinet-to-cabinet snap
        is active, matching the wall corner / center-snap convention.
        """
        cage_obj = self._preview_cage.obj
        cabinet_height = self._preview_cage.get_input('Dim Z')
        cabinet_width = self._cabinet_width
        z = cabinet_height + units.inch(4.0)

        s = cage_obj.matrix_world @ Vector((0, 0, z))
        e = cage_obj.matrix_world @ Vector((cabinet_width, 0, z))
        snap_color = (
            (0.30, 0.95, 0.40, 1.0) if self._cabinet_snap_side else None
        )
        return [hb_placement.PlacementDimSpec(
            s, e,
            units.unit_to_string(context.scene.unit_settings, cabinet_width),
            snap_color,
        )]

    # ---------------- finalize / cancel ----------------

    def _finalize(self, context):
        """Commit: capture cage transform, delete cage, build real cabinet."""
        self.remove_placement_dim_handler()
        cage_obj = self._preview_cage.obj
        captured_parent = cage_obj.parent
        captured_world = cage_obj.matrix_world.copy()
        captured_local_loc = cage_obj.location.copy()
        captured_local_rot = cage_obj.rotation_euler.copy()
        captured_width = self._cabinet_width
        captured_bay_qty = self.bay_qty

        self._delete_preview()

        cls = types_face_frame.get_cabinet_class(self.cabinet_name)
        try:
            cabinet = cls()
            cabinet.create(self.cabinet_name, bay_qty=captured_bay_qty)
        except Exception as e:
            self.report({'ERROR'}, f"Cabinet creation failed: {e}")
            hb_placement.clear_header_text(context)
            return {'CANCELLED'}

        cab_obj = cabinet.obj

        if captured_parent is not None:
            cab_obj.parent = captured_parent
            cab_obj.matrix_parent_inverse.identity()
            cab_obj.location = captured_local_loc
            cab_obj.rotation_euler = captured_local_rot
        else:
            cab_obj.matrix_world = captured_world

        # Resize to match cage width via the property update callback
        cab_props = cab_obj.face_frame_cabinet
        cab_props.width = captured_width

        # Auto-apply a sensible default bay configuration so cabinets
        # come in populated instead of empty. All bays in a multi-bay
        # cabinet receive the same config; the user changes any of
        # them via the right-click 'Change Bay' menu after.
        bays = sorted(
            [c for c in cab_obj.children if c.get(types_face_frame.TAG_BAY_CAGE)],
            key=lambda c: c.get('hb_bay_index', 0),
        )
        if bays:
            sample_width = bays[0].face_frame_bay.width
            default_config = bay_presets.default_bay_config(
                self.cabinet_name, sample_width
            )
            if default_config is not None:
                # Each apply_bay_preset already suspends internally; nesting
                # the whole loop folds all 8 bays' recalcs (including the
                # per-bay explicit recalc inside apply_bay_preset) into a
                # single recalc at the outer resume.
                with types_face_frame.suspend_recalc():
                    for bay_obj in bays:
                        ops_cabinet.apply_bay_preset(bay_obj, default_config)

        # Auto-merge with an abutting compatible neighbor on the wall.
        # When a merge happens, cab_obj is absorbed and deleted; the
        # neighbor is the survivor that selection should target.
        merged_into = _try_auto_merge_with_neighbor(context, cab_obj)
        selection_target = merged_into if merged_into is not None else cab_obj

        # Align toe-kick setback when this cabinet abuts a BASE/TALL of
        # the opposite type - the deeper one's kick face is brought
        # forward by the depth difference so the run reads as continuous.
        _align_base_tall_toe_kick(selection_target)

        # Active selection (on the survivor)
        for o in context.selected_objects:
            o.select_set(False)
        selection_target.select_set(True)
        context.view_layer.objects.active = selection_target

        try:
            bpy.ops.hb_face_frame.toggle_mode(search_obj_name=selection_target.name)
            selection_target.select_set(True)
            context.view_layer.objects.active = selection_target
        except RuntimeError:
            pass

        # Detect an adjacent perpendicular neighbor at this wall corner.
        # When found, pop the void-amount dialog so the user can configure
        # how the cabinets meet (depth-match vs. fixed void, stile widths).
        # Skipped silently when nothing qualifies - placement just finishes.
        corner_match = _detect_blind_corner_neighbor(selection_target)
        if corner_match is not None:
            neighbor, blind_side = corner_match
            try:
                bpy.ops.hb_face_frame.set_blind_corner_void_amount(
                    'INVOKE_DEFAULT',
                    blind_cabinet_name=neighbor.name,
                    current_cabinet_name=selection_target.name,
                    blind_side=blind_side,
                )
            except RuntimeError:
                pass

        hb_placement.clear_header_text(context)
        bay_label = f"{captured_bay_qty} bay" + ("" if captured_bay_qty == 1 else "s")
        self.report({'INFO'},
                    f"Placed {self.cabinet_name} ({bay_label}, "
                    f"{captured_width * 39.37008:.1f}\" wide)")
        return {'FINISHED'}

    def _cancel(self, context):
        self.remove_placement_dim_handler()
        self._delete_preview()
        hb_placement.clear_header_text(context)
        return {'CANCELLED'}

    def _delete_preview(self):
        if self._preview_cage is None:
            return
        try:
            self._delete_object_and_children(self._preview_cage.obj)
        except Exception:
            try:
                bpy.data.objects.remove(self._preview_cage.obj, do_unlink=True)
            except Exception:
                pass
        self._preview_cage = None
        self._array_modifier = None


# ---------------------------------------------------------------------------
# Appliance placement
# ---------------------------------------------------------------------------
# Mirrors the cabinet placement modal but with a fixed-width single
# cage. No bay quantity arrows, no fill mode, no typed width entry.
# Wall snap, gap-edge snap, and cabinet-to-cabinet snap behave the
# same as the cabinet flow.
class hb_face_frame_OT_place_appliance(bpy.types.Operator,
                                       hb_placement.PlacementMixin):
    """Modal: cursor drags an appliance preview cage, click to commit."""
    bl_idname = "hb_face_frame.place_appliance"
    bl_label = "Place Appliance"
    bl_description = (
        "Place an appliance on a wall or on the floor. "
        "Left/Right arrows set gap offset, Esc cancels."
    )
    bl_options = {'REGISTER', 'UNDO'}

    appliance_name: bpy.props.StringProperty(
        name="Appliance Name",
        description="Catalog name of the appliance to place",
        default="",
    )  # type: ignore

    _preview_cage = None
    _appliance_width: float = 0.0
    _appliance_height: float = 0.0
    _appliance_depth: float = 0.0
    _place_on_front: bool = True
    _gap_snap = None
    _center_snap_state = None       # None | 'WINDOW' | 'BAY' | 'PRODUCT'
    _cabinet_snap_side = None

    # Gap-relative offset state - same model as the cabinet operator.
    _left_offset: float = None
    _right_offset: float = None
    _gap_left_boundary: float = 0.0
    _gap_right_boundary: float = 0.0
    _gap_wall = None
    _position_locked: bool = False

    # ---------------- invoke / modal ----------------

    def invoke(self, context, event):
        if not self.appliance_name:
            self.report({'WARNING'}, "No appliance name supplied")
            return {'CANCELLED'}
        if self.appliance_name not in types_face_frame.APPLIANCE_NAME_DISPATCH:
            self.report({'WARNING'},
                        f"Unknown appliance: {self.appliance_name}")
            return {'CANCELLED'}

        scene_props = context.scene.hb_face_frame
        w, h, d = _appliance_dimensions(scene_props, self.appliance_name)
        self._appliance_width = w
        self._appliance_height = h
        self._appliance_depth = d
        self._place_on_front = True
        self._gap_snap = None
        self._center_snap_state = None
        self._cabinet_snap_side = None

        try:
            self._create_preview_cage(context)
        except Exception as e:
            self.report({'ERROR'}, f"Preview creation failed: {e}")
            return {'CANCELLED'}

        cage_obj = self._preview_cage.obj
        cage_obj.location = context.scene.cursor.location.copy()
        # Override Z for appliances that mount at a fixed height
        # (range hood at the upper-cabinet base). Other appliances
        # follow the cursor Z so the user can rough in shelves /
        # islands at any height.
        z_override = _appliance_z_location(scene_props, self.appliance_name)
        if z_override is not None:
            cage_obj.location.z = z_override

        self.init_placement(context)
        if self.region is None:
            self._delete_preview()
            self.report({'WARNING'}, "No 3D viewport available")
            return {'CANCELLED'}
        self.register_placement_object(cage_obj)
        self.add_placement_dim_handler(context)

        context.window_manager.modal_handler_add(self)
        self._update_header(context)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if self._preview_cage is None:
            return self._cancel(context)

        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}

        # Route typing events through the mixin first so it can own
        # ESC (cancel typing) and ENTER (commit) - otherwise our own
        # ESC would eat the event and cancel the whole modal.
        if self.placement_state == hb_placement.PlacementState.TYPING:
            if self.handle_typing_event(event):
                self._update_header(context)
                return {'RUNNING_MODAL'}

        if event.type in {'ESC', 'RIGHTMOUSE'} and event.value == 'PRESS':
            return self._cancel(context)

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            return self._finalize(context)

        # Left/right arrows: type a gap-edge offset. Inert off-wall.
        if event.type == 'LEFT_ARROW' and event.value == 'PRESS':
            if self._gap_wall is not None:
                self._handle_offset_arrow(context, side='LEFT')
            return {'RUNNING_MODAL'}

        if event.type == 'RIGHT_ARROW' and event.value == 'PRESS':
            if self._gap_wall is not None:
                self._handle_offset_arrow(context, side='RIGHT')
            return {'RUNNING_MODAL'}

        if event.type == 'MOUSEMOVE':
            # Freeze positioning while typing an offset - the live
            # preview from on_typed_value_changed drives the cage and
            # a re-snap here would overwrite it.
            if (self.placement_state == hb_placement.PlacementState.TYPING
                    and self.typing_target in (
                        hb_placement.TypingTarget.OFFSET_X,
                        hb_placement.TypingTarget.OFFSET_RIGHT)):
                return {'RUNNING_MODAL'}

            cage_obj = self._preview_cage.obj
            cage_obj.hide_set(True)
            try:
                self.update_snap(context, event)
            finally:
                cage_obj.hide_set(False)
            self._position_from_hit(context)

        return {'RUNNING_MODAL'}

    # ---------------- preview cage ----------------

    def _create_preview_cage(self, context):
        cage = hb_types.GeoNodeCage()
        cage.create('AppliancePlacementPreview')
        cage.set_input('Dim X', self._appliance_width)
        cage.set_input('Dim Y', self._appliance_depth)
        cage.set_input('Dim Z', self._appliance_height)
        cage.set_input('Mirror Y', True)
        cage.obj.display_type = 'WIRE'
        cage.obj.show_in_front = True
        cage.obj['HB_CURRENT_DRAW_OBJ'] = True
        self._preview_cage = cage

    def _update_header(self, context):
        side = "front" if self._place_on_front else "back"
        width_in = self._appliance_width * 39.37008

        if self.placement_state == hb_placement.PlacementState.TYPING:
            typed = self.get_typed_display_string()
            label = {
                hb_placement.TypingTarget.OFFSET_X: "Offset (←)",
                hb_placement.TypingTarget.OFFSET_RIGHT: "Offset (→)",
            }.get(self.typing_target, "Value")
            hb_placement.draw_header_text(
                context,
                f"{self.appliance_name}  -  {label}: {typed}  -  "
                "Enter: apply   ←/→: switch offset   "
                "Esc: cancel typing   Backspace: delete"
            )
            return

        offset_hint = ""
        if self._left_offset is not None:
            offset_hint += (
                f"  L:{units.unit_to_string(context.scene.unit_settings, self._left_offset)}"
            )
        if self._right_offset is not None:
            offset_hint += (
                f"  R:{units.unit_to_string(context.scene.unit_settings, self._right_offset)}"
            )
        hb_placement.draw_header_text(
            context,
            f"{self.appliance_name}  -  width: {width_in:.1f}\""
            f"  -  side: {side}{offset_hint}  -  "
            "←/→: gap offset   Click: place   Esc: cancel"
        )

    # ---------------- typed-input handlers ----------------

    def get_default_typing_target(self):
        # Appliances don't have a typed width; arrows are the only
        # way to enter typing mode and they set the target explicitly.
        return hb_placement.TypingTarget.OFFSET_X

    def on_typed_value_changed(self):
        """Live preview offset typing - apply, render, restore."""
        if not self.typed_value:
            return
        parsed = self.parse_typed_distance()
        if parsed is None or parsed < 0:
            return
        if self._gap_wall is None:
            return
        if self.typing_target == hb_placement.TypingTarget.OFFSET_X:
            old_val = self._left_offset
            self._left_offset = parsed
            self._reposition_with_offsets(bpy.context)
            self._left_offset = old_val
        elif self.typing_target == hb_placement.TypingTarget.OFFSET_RIGHT:
            old_val = self._right_offset
            self._right_offset = parsed
            self._reposition_with_offsets(bpy.context)
            self._right_offset = old_val

    def apply_typed_value(self):
        """Commit offset on Enter and lock the position."""
        parsed = self.parse_typed_distance()
        if (parsed is not None and parsed >= 0
                and self._gap_wall is not None):
            if self.typing_target == hb_placement.TypingTarget.OFFSET_X:
                self._left_offset = parsed
                self._gap_snap = None
                self._position_locked = True
                self._reposition_with_offsets(bpy.context)
            elif self.typing_target == hb_placement.TypingTarget.OFFSET_RIGHT:
                self._right_offset = parsed
                self._gap_snap = None
                self._position_locked = True
                self._reposition_with_offsets(bpy.context)
        self.stop_typing()

    # ---------------- offset-driven positioning ----------------

    def _handle_offset_arrow(self, context, side):
        """Start (or switch) typing a gap-edge offset.

        Front-side: LEFT arrow types the left offset; back-side flips
        the meaning since the wall is rotated 180 from the user's view.
        """
        if (side == 'LEFT') == self._place_on_front:
            target = hb_placement.TypingTarget.OFFSET_X
        else:
            target = hb_placement.TypingTarget.OFFSET_RIGHT

        if self.placement_state == hb_placement.PlacementState.TYPING:
            if self.typed_value:
                self.apply_typed_value()
            self.placement_state = hb_placement.PlacementState.TYPING
            self.typed_value = ""
            self.typing_target = target
        else:
            self.start_typing(target)

        self._update_header(context)

    def _reposition_with_offsets(self, context):
        """Place the cage using stored gap + active offsets.

        Same edge-anchoring semantics as the cabinet operator: each
        offset pins the corresponding edge. Appliances have a fixed
        width, so the cabinet slides rather than shrinks unless the
        offset-adjusted gap is too narrow to fit it.
        """
        wall = self._gap_wall
        if wall is None or self._preview_cage is None:
            return

        cage_obj = self._preview_cage.obj
        try:
            wall_geo = hb_types.GeoNodeWall(wall)
            wall_thickness = wall_geo.get_input('Thickness')
        except Exception:
            wall_thickness = 0.0

        full_left = self._gap_left_boundary
        full_right = self._gap_right_boundary
        has_left = self._left_offset is not None
        has_right = self._right_offset is not None
        min_w = units.inch(1.0)

        if has_left and has_right:
            cab_left = full_left + self._left_offset
            cab_right = full_right - self._right_offset
            cabinet_width = max(cab_right - cab_left, min_w)
            placement_x = cab_left
        elif has_left:
            placement_x = full_left + self._left_offset
            available = max(full_right - placement_x, min_w)
            cabinet_width = max(min(self._appliance_width, available), min_w)
        else:  # has_right
            cab_right = full_right - self._right_offset
            available = max(cab_right - full_left, min_w)
            cabinet_width = max(min(self._appliance_width, available), min_w)
            placement_x = cab_right - cabinet_width

        if self._place_on_front:
            cage_obj.location.x = placement_x
            cage_obj.location.y = 0
            cage_obj.rotation_euler = (0, 0, 0)
        else:
            cage_obj.location.x = placement_x + cabinet_width
            cage_obj.location.y = wall_thickness
            cage_obj.rotation_euler = (0, 0, math.pi)

        self._placement_dim_specs = self._build_dim_specs_on_wall(
            context, wall, wall_thickness,
            self._gap_left_boundary, self._gap_right_boundary,
            placement_x, cabinet_width,
        )
        if context.area is not None:
            context.area.tag_redraw()

    # ---------------- positioning ----------------

    def _update_place_on_front(self, context, wall, local_hit_y, wall_thickness):
        """Front/back side decision with hysteresis. Mirrors the cabinet
        operator's logic - a 1" band keeps the side stable while the
        cursor sits near the wall surface.
        """
        wall_center_y = wall_thickness / 2.0
        region = self.region
        rv3d = region.data if region is not None else None
        if rv3d is None:
            return

        view_z = rv3d.view_matrix[2][2]
        is_plan_view = abs(view_z) > _PLAN_VIEW_THRESHOLD
        if is_plan_view:
            view_origin = view3d_utils.region_2d_to_origin_3d(
                region, rv3d, self.mouse_pos)
            view_dir = view3d_utils.region_2d_to_vector_3d(
                region, rv3d, self.mouse_pos)
            floor_point = intersect_line_plane(
                view_origin,
                view_origin + view_dir * 10000,
                Vector((0, 0, 0)),
                Vector((0, 0, 1)),
            )
            cursor_y = (local_hit_y if floor_point is None
                        else (wall.matrix_world.inverted() @ floor_point).y)
        else:
            cursor_y = local_hit_y

        if cursor_y < wall_center_y - _FRONT_BACK_HYSTERESIS:
            self._place_on_front = True
        elif cursor_y > wall_center_y + _FRONT_BACK_HYSTERESIS:
            self._place_on_front = False

    def _position_from_hit(self, context):
        if self.hit_location is None:
            return
        wall = _detect_wall(self, context)
        if wall is not None:
            self._position_on_wall(context, wall)
        else:
            self._position_free(context)

    def _position_on_wall(self, context, wall):
        cage_obj = self._preview_cage.obj
        try:
            wall_geo = hb_types.GeoNodeWall(wall)
            wall_thickness = wall_geo.get_input('Thickness')
        except Exception:
            wall_thickness = 0.0

        if cage_obj.parent is not wall:
            cage_obj.parent = wall
            cage_obj.matrix_parent_inverse.identity()

        local_hit = wall.matrix_world.inverted() @ self.hit_location
        cursor_x = local_hit.x

        self._update_place_on_front(context, wall, local_hit.y, wall_thickness)

        try:
            result = self.find_placement_gap_by_side(
                wall, cursor_x, self._appliance_width,
                self._place_on_front, wall_thickness,
                object_z_start=cage_obj.location.z,
                object_height=self._appliance_height,
                object_depth=self._appliance_depth,
                exclude_obj=cage_obj,
            )
        except Exception:
            result = (None, None, None)
        gap_start, gap_end, snap_x = result
        if gap_start is None:
            gap_start = 0.0
            gap_end = wall_geo.get_input('Length')
            snap_x = max(gap_start, cursor_x - self._appliance_width / 2)

        gap_width = max(gap_end - gap_start, units.inch(1.0))
        cabinet_width = min(self._appliance_width, gap_width)

        # Snapshot the gap so offset typing can re-derive placement
        # without re-detecting the gap.
        self._gap_left_boundary = gap_start
        self._gap_right_boundary = gap_end
        self._gap_wall = wall

        # Offset override: typed offsets bypass cursor-based snap.
        if self._left_offset is not None or self._right_offset is not None:
            self._gap_snap = None
            self._reposition_with_offsets(context)
            return

        # Same gap-edge / center snap thresholds as cabinet placement.
        engage_corner = max(cabinet_width / 2, units.inch(6.0))
        release_corner = engage_corner + units.inch(1.0)
        engage_center = units.inch(4.0)
        release_center = engage_center + units.inch(1.0)
        left_thresh = release_corner if self._gap_snap == 'LEFT' else engage_corner
        right_thresh = release_corner if self._gap_snap == 'RIGHT' else engage_corner
        center_thresh = release_center if self._gap_snap == 'CENTER' else engage_center

        near_left = (cursor_x - gap_start) < left_thresh
        near_right = (gap_end - cursor_x) < right_thresh
        gap_center = (gap_start + gap_end) / 2
        near_center = (
            abs(cursor_x - gap_center) < center_thresh
            and cabinet_width < gap_width
        )

        if near_left and near_right:
            self._gap_snap = ('LEFT' if (cursor_x - gap_start) <
                              (gap_end - cursor_x) else 'RIGHT')
        elif near_left:
            self._gap_snap = 'LEFT'
        elif near_right:
            self._gap_snap = 'RIGHT'
        elif near_center:
            self._gap_snap = 'CENTER'
        else:
            self._gap_snap = None

        # Center snap. Range Hood mounts above an existing product so
        # it looks for a bay (most-specific) or any cabinet/appliance
        # (PRODUCT). Other appliances center on a window when the
        # cursor is over one.
        if self.appliance_name == "Range Hood":
            kinds = {'BAY', 'PRODUCT'}
        else:
            kinds = {'WINDOW'}

        cab_z_start = cage_obj.location.z
        cab_z_end = cab_z_start + self._appliance_height
        cs_x, cs_kind, _cs_w = _find_center_snap(
            self.hit_object, wall, kinds,
            (cab_z_start, cab_z_end),
        )

        if cs_kind is not None:
            self._center_snap_state = cs_kind
            self._gap_snap = None
            ideal_x = cs_x - cabinet_width / 2
            placement_x = max(gap_start,
                              min(ideal_x, gap_end - cabinet_width))
        else:
            self._center_snap_state = None
            if self._gap_snap == 'LEFT':
                placement_x = gap_start
            elif self._gap_snap == 'RIGHT':
                placement_x = gap_end - cabinet_width
            elif self._gap_snap == 'CENTER':
                placement_x = gap_start + (gap_width - cabinet_width) / 2
            else:
                placement_x = max(gap_start,
                                  min(snap_x, gap_end - cabinet_width))

        if self._place_on_front:
            cage_obj.location.x = placement_x
            cage_obj.location.y = 0
            cage_obj.rotation_euler = (0, 0, 0)
        else:
            cage_obj.location.x = placement_x + cabinet_width
            cage_obj.location.y = wall_thickness
            cage_obj.rotation_euler = (0, 0, math.pi)

        self._placement_dim_specs = self._build_dim_specs_on_wall(
            context, wall, wall_thickness,
            gap_start, gap_end, placement_x, cabinet_width,
        )
        if context.area is not None:
            context.area.tag_redraw()

    def _position_free(self, context):
        # Going off-wall releases any offset lock (gap reference is gone).
        if self._gap_wall is not None or self._position_locked:
            self._gap_wall = None
            self._left_offset = None
            self._right_offset = None
            self._position_locked = False
        # Center snap is wall-bound; clear it whenever we go off-wall.
        self._center_snap_state = None

        cage_obj = self._preview_cage.obj
        snap_target, snap_side = self.detect_cabinet_snap_target(
            self.hit_object, self.hit_location)
        if snap_target is cage_obj:
            snap_target = None
            snap_side = None
        self._cabinet_snap_side = snap_side

        if cage_obj.parent is not None:
            world = cage_obj.matrix_world.copy()
            cage_obj.parent = None
            cage_obj.matrix_world = world

        snap_result = None
        if snap_target is not None and snap_side is not None:
            if _is_corner_cabinet(snap_target) and snap_side == 'LEFT':
                snap_result = _compute_corner_left_snap_transform(
                    snap_target, self._appliance_width)
            else:
                snap_result = self.compute_cabinet_snap_transform(
                    snap_target, snap_side, self._appliance_width)

        # Appliances that mount at a fixed height (range hood) keep
        # their configured Z when off-wall instead of dropping to the
        # cursor / snap-target Z; that anchor is what makes the hood
        # read as the bay above the range.
        scene_props = context.scene.hb_face_frame
        z_override = _appliance_z_location(scene_props, self.appliance_name)

        if snap_result is not None:
            new_loc, new_rot = snap_result
            cage_obj.location = new_loc
            cage_obj.rotation_euler = new_rot
            if z_override is not None:
                cage_obj.location.z = z_override
            else:
                cage_obj.location.z = snap_target.location.z
        else:
            self._cabinet_snap_side = None
            cage_obj.location = self.hit_location.copy()
            if z_override is not None:
                cage_obj.location.z = z_override
            cage_obj.rotation_euler = (0, 0, 0)

        self._placement_dim_specs = self._build_dim_specs_free(context)
        if context.area is not None:
            context.area.tag_redraw()

    def _build_dim_specs_on_wall(self, context, wall, wall_thickness,
                                 gap_start, gap_end,
                                 placement_x, cabinet_width):
        cage_obj = self._preview_cage.obj
        z_top = cage_obj.location.z + self._appliance_height
        z_total = z_top + units.inch(4.0)
        z_offset = z_top + units.inch(8.0)
        if self._place_on_front:
            y_dim = -units.inch(2.0)
        else:
            y_dim = wall_thickness + units.inch(2.0)

        wm = wall.matrix_world
        unit_settings = context.scene.unit_settings
        specs = []
        snap_green = (0.30, 0.95, 0.40, 1.0)
        # Either gap snap or center snap (window / bay / product)
        # tints the total dim. Offset dims tint when the snap is the
        # one that balances them - center-of-gap or any center snap.
        any_snap = self._gap_snap or self._center_snap_state
        balanced = (self._gap_snap == 'CENTER') or bool(self._center_snap_state)
        total_color = snap_green if any_snap else None
        offset_color = snap_green if balanced else None

        s = wm @ Vector((placement_x, y_dim, z_total))
        e = wm @ Vector((placement_x + cabinet_width, y_dim, z_total))
        specs.append(hb_placement.PlacementDimSpec(
            s, e, units.unit_to_string(unit_settings, cabinet_width),
            total_color,
        ))

        left_offset = placement_x - gap_start
        if left_offset > units.inch(0.5):
            s = wm @ Vector((gap_start, y_dim, z_offset))
            e = wm @ Vector((placement_x, y_dim, z_offset))
            specs.append(hb_placement.PlacementDimSpec(
                s, e, units.unit_to_string(unit_settings, left_offset),
                offset_color,
            ))

        right_offset = gap_end - (placement_x + cabinet_width)
        if right_offset > units.inch(0.5):
            s = wm @ Vector((placement_x + cabinet_width, y_dim, z_offset))
            e = wm @ Vector((gap_end, y_dim, z_offset))
            specs.append(hb_placement.PlacementDimSpec(
                s, e, units.unit_to_string(unit_settings, right_offset),
                offset_color,
            ))
        return specs

    def _build_dim_specs_free(self, context):
        cage_obj = self._preview_cage.obj
        z = self._appliance_height + units.inch(4.0)
        s = cage_obj.matrix_world @ Vector((0, 0, z))
        e = cage_obj.matrix_world @ Vector((self._appliance_width, 0, z))
        snap_color = (
            (0.30, 0.95, 0.40, 1.0) if self._cabinet_snap_side else None
        )
        return [hb_placement.PlacementDimSpec(
            s, e,
            units.unit_to_string(context.scene.unit_settings,
                                 self._appliance_width),
            snap_color,
        )]

    # ---------------- finalize / cancel ----------------

    def _finalize(self, context):
        self.remove_placement_dim_handler()
        cage_obj = self._preview_cage.obj
        captured_parent = cage_obj.parent
        captured_world = cage_obj.matrix_world.copy()
        captured_local_loc = cage_obj.location.copy()
        captured_local_rot = cage_obj.rotation_euler.copy()

        self._delete_preview()

        cls = types_face_frame.APPLIANCE_NAME_DISPATCH.get(self.appliance_name)
        if cls is None:
            self.report({'ERROR'}, f"Unknown appliance: {self.appliance_name}")
            hb_placement.clear_header_text(context)
            return {'CANCELLED'}
        appliance = cls()
        # Apply preview-resolved dims so the final appliance matches
        # the cage the user just placed.
        appliance.width = self._appliance_width
        appliance.height = self._appliance_height
        appliance.depth = self._appliance_depth
        try:
            appliance.create(self.appliance_name)
        except Exception as e:
            self.report({'ERROR'}, f"Appliance creation failed: {e}")
            hb_placement.clear_header_text(context)
            return {'CANCELLED'}

        app_obj = appliance.obj
        if captured_parent is not None:
            app_obj.parent = captured_parent
            app_obj.matrix_parent_inverse.identity()
            app_obj.location = captured_local_loc
            app_obj.rotation_euler = captured_local_rot
        else:
            app_obj.matrix_world = captured_world

        for o in context.selected_objects:
            o.select_set(False)
        app_obj.select_set(True)
        context.view_layer.objects.active = app_obj

        try:
            bpy.ops.hb_face_frame.toggle_mode(search_obj_name=app_obj.name)
            app_obj.select_set(True)
            context.view_layer.objects.active = app_obj
        except RuntimeError:
            pass

        hb_placement.clear_header_text(context)
        self.report({'INFO'}, f"Placed {self.appliance_name}")
        return {'FINISHED'}

    def _cancel(self, context):
        self.remove_placement_dim_handler()
        self._delete_preview()
        hb_placement.clear_header_text(context)
        return {'CANCELLED'}

    def _delete_preview(self):
        if self._preview_cage is None:
            return
        try:
            self._delete_object_and_children(self._preview_cage.obj)
        except Exception:
            try:
                bpy.data.objects.remove(self._preview_cage.obj, do_unlink=True)
            except Exception:
                pass
        self._preview_cage = None


class hb_face_frame_OT_place_corner_cabinet(bpy.types.Operator,
                                            hb_placement.PlacementMixin):
    """Modal: cursor drags a corner-cabinet preview cage, click to commit.

    Snaps the cabinet to whichever wall corner is closer to the cursor.
    Off-wall, drops at the cursor position with no rotation. Corner
    cabinets don't take a typed width or a bay count - the dimensions
    come from scene corner-size props, and the build is always one
    cabinet at one corner.
    """
    bl_idname = "hb_face_frame.place_corner_cabinet"
    bl_label = "Place Face Frame Corner Cabinet"
    bl_description = (
        "Place a face frame corner cabinet. Snaps to whichever wall "
        "corner is closer to the cursor. Left/Right arrows set gap "
        "offset (disables corner snap). LMB commits, Esc cancels."
    )
    bl_options = {'REGISTER', 'UNDO'}

    cabinet_name: bpy.props.StringProperty(
        name="Cabinet Name",
        description="Corner cabinet type to place",
        default="",
    )  # type: ignore

    # Live state during modal session
    _preview_cage = None
    _cabinet_class = None
    _cabinet_width: float = 0.0
    _cabinet_depth: float = 0.0
    _cabinet_height: float = 0.0
    _corner_side = None  # None | 'LEFT' | 'RIGHT'
    _selected_wall = None

    # Gap-relative offset state. When an offset is active, corner snap
    # is disabled and the cabinet sits in the free (un-rotated) state
    # at gap_left_boundary + left_offset (or right equivalent).
    _left_offset: float = None
    _right_offset: float = None
    _gap_left_boundary: float = 0.0
    _gap_right_boundary: float = 0.0
    _gap_wall = None
    _position_locked: bool = False

    # ---------------- invoke / modal ----------------

    def invoke(self, context, event):
        if not self.cabinet_name:
            self.report({'WARNING'}, "No cabinet name supplied")
            return {'CANCELLED'}
        cls = types_face_frame.get_cabinet_class(self.cabinet_name)
        if cls is None or not issubclass(
                cls, types_face_frame_corner.CornerFaceFrameCabinet):
            self.report({'WARNING'},
                        f"Not a corner cabinet: {self.cabinet_name}")
            return {'CANCELLED'}
        self._cabinet_class = cls

        scene_props = context.scene.hb_face_frame
        if cls.default_cabinet_type == 'UPPER':
            size = scene_props.upper_inside_corner_size
            height = scene_props.upper_cabinet_height
        else:
            size = scene_props.base_inside_corner_size
            height = scene_props.base_cabinet_height
        self._cabinet_width = size
        self._cabinet_depth = size
        self._cabinet_height = height

        try:
            self._create_preview_cage(context)
        except Exception as e:
            self.report({'ERROR'}, f"Preview creation failed: {e}")
            return {'CANCELLED'}

        cage_obj = self._preview_cage.obj
        cursor_loc = context.scene.cursor.location
        cage_obj.location.x = cursor_loc.x
        cage_obj.location.y = cursor_loc.y
        if cls.default_cabinet_type == 'UPPER':
            cage_obj.location.z = scene_props.default_wall_cabinet_location
        else:
            cage_obj.location.z = cursor_loc.z

        self.init_placement(context)
        if self.region is None:
            self._delete_preview()
            self.report({'WARNING'}, "No 3D viewport available")
            return {'CANCELLED'}
        self.register_placement_object(cage_obj)
        self.add_placement_dim_handler(context)

        context.window_manager.modal_handler_add(self)
        self._update_header(context)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if self._preview_cage is None:
            return self._cancel(context)

        # Pass through viewport navigation
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}

        # Route typing events through the mixin first so it owns ESC
        # (cancel typing) and ENTER (commit) without our own ESC
        # handler eating the event.
        if self.placement_state == hb_placement.PlacementState.TYPING:
            if self.handle_typing_event(event):
                self._update_header(context)
                return {'RUNNING_MODAL'}

        if event.type in {'ESC', 'RIGHTMOUSE'} and event.value == 'PRESS':
            return self._cancel(context)

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            return self._finalize(context)

        # Left/right arrows: type a gap-edge offset. Inert off-wall.
        if event.type == 'LEFT_ARROW' and event.value == 'PRESS':
            if self._gap_wall is not None:
                self._handle_offset_arrow(context, side='LEFT')
            return {'RUNNING_MODAL'}

        if event.type == 'RIGHT_ARROW' and event.value == 'PRESS':
            if self._gap_wall is not None:
                self._handle_offset_arrow(context, side='RIGHT')
            return {'RUNNING_MODAL'}

        if event.type == 'MOUSEMOVE':
            # Freeze positioning while typing an offset; live preview
            # comes from on_typed_value_changed.
            if (self.placement_state == hb_placement.PlacementState.TYPING
                    and self.typing_target in (
                        hb_placement.TypingTarget.OFFSET_X,
                        hb_placement.TypingTarget.OFFSET_RIGHT)):
                return {'RUNNING_MODAL'}

            cage_obj = self._preview_cage.obj
            cage_obj.hide_set(True)
            try:
                self.update_snap(context, event)
            finally:
                cage_obj.hide_set(False)
            self._position_from_hit(context)

        return {'RUNNING_MODAL'}

    # ---------------- preview / positioning ----------------

    def _create_preview_cage(self, context):
        """Wireframe square cage matching the corner cabinet's outer
        bounding square. Mirror Y so the cage extends -Y from origin
        (matches the cabinet's back-at-origin convention).

        HB_CURRENT_DRAW_OBJ excludes the cage from hb_snap raycasts.
        """
        cage = hb_types.GeoNodeCage()
        cage.create('FaceFrameCornerPlacementPreview')
        cage.set_input('Dim X', self._cabinet_width)
        cage.set_input('Dim Y', self._cabinet_depth)
        cage.set_input('Dim Z', self._cabinet_height)
        cage.set_input('Mirror Y', True)
        cage.obj.display_type = 'WIRE'
        cage.obj.show_in_front = True
        cage.obj['HB_CURRENT_DRAW_OBJ'] = True
        self._preview_cage = cage

    def _position_from_hit(self, context):
        if self.hit_location is None:
            return
        wall = _detect_wall(self, context)
        if wall is not None:
            self._position_on_wall(context, wall)
        else:
            self._position_free(context)

    def _position_on_wall(self, context, wall):
        """Cursor-follow placement along the wall, snap to corners.

        Uses find_placement_gap_by_side for collision detection so
        existing cabinets (and adjacent-wall intrusions) carve the
        gap we work in. Corner snap engages only when the cursor is
        within engage_tol of a wall end AND that end is part of the
        gap (no other cabinet blocking it). Hysteresis on release.

        Corner snap states:
          LEFT  - location.x=0,           rotation_euler.z=0
          RIGHT - location.x=wall_length, rotation_euler.z=-pi/2
          None  - free along wall, no rotation, clamped to gap
        """
        cage_obj = self._preview_cage.obj
        try:
            wall_geo = hb_types.GeoNodeWall(wall)
            wall_length = wall_geo.get_input('Length')
            wall_thickness = wall_geo.get_input('Thickness')
        except Exception:
            return

        if cage_obj.parent is not wall:
            cage_obj.parent = wall
            cage_obj.matrix_parent_inverse.identity()

        local_hit = wall.matrix_world.inverted() @ self.hit_location
        cursor_x = local_hit.x

        # Collision-aware gap. Corners are always front-side.
        try:
            result = self.find_placement_gap_by_side(
                wall, cursor_x, self._cabinet_width,
                place_on_front=True,
                wall_thickness=wall_thickness,
                object_z_start=cage_obj.location.z,
                object_height=self._cabinet_height,
                object_depth=self._cabinet_depth,
                exclude_obj=cage_obj,
            )
        except Exception:
            result = (None, None, None)
        gap_start, gap_end, snap_x = result
        if gap_start is None:
            gap_start = 0.0
            gap_end = wall_length
            snap_x = max(gap_start, cursor_x - self._cabinet_width / 2)

        # Snapshot the gap so offset typing can re-derive placement
        # without re-detecting the gap.
        self._gap_left_boundary = gap_start
        self._gap_right_boundary = gap_end
        self._gap_wall = wall

        # Offset override: typed offsets bypass corner snap entirely
        # and place the cabinet in the free (un-rotated) state at
        # gap_start + left_offset.
        if self._left_offset is not None or self._right_offset is not None:
            self._corner_side = None
            self._reposition_with_offsets(context)
            return

        # Corner snap detection. Only available when the gap actually
        # reaches that wall end; an existing cabinet (or adjacent-wall
        # intrusion) at a corner removes that corner from the option.
        engage_tol = max(self._cabinet_width / 2, units.inch(6.0))
        release_tol = engage_tol + units.inch(2.0)
        left_thresh = release_tol if self._corner_side == 'LEFT' else engage_tol
        right_thresh = release_tol if self._corner_side == 'RIGHT' else engage_tol
        eps = units.inch(0.1)

        near_left_corner = (cursor_x < left_thresh) and (gap_start <= eps)
        near_right_corner = (
            (cursor_x > wall_length - right_thresh)
            and (gap_end >= wall_length - eps)
        )

        if near_left_corner and near_right_corner:
            self._corner_side = (
                'LEFT' if cursor_x < wall_length / 2 else 'RIGHT'
            )
        elif near_left_corner:
            self._corner_side = 'LEFT'
        elif near_right_corner:
            self._corner_side = 'RIGHT'
        else:
            self._corner_side = None

        # Position based on snap state
        gap_width = max(gap_end - gap_start, units.inch(1.0))
        if self._corner_side == 'LEFT':
            cage_obj.location.x = 0.0
            cage_obj.location.y = 0.0
            cage_obj.rotation_euler = (0, 0, 0)
            placement_x = 0.0
            cabinet_extent = self._cabinet_width
        elif self._corner_side == 'RIGHT':
            cage_obj.location.x = wall_length
            cage_obj.location.y = 0.0
            cage_obj.rotation_euler = (0, 0, math.radians(-90))
            placement_x = wall_length - self._cabinet_depth
            cabinet_extent = self._cabinet_depth
        else:
            # Free along wall: cursor-centered, clamped into the gap.
            cabinet_extent = min(self._cabinet_width, gap_width)
            placement_x = max(
                gap_start, min(snap_x, gap_end - cabinet_extent)
            )
            cage_obj.location.x = placement_x
            cage_obj.location.y = 0.0
            cage_obj.rotation_euler = (0, 0, 0)

        if self._cabinet_class.default_cabinet_type == 'UPPER':
            scene_props = context.scene.hb_face_frame
            cage_obj.location.z = scene_props.default_wall_cabinet_location
        else:
            cage_obj.location.z = 0.0

        self._selected_wall = wall
        self._placement_dim_specs = self._build_dim_specs_on_wall(
            context, wall, wall_length,
            gap_start, gap_end, placement_x, cabinet_extent,
        )
        if context.area is not None:
            context.area.tag_redraw()

    def _position_free(self, context):
        """Drop the cage at the cursor's hit location (no wall snap)."""
        # Going off-wall releases any offset lock (gap reference is gone).
        if self._gap_wall is not None or self._position_locked:
            self._gap_wall = None
            self._left_offset = None
            self._right_offset = None
            self._position_locked = False

        cage_obj = self._preview_cage.obj
        if cage_obj.parent is not None:
            world = cage_obj.matrix_world.copy()
            cage_obj.parent = None
            cage_obj.matrix_world = world
            cage_obj.rotation_euler = (0, 0, 0)
        self._corner_side = None
        self._selected_wall = None

        cage_obj.location.x = self.hit_location.x
        cage_obj.location.y = self.hit_location.y
        if self._cabinet_class.default_cabinet_type != 'UPPER':
            cage_obj.location.z = self.hit_location.z

        self._placement_dim_specs = self._build_dim_specs_free(context)
        if context.area is not None:
            context.area.tag_redraw()

    # ---------------- placement dimensions ----------------

    def _build_dim_specs_on_wall(self, context, wall, wall_length,
                                 gap_start, gap_end,
                                 placement_x, cabinet_extent):
        """Build dim specs for wall placement.

        Corner-snapped: just the total-width spec, green.
        Free along wall: total + L/R offsets from the gap edges
        (offsets shown only when > 0.5"). Mirrors the regular
        cabinet operator's offset-dim convention so the placement
        story is consistent.
        """
        cage_obj = self._preview_cage.obj
        wm = wall.matrix_world
        unit_settings = context.scene.unit_settings

        z_top = cage_obj.location.z + self._cabinet_height
        z_total = z_top + units.inch(4.0)
        z_offset = z_top + units.inch(8.0)
        y_dim = -units.inch(2.0)

        snapped = self._corner_side is not None
        snap_color = (0.30, 0.95, 0.40, 1.0)
        total_color = snap_color if snapped else None
        specs = []

        # Total width
        s = wm @ Vector((placement_x, y_dim, z_total))
        e = wm @ Vector((placement_x + cabinet_extent, y_dim, z_total))
        specs.append(hb_placement.PlacementDimSpec(
            s, e,
            units.unit_to_string(unit_settings, cabinet_extent),
            total_color,
        ))

        if snapped:
            return specs

        # Free placement: show L/R offsets to gap edges
        left_offset = placement_x - gap_start
        if left_offset > units.inch(0.5):
            s = wm @ Vector((gap_start, y_dim, z_offset))
            e = wm @ Vector((placement_x, y_dim, z_offset))
            specs.append(hb_placement.PlacementDimSpec(
                s, e, units.unit_to_string(unit_settings, left_offset),
            ))
        right_offset = gap_end - (placement_x + cabinet_extent)
        if right_offset > units.inch(0.5):
            s = wm @ Vector((placement_x + cabinet_extent, y_dim, z_offset))
            e = wm @ Vector((gap_end, y_dim, z_offset))
            specs.append(hb_placement.PlacementDimSpec(
                s, e, units.unit_to_string(unit_settings, right_offset),
            ))
        return specs

    def _build_dim_specs_free(self, context):
        """Off-wall: a single neutral-color width dim above the cage."""
        cage_obj = self._preview_cage.obj
        z = self._cabinet_height + units.inch(4.0)
        s = cage_obj.matrix_world @ Vector((0, 0, z))
        e = cage_obj.matrix_world @ Vector((self._cabinet_width, 0, z))
        return [hb_placement.PlacementDimSpec(
            s, e,
            units.unit_to_string(
                context.scene.unit_settings, self._cabinet_width),
        )]

    def _update_header(self, context):
        if self.placement_state == hb_placement.PlacementState.TYPING:
            typed = self.get_typed_display_string()
            label = {
                hb_placement.TypingTarget.OFFSET_X: "Offset (←)",
                hb_placement.TypingTarget.OFFSET_RIGHT: "Offset (→)",
            }.get(self.typing_target, "Value")
            hb_placement.draw_header_text(
                context,
                f"{self.cabinet_name}  -  {label}: {typed}  -  "
                "Enter: apply   ←/→: switch offset   "
                "Esc: cancel typing   Backspace: delete"
            )
            return

        offset_hint = ""
        if self._left_offset is not None:
            offset_hint += (
                f"  L:{units.unit_to_string(context.scene.unit_settings, self._left_offset)}"
            )
        if self._right_offset is not None:
            offset_hint += (
                f"  R:{units.unit_to_string(context.scene.unit_settings, self._right_offset)}"
            )
        msg = (f"Place {self.cabinet_name} - move cursor near a wall corner."
               f"{offset_hint}  -  ←/→: gap offset   "
               f"LMB commits, Esc cancels.")
        hb_placement.draw_header_text(context, msg)

    # ---------------- typed-input handlers ----------------

    def get_default_typing_target(self):
        # Corner cabinets have no typed width; arrows enter typing mode
        # and set the target explicitly.
        return hb_placement.TypingTarget.OFFSET_X

    def on_typed_value_changed(self):
        """Live preview offset typing - apply, render, restore."""
        if not self.typed_value:
            return
        parsed = self.parse_typed_distance()
        if parsed is None or parsed < 0:
            return
        if self._gap_wall is None:
            return
        if self.typing_target == hb_placement.TypingTarget.OFFSET_X:
            old_val = self._left_offset
            self._left_offset = parsed
            self._reposition_with_offsets(bpy.context)
            self._left_offset = old_val
        elif self.typing_target == hb_placement.TypingTarget.OFFSET_RIGHT:
            old_val = self._right_offset
            self._right_offset = parsed
            self._reposition_with_offsets(bpy.context)
            self._right_offset = old_val

    def apply_typed_value(self):
        """Commit offset on Enter and lock the position."""
        parsed = self.parse_typed_distance()
        if (parsed is not None and parsed >= 0
                and self._gap_wall is not None):
            if self.typing_target == hb_placement.TypingTarget.OFFSET_X:
                self._left_offset = parsed
                self._corner_side = None
                self._position_locked = True
                self._reposition_with_offsets(bpy.context)
            elif self.typing_target == hb_placement.TypingTarget.OFFSET_RIGHT:
                self._right_offset = parsed
                self._corner_side = None
                self._position_locked = True
                self._reposition_with_offsets(bpy.context)
        self.stop_typing()

    # ---------------- offset-driven positioning ----------------

    def _handle_offset_arrow(self, context, side):
        """Start (or switch) typing a gap-edge offset.

        Corner cabinets are always front-side, so no back-side flip
        is needed - LEFT arrow always means left offset.
        """
        if side == 'LEFT':
            target = hb_placement.TypingTarget.OFFSET_X
        else:
            target = hb_placement.TypingTarget.OFFSET_RIGHT

        if self.placement_state == hb_placement.PlacementState.TYPING:
            if self.typed_value:
                self.apply_typed_value()
            self.placement_state = hb_placement.PlacementState.TYPING
            self.typed_value = ""
            self.typing_target = target
        else:
            self.start_typing(target)

        self._update_header(context)

    def _reposition_with_offsets(self, context):
        """Place the cage in free (un-rotated) state at the offset.

        Corner snap is intentionally bypassed - typing an offset is an
        explicit "I want it here" override. Edge-anchoring matches the
        cabinet/appliance operators: left_offset pins the cabinet's
        left edge, right_offset pins the right edge, both pin both.
        Corner cabinets have a fixed extent so they slide rather than
        shrink unless the offset-adjusted gap is narrower.
        """
        wall = self._gap_wall
        if wall is None or self._preview_cage is None:
            return

        cage_obj = self._preview_cage.obj
        try:
            wall_geo = hb_types.GeoNodeWall(wall)
            wall_length = wall_geo.get_input('Length')
        except Exception:
            wall_length = 0.0

        if cage_obj.parent is not wall:
            cage_obj.parent = wall
            cage_obj.matrix_parent_inverse.identity()

        full_left = self._gap_left_boundary
        full_right = self._gap_right_boundary
        has_left = self._left_offset is not None
        has_right = self._right_offset is not None
        min_w = units.inch(1.0)

        if has_left and has_right:
            cab_left = full_left + self._left_offset
            cab_right = full_right - self._right_offset
            cabinet_extent = max(cab_right - cab_left, min_w)
            placement_x = cab_left
        elif has_left:
            placement_x = full_left + self._left_offset
            available = max(full_right - placement_x, min_w)
            cabinet_extent = max(min(self._cabinet_width, available), min_w)
        else:  # has_right
            cab_right = full_right - self._right_offset
            available = max(cab_right - full_left, min_w)
            cabinet_extent = max(min(self._cabinet_width, available), min_w)
            placement_x = cab_right - cabinet_extent

        cage_obj.location.x = placement_x
        cage_obj.location.y = 0.0
        cage_obj.rotation_euler = (0, 0, 0)

        if self._cabinet_class.default_cabinet_type == 'UPPER':
            scene_props = context.scene.hb_face_frame
            cage_obj.location.z = scene_props.default_wall_cabinet_location
        else:
            cage_obj.location.z = 0.0

        self._selected_wall = wall
        self._placement_dim_specs = self._build_dim_specs_on_wall(
            context, wall, wall_length,
            self._gap_left_boundary, self._gap_right_boundary,
            placement_x, cabinet_extent,
        )
        if context.area is not None:
            context.area.tag_redraw()

    # ---------------- finalize / cancel ----------------

    def _finalize(self, context):
        """Commit: capture cage transform, delete cage, build real cabinet."""
        self.remove_placement_dim_handler()
        cage_obj = self._preview_cage.obj
        captured_parent = cage_obj.parent
        captured_world = cage_obj.matrix_world.copy()
        captured_local_loc = cage_obj.location.copy()
        captured_local_rot = cage_obj.rotation_euler.copy()

        self._delete_preview()

        cls = self._cabinet_class
        try:
            cabinet = cls()
            cabinet.create(self.cabinet_name)
        except Exception as e:
            self.report({'ERROR'}, f"Cabinet creation failed: {e}")
            hb_placement.clear_header_text(context)
            return {'CANCELLED'}

        cab_obj = cabinet.obj
        if captured_parent is not None:
            cab_obj.parent = captured_parent
            cab_obj.matrix_parent_inverse.identity()
            cab_obj.location = captured_local_loc
            cab_obj.rotation_euler = captured_local_rot
        else:
            cab_obj.matrix_world = captured_world

        for o in context.selected_objects:
            o.select_set(False)
        cab_obj.select_set(True)
        context.view_layer.objects.active = cab_obj
        try:
            bpy.ops.hb_face_frame.toggle_mode(search_obj_name=cab_obj.name)
            cab_obj.select_set(True)
            context.view_layer.objects.active = cab_obj
        except RuntimeError:
            pass

        hb_placement.clear_header_text(context)
        side = self._corner_side or 'free'
        self.report({'INFO'}, f"Placed {self.cabinet_name} ({side})")
        return {'FINISHED'}

    def _cancel(self, context):
        self.remove_placement_dim_handler()
        self._delete_preview()
        hb_placement.clear_header_text(context)
        return {'CANCELLED'}

    def _delete_preview(self):
        if self._preview_cage is None:
            return
        try:
            self._delete_object_and_children(self._preview_cage.obj)
        except Exception:
            try:
                bpy.data.objects.remove(self._preview_cage.obj, do_unlink=True)
            except Exception:
                pass
        self._preview_cage = None


class hb_face_frame_OT_set_blind_corner_void_amount(bpy.types.Operator):
    """Modal popup invoked after a placement that lands at a 90-degree
    wall corner with a perpendicular cabinet neighbor. Lets the user
    pick how the two cabinets meet (depth-match vs. fixed void) and
    what stile widths apply, then applies the blind state to the
    neighbor and the matching adjacent-side state to the placed
    cabinet.
    """
    bl_idname = "hb_face_frame.set_blind_corner_void_amount"
    bl_label = "Set Blind Corner Void Amount"
    bl_description = (
        "Configure how the placed cabinet meets a perpendicular "
        "cabinet at this wall corner"
    )
    bl_options = {'UNDO'}

    blind_cabinet_name: bpy.props.StringProperty(
        name="Blind Cabinet Name", default="",
    )  # type: ignore
    current_cabinet_name: bpy.props.StringProperty(
        name="Placed Cabinet Name", default="",
    )  # type: ignore
    # 'LEFT' = neighbor's left side becomes blind (placed cabinet near
    # the right end of its wall); 'RIGHT' = neighbor's right side blind
    # (placed cabinet near the left end).
    blind_side: bpy.props.EnumProperty(
        name="Blind Side",
        items=[('LEFT', "Left", ""), ('RIGHT', "Right", "")],
        default='LEFT',
    )  # type: ignore

    match_cabinet_depth: bpy.props.BoolProperty(
        name="Match Cabinet Depth",
        description=(
            "Auto-set the void so the blind cabinet's exposed end "
            "lines up with the back of the placed cabinet's face frame"
        ),
        default=False,
    )  # type: ignore
    void_amount: bpy.props.FloatProperty(
        name="Void Amount", default=units.inch(1.0),
        min=0.0, unit='LENGTH', precision=4,
    )  # type: ignore
    blind_stile_width: bpy.props.FloatProperty(
        name="Exposed Blind Stile Width",
        description=(
            "Visible portion of the blind end stile; the 0.75 inch "
            "accept-adjacent add is applied internally so the actual "
            "stile width is this value plus 0.75 inch"
        ),
        default=units.inch(3.0),
        min=0.0, unit='LENGTH', precision=4,
    )  # type: ignore
    current_cabinet_stile_width: bpy.props.FloatProperty(
        name="Placed Cabinet Stile Width",
        default=units.inch(2.0),
        min=0.0, unit='LENGTH', precision=4,
    )  # type: ignore

    def invoke(self, context, event):
        scene = context.scene
        ff_scene = getattr(scene, 'hb_face_frame', None)
        if ff_scene is not None:
            self.blind_stile_width = ff_scene.ff_blind_stile_width
            self.current_cabinet_stile_width = ff_scene.ff_end_stile_width
        return context.window_manager.invoke_props_dialog(self, width=420)

    def draw(self, context):
        layout = self.layout
        placed = bpy.data.objects.get(self.current_cabinet_name)
        blind = bpy.data.objects.get(self.blind_cabinet_name)
        if placed is None or blind is None:
            layout.label(text="Cabinet reference lost", icon='ERROR')
            return

        side_label = "left" if self.blind_side == 'LEFT' else "right"
        layout.label(
            text=f"{blind.name}'s {side_label} end will become blind",
            icon='INFO',
        )

        row = layout.row(align=True)
        row.label(text="Match Cabinet Depth:")
        row.prop(self, 'match_cabinet_depth', text="")

        if self.match_cabinet_depth:
            depth_in = placed.face_frame_cabinet.depth * 39.37008
            layout.label(
                text=f"Void will match the placed cabinet's depth ({depth_in:.2f} in)"
            )
        else:
            row = layout.row(align=True)
            row.label(text="Void Amount:")
            row.prop(self, 'void_amount', text="")

        row = layout.row(align=True)
        row.label(text="Exposed Blind Stile Width:")
        row.prop(self, 'blind_stile_width', text="")

        row = layout.row(align=True)
        row.label(text="Placed Cabinet Stile Width:")
        row.prop(self, 'current_cabinet_stile_width', text="")

    def execute(self, context):
        blind_obj = bpy.data.objects.get(self.blind_cabinet_name)
        placed_obj = bpy.data.objects.get(self.current_cabinet_name)
        if blind_obj is None or placed_obj is None:
            self.report({'WARNING'}, "Cabinet missing; aborting blind setup")
            return {'CANCELLED'}

        blind_props = blind_obj.face_frame_cabinet
        placed_props = placed_obj.face_frame_cabinet
        ff_thickness = placed_props.face_frame_thickness
        depth = placed_props.depth

        # Width reduction and blind state by mode:
        #   match-depth: shrink so the blind cabinet's exposed end lines
        #     up flush with the back of the placed cabinet's face frame.
        #     No blind area remains inside the blind cabinet, so the
        #     blind flag goes off and no blind panel is rendered.
        #   void mode: shrink by the user-typed void only. The blind
        #     area inside the blind cabinet covers the placed cabinet's
        #     remaining depth minus the face frame thickness.
        if self.match_cabinet_depth:
            width_reduction = max(depth - ff_thickness, 0.0)
            new_blind_flag = False
            new_blind_amount = 0.0
        else:
            width_reduction = self.void_amount
            new_blind_flag = True
            new_blind_amount = max(
                depth - self.void_amount - ff_thickness, 0.0
            )

        # Cap the reduction at the current width so the cabinet doesn't
        # collapse below 1" (a sentinel; the user can recover by widening).
        new_blind_width = max(
            blind_props.width - width_reduction, units.inch(1.0)
        )
        actual_reduction = blind_props.width - new_blind_width

        # Stile width: the recompute callback would write
        # ff_blind_stile_width (+0.75 when blind flag is True). Override
        # with the user's value, applying the 0.75" accept-adjacent add
        # only when the blind flag remains on.
        final_stile_w = self.blind_stile_width + (
            units.inch(0.75) if new_blind_flag else 0.0
        )

        with types_face_frame.suspend_recalc():
            if self.blind_side == 'LEFT':
                # Shift the cabinet's wall-local X by the reduction so
                # the right edge stays anchored while the left edge
                # moves away from the wall corner. Cabinet origin sits
                # at the left edge, so location.x tracks that edge.
                blind_obj.location.x += actual_reduction
                blind_props.width = new_blind_width
                blind_props.left_stile_type = 'BLIND'
                blind_props.blind_left = new_blind_flag
                blind_props.blind_amount_left = new_blind_amount
                blind_props.left_stile_width = final_stile_w
                placed_props.right_stile_type = 'BLIND'
                placed_props.right_stile_width = self.current_cabinet_stile_width
            else:  # 'RIGHT'
                # Shrinking from the right edge requires no location
                # shift since the origin sits at the left edge.
                blind_props.width = new_blind_width
                blind_props.right_stile_type = 'BLIND'
                blind_props.blind_right = new_blind_flag
                blind_props.blind_amount_right = new_blind_amount
                blind_props.right_stile_width = final_stile_w
                placed_props.left_stile_type = 'BLIND'
                placed_props.left_stile_width = self.current_cabinet_stile_width

        return {'FINISHED'}


classes = (
    hb_face_frame_OT_place_cabinet,
    hb_face_frame_OT_place_appliance,
    hb_face_frame_OT_place_corner_cabinet,
    hb_face_frame_OT_set_blind_corner_void_amount,
)


register, unregister = bpy.utils.register_classes_factory(classes)
