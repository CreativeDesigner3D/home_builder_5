"""Right-click context menus for face frame cabinets, bays, and mid stiles.

The right-click handler in ui/menu_apend.py reads obj['MENU_ID'] from the
active object and shows the named Menu class. Each face-frame-tagged cage
or part sets its MENU_ID to one of the menu classes defined here.

Pass 1 keeps the menus minimal - only items that have working operators
(Recalculate + the three scoped Properties popups). Action operators
(Add Bay, Split Bay, Delete Bay, Insert Mid Stile, etc.) will land in a
later pass once those operators are implemented.
"""
import bpy

from . import bay_presets
from . import types_face_frame
from . import types_face_frame_corner
from .operators import ops_part_commands
from ... import units


class HOME_BUILDER_MT_face_frame_cabinet_commands(bpy.types.Menu):
    """Right-click menu for a face frame cabinet root."""
    bl_label = "Face Frame Cabinet Commands"

    def draw(self, context):
        layout = self.layout
        layout.operator("hb_face_frame.cabinet_prompts",
                        text="Cabinet Properties...", icon='WINDOW')
        # Duplicate: copy-and-place. Seeds the placement modal from
        # this cabinet; the drop deep-copies the whole hierarchy so
        # bay configs, fronts, and the style come along. F in the
        # modal toggles fill-the-gap. Corner cabinets place through
        # a different modal - no duplicate for them yet.
        _dup_root = types_face_frame.find_cabinet_root(context.active_object)
        if (_dup_root is not None
                and getattr(_dup_root.face_frame_cabinet,
                            'corner_type', 'NONE') == 'NONE'):
            op = layout.operator("hb_face_frame.place_cabinet",
                                 text="Duplicate", icon='DUPLICATE')
            op.source_cabinet_name = _dup_root.name
            op = layout.operator("hb_face_frame.place_cabinet",
                                 text="Duplicate Mirror", icon='MOD_MIRROR')
            op.source_cabinet_name = _dup_root.name
            op.mirror = True
        layout.separator()
        layout.operator("hb_face_frame.join_cabinets",
                        text="Join Cabinets", icon='AUTOMERGE_ON')
        layout.operator("hb_face_frame.equalize_bays",
                        text="Equalize Bays", icon='ALIGN_JUSTIFY')

        # Show "Create Cabinet Group" whenever at least one cabinet is in
        # the selection. A single-cabinet group is allowed on purpose: the
        # 2D sheet set generates a 9-view (IslandNineView) per cabinet group
        # (generate_room_views loops get_cabinet_groups), so grouping one
        # cabinet is how a user opts that cabinet into its own 9-view.
        # find_cabinet_root walks any selected part up to its root, so the
        # menu surfaces correctly whether the user picked roots, bays, or
        # individual face frame parts.
        selected_roots = set()
        for obj in context.selected_objects:
            root = types_face_frame.find_cabinet_root(obj)
            if root is not None:
                selected_roots.add(root.name)
        if len(selected_roots) >= 1:
            layout.operator("hb_face_frame.create_cabinet_group",
                            text="Create Cabinet Group", icon='ADD')

        # "Select Cabinet Group" - re-collapse the group (hide the member
        # cabinet cages, show the group cage). The group cage is hidden
        # whenever a selection mode is active, so this is how the user gets
        # it back. Shown only when the right-clicked cabinet is in a group:
        # walk its root's parents to an IS_CAGE_GROUP cage.
        active_root = types_face_frame.find_cabinet_root(context.active_object)
        cur = active_root.parent if active_root is not None else None
        while cur is not None and not cur.get('IS_CAGE_GROUP'):
            cur = cur.parent
        if cur is not None:
            layout.operator("hb_face_frame.select_cabinet_group",
                            text="Select Cabinet Group", icon='OBJECT_ORIGIN')
            layout.operator("hb_face_frame.ungroup_cabinet",
                            text="Ungroup Cabinet", icon='GROUP')

        # Show Applied Panels - only when the right-clicked cabinet has
        # applied finished-end panels (children tagged
        # TAG_APPLIED_PANEL_SIDE). Runs the existing selection-mode flip
        # (Finished Ends panel has the same button): every applied
        # panel's cage becomes clickable for right-click editing and the
        # host cabinet cages drop out of the way. Any standard mode in
        # the picker (Cabinets, Bays, ...) returns to normal.
        if active_root is not None and any(
                child.get(types_face_frame.TAG_APPLIED_PANEL_SIDE)
                for child in active_root.children):
            layout.separator()
            layout.operator("hb_face_frame.show_applied_panels",
                            text="Show Applied Panels", icon='HIDE_OFF')

        # Tip-up wedge calculator - refrigerator cabinets only. The root
        # carries this menu's MENU_ID, so the right-clicked active object
        # is the cabinet root; find_cabinet_root is used anyway for safety.
        root = types_face_frame.find_cabinet_root(context.active_object)
        if root is not None and root.get('CLASS_NAME') == 'RefrigeratorCabinet':
            layout.separator()
            layout.operator("hb_face_frame.add_refrigerator_wedge",
                            text="Wedge Calculator...", icon='MOD_BEVEL')
            if root.face_frame_cabinet.wedge_enabled:
                layout.operator("hb_face_frame.remove_refrigerator_wedge",
                                text="Remove Wedge", icon='X')

        layout.separator()
        layout.operator("hb_face_frame.delete_cabinet",
                        text="Delete Cabinet", icon='X')


