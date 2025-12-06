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
        for child in self.current_wall.obj.children:
            self.register_placement_object(child)
        
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
        # Also remove the wall's obj_x object from cancel list
        for child in self.current_wall.obj.children:
            if 'obj_x' in child and child in self.placement_objects:
                self.placement_objects.remove(child)

        # Update miter angles for this wall and connected walls
        update_connected_wall_miters(self.current_wall.obj)

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
            self.cancel_placement(context)
            hb_placement.clear_header_text(context)
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


class home_builder_walls_OT_wall_prompts(bpy.types.Operator):
    bl_idname = "home_builder_walls.wall_prompts"
    bl_label = "Wall Prompts"
    bl_description = "This shows the prompts for the selected wall"

    wall: hb_types.GeoNodeWall = None
    previous_rotation: float = 0.0

    wall_length: bpy.props.FloatProperty(name="Width",unit='LENGTH',precision=6)# type: ignore
    wall_height: bpy.props.FloatProperty(name="Height",unit='LENGTH',precision=6)# type: ignore
    wall_thickness: bpy.props.FloatProperty(name="Depth",unit='LENGTH',precision=6)# type: ignore

    @classmethod
    def poll(cls, context):
        return context.object and 'IS_WALL_BP' in context.object

    def check(self, context):
        self.wall.set_input('Length', self.wall_length)
        self.wall.set_input('Height', self.wall_height)
        self.wall.set_input('Thickness', self.wall_thickness)
        calculate_wall_miter_angles(self.wall.obj)
        left_wall = self.wall.get_connected_wall('left')
        if left_wall:
            calculate_wall_miter_angles(left_wall.obj)
        
        right_wall = self.wall.get_connected_wall('right')
        if right_wall:
            calculate_wall_miter_angles(right_wall.obj)        
        return True

    def invoke(self, context, event):
        self.wall = hb_types.GeoNodeWall(context.object)
        self.wall_length = self.wall.get_input('Length')
        self.wall_height = self.wall.get_input('Height')
        self.wall_thickness = self.wall.get_input('Thickness')
        self.previous_rotation = self.wall.obj.rotation_euler.z
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def execute(self, context):
        return {'FINISHED'}

    def get_first_wall_bp(self,context,obj):
        if len(obj.constraints) > 0:
            bp = obj.constraints[0].target.parent
            return self.get_first_wall_bp(context,bp)
        else:
            return obj   

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        row = box.row()
        
        col = row.column(align=True)
        row1 = col.row(align=True)
        row1.label(text='Length:')
        row1.prop(self, 'wall_length', text="")
        
        row1 = col.row(align=True)
        row1.label(text='Height:')
        row1.prop(self, 'wall_height', text="")      

        row1 = col.row(align=True)
        row1.label(text='Thickness:')
        row1.prop(self, 'wall_thickness', text="") 

        if len(self.wall.obj.constraints) > 0:
            first_wall = self.get_first_wall_bp(context,self.wall.obj)
            col = row.column(align=True)
            col.label(text="Location X:")
            col.label(text="Location Y:")
            col.label(text="Location Z:")
        
            col = row.column(align=True)
            col.prop(first_wall,'location',text="")            
        else:
            col = row.column(align=True)
            col.label(text="Location X:")
            col.label(text="Location Y:")
            col.label(text="Location Z:")
        
            col = row.column(align=True)
            col.prop(self.wall.obj,'location',text="")
        
        row = box.row()
        row.label(text='Rotation Z:')
        row.prop(self.wall.obj,'rotation_euler',index=2,text="")  


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



class home_builder_walls_OT_update_wall_miters(bpy.types.Operator):
    """Update miter angles for all walls based on their connections"""
    bl_idname = "home_builder_walls.update_wall_miters"
    bl_label = "Update Wall Miters"
    bl_options = {'UNDO'}

    def execute(self, context):
        update_all_wall_miters()
        self.report({'INFO'}, "Updated wall miter angles")
        return {'FINISHED'}


classes = (
    home_builder_walls_OT_draw_walls,
    home_builder_walls_OT_wall_prompts,
    home_builder_walls_OT_update_wall_height,
    home_builder_walls_OT_update_wall_thickness,
    home_builder_walls_OT_update_wall_miters,
)

register, unregister = bpy.utils.register_classes_factory(classes)
# Wall Miter Angle Calculation
def calculate_wall_miter_angles(wall_obj):
    """
    Calculate and set the miter angles for a wall based on connected walls.
    Uses the GeoNodeWall.get_connected_wall() method to find connections.
    
    The miter angle formula:
    - turn_angle = connected_wall_rotation - this_wall_rotation (normalized to -180° to 180°)
    - For the RIGHT end (end of wall): right_angle = -turn_angle / 2
    - For the LEFT end (start of wall): left_angle = turn_angle / 2
    """
    import math
    
    wall = hb_types.GeoNodeWall(wall_obj)
    this_rot = wall_obj.rotation_euler.z
    
    # Get connected wall on the left (at our START)
    left_wall = wall.get_connected_wall('left')
    if left_wall:
        prev_rot = left_wall.obj.rotation_euler.z
        turn = this_rot - prev_rot
        # Normalize turn angle to -pi to pi
        while turn > math.pi: turn -= 2 * math.pi
        while turn < -math.pi: turn += 2 * math.pi
        
        left_angle = turn / 2
        wall.set_input('Left Angle', left_angle)
    else:
        wall.set_input('Left Angle', 0)
    
    # Get connected wall on the right (at our END)
    right_wall = wall.get_connected_wall('right')
    if right_wall:
        next_rot = right_wall.obj.rotation_euler.z
        turn = next_rot - this_rot
        # Normalize turn angle to -pi to pi
        while turn > math.pi: turn -= 2 * math.pi
        while turn < -math.pi: turn += 2 * math.pi
        
        right_angle = -turn / 2
        wall.set_input('Right Angle', right_angle)
    else:
        wall.set_input('Right Angle', 0)


def update_all_wall_miters():
    """Update miter angles for all walls in the scene."""
    for obj in bpy.data.objects:
        if 'IS_WALL_BP' in obj:
            calculate_wall_miter_angles(obj)


def update_connected_wall_miters(wall_obj):
    """Update miter angles for a wall and all walls connected to it."""
    wall = hb_types.GeoNodeWall(wall_obj)
    print("GOT WALL",wall.obj)
    
    # Update this wall
    calculate_wall_miter_angles(wall_obj)

    print("CALCULATED MITERS FOR",wall.obj)
    
    # Update connected wall on the left
    left_wall = wall.get_connected_wall('left')
    if left_wall:
        calculate_wall_miter_angles(left_wall.obj)
        print("CALCULATED MITERS FOR LEFT WALL",left_wall.obj)
    
    # Update connected wall on the right
    right_wall = wall.get_connected_wall('right')
    if right_wall:
        calculate_wall_miter_angles(right_wall.obj)
        print("CALCULATED MITERS FOR RIGHT WALL",right_wall.obj)


