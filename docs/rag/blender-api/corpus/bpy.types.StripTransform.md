<!-- source: Blender Python API reference 5.2 / bpy.types.StripTransform.html -->

<a id="striptransform-bpy-struct"></a>

# StripTransform(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.StripTransform"></a>

### class bpy.types.StripTransform(bpy_struct)

Transform parameters for a sequence strip

<a id="bpy.types.StripTransform.filter"></a>

#### bpy.types.StripTransform.filter

Type of filter to use for image transformation (default `'AUTO'`)

- `AUTO`
  Auto – Automatically choose filter based on scaling factor.
- `NEAREST`
  Nearest – Use nearest sample.
- `BILINEAR`
  Bilinear – Interpolate between 2×2 samples.
- `CUBIC_MITCHELL`
  Cubic Mitchell – Cubic Mitchell filter on 4×4 samples.
- `CUBIC_BSPLINE`
  Cubic B-Spline – Cubic B-Spline filter (blurry but no ringing) on 4×4 samples.
- `BOX`
  Box – Averages source image samples that fall under destination pixel.

**Type:**

Literal[‘AUTO’, ‘NEAREST’, ‘BILINEAR’, ‘CUBIC_MITCHELL’, ‘CUBIC_BSPLINE’, ‘BOX’]

<a id="bpy.types.StripTransform.offset_x"></a>

#### bpy.types.StripTransform.offset_x

Move along X axis (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.StripTransform.offset_y"></a>

#### bpy.types.StripTransform.offset_y

Move along Y axis (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.StripTransform.origin"></a>

#### bpy.types.StripTransform.origin

Origin of image for transformation (array of 2 items, in [-inf, inf], default (0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.StripTransform.rotation"></a>

#### bpy.types.StripTransform.rotation

Rotate around image center (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.StripTransform.scale_x"></a>

#### bpy.types.StripTransform.scale_x

Scale along X axis (in [0, inf], default 1.0)

**Type:**

float

<a id="bpy.types.StripTransform.scale_y"></a>

#### bpy.types.StripTransform.scale_y

Scale along Y axis (in [0, inf], default 1.0)

**Type:**

float

<a id="bpy.types.StripTransform.bl_rna_get_subclass"></a>

#### classmethod bpy.types.StripTransform.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.StripTransform.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.StripTransform.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`EffectStrip.transform`](bpy.types.EffectStrip.md#bpy.types.EffectStrip.transform "bpy.types.EffectStrip.transform") - [`ImageStrip.transform`](bpy.types.ImageStrip.md#bpy.types.ImageStrip.transform "bpy.types.ImageStrip.transform") - [`MaskStrip.transform`](bpy.types.MaskStrip.md#bpy.types.MaskStrip.transform "bpy.types.MaskStrip.transform") - [`MetaStrip.transform`](bpy.types.MetaStrip.md#bpy.types.MetaStrip.transform "bpy.types.MetaStrip.transform") | - [`MovieClipStrip.transform`](bpy.types.MovieClipStrip.md#bpy.types.MovieClipStrip.transform "bpy.types.MovieClipStrip.transform") - [`MovieStrip.transform`](bpy.types.MovieStrip.md#bpy.types.MovieStrip.transform "bpy.types.MovieStrip.transform") - [`SceneStrip.transform`](bpy.types.SceneStrip.md#bpy.types.SceneStrip.transform "bpy.types.SceneStrip.transform") |
