"""Corbel placement and commands.

Placing a corbel is two steps: pick a style from a menu, then the
appliance placement modal drops a cage of that style's size (cursor
follow, wall snap, top at the base cabinet height). The style picked is
remembered on the scene for the next one.
"""

import bpy

from .... import hb_utils, hb_types, hb_placement
from ...common import corbels
from . import ops_placement


def _corbel_root(obj):
    while obj is not None:
        if obj.get(corbels.CORBEL_TAG):
            return obj
        obj = obj.parent
    return None


def _selected_corbels(context):
    roots = []
    for obj in list(context.selected_objects) + [context.active_object]:
        root = _corbel_root(obj)
        if root is not None and root not in roots:
            roots.append(root)
    return roots


def _draw_style_list(layout, op_idname, current=None):
    """Every style as a menu row, grouped by vendor, size on the right of
    the name. ``current`` gets a check mark."""
    for gi, (group, items) in enumerate(corbels.grouped_styles()):
        if gi:
            layout.separator()
        layout.label(text=group)
        for s in items:
            op = layout.operator(
                op_idname,
                text="%s    %s" % (s['label'], corbels.size_text(s)),
                icon='CHECKMARK' if s['key'] == current else 'BLANK1')
            op.style = s['key']


class HOME_BUILDER_MT_corbel_styles(bpy.types.Menu):
    """The style picker the Corbel tile opens."""
    bl_label = "Corbel"

    def draw(self, context):
        _draw_style_list(self.layout, "hb_face_frame.place_corbel",
                         context.scene.get(
                             ops_placement.CORBEL_STYLE_SCENE_KEY))


class HOME_BUILDER_MT_corbel_change_style(bpy.types.Menu):
    bl_label = "Change Style"

    def draw(self, context):
        root = _corbel_root(context.active_object)
        _draw_style_list(self.layout, "hb_face_frame.set_corbel_style",
                         root.get(corbels.STYLE_PROP) if root else None)


class hb_face_frame_OT_place_corbel(bpy.types.Operator):
    """Place a corbel. Without a style, opens the style menu"""
    bl_idname = "hb_face_frame.place_corbel"
    bl_label = "Place Corbel"

    style: bpy.props.StringProperty(name="Style", default="")  # type: ignore

    def invoke(self, context, event):
        if self.style:
            return self.execute(context)
        # The library tiles act on the mouse PRESS. A menu opened there
        # takes the release that follows as its pick and closes, so the
        # menu only stayed up while the button was held. Wait for the
        # release, then open it.
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        bpy.ops.wm.call_menu(name=HOME_BUILDER_MT_corbel_styles.__name__)
        return {'FINISHED'}

    def modal(self, context, event):
        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            bpy.ops.wm.call_menu(name=HOME_BUILDER_MT_corbel_styles.__name__)
            return {'FINISHED'}
        if event.type in {'ESC', 'RIGHTMOUSE'}:
            return {'CANCELLED'}
        return {'RUNNING_MODAL'}

    def execute(self, context):
        if corbels.find_style(self.style) is None:
            return {'CANCELLED'}
        context.scene[ops_placement.CORBEL_STYLE_SCENE_KEY] = self.style
        bpy.ops.hb_face_frame.place_appliance(
            'INVOKE_DEFAULT', appliance_name="Corbel")
        return {'FINISHED'}


class hb_face_frame_OT_set_corbel_style(bpy.types.Operator):
    """Change the style of the selected corbels"""
    bl_idname = "hb_face_frame.set_corbel_style"
    bl_label = "Corbel Style"
    bl_options = {'REGISTER', 'UNDO'}

    style: bpy.props.StringProperty(name="Style", default="")  # type: ignore

    @classmethod
    def poll(cls, context):
        return _corbel_root(context.active_object) is not None

    def execute(self, context):
        if corbels.find_style(self.style) is None:
            return {'CANCELLED'}
        for root in _selected_corbels(context):
            # Keep the top where it was: a corbel hangs from the surface
            # it supports.
            top = (root.location.z
                   + hb_types.GeoNodeCage(root).get_input('Dim Z'))
            corbels.apply_style(root, self.style)
            _w, h, _d = corbels.Corbel.size_for(self.style)
            root.location.z = top - h
        context.scene[ops_placement.CORBEL_STYLE_SCENE_KEY] = self.style
        return {'FINISHED'}


