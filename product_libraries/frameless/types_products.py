import bpy
import math
from ...hb_types import GeoNodeCage, GeoNodeCutpart
from ... import units
from ...units import inch
from .types_frameless import CabinetPart, CabinetSideNotched


class Product(GeoNodeCage):
    """Base class for frameless products (non-cabinet products).
    
    Products use IS_FRAMELESS_PRODUCT_CAGE marker so they appear in Cabinets
    selection mode but are distinguishable from actual cabinets.
    """

    width = inch(36)
    height = inch(34.5)
    depth = inch(24)

    def add_properties_common(self):
        props = bpy.context.scene.hb_frameless
        self.add_property('Material Thickness', 'DISTANCE', props.default_carcass_part_thickness)

    def create_product(self, name):
        """Create the product cage object with standard markers."""
        super().create(name)
        self.obj['IS_FRAMELESS_PRODUCT_CAGE'] = True
        self.obj['MENU_ID'] = 'HOME_BUILDER_MT_part_commands'
        self.obj.display_type = 'WIRE'

        self.set_input('Dim X', self.width)
        self.set_input('Dim Y', self.depth)
        self.set_input('Dim Z', self.height)
        self.set_input('Mirror Y', True)


class FloatingShelf(Product):
    """Floating shelf mounted on wall.
    
    Dim X = shelf width, Dim Y = shelf depth, Dim Z = shelf thickness.
    """

    def __init__(self):
        super().__init__()
        props = bpy.context.scene.hb_frameless
        self.width = props.default_cabinet_width
        self.depth = inch(12)
        self.height = inch(2.5)

    def add_properties(self):
        self.add_property('Finish Left', 'CHECKBOX', True)
        self.add_property('Finish Right', 'CHECKBOX', True)
        self.add_property('Include LED Route Bottom', 'CHECKBOX', False)
        self.add_property('Include LED Route Top', 'CHECKBOX', False)
        self.add_property('LED Width Top', 'DISTANCE', inch(0.5))
        self.add_property('LED Width Bottom', 'DISTANCE', inch(0.5))
        self.add_property('LED Inset Top', 'DISTANCE', inch(2))
        self.add_property('LED Inset Bottom', 'DISTANCE', inch(2))
        self.add_property('LED Route Depth', 'DISTANCE', inch(.25))

    def create(self, name="Floating Shelf"):
        self.create_product(name)
        self.obj['PART_TYPE'] = 'FLOATING_SHELF'

        self.add_properties_common()
        self.add_properties()

        dim_x = self.var_input('Dim X', 'dim_x')
        dim_y = self.var_input('Dim Y', 'dim_y')
        dim_z = self.var_input('Dim Z', 'dim_z')
        mt = self.var_prop('Material Thickness', 'mt')
        fl = self.var_prop('Finish Left', 'fl')
        fr = self.var_prop('Finish Right', 'fr')
        led_rb = self.var_prop('Include LED Route Bottom', 'led_rb')
        led_rt = self.var_prop('Include LED Route Top', 'led_rt')
        led_wt = self.var_prop('LED Width Top', 'led_wt')
        led_wb = self.var_prop('LED Width Bottom', 'led_wb')
        led_it = self.var_prop('LED Inset Top', 'led_it')
        led_ib = self.var_prop('LED Inset Bottom', 'led_ib')
        led_depth = self.var_prop('LED Route Depth', 'led_depth')

        front = CabinetPart()
        front.create('Front')
        front.obj.parent = self.obj
        front.obj.rotation_euler.x = math.radians(-90)
        front.driver_location('y', '-dim_y', [dim_y])
        front.driver_input("Length", 'dim_x', [dim_x])
        front.driver_input("Width", 'dim_z', [dim_z])
        front.driver_input("Thickness", 'mt', [mt])
        front.set_input("Mirror Y", True)

        top = CabinetPart()
        top.create('Top')
        top.obj.parent = self.obj
        top.driver_location('x', 'IF(fl,mt,0)',[mt,fl])
        top.driver_location('y', '-dim_y+mt', [dim_y, mt])
        top.driver_location('z', 'dim_z', [dim_z, mt])
        top.driver_input("Length", 'dim_x-IF(fl,mt,0)-IF(fr,mt,0)', [dim_x,fl,fr,mt])
        top.driver_input("Width", 'dim_y-mt', [dim_y,mt])
        top.driver_input("Thickness", 'mt', [mt])
        top.set_input("Mirror Z", True)

        led_route = top.add_part_modifier('CPM_CUTOUT','LED Route')
        led_route.driver_input('X','-.01',[])
        led_route.driver_input('Y','led_ib',[led_ib])
        led_route.driver_input('End X','dim_x',[dim_x])
        led_route.driver_input('End Y','led_ib+led_wb',[led_ib,led_wb])        
        led_route.driver_input('Route Depth','led_depth',[led_depth])
        led_route.set_input('Flip Z',True)

        bottom = CabinetPart()
        bottom.create('Bottom')
        bottom.obj.parent = self.obj
        bottom.driver_location('x', 'IF(fl,mt,0)',[mt,fl])
        bottom.driver_location('y', '-dim_y+mt', [dim_y, mt])
        bottom.driver_input("Length", 'dim_x-IF(fl,mt,0)-IF(fr,mt,0)', [dim_x,fl,fr,mt])
        bottom.driver_input("Width", 'dim_y-mt', [dim_y,mt])
        bottom.driver_input("Thickness", 'mt', [mt])

        led_route = bottom.add_part_modifier('CPM_CUTOUT','LED Route')
        led_route.driver_input('X','-.01',[])
        led_route.driver_input('Y','led_it',[led_it])
        led_route.driver_input('End X','dim_x',[dim_x])
        led_route.driver_input('End Y','led_it+led_wt',[led_it,led_wt])        
        led_route.driver_input('Route Depth','led_depth',[led_depth])
        led_route.set_input('Flip Z',False)

        l_panel = CabinetPart()
        l_panel.create('Left Panel')
        l_panel.obj.parent = self.obj
        l_panel.obj.rotation_euler.x = math.radians(-90)
        l_panel.obj.rotation_euler.z = math.radians(90)
        l_panel.driver_input("Length", 'dim_y-mt', [dim_y,mt])
        l_panel.driver_input("Width", 'dim_z', [dim_z])
        l_panel.driver_input("Thickness", 'mt', [mt])
        l_panel.driver_hide('IF(fl,False,True)', [fl])
        l_panel.set_input("Mirror X", True)
        l_panel.set_input("Mirror Y", True)
        l_panel.set_input("Mirror Z", True)

        r_panel = CabinetPart()
        r_panel.create('Right Panel')
        r_panel.obj.parent = self.obj
        r_panel.obj.rotation_euler.x = math.radians(-90)
        r_panel.obj.rotation_euler.z = math.radians(90)
        r_panel.driver_location('x', 'dim_x', [dim_x])
        r_panel.driver_input("Length", 'dim_y-mt', [dim_y,mt])
        r_panel.driver_input("Width", 'dim_z', [dim_z])
        r_panel.driver_input("Thickness", 'mt', [mt])
        r_panel.driver_hide('IF(fr,False,True)', [fr])
        r_panel.set_input("Mirror X", True)
        r_panel.set_input("Mirror Y", True)


