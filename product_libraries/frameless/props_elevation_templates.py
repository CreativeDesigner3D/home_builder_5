import bpy
import math
import os
from bpy.types import PropertyGroup, Operator, Menu
from bpy.props import (
    BoolProperty,
    FloatProperty,
    IntProperty,
    PointerProperty,
    StringProperty,
    CollectionProperty,
    EnumProperty,
)
from mathutils import Vector
from . import types_frameless
from ..common import types_appliances
from ... import hb_utils, hb_types, hb_project, units
from ...units import inch

def update_template_preview(self, context):
    """Callback when any template property changes."""
    if hasattr(self, 'update_preview') and self.is_active:
        self.update_preview(context)


# =====================================================================
# BASE TEMPLATE CLASS
# =====================================================================

class HB_Frameless_Base_Template(PropertyGroup):
    """
    Base class for all elevation templates.
    Contains common properties shared across templates.
    """
    
    # Common room properties
    ceiling_height: FloatProperty(
        name="Ceiling Height",
        default=inch(96),
        unit='LENGTH',
        precision=4,
        update=update_template_preview
    )  # type: ignore

    wall_width: FloatProperty(
        name="Wall Width",
        default=inch(120),
        unit='LENGTH',
        precision=4,
        update=update_template_preview
    )  # type: ignore
    
    # Common offset properties
    left_offset: FloatProperty(
        name="Left Offset",
        default=0,
        unit='LENGTH',
        precision=4,
        update=update_template_preview
    )  # type: ignore
    
    right_offset: FloatProperty(
        name="Right Offset",
        default=0,
        unit='LENGTH',
        precision=4,
        update=update_template_preview
    )  # type: ignore

    # Wall reference
    obj_wall: PointerProperty(
        name="Wall",
        type=bpy.types.Object
    )  # type: ignore
    
    # Track if preview is active
    is_active: BoolProperty(
        name="Is Active",
        default=False
    )  # type: ignore

    def get_wall(self):
        """Get the wall as a GeoNodeWall object."""
        if self.obj_wall:
            return hb_types.GeoNodeWall(self.obj_wall)
        return None

    def set_wall(self, wall):
        """Set the wall from a GeoNodeWall object or bp."""
        if wall and hasattr(wall, 'obj'):
            self.obj_wall = wall.obj
        elif wall:
            self.obj_wall = wall

    def init_from_wall(self, wall_obj):
        """Initialize template properties from an existing wall."""
        self.obj_wall = wall_obj
        wall = hb_types.GeoNodeWall(wall_obj)
        self.wall_width = wall.get_input('Length')
        
        # Get ceiling height from project settings
        main_scene = hb_project.get_main_scene()
        if main_scene:
            hb_props = main_scene.home_builder
            self.ceiling_height = hb_props.ceiling_height

    def get_cabinet_props(self, context):
        """Get the frameless cabinet properties."""
        return context.scene.hb_frameless

    def get_cabinet_style(self, context):
        """Get the currently selected cabinet style."""
        props = self.get_cabinet_props(context)
        main_scene = hb_project.get_main_scene()
        main_props = main_scene.hb_frameless
        
        if main_props.cabinet_styles and props.active_cabinet_style_index < len(main_props.cabinet_styles):
            return main_props.cabinet_styles[props.active_cabinet_style_index]
        return None

    def get_door_style(self, context):
        """Get the currently selected door style."""
        props = self.get_cabinet_props(context)
        main_scene = hb_project.get_main_scene()
        main_props = main_scene.hb_frameless
        
        if main_props.door_styles and props.active_door_style_index < len(main_props.door_styles):
            return main_props.door_styles[props.active_door_style_index]
        return None

    def apply_styles_to_cabinet(self, context, cabinet_obj):
        """Apply current cabinet and door styles to a cabinet."""
        props = self.get_cabinet_props(context)
        
        # Store style indices on cabinet
        cabinet_obj['CABINET_STYLE_INDEX'] = props.active_cabinet_style_index
        cabinet_obj['DOOR_STYLE_INDEX'] = props.active_door_style_index
        
        # Apply cabinet style (materials)
        cabinet_style = self.get_cabinet_style(context)
        if cabinet_style:
            cabinet_style.assign_style_to_cabinet(cabinet_obj)
        
        # Apply door style to fronts
        door_style = self.get_door_style(context)
        if door_style:
            for child in cabinet_obj.children_recursive:
                if child.get('IS_DOOR_FRONT') or child.get('IS_DRAWER_FRONT'):
                    door_style.assign_style_to_front(child)

    def create_preview_cage(self, context, name, label, parent=None):
        """Create a preview cage (3D box) with rectangle labels for front and top views."""
        # Create the 3D cage
        cage = hb_types.GeoNodeCage()
        cage.create(name)
        cage.obj['IS_TEMPLATE_PREVIEW'] = True
        cage.obj['IS_FRAMELESS_CABINET_CAGE'] = True  # Display with correct visual properties
        cage.obj['PREVIEW_LABEL'] = label
        cage.set_input("Mirror Y", True)  # Cabinet base point is back left corner
        if parent:
            cage.obj.parent = parent
        
        # Create a rectangle label on the front face (for elevation view)
        rect_front = hb_types.GeoNodeRectangle()
        rect_front.create(name + "_Label_Front")
        rect_front.obj['IS_TEMPLATE_PREVIEW'] = True
        rect_front.obj['IS_2D_ANNOTATION'] = True  # Prevent selection mode from changing color
        rect_front.obj.parent = cage.obj
        rect_front.obj.color = (0, 0, 0, 1)  # Black
        rect_front.obj.rotation_euler.x = math.radians(90)  # Rotate to face forward
        rect_front.set_input("Text", label)
        rect_front.set_input("Text Size", inch(2))
        rect_front.set_input("Line Thickness", inch(0.1))
        
        # Create a rectangle label on the top face (for plan view)
        rect_top = hb_types.GeoNodeRectangle()
        rect_top.create(name + "_Label_Top")
        rect_top.obj['IS_TEMPLATE_PREVIEW'] = True
        rect_top.obj['IS_2D_ANNOTATION'] = True  # Prevent selection mode from changing color
        rect_top.obj.parent = cage.obj
        rect_top.obj.color = (0, 0, 0, 1)  # Black
        # No rotation needed - rectangle lies flat on top
        rect_top.set_input("Text", label)
        rect_top.set_input("Text Size", inch(2))
        rect_top.set_input("Line Thickness", inch(0.1))
        
        return cage.obj, rect_front.obj, rect_top.obj

    def update_preview_cage(self, cage_obj, rect_front_obj, rect_top_obj, x, y, z, width, depth, height, label=None, visible=True):
        """Update a preview cage's position, size, and labels."""
        if cage_obj is None:
            return
        cage_obj.hide_viewport = not visible
        if rect_front_obj:
            rect_front_obj.hide_viewport = not visible
        if rect_top_obj:
            rect_top_obj.hide_viewport = not visible
        
        if visible:
            cage_obj.location.x = x
            cage_obj.location.y = y
            cage_obj.location.z = z
            
            cage = hb_types.GeoNodeCage(cage_obj)
            cage.set_input("Dim X", width)
            cage.set_input("Dim Y", depth)
            cage.set_input("Dim Z", height)
            
            # Update front rectangle (elevation view)
            if rect_front_obj:
                rect_front = hb_types.GeoNodeRectangle(rect_front_obj)
                rect_front.set_input("Dim X", width)
                rect_front.set_input("Dim Y", height)  # Rectangle shows width x height (front view)
                # Position rectangle at front of cage (parented, so relative coords)
                rect_front_obj.location.x = 0
                rect_front_obj.location.y = -depth
                rect_front_obj.location.z = 0
                rect_front.set_input("Text Y Offset", 0)  # Center text in cage
                if label:
                    rect_front.set_input("Text", label)
            
            # Update top rectangle (plan view)
            if rect_top_obj:
                rect_top = hb_types.GeoNodeRectangle(rect_top_obj)
                rect_top.set_input("Dim X", width)
                rect_top.set_input("Dim Y", depth)  # Rectangle shows width x depth (plan view)
                # Position rectangle on top of cage
                rect_top_obj.location.x = 0
                rect_top_obj.location.y = -depth
                rect_top_obj.location.z = height
                rect_top.set_input("Text Y Offset", 0)  # Center text
                if label:
                    rect_top.set_input("Text", label)

    def delete_preview_objects(self, context):
        """Delete all preview objects."""
        if self.obj_wall:
            for child in list(self.obj_wall.children):
                if child.get('IS_TEMPLATE_PREVIEW'):
                    hb_utils.delete_obj_and_children(child)

    def create_preview(self, context):
        """Create preview objects. Override in subclass."""
        pass

    def update_preview(self, context):
        """Update preview objects when properties change. Override in subclass."""
        pass

    def draw_cabinets(self, context):
        """Draw the actual cabinets. Override in subclass."""
        pass
    
    def clear_preview(self, context):
        """Clear preview objects. Override in subclass."""
        self.delete_preview_objects(context)
        self.is_active = False

    def draw_ui(self, context, layout):
        """Draw the UI for this template. Override in subclass."""
        pass


