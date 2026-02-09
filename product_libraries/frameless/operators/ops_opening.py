import bpy
from .. import types_frameless
from .. import props_hb_frameless
from .... import hb_utils, hb_types, units


def get_door_height(door_obj):
    """Get the door's height (Length) from the geometry node modifier.
    
    Args:
        door_obj: The door object
        
    Returns:
        Door height in meters, or 0 if not found
    """
    door = hb_types.GeoNodeObject(door_obj)
    if door.has_input('Length'):
        return door.get_input('Length')
    return 0


def get_pull_location_from_position(door_obj):
    """Determine pull location based on the door's world position and size.
    
    Uses the door's world Z position to determine whether the pull should be 
    at Base (top of door), Upper (bottom of door), or Tall (middle of door) 
    position. Also checks if the door is tall enough for the Tall pull location.
    
    Args:
        door_obj: The door object (must have world matrix calculated)
        
    Returns:
        'Base', 'Tall', or 'Upper'
    """
    # Get the door's world position
    world_matrix = door_obj.matrix_world
    
    # Get Z position of door bottom in world space
    door_bottom_z = world_matrix.translation.z
    
    # Thresholds in meters (converted from inches)
    BASE_THRESHOLD = units.inch(36)    # Below 36" from floor - use Base
    UPPER_THRESHOLD = units.inch(48)   # Above 48" from floor - use Upper
    
    # First determine location based on position
    if door_bottom_z < BASE_THRESHOLD:
        return 'Base'
    elif door_bottom_z >= UPPER_THRESHOLD:
        return 'Upper'
    else:
        # Would be Tall, but check if door is tall enough
        door_height = get_door_height(door_obj)
        tall_pull_location = door_obj.get('Tall Pull Vertical Location', units.inch(36))
        
        # If the door height is less than the tall pull vertical location,
        # the pull would be placed off the door - use Base or Upper instead
        if door_height > 0 and door_height < tall_pull_location:
            # Door is too short for Tall - decide based on position
            # If closer to floor, use Base; if higher up, use Upper
            if door_bottom_z < units.inch(42):
                return 'Base'
            else:
                return 'Upper'
        
        return 'Tall'


def assign_pull_locations_to_cabinet(cabinet_bp):
    """Assign appropriate pull locations to all doors in a cabinet.
    
    Scans all door fronts in the cabinet and assigns pull locations
    based on their world positions and sizes.
    
    Args:
        cabinet_bp: The cabinet base point object
    """
    # Update the scene to ensure world matrices are current
    bpy.context.view_layer.update()
    
    for child in cabinet_bp.children_recursive:
        if child.get('IS_DOOR_FRONT'):
            pull_location = get_pull_location_from_position(child)
            
            # Set the Pull Location property (0=Base, 1=Tall, 2=Upper)
            pull_index = {'Base': 0, 'Tall': 1, 'Upper': 2}.get(pull_location, 0)
            
            # Set the Pull Location directly on the object
            if 'Pull Location' in child:
                child['Pull Location'] = pull_index