class Valance(Product):
    """Decorative front-facing board.
    
    A thin board oriented vertically on the front face.
    Dim X = width, Dim Y = depth, Dim Z = height.
    Placed like an upper cabinet.
    """

    def __init__(self):
        super().__init__()
        props = bpy.context.scene.hb_frameless
        self.width = props.default_cabinet_width
        self.depth = props.upper_cabinet_depth
        self.height = inch(4)

    def add_properties(self):
        self.add_property('Top Scribe Amount', 'DISTANCE', inch(.5))
        self.add_property('Finish Left', 'CHECKBOX', False)
        self.add_property('Finish Right', 'CHECKBOX', False)
        self.add_property('Remove Cover', 'CHECKBOX', False)
        self.add_property('Flush Bottom', 'CHECKBOX', False)

    def create(self, name="Valance"):
        self.create_product(name)
        self.obj['PART_TYPE'] = 'VALANCE'

        self.add_properties_common()
        self.add_properties()

        dim_x = self.var_input('Dim X', 'dim_x')
        dim_y = self.var_input('Dim Y', 'dim_y')
        dim_z = self.var_input('Dim Z', 'dim_z')
        mt = self.var_prop('Material Thickness', 'mt')
        tsa = self.var_prop('Top Scribe Amount', 'tsa')
        fl = self.var_prop('Finish Left', 'fl')
        fr = self.var_prop('Finish Right', 'fr')
        rc = self.var_prop('Remove Cover', 'rc')
        fb = self.var_prop('Flush Bottom', 'fb')

        valance = CabinetPart()
        valance.create('Valance Board')
        valance.obj.parent = self.obj
        valance.obj.rotation_euler.x = math.radians(-90)
        valance.driver_location('y', '-dim_y', [dim_y])
        valance.driver_input("Length", 'dim_x', [dim_x])
        valance.driver_input("Width", 'dim_z', [dim_z])
        valance.driver_input("Thickness", 'mt', [mt])
        valance.set_input("Mirror Y", True)
        valance.obj['Finish Top'] = True
        valance.obj['Finish Bottom'] = True

        cover = CabinetPart()
        cover.create('Cover')
        cover.obj.parent = self.obj
        cover.driver_location('x', 'IF(fl,mt,0)',[mt,fl])
        cover.driver_location('y', '-dim_y+mt', [dim_y, mt])
        cover.driver_location('z', 'IF(fb,0,dim_z-tsa-mt)', [fb, dim_z, mt, tsa])
        cover.driver_input("Length", 'dim_x-IF(fl,mt,0)-IF(fr,mt,0)', [dim_x,fl,fr,mt])
        cover.driver_input("Width", 'dim_y-mt', [dim_y,mt])
        cover.driver_input("Thickness", 'mt', [mt])
        cover.driver_hide('IF(rc,True,False)', [rc])
        cover.obj['Finish Top'] = False
        cover.obj['Finish Bottom'] = True

        l_panel = CabinetPart()
        l_panel.create('Left Panel')
        l_panel.obj.parent = self.obj
        l_panel.obj.rotation_euler.x = math.radians(-90)
        l_panel.obj.rotation_euler.z = math.radians(90)
        l_panel.driver_input("Length", 'dim_y-mt', [dim_y,mt])
        l_panel.driver_input("Width", 'dim_z', [dim_z])
        l_panel.driver_input("Thickness", 'mt', [mt])
        l_panel.driver_hide('IF(fl,False,True)', [fl])
        l_panel.set_input("Mirror X", True)
        l_panel.set_input("Mirror Y", True)
        l_panel.set_input("Mirror Z", True)
        l_panel.obj['Finish Top'] = True
        l_panel.obj['Finish Bottom'] = True

        r_panel = CabinetPart()
        r_panel.create('Right Panel')
        r_panel.obj.parent = self.obj
        r_panel.obj.rotation_euler.x = math.radians(-90)
        r_panel.obj.rotation_euler.z = math.radians(90)
        r_panel.driver_location('x', 'dim_x', [dim_x])
        r_panel.driver_input("Length", 'dim_y-mt', [dim_y,mt])
        r_panel.driver_input("Width", 'dim_z', [dim_z])
        r_panel.driver_input("Thickness", 'mt', [mt])
        r_panel.driver_hide('IF(fr,False,True)', [fr])
        r_panel.set_input("Mirror X", True)
        r_panel.set_input("Mirror Y", True)
        r_panel.obj['Finish Top'] = True
        r_panel.obj['Finish Bottom'] = True


