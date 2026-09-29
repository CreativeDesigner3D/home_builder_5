<!-- source: Blender Python API reference 5.2 / bpy.types.UserAssetLibrary.html -->

<a id="userassetlibrary-bpy-struct"></a>

# UserAssetLibrary(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.UserAssetLibrary"></a>

### class bpy.types.UserAssetLibrary(bpy_struct)

Settings to define a reusable library for Asset Browsers to use

<a id="bpy.types.UserAssetLibrary.enabled"></a>

#### bpy.types.UserAssetLibrary.enabled

Enable the asset library (default True)

**Type:**

bool

<a id="bpy.types.UserAssetLibrary.import_method"></a>

#### bpy.types.UserAssetLibrary.import_method

Determine how the asset will be imported, unless overridden by the Asset Browser (default `'PACK'`)

**Type:**

Literal[[Asset Import Method Items](bpy_types_enum_items/asset_import_method_items.md#rna-enum-asset-import-method-items)]

<a id="bpy.types.UserAssetLibrary.name"></a>

#### bpy.types.UserAssetLibrary.name

Identifier (not necessarily unique) for the asset library (default “”, never None)

**Type:**

str

<a id="bpy.types.UserAssetLibrary.path"></a>

#### bpy.types.UserAssetLibrary.path

Path to a directory with .blend files to use as an asset library (default “”, never None)

**Type:**

str

<a id="bpy.types.UserAssetLibrary.remote_url"></a>

#### bpy.types.UserAssetLibrary.remote_url

Remote URL to the asset library (default “”, never None)

**Type:**

str

<a id="bpy.types.UserAssetLibrary.use_relative_path"></a>

#### bpy.types.UserAssetLibrary.use_relative_path

Use relative path when linking assets from this asset library (default True)

**Type:**

bool

<a id="bpy.types.UserAssetLibrary.use_remote_url"></a>

#### bpy.types.UserAssetLibrary.use_remote_url

Synchronize the asset library with a remote URL (default False, readonly)

**Type:**

bool

<a id="bpy.types.UserAssetLibrary.bl_rna_get_subclass"></a>

#### classmethod bpy.types.UserAssetLibrary.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.UserAssetLibrary.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.UserAssetLibrary.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values

<a id="references"></a>

## References

|  |  |
| --- | --- |
| - [`AssetLibraryCollection.new`](bpy.types.AssetLibraryCollection.md#bpy.types.AssetLibraryCollection.new "bpy.types.AssetLibraryCollection.new") - [`AssetLibraryCollection.remove`](bpy.types.AssetLibraryCollection.md#bpy.types.AssetLibraryCollection.remove "bpy.types.AssetLibraryCollection.remove") | - [`PreferencesFilePaths.asset_libraries`](bpy.types.PreferencesFilePaths.md#bpy.types.PreferencesFilePaths.asset_libraries "bpy.types.PreferencesFilePaths.asset_libraries") |
