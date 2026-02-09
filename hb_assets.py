import bpy
import os

BUNDLED_LIBRARY_NAME = "Home Builder"
EXTENDED_LIBRARY_NAME = "Home Builder Extended"


def get_addon_assets_path():
    """Return the path to the addon's bundled assets directory."""
    return os.path.join(os.path.dirname(__file__), "assets")


def get_extended_assets_path():
    """Return the user-configured extended library path, or empty string."""
    prefs = bpy.context.preferences.addons[__package__].preferences
    return bpy.path.abspath(prefs.extended_library_path) if prefs.extended_library_path else ""


def get_catalog_map():
    """Parse the blender_assets.cats.txt and return a dict of {catalog_path: uuid}."""
    cats_file = os.path.join(get_addon_assets_path(), "blender_assets.cats.txt")
    catalog_map = {}
    if os.path.exists(cats_file):
        with open(cats_file, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or line.startswith("VERSION"):
                    continue
                parts = line.split(":")
                if len(parts) >= 2:
                    uid = parts[0]
                    path = parts[1]
                    catalog_map[path] = uid
    return catalog_map


def _register_library(name, path):
    """Register a path as a Blender asset library. Returns the library or None."""
    if not path or not os.path.isdir(path):
        return None

    asset_libs = bpy.context.preferences.filepaths.asset_libraries
    for lib in asset_libs:
        if lib.name == name:
            if lib.path != path:
                lib.path = path
            return lib

    lib = asset_libs.new(name=name, directory=path)
    lib.import_method = 'APPEND'
    return lib


def _remove_library(name):
    """Remove a named asset library from Blender preferences."""
    asset_libs = bpy.context.preferences.filepaths.asset_libraries
    for i, lib in enumerate(asset_libs):
        if lib.name == name:
            asset_libs.remove(asset_libs[i])
            return


def ensure_asset_libraries():
    """Register both bundled and extended asset libraries."""
    _register_library(BUNDLED_LIBRARY_NAME, get_addon_assets_path())
    ext_path = get_extended_assets_path()
    if ext_path:
        _register_library(EXTENDED_LIBRARY_NAME, ext_path)


def remove_asset_libraries():
    """Remove both asset libraries from Blender preferences."""
    _remove_library(BUNDLED_LIBRARY_NAME)
    _remove_library(EXTENDED_LIBRARY_NAME)


def refresh_extended_library():
    """Re-register or remove the extended library based on current preference."""
    ext_path = get_extended_assets_path()
    if ext_path and os.path.isdir(ext_path):
        _register_library(EXTENDED_LIBRARY_NAME, ext_path)
    else:
        _remove_library(EXTENDED_LIBRARY_NAME)


class VIEW3D_AST_home_builder(bpy.types.AssetShelf):
    bl_space_type = 'VIEW_3D'
    bl_idname = "VIEW3D_AST_home_builder"
    bl_options = {'DEFAULT_VISIBLE'}

    bl_default_preview_size = 96

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    @classmethod
    def asset_poll(cls, asset):
        return asset.id_type in {'OBJECT', 'COLLECTION', 'MATERIAL'}

    @classmethod
    def draw_context_menu(cls, context, asset, layout):
        layout.operator("object.delete", text="Delete Selected", icon='X')


class HB_OT_assign_asset_catalog(bpy.types.Operator):
    """Assign a catalog to all assets in a .blend file"""
    bl_idname = "home_builder.assign_asset_catalog"
    bl_label = "Assign Asset Catalog"
    bl_description = "Assign a catalog category to all marked assets in the current file"
    bl_options = {'REGISTER', 'UNDO'}

    catalog_path: bpy.props.EnumProperty(
        name="Catalog",
        description="Select the catalog to assign",
        items=lambda self, context: HB_OT_assign_asset_catalog._get_catalog_items(context),
    )  # type: ignore

    @staticmethod
    def _get_catalog_items(context):
        catalog_map = get_catalog_map()
        items = []
        for path in sorted(catalog_map.keys()):
            items.append((path, path, ""))
        if not items:
            items.append(('NONE', "No catalogs found", ""))
        return items

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "catalog_path")

    def execute(self, context):
        catalog_map = get_catalog_map()
        catalog_uuid = catalog_map.get(self.catalog_path, "")
        if not catalog_uuid:
            self.report({'ERROR'}, "Catalog not found")
            return {'CANCELLED'}

        count = 0
        for obj in bpy.data.objects:
            if obj.asset_data:
                obj.asset_data.catalog_id = catalog_uuid
                count += 1
        for mat in bpy.data.materials:
            if mat.asset_data:
                mat.asset_data.catalog_id = catalog_uuid
                count += 1
        for col in bpy.data.collections:
            if col.asset_data:
                col.asset_data.catalog_id = catalog_uuid
                count += 1

        self.report({'INFO'}, f"Assigned {count} assets to catalog: {self.catalog_path}")
        return {'FINISHED'}


class HB_OT_refresh_extended_library(bpy.types.Operator):
    """Refresh the extended asset library after changing the path"""
    bl_idname = "home_builder.refresh_extended_library"
    bl_label = "Refresh Extended Library"

    def execute(self, context):
        refresh_extended_library()
        self.report({'INFO'}, "Extended library updated")
        return {'FINISHED'}


classes = (
    VIEW3D_AST_home_builder,
    HB_OT_assign_asset_catalog,
    HB_OT_refresh_extended_library,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    ensure_asset_libraries()


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    remove_asset_libraries()
