import bpy
import bmesh
import math
from mathutils import Vector
from .. import hb_types, hb_snap, hb_placement, units

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
    
    # Free rotation mode (Alt toggles, snaps to 15° increments)
    free_rotation: bool = False

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
            
            if self.free_rotation:
                # Free rotation mode - snap to 15° increments
                angle = math.atan2(y, x)
                # Snap to nearest 15 degrees
                snap_angle = round(math.degrees(angle) / 15) * 15
                self.current_wall.obj.rotation_euler.z = math.radians(snap_angle)
                
                # Length is the full distance to cursor
                length = math.sqrt(x * x + y * y)
                self.current_wall.set_input('Length', length)
            else:
                # Default mode - snap to orthogonal (90°) directions
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
            angle_deg = round(math.degrees(self.current_wall.obj.rotation_euler.z))
            rotation_mode = "Free (15°)" if self.free_rotation else "Ortho (90°)"
            text = f"Length: {length_str} | Angle: {angle_deg}° | {rotation_mode} | Alt: toggle rotation | Type for exact | Click to place"
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
        self.free_rotation = False

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

        # Alt key toggles free rotation mode
        if event.type == 'LEFT_ALT' and event.value == 'PRESS':
            self.free_rotation = not self.free_rotation
            self.update_header(context)
            return {'RUNNING_MODAL'}

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


class home_builder_walls_OT_add_floor(bpy.types.Operator):
    bl_idname = "home_builder_walls.add_floor"
    bl_label = "Add Floor"
    bl_description = "This will add a floor to the room based on the wall layout"
    bl_options = {'UNDO'}

    def create_floor_mesh(self,name, points):
        """Create a floor mesh from boundary points."""
        
        mesh = bpy.data.meshes.new(name)
        obj = bpy.data.objects.new(name, mesh)
        
        bpy.context.collection.objects.link(obj)
        
        bm = bmesh.new()
        
        # If closed loop, remove duplicate closing point
        closed = is_closed_loop(points)
        if closed:
            points = points[:-1]
        
        # Add vertices
        verts = [bm.verts.new(p) for p in points]
        bm.verts.ensure_lookup_table()
        
        # Create boundary edges
        edges = []
        for i in range(len(verts)):
            next_i = (i + 1) % len(verts)
            edge = bm.edges.new((verts[i], verts[next_i]))
            edges.append(edge)
        
        # Fill to create faces (handles non-convex shapes)
        bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=edges)
        
        bm.to_mesh(mesh)
        bm.free()
        
        return obj      

    def execute(self, context):
        chains = find_wall_chains()
        
        if not chains:
            self.report({'WARNING'}, "No connected walls found")
            return {'CANCELLED'}
        
        floors_created = 0
        for i, chain in enumerate(chains):
            points = get_room_boundary_points(chain)
            
            # Handle cases with only 1 or 2 walls - create rectangular floor from bounding box
            if len(points) < 3 or (len(points) <= 3 and not is_closed_loop(points)):
                # Get all wall endpoints to calculate bounding box
                all_points = []
                for wall in chain:
                    start, end = get_wall_endpoints(wall)
                    all_points.append(Vector((start.x, start.y, 0)))
                    all_points.append(Vector((end.x, end.y, 0)))
                
                if len(all_points) >= 2:
                    # Calculate bounding box
                    min_x = min(p.x for p in all_points)
                    max_x = max(p.x for p in all_points)
                    min_y = min(p.y for p in all_points)
                    max_y = max(p.y for p in all_points)
                    
                    # Ensure we have a valid rectangle (not a line)
                    if abs(max_x - min_x) < 0.01:
                        # Walls are vertical, extend horizontally
                        max_x = min_x + 3.0  # Default 3 meters width
                    if abs(max_y - min_y) < 0.01:
                        # Walls are horizontal, extend vertically
                        max_y = min_y + 3.0  # Default 3 meters depth
                    
                    # Create rectangular floor points (counter-clockwise)
                    points = [
                        Vector((min_x, min_y, 0)),
                        Vector((max_x, min_y, 0)),
                        Vector((max_x, max_y, 0)),
                        Vector((min_x, max_y, 0)),
                        Vector((min_x, min_y, 0)),  # Close the loop
                    ]
                else:
                    continue
            else:
                # Close the loop if not already closed
                if not is_closed_loop(points):
                    points.append(points[0].copy())
            
            # Create floor name
            name = "Floor" if i == 0 else f"Floor.{i:03d}"
            
            floor_obj = self.create_floor_mesh(name, points)
            floor_obj['IS_FLOOR_BP'] = True
            
            floors_created += 1
        
        if floors_created > 0:
            self.report({'INFO'}, f"Created {floors_created} floor(s)")
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Could not create floor - insufficient wall data")
            return {'CANCELLED'}


