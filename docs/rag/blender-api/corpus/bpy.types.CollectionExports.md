<!-- source: Blender Python API reference 5.2 / bpy.types.CollectionExports.html -->

<a id="collectionexports-bpy-prop-collection"></a>

# CollectionExports(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.CollectionExports"></a>

### class bpy.types.CollectionExports(bpy_prop_collection)

Collection of export handlers

<a id="bpy.types.CollectionExports.new"></a>

#### bpy.types.CollectionExports.new(type, *, name='')

Add an export handler to the collection

**Parameters:**

- **type** (Literal['IO_FH_alembic', 'IO_FH_usd', 'IO_FH_obj', 'IO_FH_ply', 'IO_FH_stl', 'IO_FH_fbx', 'IO_FH_gltf2']) – Type, The type of export handler to add
- **name** (str) – Name, Name of the new export handler (optional, never None)

**Returns:**

Newly created export handler

**Return type:**

[`CollectionExport`](bpy.types.CollectionExport.md#bpy.types.CollectionExport "bpy.types.CollectionExport")

<a id="bpy.types.CollectionExports.remove"></a>

#### bpy.types.CollectionExports.remove(exporter)

Remove an export handler from the collection

**Parameters:**

**exporter** ([`CollectionExport`](bpy.types.CollectionExport.md#bpy.types.CollectionExport "bpy.types.CollectionExport") | None) – Export Handler to remove

<a id="bpy.types.CollectionExports.move"></a>

#### bpy.types.CollectionExports.move(from_index, to_index)

Move an export handler

**Parameters:**

- **from_index** (int) – From Index, Index to move (in [-inf, inf])
- **to_index** (int) – To Index, Target index (in [-inf, inf])

<a id="bpy.types.CollectionExports.bl_rna_get_subclass"></a>

#### classmethod bpy.types.CollectionExports.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.CollectionExports.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.CollectionExports.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Collection.exporters`](bpy.types.Collection.md#bpy.types.Collection.exporters "bpy.types.Collection.exporters") |  |
