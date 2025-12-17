import bpy
import math
from mathutils import Vector
from .. import hb_details
from .. import hb_types
from .. import hb_snap
from .. import hb_placement
from .. import hb_detail_library
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
    bl_description = "Draw a 2D polyline. Click to place points, type for exact length. Snaps to vertices and perpendicular points."
    bl_options = {'UNDO'}
    
    # Polyline state
    polyline: hb_details.GeoNodePolyline = None
    current_point: Vector = None  # The last confirmed point
    point_count: int = 0  # Number of confirmed points
    
    # Ortho mode (snap to 0, 45, 90 degree angles)
    ortho_mode: bool = True
    ortho_angle: float = 0.0
    
    # Angle lock state
    angle_locked: bool = False  # When True, line angle is locked
    locked_angle: float = 0.0  # The locked angle value
    
    # Tracking state (extend line to align with snap point's X or Y)
    tracking_point: Vector = None  # The reference point we're tracking to
    is_tracking: bool = False  # True when extending to align with a tracked point
    
    # Snap state
    is_snapped: bool = False
    is_perp_snap: bool = False  # True when snapped to perpendicular foot
    snap_screen_pos: tuple = None
    
    # Draw handler
    _handle = None
    
    def get_curve_vertices(self, context) -> list:
        """Get all curve vertices in the scene as world coordinates."""
        vertices = []
        
        # Add vertices from all curves (excluding current rectangle being drawn)
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
    
    def get_curve_segments(self, context) -> list:
        """Get all curve segments as (start, end) tuples."""
        segments = []
        
        # Add segments from all curves (excluding current rectangle being drawn)
        for obj in context.scene.objects:
            if obj.type == 'CURVE' and (not self.polyline or obj != self.polyline.obj):
                matrix = obj.matrix_world
                for spline in obj.data.splines:
                    points = spline.points
                    num_pts = len(points)
                    for i in range(num_pts - 1):
                        p1 = matrix @ Vector((points[i].co[0], points[i].co[1], points[i].co[2]))
                        p2 = matrix @ Vector((points[i+1].co[0], points[i+1].co[1], points[i+1].co[2]))
                        segments.append((Vector((p1.x, p1.y, 0)), Vector((p2.x, p2.y, 0))))
                    
                    # If cyclic, add closing segment
                    if spline.use_cyclic_u and num_pts > 1:
                        p1 = matrix @ Vector((points[-1].co[0], points[-1].co[1], points[-1].co[2]))
                        p2 = matrix @ Vector((points[0].co[0], points[0].co[1], points[0].co[2]))
                        segments.append((Vector((p1.x, p1.y, 0)), Vector((p2.x, p2.y, 0))))
        
        return segments
    
    def get_perpendicular_foot(self, point: Vector, seg_start: Vector, seg_end: Vector) -> tuple:
        """
        Calculate the perpendicular foot from a point to a line segment.
        Returns (foot_point, distance, t) where t is the parameter along the segment (0-1).
        Returns None if the foot is outside the segment.
        """
        seg_vec = seg_end - seg_start
        seg_len_sq = seg_vec.length_squared
        
        if seg_len_sq < 0.00001:
            return None
        
        # Calculate parameter t
        t = (point - seg_start).dot(seg_vec) / seg_len_sq
        
        # Check if foot is within segment (with small tolerance)
        if t < -0.01 or t > 1.01:
            return None
        
        # Clamp t to segment
        t = max(0, min(1, t))
        
        # Calculate foot point
        foot = seg_start + seg_vec * t
        distance = (point - foot).length
        
        return (foot, distance, t)
    
    def find_nearest_perp_snap(self, context, point: Vector) -> tuple:
        """
        Find the nearest perpendicular foot point on any segment.
        Returns (foot_point, segment) or (None, None) if none found within snap radius.
        """
        from bpy_extras import view3d_utils
        
        segments = self.get_curve_segments(context)
        if not segments:
            return (None, None)
        
        best_foot = None
        best_segment = None
        best_screen_dist = SNAP_RADIUS
        
        for seg_start, seg_end in segments:
            result = self.get_perpendicular_foot(point, seg_start, seg_end)
            if result:
                foot, _, t = result
                
                # Skip if foot is at the segment endpoints (we snap to vertices for those)
                if t < 0.05 or t > 0.95:
                    continue
                
                # Check screen distance
                foot_2d = view3d_utils.location_3d_to_region_2d(self.region, self.region.data, foot)
                if foot_2d:
                    screen_dist = (foot_2d - self.mouse_pos).length
                    if screen_dist < best_screen_dist:
                        best_screen_dist = screen_dist
                        best_foot = foot
                        best_segment = (seg_start, seg_end)
        
        return (best_foot, best_segment)
    
    def find_nearest_segment_angle(self, context) -> float:
        """
        Find the angle of the nearest line segment for perpendicular constraint.
        Returns the perpendicular angle (segment angle + 90 degrees).
        """
        from bpy_extras import view3d_utils
        
        if not self.hit_location:
            return 0.0
        
        point = Vector((self.hit_location.x, self.hit_location.y, 0))
        segments = self.get_curve_segments(context)
        
        if not segments:
            return 0.0
        
        best_segment = None
        best_dist = float('inf')
        
        for seg_start, seg_end in segments:
            # Get distance from point to segment
            result = self.get_perpendicular_foot(point, seg_start, seg_end)
            if result:
                _, dist, _ = result
                if dist < best_dist:
                    best_dist = dist
                    best_segment = (seg_start, seg_end)
            else:
                # Point is outside segment, use distance to nearest endpoint
                dist1 = (point - seg_start).length
                dist2 = (point - seg_end).length
                dist = min(dist1, dist2)
                if dist < best_dist:
                    best_dist = dist
                    best_segment = (seg_start, seg_end)
        
        if best_segment:
            seg_vec = best_segment[1] - best_segment[0]
            seg_angle = math.atan2(seg_vec.y, seg_vec.x)
            # Return perpendicular angle
            return seg_angle + math.pi / 2
        
        return 0.0
    
    def find_tracking_point(self, context) -> Vector:
        """
        Find the nearest vertex for tracking (extension alignment).
        Returns the point or None if none nearby.
        """
        from bpy_extras import view3d_utils
        
        vertices = self.get_curve_vertices(context)
        if not vertices:
            return None
        
        # Use a larger radius for tracking detection
        TRACKING_RADIUS = SNAP_RADIUS * 2
        
        best_vertex = None
        best_distance = TRACKING_RADIUS
        
        for co in vertices:
            co2D = view3d_utils.location_3d_to_region_2d(self.region, self.region.data, co)
            if co2D is not None:
                distance = (co2D - self.mouse_pos).length
                if distance < best_distance:
                    best_vertex = co.copy()
                    best_distance = distance
        
        return best_vertex
    
    def calculate_tracking_intersection(self, ref_point: Vector) -> Vector:
        """
        Calculate where the current line (at ortho_angle from current_point) 
        intersects with a horizontal or vertical line through ref_point.
        Returns the intersection point.
        """
        if not self.current_point:
            return None
        
        cos_a = math.cos(self.ortho_angle)
        sin_a = math.sin(self.ortho_angle)
        
        x0, y0 = self.current_point.x, self.current_point.y
        rx, ry = ref_point.x, ref_point.y
        
        # Determine which alignment to use based on angle
        # Horizontal-ish angles (0°, 180°) -> align X
        # Vertical-ish angles (90°, 270°) -> align Y
        # Diagonal angles -> choose based on which gives forward progress
        
        angle_deg = math.degrees(self.ortho_angle) % 360
        
        t_x = None  # Parameter for X alignment
        t_y = None  # Parameter for Y alignment
        
        # Calculate t for X alignment (vertical line through ref_point)
        if abs(cos_a) > 0.001:
            t_x = (rx - x0) / cos_a
        
        # Calculate t for Y alignment (horizontal line through ref_point)
        if abs(sin_a) > 0.001:
            t_y = (ry - y0) / sin_a
        
        # Choose the appropriate t based on angle
        t = None
        
        if t_x is not None and t_y is not None:
            # Both are valid - choose based on angle
            # For mostly horizontal (within 45° of horizontal), prefer X alignment
            # For mostly vertical (within 45° of vertical), prefer Y alignment
            if abs(cos_a) > abs(sin_a):
                t = t_x if t_x > 0 else t_y
            else:
                t = t_y if t_y > 0 else t_x
        elif t_x is not None:
            t = t_x
        elif t_y is not None:
            t = t_y
        
        if t is not None and t > 0:
            # Calculate intersection point
            ix = x0 + t * cos_a
            iy = y0 + t * sin_a
            return Vector((ix, iy, 0))
        
        return None
    
    def project_to_snap_point(self, snap_point: Vector) -> Vector:
        """
        Project along locked angle to align with snap point's X or Y coordinate.
        Returns the projected point on the locked angle line.
        """
        if not self.current_point:
            return None
        
        cos_a = math.cos(self.locked_angle)
        sin_a = math.sin(self.locked_angle)
        
        x0, y0 = self.current_point.x, self.current_point.y
        sx, sy = snap_point.x, snap_point.y
        
        # Calculate t for X alignment (where line crosses x = sx)
        t_x = None
        if abs(cos_a) > 0.001:
            t_x = (sx - x0) / cos_a
        
        # Calculate t for Y alignment (where line crosses y = sy)
        t_y = None
        if abs(sin_a) > 0.001:
            t_y = (sy - y0) / sin_a
        
        # Choose which alignment based on angle
        # Mostly horizontal -> use X alignment
        # Mostly vertical -> use Y alignment
        t = None
        if abs(cos_a) > abs(sin_a):
            # Mostly horizontal - align X
            t = t_x
        else:
            # Mostly vertical - align Y
            t = t_y
        
        if t is not None:
            ix = x0 + t * cos_a
            iy = y0 + t * sin_a
            return Vector((ix, iy, 0))
        
        return None
    
    def snap_to_curves(self, context) -> Vector:
        """Try to snap to nearby curve vertices or perpendicular foot points. Returns snapped point or None."""
        from bpy_extras import view3d_utils
        
        best_point = None
        best_distance = SNAP_RADIUS
        self.is_perp_snap = False
        
        # First check vertex snaps (higher priority)
        vertices = self.get_curve_vertices(context)
        for co in vertices:
            co2D = view3d_utils.location_3d_to_region_2d(self.region, self.region.data, co)
            if co2D is not None:
                distance = (co2D - self.mouse_pos).length
                if distance < best_distance:
                    best_point = co.copy()
                    best_distance = distance
                    self.is_perp_snap = False
        
        # Then check perpendicular foot snaps (only if no vertex snap or perp is closer)
        if self.hit_location:
            point = Vector((self.hit_location.x, self.hit_location.y, 0))
            perp_foot, perp_segment = self.find_nearest_perp_snap(context, point)
            
            if perp_foot:
                foot_2d = view3d_utils.location_3d_to_region_2d(self.region, self.region.data, perp_foot)
                if foot_2d:
                    distance = (foot_2d - self.mouse_pos).length
                    if distance < best_distance:
                        best_point = perp_foot.copy()
                        best_distance = distance
                        self.is_perp_snap = True
        
        return best_point
    
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
        self.is_perp_snap = False
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
        
        # Apply annotation settings from scene
        hb_scene = context.scene.home_builder
        self.polyline.obj.data.bevel_depth = hb_scene.annotation_line_thickness
        color = tuple(hb_scene.annotation_line_color) + (1.0,)
        self.polyline.obj.color = color
        if self.polyline.obj.data.materials:
            mat = self.polyline.obj.data.materials[0]
            if mat and mat.use_nodes:
                bsdf = mat.node_tree.nodes.get("Principled BSDF")
                if bsdf:
                    bsdf.inputs["Base Color"].default_value = color
        
        self.register_placement_object(self.polyline.obj)
        self.point_count = 0
        self.current_point = None
    
    def _update_from_mouse(self):
        """Update preview point based on mouse position."""
        from bpy_extras import view3d_utils
        
        if self.point_count == 0 or not self.hit_location:
            return
        
        # Reset tracking state
        self.is_tracking = False
        self.tracking_point = None
        
        # When angle is locked, check for snap points and project along locked angle
        if self.angle_locked and self.current_point:
            snap = self.snap_to_curves(bpy.context)
            if snap:
                # Project along locked angle to align with snap point
                snap_point = Vector((snap.x, snap.y, 0))
                projected = self.project_to_snap_point(snap_point)
                if projected:
                    self.is_snapped = True
                    self.is_tracking = True
                    self.tracking_point = snap_point.copy()
                    screen_pos = view3d_utils.location_3d_to_region_2d(self.region, self.region.data, projected)
                    self.snap_screen_pos = (screen_pos.x, screen_pos.y) if screen_pos else None
                    self._set_preview_point(projected)
                    return
            
            # No snap - just extend along locked angle based on mouse distance
            self.is_snapped = False
            end_point = Vector(self.hit_location)
            end_point.z = 0
            
            dx = end_point.x - self.current_point.x
            dy = end_point.y - self.current_point.y
            
            # Project mouse position onto locked angle direction
            cos_a = math.cos(self.locked_angle)
            sin_a = math.sin(self.locked_angle)
            
            # Dot product gives length along locked direction
            length = dx * cos_a + dy * sin_a
            
            end_point.x = self.current_point.x + cos_a * length
            end_point.y = self.current_point.y + sin_a * length
            
            screen_pos = view3d_utils.location_3d_to_region_2d(self.region, self.region.data, end_point)
            self.snap_screen_pos = (screen_pos.x, screen_pos.y) if screen_pos else None
            self._set_preview_point(end_point)
            return
        
        # Normal behavior (not locked)
        # Check for direct vertex snap first (highest priority)
        snap = self.snap_to_curves(bpy.context)
        if snap:
            self.is_snapped = True
            end_point = Vector((snap.x, snap.y, 0))
            screen_pos = view3d_utils.location_3d_to_region_2d(self.region, self.region.data, snap)
            self.snap_screen_pos = (screen_pos.x, screen_pos.y) if screen_pos else None
            if self.current_point:
                dx = end_point.x - self.current_point.x
                dy = end_point.y - self.current_point.y
                self.ortho_angle = math.atan2(dy, dx)
            self._set_preview_point(end_point)
            return
        
        self.is_snapped = False
        self.is_perp_snap = False
        end_point = Vector(self.hit_location)
        end_point.z = 0
        
        if self.current_point:
            dx = end_point.x - self.current_point.x
            dy = end_point.y - self.current_point.y
            
            if abs(dx) < 0.0001 and abs(dy) < 0.0001:
                return
            
            length = math.sqrt(dx * dx + dy * dy)
            
            if self.ortho_mode:
                # Snap to nearest 45 degrees
                angle = math.atan2(dy, dx)
                snap_angle = round(math.degrees(angle) / 45) * 45
                self.ortho_angle = math.radians(snap_angle)
                
                # Recalculate end point on snapped angle
                end_point.x = self.current_point.x + math.cos(self.ortho_angle) * length
                end_point.y = self.current_point.y + math.sin(self.ortho_angle) * length
            else:
                # Free angle
                self.ortho_angle = math.atan2(dy, dx)
            
            # Update screen position
            screen_pos = view3d_utils.location_3d_to_region_2d(self.region, self.region.data, end_point)
            self.snap_screen_pos = (screen_pos.x, screen_pos.y) if screen_pos else None
        
        self._set_preview_point(end_point)
    
    def _confirm_point(self):
        """Confirm the current preview point and add a new preview point."""
        if self.polyline and self.polyline.obj:
            # The current preview point becomes confirmed
            self.current_point = self._get_preview_point().copy()
            self.point_count += 1
            
            # Unlock angle after placing point
            self.angle_locked = False
            
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
        # Build snap indicator text
        if self.is_tracking and self.angle_locked:
            snap_text = " [LOCK+SNAP]"
        elif self.angle_locked:
            snap_text = " [LOCK]"
        elif self.is_perp_snap:
            snap_text = " [PERP]"
        elif self.is_snapped:
            snap_text = " [SNAP]"
        else:
            snap_text = ""
        
        if self.placement_state == hb_placement.PlacementState.TYPING:
            text = f"Segment Length: {self.typed_value}_ | Enter to confirm | Esc to cancel typing"
        elif self.point_count > 0:
            length = self._get_segment_length()
            length_str = units.unit_to_string(context.scene.unit_settings, length)
            
            # Show locked angle or current angle
            if self.angle_locked:
                angle_deg = round(math.degrees(self.locked_angle))
            else:
                angle_deg = round(math.degrees(self.ortho_angle))
            
            mode = "Ortho" if self.ortho_mode else "Free"
            
            close_text = " | C: close" if self.point_count >= 2 else ""
            lock_hint = "L: unlock" if self.angle_locked else "L: lock"
            text = f"Length: {length_str} | {angle_deg}° | {mode}{snap_text} | {lock_hint}{close_text} | Right-click: finish"
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
        self.angle_locked = False
        self.locked_angle = 0.0
        self.tracking_point = None
        self.is_tracking = False
        self.is_snapped = False
        self.is_perp_snap = False
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
        
        # C key - close the shape
        if event.type == 'C' and event.value == 'PRESS':
            if self.point_count >= 2:
                # Need at least 2 points to close
                self._remove_draw_handler()
                self._finalize()
                
                # Close the polyline
                if self.polyline and self.polyline.obj:
                    self.polyline.obj.data.splines[0].use_cyclic_u = True
                
                if self.polyline.obj in self.placement_objects:
                    self.placement_objects.remove(self.polyline.obj)
                hb_placement.clear_header_text(context)
                return {'FINISHED'}
            return {'RUNNING_MODAL'}
        
        # Escape - cancel everything
        if event.type == 'ESC' and event.value == 'PRESS':
            self._remove_draw_handler()
            self.cancel_placement(context)
            hb_placement.clear_header_text(context)
            return {'CANCELLED'}
        
        # Alt - toggle ortho mode
        if event.type == 'LEFT_ALT' and event.value == 'PRESS':
            self.ortho_mode = not self.ortho_mode
            self.angle_locked = False  # Unlock when toggling ortho
            self.update_header(context)
            return {'RUNNING_MODAL'}
        
        # L - lock/unlock angle
        if event.type == 'L' and event.value == 'PRESS':
            if self.point_count > 0:
                if self.angle_locked:
                    # Unlock
                    self.angle_locked = False
                else:
                    # Lock current angle
                    self.locked_angle = self.ortho_angle
                    self.angle_locked = True
                self.update_header(context)
            return {'RUNNING_MODAL'}
        
        # Pass through navigation
        if hb_snap.event_is_pass_through(event):
            return {'PASS_THROUGH'}
        
        return {'RUNNING_MODAL'}


