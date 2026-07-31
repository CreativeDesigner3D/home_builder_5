"""Closet starter operators: modal placement, selection-mode toggle,
bay insert/delete, delete, and properties popups.

Placement ports the face_frame place-cabinet modal's core wall
path: a preview cage with an array modifier previews the bays, the cage
parents to the wall under the cursor, width auto-fills the gap between
neighbors (shared PlacementMixin gap detection), W/numbers type a width,
Up/Down set bay quantity, Left/Right type gap-edge offsets, R rotates in
free placement, and GPU dims annotate width + gap offsets. Face-frame
extras (corner snap, island facing, window centering, recess) are
intentionally not ported - closets don't need them yet.
"""
import bpy
import math
import os
from mathutils import Vector

from .... import hb_types, hb_placement, hb_snap, units
from ...frameless.operators.ops_placement import toggle_cabinet_color
# Shared wall detection (raycast + nearest-wall floor fallback). Lives in
# face_frame today; promote to hb_placement if a third library needs it.
from ...face_frame.operators.ops_placement import _detect_wall
from .. import const_closets as const
from .. import types_closets
from .. import drawer_boxes_closets

# Per-opening box-system choices: "Use Default" (defer to the project
# setting) plus every box system. Held at module scope so the enum
# item strings stay alive for the property.
_DRAWER_BOX_OVERRIDE_ITEMS = [
    ('DEFAULT', "Use Default", "Use the project drawer box setting"),
] + list(drawer_boxes_closets.BOX_TYPES)

_BAY_QTY_MIN = const.MIN_BAY_QTY
_BAY_QTY_MAX = const.MAX_BAY_QTY
# Cursor must cross the wall centerline by this much before the
# placement side flips (mirrors face_frame's hysteresis).
_FRONT_BACK_HYSTERESIS = 0.05
_PLAN_VIEW_THRESHOLD = 0.999
_SNAP_GREEN = (0.30, 0.95, 0.40, 1.0)


def _apply_finish(root_obj):
    """Assign the closets material selection (scene dropdowns) to every
    cutpart under the starter; while no closet material resolves (e.g.
    missing assets library) fall back to the active cabinet style's
    finish via the shared face_frame helper. Best-effort: failure
    leaves parts unfinished rather than failing placement."""
    try:
        from .. import materials_closets
        if materials_closets.apply_to_starter(root_obj):
            return
    except Exception:
        pass
    try:
        from ...face_frame.types_face_frame import apply_active_finish_to_product
        apply_active_finish_to_product(root_obj)
    except Exception:
        pass


def _apply_selection_shading(context, root_obj, keep_active=True):
    """Run the selection-mode shading pass scoped to one starter so
    freshly created objects land already shaded for the current mode
    (face_frame does the same after placement). toggle_mode deselects
    everything, so restore the active selection after."""
    if root_obj is None:
        return
    try:
        bpy.ops.hb_closets.toggle_mode(search_obj_name=root_obj.name)
        if keep_active:
            root_obj.select_set(True)
            context.view_layer.objects.active = root_obj
    except RuntimeError:
        pass


def _clearance_obstacles(scene, exclude_obj, z0, z1):
    """Plan-view obstacles for island clearance: wall bodies and every
    cabinet/closet root that overlaps the island's height band. Each
    entry is (world->local matrix, x_min, x_max, y_min, y_max, label)
    describing an oriented rectangle in its own local frame."""
    out = []
    for obj in scene.objects:
        if obj is exclude_obj or obj.get('hb_preview'):
            continue
        if 'IS_WALL_BP' in obj:
            try:
                g = hb_types.GeoNodeWall(obj)
                length = g.get_input('Length')
                thickness = g.get_input('Thickness')
            except Exception:
                continue
            out.append((obj.matrix_world.inverted(),
                        0.0, length, 0.0, thickness, "wall"))
        elif any(m in obj for m in hb_placement.CABINET_MARKERS):
            try:
                g = hb_types.GeoNodeObject(obj)
                w = g.get_input('Dim X')
                d = g.get_input('Dim Y')
                h = g.get_input('Dim Z')
            except Exception:
                continue
            oz = obj.matrix_world.translation.z
            if not (z0 < oz + h - 1e-4 and oz < z1 - 1e-4):
                continue
            out.append((obj.matrix_world.inverted(),
                        0.0, w, -d, 0.0, "closet"))
    return out


def _ray_rect_distance(origin, direction, rect):
    """Distance along a plan ray to an oriented rectangle, or None.
    Slab test in the rectangle's local XY frame."""
    inv, x0, x1, y0, y1, _label = rect
    o = inv @ origin
    d = inv.to_3x3() @ direction
    t_min, t_max = 0.0, 1e9
    for axis, lo, hi in ((0, x0, x1), (1, y0, y1)):
        dv = d[axis]
        ov = o[axis]
        if abs(dv) < 1e-9:
            if ov < lo or ov > hi:
                return None
            continue
        ta = (lo - ov) / dv
        tb = (hi - ov) / dv
        if ta > tb:
            ta, tb = tb, ta
        t_min = max(t_min, ta)
        t_max = min(t_max, tb)
        if t_min > t_max:
            return None
    return t_min if t_min >= 0.0 else None


_ISLAND_SIDES = ('FRONT', 'RIGHT', 'BACK', 'LEFT')


def _island_clearances(cage_obj, width, depth, z0, height, scene):
    """Nearest clearance per island side, measured in plan from three
    points along each face outward to walls and other closets. Returns
    {side: (distance, label) | None} - None when a side is open past
    the search reach."""
    mw = cage_obj.matrix_world
    x_axis = (mw.to_3x3() @ Vector((1.0, 0.0, 0.0))).normalized()
    y_axis = (mw.to_3x3() @ Vector((0.0, 1.0, 0.0))).normalized()
    x_axis.z = y_axis.z = 0.0
    obstacles = _clearance_obstacles(scene, cage_obj, z0, z0 + height)
    inset = min(units.inch(2.0), width / 4.0, depth / 4.0)
    faces = {
        'FRONT': (-y_axis, [(x, -depth) for x in
                            (inset, width / 2.0, width - inset)]),
        'BACK': (y_axis, [(x, 0.0) for x in
                          (inset, width / 2.0, width - inset)]),
        'LEFT': (-x_axis, [(0.0, -y) for y in
                           (inset, depth / 2.0, depth - inset)]),
        'RIGHT': (x_axis, [(width, -y) for y in
                           (inset, depth / 2.0, depth - inset)]),
    }
    result = {}
    for side, (normal, points) in faces.items():
        best = None
        best_label = ""
        for px, py in points:
            origin = mw @ Vector((px, py, 0.0))
            origin.z = 0.0
            for rect in obstacles:
                t = _ray_rect_distance(origin, normal, rect)
                if t is not None and t <= const.CLEARANCE_MAX_REACH:
                    if best is None or t < best:
                        best = t
                        best_label = rect[5]
        result[side] = (best, best_label) if best is not None else None
    return result


def _detect_corner_closet_neighbor(root_obj):
    """Find closet starters on adjacent perpendicular walls that meet
    root_obj at its wall's corners. Returns a list of
    ``(neighbor, placed_end, gap)`` tuples - one per qualifying end, so
    a closet filling a wall between two occupied corners yields both -
    where ``placed_end`` is which end of the placed starter faces that
    corner ('LEFT' = its low-x end) and ``gap`` is the current distance
    between that end and the neighbor's intrusion boundary on this
    wall. Empty list when nothing qualifies.

    Adapted from face_frame's _detect_blind_corner_neighbor, reduced to
    what closets need: square (~90 deg) corners only, closet-starter
    neighbors only. L-shelf corner units resolve the corner themselves,
    so they never qualify as a neighbor. Gates mirror face_frame: the
    neighbor must share a height band with the placed starter and have
    a footprint corner near the wall corner (a far closet on the same
    adjacent wall projects the same intrusion, so intrusion alone can't
    disambiguate), and the placed starter's corner-side edge must sit at
    the wall end or at the intrusion boundary (within 1")."""
    matches = []
    wall = root_obj.parent
    if wall is None or 'IS_WALL_BP' not in wall:
        return matches
    try:
        wall_geo = hb_types.GeoNodeWall(wall)
        wall_length = wall_geo.get_input('Length')
    except Exception:
        return matches

    sp = root_obj.hb_closet_starter
    cab_left = root_obj.location.x
    cab_right = cab_left + sp.width
    our_z0 = root_obj.matrix_world.translation.z
    our_z1 = our_z0 + sp.height

    EDGE_TOL = units.inch(1.0)
    ANGLE_TOL_DEG = 5.0
    CORNER_NEAR_TOL = units.inch(8.0)
    Z_TOL = units.inch(0.25)
    our_inv = wall.matrix_world.inverted()

    for direction in ('left', 'right'):
        adj_node = wall_geo.get_connected_wall(direction=direction,
                                               include_loop_seam=True)
        if adj_node is None:
            continue

        # Square-corner gate on the walls' length axes.
        a_axis = wall.matrix_world.to_3x3() @ Vector((1.0, 0.0, 0.0))
        b_axis = adj_node.obj.matrix_world.to_3x3() @ Vector((1.0, 0.0, 0.0))
        a_axis.z = 0.0
        b_axis.z = 0.0
        if a_axis.length < 1e-8 or b_axis.length < 1e-8:
            continue
        a_axis.normalize()
        b_axis.normalize()
        cos = max(-1.0, min(1.0, a_axis.dot(b_axis)))
        if abs(math.degrees(math.acos(cos)) - 90.0) > ANGLE_TOL_DEG:
            continue

        corner_local = Vector(
            (wall_length if direction == 'right' else 0.0, 0.0))
        best_obj = None
        best_intrusion = 0.0
        for child in adj_node.obj.children:
            if child.get('obj_x') or child.get('IS_2D_ANNOTATION'):
                continue
            if types_closets.TAG_STARTER_CAGE not in child:
                continue
            if str(child.get('CLASS_NAME', '')).startswith('LShelf'):
                continue
            try:
                geo = hb_types.GeoNodeObject(child)
                child_w = geo.get_input('Dim X')
                child_d = geo.get_input('Dim Y')
                child_h = geo.get_input('Dim Z')
            except Exception:
                continue
            child_z0 = child.matrix_world.translation.z
            if not (our_z0 < child_z0 + child_h - Z_TOL
                    and child_z0 < our_z1 - Z_TOL):
                continue
            local_corners = [
                Vector((0.0, 0.0, 0.0)),
                Vector((child_w, 0.0, 0.0)),
                Vector((0.0, -child_d, 0.0)),
                Vector((child_w, -child_d, 0.0)),
            ]
            corners_our = [our_inv @ (child.matrix_world @ c)
                           for c in local_corners]
            if min((c.xy - corner_local).length
                   for c in corners_our) > CORNER_NEAR_TOL:
                continue
            if direction == 'left':
                intrusion = max(
                    (c.x for c in corners_our if c.x > 0), default=0.0)
            else:
                intrusion = max(
                    (wall_length - c.x for c in corners_our
                     if c.x < wall_length),
                    default=0.0)
            if intrusion > best_intrusion:
                best_intrusion = intrusion
                best_obj = child
        if best_obj is None:
            continue

        if direction == 'left':
            gap = cab_left - best_intrusion
            qualifies = (cab_left <= EDGE_TOL or abs(gap) <= EDGE_TOL)
        else:
            gap = (wall_length - best_intrusion) - cab_right
            qualifies = (cab_right >= wall_length - EDGE_TOL
                         or abs(gap) <= EDGE_TOL)
        if not qualifies:
            continue
        placed_end = 'LEFT' if direction == 'left' else 'RIGHT'
        matches.append((best_obj, placed_end, max(gap, 0.0)))
    return matches


# ---------------------------------------------------------------------------
# Selection mode toggle
# ---------------------------------------------------------------------------
class hb_closets_OT_toggle_mode(bpy.types.Operator):
    """Apply visibility/highlighting for the current closet selection
    mode. Mirrors the face_frame toggle_mode operator, scoped to
    closet-tagged objects."""
    bl_idname = "hb_closets.toggle_mode"
    bl_label = "Toggle Closet Selection Mode"
    bl_description = "Highlight objects matching the current closet selection mode"

    search_obj_name: bpy.props.StringProperty(name="Search Object Name", default="")  # type: ignore

    MODE_TAGS = {
        'Starters': types_closets.TAG_STARTER_CAGE,
        'Bays': types_closets.TAG_BAY_CAGE,
        'Openings': types_closets.TAG_OPENING_CAGE,
    }

    def _matches_mode(self, obj, mode):
        if mode == 'Parts':
            # Parts render at default color (the execute() off-path), but
            # the mode is still readable for selection scoping elsewhere.
            return False
        tag = self.MODE_TAGS.get(mode)
        if tag is None:
            return False
        return tag in obj

    def _toggle_one(self, obj, mode):
        # Never touch scene geometry outside the closet hierarchy.
        if any(t in obj for t in ('IS_WALL_BP', 'IS_ENTRY_DOOR_BP',
                                  'IS_WINDOW_BP', 'IS_CUTTING_OBJ',
                                  'IS_2D_ANNOTATION')):
            return
        if types_closets.find_starter_root(obj) is None:
            return
        if self._matches_mode(obj, mode):
            toggle_cabinet_color(obj, True,
                                 type_name=self.MODE_TAGS.get(mode, ''),
                                 dont_show_parent=False)
        else:
            toggle_cabinet_color(obj, False,
                                 type_name=self.MODE_TAGS.get(mode, ''))

    def execute(self, context):
        props = context.scene.hb_closets
        mode = props.closet_selection_mode
        # Master toggle off (or Parts mode) routes everything through the
        # "not highlighted" branch: parts at default render, cages hidden.
        if not props.closet_selection_mode_enabled or mode == 'Parts':
            mode = '__off__'

        if self.search_obj_name and self.search_obj_name in bpy.data.objects:
            root_obj = bpy.data.objects[self.search_obj_name]
            self._toggle_one(root_obj, mode)
            for child in root_obj.children_recursive:
                self._toggle_one(child, mode)
        else:
            for obj in context.scene.objects:
                self._toggle_one(obj, mode)

        bpy.ops.object.select_all(action='DESELECT')
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Placement modal
# ---------------------------------------------------------------------------
def _flip_bay_swing(bay):
    """LEFT<->RIGHT flip of a bay-wide front's swing; DOUBLE, LIFT_UP
    and empty values pass through unchanged."""
    bp = bay.hb_closet_bay
    if bp.door_swing == 'LEFT':
        bp.door_swing = 'RIGHT'
    elif bp.door_swing == 'RIGHT':
        bp.door_swing = 'LEFT'


def _flip_opening_swing(opening):
    """LEFT<->RIGHT flip of an opening's door swing; DOUBLE and no-door
    openings pass through unchanged."""
    op = opening.hb_closet_opening
    if op.door_swing == 'LEFT':
        op.door_swing = 'RIGHT'
    elif op.door_swing == 'RIGHT':
        op.door_swing = 'LEFT'


def _mirror_starter_config(root):
    """Flip a duplicated starter's configuration left<->right: reverse
    the bay order (bay widths and contents travel with their bays) and
    flip every LEFT/RIGHT door swing, bay-wide and per-opening. Shared
    panels, rods, shelves, and fronts regenerate on the recalc."""
    bays = sorted(
        [c for c in root.children if c.get(types_closets.TAG_BAY_CAGE)],
        key=lambda c: c.get('hb_bay_index', 0))
    n = len(bays)
    for i, bay in enumerate(bays):
        bay['hb_bay_index'] = n - 1 - i
        bay.hb_closet_bay.bay_index = n - 1 - i
        _flip_bay_swing(bay)
        for child in bay.children:
            if child.get(types_closets.TAG_OPENING_CAGE):
                _flip_opening_swing(child)
    types_closets.recalculate_closet_starter(root)


def _dispatch_name_for_starter(src):
    """Library name whose class matches the source root's CLASS_NAME,
    so duplicate-mode lookups resolve to the same starter class."""
    cls_name = src.get('CLASS_NAME', '')
    for name, cls in types_closets.CLOSET_NAME_DISPATCH.items():
        if cls.__name__ == cls_name:
            return name
    return None


