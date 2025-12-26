import bpy
import math
import os
from mathutils import Vector, Matrix
from bpy_extras import view3d_utils
from . import types_frameless
from . import props_hb_frameless
from ... import hb_utils, hb_project, hb_snap, hb_placement, hb_details, hb_types, units

def has_child_item_type(obj,item_type):
    for child in obj.children_recursive:
        if item_type in child:
            return True
    return False

def toggle_cabinet_color(obj,toggle,type_name="",dont_show_parent=True):
    hb_props = bpy.context.window_manager.home_builder
    add_on_prefs = hb_props.get_user_preferences(bpy.context)         

    if toggle:
        if dont_show_parent:
            if has_child_item_type(obj,type_name):
                return
        obj.color = add_on_prefs.cabinet_color
        obj.show_in_front = True
        obj.hide_viewport = False
        obj.display_type = 'SOLID'
        obj.select_set(True)

    else:
        obj.show_name = False
        obj.show_in_front = False
        if 'IS_GEONODE_CAGE' in obj:
            obj.color = [0.000000, 0.000000, 0.000000, 0.100000]
            obj.display_type = 'WIRE'
            obj.hide_viewport = True
        elif 'IS_2D_ANNOTATION' in obj:
            obj.color = add_on_prefs.annotation_color
            obj.display_type = 'SOLID'
        else:
            obj.color = [1.000000, 1.000000, 1.000000, 1.000000]
            obj.display_type = 'SOLID'
        obj.select_set(False)

class WallObjectPlacementMixin(hb_placement.PlacementMixin):
    """
    Extended placement mixin for objects placed on walls.
    Adds support for left/right offset and width input.
    """
    
    offset_from_right: bool = False
    position_locked: bool = False
    
    selected_wall = None
    wall_length: float = 0
    placement_x: float = 0
    
    def get_placed_object(self):
        raise NotImplementedError
    
    def get_placed_object_width(self) -> float:
        raise NotImplementedError
    
    def set_placed_object_width(self, width: float):
        raise NotImplementedError
    
    def get_default_typing_target(self):
        return hb_placement.TypingTarget.WIDTH
    
    def handle_typing_event(self, event) -> bool:
        if event.value == 'PRESS':
            # Intercept Enter - modal handles it as "accept placement"
            if event.type in {'RET', 'NUMPAD_ENTER'}:
                # Don't consume - let modal handle as placement accept
                return False
            
            if event.type == 'LEFT_ARROW':
                # On back side, left arrow = right offset (directions are flipped)
                if self.place_on_front:
                    self.offset_from_right = False
                    target = hb_placement.TypingTarget.OFFSET_X
                else:
                    self.offset_from_right = True
                    target = hb_placement.TypingTarget.OFFSET_RIGHT
                
                if self.placement_state == hb_placement.PlacementState.TYPING:
                    if self.typed_value:
                        self.apply_typed_value_silent()
                    self.typed_value = ""
                    self.typing_target = target
                else:
                    self.start_typing(target)
                return True
            
            if event.type == 'RIGHT_ARROW':
                # On back side, right arrow = left offset (directions are flipped)
                if self.place_on_front:
                    self.offset_from_right = True
                    target = hb_placement.TypingTarget.OFFSET_RIGHT
                else:
                    self.offset_from_right = False
                    target = hb_placement.TypingTarget.OFFSET_X
                
                if self.placement_state == hb_placement.PlacementState.TYPING:
                    if self.typed_value:
                        self.apply_typed_value_silent()
                    self.typed_value = ""
                    self.typing_target = target
                else:
                    self.start_typing(target)
                return True
            
            if event.type == 'W':
                if self.placement_state == hb_placement.PlacementState.TYPING:
                    # Accept current value before switching
                    if self.typed_value:
                        self.apply_typed_value_silent()
                    self.typed_value = ""
                    self.typing_target = hb_placement.TypingTarget.WIDTH
                else:
                    self.start_typing(hb_placement.TypingTarget.WIDTH)
                return True
            
            if event.type == 'H':
                if self.placement_state == hb_placement.PlacementState.TYPING:
                    # Accept current value before switching
                    if self.typed_value:
                        self.apply_typed_value_silent()
                    self.typed_value = ""
                    self.typing_target = hb_placement.TypingTarget.HEIGHT
                else:
                    self.start_typing(hb_placement.TypingTarget.HEIGHT)
                return True
        
        # Call base class but it will also check Enter - we need to skip that
        # Handle number keys and backspace ourselves to avoid Enter handling
        if self.placement_state == hb_placement.PlacementState.PLACING:
            if event.type in hb_placement.NUMBER_KEYS and event.value == 'PRESS':
                # Auto-start typing with WIDTH as default
                self.typing_target = hb_placement.TypingTarget.WIDTH
                self.placement_state = hb_placement.PlacementState.TYPING
                self.typed_value = hb_placement.NUMBER_KEYS[event.type]
                self.on_typed_value_changed()
                return True
        
        if self.placement_state == hb_placement.PlacementState.TYPING:
            if event.value == 'PRESS':
                # Number input
                if event.type in hb_placement.NUMBER_KEYS:
                    self.typed_value += hb_placement.NUMBER_KEYS[event.type]
                    self.on_typed_value_changed()
                    return True
                
                # Backspace
                if event.type == 'BACK_SPACE':
                    if self.typed_value:
                        self.typed_value = self.typed_value[:-1]
                        self.on_typed_value_changed()
                    else:
                        self.stop_typing()
                    return True
                
                # Escape - cancel typing
                if event.type == 'ESC':
                    self.stop_typing()
                    return True
        
        return False
    
    def apply_typed_value_silent(self):
        """Apply typed value without stopping typing mode."""
        self.apply_typed_value()
        # Re-enter typing state (apply_typed_value calls stop_typing)
        self.placement_state = hb_placement.PlacementState.TYPING
    
    def apply_typed_value(self):
        parsed = self.parse_typed_distance()
        if parsed is None:
            self.stop_typing()
            return
        
        obj = self.get_placed_object()
        if not obj:
            self.stop_typing()
            return
            
        if self.typing_target == hb_placement.TypingTarget.OFFSET_X:
            self.placement_x = parsed
            obj.location.x = parsed
            self.offset_from_right = False
            self.position_locked = True
            
        elif self.typing_target == hb_placement.TypingTarget.OFFSET_RIGHT:
            if self.selected_wall:
                obj_width = self.get_placed_object_width()
                self.placement_x = self.wall_length - parsed - obj_width
                obj.location.x = self.placement_x
            self.offset_from_right = True
            self.position_locked = True
            
        elif self.typing_target == hb_placement.TypingTarget.WIDTH:
            self.set_placed_object_width(parsed)
            if self.offset_from_right and self.selected_wall:
                self.update_position_for_width_change()
                
        elif self.typing_target == hb_placement.TypingTarget.HEIGHT:
            self.set_placed_object_height(parsed)
        
        self.stop_typing()
    
    def set_placed_object_height(self, height: float):
        pass
    
    def update_position_for_width_change(self):
        pass
    
    def on_typed_value_changed(self):
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
        unit_settings = context.scene.unit_settings
        obj_width = self.get_placed_object_width()
        
        if self.offset_from_right:
            offset_from_right = self.wall_length - self.placement_x - obj_width
            return f"Offset (→): {units.unit_to_string(unit_settings, offset_from_right)}"
        else:
            return f"Offset (←): {units.unit_to_string(unit_settings, self.placement_x)}"