# =============================================================================
# RECTANGLE DRAWING OPERATOR
# =============================================================================

class home_builder_details_OT_draw_rectangle(bpy.types.Operator, hb_placement.PlacementMixin):
    bl_idname = "home_builder_details.draw_rectangle"
    bl_label = "Draw Rectangle"
    bl_description = "Draw a rectangle by clicking two corners or typing dimensions. Snaps to existing vertices."
    bl_options = {'UNDO'}
    
    # Rectangle state
    polyline: hb_details.GeoNodePolyline = None
    first_corner: Vector = None
    has_first_corner: bool = False
    
    # Typed dimensions
    typed_width: str = ""
    typed_height: str = ""
    typing_width: bool = False  # True = typing width, False = typing height
    is_typing: bool = False
    
    # Current dimensions (for display and rectangle update)
    current_width: float = 0.0
    current_height: float = 0.0
    
    # Snap state
    is_snapped: bool = False
    snap_screen_pos: tuple = None
    
    # Draw handler
    _handle = None
    
    def get_curve_vertices(self, context) -> list:
        """Get all curve vertices in the scene as world coordinates."""
        vertices = []
        
        # Add vertices from all curves (excluding current rectangle being drawn)
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
    
    def get_curve_segments(self, context) -> list:
        """Get all curve segments as (start, end) tuples."""
        segments = []
        
        # Add segments from all curves (excluding current rectangle being drawn)
        for obj in context.scene.objects:
            if obj.type == 'CURVE' and (not self.polyline or obj != self.polyline.obj):
                matrix = obj.matrix_world
                for spline in obj.data.splines:
                    points = spline.points
                    num_pts = len(points)
                    for i in range(num_pts - 1):
                        p1 = matrix @ Vector((points[i].co[0], points[i].co[1], points[i].co[2]))
                        p2 = matrix @ Vector((points[i+1].co[0], points[i+1].co[1], points[i+1].co[2]))
                        segments.append((Vector((p1.x, p1.y, 0)), Vector((p2.x, p2.y, 0))))
                    
                    # If cyclic, add closing segment
                    if spline.use_cyclic_u and num_pts > 1:
                        p1 = matrix @ Vector((points[-1].co[0], points[-1].co[1], points[-1].co[2]))
                        p2 = matrix @ Vector((points[0].co[0], points[0].co[1], points[0].co[2]))
                        segments.append((Vector((p1.x, p1.y, 0)), Vector((p2.x, p2.y, 0))))
        
        return segments
    
    def get_perpendicular_foot(self, point: Vector, seg_start: Vector, seg_end: Vector) -> tuple:
        """
        Calculate the perpendicular foot from a point to a line segment.
        Returns (foot_point, distance, t) where t is the parameter along the segment (0-1).
        Returns None if the foot is outside the segment.
        """
        seg_vec = seg_end - seg_start
        seg_len_sq = seg_vec.length_squared
        
        if seg_len_sq < 0.00001:
            return None
        
        # Calculate parameter t
        t = (point - seg_start).dot(seg_vec) / seg_len_sq
        
        # Check if foot is within segment (with small tolerance)
        if t < -0.01 or t > 1.01:
            return None
        
        # Clamp t to segment
        t = max(0, min(1, t))
        
        # Calculate foot point
        foot = seg_start + seg_vec * t
        distance = (point - foot).length
        
        return (foot, distance, t)
    
    def find_nearest_perp_snap(self, context, point: Vector) -> tuple:
        """
        Find the nearest perpendicular foot point on any segment.
        Returns (foot_point, segment) or (None, None) if none found within snap radius.
        """
        from bpy_extras import view3d_utils
        
        segments = self.get_curve_segments(context)
        if not segments:
            return (None, None)
        
        best_foot = None
        best_segment = None
        best_screen_dist = SNAP_RADIUS
        
        for seg_start, seg_end in segments:
            result = self.get_perpendicular_foot(point, seg_start, seg_end)
            if result:
                foot, _, t = result
                
                # Skip if foot is at the segment endpoints (we snap to vertices for those)
                if t < 0.05 or t > 0.95:
                    continue
                
                # Check screen distance
                foot_2d = view3d_utils.location_3d_to_region_2d(self.region, self.region.data, foot)
                if foot_2d:
                    screen_dist = (foot_2d - self.mouse_pos).length
                    if screen_dist < best_screen_dist:
                        best_screen_dist = screen_dist
                        best_foot = foot
                        best_segment = (seg_start, seg_end)
        
        return (best_foot, best_segment)
    
    def find_nearest_segment_angle(self, context) -> float:
        """
        Find the angle of the nearest line segment for perpendicular constraint.
        Returns the perpendicular angle (segment angle + 90 degrees).
        """
        from bpy_extras import view3d_utils
        
        if not self.hit_location:
            return 0.0
        
        point = Vector((self.hit_location.x, self.hit_location.y, 0))
        segments = self.get_curve_segments(context)
        
        if not segments:
            return 0.0
        
        best_segment = None
        best_dist = float('inf')
        
        for seg_start, seg_end in segments:
            # Get distance from point to segment
            result = self.get_perpendicular_foot(point, seg_start, seg_end)
            if result:
                _, dist, _ = result
                if dist < best_dist:
                    best_dist = dist
                    best_segment = (seg_start, seg_end)
            else:
                # Point is outside segment, use distance to nearest endpoint
                dist1 = (point - seg_start).length
                dist2 = (point - seg_end).length
                dist = min(dist1, dist2)
                if dist < best_dist:
                    best_dist = dist
                    best_segment = (seg_start, seg_end)
        
        if best_segment:
            seg_vec = best_segment[1] - best_segment[0]
            seg_angle = math.atan2(seg_vec.y, seg_vec.x)
            # Return perpendicular angle
            return seg_angle + math.pi / 2
        
        return 0.0
    
    def find_tracking_point(self, context) -> Vector:
        """
        Find the nearest vertex for tracking (extension alignment).
        Returns the point or None if none nearby.
        """
        from bpy_extras import view3d_utils
        
        vertices = self.get_curve_vertices(context)
        if not vertices:
            return None
        
        # Use a larger radius for tracking detection
        TRACKING_RADIUS = SNAP_RADIUS * 2
        
        best_vertex = None
        best_distance = TRACKING_RADIUS
        
        for co in vertices:
            co2D = view3d_utils.location_3d_to_region_2d(self.region, self.region.data, co)
            if co2D is not None:
                distance = (co2D - self.mouse_pos).length
                if distance < best_distance:
                    best_vertex = co.copy()
                    best_distance = distance
        
        return best_vertex
    
    def calculate_tracking_intersection(self, ref_point: Vector) -> Vector:
        """
        Calculate where the current line (at ortho_angle from current_point) 
        intersects with a horizontal or vertical line through ref_point.
        Returns the intersection point.
        """
        if not self.current_point:
            return None
        
        cos_a = math.cos(self.ortho_angle)
        sin_a = math.sin(self.ortho_angle)
        
        x0, y0 = self.current_point.x, self.current_point.y
        rx, ry = ref_point.x, ref_point.y
        
        # Determine which alignment to use based on angle
        # Horizontal-ish angles (0°, 180°) -> align X
        # Vertical-ish angles (90°, 270°) -> align Y
        # Diagonal angles -> choose based on which gives forward progress
        
        angle_deg = math.degrees(self.ortho_angle) % 360
        
        t_x = None  # Parameter for X alignment
        t_y = None  # Parameter for Y alignment
        
        # Calculate t for X alignment (vertical line through ref_point)
        if abs(cos_a) > 0.001:
            t_x = (rx - x0) / cos_a
        
        # Calculate t for Y alignment (horizontal line through ref_point)
        if abs(sin_a) > 0.001:
            t_y = (ry - y0) / sin_a
        
        # Choose the appropriate t based on angle
        t = None
        
        if t_x is not None and t_y is not None:
            # Both are valid - choose based on angle
            # For mostly horizontal (within 45° of horizontal), prefer X alignment
            # For mostly vertical (within 45° of vertical), prefer Y alignment
            if abs(cos_a) > abs(sin_a):
                t = t_x if t_x > 0 else t_y
            else:
                t = t_y if t_y > 0 else t_x
        elif t_x is not None:
            t = t_x
        elif t_y is not None:
            t = t_y
        
        if t is not None and t > 0:
            # Calculate intersection point
            ix = x0 + t * cos_a
            iy = y0 + t * sin_a
            return Vector((ix, iy, 0))
        
        return None
    
    def project_to_snap_point(self, snap_point: Vector) -> Vector:
        """
        Project along locked angle to align with snap point's X or Y coordinate.
        Returns the projected point on the locked angle line.
        """
        if not self.current_point:
            return None
        
        cos_a = math.cos(self.locked_angle)
        sin_a = math.sin(self.locked_angle)
        
        x0, y0 = self.current_point.x, self.current_point.y
        sx, sy = snap_point.x, snap_point.y
        
        # Calculate t for X alignment (where line crosses x = sx)
        t_x = None
        if abs(cos_a) > 0.001:
            t_x = (sx - x0) / cos_a
        
        # Calculate t for Y alignment (where line crosses y = sy)
        t_y = None
        if abs(sin_a) > 0.001:
            t_y = (sy - y0) / sin_a
        
        # Choose which alignment based on angle
        # Mostly horizontal -> use X alignment
        # Mostly vertical -> use Y alignment
        t = None
        if abs(cos_a) > abs(sin_a):
            # Mostly horizontal - align X
            t = t_x
        else:
            # Mostly vertical - align Y
            t = t_y
        
        if t is not None:
            ix = x0 + t * cos_a
            iy = y0 + t * sin_a
            return Vector((ix, iy, 0))
        
        return None
    
    def snap_to_curves(self, context) -> Vector:
        """Try to snap to nearby curve vertices or perpendicular foot points. Returns snapped point or None."""
        from bpy_extras import view3d_utils
        
        best_point = None
        best_distance = SNAP_RADIUS
        self.is_perp_snap = False
        
        # First check vertex snaps (higher priority)
        vertices = self.get_curve_vertices(context)
        for co in vertices:
            co2D = view3d_utils.location_3d_to_region_2d(self.region, self.region.data, co)
            if co2D is not None:
                distance = (co2D - self.mouse_pos).length
                if distance < best_distance:
                    best_point = co.copy()
                    best_distance = distance
                    self.is_perp_snap = False
        
        # Then check perpendicular foot snaps (only if no vertex snap or perp is closer)
        if self.hit_location:
            point = Vector((self.hit_location.x, self.hit_location.y, 0))
            perp_foot, perp_segment = self.find_nearest_perp_snap(context, point)
            
            if perp_foot:
                foot_2d = view3d_utils.location_3d_to_region_2d(self.region, self.region.data, perp_foot)
                if foot_2d:
                    distance = (foot_2d - self.mouse_pos).length
                    if distance < best_distance:
                        best_point = perp_foot.copy()
                        best_distance = distance
                        self.is_perp_snap = True
        
        return best_point
    
    def get_snapped_position(self, context) -> Vector:
        """Get position, snapping to curves if possible."""
        from bpy_extras import view3d_utils
        
        snap = self.snap_to_curves(context)
        if snap:
            self.is_snapped = True
            screen_pos = view3d_utils.location_3d_to_region_2d(self.region, self.region.data, snap)
            self.snap_screen_pos = (screen_pos.x, screen_pos.y) if screen_pos else None
            return Vector((snap.x, snap.y, 0))
        
        self.is_snapped = False
        if self.hit_location:
            screen_pos = view3d_utils.location_3d_to_region_2d(self.region, self.region.data, self.hit_location)
            self.snap_screen_pos = (screen_pos.x, screen_pos.y) if screen_pos else None
            return Vector((self.hit_location.x, self.hit_location.y, 0))
        
        self.snap_screen_pos = None
        return Vector((0, 0, 0))
    
    def create_rectangle(self, context):
        """Create a new rectangle polyline object."""
        self.polyline = hb_details.GeoNodePolyline()
        self.polyline.create("Rectangle")
        
        # Apply annotation settings from scene
        hb_scene = context.scene.home_builder
        self.polyline.obj.data.bevel_depth = hb_scene.annotation_line_thickness
        color = tuple(hb_scene.annotation_line_color) + (1.0,)
        self.polyline.obj.color = color
        if self.polyline.obj.data.materials:
            mat = self.polyline.obj.data.materials[0]
            if mat and mat.use_nodes:
                bsdf = mat.node_tree.nodes.get("Principled BSDF")
                if bsdf:
                    bsdf.inputs["Base Color"].default_value = color
        
        self.register_placement_object(self.polyline.obj)
        
        # Add 3 more points (total 4 for rectangle)
        self.polyline.add_point(Vector((0, 0, 0)))
        self.polyline.add_point(Vector((0, 0, 0)))
        self.polyline.add_point(Vector((0, 0, 0)))
        
        # Close the rectangle
        self.polyline.close()
    
    def update_rectangle_from_corners(self, second_corner: Vector):
        """Update rectangle points based on two corners."""
        if not self.first_corner or not self.polyline:
            return
        
        x1, y1 = self.first_corner.x, self.first_corner.y
        x2, y2 = second_corner.x, second_corner.y
        
        # Store current dimensions
        self.current_width = abs(x2 - x1)
        self.current_height = abs(y2 - y1)
        
        # Set the 4 corners (counter-clockwise from first corner)
        self.polyline.set_point(0, Vector((x1, y1, 0)))  # First corner
        self.polyline.set_point(1, Vector((x2, y1, 0)))  # Bottom-right
        self.polyline.set_point(2, Vector((x2, y2, 0)))  # Second corner (opposite)
        self.polyline.set_point(3, Vector((x1, y2, 0)))  # Top-left
    
    def update_rectangle_from_dimensions(self, width: float, height: float):
        """Update rectangle based on typed dimensions."""
        if not self.first_corner or not self.polyline:
            return
        
        x1, y1 = self.first_corner.x, self.first_corner.y
        x2 = x1 + width
        y2 = y1 + height
        
        self.current_width = width
        self.current_height = height
        
        # Set the 4 corners
        self.polyline.set_point(0, Vector((x1, y1, 0)))
        self.polyline.set_point(1, Vector((x2, y1, 0)))
        self.polyline.set_point(2, Vector((x2, y2, 0)))
        self.polyline.set_point(3, Vector((x1, y2, 0)))
    
    def parse_dimension(self, value_str: str) -> float:
        """Parse a typed dimension string to meters. Returns 0.0 if parsing fails."""
        if not value_str:
            return 0.0
        result = self.parse_typed_distance(value_str)
        return result if result is not None else 0.0
    
    def _remove_draw_handler(self):
        """Remove the draw handler."""
        if self._handle:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            self._handle = None
    
    def update_header(self, context):
        snap_text = " [SNAP]" if self.is_snapped else ""
        
        if not self.has_first_corner:
            text = f"Click first corner{snap_text} | Right-click/Esc to cancel"
        elif self.is_typing:
            if self.typing_width:
                text = f"Width: {self.typed_width}_ | Tab for height | Enter to confirm | Esc to cancel"
            else:
                width_str = units.unit_to_string(context.scene.unit_settings, self.parse_dimension(self.typed_width) or self.current_width)
                text = f"Width: {width_str} | Height: {self.typed_height}_ | Enter to confirm | Esc to cancel"
        else:
            width_str = units.unit_to_string(context.scene.unit_settings, self.current_width)
            height_str = units.unit_to_string(context.scene.unit_settings, self.current_height)
            text = f"Width: {width_str} | Height: {height_str}{snap_text} | Type for exact size | Click to place"
        
        hb_placement.draw_header_text(context, text)
    
    def handle_typing(self, event) -> bool:
        """Handle keyboard input for typing dimensions. Returns True if event was consumed."""
        # Number keys to start or continue typing
        if event.type in hb_placement.NUMBER_KEYS and event.value == 'PRESS':
            if not self.is_typing:
                # Start typing width
                self.is_typing = True
                self.typing_width = True
                self.typed_width = hb_placement.NUMBER_KEYS[event.type]
                self.typed_height = ""
            elif self.typing_width:
                self.typed_width += hb_placement.NUMBER_KEYS[event.type]
            else:
                self.typed_height += hb_placement.NUMBER_KEYS[event.type]
            
            # Update rectangle preview
            self._update_from_typed()
            return True
        
        if not self.is_typing:
            return False
        
        # Backspace
        if event.type == 'BACK_SPACE' and event.value == 'PRESS':
            if self.typing_width:
                if self.typed_width:
                    self.typed_width = self.typed_width[:-1]
                else:
                    # Exit typing mode
                    self.is_typing = False
            else:
                if self.typed_height:
                    self.typed_height = self.typed_height[:-1]
                else:
                    # Go back to typing width
                    self.typing_width = True
            self._update_from_typed()
            return True
        
        # Tab - switch between width and height
        if event.type == 'TAB' and event.value == 'PRESS':
            if self.typing_width:
                self.typing_width = False
            else:
                self.typing_width = True
            return True
        
        # Enter - confirm
        if event.type in {'RET', 'NUMPAD_ENTER'} and event.value == 'PRESS':
            width = self.parse_dimension(self.typed_width)
            height = self.parse_dimension(self.typed_height)
            
            if width > 0 and height > 0:
                self.update_rectangle_from_dimensions(width, height)
                return False  # Let modal handle the finish
            elif width > 0 and not self.typed_height:
                # Only width typed, switch to height
                self.typing_width = False
                return True
            return True
        
        # Escape - cancel typing
        if event.type == 'ESC' and event.value == 'PRESS':
            self.is_typing = False
            self.typed_width = ""
            self.typed_height = ""
            return True
        
        return False
    
    def _update_from_typed(self):
        """Update rectangle from currently typed values."""
        width = self.parse_dimension(self.typed_width) if self.typed_width else self.current_width
        height = self.parse_dimension(self.typed_height) if self.typed_height else self.current_height
        
        # Ensure we have valid numbers (parse_dimension can return 0.0 for incomplete input like ".")
        width = width or 0.0
        height = height or 0.0
        
        if width > 0 or height > 0:
            self.update_rectangle_from_dimensions(
                width if width > 0 else 0.1,
                height if height > 0 else 0.1
            )
    
    def execute(self, context):
        # Initialize placement
        self.init_placement(context)
        
        # Reset state
        self.polyline = None
        self.first_corner = None
        self.has_first_corner = False
        self.is_snapped = False
        self.snap_screen_pos = None
        self.typed_width = ""
        self.typed_height = ""
        self.typing_width = False
        self.is_typing = False
        self.current_width = 0.0
        self.current_height = 0.0
        
        # Add draw handler for snap indicator
        args = (self, context)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(
            draw_snap_indicator, args, 'WINDOW', 'POST_PIXEL')
        
        # Create rectangle
        self.create_rectangle(context)
        
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
    
    def modal(self, context, event):
        context.window.cursor_set('CROSSHAIR')
        context.area.tag_redraw()
        
        if event.type == "INBETWEEN_MOUSEMOVE":
            return {'RUNNING_MODAL'}
        
        # Handle typing input first (only after first corner is placed)
        if self.has_first_corner and self.handle_typing(event):
            self.update_header(context)
            return {'RUNNING_MODAL'}
        
        # Check if we should finish after Enter with valid dimensions
        if self.has_first_corner and event.type in {'RET', 'NUMPAD_ENTER'} and event.value == 'PRESS':
            width = self.parse_dimension(self.typed_width) if self.typed_width else 0
            height = self.parse_dimension(self.typed_height) if self.typed_height else 0
            
            if width > 0 and height > 0:
                self.update_rectangle_from_dimensions(width, height)
                self._remove_draw_handler()
                if self.polyline.obj in self.placement_objects:
                    self.placement_objects.remove(self.polyline.obj)
                hb_placement.clear_header_text(context)
                return {'FINISHED'}
        
        # Update snap (only if not typing)
        if not self.is_typing:
            if self.polyline and self.polyline.obj:
                self.polyline.obj.hide_set(True)
            self.update_snap(context, event)
            if self.polyline and self.polyline.obj:
                self.polyline.obj.hide_set(False)
            
            # Get current position with snapping
            current_pos = self.get_snapped_position(context)
            
            # Update rectangle preview
            if not self.has_first_corner:
                # Before first click, show rectangle at cursor (zero size)
                self.polyline.set_point(0, current_pos)
                self.polyline.set_point(1, current_pos)
                self.polyline.set_point(2, current_pos)
                self.polyline.set_point(3, current_pos)
            else:
                # After first click, update rectangle from first corner to cursor
                self.update_rectangle_from_corners(current_pos)
        
        self.update_header(context)
        
        # Left click - place corner
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if not self.has_first_corner:
                # Set first corner
                current_pos = self.get_snapped_position(context)
                self.first_corner = current_pos.copy()
                self.has_first_corner = True
                self.update_rectangle_from_corners(current_pos)
            elif not self.is_typing:
                # Confirm rectangle (only if not currently typing)
                self._remove_draw_handler()
                if self.polyline.obj in self.placement_objects:
                    self.placement_objects.remove(self.polyline.obj)
                hb_placement.clear_header_text(context)
                return {'FINISHED'}
            return {'RUNNING_MODAL'}
        
        # Right click / Escape - cancel (if not typing)
        if event.type == 'RIGHTMOUSE' and event.value == 'PRESS':
            self._remove_draw_handler()
            self.cancel_placement(context)
            hb_placement.clear_header_text(context)
            return {'CANCELLED'}
        
        if event.type == 'ESC' and event.value == 'PRESS' and not self.is_typing:
            self._remove_draw_handler()
            self.cancel_placement(context)
            hb_placement.clear_header_text(context)
            return {'CANCELLED'}
        
        # Pass through navigation
        if hb_snap.event_is_pass_through(event):
            return {'PASS_THROUGH'}
        
        return {'RUNNING_MODAL'}


