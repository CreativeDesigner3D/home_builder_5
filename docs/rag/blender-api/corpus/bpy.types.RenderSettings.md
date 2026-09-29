<!-- source: Blender Python API reference 5.2 / bpy.types.RenderSettings.html -->

<a id="rendersettings-bpy-struct"></a>

# RenderSettings(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.RenderSettings"></a>

### class bpy.types.RenderSettings(bpy_struct)

Rendering settings for a Scene data-block

<a id="bpy.types.RenderSettings.anisotropic_filter"></a>

#### bpy.types.RenderSettings.anisotropic_filter

Quality of anisotropic filtering in materials (default `'FILTER_2'`)

- `FILTER_0`
  Off – Turn off anisotropic filtering.
- `FILTER_2`
  2× – Use 2 samples for anisotropic filtering.
- `FILTER_4`
  4× – Use 4 samples for anisotropic filtering.
- `FILTER_8`
  8× – Use 8 samples for anisotropic filtering.
- `FILTER_16`
  16× – Use 16 samples for anisotropic filtering.

**Type:**

Literal[‘FILTER_0’, ‘FILTER_2’, ‘FILTER_4’, ‘FILTER_8’, ‘FILTER_16’]

<a id="bpy.types.RenderSettings.bake"></a>

#### bpy.types.RenderSettings.bake

(readonly, never None)

**Type:**

