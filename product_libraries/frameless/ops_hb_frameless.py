import bpy
from mathutils import Vector
from . import types_frameless
from ... import hb_utils, hb_snap, hb_placement, hb_types, units


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
        return hb_placement.TypingTarget.OFFSET_X
    
    def handle_typing_event(self, event) -> bool:
        if event.value == 'PRESS':
            if event.type == 'LEFT_ARROW':
                self.offset_from_right = False
                if self.placement_state == hb_placement.PlacementState.TYPING:
                    self.typing_target = hb_placement.TypingTarget.OFFSET_X
                else:
                    self.start_typing(hb_placement.TypingTarget.OFFSET_X)
                self.on_typed_value_changed()
                return True
            
            if event.type == 'RIGHT_ARROW':
                self.offset_from_right = True
                if self.placement_state == hb_placement.PlacementState.TYPING:
                    self.typing_target = hb_placement.TypingTarget.OFFSET_RIGHT
                else:
                    self.start_typing(hb_placement.TypingTarget.OFFSET_RIGHT)
                self.on_typed_value_changed()
                return True
            
            if event.type == 'W':
                if self.placement_state == hb_placement.PlacementState.TYPING:
                    self.typing_target = hb_placement.TypingTarget.WIDTH
                else:
                    self.start_typing(hb_placement.TypingTarget.WIDTH)
                self.on_typed_value_changed()
                return True
            
            if event.type == 'H':
                if self.placement_state == hb_placement.PlacementState.TYPING:
                    self.typing_target = hb_placement.TypingTarget.HEIGHT
                else:
                    self.start_typing(hb_placement.TypingTarget.HEIGHT)
                self.on_typed_value_changed()
                return True
        
        return super().handle_typing_event(event)
    
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

    def get_placed_object(self):
        return self.preview_cage.obj if self.preview_cage else None
    
    def get_placed_object_width(self) -> float:
        """Returns the TOTAL width of all cabinets."""
        return self.individual_cabinet_width * self.cabinet_quantity
    
    def set_placed_object_width(self, width: float):
        """Set width for a single cabinet."""
        self.individual_cabinet_width = width
        self.fill_mode = False
        self.auto_quantity = False
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
            self.individual_cabinet_width = parsed
            self.fill_mode = False
            self.auto_quantity = False
            self.update_preview_cage()
            self.update_preview_position()
                
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
        
        self.preview_cage.obj.parent = self.selected_wall
        self.preview_cage.obj.location.x = self.placement_x
        self.preview_cage.obj.location.y = 0
        self.preview_cage.obj.location.z = self.get_cabinet_z_location(bpy.context)
        self.preview_cage.obj.rotation_euler = (0, 0, 0)
    
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
        
        self.register_placement_object(self.preview_cage.obj)

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
        
        if not self.preview_cage or not self.selected_wall:
            return
        
        if self.typing_target == hb_placement.TypingTarget.OFFSET_X:
            # Live preview of left offset (temporarily set it)
            old_left = self.left_offset
            self.left_offset = parsed
            self.recalculate_from_offsets(bpy.context)
            self.left_offset = old_left  # Restore until Enter is pressed
            
        elif self.typing_target == hb_placement.TypingTarget.OFFSET_RIGHT:
            # Live preview of right offset (temporarily set it)
            old_right = self.right_offset
            self.right_offset = parsed
            self.recalculate_from_offsets(bpy.context)
            self.right_offset = old_right  # Restore until Enter is pressed
                
        elif self.typing_target == hb_placement.TypingTarget.WIDTH:
            self.individual_cabinet_width = parsed
            self.update_preview_cage()
            self.update_preview_position()
            
        elif self.typing_target == hb_placement.TypingTarget.HEIGHT:
            self.preview_cage.set_input('Dim Z', parsed)

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
            self.auto_quantity = False
            self.update_preview_cage()

    def set_position_on_wall(self, context):
        """Position preview cage on the selected wall."""
        if not self.selected_wall or not self.preview_cage:
            return
            
        wall = hb_types.GeoNodeWall(self.selected_wall)
        self.wall_length = wall.get_input('Length')
        
        # Get local X position on wall from world hit location
        world_loc = Vector(self.hit_location)
        local_loc = self.selected_wall.matrix_world.inverted() @ world_loc
        cursor_x = local_loc.x
        
        # Find available gap and store boundaries
        gap_start, gap_end, snap_x = self.find_placement_gap(
            self.selected_wall, 
            cursor_x, 
            self.individual_cabinet_width,
            exclude_obj=self.preview_cage.obj
        )
        
        # Store gap boundaries for offset calculations
        self.gap_left_boundary = gap_start
        self.gap_right_boundary = gap_end
        
        gap_width = gap_end - gap_start
        self.current_gap_width = gap_width
        
        # Auto-calculate quantity if in auto mode
        if self.auto_quantity and self.fill_mode:
            new_qty = self.calculate_auto_quantity(gap_width)
            if new_qty != self.cabinet_quantity:
                self.cabinet_quantity = new_qty
                self.array_modifier.count = self.cabinet_quantity
        
        # Calculate individual cabinet width
        if self.fill_mode and gap_width > 0:
            self.individual_cabinet_width = gap_width / self.cabinet_quantity
            snap_x = gap_start
        
        # Update preview cage
        self.preview_cage.set_input('Dim X', self.individual_cabinet_width)
        
        # Clamp snap_x to wall bounds
        total_width = self.individual_cabinet_width * self.cabinet_quantity
        snap_x = max(0, min(snap_x, self.wall_length - total_width))
        
        self.placement_x = snap_x
        
        # Position preview
        self.preview_cage.obj.parent = self.selected_wall
        self.preview_cage.obj.location.x = snap_x
        self.preview_cage.obj.location.y = 0
        self.preview_cage.obj.location.z = self.get_cabinet_z_location(context)
        self.preview_cage.obj.rotation_euler = (0, 0, 0)

    def set_position_free(self):
        """Position preview freely when not over a wall."""
        if self.preview_cage and self.hit_location:
            self.preview_cage.obj.parent = None
            self.preview_cage.obj.location = Vector(self.hit_location)
            self.preview_cage.obj.location.z = self.get_cabinet_z_location(bpy.context)

    def create_final_cabinets(self, context):
        """Create the actual cabinet objects when user confirms placement."""
        cabinets = []
        current_x = self.placement_x
        z_loc = self.get_cabinet_z_location(context)
        
        for i in range(self.cabinet_quantity):
            cabinet = types_frameless.Cabinet()
            cabinet.width = self.individual_cabinet_width
            cabinet.height = self.get_cabinet_height(context)
            cabinet.depth = self.get_cabinet_depth(context)
            cabinet.create(f'Cabinet')
            
            # Add doors
            doors = types_frameless.Doors()
            cabinet.add_cage_to_bay(doors)
            
            # Position
            cabinet.obj.parent = self.selected_wall
            cabinet.obj.location.x = current_x
            cabinet.obj.location.y = 0
            cabinet.obj.location.z = z_loc
            cabinet.obj.rotation_euler = (0, 0, 0)
            
            # Apply toggle mode for display
            bpy.ops.hb_frameless.toggle_mode(search_obj_name=cabinet.obj.name)
            
            cabinets.append(cabinet)
            current_x += self.individual_cabinet_width
        
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
            text = f"{target_name}: {self.typed_value}_ | Enter confirm | ↑/↓ qty | ←/→ offset | W width | F fill | Esc cancel"
        elif self.selected_wall:
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
            
            width_str = units.unit_to_string(unit_settings, self.individual_cabinet_width)
            fill_str = "Fill: ON" if self.fill_mode else "Fill: OFF"
            qty_str = f"Qty: {self.cabinet_quantity}"
            gap_str = f"Gap: {units.unit_to_string(unit_settings, self.gap_right_boundary - self.gap_left_boundary)}"
            text = f"{gap_str} | {offset_str} | {qty_str} × {width_str} | {fill_str} | ↑/↓ qty | ←/→ offset | W width | Esc cancel"
        else:
            text = f"Place {self.cabinet_type.title()} Cabinet | Move over a wall | Esc to cancel"
        
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

        self.create_preview_cage(context)

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        context.window.cursor_set('CROSSHAIR')

        if event.type == "INBETWEEN_MOUSEMOVE":
            return {'RUNNING_MODAL'}

        # Up/Down arrows to change quantity
        if event.type == 'UP_ARROW' and event.value == 'PRESS':
            self.update_cabinet_quantity(context, self.cabinet_quantity + 1)
            self.position_locked = False
            return {'RUNNING_MODAL'}
        
        if event.type == 'DOWN_ARROW' and event.value == 'PRESS':
            self.update_cabinet_quantity(context, self.cabinet_quantity - 1)
            self.position_locked = False
            return {'RUNNING_MODAL'}

        # Toggle fill mode with F
        if event.type == 'F' and event.value == 'PRESS':
            self.fill_mode = not self.fill_mode
            self.auto_quantity = self.fill_mode
            self.position_locked = False
            self.update_header(context)
            return {'RUNNING_MODAL'}

        # Let mixin handle typing events
        if self.handle_typing_event(event):
            self.update_header(context)
            return {'RUNNING_MODAL'}

        # Update snap (hide preview during raycast)
        self.preview_cage.obj.hide_set(True)
        self.update_snap(context, event)
        self.preview_cage.obj.hide_set(False)

        # Check if we're over a wall
        self.selected_wall = None
        if self.hit_object and 'IS_WALL_BP' in self.hit_object:
            self.selected_wall = self.hit_object
            wall = hb_types.GeoNodeWall(self.selected_wall)
            self.wall_length = wall.get_input('Length')

        # Update position if not typing and not locked
        if self.placement_state != hb_placement.PlacementState.TYPING:
            if self.selected_wall:
                if not self.position_locked:
                    self.set_position_on_wall(context)
            else:
                self.set_position_free()
                self.position_locked = False

        self.update_header(context)

        # Left click - create actual cabinets and place them
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if self.selected_wall:
                # Create the real cabinets
                self.create_final_cabinets(context)
                
                # Remove preview cage
                if self.preview_cage and self.preview_cage.obj:
                    bpy.data.objects.remove(self.preview_cage.obj, do_unlink=True)
                self.placement_objects = []
                
                hb_placement.clear_header_text(context)
                context.window.cursor_set('DEFAULT')
                return {'FINISHED'}
            else:
                self.report({'WARNING'}, "Cabinet must be placed on a wall")
                return {'RUNNING_MODAL'}

        # Right click or Escape - cancel
        if event.type in {'RIGHTMOUSE', 'ESC'} and event.value == 'PRESS':
            self.cancel_placement(context)
            hb_placement.clear_header_text(context)
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

    def has_child_item_type(self,obj,item_type):
        for child in obj.children_recursive:
            if item_type in child:
                return True
        return False

    def toggle_cabinet_color(self,obj,toggle,type_name="",dont_show_parent=True):
        hb_props = bpy.context.window_manager.home_builder
        add_on_prefs = hb_props.get_user_preferences(bpy.context)         

        if toggle:
            if dont_show_parent:
                if self.has_child_item_type(obj,type_name):
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

    def toggle_obj(self,obj):
        if 'IS_WALL_BP' in obj or 'IS_ENTRY_DOOR_BP' in obj or 'IS_WINDOW_BP' in obj:
            return        
        if self.toggle_type in obj:
            self.toggle_cabinet_color(obj,True,type_name=self.toggle_type)
        else:
            self.toggle_cabinet_color(obj,False,type_name=self.toggle_type)

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


