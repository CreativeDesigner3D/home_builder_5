import bpy
import math
from mathutils import Vector
from .. import hb_details
from .. import hb_types
from .. import hb_snap
from .. import hb_placement
from .. import units


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
    bl_description = "Draw a 2D line. Click to place points, type for exact length"
    bl_options = {'UNDO'}
    
    # Line state
    current_line: hb_details.GeoNodeLine = None
    start_point: Vector = None
    has_start_point: bool = False
    
    # Ortho mode (snap to 0, 45, 90 degree angles)
    ortho_mode: bool = True
    ortho_angle: float = 0.0
    
    def get_default_typing_target(self):
        return hb_placement.TypingTarget.LENGTH
    
    def on_typed_value_changed(self):
        if self.typed_value and self.current_line and self.has_start_point:
            parsed = self.parse_typed_distance()
            if parsed is not None:
                self._update_line_from_length(parsed)
        self.update_header(bpy.context)
    
    def apply_typed_value(self):
        parsed = self.parse_typed_distance()
        if parsed is not None and self.current_line and self.has_start_point:
            self._update_line_from_length(parsed)
            self._confirm_line()
        self.stop_typing()
    
    def _update_line_from_length(self, length: float):
        """Update line end point based on typed length and current angle."""
        if self.start_point:
            end_x = self.start_point.x + math.cos(self.ortho_angle) * length
            end_y = self.start_point.y + math.sin(self.ortho_angle) * length
            end_point = Vector((end_x, end_y, 0))
            self.current_line.set_points(self.start_point, end_point)
    
    def create_line(self, context):
        """Create a new line object."""
        self.current_line = hb_details.GeoNodeLine()
        self.current_line.create("Line")
        self.register_placement_object(self.current_line.obj)
    
    def _set_line_from_mouse(self):
        """Update line based on mouse position."""
        if not self.has_start_point or not self.hit_location:
            return
        
        end_point = Vector(self.hit_location)
        end_point.z = 0  # Keep in XY plane
        
        if self.ortho_mode:
            # Calculate angle from start to mouse
            dx = end_point.x - self.start_point.x
            dy = end_point.y - self.start_point.y
            
            if abs(dx) < 0.0001 and abs(dy) < 0.0001:
                return
            
            angle = math.atan2(dy, dx)
            
            # Snap to nearest 45 degrees
            snap_angle = round(math.degrees(angle) / 45) * 45
            self.ortho_angle = math.radians(snap_angle)
            
            # Calculate length
            length = math.sqrt(dx * dx + dy * dy)
            
            # Recalculate end point on snapped angle
            end_point.x = self.start_point.x + math.cos(self.ortho_angle) * length
            end_point.y = self.start_point.y + math.sin(self.ortho_angle) * length
        else:
            # Free angle - just use mouse position
            dx = end_point.x - self.start_point.x
            dy = end_point.y - self.start_point.y
            self.ortho_angle = math.atan2(dy, dx)
        
        self.current_line.set_points(self.start_point, end_point)
    
    def _confirm_line(self):
        """Confirm current line and prepare for next."""
        if self.current_line and self.current_line.obj:
            # Remove from cancel list (it's confirmed)
            if self.current_line.obj in self.placement_objects:
                self.placement_objects.remove(self.current_line.obj)
            
            # Update start point to end of line
            spline = self.current_line.obj.data.splines[0]
            end_co = spline.points[1].co
            self.start_point = Vector((end_co[0], end_co[1], 0))
            
            # Create next line
            self.create_line(bpy.context)
    
    def update_header(self, context):
        if self.placement_state == hb_placement.PlacementState.TYPING:
            text = f"Line Length: {self.typed_value}_ | Enter to confirm | Esc to cancel typing"
        elif self.has_start_point:
            length = self.current_line.get_length()
            length_str = units.unit_to_string(context.scene.unit_settings, length)
            angle_deg = round(math.degrees(self.ortho_angle))
            mode = "Ortho (45°)" if self.ortho_mode else "Free"
            text = f"Length: {length_str} | Angle: {angle_deg}° | {mode} | Alt: toggle ortho | Type for exact | Click to place"
        else:
            text = "Click to place first point | Right-click/Esc to cancel"
        
        hb_placement.draw_header_text(context, text)
    
    def execute(self, context):
        # Initialize placement
        self.init_placement(context)
        
        # Reset state
        self.current_line = None
        self.start_point = None
        self.has_start_point = False
        self.ortho_mode = True
        self.ortho_angle = 0.0
        
        # Create first line
        self.create_line(context)
        
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
    
    def modal(self, context, event):
        context.window.cursor_set('CROSSHAIR')
        
        if event.type == "INBETWEEN_MOUSEMOVE":
            return {'RUNNING_MODAL'}
        
        # Handle typing
        if self.handle_typing_event(event):
            self.update_header(context)
            return {'RUNNING_MODAL'}
        
        # Update snap
        if self.current_line and self.current_line.obj:
            self.current_line.obj.hide_set(True)
        self.update_snap(context, event)
        if self.current_line and self.current_line.obj:
            self.current_line.obj.hide_set(False)
        
        # Update line position
        if self.placement_state != hb_placement.PlacementState.TYPING:
            if not self.has_start_point and self.hit_location:
                # Move line origin to mouse
                self.current_line.obj.location = self.hit_location
            else:
                self._set_line_from_mouse()
        
        self.update_header(context)
        
        # Left click - place point
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if not self.has_start_point:
                self.start_point = Vector(self.hit_location) if self.hit_location else Vector((0, 0, 0))
                self.start_point.z = 0
                self.has_start_point = True
                
                # Set line start
                self.current_line.obj.location = (0, 0, 0)
                self.current_line.set_points(self.start_point, self.start_point)
            else:
                self._confirm_line()
            return {'RUNNING_MODAL'}
        
        # Right click - finish
        if event.type == 'RIGHTMOUSE' and event.value == 'PRESS':
            self.cancel_placement(context)
            hb_placement.clear_header_text(context)
            return {'FINISHED'}
        
        # Escape - cancel
        if event.type == 'ESC' and event.value == 'PRESS':
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
    bl_description = "Add a dimension annotation. Click two points, then set offset"
    bl_options = {'UNDO'}
    
    # Dimension state
    dim: hb_types.GeoNodeDimension = None
    first_point: Vector = None
    second_point: Vector = None
    click_count: int = 0
    
    def create_dimension(self, context):
        """Create dimension object."""
        self.dim = hb_types.GeoNodeDimension()
        self.dim.create("Dimension")
        self.dim.obj['IS_2D_ANNOTATION'] = True
        self.register_placement_object(self.dim.obj)
    
    def update_header(self, context):
        if self.click_count == 0:
            text = "Click first point | Right-click/Esc to cancel"
        elif self.click_count == 1:
            text = "Click second point | Right-click/Esc to cancel"
        else:
            text = "Move to set offset, then click to place | Right-click/Esc to cancel"
        
        hb_placement.draw_header_text(context, text)
    
    def execute(self, context):
        self.init_placement(context)
        
        self.dim = None
        self.first_point = None
        self.second_point = None
        self.click_count = 0
        
        self.create_dimension(context)
        
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
    
    def modal(self, context, event):
        context.window.cursor_set('CROSSHAIR')
        
        if event.type == "INBETWEEN_MOUSEMOVE":
            return {'RUNNING_MODAL'}
        
        # Update snap
        if self.dim and self.dim.obj:
            self.dim.obj.hide_set(True)
        self.update_snap(context, event)
        if self.dim and self.dim.obj:
            self.dim.obj.hide_set(False)
        
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
                cross = line_dir.x * to_hit.y - line_dir.y * to_hit.x
                if cross < 0:
                    offset = -offset
                
                self.dim.set_input("Leader Length", abs(offset))
        
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
                if self.dim.obj in self.placement_objects:
                    self.placement_objects.remove(self.dim.obj)
                hb_placement.clear_header_text(context)
                return {'FINISHED'}
            return {'RUNNING_MODAL'}
        
        # Right click / Escape - cancel
        if event.type in {'RIGHTMOUSE', 'ESC'} and event.value == 'PRESS':
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