class home_builder_walls_OT_add_room_lights(bpy.types.Operator):
    bl_idname = "home_builder_walls.add_room_lights"
    bl_label = "Add Room Lights"
    bl_description = "Add ceiling lights to the room based on room size"
    bl_options = {'UNDO'}

    light_spacing: bpy.props.FloatProperty(
        name="Light Spacing",
        description="Minimum spacing between lights",
        default=1.2192,  # 4 feet in meters
        min=0.3,
        max=3.0,
        unit='LENGTH'
    )  # type: ignore

    edge_offset: bpy.props.FloatProperty(
        name="Edge Offset",
        description="Distance from walls to lights",
        default=0.6096,  # 2 feet in meters
        min=0.15,
        max=1.5,
        unit='LENGTH'
    )  # type: ignore

    light_power: bpy.props.FloatProperty(
        name="Light Power",
        description="Power of each light in watts",
        default=200.0,
        min=10.0,
        max=2000.0,
        unit='POWER'
    )  # type: ignore

    light_temperature: bpy.props.FloatProperty(
        name="Color Temperature",
        description="Light color temperature in Kelvin",
        default=3000.0,
        min=2000.0,
        max=6500.0
    )  # type: ignore

    ceiling_offset: bpy.props.FloatProperty(
        name="Ceiling Offset", 
        description="Distance below ceiling to place lights",
        default=0.0254,  # 1 inch
        min=0.0,
        max=0.3,
        unit='LENGTH'
    )  # type: ignore

    def calculate_light_grid(self,boundary_points, min_spacing=1.2, edge_offset=0.6):
        """
        Calculate optimal light positions for a room.
        
        Args:
            boundary_points: List of 2D vectors defining room boundary
            min_spacing: Minimum spacing between lights in meters
            edge_offset: Distance from walls in meters
        
        Returns:
            List of 2D Vector positions for lights
        """

        xs = [p.x for p in boundary_points]
        ys = [p.y for p in boundary_points]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        width = max_x - min_x
        depth = max_y - min_y
        
        usable_width = width - (2 * edge_offset)
        usable_depth = depth - (2 * edge_offset)
        
        # Ensure at least 1 light
        num_x = max(1, int(usable_width / min_spacing) + 1)
        num_y = max(1, int(usable_depth / min_spacing) + 1)
        
        spacing_x = usable_width / max(1, num_x - 1) if num_x > 1 else 0
        spacing_y = usable_depth / max(1, num_y - 1) if num_y > 1 else 0
        
        positions = []
        start_x = min_x + edge_offset
        start_y = min_y + edge_offset
        
        for i in range(num_x):
            for j in range(num_y):
                if num_x == 1:
                    x = (min_x + max_x) / 2
                else:
                    x = start_x + i * spacing_x
                
                if num_y == 1:
                    y = (min_y + max_y) / 2
                else:
                    y = start_y + j * spacing_y
                
                pos = Vector((x, y))
                if point_in_polygon(pos, boundary_points):
                    positions.append(pos)
        
        return positions

    def kelvin_to_rgb(self,temperature):
        """Convert color temperature in Kelvin to RGB values."""
        # Attempt approximation of blackbody radiation curve
        temp = temperature / 100.0
        
        # Red
        if temp <= 66:
            red = 255
        else:
            red = temp - 60
            red = 329.698727446 * (red ** -0.1332047592)
            red = max(0, min(255, red))
        
        # Green
        if temp <= 66:
            green = temp
            green = 99.4708025861 * math.log(green) - 161.1195681661
        else:
            green = temp - 60
            green = 288.1221695283 * (green ** -0.0755148492)
        green = max(0, min(255, green))
        
        # Blue
        if temp >= 66:
            blue = 255
        elif temp <= 19:
            blue = 0
        else:
            blue = temp - 10
            blue = 138.5177312231 * math.log(blue) - 305.0447927307
            blue = max(0, min(255, blue))
        
        return (red / 255.0, green / 255.0, blue / 255.0)


    def create_room_lights(self,light_positions, height, light_power=200, light_temperature=3000):
        """
        Create point lights at the specified positions.
        
        Args:
            light_positions: List of 2D Vector positions
            height: Z height for lights
            light_power: Power in watts
            light_temperature: Color temperature in Kelvin
        
        Returns:
            List of created light objects
        """

        lights = []
        
        # Create or get collection for lights
        light_collection_name = "Room Lights"
        if light_collection_name not in bpy.data.collections:
            light_collection = bpy.data.collections.new(light_collection_name)
            bpy.context.scene.collection.children.link(light_collection)
        else:
            light_collection = bpy.data.collections[light_collection_name]
        
        # Get color from temperature
        color = self.kelvin_to_rgb(light_temperature)
        
        for i, pos in enumerate(light_positions):
            # Create light data
            light_data = bpy.data.lights.new(name=f"Room_Light_{i:03d}", type='POINT')
            light_data.energy = light_power
            light_data.shadow_soft_size = 0.1  # Soft shadows
            light_data.color = color
            
            # Create light object
            light_obj = bpy.data.objects.new(name=f"Room_Light_{i:03d}", object_data=light_data)
            light_obj.location = (pos.x, pos.y, height)
            
            # Link to collection
            light_collection.objects.link(light_obj)
            
            # Mark as room light
            light_obj['IS_ROOM_LIGHT'] = True
            
            lights.append(light_obj)
        
        return lights

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=350)

    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        box.label(text="Light Placement", icon='LIGHT')
        col = box.column(align=True)
        col.prop(self, 'light_spacing')
        col.prop(self, 'edge_offset')
        
        box = layout.box()
        box.label(text="Light Properties", icon='OUTLINER_OB_LIGHT')
        col = box.column(align=True)
        col.prop(self, 'light_power')
        col.prop(self, 'light_temperature')
        col.prop(self, 'ceiling_offset')

    def execute(self, context):
        chains = find_wall_chains()
        
        if not chains:
            self.report({'WARNING'}, "No connected walls found")
            return {'CANCELLED'}
        
        total_lights = 0
        
        for chain in chains:
            points = get_room_boundary_points(chain)
            
            if len(points) < 3:
                continue
            
            # Close polygon for point-in-polygon test
            if not is_closed_loop(points):
                points.append(points[0].copy())
            
            # Get ceiling height from first wall in chain
            wall = hb_types.GeoNodeWall(chain[0])
            ceiling_height = wall.get_input('Height')
            
            # Calculate light positions
            light_positions = self.calculate_light_grid(
                points, 
                min_spacing=self.light_spacing, 
                edge_offset=self.edge_offset
            )
            
            if not light_positions:
                continue
            
            # Create lights
            lights = self.create_room_lights(
                light_positions,
                height=ceiling_height - self.ceiling_offset,
                light_power=self.light_power,
                light_temperature=self.light_temperature
            )
            
            total_lights += len(lights)
        
        if total_lights > 0:
            self.report({'INFO'}, f"Created {total_lights} light(s)")
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Could not create lights - room too small or invalid")
            return {'CANCELLED'}


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
    home_builder_walls_OT_add_floor,
    home_builder_walls_OT_add_room_lights,
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

    # Update this wall
    calculate_wall_miter_angles(wall_obj)

    # Update connected wall on the left
    left_wall = wall.get_connected_wall('left')
    if left_wall:
        calculate_wall_miter_angles(left_wall.obj)

    # Update connected wall on the right
    right_wall = wall.get_connected_wall('right')
    if right_wall:
        calculate_wall_miter_angles(right_wall.obj)

