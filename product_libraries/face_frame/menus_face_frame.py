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


class HOME_BUILDER_MT_face_frame_cabinet_commands(bpy.types.Menu):
    """Right-click menu for a face frame cabinet root."""
    bl_label = "Face Frame Cabinet Commands"

    def draw(self, context):
        layout = self.layout
        layout.operator("hb_face_frame.cabinet_prompts",
                        text="Cabinet Properties...", icon='WINDOW')
        layout.separator()
        layout.operator("hb_face_frame.recalculate_cabinet",
                        text="Recalculate", icon='FILE_REFRESH')
        layout.separator()
        layout.operator("hb_face_frame.delete_cabinet",
                        text="Delete Cabinet", icon='X')


class HOME_BUILDER_MT_face_frame_bay_commands(bpy.types.Menu):
    """Right-click menu for a face frame bay cage."""
    bl_label = "Face Frame Bay Commands"

    def draw(self, context):
        layout = self.layout
        layout.operator("hb_face_frame.bay_prompts",
                        text="Bay Properties...", icon='WINDOW')


class HOME_BUILDER_MT_face_frame_mid_stile_commands(bpy.types.Menu):
    """Right-click menu for a face frame mid stile part."""
    bl_label = "Face Frame Mid Stile Commands"

    def draw(self, context):
        layout = self.layout
        layout.operator("hb_face_frame.mid_stile_prompts",
                        text="Mid Stile Properties...", icon='WINDOW')


class HOME_BUILDER_MT_face_frame_opening_commands(bpy.types.Menu):
    """Right-click menu for a face frame opening cage."""
    bl_label = "Face Frame Opening Commands"

    def draw(self, context):
        layout = self.layout
        layout.operator("hb_face_frame.opening_prompts",
                        text="Opening Properties...", icon='WINDOW')
        layout.separator()
        op = layout.operator("hb_face_frame.split_opening",
                             text="Split Horizontal", icon='SNAP_EDGE')
        op.axis = 'H'
        op = layout.operator("hb_face_frame.split_opening",
                             text="Split Vertical", icon='PAUSE')
        op.axis = 'V' 


classes = (
    HOME_BUILDER_MT_face_frame_cabinet_commands,
    HOME_BUILDER_MT_face_frame_bay_commands,
    HOME_BUILDER_MT_face_frame_mid_stile_commands,
    HOME_BUILDER_MT_face_frame_opening_commands,
)


register, unregister = bpy.utils.register_classes_factory(classes)
