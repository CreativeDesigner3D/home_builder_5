"""General-purpose operators for the addon (cross-library utilities)."""

import bpy


class HB_MT_call_menu_wrapper(bpy.types.Menu):
    """Wrapper menu that forces INVOKE_DEFAULT on its contents.

    Blender popup menus invoked via wm.call_menu run their items under an
    EXEC_* operator context by default. Operators that rely on invoke()
    (props dialogs, modal placement, search popups) silently no-op in that
    context - execute() returns {'FINISHED'} without ever popping the UI.

    Inlining the target menu via layout.menu_contents() lets us set the
    layout's operator_context once on the wrapper. The inner menu's draw()
    runs against our layout, so every layout.operator(...) call inside
    inherits INVOKE_DEFAULT - no per-menu patching required.
    """
    bl_idname = "HB_MT_call_menu_wrapper"
    bl_label = "HB Menu"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'
        obj = context.object
        if (obj and "MENU_ID" in obj and obj["MENU_ID"]
                and hasattr(bpy.types, obj["MENU_ID"])):
            layout.menu_contents(obj["MENU_ID"])


class HB_GENERAL_OT_menu(bpy.types.Operator):
    """Pops the context menu for the active HB5 asset.

    Reads the ``MENU_ID`` custom property off the active object and pops a
    wrapper menu that inlines that target. The wrapper exists to force an
    INVOKE_DEFAULT operator context on the inner menu's items.

    Falls back to Blender's default object context menu when no HB5 asset
    is active so right-click is never dead.

    Intended to be bound to RIGHTMOUSE (3D View > Object Mode) in the
    user's keymap preferences.
    """
    bl_idname = "hb_general.menu"
    bl_label = "HB Menu"
    bl_description = "Open the context menu for the selected HB5 asset"
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        obj = context.object
        menu_id = ""
        if obj and "MENU_ID" in obj and obj["MENU_ID"]:
            menu_id = obj["MENU_ID"]

        if menu_id and hasattr(bpy.types, menu_id):
            bpy.ops.wm.call_menu('INVOKE_DEFAULT',
                                 name="HB_MT_call_menu_wrapper")
        else:
            # No HB5 menu on the active object - fall through to the
            # native context menu so RMB still works on stock Blender
            # objects, empties, etc.
            bpy.ops.wm.call_menu('INVOKE_DEFAULT',
                                 name="VIEW3D_MT_object_context_menu")

        return {'FINISHED'}


classes = (
    HB_MT_call_menu_wrapper,
    HB_GENERAL_OT_menu,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
