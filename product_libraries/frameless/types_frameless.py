import bpy
import math
import os
from ...hb_types import GeoNodeObject, GeoNodeCage, GeoNodeCutpart, GeoNodeHardware
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
        self.obj.display_type = 'WIRE'
        
        self.set_input('Dim X', self.width)
        self.set_input('Dim Y', self.depth)
        self.set_input('Dim Z', self.height)
        self.set_input('Mirror Y', True)

    def create_base_tall_carcass(self,name):
        self.create_cabinet(name)

        self.add_properties_common()
        self.add_properties_toe_kick()

        dim_x = self.var_input('Dim X', 'dim_x')
        dim_y = self.var_input('Dim Y', 'dim_y')
        dim_z = self.var_input('Dim Z', 'dim_z')

        mt = self.var_prop('Material Thickness', 'mt')
        tkh = self.var_prop('Toe Kick Height', 'tkh')
        tks = self.var_prop('Toe Kick Setback', 'tks')

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

        back = CabinetPart()
        back.create('Back')
        back.obj.parent = self.obj
        back.obj.rotation_euler.x = math.radians(90)
        back.obj.rotation_euler.y = math.radians(-90)
        back.driver_location('x', 'mt',[mt])
        back.driver_location('z', 'tkh+mt',[tkh,mt])
        back.driver_input("Length", 'dim_z-tkh-(mt*2)', [dim_z,tkh,mt])
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
        opening.driver_location('z', 'tkh+mt',[tkh,mt])
        opening.driver_input("Dim X", 'dim_x-(mt*2)', [dim_x,mt])
        opening.driver_input("Dim Y", 'dim_y-mt', [dim_y,mt])
        opening.driver_input("Dim Z", 'dim_z-tkh-(mt*2)', [dim_z,tkh,mt])

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
        self.create_base_tall_carcass(name)
        self.obj['CABINET_TYPE'] = 'BASE'
        
        # Add exterior based on base_exterior property
        props = bpy.context.scene.hb_frameless
        self.add_exterior()
    
    def add_exterior(self):
        """Add doors/drawers based on exterior type."""
        print(self.default_exterior)
        if self.default_exterior == 'Doors':
            self.add_doors()
        elif self.default_exterior == 'Door Drawer':
            self.add_door_drawer()
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
    
    def add_door_drawer(self):
        """Add a drawer on top and doors below."""
        drawer = Drawer()
        drawer.half_overlay_bottom = True
        door = Doors()
        door.half_overlay_top = True

        door_drawer = SplitterVertical()
        door_drawer.splitter_qty = 1
        door_drawer.opening_sizes = [inch(5),0]
        door_drawer.opening_inserts = [drawer,door]
        self.add_cage_to_bay(door_drawer)
    
    def add_drawer_stack(self, count):
        """Add a stack of drawers."""
        door_drawer = SplitterVertical()
        door_drawer.splitter_qty = count - 1
        for i in range(count):
            drawer = Drawer()
            if i == 0:
                drawer.half_overlay_bottom = True
                door_drawer.opening_sizes.append(inch(5))
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
        self.width = props.default_cabinet_width
        self.height = props.tall_cabinet_height
        self.depth = props.tall_cabinet_depth
    
    def create(self, name="Tall Cabinet"):
        self.create_base_tall_carcass(name)
        self.obj['CABINET_TYPE'] = 'TALL'
        self.add_doors()
    
    def add_doors(self):
        """Add door fronts to the cabinet bay."""
        if self.is_stacked:
            pass #TODO: IMPELMENT STATCKED DOOR OPENINGS
        else:
            doors = Doors()
            doors.door_pull_location = "Tall"
            self.add_cage_to_bay(doors)


class UpperCabinet(Cabinet):
    """Wall-mounted upper cabinet. No toe kick."""
    
    is_stacked = False

    def __init__(self):
        super().__init__()
        props = bpy.context.scene.hb_frameless
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
        if self.is_stacked:
            pass #TODO: IMPELMENT STATCKED DOOR OPENINGS
        else:
            doors = Doors()
            doors.door_pull_location = "Upper"
            self.add_cage_to_bay(doors)


