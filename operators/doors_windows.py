import bpy
from .. import hb_types, hb_snap, hb_placement, units
import math
from mathutils import Vector


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
        cutting_obj.display_type = 'WIRE'
        
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
        self.door = hb_types.GeoNodeCage()
        self.door.create("Door")
        self.door.obj['IS_ENTRY_DOOR_BP'] = True
        self.door.set_input('Dim X', props.door_single_width)
        self.door.set_input('Dim Y', props.wall_thickness)
        self.door.set_input('Dim Z', props.door_height)
        self.door.obj.display_type = 'WIRE'
        
        self.register_placement_object(self.door.obj)

    def set_position_on_wall(self):
        """Position door on the selected wall with gap-aware snapping."""
        if not self.selected_wall or not self.door:
            return
            
        wall = hb_types.GeoNodeWall(self.selected_wall)
        self.wall_length = wall.get_input('Length')
        wall_thickness = wall.get_input('Thickness')
        door_width = self.get_placed_object_width()
        
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
        self.window = hb_types.GeoNodeCage()
        self.window.create("Window")
        self.window.obj['IS_WINDOW_BP'] = True
        self.window.set_input('Dim X', props.window_width)
        self.window.set_input('Dim Y', props.wall_thickness)
        self.window.set_input('Dim Z', props.window_height)
        self.window.obj.display_type = 'WIRE'
        
        self.register_placement_object(self.window.obj)

    def set_position_on_wall(self):
        """Position window on the selected wall with gap-aware snapping."""
        if not self.selected_wall or not self.window:
            return
            
        props = bpy.context.scene.home_builder
        wall = hb_types.GeoNodeWall(self.selected_wall)
        self.wall_length = wall.get_input('Length')
        wall_thickness = wall.get_input('Thickness')
        window_width = self.get_placed_object_width()
        
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


classes = (
    home_builder_doors_windows_OT_place_door,
    home_builder_doors_windows_OT_place_window,
)

register, unregister = bpy.utils.register_classes_factory(classes)
