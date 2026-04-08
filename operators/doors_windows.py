import bpy
from .. import hb_types, hb_snap, hb_placement, units
import math
from mathutils import Vector
from ..hb_details import GeoNodeText

# Single door swing options: (label, {geo node inputs})
SINGLE_DOOR_SWINGS = [
    ('Inside Left',   {'Swing Inside': True,  'Is Left': True,  'Is Double': False}),
    ('Inside Right',  {'Swing Inside': True,  'Is Left': False, 'Is Double': False}),
    ('Outside Left',  {'Swing Inside': False, 'Is Left': True,  'Is Double': False}),
    ('Outside Right', {'Swing Inside': False, 'Is Left': False, 'Is Double': False}),
]

# Double door swing options: (label, {geo node inputs})
DOUBLE_DOOR_SWINGS = [
    ('Inside',  {'Swing Inside': True,  'Is Double': True}),
    ('Outside', {'Swing Inside': False, 'Is Double': True}),
]


class WallObjectPlacementMixin(hb_placement.PlacementMixin):
    """
    Extended placement mixin for objects placed on walls (doors, windows, cabinets).
    Adds support for left/right offset and width input.
    """
    
    # Track which direction offset is measured from
    offset_from_right: bool = False
    
    # Track if user has explicitly set position (don't follow mouse)
    position_locked: bool = False
    
    # Wall context
    selected_wall = None
    wall_length: float = 0
    placement_x: float = 0
    
    # Gap boundaries for offset calculations
    gap_left_boundary: float = 0
    gap_right_boundary: float = 0
    
    # Dimensions
    dim_total_width = None
    dim_left_offset = None
    dim_right_offset = None
    
    def get_view_distance(self, context):
        """Get the current view distance for scaling UI elements."""
        try:
            for area in context.screen.areas:
                if area.type == 'VIEW_3D':
                    for space in area.spaces:
                        if space.type == 'VIEW_3D':
                            return space.region_3d.view_distance
        except:
            pass
        return 10.0
    
    def create_placement_dimensions(self):
        """Create dimension annotations for placement feedback."""
        # Total width dimension
        self.dim_total_width = hb_types.GeoNodeDimension()
        self.dim_total_width.create("Dim_Total_Width")
        self.dim_total_width.obj.show_in_front = True
        self.register_placement_object(self.dim_total_width.obj)
        
        # Left offset dimension
        self.dim_left_offset = hb_types.GeoNodeDimension()
        self.dim_left_offset.create("Dim_Left_Offset")
        self.dim_left_offset.obj.show_in_front = True
        self.register_placement_object(self.dim_left_offset.obj)
        
        # Right offset dimension
        self.dim_right_offset = hb_types.GeoNodeDimension()
        self.dim_right_offset.create("Dim_Right_Offset")
        self.dim_right_offset.obj.show_in_front = True
        self.register_placement_object(self.dim_right_offset.obj)
    
    def get_dimension_rotation(self, context, base_rotation_z):
        """Calculate dimension rotation to face the camera based on view angle.
        
        Returns: (rotation_tuple, is_plan_view)
        """
        region_3d = None
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                region_3d = area.spaces.active.region_3d
                break
        
        if not region_3d:
            return (0, 0, base_rotation_z), True
        
        view_matrix = region_3d.view_matrix
        view_dir = Vector((view_matrix[2][0], view_matrix[2][1], view_matrix[2][2]))
        
        vertical_component = abs(view_dir.z)
        
        if vertical_component > 0.7:
            # Plan view - dimension lies flat
            return (0, 0, base_rotation_z), True
        else:
            # Elevation/3D view - rotate dimension to stand up
            return (math.radians(90), 0, base_rotation_z), False

    def update_placement_dimensions(self, context, obj_width, obj_height, wall_thickness, z_offset=0):
        """Update dimension positions and values."""
        if not self.dim_total_width or not self.selected_wall:
            return
        
        # Scale text based on view distance
        view_dist = self.get_view_distance(context)
        base_size = units.inch(8)
        text_size = base_size * (view_dist / 10.0)
        text_size = max(units.inch(4), min(units.inch(24), text_size))
        
        self.dim_total_width.set_input("Text Size", text_size)
        self.dim_left_offset.set_input("Text Size", text_size)
        self.dim_right_offset.set_input("Text Size", text_size)
        
        wall_matrix = self.selected_wall.matrix_world
        wall_rotation_z = self.selected_wall.rotation_euler.z
        
        left_offset = self.placement_x - self.gap_left_boundary
        right_offset = self.gap_right_boundary - (self.placement_x + obj_width)
        
        # Get rotation based on view angle
        dim_rotation, is_plan_view = self.get_dimension_rotation(context, wall_rotation_z)
        
        # Position at mid-height of object, accounting for z offset
        dim_z = z_offset + obj_height / 2
        dim_y = wall_thickness + units.inch(2)
        
        # Total width dimension
        local_pos = Vector((self.placement_x, dim_y, dim_z))
        self.dim_total_width.obj.location = wall_matrix @ local_pos
        self.dim_total_width.obj.rotation_euler = dim_rotation
        self.dim_total_width.obj.data.splines[0].points[1].co = (obj_width, 0, 0, 1)
        self.dim_total_width.set_decimal()
        self.dim_total_width.obj.hide_set(False)
        
        # Left offset dimension
        if left_offset > units.inch(0.5):
            local_pos = Vector((self.gap_left_boundary, dim_y, dim_z))
            self.dim_left_offset.obj.location = wall_matrix @ local_pos
            self.dim_left_offset.obj.rotation_euler = dim_rotation
            self.dim_left_offset.obj.data.splines[0].points[1].co = (left_offset, 0, 0, 1)
            self.dim_left_offset.set_decimal()
            self.dim_left_offset.obj.hide_set(False)
        else:
            self.dim_left_offset.obj.hide_set(True)
        
        # Right offset dimension
        if right_offset > units.inch(0.5):
            local_pos = Vector((self.placement_x + obj_width, dim_y, dim_z))
            self.dim_right_offset.obj.location = wall_matrix @ local_pos
            self.dim_right_offset.obj.rotation_euler = dim_rotation
            self.dim_right_offset.obj.data.splines[0].points[1].co = (right_offset, 0, 0, 1)
            self.dim_right_offset.set_decimal()
            self.dim_right_offset.obj.hide_set(False)
        else:
            self.dim_right_offset.obj.hide_set(True)
    
    def hide_placement_dimensions(self):
        """Hide all placement dimensions."""
        if self.dim_total_width:
            self.dim_total_width.obj.hide_set(True)
        if self.dim_left_offset:
            self.dim_left_offset.obj.hide_set(True)
        if self.dim_right_offset:
            self.dim_right_offset.obj.hide_set(True)
    
    def delete_placement_dimensions(self):
        """Delete all placement dimension objects."""
        for dim in [self.dim_total_width, self.dim_left_offset, self.dim_right_offset]:
            if dim and dim.obj and dim.obj.name in bpy.data.objects:
                # Remove from placement_objects if present
                if dim.obj in self.placement_objects:
                    self.placement_objects.remove(dim.obj)
                bpy.data.objects.remove(dim.obj, do_unlink=True)
        self.dim_total_width = None
        self.dim_left_offset = None
        self.dim_right_offset = None
    
    def get_placed_object(self):
        """Override this to return the object being placed."""
        raise NotImplementedError
    
    def get_placed_object_width(self) -> float:
        """Override this to return the width of the object being placed."""
        raise NotImplementedError
    
    def set_placed_object_width(self, width: float):
        """Override this to set the width of the object being placed."""
        raise NotImplementedError
    
    def get_default_typing_target(self):
        """Default to width when user starts typing numbers."""
        return hb_placement.TypingTarget.WIDTH
    
    def handle_typing_event(self, event) -> bool:
        """Extended to handle arrow keys and W for switching input mode.
        
        Workflow: type 30 → left arrow → type 5 → Enter
        = set width to 30", then place 5" from left edge.
        
        Switching modes (arrow keys, W, H) applies the current value
        first, then clears and starts the new input mode.
        """
        
        if event.value == 'PRESS':
            # Left arrow - apply current value, switch to offset from left
            if event.type == 'LEFT_ARROW':
                self.offset_from_right = False
                if self.placement_state == hb_placement.PlacementState.TYPING and self.typed_value:
                    self.apply_typed_value()
                self.start_typing(hb_placement.TypingTarget.OFFSET_X)
                return True
            
            # Right arrow - apply current value, switch to offset from right
            if event.type == 'RIGHT_ARROW':
                self.offset_from_right = True
                if self.placement_state == hb_placement.PlacementState.TYPING and self.typed_value:
                    self.apply_typed_value()
                self.start_typing(hb_placement.TypingTarget.OFFSET_RIGHT)
                return True
            
            # W - apply current value, switch to width
            if event.type == 'W':
                if self.placement_state == hb_placement.PlacementState.TYPING and self.typed_value:
                    self.apply_typed_value()
                self.start_typing(hb_placement.TypingTarget.WIDTH)
                return True
            
            # H - apply current value, switch to height
            if event.type == 'H':
                if self.placement_state == hb_placement.PlacementState.TYPING and self.typed_value:
                    self.apply_typed_value()
                self.start_typing(hb_placement.TypingTarget.HEIGHT)
                return True
        
        # Fall back to base typing handler
        return super().handle_typing_event(event)
    
    def apply_typed_value(self):
        """Apply typed value based on current target."""
        parsed = self.parse_typed_distance()
        if parsed is None:
            self.stop_typing()
            return
        
        obj = self.get_placed_object()
        if not obj:
            self.stop_typing()
            return
            
        if self.typing_target == hb_placement.TypingTarget.OFFSET_X:
            # Offset from left
            self.placement_x = parsed
            obj.location.x = parsed
            self.offset_from_right = False
            self.position_locked = True  # Lock position after explicit input
            
        elif self.typing_target == hb_placement.TypingTarget.OFFSET_RIGHT:
            # Offset from right - calculate X from right edge
            if self.selected_wall:
                obj_width = self.get_placed_object_width()
                self.placement_x = self.wall_length - parsed - obj_width
                obj.location.x = self.placement_x
            self.offset_from_right = True
            self.position_locked = True  # Lock position after explicit input
            
        elif self.typing_target == hb_placement.TypingTarget.WIDTH:
            self.set_placed_object_width(parsed)
            # Recalculate position if offset from right
            if self.offset_from_right and self.selected_wall:
                # Keep right edge in same place
                self.update_position_for_width_change()
                
        elif self.typing_target == hb_placement.TypingTarget.HEIGHT:
            self.set_placed_object_height(parsed)
        
        self.stop_typing()
    
    def set_placed_object_height(self, height: float):
        """Override this to set height. Default does nothing."""
        pass

    def get_placed_object_height(self) -> float:
        """Override to return the placed object's height (Z dim)."""
        return 0.0

    def set_placed_object_depth(self, depth: float):
        """Override to set the placed object's depth (Y dim, matched to wall thickness)."""
        pass

    def get_two_point_z_offset(self, context) -> float:
        """Override to return the placement Z offset.
        Default 0 (doors). Windows override to props.window_height_from_floor."""
        return 0.0

    def update_position_for_width_change(self):
        """Recalculate X position after width change when offset from right."""
        pass
    
    def on_typed_value_changed(self):
        """Update preview as user types."""
        if not self.typed_value:
            return
            
        parsed = self.parse_typed_distance()
        if parsed is None:
            return
            
        obj = self.get_placed_object()
        if not obj:
            return
        
        if self.typing_target == hb_placement.TypingTarget.OFFSET_X:
            self.placement_x = parsed
            obj.location.x = parsed
            
        elif self.typing_target == hb_placement.TypingTarget.OFFSET_RIGHT:
            if self.selected_wall:
                obj_width = self.get_placed_object_width()
                self.placement_x = self.wall_length - parsed - obj_width
                obj.location.x = self.placement_x
                
        elif self.typing_target == hb_placement.TypingTarget.WIDTH:
            self.set_placed_object_width(parsed)
            
        elif self.typing_target == hb_placement.TypingTarget.HEIGHT:
            self.set_placed_object_height(parsed)
        
        # Refresh dimensions after value change
        self.refresh_placement_dimensions()
    
    def refresh_placement_dimensions(self):
        """Override in subclass to refresh dimensions after typing changes."""
        pass
    
    def get_offset_display(self, context) -> str:
        """Get formatted offset string showing distance from appropriate edge."""
        unit_settings = context.scene.unit_settings
        obj_width = self.get_placed_object_width()
        
        if self.offset_from_right:
            offset_from_right = self.wall_length - self.placement_x - obj_width
            return f"Offset (→): {units.unit_to_string(unit_settings, offset_from_right)}"
        else:
            return f"Offset (←): {units.unit_to_string(unit_settings, self.placement_x)}"
    
    def cut_wall(self, wall_obj, cutting_obj):
        """Add a boolean modifier to the wall to cut a hole for the door/window."""
        # Create a unique modifier name based on the cutting object
        mod_name = f"Boolean_{cutting_obj.name}"
        
        # Check if modifier already exists
        if mod_name in wall_obj.modifiers:
            return wall_obj.modifiers[mod_name]
        
        # Add boolean modifier
        mod = wall_obj.modifiers.new(name=mod_name, type='BOOLEAN')
        mod.operation = 'DIFFERENCE'
        mod.object = cutting_obj
        mod.solver = 'EXACT'
        
        # Hide the cutting object from render
        cutting_obj.hide_render = True
        
        return mod

    # ========== Two-Point Width Mode (D key) ==========

    def init_two_point_state(self):
        """Initialize two-point width mode state. Call from execute()."""
        self.define_width_mode = False
        self.width_start_set = False
        self.width_start_x = 0.0
        self.width_start_wall = None
        self.width_start_gap = (0.0, 0.0)
        self.last_width_direction = 1
        self.width_locked_in_phase2 = False

    def two_point_in_phase1(self) -> bool:
        return self.define_width_mode and not self.width_start_set

    def two_point_in_phase2(self) -> bool:
        return self.define_width_mode and self.width_start_set

    def update_two_point_phase2_position(self, context):
        """Position the placed object using a captured start point + cursor/typed end."""
        if not self.selected_wall:
            return
        placed = self.get_placed_object()
        if placed is None:
            return

        wall = hb_types.GeoNodeWall(self.selected_wall)
        self.wall_length = wall.get_input('Length')
        wall_thickness = wall.get_input('Thickness')
        obj_height = self.get_placed_object_height()
        z_offset = self.get_two_point_z_offset(context)

        # Cursor in wall-local X
        world_loc = Vector(self.hit_location)
        local_loc = self.selected_wall.matrix_world.inverted() @ world_loc
        cursor_x = local_loc.x

        # Direction follows cursor relative to start
        delta = cursor_x - self.width_start_x
        if abs(delta) > 0.001:
            self.last_width_direction = 1 if delta > 0 else -1

        # Width: cursor-driven unless typed value locked it
        if self.width_locked_in_phase2:
            width = self.get_placed_object_width()
        else:
            width = abs(delta)
            width = hb_snap.snap_value_to_grid(width)
            if width < 0.001:
                width = 0.001
            self.set_placed_object_width(width)

        gap_start, gap_end = self.width_start_gap
        max_width = max(0.0, gap_end - gap_start)
        if width > max_width:
            width = max_width
            self.set_placed_object_width(width)

        if self.last_width_direction > 0:
            snap_x = self.width_start_x
        else:
            snap_x = self.width_start_x - width
        snap_x = max(gap_start, min(snap_x, gap_end - width))

        self.placement_x = snap_x
        self.gap_left_boundary = gap_start
        self.gap_right_boundary = gap_end

        placed.parent = self.selected_wall
        placed.location.x = snap_x
        placed.location.y = 0
        placed.location.z = z_offset
        placed.rotation_euler = (0, 0, 0)
        self.set_placed_object_depth(wall_thickness)

        self.update_placement_dimensions(
            context, width, obj_height, wall_thickness, z_offset)

    def update_two_point_phase1_dimensions(self, context):
        """Show gap-relative offset dims at the cursor while picking the start point.
        The placed object itself stays hidden — caller is responsible for that."""
        placed = self.get_placed_object()
        if not self.selected_wall or placed is None:
            self.hide_placement_dimensions()
            return

        wall = hb_types.GeoNodeWall(self.selected_wall)
        self.wall_length = wall.get_input('Length')
        wall_thickness = wall.get_input('Thickness')
        obj_height = self.get_placed_object_height()
        z_offset = self.get_two_point_z_offset(context)

        world_loc = Vector(self.hit_location)
        local_loc = self.selected_wall.matrix_world.inverted() @ world_loc
        cursor_x = hb_snap.snap_value_to_grid(local_loc.x)

        gap_start, gap_end, _ = self.find_placement_gap(
            self.selected_wall, cursor_x, 0.0, exclude_obj=placed)
        cursor_x = max(gap_start, min(cursor_x, gap_end))

        self.placement_x = cursor_x
        self.gap_left_boundary = gap_start
        self.gap_right_boundary = gap_end

        # Reuse update_placement_dimensions with width=0 so left/right are
        # measured from the cursor as a single point.
        self.update_placement_dimensions(
            context, 0.0, obj_height, wall_thickness, z_offset)
        if self.dim_total_width:
            self.dim_total_width.obj.hide_set(True)

    def handle_two_point_phase1_click(self) -> bool:
        """Capture the start point on a left click in phase 1.
        Returns True if the click was consumed (caller should not place)."""
        if not self.two_point_in_phase1():
            return False
        if not self.selected_wall:
            return False
        placed = self.get_placed_object()
        if placed is None:
            return False
        world_loc = Vector(self.hit_location)
        local_loc = self.selected_wall.matrix_world.inverted() @ world_loc
        start_x = hb_snap.snap_value_to_grid(local_loc.x)
        gap_start, gap_end, _ = self.find_placement_gap(
            self.selected_wall, start_x, 0.0, exclude_obj=placed)
        start_x = max(gap_start, min(start_x, gap_end))
        self.width_start_x = start_x
        self.width_start_wall = self.selected_wall
        self.width_start_gap = (gap_start, gap_end)
        self.width_start_set = True
        self.width_locked_in_phase2 = False
        self.last_width_direction = 1
        return True

    def handle_two_point_rmb_undo(self, event) -> bool:
        """Right-click in phase 2 = soft undo (re-pick start). Returns True if handled."""
        if (event.type == 'RIGHTMOUSE' and event.value == 'PRESS'
                and self.two_point_in_phase2()):
            self.width_start_set = False
            self.width_start_wall = None
            self.width_locked_in_phase2 = False
            return True
        return False

    def handle_two_point_d_key(self, event) -> bool:
        """D key toggles two-point width mode. Returns True if handled."""
        if event.type == 'D' and event.value == 'PRESS':
            if self.placement_state != hb_placement.PlacementState.TYPING:
                self.define_width_mode = not self.define_width_mode
                if not self.define_width_mode:
                    self.width_start_set = False
                    self.width_start_wall = None
                    self.width_locked_in_phase2 = False
                return True
        return False

    def maybe_lock_typed_width(self, was_typing_width: bool):
        """Call after handle_typing_event consumed an event. If the user just
        finished typing a WIDTH value while in phase 2, lock the width so the
        cursor only controls direction, not magnitude."""
        if (was_typing_width
                and self.placement_state != hb_placement.PlacementState.TYPING
                and self.two_point_in_phase2()):
            self.width_locked_in_phase2 = True

    # ========== End Two-Point Width Mode ==========


