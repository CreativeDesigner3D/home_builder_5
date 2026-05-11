import bpy
from mathutils import Vector

from .. import types_face_frame
from .. import types_face_frame_corner
from .. import bay_presets
from .. import props_hb_face_frame
from ....units import inch
from .... import hb_types, hb_utils
from ...frameless.operators.ops_placement import toggle_cabinet_color


# ---------------------------------------------------------------------------
# Operator: drop a cabinet from the library
# ---------------------------------------------------------------------------
class hb_face_frame_OT_draw_cabinet(bpy.types.Operator):
    """Drop a face frame cabinet at the 3D cursor."""
    bl_idname = "hb_face_frame.draw_cabinet"
    bl_label = "Draw Face Frame Cabinet"
    bl_options = {'REGISTER', 'UNDO'}

    cabinet_name: bpy.props.StringProperty(
        name="Cabinet Name",
        description="The face frame cabinet type to draw",
        default="",
    )  # type: ignore

    bay_qty: bpy.props.IntProperty(
        name="Bay Quantity",
        description="Number of bays to create on the cabinet (1-10)",
        default=1, min=1, max=10,
    )  # type: ignore

    def execute(self, context):
        # Thin wrapper over the modal placement operator. Lets the
        # catalog browser keep calling hb_face_frame.draw_cabinet while
        # the actual placement (cursor follow, wall snap, click-to-
        # commit) lives in hb_face_frame.place_cabinet. Same pattern
        # frameless uses (see ops_placement.py in that library).
        if not self.cabinet_name:
            self.report({'WARNING'}, "No cabinet name supplied")
            return {'CANCELLED'}
        # Appliance products: invoke the appliance placement modal
        # (cursor follow + wall snap, fixed width, single instance).
        if self.cabinet_name in types_face_frame.APPLIANCE_NAME_DISPATCH:
            bpy.ops.hb_face_frame.place_appliance(
                'INVOKE_DEFAULT',
                appliance_name=self.cabinet_name,
            )
            return {'FINISHED'}
        # Corner cabinets get a dedicated placement modal - same
        # cursor-follow / GPU-dim feedback as regular cabinets, but
        # snaps to wall corners instead of gap edges and skips the
        # fill / bay-qty / typed-width affordances that don't apply
        # to a corner build.
        cls = types_face_frame.get_cabinet_class(self.cabinet_name)
        if cls is not None and issubclass(
                cls, types_face_frame_corner.CornerFaceFrameCabinet):
            bpy.ops.hb_face_frame.place_corner_cabinet(
                'INVOKE_DEFAULT',
                cabinet_name=self.cabinet_name,
            )
            return {'FINISHED'}
        bpy.ops.hb_face_frame.place_cabinet(
            'INVOKE_DEFAULT',
            cabinet_name=self.cabinet_name,
            bay_qty=self.bay_qty,
        )
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Operator: delete the active face frame cabinet (and any others selected)
# ---------------------------------------------------------------------------
class hb_face_frame_OT_delete_cabinet(bpy.types.Operator):
    """Delete every face frame cabinet currently selected."""
    bl_idname = "hb_face_frame.delete_cabinet"
    bl_label = "Delete Face Frame Cabinet"
    bl_description = "Delete the selected cabinet(s) and all their parts"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return types_face_frame.find_cabinet_root(context.active_object) is not None

    def execute(self, context):
        # Collect distinct cabinet roots from the selection so that
        # selecting any descendant (bay, opening, mid stile, part)
        # still resolves to the cabinet, and selecting multiple parts
        # of the same cabinet only triggers one delete.
        roots = []
        seen = set()
        for obj in context.selected_objects:
            root = types_face_frame.find_cabinet_root(obj)
            if root is None or root.name in seen:
                continue
            seen.add(root.name)
            roots.append(root)

        if not roots:
            self.report({'WARNING'}, "No face frame cabinet selected")
            return {'CANCELLED'}

        for root in roots:
            hb_utils.delete_obj_and_children(root)

        self.report({'INFO'}, f"Deleted {len(roots)} cabinet(s)")
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Operator: join multiple selected cabinets into one
# ---------------------------------------------------------------------------
class hb_face_frame_OT_join_cabinets(bpy.types.Operator):
    """Merge selected face frame cabinets into the active cabinet,
    sharing a continuous face frame. Each absorbed cabinet's bays
    (and per-opening configuration) carry over; the active cabinet
    is the survivor.
    """
    bl_idname = "hb_face_frame.join_cabinets"
    bl_label = "Join Cabinets"
    bl_description = (
        "Merge selected face frame cabinets into the active cabinet, "
        "sharing one continuous face frame"
    )
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        # Need at least two distinct face frame cabinets in the
        # selection, with the active object resolving to one of them.
        active_root = types_face_frame.find_cabinet_root(context.active_object)
        if active_root is None:
            return False
        seen = {active_root.name}
        for obj in context.selected_objects:
            root = types_face_frame.find_cabinet_root(obj)
            if root is not None:
                seen.add(root.name)
                if len(seen) >= 2:
                    return True
        return False

    def execute(self, context):
        active_root = types_face_frame.find_cabinet_root(context.active_object)
        if active_root is None:
            self.report({'ERROR'}, "No active face frame cabinet")
            return {'CANCELLED'}

        roots = []
        seen = set()
        for obj in context.selected_objects:
            root = types_face_frame.find_cabinet_root(obj)
            if root is None or root.name in seen:
                continue
            seen.add(root.name)
            roots.append(root)

        if len(roots) < 2:
            self.report({'WARNING'}, "Select two or more face frame cabinets")
            return {'CANCELLED'}

        # All selected cabinets must share a parent (same wall, or all
        # unparented). The merge primitive checks per-pair, but bailing
        # here gives a clearer error than "merge failed".
        if len({r.parent for r in roots}) > 1:
            self.report({'ERROR'}, "Cabinets must share the same parent")
            return {'CANCELLED'}

        # Sort left-to-right and pre-flight every adjacent pair before
        # any merge runs - half-merged state on a partial failure is
        # confusing for the user even with undo.
        roots.sort(key=lambda r: r.location.x)
        eps = 1e-4
        tol = inch(1.0)
        for a, b in zip(roots, roots[1:]):
            ap = a.face_frame_cabinet
            bp = b.face_frame_cabinet
            if abs(ap.height - bp.height) > eps:
                self.report({'ERROR'}, "Cabinets must match in height")
                return {'CANCELLED'}
            if abs(ap.depth - bp.depth) > eps:
                self.report({'ERROR'}, "Cabinets must match in depth")
                return {'CANCELLED'}
            if abs(a.matrix_world.translation.z - b.matrix_world.translation.z) > eps:
                self.report({'ERROR'}, "Cabinets must sit at the same Z")
                return {'CANCELLED'}
            if ap.corner_type != 'NONE' or bp.corner_type != 'NONE':
                self.report({'ERROR'}, "Corner cabinets cannot be joined")
                return {'CANCELLED'}
            if abs(b.location.x - (a.location.x + ap.width)) > tol:
                self.report({'ERROR'},
                            "Cabinets must abut along the wall (no gaps)")
                return {'CANCELLED'}

        # Active becomes anchor. Merge cabinets on each side of active
        # closest-first so the running anchor's geometry stays sane.
        active_idx = roots.index(active_root)
        for i in range(active_idx - 1, -1, -1):
            if not types_face_frame.merge_cabinets(active_root, roots[i], 'LEFT'):
                self.report({'ERROR'}, "Merge failed during pairwise join")
                return {'CANCELLED'}
        for i in range(active_idx + 1, len(roots)):
            if not types_face_frame.merge_cabinets(active_root, roots[i], 'RIGHT'):
                self.report({'ERROR'}, "Merge failed during pairwise join")
                return {'CANCELLED'}

        for o in context.selected_objects:
            o.select_set(False)
        active_root.select_set(True)
        context.view_layer.objects.active = active_root

        self.report({'INFO'}, f"Joined {len(roots)} cabinets")
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Helper: resolve active object to (bay, cabinet_root)
# ---------------------------------------------------------------------------
def _find_active_bay_and_root(context):
    """Walk up from the active object to find the enclosing bay cage
    and cabinet root. Returns (bay, root) or (None, None)."""
    obj = context.active_object
    if obj is None:
        return None, None
    bay = None
    cur = obj
    while cur is not None:
        if bay is None and cur.get(types_face_frame.TAG_BAY_CAGE):
            bay = cur
        if cur.get(types_face_frame.TAG_CABINET_CAGE):
            return bay, cur
        cur = cur.parent
    return None, None


def _bay_count(root):
    return sum(1 for c in root.children
               if c.get(types_face_frame.TAG_BAY_CAGE))


# ---------------------------------------------------------------------------
# Operators: break a cabinet at gaps adjacent to the active bay
# ---------------------------------------------------------------------------
class hb_face_frame_OT_break_cabinet_left(bpy.types.Operator):
    """Break the cabinet at the gap to the left of the active bay.
    The active bay becomes the leftmost bay of the new right-side
    cabinet; its width is locked so it holds through the recalc.
    """
    bl_idname = "hb_face_frame.break_cabinet_left"
    bl_label = "Break Left"
    bl_description = "Split the cabinet at the gap left of the active bay"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        bay, root = _find_active_bay_and_root(context)
        if bay is None or root is None:
            return False
        return bay.face_frame_bay.bay_index > 0

    def execute(self, context):
        bay, root = _find_active_bay_and_root(context)
        if bay is None or root is None:
            self.report({'ERROR'}, "No active bay")
            return {'CANCELLED'}
        bay_index = bay.face_frame_bay.bay_index
        if bay_index <= 0:
            self.report({'WARNING'}, "Active bay is the first bay")
            return {'CANCELLED'}
        bay.face_frame_bay.unlock_width = True
        new_root = types_face_frame.break_cabinet_at_gap(root, bay_index - 1)
        if new_root is None:
            self.report({'ERROR'}, "Break failed")
            return {'CANCELLED'}
        return {'FINISHED'}


