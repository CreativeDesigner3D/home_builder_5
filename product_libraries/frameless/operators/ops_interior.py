import bpy
import math
from .. import types_frameless
from .. import props_hb_frameless
from .... import hb_utils, hb_types, units
from ....units import inch


def get_default_shelf_quantity(opening_height, opening_depth):
    """Determine the default number of shelves based on opening height and depth.
    
    Args:
        opening_height: The interior opening height in meters.
        opening_depth: The interior opening depth in meters.
        
    Returns:
        Integer shelf count.
    """
    height_inches = opening_height / inch(1)
    depth_inches = opening_depth / inch(1)
    
    if depth_inches <= 18:
        if height_inches <= 20:
            return 1
        elif height_inches <= 32:
            return 2
        elif height_inches <= 44:
            return 3
        else:
            return 4
    else:
        if height_inches <= 28:
            return 1
        elif height_inches <= 40:
            return 2
        elif height_inches <= 52:
            return 3
        else:
            return 4


def update_shelf_quantities(context, cabinet_obj):
    """Find all shelf interiors in a cabinet and set their quantity based on opening height.
    
    Should be called after run_calc_fix so drivers have resolved.
    
    Args:
        context: Blender context
        cabinet_obj: The cabinet base point object
    """
    for obj in cabinet_obj.children_recursive:
        if 'IS_FRAMELESS_INTERIOR_CAGE' in obj and 'Shelf Quantity' in obj:
            interior = hb_types.GeoNodeCage(obj)
            try:
                opening_height = interior.get_input('Dim Z')
                opening_depth = interior.get_input('Dim Y')
                qty = get_default_shelf_quantity(opening_height, opening_depth)
                obj['Shelf Quantity'] = qty
            except (ValueError, KeyError):
                pass


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

    def delete_interior_children(self, interior_obj):
        """Delete all children of the interior."""
        children = list(interior_obj.children)
        for child in children:
            self.delete_interior_children(child)
            bpy.data.objects.remove(child, do_unlink=True)

    def get_parent_opening(self, interior_obj):
        """Get the parent opening of the interior."""
        parent = interior_obj.parent
        while parent:
            if 'IS_FRAMELESS_OPENING_CAGE' in parent or 'IS_FRAMELESS_BAY_CAGE' in parent:
                return parent
            parent = parent.parent
        return None

    def add_interior_to_opening(self, opening_obj, interior):
        """Add an interior to an opening with proper drivers."""
        interior.create()
        interior.obj.parent = opening_obj
        
        if 'IS_FRAMELESS_OPENING_CAGE' in opening_obj:
            opening = types_frameless.CabinetOpening(opening_obj)
        else:
            opening = types_frameless.CabinetBay(opening_obj)
        
        dim_x = opening.var_input('Dim X', 'dim_x')
        dim_y = opening.var_input('Dim Y', 'dim_y')
        dim_z = opening.var_input('Dim Z', 'dim_z')
        interior.driver_input('Dim X', 'dim_x', [dim_x])
        interior.driver_input('Dim Y', 'dim_y', [dim_y])
        interior.driver_input('Dim Z', 'dim_z', [dim_z])

    def execute(self, context):
        interior_bp = hb_utils.get_interior_bp(context.object)
        if not interior_bp:
            self.report({'ERROR'}, "Could not find interior")
            return {'CANCELLED'}
        
        # Get parent opening before deleting
        parent_opening = self.get_parent_opening(interior_bp)
        if not parent_opening:
            self.report({'ERROR'}, "Could not find parent opening")
            return {'CANCELLED'}
        
        # Delete the old interior
        self.delete_interior_children(interior_bp)
        bpy.data.objects.remove(interior_bp, do_unlink=True)
        
        # Create new interior based on type
        if self.interior_type == 'SHELVES':
            interior = types_frameless.CabinetShelves()
            self.add_interior_to_opening(parent_opening, interior)
        elif self.interior_type == 'EMPTY':
            pass  # No interior needed
        
        # Run calc fix and update shelf quantities
        cabinet_bp = hb_utils.get_cabinet_bp(parent_opening)
        if cabinet_bp:
            hb_utils.run_calc_fix(context, cabinet_bp)
            update_shelf_quantities(context, cabinet_bp)
            hb_utils.run_calc_fix(context, cabinet_bp)
        
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
        min=2, max=10,
        default=2
    ) # type: ignore
    
    previous_section_count: bpy.props.IntProperty(default=0) # type: ignore
    splitter_obj_name: bpy.props.StringProperty(name="Splitter Object") # type: ignore
    parent_obj_name: bpy.props.StringProperty(name="Parent Object") # type: ignore

    # Section types
    section_1_type: bpy.props.EnumProperty(name="Section 1", items=[('SHELVES', "Shelves", ""), ('EMPTY', "Empty", "")], default='SHELVES') # type: ignore
    section_2_type: bpy.props.EnumProperty(name="Section 2", items=[('SHELVES', "Shelves", ""), ('EMPTY', "Empty", "")], default='SHELVES') # type: ignore
    section_3_type: bpy.props.EnumProperty(name="Section 3", items=[('SHELVES', "Shelves", ""), ('EMPTY', "Empty", "")], default='SHELVES') # type: ignore
    section_4_type: bpy.props.EnumProperty(name="Section 4", items=[('SHELVES', "Shelves", ""), ('EMPTY', "Empty", "")], default='SHELVES') # type: ignore
    section_5_type: bpy.props.EnumProperty(name="Section 5", items=[('SHELVES', "Shelves", ""), ('EMPTY', "Empty", "")], default='SHELVES') # type: ignore
    section_6_type: bpy.props.EnumProperty(name="Section 6", items=[('SHELVES', "Shelves", ""), ('EMPTY', "Empty", "")], default='SHELVES') # type: ignore
    section_7_type: bpy.props.EnumProperty(name="Section 7", items=[('SHELVES', "Shelves", ""), ('EMPTY', "Empty", "")], default='SHELVES') # type: ignore
    section_8_type: bpy.props.EnumProperty(name="Section 8", items=[('SHELVES', "Shelves", ""), ('EMPTY', "Empty", "")], default='SHELVES') # type: ignore
    section_9_type: bpy.props.EnumProperty(name="Section 9", items=[('SHELVES', "Shelves", ""), ('EMPTY', "Empty", "")], default='SHELVES') # type: ignore
    section_10_type: bpy.props.EnumProperty(name="Section 10", items=[('SHELVES', "Shelves", ""), ('EMPTY', "Empty", "")], default='SHELVES') # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj:
            interior_bp = hb_utils.get_interior_bp(obj)
            return interior_bp is not None
        return False

    def delete_children(self, obj):
        """Delete all children of the object."""
        children = list(obj.children)
        for child in children:
            self.delete_children(child)
            bpy.data.objects.remove(child, do_unlink=True)

    def get_splitter_obj(self):
        """Get the splitter object by name."""
        if self.splitter_obj_name and self.splitter_obj_name in bpy.data.objects:
            return bpy.data.objects[self.splitter_obj_name]
        return None

    def get_parent_obj(self):
        """Get the parent object by name."""
        if self.parent_obj_name and self.parent_obj_name in bpy.data.objects:
            return bpy.data.objects[self.parent_obj_name]
        return None

    def get_parent_opening(self, interior_obj):
        """Get the parent opening of the interior."""
        parent = interior_obj.parent
        while parent:
            if 'IS_FRAMELESS_OPENING_CAGE' in parent or 'IS_FRAMELESS_BAY_CAGE' in parent:
                return parent
            parent = parent.parent
        return None

    def create_splitter(self, context, parent_obj):
        """Create or recreate the splitter with current settings."""
        # Delete existing children of parent interior
        self.delete_children(parent_obj)
        
        # Remove the old interior object
        parent_opening = self.get_parent_opening(parent_obj)
        if parent_obj and parent_obj.name in bpy.data.objects:
            bpy.data.objects.remove(parent_obj, do_unlink=True)
        
        if not parent_opening:
            return None
        
        # Create empty splitter (no section types yet - just for sizing)
        splitter = types_frameless.InteriorSplitterVertical()
        splitter.splitter_qty = self.section_count - 1
        splitter.section_sizes = [0] * self.section_count
        splitter.section_types = ['EMPTY'] * self.section_count  # Empty for preview
        splitter.create()
        
        # Parent to opening and set up dimension drivers
        splitter.obj.parent = parent_opening
        
        if 'IS_FRAMELESS_OPENING_CAGE' in parent_opening:
            opening = types_frameless.CabinetOpening(parent_opening)
        else:
            opening = types_frameless.CabinetBay(parent_opening)
            
        dim_x = opening.var_input('Dim X', 'dim_x')
        dim_y = opening.var_input('Dim Y', 'dim_y')
        dim_z = opening.var_input('Dim Z', 'dim_z')
        splitter.driver_input('Dim X', 'dim_x', [dim_x])
        splitter.driver_input('Dim Y', 'dim_y', [dim_y])
        splitter.driver_input('Dim Z', 'dim_z', [dim_z])
        
        self.splitter_obj_name = splitter.obj.name
        self.parent_obj_name = parent_opening.name
        self.previous_section_count = self.section_count
        
        # Run calc fix
        cabinet_bp = hb_utils.get_cabinet_bp(parent_opening)
        if cabinet_bp:
            hb_utils.run_calc_fix(context, cabinet_bp)
        
        return splitter.obj

    def invoke(self, context, event):
        # Find interior
        interior_bp = hb_utils.get_interior_bp(context.object)
        if not interior_bp:
            self.report({'ERROR'}, "Could not find interior")
            return {'CANCELLED'}
        
        # Create initial splitter (replaces old interior)
        self.create_splitter(context, interior_bp)
        
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def check(self, context):
        parent_obj = self.get_parent_obj()
        if not parent_obj:
            return False
        
        # If section count changed, recreate the splitter
        if self.section_count != self.previous_section_count:
            # Get current splitter and delete it
            splitter_obj = self.get_splitter_obj()
            if splitter_obj:
                self.delete_children(splitter_obj)
                bpy.data.objects.remove(splitter_obj, do_unlink=True)
            
            # Create new splitter directly in the opening
            splitter = types_frameless.InteriorSplitterVertical()
            splitter.splitter_qty = self.section_count - 1
            splitter.section_sizes = [0] * self.section_count
            splitter.section_types = ['EMPTY'] * self.section_count
            splitter.create()
            
            splitter.obj.parent = parent_obj
            
            if 'IS_FRAMELESS_OPENING_CAGE' in parent_obj:
                opening = types_frameless.CabinetOpening(parent_obj)
            else:
                opening = types_frameless.CabinetBay(parent_obj)
                
            dim_x = opening.var_input('Dim X', 'dim_x')
            dim_y = opening.var_input('Dim Y', 'dim_y')
            dim_z = opening.var_input('Dim Z', 'dim_z')
            splitter.driver_input('Dim X', 'dim_x', [dim_x])
            splitter.driver_input('Dim Y', 'dim_y', [dim_y])
            splitter.driver_input('Dim Z', 'dim_z', [dim_z])
            
            self.splitter_obj_name = splitter.obj.name
            self.previous_section_count = self.section_count
            
            cabinet_bp = hb_utils.get_cabinet_bp(parent_obj)
            if cabinet_bp:
                hb_utils.run_calc_fix(context, cabinet_bp)
            return True
        
        # Otherwise just recalculate
        splitter_obj = self.get_splitter_obj()
        if splitter_obj:
            for calculator in splitter_obj.home_builder.calculators:
                calculator.calculate()
            
            cabinet_bp = hb_utils.get_cabinet_bp(splitter_obj)
            if cabinet_bp:
                hb_utils.run_calc_fix(context, cabinet_bp)
        
        return True

    def execute(self, context):
        parent_obj = self.get_parent_obj()
        splitter_obj = self.get_splitter_obj()
        
        if not parent_obj or not splitter_obj:
            self.report({'ERROR'}, "Could not find objects")
            return {'CANCELLED'}
        
        # Get the current calculator values before recreating
        section_sizes = []
        for calculator in splitter_obj.home_builder.calculators:
            for prompt in calculator.prompts:
                if prompt.equal:
                    section_sizes.append(0)
                else:
                    section_sizes.append(prompt.distance_value)
        
        # Delete existing splitter and create final one with section types
        self.delete_children(splitter_obj)
        bpy.data.objects.remove(splitter_obj, do_unlink=True)
        
        type_props = [
            self.section_1_type, self.section_2_type, self.section_3_type,
            self.section_4_type, self.section_5_type, self.section_6_type,
            self.section_7_type, self.section_8_type, self.section_9_type,
            self.section_10_type
        ]
        
        section_types = []
        for i in range(self.section_count):
            section_types.append(type_props[i])
        
        # Create final splitter with section types
        splitter = types_frameless.InteriorSplitterVertical()
        splitter.splitter_qty = self.section_count - 1
        splitter.section_sizes = section_sizes
        splitter.section_types = section_types
        splitter.create()
        
        # Parent and set up drivers
        splitter.obj.parent = parent_obj
        
        if 'IS_FRAMELESS_OPENING_CAGE' in parent_obj:
            opening = types_frameless.CabinetOpening(parent_obj)
        else:
            opening = types_frameless.CabinetBay(parent_obj)
            
        dim_x = opening.var_input('Dim X', 'dim_x')
        dim_y = opening.var_input('Dim Y', 'dim_y')
        dim_z = opening.var_input('Dim Z', 'dim_z')
        splitter.driver_input('Dim X', 'dim_x', [dim_x])
        splitter.driver_input('Dim Y', 'dim_y', [dim_y])
        splitter.driver_input('Dim Z', 'dim_z', [dim_z])
        
        # Run calc fix and update shelf quantities
        cabinet_bp = hb_utils.get_cabinet_bp(parent_obj)
        if cabinet_bp:
            hb_utils.run_calc_fix(context, cabinet_bp)
            update_shelf_quantities(context, cabinet_bp)
            hb_utils.run_calc_fix(context, cabinet_bp)
        
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        box.prop(self, 'section_count')
        
        splitter_obj = self.get_splitter_obj()
        
        # Section heights from calculator
        box = layout.box()
        box.label(text="Section Heights:", icon='SNAP_GRID')
        
        if splitter_obj:
            for calculator in splitter_obj.home_builder.calculators:
                col = box.column(align=True)
                for prompt in calculator.prompts:
                    row = col.row(align=True)
                    row.active = not prompt.equal
                    row.prop(prompt, 'distance_value', text=prompt.name)
                    row.prop(prompt, 'equal', text="", icon='LINKED' if prompt.equal else 'UNLINKED')
        
        # Section types
        box = layout.box()
        box.label(text="Section Types:", icon='MESH_PLANE')
        
        type_props = [
            'section_1_type', 'section_2_type', 'section_3_type',
            'section_4_type', 'section_5_type', 'section_6_type',
            'section_7_type', 'section_8_type', 'section_9_type',
            'section_10_type'
        ]
        
        col = box.column(align=True)
        for i in range(self.section_count):
            row = col.row(align=True)
            row.label(text=f"Section {i+1}:")
            row.prop(self, type_props[i], text="")


