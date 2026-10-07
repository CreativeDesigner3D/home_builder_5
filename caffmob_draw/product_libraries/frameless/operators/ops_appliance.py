import bpy
from .... import hb_utils, hb_types

class hb_frameless_OT_appliance_prompts(bpy.types.Operator):
    bl_idname = "caffmob_frameless.appliance_prompts"
    bl_label = "Appliance Prompts"
    bl_description = "Edit appliance properties"
    bl_options = {'UNDO'}

    appliance_width: bpy.props.FloatProperty(name="Width", unit='LENGTH', precision=5) # type: ignore
    appliance_height: bpy.props.FloatProperty(name="Height", unit='LENGTH', precision=5) # type: ignore
    appliance_depth: bpy.props.FloatProperty(name="Depth", unit='LENGTH', precision=5) # type: ignore

    appliance = None

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj:
            appliance_bp = hb_utils.get_appliance_bp(obj)
            return appliance_bp is not None
        return False

    def invoke(self, context, event):
        appliance_bp = hb_utils.get_appliance_bp(context.object)
        self.appliance = hb_types.GeoNodeCage(appliance_bp)
        self.appliance_width = self.appliance.get_input('Dim X')
        self.appliance_height = self.appliance.get_input('Dim Z')
        self.appliance_depth = self.appliance.get_input('Dim Y')
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def check(self, context):
        self.appliance.set_input('Dim X', self.appliance_width)
        self.appliance.set_input('Dim Z', self.appliance_height)
        self.appliance.set_input('Dim Y', self.appliance_depth)
        return True

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)

        row = col.row(align=True)
        row.label(text="Width:")
        row.prop(self, 'appliance_width', text="")

        row = col.row(align=True)
        row.label(text="Height:")
        row.prop(self, 'appliance_height', text="")

        row = col.row(align=True)
        row.label(text="Depth:")
        row.prop(self, 'appliance_depth', text="")


class hb_frameless_OT_delete_appliance(bpy.types.Operator):
    bl_idname = "caffmob_frameless.delete_appliance"
    bl_label = "Delete Appliance"
    bl_description = "Delete the selected appliance"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj:
            appliance_bp = hb_utils.get_appliance_bp(obj)
            return appliance_bp is not None
        return False

    def execute(self, context):
        appliance_bp = hb_utils.get_appliance_bp(context.object)
        hb_utils.delete_obj_and_children(appliance_bp)
        return {'FINISHED'}


classes = (
    hb_frameless_OT_appliance_prompts,
    hb_frameless_OT_delete_appliance,
)

def register():
    for cls in classes:
        reg_cls = (cls if cls.is_registered else getattr(bpy.types, cls.__name__, None))
        if reg_cls:
            try:
                bpy.utils.unregister_class(reg_cls)
            except Exception:
                pass
        try:
            bpy.utils.register_class(cls)
        except Exception:
            pass


def unregister():
    for cls in reversed(classes):
        reg_cls = (cls if cls.is_registered else getattr(bpy.types, cls.__name__, None))
        if reg_cls:
            try:
                bpy.utils.unregister_class(reg_cls)
            except Exception:
                pass
