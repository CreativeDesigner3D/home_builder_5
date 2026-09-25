import bpy
import math
import os
from ...hb_types import GeoNodeObject, GeoNodeCage, GeoNodeCutpart, GeoNodeHardware, GeoNodeDrawerBox, CabinetPartModifier
from ... import hb_project
from ... import units
from ...units import inch
from . import solver_frameless

class Cabinet(GeoNodeCage):

    default_exterior = "Doors"

    width = inch(18)
    height = inch(34)
    depth = inch(24)

    def add_properties_common(self):
        props = bpy.context.scene.hb_frameless
        self.add_property('Material Thickness', 'DISTANCE', props.default_carcass_part_thickness)

    def _get_toe_kick_type_index(self):
        """Map the default_toe_kick_type enum to a COMBOBOX index."""
        props = bpy.context.scene.hb_frameless
        type_map = {
            'Notch Ends to Floor': 0,
            'Ladder Style': 1,
            'Floating': 2,
            'Leg Levelers': 3,
        }
        return type_map.get(props.default_toe_kick_type, 0)

    def add_properties_toe_kick(self):
        props = bpy.context.scene.hb_frameless
        self.add_property('Toe Kick Height', 'DISTANCE', props.default_toe_kick_height)
        self.add_property('Toe Kick Setback', 'DISTANCE', props.default_toe_kick_setback)
        self.add_property('Flush Toe Kick', 'CHECKBOX', False)
        self.add_property('Toe Kick Panel', 'CHECKBOX', False)
        self.add_property('Toe Kick Panel Thickness', 'DISTANCE', inch(0.375))
        self.add_property('Toe Kick End Inset', 'DISTANCE', 0.0)
        self.add_property('Remove Bottom', 'CHECKBOX', False)
        tkt_index = self._get_toe_kick_type_index()
        self.add_property('Toe Kick Type', 'COMBOBOX', tkt_index,
                          combobox_items=["Notch Ends to Floor", "Ladder Style", "Floating", "Leg Levelers"])
        self.add_property('Leg Leveler Inset', 'DISTANCE', props.default_leg_leveler_inset)
    
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
                solver_frameless.attach_cage(cage.obj, bay.obj)

    def _get_leg_leveler_object(self):
        """Get the leg leveler mesh object, loading once and caching via scene props."""
        from ... import hb_project

        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless

        # Return cached if available
        if props.current_leg_leveler_object:
            return props.current_leg_leveler_object

        # Load from file
        leveler_path = os.path.join(
            os.path.dirname(__file__), 'frameless_assets', 'leg_levelers', 'Leg Leveler.blend'
        )
        if not os.path.exists(leveler_path):
            print(f"WARNING: Leg leveler file not found: {leveler_path}")
            return None

        with bpy.data.libraries.load(leveler_path) as (data_from, data_to):
            data_to.objects = data_from.objects

        for obj in data_to.objects:
            props.current_leg_leveler_object = obj
            return obj
        return None

    def _add_leg_levelers(self):
        """Add four leg leveler hardware objects at the bottom corners of the
        cabinet, placed by the solver."""
        ll_obj = self._get_leg_leveler_object()
        if ll_obj is None:
            return
        for name, role in (('Leg Leveler FL', 'LEG_LEVELER_FL'),
                           ('Leg Leveler FR', 'LEG_LEVELER_FR'),
                           ('Leg Leveler BL', 'LEG_LEVELER_BL'),
                           ('Leg Leveler BR', 'LEG_LEVELER_BR')):
            ll = GeoNodeHardware()
            ll.create(name)
            ll.obj['IS_LEG_LEVELER'] = True
            ll.obj[solver_frameless.PART_ROLE_KEY] = role
            ll.obj.parent = self.obj
            ll.set_input("Object", ll_obj)
            ll.obj.location.z = 0

    def create_cabinet(self,name):
        super().create(name)
        self.obj['IS_FRAMELESS_CABINET_CAGE'] = True
        self.obj['MENU_ID'] = 'HOME_BUILDER_MT_cabinet_commands'
        self.obj.display_type = 'WIRE'
        
        self.set_input('Dim X', self.width)
        self.set_input('Dim Y', self.depth)
        self.set_input('Dim Z', self.height)
        self.set_input('Mirror Y', True)

    def _add_carcass_part(self, name, role, part_cls=None, rotation=(0, 0, 0),
                          mirror='', finish=None):
        """One carcass part, parented and tagged. Size and position are the
        solver's to write, so only the fixed orientation is set here."""
        part = (part_cls or CabinetPart)()
        part.create(name)
        part.obj.parent = self.obj
        part.obj[solver_frameless.PART_ROLE_KEY] = role
        part.obj.rotation_euler = tuple(math.radians(a) for a in rotation)
        for axis in mirror:
            part.set_input('Mirror ' + axis, True)
        if finish is not None:
            part.obj['Finish Top'] = finish[0]
            part.obj['Finish Bottom'] = finish[1]
        return part

    def _add_carcass_sides(self, notched):
        side_cls = CabinetSideNotched if notched else CabinetPart
        self._add_carcass_part('Left Side', 'LEFT_SIDE', side_cls,
                               rotation=(0, -90, 0), mirror='YZ')
        self._add_carcass_part('Right Side', 'RIGHT_SIDE', side_cls,
                               rotation=(0, -90, 0), mirror='Y')

    def _add_carcass_bay(self):
        bay = CabinetBay()
        bay.create("Bay")
        bay.obj.parent = self.obj
        bay.obj[solver_frameless.PART_ROLE_KEY] = 'BAY'
        return bay

    def _add_top_options(self):
        """Stretchers and sink apron alongside the full top; the solver
        shows whichever Base Top Construction asks for."""
        self._add_carcass_part('Front Stretcher', 'FRONT_STRETCHER',
                               mirror='Z', finish=(False, False))
        self._add_carcass_part('Back Stretcher', 'BACK_STRETCHER',
                               mirror='Z', finish=(False, False))
        self._add_carcass_part('Sink Apron', 'SINK_APRON', rotation=(-90, 0, 0))

    def _add_toe_kick_extras(self, toe_kick_type):
        if toe_kick_type == 1:  # Ladder Style
            ladder = LadderBaseCage()
            ladder.create('Ladder Base')
            ladder.obj.parent = self.obj
            ladder.obj[solver_frameless.PART_ROLE_KEY] = 'LADDER_BASE'
        elif toe_kick_type == 3:  # Leg Levelers
            self._add_leg_levelers()

    def create_base_carcass(self,name):
        self.create_cabinet(name)

        self.add_properties_common()
        self.add_properties_toe_kick()
        self.add_properties_base_top()
        self.obj[solver_frameless.CARCASS_KEY] = 'BASE'

        toe_kick_type = self.obj.get('Toe Kick Type', 0)

        # Notch Ends to Floor cuts the toe kick out of the sides; the other
        # types stand plain sides on the toe kick assembly.
        self._add_carcass_sides(notched=toe_kick_type == 0)
        self._add_carcass_part('Bottom', 'BOTTOM', mirror='Y')
        self._add_carcass_part('Back', 'BACK', rotation=(90, -90, 0), mirror='Y')
        if toe_kick_type == 0:
            self._add_carcass_part('Toe Kick', 'TOE_KICK', rotation=(-90, 0, 0), mirror='Y')
        self._add_carcass_part('Top', 'TOP', mirror='YZ')
        self._add_top_options()
        self._add_carcass_bay()
        self._add_toe_kick_extras(toe_kick_type)

        solver_frameless.recalculate_cabinet(self.obj)

    def create_tall_carcass(self,name):
        """Create tall cabinet carcass - always uses full top, no stretcher options."""
        self.create_cabinet(name)

        self.add_properties_common()
        self.add_properties_toe_kick()
        # Note: No add_properties_base_top() - tall cabinets always have full top
        self.obj[solver_frameless.CARCASS_KEY] = 'TALL'

        toe_kick_type = self.obj.get('Toe Kick Type', 0)

        self._add_carcass_sides(notched=toe_kick_type == 0)
        self._add_carcass_part('Bottom', 'BOTTOM', mirror='Y')
        self._add_carcass_part('Back', 'BACK', rotation=(90, -90, 0), mirror='Y')
        if toe_kick_type == 0:
            self._add_carcass_part('Toe Kick', 'TOE_KICK', rotation=(-90, 0, 0), mirror='Y')
        self._add_carcass_part('Top', 'TOP', mirror='YZ')
        self._add_carcass_bay()
        self._add_toe_kick_extras(toe_kick_type)

        solver_frameless.recalculate_cabinet(self.obj)

    def create_upper_carcass(self,name):
        self.create_cabinet(name)

        self.add_properties_common()
        self.obj[solver_frameless.CARCASS_KEY] = 'UPPER'

        self._add_carcass_sides(notched=False)
        self._add_carcass_part('Bottom', 'BOTTOM', mirror='Y')
        self._add_carcass_part('Back', 'BACK', rotation=(90, -90, 0), mirror='Y')
        self._add_carcass_part('Top', 'TOP', mirror='YZ')
        self._add_carcass_bay()

        solver_frameless.recalculate_cabinet(self.obj)

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
        elif self.default_exterior == 'Sink':
            self.add_sink_front()
        elif self.default_exterior == 'Open':
            self.add_open_shelves()

    def add_doors(self):
        """Add door fronts to the cabinet bay."""
        doors = Doors()
        doors.door_pull_location = "Base"
        self.add_cage_to_bay(doors)

    def add_sink_front(self):
        """A false front where a drawer would be, doors below: the sink
        bowl takes the space behind the false front."""
        props = bpy.context.scene.hb_frameless

        front = FalseFront()
        front.half_overlay_bottom = True
        doors = Doors()
        doors.half_overlay_top = True
        doors.seed_shelves = False

        split = SplitterVertical()
        split.splitter_qty = 1
        split.opening_sizes = [props.top_drawer_front_height, 0]
        split.opening_inserts = [front, doors]
        self.add_cage_to_bay(split)
        self.obj['IS_SINK_CABINET'] = True
        # A sink base is built for the bowl whatever the room default:
        # apron top, and the solver hangs the sink model in the bay.
        self.obj['Base Top Construction'] = solver_frameless.TOP_SINK
        solver_frameless.recalculate_cabinet(self.obj)

    def add_open_shelves(self):
        """No front at all: the bay stays open with adjustable shelves."""
        self.add_cage_to_bay(OpenWithShelves())
    
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


