<!-- source: Blender Python API reference 5.2 / bpy.types.RigidBodyObject.html -->

<a id="rigidbodyobject-bpy-struct"></a>

# RigidBodyObject(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.RigidBodyObject"></a>

### class bpy.types.RigidBodyObject(bpy_struct)

Settings for object participating in Rigid Body Simulation

<a id="bpy.types.RigidBodyObject.angular_damping"></a>

#### bpy.types.RigidBodyObject.angular_damping

Amount of angular velocity that is lost over time (in [0, 1], default 0.1)

**Type:**

float

<a id="bpy.types.RigidBodyObject.collision_collections"></a>

#### bpy.types.RigidBodyObject.collision_collections

Collision collections rigid body belongs to (array of 20 items, default (False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[bool]

<a id="bpy.types.RigidBodyObject.collision_margin"></a>

#### bpy.types.RigidBodyObject.collision_margin

Threshold of distance near surface where collisions are still considered (best results when non-zero) (in [0, 1], default 0.04)

**Type:**

float

<a id="bpy.types.RigidBodyObject.collision_shape"></a>

#### bpy.types.RigidBodyObject.collision_shape

Collision Shape of object in Rigid Body Simulations (default `'BOX'`)

**Type:**

Literal[[Rigidbody Object Shape Items](bpy_types_enum_items/rigidbody_object_shape_items.md#rna-enum-rigidbody-object-shape-items)]

<a id="bpy.types.RigidBodyObject.deactivate_angular_velocity"></a>

#### bpy.types.RigidBodyObject.deactivate_angular_velocity

Angular Velocity below which simulation stops simulating object (in [0, inf], default 0.5)

**Type:**

float

<a id="bpy.types.RigidBodyObject.deactivate_linear_velocity"></a>

#### bpy.types.RigidBodyObject.deactivate_linear_velocity

Linear Velocity below which simulation stops simulating object (in [0, inf], default 0.4)

**Type:**

float

<a id="bpy.types.RigidBodyObject.enabled"></a>

#### bpy.types.RigidBodyObject.enabled

Rigid Body actively participates to the simulation (default True)

**Type:**

bool

<a id="bpy.types.RigidBodyObject.friction"></a>

#### bpy.types.RigidBodyObject.friction

Resistance of object to movement (in [0, inf], default 0.5)

**Type:**

float

<a id="bpy.types.RigidBodyObject.kinematic"></a>

#### bpy.types.RigidBodyObject.kinematic

Allow rigid body to be controlled by the animation system (default False)

**Type:**

bool

<a id="bpy.types.RigidBodyObject.linear_damping"></a>

#### bpy.types.RigidBodyObject.linear_damping

Amount of linear velocity that is lost over time (in [0, 1], default 0.04)

**Type:**

float

<a id="bpy.types.RigidBodyObject.mass"></a>

#### bpy.types.RigidBodyObject.mass

How much the object ‘weighs’ irrespective of gravity (in [0.001, inf], default 1.0)

**Type:**

float

<a id="bpy.types.RigidBodyObject.mesh_source"></a>

#### bpy.types.RigidBodyObject.mesh_source

Source of the mesh used to create collision shape (default `'BASE'`)

- `BASE`
  Base – Base mesh.
- `DEFORM`
  Deform – Deformations (shape keys, deform modifiers).
- `FINAL`
  Final – All modifiers.

**Type:**

Literal[‘BASE’, ‘DEFORM’, ‘FINAL’]

<a id="bpy.types.RigidBodyObject.restitution"></a>

#### bpy.types.RigidBodyObject.restitution

Tendency of object to bounce after colliding with another (0 = stays still, 1 = perfectly elastic) (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.RigidBodyObject.type"></a>

#### bpy.types.RigidBodyObject.type

Role of object in Rigid Body Simulations (default `'ACTIVE'`)

**Type:**

Literal[[Rigidbody Object Type Items](bpy_types_enum_items/rigidbody_object_type_items.md#rna-enum-rigidbody-object-type-items)]

<a id="bpy.types.RigidBodyObject.use_deactivation"></a>

#### bpy.types.RigidBodyObject.use_deactivation

Enable deactivation of resting rigid bodies (increases performance and stability but can cause glitches) (default True)

**Type:**

bool

<a id="bpy.types.RigidBodyObject.use_deform"></a>

#### bpy.types.RigidBodyObject.use_deform

Rigid body deforms during simulation (default False)

**Type:**

bool

<a id="bpy.types.RigidBodyObject.use_margin"></a>

#### bpy.types.RigidBodyObject.use_margin

Use custom collision margin (some shapes will have a visible gap around them) (default False)

**Type:**

bool

<a id="bpy.types.RigidBodyObject.use_start_deactivated"></a>

#### bpy.types.RigidBodyObject.use_start_deactivated

Deactivate rigid body at the start of the simulation (default False)

**Type:**

bool

<a id="bpy.types.RigidBodyObject.bl_rna_get_subclass"></a>

#### classmethod bpy.types.RigidBodyObject.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.RigidBodyObject.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.RigidBodyObject.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([type](#bpy.types.RigidBodyObject.type "bpy.types.RigidBodyObject.type") | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

[type](#bpy.types.RigidBodyObject.type "bpy.types.RigidBodyObject.type")

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
| - [`Object.rigid_body`](bpy.types.Object.md#bpy.types.Object.rigid_body "bpy.types.Object.rigid_body") |  |
