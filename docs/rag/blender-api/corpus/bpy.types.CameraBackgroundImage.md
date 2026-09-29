<!-- source: Blender Python API reference 5.2 / bpy.types.CameraBackgroundImage.html -->

<a id="camerabackgroundimage-bpy-struct"></a>

# CameraBackgroundImage(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.CameraBackgroundImage"></a>

### class bpy.types.CameraBackgroundImage(bpy_struct)

Image and settings for display in the 3D View background

<a id="bpy.types.CameraBackgroundImage.alpha"></a>

#### bpy.types.CameraBackgroundImage.alpha

Image opacity to blend the image against the background color (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.CameraBackgroundImage.clip"></a>

#### bpy.types.CameraBackgroundImage.clip

Movie clip displayed and edited in this space

**Type:**

[`MovieClip`](bpy.types.MovieClip.md#bpy.types.MovieClip "bpy.types.MovieClip") | None

<a id="bpy.types.CameraBackgroundImage.clip_user"></a>

#### bpy.types.CameraBackgroundImage.clip_user

Parameters defining which frame of the movie clip is displayed (readonly, never None)

**Type:**

[`MovieClipUser`](bpy.types.MovieClipUser.md#bpy.types.MovieClipUser "bpy.types.MovieClipUser")

<a id="bpy.types.CameraBackgroundImage.display_depth"></a>

#### bpy.types.CameraBackgroundImage.display_depth

Display under or over everything (default `'BACK'`)

**Type:**

Literal[‘BACK’, ‘FRONT’]

<a id="bpy.types.CameraBackgroundImage.frame_method"></a>

#### bpy.types.CameraBackgroundImage.frame_method

How the image fits in the camera frame (default `'FIT'`)

**Type:**

Literal[‘STRETCH’, ‘FIT’, ‘CROP’]

<a id="bpy.types.CameraBackgroundImage.image"></a>

#### bpy.types.CameraBackgroundImage.image

Image displayed and edited in this space

**Type:**

[`Image`](bpy.types.Image.md#bpy.types.Image "bpy.types.Image") | None

<a id="bpy.types.CameraBackgroundImage.image_user"></a>

#### bpy.types.CameraBackgroundImage.image_user

Parameters defining which layer, pass and frame of the image is displayed (readonly, never None)

**Type:**

[`ImageUser`](bpy.types.ImageUser.md#bpy.types.ImageUser "bpy.types.ImageUser")

<a id="bpy.types.CameraBackgroundImage.is_override_data"></a>

#### bpy.types.CameraBackgroundImage.is_override_data

In a local override camera, whether this background image comes from the linked reference camera, or is local to the override (default True, readonly)

**Type:**

bool

<a id="bpy.types.CameraBackgroundImage.offset"></a>

#### bpy.types.CameraBackgroundImage.offset

(array of 2 items, in [-inf, inf], default (0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.CameraBackgroundImage.rotation"></a>

#### bpy.types.CameraBackgroundImage.rotation

Rotation for the background image (ortho view only) (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.CameraBackgroundImage.scale"></a>

#### bpy.types.CameraBackgroundImage.scale

Scale the background image (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.CameraBackgroundImage.show_background_image"></a>

#### bpy.types.CameraBackgroundImage.show_background_image

Show this image as background (default True)

**Type:**

bool

<a id="bpy.types.CameraBackgroundImage.show_expanded"></a>

#### bpy.types.CameraBackgroundImage.show_expanded

Show the details in the user interface (default False)

**Type:**

bool

<a id="bpy.types.CameraBackgroundImage.show_on_foreground"></a>

#### bpy.types.CameraBackgroundImage.show_on_foreground

Show this image in front of objects in viewport (default False)

**Type:**

bool

<a id="bpy.types.CameraBackgroundImage.source"></a>

#### bpy.types.CameraBackgroundImage.source

Data source used for background (default `'IMAGE'`)

**Type:**

Literal[‘IMAGE’, ‘MOVIE_CLIP’]

<a id="bpy.types.CameraBackgroundImage.use_camera_clip"></a>

#### bpy.types.CameraBackgroundImage.use_camera_clip

Use movie clip from active scene camera (default False)

**Type:**

bool

<a id="bpy.types.CameraBackgroundImage.use_flip_x"></a>

#### bpy.types.CameraBackgroundImage.use_flip_x

Flip the background image horizontally (default False)

**Type:**

bool

<a id="bpy.types.CameraBackgroundImage.use_flip_y"></a>

#### bpy.types.CameraBackgroundImage.use_flip_y

Flip the background image vertically (default False)

**Type:**

bool

<a id="bpy.types.CameraBackgroundImage.bl_rna_get_subclass"></a>

#### classmethod bpy.types.CameraBackgroundImage.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.CameraBackgroundImage.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.CameraBackgroundImage.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Camera.background_images`](bpy.types.Camera.md#bpy.types.Camera.background_images "bpy.types.Camera.background_images") - [`CameraBackgroundImages.new`](bpy.types.CameraBackgroundImages.md#bpy.types.CameraBackgroundImages.new "bpy.types.CameraBackgroundImages.new") | - [`CameraBackgroundImages.remove`](bpy.types.CameraBackgroundImages.md#bpy.types.CameraBackgroundImages.remove "bpy.types.CameraBackgroundImages.remove") |
