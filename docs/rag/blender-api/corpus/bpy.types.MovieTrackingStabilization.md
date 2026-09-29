<!-- source: Blender Python API reference 5.2 / bpy.types.MovieTrackingStabilization.html -->

<a id="movietrackingstabilization-bpy-struct"></a>

# MovieTrackingStabilization(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.MovieTrackingStabilization"></a>

### class bpy.types.MovieTrackingStabilization(bpy_struct)

2D stabilization based on tracking markers

<a id="bpy.types.MovieTrackingStabilization.active_rotation_track_index"></a>

#### bpy.types.MovieTrackingStabilization.active_rotation_track_index

Index of active track in rotation stabilization tracks list (in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.MovieTrackingStabilization.active_track_index"></a>

#### bpy.types.MovieTrackingStabilization.active_track_index

Index of active track in translation stabilization tracks list (in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.MovieTrackingStabilization.anchor_frame"></a>

#### bpy.types.MovieTrackingStabilization.anchor_frame

Reference point to anchor stabilization (other frames will be adjusted relative to this frame’s position) (in [0, 1048574], default 0)

**Type:**

int

<a id="bpy.types.MovieTrackingStabilization.filter_type"></a>

#### bpy.types.MovieTrackingStabilization.filter_type

Interpolation to use for sub-pixel shifts and rotations due to stabilization (default `'NEAREST'`)

- `NEAREST`
  Nearest – No interpolation, use nearest neighbor pixel.
- `BILINEAR`
  Bilinear – Simple interpolation between adjacent pixels.
- `BICUBIC`
  Bicubic – High quality pixel interpolation.

**Type:**

Literal[‘NEAREST’, ‘BILINEAR’, ‘BICUBIC’]

<a id="bpy.types.MovieTrackingStabilization.influence_location"></a>

#### bpy.types.MovieTrackingStabilization.influence_location

Influence of stabilization algorithm on footage location (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.MovieTrackingStabilization.influence_rotation"></a>

#### bpy.types.MovieTrackingStabilization.influence_rotation

Influence of stabilization algorithm on footage rotation (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.MovieTrackingStabilization.influence_scale"></a>

#### bpy.types.MovieTrackingStabilization.influence_scale

Influence of stabilization algorithm on footage scale (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.MovieTrackingStabilization.rotation_tracks"></a>

#### bpy.types.MovieTrackingStabilization.rotation_tracks

Collection of tracks used for 2D stabilization (translation) (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`MovieTrackingTrack`](bpy.types.MovieTrackingTrack.md#bpy.types.MovieTrackingTrack "bpy.types.MovieTrackingTrack")]

<a id="bpy.types.MovieTrackingStabilization.scale_max"></a>

#### bpy.types.MovieTrackingStabilization.scale_max

Limit the amount of automatic scaling (in [0, 10], default 0.0)

**Type:**

float

<a id="bpy.types.MovieTrackingStabilization.show_tracks_expanded"></a>

#### bpy.types.MovieTrackingStabilization.show_tracks_expanded

Show UI list of tracks participating in stabilization (default False)

**Type:**

bool

<a id="bpy.types.MovieTrackingStabilization.target_position"></a>

#### bpy.types.MovieTrackingStabilization.target_position

Known relative offset of original shot, will be subtracted (e.g. for panning shot, can be animated) (array of 2 items, in [-inf, inf], default (0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.MovieTrackingStabilization.target_rotation"></a>

#### bpy.types.MovieTrackingStabilization.target_rotation

Rotation present on original shot, will be compensated (e.g. for deliberate tilting) (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.MovieTrackingStabilization.target_scale"></a>

#### bpy.types.MovieTrackingStabilization.target_scale

Explicitly scale resulting frame to compensate zoom of original shot (in [1.192e-07, inf], default 0.0)

**Type:**

float

<a id="bpy.types.MovieTrackingStabilization.tracks"></a>

#### bpy.types.MovieTrackingStabilization.tracks

Collection of tracks used for 2D stabilization (translation) (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`MovieTrackingTrack`](bpy.types.MovieTrackingTrack.md#bpy.types.MovieTrackingTrack "bpy.types.MovieTrackingTrack")]

<a id="bpy.types.MovieTrackingStabilization.use_2d_stabilization"></a>

#### bpy.types.MovieTrackingStabilization.use_2d_stabilization

Use 2D stabilization for footage (default False)

**Type:**

bool

<a id="bpy.types.MovieTrackingStabilization.use_autoscale"></a>

#### bpy.types.MovieTrackingStabilization.use_autoscale

Automatically scale footage to cover unfilled areas when stabilizing (default False)

**Type:**

bool

<a id="bpy.types.MovieTrackingStabilization.use_stabilize_rotation"></a>

#### bpy.types.MovieTrackingStabilization.use_stabilize_rotation

Stabilize detected rotation around center of frame (default False)

**Type:**

bool

<a id="bpy.types.MovieTrackingStabilization.use_stabilize_scale"></a>

#### bpy.types.MovieTrackingStabilization.use_stabilize_scale

Compensate any scale changes relative to center of rotation (default False)

**Type:**

bool

<a id="bpy.types.MovieTrackingStabilization.bl_rna_get_subclass"></a>

#### classmethod bpy.types.MovieTrackingStabilization.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.MovieTrackingStabilization.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.MovieTrackingStabilization.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`MovieTracking.stabilization`](bpy.types.MovieTracking.md#bpy.types.MovieTracking.stabilization "bpy.types.MovieTracking.stabilization") |  |
