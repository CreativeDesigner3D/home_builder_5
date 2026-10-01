# O hot-reload precisa ocorrer antes das importações dos submódulos.
# ruff: noqa: E402
import sys
import importlib
import bpy  # type: ignore
from bpy.app.handlers import persistent  # type: ignore

# Hot-reload submodules during active development
_submodule_names = [
    "compat", "data", "standards", "geometry", "cutting", "ui", "overlays",
    "hb_props", "hb_project", "hb_props_obstacles", "ops",
    "view3d_sidebar", "menu_apend", "menus",
    "walls", "doors_windows", "layouts", "rooms", "details",
    "ops_obstacles", "export", "ops_stairs", "scene_navigator",
    "viewport_hud", "ops_general", "closets", "face_frame",
    "frameless", "wood_hoods", "molding", "hb_layouts", "hb_assets"
]
for _mod_name in _submodule_names:
    _full_name = f"{__name__}.{_mod_name}"
    if _full_name in sys.modules:
        importlib.reload(sys.modules[_full_name])

# Import modern modules
from . import compat as compat
from . import data
from . import standards
from . import geometry as geometry
from . import cutting as cutting
from . import ui
from . import overlays
from . import operators as btm_operators

# Import legacy modules
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
from .operators import viewport_hud
from .operators import ops_general
from .product_libraries import closets
from .product_libraries import face_frame
from .product_libraries import frameless
from .product_libraries.common import wood_hoods
from . import molding
from . import hb_layouts as hb_layouts
from . import hb_assets


@persistent
def load_file_post(scene):
    """ Load Default Drivers and ensure project data exists """
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
    if main_scene and hasattr(main_scene, "hb_frameless"):
        main_scene.hb_frameless.ensure_default_style()

    # Padrão de Dimensões: definições embutidas e migrações M-01/M-02 (uma vez por arquivo).
    standards.migration.run(main_scene)

    # Modal operators do not survive a .blend load -- re-arm the HUD listener.
    from .operators import viewport_hud
    viewport_hud.ensure_listener()


def _update_use_viewport_hud(self, context):
    """Flipping the HUD preference: redraw every 3D viewport so the change shows immediately."""
    if bpy.context.window_manager:
        for window in bpy.context.window_manager.windows:
            if window.screen:
                for area in window.screen.areas:
                    if area.type == 'VIEW_3D':
                        area.tag_redraw()


