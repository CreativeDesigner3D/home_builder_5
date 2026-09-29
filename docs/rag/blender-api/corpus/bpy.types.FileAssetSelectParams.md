<!-- source: Blender Python API reference 5.2 / bpy.types.FileAssetSelectParams.html -->

<a id="fileassetselectparams-fileselectparams"></a>

# FileAssetSelectParams(FileSelectParams)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`FileSelectParams`](bpy.types.FileSelectParams.md#bpy.types.FileSelectParams "bpy.types.FileSelectParams")

<a id="bpy.types.FileAssetSelectParams"></a>

### class bpy.types.FileAssetSelectParams(FileSelectParams)

Settings for the file selection in Asset Browser mode

<a id="bpy.types.FileAssetSelectParams.asset_access"></a>

#### bpy.types.FileAssetSelectParams.asset_access

Choose the visibility of online and offline assets (default `'ALL'`)

**Type:**

Literal[[Asset Access Items](bpy_types_enum_items/asset_access_items.md#rna-enum-asset-access-items)]

<a id="bpy.types.FileAssetSelectParams.asset_catalog_visibility"></a>

#### bpy.types.FileAssetSelectParams.asset_catalog_visibility

Which assets to show based on catalog filter (default `'ALL'`)

- `ALL`
  All – Show assets from all catalogs.
- `CATALOG`
  Catalog – Show assets from the active catalog only.
- `UNASSIGNED`
  Unassigned – Show assets not assigned to any catalog.

**Type:**

Literal[‘ALL’, ‘CATALOG’, ‘UNASSIGNED’]

<a id="bpy.types.FileAssetSelectParams.asset_library_reference"></a>

#### bpy.types.FileAssetSelectParams.asset_library_reference

(default `'ALL'`)

- `ALL`
  All Libraries – Show assets from all of the listed asset libraries.
- `LOCAL`
  Current File – Show the assets currently available in this Blender session.
- `ESSENTIALS`
  Essentials – Show basic building blocks and utilities coming with Blender.
- `ONLINE_ESSENTIALS`
  Online Essentials – Show additional building blocks and utilities available online.
- `CUSTOM`
  Custom – Show assets from the asset libraries configured in the Preferences.

**Type:**

Literal[‘ALL’, ‘LOCAL’, ‘ESSENTIALS’, ‘ONLINE_ESSENTIALS’, ‘CUSTOM’]

<a id="bpy.types.FileAssetSelectParams.catalog_id"></a>

#### bpy.types.FileAssetSelectParams.catalog_id

The UUID of the catalog shown in the browser (default “”, never None)

**Type:**

str

<a id="bpy.types.FileAssetSelectParams.filter_asset_id"></a>

#### bpy.types.FileAssetSelectParams.filter_asset_id

Which asset types to show/hide, when browsing an asset library (readonly, never None)

**Type:**

[`FileAssetSelectIDFilter`](bpy.types.FileAssetSelectIDFilter.md#bpy.types.FileAssetSelectIDFilter "bpy.types.FileAssetSelectIDFilter")

<a id="bpy.types.FileAssetSelectParams.import_method"></a>

#### bpy.types.FileAssetSelectParams.import_method

Determine how the asset will be imported (default `'LINK'`)

- `FOLLOW_PREFS`
  Follow Asset or Preferences – Use the import method set in the Preferences for this asset library, don’t override it for this Asset Browser.
- `LINK`
  Link – Import the assets as linked data-block.
- `APPEND`
  Append – Import the asset as copied data-block, with no link to the original asset data-block.
- `APPEND_REUSE`
  Append (Reuse Data) – Import the asset as copied data-block while avoiding multiple copies of nested, typically heavy data. For example the textures of a material asset, or the mesh of an object asset, don’t have to be copied every time this asset is imported. The instances of the asset share the data instead.
- `PACK`
  Pack – Import the asset as linked data-block, and pack it in the current file (ensures that it remains unchanged in case the library data is modified, is not available anymore, etc.).

**Type:**

Literal[‘FOLLOW_PREFS’, ‘LINK’, ‘APPEND’, ‘APPEND_REUSE’, ‘PACK’]

<a id="bpy.types.FileAssetSelectParams.instance_collections_on_append"></a>

#### bpy.types.FileAssetSelectParams.instance_collections_on_append

Create instances for collections when appending, rather than adding them directly to the scene (default False)

**Type:**

bool

<a id="bpy.types.FileAssetSelectParams.instance_collections_on_link"></a>

#### bpy.types.FileAssetSelectParams.instance_collections_on_link

Create instances for collections when linking, rather than adding them directly to the scene (default False)

**Type:**

bool

<a id="bpy.types.FileAssetSelectParams.bl_rna_get_subclass"></a>

#### classmethod bpy.types.FileAssetSelectParams.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.FileAssetSelectParams.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.FileAssetSelectParams.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, FileSelectParams.title, FileSelectParams.directory, FileSelectParams.filename, FileSelectParams.use_library_browsing, FileSelectParams.display_type, FileSelectParams.recursion_level, FileSelectParams.show_details_size, FileSelectParams.show_details_datetime, FileSelectParams.use_filter, FileSelectParams.show_hidden, FileSelectParams.sort_method, FileSelectParams.use_sort_invert, FileSelectParams.use_filter_image, FileSelectParams.use_filter_blender, FileSelectParams.use_filter_backup, FileSelectParams.use_filter_movie, FileSelectParams.use_filter_script, FileSelectParams.use_filter_font, FileSelectParams.use_filter_sound, FileSelectParams.use_filter_text, FileSelectParams.use_filter_volume, FileSelectParams.use_filter_folder, FileSelectParams.use_filter_blendid, FileSelectParams.use_filter_asset_only, FileSelectParams.filter_id, FileSelectParams.filter_glob, FileSelectParams.filter_search, FileSelectParams.display_size, FileSelectParams.display_size_discrete, FileSelectParams.list_display_size, FileSelectParams.list_column_size

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, FileSelectParams.bl_rna_get_subclass, FileSelectParams.bl_rna_get_subclass_py
