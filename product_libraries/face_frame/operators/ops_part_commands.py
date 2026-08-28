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
import json
import os

import bpy
from bpy.props import (BoolProperty, BoolVectorProperty, EnumProperty,
                       FloatProperty, IntProperty, StringProperty)

from .. import types_face_frame
from .. import types_face_frame_corner
from .. import cabinet_column
from ....hb_types import GeoNodeCutpart, CabinetPartModifier
from .... import units
from .... import hb_utils


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

# Side panels that can be seamed, and the side each one means. Both
# pieces of an already-seamed panel are here so the joint can be moved
# or removed by clicking either board.
_SEAMABLE_SIDE_ROLES = {
    types_face_frame.PART_ROLE_LEFT_SIDE: 'LEFT',
    types_face_frame.PART_ROLE_RIGHT_SIDE: 'RIGHT',
    types_face_frame.PART_ROLE_LEFT_SIDE_SEAM: 'LEFT',
    types_face_frame.PART_ROLE_RIGHT_SIDE_SEAM: 'RIGHT',
}


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

def _rail_flush_kick(root, bay):
    """Kick-zone height folded into a FLUSH cabinet's bottom rail.

    FLUSH builds the bottom rail down to the floor at kick_height +
    bottom_rail_width (see solver bottom_rail_segments), so the width
    the user sees and types is the BUILT wide rail: display adds this
    amount and a commit subtracts it, keeping type-back-what-you-see a
    no-op. 0 for every other kick type. A bay the per-bay flush toggle
    locked at kick 0 already holds the full total in its rail width,
    so adding its (zero) kick stays correct.
    """
    cab = root.face_frame_cabinet
    if cab.cabinet_type not in ('BASE', 'TALL', 'LAP_DRAWER'):
        return 0.0
    if cab.corner_type != 'NONE' or cab.toe_kick_type != 'FLUSH':
        return 0.0
    if bay is not None:
        return bay.face_frame_bay.kick_height
    return cab.toe_kick_height


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
        width = (bay.face_frame_bay.bottom_rail_width
                 if bay else cab.bottom_rail_width)
        return width + _rail_flush_kick(root, bay)
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
        if cab.corner_type != 'NONE':
            # Corner cabinets have no bay cages; their recalc reads the
            # cabinet-level rail widths directly.
            return cab, 'top_rail_width'
        start = obj.get('hb_segment_start_bay', 0)
        bay = _find_bay_with_index(root, start)
        return (bay.face_frame_bay, 'top_rail_width') if bay else (None, None)
    if role == types_face_frame.PART_ROLE_BOTTOM_RAIL:
        if cab.corner_type != 'NONE':
            return cab, 'bottom_rail_width'
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
        unlock_attr = ('unlock_top_rail'
                       if role == types_face_frame.PART_ROLE_TOP_RAIL
                       else 'unlock_bottom_rail')
        if cab.corner_type != 'NONE':
            # Corner cabinets carry the rail width at cabinet level.
            setattr(cab, unlock_attr, True)
            return
        start = obj.get('hb_segment_start_bay', 0)
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
        attr = ('top_rail_width'
                if role == types_face_frame.PART_ROLE_TOP_RAIL
                else 'bottom_rail_width')
        if cab.corner_type != 'NONE':
            # Corner cabinets have no bay cages; their recalc reads the
            # cabinet-level rail widths directly.
            setattr(cab, attr, value)
            return
        start = obj.get('hb_segment_start_bay', 0)
        indices = _rail_segment_bay_indices(root, start, role)
        bays = _bays_by_index(root)
        for idx in indices:
            bay = bays.get(idx)
            if bay is not None:
                v = value
                if role == types_face_frame.PART_ROLE_BOTTOM_RAIL:
                    # The typed value is the BUILT wide rail on a FLUSH
                    # cabinet; store the rail's own share, floored at 0
                    # so a value under the kick height can't go negative.
                    v = max(value - _rail_flush_kick(root, bay), 0.0)
                setattr(bay.face_frame_bay, attr, v)
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
        unlock_attr = ('unlock_top_rail'
                       if role == types_face_frame.PART_ROLE_TOP_RAIL
                       else 'unlock_bottom_rail')
        if cab.corner_type != 'NONE':
            # Corner cabinets carry the rail width at cabinet level.
            setattr(cab, unlock_attr, False)
            return
        start = obj.get('hb_segment_start_bay', 0)
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


def seam_side_for(obj):
    """'LEFT' / 'RIGHT' when obj is a side panel that could be seamed,
    else None. Used by the menu so the item only shows on a panel the
    seam actually applies to."""
    if obj is None:
        return None
    return _SEAMABLE_SIDE_ROLES.get(obj.get('hb_part_role'))


def seam_available(obj):
    """True when the clicked side panel can carry a panel seam -- a
    FINISHED end on a square (non-angled, non-back-extended) cabinet.
    Everything else gets its finish from a separate part or is a splayed
    trapezoid, neither of which is the single board a seam divides."""
    side = seam_side_for(obj)
    if side is None:
        return False
    root = types_face_frame.find_cabinet_root(obj)
    if root is None:
        return False
    try:
        return types_face_frame.FaceFrameCabinet(root).side_seam_available(side)
    except Exception:
        return False


class hb_face_frame_OT_set_panel_seam(bpy.types.Operator):
    """Set the joint height of a seamed finished end.

    A finished end taller than the stock it is cut from has to be made
    from two boards. The height is measured from the cabinet bottom --
    the floor, on a floor-standing cabinet -- because that is the datum
    the shop reads off the elevation. Live-bound to the cabinet prop, so
    the panel splits as the number is typed; 0 puts it back to one piece.
    """
    bl_idname = "hb_face_frame.set_panel_seam"
    bl_label = "Set Panel Seam"
    bl_description = "Set the height this finished end is seamed at"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return seam_available(context.active_object)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)

    def draw(self, context):
        obj = context.active_object
        side = seam_side_for(obj)
        root = types_face_frame.find_cabinet_root(obj)
        if side is None or root is None:
            self.layout.label(text="No side panel selected", icon='INFO')
            return
        cab = root.face_frame_cabinet
        attr = ('left_side_seam_height' if side == 'LEFT'
                else 'right_side_seam_height')
        none_attr = ('left_side_no_seam' if side == 'LEFT'
                     else 'right_side_no_seam')
        no_seam = getattr(cab, none_attr, False)
        col = self.layout.column(align=True)
        col.label(text=f"{side.title()} Finished End", icon='MOD_SOLIDIFY')
        col.prop(cab, none_attr, text="No Seam")
        # Greyed rather than hidden, so the height that was typed is
        # still visible while the end is being built in one piece.
        row = col.row(align=True)
        row.enabled = not no_seam
        row.prop(cab, attr, text="Seam Height")
        col.separator()
        if no_seam:
            col.label(text="Built in one piece, whatever its length.",
                      icon='INFO')
        else:
            col.label(text="Measured up from the cabinet bottom.", icon='INFO')
            col.label(text="0 leaves the panel in one piece.")

    def execute(self, context):
        return {'FINISHED'}


class hb_face_frame_OT_remove_panel_seam(bpy.types.Operator):
    """Put a seamed finished end back to one board."""
    bl_idname = "hb_face_frame.remove_panel_seam"
    bl_label = "Remove Panel Seam"
    bl_description = "Build this finished end as a single panel again"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return seam_available(context.active_object)

    def execute(self, context):
        obj = context.active_object
        side = seam_side_for(obj)
        root = types_face_frame.find_cabinet_root(obj)
        if side is None or root is None:
            return {'CANCELLED'}
        cab = root.face_frame_cabinet
        setattr(cab, 'left_side_seam_height' if side == 'LEFT'
                else 'right_side_seam_height', 0.0)
        # Clearing a seam puts the end back to being measured -- the
        # No Seam exemption is a separate answer, given deliberately.
        setattr(cab, 'left_side_no_seam' if side == 'LEFT'
                else 'right_side_no_seam', False)
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
        # On an applied panel the flag lands on the panel's own props,
        # but the geometry it drives (the panel's kick notch) is built
        # by the HOST cabinet's recalc - the panel's own recalc, which
        # the property update just ran, can't reach it.
        if root.get(types_face_frame.TAG_APPLIED_PANEL_SIDE):
            host = types_face_frame.find_cabinet_root(root.parent)
            if host is not None:
                types_face_frame.recalculate_face_frame_cabinet(host)
        return {'FINISHED'}


