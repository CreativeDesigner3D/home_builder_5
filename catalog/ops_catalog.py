"""Catalog action operators.

Single dispatch entry point: hb_catalog.activate_item takes an item_id,
looks up the entry, and calls the named action_operator with action_args
as kwargs. If the named operator doesn't exist (not yet implemented),
falls back to a graceful info notification.

hb_catalog.not_yet_implemented is a placeholder action that catalog
entries can wire to until their real operator is built.
"""
import bpy

from . import catalog_data


class hb_catalog_OT_activate_item(bpy.types.Operator):
    """Dispatch a catalog entry's action operator with its configured args."""
    bl_idname = "hb_catalog.activate_item"
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
            self.report({'INFO'},
                        f"{entry['name']}: operator '{action_op}' not implemented yet")
            return {'CANCELLED'}

        kwargs = entry.get('action_args', {}) or {}
        try:
            op(**kwargs)
        except Exception as e:
            self.report({'ERROR'}, f"Failed to activate {entry['name']}: {e}")
            return {'CANCELLED'}

        return {'FINISHED'}


class hb_catalog_OT_not_yet_implemented(bpy.types.Operator):
    """Placeholder action for catalog entries whose real operator isn't
    wired up yet. Reports an info message identifying which item was
    activated. Replace each entry's action_operator with the real
    bl_idname as those operators land.
    """
    bl_idname = "hb_catalog.not_yet_implemented"
    bl_label = "Not Yet Implemented"
    bl_options = {'REGISTER'}

    item_name: bpy.props.StringProperty(default="(unnamed)")  # type: ignore

    def execute(self, context):
        self.report({'INFO'}, f"{self.item_name}: not yet implemented")
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