[`BakeSettings`](bpy.types.BakeSettings.md#bpy.types.BakeSettings "bpy.types.BakeSettings")

<a id="bpy.types.RenderSettings.border_max_x"></a>

#### bpy.types.RenderSettings.border_max_x

Maximum X value for the render region (in [0, 1], default 1.0)

**Type:**

float

<a id="bpy.types.RenderSettings.border_max_y"></a>

#### bpy.types.RenderSettings.border_max_y

Maximum Y value for the render region (in [0, 1], default 1.0)

**Type:**

float

<a id="bpy.types.RenderSettings.border_min_x"></a>

#### bpy.types.RenderSettings.border_min_x

Minimum X value for the render region (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.RenderSettings.border_min_y"></a>

#### bpy.types.RenderSettings.border_min_y

Minimum Y value for the render region (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.RenderSettings.compositor_denoise_device"></a>

#### bpy.types.RenderSettings.compositor_denoise_device

The device to use to process the denoise nodes in the compositor (default `'AUTO'`)

- `AUTO`
  Auto – Use the same device used by the compositor to process the denoise node.
- `CPU`
  CPU – Use the CPU to process the denoise node.
- `GPU`
  GPU – Use the GPU to process the denoise node if available, otherwise fallback to CPU.

**Type:**

Literal[‘AUTO’, ‘CPU’, ‘GPU’]

<a id="bpy.types.RenderSettings.compositor_denoise_final_quality"></a>

#### bpy.types.RenderSettings.compositor_denoise_final_quality

The quality used by denoise nodes during the compositing of final renders if the nodes’ quality option is set to Follow Scene (default `'HIGH'`)

- `HIGH`
  High – High quality.
- `BALANCED`
  Balanced – Balanced between performance and quality.
- `FAST`
  Fast – High performance.

**Type:**

Literal[‘HIGH’, ‘BALANCED’, ‘FAST’]

<a id="bpy.types.RenderSettings.compositor_denoise_preview_quality"></a>

#### bpy.types.RenderSettings.compositor_denoise_preview_quality

The quality used by denoise nodes during viewport and interactive compositing if the nodes’ quality option is set to Follow Scene (default `'BALANCED'`)

- `HIGH`
  High – High quality.
- `BALANCED`
  Balanced – Balanced between performance and quality.
- `FAST`
  Fast – High performance.

**Type:**

Literal[‘HIGH’, ‘BALANCED’, ‘FAST’]

<a id="bpy.types.RenderSettings.compositor_device"></a>

#### bpy.types.RenderSettings.compositor_device

Set how compositing is executed (default `'GPU'`)

**Type:**

Literal[‘CPU’, ‘GPU’]

<a id="bpy.types.RenderSettings.compositor_precision"></a>

#### bpy.types.RenderSettings.compositor_precision

The precision of compositor intermediate result (default `'AUTO'`)

- `AUTO`
  Auto – Full precision for final renders, half precision otherwise.
- `FULL`
  Full – Full precision.

**Type:**

Literal[‘AUTO’, ‘FULL’]

<a id="bpy.types.RenderSettings.dither_intensity"></a>

#### bpy.types.RenderSettings.dither_intensity

Amount of dithering noise added to the rendered image to break up banding (in [0, inf], default 1.0)

**Type:**

float

<a id="bpy.types.RenderSettings.engine"></a>

#### bpy.types.RenderSettings.engine

Engine to use for rendering (default `'BLENDER_EEVEE'`)

**Type:**

Literal[‘BLENDER_EEVEE’]

<a id="bpy.types.RenderSettings.ffmpeg"></a>

#### bpy.types.RenderSettings.ffmpeg

FFmpeg related settings for the scene (readonly)

**Type:**

[`FFmpegSettings`](bpy.types.FFmpegSettings.md#bpy.types.FFmpegSettings "bpy.types.FFmpegSettings") | None

<a id="bpy.types.RenderSettings.file_extension"></a>

#### bpy.types.RenderSettings.file_extension

The file extension used for saving renders (default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.RenderSettings.filepath"></a>

#### bpy.types.RenderSettings.filepath

Directory/name to save animations, # characters define the position and padding of frame numbers (default “//”, never None, blend relative `//` prefix supported, Supports [template expressions](https://docs.blender.org/manual/en/5.2/files/file_paths.html#path-templates))

**Type:**

str

<a id="bpy.types.RenderSettings.film_transparent"></a>

#### bpy.types.RenderSettings.film_transparent

World background is transparent, for compositing the render over another background (default False)

**Type:**

bool

<a id="bpy.types.RenderSettings.filter_size"></a>

#### bpy.types.RenderSettings.filter_size

Width over which the reconstruction filter combines samples (in [0, 500], default 1.5)

**Type:**

float

<a id="bpy.types.RenderSettings.fps"></a>

#### bpy.types.RenderSettings.fps

Framerate, expressed in frames per second (in [1, 32767], default 24)

**Type:**

int

<a id="bpy.types.RenderSettings.fps_base"></a>

#### bpy.types.RenderSettings.fps_base

Framerate base (in [1e-05, 1e+06], default 1.0)

**Type:**

float

<a id="bpy.types.RenderSettings.frame_map_new"></a>

#### bpy.types.RenderSettings.frame_map_new

How many frames the Map Old will last (in [1, 900], default 100)

**Type:**

int

<a id="bpy.types.RenderSettings.frame_map_old"></a>

#### bpy.types.RenderSettings.frame_map_old

Old mapping value in frames (in [1, 900], default 100)

**Type:**

int

<a id="bpy.types.RenderSettings.hair_subdiv"></a>

#### bpy.types.RenderSettings.hair_subdiv

Additional subdivision along the curves (in [0, 3], default 0)

**Type:**

int

<a id="bpy.types.RenderSettings.hair_type"></a>

#### bpy.types.RenderSettings.hair_type

Curves shape type (default `'STRAND'`)

**Type:**

Literal[‘STRAND’, ‘STRIP’, ‘CYLINDER’]

<a id="bpy.types.RenderSettings.has_multiple_engines"></a>

#### bpy.types.RenderSettings.has_multiple_engines

More than one rendering engine is available (default False, readonly)

**Type:**

bool

<a id="bpy.types.RenderSettings.image_settings"></a>

#### bpy.types.RenderSettings.image_settings

(readonly, never None)

**Type:**

[`ImageFormatSettings`](bpy.types.ImageFormatSettings.md#bpy.types.ImageFormatSettings "bpy.types.ImageFormatSettings")

<a id="bpy.types.RenderSettings.is_movie_format"></a>

#### bpy.types.RenderSettings.is_movie_format

When true the format is a movie (default False, readonly)

**Type:**

bool

<a id="bpy.types.RenderSettings.line_thickness"></a>

#### bpy.types.RenderSettings.line_thickness

Line thickness in pixels (in [0, 10000], default 1.0)

**Type:**

float

<a id="bpy.types.RenderSettings.line_thickness_mode"></a>

#### bpy.types.RenderSettings.line_thickness_mode

Line thickness mode for Freestyle line drawing (default `'ABSOLUTE'`)

- `ABSOLUTE`
  Absolute – Specify unit line thickness in pixels.
- `RELATIVE`
  Relative – Unit line thickness is scaled by the proportion of the present vertical image resolution to 480 pixels.

**Type:**

Literal[‘ABSOLUTE’, ‘RELATIVE’]

<a id="bpy.types.RenderSettings.metadata_input"></a>

#### bpy.types.RenderSettings.metadata_input

Where to take the metadata from (default `'SCENE'`)

- `SCENE`
  Scene – Use metadata from the current scene.
- `STRIPS`
  Sequencer Strips – Use metadata from the strips in the sequencer.

**Type:**

Literal[‘SCENE’, ‘STRIPS’]

<a id="bpy.types.RenderSettings.motion_blur_position"></a>

#### bpy.types.RenderSettings.motion_blur_position

Offset for the shutter’s time interval, allows to change the motion blur trails (default `'CENTER'`)

- `START`
  Start on Frame – The shutter opens at the current frame.
- `CENTER`
  Center on Frame – The shutter is open during the current frame.
- `END`
  End on Frame – The shutter closes at the current frame.

**Type:**

Literal[‘START’, ‘CENTER’, ‘END’]

<a id="bpy.types.RenderSettings.motion_blur_shutter"></a>

#### bpy.types.RenderSettings.motion_blur_shutter

Time taken in frames between shutter open and close (in [0, inf], default 0.5)

**Type:**

float

<a id="bpy.types.RenderSettings.motion_blur_shutter_curve"></a>

#### bpy.types.RenderSettings.motion_blur_shutter_curve

Curve defining the shutter’s openness over time (readonly)

**Type:**

[`CurveMapping`](bpy.types.CurveMapping.md#bpy.types.CurveMapping "bpy.types.CurveMapping") | None

<a id="bpy.types.RenderSettings.pixel_aspect_x"></a>

#### bpy.types.RenderSettings.pixel_aspect_x

Horizontal aspect ratio - for anamorphic or non-square pixel output (in [1, 200], default 1.0)

**Type:**

float

<a id="bpy.types.RenderSettings.pixel_aspect_y"></a>

#### bpy.types.RenderSettings.pixel_aspect_y

Vertical aspect ratio - for anamorphic or non-square pixel output (in [1, 200], default 1.0)

**Type:**

float

<a id="bpy.types.RenderSettings.ppm_base"></a>

#### bpy.types.RenderSettings.ppm_base

The base unit for pixels per meter. (in [1e-05, 1e+06], default 0.0254)

**Type:**

float

<a id="bpy.types.RenderSettings.ppm_factor"></a>

#### bpy.types.RenderSettings.ppm_factor

The pixel density meta-data written to supported image formats. This value is multiplied by the PPM-base which defines the unit (typically inches or meters) (in [1e-05, 1e+06], default 72.0)

**Type:**

float

<a id="bpy.types.RenderSettings.preview_pixel_size"></a>

#### bpy.types.RenderSettings.preview_pixel_size

Pixel size for viewport rendering (default `'AUTO'`)

- `AUTO`
  Automatic – Automatic pixel size, depends on the user interface scale.
- `1`
  1× – Render at full resolution.
- `2`
  2× – Render at 50% resolution.
- `4`
  4× – Render at 25% resolution.
- `8`
  8× – Render at 12.5% resolution.

**Type:**

Literal[‘AUTO’, ‘1’, ‘2’, ‘4’, ‘8’]

<a id="bpy.types.RenderSettings.resolution_percentage"></a>

#### bpy.types.RenderSettings.resolution_percentage

Percentage scale for render resolution (in [1, 32767], default 100)

**Type:**

int

<a id="bpy.types.RenderSettings.resolution_x"></a>

#### bpy.types.RenderSettings.resolution_x

Number of horizontal pixels in the rendered image (in [4, 65536], default 1920)

**Type:**

int

<a id="bpy.types.RenderSettings.resolution_y"></a>

#### bpy.types.RenderSettings.resolution_y

Number of vertical pixels in the rendered image (in [4, 65536], default 1080)

**Type:**

int

<a id="bpy.types.RenderSettings.save_output"></a>

#### bpy.types.RenderSettings.save_output

Write frames to disk for animation renders (default True)

**Type:**

bool

<a id="bpy.types.RenderSettings.sequencer_gl_preview"></a>

#### bpy.types.RenderSettings.sequencer_gl_preview

Display method used in the sequencer view (default `'SOLID'`)

**Type:**

Literal[[Shading Type Items](bpy_types_enum_items/shading_type_items.md#rna-enum-shading-type-items)]

<a id="bpy.types.RenderSettings.simplify_child_particles"></a>

#### bpy.types.RenderSettings.simplify_child_particles

Global child particles percentage (in [0, 1], default 1.0)

**Type:**

float

<a id="bpy.types.RenderSettings.simplify_child_particles_render"></a>

#### bpy.types.RenderSettings.simplify_child_particles_render

Global child particles percentage during rendering (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.RenderSettings.simplify_gpencil"></a>

#### bpy.types.RenderSettings.simplify_gpencil

Simplify Grease Pencil drawing (default False)

**Type:**

bool

<a id="bpy.types.RenderSettings.simplify_gpencil_antialiasing"></a>

#### bpy.types.RenderSettings.simplify_gpencil_antialiasing

Use Antialiasing to smooth stroke edges (default True)

**Type:**

bool

<a id="bpy.types.RenderSettings.simplify_gpencil_modifier"></a>

#### bpy.types.RenderSettings.simplify_gpencil_modifier

Display modifiers (default True)

**Type:**

bool

<a id="bpy.types.RenderSettings.simplify_gpencil_onplay"></a>

#### bpy.types.RenderSettings.simplify_gpencil_onplay

Simplify Grease Pencil only during animation playback (default False)

**Type:**

bool

<a id="bpy.types.RenderSettings.simplify_gpencil_shader_fx"></a>

#### bpy.types.RenderSettings.simplify_gpencil_shader_fx

Display Shader Effects (default True)

**Type:**

bool

<a id="bpy.types.RenderSettings.simplify_gpencil_tint"></a>

#### bpy.types.RenderSettings.simplify_gpencil_tint

Display layer tint (default True)

**Type:**

bool

<a id="bpy.types.RenderSettings.simplify_gpencil_view_fill"></a>

#### bpy.types.RenderSettings.simplify_gpencil_view_fill

Display fill strokes in the viewport (default True)

**Type:**

bool

<a id="bpy.types.RenderSettings.simplify_subdivision"></a>

#### bpy.types.RenderSettings.simplify_subdivision

Global maximum subdivision level (in [0, 32767], default 6)

**Type:**

int

<a id="bpy.types.RenderSettings.simplify_subdivision_render"></a>

#### bpy.types.RenderSettings.simplify_subdivision_render

Global maximum subdivision level during rendering (in [0, 32767], default 0)

**Type:**

int

<a id="bpy.types.RenderSettings.simplify_volumes"></a>

#### bpy.types.RenderSettings.simplify_volumes

Resolution percentage of volume objects in viewport (in [0, 1], default 1.0)

**Type:**

float

<a id="bpy.types.RenderSettings.stamp_background"></a>

#### bpy.types.RenderSettings.stamp_background

Color to use behind stamp text (array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.25))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.RenderSettings.stamp_font_size"></a>

#### bpy.types.RenderSettings.stamp_font_size

Size of the font used when rendering stamp text (in [8, 64], default 12)

**Type:**

int

<a id="bpy.types.RenderSettings.stamp_foreground"></a>

#### bpy.types.RenderSettings.stamp_foreground

Color to use for stamp text (array of 4 items, in [0, 1], default (0.8, 0.8, 0.8, 1.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.RenderSettings.stamp_note_text"></a>

#### bpy.types.RenderSettings.stamp_note_text

Custom text to appear in the stamp note (default “”, never None)

**Type:**

str

<a id="bpy.types.RenderSettings.stereo_views"></a>

#### bpy.types.RenderSettings.stereo_views

(default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`SceneRenderView`](bpy.types.SceneRenderView.md#bpy.types.SceneRenderView "bpy.types.SceneRenderView")]

<a id="bpy.types.RenderSettings.threads"></a>

#### bpy.types.RenderSettings.threads

Maximum number of CPU cores to use simultaneously while rendering (for multi-core/CPU systems) (in [1, 1024], default 1)

**Type:**

int

<a id="bpy.types.RenderSettings.threads_mode"></a>

#### bpy.types.RenderSettings.threads_mode

Determine the amount of render threads used (default `'AUTO'`)

- `AUTO`
  Auto-Detect – Automatically determine the number of threads, based on CPUs.
- `FIXED`
  Fixed – Manually determine the number of threads.

**Type:**

Literal[‘AUTO’, ‘FIXED’]

<a id="bpy.types.RenderSettings.use_auto_generate_texture_cache"></a>

#### bpy.types.RenderSettings.use_auto_generate_texture_cache

Automatically create tx files from image files when rendering, if the files do not exist or are outdated. The path to store the texture cache files is configured in the preferences (default False)

**Type:**

bool

<a id="bpy.types.RenderSettings.use_border"></a>

#### bpy.types.RenderSettings.use_border

Render a user-defined render region, within the frame size (default False)

**Type:**

bool

<a id="bpy.types.RenderSettings.use_compositing"></a>

#### bpy.types.RenderSettings.use_compositing

Process the render result through the compositing pipeline, if a compositing node group is assigned to the scene (default True)

**Type:**

bool

<a id="bpy.types.RenderSettings.use_crop_to_border"></a>

#### bpy.types.RenderSettings.use_crop_to_border

Crop the rendered frame to the defined render region size (default False)

**Type:**

bool

<a id="bpy.types.RenderSettings.use_file_extension"></a>

#### bpy.types.RenderSettings.use_file_extension

Add the file format extensions to the rendered file name (eg: filename + .jpg) (default True)

**Type:**

bool

<a id="bpy.types.RenderSettings.use_freestyle"></a>

#### bpy.types.RenderSettings.use_freestyle

Draw stylized strokes using Freestyle (default False)

**Type:**

bool

<a id="bpy.types.RenderSettings.use_high_quality_normals"></a>

#### bpy.types.RenderSettings.use_high_quality_normals

Use high quality tangent space at the cost of lower performance (default False)

**Type:**

bool

<a id="bpy.types.RenderSettings.use_lock_interface"></a>

#### bpy.types.RenderSettings.use_lock_interface

Lock interface during rendering in favor of giving more memory to the renderer (default False)

**Type:**

bool

<a id="bpy.types.RenderSettings.use_motion_blur"></a>

#### bpy.types.RenderSettings.use_motion_blur

Use multi-sampled 3D scene motion blur (default False)

**Type:**

bool

<a id="bpy.types.RenderSettings.use_multiview"></a>

#### bpy.types.RenderSettings.use_multiview

Use multiple views in the scene (default False)

**Type:**

bool

<a id="bpy.types.RenderSettings.use_overwrite"></a>

#### bpy.types.RenderSettings.use_overwrite

Overwrite existing files while rendering (default True)

**Type:**

bool

<a id="bpy.types.RenderSettings.use_persistent_data"></a>

#### bpy.types.RenderSettings.use_persistent_data

Keep render data around for faster re-renders and animation renders, at the cost of increased memory usage (default False)

**Type:**

bool

<a id="bpy.types.RenderSettings.use_placeholder"></a>

#### bpy.types.RenderSettings.use_placeholder

Create empty placeholder files while rendering frames (similar to Unix ‘touch’) (default False)

**Type:**

bool

<a id="bpy.types.RenderSettings.use_render_cache"></a>

#### bpy.types.RenderSettings.use_render_cache

Save render cache to EXR files (useful for heavy compositing, Note: affects indirectly rendered scenes) (default False)

**Type:**

bool

<a id="bpy.types.RenderSettings.use_sequencer"></a>

#### bpy.types.RenderSettings.use_sequencer

Process the render (and composited) result through the video sequence editor pipeline, if sequencer strips exist (default True)

**Type:**

bool

<a id="bpy.types.RenderSettings.use_sequencer_override_scene_strip"></a>

#### bpy.types.RenderSettings.use_sequencer_override_scene_strip

Use Workbench render and world settings from the sequencer scene, instead of each strip’s scene (default False)

**Type:**

bool

<a id="bpy.types.RenderSettings.use_simplify"></a>

#### bpy.types.RenderSettings.use_simplify

Enable simplification of scene for quicker preview renders (default False)

**Type:**

bool

<a id="bpy.types.RenderSettings.use_simplify_normals"></a>

#### bpy.types.RenderSettings.use_simplify_normals

Skip computing custom normals and face corner normals for displaying meshes in the viewport (default False)

**Type:**

bool

<a id="bpy.types.RenderSettings.use_single_layer"></a>

#### bpy.types.RenderSettings.use_single_layer

Only render the active layer. Only affects rendering from the interface, ignored for rendering from command line. (default False)

**Type:**

bool

<a id="bpy.types.RenderSettings.use_spherical_stereo"></a>

#### bpy.types.RenderSettings.use_spherical_stereo

Active render engine supports spherical stereo rendering (default False, readonly)

**Type:**

bool

<a id="bpy.types.RenderSettings.use_stamp"></a>

#### bpy.types.RenderSettings.use_stamp

Render the stamp info text in the rendered image (default False)

**Type:**

bool

<a id="bpy.types.RenderSettings.use_stamp_camera"></a>

#### bpy.types.RenderSettings.use_stamp_camera

Include the name of the active camera in image metadata (default True)

**Type:**

bool

<a id="bpy.types.RenderSettings.use_stamp_date"></a>

#### bpy.types.RenderSettings.use_stamp_date

Include the current date in image/video metadata (default True)

**Type:**

bool

<a id="bpy.types.RenderSettings.use_stamp_filename"></a>

#### bpy.types.RenderSettings.use_stamp_filename

Include the .blend filename in image/video metadata (default True)

**Type:**

bool

<a id="bpy.types.RenderSettings.use_stamp_frame"></a>

#### bpy.types.RenderSettings.use_stamp_frame

Include the frame number in image metadata (default True)

**Type:**

bool

<a id="bpy.types.RenderSettings.use_stamp_frame_range"></a>

#### bpy.types.RenderSettings.use_stamp_frame_range

Include the rendered frame range in image/video metadata (default False)

**Type:**

bool

<a id="bpy.types.RenderSettings.use_stamp_hostname"></a>

#### bpy.types.RenderSettings.use_stamp_hostname

Include the hostname of the machine that rendered the frame (default False)

**Type:**

bool

<a id="bpy.types.RenderSettings.use_stamp_labels"></a>

#### bpy.types.RenderSettings.use_stamp_labels

Display stamp labels (“Camera” in front of camera name, etc.) (default True)

**Type:**

bool

<a id="bpy.types.RenderSettings.use_stamp_lens"></a>

#### bpy.types.RenderSettings.use_stamp_lens

Include the active camera’s lens in image metadata (default False)

**Type:**

bool

<a id="bpy.types.RenderSettings.use_stamp_marker"></a>

#### bpy.types.RenderSettings.use_stamp_marker

Include the name of the last marker in image metadata (default False)

**Type:**

bool

<a id="bpy.types.RenderSettings.use_stamp_memory"></a>

#### bpy.types.RenderSettings.use_stamp_memory

Include the peak memory usage in image metadata (default True)

**Type:**

bool

<a id="bpy.types.RenderSettings.use_stamp_note"></a>

#### bpy.types.RenderSettings.use_stamp_note

Include a custom note in image/video metadata (default False)

**Type:**

bool

<a id="bpy.types.RenderSettings.use_stamp_render_time"></a>

#### bpy.types.RenderSettings.use_stamp_render_time

Include the render time in image metadata (default True)

**Type:**

bool

<a id="bpy.types.RenderSettings.use_stamp_scene"></a>

#### bpy.types.RenderSettings.use_stamp_scene

Include the name of the active scene in image/video metadata (default True)

**Type:**

bool

<a id="bpy.types.RenderSettings.use_stamp_sequencer_strip"></a>

#### bpy.types.RenderSettings.use_stamp_sequencer_strip

Include the name of the foreground sequence strip in image metadata (default False)

**Type:**

bool

<a id="bpy.types.RenderSettings.use_stamp_time"></a>

#### bpy.types.RenderSettings.use_stamp_time

Include the rendered frame timecode as HH:MM:SS.FF in image metadata (default True)

**Type:**

bool

<a id="bpy.types.RenderSettings.use_texture_cache"></a>

#### bpy.types.RenderSettings.use_texture_cache

Load texture tiles at appropriate resolution on demand to reduce memory usage. This avoids loading all textures into memory, at the cost of extra disk space and some performance (default True)

**Type:**

bool

<a id="bpy.types.RenderSettings.views"></a>

#### bpy.types.RenderSettings.views

(default None, readonly)

**Type:**

[`RenderViews`](bpy.types.RenderViews.md#bpy.types.RenderViews "bpy.types.RenderViews")[[`SceneRenderView`](bpy.types.SceneRenderView.md#bpy.types.SceneRenderView "bpy.types.SceneRenderView")]

<a id="bpy.types.RenderSettings.views_format"></a>

#### bpy.types.RenderSettings.views_format

(default `'STEREO_3D'`)

- `STEREO_3D`
  Stereo 3D – Single stereo camera system, adjust the stereo settings in the camera panel.
- `MULTIVIEW`
  Multi-View – Multi camera system, adjust the cameras individually.

**Type:**

Literal[‘STEREO_3D’, ‘MULTIVIEW’]

<a id="bpy.types.RenderSettings.frame_path"></a>

#### bpy.types.RenderSettings.frame_path(*, frame=-2147483648, preview=False, view='')

Return the absolute path to the filename to be written for a given frame

**Parameters:**

- **frame** (int) – Frame number to use, if unset the current frame will be used (in [-inf, inf], optional)
- **preview** (bool) – Preview, Use preview range (optional)
- **view** (str) – View, The name of the view to use to replace the “%” chars (optional, never None)

**Returns:**

File Path, The resulting filepath from the scenes render settings (never None)

**Return type:**

str

<a id="bpy.types.RenderSettings.bl_rna_get_subclass"></a>

#### classmethod bpy.types.RenderSettings.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.RenderSettings.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.RenderSettings.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`RenderEngine.render`](bpy.types.RenderEngine.md#bpy.types.RenderEngine.render "bpy.types.RenderEngine.render") | - [`Scene.render`](bpy.types.Scene.md#bpy.types.Scene.render "bpy.types.Scene.render") |