class hb_face_frame_OT_set_cabinet_column(bpy.types.Operator):
    """Apply, edit, or remove the cabinet column on the selected stile.

    A cabinet column is a split turning (end blocks, spools, styled
    shaft) applied over the frame face on a stile - flush with the
    cabinet end on an end stile, centered on a mid stile. The stile is
    opened up to Stile Width (4" by default) when the column is set,
    and put back when it is removed if it still holds that width. The
    assignment lives in the cabinet's cabinet_columns collection keyed
    by stile; this dialog is its only editor. Also reachable by
    right-clicking a built column component (the key rides on it).
    """
    bl_idname = "hb_face_frame.set_cabinet_column"
    bl_label = "Cabinet Column"
    bl_description = ("Apply or edit the split-turned cabinet column "
                      "on this stile")
    bl_options = {'UNDO'}

    style: EnumProperty(
        name="Style", items=cabinet_column.STYLE_ITEMS,
        default='SMOOTH')  # type: ignore
    size: EnumProperty(
        name="Size", items=cabinet_column.SIZE_ITEMS,
        default='LARGE')  # type: ignore
    stile_width: FloatProperty(
        name="Stile Width", default=cabinet_column.STILE_WIDTH,
        unit='LENGTH', precision=4, min=0.0,
        description="Width the stile under the column is opened up to "
                    "(0 = leave the stile as it is)",
    )  # type: ignore
    top_block: BoolProperty(
        name="Top End Block", default=True)  # type: ignore
    top_block_height: FloatProperty(
        name="Height", default=0.0, unit='LENGTH', precision=4, min=0.0,
        description="0 = default (1\" taller than the top rail)",
    )  # type: ignore
    bottom_block: BoolProperty(
        name="Bottom End Block", default=True)  # type: ignore
    bottom_block_height: FloatProperty(
        name="Height", default=0.0, unit='LENGTH', precision=4, min=0.0,
        description="0 = default (1\" taller than the top rail, like "
                    "the top block)",
    )  # type: ignore
    floor_block: BoolProperty(
        name="Bottom Block at Floor", default=False,
        description="Plain plinth block at the floor (for a flush kick "
                    "or a stile extended to the floor)")  # type: ignore
    floor_block_height: FloatProperty(
        name="Height", default=0.0, unit='LENGTH', precision=4, min=0.0,
        description="0 = default (fills the kick recess, or 4\" on a "
                    "flush kick)",
    )  # type: ignore
    remove: BoolProperty(
        name="Remove Column", default=False)  # type: ignore

    @staticmethod
    def _stile_key(obj):
        if obj is None:
            return None
        role = obj.get('hb_part_role')
        if role == types_face_frame.PART_ROLE_LEFT_STILE:
            return 'LEFT'
        if role == types_face_frame.PART_ROLE_RIGHT_STILE:
            return 'RIGHT'
        if role == types_face_frame.PART_ROLE_MID_STILE:
            return 'MID_%d' % obj.get('hb_mid_stile_index', 0)
        if role == cabinet_column.PART_ROLE:
            return obj.get('hb_column_key')
        return None

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if cls._stile_key(obj) is None:
            return False
        root = types_face_frame.find_cabinet_root(obj)
        return (root is not None
                and root.face_frame_cabinet.corner_type == 'NONE')

    def _existing(self, root, key):
        for i, entry in enumerate(root.face_frame_cabinet.cabinet_columns):
            if entry.stile_key == key:
                return i
        return -1

    @staticmethod
    def _stile_width_target(root, key):
        """(getter, setter, unlocker) for the width of the stile at
        key, or None when the key doesn't resolve to a stile."""
        cab = root.face_frame_cabinet
        if key == 'LEFT':
            return (lambda: cab.left_stile_width,
                    lambda v: setattr(cab, 'left_stile_width', v),
                    lambda f: setattr(cab, 'unlock_left_stile', f))
        if key == 'RIGHT':
            return (lambda: cab.right_stile_width,
                    lambda v: setattr(cab, 'right_stile_width', v),
                    lambda f: setattr(cab, 'unlock_right_stile', f))
        if key.startswith('MID_'):
            try:
                gap = int(key[4:])
            except ValueError:
                return None
            coll = cab.mid_stile_widths
            while len(coll) <= gap:
                coll.add()
            ms = coll[gap]
            return (lambda: ms.width,
                    lambda v: setattr(ms, 'width', v),
                    lambda f: setattr(ms, 'unlock', f))
        return None

    def _apply_stile_width(self, root, key, width):
        """Open the stile up to the column's stile width. Unlocked so
        a style re-apply leaves it alone (like Set Width does)."""
        if width <= 0.0:
            return
        target = self._stile_width_target(root, key)
        if target is None:
            return
        get, put, unlock = target
        unlock(True)
        if abs(get() - width) > 1e-7:
            put(width)

    def _restore_stile_width(self, root, key, applied):
        """Undo _apply_stile_width when the column is removed: only if
        the stile still holds the width the column set (a user edit
        since is theirs to keep). Re-locking snaps a styled cabinet's
        stile back to the style value; an unstyled one takes the
        cabinet default (mid) or type-driven width (ends)."""
        if applied <= 0.0:
            return
        target = self._stile_width_target(root, key)
        if target is None:
            return
        get, put, unlock = target
        if abs(get() - applied) > 1e-7:
            return
        unlock(False)
        cab = root.face_frame_cabinet
        if key in ('LEFT', 'RIGHT'):
            # Re-locking an end stile re-applied the style; only an
            # unstyled cabinet needs the type-driven width written.
            if not root.get('STYLE_NAME'):
                from .. import props_hb_face_frame
                props_hb_face_frame._recompute_blind_stile_width(cab, key)
        else:
            # Mid stile relock doesn't re-apply the style; the
            # cabinet default is what the style cascade writes.
            put(cab.bay_mid_stile_width)

    def invoke(self, context, event):
        obj = context.active_object
        self._key = self._stile_key(obj)
        self._root = types_face_frame.find_cabinet_root(obj)
        self.remove = False
        idx = self._existing(self._root, self._key)
        self._had_entry = idx >= 0
        if self._had_entry:
            entry = self._root.face_frame_cabinet.cabinet_columns[idx]
            self.style = entry.style
            self.size = entry.size
            self.stile_width = entry.stile_width
            self.top_block = entry.top_block
            self.top_block_height = entry.top_block_height
            self.bottom_block = entry.bottom_block
            self.bottom_block_height = entry.bottom_block_height
            self.floor_block = entry.floor_block
            self.floor_block_height = entry.floor_block_height
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(self, 'style')
        col.prop(self, 'size')
        col.prop(self, 'stile_width')
        row = col.row(align=True)
        row.prop(self, 'top_block')
        sub = row.row(align=True)
        sub.enabled = self.top_block
        sub.prop(self, 'top_block_height', text="")
        row = col.row(align=True)
        row.prop(self, 'bottom_block')
        sub = row.row(align=True)
        sub.enabled = self.bottom_block
        sub.prop(self, 'bottom_block_height', text="")
        row = col.row(align=True)
        row.prop(self, 'floor_block')
        sub = row.row(align=True)
        sub.enabled = self.floor_block
        sub.prop(self, 'floor_block_height', text="")
        if self._had_entry:
            col.separator()
            col.prop(self, 'remove', icon='X')

    def execute(self, context):
        root = getattr(self, '_root', None)
        key = getattr(self, '_key', None)
        if root is None or key is None:
            # Called without invoke (scripted EXEC_DEFAULT): resolve
            # from the active object directly.
            obj = context.active_object
            key = self._stile_key(obj)
            root = types_face_frame.find_cabinet_root(obj)
        if root is None or key is None:
            return {'CANCELLED'}
        cab = root.face_frame_cabinet
        idx = self._existing(root, key)
        if self.remove:
            if idx >= 0:
                applied = cab.cabinet_columns[idx].stile_width
                cab.cabinet_columns.remove(idx)
                self._restore_stile_width(root, key, applied)
        else:
            entry = (cab.cabinet_columns[idx] if idx >= 0
                     else cab.cabinet_columns.add())
            entry.stile_key = key
            entry.style = self.style
            entry.size = self.size
            entry.stile_width = self.stile_width
            self._apply_stile_width(root, key, self.stile_width)
            entry.top_block = self.top_block
            entry.top_block_height = self.top_block_height
            entry.bottom_block = self.bottom_block
            entry.bottom_block_height = self.bottom_block_height
            entry.floor_block = self.floor_block
            entry.floor_block_height = self.floor_block_height
        types_face_frame.recalculate_face_frame_cabinet(root)
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


# Stash for the toe kick type a flush toggle replaced, so toggling back
# restores what the cabinet had (NOTCH, FLOATING, ...) instead of
# assuming NOTCH.
_PRE_FLUSH_TOE_KICK_TYPE = 'HB_PRE_FLUSH_TOE_KICK_TYPE'


def _flush_rail_root(obj):
    """Cabinet root for the flush-rail toggle, or None when the clicked
    part doesn't qualify: bottom rails on plain BASE / TALL cabinets
    only (uppers have no kick; corners carry their own kick frame)."""
    if obj is None or obj.get('hb_part_role') \
            != types_face_frame.PART_ROLE_BOTTOM_RAIL:
        return None
    root = types_face_frame.find_cabinet_root(obj)
    if root is None:
        return None
    cab = root.face_frame_cabinet
    if cab.cabinet_type not in ('BASE', 'TALL'):
        return None
    if cab.corner_type != 'NONE':
        return None
    return root


class hb_face_frame_OT_toggle_flush_bottom_rail(bpy.types.Operator):
    """Toggle the cabinet between its recessed toe kick and the FLUSH
    (wide bottom rail) construction, from the clicked bottom rail. The
    prior toe kick type is stashed on the cabinet root so toggling back
    restores it exactly. Base / Tall cabinets only.
    """
    bl_idname = "hb_face_frame.toggle_flush_bottom_rail"
    bl_label = "Toggle Flush Bottom Rail"
    bl_description = ("Switch this cabinet between its toe kick and the "
                      "flush wide-bottom-rail construction")
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return _flush_rail_root(context.active_object) is not None

    def execute(self, context):
        root = _flush_rail_root(context.active_object)
        if root is None:
            return {'CANCELLED'}
        cab = root.face_frame_cabinet
        if cab.toe_kick_type == 'FLUSH':
            # The enum write recalcs via its update callback.
            cab.toe_kick_type = root.get(_PRE_FLUSH_TOE_KICK_TYPE, 'NOTCH')
            self.report({'INFO'}, "Flush bottom rail removed")
        else:
            root[_PRE_FLUSH_TOE_KICK_TYPE] = cab.toe_kick_type
            cab.toe_kick_type = 'FLUSH'
            self.report({'INFO'}, "Flush bottom rail set")
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


def _misc_part_recarve(obj):
    """Re-carve a textured (beadboard / shiplap) Misc Part after a GN
    input write -- the static mesh doesn't follow the inputs on its
    own. No-op for plain panels."""
    if not obj.get('HB_STATIC_TEXTURED'):
        return
    part = types_face_frame.MiscPart()
    part.obj = obj
    part.rebuild()


def _on_misc_width_update(self, context):
    """Live-apply Width -> the cutpart's 'Length' (X) input."""
    obj = _misc_part_for_dialog(self)
    if obj is not None:
        GeoNodeCutpart(obj).set_input('Length', self.part_width)
        _misc_part_recarve(obj)


def _on_misc_depth_update(self, context):
    """Live-apply Depth -> the cutpart's 'Width' (Y) input."""
    obj = _misc_part_for_dialog(self)
    if obj is not None:
        GeoNodeCutpart(obj).set_input('Width', self.part_depth)
        _misc_part_recarve(obj)


def _on_misc_thickness_update(self, context):
    """Live-apply Thickness -> the cutpart's 'Thickness' (Z) input."""
    obj = _misc_part_for_dialog(self)
    if obj is not None:
        GeoNodeCutpart(obj).set_input('Thickness', self.part_thickness)
        _misc_part_recarve(obj)


def _on_misc_panel_type_update(self, context):
    """Live-apply the panel type: stamp it on the part and rebuild --
    PANEL restores the live GN cutpart, BEADBOARD / SHIPLAP carve the
    static textured mesh."""
    obj = _misc_part_for_dialog(self)
    if obj is None:
        return
    obj['HB_MISC_PANEL_TYPE'] = self.panel_type
    part = types_face_frame.MiscPart()
    part.obj = obj
    part.rebuild()


class hb_face_frame_OT_set_misc_part_dimensions(bpy.types.Operator):
    """Misc Part properties: size + panel type (plain / beadboard / shiplap).

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
    # bl_idname kept for compatibility; the dialog outgrew its name and
    # presents as Part Properties (size + panel type).
    bl_idname = "hb_face_frame.set_misc_part_dimensions"
    bl_label = "Part Properties"
    bl_description = ("Edit this part's size and panel type "
                      "(plain / beadboard / shiplap)")
    bl_options = {'UNDO'}

    # Resolved each tick by the update callbacks (see _misc_part_for_dialog).
    source_obj_name: StringProperty(default='', options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore

    part_width: FloatProperty(name="Width", unit='LENGTH', precision=4, min=0.0,
                              update=_on_misc_width_update)  # type: ignore
    part_depth: FloatProperty(name="Depth", unit='LENGTH', precision=4, min=0.0,
                              update=_on_misc_depth_update)  # type: ignore
    part_thickness: FloatProperty(name="Thickness", unit='LENGTH', precision=4, min=0.0,
                                  update=_on_misc_thickness_update)  # type: ignore
    panel_type: EnumProperty(
        name="Type",
        items=[
            ('PANEL', "Panel", "Plain flat panel"),
            ('BEADBOARD', "Beadboard",
             "Vertical quirk-bead grooves carved across the face"),
            ('SHIPLAP', "Shiplap",
             "Nickel-gap plank reveals carved across the face"),
            ('V_GROOVE', "V-Groove",
             "Vertical v-groove cuts carved across the face"),
            ('SLOTTED_SHELF', "Slotted Shelf",
             "Equally spaced slats set flush in a solid perimeter frame"),
        ],
        default='PANEL',
        update=_on_misc_panel_type_update)  # type: ignore

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
        self.panel_type = obj.get('HB_MISC_PANEL_TYPE', 'PANEL')
        self.source_obj_name = obj.name
        return context.window_manager.invoke_props_dialog(self, width=260)

    def draw(self, context):
        col = self.layout.column(align=True)
        col.prop(self, 'part_width')
        col.prop(self, 'part_depth')
        col.prop(self, 'part_thickness')
        col.separator()
        col.prop(self, 'panel_type')

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


def _rebuild_door_part(obj):
    """Rebuild a Python-built Door Part after its cutpart inputs changed.

    A GN front resizes live off the modifier inputs, but a door_builder
    front is a static mesh (HB_DOOR_FRAME 5-piece or HB_STATIC_SLAB) with
    the cutpart modifier kept only as the Length/Width/Thickness store --
    writing the inputs alone leaves the visible mesh at the old size.
    Re-run the part's assigned style (DOOR_STYLE_NAME in the role's pool,
    falling back to the active style), which re-reads the inputs and
    rebuilds the mesh. No-op for live GN fronts."""
    if not (obj.get('HB_DOOR_FRAME') or obj.get('HB_STATIC_SLAB')):
        return
    from .. import props_hb_face_frame as props
    ds = None
    ff = props.get_style_props()
    if ff is not None:
        name = obj.get('DOOR_STYLE_NAME')
        role = obj.get('hb_part_role')
        pool = (ff.drawer_front_styles
                if role in ('DRAWER_FRONT', 'FALSE_FRONT', 'TILT_OUT')
                else ff.door_styles)
        ds = next((d for d in pool if d.name == name), None)
    if ds is None:
        ds = types_face_frame._active_door_style()
    if ds is not None:
        ds.assign_style_to_front(obj)


def _on_door_width_update(self, context):
    """Live-apply Width -> the door's 'Width' input, then re-track the pull."""
    obj = _door_part_for_dialog(self)
    if obj is not None:
        GeoNodeCutpart(obj).set_input('Width', self.part_width)
        _rebuild_door_part(obj)
        types_face_frame.position_door_part_pull(obj)


