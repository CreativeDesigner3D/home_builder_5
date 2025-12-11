import bpy
import math
from mathutils import Vector
from . import hb_types
from . import units

# =============================================================================
# PAPER SIZE DEFINITIONS
# =============================================================================

# Paper sizes in inches (width, height) - portrait orientation
PAPER_SIZES = {
    'LETTER': (8.5, 11.0),
    'LEGAL': (8.5, 14.0),
    'TABLOID': (11.0, 17.0),
    'A4': (8.27, 11.69),
    'A3': (11.69, 16.54),
}

# Default DPI for rendering
DEFAULT_DPI = 150

def get_paper_resolution(paper_size: str, landscape: bool = True, dpi: int = DEFAULT_DPI) -> tuple:
    """Get pixel resolution for a paper size.
    
    Args:
        paper_size: Paper size name (LETTER, LEGAL, TABLOID, A4, A3)
        landscape: If True, swap width and height
        dpi: Dots per inch for rendering
    
    Returns:
        Tuple of (width_px, height_px)
    """
    if paper_size not in PAPER_SIZES:
        paper_size = 'LETTER'
    
    width_in, height_in = PAPER_SIZES[paper_size]
    
    if landscape:
        width_in, height_in = height_in, width_in
    
    return (int(width_in * dpi), int(height_in * dpi))





# =============================================================================
# TITLE BLOCK
# =============================================================================

class TitleBlock:
    """Title block for layout views."""
    
    obj: bpy.types.Object = None
    text_objects: list = None
    
    def __init__(self, obj=None):
        self.obj = obj
        self.text_objects = []
    
    def create(self, scene: bpy.types.Scene, camera: bpy.types.Object):
        """Create a title block for the given scene and camera."""
        
        # Get camera ortho scale to size the title block
        ortho_scale = camera.data.ortho_scale
        
        # Calculate title block dimensions based on camera view
        block_width = ortho_scale * 0.95  # 95% of view width
        block_height = ortho_scale * 0.12  # 12% of view height
        
        # Position at bottom of camera view
        block_y_offset = -10  # Distance from camera (doesn't matter for ortho)
        block_z_offset = -ortho_scale / 2 + block_height / 2 + ortho_scale * 0.02
        
        # Create title block mesh
        verts = [
            (-block_width/2, 0, -block_height/2),
            (block_width/2, 0, -block_height/2),
            (block_width/2, 0, block_height/2),
            (-block_width/2, 0, block_height/2),
        ]
        faces = [(0, 1, 2, 3)]
        
        mesh = bpy.data.meshes.new(f"{scene.name}_TitleBlock_Mesh")
        mesh.from_pydata(verts, [], faces)
        mesh.update()
        
        self.obj = bpy.data.objects.new(f"{scene.name}_TitleBlock", mesh)
        scene.collection.objects.link(self.obj)
        
        # Parent to camera
        self.obj.parent = camera
        self.obj.location = (0, block_y_offset, block_z_offset)
        
        # Create material (white background)
        mat = bpy.data.materials.new(f"{scene.name}_TitleBlock_Mat")
        mat.use_nodes = True
        mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (1, 1, 1, 1)
        self.obj.data.materials.append(mat)
        
        # Text size relative to block height
        large_text_size = block_height * 0.35
        small_text_size = block_height * 0.25
        
        # Add text fields
        # Project name - top left, large
        self._add_text_field(scene, camera, "project_name", "Project Name", 
                            (-block_width/2 + block_width * 0.02, block_y_offset + 0.001, block_z_offset + block_height * 0.15),
                            size=large_text_size)
        
        # View name - bottom left, medium
        self._add_text_field(scene, camera, "view_name", scene.name,
                            (-block_width/2 + block_width * 0.02, block_y_offset + 0.001, block_z_offset - block_height * 0.25),
                            size=small_text_size)
        
        # Scale info - right side
        scale_text = scene.get('hb_layout_scale', '1/4"=1\'')
        self._add_text_field(scene, camera, "scale", f"Scale: {scale_text}",
                            (block_width/2 - block_width * 0.25, block_y_offset + 0.001, block_z_offset),
                            size=small_text_size)
        
        return self.obj
    
    def _add_text_field(self, scene, camera, field_name, text, location, size=0.05):
        """Add a text object to the title block."""
        # Create text curve
        text_curve = bpy.data.curves.new(f"{scene.name}_{field_name}", 'FONT')
        text_curve.body = text
        text_curve.size = size
        text_curve.align_x = 'LEFT'
        text_curve.align_y = 'CENTER'
        
        text_obj = bpy.data.objects.new(f"{scene.name}_{field_name}", text_curve)
        scene.collection.objects.link(text_obj)
        
        # Parent to camera
        text_obj.parent = camera
        text_obj.location = location
        # Rotate to face camera (text should be in XZ plane, facing -Y)
        text_obj.rotation_euler = (math.radians(90), 0, 0)
        
        # Black material
        mat = bpy.data.materials.new(f"{scene.name}_{field_name}_Mat")
        mat.use_nodes = True
        mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0, 0, 0, 1)
        text_obj.data.materials.append(mat)
        
        self.text_objects.append(text_obj)
        return text_obj
    
    def update(self, scene: bpy.types.Scene):
        """Update title block text from scene properties."""
        for obj in self.text_objects:
            if 'view_name' in obj.name:
                obj.data.body = scene.name
            elif 'scale' in obj.name:
                scale_text = scene.get('hb_layout_scale', '1/4"=1\'')
                obj.data.body = f"Scale: {scale_text}"


