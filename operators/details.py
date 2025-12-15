import bpy
import math
from mathutils import Vector
from .. import hb_details
from .. import hb_types
from .. import hb_snap
from .. import hb_placement
from .. import units


# Snap radius in pixels for vertex snapping
SNAP_RADIUS = 20


# =============================================================================
# SNAP INDICATOR DRAWING
# =============================================================================

def draw_snap_indicator(self, context):
    """Draw visual feedback for snapping - green circle when snapped, yellow when not."""
    import gpu
    from gpu_extras.batch import batch_for_shader
    import math
    
    if not hasattr(self, 'snap_screen_pos') or self.snap_screen_pos is None:
        return
    
    x, y = self.snap_screen_pos
    
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    gpu.state.blend_set('ALPHA')
    gpu.state.line_width_set(2.0)
    
    if self.is_snapped:
        # Green circle for snapped point
        color = (0.0, 1.0, 0.0, 1.0)
        radius = 10
    else:
        # Yellow circle for unsnapped point  
        color = (1.0, 1.0, 0.0, 0.8)
        radius = 6
    
    # Draw circle
    segments = 32
    circle_verts = []
    for i in range(segments + 1):
        angle = 2 * math.pi * i / segments
        cx = x + radius * math.cos(angle)
        cy = y + radius * math.sin(angle)
        circle_verts.append((cx, cy))
    
    shader.bind()
    shader.uniform_float("color", color)
    batch = batch_for_shader(shader, 'LINE_STRIP', {"pos": circle_verts})
    batch.draw(shader)
    
    # Draw crosshair inside circle if snapped
    if self.is_snapped:
        cross_size = 6
        cross_verts = [
            (x - cross_size, y), (x + cross_size, y),
            (x, y - cross_size), (x, y + cross_size),
        ]
        batch = batch_for_shader(shader, 'LINES', {"pos": cross_verts})
        batch.draw(shader)
    
    gpu.state.blend_set('NONE')
    gpu.state.line_width_set(1.0)


# =============================================================================
# DETAIL SCENE OPERATORS
# =============================================================================

class home_builder_details_OT_create_detail(bpy.types.Operator):
    bl_idname = "home_builder_details.create_detail"
    bl_label = "Create Detail"
    bl_description = "Create a new 2D detail drawing scene"
    bl_options = {'UNDO'}
    
    detail_name: bpy.props.StringProperty(
        name="Detail Name",
        default="Detail",
        description="Name for the new detail"
    )  # type: ignore
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "detail_name")
    
    def execute(self, context):
        detail = hb_details.DetailView()
        scene = detail.create(self.detail_name)
        
        # Switch to the new scene
        bpy.ops.home_builder_layouts.go_to_layout_view(scene_name=scene.name)
        
        self.report({'INFO'}, f"Created detail: {scene.name}")
        return {'FINISHED'}


class home_builder_details_OT_delete_detail(bpy.types.Operator):
    bl_idname = "home_builder_details.delete_detail"
    bl_label = "Delete Detail"
    bl_description = "Delete the selected detail scene"
    bl_options = {'UNDO'}
    
    scene_name: bpy.props.StringProperty(name="Scene Name")  # type: ignore
    
    def execute(self, context):
        if self.scene_name in bpy.data.scenes:
            scene = bpy.data.scenes[self.scene_name]
            
            # If we're deleting the current scene, switch to another first
            if context.scene == scene:
                # Find another scene to switch to
                other_scenes = [s for s in bpy.data.scenes if s != scene]
                if other_scenes:
                    context.window.scene = other_scenes[0]
            
            bpy.data.scenes.remove(scene)
            self.report({'INFO'}, f"Deleted detail: {self.scene_name}")
        
        return {'FINISHED'}


# =============================================================================
# LINE DRAWING OPERATOR
# =============================================================================