class CabinetBay(GeoNodeCage):

    def create(self,name):
        super().create(name)
        self.obj['IS_FRAMELESS_BAY_CAGE'] = True
        self.obj.display_type = 'WIRE'


class SplitterVertical(GeoNodeCage):

    splitter_qty = 1
    opening_sizes = []
    opening_inserts = []

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

        # Add Shelf Splitters
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

        # Set Opening Sizes
        for i in range(1,self.splitter_qty+2):
            if self.opening_sizes[i-1] != 0:
                oh = opening_calculator.get_calculator_prompt('Opening ' + str(i) + ' Height')
                oh.equal = False
                oh.distance_value = self.opening_sizes[i-1]

        opening_calculator.calculate() 


class CabinetOpening(GeoNodeCage):

    half_overlay_top = False
    half_overlay_bottom = False
    half_overlay_left = False
    half_overlay_right = False

    def create(self,name):
        super().create(name)
        self.obj['IS_FRAMELESS_OPENING_CAGE'] = True
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

        # Overlay Prompts Stored in Separate Empty Object to Avoid Circular Dependency Graph Issues
        self.overlay_prompts = self.add_empty('Overlay Prompt Obj')
        self.overlay_prompts.home_builder.add_property("Overlay Top",'DISTANCE',0.0)
        self.overlay_prompts.home_builder.add_property("Overlay Bottom",'DISTANCE',0.0)
        self.overlay_prompts.home_builder.add_property("Overlay Left",'DISTANCE',0.0)
        self.overlay_prompts.home_builder.add_property("Overlay Right",'DISTANCE',0.0)

        self.overlay_prompts.home_builder.driver_prop("Overlay Top", "IF(hot,(tt-vg)/2,tt-tr)", [hot,tt,vg,tr])
        self.overlay_prompts.home_builder.driver_prop("Overlay Bottom", "IF(hob,(bt-vg)/2,bt-br)", [hob,bt,vg,br])
        self.overlay_prompts.home_builder.driver_prop("Overlay Left", "IF(hol,(lt-vg)/2,lt-lr)", [hol,lt,vg,lr])
        self.overlay_prompts.home_builder.driver_prop("Overlay Right", "IF(hor,(rt-vg)/2,rt-rr)", [hor,rt,vg,rr])

        return self.overlay_prompts


class CabinetInterior(GeoNodeCage):

    def create(self,name):
        super().create(name)
        self.obj['IS_FRAMELESS_INTERIOR_CAGE'] = True
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
        shelves.obj.parent = self.obj
        # array_mod = shelves.obj.modifiers.new('Qty','ARRAY')
        # array_mod.count = 1   
        # array_mod.use_relative_offset = False
        # array_mod.use_constant_offset = True
        # array_mod.constant_offset_displace = (0,0,0)        
        shelves.driver_location('x', 'clip_gap',[clip_gap])
        shelves.driver_location('y', 'setback',[setback])
        shelves.driver_location('z', '(dim_z-(mt*qty))/(qty+1)',[dim_z,mt,qty])
        shelves.driver_input("Length", 'dim_x-clip_gap*2', [dim_x,clip_gap])
        shelves.driver_input("Width", 'dim_y-setback', [dim_y,setback])
        shelves.driver_input("Thickness", 'mt', [mt])
        # shelves.set_input("Mirror Y", True)
        # shelves.set_input("Mirror Z", False)


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

        left_door = CabinetDoor()
        left_door.door_pull_location = self.door_pull_location
        left_door.create('Left Door')
        left_door.obj.parent = self.obj
        left_door.obj.rotation_euler.x = math.radians(90)
        left_door.obj.rotation_euler.y = math.radians(-90)
        left_door.driver_location('x', '-lo',[lo])
        left_door.driver_location('y', '-door_to_cab_gap',[door_to_cab_gap])
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
        right_door.driver_location('y', '-door_to_cab_gap',[door_to_cab_gap])
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

        interior.create('Interior')
        interior.obj.parent = self.obj
        interior.driver_input('Dim X','x',[x])
        interior.driver_input('Dim Y','y',[y])
        interior.driver_input('Dim Z','z',[z])         