class LapDrawerCabinet(Cabinet):
    """Lap drawer cabinet - a single drawer box raised off the floor.
    
    The box height is determined by top_drawer_front_height.
    The top of the cabinet aligns with the top of a standard base cabinet.
    """
    
    def __init__(self):
        super().__init__()
        props = bpy.context.scene.hb_frameless
        self.width = props.default_cabinet_width
        self.height = props.top_drawer_front_height
        self.depth = props.base_cabinet_depth
    
    def create(self, name="Lap Drawer"):
        self.create_lap_drawer_carcass(name)
        self.obj['CABINET_TYPE'] = 'BASE'
        
        # Add single drawer exterior
        drawer = Drawer()
        self.add_cage_to_bay(drawer)
    
    def create_lap_drawer_carcass(self, name):
        self.create_cabinet(name)

        props = bpy.context.scene.hb_frameless

        self.add_properties_common()
        self.add_properties_base_top()
        self.obj[solver_frameless.CARCASS_KEY] = 'LAP_DRAWER'

        # Z location: top aligns with base cabinet height
        self.obj.location.z = props.base_cabinet_height - self.height

        self._add_carcass_sides(notched=False)
        self._add_carcass_part('Bottom', 'BOTTOM', mirror='Y')
        self._add_carcass_part('Back', 'BACK', rotation=(90, -90, 0), mirror='Y')
        self._add_carcass_part('Top', 'TOP', mirror='YZ')
        self._add_top_options()
        self._add_carcass_bay()

        solver_frameless.recalculate_cabinet(self.obj)


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
        if self.default_exterior == 'Open':
            self.add_cage_to_bay(OpenWithShelves())
        else:
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
        door_drawer.create()
        # The bottom opening houses the refrigerator model itself; the
        # solver keeps it sized to the opening.
        for (role, index), opening in solver_frameless.split_parts(
                door_drawer.obj).items():
            if role == 'OPENING' and index == 2:
                opening['APPLIANCE_OPENING'] = 'REFRIGERATOR'
        for child in self.obj.children_recursive:
            if 'IS_FRAMELESS_BAY_CAGE' in child:
                door_drawer.obj.parent = child
                solver_frameless.attach_cage(door_drawer.obj, child)


# Column refrigeration: a tall cabinet whose bottom opening houses a
# panel-ready column unit, with doors over it.
COLUMN_UNITS = {
    'Tall Column Refrigerator': "Column Refrigerator",
    'Tall Column Freezer': "Column Freezer",
}
COLUMN_WIDTH = inch(30.0)
COLUMN_OPENING_HEIGHT = inch(80.0)
# Tall enough for doors of a useful height over the unit.
COLUMN_MIN_CABINET_HEIGHT = inch(96.0)