class hb_frameless_OT_change_bay_opening(bpy.types.Operator):
    bl_idname = "hb_frameless.change_bay_opening"
    bl_label = "Change Bay Opening"
    bl_description = "Change the type of opening in this bay"
    bl_options = {'UNDO'}

    opening_type: bpy.props.EnumProperty(
        name="Opening Type",
        items=[
            # Doors
            ('LEFT_DOOR', "Left Door", "Single left swing door"),
            ('RIGHT_DOOR', "Right Door", "Single right swing door"),
            ('DOUBLE_DOORS', "Double Doors", "Double swing doors"),
            ('FLIP_UP_DOOR', "Flip Up Door", "Door hinged at top, swings up"),
            # Stacked Doors
            ('LEFT_STACKED_DOOR', "Left Stacked Door", "Two left swing doors stacked"),
            ('RIGHT_STACKED_DOOR', "Right Stacked Door", "Two right swing doors stacked"),
            ('DOUBLE_STACKED_DOOR', "Double Stacked Door", "Two double doors stacked"),
            ('LEFT_3_STACKED_DOOR', "Left 3 Stacked Door", "Three left swing doors stacked"),
            ('RIGHT_3_STACKED_DOOR', "Right 3 Stacked Door", "Three right swing doors stacked"),
            ('DOUBLE_3_STACKED_DOOR', "Double 3 Stacked Door", "Three double doors stacked"),
            # Drawer/Door Combos (Base)
            ('DOOR_DRAWER', "1 Drawer 1 Door", "One drawer over one door"),
            ('1_DRAWER_2_DOOR', "1 Drawer 2 Door", "One drawer over double doors"),
            ('2_DRAWER_2_DOOR', "2 Drawer 2 Door", "Two drawers over double doors"),
            # Drawers
            ('SINGLE_DRAWER', "Single Drawer", "Single drawer"),
            ('2_DRAWER_STACK', "2 Drawer Stack", "Two equal drawers"),
            ('3_DRAWER_STACK', "3 Drawer Stack", "Three equal drawers"),
            ('4_DRAWER_STACK', "4 Drawer Stack", "Four equal drawers"),
            # Pullouts
            ('PULLOUT', "Pullout", "Pullout with pull at top"),
            ('PULLOUT_WITH_DRAWER', "Pullout with Drawer", "Pullout with drawer above"),
            ('TALL_PULLOUT', "Tall Pullout", "Full height pullout"),
            ('DOORS_WITH_TALL_PULLOUT', "Doors with Tall Pullout", "Doors above tall pullout"),
            # Upper Door/Drawer Combos
            ('DOORS_WITH_1_DRAWER', "Doors with 1 Drawer", "Doors above one drawer"),
            ('DOORS_WITH_2_DRAWER', "Doors with 2 Drawers", "Doors above two drawers"),
            ('DOORS_WITH_3_DRAWER', "Doors with 3 Drawers", "Doors above three drawers"),
            ('DOORS_WITH_PULLOUT', "Doors with Pullout", "Doors above pullout"),
            # Other
            ('FALSE_FRONT', "False Front", "Decorative panel with no hardware"),
            ('MICROWAVE_DRAWER', "Microwave with Drawer", "Microwave opening with drawer below"),
            ('OPEN', "Open", "Open with no front"),
            ('OPEN_WITH_SHELVES', "Open With Shelves", "Open with adjustable shelves"),
            ('APPLIANCE', "Appliance", "Built-in appliance opening"),
            ('DOUBLE_APPLIANCE', "Double Appliance", "Two appliance openings stacked"),
        ],
        default='LEFT_DOOR'
    ) # type: ignore
    
    appliance_name: bpy.props.StringProperty(
        name="Appliance Name",
        default="Appliance"
    ) # type: ignore

    @classmethod
    def poll(cls, context):
        # Allow if any selected object is a bay
        for obj in context.selected_objects:
            if 'IS_FRAMELESS_BAY_CAGE' in obj:
                return True
            bay_bp = hb_utils.get_bay_bp(obj)
            if bay_bp is not None:
                return True
        return False

    def delete_bay_children(self, bay_obj):
        """Delete all children of the bay."""
        children = list(bay_obj.children)
        for child in children:
            self.delete_bay_children(child)
            bpy.data.objects.remove(child, do_unlink=True)

    def add_cage_to_bay(self, bay, cage):
        """Add a cage to the bay with proper dimension drivers."""
        cage.create()
        cage.obj.parent = bay.obj
        dim_x = bay.var_input('Dim X', 'dim_x')
        dim_y = bay.var_input('Dim Y', 'dim_y')
        dim_z = bay.var_input('Dim Z', 'dim_z')
        cage.driver_input('Dim X', 'dim_x', [dim_x])
        cage.driver_input('Dim Y', 'dim_y', [dim_y])
        cage.driver_input('Dim Z', 'dim_z', [dim_z])

    def get_cabinet_type(self, bay_obj):
        """Get the cabinet type from the cabinet parent."""
        cabinet_bp = hb_utils.get_cabinet_bp(bay_obj)
        if cabinet_bp:
            return cabinet_bp.get('CABINET_TYPE', 'BASE')
        return 'BASE'

    def get_pull_location(self, cabinet_type, position, total_openings):
        """Determine pull location based on cabinet type and opening position.
        
        Args:
            cabinet_type: 'BASE', 'UPPER', or 'TALL'
            position: 0-indexed position from top (0 = top opening)
            total_openings: Total number of openings in the split
            
        Returns:
            'Base', 'Tall', or 'Upper'
        """
        if cabinet_type == 'BASE':
            return 'Base'
        elif cabinet_type == 'UPPER':
            return 'Upper'
        elif cabinet_type == 'TALL':
            if total_openings == 1:
                return 'Tall'
            elif total_openings == 2:
                # Top opening uses Upper, bottom uses Base
                return 'Upper' if position == 0 else 'Base'
            else:
                # 3+ openings: top=Upper, middle=Tall, bottom=Base
                if position == 0:
                    return 'Upper'
                elif position == total_openings - 1:
                    return 'Base'
                else:
                    return 'Tall'
        return 'Base'

    def create_doors(self, bay, door_swing):
        """Create doors opening with specified swing direction."""
        cabinet_type = self.get_cabinet_type(bay.obj)
        
        doors = types_frameless.Doors()
        doors.door_pull_location = self.get_pull_location(cabinet_type, 0, 1)
        
        self.add_cage_to_bay(bay, doors)
        
        # Set door swing: 0=Left, 1=Right, 2=Double
        doors.obj['Door Swing'] = door_swing

    def create_drawer(self, bay):
        """Create single drawer opening."""
        drawer = types_frameless.Drawer()
        self.add_cage_to_bay(bay, drawer)

    def create_pullout(self, bay):
        """Create pullout opening (drawer with pull at top)."""
        pullout = types_frameless.Pullout()
        self.add_cage_to_bay(bay, pullout)

    def create_flip_up_door(self, bay):
        """Create flip up door opening (hinged at top, swings up)."""
        flip_up = types_frameless.FlipUpDoor()
        self.add_cage_to_bay(bay, flip_up)

    def create_false_front(self, bay):
        """Create false front (decorative panel with no hardware)."""
        false_front = types_frameless.FalseFront()
        self.add_cage_to_bay(bay, false_front)

    def create_appliance(self, bay, appliance_name="Appliance"):
        """Create appliance opening with centered text."""
        appliance = types_frameless.Appliance()
        appliance.appliance_name = appliance_name
        self.add_cage_to_bay(bay, appliance)

    def create_built_in_appliance(self, bay):
        """Create built-in appliance: doors on top, appliance 30" in center, doors on bottom."""
        cabinet_type = self.get_cabinet_type(bay.obj)
        
        # Top doors (position 0 of 3)
        top_doors = types_frameless.Doors()
        top_doors.door_pull_location = self.get_pull_location(cabinet_type, 0, 3)
        top_doors.half_overlay_bottom = True
        
        # Center appliance (position 1 of 3)
        appliance = types_frameless.Appliance()
        appliance.appliance_name = "Appliance"
        
        # Bottom doors (position 2 of 3)
        bottom_doors = types_frameless.Doors()
        bottom_doors.door_pull_location = self.get_pull_location(cabinet_type, 2, 3)
        bottom_doors.half_overlay_top = True
        
        splitter = types_frameless.SplitterVertical()
        splitter.splitter_qty = 2
        splitter.opening_sizes = [0, units.inch(30), 0]  # Equal top/bottom, 30" center
        splitter.opening_inserts = [top_doors, appliance, bottom_doors]
        self.add_cage_to_bay(bay, splitter)
        
        # Set double doors
        for child in bay.obj.children_recursive:
            if 'Door Swing' in child:
                child['Door Swing'] = 2

    def create_built_in_double_appliance(self, bay):
        """Create built-in double appliance: doors on top, two appliances in center, drawer on bottom."""
        props = bpy.context.scene.hb_frameless
        cabinet_type = self.get_cabinet_type(bay.obj)
        
        # Top doors (position 0 of 4)
        top_doors = types_frameless.Doors()
        top_doors.door_pull_location = self.get_pull_location(cabinet_type, 0, 4)
        top_doors.half_overlay_bottom = True
        
        # First appliance (position 1 of 4)
        appliance1 = types_frameless.Appliance()
        appliance1.appliance_name = "Appliance"
        
        # Second appliance (position 2 of 4)
        appliance2 = types_frameless.Appliance()
        appliance2.appliance_name = "Appliance"
        
        # Bottom drawer (position 3 of 4)
        drawer = types_frameless.Drawer()
        drawer.half_overlay_top = True
        
        splitter = types_frameless.SplitterVertical()
        splitter.splitter_qty = 3
        splitter.opening_sizes = [0, units.inch(30), units.inch(30), props.top_drawer_front_height]
        splitter.opening_inserts = [top_doors, appliance1, appliance2, drawer]
        self.add_cage_to_bay(bay, splitter)
        
        # Set double doors
        for child in bay.obj.children_recursive:
            if 'Door Swing' in child:
                child['Door Swing'] = 2

    def create_open_with_shelves(self, bay):
        """Create open opening with adjustable shelves."""
        open_shelves = types_frameless.OpenWithShelves()
        self.add_cage_to_bay(bay, open_shelves)

    def create_stacked_doors(self, bay, door_swing, stack_count=2):
        """Create stacked doors (2 or 3 high).
        
        Args:
            bay: The bay to add to
            door_swing: 0=Left, 1=Right, 2=Double
            stack_count: Number of doors stacked (2 or 3)
        """
        cabinet_type = self.get_cabinet_type(bay.obj)
        
        # Create door inserts for each opening with proper half overlays and pull locations
        inserts = []
        for i in range(stack_count):
            doors = types_frameless.Doors()
            doors.door_pull_location = self.get_pull_location(cabinet_type, i, stack_count)
            
            # Set half overlays: top door needs bottom, bottom door needs top, middle needs both
            if i > 0:  # Not the top door
                doors.half_overlay_top = True
            if i < stack_count - 1:  # Not the bottom door
                doors.half_overlay_bottom = True
            
            inserts.append(doors)
        
        splitter = types_frameless.SplitterVertical()
        splitter.splitter_qty = stack_count - 1
        splitter.opening_sizes = [0] * stack_count  # Equal sizes
        splitter.opening_inserts = inserts
        self.add_cage_to_bay(bay, splitter)
        
        # Set door swing after creation
        for child in bay.obj.children_recursive:
            if 'Door Swing' in child:
                child['Door Swing'] = door_swing

    def create_1_drawer_2_door(self, bay):
        """Create 1 drawer over double doors (base cabinet)."""
        props = bpy.context.scene.hb_frameless
        cabinet_type = self.get_cabinet_type(bay.obj)
        
        drawer = types_frameless.Drawer()
        drawer.half_overlay_bottom = True
        
        doors = types_frameless.Doors()
        doors.door_pull_location = self.get_pull_location(cabinet_type, 1, 2)  # position 1 of 2
        doors.half_overlay_top = True
        
        splitter = types_frameless.SplitterVertical()
        splitter.splitter_qty = 1
        splitter.opening_sizes = [props.top_drawer_front_height, 0]
        splitter.opening_inserts = [drawer, doors]
        self.add_cage_to_bay(bay, splitter)
        
        # Set double doors
        for child in bay.obj.children_recursive:
            if 'Door Swing' in child:
                child['Door Swing'] = 2

    def create_2_drawer_2_door(self, bay):
        """Create 2 horizontal drawers (side by side) over double doors (base cabinet)."""
        props = bpy.context.scene.hb_frameless
        cabinet_type = self.get_cabinet_type(bay.obj)
        
        # Create horizontal splitter with two drawers side by side
        horiz_splitter = types_frameless.SplitterHorizontal()
        horiz_splitter.splitter_qty = 1
        horiz_splitter.opening_sizes = [0, 0]  # Equal widths
        
        drawer1 = types_frameless.Drawer()
        drawer1.half_overlay_right = True
        drawer1.half_overlay_bottom = True
        drawer2 = types_frameless.Drawer()
        drawer2.half_overlay_left = True
        drawer2.half_overlay_bottom = True
        horiz_splitter.opening_inserts = [drawer1, drawer2]
        
        # Create doors for bottom
        doors = types_frameless.Doors()
        doors.door_pull_location = self.get_pull_location(cabinet_type, 1, 2)  # position 1 of 2
        doors.half_overlay_top = True
        
        # Create vertical splitter with horizontal drawer section on top, doors below
        splitter = types_frameless.SplitterVertical()
        splitter.splitter_qty = 1
        splitter.opening_sizes = [props.top_drawer_front_height, 0]
        splitter.opening_inserts = [horiz_splitter, doors]
        self.add_cage_to_bay(bay, splitter)
        
        # Set double doors
        for child in bay.obj.children_recursive:
            if 'Door Swing' in child:
                child['Door Swing'] = 2

    def create_pullout_with_drawer(self, bay):
        """Create pullout with drawer above."""
        props = bpy.context.scene.hb_frameless
        
        drawer = types_frameless.Drawer()
        drawer.half_overlay_bottom = True
        
        pullout = types_frameless.Pullout()
        pullout.half_overlay_top = True
        
        splitter = types_frameless.SplitterVertical()
        splitter.splitter_qty = 1
        splitter.opening_sizes = [props.top_drawer_front_height, 0]
        splitter.opening_inserts = [drawer, pullout]
        self.add_cage_to_bay(bay, splitter)

    def create_microwave_drawer(self, bay):
        """Create microwave opening with drawer below."""
        splitter = types_frameless.SplitterVertical()
        splitter.splitter_qty = 1
        splitter.opening_sizes = [0, units.inch(6)]  # Microwave space, small drawer
        
        appliance = types_frameless.Appliance()
        appliance.appliance_name = "Microwave"
        drawer = types_frameless.Drawer()
        
        splitter.opening_inserts = [appliance, drawer]
        self.add_cage_to_bay(bay, splitter)

    def create_doors_with_drawers(self, bay, drawer_count=1):
        """Create doors above drawers (upper cabinet style).
        
        Args:
            bay: The bay to add to
            drawer_count: Number of drawers below (1, 2, or 3)
        """
        props = bpy.context.scene.hb_frameless
        cabinet_type = self.get_cabinet_type(bay.obj)
        total_openings = drawer_count + 1
        
        # Doors on top with half overlay on bottom
        doors = types_frameless.Doors()
        doors.door_pull_location = self.get_pull_location(cabinet_type, 0, total_openings)  # position 0
        doors.half_overlay_bottom = True
        
        inserts = [doors]
        sizes = [0]  # Doors get remaining space
        
        # Add drawers with proper half overlays
        for i in range(drawer_count):
            drawer = types_frameless.Drawer()
            drawer.half_overlay_top = True
            if i < drawer_count - 1:  # Not the last drawer
                drawer.half_overlay_bottom = True
            inserts.append(drawer)
            sizes.append(props.top_drawer_front_height)
        
        splitter = types_frameless.SplitterVertical()
        splitter.splitter_qty = drawer_count
        splitter.opening_sizes = sizes
        splitter.opening_inserts = inserts
        self.add_cage_to_bay(bay, splitter)

    def create_doors_with_pullout(self, bay):
        """Create doors above pullout (upper cabinet style)."""
        cabinet_type = self.get_cabinet_type(bay.obj)
        
        doors = types_frameless.Doors()
        doors.door_pull_location = self.get_pull_location(cabinet_type, 0, 2)  # position 0 of 2
        doors.half_overlay_bottom = True
        
        pullout = types_frameless.Pullout()
        pullout.half_overlay_top = True
        
        splitter = types_frameless.SplitterVertical()
        splitter.splitter_qty = 1
        splitter.opening_sizes = [0, units.inch(8)]  # Doors, pullout
        splitter.opening_inserts = [doors, pullout]
        self.add_cage_to_bay(bay, splitter)

    def create_tall_pullout(self, bay):
        """Create full height pullout (tall cabinet)."""
        pullout = types_frameless.Pullout()
        self.add_cage_to_bay(bay, pullout)

    def create_doors_with_tall_pullout(self, bay, door_swing=2):
        """Create doors above tall pullout (tall cabinet)."""
        cabinet_type = self.get_cabinet_type(bay.obj)
        
        doors = types_frameless.Doors()
        doors.door_pull_location = self.get_pull_location(cabinet_type, 0, 2)  # position 0 of 2
        doors.half_overlay_bottom = True
        
        pullout = types_frameless.Pullout()
        pullout.half_overlay_top = True
        
        splitter = types_frameless.SplitterVertical()
        splitter.splitter_qty = 1
        splitter.opening_sizes = [units.inch(18), 0]  # Doors, tall pullout
        splitter.opening_inserts = [doors, pullout]
        self.add_cage_to_bay(bay, splitter)
        
        # Set door swing
        for child in bay.obj.children_recursive:
            if 'Door Swing' in child:
                child['Door Swing'] = door_swing

    def create_door_drawer(self, bay):
        """Create door/drawer combo (drawer on top, single door below)."""
        props = bpy.context.scene.hb_frameless
        cabinet_type = self.get_cabinet_type(bay.obj)
        
        drawer = types_frameless.Drawer()
        drawer.half_overlay_bottom = True
        
        door = types_frameless.Doors()
        door.half_overlay_top = True
        door.door_pull_location = self.get_pull_location(cabinet_type, 1, 2)  # position 1 of 2

        splitter = types_frameless.SplitterVertical()
        splitter.splitter_qty = 1
        splitter.opening_sizes = [props.top_drawer_front_height, 0]
        splitter.opening_inserts = [drawer, door]
        self.add_cage_to_bay(bay, splitter)
        
        # Set single door (left swing)
        for child in bay.obj.children_recursive:
            if 'Door Swing' in child:
                child['Door Swing'] = 0

    def create_drawer_stack(self, bay, count):
        """Create a stack of drawers."""
        props = bpy.context.scene.hb_frameless
        
        # 2 drawers are always equal, 3+ use top_drawer_front_height setting
        if count == 2:
            top_drawer_height = 0  # Equal
        elif props.equal_drawer_stack_heights:
            top_drawer_height = 0
        else:
            top_drawer_height = props.top_drawer_front_height

        splitter = types_frameless.SplitterVertical()
        splitter.splitter_qty = count - 1
        
        for i in range(count):
            drawer = types_frameless.Drawer()
            if i == 0:
                drawer.half_overlay_bottom = True
                splitter.opening_sizes.append(top_drawer_height)
            elif i == count - 1:
                drawer.half_overlay_top = True
                splitter.opening_sizes.append(0)
            else:
                drawer.half_overlay_top = True
                drawer.half_overlay_bottom = True
                splitter.opening_sizes.append(0)
            splitter.opening_inserts.append(drawer)
        
        self.add_cage_to_bay(bay, splitter)

    def execute(self, context):
        # Collect all bay objects from selection
        bay_objs = []
        for obj in context.selected_objects:
            if 'IS_FRAMELESS_BAY_CAGE' in obj:
                bay_objs.append(obj)
            else:
                bay_bp = hb_utils.get_bay_bp(obj)
                if bay_bp and bay_bp not in bay_objs:
                    bay_objs.append(bay_bp)
        
        if not bay_objs:
            self.report({'ERROR'}, "Could not find any bays in selection")
            return {'CANCELLED'}
        
        # Track cabinets that need style reassignment
        cabinets_to_update = set()
        
        # Apply change to all selected bays
        for bay_obj in bay_objs:
            bay = types_frameless.CabinetBay(bay_obj)
            
            # Delete existing bay children
            self.delete_bay_children(bay_obj)
            
            # Create new opening based on type
            # Single Doors
            if self.opening_type == 'LEFT_DOOR':
                self.create_doors(bay, door_swing=0)
            elif self.opening_type == 'RIGHT_DOOR':
                self.create_doors(bay, door_swing=1)
            elif self.opening_type == 'DOUBLE_DOORS':
                self.create_doors(bay, door_swing=2)
            elif self.opening_type == 'FLIP_UP_DOOR':
                self.create_flip_up_door(bay)
            # Stacked Doors
            elif self.opening_type == 'LEFT_STACKED_DOOR':
                self.create_stacked_doors(bay, door_swing=0, stack_count=2)
            elif self.opening_type == 'RIGHT_STACKED_DOOR':
                self.create_stacked_doors(bay, door_swing=1, stack_count=2)
            elif self.opening_type == 'DOUBLE_STACKED_DOOR':
                self.create_stacked_doors(bay, door_swing=2, stack_count=2)
            elif self.opening_type == 'LEFT_3_STACKED_DOOR':
                self.create_stacked_doors(bay, door_swing=0, stack_count=3)
            elif self.opening_type == 'RIGHT_3_STACKED_DOOR':
                self.create_stacked_doors(bay, door_swing=1, stack_count=3)
            elif self.opening_type == 'DOUBLE_3_STACKED_DOOR':
                self.create_stacked_doors(bay, door_swing=2, stack_count=3)
            # Drawer/Door Combos (Base)
            elif self.opening_type == 'DOOR_DRAWER':
                self.create_door_drawer(bay)
            elif self.opening_type == '1_DRAWER_2_DOOR':
                self.create_1_drawer_2_door(bay)
            elif self.opening_type == '2_DRAWER_2_DOOR':
                self.create_2_drawer_2_door(bay)
            # Drawers
            elif self.opening_type == 'SINGLE_DRAWER':
                self.create_drawer(bay)
            elif self.opening_type == '2_DRAWER_STACK':
                self.create_drawer_stack(bay, 2)
            elif self.opening_type == '3_DRAWER_STACK':
                self.create_drawer_stack(bay, 3)
            elif self.opening_type == '4_DRAWER_STACK':
                self.create_drawer_stack(bay, 4)
            # Pullouts
            elif self.opening_type == 'PULLOUT':
                self.create_pullout(bay)
            elif self.opening_type == 'PULLOUT_WITH_DRAWER':
                self.create_pullout_with_drawer(bay)
            elif self.opening_type == 'TALL_PULLOUT':
                self.create_tall_pullout(bay)
            elif self.opening_type == 'DOORS_WITH_TALL_PULLOUT':
                self.create_doors_with_tall_pullout(bay)
            # Upper Door/Drawer Combos
            elif self.opening_type == 'DOORS_WITH_1_DRAWER':
                self.create_doors_with_drawers(bay, drawer_count=1)
            elif self.opening_type == 'DOORS_WITH_2_DRAWER':
                self.create_doors_with_drawers(bay, drawer_count=2)
            elif self.opening_type == 'DOORS_WITH_3_DRAWER':
                self.create_doors_with_drawers(bay, drawer_count=3)
            elif self.opening_type == 'DOORS_WITH_PULLOUT':
                self.create_doors_with_pullout(bay)
            # Other
            elif self.opening_type == 'FALSE_FRONT':
                self.create_false_front(bay)
            elif self.opening_type == 'MICROWAVE_DRAWER':
                self.create_microwave_drawer(bay)
            elif self.opening_type == 'OPEN':
                pass  # No children needed for open
            elif self.opening_type == 'OPEN_WITH_SHELVES':
                self.create_open_with_shelves(bay)
            elif self.opening_type == 'APPLIANCE':
                self.create_built_in_appliance(bay)
            elif self.opening_type == 'DOUBLE_APPLIANCE':
                self.create_built_in_double_appliance(bay)
            
            hb_utils.run_calc_fix(context, bay.obj)
            hb_utils.run_calc_fix(context, bay.obj)
            
            # Track cabinet for style reassignment
            cabinet_bp = hb_utils.get_cabinet_bp(bay_obj)
            if cabinet_bp:
                cabinets_to_update.add(cabinet_bp.name)
        
        # Assign pull locations based on world position
        for cabinet_name in cabinets_to_update:
            cabinet_bp = bpy.data.objects.get(cabinet_name)
            if cabinet_bp:
                assign_pull_locations_to_cabinet(cabinet_bp)
        
        # Reassign cabinet styles to apply materials to new parts
        for cabinet_name in cabinets_to_update:
            bpy.ops.hb_frameless.assign_cabinet_style(cabinet_name=cabinet_name)
        
        return {'FINISHED'}


