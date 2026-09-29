<!-- source: Blender Python API reference 5.2 / bpy.types.SoundStrip.html -->

<a id="soundstrip-strip"></a>

# SoundStrip(Strip)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Strip`](bpy.types.Strip.md#bpy.types.Strip "bpy.types.Strip")

<a id="bpy.types.SoundStrip"></a>

### class bpy.types.SoundStrip(Strip)

Sequence strip defining a sound to be played over a period of time

<a id="bpy.types.SoundStrip.animation_offset_end"></a>

#### bpy.types.SoundStrip.animation_offset_end

Animation end offset (trim end) (in [0, inf], default 0)

Deprecated since version 5.10: removal planned in version 6.0

Replaced by ‘.content_trim_end’.

**Type:**

int

<a id="bpy.types.SoundStrip.animation_offset_start"></a>

#### bpy.types.SoundStrip.animation_offset_start

Animation start offset (trim start) (in [0, inf], default 0)

Deprecated since version 5.10: removal planned in version 6.0

Replaced by ‘.content_trim_start’.

**Type:**

int

<a id="bpy.types.SoundStrip.content_trim_end"></a>

#### bpy.types.SoundStrip.content_trim_end

Number of frames to ignore from the end of the underlying source. The source content is trimmed, and future frames are turned into holds (in [0, inf], default 0)

**Type:**

int

<a id="bpy.types.SoundStrip.content_trim_start"></a>

#### bpy.types.SoundStrip.content_trim_start

Number of frames to ignore from the start of the underlying source. The source content is trimmed, and previous frames are turned into holds (in [0, inf], default 0)

**Type:**

int

<a id="bpy.types.SoundStrip.pan"></a>

#### bpy.types.SoundStrip.pan

Playback panning of the sound (only for Mono sources) (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.SoundStrip.pitch_correction"></a>

#### bpy.types.SoundStrip.pitch_correction

Maintain the original pitch of the audio when changing playback speed (default False)

**Type:**

bool

<a id="bpy.types.SoundStrip.retiming_keys"></a>

#### bpy.types.SoundStrip.retiming_keys

(default None, readonly)

**Type:**

[`RetimingKeys`](bpy.types.RetimingKeys.md#bpy.types.RetimingKeys "bpy.types.RetimingKeys")[[`RetimingKey`](bpy.types.RetimingKey.md#bpy.types.RetimingKey "bpy.types.RetimingKey")]

<a id="bpy.types.SoundStrip.show_waveform"></a>

#### bpy.types.SoundStrip.show_waveform

Display the audio waveform inside the strip (default False)

**Type:**

bool

<a id="bpy.types.SoundStrip.sound"></a>

#### bpy.types.SoundStrip.sound

Sound data-block used by this strip

**Type:**

[`Sound`](bpy.types.Sound.md#bpy.types.Sound "bpy.types.Sound") | None

<a id="bpy.types.SoundStrip.sound_offset"></a>

#### bpy.types.SoundStrip.sound_offset

Subframe offset of the sound source start expressed in seconds (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.SoundStrip.volume"></a>

#### bpy.types.SoundStrip.volume

Playback volume of the sound (in [0, 100], default 1.0)

**Type:**

float

<a id="bpy.types.SoundStrip.bl_rna_get_subclass"></a>

#### classmethod bpy.types.SoundStrip.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.SoundStrip.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.SoundStrip.bl_rna_get_subclass_py(id, default=None, /)

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
