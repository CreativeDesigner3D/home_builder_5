"""Right-click commands shared by all face frame parts.

Three quick actions surface on every face frame part - end stiles, mid
stiles, top/bottom rails, and bay-internal splitters. Each operator
dispatches by the active part's hb_part_role to the appropriate prop:

- Set Width  -> cab.left_stile_width / right_stile_width (end stiles)
                cab.mid_stile_widths[msi]                (mid stiles between bays)
                bay.top_rail_width / bottom_rail_width   (top/bottom rails per bay)
                split.splitter_width                     (bay-internal splitters)
- Set Scribe -> cab.left_scribe / right_scribe / top_scribe
                (only end stiles and top rail expose this)
- Toggle Stile to Floor -> cab.extend_left_stile_to_floor /
                           cab.extend_right_stile_to_floor
                (only end stiles expose this)

Width writes also flip the matching unlock flag so a later style apply
doesn't reset the user's value.
"""
import bpy
from bpy.props import BoolProperty, FloatProperty, StringProperty

from .. import types_face_frame
from .. import types_face_frame_corner
from ....hb_types import GeoNodeCutpart, CabinetPartModifier
from .... import units


# Role sets used by each operator's poll and the menu's draw.
_ROLES_WITH_WIDTH = frozenset({
    types_face_frame.PART_ROLE_LEFT_STILE,
    types_face_frame.PART_ROLE_RIGHT_STILE,
    types_face_frame.PART_ROLE_MID_STILE,
    types_face_frame.PART_ROLE_TOP_RAIL,
    types_face_frame.PART_ROLE_BOTTOM_RAIL,
    types_face_frame.PART_ROLE_BAY_MID_RAIL,
    types_face_frame.PART_ROLE_BAY_MID_STILE,
})

_ROLES_WITH_SCRIBE = frozenset({
    types_face_frame.PART_ROLE_LEFT_STILE,
    types_face_frame.PART_ROLE_RIGHT_STILE,
    types_face_frame.PART_ROLE_TOP_RAIL,
})

_END_STILE_ROLES = frozenset({
    types_face_frame.PART_ROLE_LEFT_STILE,
    types_face_frame.PART_ROLE_RIGHT_STILE,
})


# ---------------------------------------------------------------------------
# Lookup helpers
# ---------------------------------------------------------------------------

def _find_bay_with_index(root, bay_index):
    """Bay cage with the matching hb_bay_index, or None."""
    for child in root.children:
        if (child.get(types_face_frame.TAG_BAY_CAGE)
                and child.get('hb_bay_index') == bay_index):
            return child
    return None


def _find_owning_split_node(part_obj):
    """The split node that owns a bay-internal splitter part. Bay mid
    rails / mid stiles carry hb_split_node_name at creation time -
    the cleanest handle on the owning split.
    """
    name = part_obj.get('hb_split_node_name')
    if not name:
        return None
    return bpy.data.objects.get(name)


# ---------------------------------------------------------------------------
# Width: read current and apply
# ---------------------------------------------------------------------------

def _get_current_width(obj, role, root):
    """Effective width currently in use for this part."""
    cab = root.face_frame_cabinet
    if role == types_face_frame.PART_ROLE_LEFT_STILE:
        return cab.left_stile_width
    if role == types_face_frame.PART_ROLE_RIGHT_STILE:
        return cab.right_stile_width
    if role == types_face_frame.PART_ROLE_MID_STILE:
        msi = obj.get('hb_mid_stile_index', 0)
        if 0 <= msi < len(cab.mid_stile_widths):
            return cab.mid_stile_widths[msi].width
        return cab.bay_mid_stile_width
    if role == types_face_frame.PART_ROLE_TOP_RAIL:
        start = obj.get('hb_segment_start_bay', 0)
        bay = _find_bay_with_index(root, start)
        return bay.face_frame_bay.top_rail_width if bay else cab.top_rail_width
    if role == types_face_frame.PART_ROLE_BOTTOM_RAIL:
        start = obj.get('hb_segment_start_bay', 0)
        bay = _find_bay_with_index(root, start)
        return (bay.face_frame_bay.bottom_rail_width
                if bay else cab.bottom_rail_width)
    if role in (types_face_frame.PART_ROLE_BAY_MID_RAIL,
                types_face_frame.PART_ROLE_BAY_MID_STILE):
        split = _find_owning_split_node(obj)
        if split is not None:
            # Each splitter member can hold its own width (keyed by the
            # hb_splitter_index stamped on the part); fall back to the
            # split's scalar splitter_width when this index isn't overridden.
            idx = obj.get('hb_splitter_index', 0)
            coll = split.face_frame_split.splitter_widths
            if 0 <= idx < len(coll) and coll[idx].active:
                return coll[idx].width
            return split.face_frame_split.splitter_width
        # Fall back to cabinet-level default; only used if the part lost its
        # split-node reference somehow.
        return (cab.bay_mid_rail_width
                if role == types_face_frame.PART_ROLE_BAY_MID_RAIL
                else cab.bay_mid_stile_width)
    return 0.0


def _resolve_width_target(obj, role, root):
    """Return (propgroup, attr_name) for the width prop this part owns,
    or (None, None) if the part has no resolvable target. Used by the
    operator's draw() to render a live-bound layout.prop.
    """
    cab = root.face_frame_cabinet
    if role == types_face_frame.PART_ROLE_LEFT_STILE:
        return cab, 'left_stile_width'
    if role == types_face_frame.PART_ROLE_RIGHT_STILE:
        return cab, 'right_stile_width'
    if role == types_face_frame.PART_ROLE_MID_STILE:
        msi = obj.get('hb_mid_stile_index', 0)
        if 0 <= msi < len(cab.mid_stile_widths):
            return cab.mid_stile_widths[msi], 'width'
        return None, None
    if role == types_face_frame.PART_ROLE_TOP_RAIL:
        start = obj.get('hb_segment_start_bay', 0)
        bay = _find_bay_with_index(root, start)
        return (bay.face_frame_bay, 'top_rail_width') if bay else (None, None)
    if role == types_face_frame.PART_ROLE_BOTTOM_RAIL:
        start = obj.get('hb_segment_start_bay', 0)
        bay = _find_bay_with_index(root, start)
        return (bay.face_frame_bay, 'bottom_rail_width') if bay else (None, None)
    if role in (types_face_frame.PART_ROLE_BAY_MID_RAIL,
                types_face_frame.PART_ROLE_BAY_MID_STILE):
        split = _find_owning_split_node(obj)
        return (split.face_frame_split, 'splitter_width') if split else (None, None)
    return None, None


def get_current_width(obj):
    """Effective width currently in use for a face frame part, or None
    if obj isn't a face frame part with a resolvable width target.
    Used by the right-click menu's draw() to label the Set Width entry
    with the part's current width.
    """
    if obj is None:
        return None
    role = obj.get('hb_part_role')
    if role not in _ROLES_WITH_WIDTH:
        return None
    root = types_face_frame.find_cabinet_root(obj)
    if root is None:
        return None
    return _get_current_width(obj, role, root)


def _rail_segment_bay_indices(root, start_bay_index, role):
    """Bay indices that make up the current rail segment starting at
    start_bay_index. Uses the solver's segment computation so the
    span matches the rail object the user actually clicked on.
    """
    from .. import solver_face_frame
    layout = solver_face_frame.FaceFrameLayout(root)
    if role == types_face_frame.PART_ROLE_TOP_RAIL:
        segments = solver_face_frame.top_rail_segments(layout)
    elif role == types_face_frame.PART_ROLE_BOTTOM_RAIL:
        segments = solver_face_frame.bottom_rail_segments(layout)
    else:
        return [start_bay_index]
    for seg in segments:
        if seg['start_bay'] == start_bay_index:
            return list(range(seg['start_bay'], seg['end_bay'] + 1))
    return [start_bay_index]


def _bays_by_index(root):
    """Dict of {bay_index: bay_obj} for all bays under root."""
    out = {}
    for child in root.children:
        if child.get(types_face_frame.TAG_BAY_CAGE):
            out[child.get('hb_bay_index')] = child
    return out


def _flip_unlock_for_role(obj, role, root):
    """Flip the unlock flag(s) so a later style apply leaves the user's
    value alone. For top / bottom rails this flips unlock on every bay
    in the rail's current segment so the cabinet style cascade can't
    re-split the rail by writing the cabinet default into the middle
    bays.

    Bay-internal splitters (mid rails / mid stiles) flip
    unlock_splitter_width on their owning split node so the style
    cascade leaves the per-split width alone.
    """
    cab = root.face_frame_cabinet
    if role == types_face_frame.PART_ROLE_LEFT_STILE:
        cab.unlock_left_stile = True
        return
    if role == types_face_frame.PART_ROLE_RIGHT_STILE:
        cab.unlock_right_stile = True
        return
    if role == types_face_frame.PART_ROLE_MID_STILE:
        msi = obj.get('hb_mid_stile_index', 0)
        if 0 <= msi < len(cab.mid_stile_widths):
            cab.mid_stile_widths[msi].unlock = True
        return
    if role in (types_face_frame.PART_ROLE_TOP_RAIL,
                types_face_frame.PART_ROLE_BOTTOM_RAIL):
        start = obj.get('hb_segment_start_bay', 0)
        unlock_attr = ('unlock_top_rail'
                       if role == types_face_frame.PART_ROLE_TOP_RAIL
                       else 'unlock_bottom_rail')
        indices = _rail_segment_bay_indices(root, start, role)
        bays = _bays_by_index(root)
        for idx in indices:
            bay = bays.get(idx)
            if bay is not None:
                setattr(bay.face_frame_bay, unlock_attr, True)
        return
    if role in (types_face_frame.PART_ROLE_BAY_MID_RAIL,
                types_face_frame.PART_ROLE_BAY_MID_STILE):
        split = _find_owning_split_node(obj)
        if split is not None:
            split.face_frame_split.unlock_splitter_width = True