# =====================================================================
# REFRIGERATOR RANGE TEMPLATE
# =====================================================================

class Refrigerator_Range_Template(HB_Frameless_Base_Template):
    """
    Template for a wall with refrigerator and range.
    Creates individual frameless cabinets.
    """

    refrigerator_location: EnumProperty(
        name="Refrigerator Location",
        items=[
            ('NONE', 'None', 'No refrigerator'),
            ('LEFT', 'Left', 'Refrigerator on left'),
            ('RIGHT', 'Right', 'Refrigerator on right')
        ],
        default='NONE',
        update=update_template_preview
    )  # type: ignore

    range_location: EnumProperty(
        name="Range Location",
        items=[
            ('NONE', 'None', 'No range'),
            ('CENTER', 'Center', 'Range in center')
        ],
        default='NONE',
        update=update_template_preview
    )  # type: ignore

    refrigerator_width: FloatProperty(
        name="Refrigerator Width",
        default=inch(36),
        unit='LENGTH',
        precision=4,
        update=update_template_preview
    )  # type: ignore

    range_width: FloatProperty(
        name="Range Width",
        default=inch(30),
        unit='LENGTH',
        precision=4,
        update=update_template_preview
    )  # type: ignore

    range_hood_type: EnumProperty(
        name="Range Hood Type",
        items=[
            ('EMPTY', 'Empty', 'Leave space above range empty for hood'),
            ('RAISE_UPPER', 'Raise Upper', 'Raise upper cabinet above range')
        ],
        default='EMPTY',
        update=update_template_preview
    )  # type: ignore

    range_hood_height: FloatProperty(
        name="Range Hood Height",
        default=inch(20),
        unit='LENGTH',
        precision=4,
        update=update_template_preview
    )  # type: ignore

    pantry_location: EnumProperty(
        name="Pantry Location",
        items=[
            ('NONE', 'None', 'No pantry'),
            ('LEFT', 'Left', 'Pantry on left'),
            ('RIGHT', 'Right', 'Pantry on right')
        ],
        default='NONE',
        update=update_template_preview
    )  # type: ignore

    pantry_width: FloatProperty(
        name="Pantry Width",
        default=inch(18),
        unit='LENGTH',
        precision=4,
        update=update_template_preview
    )  # type: ignore

    left_base_cabinet_qty: IntProperty(
        name="Left Base Cabinet Qty",
        default=2,
        min=1,
        max=6,
        update=update_template_preview
    )  # type: ignore

    right_base_cabinet_qty: IntProperty(
        name="Right Base Cabinet Qty",
        default=2,
        min=1,
        max=6,
        update=update_template_preview
    )  # type: ignore

    left_upper_cabinet_qty: IntProperty(
        name="Left Upper Cabinet Qty",
        default=2,
        min=1,
        max=6,
        update=update_template_preview
    )  # type: ignore

    right_upper_cabinet_qty: IntProperty(
        name="Right Upper Cabinet Qty",
        default=2,
        min=1,
        max=6,
        update=update_template_preview
    )  # type: ignore

    # Preview cage objects (3D boxes)
    cage_refrigerator: PointerProperty(name="Refrigerator Cage", type=bpy.types.Object)  # type: ignore
    cage_range: PointerProperty(name="Range Cage", type=bpy.types.Object)  # type: ignore
    cage_pantry: PointerProperty(name="Pantry Cage", type=bpy.types.Object)  # type: ignore
    cage_left_base: PointerProperty(name="Left Base Cage", type=bpy.types.Object)  # type: ignore
    cage_right_base: PointerProperty(name="Right Base Cage", type=bpy.types.Object)  # type: ignore
    cage_left_upper: PointerProperty(name="Left Upper Cage", type=bpy.types.Object)  # type: ignore
    cage_right_upper: PointerProperty(name="Right Upper Cage", type=bpy.types.Object)  # type: ignore
    
    # Preview rectangle labels (front - elevation view)
    rect_refrigerator: PointerProperty(name="Refrigerator Rect", type=bpy.types.Object)  # type: ignore
    rect_range: PointerProperty(name="Range Rect", type=bpy.types.Object)  # type: ignore
    rect_pantry: PointerProperty(name="Pantry Rect", type=bpy.types.Object)  # type: ignore
    rect_left_base: PointerProperty(name="Left Base Rect", type=bpy.types.Object)  # type: ignore
    rect_right_base: PointerProperty(name="Right Base Rect", type=bpy.types.Object)  # type: ignore
    rect_left_upper: PointerProperty(name="Left Upper Rect", type=bpy.types.Object)  # type: ignore
    rect_right_upper: PointerProperty(name="Right Upper Rect", type=bpy.types.Object)  # type: ignore
    
    # Preview rectangle labels (top - plan view)
    rect_top_refrigerator: PointerProperty(name="Refrigerator Rect Top", type=bpy.types.Object)  # type: ignore
    rect_top_range: PointerProperty(name="Range Rect Top", type=bpy.types.Object)  # type: ignore
    rect_top_pantry: PointerProperty(name="Pantry Rect Top", type=bpy.types.Object)  # type: ignore
    rect_top_left_base: PointerProperty(name="Left Base Rect Top", type=bpy.types.Object)  # type: ignore
    rect_top_right_base: PointerProperty(name="Right Base Rect Top", type=bpy.types.Object)  # type: ignore
    rect_top_left_upper: PointerProperty(name="Left Upper Rect Top", type=bpy.types.Object)  # type: ignore
    rect_top_right_upper: PointerProperty(name="Right Upper Rect Top", type=bpy.types.Object)  # type: ignore

    def create_preview(self, context):
        """Create all preview cages and rectangles for this template."""
        if not self.obj_wall:
            return
        
        # Create preview cages with rectangle labels (front and top)
        self.cage_refrigerator, self.rect_refrigerator, self.rect_top_refrigerator = self.create_preview_cage(
            context, "PREVIEW_REFRIGERATOR", "REFRIGERATOR", self.obj_wall)
        self.cage_range, self.rect_range, self.rect_top_range = self.create_preview_cage(
            context, "PREVIEW_RANGE", "RANGE", self.obj_wall)
        self.cage_pantry, self.rect_pantry, self.rect_top_pantry = self.create_preview_cage(
            context, "PREVIEW_PANTRY", "PANTRY", self.obj_wall)
        self.cage_left_base, self.rect_left_base, self.rect_top_left_base = self.create_preview_cage(
            context, "PREVIEW_LEFT_BASE", "BASE CABINETS", self.obj_wall)
        self.cage_right_base, self.rect_right_base, self.rect_top_right_base = self.create_preview_cage(
            context, "PREVIEW_RIGHT_BASE", "BASE CABINETS", self.obj_wall)
        self.cage_left_upper, self.rect_left_upper, self.rect_top_left_upper = self.create_preview_cage(
            context, "PREVIEW_LEFT_UPPER", "UPPER CABINETS", self.obj_wall)
        self.cage_right_upper, self.rect_right_upper, self.rect_top_right_upper = self.create_preview_cage(
            context, "PREVIEW_RIGHT_UPPER", "UPPER CABINETS", self.obj_wall)
        
        self.is_active = True
        self.update_preview(context)
        
        # Toggle selection mode to display cabinet cages correctly
        props = self.get_cabinet_props(context)
        props.frameless_selection_mode = "Cabinets"
        
        # Update preview again to properly hide cages that should be hidden
        self.update_preview(context)

    def update_preview(self, context):
        """Update all preview cages based on current property values."""
        if not self.obj_wall or not self.is_active:
            return
        
        props = self.get_cabinet_props(context)
        
        # Get dimensions from props
        base_height = props.base_cabinet_height
        base_depth = props.base_cabinet_depth
        tall_depth = props.tall_cabinet_depth
        upper_depth = props.upper_cabinet_depth
        upper_z = props.default_wall_cabinet_location
        top_clearance = props.default_top_cabinet_clearance
        tall_height = self.ceiling_height - top_clearance
        upper_height = self.ceiling_height - top_clearance - upper_z
        
        # Track offsets
        left_offset = self.left_offset
        right_offset = self.right_offset
        upper_left_offset = self.left_offset
        upper_right_offset = self.right_offset
        
        # Handle pantry
        if self.pantry_location == 'LEFT':
            self.update_preview_cage(self.cage_pantry, self.rect_pantry, self.rect_top_pantry,
                                     left_offset, 0, 0,
                                     self.pantry_width, tall_depth, tall_height,
                                     "PANTRY (1)", True)
            left_offset += self.pantry_width
            upper_left_offset += self.pantry_width
        elif self.pantry_location == 'RIGHT':
            self.update_preview_cage(self.cage_pantry, self.rect_pantry, self.rect_top_pantry,
                                     self.wall_width - self.pantry_width - right_offset, 0, 0,
                                     self.pantry_width, tall_depth, tall_height,
                                     "PANTRY (1)", True)
            right_offset += self.pantry_width
            upper_right_offset += self.pantry_width
        else:
            self.update_preview_cage(self.cage_pantry, self.rect_pantry, self.rect_top_pantry, 0, 0, 0, 0, 0, 0, visible=False)
        
        # Handle refrigerator
        if self.refrigerator_location == 'LEFT':
            self.update_preview_cage(self.cage_refrigerator, self.rect_refrigerator, self.rect_top_refrigerator,
                                     left_offset, 0, 0,
                                     self.refrigerator_width, tall_depth, tall_height,
                                     "REFRIGERATOR (1)", True)
            left_offset += self.refrigerator_width
            upper_left_offset += self.refrigerator_width
        elif self.refrigerator_location == 'RIGHT':
            self.update_preview_cage(self.cage_refrigerator, self.rect_refrigerator, self.rect_top_refrigerator,
                                     self.wall_width - self.refrigerator_width - right_offset, 0, 0,
                                     self.refrigerator_width, tall_depth, tall_height,
                                     "REFRIGERATOR (1)", True)
            right_offset += self.refrigerator_width
            upper_right_offset += self.refrigerator_width
        else:
            self.update_preview_cage(self.cage_refrigerator, self.rect_refrigerator, self.rect_top_refrigerator, 0, 0, 0, 0, 0, 0, visible=False)
        
        # Handle base cabinets and range
        available_base_width = self.wall_width - left_offset - right_offset
        
        if self.range_location == 'CENTER':
            base_width_each = (available_base_width - self.range_width) / 2
            
            # Left base cabinets
            left_label = f"BASE ({self.left_base_cabinet_qty})"
            self.update_preview_cage(self.cage_left_base, self.rect_left_base, self.rect_top_left_base,
                                     left_offset, 0, 0,
                                     base_width_each, base_depth, base_height,
                                     left_label, True)
            
            # Range
            self.update_preview_cage(self.cage_range, self.rect_range, self.rect_top_range,
                                     left_offset + base_width_each, 0, 0,
                                     self.range_width, base_depth, base_height,
                                     "RANGE (1)", True)
            
            # Right base cabinets
            right_label = f"BASE ({self.right_base_cabinet_qty})"
            self.update_preview_cage(self.cage_right_base, self.rect_right_base, self.rect_top_right_base,
                                     left_offset + base_width_each + self.range_width, 0, 0,
                                     base_width_each, base_depth, base_height,
                                     right_label, True)
        else:
            # No range - single base cabinet area
            base_label = f"BASE ({self.left_base_cabinet_qty})"
            self.update_preview_cage(self.cage_left_base, self.rect_left_base, self.rect_top_left_base,
                                     left_offset, 0, 0,
                                     available_base_width, base_depth, base_height,
                                     base_label, True)
            self.update_preview_cage(self.cage_range, self.rect_range, self.rect_top_range, 0, 0, 0, 0, 0, 0, visible=False)
            self.update_preview_cage(self.cage_right_base, self.rect_right_base, self.rect_top_right_base, 0, 0, 0, 0, 0, 0, visible=False)
        
        # Handle upper cabinets
        available_upper_width = self.wall_width - upper_left_offset - upper_right_offset
        
        if self.range_location == 'CENTER':
            if self.range_hood_type == 'EMPTY':
                # Two separate upper cabinet areas
                upper_width_each = (available_upper_width - self.range_width) / 2
                
                left_upper_label = f"UPPER ({self.left_upper_cabinet_qty})"
                self.update_preview_cage(self.cage_left_upper, self.rect_left_upper, self.rect_top_left_upper,
                                         upper_left_offset, 0, upper_z,
                                         upper_width_each, upper_depth, upper_height,
                                         left_upper_label, True)
                
                right_upper_label = f"UPPER ({self.right_upper_cabinet_qty})"
                self.update_preview_cage(self.cage_right_upper, self.rect_right_upper, self.rect_top_right_upper,
                                         upper_left_offset + upper_width_each + self.range_width, 0, upper_z,
                                         upper_width_each, upper_depth, upper_height,
                                         right_upper_label, True)
            else:
                # Raised upper - one cabinet spans full width
                upper_label = f"UPPER ({self.left_upper_cabinet_qty})"
                self.update_preview_cage(self.cage_left_upper, self.rect_left_upper, self.rect_top_left_upper,
                                         upper_left_offset, 0, upper_z,
                                         available_upper_width, upper_depth, upper_height,
                                         upper_label, True)
                self.update_preview_cage(self.cage_right_upper, self.rect_right_upper, self.rect_top_right_upper, 0, 0, 0, 0, 0, 0, visible=False)
        else:
            # No range - single upper cabinet area
            upper_label = f"UPPER ({self.left_upper_cabinet_qty})"
            self.update_preview_cage(self.cage_left_upper, self.rect_left_upper, self.rect_top_left_upper,
                                     upper_left_offset, 0, upper_z,
                                     available_upper_width, upper_depth, upper_height,
                                     upper_label, True)
            self.update_preview_cage(self.cage_right_upper, self.rect_right_upper, self.rect_top_right_upper, 0, 0, 0, 0, 0, 0, visible=False)

    def draw_cabinets(self, context):
        """Draw the actual cabinets from the template."""
        if not self.obj_wall:
            return []
        
        created_cabinets = []
        props = self.get_cabinet_props(context)
        
        # Get dimensions
        base_depth = props.base_cabinet_depth
        tall_depth = props.tall_cabinet_depth
        upper_depth = props.upper_cabinet_depth
        base_height = props.base_cabinet_height
        upper_z = props.default_wall_cabinet_location
        top_clearance = props.default_top_cabinet_clearance
        tall_height = self.ceiling_height - top_clearance
        upper_height = self.ceiling_height - top_clearance - upper_z
        
        # Track offsets
        left_offset = self.left_offset
        right_offset = self.right_offset
        upper_left_offset = self.left_offset
        upper_right_offset = self.right_offset
        
        wall = hb_types.GeoNodeWall(self.obj_wall)
        
        # Create pantry
        if self.pantry_location == 'LEFT':
            pantry = types_frameless.TallCabinet()
            pantry.width = self.pantry_width
            pantry.depth = tall_depth
            pantry.height = tall_height
            pantry.create("Pantry")
            pantry.obj.parent = self.obj_wall
            pantry.obj.location.x = left_offset
            self.apply_styles_to_cabinet(context, pantry.obj)
            hb_utils.run_calc_fix(context, pantry.obj)
            created_cabinets.append(pantry.obj)
            left_offset += self.pantry_width
            upper_left_offset += self.pantry_width
            
        elif self.pantry_location == 'RIGHT':
            pantry = types_frameless.TallCabinet()
            pantry.width = self.pantry_width
            pantry.depth = tall_depth
            pantry.height = tall_height
            pantry.create("Pantry")
            pantry.obj.parent = self.obj_wall
            pantry.obj.location.x = self.wall_width - self.pantry_width - right_offset
            self.apply_styles_to_cabinet(context, pantry.obj)
            hb_utils.run_calc_fix(context, pantry.obj)
            created_cabinets.append(pantry.obj)
            right_offset += self.pantry_width
            upper_right_offset += self.pantry_width
        
        # Create refrigerator cabinet
        if self.refrigerator_location == 'LEFT':
            fridge = types_frameless.RefrigeratorCabinet()
            fridge.width = self.refrigerator_width
            fridge.depth = tall_depth
            fridge.height = tall_height
            fridge.create("Refrigerator Cabinet")
            fridge.obj.parent = self.obj_wall
            fridge.obj.location.x = left_offset
            self.apply_styles_to_cabinet(context, fridge.obj)
            hb_utils.run_calc_fix(context, fridge.obj)
            created_cabinets.append(fridge.obj)
            left_offset += self.refrigerator_width
            upper_left_offset += self.refrigerator_width
            
        elif self.refrigerator_location == 'RIGHT':
            fridge = types_frameless.RefrigeratorCabinet()
            fridge.width = self.refrigerator_width
            fridge.depth = tall_depth
            fridge.height = tall_height
            fridge.create("Refrigerator Cabinet")
            fridge.obj.parent = self.obj_wall
            fridge.obj.location.x = self.wall_width - self.refrigerator_width - right_offset
            self.apply_styles_to_cabinet(context, fridge.obj)
            hb_utils.run_calc_fix(context, fridge.obj)
            created_cabinets.append(fridge.obj)
            right_offset += self.refrigerator_width
            upper_right_offset += self.refrigerator_width
        
        # Calculate base cabinet areas
        available_base_width = self.wall_width - left_offset - right_offset
        
        if self.range_location == 'CENTER':
            base_width_each = (available_base_width - self.range_width) / 2
            left_cabinet_width = base_width_each / self.left_base_cabinet_qty
            right_cabinet_width = base_width_each / self.right_base_cabinet_qty
            
            # Create left base cabinets
            current_x = left_offset
            for i in range(self.left_base_cabinet_qty):
                cab = types_frameless.BaseCabinet()
                cab.width = left_cabinet_width
                cab.depth = base_depth
                cab.height = base_height
                cab.create(f"Base Cabinet L{i+1}")
                cab.obj.parent = self.obj_wall
                cab.obj.location.x = current_x
                self.apply_styles_to_cabinet(context, cab.obj)
                hb_utils.run_calc_fix(context, cab.obj)
                created_cabinets.append(cab.obj)
                current_x += left_cabinet_width
            
            # Create range (appliance)
            range_app = types_appliances.Range()
            range_app.width = self.range_width
            range_app.depth = base_depth
            range_app.height = base_height
            range_app.create("Range")
            range_app.obj.parent = self.obj_wall
            range_app.obj.location.x = left_offset + base_width_each
            created_cabinets.append(range_app.obj)
            
            # Create right base cabinets
            current_x = left_offset + base_width_each + self.range_width
            for i in range(self.right_base_cabinet_qty):
                cab = types_frameless.BaseCabinet()
                cab.width = right_cabinet_width
                cab.depth = base_depth
                cab.height = base_height
                cab.create(f"Base Cabinet R{i+1}")
                cab.obj.parent = self.obj_wall
                cab.obj.location.x = current_x
                self.apply_styles_to_cabinet(context, cab.obj)
                hb_utils.run_calc_fix(context, cab.obj)
                created_cabinets.append(cab.obj)
                current_x += right_cabinet_width
        else:
            # No range - create base cabinets across full width
            cabinet_width = available_base_width / self.left_base_cabinet_qty
            current_x = left_offset
            for i in range(self.left_base_cabinet_qty):
                cab = types_frameless.BaseCabinet()
                cab.width = cabinet_width
                cab.depth = base_depth
                cab.height = base_height
                cab.create(f"Base Cabinet {i+1}")
                cab.obj.parent = self.obj_wall
                cab.obj.location.x = current_x
                self.apply_styles_to_cabinet(context, cab.obj)
                hb_utils.run_calc_fix(context, cab.obj)
                created_cabinets.append(cab.obj)
                current_x += cabinet_width
        
        # Create upper cabinets
        available_upper_width = self.wall_width - upper_left_offset - upper_right_offset
        
        if self.range_location == 'CENTER' and self.range_hood_type == 'EMPTY':
            # Two separate upper cabinet areas
            upper_width_each = (available_upper_width - self.range_width) / 2
            left_upper_width = upper_width_each / self.left_upper_cabinet_qty
            right_upper_width = upper_width_each / self.right_upper_cabinet_qty
            
            # Left uppers
            current_x = upper_left_offset
            for i in range(self.left_upper_cabinet_qty):
                cab = types_frameless.UpperCabinet()
                cab.width = left_upper_width
                cab.depth = upper_depth
                cab.height = upper_height
                cab.create(f"Upper Cabinet L{i+1}")
                cab.obj.parent = self.obj_wall
                cab.obj.location.x = current_x
                cab.obj.location.z = upper_z
                self.apply_styles_to_cabinet(context, cab.obj)
                hb_utils.run_calc_fix(context, cab.obj)
                created_cabinets.append(cab.obj)
                current_x += left_upper_width
            
            # Right uppers
            current_x = upper_left_offset + upper_width_each + self.range_width
            for i in range(self.right_upper_cabinet_qty):
                cab = types_frameless.UpperCabinet()
                cab.width = right_upper_width
                cab.depth = upper_depth
                cab.height = upper_height
                cab.create(f"Upper Cabinet R{i+1}")
                cab.obj.parent = self.obj_wall
                cab.obj.location.x = current_x
                cab.obj.location.z = upper_z
                self.apply_styles_to_cabinet(context, cab.obj)
                hb_utils.run_calc_fix(context, cab.obj)
                created_cabinets.append(cab.obj)
                current_x += right_upper_width
        else:
            # Single upper area (no range, or raised upper over range)
            upper_cab_width = available_upper_width / self.left_upper_cabinet_qty
            current_x = upper_left_offset
            for i in range(self.left_upper_cabinet_qty):
                cab = types_frameless.UpperCabinet()
                cab.width = upper_cab_width
                cab.depth = upper_depth
                cab.height = upper_height
                cab.create(f"Upper Cabinet {i+1}")
                cab.obj.parent = self.obj_wall
                cab.obj.location.x = current_x
                cab.obj.location.z = upper_z
                self.apply_styles_to_cabinet(context, cab.obj)
                hb_utils.run_calc_fix(context, cab.obj)
                created_cabinets.append(cab.obj)
                current_x += upper_cab_width
        
        # Clear the preview
        self.clear_preview(context)
        
        return created_cabinets

    def clear_preview(self, context):
        """Clear all preview objects."""
        # Delete preview cages (rects are children, so they get deleted too)
        for cage in [self.cage_refrigerator, self.cage_range, self.cage_pantry,
                     self.cage_left_base, self.cage_right_base,
                     self.cage_left_upper, self.cage_right_upper]:
            if cage:
                hb_utils.delete_obj_and_children(cage)
        
        # Clear cage references
        self.cage_refrigerator = None
        self.cage_range = None
        self.cage_pantry = None
        self.cage_left_base = None
        self.cage_right_base = None
        self.cage_left_upper = None
        self.cage_right_upper = None
        
        # Clear front rect references
        self.rect_refrigerator = None
        self.rect_range = None
        self.rect_pantry = None
        self.rect_left_base = None
        self.rect_right_base = None
        self.rect_left_upper = None
        self.rect_right_upper = None
        
        # Clear top rect references
        self.rect_top_refrigerator = None
        self.rect_top_range = None
        self.rect_top_pantry = None
        self.rect_top_left_base = None
        self.rect_top_right_base = None
        self.rect_top_left_upper = None
        self.rect_top_right_upper = None
        
        self.is_active = False

    def draw_ui(self, context, layout):
        """Draw the UI for this template."""
        props = self.get_cabinet_props(context)
        
        # Room dimensions
        box = layout.box()
        box.label(text="Room Dimensions", icon='HOME')
        
        row = box.row()
        row.label(text="Wall Width:")
        row.prop(self, 'wall_width', text="")
        
        row = box.row()
        row.label(text="Ceiling Height:")
        row.prop(self, 'ceiling_height', text="")
        
        # Appliances
        box = layout.box()
        box.label(text="Appliances", icon='OUTLINER_OB_SURFACE')
        
        row = box.row()
        row.label(text="Pantry:")
        row.prop(self, 'pantry_location', text="")
        
        if self.pantry_location != 'NONE':
            row = box.row()
            row.label(text="Pantry Width:")
            row.prop(self, 'pantry_width', text="")
        
        row = box.row()
        row.label(text="Refrigerator:")
        row.prop(self, 'refrigerator_location', text="")
        
        if self.refrigerator_location != 'NONE':
            row = box.row()
            row.label(text="Refrigerator Width:")
            row.prop(self, 'refrigerator_width', text="")
        
        row = box.row()
        row.label(text="Range:")
        row.prop(self, 'range_location', text="")
        
        if self.range_location != 'NONE':
            row = box.row()
            row.label(text="Range Width:")
            row.prop(self, 'range_width', text="")
            
            row = box.row()
            row.label(text="Above Range:")
            row.prop(self, 'range_hood_type', text="")
            
            if self.range_hood_type == 'RAISE_UPPER':
                row = box.row()
                row.label(text="Hood Height:")
                row.prop(self, 'range_hood_height', text="")
        
        # Cabinet quantities
        box = layout.box()
        box.label(text="Cabinet Quantities", icon='LINENUMBERS_ON')
        
        row = box.row()
        row.label(text="")
        row.label(text="Left")
        row.label(text="Right")
        
        row = box.row()
        row.label(text="Base:")
        row.prop(self, 'left_base_cabinet_qty', text="")
        if self.range_location != 'NONE':
            row.prop(self, 'right_base_cabinet_qty', text="")
        else:
            row.label(text="")
        
        row = box.row()
        row.label(text="Upper:")
        row.prop(self, 'left_upper_cabinet_qty', text="")
        if self.range_location != 'NONE' and self.range_hood_type == 'EMPTY':
            row.prop(self, 'right_upper_cabinet_qty', text="")
        else:
            row.label(text="")
        
        # Offsets
        box = layout.box()
        box.label(text="Offsets", icon='ARROW_LEFTRIGHT')
        
        row = box.row()
        row.label(text="Left Offset:")
        row.prop(self, 'left_offset', text="")
        
        row = box.row()
        row.label(text="Right Offset:")
        row.prop(self, 'right_offset', text="")