class HOME_BUILDER_MT_face_frame_cabinet_group_commands(bpy.types.Menu):
    """Right-click menu for a cabinet group cage (IS_CAGE_GROUP)."""
    bl_label = "Cabinet Group Commands"

    def draw(self, context):
        layout = self.layout
        layout.operator("hb_face_frame.grab_cabinet_group",
                        text="Grab Cabinet Group", icon='OBJECT_ORIGIN')
        layout.separator()
        layout.operator("hb_face_frame.ungroup_cabinet",
                        text="Ungroup Cabinet", icon='GROUP')


class HOME_BUILDER_MT_face_frame_bay_commands(bpy.types.Menu):
    """Right-click menu for a face frame bay cage."""
    bl_label = "Face Frame Bay Commands"

    def draw(self, context):
        layout = self.layout
        layout.operator("hb_face_frame.bay_prompts",
                        text="Bay Properties...", icon='WINDOW')

        # Change Bay submenu (preset swaps) sits right under Properties
        # so type-changing edits stay grouped with property edits. Hidden
        # for cabinet types with no presets (currently LAP_DRAWER).
        bay_obj = context.active_object
        cab_root = (types_face_frame.find_cabinet_root(bay_obj)
                    if bay_obj is not None else None)
        if cab_root is not None:
            cabinet_type = cab_root.face_frame_cabinet.cabinet_type
            if cabinet_type in bay_presets.MENU_ENTRIES:
                layout.menu("HOME_BUILDER_MT_face_frame_change_bay",
                            text="Change Bay")
            # Appliance configs (sink / cooktop) are base-bay only.
            if cabinet_type == 'BASE':
                layout.menu("HOME_BUILDER_MT_face_frame_add_appliance",
                            text="Add Appliance to Bay", icon='MOD_FLUIDSIM')
            # Flush toe kick toggle - base / tall only (uppers have no
            # kick to flush).
            if cabinet_type in ('BASE', 'TALL'):
                layout.operator("hb_face_frame.toggle_flush_toe_kick",
                                text="Toggle Flush Toe Kick",
                                icon='SNAP_PERPENDICULAR')

        # Structural edits live below in their own group. Anchored on
        # the right-clicked bay's index since the bay cage is the active
        # object when this menu opens.
        bay_index = (bay_obj.face_frame_bay.bay_index
                     if bay_obj is not None
                     and bay_obj.get(types_face_frame.TAG_BAY_CAGE)
                     else 0)
        layout.separator()
        op = layout.operator("hb_face_frame.insert_bay",
                             text="Insert Bay Before", icon='TRIA_LEFT')
        op.bay_index = bay_index
        op.direction = 'BEFORE'
        op = layout.operator("hb_face_frame.insert_bay",
                             text="Insert Bay After", icon='TRIA_RIGHT')
        op.bay_index = bay_index
        op.direction = 'AFTER'
        # Honest labeling: on a single-bay cabinet the operator
        # degrades to deleting the whole cabinet, so say so up front.
        _n_bays = (sum(1 for c in cab_root.children
                       if c.get(types_face_frame.TAG_BAY_CAGE))
                   if cab_root is not None else 0)
        op = layout.operator(
            "hb_face_frame.delete_bay",
            text=("Delete Cabinet" if _n_bays <= 1 else "Delete Bay"),
            icon='X')
        op.bay_index = bay_index

        layout.separator()
        layout.operator("hb_face_frame.break_cabinet_left",
                        text="Break Left", icon='TRIA_LEFT_BAR')
        layout.operator("hb_face_frame.break_cabinet_right",
                        text="Break Right", icon='TRIA_RIGHT_BAR')
        layout.operator("hb_face_frame.break_cabinet_both",
                        text="Break Both", icon='UNLINKED')
        layout.operator("hb_face_frame.equalize_bays",
                        text="Equalize Bays", icon='ALIGN_JUSTIFY')

        # Equalize-door-width is bay-scope by selection but cabinet-
        # scope in its effect (every bay in the picked cabinets is
        # recalculated). Lives at the bottom of the bay menu so the
        # structural edits above stay grouped.
        layout.separator()
        layout.operator("hb_face_frame.set_equal_door_width",
                        text="Set Equal Door Width",
                        icon='ALIGN_JUSTIFY')


