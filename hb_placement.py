import bpy
import blf
import gpu
import math
from collections import namedtuple
from mathutils import Vector, Matrix
from enum import Enum, auto
from bpy_extras import view3d_utils
from gpu_extras.batch import batch_for_shader
from . import hb_snap, units


# Placement-dimension spec consumed by draw_placement_dimensions.
# `start` / `end` are world-space Vectors; `text` is the formatted label.
# `color` is an optional RGBA tuple - defaults to None, in which case the
# drawer uses its own default white. Use it to highlight snap-state etc.
PlacementDimSpec = namedtuple(
    'PlacementDimSpec',
    ['start', 'end', 'text', 'color'],
    defaults=[None],
)

class PlacementState(Enum):
    """States for placement modal operators"""
    IDLE = auto()
    PLACING = auto()        # Following mouse, not yet committed
    TYPING = auto()         # User is entering a numeric value
    ADJUSTING = auto()      # Placed but adjusting (size, rotation, etc.)


class TypingTarget(Enum):
    """What value the user is typing"""
    NONE = auto()
    LENGTH = auto()         # Wall length, cabinet width
    OFFSET_X = auto()       # X offset from left side
    OFFSET_RIGHT = auto()   # X offset from right side
    OFFSET_Y = auto()       # Y offset (depth)
    WIDTH = auto()          # Object width
    HEIGHT = auto()         # Object height
    DEPTH = auto()          # Object depth


# Keys that trigger number input
NUMBER_KEYS = {
    'ZERO': '0', 'ONE': '1', 'TWO': '2', 'THREE': '3', 'FOUR': '4',
    'FIVE': '5', 'SIX': '6', 'SEVEN': '7', 'EIGHT': '8', 'NINE': '9',
    'NUMPAD_0': '0', 'NUMPAD_1': '1', 'NUMPAD_2': '2', 'NUMPAD_3': '3',
    'NUMPAD_4': '4', 'NUMPAD_5': '5', 'NUMPAD_6': '6', 'NUMPAD_7': '7',
    'NUMPAD_8': '8', 'NUMPAD_9': '9',
    'PERIOD': '.', 'NUMPAD_PERIOD': '.',
    'MINUS': '-', 'NUMPAD_MINUS': '-',
    'SLASH': '/', 'NUMPAD_SLASH': '/',  # For fractions like 3/4
}


# Custom-property markers identifying objects that placement code
# should treat as cabinets/appliances - for snap-target lookups,
# adjacent-wall intrusion, etc. Centralized here so both libraries
# (and any future ones) check the same set.
CABINET_MARKERS = frozenset({
    'IS_FRAMELESS_CABINET_CAGE',
    'IS_FACE_FRAME_CABINET_CAGE',
    'IS_APPLIANCE',
})


