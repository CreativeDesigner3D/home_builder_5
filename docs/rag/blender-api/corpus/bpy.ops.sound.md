<!-- source: Blender Python API reference 5.2 / bpy.ops.sound.html -->

<a id="module-bpy.ops.sound"></a>

# Sound Operators

<a id="bpy.ops.sound.bake_animation"></a>

### bpy.ops.sound.bake_animation()

Update the audio animation cache

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sound.mixdown"></a>

### bpy.ops.sound.mixdown(*, filepath='', check_existing=True, filter_blender=False, filter_backup=False, filter_image=False, filter_movie=False, filter_python=False, filter_font=False, filter_sound=True, filter_text=False, filter_archive=False, filter_btx=False, filter_alembic=False, filter_usd=False, filter_obj=False, filter_volume=False, filter_folder=True, filter_blenlib=False, filemode=9, relative_path=True, display_type='DEFAULT', sort_method='', accuracy=1024, container='FLAC', codec='FLAC', channels='STEREO', format='S16', mixrate=48000, bitrate=192, split_channels=False)

Mix the scene’s audio to a sound file

**Parameters:**

- **filepath** (str) – File Path, Path to file (optional, never None)
- **check_existing** (bool) – Check Existing, Check and warn on overwriting existing files (optional)
- **filter_blender** (bool) – Filter .blend files, (optional)
- **filter_backup** (bool) – Filter backup .blend files, (optional)
- **filter_image** (bool) – Filter image files, (optional)
- **filter_movie** (bool) – Filter movie files, (optional)
- **filter_python** (bool) – Filter Python files, (optional)
- **filter_font** (bool) – Filter font files, (optional)
- **filter_sound** (bool) – Filter sound files, (optional)
- **filter_text** (bool) – Filter text files, (optional)
- **filter_archive** (bool) – Filter archive files, (optional)
- **filter_btx** (bool) – Filter btx files, (optional)
- **filter_alembic** (bool) – Filter Alembic files, (optional)
- **filter_usd** (bool) – Filter USD files, (optional)
- **filter_obj** (bool) – Filter OBJ files, (optional)
- **filter_volume** (bool) – Filter OpenVDB volume files, (optional)
- **filter_folder** (bool) – Filter folders, (optional)
- **filter_blenlib** (bool) – Filter Blender IDs, (optional)
- **filemode** (int) – File Browser Mode, The setting for the file browser mode to load a .blend file, a library or a special file (in [1, 9], optional)
- **relative_path** (bool) – Relative Path, Select the file relative to the blend file (optional)
- **display_type** (Literal['DEFAULT', 'LIST_VERTICAL', 'LIST_HORIZONTAL', 'THUMBNAIL']) –

  Display Type, (optional)

  - `DEFAULT`
    Default – Automatically determine display type for files.
  - `LIST_VERTICAL`
    Short List – Display files as short list.
  - `LIST_HORIZONTAL`
    Long List – Display files as a detailed list.
  - `THUMBNAIL`
    Thumbnails – Display files as thumbnails.
- **sort_method** (str) – File sorting mode, (optional)
- **accuracy** (int) – Accuracy, Sample accuracy, important for animation data (the lower the value, the more accurate) (in [1, inf], optional)
- **container** (Literal['AAC', 'AC3', 'FLAC', 'MATROSKA', 'MP2', 'MP3', 'OGG', 'WAV']) –

  Container, File format (optional)

  - `AAC`
    AAC – Advanced Audio Coding.
  - `AC3`
    AC3 – Dolby Digital ATRAC 3.
  - `FLAC`
    FLAC – Free Lossless Audio Codec.
  - `MATROSKA`
    MKV – Matroska.
  - `MP2`
    MP2 – MPEG-1 Audio Layer II.
  - `MP3`
    MP3 – MPEG-2 Audio Layer III.
  - `OGG`
    OGG – Xiph.Org Ogg Container.
  - `WAV`
    WAV – Waveform Audio File Format.