# =====================================================================
# ISLAND TEMPLATE
# =====================================================================

class Island_Template(HB_Frameless_Base_Template):
    """
    Template for a kitchen island.
    Island faces the selected wall (rotated 180 degrees).
    """

    island_depth: FloatProperty(
        name="Island Depth",
        default=inch(24),
        unit='LENGTH',
        precision=4,
        update=update_template_preview
    )  # type: ignore

    offset_from_wall: FloatProperty(
        name="Offset From Wall",
        default=inch(72),
        unit='LENGTH',
        precision=4,
        update=update_template_preview
    )  # type: ignore

    sink_location: EnumProperty(
        name="Sink Location",
        items=[
            ('NONE', 'None', 'No sink'),
            ('CENTER', 'Center', 'Sink in center')
        ],
        default='NONE',
        update=update_template_preview
    )  # type: ignore

    sink_width: FloatProperty(
        name="Sink Width",
        default=inch(36),
        unit='LENGTH',
        precision=4,
        update=update_template_preview
    )  # type: ignore

    dishwasher_location: EnumProperty(
        name="Dishwasher Location",
        items=[
            ('NONE', 'None', 'No dishwasher'),
            ('LEFT', 'Left of Sink', 'Dishwasher left of sink'),
            ('RIGHT', 'Right of Sink', 'Dishwasher right of sink')
        ],
        default='NONE',
        update=update_template_preview
    )  # type: ignore

    dishwasher_width: FloatProperty(
        name="Dishwasher Width",
        default=inch(24),
        unit='LENGTH',
        precision=4,
        update=update_template_preview
    )  # type: ignore

    left_cabinet_qty: IntProperty(
        name="Left Cabinet Qty",
        default=2,
        min=1,
        max=6,
        update=update_template_preview
    )  # type: ignore

    right_cabinet_qty: IntProperty(
        name="Right Cabinet Qty",
        default=2,
        min=1,
        max=6,
        update=update_template_preview
    )  # type: ignore

    # Preview cage objects
    cage_left_base: PointerProperty(name="Left Base Cage", type=bpy.types.Object)  # type: ignore
    cage_sink: PointerProperty(name="Sink Cage", type=bpy.types.Object)  # type: ignore
    cage_dishwasher: PointerProperty(name="Dishwasher Cage", type=bpy.types.Object)  # type: ignore
    cage_right_base: PointerProperty(name="Right Base Cage", type=bpy.types.Object)  # type: ignore
    
    # Preview rectangle labels (front - elevation view)
    rect_left_base: PointerProperty(name="Left Base Rect", type=bpy.types.Object)  # type: ignore
    rect_sink: PointerProperty(name="Sink Rect", type=bpy.types.Object)  # type: ignore
    rect_dishwasher: PointerProperty(name="Dishwasher Rect", type=bpy.types.Object)  # type: ignore
    rect_right_base: PointerProperty(name="Right Base Rect", type=bpy.types.Object)  # type: ignore
    
    # Preview rectangle labels (top - plan view)
    rect_top_left_base: PointerProperty(name="Left Base Rect Top", type=bpy.types.Object)  # type: ignore
    rect_top_sink: PointerProperty(name="Sink Rect Top", type=bpy.types.Object)  # type: ignore
    rect_top_dishwasher: PointerProperty(name="Dishwasher Rect Top", type=bpy.types.Object)  # type: ignore
    rect_top_right_base: PointerProperty(name="Right Base Rect Top", type=bpy.types.Object)  # type: ignore

    def create_preview(self, context):
        """Create all preview cages for this template."""
        if not self.obj_wall:
            return
        
        # Create preview cages with rectangle labels (front and top)
        self.cage_left_base, self.rect_left_base, self.rect_top_left_base = self.create_preview_cage(
            context, "PREVIEW_LEFT_BASE", "BASE CABINETS", self.obj_wall)
        self.cage_sink, self.rect_sink, self.rect_top_sink = self.create_preview_cage(
            context, "PREVIEW_SINK", "SINK CABINET", self.obj_wall)
        self.cage_dishwasher, self.rect_dishwasher, self.rect_top_dishwasher = self.create_preview_cage(
            context, "PREVIEW_DISHWASHER", "DISHWASHER", self.obj_wall)
        self.cage_right_base, self.rect_right_base, self.rect_top_right_base = self.create_preview_cage(
            context, "PREVIEW_RIGHT_BASE", "BASE CABINETS", self.obj_wall)
        
        self.is_active = True
        self.update_preview(context)
        
        # Toggle selection mode to display cabinet cages correctly
        props = self.get_cabinet_props(context)
        props.frameless_selection_mode = "Cabinets"
        
        # Update preview again to properly hide cages that should be hidden
        self.update_preview(context)

    def update_preview(self, context):
        """Update all preview cages based on current property values."""
        if not self.obj_wall or not self.is_active:
            return
        
        props = self.get_cabinet_props(context)
        base_height = props.base_cabinet_height
        
        # Get wall width and calculate island width
        wall = hb_types.GeoNodeWall(self.obj_wall)
        wall_width = wall.get_input('Length')
        island_width = wall_width - self.left_offset - self.right_offset
        
        # Island is rotated 180 degrees and offset from wall
        island_y = -self.offset_from_wall - self.island_depth
        island_rotation = math.pi  # 180 degrees
        
        has_sink = self.sink_location != 'NONE'
        has_dishwasher = self.dishwasher_location != 'NONE' and has_sink
        
        if not has_sink:
            # No sink - single base cabinet area spans full width
            label = f"BASE ({self.left_cabinet_qty})"
            self.update_preview_cage(self.cage_left_base, self.rect_left_base, self.rect_top_left_base,
                                     wall_width - self.right_offset, island_y, 0,
                                     island_width, self.island_depth, base_height,
                                     label, True)
            # Set rotation
            if self.cage_left_base:
                self.cage_left_base.rotation_euler.z = island_rotation
            
            # Hide unused cages
            self.update_preview_cage(self.cage_sink, self.rect_sink, self.rect_top_sink, 0, 0, 0, 0, 0, 0, visible=False)
            self.update_preview_cage(self.cage_dishwasher, self.rect_dishwasher, self.rect_top_dishwasher, 0, 0, 0, 0, 0, 0, visible=False)
            self.update_preview_cage(self.cage_right_base, self.rect_right_base, self.rect_top_right_base, 0, 0, 0, 0, 0, 0, visible=False)
        else:
            # Sink in center
            side_width = (island_width - self.sink_width) / 2
            
            if has_dishwasher and self.dishwasher_location == 'LEFT':
                left_cabinet_width = side_width - self.dishwasher_width
                right_cabinet_width = side_width
            elif has_dishwasher and self.dishwasher_location == 'RIGHT':
                left_cabinet_width = side_width
                right_cabinet_width = side_width - self.dishwasher_width
            else:
                left_cabinet_width = side_width
                right_cabinet_width = side_width
            
            # When rotated 180, place cabinets from right to left
            current_x = wall_width - self.right_offset
            
            # Right base cabinets (placed first since we're going right to left)
            right_label = f"BASE ({self.right_cabinet_qty})"
            self.update_preview_cage(self.cage_right_base, self.rect_right_base, self.rect_top_right_base,
                                     current_x, island_y, 0,
                                     right_cabinet_width, self.island_depth, base_height,
                                     right_label, True)
            if self.cage_right_base:
                self.cage_right_base.rotation_euler.z = island_rotation
            current_x -= right_cabinet_width
            
            # Dishwasher (right of sink)
            if has_dishwasher and self.dishwasher_location == 'RIGHT':
                self.update_preview_cage(self.cage_dishwasher, self.rect_dishwasher, self.rect_top_dishwasher,
                                         current_x, island_y, 0,
                                         self.dishwasher_width, self.island_depth, base_height,
                                         "DISHWASHER (1)", True)
                if self.cage_dishwasher:
                    self.cage_dishwasher.rotation_euler.z = island_rotation
                current_x -= self.dishwasher_width
            
            # Sink cabinet
            self.update_preview_cage(self.cage_sink, self.rect_sink, self.rect_top_sink,
                                     current_x, island_y, 0,
                                     self.sink_width, self.island_depth, base_height,
                                     "SINK (1)", True)
            if self.cage_sink:
                self.cage_sink.rotation_euler.z = island_rotation
            current_x -= self.sink_width
            
            # Dishwasher (left of sink)
            if has_dishwasher and self.dishwasher_location == 'LEFT':
                self.update_preview_cage(self.cage_dishwasher, self.rect_dishwasher, self.rect_top_dishwasher,
                                         current_x, island_y, 0,
                                         self.dishwasher_width, self.island_depth, base_height,
                                         "DISHWASHER (1)", True)
                if self.cage_dishwasher:
                    self.cage_dishwasher.rotation_euler.z = island_rotation
                current_x -= self.dishwasher_width
            
            if not has_dishwasher:
                self.update_preview_cage(self.cage_dishwasher, self.rect_dishwasher, self.rect_top_dishwasher, 0, 0, 0, 0, 0, 0, visible=False)
            
            # Left base cabinets (placed last)
            left_label = f"BASE ({self.left_cabinet_qty})"
            self.update_preview_cage(self.cage_left_base, self.rect_left_base, self.rect_top_left_base,
                                     current_x, island_y, 0,
                                     left_cabinet_width, self.island_depth, base_height,
                                     left_label, True)
            if self.cage_left_base:
                self.cage_left_base.rotation_euler.z = island_rotation

    def draw_cabinets(self, context):
        """Draw the actual cabinets from the template."""
        if not self.obj_wall:
            return []
        
        created_cabinets = []
        props = self.get_cabinet_props(context)
        
        base_height = props.base_cabinet_height
        
        # Get wall width and calculate island width
        wall = hb_types.GeoNodeWall(self.obj_wall)
        wall_width = wall.get_input('Length')
        island_width = wall_width - self.left_offset - self.right_offset
        
        # Island position and rotation (in wall's local space)
        island_y = -self.offset_from_wall - self.island_depth
        island_rotation = math.pi
        
        # Get wall transform for converting to world space
        # Islands are NOT parented to walls - they're freestanding
        wall_matrix = self.obj_wall.matrix_world
        wall_rotation_z = self.obj_wall.rotation_euler.z
        
        has_sink = self.sink_location != 'NONE'
        has_dishwasher = self.dishwasher_location != 'NONE' and has_sink
        
        if not has_sink:
            # No sink - create base cabinets spanning full width
            cabinet_width = island_width / self.left_cabinet_qty
            current_x = wall_width - self.right_offset
            
            for i in range(self.left_cabinet_qty):
                cab = types_frameless.BaseCabinet()
                cab.width = cabinet_width
                cab.depth = self.island_depth
                cab.height = base_height
                cab.create(f"Island Cabinet {i+1}")
                # Islands are NOT parented to walls - position in world space
                local_pos = Vector((current_x, island_y, 0))
                world_pos = wall_matrix @ local_pos
                cab.obj.location = world_pos
                cab.obj.rotation_euler.z = wall_rotation_z + island_rotation
                self.apply_styles_to_cabinet(context, cab.obj)
                hb_utils.run_calc_fix(context, cab.obj)
                created_cabinets.append(cab.obj)
                current_x -= cabinet_width
        else:
            # Sink in center
            side_width = (island_width - self.sink_width) / 2
            
            if has_dishwasher and self.dishwasher_location == 'LEFT':
                left_cabinet_width = side_width - self.dishwasher_width
                right_cabinet_width = side_width
            elif has_dishwasher and self.dishwasher_location == 'RIGHT':
                left_cabinet_width = side_width
                right_cabinet_width = side_width - self.dishwasher_width
            else:
                left_cabinet_width = side_width
                right_cabinet_width = side_width
            
            current_x = wall_width - self.right_offset
            
            # Right base cabinets
            right_cab_width = right_cabinet_width / self.right_cabinet_qty
            for i in range(self.right_cabinet_qty):
                cab = types_frameless.BaseCabinet()
                cab.width = right_cab_width
                cab.depth = self.island_depth
                cab.height = base_height
                cab.create(f"Island Cabinet R{i+1}")
                # Islands are NOT parented to walls - position in world space
                local_pos = Vector((current_x, island_y, 0))
                world_pos = wall_matrix @ local_pos
                cab.obj.location = world_pos
                cab.obj.rotation_euler.z = wall_rotation_z + island_rotation
                self.apply_styles_to_cabinet(context, cab.obj)
                hb_utils.run_calc_fix(context, cab.obj)
                created_cabinets.append(cab.obj)
                current_x -= right_cab_width
            
            # Dishwasher (right of sink)
            if has_dishwasher and self.dishwasher_location == 'RIGHT':
                dishwasher = types_appliances.Dishwasher()
                dishwasher.width = self.dishwasher_width
                dishwasher.depth = self.island_depth
                dishwasher.height = base_height
                dishwasher.create("Dishwasher")
                # Islands are NOT parented to walls - position in world space
                local_pos = Vector((current_x, island_y, 0))
                world_pos = wall_matrix @ local_pos
                dishwasher.obj.location = world_pos
                dishwasher.obj.rotation_euler.z = wall_rotation_z + island_rotation
                created_cabinets.append(dishwasher.obj)
                current_x -= self.dishwasher_width
            
            # Sink cabinet
            sink_cab = types_frameless.BaseCabinet()
            sink_cab.width = self.sink_width
            sink_cab.depth = self.island_depth
            sink_cab.height = base_height
            sink_cab.create("Sink Cabinet")
            # Islands are NOT parented to walls - position in world space
            local_pos = Vector((current_x, island_y, 0))
            world_pos = wall_matrix @ local_pos
            sink_cab.obj.location = world_pos
            sink_cab.obj.rotation_euler.z = wall_rotation_z + island_rotation
            self.apply_styles_to_cabinet(context, sink_cab.obj)
            hb_utils.run_calc_fix(context, sink_cab.obj)
            created_cabinets.append(sink_cab.obj)
            current_x -= self.sink_width
            
            # Dishwasher (left of sink)
            if has_dishwasher and self.dishwasher_location == 'LEFT':
                dishwasher = types_appliances.Dishwasher()
                dishwasher.width = self.dishwasher_width
                dishwasher.depth = self.island_depth
                dishwasher.height = base_height
                dishwasher.create("Dishwasher")
                # Islands are NOT parented to walls - position in world space
                local_pos = Vector((current_x, island_y, 0))
                world_pos = wall_matrix @ local_pos
                dishwasher.obj.location = world_pos
                dishwasher.obj.rotation_euler.z = wall_rotation_z + island_rotation
                created_cabinets.append(dishwasher.obj)
                current_x -= self.dishwasher_width
            
            # Left base cabinets
            left_cab_width = left_cabinet_width / self.left_cabinet_qty
            for i in range(self.left_cabinet_qty):
                cab = types_frameless.BaseCabinet()
                cab.width = left_cab_width
                cab.depth = self.island_depth
                cab.height = base_height
                cab.create(f"Island Cabinet L{i+1}")
                # Islands are NOT parented to walls - position in world space
                local_pos = Vector((current_x, island_y, 0))
                world_pos = wall_matrix @ local_pos
                cab.obj.location = world_pos
                cab.obj.rotation_euler.z = wall_rotation_z + island_rotation
                self.apply_styles_to_cabinet(context, cab.obj)
                hb_utils.run_calc_fix(context, cab.obj)
                created_cabinets.append(cab.obj)
                current_x -= left_cab_width
        
        # Clear the preview
        self.clear_preview(context)
        
        return created_cabinets

    def clear_preview(self, context):
        """Clear all preview objects."""
        for cage in [self.cage_left_base, self.cage_sink, self.cage_dishwasher, self.cage_right_base]:
            if cage:
                hb_utils.delete_obj_and_children(cage)
        
        self.cage_left_base = None
        self.cage_sink = None
        self.cage_dishwasher = None
        self.cage_right_base = None
        
        # Clear front rect references
        self.rect_left_base = None
        self.rect_sink = None
        self.rect_dishwasher = None
        self.rect_right_base = None
        
        # Clear top rect references
        self.rect_top_left_base = None
        self.rect_top_sink = None
        self.rect_top_dishwasher = None
        self.rect_top_right_base = None
        
        self.is_active = False

    def draw_ui(self, context, layout):
        """Draw the UI for this template."""
        props = self.get_cabinet_props(context)
        
        # Island dimensions
        box = layout.box()
        box.label(text="Island Dimensions", icon='MESH_PLANE')
        
        row = box.row()
        row.label(text="Island Depth:")
        row.prop(self, 'island_depth', text="")
        
        row = box.row()
        row.label(text="Offset From Wall:")
        row.prop(self, 'offset_from_wall', text="")
        
        # Appliances
        box = layout.box()
        box.label(text="Appliances", icon='OUTLINER_OB_SURFACE')
        
        row = box.row()
        row.label(text="Sink:")
        row.prop(self, 'sink_location', text="")
        
        if self.sink_location != 'NONE':
            row = box.row()
            row.label(text="Sink Width:")
            row.prop(self, 'sink_width', text="")
            
            row = box.row()
            row.label(text="Dishwasher:")
            row.prop(self, 'dishwasher_location', text="")
            
            if self.dishwasher_location != 'NONE':
                row = box.row()
                row.label(text="Dishwasher Width:")
                row.prop(self, 'dishwasher_width', text="")
        
        # Cabinet quantities
        box = layout.box()
        box.label(text="Cabinet Quantities", icon='LINENUMBERS_ON')
        
        row = box.row()
        row.label(text="")
        row.label(text="Left")
        row.label(text="Right")
        
        row = box.row()
        row.label(text="Base:")
        row.prop(self, 'left_cabinet_qty', text="")
        if self.sink_location != 'NONE':
            row.prop(self, 'right_cabinet_qty', text="")
        else:
            row.label(text="")
        
        # Offsets
        box = layout.box()
        box.label(text="Offsets", icon='ARROW_LEFTRIGHT')
        
        row = box.row()
        row.label(text="Left Offset:")
        row.prop(self, 'left_offset', text="")
        
        row = box.row()
        row.label(text="Right Offset:")
        row.prop(self, 'right_offset', text="")


