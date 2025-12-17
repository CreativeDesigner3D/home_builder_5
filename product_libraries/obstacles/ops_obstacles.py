import bpy
import math
from mathutils import Vector, Matrix
from ... import hb_utils, hb_snap, hb_placement, hb_types, units
from . import props_obstacles


# =============================================================================
# OBSTACLE CREATION UTILITIES
# =============================================================================

def create_obstacle_mesh(name, width, height, depth, obstacle_type):
    """Create a simple box mesh for the obstacle."""
    import bmesh
    
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    
    bm = bmesh.new()
    
    # Circular obstacles
    if any(x in obstacle_type for x in ['CIRCLE', 'RECESSED', 'SPRINKLER', 'DETECTOR', 'FAN', 'DRAIN']):
        bmesh.ops.create_cone(
            bm, segments=16,
            radius1=width / 2, radius2=width / 2,
            depth=depth, cap_ends=True
        )
    # Pipes/columns (vertical cylinder)
    elif 'PIPE' in obstacle_type or 'COLUMN' in obstacle_type:
        bmesh.ops.create_cone(
            bm, segments=12,
            radius1=width / 2, radius2=width / 2,
            depth=height, cap_ends=True
        )
    # Default box
    else:
        bmesh.ops.create_cube(bm, size=1.0)
        for v in bm.verts:
            v.co.x *= width
            v.co.y *= depth
            v.co.z *= height
    
    bm.to_mesh(mesh)
    bm.free()
    
    return obj


def get_obstacle_color(obstacle_type):
    """Get display color based on obstacle type."""
    if 'OUTLET' in obstacle_type or 'SWITCH' in obstacle_type:
        return (0.9, 0.9, 0.7, 1.0)  # Light yellow - electrical
    elif 'VENT' in obstacle_type:
        return (0.6, 0.8, 0.9, 1.0)  # Light blue - HVAC
    elif 'LIGHT' in obstacle_type or 'FAN' in obstacle_type:
        return (1.0, 0.95, 0.8, 1.0)  # Warm white - lighting
    elif 'FIRE' in obstacle_type or 'SMOKE' in obstacle_type or 'SPRINKLER' in obstacle_type:
        return (1.0, 0.4, 0.4, 1.0)  # Red - fire safety
    elif 'ACCESS' in obstacle_type:
        return (0.7, 0.7, 0.7, 1.0)  # Gray - access panels
    elif 'PIPE' in obstacle_type or 'COLUMN' in obstacle_type or 'BEAM' in obstacle_type:
        return (0.6, 0.5, 0.4, 1.0)  # Brown - structural
    elif 'DRAIN' in obstacle_type:
        return (0.5, 0.5, 0.6, 1.0)  # Blue-gray - plumbing
    else:
        return (0.8, 0.6, 0.4, 1.0)  # Orange - misc


# =============================================================================
# PLACEMENT OPERATOR
# =============================================================================

