import bpy
import bmesh
import math
import os
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
    
    # Endpoint snapping state
    snap_wall = None  # Wall we're snapping to
    snap_endpoint = None  # 'start' or 'end'
    snap_surface = None  # 'front' or 'back' for surface snapping
    snap_location = None  # Snap location for surface snapping
    highlighted_wall = None  # Currently highlighted wall object

    def get_default_typing_target(self):
        """When user starts typing, they're entering wall length."""
        return hb_placement.TypingTarget.LENGTH

    def find_nearby_wall_endpoint(self, context, threshold=0.15):
        """
        Find if mouse is near any existing wall endpoint.
        
        Args:
            context: Blender context
            threshold: Distance threshold in meters
            
        Returns:
            Tuple of (wall_obj, endpoint_type, endpoint_location) or (None, None, None)
            endpoint_type is 'start' or 'end'
        """
        if not self.hit_location:
            return None, None, None
        
        mouse_loc = Vector((self.hit_location[0], self.hit_location[1], 0))
        
        best_wall = None
        best_endpoint = None
        best_location = None
        best_distance = threshold
        
        for obj in context.view_layer.objects:
            if 'IS_WALL_BP' not in obj:
                continue
            # Skip the current wall being drawn
            if self.current_wall and obj == self.current_wall.obj:
                continue
            
            # Get wall endpoints
            start, end = get_wall_endpoints(obj)
            start_3d = Vector((start.x, start.y, 0))
            end_3d = Vector((end.x, end.y, 0))
            
            # Check start point
            dist_start = (mouse_loc - start_3d).length
            if dist_start < best_distance:
                best_distance = dist_start
                best_wall = obj
                best_endpoint = 'start'
                best_location = start_3d
            
            # Check end point
            dist_end = (mouse_loc - end_3d).length
            if dist_end < best_distance:
                best_distance = dist_end
                best_wall = obj
                best_endpoint = 'end'
                best_location = end_3d
        
        return best_wall, best_endpoint, best_location

    def highlight_wall(self, wall_obj, highlight=True):
        """Highlight or unhighlight a wall."""
        if wall_obj is None:
            return
        
        # Check if object is still valid and in the view layer
        try:
            if wall_obj.name not in bpy.context.view_layer.objects:
                return
        except ReferenceError:
            return
        
        if highlight:
            # Store original color and set highlight color
            if 'original_color' not in wall_obj:
                wall_obj['original_color'] = list(wall_obj.color)
            wall_obj.color = (0.0, 1.0, 0.5, 1.0)  # Green highlight
            wall_obj.select_set(True)
        else:
            # Restore original color
            if 'original_color' in wall_obj:
                wall_obj.color = wall_obj['original_color']
                del wall_obj['original_color']
            wall_obj.select_set(False)

    def clear_wall_highlight(self):
        """Clear any highlighted wall."""
        if self.highlighted_wall:
            try:
                # Check if object is still valid before trying to unhighlight
                if self.highlighted_wall.name in bpy.context.view_layer.objects:
                    self.highlight_wall(self.highlighted_wall, highlight=False)
            except ReferenceError:
                pass
            self.highlighted_wall = None
        self.snap_wall = None
        self.snap_endpoint = None
        self.snap_surface = None
        self.snap_location = None

    def is_top_view(self, context):
        """Check if we're looking from above (top-ish view)."""
        view_matrix = context.region_data.view_matrix
        # Get the view direction (negative Z of view matrix = looking direction)
        view_dir = Vector((view_matrix[2][0], view_matrix[2][1], view_matrix[2][2]))
        # If view direction is mostly vertical (looking down), we're in top view
        # Check if the Z component dominates
        return abs(view_dir.z) > 0.7

    def find_wall_surface_snap_2d(self, context, threshold=0.15):
        """
        2D proximity-based wall surface detection for top view.
        Finds the nearest wall edge (front or back face) to the mouse position.
        
        Wall origin is at back face (local Y=0), front face is at Y=thickness.
        
        Returns:
            Tuple of (wall_obj, snap_location, face) or (None, None, None)
        """
        if not self.hit_location:
            return None, None, None
        
        mouse_2d = Vector((self.hit_location[0], self.hit_location[1]))
        
        best_wall = None
        best_location = None
        best_face = None
        best_distance = threshold
        
        for obj in context.view_layer.objects:
            if 'IS_WALL_BP' not in obj:
                continue
            if self.current_wall and obj == self.current_wall.obj:
                continue
            
            wall = hb_types.GeoNodeWall(obj)
            wall_length = wall.get_input('Length')
            wall_thickness = wall.get_input('Thickness')
            
            world_matrix = obj.matrix_world
            
            # Get wall direction vector (local X axis in world space) - column 0
            wall_dir = Vector((world_matrix[0][0], world_matrix[1][0])).normalized()
            # Get wall perpendicular (local Y axis in world space) - column 1
            wall_perp = Vector((world_matrix[0][1], world_matrix[1][1])).normalized()
            # Wall origin (back face at local Y=0) - column 3
            wall_origin = Vector((world_matrix[0][3], world_matrix[1][3]))
            
            # Back face is at origin (Y=0 in local)
            # Front face is at origin + perp * thickness (Y=thickness in local)
            for face, offset in [('back', 0), ('front', wall_thickness)]:
                # Edge start and end points
                edge_start = wall_origin + wall_perp * offset
                edge_end = edge_start + wall_dir * wall_length
                
                # Find closest point on edge line to mouse
                edge_vec = edge_end - edge_start
                edge_len = edge_vec.length
                if edge_len < 0.001:
                    continue
                edge_dir = edge_vec / edge_len
                
                # Project mouse onto edge line
                to_mouse = mouse_2d - edge_start
                proj_dist = to_mouse.dot(edge_dir)
                proj_dist = max(0, min(edge_len, proj_dist))  # Clamp to edge
                
                closest_point = edge_start + edge_dir * proj_dist
                distance = (mouse_2d - closest_point).length
                
                if distance < best_distance:
                    best_distance = distance
                    best_wall = obj
                    best_location = Vector((closest_point.x, closest_point.y, 0))
                    best_face = face
        
        return best_wall, best_location, best_face

    def find_wall_surface_snap(self, context):
        """
        Find if mouse is over/near a wall surface.
        Uses raycast in perspective/side views, 2D proximity in top view.
        
        Returns:
            Tuple of (wall_obj, snap_location, face) or (None, None, None)
            face is 'front' or 'back'
        """
        # In top view, use 2D proximity detection
        if self.is_top_view(context):
            return self.find_wall_surface_snap_2d(context)
        
        # Otherwise use raycast-based detection
        if not self.hit_object or not self.hit_location:
            return None, None, None
        
        # Check if we hit a wall (could be the wall itself or a child)
        wall_obj = None
        check_obj = self.hit_object
        while check_obj:
            if 'IS_WALL_BP' in check_obj:
                wall_obj = check_obj
                break
            check_obj = check_obj.parent
        
        if not wall_obj:
            return None, None, None
        
        # Skip the current wall being drawn
        if self.current_wall and wall_obj == self.current_wall.obj:
            return None, None, None
        
        wall = hb_types.GeoNodeWall(wall_obj)
        wall_length = wall.get_input('Length')
        wall_thickness = wall.get_input('Thickness')
        
        # Transform hit position to wall's local space
        world_matrix = wall_obj.matrix_world
        local_matrix = world_matrix.inverted()
        local_hit = local_matrix @ Vector((self.hit_location[0], self.hit_location[1], self.hit_location[2]))
        
        # Clamp X position to wall length
        snap_x = max(0, min(wall_length, local_hit.x))
        
        # Determine which face based on local Y
        if local_hit.y >= 0:
            face = 'front'
        else:
            face = 'back'
        
        # Keep the Y from the hit (it's on the surface), set Z to 0
        local_snap = Vector((snap_x, local_hit.y, 0))
        world_snap = world_matrix @ local_snap
        
        return wall_obj, Vector((world_snap.x, world_snap.y, 0)), face

    def find_chain_start(self, wall_obj):
        """Trace back through wall chain to find the first wall and count walls.
        
        Returns:
            Tuple of (first_wall_obj, wall_count) or (None, 0)
        """
        visited = set()
        current = hb_types.GeoNodeWall(wall_obj)
        count = 1
        
        while True:
            visited.add(current.obj.name)
            left_wall = current.get_connected_wall('left')
            if left_wall and left_wall.obj.name not in visited:
                current = left_wall
                count += 1
            else:
                break
        
        return current, count

    def connect_to_existing_wall(self, wall_obj, endpoint):
        """
        Connect current wall to an existing wall's endpoint and set up for continued drawing.
        
        Args:
            wall_obj: The existing wall to connect to
            endpoint: 'start' or 'end' - which endpoint to connect to
        """
        existing_wall = hb_types.GeoNodeWall(wall_obj)
        
        # Get the endpoint location
        start, end = get_wall_endpoints(wall_obj)
        
        if endpoint == 'end':
            # Connect to end of existing wall - our wall starts there
            connect_location = Vector((end.x, end.y, 0))
            # Set previous_wall so our wall connects properly
            self.previous_wall = existing_wall
            # Use constraint to connect
            self.current_wall.connect_to_wall(existing_wall)
            
            # Trace chain to find first wall for room closing
            first_wall_geonode, chain_count = self.find_chain_start(wall_obj)
            if chain_count >= 2:
                self.first_wall = first_wall_geonode
                self.confirmed_wall_count = chain_count
        else:
            # Connect to start of existing wall
            connect_location = Vector((start.x, start.y, 0))
            # Position our wall at the start point
            self.current_wall.obj.location = connect_location
        
        self.start_point = connect_location
        self.has_start_point = True

    def on_typed_value_changed(self):
        """Update dimension display as user types."""
        if self.typed_value:
            parsed = self.parse_typed_distance()
            if parsed is not None and self.current_wall:
                self.current_wall.set_input('Length', parsed)
                self.update_dimension(bpy.context)
        self.update_header(bpy.context)

    def apply_typed_value(self):
        """Apply typed length and advance to next wall."""
        parsed = self.parse_typed_distance()
        if parsed is not None and self.current_wall:
            self.current_wall.set_input('Length', parsed)
            self.update_dimension(bpy.context)
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
        return 10.0  # Default fallback

    def update_dimension(self, context=None):
        """Update dimension display to match wall length."""
        if self.current_wall and self.dim:
            length = self.current_wall.get_input('Length')
            height = self.current_wall.get_input('Height')
            self.dim.obj.location.z = height + units.inch(1)
            self.dim.obj.data.splines[0].points[1].co = (length, 0, 0, 0)
            
            # Update decimal precision based on value
            self.dim.set_decimal()
            
            # Scale text size based on view distance
            if context:
                view_dist = self.get_view_distance(context)
                # Base size at view distance of 10m, scale proportionally
                base_size = units.inch(8)
                text_size = base_size * (view_dist / 10.0)
                # Clamp to reasonable range
                text_size = max(units.inch(4), min(units.inch(24), text_size))
                self.dim.set_input("Text Size", text_size)

    def set_wall_position_from_mouse(self):
        """Update wall position/rotation based on mouse location."""
        if not self.has_start_point:
            # First point - just move the wall origin (snapped to grid)
            if self.hit_location:
                snapped_loc = hb_snap.snap_vector_to_grid(Vector(self.hit_location))
                self.current_wall.obj.location = snapped_loc
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
                
                # Length is the full distance to cursor (snapped to grid)
                length = math.sqrt(x * x + y * y)
                self.current_wall.set_input('Length', hb_snap.snap_value_to_grid(length))
            else:
                # Default mode - snap to orthogonal (90°) directions
                if abs(x) > abs(y):
                    # Horizontal
                    if x > 0:
                        self.current_wall.obj.rotation_euler.z = math.radians(0)
                    else:
                        self.current_wall.obj.rotation_euler.z = math.radians(180)
                    self.current_wall.set_input('Length', hb_snap.snap_value_to_grid(abs(x)))
                else:
                    # Vertical
                    if y > 0:
                        self.current_wall.obj.rotation_euler.z = math.radians(90)
                    else:
                        self.current_wall.obj.rotation_euler.z = math.radians(-90)
                    self.current_wall.set_input('Length', hb_snap.snap_value_to_grid(abs(y)))

            self.update_dimension(bpy.context)

    def close_room(self, context):
        """Close the room by connecting the current wall back to the first wall."""
        closing_wall = self.current_wall
        first_wall = self.first_wall
        
        # Calculate angle and distance to first wall's origin
        first_loc = first_wall.obj.location
        dx = first_loc.x - self.start_point.x
        dy = first_loc.y - self.start_point.y
        closing_length = math.sqrt(dx * dx + dy * dy)
        
        if closing_length < 0.01:
            return
        
        closing_angle = math.atan2(dy, dx)
        closing_wall.obj.rotation_euler.z = closing_angle
        closing_wall.set_input('Length', closing_length)
        
        # Connect closing wall's end to first wall
        closing_wall.obj_x.home_builder.connected_object = first_wall.obj
        
        context.view_layer.update()
        
        # Update miter angles for previous wall and closing wall's left side
        calculate_wall_miter_angles(closing_wall.obj)
        calculate_wall_miter_angles(self.previous_wall.obj)
        
        # Set miter angles between closing wall's end and first wall's start
        closing_rot = closing_wall.obj.rotation_euler.z
        first_rot = first_wall.obj.rotation_euler.z
        turn = first_rot - closing_rot
        while turn > math.pi: turn -= 2 * math.pi
        while turn < -math.pi: turn += 2 * math.pi
        closing_wall.set_input('Right Angle', -turn / 2)
        first_wall.set_input('Left Angle', turn / 2)
        
        # Remove closing wall from cancel list (it's confirmed)
        if closing_wall.obj in self.placement_objects:
            self.placement_objects.remove(closing_wall.obj)
        for child in closing_wall.obj.children:
            if child in self.placement_objects:
                self.placement_objects.remove(child)
        
        # Clean up dimension
        if self.dim:
            if self.dim.obj in self.placement_objects:
                self.placement_objects.remove(self.dim.obj)
            bpy.data.objects.remove(self.dim.obj, do_unlink=True)

    def confirm_current_wall(self):
        """Finalize current wall and prepare for next."""
        # Capture the very first start point (before it gets updated)
        if self.first_start_point is None:
            self.first_start_point = self.start_point.copy()
        
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

        self.confirmed_wall_count += 1
        if self.confirmed_wall_count == 1:
            self.first_wall = self.current_wall
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
            close_hint = " | C: close room" if self.confirmed_wall_count >= 2 and self.first_wall is not None else ""
            text = f"Length: {length_str} | Angle: {angle_deg}° | {rotation_mode} | Alt: toggle rotation | Type for exact | Click to place{close_hint}"
        else:
            if self.snap_wall and self.snap_endpoint:
                text = "Click to connect to wall endpoint | Right-click to cancel | Esc to cancel"
            elif self.snap_wall and self.snap_surface:
                text = f"Click to start on wall ({self.snap_surface} face) | Right-click to cancel | Esc to cancel"
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
        self.first_start_point = None
        self.first_wall = None
        self.confirmed_wall_count = 0
        
        # Reset endpoint snapping state
        self.snap_wall = None
        self.snap_endpoint = None
        self.snap_surface = None
        self.snap_location = None
        self.highlighted_wall = None

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

        # Check for nearby wall endpoints or surfaces (only before first point placed)
        if not self.has_start_point:
            # First check for endpoint snap (higher priority)
            snap_wall, snap_endpoint, snap_location = self.find_nearby_wall_endpoint(context)
            
            if snap_wall:
                # Endpoint snap found
                if snap_wall != self.highlighted_wall:
                    self.clear_wall_highlight()
                    self.highlight_wall(snap_wall, highlight=True)
                    self.highlighted_wall = snap_wall
                
                self.snap_wall = snap_wall
                self.snap_endpoint = snap_endpoint
                self.snap_surface = None
                self.snap_location = snap_location
                self.hit_location = snap_location
            else:
                # No endpoint - check for wall surface snap
                surface_wall, surface_location, surface_face = self.find_wall_surface_snap(context)
                
                if surface_wall:
                    # Surface snap found
                    if surface_wall != self.highlighted_wall:
                        self.clear_wall_highlight()
                        self.highlight_wall(surface_wall, highlight=True)
                        self.highlighted_wall = surface_wall
                    
                    self.snap_wall = surface_wall
                    self.snap_endpoint = None
                    self.snap_surface = surface_face
                    self.snap_location = surface_location
                    self.hit_location = surface_location
                else:
                    # No snap - clear any highlighting
                    if self.highlighted_wall:
                        self.clear_wall_highlight()

        # Update position if not typing
        if self.placement_state != hb_placement.PlacementState.TYPING:
            self.set_wall_position_from_mouse()

        self.update_header(context)

        # Left click - place point
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if not self.has_start_point:
                # Check if we're snapping to an existing wall endpoint
                if self.snap_wall and self.snap_endpoint:
                    self.connect_to_existing_wall(self.snap_wall, self.snap_endpoint)
                    self.clear_wall_highlight()
                elif self.snap_wall and self.snap_surface:
                    # Snapping to wall surface - use snap location as start point
                    self.start_point = Vector(self.snap_location)
                    self.has_start_point = True
                    self.clear_wall_highlight()
                else:
                    # Set first point normally (snapped to grid)
                    self.start_point = hb_snap.snap_vector_to_grid(Vector(self.hit_location))
                    self.has_start_point = True
            else:
                # Confirm wall and start next
                self.confirm_current_wall()
            return {'RUNNING_MODAL'}

        # Right click - finish drawing
        if event.type == 'RIGHTMOUSE' and event.value == 'PRESS':
            # Clear any wall highlight
            self.clear_wall_highlight()
            # Remove current unfinished wall
            self.cancel_placement(context)
            hb_placement.clear_header_text(context)
            return {'FINISHED'}

        # Escape - cancel everything
        if event.type == 'ESC' and event.value == 'PRESS':
            # Clear any wall highlight
            self.clear_wall_highlight()
            self.cancel_placement(context)
            hb_placement.clear_header_text(context)
            return {'CANCELLED'}

        # C key - close room (requires 2+ confirmed walls)
        if event.type == 'C' and event.value == 'PRESS' and self.has_start_point:
            if self.confirmed_wall_count >= 2 and self.first_wall is not None:
                self.close_room(context)
                self.clear_wall_highlight()
                hb_placement.clear_header_text(context)
                return {'FINISHED'}
            return {'RUNNING_MODAL'}

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
        
        # UV unwrap - planar projection from top down (X,Y -> U,V)
        uv_layer = bm.loops.layers.uv.new("UVMap")
        for face in bm.faces:
            for loop in face.loops:
                loop[uv_layer].uv = (loop.vert.co.x, loop.vert.co.y)
        
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



