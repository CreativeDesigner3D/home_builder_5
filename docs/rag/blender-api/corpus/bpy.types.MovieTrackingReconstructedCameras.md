<!-- source: Blender Python API reference 5.2 / bpy.types.MovieTrackingReconstructedCameras.html -->

<a id="movietrackingreconstructedcameras-bpy-prop-collection"></a>

# MovieTrackingReconstructedCameras(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.MovieTrackingReconstructedCameras"></a>

### class bpy.types.MovieTrackingReconstructedCameras(bpy_prop_collection)

Collection of solved cameras

<a id="bpy.types.MovieTrackingReconstructedCameras.find_frame"></a>

#### bpy.types.MovieTrackingReconstructedCameras.find_frame(*, frame=1)

Find a reconstructed camera for a give frame number

**Parameters:**

**frame** (int) – Frame, Frame number to find camera for (in [0, 1048574], optional)

**Returns:**

Camera for a given frame

**Return type:**

[`MovieReconstructedCamera`](bpy.types.MovieReconstructedCamera.md#bpy.types.MovieReconstructedCamera "bpy.types.MovieReconstructedCamera")

<a id="bpy.types.MovieTrackingReconstructedCameras.matrix_from_frame"></a>

#### bpy.types.MovieTrackingReconstructedCameras.matrix_from_frame(*, frame=1)

Return interpolated camera matrix for a given frame

**Parameters:**

**frame** (int) – Frame, Frame number to find camera for (in [0, 1048574], optional)

**Returns:**

Matrix, Interpolated camera matrix for a given frame (multi-dimensional array of 4 * 4 items, in [-inf, inf])

**Return type:**

[`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")

<a id="bpy.types.MovieTrackingReconstructedCameras.bl_rna_get_subclass"></a>

#### classmethod bpy.types.MovieTrackingReconstructedCameras.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.MovieTrackingReconstructedCameras.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.MovieTrackingReconstructedCameras.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`MovieTrackingReconstruction.cameras`](bpy.types.MovieTrackingReconstruction.md#bpy.types.MovieTrackingReconstruction.cameras "bpy.types.MovieTrackingReconstruction.cameras") |  |
