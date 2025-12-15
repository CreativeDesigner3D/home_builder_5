import bpy
import math
from mathutils import Vector, Matrix, Euler
from . import hb_types
from . import units

# =============================================================================
# PAPER SIZE DEFINITIONS (shared with hb_layouts)
# =============================================================================

PAPER_SIZES = {
    'LETTER': (8.5, 11.0),
    'LEGAL': (8.5, 14.0),
    'TABLOID': (11.0, 17.0),
    'A4': (8.27, 11.69),
    'A3': (11.69, 16.54),
}

DEFAULT_DPI = 150


# =============================================================================
# DETAIL VIEW CLASS
# =============================================================================

class DetailView:
    """Class for 2D detail drawings - like AutoCAD detail views."""
    
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
        
        # Create new scene
        self.scene = bpy.data.scenes.new(base_name)
        self.scene['IS_DETAIL_VIEW'] = True
        bpy.context.window.scene = self.scene
        
        # Copy unit settings to new scene
        self.scene.unit_settings.system = unit_system
        self.scene.unit_settings.scale_length = unit_scale
        self.scene.unit_settings.length_unit = unit_length
        
        # Copy snap settings
        new_tool_settings = bpy.context.tool_settings
        new_tool_settings.snap_elements = snap_elements
        new_tool_settings.use_snap = use_snap
        
        # Set up 2D workspace view
        self._setup_2d_view()
        
        return self.scene
    
    
    def _setup_2d_view(self):
        """Configure viewport for 2D drawing."""
        # Set viewport to top-down orthographic
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.region_3d.view_perspective = 'ORTHO'
                        space.region_3d.view_rotation = Euler((0, 0, 0)).to_quaternion()
                        space.shading.type = 'SOLID'
                        space.shading.color_type = 'OBJECT'
                        space.shading.light = 'FLAT'
                        space.overlay.show_floor = False
                        space.overlay.show_axis_x = True
                        space.overlay.show_axis_y = True
                        space.overlay.show_axis_z = False
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
        self.obj.color = (0, 0, 0, 1)  # Black line
        
        # Link to scene
        bpy.context.scene.collection.objects.link(self.obj)
        
        # Create black material
        mat = bpy.data.materials.new(f"{name}_Mat")
        mat.use_nodes = True
        mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0, 0, 0, 1)
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
        curve = bpy.data.curves.new(name, 'CURVE')
        curve.dimensions = '2D'
        
        # Create initial spline with one point
        spline = curve.splines.new('POLY')
        spline.points[0].co = (0, 0, 0, 1)
        
        # Create object
        self.obj = bpy.data.objects.new(name, curve)
        self.obj['IS_DETAIL_POLYLINE'] = True
        self.obj.color = (0, 0, 0, 1)
        
        bpy.context.scene.collection.objects.link(self.obj)
        
        # Create material
        mat = bpy.data.materials.new(f"{name}_Mat")
        mat.use_nodes = True
        mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0, 0, 0, 1)
        curve.materials.append(mat)
        
        curve.bevel_depth = 0.002
        
        return self.obj
    
    def add_point(self, point: Vector):
        """Add a point to the polyline."""
        if self.obj and self.obj.type == 'CURVE':
            spline = self.obj.data.splines[0]
            spline.points.add(1)
            idx = len(spline.points) - 1
            spline.points[idx].co = (point.x, point.y, point.z, 1)
    
    def set_point(self, index: int, point: Vector):
        """Set a specific point in the polyline."""
        if self.obj and self.obj.type == 'CURVE':
            spline = self.obj.data.splines[0]
            if 0 <= index < len(spline.points):
                spline.points[index].co = (point.x, point.y, point.z, 1)
    
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
        mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0, 0, 0, 1)
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
        """Set the circle center location."""
        if self.obj:
            self.obj.location = (center[0], center[1], 0)
    
    def get_radius(self) -> float:
        """Get the current radius."""
        return getattr(self, '_radius', 1.0)

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
        self.obj.color = (0, 0, 0, 1)
        
        bpy.context.scene.collection.objects.link(self.obj)
        
        # Create black material
        mat = bpy.data.materials.new(f"{name}_Mat")
        mat.use_nodes = True
        mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0, 0, 0, 1)
        text_data.materials.append(mat)
        
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
        align_y: 'TOP', 'TOP_BASELINE', 'MIDDLE', 'BOTTOM_BASELINE', 'BOTTOM'
        """
        if self.obj and self.obj.type == 'FONT':
            self.obj.data.align_x = align_x
            self.obj.data.align_y = align_y