class SupportFrame(Product):
    """Open rectangular frame (sides, top, bottom).
    
    Used for supporting countertop overhangs, peninsulas, etc.
    Has configurable legs at each corner with inset or wrapped options.
    """

    def __init__(self):
        super().__init__()
        props = bpy.context.scene.hb_frameless
        self.width = inch(60)
        self.height = inch(4)
        self.depth = inch(24)

    def add_properties(self):
        self.add_property('Support Spacing', 'DISTANCE', inch(16))
        self.add_property('Front Left Leg', 'CHECKBOX', True)
        self.add_property('Front Right Leg', 'CHECKBOX', True)
        self.add_property('Back Left Leg', 'CHECKBOX', True)
        self.add_property('Back Right Leg', 'CHECKBOX', True)
        self.add_property('Leg Width', 'DISTANCE', inch(3.5))
        self.add_property('Leg Depth', 'DISTANCE', inch(3.5))
        self.add_property('Leg Height', 'DISTANCE', inch(34.5))
        self.add_property('Front Left Leg Type', 'COMBOBOX', 0, combobox_items=["Inset", "Wrapped"])
        self.add_property('Front Right Leg Type', 'COMBOBOX', 0, combobox_items=["Inset", "Wrapped"])
        self.add_property('Back Left Leg Type', 'COMBOBOX', 0, combobox_items=["Inset", "Wrapped"])
        self.add_property('Back Right Leg Type', 'COMBOBOX', 0, combobox_items=["Inset", "Wrapped"])

    def create(self, name="Support Frame"):
        self.create_product(name)
        self.obj['PART_TYPE'] = 'SUPPORT_FRAME'

        self.add_properties_common()
        self.add_properties()

        dim_x = self.var_input('Dim X', 'dim_x')
        dim_y = self.var_input('Dim Y', 'dim_y')
        dim_z = self.var_input('Dim Z', 'dim_z')
        mt = self.var_prop('Material Thickness', 'mt')
        ss = self.var_prop('Support Spacing', 'ss')
        fll = self.var_prop('Front Left Leg', 'fll')
        frl = self.var_prop('Front Right Leg', 'frl')
        bll = self.var_prop('Back Left Leg', 'bll')
        brl = self.var_prop('Back Right Leg', 'brl')
        lw = self.var_prop('Leg Width', 'lw')
        ld = self.var_prop('Leg Depth', 'ld')
        lh = self.var_prop('Leg Height', 'lh')
        fllt = self.var_prop('Front Left Leg Type', 'fllt')
        frlt = self.var_prop('Front Right Leg Type', 'frlt')
        bllt = self.var_prop('Back Left Leg Type', 'bllt')
        brlt = self.var_prop('Back Right Leg Type', 'brlt')

        l_panel = CabinetPart()
        l_panel.create('Left Panel')
        l_panel.obj.parent = self.obj
        l_panel.obj.rotation_euler.x = math.radians(-90)
        l_panel.obj.rotation_euler.z = math.radians(90)
        l_panel.driver_location('y', '-IF(AND(bll,bllt==1),ld,mt)', [mt, bll, bllt, ld])
        l_panel.driver_input("Length", 'dim_y-IF(AND(fll,fllt==1),ld,mt)-IF(AND(bll,bllt==1),ld,mt)', [dim_y, mt, fll, fllt, ld, bll, bllt])
        l_panel.driver_input("Width", 'dim_z', [dim_z])
        l_panel.driver_input("Thickness", 'mt', [mt])
        l_panel.set_input("Mirror X", True)
        l_panel.set_input("Mirror Y", True)
        l_panel.set_input("Mirror Z", True)

        r_panel = CabinetPart()
        r_panel.create('Right Panel')
        r_panel.obj.parent = self.obj
        r_panel.obj.rotation_euler.x = math.radians(-90)
        r_panel.obj.rotation_euler.z = math.radians(90)
        r_panel.driver_location('x', 'dim_x', [dim_x])
        r_panel.driver_location('y', '-IF(AND(brl,brlt==1),ld,mt)', [mt, brl, brlt, ld])
        r_panel.driver_input("Length", 'dim_y-IF(AND(frl,frlt==1),ld,mt)-IF(AND(brl,brlt==1),ld,mt)', [dim_y, mt, frl, frlt, ld, brl, brlt])
        r_panel.driver_input("Width", 'dim_z', [dim_z])
        r_panel.driver_input("Thickness", 'mt', [mt])
        r_panel.set_input("Mirror X", True)
        r_panel.set_input("Mirror Y", True)

        front = CabinetPart()
        front.create('Front Panel')
        front.obj.parent = self.obj
        front.obj.rotation_euler.x = math.radians(90)
        front.driver_location('x', 'IF(AND(fll,fllt==1),lw,0)', [fll, fllt, lw])
        front.driver_location('y', '-dim_y', [dim_y])
        front.driver_input("Length", 'dim_x-IF(AND(fll,fllt==1),lw,0)-IF(AND(frl,frlt==1),lw,0)', [dim_x, fll, fllt, lw, frl, frlt])
        front.driver_input("Width", 'dim_z', [dim_z])
        front.driver_input("Thickness", 'mt', [mt])
        front.set_input("Mirror Z", True)

        back = CabinetPart()
        back.create('Back Panel')
        back.obj.parent = self.obj
        back.obj.rotation_euler.x = math.radians(90)
        back.driver_location('x', 'IF(AND(bll,bllt==1),lw,0)', [bll, bllt, lw])
        back.driver_input("Length", 'dim_x-IF(AND(bll,bllt==1),lw,0)-IF(AND(brl,brlt==1),lw,0)', [dim_x, bll, bllt, lw, brl, brlt])
        back.driver_input("Width", 'dim_z', [dim_z])
        back.driver_input("Thickness", 'mt', [mt])

        # Support with array modifier
        support = CabinetPart()
        support.create('Support')
        support.obj.parent = self.obj
        support.obj.rotation_euler.x = math.radians(-90)
        support.obj.rotation_euler.z = math.radians(90)
        support.driver_location('x', 'ss', [ss])
        support.driver_location('y', '-mt', [mt])
        support.driver_input("Length", 'dim_y-mt*2', [dim_y, mt])
        support.driver_input("Width", 'dim_z', [dim_z])
        support.driver_input("Thickness", 'mt', [mt])
        support.set_input("Mirror X", True)
        support.set_input("Mirror Y", True)
        support.set_input("Mirror Z", True)
        support.obj['Finish Top'] = False
        support.obj['Finish Bottom'] = False
        array_mod = support.obj.modifiers.new('Qty', 'ARRAY')
        array_mod.count = 1
        array_mod.use_relative_offset = False
        array_mod.use_constant_offset = True
        array_mod.constant_offset_displace = (0, 0, 0)
        support.obj.home_builder.add_driver(
            'modifiers["' + array_mod.name + '"].count', -1,
            'IF(ss>0,floor((dim_x-mt*2-ss)/ss)+1,0)',
            [ss, dim_x, mt])
        support.obj.home_builder.add_driver(
            'modifiers["' + array_mod.name + '"].constant_offset_displace', 2,
            '-ss', [ss])

        # ---- LEGS ----

        # Front Left Leg
        fl_leg = CabinetPart()
        fl_leg.create('Front Left Leg')
        fl_leg.obj.parent = self.obj
        fl_leg.obj.rotation_euler.y = math.radians(-90)
        fl_leg.obj.rotation_euler.z = math.radians(-90)
        fl_leg.driver_location('x', 'IF(fllt==0,mt,0)', [fllt, mt])
        fl_leg.driver_location('y', 'IF(fllt==0,-(dim_y-mt),-dim_y)', [fllt, dim_y, mt, ld])
        fl_leg.driver_location('z', 'dim_z', [dim_z])
        fl_leg.driver_input("Length", 'lh', [lh])
        fl_leg.driver_input("Width", 'lw', [lw])
        fl_leg.driver_input("Thickness", 'ld', [ld])
        fl_leg.driver_hide('IF(fll,False,True)', [fll])
        fl_leg.set_input("Mirror X", True)
        fl_leg.obj['Finish Top'] = True
        fl_leg.obj['Finish Bottom'] = True

        # Front Right Leg
        fr_leg = CabinetPart()
        fr_leg.create('Front Right Leg')
        fr_leg.obj.parent = self.obj
        fr_leg.obj.rotation_euler.y = math.radians(-90)
        fr_leg.driver_location('x', 'IF(frlt==0,dim_x-mt,dim_x)', [frlt, dim_x, mt, lw])
        fr_leg.driver_location('y', 'IF(frlt==0,-(dim_y-mt),-dim_y)', [frlt, dim_y, mt, ld])
        fr_leg.driver_location('z', 'dim_z', [dim_z])
        fr_leg.driver_input("Length", 'lh', [lh])
        fr_leg.driver_input("Width", 'ld', [ld])
        fr_leg.driver_input("Thickness", 'lw', [lw])
        fr_leg.driver_hide('IF(frl,False,True)', [frl])
        fr_leg.set_input("Mirror X", True)
        fr_leg.obj['Finish Top'] = True
        fr_leg.obj['Finish Bottom'] = True

        # Back Left Leg
        bl_leg = CabinetPart()
        bl_leg.create('Back Left Leg')
        bl_leg.obj.parent = self.obj
        bl_leg.obj.rotation_euler.y = math.radians(-90)
        bl_leg.obj.rotation_euler.z = math.radians(180)
        bl_leg.driver_location('x', 'IF(bllt==0,mt,0)', [bllt, mt])
        bl_leg.driver_location('y', 'IF(bllt==0,-(mt),0)', [bllt, mt, ld])
        bl_leg.driver_location('z', 'dim_z', [dim_z])
        bl_leg.driver_input("Length", 'lh', [lh])
        bl_leg.driver_input("Width", 'ld', [ld])
        bl_leg.driver_input("Thickness", 'lw', [lw])
        bl_leg.driver_hide('IF(bll,False,True)', [bll])
        bl_leg.set_input("Mirror X", True)
        bl_leg.obj['Finish Top'] = True
        bl_leg.obj['Finish Bottom'] = True

        # Back Right Leg
        br_leg = CabinetPart()
        br_leg.create('Back Right Leg')
        br_leg.obj.parent = self.obj
        br_leg.obj.rotation_euler.y = math.radians(-90)
        br_leg.obj.rotation_euler.z = math.radians(90)
        br_leg.driver_location('x', 'IF(brlt==0,dim_x-mt,dim_x)', [brlt, dim_x, mt, lw])
        br_leg.driver_location('y', 'IF(brlt==0,-(mt),0)', [brlt, mt, ld])
        br_leg.driver_location('z', 'dim_z', [dim_z])
        br_leg.driver_input("Length", 'lh', [lh])
        br_leg.driver_input("Width", 'lw', [lw])
        br_leg.driver_input("Thickness", 'ld', [ld])
        br_leg.driver_hide('IF(brl,False,True)', [brl])
        br_leg.set_input("Mirror X", True)
        br_leg.obj['Finish Top'] = True
        br_leg.obj['Finish Bottom'] = True

