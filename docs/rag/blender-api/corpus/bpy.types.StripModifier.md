<!-- source: Blender Python API reference 5.2 / bpy.types.StripModifier.html -->

<a id="stripmodifier-bpy-struct"></a>

# StripModifier(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

Subclasses

- [BrightContrastModifier(StripModifier)](bpy.types.BrightContrastModifier.md)
- [ColorBalanceModifier(StripModifier)](bpy.types.ColorBalanceModifier.md)
- [CurvesModifier(StripModifier)](bpy.types.CurvesModifier.md)
- [EchoModifier(StripModifier)](bpy.types.EchoModifier.md)
- [HueCorrectModifier(StripModifier)](bpy.types.HueCorrectModifier.md)
- [MaskStripModifier(StripModifier)](bpy.types.MaskStripModifier.md)
- [PitchModifier(StripModifier)](bpy.types.PitchModifier.md)
- [SequencerCompositorModifierData(StripModifier)](bpy.types.SequencerCompositorModifierData.md)
- [SequencerTonemapModifierData(StripModifier)](bpy.types.SequencerTonemapModifierData.md)
- [SoundEqualizerModifier(StripModifier)](bpy.types.SoundEqualizerModifier.md)
- [WhiteBalanceModifier(StripModifier)](bpy.types.WhiteBalanceModifier.md)

<a id="bpy.types.StripModifier"></a>

### class bpy.types.StripModifier(bpy_struct)

Modifier for sequence strip

<a id="bpy.types.StripModifier.enable"></a>

#### bpy.types.StripModifier.enable

Use modifier during render (default True)

**Type:**

bool

<a id="bpy.types.StripModifier.input_mask_id"></a>

#### bpy.types.StripModifier.input_mask_id

Mask ID used as mask input for the modifier

**Type:**

[`Mask`](bpy.types.Mask.md#bpy.types.Mask "bpy.types.Mask") | None

<a id="bpy.types.StripModifier.input_mask_strip"></a>

#### bpy.types.StripModifier.input_mask_strip

Strip used as mask input for the modifier

**Type:**

[`Strip`](bpy.types.Strip.md#bpy.types.Strip "bpy.types.Strip") | None

<a id="bpy.types.StripModifier.input_mask_type"></a>

#### bpy.types.StripModifier.input_mask_type

Type of input data used for mask (default `'STRIP'`)

- `STRIP`
  Strip – Use sequencer strip as mask input.
- `ID`
  Mask – Use mask ID as mask input.

**Type:**

Literal[‘STRIP’, ‘ID’]

<a id="bpy.types.StripModifier.is_active"></a>

#### bpy.types.StripModifier.is_active

This modifier is active (default False)

**Type:**

bool

<a id="bpy.types.StripModifier.mask_time"></a>

#### bpy.types.StripModifier.mask_time

Time to use for the Mask animation (default `'RELATIVE'`)

- `RELATIVE`
  Relative – Mask animation is offset to start of strip.
- `ABSOLUTE`
  Absolute – Mask animation is in sync with scene frame.

**Type:**

Literal[‘RELATIVE’, ‘ABSOLUTE’]

<a id="bpy.types.StripModifier.mute"></a>

#### bpy.types.StripModifier.mute

Mute this modifier (default False)

**Type:**

bool

<a id="bpy.types.StripModifier.name"></a>

#### bpy.types.StripModifier.name

(default “”, never None)

**Type:**

str

<a id="bpy.types.StripModifier.show_expanded"></a>

#### bpy.types.StripModifier.show_expanded

Mute expanded settings for the modifier (default False)

**Type:**

bool

<a id="bpy.types.StripModifier.show_preview"></a>

#### bpy.types.StripModifier.show_preview

Display modifier in preview (default False)

**Type:**

bool

<a id="bpy.types.StripModifier.type"></a>

#### bpy.types.StripModifier.type

(default `'BRIGHT_CONTRAST'`, readonly)

**Type:**

Literal[[Strip Modifier Type Items](bpy_types_enum_items/strip_modifier_type_items.md#rna-enum-strip-modifier-type-items)]

<a id="bpy.types.StripModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.StripModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.StripModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.StripModifier.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([type](#bpy.types.StripModifier.type "bpy.types.StripModifier.type") | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

[type](#bpy.types.StripModifier.type "bpy.types.StripModifier.type")

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
| - `bpy.context.strip_modifier` - [`Strip.modifiers`](bpy.types.Strip.md#bpy.types.Strip.modifiers "bpy.types.Strip.modifiers") - [`StripModifiers.active`](bpy.types.StripModifiers.md#bpy.types.StripModifiers.active "bpy.types.StripModifiers.active") | - [`StripModifiers.new`](bpy.types.StripModifiers.md#bpy.types.StripModifiers.new "bpy.types.StripModifiers.new") - [`StripModifiers.remove`](bpy.types.StripModifiers.md#bpy.types.StripModifiers.remove "bpy.types.StripModifiers.remove") |
