<!-- source: Blender Python API reference 5.2 / bpy.types.CollisionSettings.html -->

<a id="collisionsettings-bpy-struct"></a>

# CollisionSettings(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.CollisionSettings"></a>

### class bpy.types.CollisionSettings(bpy_struct)

Collision settings for object in physics simulation

<a id="bpy.types.CollisionSettings.absorption"></a>

#### bpy.types.CollisionSettings.absorption

How much of effector force gets lost during collision with this object (in percent) (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.CollisionSettings.cloth_friction"></a>

#### bpy.types.CollisionSettings.cloth_friction

Friction for cloth collisions (in [0, 80], default 0.0)

**Type:**

float

<a id="bpy.types.CollisionSettings.damping"></a>

#### bpy.types.CollisionSettings.damping

Amount of damping during collision (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.CollisionSettings.damping_factor"></a>

#### bpy.types.CollisionSettings.damping_factor

Amount of damping during particle collision (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.CollisionSettings.damping_random"></a>

#### bpy.types.CollisionSettings.damping_random

Random variation of damping (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.CollisionSettings.friction_factor"></a>

#### bpy.types.CollisionSettings.friction_factor

Amount of friction during particle collision (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.CollisionSettings.friction_random"></a>

#### bpy.types.CollisionSettings.friction_random

Random variation of friction (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.CollisionSettings.permeability"></a>

#### bpy.types.CollisionSettings.permeability

Chance that the particle will pass through the mesh (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.CollisionSettings.stickiness"></a>

#### bpy.types.CollisionSettings.stickiness

Amount of stickiness to surface collision (in [0, 10], default 0.0)

**Type:**

float

<a id="bpy.types.CollisionSettings.thickness_inner"></a>

#### bpy.types.CollisionSettings.thickness_inner

Inner face thickness (only used by softbodies) (in [0.001, 1], default 0.0)

**Type:**

float

<a id="bpy.types.CollisionSettings.thickness_outer"></a>

#### bpy.types.CollisionSettings.thickness_outer

Outer face thickness (in [0.001, 1], default 0.0)

**Type:**

float

<a id="bpy.types.CollisionSettings.use"></a>

#### bpy.types.CollisionSettings.use

Enable this object as a collider for physics systems (default False)

**Type:**

bool

<a id="bpy.types.CollisionSettings.use_culling"></a>

#### bpy.types.CollisionSettings.use_culling

Cloth collision acts with respect to the collider normals (improves penetration recovery) (default False)

**Type:**

bool

<a id="bpy.types.CollisionSettings.use_normal"></a>

#### bpy.types.CollisionSettings.use_normal

Cloth collision impulses act in the direction of the collider normals (more reliable in some cases) (default False)

**Type:**

bool

<a id="bpy.types.CollisionSettings.use_particle_kill"></a>

#### bpy.types.CollisionSettings.use_particle_kill

Kill collided particles (default False)

**Type:**

bool

<a id="bpy.types.CollisionSettings.bl_rna_get_subclass"></a>

#### classmethod bpy.types.CollisionSettings.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.CollisionSettings.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.CollisionSettings.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`CollisionModifier.settings`](bpy.types.CollisionModifier.md#bpy.types.CollisionModifier.settings "bpy.types.CollisionModifier.settings") | - [`Object.collision`](bpy.types.Object.md#bpy.types.Object.collision "bpy.types.Object.collision") |