class hb_frameless_OT_opening_prompts(bpy.types.Operator):
    bl_idname = "hb_frameless.opening_prompts"
    bl_label = "Opening Prompts"
    bl_description = "Edit opening properties"
    bl_options = {'UNDO'}

    door_swing: bpy.props.EnumProperty(
        name="Door Swing",
        items=[
            ('0', "Left", "Left swing"),
            ('1', "Right", "Right swing"),
            ('2', "Double", "Double doors"),
        ],
        default='2'
    ) # type: ignore

    inset_front: bpy.props.BoolProperty(name="Inset Front", default=False) # type: ignore
    half_overlay_top: bpy.props.BoolProperty(name="Half Overlay Top", default=False) # type: ignore
    half_overlay_bottom: bpy.props.BoolProperty(name="Half Overlay Bottom", default=False) # type: ignore
    half_overlay_left: bpy.props.BoolProperty(name="Half Overlay Left", default=False) # type: ignore
    half_overlay_right: bpy.props.BoolProperty(name="Half Overlay Right", default=False) # type: ignore

    opening = None

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj:
            if 'IS_FRAMELESS_OPENING_CAGE' in obj:
                return True
            opening_bp = hb_utils.get_opening_bp(obj)
            return opening_bp is not None
        return False

    def invoke(self, context, event):
        opening_bp = context.object if 'IS_FRAMELESS_OPENING_CAGE' in context.object else hb_utils.get_opening_bp(context.object)
        self.opening = hb_types.GeoNodeCage(opening_bp)
        
        if 'Door Swing' in opening_bp:
            self.door_swing = str(opening_bp['Door Swing'])
        if 'Inset Front' in opening_bp:
            self.inset_front = opening_bp['Inset Front']
        if 'Half Overlay Top' in opening_bp:
            self.half_overlay_top = opening_bp['Half Overlay Top']
        if 'Half Overlay Bottom' in opening_bp:
            self.half_overlay_bottom = opening_bp['Half Overlay Bottom']
        if 'Half Overlay Left' in opening_bp:
            self.half_overlay_left = opening_bp['Half Overlay Left']
        if 'Half Overlay Right' in opening_bp:
            self.half_overlay_right = opening_bp['Half Overlay Right']
        
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=250)

    def check(self, context):
        if 'Door Swing' in self.opening.obj:
            self.opening.obj['Door Swing'] = int(self.door_swing)
        if 'Inset Front' in self.opening.obj:
            self.opening.obj['Inset Front'] = self.inset_front
        if 'Half Overlay Top' in self.opening.obj:
            self.opening.obj['Half Overlay Top'] = self.half_overlay_top
        if 'Half Overlay Bottom' in self.opening.obj:
            self.opening.obj['Half Overlay Bottom'] = self.half_overlay_bottom
        if 'Half Overlay Left' in self.opening.obj:
            self.opening.obj['Half Overlay Left'] = self.half_overlay_left
        if 'Half Overlay Right' in self.opening.obj:
            self.opening.obj['Half Overlay Right'] = self.half_overlay_right
        hb_utils.run_calc_fix(context, self.opening.obj)
        return True

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        
        if 'Door Swing' in self.opening.obj:
            row = box.row()
            row.label(text="Door Swing:")
            row.prop(self, 'door_swing', text="")
        
        if 'Inset Front' in self.opening.obj:
            row = box.row()
            row.prop(self, 'inset_front')
        
        # Half Overlay Properties
        has_half_overlay = any(prop in self.opening.obj for prop in ['Half Overlay Top', 'Half Overlay Bottom', 'Half Overlay Left', 'Half Overlay Right'])
        if has_half_overlay:
            box = layout.box()
            box.label(text="Half Overlay")
            col = box.column(align=True)
            
            if 'Half Overlay Top' in self.opening.obj:
                col.prop(self, 'half_overlay_top')
            if 'Half Overlay Bottom' in self.opening.obj:
                col.prop(self, 'half_overlay_bottom')
            if 'Half Overlay Left' in self.opening.obj:
                col.prop(self, 'half_overlay_left')
            if 'Half Overlay Right' in self.opening.obj:
                col.prop(self, 'half_overlay_right')


