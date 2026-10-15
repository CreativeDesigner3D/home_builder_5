"""Corbel placement and commands.

Placing a corbel is two steps: pick a style from a search list, then the
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


class hb_face_frame_OT_place_corbel(bpy.types.Operator):
    """Pick a corbel style, then place it"""
    bl_idname = "hb_face_frame.place_corbel"
    bl_label = "Place Corbel"
    bl_property = "style"

    style: bpy.props.EnumProperty(
        name="Style", items=corbels.style_enum_items)  # type: ignore

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        if self.style == 'NONE':
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
    bl_property = "style"

    style: bpy.props.EnumProperty(
        name="Style", items=corbels.style_enum_items)  # type: ignore

    @classmethod
    def poll(cls, context):
        return _corbel_root(context.active_object) is not None

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        if self.style == 'NONE':
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
        layout.operator("hb_face_frame.set_corbel_style",
                        text="Change Style...", icon='MOD_BEVEL')
        layout.separator()
        layout.operator("hb_face_frame.delete_corbel", text="Delete Corbel")


classes = (
    hb_face_frame_OT_place_corbel,
    hb_face_frame_OT_set_corbel_style,
    hb_face_frame_OT_delete_corbel,
    HOME_BUILDER_MT_corbel_commands,
)

register, unregister = bpy.utils.register_classes_factory(classes)
