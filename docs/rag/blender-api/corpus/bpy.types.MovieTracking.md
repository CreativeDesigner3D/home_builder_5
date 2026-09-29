<!-- source: Blender Python API reference 5.2 / bpy.types.MovieTracking.html -->

<a id="movietracking-bpy-struct"></a>

# MovieTracking(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.MovieTracking"></a>

### class bpy.types.MovieTracking(bpy_struct)

Match-moving data for tracking

<a id="bpy.types.MovieTracking.active_object_index"></a>

#### bpy.types.MovieTracking.active_object_index

Index of active object (in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.MovieTracking.camera"></a>

#### bpy.types.MovieTracking.camera

(readonly)

**Type:**

[`MovieTrackingCamera`](bpy.types.MovieTrackingCamera.md#bpy.types.MovieTrackingCamera "bpy.types.MovieTrackingCamera") | None

<a id="bpy.types.MovieTracking.dopesheet"></a>

#### bpy.types.MovieTracking.dopesheet

(readonly)

**Type:**

[`MovieTrackingDopesheet`](bpy.types.MovieTrackingDopesheet.md#bpy.types.MovieTrackingDopesheet "bpy.types.MovieTrackingDopesheet") | None

<a id="bpy.types.MovieTracking.objects"></a>

#### bpy.types.MovieTracking.objects

Collection of objects in this tracking data object (default None, readonly)

**Type:**

[`MovieTrackingObjects`](bpy.types.MovieTrackingObjects.md#bpy.types.MovieTrackingObjects "bpy.types.MovieTrackingObjects")[[`MovieTrackingObject`](bpy.types.MovieTrackingObject.md#bpy.types.MovieTrackingObject "bpy.types.MovieTrackingObject")]

<a id="bpy.types.MovieTracking.plane_tracks"></a>

#### bpy.types.MovieTracking.plane_tracks

Collection of plane tracks in this tracking data object. Deprecated, use objects[name].plane_tracks (default None, readonly)

**Type:**

[`MovieTrackingPlaneTracks`](bpy.types.MovieTrackingPlaneTracks.md#bpy.types.MovieTrackingPlaneTracks "bpy.types.MovieTrackingPlaneTracks")[[`MovieTrackingPlaneTrack`](bpy.types.MovieTrackingPlaneTrack.md#bpy.types.MovieTrackingPlaneTrack "bpy.types.MovieTrackingPlaneTrack")]

<a id="bpy.types.MovieTracking.reconstruction"></a>

#### bpy.types.MovieTracking.reconstruction

(readonly)

**Type:**

[`MovieTrackingReconstruction`](bpy.types.MovieTrackingReconstruction.md#bpy.types.MovieTrackingReconstruction "bpy.types.MovieTrackingReconstruction") | None

<a id="bpy.types.MovieTracking.settings"></a>

#### bpy.types.MovieTracking.settings

(readonly)

**Type:**

[`MovieTrackingSettings`](bpy.types.MovieTrackingSettings.md#bpy.types.MovieTrackingSettings "bpy.types.MovieTrackingSettings") | None

<a id="bpy.types.MovieTracking.stabilization"></a>

#### bpy.types.MovieTracking.stabilization

(readonly)

**Type:**

[`MovieTrackingStabilization`](bpy.types.MovieTrackingStabilization.md#bpy.types.MovieTrackingStabilization "bpy.types.MovieTrackingStabilization") | None

<a id="bpy.types.MovieTracking.tracks"></a>

#### bpy.types.MovieTracking.tracks

Collection of tracks in this tracking data object. Deprecated, use objects[name].tracks (default None, readonly)

**Type:**

[`MovieTrackingTracks`](bpy.types.MovieTrackingTracks.md#bpy.types.MovieTrackingTracks "bpy.types.MovieTrackingTracks")[[`MovieTrackingTrack`](bpy.types.MovieTrackingTrack.md#bpy.types.MovieTrackingTrack "bpy.types.MovieTrackingTrack")]

<a id="bpy.types.MovieTracking.bl_rna_get_subclass"></a>

#### classmethod bpy.types.MovieTracking.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.MovieTracking.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.MovieTracking.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`MovieClip.tracking`](bpy.types.MovieClip.md#bpy.types.MovieClip.tracking "bpy.types.MovieClip.tracking") |  |
