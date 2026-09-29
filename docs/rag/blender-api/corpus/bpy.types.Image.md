<!-- source: Blender Python API reference 5.2 / bpy.types.Image.html -->

<a id="image-id"></a>

# Image(ID)

<a id="image-data"></a>

## Image Data

The Image data-block is a shallow wrapper around image or video file(s)
(on disk, as packed data, or generated).

All actual data like the pixel buffer, size, resolution etc. is
cached in an [`imbuf.types.ImBuf`](imbuf.types.md#imbuf.types.ImBuf "imbuf.types.ImBuf") image buffer (or several buffers
in some cases, like UDIM textures, multi-views, animations…).

Several properties and functions of the Image data-block are then actually
using/modifying its image buffer, and not the Image data-block itself.

> **Warning:**
>
> One key limitation is that image buffers are not shared between different
> Image data-blocks, and they are not duplicated when copying an image.
>
> So until a modified image buffer is saved on disk, duplicating its Image
> data-block will not propagate the underlying buffer changes to the new Image.

This example script generates an Image data-block with a given size,
change its first pixel, rescale it, and duplicates the image.

The duplicated image still has the same size and colors as the original image
at its creation, all editing in the original image’s buffer is ‘lost’ in its copy.

```python
import bpy

image_src = bpy.data.images.new('src', 1024, 102)
print(image_src.size)
print(image_src.pixels[0:4])

image_src.scale(1024, 720)
image_src.pixels[0:4] = (0.5, 0.5, 0.5, 0.5)
image_src.update()
print(image_src.size)
print(image_src.pixels[0:4])

image_dest = image_src.copy()
image_dest.update()
print(image_dest.size)
print(image_dest.pixels[0:4])
```

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")

<a id="bpy.types.Image"></a>

### class bpy.types.Image(ID)

Image data-block referencing an external or packed image

<a id="bpy.types.Image.alpha_mode"></a>

#### bpy.types.Image.alpha_mode

Representation of alpha in the image file, to convert to and from when saving and loading the image (default `'STRAIGHT'`)

- `STRAIGHT`
  Straight – Store RGB and alpha channels separately with alpha acting as a mask, also known as unassociated alpha. Commonly used by image editing applications and file formats like PNG..
- `PREMUL`
  Premultiplied – Store RGB channels with alpha multiplied in, also known as associated alpha. The natural format for renders and used by file formats like OpenEXR..
- `CHANNEL_PACKED`
  Channel Packed – Different images are packed in the RGB and alpha channels, and they should not affect each other. Channel packing is commonly used by game engines to save memory..
- `NONE`
  None – Ignore alpha channel from the file and make image fully opaque.

**Type:**

Literal[‘STRAIGHT’, ‘PREMUL’, ‘CHANNEL_PACKED’, ‘NONE’]

<a id="bpy.types.Image.channels"></a>

#### bpy.types.Image.channels

