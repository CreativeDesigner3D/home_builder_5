<!-- source: Blender Python API reference 5.2 / bpy.types.RigidBodyConstraint.html -->

<a id="rigidbodyconstraint-bpy-struct"></a>

# RigidBodyConstraint(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.RigidBodyConstraint"></a>

### class bpy.types.RigidBodyConstraint(bpy_struct)

Constraint influencing Objects inside Rigid Body Simulation

<a id="bpy.types.RigidBodyConstraint.breaking_threshold"></a>

#### bpy.types.RigidBodyConstraint.breaking_threshold

Impulse threshold that must be reached for the constraint to break (in [0, inf], default 10.0)

**Type:**

float

<a id="bpy.types.RigidBodyConstraint.disable_collisions"></a>

#### bpy.types.RigidBodyConstraint.disable_collisions

Disable collisions between constrained rigid bodies (default False)

**Type:**

bool

<a id="bpy.types.RigidBodyConstraint.enabled"></a>

#### bpy.types.RigidBodyConstraint.enabled

Enable this constraint (default False)

**Type:**

bool

<a id="bpy.types.RigidBodyConstraint.limit_ang_x_lower"></a>

#### bpy.types.RigidBodyConstraint.limit_ang_x_lower

Lower limit of X axis rotation (in [-6.28319, 6.28319], default -0.785398)

**Type:**

float

<a id="bpy.types.RigidBodyConstraint.limit_ang_x_upper"></a>

#### bpy.types.RigidBodyConstraint.limit_ang_x_upper

Upper limit of X axis rotation (in [-6.28319, 6.28319], default 0.785398)

**Type:**

float

<a id="bpy.types.RigidBodyConstraint.limit_ang_y_lower"></a>

#### bpy.types.RigidBodyConstraint.limit_ang_y_lower

Lower limit of Y axis rotation (in [-6.28319, 6.28319], default -0.785398)

**Type:**

float

<a id="bpy.types.RigidBodyConstraint.limit_ang_y_upper"></a>

#### bpy.types.RigidBodyConstraint.limit_ang_y_upper

Upper limit of Y axis rotation (in [-6.28319, 6.28319], default 0.785398)

**Type:**

float

<a id="bpy.types.RigidBodyConstraint.limit_ang_z_lower"></a>

#### bpy.types.RigidBodyConstraint.limit_ang_z_lower

Lower limit of Z axis rotation (in [-6.28319, 6.28319], default -0.785398)

**Type:**

float

<a id="bpy.types.RigidBodyConstraint.limit_ang_z_upper"></a>

#### bpy.types.RigidBodyConstraint.limit_ang_z_upper

Upper limit of Z axis rotation (in [-6.28319, 6.28319], default 0.785398)

**Type:**

float

<a id="bpy.types.RigidBodyConstraint.limit_lin_x_lower"></a>

#### bpy.types.RigidBodyConstraint.limit_lin_x_lower

Lower limit of X axis translation (in [-inf, inf], default -1.0)

**Type:**

float

<a id="bpy.types.RigidBodyConstraint.limit_lin_x_upper"></a>

#### bpy.types.RigidBodyConstraint.limit_lin_x_upper

Upper limit of X axis translation (in [-inf, inf], default 1.0)

**Type:**

float

<a id="bpy.types.RigidBodyConstraint.limit_lin_y_lower"></a>

#### bpy.types.RigidBodyConstraint.limit_lin_y_lower

Lower limit of Y axis translation (in [-inf, inf], default -1.0)

**Type:**

float

<a id="bpy.types.RigidBodyConstraint.limit_lin_y_upper"></a>

#### bpy.types.RigidBodyConstraint.limit_lin_y_upper

Upper limit of Y axis translation (in [-inf, inf], default 1.0)

**Type:**

float

<a id="bpy.types.RigidBodyConstraint.limit_lin_z_lower"></a>

#### bpy.types.RigidBodyConstraint.limit_lin_z_lower

Lower limit of Z axis translation (in [-inf, inf], default -1.0)

**Type:**

float

<a id="bpy.types.RigidBodyConstraint.limit_lin_z_upper"></a>

#### bpy.types.RigidBodyConstraint.limit_lin_z_upper

Upper limit of Z axis translation (in [-inf, inf], default 1.0)

**Type:**

float

<a id="bpy.types.RigidBodyConstraint.motor_ang_max_impulse"></a>

#### bpy.types.RigidBodyConstraint.motor_ang_max_impulse

Maximum angular motor impulse (in [0, inf], default 1.0)

**Type:**

float

<a id="bpy.types.RigidBodyConstraint.motor_ang_target_velocity"></a>