class BTM_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__ or __name__

    use_viewport_hud: bpy.props.BoolProperty(
        name="Controles na Viewport",
        description="Desenhar os atalhos de navegação e modos de seleção diretamente na Viewport 3D",
        default=False,
        update=_update_use_viewport_hud,
    )  # type: ignore

    hide_2d_drawing_panels: bpy.props.BoolProperty(
        name="Ocultar Painéis 2D",
        description="Ocultar as abas de Views 2D, Detalhes e Anotações na barra lateral",
        default=False,
    )  # type: ignore

    wall_color: bpy.props.FloatVectorProperty(name="Cor das Paredes", size=4, min=0, max=1, default=(0.252832, 0.500434, 0.735662, 1.0), subtype="COLOR")  # type: ignore
    cabinet_color: bpy.props.FloatVectorProperty(name="Cor dos Armários", size=4, min=0, max=1, default=(0.0, 0.5, 0.7, 0.3), subtype="COLOR")  # type: ignore
    door_window_color: bpy.props.FloatVectorProperty(name="Cor de Portas/Janelas", size=4, min=0, max=1, default=(0.0, 0.5, 0.7, 0.1), subtype="COLOR")  # type: ignore
    annotation_color: bpy.props.FloatVectorProperty(name="Cor dos Textos", size=4, min=0, max=1, default=(0.0, 0.0, 0.0, 1.0), subtype="COLOR")  # type: ignore
    annotation_highlight_color: bpy.props.FloatVectorProperty(name="Cor de Destaque", size=4, min=0, max=1, default=(1.0, 1.0, 0.0, 1.0), subtype="COLOR")  # type: ignore
    obstacle_color: bpy.props.FloatVectorProperty(name="Cor dos Obstáculos", size=4, min=0, max=1, default=(0.9, 0.7, 0.4, 0.8), subtype="COLOR")  # type: ignore

    designer_name: bpy.props.StringProperty(
        name="Nome do Designer",
        description="Nome impresso nas pranchas e relatórios técnicos"
    )  # type: ignore

    # Layout view defaults
    line_engine: bpy.props.EnumProperty(
        name="Engine 2D",
        items=[
            ('FREESTYLE', 'Freestyle', 'Freestyle clássico'),
            ('LINEART', 'Grease Pencil Line Art', 'Linhas em tempo real (Line Art)'),
        ],
        default='FREESTYLE'
    )  # type: ignore

    default_paper_size: bpy.props.EnumProperty(
        name="Tamanho de Papel Padrão",
        items=[
            ('LETTER', 'Letter (Carta)', ''),
            ('LEGAL', 'Ofício', ''),
            ('TABLOID', 'Tabloide', ''),
            ('A4', 'A4', ''),
            ('A3', 'A3', ''),
        ],
        default='LEGAL'
    )  # type: ignore

    default_layout_scale: bpy.props.EnumProperty(
        name="Escala Padrão",
        items=[
            ('1:1', '1:1', ''),
            ('1:5', '1:5', ''),
            ('1:10', '1:10', ''),
            ('1:20', '1:20', ''),
            ('1:25', '1:25', ''),
            ('1:50', '1:50', ''),
            ('1:100', '1:100', ''),
        ],
        default='1:50'
    )  # type: ignore

    default_paper_landscape: bpy.props.BoolProperty(
        name="Orientação Paisagem",
        default=True
    )  # type: ignore

    asset_libraries: bpy.props.CollectionProperty(type=hb_assets.BTM_AssetLibraryEntry)  # type: ignore
    asset_libraries_index: bpy.props.IntProperty(name="Biblioteca Ativa", default=0)  # type: ignore

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "use_viewport_hud")
        layout.prop(self, "hide_2d_drawing_panels")

        box = layout.box()
        box.label(text="Padrões do Layout 2D", icon='RENDERLAYERS')
        col = box.column(align=True)
        col.prop(self, "line_engine")
        col.prop(self, "default_paper_size")
        col.prop(self, "default_layout_scale")
        col.prop(self, "default_paper_landscape")

        layout.separator()

        box = layout.box()
        box.label(text="Bibliotecas de Ativos", icon='ASSET_MANAGER')
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
    # Register assets first
    hb_assets.register()
    if not hasattr(bpy.types, BTM_AddonPreferences.__name__):
        try:
            bpy.utils.register_class(BTM_AddonPreferences)
        except Exception:
            pass

    # Register modern data layer and translation
    data.register()
    standards.register()
    cutting.register()

    # Register legacy properties
    hb_props.register()
    hb_project.register()
    hb_props_obstacles.register()

    # Register legacy operators
    ops_obstacles.register()
    walls.register()
    layouts.register()
    rooms.register()
    details.register()
    doors_windows.register()
    export.register()
    ops_stairs.register()
    scene_navigator.register()
    viewport_hud.register()
    ops_general.register()
    ops.register()

    # Register modern UI, operators & draw handlers
    btm_operators.register()
    ui.register()
    overlays.register()

    # Register legacy UI
    view3d_sidebar.register()
    menu_apend.register()
    menus.register()

    # Register product libraries
    closets.register()
    face_frame.register()
    frameless.register()
    wood_hoods.register()
    molding.register()

    # Re-arm asset library and handlers
    hb_assets.ensure_asset_libraries()
    if load_file_post not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(load_file_post)

    import inspect
    from . import hb_driver_functions
    for name, obj in inspect.getmembers(hb_driver_functions):
        if name not in bpy.app.driver_namespace:
            bpy.app.driver_namespace[name] = obj


def unregister():
    if load_file_post in bpy.app.handlers.load_post:
        try:
            bpy.app.handlers.load_post.remove(load_file_post)
        except Exception:
            pass

    # Unregister libraries
    closets.unregister()
    molding.unregister()
    wood_hoods.unregister()
    face_frame.unregister()
    frameless.unregister()

    # Unregister legacy UI
    menus.unregister()
    menu_apend.unregister()
    view3d_sidebar.unregister()

    # Unregister modern UI, operators & draw handlers
    overlays.unregister()
    ui.unregister()
    btm_operators.unregister()

    # Unregister legacy operators
    ops.unregister()
    ops_general.unregister()
    viewport_hud.unregister()
    scene_navigator.unregister()
    ops_stairs.unregister()
    export.unregister()
    doors_windows.unregister()
    details.unregister()
    rooms.unregister()
    layouts.unregister()
    walls.unregister()
    ops_obstacles.unregister()

    # Unregister properties
    hb_props_obstacles.unregister()
    hb_project.unregister()
    hb_props.unregister()

    # Unregister modern data
    cutting.unregister()
    standards.unregister()
    data.unregister()

    try:
        bpy.utils.unregister_class(BTM_AddonPreferences)
    except Exception:
        pass
    hb_assets.unregister()


if __name__ == "__main__":
    register()
