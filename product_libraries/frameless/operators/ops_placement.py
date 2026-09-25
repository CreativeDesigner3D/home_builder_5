import bpy
import math
import os
from mathutils import Vector, Matrix
from bpy_extras import view3d_utils
from .. import types_frameless
from .. import types_products
from mathutils.geometry import intersect_line_plane, intersect_point_line

# Part name to class mapping (module-level, not operator attribute)
PART_CLASS_MAP = {
    'Floating Shelves': types_products.FloatingShelf,
    'Valance': types_products.Valance,
    'Support Frame': types_products.SupportFrame,
    'Half Wall': types_products.HalfWall,
    'Misc Part': types_products.MiscPart,
    'Leg': types_products.Leg,
    'Tall Leg': types_products.TallLeg,
    'Upper Leg': types_products.UpperLeg,
    'Panel': types_products.Panel,
    'Corner Filler': types_products.CornerFiller,
    'Base Assembly': types_products.BaseAssembly,
}
from .. import props_hb_frameless
from .. import quiet_cages
from . import ops_base_assembly
from ...common import types_appliances, appliance_geo
from .... import hb_utils, hb_project, hb_snap, hb_placement, hb_details, hb_types, units

def has_child_item_type(obj,item_type):
    for child in obj.children_recursive:
        if item_type in child:
            return True
    return False

def _under_hidden_wall(obj):
    """True when obj hangs under a wall the user hid (Hide Wall / Isolate
    Selected Walls). Selection-mode highlighting must not resurrect these:
    cages are hidden while their mode is inactive, so the wall-hide pass
    skips them (already hidden), and force-showing them here would float
    openings in space where the hidden wall stands."""
    p = obj.parent
    while p is not None:
        if p.get('IS_WALL_BP'):
            try:
                return p.hide_viewport or p.hide_get()
            except RuntimeError:
                return p.hide_viewport
        p = p.parent
    return False

def _style_color(obj, fallback, highlight):
    """``obj``'s cabinet-style colour where that view mode is on, else
    ``fallback``.

    Style colours are a way of looking at the whole scene, so they have
    to outlast a selection-mode change: without this, entering a mode
    repainted every cage with the generic highlight and the styles
    vanished. ``highlight`` says whether this object is what the active
    mode offers to be clicked, which is what earns the see-through wash.
    Imported at call time -- the style pool lives in a sibling product
    library that imports this module.
    """
    try:
        from ...face_frame import props_hb_face_frame
        return props_hb_face_frame.style_color_for_object(
            obj, highlight=highlight) or fallback
    except Exception:
        return fallback


def toggle_cabinet_color(obj,toggle,type_name="",dont_show_parent=True):
    hb_props = bpy.context.window_manager.home_builder
    add_on_prefs = hb_props.get_user_preferences(bpy.context)

    if toggle:
        if dont_show_parent:
            if has_child_item_type(obj,type_name):
                return
        if _under_hidden_wall(obj):
            return
        obj.color = _style_color(obj, add_on_prefs.cabinet_color,
                                 highlight=True)
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
            obj.color = _style_color(
                obj, [1.000000, 1.000000, 1.000000, 1.000000],
                highlight=False)
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

APPLIANCE_CLASSES = {
    'RANGE': types_appliances.Range,
    'DISHWASHER': types_appliances.Dishwasher,
    'UNDER_COUNTER': types_appliances.UnderCounterAppliance,
    'REFRIGERATOR': types_appliances.Refrigerator,
    'HOOD': types_appliances.Hood,
    'COOKTOP': types_appliances.Cooktop,
    'WALL_OVEN': types_appliances.WallOven,
    'MICROWAVE': types_appliances.Microwave,
    'SINK': types_appliances.Sink,
}


def appliance_class_for(appliance_type):
    return APPLIANCE_CLASSES.get(appliance_type)


