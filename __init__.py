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
from .operators import export
from .operators import ops_stairs
from .operators import scene_navigator
from .operators import room_palette
from .operators import measure_tool
from .operators import library_panel
from .operators import options_panel
from .operators import layout_lock
from .operators import viewport_hud
from .operators import room_dim_overlay
from .operators import ops_general
from .operators import ops_surfaces
from .operators import ops_room_dressing
from .product_libraries import closets
from .product_libraries import face_frame
from .product_libraries import frameless
from .product_libraries.common import wood_hoods
from .product_libraries.common import door_window_geo
from .product_libraries.common import appliance_geo
from . import molding
# Catalog browser - intentionally disabled. The package lives at
# home_builder_5/catalog/ for future revisit. Re-enable by uncommenting
# the import here plus the register()/unregister() calls below.
# from . import catalog
from . import hb_layouts
from . import hb_assets
from . import hb_snap_engine

from bpy.app.handlers import persistent

bl_info = {
    "name": "Home Builder 5",
    "author": "Andrew Peel",
    "version": (5, 1, 71),
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

    # Modal operators do not survive a .blend load -- re-arm the HUD listener.
    from .operators import viewport_hud
    viewport_hud.ensure_listener()

    # Door/window boolean cutters saved while still visible in the
    # viewport would cover their own opening in rendered shading.
    from .product_libraries.common import door_window_geo
    door_window_geo.hide_reveal_cutters()


def _update_use_viewport_hud(self, context):
    """Flipping the HUD preference: redraw every 3D viewport so the change
    shows immediately in both the viewport and the sidebar."""
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()


def _apply_sidebar_tab_first():
    """Sync the tab-pin panel with the preference. Safe to call from
    register(); from a property update it must be deferred (see below)."""
    try:
        prefs = bpy.context.preferences.addons[__package__].preferences
        enabled = bool(prefs.sidebar_tab_first)
    except (KeyError, AttributeError):
        enabled = False
    view3d_sidebar.apply_tab_pin(enabled)


def _update_sidebar_tab_first(self, context):
    """Panel (un)registration can't happen inside a property update, so
    defer it onto a one-shot timer, then redraw the 3D viewports."""
    def _apply():
        try:
            _apply_sidebar_tab_first()
        except Exception as e:
            print(f"Home Builder: sidebar tab pin toggle skipped: {e}")
        _update_use_viewport_hud(None, None)
        return None
    bpy.app.timers.register(_apply, first_interval=0.0)


class Home_Builder_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    sidebar_tab_first: bpy.props.BoolProperty(
        name="Keep Sidebar Tab First",
        description="Always list the Home Builder tab first in the 3D "
                    "viewport sidebar. When off, Blender orders it with "
                    "the other add-on tabs",
        default=False,
        update=_update_sidebar_tab_first,
    ) # type: ignore

    use_viewport_hud: bpy.props.BoolProperty(
        name="Viewport Controls",
        description="Draw the scene navigator and selection mode controls "
                    "in the 3D viewport instead of the sidebar",
        default=False,
        update=_update_use_viewport_hud,
    ) # type: ignore

    use_room_palette: bpy.props.BoolProperty(
        name="Room Tool Palette",
        description="Show the room tools - draw walls, hang doors and "
                    "windows, add a floor or ceiling - as a glyph strip "
                    "in the 3D viewport. The sidebar buttons keep working "
                    "either way",
        default=True,
        update=_update_use_viewport_hud,
    ) # type: ignore

    palette_expanded: bpy.props.BoolProperty(
        name="Expanded Tool Bar",
        description="Name every tool, head each group with a caption, and "
                    "give a tool's settings a row of their own instead of "
                    "a small corner. Costs viewport width, and is worth it "
                    "while the marks are still unfamiliar",
        default=False,
        update=_update_use_viewport_hud,
    ) # type: ignore

    hide_2d_drawing_panels: bpy.props.BoolProperty(
        name="Hide 2D Drawing Panels",
        description="Hide the Layout Views, 2D Details, and Annotations ",
        default=False,
    ) # type: ignore

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
    line_engine: bpy.props.EnumProperty(
        name="2D Line Engine",
        description="How newly generated 2D layout views draw their line work",
        items=[
            ('FREESTYLE', 'Freestyle',
             'Classic Freestyle lines. Only visible in the final render'),
            ('LINEART', 'Grease Pencil Line Art',
             'Grease Pencil Line Art strokes. Visible live in the viewport '
             'and much faster to render'),
            ('SEMANTIC', 'Vector Edges (Experimental)',
             'Export-time vector line generation from the model\'s own edges. '
             'Views render with Freestyle until an exporter consumes the '
             'vector line data'),
        ],
        default='FREESTYLE'
    )# type: ignore

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
            ('1:1', '1:1', 'Full size'),
            ('1:5', '1:5', 'Detail drawings'),
            ('1:10', '1:10', 'Detail drawings'),
            ('1:20', '1:20', 'Sections and elevations'),
            ('1:25', '1:25', 'Sections and elevations'),
            ('1:50', '1:50', 'Common for floor plans'),
            ('1:100', '1:100', 'Floor plans and site plans'),
            ('1:200', '1:200', 'Site plans'),
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

        layout.prop(self, "sidebar_tab_first")
        layout.prop(self, "hide_2d_drawing_panels")

        # Viewport interface. Every one of these is off by default:
        # they add controls painted into the 3D viewport, and the
        # sidebar keeps working exactly the same either way.
        box = layout.box()
        box.label(text="Viewport Interface", icon='WINDOW')
        col = box.column(align=True)
        col.prop(self, "use_viewport_hud")
        col.prop(self, "use_room_palette")
        sub = col.column(align=True)
        sub.enabled = self.use_room_palette
        sub.prop(self, "palette_expanded")
        
        # Layout view defaults
        box = layout.box()
        box.label(text="Layout View Defaults", icon='RENDERLAYERS')
        col = box.column(align=True)
        col.prop(self, "line_engine")
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

        box = layout.box()
        box.label(text="Cabinet Pull Libraries", icon='TOOL_SETTINGS')
        row = box.row(align=True)
        row.operator("hb_face_frame.install_pull_library",
                     text="Install Pull Library...", icon='IMPORT')
        row.operator("hb_face_frame.open_pull_library_folder",
                     text="", icon='FILE_FOLDER')
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
    hb_snap_engine.register()
    hb_props_obstacles.register()
    ops_obstacles.register()
    walls.register()
    layouts.register()
    rooms.register()
    details.register()
    doors_windows.register()
    export.register()
    ops_stairs.register()
    layout_lock.register()
    scene_navigator.register()
    viewport_hud.register()
    room_palette.register()
    measure_tool.register()      # after the palette: it fills its registries
    ops_room_dressing.register()  # same: registers the lights option form
    library_panel.register()
    options_panel.register()
    room_dim_overlay.register()
    ops_general.register()
    ops_surfaces.register()
    ops.register()
    view3d_sidebar.register()
    try:
        _apply_sidebar_tab_first()
    except Exception as e:
        print(f"Home Builder: sidebar tab pin init skipped: {e}")
    menu_apend.register()
    menus.register()
    closets.register()
    face_frame.register()
    frameless.register()
    wood_hoods.register()
    door_window_geo.register()
    appliance_geo.register()
    molding.register()
    # catalog.register()

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
    hb_snap_engine.unregister()
    hb_props_obstacles.unregister()
    ops_obstacles.unregister()
    walls.unregister()
    layouts.unregister()
    rooms.unregister()
    details.unregister()
    doors_windows.unregister()
    export.unregister()
    options_panel.unregister()
    library_panel.unregister()
    ops_room_dressing.unregister()
    measure_tool.unregister()    # before the palette, to empty its registries
    room_palette.unregister()
    scene_navigator.unregister()
    viewport_hud.unregister()
    layout_lock.unregister()
    room_dim_overlay.unregister()
    ops_stairs.unregister()
    ops_surfaces.unregister()
    ops_general.unregister()
    ops.unregister()
    view3d_sidebar.unregister()
    menu_apend.unregister()
    menus.unregister()
    # catalog.unregister()
    closets.unregister()
    molding.unregister()
    appliance_geo.unregister()
    door_window_geo.unregister()
    wood_hoods.unregister()
    face_frame.unregister()
    frameless.unregister()
    hb_assets.unregister()

    bpy.app.handlers.load_post.remove(load_file_post)

if __name__ == '__main__':
    register()    