class _PlaceWallObjectBase(bpy.types.Operator, WallObjectPlacementMixin):
    """Base class for door/window placement operators.

    Not registered. Subclasses configure per-type behavior via class
    attributes; the base class implements the entire modal flow.
    """
    bl_options = {'UNDO'}

    # ===== Per-type configuration (override in subclasses) =====
    OBJECT_NAME = "Object"           # passed to GeoNodeCage.create()
    OBJECT_LABEL = "object"          # human label for headers/messages
    BP_FLAG = ""                     # 'IS_ENTRY_DOOR_BP' / 'IS_WINDOW_BP'
    MENU_ID = ""                     # menu shown when clicking the placed object
    WIDTH_PROP_NAME = ""             # 'door_single_width' / 'window_width' / etc.
    HEIGHT_PROP_NAME = ""            # 'door_height' / 'window_height'
    Z_OFFSET_PROP_NAME = None        # None = floor-anchored, else home_builder prop name
    TEXT_KIND = "DOOR"               # GeoNodeText kind: 'DOOR' or 'WINDOW'
    TEXT_NAME = "Object Text"        # GeoNodeText object name
    HAS_SWING = False                # True for single/double door
    SWING_LIST = None                # SINGLE_DOOR_SWINGS / DOUBLE_DOOR_SWINGS / None
    INITIAL_SWING_INPUTS = None      # dict of initial inputs to set on the swing object
    RESET_Z_WHEN_FREE = True         # set z=0 when off-wall (False for window)

    # ===== Abstract method implementations (mixin protocol) =====

    def get_placed_object(self):
        return self.placed_obj.obj if self.placed_obj else None

    def get_placed_object_width(self) -> float:
        if self.placed_obj:
            return self.placed_obj.get_input('Dim X')
        return 0.0

    def set_placed_object_width(self, width: float):
        if self.placed_obj:
            self.placed_obj.set_input('Dim X', width)

    def get_placed_object_height(self) -> float:
        if self.placed_obj:
            return self.placed_obj.get_input('Dim Z')
        return 0.0

    def set_placed_object_height(self, height: float):
        if self.placed_obj:
            self.placed_obj.set_input('Dim Z', height)

    def set_placed_object_depth(self, depth: float):
        if self.placed_obj:
            self.placed_obj.set_input('Dim Y', depth)

    def get_two_point_z_offset(self, context) -> float:
        if self.Z_OFFSET_PROP_NAME:
            return getattr(context.scene.home_builder, self.Z_OFFSET_PROP_NAME)
        return 0.0

    # ===== Door swing (no-ops if HAS_SWING is False) =====

    def apply_door_swing_type(self):
        if not self.HAS_SWING or not self.swing_obj:
            return
        swing_label, inputs = self.SWING_LIST[self.door_swing_index]
        for input_name, value in inputs.items():
            self.swing_obj.set_input(input_name, value)

    def cycle_door_swing(self, direction: int):
        if not self.HAS_SWING:
            return
        self.door_swing_index = (self.door_swing_index + direction) % len(self.SWING_LIST)
        self.apply_door_swing_type()

    # ===== Object creation =====

    def create_placed_object(self, context):
        """Create the placed object: cage + text + optional swing annotation."""
        props = context.scene.home_builder
        hb_wm = bpy.context.window_manager.home_builder
        add_on_prefs = hb_wm.get_user_preferences(bpy.context)

        self.placed_obj = hb_types.GeoNodeCage()
        self.placed_obj.create(self.OBJECT_NAME)
        if self.BP_FLAG:
            self.placed_obj.obj[self.BP_FLAG] = True
        if self.MENU_ID:
            self.placed_obj.obj['MENU_ID'] = self.MENU_ID
        self.placed_obj.set_input('Dim X', getattr(props, self.WIDTH_PROP_NAME))
        self.placed_obj.set_input('Dim Y', props.wall_thickness)
        self.placed_obj.set_input('Dim Z', getattr(props, self.HEIGHT_PROP_NAME))
        self.placed_obj.obj.color = add_on_prefs.door_window_color
        if props.show_entry_door_and_window_cages:
            self.placed_obj.obj.display_type = 'TEXTURED'
            self.placed_obj.obj.show_in_front = True
        else:
            self.placed_obj.obj.display_type = 'WIRE'

        dim_x = self.placed_obj.var_input('Dim X', 'dim_x')
        dim_y = self.placed_obj.var_input('Dim Y', 'dim_y')
        dim_z = self.placed_obj.var_input('Dim Z', 'dim_z')

        # Optional swing annotation (door subclasses only)
        self.swing_obj = None
        if self.HAS_SWING:
            self.swing_obj = hb_types.GeoNodeDoorSwing()
            self.swing_obj.create('Door Swing Annotation')
            self.swing_obj.obj.parent = self.placed_obj.obj
            self.swing_obj.driver_input("Dim X", 'dim_x', [dim_x])
            self.swing_obj.driver_input("Dim Y", 'dim_y', [dim_y])
            if self.INITIAL_SWING_INPUTS:
                for k, v in self.INITIAL_SWING_INPUTS.items():
                    self.swing_obj.set_input(k, v)

        # Text annotation
        text = GeoNodeText()
        text.create(self.TEXT_NAME, self.TEXT_KIND, props.annotation_text_size)
        text.obj.parent = self.placed_obj.obj
        text.obj.rotation_euler.x = math.radians(90)
        text.driver_location("x", 'dim_x/2', [dim_x])
        text.driver_location("y", 'dim_y/2', [dim_y])
        text.driver_location("z", 'dim_z/2', [dim_z])
        text.set_alignment('CENTER', 'CENTER')

        self.register_placement_object(self.placed_obj.obj)
        self.create_placement_dimensions()

    # ===== Position helpers =====

    def set_position_on_wall(self):
        if not self.selected_wall or not self.placed_obj:
            return

        # Two-point width mode, phase 2: anchored to a captured start point
        if self.two_point_in_phase2() and self.width_start_wall is not None:
            if self.width_start_wall.name in bpy.data.objects:
                self.selected_wall = self.width_start_wall
                self.update_two_point_phase2_position(bpy.context)
                return
            self.width_start_set = False
            self.width_start_wall = None
            self.width_locked_in_phase2 = False

        wall = hb_types.GeoNodeWall(self.selected_wall)
        self.wall_length = wall.get_input('Length')
        wall_thickness = wall.get_input('Thickness')
        obj_width = self.get_placed_object_width()
        obj_height = self.get_placed_object_height()
        z_offset = self.get_two_point_z_offset(bpy.context)

        world_loc = Vector(self.hit_location)
        local_loc = self.selected_wall.matrix_world.inverted() @ world_loc
        cursor_x = local_loc.x

        gap_start, gap_end, snap_x = self.find_placement_gap(
            self.selected_wall, cursor_x, obj_width,
            exclude_obj=self.placed_obj.obj
        )
        self.gap_left_boundary = gap_start
        self.gap_right_boundary = gap_end

        snap_x = hb_snap.snap_value_to_grid(snap_x)
        snap_x = max(0, min(snap_x, self.wall_length - obj_width))
        self.placement_x = snap_x

        self.placed_obj.obj.parent = self.selected_wall
        self.placed_obj.obj.location.x = snap_x
        self.placed_obj.obj.location.y = 0
        self.placed_obj.obj.location.z = z_offset
        self.placed_obj.obj.rotation_euler = (0, 0, 0)
        self.placed_obj.set_input("Dim Y", wall_thickness)

        self.update_placement_dimensions(
            bpy.context, obj_width, obj_height, wall_thickness, z_offset)

    def set_position_free(self):
        if self.placed_obj and self.hit_location:
            self.placed_obj.obj.parent = None
            self.placed_obj.obj.location = hb_snap.snap_vector_to_grid(Vector(self.hit_location))
            if self.RESET_Z_WHEN_FREE:
                self.placed_obj.obj.location.z = 0
        self.hide_placement_dimensions()

    def refresh_placement_dimensions(self):
        if self.selected_wall and self.placed_obj:
            wall = hb_types.GeoNodeWall(self.selected_wall)
            wall_thickness = wall.get_input('Thickness')
            obj_width = self.get_placed_object_width()
            obj_height = self.get_placed_object_height()
            z_offset = self.get_two_point_z_offset(bpy.context)
            self.update_placement_dimensions(
                bpy.context, obj_width, obj_height, wall_thickness, z_offset)

    # ===== Header text =====

    def update_header(self, context):
        mode_tag = " [2-Point]" if self.define_width_mode else ""
        swing_label = ""
        if self.HAS_SWING and self.SWING_LIST:
            swing_label = self.SWING_LIST[self.door_swing_index][0]
        swing_text = f" | Swing: {swing_label}" if swing_label else ""
        swing_keys = " | \u2191/\u2193 swing" if self.HAS_SWING else ""
        label = self.OBJECT_LABEL

        if self.placement_state == hb_placement.PlacementState.TYPING:
            target_name = {
                hb_placement.TypingTarget.OFFSET_X: "Offset (\u2190)",
                hb_placement.TypingTarget.OFFSET_RIGHT: "Offset (\u2192)",
                hb_placement.TypingTarget.WIDTH: "Width",
                hb_placement.TypingTarget.HEIGHT: "Height",
            }.get(self.typing_target, "Value")
            text = f"{target_name}: {self.typed_value}_{swing_text} | Enter to confirm | W width | H height | Esc cancel{mode_tag}"
        elif self.two_point_in_phase2():
            width_str = units.unit_to_string(context.scene.unit_settings, self.get_placed_object_width())
            lock_hint = " [W locked]" if self.width_locked_in_phase2 else ""
            text = f"{mode_tag} Click end point | Width: {width_str}{lock_hint}{swing_text} | W: type width | Right-click: re-pick start | D: exit 2-point | Esc cancel"
        elif self.two_point_in_phase1():
            text = f"{mode_tag} Click start point on wall{swing_text} | W: type width | D: exit 2-point | Esc cancel"
        elif self.selected_wall:
            offset_str = self.get_offset_display(context)
            width_str = units.unit_to_string(context.scene.unit_settings, self.get_placed_object_width())
            text = f"{offset_str} | Width: {width_str}{swing_text}{swing_keys} | \u2190/\u2192 offset | W width | D: 2-point width | Click to place | Esc cancel"
        else:
            text = f"Move over a wall to place {label}{swing_keys} | D: 2-point width | Esc to cancel"

        hb_placement.draw_header_text(context, text)

    # ===== Operator lifecycle =====

    def execute(self, context):
        self.init_placement(context)

        self.placed_obj = None
        self.swing_obj = None
        self.door_swing_index = 0
        self.selected_wall = None
        self.wall_length = 0
        self.placement_x = 0
        self.offset_from_right = False
        self.position_locked = False

        self.init_two_point_state()

        self.create_placed_object(context)

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        context.window.cursor_set('CROSSHAIR')

        if event.type == "INBETWEEN_MOUSEMOVE":
            return {'RUNNING_MODAL'}

        # Up/Down arrow - cycle door swing type (only if HAS_SWING)
        if self.HAS_SWING and event.type in {'UP_ARROW', 'DOWN_ARROW'} and event.value == 'PRESS':
            direction = 1 if event.type == 'UP_ARROW' else -1
            self.cycle_door_swing(direction)
            self.update_header(context)
            return {'RUNNING_MODAL'}

        # Let mixin handle typing events first; detect finish-of-WIDTH-typing
        # to lock the typed width during two-point phase 2.
        was_typing_width = (
            self.placement_state == hb_placement.PlacementState.TYPING
            and self.typing_target == hb_placement.TypingTarget.WIDTH
        )
        if self.handle_typing_event(event):
            self.maybe_lock_typed_width(was_typing_width)
            self.update_header(context)
            return {'RUNNING_MODAL'}

        # Update snap (hide placed object during raycast)
        self.placed_obj.obj.hide_set(True)
        self.update_snap(context, event)
        self.placed_obj.obj.hide_set(False)

        # Check if we're over a wall
        self.selected_wall = None
        if self.hit_object and 'IS_WALL_BP' in self.hit_object:
            self.selected_wall = self.hit_object
            wall = hb_types.GeoNodeWall(self.selected_wall)
            self.wall_length = wall.get_input('Length')

        # Two-point phase 1: hide the object so the user picks a clean start,
        # but still show the gap-relative offset dimensions.
        in_phase1 = self.two_point_in_phase1()
        if in_phase1:
            self.placed_obj.obj.hide_set(True)
            self.update_two_point_phase1_dimensions(context)

        typing_offset = (self.placement_state == hb_placement.PlacementState.TYPING
                         and self.typing_target in (hb_placement.TypingTarget.OFFSET_X,
                                                    hb_placement.TypingTarget.OFFSET_RIGHT))
        if not typing_offset and not self.position_locked and not in_phase1:
            if self.selected_wall:
                self.set_position_on_wall()
            else:
                self.set_position_free()
                self.position_locked = False

        self.update_header(context)

        # Left click - place (or capture start point in two-point phase 1)
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if self.selected_wall:
                if self.handle_two_point_phase1_click():
                    return {'RUNNING_MODAL'}
                if self.placed_obj.obj in self.placement_objects:
                    self.placement_objects.remove(self.placed_obj.obj)
                self.delete_placement_dimensions()
                self.cut_wall(self.selected_wall, self.placed_obj.obj)
                hb_placement.clear_header_text(context)
                context.window.cursor_set('DEFAULT')
                return {'FINISHED'}
            else:
                self.report({'WARNING'}, f"{self.OBJECT_LABEL.capitalize()} must be placed on a wall")
                return {'RUNNING_MODAL'}

        # Right click in two-point phase 2 = soft undo
        if self.handle_two_point_rmb_undo(event):
            self.update_header(context)
            return {'RUNNING_MODAL'}

        if event.type in {'RIGHTMOUSE', 'ESC'} and event.value == 'PRESS':
            self.cancel_placement(context)
            hb_placement.clear_header_text(context)
            return {'CANCELLED'}

        # D key toggles two-point width mode
        if self.handle_two_point_d_key(event):
            self.update_header(context)
            return {'RUNNING_MODAL'}

        if hb_snap.event_is_pass_through(event):
            return {'PASS_THROUGH'}

        return {'RUNNING_MODAL'}