# =====================================================================
# TEMPLATE REGISTRY
# =====================================================================

TEMPLATE_REGISTRY = {
    'Refrigerator Range': 'hb_template_refrigerator_range',
    'Island': 'hb_template_island',
}


def get_template(context, template_name):
    """Get a template PropertyGroup by name."""
    prop_name = TEMPLATE_REGISTRY.get(template_name)
    if prop_name:
        return getattr(context.scene, prop_name, None)
    return None


# =====================================================================
# OPERATORS
# =====================================================================

class hb_frameless_OT_select_elevation_template(Operator):
    bl_idname = "hb_frameless.select_elevation_template"
    bl_label = "Select Elevation Template"
    bl_description = "Select an elevation template for the current wall"
    bl_options = {'UNDO'}

    template_name: StringProperty(name="Template Name")  # type: ignore

    @classmethod
    def poll(cls, context):
        wall_bp = hb_utils.get_wall_bp(context.active_object)
        return wall_bp is not None

    def execute(self, context):
        wall_bp = hb_utils.get_wall_bp(context.active_object)
        if not wall_bp:
            self.report({'ERROR'}, "No wall selected")
            return {'CANCELLED'}

        template = get_template(context, self.template_name)
        if not template:
            self.report({'ERROR'}, f"Template '{self.template_name}' not found")
            return {'CANCELLED'}

        # Clear any existing preview
        if template.is_active:
            template.clear_preview(context)

        # Initialize and create preview
        template.init_from_wall(wall_bp)
        template.create_preview(context)

        # Store active template name
        context.scene.hb_frameless.selected_template = self.template_name

        return {'FINISHED'}