class hb_face_frame_OT_break_cabinet_right(bpy.types.Operator):
    """Break the cabinet at the gap to the right of the active bay.
    The active bay stays as the rightmost bay of the (modified)
    original cabinet; its width is locked so it holds through the
    recalc.
    """
    bl_idname = "hb_face_frame.break_cabinet_right"
    bl_label = "Break Right"
    bl_description = "Split the cabinet at the gap right of the active bay"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        bay, root = _find_active_bay_and_root(context)
        if bay is None or root is None:
            return False
        return bay.face_frame_bay.bay_index < _bay_count(root) - 1

    def execute(self, context):
        bay, root = _find_active_bay_and_root(context)
        if bay is None or root is None:
            self.report({'ERROR'}, "No active bay")
            return {'CANCELLED'}
        bay_index = bay.face_frame_bay.bay_index
        if bay_index >= _bay_count(root) - 1:
            self.report({'WARNING'}, "Active bay is the last bay")
            return {'CANCELLED'}
        bay.face_frame_bay.unlock_width = True
        new_root = types_face_frame.break_cabinet_at_gap(root, bay_index)
        if new_root is None:
            self.report({'ERROR'}, "Break failed")
            return {'CANCELLED'}
        return {'FINISHED'}


class hb_face_frame_OT_break_cabinet_both(bpy.types.Operator):
    """Break the cabinet on both sides of the active bay so the
    active bay becomes its own single-bay cabinet. On a first or
    last bay, only the applicable side breaks. The active bay's
    width is locked so it holds through the recalcs.
    """
    bl_idname = "hb_face_frame.break_cabinet_both"
    bl_label = "Break Both"
    bl_description = (
        "Split the cabinet on both sides of the active bay so it "
        "becomes its own single-bay cabinet"
    )
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        bay, root = _find_active_bay_and_root(context)
        if bay is None or root is None:
            return False
        return _bay_count(root) > 1

    def execute(self, context):
        bay, root = _find_active_bay_and_root(context)
        if bay is None or root is None:
            self.report({'ERROR'}, "No active bay")
            return {'CANCELLED'}
        count = _bay_count(root)
        if count <= 1:
            self.report({'WARNING'}, "Cabinet has only one bay")
            return {'CANCELLED'}
        bay_index = bay.face_frame_bay.bay_index
        bay.face_frame_bay.unlock_width = True
        # Break right first so the original keeps the active bay; the
        # subsequent break-left then operates on the modified original.
        if bay_index < count - 1:
            if types_face_frame.break_cabinet_at_gap(root, bay_index) is None:
                self.report({'ERROR'}, "Break (right) failed")
                return {'CANCELLED'}
        if bay_index > 0:
            if types_face_frame.break_cabinet_at_gap(root, bay_index - 1) is None:
                self.report({'ERROR'}, "Break (left) failed")
                return {'CANCELLED'}
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Operator: selection mode toggle (highlights matching objects, dims others)
# ---------------------------------------------------------------------------
class hb_face_frame_OT_toggle_mode(bpy.types.Operator):
    """Apply visibility/highlighting for the current face frame selection mode.

    Mirrors the frameless toggle_mode operator but scoped to face-frame-tagged
    objects. Iterates scene objects (or the children of search_obj_name), and
    for each object decides whether it matches the active mode. Matching
    objects become solid + selectable; non-matching objects get hidden/dimmed.
    """
    bl_idname = "hb_face_frame.toggle_mode"
    bl_label = "Toggle Face Frame Selection Mode"
    bl_description = "Highlight objects matching the current face frame selection mode"

    search_obj_name: bpy.props.StringProperty(name="Search Object Name", default="")  # type: ignore

    # Object-marker tags for cage-level modes
    MODE_TAGS = {
        'Cabinets':  types_face_frame.TAG_CABINET_CAGE,
        'Bays':      types_face_frame.TAG_BAY_CAGE,
        'Openings':  'IS_FACE_FRAME_OPENING_CAGE',     # Phase 3c
        'Interiors': 'IS_FACE_FRAME_INTERIOR_PART',    # Phase 3d
    }

    def _matches_mode(self, obj, mode):
        """Return True if obj should be highlighted in the given mode."""
        if mode == 'Face Frame':
            return obj.get('hb_part_role') in types_face_frame.FACE_FRAME_PART_ROLES
        if mode == 'Parts':
            if not obj.get('CABINET_PART'):
                return False
            # Conditional parts (corner finish kicks, kick returns,
            # slot-1 mid-divs / partition skins, etc.) are persistent
            # children that the recalc layer marks hide_render=True when
            # currently inactive. Skip those so Parts mode doesn't
            # surface them as zero-geometry phantom selections.
            if obj.hide_render:
                return False
            return True
        if mode == 'Cabinets' and obj.get('IS_APPLIANCE'):
            # Appliances live alongside cabinets in the catalog and
            # should highlight together in Cabinets mode.
            return True
        tag = self.MODE_TAGS.get(mode)
        if tag is None:
            return False
        return tag in obj

    def _toggle_one(self, obj, mode):
        """Apply highlight/dim to a single object."""
        # Skip walls, doors, windows, cutting objects - they are not part of
        # the face frame hierarchy and shouldn't be touched by mode toggling.
        if any(t in obj for t in ('IS_WALL_BP', 'IS_ENTRY_DOOR_BP',
                                  'IS_WINDOW_BP', 'IS_CUTTING_OBJ')):
            return
        # Only touch objects that are part of a face frame cabinet,
        # an appliance product, or are generic cabinet parts/cages we
        # know about. Avoids dimming arbitrary scene geometry.
        if (types_face_frame.find_cabinet_root(obj) is None
                and not obj.get('IS_APPLIANCE')):
            return

        if self._matches_mode(obj, mode):
            toggle_cabinet_color(obj, True, type_name=self.MODE_TAGS.get(mode, ''))
        else:
            toggle_cabinet_color(obj, False, type_name=self.MODE_TAGS.get(mode, ''))

    def execute(self, context):
        ff_scene = context.scene.hb_face_frame
        mode = ff_scene.face_frame_selection_mode
        # When the master toggle is off, route every object through the
        # "not highlighted" branch by passing a sentinel mode that no
        # _matches_mode case recognizes - keeps all face frame parts in
        # their default render state and hides the cages.
        # Parts mode also takes the off-path so individual parts render
        # at default color rather than the cabinet-color highlight; the
        # mode value is still readable elsewhere for selection scoping.
        if not ff_scene.face_frame_selection_mode_enabled or mode == 'Parts':
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
# Operator: cabinet prompts popup (right-click -> Cabinet Prompts)
# ---------------------------------------------------------------------------
class hb_face_frame_OT_cabinet_prompts(bpy.types.Operator):
    """Open the cabinet-wide properties dialog.

    Tabbed: General (dimensions), Construction (material / toe kick /
    stretchers), Face Frame (stile / rail / overlay defaults). Only
    cabinet-wide settings here - per-bay editing goes through
    hb_face_frame.bay_prompts; per-mid-stile editing through
    hb_face_frame.mid_stile_prompts.
    """
    bl_idname = "hb_face_frame.cabinet_prompts"
    bl_label = "Cabinet Properties"
    bl_description = "Edit cabinet-wide properties (dimensions, construction, face frame defaults)"
    bl_options = {'UNDO'}

    # Tab state lives on the operator instance so it persists across
    # the dialog's draw calls. Default lands on General each open.
    active_tab: bpy.props.EnumProperty(
        name="Tab",
        items=[
            ('GENERAL',      "General",      "Dimensions"),
            ('CONSTRUCTION', "Construction", "Material, toe kick, stretchers"),
            ('FACE_FRAME',   "Face Frame",   "Frame thickness, stiles, rails, default overlays"),
        ],
        default='GENERAL',
    )  # type: ignore

    @classmethod
    def poll(cls, context):
        return types_face_frame.find_cabinet_root(context.active_object) is not None

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=320)

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        from .. import ui_face_frame
        root = types_face_frame.find_cabinet_root(context.active_object)
        if root is None:
            self.layout.label(text="No face frame cabinet selected", icon='INFO')
            return
        layout = self.layout
        cab_props = root.face_frame_cabinet

        ui_face_frame.draw_identity(layout, root)
        layout.separator()

        # Tab strip - expand=True renders the enum as a row of toggle
        # buttons rather than a dropdown.
        row = layout.row()
        row.prop(self, 'active_tab', expand=True)
        layout.separator()

        if self.active_tab == 'GENERAL':
            ui_face_frame.draw_dimensions(layout, root)
            # Bay section sits under cabinet dimensions on the same tab.
            # Single-bay collapses to a one-line size readout (cabinet
            # dims above are the editor); multi-bay gets a compact box
            # per bay with editable size + an expand toggle for more.
            ui_face_frame.draw_bays_in_prompts(layout, root)
        elif self.active_tab == 'CONSTRUCTION':
            ui_face_frame.draw_construction(layout, cab_props)
        elif self.active_tab == 'FACE_FRAME':
            ui_face_frame.draw_face_frame_defaults(layout, cab_props)


# Maximum count of openings the split dialog can produce in one shot.
# Bounded by the FloatVectorProperty / BoolVectorProperty fixed sizes
# below; raise both if more is needed.
MAX_SPLIT_OPENINGS = 8