class hb_frameless_OT_place_cabinet(bpy.types.Operator, WallObjectPlacementMixin):
    bl_idname = "hb_frameless.place_cabinet"
    bl_label = "Place Cabinet"
    bl_description = "Place a cabinet on a wall. Arrow keys for offset, W for width, F to fill gap, Escape to cancel"
    bl_options = {'UNDO'}

    cabinet_name: bpy.props.StringProperty(name="Cabinet Name",default="")# type: ignore

    # Cabinet type to place
    cabinet_type: bpy.props.EnumProperty(
        name="Cabinet Type",
        items=[
            ('BASE', "Base", "Base cabinet"),
            ('TALL', "Tall", "Tall cabinet"),
            ('UPPER', "Upper", "Upper cabinet"),
        ],
        default='BASE'
    )  # type: ignore

    # Preview cage (lightweight, with array modifier)
    preview_cage = None
    array_modifier = None
    
    fill_mode: bool = True
    cabinet_quantity: int = 1
    auto_quantity: bool = True
    current_gap_width: float = 0
    max_single_cabinet_width: float = 0
    individual_cabinet_width: float = 0
    
    # User-defined offsets (None means not set, use auto snap)
    left_offset: float = None  # Distance from left gap boundary
    right_offset: float = None  # Distance from right gap boundary
    
    # Current gap boundaries (detected from obstacles)
    gap_left_boundary: float = 0  # X position of left side of current gap
    gap_right_boundary: float = 0  # X position of right side of current gap
    
    # Which side of wall to place on (True = front/negative Y, False = back/positive Y)
    place_on_front: bool = True
    
    # Floor cabinet snapping
    snap_cabinet = None  # Cabinet we're snapping to
    snap_side: str = None  # 'LEFT' or 'RIGHT' side of the snap cabinet
    
    # Placement dimensions
    dim_total_width = None  # Dimension showing total cabinet width
    dim_left_offset = None  # Dimension showing left offset from gap edge
    dim_right_offset = None  # Dimension showing right offset from gap edge

    def get_placed_object(self):
        return self.preview_cage.obj if self.preview_cage else None
    
    def get_placed_object_width(self) -> float:
        """Returns the TOTAL width of all cabinets."""
        return self.individual_cabinet_width * self.cabinet_quantity
    
    def set_placed_object_width(self, width: float):
        """Set TOTAL width for all cabinets - individual width is total/quantity."""
        self.individual_cabinet_width = width / self.cabinet_quantity
        self.fill_mode = False
        self.update_preview_cage()
    
    def apply_typed_value(self):
        """Override to recalculate gap after typing offset."""
        parsed = self.parse_typed_distance()
        if parsed is None:
            self.stop_typing()
            return
        
        if not self.preview_cage:
            self.stop_typing()
            return
        
        if self.typing_target == hb_placement.TypingTarget.OFFSET_X:
            # Set left offset
            self.left_offset = parsed
            self.position_locked = True
            self.recalculate_from_offsets(bpy.context)
            
        elif self.typing_target == hb_placement.TypingTarget.OFFSET_RIGHT:
            # Set right offset
            self.right_offset = parsed
            self.position_locked = True
            self.recalculate_from_offsets(bpy.context)
            
        elif self.typing_target == hb_placement.TypingTarget.WIDTH:
            # User types TOTAL width - auto-calculate quantity based on max 36" rule
            if self.auto_quantity:
                self.cabinet_quantity = self.calculate_auto_quantity(parsed)
                self.array_modifier.count = self.cabinet_quantity
            self.individual_cabinet_width = parsed / self.cabinet_quantity
            self.fill_mode = False
            self.update_preview_cage()
                
        elif self.typing_target == hb_placement.TypingTarget.HEIGHT:
            self.preview_cage.set_input('Dim Z', parsed)
        
        self.stop_typing()
    
    def recalculate_from_offsets(self, context):
        """Recalculate quantity and width based on left and/or right offsets relative to current gap."""
        if not self.selected_wall:
            return
        
        # Use the detected gap boundaries as the reference
        # Offsets are relative to these boundaries, not the wall edges
        
        # Determine actual gap_start (left boundary + left offset)
        if self.left_offset is not None:
            gap_start = self.gap_left_boundary + self.left_offset
        else:
            gap_start = self.gap_left_boundary
        
        # Determine actual gap_end (right boundary - right offset)
        if self.right_offset is not None:
            gap_end = self.gap_right_boundary - self.right_offset
        else:
            gap_end = self.gap_right_boundary
        
        # Calculate gap
        gap_width = gap_end - gap_start
        self.current_gap_width = gap_width
        self.placement_x = gap_start
        
        if self.fill_mode and gap_width > 0:
            if self.auto_quantity:
                self.cabinet_quantity = self.calculate_auto_quantity(gap_width)
            self.individual_cabinet_width = gap_width / self.cabinet_quantity
        
        self.update_preview_cage()
        self.update_preview_position()
    
    def update_preview_position(self):
        """Update preview cage position without recalculating gap."""
        if not self.preview_cage or not self.selected_wall:
            return
        
        import math
        wall = hb_types.GeoNodeWall(self.selected_wall)
        wall_thickness = wall.get_input('Thickness')
        cabinet_depth = self.get_cabinet_depth(bpy.context)
        total_width = self.individual_cabinet_width * self.cabinet_quantity
        
        self.preview_cage.obj.parent = self.selected_wall
        self.preview_cage.obj.location.z = self.get_cabinet_z_location(bpy.context)
        
        if self.place_on_front:
            self.preview_cage.obj.location.x = self.placement_x
            self.preview_cage.obj.location.y = 0
            self.preview_cage.obj.rotation_euler = (0, 0, 0)
        else:
            self.preview_cage.obj.location.x = self.placement_x + total_width
            self.preview_cage.obj.location.y = wall_thickness
            self.preview_cage.obj.rotation_euler = (0, 0, math.pi)
    
    def set_placed_object_height(self, height: float):
        if self.preview_cage:
            self.preview_cage.set_input('Dim Z', height)

    def get_cabinet_depth(self, context) -> float:
        props = context.scene.hb_frameless
        if self.cabinet_type == 'BASE':
            return props.base_cabinet_depth
        elif self.cabinet_type == 'TALL':
            return props.tall_cabinet_depth
        elif self.cabinet_type == 'UPPER':
            return props.upper_cabinet_depth
        return props.base_cabinet_depth

    def get_cabinet_height(self, context) -> float:
        props = context.scene.hb_frameless
        if self.cabinet_type == 'BASE':
            return props.base_cabinet_height
        elif self.cabinet_type == 'TALL':
            return props.tall_cabinet_height
        elif self.cabinet_type == 'UPPER':
            return props.upper_cabinet_height
        return props.base_cabinet_height

    def get_cabinet_z_location(self, context) -> float:
        props = context.scene.hb_frameless
        if self.cabinet_type == 'UPPER':
            return props.default_wall_cabinet_location
        return 0
    
    def get_cage_center_snap(self, cursor_x: float, cabinet_width: float) -> float:
        """
        Check if cursor is over a GeoNodeCage with no height collision.
        Returns the X position to center the cabinet on that cage, or None.
        
        This is used to center a base cabinet under a window, for example.
        """
        if not self.hit_object or not self.selected_wall:
            return None
        
        # Find if hit object or its parents is a GeoNodeCage
        cage_obj = None
        current = self.hit_object
        while current and current != self.selected_wall:
            if 'IS_GEONODE_CAGE' in current:
                cage_obj = current
                break
            # Also check for window/door base points that contain cages
            if 'IS_WINDOW_BP' in current or 'IS_ENTRY_DOOR_BP' in current:
                # Find the cage child
                for child in current.children:
                    if 'IS_GEONODE_CAGE' in child:
                        cage_obj = child
                        break
                if cage_obj:
                    break
            current = current.parent
        
        if not cage_obj:
            return None
        
        # Get cage dimensions
        try:
            cage = hb_types.GeoNodeObject(cage_obj)
            cage_width = cage.get_input('Dim X')
            cage_height = cage.get_input('Dim Z')
            cage_z_start = cage_obj.location.z
            cage_z_end = cage_z_start + cage_height
        except:
            return None
        
        # Get cabinet vertical bounds
        cabinet_z_start = self.get_cabinet_z_location(bpy.context)
        cabinet_height = self.get_cabinet_height(bpy.context)
        cabinet_z_end = cabinet_z_start + cabinet_height
        
        # Check for height collision
        # Two ranges overlap if: start1 < end2 AND start2 < end1
        has_height_collision = (cabinet_z_start < cage_z_end) and (cage_z_start < cabinet_z_end)
        
        if has_height_collision:
            # There's a collision, don't snap to this cage
            return None
        
        # No height collision - calculate centered position
        # Get cage X position (handle rotation for back side placement)
        import math
        is_rotated = abs(cage_obj.rotation_euler.z - math.pi) < 0.1 or abs(cage_obj.rotation_euler.z + math.pi) < 0.1
        
        if is_rotated:
            cage_x_start = cage_obj.location.x - cage_width
        else:
            cage_x_start = cage_obj.location.x
        
        cage_center_x = cage_x_start + cage_width / 2
        
        # Return position that centers cabinet on cage
        centered_snap_x = cage_center_x - cabinet_width / 2
        return centered_snap_x

    def create_preview_cage(self, context):
        """Create a lightweight preview cage with array modifier."""
        props = context.scene.hb_frameless
        
        # Create simple cage for preview
        self.preview_cage = hb_types.GeoNodeCage()
        self.preview_cage.create('Preview')
        
        self.individual_cabinet_width = props.default_cabinet_width
        self.preview_cage.set_input('Dim X', self.individual_cabinet_width)
        self.preview_cage.set_input('Dim Y', self.get_cabinet_depth(context))
        self.preview_cage.set_input('Dim Z', self.get_cabinet_height(context))
        self.preview_cage.set_input('Mirror Y', True)
        
        # Add array modifier for quantity preview
        self.array_modifier = self.preview_cage.obj.modifiers.new(name='Quantity', type='ARRAY')
        self.array_modifier.use_relative_offset = True
        self.array_modifier.relative_offset_displace = (1, 0, 0)
        self.array_modifier.count = self.cabinet_quantity
        
        # Style the preview
        self.preview_cage.obj.display_type = 'WIRE'
        self.preview_cage.obj.show_in_front = True
        self.preview_cage.set_input('Mirror Y', True)  # Always mirror Y for proper display
        
        self.register_placement_object(self.preview_cage.obj)
    
    def create_dimensions(self, context):
        """Create dimension annotations for placement feedback."""
        # Total width dimension (above cabinets)
        self.dim_total_width = hb_types.GeoNodeDimension()
        self.dim_total_width.create("Dim_Total_Width")
        self.dim_total_width.obj.show_in_front = True
        self.register_placement_object(self.dim_total_width.obj)
        
        # Left offset dimension
        self.dim_left_offset = hb_types.GeoNodeDimension()
        self.dim_left_offset.create("Dim_Left_Offset")
        self.dim_left_offset.obj.show_in_front = True
        self.register_placement_object(self.dim_left_offset.obj)
        
        # Right offset dimension
        self.dim_right_offset = hb_types.GeoNodeDimension()
        self.dim_right_offset.create("Dim_Right_Offset")
        self.dim_right_offset.obj.show_in_front = True
        self.register_placement_object(self.dim_right_offset.obj)
    
    def cleanup_placement_objects(self):
        """Remove preview cage and dimensions."""
        if self.preview_cage and self.preview_cage.obj:
            bpy.data.objects.remove(self.preview_cage.obj, do_unlink=True)
        if self.dim_total_width and self.dim_total_width.obj:
            bpy.data.objects.remove(self.dim_total_width.obj, do_unlink=True)
        if self.dim_left_offset and self.dim_left_offset.obj:
            bpy.data.objects.remove(self.dim_left_offset.obj, do_unlink=True)
        if self.dim_right_offset and self.dim_right_offset.obj:
            bpy.data.objects.remove(self.dim_right_offset.obj, do_unlink=True)
        self.placement_objects = []
    
    def get_dimension_rotation(self, context, base_rotation_z):
        """Calculate dimension rotation to face the camera based on view angle."""

        # Get the 3D view
        region_3d = None
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                region_3d = area.spaces.active.region_3d
                break
        
        if not region_3d:
            return (0, 0, base_rotation_z)
        
        # Get view rotation matrix and extract the view direction
        view_matrix = region_3d.view_matrix
        # View direction is the negative Z axis of the view matrix (pointing into screen)
        view_dir = Vector((view_matrix[2][0], view_matrix[2][1], view_matrix[2][2]))
        
        # Check if we're looking more from above (plan view) or from the side (elevation)
        # view_dir.z close to -1 means looking straight down (plan view)
        # view_dir.z close to 0 means looking from the side (elevation view)
        
        vertical_component = abs(view_dir.z)
        
        if vertical_component > 0.7:
            # Plan view - dimension lies flat (X rotation = 0)
            return (0, 0, base_rotation_z)
        else:
            # Elevation/3D view - rotate dimension to stand up (X rotation = 90)
            return (math.radians(90), 0, base_rotation_z)
    
    def update_dimensions(self, context):
        """Update dimension positions and values."""
        if not self.preview_cage:
            return
        
        if not self.dim_total_width or not self.dim_left_offset or not self.dim_right_offset:
            return
        
        total_width = self.individual_cabinet_width * self.cabinet_quantity
        cabinet_height = self.get_cabinet_height(context)
        dim_z = cabinet_height + units.inch(4)  # Above cabinet
        
        # Never parent dimensions to wall - keep in world space
        self.dim_total_width.obj.parent = None
        self.dim_left_offset.obj.parent = None
        self.dim_right_offset.obj.parent = None
        
        if self.selected_wall:
            # Wall placement - show all three dimensions in world space
            wall = hb_types.GeoNodeWall(self.selected_wall)
            wall_thickness = wall.get_input('Thickness')
            wall_matrix = self.selected_wall.matrix_world
            wall_rotation_z = self.selected_wall.rotation_euler.z
            
            left_offset = self.placement_x - self.gap_left_boundary
            right_offset = self.gap_right_boundary - (self.placement_x + total_width)

            # Y position based on which side of wall (in local space)
            if self.place_on_front:
                dim_y = -units.inch(2)
            else:
                dim_y = wall_thickness + units.inch(2)
            
            # Get rotation based on view angle
            dim_rotation = self.get_dimension_rotation(context, wall_rotation_z)
            
            # Total width dimension - above cabinets (convert to world space)
            local_pos = Vector((self.placement_x, dim_y, dim_z))
            self.dim_total_width.obj.location = wall_matrix @ local_pos
            self.dim_total_width.obj.rotation_euler = dim_rotation
            self.dim_total_width.obj.data.splines[0].points[1].co = (total_width, 0, 0, 1)
            self.dim_total_width.obj.hide_set(False)
            
            # Left offset dimension - from gap start to cabinet start
            if left_offset > units.inch(0.5):
                local_pos = Vector((self.gap_left_boundary, dim_y, dim_z + units.inch(8)))
                self.dim_left_offset.obj.location = wall_matrix @ local_pos
                self.dim_left_offset.obj.rotation_euler = dim_rotation
                self.dim_left_offset.obj.data.splines[0].points[1].co = (left_offset, 0, 0, 1)
                self.dim_left_offset.obj.hide_set(False)
            else:
                self.dim_left_offset.obj.hide_set(True)
            
            # Right offset dimension - from cabinet end to gap end
            if right_offset > units.inch(0.5):
                local_pos = Vector((self.placement_x + total_width, dim_y, dim_z + units.inch(8)))
                self.dim_right_offset.obj.location = wall_matrix @ local_pos
                self.dim_right_offset.obj.rotation_euler = dim_rotation
                self.dim_right_offset.obj.data.splines[0].points[1].co = (right_offset, 0, 0, 1)
                self.dim_right_offset.obj.hide_set(False)
            else:
                self.dim_right_offset.obj.hide_set(True)
        else:
            # Floor placement - just show total width
            base_rotation_z = self.preview_cage.obj.rotation_euler.z
            dim_rotation = self.get_dimension_rotation(context, base_rotation_z)
            
            self.dim_total_width.obj.location = self.preview_cage.obj.location.copy()
            self.dim_total_width.obj.location.z = dim_z
            self.dim_total_width.obj.rotation_euler = dim_rotation
            self.dim_total_width.obj.data.splines[0].points[1].co = (total_width, 0, 0, 1)
            self.dim_total_width.obj.hide_set(False)
            
            # Hide offset dimensions on floor
            self.dim_left_offset.obj.hide_set(True)
            self.dim_right_offset.obj.hide_set(True)

    def update_preview_cage(self):
        """Update preview cage dimensions and array count."""
        if not self.preview_cage:
            return
        
        self.preview_cage.set_input('Dim X', self.individual_cabinet_width)
        self.array_modifier.count = self.cabinet_quantity
    
    def on_typed_value_changed(self):
        """Live preview while typing."""
        if not self.typed_value:
            return
            
        parsed = self.parse_typed_distance()
        if parsed is None:
            return
        
        if not self.preview_cage:
            return
        
        if self.typing_target == hb_placement.TypingTarget.OFFSET_X:
            if not self.selected_wall:
                return
            # Live preview of left offset (temporarily set it)
            old_left = self.left_offset
            self.left_offset = parsed
            self.recalculate_from_offsets(bpy.context)
            self.update_dimensions(bpy.context)
            self.left_offset = old_left  # Restore until accepted
            
        elif self.typing_target == hb_placement.TypingTarget.OFFSET_RIGHT:
            if not self.selected_wall:
                return
            # Live preview of right offset (temporarily set it)
            old_right = self.right_offset
            self.right_offset = parsed
            self.recalculate_from_offsets(bpy.context)
            self.update_dimensions(bpy.context)
            self.right_offset = old_right  # Restore until accepted
                
        elif self.typing_target == hb_placement.TypingTarget.WIDTH:
            # User types TOTAL width - disable fill mode so set_position_on_wall doesn't override
            self.fill_mode = False
            # Auto-calculate quantity based on max 36" rule
            if self.auto_quantity:
                new_qty = self.calculate_auto_quantity(parsed)
                if new_qty != self.cabinet_quantity:
                    self.cabinet_quantity = new_qty
                    self.array_modifier.count = self.cabinet_quantity
            self.individual_cabinet_width = parsed / self.cabinet_quantity
            self.update_preview_cage()
            self.update_preview_position()
            self.update_dimensions(bpy.context)
            
        elif self.typing_target == hb_placement.TypingTarget.HEIGHT:
            self.preview_cage.set_input('Dim Z', parsed)

    def find_placement_gap_by_side(self, wall_obj, cursor_x: float, object_width: float, 
                                     place_on_front: bool, wall_thickness: float) -> tuple:
        """
        Find the available gap at cursor position, only considering objects on the same side
        that overlap vertically with the cabinet being placed.
        Doors and windows are always considered as they cut through the entire wall.
        
        Args:
            wall_obj: The wall object
            cursor_x: Cursor X position in wall's local space
            object_width: Width of the object being placed
            place_on_front: True if placing on front side of wall
            wall_thickness: Thickness of the wall
        
        Returns (gap_start, gap_end, snap_x)
        """
        wall = hb_types.GeoNodeWall(wall_obj)
        wall_length = wall.get_input('Length')
        
        # Get the Z bounds of the cabinet being placed
        cabinet_z_start = self.get_cabinet_z_location(bpy.context)
        cabinet_height = self.get_cabinet_height(bpy.context)
        cabinet_z_end = cabinet_z_start + cabinet_height
        
        # Get all children and filter appropriately
        children = []
        for child in wall_obj.children:
            # Skip helper objects
            if child.get('obj_x'):
                continue
            # Skip the preview cage
            if self.preview_cage and child == self.preview_cage.obj:
                continue
            # Skip dimension annotations (they have IS_2D_ANNOTATION custom property)
            if child.get('IS_2D_ANNOTATION'):
                continue
            
            # Doors and windows are obstacles for BOTH sides (they cut through wall)
            is_door_or_window = 'IS_ENTRY_DOOR_BP' in child or 'IS_WINDOW_BP' in child
            
            if not is_door_or_window:
                # For cabinets/other objects, check which side they're on
                child_y = child.location.y
                child_on_front = child_y < wall_thickness / 2
                
                # Only include children on the same side
                if child_on_front != place_on_front:
                    continue
            
            # Get object vertical bounds
            child_z_start = child.location.z
            child_z_end = child_z_start
            child_width = 0
            
            if hasattr(child, 'home_builder') and child.home_builder.mod_name:
                try:
                    geo_obj = hb_types.GeoNodeObject(child)
                    child_width = geo_obj.get_input('Dim X')
                    child_height = geo_obj.get_input('Dim Z')
                    child_z_end = child_z_start + child_height
                except:
                    pass
            
            # Check for vertical overlap
            # Two ranges overlap if: start1 < end2 AND start2 < end1
            has_vertical_overlap = (cabinet_z_start < child_z_end) and (child_z_start < cabinet_z_end)
            
            if not has_vertical_overlap:
                # No vertical collision, skip this object (including doors/windows)
                continue
            
            # Get object horizontal bounds
            # Check if object is rotated 180° (back side placement)
            import math
            is_rotated = abs(child.rotation_euler.z - math.pi) < 0.1 or abs(child.rotation_euler.z + math.pi) < 0.1
            
            if is_rotated:
                # Back side: location.x is at right edge, cabinet extends left
                x_start = child.location.x - child_width
                x_end = child.location.x
            else:
                # Front side: location.x is at left edge, cabinet extends right
                x_start = child.location.x
                x_end = x_start + child_width
            
            children.append((x_start, x_end, child))
        
        # Sort by X position
        children = sorted(children, key=lambda x: x[0])
        
        if not children:
            return (0, wall_length, cursor_x)
        
        # Find which gap the cursor is in
        gap_start = 0
        gap_end = wall_length
        
        for x_start, x_end, obj in children:
            if cursor_x < x_start:
                gap_end = x_start
                break
            else:
                gap_start = x_end
        
        # Check if cursor is past all objects
        if children and cursor_x >= children[-1][1]:
            gap_start = children[-1][1]
            gap_end = wall_length
        
        # Determine snap position within gap
        gap_width = gap_end - gap_start
        
        if object_width >= gap_width:
            snap_x = gap_start
        elif cursor_x - gap_start < object_width / 2:
            snap_x = gap_start
        elif gap_end - cursor_x < object_width / 2:
            snap_x = gap_end - object_width
        else:
            snap_x = cursor_x - object_width / 2
        
        return (gap_start, gap_end, snap_x)

    def calculate_auto_quantity(self, gap_width: float) -> int:
        """Calculate how many cabinets needed so none exceed max width."""
        if gap_width <= 0:
            return 1
        if gap_width <= self.max_single_cabinet_width:
            return 1
        import math
        return math.ceil(gap_width / self.max_single_cabinet_width)

    def update_cabinet_quantity(self, context, new_quantity: int):
        """Update the number of cabinets."""
        new_quantity = max(1, new_quantity)
        if new_quantity != self.cabinet_quantity:
            self.cabinet_quantity = new_quantity
            self.update_preview_cage()

    def set_position_on_wall(self, context):
        """Position preview cage on the selected wall."""
        if not self.selected_wall or not self.preview_cage:
            return
            
        wall = hb_types.GeoNodeWall(self.selected_wall)
        self.wall_length = wall.get_input('Length')
        wall_thickness = wall.get_input('Thickness')
        cabinet_depth = self.get_cabinet_depth(context)
        
        # Get local position on wall from world hit location
        world_loc = Vector(self.hit_location)
        local_loc = self.selected_wall.matrix_world.inverted() @ world_loc
        cursor_x = local_loc.x
        cursor_y = local_loc.y
        
        # Determine which side of wall based on cursor Y position
        # Wall mesh extends from Y=0 (front face) to Y=thickness (back face)
        self.place_on_front = cursor_y < wall_thickness / 2
        
        # Find available gap, filtering by which side we're placing on
        gap_start, gap_end, snap_x = self.find_placement_gap_by_side(
            self.selected_wall, 
            cursor_x, 
            self.individual_cabinet_width,
            self.place_on_front,
            wall_thickness
        )
        
        # Store gap boundaries for offset calculations
        self.gap_left_boundary = gap_start
        self.gap_right_boundary = gap_end
        
        gap_width = gap_end - gap_start
        self.current_gap_width = gap_width
        
        # If fill_mode (user hasn't typed a width), auto-calculate quantity and fill gap
        if self.fill_mode and gap_width > 0:
            if self.auto_quantity:
                new_qty = self.calculate_auto_quantity(gap_width)
                if new_qty != self.cabinet_quantity:
                    self.cabinet_quantity = new_qty
                    self.array_modifier.count = self.cabinet_quantity
            self.individual_cabinet_width = gap_width / self.cabinet_quantity
            snap_x = gap_start
        else:
            # User has typed a width - check for auto-snap positions
            total_width = self.individual_cabinet_width * self.cabinet_quantity
            left_gap = snap_x - gap_start
            
            # Check if cursor is over a GeoNodeCage with no height collision (e.g., window)
            cage_center_snap = self.get_cage_center_snap(cursor_x, total_width)
            
            if cage_center_snap is not None:
                # Snap to center on the cage (e.g., center base cabinet under window)
                snap_x = cage_center_snap
            else:
                # Calculate centered position in gap
                centered_x = gap_start + (gap_width - total_width) / 2
                distance_from_center = abs(snap_x - centered_x)
                
                # Snap to center if cursor is within 4 inches of center position
                if distance_from_center < units.inch(4):
                    snap_x = centered_x
                # Snap to left if within 4 inches of left boundary
                elif left_gap < units.inch(4) and left_gap > 0:
                    snap_x = gap_start
        
        # Update preview cage
        self.preview_cage.set_input('Dim X', self.individual_cabinet_width)
        
        # Clamp snap_x to wall bounds
        total_width = self.individual_cabinet_width * self.cabinet_quantity
        snap_x = max(0, min(snap_x, self.wall_length - total_width))
        
        self.placement_x = snap_x
        
        # Position preview based on which side of wall
        self.preview_cage.obj.parent = self.selected_wall
        self.preview_cage.obj.location.z = self.get_cabinet_z_location(context)
        
        if self.place_on_front:
            # Front side - cabinet back against wall (Y = 0), no rotation
            self.preview_cage.obj.location.x = snap_x
            self.preview_cage.obj.location.y = 0
            self.preview_cage.obj.rotation_euler = (0, 0, 0)
        else:
            # Back side - rotated 180° around Z axis
            # Cabinet origin is back-left, so when rotated 180°:
            # - Need to offset X by width (since it rotates around origin)
            # - Y at wall_thickness (cabinet back against wall back)
            import math
            self.preview_cage.obj.location.x = snap_x + total_width
            self.preview_cage.obj.location.y = wall_thickness
            self.preview_cage.obj.rotation_euler = (0, 0, math.pi)
        
        # Update dimensions
        self.update_dimensions(context)

    def find_cabinet_bp(self, obj):
        """Find the cabinet base point (cage) from any child object."""
        if obj is None:
            return None
        
        # Check the object itself
        if 'IS_FRAMELESS_CABINET_CAGE' in obj:
            return obj
        
        # Walk up parent hierarchy (but stop at walls)
        current = obj
        while current:
            if 'IS_WALL_BP' in current:
                return None  # Don't snap to wall-parented cabinets from floor mode
            if 'IS_FRAMELESS_CABINET_CAGE' in current:
                return current
            current = current.parent
        
        return None
    
    def set_position_free(self):
        """Position cabinet(s) on the floor, snapping to nearby cabinets."""
        if not self.preview_cage or not self.hit_location:
            return
        
        import math
        
        # Reset snap state
        self.snap_cabinet = None
        self.snap_side = None
        
        # Try to find a cabinet from what we hit
        snap_target = None
        if self.hit_object:
            snap_target = self.find_cabinet_bp(self.hit_object)
        
        # Make sure we don't snap to ourselves
        if snap_target and snap_target != self.preview_cage.obj:
            try:
                snap_cab = hb_types.GeoNodeObject(snap_target)
                snap_width = snap_cab.get_input('Dim X')
                
                # Transform hit location to cabinet's local space
                local_hit = snap_target.matrix_world.inverted() @ Vector(self.hit_location)
                
                # Determine which side based on local X position
                if local_hit.x < snap_width / 2:
                    self.snap_side = 'LEFT'
                else:
                    self.snap_side = 'RIGHT'
                
                self.snap_cabinet = snap_target
            except:
                pass
        
        if self.snap_cabinet:
            self.position_snapped_to_cabinet()
        else:
            # Free placement on floor
            self.preview_cage.obj.parent = None
            self.preview_cage.obj.location = Vector(self.hit_location)
            if self.cabinet_type == 'UPPER':
                self.preview_cage.obj.location.z = self.get_cabinet_z_location(bpy.context)
            else:
                self.preview_cage.obj.location.z = 0
            self.preview_cage.obj.rotation_euler = (0, 0, 0)
        
        # Reset gap boundaries for floor placement
        self.gap_left_boundary = 0
        self.gap_right_boundary = self.individual_cabinet_width * self.cabinet_quantity
        self.current_gap_width = self.gap_right_boundary
        
        # Update dimensions
        self.update_dimensions(bpy.context)
    
    def position_snapped_to_cabinet(self):
        """Position preview cage snapped to an existing cabinet."""

        if not self.snap_cabinet or not self.preview_cage:
            return
        
        try:
            snap_cab = hb_types.GeoNodeObject(self.snap_cabinet)
            snap_width = snap_cab.get_input('Dim X')
        except:
            return
        
        # Get the snap cabinet's rotation
        snap_rotation = self.snap_cabinet.rotation_euler.z
        
        # Calculate total width of cabinets being placed
        total_width = self.individual_cabinet_width * self.cabinet_quantity
        
        # Position based on which side we're snapping to
        if self.snap_side == 'LEFT':
            # Place to the left of snap cabinet - our right edge meets their left edge
            local_offset = Vector((-total_width, 0, 0))
        else:
            # Place to the right of snap cabinet - our left edge meets their right edge
            local_offset = Vector((snap_width, 0, 0))
        
        # Transform offset to world space using snap cabinet's rotation
        rotation_matrix = Matrix.Rotation(snap_rotation, 4, 'Z')
        world_offset = rotation_matrix @ local_offset
        
        # Set position and rotation to match snap cabinet
        self.preview_cage.obj.parent = None
        self.preview_cage.obj.location = self.snap_cabinet.location + world_offset
        
        if self.cabinet_type == 'UPPER':
            self.preview_cage.obj.location.z = self.get_cabinet_z_location(bpy.context)
        else:
            self.preview_cage.obj.location.z = self.snap_cabinet.location.z
        
        self.preview_cage.obj.rotation_euler = self.snap_cabinet.rotation_euler

    def assign_door_styles_to_cabinet(self, cabinet_obj):
        """Assign the active door style to all fronts in a cabinet.
        
        Should be called after drivers have calculated final sizes.
        """
        from . import props_hb_frameless
        
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        
        # Ensure at least one door style exists
        if len(props.door_styles) == 0:
            # Create default Slab door style
            new_style = props.door_styles.add()
            new_style.name = "Slab"
            new_style.door_type = 'SLAB'
            props.active_door_style_index = 0
        
        # Get active door style
        style_index = props.active_door_style_index
        if style_index >= len(props.door_styles):
            style_index = 0
        style = props.door_styles[style_index]
        
        # Find all fronts in the cabinet hierarchy and assign style
        for obj in cabinet_obj.children_recursive:
            if obj.get('IS_DOOR_FRONT') or obj.get('IS_DRAWER_FRONT'):
                obj['DOOR_STYLE_INDEX'] = style_index
                style.assign_style_to_front(obj)

    def get_cabinet_class(self):
        if self.cabinet_type == 'BASE':
            cabinet = types_frameless.BaseCabinet()
            if self.cabinet_name == 'Base Door':
                cabinet.default_exterior = "Doors"
            elif self.cabinet_name == 'Base Door Drw':
                cabinet.default_exterior = "Door Drawer"
            elif self.cabinet_name == 'Base Drawer':
                cabinet.default_exterior = "3 Drawers"
        elif self.cabinet_type == 'TALL':
            cabinet = types_frameless.TallCabinet()
        elif self.cabinet_type == 'UPPER':
            cabinet = types_frameless.UpperCabinet()
        else:
            cabinet = types_frameless.Cabinet()    
        return cabinet    

    def create_final_cabinets(self, context):
        """Create the actual cabinet objects when user confirms placement."""
        cabinets = []
        cabinet_depth = self.get_cabinet_depth(context)
        
        if self.selected_wall:
            # Wall placement
            wall = hb_types.GeoNodeWall(self.selected_wall)
            wall_thickness = wall.get_input('Thickness')
            current_x = self.placement_x
            z_loc = self.get_cabinet_z_location(context)
            
            for i in range(self.cabinet_quantity):
                cabinet = self.get_cabinet_class()
                cabinet.width = self.individual_cabinet_width
                cabinet.height = self.get_cabinet_height(context)
                cabinet.depth = cabinet_depth
                cabinet.create(f'Cabinet')
                
                # Add doors
                # doors = types_frameless.Doors()
                # cabinet.add_cage_to_bay(doors)
                
                # Position based on which side of wall
                cabinet.obj.parent = self.selected_wall
                cabinet.obj.location.z = z_loc
                
                if self.place_on_front:
                    cabinet.obj.location.x = current_x
                    cabinet.obj.location.y = 0
                    cabinet.obj.rotation_euler = (0, 0, 0)
                else:
                    # Back side - rotated 180° around Z
                    cabinet.obj.location.x = current_x + self.individual_cabinet_width
                    cabinet.obj.location.y = wall_thickness
                    cabinet.obj.rotation_euler = (0, 0, math.pi)
                
                cabinets.append(cabinet)
                current_x += self.individual_cabinet_width
        else:
            # Floor placement (free or snapped)

            start_loc = self.preview_cage.obj.location.copy()
            rotation = self.preview_cage.obj.rotation_euler.copy()
            rotation_z = rotation.z
            
            for i in range(self.cabinet_quantity):
                cabinet = self.get_cabinet_class()
                cabinet.width = self.individual_cabinet_width
                cabinet.height = self.get_cabinet_height(context)
                cabinet.depth = cabinet_depth
                cabinet.create(f'Cabinet')
                
                # Add doors
                # doors = types_frameless.Doors()
                # cabinet.add_cage_to_bay(doors)
                
                # Calculate offset for this cabinet in the row
                # Offset in local X direction based on rotation
                local_offset = Vector((i * self.individual_cabinet_width, 0, 0))
                rotation_matrix = Matrix.Rotation(rotation_z, 4, 'Z')
                world_offset = rotation_matrix @ local_offset
                
                # Position on floor
                cabinet.obj.parent = None
                cabinet.obj.location = start_loc + world_offset
                cabinet.obj.rotation_euler = rotation
                
                # Base cabinets on floor
                if self.cabinet_type == 'UPPER':
                    cabinet.obj.location.z = self.get_cabinet_z_location(context)
                else:
                    cabinet.obj.location.z = start_loc.z
                
                cabinets.append(cabinet)
        
        return cabinets

    def update_header(self, context):
        """Update header text with instructions."""
        unit_settings = context.scene.unit_settings
        
        if self.placement_state == hb_placement.PlacementState.TYPING:
            target_name = {
                hb_placement.TypingTarget.OFFSET_X: "Gap Offset (←)",
                hb_placement.TypingTarget.OFFSET_RIGHT: "Gap Offset (→)",
                hb_placement.TypingTarget.WIDTH: "Width",
                hb_placement.TypingTarget.HEIGHT: "Height",
            }.get(self.typing_target, "Value")
            text = f"{target_name}: {self.typed_value}_ | ↑/↓ qty | ←/→ offset | Enter place | Esc cancel"
        elif self.selected_wall:
            # Show which side of wall
            side_str = "Front" if self.place_on_front else "Back"
            
            # Show both offsets if set
            offset_parts = []
            if self.left_offset is not None:
                offset_parts.append(f"←{units.unit_to_string(unit_settings, self.left_offset)}")
            if self.right_offset is not None:
                offset_parts.append(f"→{units.unit_to_string(unit_settings, self.right_offset)}")
            
            if offset_parts:
                offset_str = " | ".join(offset_parts)
            else:
                offset_str = self.get_offset_display(context)
            
            # Show total width and individual width
            total_width = self.individual_cabinet_width * self.cabinet_quantity
            total_str = units.unit_to_string(unit_settings, total_width)
            individual_str = units.unit_to_string(unit_settings, self.individual_cabinet_width)
            qty_str = f"{self.cabinet_quantity}"
            gap_str = f"Gap: {units.unit_to_string(unit_settings, self.gap_right_boundary - self.gap_left_boundary)}"
            text = f"{side_str} | {gap_str} | {offset_str} | {qty_str} × {individual_str} = {total_str} | ↑/↓ qty | ←/→ offset | Enter place | Esc cancel"
        else:
            # Floor placement
            unit_settings = context.scene.unit_settings
            total_width = self.individual_cabinet_width * self.cabinet_quantity
            total_str = units.unit_to_string(unit_settings, total_width)
            individual_str = units.unit_to_string(unit_settings, self.individual_cabinet_width)
            qty_str = f"{self.cabinet_quantity}"
            if self.snap_cabinet:
                snap_str = f"Snap {self.snap_side}"
                text = f"Floor | {snap_str} | {qty_str} × {individual_str} = {total_str} | ↑/↓ qty | Click place | Esc cancel"
            else:
                text = f"Floor | {qty_str} × {individual_str} = {total_str} | ↑/↓ qty | Click place | Esc cancel"
        
        hb_placement.draw_header_text(context, text)

    def execute(self, context):
        self.init_placement(context)
        
        self.preview_cage = None
        self.array_modifier = None
        self.selected_wall = None
        self.wall_length = 0
        self.placement_x = 0
        self.offset_from_right = False
        self.position_locked = False
        self.fill_mode = context.scene.hb_frameless.fill_cabinets
        self.cabinet_quantity = 1
        self.auto_quantity = True
        self.current_gap_width = 0
        self.max_single_cabinet_width = units.inch(36)
        self.individual_cabinet_width = context.scene.hb_frameless.default_cabinet_width
        self.left_offset = None
        self.right_offset = None
        self.gap_left_boundary = 0
        self.gap_right_boundary = 0
        self.place_on_front = True
        self.snap_cabinet = None
        self.snap_side = None
        self.dim_total_width = None
        self.dim_left_offset = None
        self.dim_right_offset = None

        self.create_preview_cage(context)
        self.create_dimensions(context)

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        context.window.cursor_set('CROSSHAIR')

        if event.type == "INBETWEEN_MOUSEMOVE":
            return {'RUNNING_MODAL'}

        # Up/Down arrows to change quantity (disables auto-quantity)
        if event.type == 'UP_ARROW' and event.value == 'PRESS':
            # Accept any typed value first
            if self.placement_state == hb_placement.PlacementState.TYPING and self.typed_value:
                self.apply_typed_value()
            self.auto_quantity = False  # User is manually setting quantity
            self.update_cabinet_quantity(context, self.cabinet_quantity + 1)
            self.position_locked = False
            return {'RUNNING_MODAL'}
        
        if event.type == 'DOWN_ARROW' and event.value == 'PRESS':
            # Accept any typed value first
            if self.placement_state == hb_placement.PlacementState.TYPING and self.typed_value:
                self.apply_typed_value()
            self.auto_quantity = False  # User is manually setting quantity
            self.update_cabinet_quantity(context, self.cabinet_quantity - 1)
            self.position_locked = False
            return {'RUNNING_MODAL'}

        # Let mixin handle typing events
        if self.handle_typing_event(event):
            self.update_header(context)
            return {'RUNNING_MODAL'}

        # Update snap (hide preview and dimensions during raycast and position calculation)
        self.preview_cage.obj.hide_set(True)
        if self.dim_total_width:
            self.dim_total_width.obj.hide_set(True)
        if self.dim_left_offset:
            self.dim_left_offset.obj.hide_set(True)
        if self.dim_right_offset:
            self.dim_right_offset.obj.hide_set(True)
        
        self.update_snap(context, event)
        
        self.preview_cage.obj.hide_set(False)

        # Check if we're over a wall (or a child of a wall like a window)
        self.selected_wall = None
        if self.hit_object:
            # Walk up parent hierarchy to find wall
            current = self.hit_object
            while current:
                if 'IS_WALL_BP' in current:
                    self.selected_wall = current
                    wall = hb_types.GeoNodeWall(self.selected_wall)
                    self.wall_length = wall.get_input('Length')
                    break
                current = current.parent

        # Update position if not locked
        # Allow position updates while typing WIDTH (but not offsets)
        typing_allows_movement = (
            self.placement_state != hb_placement.PlacementState.TYPING or
            self.typing_target == hb_placement.TypingTarget.WIDTH or
            self.typing_target == hb_placement.TypingTarget.HEIGHT
        )
        
        if typing_allows_movement:
            if self.selected_wall:
                if not self.position_locked:
                    self.set_position_on_wall(context)
            else:
                self.set_position_free()
                self.position_locked = False

        # Show dimensions after position calculation (they were hidden for raycast)
        self.update_dimensions(context)
        
        self.update_header(context)

        # Left click or Enter - create actual cabinets and place them
        if (event.type == 'LEFTMOUSE' and event.value == 'PRESS') or (event.type in {'RET', 'NUMPAD_ENTER'} and event.value == 'PRESS'):
            # Accept any typed value first
            if self.placement_state == hb_placement.PlacementState.TYPING and self.typed_value:
                self.apply_typed_value()
            
            # Create the real cabinets (on wall or floor)
            cabinets = self.create_final_cabinets(context)
            for cabinet in cabinets:
                # Assign the active cabinet style to the cabinet
                bpy.ops.hb_frameless.assign_cabinet_style(cabinet_name=cabinet.obj.name)
                # Apply toggle mode for display
                bpy.ops.hb_frameless.toggle_mode(search_obj_name=cabinet.obj.name)
                # Force driver update for grandchild objects (workaround for Blender bug #133392)
                hb_utils.run_calc_fix(context, cabinet.obj)
                # Assign door styles to all fronts (after drivers have calculated sizes)
                self.assign_door_styles_to_cabinet(cabinet.obj)
            # Remove preview cage and dimensions
            self.cleanup_placement_objects()
            
            hb_placement.clear_header_text(context)
            context.window.cursor_set('DEFAULT')
            return {'FINISHED'}

        # Right click or Escape - cancel
        if event.type in {'RIGHTMOUSE', 'ESC'} and event.value == 'PRESS':
            self.cleanup_placement_objects()
            hb_placement.clear_header_text(context)
            context.window.cursor_set('DEFAULT')
            return {'CANCELLED'}

        if hb_snap.event_is_pass_through(event):
            return {'PASS_THROUGH'}

        return {'RUNNING_MODAL'}