class ColumnRefrigeratorCabinet(RefrigeratorCabinet):
    """A column refrigerator or freezer housed in a tall cabinet. The
    unit is panelled and set a door gap proud of the carcass, so its panel
    finishes flush with the cabinet doors."""

    def __init__(self, column='Tall Column Refrigerator'):
        super().__init__()
        props = bpy.context.scene.hb_frameless
        self.column = column if column in COLUMN_UNITS else 'Tall Column Refrigerator'
        self.width = COLUMN_WIDTH
        self.height = max(props.tall_cabinet_height, COLUMN_MIN_CABINET_HEIGHT)

    def create(self, name="Column Refrigerator"):
        super().create(name)
        self.obj['COLUMN_UNIT'] = self.column
        solver_frameless.recalculate_cabinet(self.obj)
        from ..common import appliance_geo
        # Collected first: panelling the unit rebuilds its model.
        openings = [o for o in self.obj.children_recursive
                    if o.get('APPLIANCE_OPENING') == 'REFRIGERATOR']
        for opening in openings:
            model = appliance_geo.opening_appliance(opening)
            if model is not None:
                model['APPLIANCE_NAME'] = COLUMN_UNITS[self.column]
                model['HB_LIBRARY'] = 'FRAMELESS'
                appliance_geo.set_front_style(model, 'CABINET')
                # The run is laid out over the opening like a door, so
                # the panel needs no margin of its own.
                panels = model.appliance_panels
                panels.end_reveal = 0.0

    def add_openings(self):
        top_doors = Doors()
        top_doors.half_overlay_bottom = True
        top_doors.door_pull_location = "Upper"
        splitter = SplitterVertical()
        splitter.splitter_qty = 1
        splitter.opening_sizes = [0, COLUMN_OPENING_HEIGHT]
        splitter.opening_inserts = [top_doors, None]
        splitter.create()
        for (role, index), opening in solver_frameless.split_parts(
                splitter.obj).items():
            if role == 'OPENING' and index == 2:
                opening['APPLIANCE_OPENING'] = 'REFRIGERATOR'
                opening['APPLIANCE_PROUD'] = inch(0.125)
                opening['APPLIANCE_SEED'] = {'fridge_config': 'COLUMN',
                                             'grille_height': 0.0}
        for child in self.obj.children_recursive:
            if 'IS_FRAMELESS_BAY_CAGE' in child:
                splitter.obj.parent = child
                solver_frameless.attach_cage(splitter.obj, child)


# Appliance towers, top to bottom: (insert, fixed height or 0 to share
# what the fixed ones leave). The oven and microwave openings are sized
# to common cut-outs; Edit Opening Sizes changes them per cabinet.
APPLIANCE_TOWERS = {
    'Tall Oven': (('DOORS', 0.0), ('WALL_OVEN', inch(29.0)),
                  ('DRAWER', inch(12.0)), ('DRAWER', inch(12.0))),
    'Tall Double Oven': (('DOORS', 0.0), ('WALL_OVEN', inch(29.0)),
                         ('WALL_OVEN', inch(29.0)), ('DRAWER', inch(10.0))),
    'Tall Oven Microwave': (('DOORS', 0.0), ('MICROWAVE', inch(18.0)),
                            ('WALL_OVEN', inch(29.0)), ('DRAWER', inch(12.0))),
}
APPLIANCE_LABELS = {'WALL_OVEN': "Oven", 'MICROWAVE': "Microwave"}
# A 30" wall oven's box: its 28-1/2" cut-out is the tower's inside width.
APPLIANCE_TOWER_WIDTH = inch(30.0)


class ApplianceTowerCabinet(TallCabinet):
    """Tall cabinet built around wall ovens and microwaves: doors over
    the appliance openings, drawers under them. Each appliance opening
    houses the appliance's model."""

    def __init__(self, tower='Tall Oven'):
        super().__init__()
        self.tower = tower if tower in APPLIANCE_TOWERS else 'Tall Oven'
        self.width = APPLIANCE_TOWER_WIDTH

    def create(self, name="Oven Tower"):
        self.create_tall_carcass(name)
        self.obj['CABINET_TYPE'] = 'TALL'
        self.obj['APPLIANCE_TOWER'] = self.tower
        stack = APPLIANCE_TOWERS[self.tower]
        splitter = SplitterVertical()
        splitter.splitter_qty = len(stack) - 1
        last = len(stack) - 1
        for i, (kind, size) in enumerate(stack):
            if kind == 'DOORS':
                insert = Doors()
                insert.door_pull_location = "Upper"
            elif kind == 'DRAWER':
                insert = Drawer()
            else:
                insert = Appliance()
                insert.appliance_name = APPLIANCE_LABELS.get(kind, "Appliance")
                insert.appliance_type = kind
            insert.half_overlay_top = i > 0
            insert.half_overlay_bottom = i < last
            splitter.opening_sizes.append(size)
            splitter.opening_inserts.append(insert)
        self.add_cage_to_bay(splitter)


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
        if self.default_exterior == 'Open':
            self.add_cage_to_bay(OpenWithShelves())
        else:
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


# ---------------------------------------------------------------------------
# Blind corner cabinets
# ---------------------------------------------------------------------------
# A blind corner runs into the corner and lets the neighbouring run butt
# against it. The part that ends up behind the neighbour is closed by a
# blind panel captured in the carcass -- between the top and bottom,
# against the corner-side end, flush with the front edges -- and the
# doors overlay the rest. The panel reaches far enough out of the corner
# for a cabinet on the adjacent wall to land on it: that cabinet's
# depth, its fronts, and the corner filler that lets the doors clear.

BLIND_NEIGHBOR_FRONT = inch(0.875)   # door gap plus front thickness
BLIND_FILLER_WIDTH = inch(1.5)       # types_products.CORNER_FILLER_WIDTH


class BlindCornerMixin:
    """Shared front for the three blind corner cabinets."""

    blind_side = 'Left'     # which end goes into the corner
    blind_width = None      # None: sized for the adjacent wall's cabinet

    def blind_panel_width(self):
        """Corner-side end of the cabinet to the edge of the doors."""
        if self.blind_width:
            return self.blind_width
        props = bpy.context.scene.hb_frameless
        neighbor_depth = {
            'TALL': props.tall_cabinet_depth,
            'UPPER': props.upper_cabinet_depth,
        }.get(self.obj.get('CABINET_TYPE'), props.base_cabinet_depth)
        return neighbor_depth + BLIND_NEIGHBOR_FRONT + BLIND_FILLER_WIDTH

    def add_blind_exterior(self, pull_location="Base"):
        self.obj['IS_BLIND_CORNER'] = True
        self.obj['Blind Side'] = self.blind_side
        self.add_property('Blind Width', 'DISTANCE', self.blind_panel_width())
        self._add_carcass_part('Blind Panel', 'BLIND_PANEL',
                               rotation=(90, -90, 0), mirror='Y')

        # The solver narrows the bay to what the blind panel leaves.
        doors = Doors()
        doors.door_pull_location = pull_location
        self.add_cage_to_bay(doors)
        solver_frameless.recalculate_cabinet(self.obj)


class BlindCornerBaseCabinet(BlindCornerMixin, BaseCabinet):
    """Base blind corner: doors on what the blind panel leaves."""

    def __init__(self):
        super().__init__()
        self.width = bpy.context.scene.hb_frameless.base_width_blind

    def create(self, name="Blind Base"):
        self.create_base_carcass(name)
        self.obj['CABINET_TYPE'] = 'BASE'
        self.add_blind_exterior("Base")


class BlindCornerTallCabinet(BlindCornerMixin, TallCabinet):
    """Tall blind corner: full height, doors on what the blind panel leaves."""

    def __init__(self):
        super().__init__()
        self.width = bpy.context.scene.hb_frameless.tall_width_blind

    def create(self, name="Blind Tall"):
        self.create_tall_carcass(name)
        self.obj['CABINET_TYPE'] = 'TALL'
        self.add_blind_exterior("Tall")


