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

_BAY_QTY_MIN = 1
_BAY_QTY_MAX = 9
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
def _flip_swing_idprop(obj, key):
    """LEFT<->RIGHT flip of a door-swing idprop; DOUBLE and unset
    values pass through unchanged."""
    v = obj.get(key)
    if v == 'LEFT':
        obj[key] = 'RIGHT'
    elif v == 'RIGHT':
        obj[key] = 'LEFT'


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
        _flip_swing_idprop(bay, types_closets.PROP_BAY_DOOR_SWING)
        for child in bay.children:
            if child.get(types_closets.TAG_OPENING_CAGE):
                _flip_swing_idprop(child, types_closets.PROP_DOOR_SWING)
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
        # already-flipped bay order.
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
        existing = int(opening.get(types_closets.PROP_ADJ_SHELF_QTY, 0))
        self.qty = existing or types_closets.default_adj_shelf_qty(opening)
        return context.window_manager.invoke_props_dialog(self, width=250)

    def execute(self, context):
        opening = types_closets.find_opening_cage(context.active_object)
        if opening is None:
            return {'CANCELLED'}
        opening[types_closets.PROP_ADJ_SHELF_QTY] = self.qty
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
        opening = _active_opening_for_insert(context)
        if opening is None:
            return {'CANCELLED'}
        for key, value in values.items():
            opening[key] = value
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

    def invoke(self, context, event):
        from .. import const_closets as const
        opening = _active_opening_for_insert(context)
        if opening is not None:
            self.qty = int(opening.get(types_closets.PROP_DRAWER_QTY, 3)) or 3
            self.front_height = float(opening.get(
                types_closets.PROP_DRAWER_FRONT_HEIGHT,
                const.DRAWER_FRONT_HEIGHT))
        return context.window_manager.invoke_props_dialog(self, width=250)

    def execute(self, context):
        from .. import const_closets as const
        opening = _active_opening_for_insert(context)
        if opening is None:
            return {'CANCELLED'}
        opening[types_closets.PROP_DRAWER_QTY] = self.qty
        opening[types_closets.PROP_DRAWER_FRONT_HEIGHT] = self.front_height
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
               ('DOUBLE', "Double", "Pair of doors")],
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
            bay[types_closets.PROP_BAY_DOOR_SWING] = swing
            bay[types_closets.PROP_BAY_IS_HAMPER] = 1 if self.is_hamper else 0
            # Bay-wide doors supersede opening doors on the front side;
            # door openings get default adjustable shelves behind them
            # (seed_door_shelves skips occupied openings).
            for op in bay.children:
                if (op.get(types_closets.TAG_OPENING_CAGE)
                        and op.get(types_closets.PROP_OPENING_SIDE, 'FRONT')
                        == 'FRONT'):
                    op[types_closets.PROP_DOOR_SWING] = ''
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
            types_closets.PROP_DOOR_SWING: swing,
            types_closets.PROP_IS_HAMPER: 1 if self.is_hamper else 0,
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
            self.cols = int(opening.get(types_closets.PROP_CUBBY_COLS, 3)) or 3
            self.rows = int(opening.get(types_closets.PROP_CUBBY_ROWS, 3)) or 3
        return context.window_manager.invoke_props_dialog(self, width=250)

    def execute(self, context):
        return self._commit(context, {
            types_closets.PROP_CUBBY_COLS: self.cols,
            types_closets.PROP_CUBBY_ROWS: self.rows,
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
        qty = int(opening.get(types_closets.PROP_ADJ_SHELF_QTY, 0))
        opening[types_closets.PROP_ADJ_SHELF_QTY] = max(0, qty + self.delta)
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
            if bay is not None:
                bay[types_closets.PROP_BAY_DOOR_SWING] = ''
            if root is not None:
                types_closets.recalculate_closet_starter(root)
            return {'FINISHED'}
        opening = types_closets.find_opening_cage(obj)
        remove_obj = True

        if opening is not None:
            tcm = types_closets
            if role == tcm.PART_ROLE_ADJ_SHELF:
                qty = int(opening.get(tcm.PROP_ADJ_SHELF_QTY, 0))
                opening[tcm.PROP_ADJ_SHELF_QTY] = max(0, qty - 1)
            elif role == tcm.PART_ROLE_DRAWER_FRONT:
                # The regenerator removes the highest-index front AND its
                # box; let it own the removal.
                qty = int(opening.get(tcm.PROP_DRAWER_QTY, 0))
                opening[tcm.PROP_DRAWER_QTY] = max(0, qty - 1)
                remove_obj = False
            elif role == tcm.PART_ROLE_DOOR:
                opening[tcm.PROP_DOOR_SWING] = ''
                remove_obj = False
            elif role == tcm.PART_ROLE_CUBBY_DIVISION:
                cols = int(opening.get(tcm.PROP_CUBBY_COLS, 1))
                opening[tcm.PROP_CUBBY_COLS] = max(1, cols - 1)
                remove_obj = False
            elif role == tcm.PART_ROLE_CUBBY_SHELF:
                rows = int(opening.get(tcm.PROP_CUBBY_ROWS, 1))
                opening[tcm.PROP_CUBBY_ROWS] = max(1, rows - 1)
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


class hb_closets_OT_starter_prompts(bpy.types.Operator):
    """Edit the active starter's dimensions and options."""
    bl_idname = "hb_closets.starter_prompts"
    bl_label = "Closet Starter Properties"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return types_closets.find_starter_root(context.active_object) is not None

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=350)

    def draw(self, context):
        layout = self.layout
        root = types_closets.find_starter_root(context.active_object)
        if root is None:
            return
        sp = root.hb_closet_starter
        col = layout.column(align=True)
        col.prop(sp, 'width')
        col.prop(sp, 'height')
        col.prop(sp, 'depth')
        col = layout.column(align=True)
        col.prop(sp, 'toe_kick_height')
        col.prop(sp, 'toe_kick_setback')
        col.prop(sp, 'include_countertop')
        # Compact per-bay rows: width+lock / floor toggle.
        bays = sorted([c for c in root.children
                       if c.get(types_closets.TAG_BAY_CAGE)],
                      key=lambda o: o.get('hb_bay_index', 0))
        if bays:
            box = layout.box()
            box.label(text="Bays (width / height / depth)")
            for bay in bays:
                bp = bay.hb_closet_bay
                row = box.row(align=True)
                row.label(text=f"{bp.bay_index + 1}")
                row.prop(bp, 'width', text="")
                row.prop(bp, 'width_locked', text="",
                         icon='LOCKED' if bp.width_locked else 'UNLOCKED')
                row.prop(bp, 'height', text="")
                row.prop(bp, 'depth', text="")
                row.prop(bp, 'floor_mounted', text="", icon='TRIA_DOWN_BAR')

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
        return context.window_manager.invoke_props_dialog(self, width=350)

    def draw(self, context):
        layout = self.layout
        bay = types_closets.find_bay_cage(context.active_object)
        if bay is None:
            return
        bp = bay.hb_closet_bay
        row = layout.row(align=True)
        row.prop(bp, 'width')
        row.prop(bp, 'width_locked', text="",
                 icon='LOCKED' if bp.width_locked else 'UNLOCKED')
        col = layout.column(align=True)
        col.prop(bp, 'height')
        col.prop(bp, 'depth')
        col = layout.column(align=True)
        col.prop(bp, 'floor_mounted')
        col.prop(bp, 'remove_bottom')
        col.prop(bp, 'remove_cleat')

    def execute(self, context):
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

        for side in sides:
            actual = red[side] * factor
            span = getattr(self, f'gap_{side}') + actual
            top_on = getattr(self, f'top_{side}') and span > 1e-4
            root[f'hb_bridge_{side}'] = 1 if top_on else 0
            root[f'hb_bridge_w_{side}'] = float(max(span, 0.0))
            root[f'hb_bridge_bot_{side}'] = (
                1 if (top_on and getattr(self, f'bottom_{side}')) else 0)
            if side == 'left':
                root.location.x += actual

        sp.width = new_width  # update callback relays out
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
        # Live preview while the dialog is open (legacy behavior).
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
    """Add crown molding along the top of every closet in the room
    using the selected profile (re-run after layout changes; clears
    each starter's previous crown first)."""
    bl_idname = "hb_closets.add_molding"
    bl_label = "Add Crown Molding"
    bl_options = {'UNDO'}

    def execute(self, context):
        from .. import molding_closets
        profile_name = getattr(context.scene.hb_closets,
                               'closet_crown_profile',
                               molding_closets.DEFAULT_PROFILE)
        profile = molding_closets.load_profile(profile_name)
        if profile is None:
            self.report({'WARNING'}, "Crown profile not found")
            return {'CANCELLED'}
        made = 0
        for obj in context.scene.objects:
            if (obj.get(types_closets.TAG_STARTER_CAGE)
                    and not str(obj.get('CLASS_NAME', '')
                                ).startswith('LShelf')):
                made += molding_closets.add_crown_to_starter(obj, profile)
        if made == 0:
            self.report({'INFO'},
                        "No qualifying runs (bays under 60\" are skipped)")
            return {'CANCELLED'}
        self.report({'INFO'}, f"Added crown to {made} runs")
        return {'FINISHED'}


class hb_closets_OT_delete_molding(bpy.types.Operator):
    """Remove all closet molding from the room"""
    bl_idname = "hb_closets.delete_molding"
    bl_label = "Clear Closet Molding"
    bl_options = {'UNDO'}

    def execute(self, context):
        from .. import molding_closets
        removed = 0
        for obj in list(context.scene.objects):
            if obj.get(molding_closets.TAG_MOLDING):
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
    hb_closets_OT_add_doors,
    hb_closets_OT_add_cubbies,
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
    hb_closets_OT_set_corner_clearance,
    hb_closets_OT_add_molding,
    hb_closets_OT_delete_molding,
    hb_closets_OT_change_hanger,
    hb_closets_OT_install_model_pack,
    hb_closets_OT_randomize_hangers,
)

register, unregister = bpy.utils.register_classes_factory(classes)