class hb_frameless_OT_change_opening_type(bpy.types.Operator):
    bl_idname = "hb_frameless.change_opening_type"
    bl_label = "Change Opening Type"
    bl_description = "Change this opening to a different type"
    bl_options = {'UNDO'}

    opening_type: bpy.props.EnumProperty(
        name="Opening Type",
        items=[
            ('LEFT_DOOR', "Left Door", "Single left swing door"),
            ('RIGHT_DOOR', "Right Door", "Single right swing door"),
            ('DOUBLE_DOORS', "Double Doors", "Double swing doors"),
            ('FLIP_UP_DOOR', "Flip Up Door", "Door hinged at top, swings up"),
            ('SINGLE_DRAWER', "Single Drawer", "Single drawer"),
            ('PULLOUT', "Pullout", "Pullout with pull at top"),
            ('FALSE_FRONT', "False Front", "Decorative panel with no hardware"),
            ('OPEN', "Open", "Open (no front)"),
            ('OPEN_WITH_SHELVES', "Open with Shelves", "Open with adjustable shelves"),
        ],
        default='LEFT_DOOR'
    ) # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj:
            if 'IS_FRAMELESS_OPENING_CAGE' in obj:
                return True
            opening_bp = hb_utils.get_opening_bp(obj)
            return opening_bp is not None
        return False

    def delete_opening_children(self, opening_obj):
        """Delete all children of the opening."""
        children = list(opening_obj.children)
        for child in children:
            self.delete_opening_children(child)
            bpy.data.objects.remove(child, do_unlink=True)

    def get_cabinet_type(self, opening_obj):
        """Get the cabinet type from the cabinet parent."""
        cabinet_bp = hb_utils.get_cabinet_bp(opening_obj)
        if cabinet_bp:
            return cabinet_bp.get('CABINET_TYPE', 'BASE')
        return 'BASE'

    def get_half_overlay_from_parent(self, opening_obj):
        """
        Determine half overlay settings based on opening's position in splitter.
        Returns (half_overlay_top, half_overlay_bottom, half_overlay_left, half_overlay_right)
        """
        half_top = False
        half_bottom = False
        half_left = False
        half_right = False
        
        # Check if parent is a vertical or horizontal splitter
        parent = opening_obj.parent
        if parent:
            if 'IS_FRAMELESS_SPLITTER_VERTICAL_CAGE' in parent:
                # Find all sibling openings to determine position
                siblings = [c for c in parent.children if 'IS_FRAMELESS_OPENING_CAGE' in c]
                siblings.sort(key=lambda o: o.location.z)  # Sort by Z for vertical splitter
                
                if len(siblings) > 1:
                    idx = siblings.index(opening_obj) if opening_obj in siblings else -1
                    if idx >= 0:
                        if idx > 0:  # Not the bottom opening
                            half_bottom = True
                        if idx < len(siblings) - 1:  # Not the top opening
                            half_top = True
                            
            elif 'IS_FRAMELESS_SPLITTER_HORIZONTAL_CAGE' in parent:
                # Find all sibling openings to determine position
                siblings = [c for c in parent.children if 'IS_FRAMELESS_OPENING_CAGE' in c]
                siblings.sort(key=lambda o: o.location.x)  # Sort by X for horizontal splitter
                
                if len(siblings) > 1:
                    idx = siblings.index(opening_obj) if opening_obj in siblings else -1
                    if idx >= 0:
                        if idx > 0:  # Not the leftmost opening
                            half_left = True
                        if idx < len(siblings) - 1:  # Not the rightmost opening
                            half_right = True
        
        return half_top, half_bottom, half_left, half_right

    def add_insert_to_opening(self, opening, insert):
        """Add an insert to the opening with proper dimension drivers."""
        insert.create()
        insert.obj.parent = opening.obj
        dim_x = opening.var_input('Dim X', 'dim_x')
        dim_y = opening.var_input('Dim Y', 'dim_y')
        dim_z = opening.var_input('Dim Z', 'dim_z')
        insert.driver_input('Dim X', 'dim_x', [dim_x])
        insert.driver_input('Dim Y', 'dim_y', [dim_y])
        insert.driver_input('Dim Z', 'dim_z', [dim_z])

    def create_doors(self, opening, door_swing, half_top, half_bottom, half_left, half_right):
        """Create doors with specified swing direction."""
        cabinet_type = self.get_cabinet_type(opening.obj)
        
        doors = types_frameless.Doors()
        
        # Determine pull location based on cabinet type and position
        # half_top=True means there's an opening above (not at top)
        # half_bottom=True means there's an opening below (not at bottom)
        is_top = not half_top
        is_bottom = not half_bottom
        
        if cabinet_type == 'UPPER':
            doors.door_pull_location = "Upper"
        elif cabinet_type == 'TALL':
            if is_top and not is_bottom:
                doors.door_pull_location = "Upper"
            elif is_bottom and not is_top:
                doors.door_pull_location = "Base"
            elif is_top and is_bottom:
                # Single opening - use Tall
                doors.door_pull_location = "Tall"
            else:
                # Middle opening
                doors.door_pull_location = "Tall"
        else:
            doors.door_pull_location = "Base"
        
        # Apply half overlays based on position in splitter
        doors.half_overlay_top = half_top
        doors.half_overlay_bottom = half_bottom
        doors.half_overlay_left = half_left
        doors.half_overlay_right = half_right
        
        self.add_insert_to_opening(opening, doors)
        
        # Set door swing: 0=Left, 1=Right, 2=Double
        doors.obj['Door Swing'] = door_swing

    def create_drawer(self, opening, half_top, half_bottom, half_left, half_right):
        """Create single drawer."""
        drawer = types_frameless.Drawer()
        
        # Apply half overlays based on position in splitter
        drawer.half_overlay_top = half_top
        drawer.half_overlay_bottom = half_bottom
        drawer.half_overlay_left = half_left
        drawer.half_overlay_right = half_right
        
        self.add_insert_to_opening(opening, drawer)

    def create_pullout(self, opening, half_top, half_bottom, half_left, half_right):
        """Create pullout (drawer with pull at top)."""
        pullout = types_frameless.Pullout()
        
        # Apply half overlays based on position in splitter
        pullout.half_overlay_top = half_top
        pullout.half_overlay_bottom = half_bottom
        pullout.half_overlay_left = half_left
        pullout.half_overlay_right = half_right
        
        self.add_insert_to_opening(opening, pullout)

    def create_flip_up_door(self, opening, half_top, half_bottom, half_left, half_right):
        """Create flip up door (hinged at top, swings up)."""
        flip_up = types_frameless.FlipUpDoor()
        
        # Apply half overlays based on position in splitter
        flip_up.half_overlay_top = half_top
        flip_up.half_overlay_bottom = half_bottom
        flip_up.half_overlay_left = half_left
        flip_up.half_overlay_right = half_right
        
        self.add_insert_to_opening(opening, flip_up)

    def create_false_front(self, opening, half_top, half_bottom, half_left, half_right):
        """Create false front (decorative panel with no hardware)."""
        false_front = types_frameless.FalseFront()
        
        # Apply half overlays based on position in splitter
        false_front.half_overlay_top = half_top
        false_front.half_overlay_bottom = half_bottom
        false_front.half_overlay_left = half_left
        false_front.half_overlay_right = half_right
        
        self.add_insert_to_opening(opening, false_front)

    def execute(self, context):
        opening_obj = context.object if 'IS_FRAMELESS_OPENING_CAGE' in context.object else hb_utils.get_opening_bp(context.object)
        if not opening_obj:
            self.report({'ERROR'}, "Could not find opening")
            return {'CANCELLED'}
        
        opening = types_frameless.CabinetOpening(opening_obj)
        
        # Get half overlay settings based on position in splitter
        half_top, half_bottom, half_left, half_right = self.get_half_overlay_from_parent(opening_obj)
        
        # Delete existing opening children
        self.delete_opening_children(opening_obj)
        
        # Create new insert based on type
        if self.opening_type == 'LEFT_DOOR':
            self.create_doors(opening, door_swing=0, half_top=half_top, half_bottom=half_bottom, 
                            half_left=half_left, half_right=half_right)
        elif self.opening_type == 'RIGHT_DOOR':
            self.create_doors(opening, door_swing=1, half_top=half_top, half_bottom=half_bottom,
                            half_left=half_left, half_right=half_right)
        elif self.opening_type == 'DOUBLE_DOORS':
            self.create_doors(opening, door_swing=2, half_top=half_top, half_bottom=half_bottom,
                            half_left=half_left, half_right=half_right)
        elif self.opening_type == 'FLIP_UP_DOOR':
            self.create_flip_up_door(opening, half_top=half_top, half_bottom=half_bottom,
                                    half_left=half_left, half_right=half_right)
        elif self.opening_type == 'SINGLE_DRAWER':
            self.create_drawer(opening, half_top=half_top, half_bottom=half_bottom,
                             half_left=half_left, half_right=half_right)
        elif self.opening_type == 'PULLOUT':
            self.create_pullout(opening, half_top=half_top, half_bottom=half_bottom,
                              half_left=half_left, half_right=half_right)
        elif self.opening_type == 'FALSE_FRONT':
            self.create_false_front(opening, half_top=half_top, half_bottom=half_bottom,
                                   half_left=half_left, half_right=half_right)
        elif self.opening_type == 'OPEN':
            pass  # No children needed for open
        elif self.opening_type == 'OPEN_WITH_SHELVES':
            open_shelves = types_frameless.OpenWithShelves()
            self.add_insert_to_opening(opening, open_shelves)
        
        # Run calc fix to update
        cabinet_bp = hb_utils.get_cabinet_bp(opening_obj)
        if cabinet_bp:
            hb_utils.run_calc_fix(context, cabinet_bp)
            # Assign pull locations based on world position
            assign_pull_locations_to_cabinet(cabinet_bp)
        
        return {'FINISHED'}