Number of channels in pixels buffer (in [0, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.Image.colorspace_settings"></a>

#### bpy.types.Image.colorspace_settings

Input color space settings (readonly)

**Type:**

[`ColorManagedInputColorspaceSettings`](bpy.types.ColorManagedInputColorspaceSettings.md#bpy.types.ColorManagedInputColorspaceSettings "bpy.types.ColorManagedInputColorspaceSettings") | None

<a id="bpy.types.Image.depth"></a>

#### bpy.types.Image.depth

Image bit depth (in [0, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.Image.display_aspect"></a>

#### bpy.types.Image.display_aspect

Display Aspect for this image, does not affect rendering (array of 2 items, in [0.1, inf], default (1.0, 1.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.Image.file_format"></a>

#### bpy.types.Image.file_format

Format used for re-saving this file (default `'TARGA'`)

**Type:**

Literal[[Image Type All Items](bpy_types_enum_items/image_type_all_items.md#rna-enum-image-type-all-items)]

<a id="bpy.types.Image.filepath"></a>

#### bpy.types.Image.filepath

Image/Movie file name (default “”, never None, blend relative `//` prefix supported)

**Type:**

str

<a id="bpy.types.Image.filepath_raw"></a>

#### bpy.types.Image.filepath_raw

Image/Movie file name (without data refreshing) (default “”, never None, blend relative `//` prefix supported)

**Type:**

str

<a id="bpy.types.Image.frame_duration"></a>

#### bpy.types.Image.frame_duration

Duration (in frames) of the image (1 when not a video/sequence) (in [0, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.Image.generated_color"></a>

#### bpy.types.Image.generated_color

Fill color for the generated image (array of 4 items, in [0, inf], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.Image.generated_height"></a>

#### bpy.types.Image.generated_height

Generated image height (in [1, 65536], default 1024)

**Type:**

int

<a id="bpy.types.Image.generated_type"></a>

#### bpy.types.Image.generated_type

Generated image type (default `'UV_GRID'`)

**Type:**

Literal[[Image Generated Type Items](bpy_types_enum_items/image_generated_type_items.md#rna-enum-image-generated-type-items)]

<a id="bpy.types.Image.generated_width"></a>

#### bpy.types.Image.generated_width

Generated image width (in [1, 65536], default 1024)

**Type:**

int

<a id="bpy.types.Image.has_data"></a>

#### bpy.types.Image.has_data

True if the image data is loaded into memory (default False, readonly)

**Type:**

bool

<a id="bpy.types.Image.is_dirty"></a>

#### bpy.types.Image.is_dirty

Image has changed and is not saved (default False, readonly)

**Type:**

bool

<a id="bpy.types.Image.is_float"></a>

#### bpy.types.Image.is_float

True if this image is stored in floating-point buffer (default False, readonly)

**Type:**

bool

<a id="bpy.types.Image.is_multiview"></a>

#### bpy.types.Image.is_multiview

Image has more than one view (default False, readonly)

**Type:**

bool

<a id="bpy.types.Image.is_stereo_3d"></a>

#### bpy.types.Image.is_stereo_3d

Image has left and right views (default False, readonly)

**Type:**

bool

<a id="bpy.types.Image.packed_file"></a>

#### bpy.types.Image.packed_file

First packed file of the image (readonly)

**Type:**

[`PackedFile`](bpy.types.PackedFile.md#bpy.types.PackedFile "bpy.types.PackedFile") | None

<a id="bpy.types.Image.packed_files"></a>

#### bpy.types.Image.packed_files

Collection of packed images (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`ImagePackedFile`](bpy.types.ImagePackedFile.md#bpy.types.ImagePackedFile "bpy.types.ImagePackedFile")]

<a id="bpy.types.Image.pixels"></a>

#### bpy.types.Image.pixels

Image buffer pixels in floating-point values (dynamic array, in [-inf, inf], default 0.0)

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.Image.render_slots"></a>

#### bpy.types.Image.render_slots

Render slots of the image (default None, readonly)

**Type:**

[`RenderSlots`](bpy.types.RenderSlots.md#bpy.types.RenderSlots "bpy.types.RenderSlots")[[`RenderSlot`](bpy.types.RenderSlot.md#bpy.types.RenderSlot "bpy.types.RenderSlot")]

<a id="bpy.types.Image.resolution"></a>

#### bpy.types.Image.resolution

X/Y pixels per meter, for the image buffer (array of 2 items, in [-inf, inf], default (0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.Image.seam_margin"></a>

#### bpy.types.Image.seam_margin

Margin to take into account when fixing UV seams during painting. Higher number would improve seam-fixes for mipmaps, but decreases performance. (in [-32768, 32767], default 8)

**Type:**

int

<a id="bpy.types.Image.size"></a>

#### bpy.types.Image.size

Width and height of the image buffer in pixels, zero when image data cannot be loaded (array of 2 items, in [-inf, inf], default (0, 0), readonly)

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[int]

<a id="bpy.types.Image.source"></a>

#### bpy.types.Image.source

Where the image comes from (default `'FILE'`)

- `FILE`
  Single Image – Single image file.
- `SEQUENCE`
  Image Sequence – Multiple image files, as a sequence.
- `MOVIE`
  Movie – Movie file.
- `GENERATED`
  Generated – Generated image.
- `VIEWER`
  Viewer – Compositing node viewer.
- `TILED`
  UDIM Tiles – Tiled UDIM image texture.

**Type:**

Literal[‘FILE’, ‘SEQUENCE’, ‘MOVIE’, ‘GENERATED’, ‘VIEWER’, ‘TILED’]

<a id="bpy.types.Image.stereo_3d_format"></a>

#### bpy.types.Image.stereo_3d_format

Settings for stereo 3d (readonly, never None)

**Type:**

[`Stereo3dFormat`](bpy.types.Stereo3dFormat.md#bpy.types.Stereo3dFormat "bpy.types.Stereo3dFormat")

<a id="bpy.types.Image.tiles"></a>

#### bpy.types.Image.tiles

Tiles of the image (default None, readonly)

**Type:**

[`UDIMTiles`](bpy.types.UDIMTiles.md#bpy.types.UDIMTiles "bpy.types.UDIMTiles")[[`UDIMTile`](bpy.types.UDIMTile.md#bpy.types.UDIMTile "bpy.types.UDIMTile")]

<a id="bpy.types.Image.type"></a>

#### bpy.types.Image.type

How to generate the image (default `'IMAGE'`, readonly)

**Type:**

Literal[‘IMAGE’, ‘MULTILAYER’, ‘UV_TEST’, ‘RENDER_RESULT’, ‘COMPOSITING’]

<a id="bpy.types.Image.use_deinterlace"></a>

#### bpy.types.Image.use_deinterlace

Deinterlace movie file on load (default False)

**Type:**

bool

<a id="bpy.types.Image.use_generated_float"></a>

#### bpy.types.Image.use_generated_float

Generate floating-point buffer (default False)

**Type:**

bool

<a id="bpy.types.Image.use_half_precision"></a>

#### bpy.types.Image.use_half_precision

Use 16 bits per channel to lower the memory usage during rendering.
Note: Not supported by Cycles

(default True)

**Type:**

bool

<a id="bpy.types.Image.use_multiview"></a>

#### bpy.types.Image.use_multiview

Use Multiple Views (when available) (default False)

**Type:**

bool

<a id="bpy.types.Image.use_view_as_render"></a>

#### bpy.types.Image.use_view_as_render

Apply render part of display transformation when displaying this image on the screen (default False)

**Type:**

bool

<a id="bpy.types.Image.views_format"></a>

#### bpy.types.Image.views_format

Mode to load image views (default `'INDIVIDUAL'`)

**Type:**

Literal[[Views Format Items](bpy_types_enum_items/views_format_items.md#rna-enum-views-format-items)]

<a id="bpy.types.Image.save_render"></a>

#### bpy.types.Image.save_render(filepath, *, scene=None, quality=0)

Save image to a specific path using a scenes render settings

**Parameters:**

- **filepath** (str) – Output path (never None)
- **scene** ([`Scene`](bpy.types.Scene.md#bpy.types.Scene "bpy.types.Scene") | None) – Scene to take image parameters from (optional)
- **quality** (int) – Quality, Quality for image formats that support lossy compression, uses default quality if not specified (in [0, 100], optional)

<a id="bpy.types.Image.save"></a>

#### bpy.types.Image.save(*, filepath='', quality=0, save_copy=False)

Save image

**Parameters:**

- **filepath** (str) – Output path, uses image data-block filepath if not specified (optional, never None)
- **quality** (int) – Quality, Quality for image formats that support lossy compression, uses default quality if not specified (in [0, 100], optional)
- **save_copy** (bool) – Save Copy, Save the image as a copy, without updating current image’s filepath (optional)

<a id="bpy.types.Image.pack"></a>

#### bpy.types.Image.pack(*, data=b'', data_len=0)

Pack an image as embedded data into the .blend file

**Parameters:**

- **data** (bytes) – data, Raw data (bytes, exact content of the embedded file) (optional, never None)
- **data_len** (int) – data_len, length of given data (mandatory if data is provided) (in [0, inf], optional)

<a id="bpy.types.Image.unpack"></a>

#### bpy.types.Image.unpack(*, method='USE_LOCAL')

Save an image packed in the .blend file to disk

**Parameters:**

**method** (Literal[[Unpack Method Items](bpy_types_enum_items/unpack_method_items.md#rna-enum-unpack-method-items)]) – method, How to unpack (optional)

<a id="bpy.types.Image.reload"></a>

#### bpy.types.Image.reload()

Reload the image from its source path

<a id="bpy.types.Image.update"></a>

#### bpy.types.Image.update()

Update the display image from the floating-point buffer

<a id="bpy.types.Image.scale"></a>

#### bpy.types.Image.scale(width, height, *, frame=0, tile_index=0)

Scale the buffer of the image, in pixels

**Parameters:**

- **width** (int) – Width (in [1, inf])
- **height** (int) – Height (in [1, inf])
- **frame** (int) – Frame, Frame (for image sequences) (in [0, inf], optional)
- **tile_index** (int) – Tile, Tile index (for tiled images) (in [0, inf], optional)

<a id="bpy.types.Image.gl_touch"></a>

#### bpy.types.Image.gl_touch(*, frame=0, layer_index=0, pass_index=0)

Delay the image from being cleaned from the cache due inactivity

**Parameters:**

- **frame** (int) – Frame, Frame of image sequence or movie (in [0, inf], optional)
- **layer_index** (int) – Layer, Index of layer that should be loaded (in [0, inf], optional)
- **pass_index** (int) – Pass, Index of pass that should be loaded (in [0, inf], optional)

**Returns:**

Error, OpenGL error value (in [-inf, inf])

**Return type:**

int

<a id="bpy.types.Image.gl_load"></a>

#### bpy.types.Image.gl_load(*, frame=0, layer_index=0, pass_index=0)

Load the image into an OpenGL texture. On success, image.bindcode will contain the OpenGL texture bindcode. Colors read from the texture will be in scene linear color space and have premultiplied or straight alpha matching the image alpha mode.

**Parameters:**

- **frame** (int) – Frame, Frame of image sequence or movie (in [0, inf], optional)
- **layer_index** (int) – Layer, Index of layer that should be loaded (in [0, inf], optional)
- **pass_index** (int) – Pass, Index of pass that should be loaded (in [0, inf], optional)

**Returns:**

Error, OpenGL error value (in [-inf, inf])

**Return type:**

int

<a id="bpy.types.Image.gl_free"></a>

#### bpy.types.Image.gl_free()

Free the image from OpenGL graphics memory

<a id="bpy.types.Image.filepath_from_user"></a>

#### bpy.types.Image.filepath_from_user(*, image_user=None)

Return the absolute path to the filepath of an image frame specified by the image user

**Parameters:**

**image_user** ([`ImageUser`](bpy.types.ImageUser.md#bpy.types.ImageUser "bpy.types.ImageUser") | None) – Image user of the image to get filepath for (optional)

**Returns:**

File Path, The resulting filepath from the image and its user (never None)

**Return type:**

str

<a id="bpy.types.Image.buffers_free"></a>

#### bpy.types.Image.buffers_free()

Free the image buffers from memory

<a id="bpy.types.Image.bl_rna_get_subclass"></a>

#### classmethod bpy.types.Image.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.Image.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.Image.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([type](#bpy.types.Image.type "bpy.types.Image.type") | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

[type](#bpy.types.Image.type "bpy.types.Image.type")

<a id="inherited-properties"></a>

### Inherited Properties

bpy_struct.id_data, ID.name, ID.name_full, ID.id_type, ID.session_uid, ID.is_evaluated, ID.original, ID.users, ID.use_fake_user, ID.use_extra_user, ID.is_embedded_data, ID.is_linked_packed, ID.is_missing, ID.is_runtime_data, ID.is_editable, ID.tag, ID.is_library_indirect, ID.library, ID.library_weak_reference, ID.asset_data, ID.override_library, ID.preview

<a id="inherited-functions"></a>

### Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, ID.bl_system_properties_get, ID.rename, ID.evaluated_get, ID.copy, ID.asset_mark, ID.asset_clear, ID.asset_generate_preview, ID.override_create, ID.override_hierarchy_create, ID.user_clear, ID.user_remap, ID.make_local, ID.user_of_id, ID.animation_data_create, ID.animation_data_clear, ID.update_tag, ID.preview_ensure, ID.bl_rna_get_subclass, ID.bl_rna_get_subclass_py

<a id="references"></a>

### References

|  |  |
| --- | --- |
| - `bpy.context.edit_image` - [`BlendData.images`](bpy.types.BlendData.md#bpy.types.BlendData.images "bpy.types.BlendData.images") - [`BlendDataImages.load`](bpy.types.BlendDataImages.md#bpy.types.BlendDataImages.load "bpy.types.BlendDataImages.load") - [`BlendDataImages.new`](bpy.types.BlendDataImages.md#bpy.types.BlendDataImages.new "bpy.types.BlendDataImages.new") - [`BlendDataImages.remove`](bpy.types.BlendDataImages.md#bpy.types.BlendDataImages.remove "bpy.types.BlendDataImages.remove") - [`CameraBackgroundImage.image`](bpy.types.CameraBackgroundImage.md#bpy.types.CameraBackgroundImage.image "bpy.types.CameraBackgroundImage.image") - [`CompositorNodeCryptomatteV2.image`](bpy.types.CompositorNodeCryptomatteV2.md#bpy.types.CompositorNodeCryptomatteV2.image "bpy.types.CompositorNodeCryptomatteV2.image") - [`CompositorNodeImage.image`](bpy.types.CompositorNodeImage.md#bpy.types.CompositorNodeImage.image "bpy.types.CompositorNodeImage.image") - [`GeometryNodeInputImage.image`](bpy.types.GeometryNodeInputImage.md#bpy.types.GeometryNodeInputImage.image "bpy.types.GeometryNodeInputImage.image") - [`ImagePaint.canvas`](bpy.types.ImagePaint.md#bpy.types.ImagePaint.canvas "bpy.types.ImagePaint.canvas") - [`ImagePaint.clone_image`](bpy.types.ImagePaint.md#bpy.types.ImagePaint.clone_image "bpy.types.ImagePaint.clone_image") - [`ImagePaint.stencil_image`](bpy.types.ImagePaint.md#bpy.types.ImagePaint.stencil_image "bpy.types.ImagePaint.stencil_image") - [`ImageTexture.image`](bpy.types.ImageTexture.md#bpy.types.ImageTexture.image "bpy.types.ImageTexture.image") | - [`Material.texture_paint_images`](bpy.types.Material.md#bpy.types.Material.texture_paint_images "bpy.types.Material.texture_paint_images") - [`MaterialGPencilStyle.fill_image`](bpy.types.MaterialGPencilStyle.md#bpy.types.MaterialGPencilStyle.fill_image "bpy.types.MaterialGPencilStyle.fill_image") - [`MaterialGPencilStyle.stroke_image`](bpy.types.MaterialGPencilStyle.md#bpy.types.MaterialGPencilStyle.stroke_image "bpy.types.MaterialGPencilStyle.stroke_image") - [`MovieTrackingPlaneTrack.image`](bpy.types.MovieTrackingPlaneTrack.md#bpy.types.MovieTrackingPlaneTrack.image "bpy.types.MovieTrackingPlaneTrack.image") - [`NodeSocketImage.default_value`](bpy.types.NodeSocketImage.md#bpy.types.NodeSocketImage.default_value "bpy.types.NodeSocketImage.default_value") - [`NodeTreeInterfaceSocketImage.default_value`](bpy.types.NodeTreeInterfaceSocketImage.md#bpy.types.NodeTreeInterfaceSocketImage.default_value "bpy.types.NodeTreeInterfaceSocketImage.default_value") - [`PaintModeSettings.canvas_image`](bpy.types.PaintModeSettings.md#bpy.types.PaintModeSettings.canvas_image "bpy.types.PaintModeSettings.canvas_image") - [`ShaderNodeTexEnvironment.image`](bpy.types.ShaderNodeTexEnvironment.md#bpy.types.ShaderNodeTexEnvironment.image "bpy.types.ShaderNodeTexEnvironment.image") - [`ShaderNodeTexImage.image`](bpy.types.ShaderNodeTexImage.md#bpy.types.ShaderNodeTexImage.image "bpy.types.ShaderNodeTexImage.image") - [`SpaceImageEditor.image`](bpy.types.SpaceImageEditor.md#bpy.types.SpaceImageEditor.image "bpy.types.SpaceImageEditor.image") - [`TextureNodeImage.image`](bpy.types.TextureNodeImage.md#bpy.types.TextureNodeImage.image "bpy.types.TextureNodeImage.image") - [`UILayout.template_image_layers`](bpy.types.UILayout.md#bpy.types.UILayout.template_image_layers "bpy.types.UILayout.template_image_layers") |
