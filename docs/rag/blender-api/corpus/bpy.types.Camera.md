<!-- source: Blender Python API reference 5.2 / bpy.types.Camera.html -->

<a id="camera-id"></a>

# Camera(ID)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")

<a id="bpy.types.Camera"></a>

### class bpy.types.Camera(ID)

Camera data-block for storing camera settings

<a id="bpy.types.Camera.angle"></a>

#### bpy.types.Camera.angle

Camera lens field of view (in [0.00640536, 3.01675], default 0.69115)

**Type:**

float

<a id="bpy.types.Camera.angle_x"></a>

#### bpy.types.Camera.angle_x

Camera lens horizontal field of view (in [0.00640536, 3.01675], default 0.0)

**Type:**

float

<a id="bpy.types.Camera.angle_y"></a>

#### bpy.types.Camera.angle_y

Camera lens vertical field of view (in [0.00640536, 3.01675], default 0.0)

**Type:**

float

<a id="bpy.types.Camera.animation_data"></a>

#### bpy.types.Camera.animation_data

Animation data for this data-block (readonly)

**Type:**

[`AnimData`](bpy.types.AnimData.md#bpy.types.AnimData "bpy.types.AnimData") | None

<a id="bpy.types.Camera.background_images"></a>

#### bpy.types.Camera.background_images

List of background images (default None, readonly)

**Type:**

[`CameraBackgroundImages`](bpy.types.CameraBackgroundImages.md#bpy.types.CameraBackgroundImages "bpy.types.CameraBackgroundImages")[[`CameraBackgroundImage`](bpy.types.CameraBackgroundImage.md#bpy.types.CameraBackgroundImage "bpy.types.CameraBackgroundImage")]

<a id="bpy.types.Camera.central_cylindrical_radius"></a>

#### bpy.types.Camera.central_cylindrical_radius

Radius of the virtual cylinder (in [1e-05, inf], default 1.0)

**Type:**

float

<a id="bpy.types.Camera.central_cylindrical_range_u_max"></a>

#### bpy.types.Camera.central_cylindrical_range_u_max

Maximum Longitude value for the central cylindrical lens (in [-inf, inf], default 3.14159)

**Type:**

float

<a id="bpy.types.Camera.central_cylindrical_range_u_min"></a>

#### bpy.types.Camera.central_cylindrical_range_u_min

Minimum Longitude value for the central cylindrical lens (in [-inf, inf], default -3.14159)

**Type:**

float

<a id="bpy.types.Camera.central_cylindrical_range_v_max"></a>

#### bpy.types.Camera.central_cylindrical_range_v_max

Maximum Height value for the central cylindrical lens (in [-inf, inf], default 1.0)

**Type:**

float

<a id="bpy.types.Camera.central_cylindrical_range_v_min"></a>

#### bpy.types.Camera.central_cylindrical_range_v_min

Minimum Height value for the central cylindrical lens (in [-inf, inf], default -1.0)

**Type:**

float

<a id="bpy.types.Camera.clip_end"></a>

#### bpy.types.Camera.clip_end

Camera far clipping distance (in [1e-06, inf], default 1000.0)

**Type:**

float

<a id="bpy.types.Camera.clip_start"></a>

#### bpy.types.Camera.clip_start

Camera near clipping distance (in [1e-06, inf], default 0.1)

**Type:**

float

<a id="bpy.types.Camera.composition_guide_color"></a>

#### bpy.types.Camera.composition_guide_color

Color and alpha for compositional guide overlays (array of 4 items, in [0, inf], default (0.5, 0.5, 0.5, 1.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.Camera.custom_bytecode"></a>

#### bpy.types.Camera.custom_bytecode

Compiled bytecode of the custom shader (default “”, never None)

**Type:**

str

<a id="bpy.types.Camera.custom_bytecode_hash"></a>

#### bpy.types.Camera.custom_bytecode_hash

Hash of the compiled bytecode of the custom shader, for quick equality checking (default “”, never None)

**Type:**

str

<a id="bpy.types.Camera.custom_filepath"></a>

#### bpy.types.Camera.custom_filepath

Path to the shader defining the custom camera (default “”, never None)

**Type:**

str

<a id="bpy.types.Camera.custom_mode"></a>

#### bpy.types.Camera.custom_mode

(default `'INTERNAL'`)

- `INTERNAL`
  Internal – Use internal text data-block.
- `EXTERNAL`
  External – Use external file.

**Type:**

Literal[‘INTERNAL’, ‘EXTERNAL’]

<a id="bpy.types.Camera.custom_shader"></a>

#### bpy.types.Camera.custom_shader

Shader defining the custom camera

**Type:**

[`Text`](bpy.types.Text.md#bpy.types.Text "bpy.types.Text") | None

<a id="bpy.types.Camera.cycles_custom"></a>

#### bpy.types.Camera.cycles_custom

Parameters for custom (OSL-based) cameras (readonly)

**Type:**

`CyclesCustomCameraSettings` | None

<a id="bpy.types.Camera.display_size"></a>

#### bpy.types.Camera.display_size

Apparent size of the Camera object in the 3D View (in [0.01, 1000], default 1.0)

**Type:**

float

<a id="bpy.types.Camera.dof"></a>

#### bpy.types.Camera.dof

(readonly)

**Type:**

[`CameraDOFSettings`](bpy.types.CameraDOFSettings.md#bpy.types.CameraDOFSettings "bpy.types.CameraDOFSettings") | None

<a id="bpy.types.Camera.fisheye_fov"></a>

#### bpy.types.Camera.fisheye_fov

Field of view for the fisheye lens (in [0.1745, 31.4159], default 3.14159)

**Type:**

float

<a id="bpy.types.Camera.fisheye_lens"></a>

#### bpy.types.Camera.fisheye_lens

Lens focal length (mm) (in [0.01, 100], default 10.5)

**Type:**

float

<a id="bpy.types.Camera.fisheye_polynomial_k0"></a>

#### bpy.types.Camera.fisheye_polynomial_k0

Coefficient K0 of the lens polynomial (in [-inf, inf], default -1.17351e-05)

**Type:**

float

<a id="bpy.types.Camera.fisheye_polynomial_k1"></a>

#### bpy.types.Camera.fisheye_polynomial_k1

Coefficient K1 of the lens polynomial (in [-inf, inf], default -0.0199887)

**Type:**

float

<a id="bpy.types.Camera.fisheye_polynomial_k2"></a>

#### bpy.types.Camera.fisheye_polynomial_k2

Coefficient K2 of the lens polynomial (in [-inf, inf], default -3.3525e-06)

**Type:**

float

<a id="bpy.types.Camera.fisheye_polynomial_k3"></a>

#### bpy.types.Camera.fisheye_polynomial_k3

Coefficient K3 of the lens polynomial (in [-inf, inf], default 3.0993e-06)

**Type:**

float

<a id="bpy.types.Camera.fisheye_polynomial_k4"></a>

#### bpy.types.Camera.fisheye_polynomial_k4

Coefficient K4 of the lens polynomial (in [-inf, inf], default -2.61e-08)

**Type:**

float

<a id="bpy.types.Camera.latitude_max"></a>

#### bpy.types.Camera.latitude_max

Maximum latitude (vertical angle) for the equirectangular lens (in [-1.5708, 1.5708], default 1.5708)

**Type:**

float

<a id="bpy.types.Camera.latitude_min"></a>

#### bpy.types.Camera.latitude_min

Minimum latitude (vertical angle) for the equirectangular lens (in [-1.5708, 1.5708], default -1.5708)

**Type:**

float

<a id="bpy.types.Camera.lens"></a>

#### bpy.types.Camera.lens

Perspective Camera focal length value in millimeters (in [1, inf], default 50.0)

**Type:**

float

<a id="bpy.types.Camera.lens_unit"></a>

#### bpy.types.Camera.lens_unit

Unit to edit lens in for the user interface (default `'MILLIMETERS'`)

- `MILLIMETERS`
  Millimeters – Specify focal length of the lens in millimeters.
- `FOV`
  Field of View – Specify the lens as the field of view’s angle.

**Type:**

Literal[‘MILLIMETERS’, ‘FOV’]

<a id="bpy.types.Camera.longitude_max"></a>

#### bpy.types.Camera.longitude_max

Maximum longitude (horizontal angle) for the equirectangular lens (in [-inf, inf], default 3.14159)

**Type:**

float

<a id="bpy.types.Camera.longitude_min"></a>

#### bpy.types.Camera.longitude_min

Minimum longitude (horizontal angle) for the equirectangular lens (in [-inf, inf], default -3.14159)

**Type:**

float

<a id="bpy.types.Camera.ortho_scale"></a>

#### bpy.types.Camera.ortho_scale

Orthographic Camera scale (similar to zoom) (in [0, inf], default 6.0)

**Type:**

float

<a id="bpy.types.Camera.panorama_type"></a>

#### bpy.types.Camera.panorama_type

Distortion to use for the calculation (default `'FISHEYE_EQUISOLID'`)

- `EQUIRECTANGULAR`
  Equirectangular – Spherical camera for environment maps, also known as Lat Long panorama.
- `EQUIANGULAR_CUBEMAP_FACE`
  Equiangular Cubemap Face – Single face of an equiangular cubemap.
- `MIRRORBALL`
  Mirror Ball – Mirror ball mapping for environment maps.
- `FISHEYE_EQUIDISTANT`
  Fisheye Equidistant – Ideal for fulldomes, ignore the sensor dimensions.
- `FISHEYE_EQUISOLID`
  Fisheye Equisolid – Similar to most fisheye modern lens, takes sensor dimensions into consideration.
- `FISHEYE_LENS_POLYNOMIAL`
  Fisheye Lens Polynomial – Defines the lens projection as polynomial to allow real world camera lenses to be mimicked.
- `CENTRAL_CYLINDRICAL`
  Central Cylindrical – Projection onto a virtual cylinder from its center, similar as a rotating panoramic camera.

**Type:**

Literal[‘EQUIRECTANGULAR’, ‘EQUIANGULAR_CUBEMAP_FACE’, ‘MIRRORBALL’, ‘FISHEYE_EQUIDISTANT’, ‘FISHEYE_EQUISOLID’, ‘FISHEYE_LENS_POLYNOMIAL’, ‘CENTRAL_CYLINDRICAL’]

<a id="bpy.types.Camera.passepartout_alpha"></a>

#### bpy.types.Camera.passepartout_alpha

Opacity (alpha) of the darkened overlay in Camera view (in [0, 1], default 0.5)

**Type:**

float

<a id="bpy.types.Camera.sensor_fit"></a>

#### bpy.types.Camera.sensor_fit

Method to fit image and field of view angle inside the sensor (default `'AUTO'`)

- `AUTO`
  Auto – Fit to the sensor width or height depending on image resolution.
- `HORIZONTAL`
  Horizontal – Fit to the sensor width.
- `VERTICAL`
  Vertical – Fit to the sensor height.

**Type:**

Literal[‘AUTO’, ‘HORIZONTAL’, ‘VERTICAL’]

<a id="bpy.types.Camera.sensor_height"></a>

#### bpy.types.Camera.sensor_height

Vertical size of the image sensor area in millimeters (in [1, inf], default 24.0)

**Type:**

float

<a id="bpy.types.Camera.sensor_width"></a>

#### bpy.types.Camera.sensor_width

Horizontal size of the image sensor area in millimeters (in [1, inf], default 36.0)

**Type:**

float

<a id="bpy.types.Camera.shift_x"></a>

#### bpy.types.Camera.shift_x

Camera horizontal shift (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.Camera.shift_y"></a>

#### bpy.types.Camera.shift_y

Camera vertical shift (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.Camera.show_background_images"></a>

#### bpy.types.Camera.show_background_images

Display reference images behind objects in the 3D View (default False)

**Type:**

bool

<a id="bpy.types.Camera.show_composition_center"></a>

#### bpy.types.Camera.show_composition_center

Display center composition guide inside the camera view (default False)

**Type:**

bool

<a id="bpy.types.Camera.show_composition_center_diagonal"></a>

#### bpy.types.Camera.show_composition_center_diagonal

Display diagonal center composition guide inside the camera view (default False)

**Type:**

bool

<a id="bpy.types.Camera.show_composition_golden"></a>

#### bpy.types.Camera.show_composition_golden

Display golden ratio composition guide inside the camera view (default False)

**Type:**

bool

<a id="bpy.types.Camera.show_composition_golden_tria_a"></a>

#### bpy.types.Camera.show_composition_golden_tria_a

Display golden triangle A composition guide inside the camera view (default False)

**Type:**

bool

<a id="bpy.types.Camera.show_composition_golden_tria_b"></a>

#### bpy.types.Camera.show_composition_golden_tria_b

Display golden triangle B composition guide inside the camera view (default False)

**Type:**

bool

<a id="bpy.types.Camera.show_composition_harmony_tri_a"></a>

#### bpy.types.Camera.show_composition_harmony_tri_a

Display harmony A composition guide inside the camera view (default False)

**Type:**

bool

<a id="bpy.types.Camera.show_composition_harmony_tri_b"></a>

#### bpy.types.Camera.show_composition_harmony_tri_b

Display harmony B composition guide inside the camera view (default False)

**Type:**

bool

<a id="bpy.types.Camera.show_composition_thirds"></a>

#### bpy.types.Camera.show_composition_thirds

Display rule of thirds composition guide inside the camera view (default False)

**Type:**

bool

<a id="bpy.types.Camera.show_limits"></a>

#### bpy.types.Camera.show_limits

Display the clipping range and focus point on the camera (default False)

**Type:**

bool

<a id="bpy.types.Camera.show_mist"></a>

#### bpy.types.Camera.show_mist

Display a line from the Camera to indicate the mist area (default False)

**Type:**

bool

<a id="bpy.types.Camera.show_name"></a>

#### bpy.types.Camera.show_name

Show the active Camera’s name in Camera view (default False)

**Type:**

bool

<a id="bpy.types.Camera.show_passepartout"></a>

#### bpy.types.Camera.show_passepartout

Show a darkened overlay outside the image area in Camera view (default True)

**Type:**

bool

<a id="bpy.types.Camera.show_safe_areas"></a>

#### bpy.types.Camera.show_safe_areas

Show TV title safe and action safe areas in Camera view (default False)

**Type:**

bool

<a id="bpy.types.Camera.show_safe_center"></a>

#### bpy.types.Camera.show_safe_center

Show safe areas to fit content in a different aspect ratio (default False)

**Type:**

bool

<a id="bpy.types.Camera.show_sensor"></a>

#### bpy.types.Camera.show_sensor

Show sensor size (film gate) in Camera view (default False)

**Type:**

bool

<a id="bpy.types.Camera.stereo"></a>

#### bpy.types.Camera.stereo

(readonly, never None)

**Type:**

[`CameraStereoData`](bpy.types.CameraStereoData.md#bpy.types.CameraStereoData "bpy.types.CameraStereoData")

<a id="bpy.types.Camera.type"></a>

#### bpy.types.Camera.type

Camera types (default `'PERSP'`)

**Type:**

Literal[‘PERSP’, ‘ORTHO’, ‘PANO’, ‘CUSTOM’]

<a id="bpy.types.Camera.view_frame"></a>

#### bpy.types.Camera.view_frame(*, scene=None)

Return 4 points for the cameras frame (before object transformation)

**Parameters:**

**scene** ([`Scene`](bpy.types.Scene.md#bpy.types.Scene "bpy.types.Scene") | None) – Scene to use for aspect calculation, when omitted 1:1 aspect is used (optional)

**Returns:**

`result_1`, Result, [`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

`result_2`, Result, [`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

`result_3`, Result, [`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

`result_4`, Result, [`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

**Return type:**

tuple[[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector"), [`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector"), [`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector"), [`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")]

<a id="bpy.types.Camera.bl_rna_get_subclass"></a>

#### classmethod bpy.types.Camera.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.Camera.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.Camera.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([type](#bpy.types.Camera.type "bpy.types.Camera.type") | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

[type](#bpy.types.Camera.type "bpy.types.Camera.type")

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
| - `bpy.context.camera` - [`BlendData.cameras`](bpy.types.BlendData.md#bpy.types.BlendData.cameras "bpy.types.BlendData.cameras") - [`BlendDataCameras.new`](bpy.types.BlendDataCameras.md#bpy.types.BlendDataCameras.new "bpy.types.BlendDataCameras.new") | - [`BlendDataCameras.remove`](bpy.types.BlendDataCameras.md#bpy.types.BlendDataCameras.remove "bpy.types.BlendDataCameras.remove") - [`RenderEngine.update_custom_camera`](bpy.types.RenderEngine.md#bpy.types.RenderEngine.update_custom_camera "bpy.types.RenderEngine.update_custom_camera") |