class home_builder_obstacles_OT_place_obstacle(bpy.types.Operator, hb_placement.PlacementMixin):
    bl_idname = "home_builder_obstacles.place_obstacle"
    bl_label = "Place Obstacle"
    bl_description = "Place an obstacle on a wall, floor, or ceiling"
    bl_options = {'UNDO'}
    
    # Obstacle object being placed
    obstacle_obj = None
    
    # Target wall (if placing on wall)
    target_wall = None
    target_type: str = 'FLOOR'  # 'WALL', 'FLOOR', 'CEILING'
    
    # Wall placement state
    wall_length: float = 0
    wall_position_x: float = 0  # Position along wall
    height_from_floor: float = 0
    
    # Obstacle dimensions (from scene props)
    obs_width: float = 0
    obs_height: float = 0
    obs_depth: float = 0
    obs_surface_type: str = 'ANY'
    
    def get_default_typing_target(self):
        """Default to offset from left when typing."""
        return hb_placement.TypingTarget.OFFSET_X
    
    def get_next_typing_target(self):
        """Cycle between offset and height."""
        if self.typing_target == hb_placement.TypingTarget.OFFSET_X:
            return hb_placement.TypingTarget.HEIGHT
        elif self.typing_target == hb_placement.TypingTarget.OFFSET_RIGHT:
            return hb_placement.TypingTarget.HEIGHT
        elif self.typing_target == hb_placement.TypingTarget.HEIGHT:
            return hb_placement.TypingTarget.OFFSET_X
        return hb_placement.TypingTarget.NONE
    
    def on_typed_value_changed(self):
        """Update position when typed value changes."""
        parsed = self.parse_typed_distance()
        if parsed is None:
            return
        
        if self.typing_target == hb_placement.TypingTarget.OFFSET_X:
            self.wall_position_x = parsed + self.obs_width / 2
        elif self.typing_target == hb_placement.TypingTarget.OFFSET_RIGHT:
            self.wall_position_x = self.wall_length - parsed - self.obs_width / 2
        elif self.typing_target == hb_placement.TypingTarget.HEIGHT:
            self.height_from_floor = parsed
    
    def apply_typed_value(self):
        """Apply typed value and exit typing mode."""
        self.on_typed_value_changed()
        self.stop_typing()
    
    # -------------------------------------------------------------------------
    # Wall utilities
    # -------------------------------------------------------------------------
    
    def get_walls_in_scene(self, context):
        """Get all wall objects in the current scene."""
        return [obj for obj in context.scene.objects if obj.get('IS_WALL_BP')]
    
    def get_wall_length(self, wall):
        """Get wall length from obj_x child or geometry node input."""
        for child in wall.children:
            if child.get('obj_x'):
                return child.location.x
        
        for mod in wall.modifiers:
            if mod.type == 'NODES' and mod.node_group:
                try:
                    return mod["Input_2"]
                except:
                    pass
        return 3.0
    
    def get_wall_thickness(self, wall):
        """Get wall thickness from geometry node input."""
        for mod in wall.modifiers:
            if mod.type == 'NODES' and mod.node_group:
                try:
                    return mod["Input_3"]
                except:
                    pass
        return units.inch(4.5)
    
    def find_nearest_wall(self, context, location):
        """
        Find the nearest wall to a 3D location.
        Returns (wall, position_along_wall, distance_to_wall).
        """
        if location is None:
            return None, 0, float('inf')
        
        walls = self.get_walls_in_scene(context)
        if not walls:
            return None, 0, float('inf')
        
        loc_2d = Vector((location.x, location.y))
        
        best_wall = None
        best_position = 0
        best_distance = float('inf')
        
        for wall in walls:
            # Get wall world position and rotation
            wall_start = wall.matrix_world.translation.copy()
            wall_start_2d = Vector((wall_start.x, wall_start.y))
            
            wall_length = self.get_wall_length(wall)
            wall_rot = wall.matrix_world.to_euler()
            wall_angle = wall_rot.z
            
            # Calculate wall direction and end point
            wall_dir = Vector((math.cos(wall_angle), math.sin(wall_angle)))
            wall_end_2d = wall_start_2d + wall_dir * wall_length
            
            # Project point onto wall line
            wall_vec = wall_end_2d - wall_start_2d
            to_point = loc_2d - wall_start_2d
            
            wall_len_sq = wall_vec.length_squared
            if wall_len_sq > 0.0001:
                t = to_point.dot(wall_vec) / wall_len_sq
                t = max(0, min(1, t))
            else:
                t = 0
            
            # Closest point on wall
            closest = wall_start_2d + wall_vec * t
            dist = (loc_2d - closest).length
            
            if dist < best_distance:
                best_distance = dist
                best_wall = wall
                best_position = t * wall_length
        
        return best_wall, best_position, best_distance
    
    # -------------------------------------------------------------------------
    # Obstacle creation
    # -------------------------------------------------------------------------
    
    def create_obstacle(self, context):
        """Create the obstacle mesh object."""
        hb_obs = context.scene.hb_obstacles
        obs_data = props_obstacles.get_obstacle_data(hb_obs.obstacle_type)
        
        if not obs_data:
            return None
        
        # Store dimensions
        self.obs_width = hb_obs.obstacle_width
        self.obs_height = hb_obs.obstacle_height
        self.obs_depth = hb_obs.obstacle_depth
        self.height_from_floor = hb_obs.obstacle_height_from_floor
        self.obs_surface_type = obs_data[8]
        
        # Create mesh
        self.obstacle_obj = create_obstacle_mesh(
            obs_data[1],
            self.obs_width,
            self.obs_height,
            self.obs_depth,
            hb_obs.obstacle_type
        )
        
        # Set properties
        self.obstacle_obj['IS_OBSTACLE'] = True
        self.obstacle_obj['OBSTACLE_TYPE'] = hb_obs.obstacle_type
        self.obstacle_obj['OBSTACLE_SURFACE'] = self.obs_surface_type
        
        # Set color
        color = get_obstacle_color(hb_obs.obstacle_type)
        self.obstacle_obj.color = color
        
        # Create material
        mat = bpy.data.materials.new(f"{obs_data[1]}_Mat")
        mat.use_nodes = True
        mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = color
        mat.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value = 0.8
        mat.blend_method = 'BLEND'
        self.obstacle_obj.data.materials.append(mat)
        
        # Link to scene
        context.scene.collection.objects.link(self.obstacle_obj)
        self.register_placement_object(self.obstacle_obj)
        
        return self.obstacle_obj
    
    def update_obstacle_position(self, context):
        """Update obstacle position based on current target."""
        if not self.obstacle_obj:
            return
        
        if self.target_type == 'WALL' and self.target_wall:
            # Get wall transform
            wall_start = self.target_wall.matrix_world.translation.copy()
            wall_rot = self.target_wall.matrix_world.to_euler()
            wall_angle = wall_rot.z
            wall_thickness = self.get_wall_thickness(self.target_wall)
            
            # Direction vectors
            wall_dir = Vector((math.cos(wall_angle), math.sin(wall_angle), 0))
            perp_dir = Vector((-math.sin(wall_angle), math.cos(wall_angle), 0))
            
            # Clamp position to wall bounds
            half_width = self.obs_width / 2
            pos_x = max(half_width, min(self.wall_length - half_width, self.wall_position_x))
            
            # Calculate position on wall surface
            pos = wall_start.copy()
            pos += wall_dir * pos_x
            pos += perp_dir * (wall_thickness / 2 + self.obs_depth / 2)
            pos.z = self.height_from_floor
            
            self.obstacle_obj.location = pos
            self.obstacle_obj.rotation_euler.z = wall_angle
            
        elif self.target_type == 'CEILING':
            if self.hit_location:
                ceiling_height = context.scene.home_builder.ceiling_height
                self.obstacle_obj.location = Vector((
                    self.hit_location.x,
                    self.hit_location.y,
                    ceiling_height - self.obs_depth / 2
                ))
            self.obstacle_obj.rotation_euler.z = 0
            
        else:  # FLOOR
            if self.hit_location:
                self.obstacle_obj.location = Vector((
                    self.hit_location.x,
                    self.hit_location.y,
                    self.obs_height / 2
                ))
            self.obstacle_obj.rotation_euler.z = 0
    
    def update_header(self, context):
        """Update header text display."""
        hb_obs = context.scene.hb_obstacles
        obs_data = props_obstacles.get_obstacle_data(hb_obs.obstacle_type)
        obs_name = obs_data[1] if obs_data else "Obstacle"
        
        if self.placement_state == hb_placement.PlacementState.TYPING:
            display = self.get_typed_display_string()
            text = f"{display}_ | Enter to confirm | Esc to cancel"
        elif self.target_type == 'WALL' and self.target_wall:
            pos_str = units.unit_to_string(context.scene.unit_settings, self.wall_position_x)
            len_str = units.unit_to_string(context.scene.unit_settings, self.wall_length)
            height_str = units.unit_to_string(context.scene.unit_settings, self.height_from_floor)
            text = f"{obs_name} | {self.target_wall.name} | Pos: {pos_str}/{len_str} | H: {height_str} | ← → H Tab | Click to place"
        else:
            text = f"{obs_name} ({self.target_type}) | Click to place | Esc to cancel"
        
        hb_placement.draw_header_text(context, text)
    
    # -------------------------------------------------------------------------
    # Operator methods
    # -------------------------------------------------------------------------
    
    def execute(self, context):
        hb_obs = context.scene.hb_obstacles
        
        if hb_obs.obstacle_type.startswith('HEADER_'):
            self.report({'WARNING'}, "Please select an obstacle type first")
            return {'CANCELLED'}
        
        # Initialize placement mixin
        self.init_placement(context)
        
        # Reset state
        self.obstacle_obj = None
        self.target_wall = None
        self.target_type = 'FLOOR'
        self.wall_length = 0
        self.wall_position_x = 0
        
        # Create obstacle
        if not self.create_obstacle(context):
            self.report({'ERROR'}, "Failed to create obstacle")
            return {'CANCELLED'}
        
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
    
    def modal(self, context, event):
        context.area.tag_redraw()
        
        # Ignore intermediate mouse moves
        if event.type == 'INBETWEEN_MOUSEMOVE':
            return {'RUNNING_MODAL'}
        
        # Handle arrow keys for typing targets
        if event.value == 'PRESS':
            if event.type == 'LEFT_ARROW':
                if self.placement_state == hb_placement.PlacementState.TYPING:
                    self.apply_typed_value()
                self.start_typing(hb_placement.TypingTarget.OFFSET_X)
                self.update_header(context)
                return {'RUNNING_MODAL'}
            
            if event.type == 'RIGHT_ARROW':
                if self.placement_state == hb_placement.PlacementState.TYPING:
                    self.apply_typed_value()
                self.start_typing(hb_placement.TypingTarget.OFFSET_RIGHT)
                self.update_header(context)
                return {'RUNNING_MODAL'}
            
            if event.type == 'H':
                if self.placement_state == hb_placement.PlacementState.TYPING:
                    self.apply_typed_value()
                self.start_typing(hb_placement.TypingTarget.HEIGHT)
                self.update_header(context)
                return {'RUNNING_MODAL'}
        
        # Handle typing events (numbers, backspace, enter)
        if self.handle_typing_event(event):
            self.update_obstacle_position(context)
            self.update_header(context)
            return {'RUNNING_MODAL'}
        
        # Update snap - hide obstacle during raycast
        if self.obstacle_obj:
            self.obstacle_obj.hide_set(True)
        self.update_snap(context, event)
        if self.obstacle_obj:
            self.obstacle_obj.hide_set(False)
        
        # Determine target based on surface type and hit location
        if self.placement_state != hb_placement.PlacementState.TYPING:
            if self.hit_location:
                wall, wall_pos, wall_dist = self.find_nearest_wall(context, self.hit_location)
                
                # Wall snap threshold (1 meter)
                snap_threshold = 1.0
                
                if self.obs_surface_type == 'WALL':
                    # WALL-only: always snap to nearest wall
                    if wall:
                        self.target_wall = wall
                        self.target_type = 'WALL'
                        self.wall_length = self.get_wall_length(wall)
                        self.wall_position_x = wall_pos
                elif self.obs_surface_type == 'CEILING':
                    self.target_wall = None
                    self.target_type = 'CEILING'
                elif self.obs_surface_type == 'FLOOR':
                    self.target_wall = None
                    self.target_type = 'FLOOR'
                else:  # ANY
                    if wall and wall_dist < snap_threshold:
                        self.target_wall = wall
                        self.target_type = 'WALL'
                        self.wall_length = self.get_wall_length(wall)
                        self.wall_position_x = wall_pos
                    else:
                        self.target_wall = None
                        self.target_type = 'FLOOR'
        
        # Update obstacle position
        self.update_obstacle_position(context)
        self.update_header(context)
        
        # Left click - place
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if self.obstacle_obj:
                # Parent to wall if on wall
                if self.target_wall:
                    self.obstacle_obj.parent = self.target_wall
                    self.obstacle_obj.matrix_parent_inverse = self.target_wall.matrix_world.inverted()
                
                # Keep the obstacle (remove from cleanup list)
                if self.obstacle_obj in self.placement_objects:
                    self.placement_objects.remove(self.obstacle_obj)
                
                # Select
                bpy.ops.object.select_all(action='DESELECT')
                self.obstacle_obj.select_set(True)
                context.view_layer.objects.active = self.obstacle_obj
                
                hb_placement.clear_header_text(context)
                self.report({'INFO'}, f"Placed {self.obstacle_obj.name}")
                return {'FINISHED'}
        
        # Cancel
        if event.type in {'RIGHTMOUSE', 'ESC'} and event.value == 'PRESS':
            if self.placement_state == hb_placement.PlacementState.TYPING:
                self.stop_typing()
                self.update_header(context)
                return {'RUNNING_MODAL'}
            
            self.cancel_placement(context)
            hb_placement.clear_header_text(context)
            return {'CANCELLED'}
        
        # Pass through navigation
        if hb_snap.event_is_pass_through(event):
            return {'PASS_THROUGH'}
        
        return {'RUNNING_MODAL'}


