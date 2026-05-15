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
from .operators import ops_part_commands
from ... import units


class HOME_BUILDER_MT_face_frame_cabinet_commands(bpy.types.Menu):
    """Right-click menu for a face frame cabinet root."""
    bl_label = "Face Frame Cabinet Commands"

    def draw(self, context):
        layout = self.layout
        layout.operator("hb_face_frame.cabinet_prompts",
                        text="Cabinet Properties...", icon='WINDOW')
        layout.operator("hb_face_frame.grab_cabinet",
                        text="Grab Cabinet", icon='OBJECT_ORIGIN')
        layout.operator("hb_face_frame.grab_face_frame",
                        text="Grab Face Frame", icon='MOD_EDGESPLIT')
        layout.separator()
        layout.operator("hb_face_frame.open_mode",
                        text="Open Mode", icon='MOD_BOOLEAN')
        layout.separator()
        layout.operator("hb_face_frame.join_cabinets",
                        text="Join Cabinets", icon='AUTOMERGE_ON')

        # Show "Create Cabinet Group" only when more than one cabinet is
        # in the selection - grouping a single cabinet is rarely useful.
        # find_cabinet_root walks any selected part up to its root, so the
        # menu surfaces correctly whether the user picked roots, bays, or
        # individual face frame parts.
        selected_roots = set()
        for obj in context.selected_objects:
            root = types_face_frame.find_cabinet_root(obj)
            if root is not None:
                selected_roots.add(root.name)
        if len(selected_roots) > 1:
            layout.operator("hb_face_frame.create_cabinet_group",
                            text="Create Cabinet Group", icon='ADD')

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
        op = layout.operator("hb_face_frame.delete_bay",
                             text="Delete Bay", icon='X')
        op.bay_index = bay_index

        layout.separator()
        layout.operator("hb_face_frame.break_cabinet_left",
                        text="Break Left", icon='TRIA_LEFT_BAR')
        layout.operator("hb_face_frame.break_cabinet_right",
                        text="Break Right", icon='TRIA_RIGHT_BAR')
        layout.operator("hb_face_frame.break_cabinet_both",
                        text="Break Both", icon='UNLINKED')

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

        # Width applies to every face frame part. Label includes the
        # current value so the user can read it without opening the popup.
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

        # Stile-to-floor is end-stile only.
        if role in (types_face_frame.PART_ROLE_LEFT_STILE,
                    types_face_frame.PART_ROLE_RIGHT_STILE):
            layout.operator("hb_face_frame.toggle_stile_to_floor",
                            text="Toggle Stile to Floor",
                            icon='TRIA_DOWN_BAR')

        # Mid stiles keep their deeper properties popup (extend up /
        # down) as an additional item.
        if role == types_face_frame.PART_ROLE_MID_STILE:
            layout.separator()
            layout.operator("hb_face_frame.mid_stile_prompts",
                            text="Mid Stile Properties...", icon='WINDOW')


class HOME_BUILDER_MT_face_frame_opening_commands(bpy.types.Menu):
    """Right-click menu for a face frame opening cage."""
    bl_label = "Face Frame Opening Commands"

    def draw(self, context):
        layout = self.layout
        layout.operator("hb_face_frame.opening_prompts",
                        text="Opening Properties...", icon='WINDOW')
        layout.menu("HOME_BUILDER_MT_face_frame_change_opening",
                    text="Change Opening")
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

    # (config_value, display_text). Order matches the user-facing list.
    ENTRIES = [
        ('OPEN',              "Open"),
        ('OPEN_WITH_SHELVES', "Open with Shelves"),
        ('LEFT_DOOR',         "Left Door"),
        ('RIGHT_DOOR',        "Right Door"),
        ('DOUBLE_DOOR',       "Double Door"),
        ('FLIP_UP_DOOR',      "Flip Up Door"),
        ('FLIP_DOWN_DOOR',    "Flip Down Door"),
        ('DRAWER',            "Drawer"),
        ('PULLOUT',           "Pullout"),
        ('INSET_PANEL',       "Inset Panel"),
        ('FALSE_FRONT',       "False Front"),
        ('APPLIANCE',         "Appliance"),
    ]

    def draw(self, context):
        layout = self.layout
        for config, label in self.ENTRIES:
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
            config, label = entry
            op = layout.operator("hb_face_frame.change_bay", text=label)
            op.config = config


classes = (
    HOME_BUILDER_MT_face_frame_cabinet_commands,
    HOME_BUILDER_MT_face_frame_cabinet_group_commands,
    HOME_BUILDER_MT_face_frame_bay_commands,
    HOME_BUILDER_MT_face_frame_part_commands,
    HOME_BUILDER_MT_face_frame_opening_commands,
    HOME_BUILDER_MT_face_frame_change_opening,
    HOME_BUILDER_MT_face_frame_change_bay,
)


register, unregister = bpy.utils.register_classes_factory(classes)
