import bpy
import math
import os
from ...hb_types import GeoNodeObject, GeoNodeCage, GeoNodeCutpart, GeoNodeHardware, GeoNodeDrawerBox, CabinetPartModifier
from ... import hb_project
from ... import units
from ...units import inch

class Cabinet(GeoNodeCage):

    default_exterior = "Doors"

    width = inch(18)
    height = inch(34)
    depth = inch(24)

    def add_properties_common(self):
        props = bpy.context.scene.hb_frameless
        self.add_property('Material Thickness', 'DISTANCE', props.default_carcass_part_thickness)

    def add_properties_toe_kick(self):
        props = bpy.context.scene.hb_frameless
        self.add_property('Toe Kick Height', 'DISTANCE', props.default_toe_kick_height)
        self.add_property('Toe Kick Setback', 'DISTANCE', props.default_toe_kick_setback)
        self.add_property('Remove Bottom', 'CHECKBOX', False)
    
    def add_properties_base_top(self):
        """Add base top construction properties."""
        props = bpy.context.scene.hb_frameless
        if props.base_top_construction == "Full Top":
            base_top_construction_index = 0
        elif props.base_top_construction == "Stretchers":
            base_top_construction_index = 1
        self.add_property('Base Top Construction', 'COMBOBOX', base_top_construction_index, combobox_items=["Full Top", "Stretchers", "Sink"])
        self.add_property('Stretcher Width', 'DISTANCE', inch(4))
        self.add_property('Sink Apron Width', 'DISTANCE', inch(7))
    
    def add_cage_to_bay(self,cage):
        cage.create()
        for child in self.obj.children_recursive:
            if 'IS_FRAMELESS_BAY_CAGE' in child:
                bay = CabinetBay(child)
                cage.obj.parent = child
                dim_x = bay.var_input('Dim X', 'dim_x')
                dim_y = bay.var_input('Dim Y', 'dim_y')
                dim_z = bay.var_input('Dim Z', 'dim_z') 
                cage.driver_input('Dim X', 'dim_x',[dim_x])
                cage.driver_input('Dim Y', 'dim_y',[dim_y])
                cage.driver_input('Dim Z', 'dim_z',[dim_z])

    def create_cabinet(self,name):
        super().create(name)
        self.obj['IS_FRAMELESS_CABINET_CAGE'] = True
        self.obj['MENU_ID'] = 'HOME_BUILDER_MT_cabinet_commands'
        self.obj.display_type = 'WIRE'
        
        self.set_input('Dim X', self.width)
        self.set_input('Dim Y', self.depth)
        self.set_input('Dim Z', self.height)
        self.set_input('Mirror Y', True)

    def create_base_carcass(self,name):
        self.create_cabinet(name)

        self.add_properties_common()
        self.add_properties_toe_kick()
        self.add_properties_base_top()

        dim_x = self.var_input('Dim X', 'dim_x')
        dim_y = self.var_input('Dim Y', 'dim_y')
        dim_z = self.var_input('Dim Z', 'dim_z')

        mt = self.var_prop('Material Thickness', 'mt')
        tkh = self.var_prop('Toe Kick Height', 'tkh')
        tks = self.var_prop('Toe Kick Setback', 'tks')
        rb = self.var_prop('Remove Bottom', 'rb')
        btc = self.var_prop('Base Top Construction', 'btc')  # 0=Full Top, 1=Stretchers, 2=Sink
        sw = self.var_prop('Stretcher Width', 'sw')
        saw = self.var_prop('Sink Apron Width', 'saw')

        left_side = CabinetSideNotched()
        left_side.create('Left Side',tkh,tks,mt)
        left_side.obj.parent = self.obj
        left_side.obj.rotation_euler.y = math.radians(-90)
        left_side.driver_input("Length", 'dim_z', [dim_z])
        left_side.driver_input("Width", 'dim_y', [dim_y])
        left_side.driver_input("Thickness", 'mt', [mt])
        left_side.set_input("Mirror Y", True)
        left_side.set_input("Mirror Z", True)

        right_side = CabinetSideNotched()
        right_side.create('Right Side',tkh,tks,mt)
        right_side.obj.parent = self.obj
        right_side.driver_location('x', 'dim_x',[dim_x])
        right_side.obj.rotation_euler.y = math.radians(-90)
        right_side.driver_input("Length", 'dim_z', [dim_z])
        right_side.driver_input("Width", 'dim_y', [dim_y])
        right_side.driver_input("Thickness", 'mt', [mt])
        right_side.set_input("Mirror Y", True)
        right_side.set_input("Mirror Z", False)

        bottom = CabinetPart()
        bottom.create('Bottom')
        bottom.obj.parent = self.obj
        bottom.driver_location('x', 'mt',[mt])
        bottom.driver_location('z', 'tkh',[tkh])
        bottom.driver_input("Length", 'dim_x-(mt*2)', [dim_x,mt])
        bottom.driver_input("Width", 'dim_y', [dim_y])
        bottom.driver_input("Thickness", 'mt', [mt])
        bottom.set_input("Mirror Y", True)
        bottom.set_input("Mirror Z", False)
        bottom.driver_hide('IF(rb==1,True,False)', [rb])

        back = CabinetPart()
        back.create('Back')
        back.obj.parent = self.obj
        back.obj.rotation_euler.x = math.radians(90)
        back.obj.rotation_euler.y = math.radians(-90)
        back.driver_location('x', 'mt',[mt])
        back.driver_location('z', 'IF(rb==1,0,tkh+mt)',[rb,tkh,mt])
        back.driver_input("Length", 'IF(rb==1,dim_z,dim_z-tkh-mt)-IF(btc==2,0,mt)', [rb,dim_z,tkh,mt,btc])
        back.driver_input("Width", 'dim_x-(mt*2)', [dim_x,mt])
        back.driver_input("Thickness", 'mt', [mt])
        back.set_input("Mirror Y", True)

        toe_kick = CabinetPart()
        toe_kick.create('Toe Kick')
        toe_kick.obj.parent = self.obj
        toe_kick.obj.rotation_euler.x = math.radians(-90)
        toe_kick.driver_location('x', 'mt',[mt])
        toe_kick.driver_location('y', '-dim_y+tks',[dim_y,tks])
        toe_kick.driver_input("Length", 'dim_x-(mt*2)', [dim_x,mt])
        toe_kick.driver_input("Width", 'tkh', [tkh])
        toe_kick.driver_input("Thickness", 'mt', [mt])
        toe_kick.set_input("Mirror Y", True)
        toe_kick.set_input("Mirror Z", False)
        toe_kick.driver_hide('IF(rb==1,True,False)', [rb])

        # Full Top - shown when btc==0
        top = CabinetPart()
        top.create('Top')
        top.obj.parent = self.obj
        top.driver_location('x', 'mt',[mt])
        top.driver_location('z', 'dim_z',[dim_z])
        top.driver_input("Length", 'dim_x-(mt*2)', [dim_x,mt])
        top.driver_input("Width", 'dim_y', [dim_y])
        top.driver_input("Thickness", 'mt', [mt])
        top.set_input("Mirror Y", True)
        top.set_input("Mirror Z", True)
        top.driver_hide('IF(btc!=0,True,False)', [btc])

        # Front Stretcher - shown when btc==1 (Stretchers)
        front_stretcher = CabinetPart()
        front_stretcher.create('Front Stretcher')
        front_stretcher.obj.parent = self.obj
        front_stretcher.driver_location('x', 'mt', [mt])
        front_stretcher.driver_location('y', '-dim_y', [dim_y])
        front_stretcher.driver_location('z', 'dim_z', [dim_z])
        front_stretcher.driver_input("Length", 'dim_x-(mt*2)', [dim_x, mt])
        front_stretcher.driver_input("Width", 'sw', [sw])
        front_stretcher.driver_input("Thickness", 'mt', [mt])
        front_stretcher.set_input("Mirror Z", True)
        front_stretcher.driver_hide('IF(btc!=1,True,False)', [btc])
        front_stretcher.obj['Finish Top'] = False
        front_stretcher.obj['Finish Bottom'] = False

        # Back Stretcher - shown when btc==1 (Stretchers)
        back_stretcher = CabinetPart()
        back_stretcher.create('Back Stretcher')
        back_stretcher.obj.parent = self.obj
        back_stretcher.driver_location('x', 'mt', [mt])
        back_stretcher.driver_location('y', '-sw', [sw])
        back_stretcher.driver_location('z', 'dim_z', [dim_z])
        back_stretcher.driver_input("Length", 'dim_x-(mt*2)', [dim_x, mt])
        back_stretcher.driver_input("Width", 'sw', [sw])
        back_stretcher.driver_input("Thickness", 'mt', [mt])
        back_stretcher.set_input("Mirror Z", True)
        back_stretcher.driver_hide('IF(btc!=1,True,False)', [btc])
        back_stretcher.obj['Finish Top'] = False
        back_stretcher.obj['Finish Bottom'] = False

        # Sink Apron Front - shown when btc==2 (Sink)
        sink_apron = CabinetPart()
        sink_apron.create('Sink Apron')
        sink_apron.obj.parent = self.obj
        sink_apron.obj.rotation_euler.x = math.radians(-90)
        sink_apron.driver_location('x', 'mt', [mt])
        sink_apron.driver_location('y', '-dim_y', [dim_y])
        sink_apron.driver_location('z', 'dim_z', [dim_z])
        sink_apron.driver_input("Length", 'dim_x-(mt*2)', [dim_x, mt])
        sink_apron.driver_input("Width", 'saw', [saw])
        sink_apron.driver_input("Thickness", 'mt', [mt])
        sink_apron.driver_hide('IF(btc!=2,True,False)', [btc])

        opening = CabinetBay()
        opening.create("Bay")
        opening.obj.parent = self.obj
        opening.driver_location('x', 'mt',[mt])
        opening.driver_location('y', '-dim_y',[dim_y])
        opening.driver_location('z', 'tkh+IF(rb,0,mt)',[tkh,mt,rb])
        opening.driver_input("Dim X", 'dim_x-(mt*2)', [dim_x,mt])
        opening.driver_input("Dim Y", 'dim_y-mt', [dim_y,mt])
        opening.driver_input("Dim Z", 'dim_z-tkh-IF(rb,0,mt)-mt', [dim_z,tkh,mt,rb])

    def create_tall_carcass(self,name):
        """Create tall cabinet carcass - always uses full top, no stretcher options."""
        self.create_cabinet(name)

        self.add_properties_common()
        self.add_properties_toe_kick()
        # Note: No add_properties_base_top() - tall cabinets always have full top

        dim_x = self.var_input('Dim X', 'dim_x')
        dim_y = self.var_input('Dim Y', 'dim_y')
        dim_z = self.var_input('Dim Z', 'dim_z')

        mt = self.var_prop('Material Thickness', 'mt')
        tkh = self.var_prop('Toe Kick Height', 'tkh')
        tks = self.var_prop('Toe Kick Setback', 'tks')
        rb = self.var_prop('Remove Bottom', 'rb')

        left_side = CabinetSideNotched()
        left_side.create('Left Side',tkh,tks,mt)
        left_side.obj.parent = self.obj
        left_side.obj.rotation_euler.y = math.radians(-90)
        left_side.driver_input("Length", 'dim_z', [dim_z])
        left_side.driver_input("Width", 'dim_y', [dim_y])
        left_side.driver_input("Thickness", 'mt', [mt])
        left_side.set_input("Mirror Y", True)
        left_side.set_input("Mirror Z", True)

        right_side = CabinetSideNotched()
        right_side.create('Right Side',tkh,tks,mt)
        right_side.obj.parent = self.obj
        right_side.driver_location('x', 'dim_x',[dim_x])
        right_side.obj.rotation_euler.y = math.radians(-90)
        right_side.driver_input("Length", 'dim_z', [dim_z])
        right_side.driver_input("Width", 'dim_y', [dim_y])
        right_side.driver_input("Thickness", 'mt', [mt])
        right_side.set_input("Mirror Y", True)
        right_side.set_input("Mirror Z", False)

        bottom = CabinetPart()
        bottom.create('Bottom')
        bottom.obj.parent = self.obj
        bottom.driver_location('x', 'mt',[mt])
        bottom.driver_location('z', 'tkh',[tkh])
        bottom.driver_input("Length", 'dim_x-(mt*2)', [dim_x,mt])
        bottom.driver_input("Width", 'dim_y', [dim_y])
        bottom.driver_input("Thickness", 'mt', [mt])
        bottom.set_input("Mirror Y", True)
        bottom.set_input("Mirror Z", False)
        bottom.driver_hide('IF(rb==1,True,False)', [rb])

        back = CabinetPart()
        back.create('Back')
        back.obj.parent = self.obj
        back.obj.rotation_euler.x = math.radians(90)
        back.obj.rotation_euler.y = math.radians(-90)
        back.driver_location('x', 'mt',[mt])
        back.driver_location('z', 'IF(rb==1,0,tkh+mt)',[rb,tkh,mt])
        back.driver_input("Length", 'IF(rb==1,dim_z,dim_z-tkh-mt)-mt', [rb,dim_z,tkh,mt])
        back.driver_input("Width", 'dim_x-(mt*2)', [dim_x,mt])
        back.driver_input("Thickness", 'mt', [mt])
        back.set_input("Mirror Y", True)

        toe_kick = CabinetPart()
        toe_kick.create('Toe Kick')
        toe_kick.obj.parent = self.obj
        toe_kick.obj.rotation_euler.x = math.radians(-90)
        toe_kick.driver_location('x', 'mt',[mt])
        toe_kick.driver_location('y', '-dim_y+tks',[dim_y,tks])
        toe_kick.driver_input("Length", 'dim_x-(mt*2)', [dim_x,mt])
        toe_kick.driver_input("Width", 'tkh', [tkh])
        toe_kick.driver_input("Thickness", 'mt', [mt])
        toe_kick.set_input("Mirror Y", True)
        toe_kick.set_input("Mirror Z", False)
        toe_kick.driver_hide('IF(rb==1,True,False)', [rb])

        # Full Top - always present for tall cabinets
        top = CabinetPart()
        top.create('Top')
        top.obj.parent = self.obj
        top.driver_location('x', 'mt',[mt])
        top.driver_location('z', 'dim_z',[dim_z])
        top.driver_input("Length", 'dim_x-(mt*2)', [dim_x,mt])
        top.driver_input("Width", 'dim_y', [dim_y])
        top.driver_input("Thickness", 'mt', [mt])
        top.set_input("Mirror Y", True)
        top.set_input("Mirror Z", True)

        opening = CabinetBay()
        opening.create("Bay")
        opening.obj.parent = self.obj
        opening.driver_location('x', 'mt',[mt])
        opening.driver_location('y', '-dim_y',[dim_y])
        opening.driver_location('z', 'tkh+IF(rb,0,mt)',[tkh,mt,rb])
        opening.driver_input("Dim X", 'dim_x-(mt*2)', [dim_x,mt])
        opening.driver_input("Dim Y", 'dim_y-mt', [dim_y,mt])
        opening.driver_input("Dim Z", 'dim_z-tkh-IF(rb,0,mt)-mt', [dim_z,tkh,mt,rb])

    def create_upper_carcass(self,name):
        self.create_cabinet(name)

        self.add_properties_common()
        
        dim_x = self.var_input('Dim X', 'dim_x')
        dim_y = self.var_input('Dim Y', 'dim_y')
        dim_z = self.var_input('Dim Z', 'dim_z')
        mt = self.var_prop('Material Thickness', 'mt')

        # Left side (no notch for upper)
        left_side = CabinetPart()
        left_side.create('Left Side')
        left_side.obj.parent = self.obj
        left_side.obj.rotation_euler.y = math.radians(-90)
        left_side.driver_input("Length", 'dim_z', [dim_z])
        left_side.driver_input("Width", 'dim_y', [dim_y])
        left_side.driver_input("Thickness", 'mt', [mt])
        left_side.set_input("Mirror Y", True)
        left_side.set_input("Mirror Z", True)

        # Right side
        right_side = CabinetPart()
        right_side.create('Right Side')
        right_side.obj.parent = self.obj
        right_side.driver_location('x', 'dim_x', [dim_x])
        right_side.obj.rotation_euler.y = math.radians(-90)
        right_side.driver_input("Length", 'dim_z', [dim_z])
        right_side.driver_input("Width", 'dim_y', [dim_y])
        right_side.driver_input("Thickness", 'mt', [mt])
        right_side.set_input("Mirror Y", True)
        right_side.set_input("Mirror Z", False)

        # Bottom
        bottom = CabinetPart()
        bottom.create('Bottom')
        bottom.obj.parent = self.obj
        bottom.driver_location('x', 'mt', [mt])
        bottom.driver_input("Length", 'dim_x-(mt*2)', [dim_x, mt])
        bottom.driver_input("Width", 'dim_y', [dim_y])
        bottom.driver_input("Thickness", 'mt', [mt])
        bottom.set_input("Mirror Y", True)
        bottom.set_input("Mirror Z", False)

        # Back
        back = CabinetPart()
        back.create('Back')
        back.obj.parent = self.obj
        back.obj.rotation_euler.x = math.radians(90)
        back.obj.rotation_euler.y = math.radians(-90)
        back.driver_location('x', 'mt', [mt])
        back.driver_location('z', 'mt', [mt])
        back.driver_input("Length", 'dim_z-(mt*2)', [dim_z, mt])
        back.driver_input("Width", 'dim_x-(mt*2)', [dim_x, mt])
        back.driver_input("Thickness", 'mt', [mt])
        back.set_input("Mirror Y", True)

        # Top
        top = CabinetPart()
        top.create('Top')
        top.obj.parent = self.obj
        top.driver_location('x', 'mt', [mt])
        top.driver_location('z', 'dim_z', [dim_z])
        top.driver_input("Length", 'dim_x-(mt*2)', [dim_x, mt])
        top.driver_input("Width", 'dim_y', [dim_y])
        top.driver_input("Thickness", 'mt', [mt])
        top.set_input("Mirror Y", True)
        top.set_input("Mirror Z", True)

        # Opening
        opening = CabinetBay()
        opening.create("Bay")
        opening.obj.parent = self.obj
        opening.driver_location('x', 'mt', [mt])
        opening.driver_location('y', '-dim_y', [dim_y])
        opening.driver_location('z', 'mt', [mt])
        opening.driver_input("Dim X", 'dim_x-(mt*2)', [dim_x, mt])
        opening.driver_input("Dim Y", 'dim_y-mt', [dim_y, mt])
        opening.driver_input("Dim Z", 'dim_z-(mt*2)', [dim_z, mt])

