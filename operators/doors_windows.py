import bpy
from .. import hb_types, hb_snap, hb_placement, units
import math
from mathutils import Vector
from ..hb_details import GeoNodeText

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
        """Default to offset from left."""
        return hb_placement.TypingTarget.OFFSET_X
    
    def handle_typing_event(self, event) -> bool:
        """Extended to handle arrow keys and W for switching input mode."""
        
        # Check for mode-switching keys before typing starts
        if event.value == 'PRESS':
            # Left arrow - offset from left
            if event.type == 'LEFT_ARROW':
                self.offset_from_right = False
                if self.placement_state == hb_placement.PlacementState.TYPING:
                    # Already typing, just switch mode
                    self.typing_target = hb_placement.TypingTarget.OFFSET_X
                else:
                    # Start typing offset from left
                    self.start_typing(hb_placement.TypingTarget.OFFSET_X)
                self.on_typed_value_changed()
                return True
            
            # Right arrow - offset from right
            if event.type == 'RIGHT_ARROW':
                self.offset_from_right = True
                if self.placement_state == hb_placement.PlacementState.TYPING:
                    # Already typing, just switch mode
                    self.typing_target = hb_placement.TypingTarget.OFFSET_RIGHT
                else:
                    # Start typing offset from right
                    self.start_typing(hb_placement.TypingTarget.OFFSET_RIGHT)
                self.on_typed_value_changed()
                return True
            
            # W - width
            if event.type == 'W':
                if self.placement_state == hb_placement.PlacementState.TYPING:
                    self.typing_target = hb_placement.TypingTarget.WIDTH
                else:
                    self.start_typing(hb_placement.TypingTarget.WIDTH)
                self.on_typed_value_changed()
                return True
            
            # H - height (for windows/doors)
            if event.type == 'H':
                if self.placement_state == hb_placement.PlacementState.TYPING:
                    self.typing_target = hb_placement.TypingTarget.HEIGHT
                else:
                    self.start_typing(hb_placement.TypingTarget.HEIGHT)
                self.on_typed_value_changed()
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