# =============================================================================
# CIRCLE DRAWING OPERATOR
# =============================================================================

class home_builder_details_OT_draw_circle(bpy.types.Operator, hb_placement.PlacementMixin):
    bl_idname = "home_builder_details.draw_circle"
    bl_label = "Draw Circle"
    bl_description = "Draw a circle by clicking center then setting radius. Type for exact size."
    bl_options = {'UNDO'}
    
    # Circle state
    circle: hb_details.GeoNodeCircle = None
    center: Vector = None
    has_center: bool = False
    
    # Typed radius
    typed_radius: str = ""
    is_typing: bool = False
    
    # Current radius for display
    current_radius: float = 0.0
    
    # Snap state
    is_snapped: bool = False
    snap_screen_pos: tuple = None
    
    # Draw handler
    _handle = None
    
    def get_curve_vertices(self, context) -> list:
        """Get all curve vertices in the scene as world coordinates."""
        vertices = []
        for obj in context.scene.objects:
            if obj.type == 'CURVE' and (not self.circle or obj != self.circle.obj):
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
        
        best_point = None
        best_distance = SNAP_RADIUS
        
        vertices = self.get_curve_vertices(context)
        for co in vertices:
            co2D = view3d_utils.location_3d_to_region_2d(self.region, self.region.data, co)
            if co2D is not None:
                distance = (co2D - self.mouse_pos).length
                if distance < best_distance:
                    best_point = co.copy()
                    best_distance = distance
        
        return best_point
    
    def get_snapped_position(self, context) -> Vector:
        """Get position, snapping to curves if possible."""
        from bpy_extras import view3d_utils
        
        snap = self.snap_to_curves(context)
        if snap:
            self.is_snapped = True
            screen_pos = view3d_utils.location_3d_to_region_2d(self.region, self.region.data, snap)
            self.snap_screen_pos = (screen_pos.x, screen_pos.y) if screen_pos else None
            return Vector((snap.x, snap.y, 0))
        
        self.is_snapped = False
        if self.hit_location:
            screen_pos = view3d_utils.location_3d_to_region_2d(self.region, self.region.data, self.hit_location)
            self.snap_screen_pos = (screen_pos.x, screen_pos.y) if screen_pos else None
            return Vector((self.hit_location.x, self.hit_location.y, 0))
        
        self.snap_screen_pos = None
        return Vector((0, 0, 0))
    
    def create_circle(self, context):
        """Create a new circle object."""
        self.circle = hb_details.GeoNodeCircle()
        self.circle.create("Circle")
        
        # Apply annotation settings from scene
        hb_scene = context.scene.home_builder
        self.circle.obj.data.bevel_depth = hb_scene.annotation_line_thickness
        color = tuple(hb_scene.annotation_line_color) + (1.0,)
        self.circle.obj.color = color
        if self.circle.obj.data.materials:
            mat = self.circle.obj.data.materials[0]
            if mat and mat.use_nodes:
                bsdf = mat.node_tree.nodes.get("Principled BSDF")
                if bsdf:
                    bsdf.inputs["Base Color"].default_value = color
        
        self.circle.set_radius(0.001)  # Start very small
        self.register_placement_object(self.circle.obj)
    
    def parse_radius(self, value_str: str) -> float:
        """Parse a typed radius string to meters. Returns 0.0 if parsing fails."""
        if not value_str:
            return 0.0
        result = self.parse_typed_distance(value_str)
        return result if result is not None else 0.0
    
    def _remove_draw_handler(self):
        """Remove the draw handler."""
        if self._handle:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            self._handle = None
    
    def update_header(self, context):
        snap_text = " [SNAP]" if self.is_snapped else ""
        
        if not self.has_center:
            text = f"Click to place center{snap_text} | Right-click/Esc to cancel"
        elif self.is_typing:
            text = f"Radius: {self.typed_radius}_ | Enter to confirm | Esc to cancel typing"
        else:
            radius_str = units.unit_to_string(context.scene.unit_settings, self.current_radius)
            diameter_str = units.unit_to_string(context.scene.unit_settings, self.current_radius * 2)
            text = f"Radius: {radius_str} | Diameter: {diameter_str}{snap_text} | Type for exact | Click to place"
        
        hb_placement.draw_header_text(context, text)
    
    def handle_typing(self, event) -> bool:
        """Handle keyboard input for typing radius. Returns True if event was consumed."""
        # Number keys to start or continue typing
        if event.type in hb_placement.NUMBER_KEYS and event.value == 'PRESS':
            if not self.is_typing:
                self.is_typing = True
                self.typed_radius = hb_placement.NUMBER_KEYS[event.type]
            else:
                self.typed_radius += hb_placement.NUMBER_KEYS[event.type]
            
            # Update circle preview
            radius = self.parse_radius(self.typed_radius)
            if radius > 0:
                self.circle.set_radius(radius)
                self.current_radius = radius
            return True
        
        if not self.is_typing:
            return False
        
        # Backspace
        if event.type == 'BACK_SPACE' and event.value == 'PRESS':
            if self.typed_radius:
                self.typed_radius = self.typed_radius[:-1]
                radius = self.parse_radius(self.typed_radius)
                if radius > 0:
                    self.circle.set_radius(radius)
                    self.current_radius = radius
            else:
                self.is_typing = False
            return True
        
        # Enter - confirm
        if event.type in {'RET', 'NUMPAD_ENTER'} and event.value == 'PRESS':
            radius = self.parse_radius(self.typed_radius)
            if radius > 0:
                self.circle.set_radius(radius)
                self.current_radius = radius
                return False  # Let modal handle the finish
            return True
        
        # Escape - cancel typing
        if event.type == 'ESC' and event.value == 'PRESS':
            self.is_typing = False
            self.typed_radius = ""
            return True
        
        return False
    
    def execute(self, context):
        # Initialize placement
        self.init_placement(context)
        
        # Reset state
        self.circle = None
        self.center = None
        self.has_center = False
        self.is_snapped = False
        self.snap_screen_pos = None
        self.typed_radius = ""
        self.is_typing = False
        self.current_radius = 0.0
        
        # Add draw handler for snap indicator
        args = (self, context)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(
            draw_snap_indicator, args, 'WINDOW', 'POST_PIXEL')
        
        # Create circle
        self.create_circle(context)
        
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
    
    def modal(self, context, event):
        context.window.cursor_set('CROSSHAIR')
        context.area.tag_redraw()
        
        if event.type == "INBETWEEN_MOUSEMOVE":
            return {'RUNNING_MODAL'}
        
        # Handle typing input first (only after center is placed)
        if self.has_center and self.handle_typing(event):
            self.update_header(context)
            return {'RUNNING_MODAL'}
        
        # Check if we should finish after Enter with valid radius
        if self.has_center and event.type in {'RET', 'NUMPAD_ENTER'} and event.value == 'PRESS':
            radius = self.parse_radius(self.typed_radius) if self.typed_radius else self.current_radius
            if radius > 0:
                self.circle.set_radius(radius)
                self._remove_draw_handler()
                if self.circle.obj in self.placement_objects:
                    self.placement_objects.remove(self.circle.obj)
                hb_placement.clear_header_text(context)
                return {'FINISHED'}
        
        # Update snap (only if not typing)
        if not self.is_typing:
            if self.circle and self.circle.obj:
                self.circle.obj.hide_set(True)
            self.update_snap(context, event)
            if self.circle and self.circle.obj:
                self.circle.obj.hide_set(False)
            
            # Get current position with snapping
            current_pos = self.get_snapped_position(context)
            
            # Update circle preview
            if not self.has_center:
                # Before center click, move circle to cursor
                self.circle.set_center(current_pos)
            else:
                # After center click, update radius from cursor distance
                dx = current_pos.x - self.center.x
                dy = current_pos.y - self.center.y
                radius = math.sqrt(dx * dx + dy * dy)
                if radius > 0.001:
                    self.circle.set_radius(radius)
                    self.current_radius = radius
        
        self.update_header(context)
        
        # Left click - place center or confirm
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if not self.has_center:
                # Set center
                current_pos = self.get_snapped_position(context)
                self.center = current_pos.copy()
                self.circle.set_center(self.center)
                self.has_center = True
            elif not self.is_typing:
                # Confirm circle (only if not currently typing)
                if self.current_radius > 0.001:
                    self._remove_draw_handler()
                    if self.circle.obj in self.placement_objects:
                        self.placement_objects.remove(self.circle.obj)
                    hb_placement.clear_header_text(context)
                    return {'FINISHED'}
            return {'RUNNING_MODAL'}
        
        # Right click / Escape - cancel (if not typing)
        if event.type == 'RIGHTMOUSE' and event.value == 'PRESS':
            self._remove_draw_handler()
            self.cancel_placement(context)
            hb_placement.clear_header_text(context)
            return {'CANCELLED'}
        
        if event.type == 'ESC' and event.value == 'PRESS' and not self.is_typing:
            self._remove_draw_handler()
            self.cancel_placement(context)
            hb_placement.clear_header_text(context)
            return {'CANCELLED'}
        
        # Pass through navigation
        if hb_snap.event_is_pass_through(event):
            return {'PASS_THROUGH'}
        
        return {'RUNNING_MODAL'}