def _on_door_height_update(self, context):
    """Live-apply Height -> the door's 'Length' input, then re-track the pull."""
    obj = _door_part_for_dialog(self)
    if obj is not None:
        GeoNodeCutpart(obj).set_input('Length', self.part_height)
        _rebuild_door_part(obj)
        types_face_frame.position_door_part_pull(obj)


def _on_door_thickness_update(self, context):
    """Live-apply Thickness -> the door's 'Thickness' input, then re-track
    the pull (it mounts on the front face = thickness)."""
    obj = _door_part_for_dialog(self)
    if obj is not None:
        GeoNodeCutpart(obj).set_input('Thickness', self.part_thickness)
        _rebuild_door_part(obj)
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
    """True for a 5-piece styled front: python-built (the HB_DOOR_FRAME
    stamp from assign_style_to_front) or the GN fallback's 'Door Style'
    modifier. Slab fronts have neither."""
    if obj is None:
        return False
    return 'HB_DOOR_FRAME' in obj or _door_style_mod(obj) is not None


def _front_frame_values(front):
    """The rendered frame values of a 5-piece front as a plain dict
    (left / right stile, top / bottom rail, add_mid, center_mid, mid_w,
    mid_loc), read off the HB_DOOR_FRAME stamp (python-built door) or
    the 'Door Style' modifier inputs (GN fallback). None for slabs."""
    if front is None:
        return None
    stamp = front.get('HB_DOOR_FRAME')
    if stamp is not None:
        return {
            'left': stamp.get('left_stile', 0.0),
            'right': stamp.get('right_stile', 0.0),
            'top': stamp.get('top_rail', 0.0),
            'bottom': stamp.get('bottom_rail', 0.0),
            'add_mid': bool(stamp.get('add_mid_rail', False)),
            'center_mid': bool(stamp.get('mid_center', True)),
            'mid_w': stamp.get('mid_rail_width', 0.0),
            'mid_stile_w': stamp.get('mid_stile_width', 0.0),
            'mid_loc': stamp.get('mid_loc', 0.0),
        }
    mod = _door_style_mod(front)
    if mod is None:
        return None
    # The CPM_5PIECEDOOR node renders its Left / Right stile inputs on
    # the OPPOSITE visual sides from their names, so reads swap the
    # same way assign_style_to_front's writes do: the node's 'Left
    # Stile Width' input carries the viewer's RIGHT stile.
    return {
        'left': _mod_input_get(mod, "Right Stile Width", 0.0),
        'right': _mod_input_get(mod, "Left Stile Width", 0.0),
        'top': _mod_input_get(mod, "Top Rail Width", 0.0),
        'bottom': _mod_input_get(mod, "Bottom Rail Width", 0.0),
        'add_mid': bool(_mod_input_get(mod, "Add Mid Rail", False)),
        'center_mid': bool(_mod_input_get(mod, "Center Mid Rail", True)),
        'mid_w': _mod_input_get(mod, "Mid Rail Width", 0.0),
        # The GN door has no mid stile member -- 0 seeds from the stile.
        'mid_stile_w': 0.0,
        'mid_loc': _mod_input_get(mod, "Mid Rail Location", 0.0),
    }