# =============================================================================
# CABINET TYPES
# =============================================================================

class BaseCabinet(Cabinet):
    """Standard base cabinet with toe kick. Sits on floor."""
    
    def __init__(self):
        super().__init__()
        props = bpy.context.scene.hb_frameless
        self.width = props.default_cabinet_width
        self.height = props.base_cabinet_height
        self.depth = props.base_cabinet_depth
    
    def create(self, name="Base Cabinet"):
        self.create_base_carcass(name)
        self.obj['CABINET_TYPE'] = 'BASE'
        
        # Add exterior based on base_exterior property
        props = bpy.context.scene.hb_frameless
        self.add_exterior()
    
    def add_exterior(self):
        """Add doors/drawers based on exterior type."""
        if self.default_exterior == 'Doors':
            self.add_doors()
        elif self.default_exterior == 'Door Drawer':
            self.add_drawer_door()
        elif self.default_exterior == '2 Drawers':
            self.add_drawer_stack(2)
        elif self.default_exterior == '3 Drawers':
            self.add_drawer_stack(3)
        elif self.default_exterior == '4 Drawers':
            self.add_drawer_stack(4)
        # 'Open' = no exterior
    
    def add_doors(self):
        """Add door fronts to the cabinet bay."""
        doors = Doors()
        doors.door_pull_location = "Base"
        self.add_cage_to_bay(doors)
    
    def add_drawer_door(self):
        """Add a drawer on top and doors below."""
        props = bpy.context.scene.hb_frameless

        drawer = Drawer()
        drawer.half_overlay_bottom = True
        door = Doors()
        door.half_overlay_top = True

        door_drawer = SplitterVertical()
        door_drawer.splitter_qty = 1
        door_drawer.opening_sizes = [props.top_drawer_front_height,0]
        door_drawer.opening_inserts = [drawer,door]
        self.add_cage_to_bay(door_drawer)
    
    def add_drawer_stack(self, count):
        """Add a stack of drawers."""
        #TODO: Implement DrawerStack Class to handle equal drawer heights
        # SplitterVertical keeps opening height equal but does not account 
        # for drawer front overlay
        props = bpy.context.scene.hb_frameless
        equal_drawer_stack_heights = props.equal_drawer_stack_heights
        if equal_drawer_stack_heights:
            top_drawer_height = 0 # 0 means equal height
        else:
            top_drawer_height = props.top_drawer_front_height

        door_drawer = SplitterVertical()
        door_drawer.splitter_qty = count - 1
        for i in range(count):
            drawer = Drawer()
            if i == 0:
                drawer.half_overlay_bottom = True
                door_drawer.opening_sizes.append(top_drawer_height)
            elif i == count - 1:
                drawer.half_overlay_top = True
                door_drawer.opening_sizes.append(0)
            else:
                drawer.half_overlay_top = True
                drawer.half_overlay_bottom = True
                door_drawer.opening_sizes.append(0)
            door_drawer.opening_inserts.append(drawer)
        self.add_cage_to_bay(door_drawer)


class TallCabinet(Cabinet):
    """Tall cabinet (pantry, oven, utility). Has toe kick, full height."""
    
    is_stacked = False

    def __init__(self):
        super().__init__()
        props = bpy.context.scene.hb_frameless
        self.is_stacked = False
        self.width = props.default_cabinet_width
        self.height = props.tall_cabinet_height
        self.depth = props.tall_cabinet_depth
    
    def create(self, name="Tall Cabinet"):
        self.create_tall_carcass(name)
        self.obj['CABINET_TYPE'] = 'TALL'
        self.add_doors()
    
    def add_doors(self):
        """Add door fronts to the cabinet bay."""
        props = bpy.context.scene.hb_frameless

        if self.is_stacked:
            top_doors = Doors()
            top_doors.half_overlay_bottom = True
            top_doors.door_pull_location = "Upper"
            bottom_doors = Doors()
            bottom_doors.half_overlay_top = True
            bottom_doors.door_pull_location = "Tall"

            door_drawer = SplitterVertical()
            door_drawer.splitter_qty = 1
            door_drawer.opening_sizes = [0,props.tall_cabinet_split_height]
            door_drawer.opening_inserts = [top_doors,bottom_doors]
            self.add_cage_to_bay(door_drawer)
        else:
            doors = Doors()
            doors.door_pull_location = "Tall"
            self.add_cage_to_bay(doors)



class RefrigeratorCabinet(Cabinet):
    """Refrigerator cabinet - tall cabinet with bottom removed and split opening.
    Bottom section is empty for the refrigerator, top section has doors for storage.
    """

    def __init__(self):
        super().__init__()
        props = bpy.context.scene.hb_frameless
        self.width = props.refrigerator_cabinet_width
        self.height = props.tall_cabinet_height
        self.depth = props.tall_cabinet_depth
    
    def create(self, name="Refrigerator Cabinet"):
        self.create_tall_carcass(name)
        self.obj['CABINET_TYPE'] = 'TALL'
        self.obj['IS_REFRIGERATOR_CABINET'] = True
        
        # Remove the bottom panel for the refrigerator
        self.set_property('Remove Bottom', True)
        self.set_property('Toe Kick Height', 0)
        
        self.add_openings()
    
    def add_openings(self):
        """Add split openings - empty bottom for fridge, doors on top."""
        props = bpy.context.scene.hb_frameless
        
        # Top section gets doors
        top_doors = Doors()
        top_doors.half_overlay_bottom = True
        top_doors.door_pull_location = "Upper"
        
        # Bottom section is empty (None = no insert, just an opening)
        # The refrigerator appliance can be placed here separately
        
        # Create vertical splitter with 2 openings
        # opening_sizes: [top_height, bottom_height]
        # Using 0 for top means it takes remaining space after bottom is set
        door_drawer = SplitterVertical()
        door_drawer.splitter_qty = 1
        door_drawer.opening_sizes = [0, props.refrigerator_height]  # Top flexible, bottom = fridge height
        door_drawer.opening_inserts = [top_doors, None]  # Doors on top, empty on bottom
        self.add_cage_to_bay(door_drawer)


class UpperCabinet(Cabinet):
    """Wall-mounted upper cabinet. No toe kick."""
    
    is_stacked = False

    def __init__(self):
        super().__init__()
        props = bpy.context.scene.hb_frameless
        self.is_stacked = False
        self.width = props.default_cabinet_width
        self.height = props.upper_cabinet_height
        self.depth = props.upper_cabinet_depth
    
    def create(self, name="Upper Cabinet"):
        self.create_upper_carcass(name)
        self.obj['CABINET_TYPE'] = 'UPPER'
        self.obj.display_type = 'WIRE'
        self.add_doors()
    
    def add_doors(self):
        """Add door fronts to the cabinet bay."""
        props = bpy.context.scene.hb_frameless

        if self.is_stacked:
            top_doors = Doors()
            top_doors.half_overlay_bottom = True
            top_doors.door_pull_location = "Upper"
            bottom_doors = Doors()
            bottom_doors.half_overlay_top = True
            bottom_doors.door_pull_location = "Upper"

            door_drawer = SplitterVertical()
            door_drawer.splitter_qty = 1
            door_drawer.opening_sizes = [props.upper_top_stacked_cabinet_height,0]
            door_drawer.opening_inserts = [top_doors,bottom_doors]
            self.add_cage_to_bay(door_drawer)
        else:
            doors = Doors()
            doors.door_pull_location = "Upper"
            self.add_cage_to_bay(doors)


class CabinetBay(GeoNodeCage):

    def create(self,name):
        super().create(name)
        self.obj['IS_FRAMELESS_BAY_CAGE'] = True
        self.obj['MENU_ID'] = 'HOME_BUILDER_MT_bay_commands'
        self.obj.display_type = 'WIRE'