class BlindCornerUpperCabinet(BlindCornerMixin, UpperCabinet):
    """Upper blind corner: doors on what the blind panel leaves."""

    def __init__(self):
        super().__init__()
        self.width = bpy.context.scene.hb_frameless.upper_width_blind

    def create(self, name="Blind Upper"):
        self.create_upper_carcass(name)
        self.obj['CABINET_TYPE'] = 'UPPER'
        self.obj.display_type = 'WIRE'
        self.add_blind_exterior("Upper")


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
        solver_frameless.attach_cage(insert.obj, opening.obj)
        
    def create(self):
        super().create('Splitter Vertical')
        props = bpy.context.scene.hb_frameless

        self.obj['IS_FRAMELESS_SPLITTER_VERTICAL_CAGE'] = True
        self.obj.display_type = 'WIRE'

        self.add_property('Shelf Quantity', 'QUANTITY', 1)
        self.add_property('Material Thickness', 'DISTANCE', props.default_carcass_part_thickness)

        # Opening heights live on a calculator: the solver reads them and
        # fills in the equal ones from whatever height is left over.
        empty_obj = self.add_empty("Calc Object")
        empty_obj.empty_display_size = .001
        opening_calculator = self.obj.home_builder.add_calculator("Opening Calculator",empty_obj)
        for i in range(1,self.splitter_qty+2):
            opening_calculator.add_calculator_prompt('Opening ' + str(i) + ' Height')

        # Add Shelf Splitters and Openings from Top to Bottom
        for i in range(1,self.splitter_qty+2):
            if i < self.splitter_qty+1:
                shelf = CabinetPart()
                shelf.create('Vertical Splitter ' + str(i))
                shelf.obj.parent = self.obj
                solver_frameless.tag_split_part(shelf.obj, 'SPLITTER', i)

            opening = CabinetOpening()
            opening.create('Opening ' + str(i))
            opening.obj.parent = self.obj
            solver_frameless.tag_split_part(opening.obj, 'OPENING', i)

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
        solver_frameless.attach_cage(insert.obj, opening.obj)
        
    def create(self):
        super().create('Splitter Horizontal')
        props = bpy.context.scene.hb_frameless

        self.obj['IS_FRAMELESS_SPLITTER_HORIZONTAL_CAGE'] = True
        self.obj.display_type = 'WIRE'

        self.add_property('Divider Quantity', 'QUANTITY', 1)
        self.add_property('Material Thickness', 'DISTANCE', props.default_carcass_part_thickness)

        # Opening widths live on a calculator: the solver reads them and
        # fills in the equal ones from whatever width is left over.
        empty_obj = self.add_empty("Calc Object")
        empty_obj.empty_display_size = .001
        opening_calculator = self.obj.home_builder.add_calculator("Opening Calculator",empty_obj)
        for i in range(1,self.splitter_qty+2):
            opening_calculator.add_calculator_prompt('Opening ' + str(i) + ' Width')

        # Add Openings and Dividers from Left to Right
        for i in range(1,self.splitter_qty+2):
            opening = CabinetOpening()
            opening.create('Opening ' + str(i))
            opening.obj.parent = self.obj
            solver_frameless.tag_split_part(opening.obj, 'OPENING', i)

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
                divider.set_input("Mirror Z",True)
                solver_frameless.tag_split_part(divider.obj, 'SPLITTER', i)

        # Set Opening Sizes
        for i in range(1,self.splitter_qty+2):
            if len(self.opening_sizes) > i - 1 and self.opening_sizes[i-1] != 0:
                ow = opening_calculator.get_calculator_prompt('Opening ' + str(i) + ' Width')
                ow.equal = False
                ow.distance_value = self.opening_sizes[i-1]


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
        props = bpy.context.scene.hb_frameless
        self.add_property("Left Thickness",'DISTANCE',props.default_carcass_part_thickness)
        self.add_property("Right Thickness",'DISTANCE',props.default_carcass_part_thickness)
        self.add_property("Top Thickness",'DISTANCE',props.default_carcass_part_thickness)
        self.add_property("Bottom Thickness",'DISTANCE',props.default_carcass_part_thickness)

    def add_properties_front_overlay_calculations(self):

        self.overlay_prompts = self.add_empty('Overlay Prompt Obj')
        self.overlay_prompts.home_builder.add_property("Overlay Top",'DISTANCE',0.0)
        self.overlay_prompts.home_builder.add_property("Overlay Bottom",'DISTANCE',0.0)
        self.overlay_prompts.home_builder.add_property("Overlay Left",'DISTANCE',0.0)
        self.overlay_prompts.home_builder.add_property("Overlay Right",'DISTANCE',0.0)
        # Values are written by the solver from the reveal prompts above.
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

        # One shelf, arrayed up the interior by the solver.
        shelves = CabinetPart()
        shelves.create('Shelf')
        shelves.obj['IS_FRAMELESS_INTERIOR_PART'] = True
        shelves.obj['MENU_ID'] = 'HOME_BUILDER_MT_interior_part_commands'
        # Interior parts get interior material on both sides
        shelves.obj['Finish Top'] = False
        shelves.obj['Finish Bottom'] = False
        shelves.obj.parent = self.obj
        shelves.obj[solver_frameless.PART_ROLE_KEY] = 'SHELF'
        array_mod = shelves.obj.modifiers.new('Qty','ARRAY')
        array_mod.count = 1
        array_mod.use_relative_offset = False
        array_mod.use_constant_offset = True
        array_mod.constant_offset_displace = (0,0,0)


class CabinetInteriorItems(CabinetInterior):
    """Interior built from a list of interior items (roll-outs, tray
    dividers, shelves...). The list lives on the cage; the solver builds
    the parts (see interior_items)."""

    seed_kind = None

    def create(self,name):
        super().create(name)
        self.obj['IS_FRAMELESS_ITEMS_INTERIOR'] = True
        if self.seed_kind:
            from . import interior_items
            interior_items.add_item(self.obj, self.seed_kind)


class Doors(CabinetOpening):

    door_pull_location = "Base"
    # None follows the room's Shelves Behind Doors setting; a sink base
    # says False, since the bowl and trap take that space.
    seed_shelves = None

    def create(self):
        super().create("Doors")

        self.add_property('Front Thickness', 'DISTANCE', inch(.75))
        self.add_property('Vertical Gap', 'DISTANCE', inch(.125))
        self.add_property("Door Swing",'COMBOBOX',2,combobox_items=["Left","Right","Double"])
        self.add_properties_opening_thickness()
        self.add_properties_front_overlays()
        overlay_prompts = self.add_properties_front_overlay_calculations()




        left_door = CabinetDoor()
        left_door.door_pull_location = self.door_pull_location
        left_door.create('Left Door')
        left_door.obj.parent = self.obj
        left_door.obj.rotation_euler.x = math.radians(90)
        left_door.obj.rotation_euler.y = math.radians(-90)
        left_door.set_input("Mirror Y", True)  

        right_door = CabinetDoor()
        right_door.door_pull_location = self.door_pull_location
        right_door.create('Right Door')
        right_door.obj.parent = self.obj
        right_door.obj.rotation_euler.x = math.radians(90)
        right_door.obj.rotation_euler.y = math.radians(-90)
        right_door.set_input("Mirror Y", False)

        seed = self.seed_shelves
        if seed is None:
            seed = bpy.context.scene.hb_frameless.seed_door_shelves
        if seed:
            self.add_interior(CabinetShelves())

    def add_interior(self,interior):
        interior.create('Interior')
        solver_frameless.attach_cage(interior.obj, self.obj)


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




        # Single door covering entire opening with centered, rotated pull
        door = CabinetFlipUpDoor()
        door.create('Flip Up Door')
        door.obj.parent = self.obj
        door.obj.rotation_euler.x = math.radians(90)
        door.obj.rotation_euler.y = math.radians(-90)
        door.set_input("Mirror Y", True)

        if bpy.context.scene.hb_frameless.seed_door_shelves:
            self.add_interior(CabinetShelves())

    def add_interior(self, interior):
        interior.create('Interior')
        solver_frameless.attach_cage(interior.obj, self.obj)


