import bpy
from mathutils import Vector
from enum import Enum, auto
from . import hb_snap, units


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
    OFFSET_X = auto()       # X offset from snap point
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
        
    def update_snap(self, context, event):
        """
        Update snap calculation based on current mouse position.
        Populates self.hit_location and self.hit_object.
        
        Call this early in your modal() before position logic.
        """
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
            TypingTarget.OFFSET_X: "Offset",
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
        Removes any objects registered with register_placement_object().
        """
        if self.placement_objects:
            for obj in self.placement_objects:
                if obj and obj.name in bpy.data.objects:
                    bpy.data.objects.remove(obj, do_unlink=True)
            self.placement_objects = []
            
        self.placement_state = PlacementState.IDLE
        context.window.cursor_set('DEFAULT')
        
    # -------------------------------------------------------------------------
    # Wall Children Utilities
    # -------------------------------------------------------------------------
    
    def get_wall_children_sorted(self, wall_obj) -> list:
        """
        Get all placed objects on a wall, sorted by X location.
        Useful for finding gaps and snap points.
        
        Returns list of (x_start, x_end, obj) tuples.
        """
        children = []
        for child in wall_obj.children:
            # Skip helper objects
            if child.get('obj_x'):
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
    
    def find_placement_gap(self, wall_obj, cursor_x: float, object_width: float) -> tuple:
        """
        Find the available gap at cursor position on a wall.
        
        Returns (gap_start, gap_end, snap_x) where snap_x is the suggested
        X position for placement.
        """
        from . import hb_types
        
        wall = hb_types.GeoNodeWall(wall_obj)
        wall_length = wall.get_input('Length')
        
        children = self.get_wall_children_sorted(wall_obj)
        
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
