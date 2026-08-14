"""Right-click context menus for closet starters, bays, and openings.

The right-click handler in ui/menu_apend.py reads obj['MENU_ID'] from
the active object and shows the named Menu class.
"""
import bpy

from . import types_closets


class HOME_BUILDER_MT_closet_starter_commands(bpy.types.Menu):
    """Right-click menu for a closet starter root."""
    bl_label = "Closet Starter Commands"

    def draw(self, context):
        layout = self.layout
        layout.operator("hb_closets.starter_prompts",
                        text="Starter Properties...", icon='WINDOW')
        # Duplicate: copy-and-place. Seeds the placement modal from
        # this starter; the drop deep-copies the hierarchy so all bay
        # configs come along. F in the modal toggles fill-the-gap.
        _dup_root = types_closets.find_starter_root(context.active_object)
        if _dup_root is not None:
            op = layout.operator("hb_closets.place_starter",
                                 text="Duplicate", icon='DUPLICATE')
            op.source_starter_name = _dup_root.name
            op = layout.operator("hb_closets.place_starter",
                                 text="Duplicate Mirror", icon='MOD_MIRROR')
            op.source_starter_name = _dup_root.name
            op.mirror = True
        # Re-opens the placement-time clearance dialog; cancels itself
        # with an info report when no corner neighbor qualifies.
        layout.operator("hb_closets.set_corner_clearance",
                        text="Corner Clearance...", icon='SNAP_EDGE')
        layout.separator()
        layout.operator("hb_closets.delete_starter",
                        text="Delete Starter", icon='X')


class HOME_BUILDER_MT_closet_hanger_commands(bpy.types.Menu):
    """Right-click menu for a display hanger."""
    bl_label = "Hanger Commands"

    def draw(self, context):
        self.layout.operator("hb_closets.change_hanger",
                             text="Change Hanger...", icon='MOD_CLOTH')


class HOME_BUILDER_MT_closet_bay_commands(bpy.types.Menu):
    """Right-click menu for a closet bay cage."""
    bl_label = "Closet Bay Commands"

    def draw(self, context):
        # Menu order: Properties | shelf, rod | Change Bay, fronts
        # submenu | structure (insert x2, clear) | delete. Adjustable
        # Shelves / Cubbies intentionally absent here - reachable via
        # Change Bay and the opening menu.
        layout = self.layout
        layout.operator("hb_closets.bay_prompts",
                        text="Bay Properties...", icon='WINDOW')
        layout.separator()
        op = layout.operator("hb_closets.add_part",
                             text="Add Fixed Shelf", icon='FIXED_SIZE')
        op.part_type = 'FIXED_SHELF'
        op = layout.operator("hb_closets.add_part",
                             text="Add Closet Rod", icon='MOD_CLOTH')
        op.part_type = 'ROD'
        layout.separator()
        layout.menu("HOME_BUILDER_MT_closet_change_bay",
                    text="Bay Configuration", icon='PRESET')
        layout.menu("HOME_BUILDER_MT_closet_doors_drawers",
                    text="Add Doors & Drawers", icon='SNAP_VOLUME')
        layout.separator()
        layout.operator("hb_closets.copy_bay",
                        text="Copy Bay", icon='COPYDOWN')
        layout.operator("hb_closets.paste_bay",
                        text="Paste Bay", icon='PASTEDOWN')
        layout.separator()
        op = layout.operator("hb_closets.insert_bay",
                             text="Insert Bay Left", icon='TRIA_LEFT')
        op.direction = 'BEFORE'
        op = layout.operator("hb_closets.insert_bay",
                             text="Insert Bay Right", icon='TRIA_RIGHT')
        op.direction = 'AFTER'
        layout.operator("hb_closets.clear_bay",
                        text="Clear Bay", icon='TRASH')
        layout.separator()
        # Honest labeling: on a single-bay starter the operator
        # degrades to deleting the whole starter, so say so up front.
        _root = types_closets.find_starter_root(context.active_object)
        _n_bays = (sum(1 for c in _root.children
                       if c.get(types_closets.TAG_BAY_CAGE))
                   if _root is not None else 0)
        layout.operator(
            "hb_closets.delete_bay",
            text=("Delete Starter" if _n_bays <= 1 else "Delete Bay"),
            icon='X')


def _draw_add_part_entries(layout):
    """Shared add-part section for the bay and opening menus."""
    op = layout.operator("hb_closets.add_part",
                         text="Add Fixed Shelf", icon='FIXED_SIZE')
    op.part_type = 'FIXED_SHELF'
    op = layout.operator("hb_closets.add_part",
                         text="Add Closet Rod", icon='MOD_CLOTH')
    op.part_type = 'ROD'
    layout.operator("hb_closets.add_adj_shelves",
                    text="Adjustable Shelves...", icon='ALIGN_JUSTIFY')
    layout.operator("hb_closets.divide_opening",
                    text="Divide Opening...", icon='MOD_ARRAY')
    layout.separator()
    layout.menu("HOME_BUILDER_MT_closet_doors_drawers",
                text="Add Doors & Drawers", icon='SNAP_VOLUME')
    layout.menu("HOME_BUILDER_MT_closet_accessories",
                text="Add Accessory",
                icon='OUTLINER_OB_GROUP_INSTANCE')


