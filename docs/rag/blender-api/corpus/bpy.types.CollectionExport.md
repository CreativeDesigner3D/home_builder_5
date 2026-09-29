<!-- source: Blender Python API reference 5.2 / bpy.types.CollectionExport.html -->

<a id="collectionexport-bpy-struct"></a>

# CollectionExport(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.CollectionExport"></a>

### class bpy.types.CollectionExport(bpy_struct)

<a id="bpy.types.CollectionExport.export_properties"></a>

#### bpy.types.CollectionExport.export_properties

Properties associated with the configured exporter (readonly)

**Type:**

[`PropertyGroup`](bpy.types.PropertyGroup.md#bpy.types.PropertyGroup "bpy.types.PropertyGroup") | None

<a id="bpy.types.CollectionExport.filepath"></a>

#### bpy.types.CollectionExport.filepath

The file path used for exporting (default “”, never None, blend relative `//` prefix supported)

**Type:**

str

<a id="bpy.types.CollectionExport.is_open"></a>

#### bpy.types.CollectionExport.is_open

Whether the panel is expanded or closed (default False)

**Type:**

bool

<a id="bpy.types.CollectionExport.name"></a>

#### bpy.types.CollectionExport.name

(default “”, never None)

**Type:**

str

<a id="bpy.types.CollectionExport.bl_rna_get_subclass"></a>

#### classmethod bpy.types.CollectionExport.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.CollectionExport.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.CollectionExport.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Collection.exporters`](bpy.types.Collection.md#bpy.types.Collection.exporters "bpy.types.Collection.exporters") - [`CollectionExports.new`](bpy.types.CollectionExports.md#bpy.types.CollectionExports.new "bpy.types.CollectionExports.new") | - [`CollectionExports.remove`](bpy.types.CollectionExports.md#bpy.types.CollectionExports.remove "bpy.types.CollectionExports.remove") |
