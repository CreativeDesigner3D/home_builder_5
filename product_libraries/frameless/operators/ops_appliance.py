import bpy
from .. import types_frameless
from .. import props_hb_frameless
from .... import hb_utils, hb_types, units

class hb_frameless_OT_appliance_prompts(bpy.types.Operator):
    bl_idname = "hb_frameless.appliance_prompts"
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


class hb_frameless_OT_set_appliance_label(bpy.types.Operator):
    """Rename the annotation label drawn on an appliance cage (e.g. a
    generic under-counter appliance labeled BEV CENTER / WINE FRIDGE /
    ICE MAKER). Rewrites the cage's text child and the stored
    APPLIANCE_LABEL."""
    bl_idname = "hb_frameless.set_appliance_label"
    bl_label = "Set Appliance Label"
    bl_description = "Rename the label drawn on this appliance"
    bl_options = {'UNDO'}

    label_text: bpy.props.StringProperty(name="Label", default="") # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj:
            return hb_utils.get_appliance_bp(obj) is not None
        return False

    def invoke(self, context, event):
        bp = hb_utils.get_appliance_bp(context.object)
        self.label_text = (bp.get('APPLIANCE_LABEL')
                           or bp.get('APPLIANCE_TYPE') or "")
        return context.window_manager.invoke_props_dialog(self, width=280)

    def draw(self, context):
        self.layout.prop(self, 'label_text')

    def execute(self, context):
        bp = hb_utils.get_appliance_bp(context.object)
        text = self.label_text.strip()
        if not text:
            return {'CANCELLED'}
        bp['APPLIANCE_LABEL'] = text
        for child in bp.children:
            if child.get('IS_APPLIANCE_TEXT') and child.type == 'FONT':
                child.data.body = text
        return {'FINISHED'}


class hb_frameless_OT_delete_appliance(bpy.types.Operator):
    bl_idname = "hb_frameless.delete_appliance"
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
    hb_frameless_OT_set_appliance_label,
    hb_frameless_OT_delete_appliance,
)

register, unregister = bpy.utils.register_classes_factory(classes)
