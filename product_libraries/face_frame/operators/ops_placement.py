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
    return (cls.width, cls.height, cls.depth)


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


class hb_face_frame_OT_place_cabinet(bpy.types.Operator,
                                     hb_placement.PlacementMixin):
    """Modal: cursor drags a face-frame preview cage, click to commit."""
    bl_idname = "hb_face_frame.place_cabinet"
    bl_label = "Place Face Frame Cabinet"
    bl_description = (
        "Place a face frame cabinet on a wall or on the floor. "
        "Up/Down arrows adjust bay quantity, Esc cancels."
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
    _cabinet_snap_side = None       # None | 'LEFT' | 'RIGHT' off-wall cabinet-to-cabinet snap

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

        if event.type == 'MOUSEMOVE':
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
        """Live preview: parse typed_value and resize cage every keystroke.

        Errors are silent (incomplete typing like "5'" briefly fails to
        parse, which is fine - we just skip live preview until the
        value parses).
        """
        if not self.typed_value:
            return
        if self.typing_target != hb_placement.TypingTarget.WIDTH:
            return
        parsed = self.parse_typed_distance()
        if parsed is None or parsed <= 0:
            return
        self._apply_width(parsed, fill_mode=False)

    def apply_typed_value(self):
        """Commit the typed value on ENTER. Disables fill mode."""
        if self.typing_target == hb_placement.TypingTarget.WIDTH:
            parsed = self.parse_typed_distance()
            if parsed is not None and parsed > 0:
                self._apply_width(parsed, fill_mode=False)
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
        # they can see what they've entered. Otherwise show the static
        # state (size, side, key hints).
        if self.placement_state == hb_placement.PlacementState.TYPING:
            typed = self.get_typed_display_string()
            hb_placement.draw_header_text(
                context,
                f"{self.cabinet_name}  -  {typed}  -  "
                "Enter: apply   Esc: cancel typing   Backspace: delete"
            )
        else:
            hb_placement.draw_header_text(
                context,
                f"{self.cabinet_name}  -  {bay_label} ({mode})  -  "
                f"width: {width_in:.1f}\"  -  side: {side}  -  "
                "W/numbers: type width   Up/Down: bays   "
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

        # In fill mode, cabinet width follows the gap. With typed width
        # (fill_mode=False), the user controls the width; gap snap
        # forces the cabinet flush to the chosen end or centered in
        # the gap, otherwise we clamp the cursor-centered position
        # into the gap.
        if self._fill_mode:
            self._apply_width(gap_width, fill_mode=True)
            placement_x = gap_start
            cabinet_width = gap_width
        else:
            cabinet_width = min(self._cabinet_width, gap_width)
            if self._gap_snap == 'LEFT':
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
        # user has a clear "this is locked" signal. For CENTER, the
        # offset dims also go green because their equality IS the
        # snap; otherwise it could look like the cabinet just happens
        # to be centered.
        snap_green = (0.30, 0.95, 0.40, 1.0)
        total_color = snap_green if self._gap_snap else None
        offset_color = snap_green if self._gap_snap == 'CENTER' else None
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

        # Active selection
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
        "Esc cancels."
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
    _cabinet_snap_side = None

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
        self._cabinet_snap_side = None

        try:
            self._create_preview_cage(context)
        except Exception as e:
            self.report({'ERROR'}, f"Preview creation failed: {e}")
            return {'CANCELLED'}

        cage_obj = self._preview_cage.obj
        cage_obj.location = context.scene.cursor.location.copy()

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

        if event.type in {'ESC', 'RIGHTMOUSE'} and event.value == 'PRESS':
            return self._cancel(context)

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            return self._finalize(context)

        if event.type == 'MOUSEMOVE':
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
        hb_placement.draw_header_text(
            context,
            f"{self.appliance_name}  -  width: {width_in:.1f}\""
            f"  -  side: {side}  -  Click: place   Esc: cancel"
        )

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

        if snap_result is not None:
            new_loc, new_rot = snap_result
            cage_obj.location = new_loc
            cage_obj.rotation_euler = new_rot
            cage_obj.location.z = snap_target.location.z
        else:
            self._cabinet_snap_side = None
            cage_obj.location = self.hit_location.copy()
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
        total_color = snap_green if self._gap_snap else None
        offset_color = snap_green if self._gap_snap == 'CENTER' else None

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
        "corner is closer to the cursor. LMB commits, Esc cancels."
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

        if event.type in {'ESC', 'RIGHTMOUSE'} and event.value == 'PRESS':
            return self._cancel(context)

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            return self._finalize(context)

        if event.type == 'MOUSEMOVE':
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
        msg = (f"Place {self.cabinet_name} - move cursor near a wall corner. "
               f"LMB commits, Esc cancels.")
        hb_placement.draw_header_text(context, msg)

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


classes = (
    hb_face_frame_OT_place_cabinet,
    hb_face_frame_OT_place_appliance,
    hb_face_frame_OT_place_corner_cabinet,
)


register, unregister = bpy.utils.register_classes_factory(classes)