class hb_closets_OT_place_starter(bpy.types.Operator,
                                  hb_placement.PlacementMixin):
    """Place a closet starter. On a wall the width fills the available
    gap; W or numbers type a width, Up/Down set bay quantity, Left/Right
    type gap-edge offsets, R rotates in free placement, click places,
    Right-click or Esc cancels."""
    bl_idname = "hb_closets.place_starter"
    bl_label = "Place Closet Starter"
    bl_options = {'UNDO'}

    starter_name: bpy.props.StringProperty(
        name="Starter Name", default="Base")  # type: ignore
    bay_qty: bpy.props.IntProperty(
        name="Bay Quantity", default=4,
        min=_BAY_QTY_MIN, max=_BAY_QTY_MAX)  # type: ignore
    source_starter_name: bpy.props.StringProperty(
        name="Source Starter Name",
        description="When set, duplicate this existing starter root "
                    "instead of building a new starter from defaults",
        default="")  # type: ignore
    mirror: bpy.props.BoolProperty(
        name="Mirror",
        description="Duplicate mode only: flip the copy left-to-right "
                    "(bay order and door swings)",
        default=False)  # type: ignore

    # Live modal state; reset per session in invoke().
    _preview_cage = None
    _array_modifier = None
    _source_obj = None   # duplicate mode: starter root being copied
    _cabinet_width: float = 0.0
    _cabinet_depth: float = 0.0
    _cabinet_height: float = 0.0
    _is_hanging: bool = False
    _fill_mode: bool = True
    _auto_bay_qty: bool = True
    _place_on_front: bool = True
    _free_rotation_z: float = 0.0
    _gap_snap = None
    _gap_wall = None
    _gap_left_boundary: float = 0.0
    _gap_right_boundary: float = 0.0
    _left_offset = None
    _right_offset = None

    # ---------------- lifecycle ----------------

    def invoke(self, context, event):
        # Duplicate mode: resolve the source starter and derive its
        # library name from the stored class so downstream lookups
        # (corner / island / hanging flags) match the source.
        self._source_obj = None
        if self.source_starter_name:
            src = bpy.data.objects.get(self.source_starter_name)
            if src is None or not src.get(types_closets.TAG_STARTER_CAGE):
                self.report({'WARNING'},
                            f"Source starter not found: "
                            f"{self.source_starter_name}")
                return {'CANCELLED'}
            name = _dispatch_name_for_starter(src)
            if name is None:
                self.report({'WARNING'},
                            "Cannot duplicate: unknown starter class")
                return {'CANCELLED'}
            self._source_obj = src
            self.starter_name = name
        cls = types_closets.get_starter_class(self.starter_name)
        if cls is None:
            self.report({'WARNING'}, f"Unknown starter: {self.starter_name}")
            return {'CANCELLED'}

        scene_props = context.scene.hb_closets
        cls_inst = cls()
        self._is_hanging = not cls.floor_mounted
        self._is_corner = bool(getattr(cls, 'is_corner', False))
        # Island placement extras (clearance dims / aisle detents /
        # typed clearance) key off this.
        self._is_island = 'Island' in self.starter_name
        self._is_island_double = 'Double' in self.starter_name
        self._active_clearance_side = 'FRONT'
        self._suppress_detents = False
        self._clearance_anchor = None   # (location, clearance) at typing start
        self._last_clearances = {}
        self._detent_hit = set()
        if self._is_corner:
            # Corner L units are fixed-footprint singles: no gap fill,
            # no bay tiling.
            from .. import const_closets as const
            self._cabinet_width = const.L_SHELF_SIZE
            self._cabinet_depth = const.L_SHELF_SIZE
            self.bay_qty = 1
        else:
            self._cabinet_width = scene_props.default_closet_width
            self._cabinet_depth = (cls.default_depth
                                   if cls.default_depth is not None
                                   else scene_props.default_panel_depth)
        # Auto-fill widths picked up over a wall reset to this off-wall
        # (typed widths persist - they clear fill mode).
        self._default_free_width = self._cabinet_width
        if not self._is_corner:
            # Derive the initial bay count from the width (target 42",
            # no bay > 42"); fill mode recomputes it per wall gap.
            self.bay_qty = types_closets.auto_bay_qty(self._cabinet_width)
        self._cabinet_height = cls_inst.default_height(scene_props)
        self._fill_mode = not self._is_corner
        self._auto_bay_qty = not self._is_corner
        if self._source_obj is not None:
            # Seed from the source's real dimensions and bay count.
            # Fill starts OFF (the copy keeps its size); F toggles
            # fill-the-gap in the modal. Bay count is pinned so a
            # fill stretches the copied bays rather than re-deriving
            # a quantity. _default_free_width keeps off-wall resets
            # at the source width too.
            sp = self._source_obj.hb_closet_starter
            self._cabinet_width = sp.width
            self._cabinet_depth = sp.depth
            self._cabinet_height = sp.height
            self._default_free_width = self._cabinet_width
            self._fill_mode = False
            self._auto_bay_qty = False
            self.bay_qty = max(1, min(_BAY_QTY_MAX, sum(
                1 for c in self._source_obj.children
                if c.get(types_closets.TAG_BAY_CAGE))))
        self._place_on_front = True
        self._free_rotation_z = 0.0
        self._gap_snap = None
        self._gap_wall = None
        self._left_offset = None
        self._right_offset = None

        self._create_preview_cage(context)

        cage_obj = self._preview_cage.obj
        cursor_loc = context.scene.cursor.location
        cage_obj.location.x = cursor_loc.x
        cage_obj.location.y = cursor_loc.y
        if self._source_obj is not None:
            # Keep the source's mounting height (custom hang heights)
            # instead of the scene default.
            cage_obj.location.z =                 self._source_obj.matrix_world.translation.z
        else:
            cage_obj.location.z = self._mount_z(scene_props)

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

    def _mount_z(self, scene_props):
        if self._is_hanging:
            return scene_props.hanging_top_height - self._cabinet_height
        return 0.0

    def _create_preview_cage(self, context):
        """Wireframe cage: one bay cell arrayed bay_qty times, extending
        -Y from origin like the starter itself. HB_CURRENT_DRAW_OBJ keeps
        it out of hb_snap raycasts."""
        cage = hb_types.GeoNodeCage()
        cage.create('ClosetPlacementPreview')
        cage.set_input('Dim X', self._cabinet_width / max(self.bay_qty, 1))
        cage.set_input('Dim Y', self._cabinet_depth)
        cage.set_input('Dim Z', self._cabinet_height)
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

    def _delete_preview(self):
        if self._preview_cage is not None:
            obj = self._preview_cage.obj
            try:
                bpy.data.objects.remove(obj, do_unlink=True)
            except ReferenceError:
                pass
        self._preview_cage = None
        self._array_modifier = None
        self.placement_objects = []

    def _cancel(self, context):
        self.remove_placement_dim_handler()
        self._delete_preview()
        hb_placement.clear_header_text(context)
        context.window.cursor_set('DEFAULT')
        return {'CANCELLED'}

    # ---------------- typed input integration ----------------

    def get_default_typing_target(self):
        return hb_placement.TypingTarget.WIDTH

    def on_typed_value_changed(self):
        if not self.typed_value:
            return
        parsed = self.parse_typed_distance()
        if parsed is None:
            return
        if self.typing_target == hb_placement.TypingTarget.WIDTH:
            if parsed > 0:
                self._apply_width(parsed, fill_mode=False)
        elif self.typing_target == hb_placement.TypingTarget.OFFSET_X:
            if parsed >= 0 and self._gap_wall is not None:
                old = self._left_offset
                self._left_offset = parsed
                self._reposition_with_offsets(bpy.context)
                self._left_offset = old
            elif (parsed >= 0 and self._gap_wall is None
                    and getattr(self, '_is_island', False)):
                self._apply_island_clearance(bpy.context, parsed)
        elif self.typing_target == hb_placement.TypingTarget.OFFSET_RIGHT:
            if parsed >= 0 and self._gap_wall is not None:
                old = self._right_offset
                self._right_offset = parsed
                self._reposition_with_offsets(bpy.context)
                self._right_offset = old

    def apply_typed_value(self):
        parsed = self.parse_typed_distance()
        if self.typing_target == hb_placement.TypingTarget.WIDTH:
            if parsed is not None and parsed > 0:
                self._apply_width(parsed, fill_mode=False)
        elif self.typing_target == hb_placement.TypingTarget.OFFSET_X:
            if parsed is not None and parsed >= 0 and self._gap_wall is not None:
                self._left_offset = parsed
                self._right_offset = None
                self._gap_snap = None
                self._reposition_with_offsets(bpy.context)
            elif (parsed is not None and parsed >= 0
                    and self._gap_wall is None
                    and getattr(self, '_is_island', False)):
                self._apply_island_clearance(bpy.context, parsed)
        elif self.typing_target == hb_placement.TypingTarget.OFFSET_RIGHT:
            if parsed is not None and parsed >= 0 and self._gap_wall is not None:
                self._right_offset = parsed
                self._left_offset = None
                self._gap_snap = None
                self._reposition_with_offsets(bpy.context)
        self.stop_typing()

    def _apply_width(self, width, fill_mode):
        """Set the preview width. fill_mode=False is the typed path (the
        next wall hover must not overwrite it); True is the auto-fill
        path where width follows the wall gap."""
        if getattr(self, '_is_corner', False):
            return  # fixed footprint
        if abs(width - self._cabinet_width) < 1e-5 and fill_mode == self._fill_mode:
            return
        self._cabinet_width = width
        self._fill_mode = fill_mode
        if self._auto_bay_qty:
            new_qty = types_closets.auto_bay_qty(width)
            if new_qty != self.bay_qty:
                self.bay_qty = new_qty
        self._update_cage()
        if not fill_mode and self.hit_location is not None:
            self._position_from_hit(bpy.context)

    def _handle_offset_arrow(self, context, side):
        """Left/Right arrow: start typing a gap-edge offset."""
        target = (hb_placement.TypingTarget.OFFSET_X if side == 'LEFT'
                  else hb_placement.TypingTarget.OFFSET_RIGHT)
        if self.placement_state == hb_placement.PlacementState.TYPING:
            if self.typed_value:
                self.apply_typed_value()
            self.typed_value = ""
            self.typing_target = target
            self.placement_state = hb_placement.PlacementState.TYPING
        else:
            self.start_typing(target)
        self._update_header(context)

    def _reposition_with_offsets(self, context):
        """Place the cage using per-side effective offsets from the
        true gap edges: a typed offset wins on ITS side; the other side
        keeps its automatic inside-corner pull-off. In fill mode the
        offsets TRIM the fill, so the starter shrinks and still reaches
        each side's effective edge; a typed width is preserved and only
        shifts (anchored to the typed side)."""
        if self._gap_wall is None:
            return
        if self._left_offset is None and self._right_offset is None:
            return
        gap_start = self._gap_left_boundary
        gap_end = self._gap_right_boundary
        left = (self._left_offset if self._left_offset is not None
                else getattr(self, '_auto_left_inset', 0.0))
        right = (self._right_offset if self._right_offset is not None
                 else getattr(self, '_auto_right_inset', 0.0))
        span = max(gap_end - gap_start - left - right, units.inch(1.0))
        if self._fill_mode:
            width = span
            self._apply_width(width, fill_mode=True)
        else:
            width = min(self._cabinet_width, span)
        if self._right_offset is not None and self._left_offset is None:
            placement_x = gap_end - right - width
        else:
            placement_x = gap_start + left
        self._place_cage_on_wall(context, self._gap_wall, placement_x, width,
                                 gap_start, gap_end)

    def _corner_insets(self, wall, wall_geo, wall_length, wall_thickness):
        """(left, right) automatic pull-offs for INSIDE corners on the
        placement side. A connected wall only earns the pull-off when
        it extends into the half-space the closet occupies (front:
        -Y; back: beyond the wall thickness) - outside corners and
        open ends need no relief. Tested via the connected wall's far
        endpoint in this wall's local frame, so any wall angle works."""
        insets = [0.0, 0.0]
        inv = wall.matrix_world.inverted()
        for i, direction in enumerate(('left', 'right')):
            try:
                node = wall_geo.get_connected_wall(
                    direction=direction, include_loop_seam=True)
                if node is None:
                    continue
                adj = node.obj
                adj_len = hb_types.GeoNodeWall(adj).get_input('Length')
                a = inv @ adj.matrix_world.translation
                b = inv @ (adj.matrix_world
                           @ Vector((adj_len, 0.0, 0.0)))
                corner = Vector((0.0 if direction == 'left'
                                 else wall_length, 0.0, 0.0))
                far = a if (a - corner).length > (b - corner).length else b
                if self._place_on_front:
                    inside = far.y < -1e-4
                else:
                    inside = far.y > wall_thickness + 1e-4
                if inside:
                    insets[i] = const.CORNER_PULL_OFF
            except Exception:
                continue
        return insets

    # ---------------- positioning ----------------

    def _position_from_hit(self, context):
        if self.hit_location is None:
            return
        wall = _detect_wall(self, context)
        if wall is not None:
            self._position_on_wall(context, wall)
            return
        self._position_free(context)

    def _update_place_on_front(self, context, wall, local_hit_y, wall_thickness):
        """Which side of the wall the cursor is on, with hysteresis. In a
        plan view the raycast often hits the wall TOP face, so project
        the cursor to the floor plane for a usable Y signal."""
        from bpy_extras import view3d_utils
        from mathutils.geometry import intersect_line_plane
        wall_center_y = wall_thickness / 2.0
        region = self.region
        rv3d = region.data if region is not None else None
        if rv3d is None:
            return
        cursor_y = local_hit_y
        if abs(rv3d.view_matrix[2][2]) > _PLAN_VIEW_THRESHOLD:
            view_origin = view3d_utils.region_2d_to_origin_3d(
                region, rv3d, self.mouse_pos)
            view_dir = view3d_utils.region_2d_to_vector_3d(
                region, rv3d, self.mouse_pos)
            floor_point = intersect_line_plane(
                view_origin, view_origin + view_dir * 10000,
                Vector((0, 0, 0)), Vector((0, 0, 1)))
            if floor_point is not None:
                cursor_y = (wall.matrix_world.inverted() @ floor_point).y
        if cursor_y < wall_center_y - _FRONT_BACK_HYSTERESIS:
            self._place_on_front = True
        elif cursor_y > wall_center_y + _FRONT_BACK_HYSTERESIS:
            self._place_on_front = False

    def _position_on_wall(self, context, wall):
        """Parent the cage to the wall; fill or snap within the gap
        between neighbors (shared PlacementMixin gap detection). Corner
        L units skip the gap logic entirely: they snap to the nearer
        wall END and orient so their wings hug both walls (the L fits
        either corner by rotation alone - origin AT the corner, 0 deg
        for the left end, -90 for the right)."""
        cage_obj = self._preview_cage.obj
        if getattr(self, '_is_corner', False):
            try:
                wall_geo = hb_types.GeoNodeWall(wall)
                wall_length = wall_geo.get_input('Length')
            except Exception:
                wall_length = 0.0
            if cage_obj.parent is not wall:
                cage_obj.parent = wall
                cage_obj.matrix_parent_inverse.identity()
            local_hit = wall.matrix_world.inverted() @ self.hit_location
            cage_obj.location.z = self._mount_z(context.scene.hb_closets)
            if local_hit.x <= wall_length / 2.0:
                cage_obj.location.x = 0.0
                cage_obj.location.y = 0.0
                cage_obj.rotation_euler = (0, 0, 0)
            else:
                cage_obj.location.x = wall_length
                cage_obj.location.y = 0.0
                cage_obj.rotation_euler = (0, 0, math.radians(-90))
            self._gap_wall = None
            self._placement_dim_specs = []
            if context.area is not None:
                context.area.tag_redraw()
            return
        try:
            wall_geo = hb_types.GeoNodeWall(wall)
            wall_thickness = wall_geo.get_input('Thickness')
            wall_length = wall_geo.get_input('Length')
        except Exception:
            wall_thickness = 0.0
            wall_length = 0.0

        if cage_obj.parent is not wall:
            cage_obj.parent = wall
            cage_obj.matrix_parent_inverse.identity()

        local_hit = wall.matrix_world.inverted() @ self.hit_location
        cursor_x = local_hit.x
        cage_obj.location.z = self._mount_z(context.scene.hb_closets)

        self._update_place_on_front(context, wall, local_hit.y, wall_thickness)

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
        if gap_start is None:
            gap_start = 0.0
            gap_end = wall_length
            snap_x = max(gap_start, cursor_x - self._cabinet_width / 2)

        self._gap_left_boundary = gap_start
        self._gap_right_boundary = gap_end
        self._gap_wall = wall

        # Automatic 1/2" pull-off at bare INSIDE corners so the closet
        # clears the return wall. Only when the gap edge IS the wall
        # end (a corner neighbor's intrusion has already moved the edge
        # - the clearance dialog owns that case) AND the connected wall
        # turns into the placement side (_corner_insets). Stored per
        # side so a typed offset on one end replaces its own pull-off
        # while the other end keeps its automatic one.
        try:
            auto_left, auto_right = self._corner_insets(
                wall, wall_geo, wall_length, wall_thickness)
        except Exception:
            auto_left = auto_right = 0.0
        if gap_start > 1e-6:
            auto_left = 0.0
        if gap_end < wall_length - 1e-6:
            auto_right = 0.0
        self._auto_left_inset = auto_left
        self._auto_right_inset = auto_right

        # Typed offset owns positioning once set (measured from the
        # TRUE gap edge; per-side merge with the automatic pull-offs
        # happens in _reposition_with_offsets).
        if self._left_offset is not None or self._right_offset is not None:
            self._gap_snap = None
            self._reposition_with_offsets(context)
            return

        gap_start += auto_left
        gap_end -= auto_right

        gap_width = max(gap_end - gap_start, units.inch(1.0))

        # Edge / center snap with hysteresis (fixed-floor engage zone so
        # narrow starters still get a usable zone; wider release so the
        # snap doesn't pop at the boundary). Fill mode pins to gap_start.
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
        near_center = (abs(cursor_x - gap_center) < center_thresh
                       and self._cabinet_width < gap_width)

        if self._fill_mode:
            self._gap_snap = None
        elif near_left and near_right:
            self._gap_snap = ('LEFT' if (cursor_x - gap_start) < (gap_end - cursor_x)
                              else 'RIGHT')
        elif near_left:
            self._gap_snap = 'LEFT'
        elif near_right:
            self._gap_snap = 'RIGHT'
        elif near_center:
            self._gap_snap = 'CENTER'
        else:
            self._gap_snap = None

        if self._fill_mode:
            self._apply_width(gap_width, fill_mode=True)
            placement_x = gap_start
            width = gap_width
        else:
            width = min(self._cabinet_width, gap_width)
            if self._gap_snap == 'LEFT':
                placement_x = gap_start
            elif self._gap_snap == 'RIGHT':
                placement_x = gap_end - width
            elif self._gap_snap == 'CENTER':
                placement_x = gap_start + (gap_width - width) / 2
            else:
                placement_x = max(gap_start, min(snap_x, gap_end - width))

        self._place_cage_on_wall(context, wall, placement_x, width,
                                 gap_start, gap_end)

    def _place_cage_on_wall(self, context, wall, placement_x, width,
                            gap_start, gap_end):
        """Write the cage transform for a wall placement and refresh the
        dim overlay. Back side: rotate pi around Z and offset by width
        (rotation about the origin shifts the geometry) + thickness."""
        cage_obj = self._preview_cage.obj
        try:
            wall_thickness = hb_types.GeoNodeWall(wall).get_input('Thickness')
        except Exception:
            wall_thickness = 0.0
        if self._place_on_front:
            cage_obj.location.x = placement_x
            cage_obj.location.y = 0.0
            cage_obj.rotation_euler = (0, 0, 0)
        else:
            cage_obj.location.x = placement_x + width
            cage_obj.location.y = wall_thickness
            cage_obj.rotation_euler = (0, 0, math.pi)

        self._placement_dim_specs = self._build_dim_specs_on_wall(
            context, wall, wall_thickness,
            gap_start, gap_end, placement_x, width)
        if context.area is not None:
            context.area.tag_redraw()

    def _position_free(self, context):
        """Off-wall: follow the cursor on the floor grid with the free
        rotation applied (R rotates; no automatic alignment). Hanging
        starters keep their mount height. A wall hover's auto-fill
        width resets to the library default out here (typed widths
        stick). Islands additionally snap their clearances to standard
        aisle widths (Shift bypasses) and draw live clearance dims on
        all four sides, with the opening faces labeled."""
        cage_obj = self._preview_cage.obj
        if cage_obj.parent is not None:
            world = cage_obj.matrix_world.copy()
            cage_obj.parent = None
            cage_obj.matrix_world = world
        self._gap_wall = None
        self._gap_snap = None

        is_island = getattr(self, '_is_island', False)
        if (self._fill_mode and not getattr(self, '_is_corner', False)):
            default_w = getattr(self, '_default_free_width', None)
            if default_w and abs(self._cabinet_width - default_w) > 1e-6:
                self._apply_width(default_w, fill_mode=True)

        snapped = hb_snap.snap_vector_to_grid(Vector(self.hit_location))
        cage_obj.location.x = snapped.x
        cage_obj.location.y = snapped.y
        cage_obj.location.z = self._mount_z(context.scene.hb_closets)
        cage_obj.rotation_euler = (0, 0, self._free_rotation_z)

        if is_island:
            self._apply_island_detents(context)

        unit_settings = context.scene.unit_settings
        z_dim = cage_obj.location.z + self._cabinet_height + units.inch(4.0)
        wm = cage_obj.matrix_world
        s = wm @ Vector((0.0, 0.0, 0.0))
        e = wm @ Vector((self._cabinet_width, 0.0, 0.0))
        s.z = e.z = z_dim
        self._placement_dim_specs = [hb_placement.PlacementDimSpec(
            s, e, units.unit_to_string(unit_settings, self._cabinet_width),
            None)]
        if is_island:
            self._placement_dim_specs += self._island_clearance_dims(context)
        if context.area is not None:
            context.area.tag_redraw()

    def _island_current_clearances(self, context):
        cage_obj = self._preview_cage.obj
        return _island_clearances(
            cage_obj, self._cabinet_width, self._cabinet_depth,
            cage_obj.location.z, self._cabinet_height, context.scene)

    def _apply_island_detents(self, context):
        """Nudge the island so a clearance near a standard aisle width
        lands exactly on it - per axis, using that axis's nearer side.
        Shift (recorded on mousemove) bypasses."""
        self._detent_hit = set()
        if self._suppress_detents:
            return
        cage_obj = self._preview_cage.obj
        clearances = self._island_current_clearances(context)
        mw = cage_obj.matrix_world
        x_axis = (mw.to_3x3() @ Vector((1.0, 0.0, 0.0))).normalized()
        y_axis = (mw.to_3x3() @ Vector((0.0, 1.0, 0.0))).normalized()
        normals = {'FRONT': -y_axis, 'BACK': y_axis,
                   'LEFT': -x_axis, 'RIGHT': x_axis}
        for pair in (('LEFT', 'RIGHT'), ('FRONT', 'BACK')):
            candidates = [(clearances[s][0], s) for s in pair
                          if clearances.get(s) is not None]
            if not candidates:
                continue
            dist, side = min(candidates)
            for detent in const.AISLE_DETENTS:
                if abs(dist - detent) <= const.AISLE_SNAP_ENGAGE:
                    delta = dist - detent
                    move = normals[side] * delta
                    cage_obj.location.x += move.x
                    cage_obj.location.y += move.y
                    self._detent_hit.add(side)
                    break

    def _island_clearance_dims(self, context):
        """One dim per side, from the face center out to the obstacle
        it measured. Detent-snapped sides draw green; the arrow-active
        side carries a marker so typed clearances have a visible
        target. Opening faces are labeled (Front - and Back on double
        islands) so the facing reads at a glance; a labeled face with
        nothing in reach still gets a short marker."""
        cage_obj = self._preview_cage.obj
        clearances = self._island_current_clearances(context)
        self._last_clearances = clearances
        mw = cage_obj.matrix_world
        w, d = self._cabinet_width, self._cabinet_depth
        x_axis = (mw.to_3x3() @ Vector((1.0, 0.0, 0.0))).normalized()
        y_axis = (mw.to_3x3() @ Vector((0.0, 1.0, 0.0))).normalized()
        centers = {'FRONT': (Vector((w / 2.0, -d, 0.0)), -y_axis),
                   'BACK': (Vector((w / 2.0, 0.0, 0.0)), y_axis),
                   'LEFT': (Vector((0.0, -d / 2.0, 0.0)), -x_axis),
                   'RIGHT': (Vector((w, -d / 2.0, 0.0)), x_axis)}
        facing = {'FRONT': "Front"}
        if getattr(self, '_is_island_double', False):
            facing['BACK'] = "Back"
        z_dim = cage_obj.location.z + units.inch(1.0)
        unit_settings = context.scene.unit_settings
        specs = []
        for side, (local, normal) in centers.items():
            entry = clearances.get(side)
            prefix = facing.get(side, "")
            if entry is None:
                if prefix:
                    # No obstacle in reach: short marker so the facing
                    # still reads.
                    s = mw @ local
                    e = s + normal * units.inch(18.0)
                    s.z = e.z = z_dim
                    specs.append(hb_placement.PlacementDimSpec(
                        s, e, prefix, None))
                continue
            dist, label = entry
            s = mw @ local
            e = s + normal * dist
            s.z = e.z = z_dim
            text = units.unit_to_string(unit_settings, dist)
            if prefix:
                text = f"{prefix} {text}"
            if side == self._active_clearance_side:
                text = f"> {text} <"
            color = _SNAP_GREEN if side in self._detent_hit else None
            specs.append(hb_placement.PlacementDimSpec(s, e, text, color))
        return specs

    def _handle_island_arrow(self, context, step):
        """Left/Right arrow while placing an island: cycle the active
        clearance side and start typing its distance."""
        idx = _ISLAND_SIDES.index(self._active_clearance_side)
        self._active_clearance_side = _ISLAND_SIDES[(idx + step)
                                                    % len(_ISLAND_SIDES)]
        entry = (self._last_clearances or {}).get(
            self._active_clearance_side)
        anchor_clear = entry[0] if entry else None
        self._clearance_anchor = (
            self._preview_cage.obj.location.copy(), anchor_clear)
        if self.placement_state == hb_placement.PlacementState.TYPING:
            self.typed_value = ""
            self.typing_target = hb_placement.TypingTarget.OFFSET_X
        else:
            self.start_typing(hb_placement.TypingTarget.OFFSET_X)
        self._position_free(context)
        self._update_header(context)

    def _apply_island_clearance(self, context, value):
        """Move the island along the active side's normal so that
        side's clearance equals the typed value, measured from the
        typing-anchor position (so live keystrokes don't compound)."""
        if self._clearance_anchor is None:
            return
        anchor_loc, anchor_clear = self._clearance_anchor
        if anchor_clear is None:
            return
        cage_obj = self._preview_cage.obj
        cage_obj.location = anchor_loc.copy()
        mw = cage_obj.matrix_world
        x_axis = (mw.to_3x3() @ Vector((1.0, 0.0, 0.0))).normalized()
        y_axis = (mw.to_3x3() @ Vector((0.0, 1.0, 0.0))).normalized()
        normals = {'FRONT': -y_axis, 'BACK': y_axis,
                   'LEFT': -x_axis, 'RIGHT': x_axis}
        normal = normals[self._active_clearance_side]
        delta = anchor_clear - value
        move = normal * delta
        cage_obj.location.x += move.x
        cage_obj.location.y += move.y
        # Refresh dims without re-reading the cursor.
        self._placement_dim_specs = self._placement_dim_specs[:1]
        self._placement_dim_specs += self._island_clearance_dims(context)
        if context.area is not None:
            context.area.tag_redraw()

    def _build_dim_specs_on_wall(self, context, wall, wall_thickness,
                                 gap_start, gap_end, placement_x, width):
        """Total width 4" above the cage top; left/right gap offsets 8"
        above. Snap green flags an engaged edge/center snap."""
        cage_obj = self._preview_cage.obj
        z_top = cage_obj.location.z + self._cabinet_height
        z_total = z_top + units.inch(4.0)
        z_offset = z_top + units.inch(8.0)
        y_dim = (-units.inch(2.0) if self._place_on_front
                 else wall_thickness + units.inch(2.0))
        wm = wall.matrix_world
        unit_settings = context.scene.unit_settings
        specs = []

        total_color = _SNAP_GREEN if self._gap_snap else None
        offset_color = _SNAP_GREEN if self._gap_snap == 'CENTER' else None
        s = wm @ Vector((placement_x, y_dim, z_total))
        e = wm @ Vector((placement_x + width, y_dim, z_total))
        specs.append(hb_placement.PlacementDimSpec(
            s, e, units.unit_to_string(unit_settings, width), total_color))

        left_offset = placement_x - gap_start
        if left_offset > units.inch(0.5):
            s = wm @ Vector((gap_start, y_dim, z_offset))
            e = wm @ Vector((placement_x, y_dim, z_offset))
            specs.append(hb_placement.PlacementDimSpec(
                s, e, units.unit_to_string(unit_settings, left_offset),
                offset_color))

        right_offset = gap_end - (placement_x + width)
        if right_offset > units.inch(0.5):
            s = wm @ Vector((placement_x + width, y_dim, z_offset))
            e = wm @ Vector((gap_end, y_dim, z_offset))
            specs.append(hb_placement.PlacementDimSpec(
                s, e, units.unit_to_string(unit_settings, right_offset),
                offset_color))
        return specs

    # ---------------- header ----------------

    def _update_header(self, context):
        title = (f"{self.starter_name} Starter" if self._source_obj is None
                 else ("Duplicate Mirror " if self.mirror else "Duplicate ")
                 + self._source_obj.name)
        bay_label = f"{self.bay_qty} bay" + ("" if self.bay_qty == 1 else "s")
        mode = "auto" if self._auto_bay_qty else "manual"
        width_str = units.unit_to_string(
            context.scene.unit_settings, self._cabinet_width)
        if self.placement_state == hb_placement.PlacementState.TYPING:
            typed = self.get_typed_display_string()
            label = {
                hb_placement.TypingTarget.WIDTH: "Width",
                hb_placement.TypingTarget.OFFSET_X: "Offset (left)",
                hb_placement.TypingTarget.OFFSET_RIGHT: "Offset (right)",
            }.get(self.typing_target, "Value")
            if (getattr(self, '_is_island', False)
                    and self._gap_wall is None
                    and self.typing_target
                    == hb_placement.TypingTarget.OFFSET_X):
                side = self._active_clearance_side.title()
                label = f"Clearance ({side})"
            hb_placement.draw_header_text(
                context,
                f"{title}  -  {label}: {typed}  -  "
                "Enter: apply   Esc: cancel typing   Backspace: delete")
        else:
            hb_placement.draw_header_text(
                context,
                f"{title}  -  {bay_label} ({mode})  -  "
                f"width: {width_str}  -  "
                + ("F: fill gap   " if self._source_obj is not None else "")
                + "W/numbers: width   Up/Down: bays   Left/Right: gap offset   "
                "R: rotate   Click: place   Esc: cancel")

    # ---------------- modal ----------------

    def modal(self, context, event):
        if self._preview_cage is None:
            return self._cancel(context)

        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}

        if self.placement_state == hb_placement.PlacementState.TYPING:
            if self.handle_typing_event(event):
                self._update_header(context)
                return {'RUNNING_MODAL'}

        if (event.type == 'W' and event.value == 'PRESS'
                and self.placement_state == hb_placement.PlacementState.PLACING):
            self.start_typing(hb_placement.TypingTarget.WIDTH)
            self._update_header(context)
            return {'RUNNING_MODAL'}

        if (event.type == 'R' and event.value == 'PRESS'
                and self.placement_state == hb_placement.PlacementState.PLACING):
            self._free_rotation_z = (
                self._free_rotation_z + math.radians(90)) % math.radians(360)
            self._position_from_hit(context)
            self._update_header(context)
            return {'RUNNING_MODAL'}

        # 'F' (duplicate mode only) toggles fill-the-gap. The copy
        # starts at the source's width; F stretches it to the wall
        # gap (bay count pinned - the copied bays widen), F again
        # restores the source width.
        if (event.type == 'F' and event.value == 'PRESS'
                and self._source_obj is not None
                and not getattr(self, '_is_corner', False)
                and self.placement_state == hb_placement.PlacementState.PLACING):
            if self._fill_mode:
                self._apply_width(self._source_obj.hb_closet_starter.width,
                                  fill_mode=False)
            else:
                self._fill_mode = True
                if self.hit_location is not None:
                    self._position_from_hit(context)
            self._update_header(context)
            return {'RUNNING_MODAL'}

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
            new_qty = min(self.bay_qty + 1, _BAY_QTY_MAX)
            if new_qty != self.bay_qty:
                self.bay_qty = new_qty
                self._auto_bay_qty = False
                self._update_cage()
                self._update_header(context)
            return {'RUNNING_MODAL'}

        if event.type == 'DOWN_ARROW' and event.value == 'PRESS':
            new_qty = max(self.bay_qty - 1, _BAY_QTY_MIN)
            if new_qty != self.bay_qty:
                self.bay_qty = new_qty
                self._auto_bay_qty = False
                self._update_cage()
                self._update_header(context)
            return {'RUNNING_MODAL'}

        if event.type == 'LEFT_ARROW' and event.value == 'PRESS':
            if self._gap_wall is not None:
                self._handle_offset_arrow(context, side='LEFT')
            elif getattr(self, '_is_island', False):
                self._handle_island_arrow(context, step=-1)
            return {'RUNNING_MODAL'}

        if event.type == 'RIGHT_ARROW' and event.value == 'PRESS':
            if self._gap_wall is not None:
                self._handle_offset_arrow(context, side='RIGHT')
            elif getattr(self, '_is_island', False):
                self._handle_island_arrow(context, step=1)
            return {'RUNNING_MODAL'}

        if event.type == 'MOUSEMOVE':
            if (self.placement_state == hb_placement.PlacementState.TYPING
                    and self.typing_target in (
                        hb_placement.TypingTarget.OFFSET_X,
                        hb_placement.TypingTarget.OFFSET_RIGHT)):
                return {'RUNNING_MODAL'}
            self._suppress_detents = event.shift
            cage_obj = self._preview_cage.obj
            cage_obj.hide_set(True)
            try:
                self.update_snap(context, event)
            finally:
                cage_obj.hide_set(False)
            self._position_from_hit(context)

        return {'RUNNING_MODAL'}

    # ---------------- commit ----------------

    def _finalize(self, context):
        """Capture the cage transform, delete it, build the real starter
        there, and push the placed width through the prop update path."""
        self.remove_placement_dim_handler()
        cage_obj = self._preview_cage.obj
        captured_parent = cage_obj.parent
        captured_world = cage_obj.matrix_world.copy()
        captured_local_loc = cage_obj.location.copy()
        captured_local_rot = cage_obj.rotation_euler.copy()
        captured_width = self._cabinet_width
        captured_bay_qty = self.bay_qty
        self._delete_preview()

        if self._source_obj is not None:
            return self._finalize_duplicate(
                context, captured_parent, captured_world,
                captured_local_loc, captured_local_rot, captured_width)

        cls = types_closets.get_starter_class(self.starter_name)
        try:
            starter = cls()
            starter.create_starter(f"{self.starter_name} Closet",
                                   captured_bay_qty)
        except Exception as e:
            self.report({'ERROR'}, f"Starter creation failed: {e}")
            hb_placement.clear_header_text(context)
            return {'CANCELLED'}

        root = starter.obj
        if captured_parent is not None:
            root.parent = captured_parent
            root.matrix_parent_inverse.identity()
            root.location = captured_local_loc
            root.rotation_euler = captured_local_rot
        else:
            root.matrix_world = captured_world

        # Resize through the update callback so the solver relays out.
        root.hb_closet_starter.width = captured_width

        _apply_finish(root)

        for o in context.selected_objects:
            o.select_set(False)
        root.select_set(True)
        context.view_layer.objects.active = root
        _apply_selection_shading(context, root)

        # Adjacent perpendicular closets at this wall's corners: pop the
        # clearance dialog so the user sets the access gap + bridge
        # shelves per occupied end (face_frame's blind-corner flow; one
        # dialog covers both ends when the closet fills the wall between
        # two neighbors). Corner L units resolve the corner themselves -
        # skip. Silent when nothing qualifies: placement just finishes.
        if not getattr(self, '_is_corner', False):
            matches = _detect_corner_closet_neighbor(root)
            if matches:
                kwargs = {'closet_name': root.name}
                for neighbor, placed_end, gap in matches:
                    k = placed_end.lower()
                    kwargs[f'has_{k}'] = True
                    kwargs[f'neighbor_{k}'] = neighbor.name
                    kwargs[f'gap_{k}'] = gap
                try:
                    bpy.ops.hb_closets.set_corner_clearance(
                        'INVOKE_DEFAULT', **kwargs)
                except RuntimeError:
                    pass

        hb_placement.clear_header_text(context)
        context.window.cursor_set('DEFAULT')
        width_str = units.unit_to_string(
            context.scene.unit_settings, captured_width)
        self.report({'INFO'},
                    f"Placed {self.starter_name} starter ({width_str})")
        return {'FINISHED'}

    def _finalize_duplicate(self, context, captured_parent, captured_world,
                            captured_local_loc, captured_local_rot,
                            captured_width):
        """Commit for duplicate mode: deep-copy the source hierarchy at
        the cage transform, keeping every bay config and finish (the
        fresh-build path - create_starter + _apply_finish - is
        skipped). Only the position-driven corner-clearance dialog
        still runs."""
        src = self._source_obj
        if src is None or src.name not in bpy.data.objects:
            self.report({'ERROR'}, "Source starter no longer exists")
            hb_placement.clear_header_text(context)
            context.window.cursor_set('DEFAULT')
            return {'CANCELLED'}

        try:
            root = hb_placement.duplicate_object_hierarchy(context, src)
        except Exception:
            root = None
        if root is None:
            self.report({'ERROR'}, "Duplicate failed")
            hb_placement.clear_header_text(context)
            context.window.cursor_set('DEFAULT')
            return {'CANCELLED'}

        if captured_parent is not None:
            root.parent = captured_parent
            root.matrix_parent_inverse.identity()
            root.location = captured_local_loc
            root.rotation_euler = captured_local_rot
        else:
            root.parent = None
            root.matrix_world = captured_world

        # Mirror before the width push so the fill recalc lays out the
        # already-flipped bay order. Both steps ride the one solve at
        # the end of the block.
        with types_closets.suspend_recalc():
            if self.mirror:
                _mirror_starter_config(root)

            # Fill-the-gap commit: push the gap width through the prop
            # update path so the copied bays stretch proportionally.
            if abs(captured_width - root.hb_closet_starter.width) > 1e-5:
                root.hb_closet_starter.width = captured_width

        for o in context.selected_objects:
            o.select_set(False)
        root.select_set(True)
        context.view_layer.objects.active = root
        _apply_selection_shading(context, root)

        # Same corner handling as a fresh placement - driven by the
        # drop position, not by how the starter was built.
        if not getattr(self, '_is_corner', False):
            matches = _detect_corner_closet_neighbor(root)
            if matches:
                kwargs = {'closet_name': root.name}
                for neighbor, placed_end, gap in matches:
                    k = placed_end.lower()
                    kwargs[f'has_{k}'] = True
                    kwargs[f'neighbor_{k}'] = neighbor.name
                    kwargs[f'gap_{k}'] = gap
                try:
                    bpy.ops.hb_closets.set_corner_clearance(
                        'INVOKE_DEFAULT', **kwargs)
                except RuntimeError:
                    pass

        hb_placement.clear_header_text(context)
        context.window.cursor_set('DEFAULT')
        self.report({'INFO'},
                    ("Duplicated (mirrored) " if self.mirror
                     else "Duplicated ") + src.name)
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Bay insert / delete
# ---------------------------------------------------------------------------
class hb_closets_OT_insert_bay(bpy.types.Operator):
    """Insert a bay next to the active bay."""
    bl_idname = "hb_closets.insert_bay"
    bl_label = "Insert Closet Bay"
    bl_options = {'UNDO'}

    direction: bpy.props.EnumProperty(
        name="Direction",
        items=[('BEFORE', "Left", "Insert to the left of this bay"),
               ('AFTER', "Right", "Insert to the right of this bay")],
        default='AFTER')  # type: ignore

    @classmethod
    def poll(cls, context):
        return types_closets.find_bay_cage(context.active_object) is not None

    def execute(self, context):
        bay = types_closets.find_bay_cage(context.active_object)
        root = types_closets.find_starter_root(bay)
        if bay is None or root is None:
            return {'CANCELLED'}
        starter = types_closets._wrap_starter(root)
        new_bay = starter.insert_bay(bay.get('hb_bay_index', 0),
                                     self.direction)
        if new_bay is not None:
            _apply_finish(root)
            _apply_selection_shading(context, root)
        return {'FINISHED'}