class hb_face_frame_OT_split_opening(bpy.types.Operator):
    """Subdivide an opening with N-1 horizontal or vertical splitters,
    producing `count` total openings inside one new split node.

    Inserts a new split-node Empty between the active opening and its
    current parent (bay or another split node). The active opening is
    moved under the split node as the LAST child; (count - 1) fresh
    openings are inserted before it.

    Convention: original is at the highest child index (bottom for
    H-split, right for V-split); new openings fill the lower indices
    (top for H-split, left for V-split). Drawer-on-top-of-door is the
    canonical use case with count = 2.

    Per-opening size + unlock can be set in the dialog: unlocked
    openings hold their typed size during recalc, locked (the default)
    share evenly. The mid rail / mid stile width for THIS split is
    also configurable; it overrides the cabinet-level default for
    this split only.
    """
    bl_idname = "hb_face_frame.split_opening"
    bl_label = "Split Opening"
    bl_options = {'REGISTER', 'UNDO'}

    axis: bpy.props.EnumProperty(
        name="Axis",
        items=[
            ('H', "Horizontal", "Add mid rails; new openings above, original below"),
            ('V', "Vertical",   "Add mid stiles; new openings on the left, original on the right"),
        ],
        default='H',
    )  # type: ignore
    count: bpy.props.IntProperty(
        name="Openings",
        description="Total number of openings the split should produce (including the original)",
        default=2, min=2, max=MAX_SPLIT_OPENINGS,
    )  # type: ignore
    mid_rail_width: bpy.props.FloatProperty(
        name="Mid Rail Width",
        description="Width of mid rails for this split (H-axis only)",
        default=inch(1.5), unit='LENGTH', precision=4,
    )  # type: ignore
    mid_stile_width: bpy.props.FloatProperty(
        name="Mid Stile Width",
        description="Width of mid stiles for this split (V-axis only)",
        default=inch(2.0), unit='LENGTH', precision=4,
    )  # type: ignore
    add_backing: bpy.props.BoolProperty(
        name="Add Backing",
        description="Add a carcass shelf (H-split) or division (V-split) behind each splitter",
        default=True,
    )  # type: ignore
    sizes: bpy.props.FloatVectorProperty(
        name="Sizes",
        description="Per-opening size (used only when the matching unlock flag is on)",
        size=MAX_SPLIT_OPENINGS,
        default=(0.0,) * MAX_SPLIT_OPENINGS,
        unit='LENGTH', precision=4,
    )  # type: ignore
    unlocks: bpy.props.BoolVectorProperty(
        name="Unlocks",
        description="When on, the opening's size is held at the typed value during redistribution",
        size=MAX_SPLIT_OPENINGS,
        default=(False,) * MAX_SPLIT_OPENINGS,
    )  # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj is not None
                and obj.get(types_face_frame.TAG_OPENING_CAGE))

    def invoke(self, context, event):
        # Initialize axis-specific defaults from the cabinet so the
        # dialog opens with sensible starting values rather than the
        # operator's hard-coded class defaults.
        root = types_face_frame.find_cabinet_root(context.active_object)
        if root is not None:
            cab_props = root.face_frame_cabinet
            self.mid_rail_width = cab_props.bay_mid_rail_width
            self.mid_stile_width = cab_props.bay_mid_stile_width
        # Reset per-opening fields so previous invocations don't leak in
        zeros = (0.0,) * MAX_SPLIT_OPENINGS
        falses = (False,) * MAX_SPLIT_OPENINGS
        self.sizes = zeros
        self.unlocks = falses
        return context.window_manager.invoke_props_dialog(self, width=360)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'axis', expand=True)
        layout.prop(self, 'count')
        if self.axis == 'H':
            layout.prop(self, 'mid_rail_width')
            layout.prop(self, 'add_backing', text="Add Shelf Behind Mid Rail")
            first_label, last_label = 'Top', 'Bottom'
        else:
            layout.prop(self, 'mid_stile_width')
            layout.prop(self, 'add_backing', text="Add Division Behind Mid Stile")
            first_label, last_label = 'Left', 'Right'

        layout.separator()
        layout.label(text="Opening Sizes")
        for i in range(self.count):
            if i == 0:
                label = first_label
            elif i == self.count - 1:
                label = last_label
            else:
                label = f"#{i + 1}"
            row = layout.row(align=True)
            field = row.row(align=True)
            field.enabled = self.unlocks[i]
            field.prop(self, 'sizes', index=i, text=label)
            lock_icon = 'UNLOCKED' if self.unlocks[i] else 'LOCKED'
            row.prop(self, 'unlocks', index=i, text="", icon=lock_icon)

    def execute(self, context):
        original = context.active_object
        root = types_face_frame.find_cabinet_root(original)
        if root is None:
            self.report({'WARNING'}, "Active opening is not in a face frame cabinet")
            return {'CANCELLED'}

        old_parent = original.parent
        old_index = original.get('hb_split_child_index', 0)

        # Snapshot original's current size + unlock for handing to the
        # split node (which will now occupy original's slot in the
        # parent tree).
        op_props = original.face_frame_opening
        inherited_size = op_props.size
        inherited_unlock = op_props.unlock_size

        # Create split node empty
        split_obj = bpy.data.objects.new('Split Node', None)
        bpy.context.scene.collection.objects.link(split_obj)
        split_obj.empty_display_type = 'PLAIN_AXES'
        split_obj.empty_display_size = 0.001
        split_obj[types_face_frame.TAG_SPLIT_NODE] = True
        split_obj.parent = old_parent
        split_obj['hb_split_child_index'] = old_index
        sp = split_obj.face_frame_split
        sp.axis = self.axis
        sp.size = inherited_size
        sp.unlock_size = inherited_unlock
        sp.splitter_width = (self.mid_rail_width if self.axis == 'H'
                             else self.mid_stile_width)
        sp.add_backing = self.add_backing

        # Find the bay (for opening_index counter) before re-parenting.
        bay = original
        while bay is not None and not bay.get(types_face_frame.TAG_BAY_CAGE):
            bay = bay.parent
        if bay is not None:
            existing = [c for c in bay.children_recursive
                        if c.get(types_face_frame.TAG_OPENING_CAGE)]
            next_idx = 1 + max(
                (c.face_frame_opening.opening_index for c in existing),
                default=-1,
            )
        else:
            next_idx = 1

        # Create (count - 1) new sibling openings at indices 0 .. count-2.
        # The dialog's per-opening size + unlock arrays cover all `count`
        # children; the original takes the last slot (index count - 1).
        new_count = max(0, self.count - 1)
        new_openings = []
        default_front = types_face_frame.default_front_type_for_root(root)
        for i in range(new_count):
            new_op = types_face_frame.FaceFrameOpening()
            new_op.create('Opening')
            new_op.obj.parent = split_obj
            new_op.obj['hb_split_child_index'] = i
            new_op.obj.face_frame_opening.opening_index = next_idx + i
            new_op.obj.face_frame_opening.size = self.sizes[i]
            new_op.obj.face_frame_opening.unlock_size = self.unlocks[i]
            # New openings inherit the root's default front type. Splits
            # don't copy from the original opening - the original keeps
            # its own front_type, the new siblings get the default.
            new_op.obj.face_frame_opening.front_type = default_front
            new_openings.append(new_op.obj)

        # Re-parent original under split as the last child.
        original.parent = split_obj
        original['hb_split_child_index'] = new_count
        op_props.size = self.sizes[new_count]
        op_props.unlock_size = self.unlocks[new_count]

        types_face_frame.recalculate_face_frame_cabinet(root)

        # Apply current selection mode's visual treatment to the new
        # cages and the split node so they appear correctly highlighted
        # / dimmed instead of stuck on default colors. Scoped to this
        # cabinet via search_obj_name to avoid touching unrelated scene
        # geometry.
        try:
            bpy.ops.hb_face_frame.toggle_mode(search_obj_name=root.name)
        except RuntimeError:
            # toggle_mode poll might fail in unusual contexts; not
            # fatal, the new cages are still functionally valid.
            pass

        self.report({'INFO'},
                    f"Split {original.name} into {self.count} along {self.axis}-axis")
        return {'FINISHED'}


class hb_face_frame_OT_opening_prompts(bpy.types.Operator):
    """Open a focused properties dialog for a single opening.

    Operates on the active object - which must be an opening cage. Shows
    front type, hinge side, and the four per-side overlay rows.
    """
    bl_idname = "hb_face_frame.opening_prompts"
    bl_label = "Opening Properties"
    bl_description = "Edit a single opening's properties"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj is None:
            return False
        return bool(obj.get(types_face_frame.TAG_OPENING_CAGE))

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        from .. import ui_face_frame
        opening_obj = context.active_object
        if opening_obj is None or not opening_obj.get(
                types_face_frame.TAG_OPENING_CAGE):
            self.layout.label(text="No opening selected", icon='INFO')
            return
        ui_face_frame.draw_opening_properties(self.layout, opening_obj)


class hb_face_frame_OT_bay_prompts(bpy.types.Operator):
    """Open a focused properties dialog for a single bay.

    Operates on the active object - which must be a bay cage (i.e., the
    user right-clicked on a bay or has it selected). Shows only that
    bay's properties: width, height, depth, kick height, top offset,
    rail width overrides, remove_bottom, delete_bay.
    """
    bl_idname = "hb_face_frame.bay_prompts"
    bl_label = "Bay Properties"
    bl_description = "Edit a single bay's properties"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj is None:
            return False
        return bool(obj.get(types_face_frame.TAG_BAY_CAGE))

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        from .. import ui_face_frame
        bay_obj = context.active_object
        if bay_obj is None or not bay_obj.get(types_face_frame.TAG_BAY_CAGE):
            self.layout.label(text="No bay selected", icon='INFO')
            return
        ui_face_frame.draw_bay_properties(self.layout, bay_obj)


class hb_face_frame_OT_mid_stile_prompts(bpy.types.Operator):
    """Open a focused properties dialog for a single mid stile.

    Operates on the active object - which must be a mid stile face frame
    part (hb_part_role == PART_ROLE_MID_STILE). Shows just that mid
    stile's width, extend up, and extend down.
    """
    bl_idname = "hb_face_frame.mid_stile_prompts"
    bl_label = "Mid Stile Properties"
    bl_description = "Edit a single mid stile's properties"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj is None:
            return False
        return obj.get('hb_part_role') == types_face_frame.PART_ROLE_MID_STILE

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=260)

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        from .. import ui_face_frame
        obj = context.active_object
        if obj is None or obj.get('hb_part_role') != types_face_frame.PART_ROLE_MID_STILE:
            self.layout.label(text="No mid stile selected", icon='INFO')
            return
        root = types_face_frame.find_cabinet_root(obj)
        if root is None:
            self.layout.label(text="No cabinet root found", icon='ERROR')
            return
        msi = obj.get('hb_mid_stile_index', 0)
        ui_face_frame.draw_mid_stile_properties(self.layout, root, msi)


def _resolve_interior_target(operator, context):
    """Return the active interior target object for an operator,
    honoring an explicit `target_name` set by the inline opening
    popup when present, else falling back to context.active_object.
    Used so buttons rendered inside the opening's modal popup can
    address a specific leaf without changing the active object.
    """
    name = getattr(operator, 'target_name', '') or ''
    if name:
        obj = bpy.data.objects.get(name)
        if obj is not None:
            return obj
    return context.active_object