class hb_frameless_OT_custom_vertical_splitter(bpy.types.Operator):
    bl_idname = "hb_frameless.custom_vertical_splitter"
    bl_label = "Custom Vertical Openings"
    bl_description = "Create custom vertical openings with adjustable sizes"
    bl_options = {'UNDO'}

    opening_count: bpy.props.IntProperty(
        name="Number of Openings",
        min=2, max=10,
        default=2
    ) # type: ignore
    
    previous_opening_count: bpy.props.IntProperty(default=0) # type: ignore
    splitter_obj_name: bpy.props.StringProperty(name="Splitter Object") # type: ignore
    parent_obj_name: bpy.props.StringProperty(name="Parent Object") # type: ignore

    # Opening inserts
    opening_1_insert: bpy.props.EnumProperty(name="Opening 1", items=[('DOORS', "Doors", ""), ('DRAWER', "Drawer", ""), ('OPEN', "Open", "")], default='DOORS') # type: ignore
    opening_2_insert: bpy.props.EnumProperty(name="Opening 2", items=[('DOORS', "Doors", ""), ('DRAWER', "Drawer", ""), ('OPEN', "Open", "")], default='DOORS') # type: ignore
    opening_3_insert: bpy.props.EnumProperty(name="Opening 3", items=[('DOORS', "Doors", ""), ('DRAWER', "Drawer", ""), ('OPEN', "Open", "")], default='DOORS') # type: ignore
    opening_4_insert: bpy.props.EnumProperty(name="Opening 4", items=[('DOORS', "Doors", ""), ('DRAWER', "Drawer", ""), ('OPEN', "Open", "")], default='DOORS') # type: ignore
    opening_5_insert: bpy.props.EnumProperty(name="Opening 5", items=[('DOORS', "Doors", ""), ('DRAWER', "Drawer", ""), ('OPEN', "Open", "")], default='DOORS') # type: ignore
    opening_6_insert: bpy.props.EnumProperty(name="Opening 6", items=[('DOORS', "Doors", ""), ('DRAWER', "Drawer", ""), ('OPEN', "Open", "")], default='DOORS') # type: ignore
    opening_7_insert: bpy.props.EnumProperty(name="Opening 7", items=[('DOORS', "Doors", ""), ('DRAWER', "Drawer", ""), ('OPEN', "Open", "")], default='DOORS') # type: ignore
    opening_8_insert: bpy.props.EnumProperty(name="Opening 8", items=[('DOORS', "Doors", ""), ('DRAWER', "Drawer", ""), ('OPEN', "Open", "")], default='DOORS') # type: ignore
    opening_9_insert: bpy.props.EnumProperty(name="Opening 9", items=[('DOORS', "Doors", ""), ('DRAWER', "Drawer", ""), ('OPEN', "Open", "")], default='DOORS') # type: ignore
    opening_10_insert: bpy.props.EnumProperty(name="Opening 10", items=[('DOORS', "Doors", ""), ('DRAWER', "Drawer", ""), ('OPEN', "Open", "")], default='DOORS') # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj:
            bay_bp = hb_utils.get_bay_bp(obj)
            opening_bp = hb_utils.get_opening_bp(obj)
            return bay_bp is not None or opening_bp is not None
        return False

    def delete_children(self, obj):
        """Delete all children of the object."""
        children = list(obj.children)
        for child in children:
            self.delete_children(child)
            bpy.data.objects.remove(child, do_unlink=True)

    def get_cabinet_type(self, obj):
        """Get the cabinet type from the cabinet parent."""
        cabinet_bp = hb_utils.get_cabinet_bp(obj)
        if cabinet_bp:
            return cabinet_bp.get('CABINET_TYPE', 'BASE')
        return 'BASE'

    def get_splitter_obj(self):
        """Get the splitter object by name."""
        if self.splitter_obj_name and self.splitter_obj_name in bpy.data.objects:
            return bpy.data.objects[self.splitter_obj_name]
        return None

    def get_parent_obj(self):
        """Get the parent object by name."""
        if self.parent_obj_name and self.parent_obj_name in bpy.data.objects:
            return bpy.data.objects[self.parent_obj_name]
        return None

    def create_splitter(self, context, parent_obj):
        """Create or recreate the splitter with current settings."""
        # Delete existing children of parent
        self.delete_children(parent_obj)
        
        # Create empty splitter (no inserts yet - just for sizing)
        splitter = types_frameless.SplitterVertical()
        splitter.splitter_qty = self.opening_count - 1
        splitter.opening_sizes = [0] * self.opening_count  # All equal initially
        splitter.opening_inserts = [None] * self.opening_count  # No inserts yet
        splitter.create()
        
        # Parent to bay/opening and set up dimension drivers
        splitter.obj.parent = parent_obj
        
        if 'IS_FRAMELESS_BAY_CAGE' in parent_obj:
            bay = types_frameless.CabinetBay(parent_obj)
        else:
            bay = types_frameless.CabinetOpening(parent_obj)
            
        dim_x = bay.var_input('Dim X', 'dim_x')
        dim_y = bay.var_input('Dim Y', 'dim_y')
        dim_z = bay.var_input('Dim Z', 'dim_z')
        splitter.driver_input('Dim X', 'dim_x', [dim_x])
        splitter.driver_input('Dim Y', 'dim_y', [dim_y])
        splitter.driver_input('Dim Z', 'dim_z', [dim_z])
        hb_utils.run_calc_fix(context, splitter.obj,passes=3)
        
        self.splitter_obj_name = splitter.obj.name
        self.previous_opening_count = self.opening_count
        
        # Run calc fix
        cabinet_bp = hb_utils.get_cabinet_bp(parent_obj)
        if cabinet_bp:
            hb_utils.run_calc_fix(context, cabinet_bp,passes=3)
        
        return splitter.obj

    def invoke(self, context, event):
        # Find parent opening or bay (prioritize opening so user can keep splitting)
        obj = context.object
        opening_bp = hb_utils.get_opening_bp(obj)
        bay_bp = hb_utils.get_bay_bp(obj)
        
        # Prioritize opening over bay
        parent_obj = opening_bp if opening_bp else bay_bp
        if not parent_obj:
            self.report({'ERROR'}, "Could not find bay or opening")
            return {'CANCELLED'}
        
        self.parent_obj_name = parent_obj.name
        
        # Create initial splitter
        self.create_splitter(context, parent_obj)
        
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def check(self, context):
        parent_obj = self.get_parent_obj()
        if not parent_obj:
            return False
        
        # If opening count changed, recreate the splitter
        if self.opening_count != self.previous_opening_count:
            self.create_splitter(context, parent_obj)
            return True
        
        # Otherwise just recalculate
        splitter_obj = self.get_splitter_obj()
        if splitter_obj:
            for calculator in splitter_obj.home_builder.calculators:
                calculator.calculate()
            
            cabinet_bp = hb_utils.get_cabinet_bp(splitter_obj)
            if cabinet_bp:
                hb_utils.run_calc_fix(context, cabinet_bp)
        
        return True

    def create_insert(self, insert_type, cabinet_type, is_top, is_bottom, opening_bottom_z=0):
        """Create an insert based on the type.
        
        Args:
            insert_type: Type of insert ('DOORS', 'DRAWER', 'OPEN')
            cabinet_type: Cabinet type ('BASE', 'TALL', 'UPPER')
            is_top: Whether this is the topmost opening
            is_bottom: Whether this is the bottommost opening
            opening_bottom_z: Z position of opening bottom from floor (meters)
        """
        if insert_type == 'DOORS':
            doors = types_frameless.Doors()
            
            # Determine pull location based on cabinet type and position
            if cabinet_type == 'UPPER':
                doors.door_pull_location = "Upper"
            elif cabinet_type == 'TALL':
                if is_top and not is_bottom:
                    doors.door_pull_location = "Upper"
                elif is_bottom and not is_top:
                    doors.door_pull_location = "Base"
                elif is_top and is_bottom:
                    # Single opening - use Tall
                    doors.door_pull_location = "Tall"
                else:
                    # Middle opening
                    doors.door_pull_location = "Tall"
            else:
                doors.door_pull_location = "Base"
            
            if not is_top:
                doors.half_overlay_top = True
            if not is_bottom:
                doors.half_overlay_bottom = True
            return doors
        elif insert_type == 'DRAWER':
            drawer = types_frameless.Drawer()
            if not is_top:
                drawer.half_overlay_top = True
            if not is_bottom:
                drawer.half_overlay_bottom = True
            return drawer
        else:  # OPEN
            return None

    def execute(self, context):
        parent_obj = self.get_parent_obj()
        splitter_obj = self.get_splitter_obj()
        
        if not parent_obj or not splitter_obj:
            self.report({'ERROR'}, "Could not find objects")
            return {'CANCELLED'}
        
        # Get the current calculator values before recreating
        opening_sizes = []
        for calculator in splitter_obj.home_builder.calculators:
            for prompt in calculator.prompts:
                if prompt.equal:
                    opening_sizes.append(0)
                else:
                    opening_sizes.append(prompt.distance_value)
        
        # Delete existing and create final splitter with inserts
        self.delete_children(parent_obj)
        
        cabinet_type = self.get_cabinet_type(parent_obj)
        
        # Calculate opening Z positions for pull location logic
        # Get parent bay/opening dimensions
        if 'IS_FRAMELESS_BAY_CAGE' in parent_obj:
            parent_cage = types_frameless.CabinetBay(parent_obj)
        else:
            parent_cage = types_frameless.CabinetOpening(parent_obj)
        
        parent_dim_z = parent_cage.get_input('Dim Z')
        
        # Get parent's world Z position (bottom of the bay/opening)
        parent_world_z = parent_obj.matrix_world.translation.z
        
        # Calculate actual opening sizes (resolve equal-sized openings)
        props = bpy.context.scene.hb_frameless
        divider_thickness = props.default_carcass_part_thickness
        total_dividers = (self.opening_count - 1) * divider_thickness
        available_height = parent_dim_z - total_dividers
        
        # Count equal-sized openings and sum of fixed sizes
        equal_count = opening_sizes.count(0)
        fixed_sum = sum(s for s in opening_sizes if s > 0)
        
        if equal_count > 0:
            equal_size = (available_height - fixed_sum) / equal_count
        else:
            equal_size = 0
        
        # Calculate actual sizes
        actual_sizes = [s if s > 0 else equal_size for s in opening_sizes]
        
        # Calculate bottom Z position for each opening (from floor)
        # Openings are ordered top to bottom, so opening 0 is at top
        opening_bottom_z_positions = []
        for i in range(self.opening_count):
            # Sum heights of openings below this one (i+1 to end) plus dividers
            height_below = sum(actual_sizes[i+1:])
            dividers_below = (self.opening_count - 1 - i) * divider_thickness
            bottom_z = parent_world_z + height_below + dividers_below
            opening_bottom_z_positions.append(bottom_z)
        
        insert_props = [
            self.opening_1_insert, self.opening_2_insert, self.opening_3_insert,
            self.opening_4_insert, self.opening_5_insert, self.opening_6_insert,
            self.opening_7_insert, self.opening_8_insert, self.opening_9_insert,
            self.opening_10_insert
        ]
        
        opening_inserts = []
        for i in range(self.opening_count):
            is_top = (i == 0)
            is_bottom = (i == self.opening_count - 1)
            opening_bottom_z = opening_bottom_z_positions[i]
            insert = self.create_insert(insert_props[i], cabinet_type, is_top, is_bottom, opening_bottom_z)
            opening_inserts.append(insert)
        
        # Create final splitter with inserts
        splitter = types_frameless.SplitterVertical()
        splitter.splitter_qty = self.opening_count - 1
        splitter.opening_sizes = opening_sizes
        splitter.opening_inserts = opening_inserts
        splitter.create()
        
        # Parent and set up drivers
        splitter.obj.parent = parent_obj
        
        if 'IS_FRAMELESS_BAY_CAGE' in parent_obj:
            bay = types_frameless.CabinetBay(parent_obj)
        else:
            bay = types_frameless.CabinetOpening(parent_obj)
            
        dim_x = bay.var_input('Dim X', 'dim_x')
        dim_y = bay.var_input('Dim Y', 'dim_y')
        dim_z = bay.var_input('Dim Z', 'dim_z')
        splitter.driver_input('Dim X', 'dim_x', [dim_x])
        splitter.driver_input('Dim Y', 'dim_y', [dim_y])
        splitter.driver_input('Dim Z', 'dim_z', [dim_z])
        hb_utils.run_calc_fix(context, splitter.obj,passes=3)
        
        # Run calc fix
        cabinet_bp = hb_utils.get_cabinet_bp(parent_obj)
        if cabinet_bp:
            hb_utils.run_calc_fix(context, cabinet_bp)
            # Assign pull locations based on world position
            assign_pull_locations_to_cabinet(cabinet_bp)
            # Reassign cabinet style to apply materials to new parts
            bpy.ops.hb_frameless.assign_cabinet_style(cabinet_name=cabinet_bp.name)
        
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        box.prop(self, 'opening_count')
        
        splitter_obj = self.get_splitter_obj()
        
        # Opening sizes from calculator
        box = layout.box()
        box.label(text="Opening Heights:", icon='SNAP_GRID')
        
        if splitter_obj:
            for calculator in splitter_obj.home_builder.calculators:
                col = box.column(align=True)
                for prompt in calculator.prompts:
                    row = col.row(align=True)
                    row.active = not prompt.equal
                    row.prop(prompt, 'distance_value', text=prompt.name)
                    row.prop(prompt, 'equal', text="", icon='LINKED' if prompt.equal else 'UNLINKED')
        
        # Insert types
        box = layout.box()
        box.label(text="Opening Types:", icon='MESH_PLANE')
        
        insert_props = [
            'opening_1_insert', 'opening_2_insert', 'opening_3_insert',
            'opening_4_insert', 'opening_5_insert', 'opening_6_insert',
            'opening_7_insert', 'opening_8_insert', 'opening_9_insert',
            'opening_10_insert'
        ]
        
        col = box.column(align=True)
        for i in range(self.opening_count):
            row = col.row(align=True)
            row.label(text=f"Opening {i+1}:")
            row.prop(self, insert_props[i], text="")