class home_builder_doors_windows_OT_place_door(_PlaceWallObjectBase):
    bl_idname = "home_builder_doors_windows.place_door"
    bl_label = "Place Door"
    bl_description = "Place a door on a wall. Arrow keys for offset direction, W for width, Up/Down for swing type, Escape to cancel"

    OBJECT_NAME = "Door"
    OBJECT_LABEL = "door"
    BP_FLAG = "IS_ENTRY_DOOR_BP"
    MENU_ID = "HOME_BUILDER_MT_door_commands"
    WIDTH_PROP_NAME = "door_single_width"
    HEIGHT_PROP_NAME = "door_height"
    TEXT_KIND = "DOOR"
    TEXT_NAME = "Door Text"
    HAS_SWING = True
    SWING_LIST = SINGLE_DOOR_SWINGS


class home_builder_doors_windows_OT_place_double_door(_PlaceWallObjectBase):
    bl_idname = "home_builder_doors_windows.place_double_door"
    bl_label = "Place Double Door"
    bl_description = "Place a double door on a wall. Arrow keys for offset direction, W for width, Up/Down for swing type, Escape to cancel"

    OBJECT_NAME = "Double Door"
    OBJECT_LABEL = "double door"
    BP_FLAG = "IS_ENTRY_DOOR_BP"
    MENU_ID = "HOME_BUILDER_MT_door_commands"
    WIDTH_PROP_NAME = "door_double_width"
    HEIGHT_PROP_NAME = "door_height"
    TEXT_KIND = "DOOR"
    TEXT_NAME = "Door Text"
    HAS_SWING = True
    SWING_LIST = DOUBLE_DOOR_SWINGS
    INITIAL_SWING_INPUTS = {'Is Double': True, 'Swing Inside': True}