class HOME_BUILDER_MT_closet_accessories(bpy.types.Menu):
    """What can be hung in a closet, grouped the way it mounts.

    One submenu per mounting family, so the list reads as three short
    menus rather than one long one. Picking one starts placing it, so
    the choice and the placing are one action rather than a dialog and
    then a height typed in."""
    bl_idname = "HOME_BUILDER_MT_closet_accessories"
    bl_label = "Add Accessory"

    def draw(self, context):
        from . import accessories_closets as acc
        layout = self.layout
        offered = acc.catalog_items()
        families = {d.family for d in offered}
        for family, menu_id in (
                (acc.FAMILY_OPENING,
                 "HOME_BUILDER_MT_closet_accessories_opening"),
                (acc.FAMILY_PANEL,
                 "HOME_BUILDER_MT_closet_accessories_panel")):
            if family in families:
                layout.menu(menu_id,
                            text=acc.FAMILY_LABELS.get(family, family))
        # Insert is always offered: alongside whatever the catalog
        # carries, it is where the built-in inserts - rollouts, shoe
        # shelves, cubbies - live.
        layout.menu("HOME_BUILDER_MT_closet_accessories_insert",
                    text=acc.FAMILY_LABELS.get(acc.FAMILY_INSERT,
                                               "Insert"))
        # The Curate line stands apart while it is being evaluated;
        # the guard lets this menu draw even where that module is
        # not registered.
        if hasattr(bpy.types,
                   'HOME_BUILDER_MT_closet_accessories_curate'):
            layout.separator()
            layout.menu("HOME_BUILDER_MT_closet_accessories_curate",
                        text="Curate")


class _closet_accessory_family_menu(bpy.types.Menu):
    """One mounting family's slice of the accessory catalog."""
    family = None

    def draw(self, context):
        from . import accessories_closets as acc
        layout = self.layout
        for acc_def in acc.catalog_items(family=self.family):
            op = layout.operator("hb_closets.place_accessory",
                                 text=acc_def.label)
            op.accessory = acc_def.key


class HOME_BUILDER_MT_closet_accessories_opening(
        _closet_accessory_family_menu):
    bl_idname = "HOME_BUILDER_MT_closet_accessories_opening"
    bl_label = "Opening"
    family = 'OPENING'


class HOME_BUILDER_MT_closet_accessories_panel(
        _closet_accessory_family_menu):
    bl_idname = "HOME_BUILDER_MT_closet_accessories_panel"
    bl_label = "Panel"
    family = 'PANEL'


class HOME_BUILDER_MT_closet_accessories_insert(
        _closet_accessory_family_menu):
    """The insert family: the built-in opening fills first, then
    whatever insert accessories the catalog carries."""
    bl_idname = "HOME_BUILDER_MT_closet_accessories_insert"
    bl_label = "Insert"
    family = 'INSERT'

    def draw(self, context):
        layout = self.layout
        layout.operator("hb_closets.add_rollouts",
                        text="Rollout Trays...", icon='MESH_PLANE')
        layout.operator("hb_closets.add_slanted_shelves",
                        text="Slanted Shoe Shelves...", icon='SORTBYEXT')
        layout.operator("hb_closets.add_cubbies",
                        text="Cubbies...", icon='MESH_GRID')
        from . import accessories_closets as acc
        if acc.catalog_items(family=self.family):
            layout.separator()
        _closet_accessory_family_menu.draw(self, context)


class HOME_BUILDER_MT_closet_opening_commands(bpy.types.Menu):
    """Right-click menu for a closet opening cage."""
    bl_label = "Closet Opening Commands"

    def draw(self, context):
        # Properties, Change Opening, then the add entries, then clear.
        # Both levels are offered: the opening dialog edits what fills
        # this segment, the bay dialog the section it sits in.
        layout = self.layout
        layout.operator("hb_closets.opening_prompts",
                        text="Opening Properties...", icon='WINDOW')
        layout.operator("hb_closets.bay_prompts",
                        text="Bay Properties...", icon='WINDOW')
        layout.separator()
        layout.menu("HOME_BUILDER_MT_closet_change_opening",
                    text="Change Opening", icon='PRESET')
        layout.separator()
        _draw_add_part_entries(layout)
        layout.separator()
        layout.operator("hb_closets.copy_opening",
                        text="Copy Opening", icon='COPYDOWN')
        layout.operator("hb_closets.paste_opening",
                        text="Paste Opening", icon='PASTEDOWN')
        layout.separator()
        layout.operator("hb_closets.clear_opening",
                        text="Clear Opening", icon='TRASH')


class HOME_BUILDER_MT_closet_change_bay(bpy.types.Menu):
    """Standard bay configurations - clears the bay and rebuilds it.
    Grouped with separators."""
    bl_label = "Bay Configuration"

    def draw(self, context):
        layout = self.layout
        from . import types_closets
        for gi, group in enumerate(types_closets.BAY_CONFIG_GROUPS):
            if gi > 0:
                layout.separator()
            for cid, label in group:
                op = layout.operator("hb_closets.change_bay", text=label)
                op.config = cid