#### bpy.types.RigidBodyConstraint.motor_ang_target_velocity

Target angular motor velocity (in [-inf, inf], default 1.0)

**Type:**

float

<a id="bpy.types.RigidBodyConstraint.motor_lin_max_impulse"></a>

#### bpy.types.RigidBodyConstraint.motor_lin_max_impulse

Maximum linear motor impulse (in [0, inf], default 1.0)

**Type:**

float

<a id="bpy.types.RigidBodyConstraint.motor_lin_target_velocity"></a>

#### bpy.types.RigidBodyConstraint.motor_lin_target_velocity

Target linear motor velocity (in [-inf, inf], default 1.0)

**Type:**

float

<a id="bpy.types.RigidBodyConstraint.object1"></a>

#### bpy.types.RigidBodyConstraint.object1

First Rigid Body Object to be constrained

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.RigidBodyConstraint.object2"></a>

#### bpy.types.RigidBodyConstraint.object2

Second Rigid Body Object to be constrained

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.RigidBodyConstraint.solver_iterations"></a>

#### bpy.types.RigidBodyConstraint.solver_iterations

Number of constraint solver iterations made per simulation step (higher values are more accurate but slower) (in [1, 1000], default 10)

**Type:**

int

<a id="bpy.types.RigidBodyConstraint.spring_damping_ang_x"></a>

#### bpy.types.RigidBodyConstraint.spring_damping_ang_x

Damping on the X rotational axis (in [0, inf], default 0.5)

**Type:**

float

<a id="bpy.types.RigidBodyConstraint.spring_damping_ang_y"></a>

#### bpy.types.RigidBodyConstraint.spring_damping_ang_y

Damping on the Y rotational axis (in [0, inf], default 0.5)

**Type:**

float

<a id="bpy.types.RigidBodyConstraint.spring_damping_ang_z"></a>

#### bpy.types.RigidBodyConstraint.spring_damping_ang_z

Damping on the Z rotational axis (in [0, inf], default 0.5)

**Type:**

float

<a id="bpy.types.RigidBodyConstraint.spring_damping_x"></a>

#### bpy.types.RigidBodyConstraint.spring_damping_x

Damping on the X axis (in [0, inf], default 0.5)

**Type:**

float

<a id="bpy.types.RigidBodyConstraint.spring_damping_y"></a>

#### bpy.types.RigidBodyConstraint.spring_damping_y

Damping on the Y axis (in [0, inf], default 0.5)

**Type:**

float

<a id="bpy.types.RigidBodyConstraint.spring_damping_z"></a>

#### bpy.types.RigidBodyConstraint.spring_damping_z

Damping on the Z axis (in [0, inf], default 0.5)

**Type:**

float

<a id="bpy.types.RigidBodyConstraint.spring_stiffness_ang_x"></a>

#### bpy.types.RigidBodyConstraint.spring_stiffness_ang_x

Stiffness on the X rotational axis (in [0, inf], default 10.0)

**Type:**

float

<a id="bpy.types.RigidBodyConstraint.spring_stiffness_ang_y"></a>

#### bpy.types.RigidBodyConstraint.spring_stiffness_ang_y

Stiffness on the Y rotational axis (in [0, inf], default 10.0)

**Type:**

float

<a id="bpy.types.RigidBodyConstraint.spring_stiffness_ang_z"></a>

#### bpy.types.RigidBodyConstraint.spring_stiffness_ang_z

Stiffness on the Z rotational axis (in [0, inf], default 10.0)

**Type:**

float

<a id="bpy.types.RigidBodyConstraint.spring_stiffness_x"></a>

#### bpy.types.RigidBodyConstraint.spring_stiffness_x

Stiffness on the X axis (in [0, inf], default 10.0)

**Type:**

float

<a id="bpy.types.RigidBodyConstraint.spring_stiffness_y"></a>

#### bpy.types.RigidBodyConstraint.spring_stiffness_y

Stiffness on the Y axis (in [0, inf], default 10.0)

**Type:**

float

<a id="bpy.types.RigidBodyConstraint.spring_stiffness_z"></a>

#### bpy.types.RigidBodyConstraint.spring_stiffness_z

Stiffness on the Z axis (in [0, inf], default 10.0)

**Type:**

float

<a id="bpy.types.RigidBodyConstraint.spring_type"></a>

#### bpy.types.RigidBodyConstraint.spring_type

Which implementation of spring to use (default `'SPRING1'`)

- `SPRING1`
  Blender 2.7 – Spring implementation used in Blender 2.7. Damping is capped at 1.0.
- `SPRING2`
  Blender 2.8 – New implementation available since 2.8.