class SplitterVertical(GeoNodeCage):

    splitter_qty = 1
    opening_sizes = []
    opening_inserts = []

    def __init__(self, obj=None):
        super().__init__(obj)
        self.splitter_qty = 1 # Default Splitter Quantity. Opening Qty = Splitter Qty + 1
        self.opening_sizes = [] # Default Opening Sizes top to bottom 0 is equal
        self.opening_inserts = [] # Default Opening Inserts top to bottom

    def add_insert_into_opening(self,opening,insert):
        dim_x = opening.var_input('Dim X', 'dim_x')
        dim_y = opening.var_input('Dim Y', 'dim_y')
        dim_z = opening.var_input('Dim Z', 'dim_z')

        insert.obj.parent = opening.obj
        insert.driver_input("Dim X", 'dim_x', [dim_x])
        insert.driver_input("Dim Y", 'dim_y', [dim_y])
        insert.driver_input("Dim Z", 'dim_z', [dim_z])
        
    def create(self):
        super().create('Splitter Vertical')
        props = bpy.context.scene.hb_frameless

        self.obj['IS_FRAMELESS_SPLITTER_VERTICAL_CAGE'] = True
        self.obj.display_type = 'WIRE'

        self.add_property('Shelf Quantity', 'QUANTITY', 1)
        self.add_property('Material Thickness', 'DISTANCE', props.default_carcass_part_thickness)

        # Add calculator for opening heights
        empty_obj = self.add_empty("Calc Object")
        empty_obj.empty_display_size = .001
        opening_calculator = self.obj.home_builder.add_calculator("Opening Calculator",empty_obj)
        for i in range(1,self.splitter_qty+2):
            opening_calculator.add_calculator_prompt('Opening ' + str(i) + ' Height')

        dim_x = self.var_input('Dim X', 'dim_x')
        dim_y = self.var_input('Dim Y', 'dim_y')
        dim_z = self.var_input('Dim Z', 'dim_z')
        mt = self.var_prop('Material Thickness', 'mt')

        # Total distance is height minus material thickness for all splitters
        opening_calculator.set_total_distance('dim_z-mt*' + str(self.splitter_qty),[dim_z,mt])
        
        previous_splitter = None

        # Add Shelf Splitters Adding from Top to Bottom
        for i in range(1,self.splitter_qty+2):
            opening_prompt = opening_calculator.get_calculator_prompt('Opening ' + str(i) + ' Height')
            oh = opening_prompt.get_var('Opening Calculator','oh')

            # Add Shelf
            if i < self.splitter_qty+1:
                shelf = CabinetPart()
                shelf.create('Vertical Splitter ' + str(i))
                shelf.obj.parent = self.obj      
                if previous_splitter:
                    loc_z = previous_splitter.var_location('loc_z','z')
                    shelf.driver_location('z', 'loc_z-oh-mt',[loc_z,oh,mt])
                else:
                    shelf.driver_location('z', 'dim_z-oh-mt',[dim_z,oh,mt])   
                shelf.driver_input("Length", 'dim_x', [dim_x])
                shelf.driver_input("Width", 'dim_y', [dim_y])
                shelf.driver_input("Thickness", 'mt', [mt])

            previous_splitter = shelf

            loc_z = previous_splitter.var_location('loc_z','z')

            # Add Opening
            opening = CabinetOpening()
            opening.create('Opening ' + str(i))
            opening.obj.parent = self.obj
            if i < self.splitter_qty+1:
                opening.driver_location('z', 'loc_z+mt',[loc_z,mt])
            else:
                opening.obj.location.z = 0
            
            opening.driver_input("Dim X", 'dim_x', [dim_x])
            opening.driver_input("Dim Y", 'dim_y', [dim_y])
            opening.driver_input("Dim Z", 'oh', [oh])

            # Add Insert into Opening
            if len(self.opening_inserts) > i - 1:
                insert = self.opening_inserts[i-1]
                if insert:
                    insert.create()
                    self.add_insert_into_opening(opening,insert)
                    
                    # Set FORCE_HALF_OVERLAY flags for split openings
                    # Top opening (i=1) needs half overlay on bottom where it meets splitter
                    # Bottom opening (i=splitter_qty+1) needs half overlay on top
                    # Middle openings need both
                    if i > 1:  # Not the top opening - force half overlay on top
                        insert.obj['FORCE_HALF_OVERLAY_TOP'] = True
                    if i <= self.splitter_qty:  # Not the bottom opening - force half overlay on bottom
                        insert.obj['FORCE_HALF_OVERLAY_BOTTOM'] = True

        # Set Opening Sizes
        for i in range(1,self.splitter_qty+2):
            if self.opening_sizes[i-1] != 0:
                oh = opening_calculator.get_calculator_prompt('Opening ' + str(i) + ' Height')
                oh.equal = False
                oh.distance_value = self.opening_sizes[i-1]

        opening_calculator.calculate() 




class SplitterHorizontal(GeoNodeCage):

    splitter_qty = 1
    opening_sizes = []
    opening_inserts = []

    def __init__(self, obj=None):
        super().__init__(obj)
        self.splitter_qty = 1 # Default Splitter Quantity. Opening Qty = Splitter Qty + 1
        self.opening_sizes = [] # Default Opening Sizes left to right 0 is equal
        self.opening_inserts = [] # Default Opening Inserts left to right

    def add_insert_into_opening(self,opening,insert):
        dim_x = opening.var_input('Dim X', 'dim_x')
        dim_y = opening.var_input('Dim Y', 'dim_y')
        dim_z = opening.var_input('Dim Z', 'dim_z')

        insert.obj.parent = opening.obj
        insert.driver_input("Dim X", 'dim_x', [dim_x])
        insert.driver_input("Dim Y", 'dim_y', [dim_y])
        insert.driver_input("Dim Z", 'dim_z', [dim_z])
        
    def create(self):
        super().create('Splitter Horizontal')
        props = bpy.context.scene.hb_frameless

        self.obj['IS_FRAMELESS_SPLITTER_HORIZONTAL_CAGE'] = True
        self.obj.display_type = 'WIRE'

        self.add_property('Divider Quantity', 'QUANTITY', 1)
        self.add_property('Material Thickness', 'DISTANCE', props.default_carcass_part_thickness)

        # Add calculator for opening widths
        empty_obj = self.add_empty("Calc Object")
        empty_obj.empty_display_size = .001
        opening_calculator = self.obj.home_builder.add_calculator("Opening Calculator",empty_obj)
        for i in range(1,self.splitter_qty+2):
            opening_calculator.add_calculator_prompt('Opening ' + str(i) + ' Width')

        dim_x = self.var_input('Dim X', 'dim_x')
        dim_y = self.var_input('Dim Y', 'dim_y')
        dim_z = self.var_input('Dim Z', 'dim_z')
        mt = self.var_prop('Material Thickness', 'mt')

        # Total distance is width minus material thickness for all splitters
        opening_calculator.set_total_distance('dim_x-mt*' + str(self.splitter_qty),[dim_x,mt])
        
        previous_splitter = None

        # Add Openings and Dividers from Left to Right
        for i in range(1,self.splitter_qty+2):
            opening_prompt = opening_calculator.get_calculator_prompt('Opening ' + str(i) + ' Width')
            ow = opening_prompt.get_var('Opening Calculator','ow')

            # Add Opening FIRST (before divider, so it references the correct previous_splitter)
            opening = CabinetOpening()
            opening.create('Opening ' + str(i))
            opening.obj.parent = self.obj
            if i == 1:
                opening.obj.location.x = 0
            else:
                loc_x = previous_splitter.var_location('loc_x','x')
                opening.driver_location('x', 'loc_x+mt',[loc_x,mt])
            
            opening.driver_input("Dim X", 'ow', [ow])
            opening.driver_input("Dim Y", 'dim_y', [dim_y])
            opening.driver_input("Dim Z", 'dim_z', [dim_z])

            # Add Insert into Opening
            if len(self.opening_inserts) > i - 1:
                insert = self.opening_inserts[i-1]
                if insert:
                    insert.create()
                    self.add_insert_into_opening(opening,insert)
                    
                    # Set FORCE_HALF_OVERLAY flags for split openings
                    # Left opening (i=1) needs half overlay on right where it meets divider
                    # Right opening (i=splitter_qty+1) needs half overlay on left
                    # Middle openings need both
                    if i > 1:  # Not the left opening - force half overlay on left
                        insert.obj['FORCE_HALF_OVERLAY_LEFT'] = True
                    if i <= self.splitter_qty:  # Not the right opening - force half overlay on right
                        insert.obj['FORCE_HALF_OVERLAY_RIGHT'] = True

            # Add Divider AFTER the opening (to its right)
            if i < self.splitter_qty+1:
                divider = CabinetPart()
                divider.create('Horizontal Splitter ' + str(i))
                divider.obj.parent = self.obj
                divider.obj.rotation_euler.y = math.radians(-90)
                if previous_splitter:
                    loc_x = previous_splitter.var_location('loc_x','x')
                    divider.driver_location('x', 'loc_x+ow+mt',[loc_x,ow,mt])
                else:
                    divider.driver_location('x', 'ow',[ow])
                divider.driver_input("Length", 'dim_z', [dim_z])
                divider.driver_input("Width", 'dim_y', [dim_y])
                divider.driver_input("Thickness", 'mt', [mt])
                divider.set_input("Mirror Z",True)

                previous_splitter = divider

        # Set Opening Sizes
        for i in range(1,self.splitter_qty+2):
            if len(self.opening_sizes) > i - 1 and self.opening_sizes[i-1] != 0:
                ow = opening_calculator.get_calculator_prompt('Opening ' + str(i) + ' Width')
                ow.equal = False
                ow.distance_value = self.opening_sizes[i-1]

        opening_calculator.calculate() 


class CabinetOpening(GeoNodeCage):

    half_overlay_top = False
    half_overlay_bottom = False
    half_overlay_left = False
    half_overlay_right = False

    def create(self,name):
        super().create(name)
        self.obj['IS_FRAMELESS_OPENING_CAGE'] = True
        self.obj['MENU_ID'] = 'HOME_BUILDER_MT_opening_commands'
        self.obj.display_type = 'WIRE'

    def add_properties_front_overlays(self):
        self.add_property("Inset Front",'CHECKBOX',False)
        self.add_property("Door to Cabinet Gap",'DISTANCE',inch(.125))    
        self.add_property("Half Overlay Top",'CHECKBOX',self.half_overlay_top)
        self.add_property("Half Overlay Bottom",'CHECKBOX',self.half_overlay_bottom)
        self.add_property("Half Overlay Left",'CHECKBOX',self.half_overlay_left)
        self.add_property("Half Overlay Right",'CHECKBOX',self.half_overlay_right)
        self.add_property("Inset Reveal",'DISTANCE',inch(.125))
        self.add_property("Top Reveal",'DISTANCE',inch(.0625))
        self.add_property("Bottom Reveal",'DISTANCE',inch(0))
        self.add_property("Left Reveal",'DISTANCE',inch(.0625))
        self.add_property("Right Reveal",'DISTANCE',inch(.0625))
        self.add_property("Vertical Gap",'DISTANCE',inch(.125))
        self.add_property("Horizontal Gap",'DISTANCE',inch(.125))

    def add_properties_opening_thickness(self):
        self.add_property("Left Thickness",'DISTANCE',inch(.75))
        self.add_property("Right Thickness",'DISTANCE',inch(.75))
        self.add_property("Top Thickness",'DISTANCE',inch(.75))
        self.add_property("Bottom Thickness",'DISTANCE',inch(.75))

    def add_properties_front_overlay_calculations(self):
        hot = self.var_prop('Half Overlay Top', 'hot')
        hob = self.var_prop('Half Overlay Bottom', 'hob')
        hol = self.var_prop('Half Overlay Left', 'hol')
        hor = self.var_prop('Half Overlay Right', 'hor')
        lt = self.var_prop('Left Thickness', 'lt')
        rt = self.var_prop('Right Thickness', 'rt')
        tt = self.var_prop('Top Thickness', 'tt')
        bt = self.var_prop('Bottom Thickness', 'bt')
        vg = self.var_prop('Vertical Gap', 'vg')
        lr = self.var_prop('Left Reveal', 'lr')
        rr = self.var_prop('Right Reveal', 'rr')
        tr = self.var_prop('Top Reveal', 'tr')
        br = self.var_prop('Bottom Reveal', 'br')
        inset = self.var_prop('Inset Front', 'inset')
        ir = self.var_prop('Inset Reveal', 'ir')

        # Overlay Prompts Stored in Separate Empty Object to Avoid Circular Dependency Graph Issues
        self.overlay_prompts = self.add_empty('Overlay Prompt Obj')
        self.overlay_prompts.home_builder.add_property("Overlay Top",'DISTANCE',0.0)
        self.overlay_prompts.home_builder.add_property("Overlay Bottom",'DISTANCE',0.0)
        self.overlay_prompts.home_builder.add_property("Overlay Left",'DISTANCE',0.0)
        self.overlay_prompts.home_builder.add_property("Overlay Right",'DISTANCE',0.0)

        # Inset: negative overlay (door smaller than opening by inset reveal)
        # Half Overlay: (thickness - gap) / 2
        # Full Overlay: thickness - reveal
        self.overlay_prompts.home_builder.driver_prop("Overlay Top", "IF(inset,-ir,IF(hot,(tt-vg)/2,tt-tr))", [inset,ir,hot,tt,vg,tr])
        self.overlay_prompts.home_builder.driver_prop("Overlay Bottom", "IF(inset,-ir,IF(hob,(bt-vg)/2,bt-br))", [inset,ir,hob,bt,vg,br])
        self.overlay_prompts.home_builder.driver_prop("Overlay Left", "IF(inset,-ir,IF(hol,(lt-vg)/2,lt-lr))", [inset,ir,hol,lt,vg,lr])
        self.overlay_prompts.home_builder.driver_prop("Overlay Right", "IF(inset,-ir,IF(hor,(rt-vg)/2,rt-rr))", [inset,ir,hor,rt,vg,rr])

        return self.overlay_prompts


class CabinetInterior(GeoNodeCage):

    def create(self,name):
        super().create(name)
        self.obj['IS_FRAMELESS_INTERIOR_CAGE'] = True
        self.obj['MENU_ID'] = 'HOME_BUILDER_MT_interior_commands'
        self.obj.display_type = 'WIRE'


class CabinetShelves(CabinetInterior):

    def create(self,name):
        super().create(name)
        props = bpy.context.scene.hb_frameless

        self.add_property('Shelf Quantity', 'QUANTITY', 1)
        self.add_property('Material Thickness', 'DISTANCE', props.default_carcass_part_thickness)
        self.add_property('Shelf Clip Gap', 'DISTANCE', inch(.125))
        self.add_property('Shelf Setback', 'DISTANCE', inch(.25))

        dim_x = self.var_input('Dim X', 'dim_x')
        dim_y = self.var_input('Dim Y', 'dim_y')
        dim_z = self.var_input('Dim Z', 'dim_z')

        mt = self.var_prop('Material Thickness', 'mt')
        setback = self.var_prop('Shelf Setback', 'setback')
        clip_gap = self.var_prop('Shelf Clip Gap', 'clip_gap')
        qty = self.var_prop('Shelf Quantity', 'qty')

        shelves = CabinetPart()
        shelves.create('Shelf')
        shelves.obj['IS_FRAMELESS_INTERIOR_PART'] = True
        shelves.obj['MENU_ID'] = 'HOME_BUILDER_MT_interior_part_commands'
        # Interior parts get interior material on both sides
        shelves.obj['Finish Top'] = False
        shelves.obj['Finish Bottom'] = False
        shelves.obj.parent = self.obj
        array_mod = shelves.obj.modifiers.new('Qty','ARRAY')
        array_mod.count = 1   
        array_mod.use_relative_offset = False
        array_mod.use_constant_offset = True
        array_mod.constant_offset_displace = (0,0,0)        
        shelves.driver_location('x', 'clip_gap',[clip_gap])
        shelves.driver_location('y', 'setback',[setback])
        shelves.driver_location('z', '(dim_z-(mt*qty))/(qty+1)',[dim_z,mt,qty])
        shelves.driver_input("Length", 'dim_x-clip_gap*2', [dim_x,clip_gap])
        shelves.driver_input("Width", 'dim_y-setback', [dim_y,setback])
        shelves.driver_input("Thickness", 'mt', [mt])
        shelves.obj.home_builder.add_driver('modifiers["' + array_mod.name + '"].count',-1,'qty',[qty])
        shelves.obj.home_builder.add_driver('modifiers["' + array_mod.name + '"].constant_offset_displace',2,
                                     '((dim_z-(mt*qty))/(qty+1))+mt',
                                     [dim_z,mt,qty])        


