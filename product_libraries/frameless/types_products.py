import bpy
import math
from ...hb_types import GeoNodeCage, GeoNodeCutpart
from ... import units
from ...units import inch
from .types_frameless import CabinetPart


class Product(GeoNodeCage):
    """Base class for frameless parts (non-cabinet products).
    
    Parts use IS_FRAMELESS_PRODUCT_CAGE marker so they appear in Cabinets
    selection mode but are distinguishable from actual cabinets.
    """

    width = inch(36)
    height = inch(34.5)
    depth = inch(24)

    def add_properties_common(self):
        props = bpy.context.scene.hb_frameless
        self.add_property('Material Thickness', 'DISTANCE', props.default_carcass_part_thickness)

    def create_product(self, name):
        """Create the part cage object with standard markers."""
        super().create(name)
        self.obj['IS_FRAMELESS_PRODUCT_CAGE'] = True
        self.obj['MENU_ID'] = 'HOME_BUILDER_MT_part_commands'
        self.obj.display_type = 'WIRE'

        self.set_input('Dim X', self.width)
        self.set_input('Dim Y', self.depth)
        self.set_input('Dim Z', self.height)
        self.set_input('Mirror Y', True)


class FloatingShelf(Product):
    """Floating shelf mounted on wall. Single shelf board, no carcass.
    
    Dim X = shelf width, Dim Y = shelf depth, Dim Z = shelf thickness.
    Placed like an upper cabinet (at wall cabinet location height).
    """

    def __init__(self):
        super().__init__()
        props = bpy.context.scene.hb_frameless
        self.width = props.default_cabinet_width
        self.depth = inch(12)
        self.height = inch(1.5)

    def create(self, name="Floating Shelf"):
        self.create_product(name)
        self.obj['PART_TYPE'] = 'FLOATING_SHELF'

        self.add_properties_common()

        dim_x = self.var_input('Dim X', 'dim_x')
        dim_y = self.var_input('Dim Y', 'dim_y')
        dim_z = self.var_input('Dim Z', 'dim_z')

        shelf = CabinetPart()
        shelf.create('Shelf')
        shelf.obj.parent = self.obj
        shelf.driver_input("Length", 'dim_x', [dim_x])
        shelf.driver_input("Width", 'dim_y', [dim_y])
        shelf.driver_input("Thickness", 'dim_z', [dim_z])
        shelf.set_input("Mirror Y", True)
        shelf.obj['Finish Top'] = True
        shelf.obj['Finish Bottom'] = True


class Valance(Product):
    """Decorative front-facing board, typically mounted above upper cabinets.
    
    A thin board oriented vertically on the front face.
    Dim X = width, Dim Y = thickness, Dim Z = height (drop).
    Placed like an upper cabinet.
    """

    def __init__(self):
        super().__init__()
        props = bpy.context.scene.hb_frameless
        self.width = props.default_cabinet_width
        self.depth = props.default_carcass_part_thickness
        self.height = inch(4)

    def create(self, name="Valance"):
        self.create_product(name)
        self.obj['PART_TYPE'] = 'VALANCE'

        self.add_properties_common()

        dim_x = self.var_input('Dim X', 'dim_x')
        dim_y = self.var_input('Dim Y', 'dim_y')
        dim_z = self.var_input('Dim Z', 'dim_z')

        board = CabinetPart()
        board.create('Valance Board')
        board.obj.parent = self.obj
        board.obj.rotation_euler.x = math.radians(-90)
        board.obj.location.y = -self.depth
        board.driver_input("Length", 'dim_x', [dim_x])
        board.driver_input("Width", 'dim_z', [dim_z])
        board.driver_input("Thickness", 'dim_y', [dim_y])
        board.set_input("Mirror Y", False)
        board.obj['Finish Top'] = True
        board.obj['Finish Bottom'] = True