class hb_frameless_OT_custom_horizontal_splitter(bpy.types.Operator):
    bl_idname = "hb_frameless.custom_horizontal_splitter"
    bl_label = "Custom Horizontal Openings"
    bl_description = "Create custom horizontal openings with adjustable sizes"
    bl_options = {'UNDO'}

    opening_count: bpy.props.IntProperty(
        name="Number of Openings",
        min=2, max=10,
        default=2
    ) # type: ignore
    
    previous_opening_count: bpy.props.IntProperty(default=0) # type: ignore
    splitter_obj_name: bpy.props.StringProperty(name="Splitter Object") # type: ignore
    parent_obj_name: bpy.props.StringProperty(name="Parent Object") # type: ignore

    # Opening inserts
    opening_1_insert: bpy.props.EnumProperty(name="Opening 1", items=[('DOORS', "Doors", ""), ('DRAWER', "Drawer", ""), ('OPEN', "Open", "")], default='DOORS') # type: ignore
    opening_2_insert: bpy.props.EnumProperty(name="Opening 2", items=[('DOORS', "Doors", ""), ('DRAWER', "Drawer", ""), ('OPEN', "Open", "")], default='DOORS') # type: ignore
    opening_3_insert: bpy.props.EnumProperty(name="Opening 3", items=[('DOORS', "Doors", ""), ('DRAWER', "Drawer", ""), ('OPEN', "Open", "")], default='DOORS') # type: ignore
    opening_4_insert: bpy.props.EnumProperty(name="Opening 4", items=[('DOORS', "Doors", ""), ('DRAWER', "Drawer", ""), ('OPEN', "Open", "")], default='DOORS') # type: ignore
    opening_5_insert: bpy.props.EnumProperty(name="Opening 5", items=[('DOORS', "Doors", ""), ('DRAWER', "Drawer", ""), ('OPEN', "Open", "")], default='DOORS') # type: ignore
    opening_6_insert: bpy.props.EnumProperty(name="Opening 6", items=[('DOORS', "Doors", ""), ('DRAWER', "Drawer", ""), ('OPEN', "Open", "")], default='DOORS') # type: ignore
    opening_7_insert: bpy.props.EnumProperty(name="Opening 7", items=[('DOORS', "Doors", ""), ('DRAWER', "Drawer", ""), ('OPEN', "Open", "")], default='DOORS') # type: ignore
    opening_8_insert: bpy.props.EnumProperty(name="Opening 8", items=[('DOORS', "Doors", ""), ('DRAWER', "Drawer", ""), ('OPEN', "Open", "")], default='DOORS') # type: ignore
    opening_9_insert: bpy.props.EnumProperty(name="Opening 9", items=[('DOORS', "Doors", ""), ('DRAWER', "Drawer", ""), ('OPEN', "Open", "")], default='DOORS') # type: ignore
    opening_10_insert: bpy.props.EnumProperty(name="Opening 10", items=[('DOORS', "Doors", ""), ('DRAWER', "Drawer", ""), ('OPEN', "Open", "")], default='DOORS') # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj:
            bay_bp = hb_utils.get_bay_bp(obj)
            opening_bp = hb_utils.get_opening_bp(obj)
            return bay_bp is not None or opening_bp is not None
        return False

    def delete_children(self, obj):
        """Delete all children of the object."""
        children = list(obj.children)
        for child in children:
            self.delete_children(child)
            bpy.data.objects.remove(child, do_unlink=True)

    def get_cabinet_type(self, obj):
        """Get the cabinet type from the cabinet parent."""
        cabinet_bp = hb_utils.get_cabinet_bp(obj)
        if cabinet_bp:
            return cabinet_bp.get('CABINET_TYPE', 'BASE')
        return 'BASE'

    def get_splitter_obj(self):
        """Get the splitter object by name."""
        if self.splitter_obj_name and self.splitter_obj_name in bpy.data.objects:
            return bpy.data.objects[self.splitter_obj_name]
        return None

    def get_parent_obj(self):
        """Get the parent object by name."""
        if self.parent_obj_name and self.parent_obj_name in bpy.data.objects:
            return bpy.data.objects[self.parent_obj_name]
        return None

    def create_splitter(self, context, parent_obj):
        """Create or recreate the splitter with current settings."""
        # Delete existing children of parent
        self.delete_children(parent_obj)
        
        # Create empty splitter (no inserts yet - just for sizing)
        splitter = types_frameless.SplitterHorizontal()
        splitter.splitter_qty = self.opening_count - 1
        splitter.opening_sizes = [0] * self.opening_count  # All equal initially
        splitter.opening_inserts = [None] * self.opening_count  # No inserts yet
        splitter.create()
        
        # Parent to bay/opening and set up dimension drivers
        splitter.obj.parent = parent_obj
        
        if 'IS_FRAMELESS_BAY_CAGE' in parent_obj:
            bay = types_frameless.CabinetBay(parent_obj)
        else:
            bay = types_frameless.CabinetOpening(parent_obj)
            
        dim_x = bay.var_input('Dim X', 'dim_x')
        dim_y = bay.var_input('Dim Y', 'dim_y')
        dim_z = bay.var_input('Dim Z', 'dim_z')
        splitter.driver_input('Dim X', 'dim_x', [dim_x])
        splitter.driver_input('Dim Y', 'dim_y', [dim_y])
        splitter.driver_input('Dim Z', 'dim_z', [dim_z])
        hb_utils.run_calc_fix(context, splitter.obj, passes=3)
        
        self.splitter_obj_name = splitter.obj.name
        self.previous_opening_count = self.opening_count
        
        # Run calc fix
        cabinet_bp = hb_utils.get_cabinet_bp(parent_obj)
        if cabinet_bp:
            hb_utils.run_calc_fix(context, cabinet_bp, passes=3)
        
        return splitter.obj

    def invoke(self, context, event):
        # Find parent opening or bay (prioritize opening so user can keep splitting)
        obj = context.object
        opening_bp = hb_utils.get_opening_bp(obj)
        bay_bp = hb_utils.get_bay_bp(obj)
        
        # Prioritize opening over bay
        parent_obj = opening_bp if opening_bp else bay_bp
        if not parent_obj:
            self.report({'ERROR'}, "Could not find bay or opening")
            return {'CANCELLED'}
        
        self.parent_obj_name = parent_obj.name
        
        # Create initial splitter
        self.create_splitter(context, parent_obj)
        
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def check(self, context):
        parent_obj = self.get_parent_obj()
        if not parent_obj:
            return False
        
        # If opening count changed, recreate the splitter
        if self.opening_count != self.previous_opening_count:
            self.create_splitter(context, parent_obj)
            return True
        
        # Otherwise just recalculate
        splitter_obj = self.get_splitter_obj()
        if splitter_obj:
            for calculator in splitter_obj.home_builder.calculators:
                calculator.calculate()
            
            cabinet_bp = hb_utils.get_cabinet_bp(splitter_obj)
            if cabinet_bp:
                hb_utils.run_calc_fix(context, cabinet_bp)
        
        return True

    def create_insert(self, insert_type, cabinet_type, is_left, is_right):
        """Create an insert based on the type."""
        if insert_type == 'DOORS':
            doors = types_frameless.Doors()
            # Determine pull location based on cabinet type
            # For horizontal splits, all openings are at same height
            if cabinet_type == 'UPPER':
                doors.door_pull_location = "Upper"
            elif cabinet_type == 'TALL':
                # For horizontal splits in tall cabinets, use Tall as default
                doors.door_pull_location = "Tall"
            else:
                doors.door_pull_location = "Base"
            # Set half overlays for side-by-side openings
            if not is_left:
                doors.half_overlay_left = True
            if not is_right:
                doors.half_overlay_right = True
            return doors
        elif insert_type == 'DRAWER':
            drawer = types_frameless.Drawer()
            if not is_left:
                drawer.half_overlay_left = True
            if not is_right:
                drawer.half_overlay_right = True
            return drawer
        else:  # OPEN
            return None

    def execute(self, context):
        parent_obj = self.get_parent_obj()
        splitter_obj = self.get_splitter_obj()
        
        if not parent_obj or not splitter_obj:
            self.report({'ERROR'}, "Could not find objects")
            return {'CANCELLED'}
        
        # Get the current calculator values before recreating
        opening_sizes = []
        for calculator in splitter_obj.home_builder.calculators:
            for prompt in calculator.prompts:
                if prompt.equal:
                    opening_sizes.append(0)
                else:
                    opening_sizes.append(prompt.distance_value)
        
        # Delete existing and create final splitter with inserts
        self.delete_children(parent_obj)
        
        cabinet_type = self.get_cabinet_type(parent_obj)
        
        insert_props = [
            self.opening_1_insert, self.opening_2_insert, self.opening_3_insert,
            self.opening_4_insert, self.opening_5_insert, self.opening_6_insert,
            self.opening_7_insert, self.opening_8_insert, self.opening_9_insert,
            self.opening_10_insert
        ]
        
        opening_inserts = []
        for i in range(self.opening_count):
            is_left = (i == 0)
            is_right = (i == self.opening_count - 1)
            insert = self.create_insert(insert_props[i], cabinet_type, is_left, is_right)
            opening_inserts.append(insert)
        
        # Create final splitter with inserts
        splitter = types_frameless.SplitterHorizontal()
        splitter.splitter_qty = self.opening_count - 1
        splitter.opening_sizes = opening_sizes
        splitter.opening_inserts = opening_inserts
        splitter.create()
        
        # Parent and set up drivers
        splitter.obj.parent = parent_obj
        
        if 'IS_FRAMELESS_BAY_CAGE' in parent_obj:
            bay = types_frameless.CabinetBay(parent_obj)
        else:
            bay = types_frameless.CabinetOpening(parent_obj)
            
        dim_x = bay.var_input('Dim X', 'dim_x')
        dim_y = bay.var_input('Dim Y', 'dim_y')
        dim_z = bay.var_input('Dim Z', 'dim_z')
        splitter.driver_input('Dim X', 'dim_x', [dim_x])
        splitter.driver_input('Dim Y', 'dim_y', [dim_y])
        splitter.driver_input('Dim Z', 'dim_z', [dim_z])
        hb_utils.run_calc_fix(context, splitter.obj, passes=3)
        
        # Run calc fix
        cabinet_bp = hb_utils.get_cabinet_bp(parent_obj)
        if cabinet_bp:
            hb_utils.run_calc_fix(context, cabinet_bp)
            # Assign pull locations based on world position
            assign_pull_locations_to_cabinet(cabinet_bp)
            # Reassign cabinet style to apply materials to new parts
            bpy.ops.hb_frameless.assign_cabinet_style(cabinet_name=cabinet_bp.name)
        
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        box.prop(self, 'opening_count')
        
        splitter_obj = self.get_splitter_obj()
        
        # Opening widths from calculator
        box = layout.box()
        box.label(text="Opening Widths:", icon='SNAP_GRID')
        
        if splitter_obj:
            for calculator in splitter_obj.home_builder.calculators:
                col = box.column(align=True)
                for prompt in calculator.prompts:
                    row = col.row(align=True)
                    row.active = not prompt.equal
                    row.prop(prompt, 'distance_value', text=prompt.name)
                    row.prop(prompt, 'equal', text="", icon='LINKED' if prompt.equal else 'UNLINKED')
        
        # Insert types
        box = layout.box()
        box.label(text="Opening Types:", icon='MESH_PLANE')
        
        insert_props = [
            'opening_1_insert', 'opening_2_insert', 'opening_3_insert',
            'opening_4_insert', 'opening_5_insert', 'opening_6_insert',
            'opening_7_insert', 'opening_8_insert', 'opening_9_insert',
            'opening_10_insert'
        ]
        
        col = box.column(align=True)
        for i in range(self.opening_count):
            row = col.row(align=True)
            row.label(text=f"Opening {i+1}:")
            row.prop(self, insert_props[i], text="")




