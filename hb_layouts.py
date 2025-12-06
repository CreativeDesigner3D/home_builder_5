import bpy
import math
from mathutils import Vector
from . import hb_types
from . import units

# =============================================================================
# LAYOUT VIEW SYSTEM
# =============================================================================

class LayoutView:
    """Base class for 2D layout views."""
    
    scene: bpy.types.Scene = None
    camera: bpy.types.Object = None
    
    def __init__(self, scene=None):
        if scene:
            self.scene = scene
            # Find camera in scene
            for obj in scene.objects:
                if obj.type == 'CAMERA':
                    self.camera = obj
                    break
    
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
        return self.scene
    
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
    
    def create(self, wall_obj: bpy.types.Object, name: str = None) -> bpy.types.Scene:
        """
        Create an elevation view for a wall.
        
        Args:
            wall_obj: The wall object to create elevation for
            name: Optional name for the view (defaults to wall name + " Elevation")
        
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
        
        # Calculate camera position
        # Camera should be centered on wall, positioned in front
        wall_center_local = Vector((wall_length / 2, -2, wall_height / 2))  # 2m in front of wall
        wall_center_world = wall_obj.matrix_world @ wall_center_local
        
        # Camera rotation to face the wall (pointing in +Y direction in wall's local space)
        # Wall's local +Y is into the wall, so camera looks in -Y (which is wall's front)
        wall_rotation_z = wall_obj.rotation_euler.z
        camera_rotation = (math.radians(90), 0, wall_rotation_z)
        
        # Create camera
        self.create_camera(f"{view_name} Camera", wall_center_world, camera_rotation)
        
        # Set ortho scale to fit wall with some margin
        margin = 0.2  # 20cm margin
        max_dimension = max(wall_length, wall_height) + margin * 2
        self.set_camera_ortho_scale(max_dimension)
        
        # Create collection for wall objects
        self.content_collection = bpy.data.collections.new(f"{view_name} Content")
        
        # Add wall and all its children to the collection
        self._add_object_to_collection(wall_obj, self.content_collection)
        
        # Create collection instance in the new scene
        self.collection_instance = bpy.data.objects.new(f"{view_name} Instance", None)
        self.collection_instance.instance_type = 'COLLECTION'
        self.collection_instance.instance_collection = self.content_collection
        self.scene.collection.objects.link(self.collection_instance)
        
        return self.scene
    
    def _add_object_to_collection(self, obj: bpy.types.Object, collection: bpy.types.Collection):
        """Recursively add object and its children to collection."""
        # Link object to collection (it can be in multiple collections)
        if obj.name not in collection.objects:
            collection.objects.link(obj)
        
        # Add all children recursively
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
        self.collection_instance.instance_type = 'COLLECTION'
        self.collection_instance.instance_collection = self.content_collection
        self.scene.collection.objects.link(self.collection_instance)
        
        return self.scene
    
    def _add_object_to_collection(self, obj: bpy.types.Object, collection: bpy.types.Collection):
        """Recursively add object and its children to collection."""
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
        self.collection_instance.instance_type = 'COLLECTION'
        self.collection_instance.instance_collection = self.content_collection
        self.scene.collection.objects.link(self.collection_instance)
        
        return self.scene
    
    def _add_object_to_collection(self, obj: bpy.types.Object, collection: bpy.types.Collection):
        """Recursively add object and its children to collection."""
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