class HalfWall(Product):
    """Pony wall / knee wall.
    
    Constructed with studs, skins, and optional finished end caps.
    """

    def __init__(self):
        super().__init__()
        self.width = inch(36)
        self.height = inch(42)
        self.depth = inch(6)

    def add_properties(self):
        self.add_property('Stud Thickness', 'DISTANCE', inch(.75))
        self.add_property('Skin Thickness', 'DISTANCE', inch(0.25))
        self.add_property('Stud Spacing', 'DISTANCE', inch(16))
        self.add_property('End Stud From Edge', 'DISTANCE', inch(1.5))
        self.add_property('Left End Cap', 'CHECKBOX', False)
        self.add_property('Right End Cap', 'CHECKBOX', False)
        self.add_property('Finished End Setback', 'DISTANCE', inch(0))
        self.add_property('Left Finished Revel', 'DISTANCE', inch(0))
        self.add_property('Right Finished Revel', 'DISTANCE', inch(0))
        self.add_property('Finish Front', 'CHECKBOX', True)
        self.add_property('Finish Back', 'CHECKBOX', False)

    def create(self, name="Half Wall"):
        self.create_product(name)
        self.obj['PART_TYPE'] = 'HALF_WALL'

        self.add_properties_common()
        self.add_properties()

        dim_x = self.var_input('Dim X', 'dim_x')
        dim_y = self.var_input('Dim Y', 'dim_y')
        dim_z = self.var_input('Dim Z', 'dim_z')
        mt = self.var_prop('Material Thickness', 'mt')
        st = self.var_prop('Stud Thickness', 'st')
        skt = self.var_prop('Skin Thickness', 'skt')
        ssp = self.var_prop('Stud Spacing', 'ssp')
        esfe = self.var_prop('End Stud From Edge', 'esfe')
        lec = self.var_prop('Left End Cap', 'lec')
        rec = self.var_prop('Right End Cap', 'rec')
        fes = self.var_prop('Finished End Setback', 'fes')
        lfr = self.var_prop('Left Finished Revel', 'lfr')
        rfr = self.var_prop('Right Finished Revel', 'rfr')
        ff = self.var_prop('Finish Front', 'ff')
        fba = self.var_prop('Finish Back', 'fba')

        left_end = CabinetPart()
        left_end.create('Left End')
        left_end.obj.parent = self.obj
        left_end.obj.rotation_euler.x = math.radians(90)
        left_end.obj.rotation_euler.y = math.radians(-90)
        left_end.obj.rotation_euler.z = math.radians(-90)
        left_end.driver_input("Length", 'dim_z', [dim_z])
        left_end.driver_input("Width", 'dim_y', [dim_y])
        left_end.driver_input("Thickness", 'mt', [mt])
        left_end.set_input("Mirror Y", True)
        left_end.set_input("Mirror Z", True)
        left_end.obj['Finish Top'] = True
        left_end.obj['Finish Bottom'] = True

        right_end = CabinetPart()
        right_end.create('Right End')
        right_end.obj.parent = self.obj
        right_end.obj.rotation_euler.x = math.radians(90)
        right_end.obj.rotation_euler.y = math.radians(-90)
        right_end.obj.rotation_euler.z = math.radians(-90)
        right_end.driver_location('x', 'dim_x', [dim_x])
        right_end.driver_input("Length", 'dim_z', [dim_z])
        right_end.driver_input("Width", 'dim_y', [dim_y])
        right_end.driver_input("Thickness", 'mt', [mt])
        right_end.set_input("Mirror Y", True)
        right_end.obj['Finish Top'] = True
        right_end.obj['Finish Bottom'] = True

        top = CabinetPart()
        top.create('Right End')
        top.obj.parent = self.obj
        top.driver_location('x', 'mt', [mt])
        top.driver_location('y', '-st', [st])
        top.driver_location('z', 'dim_z', [dim_z])
        top.driver_input("Length", 'dim_x-mt-mt', [dim_x,mt])
        top.driver_input("Width", 'dim_y-st*2', [dim_y,st])
        top.driver_input("Thickness", 'mt', [mt])
        top.set_input("Mirror Y", True)
        top.set_input("Mirror Z", True)
        top.obj['Finish Top'] = False
        top.obj['Finish Bottom'] = False

        bottom = CabinetPart()
        bottom.create('Right End')
        bottom.obj.parent = self.obj
        bottom.driver_location('x', 'mt', [mt])
        bottom.driver_location('y', '-st', [st])
        bottom.driver_input("Length", 'dim_x-mt-mt', [dim_x,mt])
        bottom.driver_input("Width", 'dim_y-st*2', [dim_y,st])
        bottom.driver_input("Thickness", 'mt', [mt])
        bottom.set_input("Mirror Y", True)
        bottom.obj['Finish Top'] = False
        bottom.obj['Finish Bottom'] = False

        front_skin = CabinetPart()
        front_skin.create('Front Skin')
        front_skin.obj.parent = self.obj
        front_skin.obj.rotation_euler.x = math.radians(90)
        front_skin.driver_location('x', 'mt', [mt])
        front_skin.driver_location('y', '-dim_y', [dim_y])
        front_skin.driver_input("Length", 'dim_x-mt-mt', [dim_x,mt])
        front_skin.driver_input("Width", 'dim_z', [dim_z])
        front_skin.driver_input("Thickness", 'st', [st])
        front_skin.set_input("Mirror Z", True)
        front_skin.obj['Finish Top'] = True
        front_skin.obj['Finish Bottom'] = True

        back_skin = CabinetPart()
        back_skin.create('Back Skin')
        back_skin.obj.parent = self.obj
        back_skin.obj.rotation_euler.x = math.radians(90)
        back_skin.driver_location('x', 'mt', [mt])
        back_skin.driver_input("Length", 'dim_x-mt-mt', [dim_x,mt])
        back_skin.driver_input("Width", 'dim_z', [dim_z])
        back_skin.driver_input("Thickness", 'st', [st])
        back_skin.obj['Finish Top'] = True
        back_skin.obj['Finish Bottom'] = True

        # Stud with array modifier
        stud = CabinetPart()
        stud.create('Stud')
        stud.obj.parent = self.obj
        stud.obj.rotation_euler.x = math.radians(90)
        stud.obj.rotation_euler.y = math.radians(-90)
        stud.obj.rotation_euler.z = math.radians(-90)
        stud.driver_location('x', 'mt+esfe', [mt, esfe])
        stud.driver_location('y', '-st', [st])
        stud.driver_location('z', 'mt', [mt])
        stud.driver_input("Length", 'dim_z-mt*2', [dim_z, mt])
        stud.driver_input("Width", 'dim_y-st*2', [dim_y, st])
        stud.driver_input("Thickness", 'st', [st])
        stud.set_input("Mirror Y", True)
        stud.set_input("Mirror Z", True)
        stud.obj['Finish Top'] = False
        stud.obj['Finish Bottom'] = False
        array_mod = stud.obj.modifiers.new('Qty', 'ARRAY')
        array_mod.count = 1
        array_mod.use_relative_offset = False
        array_mod.use_constant_offset = True
        array_mod.constant_offset_displace = (0, 0, 0)
        stud.obj.home_builder.add_driver(
            'modifiers["' + array_mod.name + '"].count', -1,
            'IF(ssp>0,floor((dim_x-mt*2-esfe*2)/ssp)+1,1)',
            [ssp, dim_x, mt, esfe])
        stud.obj.home_builder.add_driver(
            'modifiers["' + array_mod.name + '"].constant_offset_displace', 2,
            '-ssp', [ssp])