class home_builder_doors_windows_OT_place_open_door(_PlaceWallObjectBase):
    bl_idname = "home_builder_doors_windows.place_open_door"
    bl_label = "Place Open Door"
    bl_description = "Place an open doorway on a wall. Arrow keys for offset direction, W for width, Escape to cancel"

    OBJECT_NAME = "Open Door"
    OBJECT_LABEL = "open door"
    BP_FLAG = "IS_ENTRY_DOOR_BP"
    MENU_ID = "HOME_BUILDER_MT_door_commands"
    WIDTH_PROP_NAME = "door_single_width"
    HEIGHT_PROP_NAME = "door_height"
    TEXT_KIND = "DOOR"
    TEXT_NAME = "Door Text"


class home_builder_doors_windows_OT_place_window(_PlaceWallObjectBase):
    bl_idname = "home_builder_doors_windows.place_window"
    bl_label = "Place Window"
    bl_description = "Place a window on a wall. Arrow keys for offset direction, W for width, Escape to cancel"

    OBJECT_NAME = "Window"
    OBJECT_LABEL = "window"
    BP_FLAG = "IS_WINDOW_BP"
    MENU_ID = "HOME_BUILDER_MT_window_commands"
    WIDTH_PROP_NAME = "window_width"
    HEIGHT_PROP_NAME = "window_height"
    Z_OFFSET_PROP_NAME = "window_height_from_floor"
    TEXT_KIND = "WINDOW"
    TEXT_NAME = "Window Text"
    RESET_Z_WHEN_FREE = False


