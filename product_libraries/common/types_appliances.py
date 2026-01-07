import bpy
import math
from ...hb_types import GeoNodeObject, GeoNodeCage, GeoNodeCutpart
from ...hb_details import GeoNodeText
from ... import units
from ...units import inch


class Appliance(GeoNodeCage):
    """Base class for all appliances."""
    
    width = inch(30)
    height = inch(36)
    depth = inch(24)
    
    def create_appliance(self, name, appliance_type):
        """Create an appliance with standard setup.
        
        Args:
            name: Display name for the appliance
            appliance_type: Type identifier (RANGE, DISHWASHER, REFRIGERATOR, etc.)
        """
        super().create(name)
        self.obj['IS_APPLIANCE'] = True
        self.obj['APPLIANCE_TYPE'] = appliance_type
        self.obj['MENU_ID'] = 'HOME_BUILDER_MT_appliance_commands'
        self.obj.display_type = 'WIRE'
        
        self.set_input('Dim X', self.width)
        self.set_input('Dim Y', self.depth)
        self.set_input('Dim Z', self.height)
        self.set_input('Mirror Y', True)

        dim_x = self.var_input('Dim X', 'dim_x')
        dim_y = self.var_input('Dim Y', 'dim_y')
        dim_z = self.var_input('Dim Z', 'dim_z')

        props = bpy.context.scene.home_builder

        appliance_text = GeoNodeText()
        appliance_text.create('Appliance Text', appliance_type, props.annotation_text_size)
        appliance_text.obj.parent = self.obj
        appliance_text.obj.rotation_euler.x = math.radians(90)
        appliance_text.driver_location("x", 'dim_x/2', [dim_x])
        appliance_text.driver_location("y", '-dim_y', [dim_y])
        appliance_text.driver_location("z", 'dim_z/2', [dim_z])
        appliance_text.set_alignment('CENTER', 'CENTER')


class Range(Appliance):
    """Freestanding range/stove appliance."""
    
    width = inch(30)
    height = inch(36)
    depth = inch(25)
    
    def create(self, name="Range"):
        self.create_appliance(name, 'RANGE')
        
        # Add range-specific properties
        self.add_property('Has Hood', 'CHECKBOX', False)
        self.add_property('Hood Height', 'DISTANCE', inch(24))


class Cooktop(Appliance):
    """Built-in cooktop for counter installation."""
    
    width = inch(30)
    height = inch(4)
    depth = inch(21)
    
    def create(self, name="Cooktop"):
        self.create_appliance(name, 'COOKTOP')
        self.obj['IS_COUNTERTOP_APPLIANCE'] = True


class WallOven(Appliance):
    """Wall-mounted oven."""
    
    width = inch(30)
    height = inch(29)
    depth = inch(24)
    
    def create(self, name="Wall Oven"):
        self.create_appliance(name, 'WALL_OVEN')
        
        # Add wall oven specific properties
        self.add_property('Is Double Oven', 'CHECKBOX', False)
        
    def set_double_oven(self, is_double=True):
        """Configure as double oven."""
        if is_double:
            self.set_input('Dim Z', inch(51))
        else:
            self.set_input('Dim Z', inch(29))
        self.obj['Is Double Oven'] = is_double


class Dishwasher(Appliance):
    """Standard dishwasher appliance."""
    
    width = inch(24)
    height = inch(34)
    depth = inch(24)
    
    def create(self, name="Dishwasher"):
        self.create_appliance(name, 'DISHWASHER')
        
        # Add dishwasher-specific properties
        self.add_property('Panel Ready', 'CHECKBOX', False)


class Refrigerator(Appliance):
    """Refrigerator appliance."""
    
    width = inch(36)
    height = inch(70)
    depth = inch(30)
    
    def create(self, name="Refrigerator"):
        self.create_appliance(name, 'REFRIGERATOR')
        
        # Add refrigerator-specific properties
        self.add_property('Counter Depth', 'CHECKBOX', False)
        self.add_property('Has Water Line', 'CHECKBOX', True)
        
    def set_counter_depth(self, is_counter_depth=True):
        """Configure as counter-depth refrigerator."""
        if is_counter_depth:
            self.set_input('Dim Y', inch(24))
        else:
            self.set_input('Dim Y', inch(30))
        self.obj['Counter Depth'] = is_counter_depth


class Microwave(Appliance):
    """Microwave oven - can be countertop or over-range."""
    
    width = inch(24)
    height = inch(12)
    depth = inch(14)
    
    def create(self, name="Microwave"):
        self.create_appliance(name, 'MICROWAVE')
        
        # Add microwave-specific properties
        self.add_property('Over Range', 'CHECKBOX', False)
        self.add_property('Built In', 'CHECKBOX', False)
        
    def set_over_range(self):
        """Configure as over-range microwave with ventilation."""
        self.set_input('Dim X', inch(30))
        self.set_input('Dim Z', inch(17))
        self.set_input('Dim Y', inch(16))
        self.obj['Over Range'] = True


class Hood(Appliance):
    """Range hood / ventilation."""
    
    width = inch(30)
    height = inch(6)
    depth = inch(20)
    
    def create(self, name="Hood"):
        self.create_appliance(name, 'HOOD')
        
        # Add hood-specific properties
        self.add_property('Hood Style', 'TEXT', 'Under Cabinet')  # Under Cabinet, Wall Mount, Island
        self.add_property('CFM Rating', 'QUANTITY', 400)


class Sink(Appliance):
    """Kitchen or bathroom sink."""
    
    width = inch(33)
    height = inch(10)
    depth = inch(22)
    
    def create(self, name="Sink"):
        self.create_appliance(name, 'SINK')
        self.obj['IS_COUNTERTOP_APPLIANCE'] = True
        
        # Add sink-specific properties
        self.add_property('Sink Type', 'TEXT', 'Double Bowl')  # Single, Double, Farmhouse
        self.add_property('Undermount', 'CHECKBOX', True)


class WashingMachine(Appliance):
    """Clothes washing machine."""
    
    width = inch(27)
    height = inch(38)
    depth = inch(30)
    
    def create(self, name="Washing Machine"):
        self.create_appliance(name, 'WASHING_MACHINE')
        
        self.add_property('Front Load', 'CHECKBOX', True)


class Dryer(Appliance):
    """Clothes dryer."""
    
    width = inch(27)
    height = inch(38)
    depth = inch(30)
    
    def create(self, name="Dryer"):
        self.create_appliance(name, 'DRYER')
        
        self.add_property('Front Load', 'CHECKBOX', True)
        self.add_property('Gas', 'CHECKBOX', False)