class hb_frameless_OT_toggle_mode(bpy.types.Operator):
    """Toggle Cabinet Openings"""
    bl_idname = "hb_frameless.toggle_mode"
    bl_label = 'Toggle Mode'
    bl_description = "This will toggle the cabinet mode"

    search_obj_name: bpy.props.StringProperty(name="Search Object Name",default="")# type: ignore
    toggle_type: bpy.props.StringProperty(name="Toggle Type",default="")# type: ignore
    toggle_on: bpy.props.BoolProperty(name="Toggle On",default=False)# type: ignore

    def toggle_obj(self,obj):
        if 'IS_WALL_BP' in obj or 'IS_ENTRY_DOOR_BP' in obj or 'IS_WINDOW_BP' in obj:
            return        
        if self.toggle_type in obj:
            toggle_cabinet_color(obj,True,type_name=self.toggle_type)
        else:
            toggle_cabinet_color(obj,False,type_name=self.toggle_type)

    def execute(self, context):
        props = context.scene.hb_frameless
        if props.frameless_selection_mode == 'Cabinets':
            self.toggle_type="IS_FRAMELESS_CABINET_CAGE"
        elif props.frameless_selection_mode == 'Bays':
            self.toggle_type="IS_FRAMELESS_BAY_CAGE"            
        elif props.frameless_selection_mode == 'Openings':
            self.toggle_type="IS_FRAMELESS_OPENING_CAGE"
        elif props.frameless_selection_mode == 'Interiors':
            self.toggle_type="IS_FRAMELESS_INTERIOR_PART"
        elif props.frameless_selection_mode == 'Parts':
            self.toggle_type="NO_TYPE"      

        if self.search_obj_name in bpy.data.objects:
            obj = bpy.data.objects[self.search_obj_name]
            self.toggle_obj(obj)
            for child in obj.children_recursive:
                self.toggle_obj(child)
        else:
            for obj in context.scene.objects:
                self.toggle_obj(obj)
        bpy.ops.object.select_all(action='DESELECT')
        return {'FINISHED'}


