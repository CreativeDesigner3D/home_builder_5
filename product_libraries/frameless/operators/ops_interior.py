import bpy
from .. import types_frameless
from .. import props_hb_frameless
from .... import hb_utils, hb_types, units

class hb_frameless_OT_interior_prompts(bpy.types.Operator):
    bl_idname = "hb_frameless.interior_prompts"
    bl_label = "Interior Prompts"
    bl_description = "Edit interior properties"
    bl_options = {'UNDO'}

    shelf_quantity: bpy.props.IntProperty(name="Shelf Quantity", min=0, max=10, default=1) # type: ignore
    shelf_setback: bpy.props.FloatProperty(name="Shelf Setback", unit='LENGTH', precision=5) # type: ignore
    shelf_clip_gap: bpy.props.FloatProperty(name="Shelf Clip Gap", unit='LENGTH', precision=5) # type: ignore

    interior = None

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj:
            interior_bp = hb_utils.get_interior_bp(obj)
            return interior_bp is not None
        return False

    def invoke(self, context, event):
        interior_bp = hb_utils.get_interior_bp(context.object)
        self.interior = hb_types.GeoNodeCage(interior_bp)
        
        if 'Shelf Quantity' in interior_bp:
            self.shelf_quantity = interior_bp['Shelf Quantity']
        if 'Shelf Setback' in interior_bp:
            self.shelf_setback = interior_bp['Shelf Setback']
        if 'Shelf Clip Gap' in interior_bp:
            self.shelf_clip_gap = interior_bp['Shelf Clip Gap']
        
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def check(self, context):
        if 'Shelf Quantity' in self.interior.obj:
            self.interior.obj['Shelf Quantity'] = self.shelf_quantity
        if 'Shelf Setback' in self.interior.obj:
            self.interior.obj['Shelf Setback'] = self.shelf_setback
        if 'Shelf Clip Gap' in self.interior.obj:
            self.interior.obj['Shelf Clip Gap'] = self.shelf_clip_gap
        hb_utils.run_calc_fix(context, self.interior.obj)
        return True

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)
        
        if 'Shelf Quantity' in self.interior.obj:
            row = col.row(align=True)
            row.label(text="Shelf Quantity:")
            row.prop(self, 'shelf_quantity', text="")
        
        if 'Shelf Setback' in self.interior.obj:
            row = col.row(align=True)
            row.label(text="Shelf Setback:")
            row.prop(self, 'shelf_setback', text="")
        
        if 'Shelf Clip Gap' in self.interior.obj:
            row = col.row(align=True)
            row.label(text="Shelf Clip Gap:")
            row.prop(self, 'shelf_clip_gap', text="")


class hb_frameless_OT_change_interior_type(bpy.types.Operator):
    bl_idname = "hb_frameless.change_interior_type"
    bl_label = "Change Interior Type"
    bl_description = "Change the interior configuration"
    bl_options = {'UNDO'}

    interior_type: bpy.props.EnumProperty(
        name="Interior Type",
        items=[
            ('SHELVES', "Shelves", "Standard adjustable shelves"),
            ('ROLLOUTS', "Rollouts", "Pull-out rollout trays"),
            ('TRAY_DIVIDERS', "Tray Dividers", "Vertical tray dividers"),
            ('EMPTY', "Empty", "No interior parts"),
        ],
        default='SHELVES'
    ) # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj:
            interior_bp = hb_utils.get_interior_bp(obj)
            return interior_bp is not None
        return False

    def execute(self, context):
        interior_bp = hb_utils.get_interior_bp(context.object)
        if not interior_bp:
            self.report({'ERROR'}, "Could not find interior")
            return {'CANCELLED'}
        
        # TODO: Implement interior type change logic
        # This will need to:
        # 1. Delete existing interior children
        # 2. Create new interior based on type
        # 3. Re-link dimensions from parent opening
        
        self.report({'INFO'}, f"Interior will be changed to {self.interior_type}")
        return {'FINISHED'}