# =============================================================================
# TEXT ANNOTATION OPERATOR
# =============================================================================

class home_builder_details_OT_add_text(bpy.types.Operator, hb_placement.PlacementMixin):
    bl_idname = "home_builder_details.add_text"
    bl_label = "Add Text"
    bl_description = "Add text annotation. Click to place, then Tab to edit."
    bl_options = {'UNDO'}
    
    # Text state
    text_obj: hb_details.GeoNodeText = None
    
    # Snap state
    is_snapped: bool = False
    snap_screen_pos: tuple = None
    
    # Draw handler
    _handle = None
    
    def get_curve_vertices(self, context) -> list:
        """Get all curve vertices in the scene as world coordinates."""
        vertices = []
        for obj in context.scene.objects:
            if obj.type == 'CURVE':
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
        
        best_point = None
        best_distance = SNAP_RADIUS
        
        vertices = self.get_curve_vertices(context)
        for co in vertices:
            co2D = view3d_utils.location_3d_to_region_2d(self.region, self.region.data, co)
            if co2D is not None:
                distance = (co2D - self.mouse_pos).length
                if distance < best_distance:
                    best_point = co.copy()
                    best_distance = distance
        
        return best_point
    
    def get_snapped_position(self, context) -> Vector:
        """Get position, snapping to curves if possible."""
        from bpy_extras import view3d_utils
        
        snap = self.snap_to_curves(context)
        if snap:
            self.is_snapped = True
            screen_pos = view3d_utils.location_3d_to_region_2d(self.region, self.region.data, snap)
            self.snap_screen_pos = (screen_pos.x, screen_pos.y) if screen_pos else None
            return Vector((snap.x, snap.y, 0))
        
        self.is_snapped = False
        if self.hit_location:
            screen_pos = view3d_utils.location_3d_to_region_2d(self.region, self.region.data, self.hit_location)
            self.snap_screen_pos = (screen_pos.x, screen_pos.y) if screen_pos else None
            return Vector((self.hit_location.x, self.hit_location.y, 0))
        
        self.snap_screen_pos = None
        return Vector((0, 0, 0))
    
    def create_text(self, context):
        """Create a new text object."""
        hb_scene = context.scene.home_builder
        
        self.text_obj = hb_details.GeoNodeText()
        self.text_obj.create("Text", "TEXT", hb_scene.annotation_text_size)
        
        # Apply font if set
        if hb_scene.annotation_font:
            self.text_obj.obj.data.font = hb_scene.annotation_font
        
        # Apply text color
        color = tuple(hb_scene.annotation_text_color) + (1.0,)
        self.text_obj.obj.color = color
        if self.text_obj.obj.data.materials:
            mat = self.text_obj.obj.data.materials[0]
            if mat and mat.use_nodes:
                bsdf = mat.node_tree.nodes.get("Principled BSDF")
                if bsdf:
                    bsdf.inputs["Base Color"].default_value = color
        
        self.register_placement_object(self.text_obj.obj)
    
    def _remove_draw_handler(self):
        """Remove the draw handler."""
        if self._handle:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            self._handle = None
    
    def update_header(self, context):
        snap_text = " [SNAP]" if self.is_snapped else ""
        text = f"Click to place text{snap_text} | Tab to edit after placing | Right-click/Esc to cancel"
        hb_placement.draw_header_text(context, text)
    
    def execute(self, context):
        # Initialize placement
        self.init_placement(context)
        
        # Reset state
        self.text_obj = None
        self.is_snapped = False
        self.snap_screen_pos = None
        
        # Add draw handler for snap indicator
        args = (self, context)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(
            draw_snap_indicator, args, 'WINDOW', 'POST_PIXEL')
        
        # Create text object
        self.create_text(context)
        
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
    
    def modal(self, context, event):
        context.window.cursor_set('CROSSHAIR')
        context.area.tag_redraw()
        
        if event.type == "INBETWEEN_MOUSEMOVE":
            return {'RUNNING_MODAL'}
        
        # Update snap
        if self.text_obj and self.text_obj.obj:
            self.text_obj.obj.hide_set(True)
        self.update_snap(context, event)
        if self.text_obj and self.text_obj.obj:
            self.text_obj.obj.hide_set(False)
        
        # Get current position with snapping
        current_pos = self.get_snapped_position(context)
        
        # Update text position
        self.text_obj.set_location(current_pos)
        
        self.update_header(context)
        
        # Left click - place text
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            current_pos = self.get_snapped_position(context)
            self.text_obj.set_location(current_pos)
            
            # Select the text object so user can Tab to edit
            bpy.ops.object.select_all(action='DESELECT')
            self.text_obj.obj.select_set(True)
            context.view_layer.objects.active = self.text_obj.obj
            
            self._remove_draw_handler()
            if self.text_obj.obj in self.placement_objects:
                self.placement_objects.remove(self.text_obj.obj)
            hb_placement.clear_header_text(context)
            return {'FINISHED'}
        
        # Right click / Escape - cancel
        if event.type in {'RIGHTMOUSE', 'ESC'} and event.value == 'PRESS':
            self._remove_draw_handler()
            self.cancel_placement(context)
            hb_placement.clear_header_text(context)
            return {'CANCELLED'}
        
        # Pass through navigation
        if hb_snap.event_is_pass_through(event):
            return {'PASS_THROUGH'}
        
        return {'RUNNING_MODAL'}


