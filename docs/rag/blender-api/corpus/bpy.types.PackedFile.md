<!-- source: Blender Python API reference 5.2 / bpy.types.PackedFile.html -->

<a id="packedfile-bpy-struct"></a>

# PackedFile(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.PackedFile"></a>

### class bpy.types.PackedFile(bpy_struct)

External file packed into the .blend file

<a id="bpy.types.PackedFile.data"></a>

#### bpy.types.PackedFile.data

Raw data (bytes, exact content of the embedded file) (default b””, readonly, never None)

**Type:**

bytes

<a id="bpy.types.PackedFile.size"></a>

#### bpy.types.PackedFile.size

Size of packed file in bytes (in [-inf, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.PackedFile.bl_rna_get_subclass"></a>

#### classmethod bpy.types.PackedFile.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.PackedFile.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.PackedFile.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Image.packed_file`](bpy.types.Image.md#bpy.types.Image.packed_file "bpy.types.Image.packed_file") - [`ImagePackedFile.packed_file`](bpy.types.ImagePackedFile.md#bpy.types.ImagePackedFile.packed_file "bpy.types.ImagePackedFile.packed_file") - [`Library.packed_file`](bpy.types.Library.md#bpy.types.Library.packed_file "bpy.types.Library.packed_file") | - [`Sound.packed_file`](bpy.types.Sound.md#bpy.types.Sound.packed_file "bpy.types.Sound.packed_file") - [`VectorFont.packed_file`](bpy.types.VectorFont.md#bpy.types.VectorFont.packed_file "bpy.types.VectorFont.packed_file") - [`Volume.packed_file`](bpy.types.Volume.md#bpy.types.Volume.packed_file "bpy.types.Volume.packed_file") |