class hb_closets_OT_delete_bay(bpy.types.Operator):
    """Delete the active bay (the remaining bays absorb its width)."""
    bl_idname = "hb_closets.delete_bay"
    bl_label = "Delete Closet Bay"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return types_closets.find_bay_cage(context.active_object) is not None

    def execute(self, context):
        bay = types_closets.find_bay_cage(context.active_object)
        root = types_closets.find_starter_root(bay)
        if bay is None or root is None:
            return {'CANCELLED'}
        n_bays = sum(1 for c in root.children
                     if c.get(types_closets.TAG_BAY_CAGE))
        if n_bays <= 1:
            # Deleting the only bay would leave an empty shell, so the
            # command degrades to deleting the starter (same path as
            # the right-click Delete Starter command).
            name = root.name
            types_closets.delete_starter(root)
            self.report({'INFO'}, f"Deleted starter {name}")
            return {'FINISHED'}
        starter = types_closets._wrap_starter(root)
        if not starter.delete_bay(bay.get('hb_bay_index', 0)):
            self.report({'WARNING'}, "A starter needs at least one bay")
            return {'CANCELLED'}
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Interior parts
# ---------------------------------------------------------------------------
class hb_closets_OT_add_part(bpy.types.Operator,
                             hb_placement.PlacementMixin):
    """Modal add-part: hover an opening to preview the part at the cursor
    height (snapped), GPU dims show the clearances below/above, click to
    place and keep adding, Right-click or Esc to finish."""
    bl_idname = "hb_closets.add_part"
    bl_label = "Add Closet Part"
    bl_options = {'UNDO'}

    part_type: bpy.props.EnumProperty(
        name="Part Type",
        items=[('FIXED_SHELF', "Fixed Shelf", "Fixed shelf at a set height"),
               ('ROD', "Closet Rod", "Closet rod at a set height")],
        default='FIXED_SHELF')  # type: ignore

    _preview = None
    _opening = None

    def _make_preview(self, opening):
        from .. import const_closets as const
        if self.part_type == 'ROD':
            obj = types_closets.add_rod(opening, const.ROD_TOP_OFFSET)
        else:
            obj = types_closets.add_fixed_shelf(opening, 0.0)
        # Previews are invisible to the split reconciler; the flag comes
        # off on commit, which is when a fixed shelf splits its opening.
        obj['hb_preview'] = 1
        return obj

    def _drop_preview(self):
        if self._preview is not None:
            try:
                # Tree remove: a preview part may have grown children
                # (rod hangers) that a bare remove would strand.
                types_closets._remove_part_tree(self._preview)
            except ReferenceError:
                pass
        self._preview = None
        self._opening = None

    def _opening_interior_h(self, opening):
        try:
            return hb_types.GeoNodeCage(opening).get_input('Dim Z')
        except Exception:
            return 0.0

    def _resolve_opening_under_cursor(self, context):
        """(opening, local_z, interior_h) for the opening under the mouse.

        Closet interiors are open-backed, so a scene raycast usually
        sails THROUGH an opening and hits the wall/floor behind it (and
        in Starters mode the highlighted root cage eats the hit) - so
        don't depend on geometry at all: intersect the mouse ray with
        every opening cage's user-facing plane (front face; y=0 face for
        a double island's BACK openings) and take the nearest hit that
        lands inside the opening rectangle."""
        from bpy_extras import view3d_utils
        from ...face_frame import split_preview
        region = self.region
        rv3d = region.data if region is not None else None
        if rv3d is None or self.mouse_pos is None:
            return None
        origin = view3d_utils.region_2d_to_origin_3d(
            region, rv3d, self.mouse_pos)
        direction = view3d_utils.region_2d_to_vector_3d(
            region, rv3d, self.mouse_pos)
        best = None
        for obj in context.scene.objects:
            if not obj.get(types_closets.TAG_OPENING_CAGE):
                continue
            try:
                cage = hb_types.GeoNodeCage(obj)
                o_w = cage.get_input('Dim X')
                o_d = cage.get_input('Dim Y')
                o_h = cage.get_input('Dim Z')
            except Exception:
                continue
            if o_w <= 0.0 or o_h <= 0.0:
                continue
            inv = split_preview._world_matrix(obj).inverted()
            o_l = inv @ origin
            d_l = inv.to_3x3() @ direction
            if abs(d_l.y) < 1e-8:
                continue
            side = obj.get(types_closets.PROP_OPENING_SIDE, 'FRONT')
            plane_y = 0.0 if side == 'BACK' else -o_d
            t = (plane_y - o_l.y) / d_l.y
            if t <= 0.0:
                continue
            p = o_l + d_l * t
            if -0.001 <= p.x <= o_w + 0.001 and -0.001 <= p.z <= o_h + 0.001:
                if best is None or t < best[0]:
                    best = (t, obj, p.z, o_h)
        if best is None:
            return None
        return best[1], best[2], best[3]

    def _update_preview(self, context):
        """Move the preview into the opening under the cursor at the
        cursor's opening-local height, then relay the starter out so the
        preview part sizes itself like a committed part."""
        from .. import const_closets as const
        resolved = self._resolve_opening_under_cursor(context)
        if resolved is None:
            return
        opening, local_z, _interior = resolved
        if opening is not self._opening:
            root_prev = (types_closets.find_starter_root(self._opening)
                         if self._opening else None)
            self._drop_preview()
            self._preview = self._make_preview(opening)
            self._opening = opening
            if root_prev is not None:
                types_closets.recalculate_closet_starter(root_prev)

        interior_h = self._opening_interior_h(opening)
        # 32mm system: shelf/rod locations land on system holes. The
        # hole lattice is defined from the BAY interior bottom, so add
        # the segment offset before snapping and remove it after -
        # holes stay aligned across split segments.
        seg_bottom = opening.get('hb_seg_bottom', 0.0)
        z = const.snap_system_hole(seg_bottom + local_z) - seg_bottom
        z = max(0.0, min(z, interior_h))
        if self.part_type == 'ROD':
            # Stored as distance from the opening top (rods ride the top).
            self._preview['hb_z_offset'] = float(interior_h - z)
            self._preview['hb_anchor_top'] = 1
        else:
            self._preview['hb_z_offset'] = float(z)
            self._preview['hb_anchor_top'] = 0

        root = types_closets.find_starter_root(opening)
        if root is not None:
            types_closets.recalculate_closet_starter(root)

        # Clearance dims: below (opening bottom -> part) and above
        # (part -> opening top) at the front of the opening.
        wm = opening.matrix_world
        try:
            depth = hb_types.GeoNodeCage(opening).get_input('Dim Y')
        except Exception:
            depth = 0.0
        x_dim = units.inch(2.0)
        y_dim = -depth - units.inch(1.0)
        z_part = self._preview.location.z
        unit_settings = context.scene.unit_settings
        specs = []
        if z_part > units.inch(0.5):
            specs.append(hb_placement.PlacementDimSpec(
                wm @ Vector((x_dim, y_dim, 0.0)),
                wm @ Vector((x_dim, y_dim, z_part)),
                units.unit_to_string(unit_settings, z_part), None))
        if interior_h - z_part > units.inch(0.5):
            specs.append(hb_placement.PlacementDimSpec(
                wm @ Vector((x_dim, y_dim, z_part)),
                wm @ Vector((x_dim, y_dim, interior_h)),
                units.unit_to_string(unit_settings, interior_h - z_part),
                None))
        self._placement_dim_specs = specs
        if context.area is not None:
            context.area.tag_redraw()

    def invoke(self, context, event):
        self.init_placement(context)
        if self.region is None:
            self.report({'WARNING'}, "No 3D viewport available")
            return {'CANCELLED'}
        self.add_placement_dim_handler(context)
        label = ("fixed shelf" if self.part_type == 'FIXED_SHELF'
                 else "closet rod")
        hb_placement.draw_header_text(
            context,
            f"Add {label}: hover an opening, click to place "
            "(keeps adding), Right-click/Esc to finish")
        context.window.cursor_set('CROSSHAIR')
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def _finish(self, context, keep_last):
        if not keep_last:
            root = (types_closets.find_starter_root(self._opening)
                    if self._opening else None)
            self._drop_preview()
            if root is not None:
                types_closets.recalculate_closet_starter(root)
        self.remove_placement_dim_handler()
        hb_placement.clear_header_text(context)
        context.window.cursor_set('DEFAULT')
        return {'FINISHED'} if keep_last else {'CANCELLED'}

    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}

        if event.type == 'MOUSEMOVE':
            # Plane-based resolution only needs the mouse position; no
            # raycast, so no hide/unhide dance around the preview.
            self.mouse_pos = Vector((event.mouse_region_x,
                                     event.mouse_region_y))
            self._update_preview(context)
            return {'RUNNING_MODAL'}

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if self._preview is not None and self._opening is not None:
                # Commit: the preview IS the part. Clearing the preview
                # flag lets the reconciler adopt a fixed shelf as a
                # SPLITTER on the recalc below (the opening divides into
                # two segments). Then start a fresh preview to keep adding.
                committed_opening = self._opening
                if 'hb_preview' in self._preview:
                    del self._preview['hb_preview']
                root = types_closets.find_starter_root(committed_opening)
                if root is not None and self.part_type != 'ROD':
                    _apply_finish(root)
                if root is not None:
                    types_closets.recalculate_closet_starter(root)
                _apply_selection_shading(context, root, keep_active=False)
                self._preview = self._make_preview(committed_opening)
                if root is not None:
                    types_closets.recalculate_closet_starter(root)
            return {'RUNNING_MODAL'}

        if event.type in {'RIGHTMOUSE', 'ESC'} and event.value == 'PRESS':
            return self._finish(context, keep_last=False)

        if hb_snap.event_is_pass_through(event):
            return {'PASS_THROUGH'}

        return {'RUNNING_MODAL'}