class hb_frameless_OT_custom_interior_horizontal(bpy.types.Operator):
    bl_idname = "hb_frameless.custom_interior_horizontal"
    bl_label = "Custom Horizontal Interior Division"
    bl_description = "Create custom horizontal interior divisions with adjustable sizes"
    bl_options = {'UNDO'}

    section_count: bpy.props.IntProperty(
        name="Number of Sections",
        min=2, max=10,
        default=2
    ) # type: ignore
    
    previous_section_count: bpy.props.IntProperty(default=0) # type: ignore
    splitter_obj_name: bpy.props.StringProperty(name="Splitter Object") # type: ignore
    parent_obj_name: bpy.props.StringProperty(name="Parent Object") # type: ignore

    # Section types
    section_1_type: bpy.props.EnumProperty(name="Section 1", items=[('SHELVES', "Shelves", ""), ('EMPTY', "Empty", "")], default='SHELVES') # type: ignore
    section_2_type: bpy.props.EnumProperty(name="Section 2", items=[('SHELVES', "Shelves", ""), ('EMPTY', "Empty", "")], default='SHELVES') # type: ignore
    section_3_type: bpy.props.EnumProperty(name="Section 3", items=[('SHELVES', "Shelves", ""), ('EMPTY', "Empty", "")], default='SHELVES') # type: ignore
    section_4_type: bpy.props.EnumProperty(name="Section 4", items=[('SHELVES', "Shelves", ""), ('EMPTY', "Empty", "")], default='SHELVES') # type: ignore
    section_5_type: bpy.props.EnumProperty(name="Section 5", items=[('SHELVES', "Shelves", ""), ('EMPTY', "Empty", "")], default='SHELVES') # type: ignore
    section_6_type: bpy.props.EnumProperty(name="Section 6", items=[('SHELVES', "Shelves", ""), ('EMPTY', "Empty", "")], default='SHELVES') # type: ignore
    section_7_type: bpy.props.EnumProperty(name="Section 7", items=[('SHELVES', "Shelves", ""), ('EMPTY', "Empty", "")], default='SHELVES') # type: ignore
    section_8_type: bpy.props.EnumProperty(name="Section 8", items=[('SHELVES', "Shelves", ""), ('EMPTY', "Empty", "")], default='SHELVES') # type: ignore
    section_9_type: bpy.props.EnumProperty(name="Section 9", items=[('SHELVES', "Shelves", ""), ('EMPTY', "Empty", "")], default='SHELVES') # type: ignore
    section_10_type: bpy.props.EnumProperty(name="Section 10", items=[('SHELVES', "Shelves", ""), ('EMPTY', "Empty", "")], default='SHELVES') # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj:
            interior_bp = hb_utils.get_interior_bp(obj)
            return interior_bp is not None
        return False

    def delete_children(self, obj):
        """Delete all children of the object."""
        children = list(obj.children)
        for child in children:
            self.delete_children(child)
            bpy.data.objects.remove(child, do_unlink=True)

    def get_splitter_obj(self):
        """Get the splitter object by name."""
        if self.splitter_obj_name and self.splitter_obj_name in bpy.data.objects:
            return bpy.data.objects[self.splitter_obj_name]
        return None

    def get_parent_obj(self):
        """Get the parent object by name."""
        if self.parent_obj_name and self.parent_obj_name in bpy.data.objects:
            return bpy.data.objects[self.parent_obj_name]
        return None

    def get_parent_opening(self, interior_obj):
        """Get the parent opening of the interior."""
        parent = interior_obj.parent
        while parent:
            if 'IS_FRAMELESS_OPENING_CAGE' in parent or 'IS_FRAMELESS_BAY_CAGE' in parent:
                return parent
            parent = parent.parent
        return None

    def create_splitter(self, context, parent_obj):
        """Create or recreate the splitter with current settings."""
        # Delete existing children of parent interior
        self.delete_children(parent_obj)
        
        # Remove the old interior object
        parent_opening = self.get_parent_opening(parent_obj)
        if parent_obj and parent_obj.name in bpy.data.objects:
            bpy.data.objects.remove(parent_obj, do_unlink=True)
        
        if not parent_opening:
            return None
        
        # Create empty splitter
        splitter = types_frameless.InteriorSplitterHorizontal()
        splitter.splitter_qty = self.section_count - 1
        splitter.section_sizes = [0] * self.section_count
        splitter.section_types = ['EMPTY'] * self.section_count
        splitter.create()
        
        # Parent to opening and set up dimension drivers
        splitter.obj.parent = parent_opening
        
        if 'IS_FRAMELESS_OPENING_CAGE' in parent_opening:
            opening = types_frameless.CabinetOpening(parent_opening)
        else:
            opening = types_frameless.CabinetBay(parent_opening)
            
        dim_x = opening.var_input('Dim X', 'dim_x')
        dim_y = opening.var_input('Dim Y', 'dim_y')
        dim_z = opening.var_input('Dim Z', 'dim_z')
        splitter.driver_input('Dim X', 'dim_x', [dim_x])
        splitter.driver_input('Dim Y', 'dim_y', [dim_y])
        splitter.driver_input('Dim Z', 'dim_z', [dim_z])
        
        self.splitter_obj_name = splitter.obj.name
        self.parent_obj_name = parent_opening.name
        self.previous_section_count = self.section_count
        
        # Run calc fix
        cabinet_bp = hb_utils.get_cabinet_bp(parent_opening)
        if cabinet_bp:
            hb_utils.run_calc_fix(context, cabinet_bp)
        
        return splitter.obj

    def invoke(self, context, event):
        # Find interior
        interior_bp = hb_utils.get_interior_bp(context.object)
        if not interior_bp:
            self.report({'ERROR'}, "Could not find interior")
            return {'CANCELLED'}
        
        # Create initial splitter (replaces old interior)
        self.create_splitter(context, interior_bp)
        
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def check(self, context):
        parent_obj = self.get_parent_obj()
        if not parent_obj:
            return False
        
        # If section count changed, recreate the splitter
        if self.section_count != self.previous_section_count:
            splitter_obj = self.get_splitter_obj()
            if splitter_obj:
                self.delete_children(splitter_obj)
                bpy.data.objects.remove(splitter_obj, do_unlink=True)
            
            splitter = types_frameless.InteriorSplitterHorizontal()
            splitter.splitter_qty = self.section_count - 1
            splitter.section_sizes = [0] * self.section_count
            splitter.section_types = ['EMPTY'] * self.section_count
            splitter.create()
            
            splitter.obj.parent = parent_obj
            
            if 'IS_FRAMELESS_OPENING_CAGE' in parent_obj:
                opening = types_frameless.CabinetOpening(parent_obj)
            else:
                opening = types_frameless.CabinetBay(parent_obj)
                
            dim_x = opening.var_input('Dim X', 'dim_x')
            dim_y = opening.var_input('Dim Y', 'dim_y')
            dim_z = opening.var_input('Dim Z', 'dim_z')
            splitter.driver_input('Dim X', 'dim_x', [dim_x])
            splitter.driver_input('Dim Y', 'dim_y', [dim_y])
            splitter.driver_input('Dim Z', 'dim_z', [dim_z])
            
            self.splitter_obj_name = splitter.obj.name
            self.previous_section_count = self.section_count
            
            cabinet_bp = hb_utils.get_cabinet_bp(parent_obj)
            if cabinet_bp:
                hb_utils.run_calc_fix(context, cabinet_bp)
            return True
        
        # Otherwise just recalculate
        splitter_obj = self.get_splitter_obj()
        if splitter_obj:
            for calculator in splitter_obj.home_builder.calculators:
                calculator.calculate()
            
            cabinet_bp = hb_utils.get_cabinet_bp(splitter_obj)
            if cabinet_bp:
                hb_utils.run_calc_fix(context, cabinet_bp)
        
        return True

    def execute(self, context):
        parent_obj = self.get_parent_obj()
        splitter_obj = self.get_splitter_obj()
        
        if not parent_obj or not splitter_obj:
            self.report({'ERROR'}, "Could not find objects")
            return {'CANCELLED'}
        
        # Get the current calculator values before recreating
        section_sizes = []
        for calculator in splitter_obj.home_builder.calculators:
            for prompt in calculator.prompts:
                if prompt.equal:
                    section_sizes.append(0)
                else:
                    section_sizes.append(prompt.distance_value)
        
        # Delete existing splitter and create final one with section types
        self.delete_children(splitter_obj)
        bpy.data.objects.remove(splitter_obj, do_unlink=True)
        
        type_props = [
            self.section_1_type, self.section_2_type, self.section_3_type,
            self.section_4_type, self.section_5_type, self.section_6_type,
            self.section_7_type, self.section_8_type, self.section_9_type,
            self.section_10_type
        ]
        
        section_types = []
        for i in range(self.section_count):
            section_types.append(type_props[i])
        
        # Create final splitter with section types
        splitter = types_frameless.InteriorSplitterHorizontal()
        splitter.splitter_qty = self.section_count - 1
        splitter.section_sizes = section_sizes
        splitter.section_types = section_types
        splitter.create()
        
        # Parent and set up drivers
        splitter.obj.parent = parent_obj
        
        if 'IS_FRAMELESS_OPENING_CAGE' in parent_obj:
            opening = types_frameless.CabinetOpening(parent_obj)
        else:
            opening = types_frameless.CabinetBay(parent_obj)
            
        dim_x = opening.var_input('Dim X', 'dim_x')
        dim_y = opening.var_input('Dim Y', 'dim_y')
        dim_z = opening.var_input('Dim Z', 'dim_z')
        splitter.driver_input('Dim X', 'dim_x', [dim_x])
        splitter.driver_input('Dim Y', 'dim_y', [dim_y])
        splitter.driver_input('Dim Z', 'dim_z', [dim_z])
        
        # Run calc fix and update shelf quantities
        cabinet_bp = hb_utils.get_cabinet_bp(parent_obj)
        if cabinet_bp:
            hb_utils.run_calc_fix(context, cabinet_bp)
            update_shelf_quantities(context, cabinet_bp)
            hb_utils.run_calc_fix(context, cabinet_bp)
        
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        box.prop(self, 'section_count')
        
        splitter_obj = self.get_splitter_obj()
        
        # Section widths from calculator
        box = layout.box()
        box.label(text="Section Widths:", icon='SNAP_GRID')
        
        if splitter_obj:
            for calculator in splitter_obj.home_builder.calculators:
                col = box.column(align=True)
                for prompt in calculator.prompts:
                    row = col.row(align=True)
                    row.active = not prompt.equal
                    row.prop(prompt, 'distance_value', text=prompt.name)
                    row.prop(prompt, 'equal', text="", icon='LINKED' if prompt.equal else 'UNLINKED')
        
        # Section types
        box = layout.box()
        box.label(text="Section Types:", icon='MESH_PLANE')
        
        type_props = [
            'section_1_type', 'section_2_type', 'section_3_type',
            'section_4_type', 'section_5_type', 'section_6_type',
            'section_7_type', 'section_8_type', 'section_9_type',
            'section_10_type'
        ]
        
        col = box.column(align=True)
        for i in range(self.section_count):
            row = col.row(align=True)
            row.label(text=f"Section {i+1}:")
            row.prop(self, type_props[i], text="")


