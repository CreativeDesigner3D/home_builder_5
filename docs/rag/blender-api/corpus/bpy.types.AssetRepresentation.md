<!-- source: Blender Python API reference 5.2 / bpy.types.AssetRepresentation.html -->

<a id="assetrepresentation-bpy-struct"></a>

# AssetRepresentation(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.AssetRepresentation"></a>

### class bpy.types.AssetRepresentation(bpy_struct)

Information about an entity that makes it possible for the asset system to deal with the entity as asset

<a id="bpy.types.AssetRepresentation.full_library_path"></a>

#### bpy.types.AssetRepresentation.full_library_path

Absolute path to the .blend file containing this asset (default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.AssetRepresentation.full_path"></a>

#### bpy.types.AssetRepresentation.full_path

Absolute path to the .blend file containing this asset extended with the path of the asset inside the file (default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.AssetRepresentation.id_type"></a>

#### bpy.types.AssetRepresentation.id_type

The type of the data-block, if the asset represents one (‘NONE’ otherwise) (default `'ACTION'`, readonly)

**Type:**

Literal[[Id Type Items](bpy_types_enum_items/id_type_items.md#rna-enum-id-type-items)]

<a id="bpy.types.AssetRepresentation.is_online"></a>

#### bpy.types.AssetRepresentation.is_online

True if this asset is accessed via internet, not stored on disk (default False, readonly)

**Type:**

bool

<a id="bpy.types.AssetRepresentation.local_id"></a>

#### bpy.types.AssetRepresentation.local_id

The local data-block this asset represents; only valid if that is a data-block in this file (readonly)

**Type:**

[`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID") | None

<a id="bpy.types.AssetRepresentation.metadata"></a>

#### bpy.types.AssetRepresentation.metadata

Additional information about the asset (readonly)

**Type:**

[`AssetMetaData`](bpy.types.AssetMetaData.md#bpy.types.AssetMetaData "bpy.types.AssetMetaData") | None

<a id="bpy.types.AssetRepresentation.name"></a>

#### bpy.types.AssetRepresentation.name

(default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.AssetRepresentation.owner_asset_library"></a>

#### bpy.types.AssetRepresentation.owner_asset_library

The asset library containing this asset (readonly)

**Type:**

[`AssetLibrary`](bpy.types.AssetLibrary.md#bpy.types.AssetLibrary "bpy.types.AssetLibrary") | None

<a id="bpy.types.AssetRepresentation.bl_rna_get_subclass"></a>

#### classmethod bpy.types.AssetRepresentation.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.AssetRepresentation.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.AssetRepresentation.bl_rna_get_subclass_py(id, default=None, /)

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
| - `bpy.context.asset` - `bpy.context.selected_assets` - [`AssetShelf.asset_poll`](bpy.types.AssetShelf.md#bpy.types.AssetShelf.asset_poll "bpy.types.AssetShelf.asset_poll") | - [`AssetShelf.draw_context_menu`](bpy.types.AssetShelf.md#bpy.types.AssetShelf.draw_context_menu "bpy.types.AssetShelf.draw_context_menu") - [`Context.asset`](bpy.types.Context.md#bpy.types.Context.asset "bpy.types.Context.asset") |