def _interior_items_target(obj):
    """Return the props object whose `interior_items` collection should
    be edited by add/remove operators when `obj` is active. Returns
    None for objects that don't carry items (cabinet, bay, parts).

    - Opening cage with no tree: opening's flat interior_items.
    - Opening cage with a tree: None (the user must drill into a leaf).
    - Interior region (leaf): the leaf's interior_items.
    """
    if obj.get(types_face_frame.TAG_OPENING_CAGE):
        # When the opening has a tree, items live on leaves and the
        # opening's flat collection is dead. Block direct edits to
        # avoid silent writes the walker would never read.
        has_tree = any(
            c.get(types_face_frame.TAG_INTERIOR_SPLIT_NODE)
            or c.get(types_face_frame.TAG_INTERIOR_REGION)
            for c in obj.children
        )
        if has_tree:
            return None
        return obj.face_frame_opening
    if obj.get(types_face_frame.TAG_INTERIOR_REGION):
        return obj.face_frame_interior_region
    return None


class hb_face_frame_OT_add_interior_item(bpy.types.Operator):
    """Append a new interior item to the active opening's collection.
    Auto-seeds qty fields where applicable; field defaults on
    Face_Frame_Interior_Item supply the rest, and the user edits in
    the panel afterward.

    The half_depth flag is a shortcut: when on, sets the new item's
    kind to ADJUSTABLE_SHELF and bumps shelf_setback to 6" (a half-
    depth shelf is just a deeper-setback adjustable shelf).
    """
    bl_idname = "hb_face_frame.add_interior_item"
    bl_label = "Add Interior Item"
    bl_options = {'UNDO'}

    kind: bpy.props.EnumProperty(
        name="Kind",
        items=props_hb_face_frame.Face_Frame_Interior_Item.INTERIOR_KIND_ITEMS,
        default='ADJUSTABLE_SHELF',
    )  # type: ignore

    half_depth: bpy.props.BoolProperty(
        name="Half Depth",
        description="Create a half-depth adjustable shelf (kind = ADJUSTABLE_SHELF, shelf_setback = 6\")",
        default=False,
    )  # type: ignore

    target_name: bpy.props.StringProperty(
        name="Target Name",
        description="Object name to target instead of active_object "
                    "(used when the panel renders inside a modal popup)",
        default="",
    )  # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj is None:
            return False
        return bool(obj.get(types_face_frame.TAG_OPENING_CAGE)
                    or obj.get(types_face_frame.TAG_INTERIOR_REGION))

    def execute(self, context):
        target = _resolve_interior_target(self, context)
        if target is None:
            self.report({'WARNING'}, "Could not resolve target")
            return {'CANCELLED'}
        target_props = _interior_items_target(target)
        if target_props is None:
            self.report({'WARNING'},
                        "Select an opening or interior region first")
            return {'CANCELLED'}

        item = target_props.interior_items.add()
        if self.half_depth:
            # The half-depth preset is a kind override: regardless of
            # what kind the operator was called with, we land on an
            # adjustable shelf with the deeper setback.
            item.kind = 'ADJUSTABLE_SHELF'
            item.shelf_setback = inch(6.0)
        else:
            item.kind = self.kind

        # Field defaults on the prop class (shelf_qty=1, qty=2, tray_qty=3,
        # vanity_z=11", ...) cover the initial values; the recalc owns
        # any auto-recompute (shelf_qty when unlock_shelf_qty is False).

        target_props.interior_items_index = len(target_props.interior_items) - 1
        # Property writes above already trigger update_cabinet_dim,
        # but call recalc explicitly so the new parts appear even if
        # the update path was suppressed by a re-entrance guard.
        root = types_face_frame.find_cabinet_root(target)
        if root is not None:
            types_face_frame.recalculate_face_frame_cabinet(root)
        return {'FINISHED'}


class hb_face_frame_OT_remove_interior_item(bpy.types.Operator):
    """Remove an interior item from the active opening. Targets the
    item at `index` when set explicitly (per-row remove buttons), or
    falls back to interior_items_index when called without args.
    """
    bl_idname = "hb_face_frame.remove_interior_item"
    bl_label = "Remove Interior Item"
    bl_options = {'UNDO'}

    index: bpy.props.IntProperty(
        name="Index",
        description="Item index to remove (-1 uses the active index)",
        default=-1,
    )  # type: ignore

    target_name: bpy.props.StringProperty(
        name="Target Name",
        description="Object name to target instead of active_object",
        default="",
    )  # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj is None:
            return False
        target_props = _interior_items_target(obj)
        if target_props is None:
            return False
        return len(target_props.interior_items) > 0

    def execute(self, context):
        target = _resolve_interior_target(self, context)
        if target is None:
            return {'CANCELLED'}
        target_props = _interior_items_target(target)
        if target_props is None:
            return {'CANCELLED'}
        idx = (self.index if self.index >= 0
               else target_props.interior_items_index)
        if 0 <= idx < len(target_props.interior_items):
            target_props.interior_items.remove(idx)
            if target_props.interior_items_index >= len(target_props.interior_items):
                target_props.interior_items_index = max(
                    0, len(target_props.interior_items) - 1
                )
        root = types_face_frame.find_cabinet_root(target)
        if root is not None:
            types_face_frame.recalculate_face_frame_cabinet(root)
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Interior split operators
# ---------------------------------------------------------------------------
# Two operators (Add Division, Add Fixed Shelf) plus a shared splitter that
# handles both "first split of a flat opening" (the opening's items migrate
# onto the lower/left child) and "subdivide an existing leaf" (the leaf
# becomes the lower/left child, a fresh empty leaf is the upper/right).
def _read_cage_dims(obj):
    """Return cage_dim_x/y/z dict by reading 'Dim X/Y/Z' inputs off the
    object's geometry node modifier. Used by the split operator to seed
    the new children's sizes from the active target's current rect.
    """
    rect = {'cage_dim_x': 0.0, 'cage_dim_y': 0.0, 'cage_dim_z': 0.0}
    nm = next((m for m in obj.modifiers if m.type == 'NODES'), None)
    if not (nm and nm.node_group):
        return rect
    for sk in nm.node_group.interface.items_tree:
        if sk.in_out != 'INPUT':
            continue
        if sk.name == 'Dim X':
            rect['cage_dim_x'] = nm.get(sk.identifier, 0.0) or 0.0
        elif sk.name == 'Dim Y':
            rect['cage_dim_y'] = nm.get(sk.identifier, 0.0) or 0.0
        elif sk.name == 'Dim Z':
            rect['cage_dim_z'] = nm.get(sk.identifier, 0.0) or 0.0
    return rect


def _copy_interior_items(src, dst):
    """Append every item in src CollectionProperty into dst, copying all
    user-facing fields. Used by the flat -> tree migration on first split
    and (later) by tree collapse.
    """
    for s in src:
        d = dst.add()
        for prop in s.bl_rna.properties:
            if prop.identifier == 'rna_type' or prop.is_readonly:
                continue
            try:
                setattr(d, prop.identifier, getattr(s, prop.identifier))
            except (AttributeError, TypeError):
                # Skip props we can't copy (pointer types, etc.); none
                # of those exist on Face_Frame_Interior_Item today, but
                # the loop is defensive against future additions.
                pass


def _split_active_region(target, axis):
    """Insert a new split node + two child leaves at the position of
    `target`. axis = 'V' (vertical divider) or 'H' (horizontal divider).
    Handles both target=opening (flat -> tree) and target=existing leaf
    (subdivide). All initial size writes are bracketed by the
    _DISTRIBUTING_WIDTHS guard so the auto-lock-on-edit callback
    treats them as system writes (the user just clicked "Add" - they
    didn't type a custom size).
    """
    is_flat_opening = bool(target.get(types_face_frame.TAG_OPENING_CAGE))
    is_leaf = bool(target.get(types_face_frame.TAG_INTERIOR_REGION))
    if not (is_flat_opening or is_leaf):
        return None

    rect = _read_cage_dims(target)
    parent_dim = (rect['cage_dim_x'] if axis == 'V'
                  else rect['cage_dim_z'])
    div_t = inch(0.75)
    half = max(0.0, (parent_dim - div_t) / 2.0)

    root = types_face_frame.find_cabinet_root(target)
    guard_id = id(root) if root is not None else None

    def _seed_size(props, value, unlock):
        """Write size + unlock_size as a system-style seed: bracketed
        by the redistribution guard so the size update callback skips
        the auto-lock (user didn't type this value)."""
        if guard_id is not None:
            types_face_frame._DISTRIBUTING_WIDTHS.add(guard_id)
        try:
            props.size = value
            props.unlock_size = unlock
        finally:
            if guard_id is not None:
                types_face_frame._DISTRIBUTING_WIDTHS.discard(guard_id)

    # Create the split node empty
    split = bpy.data.objects.new('Interior Split', None)
    bpy.context.scene.collection.objects.link(split)
    split.empty_display_type = 'PLAIN_AXES'
    split.empty_display_size = 0.001
    split[types_face_frame.TAG_INTERIOR_SPLIT_NODE] = True
    sp = split.face_frame_interior_split
    sp.axis = axis
    sp.divider_thickness = div_t

    if is_flat_opening:
        opening = target
        split.parent = opening
        split.location = (0.0, 0.0, 0.0)

        # Lower/left child: existing items migrate here. Per the locked
        # design, items move to lower/left on first split.
        leaf_a = types_face_frame.FaceFrameInteriorRegion()
        leaf_a.create('Region 1')
        leaf_a.obj.parent = split
        leaf_a.obj['hb_interior_child_index'] = 0
        _seed_size(leaf_a.obj.face_frame_interior_region, half, False)
        _copy_interior_items(
            opening.face_frame_opening.interior_items,
            leaf_a.obj.face_frame_interior_region.interior_items,
        )
        opening.face_frame_opening.interior_items.clear()

        # Upper/right child: empty leaf
        leaf_b = types_face_frame.FaceFrameInteriorRegion()
        leaf_b.create('Region 2')
        leaf_b.obj.parent = split
        leaf_b.obj['hb_interior_child_index'] = 1
        _seed_size(leaf_b.obj.face_frame_interior_region, half, False)
        return split

    # Subdivide existing leaf: split node takes leaf's slot in parent;
    # leaf becomes child 0; a new empty leaf becomes child 1.
    leaf = target
    leaf_parent = leaf.parent
    leaf_index = leaf.get('hb_interior_child_index', 0)
    rp_existing = leaf.face_frame_interior_region

    # Hand the leaf's current size + unlock to the new split (which now
    # occupies the leaf's slot).
    _seed_size(sp, rp_existing.size, rp_existing.unlock_size)

    split.parent = leaf_parent
    split['hb_interior_child_index'] = leaf_index
    leaf.parent = split
    leaf['hb_interior_child_index'] = 0
    _seed_size(rp_existing, half, False)

    leaf_b = types_face_frame.FaceFrameInteriorRegion()
    leaf_b.create('Region')
    leaf_b.obj.parent = split
    leaf_b.obj['hb_interior_child_index'] = 1
    _seed_size(leaf_b.obj.face_frame_interior_region, half, False)
    return split


