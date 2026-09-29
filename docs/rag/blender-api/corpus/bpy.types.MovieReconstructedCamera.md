<!-- source: Blender Python API reference 5.2 / bpy.types.MovieReconstructedCamera.html -->

<a id="moviereconstructedcamera-bpy-struct"></a>

# MovieReconstructedCamera(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.MovieReconstructedCamera"></a>

### class bpy.types.MovieReconstructedCamera(bpy_struct)

Match-moving reconstructed camera data from tracker

<a id="bpy.types.MovieReconstructedCamera.average_error"></a>

#### bpy.types.MovieReconstructedCamera.average_error

Average error of reconstruction (in [-inf, inf], default 0.0, readonly)

**Type:**

float

<a id="bpy.types.MovieReconstructedCamera.frame"></a>

#### bpy.types.MovieReconstructedCamera.frame

Frame number marker is keyframed on (in [-inf, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.MovieReconstructedCamera.matrix"></a>

#### bpy.types.MovieReconstructedCamera.matrix

Worldspace transformation matrix (multi-dimensional array of 4 * 4 items, in [-inf, inf], default ((0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0)), readonly)

**Type:**

[`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")

<a id="bpy.types.MovieReconstructedCamera.bl_rna_get_subclass"></a>

#### classmethod bpy.types.MovieReconstructedCamera.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.MovieReconstructedCamera.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.MovieReconstructedCamera.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`MovieTrackingReconstructedCameras.find_frame`](bpy.types.MovieTrackingReconstructedCameras.md#bpy.types.MovieTrackingReconstructedCameras.find_frame "bpy.types.MovieTrackingReconstructedCameras.find_frame") | - [`MovieTrackingReconstruction.cameras`](bpy.types.MovieTrackingReconstruction.md#bpy.types.MovieTrackingReconstruction.cameras "bpy.types.MovieTrackingReconstruction.cameras") |
