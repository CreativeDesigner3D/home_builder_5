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


class HB_GENERAL_OT_delete(bpy.types.Operator):
    """HB5-aware delete: routes to the correct delete operator for the
    selected asset, falling back to Blender's object delete otherwise.

    Stock ``object.delete`` removes only the selected objects, which leaves
    orphaned children behind when the selection is an HB5 cage or part, and
    never runs the cleanup an HB5 asset needs (wall miter recompute,
    neighbor constraint removal, etc.). This operator classifies the active
    object and dispatches:

    - face frame cabinet  -> hb_face_frame.delete_cabinet
    - frameless cabinet   -> hb_frameless.delete_cabinet
    - frameless appliance -> hb_frameless.delete_appliance
    - door / window       -> home_builder_doors_windows.delete_door_window
    - wall                -> home_builder_walls.delete_wall
    - anything else       -> object.delete

    Each HB5 delete operator already sweeps ``selected_objects`` for its own
    kind, so multi-select delete (several cabinets, several walls) works
    without extra handling here - the active object only decides which kind
    is targeted. Mixed selections delete the active object's kind only.

    The cabinet, appliance, and door/window checks all run before the wall
    check on purpose: those assets sit in the wall's parent chain (a door
    or window BP is a direct child of the wall BP), so the wall test would
    otherwise misfire and delete the whole wall instead of the asset on it.

    Intended to be bound to the DEL key (3D View > Object Mode) in the
    user's keymap preferences.
    """
    bl_idname = "hb_general.delete"
    bl_label = "HB Delete"
    bl_description = "Delete the selected HB5 asset and all of its parts"
    bl_options = {'UNDO'}

    def execute(self, context):
        # Deferred imports: ops_general is imported before the product
        # libraries during addon registration, so importing these at module
        # scope would risk an early/circular import.
        from .. import hb_utils
        from ..product_libraries.face_frame import types_face_frame

        obj = context.active_object

        if types_face_frame.find_cabinet_root(obj) is not None:
            bpy.ops.hb_face_frame.delete_cabinet()
        elif hb_utils.get_cabinet_bp(obj) is not None:
            bpy.ops.hb_frameless.delete_cabinet()
        elif hb_utils.get_appliance_bp(obj) is not None:
            bpy.ops.hb_frameless.delete_appliance()
        elif obj and obj.get('IS_WINDOW_BP'):
            bpy.ops.home_builder_doors_windows.delete_door_window(
                object_type='WINDOW')
        elif obj and obj.get('IS_ENTRY_DOOR_BP'):
            bpy.ops.home_builder_doors_windows.delete_door_window(
                object_type='DOOR')
        elif obj and (obj.get('IS_WALL_BP')
                      or (obj.parent and obj.parent.get('IS_WALL_BP'))):
            bpy.ops.home_builder_walls.delete_wall()
        else:
            # Not an HB5 asset - stock delete with no confirm popup, matching
            # DEL's default behavior (X keeps its own stock confirm binding).
            bpy.ops.object.delete(confirm=False)

        return {'FINISHED'}


classes = (
    HB_MT_call_menu_wrapper,
    HB_GENERAL_OT_menu,
    HB_GENERAL_OT_delete,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
