<!-- source: Blender Python API reference 5.2 / bpy.types.Scopes.html -->

<a id="scopes-bpy-struct"></a>

# Scopes(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.Scopes"></a>

### class bpy.types.Scopes(bpy_struct)

Scopes for statistical view of an image

<a id="bpy.types.Scopes.accuracy"></a>

#### bpy.types.Scopes.accuracy

Proportion of original image source pixel lines to sample (in [0, 100], default 0.0)

**Type:**

float

<a id="bpy.types.Scopes.histogram"></a>

#### bpy.types.Scopes.histogram

Histogram for viewing image statistics (readonly)

**Type:**

[`Histogram`](bpy.types.Histogram.md#bpy.types.Histogram "bpy.types.Histogram") | None

<a id="bpy.types.Scopes.use_full_resolution"></a>

#### bpy.types.Scopes.use_full_resolution

Sample every pixel of the image (default False)

**Type:**

bool

<a id="bpy.types.Scopes.vectorscope_alpha"></a>

#### bpy.types.Scopes.vectorscope_alpha

Opacity of the points (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.Scopes.vectorscope_mode"></a>

#### bpy.types.Scopes.vectorscope_mode

(default `'RGB'`)

**Type:**

Literal[‘LUMA’, ‘RGB’]

<a id="bpy.types.Scopes.waveform_alpha"></a>

#### bpy.types.Scopes.waveform_alpha

Opacity of the points (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.Scopes.waveform_mode"></a>

#### bpy.types.Scopes.waveform_mode

(default `'LUMA'`)

**Type:**

Literal[‘LUMA’, ‘PARADE’, ‘YCBCR601’, ‘YCBCR709’, ‘YCBCRJPG’, ‘RGB’]

<a id="bpy.types.Scopes.bl_rna_get_subclass"></a>

#### classmethod bpy.types.Scopes.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.Scopes.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.Scopes.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`SpaceImageEditor.scopes`](bpy.types.SpaceImageEditor.md#bpy.types.SpaceImageEditor.scopes "bpy.types.SpaceImageEditor.scopes") |  |