# =============================================================================
# FILLET/RADIUS OPERATOR
# =============================================================================

class home_builder_details_OT_add_fillet(bpy.types.Operator):
    bl_idname = "home_builder_details.add_fillet"
    bl_label = "Add Fillet"
    bl_description = "Add a radius/fillet to the selected corner point"
    bl_options = {'REGISTER', 'UNDO'}
    
    radius: bpy.props.FloatProperty(
        name="Radius",
        description="Fillet radius",
        default=0.0254,  # 1 inch
        min=0.001,
        unit='LENGTH',
    )
    
    segments: bpy.props.IntProperty(
        name="Segments",
        description="Number of segments in the fillet arc",
        default=8,
        min=2,
        max=32,
    )
    
    @classmethod
    def poll(cls, context):
        # Must be in edit mode on a curve
        if context.mode != 'EDIT_CURVE':
            return False
        obj = context.active_object
        if not obj or obj.type != 'CURVE':
            return False
        return True
    
    def get_selected_point_info(self, context):
        """
        Find the selected point and verify it has neighbors.
        Returns (spline, point_index) or (None, None) if invalid.
        """
        obj = context.active_object
        curve = obj.data
        
        for spline in curve.splines:
            if spline.type != 'POLY':
                continue
            
            points = spline.points
            num_points = len(points)
            is_cyclic = spline.use_cyclic_u
            
            selected_indices = []
            for i, point in enumerate(points):
                if point.select:
                    selected_indices.append(i)
            
            # Must have exactly one point selected
            if len(selected_indices) != 1:
                continue
            
            idx = selected_indices[0]
            
            # Check if point has neighbors
            if is_cyclic:
                # Cyclic spline - all points have neighbors
                return (spline, idx)
            else:
                # Non-cyclic - endpoints don't have both neighbors
                if idx == 0 or idx == num_points - 1:
                    continue
                return (spline, idx)
        
        return (None, None)
    
    def invoke(self, context, event):
        spline, idx = self.get_selected_point_info(context)
        if spline is None:
            self.report({'WARNING'}, "Select a single corner point (not an endpoint)")
            return {'CANCELLED'}
        
        return context.window_manager.invoke_props_dialog(self)
    
    def execute(self, context):
        import math
        
        obj = context.active_object
        curve = obj.data
        
        # Get info while in edit mode
        spline, point_idx = self.get_selected_point_info(context)
        if spline is None:
            self.report({'WARNING'}, "Select a single corner point (not an endpoint)")
            return {'CANCELLED'}
        
        # Find spline index
        spline_idx = None
        for i, s in enumerate(curve.splines):
            if s == spline:
                spline_idx = i
                break
        
        if spline_idx is None:
            self.report({'ERROR'}, "Could not find spline")
            return {'CANCELLED'}
        
        # Get point data while still in edit mode
        points = spline.points
        num_points = len(points)
        is_cyclic = spline.use_cyclic_u
        
        # Get the three point indices: prev, current (corner), next
        if is_cyclic:
            prev_idx = (point_idx - 1) % num_points
            next_idx = (point_idx + 1) % num_points
        else:
            prev_idx = point_idx - 1
            next_idx = point_idx + 1
        
        # Get coordinates (in object space)
        p_prev = Vector((points[prev_idx].co[0], points[prev_idx].co[1], 0))
        p_corner = Vector((points[point_idx].co[0], points[point_idx].co[1], 0))
        p_next = Vector((points[next_idx].co[0], points[next_idx].co[1], 0))
        
        # Store all point coordinates before leaving edit mode
        all_points_data = [(pt.co[0], pt.co[1], pt.co[2], pt.co[3]) for pt in points]
        
        # Calculate direction vectors
        dir_in = (p_corner - p_prev).normalized()
        dir_out = (p_next - p_corner).normalized()
        
        # Calculate the angle between the two edges
        dot = dir_in.dot(dir_out)
        dot = max(-1, min(1, dot))  # Clamp for numerical stability
        angle = math.acos(dot)
        
        if angle < 0.01 or angle > math.pi - 0.01:
            self.report({'WARNING'}, "Cannot fillet: edges are nearly parallel")
            return {'CANCELLED'}
        
        # Calculate the half angle
        half_angle = (math.pi - angle) / 2
        
        # Distance from corner to tangent points
        tan_dist = self.radius / math.tan(half_angle)
        
        # Check if radius is too large
        dist_to_prev = (p_corner - p_prev).length
        dist_to_next = (p_next - p_corner).length
        
        if tan_dist > dist_to_prev * 0.9 or tan_dist > dist_to_next * 0.9:
            self.report({'WARNING'}, "Radius too large for this corner")
            return {'CANCELLED'}
        
        # Calculate tangent points
        tangent_in = p_corner - dir_in * tan_dist
        tangent_out = p_corner + dir_out * tan_dist
        
        # Calculate arc center
        bisector = ((-dir_in + dir_out) / 2).normalized()
        center_dist = self.radius / math.sin(half_angle)
        arc_center = p_corner + bisector * center_dist
        
        # Generate arc points
        arc_points = []
        
        start_vec = (tangent_in - arc_center).normalized()
        end_vec = (tangent_out - arc_center).normalized()
        
        cross = start_vec.x * end_vec.y - start_vec.y * end_vec.x
        
        start_angle = math.atan2(start_vec.y, start_vec.x)
        end_angle = math.atan2(end_vec.y, end_vec.x)
        
        if cross > 0:
            if end_angle <= start_angle:
                end_angle += 2 * math.pi
        else:
            if end_angle >= start_angle:
                end_angle -= 2 * math.pi
        
        for i in range(self.segments + 1):
            t = i / self.segments
            current_angle = start_angle + t * (end_angle - start_angle)
            x = arc_center.x + self.radius * math.cos(current_angle)
            y = arc_center.y + self.radius * math.sin(current_angle)
            arc_points.append((x, y, 0, 1))
        
        # Exit edit mode to modify curve data
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Get fresh references after mode change
        curve = obj.data
        spline = curve.splines[spline_idx]
        
        # Build new points list
        new_points = []
        for i, pt_data in enumerate(all_points_data):
            if i == point_idx:
                # Replace corner with arc points
                for arc_pt in arc_points:
                    new_points.append(arc_pt)
            else:
                new_points.append(pt_data)
        
        # Clear and recreate spline
        curve.splines.remove(spline)
        
        new_spline = curve.splines.new('POLY')
        new_spline.points.add(len(new_points) - 1)
        
        for i, pt in enumerate(new_points):
            new_spline.points[i].co = pt
        
        new_spline.use_cyclic_u = is_cyclic
        
        # Return to edit mode
        bpy.ops.object.mode_set(mode='EDIT')
        
        return {'FINISHED'}
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "radius")
        layout.prop(self, "segments")