def build_cabinet_for(cabinet_name, cabinet_type, is_appliance=False,
                      appliance_type='', blind_side='Left'):
    """The class instance a catalog name stands for -- cabinet, corner
    cabinet, product or appliance -- ready for create(). The placement
    operator and the thumbnail renderer both build through here, so a
    picture in the browser is of the thing that gets placed."""
    # Handle appliances
    if is_appliance:
        appliance_class = appliance_class_for(appliance_type)
        if appliance_class:
            return appliance_class()
        return types_frameless.Cabinet()

    # Handle parts
    if cabinet_name in PART_CLASS_MAP:
        return PART_CLASS_MAP[cabinet_name]()

    # Handle corner cabinets first
    if 'Diagonal Corner' in cabinet_name:
        if 'Base' in cabinet_name:
            return types_frameless.DiagonalCornerBaseCabinet()
        elif 'Tall' in cabinet_name:
            return types_frameless.DiagonalCornerTallCabinet()
        elif 'Upper' in cabinet_name:
            return types_frameless.DiagonalCornerUpperCabinet()
    
    if 'Pie Cut Corner' in cabinet_name or 'L-Shape Corner' in cabinet_name:
        if 'Base' in cabinet_name:
            return types_frameless.PieCutCornerBaseCabinet()
        elif 'Tall' in cabinet_name:
            return types_frameless.PieCutCornerTallCabinet()
        elif 'Upper' in cabinet_name:
            return types_frameless.PieCutCornerUpperCabinet()
    
    # Handle regular cabinets
    if cabinet_name == 'Lap Drawer':
        cabinet = types_frameless.LapDrawerCabinet()
        return cabinet
    if cabinet_name.startswith('Blind '):
        # Which end goes into the corner: the end the run was placed
        # against, or left when placed away from any corner.
        blind_cls = {
            'BASE': types_frameless.BlindCornerBaseCabinet,
            'TALL': types_frameless.BlindCornerTallCabinet,
            'UPPER': types_frameless.BlindCornerUpperCabinet,
        }.get(cabinet_type, types_frameless.BlindCornerBaseCabinet)
        cabinet = blind_cls()
        cabinet.blind_side = blind_side
        return cabinet
    if cabinet_type == 'BASE':
        cabinet = types_frameless.BaseCabinet()
        if cabinet_name == 'Base Door':
            cabinet.default_exterior = "Doors"
        elif cabinet_name == 'Base Door Drw':
            cabinet.default_exterior = "Door Drawer"
        elif cabinet_name == 'Base Drawer':
            cabinet.default_exterior = "3 Drawers"
        elif cabinet_name == 'Sink Base':
            cabinet.default_exterior = "Sink"
        elif cabinet_name == 'Base Open':
            cabinet.default_exterior = "Open"
    elif cabinet_type == 'TALL':
        if cabinet_name == 'Refrigerator Cabinet':
            cabinet = types_frameless.RefrigeratorCabinet()
        else:
            cabinet = types_frameless.TallCabinet()
            if cabinet_name == 'Tall Stacked':
                cabinet.is_stacked = True
            elif cabinet_name == 'Tall Open':
                cabinet.default_exterior = "Open"
    elif cabinet_type == 'UPPER':
        cabinet = types_frameless.UpperCabinet()
        if cabinet_name == 'Upper Stacked':
            cabinet.is_stacked = True
        elif cabinet_name == 'Upper Open':
            cabinet.default_exterior = "Open"
    else:
        cabinet = types_frameless.Cabinet()    
    return cabinet    



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
    
    # Corner cabinet placement side (right side needs -90° rotation)
    corner_right_side: bool = False
    
    # Placement dimensions

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

    def is_blind_corner(self):
        return self.cabinet_name.startswith('Blind ')

    def is_base_assembly(self):
        return self.cabinet_name == 'Base Assembly'

    # What stops a base assembly running along a wall. Cabinets do not:
    # the base goes under them.
    BASE_ASSEMBLY_OBSTACLES = ('IS_BASE_ASSEMBLY', 'IS_APPLIANCE',
                               'IS_ENTRY_DOOR_BP', 'IS_CLOSET_STARTER_CAGE')

    def blocks_placement(self, obj):
        if self.is_base_assembly():
            return any(obj.get(tag) for tag in self.BASE_ASSEMBLY_OBSTACLES)
        return super().blocks_placement(obj)

    def blind_side_for_placement(self):
        """The end of the run that reaches a wall end: that is the end
        going into the corner. Away from both ends, the left."""
        if not self.selected_wall:
            return 'Left'
        tol = units.inch(1.0)
        total = self.individual_cabinet_width * self.cabinet_quantity
        if self.placement_x + total >= self.wall_length - tol:
            return 'Right'
        return 'Left'

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
        if (self.cursor_z_tracking or self.align_top_to_base) and self.cursor_z_product_height > 0:
            return self.cursor_z_product_height
        props = context.scene.hb_frameless
        if self.cabinet_name == 'Lap Drawer':
            return props.top_drawer_front_height
        if self.is_base_assembly():
            return props.default_toe_kick_height
        if self.cabinet_type == 'BASE':
            return props.base_cabinet_height
        elif self.cabinet_type == 'TALL':
            return props.tall_cabinet_height
        elif self.cabinet_type == 'UPPER':
            return props.upper_cabinet_height
        return props.base_cabinet_height

    def keeps_natural_z(self) -> bool:
        """Whether this product sits at its own height off the wall too.
        Uppers hang at the wall-cabinet height, hoods over the range, a
        support frame under the base top, and a lap drawer at the top of
        the base run -- none of them belong on the floor or at a snap
        target's height."""
        return (self.align_top_to_base
                or self.cabinet_type == 'UPPER'
                or self.cabinet_name == 'Lap Drawer'
                or (self.is_appliance and self.appliance_type == 'HOOD'))

    def get_cabinet_z_location(self, context) -> float:
        # Floating shelves track cursor Z position
        if self.cursor_z_tracking:
            return self.cursor_z
        
        # Support Frame: top aligns with base cabinet top
        if self.align_top_to_base:
            props = context.scene.hb_frameless
            frame_height = self.preview_cage.get_input('Dim Z') if self.preview_cage else units.inch(4)
            return props.base_cabinet_height - frame_height
        
        props = context.scene.hb_frameless
        
        if self.cabinet_name == 'Lap Drawer':
            return props.base_cabinet_height - props.top_drawer_front_height
        
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
            # Hood extends from its Z location to the ceiling -- this
            # room's ceiling, which is not the main scene's when the
            # rooms have different wall heights.
            hb_props = hb_project.get_settings_scene(context).home_builder
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
            elif self.is_blind_corner():
                # One cabinet at its own width: the blind is sized for
                # the adjacent wall, so it neither fills nor repeats.
                self.individual_cabinet_width = {
                    'TALL': props.tall_width_blind,
                    'UPPER': props.upper_width_blind,
                }.get(self.cabinet_type, props.base_width_blind)
                self.fill_mode = False
                self.auto_quantity = False
                self.cabinet_quantity = 1
            elif 'Corner' in self.cabinet_name:
                # Corner cabinets use corner size for both width and depth
                if 'Base' in self.cabinet_name:
                    corner_size = props.base_inside_corner_size
                elif 'Tall' in self.cabinet_name:
                    corner_size = props.tall_inside_corner_size
                elif 'Upper' in self.cabinet_name:
                    corner_size = props.upper_inside_corner_size
                else:
                    corner_size = props.base_inside_corner_size
                self.individual_cabinet_width = corner_size
                self.fill_mode = False
                self.auto_quantity = False
                self.cabinet_quantity = 1
            elif self.cabinet_name in PART_CLASS_MAP:
                # Parts use their own default dimensions
                part_instance = PART_CLASS_MAP[self.cabinet_name]()
                self.individual_cabinet_width = part_instance.width
                if (self.cursor_z_tracking or self.align_top_to_base
                        or self.is_base_assembly()):
                    # Fill-gap products (Floating Shelves, Support Frame, etc.) with qty 1
                    self.auto_quantity = False
                    self.cabinet_quantity = 1
                else:
                    self.fill_mode = False
                    self.auto_quantity = False
                    self.cabinet_quantity = 1
            else:
                self.individual_cabinet_width = props.default_cabinet_width
            self.preview_cage.set_input('Dim X', self.individual_cabinet_width)
            if 'Corner' in self.cabinet_name:
                self.preview_cage.set_input('Dim Y', corner_size)
            elif self.cabinet_name in PART_CLASS_MAP:
                part_instance = PART_CLASS_MAP[self.cabinet_name]()
                self.preview_cage.set_input('Dim Y', part_instance.depth)
                self.preview_cage.set_input('Dim Z', part_instance.height)
            else:
                self.preview_cage.set_input('Dim Y', self.get_cabinet_depth(context))
            if self.cabinet_name not in PART_CLASS_MAP:
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
    
    def cleanup_placement_objects(self):
        """Remove the preview cage and the dimension overlay."""
        if self.preview_cage and self.preview_cage.obj:
            bpy.data.objects.remove(self.preview_cage.obj, do_unlink=True)
        self.remove_placement_dim_handler()
        self.placement_objects = []

    # ---- Placement dimensions ---------------------------------------------
    # Drawn in screen space by the shared handler (hb_placement), the way
    # the face frame library annotates placement: a spec list rebuilt
    # whenever the cage moves, no dimension objects in the scene. Green
    # marks a snap -- the centre of a gap or a neighbouring cabinet.

    SNAP_GREEN = (0.30, 0.95, 0.40, 1.0)

    def update_dimensions(self, context):
        """Rebuild the overlay for the cage's current position: the
        total width, the left / right offsets inside the gap on a wall,
        and the floor height for cursor-Z products."""
        if not self.preview_cage or not self.preview_cage.obj:
            return
        if getattr(self, '_placement_dim_handle', None) is None:
            return
        if self.selected_wall and not self.free_standing:
            specs = self._dim_specs_on_wall(context)
        else:
            specs = self._dim_specs_free(context)
            if self.facing_aisle is not None:
                start, end = self.facing_aisle
                lift = Vector((0.0, 0.0, self.get_cabinet_height(context) + units.inch(4.0)))
                specs.append(hb_placement.PlacementDimSpec(
                    start + lift, end + lift,
                    units.unit_to_string(context.scene.unit_settings,
                                         (end - start).length),
                    self.SNAP_GREEN))
        specs.extend(self._dim_specs_height(context))
        self._placement_dim_specs = specs
        self._facing_arrow_segments = self.build_facing_arrow()
        if context.area:
            context.area.tag_redraw()

    def _dim_specs_on_wall(self, context):
        """Wall case: coordinates are wall-local (the cage is parented to
        the wall) and the wall matrix maps them into world space. Total
        width sits 4" above the cabinet top, the offsets 8" above so the
        two rows stay clear of each other."""
        cage_obj = self.preview_cage.obj
        total_width = self.individual_cabinet_width * self.cabinet_quantity
        cabinet_height = self.get_cabinet_height(context)
        wall = hb_types.GeoNodeWall(self.selected_wall)
        wall_thickness = wall.get_input('Thickness')
        wm = self.selected_wall.matrix_world
        unit_settings = context.scene.unit_settings

        z_top = cage_obj.location.z + cabinet_height
        z_total = z_top + units.inch(4.0)
        z_offset = z_top + units.inch(8.0)
        # Inset toward the room so the line clears the wall surface.
        if self.place_on_front:
            y_dim = -units.inch(2.0)
        else:
            y_dim = wall_thickness + units.inch(2.0)

        # Centre snap balances the two offsets, so it tints all three;
        # a cabinet snap only says where the cabinet is.
        centred = bool(self.center_snap_state)
        total_color = self.SNAP_GREEN if (centred or self.snap_cabinet) else None
        offset_color = self.SNAP_GREEN if centred else None

        x0 = self.placement_x
        x1 = x0 + total_width
        specs = [hb_placement.PlacementDimSpec(
            wm @ Vector((x0, y_dim, z_total)),
            wm @ Vector((x1, y_dim, z_total)),
            units.unit_to_string(unit_settings, total_width),
            total_color)]

        left_offset = x0 - self.gap_left_boundary
        if left_offset > units.inch(0.5):
            specs.append(hb_placement.PlacementDimSpec(
                wm @ Vector((self.gap_left_boundary, y_dim, z_offset)),
                wm @ Vector((x0, y_dim, z_offset)),
                units.unit_to_string(unit_settings, left_offset),
                offset_color))
        right_offset = self.gap_right_boundary - x1
        if right_offset > units.inch(0.5):
            specs.append(hb_placement.PlacementDimSpec(
                wm @ Vector((x1, y_dim, z_offset)),
                wm @ Vector((self.gap_right_boundary, y_dim, z_offset)),
                units.unit_to_string(unit_settings, right_offset),
                offset_color))

        # The corner fillers the commit will build, where the offsets
        # would be: a run that reaches a corner has no offset there.
        filler_w = types_products.CORNER_FILLER_WIDTH
        filler_text = units.unit_to_string(unit_settings, filler_w) + " Filler"
        reaches_left, reaches_right = self.corner_fillers_reached()
        if reaches_left:
            specs.append(hb_placement.PlacementDimSpec(
                wm @ Vector((self.gap_left_boundary - filler_w, y_dim, z_offset)),
                wm @ Vector((self.gap_left_boundary, y_dim, z_offset)),
                filler_text, self.SNAP_GREEN))
        if reaches_right:
            specs.append(hb_placement.PlacementDimSpec(
                wm @ Vector((self.gap_right_boundary, y_dim, z_offset)),
                wm @ Vector((self.gap_right_boundary + filler_w, y_dim, z_offset)),
                filler_text, self.SNAP_GREEN))
        return specs

    def _dim_specs_free(self, context):
        """Off a wall there is no gap to annotate: just the total width,
        above the cabinet, green while snapped to a neighbour."""
        cage_obj = self.preview_cage.obj
        total_width = self.individual_cabinet_width * self.cabinet_quantity
        cabinet_height = self.get_cabinet_height(context)
        # A fresh matrix: the cage was placed this same tick, and
        # matrix_world would still say where it used to be.
        m = hb_placement.pending_world_matrix(cage_obj)
        z = cabinet_height + units.inch(4.0)
        return [hb_placement.PlacementDimSpec(
            m @ Vector((0.0, 0.0, z)),
            m @ Vector((total_width, 0.0, z)),
            units.unit_to_string(context.scene.unit_settings, total_width),
            self.SNAP_GREEN if self.snap_cabinet else None)]

    def _dim_specs_height(self, context):
        """Floor-to-bottom height for cursor-Z products (floating
        shelves, valances), beside the cabinet's left edge."""
        if not self.cursor_z_tracking:
            return []
        cage_obj = self.preview_cage.obj
        height = cage_obj.location.z
        if height <= units.inch(0.5):
            return []
        unit_settings = context.scene.unit_settings
        if self.selected_wall:
            wall = hb_types.GeoNodeWall(self.selected_wall)
            wall_thickness = wall.get_input('Thickness')
            wm = self.selected_wall.matrix_world
            if self.place_on_front:
                y_dim = -units.inch(2.0)
            else:
                y_dim = wall_thickness + units.inch(2.0)
            x = self.placement_x - units.inch(2.0)
            s = wm @ Vector((x, y_dim, 0.0))
            e = wm @ Vector((x, y_dim, height))
        else:
            m = hb_placement.pending_world_matrix(cage_obj)
            s = m @ Vector((-units.inch(2.0), 0.0, -height))
            e = m @ Vector((-units.inch(2.0), 0.0, 0.0))
        return [hb_placement.PlacementDimSpec(
            s, e, units.unit_to_string(unit_settings, height), None)]

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
        if self.is_blind_corner():
            new_quantity = 1
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
            # A hidden wall is not somewhere to put anything.
            if not hb_placement.object_shown(obj, context.space_data):
                continue
            
            wall = hb_types.GeoNodeWall(obj)
            # Skip walls whose geo node modifier has been applied - they're
            # static meshes now and can't report Length/Thickness parametrically.
            if not wall.has_modifier():
                continue
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

    # ---- Corner fillers ---------------------------------------------------
    # A cabinet that lands in an inside corner cannot open its door into
    # the wall beside it. The corner keeps 1.5" for an L-shaped filler
    # (types_products.CornerFiller) whose face lines up with the doors;
    # the reservation moves the gap boundary in, so the placement, the
    # dims and fill mode all see the corner as already spoken for, and
    # the commit builds the filler in the space it kept.

    def wants_corner_fillers(self):
        """Cabinets only: appliances, parts, corner cabinets and the
        cursor-height products close no corner."""
        return (not self.is_appliance
                and self.cabinet_name not in PART_CLASS_MAP
                and 'Corner' not in self.cabinet_name
                and not self.is_blind_corner()
                and not self.cursor_z_tracking
                and not self.align_top_to_base)

    def inside_corner(self, wall_obj, side):
        """Whether this wall's `side` end ('left' / 'right') meets a
        connected wall that turns toward the placement side -- an inside
        corner from where the cabinet stands. The neighbour's away
        vector is read in this wall's frame, the way the gap scan does,
        so wall angles and draw order do not matter."""
        try:
            wall = hb_types.GeoNodeWall(wall_obj)
            adj = wall.get_connected_wall(direction=side, include_loop_seam=True)
            if not adj:
                return False
            adj_obj = adj.obj
            adj_len = adj.get_input('Length')
        except Exception:
            return False
        away = -1.0 if side == 'left' else 1.0
        away_world = adj_obj.matrix_world.to_3x3() @ Vector((away, 0.0, 0.0))
        away_local_y = (wall_obj.matrix_world.inverted().to_3x3() @ away_world).y
        if self.place_on_front:
            return away_local_y < -0.001
        return away_local_y > 0.001

    def blind_corner_reach(self, context, side):
        """How far a blind corner cabinet on the wall connected at this
        wall's `side` end reaches into this wall, or 0.0 with none there.
        Its blind panel is the corner as far as the run on this wall is
        concerned, so the run keeps a filler against it the way it does
        against a wall. The footprint is mapped into this wall's frame
        the way the gap scan maps its adjacent-wall intrusions."""
        try:
            adj = hb_types.GeoNodeWall(self.selected_wall).get_connected_wall(
                direction=side, include_loop_seam=True)
        except Exception:
            return 0.0
        if not adj:
            return 0.0
        z0 = self.get_cabinet_z_location(context)
        z1 = z0 + self.get_cabinet_height(context)
        to_wall = self.selected_wall.matrix_world.inverted()
        reach = 0.0
        for child in adj.obj.children:
            if not child.get('IS_BLIND_CORNER'):
                continue
            cage = hb_types.GeoNodeCage(child)
            dim_x, dim_y, dim_z = (cage.get_input('Dim X'), cage.get_input('Dim Y'),
                                   cage.get_input('Dim Z'))
            if not (z0 < child.location.z + dim_z and child.location.z < z1):
                continue
            for corner in ((0, 0, 0), (dim_x, 0, 0), (0, -dim_y, 0), (dim_x, -dim_y, 0)):
                x = (to_wall @ (child.matrix_world @ Vector(corner))).x
                if side == 'left':
                    reach = max(reach, x)
                else:
                    reach = max(reach, self.wall_length - x)
        return reach

    def reserve_corner_fillers(self, context, gap_start, gap_end, snap_x):
        """Move a gap boundary that sits at an inside corner -- the wall
        itself, or a blind corner cabinet standing in it -- in by the
        filler width, remembering which ends were reserved for the
        commit. Returns the adjusted (gap_start, gap_end, snap_x)."""
        self.corner_filler_left = False
        self.corner_filler_right = False
        if not self.wants_corner_fillers() or not self.selected_wall:
            return gap_start, gap_end, snap_x
        width = types_products.CORNER_FILLER_WIDTH
        tol = units.inch(0.05)

        def at_corner(distance, side):
            """`distance` is the gap boundary's from that end of the wall."""
            if distance <= tol:
                return True
            reach = self.blind_corner_reach(context, side)
            return reach > 0.0 and abs(distance - reach) <= tol

        if (at_corner(gap_start, 'left')
                and self.inside_corner(self.selected_wall, 'left')):
            gap_start += width
            self.corner_filler_left = True
        if (at_corner(self.wall_length - gap_end, 'right')
                and self.inside_corner(self.selected_wall, 'right')):
            gap_end -= width
            self.corner_filler_right = True
        if gap_end - gap_start < units.inch(1.0):
            # Too tight to keep either: give the corners back.
            self.corner_filler_left = self.corner_filler_right = False
            return gap_start, gap_end, snap_x
        total = self.individual_cabinet_width * self.cabinet_quantity
        snap_x = max(gap_start, min(snap_x, gap_end - total))
        return gap_start, gap_end, snap_x

    def create_corner_filler(self, context, wall_thickness, x, cabinet_on_right):
        """Build the filler for one corner, standing in the reserved 1.5"
        that starts at wall-local `x`, sized to the cabinet being placed
        and reaching out to its door plane."""
        filler = types_products.CornerFiller()
        filler.width = types_products.CORNER_FILLER_WIDTH
        filler.height = self.get_cabinet_height(context)
        filler.depth = self.get_cabinet_depth(context) + types_products.FRONT_THICKNESS
        props = context.scene.hb_frameless
        has_kick = self.cabinet_type in ('BASE', 'TALL')
        filler.toe_kick_height = props.default_toe_kick_height if has_kick else 0.0
        filler.toe_kick_setback = props.default_toe_kick_setback if has_kick else 0.0
        # A back-side run is turned 180, which swaps which local side
        # the cabinet is on.
        filler.cabinet_on_right = cabinet_on_right if self.place_on_front else not cabinet_on_right
        filler.create('Corner Filler')
        filler.obj.parent = self.selected_wall
        filler.obj.location.z = self.get_cabinet_z_location(context)
        if self.place_on_front:
            filler.obj.location.x = x
            filler.obj.location.y = 0
            filler.obj.rotation_euler = (0, 0, 0)
        else:
            filler.obj.location.x = x + filler.width
            filler.obj.location.y = wall_thickness
            filler.obj.rotation_euler = (0, 0, math.pi)
        return filler

    def corner_fillers_reached(self):
        """(left, right): the reserved corners the cabinet run actually
        touches, which are the ones that get a filler."""
        if not self.selected_wall:
            return False, False
        tol = units.inch(0.05)
        total = self.individual_cabinet_width * self.cabinet_quantity
        left = (getattr(self, 'corner_filler_left', False)
                and abs(self.placement_x - self.gap_left_boundary) <= tol)
        right = (getattr(self, 'corner_filler_right', False)
                 and abs(self.placement_x + total - self.gap_right_boundary) <= tol)
        return left, right

    def create_corner_fillers(self, context, wall_thickness):
        """The fillers for the corners the cabinet run actually reaches:
        one at each reserved end the run touches."""
        fillers = []
        width = types_products.CORNER_FILLER_WIDTH
        reaches_left, reaches_right = self.corner_fillers_reached()
        if reaches_left:
            fillers.append(self.create_corner_filler(
                context, wall_thickness, self.gap_left_boundary - width, True))
        if reaches_right:
            fillers.append(self.create_corner_filler(
                context, wall_thickness, self.gap_right_boundary, False))
        return fillers

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
        
        # Track cursor Z for products that follow the cursor height (e.g. Floating Shelves)
        if self.cursor_z_tracking:
            z_inches = round(units.meter_to_inch(local_loc.z))
            z_inches = max(0, z_inches)  # Don't go below floor
            self.cursor_z = units.inch(z_inches)
        
        self.update_place_on_front(wall_thickness, cursor_y)

        # Find available gap, filtering by which side we're placing on
        gap_start, gap_end, snap_x = self.find_placement_gap_by_side(
            self.selected_wall,
            cursor_x,
            self.individual_cabinet_width,
            self.place_on_front,
            wall_thickness,
            object_z_start=self.get_cabinet_z_location(context),
            object_height=self.get_cabinet_height(context),
            object_depth=self.get_cabinet_depth(context),
            exclude_obj=self.preview_cage.obj if self.preview_cage else None,
        )
        self.finish_position_on_wall(context, wall_thickness, cursor_x,
                                     gap_start, gap_end, snap_x)

    def update_place_on_front(self, wall_thickness, cursor_y):
        """Which side of the selected wall the cursor is on, with an inch
        of hysteresis so the cabinet does not flip sides at the centre.
        Plan view and 3D view read the cursor differently."""
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

    def finish_position_on_wall(self, context, wall_thickness, cursor_x,
                                gap_start, gap_end, snap_x):
        """The rest of wall placement once the gap under the cursor is
        known: corner fillers, fill or snap, and the preview cage."""
        # An inside corner keeps 1.5" for the filler that closes it, so
        # the cabinet lands beside the filler rather than in the corner.
        gap_start, gap_end, snap_x = self.reserve_corner_fillers(
            context, gap_start, gap_end, snap_x)

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
                # Snap to right if within 4 inches of right boundary
                elif 0 < gap_end - (snap_x + total_width) < units.inch(4):
                    snap_x = gap_end - total_width
        
        # Corner cabinet special handling
        is_corner = 'Corner' in self.cabinet_name
        if is_corner:
            corner_snap_threshold = self.individual_cabinet_width
            near_left = cursor_x < corner_snap_threshold
            near_right = cursor_x > (self.wall_length - corner_snap_threshold)
            
            if near_left or near_right:
                self.corner_right_side = near_right
                
                if self.corner_right_side:
                    snap_x = self.wall_length
                else:
                    snap_x = 0
                
                self.placement_x = snap_x
                
                self.preview_cage.obj.parent = self.selected_wall
                self.preview_cage.obj.location.z = self.get_cabinet_z_location(context)
                self.preview_cage.obj.location.y = 0
                
                if self.corner_right_side:
                    self.preview_cage.obj.location.x = self.wall_length
                    self.preview_cage.obj.rotation_euler = (0, 0, math.radians(-90))
                else:
                    self.preview_cage.obj.location.x = 0
                    self.preview_cage.obj.rotation_euler = (0, 0, 0)
            else:
                # Not near a corner - position freely along wall
                self.corner_right_side = False
                snap_x = hb_snap.snap_value_to_grid(cursor_x)
                snap_x = max(0, min(snap_x, self.wall_length - self.individual_cabinet_width))
                self.placement_x = snap_x
                
                self.preview_cage.obj.parent = self.selected_wall
                self.preview_cage.obj.location.z = self.get_cabinet_z_location(context)
                self.preview_cage.obj.location.x = snap_x
                self.preview_cage.obj.location.y = 0
                self.preview_cage.obj.rotation_euler = (0, 0, 0)
        else:
            # Update preview cage
            self.preview_cage.set_input('Dim X', self.individual_cabinet_width)
            
            # Apply grid snapping when not using special snap modes
            # (center snap, cage snap, fill mode all set snap_x precisely)
            # A cabinet sitting on a gap boundary stays there: the
            # boundary beside a corner filler is off the grid, and a
            # cabinet nudged off it would lose its filler.
            total_width = self.individual_cabinet_width * self.cabinet_quantity
            tol = units.inch(0.05)
            on_boundary = (abs(snap_x - gap_start) <= tol
                           or abs(snap_x + total_width - gap_end) <= tol)
            if not self.center_snap_state and not self.fill_mode and not on_boundary:
                snap_x = hb_snap.snap_value_to_grid(snap_x)
                snap_x = max(gap_start, min(snap_x, gap_end - total_width))
            
            # Clamp snap_x to wall bounds
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

    # ---- Free-standing placement -------------------------------------------
    # R turns the cabinet a quarter turn at a time. On the floor that is
    # simply its heading. Against a wall a quarter turn means peninsula:
    # the cabinet's END goes flush to the wall and the run projects into
    # the room. A Sink Base over a Range -- or any turned cabinet over a
    # range or a base cabinet -- stands as an island facing it across an
    # aisle. All three finish unparented, the way an island does, because
    # everything downstream reads a wall's children as running along it.

    FACING_AISLE = units.inch(48.0)

    def is_quarter_turned(self):
        """A quarter turn (90 / 270) is the signal that wall placement
        should go peninsula; 0 / 180 stay on the wall, which owns facing."""
        return abs((self.free_rotation_z % math.pi) - math.pi / 2.0) < 0.01

    def facing_target(self):
        """The range or base cabinet under the cursor that this cabinet
        should stand facing, or None. A Sink Base takes a range of its
        own accord; anything else asks by being turned with R first."""
        turned = self.free_rotation_z != 0.0
        if self.cabinet_name != 'Sink Base' and not turned:
            return None
        if self.is_appliance or self.cabinet_name in PART_CLASS_MAP:
            return None
        current = self.hit_object
        while current is not None:
            if (current.get('IS_APPLIANCE')
                    and current.get('APPLIANCE_TYPE') == 'RANGE'
                    and not current.get('IS_CABINET_APPLIANCE')):
                return current
            if (turned and current.get('IS_FRAMELESS_CABINET_CAGE')
                    and current.get('CABINET_TYPE') == 'BASE'):
                return current
            current = current.parent
        return None

    def release_wall_state(self, context):
        """Going free-standing drops everything that belongs to a wall
        gap: fillers, offsets, centre snaps, and a gap-filled width."""
        self.free_standing = True
        self.corner_filler_left = False
        self.corner_filler_right = False
        self.left_offset = None
        self.right_offset = None
        self.position_locked = False
        self.center_snap_state = None
        self.snap_cabinet = None
        self.snap_side = None
        if self.fill_mode:
            # Nothing to fill off the wall: back to the width it came in at.
            if self.auto_quantity:
                self.cabinet_quantity = 1
                self.array_modifier.count = 1
            self.individual_cabinet_width = self.default_width
            self.preview_cage.set_input('Dim X', self.individual_cabinet_width)

    def stand_free(self, context, location, rotation_z):
        cage_obj = self.preview_cage.obj
        cage_obj.parent = None
        cage_obj.location = location
        cage_obj.rotation_euler = (0.0, 0.0, rotation_z)
        total = self.individual_cabinet_width * self.cabinet_quantity
        self.gap_left_boundary = 0
        self.gap_right_boundary = total
        self.current_gap_width = total

    def set_position_peninsula(self, context):
        """The cabinet's end flush against the wall, the run projecting
        into the room. Its footprint ALONG the wall is its depth, which
        follows the cursor and stops at whatever already stands on the
        wall, through the same gap scan ordinary placement uses."""
        self.release_wall_state(context)
        wall_obj = self.selected_wall
        wall = hb_types.GeoNodeWall(wall_obj)
        wall_thickness = wall.get_input('Thickness')
        wall_length = wall.get_input('Length')
        local_hit = wall_obj.matrix_world.inverted() @ Vector(self.hit_location)
        self.update_place_on_front(wall_thickness, local_hit.y)
        room_dir = -1.0 if self.place_on_front else 1.0
        flush_y = 0.0 if self.place_on_front else wall_thickness

        total = self.individual_cabinet_width * self.cabinet_quantity
        depth = self.get_cabinet_depth(context)
        z = self.get_cabinet_z_location(context)

        gap_start, gap_end, span_start = self.find_placement_gap_by_side(
            wall_obj, local_hit.x, depth, self.place_on_front, wall_thickness,
            object_z_start=z, object_height=self.get_cabinet_height(context),
            object_depth=total, exclude_obj=self.preview_cage.obj)
        if gap_start is None:
            gap_start, gap_end = 0.0, wall_length
        span_start = hb_snap.snap_value_to_grid(local_hit.x - depth / 2.0)
        span_start = max(gap_start, min(span_start, gap_end - depth))
        span_end = span_start + depth

        # Two headings stand square to the wall. R is read against the
        # wall rather than the room: one press faces one way along it,
        # three the other, whichever way the wall itself runs.
        wall_rot_z = wall_obj.matrix_world.to_euler().z
        half_pi = math.pi / 2.0
        theta = (half_pi if (self.free_rotation_z % (2.0 * math.pi)) < math.pi
                 else -half_pi)
        # The cabinet's width runs along wall-local Y. Pointing into the
        # room, the origin end meets the wall; pointing at the wall, the
        # far end does and the origin stands out in the room.
        width_dir = 1.0 if theta > 0 else -1.0
        origin_x = span_start if theta > 0 else span_end
        origin_y = flush_y if width_dir == room_dir else flush_y + room_dir * total
        origin = wall_obj.matrix_world @ Vector((origin_x, origin_y, 0.0))
        self.stand_free(context, Vector((origin.x, origin.y, z)),
                        wall_rot_z + theta)
        self.update_dimensions(context)

    def set_position_facing(self, context, target):
        """An island facing ``target`` across the aisle, centred on it."""
        self.release_wall_state(context)
        cage = hb_types.GeoNodeCage(target)
        target_w = cage.get_input('Dim X')
        target_d = cage.get_input('Dim Y')
        m3 = target.matrix_world.to_3x3()
        front_dir = m3 @ Vector((0.0, -1.0, 0.0))
        width_dir = m3 @ Vector((1.0, 0.0, 0.0))
        for axis in (front_dir, width_dir):
            axis.z = 0.0
            axis.normalize()
        front_center = target.matrix_world @ Vector((target_w / 2.0, -target_d, 0.0))

        total = self.individual_cabinet_width * self.cabinet_quantity
        depth = self.get_cabinet_depth(context)
        # Origin is the back-left corner. Turned to face the target its
        # own +X runs against width_dir, so stepping half a width along
        # width_dir centres it.
        location = (front_center + front_dir * (self.FACING_AISLE + depth)
                    + width_dir * (total / 2.0))
        location.z = (self.get_cabinet_z_location(context)
                      if self.keeps_natural_z()
                      else target.matrix_world.translation.z)
        self.stand_free(context, location,
                        math.atan2(-front_dir.x, front_dir.y))
        self.facing_aisle = (front_center,
                             front_center + front_dir * self.FACING_AISLE)
        self.update_dimensions(context)

    def build_facing_arrow(self):
        """World-space segments for the arrow out of the cage's front,
        drawn by the shared placement-dim handler. Read from the cage's
        pending matrix: matrix_world lags a cage moved this same tick."""
        if not self.preview_cage or not self.preview_cage.obj:
            return None
        width = self.individual_cabinet_width * self.cabinet_quantity
        depth = self.preview_cage.get_input('Dim Y')
        height = self.preview_cage.get_input('Dim Z')
        if width <= 0 or depth <= 0:
            return None
        m = hb_placement.pending_world_matrix(self.preview_cage.obj)
        base = m @ Vector((width / 2.0, -depth / 2.0, height / 2.0))
        direction = m.to_3x3() @ Vector((0.0, -1.0, 0.0))
        direction.z = 0.0
        if direction.length < 1e-6:
            return None
        direction.normalize()
        # By depth, not width: the tip lands just past the front face
        # however wide a gap-filling run gets.
        length = min(max(depth * 0.75, units.inch(6.0)), units.inch(18.0))
        tip = base + direction * length
        perp = Vector((-direction.y, direction.x, 0.0))
        back = tip - direction * (length * 0.28)
        head = length * 0.16
        return [(base, tip), (tip, back + perp * head), (tip, back - perp * head)]

    def set_position_free(self):
        """Position cabinet(s) on the floor, snapping to nearby cabinets."""
        if not self.preview_cage or not self.hit_location:
            return
        
        # Reset snap state
        self.snap_cabinet = None
        self.snap_side = None
        self.center_snap_state = None  # No center snapping on floor
        
        # Detect a cabinet under the cursor (excluding ourselves)
        snap_target, snap_side = self.detect_cabinet_snap_target(
            self.hit_object, self.hit_location)
        if snap_target is not None and snap_target != self.preview_cage.obj:
            self.snap_cabinet = snap_target
            self.snap_side = snap_side
        
        if self.snap_cabinet:
            self.position_snapped_to_cabinet()
        else:
            # Free placement on floor (snapped to grid)
            self.preview_cage.obj.parent = None
            self.preview_cage.obj.location = hb_snap.snap_vector_to_grid(Vector(self.hit_location))
            # Set Z location based on cabinet/appliance type
            if self.keeps_natural_z():
                self.preview_cage.obj.location.z = self.get_cabinet_z_location(bpy.context)
            else:
                self.preview_cage.obj.location.z = 0
            self.preview_cage.obj.rotation_euler = (0, 0, self.free_rotation_z)
        
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

        total_width = self.individual_cabinet_width * self.cabinet_quantity
        result = self.compute_cabinet_snap_transform(
            self.snap_cabinet, self.snap_side, total_width)
        if result is None:
            return
        new_loc, new_rot = result

        self.preview_cage.obj.parent = None
        self.preview_cage.obj.location = new_loc
        self.preview_cage.obj.rotation_euler = new_rot

        # Z override: uppers / align-top-to-base / hoods all need their
        # natural Z, not the snap target's. Otherwise inherit Z from
        # the snap target so a row of cabinets stays at the same height.
        if self.keeps_natural_z():
            self.preview_cage.obj.location.z = self.get_cabinet_z_location(bpy.context)
        else:
            self.preview_cage.obj.location.z = self.snap_cabinet.location.z

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
        return appliance_class_for(self.appliance_type)

    def get_cabinet_class(self):
        return build_cabinet_for(
            self.cabinet_name, self.cabinet_type, self.is_appliance,
            self.appliance_type,
            self.blind_side_for_placement() if self.is_blind_corner() else 'Left')

    def create_final_cabinets(self, context):
        """Create the actual cabinet objects when user confirms placement."""
        cabinets = []
        cabinet_depth = self.get_cabinet_depth(context)

        if self.selected_wall and not self.free_standing:
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
                elif self.cabinet_name in PART_CLASS_MAP:
                    # Parts use their own default height/depth, only override width
                    cabinet.width = self.individual_cabinet_width
                    cabinet.create(self.cabinet_name)
                else:
                    cabinet.width = self.individual_cabinet_width
                    cabinet.height = self.get_cabinet_height(context)
                    cabinet.depth = cabinet_depth
                    cabinet.create(f'Cabinet')
                
                # Position based on which side of wall
                cabinet.obj.parent = self.selected_wall
                cabinet.obj.location.z = z_loc
                
                is_corner = 'Corner' in self.cabinet_name
                if is_corner and self.corner_right_side:
                    cabinet.obj.location.x = self.wall_length
                    cabinet.obj.location.y = 0
                    cabinet.obj.rotation_euler = (0, 0, math.radians(-90))
                elif is_corner:
                    cabinet.obj.location.x = current_x
                    cabinet.obj.location.y = 0
                    cabinet.obj.rotation_euler = (0, 0, 0)
                elif self.place_on_front:
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

            # The corner fillers the run reaches, styled and shown like
            # the cabinets beside them.
            self.placed_fillers = self.create_corner_fillers(context, wall_thickness)
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
                elif self.cabinet_name in PART_CLASS_MAP:
                    # Parts use their own default height/depth, only override width
                    cabinet.width = self.individual_cabinet_width
                    cabinet.create(self.cabinet_name)
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
                if self.keeps_natural_z():
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
        elif self.selected_wall and not getattr(self, 'free_standing', False):
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
            
            text = f"{side_str} | {gap_str} | {offset_str} | {qty_str} × {individual_str} = {total_str}{center_str} | ↑/↓ qty | ←/→ offset | R peninsula | Enter place | Esc cancel"
        else:
            # Floor placement
            unit_settings = context.scene.unit_settings
            total_width = self.individual_cabinet_width * self.cabinet_quantity
            total_str = units.unit_to_string(unit_settings, total_width)
            individual_str = units.unit_to_string(unit_settings, self.individual_cabinet_width)
            qty_str = f"{self.cabinet_quantity}"
            if getattr(self, 'facing_aisle', None) is not None:
                where = "Island facing"
            elif getattr(self, 'free_standing', False):
                where = "Peninsula"
            else:
                where = "Floor"
            if self.snap_cabinet:
                snap_str = f"Snap {self.snap_side}"
                text = f"{where} | {snap_str} | {qty_str} × {individual_str} = {total_str} | ↑/↓ qty | R rotate | Click place | Esc cancel"
            else:
                text = f"{where} | {qty_str} × {individual_str} = {total_str} | ↑/↓ qty | R rotate | Click place | Esc cancel"
        
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
        self.cursor_z_tracking = False
        self.cursor_z = 0
        self.cursor_z_product_height = 0
        self.align_top_to_base = False
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
        self.corner_right_side = False
        self.free_rotation_z = 0.0
        self.free_standing = False
        self.facing_aisle = None
        self._facing_arrow_segments = None

        # Products that follow cursor Z with inch snapping, fill gap with qty 1
        if self.cabinet_name in ('Floating Shelves', 'Valance'):
            self.cursor_z_tracking = True
            self.cabinet_type = 'UPPER'
            self.cursor_z = context.scene.hb_frameless.default_wall_cabinet_location
            self.fill_mode = True
            part_instance = PART_CLASS_MAP[self.cabinet_name]()
            self.cursor_z_product_height = part_instance.height

        # Base Assembly: one base along whatever of the wall is free of
        # other bases, appliances and doors; cabinets go over it.
        if self.is_base_assembly():
            self.fill_mode = True

        # Support Frame: top aligns with top of base cabinets, fill gap
        if self.cabinet_name == 'Support Frame':
            self.align_top_to_base = True
            self.fill_mode = True
            part_instance = PART_CLASS_MAP[self.cabinet_name]()
            self.cursor_z_product_height = part_instance.height

        self.create_preview_cage(context)
        # The width it comes in at, for when a free-standing placement
        # gives up a width it took from filling a wall gap.
        self.default_width = self.individual_cabinet_width
        self.add_placement_dim_handler(context)

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

        # R turns the cabinet a quarter turn. The turn takes effect in the
        # positioning below, so the preview and its arrow follow at once.
        if (event.type == 'R' and event.value == 'PRESS'
                and self.placement_state != hb_placement.PlacementState.TYPING):
            self.free_rotation_z = ((self.free_rotation_z + math.radians(90))
                                    % math.radians(360))

        # Let mixin handle typing events
        if self.handle_typing_event(event):
            self.update_header(context)
            return {'RUNNING_MODAL'}

        # Update snap (hide the preview during raycast and position calculation)
        self.preview_cage.obj.hide_set(True)

        self.update_snap(context, event)
        
        self.preview_cage.obj.hide_set(False)

        # Check if we're over a wall (or a child of a wall like a window)
        self.selected_wall = None
        if self.hit_object:
            # Walk up parent hierarchy to find wall
            current = self.hit_object
            while current:
                if 'IS_WALL_BP' in current:
                    # Only accept the wall if it still has its geo node modifier.
                    # Applied walls can't be used as a parametric placement
                    # target - reject them so downstream reads are safe.
                    candidate = hb_types.GeoNodeWall(current)
                    if candidate.has_modifier():
                        self.selected_wall = current
                        self.wall_length = candidate.get_input('Length')
                    break
                current = current.parent
        
        # Fallback: if raycast missed, find nearest wall based on cursor position
        if not self.selected_wall:
            self.selected_wall = self.find_nearest_wall_from_cursor(context)
            if self.selected_wall:
                wall = hb_types.GeoNodeWall(self.selected_wall)
                # find_nearest_wall_from_cursor already filters out applied walls,
                # but re-check defensively in case of edge cases.
                if wall.has_modifier():
                    self.wall_length = wall.get_input('Length')
                else:
                    self.selected_wall = None

        # Update position if not locked
        # Allow position updates while typing WIDTH (but not offsets)
        typing_allows_movement = (
            self.placement_state != hb_placement.PlacementState.TYPING or
            self.typing_target == hb_placement.TypingTarget.WIDTH or
            self.typing_target == hb_placement.TypingTarget.HEIGHT
        )
        
        if typing_allows_movement:
            self.free_standing = False
            self.facing_aisle = None
            target = self.facing_target()
            if target is not None:
                self.set_position_facing(context, target)
            elif (self.selected_wall and self.is_quarter_turned()
                  and 'Corner' not in self.cabinet_name):
                self.set_position_peninsula(context)
            elif self.selected_wall:
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
            self.placed_fillers = []
            cabinets = self.create_final_cabinets(context)
            for filler in self.placed_fillers:
                bpy.ops.hb_frameless.assign_cabinet_style(cabinet_name=filler.obj.name)
                hb_utils.run_calc_fix(context, filler.obj)
                bpy.ops.hb_frameless.toggle_mode(search_obj_name=filler.obj.name)
            for cabinet in cabinets:
                if cabinet.obj.get('IS_BASE_ASSEMBLY'):
                    # Placed by hand, so rebuilding the room's bases
                    # leaves it and whatever stands on it alone.
                    cabinet.obj[ops_base_assembly.EDITED_KEY] = True
                if not self.is_appliance:
                    # Cabinet-specific operations (skip for appliances)
                    # Assign the active cabinet style to the cabinet
                    bpy.ops.hb_frameless.assign_cabinet_style(cabinet_name=cabinet.obj.name)
                    # Force driver update for grandchild objects (workaround for Blender bug #133392)
                    hb_utils.run_calc_fix(context, cabinet.obj)
                    hb_utils.run_calc_fix(context, cabinet.obj)
                    # Assign door styles to all fronts (after drivers have calculated sizes)
                    self.assign_door_styles_to_cabinet(cabinet.obj)
                    # Calculate default shelf quantities based on opening heights
                    bpy.ops.hb_frameless.calculate_shelf_quantity(cabinet_name=cabinet.obj.name)
                else:
                    # Panels on this appliance dress to match frameless
                    # cabinetry in the active cabinet style.
                    cabinet.obj['HB_LIBRARY'] = 'FRAMELESS'
                    cabinet.obj['CABINET_STYLE_INDEX'] = \
                        context.scene.hb_frameless.active_cabinet_style_index
                    appliance_geo.seed_on_place(cabinet.obj)
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