class Drawer(CabinetOpening):

    def create(self):
        super().create("Drawers")

        self.add_property('Front Thickness', 'DISTANCE', inch(.75))
        self.add_properties_opening_thickness()
        self.add_properties_front_overlays()
        overlay_prompts = self.add_properties_front_overlay_calculations()




        drawer_front = CabinetDrawerFront()
        drawer_front.create('Drawer Front')
        drawer_front.obj.parent = self.obj
        drawer_front.obj.rotation_euler.x = math.radians(90)
        drawer_front.obj.rotation_euler.y = math.radians(-90)
        drawer_front.set_input("Mirror Y", True)
        drawer_front.add_drawer_box()


class Pullout(CabinetOpening):
    """A pullout is similar to a drawer but with the pull at the top instead of centered.
    Default interior is a Drawer Box, but different accessories can be added.
    """

    door_pull_location = "Base"

    def create(self):
        super().create("Pullout")

        self.add_property('Front Thickness', 'DISTANCE', inch(.75))
        self.add_properties_opening_thickness()
        self.add_properties_front_overlays()
        overlay_prompts = self.add_properties_front_overlay_calculations()




        pullout_front = CabinetPulloutFront()
        pullout_front.door_pull_location = self.door_pull_location
        pullout_front.create('Pullout Front')
        pullout_front.obj.parent = self.obj
        pullout_front.obj.rotation_euler.x = math.radians(90)
        pullout_front.obj.rotation_euler.y = math.radians(-90)
        pullout_front.set_input("Mirror Y", True)
        
        pullout_front.add_drawer_box()


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




        drawer_front = CabinetDrawerFront()
        drawer_front.create('False Front')
        drawer_front.obj.parent = self.obj
        drawer_front.obj.rotation_euler.x = math.radians(90)
        drawer_front.obj.rotation_euler.y = math.radians(-90)
        drawer_front.set_input("Mirror Y", True)
        
        # Set False Front to True - no drawer box or handle
        drawer_front.set_property("False Front", True)
        # No drawer box added for false front


# Appliance model an Appliance opening houses (see Appliance).
APPLIANCE_KIND_KEY = 'APPLIANCE_KIND'


class Appliance(CabinetOpening):
    """An appliance opening displays centered text with the appliance name.
    Used for built-in appliances like ovens, microwaves, refrigerators, etc.
    """
    
    appliance_name = "Appliance"
    # WALL_OVEN / MICROWAVE: the opening houses that appliance's model,
    # kept sized to it by the solver. None is a label only.
    appliance_type = None

    def create(self):
        from ...hb_details import GeoNodeText

        super().create("Appliance")

        # Store appliance name on the object
        self.obj['APPLIANCE_NAME'] = self.appliance_name
        if self.appliance_type:
            self.obj[APPLIANCE_KIND_KEY] = self.appliance_type
        
        
        props = bpy.context.scene.home_builder
        
        appliance_text = GeoNodeText()
        appliance_text.create('Appliance Text', self.appliance_name, props.annotation_text_size)
        appliance_text.obj.parent = self.obj
        appliance_text.obj['IS_APPLIANCE_TEXT'] = True
        appliance_text.obj.rotation_euler.x = math.radians(90)
        appliance_text.set_alignment('CENTER', 'CENTER')


class OpenWithShelves(CabinetOpening):
    """An open opening with adjustable shelves.
    No door or drawer front, just exposed shelves.
    """
    
    def create(self):
        super().create("Open With Shelves")
        self.add_interior(CabinetShelves())
        
    def add_interior(self,interior):
        interior.create('Interior')
        solver_frameless.attach_cage(interior.obj, self.obj)


class CabinetPart(GeoNodeCutpart):

    def create(self,name):
        super().create(name)
        self.obj['CABINET_PART'] = True
        self.obj['Finish Top'] = False
        self.obj['Finish Bottom'] = True
        self.set_input('Length', inch(24))
        self.set_input('Width', inch(18))
        self.set_input('Thickness', inch(.75))  


class LadderBaseCage(GeoNodeCage):
    """Placeholder cage representing a ladder-style toe kick base assembly.
    
    This is a wireframe cage showing the overall dimensions of the ladder base.
    The actual ladder parts (side pieces, stretchers) will be implemented later.
    """

    def create(self, name):
        super().create(name)
        self.obj['IS_LADDER_BASE'] = True
        self.obj['IS_FRAMELESS_LADDER_CAGE'] = True
        self.obj.color = (0.5, 0.3, 0, 1)  # Brown-ish color to distinguish from cabinet cage


# Toe Kick Type prompt choices, by index.
TOE_KICK_TYPES = ["Notch Ends to Floor", "Ladder Style", "Floating", "Leg Levelers"]
TOE_KICK_NOTCH, TOE_KICK_LADDER, TOE_KICK_FLOATING, TOE_KICK_LEGS = range(4)
_TOE_KICK_PART_ROLES = frozenset({
    'TOE_KICK', 'LEFT_TOE_KICK', 'RIGHT_TOE_KICK', 'LADDER_BASE',
    'TOE_KICK_PANEL', 'TOE_KICK_RETURN_LEFT', 'TOE_KICK_RETURN_RIGHT',
    'LEG_LEVELER_FL', 'LEG_LEVELER_FR', 'LEG_LEVELER_BL', 'LEG_LEVELER_BR',
})


def _remove_tree(obj):
    for child in list(obj.children):
        _remove_tree(child)
    bpy.data.objects.remove(obj, do_unlink=True)


def _set_side_notch(side_obj, notched):
    """Add or take off the toe kick notch on a cabinet side."""
    mod = side_obj.modifiers.get(solver_frameless.NOTCH_MOD_NAME)
    if notched and mod is None:
        notch = GeoNodeCutpart(side_obj).add_part_modifier(
            'CPM_CORNERNOTCH', solver_frameless.NOTCH_MOD_NAME)
        notch.set_input('Flip Y', True)
    elif not notched and mod is not None:
        side_obj.modifiers.remove(mod)