class home_builder_doors_windows_OT_door_prompts(bpy.types.Operator):
    bl_idname = "home_builder_doors_windows.door_prompts"
    bl_label = "Door Prompts"
    bl_description = "Edit door properties"
    bl_options = {'UNDO'}

    door_width: bpy.props.FloatProperty(name="Width", unit='LENGTH', precision=5)  # type: ignore
    door_height: bpy.props.FloatProperty(name="Height", unit='LENGTH', precision=5)  # type: ignore

    door = None

    @classmethod
    def poll(cls, context):
        return context.object and context.object.get('IS_ENTRY_DOOR_BP')

    def check(self, context):
        self.door.set_input('Dim X', self.door_width)
        self.door.set_input('Dim Z', self.door_height)
        return True

    def invoke(self, context, event):
        self.door = hb_types.GeoNodeCage(context.object)
        self.door_width = self.door.get_input('Dim X')
        self.door_height = self.door.get_input('Dim Z')
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        
        row = box.row()
        row.label(text="Width:")
        row.prop(self, 'door_width', text="")
        
        row = box.row()
        row.label(text="Height:")
        row.prop(self, 'door_height', text="")
        
        row = box.row()
        row.label(text="Location X:")
        row.prop(self.door.obj, 'location', index=0, text="")


class home_builder_doors_windows_OT_window_prompts(bpy.types.Operator):
    bl_idname = "home_builder_doors_windows.window_prompts"
    bl_label = "Window Prompts"
    bl_description = "Edit window properties"
    bl_options = {'UNDO'}

    window_width: bpy.props.FloatProperty(name="Width", unit='LENGTH', precision=5)  # type: ignore
    window_height: bpy.props.FloatProperty(name="Height", unit='LENGTH', precision=5)  # type: ignore
    height_from_floor: bpy.props.FloatProperty(name="Height From Floor", unit='LENGTH', precision=5)  # type: ignore

    window = None

    @classmethod
    def poll(cls, context):
        return context.object and context.object.get('IS_WINDOW_BP')

    def check(self, context):
        self.window.set_input('Dim X', self.window_width)
        self.window.set_input('Dim Z', self.window_height)
        self.window.obj.location.z = self.height_from_floor
        return True

    def invoke(self, context, event):
        self.window = hb_types.GeoNodeCage(context.object)
        self.window_width = self.window.get_input('Dim X')
        self.window_height = self.window.get_input('Dim Z')
        self.height_from_floor = self.window.obj.location.z
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        
        row = box.row()
        row.label(text="Width:")
        row.prop(self, 'window_width', text="")
        
        row = box.row()
        row.label(text="Height:")
        row.prop(self, 'window_height', text="")
        
        row = box.row()
        row.label(text="Height From Floor:")
        row.prop(self, 'height_from_floor', text="")
        
        row = box.row()
        row.label(text="Location X:")
        row.prop(self.window.obj, 'location', index=0, text="")


