<!-- source: Blender Python API reference 5.2 / bpy.types.AssetLibrary.html -->

<a id="assetlibrary-bpy-struct"></a>

# AssetLibrary(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.AssetLibrary"></a>

### class bpy.types.AssetLibrary(bpy_struct)

Container for asset catalogs and assets

<a id="bpy.types.AssetLibrary.is_editable"></a>

#### bpy.types.AssetLibrary.is_editable

Assets and catalogs in this library can be edited from the current Blender instance (default False, readonly)

**Type:**

bool

<a id="bpy.types.AssetLibrary.type"></a>

#### bpy.types.AssetLibrary.type

(default `'ALL'`, readonly)

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

<a id="bpy.types.AssetLibrary.online_assets_url"></a>

#### classmethod bpy.types.AssetLibrary.online_assets_url()

online_assets_url

**Returns:**

URL, Remote location of the Online Essentials library (never None)

**Return type:**

str

<a id="bpy.types.AssetLibrary.online_assets_cache_path"></a>

#### classmethod bpy.types.AssetLibrary.online_assets_cache_path()

online_assets_cache_path

**Returns:**

Path, Local location of the Online Essentials library’s disk cache (never None)

**Return type:**

str

<a id="bpy.types.AssetLibrary.bl_rna_get_subclass"></a>

#### classmethod bpy.types.AssetLibrary.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.AssetLibrary.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.AssetLibrary.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([type](#bpy.types.AssetLibrary.type "bpy.types.AssetLibrary.type") | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

[type](#bpy.types.AssetLibrary.type "bpy.types.AssetLibrary.type")

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
| - [`AssetRepresentation.owner_asset_library`](bpy.types.AssetRepresentation.md#bpy.types.AssetRepresentation.owner_asset_library "bpy.types.AssetRepresentation.owner_asset_library") |  |