class hb_frameless_OT_draw_cabinet(bpy.types.Operator):
    """Legacy operator - redirects to place_cabinet"""
    bl_idname = "hb_frameless.draw_cabinet"
    bl_label = "Draw Cabinet"

    cabinet_name: bpy.props.StringProperty(name="Cabinet Name")  # type: ignore

    def execute(self, context):
        # Map cabinet names to types
        type_map = {
            'Base': 'BASE',
            'Tall': 'TALL',
            'Upper': 'UPPER',
        }
        cabinet_type = type_map.get(self.cabinet_name, 'BASE')
        bpy.ops.hb_frameless.place_cabinet('INVOKE_DEFAULT', cabinet_type=cabinet_type, cabinet_name=self.cabinet_name)
        return {'FINISHED'}


class hb_frameless_OT_update_toe_kick_prompts(bpy.types.Operator):
    bl_idname = "hb_frameless.update_toe_kick_prompts"
    bl_label = "Update Toe Kick Prompts"

    def execute(self, context):
        frameless_props = context.scene.hb_frameless
        for obj in context.scene.objects:
            if 'Toe Kick Height' in obj:
                obj['Toe Kick Height'] = frameless_props.default_toe_kick_height
            if 'Toe Kick Setback' in obj:
                obj['Toe Kick Setback'] = frameless_props.default_toe_kick_setback  
            hb_utils.run_calc_fix(context,obj)              
        return {'FINISHED'}


class hb_frameless_OT_update_base_top_construction_prompts(bpy.types.Operator):
    bl_idname = "hb_frameless.update_base_top_construction_prompts"
    bl_label = "Update Base Top Construction Prompts"

    def execute(self, context):
        print('TODO: Update Base Top Construction Prompts')
        return {'FINISHED'}


class hb_frameless_OT_update_drawer_front_height_prompts(bpy.types.Operator):
    bl_idname = "hb_frameless.update_drawer_front_height_prompts"
    bl_label = "Update Drawer Front Height Prompts"

    def execute(self, context):
        print('TODO: Update Drawer Front Height Prompts')
        return {'FINISHED'}


class hb_frameless_OT_update_door_and_drawer_front_style(bpy.types.Operator):
    """Update all door and drawer fronts with the selected door style"""
    bl_idname = "hb_frameless.update_door_and_drawer_front_style"
    bl_label = "Update Door and Drawer Front Style"
    bl_options = {'REGISTER', 'UNDO'}

    selected_index: bpy.props.IntProperty(name="Selected Index", default=-1)# type: ignore

    def execute(self, context):
        main_scene = hb_project.get_main_scene()
        frameless_props = main_scene.hb_frameless

        if self.selected_index < 0 or self.selected_index >= len(frameless_props.door_styles):
            self.report({'WARNING'}, "Invalid door style index")
            return {'CANCELLED'}

        selected_door_style = frameless_props.door_styles[self.selected_index]
        success_count = 0
        skip_count = 0

        for obj in context.scene.objects:
            if 'IS_DOOR_FRONT' in obj or 'IS_DRAWER_FRONT' in obj:
                result = selected_door_style.assign_style_to_front(obj)
                if result == True:
                    success_count += 1
                else:
                    skip_count += 1

        if skip_count > 0:
            self.report({'WARNING'}, f"Updated {success_count} front(s), skipped {skip_count} (too small for style)")
        else:
            self.report({'INFO'}, f"Updated {success_count} front(s) with style '{selected_door_style.name}'")
        return {'FINISHED'}


class hb_frameless_OT_update_cabinet_sizes(bpy.types.Operator):
    bl_idname = "hb_frameless.update_cabinet_sizes"
    bl_label = "Update Cabinet Sizes"

    def execute(self, context):
        props = context.scene.hb_frameless
        return {'FINISHED'}


class hb_frameless_OT_create_cabinet_group(bpy.types.Operator):
    bl_idname = "hb_frameless.create_cabinet_group"
    bl_label = "Create Cabinet Group"
    bl_description = "This will create a cabinet group for all of the selected cabinets"

    def execute(self, context):
        # Get Selected Cabinets
        selected_cabinets = []
        for obj in context.selected_objects:
            if 'IS_FRAMELESS_CABINET_CAGE' in obj:
                cabinet_cage = types_frameless.Cabinet(obj)
                selected_cabinets.append(cabinet_cage)
        
        if not selected_cabinets:
            self.report({'WARNING'}, "No cabinets selected")
            return {'CANCELLED'}
        
        # Find overall size and base point for new group
        base_point_location, base_point_rotation, overall_width, overall_depth, overall_height = \
            self.calculate_group_bounds(selected_cabinets)

        # Create Cabinet Group
        cabinet_group = types_frameless.Cabinet()
        cabinet_group.create("New Cabinet Group")
        cabinet_group.obj['IS_CAGE_GROUP'] = True
        cabinet_group.obj.parent = None
        cabinet_group.obj.location = base_point_location
        cabinet_group.obj.rotation_euler = base_point_rotation
        cabinet_group.set_input('Dim X', overall_width)
        cabinet_group.set_input('Dim Y', overall_depth)
        cabinet_group.set_input('Dim Z', overall_height)
        cabinet_group.set_input('Mirror Y', True)
        
        bpy.ops.object.select_all(action='DESELECT')

        # Reparent all selected cabinets to the new group
        # We need to preserve their world position while changing parent
        for selected_cabinet in selected_cabinets:
            # Store world matrix before reparenting
            world_matrix = selected_cabinet.obj.matrix_world.copy()
            
            # Set new parent
            selected_cabinet.obj.parent = cabinet_group.obj
            
            # Restore world position by calculating new local matrix
            selected_cabinet.obj.matrix_world = world_matrix
        
        cabinet_group.obj.select_set(True)
        context.view_layer.objects.active = cabinet_group.obj

        bpy.ops.hb_frameless.select_cabinet_group(toggle_on=True,cabinet_group_name=cabinet_group.obj.name)

        return {'FINISHED'}
    
    def calculate_group_bounds(self, selected_cabinets):
        """
        Calculate the overall bounds of selected cabinets in world space.
        Works for kitchen islands with cabinets at any rotation (0°, 90°, 180°, 270°).
        
        Cabinet coordinate system:
        - Origin at back-left-bottom
        - Dim X extends in +X (local)
        - Dim Y is MIRRORED, extends in -Y (local) toward front
        - Dim Z extends in +Z (local)
        
        Returns (location, rotation, width, depth, height)
        Location is at back-left-bottom of the world-space bounding box.
        """

        if not selected_cabinets:
            return (Vector((0, 0, 0)), (0, 0, 0), 0, 0, 0)
        
        # Initialize world-space bounds
        min_x = float('inf')
        max_x = float('-inf')
        min_y = float('inf')
        max_y = float('-inf')
        min_z = float('inf')
        max_z = float('-inf')
        
        for cabinet in selected_cabinets:
            # Get cabinet dimensions
            cab_width = cabinet.get_input('Dim X')
            cab_depth = cabinet.get_input('Dim Y')
            cab_height = cabinet.get_input('Dim Z')
            
            # Define the 8 corners in cabinet's LOCAL space
            # Y is mirrored, so depth extends in -Y direction
            local_corners = [
                Vector((0, 0, 0)),                    # back-left-bottom (origin)
                Vector((cab_width, 0, 0)),            # back-right-bottom
                Vector((0, -cab_depth, 0)),           # front-left-bottom
                Vector((cab_width, -cab_depth, 0)),   # front-right-bottom
                Vector((0, 0, cab_height)),           # back-left-top
                Vector((cab_width, 0, cab_height)),   # back-right-top
                Vector((0, -cab_depth, cab_height)),  # front-left-top
                Vector((cab_width, -cab_depth, cab_height)),  # front-right-top
            ]
            
            # Transform each corner to world space using cabinet's full matrix
            world_matrix = cabinet.obj.matrix_world
            for local_corner in local_corners:
                world_corner = world_matrix @ local_corner
                min_x = min(min_x, world_corner.x)
                max_x = max(max_x, world_corner.x)
                min_y = min(min_y, world_corner.y)
                max_y = max(max_y, world_corner.y)
                min_z = min(min_z, world_corner.z)
                max_z = max(max_z, world_corner.z)
        
        # Calculate overall dimensions
        overall_width = max_x - min_x
        overall_depth = max_y - min_y
        overall_height = max_z - min_z
        
        # Group cage location: back-left-bottom of world AABB
        # Since group cage also has mirrored Y, origin is at back (max_y), not front (min_y)
        base_point_location = Vector((min_x, max_y, min_z))
        
        # Group rotation is (0, 0, 0) since we're using world-space AABB
        base_point_rotation = (0, 0, 0)
        
        return (base_point_location, base_point_rotation, overall_width, overall_depth, overall_height)


class hb_frameless_OT_add_door_style(bpy.types.Operator):
    """Add a new door style"""
    bl_idname = "hb_frameless.add_door_style"
    bl_label = "Add Door Style"
    bl_description = "Add a new door style"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        
        # Create new style
        style = props.door_styles.add()
        
        # Generate unique name
        base_name = "Door Style"
        existing_names = [s.name for s in props.door_styles]
        counter = len(props.door_styles)
        while f"{base_name} {counter}" in existing_names:
            counter += 1
        style.name = f"{base_name} {counter}"
        
        # Set as active
        props.active_door_style_index = len(props.door_styles) - 1
        
        self.report({'INFO'}, f"Added door style: {style.name}")
        return {'FINISHED'}


class hb_frameless_OT_remove_door_style(bpy.types.Operator):
    """Remove the selected door style"""
    bl_idname = "hb_frameless.remove_door_style"
    bl_label = "Remove Door Style"
    bl_description = "Remove the selected door style (at least one style must remain)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        return len(props.door_styles) > 1

    def execute(self, context):
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        
        if len(props.door_styles) <= 1:
            self.report({'WARNING'}, "Cannot remove the last door style")
            return {'CANCELLED'}
        
        index = props.active_door_style_index
        style_name = props.door_styles[index].name
        
        # Remove the style
        props.door_styles.remove(index)
        
        # Adjust active index
        if props.active_door_style_index >= len(props.door_styles):
            props.active_door_style_index = len(props.door_styles) - 1
        
        # Update any fronts that referenced this style
        for scene in bpy.data.scenes:
            for obj in scene.objects:
                if obj.get('IS_DOOR_FRONT') or obj.get('IS_DRAWER_FRONT'):
                    front_style_index = obj.get('DOOR_STYLE_INDEX', 0)
                    if front_style_index == index:
                        obj['DOOR_STYLE_INDEX'] = 0
                    elif front_style_index > index:
                        obj['DOOR_STYLE_INDEX'] = front_style_index - 1
        
        self.report({'INFO'}, f"Removed door style: {style_name}")
        return {'FINISHED'}


class hb_frameless_OT_duplicate_door_style(bpy.types.Operator):
    """Duplicate the selected door style"""
    bl_idname = "hb_frameless.duplicate_door_style"
    bl_label = "Duplicate Door Style"
    bl_description = "Create a copy of the selected door style"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        return len(props.door_styles) > 0

    def execute(self, context):
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        
        if not props.door_styles:
            return {'CANCELLED'}
        
        source = props.door_styles[props.active_door_style_index]
        
        # Create new style
        new_style = props.door_styles.add()
        new_style.name = f"{source.name} Copy"
        
        # Copy all properties
        new_style.door_type = source.door_type
        new_style.panel_material = source.panel_material
        new_style.stile_width = source.stile_width
        new_style.rail_width = source.rail_width
        new_style.add_mid_rail = source.add_mid_rail
        new_style.center_mid_rail = source.center_mid_rail
        new_style.mid_rail_width = source.mid_rail_width
        new_style.mid_rail_location = source.mid_rail_location
        new_style.panel_thickness = source.panel_thickness
        new_style.panel_inset = source.panel_inset
        new_style.edge_profile_type = source.edge_profile_type
        new_style.outside_profile = source.outside_profile
        new_style.inside_profile = source.inside_profile
        
        # Set as active
        props.active_door_style_index = len(props.door_styles) - 1
        
        self.report({'INFO'}, f"Duplicated door style: {new_style.name}")
        return {'FINISHED'}


class hb_frameless_OT_assign_door_style_to_selected_fronts(bpy.types.Operator):
    """Paint door style onto fronts - click doors/drawers to assign the active style"""
    bl_idname = "hb_frameless.assign_door_style_to_selected_fronts"
    bl_label = "Paint Door Style"
    bl_description = "Click on door or drawer fronts to assign the active door style. Right-click or ESC to finish"
    bl_options = {'REGISTER', 'UNDO'}

    # Track state
    hovered_front = None
    assigned_count: int = 0
    style_name: str = ""
    style_index: int = 0
    
    # Store original object state for restoration
    original_states = {}

    @classmethod
    def poll(cls, context):
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        return len(props.door_styles) > 0

    def get_front_under_mouse(self, context, event):
        """Ray cast to find door/drawer front under mouse cursor."""
        region = context.region
        rv3d = context.region_data
        
        if not region or not rv3d:
            return None
        
        coord = (event.mouse_region_x, event.mouse_region_y)
        view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
        ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
        
        depsgraph = context.evaluated_depsgraph_get()
        result, location, normal, index, obj, matrix = context.scene.ray_cast(
            depsgraph, ray_origin, view_vector
        )
        
        if result and obj:
            current = obj
            while current:
                if current.get('IS_DOOR_FRONT') or current.get('IS_DRAWER_FRONT'):
                    return current
                current = current.parent
        
        return None

    def highlight_front(self, obj, highlight=True):
        """Highlight or unhighlight a front by selecting it."""
        if highlight:
            if obj.name not in self.original_states:
                self.original_states[obj.name] = {
                    'selected': obj.select_get(),
                }
            obj.select_set(True)
        else:
            if obj.name in self.original_states:
                state = self.original_states[obj.name]
                obj.select_set(state['selected'])

    def update_header(self, context):
        """Update header text with current status."""
        text = f"Door Style: '{self.style_name}' | LMB: Assign style | RMB/ESC: Finish | Assigned: {self.assigned_count}"
        context.area.header_text_set(text)

    def assign_style_to_front(self, context, front_obj):
        """Assign the active style to a front."""
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        style = props.door_styles[self.style_index]
        
        result = style.assign_style_to_front(front_obj)
        
        if result == True:
            front_obj['DOOR_STYLE_INDEX'] = self.style_index
            return True
        elif isinstance(result, str):
            # Validation error - show message
            self.report({'WARNING'}, result)
            return False
        else:
            return False

    def cleanup(self, context):
        """Clean up modal state."""
        for obj_name in list(self.original_states.keys()):
            obj = bpy.data.objects.get(obj_name)
            if obj:
                self.highlight_front(obj, highlight=False)
        
        self.original_states.clear()
        self.hovered_front = None
        context.area.header_text_set(None)
        context.window.cursor_set('DEFAULT')

    def invoke(self, context, event):
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        
        if not props.door_styles:
            self.report({'WARNING'}, "No door styles defined")
            return {'CANCELLED'}
        
        self.style_index = props.active_door_style_index
        self.style_name = props.door_styles[self.style_index].name
        self.assigned_count = 0
        self.hovered_front = None
        self.original_states = {}
        
        bpy.ops.object.select_all(action='DESELECT')
        context.window.cursor_set('PAINT_BRUSH')
        self.update_header(context)
        context.window_manager.modal_handler_add(self)
        
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        context.area.tag_redraw()
        
        if event.type in {'RIGHTMOUSE', 'ESC'}:
            if event.value == 'PRESS':
                self.cleanup(context)
                if self.assigned_count > 0:
                    self.report({'INFO'}, f"Assigned '{self.style_name}' to {self.assigned_count} front(s)")
                else:
                    self.report({'INFO'}, "Style painting cancelled")
                return {'FINISHED'}
        
        if event.type == 'MOUSEMOVE':
            front = self.get_front_under_mouse(context, event)
            
            if self.hovered_front and self.hovered_front != front:
                self.highlight_front(self.hovered_front, highlight=False)
            
            if front and front != self.hovered_front:
                self.highlight_front(front, highlight=True)
            
            self.hovered_front = front
        
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if self.hovered_front:
                if self.assign_style_to_front(context, self.hovered_front):
                    self.assigned_count += 1
                    self.update_header(context)
                return {'RUNNING_MODAL'}
        
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}
        
        if event.type in {'NUMPAD_1', 'NUMPAD_2', 'NUMPAD_3', 'NUMPAD_4', 'NUMPAD_5', 
                          'NUMPAD_6', 'NUMPAD_7', 'NUMPAD_8', 'NUMPAD_9', 'NUMPAD_0'}:
            return {'PASS_THROUGH'}
        
        return {'RUNNING_MODAL'}