class home_builder_doors_windows_OT_flip_door_swing(bpy.types.Operator):
    bl_idname = "home_builder_doors_windows.flip_door_swing"
    bl_label = "Flip Door Swing"
    bl_description = "Flip the door swing direction (swings inside/outside)"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object and context.object.get('IS_ENTRY_DOOR_BP')

    def execute(self, context):
        door_obj = context.object
        # Find the door swing child
        for child in door_obj.children:
            if 'Door Swing' in child.name:
                door_swing = hb_types.GeoNodeObject(child)
                try:
                    current = door_swing.get_input('Swing Inside')
                    door_swing.set_input('Swing Inside', not current)
                    self.report({'INFO'}, "Door swing flipped")
                except:
                    self.report({'WARNING'}, "Could not find Swing Inside input")
                break
        return {'FINISHED'}


class home_builder_doors_windows_OT_flip_door_hand(bpy.types.Operator):
    bl_idname = "home_builder_doors_windows.flip_door_hand"
    bl_label = "Flip Door Hand"
    bl_description = "Flip the door hand (left/right hinge)"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object and context.object.get('IS_ENTRY_DOOR_BP')

    def execute(self, context):
        door_obj = context.object
        # Find the door swing child
        for child in door_obj.children:
            if 'Door Swing' in child.name:
                door_swing = hb_types.GeoNodeObject(child)
                try:
                    current = door_swing.get_input('Is Left')
                    door_swing.set_input('Is Left', not current)
                    self.report({'INFO'}, "Door hand flipped")
                except:
                    self.report({'WARNING'}, "Could not find Is Left input")
                break
        return {'FINISHED'}