class home_builder_walls_OT_add_ceiling(bpy.types.Operator):
    bl_idname = "home_builder_walls.add_ceiling"
    bl_label = "Add Ceiling"
    bl_description = "This will add a ceiling to the room based on the wall layout"
    bl_options = {'UNDO'}

    def create_ceiling_mesh(self, name, points, height):
        """Create a ceiling mesh from boundary points at the given height."""
        mesh = bpy.data.meshes.new(name)
        obj = bpy.data.objects.new(name, mesh)

        bpy.context.collection.objects.link(obj)

        bm = bmesh.new()

        # If closed loop, remove duplicate closing point
        closed = is_closed_loop(points)
        if closed:
            points = points[:-1]

        # Add vertices at ceiling height
        verts = [bm.verts.new(Vector((p.x, p.y, height))) for p in points]
        bm.verts.ensure_lookup_table()

        # Create boundary edges
        edges = []
        for i in range(len(verts)):
            next_i = (i + 1) % len(verts)
            edge = bm.edges.new((verts[i], verts[next_i]))
            edges.append(edge)

        # Fill to create faces
        bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=edges)

        # Flip normals so they face downward (into the room)
        bmesh.ops.reverse_faces(bm, faces=bm.faces[:])

        # UV unwrap - planar projection from top down (X,Y -> U,V)
        uv_layer = bm.loops.layers.uv.new("UVMap")
        for face in bm.faces:
            for loop in face.loops:
                loop[uv_layer].uv = (loop.vert.co.x, loop.vert.co.y)

        bm.to_mesh(mesh)
        bm.free()

        return obj

    def execute(self, context):
        props = context.scene.home_builder
        ceiling_height = props.ceiling_height

        chains = find_wall_chains()

        if not chains:
            self.report({'WARNING'}, "No connected walls found")
            return {'CANCELLED'}

        ceilings_created = 0
        for i, chain in enumerate(chains):
            # Try to get ceiling height from the first wall in the chain
            wall = hb_types.GeoNodeWall(chain[0])
            chain_height = wall.get_input('Height')
            if chain_height is None or chain_height == 0:
                chain_height = ceiling_height

            points = get_room_boundary_points(chain)

            # Handle cases with only 1 or 2 walls
            if len(points) < 3 or (len(points) <= 3 and not is_closed_loop(points)):
                all_points = []
                for w in chain:
                    start, end = get_wall_endpoints(w)
                    all_points.append(Vector((start.x, start.y, 0)))
                    all_points.append(Vector((end.x, end.y, 0)))

                if len(all_points) >= 2:
                    min_x = min(p.x for p in all_points)
                    max_x = max(p.x for p in all_points)
                    min_y = min(p.y for p in all_points)
                    max_y = max(p.y for p in all_points)

                    if abs(max_x - min_x) < 0.01:
                        max_x = min_x + 3.0
                    if abs(max_y - min_y) < 0.01:
                        max_y = min_y + 3.0

                    points = [
                        Vector((min_x, min_y, 0)),
                        Vector((max_x, min_y, 0)),
                        Vector((max_x, max_y, 0)),
                        Vector((min_x, max_y, 0)),
                        Vector((min_x, min_y, 0)),
                    ]
                else:
                    continue
            else:
                if not is_closed_loop(points):
                    points.append(points[0].copy())

            name = "Ceiling" if i == 0 else f"Ceiling.{i:03d}"

            ceiling_obj = self.create_ceiling_mesh(name, points, chain_height)
            ceiling_obj['IS_CEILING_BP'] = True

            ceilings_created += 1

        if ceilings_created > 0:
            self.report({'INFO'}, f"Created {ceilings_created} ceiling(s)")
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Could not create ceiling - insufficient wall data")
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
        
        # Create or get scene-specific collection for lights
        scene = bpy.context.scene
        light_collection_name = f"{scene.name} - Lights"
        if light_collection_name not in bpy.data.collections:
            light_collection = bpy.data.collections.new(light_collection_name)
            scene.collection.children.link(light_collection)
        else:
            light_collection = bpy.data.collections[light_collection_name]
            # Ensure it's linked to the current scene
            if light_collection.name not in scene.collection.children:
                scene.collection.children.link(light_collection)
        
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
            
            # Handle cases with only 1 or 2 walls - create rectangular boundary from bounding box
            if len(points) < 3 or (len(points) <= 3 and not is_closed_loop(points)):
                all_points = []
                for wall in chain:
                    start, end = get_wall_endpoints(wall)
                    all_points.append(Vector((start.x, start.y, 0)))
                    all_points.append(Vector((end.x, end.y, 0)))
                
                if len(all_points) < 2:
                    continue
                
                min_x = min(p.x for p in all_points)
                max_x = max(p.x for p in all_points)
                min_y = min(p.y for p in all_points)
                max_y = max(p.y for p in all_points)
                
                if abs(max_x - min_x) < 0.01:
                    max_x = min_x + 3.0
                if abs(max_y - min_y) < 0.01:
                    max_y = min_y + 3.0
                
                points = [
                    Vector((min_x, min_y, 0)),
                    Vector((max_x, min_y, 0)),
                    Vector((max_x, max_y, 0)),
                    Vector((min_x, max_y, 0)),
                    Vector((min_x, min_y, 0)),
                ]
            else:
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