class PlacementMixin:
    """
    Mixin class providing common placement functionality for modal operators.
    
    Add this to your operator class and call the appropriate methods.
    
    Usage:
        class MyPlacementOperator(bpy.types.Operator, PlacementMixin):
            def invoke(self, context, event):
                self.init_placement(context)
                # ... your setup
                
            def modal(self, context, event):
                self.update_snap(context, event)
                
                if self.handle_typing_event(event):
                    return {'RUNNING_MODAL'}
                # ... rest of your modal
    """
    
    # State tracking
    placement_state: PlacementState = PlacementState.IDLE
    typing_target: TypingTarget = TypingTarget.NONE
    typed_value: str = ""
    
    # Snap results (populated by update_snap)
    region = None
    mouse_pos: Vector = None
    hit_location: Vector = None
    hit_object = None
    
    # Objects being placed (for cleanup on cancel)
    placement_objects: list = None
    
    def init_placement(self, context):
        """Initialize placement state. Call this in invoke() or execute()."""
        self.placement_state = PlacementState.PLACING
        self.typing_target = TypingTarget.NONE
        self.typed_value = ""
        self.region = hb_snap.get_region(context)
        self.mouse_pos = Vector((0, 0))
        self.hit_location = None
        self.hit_object = None
        self.placement_objects = []
        
    def register_placement_object(self, obj):
        """Register an object for cleanup on cancel."""
        if self.placement_objects is None:
            self.placement_objects = []
        self.placement_objects.append(obj)

    def add_placement_dim_handler(self, context):
        """Register a POST_PIXEL handler that draws placement dimensions.

        After this is called, write a list of PlacementDimSpec values to
        self._placement_dim_specs and call context.area.tag_redraw() to
        flush. Idempotent - safe to call once in invoke().
        """
        if getattr(self, '_placement_dim_handle', None):
            return
        self._placement_dim_specs = []
        self._placement_dim_handle = bpy.types.SpaceView3D.draw_handler_add(
            draw_placement_dimensions, (self, context),
            'WINDOW', 'POST_PIXEL',
        )

    def remove_placement_dim_handler(self):
        """Tear down the placement-dim handler. Idempotent."""
        handle = getattr(self, '_placement_dim_handle', None)
        if handle is not None:
            try:
                bpy.types.SpaceView3D.draw_handler_remove(handle, 'WINDOW')
            except Exception:
                pass
        self._placement_dim_handle = None
        self._placement_dim_specs = []

    def update_snap(self, context, event):
        """
        Update snap calculation based on current mouse position.
        Populates self.hit_location and self.hit_object.
        
        Call this early in your modal() before position logic.
        """
        # Update region to match the viewport the mouse is currently over
        region = hb_snap.get_region(context, event.mouse_x, event.mouse_y)
        if region is not None:
            self.region = region
        self.mouse_pos = Vector((
            event.mouse_x - self.region.x,
            event.mouse_y - self.region.y
        ))
        hb_snap.main(self, event.ctrl, context)
    
    # -------------------------------------------------------------------------
    # Typed Input Handling
    # -------------------------------------------------------------------------
    
    def start_typing(self, target: TypingTarget, initial_value: str = ""):
        """Begin typed input mode for a specific value."""
        self.placement_state = PlacementState.TYPING
        self.typing_target = target
        self.typed_value = initial_value
        
    def stop_typing(self):
        """Exit typing mode without applying."""
        self.placement_state = PlacementState.PLACING
        self.typing_target = TypingTarget.NONE
        self.typed_value = ""
        
    def handle_typing_event(self, event) -> bool:
        """
        Handle keyboard events for numeric input.
        
        Returns True if the event was consumed (don't process further).
        Returns False if the event should be handled elsewhere.
        
        Auto-starts typing mode if a number key is pressed while not typing.
        """
        # Start typing if user presses a number key while in PLACING state
        if self.placement_state == PlacementState.PLACING:
            if event.type in NUMBER_KEYS and event.value == 'PRESS':
                # Auto-start typing - subclass should set appropriate target
                if self.typing_target == TypingTarget.NONE:
                    self.typing_target = self.get_default_typing_target()
                self.placement_state = PlacementState.TYPING
                self.typed_value = NUMBER_KEYS[event.type]
                self.on_typed_value_changed()
                return True
                
        # Handle typing mode
        if self.placement_state == PlacementState.TYPING:
            if event.value != 'PRESS':
                return False
                
            # Number/symbol input
            if event.type in NUMBER_KEYS:
                self.typed_value += NUMBER_KEYS[event.type]
                self.on_typed_value_changed()
                return True
                
            # Backspace
            if event.type == 'BACK_SPACE':
                if self.typed_value:
                    self.typed_value = self.typed_value[:-1]
                    self.on_typed_value_changed()
                else:
                    # Empty value, exit typing mode
                    self.stop_typing()
                return True
                
            # Enter/Return - apply the value
            if event.type in {'RET', 'NUMPAD_ENTER'}:
                self.apply_typed_value()
                return True
                
            # Escape - cancel typing
            if event.type == 'ESC':
                self.stop_typing()
                return True
                
            # Tab - cycle to next typing target (optional)
            if event.type == 'TAB':
                next_target = self.get_next_typing_target()
                if next_target != TypingTarget.NONE:
                    self.apply_typed_value()
                    self.start_typing(next_target)
                return True
                
        return False
    
    def get_default_typing_target(self) -> TypingTarget:
        """
        Override this to specify what value typing should target by default.
        For walls: LENGTH
        For placed objects: OFFSET_X
        """
        return TypingTarget.LENGTH
    
    def get_next_typing_target(self) -> TypingTarget:
        """
        Override this to enable Tab cycling between input fields.
        Return NONE to disable cycling.
        """
        return TypingTarget.NONE
    
    def on_typed_value_changed(self):
        """
        Override this to update visual feedback when typed value changes.
        For example, update a dimension display or header text.
        """
        pass
    
    def apply_typed_value(self):
        """
        Override this to apply the typed value to your geometry.
        Called when user presses Enter.
        
        Use self.parse_typed_distance() to convert the string to meters.
        """
        self.stop_typing()
    
    def parse_typed_distance(self, value_str: str = None) -> float:
        """
        Parse a typed string as a distance value, returning meters.
        
        Supports:
        - Plain numbers (interpreted based on scene units)
        - Feet and inches: 5'6" or 5' 6" or 5'6
        - Fractions: 5/8 or 5 3/4
        - Explicit units: 24" or 24in or 600mm or 0.6m
        
        Returns None if parsing fails.
        """
        if value_str is None:
            value_str = self.typed_value
            
        value_str = value_str.strip()
        if not value_str:
            return None
            
        try:
            # Check for feet/inches notation: 5'6" or 5' 6"
            if "'" in value_str:
                return self._parse_feet_inches(value_str)
            
            # Check for explicit units
            if value_str.endswith('"') or value_str.lower().endswith('in'):
                num = self._extract_number(value_str.rstrip('"').rstrip('in').rstrip('IN'))
                return units.inch(num) if num is not None else None
                
            if value_str.lower().endswith('mm'):
                num = self._extract_number(value_str[:-2])
                return units.millimeter(num) if num is not None else None
                
            if value_str.lower().endswith('cm'):
                num = self._extract_number(value_str[:-2])
                return units.centimeter(num) if num is not None else None
                
            if value_str.lower().endswith('m'):
                num = self._extract_number(value_str[:-1])
                return num  # Already in meters
                
            if value_str.endswith("'") or value_str.lower().endswith('ft'):
                num = self._extract_number(value_str.rstrip("'").rstrip('ft').rstrip('FT'))
                return units.feet(num) if num is not None else None
            
            # Plain number - interpret based on scene units
            num = self._extract_number(value_str)
            if num is not None:
                return self._number_to_scene_units(num)
                
        except (ValueError, ZeroDivisionError):
            pass
            
        return None
    
    def _parse_feet_inches(self, value_str: str) -> float:
        """Parse feet/inches notation like 5'6" or 5' 6 1/2" """
        parts = value_str.replace('"', '').split("'")
        feet_val = self._extract_number(parts[0].strip()) or 0
        
        inches_val = 0
        if len(parts) > 1 and parts[1].strip():
            inches_val = self._extract_number(parts[1].strip()) or 0
            
        return units.feet(feet_val) + units.inch(inches_val)
    
    def _extract_number(self, s: str) -> float:
        """
        Extract a number from string, handling fractions like "3/4" or "5 3/4"
        """
        s = s.strip()
        if not s:
            return None
            
        # Check for fraction with whole number: "5 3/4"
        if ' ' in s and '/' in s:
            parts = s.split(' ')
            whole = float(parts[0])
            frac_parts = parts[1].split('/')
            frac = float(frac_parts[0]) / float(frac_parts[1])
            return whole + frac
            
        # Check for simple fraction: "3/4"
        if '/' in s:
            parts = s.split('/')
            return float(parts[0]) / float(parts[1])
            
        # Plain number
        return float(s)
    
    def _number_to_scene_units(self, num: float) -> float:
        """Convert a plain number to meters based on scene unit settings."""
        unit_settings = bpy.context.scene.unit_settings
        
        if unit_settings.system == 'IMPERIAL':
            # Assume inches for imperial
            return units.inch(num)
        elif unit_settings.system == 'METRIC':
            if unit_settings.length_unit == 'MILLIMETERS':
                return units.millimeter(num)
            elif unit_settings.length_unit == 'CENTIMETERS':
                return units.centimeter(num)
            else:
                return num  # Meters
        else:
            return num  # None/generic - assume meters
    
    def get_typed_display_string(self) -> str:
        """Get a formatted string showing what the user is typing."""
        if not self.typed_value:
            return ""
        
        target_name = {
            TypingTarget.LENGTH: "Length",
            TypingTarget.OFFSET_X: "Offset (←)",
            TypingTarget.OFFSET_RIGHT: "Offset (→)",
            TypingTarget.WIDTH: "Width",
            TypingTarget.HEIGHT: "Height",
            TypingTarget.DEPTH: "Depth",
        }.get(self.typing_target, "Value")
        
        return f"{target_name}: {self.typed_value}"
    
    # -------------------------------------------------------------------------
    # Cancel / Cleanup
    # -------------------------------------------------------------------------
    
    def cancel_placement(self, context):
        """
        Clean up and cancel the placement operation.
        Removes any objects registered with register_placement_object() and their children.
        """
        if self.placement_objects:
            for obj in self.placement_objects:
                try:
                    # Check if object reference is still valid
                    if obj and obj.name in bpy.data.objects:
                        # Delete children first (recursively)
                        self._delete_object_and_children(obj)
                except ReferenceError:
                    # Object was already deleted (e.g., as a child of another object)
                    pass
            self.placement_objects = []
            
        self.placement_state = PlacementState.IDLE
        context.window.cursor_set('DEFAULT')
    
    def _delete_object_and_children(self, obj):
        """Recursively delete an object and all its children."""
        try:
            if not obj or obj.name not in bpy.data.objects:
                return
            
            # Collect all children first (can't iterate while modifying)
            children = list(obj.children)
            
            # Delete children recursively
            for child in children:
                self._delete_object_and_children(child)
            
            # Now delete the object itself
            if obj.name in bpy.data.objects:
                bpy.data.objects.remove(obj, do_unlink=True)
        except ReferenceError:
            # Object was already deleted
            pass
        
    # -------------------------------------------------------------------------
    # Wall Children Utilities
    # -------------------------------------------------------------------------
    
    def get_wall_children_sorted(self, wall_obj, exclude_obj=None) -> list:
        """
        Get all placed objects on a wall, sorted by X location.
        Useful for finding gaps and snap points.
        
        Args:
            wall_obj: The wall object to search
            exclude_obj: Optional object to exclude (e.g., the object being placed)
        
        Returns list of (x_start, x_end, obj) tuples.
        """
        children = []
        for child in wall_obj.children:
            # Skip helper objects
            if child.get('obj_x'):
                continue
            # Skip the object being placed
            if exclude_obj and child == exclude_obj:
                continue
            # Get object bounds on wall
            x_start = child.location.x
            # Try to get width from geometry node input
            x_end = x_start
            if hasattr(child, 'home_builder') and child.home_builder.mod_name:
                try:
                    from . import hb_types
                    geo_obj = hb_types.GeoNodeObject(child)
                    width = geo_obj.get_input('Dim X')
                    x_end = x_start + width
                except:
                    pass
            children.append((x_start, x_end, child))
            
        return sorted(children, key=lambda x: x[0])
    
    def find_placement_gap(self, wall_obj, cursor_x: float, object_width: float, exclude_obj=None) -> tuple:
        """
        Find the available gap at cursor position on a wall.
        
        Args:
            wall_obj: The wall object
            cursor_x: Cursor X position in wall's local space
            object_width: Width of the object being placed
            exclude_obj: Optional object to exclude from collision checks
        
        Returns (gap_start, gap_end, snap_x) where snap_x is the suggested
        X position for placement.
        """
        from . import hb_types
        
        wall = hb_types.GeoNodeWall(wall_obj)
        wall_length = wall.get_input('Length')
        
        children = self.get_wall_children_sorted(wall_obj, exclude_obj)
        
        if not children:
            # Empty wall - full length available
            return (0, wall_length, cursor_x)
        
        # Find which gap the cursor is in
        gap_start = 0
        gap_end = wall_length
        
        for x_start, x_end, obj in children:
            if cursor_x < x_start:
                # Cursor is before this object
                gap_end = x_start
                break
            else:
                # Cursor is after this object's start
                gap_start = x_end
                
        # Check if cursor is past all objects
        if children and cursor_x >= children[-1][1]:
            gap_start = children[-1][1]
            gap_end = wall_length
            
        # Determine snap position within gap
        gap_width = gap_end - gap_start
        
        if object_width >= gap_width:
            # Object fills or exceeds gap - snap to start
            snap_x = gap_start
        elif cursor_x - gap_start < object_width / 2:
            # Near left edge - snap to left
            snap_x = gap_start
        elif gap_end - cursor_x < object_width / 2:
            # Near right edge - snap right edge to gap end
            snap_x = gap_end - object_width
        else:
            # In middle - follow cursor
            snap_x = cursor_x - object_width / 2
            
        return (gap_start, gap_end, snap_x)

    def find_cabinet_bp(self, obj, marker_set=None):
        """Walk obj's parent chain looking for a cabinet/appliance root.

        Returns the first ancestor (including obj itself) whose custom
        properties include any marker in marker_set, or None if no
        match is found before hitting a wall root.

        marker_set defaults to CABINET_MARKERS, which covers both
        library types and appliances. Pass a narrower set to scope
        the search (e.g., only frameless cabinets).

        Walls terminate the walk - this is for cabinet-to-cabinet
        snap from off-wall placement, where wall-parented cabinets
        are NOT valid snap targets.
        """
        if obj is None:
            return None
        markers = marker_set if marker_set is not None else CABINET_MARKERS
        current = obj
        while current is not None:
            if 'IS_WALL_BP' in current:
                return None
            for m in markers:
                if m in current:
                    return current
            current = current.parent
        return None

    def detect_cabinet_snap_target(self, hit_obj, hit_location):
        """Resolve `hit_obj` to a cabinet root and pick which side
        (LEFT or RIGHT in the cabinet's local frame) the hit is on.

        Walks via find_cabinet_bp so wall-parented cabinets don't
        come back as targets when the hit is on a deep child part.
        Side is decided by hit_location's X relative to the cabinet's
        local center, so a hit on the cabinet's left half snaps the
        new object to the LEFT (against this cabinet's left face),
        and a hit on the right half snaps RIGHT.

        Returns (snap_obj, snap_side) or (None, None) if no cabinet
        root is found or its Dim X can't be read.
        """
        from . import hb_types
        snap_obj = self.find_cabinet_bp(hit_obj)
        if snap_obj is None or hit_location is None:
            return (None, None)
        try:
            snap_geo = hb_types.GeoNodeObject(snap_obj)
            snap_width = snap_geo.get_input('Dim X')
        except Exception:
            return (None, None)
        local_hit = snap_obj.matrix_world.inverted() @ hit_location
        snap_side = 'LEFT' if local_hit.x < snap_width / 2 else 'RIGHT'
        return (snap_obj, snap_side)

    def compute_cabinet_snap_transform(self, snap_obj, snap_side,
                                      new_object_width):
        """World-space (location, rotation_euler) for an object placed
        flush against the LEFT or RIGHT face of `snap_obj`, sharing
        its Z rotation.

        Math is in the snap target's local frame: LEFT means the new
        object's right edge meets snap_obj's left edge (offset is
        -new_object_width along snap-local X). RIGHT means the new
        object's left edge meets snap_obj's right edge (offset is
        +snap_width along snap-local X). The offset is then rotated
        into world space by snap_obj's Z rotation.

        Z is the snap target's Z. Callers that need a different Z
        (e.g. uppers pinned to a fixed height) override on the
        returned location.

        Returns (Vector, Euler) or None if Dim X unreadable.
        """
        from . import hb_types
        try:
            snap_geo = hb_types.GeoNodeObject(snap_obj)
            snap_width = snap_geo.get_input('Dim X')
        except Exception:
            return None

        if snap_side == 'LEFT':
            local_offset = Vector((-new_object_width, 0, 0))
        else:
            local_offset = Vector((snap_width, 0, 0))

        rot_z = snap_obj.rotation_euler.z
        world_offset = Matrix.Rotation(rot_z, 4, 'Z') @ local_offset
        new_loc = snap_obj.location + world_offset
        new_rot = snap_obj.rotation_euler.copy()
        return (new_loc, new_rot)

    def get_adjacent_wall_intrusion(self, wall_obj, side,
                                    object_z_start=None,
                                    object_height=None,
                                    object_depth=None,
                                    place_on_front=True):
        """How far cabinets on a connected wall intrude into this wall.

        Walks the connected wall's children matching CABINET_MARKERS,
        maps each cabinet's footprint into this wall's local frame via
        its matrix_world (so any rotation - including -90 corner
        placements - is handled correctly without enumerating cases),
        and returns the largest X distance any intruding corner sits
        inside this wall's bounds at the requested end.

        Vertical and depth filtering are opt-in via the kwargs; pass
        None on either pair to skip that filter (then every cabinet
        on the connected wall counts as a potential intrusion).

        side is 'left' (the x=0 end) or 'right' (x=wall_length).
        Returns 0.0 if no connected wall or no intruding cabinet.
        """
        from . import hb_types

        wall = hb_types.GeoNodeWall(wall_obj)
        adj_wall_node = wall.get_connected_wall(direction=side)
        if not adj_wall_node:
            return 0.0
        adj_wall_obj = adj_wall_node.obj

        wall_length = wall.get_input('Length')
        wall_thickness = wall.get_input('Thickness')
        wall_matrix_inv = wall_obj.matrix_world.inverted()

        check_vertical = (object_z_start is not None and
                          object_height is not None)
        if check_vertical:
            object_z_end = object_z_start + object_height

        check_depth = object_depth is not None
        if check_depth:
            if place_on_front:
                our_y_min = -object_depth
                our_y_max = 0.0
            else:
                our_y_min = wall_thickness
                our_y_max = wall_thickness + object_depth

        max_intrusion = 0.0

        for child in adj_wall_obj.children:
            if child.get('obj_x') or child.get('IS_2D_ANNOTATION'):
                continue
            if not any(m in child for m in CABINET_MARKERS):
                continue

            try:
                child_geo = hb_types.GeoNodeObject(child)
                child_width = child_geo.get_input('Dim X')
                child_depth_val = child_geo.get_input('Dim Y')
                child_height = child_geo.get_input('Dim Z')
            except Exception:
                continue

            if check_vertical:
                child_z_start = child.location.z
                child_z_end = child_z_start + child_height
                if not (object_z_start < child_z_end and
                        child_z_start < object_z_end):
                    continue

            # Cabinet's footprint corners in cabinet-local space.
            # HB cabinets place origin at back-left and extend +X
            # (Dim X) along width, -Y (Dim Y) along depth into the
            # room. Using matrix_world for the world map handles ANY
            # rotation correctly, including -90 right-corner placements.
            local_corners = [
                Vector((0, 0, 0)),
                Vector((child_width, 0, 0)),
                Vector((0, -child_depth_val, 0)),
                Vector((child_width, -child_depth_val, 0)),
            ]
            corners_our = [
                wall_matrix_inv @ (child.matrix_world @ c)
                for c in local_corners
            ]

            if check_depth:
                adj_y_min = min(c.y for c in corners_our)
                adj_y_max = max(c.y for c in corners_our)
                if not (our_y_min < adj_y_max and adj_y_min < our_y_max):
                    continue

            if side == 'left':
                # Intrusion = how far past x=0 any corner sits
                for c in corners_our:
                    if c.x > 0:
                        max_intrusion = max(max_intrusion, c.x)
            else:
                # Intrusion = how far back from x=wall_length any
                # corner sits (positive = inside the wall span)
                for c in corners_our:
                    if c.x < wall_length:
                        max_intrusion = max(max_intrusion,
                                            wall_length - c.x)

        return max(0.0, max_intrusion)

    def find_placement_gap_by_side(self, wall_obj, cursor_x: float,
                                   object_width: float,
                                   place_on_front: bool,
                                   wall_thickness: float,
                                   object_z_start: float = None,
                                   object_height: float = None,
                                   object_depth: float = None,
                                   exclude_obj=None) -> tuple:
        """Side-aware version of find_placement_gap.

        Filters wall children to those on the same wall side as the
        object being placed. Doors and windows count as obstacles on
        BOTH sides (they cut through). Snap lines act as zero-width
        boundary obstacles. Adjacent-wall intrusion (delegated to
        get_adjacent_wall_intrusion) becomes virtual obstacles at
        the wall ends.

        Vertical filtering is opt-in: pass object_z_start AND
        object_height to skip children that don't overlap the
        object's Z range (e.g., a base cabinet doesn't block an
        upper above it). If either is None, vertical filtering
        is disabled and every same-side child is an obstacle.

        Returns (gap_start, gap_end, snap_x). On a non-parametric
        wall (no modifier), returns (None, None, None).
        """
        from . import hb_types

        wall = hb_types.GeoNodeWall(wall_obj)
        if not wall.has_modifier():
            return None, None, None
        wall_length = wall.get_input('Length')

        check_vertical = (
            object_z_start is not None and object_height is not None
        )
        if check_vertical:
            object_z_end = object_z_start + object_height

        children = []
        for child in wall_obj.children:
            if child.get('obj_x'):
                continue
            if exclude_obj is not None and child == exclude_obj:
                continue
            if child.get('IS_2D_ANNOTATION'):
                continue
            if child.get('IS_SNAP_LINE'):
                continue  # handled separately as zero-width boundaries

            # Doors/windows cut through both sides - always an obstacle.
            is_opening = ('IS_ENTRY_DOOR_BP' in child or
                          'IS_WINDOW_BP' in child)
            if not is_opening:
                child_on_front = child.location.y < wall_thickness / 2
                if child_on_front != place_on_front:
                    continue

            child_z_start = child.location.z
            child_z_end = child_z_start
            child_width = 0
            if hasattr(child, 'home_builder') and child.home_builder.mod_name:
                try:
                    geo_obj = hb_types.GeoNodeObject(child)
                    child_width = geo_obj.get_input('Dim X')
                    child_height_val = geo_obj.get_input('Dim Z')
                    child_z_end = child_z_start + child_height_val
                except Exception:
                    pass

            if check_vertical:
                # Two ranges overlap iff start1 < end2 AND start2 < end1.
                overlaps = (object_z_start < child_z_end and
                            child_z_start < object_z_end)
                if not overlaps:
                    continue

            # Resolve horizontal extent based on rotation. Back-side
            # cabinets are rotated 180 around Z so location.x is the
            # right edge; -90 corner cabinets have origin at right
            # and extend by Dim Y along the wall.
            rot_z = child.rotation_euler.z
            is_rot_180 = (abs(rot_z - math.pi) < 0.1 or
                          abs(rot_z + math.pi) < 0.1)
            is_rot_neg90 = (abs(rot_z - math.radians(-90)) < 0.1 or
                            abs(rot_z - math.radians(270)) < 0.1)

            if is_rot_neg90:
                try:
                    child_depth = hb_types.GeoNodeObject(child).get_input('Dim Y')
                except Exception:
                    child_depth = child_width
                x_start = child.location.x - child_depth
                x_end = child.location.x
            elif is_rot_180:
                x_start = child.location.x - child_width
                x_end = child.location.x
            else:
                x_start = child.location.x
                x_end = x_start + child_width

            children.append((x_start, x_end, child))

        children.sort(key=lambda x: x[0])

        # Adjacent-wall intrusion as virtual obstacles at the ends.
        # Pass our own filter params through so the intrusion check
        # uses the same vertical / depth / side criteria as the
        # primary same-wall scan above.
        left_intrusion = self.get_adjacent_wall_intrusion(
            wall_obj, 'left',
            object_z_start=object_z_start,
            object_height=object_height,
            object_depth=object_depth,
            place_on_front=place_on_front,
        )
        if left_intrusion > 0:
            children.append((0.0, left_intrusion, None))
        right_intrusion = self.get_adjacent_wall_intrusion(
            wall_obj, 'right',
            object_z_start=object_z_start,
            object_height=object_height,
            object_depth=object_depth,
            place_on_front=place_on_front,
        )
        if right_intrusion > 0:
            children.append((wall_length - right_intrusion, wall_length, None))
        if left_intrusion > 0 or right_intrusion > 0:
            children.sort(key=lambda x: x[0])

        # Snap lines as zero-width boundaries.
        for child in wall_obj.children:
            if child.get('IS_SNAP_LINE'):
                snap_x_pos = child.get('SNAP_X_POSITION', child.location.x)
                children.append((snap_x_pos, snap_x_pos, child))
        children.sort(key=lambda x: x[0])

        if not children:
            return (0, wall_length, cursor_x)

        gap_start = 0
        gap_end = wall_length
        for x_start, x_end, _ in children:
            if cursor_x < x_start:
                gap_end = x_start
                break
            else:
                gap_start = x_end
        if cursor_x >= children[-1][1]:
            gap_start = children[-1][1]
            gap_end = wall_length

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


