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
from bpy.props import FloatProperty, StringProperty

from .. import types_face_frame


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
    target, attr = _resolve_width_target(obj, role, root)
    if target is None:
        return None
    return getattr(target, attr)


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

    Bay-internal splitters have no unlock prop (per-split splitter_width
    is overwritten unconditionally by the style cascade); nothing to
    flip for those roles.
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
            split.face_frame_split.splitter_width = value
        return


def _on_value_update(self, context):
    """FloatProperty update callback for the operator's value prop.
    Resolves the source part, role, and cabinet root each tick (so a
    user changing the active object mid-drag doesn't strand the
    operator), then fans the new value out through one suspended
    recalc.
    """
    if getattr(self, '_suppress_update', False):
        return
    obj = bpy.data.objects.get(self.source_obj_name)
    if obj is None:
        return
    role = obj.get('hb_part_role')
    root = types_face_frame.find_cabinet_root(obj)
    if root is None:
        return
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

        self.source_obj_name = obj.name

        # Pre-flip unlocks so a later style apply leaves the user's value
        # alone. For rails, flips on every bay in the current segment so
        # the cascade can't re-split the rail.
        _flip_unlock_for_role(obj, role, root)

        # Seed value from the current width without firing the fanout
        # (which would be a no-op write but still kick off a recalc).
        target, attr = _resolve_width_target(obj, role, root)
        self._suppress_update = True
        try:
            self.value = getattr(target, attr) if target is not None else 0.0
        finally:
            self._suppress_update = False

        return context.window_manager.invoke_props_dialog(self, width=260)

    def draw(self, context):
        obj = bpy.data.objects.get(self.source_obj_name) or context.active_object
        col = self.layout.column(align=True)
        if obj is not None:
            col.label(text=obj.name, icon='SNAP_EDGE')
        col.prop(self, 'value', text="Width")

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
        return obj.get('hb_part_role') in _END_STILE_ROLES

    def execute(self, context):
        obj = context.active_object
        role = obj.get('hb_part_role')
        root = types_face_frame.find_cabinet_root(obj)
        if root is None:
            return {'CANCELLED'}
        cab = root.face_frame_cabinet
        if role == types_face_frame.PART_ROLE_LEFT_STILE:
            cab.extend_left_stile_to_floor = not cab.extend_left_stile_to_floor
        else:
            cab.extend_right_stile_to_floor = not cab.extend_right_stile_to_floor
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

classes = (
    hb_face_frame_OT_set_part_width,
    hb_face_frame_OT_set_part_scribe,
    hb_face_frame_OT_toggle_stile_to_floor,
)


register, unregister = bpy.utils.register_classes_factory(classes)
