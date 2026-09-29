<!-- source: Blender Python API reference 5.2 / bpy.types.MovieTrackingPlaneMarker.html -->

<a id="movietrackingplanemarker-bpy-struct"></a>

# MovieTrackingPlaneMarker(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.MovieTrackingPlaneMarker"></a>

### class bpy.types.MovieTrackingPlaneMarker(bpy_struct)

Match-moving plane marker data for tracking

<a id="bpy.types.MovieTrackingPlaneMarker.corners"></a>

#### bpy.types.MovieTrackingPlaneMarker.corners

Array of coordinates which represents UI rectangle corners in frame normalized coordinates (multi-dimensional array of 4 * 2 items, in [-inf, inf], default ((0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0)))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]]

<a id="bpy.types.MovieTrackingPlaneMarker.frame"></a>

#### bpy.types.MovieTrackingPlaneMarker.frame

Frame number marker is keyframed on (in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.MovieTrackingPlaneMarker.mute"></a>

#### bpy.types.MovieTrackingPlaneMarker.mute

Is marker muted for current frame (default False)

**Type:**

bool

<a id="bpy.types.MovieTrackingPlaneMarker.bl_rna_get_subclass"></a>

#### classmethod bpy.types.MovieTrackingPlaneMarker.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.MovieTrackingPlaneMarker.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.MovieTrackingPlaneMarker.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`MovieTrackingPlaneMarkers.find_frame`](bpy.types.MovieTrackingPlaneMarkers.md#bpy.types.MovieTrackingPlaneMarkers.find_frame "bpy.types.MovieTrackingPlaneMarkers.find_frame") - [`MovieTrackingPlaneMarkers.insert_frame`](bpy.types.MovieTrackingPlaneMarkers.md#bpy.types.MovieTrackingPlaneMarkers.insert_frame "bpy.types.MovieTrackingPlaneMarkers.insert_frame") | - [`MovieTrackingPlaneTrack.markers`](bpy.types.MovieTrackingPlaneTrack.md#bpy.types.MovieTrackingPlaneTrack.markers "bpy.types.MovieTrackingPlaneTrack.markers") |
