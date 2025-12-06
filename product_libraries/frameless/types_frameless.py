import bpy
import math
import os
from ...hb_types import GeoNodeObject, GeoNodeCage, GeoNodeCutpart, GeoNodeHardware
from ...units import inch

class Cabinet(GeoNodeCage):

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

    def create(self,name):
        super().create(name)
        self.obj['IS_FRAMELESS_CABINET_CAGE'] = True
        self.obj.display_type = 'WIRE'
        
        self.set_input('Dim X', self.width)
        self.set_input('Dim Y', self.depth)
        self.set_input('Dim Z', self.height)
        self.set_input('Mirror Y', True)

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
        opening.driver_input("Dim Y", 'dim_y', [dim_y])
        opening.driver_input("Dim Z", 'dim_z-tkh-(mt*2)', [dim_z,tkh,mt])


class CabinetBay(GeoNodeCage):

    def create(self,name):
        super().create(name)
        self.obj['IS_FRAMELESS_BAY_CAGE'] = True
        self.obj.display_type = 'WIRE'


class CabinetOpening(GeoNodeCage):

    def create(self,name):
        super().create(name)
        self.obj['IS_FRAMELESS_OPENING_CAGE'] = True
        self.obj.display_type = 'WIRE'

    def add_properties_front_overlays(self):
        self.add_property("Inset Front",'CHECKBOX',False)
        self.add_property("Door to Cabinet Gap",'DISTANCE',inch(.125))    
        self.add_property("Half Overlay Top",'CHECKBOX',False)
        self.add_property("Half Overlay Bottom",'CHECKBOX',False)
        self.add_property("Half Overlay Left",'CHECKBOX',False)
        self.add_property("Half Overlay Right",'CHECKBOX',False)
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


class Doors(CabinetOpening):

    def create(self):
        super().create("Doors")
        self.obj['IS_FRAMELESS_DOORS_CAGE'] = True
        self.obj.display_type = 'WIRE'

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


class CabinetPart(GeoNodeCutpart):

    def create(self,name):
        super().create(name)
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


class CabinetDoor(CabinetPart):

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

        self.add_property("Pull Location",'COMBOBOX',0,combobox_items=["Base","Tall","Upper"])
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