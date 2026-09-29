<!-- source: Blender Python API reference 5.2 / bpy.types.MovieTrackingObject.html -->

<a id="movietrackingobject-bpy-struct"></a>

# MovieTrackingObject(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.MovieTrackingObject"></a>

### class bpy.types.MovieTrackingObject(bpy_struct)

Match-moving object tracking and reconstruction data

<a id="bpy.types.MovieTrackingObject.is_camera"></a>

#### bpy.types.MovieTrackingObject.is_camera

Object is used for camera tracking (default False, readonly)

**Type:**

bool

<a id="bpy.types.MovieTrackingObject.keyframe_a"></a>

#### bpy.types.MovieTrackingObject.keyframe_a

First keyframe used for reconstruction initialization (in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.MovieTrackingObject.keyframe_b"></a>

#### bpy.types.MovieTrackingObject.keyframe_b

Second keyframe used for reconstruction initialization (in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.MovieTrackingObject.name"></a>

#### bpy.types.MovieTrackingObject.name

Unique name of object (default “”, never None)

**Type:**

str

<a id="bpy.types.MovieTrackingObject.plane_tracks"></a>

#### bpy.types.MovieTrackingObject.plane_tracks

Collection of plane tracks in this tracking data object (default None, readonly)

**Type:**

[`MovieTrackingObjectPlaneTracks`](bpy.types.MovieTrackingObjectPlaneTracks.md#bpy.types.MovieTrackingObjectPlaneTracks "bpy.types.MovieTrackingObjectPlaneTracks")[[`MovieTrackingPlaneTrack`](bpy.types.MovieTrackingPlaneTrack.md#bpy.types.MovieTrackingPlaneTrack "bpy.types.MovieTrackingPlaneTrack")]

<a id="bpy.types.MovieTrackingObject.reconstruction"></a>

#### bpy.types.MovieTrackingObject.reconstruction

(readonly)

**Type:**

[`MovieTrackingReconstruction`](bpy.types.MovieTrackingReconstruction.md#bpy.types.MovieTrackingReconstruction "bpy.types.MovieTrackingReconstruction") | None

<a id="bpy.types.MovieTrackingObject.scale"></a>

#### bpy.types.MovieTrackingObject.scale

Scale of object solution in camera space (in [0.0001, 10000], default 1.0)

**Type:**

float

<a id="bpy.types.MovieTrackingObject.tracks"></a>

#### bpy.types.MovieTrackingObject.tracks

Collection of tracks in this tracking data object (default None, readonly)

**Type:**

[`MovieTrackingObjectTracks`](bpy.types.MovieTrackingObjectTracks.md#bpy.types.MovieTrackingObjectTracks "bpy.types.MovieTrackingObjectTracks")[[`MovieTrackingTrack`](bpy.types.MovieTrackingTrack.md#bpy.types.MovieTrackingTrack "bpy.types.MovieTrackingTrack")]

<a id="bpy.types.MovieTrackingObject.bl_rna_get_subclass"></a>

#### classmethod bpy.types.MovieTrackingObject.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.MovieTrackingObject.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.MovieTrackingObject.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`MovieTracking.objects`](bpy.types.MovieTracking.md#bpy.types.MovieTracking.objects "bpy.types.MovieTracking.objects") - [`MovieTrackingObjects.active`](bpy.types.MovieTrackingObjects.md#bpy.types.MovieTrackingObjects.active "bpy.types.MovieTrackingObjects.active") | - [`MovieTrackingObjects.new`](bpy.types.MovieTrackingObjects.md#bpy.types.MovieTrackingObjects.new "bpy.types.MovieTrackingObjects.new") - [`MovieTrackingObjects.remove`](bpy.types.MovieTrackingObjects.md#bpy.types.MovieTrackingObjects.remove "bpy.types.MovieTrackingObjects.remove") |