class LayoutView:
    """Base class for 2D layout views."""
    
    scene: bpy.types.Scene = None
    camera: bpy.types.Object = None
    paper_size: str = 'LETTER'
    landscape: bool = True
    dpi: int = DEFAULT_DPI
    
    def __init__(self, scene=None):
        if scene:
            self.scene = scene
            # Find camera in scene
            for obj in scene.objects:
                if obj.type == 'CAMERA':
                    self.camera = obj
                    break
            # Restore paper settings from scene
            self.paper_size = scene.get('PAPER_SIZE', 'LETTER')
            self.landscape = scene.get('PAPER_LANDSCAPE', True)
            self.dpi = scene.get('PAPER_DPI', DEFAULT_DPI)
    
    @staticmethod
    def get_all_layout_views():
        """Return all scenes tagged as layout views."""
        views = []
        for scene in bpy.data.scenes:
            if scene.get('IS_LAYOUT_VIEW'):
                views.append(scene)
        return views
    
    def create_scene(self, name: str) -> bpy.types.Scene:
        """Create a new scene for the layout view."""
        self.scene = bpy.data.scenes.new(name)
        self.scene['IS_LAYOUT_VIEW'] = True
        
        # Set up render settings for layout views
        self._setup_render_settings()
        
        return self.scene
    
    def _setup_render_settings(self):
        """Configure render settings for 2D layout output."""
        if not self.scene:
            return
        
        # Use Workbench render engine
        self.scene.render.engine = 'BLENDER_WORKBENCH'
        
        # Set render samples to 32
        self.scene.display.render_aa = '32'
        
        # Set shading color type to Object
        self.scene.display.shading.color_type = 'OBJECT'
        self.scene.display.shading.light = 'FLAT'
        
        # Set shading to solid
        self.scene.display.shading.type = 'SOLID'
        
        # Enable Freestyle
        self.scene.render.use_freestyle = True
        
        # Set up Freestyle line set on the view layer
        # First, we need to get the view layer for this scene
        if self.scene.view_layers:
            view_layer = self.scene.view_layers[0]
            
            # Enable Freestyle on the view layer
            view_layer.use_freestyle = True
            
            # Create a line set if none exists
            if len(view_layer.freestyle_settings.linesets) == 0:
                view_layer.freestyle_settings.linesets.new('LineSet')
            
            # Configure the line set
            lineset = view_layer.freestyle_settings.linesets[0]
            lineset.select_silhouette = True
            lineset.select_border = True
            lineset.select_crease = True
            lineset.select_edge_mark = True
    
    def create_camera(self, name: str, location: Vector, rotation: tuple) -> bpy.types.Object:
        """Create an orthographic camera for the view."""
        cam_data = bpy.data.cameras.new(name)
        cam_data.type = 'ORTHO'
        
        self.camera = bpy.data.objects.new(name, cam_data)
        self.scene.collection.objects.link(self.camera)
        
        self.camera.location = location
        self.camera.rotation_euler = rotation
        
        # Set as active camera for scene
        self.scene.camera = self.camera
        
        return self.camera
    
    def set_camera_ortho_scale(self, scale: float):
        """Set the orthographic scale of the camera."""
        if self.camera and self.camera.data:
            self.camera.data.ortho_scale = scale
    
    def set_paper_size(self, paper_size: str = 'LETTER', landscape: bool = True, dpi: int = None):
        """Set the paper size for this layout view.
        
        Args:
            paper_size: Paper size name (LETTER, LEGAL, TABLOID, A4, A3)
            landscape: If True, use landscape orientation
            dpi: Dots per inch (uses default if None)
        """
        if dpi is None:
            dpi = self.dpi
        
        self.paper_size = paper_size
        self.landscape = landscape
        self.dpi = dpi
        
        # Store in scene for persistence
        if self.scene:
            self.scene['PAPER_SIZE'] = paper_size
            self.scene['PAPER_LANDSCAPE'] = landscape
            self.scene['PAPER_DPI'] = dpi
        
        # Set render resolution
        width_px, height_px = get_paper_resolution(paper_size, landscape, dpi)
        if self.scene:
            self.scene.render.resolution_x = width_px
            self.scene.render.resolution_y = height_px
            self.scene.render.resolution_percentage = 100
    
    def get_paper_aspect_ratio(self) -> float:
        """Get the aspect ratio (width/height) of the current paper size."""
        width_px, height_px = get_paper_resolution(self.paper_size, self.landscape, self.dpi)
        return width_px / height_px
    
    def delete(self):
        """Delete this layout view and its scene."""
        if self.scene:
            bpy.data.scenes.remove(self.scene)
            self.scene = None
            self.camera = None


