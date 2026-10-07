"""Catalog action operators.

Single dispatch entry point: caffmob_catalog.activate_item takes an item_id,
looks up the entry, and calls the named action_operator with action_args
as kwargs. If the named operator doesn't exist (not yet implemented),
falls back to a graceful info notification.

caffmob_catalog.not_yet_implemented is a placeholder action that catalog
entries can wire to until their real operator is built.
"""
import bpy

from . import catalog_data


def _apply_global_assembly_config(context, obj):
    """Apply active global scene assembly configurations to a placed catalog item."""
    if obj is None:
        return
    from ..product_libraries.face_frame import types_face_frame
    root = types_face_frame.find_cabinet_root(obj) or obj

    if hasattr(root, 'face_frame_cabinet'):
        try:
            from ..product_libraries.face_frame import props_hb_face_frame
            props_hb_face_frame.ensure_default_styles(context)
            scene_props = props_hb_face_frame.get_style_props(context)
            idx = scene_props.active_cabinet_style_index
            if 0 <= idx < len(scene_props.cabinet_styles):
                scene_props.cabinet_styles[idx].assign_style_to_cabinet(root)
        except Exception:
            pass
    elif hasattr(root, 'hb_frameless'):
        try:
            from ..product_libraries.frameless import props_hb_frameless
            props_hb_frameless.ensure_default_styles(context)
            scene_props = props_hb_frameless.get_style_props(context)
            idx = scene_props.active_cabinet_style_index
            if 0 <= idx < len(scene_props.cabinet_styles):
                scene_props.cabinet_styles[idx].assign_style_to_cabinet(root)
        except Exception:
            pass


class hb_catalog_OT_activate_item(bpy.types.Operator):
    """Dispatch a catalog entry's action operator with its configured args."""
    bl_idname = "caffmob_catalog.activate_item"
    bl_label = "Activate Catalog Item"
    bl_options = {'REGISTER', 'UNDO'}

    item_id: bpy.props.StringProperty()  # type: ignore

    def execute(self, context):
        entry = catalog_data.find_entry(self.item_id)
        if entry is None:
            self.report({'WARNING'}, f"Unknown catalog item: {self.item_id}")
            return {'CANCELLED'}

        action_op = entry.get('action_operator', '') or ''
        if not action_op:
            self.report({'INFO'}, f"{entry['name']}: no action wired")
            return {'CANCELLED'}

        if '.' not in action_op:
            self.report({'ERROR'}, f"Bad action_operator format: {action_op}")
            return {'CANCELLED'}

        module_name, method_name = action_op.split('.', 1)
        try:
            op_module = getattr(bpy.ops, module_name)
            op = getattr(op_module, method_name)
        except AttributeError:
            # Fallback to standard draw_cabinet with global assembly configs
            bpy.ops.caffmob_face_frame.draw_cabinet('INVOKE_DEFAULT', cabinet_name='Base Door')
            _apply_global_assembly_config(context, context.active_object)
            return {'FINISHED'}

        kwargs = entry.get('action_args', {}) or {}
        try:
            op(**kwargs)
            _apply_global_assembly_config(context, context.active_object)
        except Exception as e:
            self.report({'ERROR'}, f"Failed to activate {entry['name']}: {e}")
            return {'CANCELLED'}

        return {'FINISHED'}


class hb_catalog_OT_not_yet_implemented(bpy.types.Operator):
    """Fallback action for catalog entries whose real operator isn't
    built yet. Places a standard face-frame cabinet and applies global assembly configs.
    """
    bl_idname = "caffmob_catalog.not_yet_implemented"
    bl_label = "Not Yet Implemented"
    bl_options = {'REGISTER', 'UNDO'}

    item_name: bpy.props.StringProperty(default="(unnamed)")  # type: ignore

    def execute(self, context):
        # Map item to face-frame draw_cabinet
        cab_name = 'Base Door'
        if 'Upper' in self.item_name or 'Wall' in self.item_name:
            cab_name = 'Upper'
        elif 'Tall' in self.item_name or 'Pantry' in self.item_name or 'Oven' in self.item_name:
            cab_name = 'Tall'
        bpy.ops.caffmob_face_frame.draw_cabinet('INVOKE_DEFAULT', cabinet_name=cab_name)
        _apply_global_assembly_config(context, context.active_object)
        return {'FINISHED'}






classes = (
    hb_catalog_OT_activate_item,
    hb_catalog_OT_not_yet_implemented,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