def draw_header_text(context, text: str):
    """
    Draw text in the header area during modal operation.
    Call this in a draw handler.
    """
    # This is a simple approach - for more complex UI, use gpu/blf directly
    context.area.header_text_set(text)


def clear_header_text(context):
    """Clear any header text set by draw_header_text."""
    context.area.header_text_set(None)

# =============================================================================
# DIMENSION OPERATOR MIXIN
# =============================================================================

class DimensionOperatorMixin:
    """
    Base mixin for dimension operators providing unified UX across all contexts.
    
    Subclasses must implement:
        - get_snap_point(context, coord) -> (Vector, screen_pos, is_snapped)
        - get_plane_point(context, coord) -> Vector
        - create_dimension(context) -> object
    
    Subclasses may override:
        - get_snap_sources(context) -> list of objects to snap to
    """
    
    # State machine: FIRST -> SECOND -> OFFSET
    DIM_STATE_FIRST = 'FIRST'
    DIM_STATE_SECOND = 'SECOND'
    DIM_STATE_OFFSET = 'OFFSET'
    
    # Snap radius in pixels
    SNAP_RADIUS = 20
    
    def init_dimension_state(self):
        """Initialize dimension operator state. Call in invoke()."""
        self.dim_state = self.DIM_STATE_FIRST
        self.first_point = None
        self.second_point = None
        self.offset_point = None
        
        # Snap state
        self.current_point = None
        self.snap_screen_pos = None
        self.is_snapped = False
        
        # Ortho mode
        self.ortho_mode = False
        self.ortho_direction = 'AUTO'  # 'AUTO', 'HORIZONTAL', 'VERTICAL'
        
        # Draw handler reference
        self._dim_draw_handle = None
    
    def add_dimension_draw_handler(self, context):
        """Add the visual feedback draw handler."""
        args = (self, context)
        self._dim_draw_handle = bpy.types.SpaceView3D.draw_handler_add(
            draw_dimension_snap_indicator, args, 'WINDOW', 'POST_PIXEL')
    
    def remove_dimension_draw_handler(self):
        """Remove the draw handler."""
        if self._dim_draw_handle:
            bpy.types.SpaceView3D.draw_handler_remove(self._dim_draw_handle, 'WINDOW')
            self._dim_draw_handle = None
    
    def get_ortho_display(self) -> str:
        """Get display text for ortho mode state."""
        if not self.ortho_mode:
            return ""
        if self.ortho_direction == 'HORIZONTAL':
            return " [ORTHO: H]"
        elif self.ortho_direction == 'VERTICAL':
            return " [ORTHO: V]"
        return " [ORTHO]"
    
    def get_dimension_header_text(self) -> str:
        """Get header text based on current state."""
        snap_text = " [SNAP]" if self.is_snapped else ""
        ortho_text = self.get_ortho_display()
        
        if self.dim_state == self.DIM_STATE_FIRST:
            return f"Click first point{snap_text} | O: ortho | Right-click/Esc: cancel"
        elif self.dim_state == self.DIM_STATE_SECOND:
            return f"Click second point{snap_text}{ortho_text} | O: toggle ortho | Right-click/Esc: cancel"
        else:  # OFFSET
            return "Move to set offset, click to place | Right-click/Esc: cancel"
    
    def update_dimension_header(self, context):
        """Update the header with current state."""
        draw_header_text(context, self.get_dimension_header_text())
    
    def apply_ortho_constraint(self, point: 'Vector') -> 'Vector':
        """Apply ortho constraint to a point relative to first_point."""
        
        if not self.ortho_mode or not self.first_point:
            return point
        
        dx = point.x - self.first_point.x
        dy = point.y - self.first_point.y
        dz = point.z - self.first_point.z if hasattr(point, 'z') and len(point) > 2 else 0
        
        # Auto-detect direction if needed
        if self.ortho_direction == 'AUTO':
            # For 2D (detail views), compare X vs Y
            # For 3D, we'd need more complex logic based on view plane
            if abs(dx) >= abs(dy):
                self.ortho_direction = 'HORIZONTAL'
            else:
                self.ortho_direction = 'VERTICAL'
        
        # Apply constraint
        if self.ortho_direction == 'HORIZONTAL':
            return Vector((point.x, self.first_point.y, self.first_point.z if len(point) > 2 else 0))
        else:  # VERTICAL
            return Vector((self.first_point.x, point.y, self.first_point.z if len(point) > 2 else 0))
    
    def cycle_ortho_mode(self):
        """Cycle through ortho modes: OFF -> AUTO -> H -> V -> OFF"""
        if not self.ortho_mode:
            self.ortho_mode = True
            self.ortho_direction = 'AUTO'
        elif self.ortho_direction == 'AUTO':
            self.ortho_direction = 'HORIZONTAL'
        elif self.ortho_direction == 'HORIZONTAL':
            self.ortho_direction = 'VERTICAL'
        else:
            self.ortho_mode = False
            self.ortho_direction = 'AUTO'
    
    def handle_dimension_event(self, context, event) -> str:
        """
        Handle common dimension events.
        
        Returns:
            'RUNNING_MODAL' - continue
            'FINISHED' - dimension complete
            'CANCELLED' - operation cancelled
            'PASS_THROUGH' - pass event to Blender
            None - event not handled, let subclass handle it
        """
        # Update visual feedback on mouse move
        if event.type == 'MOUSEMOVE':
            coord = (event.mouse_region_x, event.mouse_region_y)
            
            if self.dim_state == self.DIM_STATE_OFFSET:
                # For offset, just get plane point (no snapping)
                self.current_point = self.get_plane_point(context, coord)
                self.snap_screen_pos = coord
                self.is_snapped = False
            else:
                # For first/second point, use snapping
                self.current_point, self.snap_screen_pos, self.is_snapped = self.get_snap_point(context, coord)
                
                # Apply ortho constraint for second point
                if self.dim_state == self.DIM_STATE_SECOND and self.current_point and self.ortho_mode:
                    self.current_point = self.apply_ortho_constraint(self.current_point)
            
            # Update live preview
            if self.dim_state in (self.DIM_STATE_SECOND, self.DIM_STATE_OFFSET) and self.current_point:
                self.update_dimension_preview(context)
            
            self.update_dimension_header(context)
            return 'RUNNING_MODAL'
        
        # Left click - advance state
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if self.current_point is None:
                return 'RUNNING_MODAL'
            
            if self.dim_state == self.DIM_STATE_FIRST:
                self.first_point = self.current_point.copy()
                # Create preview dimension after first point
                self.create_preview_dimension(context)
                self.dim_state = self.DIM_STATE_SECOND
                self.update_dimension_header(context)
                return 'RUNNING_MODAL'
            
            elif self.dim_state == self.DIM_STATE_SECOND:
                # Apply ortho constraint when confirming
                if self.ortho_mode:
                    self.second_point = self.apply_ortho_constraint(self.current_point)
                else:
                    self.second_point = self.current_point.copy()
                self.dim_state = self.DIM_STATE_OFFSET
                self.update_dimension_header(context)
                return 'RUNNING_MODAL'
            
            else:  # OFFSET state
                self.offset_point = self.current_point.copy()
                # Finalize the dimension
                self.finalize_dimension(context)
                self.remove_dimension_draw_handler()
                clear_header_text(context)
                return 'FINISHED'
        
        # O key - toggle ortho mode
        if event.type == 'O' and event.value == 'PRESS':
            self.cycle_ortho_mode()
            self.update_dimension_header(context)
            return 'RUNNING_MODAL'
        
        # Cancel
        if event.type in {'RIGHTMOUSE', 'ESC'} and event.value == 'PRESS':
            self.cancel_dimension(context)
            self.remove_dimension_draw_handler()
            clear_header_text(context)
            return 'CANCELLED'
        
        # Navigation pass-through
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return 'PASS_THROUGH'
        if event.type in {'NUMPAD_0', 'NUMPAD_1', 'NUMPAD_2', 'NUMPAD_3', 
                          'NUMPAD_4', 'NUMPAD_5', 'NUMPAD_6', 'NUMPAD_7',
                          'NUMPAD_8', 'NUMPAD_9', 'NUMPAD_PERIOD'}:
            return 'PASS_THROUGH'
        
        return None  # Not handled
    
    # --- Methods subclasses must implement ---
    
    def get_snap_point(self, context, coord: tuple):
        """
        Get snapped point for the given screen coordinate.
        
        Args:
            context: Blender context
            coord: (x, y) screen coordinates
        
        Returns:
            (point: Vector, screen_pos: tuple, is_snapped: bool)
        
        Must be implemented by subclass.
        """
        raise NotImplementedError("Subclass must implement get_snap_point()")
    
    def get_plane_point(self, context, coord: tuple):
        """
        Get point on working plane for offset positioning.
        
        Args:
            context: Blender context
            coord: (x, y) screen coordinates
        
        Returns:
            Vector - point on the working plane
        
        Must be implemented by subclass.
        """
        raise NotImplementedError("Subclass must implement get_plane_point()")
    
    def create_preview_dimension(self, context):
        """
        Create the preview dimension object after first point is set.
        Called when transitioning from FIRST to SECOND state.
        
        Should create self.preview_dim or similar and position at first_point.
        
        Must be implemented by subclass.
        """
        raise NotImplementedError("Subclass must implement create_preview_dimension()")
    
    def update_dimension_preview(self, context):
        """
        Update the preview dimension as the mouse moves.
        Called on MOUSEMOVE when in SECOND or OFFSET state.
        
        Uses self.first_point, self.current_point (for SECOND state),
        or self.second_point and self.current_point (for OFFSET state).
        
        Must be implemented by subclass.
        """
        raise NotImplementedError("Subclass must implement update_dimension_preview()")
    
    def finalize_dimension(self, context):
        """
        Finalize the dimension after all three points are set.
        Called when confirming the dimension.
        
        Uses self.first_point, self.second_point, and self.offset_point.
        Typically sets decimal precision and any final properties.
        
        Must be implemented by subclass.
        """
        raise NotImplementedError("Subclass must implement finalize_dimension()")
    
    def cancel_dimension(self, context):
        """
        Clean up when the dimension is cancelled.
        Should delete any preview objects created.
        
        Must be implemented by subclass.
        """
        raise NotImplementedError("Subclass must implement cancel_dimension()")


