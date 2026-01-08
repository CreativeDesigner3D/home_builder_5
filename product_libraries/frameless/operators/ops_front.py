import bpy
from .. import types_frameless
from .. import props_hb_frameless
from .... import hb_utils, units

class hb_frameless_OT_door_front_prompts(bpy.types.Operator):
    bl_idname = "hb_frameless.door_front_prompts"
    bl_label = "Front Prompts"
    bl_description = "Edit door/drawer front properties"
    bl_options = {'UNDO'}

    top_overlay: bpy.props.FloatProperty(name="Top Overlay", unit='LENGTH', precision=5) # type: ignore
    bottom_overlay: bpy.props.FloatProperty(name="Bottom Overlay", unit='LENGTH', precision=5) # type: ignore
    left_overlay: bpy.props.FloatProperty(name="Left Overlay", unit='LENGTH', precision=5) # type: ignore
    right_overlay: bpy.props.FloatProperty(name="Right Overlay", unit='LENGTH', precision=5) # type: ignore

    front = None

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and 'IS_CABINET_FRONT' in obj

    def invoke(self, context, event):
        self.front = context.object
        self.top_overlay = self.front.get('Top Overlay', 0)
        self.bottom_overlay = self.front.get('Bottom Overlay', 0)
        self.left_overlay = self.front.get('Left Overlay', 0)
        self.right_overlay = self.front.get('Right Overlay', 0)
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def check(self, context):
        # Note: These are usually driven, so direct setting may not work
        # This is a starting point - may need to modify overlay prompt obj instead
        return True

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)
        
        row = col.row(align=True)
        row.label(text="Top Overlay:")
        row.prop(self, 'top_overlay', text="")
        
        row = col.row(align=True)
        row.label(text="Bottom Overlay:")
        row.prop(self, 'bottom_overlay', text="")
        
        row = col.row(align=True)
        row.label(text="Left Overlay:")
        row.prop(self, 'left_overlay', text="")
        
        row = col.row(align=True)
        row.label(text="Right Overlay:")
        row.prop(self, 'right_overlay', text="")


class hb_frameless_OT_delete_front(bpy.types.Operator):
    bl_idname = "hb_frameless.delete_front"
    bl_label = "Delete Front"
    bl_description = "Delete this door or drawer front"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and 'IS_CABINET_FRONT' in obj

    def execute(self, context):
        front = context.object
        hb_utils.delete_obj_and_children(front)
        return {'FINISHED'}


classes = (
    hb_frameless_OT_door_front_prompts,
    hb_frameless_OT_delete_front,
)

register, unregister = bpy.utils.register_classes_factory(classes)