# =============================================================================
# OFFSET CURVE OPERATOR
# =============================================================================

class home_builder_details_OT_offset_curve(bpy.types.Operator):
    bl_idname = "home_builder_details.offset_curve"
    bl_label = "Offset Curve"
    bl_description = "Create an offset copy of the selected curve (like AutoCAD offset)"
    bl_options = {'REGISTER', 'UNDO'}
    
    offset_distance: bpy.props.FloatProperty(
        name="Offset Distance",
        description="Distance to offset the curve",
        default=0.0254,  # 1 inch
        min=0.0001,
        unit='LENGTH',
    )
    
    offset_side: bpy.props.EnumProperty(
        name="Side",
        description="Which side to offset",
        items=[
            ('LEFT', "Left/Inside", "Offset to the left side (inside for closed curves)"),
            ('RIGHT', "Right/Outside", "Offset to the right side (outside for closed curves)"),
        ],
        default='LEFT',
    )
    
    # Store references for live preview
    _source_obj = None
    _preview_obj = None
    _was_edit_mode = False
    
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if not obj or obj.type != 'CURVE':
            return False
        return context.mode in {'OBJECT', 'EDIT_CURVE'}
    
    def invoke(self, context, event):
        self._source_obj = context.active_object
        
        # If in edit mode, go to object mode
        self._was_edit_mode = (context.mode == 'EDIT_CURVE')
        if self._was_edit_mode:
            bpy.ops.object.mode_set(mode='OBJECT')
        
        # Create initial preview
        self._create_preview(context)
        
        return context.window_manager.invoke_props_dialog(self)
    
    def check(self, context):
        """Called when properties change - update the preview."""
        self._update_preview(context)
        return True  # Redraw the UI
    
    def cancel(self, context):
        """Called when dialog is cancelled - remove preview."""
        self._remove_preview(context)
        
        if self._was_edit_mode:
            bpy.ops.object.mode_set(mode='EDIT')
    
    def execute(self, context):
        # If preview exists (from invoke), keep it as the result
        if self._preview_obj:
            # Deselect source, select the offset result
            if self._source_obj:
                self._source_obj.select_set(False)
            
            self._preview_obj.select_set(True)
            context.view_layer.objects.active = self._preview_obj
            
            # Clear references
            self._preview_obj = None
            self._source_obj = None
            
            if self._was_edit_mode:
                bpy.ops.object.mode_set(mode='EDIT')
            
            return {'FINISHED'}
        
        # Direct execution (not through invoke) - create the offset now
        obj = context.active_object
        if not obj or obj.type != 'CURVE':
            self.report({'WARNING'}, "No curve selected")
            return {'CANCELLED'}
        
        was_edit_mode = (context.mode == 'EDIT_CURVE')
        if was_edit_mode:
            bpy.ops.object.mode_set(mode='OBJECT')
        
        curve = obj.data
        new_splines_data = []
        
        for spline in curve.splines:
            if spline.type != 'POLY':
                continue
            
            points = spline.points
            num_points = len(points)
            is_cyclic = spline.use_cyclic_u
            
            if num_points < 2:
                continue
            
            coords = [Vector((p.co[0], p.co[1], 0)) for p in points]
            offset_coords = self._calculate_offset(coords, is_cyclic)
            
            if offset_coords:
                new_splines_data.append({
                    'points': offset_coords,
                    'cyclic': is_cyclic
                })
        
        if not new_splines_data:
            self.report({'WARNING'}, "No valid splines to offset")
            if was_edit_mode:
                bpy.ops.object.mode_set(mode='EDIT')
            return {'CANCELLED'}
        
        # Create new curve
        new_curve = bpy.data.curves.new(f"{obj.name}_Offset", 'CURVE')
        new_curve.dimensions = '2D'
        
        for spline_data in new_splines_data:
            new_spline = new_curve.splines.new('POLY')
            pts = spline_data['points']
            new_spline.points.add(len(pts) - 1)
            
            for i, pt in enumerate(pts):
                new_spline.points[i].co = (pt.x, pt.y, 0, 1)
            
            new_spline.use_cyclic_u = spline_data['cyclic']
        
        # Create object
        new_obj = bpy.data.objects.new(f"{obj.name}_Offset", new_curve)
        new_obj.location = obj.location.copy()
        new_obj.rotation_euler = obj.rotation_euler.copy()
        new_obj.scale = obj.scale.copy()
        new_obj.color = (0, 0, 0, 1)
        new_obj['IS_DETAIL_POLYLINE'] = True
        
        context.scene.collection.objects.link(new_obj)
        
        # Copy or create material
        if curve.materials:
            new_curve.materials.append(curve.materials[0])
        else:
            mat = bpy.data.materials.new(f"{new_obj.name}_Mat")
            mat.use_nodes = True
            mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0, 0, 0, 1)
            new_curve.materials.append(mat)
        
        new_curve.bevel_depth = curve.bevel_depth if curve.bevel_depth > 0 else 0.002
        
        # Select new object
        obj.select_set(False)
        new_obj.select_set(True)
        context.view_layer.objects.active = new_obj
        
        if was_edit_mode:
            bpy.ops.object.mode_set(mode='EDIT')
        
        return {'FINISHED'}
    
    def _create_preview(self, context):
        """Create the preview offset curve."""
        if not self._source_obj:
            return
        
        obj = self._source_obj
        curve = obj.data
        
        # Calculate offset for all splines
        new_splines_data = []
        
        for spline in curve.splines:
            if spline.type != 'POLY':
                continue
            
            points = spline.points
            num_points = len(points)
            is_cyclic = spline.use_cyclic_u
            
            if num_points < 2:
                continue
            
            coords = [Vector((p.co[0], p.co[1], 0)) for p in points]
            offset_coords = self._calculate_offset(coords, is_cyclic)
            
            if offset_coords:
                new_splines_data.append({
                    'points': offset_coords,
                    'cyclic': is_cyclic
                })
        
        if not new_splines_data:
            return
        
        # Create new curve object
        new_curve = bpy.data.curves.new(f"{obj.name}_Offset", 'CURVE')
        new_curve.dimensions = '2D'
        
        for spline_data in new_splines_data:
            new_spline = new_curve.splines.new('POLY')
            pts = spline_data['points']
            new_spline.points.add(len(pts) - 1)
            
            for i, pt in enumerate(pts):
                new_spline.points[i].co = (pt.x, pt.y, 0, 1)
            
            new_spline.use_cyclic_u = spline_data['cyclic']
        
        # Create object
        self._preview_obj = bpy.data.objects.new(f"{obj.name}_Offset", new_curve)
        self._preview_obj.location = obj.location.copy()
        self._preview_obj.rotation_euler = obj.rotation_euler.copy()
        self._preview_obj.scale = obj.scale.copy()
        self._preview_obj.color = (0, 0, 0, 1)
        self._preview_obj['IS_DETAIL_POLYLINE'] = True
        
        context.scene.collection.objects.link(self._preview_obj)
        
        # Copy or create material
        if curve.materials:
            new_curve.materials.append(curve.materials[0])
        else:
            mat = bpy.data.materials.new(f"{self._preview_obj.name}_Mat")
            mat.use_nodes = True
            mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0, 0, 0, 1)
            new_curve.materials.append(mat)
        
        new_curve.bevel_depth = curve.bevel_depth if curve.bevel_depth > 0 else 0.002
    
    def _update_preview(self, context):
        """Update the preview with current settings."""
        if not self._preview_obj or not self._source_obj:
            return
        
        obj = self._source_obj
        curve = obj.data
        preview_curve = self._preview_obj.data
        
        # Recalculate offset for each spline
        spline_idx = 0
        for spline in curve.splines:
            if spline.type != 'POLY':
                continue
            
            points = spline.points
            num_points = len(points)
            is_cyclic = spline.use_cyclic_u
            
            if num_points < 2:
                continue
            
            coords = [Vector((p.co[0], p.co[1], 0)) for p in points]
            offset_coords = self._calculate_offset(coords, is_cyclic)
            
            if offset_coords and spline_idx < len(preview_curve.splines):
                preview_spline = preview_curve.splines[spline_idx]
                
                # Update points
                for i, pt in enumerate(offset_coords):
                    if i < len(preview_spline.points):
                        preview_spline.points[i].co = (pt.x, pt.y, 0, 1)
                
                spline_idx += 1
        
        # Force viewport update
        self._preview_obj.data.update_tag()
        context.area.tag_redraw()
    
    def _remove_preview(self, context):
        """Remove the preview object."""
        if self._preview_obj:
            # Remove the curve data and object
            curve_data = self._preview_obj.data
            bpy.data.objects.remove(self._preview_obj)
            bpy.data.curves.remove(curve_data)
            self._preview_obj = None
    
    def _calculate_offset(self, coords, is_cyclic):
        """Calculate offset points for a polyline."""
        import math
        
        num_points = len(coords)
        if num_points < 2:
            return None
        
        # Direction multiplier (left = 1, right = -1)
        side_mult = 1.0 if self.offset_side == 'LEFT' else -1.0
        offset = self.offset_distance * side_mult
        
        offset_points = []
        
        for i in range(num_points):
            p_curr = coords[i]
            
            if is_cyclic:
                p_prev = coords[(i - 1) % num_points]
                p_next = coords[(i + 1) % num_points]
                has_prev = True
                has_next = True
            else:
                has_prev = i > 0
                has_next = i < num_points - 1
                p_prev = coords[i - 1] if has_prev else None
                p_next = coords[i + 1] if has_next else None
            
            if has_prev and has_next:
                dir_in = (p_curr - p_prev).normalized()
                dir_out = (p_next - p_curr).normalized()
                
                perp_in = Vector((-dir_in.y, dir_in.x, 0))
                perp_out = Vector((-dir_out.y, dir_out.x, 0))
                
                bisector = (perp_in + perp_out).normalized()
                
                dot = perp_in.dot(bisector)
                if abs(dot) > 0.001:
                    miter_length = offset / dot
                else:
                    miter_length = offset
                
                max_miter = abs(offset) * 4
                miter_length = max(-max_miter, min(max_miter, miter_length))
                
                offset_point = p_curr + bisector * miter_length
                
            elif has_prev:
                dir_in = (p_curr - p_prev).normalized()
                perp = Vector((-dir_in.y, dir_in.x, 0))
                offset_point = p_curr + perp * offset
                
            elif has_next:
                dir_out = (p_next - p_curr).normalized()
                perp = Vector((-dir_out.y, dir_out.x, 0))
                offset_point = p_curr + perp * offset
                
            else:
                offset_point = p_curr
            
            offset_points.append(offset_point)
        
        return offset_points
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "offset_distance")
        layout.prop(self, "offset_side", expand=True)


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
        hb_scene = context.scene.home_builder
        
        self.dim = hb_types.GeoNodeDimension()
        self.dim.create("Dimension")
        self.dim.obj['IS_2D_ANNOTATION'] = True
        
        # Apply dimension settings from scene
        self.dim.set_input("Text Size", hb_scene.annotation_dimension_text_size)
        self.dim.set_input("Tick Length", hb_scene.annotation_dimension_tick_length)
        
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

