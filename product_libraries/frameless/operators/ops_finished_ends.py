import bpy
import math
import os
from .. import types_frameless
from .... import hb_utils, hb_types, hb_project, units
from ....units import inch


def get_door_from_cabinet(cabinet_obj):
    """Find a door front in the cabinet to match dimensions from."""
    for child in cabinet_obj.children_recursive:
        if child.get('IS_DOOR_FRONT') or child.get('IS_DRAWER_FRONT'):
            # Check if it has door style applied
            for mod in child.modifiers:
                if mod.type == 'NODES' and mod.node_group:
                    if 'Top Rail Width' in mod.node_group.interface.items_tree:
                        return child
    return None


def get_door_style_from_front(front_obj):
    """Get door style dimensions from a front object."""
    if not front_obj:
        return None
    
    for mod in front_obj.modifiers:
        if mod.type == 'NODES' and mod.node_group:
            ng = mod.node_group
            if 'Top Rail Width' in ng.interface.items_tree:
                def get_input(name):
                    if name in ng.interface.items_tree:
                        node_input = ng.interface.items_tree[name]
                        return mod.get(node_input.identifier, None)
                    return None
                
                return {
                    'top_rail_width': get_input('Top Rail Width'),
                    'bottom_rail_width': get_input('Bottom Rail Width'),
                    'left_stile_width': get_input('Left Stile Width'),
                    'right_stile_width': get_input('Right Stile Width'),
                    'panel_thickness': get_input('Panel Thickness'),
                    'panel_inset': get_input('Panel Inset'),
                }
    return None


def get_cabinet_style_materials(cabinet_obj):
    """Get the finish material from cabinet style."""
    style_index = cabinet_obj.get('CABINET_STYLE_INDEX', 0)
    main_scene = hb_project.get_main_scene()
    main_props = main_scene.hb_frameless
    
    if main_props.cabinet_styles and style_index < len(main_props.cabinet_styles):
        style = main_props.cabinet_styles[style_index]
        return style.get_finish_material()
    return None, None