# =============================================================================
# DELETE OBSTACLE
# =============================================================================

class home_builder_obstacles_OT_delete_obstacle(bpy.types.Operator):
    bl_idname = "home_builder_obstacles.delete_obstacle"
    bl_label = "Delete Obstacle"
    bl_description = "Delete the selected obstacle"
    bl_options = {'UNDO'}
    
    object_name: bpy.props.StringProperty(name="Object Name", default="")  # type: ignore
    
    def execute(self, context):
        if self.object_name and self.object_name in bpy.data.objects:
            obj = bpy.data.objects[self.object_name]
        elif context.active_object and context.active_object.get('IS_OBSTACLE'):
            obj = context.active_object
        else:
            self.report({'WARNING'}, "No obstacle selected")
            return {'CANCELLED'}
        
        if not obj.get('IS_OBSTACLE'):
            self.report({'WARNING'}, "Selected object is not an obstacle")
            return {'CANCELLED'}
        
        name = obj.name
        bpy.data.objects.remove(obj, do_unlink=True)
        self.report({'INFO'}, f"Deleted: {name}")
        return {'FINISHED'}


# =============================================================================
# SELECT ALL OBSTACLES
# =============================================================================

class home_builder_obstacles_OT_select_obstacles(bpy.types.Operator):
    bl_idname = "home_builder_obstacles.select_all"
    bl_label = "Select All Obstacles"
    bl_description = "Select all obstacles in the scene"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        count = 0
        for obj in context.scene.objects:
            if obj.get('IS_OBSTACLE'):
                obj.select_set(True)
                count += 1
        
        self.report({'INFO'}, f"Selected {count} obstacles" if count else "No obstacles in scene")
        return {'FINISHED'}


