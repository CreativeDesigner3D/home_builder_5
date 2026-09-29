<!-- source: Blender Python API reference 5.2 / bpy.types.RigidBodyWorld.html -->

<a id="rigidbodyworld-bpy-struct"></a>

# RigidBodyWorld(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.RigidBodyWorld"></a>

### class bpy.types.RigidBodyWorld(bpy_struct)

Self-contained rigid body simulation environment and settings

<a id="bpy.types.RigidBodyWorld.collection"></a>

#### bpy.types.RigidBodyWorld.collection

Collection containing objects participating in this simulation

**Type:**

[`Collection`](bpy.types.Collection.md#bpy.types.Collection "bpy.types.Collection") | None

<a id="bpy.types.RigidBodyWorld.constraints"></a>

#### bpy.types.RigidBodyWorld.constraints

Collection containing rigid body constraint objects

**Type:**

[`Collection`](bpy.types.Collection.md#bpy.types.Collection "bpy.types.Collection") | None

<a id="bpy.types.RigidBodyWorld.effector_weights"></a>

#### bpy.types.RigidBodyWorld.effector_weights

(readonly)

**Type:**

[`EffectorWeights`](bpy.types.EffectorWeights.md#bpy.types.EffectorWeights "bpy.types.EffectorWeights") | None

<a id="bpy.types.RigidBodyWorld.enabled"></a>

#### bpy.types.RigidBodyWorld.enabled

Simulation will be evaluated (default True)

**Type:**

bool

<a id="bpy.types.RigidBodyWorld.point_cache"></a>

#### bpy.types.RigidBodyWorld.point_cache

(readonly, never None)

**Type:**

[`PointCache`](bpy.types.PointCache.md#bpy.types.PointCache "bpy.types.PointCache")

<a id="bpy.types.RigidBodyWorld.solver_iterations"></a>

#### bpy.types.RigidBodyWorld.solver_iterations

Number of constraint solver iterations made per simulation step (higher values are more accurate but slower) (in [1, 1000], default 10)

**Type:**

int

<a id="bpy.types.RigidBodyWorld.substeps_per_frame"></a>

#### bpy.types.RigidBodyWorld.substeps_per_frame

Number of simulation steps taken per frame (higher values are more accurate but slower) (in [1, 32767], default 10)

**Type:**

int

<a id="bpy.types.RigidBodyWorld.time_scale"></a>

#### bpy.types.RigidBodyWorld.time_scale

Change the speed of the simulation (in [0, 100], default 1.0)

**Type:**

float

<a id="bpy.types.RigidBodyWorld.use_split_impulse"></a>

#### bpy.types.RigidBodyWorld.use_split_impulse

Reduce extra velocity that can build up when objects collide (lowers simulation stability a little so use only when necessary) (default False)

**Type:**

bool

<a id="bpy.types.RigidBodyWorld.convex_sweep_test"></a>

#### bpy.types.RigidBodyWorld.convex_sweep_test(object, start, end)

Sweep test convex rigidbody against the current rigidbody world

**Parameters:**

- **object** ([`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None) – Rigidbody object with a convex collision shape (never None)
- **start** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – (array of 3 items, in [-inf, inf])
- **end** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – (array of 3 items, in [-inf, inf])

**Returns:**

`object_location`, The hit location of this sweep test, [`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

`hitpoint`, The hit location of this sweep test, [`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

`normal`, The face normal at the sweep test hit location, [`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

`has_hit`, If the function has found collision point, value is 1, otherwise 0, int

**Return type:**

tuple[[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector"), [`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector"), [`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector"), int]

<a id="bpy.types.RigidBodyWorld.bl_rna_get_subclass"></a>

#### classmethod bpy.types.RigidBodyWorld.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.RigidBodyWorld.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.RigidBodyWorld.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Scene.rigidbody_world`](bpy.types.Scene.md#bpy.types.Scene.rigidbody_world "bpy.types.Scene.rigidbody_world") |  |