class hb_frameless_OT_update_cabinet_sizes(bpy.types.Operator):
    bl_idname = "hb_frameless.update_cabinet_sizes"
    bl_label = "Update Cabinet Sizes"

    def execute(self, context):
        props = context.scene.hb_frameless
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
        bpy.ops.hb_frameless.place_cabinet('INVOKE_DEFAULT', cabinet_type=cabinet_type)
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
    bl_idname = "hb_frameless.update_door_and_drawer_front_style"
    bl_label = "Update Door and Drawer Front Style"

    selected_index: bpy.props.IntProperty(name="Selected Index",default=-1)# type: ignore

    def execute(self, context):
        door_fronts = []
        drawer_fronts = []
        frameless_props = context.scene.hb_frameless

        selected_door_style = frameless_props.door_styles[self.selected_index]

        for obj in context.scene.objects:
            if 'IS_DOOR_FRONT' in obj:
                door_fronts.append(obj)
            if 'IS_DRAWER_FRONT' in obj:
                drawer_fronts.append(obj)

        for door_front_obj in door_fronts:
            door_front = types_frameless.CabinetDoor(door_front_obj)
            door_style = door_front.add_part_modifier('CPM_5PIECEDOOR','Door Style')
            door_style.set_input("Left Stile Width",selected_door_style.stile_width)
            door_style.set_input("Right Stile Width",selected_door_style.stile_width)
            door_style.set_input("Top Rail Width",selected_door_style.rail_width)
            door_style.set_input("Bottom Rail Width",selected_door_style.rail_width)
            door_style.set_input("Panel Thickness",selected_door_style.panel_thickness)
            door_style.set_input("Panel Inset",selected_door_style.panel_inset)

        return {'FINISHED'}


class hb_frameless_OT_add_door_style(bpy.types.Operator):
    bl_idname = "hb_frameless.add_door_style"
    bl_label = "Add Door Style"

    def execute(self, context):
        frameless_props = context.scene.hb_frameless
        door_style = frameless_props.door_styles.add()
        door_style.name = "New Door Style"
        return {'FINISHED'}


classes = (
    hb_frameless_OT_place_cabinet,
    hb_frameless_OT_toggle_mode,
    hb_frameless_OT_update_cabinet_sizes,
    hb_frameless_OT_draw_cabinet,
    hb_frameless_OT_update_toe_kick_prompts,
    hb_frameless_OT_update_base_top_construction_prompts,
    hb_frameless_OT_update_drawer_front_height_prompts,
    hb_frameless_OT_update_door_and_drawer_front_style,
    hb_frameless_OT_add_door_style,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