class ElevationView(LayoutView):
    """Elevation view of a wall - front orthographic projection."""
    
    wall_obj: bpy.types.Object = None
    content_collection: bpy.types.Collection = None
    collection_instance: bpy.types.Object = None
    
    def __init__(self, scene=None):
        super().__init__(scene)
        if scene:
            # Find the content collection instance
            for obj in scene.objects:
                if obj.type == 'EMPTY' and obj.instance_type == 'COLLECTION':
                    self.collection_instance = obj
                    self.content_collection = obj.instance_collection
                    break
            
            # Find the source wall from scene custom property
            wall_name = scene.get('SOURCE_WALL')
            if wall_name and wall_name in bpy.data.objects:
                self.wall_obj = bpy.data.objects[wall_name]
    
    def create(self, wall_obj: bpy.types.Object, name: str = None, 
               paper_size: str = 'LETTER', landscape: bool = True) -> bpy.types.Scene:
        """
        Create an elevation view for a wall.
        
        Args:
            wall_obj: The wall object to create elevation for
            name: Optional name for the view (defaults to wall name + " Elevation")
            paper_size: Paper size (LETTER, LEGAL, TABLOID, A4, A3)
            landscape: If True, use landscape orientation
        
        Returns:
            The created scene
        """
        self.wall_obj = wall_obj
        wall = hb_types.GeoNodeWall(wall_obj)
        
        # Get wall properties
        wall_length = wall.get_input('Length')
        wall_height = wall.get_input('Height')
        wall_thickness = wall.get_input('Thickness')
        
        # Create scene
        view_name = name or f"{wall_obj.name} Elevation"
        self.create_scene(view_name)
        self.scene['IS_ELEVATION_VIEW'] = True
        self.scene['SOURCE_WALL'] = wall_obj.name
        
        # Camera rotation to face the wall (pointing in +Y direction in wall's local space)
        wall_rotation_z = wall_obj.rotation_euler.z
        camera_rotation = (math.radians(90), 0, wall_rotation_z)
        
        # Initial camera position (will be adjusted after calculating bounds)
        wall_center_local = Vector((wall_length / 2, -2, wall_height / 2))
        wall_center_world = wall_obj.matrix_world @ wall_center_local
        
        # Create camera
        self.create_camera(f"{view_name} Camera", wall_center_world, camera_rotation)
        
        # Set paper size for proper aspect ratio
        self.set_paper_size(paper_size, landscape)
        
        # Add cabinet dimensions (before fitting camera so they're included)
        self.add_cabinet_dimensions()
        
        # Calculate bounds of all objects to fit camera properly (includes dimensions)
        self._fit_camera_to_content(wall_obj)
        
        # Create collection for wall objects
        self.content_collection = bpy.data.collections.new(f"{view_name} Content")
        
        # Add wall and all its children to the collection
        self._add_object_to_collection(wall_obj, self.content_collection)
        
        # Create collection instance in the new scene
        self.collection_instance = bpy.data.objects.new(f"{view_name} Instance", None)
        self.collection_instance.empty_display_size = .01
        self.collection_instance.instance_type = 'COLLECTION'
        self.collection_instance.instance_collection = self.content_collection
        self.scene.collection.objects.link(self.collection_instance)
        
        # Add title block
        self.title_block = TitleBlock()
        self.title_block.create(self.scene, self.camera)
        
        return self.scene
    
    def _fit_camera_to_content(self, wall_obj):
        """Adjust camera position and ortho scale to fit all wall content including dimensions."""

        wall = hb_types.GeoNodeWall(wall_obj)
        wall_length = wall.get_input('Length')
        wall_height = wall.get_input('Height')
        
        # Get wall's local coordinate system
        wall_matrix = wall_obj.matrix_world
        wall_matrix_inv = wall_matrix.inverted()
        
        # Start with wall bounds in wall's local space
        min_x, max_x = 0, wall_length
        min_z, max_z = 0, wall_height
        
        # Check all children for their bounds in wall's local space
        for child in wall_obj.children_recursive:
            # Skip cages and helper objects
            is_cage = (child.get('IS_FRAMELESS_CABINET_CAGE') or 
                       child.get('IS_FRAMELESS_BAY_CAGE') or 
                       child.get('IS_FRAMELESS_OPENING_CAGE') or
                       child.get('IS_FRAMELESS_DOORS_CAGE'))
            is_helper = (child.get('obj_x') or 'Overlay Prompt Obj' in child.name)
            
            if is_cage or is_helper:
                continue
            
            # Use bounding box for mesh objects
            if hasattr(child, 'bound_box') and child.type == 'MESH':
                bbox_corners = [child.matrix_world @ Vector(corner) for corner in child.bound_box]
                bbox_local = [wall_matrix_inv @ corner for corner in bbox_corners]
                
                child_min_x = min(c.x for c in bbox_local)
                child_max_x = max(c.x for c in bbox_local)
                child_min_z = min(c.z for c in bbox_local)
                child_max_z = max(c.z for c in bbox_local)
                
                min_x = min(min_x, child_min_x)
                max_x = max(max_x, child_max_x)
                min_z = min(min_z, child_min_z)
                max_z = max(max_z, child_max_z)
        
        # Also check dimension objects in the scene
        for obj in self.scene.collection.objects:
            if obj.get('IS_2D_ANNOTATION') and obj.type == 'CURVE':
                # Get dimension position in wall local space
                dim_local_pos = wall_matrix_inv @ obj.location
                
                # Get the dimension length from the curve endpoint
                if obj.data.splines and len(obj.data.splines[0].points) > 1:
                    dim_length = obj.data.splines[0].points[1].co.x
                    
                    # Update bounds - add generous margin for arrows and text
                    min_x = min(min_x, dim_local_pos.x - 0.1)
                    max_x = max(max_x, dim_local_pos.x + dim_length + 0.1)
                    min_z = min(min_z, dim_local_pos.z - 0.25)
                    max_z = max(max_z, dim_local_pos.z + 0.25)
        
        # Calculate center and size
        center_x = (min_x + max_x) / 2
        center_z = (min_z + max_z) / 2
        
        width = max_x - min_x
        height = max_z - min_z
        
        # Add margin (10% of the larger dimension)
        margin = max(width, height) * 0.1
        width += margin * 2
        height += margin * 2
        
        # Update camera position (center on content, 3m in front)
        camera_local_pos = Vector((center_x, -3, center_z))
        camera_world_pos = wall_matrix @ camera_local_pos
        self.camera.location = camera_world_pos
        
        # Set ortho scale to fit content
        max_dimension = max(width, height)
        self.set_camera_ortho_scale(max_dimension)

    def add_cabinet_dimensions(self):
        """Add width dimensions for all cabinets on the wall."""

        if not self.wall_obj:
            return
        
        wall = hb_types.GeoNodeWall(self.wall_obj)
        wall_matrix = self.wall_obj.matrix_world
        wall_matrix_inv = wall_matrix.inverted()
        
        # Collect cabinets by type (base/tall vs upper)
        base_tall_cabinets = []
        upper_cabinets = []
        
        for child in self.wall_obj.children:
            if child.get('IS_FRAMELESS_CABINET_CAGE'):
                # Get cabinet position in wall local space
                cabinet_local_pos = wall_matrix_inv @ child.matrix_world.translation
                
                # Get cabinet dimensions from the cage
                cage = hb_types.GeoNodeCage(child)
                cabinet_width = cage.get_input('Dim X')
                cabinet_height = cage.get_input('Dim Z')
                cabinet_z = cabinet_local_pos.z
                
                cabinet_info = {
                    'obj': child,
                    'x': cabinet_local_pos.x,
                    'z': cabinet_z,
                    'width': cabinet_width,
                    'height': cabinet_height,
                }
                
                # Upper cabinets typically start above 1.2m (48")
                if cabinet_z > 1.2:
                    upper_cabinets.append(cabinet_info)
                else:
                    base_tall_cabinets.append(cabinet_info)
        
        # Sort by x position
        base_tall_cabinets.sort(key=lambda c: c['x'])
        upper_cabinets.sort(key=lambda c: c['x'])
        
        # Create dimensions for base/tall cabinets (at bottom)
        dim_z_bottom = -units.inch(4)  # Below the cabinets
        for cab in base_tall_cabinets:
            self._create_cabinet_dimension(cab, dim_z_bottom, wall_matrix, flip_text=True)
        
        # Create dimensions for upper cabinets (at top)
        if upper_cabinets:
            # Find the top of upper cabinets
            max_top = max(c['z'] + c['height'] for c in upper_cabinets)
            dim_z_top = max_top + units.inch(4)
            for cab in upper_cabinets:
                self._create_cabinet_dimension(cab, dim_z_top, wall_matrix, flip_text=False)
    
    def _create_cabinet_dimension(self, cabinet_info, dim_z, wall_matrix, flip_text=False):
        """Create a single cabinet width dimension."""

        dim = hb_types.GeoNodeDimension()
        dim.create(f"Dim_{cabinet_info['obj'].name}")
        dim.obj['IS_2D_ANNOTATION'] = True
        
        # The create method links to bpy.context.scene, but we need it in self.scene
        # Unlink from whatever scene it was added to
        for scene in bpy.data.scenes:
            if dim.obj.name in scene.collection.objects:
                scene.collection.objects.unlink(dim.obj)
        
        # Link to our elevation scene
        self.scene.collection.objects.link(dim.obj)
        
        # Position in wall local space, then convert to world
        local_pos = Vector((cabinet_info['x'], -units.inch(2), dim_z))
        dim.obj.location = wall_matrix @ local_pos
        
        # Rotation to face camera (90 degrees on X to stand up, match wall rotation on Z)
        wall_rotation_z = self.wall_obj.rotation_euler.z
        dim.obj.rotation_euler = (math.radians(90), 0, wall_rotation_z)
        
        # Set the dimension length via the curve endpoint
        dim.obj.data.splines[0].points[1].co = (cabinet_info['width'], 0, 0, 1)
        
        # Flip text if needed (for upper cabinets)
        if flip_text:
            dim.set_input('Leader Length', units.inch(-4))
        else:
            dim.set_input('Leader Length', units.inch(4))
        
        return dim

    def _add_object_to_collection(self, obj: bpy.types.Object, collection: bpy.types.Collection):
        """Recursively add object and its children to collection.
        Skips cage objects (GeoNodeCage) as they are containers, not visible geometry."""
        
        # Skip cage objects and helper empties - they are organizational, not visible geometry
        is_cage = (obj.get('IS_FRAMELESS_CABINET_CAGE') or 
                   obj.get('IS_FRAMELESS_BAY_CAGE') or 
                   obj.get('IS_FRAMELESS_OPENING_CAGE') or
                   obj.get('IS_FRAMELESS_DOORS_CAGE'))
        
        # Skip helper empties
        is_helper = (obj.get('obj_x') or 
                     'Overlay Prompt Obj' in obj.name)
        
        if not is_cage and not is_helper:
            # Link object to collection (it can be in multiple collections)
            if obj.name not in collection.objects:
                collection.objects.link(obj)
        
        # Add all children recursively (even if parent is a cage)
        for child in obj.children:
            self._add_object_to_collection(child, collection)
    
    def update(self):
        """Update the elevation view to reflect changes in the 3D model."""
        if not self.wall_obj or not self.camera:
            return
        
        wall = hb_types.GeoNodeWall(self.wall_obj)
        wall_length = wall.get_input('Length')
        wall_height = wall.get_input('Height')
        
        # Update camera position
        wall_center_local = Vector((wall_length / 2, -2, wall_height / 2))
        wall_center_world = self.wall_obj.matrix_world @ wall_center_local
        self.camera.location = wall_center_world
        
        # Update camera rotation if wall rotated
        wall_rotation_z = self.wall_obj.rotation_euler.z
        self.camera.rotation_euler = (math.radians(90), 0, wall_rotation_z)
        
        # Update ortho scale
        margin = 0.2
        max_dimension = max(wall_length, wall_height) + margin * 2
        self.set_camera_ortho_scale(max_dimension)