class HOME_BUILDER_MT_face_frame_part_commands(bpy.types.Menu):
    """Right-click menu shared by all face frame parts - end stiles,
    mid stiles, top / bottom rails, and bay-internal splitters. Items
    shown depend on the active part's role:

      end stile  -> Set Width, Set Scribe, Toggle Stile to Floor
      top rail   -> Set Width, Set Scribe (top_scribe)
      mid stile  -> Set Width, Mid Stile Properties... (deeper popup)
      others     -> Set Width
    """
    bl_label = "Face Frame Part Commands"

    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        role = obj.get('hb_part_role') if obj is not None else None

        # Parts of an applied finished-end panel (the "panel back")
        # surface that panel's own properties dialog. find_cabinet_root
        # stops at the applied-panel root, so cabinet_prompts edits the
        # panel itself, not the host cabinet.
        panel_root = types_face_frame.find_cabinet_root(obj)
        if panel_root is not None and (
                panel_root.get(types_face_frame.TAG_APPLIED_PANEL_SIDE)
                or types_face_frame._is_standalone_panel(panel_root)):
            ptext = ("Panel Back Properties..."
                     if panel_root.get(types_face_frame.TAG_APPLIED_PANEL_SIDE)
                     else "Panel Properties...")
            layout.operator("hb_face_frame.cabinet_prompts",
                            text=ptext, icon='WINDOW')
            layout.separator()

        # 5-piece door / drawer front: stile / rail / mid rail editor.
        if ops_part_commands.has_door_style_modifier(obj):
            layout.operator("hb_face_frame.set_door_frame",
                            text="Set Door Frame...", icon='MOD_BEVEL')

        # Face frame members (stiles / rails / splitters) keep their role-aware
        # Set Width. Every other cabinet part adjusts its size via Make
        # Editable (below) - there is no direct Set Size command.
        if role in ops_part_commands._ROLES_WITH_WIDTH:
            current_w = ops_part_commands.get_current_width(obj)
            if current_w is None:
                width_text = "Set Width"
            else:
                width_text = f"Set Width: {units.unit_to_string(context.scene.unit_settings, current_w)}"
            layout.operator("hb_face_frame.set_part_width",
                            text=width_text, icon='ARROW_LEFTRIGHT')

        # Scribe only makes sense at the cabinet's outer edges: end
        # stiles (left / right) and the top rail (top_scribe).
        if role in (types_face_frame.PART_ROLE_LEFT_STILE,
                    types_face_frame.PART_ROLE_RIGHT_STILE,
                    types_face_frame.PART_ROLE_TOP_RAIL):
            layout.operator("hb_face_frame.set_part_scribe",
                            text="Set Scribe...", icon='SNAP_EDGE')

        # Stile-to-floor: end stiles and between-bay mid stiles.
        if role in (types_face_frame.PART_ROLE_LEFT_STILE,
                    types_face_frame.PART_ROLE_RIGHT_STILE,
                    types_face_frame.PART_ROLE_MID_STILE):
            layout.operator("hb_face_frame.toggle_stile_to_floor",
                            text="Toggle Stile to Floor",
                            icon='TRIA_DOWN_BAR')

        # Finished-end condition is per-side: shown on the left / right
        # carcass side panels. The operator derives the side from the
        # clicked part's role and shows only that side's enum.
        if role in (types_face_frame.PART_ROLE_LEFT_SIDE,
                    types_face_frame.PART_ROLE_RIGHT_SIDE,
                    types_face_frame_corner.PART_ROLE_CORNER_LEFT_SIDE,
                    types_face_frame_corner.PART_ROLE_CORNER_RIGHT_SIDE):
            layout.operator("hb_face_frame.set_finished_end_condition",
                            text="Set Finished End Condition...",
                            icon='MOD_SOLIDIFY')

        # Bottom rail can be removed. The rail spans the bays in its
        # segment; the operator sets Remove Bottom across that whole span
        # so the rail the user clicked goes away as one piece.
        if role == types_face_frame.PART_ROLE_BOTTOM_RAIL:
            layout.operator("hb_face_frame.remove_bottom_rail",
                            text="Remove Bottom Rail", icon='X')
            layout.menu("HOME_BUILDER_MT_face_frame_bottom_rail_profile",
                        text="Bottom Rail Profile", icon='MOD_BEVEL')

        # The valance front board carries the same decorative profile
        # option as a cabinet bottom rail (arch etc.).
        if role == types_face_frame.PART_ROLE_VALANCE_BOARD:
            layout.menu("HOME_BUILDER_MT_face_frame_bottom_rail_profile",
                        text="Bottom Profile", icon='MOD_BEVEL')

        # A mid rail can be removed (mainly between drawers). The split
        # stays; the FF member + its backing drop and the solver closes
        # the two fronts to a 3/32" reveal. No restore here - rebuild the
        # bay via Change Bay if needed.
        if role == types_face_frame.PART_ROLE_BAY_MID_RAIL:
            layout.operator("hb_face_frame.remove_mid_rail",
                            text="Remove Mid Rail", icon='X')

        # Mid stiles keep their deeper properties popup (extend up /
        # down) as an additional item.
        if role == types_face_frame.PART_ROLE_MID_STILE:
            layout.separator()
            layout.operator("hb_face_frame.mid_stile_prompts",
                            text="Mid Stile Properties...", icon='WINDOW')

        # Machining cutout (hole / route) - available on any parametric cutpart
        # (sides, backs, panels, doors, hood parts). Shows in 3D and in the 2D
        # copy, so no detail view is needed. Operator lives in ops_part_commands.
        if ops_part_commands._is_cutpart(obj):
            layout.separator()
            layout.operator("hb_face_frame.add_part_cutout",
                            text="Add Cutout...", icon='MOD_BOOLEAN')
            if ops_part_commands._user_cutout_mods(obj):
                layout.operator("hb_face_frame.remove_part_cutout",
                                text="Remove Cutout", icon='X')

        # Make Editable / Revert to Parametric. Applying a part's GeoNode(s)
        # turns it into real, hand-editable mesh that the recalc then leaves
        # alone; Revert restores parametric control. Works on structural
        # cutparts AND door / drawer fronts (each has its own apply / revert
        # path - see the operators).
        is_manual = bool(obj.get('IS_MANUAL_PART')) if obj is not None else False
        can_make_editable = (
            ops_part_commands._can_make_editable(obj)
            or ops_part_commands._can_make_front_editable(obj))
        # Hood parts have no cabinet recalc to re-drive them, so they revert via
        # their own snapshot path (home_builder.revert_hood_part) which restores
        # just the clicked part. A hood part made editable before the snapshot
        # feature has no snapshot - rebuild the hood to restore it.
        if is_manual and obj is not None and obj.get('IS_WOOD_HOOD_PART'):
            if obj.get('HOOD_PARAMETRIC_SNAPSHOT'):
                layout.separator()
                layout.operator("home_builder.revert_hood_part",
                                text="Revert to Parametric", icon='FILE_REFRESH')
        elif is_manual:
            layout.separator()
            layout.operator("hb_face_frame.revert_part_to_parametric",
                            text="Revert to Parametric", icon='FILE_REFRESH')
        elif can_make_editable:
            layout.separator()
            layout.operator("hb_face_frame.make_part_editable",
                            text="Make Editable", icon='EDITMODE_HLT')


