<!-- source: Blender Python API reference 5.2 / bpy.types.ParticleHairKey.html -->

<a id="particlehairkey-bpy-struct"></a>

# ParticleHairKey(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.ParticleHairKey"></a>

### class bpy.types.ParticleHairKey(bpy_struct)

Particle key for hair particle system

<a id="bpy.types.ParticleHairKey.co"></a>

#### bpy.types.ParticleHairKey.co

Location of the hair key in object space (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.ParticleHairKey.co_local"></a>

#### bpy.types.ParticleHairKey.co_local

Location of the hair key in its local coordinate system, relative to the emitting face (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.ParticleHairKey.time"></a>

#### bpy.types.ParticleHairKey.time

Relative time of key over hair length (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.ParticleHairKey.weight"></a>

#### bpy.types.ParticleHairKey.weight

Weight for cloth simulation (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.ParticleHairKey.co_object"></a>

#### bpy.types.ParticleHairKey.co_object(object, modifier, particle)

Obtain hairkey location with particle and modifier data

**Parameters:**

- **object** ([`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None) – Object (never None)
- **modifier** ([`ParticleSystemModifier`](bpy.types.ParticleSystemModifier.md#bpy.types.ParticleSystemModifier "bpy.types.ParticleSystemModifier") | None) – Particle modifier (never None)
- **particle** ([`Particle`](bpy.types.Particle.md#bpy.types.Particle "bpy.types.Particle") | None) – hair particle (never None)

**Returns:**

Co, Exported hairkey location (array of 3 items, in [-inf, inf])

**Return type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.ParticleHairKey.co_object_set"></a>

#### bpy.types.ParticleHairKey.co_object_set(object, modifier, particle, co)

Set hairkey location with particle and modifier data

**Parameters:**

- **object** ([`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None) – Object (never None)
- **modifier** ([`ParticleSystemModifier`](bpy.types.ParticleSystemModifier.md#bpy.types.ParticleSystemModifier "bpy.types.ParticleSystemModifier") | None) – Particle modifier (never None)
- **particle** ([`Particle`](bpy.types.Particle.md#bpy.types.Particle "bpy.types.Particle") | None) – hair particle (never None)
- **co** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Co, Specified hairkey location (array of 3 items, in [-inf, inf])

<a id="bpy.types.ParticleHairKey.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ParticleHairKey.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ParticleHairKey.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ParticleHairKey.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Particle.hair_keys`](bpy.types.Particle.md#bpy.types.Particle.hair_keys "bpy.types.Particle.hair_keys") |  |
