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
from ....hb_types import GeoNodeCutpart


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

        # Seed the dialog value BEFORE source_obj_name is set. The
        # value prop's update callback (_on_value_update) bails while
        # source_obj_name is empty, so the seed write cannot fan out or
        # trigger a recalc. An operator-instance flag did not survive
        # into the callback reliably, hence the empty-name approach.
        # Seed from the EFFECTIVE width (handles per-splitter overrides,
        # which _resolve_width_target's scalar target wouldn't reflect).
        self.value = _get_current_width(obj, role, root)

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
                return mod[item.identifier]
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


def _on_df_mid_mode(self, context):
    front = _door_frame_for_dialog(self)
    if front is not None:
        store = _frame_store(front)
        store['HB_FRAME_OVR_MID_RAIL_MODE'] = self.mid_rail_mode
        if self.mid_rail_mode == 'CUSTOM':
            store['HB_FRAME_OVR_MID_RAIL_LOCATION'] = self.mid_rail_location
        _reapply_frame_store(store, front)


def _on_df_mid_loc(self, context):
    front = _door_frame_for_dialog(self)
    if front is not None:
        store = _frame_store(front)
        store['HB_FRAME_OVR_MID_RAIL_LOCATION'] = self.mid_rail_location
        if store.get('HB_FRAME_OVR_MID_RAIL_MODE') == 'CUSTOM':
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
        items=[('CENTERED', "Centered", "Mid rail centered vertically"),
               ('THIRD', "1/3 - 2/3", "Mid rail 1/3 up from the bottom"),
               ('CUSTOM', "Custom", "Mid rail at a custom location")],
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
        row.enabled = self.mid_rail_mode == 'CUSTOM'
        row.prop(self, 'mid_rail_location')

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


classes = (
    hb_face_frame_OT_set_part_width,
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
)


register, unregister = bpy.utils.register_classes_factory(classes)