class hb_frameless_OT_update_fronts_from_style(bpy.types.Operator):
    """Update all fronts that use the active door style"""
    bl_idname = "hb_frameless.update_fronts_from_style"
    bl_label = "Update Fronts from Style"
    bl_description = "Update all door and drawer fronts that use the active door style"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        return len(props.door_styles) > 0

    def execute(self, context):
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        
        if not props.door_styles:
            self.report({'WARNING'}, "No door styles defined")
            return {'CANCELLED'}
        
        style_index = props.active_door_style_index
        style = props.door_styles[style_index]
        
        success_count = 0
        skip_count = 0
        for scene in bpy.data.scenes:
            for obj in scene.objects:
                if obj.get('IS_DOOR_FRONT') or obj.get('IS_DRAWER_FRONT'):
                    front_style_index = obj.get('DOOR_STYLE_INDEX', 0)
                    if front_style_index == style_index:
                        result = style.assign_style_to_front(obj)
                        if result == True:
                            success_count += 1
                        else:
                            skip_count += 1
        
        if skip_count > 0:
            self.report({'WARNING'}, f"Updated {success_count} front(s), skipped {skip_count} (too small for style)")
        else:
            self.report({'INFO'}, f"Updated {success_count} front(s) with style '{style.name}'")
        return {'FINISHED'}


class hb_frameless_OT_select_cabinet_group(bpy.types.Operator):
    """Select Cabinet Group"""
    bl_idname = "hb_frameless.select_cabinet_group"
    bl_label = 'Select Cabinet Group'
    bl_description = "This will select the cabinet group"

    toggle_on: bpy.props.BoolProperty(name="Toggle On",default=False)# type: ignore

    cabinet_group_name: bpy.props.StringProperty(name="Cabinet Group Name",default="")# type: ignore

    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        cabinet_group = bpy.data.objects[self.cabinet_group_name]
        toggle_cabinet_color(cabinet_group,True,type_name="IS_FRAMELESS_CABINET_CAGE",dont_show_parent=False)
        cabinet_group.select_set(True)
        context.view_layer.objects.active = cabinet_group
        for obj in cabinet_group.children_recursive:
            if 'IS_FRAMELESS_CABINET_CAGE' in obj:
                obj.hide_viewport = True
        return {'FINISHED'}     


class hb_frameless_OT_save_cabinet_group_to_user_library(bpy.types.Operator):
    """Save Cabinet Group to User Library"""
    bl_idname = "hb_frameless.save_cabinet_group_to_user_library"
    bl_label = 'Save Cabinet Group to User Library'
    bl_description = "This will save the cabinet group to the user library"
    bl_options = {'UNDO'}

    cabinet_group_name: bpy.props.StringProperty(
        name="Cabinet Group Name",
        default=""
    )  # type: ignore
    
    save_path: bpy.props.StringProperty(
        name="Save Location",
        subtype='DIR_PATH',
        default=""
    )  # type: ignore
    
    create_thumbnail: bpy.props.BoolProperty(
        name="Create Thumbnail",
        description="Generate a thumbnail image for the library",
        default=True
    )  # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.object
        if not obj:
            return False
        # Check if it's a cabinet group (cabinet cage with cabinet children)
        if 'IS_CAGE_GROUP' in obj:
            return True
        return False
    
    def invoke(self, context, event):
        self.cabinet_group_name = context.object.name
        
        # Set default save path to user documents
        
        default_path = os.path.join(os.path.expanduser("~"), "Documents", "Home Builder Library", "Cabinet Groups")
        self.save_path = default_path
        
        return context.window_manager.invoke_props_dialog(self, width=400)
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "cabinet_group_name")
        layout.prop(self, "save_path")
        layout.prop(self, "create_thumbnail")
    
    def execute(self, context):
        cabinet_group = context.object
        
        if not self.cabinet_group_name:
            self.report({'ERROR'}, "Please enter a name for the cabinet group")
            return {'CANCELLED'}
        
        if not self.save_path:
            self.report({'ERROR'}, "Please select a save location")
            return {'CANCELLED'}
        
        # Create directory if it doesn't exist
        os.makedirs(self.save_path, exist_ok=True)
        
        # Sanitize filename
        safe_name = "".join(c for c in self.cabinet_group_name if c.isalnum() or c in (' ', '-', '_')).strip()
        blend_filename = f"{safe_name}.blend"
        blend_filepath = os.path.join(self.save_path, blend_filename)
        
        # Check if file already exists
        if os.path.exists(blend_filepath):
            self.report({'WARNING'}, f"File already exists: {blend_filename}. Overwriting.")
        
        # Collect all objects to save (cabinet group and all descendants)
        objects_to_save = self._collect_objects_recursive(cabinet_group)
        
        # Collect all data blocks used by these objects
        data_blocks = self._collect_data_blocks(objects_to_save)
        
        # Save to blend file
        bpy.data.libraries.write(
            blend_filepath,
            data_blocks,
            path_remap='RELATIVE_ALL',
            fake_user=True
        )
        
        # Generate thumbnail if requested
        if self.create_thumbnail:
            self._create_thumbnail(context, cabinet_group, self.save_path, safe_name)
        
        self.report({'INFO'}, f"Saved cabinet group to: {blend_filepath}")
        return {'FINISHED'}
    
    def _collect_objects_recursive(self, obj):
        """Collect object and all its descendants."""
        objects = {obj}
        for child in obj.children:
            objects.update(self._collect_objects_recursive(child))
        return objects
    
    def _collect_data_blocks(self, objects):
        """Collect all data blocks needed to save the objects."""
        data_blocks = set()
        
        for obj in objects:
            data_blocks.add(obj)
            
            # Add object data (mesh, curve, etc.)
            if obj.data:
                data_blocks.add(obj.data)
            
            # Add materials
            if hasattr(obj, 'data') and obj.data and hasattr(obj.data, 'materials'):
                for mat in obj.data.materials:
                    if mat:
                        data_blocks.add(mat)
                        # Add material node tree textures
                        if mat.use_nodes and mat.node_tree:
                            for node in mat.node_tree.nodes:
                                if node.type == 'TEX_IMAGE' and node.image:
                                    data_blocks.add(node.image)
            
            # Add modifiers' objects (like geometry nodes)
            for mod in obj.modifiers:
                if mod.type == 'NODES' and mod.node_group:
                    data_blocks.add(mod.node_group)
        
        return data_blocks
    
    def _create_thumbnail(self, context, cabinet_group, save_path, name):
        """Create a thumbnail image for the cabinet group."""

        # Store current state
        original_camera = context.scene.camera
        original_render_x = context.scene.render.resolution_x
        original_render_y = context.scene.render.resolution_y
        original_render_percentage = context.scene.render.resolution_percentage
        original_engine = context.scene.render.engine
        original_filepath = context.scene.render.filepath
        
        try:
            # Get cabinet group bounds
            cage = types_frameless.Cabinet(cabinet_group)
            width = cage.get_input('Dim X')
            depth = cage.get_input('Dim Y')
            height = cage.get_input('Dim Z')
            
            # Create temporary camera
            cam_data = bpy.data.cameras.new("ThumbnailCam")
            cam_data.type = 'ORTHO'
            cam_obj = bpy.data.objects.new("ThumbnailCam", cam_data)
            context.scene.collection.objects.link(cam_obj)
            
            # Position camera for isometric-ish view
            import math
            center = cabinet_group.matrix_world @ Vector((width/2, -depth/2, height/2))
            
            # Camera distance based on largest dimension
            max_dim = max(width, depth, height)
            cam_data.ortho_scale = max_dim * 1.5
            
            # Position for 3/4 view
            cam_obj.location = center + Vector((max_dim, -max_dim, max_dim * 0.8))
            
            # Point camera at center
            direction = center - cam_obj.location
            rot_quat = direction.to_track_quat('-Z', 'Y')
            cam_obj.rotation_euler = rot_quat.to_euler()
            
            # Set up render
            context.scene.camera = cam_obj
            context.scene.render.resolution_x = 256
            context.scene.render.resolution_y = 256
            context.scene.render.resolution_percentage = 100
            context.scene.render.engine = 'BLENDER_WORKBENCH'
            context.scene.render.film_transparent = True
            context.scene.render.use_freestyle = True
            context.scene.render.line_thickness = .5
            
            # Render thumbnail
            thumbnail_path = os.path.join(save_path, f"{name}.png")
            context.scene.render.filepath = thumbnail_path
            bpy.ops.render.render(write_still=True)
            
            # Cleanup
            bpy.data.objects.remove(cam_obj)
            bpy.data.cameras.remove(cam_data)
            
        except Exception as e:
            print(f"Failed to create thumbnail: {e}")
        
        finally:
            # Restore original state
            context.scene.camera = original_camera
            context.scene.render.resolution_x = original_render_x
            context.scene.render.resolution_y = original_render_y
            context.scene.render.resolution_percentage = original_render_percentage
            context.scene.render.engine = original_engine
            context.scene.render.filepath = original_filepath  

class hb_frameless_OT_load_cabinet_group_from_library(bpy.types.Operator):
    """Load Cabinet Group from User Library"""
    bl_idname = "hb_frameless.load_cabinet_group_from_library"
    bl_label = 'Load Cabinet Group from Library'
    bl_description = "Load a cabinet group from the user library into the current scene"
    bl_options = {'UNDO'}

    filepath: bpy.props.StringProperty(
        name="File Path",
        subtype='FILE_PATH'
    )  # type: ignore

    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        if not self.filepath or not os.path.exists(self.filepath):
            self.report({'ERROR'}, f"File not found: {self.filepath}")
            return {'CANCELLED'}
        
        # Link or append the cabinet group from the library file
        with bpy.data.libraries.load(self.filepath, link=False) as (data_from, data_to):
            # Get all objects from the file
            data_to.objects = data_from.objects
            data_to.meshes = data_from.meshes
            data_to.materials = data_from.materials
            data_to.node_groups = data_from.node_groups
        
        # Find the root cabinet group (the one without a parent that is a cabinet cage)
        root_objects = []
        for obj in data_to.objects:
            if obj is not None:
                # Link to scene
                context.scene.collection.objects.link(obj)
                
                # Check if it's a root cabinet group
                if 'IS_FRAMELESS_CABINET_CAGE' in obj and obj.parent is None:
                    root_objects.append(obj)
        
        # Select the imported objects
        bpy.ops.object.select_all(action='DESELECT')
        for obj in root_objects:
            obj.select_set(True)
            context.view_layer.objects.active = obj
        
        # Position at 3D cursor
        for obj in root_objects:
            obj.location = context.scene.cursor.location
        
        self.report({'INFO'}, f"Loaded cabinet group from: {os.path.basename(self.filepath)}")
        return {'FINISHED'}


class hb_frameless_OT_refresh_user_library(bpy.types.Operator):
    """Refresh User Library"""
    bl_idname = "hb_frameless.refresh_user_library"
    bl_label = 'Refresh User Library'
    bl_description = "Refresh the list of items in the user library"

    def execute(self, context):
        # Clear cached previews so they get reloaded
        props_hb_frameless.clear_library_previews()
        
        # Force UI redraw
        for area in context.screen.areas:
            area.tag_redraw()
        
        self.report({'INFO'}, "User library refreshed")
        return {'FINISHED'}


class hb_frameless_OT_open_user_library_folder(bpy.types.Operator):
    """Open User Library Folder"""
    bl_idname = "hb_frameless.open_user_library_folder"
    bl_label = 'Open User Library Folder'
    bl_description = "Open the user library folder in file explorer"

    def execute(self, context):
        import os
        import subprocess
        import platform
        
        library_path = get_user_library_path()
        
        if not os.path.exists(library_path):
            os.makedirs(library_path, exist_ok=True)
        
        # Open folder in system file explorer
        if platform.system() == 'Windows':
            os.startfile(library_path)
        elif platform.system() == 'Darwin':  # macOS
            subprocess.Popen(['open', library_path])
        else:  # Linux
            subprocess.Popen(['xdg-open', library_path])
        
        return {'FINISHED'}


class hb_frameless_OT_delete_library_item(bpy.types.Operator):
    """Delete Item from User Library"""
    bl_idname = "hb_frameless.delete_library_item"
    bl_label = 'Delete Library Item'
    bl_description = "Delete a cabinet group from the user library"

    filepath: bpy.props.StringProperty(
        name="File Path",
        subtype='FILE_PATH'
    )  # type: ignore
    
    item_name: bpy.props.StringProperty(
        name="Item Name"
    )  # type: ignore

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)
    
    def execute(self, context):
        import os
        
        if not self.filepath or not os.path.exists(self.filepath):
            self.report({'ERROR'}, f"File not found: {self.filepath}")
            return {'CANCELLED'}
        
        # Delete the blend file
        os.remove(self.filepath)
        
        # Delete thumbnail if it exists
        thumbnail_path = self.filepath.replace('.blend', '.png')
        if os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)
        
        # Clear preview cache so it doesn't show deleted item
        from . import props_hb_frameless
        props_hb_frameless.clear_library_previews()
        
        self.report({'INFO'}, f"Deleted: {self.item_name}")
        
        # Force UI redraw
        for area in context.screen.areas:
            area.tag_redraw()
        
        return {'FINISHED'}


def get_user_library_path():
    """Get the default user library path for cabinet groups."""
    import os
    return os.path.join(os.path.expanduser("~"), "Documents", "Home Builder Library", "Cabinet Groups")


def get_user_library_items():
    """Get list of cabinet group files in the user library."""
    import os
    
    library_path = get_user_library_path()
    items = []
    
    if not os.path.exists(library_path):
        return items
    
    for filename in os.listdir(library_path):
        if filename.endswith('.blend'):
            name = filename[:-6]  # Remove .blend extension
            filepath = os.path.join(library_path, filename)
            
            # Check for thumbnail
            thumbnail_path = os.path.join(library_path, f"{name}.png")
            has_thumbnail = os.path.exists(thumbnail_path)
            
            items.append({
                'name': name,
                'filepath': filepath,
                'thumbnail': thumbnail_path if has_thumbnail else None
            })
    
    return items




# =============================================================================
# CABINET STYLE OPERATORS
# =============================================================================

class hb_frameless_OT_add_cabinet_style(bpy.types.Operator):
    """Add a new cabinet style"""
    bl_idname = "hb_frameless.add_cabinet_style"
    bl_label = "Add Cabinet Style"
    bl_description = "Add a new cabinet style"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.hb_frameless
        
        # Create new style
        style = props.cabinet_styles.add()
        
        # Generate unique name
        base_name = "Style"
        existing_names = [s.name for s in props.cabinet_styles]
        counter = len(props.cabinet_styles)
        while f"{base_name} {counter}" in existing_names:
            counter += 1
        style.name = f"{base_name} {counter}"
        
        # Set as active
        props.active_cabinet_style_index = len(props.cabinet_styles) - 1
        
        self.report({'INFO'}, f"Added cabinet style: {style.name}")
        return {'FINISHED'}


