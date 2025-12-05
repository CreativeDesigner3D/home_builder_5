import bpy

def draw_object_mode_right_click_menu(self, context):
    layout = self.layout
    layout.operator_context = 'INVOKE_AREA'
    obj = context.object
    menu_id = ""
    if obj and "MENU_ID" in obj and obj["MENU_ID"] != "":
        menu_id = obj["MENU_ID"]

    if menu_id and hasattr(bpy.types, menu_id):
        layout.menu(menu_id)
        layout.separator()


def register():
    bpy.types.VIEW3D_MT_object_context_menu.prepend(draw_object_mode_right_click_menu)  

def unregister():
    bpy.types.VIEW3D_MT_object_context_menu.remove(draw_object_mode_right_click_menu)   