class hb_closets_OT_add_adj_shelves(bpy.types.Operator):
    """Set the adjustable shelf count for the active opening (shelves
    space themselves evenly)."""
    bl_idname = "hb_closets.add_adj_shelves"
    bl_label = "Adjustable Shelves"
    bl_options = {'UNDO'}

    qty: bpy.props.IntProperty(name="Shelf Quantity", default=3,
                               min=0, max=20)  # type: ignore

    @classmethod
    def poll(cls, context):
        return types_closets.find_opening_cage(context.active_object) is not None

    def invoke(self, context, event):
        opening = types_closets.find_opening_cage(context.active_object)
        # Default to the computed count for this opening's height; keep
        # an existing user setting if the opening already has shelves.
        existing = int(opening.hb_closet_opening.adj_shelf_qty)
        self.qty = existing or types_closets.default_adj_shelf_qty(opening)
        return context.window_manager.invoke_props_dialog(self, width=250)

    def execute(self, context):
        opening = types_closets.find_opening_cage(context.active_object)
        if opening is None:
            return {'CANCELLED'}
        opening.hb_closet_opening.adj_shelf_qty = self.qty
        root = types_closets.find_starter_root(opening)
        types_closets.recalculate_closet_starter(root)
        _apply_finish(root)
        _apply_selection_shading(context, root)
        return {'FINISHED'}


def _opening_for_insert(obj):
    """Resolve the opening an insert/config command targets from one
    object. On double islands a bay has FRONT and BACK openings - prefer
    the one obj lives under, falling back to the FRONT opening."""
    opening = types_closets.find_opening_cage(obj)
    if opening is not None and not obj.get(types_closets.TAG_BAY_CAGE):
        return opening
    bay = types_closets.find_bay_cage(obj)
    if bay is None:
        return opening
    openings = [c for c in bay.children
                if c.get(types_closets.TAG_OPENING_CAGE)]
    for c in openings:
        if c.get(types_closets.PROP_OPENING_SIDE, 'FRONT') == 'FRONT':
            return c
    return openings[0] if openings else opening


def _active_opening_for_insert(context):
    return _opening_for_insert(context.active_object)


def _selection_pool(context):
    """Selected objects + the active object (a right-click menu command
    runs on the active object, but shift-selected cages stay selected)."""
    pool = list(context.selected_objects)
    active = context.active_object
    if active is not None and active not in pool:
        pool.append(active)
    return pool


def _selected_openings(context):
    """Distinct target openings across the whole selection, so a config
    command applies to every shift-selected opening (or bay), not just
    the active one."""
    openings = []
    for obj in _selection_pool(context):
        opening = _opening_for_insert(obj)
        if opening is not None and opening not in openings:
            openings.append(opening)
    return openings


def _selected_bays(context):
    """Distinct bay cages across the whole selection (any selected
    object under a bay maps to that bay)."""
    bays = []
    for obj in _selection_pool(context):
        bay = types_closets.find_bay_cage(obj)
        if bay is not None and bay not in bays:
            bays.append(bay)
    return bays


def _reselect_cages(context, cages):
    """Restore a multi-cage selection after the shading pass
    (toggle_mode deselects everything). A config change can rebuild
    segment cages, so dead references are skipped."""
    for o in list(context.selected_objects):
        o.select_set(False)
    alive = []
    for cage in cages:
        try:
            cage.select_set(True)
            alive.append(cage)
        except (ReferenceError, RuntimeError):
            continue
    if alive:
        context.view_layer.objects.active = alive[0]


class _ClosetInsertDialog:
    """Shared plumbing for the opening-config insert dialogs."""

    @classmethod
    def poll(cls, context):
        return types_closets.find_opening_cage(context.active_object) is not None

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=250)

    def _commit(self, context, values):
        """Write a dialog's settings onto the active opening and redraw.

        Keys are field names on the opening's settings group, so a
        subclass names what it is setting rather than reaching for a
        storage key."""
        opening = _active_opening_for_insert(context)
        if opening is None:
            return {'CANCELLED'}
        for name, value in values.items():
            setattr(opening.hb_closet_opening, name, value)
        root = types_closets.find_starter_root(opening)
        types_closets.recalculate_closet_starter(root)
        _apply_finish(root)
        _apply_selection_shading(context, root)
        return {'FINISHED'}


class hb_closets_OT_add_drawers(_ClosetInsertDialog, bpy.types.Operator):
    """Set the drawer stack for the active opening (fronts stack from
    the bottom; each drawer gets a box behind its front)."""
    bl_idname = "hb_closets.add_drawers"
    bl_label = "Drawers"
    bl_options = {'UNDO'}

    qty: bpy.props.IntProperty(name="Drawer Quantity", default=3,
                               min=0, max=10)  # type: ignore
    front_height: bpy.props.FloatProperty(
        name="Front Height", default=0.1905,  # 7.5"
        unit='LENGTH', precision=4)  # type: ignore
    drawer_box: bpy.props.EnumProperty(
        name="Drawer Box",
        items=_DRAWER_BOX_OVERRIDE_ITEMS,
        default='DEFAULT')  # type: ignore

    def invoke(self, context, event):
        opening = _active_opening_for_insert(context)
        if opening is not None:
            op = opening.hb_closet_opening
            self.qty = int(op.drawer_qty) or 3
            self.front_height = float(op.drawer_front_height)
            self.drawer_box = op.drawer_box_override or 'DEFAULT'
        return context.window_manager.invoke_props_dialog(self, width=250)

    def execute(self, context):
        from .. import const_closets as const
        opening = _active_opening_for_insert(context)
        if opening is None:
            return {'CANCELLED'}
        opening.hb_closet_opening.drawer_qty = self.qty
        opening.hb_closet_opening.drawer_front_height = self.front_height
        # 'Use Default' clears the per-opening override so the box system
        # follows the project setting again.
        if self.drawer_box and self.drawer_box != 'DEFAULT':
            opening.hb_closet_opening.drawer_box_override = self.drawer_box
        else:
            opening.hb_closet_opening.property_unset('drawer_box_override')
        root = types_closets.find_starter_root(opening)
        bay = types_closets.find_bay_cage(opening)

        # A drawer bank comes in capped by a fixed shelf (shop
        # convention). The cap's underside sits so the top drawer front
        # half-overlays it: qty*(front_h + gap) - shelf_thickness in
        # opening-local Z. If this segment is already capped, MOVE the
        # cap to match the new stack instead of stacking another shelf.
        if self.qty > 0 and bay is not None:
            st = context.scene.hb_closets.shelf_thickness
            cap_z_local = self.qty * (self.front_height
                                      + const.FRONT_GAP) - st
            seg_bottom = opening.get('hb_seg_bottom', 0.0)
            side = opening.get(types_closets.PROP_OPENING_SIDE, 'FRONT')
            shelves = sorted(
                [c for c in bay.children
                 if c.get('hb_part_role')
                 == types_closets.PART_ROLE_FIXED_SHELF
                 and c.get(types_closets.PROP_OPENING_SIDE,
                           'FRONT') == side
                 and not c.get('hb_preview')],
                key=lambda o: o.get('hb_z_offset', 0.0))
            cap = next((sh for sh in shelves
                        if sh.get('hb_z_offset', 0.0)
                        >= seg_bottom - 1e-6), None)
            if cap is not None:
                cap['hb_z_offset'] = float(seg_bottom + cap_z_local)
            else:
                types_closets.add_fixed_shelf(opening, cap_z_local)

        types_closets.recalculate_closet_starter(root)
        _apply_finish(root)
        _apply_selection_shading(context, root)
        return {'FINISHED'}


