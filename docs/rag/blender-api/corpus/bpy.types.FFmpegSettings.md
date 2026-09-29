<!-- source: Blender Python API reference 5.2 / bpy.types.FFmpegSettings.html -->

<a id="ffmpegsettings-bpy-struct"></a>

# FFmpegSettings(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.FFmpegSettings"></a>

### class bpy.types.FFmpegSettings(bpy_struct)

FFmpeg related settings for the scene

<a id="bpy.types.FFmpegSettings.audio_bitrate"></a>

#### bpy.types.FFmpegSettings.audio_bitrate

Audio bitrate (kb/s) (in [32, 2048], default 192)

**Type:**

int

<a id="bpy.types.FFmpegSettings.audio_channels"></a>

#### bpy.types.FFmpegSettings.audio_channels

Audio channel count (default `'STEREO'`)

- `MONO`
  Mono – Set audio channels to mono.
- `STEREO`
  Stereo – Set audio channels to stereo.
- `SURROUND4`
  4 Channels – Set audio channels to 4 channels.
- `SURROUND51`
  5.1 Surround – Set audio channels to 5.1 surround sound.
- `SURROUND71`
  7.1 Surround – Set audio channels to 7.1 surround sound.

**Type:**

Literal[‘MONO’, ‘STEREO’, ‘SURROUND4’, ‘SURROUND51’, ‘SURROUND71’]

<a id="bpy.types.FFmpegSettings.audio_codec"></a>

#### bpy.types.FFmpegSettings.audio_codec

FFmpeg audio codec to use (default `'NONE'`)

- `NONE`
  No Audio – Disables audio output, for video-only renders.
- `AAC`
  AAC.
- `AC3`
  AC3.
- `FLAC`
  FLAC.
- `MP2`
  MP2.
- `MP3`
  MP3.
- `OPUS`
  Opus.
- `PCM`
  PCM.
- `VORBIS`
  Vorbis.

**Type:**

Literal[‘NONE’, ‘AAC’, ‘AC3’, ‘FLAC’, ‘MP2’, ‘MP3’, ‘OPUS’, ‘PCM’, ‘VORBIS’]

<a id="bpy.types.FFmpegSettings.audio_mixrate"></a>

#### bpy.types.FFmpegSettings.audio_mixrate

Audio sample rate (samples/s) (in [8000, 192000], default 48000)

**Type:**

int

<a id="bpy.types.FFmpegSettings.audio_volume"></a>

#### bpy.types.FFmpegSettings.audio_volume

Audio volume (in [0, 1], default 1.0)

**Type:**

float

<a id="bpy.types.FFmpegSettings.buffersize"></a>

#### bpy.types.FFmpegSettings.buffersize

Rate control: buffer size (kb) (in [0, 2000], default 0)

**Type:**

int

<a id="bpy.types.FFmpegSettings.codec"></a>

#### bpy.types.FFmpegSettings.codec

FFmpeg codec to use for video output (default `'H264'`)

- `NONE`
  No Video – Disables video output, for audio-only renders.
- `AV1`
  AV1.
- `H264`
  H.264.
- `H265`
  H.265 / HEVC.
- `WEBM`
  WebM / VP9.
- `DNXHD`
  DNxHD.
- `DV`
  DV.
- `FFV1`
  FFmpeg video codec #1.
- `FLASH`
  Flash Video.
- `HUFFYUV`
  HuffYUV.
- `MPEG1`
  MPEG-1.
- `MPEG2`
  MPEG-2.
- `MPEG4`
  MPEG-4 (divx).
- `PNG`
  PNG.
- `PRORES`
  ProRes.
- `QTRLE`
  QuickTime Animation.
- `THEORA`
  Theora.

**Type:**

Literal[‘NONE’, ‘AV1’, ‘H264’, ‘H265’, ‘WEBM’, ‘DNXHD’, ‘DV’, ‘FFV1’, ‘FLASH’, ‘HUFFYUV’, ‘MPEG1’, ‘MPEG2’, ‘MPEG4’, ‘PNG’, ‘PRORES’, ‘QTRLE’, ‘THEORA’]

<a id="bpy.types.FFmpegSettings.constant_rate_factor"></a>

#### bpy.types.FFmpegSettings.constant_rate_factor

Constant Rate Factor (CRF); tradeoff between video quality and file size (default `'MEDIUM'`)

- `NONE`
  Constant Bitrate – Configure constant bit rate, rather than constant output quality.
- `LOSSLESS`
  Lossless.
- `PERC_LOSSLESS`
  Perceptually Lossless.
- `HIGH`
  High Quality.