# =============================================================================
# SELECT SINGLE OBSTACLE
# =============================================================================

class home_builder_obstacles_OT_select_obstacle(bpy.types.Operator):
    bl_idname = "home_builder_obstacles.select_obstacle"
    bl_label = "Select Obstacle"
    bl_description = "Select or deselect this obstacle"
    bl_options = {'UNDO'}
    
    object_name: bpy.props.StringProperty(name="Object Name", default="")  # type: ignore
    
    def execute(self, context):
        if not self.object_name or self.object_name not in bpy.data.objects:
            self.report({'WARNING'}, "Object not found")
            return {'CANCELLED'}
        
        obj = bpy.data.objects[self.object_name]
        
        if obj.select_get():
            obj.select_set(False)
        else:
            obj.select_set(True)
            context.view_layer.objects.active = obj
        
        return {'FINISHED'}


# =============================================================================
# EDIT OBSTACLE
# =============================================================================

class home_builder_obstacles_OT_edit_obstacle(bpy.types.Operator):
    bl_idname = "home_builder_obstacles.edit_obstacle"
    bl_label = "Edit Obstacle"
    bl_description = "Edit obstacle dimensions"
    bl_options = {'REGISTER', 'UNDO'}
    
    width: bpy.props.FloatProperty(name="Width", default=0.07, min=0.01, unit='LENGTH')  # type: ignore
    height: bpy.props.FloatProperty(name="Height", default=0.1143, min=0.01, unit='LENGTH')  # type: ignore
    depth: bpy.props.FloatProperty(name="Depth", default=0.05, min=0.01, unit='LENGTH')  # type: ignore
    
    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.get('IS_OBSTACLE')
    
    def invoke(self, context, event):
        obj = context.active_object
        if obj.type == 'MESH':
            from mathutils import Vector
            bounds = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
            self.width = max(v.x for v in bounds) - min(v.x for v in bounds)
            self.height = max(v.z for v in bounds) - min(v.z for v in bounds)
            self.depth = max(v.y for v in bounds) - min(v.y for v in bounds)
        return context.window_manager.invoke_props_dialog(self)
    
    def execute(self, context):
        obj = context.active_object
        loc, rot, parent = obj.location.copy(), obj.rotation_euler.copy(), obj.parent
        obs_type = obj.get('OBSTACLE_TYPE', 'CUSTOM_RECT')
        old_mesh = obj.data
        
        import bmesh
        mesh = bpy.data.meshes.new(obj.name)
        bm = bmesh.new()
        
        if 'CIRCLE' in obs_type or 'RECESSED' in obs_type:
            bmesh.ops.create_cone(bm, segments=16, radius1=self.width/2, radius2=self.width/2, depth=self.depth, cap_ends=True)
        else:
            bmesh.ops.create_cube(bm, size=1.0)
            for v in bm.verts:
                v.co.x *= self.width
                v.co.y *= self.depth
                v.co.z *= self.height
        
        bm.to_mesh(mesh)
        bm.free()
        
        obj.data = mesh
        bpy.data.meshes.remove(old_mesh)
        obj.location, obj.rotation_euler = loc, rot
        if parent:
            obj.parent = parent
        
        return {'FINISHED'}
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "width")
        layout.prop(self, "height")
        layout.prop(self, "depth")


# =============================================================================
# REGISTRATION
# =============================================================================

classes = (
    home_builder_obstacles_OT_place_obstacle,
    home_builder_obstacles_OT_delete_obstacle,
    home_builder_obstacles_OT_select_obstacles,
    home_builder_obstacles_OT_select_obstacle,
    home_builder_obstacles_OT_edit_obstacle,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
