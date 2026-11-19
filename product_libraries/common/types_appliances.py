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
    # True for appliances whose width is meant to vary (e.g. a range
    # hood spanning the range below it). Placement enables a typed
    # width override only for these; fixed-size appliances ignore it.
    variable_width = False
    
    def create_appliance(self, name, appliance_type, label=None):
        """Create an appliance with standard setup.

        Args:
            name: Display name for the appliance
            appliance_type: Type identifier (RANGE, DISHWASHER, REFRIGERATOR, etc.)
            label: Annotation text drawn on the cage; defaults to
                appliance_type. Stored on the root (APPLIANCE_LABEL) so
                the Set Label command can re-read / rewrite it.
        """
        super().create(name)
        self.obj['IS_APPLIANCE'] = True
        self.obj['APPLIANCE_TYPE'] = appliance_type
        self.obj['APPLIANCE_LABEL'] = label or appliance_type
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
        appliance_text.create('Appliance Text', label or appliance_type,
                              props.annotation_text_size)
        appliance_text.obj.parent = self.obj
        appliance_text.obj['IS_APPLIANCE_TEXT'] = True
        appliance_text.obj.rotation_euler.x = math.radians(90)
        # The drivers ride on delta_location so the label still follows
        # the appliance's size while its location stays free to move.
        z_expr = (LOW_LABEL_Z_EXPR if appliance_type in LOW_LABEL_TYPES
                  else 'dim_z/2')
        _drive_delta(appliance_text.obj, 0, 'dim_x/2', [dim_x])
        _drive_delta(appliance_text.obj, 1, '-dim_y', [dim_y])
        _drive_delta(appliance_text.obj, 2, z_expr, [dim_z])
        appliance_text.set_alignment('CENTER', 'CENTER')


# Floor-standing appliances whose label reads in the open lower part of
# the face: mid-height is where opening dimensions run on elevations.
LOW_LABEL_TYPES = {'DISHWASHER', 'RANGE', 'UNDER_COUNTER'}
LOW_LABEL_Z_EXPR = 'min(dim_z/2, 0.1524)'   # 6 in up, or mid on a short unit


def _drive_delta(obj, index, expression, variables):
    from ... import hb_utils
    driver = obj.driver_add('delta_location', index)
    hb_utils.add_driver_variables(driver, variables)
    driver.driver.expression = expression


def free_appliance_labels():
    """Move the size drivers of older appliance labels from location to
    delta_location, so a label can be dragged clear of other notes and
    still follow the appliance. Where it sits does not change."""
    count = 0
    for obj in bpy.data.objects:
        if not obj.get('IS_APPLIANCE_TEXT'):
            continue
        parent = obj.parent
        if parent is None or not parent.get('IS_APPLIANCE'):
            continue
        ad = obj.animation_data
        if ad is None:
            continue
        olds = [fc for fc in ad.drivers if fc.data_path == 'location']
        if not olds:
            continue
        for fc in olds:
            index = fc.array_index
            new = obj.driver_add('delta_location', index)
            for var in fc.driver.variables:
                nv = new.driver.variables.new()
                nv.type = var.type
                nv.name = var.name
                for t_old, t_new in zip(var.targets, nv.targets):
                    t_new.id = t_old.id
                    t_new.data_path = t_old.data_path
            new.driver.expression = fc.driver.expression
            obj.driver_remove('location', index)
            obj.location[index] = 0.0
        count += 1
    return count


class Range(Appliance):
    """Freestanding range/stove appliance."""
    
    width = inch(30)
    height = inch(36)
    depth = inch(25)
    variable_width = True
    
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
    
    APPLIANCE_TYPE = 'COOKTOP'

    def create(self, name="Cooktop"):
        self.create_appliance(name, 'COOKTOP')
        self.obj['IS_COUNTERTOP_APPLIANCE'] = True


class WallOven(Appliance):
    """Wall-mounted oven."""
    
    width = inch(30)
    height = inch(29)
    depth = inch(24)
    
    APPLIANCE_TYPE = 'WALL_OVEN'

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


class UnderCounterAppliance(Appliance):
    """Generic under-counter appliance (beverage center, wine fridge,
    ice maker, ...). Dishwasher-sized wireframe cage; the annotation
    label is user-editable via the Set Label command so one product
    covers the whole category."""

    width = inch(24)
    height = inch(34)
    depth = inch(24)
    # One product covers units of many widths (ice maker, compactor,
    # wine fridge), so it takes a typed width while placing.
    variable_width = True

    def create(self, name="Under Counter Appliance"):
        self.create_appliance(name, 'UNDER_COUNTER', label='BEV CENTER')

        # Paneled like a dishwasher more often than not.
        self.add_property('Panel Ready', 'CHECKBOX', False)