def set_toe_kick_type(cabinet_obj, toe_kick_type):
    """Switch a base, tall or corner base cabinet to another toe kick
    type in place: the toe kick parts of the old type come off, the new
    type's go on, the sides take or lose the notch, and the cabinet is
    solved and repainted. Returns False for a cabinet with no toe kick."""
    kind = solver_frameless.carcass_kind(cabinet_obj)
    if kind not in ('BASE', 'TALL', 'CORNER_BASE'):
        return False
    toe_kick_type = int(toe_kick_type)
    parts = solver_frameless.carcass_parts(cabinet_obj)
    for role, obj in parts.items():
        if role in _TOE_KICK_PART_ROLES:
            _remove_tree(obj)
    for role in ('LEFT_SIDE', 'RIGHT_SIDE'):
        side = parts.get(role)
        if side is not None:
            _set_side_notch(side, toe_kick_type == TOE_KICK_NOTCH)

    if 'Toe Kick Type' in cabinet_obj:
        cabinet_obj['Toe Kick Type'] = toe_kick_type
    else:
        Cabinet(cabinet_obj).add_property(
            'Toe Kick Type', 'COMBOBOX', toe_kick_type,
            combobox_items=TOE_KICK_TYPES)

    if kind == 'CORNER_BASE':
        cab = CornerCabinet(cabinet_obj)
        if toe_kick_type == TOE_KICK_NOTCH:
            cab._add_carcass_part('Left Toe Kick', 'LEFT_TOE_KICK',
                                  rotation=(-90, 0, 90), mirror='Y')
            cab._add_carcass_part('Right Toe Kick', 'RIGHT_TOE_KICK',
                                  rotation=(-90, 0, 0), mirror='XY')
        elif toe_kick_type == TOE_KICK_LADDER:
            ladder = LadderBaseCage()
            ladder.create('Ladder Base')
            ladder.obj.parent = cabinet_obj
            ladder.obj[solver_frameless.PART_ROLE_KEY] = 'LADDER_BASE'
        elif toe_kick_type == TOE_KICK_LEGS:
            cab._add_corner_leg_levelers()
    else:
        cab = Cabinet(cabinet_obj)
        if toe_kick_type == TOE_KICK_NOTCH:
            cab._add_carcass_part('Toe Kick', 'TOE_KICK', rotation=(-90, 0, 0),
                                  mirror='Y')
        cab._add_toe_kick_extras(toe_kick_type)

    solver_frameless.recalculate_cabinet(cabinet_obj)
    main_scene = hb_project.get_main_scene()
    styles = main_scene.hb_frameless.cabinet_styles
    if len(styles):
        index = cabinet_obj.get('CABINET_STYLE_INDEX', 0)
        style = styles[index] if 0 <= index < len(styles) else styles[0]
        style.apply_materials_to_cabinet(cabinet_obj)
    return True


class CabinetSideNotched(CabinetPart):
    """A side with the toe kick notched out of its front bottom corner;
    the solver sizes the notch."""

    def create(self,name):
        super().create(name)
        self.set_input('Length', inch(24))
        self.set_input('Width', inch(18))
        self.set_input('Thickness', inch(.75))

        notch = self.add_part_modifier('CPM_CORNERNOTCH','Notch')
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
        """The source object for this front's pull, or None when pulls
        are off. The closet library's handle list, loaded and finished
        by props_hb_frameless.resolve_pull_object."""
        from . import props_hb_frameless
        return props_hb_frameless.resolve_pull_object(pull_type)

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
        
        pull_obj = self.get_pull_object()
        pull_length = pull_obj.dimensions.x if pull_obj else 0.1016  # Default to 4 inches
        self.add_property('Pull Length', 'DISTANCE', pull_length)


        pull = GeoNodeHardware()
        pull.create('Pull')
        pull.obj['IS_CABINET_PULL'] = True
        pull.obj.parent = self.obj
        pull.obj.rotation_euler.x = math.radians(-90)
        if pull_obj:
            pull.set_input("Object",pull_obj)


class CabinetFlipUpDoor(CabinetFront):
    """A flip-up door front with the pull rotated 90 degrees, centered horizontally, 
    and positioned at the bottom like an upper cabinet pull."""
    
    def create(self, name):
        super().create(name)
        self.obj['IS_DOOR_FRONT'] = True
        self.obj['IS_FLIP_UP_DOOR'] = True
        props = bpy.context.scene.hb_frameless
        
        pull_obj = self.get_pull_object()
        pull_length = pull_obj.dimensions.x if pull_obj else 0.1016  # Default to 4 inches
        self.add_property('Pull Length', 'DISTANCE', pull_length)
        self.add_property('Pull Vertical Location', 'DISTANCE', props.pull_vertical_location_upper)


        pull = GeoNodeHardware()
        pull.create('Pull')
        pull.obj['IS_CABINET_PULL'] = True
        pull.obj.parent = self.obj
        pull.obj.rotation_euler.x = math.radians(-90)
        pull.obj.rotation_euler.z = math.radians(90)
        if pull_obj:
            pull.set_input("Object", pull_obj)


class CabinetDrawerFront(CabinetFront):

    door_pull_location = "Base"
    
    def create(self,name):
        super().create(name)
        self.obj['IS_DRAWER_FRONT'] = True
        props = bpy.context.scene.hb_frameless

        self.add_property("False Front",'CHECKBOX', False)
        self.add_property("Center Pull",'CHECKBOX',props.center_pulls_on_drawer_front)
        self.add_property('Handle Horizontal Location', 'DISTANCE', props.pull_vertical_location_drawers)
        
        pull_obj = self.get_pull_object(pull_type='drawer')
        pull_length = pull_obj.dimensions.x if pull_obj else 0.1016  # Default to 4 inches
        self.add_property('Pull Length', 'DISTANCE', pull_length)


        pull = GeoNodeHardware()
        pull.create('Pull')
        pull.obj['IS_CABINET_PULL'] = True
        pull.obj.parent = self.obj
        pull.obj.rotation_euler.x = math.radians(-90)
        pull.obj.rotation_euler.z = math.radians(90)
        if pull_obj:
            pull.set_input("Object",pull_obj)

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
        

        
        # Add drawer box properties if not present
        if 'Drawer Box Side Clearance' not in self.obj:
            self.add_property('Drawer Box Side Clearance', 'DISTANCE', inch(0.5))
            self.add_property('Drawer Box Top Clearance', 'DISTANCE', inch(0.75))
            self.add_property('Drawer Box Rear Clearance', 'DISTANCE', inch(1.0))
            self.add_property('Drawer Box Bottom Clearance', 'DISTANCE', inch(.5))
        
        
        drawer_box = GeoNodeDrawerBox()
        drawer_box.create('Drawer Box')
        drawer_box.obj['IS_FRAMELESS_INTERIOR_PART'] = True
        drawer_box.obj['MENU_ID'] = 'HOME_BUILDER_MT_interior_part_commands'
        drawer_box.obj.parent = self.obj
        drawer_box.obj.rotation_euler.x = math.radians(-90)
        drawer_box.obj.rotation_euler.z = math.radians(-90)


