<!-- source: Blender Python API reference 5.2 / bpy.types.Particle.html -->

<a id="particle-bpy-struct"></a>

# Particle(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.Particle"></a>

### class bpy.types.Particle(bpy_struct)

Particle in a particle system

<a id="bpy.types.Particle.alive_state"></a>

#### bpy.types.Particle.alive_state

(default `'DEAD'`)

**Type:**

Literal[‘DEAD’, ‘UNBORN’, ‘ALIVE’, ‘DYING’]

<a id="bpy.types.Particle.angular_velocity"></a>

#### bpy.types.Particle.angular_velocity

(array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.Particle.birth_time"></a>

#### bpy.types.Particle.birth_time

(in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.Particle.die_time"></a>

#### bpy.types.Particle.die_time

(in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.Particle.hair_keys"></a>

#### bpy.types.Particle.hair_keys

(default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`ParticleHairKey`](bpy.types.ParticleHairKey.md#bpy.types.ParticleHairKey "bpy.types.ParticleHairKey")]

<a id="bpy.types.Particle.is_exist"></a>

#### bpy.types.Particle.is_exist

(default True, readonly)

**Type:**

bool

<a id="bpy.types.Particle.is_visible"></a>

#### bpy.types.Particle.is_visible

(default True, readonly)

**Type:**

bool

<a id="bpy.types.Particle.lifetime"></a>

#### bpy.types.Particle.lifetime

(in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.Particle.location"></a>

#### bpy.types.Particle.location

(array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.Particle.particle_keys"></a>

#### bpy.types.Particle.particle_keys

(default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`ParticleKey`](bpy.types.ParticleKey.md#bpy.types.ParticleKey "bpy.types.ParticleKey")]

<a id="bpy.types.Particle.prev_angular_velocity"></a>

#### bpy.types.Particle.prev_angular_velocity

(array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.Particle.prev_location"></a>

#### bpy.types.Particle.prev_location

(array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.Particle.prev_rotation"></a>

#### bpy.types.Particle.prev_rotation

(array of 4 items, in [-inf, inf], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`mathutils.Quaternion`](mathutils.md#mathutils.Quaternion "mathutils.Quaternion")

<a id="bpy.types.Particle.prev_velocity"></a>

#### bpy.types.Particle.prev_velocity

(array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.Particle.rotation"></a>

#### bpy.types.Particle.rotation

(array of 4 items, in [-inf, inf], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`mathutils.Quaternion`](mathutils.md#mathutils.Quaternion "mathutils.Quaternion")

<a id="bpy.types.Particle.size"></a>

#### bpy.types.Particle.size

(in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.Particle.velocity"></a>

#### bpy.types.Particle.velocity

(array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.Particle.uv_on_emitter"></a>

#### bpy.types.Particle.uv_on_emitter(modifier)

Obtain UV coordinates for a particle on an evaluated mesh.

**Parameters:**

**modifier** ([`ParticleSystemModifier`](bpy.types.ParticleSystemModifier.md#bpy.types.ParticleSystemModifier "bpy.types.ParticleSystemModifier") | None) – Particle modifier from an evaluated object (never None)

**Returns:**

uv, (array of 2 items, in [-inf, inf])

**Return type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.Particle.bl_rna_get_subclass"></a>

#### classmethod bpy.types.Particle.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.Particle.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.Particle.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`ParticleHairKey.co_object`](bpy.types.ParticleHairKey.md#bpy.types.ParticleHairKey.co_object "bpy.types.ParticleHairKey.co_object") - [`ParticleHairKey.co_object_set`](bpy.types.ParticleHairKey.md#bpy.types.ParticleHairKey.co_object_set "bpy.types.ParticleHairKey.co_object_set") - [`ParticleSystem.mcol_on_emitter`](bpy.types.ParticleSystem.md#bpy.types.ParticleSystem.mcol_on_emitter "bpy.types.ParticleSystem.mcol_on_emitter") | - [`ParticleSystem.particles`](bpy.types.ParticleSystem.md#bpy.types.ParticleSystem.particles "bpy.types.ParticleSystem.particles") - [`ParticleSystem.uv_on_emitter`](bpy.types.ParticleSystem.md#bpy.types.ParticleSystem.uv_on_emitter "bpy.types.ParticleSystem.uv_on_emitter") |
