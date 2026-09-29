<!-- source: Blender Python API reference 5.2 / bpy.types.MovieTrackingObjectTracks.html -->

<a id="movietrackingobjecttracks-bpy-prop-collection"></a>

# MovieTrackingObjectTracks(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.MovieTrackingObjectTracks"></a>

### class bpy.types.MovieTrackingObjectTracks(bpy_prop_collection)

Collection of movie tracking tracks

<a id="bpy.types.MovieTrackingObjectTracks.active"></a>

#### bpy.types.MovieTrackingObjectTracks.active

Active track in this tracking data object

**Type:**

[`MovieTrackingTrack`](bpy.types.MovieTrackingTrack.md#bpy.types.MovieTrackingTrack "bpy.types.MovieTrackingTrack") | None

<a id="bpy.types.MovieTrackingObjectTracks.new"></a>

#### bpy.types.MovieTrackingObjectTracks.new(*, name='', frame=1)

create new motion track in this movie clip

**Parameters:**

- **name** (str) – Name of new track (optional, never None)
- **frame** (int) – Frame, Frame number to add tracks on (in [0, 1048574], optional)

**Returns:**

Newly created track

**Return type:**

[`MovieTrackingTrack`](bpy.types.MovieTrackingTrack.md#bpy.types.MovieTrackingTrack "bpy.types.MovieTrackingTrack")

<a id="bpy.types.MovieTrackingObjectTracks.bl_rna_get_subclass"></a>

#### classmethod bpy.types.MovieTrackingObjectTracks.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.MovieTrackingObjectTracks.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.MovieTrackingObjectTracks.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`MovieTrackingObject.tracks`](bpy.types.MovieTrackingObject.md#bpy.types.MovieTrackingObject.tracks "bpy.types.MovieTrackingObject.tracks") |  |