class home_builder_doors_windows_OT_place_door(bpy.types.Operator, WallObjectPlacementMixin):
    bl_idname = "home_builder_doors_windows.place_door"
    bl_label = "Place Door"
    bl_description = "Place a door on a wall. Arrow keys for offset direction, W for width, Escape to cancel"
    bl_options = {'UNDO'}

    door = None

    def get_placed_object(self):
        return self.door.obj if self.door else None
    
    def get_placed_object_width(self) -> float:
        if self.door:
            return self.door.get_input('Dim X')
        return 0
    
    def set_placed_object_width(self, width: float):
        if self.door:
            self.door.set_input('Dim X', width)
    
    def set_placed_object_height(self, height: float):
        if self.door:
            self.door.set_input('Dim Z', height)

    def create_door(self, context):
        """Create the door object."""
        props = context.scene.home_builder
        hb_wm = bpy.context.window_manager.home_builder
        add_on_prefs = hb_wm.get_user_preferences(bpy.context)  

        self.door = hb_types.GeoNodeCage()
        self.door.create("Door")
        self.door.obj['IS_ENTRY_DOOR_BP'] = True
        self.door.obj['MENU_ID'] = 'HOME_BUILDER_MT_door_commands'
        self.door.set_input('Dim X', props.door_single_width)
        self.door.set_input('Dim Y', props.wall_thickness)
        self.door.set_input('Dim Z', props.door_height)
        self.door.obj.color = add_on_prefs.door_window_color
        if props.show_entry_door_and_window_cages:
            self.door.obj.display_type = 'TEXTURED'
            self.door.obj.show_in_front = True
        else:
            self.door.obj.display_type = 'WIRE'

        dim_x = self.door.var_input('Dim X', 'dim_x')
        dim_y = self.door.var_input('Dim Y', 'dim_y')
        dim_z = self.door.var_input('Dim Z', 'dim_z')

        door_swing = hb_types.GeoNodeDoorSwing()
        door_swing.create('Door Swing Annotation')
        door_swing.obj.parent = self.door.obj
        door_swing.driver_input("Dim X", 'dim_x', [dim_x])
        door_swing.driver_input("Dim Y", 'dim_y', [dim_y])

        door_text = GeoNodeText()
        door_text.create('Door Text', 'DOOR', props.annotation_text_size)
        door_text.obj.parent = self.door.obj
        door_text.obj.rotation_euler.x = math.radians(90)
        door_text.driver_location("x", 'dim_x/2', [dim_x])
        door_text.driver_location("y", 'dim_y/2', [dim_y])
        door_text.driver_location("z", 'dim_z/2', [dim_z])
        door_text.set_alignment('CENTER', 'CENTER')
        
        self.register_placement_object(self.door.obj)
        
        # Create placement dimensions
        self.create_placement_dimensions()

    def set_position_on_wall(self):
        """Position door on the selected wall with gap-aware snapping."""
        if not self.selected_wall or not self.door:
            return
            
        wall = hb_types.GeoNodeWall(self.selected_wall)
        self.wall_length = wall.get_input('Length')
        wall_thickness = wall.get_input('Thickness')
        door_width = self.get_placed_object_width()
        door_height = self.door.get_input('Dim Z')
        
        # Get local X position on wall from world hit location
        world_loc = Vector(self.hit_location)
        local_loc = self.selected_wall.matrix_world.inverted() @ world_loc
        cursor_x = local_loc.x
        
        # Find available gap and snap position (exclude self from collision check)
        gap_start, gap_end, snap_x = self.find_placement_gap(
            self.selected_wall, 
            cursor_x, 
            door_width,
            exclude_obj=self.door.obj
        )
        
        # Store gap boundaries for dimension display
        self.gap_left_boundary = gap_start
        self.gap_right_boundary = gap_end
        
        # Apply grid snapping
        snap_x = hb_snap.snap_value_to_grid(snap_x)
        
        # Clamp to wall bounds
        snap_x = max(0, min(snap_x, self.wall_length - door_width))
        
        self.placement_x = snap_x
        
        # Parent to wall and set position
        self.door.obj.parent = self.selected_wall
        self.door.obj.location.x = snap_x
        self.door.obj.location.y = 0
        self.door.obj.location.z = 0
        self.door.obj.rotation_euler = (0, 0, 0)
        
        # Match door depth to wall thickness
        self.door.set_input("Dim Y", wall_thickness)
        
        # Update placement dimensions
        self.update_placement_dimensions(bpy.context, door_width, door_height, wall_thickness)

    def set_position_free(self):
        """Position door freely when not over a wall."""
        if self.door and self.hit_location:
            self.door.obj.parent = None
            self.door.obj.location = hb_snap.snap_vector_to_grid(Vector(self.hit_location))
            self.door.obj.location.z = 0
        # Hide dimensions when not on wall
        self.hide_placement_dimensions()

    def refresh_placement_dimensions(self):
        """Refresh dimensions after typing changes."""
        if self.selected_wall and self.door:
            wall = hb_types.GeoNodeWall(self.selected_wall)
            wall_thickness = wall.get_input('Thickness')
            door_width = self.get_placed_object_width()
            door_height = self.door.get_input('Dim Z')
            self.update_placement_dimensions(bpy.context, door_width, door_height, wall_thickness)

    def update_header(self, context):
        """Update header text with instructions."""
        if self.placement_state == hb_placement.PlacementState.TYPING:
            target_name = {
                hb_placement.TypingTarget.OFFSET_X: "Offset (←)",
                hb_placement.TypingTarget.OFFSET_RIGHT: "Offset (→)",
                hb_placement.TypingTarget.WIDTH: "Width",
                hb_placement.TypingTarget.HEIGHT: "Height",
            }.get(self.typing_target, "Value")
            text = f"{target_name}: {self.typed_value}_ | Enter to confirm | ←/→ offset | W width | H height | Esc cancel"
        elif self.selected_wall:
            offset_str = self.get_offset_display(context)
            width_str = units.unit_to_string(context.scene.unit_settings, self.get_placed_object_width())
            text = f"{offset_str} | Width: {width_str} | ←/→ offset | W width | Click to place | Esc cancel"
        else:
            text = "Move over a wall to place door | Esc to cancel"
        
        hb_placement.draw_header_text(context, text)

    def execute(self, context):
        self.init_placement(context)
        
        self.door = None
        self.selected_wall = None
        self.wall_length = 0
        self.placement_x = 0
        self.offset_from_right = False
        self.position_locked = False

        self.create_door(context)

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        context.window.cursor_set('CROSSHAIR')

        if event.type == "INBETWEEN_MOUSEMOVE":
            return {'RUNNING_MODAL'}

        # Let mixin handle typing events first
        if self.handle_typing_event(event):
            self.update_header(context)
            return {'RUNNING_MODAL'}

        # Update snap (hide door during raycast)
        self.door.obj.hide_set(True)
        self.update_snap(context, event)
        self.door.obj.hide_set(False)

        # Check if we're over a wall
        self.selected_wall = None
        if self.hit_object and 'IS_WALL_BP' in self.hit_object:
            self.selected_wall = self.hit_object
            # Update wall length for offset calculations
            wall = hb_types.GeoNodeWall(self.selected_wall)
            self.wall_length = wall.get_input('Length')

        # Update position if not typing and not locked
        if self.placement_state != hb_placement.PlacementState.TYPING:
            if self.selected_wall:
                if not self.position_locked:
                    self.set_position_on_wall()
            else:
                self.set_position_free()
                self.position_locked = False  # Reset lock when off wall

        self.update_header(context)

        # Left click - place door
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if self.selected_wall:
                if self.door.obj in self.placement_objects:
                    self.placement_objects.remove(self.door.obj)
                # Delete placement dimensions
                self.delete_placement_dimensions()
                # Cut hole in wall
                self.cut_wall(self.selected_wall, self.door.obj)
                hb_placement.clear_header_text(context)
                context.window.cursor_set('DEFAULT')
                return {'FINISHED'}
            else:
                self.report({'WARNING'}, "Door must be placed on a wall")
                return {'RUNNING_MODAL'}

        # Right click or Escape - cancel
        if event.type in {'RIGHTMOUSE', 'ESC'} and event.value == 'PRESS':
            self.cancel_placement(context)
            hb_placement.clear_header_text(context)
            return {'CANCELLED'}

        if hb_snap.event_is_pass_through(event):
            return {'PASS_THROUGH'}

        return {'RUNNING_MODAL'}


