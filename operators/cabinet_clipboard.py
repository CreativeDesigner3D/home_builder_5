"""Copy a cabinet and paste it into any room.

Copy remembers the cabinet; Paste starts the library's own
duplicate-and-place command on it in whatever room is open, so the copy
keeps its bays, fronts, interiors and style and is placed with the usual
wall snapping, gap fill and typed widths. The cabinet is only read when
it is pasted, so later edits to it show up in the next paste.
"""

import bpy

from .. import hb_utils


# Name of the copied cabinet's root object; '' when nothing is copied.
_clipboard_name = ''


def _face_frame_root(obj):
    while obj is not None:
        if obj.get('IS_FACE_FRAME_CABINET_CAGE'):
            return obj
        obj = obj.parent
    return None


def copyable_root(obj):
    """(root, library) for the cabinet ``obj`` belongs to, or (None, None).

    Only cabinets the libraries can duplicate-and-place qualify: face
    frame corner cabinets place through a different command and are left
    out, as they are from Duplicate.
    """
    root = _face_frame_root(obj)
    if root is not None:
        props = getattr(root, 'face_frame_cabinet', None)
        if getattr(props, 'corner_type', 'NONE') != 'NONE':
            return None, None
        return root, 'FACE_FRAME'
    root = hb_utils.get_cabinet_bp(obj)
    if root is not None and root.get('IS_FRAMELESS_CABINET_CAGE'):
        return root, 'FRAMELESS'
    return None, None


def copied_cabinet():
    """(root, library) of the copied cabinet, or (None, None) when nothing
    is copied or it has since been deleted."""
    if not _clipboard_name:
        return None, None
    obj = bpy.data.objects.get(_clipboard_name)
    if obj is None:
        return None, None
    return copyable_root(obj)


class home_builder_OT_copy_cabinet(bpy.types.Operator):
    bl_idname = "home_builder.copy_cabinet"
    bl_label = "Copy Cabinet"
    bl_description = ("Copy this cabinet so it can be pasted into any "
                      "room, with all of its settings")

    @classmethod
    def poll(cls, context):
        return copyable_root(context.object)[0] is not None

    def execute(self, context):
        global _clipboard_name
        root, _library = copyable_root(context.object)
        if root is None:
            return {'CANCELLED'}
        _clipboard_name = root.name
        self.report({'INFO'}, f"Copied {root.name}. Right-click in any "
                              "room and choose Paste Cabinet")
        return {'FINISHED'}


class home_builder_OT_paste_cabinet(bpy.types.Operator):
    bl_idname = "home_builder.paste_cabinet"
    bl_label = "Paste Cabinet"
    bl_description = ("Place a copy of the copied cabinet in this room, "
                      "on any wall")

    @classmethod
    def poll(cls, context):
        if not hb_utils.is_room_scene(context.scene):
            return False
        return copied_cabinet()[0] is not None

    def invoke(self, context, event):
        root, library = copied_cabinet()
        if root is None:
            self.report({'WARNING'}, "The copied cabinet no longer exists")
            return {'CANCELLED'}
        # The placement modal runs on its own from here; this command is
        # done once it has started.
        if library == 'FACE_FRAME':
            result = bpy.ops.hb_face_frame.place_cabinet(
                'INVOKE_DEFAULT', source_cabinet_name=root.name)
        else:
            result = bpy.ops.hb_frameless.duplicate_cabinet(
                'INVOKE_DEFAULT', source_name=root.name)
        if result & {'RUNNING_MODAL', 'FINISHED'}:
            return {'FINISHED'}
        return {'CANCELLED'}

    def execute(self, context):
        return self.invoke(context, None)


def draw_paste_item(layout, context):
    """Paste Cabinet in the viewport right-click menu, naming the copied
    cabinet. Returns True when something was drawn."""
    if not home_builder_OT_paste_cabinet.poll(context):
        return False
    root, _library = copied_cabinet()
    layout.operator(home_builder_OT_paste_cabinet.bl_idname,
                    text=f"Paste Cabinet ({root.name})", icon='PASTEDOWN')
    return True


classes = (
    home_builder_OT_copy_cabinet,
    home_builder_OT_paste_cabinet,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