class hb_frameless_OT_interior_part_prompts(bpy.types.Operator):
    bl_idname = "hb_frameless.interior_part_prompts"
    bl_label = "Interior Part Prompts"
    bl_description = "Edit interior part properties"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and 'IS_FRAMELESS_INTERIOR_PART' in obj

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        obj = context.object
        
        box = layout.box()
        box.label(text=f"Part: {obj.name}")
        
        # Show relevant properties from the object
        if obj.modifiers:
            for mod in obj.modifiers:
                if mod.type == 'NODES' and mod.node_group:
                    for input in mod.node_group.interface.items_tree:
                        if input.item_type == 'SOCKET' and input.in_out == 'INPUT':
                            if hasattr(mod, f'["{input.identifier}"]'):
                                box.prop(mod, f'["{input.identifier}"]', text=input.name)


class hb_frameless_OT_delete_interior_part(bpy.types.Operator):
    bl_idname = "hb_frameless.delete_interior_part"
    bl_label = "Delete Interior Part"
    bl_description = "Delete this interior part"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and 'IS_FRAMELESS_INTERIOR_PART' in obj

    def execute(self, context):
        obj = context.object
        hb_utils.delete_obj_and_children(obj)
        return {'FINISHED'}


class hb_frameless_OT_custom_interior_vertical(bpy.types.Operator):
    bl_idname = "hb_frameless.custom_interior_vertical"
    bl_label = "Custom Vertical Interior Division"
    bl_description = "Create custom vertical interior divisions with adjustable sizes"
    bl_options = {'UNDO'}

    section_count: bpy.props.IntProperty(
        name="Number of Sections",
        min=2, max=6,
        default=2
    ) # type: ignore

    # Section heights (0 = equal distribution)
    section_1_height: bpy.props.FloatProperty(name="Section 1 Height", unit='LENGTH', default=0) # type: ignore
    section_2_height: bpy.props.FloatProperty(name="Section 2 Height", unit='LENGTH', default=0) # type: ignore
    section_3_height: bpy.props.FloatProperty(name="Section 3 Height", unit='LENGTH', default=0) # type: ignore
    section_4_height: bpy.props.FloatProperty(name="Section 4 Height", unit='LENGTH', default=0) # type: ignore

    # Section types
    section_1_type: bpy.props.EnumProperty(name="Section 1", items=[('SHELVES', "Shelves", ""), ('ROLLOUTS', "Rollouts", ""), ('TRAY_DIVIDERS', "Tray Dividers", ""), ('EMPTY', "Empty", "")], default='SHELVES') # type: ignore
    section_2_type: bpy.props.EnumProperty(name="Section 2", items=[('SHELVES', "Shelves", ""), ('ROLLOUTS', "Rollouts", ""), ('TRAY_DIVIDERS', "Tray Dividers", ""), ('EMPTY', "Empty", "")], default='SHELVES') # type: ignore
    section_3_type: bpy.props.EnumProperty(name="Section 3", items=[('SHELVES', "Shelves", ""), ('ROLLOUTS', "Rollouts", ""), ('TRAY_DIVIDERS', "Tray Dividers", ""), ('EMPTY', "Empty", "")], default='SHELVES') # type: ignore
    section_4_type: bpy.props.EnumProperty(name="Section 4", items=[('SHELVES', "Shelves", ""), ('ROLLOUTS', "Rollouts", ""), ('TRAY_DIVIDERS', "Tray Dividers", ""), ('EMPTY', "Empty", "")], default='SHELVES') # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj:
            interior_bp = hb_utils.get_interior_bp(obj)
            interior_part = hb_utils.get_interior_part_bp(obj)
            return interior_bp is not None or interior_part is not None
        return False

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def execute(self, context):
        # Find the interior cage
        interior_bp = hb_utils.get_interior_bp(context.object)
        if not interior_bp:
            # Try to find from interior part
            if 'IS_FRAMELESS_INTERIOR_PART' in context.object:
                interior_bp = hb_utils.get_interior_bp(context.object.parent)
        
        if not interior_bp:
            self.report({'ERROR'}, "Could not find interior")
            return {'CANCELLED'}
        
        # TODO: Implement the actual interior splitter creation
        # 1. Get parent opening dimensions
        # 2. Delete existing interior children
        # 3. Create InteriorSplitterVertical with settings
        
        self.report({'INFO'}, f"Will create {self.section_count} vertical interior sections")
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        box.prop(self, 'section_count')
        
        box = layout.box()
        box.label(text="Section Configuration (0 = Equal):")
        
        height_props = ['section_1_height', 'section_2_height', 'section_3_height', 'section_4_height']
        type_props = ['section_1_type', 'section_2_type', 'section_3_type', 'section_4_type']
        
        for i in range(min(self.section_count, 4)):
            row = box.row(align=True)
            row.label(text=f"Section {i+1}:")
            row.prop(self, height_props[i], text="Height")
            row.prop(self, type_props[i], text="")