class Drawer(CabinetOpening):

    def create(self):
        super().create("Doors")

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

        drawer_front = CabinetDrawerFront()
        drawer_front.create('Drawer Front')
        drawer_front.obj.parent = self.obj
        drawer_front.obj.rotation_euler.x = math.radians(90)
        drawer_front.obj.rotation_euler.y = math.radians(-90)
        drawer_front.driver_location('x', '-lo',[lo])
        drawer_front.driver_location('y', '-door_to_cab_gap',[door_to_cab_gap])
        drawer_front.driver_location('z', '-bo',[bo])
        drawer_front.driver_input("Length", 'dim_z+to+bo', [dim_z,to,bo])
        drawer_front.driver_input("Width", 'dim_x+lo+ro', [dim_x,lo,ro])
        drawer_front.driver_input("Thickness", 'ft', [ft])   
        drawer_front.set_input("Mirror Y", True)

        self.add_drawer_box()

    def add_drawer_box(self):
        pass
        #TODO:ADD Drawer BOX
        # x = self.var_input('Dim X', 'x')
        # y = self.var_input('Dim Y', 'y')
        # z = self.var_input('Dim Z', 'z')

        # interior.create('Interior')
        # interior.obj.parent = self.obj
        # interior.driver_input('Dim X','x',[x])
        # interior.driver_input('Dim Y','y',[y])
        # interior.driver_input('Dim Z','z',[z])   


class CabinetPart(GeoNodeCutpart):

    def create(self,name):
        super().create(name)
        self.obj['CABINET_PART'] = True
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

class CabinetDoor(CabinetFront):

    door_pull_location = "Base"

    def get_pull_object(self):
        props = bpy.context.scene.hb_frameless
        if props.current_door_pull_object:
            return props.current_door_pull_object
        else:
            pull_path = os.path.join(os.path.dirname(__file__),'frameless_assets','cabinet_pulls','Mushroom Knob.blend')

            with bpy.data.libraries.load(pull_path) as (data_from, data_to):
                data_to.objects = data_from.objects 
            
            for obj in data_to.objects:
                pull_obj = obj   
                props.current_door_pull_object = pull_obj
                return pull_obj
    
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

        length = self.var_input('Length', 'length')
        width = self.var_input('Width', 'width')
        thickness = self.var_input('Thickness', 'thickness')
        mirror_y = self.var_input('Mirror Y', 'mirror_y')
        hhl = self.var_prop('Handle Horizontal Location', 'hhl')
        pl = self.var_prop('Pull Location', 'pl')
        pvl_base = self.var_prop('Base Pull Vertical Location', 'pvl_base')
        pvl_tall = self.var_prop('Tall Pull Vertical Location', 'pvl_tall')
        pvl_upper = self.var_prop('Upper Pull Vertical Location', 'pvl_upper')

        pull = GeoNodeHardware()
        pull.create('Pull')
        pull.obj.parent = self.obj
        pull.obj.rotation_euler.x = math.radians(-90)
        pull.set_input("Object",self.get_pull_object())
        pull.driver_location('x', 'IF(pl==0,length-pvl_base,IF(pl==1,pvl_tall,pvl_upper))',[length,pl,pvl_base,pvl_tall,pvl_upper])
        pull.driver_location('y', 'IF(mirror_y,-width+hhl,width-hhl)',[width,hhl,mirror_y])
        pull.driver_location('z', 'thickness',[thickness])


