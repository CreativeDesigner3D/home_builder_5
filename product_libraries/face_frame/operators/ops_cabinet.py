import bpy

from .. import types_face_frame
from ....units import inch
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
        bpy.ops.hb_face_frame.place_cabinet(
            'INVOKE_DEFAULT',
            cabinet_name=self.cabinet_name,
            bay_qty=self.bay_qty,
        )
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Operator: force a recalc on the active cabinet
# ---------------------------------------------------------------------------
class hb_face_frame_OT_recalculate_cabinet(bpy.types.Operator):
    """Force-recalculate the active face frame cabinet."""
    bl_idname = "hb_face_frame.recalculate_cabinet"
    bl_label = "Recalculate Face Frame Cabinet"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return types_face_frame.find_cabinet_root(context.active_object) is not None

    def execute(self, context):
        root = types_face_frame.find_cabinet_root(context.active_object)
        if root is None:
            self.report({'WARNING'}, "No face frame cabinet selected")
            return {'CANCELLED'}
        types_face_frame.recalculate_face_frame_cabinet(root)
        self.report({'INFO'}, f"Recalculated {root.name}")
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Operator: backfill missing opening cages on existing face frame cabinets
# ---------------------------------------------------------------------------
# Used when the data model gains new per-bay structures (openings here;
# possibly more later). Walks every face frame cabinet in the scene and
# creates an Opening 1 child on any bay that lacks one, then recalculates
# each touched cabinet so the new openings get sized.
class hb_face_frame_OT_backfill_openings(bpy.types.Operator):
    """Add an opening cage to any face frame bay missing one."""
    bl_idname = "hb_face_frame.backfill_openings"
    bl_label = "Backfill Face Frame Openings"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        added = 0
        touched_cabinets = []
        for cab_obj in bpy.data.objects:
            if not cab_obj.get(types_face_frame.TAG_CABINET_CAGE):
                continue
            cabinet_added = 0
            for bay_obj in cab_obj.children:
                if not bay_obj.get(types_face_frame.TAG_BAY_CAGE):
                    continue
                if any(c.get(types_face_frame.TAG_OPENING_CAGE)
                       for c in bay_obj.children):
                    continue
                opening = types_face_frame.FaceFrameOpening()
                opening.create('Opening 1')
                opening.obj.parent = bay_obj
                opening.obj['hb_opening_index'] = 0
                opening.obj.face_frame_opening.opening_index = 0
                cabinet_added += 1
            if cabinet_added:
                touched_cabinets.append(cab_obj)
                added += cabinet_added

        for cab_obj in touched_cabinets:
            types_face_frame.recalculate_face_frame_cabinet(cab_obj)

        self.report(
            {'INFO'},
            f"Added {added} opening(s) across {len(touched_cabinets)} cabinet(s)",
        )
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
            return bool(obj.get('CABINET_PART'))
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
        # Only touch objects that are part of a face frame cabinet, or are
        # generic cabinet parts/cages we know about. Avoids dimming arbitrary
        # scene geometry.
        if types_face_frame.find_cabinet_root(obj) is None:
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
        if not ff_scene.face_frame_selection_mode_enabled:
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

    Shows ONLY cabinet-wide settings (dimensions, construction, face
    frame defaults) - not per-bay properties. Per-bay editing goes
    through hb_face_frame.bay_prompts; per-mid-stile editing goes
    through hb_face_frame.mid_stile_prompts.
    """
    bl_idname = "hb_face_frame.cabinet_prompts"
    bl_label = "Cabinet Properties"
    bl_description = "Edit cabinet-wide properties (dimensions, construction, face frame defaults)"
    bl_options = {'UNDO'}

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
        ui_face_frame.draw_cabinet_wide(self.layout, root)


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
        for i in range(new_count):
            new_op = types_face_frame.FaceFrameOpening()
            new_op.create('Opening')
            new_op.obj.parent = split_obj
            new_op.obj['hb_split_child_index'] = i
            new_op.obj.face_frame_opening.opening_index = next_idx + i
            new_op.obj.face_frame_opening.size = self.sizes[i]
            new_op.obj.face_frame_opening.unlock_size = self.unlocks[i]
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


classes = (
    hb_face_frame_OT_draw_cabinet,
    hb_face_frame_OT_recalculate_cabinet,
    hb_face_frame_OT_backfill_openings,
    hb_face_frame_OT_toggle_mode,
    hb_face_frame_OT_cabinet_prompts,
    hb_face_frame_OT_bay_prompts,
    hb_face_frame_OT_opening_prompts,
    hb_face_frame_OT_split_opening,
    hb_face_frame_OT_mid_stile_prompts,
)


register, unregister = bpy.utils.register_classes_factory(classes)
