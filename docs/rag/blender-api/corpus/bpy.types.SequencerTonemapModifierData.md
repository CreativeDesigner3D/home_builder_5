<!-- source: Blender Python API reference 5.2 / bpy.types.SequencerTonemapModifierData.html -->

<a id="sequencertonemapmodifierdata-stripmodifier"></a>

# SequencerTonemapModifierData(StripModifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`StripModifier`](bpy.types.StripModifier.md#bpy.types.StripModifier "bpy.types.StripModifier")

<a id="bpy.types.SequencerTonemapModifierData"></a>

### class bpy.types.SequencerTonemapModifierData(StripModifier)

Tone mapping modifier

<a id="bpy.types.SequencerTonemapModifierData.adaptation"></a>

#### bpy.types.SequencerTonemapModifierData.adaptation

If 0, global; if 1, based on pixel intensity (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.SequencerTonemapModifierData.contrast"></a>

#### bpy.types.SequencerTonemapModifierData.contrast

Set to 0 to use estimate from input image (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.SequencerTonemapModifierData.correction"></a>

#### bpy.types.SequencerTonemapModifierData.correction

If 0, same for all channels; if 1, each independent (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.SequencerTonemapModifierData.gamma"></a>

#### bpy.types.SequencerTonemapModifierData.gamma

If not used, set to 1 (in [0.001, 3], default 0.0)

**Type:**

float

<a id="bpy.types.SequencerTonemapModifierData.intensity"></a>

#### bpy.types.SequencerTonemapModifierData.intensity

If less than zero, darkens image; otherwise, makes it brighter (in [-8, 8], default 0.0)

**Type:**

float

<a id="bpy.types.SequencerTonemapModifierData.key"></a>

#### bpy.types.SequencerTonemapModifierData.key

The value the average luminance is mapped to (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.SequencerTonemapModifierData.offset"></a>

#### bpy.types.SequencerTonemapModifierData.offset

Normally always 1, but can be used as an extra control to alter the brightness curve (in [0.001, 10], default 0.0)

**Type:**

float

<a id="bpy.types.SequencerTonemapModifierData.open_mask_input_panel"></a>

#### bpy.types.SequencerTonemapModifierData.open_mask_input_panel

(default False)

**Type:**

bool

<a id="bpy.types.SequencerTonemapModifierData.tonemap_type"></a>

#### bpy.types.SequencerTonemapModifierData.tonemap_type

Tone mapping algorithm (default `'RH_SIMPLE'`)

**Type:**

Literal[‘RD_PHOTORECEPTOR’, ‘RH_SIMPLE’]

<a id="bpy.types.SequencerTonemapModifierData.bl_rna_get_subclass"></a>

#### classmethod bpy.types.SequencerTonemapModifierData.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.SequencerTonemapModifierData.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.SequencerTonemapModifierData.bl_rna_get_subclass_py(id, default=None, /)

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