_BOX_LABELS = {b[0]: b[1] for b in drawer_boxes_closets.BOX_TYPES}


def _box_size_names(tag):
    """(height name, length name) parsed from a box size tag such as
    'H251 L350'. WOOD/NONE map to a plain readout."""
    if not tag or tag in ('NONE', ''):
        return ('None', 'None')
    if tag == 'WOOD':
        return ('Wood', 'Wood')
    height_name = length_name = ""
    for part in str(tag).split():
        if part.startswith('H'):
            height_name = part[1:]
        elif part.startswith('L'):
            length_name = part[1:]
    return (height_name or '-', length_name or '-')


class hb_closets_OT_drawer_accessory(bpy.types.Operator):
    """Drawer Options for the selected drawer front: the current box
    system and its size names, a per-drawer box-system and size override,
    and a fitted jewelry tray."""
    bl_idname = "hb_closets.drawer_accessory"
    bl_label = "Drawer Options"
    bl_options = {'UNDO'}

    box_override: bpy.props.EnumProperty(
        name="Override Drawer Type",
        items=_DRAWER_BOX_OVERRIDE_ITEMS,
        default='DEFAULT')  # type: ignore
    override_depth: bpy.props.FloatProperty(
        name="Depth", default=0.0, min=0.0,
        unit='LENGTH', precision=4,
        description="Force the box depth (0 = system size)")  # type: ignore
    override_height: bpy.props.FloatProperty(
        name="Height", default=0.0, min=0.0,
        unit='LENGTH', precision=4,
        description="Force the box height (0 = system size)")  # type: ignore
    jewelry_tray: bpy.props.EnumProperty(
        name="Jewelry Tray",
        items=types_closets.JEWELRY_TRAY_COLOR_ITEMS,
        default='NONE')  # type: ignore
    resize_to_fit: bpy.props.BoolProperty(
        name="Resize drawer to fit tray",
        description="Adjust this drawer's width so the tray fits",
        default=False)  # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj is not None and obj.get('hb_part_role')
                == types_closets.PART_ROLE_DRAWER_FRONT)

    def _front(self, context):
        obj = context.active_object
        if (obj is not None and obj.get('hb_part_role')
                == types_closets.PART_ROLE_DRAWER_FRONT):
            return obj
        return None

    def invoke(self, context, event):
        front = self._front(context)
        if front is not None:
            self.box_override = (
                front.get(types_closets.PROP_FRONT_BOX_OVERRIDE, '')
                or 'DEFAULT')
            self.override_depth = float(
                front.get(types_closets.PROP_BOX_DEPTH_OVERRIDE, 0.0))
            self.override_height = float(
                front.get(types_closets.PROP_BOX_HEIGHT_OVERRIDE, 0.0))
            self.jewelry_tray = (
                front.get(types_closets.PROP_JEWELRY_TRAY, '') or 'NONE')
        return context.window_manager.invoke_props_dialog(self, width=320)

    def draw(self, context):
        layout = self.layout
        front = self._front(context)

        box = layout.box()
        if front is not None:
            resolved = front.get(types_closets.PROP_BOX_TYPE_RESOLVED, '')
            row = box.row()
            row.label(text="Current Drawer:")
            row.label(text=_BOX_LABELS.get(resolved, "-"))
        row = box.row()
        row.label(text="Override Drawer Type:")
        row.prop(self, 'box_override', text="")
        row = box.row(align=True)
        row.label(text="Override Size:")
        row.prop(self, 'override_depth')
        row.prop(self, 'override_height')
        if front is not None:
            h_name, l_name = _box_size_names(
                front.get(types_closets.PROP_BOX_SIZE_TAG, ''))
            row = box.row()
            row.label(text="Height Name:")
            row.label(text=h_name)
            row = box.row()
            row.label(text="Length Name:")
            row.label(text=l_name)
            open_h_mm = round(
                float(front.get(types_closets.PROP_OPEN_HEIGHT, 0.0))
                / 0.001, 1)
            row = box.row()
            row.label(text="Opening Height:")
            row.label(text=str(open_h_mm) + " mm")

        box = layout.box()
        row = box.row()
        row.label(text="Jewelry Tray:")
        row.prop(self, 'jewelry_tray', text="")
        if front is not None and self.jewelry_tray != 'NONE':
            inside = float(front.get('hb_inside_w', 0.0))
            depth = float(front.get('hb_open_depth', 0.0))
            name = types_closets.jewelry_tray_name(
                self.jewelry_tray, inside, depth)
            if name:
                box.label(text="Tray: " + name)
            else:
                box.label(text="Drawer size not valid for this tray.",
                          icon='ERROR')
                box.prop(self, 'resize_to_fit')

    def _write_front(self, front):
        """Store the dialog's overrides and tray choice on the front,
        clearing each when it is left at its default."""
        # Box-system override (Use Default clears it).
        if self.box_override and self.box_override != 'DEFAULT':
            front[types_closets.PROP_FRONT_BOX_OVERRIDE] = self.box_override
        elif types_closets.PROP_FRONT_BOX_OVERRIDE in front:
            del front[types_closets.PROP_FRONT_BOX_OVERRIDE]
        # Size overrides (0 clears them).
        if self.override_depth > 0.0:
            front[types_closets.PROP_BOX_DEPTH_OVERRIDE] = self.override_depth
        elif types_closets.PROP_BOX_DEPTH_OVERRIDE in front:
            del front[types_closets.PROP_BOX_DEPTH_OVERRIDE]
        if self.override_height > 0.0:
            front[types_closets.PROP_BOX_HEIGHT_OVERRIDE] = self.override_height
        elif types_closets.PROP_BOX_HEIGHT_OVERRIDE in front:
            del front[types_closets.PROP_BOX_HEIGHT_OVERRIDE]
        # Jewelry tray.
        if self.jewelry_tray and self.jewelry_tray != 'NONE':
            front[types_closets.PROP_JEWELRY_TRAY] = self.jewelry_tray
        elif types_closets.PROP_JEWELRY_TRAY in front:
            del front[types_closets.PROP_JEWELRY_TRAY]

    def check(self, context):
        """Live re-solve: apply the current choices and rebuild so the
        readouts (current drawer, size names, tray) update as edited."""
        front = self._front(context)
        if front is None:
            return False
        self._write_front(front)
        root = types_closets.find_starter_root(front)
        if root is not None:
            types_closets.recalculate_closet_starter(root)
        return True

    def execute(self, context):
        front = self._front(context)
        if front is None:
            return {'CANCELLED'}
        self._write_front(front)
        root = types_closets.find_starter_root(front)
        if root is not None:
            types_closets.recalculate_closet_starter(root)
            # A drawer too small/large for the tray can size itself to fit.
            if self.resize_to_fit:
                types_closets.resize_for_jewelry_tray(front)
            _apply_finish(root)
            _apply_selection_shading(context, root)
        return {'FINISHED'}


class hb_closets_OT_resize_drawer_for_tray(bpy.types.Operator):
    """Resize the selected drawer's width so its assigned jewelry tray
    fits. A single-bay closet grows overall; a multi-bay closet resizes
    just this bay and lets the others redistribute."""
    bl_idname = "hb_closets.resize_drawer_for_tray"
    bl_label = "Resize Drawer to Fit Tray"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj is not None
                and obj.get('hb_part_role')
                == types_closets.PART_ROLE_DRAWER_FRONT
                and bool(obj.get(types_closets.PROP_JEWELRY_TRAY, '')))

    def execute(self, context):
        front = context.active_object
        changed = types_closets.resize_for_jewelry_tray(front)
        root = types_closets.find_starter_root(front)
        if root is not None:
            _apply_finish(root)
            _apply_selection_shading(context, root)
        if not changed:
            self.report({'INFO'}, "Drawer already fits the tray.")
        return {'FINISHED'}


class hb_closets_OT_add_doors(_ClosetInsertDialog, bpy.types.Operator):
    """Add a door front to the active opening. No dialog - the menu
    entries bake the swing (left / right / double) and the hamper flag;
    picking a different entry replaces the existing fronts. Delete Part
    on a door removes it."""
    bl_idname = "hb_closets.add_doors"
    bl_label = "Add Door"
    bl_options = {'UNDO'}

    swing: bpy.props.EnumProperty(
        name="Swing",
        items=[('NONE', "None", "Remove doors"),
               ('LEFT', "Left", "Single door hinged left"),
               ('RIGHT', "Right", "Single door hinged right"),
               ('DOUBLE', "Double", "Pair of doors"),
               ('LIFT_UP', "Lift Up", "Single top-hinged lift-up door")],
        default='LEFT')  # type: ignore
    is_hamper: bpy.props.BoolProperty(
        name="Hamper (tilt-out)", default=False)  # type: ignore

    def invoke(self, context, event):
        # Direct action, no dialog (menu entries carry the props).
        return self.execute(context)

    def execute(self, context):
        swing = '' if self.swing == 'NONE' else self.swing
        obj = context.active_object
        # Right-clicked a BAY cage -> doors span the whole bay; an
        # OPENING cage -> doors scope to that opening (segment).
        if obj is not None and obj.get(types_closets.TAG_BAY_CAGE):
            bay = types_closets.find_bay_cage(obj)
            root = types_closets.find_starter_root(bay)
            if bay is None or root is None:
                return {'CANCELLED'}
            # The bay's front relays the run out itself, so the whole
            # write burst is held to the one solve at the end.
            with types_closets.suspend_recalc():
                bp = bay.hb_closet_bay
                bp.door_swing = swing
                bp.is_hamper = bool(self.is_hamper)
                # Bay-wide doors supersede opening doors on the front
                # side; door openings get default adjustable shelves
                # behind them (seed_door_shelves skips occupied ones).
                for op in bay.children:
                    if (op.get(types_closets.TAG_OPENING_CAGE)
                            and op.get(types_closets.PROP_OPENING_SIDE,
                                       'FRONT') == 'FRONT'):
                        op.hb_closet_opening.door_swing = ''
                        if swing and not self.is_hamper:
                            types_closets.seed_door_shelves(op)
                types_closets.recalculate_closet_starter(root)
            _apply_finish(root)
            _apply_selection_shading(context, root)
            return {'FINISHED'}
        # Door openings get default adjustable shelves behind them
        # (skipped for hampers and occupied openings).
        if swing and not self.is_hamper:
            opening = _active_opening_for_insert(context)
            if opening is not None:
                types_closets.seed_door_shelves(opening)
        return self._commit(context, {
            'door_swing': swing,
            'is_hamper': self.is_hamper,
        })


class hb_closets_OT_add_cubbies(_ClosetInsertDialog, bpy.types.Operator):
    """Set the cubby grid for the active opening (1x1 removes it)."""
    bl_idname = "hb_closets.add_cubbies"
    bl_label = "Cubbies"
    bl_options = {'UNDO'}

    cols: bpy.props.IntProperty(name="Columns", default=3, min=1, max=12)  # type: ignore
    rows: bpy.props.IntProperty(name="Rows", default=3, min=1, max=12)  # type: ignore

    def invoke(self, context, event):
        opening = _active_opening_for_insert(context)
        if opening is not None:
            op = opening.hb_closet_opening
            # One by one is no grid at all, so the dialog opens on the
            # standard 3x3 rather than showing the empty state back.
            if op.cubby_cols > 1 or op.cubby_rows > 1:
                self.cols = int(op.cubby_cols)
                self.rows = int(op.cubby_rows)
            else:
                self.cols = 3
                self.rows = 3
        return context.window_manager.invoke_props_dialog(self, width=250)

    def execute(self, context):
        return self._commit(context, {
            'cubby_cols': self.cols,
            'cubby_rows': self.rows,
        })


class hb_closets_OT_add_rollouts(_ClosetInsertDialog, bpy.types.Operator):
    """Set the pull-out (rollout) trays for the active opening. Each tray
    stands the given Rollout Height; the trays are spaced evenly (0
    quantity removes them)."""
    bl_idname = "hb_closets.add_rollouts"
    bl_label = "Rollout Trays"
    bl_options = {'UNDO'}

    qty: bpy.props.IntProperty(name="Quantity", default=3,
                               min=0, max=12)  # type: ignore
    rollout_height: bpy.props.FloatProperty(
        name="Rollout Height", default=0.1016,  # 4"
        unit='LENGTH', precision=4)  # type: ignore

    def invoke(self, context, event):
        from .. import const_closets as const
        opening = _active_opening_for_insert(context)
        if opening is not None:
            op = opening.hb_closet_opening
            self.qty = int(op.rollout_qty) or const.ROLLOUT_DEFAULT_QTY
            self.rollout_height = float(op.rollout_height)
        return context.window_manager.invoke_props_dialog(self, width=250)

    def execute(self, context):
        return self._commit(context, {
            'rollout_qty': self.qty,
            'rollout_height': self.rollout_height,
        })


class hb_closets_OT_add_slanted_shelves(_ClosetInsertDialog,
                                        bpy.types.Operator):
    """Set the slanted shoe shelves for the active opening: a stack of
    tilted shelves, each with a metal shoe fence across the front (0
    quantity removes them)."""
    bl_idname = "hb_closets.add_slanted_shelves"
    bl_label = "Slanted Shoe Shelves"
    bl_options = {'UNDO'}

    qty: bpy.props.IntProperty(name="Shelf Quantity", default=4,
                               min=0, max=10)  # type: ignore
    spacing: bpy.props.FloatProperty(
        name="Distance Between Shelves", default=0.2032,  # 8"
        unit='LENGTH', precision=4)  # type: ignore
    angle: bpy.props.FloatProperty(
        name="Shelf Angle", default=math.radians(17.25),
        subtype='ANGLE', unit='ROTATION')  # type: ignore
    color: bpy.props.EnumProperty(
        name="Fence Color",
        items=types_closets.SHOE_FENCE_COLOR_ITEMS,
        default=types_closets.SHOE_FENCE_COLORS[0])  # type: ignore

    def invoke(self, context, event):
        from .. import const_closets as const
        opening = _active_opening_for_insert(context)
        if opening is not None:
            op = opening.hb_closet_opening
            self.qty = int(op.slant_qty) or const.SLANT_SHELF_DEFAULT_QTY
            self.spacing = float(op.slant_spacing)
            self.angle = float(op.slant_angle)
            self.color = types_closets.shoe_fence_color(op.slant_color)
        return context.window_manager.invoke_props_dialog(self, width=280)

    def execute(self, context):
        return self._commit(context, {
            'slant_qty': self.qty,
            'slant_spacing': self.spacing,
            'slant_angle': self.angle,
            'slant_color': self.color,
        })


class hb_closets_OT_change_bay(bpy.types.Operator):
    """Rebuild every selected bay as a standard configuration (clears
    the bays' current contents first). Shift-select several bays to
    change them all at once; anything selected under a bay counts."""
    bl_idname = "hb_closets.change_bay"
    bl_label = "Bay Configuration"
    bl_options = {'UNDO'}

    config: bpy.props.EnumProperty(
        name="Configuration",
        items=[(cid, label, "") for cid, label in types_closets.BAY_CONFIGS],
        default='ADJ_SHELVES')  # type: ignore

    @classmethod
    def poll(cls, context):
        return types_closets.find_bay_cage(context.active_object) is not None

    def execute(self, context):
        bays = _selected_bays(context)
        if not bays:
            return {'CANCELLED'}
        applied = 0
        roots = []
        for bay in bays:
            try:
                if not types_closets.apply_bay_config(bay, self.config):
                    continue
            except ReferenceError:
                # An earlier apply rebuilt this cage out from under us.
                continue
            applied += 1
            root = types_closets.find_starter_root(bay)
            if root is not None and root not in roots:
                roots.append(root)
        if not applied:
            return {'CANCELLED'}
        for root in roots:
            _apply_finish(root)
            _apply_selection_shading(context, root)
        _reselect_cages(context, bays)
        if applied > 1:
            self.report({'INFO'}, f"Changed {applied} bays")
        return {'FINISHED'}


# Clipboards for copy/paste of bay & opening contents (survive object
# deletion; a copy persists until overwritten so it can paste to many).
_bay_clipboard = None
_opening_clipboard = None


class hb_closets_OT_copy_bay(bpy.types.Operator):
    """Copy all contents of the active bay to the clipboard, to paste
    onto other bays."""
    bl_idname = "hb_closets.copy_bay"
    bl_label = "Copy Bay"

    @classmethod
    def poll(cls, context):
        return types_closets.find_bay_cage(context.active_object) is not None

    def execute(self, context):
        global _bay_clipboard
        bay = types_closets.find_bay_cage(context.active_object)
        if bay is None:
            return {'CANCELLED'}
        _bay_clipboard = types_closets.serialize_bay(bay)
        self.report({'INFO'}, "Bay contents copied")
        return {'FINISHED'}


class hb_closets_OT_paste_bay(bpy.types.Operator):
    """Replace the active bay's contents with the copied bay."""
    bl_idname = "hb_closets.paste_bay"
    bl_label = "Paste Bay"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return (_bay_clipboard is not None
                and types_closets.find_bay_cage(context.active_object)
                is not None)

    def execute(self, context):
        bay = types_closets.find_bay_cage(context.active_object)
        root = types_closets.find_starter_root(bay)
        if bay is None or not types_closets.apply_bay_data(
                bay, _bay_clipboard):
            return {'CANCELLED'}
        _apply_finish(root)
        _apply_selection_shading(context, root)
        return {'FINISHED'}


class hb_closets_OT_copy_opening(bpy.types.Operator):
    """Copy the active opening's contents to the clipboard."""
    bl_idname = "hb_closets.copy_opening"
    bl_label = "Copy Opening"

    @classmethod
    def poll(cls, context):
        return (types_closets.find_opening_cage(context.active_object)
                is not None)

    def execute(self, context):
        global _opening_clipboard
        opening = _active_opening_for_insert(context)
        if opening is None:
            return {'CANCELLED'}
        _opening_clipboard = types_closets.serialize_opening(opening)
        self.report({'INFO'}, "Opening contents copied")
        return {'FINISHED'}


