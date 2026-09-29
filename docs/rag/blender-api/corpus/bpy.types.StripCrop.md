<!-- source: Blender Python API reference 5.2 / bpy.types.StripCrop.html -->

<a id="stripcrop-bpy-struct"></a>

# StripCrop(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.StripCrop"></a>

### class bpy.types.StripCrop(bpy_struct)

Cropping parameters for a sequence strip

<a id="bpy.types.StripCrop.max_x"></a>

#### bpy.types.StripCrop.max_x

Number of pixels to crop from the right side (in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.StripCrop.max_y"></a>

#### bpy.types.StripCrop.max_y

Number of pixels to crop from the top (in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.StripCrop.min_x"></a>

#### bpy.types.StripCrop.min_x

Number of pixels to crop from the left side (in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.StripCrop.min_y"></a>

#### bpy.types.StripCrop.min_y

Number of pixels to crop from the bottom (in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.StripCrop.bl_rna_get_subclass"></a>

#### classmethod bpy.types.StripCrop.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.StripCrop.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.StripCrop.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`EffectStrip.crop`](bpy.types.EffectStrip.md#bpy.types.EffectStrip.crop "bpy.types.EffectStrip.crop") - [`ImageStrip.crop`](bpy.types.ImageStrip.md#bpy.types.ImageStrip.crop "bpy.types.ImageStrip.crop") - [`MaskStrip.crop`](bpy.types.MaskStrip.md#bpy.types.MaskStrip.crop "bpy.types.MaskStrip.crop") - [`MetaStrip.crop`](bpy.types.MetaStrip.md#bpy.types.MetaStrip.crop "bpy.types.MetaStrip.crop") | - [`MovieClipStrip.crop`](bpy.types.MovieClipStrip.md#bpy.types.MovieClipStrip.crop "bpy.types.MovieClipStrip.crop") - [`MovieStrip.crop`](bpy.types.MovieStrip.md#bpy.types.MovieStrip.crop "bpy.types.MovieStrip.crop") - [`SceneStrip.crop`](bpy.types.SceneStrip.md#bpy.types.SceneStrip.crop "bpy.types.SceneStrip.crop") |
