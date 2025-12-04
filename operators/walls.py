import bpy
from .. import hb_types, hb_snap, hb_placement, units
import math
from mathutils import Vector


class home_builder_walls_OT_draw_walls(bpy.types.Operator, hb_placement.PlacementMixin):
    bl_idname = "home_builder_walls.draw_walls"
    bl_label = "Draw Walls"
    bl_description = "Enter Draw Walls Mode. Click to place points, type for exact length, Escape to cancel"
    bl_options = {'UNDO'}

    # Wall-specific state
    current_wall = None
    previous_wall = None
    start_point: Vector = None
    dim = None
    
    # Track if we've placed the first point
    has_start_point: bool = False

    def get_default_typing_target(self):
        """When user starts typing, they're entering wall length."""
        return hb_placement.TypingTarget.LENGTH

    def on_typed_value_changed(self):
        """Update dimension display as user types."""
        if self.typed_value:
            parsed = self.parse_typed_distance()
            if parsed is not None and self.current_wall:
                self.current_wall.set_input('Length', parsed)
                self.update_dimension()
        self.update_header(bpy.context)

    def apply_typed_value(self):
        """Apply typed length and advance to next wall."""
        parsed = self.parse_typed_distance()
        if parsed is not None and self.current_wall:
            self.current_wall.set_input('Length', parsed)
            self.update_dimension()
            # Confirm this wall and start next
            self.confirm_current_wall()
        self.stop_typing()

    def create_wall(self, context):
        """Create a new wall segment."""
        props = context.scene.home_builder
        self.current_wall = hb_types.GeoNodeWall()
        self.current_wall.create("Wall")
        self.current_wall.set_input('Thickness', props.wall_thickness)
        self.current_wall.set_input('Height', props.ceiling_height)
        
        # Register for cleanup on cancel
        self.register_placement_object(self.current_wall.obj)
        
        if self.previous_wall:
            self.current_wall.connect_to_wall(self.previous_wall)

        # Parent dimension to wall
        self.dim.obj.parent = self.current_wall.obj
        self.dim.set_input("Leader Length", props.wall_thickness / 2)
        self.dim.obj.data.splines[0].points[1].co = (0, 0, 0, 0)

    def create_dimension(self):
        """Create the dimension annotation."""
        self.dim = hb_types.GeoNodeDimension()
        self.dim.create("Dimension")
        self.register_placement_object(self.dim.obj)

    def update_dimension(self):
        """Update dimension display to match wall length."""
        if self.current_wall and self.dim:
            length = self.current_wall.get_input('Length')
            height = self.current_wall.get_input('Height')
            self.dim.obj.location.z = height + units.inch(1)
            self.dim.obj.data.splines[0].points[1].co = (length, 0, 0, 0)

    def set_wall_position_from_mouse(self):
        """Update wall position/rotation based on mouse location."""
        if not self.has_start_point:
            # First point - just move the wall origin
            if self.hit_location:
                self.current_wall.obj.location = self.hit_location
        else:
            # Drawing length - calculate from start point
            x = self.hit_location[0] - self.start_point[0]
            y = self.hit_location[1] - self.start_point[1]

            # Snap to orthogonal directions
            if abs(x) > abs(y):
                # Horizontal
                if x > 0:
                    self.current_wall.obj.rotation_euler.z = math.radians(0)
                else:
                    self.current_wall.obj.rotation_euler.z = math.radians(180)
                self.current_wall.set_input('Length', abs(x))
            else:
                # Vertical
                if y > 0:
                    self.current_wall.obj.rotation_euler.z = math.radians(90)
                else:
                    self.current_wall.obj.rotation_euler.z = math.radians(-90)
                self.current_wall.set_input('Length', abs(y))

            self.update_dimension()

    def confirm_current_wall(self):
        """Finalize current wall and prepare for next."""
        # Update start point to end of current wall
        wall_length = self.current_wall.get_input('Length')
        angle = self.current_wall.obj.rotation_euler.z
        
        self.start_point = Vector((
            self.start_point.x + math.cos(angle) * wall_length,
            self.start_point.y + math.sin(angle) * wall_length,
            0
        ))
        
        # Current wall becomes previous, remove from cancel list (it's confirmed)
        if self.current_wall.obj in self.placement_objects:
            self.placement_objects.remove(self.current_wall.obj)
        
        self.previous_wall = self.current_wall
        self.create_wall(bpy.context)

    def update_header(self, context):
        """Update header text with instructions and current value."""
        if self.placement_state == hb_placement.PlacementState.TYPING:
            text = f"Wall Length: {self.typed_value}_ | Enter to confirm | Esc to cancel typing"
        elif self.has_start_point:
            length = self.current_wall.get_input('Length')
            length_str = units.unit_to_string(context.scene.unit_settings, length)
            text = f"Length: {length_str} | Type for exact | Click to place | Right-click to finish | Esc to cancel"
        else:
            text = "Click to place first point | Right-click to cancel | Esc to cancel"
        
        hb_placement.draw_header_text(context, text)

    def execute(self, context):
        # Initialize placement mixin
        self.init_placement(context)
        
        # Reset wall-specific state
        self.current_wall = None
        self.previous_wall = None
        self.start_point = None
        self.has_start_point = False
        self.dim = None

        # Create initial objects
        self.create_dimension()
        self.create_wall(context)

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        context.window.cursor_set('CROSSHAIR')

        # Skip intermediate mouse moves
        if event.type == "INBETWEEN_MOUSEMOVE":
            return {'RUNNING_MODAL'}

        # Let mixin handle typing events first
        if self.handle_typing_event(event):
            self.update_header(context)
            return {'RUNNING_MODAL'}

        # Update snap (hide current wall during raycast)
        self.current_wall.obj.hide_set(True)
        self.update_snap(context, event)
        self.current_wall.obj.hide_set(False)

        # Update position if not typing
        if self.placement_state != hb_placement.PlacementState.TYPING:
            self.set_wall_position_from_mouse()

        self.update_header(context)

        # Left click - place point
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if not self.has_start_point:
                # Set first point
                self.start_point = Vector(self.hit_location)
                self.has_start_point = True
            else:
                # Confirm wall and start next
                self.confirm_current_wall()
            return {'RUNNING_MODAL'}

        # Right click - finish drawing
        if event.type == 'RIGHTMOUSE' and event.value == 'PRESS':
            # Remove current unfinished wall
            if self.current_wall and self.current_wall.obj:
                bpy.data.objects.remove(self.current_wall.obj, do_unlink=True)
            if self.dim and self.dim.obj:
                bpy.data.objects.remove(self.dim.obj, do_unlink=True)
            hb_placement.clear_header_text(context)
            context.window.cursor_set('DEFAULT')
            return {'FINISHED'}

        # Escape - cancel everything
        if event.type == 'ESC' and event.value == 'PRESS':
            self.cancel_placement(context)
            hb_placement.clear_header_text(context)
            return {'CANCELLED'}

        # Pass through navigation events
        if hb_snap.event_is_pass_through(event):
            return {'PASS_THROUGH'}

        return {'RUNNING_MODAL'}


