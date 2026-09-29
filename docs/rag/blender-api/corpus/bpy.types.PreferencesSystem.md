<!-- source: Blender Python API reference 5.2 / bpy.types.PreferencesSystem.html -->

<a id="preferencessystem-bpy-struct"></a>

# PreferencesSystem(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.PreferencesSystem"></a>

### class bpy.types.PreferencesSystem(bpy_struct)

Graphics driver and operating system settings

<a id="bpy.types.PreferencesSystem.anisotropic_filter"></a>

#### bpy.types.PreferencesSystem.anisotropic_filter

Quality of anisotropic filtering (default `'FILTER_2'`)

**Type:**

Literal[‘FILTER_0’, ‘FILTER_2’, ‘FILTER_4’, ‘FILTER_8’, ‘FILTER_16’]

<a id="bpy.types.PreferencesSystem.audio_channels"></a>

#### bpy.types.PreferencesSystem.audio_channels

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

<a id="bpy.types.PreferencesSystem.audio_device"></a>

#### bpy.types.PreferencesSystem.audio_device

Audio output device (default `'None'`)

- `None`
  None – No device - there will be no audio output.

**Type:**

Literal[‘None’]

<a id="bpy.types.PreferencesSystem.audio_mixing_buffer"></a>

#### bpy.types.PreferencesSystem.audio_mixing_buffer

Number of samples used by the audio mixing buffer (default `'SAMPLES_2048'`)

- `SAMPLES_256`
  256 Samples – Set audio mixing buffer size to 256 samples.
- `SAMPLES_512`
  512 Samples – Set audio mixing buffer size to 512 samples.
- `SAMPLES_1024`
  1024 Samples – Set audio mixing buffer size to 1024 samples.
- `SAMPLES_2048`
  2048 Samples – Set audio mixing buffer size to 2048 samples.
- `SAMPLES_4096`
  4096 Samples – Set audio mixing buffer size to 4096 samples.
- `SAMPLES_8192`
  8192 Samples – Set audio mixing buffer size to 8192 samples.
- `SAMPLES_16384`
  16384 Samples – Set audio mixing buffer size to 16384 samples.
- `SAMPLES_32768`
  32768 Samples – Set audio mixing buffer size to 32768 samples.

**Type:**

Literal[‘SAMPLES_256’, ‘SAMPLES_512’, ‘SAMPLES_1024’, ‘SAMPLES_2048’, ‘SAMPLES_4096’, ‘SAMPLES_8192’, ‘SAMPLES_16384’, ‘SAMPLES_32768’]

<a id="bpy.types.PreferencesSystem.audio_sample_format"></a>

#### bpy.types.PreferencesSystem.audio_sample_format

Audio sample format (default `'FLOAT'`)

- `U8`
  8-bit Unsigned – Set audio sample format to 8-bit unsigned integer.
- `S16`
  16-bit Signed – Set audio sample format to 16-bit signed integer.
- `S24`
  24-bit Signed – Set audio sample format to 24-bit signed integer.
- `S32`
  32-bit Signed – Set audio sample format to 32-bit signed integer.
- `FLOAT`
  32-bit Float – Set audio sample format to 32-bit float.
- `DOUBLE`
  64-bit Float – Set audio sample format to 64-bit float.

**Type:**

Literal[‘U8’, ‘S16’, ‘S24’, ‘S32’, ‘FLOAT’, ‘DOUBLE’]

<a id="bpy.types.PreferencesSystem.audio_sample_rate"></a>

#### bpy.types.PreferencesSystem.audio_sample_rate

Audio sample rate (default `'RATE_48000'`)

- `RATE_44100`
  44.1 kHz – Set audio sampling rate to 44100 samples per second.
- `RATE_48000`
  48 kHz – Set audio sampling rate to 48000 samples per second.
- `RATE_96000`
  96 kHz – Set audio sampling rate to 96000 samples per second.
- `RATE_192000`
  192 kHz – Set audio sampling rate to 192000 samples per second.

**Type:**

Literal[‘RATE_44100’, ‘RATE_48000’, ‘RATE_96000’, ‘RATE_192000’]

<a id="bpy.types.PreferencesSystem.dpi"></a>

#### bpy.types.PreferencesSystem.dpi