class hb_frameless_OT_custom_interior_horizontal(bpy.types.Operator):
    bl_idname = "hb_frameless.custom_interior_horizontal"
    bl_label = "Custom Horizontal Interior Division"
    bl_description = "Create custom horizontal interior divisions with adjustable sizes"
    bl_options = {'UNDO'}

    section_count: bpy.props.IntProperty(
        name="Number of Sections",
        min=2, max=6,
        default=2
    ) # type: ignore

    # Section widths (0 = equal distribution)
    section_1_width: bpy.props.FloatProperty(name="Section 1 Width", unit='LENGTH', default=0) # type: ignore
    section_2_width: bpy.props.FloatProperty(name="Section 2 Width", unit='LENGTH', default=0) # type: ignore
    section_3_width: bpy.props.FloatProperty(name="Section 3 Width", unit='LENGTH', default=0) # type: ignore
    section_4_width: bpy.props.FloatProperty(name="Section 4 Width", unit='LENGTH', default=0) # type: ignore

    # Section types
    section_1_type: bpy.props.EnumProperty(name="Section 1", items=[('SHELVES', "Shelves", ""), ('ROLLOUTS', "Rollouts", ""), ('TRAY_DIVIDERS', "Tray Dividers", ""), ('EMPTY', "Empty", "")], default='SHELVES') # type: ignore
    section_2_type: bpy.props.EnumProperty(name="Section 2", items=[('SHELVES', "Shelves", ""), ('ROLLOUTS', "Rollouts", ""), ('TRAY_DIVIDERS', "Tray Dividers", ""), ('EMPTY', "Empty", "")], default='SHELVES') # type: ignore
    section_3_type: bpy.props.EnumProperty(name="Section 3", items=[('SHELVES', "Shelves", ""), ('ROLLOUTS', "Rollouts", ""), ('TRAY_DIVIDERS', "Tray Dividers", ""), ('EMPTY', "Empty", "")], default='SHELVES') # type: ignore
    section_4_type: bpy.props.EnumProperty(name="Section 4", items=[('SHELVES', "Shelves", ""), ('ROLLOUTS', "Rollouts", ""), ('TRAY_DIVIDERS', "Tray Dividers", ""), ('EMPTY', "Empty", "")], default='SHELVES') # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj:
            interior_bp = hb_utils.get_interior_bp(obj)
            interior_part = hb_utils.get_interior_part_bp(obj)
            return interior_bp is not None or interior_part is not None
        return False

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def execute(self, context):
        # Find the interior cage
        interior_bp = hb_utils.get_interior_bp(context.object)
        if not interior_bp:
            if 'IS_FRAMELESS_INTERIOR_PART' in context.object:
                interior_bp = hb_utils.get_interior_bp(context.object.parent)
        
        if not interior_bp:
            self.report({'ERROR'}, "Could not find interior")
            return {'CANCELLED'}
        
        # TODO: Implement the actual interior splitter creation
        
        self.report({'INFO'}, f"Will create {self.section_count} horizontal interior sections")
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        box.prop(self, 'section_count')
        
        box = layout.box()
        box.label(text="Section Configuration (0 = Equal):")
        
        width_props = ['section_1_width', 'section_2_width', 'section_3_width', 'section_4_width']
        type_props = ['section_1_type', 'section_2_type', 'section_3_type', 'section_4_type']
        
        for i in range(min(self.section_count, 4)):
            row = box.row(align=True)
            row.label(text=f"Section {i+1}:")
            row.prop(self, width_props[i], text="Width")
            row.prop(self, type_props[i], text="")


classes = (
    hb_frameless_OT_interior_prompts,
    hb_frameless_OT_change_interior_type,
    hb_frameless_OT_interior_part_prompts,
    hb_frameless_OT_delete_interior_part,
    hb_frameless_OT_custom_interior_vertical,
    hb_frameless_OT_custom_interior_horizontal,
)

register, unregister = bpy.utils.register_classes_factory(classes)