class Doors(CabinetOpening):

    door_pull_location = "Base"

    def create(self):
        super().create("Doors")

        self.add_property('Front Thickness', 'DISTANCE', inch(.75))
        self.add_property('Vertical Gap', 'DISTANCE', inch(.125))
        self.add_property("Door Swing",'COMBOBOX',2,combobox_items=["Left","Right","Double"])
        self.add_properties_opening_thickness()
        self.add_properties_front_overlays()
        overlay_prompts = self.add_properties_front_overlay_calculations()

        to = overlay_prompts.home_builder.var_prop('Overlay Top', 'to')
        bo = overlay_prompts.home_builder.var_prop('Overlay Bottom', 'bo')
        lo = overlay_prompts.home_builder.var_prop('Overlay Left', 'lo')
        ro = overlay_prompts.home_builder.var_prop('Overlay Right', 'ro')

        dim_x = self.var_input('Dim X', 'dim_x')
        dim_y = self.var_input('Dim Y', 'dim_y')
        dim_z = self.var_input('Dim Z', 'dim_z')
        ft = self.var_prop('Front Thickness', 'ft')
        vg = self.var_prop('Vertical Gap', 'vg')
        ds = self.var_prop('Door Swing', 'ds')
        door_to_cab_gap = self.var_prop('Door to Cabinet Gap', 'door_to_cab_gap')

        inset = self.var_prop('Inset Front', 'inset')

        left_door = CabinetDoor()
        left_door.door_pull_location = self.door_pull_location
        left_door.create('Left Door')
        left_door.obj.parent = self.obj
        left_door.obj.rotation_euler.x = math.radians(90)
        left_door.obj.rotation_euler.y = math.radians(-90)
        left_door.driver_location('x', '-lo',[lo])
        # Inset: door sits inside opening (Y=0), Overlay: door projects forward
        left_door.driver_location('y', 'IF(inset,ft,-door_to_cab_gap)',[inset,ft,door_to_cab_gap])
        left_door.driver_location('z', '-bo',[bo])
        left_door.driver_input("Length", 'dim_z+to+bo', [dim_z,to,bo])
        left_door.driver_input("Width", 'IF(ds==2,(dim_x+lo+ro-vg)/2,dim_x+lo+ro)', [dim_x,lo,ro,vg,ds])
        left_door.driver_input("Thickness", 'ft', [ft])   
        left_door.driver_hide('IF(ds==1,True,False)',[ds])
        left_door.set_input("Mirror Y", True)  

        right_door = CabinetDoor()
        right_door.door_pull_location = self.door_pull_location
        right_door.create('Right Door')
        right_door.obj.parent = self.obj
        right_door.obj.rotation_euler.x = math.radians(90)
        right_door.obj.rotation_euler.y = math.radians(-90)
        right_door.driver_location('x', 'dim_x+ro',[dim_x,ro])
        # Inset: door sits inside opening (Y=0), Overlay: door projects forward
        right_door.driver_location('y', 'IF(inset,ft,-door_to_cab_gap)',[inset,ft,door_to_cab_gap])
        right_door.driver_location('z', '-bo',[bo])
        right_door.driver_input("Length", 'dim_z+to+bo', [dim_z,to,bo])
        right_door.driver_input("Width", 'IF(ds==2,(dim_x+lo+ro-vg)/2,dim_x+lo+ro)', [dim_x,lo,ro,vg,ds])
        right_door.driver_input("Thickness", 'ft', [ft]) 
        right_door.driver_hide('IF(ds==0,True,False)',[ds])  
        right_door.set_input("Mirror Y", False) 

        self.add_interior(CabinetShelves())

    def add_interior(self,interior):
        x = self.var_input('Dim X', 'x')
        y = self.var_input('Dim Y', 'y')
        z = self.var_input('Dim Z', 'z')
        inset = self.var_prop('Inset Front', 'inset')
        ft = self.var_prop('Front Thickness', 'ft')

        interior.create('Interior')
        interior.obj.parent = self.obj
        interior.driver_location('y', 'IF(inset,ft,0)',[inset,ft])
        interior.driver_input('Dim X','x',[x])
        interior.driver_input('Dim Y','y-IF(inset,ft,0)',[y,inset,ft])
        interior.driver_input('Dim Z','z',[z])         


class FlipUpDoor(CabinetOpening):
    """A flip-up door hinges at the top and swings upward.
    Commonly used on upper cabinets for easy access.
    Pull is rotated 90 degrees and centered on the door.
    """

    def create(self):
        super().create("Flip Up Door")

        self.add_property('Front Thickness', 'DISTANCE', inch(.75))
        self.add_properties_opening_thickness()
        self.add_properties_front_overlays()
        overlay_prompts = self.add_properties_front_overlay_calculations()

        to = overlay_prompts.home_builder.var_prop('Overlay Top', 'to')
        bo = overlay_prompts.home_builder.var_prop('Overlay Bottom', 'bo')
        lo = overlay_prompts.home_builder.var_prop('Overlay Left', 'lo')
        ro = overlay_prompts.home_builder.var_prop('Overlay Right', 'ro')

        dim_x = self.var_input('Dim X', 'dim_x')
        dim_y = self.var_input('Dim Y', 'dim_y')
        dim_z = self.var_input('Dim Z', 'dim_z')
        ft = self.var_prop('Front Thickness', 'ft')
        door_to_cab_gap = self.var_prop('Door to Cabinet Gap', 'door_to_cab_gap')

        inset = self.var_prop('Inset Front', 'inset')

        # Single door covering entire opening with centered, rotated pull
        door = CabinetFlipUpDoor()
        door.create('Flip Up Door')
        door.obj.parent = self.obj
        door.obj.rotation_euler.x = math.radians(90)
        door.obj.rotation_euler.y = math.radians(-90)
        door.driver_location('x', '-lo', [lo])
        door.driver_location('y', 'IF(inset,ft,-door_to_cab_gap)', [inset, ft, door_to_cab_gap])
        door.driver_location('z', '-bo', [bo])
        door.driver_input("Length", 'dim_z+to+bo', [dim_z, to, bo])
        door.driver_input("Width", 'dim_x+lo+ro', [dim_x, lo, ro])
        door.driver_input("Thickness", 'ft', [ft])
        door.set_input("Mirror Y", True)

        self.add_interior(CabinetShelves())

    def add_interior(self, interior):
        x = self.var_input('Dim X', 'x')
        y = self.var_input('Dim Y', 'y')
        z = self.var_input('Dim Z', 'z')
        inset = self.var_prop('Inset Front', 'inset')
        ft = self.var_prop('Front Thickness', 'ft')

        interior.create('Interior')
        interior.obj.parent = self.obj
        interior.driver_location('y', 'IF(inset,ft,0)', [inset, ft])
        interior.driver_input('Dim X', 'x', [x])
        interior.driver_input('Dim Y', 'y-IF(inset,ft,0)', [y, inset, ft])
        interior.driver_input('Dim Z', 'z', [z])


class Drawer(CabinetOpening):

    def create(self):
        super().create("Drawers")

        self.add_property('Front Thickness', 'DISTANCE', inch(.75))
        self.add_properties_opening_thickness()
        self.add_properties_front_overlays()
        overlay_prompts = self.add_properties_front_overlay_calculations()

        to = overlay_prompts.home_builder.var_prop('Overlay Top', 'to')
        bo = overlay_prompts.home_builder.var_prop('Overlay Bottom', 'bo')
        lo = overlay_prompts.home_builder.var_prop('Overlay Left', 'lo')
        ro = overlay_prompts.home_builder.var_prop('Overlay Right', 'ro')

        dim_x = self.var_input('Dim X', 'dim_x')
        dim_y = self.var_input('Dim Y', 'dim_y')
        dim_z = self.var_input('Dim Z', 'dim_z')
        ft = self.var_prop('Front Thickness', 'ft')
        door_to_cab_gap = self.var_prop('Door to Cabinet Gap', 'door_to_cab_gap')

        inset = self.var_prop('Inset Front', 'inset')

        drawer_front = CabinetDrawerFront()
        drawer_front.create('Drawer Front')
        drawer_front.obj.parent = self.obj
        drawer_front.obj.rotation_euler.x = math.radians(90)
        drawer_front.obj.rotation_euler.y = math.radians(-90)
        drawer_front.driver_location('x', '-lo',[lo])
        # Inset: drawer front sits inside opening (Y=0), Overlay: projects forward
        drawer_front.driver_location('y', 'IF(inset,ft,-door_to_cab_gap)',[inset,ft,door_to_cab_gap])
        drawer_front.driver_location('z', '-bo',[bo])
        drawer_front.driver_input("Length", 'dim_z+to+bo', [dim_z,to,bo])
        drawer_front.driver_input("Width", 'dim_x+lo+ro', [dim_x,lo,ro])
        drawer_front.driver_input("Thickness", 'ft', [ft]) 
        drawer_front.driver_prop("Top Overlay", 'to', [to])
        drawer_front.driver_prop("Bottom Overlay", 'bo', [bo])
        drawer_front.driver_prop("Left Overlay", 'lo', [lo])
        drawer_front.driver_prop("Right Overlay", 'ro', [ro])
        drawer_front.set_input("Mirror Y", True)
        drawer_front.add_drawer_box()


class Pullout(CabinetOpening):
    """A pullout is similar to a drawer but with the pull at the top instead of centered.
    Default interior is a Drawer Box, but different accessories can be added.
    """

    def create(self):
        super().create("Pullout")

        self.add_property('Front Thickness', 'DISTANCE', inch(.75))
        self.add_properties_opening_thickness()
        self.add_properties_front_overlays()
        overlay_prompts = self.add_properties_front_overlay_calculations()

        to = overlay_prompts.home_builder.var_prop('Overlay Top', 'to')
        bo = overlay_prompts.home_builder.var_prop('Overlay Bottom', 'bo')
        lo = overlay_prompts.home_builder.var_prop('Overlay Left', 'lo')
        ro = overlay_prompts.home_builder.var_prop('Overlay Right', 'ro')

        dim_x = self.var_input('Dim X', 'dim_x')
        dim_y = self.var_input('Dim Y', 'dim_y')
        dim_z = self.var_input('Dim Z', 'dim_z')
        ft = self.var_prop('Front Thickness', 'ft')
        door_to_cab_gap = self.var_prop('Door to Cabinet Gap', 'door_to_cab_gap')

        inset = self.var_prop('Inset Front', 'inset')

        drawer_front = CabinetDrawerFront()
        drawer_front.create('Pullout Front')
        drawer_front.obj.parent = self.obj
        drawer_front.obj.rotation_euler.x = math.radians(90)
        drawer_front.obj.rotation_euler.y = math.radians(-90)
        drawer_front.driver_location('x', '-lo',[lo])
        # Inset: drawer front sits inside opening (Y=0), Overlay: projects forward
        drawer_front.driver_location('y', 'IF(inset,ft,-door_to_cab_gap)',[inset,ft,door_to_cab_gap])
        drawer_front.driver_location('z', '-bo',[bo])
        drawer_front.driver_input("Length", 'dim_z+to+bo', [dim_z,to,bo])
        drawer_front.driver_input("Width", 'dim_x+lo+ro', [dim_x,lo,ro])
        drawer_front.driver_input("Thickness", 'ft', [ft]) 
        drawer_front.driver_prop("Top Overlay", 'to', [to])
        drawer_front.driver_prop("Bottom Overlay", 'bo', [bo])
        drawer_front.driver_prop("Left Overlay", 'lo', [lo])
        drawer_front.driver_prop("Right Overlay", 'ro', [ro])
        drawer_front.set_input("Mirror Y", True)
        
        # Set Center Pull to False - pull will be at top
        drawer_front.set_property("Center Pull", False)
        
        drawer_front.add_drawer_box()


class FalseFront(CabinetOpening):
    """A false front is a decorative panel with no drawer box or handle.
    Used for sink cabinet fronts, filler panels, or decorative purposes.
    """

    def create(self):
        super().create("False Front")

        self.add_property('Front Thickness', 'DISTANCE', inch(.75))
        self.add_properties_opening_thickness()
        self.add_properties_front_overlays()
        overlay_prompts = self.add_properties_front_overlay_calculations()

        to = overlay_prompts.home_builder.var_prop('Overlay Top', 'to')
        bo = overlay_prompts.home_builder.var_prop('Overlay Bottom', 'bo')
        lo = overlay_prompts.home_builder.var_prop('Overlay Left', 'lo')
        ro = overlay_prompts.home_builder.var_prop('Overlay Right', 'ro')

        dim_x = self.var_input('Dim X', 'dim_x')
        dim_y = self.var_input('Dim Y', 'dim_y')
        dim_z = self.var_input('Dim Z', 'dim_z')
        ft = self.var_prop('Front Thickness', 'ft')
        door_to_cab_gap = self.var_prop('Door to Cabinet Gap', 'door_to_cab_gap')

        inset = self.var_prop('Inset Front', 'inset')

        drawer_front = CabinetDrawerFront()
        drawer_front.create('False Front')
        drawer_front.obj.parent = self.obj
        drawer_front.obj.rotation_euler.x = math.radians(90)
        drawer_front.obj.rotation_euler.y = math.radians(-90)
        drawer_front.driver_location('x', '-lo', [lo])
        drawer_front.driver_location('y', 'IF(inset,ft,-door_to_cab_gap)', [inset, ft, door_to_cab_gap])
        drawer_front.driver_location('z', '-bo', [bo])
        drawer_front.driver_input("Length", 'dim_z+to+bo', [dim_z, to, bo])
        drawer_front.driver_input("Width", 'dim_x+lo+ro', [dim_x, lo, ro])
        drawer_front.driver_input("Thickness", 'ft', [ft])
        drawer_front.driver_prop("Top Overlay", 'to', [to])
        drawer_front.driver_prop("Bottom Overlay", 'bo', [bo])
        drawer_front.driver_prop("Left Overlay", 'lo', [lo])
        drawer_front.driver_prop("Right Overlay", 'ro', [ro])
        drawer_front.set_input("Mirror Y", True)
        
        # Set False Front to True - no drawer box or handle
        drawer_front.set_property("False Front", True)
        # No drawer box added for false front