class hb_frameless_OT_update_finished_end(bpy.types.Operator):
    bl_idname = "hb_frameless.update_finished_end"
    bl_label = "Update Finished End"
    bl_description = "Update the finished end condition for the selected cabinet"
    bl_options = {'UNDO'}

    side: bpy.props.EnumProperty(
        name="Side",
        items=[
            ('LEFT', "Left", "Left side"),
            ('RIGHT', "Right", "Right side"),
            ('BACK', "Back", "Back panel"),
        ],
        default='LEFT'
    )  # type: ignore

    finished_end_type: bpy.props.EnumProperty(
        name="Finished End Type",
        items=[
            ('NONE', "None (Remove)", "Remove finished end"),
            ('SLAB', "Slab Panel", "Simple slab panel"),
            ('5PIECE', "5-Piece Panel", "5-piece panel matching door style"),
        ],
        default='5PIECE'
    )  # type: ignore

    panel_to_floor: bpy.props.BoolProperty(
        name="Panel to Floor",
        description="Extend panel to floor (below toe kick)",
        default=True
    )  # type: ignore

    match_door_style: bpy.props.BoolProperty(
        name="Match Door Style",
        description="Match rail/stile dimensions from cabinet door",
        default=True
    )  # type: ignore

    top_rail_width: bpy.props.FloatProperty(
        name="Top Rail Width",
        default=inch(2.5),
        unit='LENGTH',
        precision=4
    )  # type: ignore

    bottom_rail_width: bpy.props.FloatProperty(
        name="Bottom Rail Width",
        default=inch(2.5),
        unit='LENGTH',
        precision=4
    )  # type: ignore

    stile_width: bpy.props.FloatProperty(
        name="Stile Width",
        default=inch(2.5),
        unit='LENGTH',
        precision=4
    )  # type: ignore

    cabinet_obj = None
    door_obj = None
    door_style = None

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj:
            cabinet_bp = hb_utils.get_cabinet_bp(obj)
            return cabinet_bp is not None
        return False

    def has_applied_end(self, cabinet_obj, side):
        """Check if cabinet already has an applied end on the specified side."""
        for child in cabinet_obj.children:
            if child.get('IS_APPLIED_END_' + side):
                return True
        return False

    def remove_applied_end(self, cabinet_obj, side):
        """Remove existing applied end from specified side."""
        for child in list(cabinet_obj.children):
            if child.get('IS_APPLIED_END_' + side):
                hb_utils.delete_obj_and_children(child)

    def create_slab_panel(self, context, cabinet_obj, side):
        """Create a simple slab applied end panel."""
        props = bpy.context.scene.hb_frameless
        cabinet = hb_types.GeoNodeCage(cabinet_obj)
        
        dim_x = cabinet.var_input('Dim X', 'dim_x')
        dim_y = cabinet.var_input('Dim Y', 'dim_y')
        dim_z = cabinet.var_input('Dim Z', 'dim_z')
        
        # Extension to be flush with door front
        front_extension = inch(0.875)  # gap + thickness
        
        panel = types_frameless.CabinetPart()
        panel.create(f'Applied End {side.title()}')
        panel.obj['IS_APPLIED_END_' + side] = True
        panel.obj['IS_SLAB_PANEL'] = True
        panel.obj['MENU_ID'] = 'HOME_BUILDER_MT_applied_end_commands'
        panel.obj.parent = cabinet_obj
        panel.obj.location.z = 0
        
        if side == 'LEFT':
            panel.obj.rotation_euler.y = math.radians(-90)
            panel.obj.location.x = 0
            panel.set_input("Mirror Y", True)
            panel.set_input("Mirror Z", False)
            panel.driver_input("Length", 'dim_z', [dim_z])
            panel.driver_input("Width", f'dim_y+{front_extension}', [dim_y])
            
        elif side == 'RIGHT':
            panel.obj.rotation_euler.y = math.radians(-90)
            panel.driver_location('x', 'dim_x', [dim_x])
            panel.set_input("Mirror Y", True)
            panel.set_input("Mirror Z", True)
            panel.driver_input("Length", 'dim_z', [dim_z])
            panel.driver_input("Width", f'dim_y+{front_extension}', [dim_y])
            
        elif side == 'BACK':
            panel.obj.rotation_euler.x = math.radians(90)
            panel.obj.location.y = 0
            panel.set_input("Mirror Y", False)
            panel.set_input("Mirror Z", True)
            panel.driver_input("Length", 'dim_x', [dim_x])
            panel.driver_input("Width", 'dim_z', [dim_z])
        
        panel.set_input("Thickness", props.default_carcass_part_thickness)
        
        # Assign materials
        material, material_rotated = get_cabinet_style_materials(cabinet_obj)
        if material:
            panel.set_input("Top Surface", material)
            panel.set_input("Bottom Surface", material)
            panel.set_input("Edge W1", material_rotated)
            panel.set_input("Edge W2", material_rotated)
            panel.set_input("Edge L1", material_rotated)
            panel.set_input("Edge L2", material_rotated)
        
        return panel.obj

    def create_5piece_panel(self, context, cabinet_obj, side):
        """Create a 5-piece applied end panel matching door style."""
        props = bpy.context.scene.hb_frameless
        cabinet = hb_types.GeoNodeCage(cabinet_obj)
        
        dim_x = cabinet.var_input('Dim X', 'dim_x')
        dim_y = cabinet.var_input('Dim Y', 'dim_y')
        dim_z = cabinet.var_input('Dim Z', 'dim_z')
        
        # Get toe kick height if it exists
        tkh_value = 0
        try:
            tkh_value = cabinet_obj.get('Toe Kick Height', 0)
        except:
            pass
        
        # Create the base panel
        panel = types_frameless.CabinetPart()
        panel.create(f'Applied Panel 5Piece {side.title()}')
        panel.obj['IS_APPLIED_END_' + side] = True
        panel.obj['IS_APPLIED_PANEL_5PIECE'] = True
        panel.obj['MENU_ID'] = 'HOME_BUILDER_MT_applied_end_commands'
        panel.obj.parent = cabinet_obj
        
        # Finish both sides of panel
        panel.obj['Finish Top'] = True
        panel.obj['Finish Bottom'] = True
        
        if side == 'LEFT':
            panel.obj.rotation_euler.y = math.radians(-90)
            panel.obj.location.x = 0
            panel.set_input("Mirror Y", True)
            panel.set_input("Mirror Z", False)
            
            if self.panel_to_floor:
                panel.obj.location.z = 0
                panel.driver_input("Length", 'dim_z', [dim_z])
            else:
                panel.obj.location.z = tkh_value
                panel.driver_input("Length", f'dim_z-{tkh_value}', [dim_z])
            
            # Width is cabinet depth minus carcass thickness
            panel.driver_input("Width", f'dim_y-{inch(0.75)}', [dim_y])
            
        elif side == 'RIGHT':
            panel.obj.rotation_euler.y = math.radians(-90)
            panel.driver_location('x', 'dim_x', [dim_x])
            panel.set_input("Mirror Y", True)
            panel.set_input("Mirror Z", True)
            
            if self.panel_to_floor:
                panel.obj.location.z = 0
                panel.driver_input("Length", 'dim_z', [dim_z])
            else:
                panel.obj.location.z = tkh_value
                panel.driver_input("Length", f'dim_z-{tkh_value}', [dim_z])
            
            panel.driver_input("Width", f'dim_y-{inch(0.75)}', [dim_y])
            
        elif side == 'BACK':
            panel.obj.rotation_euler.x = math.radians(90)
            panel.obj.location.y = 0
            panel.set_input("Mirror Y", False)
            panel.set_input("Mirror Z", True)
            panel.driver_input("Length", 'dim_x', [dim_x])
            panel.driver_input("Width", 'dim_z', [dim_z])
        
        panel.set_input("Thickness", inch(0.75))
        
        # Add 5-piece door modifier
        door_style_mod = panel.add_part_modifier('CPM_5PIECEDOOR', 'Door Style')
        
        # Set dimensions
        if self.match_door_style and self.door_style:
            door_style_mod.set_input("Left Stile Width", self.door_style.get('left_stile_width', self.stile_width))
            door_style_mod.set_input("Right Stile Width", self.door_style.get('right_stile_width', self.stile_width))
            door_style_mod.set_input("Top Rail Width", self.door_style.get('top_rail_width', self.top_rail_width))
            door_style_mod.set_input("Bottom Rail Width", self.door_style.get('bottom_rail_width', self.bottom_rail_width))
            door_style_mod.set_input("Panel Thickness", self.door_style.get('panel_thickness', inch(0.75)))
            door_style_mod.set_input("Panel Inset", self.door_style.get('panel_inset', inch(0.25)))
        else:
            door_style_mod.set_input("Left Stile Width", self.stile_width)
            door_style_mod.set_input("Right Stile Width", self.stile_width)
            door_style_mod.set_input("Top Rail Width", self.top_rail_width)
            door_style_mod.set_input("Bottom Rail Width", self.bottom_rail_width)
            door_style_mod.set_input("Panel Thickness", inch(0.75))
            door_style_mod.set_input("Panel Inset", inch(0.25))
        
        # Assign materials
        material, material_rotated = get_cabinet_style_materials(cabinet_obj)
        if material:
            # Assign to base cutpart
            panel.set_input("Top Surface", material)
            panel.set_input("Bottom Surface", material)
            panel.set_input("Edge W1", material_rotated)
            panel.set_input("Edge W2", material_rotated)
            panel.set_input("Edge L1", material_rotated)
            panel.set_input("Edge L2", material_rotated)
            
            # Assign to 5-piece door modifier
            try:
                door_style_mod.set_input("Stile Material", material)
                door_style_mod.set_input("Rail Material", material)
                door_style_mod.set_input("Panel Material", material)
            except:
                pass  # Some inputs may not exist
        
        door_style_mod.mod.show_viewport = True
        
        return panel.obj

    def invoke(self, context, event):
        self.cabinet_obj = hb_utils.get_cabinet_bp(context.object)
        if not self.cabinet_obj:
            return {'CANCELLED'}
        
        # Try to detect which side based on object name
        obj_name = context.object.name.upper()
        if 'LEFT' in obj_name:
            self.side = 'LEFT'
        elif 'RIGHT' in obj_name:
            self.side = 'RIGHT'
        elif 'BACK' in obj_name:
            self.side = 'BACK'
        
        # Try to get door dimensions
        self.door_obj = get_door_from_cabinet(self.cabinet_obj)
        self.door_style = get_door_style_from_front(self.door_obj)
        
        # Pre-fill values from door style if available
        if self.door_style:
            if self.door_style.get('top_rail_width'):
                self.top_rail_width = self.door_style['top_rail_width']
            if self.door_style.get('bottom_rail_width'):
                self.bottom_rail_width = self.door_style['bottom_rail_width']
            if self.door_style.get('left_stile_width'):
                self.stile_width = self.door_style['left_stile_width']
        
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def execute(self, context):
        cabinet_bp = hb_utils.get_cabinet_bp(context.object)
        if not cabinet_bp:
            self.report({'ERROR'}, "Could not find cabinet")
            return {'CANCELLED'}
        
        # Remove existing applied end
        self.remove_applied_end(cabinet_bp, self.side)
        
        # Create new panel based on type
        if self.finished_end_type == 'NONE':
            pass  # Just removed, nothing to add
        elif self.finished_end_type == 'SLAB':
            self.create_slab_panel(context, cabinet_bp, self.side)
        elif self.finished_end_type == '5PIECE':
            self.create_5piece_panel(context, cabinet_bp, self.side)
        
        hb_utils.run_calc_fix(context, cabinet_bp)
        
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        box.label(text=f"Update {self.side.title()} Finished End", icon='MOD_SOLIDIFY')
        
        col = box.column(align=True)
        col.prop(self, "finished_end_type", text="Type")
        
        if self.finished_end_type == '5PIECE':
            col.separator()
            col.prop(self, "panel_to_floor")
            col.separator()
            col.prop(self, "match_door_style")
            
            if not self.match_door_style:
                box2 = layout.box()
                box2.label(text="Custom Dimensions", icon='SETTINGS')
                col2 = box2.column(align=True)
                col2.prop(self, "top_rail_width")
                col2.prop(self, "bottom_rail_width")
                col2.prop(self, "stile_width")
            elif self.door_style:
                box2 = layout.box()
                box2.label(text="Door Style Dimensions (Read Only):", icon='INFO')
                col2 = box2.column(align=True)
                col2.enabled = False
                col2.prop(self, "top_rail_width", text="Top Rail")
                col2.prop(self, "bottom_rail_width", text="Bottom Rail")
                col2.prop(self, "stile_width", text="Stile Width")
            else:
                box2 = layout.box()
                box2.label(text="No door found - using defaults", icon='ERROR')


