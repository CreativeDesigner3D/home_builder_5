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
        self.circle.obj.color = (0, 0, 0, 1)  # Ensure black color
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
    
    # Text size (default 1/2" for cabinet drawings)
    text_size: float = 0.0127  # 1/2 inch in meters
    
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
        self.text_obj = hb_details.GeoNodeText()
        self.text_obj.create("Text", "TEXT", self.text_size)
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
    
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if not obj or obj.type != 'CURVE':
            return False
        return context.mode in {'OBJECT', 'EDIT_CURVE'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
    def execute(self, context):
        import math
        
        obj = context.active_object
        
        # If in edit mode, go to object mode
        was_edit_mode = (context.mode == 'EDIT_CURVE')
        if was_edit_mode:
            bpy.ops.object.mode_set(mode='OBJECT')
        
        curve = obj.data
        
        # Process each spline
        new_splines_data = []
        
        for spline in curve.splines:
            if spline.type != 'POLY':
                continue
            
            points = spline.points
            num_points = len(points)
            is_cyclic = spline.use_cyclic_u
            
            if num_points < 2:
                continue
            
            # Get point coordinates
            coords = [Vector((p.co[0], p.co[1], 0)) for p in points]
            
            # Calculate offset points
            offset_coords = self.calculate_offset(coords, is_cyclic)
            
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
        
        # Create new curve object with offset splines
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
        
        # Copy material from original
        if curve.materials:
            mat = curve.materials[0]
            new_curve.materials.append(mat)
        else:
            # Create black material
            mat = bpy.data.materials.new(f"{new_obj.name}_Mat")
            mat.use_nodes = True
            mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0, 0, 0, 1)
            new_curve.materials.append(mat)
        
        # Set bevel
        new_curve.bevel_depth = curve.bevel_depth if curve.bevel_depth > 0 else 0.002
        
        # Select new object
        bpy.ops.object.select_all(action='DESELECT')
        new_obj.select_set(True)
        context.view_layer.objects.active = new_obj
        
        if was_edit_mode:
            bpy.ops.object.mode_set(mode='EDIT')
        
        return {'FINISHED'}
    
    def calculate_offset(self, coords, is_cyclic):
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
            # Get current point and neighbors
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
                # Interior point - calculate bisector offset
                dir_in = (p_curr - p_prev).normalized()
                dir_out = (p_next - p_curr).normalized()
                
                # Calculate perpendiculars (rotated 90 degrees)
                perp_in = Vector((-dir_in.y, dir_in.x, 0))
                perp_out = Vector((-dir_out.y, dir_out.x, 0))
                
                # Average perpendicular (bisector direction)
                bisector = (perp_in + perp_out).normalized()
                
                # Calculate the miter length
                # The miter length accounts for the angle between segments
                dot = perp_in.dot(bisector)
                if abs(dot) > 0.001:
                    miter_length = offset / dot
                else:
                    miter_length = offset
                
                # Limit miter length to avoid extreme spikes at sharp angles
                max_miter = abs(offset) * 4
                miter_length = max(-max_miter, min(max_miter, miter_length))
                
                offset_point = p_curr + bisector * miter_length
                
            elif has_prev:
                # End point - offset perpendicular to incoming edge
                dir_in = (p_curr - p_prev).normalized()
                perp = Vector((-dir_in.y, dir_in.x, 0))
                offset_point = p_curr + perp * offset
                
            elif has_next:
                # Start point - offset perpendicular to outgoing edge
                dir_out = (p_next - p_curr).normalized()
                perp = Vector((-dir_out.y, dir_out.x, 0))
                offset_point = p_curr + perp * offset
                
            else:
                # Single point - can't offset
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
    home_builder_details_OT_draw_rectangle,
    home_builder_details_OT_draw_circle,
    home_builder_details_OT_add_text,
    home_builder_details_OT_add_fillet,
    home_builder_details_OT_offset_curve,
    home_builder_details_OT_add_dimension,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