# Object-marker tag each selection mode offers. 'Parts' offers no cage:
# every part renders at its default colour and is clicked directly.
SELECTION_MODE_TAGS = {
    'Cabinets': 'IS_FRAMELESS_CABINET_CAGE',
    'Bays': 'IS_FRAMELESS_BAY_CAGE',
    'Openings': 'IS_FRAMELESS_OPENING_CAGE',
    'Interiors': 'IS_FRAMELESS_INTERIOR_PART',
    'Parts': 'NO_TYPE',
}

# Markers that should be treated like cabinets for selection purposes
CABINET_LIKE_MARKERS = ['IS_FRAMELESS_CABINET_CAGE', 'IS_FRAMELESS_PRODUCT_CAGE', 'IS_APPLIANCE']


def selection_mode_matches(obj, mode):
    """True if ``obj`` is what the given selection mode offers."""
    if mode == 'Cabinets':
        return any(marker in obj for marker in CABINET_LIKE_MARKERS)
    return SELECTION_MODE_TAGS.get(mode, 'NO_TYPE') in obj


def _selection_mode_toggle_one(obj, mode):
    if 'IS_WALL_BP' in obj or 'IS_ENTRY_DOOR_BP' in obj or 'IS_WINDOW_BP' in obj or 'IS_CUTTING_OBJ' in obj:
        return
    type_name = SELECTION_MODE_TAGS.get(mode, 'NO_TYPE')
    if selection_mode_matches(obj, mode):
        # Material Preview / Rendered: a cage the mode offers stays
        # hidden unless it is selected (see quiet_cages).
        if quiet_cages.keep_hidden(obj, mode):
            toggle_cabinet_color(obj, False, type_name=type_name)
            return
        toggle_cabinet_color(obj, True, type_name=type_name)
    else:
        toggle_cabinet_color(obj, False, type_name=type_name)


