<!-- source: Blender Python API reference 5.2 / bpy.types.ParticleKey.html -->

<a id="particlekey-bpy-struct"></a>

# ParticleKey(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.ParticleKey"></a>

### class bpy.types.ParticleKey(bpy_struct)

Key location for a particle over time

<a id="bpy.types.ParticleKey.angular_velocity"></a>

#### bpy.types.ParticleKey.angular_velocity

Key angular velocity (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.ParticleKey.location"></a>

#### bpy.types.ParticleKey.location

Key location (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.ParticleKey.rotation"></a>

#### bpy.types.ParticleKey.rotation

Key rotation quaternion (array of 4 items, in [-inf, inf], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`mathutils.Quaternion`](mathutils.md#mathutils.Quaternion "mathutils.Quaternion")

<a id="bpy.types.ParticleKey.time"></a>

#### bpy.types.ParticleKey.time

Time of key over the simulation (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.ParticleKey.velocity"></a>

#### bpy.types.ParticleKey.velocity

Key velocity (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.ParticleKey.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ParticleKey.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ParticleKey.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ParticleKey.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Particle.particle_keys`](bpy.types.Particle.md#bpy.types.Particle.particle_keys "bpy.types.Particle.particle_keys") |  |
