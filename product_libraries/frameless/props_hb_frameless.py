from typing import Any
import bpy
import os
from bpy.types import (
        Operator,
        Panel,
        PropertyGroup,
        UIList,
        AddonPreferences,
        )
from bpy.props import (
        BoolProperty,
        FloatProperty,
        IntProperty,
        PointerProperty,
        StringProperty,
        CollectionProperty,
        EnumProperty,
        )
from ... import units

def update_top_cabinet_clearance(self,context):
    hb_props = context.scene.home_builder
    self.tall_cabinet_height = hb_props.wall_height-self.default_top_cabinet_clearance
    self.upper_cabinet_height = hb_props.wall_height-self.default_top_cabinet_clearance-self.default_wall_cabinet_location

def update_include_drawer_boxes(self,context):
    print('UPDATE INCLUDE DRAWER BOXES',self.include_drawer_boxes)

def update_show_machining(self,context):
    print('UPDATE SHOW MACHINING',self.show_machining)

def update_frameless_selection_mode(self,context):
    bpy.ops.hb_frameless.toggle_mode(search_obj_name="")

class Frameless_Door_Style(PropertyGroup): 
    show_options: BoolProperty(name="Show Options",description="Show Options",default=False)# type: ignore
    stile_width: FloatProperty(name="Left Stile Width",description="Left Stile Width.",default=units.inch(2.0),unit='LENGTH',precision=4)# type: ignore
    rail_width: FloatProperty(name="Top Rail Width",description="Top Rail Width.",default=units.inch(2.0),unit='LENGTH',precision=4)# type: ignore
    panel_thickness: FloatProperty(name="Panel Thickness",description="Panel Thickness.",default=units.inch(.5),unit='LENGTH',precision=4)# type: ignore
    panel_inset: FloatProperty(name="Panel Inset",description="Panel Inset.",default=units.inch(.25),unit='LENGTH',precision=4)# type: ignore

