<!-- source: Blender Python API reference 5.2 / bpy.types.Histogram.html -->

<a id="histogram-bpy-struct"></a>

# Histogram(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.Histogram"></a>

### class bpy.types.Histogram(bpy_struct)

Statistical view of the levels of color in an image

<a id="bpy.types.Histogram.mode"></a>

#### bpy.types.Histogram.mode

Channels to display in the histogram (default `'LUMA'`)

- `LUMA`
  Luma – Luma.
- `RGB`
  RGB – Red Green Blue.
- `R`
  R – Red.
- `G`
  G – Green.
- `B`
  B – Blue.
- `A`
  A – Alpha.

**Type:**

Literal[‘LUMA’, ‘RGB’, ‘R’, ‘G’, ‘B’, ‘A’]

<a id="bpy.types.Histogram.show_line"></a>

#### bpy.types.Histogram.show_line

Display lines rather than filled shapes (default False)

**Type:**

bool

<a id="bpy.types.Histogram.bl_rna_get_subclass"></a>

#### classmethod bpy.types.Histogram.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.Histogram.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.Histogram.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Scopes.histogram`](bpy.types.Scopes.md#bpy.types.Scopes.histogram "bpy.types.Scopes.histogram") | - [`SpaceImageEditor.sample_histogram`](bpy.types.SpaceImageEditor.md#bpy.types.SpaceImageEditor.sample_histogram "bpy.types.SpaceImageEditor.sample_histogram") |