class HOME_BUILDER_MT_face_frame_interior_part_commands(bpy.types.Menu):
    """Right-click menu for an interior part (shelf, pullout, mesh part,
    rollout box, etc.). Surfaces the owning opening's properties so the
    user can edit the opening's interior_items list without having to
    select the opening cage directly. The opening_prompts operator
    handles the walk-up from the clicked interior part.
    """
    bl_label = "Face Frame Interior Part Commands"

    def draw(self, context):
        layout = self.layout
        layout.operator("hb_face_frame.opening_prompts",
                        text="Opening Properties...", icon='WINDOW')


class HOME_BUILDER_MT_face_frame_opening_commands(bpy.types.Menu):
    """Right-click menu for a face frame opening cage."""
    bl_label = "Face Frame Opening Commands"

    def draw(self, context):
        layout = self.layout
        layout.operator("hb_face_frame.opening_prompts",
                        text="Opening Properties...", icon='WINDOW')
        layout.menu("HOME_BUILDER_MT_face_frame_change_opening",
                    text="Change Opening")
        layout.operator("hb_face_frame.accessory_menu",
                        text="Add Accessory...", icon='ADD')
        layout.separator()
        op = layout.operator("hb_face_frame.split_opening",
                             text="Split Horizontal", icon='SNAP_EDGE')
        op.axis = 'H'
        op = layout.operator("hb_face_frame.split_opening",
                             text="Split Vertical", icon='PAUSE')
        op.axis = 'V' 


