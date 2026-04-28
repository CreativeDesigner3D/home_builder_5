"""Right-click context menus for face frame cabinets, bays, and openings.

The right-click handler in ui/menu_apend.py reads obj['MENU_ID'] from the
active object and shows the named Menu class. Each face-frame-tagged cage
sets its MENU_ID to one of the menu classes defined here.
"""
import bpy


class HOME_BUILDER_MT_face_frame_cabinet_commands(bpy.types.Menu):
    """Right-click menu for a face frame cabinet root."""
    bl_label = "Face Frame Cabinet Commands"

    def draw(self, context):
        layout = self.layout
        layout.operator("hb_face_frame.cabinet_prompts",
                        text="Cabinet Properties", icon='WINDOW')
        layout.separator()
        layout.operator("hb_face_frame.recalculate_cabinet",
                        text="Recalculate", icon='FILE_REFRESH')


class HOME_BUILDER_MT_face_frame_bay_commands(bpy.types.Menu):
    """Right-click menu for a face frame bay cage.

    Phase 3a stub. Phase 3b expands this with bay configuration commands
    (split opening, change opening type, etc.) once bays are real.
    """
    bl_label = "Face Frame Bay Commands"

    def draw(self, context):
        layout = self.layout
        layout.label(text="Bay commands coming in Phase 3b", icon='INFO')


classes = (
    HOME_BUILDER_MT_face_frame_cabinet_commands,
    HOME_BUILDER_MT_face_frame_bay_commands,
)


register, unregister = bpy.utils.register_classes_factory(classes)