def apply_frameless_selection_mode(context, root_obj=None):
    """Re-apply the current frameless selection mode: to ``root_obj``'s
    subtree when given, else every object in the scene. Leaves the
    selection to the caller."""
    mode = context.scene.hb_frameless.frameless_selection_mode
    if root_obj is not None:
        objs = [root_obj, *root_obj.children_recursive]
    else:
        objs = list(context.scene.objects)
    with hb_utils.children_index():
        for obj in objs:
            _selection_mode_toggle_one(obj, mode)
    quiet_cages.after_mode_applied()


class hb_frameless_OT_toggle_mode(bpy.types.Operator):
    """Toggle Cabinet Openings"""
    bl_idname = "hb_frameless.toggle_mode"
    bl_label = 'Toggle Mode'
    bl_description = "This will toggle the cabinet mode"

    search_obj_name: bpy.props.StringProperty(name="Search Object Name",default="")# type: ignore
    toggle_type: bpy.props.StringProperty(name="Toggle Type",default="")# type: ignore
    toggle_on: bpy.props.BoolProperty(name="Toggle On",default=False)# type: ignore

    def execute(self, context):
        apply_frameless_selection_mode(
            context, bpy.data.objects.get(self.search_obj_name))
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
            'Under Counter Appliance': 'UNDER_COUNTER',
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
            elif 'Tall' in self.cabinet_name or self.cabinet_name in ('Refrigerator Cabinet', 'Tall Leg'):
                cabinet_type = 'TALL'
            elif 'Upper' in self.cabinet_name:
                cabinet_type = 'UPPER'
            else:
                cabinet_type = 'BASE'
            print(f"cabinet_type: {cabinet_type}")
            print(f"cabinet_name: {self.cabinet_name}")
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
