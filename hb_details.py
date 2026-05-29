import bpy
import math
import os
from mathutils import Vector, Matrix, Euler
from . import hb_types
from . import units

# =============================================================================
# DETAIL VIEW CLASS
# =============================================================================

class DetailView:
    """Class for 2D detail drawings - CAD detail views."""
    
    scene: bpy.types.Scene = None
    
    def __init__(self, scene=None):
        if scene:
            self.scene = scene
    
    @staticmethod
    def get_all_detail_views():
        """Return all scenes tagged as detail views."""
        views = []
        for scene in bpy.data.scenes:
            if scene.get('IS_DETAIL_VIEW'):
                views.append(scene)
        return views
    
    def create(self, name: str = "Detail") -> bpy.types.Scene:
        """Create a new detail scene for 2D drawing."""
        # Store original scene's units and tool settings
        original_scene = bpy.context.scene
        
        # Store unit settings
        unit_system = original_scene.unit_settings.system
        unit_scale = original_scene.unit_settings.scale_length
        unit_length = original_scene.unit_settings.length_unit
        
        # Store tool settings (snapping)
        tool_settings = bpy.context.tool_settings
        snap_elements = set(tool_settings.snap_elements)
        use_snap = tool_settings.use_snap
        
        # Generate unique name
        base_name = name
        counter = 1
        while base_name in bpy.data.scenes:
            base_name = f"{name} {counter}"
            counter += 1
        
        from . import hb_utils
        
        # Save view state if currently in a room scene
        original_scene = bpy.context.scene
        if hb_utils.is_room_scene(original_scene):
            hb_utils.save_view_state(original_scene)
        
        # Create new scene
        self.scene = bpy.data.scenes.new(base_name)
        self.scene['IS_DETAIL_VIEW'] = True
        bpy.context.window.scene = self.scene
        
        # Copy unit settings to new scene
        self.scene.unit_settings.system = unit_system
        self.scene.unit_settings.scale_length = unit_scale
        self.scene.unit_settings.length_unit = unit_length

        # Inherit the active product library (Face Frame / Frameless /
        # Closet) from the source scene. 
        _src_hb = getattr(original_scene, "home_builder", None)
        _new_hb = getattr(self.scene, "home_builder", None)
        if _src_hb is not None and _new_hb is not None:
            _new_hb.product_tab = _src_hb.product_tab
        
        # Copy snap settings
        new_tool_settings = bpy.context.tool_settings
        new_tool_settings.snap_elements = snap_elements
        new_tool_settings.use_snap = use_snap
        
        # Set up 2D workspace view
        self._setup_2d_view()
        
        return self.scene
    
    
    def _setup_2d_view(self):
        """Configure viewport for 2D drawing."""
        from . import hb_utils
        
        # Set viewport to top-down orthographic
        hb_utils.set_top_down_view()
        
        # Set shading options
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'SOLID'
                        space.shading.color_type = 'OBJECT'
                        break


# =============================================================================
# LINE GEOMETRY TYPE
# =============================================================================

class GeoNodeLine(hb_types.GeoNodeObject):
    """Simple 2D line using a curve object."""
    
    def create(self, name: str = "Line"):
        """Create a line as a simple curve."""
        # Create curve data
        curve = bpy.data.curves.new(name, 'CURVE')
        curve.dimensions = '2D'
        
        # Create a spline
        spline = curve.splines.new('POLY')
        spline.points.add(1)  # Start with 2 points (0,0) to (1,0)
        spline.points[0].co = (0, 0, 0, 1)
        spline.points[1].co = (1, 0, 0, 1)
        
        # Create object
        self.obj = bpy.data.objects.new(name, curve)
        self.obj['IS_DETAIL_LINE'] = True
        self.obj['IS_2D_ANNOTATION'] = True
        self.obj.color = (0, 0, 0, 1)  # Black line
        
        # Link to scene
        bpy.context.scene.collection.objects.link(self.obj)
        
        # Create black material
        mat = bpy.data.materials.new(f"{name}_Mat")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = (0, 0, 0, 1)
        curve.materials.append(mat)

        # Set bevel for line thickness
        curve.bevel_depth = 0.002  # Small line thickness

        return self.obj
    
    def set_points(self, start: Vector, end: Vector):
        """Set the start and end points of the line."""
        if self.obj and self.obj.type == 'CURVE':
            spline = self.obj.data.splines[0]
            spline.points[0].co = (start.x, start.y, start.z, 1)
            spline.points[1].co = (end.x, end.y, end.z, 1)
    
    def get_length(self) -> float:
        """Get the length of the line."""
        if self.obj and self.obj.type == 'CURVE':
            spline = self.obj.data.splines[0]
            p0 = Vector(spline.points[0].co[:3])
            p1 = Vector(spline.points[1].co[:3])
            return (p1 - p0).length
        return 0.0