class PlanView(LayoutView):
    """Plan view - top-down orthographic projection."""
    
    content_collection: bpy.types.Collection = None
    collection_instance: bpy.types.Object = None
    
    def __init__(self, scene=None):
        super().__init__(scene)
        if scene:
            for obj in scene.objects:
                if obj.type == 'EMPTY' and obj.instance_type == 'COLLECTION':
                    self.collection_instance = obj
                    self.content_collection = obj.instance_collection
                    break
    
    def create(self, name: str = "Floor Plan") -> bpy.types.Scene:
        """
        Create a plan view showing all walls from above.
        
        Args:
            name: Name for the view
        
        Returns:
            The created scene
        """
        # Create scene
        self.create_scene(name)
        self.scene['IS_PLAN_VIEW'] = True
        
        # Find all walls to determine bounds
        walls = []
        min_x, max_x = float('inf'), float('-inf')
        min_y, max_y = float('inf'), float('-inf')
        
        for obj in bpy.data.objects:
            if 'IS_WALL_BP' in obj:
                walls.append(obj)
                wall = hb_types.GeoNodeWall(obj)
                wall_length = wall.get_input('Length')
                
                # Get wall start and end points in world space
                start = obj.matrix_world @ Vector((0, 0, 0))
                end = obj.matrix_world @ Vector((wall_length, 0, 0))
                
                min_x = min(min_x, start.x, end.x)
                max_x = max(max_x, start.x, end.x)
                min_y = min(min_y, start.y, end.y)
                max_y = max(max_y, start.y, end.y)
        
        if not walls:
            # No walls found, create default camera position
            center = Vector((0, 0, 5))
            size = 10
        else:
            # Calculate center and size
            center_x = (min_x + max_x) / 2
            center_y = (min_y + max_y) / 2
            center = Vector((center_x, center_y, 5))  # 5m above
            
            width = max_x - min_x
            height = max_y - min_y
            size = max(width, height) + 1  # 1m margin
        
        # Create camera looking straight down
        camera_rotation = (0, 0, 0)  # Looking down -Z
        self.create_camera(f"{name} Camera", center, camera_rotation)
        self.set_camera_ortho_scale(size)
        
        # Create collection for all walls and their children
        self.content_collection = bpy.data.collections.new(f"{name} Content")
        
        for wall_obj in walls:
            self._add_object_to_collection(wall_obj, self.content_collection)
        
        # Create collection instance
        self.collection_instance = bpy.data.objects.new(f"{name} Instance", None)
        self.collection_instance.empty_display_size = .01
        self.collection_instance.instance_type = 'COLLECTION'
        self.collection_instance.instance_collection = self.content_collection
        self.scene.collection.objects.link(self.collection_instance)
        
        # Add title block
        self.title_block = TitleBlock()
        self.title_block.create(self.scene, self.camera)
        
        return self.scene
    
    def _fit_camera_to_content(self, wall_obj):
        """Adjust camera position and ortho scale to fit all wall content."""

        wall = hb_types.GeoNodeWall(wall_obj)
        wall_length = wall.get_input('Length')
        wall_height = wall.get_input('Height')
        
        # Get wall's local coordinate system
        wall_matrix = wall_obj.matrix_world
        wall_matrix_inv = wall_matrix.inverted()
        
        # Start with wall bounds in wall's local space
        min_x, max_x = 0, wall_length
        min_z, max_z = 0, wall_height
        
        # Check all children for their bounds in wall's local space
        for child in wall_obj.children_recursive:
            # Skip cages and helper objects
            is_cage = (child.get('IS_FRAMELESS_CABINET_CAGE') or 
                       child.get('IS_FRAMELESS_BAY_CAGE') or 
                       child.get('IS_FRAMELESS_OPENING_CAGE') or
                       child.get('IS_FRAMELESS_DOORS_CAGE'))
            is_helper = (child.get('obj_x') or 'Overlay Prompt Obj' in child.name)
            
            if is_cage or is_helper:
                continue
            
            # Get child's world position and convert to wall's local space
            child_world_pos = child.matrix_world.translation
            child_local_pos = wall_matrix_inv @ child_world_pos
            
            # Get child dimensions if it's a geo node object
            child_width = 0
            child_height = 0
            if hasattr(child, 'home_builder') and child.home_builder.mod_name:
                try:
                    geo_obj = hb_types.GeoNodeObject(child)
                    child_width = geo_obj.get_input('Dim X') if 'Dim X' in [i.name for i in geo_obj.obj.modifiers[geo_obj.obj.home_builder.mod_name].node_group.interface.items_tree] else 0
                    child_height = geo_obj.get_input('Dim Z') if 'Dim Z' in [i.name for i in geo_obj.obj.modifiers[geo_obj.obj.home_builder.mod_name].node_group.interface.items_tree] else 0
                except:
                    pass
            
            # Update bounds
            min_x = min(min_x, child_local_pos.x)
            max_x = max(max_x, child_local_pos.x + child_width)
            min_z = min(min_z, child_local_pos.z)
            max_z = max(max_z, child_local_pos.z + child_height)
        
        # Calculate center and size
        center_x = (min_x + max_x) / 2
        center_z = (min_z + max_z) / 2
        
        width = max_x - min_x
        height = max_z - min_z
        
        # Add margin
        margin = 0.3  # 30cm margin
        width += margin * 2
        height += margin * 2
        
        # Update camera position (center on content)
        camera_local_pos = Vector((center_x, -2, center_z))
        camera_world_pos = wall_matrix @ camera_local_pos
        self.camera.location = camera_world_pos
        
        # Set ortho scale to fit content
        max_dimension = max(width, height)
        self.set_camera_ortho_scale(max_dimension)

    def _add_object_to_collection(self, obj: bpy.types.Object, collection: bpy.types.Collection):
        """Recursively add object and its children to collection.
        Skips cage objects (GeoNodeCage) as they are containers, not visible geometry."""
        
        # Skip cage objects and helper empties - they are organizational, not visible geometry
        is_cage = (obj.get('IS_FRAMELESS_CABINET_CAGE') or 
                   obj.get('IS_FRAMELESS_BAY_CAGE') or 
                   obj.get('IS_FRAMELESS_OPENING_CAGE') or
                   obj.get('IS_FRAMELESS_DOORS_CAGE'))
        
        # Skip helper empties
        is_helper = (obj.get('obj_x') or 
                     'Overlay Prompt Obj' in obj.name)
        
        if not is_cage and not is_helper:
            if obj.name not in collection.objects:
                collection.objects.link(obj)
        
        for child in obj.children:
            self._add_object_to_collection(child, collection)