class hb_frameless_OT_calculate_shelf_quantity(bpy.types.Operator):
    """Calculate default shelf quantity based on opening height"""
    bl_idname = "hb_frameless.calculate_shelf_quantity"
    bl_label = "Calculate Shelf Quantity"
    bl_description = "Set shelf quantities based on opening heights"
    bl_options = {'UNDO'}

    cabinet_name: bpy.props.StringProperty(name="Cabinet Name", default="") # type: ignore

    def execute(self, context):
        if self.cabinet_name and self.cabinet_name in bpy.data.objects:
            cabinet_obj = bpy.data.objects[self.cabinet_name]
        elif context.object:
            cabinet_obj = hb_utils.get_cabinet_bp(context.object)
        else:
            return {'CANCELLED'}

        if cabinet_obj:
            update_shelf_quantities(context, cabinet_obj)
            hb_utils.run_calc_fix(context, cabinet_obj)

        return {'FINISHED'}


classes = (
    hb_frameless_OT_calculate_shelf_quantity,
    hb_frameless_OT_interior_prompts,
    hb_frameless_OT_change_interior_type,
    hb_frameless_OT_interior_part_prompts,
    hb_frameless_OT_delete_interior_part,
    hb_frameless_OT_custom_interior_vertical,
    hb_frameless_OT_custom_interior_horizontal,
)

register, unregister = bpy.utils.register_classes_factory(classes)