class hb_closets_OT_paste_opening(bpy.types.Operator):
    """Replace the active opening's contents with the copied opening."""
    bl_idname = "hb_closets.paste_opening"
    bl_label = "Paste Opening"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return (_opening_clipboard is not None
                and types_closets.find_opening_cage(context.active_object)
                is not None)

    def execute(self, context):
        opening = _active_opening_for_insert(context)
        if opening is None:
            return {'CANCELLED'}
        root = types_closets.find_starter_root(opening)
        types_closets.apply_opening_data(opening, _opening_clipboard)
        _apply_finish(root)
        _apply_selection_shading(context, root)
        return {'FINISHED'}


class hb_closets_OT_change_opening(bpy.types.Operator):
    """Swap every selected opening to a standard configuration (clears
    their current contents first). Shift-select several openings to
    change them all at once."""
    bl_idname = "hb_closets.change_opening"
    bl_label = "Change Opening"
    bl_options = {'UNDO'}

    config: bpy.props.EnumProperty(
        name="Configuration",
        items=[(cid, label, "")
               for cid, label in types_closets.OPENING_CONFIGS],
        default='ADJ_SHELVES')  # type: ignore

    @classmethod
    def poll(cls, context):
        return (types_closets.find_opening_cage(context.active_object)
                is not None)

    def execute(self, context):
        openings = _selected_openings(context)
        if not openings:
            return {'CANCELLED'}
        applied = 0
        roots = []
        for opening in openings:
            try:
                if not types_closets.apply_opening_config(
                        opening, self.config):
                    continue
            except ReferenceError:
                # An earlier apply re-segmented this cage away.
                continue
            applied += 1
            root = types_closets.find_starter_root(opening)
            if root is not None and root not in roots:
                roots.append(root)
        if not applied:
            return {'CANCELLED'}
        for root in roots:
            _apply_finish(root)
            _apply_selection_shading(context, root)
        _reselect_cages(context, openings)
        if applied > 1:
            self.report({'INFO'}, f"Changed {applied} openings")
        return {'FINISHED'}


class hb_closets_OT_clear_opening(bpy.types.Operator):
    """Remove all contents of the active opening (shelves stay - they
    are bay structure; use Clear Bay to remove those too)."""
    bl_idname = "hb_closets.clear_opening"
    bl_label = "Clear Opening"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return types_closets.find_opening_cage(context.active_object) is not None

    def execute(self, context):
        opening = _active_opening_for_insert(context)
        if opening is None:
            return {'CANCELLED'}
        root = types_closets.find_starter_root(opening)
        types_closets.clear_opening_contents(opening)
        types_closets.recalculate_closet_starter(root)
        _apply_selection_shading(context, root)
        return {'FINISHED'}


class hb_closets_OT_clear_bay(bpy.types.Operator):
    """Remove all contents of the active bay, including its splitting
    fixed shelves - the bay merges back to one open section."""
    bl_idname = "hb_closets.clear_bay"
    bl_label = "Clear Bay"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return types_closets.find_bay_cage(context.active_object) is not None

    def execute(self, context):
        bay = types_closets.find_bay_cage(context.active_object)
        if bay is None:
            return {'CANCELLED'}
        root = types_closets.find_starter_root(bay)
        types_closets.clear_bay_contents(bay)
        types_closets.recalculate_closet_starter(root)
        _apply_selection_shading(context, root)
        return {'FINISHED'}


class hb_closets_OT_adj_shelf_step(bpy.types.Operator):
    """Add or remove one adjustable shelf from the opening of the active
    adjustable shelf (right-click on a shelf). Re-spaces the rest."""
    bl_idname = "hb_closets.adj_shelf_step"
    bl_label = "Adjustable Shelf"
    bl_options = {'UNDO'}

    delta: bpy.props.IntProperty(default=1)  # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj is not None and obj.get('hb_part_role')
                == types_closets.PART_ROLE_ADJ_SHELF)

    def execute(self, context):
        obj = context.active_object
        opening = types_closets.find_opening_cage(obj)
        root = types_closets.find_starter_root(obj)
        if opening is None or root is None:
            return {'CANCELLED'}
        qty = int(opening.hb_closet_opening.adj_shelf_qty)
        opening.hb_closet_opening.adj_shelf_qty = max(0, qty + self.delta)
        types_closets.recalculate_closet_starter(root)
        _apply_finish(root)
        _apply_selection_shading(context, root)
        return {'FINISHED'}


class hb_closets_OT_delete_part(bpy.types.Operator):
    """Delete the active interior part. Config-driven parts (adjustable
    shelves, drawers, doors, cubby parts) decrement their opening's
    config instead of fighting the regenerator."""
    bl_idname = "hb_closets.delete_part"
    bl_label = "Delete Closet Part"
    bl_options = {'UNDO'}

    PART_ROLES = {types_closets.PART_ROLE_FIXED_SHELF,
                  types_closets.PART_ROLE_ADJ_SHELF,
                  types_closets.PART_ROLE_ROD,
                  types_closets.PART_ROLE_DOOR,
                  types_closets.PART_ROLE_DRAWER_FRONT,
                  types_closets.PART_ROLE_CUBBY_DIVISION,
                  types_closets.PART_ROLE_CUBBY_SHELF}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.get('hb_part_role') in cls.PART_ROLES

    def execute(self, context):
        obj = context.active_object
        role = obj.get('hb_part_role')
        root = types_closets.find_starter_root(obj)
        # A bay-wide door lives on the bay cage; clearing its config
        # removes it (the reconciler drops the part on recalc).
        if role == types_closets.PART_ROLE_DOOR and obj.get('hb_bay_door'):
            bay = types_closets.find_bay_cage(obj)
            with types_closets.suspend_recalc():
                if bay is not None:
                    bay.hb_closet_bay.door_swing = ''
                if root is not None:
                    types_closets.recalculate_closet_starter(root)
            return {'FINISHED'}
        opening = types_closets.find_opening_cage(obj)
        remove_obj = True

        if opening is not None:
            tcm = types_closets
            if role == tcm.PART_ROLE_ADJ_SHELF:
                qty = int(opening.hb_closet_opening.adj_shelf_qty)
                opening.hb_closet_opening.adj_shelf_qty = max(0, qty - 1)
            elif role == tcm.PART_ROLE_DRAWER_FRONT:
                # The regenerator removes the highest-index front AND its
                # box; let it own the removal.
                qty = int(opening.hb_closet_opening.drawer_qty)
                opening.hb_closet_opening.drawer_qty = max(0, qty - 1)
                remove_obj = False
            elif role == tcm.PART_ROLE_DOOR:
                opening.hb_closet_opening.door_swing = ''
                remove_obj = False
            elif role == tcm.PART_ROLE_CUBBY_DIVISION:
                cols = int(opening.hb_closet_opening.cubby_cols)
                opening.hb_closet_opening.cubby_cols = max(1, cols - 1)
                remove_obj = False
            elif role == tcm.PART_ROLE_CUBBY_SHELF:
                rows = int(opening.hb_closet_opening.cubby_rows)
                opening.hb_closet_opening.cubby_rows = max(1, rows - 1)
                remove_obj = False

        if remove_obj:
            # Tree remove: rods carry hanger children (a bare remove
            # would strand them at the world origin).
            types_closets._remove_part_tree(obj)
        if root is not None:
            types_closets.recalculate_closet_starter(root)
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Delete starter + properties popups
# ---------------------------------------------------------------------------
class hb_closets_OT_delete_starter(bpy.types.Operator):
    """Delete every closet starter currently selected."""
    bl_idname = "hb_closets.delete_starter"
    bl_label = "Delete Closet Starter"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return types_closets.find_starter_root(context.active_object) is not None

    def execute(self, context):
        roots = set()
        for obj in context.selected_objects:
            root = types_closets.find_starter_root(obj)
            if root is not None:
                roots.add(root)
        for root in roots:
            types_closets.delete_starter(root)
        return {'FINISHED'}


def _set_enum_silent(pgroup, prop_name, identifier):
    """Set an enum on a PropertyGroup without firing its update
    callback (writes the underlying value directly). Used to make a
    dropdown reflect a distance that was set some other way."""
    items = pgroup.bl_rna.properties[prop_name].enum_items
    item = items.get(identifier)
    if item is not None:
        pgroup[prop_name] = item.value


def _sync_height_dropdown(pgroup):
    """Point a height dropdown at the standard height matching the
    current distance, or Custom when it sits off the standard steps."""
    key = const.nearest_panel_height_key(pgroup.height) or 'CUSTOM'
    _set_enum_silent(pgroup, 'height_preset', key)


def _starter_bays(root):
    return sorted([c for c in root.children
                   if c.get(types_closets.TAG_BAY_CAGE)],
                  key=lambda o: o.get('hb_bay_index', 0))


# How much of a per-bay row the option name takes, leaving the rest for
# the checkboxes.
_BAY_GRID_LABEL = 0.35


def _bay_grid(box, bays, rows):
    """The per-bay options as one grid: bay numbers across the top once,
    then a single row per option with its checkboxes lining up under the
    numbers.

    Each entry in `rows` is (prop_name, label, first_bay, last_bay).
    Bays outside first_bay..last_bay get a blank instead of a checkbox,
    which is how an option that belongs to a junction rather than to a
    bay is shown: a four bay run has three junctions, so it offers three
    checkboxes under the bays that own them.

    Every row is an even-column grid one column per bay, and each cell
    centers what it holds, so a checkbox lands under the middle of its
    bay number. Both halves matter: a plain row hands each cell only as
    much width as its contents need, so a row that blanks a cell - the
    junction options do - would space its checkboxes differently from
    the row above it."""
    col = box.column(align=True)

    def _cells(parent):
        return parent.grid_flow(row_major=True, columns=len(bays),
                                even_columns=True, align=True)

    header = col.split(factor=_BAY_GRID_LABEL)
    header.label(text="")
    numbers = _cells(header)
    for bay in bays:
        cell = numbers.row()
        cell.alignment = 'CENTER'
        cell.label(text=str(bay.hb_closet_bay.bay_index + 1))
    for prop_name, label, first_bay, last_bay in rows:
        split = col.split(factor=_BAY_GRID_LABEL)
        split.label(text=label)
        cells = _cells(split)
        for bay in bays:
            bp = bay.hb_closet_bay
            cell = cells.row()
            cell.alignment = 'CENTER'
            if (bp.bay_index < first_bay
                    or (last_bay is not None and bp.bay_index > last_bay)):
                cell.label(text="")
            else:
                cell.prop(bp, prop_name, text="")


def _locked_field(parent, bp, attr, unlock_attr, text=""):
    """One size field and its padlock, drawn the way the face frame
    library draws them: the field is quiet while the run owns the value
    and the padlock reads closed; clicking it hands the value to this
    bay, and the field opens for typing. Returns the row so a caller can
    keep filling it."""
    unlocked = getattr(bp, unlock_attr)
    cell = parent.row(align=True)
    field = cell.row(align=True)
    field.enabled = unlocked
    field.prop(bp, attr, text=text)
    cell.prop(bp, unlock_attr, text="",
              icon='UNLOCKED' if unlocked else 'LOCKED')
    return cell


def _section(layout, sp, toggle, label):
    """A collapsible Construction section, folding the same way the face
    frame library folds its option groups: click the header to open or
    close it. Returns the box to fill, or None when it is closed."""
    box = layout.box()
    box.prop(sp, toggle, text=label,
             icon='TRIA_DOWN' if getattr(sp, toggle) else 'TRIA_RIGHT',
             emboss=False)
    return box if getattr(sp, toggle) else None


class hb_closets_OT_starter_prompts(bpy.types.Operator):
    """Edit the active starter's sizes and options."""
    bl_idname = "hb_closets.starter_prompts"
    bl_label = "Closet Starter Properties"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return types_closets.find_starter_root(context.active_object) is not None

    def invoke(self, context, event):
        root = types_closets.find_starter_root(context.active_object)
        if root is not None:
            sp = root.hb_closet_starter
            _sync_height_dropdown(sp)
            for bay in _starter_bays(root):
                _sync_height_dropdown(bay.hb_closet_bay)
        return context.window_manager.invoke_props_dialog(self, width=560)

    # -- tab bodies ---------------------------------------------------
    def _draw_sizes(self, layout, root, sp, bays, is_corner):
        if is_corner:
            box = layout.box()
            box.label(text="Corner")
            col = box.column(align=True)
            col.prop(sp, 'l_left_depth')
            col.prop(sp, 'l_right_depth')
            col.prop(sp, 'l_shelf_qty')
            col = box.column(align=True)
            col.prop(sp, 'l_back_width')
            col.prop(sp, 'l_flip_partition')
            col = box.column(align=True)
            col.prop(sp, 'l_use_radius')
            sub = col.column(align=True)
            sub.enabled = sp.l_use_radius
            sub.prop(sp, 'l_corner_radius')
        if not bays:
            return
        box = layout.box()
        box.label(text="Bays")
        row = box.row(align=True)
        row.label(text="Bay")
        row.label(text="Width")
        row.label(text="Height")
        row.label(text="Depth")
        row.label(text="Mounting")
        for bay in bays:
            bp = bay.hb_closet_bay
            row = box.row(align=True)
            row.label(text=str(bp.bay_index + 1))
            # All three sizes read the same way: the field is quiet
            # while the run owns the value, and the padlock hands it to
            # this bay. A bay holding its own width keeps it while the
            # rest of the run is redistributed to fill the run width; a
            # bay holding its own height or depth keeps that while the
            # run size changes.
            _locked_field(row, bp, 'width', 'unlock_width')
            _locked_field(row, bp, 'height', 'unlock_height')
            _locked_field(row, bp, 'depth', 'unlock_depth')
            row.prop(bp, 'floor_mounted', toggle=True,
                     text="Floor" if bp.floor_mounted else "Hanging",
                     icon=('TRIA_DOWN_BAR' if bp.floor_mounted
                           else 'TRIA_UP_BAR'))

    def _draw_construction(self, layout, root, sp, bays, cls, is_corner):
        box = _section(layout, sp, 'show_toe_kick', "Toe Kick")
        if box is not None:
            col = box.column(align=True)
            col.prop(sp, 'toe_kick_height_preset')
            if sp.toe_kick_height_preset == 'CUSTOM':
                col.prop(sp, 'toe_kick_height')
            col.prop(sp, 'toe_kick_setback')

        if not is_corner:
            box = _section(layout, sp, 'show_ends', "Ends")
            if box is not None:
                row = box.row()
                for side, cap in (('left', "Left"), ('right', "Right")):
                    col = row.column(align=True)
                    col.label(text=cap)
                    col.prop(sp, f'{side}_side_wall_filler',
                             text="Wall Filler")
                    col.prop(sp, f'include_batten_{side}', text="Batten")
                    col.separator()
                    col.prop(sp, f'turn_off_{side}_panel',
                             text="Turn Off Panel")
                    col.prop(sp, f'{side}_finished_end', text="Finished End")
                    col.prop(sp, f'drill_through_{side}',
                             text="Drill Through")
                    col.separator()
                    col.prop(sp, f'bridge_{side}', text="Bridge")
                    sub = col.column(align=True)
                    sub.enabled = getattr(sp, f'bridge_{side}')
                    sub.prop(sp, f'bridge_{side}_width', text="Shelf Width")
                    sub.prop(sp, f'include_bottom_bridge_{side}',
                             text="Bottom Bridge")

            box = _section(layout, sp, 'show_top', "Top")
            if box is not None:
                col = box.column(align=True)
                col.prop(sp, 'add_top_accent_shelf')
                sub = col.column(align=True)
                sub.enabled = sp.add_top_accent_shelf
                sub.prop(sp, 'top_accent_overhang')

            if getattr(cls, 'has_hang_rail', False):
                box = _section(layout, sp, 'show_hang_rail', "Hang Rail")
                if box is not None:
                    col = box.column(align=True)
                    col.prop(sp, 'remove_hang_rail')
                    sub = col.column(align=True)
                    sub.enabled = not sp.remove_hang_rail
                    row = sub.row(align=True)
                    row.prop(sp, 'extend_hang_rail_left', text="Extend Left")
                    row.prop(sp, 'extend_hang_rail_right',
                             text="Extend Right")
                    sub.prop(sp, 'use_one_hang_rail_height')
                    row = sub.row(align=True)
                    row.enabled = sp.use_one_hang_rail_height
                    row.prop(sp, 'hang_rail_height_location')

        if getattr(cls, 'has_applied_back', False):
            box = _section(layout, sp, 'show_applied_back', "Applied Back")
            if box is not None:
                col = box.column(align=True)
                col.prop(sp, 'back_to_floor')
                col.prop(sp, 'applied_back_overlay')

        # Both insets act on parts a floor bay has and a hanging bay does
        # not, so say so rather than letting them read as run-wide.
        box = _section(layout, sp, 'show_insets', "Insets")
        if box is not None:
            col = box.column(align=True)
            col.prop(sp, 'inset_bottom')
            col.prop(sp, 'inset_cleat')
            box.label(text="Floor bays only", icon='INFO')

        # The extension drops hanging panels past the bottom of their
        # section so they finish alongside whatever sits below - every
        # panel, not just the ends. It only reaches hanging panels, which
        # is why it lives here rather than with the countertop.
        box = _section(layout, sp, 'show_panels', "Panels")
        if box is not None:
            sub = box.column(align=True)
            sub.prop(sp, 'extend_panels_to_countertop')
            row = sub.row(align=True)
            row.enabled = sp.extend_panels_to_countertop
            row.prop(sp, 'extend_panel_amount')

        if bays:
            box = _section(layout, sp, 'show_per_bay', "Per Bay")
            if box is not None:
                rows = [('remove_bottom', "Remove Bottom", 0, None),
                        ('remove_cleat', "Remove Cleat", 0, None)]
                # A double panel stands at a junction between two bays,
                # so the last bay has none to offer.
                if len(bays) > 1:
                    rows.append(('double_panel_right', "Double Panel",
                                 0, len(bays) - 2))
                _bay_grid(box, bays, rows)

    def _draw_countertop(self, layout, root, sp):
        layout.prop(sp, 'include_countertop')
        col = layout.column()
        col.enabled = sp.include_countertop

        box = col.box()
        box.label(text="Countertop")
        sub = box.column(align=True)
        sub.prop(sp, 'countertop_thickness')
        sub = box.column(align=True)
        sub.label(text="Overhang")
        row = sub.row(align=True)
        row.prop(sp, 'countertop_overhang_front')
        row.prop(sp, 'countertop_overhang_rear')
        row = sub.row(align=True)
        row.prop(sp, 'countertop_overhang_left')
        row.prop(sp, 'countertop_overhang_right')
        sub = box.column(align=True)
        row = sub.row(align=True)
        row.prop(sp, 'countertop_left_finished_end', text="Left Finished End")
        row.prop(sp, 'countertop_right_finished_end',
                 text="Right Finished End")

        box = col.box()
        box.label(text="Backsplash")
        sub = box.column(align=True)
        sub.prop(sp, 'include_backsplash')
        row = sub.row(align=True)
        row.enabled = sp.include_backsplash
        row.prop(sp, 'backsplash_height')

    def draw(self, context):
        layout = self.layout
        root = types_closets.find_starter_root(context.active_object)
        if root is None:
            return
        sp = root.hb_closet_starter
        cls = types_closets.WRAP_CLASS_REGISTRY.get(
            root.get('CLASS_NAME', ''), types_closets.ClosetStarter)
        is_corner = getattr(cls, 'is_corner', False)
        bays = _starter_bays(root)

        # Overall size stays visible on every tab - it is what people
        # come here to change most often.
        box = layout.box()
        box.label(text=root.name, icon='OUTLINER_OB_LATTICE')
        col = box.column(align=True)
        col.prop(sp, 'width')
        # The run height and depth carry to every bay that has not been
        # handed one of its own. The Bays table is where a bay takes a
        # size over, and where it gives it back.
        col.prop(sp, 'height_preset', text="Height")
        if sp.height_preset == 'CUSTOM':
            col.prop(sp, 'height', text="Custom Height")
        col.prop(sp, 'depth')

        # A countertop belongs to a unit that has a top to sit on - a
        # base run or an island. A tall or hanging unit finishes at its
        # own top shelf, and a corner unit has no run to cap, so neither
        # is offered the tab at all.
        has_countertop = getattr(cls, 'has_countertop', False)
        row = layout.row(align=True)
        row.prop_enum(sp, 'prompt_tab', 'SIZES')
        row.prop_enum(sp, 'prompt_tab', 'CONSTRUCTION')
        if has_countertop:
            row.prop_enum(sp, 'prompt_tab', 'COUNTERTOP')

        tab = sp.prompt_tab
        if tab == 'COUNTERTOP' and not has_countertop:
            tab = 'SIZES'
        if tab == 'SIZES':
            self._draw_sizes(layout, root, sp, bays, is_corner)
        elif tab == 'CONSTRUCTION':
            self._draw_construction(layout, root, sp, bays, cls, is_corner)
        else:
            self._draw_countertop(layout, root, sp)

    def execute(self, context):
        return {'FINISHED'}