class View3D(LayoutView):
    """3D perspective or isometric view."""
    
    content_collection: bpy.types.Collection = None
    collection_instance: bpy.types.Object = None
    
    def create(self, name: str = "3D View", perspective: bool = True) -> bpy.types.Scene:
        """
        Create a 3D view.
        
        Args:
            name: Name for the view
            perspective: True for perspective, False for isometric
        
        Returns:
            The created scene
        """
        self.create_scene(name)
        self.scene['IS_3D_VIEW'] = True
        
        # Find bounds of all walls
        walls = [obj for obj in bpy.data.objects if 'IS_WALL_BP' in obj]
        
        if walls:
            # Calculate center
            centers = []
            for wall_obj in walls:
                wall = hb_types.GeoNodeWall(wall_obj)
                wall_length = wall.get_input('Length')
                center = wall_obj.matrix_world @ Vector((wall_length / 2, 0, 0))
                centers.append(center)
            
            avg_center = sum(centers, Vector()) / len(centers)
            
            # Position camera at 45° angle
            distance = 8
            camera_pos = avg_center + Vector((distance, -distance, distance))
        else:
            camera_pos = Vector((8, -8, 8))
            avg_center = Vector((0, 0, 0))
        
        # Create camera
        cam_data = bpy.data.cameras.new(f"{name} Camera")
        if perspective:
            cam_data.type = 'PERSP'
            cam_data.lens = 35
        else:
            cam_data.type = 'ORTHO'
            cam_data.ortho_scale = 10
        
        self.camera = bpy.data.objects.new(f"{name} Camera", cam_data)
        self.scene.collection.objects.link(self.camera)
        self.camera.location = camera_pos
        
        # Point camera at center
        direction = avg_center - camera_pos
        rot_quat = direction.to_track_quat('-Z', 'Y')
        self.camera.rotation_euler = rot_quat.to_euler()
        
        self.scene.camera = self.camera
        
        # Create collection for all objects
        self.content_collection = bpy.data.collections.new(f"{name} Content")
        
        for wall_obj in walls:
            self._add_object_to_collection(wall_obj, self.content_collection)
        
        # Create collection instance
        self.collection_instance = bpy.data.objects.new(f"{name} Instance", None)
        self.collection_instance.empty_display_size = .01
        self.collection_instance.instance_type = 'COLLECTION'
        self.collection_instance.instance_collection = self.content_collection
        self.scene.collection.objects.link(self.collection_instance)
        
        # Add title block
        self.title_block = TitleBlock()
        self.title_block.create(self.scene, self.camera)
        
        return self.scene
    
    def _fit_camera_to_content(self, wall_obj):
        """Adjust camera position and ortho scale to fit all wall content."""

        wall = hb_types.GeoNodeWall(wall_obj)
        wall_length = wall.get_input('Length')
        wall_height = wall.get_input('Height')
        
        # Get wall's local coordinate system
        wall_matrix = wall_obj.matrix_world
        wall_matrix_inv = wall_matrix.inverted()
        
        # Start with wall bounds in wall's local space
        min_x, max_x = 0, wall_length
        min_z, max_z = 0, wall_height
        
        # Check all children for their bounds in wall's local space
        for child in wall_obj.children_recursive:
            # Skip cages and helper objects
            is_cage = (child.get('IS_FRAMELESS_CABINET_CAGE') or 
                       child.get('IS_FRAMELESS_BAY_CAGE') or 
                       child.get('IS_FRAMELESS_OPENING_CAGE') or
                       child.get('IS_FRAMELESS_DOORS_CAGE'))
            is_helper = (child.get('obj_x') or 'Overlay Prompt Obj' in child.name)
            
            if is_cage or is_helper:
                continue
            
            # Get child's world position and convert to wall's local space
            child_world_pos = child.matrix_world.translation
            child_local_pos = wall_matrix_inv @ child_world_pos
            
            # Get child dimensions if it's a geo node object
            child_width = 0
            child_height = 0
            if hasattr(child, 'home_builder') and child.home_builder.mod_name:
                try:
                    geo_obj = hb_types.GeoNodeObject(child)
                    child_width = geo_obj.get_input('Dim X') if 'Dim X' in [i.name for i in geo_obj.obj.modifiers[geo_obj.obj.home_builder.mod_name].node_group.interface.items_tree] else 0
                    child_height = geo_obj.get_input('Dim Z') if 'Dim Z' in [i.name for i in geo_obj.obj.modifiers[geo_obj.obj.home_builder.mod_name].node_group.interface.items_tree] else 0
                except:
                    pass
            
            # Update bounds
            min_x = min(min_x, child_local_pos.x)
            max_x = max(max_x, child_local_pos.x + child_width)
            min_z = min(min_z, child_local_pos.z)
            max_z = max(max_z, child_local_pos.z + child_height)
        
        # Calculate center and size
        center_x = (min_x + max_x) / 2
        center_z = (min_z + max_z) / 2
        
        width = max_x - min_x
        height = max_z - min_z
        
        # Add margin
        margin = 0.3  # 30cm margin
        width += margin * 2
        height += margin * 2
        
        # Update camera position (center on content)
        camera_local_pos = Vector((center_x, -2, center_z))
        camera_world_pos = wall_matrix @ camera_local_pos
        self.camera.location = camera_world_pos
        
        # Set ortho scale to fit content
        max_dimension = max(width, height)
        self.set_camera_ortho_scale(max_dimension)

    def _add_object_to_collection(self, obj: bpy.types.Object, collection: bpy.types.Collection):
        """Recursively add object and its children to collection.
        Skips cage objects (GeoNodeCage) as they are containers, not visible geometry."""
        
        # Skip cage objects and helper empties - they are organizational, not visible geometry
        is_cage = (obj.get('IS_FRAMELESS_CABINET_CAGE') or 
                   obj.get('IS_FRAMELESS_BAY_CAGE') or 
                   obj.get('IS_FRAMELESS_OPENING_CAGE') or
                   obj.get('IS_FRAMELESS_DOORS_CAGE'))
        
        # Skip helper empties
        is_helper = (obj.get('obj_x') or 
                     'Overlay Prompt Obj' in obj.name)
        
        if not is_cage and not is_helper:
            if obj.name not in collection.objects:
                collection.objects.link(obj)
        
        for child in obj.children:
            self._add_object_to_collection(child, collection)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_layout_view_from_scene(scene: bpy.types.Scene) -> LayoutView:
    """Get the appropriate LayoutView subclass for a scene."""
    if not scene.get('IS_LAYOUT_VIEW'):
        return None
    
    if scene.get('IS_ELEVATION_VIEW'):
        return ElevationView(scene)
    elif scene.get('IS_PLAN_VIEW'):
        return PlanView(scene)
    elif scene.get('IS_3D_VIEW'):
        return View3D(scene)
    else:
        return LayoutView(scene)


def create_elevation_for_wall(wall_obj: bpy.types.Object) -> ElevationView:
    """Convenience function to create an elevation view for a wall."""
    view = ElevationView()
    view.create(wall_obj)
    return view


def create_plan_view() -> PlanView:
    """Convenience function to create a plan view."""
    view = PlanView()
    view.create()
    return view


def create_3d_view(perspective: bool = True) -> View3D:
    """Convenience function to create a 3D view."""
    view = View3D()
    view.create(perspective=perspective)
    return view


def create_all_elevations() -> list:
    """Create elevation views for all walls in the scene."""
    views = []
    for obj in bpy.data.objects:
        if 'IS_WALL_BP' in obj:
            view = create_elevation_for_wall(obj)
            views.append(view)
    return views
