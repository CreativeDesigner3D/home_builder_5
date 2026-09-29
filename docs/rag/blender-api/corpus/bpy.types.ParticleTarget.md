<!-- source: Blender Python API reference 5.2 / bpy.types.ParticleTarget.html -->

<a id="particletarget-bpy-struct"></a>

# ParticleTarget(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.ParticleTarget"></a>

### class bpy.types.ParticleTarget(bpy_struct)

Target particle system

<a id="bpy.types.ParticleTarget.alliance"></a>

#### bpy.types.ParticleTarget.alliance

(default `'NEUTRAL'`)

**Type:**

Literal[‘FRIEND’, ‘NEUTRAL’, ‘ENEMY’]

<a id="bpy.types.ParticleTarget.duration"></a>

#### bpy.types.ParticleTarget.duration

(in [0, 1.04857e+06], default 0.0)

**Type:**

float

<a id="bpy.types.ParticleTarget.is_valid"></a>

#### bpy.types.ParticleTarget.is_valid

Keyed particles target is valid (default False)

**Type:**

bool

<a id="bpy.types.ParticleTarget.name"></a>

#### bpy.types.ParticleTarget.name

Particle target name (default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.ParticleTarget.object"></a>

#### bpy.types.ParticleTarget.object

The object that has the target particle system (empty if same object)

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.ParticleTarget.system"></a>

#### bpy.types.ParticleTarget.system

The index of particle system on the target object (in [1, inf], default 0)

**Type:**

int

<a id="bpy.types.ParticleTarget.time"></a>

#### bpy.types.ParticleTarget.time

(in [0, 1.04857e+06], default 0.0)

**Type:**

float

<a id="bpy.types.ParticleTarget.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ParticleTarget.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ParticleTarget.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ParticleTarget.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`ParticleSystem.active_particle_target`](bpy.types.ParticleSystem.md#bpy.types.ParticleSystem.active_particle_target "bpy.types.ParticleSystem.active_particle_target") | - [`ParticleSystem.targets`](bpy.types.ParticleSystem.md#bpy.types.ParticleSystem.targets "bpy.types.ParticleSystem.targets") |