class home_builder_walls_OT_delete_room_lights(bpy.types.Operator):
    bl_idname = "home_builder_walls.delete_room_lights"
    bl_label = "Delete All Room Lights"
    bl_description = "Remove all room lights from the scene"
    bl_options = {'UNDO'}

    def execute(self, context):
        light_objects = [obj for obj in context.scene.objects if obj.get('IS_ROOM_LIGHT')]

        if not light_objects:
            self.report({'WARNING'}, "No room lights found")
            return {'CANCELLED'}

        count = len(light_objects)
        for obj in light_objects:
            light_data = obj.data
            bpy.data.objects.remove(obj, do_unlink=True)
            if light_data and light_data.users == 0:
                bpy.data.lights.remove(light_data)

        # Remove empty lights collection (check both old and new naming)
        scene = context.scene
        for col_name in [f"{scene.name} - Lights", "Room Lights"]:
            if col_name in bpy.data.collections:
                col = bpy.data.collections[col_name]
                if len(col.objects) == 0:
                    if col.name in scene.collection.children:
                        scene.collection.children.unlink(col)
                    bpy.data.collections.remove(col)

        self.report({'INFO'}, f"Deleted {count} room light(s)")
        return {'FINISHED'}


class home_builder_walls_OT_update_room_lights(bpy.types.Operator):
    bl_idname = "home_builder_walls.update_room_lights"
    bl_label = "Update Room Lights"
    bl_description = "Update properties of all room lights"
    bl_options = {'UNDO'}

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

    light_radius: bpy.props.FloatProperty(
        name="Shadow Softness",
        description="Light source radius for shadow softness",
        default=0.1,
        min=0.0,
        max=1.0,
        unit='LENGTH'
    )  # type: ignore

    def kelvin_to_rgb(self, temperature):
        temp = temperature / 100.0
        if temp <= 66:
            red = 255
        else:
            red = temp - 60
            red = 329.698727446 * (red ** -0.1332047592)
            red = max(0, min(255, red))
        if temp <= 66:
            green = temp
            green = 99.4708025861 * math.log(green) - 161.1195681661
        else:
            green = temp - 60
            green = 288.1221695283 * (green ** -0.0755148492)
        green = max(0, min(255, green))
        if temp >= 66:
            blue = 255
        elif temp <= 19:
            blue = 0
        else:
            blue = temp - 10
            blue = 138.5177312231 * math.log(blue) - 305.0447927307
            blue = max(0, min(255, blue))
        return (red / 255.0, green / 255.0, blue / 255.0)

    def invoke(self, context, event):
        # Initialize from existing lights
        light_objects = [obj for obj in context.scene.objects if obj.get('IS_ROOM_LIGHT')]
        if not light_objects:
            self.report({'WARNING'}, "No room lights found")
            return {'CANCELLED'}

        # Read current values from first light
        first_light = light_objects[0].data
        self.light_power = first_light.energy
        self.light_radius = first_light.shadow_soft_size

        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=350)

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="Light Properties", icon='OUTLINER_OB_LIGHT')
        col = box.column(align=True)
        col.prop(self, 'light_power')
        col.prop(self, 'light_temperature')
        col.prop(self, 'light_radius')

    def execute(self, context):
        light_objects = [obj for obj in context.scene.objects if obj.get('IS_ROOM_LIGHT')]

        if not light_objects:
            self.report({'WARNING'}, "No room lights found")
            return {'CANCELLED'}

        color = self.kelvin_to_rgb(self.light_temperature)

        for obj in light_objects:
            obj.data.energy = self.light_power
            obj.data.color = color
            obj.data.shadow_soft_size = self.light_radius

        self.report({'INFO'}, f"Updated {len(light_objects)} room light(s)")
        return {'FINISHED'}


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