class hb_face_frame_OT_add_interior_division(bpy.types.Operator):
    """Add a vertical division to the active opening or interior leaf,
    splitting it into a left and a right region.
    """
    bl_idname = "hb_face_frame.add_interior_division"
    bl_label = "Add Interior Division"
    bl_options = {'UNDO'}

    target_name: bpy.props.StringProperty(
        name="Target Name", default="",
    )  # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj is None:
            return False
        return bool(obj.get(types_face_frame.TAG_OPENING_CAGE)
                    or obj.get(types_face_frame.TAG_INTERIOR_REGION))

    def execute(self, context):
        target = _resolve_interior_target(self, context)
        if target is None:
            return {'CANCELLED'}
        # When the opening already has a tree, the user must pick a leaf
        # to subdivide further. Block here so the operator is unambiguous.
        if (target.get(types_face_frame.TAG_OPENING_CAGE)
                and any(c.get(types_face_frame.TAG_INTERIOR_SPLIT_NODE)
                        or c.get(types_face_frame.TAG_INTERIOR_REGION)
                        for c in target.children)):
            self.report({'WARNING'},
                        "Opening already has interior splits - "
                        "select a region to subdivide")
            return {'CANCELLED'}

        if _split_active_region(target, axis='V') is None:
            self.report({'WARNING'},
                        "Select an opening or interior region first")
            return {'CANCELLED'}

        root = types_face_frame.find_cabinet_root(target)
        if root is not None:
            types_face_frame.recalculate_face_frame_cabinet(root)
        return {'FINISHED'}


class hb_face_frame_OT_add_interior_fixed_shelf(bpy.types.Operator):
    """Add a horizontal fixed shelf to the active opening or interior
    leaf, splitting it into a bottom and a top region.
    """
    bl_idname = "hb_face_frame.add_interior_fixed_shelf"
    bl_label = "Add Interior Fixed Shelf"
    bl_options = {'UNDO'}

    target_name: bpy.props.StringProperty(
        name="Target Name", default="",
    )  # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj is None:
            return False
        return bool(obj.get(types_face_frame.TAG_OPENING_CAGE)
                    or obj.get(types_face_frame.TAG_INTERIOR_REGION))

    def execute(self, context):
        target = _resolve_interior_target(self, context)
        if target is None:
            return {'CANCELLED'}
        if (target.get(types_face_frame.TAG_OPENING_CAGE)
                and any(c.get(types_face_frame.TAG_INTERIOR_SPLIT_NODE)
                        or c.get(types_face_frame.TAG_INTERIOR_REGION)
                        for c in target.children)):
            self.report({'WARNING'},
                        "Opening already has interior splits - "
                        "select a region to subdivide")
            return {'CANCELLED'}

        if _split_active_region(target, axis='H') is None:
            self.report({'WARNING'},
                        "Select an opening or interior region first")
            return {'CANCELLED'}

        root = types_face_frame.find_cabinet_root(target)
        if root is not None:
            types_face_frame.recalculate_face_frame_cabinet(root)
        return {'FINISHED'}


def _collect_subtree_items_into(node, dest_collection):
    """Recursively walk the interior subtree rooted at `node` and copy
    every leaf's interior_items into `dest_collection`. Doesn't modify
    or delete the source tree - the caller handles teardown.
    """
    if node.get(types_face_frame.TAG_INTERIOR_REGION):
        _copy_interior_items(
            node.face_frame_interior_region.interior_items,
            dest_collection,
        )
        return
    if not node.get(types_face_frame.TAG_INTERIOR_SPLIT_NODE):
        return
    children = sorted(
        [c for c in node.children
         if c.get(types_face_frame.TAG_INTERIOR_REGION)
         or c.get(types_face_frame.TAG_INTERIOR_SPLIT_NODE)],
        key=lambda c: c.get('hb_interior_child_index', 0),
    )
    for c in children:
        _collect_subtree_items_into(c, dest_collection)


class hb_face_frame_OT_remove_interior_split(bpy.types.Operator):
    """Remove an interior region's parent split, merging both sides
    of the split (and any nested regions under them) into a single
    flat list of items.

    If the removed split was the opening's tree root, the merged
    items fold back to the opening's flat interior_items collection
    and the opening returns to the no-tree state. Otherwise a new
    merged leaf takes the split's slot in the grandparent.

    target_name selects which leaf identifies the split to remove
    (its parent split). When two children share a parent, removing
    the split via either child gives the same result, so any leaf
    in the affected pair is a valid target.
    """
    bl_idname = "hb_face_frame.remove_interior_split"
    bl_label = "Remove Interior Split"
    bl_options = {'UNDO'}

    target_name: bpy.props.StringProperty(
        name="Target Name",
        description="Region object whose parent split should be removed",
        default="",
    )  # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj is None:
            return False
        # Either the active object is a region (sidebar) or a leaf
        # is named via target_name and the active object is the
        # opening (popup case). Both paths are valid.
        return bool(obj.get(types_face_frame.TAG_INTERIOR_REGION)
                    or obj.get(types_face_frame.TAG_OPENING_CAGE))

    def execute(self, context):
        target = _resolve_interior_target(self, context)
        if target is None or not target.get(
                types_face_frame.TAG_INTERIOR_REGION):
            self.report({'WARNING'},
                        "Select an interior region first")
            return {'CANCELLED'}

        parent_split = target.parent
        if (parent_split is None
                or not parent_split.get(
                    types_face_frame.TAG_INTERIOR_SPLIT_NODE)):
            self.report({'WARNING'},
                        "Region has no parent split to remove")
            return {'CANCELLED'}

        grandparent = parent_split.parent
        is_root_split = (
            grandparent is not None
            and grandparent.get(types_face_frame.TAG_OPENING_CAGE)
        )
        root = types_face_frame.find_cabinet_root(target)
        guard_id = id(root) if root is not None else None

        if is_root_split:
            # Fold back to flat opening: merged items go on the
            # opening's flat collection, entire subtree torn down.
            opening = grandparent
            dest = opening.face_frame_opening.interior_items
            dest.clear()  # flat collection should already be empty
            for c in list(parent_split.children):
                _collect_subtree_items_into(c, dest)
            hb_utils.delete_obj_and_children(parent_split)
        else:
            # Replace split with a merged leaf in the grandparent's
            # slot. The new leaf inherits the split's size + unlock
            # state so sibling redistribution stays balanced.
            split_index = parent_split.get('hb_interior_child_index', 0)
            split_props = parent_split.face_frame_interior_split
            split_size = split_props.size
            split_unlock = split_props.unlock_size

            new_leaf = types_face_frame.FaceFrameInteriorRegion()
            new_leaf.create('Region')
            new_leaf.obj.parent = grandparent
            new_leaf.obj['hb_interior_child_index'] = split_index

            # Seed size + unlock as a system write so the user-edit
            # auto-lock callback skips them.
            if guard_id is not None:
                types_face_frame._DISTRIBUTING_WIDTHS.add(guard_id)
            try:
                rp = new_leaf.obj.face_frame_interior_region
                rp.size = split_size
                rp.unlock_size = split_unlock
            finally:
                if guard_id is not None:
                    types_face_frame._DISTRIBUTING_WIDTHS.discard(guard_id)

            # Gather subtree items into the new leaf, then tear down
            # the old subtree (children get hauled in by the recursive
            # delete helper).
            dest = new_leaf.obj.face_frame_interior_region.interior_items
            for c in list(parent_split.children):
                _collect_subtree_items_into(c, dest)
            hb_utils.delete_obj_and_children(parent_split)

        if root is not None:
            types_face_frame.recalculate_face_frame_cabinet(root)
        return {'FINISHED'}