class GeoNodePolyline(hb_types.GeoNodeObject):
    """Multi-segment polyline for complex shapes."""
    
    def create(self, name: str = "Polyline"):
        """Create a polyline as a curve with multiple points."""

        # Get annotation settings from scene
        hb_scene = bpy.context.scene.home_builder
        line_thickness = hb_scene.annotation_line_thickness
        line_color = tuple(hb_scene.annotation_line_color) + (1.0,)

        curve = bpy.data.curves.new(name, 'CURVE')
        curve.dimensions = '2D'
        
        # Create initial spline with one point
        spline = curve.splines.new('POLY')
        spline.points[0].co = (0, 0, 0, 1)
        
        # Create object
        self.obj = bpy.data.objects.new(name, curve)
        self.obj['IS_DETAIL_POLYLINE'] = True
        self.obj['IS_2D_ANNOTATION'] = True
        self.obj.color = line_color
        
        bpy.context.scene.collection.objects.link(self.obj)
        
        # Create material
        mat = bpy.data.materials.new(f"{name}_Mat")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = line_color
        curve.materials.append(mat)
        
        curve.bevel_depth = line_thickness
        
        return self.obj
    
    def add_point(self, point: Vector):
        """Add a point to the polyline.
        
        Converts world coordinates to local coordinates based on object's matrix.
        """
        if self.obj and self.obj.type == 'CURVE':
            spline = self.obj.data.splines[0]
            spline.points.add(1)
            idx = len(spline.points) - 1
            # Convert world to local coordinates
            local_point = self.obj.matrix_world.inverted() @ point
            spline.points[idx].co = (local_point.x, local_point.y, local_point.z, 1)
    
    def set_point(self, index: int, point: Vector):
        """Set a specific point in the polyline.
        
        Converts world coordinates to local coordinates based on object's matrix.
        """
        if self.obj and self.obj.type == 'CURVE':
            spline = self.obj.data.splines[0]
            if 0 <= index < len(spline.points):
                # Convert world to local coordinates
                local_point = self.obj.matrix_world.inverted() @ point
                spline.points[index].co = (local_point.x, local_point.y, local_point.z, 1)
    
    def close(self):
        """Close the polyline to form a closed shape."""
        if self.obj and self.obj.type == 'CURVE':
            self.obj.data.splines[0].use_cyclic_u = True


class GeoNodeCircle(hb_types.GeoNodeObject):
    """Circle shape for 2D details."""
    
    SEGMENTS = 32  # Number of segments for smooth circle
    
    def create(self, name: str = "Circle", radius: float = 1.0):
        """Create a circle as a closed curve."""
        import math
        
        # Create curve data
        curve_data = bpy.data.curves.new(name, 'CURVE')
        curve_data.dimensions = '2D'
        
        # Create object
        self.obj = bpy.data.objects.new(name, curve_data)
        self.obj['IS_DETAIL_CIRCLE'] = True
        self.obj['IS_2D_ANNOTATION'] = True
        self.obj.color = (0, 0, 0, 1)
        
        bpy.context.scene.collection.objects.link(self.obj)
        
        # Create circular spline
        spline = curve_data.splines.new('POLY')
        spline.points.add(self.SEGMENTS - 1)  # Already has 1 point
        
        # Set points in a circle at the given radius
        for i in range(self.SEGMENTS):
            angle = 2 * math.pi * i / self.SEGMENTS
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            spline.points[i].co = (x, y, 0, 1)
        
        # Close the circle
        spline.use_cyclic_u = True
        
        # Set up material (black line) - match GeoNodeLine approach
        mat = bpy.data.materials.new(f"{name}_Mat")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = (0, 0, 0, 1)
        curve_data.materials.append(mat)
        
        # Set bevel for line thickness
        curve_data.bevel_depth = 0.002
        
        # Store radius for later reference
        self._radius = radius
        
        return self.obj
    
    def set_radius(self, radius: float):
        """Set the circle radius by updating all points."""
        import math
        
        if self.obj and self.obj.type == 'CURVE':
            spline = self.obj.data.splines[0]
            for i in range(len(spline.points)):
                angle = 2 * math.pi * i / len(spline.points)
                x = radius * math.cos(angle)
                y = radius * math.sin(angle)
                spline.points[i].co = (x, y, 0, 1)
            self._radius = radius
    
    def set_center(self, center):
        """Set the circle center location (uses full 3D coordinates)."""
        if self.obj:
            self.obj.location = (center[0], center[1], center[2] if len(center) > 2 else 0)
    
    def get_radius(self) -> float:
        """Get the current radius."""
        return getattr(self, '_radius', 1.0)