class hb_frameless_OT_remove_cabinet_style(bpy.types.Operator):
    """Remove the selected cabinet style"""
    bl_idname = "hb_frameless.remove_cabinet_style"
    bl_label = "Remove Cabinet Style"
    bl_description = "Remove the selected cabinet style (at least one style must remain)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        props = context.scene.hb_frameless
        # Must have more than 1 style to remove
        return len(props.cabinet_styles) > 1

    def execute(self, context):
        props = context.scene.hb_frameless
        
        if len(props.cabinet_styles) <= 1:
            self.report({'WARNING'}, "Cannot remove the last cabinet style")
            return {'CANCELLED'}
        
        index = props.active_cabinet_style_index
        style_name = props.cabinet_styles[index].name
        
        # Remove the style
        props.cabinet_styles.remove(index)
        
        # Adjust active index
        if props.active_cabinet_style_index >= len(props.cabinet_styles):
            props.active_cabinet_style_index = len(props.cabinet_styles) - 1
        
        # Update any cabinets that referenced this style
        # (shift indices for cabinets using styles after the removed one)
        for obj in context.scene.objects:
            if obj.get('IS_FRAMELESS_CABINET_CAGE'):
                cab_style_index = obj.get('CABINET_STYLE_INDEX', 0)
                if cab_style_index == index:
                    # Reset to default style
                    obj['CABINET_STYLE_INDEX'] = 0
                elif cab_style_index > index:
                    # Shift index down
                    obj['CABINET_STYLE_INDEX'] = cab_style_index - 1
        
        self.report({'INFO'}, f"Removed cabinet style: {style_name}")
        return {'FINISHED'}


class hb_frameless_OT_duplicate_cabinet_style(bpy.types.Operator):
    """Duplicate the selected cabinet style"""
    bl_idname = "hb_frameless.duplicate_cabinet_style"
    bl_label = "Duplicate Cabinet Style"
    bl_description = "Create a copy of the selected cabinet style"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        props = context.scene.hb_frameless
        return len(props.cabinet_styles) > 0

    def execute(self, context):
        props = context.scene.hb_frameless
        
        if not props.cabinet_styles:
            return {'CANCELLED'}
        
        source = props.cabinet_styles[props.active_cabinet_style_index]
        
        # Create new style
        new_style = props.cabinet_styles.add()
        new_style.name = f"{source.name} Copy"
        
        # Copy all properties
        new_style.wood_species = source.wood_species
        new_style.finish_type = source.finish_type
        new_style.finish_color = source.finish_color
        new_style.interior_material = source.interior_material
        new_style.door_overlay_type = source.door_overlay_type
        new_style.door_overlay_amount = source.door_overlay_amount
        new_style.door_gap = source.door_gap
        new_style.edge_banding = source.edge_banding
        
        # Set as active
        props.active_cabinet_style_index = len(props.cabinet_styles) - 1
        
        self.report({'INFO'}, f"Duplicated cabinet style: {new_style.name}")
        return {'FINISHED'}


class hb_frameless_OT_assign_cabinet_style_to_selected_cabinets(bpy.types.Operator):
    """Paint cabinet style onto cabinets - click cabinets to assign the active style"""
    bl_idname = "hb_frameless.assign_cabinet_style_to_selected_cabinets"
    bl_label = "Paint Cabinet Style"
    bl_description = "Click on cabinets to assign the active cabinet style. Right-click or ESC to finish"
    bl_options = {'REGISTER', 'UNDO'}

    # Track state
    hovered_cabinet = None
    assigned_count: int = 0
    style_name: str = ""
    style_index: int = 0
    
    # Store original object state for restoration
    original_states = {}

    @classmethod
    def poll(cls, context):
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        return len(props.cabinet_styles) > 0

    def get_cabinet_under_mouse(self, context, event):
        """Ray cast to find cabinet under mouse cursor."""

        region = context.region
        rv3d = context.region_data
        
        if not region or not rv3d:
            return None
        
        # Get mouse coordinates
        coord = (event.mouse_region_x, event.mouse_region_y)
        
        # Get ray from mouse position
        view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
        ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
        
        # Ray cast through scene
        depsgraph = context.evaluated_depsgraph_get()
        result, location, normal, index, obj, matrix = context.scene.ray_cast(
            depsgraph, ray_origin, view_vector
        )
        
        if result and obj:
            # Check if hit object or any of its parents is a cabinet cage
            current = obj
            while current:
                if current.get('IS_FRAMELESS_CABINET_CAGE'):
                    return current
                current = current.parent
        
        return None

    def highlight_cabinet(self, obj, highlight=True):
        """Highlight or unhighlight a cabinet cage by selecting it."""
        if highlight:
            # Store original state if not already stored
            if obj.name not in self.original_states:
                self.original_states[obj.name] = {
                    'selected': obj.select_get(),
                    'hide_viewport': obj.hide_viewport,
                }
            # Show cage as selected
            obj.hide_viewport = False
            obj.select_set(True)
        else:
            # Restore original state
            if obj.name in self.original_states:
                state = self.original_states[obj.name]
                obj.select_set(state['selected'])
                obj.hide_viewport = state['hide_viewport']

    def update_header(self, context):
        """Update header text with current status."""
        text = f"Cabinet Style: '{self.style_name}' | LMB: Assign style | RMB/ESC: Finish | Assigned: {self.assigned_count}"
        context.area.header_text_set(text)

    def assign_style_to_cabinet(self, context, cabinet_obj):
        """Assign the active style to a cabinet."""
        
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        style = props.cabinet_styles[self.style_index]
        
        cabinet_obj['CABINET_STYLE_INDEX'] = self.style_index
        cabinet_obj['CABINET_STYLE_NAME'] = style.name
        style.assign_style_to_cabinet(cabinet_obj)
        
        return True

    def cleanup(self, context):
        """Clean up modal state."""
        # Restore all highlighted objects
        for obj_name in list(self.original_states.keys()):
            obj = bpy.data.objects.get(obj_name)
            if obj:
                self.highlight_cabinet(obj, highlight=False)
        
        self.original_states.clear()
        self.hovered_cabinet = None
        
        # Clear header and restore cursor
        context.area.header_text_set(None)
        context.window.cursor_set('DEFAULT')

    def invoke(self, context, event):
        # Get style info for display
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        
        if not props.cabinet_styles:
            self.report({'WARNING'}, "No cabinet styles defined")
            return {'CANCELLED'}
        
        self.style_index = props.active_cabinet_style_index
        self.style_name = props.cabinet_styles[self.style_index].name
        self.assigned_count = 0
        self.hovered_cabinet = None
        self.original_states = {}
        
        # Deselect all objects first
        bpy.ops.object.select_all(action='DESELECT')
        
        # Set cursor to paint brush
        context.window.cursor_set('PAINT_BRUSH')
        
        # Set up modal
        self.update_header(context)
        context.window_manager.modal_handler_add(self)
        
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        # Always update the view
        context.area.tag_redraw()
        
        # Handle cancel
        if event.type in {'RIGHTMOUSE', 'ESC'}:
            if event.value == 'PRESS':
                self.cleanup(context)
                if self.assigned_count > 0:
                    self.report({'INFO'}, f"Assigned '{self.style_name}' to {self.assigned_count} cabinet(s)")
                else:
                    self.report({'INFO'}, "Style painting cancelled")
                return {'FINISHED'}
        
        # Handle mouse move - update hover highlight
        if event.type == 'MOUSEMOVE':
            cabinet = self.get_cabinet_under_mouse(context, event)
            
            # Unhighlight previous
            if self.hovered_cabinet and self.hovered_cabinet != cabinet:
                self.highlight_cabinet(self.hovered_cabinet, highlight=False)
            
            # Highlight new
            if cabinet and cabinet != self.hovered_cabinet:
                self.highlight_cabinet(cabinet, highlight=True)
            
            self.hovered_cabinet = cabinet
        
        # Handle click - assign style
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if self.hovered_cabinet:
                if self.assign_style_to_cabinet(context, self.hovered_cabinet):
                    self.assigned_count += 1
                    self.update_header(context)
                return {'RUNNING_MODAL'}
        
        # Pass through navigation events
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}
        
        # Pass through view manipulation
        if event.type in {'NUMPAD_1', 'NUMPAD_2', 'NUMPAD_3', 'NUMPAD_4', 'NUMPAD_5', 
                          'NUMPAD_6', 'NUMPAD_7', 'NUMPAD_8', 'NUMPAD_9', 'NUMPAD_0'}:
            return {'PASS_THROUGH'}
        
        return {'RUNNING_MODAL'}


class hb_frameless_OT_assign_cabinet_style(bpy.types.Operator):
    """Assign the active cabinet style to a cabinet"""
    bl_idname = "hb_frameless.assign_cabinet_style"
    bl_label = "Assign Style to Cabinet"
    bl_description = "Assign the active cabinet style to a cabinet"
    bl_options = {'REGISTER', 'UNDO'}

    cabinet_name: bpy.props.StringProperty(name="Cabinet Name",default="")# type: ignore

    def execute(self, context):
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        
        style_index = props.active_cabinet_style_index
        style = props.cabinet_styles[style_index]
        
        cabinet_obj = bpy.data.objects.get(self.cabinet_name)
        if cabinet_obj:
            cabinet_obj['CABINET_STYLE_INDEX'] = style_index
            cabinet_obj['CABINET_STYLE_NAME'] = style.name  # Store name for reference
            style.assign_style_to_cabinet(cabinet_obj)
        
        return {'FINISHED'}


class hb_frameless_OT_update_cabinets_from_style(bpy.types.Operator):
    """Update all cabinets in the scene that use the active cabinet style"""
    bl_idname = "hb_frameless.update_cabinets_from_style"
    bl_label = "Update Cabinets from Style"
    bl_description = "Update all cabinets in the scene that use the active cabinet style with current style settings"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        return len(props.cabinet_styles) > 0

    def execute(self, context):
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        
        if not props.cabinet_styles:
            self.report({'WARNING'}, "No cabinet styles defined")
            return {'CANCELLED'}
        
        style_index = props.active_cabinet_style_index
        style = props.cabinet_styles[style_index]
        
        count = 0
        # Iterate through all scenes (rooms) to find cabinets with this style
        for scene in bpy.data.scenes:
            for obj in scene.objects:
                if obj.get('IS_FRAMELESS_CABINET_CAGE'):
                    cab_style_index = obj.get('CABINET_STYLE_INDEX', 0)
                    if cab_style_index == style_index:
                        # Re-apply the style to update materials
                        style.assign_style_to_cabinet(obj)
                        obj['CABINET_STYLE_NAME'] = style.name  # Update name in case it changed
                        count += 1
        
        if count > 0:
            self.report({'INFO'}, f"Updated {count} cabinet(s) with style '{style.name}'")
        else:
            self.report({'INFO'}, f"No cabinets found using style '{style.name}'")
        
        return {'FINISHED'}



# =============================================================================
# CROWN DETAIL OPERATORS
# =============================================================================

class hb_frameless_OT_update_cabinet_pulls(bpy.types.Operator):
    bl_idname = "hb_frameless.update_cabinet_pulls"
    bl_label = "Update Cabinet Pulls"
    bl_description = "Update pulls on all cabinets to match current selection"
    bl_options = {'UNDO'}
    
    pull_type: bpy.props.EnumProperty(
        name="Pull Type",
        items=[
            ('DOOR', "Door Pulls", "Update door pulls"),
            ('DRAWER', "Drawer Pulls", "Update drawer pulls"),
            ('ALL', "All Pulls", "Update all pulls"),
        ],
        default='ALL'
    )# type: ignore

    def execute(self, context):
        from . import props_hb_frameless
        
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        
        # Clear cached pull objects to force reload
        if self.pull_type in ('DOOR', 'ALL'):
            props.current_door_pull_object = None
        if self.pull_type in ('DRAWER', 'ALL'):
            props.current_drawer_front_pull_object = None
        
        # Load new pull objects
        door_pull_obj = None
        drawer_pull_obj = None
        
        if self.pull_type in ('DOOR', 'ALL'):
            door_pull_obj = props_hb_frameless.load_pull_object(props.door_pull_selection)
            if door_pull_obj:
                props.current_door_pull_object = door_pull_obj
        
        if self.pull_type in ('DRAWER', 'ALL'):
            drawer_pull_obj = props_hb_frameless.load_pull_object(props.drawer_pull_selection)
            if drawer_pull_obj:
                props.current_drawer_front_pull_object = drawer_pull_obj
        
        # Update all existing pulls in the current scene
        updated_count = 0
        for obj in context.scene.objects:
            # Find pull hardware objects (children of door/drawer fronts)
            if obj.get('IS_DOOR_FRONT') and self.pull_type in ('DOOR', 'ALL') and door_pull_obj:
                for child in obj.children:
                    if 'Pull' in child.name and child.home_builder.mod_name:
                        try:
                            pull_hw = hb_types.GeoNodeHardware(child)
                            pull_hw.set_input("Object", door_pull_obj)
                            updated_count += 1
                        except:
                            pass
            
            elif obj.get('IS_DRAWER_FRONT') and self.pull_type in ('DRAWER', 'ALL') and drawer_pull_obj:
                for child in obj.children:
                    if 'Pull' in child.name and child.home_builder.mod_name:
                        try:
                            pull_hw = hb_types.GeoNodeHardware(child)
                            pull_hw.set_input("Object", drawer_pull_obj)
                            updated_count += 1
                        except:
                            pass
        
        self.report({'INFO'}, f"Updated {updated_count} pull(s)")
        return {'FINISHED'}


class hb_frameless_OT_update_pull_locations(bpy.types.Operator):
    bl_idname = "hb_frameless.update_pull_locations"
    bl_label = "Update Pull Locations"
    bl_description = "Update pull locations on all fronts to match current global settings"
    bl_options = {'UNDO'}
    
    update_type: bpy.props.EnumProperty(
        name="Update Type",
        items=[
            ('DOOR', "Door Fronts", "Update door pull locations"),
            ('DRAWER', "Drawer Fronts", "Update drawer pull locations"),
            ('ALL', "All Fronts", "Update all pull locations"),
        ],
        default='ALL'
    )# type: ignore

    def execute(self, context):
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        
        door_count = 0
        drawer_count = 0
        updated_fronts = []
        
        # Only update objects in the current scene
        for obj in context.scene.objects:
            # Update door fronts
            if obj.get('IS_DOOR_FRONT') and self.update_type in ('DOOR', 'ALL'):
                try:
                    # Update properties using obj['Prop Name'] syntax
                    obj['Handle Horizontal Location'] = props.pull_dim_from_edge
                    obj['Base Pull Vertical Location'] = props.pull_vertical_location_base
                    obj['Tall Pull Vertical Location'] = props.pull_vertical_location_tall
                    obj['Upper Pull Vertical Location'] = props.pull_vertical_location_upper
                    updated_fronts.append(obj)
                    door_count += 1
                except Exception as e:
                    print(f"Error updating door front {obj.name}: {e}")
            
            # Update drawer fronts
            elif obj.get('IS_DRAWER_FRONT') and self.update_type in ('DRAWER', 'ALL'):
                try:
                    obj['Center Pull'] = 1 if props.center_pulls_on_drawer_front else 0
                    obj['Handle Horizontal Location'] = props.pull_vertical_location_drawers
                    updated_fronts.append(obj)
                    drawer_count += 1
                except Exception as e:
                    print(f"Error updating drawer front {obj.name}: {e}")
        
        # Force driver recalculation (workaround for Blender bug #133392)
        # Touch location on all pull objects to mark transforms dirty
        for obj in updated_fronts:
            hb_utils.run_calc_fix(context,obj)
        
        # Report results
        if self.update_type == 'DOOR':
            self.report({'INFO'}, f"Updated {door_count} door front(s)")
        elif self.update_type == 'DRAWER':
            self.report({'INFO'}, f"Updated {drawer_count} drawer front(s)")
        else:
            self.report({'INFO'}, f"Updated {door_count} door(s) and {drawer_count} drawer(s)")
        
        return {'FINISHED'}