class hb_frameless_OT_draw_elevation_template(Operator):
    bl_idname = "hb_frameless.draw_elevation_template"
    bl_label = "Draw Elevation Template"
    bl_description = "Draw the cabinets from the current template"
    bl_options = {'UNDO'}

    def execute(self, context):
        template_name = context.scene.hb_frameless.selected_template
        template = get_template(context, template_name)
        
        if not template or not template.is_active:
            self.report({'ERROR'}, "No active template")
            return {'CANCELLED'}

        # Draw the cabinets
        cabinets = template.draw_cabinets(context)
        
        # Clear template selection
        context.scene.hb_frameless.selected_template = ""
        
        self.report({'INFO'}, f"Created {len(cabinets)} cabinet(s)")
        return {'FINISHED'}


class hb_frameless_OT_clear_elevation_template(Operator):
    bl_idname = "hb_frameless.clear_elevation_template"
    bl_label = "Clear Template Preview"
    bl_description = "Clear the current template preview"
    bl_options = {'UNDO'}

    def execute(self, context):
        template_name = context.scene.hb_frameless.selected_template
        template = get_template(context, template_name)
        
        if template:
            template.clear_preview(context)

        context.scene.hb_frameless.selected_template = ""

        return {'FINISHED'}


# =====================================================================
# MENUS
# =====================================================================