- `MEDIUM`
  Medium Quality.
- `LOW`
  Low Quality.
- `VERYLOW`
  Very Low Quality.
- `LOWEST`
  Lowest Quality.
- `CUSTOM`
  Custom Quality – Set a custom Constant Rate Factor (CRF)..

**Type:**

Literal[‘NONE’, ‘LOSSLESS’, ‘PERC_LOSSLESS’, ‘HIGH’, ‘MEDIUM’, ‘LOW’, ‘VERYLOW’, ‘LOWEST’, ‘CUSTOM’]

<a id="bpy.types.FFmpegSettings.custom_constant_rate_factor"></a>

#### bpy.types.FFmpegSettings.custom_constant_rate_factor

A smaller Constant Rate Factor (CRF) results in better video quality but larger file size. The range of allowed CRF values is dependent on the codec. (in [0, 63], default 23)

**Type:**

int

<a id="bpy.types.FFmpegSettings.ffmpeg_preset"></a>

#### bpy.types.FFmpegSettings.ffmpeg_preset

Tradeoff between encoding speed and compression ratio (default `'GOOD'`)

- `BEST`
  Slowest – Recommended if you have lots of time and want the best compression efficiency.
- `GOOD`
  Good – The default and recommended for most applications.
- `REALTIME`
  Realtime – Recommended for fast encoding.

**Type:**

Literal[‘BEST’, ‘GOOD’, ‘REALTIME’]

<a id="bpy.types.FFmpegSettings.ffmpeg_prores_profile"></a>

#### bpy.types.FFmpegSettings.ffmpeg_prores_profile

ProRes Profile (default `'422_STD'`)

**Type:**

Literal[‘422_PROXY’, ‘422_LT’, ‘422_STD’, ‘422_HQ’, ‘4444’, ‘4444_XQ’]

<a id="bpy.types.FFmpegSettings.format"></a>

#### bpy.types.FFmpegSettings.format

Output file container (default `'MKV'`)

**Type:**

Literal[‘MPEG4’, ‘MKV’, ‘WEBM’, ‘AVI’, ‘DV’, ‘FLASH’, ‘MPEG1’, ‘MPEG2’, ‘OGG’, ‘QUICKTIME’]

<a id="bpy.types.FFmpegSettings.gopsize"></a>

#### bpy.types.FFmpegSettings.gopsize

Distance between key frames, also known as GOP size; influences file size and seekability (in [0, 500], default 25)

**Type:**

int

<a id="bpy.types.FFmpegSettings.max_b_frames"></a>

#### bpy.types.FFmpegSettings.max_b_frames

Maximum number of B-frames between non-B-frames; influences file size and seekability (in [0, 16], default 0)

**Type:**

int

<a id="bpy.types.FFmpegSettings.maxrate"></a>

#### bpy.types.FFmpegSettings.maxrate

Rate control: max rate (kbit/s) (in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.FFmpegSettings.minrate"></a>

#### bpy.types.FFmpegSettings.minrate

Rate control: min rate (kbit/s) (in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.FFmpegSettings.muxrate"></a>

#### bpy.types.FFmpegSettings.muxrate

Mux rate (bits/second) (in [0, inf], default 0)

**Type:**

int

<a id="bpy.types.FFmpegSettings.packetsize"></a>

#### bpy.types.FFmpegSettings.packetsize

Mux packet size (byte) (in [0, 16384], default 0)

**Type:**

int

<a id="bpy.types.FFmpegSettings.use_autosplit"></a>

#### bpy.types.FFmpegSettings.use_autosplit

Autosplit output at 2GB boundary (default False)

**Type:**

bool

<a id="bpy.types.FFmpegSettings.use_lossless_output"></a>

#### bpy.types.FFmpegSettings.use_lossless_output

Use lossless output for video streams (default False)

**Type:**

bool

<a id="bpy.types.FFmpegSettings.use_max_b_frames"></a>

#### bpy.types.FFmpegSettings.use_max_b_frames

Set a maximum number of B-frames (default False)

**Type:**

bool

<a id="bpy.types.FFmpegSettings.video_bitrate"></a>

#### bpy.types.FFmpegSettings.video_bitrate

Video bitrate (kbit/s) (in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.FFmpegSettings.bl_rna_get_subclass"></a>

#### classmethod bpy.types.FFmpegSettings.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.FFmpegSettings.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.FFmpegSettings.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`RenderSettings.ffmpeg`](bpy.types.RenderSettings.md#bpy.types.RenderSettings.ffmpeg "bpy.types.RenderSettings.ffmpeg") |  |