class CabinetPulloutFront(CabinetFront):
    """Pullout front - uses Base/Tall/Upper pull location like doors.
    Unlike drawer fronts, pullout fronts never use centered pulls.
    """

    door_pull_location = "Base"
    
    def create(self, name):
        super().create(name)
        self.obj['IS_PULLOUT_FRONT'] = True
        props = bpy.context.scene.hb_frameless

        self.add_property("False Front", 'CHECKBOX', False)

        pull_location_index = 0
        if self.door_pull_location == "Base":
            pull_location_index = 0
        elif self.door_pull_location == "Tall":
            pull_location_index = 1
        elif self.door_pull_location == "Upper":
            pull_location_index = 2

        self.add_property("Pull Location", 'COMBOBOX', pull_location_index, combobox_items=["Base", "Tall", "Upper"])
        self.add_property('Base Pull Vertical Location', 'DISTANCE', props.pull_vertical_location_base)
        self.add_property('Tall Pull Vertical Location', 'DISTANCE', props.pull_vertical_location_tall)
        self.add_property('Upper Pull Vertical Location', 'DISTANCE', props.pull_vertical_location_upper)

        pull_obj = self.get_pull_object(pull_type='drawer')
        pull_length = pull_obj.dimensions.x if pull_obj else 0.1016
        self.add_property('Pull Length', 'DISTANCE', pull_length)


        pull = GeoNodeHardware()
        pull.create('Pull')
        pull.obj['IS_CABINET_PULL'] = True
        pull.obj.parent = self.obj
        pull.obj.rotation_euler.x = math.radians(-90)
        pull.obj.rotation_euler.z = math.radians(90)
        if pull_obj:
            pull.set_input("Object", pull_obj)

    def add_drawer_box(self):
        """Add a drawer box to this pullout front."""
        props = bpy.context.scene.hb_frameless
        
        if not props.include_drawer_boxes:
            return
        
        if self.obj.get('False Front', False):
            return

        for child in self.obj.children:
            if child.get('IS_DRAWER_BOX'):
                return


        
        if 'Drawer Box Side Clearance' not in self.obj:
            self.add_property('Drawer Box Side Clearance', 'DISTANCE', inch(0.5))
            self.add_property('Drawer Box Top Clearance', 'DISTANCE', inch(0.75))
            self.add_property('Drawer Box Rear Clearance', 'DISTANCE', inch(1.0))
            self.add_property('Drawer Box Bottom Clearance', 'DISTANCE', inch(.5))
        
        
        drawer_box = GeoNodeDrawerBox()
        drawer_box.create('Drawer Box')
        drawer_box.obj['IS_FRAMELESS_INTERIOR_PART'] = True
        drawer_box.obj['MENU_ID'] = 'HOME_BUILDER_MT_interior_part_commands'
        drawer_box.obj.parent = self.obj
        drawer_box.obj.rotation_euler.x = math.radians(-90)
        drawer_box.obj.rotation_euler.z = math.radians(-90)


# =============================================================================
# CORNER CABINETS
# =============================================================================


