<!-- source: Blender Python API reference 5.2 / bpy.types.SpeedControlStrip.html -->

<a id="speedcontrolstrip-effectstrip"></a>

# SpeedControlStrip(EffectStrip)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Strip`](bpy.types.Strip.md#bpy.types.Strip "bpy.types.Strip"), [`EffectStrip`](bpy.types.EffectStrip.md#bpy.types.EffectStrip "bpy.types.EffectStrip")

<a id="bpy.types.SpeedControlStrip"></a>

### class bpy.types.SpeedControlStrip(EffectStrip)

Sequence strip to control the speed of other strips

<a id="bpy.types.SpeedControlStrip.input_1"></a>

#### bpy.types.SpeedControlStrip.input_1

First input for the effect strip (never None)

**Type:**

[`Strip`](bpy.types.Strip.md#bpy.types.Strip "bpy.types.Strip")

<a id="bpy.types.SpeedControlStrip.input_count"></a>

#### bpy.types.SpeedControlStrip.input_count

(in [0, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.SpeedControlStrip.speed_control"></a>

#### bpy.types.SpeedControlStrip.speed_control

Speed control method (default `'STRETCH'`)

- `STRETCH`
  Stretch – Adjust input playback speed, so its duration fits strip length.
- `MULTIPLY`
  Multiply – Multiply with the speed factor.
- `FRAME_NUMBER`
  Frame Number – Frame number of the input strip.
- `LENGTH`
  Length – Percentage of the input strip length.

**Type:**

Literal[‘STRETCH’, ‘MULTIPLY’, ‘FRAME_NUMBER’, ‘LENGTH’]

<a id="bpy.types.SpeedControlStrip.speed_factor"></a>

#### bpy.types.SpeedControlStrip.speed_factor

Multiply the current speed of the strip with this number or remap current frame to this frame (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.SpeedControlStrip.speed_frame_number"></a>

#### bpy.types.SpeedControlStrip.speed_frame_number

Frame number of input strip (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.SpeedControlStrip.speed_length"></a>

#### bpy.types.SpeedControlStrip.speed_length

Percentage of input strip length (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.SpeedControlStrip.use_frame_interpolate"></a>

#### bpy.types.SpeedControlStrip.use_frame_interpolate

Do crossfade blending between current and next frame (default False)

**Type:**

bool

<a id="bpy.types.SpeedControlStrip.bl_rna_get_subclass"></a>

#### classmethod bpy.types.SpeedControlStrip.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.SpeedControlStrip.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.SpeedControlStrip.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, Strip.name, Strip.type, Strip.select, Strip.select_left_handle, Strip.select_right_handle, Strip.mute, Strip.lock, Strip.frame_final_duration, Strip.duration, Strip.frame_duration, Strip.content_duration, Strip.frame_start, Strip.content_start, Strip.content_end, Strip.frame_final_start, Strip.left_handle, Strip.frame_final_end, Strip.right_handle, Strip.frame_offset_start, Strip.left_handle_offset, Strip.frame_offset_end, Strip.right_handle_offset, Strip.channel, Strip.blend_type, Strip.blend_alpha, Strip.effect_fader, Strip.use_default_fade, Strip.color_tag, Strip.modifiers, Strip.show_retiming_keys, Strip.connections, EffectStrip.use_deinterlace, EffectStrip.alpha_mode, EffectStrip.use_flip_x, EffectStrip.use_flip_y, EffectStrip.use_float, EffectStrip.use_reverse_frames, EffectStrip.color_multiply, EffectStrip.multiply_alpha, EffectStrip.color_saturation, EffectStrip.strobe, EffectStrip.transform, EffectStrip.crop, EffectStrip.use_proxy, EffectStrip.proxy

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, Strip.bl_system_properties_get, Strip.strip_elem_from_frame, Strip.swap, Strip.move_to_meta, Strip.parent_meta, Strip.invalidate_cache, Strip.split, Strip.bl_rna_get_subclass, Strip.bl_rna_get_subclass_py, EffectStrip.bl_rna_get_subclass, EffectStrip.bl_rna_get_subclass_py