class home_builder_doors_windows_OT_toggle_double_door(bpy.types.Operator):
    bl_idname = "home_builder_doors_windows.toggle_double_door"
    bl_label = "Toggle Double Door"
    bl_description = "Toggle between single and double door"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object and context.object.get('IS_ENTRY_DOOR_BP')

    def execute(self, context):
        door_obj = context.object
        # Find the door swing child
        for child in door_obj.children:
            if 'Door Swing' in child.name:
                door_swing = hb_types.GeoNodeObject(child)
                try:
                    current = door_swing.get_input('Is Double')
                    door_swing.set_input('Is Double', not current)
                    status = "double" if not current else "single"
                    self.report({'INFO'}, f"Door set to {status}")
                except:
                    self.report({'WARNING'}, "Could not find Is Double input")
                break
        return {'FINISHED'}


class home_builder_doors_windows_OT_delete_door_window(bpy.types.Operator):
    bl_idname = "home_builder_doors_windows.delete_door_window"
    bl_label = "Delete Door/Window"
    bl_description = "Delete the selected door or window"
    bl_options = {'UNDO'}

    object_type: bpy.props.StringProperty(name="Object Type", default='DOOR')  # type: ignore

    @classmethod
    def poll(cls, context):
        if not context.object:
            return False
        return context.object.get('IS_ENTRY_DOOR_BP') or context.object.get('IS_WINDOW_BP')

    def execute(self, context):
        obj = context.object
        wall = obj.parent
        
        # Remove the boolean modifier from the wall if present
        if wall and 'IS_WALL_BP' in wall:
            # Find and remove the boolean modifier for this door/window
            for mod in wall.modifiers:
                if mod.type == 'BOOLEAN' and mod.object == obj:
                    wall.modifiers.remove(mod)
                    break
        
        # Delete all children first
        children_to_delete = list(obj.children)
        for child in children_to_delete:
            bpy.data.objects.remove(child, do_unlink=True)
        
        # Delete the door/window object
        bpy.data.objects.remove(obj, do_unlink=True)
        
        self.report({'INFO'}, f"{self.object_type.title()} deleted")
        return {'FINISHED'}


classes = (
    home_builder_doors_windows_OT_place_door,
    home_builder_doors_windows_OT_place_double_door,
    home_builder_doors_windows_OT_place_open_door,
    home_builder_doors_windows_OT_place_window,
    home_builder_doors_windows_OT_door_prompts,
    home_builder_doors_windows_OT_window_prompts,
    home_builder_doors_windows_OT_flip_door_swing,
    home_builder_doors_windows_OT_flip_door_hand,
    home_builder_doors_windows_OT_toggle_double_door,
    home_builder_doors_windows_OT_delete_door_window,
)

register, unregister = bpy.utils.register_classes_factory(classes)