class hb_frameless_OT_applied_panel_prompts(bpy.types.Operator):
    bl_idname = "hb_frameless.applied_panel_prompts"
    bl_label = "Applied Panel Prompts"
    bl_description = "Edit applied panel properties"
    bl_options = {'UNDO'}

    top_rail_width: bpy.props.FloatProperty(
        name="Top Rail Width",
        default=inch(2.5),
        unit='LENGTH',
        precision=4
    )  # type: ignore

    bottom_rail_width: bpy.props.FloatProperty(
        name="Bottom Rail Width",
        default=inch(2.5),
        unit='LENGTH',
        precision=4
    )  # type: ignore

    left_stile_width: bpy.props.FloatProperty(
        name="Left Stile Width",
        default=inch(2.5),
        unit='LENGTH',
        precision=4
    )  # type: ignore

    right_stile_width: bpy.props.FloatProperty(
        name="Right Stile Width",
        default=inch(2.5),
        unit='LENGTH',
        precision=4
    )  # type: ignore

    panel_obj = None
    door_style_mod = None

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.get('IS_APPLIED_PANEL_5PIECE')

    def get_door_style_mod(self, obj):
        """Get the door style modifier from the object."""
        for mod in obj.modifiers:
            if mod.type == 'NODES' and 'Door Style' in mod.name:
                return mod
        return None

    def invoke(self, context, event):
        self.panel_obj = context.object
        self.door_style_mod = self.get_door_style_mod(self.panel_obj)
        
        if self.door_style_mod and self.door_style_mod.node_group:
            ng = self.door_style_mod.node_group
            
            def get_input(name):
                if name in ng.interface.items_tree:
                    node_input = ng.interface.items_tree[name]
                    return self.door_style_mod.get(node_input.identifier, None)
                return None
            
            trw = get_input('Top Rail Width')
            brw = get_input('Bottom Rail Width')
            lsw = get_input('Left Stile Width')
            rsw = get_input('Right Stile Width')
            
            if trw is not None:
                self.top_rail_width = trw
            if brw is not None:
                self.bottom_rail_width = brw
            if lsw is not None:
                self.left_stile_width = lsw
            if rsw is not None:
                self.right_stile_width = rsw
        
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def execute(self, context):
        if not self.panel_obj or not self.door_style_mod:
            return {'CANCELLED'}
        
        ng = self.door_style_mod.node_group
        
        def set_input(name, value):
            if name in ng.interface.items_tree:
                node_input = ng.interface.items_tree[name]
                ng.interface_update(context)
                self.door_style_mod[node_input.identifier] = value
        
        set_input('Top Rail Width', self.top_rail_width)
        set_input('Bottom Rail Width', self.bottom_rail_width)
        set_input('Left Stile Width', self.left_stile_width)
        set_input('Right Stile Width', self.right_stile_width)
        
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        box.label(text="5-Piece Panel Dimensions", icon='MOD_SOLIDIFY')
        
        col = box.column(align=True)
        col.prop(self, "top_rail_width")
        col.prop(self, "bottom_rail_width")
        col.separator()
        col.prop(self, "left_stile_width")
        col.prop(self, "right_stile_width")


classes = (
    hb_frameless_OT_update_finished_end,
    hb_frameless_OT_applied_panel_prompts,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
