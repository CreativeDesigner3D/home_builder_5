<!-- source: Blender Python API reference 5.2 / bpy.types.KinematicConstraint.html -->

<a id="kinematicconstraint-constraint"></a>

# KinematicConstraint(Constraint)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Constraint`](bpy.types.Constraint.md#bpy.types.Constraint "bpy.types.Constraint")

<a id="bpy.types.KinematicConstraint"></a>

### class bpy.types.KinematicConstraint(Constraint)

Inverse Kinematics

<a id="bpy.types.KinematicConstraint.chain_count"></a>

#### bpy.types.KinematicConstraint.chain_count

How many bones are included in the IK effect - 0 uses all bones (in [0, 255], default 0)

**Type:**

int

<a id="bpy.types.KinematicConstraint.distance"></a>

#### bpy.types.KinematicConstraint.distance

Radius of limiting sphere (in [0, 100], default 0.0)

**Type:**

float

<a id="bpy.types.KinematicConstraint.ik_type"></a>

#### bpy.types.KinematicConstraint.ik_type

(default `'COPY_POSE'`)

**Type:**

Literal[‘COPY_POSE’, ‘DISTANCE’]

<a id="bpy.types.KinematicConstraint.iterations"></a>

#### bpy.types.KinematicConstraint.iterations

Maximum number of solving iterations (in [0, 10000], default 0)

**Type:**

int

<a id="bpy.types.KinematicConstraint.limit_mode"></a>

#### bpy.types.KinematicConstraint.limit_mode

Distances in relation to sphere of influence to allow (default `'LIMITDIST_INSIDE'`)

- `LIMITDIST_INSIDE`
  Inside – The object is constrained inside a virtual sphere around the target object, with a radius defined by the limit distance.
- `LIMITDIST_OUTSIDE`
  Outside – The object is constrained outside a virtual sphere around the target object, with a radius defined by the limit distance.
- `LIMITDIST_ONSURFACE`
  On Surface – The object is constrained on the surface of a virtual sphere around the target object, with a radius defined by the limit distance.

**Type:**

Literal[‘LIMITDIST_INSIDE’, ‘LIMITDIST_OUTSIDE’, ‘LIMITDIST_ONSURFACE’]

<a id="bpy.types.KinematicConstraint.lock_location_x"></a>

#### bpy.types.KinematicConstraint.lock_location_x

Constraint position along X axis (default True)

**Type:**

bool

<a id="bpy.types.KinematicConstraint.lock_location_y"></a>

#### bpy.types.KinematicConstraint.lock_location_y

Constraint position along Y axis (default True)

**Type:**

bool

<a id="bpy.types.KinematicConstraint.lock_location_z"></a>

#### bpy.types.KinematicConstraint.lock_location_z

Constraint position along Z axis (default True)

**Type:**

bool

<a id="bpy.types.KinematicConstraint.lock_rotation_x"></a>

#### bpy.types.KinematicConstraint.lock_rotation_x

Constraint rotation along X axis (default True)

**Type:**

bool

<a id="bpy.types.KinematicConstraint.lock_rotation_y"></a>

#### bpy.types.KinematicConstraint.lock_rotation_y

Constraint rotation along Y axis (default True)

**Type:**

bool

<a id="bpy.types.KinematicConstraint.lock_rotation_z"></a>

#### bpy.types.KinematicConstraint.lock_rotation_z

Constraint rotation along Z axis (default True)

**Type:**

bool

<a id="bpy.types.KinematicConstraint.orient_weight"></a>

#### bpy.types.KinematicConstraint.orient_weight

For Tree-IK: Weight of orientation control for this target (in [0.01, 1], default 0.0)

**Type:**

float

<a id="bpy.types.KinematicConstraint.pole_angle"></a>

#### bpy.types.KinematicConstraint.pole_angle

Pole rotation offset (in [-3.14159, 3.14159], default 0.0)

**Type:**

float

<a id="bpy.types.KinematicConstraint.pole_subtarget"></a>

#### bpy.types.KinematicConstraint.pole_subtarget

(default “”, never None)

**Type:**

str

<a id="bpy.types.KinematicConstraint.pole_target"></a>

#### bpy.types.KinematicConstraint.pole_target

Object for pole rotation

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.KinematicConstraint.reference_axis"></a>

#### bpy.types.KinematicConstraint.reference_axis

Constraint axis Lock options relative to Bone or Target reference (default `'BONE'`)

**Type:**

Literal[‘BONE’, ‘TARGET’]

<a id="bpy.types.KinematicConstraint.subtarget"></a>

#### bpy.types.KinematicConstraint.subtarget

Armature bone, mesh or lattice vertex group, … (default “”, never None)

**Type:**

str

<a id="bpy.types.KinematicConstraint.target"></a>

#### bpy.types.KinematicConstraint.target

Target object

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.KinematicConstraint.use_location"></a>

#### bpy.types.KinematicConstraint.use_location

Chain follows position of target (default False)

**Type:**

bool

<a id="bpy.types.KinematicConstraint.use_rotation"></a>

#### bpy.types.KinematicConstraint.use_rotation

Chain follows rotation of target (default False)

**Type:**

bool

<a id="bpy.types.KinematicConstraint.use_stretch"></a>

#### bpy.types.KinematicConstraint.use_stretch

Enable IK Stretching (default False)

**Type:**

bool

<a id="bpy.types.KinematicConstraint.use_tail"></a>

#### bpy.types.KinematicConstraint.use_tail

Include bone’s tail as last element in chain (default False)

**Type:**

bool

<a id="bpy.types.KinematicConstraint.weight"></a>

#### bpy.types.KinematicConstraint.weight

For Tree-IK: Weight of position control for this target (in [0.01, 1], default 0.0)

**Type:**

float

<a id="bpy.types.KinematicConstraint.bl_rna_get_subclass"></a>

#### classmethod bpy.types.KinematicConstraint.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.KinematicConstraint.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.KinematicConstraint.bl_rna_get_subclass_py(id, default=None, /)

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