class HOME_BUILDER_MT_closet_change_opening(bpy.types.Menu):
    """Swap one opening to a standard configuration. Grouped with
    separators."""
    bl_label = "Change Opening"

    def draw(self, context):
        layout = self.layout
        from . import types_closets
        for gi, group in enumerate(types_closets.OPENING_CONFIG_GROUPS):
            if gi > 0:
                layout.separator()
            for cid, label in group:
                op = layout.operator("hb_closets.change_opening", text=label)
                op.config = cid


class HOME_BUILDER_MT_closet_doors_drawers(bpy.types.Menu):
    """Add Doors & Drawers submenu. Door entries fire directly with the
    swing baked in, tilt-out hamper included (no dialog by design);
    Drawers keeps its small dialog for the quantity."""
    bl_label = "Add Doors & Drawers"

    def draw(self, context):
        layout = self.layout
        op = layout.operator("hb_closets.add_doors", text="Left Swing")
        op.swing = 'LEFT'
        op = layout.operator("hb_closets.add_doors", text="Right Swing")
        op.swing = 'RIGHT'
        op = layout.operator("hb_closets.add_doors", text="Double Door")
        op.swing = 'DOUBLE'
        op = layout.operator("hb_closets.add_doors",
                             text="Tilt Out Hamper")
        op.swing = 'TILT_OUT'
        layout.separator()
        layout.operator("hb_closets.add_drawers", text="Drawers...")


class HOME_BUILDER_MT_closet_part_commands(bpy.types.Menu):
    """Right-click menu for a user-added interior part. Adjustable
    shelves get Add/Remove Shelf on top of Delete Part."""
    bl_label = "Closet Part Commands"

    def draw(self, context):
        from . import types_closets
        layout = self.layout
        obj = context.active_object
        if (obj is not None and obj.get('hb_part_role')
                == types_closets.PART_ROLE_ADJ_SHELF):
            op = layout.operator("hb_closets.adj_shelf_step",
                                 text="Add Shelf", icon='ADD')
            op.delta = 1
            op = layout.operator("hb_closets.adj_shelf_step",
                                 text="Remove Shelf", icon='REMOVE')
            op.delta = -1
            layout.separator()
        if (obj is not None and obj.get('hb_part_role')
                == types_closets.PART_ROLE_MISC):
            layout.operator("hb_closets.misc_part_prompts",
                            text="Part Properties...", icon='WINDOW')
            layout.separator()
        if (obj is not None and obj.get('hb_part_role')
                == types_closets.PART_ROLE_CONTINUOUS_TOP):
            layout.operator("hb_closets.continuous_top_prompts",
                            text="Top Properties...", icon='WINDOW')
            layout.separator()
        if types_closets.find_accessory_cage(obj) is not None:
            layout.operator("hb_closets.accessory_prompts",
                            text="Accessory Properties...",
                            icon='WINDOW')
            layout.separator()
        if (obj is not None and obj.get('hb_part_role')
                in (types_closets.PART_ROLE_DOOR,
                    types_closets.PART_ROLE_DRAWER_FRONT)):
            layout.operator("hb_closets.front_style",
                            text="Front Style...", icon='SHADERFX')
        if (obj is not None and obj.get('hb_part_role')
                == types_closets.PART_ROLE_DRAWER_FRONT):
            layout.operator("hb_closets.drawer_accessory",
                            text="Drawer Options...", icon='MODIFIER')
            if obj.get(types_closets.PROP_JEWELRY_TRAY, ''):
                layout.operator("hb_closets.resize_drawer_for_tray",
                                text="Resize Drawer to Fit Tray",
                                icon='FULLSCREEN_ENTER')
            layout.separator()
        if (obj is not None and obj.get('hb_l_index') is not None
                and not obj.get('hb_l_carcass')):
            locked = bool(obj.get(types_closets.PROP_L_LOCKED))
            op = layout.operator(
                "hb_closets.lock_l_shelf",
                text="Unlock Shelf" if locked else "Lock Shelf",
                icon='DECORATE_UNLOCKED' if locked
                else 'DECORATE_LOCKED')
            op.lock = not locked
            layout.separator()
        layout.operator("hb_closets.delete_part",
                        text="Delete Part", icon='X')


classes = (
    HOME_BUILDER_MT_closet_starter_commands,
    HOME_BUILDER_MT_closet_hanger_commands,
    HOME_BUILDER_MT_closet_bay_commands,
    HOME_BUILDER_MT_closet_opening_commands,
    HOME_BUILDER_MT_closet_change_bay,
    HOME_BUILDER_MT_closet_change_opening,
    HOME_BUILDER_MT_closet_doors_drawers,
    HOME_BUILDER_MT_closet_accessories,
    HOME_BUILDER_MT_closet_accessories_opening,
    HOME_BUILDER_MT_closet_accessories_panel,
    HOME_BUILDER_MT_closet_accessories_insert,
    HOME_BUILDER_MT_closet_part_commands,
)

register, unregister = bpy.utils.register_classes_factory(classes)
