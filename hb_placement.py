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
        from mathutils import Vector
        
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
    import gpu
    from gpu_extras.batch import batch_for_shader
    import math
    
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
