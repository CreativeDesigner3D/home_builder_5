<!-- source: Blender Python API reference 5.2 / bpy.types.FollowTrackConstraint.html -->

<a id="followtrackconstraint-constraint"></a>

# FollowTrackConstraint(Constraint)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Constraint`](bpy.types.Constraint.md#bpy.types.Constraint "bpy.types.Constraint")

<a id="bpy.types.FollowTrackConstraint"></a>

### class bpy.types.FollowTrackConstraint(Constraint)

Lock motion to the target motion track

<a id="bpy.types.FollowTrackConstraint.camera"></a>

#### bpy.types.FollowTrackConstraint.camera

Camera to which motion is parented (if empty active scene camera is used)

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.FollowTrackConstraint.clip"></a>

#### bpy.types.FollowTrackConstraint.clip

Movie Clip to get tracking data from

**Type:**

[`MovieClip`](bpy.types.MovieClip.md#bpy.types.MovieClip "bpy.types.MovieClip") | None

<a id="bpy.types.FollowTrackConstraint.depth_object"></a>

#### bpy.types.FollowTrackConstraint.depth_object

Object used to define depth in camera space by projecting onto surface of this object

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.FollowTrackConstraint.frame_method"></a>

#### bpy.types.FollowTrackConstraint.frame_method

How the footage fits in the camera frame (default `'STRETCH'`)

**Type:**

Literal[‘STRETCH’, ‘FIT’, ‘CROP’]

<a id="bpy.types.FollowTrackConstraint.object"></a>

#### bpy.types.FollowTrackConstraint.object

Movie tracking object to follow (if empty, camera object is used) (default “”, never None)

**Type:**

str

<a id="bpy.types.FollowTrackConstraint.track"></a>

#### bpy.types.FollowTrackConstraint.track

Movie tracking track to follow (default “”, never None)

**Type:**

str

<a id="bpy.types.FollowTrackConstraint.use_3d_position"></a>

#### bpy.types.FollowTrackConstraint.use_3d_position

Use 3D position of track to parent to (default False)

**Type:**

bool

<a id="bpy.types.FollowTrackConstraint.use_active_clip"></a>

#### bpy.types.FollowTrackConstraint.use_active_clip

Use active clip defined in scene (default False)

**Type:**

bool

<a id="bpy.types.FollowTrackConstraint.use_undistorted_position"></a>

#### bpy.types.FollowTrackConstraint.use_undistorted_position

Parent to undistorted position of 2D track (default False)

**Type:**

bool

<a id="bpy.types.FollowTrackConstraint.bl_rna_get_subclass"></a>

#### classmethod bpy.types.FollowTrackConstraint.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.FollowTrackConstraint.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.FollowTrackConstraint.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, Constraint.name, Constraint.type, Constraint.is_override_data, Constraint.owner_space, Constraint.target_space, Constraint.space_object, Constraint.space_subtarget, Constraint.mute, Constraint.enabled, Constraint.show_expanded, Constraint.is_valid, Constraint.active, Constraint.influence, Constraint.error_location, Constraint.error_rotation

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, Constraint.bl_rna_get_subclass, Constraint.bl_rna_get_subclass_py