class hb_face_frame_OT_show_interior_add_menu(bpy.types.Operator):
    """Pop a menu of every interior add option (subdivisions and item
    kinds) for one target. Replaces the older multi-row button grid.

    The target_name property is captured into a closure-based draw
    function so each menu item stamps the right target on its
    operator regardless of which leaf was clicked. Lets one Add
    button serve every leaf in the inline tree view without each
    leaf needing its own row of buttons.
    """
    bl_idname = "hb_face_frame.show_interior_add_menu"
    bl_label = "Add Interior..."
    bl_options = {'UNDO'}

    target_name: bpy.props.StringProperty(
        name="Target Name", default="",
    )  # type: ignore

    def execute(self, context):
        target_name = self.target_name

        def draw_fn(menu_self, _ctx):
            layout = menu_self.layout

            # Subdivisions
            op = layout.operator(
                "hb_face_frame.add_interior_division",
                text="Division", icon='MOD_ARRAY',
            )
            op.target_name = target_name
            op = layout.operator(
                "hb_face_frame.add_interior_fixed_shelf",
                text="Fixed Shelf", icon='SNAP_FACE',
            )
            op.target_name = target_name

            layout.separator()

            # Shelves
            op = layout.operator(
                "hb_face_frame.add_interior_item", text="Adjustable Shelf",
            )
            op.kind = 'ADJUSTABLE_SHELF'
            op.half_depth = False
            op.target_name = target_name

            op = layout.operator(
                "hb_face_frame.add_interior_item", text="Glass Shelf",
            )
            op.kind = 'GLASS_SHELF'
            op.half_depth = False
            op.target_name = target_name

            op = layout.operator(
                "hb_face_frame.add_interior_item", text="Half-Depth Shelf",
            )
            op.kind = 'ADJUSTABLE_SHELF'
            op.half_depth = True
            op.target_name = target_name

            layout.separator()

            # Pullouts / rollouts / tray dividers
            op = layout.operator(
                "hb_face_frame.add_interior_item", text="Pullout",
            )
            op.kind = 'PULLOUT_SHELF'
            op.half_depth = False
            op.target_name = target_name

            op = layout.operator(
                "hb_face_frame.add_interior_item", text="Rollout",
            )
            op.kind = 'ROLLOUT'
            op.half_depth = False
            op.target_name = target_name

            op = layout.operator(
                "hb_face_frame.add_interior_item", text="Tray Dividers",
            )
            op.kind = 'TRAY_DIVIDERS'
            op.half_depth = False
            op.target_name = target_name

            layout.separator()

            # Vanity / accessory
            op = layout.operator(
                "hb_face_frame.add_interior_item", text="Vanity Shelves",
            )
            op.kind = 'VANITY_SHELVES'
            op.half_depth = False
            op.target_name = target_name

            op = layout.operator(
                "hb_face_frame.add_interior_item", text="Accessory",
            )
            op.kind = 'ACCESSORY'
            op.half_depth = False
            op.target_name = target_name

        context.window_manager.popup_menu(
            draw_fn, title="Add Interior", icon='ADD',
        )
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Bay rebuild helpers (used by change_bay)
# ---------------------------------------------------------------------------
def _wipe_bay_children(bay_obj):
    """Delete every descendant of bay_obj. The bay cage itself and its
    parent (the cabinet root) are untouched. Cabinet-level face frame
    parts (left/right stiles, top/bottom rails) are children of the
    cabinet root, not the bay, so they're safe.
    """
    import bpy
    descendants = list(bay_obj.children_recursive)
    # Reverse so deeper objects unparent before their ancestors.
    for child in reversed(descendants):
        if child.name in bpy.data.objects:
            bpy.data.objects.remove(child, do_unlink=True)


def _build_recipe_into(recipe, parent_obj, child_index,
                       opening_idx_counter, cab_props):
    """Materialize a bay_presets recipe tree as objects under parent_obj.

    Leaf -> creates one Opening cage and applies its opening preset.
    Split -> creates a Split Node empty with the right axis and splitter
             width, then recurses into each child.

    opening_idx_counter is a single-element mutable list used as a
    shared counter across recursive calls so opening_index values are
    unique within the bay.
    """
    import bpy
    kind = recipe[0]
    # size_role lives in slot 3 for both leaf and split tuples (added
    # for top-drawer pinning in BASE drawer presets). Older 3-tuples
    # default to None so callers that haven't been updated still work.
    size_role = recipe[3] if len(recipe) > 3 else None

    def apply_size_role(props):
        """Pin a node's size + unlock_size based on its size_role.
        New roles get added here; the cabinet-level value they map to
        lives on Face_Frame_Cabinet_Props.

        Order matters: unlock_size MUST be written before size. Each
        prop write fires a recalc, and a recalc with this node still
        marked unlocked will redistribute and overwrite size with the
        node's share of the available space. Writing unlock_size first
        means the recalc triggered by the size write sees a locked
        node and leaves the value alone.
        """
        if size_role == 'TOP_DRAWER':
            # Scene-level preference, not per-cabinet.
            props.unlock_size = True
            props.size = bpy.context.scene.hb_face_frame.top_drawer_opening_height
        elif size_role == 'TALL_SPLIT_BOTTOM':
            # Scene-level preference, not per-cabinet.
            props.unlock_size = True
            props.size = bpy.context.scene.hb_face_frame.tall_cabinet_split_height
        elif size_role == 'UPPER_STACKED_TOP':
            # Scene-level preference, not per-cabinet.
            props.unlock_size = True
            props.size = bpy.context.scene.hb_face_frame.upper_top_stacked_cabinet_height
        elif size_role == 'REFRIGERATOR':
            # Pins the bottom appliance opening of a refrigerator
            # cabinet to the scene's refrigerator_height so the
            # door zone above flexes with the cabinet height.
            props.unlock_size = True
            props.size = bpy.context.scene.hb_face_frame.refrigerator_height

    if kind == 'leaf':
        config = recipe[1]
        overrides = recipe[2] if len(recipe) > 2 else {}
        opening = types_face_frame.FaceFrameOpening()
        opening.create('Opening')
        opening.obj.parent = parent_obj
        opening.obj['hb_split_child_index'] = child_index
        opening.obj.face_frame_opening.opening_index = opening_idx_counter[0]
        opening_idx_counter[0] += 1
        apply_opening_preset(opening.obj, config, **overrides)
        apply_size_role(opening.obj.face_frame_opening)
        return

    if kind == 'split':
        axis = recipe[1]
        children = recipe[2]
        split_obj = bpy.data.objects.new('Split Node', None)
        bpy.context.scene.collection.objects.link(split_obj)
        split_obj.empty_display_type = 'PLAIN_AXES'
        split_obj.empty_display_size = 0.001
        split_obj[types_face_frame.TAG_SPLIT_NODE] = True
        split_obj.parent = parent_obj
        split_obj['hb_split_child_index'] = child_index
        sp = split_obj.face_frame_split
        sp.axis = axis
        sp.splitter_width = (cab_props.bay_mid_rail_width if axis == 'H'
                             else cab_props.bay_mid_stile_width)
        apply_size_role(sp)
        for i, child_recipe in enumerate(children):
            _build_recipe_into(child_recipe, split_obj, i,
                               opening_idx_counter, cab_props)
        return

    raise ValueError(f"Unknown recipe node kind: {kind!r}")


# ---------------------------------------------------------------------------
# Operator: change opening configuration (right-click quick presets)
# ---------------------------------------------------------------------------
# Each preset is a dict of actions the operator runs on the active
# opening. Recognized keys:
#   'front_type'      - required, written to op_props.front_type
#   'hinge_side'      - optional, written when present
#   'shelves'         - 'CLEAR' to remove ADJUSTABLE_SHELF items, or
#                       'ENSURE' to add one if missing. Omitted means
#                       leave shelves alone (the front_type callback
#                       still auto-adds for DOOR).
#   'appliance_label' - True to ensure an ACCESSORY item with label
#                       'Appliance' is present
_OPENING_PRESETS = {
    'OPEN':              {'front_type': 'NONE',         'shelves': 'CLEAR'},
    'OPEN_WITH_SHELVES': {'front_type': 'NONE',         'shelves': 'ENSURE'},
    'LEFT_DOOR':         {'front_type': 'DOOR',         'hinge_side': 'LEFT'},
    'RIGHT_DOOR':        {'front_type': 'DOOR',         'hinge_side': 'RIGHT'},
    'DOUBLE_DOOR':       {'front_type': 'DOOR',         'hinge_side': 'DOUBLE'},
    'FLIP_UP_DOOR':      {'front_type': 'DOOR',         'hinge_side': 'TOP'},
    'FLIP_DOWN_DOOR':    {'front_type': 'DOOR',         'hinge_side': 'BOTTOM'},
    'DRAWER':            {'front_type': 'DRAWER_FRONT'},
    'PULLOUT':           {'front_type': 'PULLOUT'},
    'INSET_PANEL':       {'front_type': 'INSET_PANEL', 'shelves': 'CLEAR'},
    'FALSE_FRONT':       {'front_type': 'FALSE_FRONT'},
    # APPLIANCE: open opening with no shelves and an 'Appliance' label.
    # Reuses the ACCESSORY interior kind for the label until a dedicated
    # APPLIANCE front_type or interior kind lands.
    'APPLIANCE':         {'front_type': 'NONE',
                          'shelves': 'CLEAR',
                          'appliance_label': True},
}


def apply_opening_preset(opening_obj, config, **overrides):
    """Programmatic version of hb_face_frame.change_opening - applies the
    named preset's prop changes to a specific opening object without
    going through bpy.ops. The caller is responsible for triggering a
    recalc when it's done batching changes.

    Recognized overrides:
      accessory_label  - replaces the label on the (typically just-added)
                         ACCESSORY interior item. Used by the bay
                         presets to set 'Microwave' instead of the
                         default 'Appliance' on appliance labels.
    """
    preset = _OPENING_PRESETS[config]
    op_props = opening_obj.face_frame_opening

    # Mutate interior_items first so the recalc kicked off by the
    # front_type write below sees the final state in one pass.
    shelves = preset.get('shelves')
    if shelves == 'CLEAR':
        for i in range(len(op_props.interior_items) - 1, -1, -1):
            if op_props.interior_items[i].kind == 'ADJUSTABLE_SHELF':
                op_props.interior_items.remove(i)
    elif shelves == 'ENSURE':
        has_shelves = any(
            item.kind == 'ADJUSTABLE_SHELF'
            for item in op_props.interior_items
        )
        if not has_shelves:
            op_props.interior_items.add()

    if preset.get('appliance_label'):
        has_accessory = any(
            item.kind == 'ACCESSORY' for item in op_props.interior_items
        )
        if not has_accessory:
            new_item = op_props.interior_items.add()
            new_item.kind = 'ACCESSORY'
            new_item.accessory_label = "Appliance"

    op_props.front_type = preset['front_type']
    if 'hinge_side' in preset:
        op_props.hinge_side = preset['hinge_side']

    # Apply post-preset overrides. accessory_label targets the most
    # recent ACCESSORY item - for fresh openings the preset just added
    # one; for re-applied presets we deliberately retarget the existing
    # item so the user's named appliance reflects the new preset.
    accessory_label = overrides.get('accessory_label')
    if accessory_label is not None:
        for item in reversed(op_props.interior_items):
            if item.kind == 'ACCESSORY':
                item.accessory_label = accessory_label
                break