class Appliance(CabinetOpening):
    """An appliance opening displays centered text with the appliance name.
    Used for built-in appliances like ovens, microwaves, refrigerators, etc.
    """
    
    appliance_name = "Appliance"
    
    def create(self):
        from ...hb_details import GeoNodeText
        
        super().create("Appliance")
        
        # Store appliance name on the object
        self.obj['APPLIANCE_NAME'] = self.appliance_name
        
        dim_x = self.var_input('Dim X', 'dim_x')
        dim_y = self.var_input('Dim Y', 'dim_y')
        dim_z = self.var_input('Dim Z', 'dim_z')
        
        props = bpy.context.scene.home_builder
        
        appliance_text = GeoNodeText()
        appliance_text.create('Appliance Text', self.appliance_name, props.annotation_text_size)
        appliance_text.obj.parent = self.obj
        appliance_text.obj['IS_APPLIANCE_TEXT'] = True
        appliance_text.obj.rotation_euler.x = math.radians(90)
        appliance_text.driver_location("x", 'dim_x/2', [dim_x])
        appliance_text.driver_location("z", 'dim_z/2', [dim_z])
        appliance_text.set_alignment('CENTER', 'CENTER')


class OpenWithShelves(CabinetOpening):
    """An open opening with adjustable shelves.
    No door or drawer front, just exposed shelves.
    """
    
    def create(self):
        super().create("Open With Shelves")
        
        props = bpy.context.scene.hb_frameless
        
        self.add_property('Shelf Quantity', 'QUANTITY', 1)
        self.add_property('Shelf Setback', 'DISTANCE', inch(.25))
        self.add_property('Shelf Clip Gap', 'DISTANCE', inch(.125))
        
        dim_x = self.var_input('Dim X', 'dim_x')
        dim_y = self.var_input('Dim Y', 'dim_y')
        dim_z = self.var_input('Dim Z', 'dim_z')
        
        self.add_property('Material Thickness', 'DISTANCE', props.default_carcass_part_thickness)
        mt_var = self.var_prop('Material Thickness', 'mt')
        setback = self.var_prop('Shelf Setback', 'setback')
        clip_gap = self.var_prop('Shelf Clip Gap', 'clip_gap')
        qty = self.var_prop('Shelf Quantity', 'qty')
        mt = self.var_prop('Material Thickness', 'mt')
        
        # Create shelf part
        shelf = CabinetPart()
        shelf.create('Shelf')
        shelf.obj['IS_FRAMELESS_INTERIOR_PART'] = True
        shelf.obj['MENU_ID'] = 'HOME_BUILDER_MT_interior_part_commands'
        shelf.obj['Finish Top'] = False
        shelf.obj['Finish Bottom'] = False
        shelf.obj.parent = self.obj
        
        shelf.driver_location('x', 'clip_gap', [clip_gap])
        shelf.driver_location('y', 'setback', [setback])
        shelf.driver_location('z', '(dim_z-(mt*qty))/(qty+1)', [dim_z, mt_var, qty])
        shelf.driver_input("Length", 'dim_x-clip_gap*2', [dim_x, clip_gap])
        shelf.driver_input("Width", 'dim_y-setback', [dim_y, setback])
        shelf.driver_input("Thickness", 'mt', [mt_var])
        array_mod = shelf.obj.modifiers.new('Qty','ARRAY')
        array_mod.count = 1   
        array_mod.use_relative_offset = False
        array_mod.use_constant_offset = True
        array_mod.constant_offset_displace = (0,0,0)    
        shelf.obj.home_builder.add_driver('modifiers["' + array_mod.name + '"].count',-1,'qty',[qty])
        shelf.obj.home_builder.add_driver('modifiers["' + array_mod.name + '"].constant_offset_displace',2,
                                     '((dim_z-(mt*qty))/(qty+1))+mt',
                                     [dim_z,mt,qty])      


class CabinetPart(GeoNodeCutpart):

    def create(self,name):
        super().create(name)
        self.obj['CABINET_PART'] = True
        self.obj['Finish Top'] = False
        self.obj['Finish Bottom'] = True
        self.set_input('Length', inch(24))
        self.set_input('Width', inch(18))
        self.set_input('Thickness', inch(.75))  


class CabinetSideNotched(CabinetPart):

    def create(self,name,tkh,tks,mt):
        super().create(name)
        self.set_input('Length', inch(24))
        self.set_input('Width', inch(18))
        self.set_input('Thickness', inch(.75))

        notch = self.add_part_modifier('CPM_CORNERNOTCH','Notch')
        notch.driver_input('X','tkh',[tkh])
        notch.driver_input('Y','tks',[tks])
        notch.driver_input('Route Depth','mt',[mt])
        notch.set_input('Flip Y',True)


class CabinetFront(CabinetPart):

    def create(self,name):
        super().create(name)
        self.obj['IS_CABINET_FRONT'] = True
        self.obj['MENU_ID'] = 'HOME_BUILDER_MT_door_front_commands'
        # Fronts get finish material on both sides
        self.obj['Finish Top'] = True
        self.obj['Finish Bottom'] = True
        self.add_overlay_properties()

    def add_overlay_properties(self):
        self.add_property('Top Overlay', 'DISTANCE', 0.0)
        self.add_property('Bottom Overlay', 'DISTANCE', 0.0)
        self.add_property('Left Overlay', 'DISTANCE', 0.0)
        self.add_property('Right Overlay', 'DISTANCE', 0.0)

    def assign_door_style(self):
        """Assign the active door style to this front.
        
        If no door styles exist, creates a default Slab style first.
        Should be called after the front object is fully created and parented.
        """
        
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        
        # Ensure at least one door style exists
        if len(props.door_styles) == 0:
            # Create default Slab door style
            new_style = props.door_styles.add()
            new_style.name = "Slab"
            new_style.door_type = 'SLAB'
            props.active_door_style_index = 0
        
        # Get active door style and assign it
        style_index = props.active_door_style_index
        if style_index < len(props.door_styles):
            style = props.door_styles[style_index]
            self.obj['DOOR_STYLE_INDEX'] = style_index
            result = style.assign_style_to_front(self.obj)
            # If assignment failed (e.g., front too small), still store the index
            # so it can be updated later when the style changes
            if result != True:
                self.obj['DOOR_STYLE_NAME'] = style.name

    def get_pull_object(self, pull_type='door'):
        """Get the pull object for doors or drawers based on current selection.
        
        Returns None if pulls are disabled (NONE) or no valid object is found.
        For CUSTOM selection, returns the pointer property object.
        For bundled pulls, loads from .blend file and caches.
        """
        from . import props_hb_frameless
        from ... import hb_project
        
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        
        # Get the selected pull filename
        if pull_type == 'drawer':
            pull_filename = props.drawer_pull_selection
            cached = props.current_drawer_front_pull_object
        else:
            pull_filename = props.door_pull_selection
            cached = props.current_door_pull_object
        
        # No pulls selected
        if pull_filename == 'NONE':
            return None
        
        # Custom pull from scene - use the pointer property directly
        if pull_filename == 'CUSTOM':
            return cached  # Returns None if not assigned yet
        
        # Bundled pull - check if cached object matches current selection
        if cached:
            pull_name = os.path.splitext(pull_filename)[0] if pull_filename else ""
            if pull_name and pull_name in cached.name:
                return cached
        
        # Load the selected bundled pull
        pull_obj = props_hb_frameless.load_pull_object(pull_filename)
        
        if pull_obj:
            if pull_type == 'drawer':
                props.current_drawer_front_pull_object = pull_obj
            else:
                props.current_door_pull_object = pull_obj
            return pull_obj
        
        return None

class CabinetDoor(CabinetFront):

    door_pull_location = "Base"
    
    def create(self,name):
        super().create(name)
        self.obj['IS_DOOR_FRONT'] = True
        props = bpy.context.scene.hb_frameless

        pull_location_index = 0
        if self.door_pull_location == "Base":
            pull_location_index = 0
        elif self.door_pull_location == "Tall":
            pull_location_index = 1
        elif self.door_pull_location == "Upper":
            pull_location_index = 2

        self.add_property("Pull Location",'COMBOBOX',pull_location_index,combobox_items=["Base","Tall","Upper"])
        self.add_property('Handle Horizontal Location', 'DISTANCE', props.pull_dim_from_edge)
        self.add_property('Base Pull Vertical Location', 'DISTANCE', props.pull_vertical_location_base)
        self.add_property('Tall Pull Vertical Location', 'DISTANCE', props.pull_vertical_location_tall)
        self.add_property('Upper Pull Vertical Location', 'DISTANCE', props.pull_vertical_location_upper)
        
        # Get pull object and its length for positioning calculations
        pull_obj = self.get_pull_object()
        pull_length = pull_obj.dimensions.x if pull_obj else 0.1016  # Default to 4 inches
        self.add_property('Pull Length', 'DISTANCE', pull_length)

        length = self.var_input('Length', 'length')
        width = self.var_input('Width', 'width')
        thickness = self.var_input('Thickness', 'thickness')
        mirror_y = self.var_input('Mirror Y', 'mirror_y')
        hhl = self.var_prop('Handle Horizontal Location', 'hhl')
        pl = self.var_prop('Pull Location', 'pl')
        pvl_base = self.var_prop('Base Pull Vertical Location', 'pvl_base')
        pvl_tall = self.var_prop('Tall Pull Vertical Location', 'pvl_tall')
        pvl_upper = self.var_prop('Upper Pull Vertical Location', 'pvl_upper')
        pull_len = self.var_prop('Pull Length', 'pull_len')
        hide_door = self.var_hide('hide_door')

        pull = GeoNodeHardware()
        pull.create('Pull')
        pull.obj['IS_CABINET_PULL'] = True
        pull.obj.parent = self.obj
        pull.obj.rotation_euler.x = math.radians(-90)
        if pull_obj:
            pull.set_input("Object",pull_obj)
        # Base: measure from top of door to TOP of pull (subtract half pull length)
        # Tall/Upper: measure from bottom of door to BOTTOM of pull (add half pull length)
        pull.driver_location('x', 'IF(pl==0,length-pvl_base-pull_len/2,IF(pl==1,pvl_tall+pull_len/2,pvl_upper+pull_len/2))',[length,pl,pvl_base,pvl_tall,pvl_upper,pull_len])
        pull.driver_location('y', 'IF(mirror_y,-width+hhl,width-hhl)',[width,hhl,mirror_y])
        pull.driver_location('z', 'thickness',[thickness])
        pull.driver_hide('hide_door',[hide_door])


class CabinetFlipUpDoor(CabinetFront):
    """A flip-up door front with the pull rotated 90 degrees, centered horizontally, 
    and positioned at the bottom like an upper cabinet pull."""
    
    def create(self, name):
        super().create(name)
        self.obj['IS_DOOR_FRONT'] = True
        self.obj['IS_FLIP_UP_DOOR'] = True
        props = bpy.context.scene.hb_frameless
        
        # Get pull object and its length for positioning calculations
        pull_obj = self.get_pull_object()
        pull_length = pull_obj.dimensions.x if pull_obj else 0.1016  # Default to 4 inches
        self.add_property('Pull Length', 'DISTANCE', pull_length)
        self.add_property('Pull Vertical Location', 'DISTANCE', props.pull_vertical_location_upper)

        length = self.var_input('Length', 'length')
        width = self.var_input('Width', 'width')
        thickness = self.var_input('Thickness', 'thickness')
        pull_len = self.var_prop('Pull Length', 'pull_len')
        pvl = self.var_prop('Pull Vertical Location', 'pvl')
        hide_door = self.var_hide('hide_door')

        pull = GeoNodeHardware()
        pull.create('Pull')
        pull.obj['IS_CABINET_PULL'] = True
        pull.obj.parent = self.obj
        # Rotate pull 90 degrees for horizontal orientation
        pull.obj.rotation_euler.x = math.radians(-90)
        pull.obj.rotation_euler.z = math.radians(90)
        if pull_obj:
            pull.set_input("Object", pull_obj)
        # Position at bottom (like upper pull) but centered horizontally
        pull.driver_location('x', 'pvl', [pvl])
        pull.driver_location('y', '-width/2', [width])
        pull.driver_location('z', 'thickness', [thickness])
        pull.driver_hide('hide_door', [hide_door])


