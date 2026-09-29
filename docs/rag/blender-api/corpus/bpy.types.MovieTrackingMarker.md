<!-- source: Blender Python API reference 5.2 / bpy.types.MovieTrackingMarker.html -->

<a id="movietrackingmarker-bpy-struct"></a>

# MovieTrackingMarker(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.MovieTrackingMarker"></a>

### class bpy.types.MovieTrackingMarker(bpy_struct)

Match-moving marker data for tracking

<a id="bpy.types.MovieTrackingMarker.co"></a>

#### bpy.types.MovieTrackingMarker.co

Marker position at frame in normalized coordinates (array of 2 items, in [-inf, inf], default (0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.MovieTrackingMarker.frame"></a>

#### bpy.types.MovieTrackingMarker.frame

Frame number marker is keyframed on (in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.MovieTrackingMarker.is_keyed"></a>

#### bpy.types.MovieTrackingMarker.is_keyed

Whether the position of the marker is keyframed or tracked (default True)

**Type:**

bool

<a id="bpy.types.MovieTrackingMarker.mute"></a>

#### bpy.types.MovieTrackingMarker.mute

Is marker muted for current frame (default False)

**Type:**

bool

<a id="bpy.types.MovieTrackingMarker.pattern_bound_box"></a>

#### bpy.types.MovieTrackingMarker.pattern_bound_box

Pattern area bounding box in normalized coordinates (multi-dimensional array of 2 * 2 items, in [-inf, inf], default ((0.0, 0.0), (0.0, 0.0)), readonly)

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]]

<a id="bpy.types.MovieTrackingMarker.pattern_corners"></a>

#### bpy.types.MovieTrackingMarker.pattern_corners

Array of coordinates which represents pattern’s corners in normalized coordinates relative to marker position (multi-dimensional array of 4 * 2 items, in [-inf, inf], default ((0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0)))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]]

<a id="bpy.types.MovieTrackingMarker.search_max"></a>

#### bpy.types.MovieTrackingMarker.search_max

Right-bottom corner of search area in normalized coordinates relative to marker position (array of 2 items, in [-inf, inf], default (0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.MovieTrackingMarker.search_min"></a>

#### bpy.types.MovieTrackingMarker.search_min

Left-bottom corner of search area in normalized coordinates relative to marker position (array of 2 items, in [-inf, inf], default (0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.MovieTrackingMarker.bl_rna_get_subclass"></a>

#### classmethod bpy.types.MovieTrackingMarker.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.MovieTrackingMarker.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.MovieTrackingMarker.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`MovieTrackingMarkers.find_frame`](bpy.types.MovieTrackingMarkers.md#bpy.types.MovieTrackingMarkers.find_frame "bpy.types.MovieTrackingMarkers.find_frame") - [`MovieTrackingMarkers.insert_frame`](bpy.types.MovieTrackingMarkers.md#bpy.types.MovieTrackingMarkers.insert_frame "bpy.types.MovieTrackingMarkers.insert_frame") | - [`MovieTrackingTrack.markers`](bpy.types.MovieTrackingTrack.md#bpy.types.MovieTrackingTrack.markers "bpy.types.MovieTrackingTrack.markers") |