def _mod_input_get(mod, name, default=None):
    """Read a NODES modifier input by socket name (identifiers are stable,
    indices are not - look the name up in the interface tree)."""
    try:
        for item in mod.node_group.interface.items_tree:
            if getattr(item, 'item_type', '') == 'SOCKET' and item.name == name:
                return hb_utils.get_gn_input(mod, item.identifier)
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
    read-only readout. Reads the rendered frame values + the cutpart Length,
    so it reflects the rendered geometry regardless of the mid-rail mode (the
    Set Door Frame dialog is live-bound, so the front already carries any
    pending edit). The rail spans [loc - Rm/2, loc + Rm/2] about its centerline
    loc within the [0, L] door.

    Returns (bottom_opening, top_opening) in metres when a mid rail is present,
    (full_opening, None) when it isn't, or None if the front can't be read.
    """
    vals = _front_frame_values(front)
    if vals is None:
        return None
    try:
        length = GeoNodeCutpart(front).get_input("Length")
    except Exception:
        return None
    if not vals['add_mid']:
        return (length - vals['top'] - vals['bottom'], None)
    half = vals['mid_w'] / 2.0
    loc = length / 2.0 if vals['center_mid'] else vals['mid_loc']
    bottom_opening = (loc - half) - vals['bottom']
    top_opening = (length - vals['top']) - (loc + half)
    return (bottom_opening, top_opening)


def _front_overall_size(front):
    """Overall (width, height) of a front for a read-only readout, read
    off its cutpart (a front's Length runs vertically). The frame fields
    above are per-member; this is the door itself, which is what gets
    ordered. None when the part can't be read."""
    if front is None:
        return None
    try:
        part = GeoNodeCutpart(front)
        return (part.get_input('Width'), part.get_input('Length'))
    except Exception:
        return None


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


def _on_df_mid_widths(self, context):
    """Shared update for the mid rail / mid stile member widths. Both
    size members the door style has no field for (it carries a single
    mid rail width, and a mid stile has always followed the outer
    stile), so they only exist as per-front overrides."""
    front = _door_frame_for_dialog(self)
    if front is not None:
        store = _frame_store(front)
        store['HB_FRAME_OVR_MID_RAIL_WIDTH'] = self.mid_rail_width
        store['HB_FRAME_OVR_MID_STILE_WIDTH'] = self.mid_stile_width
        _reapply_frame_store(store, front)


def _on_df_grid(self, context):
    """Shared update for the mid-member grid fields (rail / stile counts
    and their row / column weight strings)."""
    front = _door_frame_for_dialog(self)
    if front is not None:
        store = _frame_store(front)
        store['HB_FRAME_OVR_MID_RAIL_COUNT'] = self.mid_rails
        store['HB_FRAME_OVR_MID_STILE_COUNT'] = self.mid_stiles
        store['HB_FRAME_OVR_ROW_RATIOS'] = self.row_ratios
        store['HB_FRAME_OVR_COL_RATIOS'] = self.col_ratios
        _reapply_frame_store(store, front)


def _front_has_grid_mullion(front_obj):
    """True when the front's door style renders a Wood Mullion (GRID)
    panel -- the only panel kind whose lite counts are overridable.
    Resolves the style the same way _reapply_front_style does."""
    if front_obj is None:
        return False
    name = front_obj.get('DOOR_STYLE_NAME')
    if not name:
        return False
    from .. import props_hb_face_frame as _props
    from .. import style_options
    ff = _props.get_style_props()
    if ff is None:
        return False
    role = front_obj.get('hb_part_role')
    pool = (ff.drawer_front_styles if role in _DRAWER_FRONT_ROLES
            else ff.door_styles)
    for ds in pool:
        if ds.name == name:
            pkind = style_options.panel_kind(getattr(ds, 'front_panel', ''))
            return (pkind.get('kind') == 'GLASS'
                    and pkind.get('mullion') == 'GRID')
    return False


def _on_df_mullion(self, context):
    """Shared update for the Wood Mullion lite-count overrides."""
    front = _door_frame_for_dialog(self)
    if front is not None:
        store = _frame_store(front)
        store['HB_FRAME_OVR_MULLION_COLS'] = self.mullion_lites_wide
        store['HB_FRAME_OVR_MULLION_ROWS'] = self.mullion_lites_high
        _reapply_frame_store(store, front)


def _on_df_glass(self, context):
    """Glass Panels: which panel rows of this front are glass lites.
    Independent of the frame lock (a panel choice, not frame geometry);
    written straight to the durable store and re-applied."""
    front = _door_frame_for_dialog(self)
    if front is not None:
        store = _frame_store(front)
        store['HB_FRAME_OVR_GLASS_TOP'] = self.glass_top
        store['HB_FRAME_OVR_GLASS_BOTTOM'] = self.glass_bottom
        store['HB_FRAME_OVR_GLASS_ROWS'] = self.glass_rows
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
        store['HB_FRAME_OVR_MID_RAIL_WIDTH'] = self.mid_rail_width
        store['HB_FRAME_OVR_MID_STILE_WIDTH'] = self.mid_stile_width
        store['HB_FRAME_OVR_MID_RAIL_COUNT'] = self.mid_rails
        store['HB_FRAME_OVR_MID_STILE_COUNT'] = self.mid_stiles
        store['HB_FRAME_OVR_ROW_RATIOS'] = self.row_ratios
        store['HB_FRAME_OVR_COL_RATIOS'] = self.col_ratios
        store['HB_FRAME_OVR_MULLION_COLS'] = self.mullion_lites_wide
        store['HB_FRAME_OVR_MULLION_ROWS'] = self.mullion_lites_high
        store['HB_FRAME_FRAME_LOCKED'] = True
    else:
        store['HB_FRAME_FRAME_LOCKED'] = False
    _reapply_frame_store(store, front)


class hb_face_frame_OT_set_door_frame(bpy.types.Operator):
    """Set a 5-piece front's stile / rail widths (per side) and mid rail.

    The Modify Door checkbox (prop name lock_frame, kept for saved-file
    compatibility) pins the WHOLE interface: the values are stored as
    durable HB_FRAME_OVR_* props and the front is flagged
    HB_FRAME_FRAME_LOCKED, so the solver honors them on every recalc (a
    cabinet edit can't overwrite them). Unchecked, the fields are greyed
    and the front follows its door style (recomputed on any cabinet
    change). Live-bound like the other Set-* dialogs. Mid Rail mode:
    CENTERED, THIRD (1/3 - 2/3 -> rail near the top), or CUSTOM (uses
    Location); the Grid row supersedes those when its rail count > 0.
    """
    bl_idname = "hb_face_frame.set_door_frame"
    bl_label = "Set Door Frame"
    bl_description = "Override this front's stile, rail, and mid rail"
    bl_options = {'UNDO'}

    source_obj_name: StringProperty(default='', options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore

    lock_frame: bpy.props.BoolProperty(
        name="Modify Door",
        description="Take manual control of this door's frame: the stile / "
                    "rail / grid values below are pinned so cabinet edits "
                    "and style changes don't overwrite them. Uncheck to "
                    "follow the door style again",
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
    mid_rail_width: FloatProperty(name="Mid Rail Width", unit='LENGTH', precision=4, min=0.0,
                                  description="Width of the mid rail(s) on this front",
                                  update=_on_df_mid_widths)  # type: ignore
    mid_stile_width: FloatProperty(name="Mid Stile Width", unit='LENGTH', precision=4, min=0.0,
                                   description="Width of the mid stile(s) on this front",
                                   update=_on_df_mid_widths)  # type: ignore

    # Mid-member GRID: N mid rails x N mid stiles dividing the field
    # into panel cells (six-panel-door construction: rails run full
    # width, stiles run between the rails). A rail count > 0 supersedes
    # the single Mid Rail mode above; the weight strings size the rows /
    # columns (blank = equal).
    mid_rails: bpy.props.IntProperty(
        name="Mid Rails", min=0, max=10, default=0,
        description="Number of mid rails splitting the door into panel "
                    "rows (0 = use the Mid Rail mode above)",
        update=_on_df_grid)  # type: ignore
    mid_stiles: bpy.props.IntProperty(
        name="Mid Stiles", min=0, max=10, default=0,
        description="Number of mid stiles splitting each panel row into "
                    "columns",
        update=_on_df_grid)  # type: ignore
    row_ratios: StringProperty(
        name="Row Heights",
        description="Relative panel-row heights bottom-up, e.g. \"1 2 1\" "
                    "or \"1/4 1/2 1/4\" (blank = equal rows)",
        default='', update=_on_df_grid)  # type: ignore
    col_ratios: StringProperty(
        name="Column Widths",
        description="Relative panel-column widths left to right "
                    "(blank = equal columns)",
        default='', update=_on_df_grid)  # type: ignore

    # Wood Mullion lite-count overrides (GRID pattern only). 0 = the
    # pattern's standard counts (2 across, rows from the height chart).
    mullion_lites_wide: bpy.props.IntProperty(
        name="Lites Wide", min=0, max=12, default=0,
        description="Wood Mullion lites across (0 = standard 2)",
        update=_on_df_mullion)  # type: ignore
    mullion_lites_high: bpy.props.IntProperty(
        name="Lites High", min=0, max=12, default=0,
        description="Wood Mullion lites high (0 = automatic from the "
                    "opening-height chart)",
        update=_on_df_mullion)  # type: ignore

    # Glass Panels: per-row glass lites in an otherwise wood-panelled
    # door (glass top over a wood bottom). Top / Bottom cover the split
    # door; the rows string ("1 3", counted from the top) covers grids.
    glass_top: bpy.props.BoolProperty(
        name="Top Panel Glass", default=False,
        description="Build the top panel row as a glass lite",
        update=_on_df_glass)  # type: ignore
    glass_bottom: bpy.props.BoolProperty(
        name="Bottom Panel Glass", default=False,
        description="Build the bottom panel row as a glass lite",
        update=_on_df_glass)  # type: ignore
    glass_rows: StringProperty(
        name="Glass Rows", default='',
        description="Panel rows to build as glass, counted from the "
                    "top, e.g. \"1 3\" (for grids; blank = just the "
                    "Top / Bottom toggles)",
        update=_on_df_glass)  # type: ignore

    @classmethod
    def poll(cls, context):
        return has_door_style_modifier(context.active_object)

    def invoke(self, context, event):
        obj = context.active_object
        vals = _front_frame_values(obj) or {}
        store = _frame_store(obj)
        locked = bool(store.get('HB_FRAME_FRAME_LOCKED', False))
        # Seed BEFORE source_obj_name is set so the callbacks bail and the
        # seed writes don't fan back. Locked -> show the pinned store values;
        # unlocked -> show the front's live (style-driven) rendered values.
        def seed(ovr_key, field):
            if locked and ovr_key in store.keys():
                return store[ovr_key]
            return vals.get(field, 0.0)
        self.left_stile = seed('HB_FRAME_OVR_LEFT_STILE', 'left')
        self.right_stile = seed('HB_FRAME_OVR_RIGHT_STILE', 'right')
        self.top_rail = seed('HB_FRAME_OVR_TOP_RAIL', 'top')
        self.bottom_rail = seed('HB_FRAME_OVR_BOTTOM_RAIL', 'bottom')
        mode = store.get('HB_FRAME_OVR_MID_RAIL_MODE') if locked else None
        if not mode:
            if not vals.get('add_mid', False):
                mode = 'NONE'
            else:
                mode = 'CENTERED' if vals.get('center_mid', True) else 'CUSTOM'
        self.mid_rail_mode = mode
        if locked and 'HB_FRAME_OVR_MID_RAIL_LOCATION' in store.keys():
            self.mid_rail_location = store['HB_FRAME_OVR_MID_RAIL_LOCATION']
        else:
            self.mid_rail_location = vals.get('mid_loc', 0.0)
        # Mid-member widths. Seed at what the front renders today so an
        # untouched door keeps its look: the stamped widths, then the
        # matching outer member for a front stamped before these existed.
        self.mid_rail_width = (seed('HB_FRAME_OVR_MID_RAIL_WIDTH', 'mid_w')
                               or vals.get('mid_w', 0.0) or self.top_rail)
        self.mid_stile_width = (seed('HB_FRAME_OVR_MID_STILE_WIDTH', 'mid_stile_w')
                                or vals.get('mid_stile_w', 0.0) or self.left_stile)
        # Grid overrides live only on the store (no style-driven grid).
        if locked:
            self.mid_rails = int(store.get('HB_FRAME_OVR_MID_RAIL_COUNT', 0) or 0)
            self.mid_stiles = int(store.get('HB_FRAME_OVR_MID_STILE_COUNT', 0) or 0)
            self.row_ratios = str(store.get('HB_FRAME_OVR_ROW_RATIOS', '') or '')
            self.col_ratios = str(store.get('HB_FRAME_OVR_COL_RATIOS', '') or '')
            self.mullion_lites_wide = int(store.get('HB_FRAME_OVR_MULLION_COLS', 0) or 0)
            self.mullion_lites_high = int(store.get('HB_FRAME_OVR_MULLION_ROWS', 0) or 0)
        else:
            self.mid_rails = 0
            self.mid_stiles = 0
            self.row_ratios = ''
            self.col_ratios = ''
            self.mullion_lites_wide = 0
            self.mullion_lites_high = 0
        # Glass rows are not lock-gated: seed from the store either way.
        self.glass_top = bool(store.get('HB_FRAME_OVR_GLASS_TOP', False))
        self.glass_bottom = bool(store.get('HB_FRAME_OVR_GLASS_BOTTOM', False))
        self.glass_rows = str(store.get('HB_FRAME_OVR_GLASS_ROWS', '') or '')
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
        # Single-rail mode rows grey out while a rail-count grid is
        # active -- the grid supersedes them.
        mode_col = body.column(align=True)
        mode_col.enabled = self.mid_rails == 0
        mode_col.prop(self, 'mid_rail_mode')
        row = mode_col.row()
        row.enabled = self.mid_rail_mode in _MID_RAIL_VALUE_MODES
        # The same field carries a from-bottom location (CUSTOM) or an interior
        # panel height (TOP_PANEL / BOTTOM_PANEL); relabel to match the mode.
        loc_label = {'TOP_PANEL': "Top Panel Height",
                     'BOTTOM_PANEL': "Bottom Panel Height"}.get(self.mid_rail_mode, "Location")
        row.prop(self, 'mid_rail_location', text=loc_label)
        # Mid rail width applies to the single rail and to grid rails, so
        # it sits outside the mode column (which greys out under a grid).
        body.prop(self, 'mid_rail_width')

        body.separator()
        grid = body.column(align=True)
        row = grid.row(align=True)
        row.label(text="Grid:")
        row.prop(self, 'mid_rails', text="Rails")
        row.prop(self, 'mid_stiles', text="Stiles")
        row = grid.row()
        row.enabled = self.mid_rails > 0
        row.prop(self, 'row_ratios', text="Row Heights")
        row = grid.row()
        row.enabled = self.mid_stiles > 0
        row.prop(self, 'col_ratios', text="Col Widths")
        row = grid.row()
        row.enabled = self.mid_stiles > 0
        row.prop(self, 'mid_stile_width', text="Stile Width")

        # Wood Mullion lite counts -- only shown when the front's style
        # actually renders a GRID mullion panel.
        if _front_has_grid_mullion(_door_frame_for_dialog(self)):
            body.separator()
            mrow = body.row(align=True)
            mrow.label(text="Mullion:")
            mrow.prop(self, 'mullion_lites_wide', text="Wide")
            mrow.prop(self, 'mullion_lites_high', text="High")

        # Glass Panels -- always enabled (not frame geometry, so not behind
        # the Modify Door lock). The rows string only matters for grids.
        gbox = col.box()
        gbox.label(text="Glass Panels")
        grow = gbox.row(align=True)
        grow.prop(self, 'glass_top', text="Top")
        grow.prop(self, 'glass_bottom', text="Bottom")
        if self.mid_rails > 1:
            gbox.prop(self, 'glass_rows', text="Rows")

        us = context.scene.unit_settings
        front = _door_frame_for_dialog(self)

        # Read-only readout of the finished front's overall size, in the
        # always-enabled column so it shows whether or not the frame is
        # locked. Live like the rest of the dialog: an edit above resizes
        # nothing here (the front keeps its hole), but a front whose size
        # changed elsewhere reads correctly on the next open.
        size = _front_overall_size(front)
        if size is not None:
            sbox = col.box()
            sbox.label(text="Door Size")
            sbox.label(text="Width:  " + units.unit_to_string(us, size[0]))
            sbox.label(text="Height:  " + units.unit_to_string(us, size[1]))

        # Read-only readout of the resulting interior-panel heights. Lives in
        # the always-enabled column (not the lock-greyed body) so it's visible
        # whether the frame is locked or following its style. Grid fronts
        # skip it -- the two-opening readout doesn't describe N rows.
        openings = (None if self.mid_rails > 0 else
                    _front_panel_openings(front))
        if openings is not None:
            bottom_opening, top_opening = openings
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
# Set Door Hardware (per-door hardware callouts)
# ---------------------------------------------------------------------------
# Hardware callouts (restrictor clips / touch latches / finger rout)
# live on specific doors, not every door of a style: the door style's
# checkboxes only declare the option for the job, and each door that
# carries the letter mark is stamped individually -- painted with the
# style editor's brush buttons (ops_styles.paint_door_hardware) or
# edited here per door. Stamps live on the front's opening-cage store
# (fronts are rebuilt every recalc); downstream 2D consumers read them
# for the letter marks.

def _on_hw_field(self, context):
    front = _door_frame_for_dialog(self)
    if front is None:
        return
    store = _frame_store(front)
    store['HB_DOOR_HW_SET'] = True
    store['HB_DOOR_HW_RC'] = self.restrictor_clips
    store['HB_DOOR_HW_TL'] = self.touch_latches
    store['HB_DOOR_HW_FR'] = self.finger_rout


class hb_face_frame_OT_set_door_hardware(bpy.types.Operator):
    """Hardware callouts for THIS door: exactly the checked boxes mark
    the door on drawings (all-off = no callouts). Live-bound like the
    other Set-* dialogs; the style editor's brush buttons paint the
    same stamps across many doors."""
    bl_idname = "hb_face_frame.set_door_hardware"
    bl_label = "Set Door Hardware"
    bl_description = ("Set this door's hardware callouts (restrictor "
                      "clips / touch latches / finger rout)")
    bl_options = {'UNDO'}

    source_obj_name: StringProperty(default='', options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore

    restrictor_clips: bpy.props.BoolProperty(
        name="Restrictor Clips (RC)", default=False, update=_on_hw_field)  # type: ignore
    touch_latches: bpy.props.BoolProperty(
        name="Touch Latches (TL)", default=False, update=_on_hw_field)  # type: ignore
    finger_rout: bpy.props.BoolProperty(
        name="Finger Route (FR)", default=False, update=_on_hw_field)  # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.get('hb_part_role') == 'DOOR'

    def invoke(self, context, event):
        obj = context.active_object
        store = _frame_store(obj)
        # Seed BEFORE source_obj_name is set so the callbacks bail and
        # the seed writes don't fan back (same as Set Door Frame).
        self.restrictor_clips = bool(store.get('HB_DOOR_HW_RC', False))
        self.touch_latches = bool(store.get('HB_DOOR_HW_TL', False))
        self.finger_rout = bool(store.get('HB_DOOR_HW_FR', False))
        self.source_obj_name = obj.name
        return context.window_manager.invoke_props_dialog(self, width=240)

    def draw(self, context):
        col = self.layout.column(align=True)
        col.prop(self, 'restrictor_clips')
        col.prop(self, 'touch_latches')
        col.prop(self, 'finger_rout')

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


# ---------------------------------------------------------------------------
# Change Door Shape (quarter / half circle tops)
# ---------------------------------------------------------------------------
# Catalog quarter and half circle doors curve the door's whole top, not
# just the panel opening, and they land on ONE door at a time - a pair
# routinely has a round leaf and a square one. So the choice is stamped
# per leaf on the front's opening store (fronts are rebuilt every
# recalc) and read back by assign_style_to_front.

_DOOR_SHAPE_ITEMS = [
    ('SQUARE', "Square", "Standard square-top door"),
    ('QUARTER', "Quarter Round",
     "Quarter circle top, rising to one stile"),
    ('HALF', "Half Round", "Half circle top, arching over both stiles"),
]

_DOOR_SHAPE_HAND_ITEMS = [
    ('AUTO', "By Swing",
     "Each door's own pull side runs full height - the stile opposite "
     "its hinges. On a pair that puts the two arcs at the meeting "
     "stiles, so a multi-door selection comes out handed correctly"),
    ('LEFT', "Left", "The left stile runs full height"),
    ('RIGHT', "Right", "The right stile runs full height"),
]

_DOOR_SHAPE_RADIUS_ITEMS = [
    ('OUTSIDE', "Outside",
     "Radius measured from the outside edge of the tall stile "
     "(the arc runs out to the far corner)"),
    ('INSIDE', "Inside",
     "Radius measured from the inside edge of the tall stile "
     "(that stile keeps a square top)"),
]


def _front_door_style(front_obj):
    """The front's own door / drawer style, by DOOR_STYLE_NAME."""
    name = front_obj.get('DOOR_STYLE_NAME') if front_obj else None
    if not name:
        return None
    from .. import props_hb_face_frame as _props
    ff = _props.get_style_props()
    if ff is None:
        return None
    role = front_obj.get('hb_part_role')
    pool = (ff.drawer_front_styles if role in _DRAWER_FRONT_ROLES
            else ff.door_styles)
    for ds in pool:
        if ds.name == name:
            return ds
    return None


def door_shape_available(obj):
    """True when a round top can be cut into this door: a 5-piece door
    (not a slab), on a series whose frame the curve can follow - not a
    mitered one, where the member profile IS the frame, and not one
    carrying applied moulding - under a face frame that can be curved
    at all, and hung in an opening that can remember the choice."""
    if obj is None or obj.get('hb_part_role') != types_face_frame.PART_ROLE_DOOR:
        return False
    if not has_door_style_modifier(obj):
        return False
    if _frame_store(obj) is obj:
        return False
    from .. import props_hb_face_frame as _props
    if _props.round_top_frame_block(obj):
        return False
    ds = _front_door_style(obj)
    if ds is None or getattr(ds, 'door_type', '5_PIECE') == 'SLAB':
        return False
    if not getattr(ds, 'unlock_profiles', False):
        from .. import style_options
        prof = style_options.profiles_for_series(ds.front_series)
        if prof.get('member') or prof.get('applied'):
            return False
    return True


def _door_shape_fit_error(front_obj):
    """Why this door can't take its current round-top setting, or None.
    Runs the geometry the door itself was built to, so the dialog warns
    with the builder's own answer."""
    from .. import props_hb_face_frame as _props
    if front_obj is None:
        return None
    return _props.front_round_top_geometry(front_obj)[1]


def _door_shape_targets(context):
    """Every selected door that can take a shape (the active one
    first), de-duplicated."""
    objs = []
    active = context.active_object
    if door_shape_available(active):
        objs.append(active)
    for obj in context.selected_objects:
        if obj not in objs and door_shape_available(obj):
            objs.append(obj)
    return objs


def _apply_door_shape(op, context):
    """Write the dialog's choice onto every target door, rebuild it, and
    re-cut the frame members above the doors that changed - restyling a
    front is not a cabinet recalc, so the frame would otherwise keep its
    square opening until the next unrelated edit."""
    from .. import props_hb_face_frame as _props
    roots = []
    for front in _door_shape_targets(context):
        store = _frame_store(front)
        k_shape, k_hand, k_radius = _props.front_round_top_keys(front, store)
        if op.shape == 'SQUARE':
            for key in (k_shape, k_hand, k_radius):
                if key in store:
                    del store[key]
        else:
            store[k_shape] = op.shape
            # AUTO stores no hand: front_round_top then resolves each
            # door's tall side from its own swing, so one dialog over a
            # pair (or a whole run) hands every door individually.
            if op.hand == 'AUTO':
                if k_hand in store:
                    del store[k_hand]
            else:
                store[k_hand] = op.hand
            store[k_radius] = op.radius_mode
        _reapply_front_style(front)
        root = types_face_frame.find_cabinet_root(front)
        if root is not None and root not in roots:
            roots.append(root)
    for root in roots:
        types_face_frame.refresh_round_top_frames(root)


def _on_door_shape_field(self, context):
    _apply_door_shape(self, context)


class hb_face_frame_OT_set_door_shape(bpy.types.Operator):
    """Curve the top of the selected doors. Quarter Round rises to one
    stile, Half Round arches over both; the door's width sets the
    radius, the way the catalog cuts them. Applies to every selected
    door, so one leaf of a pair can be round and the other square."""
    bl_idname = "hb_face_frame.set_door_shape"
    bl_label = "Change Door Shape"
    bl_description = "Change the shape of the selected doors' tops"
    bl_options = {'UNDO'}

    shape: EnumProperty(
        name="Shape", items=_DOOR_SHAPE_ITEMS,
        update=_on_door_shape_field)  # type: ignore
    hand: EnumProperty(
        name="Tall Side", items=_DOOR_SHAPE_HAND_ITEMS,
        update=_on_door_shape_field)  # type: ignore
    radius_mode: EnumProperty(
        name="Radius", items=_DOOR_SHAPE_RADIUS_ITEMS,
        update=_on_door_shape_field)  # type: ignore

    source_obj_name: StringProperty(name="Source Object")  # type: ignore

    @classmethod
    def poll(cls, context):
        return door_shape_available(context.active_object)

    def invoke(self, context, event):
        from .. import props_hb_face_frame as _props
        front = context.active_object
        self.source_obj_name = front.name
        store = _frame_store(front)
        k_shape, k_hand, k_radius = _props.front_round_top_keys(front, store)
        self.shape = store.get(k_shape) or 'SQUARE'
        self.hand = store.get(k_hand) or 'AUTO'
        self.radius_mode = store.get(k_radius) or 'OUTSIDE'
        return context.window_manager.invoke_props_dialog(self, width=320)

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.prop(self, "shape", text="Shape")
        if self.shape == 'QUARTER':
            col.separator()
            col.prop(self, "hand", text="Tall Side", expand=True)
            col.separator()
            col.prop(self, "radius_mode", text="Radius", expand=True)
        front = bpy.data.objects.get(self.source_obj_name)
        reason = _door_shape_fit_error(front) if front else None
        if reason:
            box = layout.box()
            box.alert = True
            box.label(text=reason, icon='ERROR')
            box.label(text="The door is building square.")
        n = len(_door_shape_targets(context))
        if n > 1:
            layout.label(text="Applies to %d doors" % n, icon='INFO')

    def execute(self, context):
        # Live-bound via the prop update callbacks; nothing to do on OK
        # beyond telling the user when the shape didn't take.
        front = bpy.data.objects.get(self.source_obj_name)
        reason = _door_shape_fit_error(front) if front else None
        if reason:
            self.report({'WARNING'}, reason)
        return {'FINISHED'}


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
    if bool(mn) and mn in obj.modifiers:
        return True
    # Static wood-hood parts (angled bodies, shiplap wrap, sloped panels)
    # are plain meshes with no cutpart modifier: nothing to apply, but they
    # still take the manual flag so hood rebuilds leave them alone.
    return bool(obj.get('IS_WOOD_HOOD_PART')) and not any(
        m.type == 'NODES' for m in obj.modifiers)


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
        # Static wood-hood parts have no modifier -- already real mesh, they
        # just take the manual flag.
        if mn and mn in obj.modifiers:
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
        if 'HB_DOOR_FRAME' in obj:
            # Python-built door: the base mesh already IS the geometry and
            # the disabled cutpart modifier only carries inputs. Drop the
            # modifiers (applying the cutpart would overwrite the door with
            # its box) and the stamp, which marks a style-driven front.
            for mod in [m for m in obj.modifiers if m.type == 'NODES']:
                obj.modifiers.remove(mod)
            del obj['HB_DOOR_FRAME']
        else:
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


_BACKING_HOST_ROLES = frozenset({
    types_face_frame.PART_ROLE_BAY_MID_RAIL,
    types_face_frame.PART_ROLE_BAY_MID_STILE,
    types_face_frame.PART_ROLE_BAY_SHELF,
    types_face_frame.PART_ROLE_BAY_DIVISION,
})


def backing_removed(part_obj):
    """True when the splitter this part belongs to has its carcass
    backing dropped. Reads the same per-splitter entry the operator
    writes, so the menu label matches what is built."""
    split = _find_owning_split_node(part_obj)
    if split is None:
        return False
    idx = part_obj.get('hb_splitter_index', 0)
    coll = split.face_frame_split.splitter_widths
    return idx < len(coll) and bool(coll[idx].remove_backing)


class hb_face_frame_OT_toggle_splitter_backing(bpy.types.Operator):
    """Add or remove the carcass backing behind one splitter - the shelf
    behind a mid rail, the division behind a mid stile. Only that member's
    backing changes; the face frame member and the neighbouring splitters
    are untouched.

    Stored as remove_backing on the owning split node's per-splitter entry
    (keyed by hb_splitter_index) so it survives recalc, which is what lets
    a shelf come back after it has been dropped.
    """
    bl_idname = "hb_face_frame.toggle_splitter_backing"
    bl_label = "Toggle Backing Behind Splitter"
    bl_description = (
        "Add or remove the shelf behind this mid rail (the division behind "
        "a mid stile). The face frame member stays either way"
    )
    bl_options = {'UNDO'}

    remove: bpy.props.BoolProperty(
        name="Remove",
        description="Drop the backing when on, restore it when off",
        default=True,
    )  # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj is not None
                and obj.get('hb_part_role') in _BACKING_HOST_ROLES)

    def execute(self, context):
        obj = context.active_object
        split = _find_owning_split_node(obj)
        if split is None:
            self.report({'WARNING'}, "No split node found for this part")
            return {'CANCELLED'}
        sp = split.face_frame_split
        idx = obj.get('hb_splitter_index', 0)
        # Lazily grow the per-splitter collection to cover this index, then
        # set remove_backing (its update callback fires the cabinet recalc).
        coll = sp.splitter_widths
        while len(coll) <= idx:
            coll.add()
        # A split whose backing was never switched on has nothing to
        # restore, so putting one back has to flip the node flag too.
        # Every OTHER member is then pinned off first, or flipping the
        # node flag would grow shelves the user never asked for.
        if not self.remove and not sp.add_backing:
            n_children = len([c for c in split.children
                              if c.get(types_face_frame.TAG_OPENING_CAGE)
                              or c.get(types_face_frame.TAG_SPLIT_NODE)])
            while len(coll) < max(0, n_children - 1):
                coll.add()
            for i, entry in enumerate(coll):
                if i != idx:
                    entry.remove_backing = True
            sp.add_backing = True
        coll[idx].remove_backing = self.remove
        return {'FINISHED'}


_SIDE_PANEL_ROLES = frozenset({
    types_face_frame.PART_ROLE_LEFT_SIDE,
    types_face_frame.PART_ROLE_RIGHT_SIDE,
    # Corner cabs tag their exposed sides with corner-specific roles. The
    # operator edits cabinet-level finished-end props via find_cabinet_root,
    # so it works for corners once the side panel is reachable here.
    types_face_frame_corner.PART_ROLE_CORNER_LEFT_SIDE,
    types_face_frame_corner.PART_ROLE_CORNER_RIGHT_SIDE,
    # The carcass back and its finished replacement both resolve to the
    # BACK side of the dialog. Corner backs are excluded - their back
    # conditions are no-ops (against walls).
    types_face_frame.PART_ROLE_BACK,
    types_face_frame.PART_ROLE_FINISHED_BACK,
})

_BACK_PANEL_ROLES = frozenset({
    types_face_frame.PART_ROLE_BACK,
    types_face_frame.PART_ROLE_FINISHED_BACK,
})


class hb_face_frame_OT_set_finished_end_condition(bpy.types.Operator):
    """Set the finished-end condition for the clicked side or back panel.

    Launched from a left / right carcass side's (or the back's) right-click
    menu. Resolves the side from the clicked part's role and shows only that
    side's finished-end type enum (plus the flush-X amount when FLUSH_X is
    chosen; the back shows its Extend L / R pair instead). Editing the enum
    fires its existing update callback, which flips that side's finish-end
    auto flag off so exposure detection won't clobber the user's choice.
    """
    bl_idname = "hb_face_frame.set_finished_end_condition"
    bl_label = "Set Finished End Condition"
    bl_description = "Set the finished-end condition for this side"
    bl_options = {'UNDO'}

    side: bpy.props.EnumProperty(
        name="Side",
        items=[('LEFT', "Left", ""), ('RIGHT', "Right", ""),
               ('BACK', "Back", "")],
        default='LEFT',
    )  # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj is None:
            return False
        return obj.get('hb_part_role') in _SIDE_PANEL_ROLES

    def invoke(self, context, event):
        # The clicked panel is the active object; derive the side from
        # its role so the dialog edits the matching cabinet prop.
        obj = context.active_object
        role = obj.get('hb_part_role') if obj is not None else None
        if role in _BACK_PANEL_ROLES:
            self.side = 'BACK'
        elif role in (types_face_frame.PART_ROLE_RIGHT_SIDE,
                      types_face_frame_corner.PART_ROLE_CORNER_RIGHT_SIDE):
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
        if self.side == 'BACK':
            # Mirror the Finished Ends panel's back row: no flush-X
            # amount, no scribe, no return build - just the type plus
            # its two extends past the cabinet ends once finished.
            layout.prop(cab, 'back_finished_end_condition',
                        text="Back Finished End")
            if fin_type != 'UNFINISHED':
                row = layout.row(align=True)
                row.prop(cab, 'back_finished_extend_left', text="Extend L")
                row.prop(cab, 'back_finished_extend_right', text="Extend R")
            return
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
        if (fin_type in types_face_frame.RETURN_SIDE_CONDITIONS
                and getattr(cab, f'{key}_side_finished_extend_back') != 0.0
                and cab.back_finished_end_condition
                in types_face_frame.RETURN_BACK_CONDITIONS):
            layout.prop(cab, f'{key}_side_return_width',
                        text="Return Width")
            if getattr(cab, f'{key}_side_return_width') != 0.0:
                layout.prop(cab, f'{key}_side_return_panel_type',
                            text="Side Return")
                layout.prop(cab, f'{key}_side_return_stile_type',
                            text="Return Stile")
        # Symmetric finished ends are common (both ends of an island /
        # run get the same extend-back + return build), so offer a
        # one-click copy to the opposite side. Runs immediately; the
        # dialog stays open.
        other = 'RIGHT' if self.side == 'LEFT' else 'LEFT'
        layout.separator()
        props = layout.operator(
            'hb_face_frame.apply_finished_end_to_other_side',
            text=f"Apply to {other.title()} Side", icon='DUPLICATE')
        props.cabinet_name = root.name
        props.side = self.side

    def execute(self, context):
        return {'FINISHED'}


# Everything the Set Finished End Condition dialog can edit for a side,
# minus the side prefix. Copied verbatim by Apply to Other Side.
_FIN_END_SIDE_PROPS = (
    'finished_end_condition',
    'flush_x_amount',
    'side_finished_extend_back',
    'side_return_width',
    'side_return_panel_type',
    'side_return_stile_type',
)


class hb_face_frame_OT_apply_finished_end_to_other_side(bpy.types.Operator):
    """Copy one side's finished-end settings to the opposite side.

    Drawn as a button inside the Set Finished End Condition dialog.
    Copies every field that dialog can edit (see _FIN_END_SIDE_PROPS)
    from the clicked side to the other, so a symmetric extend-back /
    return-panel build only has to be entered once. Writing the enum
    fires its user-set callback, which flips the target side's
    finish-end auto flag off - the copy is pinned exactly like a manual
    edit would be.
    """
    bl_idname = "hb_face_frame.apply_finished_end_to_other_side"
    bl_label = "Apply to Other Side"
    bl_description = (
        "Copy this side's finished-end settings (type, flush amount, "
        "extend back, return width and return member types) to the "
        "opposite side"
    )
    bl_options = {'UNDO'}

    cabinet_name: bpy.props.StringProperty(name="Cabinet", default="")  # type: ignore
    side: bpy.props.EnumProperty(
        name="Source Side",
        items=[('LEFT', "Left", ""), ('RIGHT', "Right", "")],
        default='LEFT',
    )  # type: ignore

    def execute(self, context):
        obj = bpy.data.objects.get(self.cabinet_name)
        root = types_face_frame.find_cabinet_root(obj) if obj else None
        if root is None:
            self.report({'WARNING'}, "No face frame cabinet found")
            return {'CANCELLED'}
        cab = root.face_frame_cabinet
        src = self.side.lower()
        dst = 'right' if src == 'left' else 'left'
        with types_face_frame.suspend_recalc():
            for prop in _FIN_END_SIDE_PROPS:
                setattr(cab, f'{dst}_{prop}', getattr(cab, f'{src}_{prop}'))
        self.report(
            {'INFO'},
            f"Copied {src} finished end settings to {dst} side")
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


def _cutout_mod_inputs(obj, mod):
    """Read a cutout modifier's stored geometry back out, or None when it can't
    be read. Edit reopens the dialog on these values, and Cancel puts them back."""
    cpm = CabinetPartModifier(obj)
    cpm.mod = mod
    try:
        return {'x': float(cpm.get_input('X')),
                'end_x': float(cpm.get_input('End X')),
                'y': float(cpm.get_input('Y')),
                'end_y': float(cpm.get_input('End Y')),
                'depth': float(cpm.get_input('Route Depth')),
                'flip_z': bool(cpm.get_input('Flip Z'))}
    except Exception:
        return None


def _write_cutout_inputs(obj, mod, state):
    """Write a _cutout_mod_inputs() snapshot straight back to the modifier."""
    cpm = CabinetPartModifier(obj)
    cpm.mod = mod
    cpm.set_input('X', state['x'])
    cpm.set_input('End X', state['end_x'])
    cpm.set_input('Y', state['y'])
    cpm.set_input('End Y', state['end_y'])
    cpm.set_input('Route Depth', state['depth'])
    cpm.set_input('Flip Z', state['flip_z'])
    obj.update_tag()


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
    cutout is built immediately and updates LIVE as the dialog fields change.

    The same operator ADDS and EDITS: called with mod_name set to an existing
    Cutout modifier it reopens on that cut's values instead of building a new
    one, so a cutout can be corrected in place rather than removed and re-added.
    Cancel on an edit restores the values it opened with; Cancel on an add
    leaves the new cutout in place (drop it with Remove Cutout)."""
    bl_idname = "hb_face_frame.add_part_cutout"
    bl_label = "Add Cutout"
    bl_description = ("Cut a rectangular hole or route into this part "
                      "(fan/liner opening, light route, outlet)")
    bl_options = {'REGISTER', 'UNDO'}

    # Live-dialog binding: the cutout is created on invoke and each field write
    # fans straight to its CPM_CUTOUT inputs (same pattern as the Misc / Door
    # Part dimension dialogs). Target resolved by name each tick.
    source_obj_name: StringProperty(default='', options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore
    # Empty adds a new cutout; set to an existing Cutout modifier's name (what
    # the Edit entries pass) reopens the dialog on that one. SKIP_SAVE keeps an
    # edit from leaking into the next plain Add.
    mod_name: StringProperty(default='', options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore
    # JSON snapshot of the values an edit opened on, for Cancel. Empty on an add.
    restore_state: StringProperty(default='', options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore

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

    @classmethod
    def description(cls, context, properties):
        if getattr(properties, 'mod_name', ''):
            return "Reopen this cutout and change its size, position or depth"
        return cls.bl_description

    def _seed_new(self, length, width, thickness):
        self.cutout_length = min(units.inch(4.0), length)
        self.cutout_width = min(units.inch(4.0), width)
        self.center = True
        self.offset_length = 0.0
        self.offset_width = 0.0
        self.through = True
        self.route_depth = min(units.inch(0.25), thickness)
        self.back_face = False

    def _seed_from_state(self, state, length, width, thickness):
        """Fill the dialog from an existing cutout's stored inputs."""
        cl = max(state['end_x'] - state['x'], 0.0)
        cw = max(state['end_y'] - state['y'], 0.0)
        self.cutout_length = cl
        self.cutout_width = cw
        self.offset_length = state['x']
        self.offset_width = state['y']
        # Centred and through aren't stored flags - they're how the cut was
        # placed - so infer them, or a centred cutout reopens with the box clear.
        eps = units.inch(0.001)
        self.center = (abs(state['x'] - (length - cl) / 2.0) < eps
                       and abs(state['y'] - (width - cw) / 2.0) < eps)
        self.through = state['depth'] >= thickness - eps
        self.route_depth = min(state['depth'], thickness)
        self.back_face = state['flip_z']

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
        # mod_name arrives set from an Edit entry and empty from Add. Park it in
        # a local and blank the property while the fields are seeded: the update
        # callbacks bail on an empty mod_name, so seeding can't fan back over
        # values still being read (the same ordering the add path relies on).
        target = self.mod_name
        self.mod_name = ''
        self.restore_state = ''
        editing = bool(target) and obj.modifiers.get(target) is not None
        if editing:
            state = _cutout_mod_inputs(obj, obj.modifiers[target])
            if state is None:
                self.report({'ERROR'}, "This cutout could not be read")
                return {'CANCELLED'}
            self.restore_state = json.dumps(state)
            self._seed_from_state(state, length, width, thickness)
        else:
            self._seed_new(length, width, thickness)
            # Build the live cutout now so it previews as the dialog opens.
            target = _unique_cutout_name(obj)
            cpm = part.add_part_modifier(_CUTOUT_TOKEN, target)
            cpm.mod.show_viewport = True
            cpm.mod.show_render = True
        self.source_obj_name = obj.name
        self.mod_name = target
        _apply_cutout_live(self)
        title = "Edit Cutout" if editing else "Add Cutout"
        try:
            return context.window_manager.invoke_props_dialog(
                self, width=280, title=title)
        except TypeError:
            # Dialog signature with no title argument.
            return context.window_manager.invoke_props_dialog(self, width=280)

    def draw(self, context):
        col = self.layout.column(align=True)
        # The part's own Length x Width, in the same order as the two fields
        # under it. Length is the part's long edge, which is not always the
        # direction the user expects - the usual source of "it cut the wrong way".
        obj = _cutout_part_for_dialog(self)
        if obj is not None:
            try:
                part = GeoNodeCutpart(obj)
                unit = context.scene.unit_settings
                col.label(text="Part: %s x %s" % (
                    units.unit_to_string(unit, part.get_input('Length')),
                    units.unit_to_string(unit, part.get_input('Width'))))
            except Exception:
                pass
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

    def cancel(self, context):
        """Dismissing an EDIT puts the cut back the way it was found. An add has
        no snapshot, so its new cutout stays (drop it with Remove Cutout)."""
        if not self.restore_state:
            return
        obj = _cutout_part_for_dialog(self)
        if obj is None or not self.mod_name:
            return
        mod = obj.modifiers.get(self.mod_name)
        if mod is None:
            return
        try:
            state = json.loads(self.restore_state)
        except ValueError:
            return
        _write_cutout_inputs(obj, mod, state)


class hb_face_frame_OT_remove_part_cutout(bpy.types.Operator):
    """Remove a machining cutout from this part. With mod_name set (what the
    Remove entries pass) it drops that one; with no name it drops the most
    recently added, which is what a part carrying a single cutout wants."""
    bl_idname = "hb_face_frame.remove_part_cutout"
    bl_label = "Remove Cutout"
    bl_description = "Remove this machining cutout from the part"
    bl_options = {'REGISTER', 'UNDO'}

    mod_name: StringProperty(default='', options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore

    @classmethod
    def poll(cls, context):
        return len(_user_cutout_mods(context.active_object)) > 0

    def execute(self, context):
        obj = context.active_object
        mods = _user_cutout_mods(obj)
        if not mods:
            self.report({'WARNING'}, "No cutout to remove")
            return {'CANCELLED'}
        named = [m for m in mods if m.name == self.mod_name]
        obj.modifiers.remove(named[0] if named else mods[-1])
        obj.update_tag()
        return {'FINISHED'}


class hb_face_frame_OT_set_bottom_rail_profile(bpy.types.Operator):
    """Set the decorative bottom-rail profile from the right-click menu.
    Invoked on a bottom RAIL, the pick lands on that rail's bay only
    (the per-bay bottom_rail_profile override) -- users size the bays
    first, then style the one rail they clicked, without restyling its
    neighbours. Every selected bottom rail takes the pick, so a
    multi-rail selection styles in one go. With no rail in the
    selection (the valance board / cabinet menus) the pick sets the
    cabinet-level enum as before. Either write's update callback
    re-runs the recalc."""
    bl_idname = "hb_face_frame.set_bottom_rail_profile"
    bl_label = "Set Bottom Rail Profile"
    bl_description = "Cut this decorative profile into the selected bottom rail"
    bl_options = {'UNDO'}

    profile_id: StringProperty(default='NONE', options={'SKIP_SAVE'})  # type: ignore

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        rails = [o for o in context.selected_objects
                 if o.get('hb_part_role') == types_face_frame.PART_ROLE_BOTTOM_RAIL]
        active = context.active_object
        if (active is not None and active not in rails
                and active.get('hb_part_role') == types_face_frame.PART_ROLE_BOTTOM_RAIL):
            rails.append(active)
        if rails:
            # Rail-scoped: write each rail's segment-start bay override.
            # 'NONE' here FORCES a plain rail on that bay (distinct from
            # the bay enum's 'CABINET' inherit default).
            changed = 0
            for rail in rails:
                bay = types_face_frame.bay_cage_for_bottom_rail(rail)
                if bay is None:
                    continue
                try:
                    bay.face_frame_bay.bottom_rail_profile = self.profile_id
                except TypeError:
                    self.report({'WARNING'}, f"Unknown profile: {self.profile_id}")
                    return {'CANCELLED'}
                changed += 1
            if not changed:
                self.report({'WARNING'}, "Could not resolve the rail's bay")
                return {'CANCELLED'}
            return {'FINISHED'}
        root = types_face_frame.find_cabinet_root(active)
        if root is None:
            self.report({'WARNING'}, "No cabinet found for this part")
            return {'CANCELLED'}
        try:
            root.face_frame_cabinet.bottom_rail_profile = self.profile_id
        except TypeError:
            self.report({'WARNING'}, f"Unknown profile: {self.profile_id}")
            return {'CANCELLED'}
        return {'FINISHED'}


# Front roles that carry a pull - the roles the Set Pull command
# surfaces on. A false front is bare unless the user picks a pull for
# it, so it is offered here too and the choice also flips the opening's
# false_front_pull flag (see _sync_false_front_pull).
_ROLES_WITH_PULL = frozenset({
    types_face_frame.PART_ROLE_DOOR,
    types_face_frame.PART_ROLE_DRAWER_FRONT,
    types_face_frame.PART_ROLE_PULLOUT_FRONT,
    types_face_frame.PART_ROLE_TILT_OUT,
    types_face_frame.PART_ROLE_FALSE_FRONT,
})


def _sync_false_front_pull(op_props, override):
    """Mirror a pull assignment onto a FALSE_FRONT opening's
    false_front_pull flag: any real pull (or the scene default) turns
    the pull on, the 'NONE' sentinel turns it off. Other front types
    are untouched."""
    if op_props.front_type != 'FALSE_FRONT':
        return
    op_props.false_front_pull = override != 'NONE'


def _set_pull_category_items(self, context):
    """DEFAULT (scene selection) + the real pull categories + NO_PULL."""
    from .. import pulls
    items = [('DEFAULT', "Scene Default",
              "Use the scene-wide pull selection for this front kind")]
    for cat_id, label, desc in pulls.get_pull_categories():
        if cat_id == 'NONE':
            continue
        items.append((cat_id, label, desc))
    items.append(('NO_PULL', "No Pull", "Remove the pull from the front"))
    return items


def _set_pull_items(self, context):
    """Pulls in the operator's chosen category; a placeholder when the
    choice needs no pull file (scene default / no pull)."""
    from .. import pulls
    if self.category in ('DEFAULT', 'NO_PULL'):
        return [('NONE', "-", "")]
    real_cat = None
    for cat_id, label, _d in pulls.get_pull_categories():
        if cat_id == self.category:
            real_cat = label
            break
    items = pulls.get_pulls_in_category(real_cat) if real_cat else []
    return items or [('NONE', "-", "No pulls in this category")]


class hb_face_frame_OT_set_front_pull(bpy.types.Operator):
    """Set the pull on the selected door / drawer fronts, or on every
    door and drawer front in the room. Per front the choice is stored on
    the owning opening (fronts are rebuilt every recalc), so it sticks:
    Scene Default returns the front to the scene-wide selection, No Pull
    removes the pull, and a specific pull overrides just these fronts.
    Room-wide it becomes the pull each zone uses. The finish shown here
    is the scene's own - one material across every pull."""
    bl_idname = "hb_face_frame.set_front_pull"
    bl_label = "Set Pull"
    bl_description = ("Set the pull used by the selected fronts "
                      "(stored per opening)")
    bl_options = {'UNDO'}

    scope: bpy.props.EnumProperty(
        name="Apply To",
        items=[
            ('SELECTED', "Selected Fronts",
             "Only the fronts selected right now (stored per opening)"),
            ('ALL', "All Doors and Drawer Fronts",
             "Every door and drawer front in the room: this pull becomes "
             "the one each zone uses, and per-front choices that would "
             "shadow it are cleared"),
        ],
        # SKIP_SAVE: the dialog always opens on Selected Fronts. Blender
        # would otherwise remember the last choice, and a room-wide
        # rewrite is not something to inherit from an earlier press.
        default='SELECTED', options={'SKIP_SAVE'})  # type: ignore
    category: bpy.props.EnumProperty(
        name="Category", items=_set_pull_category_items)  # type: ignore
    pull: bpy.props.EnumProperty(
        name="Pull", items=_set_pull_items)  # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj is not None
                and obj.get('hb_part_role') in _ROLES_WITH_PULL)

    def _target_openings(self, context):
        """Owning opening cages of every selected front part. Corner
        cabinet doors have no opening cage and drop out (reported)."""
        from . import ops_cabinet
        openings = {}
        skipped = 0
        for obj in context.selected_objects:
            if obj.get('hb_part_role') not in _ROLES_WITH_PULL:
                continue
            opening = ops_cabinet._find_owning_opening(obj)
            if opening is None:
                skipped += 1
                continue
            openings[opening.name] = opening
        return list(openings.values()), skipped

    def _apply_everywhere(self, context, override, override_cat):
        """Make this pull the one every door and drawer front uses.

        Writes it to all four zone assignments, then takes the
        per-opening overrides out of the way - without that a front
        somebody had set by hand would keep shadowing the new pull, and
        "all fronts" would quietly not mean all.

        A false front is left alone unless it already carries a pull:
        it has none by default (a sink front reads as dead), and this
        command is about which model is used, not about handing dead
        fronts a pull they were never given.
        """
        scene_props = context.scene.hb_face_frame
        for zone in ('base', 'tall', 'upper', 'drawers'):
            setattr(scene_props, 'pull_assign_' + zone, override)
            setattr(scene_props, 'pull_assign_' + zone + '_category',
                    override_cat)
        cleared = retargeted = 0
        with types_face_frame.suspend_recalc():
            for obj in context.scene.objects:
                if not obj.get(types_face_frame.TAG_OPENING_CAGE):
                    continue
                op_props = obj.face_frame_opening
                if op_props.front_type == 'FALSE_FRONT':
                    if not op_props.false_front_pull:
                        continue
                    op_props.pull_override_category = override_cat
                    op_props.pull_override = override
                    _sync_false_front_pull(op_props, override)
                    retargeted += 1
                elif op_props.pull_override or op_props.pull_override_category:
                    op_props.pull_override_category = ''
                    op_props.pull_override = ''
                    cleared += 1
            # Zone strings carry no update callback - rebuild here, the
            # same way the pull library's Assign buttons do.
            for obj in context.scene.objects:
                if obj.get(types_face_frame.TAG_CABINET_CAGE):
                    types_face_frame.recalculate_face_frame_cabinet(obj)
        return cleared, retargeted

    def invoke(self, context, event):
        # Seed from the active front's current override so reopening
        # the dialog shows the standing choice.
        from . import ops_cabinet
        opening = ops_cabinet._find_owning_opening(context.active_object)
        if opening is not None:
            current = opening.face_frame_opening.pull_override
            if current == 'NONE':
                self.category = 'NO_PULL'
            elif current:
                from .. import pulls
                cat = opening.face_frame_opening.pull_override_category
                for cat_id, label, _d in pulls.get_pull_categories():
                    if label == cat:
                        self.category = cat_id
                        break
                for item_id, _l, _d in _set_pull_items(self, context):
                    if item_id == current:
                        self.pull = item_id
                        break
        return context.window_manager.invoke_props_dialog(self, width=280)

    def draw(self, context):
        from .. import pulls
        col = self.layout.column(align=True)
        col.prop(self, 'category', text="Category")
        if self.category not in ('DEFAULT', 'NO_PULL'):
            col.prop(self, 'pull', text="Pull")
            if self.pull not in ('NONE', ''):
                real_cat = None
                for cat_id, label, _d in pulls.get_pull_categories():
                    if cat_id == self.category:
                        real_cat = label
                        break
                icon_id = pulls.load_pull_thumbnail_icon(
                    self.pull, real_cat)
                if icon_id:
                    col.template_icon(icon_value=icon_id, scale=4.0)
        # Scene Default is a per-front instruction ("follow the zone"),
        # so there is nothing to send everywhere.
        scope = col.column(align=True)
        scope.enabled = self.category != 'DEFAULT'
        scope.separator()
        scope.prop(self, 'scope', text="Apply To")
        # The finish is one material across every pull in the scene, not
        # a per-front choice - said plainly so nobody reads it as one.
        col.separator()
        fin = col.column(align=True)
        fin.label(text="Finish (every pull in the room):")
        fin.prop(context.scene.hb_face_frame, 'pull_finish', text="")

    def execute(self, context):
        from .. import pulls
        room_wide = self.scope == 'ALL' and self.category != 'DEFAULT'
        openings, skipped = self._target_openings(context)
        if not openings and not room_wide:
            self.report({'WARNING'},
                        "No fronts with openings selected"
                        + (" (corner cabinet doors use the scene pull)"
                           if skipped else ""))
            return {'CANCELLED'}
        if self.category == 'DEFAULT':
            override, override_cat = '', ''
        elif self.category == 'NO_PULL':
            override, override_cat = 'NONE', ''
        else:
            if self.pull in ('NONE', ''):
                self.report({'WARNING'}, "Pick a pull from the category")
                return {'CANCELLED'}
            override = self.pull
            override_cat = ''
            for cat_id, label, _d in pulls.get_pull_categories():
                if cat_id == self.category:
                    override_cat = label
                    break
        stem = ("scene default" if self.category == 'DEFAULT'
                else "no pull" if self.category == 'NO_PULL'
                else os.path.splitext(override)[0])
        if room_wide:
            cleared, retargeted = self._apply_everywhere(
                context, override, override_cat)
            msg = f"Every door and drawer front set to {stem}"
            if cleared:
                msg += f"; {cleared} per-front choice(s) cleared"
            if retargeted:
                msg += f"; {retargeted} false front(s) followed"
            self.report({'INFO'}, msg)
            return {'FINISHED'}
        with types_face_frame.suspend_recalc():
            for opening in openings:
                op_props = opening.face_frame_opening
                op_props.pull_override_category = override_cat
                op_props.pull_override = override
                _sync_false_front_pull(op_props, override)
        msg = f"{len(openings)} opening(s) set to {stem}"
        if skipped:
            msg += f"; {skipped} corner front(s) skipped"
        self.report({'INFO'}, msg)
        return {'FINISHED'}


_PULL_LOCATION_ITEMS = [
    ('AUTO', "Automatic", "Cabinet-type rule (base: top, upper: bottom, tall: by door height)"),
    ('TOP', "Top of Door", "Base-style: measured down from the top of the door"),
    ('MIDDLE', "Middle of Door", "Centered on the door height"),
    ('BOTTOM', "Bottom of Door", "Upper-style: measured up from the bottom of the door"),
    ('TALL', "Tall Reach Height", "Tall-style: the tall vertical offset up from the door bottom"),
]


class hb_face_frame_OT_set_pull_location(bpy.types.Operator):
    """Pin the vertical pull position on the selected doors' openings:
    top / middle / bottom of the door (or the tall reach height), or
    back to the automatic cabinet-type rule. Stored per opening so it
    survives recalcs; the scene offsets still set the exact distances."""
    bl_idname = "hb_face_frame.set_pull_location"
    bl_label = "Set Pull Location"
    bl_description = ("Set where the pull sits on the selected doors "
                      "(stored per opening)")
    bl_options = {'UNDO'}

    location: bpy.props.EnumProperty(
        name="Location", items=_PULL_LOCATION_ITEMS,
        default='AUTO')  # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj is not None
                and obj.get('hb_part_role') in ('DOOR', 'PULLOUT_FRONT'))

    def execute(self, context):
        from . import ops_cabinet
        openings = {}
        skipped = 0
        for obj in context.selected_objects:
            if obj.get('hb_part_role') not in ('DOOR', 'PULLOUT_FRONT'):
                continue
            opening = ops_cabinet._find_owning_opening(obj)
            if opening is None:
                skipped += 1
                continue
            openings[opening.name] = opening
        if not openings:
            self.report({'WARNING'},
                        "No doors with openings selected"
                        + (" (corner cabinet doors use the automatic rule)"
                           if skipped else ""))
            return {'CANCELLED'}
        with types_face_frame.suspend_recalc():
            for opening in openings.values():
                opening.face_frame_opening.pull_location_override = self.location
        label = next(l for i, l, _d in _PULL_LOCATION_ITEMS
                     if i == self.location)
        msg = f"{len(openings)} opening(s): pulls at {label.lower()}"
        if skipped:
            msg += f"; {skipped} corner front(s) skipped"
        self.report({'INFO'}, msg)
        return {'FINISHED'}


def _fb_bays_changed(self, context):
    """Write the dialog's bay toggles back to the cabinet's
    finished_bottom_bays (all checked stores '' - whole cabinet), so
    the panels rebuild live like the other options."""
    if getattr(self, '_fb_init', False):
        return
    # The shelf dialog never draws these, and with no segment keys behind
    # them they would write an empty scope over the cabinet's own.
    if getattr(self, 'shelf_split', ''):
        return
    root = bpy.data.objects.get(self.cabinet_name)
    if root is None:
        return
    keys = [k for k in self.segment_keys.split(',') if k]
    selected = [k for i, k in enumerate(keys) if self.bay_flags[i]]
    if len(selected) == len(keys):
        value = ''                                   # all of them
    elif selected:
        value = ','.join(selected)
    else:
        # Every box cleared. Joining nothing gives '', which reads back
        # as ALL - the opposite of what was asked for.
        value = types_face_frame.FINISHED_BOTTOM_BAYS_NONE
    cab = root.face_frame_cabinet
    if cab.finished_bottom_bays != value:
        cab.finished_bottom_bays = value


def _fb_shelf_from_part(obj):
    """(split node, splitter index) for the mid-rail shelf a clicked part
    stands for, or None when the click was not about a shelf.

    Either the shelf itself, or the finish panel hanging under it - that
    panel is parented to the shelf's split node and carries the shelf's
    index in its hb_fb_key, so re-opening the dialog from the panel lands
    back on the same shelf.
    """
    if obj is None:
        return None
    role = obj.get('hb_part_role')
    if role == types_face_frame.PART_ROLE_BAY_SHELF:
        split = obj.parent
        if split is None or not split.get(types_face_frame.TAG_SPLIT_NODE):
            return None
        return split, obj.get('hb_splitter_index', 0)
    if role == types_face_frame.PART_ROLE_FINISHED_BOTTOM:
        key = obj.get('hb_fb_key') or ''
        if not key.startswith('shelf:'):
            return None
        split = obj.parent
        if split is None or not split.get(types_face_frame.TAG_SPLIT_NODE):
            return None
        try:
            return split, int(key.rsplit(':', 1)[1])
        except ValueError:
            return None
    return None


def _fb_splitter_entry(split, idx):
    """The per-splitter entry at `idx`, growing the collection to reach
    it. Same lazy growth the backing toggle uses."""
    coll = split.face_frame_split.splitter_widths
    while len(coll) <= idx:
        coll.add()
    return coll[idx]


class hb_face_frame_OT_set_finished_bottom(bpy.types.Operator):
    """Set the finished bottom condition on the clicked cabinet.
    Live-bound to the cabinet's props (the finish panel, LED route,
    and optional render light rebuild as options change); with multiple
    bottom segments (raised / dropped bays) each gets its own toggle.
    Opened from a shelf behind a mid rail it finishes that shelf instead
    - the underside on show over an appliance opening. The room button
    copies this cabinet's condition to every standard upper in the
    scene."""
    bl_idname = "hb_face_frame.set_finished_bottom"
    bl_label = "Set Finished Bottom"
    bl_description = ("Set the finished bottom condition for this "
                      "cabinet bottom or shelf (finish panel + LED route)")
    bl_options = {'UNDO'}

    cabinet_name: StringProperty(
        default='', options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore
    segment_keys: StringProperty(
        default='', options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore
    # Set when the dialog was opened from a mid-rail shelf: the split
    # node that owns it and the shelf's splitter index.
    shelf_split: StringProperty(
        default='', options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore
    shelf_index: IntProperty(
        default=0, options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore
    bay_flags: BoolVectorProperty(
        name="Bottoms", size=16, options={'SKIP_SAVE'},
        update=_fb_bays_changed)  # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj is None:
            return False
        root = types_face_frame.find_cabinet_root(obj)
        if root is None or root.face_frame_cabinet.corner_type != 'NONE':
            return False
        # A mid-rail shelf offers the condition on any cabinet type; the
        # carcass bottom stays an upper's business.
        return (root.get('CABINET_TYPE') == 'UPPER'
                or _fb_shelf_from_part(obj) is not None)

    def invoke(self, context, event):
        obj = context.active_object
        root = types_face_frame.find_cabinet_root(obj)
        if root is None:
            return {'CANCELLED'}
        self.cabinet_name = root.name
        shelf = _fb_shelf_from_part(obj)
        if shelf is not None:
            # Clicking the command on a shelf IS the ask, so switch that
            # shelf on. Unchecking it in the dialog takes it back off,
            # and the cabinet's own condition is left alone.
            split, idx = shelf
            self.shelf_split = split.name
            self.shelf_index = idx
            _fb_splitter_entry(split, idx).finished_bottom = True
            # A shelf is not the cabinet's bottom, and asking for one
            # says nothing about the other. The condition itself is a
            # cabinet property, so on an upper that had none the moment
            # this dialog set one every carcass bottom took it up too -
            # an empty scope means all of them. Say none of them
            # instead; a cabinet already finishing its bottoms keeps
            # whatever scope it was given.
            cab = root.face_frame_cabinet
            if cab.finished_bottom_type == 'NONE':
                cab.finished_bottom_bays = \
                    types_face_frame.FINISHED_BOTTOM_BAYS_NONE
            return context.window_manager.invoke_props_dialog(self, width=280)
        self.shelf_split = ''
        # One toggle per live carcass-bottom segment (same filter the
        # builder uses), seeded from the cabinet's current scope.
        bottoms = [c for c in root.children
                   if c.get('hb_part_role')
                   == types_face_frame.PART_ROLE_BOTTOM
                   and not c.hide_viewport
                   and not c.get('IS_MANUAL_PART')]
        keys = sorted({str(c.get('hb_segment_start_bay', 0))
                       for c in bottoms},
                      key=lambda k: int(k) if k.lstrip('-').isdigit()
                      else 0)
        self.segment_keys = ','.join(keys[:16])
        cab = root.face_frame_cabinet
        scope = {s.strip() for s in cab.finished_bottom_bays.split(',')
                 if s.strip()}
        self._fb_init = True
        for i, k in enumerate(keys[:16]):
            self.bay_flags[i] = (not scope) or (k in scope)
        self._fb_init = False
        return context.window_manager.invoke_props_dialog(self, width=280)

    def draw(self, context):
        layout = self.layout
        root = bpy.data.objects.get(self.cabinet_name)
        if root is None:
            layout.label(text="Cabinet not found", icon='INFO')
            return
        cab = root.face_frame_cabinet
        col = layout.column(align=True)
        col.prop(cab, 'finished_bottom_type', text="Condition")
        split = (bpy.data.objects.get(self.shelf_split)
                 if self.shelf_split else None)
        if split is not None:
            # Shelf dialog: the target is the shelf that was clicked, so
            # the bay toggles (which are about the carcass bottom) and
            # the room apply (uppers only) have nothing to say here.
            entry = _fb_splitter_entry(split, self.shelf_index)
            shelf_col = col.column(align=True)
            shelf_col.enabled = cab.finished_bottom_type != 'NONE'
            shelf_col.prop(entry, 'finished_bottom',
                           text="Finish This Shelf")
        else:
            keys = [k for k in self.segment_keys.split(',') if k]
            if len(keys) > 1:
                bays = col.column(align=True)
                bays.enabled = cab.finished_bottom_type != 'NONE'
                bays.label(text="Apply To:")
                for i, k in enumerate(keys):
                    try:
                        label = f"Bay {int(k) + 1}"
                    except ValueError:
                        label = f"Bay {k}"
                    bays.prop(self, 'bay_flags', index=i, text=label)
        sub = col.column(align=True)
        sub.enabled = cab.finished_bottom_type != 'NONE'
        sub.prop(cab, 'finished_bottom_led_route', text="LED Route")
        route = sub.column(align=True)
        route.enabled = cab.finished_bottom_led_route
        route.prop(cab, 'finished_bottom_route_width', text="Route Width")
        route.prop(cab, 'finished_bottom_route_depth', text="Route Depth")
        route.prop(cab, 'finished_bottom_route_inset', text="Route Inset")
        route.prop(cab, 'finished_bottom_light', text="LED Light (Render)")
        if split is None:
            col.separator()
            col.operator("hb_face_frame.apply_finished_bottom_to_room",
                         text="Apply to All Uppers in Room",
                         icon='DUPLICATE').cabinet_name = self.cabinet_name

    def execute(self, context):
        # Live-bound via the cabinet props' update callbacks.
        return {'FINISHED'}


class hb_face_frame_OT_apply_finished_bottom_to_room(bpy.types.Operator):
    """Copy the named cabinet's finished bottom condition to every
    standard upper cabinet in the scene."""
    bl_idname = "hb_face_frame.apply_finished_bottom_to_room"
    bl_label = "Apply Finished Bottom to Room"
    bl_description = ("Copy this finished bottom condition to every "
                      "upper cabinet in the room")
    bl_options = {'UNDO'}

    cabinet_name: StringProperty(
        default='', options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore

    def execute(self, context):
        source = bpy.data.objects.get(self.cabinet_name)
        if source is None:
            source = types_face_frame.find_cabinet_root(
                context.active_object)
        if source is None:
            self.report({'WARNING'}, "No source cabinet")
            return {'CANCELLED'}
        src_cab = source.face_frame_cabinet
        count = 0
        with types_face_frame.suspend_recalc():
            for obj in context.scene.objects:
                if not obj.get(types_face_frame.TAG_CABINET_CAGE):
                    continue
                if obj.get('CABINET_TYPE') != 'UPPER':
                    continue
                cab = obj.face_frame_cabinet
                if cab.corner_type != 'NONE':
                    continue
                cab.finished_bottom_type = src_cab.finished_bottom_type
                cab.finished_bottom_led_route = \
                    src_cab.finished_bottom_led_route
                cab.finished_bottom_route_width = \
                    src_cab.finished_bottom_route_width
                cab.finished_bottom_route_depth = \
                    src_cab.finished_bottom_route_depth
                cab.finished_bottom_route_inset = \
                    src_cab.finished_bottom_route_inset
                cab.finished_bottom_light = src_cab.finished_bottom_light
                # Bay scope is cabinet-specific; room apply covers
                # every bottom segment.
                cab.finished_bottom_bays = ''
                count += 1
        self.report({'INFO'},
                    f"Finished bottom applied to {count} upper(s)")
        return {'FINISHED'}


classes = (
    hb_face_frame_OT_set_front_pull,
    hb_face_frame_OT_set_pull_location,
    hb_face_frame_OT_set_finished_bottom,
    hb_face_frame_OT_apply_finished_bottom_to_room,
    hb_face_frame_OT_set_part_width,
    hb_face_frame_OT_set_finished_end_condition,
    hb_face_frame_OT_apply_finished_end_to_other_side,
    hb_face_frame_OT_set_part_scribe,
    hb_face_frame_OT_set_panel_seam,
    hb_face_frame_OT_remove_panel_seam,
    hb_face_frame_OT_toggle_stile_to_floor,
    hb_face_frame_OT_set_cabinet_column,
    hb_face_frame_OT_remove_bottom_rail,
    hb_face_frame_OT_toggle_flush_bottom_rail,
    hb_face_frame_OT_remove_mid_rail,
    hb_face_frame_OT_toggle_splitter_backing,
    hb_face_frame_OT_set_misc_part_dimensions,
    hb_face_frame_OT_set_door_part_dimensions,
    hb_face_frame_OT_assign_active_door_style,
    hb_face_frame_OT_toggle_door_part_pull,
    hb_face_frame_OT_switch_door_part_pull_side,
    hb_face_frame_OT_toggle_door_part_front_kind,
    hb_face_frame_OT_set_door_frame,
    hb_face_frame_OT_set_door_hardware,
    hb_face_frame_OT_set_door_shape,
    hb_face_frame_OT_set_cabinet_part_size,
    hb_face_frame_OT_make_part_editable,
    hb_face_frame_OT_revert_part_to_parametric,
    hb_face_frame_OT_add_part_cutout,
    hb_face_frame_OT_remove_part_cutout,
    hb_face_frame_OT_set_bottom_rail_profile,
)


register, unregister = bpy.utils.register_classes_factory(classes)