def _fan_out_value(obj, role, root, value):
    """Write the new width value to every target the originally-clicked
    part owns. Single target for end stiles, mid stiles, and bay-internal
    splitters; segment-wide for top / bottom rails. Wrapped by the
    operator in a suspend_recalc so all per-bay writes coalesce into
    one recalc per drag tick.
    """
    cab = root.face_frame_cabinet
    if role == types_face_frame.PART_ROLE_LEFT_STILE:
        cab.left_stile_width = value
        return
    if role == types_face_frame.PART_ROLE_RIGHT_STILE:
        cab.right_stile_width = value
        return
    if role == types_face_frame.PART_ROLE_MID_STILE:
        msi = obj.get('hb_mid_stile_index', 0)
        if 0 <= msi < len(cab.mid_stile_widths):
            cab.mid_stile_widths[msi].width = value
        return
    if role in (types_face_frame.PART_ROLE_TOP_RAIL,
                types_face_frame.PART_ROLE_BOTTOM_RAIL):
        start = obj.get('hb_segment_start_bay', 0)
        attr = ('top_rail_width'
                if role == types_face_frame.PART_ROLE_TOP_RAIL
                else 'bottom_rail_width')
        indices = _rail_segment_bay_indices(root, start, role)
        bays = _bays_by_index(root)
        for idx in indices:
            bay = bays.get(idx)
            if bay is not None:
                setattr(bay.face_frame_bay, attr, value)
        return
    if role in (types_face_frame.PART_ROLE_BAY_MID_RAIL,
                types_face_frame.PART_ROLE_BAY_MID_STILE):
        split = _find_owning_split_node(obj)
        if split is not None:
            # Write ONLY this member's per-index override so the other mid
            # rails / mid stiles in the same split keep their widths. The
            # collection grows lazily to cover this index; active=True makes
            # the solver honor it over the split's scalar splitter_width.
            idx = obj.get('hb_splitter_index', 0)
            coll = split.face_frame_split.splitter_widths
            while len(coll) <= idx:
                coll.add()
            coll[idx].width = value
            coll[idx].active = True
        return


def _on_value_update(self, context):
    """FloatProperty update callback for the operator's value prop.
    Resolves the source part, role, and cabinet root each tick (so a
    user changing the active object mid-drag doesn't strand the
    operator), then fans the new value out through one suspended
    recalc.

    Bails when source_obj_name is empty - invoke() relies on this to
    seed the dialog value without triggering a fanout / recalc.
    """
    obj = bpy.data.objects.get(self.source_obj_name)
    if obj is None:
        return
    role = obj.get('hb_part_role')
    root = types_face_frame.find_cabinet_root(obj)
    if root is None:
        return
    with types_face_frame.suspend_recalc():
        _fan_out_value(obj, role, root, self.value)


def _lock_for_role(obj, role, root):
    """Re-lock the part so it follows the cabinet / bay / style default
    again -- the inverse of _flip_unlock_for_role. Clearing each unlock
    flag fires that flag's own update callback, which reverts the width to
    the default on the recalc that follows. For bay mid rails / stiles the
    per-member override is dropped too so the part returns to the split's
    scalar default."""
    cab = root.face_frame_cabinet
    if role == types_face_frame.PART_ROLE_LEFT_STILE:
        cab.unlock_left_stile = False
        return
    if role == types_face_frame.PART_ROLE_RIGHT_STILE:
        cab.unlock_right_stile = False
        return
    if role == types_face_frame.PART_ROLE_MID_STILE:
        msi = obj.get('hb_mid_stile_index', 0)
        if 0 <= msi < len(cab.mid_stile_widths):
            cab.mid_stile_widths[msi].unlock = False
        return
    if role in (types_face_frame.PART_ROLE_TOP_RAIL,
                types_face_frame.PART_ROLE_BOTTOM_RAIL):
        start = obj.get('hb_segment_start_bay', 0)
        unlock_attr = ('unlock_top_rail'
                       if role == types_face_frame.PART_ROLE_TOP_RAIL
                       else 'unlock_bottom_rail')
        indices = _rail_segment_bay_indices(root, start, role)
        bays = _bays_by_index(root)
        for idx in indices:
            bay = bays.get(idx)
            if bay is not None:
                setattr(bay.face_frame_bay, unlock_attr, False)
        return
    if role in (types_face_frame.PART_ROLE_BAY_MID_RAIL,
                types_face_frame.PART_ROLE_BAY_MID_STILE):
        split = _find_owning_split_node(obj)
        if split is not None:
            sp = split.face_frame_split
            idx = obj.get('hb_splitter_index', 0)
            coll = sp.splitter_widths
            if 0 <= idx < len(coll):
                coll[idx].active = False
            sp.unlock_splitter_width = False


def _on_lock_update(self, context):
    """'Lock to Default' toggle on the Set Width dialog. Locking re-locks
    the part (its unlock flags' callbacks revert the width to the default)
    and reflects the reverted value in the field; unlocking re-flips the
    unlock and re-applies the dialog value. Bails while source_obj_name is
    empty (invoke seeds the toggle before binding)."""
    obj = bpy.data.objects.get(self.source_obj_name)
    if obj is None:
        return
    role = obj.get('hb_part_role')
    root = types_face_frame.find_cabinet_root(obj)
    if root is None:
        return
    if self.lock_to_default:
        _lock_for_role(obj, role, root)
        # Reflect the reverted default in the dialog field without
        # re-fanning it out (that would recreate the override we cleared).
        src = bpy.data.objects.get(self.source_obj_name)
        if src is not None:
            saved = self.source_obj_name
            self.source_obj_name = ''
            self.value = _get_current_width(src, role, root)
            self.source_obj_name = saved
    else:
        _flip_unlock_for_role(obj, role, root)
        with types_face_frame.suspend_recalc():
            _fan_out_value(obj, role, root, self.value)


# ---------------------------------------------------------------------------
# Scribe: read current and apply (cabinet-level only)
# ---------------------------------------------------------------------------

def _get_current_scribe(role, root):
    cab = root.face_frame_cabinet
    if role == types_face_frame.PART_ROLE_LEFT_STILE:
        return cab.left_scribe
    if role == types_face_frame.PART_ROLE_RIGHT_STILE:
        return cab.right_scribe
    if role == types_face_frame.PART_ROLE_TOP_RAIL:
        return cab.top_scribe
    return 0.0


def _apply_scribe(role, root, value):
    cab = root.face_frame_cabinet
    if role == types_face_frame.PART_ROLE_LEFT_STILE:
        cab.left_scribe = value
    elif role == types_face_frame.PART_ROLE_RIGHT_STILE:
        cab.right_scribe = value
    elif role == types_face_frame.PART_ROLE_TOP_RAIL:
        cab.top_scribe = value


# ---------------------------------------------------------------------------
# Operators
# ---------------------------------------------------------------------------

class hb_face_frame_OT_set_part_width(bpy.types.Operator):
    """Set the width of the selected face frame part. The dialog binds
    to a FloatProperty on the operator; its update callback fans the
    new value out to every relevant target. For top / bottom rails
    that span multiple bays, the value is written to every bay in the
    rail's current segment so the rail doesn't fragment at edges that
    used to be invisible. For other roles, single-target write.

    All per-bay writes coalesce into one recalc per drag tick via
    suspend_recalc.
    """
    bl_idname = "hb_face_frame.set_part_width"
    bl_label = "Set Width"
    bl_description = "Set this face frame part's width"
    bl_options = {'UNDO'}

    # Hidden state - lets the update callback resolve targets each tick
    # rather than caching them on the operator (which would go stale if
    # the user does anything else mid-drag).
    source_obj_name: StringProperty(default='', options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore

    value: FloatProperty(
        name="Width", default=0.0, unit='LENGTH', precision=4, min=0.0,
        update=_on_value_update,
    )  # type: ignore

    lock_to_default: BoolProperty(
        name="Lock to Default", default=False,
        description="Lock this part back to the cabinet / style default",
        options={'SKIP_SAVE'}, update=_on_lock_update,
    )  # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj is None:
            return False
        return obj.get('hb_part_role') in _ROLES_WITH_WIDTH

    def invoke(self, context, event):
        obj = context.active_object
        role = obj.get('hb_part_role')
        root = types_face_frame.find_cabinet_root(obj)
        if root is None:
            self.report({'WARNING'}, "No cabinet root found")
            return {'CANCELLED'}

        # Seed the dialog value BEFORE source_obj_name is set. The
        # value prop's update callback (_on_value_update) bails while
        # source_obj_name is empty, so the seed write cannot fan out or
        # trigger a recalc. An operator-instance flag did not survive
        # into the callback reliably, hence the empty-name approach.
        # Seed from the EFFECTIVE width (handles per-splitter overrides,
        # which _resolve_width_target's scalar target wouldn't reflect).
        self.value = _get_current_width(obj, role, root)
        # Reset the lock toggle while the binding is still empty so its
        # update callback bails (no premature re-lock).
        self.lock_to_default = False

        self.source_obj_name = obj.name

        # Flip unlocks LAST so a later style apply leaves the user's
        # value alone. For rails this flips every bay in the current
        # segment so the cascade can't re-split the rail. For bay-
        # internal mid rails / stiles the flag write fires a recalc that
        # rebuilds the bay and invalidates `obj` - so nothing may read
        # `obj` past this point. draw() and _on_value_update both
        # re-resolve from source_obj_name, whose name is stable across
        # recalc.
        _flip_unlock_for_role(obj, role, root)

        return context.window_manager.invoke_props_dialog(self, width=260)

    def draw(self, context):
        obj = bpy.data.objects.get(self.source_obj_name) or context.active_object
        col = self.layout.column(align=True)
        if obj is not None:
            col.label(text=obj.name, icon='SNAP_EDGE')
        row = col.row(align=True)
        sub = row.row(align=True)
        sub.enabled = not self.lock_to_default
        sub.prop(self, 'value', text="Width")
        row.prop(self, 'lock_to_default', text="",
                 icon='LOCKED' if self.lock_to_default else 'UNLOCKED')

    def execute(self, context):
        # Live-bound via the value prop's update callback; execute is
        # only invoked when the user dismisses with OK - no extra work
        # needed.
        return {'FINISHED'}


class hb_face_frame_OT_set_part_scribe(bpy.types.Operator):
    """Set scribe at the cabinet edge corresponding to the selected
    end stile or top rail. Live-bound to cab.left_scribe / right_scribe /
    top_scribe so edits apply as the user drags or types.
    """
    bl_idname = "hb_face_frame.set_part_scribe"
    bl_label = "Set Scribe"
    bl_description = "Set scribe for this cabinet edge"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj is None:
            return False
        return obj.get('hb_part_role') in _ROLES_WITH_SCRIBE

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=260)

    def draw(self, context):
        obj = context.active_object
        if obj is None:
            self.layout.label(text="No part selected", icon='INFO')
            return
        role = obj.get('hb_part_role')
        root = types_face_frame.find_cabinet_root(obj)
        if root is None:
            self.layout.label(text="No cabinet root found", icon='ERROR')
            return
        cab = root.face_frame_cabinet
        attr_by_role = {
            types_face_frame.PART_ROLE_LEFT_STILE: ('left_scribe', "Left Scribe"),
            types_face_frame.PART_ROLE_RIGHT_STILE: ('right_scribe', "Right Scribe"),
            types_face_frame.PART_ROLE_TOP_RAIL: ('top_scribe', "Top Scribe"),
        }
        entry = attr_by_role.get(role)
        if entry is None:
            self.layout.label(text="No scribe for this part", icon='ERROR')
            return
        attr, label = entry
        col = self.layout.column(align=True)
        col.label(text=obj.name, icon='SNAP_EDGE')
        col.prop(cab, attr, text=label)

    def execute(self, context):
        return {'FINISHED'}


