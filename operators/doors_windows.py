import bpy
from .. import hb_types, hb_snap, hb_placement, units
import math
from mathutils import Vector


class home_builder_doors_windows_OT_place_door(bpy.types.Operator, hb_placement.PlacementMixin):
    bl_idname = "home_builder_doors_windows.place_door"
    bl_label = "Place Door"
    bl_description = "Place a door on a wall. Type for exact offset, Escape to cancel"
    bl_options = {'UNDO'}

    # Door-specific state
    door = None
    selected_wall = None
    wall_length: float = 0
    
    # Placement position on wall (local X)
    placement_x: float = 0

    def get_default_typing_target(self):
        """When user starts typing, they're entering X offset."""
        return hb_placement.TypingTarget.OFFSET_X

    def on_typed_value_changed(self):
        """Update door position as user types."""
        if self.typed_value and self.door and self.selected_wall:
            parsed = self.parse_typed_distance()
            if parsed is not None:
                self.placement_x = parsed
                self.door.obj.location.x = parsed
        self.update_header(bpy.context)

    def apply_typed_value(self):
        """Apply typed offset."""
        parsed = self.parse_typed_distance()
        if parsed is not None and self.door:
            self.placement_x = parsed
            self.door.obj.location.x = parsed
        self.stop_typing()

    def create_door(self, context):
        """Create the door object."""
        props = context.scene.home_builder
        self.door = hb_types.GeoNodeObject()
        self.door.create("GeoNodeCage", "Door")
        self.door.obj['IS_ENTRY_DOOR_BP'] = True
        self.door.set_input('Dim X', props.door_single_width)
        self.door.set_input('Dim Y', props.wall_thickness)
        self.door.set_input('Dim Z', props.door_height)
        self.door.obj.display_type = 'WIRE'
        
        self.register_placement_object(self.door.obj)

    def get_door_width(self):
        """Get current door width."""
        if self.door:
            return self.door.get_input('Dim X')
        return 0

    def set_position_on_wall(self):
        """Position door on the selected wall with gap-aware snapping."""
        if not self.selected_wall or not self.door:
            return
            
        wall = hb_types.GeoNodeWall(self.selected_wall)
        self.wall_length = wall.get_input('Length')
        wall_thickness = wall.get_input('Thickness')
        door_width = self.get_door_width()
        
        # Get local X position on wall from world hit location
        # Transform hit location to wall's local space
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

    def set_position_free(self):
        """Position door freely when not over a wall."""
        if self.door and self.hit_location:
            self.door.obj.parent = None
            self.door.obj.location = self.hit_location
            self.door.obj.location.z = 0

    def update_header(self, context):
        """Update header text with instructions."""
        if self.placement_state == hb_placement.PlacementState.TYPING:
            text = f"Offset: {self.typed_value}_ | Enter to confirm | Esc to cancel typing"
        elif self.selected_wall:
            offset_str = units.unit_to_string(context.scene.unit_settings, self.placement_x)
            width_str = units.unit_to_string(context.scene.unit_settings, self.get_door_width())
            text = f"Offset: {offset_str} | Width: {width_str} | Type for exact offset | Click to place | Esc to cancel"
        else:
            text = "Move over a wall to place door | Esc to cancel"
        
        hb_placement.draw_header_text(context, text)

    def execute(self, context):
        # Initialize placement mixin
        self.init_placement(context)
        
        # Reset door-specific state
        self.door = None
        self.selected_wall = None
        self.wall_length = 0
        self.placement_x = 0

        # Create door
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

        # Update position if not typing
        if self.placement_state != hb_placement.PlacementState.TYPING:
            if self.selected_wall:
                self.set_position_on_wall()
            else:
                self.set_position_free()

        self.update_header(context)

        # Left click - place door
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if self.selected_wall:
                # Confirm placement - remove from cancel list
                if self.door.obj in self.placement_objects:
                    self.placement_objects.remove(self.door.obj)
                hb_placement.clear_header_text(context)
                context.window.cursor_set('DEFAULT')
                return {'FINISHED'}
            else:
                # Can't place without a wall
                self.report({'WARNING'}, "Door must be placed on a wall")
                return {'RUNNING_MODAL'}

        # Right click or Escape - cancel
        if event.type in {'RIGHTMOUSE', 'ESC'} and event.value == 'PRESS':
            self.cancel_placement(context)
            hb_placement.clear_header_text(context)
            return {'CANCELLED'}

        # Pass through navigation events
        if hb_snap.event_is_pass_through(event):
            return {'PASS_THROUGH'}

        return {'RUNNING_MODAL'}