class home_builder_details_OT_draw_line(bpy.types.Operator, hb_placement.PlacementMixin):
    bl_idname = "home_builder_details.draw_line"
    bl_label = "Draw Line"
    bl_description = "Draw a 2D polyline. Click to place points, type for exact length. Snaps to existing vertices."
    bl_options = {'UNDO'}
    
    # Polyline state
    polyline: hb_details.GeoNodePolyline = None
    current_point: Vector = None  # The last confirmed point
    point_count: int = 0  # Number of confirmed points
    
    # Ortho mode (snap to 0, 45, 90 degree angles)
    ortho_mode: bool = True
    ortho_angle: float = 0.0
    
    # Snap state
    is_snapped: bool = False
    snap_screen_pos: tuple = None
    
    # Draw handler
    _handle = None
    
    def get_curve_vertices(self, context) -> list:
        """Get all curve vertices in the scene as world coordinates."""
        vertices = []
        for obj in context.scene.objects:
            if obj.type == 'CURVE' and (not self.polyline or obj != self.polyline.obj):
                matrix = obj.matrix_world
                for spline in obj.data.splines:
                    for point in spline.points:
                        world_co = matrix @ Vector((point.co[0], point.co[1], point.co[2]))
                        vertices.append(world_co)
                    for point in spline.bezier_points:
                        world_co = matrix @ point.co
                        vertices.append(world_co)
        return vertices
    
    def snap_to_curves(self, context) -> Vector:
        """Try to snap to nearby curve vertices. Returns snapped point or None."""
        from bpy_extras import view3d_utils
        
        vertices = self.get_curve_vertices(context)
        if not vertices:
            return None
        
        best_vertex = None
        best_distance = SNAP_RADIUS
        
        for co in vertices:
            co2D = view3d_utils.location_3d_to_region_2d(self.region, self.region.data, co)
            if co2D is not None:
                distance = (co2D - self.mouse_pos).length
                if distance < best_distance:
                    best_vertex = co.copy()
                    best_distance = distance
        
        return best_vertex
    
    def get_snapped_position(self, context) -> Vector:
        """Get position, snapping to curves if possible."""
        from bpy_extras import view3d_utils
        
        snap = self.snap_to_curves(context)
        if snap:
            self.is_snapped = True
            # Store screen position for visual indicator
            screen_pos = view3d_utils.location_3d_to_region_2d(self.region, self.region.data, snap)
            self.snap_screen_pos = (screen_pos.x, screen_pos.y) if screen_pos else None
            return Vector((snap.x, snap.y, 0))
        
        self.is_snapped = False
        if self.hit_location:
            # Store screen position for visual indicator
            screen_pos = view3d_utils.location_3d_to_region_2d(self.region, self.region.data, self.hit_location)
            self.snap_screen_pos = (screen_pos.x, screen_pos.y) if screen_pos else None
            return Vector((self.hit_location.x, self.hit_location.y, 0))
        
        self.snap_screen_pos = None
        return Vector((0, 0, 0))
    
    def get_default_typing_target(self):
        return hb_placement.TypingTarget.LENGTH
    
    def on_typed_value_changed(self):
        if self.typed_value and self.polyline and self.point_count > 0:
            parsed = self.parse_typed_distance()
            if parsed is not None:
                self._update_preview_from_length(parsed)
        self.update_header(bpy.context)
    
    def apply_typed_value(self):
        parsed = self.parse_typed_distance()
        if parsed is not None and self.polyline and self.point_count > 0:
            self._update_preview_from_length(parsed)
            self._confirm_point()
        self.stop_typing()
    
    def _update_preview_from_length(self, length: float):
        """Update preview point based on typed length and current angle."""
        if self.current_point:
            end_x = self.current_point.x + math.cos(self.ortho_angle) * length
            end_y = self.current_point.y + math.sin(self.ortho_angle) * length
            end_point = Vector((end_x, end_y, 0))
            self._set_preview_point(end_point)
    
    def _set_preview_point(self, point: Vector):
        """Set the preview (last) point of the polyline."""
        if self.polyline and self.polyline.obj:
            spline = self.polyline.obj.data.splines[0]
            idx = len(spline.points) - 1
            spline.points[idx].co = (point.x, point.y, 0, 1)
    
    def _get_preview_point(self) -> Vector:
        """Get the current preview point position."""
        if self.polyline and self.polyline.obj:
            spline = self.polyline.obj.data.splines[0]
            idx = len(spline.points) - 1
            co = spline.points[idx].co
            return Vector((co[0], co[1], co[2]))
        return Vector((0, 0, 0))
    
    def _get_segment_length(self) -> float:
        """Get the length of the current segment (from last confirmed to preview)."""
        if self.current_point:
            preview = self._get_preview_point()
            return (preview - self.current_point).length
        return 0.0
    
    def create_polyline(self, context):
        """Create a new polyline object."""
        self.polyline = hb_details.GeoNodePolyline()
        self.polyline.create("Line")
        self.register_placement_object(self.polyline.obj)
        self.point_count = 0
        self.current_point = None
    
    def _update_from_mouse(self):
        """Update preview point based on mouse position."""
        from bpy_extras import view3d_utils
        
        if self.point_count == 0 or not self.hit_location:
            return
        
        # Check for snap first
        snap = self.snap_to_curves(bpy.context)
        if snap:
            self.is_snapped = True
            end_point = Vector((snap.x, snap.y, 0))
            # Store screen position for visual indicator
            screen_pos = view3d_utils.location_3d_to_region_2d(self.region, self.region.data, snap)
            self.snap_screen_pos = (screen_pos.x, screen_pos.y) if screen_pos else None
            # When snapped, skip ortho calculation
            if self.current_point:
                dx = end_point.x - self.current_point.x
                dy = end_point.y - self.current_point.y
                self.ortho_angle = math.atan2(dy, dx)
            self._set_preview_point(end_point)
            return
        
        self.is_snapped = False
        end_point = Vector(self.hit_location)
        end_point.z = 0  # Keep in XY plane
        
        # Store screen position for visual indicator (unsnapped)
        screen_pos = view3d_utils.location_3d_to_region_2d(self.region, self.region.data, end_point)
        self.snap_screen_pos = (screen_pos.x, screen_pos.y) if screen_pos else None
        
        if self.ortho_mode and self.current_point:
            # Calculate angle from last point to mouse
            dx = end_point.x - self.current_point.x
            dy = end_point.y - self.current_point.y
            
            if abs(dx) < 0.0001 and abs(dy) < 0.0001:
                return
            
            angle = math.atan2(dy, dx)
            
            # Snap to nearest 45 degrees
            snap_angle = round(math.degrees(angle) / 45) * 45
            self.ortho_angle = math.radians(snap_angle)
            
            # Calculate length
            length = math.sqrt(dx * dx + dy * dy)
            
            # Recalculate end point on snapped angle
            end_point.x = self.current_point.x + math.cos(self.ortho_angle) * length
            end_point.y = self.current_point.y + math.sin(self.ortho_angle) * length
            
            # Update screen position after ortho adjustment
            screen_pos = view3d_utils.location_3d_to_region_2d(self.region, self.region.data, end_point)
            self.snap_screen_pos = (screen_pos.x, screen_pos.y) if screen_pos else None
        else:
            # Free angle
            if self.current_point:
                dx = end_point.x - self.current_point.x
                dy = end_point.y - self.current_point.y
                self.ortho_angle = math.atan2(dy, dx)
        
        self._set_preview_point(end_point)
    
    def _confirm_point(self):
        """Confirm the current preview point and add a new preview point."""
        if self.polyline and self.polyline.obj:
            # The current preview point becomes confirmed
            self.current_point = self._get_preview_point().copy()
            self.point_count += 1
            
            # Add a new point for the next preview (starts at same position)
            self.polyline.add_point(self.current_point)
    
    def _remove_draw_handler(self):
        """Remove the draw handler."""
        if self._handle:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            self._handle = None
    
    def _finalize(self):
        """Finalize the polyline by removing the trailing preview point."""
        if self.polyline and self.polyline.obj and self.point_count > 0:
            spline = self.polyline.obj.data.splines[0]
            # If we have more points than confirmed, remove the preview
            if len(spline.points) > self.point_count:
                # Unfortunately Blender doesn't allow removing spline points directly
                # So we need to recreate the spline with fewer points
                points_data = [(p.co[0], p.co[1], p.co[2]) for p in spline.points[:self.point_count]]
                
                # Clear and recreate
                self.polyline.obj.data.splines.clear()
                new_spline = self.polyline.obj.data.splines.new('POLY')
                new_spline.points.add(len(points_data) - 1)
                for i, (x, y, z) in enumerate(points_data):
                    new_spline.points[i].co = (x, y, z, 1)
    
    def _remove_draw_handler(self):
        """Remove the draw handler."""
        if self._handle:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            self._handle = None
    
    def update_header(self, context):
        snap_text = " [SNAP]" if self.is_snapped else ""
        if self.placement_state == hb_placement.PlacementState.TYPING:
            text = f"Segment Length: {self.typed_value}_ | Enter to confirm | Esc to cancel typing"
        elif self.point_count > 0:
            length = self._get_segment_length()
            length_str = units.unit_to_string(context.scene.unit_settings, length)
            angle_deg = round(math.degrees(self.ortho_angle))
            mode = "Ortho (45°)" if self.ortho_mode else "Free"
            text = f"Length: {length_str} | Angle: {angle_deg}° | {mode}{snap_text} | Alt: toggle ortho | Type for exact | Right-click to finish"
        else:
            text = f"Click to place first point{snap_text} | Right-click/Esc to cancel"
        
        hb_placement.draw_header_text(context, text)
    
    def execute(self, context):
        # Initialize placement
        self.init_placement(context)
        
        # Reset state
        self.polyline = None
        self.current_point = None
        self.point_count = 0
        self.ortho_mode = True
        self.ortho_angle = 0.0
        self.is_snapped = False
        self.snap_screen_pos = None
        
        # Add draw handler for snap indicator
        args = (self, context)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(
            draw_snap_indicator, args, 'WINDOW', 'POST_PIXEL')
        
        # Create polyline
        self.create_polyline(context)
        
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
    
    def modal(self, context, event):
        context.window.cursor_set('CROSSHAIR')
        context.area.tag_redraw()
        
        if event.type == "INBETWEEN_MOUSEMOVE":
            return {'RUNNING_MODAL'}
        
        # Handle typing
        if self.handle_typing_event(event):
            self.update_header(context)
            return {'RUNNING_MODAL'}
        
        # Update snap
        if self.polyline and self.polyline.obj:
            self.polyline.obj.hide_set(True)
        self.update_snap(context, event)
        if self.polyline and self.polyline.obj:
            self.polyline.obj.hide_set(False)
        
        # Update preview point position
        if self.placement_state != hb_placement.PlacementState.TYPING:
            if self.point_count == 0:
                # Before first click, move the initial point to mouse (with snap)
                pos = self.get_snapped_position(context)  # This also updates snap_screen_pos
                self.polyline.set_point(0, pos)
            else:
                self._update_from_mouse()
        
        self.update_header(context)
        
        # Left click - place point
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if self.point_count == 0:
                # First point (with snap)
                start = self.get_snapped_position(context)
                self.polyline.set_point(0, start)
                self.current_point = start.copy()
                self.point_count = 1
                
                # Add preview point for next segment
                self.polyline.add_point(start)
            else:
                # Confirm current segment and add new preview
                self._confirm_point()
            return {'RUNNING_MODAL'}
        
        # Right click - finish
        if event.type == 'RIGHTMOUSE' and event.value == 'PRESS':
            self._remove_draw_handler()
            if self.point_count > 1:
                # Finalize and keep the polyline
                self._finalize()
                if self.polyline.obj in self.placement_objects:
                    self.placement_objects.remove(self.polyline.obj)
                hb_placement.clear_header_text(context)
                return {'FINISHED'}
            else:
                # Not enough points, cancel
                self.cancel_placement(context)
                hb_placement.clear_header_text(context)
                return {'CANCELLED'}
        
        # Escape - cancel everything
        if event.type == 'ESC' and event.value == 'PRESS':
            self._remove_draw_handler()
            self.cancel_placement(context)
            hb_placement.clear_header_text(context)
            return {'CANCELLED'}
        
        # Alt - toggle ortho mode
        if event.type == 'LEFT_ALT' and event.value == 'PRESS':
            self.ortho_mode = not self.ortho_mode
            self.update_header(context)
            return {'RUNNING_MODAL'}
        
        # Pass through navigation
        if hb_snap.event_is_pass_through(event):
            return {'PASS_THROUGH'}
        
        return {'RUNNING_MODAL'}


