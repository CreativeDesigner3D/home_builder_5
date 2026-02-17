import bpy
from . import hb_props
from . import hb_project
from . import hb_props_obstacles
from . import ops
from .ui import view3d_sidebar
from .ui import menu_apend
from .ui import menus
from .operators import walls
from .operators import doors_windows
from .operators import layouts
from .operators import rooms
from .operators import details
from .operators import ops_obstacles
from .product_libraries import closets
from .product_libraries import face_frame
from .product_libraries import frameless
from . import hb_layouts
from . import hb_assets

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
def load_file_post(scene):
    """ Load Default Drivers and ensure project data exists
    """
    import inspect
    from . import hb_driver_functions
    from . import hb_project
    
    # Load driver functions
    for name, obj in inspect.getmembers(hb_driver_functions):
        if name not in bpy.app.driver_namespace:
            bpy.app.driver_namespace[name] = obj
    
    # Ensure a main scene is tagged for project data
    main_scene = hb_project.ensure_main_scene()

    # Ensure a default frameless style is created
    main_scene.hb_frameless.ensure_default_style()


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
                                   default=(0.000000,0.500000,0.700000,0.100000),
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

    # Layout view defaults
    default_paper_size: bpy.props.EnumProperty(
        name="Default Paper Size",
        description="Default paper size for new layout views",
        items=[
            ('LETTER', 'Letter (8.5" x 11")', ''),
            ('LEGAL', 'Legal (8.5" x 14")', ''),
            ('TABLOID', 'Tabloid (11" x 17")', ''),
            ('A4', 'A4 (210 x 297mm)', ''),
            ('A3', 'A3 (297 x 420mm)', ''),
        ],
        default='LEGAL'
    )# type: ignore

    default_layout_scale: bpy.props.EnumProperty(
        name="Default Scale",
        description="Default drawing scale for new layout views",
        items=[
            ('3"=1\'', '3" = 1\'', 'Very detailed - 1:4'),
            ('1-1/2"=1\'', '1-1/2" = 1\'', '1:8'),
            ('1"=1\'', '1" = 1\'', '1:12'),
            ('3/4"=1\'', '3/4" = 1\'', '1:16'),
            ('1/2"=1\'', '1/2" = 1\'', '1:24'),
            ('3/8"=1\'', '3/8" = 1\'', '1:32'),
            ('1/4"=1\'', '1/4" = 1\'', '1:48 - Common for elevations'),
            ('3/16"=1\'', '3/16" = 1\'', '1:64'),
            ('1/8"=1\'', '1/8" = 1\'', '1:96 - Common for floor plans'),
            ('1/16"=1\'', '1/16" = 1\'', '1:192'),
        ],
        default='1/4"=1\''
    )# type: ignore

    default_paper_landscape: bpy.props.BoolProperty(
        name="Default Landscape",
        description="Default orientation for new layout views",
        default=True
    )# type: ignore

    asset_libraries: bpy.props.CollectionProperty(
		type=hb_assets.HB_AssetLibraryEntry,
	)# type: ignore

    asset_libraries_index: bpy.props.IntProperty(
		name="Active Library Index",
		default=0,
	)# type: ignore

    def draw(self, context):
        layout = self.layout
        
        # Layout view defaults
        box = layout.box()
        box.label(text="Layout View Defaults", icon='RENDERLAYERS')
        col = box.column(align=True)
        col.prop(self, "default_paper_size")
        col.prop(self, "default_layout_scale")
        col.prop(self, "default_paper_landscape")
        
        layout.separator()
        
        box = layout.box()
        box.label(text="Asset Libraries", icon='ASSET_MANAGER')
        row = box.row()
        row.template_list("HB_UL_asset_libraries", "", self, "asset_libraries", self, "asset_libraries_index", rows=3)
        col = row.column(align=True)
        col.operator("home_builder.add_asset_library", text="", icon='ADD')
        col.operator("home_builder.remove_asset_library", text="", icon='REMOVE')
        col.separator()
        col.operator("home_builder.refresh_asset_libraries", text="", icon='FILE_REFRESH')
        layout.prop(self, "wall_color")
        layout.prop(self, "cabinet_color")
        layout.prop(self, "door_window_color")
        layout.prop(self, "annotation_color")
        layout.prop(self, "annotation_highlight_color")
        layout.prop(self, "obstacle_color")              

def register():
    hb_assets.register()
    bpy.utils.register_class(Home_Builder_AddonPreferences)

    hb_props.register()
    hb_project.register()
    hb_props_obstacles.register()
    ops_obstacles.register()
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

    hb_assets.ensure_asset_libraries()

    bpy.app.handlers.load_post.append(load_file_post)

    # Load driver functions on first enable
    import inspect
    from . import hb_driver_functions
    for name, obj in inspect.getmembers(hb_driver_functions):
        if name not in bpy.app.driver_namespace:
            bpy.app.driver_namespace[name] = obj

def unregister():
    bpy.utils.unregister_class(Home_Builder_AddonPreferences)

    hb_props.unregister()
    hb_project.unregister()
    hb_props_obstacles.unregister()
    ops_obstacles.unregister()
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
    hb_assets.unregister()

    bpy.app.handlers.load_post.remove(load_file_post)

if __name__ == '__main__':
    register()    