class hb_closets_OT_bay_prompts(bpy.types.Operator):
    """Edit the active bay's overrides (width/height/depth/mounting)."""
    bl_idname = "hb_closets.bay_prompts"
    bl_label = "Closet Bay Properties"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return types_closets.find_bay_cage(context.active_object) is not None

    def invoke(self, context, event):
        bay = types_closets.find_bay_cage(context.active_object)
        if bay is not None:
            _sync_height_dropdown(bay.hb_closet_bay)
        return context.window_manager.invoke_props_dialog(self, width=380)

    def draw(self, context):
        layout = self.layout
        bay = types_closets.find_bay_cage(context.active_object)
        if bay is None:
            return
        bp = bay.hb_closet_bay
        root = types_closets.find_starter_root(bay)
        sp = root.hb_closet_starter if root is not None else None
        bay_count = len(_starter_bays(root)) if root is not None else 1

        box = layout.box()
        box.label(text="Bay %d" % (bp.bay_index + 1), icon='MOD_ARRAY')
        col = box.column(align=True)
        _locked_field(col, bp, 'width', 'unlock_width', text="Width")
        # Height and depth follow the run until the padlock hands one of
        # them to this bay, so both stay quiet until it does. The custom
        # height only has somewhere to go once the bay owns its height.
        row = col.row(align=True)
        field = row.row(align=True)
        field.enabled = bp.unlock_height
        field.prop(bp, 'height_preset')
        row.prop(bp, 'unlock_height', text="",
                 icon='UNLOCKED' if bp.unlock_height else 'LOCKED')
        if bp.unlock_height and bp.height_preset == 'CUSTOM':
            col.prop(bp, 'height', text="Custom Height")
        _locked_field(col, bp, 'depth', 'unlock_depth', text="Depth")

        box = layout.box()
        box.label(text="Construction", icon='SNAP_VERTEX')
        col = box.column(align=True)
        col.prop(bp, 'floor_mounted',
                 text="Floor Mounted" if bp.floor_mounted else "Hanging",
                 icon=('TRIA_DOWN_BAR' if bp.floor_mounted
                       else 'TRIA_UP_BAR'))
        col.prop(bp, 'remove_bottom')
        col.prop(bp, 'remove_cleat')
        # A double panel splits the junction this bay shares with the bay
        # on its right, so the last bay has nothing to double up on.
        if bp.bay_index < bay_count - 1:
            col.prop(bp, 'double_panel_right')
        col.separator()
        # Stacks on top of the starter's run-wide Inset Bottom, and like
        # it only means anything where there is a bottom shelf to set in.
        sub = col.column(align=True)
        sub.enabled = bp.floor_mounted and not bp.remove_bottom
        sub.prop(bp, 'bottom_shelf_inset')

        # The center back divides a double-sided island's two faces, so
        # it is only meaningful there.
        cls = types_closets.WRAP_CLASS_REGISTRY.get(
            root.get('CLASS_NAME', '') if root is not None else '',
            types_closets.ClosetStarter)
        if getattr(cls, 'is_double', False):
            box = layout.box()
            box.label(text="Center Back", icon='MESH_PLANE')
            col = box.column(align=True)
            col.prop(bp, 'include_center_back')
            sub = col.column(align=True)
            sub.enabled = bp.include_center_back
            sub.prop(bp, 'center_back_location')

    def execute(self, context):
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Opening properties
# ---------------------------------------------------------------------------
# What an opening can be filled with. One choice at a time - picking a
# different one replaces what is there, the same way Change Opening does.
_OPENING_FILL_ITEMS = [
    ('NONE', "Empty", "Nothing in this opening"),
    ('ADJ_SHELVES', "Adjustable Shelves", "Evenly spaced adjustable shelves"),
    ('DRAWERS', "Drawers", "A stack of drawer fronts and boxes"),
    ('CUBBIES', "Cubbies", "A grid of divided cubby holes"),
    ('ROLLOUTS', "Rollout Trays", "Pull-out trays on slides"),
    ('SLANTED_SHELVES', "Slanted Shoe Shelves",
     "Tilted shelves with a shoe fence across the front"),
]


def _opening_rods(opening):
    """The hang rods hanging straight off an opening, lowest first."""
    return sorted(
        [c for c in opening.children
         if c.get('hb_part_role') == types_closets.PART_ROLE_ROD],
        key=lambda o: float(o.get('hb_z_offset', 0.0)))


def _single_top_rod(opening):
    """The one rod hanging from an opening's top, when that is all there
    is. A pair of rods comes from the bay's configuration and no single
    distance from the top describes both, so the dialog leaves that
    field off rather than writing one of them over the other."""
    rods = _opening_rods(opening)
    if len(rods) == 1 and rods[0].get('hb_anchor_top'):
        return rods[0]
    return None


def _opening_fill(opening):
    """Which of the standard fills currently occupies an opening."""
    if int(opening.hb_closet_opening.drawer_qty):
        return 'DRAWERS'
    if int(opening.hb_closet_opening.rollout_qty):
        return 'ROLLOUTS'
    if int(opening.hb_closet_opening.slant_qty):
        return 'SLANTED_SHELVES'
    if (int(opening.hb_closet_opening.cubby_cols) > 1
            or int(opening.hb_closet_opening.cubby_rows) > 1):
        return 'CUBBIES'
    if int(opening.hb_closet_opening.adj_shelf_qty):
        return 'ADJ_SHELVES'
    return 'NONE'


def _opening_dims(opening):
    """(width, depth, height) of an opening cage, zeros when the cage
    has no geometry node inputs yet."""
    try:
        cage = types_closets.GeoNodeCage(opening)
        return (cage.get_input('Dim X'), cage.get_input('Dim Y'),
                cage.get_input('Dim Z'))
    except Exception:
        return (0.0, 0.0, 0.0)


class hb_closets_OT_opening_prompts(bpy.types.Operator):
    """Edit what fills the active opening: its size readout, the interior
    (shelves / drawers / cubbies / trays / shoe shelves) with that
    interior's own settings, and the front on it."""
    bl_idname = "hb_closets.opening_prompts"
    bl_label = "Closet Opening Properties"
    bl_options = {'UNDO'}

    fill: bpy.props.EnumProperty(
        name="Interior", items=_OPENING_FILL_ITEMS,
        default='ADJ_SHELVES')  # type: ignore

    shelf_qty: bpy.props.IntProperty(
        name="Shelf Quantity",
        description="How many adjustable shelves to space through the "
                    "opening",
        default=3, min=0, max=20)  # type: ignore

    drawer_qty: bpy.props.IntProperty(
        name="Drawer Quantity",
        description="How many drawers to stack in the opening",
        default=3, min=1, max=10)  # type: ignore
    drawer_front_height: bpy.props.FloatProperty(
        name="Front Height",
        description="Height of each drawer front. The top drawer takes up "
                    "whatever height is left over",
        default=0.1905,  # 7.5"
        unit='LENGTH', precision=4)  # type: ignore
    drawer_box: bpy.props.EnumProperty(
        name="Drawer Box",
        description="Which drawer box to build instead of the one the "
                    "opening size would pick on its own",
        items=_DRAWER_BOX_OVERRIDE_ITEMS,
        default='DEFAULT')  # type: ignore

    cubby_cols: bpy.props.IntProperty(
        name="Columns", description="How many cubbies across the opening",
        default=3, min=1, max=12)  # type: ignore
    cubby_rows: bpy.props.IntProperty(
        name="Rows", description="How many cubbies up the opening",
        default=3, min=1, max=12)  # type: ignore
    cubby_setback: bpy.props.FloatProperty(
        name="Setback",
        description="How far the cubby divisions and shelves sit back "
                    "from the front edge of the opening",
        default=0.00635,  # 1/4"
        min=0.0, unit='LENGTH', precision=4)  # type: ignore

    rollout_qty: bpy.props.IntProperty(
        name="Quantity",
        description="How many pull-out trays to space through the opening",
        default=3, min=1, max=12)  # type: ignore
    rollout_height: bpy.props.FloatProperty(
        name="Rollout Height", description="Height of each tray",
        default=0.1016,  # 4"
        unit='LENGTH', precision=4)  # type: ignore

    slant_qty: bpy.props.IntProperty(
        name="Shelf Quantity",
        description="How many slanted shoe shelves to stack from the "
                    "bottom of the opening up",
        default=4, min=1, max=10)  # type: ignore
    slant_spacing: bpy.props.FloatProperty(
        name="Distance Between Shelves",
        description="Vertical spacing from one shoe shelf to the next",
        default=0.2032,  # 8"
        unit='LENGTH', precision=4)  # type: ignore
    slant_angle: bpy.props.FloatProperty(
        name="Shelf Angle",
        description="How far the shoe shelves tilt up toward the front",
        default=math.radians(17.25),
        subtype='ANGLE', unit='ROTATION')  # type: ignore
    slant_color: bpy.props.EnumProperty(
        name="Fence Color",
        description="Finish of the metal shoe fence across the front of "
                    "each shelf",
        items=types_closets.SHOE_FENCE_COLOR_ITEMS,
        default=types_closets.SHOE_FENCE_COLORS[0])  # type: ignore

    door_swing: bpy.props.EnumProperty(
        name="Door",
        items=[('NONE', "None", "No front on this opening"),
               ('LEFT', "Left Swing", "Single door hinged left"),
               ('RIGHT', "Right Swing", "Single door hinged right"),
               ('DOUBLE', "Double Door", "Pair of doors"),
               ('LIFT_UP', "Lift Up", "Single top-hinged lift-up door")],
        default='NONE')  # type: ignore
    is_hamper: bpy.props.BoolProperty(
        name="Tilt Out Hamper",
        description="Hang the front on a tilt-out hamper with a wire "
                    "basket behind it instead of a plain door",
        default=False)  # type: ignore

    rod_top_offset: bpy.props.FloatProperty(
        name="Rod Distance From Top",
        description="How far below the top of the opening the rod's "
                    "centerline hangs",
        default=0.0544830,  # 2.145"
        min=0.0, unit='LENGTH', precision=4)  # type: ignore
    rod_set_from_front: bpy.props.BoolProperty(
        name="Set Distance From Front",
        description="Measure the rod front to back from the front edge of "
                    "the opening instead of from the back",
        default=False)  # type: ignore
    rod_from_front: bpy.props.FloatProperty(
        name="Dim From Front",
        description="How far back from the front edge of the opening the "
                    "rod's centerline sits",
        default=0.0508,  # 2"
        min=0.0, unit='LENGTH', precision=4)  # type: ignore
    rod_from_rear: bpy.props.FloatProperty(
        name="Dim From Rear",
        description="How far out from the back of the opening the rod's "
                    "centerline sits",
        default=0.3048,  # 12"
        min=0.0, unit='LENGTH', precision=4)  # type: ignore
    rod_width_deduction: bpy.props.FloatProperty(
        name="Width Deduction",
        description="How much shorter than the opening the rod is cut, so "
                    "it drops into the cups at each end",
        default=0.00635,  # 1/4"
        min=0.0, unit='LENGTH', precision=4)  # type: ignore
    remove_hangers: bpy.props.BoolProperty(
        name="Remove Hangers",
        description="Leave the display hangers off the rods in this "
                    "opening",
        default=False)  # type: ignore

    @classmethod
    def poll(cls, context):
        return types_closets.find_opening_cage(
            context.active_object) is not None

    def invoke(self, context, event):
        from .. import const_closets as const
        opening = _active_opening_for_insert(context)
        if opening is None:
            return {'CANCELLED'}
        # An empty opening reads back as zero of everything. The dialog
        # opens on the quantity a user would want if they picked that
        # interior, so a zero falls back to the standard starting count;
        # nothing is written until they accept.
        op = opening.hb_closet_opening
        self.fill = _opening_fill(opening)
        self.shelf_qty = (int(op.adj_shelf_qty)
                          or types_closets.default_adj_shelf_qty(opening))
        self.drawer_qty = int(op.drawer_qty) or 3
        self.drawer_front_height = float(op.drawer_front_height)
        self.drawer_box = op.drawer_box_override or 'DEFAULT'
        if op.cubby_cols > 1 or op.cubby_rows > 1:
            self.cubby_cols = int(op.cubby_cols)
            self.cubby_rows = int(op.cubby_rows)
        else:
            self.cubby_cols = 3
            self.cubby_rows = 3
        self.cubby_setback = float(op.cubby_setback)
        self.rollout_qty = int(op.rollout_qty) or const.ROLLOUT_DEFAULT_QTY
        self.rollout_height = float(op.rollout_height)
        self.slant_qty = int(op.slant_qty) or const.SLANT_SHELF_DEFAULT_QTY
        self.slant_spacing = float(op.slant_spacing)
        self.slant_angle = float(op.slant_angle)
        self.slant_color = types_closets.shoe_fence_color(
            op.slant_color)
        self.door_swing = op.door_swing or 'NONE'
        self.is_hamper = bool(op.is_hamper)
        self.rod_set_from_front = bool(op.rod_set_from_front)
        self.rod_from_front = float(op.rod_from_front)
        self.rod_from_rear = float(op.rod_from_rear)
        self.rod_width_deduction = float(op.rod_width_deduction)
        self.remove_hangers = bool(op.remove_hangers)
        rod = _single_top_rod(opening)
        self.rod_top_offset = float(
            rod.get('hb_z_offset', const.ROD_TOP_OFFSET)
            if rod is not None else const.ROD_TOP_OFFSET)
        return context.window_manager.invoke_props_dialog(self, width=380)

    def draw(self, context):
        layout = self.layout
        opening = _active_opening_for_insert(context)
        if opening is None:
            return
        width, depth, height = _opening_dims(opening)

        # Size readout. An opening is the space between fixed shelves, so
        # its size is a result of the bay - move a shelf to change it.
        box = layout.box()
        box.label(text="Opening %d"
                       % (int(opening.get('hb_opening_index', 0)) + 1),
                  icon='MESH_PLANE')
        row = box.row(align=True)
        for label, value in (("Width", width), ("Height", height),
                             ("Depth", depth)):
            col = row.column(align=True)
            col.label(text=label)
            col.label(text=units.unit_to_string(
                context.scene.unit_settings, value))
        box.label(text="Sized by the bay and the shelves around it",
                  icon='INFO')

        box = layout.box()
        box.label(text="Interior", icon='SNAP_VOLUME')
        box.prop(self, 'fill', text="")
        col = box.column(align=True)
        if self.fill == 'ADJ_SHELVES':
            col.prop(self, 'shelf_qty')
        elif self.fill == 'DRAWERS':
            col.prop(self, 'drawer_qty')
            col.prop(self, 'drawer_front_height')
            col.prop(self, 'drawer_box')
        elif self.fill == 'CUBBIES':
            col.prop(self, 'cubby_cols')
            col.prop(self, 'cubby_rows')
            col.prop(self, 'cubby_setback')
        elif self.fill == 'ROLLOUTS':
            col.prop(self, 'rollout_qty')
            col.prop(self, 'rollout_height')
        elif self.fill == 'SLANTED_SHELVES':
            col.prop(self, 'slant_qty')
            col.prop(self, 'slant_spacing')
            col.prop(self, 'slant_angle')
            col.prop(self, 'slant_color')

        box = layout.box()
        box.label(text="Front", icon='MOD_SOLIDIFY')
        box.prop(self, 'door_swing', text="")
        sub = box.row()
        sub.enabled = self.door_swing != 'NONE'
        sub.prop(self, 'is_hamper')

        # Only worth showing once something is hanging in here. The rod
        # itself is added from the opening's menu or by the bay's
        # configuration; this is where it is dimensioned afterwards.
        if _opening_rods(opening):
            box = layout.box()
            box.label(text="Rod", icon='MESH_CYLINDER')
            col = box.column(align=True)
            if _single_top_rod(opening) is not None:
                col.prop(self, 'rod_top_offset')
            col.prop(self, 'rod_set_from_front')
            if self.rod_set_from_front:
                col.prop(self, 'rod_from_front')
            else:
                col.prop(self, 'rod_from_rear')
            col.prop(self, 'rod_width_deduction')
            col.prop(self, 'remove_hangers')

    def execute(self, context):
        opening = _active_opening_for_insert(context)
        if opening is None:
            return {'CANCELLED'}
        root = types_closets.find_starter_root(opening)
        if root is None:
            return {'CANCELLED'}

        # One interior at a time: zero out the fills that were not
        # picked, then write the picked one's settings.
        opening.hb_closet_opening.adj_shelf_qty = (
            self.shelf_qty if self.fill == 'ADJ_SHELVES' else 0)
        opening.hb_closet_opening.drawer_qty = (
            self.drawer_qty if self.fill == 'DRAWERS' else 0)
        opening.hb_closet_opening.rollout_qty = (
            self.rollout_qty if self.fill == 'ROLLOUTS' else 0)
        opening.hb_closet_opening.slant_qty = (
            self.slant_qty if self.fill == 'SLANTED_SHELVES' else 0)
        opening.hb_closet_opening.cubby_cols = (
            self.cubby_cols if self.fill == 'CUBBIES' else 1)
        opening.hb_closet_opening.cubby_rows = (
            self.cubby_rows if self.fill == 'CUBBIES' else 1)

        if self.fill == 'CUBBIES':
            opening.hb_closet_opening.cubby_setback = self.cubby_setback
        elif self.fill == 'DRAWERS':
            opening.hb_closet_opening.drawer_front_height = \
                self.drawer_front_height
            if self.drawer_box and self.drawer_box != 'DEFAULT':
                opening.hb_closet_opening.drawer_box_override = \
                    self.drawer_box
            else:
                opening.hb_closet_opening.property_unset(
                    'drawer_box_override')
        elif self.fill == 'ROLLOUTS':
            opening.hb_closet_opening.rollout_height = self.rollout_height
        elif self.fill == 'SLANTED_SHELVES':
            opening.hb_closet_opening.slant_spacing = self.slant_spacing
            opening.hb_closet_opening.slant_angle = self.slant_angle
            opening.hb_closet_opening.slant_color = self.slant_color

        swing = '' if self.door_swing == 'NONE' else self.door_swing
        opening.hb_closet_opening.door_swing = swing
        opening.hb_closet_opening.is_hamper = bool(swing and self.is_hamper)

        if _opening_rods(opening):
            op = opening.hb_closet_opening
            op.rod_set_from_front = self.rod_set_from_front
            op.rod_from_front = self.rod_from_front
            op.rod_from_rear = self.rod_from_rear
            op.rod_width_deduction = self.rod_width_deduction
            op.remove_hangers = self.remove_hangers
            rod = _single_top_rod(opening)
            if rod is not None:
                rod['hb_z_offset'] = self.rod_top_offset

        types_closets.recalculate_closet_starter(root)
        _apply_finish(root)
        _apply_selection_shading(context, root)
        return {'FINISHED'}