class hb_frameless_OT_update_pull_finish(bpy.types.Operator):
    """Update finish on all cabinet pulls"""
    bl_idname = "hb_frameless.update_pull_finish"
    bl_label = "Update Pull Finish"
    bl_description = "Apply the selected finish to all cabinet pulls"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        from .props_hb_frameless import get_or_create_pull_finish_material
        
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        
        # Get or create the finish material
        finish_mat = get_or_create_pull_finish_material(props.pull_finish)
        if not finish_mat:
            self.report({'ERROR'}, "Could not create finish material")
            return {'CANCELLED'}
        
        pull_count = 0
        updated_sources = set()
        
        # Find all pull objects and their source objects
        for obj in context.scene.objects:
            # Check for door/drawer fronts and get their pull children
            if obj.get('IS_DOOR_FRONT') or obj.get('IS_DRAWER_FRONT'):
                for child in obj.children:
                    if 'Pull' in child.name:
                        # Find the geometry node modifier
                        for mod in child.modifiers:
                            if mod.type == 'NODES' and mod.node_group:
                                # Get the source object from the modifier
                                for key in mod.keys():
                                    val = mod[key]
                                    if hasattr(val, 'material_slots'):
                                        # This is the source pull object
                                        source_obj = val
                                        if source_obj.name not in updated_sources:
                                            # Apply material to source object
                                            if len(source_obj.material_slots) == 0:
                                                source_obj.data.materials.append(finish_mat)
                                            else:
                                                source_obj.material_slots[0].material = finish_mat
                                            updated_sources.add(source_obj.name)
                        pull_count += 1
        
        # Force viewport update
        context.view_layer.update()
        
        self.report({'INFO'}, f"Applied finish to {len(updated_sources)} pull type(s) ({pull_count} total pulls)")
        return {'FINISHED'}


class hb_frameless_OT_create_crown_detail(bpy.types.Operator):
    """Create a new crown molding detail"""
    bl_idname = "hb_frameless.create_crown_detail"
    bl_label = "Create Crown Detail"
    bl_description = "Create a new crown molding detail with a 2D profile scene"
    bl_options = {'REGISTER', 'UNDO'}
    
    name: bpy.props.StringProperty(
        name="Name",
        description="Name for the crown detail",
        default="Crown Detail"
    )  # type: ignore
    
    
    def execute(self, context):

        # Get main scene props
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        
        # Create a new crown detail entry
        crown = props.crown_details.add()
        crown.name = self.name

        # Create a detail scene for the crown profile
        detail = hb_details.DetailView()
        scene = detail.create(f"Crown - {self.name}")
        scene['IS_CROWN_DETAIL'] = True
        
        # Store the scene name reference
        crown.detail_scene_name = scene.name
        
        # Set as active
        props.active_crown_detail_index = len(props.crown_details) - 1
        
        # Draw a cabinet side detail as starting point to add crown molding details to
        self._draw_cabinet_side_detail(context, scene, props)
        
        # Switch to the detail scene
        bpy.ops.home_builder_layouts.go_to_layout_view(scene_name=scene.name)
        
        self.report({'INFO'}, f"Created crown detail: {self.name}")
        return {'FINISHED'}
    
    def _draw_cabinet_side_detail(self, context, scene, props):
        """Draw the top-front corner of cabinet side profile (4 inch section)."""

        # Make sure we're in the right scene
        original_scene = context.scene
        context.window.scene = scene
        
        # Get cabinet dimensions from props
        part_thickness = props.default_carcass_part_thickness
        door_to_cab_gap = units.inch(0.125) # Standard door gap TODO: look to frameless props for this
        door_overlay = part_thickness - units.inch(.0625) # Standard door overlay TODO: look to cabinet style door overlay
        door_thickness = units.inch(0.75)  # Standard door thickness
        
        # Only show 4" of the corner
        corner_size = units.inch(4)
        
        # Position the detail so the top-front corner of the cabinet side is at origin
        # -X axis goes toward the back (depth), +Y axis goes up (height)
        # Origin (0,0) is at the top-front corner of the cabinet side panel
        
        hb_scene = scene.home_builder

        # Draw cabinet side profile - L-shaped corner section
        side_profile = hb_details.GeoNodePolyline()
        side_profile.create("Cabinet Side")
        # Start at bottom of visible section (4" down from top)
        side_profile.set_point(0, Vector((0, -corner_size, 0)))
        # Go up to top-front corner
        side_profile.add_point(Vector((0, 0, 0)))
        # Go back along top edge (4" toward back)
        side_profile.add_point(Vector((-corner_size, 0, 0)))
        
        # Draw top panel - just the front portion visible in the corner
        top_panel = hb_details.GeoNodePolyline()
        top_panel.create("Cabinet Top")
        # Draw single line to show the top panel
        top_panel.set_point(0, Vector((0, -part_thickness, 0)))
        top_panel.add_point(Vector((-corner_size, -part_thickness, 0)))
        
        # Draw door profile - just the top portion visible in the corner
        door_profile = hb_details.GeoNodePolyline()
        door_profile.create("Door Face")
        # Draw U Shape Door Profile for the corner
        door_profile.set_point(0, Vector((door_to_cab_gap, -corner_size, 0)))
        door_profile.add_point(Vector((door_to_cab_gap, -part_thickness+door_overlay, 0)))
        door_profile.add_point(Vector((door_to_cab_gap+door_thickness, -part_thickness+door_overlay, 0)))
        door_profile.add_point(Vector((door_to_cab_gap+door_thickness, -corner_size, 0)))

        # Add a label/text annotation
        text = hb_details.GeoNodeText()
        text.create("Label", "CROWN DETAIL", hb_scene.annotation_text_size)
        text.set_location(Vector((0, -corner_size - units.inch(1), 0)))
        text.set_alignment('CENTER', 'TOP')
        
        # Switch back to original scene
        context.window.scene = original_scene


class hb_frameless_OT_delete_crown_detail(bpy.types.Operator):
    """Delete the selected crown detail"""
    bl_idname = "hb_frameless.delete_crown_detail"
    bl_label = "Delete Crown Detail"
    bl_description = "Delete the selected crown molding detail and its profile scene"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        return len(props.crown_details) > 0
    
    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)
    
    def execute(self, context):
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        
        if not props.crown_details:
            self.report({'WARNING'}, "No crown details to delete")
            return {'CANCELLED'}
        
        index = props.active_crown_detail_index
        crown = props.crown_details[index]
        
        # Delete the associated detail scene if it exists
        detail_scene = crown.get_detail_scene()
        if detail_scene:
            # Make sure we're not deleting the current scene
            if context.scene == detail_scene:
                # Switch to main scene first
                context.window.scene = main_scene
            
            bpy.data.scenes.remove(detail_scene)
        
        # Remove from collection
        crown_name = crown.name
        props.crown_details.remove(index)
        
        # Update active index
        if props.active_crown_detail_index >= len(props.crown_details):
            props.active_crown_detail_index = max(0, len(props.crown_details) - 1)
        
        self.report({'INFO'}, f"Deleted crown detail: {crown_name}")
        return {'FINISHED'}


class hb_frameless_OT_edit_crown_detail(bpy.types.Operator):
    """Edit the selected crown detail profile"""
    bl_idname = "hb_frameless.edit_crown_detail"
    bl_label = "Edit Crown Detail"
    bl_description = "Open the crown detail profile scene for editing"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        if len(props.crown_details) == 0:
            return False
        crown = props.crown_details[props.active_crown_detail_index]
        return crown.get_detail_scene() is not None
    
    def execute(self, context):
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        
        crown = props.crown_details[props.active_crown_detail_index]
        detail_scene = crown.get_detail_scene()
        
        if not detail_scene:
            self.report({'ERROR'}, "Crown detail scene not found")
            return {'CANCELLED'}
        
        # Switch to the detail scene
        bpy.ops.home_builder_layouts.go_to_layout_view(scene_name=detail_scene.name)
        
        self.report({'INFO'}, f"Editing crown detail: {crown.name}")
        return {'FINISHED'}


class hb_frameless_OT_assign_crown_to_cabinets(bpy.types.Operator):
    """Assign the selected crown detail to selected cabinets"""
    bl_idname = "hb_frameless.assign_crown_to_cabinets"
    bl_label = "Assign Crown to Cabinets"
    bl_description = "Create crown molding extrusions on selected cabinets using the active crown detail"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        if len(props.crown_details) == 0:
            return False
        # Check if any cabinets are selected
        for obj in context.selected_objects:
            if obj.get('IS_CABINET_BP') or obj.get('IS_FRAMELESS_CABINET_CAGE'):
                return True
        return False
    
    def execute(self, context):
        from mathutils import Vector
        
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_frameless
        
        crown = props.crown_details[props.active_crown_detail_index]
        detail_scene = crown.get_detail_scene()
        
        if not detail_scene:
            self.report({'ERROR'}, "Crown detail scene not found")
            return {'CANCELLED'}
        
        # Get all molding profiles and solid lumber from the detail scene
        profiles = []
        for obj in detail_scene.objects:
            if obj.get('IS_MOLDING_PROFILE') or obj.get('IS_SOLID_LUMBER'):
                profiles.append(obj)
        
        if not profiles:
            self.report({'WARNING'}, "No molding profiles or solid lumber found in crown detail")
            return {'CANCELLED'}
        
        # Collect unique cabinets from selection (only UPPER and TALL get crown)
        cabinets = []
        for obj in context.selected_objects:
            cabinet_bp = None
            if obj.get('IS_CABINET_BP') or obj.get('IS_FRAMELESS_CABINET_CAGE'):
                cabinet_bp = obj
            elif obj.parent:
                if obj.parent.get('IS_CABINET_BP') or obj.parent.get('IS_FRAMELESS_CABINET_CAGE'):
                    cabinet_bp = obj.parent
            
            if cabinet_bp and cabinet_bp not in cabinets:
                cab_type = cabinet_bp.get('CABINET_TYPE', '')
                if cab_type in ('UPPER', 'TALL'):
                    cabinets.append(cabinet_bp)
        
        if not cabinets:
            self.report({'WARNING'}, "No valid upper or tall cabinets selected")
            return {'CANCELLED'}
        
        # Remove any existing crown molding on selected cabinets
        for cabinet in cabinets:
            self._remove_existing_crown(cabinet)
            cabinet['CROWN_DETAIL_NAME'] = crown.name
            cabinet['CROWN_DETAIL_SCENE'] = crown.detail_scene_name
        
        # Get all walls and all cabinets in scene for adjacency detection
        all_walls = [o for o in main_scene.objects if o.get('IS_WALL_BP') or o.get('IS_WALL')]
        all_cabinets = [o for o in main_scene.objects if o.get('IS_FRAMELESS_CABINET_CAGE')]
        
        # Analyze cabinet adjacency and group connected cabinets
        cabinet_groups = self._group_adjacent_cabinets(cabinets, all_cabinets, all_walls)
        
        # Create crown molding for each group
        for group in cabinet_groups:
            for profile in profiles:
                self._create_crown_for_group(context, group, profile, all_walls, all_cabinets, main_scene)
        
        total_cabs = sum(len(g['cabinets']) for g in cabinet_groups)
        self.report({'INFO'}, f"Created crown molding on {total_cabs} cabinet(s) in {len(cabinet_groups)} group(s)")
        return {'FINISHED'}
    
    def _remove_existing_crown(self, cabinet):
        """Remove any existing crown molding children from the cabinet."""
        children_to_remove = []
        for child in cabinet.children:
            if child.get('IS_CROWN_MOLDING') or child.get('IS_CROWN_PROFILE_COPY'):
                children_to_remove.append(child)
        
        for child in children_to_remove:
            bpy.data.objects.remove(child, do_unlink=True)
    
    def _get_cabinet_bounds(self, cabinet):
        """Get world-space bounds of a cabinet."""
        world_loc = cabinet.matrix_world.translation
        dims = cabinet.dimensions
        return {
            'left_x': world_loc.x,
            'right_x': world_loc.x + dims.x,
            'front_y': world_loc.y - dims.y,
            'back_y': world_loc.y,
            'bottom_z': world_loc.z,
            'top_z': world_loc.z + dims.z,
            'width': dims.x,
            'depth': dims.y,
            'height': dims.z,
        }
    
    def _is_against_wall(self, cabinet, side, walls, tolerance=0.05):
        """Check if cabinet side is against a wall."""
        bounds = self._get_cabinet_bounds(cabinet)
        
        for wall in walls:
            wall_loc = wall.matrix_world.translation
            wall_dims = wall.dimensions
            
            # Wall bounds (walls are typically thin in Y)
            wall_min_x = wall_loc.x
            wall_max_x = wall_loc.x + wall_dims.x
            wall_min_y = wall_loc.y - wall_dims.y
            wall_max_y = wall_loc.y
            
            if side == 'left':
                # Check if cabinet's left edge is near wall's right edge or within wall
                if abs(bounds['left_x'] - wall_max_x) < tolerance or abs(bounds['left_x'] - wall_min_x) < tolerance:
                    # Check Y overlap
                    if bounds['back_y'] >= wall_min_y and bounds['front_y'] <= wall_max_y:
                        return True
            elif side == 'right':
                # Check if cabinet's right edge is near wall's left edge
                if abs(bounds['right_x'] - wall_min_x) < tolerance or abs(bounds['right_x'] - wall_max_x) < tolerance:
                    if bounds['back_y'] >= wall_min_y and bounds['front_y'] <= wall_max_y:
                        return True
            elif side == 'back':
                # Check if cabinet's back is against wall
                if abs(bounds['back_y'] - wall_min_y) < tolerance:
                    if bounds['left_x'] >= wall_min_x and bounds['right_x'] <= wall_max_x:
                        return True
        
        return False
    
    def _find_adjacent_cabinet(self, cabinet, side, all_cabinets, tolerance=0.02):
        """Find a cabinet adjacent to the given side."""
        bounds = self._get_cabinet_bounds(cabinet)
        cab_type = cabinet.get('CABINET_TYPE', '')
        
        for other in all_cabinets:
            if other == cabinet:
                continue
            
            other_bounds = self._get_cabinet_bounds(other)
            other_type = other.get('CABINET_TYPE', '')
            
            # Only consider UPPER and TALL cabinets for crown
            if other_type not in ('UPPER', 'TALL'):
                continue
            
            # Check if tops are at same height (with tolerance)
            if abs(bounds['top_z'] - other_bounds['top_z']) > tolerance:
                continue
            
            if side == 'left':
                # Check if other cabinet's right edge meets this cabinet's left edge
                if abs(other_bounds['right_x'] - bounds['left_x']) < tolerance:
                    return other
            elif side == 'right':
                # Check if other cabinet's left edge meets this cabinet's right edge
                if abs(other_bounds['left_x'] - bounds['right_x']) < tolerance:
                    return other
        
        return None
    
    def _group_adjacent_cabinets(self, selected_cabinets, all_cabinets, walls):
        """Group selected cabinets that are adjacent to each other."""
        # Sort cabinets by X position
        sorted_cabs = sorted(selected_cabinets, key=lambda c: self._get_cabinet_bounds(c)['left_x'])
        
        groups = []
        used = set()
        
        for cabinet in sorted_cabs:
            if cabinet in used:
                continue
            
            # Start a new group
            group_cabs = [cabinet]
            used.add(cabinet)
            
            # Find all connected cabinets to the right
            current = cabinet
            while True:
                right_neighbor = self._find_adjacent_cabinet(current, 'right', all_cabinets)
                if right_neighbor and right_neighbor in selected_cabinets and right_neighbor not in used:
                    group_cabs.append(right_neighbor)
                    used.add(right_neighbor)
                    current = right_neighbor
                else:
                    break
            
            # Analyze group
            first_cab = group_cabs[0]
            last_cab = group_cabs[-1]
            
            # Check wall adjacency
            left_against_wall = self._is_against_wall(first_cab, 'left', walls)
            right_against_wall = self._is_against_wall(last_cab, 'right', walls)
            
            # Check if there's an unselected adjacent cabinet (for returns)
            left_adjacent = self._find_adjacent_cabinet(first_cab, 'left', all_cabinets)
            right_adjacent = self._find_adjacent_cabinet(last_cab, 'right', all_cabinets)
            
            groups.append({
                'cabinets': group_cabs,
                'left_wall': left_against_wall,
                'right_wall': right_against_wall,
                'left_adjacent': left_adjacent,
                'right_adjacent': right_adjacent,
            })
        
        return groups
    
    def _create_crown_for_group(self, context, group, profile, walls, all_cabinets, target_scene):
        """Create crown molding extrusion for a group of cabinets."""
        from mathutils import Vector
        
        cabinets = group['cabinets']
        first_cab = cabinets[0]
        last_cab = cabinets[-1]
        
        profile_offset_x = profile.location.x  # Depth offset (positive = forward)
        profile_offset_y = profile.location.y  # Height offset
        
        # Copy the profile curve
        profile_copy = profile.copy()
        profile_copy.data = profile.data.copy()
        target_scene.collection.objects.link(profile_copy)
        
        profile_copy.location = (0, 0, 0)
        profile_copy.rotation_euler = (0, 0, 0)
        profile_copy.scale = (1, 1, 1)
        profile_copy.data.dimensions = '2D'
        profile_copy.data.bevel_depth = 0
        profile_copy.data.fill_mode = 'NONE'
        profile_copy.hide_viewport = True
        profile_copy.hide_render = True
        profile_copy.name = f"Crown_Profile_{profile.name}"
        profile_copy['IS_CROWN_PROFILE_COPY'] = True
        
        # Build path points in WORLD coordinates
        world_points = []
        
        first_bounds = self._get_cabinet_bounds(first_cab)
        last_bounds = self._get_cabinet_bounds(last_cab)
        
        # Calculate profile adjustments
        if profile_offset_x < 0:
            # Profile is set back - inset from edges
            inset = abs(profile_offset_x)
            extend = 0
        else:
            # Profile extends forward
            inset = 0
            extend = profile_offset_x
        
        # === LEFT SIDE ===
        if group['left_wall']:
            # Against wall - start at front corner, no return
            start_x = first_bounds['left_x'] + inset
            # Start directly at the front
            world_points.append(Vector((start_x, first_bounds['front_y'] - extend + inset, 0)))
        elif group['left_adjacent']:
            adj_bounds = self._get_cabinet_bounds(group['left_adjacent'])
            adj_type = group['left_adjacent'].get('CABINET_TYPE', '')
            
            # Start at left edge
            start_x = first_bounds['left_x'] + inset
            
            if adj_type == 'TALL' and first_cab.get('CABINET_TYPE') == 'UPPER':
                # Tall to the left of upper - return to tall's depth
                world_points.append(Vector((start_x, adj_bounds['front_y'] - extend + inset, 0)))
            
            # Add front point for this cabinet
            world_points.append(Vector((start_x, first_bounds['front_y'] - extend + inset, 0)))
        else:
            # Open left side - add return to back
            start_x = first_bounds['left_x'] + inset
            world_points.append(Vector((start_x, first_bounds['back_y'], 0)))
            world_points.append(Vector((start_x, first_bounds['front_y'] - extend + inset, 0)))
        
        # === MIDDLE - transitions between cabinets ===
        for i in range(len(cabinets) - 1):
            current_cab = cabinets[i]
            next_cab = cabinets[i + 1]
            current_bounds = self._get_cabinet_bounds(current_cab)
            next_bounds = self._get_cabinet_bounds(next_cab)
            
            current_type = current_cab.get('CABINET_TYPE', '')
            next_type = next_cab.get('CABINET_TYPE', '')
            
            # Transition X position (right edge of current = left edge of next)
            trans_x = current_bounds['right_x']
            
            # Check for depth change
            depth_diff = abs(current_bounds['depth'] - next_bounds['depth'])
            
            if depth_diff > 0.01:
                # Depth transition - add step
                if current_type == 'TALL' and next_type == 'UPPER':
                    # Tall to Upper - step back to upper depth
                    world_points.append(Vector((trans_x - inset, current_bounds['front_y'] - extend + inset, 0)))
                    world_points.append(Vector((trans_x - inset, next_bounds['front_y'] - extend + inset, 0)))
                elif current_type == 'UPPER' and next_type == 'TALL':
                    # Upper to Tall - step forward to tall depth  
                    world_points.append(Vector((trans_x + inset, current_bounds['front_y'] - extend + inset, 0)))
                    world_points.append(Vector((trans_x + inset, next_bounds['front_y'] - extend + inset, 0)))
            # If same depth, no intermediate points needed - path continues
        
        # === RIGHT SIDE ===
        if group['right_wall']:
            # Against wall - end at front corner, no return
            end_x = last_bounds['right_x'] - inset
            world_points.append(Vector((end_x, last_bounds['front_y'] - extend + inset, 0)))
        elif group['right_adjacent']:
            adj_bounds = self._get_cabinet_bounds(group['right_adjacent'])
            adj_type = group['right_adjacent'].get('CABINET_TYPE', '')
            
            end_x = last_bounds['right_x'] - inset
            
            # Add front point for last cabinet
            world_points.append(Vector((end_x, last_bounds['front_y'] - extend + inset, 0)))
            
            if adj_type == 'TALL' and last_cab.get('CABINET_TYPE') == 'UPPER':
                # Upper transitioning to tall on right - return to tall's depth
                world_points.append(Vector((end_x, adj_bounds['front_y'] - extend + inset, 0)))
        else:
            # Open right side - add return to back
            end_x = last_bounds['right_x'] - inset
            world_points.append(Vector((end_x, last_bounds['front_y'] - extend + inset, 0)))
            world_points.append(Vector((end_x, last_bounds['back_y'], 0)))
        
        # Convert world points to local coordinates relative to first cabinet
        first_world = first_cab.matrix_world.translation
        local_points = []
        for pt in world_points:
            local_pt = Vector((pt.x - first_world.x, pt.y - first_world.y, 0))
            local_points.append(local_pt)
        
        # Create the curve
        curve_data = bpy.data.curves.new(name=f"Crown_Path_{profile.name}", type='CURVE')
        curve_data.dimensions = '2D'
        curve_data.bevel_mode = 'OBJECT'
        curve_data.bevel_object = profile_copy
        curve_data.use_fill_caps = True
        
        spline = curve_data.splines.new('POLY')
        spline.points.add(len(local_points) - 1)
        
        for i, pt in enumerate(local_points):
            spline.points[i].co = (pt.x, pt.y, pt.z, 1)
        
        crown_obj = bpy.data.objects.new(f"Crown_{profile.name}", curve_data)
        target_scene.collection.objects.link(crown_obj)
        
        # Parent to first cabinet
        crown_obj.parent = first_cab
        crown_obj.location = (0, 0, first_bounds['height'] + profile_offset_y)
        crown_obj['IS_CROWN_MOLDING'] = True
        crown_obj['CROWN_PROFILE_NAME'] = profile.name
        
        # Add Smooth by Angle modifier
        smooth_mod = crown_obj.modifiers.new(name="Smooth by Angle", type='NODES')
        if "Smooth by Angle" not in bpy.data.node_groups:
            import os
            essentials_path = os.path.join(
                bpy.utils.resource_path('LOCAL'),
                "datafiles", "assets", "nodes", "geometry_nodes_essentials.blend"
            )
            if os.path.exists(essentials_path):
                with bpy.data.libraries.load(essentials_path) as (data_from, data_to):
                    if "Smooth by Angle" in data_from.node_groups:
                        data_to.node_groups = ["Smooth by Angle"]
        if "Smooth by Angle" in bpy.data.node_groups:
            smooth_mod.node_group = bpy.data.node_groups["Smooth by Angle"]
        
        profile_copy.parent = crown_obj
        profile_copy['IS_CROWN_PROFILE_COPY'] = True
        
        return crown_obj