class SupportFrame(Product):
    """Open rectangular frame (sides, top, bottom, no back).
    
    Used for supporting countertop overhangs, peninsulas, etc.
    Has left/right sides, top, and bottom but no back panel.
    """

    def __init__(self):
        super().__init__()
        props = bpy.context.scene.hb_frameless
        self.width = inch(24)
        self.height = props.base_cabinet_height
        self.depth = props.base_cabinet_depth

    def create(self, name="Support Frame"):
        self.create_product(name)
        self.obj['PART_TYPE'] = 'SUPPORT_FRAME'

        self.add_properties_common()

        dim_x = self.var_input('Dim X', 'dim_x')
        dim_y = self.var_input('Dim Y', 'dim_y')
        dim_z = self.var_input('Dim Z', 'dim_z')
        mt = self.var_prop('Material Thickness', 'mt')

        # Left side
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


class HalfWall(Product):
    """Thick solid panel acting as a pony wall / knee wall.
    
    A single thick part spanning width x depth x height.
    """

    def __init__(self):
        super().__init__()
        self.width = inch(36)
        self.height = inch(42)
        self.depth = inch(6)

    def create(self, name="Half Wall"):
        self.create_product(name)
        self.obj['PART_TYPE'] = 'HALF_WALL'

        dim_x = self.var_input('Dim X', 'dim_x')
        dim_y = self.var_input('Dim Y', 'dim_y')
        dim_z = self.var_input('Dim Z', 'dim_z')

        panel = CabinetPart()
        panel.create('Half Wall Panel')
        panel.obj.parent = self.obj
        panel.obj.rotation_euler.y = math.radians(-90)
        panel.driver_input("Length", 'dim_z', [dim_z])
        panel.driver_input("Width", 'dim_y', [dim_y])
        panel.driver_input("Thickness", 'dim_x', [dim_x])
        panel.set_input("Mirror Y", True)
        panel.set_input("Mirror Z", True)
        panel.obj['Finish Top'] = True
        panel.obj['Finish Bottom'] = True


class MiscPart(Product):
    """A single freely-resizable part. The simplest product.
    
    Uses IS_FRAMELESS_MISC_PART instead of IS_FRAMELESS_PRODUCT_CAGE
    so it does not appear in Cabinets selection mode.
    """

    def __init__(self):
        super().__init__()
        self.width = inch(24)
        self.height = inch(12)
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
        self.obj['PART_TYPE'] = 'MISC_PART'

        self.add_properties_common()

        dim_x = self.var_input('Dim X', 'dim_x')
        dim_y = self.var_input('Dim Y', 'dim_y')
        dim_z = self.var_input('Dim Z', 'dim_z')
        mt = self.var_prop('Material Thickness', 'mt')

        part = CabinetPart()
        part.create('Part')
        part.obj.parent = self.obj
        part.driver_input("Length", 'dim_x', [dim_x])
        part.driver_input("Width", 'dim_y', [dim_y])
        part.driver_input("Thickness", 'dim_z', [dim_z])
        part.set_input("Mirror Y", True)
        part.obj['Finish Top'] = True
        part.obj['Finish Bottom'] = True


class Leg(Product):
    """Vertical post / column.
    
    A narrow square-profile vertical part.
    Dim X = width, Dim Y = depth, Dim Z = height.
    """

    def __init__(self):
        super().__init__()
        props = bpy.context.scene.hb_frameless
        self.width = inch(4)
        self.height = props.base_cabinet_height
        self.depth = inch(4)

    def create(self, name="Leg"):
        self.create_product(name)
        self.obj['PART_TYPE'] = 'LEG'

        dim_x = self.var_input('Dim X', 'dim_x')
        dim_y = self.var_input('Dim Y', 'dim_y')
        dim_z = self.var_input('Dim Z', 'dim_z')

        post = CabinetPart()
        post.create('Leg Post')
        post.obj.parent = self.obj
        post.obj.rotation_euler.y = math.radians(-90)
        post.driver_input("Length", 'dim_z', [dim_z])
        post.driver_input("Width", 'dim_y', [dim_y])
        post.driver_input("Thickness", 'dim_x', [dim_x])
        post.set_input("Mirror Y", True)
        post.set_input("Mirror Z", True)
        post.obj['Finish Top'] = True
        post.obj['Finish Bottom'] = True


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