class CabinetDrawerFront(CabinetFront):

    door_pull_location = "Base"
    
    def create(self,name):
        super().create(name)
        self.obj['IS_DRAWER_FRONT'] = True
        props = bpy.context.scene.hb_frameless

        self.add_property("False Front",'CHECKBOX', False)
        self.add_property("Center Pull",'CHECKBOX',props.center_pulls_on_drawer_front)
        self.add_property('Handle Horizontal Location', 'DISTANCE', props.pull_vertical_location_drawers)
        
        # Get pull object and its length for positioning calculations
        pull_obj = self.get_pull_object(pull_type='drawer')
        pull_length = pull_obj.dimensions.x if pull_obj else 0.1016  # Default to 4 inches
        self.add_property('Pull Length', 'DISTANCE', pull_length)

        #Length is height of the drawer front
        length = self.var_input('Length', 'length')
        #Width is width of the drawer front
        width = self.var_input('Width', 'width')
        thickness = self.var_input('Thickness', 'thickness')
        false_front = self.var_prop('False Front', 'false_front')
        center_pull = self.var_prop('Center Pull', 'center_pull')
        hhl = self.var_prop('Handle Horizontal Location', 'hhl')
        pull_len = self.var_prop('Pull Length', 'pull_len')

        pull = GeoNodeHardware()
        pull.create('Pull')
        pull.obj['IS_CABINET_PULL'] = True
        pull.obj.parent = self.obj
        pull.obj.rotation_euler.x = math.radians(-90)
        pull.obj.rotation_euler.z = math.radians(90)
        if pull_obj:
            pull.set_input("Object",pull_obj)
        # When not centered: measure from top of drawer front to TOP of pull
        pull.driver_location('x', 'IF(center_pull,length/2,length-hhl-pull_len/2)',[center_pull,length,hhl,pull_len])
        pull.driver_location('y', '-width/2',[width])
        pull.driver_location('z', 'thickness',[thickness])
        # Hide pull when False Front is enabled
        pull.driver_hide('false_front', [false_front])

    def add_drawer_box(self):
        """Add a drawer box to this drawer front.
        Does not add drawer box if False Front is enabled.
        """
        props = bpy.context.scene.hb_frameless
        
        if not props.include_drawer_boxes:
            return
        
        # Don't add drawer box if False Front
        if self.obj.get('False Front', False):
            return

        # Check if drawer box already exists
        for child in self.obj.children:
            if child.get('IS_DRAWER_BOX'):
                return  # Already has a drawer box
        
        # Get drawer opening depth from parent
        drawer_opening = GeoNodeCage(self.obj.parent)
        opening_depth = drawer_opening.var_input('Dim Y', 'opening_depth')

        # Get drawer front variables
        df_height = self.var_input('Length', 'df_height')
        df_width = self.var_input('Width', 'df_width')
        lo = self.var_prop('Left Overlay', 'lo')
        ro = self.var_prop('Right Overlay', 'ro')
        to = self.var_prop('Top Overlay', 'to')
        bo = self.var_prop('Bottom Overlay', 'bo')
        
        # Add drawer box properties if not present
        if 'Drawer Box Side Clearance' not in self.obj:
            self.add_property('Drawer Box Side Clearance', 'DISTANCE', inch(0.5))
            self.add_property('Drawer Box Top Clearance', 'DISTANCE', inch(0.75))
            self.add_property('Drawer Box Rear Clearance', 'DISTANCE', inch(1.0))
            self.add_property('Drawer Box Bottom Clearance', 'DISTANCE', inch(.5))
        
        side_clr = self.var_prop('Drawer Box Side Clearance', 'side_clr')
        top_clr = self.var_prop('Drawer Box Top Clearance', 'top_clr')
        rear_clr = self.var_prop('Drawer Box Rear Clearance', 'rear_clr')
        bottom_clr = self.var_prop('Drawer Box Bottom Clearance', 'bottom_clr')
        
        drawer_box = GeoNodeDrawerBox()
        drawer_box.create('Drawer Box')
        drawer_box.obj['IS_FRAMELESS_INTERIOR_PART'] = True
        drawer_box.obj['MENU_ID'] = 'HOME_BUILDER_MT_interior_part_commands'
        drawer_box.obj.parent = self.obj
        drawer_box.obj.rotation_euler.x = math.radians(-90)
        drawer_box.obj.rotation_euler.z = math.radians(-90)
        # Drawer box dimensions with clearances
        drawer_box.driver_input('Dim X', 'df_width - lo - ro - (side_clr * 2)', [df_width,lo,ro,side_clr])
        drawer_box.driver_input('Dim Y', 'opening_depth - rear_clr', [opening_depth, rear_clr])
        drawer_box.driver_input('Dim Z', 'df_height - to - bo - top_clr - bottom_clr', [df_height,to,bo,top_clr,bottom_clr])
        # X is vertical location
        drawer_box.driver_location('x', 'bo + bottom_clr', [bo,bottom_clr])
        # Y is horizontal Location
        drawer_box.driver_location('y', '-lo - side_clr', [lo,side_clr])
        # Hide drawer box when False Front is enabled
        false_front = self.var_prop('False Front', 'false_front')
        drawer_box.driver_hide('false_front', [false_front])


# =============================================================================
# CORNER CABINETS
# =============================================================================



class InteriorSection(GeoNodeCage):
    """A section within an interior that can contain shelves, rollouts, etc."""

    def create(self, name):
        super().create(name)
        self.obj['IS_FRAMELESS_INTERIOR_SECTION'] = True
        self.obj['MENU_ID'] = 'HOME_BUILDER_MT_interior_commands'
        self.obj.display_type = 'WIRE'


class InteriorSplitterVertical(CabinetInterior):
    """Splits interior vertically into sections (top to bottom)."""

    splitter_qty = 1
    section_sizes = []
    section_types = []  # 'SHELVES', 'ROLLOUTS', 'TRAY_DIVIDERS', 'EMPTY'

    def __init__(self, obj=None):
        super().__init__(obj)
        self.splitter_qty = 1
        self.section_sizes = []
        self.section_types = []

    def create(self):
        super().create('Interior Splitter Vertical')
        props = bpy.context.scene.hb_frameless

        self.obj['IS_FRAMELESS_INTERIOR_SPLITTER_VERTICAL'] = True

        self.add_property('Divider Quantity', 'QUANTITY', self.splitter_qty)
        self.add_property('Material Thickness', 'DISTANCE', props.default_carcass_part_thickness)

        # Add calculator for section heights
        empty_obj = self.add_empty("Calc Object")
        empty_obj.empty_display_size = .001
        section_calculator = self.obj.home_builder.add_calculator("Section Calculator", empty_obj)
        for i in range(1, self.splitter_qty + 2):
            section_calculator.add_calculator_prompt('Section ' + str(i) + ' Height')

        dim_x = self.var_input('Dim X', 'dim_x')
        dim_y = self.var_input('Dim Y', 'dim_y')
        dim_z = self.var_input('Dim Z', 'dim_z')
        mt = self.var_prop('Material Thickness', 'mt')

        # Total distance is height minus material thickness for all dividers
        section_calculator.set_total_distance('dim_z-mt*' + str(self.splitter_qty), [dim_z, mt])

        previous_divider = None

        # Add horizontal dividers from top to bottom
        for i in range(1, self.splitter_qty + 2):
            section_prompt = section_calculator.get_calculator_prompt('Section ' + str(i) + ' Height')
            sh = section_prompt.get_var('Section Calculator', 'sh')

            # Add divider (horizontal shelf acting as divider)
            if i < self.splitter_qty + 1:
                divider = CabinetPart()
                divider.create('Interior Divider ' + str(i))
                divider.obj['IS_FRAMELESS_INTERIOR_PART'] = True
                divider.obj['MENU_ID'] = 'HOME_BUILDER_MT_interior_part_commands'
                divider.obj.parent = self.obj
                if previous_divider:
                    loc_z = previous_divider.var_location('loc_z', 'z')
                    divider.driver_location('z', 'loc_z-sh-mt', [loc_z, sh, mt])
                else:
                    divider.driver_location('z', 'dim_z-sh-mt', [dim_z, sh, mt])
                divider.driver_input("Length", 'dim_x', [dim_x])
                divider.driver_input("Width", 'dim_y', [dim_y])
                divider.driver_input("Thickness", 'mt', [mt])

                previous_divider = divider

            # Add interior section
            section = InteriorSection()
            section.create('Section ' + str(i))
            section.obj.parent = self.obj
            if i < self.splitter_qty + 1:
                loc_z = previous_divider.var_location('loc_z', 'z')
                section.driver_location('z', 'loc_z+mt', [loc_z, mt])
            else:
                section.obj.location.z = 0

            section.driver_input("Dim X", 'dim_x', [dim_x])
            section.driver_input("Dim Y", 'dim_y', [dim_y])
            section.driver_input("Dim Z", 'sh', [sh])

            # Add interior type to section based on section_types
            if len(self.section_types) > i - 1:
                section_type = self.section_types[i - 1]
                if section_type == 'SHELVES':
                    self._add_shelves_to_section(section)
                elif section_type == 'ROLLOUTS':
                    self._add_rollouts_to_section(section)
                # TRAY_DIVIDERS and EMPTY don't add anything for now

        # Set section sizes
        for i in range(1, self.splitter_qty + 2):
            if len(self.section_sizes) > i - 1 and self.section_sizes[i - 1] != 0:
                sh = section_calculator.get_calculator_prompt('Section ' + str(i) + ' Height')
                sh.equal = False
                sh.distance_value = self.section_sizes[i - 1]

        section_calculator.calculate()

    def _add_shelves_to_section(self, section):
        props = bpy.context.scene.hb_frameless
        dim_x = section.var_input('Dim X', 'dim_x')
        dim_y = section.var_input('Dim Y', 'dim_y')
        dim_z = section.var_input('Dim Z', 'dim_z')

        shelf = CabinetPart()
        shelf.create('Shelf')
        shelf.obj['IS_FRAMELESS_INTERIOR_PART'] = True
        shelf.obj['MENU_ID'] = 'HOME_BUILDER_MT_interior_part_commands'
        shelf.obj.parent = section.obj
        shelf.driver_location('z', 'dim_z/2', [dim_z])
        shelf.driver_input("Length", 'dim_x', [dim_x])
        shelf.driver_input("Width", 'dim_y-.025', [dim_y])  # Small setback
        shelf.set_input("Thickness", props.default_carcass_part_thickness)

    def _add_rollouts_to_section(self, section):
        # TODO: Implement rollout creation
        pass


class InteriorSplitterHorizontal(CabinetInterior):
    """Splits interior horizontally into sections (left to right)."""

    splitter_qty = 1
    section_sizes = []
    section_types = []

    def __init__(self, obj=None):
        super().__init__(obj)
        self.splitter_qty = 1
        self.section_sizes = []
        self.section_types = []

    def create(self):
        super().create('Interior Splitter Horizontal')
        props = bpy.context.scene.hb_frameless

        self.obj['IS_FRAMELESS_INTERIOR_SPLITTER_HORIZONTAL'] = True

        self.add_property('Divider Quantity', 'QUANTITY', self.splitter_qty)
        self.add_property('Material Thickness', 'DISTANCE', props.default_carcass_part_thickness)

        # Add calculator for section widths
        empty_obj = self.add_empty("Calc Object")
        empty_obj.empty_display_size = .001
        section_calculator = self.obj.home_builder.add_calculator("Section Calculator", empty_obj)
        for i in range(1, self.splitter_qty + 2):
            section_calculator.add_calculator_prompt('Section ' + str(i) + ' Width')

        dim_x = self.var_input('Dim X', 'dim_x')
        dim_y = self.var_input('Dim Y', 'dim_y')
        dim_z = self.var_input('Dim Z', 'dim_z')
        mt = self.var_prop('Material Thickness', 'mt')

        # Total distance is width minus material thickness for all dividers
        section_calculator.set_total_distance('dim_x-mt*' + str(self.splitter_qty), [dim_x, mt])

        previous_divider = None

        # Add vertical dividers from left to right
        for i in range(1, self.splitter_qty + 2):
            section_prompt = section_calculator.get_calculator_prompt('Section ' + str(i) + ' Width')
            sw = section_prompt.get_var('Section Calculator', 'sw')

            # Add divider (vertical panel)
            if i < self.splitter_qty + 1:
                divider = CabinetPart()
                divider.create('Interior Divider ' + str(i))
                divider.obj['IS_FRAMELESS_INTERIOR_PART'] = True
                divider.obj['MENU_ID'] = 'HOME_BUILDER_MT_interior_part_commands'
                divider.obj.parent = self.obj
                divider.obj.rotation_euler.y = math.radians(-90)
                if previous_divider:
                    loc_x = previous_divider.var_location('loc_x', 'x')
                    divider.driver_location('x', 'loc_x+sw+mt', [loc_x, sw, mt])
                else:
                    divider.driver_location('x', 'sw', [sw])
                divider.driver_input("Length", 'dim_z', [dim_z])
                divider.driver_input("Width", 'dim_y', [dim_y])
                divider.driver_input("Thickness", 'mt', [mt])

                previous_divider = divider

            # Add interior section
            section = InteriorSection()
            section.create('Section ' + str(i))
            section.obj.parent = self.obj
            if i == 1:
                section.obj.location.x = 0
            else:
                loc_x = previous_divider.var_location('loc_x', 'x')
                section.driver_location('x', 'loc_x+mt', [loc_x, mt])

            section.driver_input("Dim X", 'sw', [sw])
            section.driver_input("Dim Y", 'dim_y', [dim_y])
            section.driver_input("Dim Z", 'dim_z', [dim_z])

            # Add interior type to section
            if len(self.section_types) > i - 1:
                section_type = self.section_types[i - 1]
                if section_type == 'SHELVES':
                    self._add_shelves_to_section(section)
                elif section_type == 'ROLLOUTS':
                    self._add_rollouts_to_section(section)

        # Set section sizes
        for i in range(1, self.splitter_qty + 2):
            if len(self.section_sizes) > i - 1 and self.section_sizes[i - 1] != 0:
                sw = section_calculator.get_calculator_prompt('Section ' + str(i) + ' Width')
                sw.equal = False
                sw.distance_value = self.section_sizes[i - 1]

        section_calculator.calculate()

    def _add_shelves_to_section(self, section):
        props = bpy.context.scene.hb_frameless
        dim_x = section.var_input('Dim X', 'dim_x')
        dim_y = section.var_input('Dim Y', 'dim_y')
        dim_z = section.var_input('Dim Z', 'dim_z')

        shelf = CabinetPart()
        shelf.create('Shelf')
        shelf.obj['IS_FRAMELESS_INTERIOR_PART'] = True
        shelf.obj['MENU_ID'] = 'HOME_BUILDER_MT_interior_part_commands'
        shelf.obj.parent = section.obj
        shelf.driver_location('z', 'dim_z/2', [dim_z])
        shelf.driver_input("Length", 'dim_x', [dim_x])
        shelf.driver_input("Width", 'dim_y-.025', [dim_y])
        shelf.set_input("Thickness", props.default_carcass_part_thickness)

    def _add_rollouts_to_section(self, section):
        # TODO: Implement rollout creation
        pass


