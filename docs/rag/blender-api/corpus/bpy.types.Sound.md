<!-- source: Blender Python API reference 5.2 / bpy.types.Sound.html -->

<a id="sound-id"></a>

# Sound(ID)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")

<a id="bpy.types.Sound"></a>

### class bpy.types.Sound(ID)

Sound data-block referencing an external or packed sound file

<a id="bpy.types.Sound.channels"></a>

#### bpy.types.Sound.channels

Definition of audio channels (default `'INVALID'`, readonly)

- `INVALID`
  Invalid – Invalid.
- `MONO`
  Mono – Mono.
- `STEREO`
  Stereo – Stereo.
- `STEREO_LFE`
  Stereo LFE – Stereo FX.
- `CHANNELS_4`
  4 Channels – 4 Channels.
- `CHANNELS_5`
  5 Channels – 5 Channels.
- `SURROUND_51`
  5.1 Surround – 5.1 Surround.
- `SURROUND_61`
  6.1 Surround – 6.1 Surround.
- `SURROUND_71`
  7.1 Surround – 7.1 Surround.

**Type:**

Literal[‘INVALID’, ‘MONO’, ‘STEREO’, ‘STEREO_LFE’, ‘CHANNELS_4’, ‘CHANNELS_5’, ‘SURROUND_51’, ‘SURROUND_61’, ‘SURROUND_71’]

<a id="bpy.types.Sound.filepath"></a>

#### bpy.types.Sound.filepath

Sound sample file used by this Sound data-block (default “”, never None, blend relative `//` prefix supported)

**Type:**

str

<a id="bpy.types.Sound.packed_file"></a>

#### bpy.types.Sound.packed_file

(readonly)

**Type:**

[`PackedFile`](bpy.types.PackedFile.md#bpy.types.PackedFile "bpy.types.PackedFile") | None

<a id="bpy.types.Sound.samplerate"></a>

#### bpy.types.Sound.samplerate

Sample rate of the audio in Hz (in [-inf, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.Sound.use_memory_cache"></a>

#### bpy.types.Sound.use_memory_cache

The sound file is decoded and loaded into RAM (default False)

**Type:**

bool

<a id="bpy.types.Sound.use_mono"></a>

#### bpy.types.Sound.use_mono

If the file contains multiple audio channels they are rendered to a single one (default False)

**Type:**

bool

<a id="bpy.types.Sound.factory"></a>

#### bpy.types.Sound.factory

The aud.Factory object of the sound.

(readonly)

<a id="bpy.types.Sound.pack"></a>

#### bpy.types.Sound.pack()

Pack the sound into the current blend file

<a id="bpy.types.Sound.unpack"></a>

#### bpy.types.Sound.unpack(*, method='USE_LOCAL')

Unpack the sound to the samples filename

**Parameters:**

**method** (Literal[[Unpack Method Items](bpy_types_enum_items/unpack_method_items.md#rna-enum-unpack-method-items)]) – method, How to unpack (optional)

<a id="bpy.types.Sound.bl_rna_get_subclass"></a>

#### classmethod bpy.types.Sound.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.Sound.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.Sound.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, ID.name, ID.name_full, ID.id_type, ID.session_uid, ID.is_evaluated, ID.original, ID.users, ID.use_fake_user, ID.use_extra_user, ID.is_embedded_data, ID.is_linked_packed, ID.is_missing, ID.is_runtime_data, ID.is_editable, ID.tag, ID.is_library_indirect, ID.library, ID.library_weak_reference, ID.asset_data, ID.override_library, ID.preview

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, ID.bl_system_properties_get, ID.rename, ID.evaluated_get, ID.copy, ID.asset_mark, ID.asset_clear, ID.asset_generate_preview, ID.override_create, ID.override_hierarchy_create, ID.user_clear, ID.user_remap, ID.make_local, ID.user_of_id, ID.animation_data_create, ID.animation_data_clear, ID.update_tag, ID.preview_ensure, ID.bl_rna_get_subclass, ID.bl_rna_get_subclass_py

<a id="references"></a>

## References

|  |  |
| --- | --- |
| - [`BlendData.sounds`](bpy.types.BlendData.md#bpy.types.BlendData.sounds "bpy.types.BlendData.sounds") - [`BlendDataSounds.load`](bpy.types.BlendDataSounds.md#bpy.types.BlendDataSounds.load "bpy.types.BlendDataSounds.load") - [`BlendDataSounds.remove`](bpy.types.BlendDataSounds.md#bpy.types.BlendDataSounds.remove "bpy.types.BlendDataSounds.remove") - [`NodeSocketSound.default_value`](bpy.types.NodeSocketSound.md#bpy.types.NodeSocketSound.default_value "bpy.types.NodeSocketSound.default_value") | - [`NodeTreeInterfaceSocketSound.default_value`](bpy.types.NodeTreeInterfaceSocketSound.md#bpy.types.NodeTreeInterfaceSocketSound.default_value "bpy.types.NodeTreeInterfaceSocketSound.default_value") - [`SoundStrip.sound`](bpy.types.SoundStrip.md#bpy.types.SoundStrip.sound "bpy.types.SoundStrip.sound") - [`Speaker.sound`](bpy.types.Speaker.md#bpy.types.Speaker.sound "bpy.types.Speaker.sound") |