class hb_face_frame_OT_toggle_stile_to_floor(bpy.types.Operator):
    """Toggle whether the selected end stile extends past the toe kick
    down to the floor. Writes the cabinet-level extend_left_stile_to_floor
    or extend_right_stile_to_floor bool.
    """
    bl_idname = "hb_face_frame.toggle_stile_to_floor"
    bl_label = "Toggle Stile to Floor"
    bl_description = (
        "Toggle whether this end stile extends past the toe kick to the floor"
    )
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj is None:
            return False
        return obj.get('hb_part_role') in (
            _END_STILE_ROLES | {types_face_frame.PART_ROLE_MID_STILE})

    def execute(self, context):
        obj = context.active_object
        role = obj.get('hb_part_role')
        root = types_face_frame.find_cabinet_root(obj)
        if root is None:
            return {'CANCELLED'}
        cab = root.face_frame_cabinet
        if role == types_face_frame.PART_ROLE_LEFT_STILE:
            cab.extend_left_stile_to_floor = not cab.extend_left_stile_to_floor
        elif role == types_face_frame.PART_ROLE_RIGHT_STILE:
            cab.extend_right_stile_to_floor = not cab.extend_right_stile_to_floor
        elif role == types_face_frame.PART_ROLE_MID_STILE:
            # Per-stile to_floor on the mid_stile_widths entry, keyed by
            # the part's gap index. Grow the collection if needed (a fresh
            # entry's default width matches the solver default, no change).
            gap = obj.get('hb_mid_stile_index')
            if gap is None:
                return {'CANCELLED'}
            coll = cab.mid_stile_widths
            while len(coll) <= gap:
                coll.add()
            coll[gap].to_floor = not coll[gap].to_floor
        else:
            return {'CANCELLED'}
        return {'FINISHED'}


class hb_face_frame_OT_remove_bottom_rail(bpy.types.Operator):
    """Remove the bottom rail the user clicked.

    The bottom rail is a single segment object that can span several
    bays; removal is driven by the per-bay `remove_bottom` flag (the
    same flag exposed in the bay properties), so we set it on EVERY bay
    in the clicked rail's current segment. That drops the whole rail the
    user is looking at rather than fragmenting it at a single bay edge.
    Restore it later via Remove Bottom in the bay properties.
    """
    bl_idname = "hb_face_frame.remove_bottom_rail"
    bl_label = "Remove Bottom Rail"
    bl_description = "Remove this bottom rail (sets Remove Bottom on its bay span)"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj is not None
                and obj.get('hb_part_role')
                == types_face_frame.PART_ROLE_BOTTOM_RAIL)

    def execute(self, context):
        obj = context.active_object
        root = types_face_frame.find_cabinet_root(obj)
        if root is None:
            self.report({'WARNING'}, "No cabinet root found")
            return {'CANCELLED'}
        start = obj.get('hb_segment_start_bay', 0)
        indices = _rail_segment_bay_indices(
            root, start, types_face_frame.PART_ROLE_BOTTOM_RAIL)
        bays = _bays_by_index(root)
        # One suspend so the per-bay flag writes coalesce into a single
        # recalc - remove_bottom fires _update_cabinet_dim on each write.
        with types_face_frame.suspend_recalc():
            for idx in indices:
                bay = bays.get(idx)
                if bay is not None:
                    bay.face_frame_bay.remove_bottom = True
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Misc Part dimensions
# ---------------------------------------------------------------------------

def _misc_part_for_dialog(op):
    """The Misc Part an open Set-Dimensions dialog targets.

    Resolved by name every tick (never cached) so it survives the popup
    and a mid-edit active-object change, mirroring set_part_width's
    source_obj_name pattern. Returns None while source_obj_name is unset -
    invoke() seeds the prop values BEFORE setting the name, and the update
    callbacks bail on None so those seed writes don't fan back into the
    part.
    """
    if not op.source_obj_name:
        return None
    return bpy.data.objects.get(op.source_obj_name)


def _on_misc_width_update(self, context):
    """Live-apply Width -> the cutpart's 'Length' (X) input."""
    obj = _misc_part_for_dialog(self)
    if obj is not None:
        GeoNodeCutpart(obj).set_input('Length', self.part_width)


def _on_misc_depth_update(self, context):
    """Live-apply Depth -> the cutpart's 'Width' (Y) input."""
    obj = _misc_part_for_dialog(self)
    if obj is not None:
        GeoNodeCutpart(obj).set_input('Width', self.part_depth)


def _on_misc_thickness_update(self, context):
    """Live-apply Thickness -> the cutpart's 'Thickness' (Z) input."""
    obj = _misc_part_for_dialog(self)
    if obj is not None:
        GeoNodeCutpart(obj).set_input('Thickness', self.part_thickness)