(in [-inf, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.PreferencesSystem.geometry_nodes_stack_limit"></a>

#### bpy.types.PreferencesSystem.geometry_nodes_stack_limit

Approximate maximum size of the call stack used by Geometry Nodes. For example, this corresponds to the number of allowed nested node groups. Setting this too high can result in crashes caused by running out of stack memory. (in [1, inf], default 100)

**Type:**

int

<a id="bpy.types.PreferencesSystem.gl_clip_alpha"></a>

#### bpy.types.PreferencesSystem.gl_clip_alpha

Clip alpha below this threshold in the 3D textured view (in [0, 1], default 0.004)

**Type:**

float

<a id="bpy.types.PreferencesSystem.gl_texture_limit"></a>

#### bpy.types.PreferencesSystem.gl_texture_limit

Limit the texture size to save graphics memory (default `'CLAMP_OFF'`)

**Type:**

Literal[‘CLAMP_OFF’, ‘CLAMP_8192’, ‘CLAMP_4096’, ‘CLAMP_2048’, ‘CLAMP_1024’, ‘CLAMP_512’, ‘CLAMP_256’, ‘CLAMP_128’]

<a id="bpy.types.PreferencesSystem.gpu_backend"></a>

#### bpy.types.PreferencesSystem.gpu_backend

GPU backend to use (requires restarting Blender for changes to take effect) (default `'OPENGL'`)

- `OPENGL`
  OpenGL – Use OpenGL backend.
- `METAL`
  Metal – Use Metal backend.
- `VULKAN`
  Vulkan – Use Vulkan backend.

**Type:**

Literal[‘OPENGL’, ‘METAL’, ‘VULKAN’]

<a id="bpy.types.PreferencesSystem.gpu_preferred_device"></a>

#### bpy.types.PreferencesSystem.gpu_preferred_device

Preferred device to select during detection (requires restarting Blender for changes to take effect) (default `'AUTO'`)

- `AUTO`
  Auto – Auto detect best GPU for running Blender.

**Type:**

Literal[‘AUTO’]

<a id="bpy.types.PreferencesSystem.gpu_shader_workers"></a>

#### bpy.types.PreferencesSystem.gpu_shader_workers

Number of shader compilation threads or subprocesses, clamped at the max threads supported by the CPU (requires restarting Blender for changes to take effect). A higher number increases the RAM usage while reducing compilation time. A value of 0 will use automatic configuration. (OpenGL only) (in [0, 32], default 0)

**Type:**

int

<a id="bpy.types.PreferencesSystem.is_microsoft_store_install"></a>

#### bpy.types.PreferencesSystem.is_microsoft_store_install

Whether this blender installation is a sandboxed Microsoft Store version (default False, readonly)

**Type:**

bool

<a id="bpy.types.PreferencesSystem.legacy_compute_device_type"></a>

#### bpy.types.PreferencesSystem.legacy_compute_device_type

For backwards compatibility only (in [-inf, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.PreferencesSystem.light_ambient"></a>

#### bpy.types.PreferencesSystem.light_ambient

Color of the ambient light that uniformly lit the scene (array of 3 items, in [0, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.PreferencesSystem.memory_cache_limit"></a>

#### bpy.types.PreferencesSystem.memory_cache_limit

Memory cache limit (in megabytes) (in [0, inf], default 4096)

**Type:**

int

<a id="bpy.types.PreferencesSystem.network_connection_limit"></a>

#### bpy.types.PreferencesSystem.network_connection_limit

Limit the number of simultaneous internet connections online operations may make at once. Zero disables the limit. (in [0, 255], default 0)

**Type:**

int

<a id="bpy.types.PreferencesSystem.network_timeout"></a>

#### bpy.types.PreferencesSystem.network_timeout

The time in seconds to wait for online operations before a connection may fail with a time-out error. Zero uses the systems default. (in [0, 255], default 0)

**Type:**

int

<a id="bpy.types.PreferencesSystem.pixel_size"></a>

#### bpy.types.PreferencesSystem.pixel_size

(in [-inf, inf], default 1.0, readonly)

**Type:**

float

<a id="bpy.types.PreferencesSystem.register_all_users"></a>

#### bpy.types.PreferencesSystem.register_all_users

Make this Blender version open blend files for all users. Requires elevated privileges. (default False)

**Type:**

bool

<a id="bpy.types.PreferencesSystem.scrollback"></a>

#### bpy.types.PreferencesSystem.scrollback

Maximum number of lines to store for the console buffer (in [32, 32768], default 256)

**Type:**

int

<a id="bpy.types.PreferencesSystem.sequencer_proxy_setup"></a>

#### bpy.types.PreferencesSystem.sequencer_proxy_setup

When and how proxies are created (default `'AUTOMATIC'`)

- `MANUAL`
  Manual – Set up proxies manually.
- `AUTOMATIC`
  Automatic – Build proxies for added movie and image strips in each preview size.

**Type:**

Literal[‘MANUAL’, ‘AUTOMATIC’]

<a id="bpy.types.PreferencesSystem.shader_compilation_method"></a>

#### bpy.types.PreferencesSystem.shader_compilation_method

Compilation method used for compiling shaders in parallel. Subprocess requires a lot more RAM for each worker but might compile shaders faster on some systems. Requires restarting Blender for changes to take effect. (OpenGL only) (default `'THREAD'`)

- `THREAD`
  Thread – Use threads for compiling shaders.
- `SUBPROCESS`
  Subprocess – Use subprocesses for compiling shaders.

**Type:**

Literal[‘THREAD’, ‘SUBPROCESS’]

<a id="bpy.types.PreferencesSystem.show_panel_tabs_compact"></a>

#### bpy.types.PreferencesSystem.show_panel_tabs_compact

Display sidebar tabs in a compact size that shows icons when available (default False)

**Type:**

bool

<a id="bpy.types.PreferencesSystem.solid_lights"></a>

#### bpy.types.PreferencesSystem.solid_lights

Lights used to display objects in solid shading mode (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`UserSolidLight`](bpy.types.UserSolidLight.md#bpy.types.UserSolidLight "bpy.types.UserSolidLight")]

<a id="bpy.types.PreferencesSystem.texture_collection_rate"></a>

#### bpy.types.PreferencesSystem.texture_collection_rate

Number of seconds between each run of the GL texture garbage collector (in [1, 3600], default 60)

**Type:**

int

<a id="bpy.types.PreferencesSystem.texture_time_out"></a>

#### bpy.types.PreferencesSystem.texture_time_out

Time since last access of a GL texture in seconds after which it is freed (set to 0 to keep textures allocated) (in [0, 3600], default 120)

**Type:**

int

<a id="bpy.types.PreferencesSystem.ui_line_width"></a>

#### bpy.types.PreferencesSystem.ui_line_width

Suggested line thickness and point size in pixels, for add-ons displaying custom user interface elements, based on operating system settings and Blender UI scale (in [-inf, inf], default 1.0, readonly)

**Type:**

float

<a id="bpy.types.PreferencesSystem.ui_scale"></a>

#### bpy.types.PreferencesSystem.ui_scale

Size multiplier to use when displaying custom user interface elements, so that they are scaled correctly on screens with different DPI. This value is based on operating system DPI settings and Blender display scale. (in [-inf, inf], default 0.0, readonly)

**Type:**

float

<a id="bpy.types.PreferencesSystem.use_edit_mode_smooth_wire"></a>

#### bpy.types.PreferencesSystem.use_edit_mode_smooth_wire

Enable edit mode edge smoothing, reducing aliasing (requires restart) (default True)

**Type:**

bool

<a id="bpy.types.PreferencesSystem.use_gpu_subdivision"></a>

#### bpy.types.PreferencesSystem.use_gpu_subdivision

Enable GPU acceleration for evaluating the last subdivision surface modifiers in the stack (default True)

**Type:**

bool

<a id="bpy.types.PreferencesSystem.use_online_access"></a>

#### bpy.types.PreferencesSystem.use_online_access

Allow Blender to access the internet. Add-ons that follow this setting will only connect to the internet if enabled. However, Blender cannot prevent third-party add-ons from violating this rule. (default False)

**Type:**

bool

<a id="bpy.types.PreferencesSystem.use_overlay_smooth_wire"></a>

#### bpy.types.PreferencesSystem.use_overlay_smooth_wire

Enable overlay smooth wires, reducing aliasing (default True)

**Type:**

bool

<a id="bpy.types.PreferencesSystem.use_region_overlap"></a>

#### bpy.types.PreferencesSystem.use_region_overlap

Display tool/property regions over the main region (default True)

**Type:**

bool

<a id="bpy.types.PreferencesSystem.use_studio_light_edit"></a>

#### bpy.types.PreferencesSystem.use_studio_light_edit

View the result of the studio light editor in the viewport (default False)

**Type:**

bool

<a id="bpy.types.PreferencesSystem.vbo_collection_rate"></a>

#### bpy.types.PreferencesSystem.vbo_collection_rate

Number of seconds between each run of the GL vertex buffer object garbage collector (in [1, 3600], default 60)

**Type:**

int

<a id="bpy.types.PreferencesSystem.vbo_time_out"></a>

#### bpy.types.PreferencesSystem.vbo_time_out

Time since last access of a GL vertex buffer object in seconds after which it is freed (set to 0 to keep VBO allocated) (in [0, 3600], default 120)

**Type:**

int

<a id="bpy.types.PreferencesSystem.viewport_aa"></a>

#### bpy.types.PreferencesSystem.viewport_aa

Method of anti-aliasing in 3d viewport (default `'8'`)

- `OFF`
  No Anti-Aliasing – Scene will be rendering without any anti-aliasing.
- `FXAA`
  Single Pass Anti-Aliasing – Scene will be rendered using a single pass anti-aliasing method (FXAA).
- `5`
  5 Samples – Scene will be rendered using 5 anti-aliasing samples.
- `8`
  8 Samples – Scene will be rendered using 8 anti-aliasing samples.
- `11`
  11 Samples – Scene will be rendered using 11 anti-aliasing samples.
- `16`
  16 Samples – Scene will be rendered using 16 anti-aliasing samples.
- `32`
  32 Samples – Scene will be rendered using 32 anti-aliasing samples.

**Type:**

Literal[‘OFF’, ‘FXAA’, ‘5’, ‘8’, ‘11’, ‘16’, ‘32’]

<a id="bpy.types.PreferencesSystem.bl_rna_get_subclass"></a>

#### classmethod bpy.types.PreferencesSystem.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.PreferencesSystem.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.PreferencesSystem.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Preferences.system`](bpy.types.Preferences.md#bpy.types.Preferences.system "bpy.types.Preferences.system") |  |