# =============================================================================
# DETAIL LIBRARY OPERATORS
# =============================================================================

class home_builder_details_OT_save_detail_to_library(bpy.types.Operator):
    bl_idname = "home_builder_details.save_to_library"
    bl_label = "Save Detail to Library"
    bl_description = "Save the current detail to your user library"
    bl_options = {'REGISTER', 'UNDO'}
    
    name: bpy.props.StringProperty(
        name="Name",
        description="Name for this detail in the library",
        default="My Detail"
    )
    
    description: bpy.props.StringProperty(
        name="Description",
        description="Optional description",
        default=""
    )
    
    @classmethod
    def poll(cls, context):
        return context.scene.get('IS_DETAIL_VIEW', False)
    
    def invoke(self, context, event):
        # Default name from scene name
        scene_name = context.scene.name
        if scene_name != "Detail":
            self.name = scene_name
        return context.window_manager.invoke_props_dialog(self, width=300)
    
    def execute(self, context):
        success, message, filepath = hb_detail_library.save_detail_to_library(
            context, self.name, self.description
        )
        
        if success:
            self.report({'INFO'}, message)
        else:
            self.report({'ERROR'}, message)
            return {'CANCELLED'}
        
        return {'FINISHED'}
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "name")
        layout.prop(self, "description")