class home_builder_walls_OT_setup_world_lighting(bpy.types.Operator):
    bl_idname = "home_builder_walls.setup_world_lighting"
    bl_label = "Setup World Lighting"
    bl_description = "Setup world environment lighting using HDRI or Sky texture"
    bl_options = {'REGISTER', 'UNDO'}
    
    lighting_type: bpy.props.EnumProperty(
        name="Lighting Type",
        items=[
            ('HDRI', 'HDRI Environment', 'Use an HDRI image for environment lighting'),
            ('SKY', 'Sky Texture', 'Use a procedural sky texture'),
        ],
        default='HDRI'
    )  # type: ignore
    
    hdri_choice: bpy.props.EnumProperty(
        name="HDRI",
        items=[
            ('studio.exr', 'Studio', 'Clean studio lighting'),
            ('interior.exr', 'Interior', 'Interior room lighting'),
            ('courtyard.exr', 'Courtyard', 'Outdoor courtyard'),
            ('forest.exr', 'Forest', 'Forest environment'),
            ('city.exr', 'City', 'Urban environment'),
            ('sunrise.exr', 'Sunrise', 'Warm sunrise lighting'),
            ('sunset.exr', 'Sunset', 'Golden sunset lighting'),
            ('night.exr', 'Night', 'Night time lighting'),
        ],
        default='studio.exr'
    )  # type: ignore
    
    hdri_strength: bpy.props.FloatProperty(
        name="Strength",
        description="Brightness of the environment",
        default=1.0,
        min=0.0,
        max=10.0
    )  # type: ignore
    
    hdri_rotation: bpy.props.FloatProperty(
        name="Rotation",
        description="Rotate the environment horizontally",
        default=0.0,
        min=0.0,
        max=360.0,
        subtype='ANGLE'
    )  # type: ignore
    
    # Sky texture options
    sky_type: bpy.props.EnumProperty(
        name="Sky Type",
        items=[
            ('PREETHAM', 'Preetham', 'Simple sky model'),
            ('HOSEK_WILKIE', 'Hosek/Wilkie', 'More accurate sky model'),
            ('SINGLE_SCATTERING', 'Single Scattering', 'Realistic atmospheric scattering'),
            ('MULTIPLE_SCATTERING', 'Multiple Scattering', 'Most realistic atmospheric scattering'),
        ],
        default='MULTIPLE_SCATTERING'
    )  # type: ignore
    
    sun_elevation: bpy.props.FloatProperty(
        name="Sun Elevation",
        description="Angle of the sun above the horizon",
        default=0.7854,  # 45 degrees
        min=0.0,
        max=1.5708,  # 90 degrees
        subtype='ANGLE'
    )  # type: ignore
    
    sun_rotation: bpy.props.FloatProperty(
        name="Sun Rotation",
        description="Horizontal rotation of the sun",
        default=0.0,
        min=0.0,
        max=6.2832,  # 360 degrees
        subtype='ANGLE'
    )  # type: ignore
    
    sky_strength: bpy.props.FloatProperty(
        name="Strength",
        description="Brightness of the sky",
        default=1.0,
        min=0.0,
        max=10.0
    )  # type: ignore

    def get_hdri_path(self):
        """Get path to Blender's bundled HDRI files"""
        blender_dir = os.path.dirname(bpy.app.binary_path)
        version = f"{bpy.app.version[0]}.{bpy.app.version[1]}"
        hdri_path = os.path.join(blender_dir, version, "datafiles", "studiolights", "world")
        return hdri_path

    def setup_hdri(self, context):
        """Setup HDRI environment lighting"""
        world = context.scene.world
        if not world:
            world = bpy.data.worlds.new("World")
            context.scene.world = world
        
        world.use_nodes = True
        nodes = world.node_tree.nodes
        links = world.node_tree.links
        
        # Clear existing nodes
        nodes.clear()
        
        # Create nodes
        output = nodes.new(type='ShaderNodeOutputWorld')
        output.location = (400, 0)
        
        background = nodes.new(type='ShaderNodeBackground')
        background.location = (200, 0)
        background.inputs['Strength'].default_value = self.hdri_strength
        
        env_tex = nodes.new(type='ShaderNodeTexEnvironment')
        env_tex.location = (-200, 0)
        
        tex_coord = nodes.new(type='ShaderNodeTexCoord')
        tex_coord.location = (-600, 0)
        
        mapping = nodes.new(type='ShaderNodeMapping')
        mapping.location = (-400, 0)
        mapping.inputs['Rotation'].default_value[2] = self.hdri_rotation
        
        # Load HDRI image
        hdri_path = os.path.join(self.get_hdri_path(), self.hdri_choice)
        if os.path.exists(hdri_path):
            img = bpy.data.images.load(hdri_path, check_existing=True)
            env_tex.image = img
        else:
            self.report({'WARNING'}, f"HDRI file not found: {hdri_path}")
            return False
        
        # Connect nodes
        links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
        links.new(mapping.outputs['Vector'], env_tex.inputs['Vector'])
        links.new(env_tex.outputs['Color'], background.inputs['Color'])
        links.new(background.outputs['Background'], output.inputs['Surface'])
        
        return True

    def setup_sky(self, context):
        """Setup procedural sky texture"""
        world = context.scene.world
        if not world:
            world = bpy.data.worlds.new("World")
            context.scene.world = world
        
        world.use_nodes = True
        nodes = world.node_tree.nodes
        links = world.node_tree.links
        
        # Clear existing nodes
        nodes.clear()
        
        # Create nodes
        output = nodes.new(type='ShaderNodeOutputWorld')
        output.location = (400, 0)
        
        background = nodes.new(type='ShaderNodeBackground')
        background.location = (200, 0)
        background.inputs['Strength'].default_value = self.sky_strength
        
        sky_tex = nodes.new(type='ShaderNodeTexSky')
        sky_tex.location = (-100, 0)
        sky_tex.sky_type = self.sky_type
        sky_tex.sun_elevation = self.sun_elevation
        sky_tex.sun_rotation = self.sun_rotation
        
        # Connect nodes
        links.new(sky_tex.outputs['Color'], background.inputs['Color'])
        links.new(background.outputs['Background'], output.inputs['Surface'])
        
        return True

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=350)

    def draw(self, context):
        layout = self.layout
        
        layout.prop(self, "lighting_type", expand=True)
        
        layout.separator()
        
        if self.lighting_type == 'HDRI':
            box = layout.box()
            box.label(text="HDRI Settings", icon='WORLD')
            col = box.column(align=True)
            col.prop(self, "hdri_choice", text="Environment")
            col.prop(self, "hdri_strength")
            col.prop(self, "hdri_rotation")
        else:
            box = layout.box()
            box.label(text="Sky Settings", icon='LIGHT_SUN')
            col = box.column(align=True)
            col.prop(self, "sky_type")
            col.prop(self, "sun_elevation")
            col.prop(self, "sun_rotation")
            col.prop(self, "sky_strength")

    def execute(self, context):
        if self.lighting_type == 'HDRI':
            if self.setup_hdri(context):
                self.report({'INFO'}, f"Setup HDRI environment: {self.hdri_choice}")
            else:
                return {'CANCELLED'}
        else:
            if self.setup_sky(context):
                self.report({'INFO'}, f"Setup {self.sky_type} sky texture")
            else:
                return {'CANCELLED'}
        
        return {'FINISHED'}