class HOME_BUILDER_MT_face_frame_change_opening(bpy.types.Menu):
    """Submenu of opening configuration presets. Each entry calls
    hb_face_frame.change_opening with the appropriate config; the
    operator drives front_type, hinge_side, and the ADJUSTABLE_SHELF
    interior item to match.
    """
    bl_label = "Change Opening"

    # (config_value, display_text); ('SEP',) inserts a separator.
    ENTRIES = [
        ('OPEN',              "Open"),
        ('OPEN_WITH_SHELVES', "Open with Shelves"),
        ('SEP',),
        ('LEFT_DOOR',         "Left Door"),
        ('RIGHT_DOOR',        "Right Door"),
        ('DOUBLE_DOOR',       "Double Door"),
        ('SEP',),
        ('FLIP_UP_DOOR',      "Flip Up Door"),
        ('FLIP_DOWN_DOOR',    "Flip Down Door"),
        ('SEP',),
        ('DRAWER',            "Drawer"),
        ('FALSE_FRONT',       "False Front"),
        ('TILT_OUT',          "Tilt-Out"),
        ('PULLOUT',           "Pullout"),
        ('SEP',),
        ('INSET_PANEL',       "Inset Panel"),
        ('APPLIANCE',         "Appliance"),
    ]

    def draw(self, context):
        layout = self.layout
        for entry in self.ENTRIES:
            if entry[0] == 'SEP':
                layout.separator()
                continue
            config, label = entry
            op = layout.operator("hb_face_frame.change_opening", text=label)
            op.config = config