class home_builder_details_OT_load_detail_from_library(bpy.types.Operator):
    bl_idname = "home_builder_details.load_from_library"
    bl_label = "Load Detail from Library"
    bl_description = "Load a detail from your user library"
    bl_options = {'REGISTER', 'UNDO'}
    
    filepath: bpy.props.StringProperty(
        name="Filepath",
        description="Path to the detail file",
        default=""
    )
    
    @classmethod
    def poll(cls, context):
        return context.scene.get('IS_DETAIL_VIEW', False)
    
    def execute(self, context):
        if not self.filepath:
            self.report({'ERROR'}, "No file specified")
            return {'CANCELLED'}
        
        success, message, objects = hb_detail_library.load_detail_from_library(
            context, self.filepath
        )
        
        if success:
            self.report({'INFO'}, message)
        else:
            self.report({'ERROR'}, message)
            return {'CANCELLED'}
        
        return {'FINISHED'}


class home_builder_details_OT_delete_library_detail(bpy.types.Operator):
    bl_idname = "home_builder_details.delete_library_detail"
    bl_label = "Delete Library Detail"
    bl_description = "Delete a detail from your user library"
    bl_options = {'REGISTER', 'UNDO'}
    
    filename: bpy.props.StringProperty(
        name="Filename",
        description="Filename of the detail to delete",
        default=""
    )
    
    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)
    
    def execute(self, context):
        if not self.filename:
            self.report({'ERROR'}, "No file specified")
            return {'CANCELLED'}
        
        success, message = hb_detail_library.delete_detail_from_library(self.filename)
        
        if success:
            self.report({'INFO'}, message)
        else:
            self.report({'ERROR'}, message)
            return {'CANCELLED'}
        
        return {'FINISHED'}


class home_builder_details_OT_open_library_folder(bpy.types.Operator):
    bl_idname = "home_builder_details.open_library_folder"
    bl_label = "Open Library Folder"
    bl_description = "Open the detail library folder in file explorer"
    
    def execute(self, context):
        import subprocess
        import sys
        
        library_path = hb_detail_library.get_user_library_path()
        
        if sys.platform == 'win32':
            subprocess.Popen(['explorer', library_path])
        elif sys.platform == 'darwin':
            subprocess.Popen(['open', library_path])
        else:
            subprocess.Popen(['xdg-open', library_path])
        
        return {'FINISHED'}


classes = (
    home_builder_details_OT_create_detail,
    home_builder_details_OT_delete_detail,
    home_builder_details_OT_draw_line,
    home_builder_details_OT_draw_rectangle,
    home_builder_details_OT_draw_circle,
    home_builder_details_OT_add_text,
    home_builder_details_OT_add_fillet,
    home_builder_details_OT_offset_curve,
    home_builder_details_OT_add_dimension,
    home_builder_details_OT_save_detail_to_library,
    home_builder_details_OT_load_detail_from_library,
    home_builder_details_OT_delete_library_detail,
    home_builder_details_OT_open_library_folder,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