class hb_closets_OT_set_corner_clearance(bpy.types.Operator):
    """Pull a closet back from wall corners occupied by perpendicular
    neighbors, leaving an access clearance, with optional bridge shelves
    spanning the gap (mirrors face_frame's blind-corner dialog flow).
    Handles one or both ends in a single dialog: a closet filling a
    wall between two occupied corners gets a section per side.

    Invoked two ways: from the placement modal with the identity props
    filled in (they're SKIP_SAVE so stale names never leak into a later
    invocation), or bare from the starter right-click menu, in which
    case invoke() re-detects corner neighbors for the active starter.
    """
    bl_idname = "hb_closets.set_corner_clearance"
    bl_label = "Corner Clearance"
    bl_options = {'UNDO'}

    closet_name: bpy.props.StringProperty(
        name="Closet Name", default="",
        options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore
    has_left: bpy.props.BoolProperty(
        name="Has Left", default=False,
        options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore
    has_right: bpy.props.BoolProperty(
        name="Has Right", default=False,
        options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore
    neighbor_left: bpy.props.StringProperty(
        name="Left Neighbor", default="",
        options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore
    neighbor_right: bpy.props.StringProperty(
        name="Right Neighbor", default="",
        options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore
    gap_left: bpy.props.FloatProperty(
        name="Left Gap", default=0.0, subtype='DISTANCE', unit='LENGTH',
        options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore
    gap_right: bpy.props.FloatProperty(
        name="Right Gap", default=0.0, subtype='DISTANCE', unit='LENGTH',
        options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore

    clearance_left: bpy.props.FloatProperty(
        name="Clearance", subtype='DISTANCE', unit='LENGTH',
        default=units.inch(12.0), min=0.0,
        description=(
            "Gap between this closet's left end panel and the adjacent "
            "closet's body"))  # type: ignore
    top_left: bpy.props.BoolProperty(
        name="Include Top Bridge Shelf", default=True,
        description=(
            "Span the clearance gap with a shelf at the corner bay's "
            "top shelf height"))  # type: ignore
    bottom_left: bpy.props.BoolProperty(
        name="Include Bottom Bridge", default=False,
        description=(
            "Also bridge the gap at the bottom shelf height (adds a "
            "kick strip on floor-mounted bays)"))  # type: ignore
    clearance_right: bpy.props.FloatProperty(
        name="Clearance", subtype='DISTANCE', unit='LENGTH',
        default=units.inch(12.0), min=0.0,
        description=(
            "Gap between this closet's right end panel and the adjacent "
            "closet's body"))  # type: ignore
    top_right: bpy.props.BoolProperty(
        name="Include Top Bridge Shelf", default=True,
        description=(
            "Span the clearance gap with a shelf at the corner bay's "
            "top shelf height"))  # type: ignore
    bottom_right: bpy.props.BoolProperty(
        name="Include Bottom Bridge", default=False,
        description=(
            "Also bridge the gap at the bottom shelf height (adds a "
            "kick strip on floor-mounted bays)"))  # type: ignore

    def _sides(self):
        return [s for s, has in (('left', self.has_left),
                                 ('right', self.has_right)) if has]

    def _fill_from_matches(self, matches):
        for neighbor, placed_end, gap in matches:
            if placed_end == 'LEFT':
                self.has_left = True
                self.neighbor_left = neighbor.name
                self.gap_left = gap
            else:
                self.has_right = True
                self.neighbor_right = neighbor.name
                self.gap_right = gap

    def invoke(self, context, event):
        if not self.closet_name:
            root = types_closets.find_starter_root(context.active_object)
            if root is None:
                self.report({'INFO'}, "No closet starter selected")
                return {'CANCELLED'}
            matches = _detect_corner_closet_neighbor(root)
            if not matches:
                self.report({'INFO'},
                            "No adjacent closet at a wall corner")
                return {'CANCELLED'}
            self.closet_name = root.name
            self._fill_from_matches(matches)
        return context.window_manager.invoke_props_dialog(self, width=320)

    def draw(self, context):
        layout = self.layout
        for side in self._sides():
            box = layout.box()
            box.label(
                text=f"{getattr(self, 'neighbor_' + side)} occupies "
                     f"the corner on the {side}.")
            box.prop(self, f'clearance_{side}')
            box.prop(self, f'top_{side}')
            if getattr(self, f'top_{side}'):
                box.prop(self, f'bottom_{side}')

    def execute(self, context):
        root = bpy.data.objects.get(self.closet_name)
        if root is None:
            self.report({'WARNING'}, "Closet missing; aborting")
            return {'CANCELLED'}
        sides = self._sides()
        if not sides:
            return {'CANCELLED'}
        sp = root.hb_closet_starter

        # Shrink from each occupied corner end; the body between keeps
        # its placement (a LEFT reduction shifts the origin right, a
        # RIGHT reduction only trims width). Clamp the TOTAL so the
        # starter can't collapse, splitting any clamped shortfall
        # proportionally; each side's actual (possibly clamped)
        # reduction feeds that side's bridge span so the shelves always
        # exactly fill the real gaps.
        red = {s: getattr(self, f'clearance_{s}') - getattr(self, f'gap_{s}')
               for s in sides}
        total_red = sum(red.values())
        new_width = max(sp.width - total_red, units.inch(6.0))
        total_actual = sp.width - new_width
        factor = (total_actual / total_red
                  if total_red > 1e-9 and total_actual < total_red - 1e-9
                  else 1.0)

        # Every prompt written here would relay the starter out on
        # its own; holding them means the whole dialog costs one solve.
        with types_closets.suspend_recalc():
            for side in sides:
                actual = red[side] * factor
                span = getattr(self, f'gap_{side}') + actual
                top_on = getattr(self, f'top_{side}') and span > 1e-4
                # Straight onto the starter's bridge prompts, so what
                # the dialog set is what the prompts show afterwards.
                setattr(sp, f'bridge_{side}', top_on)
                setattr(sp, f'bridge_{side}_width', float(max(span, 0.0)))
                setattr(sp, f'include_bottom_bridge_{side}',
                        bool(top_on and getattr(self, f'bottom_{side}')))
                if side == 'left':
                    root.location.x += actual

            sp.width = new_width
            types_closets.recalculate_closet_starter(root)
        return {'FINISHED'}


class hb_closets_OT_change_hanger(bpy.types.Operator):
    """Pick the model for the selected hanger (Room Default follows the
    sidebar Hangers option). The dropdown previews live in the dialog."""
    bl_idname = "hb_closets.change_hanger"
    bl_label = "Change Hanger"
    bl_options = {'UNDO'}

    def _items(self, context):
        from .. import pulls_closets
        return pulls_closets.hanger_override_enum_items(self, context)

    hanger_model: bpy.props.EnumProperty(
        name="Hanger", items=_items)  # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.get('IS_CLOSET_HANGER')

    def _apply(self, context):
        from .. import pulls_closets
        obj = context.active_object
        if obj is None or not obj.get('IS_CLOSET_HANGER'):
            return
        if self.hanger_model == 'SCENE':
            if 'hb_hanger_model' in obj:
                del obj['hb_hanger_model']
            selection = getattr(context.scene.hb_closets,
                                'closet_hanger_model',
                                pulls_closets.DEFAULT_HANGER)
        else:
            obj['hb_hanger_model'] = self.hanger_model
            selection = self.hanger_model
        model = pulls_closets.resolve_hanger_object(selection)
        if model is not None and obj.data is not model.data:
            obj.data = model.data

    def check(self, context):
        # Live preview while the dialog is open, as in the prior
        # library.
        self._apply(context)
        return True

    def invoke(self, context, event):
        obj = context.active_object
        current = obj.get('hb_hanger_model', '') if obj else ''
        self.hanger_model = current if current else 'SCENE'
        return context.window_manager.invoke_props_dialog(self, width=300)

    def draw(self, context):
        self.layout.prop(self, 'hanger_model')

    def execute(self, context):
        self._apply(context)
        return {'FINISHED'}


class hb_closets_OT_randomize_hangers(bpy.types.Operator):
    """Randomly assign a hanger model to every hanger in the room
    (stored as per-hanger overrides - right-click a hanger and pick
    Room Default to reset one)"""
    bl_idname = "hb_closets.randomize_hangers"
    bl_label = "Randomize Hangers"
    bl_options = {'UNDO'}

    def execute(self, context):
        import random
        from .. import pulls_closets
        files = pulls_closets.get_hanger_files()
        if len(files) < 2:
            self.report({'INFO'},
                        "Install the model pack to get more hangers")
            return {'CANCELLED'}
        count = 0
        for obj in context.scene.objects:
            if not obj.get(pulls_closets.TAG_HANGER):
                continue
            rod = obj.parent
            if rod is None or rod.get('hb_preview'):
                continue
            # Only garments that FIT this rod's section: the rod's
            # opening-local height is its clearance to the section
            # bottom, so double-hang rods draw shirts while long-hang
            # sections can pull dresses and coats.
            candidates = pulls_closets.hangers_that_fit(rod.location.z)
            if not candidates:
                continue
            choice = random.choice(candidates)
            obj['hb_hanger_model'] = choice
            model = pulls_closets.resolve_hanger_object(choice)
            if model is not None and obj.data is not model.data:
                obj.data = model.data
            count += 1
        if not count:
            self.report({'INFO'}, "No hangers in the room")
            return {'CANCELLED'}
        self.report({'INFO'}, f"Randomized {count} hangers")
        return {'FINISHED'}


class hb_closets_OT_install_model_pack(bpy.types.Operator):
    """Install a downloaded model pack (.zip of hanger .blend files)
    into the user data folder - packed models never live in the
    library itself"""
    bl_idname = "hb_closets.install_model_pack"
    bl_label = "Install Model Pack"

    filepath: bpy.props.StringProperty(
        subtype='FILE_PATH', options={'SKIP_SAVE'})  # type: ignore
    filter_glob: bpy.props.StringProperty(
        default="*.zip", options={'HIDDEN'})  # type: ignore

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        import zipfile
        from .. import pulls_closets
        if not self.filepath or not os.path.isfile(self.filepath):
            self.report({'WARNING'}, "Select a model pack .zip")
            return {'CANCELLED'}
        dest = pulls_closets.user_hangers_dir(create=True)
        installed = 0
        try:
            with zipfile.ZipFile(self.filepath) as zf:
                for member in zf.namelist():
                    # Flatten to basenames: only .blend payloads land in
                    # the user folder (also defuses zip path traversal).
                    name = os.path.basename(member)
                    if not name.lower().endswith('.blend'):
                        continue
                    with zf.open(member) as src, \
                            open(os.path.join(dest, name), 'wb') as out:
                        out.write(src.read())
                    installed += 1
        except zipfile.BadZipFile:
            self.report({'ERROR'}, "Not a valid .zip file")
            return {'CANCELLED'}
        if not installed:
            self.report({'WARNING'}, "No models found in the pack")
            return {'CANCELLED'}
        pulls_closets.refresh()
        self.report({'INFO'}, f"Installed {installed} models")
        return {'FINISHED'}


class hb_closets_OT_add_molding(bpy.types.Operator):
    """Add molding along every closet in the room using the selected
    profile (re-run after layout changes; clears each starter's previous
    run of the same kind first)."""
    bl_idname = "hb_closets.add_molding"
    bl_label = "Add Molding"
    bl_options = {'UNDO'}

    molding_kind: bpy.props.StringProperty(
        name="Kind", default='CROWN')  # type: ignore

    @classmethod
    def description(cls, context, properties):
        if properties.molding_kind == 'BASE':
            return ("Add base molding along the floor of every closet in "
                    "the room using the selected profile (hanging bays "
                    "are skipped)")
        return ("Add crown molding along the top of every closet in the "
                "room using the selected profile (bays under 60\" are "
                "skipped)")

    def execute(self, context):
        from .. import molding_closets
        kind = (self.molding_kind
                if self.molding_kind in molding_closets.KINDS else 'CROWN')
        base = kind == 'BASE'
        prop_name = ('closet_base_profile' if base
                     else 'closet_crown_profile')
        # A dynamic enum reads back empty until something sets it, so an
        # untouched dropdown falls through to the kind's standard profile
        # rather than quietly adding nothing.
        profile_name = (getattr(context.scene.hb_closets, prop_name, '')
                        or molding_closets.KINDS[kind][1])
        profile = molding_closets.load_profile(profile_name, kind)
        label = "Base" if base else "Crown"
        if profile is None:
            self.report({'WARNING'}, f"{label} profile not found")
            return {'CANCELLED'}
        add = (molding_closets.add_base_to_starter if base
               else molding_closets.add_crown_to_starter)
        made = 0
        for obj in context.scene.objects:
            if (obj.get(types_closets.TAG_STARTER_CAGE)
                    and not str(obj.get('CLASS_NAME', '')
                                ).startswith('LShelf')):
                made += add(obj, profile)
        if made == 0:
            skipped = ("hanging bays are skipped" if base
                       else "bays under 60\" are skipped")
            self.report({'INFO'}, f"No qualifying runs ({skipped})")
            return {'CANCELLED'}
        self.report({'INFO'}, f"Added {label.lower()} to {made} runs")
        return {'FINISHED'}


class hb_closets_OT_delete_molding(bpy.types.Operator):
    """Remove closet molding from the room"""
    bl_idname = "hb_closets.delete_molding"
    bl_label = "Clear Closet Molding"
    bl_options = {'UNDO'}

    # Empty clears both runs; a kind clears just that one.
    molding_kind: bpy.props.StringProperty(name="Kind", default="")  # type: ignore

    @classmethod
    def description(cls, context, properties):
        if properties.molding_kind == 'BASE':
            return "Remove all closet base molding from the room"
        if properties.molding_kind == 'CROWN':
            return "Remove all closet crown molding from the room"
        return "Remove all closet molding from the room"

    def execute(self, context):
        from .. import molding_closets
        kind = self.molding_kind or None
        removed = 0
        for obj in list(context.scene.objects):
            if not obj.get(molding_closets.TAG_MOLDING):
                continue
            if kind is not None and obj.get(
                    molding_closets.PROP_MOLDING_KIND, 'CROWN') != kind:
                continue
            bpy.data.objects.remove(obj, do_unlink=True)
            removed += 1
        self.report({'INFO'}, f"Removed {removed} molding runs")
        return {'FINISHED'}


classes = (
    hb_closets_OT_toggle_mode,
    hb_closets_OT_place_starter,
    hb_closets_OT_insert_bay,
    hb_closets_OT_delete_bay,
    hb_closets_OT_add_part,
    hb_closets_OT_add_adj_shelves,
    hb_closets_OT_add_drawers,
    hb_closets_OT_drawer_accessory,
    hb_closets_OT_resize_drawer_for_tray,
    hb_closets_OT_add_doors,
    hb_closets_OT_add_cubbies,
    hb_closets_OT_add_rollouts,
    hb_closets_OT_add_slanted_shelves,
    hb_closets_OT_change_bay,
    hb_closets_OT_change_opening,
    hb_closets_OT_copy_bay,
    hb_closets_OT_paste_bay,
    hb_closets_OT_copy_opening,
    hb_closets_OT_paste_opening,
    hb_closets_OT_clear_opening,
    hb_closets_OT_clear_bay,
    hb_closets_OT_adj_shelf_step,
    hb_closets_OT_delete_part,
    hb_closets_OT_delete_starter,
    hb_closets_OT_starter_prompts,
    hb_closets_OT_bay_prompts,
    hb_closets_OT_opening_prompts,
    hb_closets_OT_set_corner_clearance,
    hb_closets_OT_add_molding,
    hb_closets_OT_delete_molding,
    hb_closets_OT_change_hanger,
    hb_closets_OT_install_model_pack,
    hb_closets_OT_randomize_hangers,
)

register, unregister = bpy.utils.register_classes_factory(classes)
