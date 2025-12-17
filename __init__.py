import bpy
from . import hb_props
from . import ops
from .ui import view3d_sidebar
from .ui import menu_apend
from .ui import menus
from .operators import walls
from .operators import doors_windows
from .operators import layouts
from .operators import rooms
from .operators import details
from .product_libraries import closets
from .product_libraries import face_frame
from .product_libraries import frameless
from .product_libraries import obstacles
from . import hb_layouts

from bpy.app.handlers import persistent

bl_info = {
    "name": "Home Builder 5",
    "author": "Andrew Peel",
    "version": (1, 0, 0),
    "blender": (5, 0, 0),
    "location": "3D Viewport Sidebar",
    "description": "Library for Designing Interior Spaces",
    "warning": "",
    "wiki_url": "",
    "category": "Asset Library",
}

@persistent
def load_driver_functions(scene):
    """ Load Default Drivers
    """
    import inspect
    from . import hb_driver_functions
    for name, obj in inspect.getmembers(hb_driver_functions):
        if name not in bpy.app.driver_namespace:
            bpy.app.driver_namespace[name] = obj
    # for obj in bpy.data.objects:
    #     if obj.type in {'EMPTY','MESH'}:
    #         drivers = []
    #         if obj.animation_data:
    #             for driver in obj.animation_data.drivers:
    #                 drivers.append(driver)

    #         if obj.data and hasattr(obj.data,'animation_data') and obj.data.animation_data:
    #             for driver in obj.data.animation_data.drivers:
    #                 drivers.append(driver)

    #         if hasattr(obj.data,'shape_keys'):
    #             if obj.data and obj.data.shape_keys and obj.data.shape_keys.animation_data:
    #                 for driver in obj.data.shape_keys.animation_data.drivers:
    #                     drivers.append(driver)
     
    #         for DR in drivers:  
    #             DR.driver.expression = DR.driver.expression

class Home_Builder_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    wall_color: bpy.props.FloatVectorProperty(name="Wall Color",
                                   description="The color of walls",
                                   size=4,
                                   min=0,
                                   max=1,
                                   default=(0.252832,0.500434,0.735662,1.000000),
                                   subtype="COLOR") # type: ignore

    cabinet_color: bpy.props.FloatVectorProperty(name="Cabinet Color",
                                   description="The color of cabinets",
                                   size=4,
                                   min=0,
                                   max=1,
                                   default=(0.000000,0.500000,0.700000,0.300000),
                                   subtype="COLOR") # type: ignore    
    
    door_window_color: bpy.props.FloatVectorProperty(name="Door Window Color",
                                   description="The color of doors and windows",
                                   size=4,
                                   min=0,
                                   max=1,
                                   default=(0.000000,0.500000,0.700000,0.300000),
                                   subtype="COLOR") # type: ignore  
                                   
    annotation_color: bpy.props.FloatVectorProperty(name="Text Color",
                                description="The color of text",
                                size=4,
                                min=0,
                                max=1,
                                default=(0.000000, 0.000000, 0.000000, 1.000000),
                                subtype="COLOR") # type: ignore    
    
    annotation_highlight_color: bpy.props.FloatVectorProperty(name="Text Highlight Color",
                            description="The color of text when highlighted",
                            size=4,
                            min=0,
                            max=1,
                            default=(1.000000, 1.000000, 0.000000, 1.000000),
                            subtype="COLOR") # type: ignore  
    
    obstacle_color: bpy.props.FloatVectorProperty(name="Obstacle Color",
                            description="The default color of obstacles",
                            size=4,
                            min=0,
                            max=1,
                            default=(0.900000, 0.700000, 0.400000, 0.800000),
                            subtype="COLOR") # type: ignore  
    
    designer_name: bpy.props.StringProperty(
		name="Designer name",
        description="Enter the designer name you want to have appear on reports"
	)# type: ignore

    user_decoration_path: bpy.props.StringProperty(
		name="User Decoration Path",
		subtype='DIR_PATH',
	)# type: ignore

    user_material_path: bpy.props.StringProperty(
		name="User Material Path",
		subtype='DIR_PATH',
	)# type: ignore

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "user_decoration_path")
        layout.prop(self, "user_material_path")
        layout.prop(self, "wall_color")
        layout.prop(self, "cabinet_color")
        layout.prop(self, "door_window_color")
        layout.prop(self, "annotation_color")
        layout.prop(self, "annotation_highlight_color")
        layout.prop(self, "obstacle_color")              

def register():
    bpy.utils.register_class(Home_Builder_AddonPreferences)

    hb_props.register()
    walls.register()
    layouts.register()
    rooms.register()
    details.register()
    doors_windows.register()
    ops.register()
    view3d_sidebar.register()
    menu_apend.register()
    menus.register()
    closets.register()
    face_frame.register()
    frameless.register()
    obstacles.register()

    bpy.app.handlers.load_post.append(load_driver_functions)

def unregister():
    bpy.utils.unregister_class(Home_Builder_AddonPreferences)

    hb_props.unregister()
    walls.unregister()
    layouts.unregister()
    rooms.unregister()
    details.unregister()
    doors_windows.unregister()
    ops.unregister()
    view3d_sidebar.unregister()
    menu_apend.unregister()
    menus.unregister()
    closets.unregister()
    face_frame.unregister()
    frameless.unregister()
    obstacles.unregister()

    bpy.app.handlers.load_post.remove(load_driver_functions)

if __name__ == '__main__':
    register()    