class Refrigerator(Appliance):
    """Refrigerator appliance."""
    
    width = inch(36)
    height = inch(70)
    depth = inch(30)
    variable_width = True

    def create(self, name="Refrigerator"):
        self.create_appliance(name, 'REFRIGERATOR')
        
        # Add refrigerator-specific properties
        self.add_property('Counter Depth', 'CHECKBOX', False)
        self.add_property('Has Water Line', 'CHECKBOX', True)
        self.add_property('Panel Ready', 'CHECKBOX', False)
        
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
    
    APPLIANCE_TYPE = 'MICROWAVE'

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
    variable_width = True
    
    def create(self, name="Hood"):
        self.create_appliance(name, 'HOOD')
        
        # Add hood-specific properties
        self.add_property('Hood Style', 'TEXT', 'Under Cabinet')  # Under Cabinet, Wall Mount, Island
        self.add_property('CFM Rating', 'QUANTITY', 400)


class UnderCabinetHood(Appliance):
    """A slim vent hood hung under an upper cabinet's bay. Its own type,
    not HOOD: a range hood stands on the wall by itself, and everything
    that looks for one (wood hoods, finished ends beside a hood) must
    not mistake this for it."""

    width = inch(30)
    height = inch(6)
    depth = inch(18)

    APPLIANCE_TYPE = 'UNDER_CABINET_HOOD'

    def create(self, name="Under Cabinet Hood"):
        self.create_appliance(name, 'UNDER_CABINET_HOOD', label='HOOD')


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


class Toilet(Appliance):
    """A close-coupled toilet, its tank against the wall."""

    width = inch(20)
    height = inch(30)
    depth = inch(29)

    APPLIANCE_TYPE = 'TOILET'

    def create(self, name="Toilet"):
        self.create_appliance(name, 'TOILET', label='WC')


class PedestalSink(Appliance):
    """A basin on a pedestal, standing free of any cabinet."""

    width = inch(24)
    height = inch(34)
    depth = inch(19)

    APPLIANCE_TYPE = 'PEDESTAL_SINK'

    def create(self, name="Pedestal Sink"):
        self.create_appliance(name, 'PEDESTAL_SINK', label='LAV')


class AlcoveTub(Appliance):
    """A tub set between two walls, its apron to the room."""

    width = inch(60)
    height = inch(20)
    depth = inch(30)

    APPLIANCE_TYPE = 'ALCOVE_TUB'

    def create(self, name="Alcove Tub"):
        self.create_appliance(name, 'ALCOVE_TUB', label='TUB')


class FreestandingTub(Appliance):
    """An oval tub standing free on the floor, a filler at its drain end."""

    width = inch(66)
    height = inch(23)
    depth = inch(32)

    APPLIANCE_TYPE = 'FREESTANDING_TUB'

    def create(self, name="Freestanding Tub"):
        self.create_appliance(name, 'FREESTANDING_TUB', label='TUB')


class Shower(Appliance):
    """A shower pan with its glass, the head and valve on the back wall."""

    width = inch(36)
    height = inch(80)
    depth = inch(36)

    APPLIANCE_TYPE = 'SHOWER'

    def create(self, name="Shower"):
        self.create_appliance(name, 'SHOWER', label='SHOWER')


class TubShower(Appliance):
    """An alcove tub with a shower over it: a curtain or a glass screen."""

    width = inch(60)
    height = inch(80)
    depth = inch(30)

    APPLIANCE_TYPE = 'TUB_SHOWER'

    def create(self, name="Tub Shower"):
        self.create_appliance(name, 'TUB_SHOWER', label='TUB / SHOWER')


class WashingMachine(Appliance):
    """Clothes washing machine."""

    width = inch(27)
    height = inch(38)
    depth = inch(30)

    APPLIANCE_TYPE = 'WASHING_MACHINE'

    def create(self, name="Washing Machine"):
        self.create_appliance(name, 'WASHING_MACHINE', label='WASHER')

        self.add_property('Front Load', 'CHECKBOX', True)


class Dryer(Appliance):
    """Clothes dryer."""

    width = inch(27)
    height = inch(38)
    depth = inch(30)

    APPLIANCE_TYPE = 'DRYER'

    def create(self, name="Dryer"):
        self.create_appliance(name, 'DRYER')

        self.add_property('Front Load', 'CHECKBOX', True)
        self.add_property('Gas', 'CHECKBOX', False)


class StackedWasherDryer(Appliance):
    """A front-load washer with its dryer stacked on top, as one unit --
    freestanding, or housed in a tall cabinet's appliance opening."""

    width = inch(27)
    height = inch(77)
    depth = inch(30)

    APPLIANCE_TYPE = 'STACKED_LAUNDRY'

    def create(self, name="Stacked Washer Dryer"):
        self.create_appliance(name, 'STACKED_LAUNDRY',
                              label='WASHER / DRYER')
        self.add_property('Gas', 'CHECKBOX', False)