class HOME_BUILDER_MT_face_frame_change_bay(bpy.types.Menu):
    """Submenu of bay configuration presets. Reads the active bay's
    cabinet type to pick which entry list to render. Each entry calls
    hb_face_frame.change_bay with the right config string; the
    operator looks the recipe up in bay_presets.PRESETS.
    """
    bl_label = "Change Bay"

    def draw(self, context):
        layout = self.layout
        bay_obj = context.active_object
        cab_root = (types_face_frame.find_cabinet_root(bay_obj)
                    if bay_obj is not None else None)
        if cab_root is None:
            layout.label(text="No cabinet selected")
            return
        cabinet_type = cab_root.face_frame_cabinet.cabinet_type
        entries = bay_presets.MENU_ENTRIES.get(cabinet_type)
        if not entries:
            layout.label(text=f"No presets for {cabinet_type}")
            return
        for entry in entries:
            if entry[0] == 'SEP':
                layout.separator()
                continue
            config, label, *rest = entry
            icon = rest[0] if rest else 'NONE'
            op = layout.operator("hb_face_frame.change_bay",
                                 text=label, icon=icon)
            op.config = config


class HOME_BUILDER_MT_face_frame_add_appliance(bpy.types.Menu):
    """Submenu: configure the active base bay for a sink or cooktop. Each
    entry invokes hb_face_frame.add_appliance_to_bay with the appliance
    kind preset; the operator opens a dialog for width / drop / config /
    interior.
    """
    bl_label = "Add Appliance to Bay"

    def draw(self, context):
        layout = self.layout
        for kind, label, icon in (
            ('KITCHEN_SINK', "Add Kitchen Sink", 'MOD_FLUIDSIM'),
            ('VANITY_SINK',  "Add Vanity Sink",  'MOD_FLUIDSIM'),
            ('COOKTOP',      "Add Cooktop",      'VOLUME_DATA'),
        ):
            op = layout.operator("hb_face_frame.add_appliance_to_bay",
                                 text=label, icon=icon)
            op.appliance_kind = kind

        # Remove entry only when the bay currently carries an appliance:
        # a SINK / COOKTOP stamp, or (dedicated sink cabinet) the
        # auto-detected annotation child.
        bay = context.active_object
        kind = bay.get('APPLIANCE_BAY') if bay is not None else None
        if kind not in ('SINK', 'COOKTOP') and bay is not None:
            kind = None
            for child in bay.children:
                if child.get('APPLIANCE_ANNOTATION'):
                    kind = ('SINK' if child.get('IS_SINK_ANNOTATION')
                            else 'COOKTOP')
                    break
        if kind in ('SINK', 'COOKTOP'):
            layout.separator()
            layout.operator("hb_face_frame.remove_appliance_from_bay",
                            text=f"Remove {kind.title()}", icon='X')


class HOME_BUILDER_MT_face_frame_leg_product_commands(bpy.types.Menu):
    """Right-click menu for a leg product root."""
    bl_label = "Leg Product Commands"

    def draw(self, context):
        layout = self.layout
        layout.operator("hb_face_frame.leg_product_prompts",
                        text="Leg Properties...", icon='WINDOW')
        layout.separator()
        layout.operator("hb_face_frame.delete_cabinet",
                        text="Delete Leg", icon='X')