class MiscPart(Product):
    """A single freely-resizable part. The simplest product.
    
    Uses IS_FRAMELESS_MISC_PART instead of IS_FRAMELESS_PRODUCT_CAGE
    so it does not appear in Cabinets selection mode.
    """

    def __init__(self):
        super().__init__()
        props = bpy.context.scene.hb_frameless
        self.width = inch(24)
        self.height =  props.default_carcass_part_thickness
        self.depth = inch(12)

    def create_product(self, name):
        """Override to use MISC marker instead of PRODUCT marker."""
        GeoNodeCage.create(self, name)
        self.obj['IS_FRAMELESS_MISC_PART'] = True
        self.obj['MENU_ID'] = 'HOME_BUILDER_MT_part_commands'
        self.obj.display_type = 'WIRE'

        self.set_input('Dim X', self.width)
        self.set_input('Dim Y', self.depth)
        self.set_input('Dim Z', self.height)
        self.set_input('Mirror Y', True)

    def create(self, name="Misc Part"):
        self.create_product(name)
        # self.obj['PART_TYPE'] = 'MISC_PART'

        # self.add_properties_common()

        # dim_x = self.var_input('Dim X', 'dim_x')
        # dim_y = self.var_input('Dim Y', 'dim_y')
        # dim_z = self.var_input('Dim Z', 'dim_z')
        # mt = self.var_prop('Material Thickness', 'mt')

        # part = CabinetPart()
        # part.create('Part')
        # part.obj.parent = self.obj
        # part.driver_input("Length", 'dim_x', [dim_x])
        # part.driver_input("Width", 'dim_y', [dim_y])
        # part.driver_input("Thickness", 'dim_z', [dim_z])
        # part.set_input("Mirror Y", True)
        # part.obj['Finish Top'] = True
        # part.obj['Finish Bottom'] = True