def draw_dimension_snap_indicator(operator, context):
    """Draw visual feedback for dimension snapping."""
    
    if not hasattr(operator, 'snap_screen_pos') or operator.snap_screen_pos is None:
        return
    
    x, y = operator.snap_screen_pos
    
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    gpu.state.blend_set('ALPHA')
    gpu.state.line_width_set(2.0)
    
    if operator.is_snapped:
        color = (0.0, 1.0, 0.0, 1.0)  # Green for snapped
        radius = 10
    else:
        color = (1.0, 1.0, 0.0, 0.8)  # Yellow for unsnapped
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
    
    # Draw crosshair if snapped
    if operator.is_snapped:
        cross_size = 6
        cross_verts = [
            (x - cross_size, y), (x + cross_size, y),
            (x, y - cross_size), (x, y + cross_size),
        ]
        batch = batch_for_shader(shader, 'LINES', {"pos": cross_verts})
        batch.draw(shader)
    
    # Draw ortho indicator if active
    if hasattr(operator, 'ortho_mode') and operator.ortho_mode:
        # Draw small "O" indicator near cursor
        gpu.state.line_width_set(1.5)
        ortho_color = (0.3, 0.7, 1.0, 1.0)  # Light blue
        shader.uniform_float("color", ortho_color)
        
        # Small circle offset from main indicator
        ox, oy = x + 15, y + 15
        ortho_radius = 5
        ortho_verts = []
        for i in range(segments + 1):
            angle = 2 * math.pi * i / segments
            cx = ox + ortho_radius * math.cos(angle)
            cy = oy + ortho_radius * math.sin(angle)
            ortho_verts.append((cx, cy))
        batch = batch_for_shader(shader, 'LINE_STRIP', {"pos": ortho_verts})
        batch.draw(shader)
    
    gpu.state.blend_set('NONE')
    gpu.state.line_width_set(1.0)


