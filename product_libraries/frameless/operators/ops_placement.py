import bpy
import math
import os
from mathutils import Vector, Matrix
from bpy_extras import view3d_utils
from .. import types_frameless
from .. import props_hb_frameless
from ...common import types_appliances
from .... import hb_utils, hb_project, hb_snap, hb_placement, hb_details, hb_types, units

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
    
    # Appliance placement
    is_appliance: bpy.props.BoolProperty(name="Is Appliance", default=False)  # type: ignore
    appliance_type: bpy.props.StringProperty(name="Appliance Type", default="")  # type: ignore

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
    
    # Center snap state: None, 'gap', or 'cage'
    center_snap_state = None
    centerline_obj = None  # Visual indicator for center snap
    
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
        
        # Hood is placed above the range
        if self.is_appliance and self.appliance_type == 'HOOD':
            # Place hood at range height (36") + clearance (typically 24-30" above cooktop)
            return units.inch(54)  # 36" range + 18" clearance
        
        return 0
    
    def get_appliance_height(self, context) -> float:
        """Get the height for an appliance, handling special cases like hoods."""
        
        if self.appliance_type == 'HOOD':
            # Hood extends from its Z location to the ceiling
            main_scene = hb_project.get_main_scene()
            hb_props = main_scene.home_builder
            ceiling_height = hb_props.ceiling_height
            hood_z = self.get_cabinet_z_location(context)
            return ceiling_height - hood_z
        
        # For other appliances, use the class default
        appliance_class = self.get_appliance_class()
        if appliance_class:
            return appliance_class.height
        return units.inch(36)
    
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
        
        # Use appliance dimensions if placing an appliance
        if self.is_appliance:
            appliance_class = self.get_appliance_class()
            if appliance_class:
                # Use scene props for appliances that have configurable widths
                if self.appliance_type in ('RANGE', 'HOOD'):
                    appliance_width = props.range_width
                elif self.appliance_type == 'DISHWASHER':
                    appliance_width = props.dishwasher_width
                elif self.appliance_type == 'REFRIGERATOR':
                    appliance_width = props.refrigerator_cabinet_width
                else:
                    appliance_width = appliance_class.width
                
                self.individual_cabinet_width = appliance_width
                self.preview_cage.set_input('Dim X', appliance_width)
                self.preview_cage.set_input('Dim Y', appliance_class.depth)
                # Use get_appliance_height for special cases like hoods
                self.preview_cage.set_input('Dim Z', self.get_appliance_height(context))
            else:
                self.individual_cabinet_width = props.default_cabinet_width
                self.preview_cage.set_input('Dim X', self.individual_cabinet_width)
                self.preview_cage.set_input('Dim Y', self.get_cabinet_depth(context))
                self.preview_cage.set_input('Dim Z', self.get_cabinet_height(context))
            # Appliances don't fill gaps and are always quantity 1
            self.fill_mode = False
            self.cabinet_quantity = 1
            self.auto_quantity = False
        else:
            # Special cabinet types use specific widths and don't auto-fill
            if self.cabinet_name == 'Refrigerator Cabinet':
                self.individual_cabinet_width = props.refrigerator_cabinet_width
                self.fill_mode = False
                self.auto_quantity = False
            elif self.cabinet_name in ('Base Built-In', 'Tall Built-In'):
                self.individual_cabinet_width = props.range_width
                self.fill_mode = False
                self.auto_quantity = False
            else:
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
        # Larger text size for placement visibility
        placement_text_size = units.inch(3)
        
        # Total width dimension (above cabinets)
        self.dim_total_width = hb_types.GeoNodeDimension()
        self.dim_total_width.create("Dim_Total_Width")
        self.dim_total_width.set_input("Text Size", placement_text_size)
        self.dim_total_width.obj.show_in_front = True
        self.register_placement_object(self.dim_total_width.obj)
        
        # Left offset dimension
        self.dim_left_offset = hb_types.GeoNodeDimension()
        self.dim_left_offset.create("Dim_Left_Offset")
        self.dim_left_offset.set_input("Text Size", placement_text_size)
        self.dim_left_offset.obj.show_in_front = True
        self.register_placement_object(self.dim_left_offset.obj)
        
        # Right offset dimension
        self.dim_right_offset = hb_types.GeoNodeDimension()
        self.dim_right_offset.create("Dim_Right_Offset")
        self.dim_right_offset.set_input("Text Size", placement_text_size)
        self.dim_right_offset.obj.show_in_front = True
        self.register_placement_object(self.dim_right_offset.obj)
        
        # Center snap indicator line (green vertical line)
        self.create_centerline()
    
    def create_centerline(self):
        """Create a green vertical line to indicate center snap."""
        # Create a simple curve for the centerline
        curve_data = bpy.data.curves.new('Centerline', 'CURVE')
        curve_data.dimensions = '3D'
        
        spline = curve_data.splines.new('POLY')
        spline.points.add(1)  # 2 points total
        spline.points[0].co = (0, 0, 0, 1)
        spline.points[1].co = (0, 0, 1, 1)  # Will be scaled to wall height
        
        self.centerline_obj = bpy.data.objects.new('Centerline', curve_data)
        bpy.context.collection.objects.link(self.centerline_obj)
        
        # Line thickness
        curve_data.bevel_depth = 0.008
        
        # Create green material
        mat = bpy.data.materials.new('Centerline_Green')
        mat.diffuse_color = (0.0, 0.9, 0.2, 1.0)  # Viewport solid color
        mat.use_nodes = True
        # Set the principled BSDF color to green
        if mat.node_tree:
            bsdf = mat.node_tree.nodes.get('Principled BSDF')
            if bsdf:
                bsdf.inputs['Base Color'].default_value = (0.0, 0.9, 0.2, 1.0)
                # Use emission for visibility
                if 'Emission Color' in bsdf.inputs:
                    bsdf.inputs['Emission Color'].default_value = (0.0, 0.9, 0.2, 1.0)
                    bsdf.inputs['Emission Strength'].default_value = 1.0
                elif 'Emission' in bsdf.inputs:
                    bsdf.inputs['Emission'].default_value = (0.0, 0.9, 0.2, 1.0)
        self.centerline_obj.data.materials.append(mat)
        
        # Viewport display settings
        self.centerline_obj.color = (0.0, 0.9, 0.2, 1.0)  # Green in solid mode
        self.centerline_obj.show_in_front = True
        self.centerline_obj.hide_set(True)  # Hidden by default
        
        self.register_placement_object(self.centerline_obj)
    
    def cleanup_placement_objects(self):
        """Remove preview cage, dimensions, and centerline."""
        if self.preview_cage and self.preview_cage.obj:
            bpy.data.objects.remove(self.preview_cage.obj, do_unlink=True)
        if self.dim_total_width and self.dim_total_width.obj:
            bpy.data.objects.remove(self.dim_total_width.obj, do_unlink=True)
        if self.dim_left_offset and self.dim_left_offset.obj:
            bpy.data.objects.remove(self.dim_left_offset.obj, do_unlink=True)
        if self.dim_right_offset and self.dim_right_offset.obj:
            bpy.data.objects.remove(self.dim_right_offset.obj, do_unlink=True)
        if self.centerline_obj:
            bpy.data.objects.remove(self.centerline_obj, do_unlink=True)
            self.centerline_obj = None
        self.placement_objects = []
    
    def get_dimension_rotation(self, context, base_rotation_z):
        """Calculate dimension rotation to face the camera based on view angle.
        
        Returns: (rotation_tuple, is_plan_view)
        """
        # Get the 3D view
        region_3d = None
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                region_3d = area.spaces.active.region_3d
                break
        
        if not region_3d:
            return (0, 0, base_rotation_z), True
        
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
            return (0, 0, base_rotation_z), True
        else:
            # Elevation/3D view - rotate dimension to stand up (X rotation = 90)
            return (math.radians(90), 0, base_rotation_z), False
    
    def update_dimensions(self, context):
        """Update dimension positions and values."""
        if not self.preview_cage:
            return
        
        if not self.dim_total_width or not self.dim_left_offset or not self.dim_right_offset:
            return
        
        total_width = self.individual_cabinet_width * self.cabinet_quantity
        cabinet_height = self.get_cabinet_height(context)
        
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

            # Get rotation and view type
            dim_rotation, is_plan_view = self.get_dimension_rotation(context, wall_rotation_z)
            
            # Position dimensions based on view type
            if is_plan_view:
                # Plan view - position above cabinet so they don't overlap footprint
                dim_z = cabinet_height + units.inch(4)
                dim_z_offset = units.inch(8)  # Extra offset for left/right dims
                # Y offset from wall
                if self.place_on_front:
                    dim_y = -units.inch(2)
                else:
                    dim_y = wall_thickness + units.inch(2)
            else:
                # 3D/Elevation view - position at cursor height (mid-cabinet)
                dim_z = cabinet_height / 2
                dim_z_offset = 0  # All dims at same height
                # Y position inline with cabinet (no offset)
                if self.place_on_front:
                    dim_y = 0
                else:
                    dim_y = wall_thickness
            
            # Total width dimension
            local_pos = Vector((self.placement_x, dim_y, dim_z))
            self.dim_total_width.obj.location = wall_matrix @ local_pos
            self.dim_total_width.obj.rotation_euler = dim_rotation
            self.dim_total_width.obj.data.splines[0].points[1].co = (total_width, 0, 0, 1)
            self.dim_total_width.obj.hide_set(False)
            
            # Left offset dimension - from gap start to cabinet start
            if left_offset > units.inch(0.5):
                local_pos = Vector((self.gap_left_boundary, dim_y, dim_z + dim_z_offset))
                self.dim_left_offset.obj.location = wall_matrix @ local_pos
                self.dim_left_offset.obj.rotation_euler = dim_rotation
                self.dim_left_offset.obj.data.splines[0].points[1].co = (left_offset, 0, 0, 1)
                self.dim_left_offset.obj.hide_set(False)
            else:
                self.dim_left_offset.obj.hide_set(True)
            
            # Right offset dimension - from cabinet end to gap end
            if right_offset > units.inch(0.5):
                local_pos = Vector((self.placement_x + total_width, dim_y, dim_z + dim_z_offset))
                self.dim_right_offset.obj.location = wall_matrix @ local_pos
                self.dim_right_offset.obj.rotation_euler = dim_rotation
                self.dim_right_offset.obj.data.splines[0].points[1].co = (right_offset, 0, 0, 1)
                self.dim_right_offset.obj.hide_set(False)
            else:
                self.dim_right_offset.obj.hide_set(True)
        else:
            # Floor placement - just show total width
            base_rotation_z = self.preview_cage.obj.rotation_euler.z
            dim_rotation, is_plan_view = self.get_dimension_rotation(context, base_rotation_z)
            
            if is_plan_view:
                dim_z = cabinet_height + units.inch(4)
            else:
                dim_z = cabinet_height / 2
            
            self.dim_total_width.obj.location = self.preview_cage.obj.location.copy()
            self.dim_total_width.obj.location.z = dim_z
            self.dim_total_width.obj.rotation_euler = dim_rotation
            self.dim_total_width.obj.data.splines[0].points[1].co = (total_width, 0, 0, 1)
            self.dim_total_width.obj.hide_set(False)
            
            # Hide offset dimensions on floor
            self.dim_left_offset.obj.hide_set(True)
            self.dim_right_offset.obj.hide_set(True)
        
        # Update centerline visibility and position
        self.update_centerline(context, total_width, cabinet_height)

    def update_centerline(self, context, total_width, cabinet_height):
        """Update centerline indicator position and visibility."""
        if not self.centerline_obj:
            return
        
        if self.center_snap_state and self.selected_wall:
            # Show centerline at center of cabinet group
            wall_matrix = self.selected_wall.matrix_world
            wall = hb_types.GeoNodeWall(self.selected_wall)
            wall_thickness = wall.get_input('Thickness')
            wall_height = wall.get_input('Height')
            
            # Center X position
            center_x = self.placement_x + total_width / 2
            
            # Y position based on which side of wall
            if self.place_on_front:
                center_y = 0
            else:
                center_y = wall_thickness
            
            # Position in world space
            local_pos = Vector((center_x, center_y, 0))
            self.centerline_obj.location = wall_matrix @ local_pos
            self.centerline_obj.rotation_euler = self.selected_wall.rotation_euler
            
            # Extend to full wall height
            self.centerline_obj.data.splines[0].points[1].co = (0, 0, wall_height, 1)
            
            self.centerline_obj.hide_set(False)
        else:
            self.centerline_obj.hide_set(True)

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
        return math.ceil(gap_width / self.max_single_cabinet_width)

    def update_cabinet_quantity(self, context, new_quantity: int):
        """Update the number of cabinets and recalculate widths if position is locked."""
        new_quantity = max(1, new_quantity)
        if new_quantity != self.cabinet_quantity:
            self.cabinet_quantity = new_quantity
            self.array_modifier.count = self.cabinet_quantity
            
            # When position is locked (user set an offset), recalculate width to fill available space
            # Check for either position_locked flag or explicit offset values
            has_offset = self.left_offset is not None or self.right_offset is not None
            if (self.position_locked or has_offset) and self.current_gap_width > 0:
                self.individual_cabinet_width = self.current_gap_width / self.cabinet_quantity
            
            self.update_preview_cage()
            self.update_preview_position()
            self.update_dimensions(context)

    def find_nearest_wall_from_cursor(self, context):
        """Find the nearest wall based on projected cursor position."""
        from bpy_extras import view3d_utils
        from mathutils.geometry import intersect_line_plane, intersect_point_line
        
        snap_distance = units.inch(6)  # Snap to wall if within 6"
        
        # Project cursor onto floor plane
        region = self.region
        rv3d = region.data
        view_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, self.mouse_pos)
        view_dir = view3d_utils.region_2d_to_vector_3d(region, rv3d, self.mouse_pos)
        
        floor_point = intersect_line_plane(view_origin, view_origin + view_dir * 10000, Vector((0,0,0)), Vector((0,0,1)))
        
        if not floor_point:
            return None
        
        cursor_2d = Vector((floor_point.x, floor_point.y))
        
        # Find all walls
        nearest_wall = None
        nearest_distance = snap_distance
        
        for obj in context.scene.objects:
            if 'IS_WALL_BP' not in obj:
                continue
            
            wall = hb_types.GeoNodeWall(obj)
            wall_length = wall.get_input('Length')
            wall_thickness = wall.get_input('Thickness')
            
            # Get wall start and end points in world space (at wall centerline)
            wall_matrix = obj.matrix_world
            local_start = Vector((0, wall_thickness / 2, 0))
            local_end = Vector((wall_length, wall_thickness / 2, 0))
            
            world_start = wall_matrix @ local_start
            world_end = wall_matrix @ local_end
            
            # Project to 2D (floor plane)
            start_2d = Vector((world_start.x, world_start.y))
            end_2d = Vector((world_end.x, world_end.y))
            
            # Find closest point on wall line segment to cursor
            closest, percent = intersect_point_line(cursor_2d, start_2d, end_2d)
            closest = Vector(closest[:2])  # Ensure 2D
            
            # Clamp to segment (percent 0-1)
            if percent < 0:
                closest = start_2d
            elif percent > 1:
                closest = end_2d
            
            distance = (cursor_2d - closest).length
            
            # Check if within wall bounds and within snap distance
            if distance < nearest_distance and 0 <= percent <= 1:
                nearest_distance = distance
                nearest_wall = obj
                # Update hit_location so set_position_on_wall works correctly
                self.hit_location = Vector((floor_point.x, floor_point.y, 0))
        
        return nearest_wall

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
        
        # Determine which side of wall based on cursor position
        # Use different methods for plan view vs 3D view
        
        from bpy_extras import view3d_utils
        from mathutils.geometry import intersect_line_plane
        
        # Detect if we're in plan view (looking down) or 3D view
        region = self.region
        rv3d = region.data
        view_matrix = rv3d.view_matrix
        view_dir = Vector((view_matrix[2][0], view_matrix[2][1], view_matrix[2][2]))
        is_plan_view = abs(view_dir.z) > 0.7
        
        wall_center_y = wall_thickness / 2
        hysteresis = units.inch(1)
        
        if is_plan_view:
            # Plan view - project cursor onto floor plane for reliable detection
            view_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, self.mouse_pos)
            view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, self.mouse_pos)
            floor_point = intersect_line_plane(view_origin, view_origin + view_vector * 10000, Vector((0,0,0)), Vector((0,0,1)))
            
            if floor_point:
                local_cursor = self.selected_wall.matrix_world.inverted() @ floor_point
                if local_cursor.y < wall_center_y - hysteresis:
                    self.place_on_front = True
                elif local_cursor.y > wall_center_y + hysteresis:
                    self.place_on_front = False
                # Otherwise keep current side
            else:
                # Fallback
                if cursor_y < wall_center_y:
                    self.place_on_front = True
                else:
                    self.place_on_front = False
        else:
            # 3D view - use raycast hit position on wall surface
            if cursor_y < wall_center_y - hysteresis:
                self.place_on_front = True
            elif cursor_y > wall_center_y + hysteresis:
                self.place_on_front = False
            # Otherwise keep current side
        
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
            self.center_snap_state = None  # Fill mode doesn't center snap
        else:
            # User has typed a width - check for auto-snap positions
            total_width = self.individual_cabinet_width * self.cabinet_quantity
            left_gap = snap_x - gap_start
            
            # Check if cursor is over a GeoNodeCage with no height collision (e.g., window)
            cage_center_snap = self.get_cage_center_snap(cursor_x, total_width)
            
            # Reset center snap state
            self.center_snap_state = None
            
            if cage_center_snap is not None:
                # Snap to center on the cage (e.g., center base cabinet under window)
                snap_x = cage_center_snap
                self.center_snap_state = 'cage'
            else:
                # Calculate centered position in gap
                centered_x = gap_start + (gap_width - total_width) / 2
                distance_from_center = abs(snap_x - centered_x)
                
                # Snap to center if cursor is within 4 inches of center position
                if distance_from_center < units.inch(4):
                    snap_x = centered_x
                    self.center_snap_state = 'gap'
                # Snap to left if within 4 inches of left boundary
                elif left_gap < units.inch(4) and left_gap > 0:
                    snap_x = gap_start
        
        # Update preview cage
        self.preview_cage.set_input('Dim X', self.individual_cabinet_width)
        
        # Apply grid snapping when not using special snap modes
        # (center snap, cage snap, fill mode all set snap_x precisely)
        if not self.center_snap_state and not self.fill_mode:
            snap_x = hb_snap.snap_value_to_grid(snap_x)
        
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
            self.preview_cage.obj.location.x = snap_x + total_width
            self.preview_cage.obj.location.y = wall_thickness
            self.preview_cage.obj.rotation_euler = (0, 0, math.pi)
        
        # Update dimensions
        self.update_dimensions(context)

    def find_cabinet_bp(self, obj):
        """Find the cabinet or appliance base point (cage) from any child object."""
        if obj is None:
            return None
        
        # Check the object itself
        if 'IS_FRAMELESS_CABINET_CAGE' in obj or 'IS_APPLIANCE' in obj:
            return obj
        
        # Walk up parent hierarchy (but stop at walls)
        current = obj
        while current:
            if 'IS_WALL_BP' in current:
                return None  # Don't snap to wall-parented cabinets from floor mode
            if 'IS_FRAMELESS_CABINET_CAGE' in current or 'IS_APPLIANCE' in current:
                return current
            current = current.parent
        
        return None
    
    def set_position_free(self):
        """Position cabinet(s) on the floor, snapping to nearby cabinets."""
        if not self.preview_cage or not self.hit_location:
            return
        
        # Reset snap state
        self.snap_cabinet = None
        self.snap_side = None
        self.center_snap_state = None  # No center snapping on floor
        
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
            # Free placement on floor (snapped to grid)
            self.preview_cage.obj.parent = None
            self.preview_cage.obj.location = hb_snap.snap_vector_to_grid(Vector(self.hit_location))
            # Set Z location based on cabinet/appliance type
            if self.cabinet_type == 'UPPER' or (self.is_appliance and self.appliance_type == 'HOOD'):
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
        
        # Set Z location based on cabinet/appliance type
        if self.cabinet_type == 'UPPER' or (self.is_appliance and self.appliance_type == 'HOOD'):
            self.preview_cage.obj.location.z = self.get_cabinet_z_location(bpy.context)
        else:
            self.preview_cage.obj.location.z = self.snap_cabinet.location.z
        
        self.preview_cage.obj.rotation_euler = self.snap_cabinet.rotation_euler

    def assign_door_styles_to_cabinet(self, cabinet_obj):
        """Assign the active door style to all fronts in a cabinet.
        
        Should be called after drivers have calculated final sizes.
        """
        
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

    def get_appliance_class(self):
        """Get the appliance class based on appliance_type."""
        
        appliance_map = {
            'RANGE': types_appliances.Range,
            'DISHWASHER': types_appliances.Dishwasher,
            'REFRIGERATOR': types_appliances.Refrigerator,
            'HOOD': types_appliances.Hood,
            'COOKTOP': types_appliances.Cooktop,
            'WALL_OVEN': types_appliances.WallOven,
            'MICROWAVE': types_appliances.Microwave,
            'SINK': types_appliances.Sink,
        }
        
        if self.appliance_type in appliance_map:
            return appliance_map[self.appliance_type]
        return None
    
    def get_cabinet_class(self):
        # Handle appliances
        if self.is_appliance:
            appliance_class = self.get_appliance_class()
            if appliance_class:
                return appliance_class()
            return types_frameless.Cabinet()
        
        # Handle corner cabinets first
        if 'Diagonal Corner' in self.cabinet_name:
            if 'Base' in self.cabinet_name:
                return types_frameless.DiagonalCornerBaseCabinet()
            elif 'Tall' in self.cabinet_name:
                return types_frameless.DiagonalCornerTallCabinet()
            elif 'Upper' in self.cabinet_name:
                return types_frameless.DiagonalCornerUpperCabinet()
        
        if 'Pie Cut Corner' in self.cabinet_name or 'L-Shape Corner' in self.cabinet_name:
            if 'Base' in self.cabinet_name:
                return types_frameless.PieCutCornerBaseCabinet()
            elif 'Tall' in self.cabinet_name:
                return types_frameless.PieCutCornerTallCabinet()
            elif 'Upper' in self.cabinet_name:
                return types_frameless.PieCutCornerUpperCabinet()
        
        # Handle regular cabinets
        if self.cabinet_type == 'BASE':
            cabinet = types_frameless.BaseCabinet()
            if self.cabinet_name == 'Base Door':
                cabinet.default_exterior = "Doors"
            elif self.cabinet_name == 'Base Door Drw':
                cabinet.default_exterior = "Door Drawer"
            elif self.cabinet_name == 'Base Drawer':
                cabinet.default_exterior = "3 Drawers"
        elif self.cabinet_type == 'TALL':
            if self.cabinet_name == 'Refrigerator Cabinet':
                cabinet = types_frameless.RefrigeratorCabinet()
            else:
                cabinet = types_frameless.TallCabinet()
                if self.cabinet_name == 'Tall Stacked':
                    cabinet.is_stacked = True
        elif self.cabinet_type == 'UPPER':
            cabinet = types_frameless.UpperCabinet()
            if self.cabinet_name == 'Upper Stacked':
                cabinet.is_stacked = True
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
                
                if self.is_appliance:
                    # Appliances use their own dimensions but allow width override
                    cabinet.width = self.individual_cabinet_width
                    # Set height for appliances that need custom height (like hoods)
                    cabinet.height = self.get_appliance_height(context)
                    cabinet.create(self.cabinet_name or 'Appliance')
                else:
                    cabinet.width = self.individual_cabinet_width
                    cabinet.height = self.get_cabinet_height(context)
                    cabinet.depth = cabinet_depth
                    cabinet.create(f'Cabinet')
                
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
                
                if self.is_appliance:
                    # Appliances use their own dimensions but allow width override
                    cabinet.width = self.individual_cabinet_width
                    # Set height for appliances that need custom height (like hoods)
                    cabinet.height = self.get_appliance_height(context)
                    cabinet.create(self.cabinet_name or 'Appliance')
                else:
                    cabinet.width = self.individual_cabinet_width
                    cabinet.height = self.get_cabinet_height(context)
                    cabinet.depth = cabinet_depth
                    cabinet.create(f'Cabinet')
                
                # Calculate offset for this cabinet in the row
                # Offset in local X direction based on rotation
                local_offset = Vector((i * self.individual_cabinet_width, 0, 0))
                rotation_matrix = Matrix.Rotation(rotation_z, 4, 'Z')
                world_offset = rotation_matrix @ local_offset
                
                # Position on floor
                cabinet.obj.parent = None
                cabinet.obj.location = start_loc + world_offset
                cabinet.obj.rotation_euler = rotation
                
                # Set Z location based on cabinet/appliance type
                if self.cabinet_type == 'UPPER' or (self.is_appliance and self.appliance_type == 'HOOD'):
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
            
            # Add center snap indicator
            center_str = ""
            if self.center_snap_state == 'gap':
                center_str = " | ↔ CENTERED"
            elif self.center_snap_state == 'cage':
                center_str = " | ↔ CENTERED"
            
            text = f"{side_str} | {gap_str} | {offset_str} | {qty_str} × {individual_str} = {total_str}{center_str} | ↑/↓ qty | ←/→ offset | Enter place | Esc cancel"
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
        self.center_snap_state = None
        self.centerline_obj = None
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
            # Don't reset position_locked - keep user's offset when changing quantity
            return {'RUNNING_MODAL'}
        
        if event.type == 'DOWN_ARROW' and event.value == 'PRESS':
            # Accept any typed value first
            if self.placement_state == hb_placement.PlacementState.TYPING and self.typed_value:
                self.apply_typed_value()
            self.auto_quantity = False  # User is manually setting quantity
            self.update_cabinet_quantity(context, self.cabinet_quantity - 1)
            # Don't reset position_locked - keep user's offset when changing quantity
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
        
        # Fallback: if raycast missed, find nearest wall based on cursor position
        if not self.selected_wall:
            self.selected_wall = self.find_nearest_wall_from_cursor(context)
            if self.selected_wall:
                wall = hb_types.GeoNodeWall(self.selected_wall)
                self.wall_length = wall.get_input('Length')

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
                if not self.is_appliance:
                    # Cabinet-specific operations (skip for appliances)
                    # Assign the active cabinet style to the cabinet
                    bpy.ops.hb_frameless.assign_cabinet_style(cabinet_name=cabinet.obj.name)
                    # Force driver update for grandchild objects (workaround for Blender bug #133392)
                    hb_utils.run_calc_fix(context, cabinet.obj)
                    hb_utils.run_calc_fix(context, cabinet.obj)
                    # Assign door styles to all fronts (after drivers have calculated sizes)
                    self.assign_door_styles_to_cabinet(cabinet.obj)
                # Apply toggle mode for display
                bpy.ops.hb_frameless.toggle_mode(search_obj_name=cabinet.obj.name)
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
    
    # Markers that should be treated like cabinets for selection purposes
    CABINET_LIKE_MARKERS = ['IS_FRAMELESS_CABINET_CAGE', 'IS_APPLIANCE']

    def is_cabinet_like(self, obj):
        """Check if object has any cabinet-like marker."""
        for marker in self.CABINET_LIKE_MARKERS:
            if marker in obj:
                return True
        return False

    def toggle_obj(self, obj):
        if 'IS_WALL_BP' in obj or 'IS_ENTRY_DOOR_BP' in obj or 'IS_WINDOW_BP' in obj:
            return
        
        # Special handling for cabinet-like objects (cabinets, appliances, etc.)
        if self.toggle_type == "IS_FRAMELESS_CABINET_CAGE":
            if self.is_cabinet_like(obj):
                toggle_cabinet_color(obj, True, type_name=self.toggle_type)
            else:
                toggle_cabinet_color(obj, False, type_name=self.toggle_type)
        else:
            if self.toggle_type in obj:
                toggle_cabinet_color(obj, True, type_name=self.toggle_type)
            else:
                toggle_cabinet_color(obj, False, type_name=self.toggle_type)

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
        # Map appliance names to types
        appliance_map = {
            'Range': 'RANGE',
            'Dishwasher': 'DISHWASHER',
            'Refrigerator': 'REFRIGERATOR',
            'Range Hood': 'HOOD',
        }
        
        # Check if this is an appliance
        is_appliance = False
        appliance_type = ""
        for name, app_type in appliance_map.items():
            if name == self.cabinet_name:
                is_appliance = True
                appliance_type = app_type
                break
        
        if is_appliance:
            bpy.ops.hb_frameless.place_cabinet(
                'INVOKE_DEFAULT', 
                cabinet_type='BASE',
                cabinet_name=self.cabinet_name,
                is_appliance=True,
                appliance_type=appliance_type
            )
        else:
            # Map cabinet names to types
            if 'Base' in self.cabinet_name:
                cabinet_type = 'BASE'
            elif 'Tall' in self.cabinet_name or self.cabinet_name == 'Refrigerator Cabinet':
                cabinet_type = 'TALL'
            elif 'Upper' in self.cabinet_name:
                cabinet_type = 'UPPER'
            else:
                cabinet_type = 'BASE'
            bpy.ops.hb_frameless.place_cabinet(
                'INVOKE_DEFAULT', 
                cabinet_type=cabinet_type, 
                cabinet_name=self.cabinet_name
            )
        return {'FINISHED'}


classes = (
    hb_frameless_OT_place_cabinet,
    hb_frameless_OT_toggle_mode,
    hb_frameless_OT_draw_cabinet,
)

register, unregister = bpy.utils.register_classes_factory(classes)