- **codec** (Literal['AAC', 'AC3', 'FLAC', 'MP2', 'MP3', 'PCM', 'VORBIS']) –

  Codec, Audio Codec (optional)

  - `AAC`
    AAC – Advanced Audio Coding.
  - `AC3`
    AC3 – Dolby Digital ATRAC 3.
  - `FLAC`
    FLAC – Free Lossless Audio Codec.
  - `MP2`
    MP2 – MPEG-1 Audio Layer II.
  - `MP3`
    MP3 – MPEG-2 Audio Layer III.
  - `PCM`
    PCM – Pulse Code Modulation (RAW).
  - `VORBIS`
    Vorbis – Xiph.Org Vorbis Codec.
- **channels** (Literal['MONO', 'STEREO', 'STEREO_LFE', 'SURROUND4', 'SURROUND5', 'SURROUND51', 'SURROUND61', 'SURROUND71']) –

  Channels, Audio channel count (optional)

  - `MONO`
    Mono – Single audio channel.
  - `STEREO`
    Stereo – Stereo audio channels.
  - `STEREO_LFE`
    Stereo LFE – Stereo with LFE channel.
  - `SURROUND4`
    4 Channels – 4 channel surround sound.
  - `SURROUND5`
    5 Channels – 5 channel surround sound.
  - `SURROUND51`
    5.1 Surround – 5.1 surround sound.
  - `SURROUND61`
    6.1 Surround – 6.1 surround sound.
  - `SURROUND71`
    7.1 Surround – 7.1 surround sound.
- **format** (Literal['U8', 'S16', 'S24', 'S32', 'F32', 'F64']) –

  Format, Sample format (optional)

  - `U8`
    U8 – 8-bit unsigned.
  - `S16`
    S16 – 16-bit signed.
  - `S24`
    S24 – 24-bit signed.
  - `S32`
    S32 – 32-bit signed.
  - `F32`
    F32 – 32-bit floating-point.
  - `F64`
    F64 – 64-bit floating-point.