class CornerCabinet(Cabinet):
    """Base class for corner cabinets.
    
    Corner cabinets fit into a corner where two walls meet at 90 degrees.
    They have an L-shaped footprint with the origin (0,0) at the back-left 
    corner (the inside corner where walls meet).
    
    - Left side extends in the -Y direction
    - Right side extends in the +X direction from the right edge
    
    Dimensions:
    - Dim X (width): total width from origin to right edge
    - Dim Y (depth): total depth from origin to front 
    - Dim Z (height): total height
    - Left Depth: depth of left wing
    - Right Depth: depth of right wing (from right side going back)
    
    Subclasses override add_corner_modifier() to control the top/bottom shape:
    - Diagonal: CPM_CHAMFER (45° angled front)
    - Pie Cut: CPM_CORNERNOTCH (rectangular notch, two fronts at 90°)
    """

    door_pull_location = "Base"  # Override in subclass: "Base", "Tall", or "Upper"
    
    corner_size = inch(36)  # Size of corner (both directions)
    
    def add_properties_corner(self):
        props = bpy.context.scene.hb_frameless
        self.add_property('Left Depth', 'DISTANCE', self.depth)
        self.add_property('Right Depth', 'DISTANCE', self.depth)

    def add_corner_modifier(self, part, dim_x, dim_y, ld, rd, mt):
        """Add the corner shape modifier to a top or bottom panel.
        
        Override in subclasses to use CPM_CHAMFER (diagonal) or 
        CPM_CORNERNOTCH (pie cut).
        """
        raise NotImplementedError("Subclasses must implement add_corner_modifier")

    def create_corner_bays(self, dim_x, dim_y, dim_z, mt, tkh, ld, rd):
        """Create bay openings for corner cabinet doors.
        
        Override in subclasses. Called at end of create_corner_base_carcass().
        Default is no bays (no doors).
        """
        pass

    def add_corner_doors(self):
        """Add a single door to each front face of the pie-cut notch.
        
        Left door covers the notch X-face (at Y=-rd, running in +X).
        Right door covers the notch Y-face (at X=ld, running in -Y).
        Both doors hinge from the notch corner.
        
        Overlay edges:
          Top/Bottom: full overlay over horizontal carcass panels
          Outer: full overlay over adjacent side panel
          Inner (corner): half gap between the two doors
        """
        dim_x = self.var_input('Dim X', 'dim_x')
        dim_y = self.var_input('Dim Y', 'dim_y')
        dim_z = self.var_input('Dim Z', 'dim_z')
        mt = self.var_prop('Material Thickness', 'mt')
        tkh = self.var_prop('Toe Kick Height', 'tkh')
        rb = self.var_prop('Remove Bottom', 'rb')
        ld = self.var_prop('Left Depth', 'ld')
        rd = self.var_prop('Right Depth', 'rd')

        # Overlay properties
        self.add_property('Front Thickness', 'DISTANCE', inch(.75))
        self.add_property('Door to Cabinet Gap', 'DISTANCE', inch(.125))
        self.add_property('Inset Front', 'CHECKBOX', False)
        self.add_property('Inset Reveal', 'DISTANCE', inch(.125))
        self.add_property('Half Overlay Top', 'CHECKBOX', False)
        self.add_property('Half Overlay Bottom', 'CHECKBOX', False)
        self.add_property('Half Overlay Outer', 'CHECKBOX', False)
        self.add_property('Top Reveal', 'DISTANCE', inch(.0625))
        self.add_property('Bottom Reveal', 'DISTANCE', inch(0))
        self.add_property('Outer Reveal', 'DISTANCE', inch(.0625))
        self.add_property('Vertical Gap', 'DISTANCE', inch(.125))

        ft = self.var_prop('Front Thickness', 'ft')
        dtcg = self.var_prop('Door to Cabinet Gap', 'dtcg')
        inset = self.var_prop('Inset Front', 'inset')
        ir = self.var_prop('Inset Reveal', 'ir')
        hot = self.var_prop('Half Overlay Top', 'hot')
        hob = self.var_prop('Half Overlay Bottom', 'hob')
        hoo = self.var_prop('Half Overlay Outer', 'hoo')
        tr = self.var_prop('Top Reveal', 'tr')
        br = self.var_prop('Bottom Reveal', 'br')
        otr = self.var_prop('Outer Reveal', 'otr')
        vg = self.var_prop('Vertical Gap', 'vg')

        # Overlay calculation empty (avoids circular dependencies)
        overlay_obj = self.add_empty('Corner Overlay Calc')
        overlay_obj.home_builder.add_property("Overlay Top", 'DISTANCE', 0.0)
        overlay_obj.home_builder.add_property("Overlay Bottom", 'DISTANCE', 0.0)
        overlay_obj.home_builder.add_property("Overlay Outer", 'DISTANCE', 0.0)

        # Inset: negative overlay (door smaller than opening)
        # Half Overlay: (thickness - gap) / 2
        # Full Overlay: thickness - reveal
        overlay_obj.home_builder.driver_prop("Overlay Top", "IF(inset,-ir,IF(hot,(mt-vg)/2,mt-tr))", [inset, ir, hot, mt, vg, tr])
        overlay_obj.home_builder.driver_prop("Overlay Bottom", "IF(inset,-ir,IF(hob,(mt-vg)/2,mt-br))", [inset, ir, hob, mt, vg, br])
        overlay_obj.home_builder.driver_prop("Overlay Outer", "IF(inset,-ir,IF(hoo,(mt-vg)/2,mt-otr))", [inset, ir, hoo, mt, vg, otr])

        to = overlay_obj.home_builder.var_prop('Overlay Top', 'to')
        bo = overlay_obj.home_builder.var_prop('Overlay Bottom', 'bo')
        oo = overlay_obj.home_builder.var_prop('Overlay Outer', 'oo')

        # Door swing: determines which door(s) get a pull handle
        self.add_property("Door Swing", 'COMBOBOX', 0, combobox_items=["Left", "Right"])
        ds = self.var_prop('Door Swing', 'ds')

        # --- Left door (notch X-face) ---
        left_door = CabinetDoor()
        left_door.door_pull_location = self.door_pull_location
        left_door.create("Left Door")
        left_door.obj.parent = self.obj
        left_door.obj.rotation_euler.y = math.radians(-90)
        left_door.obj.rotation_euler.z = math.radians(180)
        # X: inner edge at notch corner (inset flush, overlay offset by dtcg)
        left_door.driver_location('x', 'IF(inset,ld-ft,ld+dtcg)', [inset, ld, ft, dtcg])
        # Y: inset recesses into opening, overlay projects forward
        left_door.driver_location('y', 'IF(inset,-rd+ft,-rd-dtcg)', [inset, rd, ft, dtcg])
        # Z: shift down by bottom overlay
        left_door.driver_location('z', 'tkh+IF(rb,0,mt)-bo', [tkh, mt, rb, bo])
        # Height: opening height + top + bottom overlay
        left_door.driver_input("Length", 'dim_z-tkh-IF(rb,0,mt)-mt+to+bo', [dim_z, tkh, mt, rb, to, bo])
        # Width: notch X span + outer overlay (oo goes negative for inset)
        left_door.driver_input("Width", 'IF(inset,dim_y-rd+oo,dim_y-rd-mt+oo-dtcg)', [inset, dim_y, rd, mt, oo, dtcg])
        left_door.driver_input("Thickness", 'ft', [ft])

        # --- Right door (notch Y-face) ---
        right_door = CabinetDoor()
        right_door.door_pull_location = self.door_pull_location
        right_door.create("Right Door")
        right_door.obj.parent = self.obj
        right_door.obj.rotation_euler.x = math.radians(90)
        right_door.obj.rotation_euler.y = math.radians(-90)
        # X: inset recesses into opening, overlay projects forward
        right_door.driver_location('x', 'IF(inset,ld+mt-ft-oo,ld+dtcg+mt+dtcg)', [inset, ld, mt, ft, oo, dtcg])
        # Y: inner edge at notch corner (inset flush, overlay offset by dtcg)
        right_door.driver_location('y', 'IF(inset,-rd+ft,-rd-dtcg)', [inset, rd, ft, dtcg])
        # Z: shift down by bottom overlay
        right_door.driver_location('z', 'tkh+IF(rb,0,mt)-bo', [tkh, mt, rb, bo])
        # Height: opening height + top + bottom overlay
        right_door.driver_input("Length", 'dim_z-tkh-IF(rb,0,mt)-mt+to+bo', [dim_z, tkh, mt, rb, to, bo])
        # Width: notch Y span + outer overlay (oo goes negative for inset)
        right_door.driver_input("Width", 'IF(inset,dim_x-ld-mt+oo*2,dim_x-ld-mt+oo-dtcg-mt-dtcg)', [inset, dim_x, ld, mt, oo, dtcg])
        right_door.driver_input("Thickness", 'ft', [ft])
        right_door.set_input("Mirror Y", True)

        # Hide pulls based on door swing setting
        # ds==0: Left swing (pull on left door only)
        # ds==1: Right swing (pull on right door only)
        # ds==2: Both (pulls on both doors)
        for child in left_door.obj.children:
            if 'IS_CABINET_PULL' in child:
                pull = GeoNodeHardware(child)
                pull.driver_hide('IF(ds==0,True,False)', [ds])
                break

        for child in right_door.obj.children:
            if 'IS_CABINET_PULL' in child:
                pull = GeoNodeHardware(child)
                pull.driver_hide('IF(ds==1,True,False)', [ds])
                break


    def create_corner_base_carcass(self, name):
        """Create the corner base cabinet carcass.
        
        Shared by all corner base cabinet types (diagonal, pie cut).
        The top/bottom panel shape is determined by add_corner_modifier().
        """
        super().create_cabinet(name)
        
        self.add_properties_common()
        self.add_properties_toe_kick()
        self.add_properties_corner()
        
        # Set dimensions - corner size determines X and Y
        self.set_input('Dim X', self.corner_size)
        self.set_input('Dim Y', self.corner_size)
        self.set_input('Dim Z', self.height)
        
        dim_x = self.var_input('Dim X', 'dim_x')
        dim_y = self.var_input('Dim Y', 'dim_y')
        dim_z = self.var_input('Dim Z', 'dim_z')
        
        mt = self.var_prop('Material Thickness', 'mt')
        tkh = self.var_prop('Toe Kick Height', 'tkh')
        tks = self.var_prop('Toe Kick Setback', 'tks')
        ld = self.var_prop('Left Depth', 'ld')
        rd = self.var_prop('Right Depth', 'rd')
        
        # Left Side - runs along Y axis on the left edge
        # Positioned at X=0, extends from Y=0 to Y=-left_depth
        left_side = CabinetSideNotched()
        left_side.create('Left Side', tkh, tks, mt)
        left_side.obj.parent = self.obj
        left_side.obj.rotation_euler.y = math.radians(-90)
        left_side.obj.rotation_euler.z = math.radians(-90)
        left_side.driver_location('y', '-dim_y', [dim_y])
        left_side.driver_input("Length", 'dim_z', [dim_z])
        left_side.driver_input("Width", 'ld', [ld])
        left_side.driver_input("Thickness", 'mt', [mt])
        
        # Right Side - runs along X axis from the right edge
        # Positioned at Y=0, extends from X=dim_x to X=dim_x-right_depth
        right_side = CabinetSideNotched()
        right_side.create('Right Side', tkh, tks, mt)
        right_side.obj.parent = self.obj
        right_side.driver_location('x', 'dim_x', [dim_x])
        right_side.obj.rotation_euler.y = math.radians(-90)
        right_side.driver_input("Length", 'dim_z', [dim_z])
        right_side.driver_input("Width", 'rd', [rd])
        right_side.driver_input("Thickness", 'mt', [mt])
        right_side.set_input("Mirror Y", True)
        right_side.set_input("Mirror Z", False)
        
        # Left Back - vertical panel against left wall (X=0 plane)
        # Runs from the left side to the corner
        left_back = CabinetPart()
        left_back.create('Left Back')
        left_back.obj.parent = self.obj
        left_back.obj.rotation_euler.y = math.radians(-90)
        left_back.driver_location('z', 'tkh+mt', [tkh, mt])
        left_back.driver_input("Length", 'dim_z-tkh-mt*2', [dim_z, tkh, mt])
        left_back.driver_input("Width", 'dim_y-mt', [dim_y, mt])
        left_back.driver_input("Thickness", 'mt', [mt])
        left_back.set_input("Mirror Y", True)
        left_back.set_input("Mirror Z", True)
        
        # Right Back - vertical panel against right wall (Y=0 plane)
        # Runs from the right side to the corner
        right_back = CabinetPart()
        right_back.create('Right Back')
        right_back.obj.parent = self.obj
        right_back.driver_location('x', 'mt', [mt])
        right_back.driver_location('z', 'tkh+mt', [tkh, mt])
        right_back.obj.rotation_euler.x = math.radians(-90)
        right_back.driver_input("Length", 'dim_x-mt-mt', [dim_x, rd, mt])
        right_back.driver_input("Width", 'dim_z-tkh-mt*2', [dim_z, tkh, mt])
        right_back.driver_input("Thickness", 'mt', [mt])
        right_back.set_input("Mirror Y", True)
        right_back.set_input("Mirror Z", True)
        
        # Bottom panel
        bottom = CabinetPart()
        bottom.create('Bottom')
        bottom.obj.parent = self.obj
        bottom.driver_location('z', 'tkh', [tkh])
        bottom.driver_input("Length", 'dim_x-mt', [dim_x, mt])
        bottom.driver_input("Width", 'dim_y-mt', [dim_y, mt])
        bottom.driver_input("Thickness", 'mt', [mt])
        bottom.set_input("Mirror Y", True)
        bottom.set_input("Mirror Z", False)
        self.add_corner_modifier(bottom, dim_x, dim_y, ld, rd, mt)
        
        # Top panel (matching bottom)
        top = CabinetPart()
        top.create('Top')
        top.obj.parent = self.obj
        top.driver_location('z', 'dim_z', [dim_z])
        top.driver_input("Length", 'dim_x-mt', [dim_x, mt])
        top.driver_input("Width", 'dim_y-mt', [dim_y, mt])
        top.driver_input("Thickness", 'mt', [mt])
        top.set_input("Mirror Y", True)
        top.set_input("Mirror Z", True)
        self.add_corner_modifier(top, dim_x, dim_y, ld, rd, mt)

        # Toe kicks
        left_toe_kick = CabinetPart()
        left_toe_kick.create('Left Toe Kick')
        left_toe_kick.obj.parent = self.obj
        left_toe_kick.obj.rotation_euler.x = math.radians(-90)
        left_toe_kick.obj.rotation_euler.z = math.radians(90)
        left_toe_kick.driver_location('x', 'ld-tks', [ld,tks])
        left_toe_kick.driver_location('y', '-dim_y+mt', [dim_y, mt])
        left_toe_kick.driver_input("Length", 'dim_y-rd-mt+tks', [dim_y, rd, mt, tks])
        left_toe_kick.driver_input("Width", 'tkh', [tkh])
        left_toe_kick.driver_input("Thickness", 'mt', [mt])
        left_toe_kick.set_input("Mirror Y", True)
        
        right_toe_kick = CabinetPart()
        right_toe_kick.create('Right Toe Kick')
        right_toe_kick.obj.parent = self.obj
        right_toe_kick.obj.rotation_euler.x = math.radians(-90)
        right_toe_kick.driver_location('x', 'dim_x-mt', [dim_x, mt])
        right_toe_kick.driver_location('y', '-rd+tks', [rd, tks])
        right_toe_kick.driver_input("Length", 'dim_x-ld-mt+tks', [dim_x, ld, mt, tks])
        right_toe_kick.driver_input("Width", 'tkh', [tkh])
        right_toe_kick.driver_input("Thickness", 'mt', [mt])
        right_toe_kick.set_input("Mirror X", True)
        right_toe_kick.set_input("Mirror Y", True)

    def create_corner_upper_carcass(self, name):
        """Create the corner upper cabinet carcass.
        
        Similar to base but without toe kicks or notched sides.
        Bottom sits at Z=0, sides are plain CabinetPart.
        """
        super().create_cabinet(name)
        
        self.add_properties_common()
        self.add_properties_corner()
        
        # Set dimensions
        self.set_input('Dim X', self.corner_size)
        self.set_input('Dim Y', self.corner_size)
        self.set_input('Dim Z', self.height)
        
        dim_x = self.var_input('Dim X', 'dim_x')
        dim_y = self.var_input('Dim Y', 'dim_y')
        dim_z = self.var_input('Dim Z', 'dim_z')
        
        mt = self.var_prop('Material Thickness', 'mt')
        ld = self.var_prop('Left Depth', 'ld')
        rd = self.var_prop('Right Depth', 'rd')
        
        # Left Side - runs along Y axis on the left edge
        left_side = CabinetPart()
        left_side.create('Left Side')
        left_side.obj.parent = self.obj
        left_side.obj.rotation_euler.y = math.radians(-90)
        left_side.obj.rotation_euler.z = math.radians(-90)
        left_side.driver_location('y', '-dim_y', [dim_y])
        left_side.driver_input("Length", 'dim_z', [dim_z])
        left_side.driver_input("Width", 'ld', [ld])
        left_side.driver_input("Thickness", 'mt', [mt])
        
        # Right Side - runs along X axis from the right edge
        right_side = CabinetPart()
        right_side.create('Right Side')
        right_side.obj.parent = self.obj
        right_side.driver_location('x', 'dim_x', [dim_x])
        right_side.obj.rotation_euler.y = math.radians(-90)
        right_side.driver_input("Length", 'dim_z', [dim_z])
        right_side.driver_input("Width", 'rd', [rd])
        right_side.driver_input("Thickness", 'mt', [mt])
        right_side.set_input("Mirror Y", True)
        right_side.set_input("Mirror Z", False)
        
        # Left Back - vertical panel against left wall
        left_back = CabinetPart()
        left_back.create('Left Back')
        left_back.obj.parent = self.obj
        left_back.obj.rotation_euler.y = math.radians(-90)
        left_back.driver_location('z', 'mt', [mt])
        left_back.driver_input("Length", 'dim_z-mt*2', [dim_z, mt])
        left_back.driver_input("Width", 'dim_y-mt', [dim_y, mt])
        left_back.driver_input("Thickness", 'mt', [mt])
        left_back.set_input("Mirror Y", True)
        left_back.set_input("Mirror Z", True)
        
        # Right Back - vertical panel against right wall
        right_back = CabinetPart()
        right_back.create('Right Back')
        right_back.obj.parent = self.obj
        right_back.driver_location('x', 'mt', [mt])
        right_back.driver_location('z', 'mt', [mt])
        right_back.obj.rotation_euler.x = math.radians(-90)
        right_back.driver_input("Length", 'dim_x-mt-mt', [dim_x, mt])
        right_back.driver_input("Width", 'dim_z-mt*2', [dim_z, mt])
        right_back.driver_input("Thickness", 'mt', [mt])
        right_back.set_input("Mirror Y", True)
        right_back.set_input("Mirror Z", True)
        
        # Bottom panel
        bottom = CabinetPart()
        bottom.create('Bottom')
        bottom.obj.parent = self.obj
        bottom.driver_input("Length", 'dim_x-mt', [dim_x, mt])
        bottom.driver_input("Width", 'dim_y-mt', [dim_y, mt])
        bottom.driver_input("Thickness", 'mt', [mt])
        bottom.set_input("Mirror Y", True)
        bottom.set_input("Mirror Z", False)
        self.add_corner_modifier(bottom, dim_x, dim_y, ld, rd, mt)
        
        # Top panel
        top = CabinetPart()
        top.create('Top')
        top.obj.parent = self.obj
        top.driver_location('z', 'dim_z', [dim_z])
        top.driver_input("Length", 'dim_x-mt', [dim_x, mt])
        top.driver_input("Width", 'dim_y-mt', [dim_y, mt])
        top.driver_input("Thickness", 'mt', [mt])
        top.set_input("Mirror Y", True)
        top.set_input("Mirror Z", True)
        self.add_corner_modifier(top, dim_x, dim_y, ld, rd, mt)


