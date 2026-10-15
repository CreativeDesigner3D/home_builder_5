"""Corbel placement and commands.

Placing a corbel is two steps: pick a style from a menu, then the
appliance placement modal drops a cage of that style's size (cursor
follow, wall snap, top at the base cabinet height). The style picked is
remembered on the scene for the next one.
"""

import bpy

from .... import hb_utils, hb_types
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
        layout.separator()
        layout.operator("hb_face_frame.delete_corbel", text="Delete Corbel")


classes = (
    HOME_BUILDER_MT_corbel_styles,
    HOME_BUILDER_MT_corbel_change_style,
    hb_face_frame_OT_place_corbel,
    hb_face_frame_OT_set_corbel_style,
    hb_face_frame_OT_delete_corbel,
    HOME_BUILDER_MT_corbel_commands,
)

register, unregister = bpy.utils.register_classes_factory(classes)