def add_section_interior(section_obj, section_type):
    """Give a division section its own interior: adjustable shelves, or
    an items interior (roll-outs, tray dividers, bar storage...). EMPTY
    and unknown types leave the section open. Sized by the solver."""
    from . import interior_items
    if section_type == 'SHELVES':
        interior = CabinetShelves()
    elif section_type in interior_items.INTERIOR_TYPE_KINDS:
        interior = CabinetInteriorItems()
        interior.seed_kind = interior_items.INTERIOR_TYPE_KINDS[section_type]
    else:
        return None
    interior.create('Interior')
    interior.obj.parent = section_obj
    return interior.obj


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

        # Section heights live on a calculator: the solver reads them and
        # fills in the equal ones from whatever height is left over.
        empty_obj = self.add_empty("Calc Object")
        empty_obj.empty_display_size = .001
        section_calculator = self.obj.home_builder.add_calculator("Section Calculator", empty_obj)
        for i in range(1, self.splitter_qty + 2):
            section_calculator.add_calculator_prompt('Section ' + str(i) + ' Height')

        # Add horizontal dividers and sections from top to bottom
        for i in range(1, self.splitter_qty + 2):
            if i < self.splitter_qty + 1:
                divider = CabinetPart()
                divider.create('Interior Divider ' + str(i))
                divider.obj['IS_FRAMELESS_INTERIOR_PART'] = True
                divider.obj['MENU_ID'] = 'HOME_BUILDER_MT_interior_part_commands'
                divider.obj.parent = self.obj
                solver_frameless.tag_split_part(divider.obj, 'SPLITTER', i)

            section = InteriorSection()
            section.create('Section ' + str(i))
            section.obj.parent = self.obj
            solver_frameless.tag_split_part(section.obj, 'OPENING', i)

            # Add interior type to section based on section_types
            if len(self.section_types) > i - 1:
                section_type = self.section_types[i - 1]
                add_section_interior(section.obj, section_type)

        # Set section sizes
        for i in range(1, self.splitter_qty + 2):
            if len(self.section_sizes) > i - 1 and self.section_sizes[i - 1] != 0:
                sh = section_calculator.get_calculator_prompt('Section ' + str(i) + ' Height')
                sh.equal = False
                sh.distance_value = self.section_sizes[i - 1]


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

        # Section widths live on a calculator: the solver reads them and
        # fills in the equal ones from whatever width is left over.
        empty_obj = self.add_empty("Calc Object")
        empty_obj.empty_display_size = .001
        section_calculator = self.obj.home_builder.add_calculator("Section Calculator", empty_obj)
        for i in range(1, self.splitter_qty + 2):
            section_calculator.add_calculator_prompt('Section ' + str(i) + ' Width')

        # Add vertical dividers and sections from left to right
        for i in range(1, self.splitter_qty + 2):
            if i < self.splitter_qty + 1:
                divider = CabinetPart()
                divider.create('Interior Divider ' + str(i))
                divider.obj['IS_FRAMELESS_INTERIOR_PART'] = True
                divider.obj['MENU_ID'] = 'HOME_BUILDER_MT_interior_part_commands'
                divider.obj.parent = self.obj
                divider.obj.rotation_euler.y = math.radians(-90)
                solver_frameless.tag_split_part(divider.obj, 'SPLITTER', i)

            section = InteriorSection()
            section.create('Section ' + str(i))
            section.obj.parent = self.obj
            solver_frameless.tag_split_part(section.obj, 'OPENING', i)

            # Add interior type to section
            if len(self.section_types) > i - 1:
                section_type = self.section_types[i - 1]
                add_section_interior(section.obj, section_type)

        # Set section sizes
        for i in range(1, self.splitter_qty + 2):
            if len(self.section_sizes) > i - 1 and self.section_sizes[i - 1] != 0:
                sw = section_calculator.get_calculator_prompt('Section ' + str(i) + ' Width')
                sw.equal = False
                sw.distance_value = self.section_sizes[i - 1]


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

    def add_corner_modifier(self, part):
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

        The doors and their pulls are placed by the solver.
        """
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

        # Overlay values, written by the solver from the prompts above
        overlay_obj = self.add_empty('Corner Overlay Calc')
        overlay_obj.home_builder.add_property("Overlay Top", 'DISTANCE', 0.0)
        overlay_obj.home_builder.add_property("Overlay Bottom", 'DISTANCE', 0.0)
        overlay_obj.home_builder.add_property("Overlay Outer", 'DISTANCE', 0.0)
        overlay_obj[solver_frameless.PART_ROLE_KEY] = 'CORNER_OVERLAY'

        # Door swing: determines which door gets a pull handle
        self.add_property("Door Swing", 'COMBOBOX', 0, combobox_items=["Left", "Right"])

        # --- Left door (notch X-face) ---
        left_door = CabinetDoor()
        left_door.door_pull_location = self.door_pull_location
        left_door.create("Left Door")
        left_door.obj.parent = self.obj
        left_door.obj.rotation_euler.y = math.radians(-90)
        left_door.obj.rotation_euler.z = math.radians(180)
        left_door.obj[solver_frameless.PART_ROLE_KEY] = 'LEFT_DOOR'

        # --- Right door (notch Y-face) ---
        right_door = CabinetDoor()
        right_door.door_pull_location = self.door_pull_location
        right_door.create("Right Door")
        right_door.obj.parent = self.obj
        right_door.obj.rotation_euler.x = math.radians(90)
        right_door.obj.rotation_euler.y = math.radians(-90)
        right_door.set_input("Mirror Y", True)
        right_door.obj[solver_frameless.PART_ROLE_KEY] = 'RIGHT_DOOR'

    def _add_corner_leg_levelers(self):
        """Add leg leveler hardware at the four outer corners of the L."""
        ll_obj = self._get_leg_leveler_object()
        if ll_obj is None:
            return
        for name, role in (('Leg Leveler BL', 'LEG_LEVELER_BL'),
                           ('Leg Leveler BR', 'LEG_LEVELER_BR'),
                           ('Leg Leveler FL', 'LEG_LEVELER_FL'),
                           ('Leg Leveler FR', 'LEG_LEVELER_FR')):
            ll = GeoNodeHardware()
            ll.create(name)
            ll.obj['IS_LEG_LEVELER'] = True
            ll.obj[solver_frameless.PART_ROLE_KEY] = role
            ll.obj.parent = self.obj
            ll.set_input("Object", ll_obj)
            ll.obj.location.z = 0

    def _add_corner_top_bottom(self):
        bottom = self._add_carcass_part('Bottom', 'BOTTOM', mirror='Y')
        self.add_corner_modifier(bottom)
        top = self._add_carcass_part('Top', 'TOP', mirror='YZ')
        self.add_corner_modifier(top)

    def create_corner_base_carcass(self, name):
        """Create the corner base cabinet carcass.

        Shared by all corner base cabinet types (diagonal, pie cut).
        The top/bottom panel shape is determined by add_corner_modifier().
        """
        super().create_cabinet(name)

        self.add_properties_common()
        self.add_properties_toe_kick()
        self.add_properties_corner()
        self.obj[solver_frameless.CARCASS_KEY] = 'CORNER_BASE'

        # Set dimensions - corner size determines X and Y
        self.set_input('Dim X', self.corner_size)
        self.set_input('Dim Y', self.corner_size)
        self.set_input('Dim Z', self.height)

        toe_kick_type = self.obj.get('Toe Kick Type', 0)
        side_cls = CabinetSideNotched if toe_kick_type == 0 else CabinetPart

        # Sides: the left wing runs back along -Y, the right wing along +X.
        self._add_carcass_part('Left Side', 'LEFT_SIDE', side_cls,
                               rotation=(0, -90, -90))
        self._add_carcass_part('Right Side', 'RIGHT_SIDE', side_cls,
                               rotation=(0, -90, 0), mirror='Y')
        self._add_carcass_part('Left Back', 'LEFT_BACK', rotation=(0, -90, 0),
                               mirror='YZ')
        self._add_carcass_part('Right Back', 'RIGHT_BACK', rotation=(-90, 0, 0),
                               mirror='YZ')
        self._add_corner_top_bottom()

        if toe_kick_type == 0:  # Notch Ends to Floor
            self._add_carcass_part('Left Toe Kick', 'LEFT_TOE_KICK',
                                   rotation=(-90, 0, 90), mirror='Y')
            self._add_carcass_part('Right Toe Kick', 'RIGHT_TOE_KICK',
                                   rotation=(-90, 0, 0), mirror='XY')
        elif toe_kick_type == 1:  # Ladder Style
            ladder = LadderBaseCage()
            ladder.create('Ladder Base')
            ladder.obj.parent = self.obj
            ladder.obj[solver_frameless.PART_ROLE_KEY] = 'LADDER_BASE'
        elif toe_kick_type == 3:  # Leg Levelers
            self._add_corner_leg_levelers()

        solver_frameless.recalculate_cabinet(self.obj)

    def create_corner_upper_carcass(self, name):
        """Create the corner upper cabinet carcass.

        Similar to base but without toe kicks or notched sides.
        Bottom sits at Z=0, sides are plain CabinetPart.
        """
        super().create_cabinet(name)

        self.add_properties_common()
        self.add_properties_corner()
        self.obj[solver_frameless.CARCASS_KEY] = 'CORNER_UPPER'

        # Set dimensions
        self.set_input('Dim X', self.corner_size)
        self.set_input('Dim Y', self.corner_size)
        self.set_input('Dim Z', self.height)

        self._add_carcass_part('Left Side', 'LEFT_SIDE', rotation=(0, -90, -90))
        self._add_carcass_part('Right Side', 'RIGHT_SIDE', rotation=(0, -90, 0),
                               mirror='Y')
        self._add_carcass_part('Left Back', 'LEFT_BACK', rotation=(0, -90, 0),
                               mirror='YZ')
        self._add_carcass_part('Right Back', 'RIGHT_BACK', rotation=(-90, 0, 0),
                               mirror='YZ')
        self._add_corner_top_bottom()

        solver_frameless.recalculate_cabinet(self.obj)


class DiagonalCornerBaseCabinet(CornerCabinet):
    """Diagonal corner base cabinet - 45 degree angled front."""

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

    def add_corner_modifier(self, part):
        """Diagonal uses CPM_CHAMFER to cut a 45 degree angle; the solver
        sizes it."""
        chamfer = part.add_part_modifier('CPM_CHAMFER', 'Chamfer')
        chamfer.set_input('Flip X', True)


def _add_pie_cut_cage_notch(cabinet):
    """Notch the cage itself so its wireframe matches the L-shape; the
    solver sizes it."""
    cpm = CabinetPartModifier(cabinet.obj)
    cpm.add_node('CPM_CORNERNOTCH', 'Corner Notch')
    cpm.set_input('Flip X', True)
    cpm.set_input('Flip Y', True)


def _add_pie_cut_part_notch(part):
    """Pie cut uses CPM_CORNERNOTCH for a rectangular notch; the solver
    sizes it."""
    notch = part.add_part_modifier('CPM_CORNERNOTCH', 'Corner Notch')
    notch.set_input('Flip X', True)
    notch.set_input('Flip Y', True)


class PieCutCornerBaseCabinet(CornerCabinet):
    """Pie cut corner base cabinet - rectangular notch, two fronts at 90 degrees."""

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
        _add_pie_cut_cage_notch(self)
        self.add_corner_doors()
        solver_frameless.recalculate_cabinet(self.obj)

    def add_corner_modifier(self, part):
        _add_pie_cut_part_notch(part)


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
        _add_pie_cut_cage_notch(self)
        self.add_corner_doors()
        solver_frameless.recalculate_cabinet(self.obj)

    def add_corner_modifier(self, part):
        _add_pie_cut_part_notch(part)


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
        _add_pie_cut_cage_notch(self)
        self.add_corner_doors()
        solver_frameless.recalculate_cabinet(self.obj)

    def add_corner_modifier(self, part):
        _add_pie_cut_part_notch(part)