class CabinetDrawerFront(CabinetFront):

    door_pull_location = "Base"

    def get_pull_object(self):
        props = bpy.context.scene.hb_frameless
        if props.current_door_pull_object:
            return props.current_door_pull_object
        else:
            pull_path = os.path.join(os.path.dirname(__file__),'frameless_assets','cabinet_pulls','Mushroom Knob.blend')

            with bpy.data.libraries.load(pull_path) as (data_from, data_to):
                data_to.objects = data_from.objects 
            
            for obj in data_to.objects:
                pull_obj = obj   
                props.current_door_pull_object = pull_obj
                return pull_obj
    
    def create(self,name):
        super().create(name)
        self.obj['IS_DRAWER_FRONT'] = True
        props = bpy.context.scene.hb_frameless

        self.add_property("Center Pull",'CHECKBOX',props.center_pulls_on_drawer_front)
        self.add_property('Handle Horizontal Location', 'DISTANCE', inch(2.0)) #TODO: LINK TO PROPERTY

        length = self.var_input('Length', 'length')
        width = self.var_input('Width', 'width')
        thickness = self.var_input('Thickness', 'thickness')

        pull = GeoNodeHardware()
        pull.create('Pull')
        pull.obj.parent = self.obj
        pull.obj.rotation_euler.x = math.radians(-90)
        pull.set_input("Object",self.get_pull_object())
        pull.driver_location('x', 'length/2',[length])
        pull.driver_location('y', '-width/2',[width])
        pull.driver_location('z', 'thickness',[thickness])

# =============================================================================
# CORNER CABINETS
# =============================================================================

class CornerCabinet(Cabinet):
    """Base class for corner cabinets."""
    
    corner_size = inch(36)  # Size of corner (both directions)
    
    def add_properties_corner(self):
        props = bpy.context.scene.hb_frameless
        self.add_property('Left Depth', 'DISTANCE', self.depth)
        self.add_property('Right Depth', 'DISTANCE', self.depth)


class DiagonalCornerBaseCabinet(CornerCabinet):
    """Diagonal corner base cabinet - 45° angled front."""
    
    def __init__(self):
        super().__init__()
        props = bpy.context.scene.hb_frameless
        self.corner_size = props.base_inside_corner_size
        self.height = props.base_cabinet_height
        self.depth = props.base_cabinet_depth
    
    def create(self, name="Diagonal Corner Base"):
        # TODO: Implement diagonal corner geometry
        # This requires special geometry with angled front
        self.create_cabinet(name)
        self.obj['CABINET_TYPE'] = 'BASE'
        self.obj['CORNER_TYPE'] = 'DIAGONAL'


class PieCutCornerBaseCabinet(CornerCabinet):
    """L-shaped corner base cabinet - two fronts at 90°."""
    
    def __init__(self):
        super().__init__()
        props = bpy.context.scene.hb_frameless
        self.corner_size = props.base_inside_corner_size
        self.height = props.base_cabinet_height
        self.depth = props.base_cabinet_depth
    
    def create(self, name="L-Shape Corner Base"):
        # TODO: Implement L-shape corner geometry
        self.create_cabinet(name)
        self.obj['CABINET_TYPE'] = 'BASE'
        self.obj['CORNER_TYPE'] = 'PIECUT'


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
    
    def __init__(self):
        super().__init__()
        props = bpy.context.scene.hb_frameless
        self.corner_size = props.tall_inside_corner_size
        self.height = props.tall_cabinet_height
        self.depth = props.tall_cabinet_depth
    
    def create(self, name="Diagonal Corner Tall"):
        self.create_cabinet(name)
        self.obj['CABINET_TYPE'] = 'TALL'
        self.obj['CORNER_TYPE'] = 'PIECUT'


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
    
    def __init__(self):
        super().__init__()
        props = bpy.context.scene.hb_frameless
        self.corner_size = props.upper_inside_corner_size
        self.height = props.upper_cabinet_height
        self.depth = props.upper_cabinet_depth
    
    def create(self, name="Pie Cut Corner Upper"):
        self.create_cabinet(name)
        self.obj['CABINET_TYPE'] = 'UPPER'
        self.obj['CORNER_TYPE'] = 'PIECUT'