class hb_face_frame_OT_change_opening(bpy.types.Operator):
    """Apply a named opening preset to the active opening cage.

    Drives front_type, hinge_side, and the ADJUSTABLE_SHELF interior
    item in one click. Used by the right-click 'Change Opening' submenu.
    Lets the user reach the common configurations without opening the
    full opening properties dialog.
    """
    bl_idname = "hb_face_frame.change_opening"
    bl_label = "Change Opening"
    bl_options = {'UNDO'}

    config: bpy.props.EnumProperty(
        name="Configuration",
        items=[
            ('OPEN',              "Open",              "Open opening with no interior items"),
            ('OPEN_WITH_SHELVES', "Open with Shelves", "Open opening with adjustable shelves"),
            ('LEFT_DOOR',         "Left Door",         "Single door hinged on the left"),
            ('RIGHT_DOOR',        "Right Door",        "Single door hinged on the right"),
            ('DOUBLE_DOOR',       "Double Door",       "Pair of doors meeting in the middle"),
            ('FLIP_UP_DOOR',      "Flip Up Door",      "Door hinged on the top edge"),
            ('FLIP_DOWN_DOOR',    "Flip Down Door",    "Door hinged on the bottom edge"),
            ('DRAWER',            "Drawer",            "Drawer front"),
            ('PULLOUT',           "Pullout",           "Door front on a pullout slide"),
            ('INSET_PANEL',       "Inset Panel",       "Recessed 1/4\" panel filling the opening"),
            ('FALSE_FRONT',       "False Front",       "Decorative drawer-style panel; fixed"),
            ('APPLIANCE',         "Appliance",         "Opening reserved for an appliance"),
        ],
        default='OPEN',
    )  # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and bool(obj.get(types_face_frame.TAG_OPENING_CAGE))

    def execute(self, context):
        opening_obj = context.active_object
        if not opening_obj or not opening_obj.get(types_face_frame.TAG_OPENING_CAGE):
            self.report({'WARNING'}, "Select an opening first")
            return {'CANCELLED'}

        apply_opening_preset(opening_obj, self.config)

        # Belt-and-suspenders: collection mutations don't fire callbacks,
        # so a CLEAR with the same front_type as before would otherwise
        # leave stale shelf objects around. An explicit recalc closes
        # the gap.
        root = types_face_frame.find_cabinet_root(opening_obj)
        if root is not None:
            types_face_frame.recalculate_face_frame_cabinet(root)
        return {'FINISHED'}


def apply_bay_preset(bay_obj, config):
    """Wipe `bay_obj`'s contents and rebuild from a bay preset.
    Programmatic equivalent of hb_face_frame.change_bay's execute body,
    minus the user-feedback bits (active object, report, selection
    mode toggle). The caller is responsible for triggering selection
    refresh if needed; the recalc itself runs here.

    Returns True on success, False if the bay's cabinet type has no
    presets or `config` isn't recognized for that type.
    """
    if not bay_obj.get(types_face_frame.TAG_BAY_CAGE):
        return False
    root = types_face_frame.find_cabinet_root(bay_obj)
    if root is None:
        return False
    cabinet_type = root.face_frame_cabinet.cabinet_type
    presets = bay_presets.PRESETS.get(cabinet_type)
    if not presets or config not in presets:
        return False

    # Wipe + rebuild fires update callbacks on every front_type / overlay /
    # hinge write, and each one triggers a full cabinet recalc. Suspend so
    # the explicit final recalc below is the only one that actually runs.
    with types_face_frame.suspend_recalc():
        _wipe_bay_children(bay_obj)
        opening_idx = [0]
        _build_recipe_into(
            presets[config], bay_obj, 0, opening_idx, root.face_frame_cabinet,
        )
        types_face_frame.recalculate_face_frame_cabinet(root)
    return True


# ---------------------------------------------------------------------------
# Operator: change bay configuration (right-click quick presets per
# cabinet type). Wipes the bay's existing tree and rebuilds it from a
# preset recipe in bay_presets.PRESETS.
# ---------------------------------------------------------------------------
class hb_face_frame_OT_change_bay(bpy.types.Operator):
    """Apply a named bay configuration preset to the active bay cage.

    The preset's available configurations differ by cabinet type. The
    operator looks up bay_presets.PRESETS[cabinet_type][config] and
    materializes its tree of split nodes and openings under the bay,
    replacing whatever was there.

    The two CUSTOM_* configs are special: they reset the bay to a
    single opening and route to the existing split_opening dialog so
    the user picks count and per-opening sizes.
    """
    bl_idname = "hb_face_frame.change_bay"
    bl_label = "Change Bay"
    bl_options = {'UNDO'}

    config: bpy.props.StringProperty(
        name="Configuration",
        description="Bay preset id from bay_presets (or CUSTOM_VERTICAL / CUSTOM_HORIZONTAL)",
    )  # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and bool(obj.get(types_face_frame.TAG_BAY_CAGE))

    def execute(self, context):
        bay_obj = context.active_object
        if not bay_obj or not bay_obj.get(types_face_frame.TAG_BAY_CAGE):
            self.report({'WARNING'}, "Select a bay first")
            return {'CANCELLED'}
        root = types_face_frame.find_cabinet_root(bay_obj)
        if root is None:
            self.report({'WARNING'}, "Bay is not part of a cabinet")
            return {'CANCELLED'}
        cabinet_type = root.face_frame_cabinet.cabinet_type
        if cabinet_type not in bay_presets.PRESETS:
            self.report({'WARNING'}, f"No bay presets for cabinet type {cabinet_type}")
            return {'CANCELLED'}

        # Custom routes: wipe to one opening, then hand off to the
        # split dialog.
        if self.config in ('CUSTOM_VERTICAL', 'CUSTOM_HORIZONTAL'):
            _wipe_bay_children(bay_obj)
            opening_idx = [0]
            _build_recipe_into(
                bay_presets.L('OPEN'), bay_obj, 0,
                opening_idx, root.face_frame_cabinet,
            )
            types_face_frame.recalculate_face_frame_cabinet(root)
            new_opening = next(
                (c for c in bay_obj.children
                 if c.get(types_face_frame.TAG_OPENING_CAGE)), None
            )
            if new_opening is None:
                return {'FINISHED'}
            bpy.ops.object.select_all(action='DESELECT')
            new_opening.select_set(True)
            context.view_layer.objects.active = new_opening
            axis = 'V' if self.config == 'CUSTOM_VERTICAL' else 'H'
            return bpy.ops.hb_face_frame.split_opening('INVOKE_DEFAULT', axis=axis)

        if not apply_bay_preset(bay_obj, self.config):
            self.report({'WARNING'},
                        f"Unknown bay config {self.config!r} for {cabinet_type}")
            return {'CANCELLED'}

        # Re-apply selection mode so the new objects render correctly
        # instead of staying in their default colors.
        try:
            bpy.ops.hb_face_frame.toggle_mode(search_obj_name=root.name)
        except RuntimeError:
            pass
        return {'FINISHED'}


class hb_face_frame_OT_insert_bay(bpy.types.Operator):
    """Insert a new bay before or after the bay at bay_index. The new
    bay starts width=0 + unlock_width=False so the recalc redistributor
    immediately gives it an equal share of unlocked space; height and
    depth follow the cabinet's defaults."""
    bl_idname = "hb_face_frame.insert_bay"
    bl_label = "Insert Bay"
    bl_description = "Insert a new bay before or after the chosen bay"
    bl_options = {'REGISTER', 'UNDO'}

    bay_index: bpy.props.IntProperty(
        name="Bay Index",
        description="Index of the existing bay this insert is anchored to",
        default=0, min=0,
    )  # type: ignore
    direction: bpy.props.EnumProperty(
        name="Direction",
        items=[
            ('BEFORE', "Before", "Insert to the left of the anchor bay"),
            ('AFTER',  "After",  "Insert to the right of the anchor bay"),
        ],
        default='AFTER',
    )  # type: ignore

    @classmethod
    def poll(cls, context):
        return types_face_frame.find_cabinet_root(context.active_object) is not None

    def execute(self, context):
        root = types_face_frame.find_cabinet_root(context.active_object)
        if root is None:
            self.report({'ERROR'}, "No face frame cabinet selected")
            return {'CANCELLED'}
        cab = types_face_frame._wrap_cabinet(root)
        cab.insert_bay(self.bay_index, self.direction)

        # Reapply the cabinet's current selection mode so the new bay's
        # cage / opening / parts inherit the right visual treatment
        # instead of staying on default colors. Scoped via
        # search_obj_name. Same pattern split_opening uses.
        try:
            bpy.ops.hb_face_frame.toggle_mode(search_obj_name=root.name)
        except RuntimeError:
            pass
        return {'FINISHED'}


class hb_face_frame_OT_delete_bay(bpy.types.Operator):
    """Delete the bay at bay_index. Refuses if the cabinet would be
    left with zero bays. Removes the bay's full subtree (openings,
    fronts, pulls, interior items) and one mid-stile + mid-div pair."""
    bl_idname = "hb_face_frame.delete_bay"
    bl_label = "Delete Bay"
    bl_description = "Delete a bay and its mid stile / mid division"
    bl_options = {'REGISTER', 'UNDO'}

    bay_index: bpy.props.IntProperty(
        name="Bay Index",
        description="Index of the bay to remove",
        default=0, min=0,
    )  # type: ignore

    @classmethod
    def poll(cls, context):
        return types_face_frame.find_cabinet_root(context.active_object) is not None

    def execute(self, context):
        root = types_face_frame.find_cabinet_root(context.active_object)
        if root is None:
            self.report({'ERROR'}, "No face frame cabinet selected")
            return {'CANCELLED'}
        cab = types_face_frame._wrap_cabinet(root)
        ok = cab.delete_bay(self.bay_index)
        if not ok:
            self.report({'ERROR'}, "Cannot delete the only remaining bay")
            return {'CANCELLED'}
        return {'FINISHED'}


