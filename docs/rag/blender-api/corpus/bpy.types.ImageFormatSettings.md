<!-- source: Blender Python API reference 5.2 / bpy.types.ImageFormatSettings.html -->

<a id="imageformatsettings-bpy-struct"></a>

# ImageFormatSettings(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.ImageFormatSettings"></a>

### class bpy.types.ImageFormatSettings(bpy_struct)

Settings for image formats

<a id="bpy.types.ImageFormatSettings.cineon_black"></a>

#### bpy.types.ImageFormatSettings.cineon_black

Log conversion reference blackpoint (in [0, 1024], default 0)

**Type:**

int

<a id="bpy.types.ImageFormatSettings.cineon_gamma"></a>

#### bpy.types.ImageFormatSettings.cineon_gamma

Log conversion gamma (in [0, 10], default 0.0)

**Type:**

float

<a id="bpy.types.ImageFormatSettings.cineon_white"></a>

#### bpy.types.ImageFormatSettings.cineon_white

Log conversion reference whitepoint (in [0, 1024], default 0)

**Type:**

int

<a id="bpy.types.ImageFormatSettings.color_depth"></a>

#### bpy.types.ImageFormatSettings.color_depth

Bit depth per channel (default `'8'`)

**Type:**

Literal[[Image Color Depth Items](bpy_types_enum_items/image_color_depth_items.md#rna-enum-image-color-depth-items)]

<a id="bpy.types.ImageFormatSettings.color_management"></a>

#### bpy.types.ImageFormatSettings.color_management

Which color management settings to use for file saving (default `'FOLLOW_SCENE'`)

**Type:**

Literal[‘FOLLOW_SCENE’, ‘OVERRIDE’]

<a id="bpy.types.ImageFormatSettings.color_mode"></a>

#### bpy.types.ImageFormatSettings.color_mode

Choose BW for saving grayscale images, RGB for saving red, green and blue channels, and RGBA for saving red, green, blue and alpha channels (default `'RGBA'`)

**Type:**

Literal[[Image Color Mode Items](bpy_types_enum_items/image_color_mode_items.md#rna-enum-image-color-mode-items)]

<a id="bpy.types.ImageFormatSettings.compression"></a>

#### bpy.types.ImageFormatSettings.compression

Amount of time to determine best compression: 0 = no compression with fast file output, 100 = maximum lossless compression with slow file output (in [0, 100], default 15)

**Type:**

int

<a id="bpy.types.ImageFormatSettings.display_settings"></a>

#### bpy.types.ImageFormatSettings.display_settings

Settings of device saved image would be displayed on (readonly)

**Type:**

[`ColorManagedDisplaySettings`](bpy.types.ColorManagedDisplaySettings.md#bpy.types.ColorManagedDisplaySettings "bpy.types.ColorManagedDisplaySettings") | None

<a id="bpy.types.ImageFormatSettings.exr_codec"></a>

#### bpy.types.ImageFormatSettings.exr_codec

Compression codec settings for OpenEXR (default `'NONE'`)

**Type:**

Literal[[Exr Codec Items](bpy_types_enum_items/exr_codec_items.md#rna-enum-exr-codec-items)]

<a id="bpy.types.ImageFormatSettings.file_format"></a>

#### bpy.types.ImageFormatSettings.file_format

File format to save the rendered images as (default `'PNG'`)

**Type:**

Literal[[Image Type All Items](bpy_types_enum_items/image_type_all_items.md#rna-enum-image-type-all-items)]

<a id="bpy.types.ImageFormatSettings.has_linear_colorspace"></a>

#### bpy.types.ImageFormatSettings.has_linear_colorspace

File format expects linear color space (default False, readonly)

**Type:**

bool

<a id="bpy.types.ImageFormatSettings.jpeg2k_codec"></a>

#### bpy.types.ImageFormatSettings.jpeg2k_codec

Codec settings for JPEG 2000 (default `'JP2'`)

**Type:**

Literal[‘JP2’, ‘J2K’]

<a id="bpy.types.ImageFormatSettings.linear_colorspace_settings"></a>

#### bpy.types.ImageFormatSettings.linear_colorspace_settings

Output color space settings (readonly)

**Type:**

[`ColorManagedInputColorspaceSettings`](bpy.types.ColorManagedInputColorspaceSettings.md#bpy.types.ColorManagedInputColorspaceSettings "bpy.types.ColorManagedInputColorspaceSettings") | None

<a id="bpy.types.ImageFormatSettings.media_type"></a>

#### bpy.types.ImageFormatSettings.media_type

The type of media to save (default `'IMAGE'`)

**Type:**

Literal[‘IMAGE’, ‘MULTI_LAYER_IMAGE’, ‘VIDEO’]

<a id="bpy.types.ImageFormatSettings.quality"></a>

#### bpy.types.ImageFormatSettings.quality

Quality for image formats that support lossy compression (in [0, 100], default 90)

**Type:**

int

<a id="bpy.types.ImageFormatSettings.stereo_3d_format"></a>

#### bpy.types.ImageFormatSettings.stereo_3d_format

Settings for stereo 3D (readonly, never None)

**Type:**

[`Stereo3dFormat`](bpy.types.Stereo3dFormat.md#bpy.types.Stereo3dFormat "bpy.types.Stereo3dFormat")

<a id="bpy.types.ImageFormatSettings.tiff_codec"></a>

#### bpy.types.ImageFormatSettings.tiff_codec

Compression mode for TIFF (default `'DEFLATE'`)

**Type:**

Literal[‘NONE’, ‘DEFLATE’, ‘LZW’, ‘PACKBITS’]

<a id="bpy.types.ImageFormatSettings.use_cineon_log"></a>

#### bpy.types.ImageFormatSettings.use_cineon_log

Convert to logarithmic color space (default False)

**Type:**

bool

<a id="bpy.types.ImageFormatSettings.use_exr_interleave"></a>

#### bpy.types.ImageFormatSettings.use_exr_interleave

Use legacy interleaved storage of views, layers and passes for compatibility with applications that do not support more efficient multi-part OpenEXR files. (default False)

**Type:**

bool

<a id="bpy.types.ImageFormatSettings.use_jpeg2k_cinema_48"></a>

#### bpy.types.ImageFormatSettings.use_jpeg2k_cinema_48

Use OpenJPEG Cinema Preset (48fps) (default False)

**Type:**

bool

<a id="bpy.types.ImageFormatSettings.use_jpeg2k_cinema_preset"></a>

#### bpy.types.ImageFormatSettings.use_jpeg2k_cinema_preset

Use OpenJPEG Cinema Preset (default False)

**Type:**

bool

<a id="bpy.types.ImageFormatSettings.use_jpeg2k_ycc"></a>

#### bpy.types.ImageFormatSettings.use_jpeg2k_ycc

Save luminance-chrominance-chrominance channels instead of RGB colors (default False)

**Type:**

bool

<a id="bpy.types.ImageFormatSettings.use_preview"></a>

#### bpy.types.ImageFormatSettings.use_preview

When rendering animations, save JPG preview images in same directory (default False)

**Type:**

bool

<a id="bpy.types.ImageFormatSettings.view_settings"></a>

#### bpy.types.ImageFormatSettings.view_settings

Color management settings applied on image before saving (readonly)

**Type:**

[`ColorManagedViewSettings`](bpy.types.ColorManagedViewSettings.md#bpy.types.ColorManagedViewSettings "bpy.types.ColorManagedViewSettings") | None

<a id="bpy.types.ImageFormatSettings.views_format"></a>

#### bpy.types.ImageFormatSettings.views_format

Format of multiview media (default `'INDIVIDUAL'`)

**Type:**

Literal[[Views Format Multiview Items](bpy_types_enum_items/views_format_multiview_items.md#rna-enum-views-format-multiview-items)]

<a id="bpy.types.ImageFormatSettings.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ImageFormatSettings.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ImageFormatSettings.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ImageFormatSettings.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`CompositorNodeOutputFile.format`](bpy.types.CompositorNodeOutputFile.md#bpy.types.CompositorNodeOutputFile.format "bpy.types.CompositorNodeOutputFile.format") - [`NodeCompositorFileOutputItem.format`](bpy.types.NodeCompositorFileOutputItem.md#bpy.types.NodeCompositorFileOutputItem.format "bpy.types.NodeCompositorFileOutputItem.format") - [`BakeSettings.image_settings`](bpy.types.BakeSettings.md#bpy.types.BakeSettings.image_settings "bpy.types.BakeSettings.image_settings") | - [`RenderSettings.image_settings`](bpy.types.RenderSettings.md#bpy.types.RenderSettings.image_settings "bpy.types.RenderSettings.image_settings") - [`UILayout.template_image_settings`](bpy.types.UILayout.md#bpy.types.UILayout.template_image_settings "bpy.types.UILayout.template_image_settings") - [`UILayout.template_image_views`](bpy.types.UILayout.md#bpy.types.UILayout.template_image_views "bpy.types.UILayout.template_image_views") |
