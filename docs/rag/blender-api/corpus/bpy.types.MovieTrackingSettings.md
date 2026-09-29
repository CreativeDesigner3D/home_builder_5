<!-- source: Blender Python API reference 5.2 / bpy.types.MovieTrackingSettings.html -->

<a id="movietrackingsettings-bpy-struct"></a>

# MovieTrackingSettings(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.MovieTrackingSettings"></a>

### class bpy.types.MovieTrackingSettings(bpy_struct)

Match moving settings

<a id="bpy.types.MovieTrackingSettings.clean_action"></a>

#### bpy.types.MovieTrackingSettings.clean_action

Cleanup action to execute (default `'SELECT'`)

- `SELECT`
  Select – Select unclean tracks.
- `DELETE_TRACK`
  Delete Track – Delete unclean tracks.
- `DELETE_SEGMENTS`
  Delete Segments – Delete unclean segments of tracks.

**Type:**

Literal[‘SELECT’, ‘DELETE_TRACK’, ‘DELETE_SEGMENTS’]

<a id="bpy.types.MovieTrackingSettings.clean_error"></a>

#### bpy.types.MovieTrackingSettings.clean_error

Effect on tracks which have a larger re-projection error (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.MovieTrackingSettings.clean_frames"></a>

#### bpy.types.MovieTrackingSettings.clean_frames

Effect on tracks which are tracked less than the specified amount of frames (in [0, inf], default 0)

**Type:**

int

<a id="bpy.types.MovieTrackingSettings.default_correlation_min"></a>

#### bpy.types.MovieTrackingSettings.default_correlation_min

Default minimum value of correlation between matched pattern and reference that is still treated as successful tracking (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.MovieTrackingSettings.default_frames_limit"></a>

#### bpy.types.MovieTrackingSettings.default_frames_limit

Every tracking cycle, this number of frames are tracked (in [0, 32767], default 0)

**Type:**

int

<a id="bpy.types.MovieTrackingSettings.default_margin"></a>

#### bpy.types.MovieTrackingSettings.default_margin

Default distance from image boundary at which marker stops tracking (in [0, 300], default 0)

**Type:**

int

<a id="bpy.types.MovieTrackingSettings.default_motion_model"></a>

#### bpy.types.MovieTrackingSettings.default_motion_model

Default motion model to use for tracking (default `'Loc'`)

- `Perspective`
  Perspective – Search for markers that are perspectively deformed (homography) between frames.
- `Affine`
  Affine – Search for markers that are affine-deformed (t, r, k, and skew) between frames.
- `LocRotScale`
  Location, Rotation & Scale – Search for markers that are translated, rotated, and scaled between frames.
- `LocScale`
  Location & Scale – Search for markers that are translated and scaled between frames.
- `LocRot`
  Location & Rotation – Search for markers that are translated and rotated between frames.
- `Loc`
  Location – Search for markers that are translated between frames.

**Type:**

Literal[‘Perspective’, ‘Affine’, ‘LocRotScale’, ‘LocScale’, ‘LocRot’, ‘Loc’]

<a id="bpy.types.MovieTrackingSettings.default_pattern_match"></a>

#### bpy.types.MovieTrackingSettings.default_pattern_match

Track pattern from given frame when tracking marker to next frame (default `'KEYFRAME'`)

- `KEYFRAME`
  Keyframe – Track pattern from keyframe to next frame.
- `PREV_FRAME`
  Previous frame – Track pattern from current frame to next frame.

**Type:**

Literal[‘KEYFRAME’, ‘PREV_FRAME’]

<a id="bpy.types.MovieTrackingSettings.default_pattern_size"></a>

#### bpy.types.MovieTrackingSettings.default_pattern_size

Size of pattern area for newly created tracks (in [5, 1000], default 0)

**Type:**

int

<a id="bpy.types.MovieTrackingSettings.default_search_size"></a>

#### bpy.types.MovieTrackingSettings.default_search_size

Size of search area for newly created tracks (in [5, 1000], default 0)

**Type:**

int

<a id="bpy.types.MovieTrackingSettings.default_weight"></a>

#### bpy.types.MovieTrackingSettings.default_weight

Influence of newly created track on a final solution (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.MovieTrackingSettings.distance"></a>

#### bpy.types.MovieTrackingSettings.distance

Distance between two bundles used for scene scaling (in [-inf, inf], default 1.0)

**Type:**

float

<a id="bpy.types.MovieTrackingSettings.object_distance"></a>

#### bpy.types.MovieTrackingSettings.object_distance

Distance between two bundles used for object scaling (in [0.001, 10000], default 1.0)

**Type:**

float

<a id="bpy.types.MovieTrackingSettings.refine_intrinsics_focal_length"></a>

#### bpy.types.MovieTrackingSettings.refine_intrinsics_focal_length

Refine focal length during camera solving (default False)

**Type:**

bool

<a id="bpy.types.MovieTrackingSettings.refine_intrinsics_principal_point"></a>

#### bpy.types.MovieTrackingSettings.refine_intrinsics_principal_point

Refine principal point during camera solving (default False)

**Type:**

bool

<a id="bpy.types.MovieTrackingSettings.refine_intrinsics_radial_distortion"></a>

#### bpy.types.MovieTrackingSettings.refine_intrinsics_radial_distortion

Refine radial coefficients of distortion model during camera solving (default False)

**Type:**

bool

<a id="bpy.types.MovieTrackingSettings.refine_intrinsics_tangential_distortion"></a>

#### bpy.types.MovieTrackingSettings.refine_intrinsics_tangential_distortion

Refine tangential coefficients of distortion model during camera solving (default False)

**Type:**

bool

<a id="bpy.types.MovieTrackingSettings.speed"></a>

#### bpy.types.MovieTrackingSettings.speed

Limit speed of tracking to make visual feedback easier (this does not affect the tracking quality) (default `'FASTEST'`)

- `FASTEST`
  Fastest – Track as fast as possible.
- `DOUBLE`
  Double – Track with double speed.
- `REALTIME`
  Realtime – Track with realtime speed.
- `HALF`
  Half – Track with half of realtime speed.
- `QUARTER`
  Quarter – Track with quarter of realtime speed.

**Type:**

Literal[‘FASTEST’, ‘DOUBLE’, ‘REALTIME’, ‘HALF’, ‘QUARTER’]

<a id="bpy.types.MovieTrackingSettings.use_default_blue_channel"></a>

#### bpy.types.MovieTrackingSettings.use_default_blue_channel

Use blue channel from footage for tracking (default True)

**Type:**

bool

<a id="bpy.types.MovieTrackingSettings.use_default_brute"></a>

#### bpy.types.MovieTrackingSettings.use_default_brute

Use a brute-force translation-only initialization when tracking (default False)

**Type:**

bool

<a id="bpy.types.MovieTrackingSettings.use_default_green_channel"></a>

#### bpy.types.MovieTrackingSettings.use_default_green_channel

Use green channel from footage for tracking (default True)

**Type:**

bool

<a id="bpy.types.MovieTrackingSettings.use_default_mask"></a>

#### bpy.types.MovieTrackingSettings.use_default_mask

Use a Grease Pencil data-block as a mask to use only specified areas of pattern when tracking (default False)

**Type:**

bool

<a id="bpy.types.MovieTrackingSettings.use_default_normalization"></a>

#### bpy.types.MovieTrackingSettings.use_default_normalization

Normalize light intensities while tracking (slower) (default False)

**Type:**

bool

<a id="bpy.types.MovieTrackingSettings.use_default_red_channel"></a>

#### bpy.types.MovieTrackingSettings.use_default_red_channel

Use red channel from footage for tracking (default True)

**Type:**

bool

<a id="bpy.types.MovieTrackingSettings.use_keyframe_selection"></a>

#### bpy.types.MovieTrackingSettings.use_keyframe_selection

Automatically select keyframes when solving camera/object motion (default False)

**Type:**

bool

<a id="bpy.types.MovieTrackingSettings.use_tripod_solver"></a>

#### bpy.types.MovieTrackingSettings.use_tripod_solver

Use special solver to track a stable camera position, such as a tripod (default False)

**Type:**

bool

<a id="bpy.types.MovieTrackingSettings.bl_rna_get_subclass"></a>

#### classmethod bpy.types.MovieTrackingSettings.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.MovieTrackingSettings.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.MovieTrackingSettings.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`MovieTracking.settings`](bpy.types.MovieTracking.md#bpy.types.MovieTracking.settings "bpy.types.MovieTracking.settings") |  |
