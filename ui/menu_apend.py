import bpy

from . import menus

def draw_object_mode_right_click_menu(self, context):
    layout = self.layout
    layout.operator_context = 'INVOKE_AREA'
    obj = context.object
    menu_id = ""
    if obj and "MENU_ID" in obj and obj["MENU_ID"] != "":
        menu_id = obj["MENU_ID"]

    # Annotation text carries no MENU_ID -- it is created in several
    # places and predates the per-object menu convention, so match on
    # the object instead. Notes already placed in a saved project pick
    # the commands up this way too.
    if not menu_id and menus.is_annotation_text(obj):
        menu_id = "HOME_BUILDER_MT_text_commands"

    # A reference image is Blender's own object -- it arrives by being
    # dragged into the viewport, so nothing of ours ever gets to stamp a
    # MENU_ID on it. Matched on the object for the same reason, which
    # also picks up images in projects saved before these commands
    # existed.
    if not menu_id and menus.is_reference_image(obj):
        menu_id = "HOME_BUILDER_MT_reference_image_commands"

    if menu_id and hasattr(bpy.types, menu_id):
        layout.menu(menu_id)
        layout.separator()


def register():
    bpy.types.VIEW3D_MT_object_context_menu.prepend(draw_object_mode_right_click_menu)  

def unregister():
    bpy.types.VIEW3D_MT_object_context_menu.remove(draw_object_mode_right_click_menu)   