class home_builder_doors_windows_OT_place_window(bpy.types.Operator, WallObjectPlacementMixin):
    bl_idname = "home_builder_doors_windows.place_window"
    bl_label = "Place Window"
    bl_description = "Place a window on a wall. Arrow keys for offset direction, W for width, Escape to cancel"
    bl_options = {'UNDO'}

    window = None

    def get_placed_object(self):
        return self.window.obj if self.window else None
    
    def get_placed_object_width(self) -> float:
        if self.window:
            return self.window.get_input('Dim X')
        return 0
    
    def set_placed_object_width(self, width: float):
        if self.window:
            self.window.set_input('Dim X', width)
    
    def set_placed_object_height(self, height: float):
        if self.window:
            self.window.set_input('Dim Z', height)

    def create_window(self, context):
        """Create the window object."""
        props = context.scene.home_builder
        hb_wm = bpy.context.window_manager.home_builder
        add_on_prefs = hb_wm.get_user_preferences(bpy.context)  

        self.window = hb_types.GeoNodeCage()
        self.window.create("Window")
        self.window.obj['IS_WINDOW_BP'] = True
        self.window.obj['MENU_ID'] = 'HOME_BUILDER_MT_window_commands'
        self.window.set_input('Dim X', props.window_width)
        self.window.set_input('Dim Y', props.wall_thickness)
        self.window.set_input('Dim Z', props.window_height)
        self.window.obj.color = add_on_prefs.door_window_color
        if props.show_entry_door_and_window_cages:
            self.window.obj.display_type = 'TEXTURED'
            self.window.obj.show_in_front = True
        else:
            self.window.obj.display_type = 'WIRE'

        dim_x = self.window.var_input('Dim X', 'dim_x')
        dim_y = self.window.var_input('Dim Y', 'dim_y')
        dim_z = self.window.var_input('Dim Z', 'dim_z')

        window_text = GeoNodeText()
        window_text.create('Window Text', 'WINDOW', props.annotation_text_size)
        window_text.obj.parent = self.window.obj
        window_text.obj.rotation_euler.x = math.radians(90)
        window_text.driver_location("x", 'dim_x/2', [dim_x])
        window_text.driver_location("y", 'dim_y/2', [dim_y])
        window_text.driver_location("z", 'dim_z/2', [dim_z])
        window_text.set_alignment('CENTER', 'CENTER')

        self.register_placement_object(self.window.obj)
        
        # Create placement dimensions
        self.create_placement_dimensions()

    def set_position_on_wall(self):
        """Position window on the selected wall with gap-aware snapping."""
        if not self.selected_wall or not self.window:
            return
            
        props = bpy.context.scene.home_builder
        wall = hb_types.GeoNodeWall(self.selected_wall)
        self.wall_length = wall.get_input('Length')
        wall_thickness = wall.get_input('Thickness')
        window_width = self.get_placed_object_width()
        window_height = self.window.get_input('Dim Z')
        window_z = props.window_height_from_floor
        
        # Get local X position on wall from world hit location
        world_loc = Vector(self.hit_location)
        local_loc = self.selected_wall.matrix_world.inverted() @ world_loc
        cursor_x = local_loc.x
        
        # Find available gap and snap position (exclude self from collision check)
        gap_start, gap_end, snap_x = self.find_placement_gap(
            self.selected_wall, 
            cursor_x, 
            window_width,
            exclude_obj=self.window.obj
        )
        
        # Store gap boundaries for dimension display
        self.gap_left_boundary = gap_start
        self.gap_right_boundary = gap_end
        
        # Apply grid snapping
        snap_x = hb_snap.snap_value_to_grid(snap_x)
        
        # Clamp to wall bounds
        snap_x = max(0, min(snap_x, self.wall_length - window_width))
        
        self.placement_x = snap_x
        
        # Parent to wall and set position
        self.window.obj.parent = self.selected_wall
        self.window.obj.location.x = snap_x
        self.window.obj.location.y = 0
        self.window.obj.location.z = window_z
        self.window.obj.rotation_euler = (0, 0, 0)
        
        # Match window depth to wall thickness
        self.window.set_input("Dim Y", wall_thickness)
        
        # Update placement dimensions (account for window height from floor)
        self.update_placement_dimensions(bpy.context, window_width, window_height, wall_thickness, window_z)

    def set_position_free(self):
        """Position window freely when not over a wall."""
        if self.window and self.hit_location:
            self.window.obj.parent = None
            self.window.obj.location = hb_snap.snap_vector_to_grid(Vector(self.hit_location))
        # Hide dimensions when not on wall
        self.hide_placement_dimensions()

    def refresh_placement_dimensions(self):
        """Refresh dimensions after typing changes."""
        if self.selected_wall and self.window:
            props = bpy.context.scene.home_builder
            wall = hb_types.GeoNodeWall(self.selected_wall)
            wall_thickness = wall.get_input('Thickness')
            window_width = self.get_placed_object_width()
            window_height = self.window.get_input('Dim Z')
            window_z = props.window_height_from_floor
            self.update_placement_dimensions(bpy.context, window_width, window_height, wall_thickness, window_z)

    def update_header(self, context):
        """Update header text with instructions."""
        if self.placement_state == hb_placement.PlacementState.TYPING:
            target_name = {
                hb_placement.TypingTarget.OFFSET_X: "Offset (←)",
                hb_placement.TypingTarget.OFFSET_RIGHT: "Offset (→)",
                hb_placement.TypingTarget.WIDTH: "Width",
                hb_placement.TypingTarget.HEIGHT: "Height",
            }.get(self.typing_target, "Value")
            text = f"{target_name}: {self.typed_value}_ | Enter to confirm | ←/→ offset | W width | H height | Esc cancel"
        elif self.selected_wall:
            offset_str = self.get_offset_display(context)
            width_str = units.unit_to_string(context.scene.unit_settings, self.get_placed_object_width())
            text = f"{offset_str} | Width: {width_str} | ←/→ offset | W width | Click to place | Esc cancel"
        else:
            text = "Move over a wall to place window | Esc to cancel"
        
        hb_placement.draw_header_text(context, text)

    def execute(self, context):
        self.init_placement(context)
        
        self.window = None
        self.selected_wall = None
        self.wall_length = 0
        self.placement_x = 0
        self.offset_from_right = False
        self.position_locked = False

        self.create_window(context)

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        context.window.cursor_set('CROSSHAIR')

        if event.type == "INBETWEEN_MOUSEMOVE":
            return {'RUNNING_MODAL'}

        # Let mixin handle typing events first
        if self.handle_typing_event(event):
            self.update_header(context)
            return {'RUNNING_MODAL'}

        # Update snap (hide window during raycast)
        self.window.obj.hide_set(True)
        self.update_snap(context, event)
        self.window.obj.hide_set(False)

        # Check if we're over a wall
        self.selected_wall = None
        if self.hit_object and 'IS_WALL_BP' in self.hit_object:
            self.selected_wall = self.hit_object
            # Update wall length for offset calculations
            wall = hb_types.GeoNodeWall(self.selected_wall)
            self.wall_length = wall.get_input('Length')

        # Update position if not typing and not locked
        if self.placement_state != hb_placement.PlacementState.TYPING:
            if self.selected_wall:
                if not self.position_locked:
                    self.set_position_on_wall()
            else:
                self.set_position_free()
                self.position_locked = False  # Reset lock when off wall

        self.update_header(context)

        # Left click - place window
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if self.selected_wall:
                if self.window.obj in self.placement_objects:
                    self.placement_objects.remove(self.window.obj)
                # Delete placement dimensions
                self.delete_placement_dimensions()
                # Cut hole in wall
                self.cut_wall(self.selected_wall, self.window.obj)
                hb_placement.clear_header_text(context)
                context.window.cursor_set('DEFAULT')
                return {'FINISHED'}
            else:
                self.report({'WARNING'}, "Window must be placed on a wall")
                return {'RUNNING_MODAL'}

        # Right click or Escape - cancel
        if event.type in {'RIGHTMOUSE', 'ESC'} and event.value == 'PRESS':
            self.cancel_placement(context)
            hb_placement.clear_header_text(context)
            return {'CANCELLED'}

        if hb_snap.event_is_pass_through(event):
            return {'PASS_THROUGH'}

        return {'RUNNING_MODAL'}




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
    home_builder_doors_windows_OT_place_window,
    home_builder_doors_windows_OT_door_prompts,
    home_builder_doors_windows_OT_window_prompts,
    home_builder_doors_windows_OT_flip_door_swing,
    home_builder_doors_windows_OT_flip_door_hand,
    home_builder_doors_windows_OT_toggle_double_door,
    home_builder_doors_windows_OT_delete_door_window,
)

register, unregister = bpy.utils.register_classes_factory(classes)
