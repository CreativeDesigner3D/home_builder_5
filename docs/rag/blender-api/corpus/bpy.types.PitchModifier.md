<!-- source: Blender Python API reference 5.2 / bpy.types.PitchModifier.html -->

<a id="pitchmodifier-stripmodifier"></a>

# PitchModifier(StripModifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`StripModifier`](bpy.types.StripModifier.md#bpy.types.StripModifier "bpy.types.StripModifier")

<a id="bpy.types.PitchModifier"></a>

### class bpy.types.PitchModifier(StripModifier)

Shift Audio Pitch

<a id="bpy.types.PitchModifier.cents"></a>

#### bpy.types.PitchModifier.cents

A cent is one one-hundredth of a semi-tone. (in [-100, 100], default 0)

**Type:**

int

<a id="bpy.types.PitchModifier.mode"></a>

#### bpy.types.PitchModifier.mode

Mode of the pitch shift (default `'SEMITONES'`)

- `SEMITONES`
  Semitones – Shift pitch using semitones and cents.
- `RATIO`
  Ratio – Shift pitch using a direct ratio.

**Type:**

Literal[‘SEMITONES’, ‘RATIO’]

<a id="bpy.types.PitchModifier.preserve_formant"></a>

#### bpy.types.PitchModifier.preserve_formant

Whether to preserve the vocal formants when shifting the pitch. (default False)

**Type:**

bool

<a id="bpy.types.PitchModifier.quality"></a>

#### bpy.types.PitchModifier.quality

Quality of the pitch shifting (default `'HIGH'`)

- `HIGH`
  High – Prioritize high-quality pitch processing.
- `FAST`
  Fast – Prioritize speed over audio quality.
- `CONSISTENT`
  Consistent – Prioritize consistency for dynamic pitch changes.

**Type:**

Literal[‘HIGH’, ‘FAST’, ‘CONSISTENT’]

<a id="bpy.types.PitchModifier.ratio"></a>

#### bpy.types.PitchModifier.ratio

Factor by which the audio pitch is scaled. (in [0.5, 2], default 0.0)

**Type:**

float

<a id="bpy.types.PitchModifier.semitones"></a>

#### bpy.types.PitchModifier.semitones

Number of semitones to shift the pitch. (in [-12, 12], default 0)

**Type:**

int

<a id="bpy.types.PitchModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.PitchModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.PitchModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.PitchModifier.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, StripModifier.name, StripModifier.type, StripModifier.mute, StripModifier.enable, StripModifier.show_preview, StripModifier.show_expanded, StripModifier.input_mask_type, StripModifier.mask_time, StripModifier.input_mask_strip, StripModifier.input_mask_id, StripModifier.is_active

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, StripModifier.bl_rna_get_subclass, StripModifier.bl_rna_get_subclass_py
