<!-- source: Blender Python API reference 5.2 / bpy.types.IDOverrideLibraryProperty.html -->

<a id="idoverridelibraryproperty-bpy-struct"></a>

# IDOverrideLibraryProperty(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.IDOverrideLibraryProperty"></a>

### class bpy.types.IDOverrideLibraryProperty(bpy_struct)

Description of an overridden property

<a id="bpy.types.IDOverrideLibraryProperty.operations"></a>

#### bpy.types.IDOverrideLibraryProperty.operations

List of overriding operations for a property (default None, readonly)

**Type:**

[`IDOverrideLibraryPropertyOperations`](bpy.types.IDOverrideLibraryPropertyOperations.md#bpy.types.IDOverrideLibraryPropertyOperations "bpy.types.IDOverrideLibraryPropertyOperations")[[`IDOverrideLibraryPropertyOperation`](bpy.types.IDOverrideLibraryPropertyOperation.md#bpy.types.IDOverrideLibraryPropertyOperation "bpy.types.IDOverrideLibraryPropertyOperation")]

<a id="bpy.types.IDOverrideLibraryProperty.rna_path"></a>

#### bpy.types.IDOverrideLibraryProperty.rna_path

RNA path leading to that property, from owning ID (default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.IDOverrideLibraryProperty.bl_rna_get_subclass"></a>

#### classmethod bpy.types.IDOverrideLibraryProperty.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.IDOverrideLibraryProperty.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.IDOverrideLibraryProperty.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`IDOverrideLibrary.properties`](bpy.types.IDOverrideLibrary.md#bpy.types.IDOverrideLibrary.properties "bpy.types.IDOverrideLibrary.properties") - [`IDOverrideLibraryProperties.add`](bpy.types.IDOverrideLibraryProperties.md#bpy.types.IDOverrideLibraryProperties.add "bpy.types.IDOverrideLibraryProperties.add") | - [`IDOverrideLibraryProperties.remove`](bpy.types.IDOverrideLibraryProperties.md#bpy.types.IDOverrideLibraryProperties.remove "bpy.types.IDOverrideLibraryProperties.remove") |
