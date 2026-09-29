<!-- source: Blender Python API reference 5.2 / bpy.types.BlendFileColorspace.html -->

<a id="blendfilecolorspace-bpy-struct"></a>

# BlendFileColorspace(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.BlendFileColorspace"></a>

### class bpy.types.BlendFileColorspace(bpy_struct)

Information about the color space used for data-blocks in a blend file

<a id="bpy.types.BlendFileColorspace.is_missing_opencolorio_config"></a>

#### bpy.types.BlendFileColorspace.is_missing_opencolorio_config

A color space, view or display was not found, which likely means the OpenColorIO config used to create this blend file is missing (default False, readonly)

**Type:**

bool

<a id="bpy.types.BlendFileColorspace.working_space"></a>

#### bpy.types.BlendFileColorspace.working_space

Color space used for all scene linear colors in this file, and for compositing, shader and geometry nodes processing (readonly)

- `Linear Rec.709`
  Linear Rec.709 – Linear BT.709 with illuminant D65 white point.
- `Linear Rec.2020`
  Linear Rec.2020 – Linear BT.2020 with illuminant D65 white point.
- `ACEScg`
  ACEScg – Linear AP1 with ACES white point.

**Type:**

Literal[‘Linear Rec.709’, ‘Linear Rec.2020’, ‘ACEScg’]

<a id="bpy.types.BlendFileColorspace.working_space_interop_id"></a>

#### bpy.types.BlendFileColorspace.working_space_interop_id

Unique identifier for common color spaces, as defined by the Color Interop Forum. May be empty if there is no interop ID for the working space. Common values are lin_rec709_scene, lin_rec2020_scene and lin_ap1_scene (for ACEScg) (default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.BlendFileColorspace.bl_rna_get_subclass"></a>

#### classmethod bpy.types.BlendFileColorspace.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.BlendFileColorspace.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.BlendFileColorspace.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`BlendData.colorspace`](bpy.types.BlendData.md#bpy.types.BlendData.colorspace "bpy.types.BlendData.colorspace") |  |