class Frameless_Scene_Props(PropertyGroup):   
    
    frameless_selection_mode: EnumProperty(name="Frameless Selection Mode",
                    items=[('Cabinets',"Cabinets","Cabinets"),
                           ('Bays',"Bays","Bays"),
                           ('Openings',"Openings","Openings"),
                           ('Interiors',"Interiors","Interiors"),
                           ('Parts',"Parts","Parts")],
                    default='Cabinets',
                    update=update_frameless_selection_mode)# type: ignore

    #UI OPTIONS
    frameless_tabs: EnumProperty(name="Frameless Tabs",
                       items=[('LIBRARY',"Library","Library"),
                              ('OPTIONS',"Options","Options")],
                       default='LIBRARY')# type: ignore  

    show_cabinet_sizes: BoolProperty(name="Show Cabinet Sizes",description="Show Cabinet Sizes.",default=True)# type: ignore
    show_cabinet_library: BoolProperty(name="Show Cabinet Library",description="Show Cabinet Library.",default=True)# type: ignore
    show_corner_cabinet_library: BoolProperty(name="Show Corner Cabinet Library",description="Show Corner Cabinet Library.",default=False)# type: ignore
    show_appliance_library: BoolProperty(name="Show Appliance Library",description="Show Appliance Library.",default=False)# type: ignore
    show_part_library: BoolProperty(name="Show Part Library",description="Show Part Library.",default=False)# type: ignore
    show_user_library: BoolProperty(name="Show User Library",description="Show User Library.",default=True)# type: ignore
    show_general_options: BoolProperty(name="Show General Options",description="Show General Options.",default=False)# type: ignore
    show_material_options: BoolProperty(name="Show Material Options",description="Show Material Options.",default=False)# type: ignore
    show_handle_options: BoolProperty(name="Show Handle Options",description="Show Handle Options.",default=False)# type: ignore
    show_front_options: BoolProperty(name="Show Front Options",description="Show Front Options.",default=False)# type: ignore
    show_drawer_options: BoolProperty(name="Show Drawer Options",description="Show Drawer Options.",default=False)# type: ignore
    show_molding_options: BoolProperty(name="Show Molding Options",description="Show Molding Options.",default=False)# type: ignore
    show_countertop_options: BoolProperty(name="Show Countertop Options",description="Show Countertop Options.",default=False)# type: ignore

    #CABINET OPTIONS
    fill_cabinets: bpy.props.BoolProperty(name="Fill Cabinets",default = True)# type: ignore

    base_exterior: EnumProperty(name="Base Exterior",
                               items=[('Doors',"Doors","Doors"),
                                      ('Door Drawer','Door Drawer','Door Drawer'),
                                      ('2 Drawers','2 Drawers','2 Drawers'),
                                      ('3 Drawers','3 Drawers','3 Drawers'),
                                      ('4 Drawers','4 Drawers','4 Drawers'),
                                      ('Open','Open','Open')],
                               default='Door Drawer')# type: ignore

    include_drawer_boxes: bpy.props.BoolProperty(name="Include Drawer Boxes",default = False,update=update_include_drawer_boxes)# type: ignore

    base_corner_type: EnumProperty(name="Base Corner Type",
                               items=[('Diagonal Corner','Diagonal Corner','Diagonal Corner'),
                                      ('Pie Cut Corner','Pie Cut Corner','Pie Cut Corner'),
                                      ('Pie Cut 2 Drawer Base','Pie Cut 2 Drawer Base','Pie Cut 2 Drawer Base'),
                                      ('Pie Cut 3 Drawer Base','Pie Cut 3 Drawer Base','Pie Cut 3 Drawer Base'),
                                      ('Pie Cut 4 Drawer Base','Pie Cut 4 Drawer Base','Pie Cut 4 Drawer Base')],
                               default='Pie Cut Corner')# type: ignore  

    upper_corner_type: EnumProperty(name="Upper Corner Type",
                               items=[('Diagonal Corner','Diagonal Corner','Diagonal Corner'),
                                      ('Diagonal Stacked Corner','Diagonal Stacked Corner','Diagonal Stacked Corner'),
                                      ('Pie Cut Corner','Pie Cut Corner','Pie Cut Corner'),
                                      ('Pie Cut Stacked Corner','Pie Cut Stacked Corner','Pie Cut Stacked Corner')],
                               default='Pie Cut Corner')# type: ignore  

    upper_and_tall_corner_type: EnumProperty(name="Upper Corner Type",
                               items=[('Diagonal','Diagonal','Diagonal'),
                                      ('Diagonal Stacked','Diagonal Stacked','Diagonal Stacked'),
                                      ('Pie Cut','Pie Cut','Pie Cut'),
                                      ('Pie Cut Stacked','Pie Cut Stacked','Pie Cut Stacked')],
                               default='Diagonal')# type: ignore   

    #APPLIANCE SIZES
    refrigerator_height: FloatProperty(name="Refrigerator Height",
                                         description="Default Refrigerator height",
                                         default=units.inch(62.0),
                                         unit='LENGTH',
                                         precision=4)# type: ignore   

    refrigerator_cabinet_width: FloatProperty(name="Refrigerator Cabinet Width",
                                         description="Default Refrigerator cabinet width",
                                         default=units.inch(38.0),
                                         unit='LENGTH',
                                         precision=4)# type: ignore

    range_width: FloatProperty(name="Range Width",
                               description="Default Dishwasher Width",
                               default=units.inch(36.0),
                               unit='LENGTH',
                               precision=4)# type: ignore     

    dishwasher_width: FloatProperty(name="Dishwasher Width",
                                    description="Default Dishwasher Width",
                                    default=units.inch(24.0),
                                    unit='LENGTH',
                                    precision=4)# type: ignore

    #CABINET SIZES
    default_top_cabinet_clearance: FloatProperty(name="Default Top Cabinet Clearance",
                                                 description="Clearance to Hold Top Cabinets from Ceiling",
                                                 default=units.inch(12.0),
                                                 unit='LENGTH',
                                                 precision=4,
                                                 update=update_top_cabinet_clearance)# type: ignore              

    default_wall_cabinet_location: FloatProperty(name="Default Wall Cabinet Location",
                                                 description="Distance from Floor to Bottom of Wall Cabinet",
                                                 default=units.inch(54.0),
                                                 unit='LENGTH',
                                                 precision=4,
                                                 update=update_top_cabinet_clearance)# type: ignore  
    
    default_cabinet_width: FloatProperty(name="Default Cabinet Width",
                                                 description="Default width for cabinets",
                                                 default=units.inch(36.0),
                                                 unit='LENGTH',
                                                 precision=4)# type: ignore
        
    base_cabinet_depth: FloatProperty(name="Base Cabinet Depth",
                                                 description="Default depth for base cabinets",
                                                 default=units.inch(23.125),
                                                 unit='LENGTH',
                                                 precision=4)# type: ignore
    
    base_cabinet_height: FloatProperty(name="Base Cabinet Height",
                                                  description="Default height for base cabinets",
                                                  default=units.inch(34.5),
                                                  unit='LENGTH',
                                                  precision=4)# type: ignore
    
    base_inside_corner_size: FloatProperty(name="Base Inside Corner Size",
                                           description="Default width and depth for the inside base corner cabinets",
                                           default=units.inch(36.0),
                                           unit='LENGTH',
                                           precision=4)# type: ignore
    
    tall_inside_corner_size: FloatProperty(name="Tall Inside Corner Size",
                                           description="Default width and depth for the inside tall corner cabinets",
                                           default=units.inch(36.0),
                                           unit='LENGTH',
                                           precision=4)# type: ignore

    upper_inside_corner_size: FloatProperty(name="Upper Inside Corner Size",
                                           description="Default width and depth for the inside upper corner cabinets",
                                           default=units.inch(24.0),
                                           unit='LENGTH',
                                           precision=4)# type: ignore

    tall_cabinet_depth: FloatProperty(name="Tall Cabinet Depth",
                                                 description="Default depth for tall cabinets",
                                                 default=units.inch(25.5),
                                                 unit='LENGTH',
                                                 precision=4)# type: ignore
    
    tall_cabinet_height: FloatProperty(name="Tall Cabinet Height",
                                                  description="Default height for tall cabinets",
                                                  default=units.inch(84.0),
                                                  unit='LENGTH',
                                                  precision=4)# type: ignore
    
    upper_cabinet_depth: FloatProperty(name="Upper Cabinet Depth",
                                                  description="Default depth for upper cabinets",
                                                  default=units.inch(13.0),
                                                  unit='LENGTH',
                                                  precision=4)# type: ignore
    
    upper_cabinet_height: FloatProperty(name="Upper Cabinet Height",
                                                   description="Default height for upper cabinets",
                                                   default=units.inch(30),
                                                   unit='LENGTH',
                                                   precision=4)# type: ignore
    
    base_width_blind: FloatProperty(name="Base Width Blind",
                                               description="Default width for base blind corner cabinets",
                                               default=units.inch(48.0),
                                               unit='LENGTH',
                                               precision=4)# type: ignore
    
    tall_width_blind: FloatProperty(name="Tall Width Blind",
                                               description="Default width for tall blind corner cabinets",
                                               default=units.inch(48.0),
                                               unit='LENGTH',
                                               precision=4)# type: ignore

    upper_width_blind: FloatProperty(name="Upper Width Blind",
                                                description="Default width for upper blind corner cabinets",
                                                default=units.inch(36.0),
                                                unit='LENGTH',
                                                precision=4)# type: ignore
    
    top_stacked_cabinet_height: FloatProperty(name="Oven Cabinet Width",
                                    description="Default face frame Refrigerator cabinet width",
                                    default=units.inch(15),
                                    unit='LENGTH',
                                    precision=4)# type: ignore
    
    #CABINET GENERAL CONSTRUCTION OPTIONS
    show_machining: bpy.props.BoolProperty(name="Show Machining",default = True,update=update_show_machining)# type: ignore

    default_carcass_part_thickness: FloatProperty(name="Default Carcass Part Thickness",
                                                 description="",
                                                 default=units.inch(.75),
                                                 unit='LENGTH')# type: ignore

    default_toe_kick_height: FloatProperty(name="Default Toe Kick Height",
                                                 description="",
                                                 default=units.inch(4),
                                                 unit='LENGTH')# type: ignore
    
    default_toe_kick_setback: FloatProperty(name="Default Toe Kick Setback",
                                                 description="",
                                                 default=units.inch(2.5),
                                                 unit='LENGTH')# type: ignore
    
    default_toe_kick_type: EnumProperty(name="Toe Kick Type",
                       items=[('Notch Ends to Floor',"Notch Ends to Floor","Notch Ends to Floor"),
                              ('Ladder Style',"Ladder Style","Ladder Style"),
                              ('Leg Levelers',"Leg Levelers","Leg Levelers")],
                       default='Ladder Style')# type: ignore

    base_top_construction: EnumProperty(name="Base Top Construction",
                       items=[('Cutout',"Cutout","Cutout"),
                              ('Full Top',"Full Top","Full Top"),
                              ('Stretchers',"Stretchers","Stretchers")],
                       default='Cutout')# type: ignore

    equal_drawer_stack_heights: BoolProperty(name="Equal Drawer Stack Heights", 
                                             description="Check this make all drawer stack heights equal. Otherwise the Top Drawer Height will be set.", 
                                                        default=True)# type: ignore
    
    top_drawer_front_height: FloatProperty(name="Top Drawer Front Height",
                                           description="Default top drawer front height.",
                                           default=units.inch(6.0),
                                           unit='LENGTH')# type: ignore

    door_styles: CollectionProperty(type=Frameless_Door_Style, name="Door Styles")# type: ignore
    
    #CABINET PULL OPTIONS
    current_door_pull_object: PointerProperty(type=bpy.types.Object)# type: ignore
    current_drawer_front_pull_object: PointerProperty(type=bpy.types.Object)# type: ignore

    pull_dim_from_edge: FloatProperty(name="Pull Distance From Edge",
                                                 description="Distance from Edge of Door to center of pull",
                                                 default=units.inch(2.0),
                                                 unit='LENGTH')# type: ignore

    pull_vertical_location_base: FloatProperty(name="Pull Vertical Location Base",
                                                 description="Distance from Top of Base Door to Top of Pull",
                                                 default=units.inch(1.5),
                                                 unit='LENGTH')# type: ignore

    pull_vertical_location_tall: FloatProperty(name="Pull Vertical Location Base",
                                                 description="Distance from Bottom of Tall Door to Center of Pull",
                                                 default=units.inch(45),
                                                 unit='LENGTH')# type: ignore

    pull_vertical_location_upper: FloatProperty(name="Pull Vertical Location Base",
                                                 description="Distance from Bottom of Upper Door to Bottom of Pull",
                                                 default=units.inch(1.5),
                                                 unit='LENGTH')# type: ignore

    pull_vertical_location_drawers: FloatProperty(name="Pull Vertical Location Drawers",
                                                 description="Distance from Top of Drawer Front to Center of Pull",
                                                 default=units.inch(1.5),
                                                 unit='LENGTH')# type: ignore
    
    center_pulls_on_drawer_front: BoolProperty(name="Center Pulls on Drawer Front", 
                                                        description="Check this to center pulls on drawer fronts. Otherwise vertical location will be used.", 
                                                        default=True)# type: ignore

    def draw_cabinet_sizes_ui(self,layout,context):
        unit_settings = context.scene.unit_settings      
        row = layout.row()
        row.label(text="Top Cabinet Clearance:")
        row.prop(self,'default_top_cabinet_clearance',text="")  
        row.operator('hb_frameless.update_cabinet_sizes',text="",icon='FILE_REFRESH')     
        row = layout.row()
        row.label(text="Upper Cabinet Dim to Floor:")
        row.prop(self,'default_wall_cabinet_location',text="")  
        row.label(text="",icon='BLANK1')
        row = layout.row()
        row.label(text="Sizes")
        row.label(text="Base")
        row.label(text="Tall")      
        row.label(text="Upper")
        row = layout.row()
        row.label(text="Depth:")
        row.prop(self,'base_cabinet_depth',text="")
        row.prop(self,'tall_cabinet_depth',text="")
        row.prop(self,'upper_cabinet_depth',text="")   
        row = layout.row()
        row.label(text="Height:")
        row.prop(self,'base_cabinet_height',text="")
        row.label(text=units.unit_to_string(unit_settings,self.tall_cabinet_height))
        row.label(text=units.unit_to_string(unit_settings,self.upper_cabinet_height))
        row = layout.row()
        row.label(text="Stacked Top Cabinet Height:") 
        row.prop(self,'top_stacked_cabinet_height',text="")

    def draw_user_library_ui(self,layout,context):
        from . import ops_hb_frameless
        
        # Header row with refresh and folder buttons
        row = layout.row()
        row.label(text="User Library")
        row.operator('hb_frameless.refresh_user_library', text="", icon='FILE_REFRESH')
        row.operator('hb_frameless.open_user_library_folder', text="", icon='FILE_FOLDER')
        
        # Create/Save buttons
        col = layout.column(align=True)
        col.operator('hb_frameless.create_cabinet_group', text="Create Cabinet Group", icon='ADD')
        col.operator('hb_frameless.save_cabinet_group_to_user_library', text="Save to Library", icon='FILE_TICK')
        
        layout.separator()
        
        # Get library items
        library_items = ops_hb_frameless.get_user_library_items()
        
        if not library_items:
            box = layout.box()
            box.label(text="No saved cabinet groups", icon='INFO')
            box.label(text="Save a cabinet group to see it here")
        else:
            # Display library items
            box = layout.box()
            box.label(text=f"Saved Groups ({len(library_items)})", icon='ASSET_MANAGER')
            
            # Grid layout for items
            flow = box.column_flow(columns=2, align=True)
            
            for item in library_items:
                item_box = flow.box()
                item_box.scale_y = 0.9
                
                # Item name with delete button
                row = item_box.row()
                row.label(text=item['name'], icon='OUTLINER_OB_GROUP_INSTANCE')
                del_op = row.operator('hb_frameless.delete_library_item', text="", icon='X', emboss=False)
                del_op.filepath = item['filepath']
                del_op.item_name = item['name']
                
                # Load button
                op = item_box.operator('hb_frameless.load_cabinet_group_from_library', 
                                       text="Add to Scene", icon='IMPORT')
                op.filepath = item['filepath']

    def draw_library_ui(self,layout,context):
        row = layout.row(align=True)
        row.prop_enum(self, "frameless_selection_mode", 'Cabinets', icon='MESH_CUBE')
        row.prop_enum(self, "frameless_selection_mode", 'Bays', icon='MESH_CUBE')
        row.prop_enum(self, "frameless_selection_mode", 'Openings', icon='OBJECT_DATAMODE')
        row.prop_enum(self, "frameless_selection_mode", 'Interiors', icon='OBJECT_HIDDEN')    
        row.prop_enum(self, "frameless_selection_mode", 'Parts', icon='EDITMODE_HLT') 

        layout.separator()

        col = layout.column(align=True)
        row = col.row(align=True)
        row.scale_y = 1.3
        row.prop_enum(self, "frameless_tabs", 'LIBRARY', icon='ASSET_MANAGER')
        row.prop_enum(self, "frameless_tabs", 'OPTIONS', icon='PREFERENCES') 
        col.separator() 
        if self.frameless_tabs == 'LIBRARY':
            box = col.box()
            row = box.row()
            row.alignment = 'LEFT'        
            row.prop(self,'show_cabinet_sizes',text="Cabinet Sizes",icon='TRIA_DOWN' if self.show_cabinet_sizes else 'TRIA_RIGHT',emboss=False)
            if self.show_cabinet_sizes:           
                self.draw_cabinet_sizes_ui(box,context)

            box = col.box()
            row = box.row()
            row.alignment = 'LEFT'        
            row.prop(self,'show_cabinet_library',text="Cabinets",icon='TRIA_DOWN' if self.show_cabinet_library else 'TRIA_RIGHT',emboss=False)
            if self.show_cabinet_library:
                row = box.row()
                row.prop(self,'fill_cabinets',text="Fill")
                if not self.fill_cabinets:
                    row.prop(self,'default_cabinet_width',text="Width")

                row = box.row()
                row.alignment = 'LEFT'
                row.label(text="Base:")
                row.prop(self,'base_exterior',text="")
                row.alignment = 'LEFT'
                row.label(text="Include Drawer Boxes:")
                row.prop(self,'include_drawer_boxes',text="")    

                row = box.row()
                row.scale_y = 1.5                   
                row.operator('hb_frameless.draw_cabinet',text="Base").cabinet_name = 'Base'
                row.operator('hb_frameless.draw_cabinet',text="Tall").cabinet_name = 'Tall'
                row.operator('hb_frameless.draw_cabinet',text="Upper").cabinet_name = 'Upper'
                row = box.row()
                row.scale_y = 1.5   
                row.operator('hb_frameless.draw_cabinet',text="Lap Drawer").cabinet_name = 'Lap Drawer'
                row.operator('hb_frameless.draw_cabinet',text="Tall Stacked").cabinet_name = 'Tall Stacked'
                row.operator('hb_frameless.draw_cabinet',text="Upper Stacked").cabinet_name = 'Upper Stacked'  

            box = col.box()
            row = box.row()
            row.alignment = 'LEFT'        
            row.prop(self,'show_corner_cabinet_library',text="Corner Cabinets",icon='TRIA_DOWN' if self.show_corner_cabinet_library else 'TRIA_RIGHT',emboss=False)
            if self.show_corner_cabinet_library:

                row = box.row()
                row.label(text="Corner Cabinet Sizes")
                row = box.row()
                row.prop(self,'base_inside_corner_size',text="Base")
                row.prop(self,'tall_inside_corner_size',text="Tall")
                row.prop(self,'upper_inside_corner_size',text="Upper")
                row = box.row()
                row.label(text="Base Cabinet Type")
                row.prop(self,'base_corner_type',text="")
                row = box.row()
                row.label(text="Upper and Tall Cabinet Type")
                row.prop(self,'upper_and_tall_corner_type',text="")                

                row = box.row()
                row.scale_y = 1.5                   
                row.operator('hb_frameless.draw_cabinet',text="Base").cabinet_name = 'Base'
                row.operator('hb_frameless.draw_cabinet',text="Tall").cabinet_name = 'Tall'
                row.operator('hb_frameless.draw_cabinet',text="Upper").cabinet_name = 'Upper'
                row = box.row()
                row.scale_y = 1.5   
                row.operator('hb_frameless.draw_cabinet',text="Base Blind").cabinet_name = 'Base Blind'
                row.operator('hb_frameless.draw_cabinet',text="Tall Blind").cabinet_name = 'Tall Blind'
                row.operator('hb_frameless.draw_cabinet',text="Upper Blind").cabinet_name = 'Upper Blind'  

            box = col.box()
            row = box.row()
            row.alignment = 'LEFT'        
            row.prop(self,'show_appliance_library',text="Appliances",icon='TRIA_DOWN' if self.show_appliance_library else 'TRIA_RIGHT',emboss=False)
            if self.show_appliance_library:
                row = box.row()
                row.label(text="Refrigerator Height")
                row.prop(self,'refrigerator_height',text="")
                row = box.row()
                row.label(text="Widths")
                row = box.row()
                row.prop(self,'refrigerator_cabinet_width',text="Refrigerator")
                row = box.row()
                row.prop(self,'dishwasher_width',text="Dishwasher")
                row.prop(self,'range_width',text="Range")       

                row = box.row()
                row.scale_y = 1.5                   
                row.operator('hb_frameless.draw_cabinet',text="Base Built-In").cabinet_name = 'Base Built-In'
                row.operator('hb_frameless.draw_cabinet',text="Tall Built-In").cabinet_name = 'Tall Built-In'
                row.operator('hb_frameless.draw_cabinet',text="Dishwasher").cabinet_name = 'Dishwasher'
                row = box.row()
                row.scale_y = 1.5   
                row.operator('hb_frameless.draw_cabinet',text="Range").cabinet_name = 'Range'
                row.operator('hb_frameless.draw_cabinet',text="Refrigerator").cabinet_name = 'Refrigerator'
                row.operator('hb_frameless.draw_cabinet',text="Upper Blind").cabinet_name = 'Upper Blind'  

            box = col.box()
            row = box.row()
            row.alignment = 'LEFT'        
            row.prop(self,'show_part_library',text="Parts & Miscellaneous",icon='TRIA_DOWN' if self.show_part_library else 'TRIA_RIGHT',emboss=False)
            if self.show_part_library:
                row = box.row()
                row.scale_y = 1.5                   
                row.operator('hb_frameless.draw_cabinet',text="Misc Part").cabinet_name = 'Misc Part'
                row.operator('hb_frameless.draw_cabinet',text="Countertop").cabinet_name = 'Countertop'
                row.operator('hb_frameless.draw_cabinet',text="Half Wall").cabinet_name = 'Half Wall'
                row = box.row()
                row.scale_y = 1.5   
                row.operator('hb_frameless.draw_cabinet',text="Floating Shelves").cabinet_name = 'Floating Shelves'
                row.operator('hb_frameless.draw_cabinet',text="Leg").cabinet_name = 'Leg'
                row.operator('hb_frameless.draw_cabinet',text="Support Frame").cabinet_name = 'Support Frame'  
                row = box.row()
                row.scale_y = 1.5   
                row.operator('hb_frameless.draw_cabinet',text="Floating Shelves").cabinet_name = 'Floating Shelves'
                row.operator('hb_frameless.draw_cabinet',text="Leg Column").cabinet_name = 'Leg Column'
                row.operator('hb_frameless.draw_cabinet',text="Valance").cabinet_name = 'Valance'                 

            box = col.box()
            row = box.row()
            row.alignment = 'LEFT'        
            row.prop(self,'show_user_library',text="User",icon='TRIA_DOWN' if self.show_user_library else 'TRIA_RIGHT',emboss=False)
            if self.show_user_library:
                self.draw_user_library_ui(box,context)

        if self.frameless_tabs == 'OPTIONS':
            box = col.box()
            row = box.row()
            row.alignment = 'LEFT'        
            row.prop(self,'show_general_options',text="General",icon='TRIA_DOWN' if self.show_general_options else 'TRIA_RIGHT',emboss=False)
            if self.show_general_options:

                self.draw_cabinet_options_general(box,context)

            box = col.box()
            row = box.row()
            row.alignment = 'LEFT'        
            row.prop(self,'show_material_options',text="Materials",icon='TRIA_DOWN' if self.show_material_options else 'TRIA_RIGHT',emboss=False)
            if self.show_material_options:
                size_box = box.box()
                # self.draw_cabinet_options_materials(size_box,context)

            box = col.box()
            row = box.row()
            row.alignment = 'LEFT'        
            row.prop(self,'show_handle_options',text="Handles",icon='TRIA_DOWN' if self.show_handle_options else 'TRIA_RIGHT',emboss=False)
            if self.show_handle_options:
                size_box = box.box()
                self.draw_cabinet_options_handles(size_box,context)

            box = col.box()
            row = box.row()
            row.alignment = 'LEFT'        
            row.prop(self,'show_drawer_options',text="Drawer Boxes",icon='TRIA_DOWN' if self.show_drawer_options else 'TRIA_RIGHT',emboss=False)
            if self.show_drawer_options:
                size_box = box.box()
                # row = size_box.row()
                # row.operator('frameless.open_doors',text="Open Drawers").open_door = True
                # row.operator('frameless.open_doors',text="Close Drawers").open_door = False  
                # self.draw_cabinet_options_drawers(size_box,context)

            box = col.box()
            row = box.row()
            row.alignment = 'LEFT'        
            row.prop(self,'show_front_options',text="Door and Drawer Front Styles",icon='TRIA_DOWN' if self.show_front_options else 'TRIA_RIGHT',emboss=False)
            if self.show_front_options:
                row = box.row()
                row.operator('hb_frameless.add_door_style',text="Add Door Style",icon='ADD')                
                for index, door_style in enumerate[Any](self.door_styles):
                    door_box = box.box()
                    row = door_box.row()
                    row.alignment = 'LEFT'        
                    row.prop(door_style,'show_options',text=door_style.name,icon='TRIA_DOWN' if door_style.show_options else 'TRIA_RIGHT',emboss=False) 
                    row.operator('hb_frameless.update_door_and_drawer_front_style',text="",icon='FILE_REFRESH').selected_index = index                                       
                    if door_style.show_options:
                        door_box.prop(door_style,'name',text="Name")
                        door_box.prop(door_style,'stile_width',text="Stile Width")
                        door_box.prop(door_style,'rail_width',text="Rail Width")
                        door_box.prop(door_style,'panel_thickness',text="Panel Thickness")
                        door_box.prop(door_style,'panel_inset',text="Panel Inset")                
                
            box = col.box()
            row = box.row()
            row.alignment = 'LEFT'        
            row.prop(self,'show_molding_options',text="Moldings",icon='TRIA_DOWN' if self.show_molding_options else 'TRIA_RIGHT',emboss=False)
            if self.show_molding_options:
                size_box = box.box()
                # self.draw_cabinet_options_molding(size_box,context)

    def draw_cabinet_options_general(self,layout,context):
        unit_settings = context.scene.unit_settings
        size_box = layout.box()
        row = size_box.row()
        row.prop(self,'show_machining',text="Show Machining")
        row = size_box.row()
        row.label(text="Toe Kick:")
        row.operator('hb_frameless.update_toe_kick_prompts',text="",icon='FILE_REFRESH')
        row = size_box.row()
        row.prop(self,'default_toe_kick_height',text="Height")
        row.prop(self,'default_toe_kick_setback',text="Setback")
        row = size_box.row()
        row.prop(self,'default_toe_kick_type',text="Type")
        size_box = layout.box()
        row = size_box.row()
        row.label(text="Base Top Construction:")
        row.prop(self,'base_top_construction',text="")
        row.operator('hb_frameless.update_base_top_construction_prompts',text="",icon='FILE_REFRESH')        
        size_box = layout.box()            
        row = size_box.row()
        row.label(text="Drawers:")
        row.operator('hb_frameless.update_drawer_front_height_prompts',text="",icon='FILE_REFRESH')
        row = size_box.row()
        row.prop(self,'equal_drawer_stack_heights')
        if not self.equal_drawer_stack_heights:
            row = size_box.row()
            row.prop(self,'top_drawer_front_height',text="Top Drawer Front Height")

        # lib_col = layout.column(align=True)
        # ctop_box = lib_col.box()
        # row = ctop_box.row()
        # row.label(text="Counter Tops:")
        # row.operator('frameless.update_countertop_prompts',text="",icon='FILE_REFRESH')   
        # row = ctop_box.row(align=True) 
        # row.prop(self,'countertop_material',text="Material")  
        # row = ctop_box.row(align=True)
        # row.label(text="Thickness:")              
        # row.prop(self,'countertop_thickness',text="")
        # row = ctop_box.row(align=True) 
        # row.label(text="Overhang:")
        # row.prop(self,'countertop_overhang',text="")
        # row = ctop_box.row(align=True)
        # row.operator('frameless.add_countertop',text="Add",icon='ADD')
        # row = ctop_box.row(align=True)
        # row.operator('frameless.delete_countertop',text="Clear",icon='X')

    def draw_cabinet_options_handles(self,layout,context):
        size_box = layout.box()
        row = size_box.row()
        row.label(text="Door Pulls:")
        # row.operator('hb_frameless.update_door_pull_prompts',text="",icon='FILE_REFRESH')
        row = size_box.row()
        row.label(text="Door Pull:")
        row.prop(self,'current_door_pull_object',text="")
        row = size_box.row()
        row.label(text="Drawer Front Pull:")
        row.prop(self,'current_drawer_front_pull_object',text="")
        row = size_box.row()
        row.prop(self,'pull_dim_from_edge',text="Pull Distance From Edge")
        row = size_box.row()
        row.prop(self,'pull_vertical_location_base',text="Pull Vertical Location Base")
        row = size_box.row()
        row.prop(self,'pull_vertical_location_tall',text="Pull Vertical Location Tall")
        row = size_box.row()
        row.prop(self,'pull_vertical_location_upper',text="Pull Vertical Location Upper")
        row = size_box.row()
        row.prop(self,'pull_vertical_location_drawers',text="Pull Vertical Location Drawers")
        row = size_box.row()
        row.prop(self,'center_pulls_on_drawer_front',text="Center Pulls on Drawer Front")

    @classmethod
    def register(cls):
        bpy.types.Scene.hb_frameless = PointerProperty(
            name="Frameless Props",
            description="Frameless Props",
            type=cls,
        )
        
    @classmethod
    def unregister(cls):
        del bpy.types.Scene.hb_frameless            


classes = (
    Frameless_Door_Style,
    Frameless_Scene_Props,
)

register, unregister = bpy.utils.register_classes_factory(classes)         