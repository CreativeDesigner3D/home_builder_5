<!-- source: Blender Python API reference 5.2 / bpy.types.ObjectSolverConstraint.html -->

<a id="objectsolverconstraint-constraint"></a>

# ObjectSolverConstraint(Constraint)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Constraint`](bpy.types.Constraint.md#bpy.types.Constraint "bpy.types.Constraint")

<a id="bpy.types.ObjectSolverConstraint"></a>

### class bpy.types.ObjectSolverConstraint(Constraint)

Lock motion to the reconstructed object movement

<a id="bpy.types.ObjectSolverConstraint.camera"></a>

#### bpy.types.ObjectSolverConstraint.camera

Camera to which motion is parented (if empty active scene camera is used)

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.ObjectSolverConstraint.clip"></a>

#### bpy.types.ObjectSolverConstraint.clip

Movie Clip to get tracking data from

**Type:**

[`MovieClip`](bpy.types.MovieClip.md#bpy.types.MovieClip "bpy.types.MovieClip") | None

<a id="bpy.types.ObjectSolverConstraint.object"></a>

#### bpy.types.ObjectSolverConstraint.object

Movie tracking object to follow (default “”, never None)

**Type:**

str

<a id="bpy.types.ObjectSolverConstraint.set_inverse_pending"></a>

#### bpy.types.ObjectSolverConstraint.set_inverse_pending

Set to true to request recalculation of the inverse matrix (default False)

**Type:**

bool

<a id="bpy.types.ObjectSolverConstraint.use_active_clip"></a>

#### bpy.types.ObjectSolverConstraint.use_active_clip

Use active clip defined in scene (default False)

**Type:**

bool

<a id="bpy.types.ObjectSolverConstraint.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ObjectSolverConstraint.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ObjectSolverConstraint.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ObjectSolverConstraint.bl_rna_get_subclass_py(id, default=None, /)

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