class DiagonalCornerBaseCabinet(CornerCabinet):
    """Diagonal corner base cabinet - 45° angled front."""
    
    def __init__(self):
        super().__init__()
        props = bpy.context.scene.hb_frameless
        self.corner_size = props.base_inside_corner_size
        self.height = props.base_cabinet_height
        self.depth = props.base_cabinet_depth
    
    def create(self, name="Diagonal Corner Base"):
        self.create_corner_base_carcass(name)
        self.obj['CABINET_TYPE'] = 'BASE'
        self.obj['CORNER_TYPE'] = 'DIAGONAL'
        self.obj['IS_CORNER_CABINET'] = True

    def add_corner_modifier(self, part, dim_x, dim_y, ld, rd, mt):
        """Diagonal uses CPM_CHAMFER to cut a 45° angle."""
        chamfer = part.add_part_modifier('CPM_CHAMFER', 'Chamfer')
        chamfer.driver_input('X', 'dim_x-ld-mt', [dim_x, ld, mt])
        chamfer.driver_input('Y', 'dim_y-rd-mt', [dim_y, rd, mt])
        chamfer.driver_input('Route Depth', 'mt+.01', [mt])
        chamfer.set_input('Flip X', True)


class PieCutCornerBaseCabinet(CornerCabinet):
    """Pie cut corner base cabinet - rectangular notch, two fronts at 90°."""
    
    def __init__(self):
        super().__init__()
        props = bpy.context.scene.hb_frameless
        self.corner_size = props.base_inside_corner_size
        self.height = props.base_cabinet_height
        self.depth = props.base_cabinet_depth
    
    def create(self, name="Pie Cut Corner Base"):
        self.create_corner_base_carcass(name)
        self.obj['CABINET_TYPE'] = 'BASE'
        self.obj['CORNER_TYPE'] = 'PIECUT'
        self.obj['IS_CORNER_CABINET'] = True

        # Add corner notch to cage so wireframe matches the L-shape
        dim_x = self.var_input('Dim X', 'dim_x')
        dim_y = self.var_input('Dim Y', 'dim_y')
        dim_z = self.var_input('Dim Z', 'dim_z')
        ld = self.var_prop('Left Depth', 'ld')
        rd = self.var_prop('Right Depth', 'rd')
        mt = self.var_prop('Material Thickness', 'mt')
        cpm = CabinetPartModifier(self.obj)
        cpm.add_node('CPM_CORNERNOTCH', 'Corner Notch')
        cpm.driver_input('X', 'dim_x-ld', [dim_x, ld, mt])
        cpm.driver_input('Y', 'dim_y-rd', [dim_y, rd, mt])
        cpm.driver_input('Route Depth', 'dim_z+.01', [dim_z])
        cpm.set_input('Flip X', True)
        cpm.set_input('Flip Y', True)

        self.add_corner_doors()

    def add_corner_modifier(self, part, dim_x, dim_y, ld, rd, mt):
        """Pie cut uses CPM_CORNERNOTCH for a rectangular notch."""
        notch = part.add_part_modifier('CPM_CORNERNOTCH', 'Corner Notch')
        notch.driver_input('X', 'dim_x-ld-mt', [dim_x, ld, mt])
        notch.driver_input('Y', 'dim_y-rd-mt', [dim_y, rd, mt])
        notch.driver_input('Route Depth', 'mt+.01', [mt])
        notch.set_input('Flip X', True)
        notch.set_input('Flip Y', True)



class DiagonalCornerTallCabinet(CornerCabinet):
    """Diagonal corner tall cabinet."""
    
    def __init__(self):
        super().__init__()
        props = bpy.context.scene.hb_frameless
        self.corner_size = props.tall_inside_corner_size
        self.height = props.tall_cabinet_height
        self.depth = props.tall_cabinet_depth
    
    def create(self, name="Diagonal Corner Tall"):
        self.create_cabinet(name)
        self.obj['CABINET_TYPE'] = 'TALL'
        self.obj['CORNER_TYPE'] = 'DIAGONAL'


class PieCutCornerTallCabinet(CornerCabinet):
    """Pie cut corner tall cabinet."""

    door_pull_location = "Tall"
    
    def __init__(self):
        super().__init__()
        props = bpy.context.scene.hb_frameless
        self.corner_size = props.tall_inside_corner_size
        self.height = props.tall_cabinet_height
        self.depth = props.tall_cabinet_depth
    
    def create(self, name="Pie Cut Corner Tall"):
        self.create_corner_base_carcass(name)
        self.obj['CABINET_TYPE'] = 'TALL'
        self.obj['CORNER_TYPE'] = 'PIECUT'
        self.obj['IS_CORNER_CABINET'] = True

        # Add corner notch to cage
        dim_x = self.var_input('Dim X', 'dim_x')
        dim_y = self.var_input('Dim Y', 'dim_y')
        dim_z = self.var_input('Dim Z', 'dim_z')
        ld = self.var_prop('Left Depth', 'ld')
        rd = self.var_prop('Right Depth', 'rd')
        mt = self.var_prop('Material Thickness', 'mt')
        cpm = CabinetPartModifier(self.obj)
        cpm.add_node('CPM_CORNERNOTCH', 'Corner Notch')
        cpm.driver_input('X', 'dim_x-ld', [dim_x, ld, mt])
        cpm.driver_input('Y', 'dim_y-rd', [dim_y, rd, mt])
        cpm.driver_input('Route Depth', 'dim_z+.01', [dim_z])
        cpm.set_input('Flip X', True)
        cpm.set_input('Flip Y', True)

        self.add_corner_doors()

    def add_corner_modifier(self, part, dim_x, dim_y, ld, rd, mt):
        """Pie cut uses CPM_CORNERNOTCH for a rectangular notch."""
        notch = part.add_part_modifier('CPM_CORNERNOTCH', 'Corner Notch')
        notch.driver_input('X', 'dim_x-ld-mt', [dim_x, ld, mt])
        notch.driver_input('Y', 'dim_y-rd-mt', [dim_y, rd, mt])
        notch.driver_input('Route Depth', 'mt+.01', [mt])
        notch.set_input('Flip X', True)
        notch.set_input('Flip Y', True)


class DiagonalCornerUpperCabinet(CornerCabinet):
    """Diagonal corner upper cabinet."""
    
    def __init__(self):
        super().__init__()
        props = bpy.context.scene.hb_frameless
        self.corner_size = props.upper_inside_corner_size
        self.height = props.upper_cabinet_height
        self.depth = props.upper_cabinet_depth
    
    def create(self, name="Diagonal Corner Upper"):
        self.create_cabinet(name)
        self.obj['CABINET_TYPE'] = 'UPPER'
        self.obj['CORNER_TYPE'] = 'DIAGONAL'


class PieCutCornerUpperCabinet(CornerCabinet):
    """Pie-cut corner upper cabinet."""

    door_pull_location = "Upper"
    
    def __init__(self):
        super().__init__()
        props = bpy.context.scene.hb_frameless
        self.corner_size = props.upper_inside_corner_size
        self.height = props.upper_cabinet_height
        self.depth = props.upper_cabinet_depth
    
    def create(self, name="Pie Cut Corner Upper"):
        self.create_corner_upper_carcass(name)
        self.obj['CABINET_TYPE'] = 'UPPER'
        self.obj['CORNER_TYPE'] = 'PIECUT'
        self.obj['IS_CORNER_CABINET'] = True

        # Add properties that add_corner_doors expects (upper has no toe kick)
        self.add_property('Toe Kick Height', 'DISTANCE', 0)
        self.add_property('Remove Bottom', 'CHECKBOX', False)

        # Add corner notch to cage
        dim_x = self.var_input('Dim X', 'dim_x')
        dim_y = self.var_input('Dim Y', 'dim_y')
        dim_z = self.var_input('Dim Z', 'dim_z')
        ld = self.var_prop('Left Depth', 'ld')
        rd = self.var_prop('Right Depth', 'rd')
        mt = self.var_prop('Material Thickness', 'mt')
        cpm = CabinetPartModifier(self.obj)
        cpm.add_node('CPM_CORNERNOTCH', 'Corner Notch')
        cpm.driver_input('X', 'dim_x-ld', [dim_x, ld, mt])
        cpm.driver_input('Y', 'dim_y-rd', [dim_y, rd, mt])
        cpm.driver_input('Route Depth', 'dim_z+.01', [dim_z])
        cpm.set_input('Flip X', True)
        cpm.set_input('Flip Y', True)

        self.add_corner_doors()

    def add_corner_modifier(self, part, dim_x, dim_y, ld, rd, mt):
        """Pie cut uses CPM_CORNERNOTCH for a rectangular notch."""
        notch = part.add_part_modifier('CPM_CORNERNOTCH', 'Corner Notch')
        notch.driver_input('X', 'dim_x-ld-mt', [dim_x, ld, mt])
        notch.driver_input('Y', 'dim_y-rd-mt', [dim_y, rd, mt])
        notch.driver_input('Route Depth', 'mt+.01', [mt])
        notch.set_input('Flip X', True)
        notch.set_input('Flip Y', True)