# Room Lighting Helpers
def point_in_polygon(point, polygon):
    """Ray casting algorithm to check if point is inside polygon."""
    x, y = point.x, point.y
    n = len(polygon)
    inside = False
    
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i].x, polygon[i].y
        xj, yj = polygon[j].x, polygon[j].y
        
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    
    return inside
  
def get_wall_endpoints(wall_obj):
    """Get the start and end points of a wall in world coordinates."""
    
    world_matrix = wall_obj.matrix_world
    start = world_matrix.translation.copy()
    
    rot_z = wall_obj.matrix_world.to_euler().z
    
    # Find obj_x child to get wall length
    length = 0
    for child in wall_obj.children:
        if 'obj_x' in child.name.lower():
            length = child.location.x
            break
    
    direction = Vector((math.cos(rot_z), math.sin(rot_z), 0))
    end = start + direction * length
    
    return start.to_2d(), end.to_2d()

def find_wall_chains():
    """Find connected chains of walls, returning list of ordered wall objects."""
    walls = [obj for obj in bpy.data.objects if obj.get('IS_WALL_BP')]
    
    if not walls:
        return []
    
    wall_data = {}
    for wall in walls:
        start, end = get_wall_endpoints(wall)
        wall_data[wall.name] = {'obj': wall, 'start': start, 'end': end}
    
    tolerance = 0.01
    connections = {}
    
    for name1, data1 in wall_data.items():
        for name2, data2 in wall_data.items():
            if name1 == name2:
                continue
            if (data1['end'] - data2['start']).length < tolerance:
                connections[name1] = name2
    
    has_predecessor = set(connections.values())
    start_walls = [name for name in wall_data.keys() if name not in has_predecessor]
    
    if not start_walls and walls:
        start_walls = [walls[0].name]
    
    chains = []
    used = set()
    
    for start_name in start_walls:
        if start_name in used:
            continue
        
        chain = []
        current = start_name
        
        while current and current not in used:
            used.add(current)
            chain.append(wall_data[current]['obj'])
            current = connections.get(current)
            if current == start_name:
                break
        
        if chain:
            chains.append(chain)
    
    return chains

def get_room_boundary_points(wall_chain):
    """Extract boundary points from a chain of walls."""

    points = []
    
    for wall in wall_chain:
        start, end = get_wall_endpoints(wall)
        if not points or (Vector(points[-1]) - Vector((start.x, start.y, 0))).length > 0.01:
            points.append(Vector((start.x, start.y, 0)))
    
    if wall_chain:
        start, end = get_wall_endpoints(wall_chain[-1])
        points.append(Vector((end.x, end.y, 0)))
    
    return points

def is_closed_loop(points, tolerance=0.01):
    """Check if the points form a closed loop."""
    if len(points) < 3:
        return False
    return (points[0] - points[-1]).length < tolerance