class Leg(Product):
    """Vertical Leg.
    
    A narrow square-profile vertical part with toe kick and panel options.
    Dim X = width, Dim Y = depth, Dim Z = height.
    """

    def __init__(self):
        super().__init__()
        props = bpy.context.scene.hb_frameless
        self.width = inch(2)
        self.height = props.base_cabinet_height
        self.depth = props.base_cabinet_depth

    def add_properties(self):
        props = bpy.context.scene.hb_frameless
        self.add_property('Toe Kick Height', 'DISTANCE', props.default_toe_kick_height)
        self.add_property('Toe Kick Setback', 'DISTANCE', props.default_toe_kick_setback)
        #Override Depth == 0 means full depth
        self.add_property('Override Left Panel Depth', 'DISTANCE', 0.0)
        self.add_property('Override Right Panel Depth', 'DISTANCE', 0.0)
        self.add_property('Only Include Filler', 'CHECKBOX', False)
        self.add_property('Finish Type', 'COMBOBOX', 0, combobox_items=["Left", "Right", "Both"])

    def create(self, name="Leg"):
        self.create_product(name)
        self.obj['PART_TYPE'] = 'LEG'

        self.add_properties_common()
        self.add_properties()

        dim_x = self.var_input('Dim X', 'dim_x')
        dim_y = self.var_input('Dim Y', 'dim_y')
        dim_z = self.var_input('Dim Z', 'dim_z')
        mt = self.var_prop('Material Thickness', 'mt')
        tkh = self.var_prop('Toe Kick Height', 'tkh')
        tks = self.var_prop('Toe Kick Setback', 'tks')
        olpd = self.var_prop('Override Left Panel Depth', 'olpd')
        orpd = self.var_prop('Override Right Panel Depth', 'orpd')
        oif = self.var_prop('Only Include Filler', 'oif')
        ft = self.var_prop('Finish Type', 'ft')

        front = CabinetPart()
        front.create('Front')
        front.obj.parent = self.obj
        front.obj.rotation_euler.x = math.radians(-90)
        front.obj.rotation_euler.y = math.radians(-90)
        front.driver_location("z", 'tkh', [tkh])
        front.driver_location("y", '-dim_y', [dim_y])
        front.driver_input("Length", 'dim_z-tkh', [dim_z,tkh])
        front.driver_input("Width", 'dim_x', [dim_x])
        front.driver_input("Thickness", 'mt', [mt])

        tk_front = CabinetPart()
        tk_front.create('Toe Kick Front')
        tk_front.obj.parent = self.obj
        tk_front.obj.rotation_euler.x = math.radians(-90)
        tk_front.obj.rotation_euler.y = math.radians(-90)
        tk_front.driver_location("y", '-dim_y+tks', [dim_y,tks])
        tk_front.driver_input("Length", 'tkh', [tkh])
        tk_front.driver_input("Width", 'dim_x', [dim_x])
        tk_front.driver_input("Thickness", 'mt', [mt])
        tk_front.driver_hide('IF(tkh==0,True,False)', [tkh])

        left_panel = CabinetSideNotched()
        left_panel.create('Left Panel',tkh,tks,mt)
        left_panel.obj.parent = self.obj
        left_panel.obj.rotation_euler.y = math.radians(-90)
        left_panel.driver_location("y", 'IF(olpd==0,0,-dim_y+mt+olpd)', [olpd,dim_y,mt])
        left_panel.driver_input("Length", 'dim_z', [dim_z])
        left_panel.driver_input("Width", 'IF(olpd==0,dim_y-mt,olpd)', [olpd,dim_y,mt])
        left_panel.driver_input("Thickness", 'mt', [mt])
        left_panel.set_input('Mirror Z', True)
        left_panel.set_input('Mirror Y', True)
        left_panel.driver_hide('IF(oif,True,IF(OR(ft==0,ft==2),False,True))', [oif,ft])

        right_panel = CabinetSideNotched()
        right_panel.create('Right Panel',tkh,tks,mt)
        right_panel.obj.parent = self.obj
        right_panel.obj.rotation_euler.y = math.radians(-90)
        right_panel.driver_location("x", 'dim_x', [dim_x])
        right_panel.driver_location("y", 'IF(orpd==0,0,-dim_y+mt+orpd)', [orpd,dim_y,mt])
        right_panel.driver_input("Length", 'dim_z', [dim_z])
        right_panel.driver_input("Width", 'IF(orpd==0,dim_y-mt,orpd)', [orpd,dim_y,mt])
        right_panel.driver_input("Thickness", 'mt', [mt])
        right_panel.driver_hide('IF(oif,True,IF(OR(ft==1,ft==2),False,True))', [oif,ft])
        right_panel.set_input('Mirror Y', True)


class Panel(Product):
    """Single flat vertical panel (filler, end panel, etc).
    
    A thin vertical board. 
    Dim X = width, Dim Y = thickness, Dim Z = height.
    """

    def __init__(self):
        super().__init__()
        props = bpy.context.scene.hb_frameless
        self.width = inch(3)
        self.height = props.base_cabinet_height
        self.depth = props.default_carcass_part_thickness

    def create(self, name="Panel"):
        self.create_product(name)
        self.obj['PART_TYPE'] = 'PANEL'

        dim_x = self.var_input('Dim X', 'dim_x')
        dim_y = self.var_input('Dim Y', 'dim_y')
        dim_z = self.var_input('Dim Z', 'dim_z')

        panel = CabinetPart()
        panel.create('Panel Board')
        panel.obj.parent = self.obj
        panel.obj.rotation_euler.y = math.radians(-90)
        panel.driver_input("Length", 'dim_z', [dim_z])
        panel.driver_input("Width", 'dim_y', [dim_y])
        panel.driver_input("Thickness", 'dim_x', [dim_x])
        panel.set_input("Mirror Y", True)
        panel.set_input("Mirror Z", True)
        panel.obj['Finish Top'] = True
        panel.obj['Finish Bottom'] = True
