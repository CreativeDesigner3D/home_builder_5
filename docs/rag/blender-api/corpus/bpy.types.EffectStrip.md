<!-- source: Blender Python API reference 5.2 / bpy.types.EffectStrip.html -->

<a id="effectstrip-strip"></a>

# EffectStrip(Strip)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Strip`](bpy.types.Strip.md#bpy.types.Strip "bpy.types.Strip")

Subclasses

- [AddStrip(EffectStrip)](bpy.types.AddStrip.md)
- [AdjustmentStrip(EffectStrip)](bpy.types.AdjustmentStrip.md)
- [AlphaOverStrip(EffectStrip)](bpy.types.AlphaOverStrip.md)
- [AlphaUnderStrip(EffectStrip)](bpy.types.AlphaUnderStrip.md)
- [ColorMixStrip(EffectStrip)](bpy.types.ColorMixStrip.md)
- [ColorStrip(EffectStrip)](bpy.types.ColorStrip.md)
- [CompositorStrip(EffectStrip)](bpy.types.CompositorStrip.md)
- [CrossStrip(EffectStrip)](bpy.types.CrossStrip.md)
- [GammaCrossStrip(EffectStrip)](bpy.types.GammaCrossStrip.md)
- [GaussianBlurStrip(EffectStrip)](bpy.types.GaussianBlurStrip.md)
- [GlowStrip(EffectStrip)](bpy.types.GlowStrip.md)
- [MulticamStrip(EffectStrip)](bpy.types.MulticamStrip.md)
- [MultiplyStrip(EffectStrip)](bpy.types.MultiplyStrip.md)
- [SpeedControlStrip(EffectStrip)](bpy.types.SpeedControlStrip.md)
- [SubtractStrip(EffectStrip)](bpy.types.SubtractStrip.md)
- [TextStrip(EffectStrip)](bpy.types.TextStrip.md)
- [WipeStrip(EffectStrip)](bpy.types.WipeStrip.md)

<a id="bpy.types.EffectStrip"></a>

### class bpy.types.EffectStrip(Strip)

Sequence strip applying an effect on the images created by other strips

<a id="bpy.types.EffectStrip.alpha_mode"></a>

#### bpy.types.EffectStrip.alpha_mode

Representation of alpha information in the RGBA pixels (default `'STRAIGHT'`)

- `STRAIGHT`
  Straight – RGB channels in transparent pixels are unaffected by the alpha channel.
- `PREMUL`
  Premultiplied – RGB channels in transparent pixels are multiplied by the alpha channel.

**Type:**

Literal[‘STRAIGHT’, ‘PREMUL’]

<a id="bpy.types.EffectStrip.color_multiply"></a>

#### bpy.types.EffectStrip.color_multiply

(in [0, 20], default 1.0)

**Type:**

float

<a id="bpy.types.EffectStrip.color_saturation"></a>

#### bpy.types.EffectStrip.color_saturation

Adjust the intensity of the input’s color (in [0, 20], default 1.0)

**Type:**

float

<a id="bpy.types.EffectStrip.crop"></a>

#### bpy.types.EffectStrip.crop

(readonly)

**Type:**

[`StripCrop`](bpy.types.StripCrop.md#bpy.types.StripCrop "bpy.types.StripCrop") | None

<a id="bpy.types.EffectStrip.multiply_alpha"></a>

#### bpy.types.EffectStrip.multiply_alpha

Multiply alpha along with color channels (default False)

**Type:**

bool

<a id="bpy.types.EffectStrip.proxy"></a>

#### bpy.types.EffectStrip.proxy

(readonly)

**Type:**

[`StripProxy`](bpy.types.StripProxy.md#bpy.types.StripProxy "bpy.types.StripProxy") | None

<a id="bpy.types.EffectStrip.strobe"></a>

#### bpy.types.EffectStrip.strobe

Only display every nth frame (in [1, 30], default 0.0)

**Type:**

float

<a id="bpy.types.EffectStrip.transform"></a>

#### bpy.types.EffectStrip.transform

(readonly)

**Type:**

[`StripTransform`](bpy.types.StripTransform.md#bpy.types.StripTransform "bpy.types.StripTransform") | None

<a id="bpy.types.EffectStrip.use_deinterlace"></a>

#### bpy.types.EffectStrip.use_deinterlace

Remove fields from video movies (default False)

**Type:**

bool

<a id="bpy.types.EffectStrip.use_flip_x"></a>

#### bpy.types.EffectStrip.use_flip_x

Flip on the X axis (default False)

**Type:**

bool

<a id="bpy.types.EffectStrip.use_flip_y"></a>

#### bpy.types.EffectStrip.use_flip_y

Flip on the Y axis (default False)

**Type:**

bool

<a id="bpy.types.EffectStrip.use_float"></a>

#### bpy.types.EffectStrip.use_float

Convert input to float data (default False)

**Type:**

bool

<a id="bpy.types.EffectStrip.use_proxy"></a>

#### bpy.types.EffectStrip.use_proxy

Use a preview proxy for this strip (default False)

**Type:**

bool

<a id="bpy.types.EffectStrip.use_reverse_frames"></a>

#### bpy.types.EffectStrip.use_reverse_frames

Reverse frame order (default False)

**Type:**

bool

<a id="bpy.types.EffectStrip.bl_rna_get_subclass"></a>

#### classmethod bpy.types.EffectStrip.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.EffectStrip.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.EffectStrip.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, Strip.name, Strip.type, Strip.select, Strip.select_left_handle, Strip.select_right_handle, Strip.mute, Strip.lock, Strip.frame_final_duration, Strip.duration, Strip.frame_duration, Strip.content_duration, Strip.frame_start, Strip.content_start, Strip.content_end, Strip.frame_final_start, Strip.left_handle, Strip.frame_final_end, Strip.right_handle, Strip.frame_offset_start, Strip.left_handle_offset, Strip.frame_offset_end, Strip.right_handle_offset, Strip.channel, Strip.blend_type, Strip.blend_alpha, Strip.effect_fader, Strip.use_default_fade, Strip.color_tag, Strip.modifiers, Strip.show_retiming_keys, Strip.connections

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, Strip.bl_system_properties_get, Strip.strip_elem_from_frame, Strip.swap, Strip.move_to_meta, Strip.parent_meta, Strip.invalidate_cache, Strip.split, Strip.bl_rna_get_subclass, Strip.bl_rna_get_subclass_py
