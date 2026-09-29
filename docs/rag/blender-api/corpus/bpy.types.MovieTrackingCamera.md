<!-- source: Blender Python API reference 5.2 / bpy.types.MovieTrackingCamera.html -->

<a id="movietrackingcamera-bpy-struct"></a>

# MovieTrackingCamera(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.MovieTrackingCamera"></a>

### class bpy.types.MovieTrackingCamera(bpy_struct)

Match-moving camera data for tracking

<a id="bpy.types.MovieTrackingCamera.brown_k1"></a>

#### bpy.types.MovieTrackingCamera.brown_k1

First coefficient of fourth order Brown-Conrady radial distortion (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.MovieTrackingCamera.brown_k2"></a>

#### bpy.types.MovieTrackingCamera.brown_k2

Second coefficient of fourth order Brown-Conrady radial distortion (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.MovieTrackingCamera.brown_k3"></a>

#### bpy.types.MovieTrackingCamera.brown_k3

Third coefficient of fourth order Brown-Conrady radial distortion (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.MovieTrackingCamera.brown_k4"></a>

#### bpy.types.MovieTrackingCamera.brown_k4

Fourth coefficient of fourth order Brown-Conrady radial distortion (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.MovieTrackingCamera.brown_p1"></a>

#### bpy.types.MovieTrackingCamera.brown_p1

First coefficient of second order Brown-Conrady tangential distortion (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.MovieTrackingCamera.brown_p2"></a>

#### bpy.types.MovieTrackingCamera.brown_p2

Second coefficient of second order Brown-Conrady tangential distortion (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.MovieTrackingCamera.distortion_model"></a>

#### bpy.types.MovieTrackingCamera.distortion_model

Distortion model used for camera lenses (default `'POLYNOMIAL'`)

- `POLYNOMIAL`
  Polynomial – Radial distortion model which fits common cameras.
- `DIVISION`
  Divisions – Division distortion model which better represents wide-angle cameras.
- `NUKE`
  Nuke – Nuke distortion model.
- `BROWN`
  Brown – Brown-Conrady distortion model.

**Type:**

Literal[‘POLYNOMIAL’, ‘DIVISION’, ‘NUKE’, ‘BROWN’]

<a id="bpy.types.MovieTrackingCamera.division_k1"></a>

#### bpy.types.MovieTrackingCamera.division_k1

First coefficient of second order division distortion (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.MovieTrackingCamera.division_k2"></a>

#### bpy.types.MovieTrackingCamera.division_k2

Second coefficient of second order division distortion (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.MovieTrackingCamera.focal_length"></a>

#### bpy.types.MovieTrackingCamera.focal_length

Camera’s focal length (in [0.0001, inf], default 0.0)

**Type:**

float

<a id="bpy.types.MovieTrackingCamera.focal_length_pixels"></a>

#### bpy.types.MovieTrackingCamera.focal_length_pixels

Camera’s focal length (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.MovieTrackingCamera.k1"></a>

#### bpy.types.MovieTrackingCamera.k1

First coefficient of third order polynomial radial distortion (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.MovieTrackingCamera.k2"></a>

#### bpy.types.MovieTrackingCamera.k2

Second coefficient of third order polynomial radial distortion (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.MovieTrackingCamera.k3"></a>

#### bpy.types.MovieTrackingCamera.k3

Third coefficient of third order polynomial radial distortion (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.MovieTrackingCamera.nuke_k1"></a>

#### bpy.types.MovieTrackingCamera.nuke_k1

First coefficient of second order Nuke distortion (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.MovieTrackingCamera.nuke_k2"></a>

#### bpy.types.MovieTrackingCamera.nuke_k2

Second coefficient of second order Nuke distortion (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.MovieTrackingCamera.nuke_p1"></a>

#### bpy.types.MovieTrackingCamera.nuke_p1

First coefficient of tangential Nuke distortion (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.MovieTrackingCamera.nuke_p2"></a>

#### bpy.types.MovieTrackingCamera.nuke_p2

Second coefficient of tangential Nuke distortion (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.MovieTrackingCamera.pixel_aspect"></a>

#### bpy.types.MovieTrackingCamera.pixel_aspect

Pixel aspect ratio (in [0.1, inf], default 1.0)

**Type:**

float

<a id="bpy.types.MovieTrackingCamera.principal_point"></a>

#### bpy.types.MovieTrackingCamera.principal_point

Optical center of lens (array of 2 items, in [-1, 1], default (0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.MovieTrackingCamera.principal_point_pixels"></a>

#### bpy.types.MovieTrackingCamera.principal_point_pixels

Optical center of lens in pixels (array of 2 items, in [-inf, inf], default (0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.MovieTrackingCamera.sensor_width"></a>

#### bpy.types.MovieTrackingCamera.sensor_width

Width of CCD sensor in millimeters (in [0, 500], default 0.0)

**Type:**

float

<a id="bpy.types.MovieTrackingCamera.units"></a>

#### bpy.types.MovieTrackingCamera.units

Units used for camera focal length (default `'PIXELS'`)

- `PIXELS`
  px – Use pixels for units of focal length.
- `MILLIMETERS`
  mm – Use millimeters for units of focal length.

**Type:**

Literal[‘PIXELS’, ‘MILLIMETERS’]

<a id="bpy.types.MovieTrackingCamera.bl_rna_get_subclass"></a>

#### classmethod bpy.types.MovieTrackingCamera.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.MovieTrackingCamera.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.MovieTrackingCamera.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`MovieTracking.camera`](bpy.types.MovieTracking.md#bpy.types.MovieTracking.camera "bpy.types.MovieTracking.camera") |  |