class HOME_BUILDER_MT_face_frame_floating_shelf_commands(bpy.types.Menu):
    """Right-click menu for a floating shelf root."""
    bl_label = "Floating Shelf Commands"

    def draw(self, context):
        layout = self.layout
        layout.operator("hb_face_frame.floating_shelf_prompts",
                        text="Floating Shelf Properties...", icon='WINDOW')
        layout.operator("hb_face_frame.duplicate_floating_shelf",
                        text="Set Quantity & Spacing...", icon='LINENUMBERS_ON')
        # Multi-shelf editor - only when 2+ distinct floating shelves are
        # selected (align their floor height, spacing, and thickness).
        roots = set()
        for o in context.selected_objects:
            r = types_face_frame.find_cabinet_root(o)
            if r is not None and r.get('IS_FLOATING_SHELF'):
                roots.add(r.name)
        if len(roots) > 1:
            layout.operator("hb_face_frame.adjust_floating_shelves",
                            text="Adjust Spacing & Heights...", icon='LINENUMBERS_ON')
        layout.separator()
        layout.operator("hb_face_frame.delete_cabinet",
                        text="Delete Shelf", icon='X')


class HOME_BUILDER_MT_face_frame_door_part_commands(bpy.types.Menu):
    """Right-click menu for a Door Part - a bare door front (cutpart +
    door style + pull, no cabinet cage). Set Dimensions resizes the door
    (and re-tracks its pull); Assign Active Style re-applies the project's
    active cabinet style's door style; Delete routes through the HB5-aware
    delete (falls back to object.delete for a cage-less part).
    """
    bl_label = "Door Part Commands"

    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        show_pull = obj.get('DOOR_PART_SHOW_PULL', True) if obj else True
        is_drawer = (obj.get('DOOR_PART_FRONT_KIND', 'DOOR') == 'DRAWER') if obj else False
        layout.operator("hb_face_frame.set_door_part_dimensions",
                        text="Set Dimensions...", icon='ARROW_LEFTRIGHT')
        if ops_part_commands.has_door_style_modifier(obj):
            layout.operator("hb_face_frame.set_door_frame",
                            text="Set Door Frame...", icon='MOD_BEVEL')
        layout.operator("hb_face_frame.assign_active_door_style",
                        text="Assign Active Style", icon='MOD_BEVEL')
        layout.separator()
        # Front kind: door vs drawer front (only the pull placement /
        # asset differs). Label offers the OTHER kind.
        layout.operator("hb_face_frame.toggle_door_part_front_kind",
                        text="Switch to Door Front" if is_drawer else "Switch to Drawer Front",
                        icon='FILE_REFRESH')
        layout.separator()
        # Pull controls. Toggle label tracks current state; switch-side is
        # only meaningful for a shown DOOR-front pull (drawer pulls are
        # centered, so side does nothing there).
        layout.operator("hb_face_frame.toggle_door_part_pull",
                        text="Hide Pull" if show_pull else "Show Pull",
                        icon='CHECKBOX_HLT' if show_pull else 'CHECKBOX_DEHLT')
        row = layout.row()
        row.enabled = show_pull and not is_drawer
        row.operator("hb_face_frame.switch_door_part_pull_side",
                     text="Switch Pull Side", icon='ARROW_LEFTRIGHT')
        layout.separator()
        layout.operator("hb_general.delete", text="Delete Part", icon='X')


class HOME_BUILDER_MT_face_frame_valance_commands(bpy.types.Menu):
    """Right-click menu for a valance root."""
    bl_label = "Valance Commands"

    def draw(self, context):
        layout = self.layout
        layout.operator("hb_face_frame.valance_prompts",
                        text="Valance Properties...", icon='WINDOW')
        layout.menu("HOME_BUILDER_MT_face_frame_bottom_rail_profile",
                    text="Bottom Profile", icon='MOD_BEVEL')
        layout.separator()
        layout.operator("hb_face_frame.delete_cabinet",
                        text="Delete Valance", icon='X')