**Type:**

Literal[‘SPRING1’, ‘SPRING2’]

<a id="bpy.types.RigidBodyConstraint.type"></a>

#### bpy.types.RigidBodyConstraint.type

Type of Rigid Body Constraint (default `'POINT'`)

**Type:**

Literal[[Rigidbody Constraint Type Items](bpy_types_enum_items/rigidbody_constraint_type_items.md#rna-enum-rigidbody-constraint-type-items)]

<a id="bpy.types.RigidBodyConstraint.use_breaking"></a>

#### bpy.types.RigidBodyConstraint.use_breaking

Constraint can be broken if it receives an impulse above the threshold (default False)

**Type:**

bool

<a id="bpy.types.RigidBodyConstraint.use_limit_ang_x"></a>

#### bpy.types.RigidBodyConstraint.use_limit_ang_x

Limit rotation around X axis (default False)

**Type:**

bool

<a id="bpy.types.RigidBodyConstraint.use_limit_ang_y"></a>

#### bpy.types.RigidBodyConstraint.use_limit_ang_y

Limit rotation around Y axis (default False)

**Type:**

bool

<a id="bpy.types.RigidBodyConstraint.use_limit_ang_z"></a>

#### bpy.types.RigidBodyConstraint.use_limit_ang_z

Limit rotation around Z axis (default False)

**Type:**

bool

<a id="bpy.types.RigidBodyConstraint.use_limit_lin_x"></a>

#### bpy.types.RigidBodyConstraint.use_limit_lin_x

Limit translation on X axis (default False)

**Type:**

bool

<a id="bpy.types.RigidBodyConstraint.use_limit_lin_y"></a>

#### bpy.types.RigidBodyConstraint.use_limit_lin_y

Limit translation on Y axis (default False)

**Type:**

bool

<a id="bpy.types.RigidBodyConstraint.use_limit_lin_z"></a>

#### bpy.types.RigidBodyConstraint.use_limit_lin_z

Limit translation on Z axis (default False)

**Type:**

bool

<a id="bpy.types.RigidBodyConstraint.use_motor_ang"></a>

#### bpy.types.RigidBodyConstraint.use_motor_ang

Enable angular motor (default False)

**Type:**

bool

<a id="bpy.types.RigidBodyConstraint.use_motor_lin"></a>

#### bpy.types.RigidBodyConstraint.use_motor_lin

Enable linear motor (default False)

**Type:**

bool

<a id="bpy.types.RigidBodyConstraint.use_override_solver_iterations"></a>

#### bpy.types.RigidBodyConstraint.use_override_solver_iterations

Override the number of solver iterations for this constraint (default False)

**Type:**

bool

<a id="bpy.types.RigidBodyConstraint.use_spring_ang_x"></a>

#### bpy.types.RigidBodyConstraint.use_spring_ang_x

Enable spring on X rotational axis (default False)

**Type:**

bool

<a id="bpy.types.RigidBodyConstraint.use_spring_ang_y"></a>

#### bpy.types.RigidBodyConstraint.use_spring_ang_y

Enable spring on Y rotational axis (default False)

**Type:**

bool

<a id="bpy.types.RigidBodyConstraint.use_spring_ang_z"></a>

#### bpy.types.RigidBodyConstraint.use_spring_ang_z

Enable spring on Z rotational axis (default False)

**Type:**

bool

<a id="bpy.types.RigidBodyConstraint.use_spring_x"></a>

#### bpy.types.RigidBodyConstraint.use_spring_x

Enable spring on X axis (default False)

**Type:**

bool

<a id="bpy.types.RigidBodyConstraint.use_spring_y"></a>

#### bpy.types.RigidBodyConstraint.use_spring_y

Enable spring on Y axis (default False)

**Type:**

bool

<a id="bpy.types.RigidBodyConstraint.use_spring_z"></a>

#### bpy.types.RigidBodyConstraint.use_spring_z

Enable spring on Z axis (default False)

**Type:**

bool

<a id="bpy.types.RigidBodyConstraint.bl_rna_get_subclass"></a>

#### classmethod bpy.types.RigidBodyConstraint.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.RigidBodyConstraint.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.RigidBodyConstraint.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([type](#bpy.types.RigidBodyConstraint.type "bpy.types.RigidBodyConstraint.type") | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

[type](#bpy.types.RigidBodyConstraint.type "bpy.types.RigidBodyConstraint.type")

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
| - [`Object.rigid_body_constraint`](bpy.types.Object.md#bpy.types.Object.rigid_body_constraint "bpy.types.Object.rigid_body_constraint") |  |