class home_builder_walls_OT_update_wall_height(bpy.types.Operator):
    bl_idname = "home_builder_walls.update_wall_height"
    bl_label = "Update Wall Height"
    bl_description = "This will update all of the wall heights in the room"

    def execute(self, context):
        props = context.scene.home_builder
        for obj in bpy.data.objects:
            if 'IS_WALL_BP' in obj:
                wall = hb_types.GeoNodeWall(obj)
                wall.set_input('Height', props.ceiling_height)
        return {'FINISHED'}


class home_builder_walls_OT_update_wall_thickness(bpy.types.Operator):
    bl_idname = "home_builder_walls.update_wall_thickness"
    bl_label = "Update Wall Thickness"
    bl_description = "This will update all of the thickness of all of the walls in the room"

    def execute(self, context):
        props = context.scene.home_builder
        for obj in bpy.data.objects:
            if 'IS_WALL_BP' in obj:
                wall = hb_types.GeoNodeWall(obj)
                wall.set_input('Thickness', props.wall_thickness)
        return {'FINISHED'}


classes = (
    home_builder_walls_OT_draw_walls,
    home_builder_walls_OT_update_wall_height,
    home_builder_walls_OT_update_wall_thickness,
)

register, unregister = bpy.utils.register_classes_factory(classes)