def get_molding_library_path():
    """Get the path to the molding library folder."""
    import os
    return os.path.join(os.path.dirname(__file__), "frameless_assets", "moldings")


def get_molding_categories():
    """Get list of molding categories (subfolders)."""
    import os
    library_path = get_molding_library_path()
    categories = []
    if os.path.exists(library_path):
        for folder in sorted(os.listdir(library_path)):
            folder_path = os.path.join(library_path, folder)
            if os.path.isdir(folder_path):
                categories.append((folder, folder, folder))
    return categories if categories else [('NONE', "No Categories", "No molding categories found")]


def get_molding_items(category):
    """Get list of molding items in a category."""
    import os
    library_path = get_molding_library_path()
    category_path = os.path.join(library_path, category)
    items = []
    if os.path.exists(category_path):
        for f in sorted(os.listdir(category_path)):
            if f.endswith('.blend'):
                name = os.path.splitext(f)[0]
                filepath = os.path.join(category_path, f)
                # Check for thumbnail
                thumb_path = os.path.join(category_path, name + '.png')
                items.append({
                    'name': name,
                    'filepath': filepath,
                    'thumbnail': thumb_path if os.path.exists(thumb_path) else None
                })
    return items


class hb_frameless_OT_add_molding_profile(bpy.types.Operator):
    """Add a molding profile from the library to the current detail scene"""
    bl_idname = "hb_frameless.add_molding_profile"
    bl_label = "Add Molding Profile"
    bl_description = "Add a molding profile from the library to the current crown detail"
    bl_options = {'REGISTER', 'UNDO'}
    
    filepath: bpy.props.StringProperty(
        name="Filepath",
        description="Path to the molding blend file"
    )  # type: ignore
    
    molding_name: bpy.props.StringProperty(
        name="Name",
        description="Name of the molding"
    )  # type: ignore
    
    @classmethod
    def poll(cls, context):
        # Must be in a crown detail scene
        return context.scene.get('IS_CROWN_DETAIL', False) or context.scene.get('IS_DETAIL_VIEW', False)
    
    def execute(self, context):
        import os
        
        if not self.filepath or not os.path.exists(self.filepath):
            self.report({'ERROR'}, f"Molding file not found: {self.filepath}")
            return {'CANCELLED'}
        
        # Load the molding profile from the blend file
        with bpy.data.libraries.load(self.filepath, link=False) as (data_from, data_to):
            data_to.objects = data_from.objects
        
        # Link the loaded objects to the current scene
        imported_objects = []
        for obj in data_to.objects:
            if obj is not None:
                context.scene.collection.objects.link(obj)
                imported_objects.append(obj)
                
                # Mark as molding profile
                obj['IS_MOLDING_PROFILE'] = True
                obj['MOLDING_NAME'] = self.molding_name
                
                # Apply scene annotation settings if it's a curve
                if obj.type == 'CURVE':
                    hb_scene = context.scene.home_builder
                    obj.data.bevel_depth = hb_scene.annotation_line_thickness
                    color = tuple(hb_scene.annotation_line_color) + (1.0,)
                    obj.color = color
        
        # Select the imported objects
        bpy.ops.object.select_all(action='DESELECT')
        for obj in imported_objects:
            obj.select_set(True)
        
        if imported_objects:
            context.view_layer.objects.active = imported_objects[0]
            # Position at origin for user to move
            for obj in imported_objects:
                obj.location = (0, 0, 0)
        
        self.report({'INFO'}, f"Added molding profile: {self.molding_name}")
        return {'FINISHED'}


class hb_frameless_OT_add_solid_lumber(bpy.types.Operator):
    """Add a custom solid lumber profile to the detail"""
    bl_idname = "hb_frameless.add_solid_lumber"
    bl_label = "Add Solid Lumber"
    bl_description = "Add a custom solid lumber rectangle profile to the current detail"
    bl_options = {'REGISTER', 'UNDO'}
    
    thickness: bpy.props.FloatProperty(
        name="Thickness",
        description="Thickness of the lumber",
        default=0.01905,  # 0.75 inches
        min=0.001,
        unit='LENGTH',
        precision=4
    )  # type: ignore
    
    width: bpy.props.FloatProperty(
        name="Width",
        description="Width of the lumber",
        default=0.0381,  # 1.5 inches
        min=0.001,
        unit='LENGTH',
        precision=4
    )  # type: ignore
    
    orientation: bpy.props.EnumProperty(
        name="Orientation",
        description="Orientation of the lumber profile",
        items=[
            ('HORIZONTAL', "Horizontal", "Add lumber as a horizontal part"),
            ('VERTICAL', "Vertical", "Add lumber as a vertical part"),
        ],
        default='HORIZONTAL'
    )  # type: ignore
    
    @classmethod
    def poll(cls, context):
        # Must be in a detail view scene
        return context.scene.get('IS_CROWN_DETAIL', False) or context.scene.get('IS_DETAIL_VIEW', False)
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=250)
    
    def draw(self, context):
        layout = self.layout
        
        layout.prop(self, "thickness")
        layout.prop(self, "width")
        
        layout.separator()
        layout.label(text="Orientation:")
        layout.prop(self, "orientation", expand=True)
    
    def execute(self, context):
        scene = context.scene
        hb_scene = scene.home_builder
        
        # Determine dimensions based on orientation
        if self.orientation == 'HORIZONTAL':
            rect_width = self.width
            rect_height = self.thickness
        else:  # VERTICAL
            rect_width = self.thickness
            rect_height = self.width
        
        # Create a rectangle polyline for the lumber profile
        lumber = hb_details.GeoNodePolyline()
        lumber.create("Solid Lumber")
        
        # Draw rectangle starting at origin
        lumber.set_point(0, Vector((0, 0, 0)))
        lumber.add_point(Vector((rect_width, 0, 0)))
        lumber.add_point(Vector((rect_width, rect_height, 0)))
        lumber.add_point(Vector((0, rect_height, 0)))
        lumber.close()
        
        # Mark as solid lumber
        lumber.obj['IS_SOLID_LUMBER'] = True
        lumber.obj['LUMBER_THICKNESS'] = self.thickness
        lumber.obj['LUMBER_WIDTH'] = self.width
        lumber.obj['LUMBER_ORIENTATION'] = self.orientation
        
        # Select the new object
        bpy.ops.object.select_all(action='DESELECT')
        lumber.obj.select_set(True)
        context.view_layer.objects.active = lumber.obj
        
        # Report dimensions in inches for user feedback
        thickness_in = self.thickness * 39.3701
        width_in = self.width * 39.3701
        self.report({'INFO'}, f"Added {thickness_in:.2f}\" x {width_in:.2f}\" solid lumber ({self.orientation.lower()})")
        
        return {'FINISHED'}


class hb_frameless_OT_browse_molding_library(bpy.types.Operator):
    """Browse and add molding profiles from the library"""
    bl_idname = "hb_frameless.browse_molding_library"
    bl_label = "Molding Library"
    bl_description = "Browse molding profiles and add them to the current detail"
    bl_options = {'REGISTER'}
    
    category: bpy.props.EnumProperty(
        name="Category",
        description="Molding category",
        items=lambda self, context: get_molding_categories()
    )  # type: ignore
    
    @classmethod
    def poll(cls, context):
        return context.scene.get('IS_CROWN_DETAIL', False) or context.scene.get('IS_DETAIL_VIEW', False)
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)
    
    def draw(self, context):
        layout = self.layout
        
        # Category selector
        layout.prop(self, "category", text="Category")
        
        layout.separator()
        
        # Get items in selected category
        items = get_molding_items(self.category)
        
        if not items:
            layout.label(text="No moldings in this category", icon='INFO')
            return
        
        # Display items in a grid
        box = layout.box()
        flow = box.column_flow(columns=2, align=True)
        
        for item in items:
            item_box = flow.box()
            item_box.label(text=item['name'])
            
            # Show thumbnail if available
            if item['thumbnail']:
                # Load thumbnail into preview collection
                icon_id = props_hb_frameless.load_library_thumbnail(item['thumbnail'], item['name'])
                if icon_id:
                    item_box.template_icon(icon_value=icon_id, scale=4.0)
            
            # Add button
            op = item_box.operator("hb_frameless.add_molding_profile", text="Add", icon='ADD')
            op.filepath = item['filepath']
            op.molding_name = item['name']
    
    def execute(self, context):
        return {'FINISHED'}




classes = (
    hb_frameless_OT_place_cabinet,
    hb_frameless_OT_load_cabinet_group_from_library,
    hb_frameless_OT_refresh_user_library,
    hb_frameless_OT_open_user_library_folder,
    hb_frameless_OT_delete_library_item,
    hb_frameless_OT_toggle_mode,
    hb_frameless_OT_update_cabinet_sizes,
    hb_frameless_OT_draw_cabinet,
    hb_frameless_OT_update_toe_kick_prompts,
    hb_frameless_OT_update_base_top_construction_prompts,
    hb_frameless_OT_update_drawer_front_height_prompts,
    hb_frameless_OT_update_door_and_drawer_front_style,
    hb_frameless_OT_add_door_style,
    hb_frameless_OT_remove_door_style,
    hb_frameless_OT_duplicate_door_style,
    hb_frameless_OT_assign_door_style_to_selected_fronts,
    hb_frameless_OT_update_fronts_from_style,
    hb_frameless_OT_create_cabinet_group,
    hb_frameless_OT_select_cabinet_group,
    hb_frameless_OT_save_cabinet_group_to_user_library,
    hb_frameless_OT_add_cabinet_style,
    hb_frameless_OT_remove_cabinet_style,
    hb_frameless_OT_duplicate_cabinet_style,
    hb_frameless_OT_assign_cabinet_style_to_selected_cabinets,
    hb_frameless_OT_assign_cabinet_style,
    hb_frameless_OT_update_cabinets_from_style,
    hb_frameless_OT_update_cabinet_pulls,
    hb_frameless_OT_update_pull_locations,
    hb_frameless_OT_update_pull_finish,
    hb_frameless_OT_create_crown_detail,
    hb_frameless_OT_delete_crown_detail,
    hb_frameless_OT_edit_crown_detail,
    hb_frameless_OT_assign_crown_to_cabinets,
    hb_frameless_OT_add_molding_profile,
    hb_frameless_OT_add_solid_lumber,
    hb_frameless_OT_browse_molding_library,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