- **mixrate** (int) – Sample Rate, Sample rate in samples/s (in [8000, 192000], optional)
- **bitrate** (int) – Bitrate, Bitrate in kbit/s (in [32, 512], optional)
- **split_channels** (bool) – Split channels, Each channel will be rendered into a mono file (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sound.open"></a>

### bpy.ops.sound.open(*, filepath='', hide_props_region=True, check_existing=False, filter_blender=False, filter_backup=False, filter_image=False, filter_movie=True, filter_python=False, filter_font=False, filter_sound=True, filter_text=False, filter_archive=False, filter_btx=False, filter_alembic=False, filter_usd=False, filter_obj=False, filter_volume=False, filter_folder=True, filter_blenlib=False, filemode=9, relative_path=True, show_multiview=False, use_multiview=False, display_type='DEFAULT', sort_method='', cache=False, mono=False)

Load a sound file

**Parameters:**

- **filepath** (str) – File Path, Path to file (optional, never None)
- **hide_props_region** (bool) – Hide Operator Properties, Collapse the region displaying the operator settings (optional)
- **check_existing** (bool) – Check Existing, Check and warn on overwriting existing files (optional)
- **filter_blender** (bool) – Filter .blend files, (optional)
- **filter_backup** (bool) – Filter backup .blend files, (optional)
- **filter_image** (bool) – Filter image files, (optional)
- **filter_movie** (bool) – Filter movie files, (optional)
- **filter_python** (bool) – Filter Python files, (optional)
- **filter_font** (bool) – Filter font files, (optional)
- **filter_sound** (bool) – Filter sound files, (optional)
- **filter_text** (bool) – Filter text files, (optional)
- **filter_archive** (bool) – Filter archive files, (optional)
- **filter_btx** (bool) – Filter btx files, (optional)
- **filter_alembic** (bool) – Filter Alembic files, (optional)
- **filter_usd** (bool) – Filter USD files, (optional)
- **filter_obj** (bool) – Filter OBJ files, (optional)
- **filter_volume** (bool) – Filter OpenVDB volume files, (optional)
- **filter_folder** (bool) – Filter folders, (optional)
- **filter_blenlib** (bool) – Filter Blender IDs, (optional)
- **filemode** (int) – File Browser Mode, The setting for the file browser mode to load a .blend file, a library or a special file (in [1, 9], optional)
- **relative_path** (bool) – Relative Path, Select the file relative to the blend file (optional)
- **show_multiview** (bool) – Enable Multi-View, (optional)
- **use_multiview** (bool) – Use Multi-View, (optional)
- **display_type** (Literal['DEFAULT', 'LIST_VERTICAL', 'LIST_HORIZONTAL', 'THUMBNAIL']) –

  Display Type, (optional)

  - `DEFAULT`
    Default – Automatically determine display type for files.
  - `LIST_VERTICAL`
    Short List – Display files as short list.
  - `LIST_HORIZONTAL`
    Long List – Display files as a detailed list.
  - `THUMBNAIL`
    Thumbnails – Display files as thumbnails.
- **sort_method** (str) – File sorting mode, (optional)
- **cache** (bool) – Cache, Cache the sound in memory (optional)
- **mono** (bool) – Mono, Merge all the sound’s channels into one (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sound.open_mono"></a>

### bpy.ops.sound.open_mono(*, filepath='', hide_props_region=True, check_existing=False, filter_blender=False, filter_backup=False, filter_image=False, filter_movie=True, filter_python=False, filter_font=False, filter_sound=True, filter_text=False, filter_archive=False, filter_btx=False, filter_alembic=False, filter_usd=False, filter_obj=False, filter_volume=False, filter_folder=True, filter_blenlib=False, filemode=9, relative_path=True, show_multiview=False, use_multiview=False, display_type='DEFAULT', sort_method='', cache=False, mono=True)

Load a sound file as mono

**Parameters:**

- **filepath** (str) – File Path, Path to file (optional, never None)
- **hide_props_region** (bool) – Hide Operator Properties, Collapse the region displaying the operator settings (optional)
- **check_existing** (bool) – Check Existing, Check and warn on overwriting existing files (optional)
- **filter_blender** (bool) – Filter .blend files, (optional)
- **filter_backup** (bool) – Filter backup .blend files, (optional)
- **filter_image** (bool) – Filter image files, (optional)
- **filter_movie** (bool) – Filter movie files, (optional)
- **filter_python** (bool) – Filter Python files, (optional)
- **filter_font** (bool) – Filter font files, (optional)
- **filter_sound** (bool) – Filter sound files, (optional)
- **filter_text** (bool) – Filter text files, (optional)
- **filter_archive** (bool) – Filter archive files, (optional)
- **filter_btx** (bool) – Filter btx files, (optional)
- **filter_alembic** (bool) – Filter Alembic files, (optional)
- **filter_usd** (bool) – Filter USD files, (optional)
- **filter_obj** (bool) – Filter OBJ files, (optional)
- **filter_volume** (bool) – Filter OpenVDB volume files, (optional)
- **filter_folder** (bool) – Filter folders, (optional)
- **filter_blenlib** (bool) – Filter Blender IDs, (optional)
- **filemode** (int) – File Browser Mode, The setting for the file browser mode to load a .blend file, a library or a special file (in [1, 9], optional)
- **relative_path** (bool) – Relative Path, Select the file relative to the blend file (optional)
- **show_multiview** (bool) – Enable Multi-View, (optional)
- **use_multiview** (bool) – Use Multi-View, (optional)
- **display_type** (Literal['DEFAULT', 'LIST_VERTICAL', 'LIST_HORIZONTAL', 'THUMBNAIL']) –

  Display Type, (optional)

  - `DEFAULT`
    Default – Automatically determine display type for files.
  - `LIST_VERTICAL`
    Short List – Display files as short list.
  - `LIST_HORIZONTAL`
    Long List – Display files as a detailed list.
  - `THUMBNAIL`
    Thumbnails – Display files as thumbnails.
- **sort_method** (str) – File sorting mode, (optional)
- **cache** (bool) – Cache, Cache the sound in memory (optional)
- **mono** (bool) – Mono, Mixdown the sound to mono (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sound.pack"></a>

### bpy.ops.sound.pack()

Pack the sound into the current blend file

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sound.unpack"></a>

### bpy.ops.sound.unpack(*, method='USE_LOCAL', id='')

Unpack the sound to the samples filename

**Parameters:**

- **method** (Literal[[Unpack Method Items](bpy_types_enum_items/unpack_method_items.md#rna-enum-unpack-method-items)]) – Method, How to unpack (optional)
- **id** (str) – Sound Name, Sound data-block name to unpack (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sound.update_animation_flags"></a>

### bpy.ops.sound.update_animation_flags()

Update animation flags

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]
