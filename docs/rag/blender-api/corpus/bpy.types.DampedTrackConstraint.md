<!-- source: Blender Python API reference 5.2 / bpy.types.DampedTrackConstraint.html -->

<a id="dampedtrackconstraint-constraint"></a>

# DampedTrackConstraint(Constraint)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Constraint`](bpy.types.Constraint.md#bpy.types.Constraint "bpy.types.Constraint")

<a id="bpy.types.DampedTrackConstraint"></a>

### class bpy.types.DampedTrackConstraint(Constraint)

Point toward target by taking the shortest rotation path

<a id="bpy.types.DampedTrackConstraint.head_tail"></a>

#### bpy.types.DampedTrackConstraint.head_tail

Target along length of bone: Head is 0, Tail is 1 (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.DampedTrackConstraint.subtarget"></a>

#### bpy.types.DampedTrackConstraint.subtarget

Armature bone, mesh or lattice vertex group, … (default “”, never None)

**Type:**

str

<a id="bpy.types.DampedTrackConstraint.target"></a>

#### bpy.types.DampedTrackConstraint.target

Target object

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.DampedTrackConstraint.track_axis"></a>

#### bpy.types.DampedTrackConstraint.track_axis

Axis that points to the target object (default `'TRACK_X'`)

**Type:**

Literal[‘TRACK_X’, ‘TRACK_Y’, ‘TRACK_Z’, ‘TRACK_NEGATIVE_X’, ‘TRACK_NEGATIVE_Y’, ‘TRACK_NEGATIVE_Z’]

<a id="bpy.types.DampedTrackConstraint.use_bbone_shape"></a>

#### bpy.types.DampedTrackConstraint.use_bbone_shape

Follow shape of B-Bone segments when calculating Head/Tail position (default False)

**Type:**

bool

<a id="bpy.types.DampedTrackConstraint.bl_rna_get_subclass"></a>

#### classmethod bpy.types.DampedTrackConstraint.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.DampedTrackConstraint.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.DampedTrackConstraint.bl_rna_get_subclass_py(id, default=None, /)

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