class hb_face_frame_OT_set_misc_part_dimensions(bpy.types.Operator):
    """Set a Misc Part's size.

    A Misc Part is a bare GeoNodeCutpart with no cabinet cage, so it has
    none of the width / height props the other Set-* operators bind to.
    Each field is LIVE-BOUND via its update callback (same approach as
    set_part_width): editing a value writes straight to the cutpart's own
    GeoNode input while the dialog is open - execute() is only reached on
    OK and has nothing left to do. (Relying on execute alone did not apply
    on confirm in the popup context.) Labels are user-facing
    (Width / Depth / Thickness); the GeoNode input each maps to is noted
    on its update callback.
    """
    bl_idname = "hb_face_frame.set_misc_part_dimensions"
    bl_label = "Set Dimensions"
    bl_description = "Set this part's width, depth, and thickness"
    bl_options = {'UNDO'}

    # Resolved each tick by the update callbacks (see _misc_part_for_dialog).
    source_obj_name: StringProperty(default='', options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore

    part_width: FloatProperty(name="Width", unit='LENGTH', precision=4, min=0.0,
                              update=_on_misc_width_update)  # type: ignore
    part_depth: FloatProperty(name="Depth", unit='LENGTH', precision=4, min=0.0,
                              update=_on_misc_depth_update)  # type: ignore
    part_thickness: FloatProperty(name="Thickness", unit='LENGTH', precision=4, min=0.0,
                                  update=_on_misc_thickness_update)  # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and bool(obj.get('IS_FACE_FRAME_MISC_PART'))

    def invoke(self, context, event):
        obj = context.active_object
        part = GeoNodeCutpart(obj)
        # Seed the fields BEFORE source_obj_name is set: the update
        # callbacks bail while it's empty, so seeding can't write back or
        # double-apply.
        self.part_width = part.get_input('Length')
        self.part_depth = part.get_input('Width')
        self.part_thickness = part.get_input('Thickness')
        self.source_obj_name = obj.name
        return context.window_manager.invoke_props_dialog(self, width=260)

    def draw(self, context):
        col = self.layout.column(align=True)
        col.prop(self, 'part_width')
        col.prop(self, 'part_depth')
        col.prop(self, 'part_thickness')

    def execute(self, context):
        # Live-bound via the prop update callbacks; execute is only hit on
        # OK - nothing left to do.
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Door Part dimensions + style
# ---------------------------------------------------------------------------

def _door_part_for_dialog(op):
    """The Door Part an open Set-Dimensions dialog targets (resolved by name
    each tick; None while source_obj_name is unset - see the Misc Part
    equivalent)."""
    if not op.source_obj_name:
        return None
    return bpy.data.objects.get(op.source_obj_name)


def _on_door_width_update(self, context):
    """Live-apply Width -> the door's 'Width' input, then re-track the pull."""
    obj = _door_part_for_dialog(self)
    if obj is not None:
        GeoNodeCutpart(obj).set_input('Width', self.part_width)
        types_face_frame.position_door_part_pull(obj)


def _on_door_height_update(self, context):
    """Live-apply Height -> the door's 'Length' input, then re-track the pull."""
    obj = _door_part_for_dialog(self)
    if obj is not None:
        GeoNodeCutpart(obj).set_input('Length', self.part_height)
        types_face_frame.position_door_part_pull(obj)


def _on_door_thickness_update(self, context):
    """Live-apply Thickness -> the door's 'Thickness' input, then re-track
    the pull (it mounts on the front face = thickness)."""
    obj = _door_part_for_dialog(self)
    if obj is not None:
        GeoNodeCutpart(obj).set_input('Thickness', self.part_thickness)
        types_face_frame.position_door_part_pull(obj)


class hb_face_frame_OT_set_door_part_dimensions(bpy.types.Operator):
    """Set a Door Part's size.

    Same live-bound pattern as the Misc Part dialog, but the door's GeoNode
    inputs map differently: 'Length' is the door HEIGHT and 'Width' the door
    WIDTH (Face_Frame_Door_Style.assign_style_to_front's convention), so the
    fields are Width / Height / Thickness. Each edit also re-tracks the pull
    so it stays on the door as it resizes.
    """
    bl_idname = "hb_face_frame.set_door_part_dimensions"
    bl_label = "Set Dimensions"
    bl_description = "Set this door part's width, height, and thickness"
    bl_options = {'UNDO'}

    source_obj_name: StringProperty(default='', options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore

    part_width: FloatProperty(name="Width", unit='LENGTH', precision=4, min=0.0,
                              update=_on_door_width_update)  # type: ignore  # -> 'Width'
    part_height: FloatProperty(name="Height", unit='LENGTH', precision=4, min=0.0,
                               update=_on_door_height_update)  # type: ignore  # -> 'Length'
    part_thickness: FloatProperty(name="Thickness", unit='LENGTH', precision=4, min=0.0,
                                  update=_on_door_thickness_update)  # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and bool(obj.get('IS_FACE_FRAME_DOOR_PART'))

    def invoke(self, context, event):
        obj = context.active_object
        part = GeoNodeCutpart(obj)
        # Seed BEFORE source_obj_name is set so the callbacks bail and the
        # seed writes don't fan back.
        self.part_width = part.get_input('Width')
        self.part_height = part.get_input('Length')
        self.part_thickness = part.get_input('Thickness')
        self.source_obj_name = obj.name
        return context.window_manager.invoke_props_dialog(self, width=260)

    def draw(self, context):
        col = self.layout.column(align=True)
        col.prop(self, 'part_width')
        col.prop(self, 'part_height')
        col.prop(self, 'part_thickness')

    def execute(self, context):
        # Live-bound via the prop update callbacks; nothing to do on OK.
        return {'FINISHED'}


class hb_face_frame_OT_assign_active_door_style(bpy.types.Operator):
    """Re-apply the project's ACTIVE cabinet style's door style to the
    selected Door Part (re-runs assign_style_to_front: slab / 5-piece +
    DOOR_STYLE_NAME). Use after switching the active style."""
    bl_idname = "hb_face_frame.assign_active_door_style"
    bl_label = "Assign Active Style"
    bl_description = "Apply the active cabinet style's door style to this door part"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and bool(obj.get('IS_FACE_FRAME_DOOR_PART'))

    def execute(self, context):
        types_face_frame.apply_active_door_style_to_part(context.active_object)
        return {'FINISHED'}


class hb_face_frame_OT_toggle_door_part_pull(bpy.types.Operator):
    """Show / hide the pull on a Door Part. Stored as DOOR_PART_SHOW_PULL on
    the object; position_door_part_pull adds or removes the pull child to
    match."""
    bl_idname = "hb_face_frame.toggle_door_part_pull"
    bl_label = "Toggle Pull"
    bl_description = "Show or hide this door part's pull"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and bool(obj.get('IS_FACE_FRAME_DOOR_PART'))

    def execute(self, context):
        obj = context.active_object
        obj['DOOR_PART_SHOW_PULL'] = not obj.get('DOOR_PART_SHOW_PULL', True)
        types_face_frame.position_door_part_pull(obj)
        return {'FINISHED'}


class hb_face_frame_OT_switch_door_part_pull_side(bpy.types.Operator):
    """Switch the pull to the other vertical edge of a Door Part (LEFT-
    hinged <-> RIGHT-hinged). Stored as DOOR_PART_PULL_SIDE on the object."""
    bl_idname = "hb_face_frame.switch_door_part_pull_side"
    bl_label = "Switch Pull Side"
    bl_description = "Move the pull to the opposite edge of this door part"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj is not None and bool(obj.get('IS_FACE_FRAME_DOOR_PART'))
                and obj.get('DOOR_PART_SHOW_PULL', True))

    def execute(self, context):
        obj = context.active_object
        side = obj.get('DOOR_PART_PULL_SIDE', 'LEFT')
        obj['DOOR_PART_PULL_SIDE'] = 'RIGHT' if side == 'LEFT' else 'LEFT'
        types_face_frame.position_door_part_pull(obj)
        return {'FINISHED'}


class hb_face_frame_OT_toggle_door_part_front_kind(bpy.types.Operator):
    """Switch a Door Part between a DOOR front and a DRAWER front. Only the
    pull changes - DOOR: vertical bar near the top on the pull-side edge;
    DRAWER: horizontal bar centered (drawer-pull asset + the in-cabinet
    drawer placement). The front geometry / door style is left as-is.
    Stored as DOOR_PART_FRONT_KIND on the object."""
    bl_idname = "hb_face_frame.toggle_door_part_front_kind"
    bl_label = "Toggle Front Kind"
    bl_description = "Switch between a door front and a drawer front (moves the pull)"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and bool(obj.get('IS_FACE_FRAME_DOOR_PART'))

    def execute(self, context):
        obj = context.active_object
        kind = obj.get('DOOR_PART_FRONT_KIND', 'DOOR')
        obj['DOOR_PART_FRONT_KIND'] = 'DRAWER' if kind == 'DOOR' else 'DOOR'
        types_face_frame.position_door_part_pull(obj)
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Set Door Frame  (5-piece door / drawer front: per-side stile + rail +
# mid rail).  Edits are written as DURABLE per-front overrides
# (HB_FRAME_OVR_*) that assign_style_to_front honors on every recalc, then
# the front's own style is re-applied so the change shows immediately.
# ---------------------------------------------------------------------------

_DRAWER_FRONT_ROLES = frozenset({
    types_face_frame.PART_ROLE_DRAWER_FRONT,
    types_face_frame.PART_ROLE_PULLOUT_FRONT,
    types_face_frame.PART_ROLE_FALSE_FRONT,
})


def _door_style_mod(obj):
    """The 'Door Style' NODES (CPM_5PIECEDOOR) modifier on a 5-piece front,
    else None. Slab fronts have no such modifier, so they never match."""
    if obj is None:
        return None
    for mod in obj.modifiers:
        if mod.type == 'NODES' and mod.node_group and 'Door Style' in mod.name:
            return mod
    return None


def has_door_style_modifier(obj):
    return _door_style_mod(obj) is not None


def _mod_input_get(mod, name, default=None):
    """Read a NODES modifier input by socket name (identifiers are stable,
    indices are not - look the name up in the interface tree)."""
    try:
        for item in mod.node_group.interface.items_tree:
            if getattr(item, 'item_type', '') == 'SOCKET' and item.name == name:
                return getattr(mod.properties.inputs, item.identifier).value
    except Exception:
        pass
    return default


def _reapply_front_style(front_obj):
    """Re-apply the front's own door / drawer style so HB_FRAME_OVR_* edits
    take effect (mirrors what the solver does on recalc). Resolves the front's
    style by DOOR_STYLE_NAME in the role-correct pool."""
    name = front_obj.get('DOOR_STYLE_NAME')
    if not name:
        return
    from .. import props_hb_face_frame as _props
    ff = _props.get_style_props()
    if ff is None:
        return
    role = front_obj.get('hb_part_role')
    pool = (ff.drawer_front_styles if role in _DRAWER_FRONT_ROLES
            else ff.door_styles)
    for ds in pool:
        if ds.name == name:
            try:
                ds.assign_style_to_front(front_obj)
            except Exception:
                pass
            return


def _door_frame_for_dialog(op):
    if not op.source_obj_name:
        return None
    return bpy.data.objects.get(op.source_obj_name)


def _front_panel_openings(front):
    """Live interior-panel (opening) heights of a 5-piece front for a
    read-only readout. Reads the 'Door Style' modifier + the cutpart Length,
    so it reflects the rendered geometry regardless of the mid-rail mode (the
    Set Door Frame dialog is live-bound, so the modifier already carries any
    pending edit). The rail spans [loc - Rm/2, loc + Rm/2] about its centerline
    loc within the [0, L] door.

    Returns (bottom_opening, top_opening) in metres when a mid rail is present,
    (full_opening, None) when it isn't, or None if the front can't be read.
    """
    mod = _door_style_mod(front)
    if front is None or mod is None:
        return None
    try:
        length = GeoNodeCutpart(front).get_input("Length")
    except Exception:
        return None
    top_rail = _mod_input_get(mod, "Top Rail Width", 0.0)
    bottom_rail = _mod_input_get(mod, "Bottom Rail Width", 0.0)
    if not _mod_input_get(mod, "Add Mid Rail", False):
        return (length - top_rail - bottom_rail, None)
    half = _mod_input_get(mod, "Mid Rail Width", 0.0) / 2.0
    if _mod_input_get(mod, "Center Mid Rail", True):
        loc = length / 2.0
    else:
        loc = _mod_input_get(mod, "Mid Rail Location", length / 2.0)
    bottom_opening = (loc - half) - bottom_rail
    top_opening = (length - top_rail) - (loc + half)
    return (bottom_opening, top_opening)


def _frame_store(front_obj):
    """Persistent home for a front's locked frame data: its OPENING cage,
    which survives the per-recalc front rebuild (the front itself does not).
    A cage-less front (bare door part) is its own store. Mirrors
    props_hb_face_frame._front_frame_store."""
    o = front_obj.parent
    while o is not None:
        if o.get('IS_FACE_FRAME_OPENING_CAGE'):
            return o
        o = o.parent
    return front_obj


def _reapply_frame_store(store, picked_front):
    """Re-apply the style to every front the store governs (an opening cage
    governs all its leaves; a cage-less front, only itself)."""
    if store is picked_front:
        _reapply_front_style(picked_front)
        return
    for o in store.children_recursive:
        if o.get('hb_part_role') in ('DOOR', 'DRAWER_FRONT', 'PULLOUT_FRONT', 'FALSE_FRONT'):
            _reapply_front_style(o)


def _on_df_left_stile(self, context):
    front = _door_frame_for_dialog(self)
    if front is not None:
        store = _frame_store(front)
        store['HB_FRAME_OVR_LEFT_STILE'] = self.left_stile
        _reapply_frame_store(store, front)


def _on_df_right_stile(self, context):
    front = _door_frame_for_dialog(self)
    if front is not None:
        store = _frame_store(front)
        store['HB_FRAME_OVR_RIGHT_STILE'] = self.right_stile
        _reapply_frame_store(store, front)


def _on_df_top_rail(self, context):
    front = _door_frame_for_dialog(self)
    if front is not None:
        store = _frame_store(front)
        store['HB_FRAME_OVR_TOP_RAIL'] = self.top_rail
        _reapply_frame_store(store, front)


def _on_df_bottom_rail(self, context):
    front = _door_frame_for_dialog(self)
    if front is not None:
        store = _frame_store(front)
        store['HB_FRAME_OVR_BOTTOM_RAIL'] = self.bottom_rail
        _reapply_frame_store(store, front)


# Mid Rail modes whose Location field carries a user-entered value (vs. the
# fraction presets and Centered, which derive the position analytically).
# CUSTOM = location from the bottom; TOP_PANEL / BOTTOM_PANEL = the interior
# panel (opening) height that side of the rail, which the solver converts to
# a centerline location once the rail widths are known.
_MID_RAIL_VALUE_MODES = {'CUSTOM', 'TOP_PANEL', 'BOTTOM_PANEL'}


def _on_df_mid_mode(self, context):
    front = _door_frame_for_dialog(self)
    if front is not None:
        store = _frame_store(front)
        store['HB_FRAME_OVR_MID_RAIL_MODE'] = self.mid_rail_mode
        if self.mid_rail_mode in _MID_RAIL_VALUE_MODES:
            store['HB_FRAME_OVR_MID_RAIL_LOCATION'] = self.mid_rail_location
        _reapply_frame_store(store, front)


def _on_df_mid_loc(self, context):
    front = _door_frame_for_dialog(self)
    if front is not None:
        store = _frame_store(front)
        store['HB_FRAME_OVR_MID_RAIL_LOCATION'] = self.mid_rail_location
        if store.get('HB_FRAME_OVR_MID_RAIL_MODE') in _MID_RAIL_VALUE_MODES:
            _reapply_frame_store(store, front)


def _on_df_lock(self, context):
    """Lock pins the whole interface: snapshot the shown values onto the
    OPENING-cage store and flag it locked so the solver honors them on every
    recalc (the front object is rebuilt each recalc, so the data can't live
    on the front). Unlock clears the flag (values kept dormant)."""
    front = _door_frame_for_dialog(self)
    if front is None:
        return
    store = _frame_store(front)
    if self.lock_frame:
        store['HB_FRAME_OVR_LEFT_STILE'] = self.left_stile
        store['HB_FRAME_OVR_RIGHT_STILE'] = self.right_stile
        store['HB_FRAME_OVR_TOP_RAIL'] = self.top_rail
        store['HB_FRAME_OVR_BOTTOM_RAIL'] = self.bottom_rail
        store['HB_FRAME_OVR_MID_RAIL_MODE'] = self.mid_rail_mode
        store['HB_FRAME_OVR_MID_RAIL_LOCATION'] = self.mid_rail_location
        store['HB_FRAME_FRAME_LOCKED'] = True
    else:
        store['HB_FRAME_FRAME_LOCKED'] = False
    _reapply_frame_store(store, front)


class hb_face_frame_OT_set_door_frame(bpy.types.Operator):
    """Set a 5-piece front's stile / rail widths (per side) and mid rail.

    Lock Frame pins the WHOLE interface: the values are stored as durable
    HB_FRAME_OVR_* props and the front is flagged HB_FRAME_FRAME_LOCKED, so
    the solver honors them on every recalc (a cabinet edit can't overwrite
    them). Unlocked, the fields are greyed and the front follows its door
    style (recomputed on any cabinet change). Live-bound like the other
    Set-* dialogs. Mid Rail mode: CENTERED, THIRD (1/3 - 2/3 -> rail near
    the top), or CUSTOM (uses Location).
    """
    bl_idname = "hb_face_frame.set_door_frame"
    bl_label = "Set Door Frame"
    bl_description = "Override this front's stile, rail, and mid rail"
    bl_options = {'UNDO'}

    source_obj_name: StringProperty(default='', options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore

    lock_frame: bpy.props.BoolProperty(
        name="Lock Frame",
        description="Pin these stile / rail / mid rail values so cabinet edits don't overwrite them",
        default=False, update=_on_df_lock)  # type: ignore

    left_stile: FloatProperty(name="Left Stile", unit='LENGTH', precision=4, min=0.0,
                              update=_on_df_left_stile)  # type: ignore
    right_stile: FloatProperty(name="Right Stile", unit='LENGTH', precision=4, min=0.0,
                               update=_on_df_right_stile)  # type: ignore
    top_rail: FloatProperty(name="Top Rail", unit='LENGTH', precision=4, min=0.0,
                            update=_on_df_top_rail)  # type: ignore
    bottom_rail: FloatProperty(name="Bottom Rail", unit='LENGTH', precision=4, min=0.0,
                               update=_on_df_bottom_rail)  # type: ignore
    mid_rail_mode: bpy.props.EnumProperty(
        name="Mid Rail",
        items=[('NONE', "None", "No mid rail (overrides the style and the tall-door auto rail)"),
               ('CENTERED', "Centered", "Mid rail centered vertically"),
               ('THIRD', "1/3 - 2/3", "Mid rail 2/3 up from the bottom (top opening 1/3, bottom 2/3)"),
               ('QUARTER', "1/4 - 3/4", "Mid rail 3/4 up from the bottom (top opening 1/4, bottom 3/4)"),
               ('CUSTOM', "Custom", "Mid rail centerline at a custom distance from the bottom"),
               ('TOP_PANEL', "Set Top Panel Height", "Position the mid rail so the top interior panel matches the entered height"),
               ('BOTTOM_PANEL', "Set Bottom Panel Height", "Position the mid rail so the bottom interior panel matches the entered height")],
        default='CENTERED',
        update=_on_df_mid_mode)  # type: ignore
    mid_rail_location: FloatProperty(name="Location", unit='LENGTH', precision=4, min=0.0,
                                     update=_on_df_mid_loc)  # type: ignore

    @classmethod
    def poll(cls, context):
        return has_door_style_modifier(context.active_object)

    def invoke(self, context, event):
        obj = context.active_object
        mod = _door_style_mod(obj)
        store = _frame_store(obj)
        locked = bool(store.get('HB_FRAME_FRAME_LOCKED', False))
        # Seed BEFORE source_obj_name is set so the callbacks bail and the
        # seed writes don't fan back. Locked -> show the pinned store values;
        # unlocked -> show the front's live (style-driven) modifier values.
        def seed(ovr_key, mod_name):
            if locked and ovr_key in store.keys():
                return store[ovr_key]
            return _mod_input_get(mod, mod_name, 0.0)
        self.left_stile = seed('HB_FRAME_OVR_LEFT_STILE', "Left Stile Width")
        self.right_stile = seed('HB_FRAME_OVR_RIGHT_STILE', "Right Stile Width")
        self.top_rail = seed('HB_FRAME_OVR_TOP_RAIL', "Top Rail Width")
        self.bottom_rail = seed('HB_FRAME_OVR_BOTTOM_RAIL', "Bottom Rail Width")
        mode = store.get('HB_FRAME_OVR_MID_RAIL_MODE') if locked else None
        if not mode:
            if not _mod_input_get(mod, "Add Mid Rail", False):
                mode = 'NONE'
            else:
                mode = 'CENTERED' if _mod_input_get(mod, "Center Mid Rail", True) else 'CUSTOM'
        self.mid_rail_mode = mode
        if locked and 'HB_FRAME_OVR_MID_RAIL_LOCATION' in store.keys():
            self.mid_rail_location = store['HB_FRAME_OVR_MID_RAIL_LOCATION']
        else:
            self.mid_rail_location = _mod_input_get(mod, "Mid Rail Location", 0.0)
        self.lock_frame = locked
        self.source_obj_name = obj.name
        return context.window_manager.invoke_props_dialog(self, width=260)

    def draw(self, context):
        col = self.layout.column()
        col.prop(self, 'lock_frame')
        body = col.column(align=True)
        body.enabled = self.lock_frame  # unlocked -> greyed, front follows the style
        body.prop(self, 'left_stile')
        body.prop(self, 'right_stile')
        body.prop(self, 'top_rail')
        body.prop(self, 'bottom_rail')
        body.separator()
        body.prop(self, 'mid_rail_mode')
        row = body.row()
        row.enabled = self.mid_rail_mode in _MID_RAIL_VALUE_MODES
        # The same field carries a from-bottom location (CUSTOM) or an interior
        # panel height (TOP_PANEL / BOTTOM_PANEL); relabel to match the mode.
        loc_label = {'TOP_PANEL': "Top Panel Height",
                     'BOTTOM_PANEL': "Bottom Panel Height"}.get(self.mid_rail_mode, "Location")
        row.prop(self, 'mid_rail_location', text=loc_label)

        # Read-only readout of the resulting interior-panel heights. Lives in
        # the always-enabled column (not the lock-greyed body) so it's visible
        # whether the frame is locked or following its style.
        openings = _front_panel_openings(_door_frame_for_dialog(self))
        if openings is not None:
            bottom_opening, top_opening = openings
            us = context.scene.unit_settings
            box = col.box()
            box.label(text="Panel Heights")
            if top_opening is None:
                box.label(text="Panel:  " + units.unit_to_string(us, bottom_opening))
            else:
                box.label(text="Top Panel:  " + units.unit_to_string(us, top_opening))
                box.label(text="Bottom Panel:  " + units.unit_to_string(us, bottom_opening))

    def execute(self, context):
        # Live-bound via the prop update callbacks; nothing to do on OK.
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Set Size  (any cabinet cutpart: direct GeoNode Length / Width / Thickness).
# Transient for solver-driven parts - overwritten on the next recalc. A
# durable override path will come later.
# ---------------------------------------------------------------------------

def _cabinet_part_for_dialog(op):
    if not op.source_obj_name:
        return None
    return bpy.data.objects.get(op.source_obj_name)


def _is_cutpart(obj):
    """True if obj is a GeoNodeCutpart-style part (exposes a Length input)."""
    if obj is None:
        return False
    try:
        return GeoNodeCutpart(obj).get_input('Length') is not None
    except Exception:
        return False


def _on_size_width(self, context):
    obj = _cabinet_part_for_dialog(self)
    if obj is not None:
        GeoNodeCutpart(obj).set_input('Length', self.part_width)


def _on_size_depth(self, context):
    obj = _cabinet_part_for_dialog(self)
    if obj is not None:
        GeoNodeCutpart(obj).set_input('Width', self.part_depth)


def _on_size_thickness(self, context):
    obj = _cabinet_part_for_dialog(self)
    if obj is not None:
        GeoNodeCutpart(obj).set_input('Thickness', self.part_thickness)


class hb_face_frame_OT_set_cabinet_part_size(bpy.types.Operator):
    """Set any cabinet part's size by editing its cutpart GeoNode inputs
    directly. Live-bound (same pattern as the Misc Part dialog). Note: for
    parts the solver drives, this is transient - the next recalc resets it."""
    bl_idname = "hb_face_frame.set_cabinet_part_size"
    bl_label = "Set Size"
    bl_description = "Set this part's width, depth, and thickness"
    bl_options = {'UNDO'}

    source_obj_name: StringProperty(default='', options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore

    part_width: FloatProperty(name="Width", unit='LENGTH', precision=4, min=0.0,
                              update=_on_size_width)  # type: ignore
    part_depth: FloatProperty(name="Depth", unit='LENGTH', precision=4, min=0.0,
                              update=_on_size_depth)  # type: ignore
    part_thickness: FloatProperty(name="Thickness", unit='LENGTH', precision=4, min=0.0,
                                  update=_on_size_thickness)  # type: ignore

    @classmethod
    def poll(cls, context):
        return _is_cutpart(context.active_object)

    def invoke(self, context, event):
        obj = context.active_object
        part = GeoNodeCutpart(obj)
        self.part_width = part.get_input('Length')
        self.part_depth = part.get_input('Width')
        self.part_thickness = part.get_input('Thickness')
        self.source_obj_name = obj.name
        return context.window_manager.invoke_props_dialog(self, width=260)

    def draw(self, context):
        col = self.layout.column(align=True)
        col.prop(self, 'part_width')
        col.prop(self, 'part_depth')
        col.prop(self, 'part_thickness')

    def execute(self, context):
        return {'FINISHED'}


# Cutpart inputs the recalc dispatch does NOT re-apply. It rewrites
# Length / Width / Thickness / position / rotation every pass, but the
# Mirror flags are set ONCE at part creation - so a part made editable and
# later reverted renders with the wrong mirroring unless we stash the mirror
# values and restore them. L/W/T are stashed too so downstream readers
# (shop dims / cut list) have a fallback while the part is manual.
_MANUAL_STASH_INPUTS = (
    ('HB_MANUAL_LENGTH', 'Length'),
    ('HB_MANUAL_WIDTH', 'Width'),
    ('HB_MANUAL_THICKNESS', 'Thickness'),
    ('HB_MANUAL_MIRROR_X', 'Mirror X'),
    ('HB_MANUAL_MIRROR_Y', 'Mirror Y'),
    ('HB_MANUAL_MIRROR_Z', 'Mirror Z'),
)
_MANUAL_MIRROR_INPUTS = _MANUAL_STASH_INPUTS[3:]
_MANUAL_STASH_KEYS = tuple(k for k, _ in _MANUAL_STASH_INPUTS)


def _stash_part_inputs(obj):
    """Record a part's cutpart inputs as HB_MANUAL_* props before its GN is
    applied, so Revert can rebuild it faithfully - the Mirror flags in
    particular, which recalc never re-applies."""
    try:
        gn = GeoNodeCutpart(obj)
    except Exception:
        return
    for key, inp in _MANUAL_STASH_INPUTS:
        try:
            obj[key] = gn.get_input(inp)
        except Exception:
            pass


def _restore_mirror_inputs(obj):
    """Re-apply stashed Mirror X/Y/Z to a freshly re-added cutpart GN on
    Revert. No-op without a stash (a part applied by hand outside Make
    Editable keeps the GN's default mirrors)."""
    try:
        gn = GeoNodeCutpart(obj)
    except Exception:
        return
    for key, inp in _MANUAL_MIRROR_INPUTS:
        if key in obj.keys():
            gn.set_input(inp, bool(obj[key]))


def _is_manual_part(obj):
    """True if obj is a face-frame part currently under manual control.
    Misc Parts carry no hb_part_role; their tag qualifies them instead."""
    return bool(obj and obj.get('IS_MANUAL_PART')
                and (obj.get('hb_part_role')
                     or obj.get('IS_FACE_FRAME_MISC_PART')))


# Door / drawer front roles. Fronts are a SEPARATE editable path from
# structural cutparts: a front object is torn down and rebuilt on every
# recalc, so its 'manual' state is stored on the OPENING cage (IS_MANUAL_FRONT,
# which survives the rebuild) and the front-rebuild + door-style passes skip a
# manual opening (types_face_frame._update_fronts_in_opening,
# props_hb_face_frame._apply_door_styles_to_fronts).
_FRONT_EDITABLE_ROLES = frozenset({
    'DOOR', 'DRAWER_FRONT', 'PULLOUT_FRONT', 'FALSE_FRONT',
})


def _front_opening_cage(obj):
    """Walk up to the front's Opening cage (the durable anchor), or None."""
    p = obj
    while p is not None:
        if p.get('IS_FACE_FRAME_OPENING_CAGE'):
            return p
        p = p.parent
    return None


def _can_make_editable(obj):
    """True if obj is a STRUCTURAL cutpart that can be made editable: a MESH
    cutpart with its modifier present, not already manual, and not a front
    (fronts go through the front path). Face-frame parts qualify by part role;
    wood-hood cutparts and Misc Parts qualify by their tags (no role)."""
    if obj is None or obj.type != 'MESH':
        return False
    if obj.get('IS_MANUAL_PART'):
        return False
    if has_door_style_modifier(obj):
        return False
    if not (obj.get('IS_WOOD_HOOD_PART')
            or obj.get('IS_FACE_FRAME_MISC_PART')):
        # Face-frame parts must carry a non-front part role.
        role = obj.get('hb_part_role')
        if not role or role in _FRONT_EDITABLE_ROLES:
            return False
    mn = obj.home_builder.mod_name
    return bool(mn) and mn in obj.modifiers


def _can_make_front_editable(obj):
    """True if obj is a door / drawer front that can be made editable: a MESH
    front (FRONT roles) with an Opening cage ancestor, not already manual."""
    if obj is None or obj.type != 'MESH':
        return False
    if obj.get('IS_MANUAL_PART'):
        return False
    if obj.get('hb_part_role') not in _FRONT_EDITABLE_ROLES:
        return False
    return _front_opening_cage(obj) is not None


class hb_face_frame_OT_make_part_editable(bpy.types.Operator):
    """Apply a part's GeoNode(s) so its mesh becomes real, editable geometry
    and flag it as manual, so the cabinet recalc leaves it alone (it keeps its
    position / dims / rotation and stops following width / depth / style
    changes). Two paths:

    - STRUCTURAL cutpart (side / rail / stile / top / bottom / ...): apply the
      cutpart modifier, flag IS_MANUAL_PART on the part. The recalc dispatch
      skips it (CONVENTIONS - manual parts).
    - DOOR / DRAWER FRONT: a front is torn down and rebuilt every recalc, so
      flag IS_MANUAL_FRONT on the OPENING cage (which survives the rebuild) and
      IS_MANUAL_PART on the front; the front-rebuild + door-style passes skip a
      manual opening, so the applied front persists.

    Use Revert to Parametric to restore either."""
    bl_idname = "hb_face_frame.make_part_editable"
    bl_label = "Make Editable"
    bl_description = ("Apply this part's geometry so it can be edited in Edit "
                      "Mode. The part will stop following cabinet changes")
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        # Enabled when ANY selected object is editable - structural cutpart or
        # door / drawer front - so a multi-selection applies in one click.
        return any(_can_make_editable(o) or _can_make_front_editable(o)
                   for o in context.selected_objects)

    @staticmethod
    def _apply_one(context, obj):
        """Apply one STRUCTURAL part's cutpart GeoNode and flag it manual."""
        mn = obj.home_builder.mod_name
        # Stash the parametric state BEFORE applying so Revert can restore it.
        # Hood cutparts have no cabinet recalc to re-drive them, so snapshot the
        # full recipe (inputs + drivers + transform); face-frame parts only need
        # the inputs the recalc reads back.
        if obj.get('IS_WOOD_HOOD_PART'):
            from ...common import wood_hoods
            wood_hoods.snapshot_hood_part(obj)
        else:
            _stash_part_inputs(obj)
        # Apply only the cutpart modifier; any downstream system modifier
        # (e.g. a corner notch) stays live on top of the now-real mesh.
        with context.temp_override(object=obj, active_object=obj,
                                   selected_objects=[obj]):
            bpy.ops.object.modifier_apply(modifier=mn)
        obj['IS_MANUAL_PART'] = True

    @staticmethod
    def _apply_front_one(context, obj):
        """Bake a door / drawer front: apply every NODES modifier (cutpart +
        Door Style) to real mesh, then flag the front AND its opening cage so
        the recalc stops rebuilding it. No dim / mirror stash is needed -
        Revert lets the solver rebuild the front from scratch."""
        for mname in [m.name for m in obj.modifiers if m.type == 'NODES']:
            if mname in obj.modifiers:
                with context.temp_override(object=obj, active_object=obj,
                                           selected_objects=[obj]):
                    bpy.ops.object.modifier_apply(modifier=mname)
        obj['IS_MANUAL_PART'] = True
        cage = _front_opening_cage(obj)
        if cage is not None:
            cage['IS_MANUAL_FRONT'] = True

    def execute(self, context):
        # Snapshot eligible targets before mutating (applying a modifier
        # changes what _can_make_* returns). Fall back to the active object.
        pool = list(context.selected_objects) or [context.active_object]
        structural = [o for o in pool if _can_make_editable(o)]
        fronts = [o for o in pool if _can_make_front_editable(o)]
        if not structural and not fronts:
            self.report({'WARNING'}, "No editable parts selected")
            return {'CANCELLED'}
        for obj in structural:
            self._apply_one(context, obj)
        for obj in fronts:
            self._apply_front_one(context, obj)
        n = len(structural) + len(fronts)
        self.report({'INFO'},
                    f"{n} part(s) editable - parametric updates off")
        return {'FINISHED'}


class hb_face_frame_OT_revert_part_to_parametric(bpy.types.Operator):
    """Discard manual edits and restore a part to parametric control, then
    recalc so it follows the cabinet's width / depth / style again. A
    STRUCTURAL part is rebuilt in place (re-add its cutpart GN, restore the
    stashed mirror flags). A DOOR / DRAWER FRONT is rebuilt from scratch by
    the recalc once its opening's IS_MANUAL_FRONT flag is cleared. Hand-edited
    geometry is lost."""
    bl_idname = "hb_face_frame.revert_part_to_parametric"
    bl_label = "Revert to Parametric"
    bl_description = ("Discard manual edits and let this part follow cabinet "
                      "changes again. Hand edits are lost")
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        # Enabled when ANY selected object is a manual part, so a batch can
        # be reverted in one click.
        return any(_is_manual_part(o) for o in context.selected_objects)

    @staticmethod
    def _revert_one(obj, ng):
        """Restore one manual part to parametric control.

        Front: clear IS_MANUAL_FRONT on the opening cage (+ the front's
        IS_MANUAL_PART); the cabinet recalc then wipes the baked front and
        rebuilds it fresh - no in-place work needed here.

        Structural: rebuild in place - re-add the cutpart GN and restore the
        stashed mirror flags (recalc rewrites L/W/T/position but not mirrors).
        """
        cage = _front_opening_cage(obj)
        if obj.get('hb_part_role') in _FRONT_EDITABLE_ROLES and cage is not None:
            if 'IS_MANUAL_FRONT' in cage.keys():
                del cage['IS_MANUAL_FRONT']
            if 'IS_MANUAL_PART' in obj.keys():
                del obj['IS_MANUAL_PART']
            return
        obj.modifiers.clear()
        obj.data.clear_geometry()
        mod = obj.modifiers.new(name='GeoNodeCutpart', type='NODES')
        mod.node_group = ng
        mod.show_viewport = True
        obj.home_builder.mod_name = mod.name
        _restore_mirror_inputs(obj)
        # A Misc Part has no cabinet recalc to rewrite Length / Width /
        # Thickness afterwards, so restore them from the stash directly.
        if obj.get('IS_FACE_FRAME_MISC_PART'):
            gn = GeoNodeCutpart(obj)
            for key, inp in _MANUAL_STASH_INPUTS[:3]:
                if key in obj.keys():
                    gn.set_input(inp, obj[key])
        for key in ('IS_MANUAL_PART',) + _MANUAL_STASH_KEYS:
            if key in obj.keys():
                del obj[key]

    def execute(self, context):
        ng = bpy.data.node_groups.get('GeoNodeCutpart')
        if ng is None:
            self.report({'ERROR'}, "GeoNodeCutpart node group not loaded")
            return {'CANCELLED'}
        targets = [o for o in context.selected_objects if _is_manual_part(o)]
        if not targets and _is_manual_part(context.active_object):
            targets = [context.active_object]
        if not targets:
            self.report({'WARNING'}, "No manual parts selected")
            return {'CANCELLED'}
        # Revert each in place, then recalc each affected cabinet ONCE.
        roots = {}
        for obj in targets:
            self._revert_one(obj, ng)
            root = types_face_frame.find_cabinet_root(obj)
            if root is not None:
                roots[root.name] = root
        for root in roots.values():
            types_face_frame.recalculate_face_frame_cabinet(root)
        self.report({'INFO'},
                    f"{len(targets)} part(s) restored to parametric")
        return {'FINISHED'}


class hb_face_frame_OT_remove_mid_rail(bpy.types.Operator):
    """Remove the mid rail the user clicked. The opening stays SPLIT - only
    the face-frame member and its carcass backing are dropped, and the solver
    collapses the splitter space so the two (typically drawer) fronts close to
    a 3/32" reveal (MID_RAIL_REMOVED_GAP in solver_face_frame).

    Stored as remove_member on the owning split node's per-splitter entry,
    keyed by the part's hb_splitter_index, so it survives recalc. The rail
    object is gone afterward and can't be right-clicked - rebuild the bay via
    Change Bay if it's needed back.
    """
    bl_idname = "hb_face_frame.remove_mid_rail"
    bl_label = "Remove Mid Rail"
    bl_description = (
        "Remove this mid rail. Keeps the split; drops the member + its backing "
        "and closes the two fronts to a 3/32\" gap"
    )
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj is not None
                and obj.get('hb_part_role')
                == types_face_frame.PART_ROLE_BAY_MID_RAIL)

    def execute(self, context):
        obj = context.active_object
        split = _find_owning_split_node(obj)
        if split is None:
            self.report({'WARNING'}, "No split node found for this mid rail")
            return {'CANCELLED'}
        # Lazily grow the per-splitter collection to cover this index, then
        # set remove_member (its update callback fires the cabinet recalc).
        idx = obj.get('hb_splitter_index', 0)
        coll = split.face_frame_split.splitter_widths
        while len(coll) <= idx:
            coll.add()
        coll[idx].remove_member = True
        return {'FINISHED'}


_SIDE_PANEL_ROLES = frozenset({
    types_face_frame.PART_ROLE_LEFT_SIDE,
    types_face_frame.PART_ROLE_RIGHT_SIDE,
    # Corner cabs tag their exposed sides with corner-specific roles. The
    # operator edits cabinet-level finished-end props via find_cabinet_root,
    # so it works for corners once the side panel is reachable here.
    types_face_frame_corner.PART_ROLE_CORNER_LEFT_SIDE,
    types_face_frame_corner.PART_ROLE_CORNER_RIGHT_SIDE,
})


class hb_face_frame_OT_set_finished_end_condition(bpy.types.Operator):
    """Set the finished-end condition for the clicked side panel.

    Launched from a left / right carcass side's right-click menu. Resolves
    the side from the clicked part's role and shows only that side's
    finished-end type enum (plus the flush-X amount when FLUSH_X is chosen).
    Editing the enum fires its existing update callback, which flips that
    side's finish-end auto flag off so exposure detection won't clobber the
    user's choice.
    """
    bl_idname = "hb_face_frame.set_finished_end_condition"
    bl_label = "Set Finished End Condition"
    bl_description = "Set the finished-end condition for this side"
    bl_options = {'UNDO'}

    side: bpy.props.EnumProperty(
        name="Side",
        items=[('LEFT', "Left", ""), ('RIGHT', "Right", "")],
        default='LEFT',
    )  # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj is None:
            return False
        return obj.get('hb_part_role') in _SIDE_PANEL_ROLES

    def invoke(self, context, event):
        # The clicked side panel is the active object; derive the side from
        # its role so the dialog edits the matching cabinet prop.
        obj = context.active_object
        if (obj is not None
                and obj.get('hb_part_role') in (
                    types_face_frame.PART_ROLE_RIGHT_SIDE,
                    types_face_frame_corner.PART_ROLE_CORNER_RIGHT_SIDE)):
            self.side = 'RIGHT'
        else:
            self.side = 'LEFT'
        return context.window_manager.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        root = types_face_frame.find_cabinet_root(context.active_object)
        if root is None:
            layout.label(text="No face frame cabinet selected", icon='INFO')
            return
        cab = root.face_frame_cabinet
        key = self.side.lower()
        fin_type = getattr(cab, f'{key}_finished_end_condition')
        layout.prop(cab, f'{key}_finished_end_condition',
                    text=f"{self.side.title()} Finished End")
        # FLUSH_X needs its strip width to be meaningful.
        if fin_type == 'FLUSH_X':
            layout.prop(cab, f'{key}_flush_x_amount', text="Flush Amount")
        # Mirror the Finished Ends prompt (draw_finished_ends): a side
        # that carries a finished part can extend back, and once it is
        # extended past a FINISHED / PANELED back, a nonzero return
        # width caps the exposed corner with a return panel + rear
        # stile (per-member construction types appear once a return
        # exists). The dialog redraws live, so the fields follow the
        # enum as the user edits.
        if fin_type not in ('UNFINISHED', 'FLUSH_X'):
            layout.prop(cab, f'{key}_side_finished_extend_back',
                        text="Extend Back")
        if (fin_type in ('FINISHED', 'PANELED')
                and getattr(cab, f'{key}_side_finished_extend_back') != 0.0
                and cab.back_finished_end_condition
                in ('FINISHED', 'PANELED')):
            layout.prop(cab, f'{key}_side_return_width',
                        text="Return Width")
            if getattr(cab, f'{key}_side_return_width') != 0.0:
                layout.prop(cab, f'{key}_side_return_panel_type',
                            text="Side Return")
                layout.prop(cab, f'{key}_side_return_stile_type',
                            text="Return Stile")

    def execute(self, context):
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Machining cutout (CPM_CUTOUT) - user-added rectangular hole / route on a part
# ---------------------------------------------------------------------------
_CUTOUT_TOKEN = 'CPM_CUTOUT'
_CUTOUT_NAME = 'Cutout'


def _cutpart_modifier(obj):
    """The base GeoNodeCutpart modifier on a parametric part, or None. Machining
    cutouts read the part's Length / Width / Thickness from it to place and size
    the cut, so a part without it (bare / applied mesh) is not eligible in v1."""
    if obj is None or obj.type != 'MESH':
        return None
    for m in obj.modifiers:
        if (m.type == 'NODES' and m.node_group
                and m.node_group.name == 'GeoNodeCutpart'):
            return m
    return None


def _is_cutpart(obj):
    """True when a machining cutout can be added to obj."""
    return _cutpart_modifier(obj) is not None


def _user_cutout_mods(obj):
    """User-added CPM_CUTOUT modifiers on obj, in stack order. Named with the
    'Cutout' prefix so they stay distinct from system CPM_CUTOUT uses (e.g. the
    appliance-panel 'Flange *' strips)."""
    if obj is None:
        return []
    return [m for m in obj.modifiers
            if (m.type == 'NODES' and m.node_group
                and m.node_group.name == _CUTOUT_TOKEN
                and m.name.split('.')[0] == _CUTOUT_NAME)]


def _unique_cutout_name(obj):
    existing = {m.name for m in obj.modifiers}
    if _CUTOUT_NAME not in existing:
        return _CUTOUT_NAME
    i = 1
    while f"{_CUTOUT_NAME}.{i:03d}" in existing:
        i += 1
    return f"{_CUTOUT_NAME}.{i:03d}"


def _cutout_part_for_dialog(op):
    """The part a live Add-Cutout dialog is editing (resolved by name each tick;
    None while source_obj_name is unset - see the Misc / Door Part dialogs)."""
    if not op.source_obj_name:
        return None
    return bpy.data.objects.get(op.source_obj_name)


def _apply_cutout_live(op):
    """Recompute + write the live cutout's inputs from the operator's fields so
    the viewport updates as the dialog changes. Bails while source_obj_name /
    mod_name are unset (during invoke seeding)."""
    obj = _cutout_part_for_dialog(op)
    if obj is None or not op.mod_name:
        return
    mod = obj.modifiers.get(op.mod_name)
    if mod is None:
        return
    part = GeoNodeCutpart(obj)
    try:
        length = part.get_input('Length')
        width = part.get_input('Width')
        thickness = part.get_input('Thickness')
    except Exception:
        return
    cl = max(min(op.cutout_length, length), 0.0)
    cw = max(min(op.cutout_width, width), 0.0)
    if cl <= 0.0 or cw <= 0.0:
        return
    if op.center:
        x0 = (length - cl) / 2.0
        y0 = (width - cw) / 2.0
    else:
        x0 = op.offset_length
        y0 = op.offset_width
    # Keep the rectangle inside the part face.
    x0 = min(max(x0, 0.0), length - cl)
    y0 = min(max(y0, 0.0), width - cw)
    depth = thickness if op.through else min(op.route_depth, thickness)
    cpm = CabinetPartModifier(obj)
    cpm.mod = mod
    cpm.set_input('X', x0)
    cpm.set_input('End X', x0 + cl)
    cpm.set_input('Y', y0)
    cpm.set_input('End Y', y0 + cw)
    cpm.set_input('Route Depth', depth)
    cpm.set_input('Flip Z', op.back_face)
    mod.show_viewport = True
    mod.show_render = True
    obj.update_tag()


def _on_cutout_field_update(self, context):
    _apply_cutout_live(self)


class hb_face_frame_OT_add_part_cutout(bpy.types.Operator):
    """Cut a rectangular hole or route into this part - a fan / liner opening,
    a light route, an outlet cutout. The cut shows in 3D and in the 2D drawing
    (a rotated copy of the part reveals it), so no detail view is needed. The
    cutout is built immediately and updates LIVE as the dialog fields change;
    Cancel leaves it in place (drop it with Remove Cutout)."""
    bl_idname = "hb_face_frame.add_part_cutout"
    bl_label = "Add Cutout"
    bl_description = ("Cut a rectangular hole or route into this part "
                      "(fan/liner opening, light route, outlet)")
    bl_options = {'REGISTER', 'UNDO'}

    # Live-dialog binding: the cutout is created on invoke and each field write
    # fans straight to its CPM_CUTOUT inputs (same pattern as the Misc / Door
    # Part dimension dialogs). Target resolved by name each tick.
    source_obj_name: StringProperty(default='', options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore
    mod_name: StringProperty(default='', options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore

    cutout_length: FloatProperty(name="Length", unit='LENGTH', precision=4,
                                 min=0.0, default=units.inch(4.0),
                                 update=_on_cutout_field_update)  # type: ignore
    cutout_width: FloatProperty(name="Width", unit='LENGTH', precision=4,
                                min=0.0, default=units.inch(4.0),
                                update=_on_cutout_field_update)  # type: ignore
    center: BoolProperty(name="Center on Part", default=True,
                         update=_on_cutout_field_update)  # type: ignore
    offset_length: FloatProperty(name="Offset Along Length", unit='LENGTH',
                                 precision=4, min=0.0, default=0.0,
                                 update=_on_cutout_field_update)  # type: ignore
    offset_width: FloatProperty(name="Offset Along Width", unit='LENGTH',
                                precision=4, min=0.0, default=0.0,
                                update=_on_cutout_field_update)  # type: ignore
    through: BoolProperty(name="Through (Full Depth)", default=True,
                          update=_on_cutout_field_update)  # type: ignore
    route_depth: FloatProperty(name="Route Depth", unit='LENGTH', precision=4,
                               min=0.0, default=units.inch(0.25),
                               update=_on_cutout_field_update)  # type: ignore
    back_face: BoolProperty(name="Cut From Back Face", default=False,
                            update=_on_cutout_field_update)  # type: ignore

    @classmethod
    def poll(cls, context):
        return _is_cutpart(context.active_object)

    def invoke(self, context, event):
        obj = context.active_object
        part = GeoNodeCutpart(obj)
        try:
            length = part.get_input('Length')
            width = part.get_input('Width')
            thickness = part.get_input('Thickness')
        except Exception:
            self.report({'ERROR'}, "Part has no cutpart geometry to cut")
            return {'CANCELLED'}
        # Seed the fields BEFORE source_obj_name / mod_name are set: the update
        # callbacks bail while those are empty, so seeding can't fan back.
        self.cutout_length = min(units.inch(4.0), length)
        self.cutout_width = min(units.inch(4.0), width)
        self.center = True
        self.offset_length = 0.0
        self.offset_width = 0.0
        self.through = True
        self.route_depth = min(units.inch(0.25), thickness)
        self.back_face = False
        # Build the live cutout now so it previews as the dialog opens.
        name = _unique_cutout_name(obj)
        cpm = part.add_part_modifier(_CUTOUT_TOKEN, name)
        cpm.mod.show_viewport = True
        cpm.mod.show_render = True
        self.source_obj_name = obj.name
        self.mod_name = name
        _apply_cutout_live(self)
        return context.window_manager.invoke_props_dialog(self, width=280)

    def draw(self, context):
        col = self.layout.column(align=True)
        col.prop(self, 'cutout_length')
        col.prop(self, 'cutout_width')
        col.prop(self, 'center')
        if not self.center:
            col.prop(self, 'offset_length')
            col.prop(self, 'offset_width')
        col.separator()
        col.prop(self, 'through')
        if not self.through:
            col.prop(self, 'route_depth')
        col.prop(self, 'back_face')

    def execute(self, context):
        # Live-applied via the field update callbacks; the cutout already
        # exists, so OK just commits it.
        return {'FINISHED'}


class hb_face_frame_OT_remove_part_cutout(bpy.types.Operator):
    """Remove the most recently added machining cutout from this part."""
    bl_idname = "hb_face_frame.remove_part_cutout"
    bl_label = "Remove Cutout"
    bl_description = "Remove the last machining cutout added to this part"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return len(_user_cutout_mods(context.active_object)) > 0

    def execute(self, context):
        obj = context.active_object
        mods = _user_cutout_mods(obj)
        if not mods:
            self.report({'WARNING'}, "No cutout to remove")
            return {'CANCELLED'}
        obj.modifiers.remove(mods[-1])
        obj.update_tag()
        return {'FINISHED'}


class hb_face_frame_OT_set_bottom_rail_profile(bpy.types.Operator):
    """Set the cabinet's decorative bottom-rail profile from the right-click
    menu on a bottom rail. Sets the cabinet-level enum (one profile per
    cabinet); the update callback re-runs the recalc."""
    bl_idname = "hb_face_frame.set_bottom_rail_profile"
    bl_label = "Set Bottom Rail Profile"
    bl_description = "Cut this decorative profile into the cabinet's bottom rail"
    bl_options = {'UNDO'}

    profile_id: StringProperty(default='NONE', options={'SKIP_SAVE'})  # type: ignore

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        root = types_face_frame.find_cabinet_root(context.active_object)
        if root is None:
            self.report({'WARNING'}, "No cabinet found for this part")
            return {'CANCELLED'}
        try:
            root.face_frame_cabinet.bottom_rail_profile = self.profile_id
        except TypeError:
            self.report({'WARNING'}, f"Unknown profile: {self.profile_id}")
            return {'CANCELLED'}
        return {'FINISHED'}


classes = (
    hb_face_frame_OT_set_part_width,
    hb_face_frame_OT_set_finished_end_condition,
    hb_face_frame_OT_set_part_scribe,
    hb_face_frame_OT_toggle_stile_to_floor,
    hb_face_frame_OT_remove_bottom_rail,
    hb_face_frame_OT_remove_mid_rail,
    hb_face_frame_OT_set_misc_part_dimensions,
    hb_face_frame_OT_set_door_part_dimensions,
    hb_face_frame_OT_assign_active_door_style,
    hb_face_frame_OT_toggle_door_part_pull,
    hb_face_frame_OT_switch_door_part_pull_side,
    hb_face_frame_OT_toggle_door_part_front_kind,
    hb_face_frame_OT_set_door_frame,
    hb_face_frame_OT_set_cabinet_part_size,
    hb_face_frame_OT_make_part_editable,
    hb_face_frame_OT_revert_part_to_parametric,
    hb_face_frame_OT_add_part_cutout,
    hb_face_frame_OT_remove_part_cutout,
    hb_face_frame_OT_set_bottom_rail_profile,
)


register, unregister = bpy.utils.register_classes_factory(classes)