class hb_face_frame_OT_set_equal_door_width(bpy.types.Operator):
    """Equalize visible door widths across the cabinets containing
    every selected bay. Selection picks the cabinets; every bay in
    those cabinets contributes to the calculation. Each cabinet's
    own width floats to the new bay total + stiles so the cross-
    cabinet target can actually be honored.

    Bay door count rule: a bay contributes 2 doors and one
    DOUBLE_DOOR_REVEAL gap if any opening reached from the bay tree
    root via H-splits only is a DOOR with hinge_side='DOUBLE'.
    Otherwise the bay is treated as 1 door of width = bay width
    regardless of front_type. V-split nodes shrink children's
    widths so they short-circuit the descent."""
    bl_idname = "hb_face_frame.set_equal_door_width"
    bl_label = "Set Equal Door Width"
    bl_description = (
        "Make all door widths equal across the cabinets containing the "
        "selected bay(s). Every bay in those cabinets is recalculated"
    )
    bl_options = {'REGISTER', 'UNDO'}

    # 0.125" double-door reveal between leaves. Mirrors
    # solver_face_frame.DOUBLE_DOOR_REVEAL; not imported to keep this
    # operator's deps the same as its neighbors.
    _DOUBLE_DOOR_REVEAL = inch(0.125)

    @classmethod
    def poll(cls, context):
        for obj in context.selected_objects:
            if obj.get(types_face_frame.TAG_BAY_CAGE):
                return True
        ao = context.active_object
        return ao is not None and bool(ao.get(types_face_frame.TAG_BAY_CAGE))

    @staticmethod
    def _bay_has_full_width_double_door(bay_obj):
        TAG_OP = types_face_frame.TAG_OPENING_CAGE
        TAG_SP = types_face_frame.TAG_SPLIT_NODE
        roots = [c for c in bay_obj.children
                 if c.get(TAG_OP) or c.get(TAG_SP)]
        if not roots:
            return False

        def walk(node):
            if node.get(TAG_OP):
                op = node.face_frame_opening
                return (op.front_type == 'DOOR'
                        and op.hinge_side == 'DOUBLE')
            if node.get(TAG_SP):
                # Only H-splits keep children at the bay's full width.
                if node.face_frame_split.axis != 'H':
                    return False
                for c in node.children:
                    if c.get(TAG_OP) or c.get(TAG_SP):
                        if walk(c):
                            return True
            return False

        return walk(roots[0])

    def execute(self, context):
        # Collect cabinet roots from any selected bay (and the active
        # object - right-click usually activates without selecting).
        candidates = list(context.selected_objects)
        if (context.active_object is not None
                and context.active_object not in candidates):
            candidates.append(context.active_object)
        roots = []
        seen = set()
        for obj in candidates:
            if not obj.get(types_face_frame.TAG_BAY_CAGE):
                continue
            root = types_face_frame.find_cabinet_root(obj)
            if root is not None and root.name not in seen:
                roots.append(root)
                seen.add(root.name)
        if not roots:
            self.report({'WARNING'}, "Select at least one face frame bay")
            return {'CANCELLED'}

        # Per-bay info: (bay_obj, root, is_double_door_bay).
        all_bays = []
        for root in roots:
            bays = sorted(
                [c for c in root.children
                 if c.get(types_face_frame.TAG_BAY_CAGE)],
                key=lambda c: c.get('hb_bay_index', 0),
            )
            for bay in bays:
                all_bays.append((bay, root,
                                 self._bay_has_full_width_double_door(bay)))

        # Pool budget. Each bay's overlay comes from its own cabinet
        # so cabinets with different ff_door_overlay still balance.
        DD_GAP = self._DOUBLE_DOOR_REVEAL
        total_bay_widths = sum(b.face_frame_bay.width for b, _, _ in all_bays)
        # Each bay's overlay budget is (left + right) at the cabinet
        # default. Per-opening overlay overrides are not consulted in
        # v1 - same simplification a single-overlay model would make.
        total_overlay_pad = sum(
            (r.face_frame_cabinet.default_left_overlay
             + r.face_frame_cabinet.default_right_overlay)
            for _, r, _ in all_bays
        )
        num_double_bays = sum(1 for _, _, dd in all_bays if dd)
        num_doors = sum(2 if dd else 1 for _, _, dd in all_bays)
        if num_doors == 0:
            self.report({'WARNING'}, "No doors to equalize")
            return {'CANCELLED'}

        total_visible = (total_bay_widths
                         + total_overlay_pad
                         - num_double_bays * DD_GAP)
        target_door_width = total_visible / num_doors

        # Write new bay widths under one suspended recalc, then resync
        # each cabinet's overall width to the new bay total + stiles.
        # Cabinets float so the cross-cabinet target is honored.
        with types_face_frame.suspend_recalc():
            for bay, root, is_double in all_bays:
                cp = root.face_frame_cabinet
                lr_pad = cp.default_left_overlay + cp.default_right_overlay
                if is_double:
                    new_w = 2.0 * target_door_width - lr_pad + DD_GAP
                else:
                    new_w = target_door_width - lr_pad
                bp = bay.face_frame_bay
                bp.unlock_width = True
                bp.width = new_w

            for root in roots:
                cp = root.face_frame_cabinet
                bays = [c for c in root.children
                        if c.get(types_face_frame.TAG_BAY_CAGE)]
                stile_total = (cp.left_stile_width
                               + cp.right_stile_width)
                for i in range(min(len(bays) - 1,
                                   len(cp.mid_stile_widths))):
                    stile_total += cp.mid_stile_widths[i].width
                bay_total = sum(b.face_frame_bay.width for b in bays)
                cp.width = stile_total + bay_total

        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Operator: group selected face frame cabinets into a saveable cage group
# ---------------------------------------------------------------------------
class hb_face_frame_OT_create_cabinet_group(bpy.types.Operator):
    """Group selected face frame cabinets under a single cage that can be
    saved to the user library.

    The group cage is a generic GeoNodeCage with IS_CAGE_GROUP - the same
    marker frameless uses, so save/load is shared via a common library
    folder.
    """
    bl_idname = "hb_face_frame.create_cabinet_group"
    bl_label = "Create Cabinet Group"
    bl_description = "Group the selected face frame cabinets into a single cabinet group"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Walk each selected object up to its face frame cabinet root.
        # Letting users select any part (door, opening cage, etc.) means
        # they don't have to hunt for the root before grouping.
        roots = []
        seen = set()
        for obj in context.selected_objects:
            root = types_face_frame.find_cabinet_root(obj)
            if root is not None and root.name not in seen:
                seen.add(root.name)
                roots.append(root)

        if not roots:
            self.report({'WARNING'}, "No face frame cabinets selected")
            return {'CANCELLED'}

        loc, rot, w, d, h = self._calculate_group_bounds(roots)

        group = hb_types.GeoNodeCage()
        group.create("New Cabinet Group")
        group.obj['IS_CAGE_GROUP'] = True
        group.obj.parent = None
        group.obj.location = loc
        group.obj.rotation_euler = rot
        group.set_input('Dim X', w)
        group.set_input('Dim Y', d)
        group.set_input('Dim Z', h)
        # Mirror Y so the group cage matches face frame's cabinet
        # convention: origin at back, geometry extending -Y into the room.
        group.set_input('Mirror Y', True)

        bpy.ops.object.select_all(action='DESELECT')

        # Reparent preserving world transforms - the user placed these
        # cabinets where they wanted them and the group shouldn't shift
        # them at creation time.
        for root in roots:
            world_matrix = root.matrix_world.copy()
            root.parent = group.obj
            root.matrix_world = world_matrix

        group.obj.select_set(True)
        context.view_layer.objects.active = group.obj
        return {'FINISHED'}

    def _calculate_group_bounds(self, roots):
        """World-space AABB across all roots, returned as the back-left-bottom
        corner for a Mirror-Y cage (origin at back, +Y is back, geometry
        extends -Y into the room).
        """
        if not roots:
            return (Vector((0, 0, 0)), (0, 0, 0), 0, 0, 0)

        min_x = float('inf'); max_x = float('-inf')
        min_y = float('inf'); max_y = float('-inf')
        min_z = float('inf'); max_z = float('-inf')

        for root in roots:
            cab_props = root.face_frame_cabinet
            cw = cab_props.width
            cd = cab_props.depth
            ch = cab_props.height

            # Cabinet local frame: origin at back, depth in -Y (Mirror Y).
            local_corners = [
                Vector((0,   0, 0)),
                Vector((cw,  0, 0)),
                Vector((0,  -cd, 0)),
                Vector((cw, -cd, 0)),
                Vector((0,   0, ch)),
                Vector((cw,  0, ch)),
                Vector((0,  -cd, ch)),
                Vector((cw, -cd, ch)),
            ]

            mw = root.matrix_world
            for lc in local_corners:
                wc = mw @ lc
                min_x = min(min_x, wc.x); max_x = max(max_x, wc.x)
                min_y = min(min_y, wc.y); max_y = max(max_y, wc.y)
                min_z = min(min_z, wc.z); max_z = max(max_z, wc.z)

        overall_w = max_x - min_x
        overall_d = max_y - min_y
        overall_h = max_z - min_z

        # The group cage uses Mirror Y, so its origin sits at +Y (back of
        # the world AABB) and its geometry extends -Y from there.
        location = Vector((min_x, max_y, min_z))
        rotation = (0, 0, 0)

        return (location, rotation, overall_w, overall_d, overall_h)


classes = (
    hb_face_frame_OT_draw_cabinet,
    hb_face_frame_OT_create_cabinet_group,
    hb_face_frame_OT_delete_cabinet,
    hb_face_frame_OT_join_cabinets,
    hb_face_frame_OT_break_cabinet_left,
    hb_face_frame_OT_break_cabinet_right,
    hb_face_frame_OT_break_cabinet_both,
    hb_face_frame_OT_toggle_mode,
    hb_face_frame_OT_cabinet_prompts,
    hb_face_frame_OT_bay_prompts,
    hb_face_frame_OT_opening_prompts,
    hb_face_frame_OT_split_opening,
    hb_face_frame_OT_mid_stile_prompts,
    hb_face_frame_OT_add_interior_item,
    hb_face_frame_OT_remove_interior_item,
    hb_face_frame_OT_add_interior_division,
    hb_face_frame_OT_add_interior_fixed_shelf,
    hb_face_frame_OT_remove_interior_split,
    hb_face_frame_OT_show_interior_add_menu,
    hb_face_frame_OT_change_opening,
    hb_face_frame_OT_change_bay,
    hb_face_frame_OT_insert_bay,
    hb_face_frame_OT_delete_bay,
    hb_face_frame_OT_set_equal_door_width,
)


register, unregister = bpy.utils.register_classes_factory(classes)