class hb_face_frame_OT_duplicate_corbel_place(bpy.types.Operator):
    """Place a copy of this corbel on any wall or cabinet"""
    bl_idname = "hb_face_frame.duplicate_corbel_place"
    bl_label = "Duplicate Corbel"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return _corbel_root(context.active_object) is not None

    def invoke(self, context, event):
        root = _corbel_root(context.active_object)
        bpy.ops.hb_face_frame.place_appliance(
            'INVOKE_DEFAULT', appliance_name="Corbel", source_name=root.name)
        return {'FINISHED'}


class hb_face_frame_OT_duplicate_corbel(bpy.types.Operator):
    """Duplicate the selected corbels, body and all, and move the copies"""
    bl_idname = "hb_face_frame.duplicate_corbel"
    bl_label = "Duplicate Corbels"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        # Only when everything selected is a corbel. Otherwise the poll
        # fails and Shift+D falls through to Blender's own duplicate.
        if context.mode != 'OBJECT':
            return False
        sel = context.selected_objects
        return bool(sel) and all(_corbel_root(o) is not None for o in sel)

    def invoke(self, context, event):
        roots = _selected_corbels(context)
        copies = []
        for root in roots:
            new = hb_placement.duplicate_object_hierarchy(context, root)
            if new is not None:
                copies.append(new)
        if not copies:
            return {'CANCELLED'}
        bpy.ops.object.select_all(action='DESELECT')
        for new in copies:
            new.select_set(True)
        context.view_layer.objects.active = copies[-1]
        # The same grab Blender's Shift+D starts.
        bpy.ops.transform.translate('INVOKE_DEFAULT')
        return {'FINISHED'}


class hb_face_frame_OT_delete_corbel(bpy.types.Operator):
    """Delete the selected corbels"""
    bl_idname = "hb_face_frame.delete_corbel"
    bl_label = "Delete Corbel"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return _corbel_root(context.active_object) is not None

    def execute(self, context):
        for root in _selected_corbels(context):
            hb_utils.delete_obj_and_children(root)
        return {'FINISHED'}


class HOME_BUILDER_MT_corbel_commands(bpy.types.Menu):
    bl_label = "Corbel Commands"

    def draw(self, context):
        layout = self.layout
        root = _corbel_root(context.active_object)
        if root is not None:
            layout.label(text=root.get(corbels.LABEL_PROP, "Corbel"))
            layout.separator()
        layout.menu(HOME_BUILDER_MT_corbel_change_style.__name__,
                    icon='MOD_BEVEL')
        layout.operator("hb_face_frame.duplicate_corbel_place",
                        text="Duplicate", icon='DUPLICATE')
        layout.separator()
        layout.operator("hb_face_frame.delete_corbel", text="Delete Corbel")


classes = (
    HOME_BUILDER_MT_corbel_styles,
    HOME_BUILDER_MT_corbel_change_style,
    hb_face_frame_OT_place_corbel,
    hb_face_frame_OT_set_corbel_style,
    hb_face_frame_OT_duplicate_corbel_place,
    hb_face_frame_OT_duplicate_corbel,
    hb_face_frame_OT_delete_corbel,
    HOME_BUILDER_MT_corbel_commands,
)

_register_classes, _unregister_classes = bpy.utils.register_classes_factory(
    classes)

# Shift+D on a corbel copies the whole corbel. The stock duplicate only
# copies what is selected -- the cage -- and leaves the body behind.
_addon_keymaps = []


def register():
    _register_classes()
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='Object Mode', space_type='EMPTY')
        kmi = km.keymap_items.new(hb_face_frame_OT_duplicate_corbel.bl_idname,
                                  'D', 'PRESS', shift=True)
        _addon_keymaps.append((km, kmi))


def unregister():
    for km, kmi in _addon_keymaps:
        try:
            km.keymap_items.remove(kmi)
        except Exception:
            pass
    _addon_keymaps.clear()
    _unregister_classes()
