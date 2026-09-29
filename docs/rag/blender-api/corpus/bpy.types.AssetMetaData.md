<!-- source: Blender Python API reference 5.2 / bpy.types.AssetMetaData.html -->

<a id="assetmetadata-bpy-struct"></a>

# AssetMetaData(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.AssetMetaData"></a>

### class bpy.types.AssetMetaData(bpy_struct)

Additional data stored for an asset data-block

<a id="bpy.types.AssetMetaData.active_tag"></a>

#### bpy.types.AssetMetaData.active_tag

Index of the tag set for editing (in [-32768, 32767], default 0)

**Type:**

int

<a id="bpy.types.AssetMetaData.author"></a>

#### bpy.types.AssetMetaData.author

Name of the creator of the asset (default “”, never None)

**Type:**

str

<a id="bpy.types.AssetMetaData.catalog_id"></a>

#### bpy.types.AssetMetaData.catalog_id

Identifier for the asset’s catalog, used by Blender to look up the asset’s catalog path. Must be a UUID according to RFC4122. (default “”, never None)

**Type:**

str

<a id="bpy.types.AssetMetaData.catalog_simple_name"></a>

#### bpy.types.AssetMetaData.catalog_simple_name

Simple name of the asset’s catalog, for debugging and data recovery purposes (default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.AssetMetaData.copyright"></a>

#### bpy.types.AssetMetaData.copyright

Copyright notice for this asset. An empty copyright notice does not necessarily indicate that this is copyright-free. Contact the author if any clarification is needed. (default “”, never None)

**Type:**

str

<a id="bpy.types.AssetMetaData.description"></a>

#### bpy.types.AssetMetaData.description

A description of the asset to be displayed for the user (default “”, never None)

**Type:**

str

<a id="bpy.types.AssetMetaData.license"></a>

#### bpy.types.AssetMetaData.license

The type of license this asset is distributed under. An empty license name does not necessarily indicate that this is free of licensing terms. Contact the author if any clarification is needed. (default “”, never None)

**Type:**

str

<a id="bpy.types.AssetMetaData.preferred_import_method"></a>

#### bpy.types.AssetMetaData.preferred_import_method

(default `'APPEND'`)

**Type:**

Literal[[Asset Import Method Items](bpy_types_enum_items/asset_import_method_items.md#rna-enum-asset-import-method-items)]

<a id="bpy.types.AssetMetaData.tags"></a>

#### bpy.types.AssetMetaData.tags

Custom tags (name tokens) for the asset, used for filtering and general asset management (default None, readonly)

**Type:**

[`AssetTags`](bpy.types.AssetTags.md#bpy.types.AssetTags "bpy.types.AssetTags")[[`AssetTag`](bpy.types.AssetTag.md#bpy.types.AssetTag "bpy.types.AssetTag")]

<a id="bpy.types.AssetMetaData.use_preferred_import_method"></a>

#### bpy.types.AssetMetaData.use_preferred_import_method

When “Follow Asset or Preferences” is selected for the import method in the Asset Browser, use the preferred import method of this asset (default False)

**Type:**

bool

<a id="bpy.types.AssetMetaData.bl_rna_get_subclass"></a>

#### classmethod bpy.types.AssetMetaData.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.AssetMetaData.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.AssetMetaData.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`AssetRepresentation.metadata`](bpy.types.AssetRepresentation.md#bpy.types.AssetRepresentation.metadata "bpy.types.AssetRepresentation.metadata") - [`FileSelectEntry.asset_data`](bpy.types.FileSelectEntry.md#bpy.types.FileSelectEntry.asset_data "bpy.types.FileSelectEntry.asset_data") | - [`ID.asset_data`](bpy.types.ID.md#bpy.types.ID.asset_data "bpy.types.ID.asset_data") |