class home_builder_walls_OT_apply_wall_material(bpy.types.Operator):
    bl_idname = "home_builder_walls.apply_wall_material"
    bl_label = "Apply Wall Material"
    bl_description = "Apply the wall material to all walls in the scene"
    bl_options = {'UNDO'}

    def execute(self, context):
        props = context.scene.home_builder
        mat = props.wall_material
        if not mat:
            self.report({'WARNING'}, "No wall material selected")
            return {'CANCELLED'}
        
        material_inputs = [
            'Top Surface', 'Bottom Surface',
            'Inside Face', 'Outside Face',
            'Left Edge', 'Right Edge',
        ]
        wall_count = 0
        for obj in context.scene.objects:
            if obj.get('IS_WALL_BP'):
                wall = hb_types.GeoNodeWall(obj)
                for input_name in material_inputs:
                    wall.set_input(input_name, mat)
                wall_count += 1
        
        self.report({'INFO'}, f"Applied material to {wall_count} wall(s)")
        return {'FINISHED'}




class home_builder_walls_OT_delete_wall(bpy.types.Operator):
    """Delete a wall and properly disconnect from adjacent walls"""
    bl_idname = "home_builder_walls.delete_wall"
    bl_label = "Delete Wall"
    bl_description = "Delete the selected wall, removing all children and disconnecting from adjacent walls"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj and obj.get('IS_WALL_BP'):
            return True
        # Check if parent is a wall
        if obj and obj.parent and obj.parent.get('IS_WALL_BP'):
            return True
        return False

    def get_wall_bp(self, obj):
        """Get the wall base point object."""
        if obj.get('IS_WALL_BP'):
            return obj
        if obj.parent and obj.parent.get('IS_WALL_BP'):
            return obj.parent
        return None

    def execute(self, context):
        wall_bp = self.get_wall_bp(context.active_object)
        if not wall_bp:
            self.report({'WARNING'}, "No wall selected")
            return {'CANCELLED'}

        wall = hb_types.GeoNodeWall(wall_bp)

        # Find connected walls before we start deleting
        left_wall = wall.get_connected_wall('left')
        right_wall = wall.get_connected_wall('right')

        # Handle right wall (next wall constrained to our obj_x)
        if right_wall:
            # Store world location before removing constraint
            right_world_loc = right_wall.obj.matrix_world.translation.copy()

            # Remove the COPY_LOCATION constraint from right wall
            for con in right_wall.obj.constraints:
                if con.type == 'COPY_LOCATION' and con.target == wall.obj_x:
                    right_wall.obj.constraints.remove(con)
                    break

            # Set location to stored world location
            right_wall.obj.location = right_world_loc

        # Handle left wall (our wall is constrained to left wall's obj_x)
        if left_wall:
            # Clear the connected_object reference on the left wall's obj_x
            if left_wall.obj_x:
                left_wall.obj_x.home_builder.connected_object = None

        # Collect all objects to delete (wall bp + all children recursively)
        objects_to_delete = set()
        objects_to_delete.add(wall_bp)
        for child in wall_bp.children_recursive:
            objects_to_delete.add(child)

        # Deselect all first
        bpy.ops.object.select_all(action='DESELECT')

        # Delete all collected objects
        for obj in objects_to_delete:
            bpy.data.objects.remove(obj, do_unlink=True)

        # Update miter angles on remaining adjacent walls
        if left_wall and left_wall.obj.name in bpy.data.objects:
            calculate_wall_miter_angles(left_wall.obj)
        if right_wall and right_wall.obj.name in bpy.data.objects:
            calculate_wall_miter_angles(right_wall.obj)

        self.report({'INFO'}, "Wall deleted")
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)