class home_builder_doors_windows_OT_place_window(bpy.types.Operator, hb_placement.PlacementMixin):
    bl_idname = "home_builder_doors_windows.place_window"
    bl_label = "Place Window"
    bl_description = "Place a window on a wall. Type for exact offset, Escape to cancel"
    bl_options = {'UNDO'}

    # Window-specific state
    window = None
    selected_wall = None
    wall_length: float = 0
    
    # Placement position on wall (local X)
    placement_x: float = 0

    def get_default_typing_target(self):
        """When user starts typing, they're entering X offset."""
        return hb_placement.TypingTarget.OFFSET_X

    def on_typed_value_changed(self):
        """Update window position as user types."""
        if self.typed_value and self.window and self.selected_wall:
            parsed = self.parse_typed_distance()
            if parsed is not None:
                self.placement_x = parsed
                self.window.obj.location.x = parsed
        self.update_header(bpy.context)

    def apply_typed_value(self):
        """Apply typed offset."""
        parsed = self.parse_typed_distance()
        if parsed is not None and self.window:
            self.placement_x = parsed
            self.window.obj.location.x = parsed
        self.stop_typing()

    def create_window(self, context):
        """Create the window object."""
        props = context.scene.home_builder
        self.window = hb_types.GeoNodeObject()
        self.window.create("GeoNodeCage", "Window")
        self.window.obj['IS_WINDOW_BP'] = True
        self.window.set_input('Dim X', props.window_width)
        self.window.set_input('Dim Y', props.wall_thickness)
        self.window.set_input('Dim Z', props.window_height)
        self.window.obj.display_type = 'WIRE'
        
        self.register_placement_object(self.window.obj)

    def get_window_width(self):
        """Get current window width."""
        if self.window:
            return self.window.get_input('Dim X')
        return 0

    def get_window_height(self):
        """Get current window height."""
        if self.window:
            return self.window.get_input('Dim Z')
        return 0

    def set_position_on_wall(self):
        """Position window on the selected wall with gap-aware snapping."""
        if not self.selected_wall or not self.window:
            return
            
        props = bpy.context.scene.home_builder
        wall = hb_types.GeoNodeWall(self.selected_wall)
        self.wall_length = wall.get_input('Length')
        wall_thickness = wall.get_input('Thickness')
        window_width = self.get_window_width()
        
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
        
        # Clamp to wall bounds
        snap_x = max(0, min(snap_x, self.wall_length - window_width))
        
        self.placement_x = snap_x
        
        # Parent to wall and set position
        self.window.obj.parent = self.selected_wall
        self.window.obj.location.x = snap_x
        self.window.obj.location.y = 0
        self.window.obj.location.z = props.window_height_from_floor
        self.window.obj.rotation_euler = (0, 0, 0)
        
        # Match window depth to wall thickness
        self.window.set_input("Dim Y", wall_thickness)

    def set_position_free(self):
        """Position window freely when not over a wall."""
        if self.window and self.hit_location:
            self.window.obj.parent = None
            self.window.obj.location = self.hit_location

    def update_header(self, context):
        """Update header text with instructions."""
        if self.placement_state == hb_placement.PlacementState.TYPING:
            text = f"Offset: {self.typed_value}_ | Enter to confirm | Esc to cancel typing"
        elif self.selected_wall:
            offset_str = units.unit_to_string(context.scene.unit_settings, self.placement_x)
            width_str = units.unit_to_string(context.scene.unit_settings, self.get_window_width())
            text = f"Offset: {offset_str} | Width: {width_str} | Type for exact offset | Click to place | Esc to cancel"
        else:
            text = "Move over a wall to place window | Esc to cancel"
        
        hb_placement.draw_header_text(context, text)

    def execute(self, context):
        # Initialize placement mixin
        self.init_placement(context)
        
        # Reset window-specific state
        self.window = None
        self.selected_wall = None
        self.wall_length = 0
        self.placement_x = 0

        # Create window
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

        # Update position if not typing
        if self.placement_state != hb_placement.PlacementState.TYPING:
            if self.selected_wall:
                self.set_position_on_wall()
            else:
                self.set_position_free()

        self.update_header(context)

        # Left click - place window
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if self.selected_wall:
                # Confirm placement - remove from cancel list
                if self.window.obj in self.placement_objects:
                    self.placement_objects.remove(self.window.obj)
                hb_placement.clear_header_text(context)
                context.window.cursor_set('DEFAULT')
                return {'FINISHED'}
            else:
                # Can't place without a wall
                self.report({'WARNING'}, "Window must be placed on a wall")
                return {'RUNNING_MODAL'}

        # Right click or Escape - cancel
        if event.type in {'RIGHTMOUSE', 'ESC'} and event.value == 'PRESS':
            self.cancel_placement(context)
            hb_placement.clear_header_text(context)
            return {'CANCELLED'}

        # Pass through navigation events
        if hb_snap.event_is_pass_through(event):
            return {'PASS_THROUGH'}

        return {'RUNNING_MODAL'}



classes = (
    home_builder_doors_windows_OT_place_door,
    home_builder_doors_windows_OT_place_window,
)

register, unregister = bpy.utils.register_classes_factory(classes)