class HOME_BUILDER_MT_elevation_templates(Menu):
    bl_label = "Elevation Templates"
    bl_idname = "HOME_BUILDER_MT_elevation_templates"

    def draw(self, context):
        layout = self.layout
        
        for template_name in TEMPLATE_REGISTRY.keys():
            op = layout.operator(
                "hb_frameless.select_elevation_template",
                text=template_name
            )
            op.template_name = template_name


# =====================================================================
# UI PANEL HELPER
# =====================================================================

def draw_elevation_template_ui(context, layout):
    """Draw the elevation template UI section in a panel."""
    wall_bp = hb_utils.get_wall_bp(context.active_object)
    
    if not wall_bp:
        layout.label(text="Select a wall to use templates", icon='INFO')
        return
    
    props = context.scene.hb_frameless
    selected = props.selected_template
    
    # Template selector
    if selected == "" or selected not in TEMPLATE_REGISTRY:
        menu_text = "Select Elevation Template..."
    else:
        menu_text = selected
    
    row = layout.row()
    row.scale_y = 1.3
    row.menu('HOME_BUILDER_MT_elevation_templates', text=menu_text)
    
    # If template is selected, draw its UI
    if selected in TEMPLATE_REGISTRY:
        template = get_template(context, selected)
        if template and template.is_active:
            template.draw_ui(context, layout)
            
            # Action buttons
            row = layout.row(align=True)
            row.scale_y = 1.5
            row.operator('hb_frameless.draw_elevation_template', text="Draw Cabinets", icon='CHECKMARK')
            row.operator('hb_frameless.clear_elevation_template', text="Cancel", icon='X')


# =====================================================================
# REGISTRATION
# =====================================================================

classes = (
    HB_Frameless_Base_Template,
    Refrigerator_Range_Template,
    Island_Template,
    hb_frameless_OT_select_elevation_template,
    hb_frameless_OT_draw_elevation_template,
    hb_frameless_OT_clear_elevation_template,
    HOME_BUILDER_MT_elevation_templates,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Register template scene properties
    bpy.types.Scene.hb_template_refrigerator_range = PointerProperty(
        name="Refrigerator Range Template",
        type=Refrigerator_Range_Template,
    )
    bpy.types.Scene.hb_template_island = PointerProperty(
        name="Island Template",
        type=Island_Template,
    )


def unregister():
    # Unregister template scene properties
    if hasattr(bpy.types.Scene, 'hb_template_refrigerator_range'):
        del bpy.types.Scene.hb_template_refrigerator_range
    if hasattr(bpy.types.Scene, 'hb_template_island'):
        del bpy.types.Scene.hb_template_island
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