class home_builder_walls_OT_hide_wall(bpy.types.Operator):
    """Hide the selected wall and all its children"""
    bl_idname = "home_builder_walls.hide_wall"
    bl_label = "Hide Wall"
    bl_description = "Hide the selected wall and all of its children"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj and obj.get('IS_WALL_BP'):
            return True
        if obj and obj.parent and obj.parent.get('IS_WALL_BP'):
            return True
        return False

    def execute(self, context):
        obj = context.active_object
        wall_bp = obj if obj.get('IS_WALL_BP') else obj.parent

        wall_bp.hide_set(True)
        wall_bp.hide_viewport = True
        for child in wall_bp.children_recursive:
            child.hide_set(True)
            child.hide_viewport = True

        self.report({'INFO'}, f"Wall hidden")
        return {'FINISHED'}


class home_builder_walls_OT_show_all_walls(bpy.types.Operator):
    """Show all hidden walls in the scene"""
    bl_idname = "home_builder_walls.show_all_walls"
    bl_label = "Show All Walls"
    bl_description = "Unhide all hidden walls and their children"
    bl_options = {'UNDO'}

    def execute(self, context):
        count = 0
        for obj in context.scene.objects:
            if obj.get('IS_WALL_BP') and (obj.hide_get() or obj.hide_viewport):
                obj.hide_set(False)
                obj.hide_viewport = False
                for child in obj.children_recursive:
                    child.hide_set(False)
                    child.hide_viewport = False
                count += 1

        if count > 0:
            self.report({'INFO'}, f"Restored {count} hidden wall(s)")
        else:
            self.report({'INFO'}, "No hidden walls found")
        return {'FINISHED'}

classes = (
    home_builder_walls_OT_hide_wall,
    home_builder_walls_OT_show_all_walls,
    home_builder_walls_OT_delete_wall,
    home_builder_walls_OT_draw_walls,
    home_builder_walls_OT_wall_prompts,
    home_builder_walls_OT_add_floor,
    home_builder_walls_OT_add_ceiling,
    home_builder_walls_OT_add_room_lights,
    home_builder_walls_OT_setup_world_lighting,
    home_builder_walls_OT_delete_room_lights,
    home_builder_walls_OT_update_room_lights,
    home_builder_walls_OT_update_wall_height,
    home_builder_walls_OT_update_wall_thickness,
    home_builder_walls_OT_update_wall_miters,
    home_builder_walls_OT_apply_wall_material,
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
    """Find connected chains of walls in the current scene, returning list of ordered wall objects."""
    walls = [obj for obj in bpy.context.scene.objects if obj.get('IS_WALL_BP')]
    
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