class hb_frameless_OT_edit_splitter_openings(bpy.types.Operator):
    bl_idname = "hb_frameless.edit_splitter_openings"
    bl_label = "Edit Opening Sizes"
    bl_description = "Edit the sizes of openings in a vertical or horizontal splitter"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj:
            # Check if this object is a splitter
            if 'IS_FRAMELESS_SPLITTER_VERTICAL_CAGE' in obj or 'IS_FRAMELESS_SPLITTER_HORIZONTAL_CAGE' in obj:
                return True
            # Check parents
            current = obj.parent
            while current:
                if 'IS_FRAMELESS_SPLITTER_VERTICAL_CAGE' in current or 'IS_FRAMELESS_SPLITTER_HORIZONTAL_CAGE' in current:
                    return True
                current = current.parent
            # Check direct children first
            for child in obj.children:
                if 'IS_FRAMELESS_SPLITTER_VERTICAL_CAGE' in child or 'IS_FRAMELESS_SPLITTER_HORIZONTAL_CAGE' in child:
                    return True
            # Check recursive children as fallback
            for child in obj.children_recursive:
                if 'IS_FRAMELESS_SPLITTER_VERTICAL_CAGE' in child or 'IS_FRAMELESS_SPLITTER_HORIZONTAL_CAGE' in child:
                    return True
        return False

    def get_splitter_obj(self, context):
        """Find the splitter object from the selected object."""
        obj = context.object
        if not obj:
            return None
        
        # Check if this object is a splitter
        if 'IS_FRAMELESS_SPLITTER_VERTICAL_CAGE' in obj or 'IS_FRAMELESS_SPLITTER_HORIZONTAL_CAGE' in obj:
            return obj
        
        # Check parents (closest splitter going up)
        current = obj.parent
        while current:
            if 'IS_FRAMELESS_SPLITTER_VERTICAL_CAGE' in current or 'IS_FRAMELESS_SPLITTER_HORIZONTAL_CAGE' in current:
                return current
            current = current.parent
        
        # Check direct children first (for when bay is selected)
        for child in obj.children:
            if 'IS_FRAMELESS_SPLITTER_VERTICAL_CAGE' in child or 'IS_FRAMELESS_SPLITTER_HORIZONTAL_CAGE' in child:
                return child
        
        # Check recursive children as fallback
        for child in obj.children_recursive:
            if 'IS_FRAMELESS_SPLITTER_VERTICAL_CAGE' in child or 'IS_FRAMELESS_SPLITTER_HORIZONTAL_CAGE' in child:
                return child
        
        return None

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def check(self, context):
        splitter_obj = self.get_splitter_obj(context)
        if splitter_obj:
            # Recalculate the calculator
            for calculator in splitter_obj.home_builder.calculators:
                calculator.calculate()
            
            # Run calc fix to update all sizes
            cabinet_bp = hb_utils.get_cabinet_bp(splitter_obj)
            if cabinet_bp:
                hb_utils.run_calc_fix(context, cabinet_bp)
        return True

    def execute(self, context):
        splitter_obj = self.get_splitter_obj(context)
        if not splitter_obj:
            self.report({'ERROR'}, "Could not find splitter")
            return {'CANCELLED'}
        
        # Recalculate the calculator
        for calculator in splitter_obj.home_builder.calculators:
            calculator.calculate()
        
        # Run calc fix to update all sizes
        cabinet_bp = hb_utils.get_cabinet_bp(splitter_obj)
        if cabinet_bp:
            hb_utils.run_calc_fix(context, cabinet_bp)
        
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        splitter_obj = self.get_splitter_obj(context)
        
        if not splitter_obj:
            layout.label(text="No splitter found")
            return
        
        is_vertical = 'IS_FRAMELESS_SPLITTER_VERTICAL_CAGE' in splitter_obj
        
        box = layout.box()
        box.label(text="Vertical Openings:" if is_vertical else "Horizontal Openings:", icon='SNAP_GRID')
        
        # Draw calculator prompts
        for calculator in splitter_obj.home_builder.calculators:
            col = box.column(align=True)
            for prompt in calculator.prompts:
                row = col.row(align=True)
                row.active = not prompt.equal
                row.prop(prompt, 'distance_value', text=prompt.name)
                row.prop(prompt, 'equal', text="", icon='LINKED' if prompt.equal else 'UNLINKED')


classes = (
    hb_frameless_OT_change_bay_opening,
    hb_frameless_OT_opening_prompts,
    hb_frameless_OT_change_opening_type,
    hb_frameless_OT_custom_vertical_splitter,
    hb_frameless_OT_custom_horizontal_splitter,
    hb_frameless_OT_edit_splitter_openings,
)

register, unregister = bpy.utils.register_classes_factory(classes)