# =============================================================================
# DIMENSION OPERATOR (2D Detail specific)
# =============================================================================

class home_builder_details_OT_add_dimension(bpy.types.Operator, hb_placement.PlacementMixin):
    bl_idname = "home_builder_details.add_dimension"
    bl_label = "Add Dimension"
    bl_description = "Add a dimension annotation. Click two points, then set offset. Snaps to line vertices."
    bl_options = {'UNDO'}
    
    # Dimension state
    dim: hb_types.GeoNodeDimension = None
    first_point: Vector = None
    second_point: Vector = None
    click_count: int = 0
    
    # Snap indicator
    snap_point: Vector = None
    is_snapped: bool = False
    snap_screen_pos: tuple = None
    
    # Draw handler
    _handle = None
    
    def create_dimension(self, context):
        """Create dimension object."""
        self.dim = hb_types.GeoNodeDimension()
        self.dim.create("Dimension")
        self.dim.obj['IS_2D_ANNOTATION'] = True
        self.register_placement_object(self.dim.obj)
    
    def get_curve_vertices(self, context) -> list:
        """Get all curve vertices in the scene as world coordinates."""
        vertices = []
        for obj in context.scene.objects:
            if obj.type == 'CURVE' and obj != self.dim.obj:
                matrix = obj.matrix_world
                for spline in obj.data.splines:
                    for point in spline.points:
                        # Convert to world coordinates
                        world_co = matrix @ Vector((point.co[0], point.co[1], point.co[2]))
                        vertices.append(world_co)
                    # Also add bezier points if any
                    for point in spline.bezier_points:
                        world_co = matrix @ point.co
                        vertices.append(world_co)
        return vertices
    
    def snap_to_curves(self, context) -> Vector:
        """Try to snap to nearby curve vertices. Returns snapped point or None."""
        from bpy_extras import view3d_utils
        
        vertices = self.get_curve_vertices(context)
        if not vertices:
            return None
        
        best_vertex = None
        best_distance = SNAP_RADIUS
        
        for co in vertices:
            # Project vertex to 2D screen space
            co2D = view3d_utils.location_3d_to_region_2d(self.region, self.region.data, co)
            if co2D is not None:
                distance = (co2D - self.mouse_pos).length
                if distance < best_distance:
                    best_vertex = co.copy()
                    best_distance = distance
        
        return best_vertex
    
    def get_snapped_position(self, context) -> Vector:
        """Get position, snapping to curves if possible."""
        from bpy_extras import view3d_utils
        
        # First try curve snap
        snap = self.snap_to_curves(context)
        if snap:
            self.is_snapped = True
            self.snap_point = snap
            # Store screen position for visual indicator
            screen_pos = view3d_utils.location_3d_to_region_2d(self.region, self.region.data, snap)
            self.snap_screen_pos = (screen_pos.x, screen_pos.y) if screen_pos else None
            return Vector((snap.x, snap.y, 0))
        
        # Fall back to grid/raycast hit
        self.is_snapped = False
        self.snap_point = None
        if self.hit_location:
            # Store screen position for visual indicator
            screen_pos = view3d_utils.location_3d_to_region_2d(self.region, self.region.data, self.hit_location)
            self.snap_screen_pos = (screen_pos.x, screen_pos.y) if screen_pos else None
            return Vector((self.hit_location.x, self.hit_location.y, 0))
        
        self.snap_screen_pos = None
        return Vector((0, 0, 0))
    
    def _remove_draw_handler(self):
        """Remove the draw handler."""
        if self._handle:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            self._handle = None
    
    def update_header(self, context):
        snap_text = " [SNAP]" if self.is_snapped else ""
        if self.click_count == 0:
            text = f"Click first point{snap_text} | Right-click/Esc to cancel"
        elif self.click_count == 1:
            text = f"Click second point{snap_text} | Right-click/Esc to cancel"
        else:
            text = "Move to set offset, then click to place | Right-click/Esc to cancel"
        
        hb_placement.draw_header_text(context, text)
    
    def execute(self, context):
        self.init_placement(context)
        
        self.dim = None
        self.first_point = None
        self.second_point = None
        self.click_count = 0
        self.snap_point = None
        self.is_snapped = False
        self.snap_screen_pos = None
        
        # Add draw handler for snap indicator
        args = (self, context)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(
            draw_snap_indicator, args, 'WINDOW', 'POST_PIXEL')
        
        self.create_dimension(context)
        
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
    
    def modal(self, context, event):
        context.window.cursor_set('CROSSHAIR')
        context.area.tag_redraw()
        
        if event.type == "INBETWEEN_MOUSEMOVE":
            return {'RUNNING_MODAL'}
        
        # Update base snap (for grid/floor)
        if self.dim and self.dim.obj:
            self.dim.obj.hide_set(True)
        self.update_snap(context, event)
        if self.dim and self.dim.obj:
            self.dim.obj.hide_set(False)
        
        # Get position with curve snapping (only for first two clicks)
        if self.click_count < 2:
            hit = self.get_snapped_position(context)
        else:
            hit = Vector(self.hit_location) if self.hit_location else Vector((0, 0, 0))
            hit.z = 0
        
        # Update dimension based on state
        if self.click_count == 0:
            # Following mouse for first point
            self.dim.obj.location = hit
        elif self.click_count == 1:
            # Have first point, updating length
            dx = hit.x - self.first_point.x
            dy = hit.y - self.first_point.y
            length = math.sqrt(dx * dx + dy * dy)
            angle = math.atan2(dy, dx)
            
            self.dim.obj.rotation_euler.z = angle
            self.dim.obj.data.splines[0].points[1].co = (length, 0, 0, 1)
        elif self.click_count == 2:
            # Have both points, setting offset
            # Calculate perpendicular distance from hit to line
            line_vec = self.second_point - self.first_point
            line_len = line_vec.length
            if line_len > 0.0001:
                line_dir = line_vec.normalized()
                to_hit = hit - self.first_point
                
                # Project to get perpendicular distance
                parallel = to_hit.dot(line_dir)
                perp = to_hit - line_dir * parallel
                offset = perp.length
                
                # Determine sign based on which side of line
                # Cross product Z component: positive = left side, negative = right side
                cross = line_dir.x * to_hit.y - line_dir.y * to_hit.x
                if cross < 0:
                    offset = -offset
                
                # Allow negative leader length for dimensions on either side
                self.dim.set_input("Leader Length", offset)
        
        self.update_header(context)
        
        # Left click
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if self.click_count == 0:
                self.first_point = hit.copy()
                self.dim.obj.location = self.first_point
                self.click_count = 1
            elif self.click_count == 1:
                self.second_point = hit.copy()
                self.click_count = 2
            else:
                # Confirm dimension
                self._remove_draw_handler()
                if self.dim.obj in self.placement_objects:
                    self.placement_objects.remove(self.dim.obj)
                hb_placement.clear_header_text(context)
                return {'FINISHED'}
            return {'RUNNING_MODAL'}
        
        # Right click / Escape - cancel
        if event.type in {'RIGHTMOUSE', 'ESC'} and event.value == 'PRESS':
            self._remove_draw_handler()
            self.cancel_placement(context)
            hb_placement.clear_header_text(context)
            return {'CANCELLED'}
        
        if hb_snap.event_is_pass_through(event):
            return {'PASS_THROUGH'}
        
        return {'RUNNING_MODAL'}


# =============================================================================
# REGISTRATION
# =============================================================================

classes = (
    home_builder_details_OT_create_detail,
    home_builder_details_OT_delete_detail,
    home_builder_details_OT_draw_line,
    home_builder_details_OT_add_dimension,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