class HOME_BUILDER_MT_face_frame_misc_part_commands(bpy.types.Menu):
    """Right-click menu for a Misc Part - a bare GeoNodeCutpart with no
    cabinet cage. The cabinet / part-role menus don't apply, so this is
    size, machining cutouts, Make Editable / Revert, and delete. Set
    Dimensions and the cutout items edit the cutpart's GeoNode inputs, so
    they hide once the part is made editable (GN applied); Delete routes
    through the HB5-aware delete (which falls back to object.delete for a
    cage-less part).
    """
    bl_label = "Misc Part Commands"

    def draw(self, context):
        layout = self.layout
        obj = context.active_object

        if ops_part_commands._is_cutpart(obj):
            layout.operator("hb_face_frame.set_misc_part_dimensions",
                            text="Set Dimensions...", icon='ARROW_LEFTRIGHT')
            # Machining cutout - same entries as the cabinet-part menu; a
            # Misc Part is itself a parametric cutpart so the operators
            # apply unchanged.
            layout.separator()
            layout.operator("hb_face_frame.add_part_cutout",
                            text="Add Cutout...", icon='MOD_BOOLEAN')
            if ops_part_commands._user_cutout_mods(obj):
                layout.operator("hb_face_frame.remove_part_cutout",
                                text="Remove Cutout", icon='X')

        # Make Editable / Revert. A Misc Part has no cabinet recalc, so
        # Revert restores its stashed Length / Width / Thickness directly
        # (see ops_part_commands._revert_one).
        if obj is not None and obj.get('IS_MANUAL_PART'):
            layout.separator()
            layout.operator("hb_face_frame.revert_part_to_parametric",
                            text="Revert to Parametric", icon='FILE_REFRESH')
        elif ops_part_commands._can_make_editable(obj):
            layout.separator()
            layout.operator("hb_face_frame.make_part_editable",
                            text="Make Editable", icon='EDITMODE_HLT')

        layout.separator()
        layout.operator("hb_general.delete", text="Delete Part", icon='X')


class HOME_BUILDER_MT_face_frame_bottom_rail_profile(bpy.types.Menu):
    """Pick the decorative bottom-rail profile for this cabinet. Lists None +
    every '* Cutter' curve in face_frame_assets/profiles; the current choice is
    marked. Each item sets the cabinet-level bottom_rail_profile enum."""
    bl_label = "Bottom Rail Profile"

    def draw(self, context):
        import os
        layout = self.layout
        root = types_face_frame.find_cabinet_root(context.active_object)
        current = ''
        if root is not None:
            current = getattr(root.face_frame_cabinet, 'bottom_rail_profile', 'NONE')
        items = [('NONE', 'None'), ('ARCH', 'Arched')]
        d = types_face_frame.bottom_rail_profile_dir()
        if os.path.isdir(d):
            for fn in sorted(os.listdir(d)):
                if fn.endswith(' Cutter.blend'):
                    stem = fn[:-len('.blend')]
                    items.append((stem, stem[:-len(' Cutter')]))
        for pid, label in items:
            icon = 'RADIOBUT_ON' if pid == current else 'RADIOBUT_OFF'
            op = layout.operator('hb_face_frame.set_bottom_rail_profile',
                                  text=label, icon=icon)
            op.profile_id = pid


classes = (
    HOME_BUILDER_MT_face_frame_cabinet_commands,
    HOME_BUILDER_MT_face_frame_floating_shelf_commands,
    HOME_BUILDER_MT_face_frame_valance_commands,
    HOME_BUILDER_MT_face_frame_misc_part_commands,
    HOME_BUILDER_MT_face_frame_door_part_commands,
    HOME_BUILDER_MT_face_frame_leg_product_commands,
    HOME_BUILDER_MT_face_frame_cabinet_group_commands,
    HOME_BUILDER_MT_face_frame_bay_commands,
    HOME_BUILDER_MT_face_frame_part_commands,
    HOME_BUILDER_MT_face_frame_interior_part_commands,
    HOME_BUILDER_MT_face_frame_opening_commands,
    HOME_BUILDER_MT_face_frame_change_opening,
    HOME_BUILDER_MT_face_frame_change_bay,
    HOME_BUILDER_MT_face_frame_add_appliance,
    HOME_BUILDER_MT_face_frame_bottom_rail_profile,
)


register, unregister = bpy.utils.register_classes_factory(classes)