# =============================================================================
# PLACEMENT DIMENSION DRAWER
# =============================================================================

def draw_placement_dimensions(operator, context):
    """Draw placement dimension lines + labels in screen space.

    Reads ``operator._placement_dim_specs`` - a list of PlacementDimSpec
    namedtuples. Each spec has world-space ``start`` / ``end`` Vectors
    and a pre-formatted ``text`` label. The drawer projects the endpoints
    into the region, renders a line with perpendicular end ticks, and
    blits the label via blf at the line's midpoint.

    Pure draw - no scene mutation, no depsgraph cost. Replaces per-tick
    GeoNodeDimension object writes for placement feedback. Subclasses
    rebuild the spec list each time the cabinet position changes and
    call context.area.tag_redraw().
    """
    specs = getattr(operator, '_placement_dim_specs', None)
    if not specs:
        return

    region = context.region
    rv3d = context.region_data
    if region is None or rv3d is None:
        return

    default_color = (1.0, 1.0, 1.0, 0.95)
    tick_pixels = 6  # half-length of the perpendicular end tick

    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    gpu.state.blend_set('ALPHA')
    gpu.state.line_width_set(1.5)

    font_id = 0
    blf.size(font_id, 14)

    for spec in specs:
        s_world = spec.start
        e_world = spec.end
        text = spec.text
        # Per-spec color override (e.g., snap state). Falls back to
        # the drawer's default white when the spec didn't set one.
        color = spec.color if spec.color is not None else default_color

        s_screen = view3d_utils.location_3d_to_region_2d(region, rv3d, s_world)
        e_screen = view3d_utils.location_3d_to_region_2d(region, rv3d, e_world)
        if s_screen is None or e_screen is None:
            continue

        # Main dim line
        shader.bind()
        shader.uniform_float("color", color)
        batch = batch_for_shader(
            shader, 'LINES',
            {"pos": [tuple(s_screen), tuple(e_screen)]},
        )
        batch.draw(shader)

        # Perpendicular end ticks (degenerate gracefully if the line
        # collapses to a point in screen space - e.g., camera looking
        # straight down the dim axis).
        dx = e_screen.x - s_screen.x
        dy = e_screen.y - s_screen.y
        length = math.hypot(dx, dy)
        if length > 0.5:
            inv = 1.0 / length
            # Perpendicular unit vector
            px = -dy * inv
            py = dx * inv
            tx = px * tick_pixels
            ty = py * tick_pixels
            tick_verts = [
                (s_screen.x - tx, s_screen.y - ty),
                (s_screen.x + tx, s_screen.y + ty),
                (e_screen.x - tx, e_screen.y - ty),
                (e_screen.x + tx, e_screen.y + ty),
            ]
            batch = batch_for_shader(
                shader, 'LINES', {"pos": tick_verts},
            )
            batch.draw(shader)

        # Label - centered on midpoint, offset perpendicular so the
        # text doesn't sit on top of the line.
        if text:
            mx = (s_screen.x + e_screen.x) * 0.5
            my = (s_screen.y + e_screen.y) * 0.5
            text_w, text_h = blf.dimensions(font_id, text)
            if length > 0.5:
                # Offset along the perpendicular by half-text + a few px
                offset = text_h * 0.5 + 4.0
                ox = px * offset
                oy = py * offset
                tx_pos = mx + ox - text_w * 0.5
                ty_pos = my + oy - text_h * 0.5
            else:
                tx_pos = mx - text_w * 0.5
                ty_pos = my + 6.0
            blf.position(font_id, tx_pos, ty_pos, 0)
            blf.color(font_id, *color)
            blf.draw(font_id, text)

    gpu.state.blend_set('NONE')
    gpu.state.line_width_set(1.0)
