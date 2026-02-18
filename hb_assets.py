import bpy
import os

BUNDLED_LIBRARY_NAME = "Home Builder"
USER_LIBRARY_PREFIX = "HB: "


def get_addon_assets_path():
    """Return the path to the addon's bundled assets directory."""
    return os.path.join(os.path.dirname(__file__), "assets")


def get_user_libraries():
    """Return the list of user-configured library entries."""
    prefs = bpy.context.preferences.addons[__package__].preferences
    return prefs.asset_libraries


def get_user_library_paths():
    """Return all user-configured library root paths."""
    paths = []
    try:
        for entry in get_user_libraries():
            if entry.library_path:
                lib_path = bpy.path.abspath(entry.library_path)
                if os.path.isdir(lib_path) and lib_path not in paths:
                    paths.append(lib_path)
    except Exception:
        pass
    return paths


def get_all_subfolder_paths(subfolder_name, bundled_path=None):
    """Return all paths for a specific subfolder, starting with the bundled path.
    
    Args:
        subfolder_name: Folder name to look for (e.g. 'moldings', 'cabinet_pulls')
        bundled_path: The addon's built-in path for this content (included first if valid)
    
    Returns list of directory paths. User libraries are scanned for matching subfolders.
    """
    paths = []
    
    # Bundled path first
    if bundled_path and os.path.isdir(bundled_path):
        paths.append(bundled_path)
    
    # Scan user library paths for matching subfolder
    for lib_path in get_user_library_paths():
        sub = os.path.join(lib_path, subfolder_name)
        if os.path.isdir(sub) and sub not in paths:
            paths.append(sub)
    
    return paths


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


def _get_library_name(user_name):
    """Get the Blender asset library name for a user library entry."""
    return USER_LIBRARY_PREFIX + user_name


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
    """Register bundled and all user asset libraries."""
    # Clean up legacy extended library from previous versions
    _remove_library("Home Builder Extended")
    
    _register_library(BUNDLED_LIBRARY_NAME, get_addon_assets_path())
    for entry in get_user_libraries():
        if entry.library_path:
            lib_path = bpy.path.abspath(entry.library_path)
            _register_library(_get_library_name(entry.name), lib_path)


def remove_asset_libraries():
    """Remove all Home Builder asset libraries from Blender preferences."""
    _remove_library(BUNDLED_LIBRARY_NAME)
    for entry in get_user_libraries():
        _remove_library(_get_library_name(entry.name))


def refresh_user_libraries():
    """Sync all user libraries - register valid ones, remove invalid ones."""
    # Remove any HB: prefixed libraries that are no longer in the list
    asset_libs = bpy.context.preferences.filepaths.asset_libraries
    user_lib_names = {_get_library_name(e.name) for e in get_user_libraries()}
    
    to_remove = []
    for i, lib in enumerate(asset_libs):
        if lib.name.startswith(USER_LIBRARY_PREFIX) and lib.name not in user_lib_names:
            to_remove.append(lib.name)
    for name in to_remove:
        _remove_library(name)
    
    # Register/update current entries
    for entry in get_user_libraries():
        lib_name = _get_library_name(entry.name)
        if entry.library_path:
            lib_path = bpy.path.abspath(entry.library_path)
            if os.path.isdir(lib_path):
                _register_library(lib_name, lib_path)
            else:
                _remove_library(lib_name)
        else:
            _remove_library(lib_name)


class HB_AssetLibraryEntry(bpy.types.PropertyGroup):
    """A single user asset library entry."""
    name: bpy.props.StringProperty(
        name="Name",
        description="Display name for this library",
        default="New Library"
    )  # type: ignore
    library_path: bpy.props.StringProperty(
        name="Path",
        description="Path to the asset library folder",
        subtype='DIR_PATH',
    )  # type: ignore


class HB_UL_asset_libraries(bpy.types.UIList):
    """UIList for displaying user asset libraries."""
    bl_idname = "HB_UL_asset_libraries"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            row.prop(item, "name", text="", emboss=False)
            row.prop(item, "library_path", text="")
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text=item.name)


class HB_OT_add_asset_library(bpy.types.Operator):
    """Add a new asset library entry"""
    bl_idname = "home_builder.add_asset_library"
    bl_label = "Add Asset Library"

    def execute(self, context):
        prefs = context.preferences.addons[__package__].preferences
        entry = prefs.asset_libraries.add()
        entry.name = "New Library"
        prefs.asset_libraries_index = len(prefs.asset_libraries) - 1
        return {'FINISHED'}


class HB_OT_remove_asset_library(bpy.types.Operator):
    """Remove the selected asset library entry"""
    bl_idname = "home_builder.remove_asset_library"
    bl_label = "Remove Asset Library"

    def execute(self, context):
        prefs = context.preferences.addons[__package__].preferences
        index = prefs.asset_libraries_index
        if 0 <= index < len(prefs.asset_libraries):
            # Remove from Blender's asset libraries first
            entry = prefs.asset_libraries[index]
            _remove_library(_get_library_name(entry.name))
            # Remove from our list
            prefs.asset_libraries.remove(index)
            prefs.asset_libraries_index = min(index, len(prefs.asset_libraries) - 1)
        return {'FINISHED'}


class HB_OT_refresh_asset_libraries(bpy.types.Operator):
    """Refresh all user asset libraries"""
    bl_idname = "home_builder.refresh_asset_libraries"
    bl_label = "Refresh Asset Libraries"

    def execute(self, context):
        refresh_user_libraries()
        self.report({'INFO'}, "Asset libraries updated")
        return {'FINISHED'}


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


classes = (
    HB_AssetLibraryEntry,
    HB_UL_asset_libraries,
    HB_OT_add_asset_library,
    HB_OT_remove_asset_library,
    HB_OT_refresh_asset_libraries,
    VIEW3D_AST_home_builder,
    HB_OT_assign_asset_catalog,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    remove_asset_libraries()
    for cls in classes:
        bpy.utils.unregister_class(cls)