# =============================================================================
# LABEL TEXT STYLING - shared font / color resolution
# =============================================================================

# Shared material for all annotation / label text. One datablock keeps a
# per-recalc label rebuild from accumulating orphaned materials, and a
# single color edit updates every label at once.
_LABEL_MAT_NAME = "HB Label Text"


def _find_calibri():
    """Locate calibri.ttf in the Windows font directories. Returns the
    first existing path, or None on non-Windows / if Calibri is gone.
    """
    candidates = []
    windir = os.environ.get('WINDIR')
    if windir:
        candidates.append(os.path.join(windir, 'Fonts', 'calibri.ttf'))
    local = os.environ.get('LOCALAPPDATA')
    if local:
        candidates.append(os.path.join(
            local, 'Microsoft', 'Windows', 'Fonts', 'calibri.ttf'))
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


def get_label_font(scene):
    """Resolve the font for annotation / label text.

    home_builder.annotation_font wins when the user has set one. With no
    font set, Calibri is loaded from the system font directory -
    load(check_existing=True) reuses an already-loaded datablock instead
    of duplicating it. When Calibri isn't available (non-Windows, or
    uninstalled) None is returned and the caller leaves the FONT curve's
    default Bfont in place.
    """
    hb = getattr(scene, 'home_builder', None)
    if hb is not None and hb.annotation_font is not None:
        return hb.annotation_font
    path = _find_calibri()
    if path is not None:
        try:
            return bpy.data.fonts.load(path, check_existing=True)
        except RuntimeError:
            pass
    return None


def apply_label_style(text_obj, scene):
    """Apply the resolved annotation font and color to a FONT object.

    Font comes from get_label_font (user preference -> Calibri ->
    Bfont). Color comes from home_builder.annotation_text_color, written
    to both the object color and a shared Principled material so the
    text reads correctly in every shading mode.
    """
    if text_obj is None or text_obj.type != 'FONT':
        return

    font = get_label_font(scene)
    if font is not None:
        text_obj.data.font = font

    hb = getattr(scene, 'home_builder', None)
    if hb is not None:
        color = tuple(hb.annotation_text_color) + (1.0,)
    else:
        color = (0.0, 0.0, 0.0, 1.0)
    text_obj.color = color

    mat = bpy.data.materials.get(_LABEL_MAT_NAME)
    if mat is None:
        mat = bpy.data.materials.new(_LABEL_MAT_NAME)
        mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
    if mat.name not in (m.name for m in text_obj.data.materials if m):
        text_obj.data.materials.append(mat)


class GeoNodeText(hb_types.GeoNodeObject):
    """Text annotation for 2D details."""
    
    def create(self, name: str = "Text", text: str = "Text", size: float = 0.05):
        """Create a text object."""
        # Create font/text data
        text_data = bpy.data.curves.new(name, 'FONT')
        text_data.body = text
        text_data.size = size
        text_data.align_x = 'LEFT'
        text_data.align_y = 'BOTTOM'
        
        # Create object
        self.obj = bpy.data.objects.new(name, text_data)
        self.obj['IS_DETAIL_TEXT'] = True
        self.obj['IS_2D_ANNOTATION'] = True

        bpy.context.scene.collection.objects.link(self.obj)

        # Resolved annotation font + color (Calibri by default).
        apply_label_style(self.obj, bpy.context.scene)

        # Set extrude for visibility (thin 3D text)
        text_data.extrude = 0.001
        
        return self.obj
    
    def set_text(self, text: str):
        """Set the text content."""
        if self.obj and self.obj.type == 'FONT':
            self.obj.data.body = text
    
    def get_text(self) -> str:
        """Get the current text content."""
        if self.obj and self.obj.type == 'FONT':
            return self.obj.data.body
        return ""
    
    def set_size(self, size: float):
        """Set the text size."""
        if self.obj and self.obj.type == 'FONT':
            self.obj.data.size = size
    
    def set_location(self, location):
        """Set the text location."""
        if self.obj:
            self.obj.location = (location[0], location[1], 0)
    
    def set_alignment(self, align_x: str = 'LEFT', align_y: str = 'BOTTOM'):
        """Set text alignment. 
        align_x: 'LEFT', 'CENTER', 'RIGHT', 'JUSTIFY', 'FLUSH'
        align_y: 'TOP', 'TOP_BASELINE', 'CENTER', 'BOTTOM_BASELINE', 'BOTTOM'
        """
        if self.obj and self.obj.type == 'FONT':
            self.obj.data.align_x = align_x
            self.obj.data.align_y = align_y
