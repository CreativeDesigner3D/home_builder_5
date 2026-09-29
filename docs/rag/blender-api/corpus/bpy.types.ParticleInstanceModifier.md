<!-- source: Blender Python API reference 5.2 / bpy.types.ParticleInstanceModifier.html -->

<a id="particleinstancemodifier-modifier"></a>

# ParticleInstanceModifier(Modifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Modifier`](bpy.types.Modifier.md#bpy.types.Modifier "bpy.types.Modifier")

<a id="bpy.types.ParticleInstanceModifier"></a>

### class bpy.types.ParticleInstanceModifier(Modifier)

Particle system instancing modifier

<a id="bpy.types.ParticleInstanceModifier.axis"></a>

#### bpy.types.ParticleInstanceModifier.axis

Pole axis for rotation (default `'Z'`)

**Type:**

Literal[[Axis Xyz Items](bpy_types_enum_items/axis_xyz_items.md#rna-enum-axis-xyz-items)]

<a id="bpy.types.ParticleInstanceModifier.index_layer_name"></a>

#### bpy.types.ParticleInstanceModifier.index_layer_name

Custom data layer name for the index (default “”, never None)

**Type:**

str

<a id="bpy.types.ParticleInstanceModifier.object"></a>

#### bpy.types.ParticleInstanceModifier.object

Object that has the particle system

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.ParticleInstanceModifier.particle_amount"></a>

#### bpy.types.ParticleInstanceModifier.particle_amount

Amount of particles to use for instancing (in [0, 1], default 1.0)

**Type:**

float

<a id="bpy.types.ParticleInstanceModifier.particle_offset"></a>

#### bpy.types.ParticleInstanceModifier.particle_offset

Relative offset of particles to use for instancing, to avoid overlap of multiple instances (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.ParticleInstanceModifier.particle_system"></a>

#### bpy.types.ParticleInstanceModifier.particle_system

**Type:**

[`ParticleSystem`](bpy.types.ParticleSystem.md#bpy.types.ParticleSystem "bpy.types.ParticleSystem") | None

<a id="bpy.types.ParticleInstanceModifier.particle_system_index"></a>

#### bpy.types.ParticleInstanceModifier.particle_system_index

(in [1, 32767], default 1)

**Type:**

int

<a id="bpy.types.ParticleInstanceModifier.position"></a>

#### bpy.types.ParticleInstanceModifier.position

Position along path (in [0, 1], default 1.0)

**Type:**

float

<a id="bpy.types.ParticleInstanceModifier.random_position"></a>

#### bpy.types.ParticleInstanceModifier.random_position

Randomize position along path (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.ParticleInstanceModifier.random_rotation"></a>

#### bpy.types.ParticleInstanceModifier.random_rotation

Randomize rotation around path (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.ParticleInstanceModifier.rotation"></a>

#### bpy.types.ParticleInstanceModifier.rotation

Rotation around path (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.ParticleInstanceModifier.show_alive"></a>

#### bpy.types.ParticleInstanceModifier.show_alive

Show instances when particles are alive (default True)

**Type:**

bool

<a id="bpy.types.ParticleInstanceModifier.show_dead"></a>

#### bpy.types.ParticleInstanceModifier.show_dead

Show instances when particles are dead (default True)

**Type:**

bool

<a id="bpy.types.ParticleInstanceModifier.show_unborn"></a>

#### bpy.types.ParticleInstanceModifier.show_unborn

Show instances when particles are unborn (default True)

**Type:**

bool

<a id="bpy.types.ParticleInstanceModifier.space"></a>

#### bpy.types.ParticleInstanceModifier.space

Space to use for copying mesh data (default `'WORLD'`)

- `LOCAL`
  Local – Use offset from the particle object in the instance object.
- `WORLD`
  World – Use world space offset in the instance object.

**Type:**

Literal[‘LOCAL’, ‘WORLD’]

<a id="bpy.types.ParticleInstanceModifier.use_children"></a>

#### bpy.types.ParticleInstanceModifier.use_children

Create instances from child particles (default False)

**Type:**

bool

<a id="bpy.types.ParticleInstanceModifier.use_normal"></a>

#### bpy.types.ParticleInstanceModifier.use_normal

Create instances from normal particles (default True)

**Type:**

bool

<a id="bpy.types.ParticleInstanceModifier.use_path"></a>

#### bpy.types.ParticleInstanceModifier.use_path

Create instances along particle paths (default False)

**Type:**

bool

<a id="bpy.types.ParticleInstanceModifier.use_preserve_shape"></a>

#### bpy.types.ParticleInstanceModifier.use_preserve_shape

Don’t stretch the object (default False)

**Type:**

bool

<a id="bpy.types.ParticleInstanceModifier.use_size"></a>

#### bpy.types.ParticleInstanceModifier.use_size

Use particle size to scale the instances (default False)

**Type:**

bool

<a id="bpy.types.ParticleInstanceModifier.value_layer_name"></a>

#### bpy.types.ParticleInstanceModifier.value_layer_name

Custom data layer name for the randomized value (default “”, never None)

**Type:**

str

<a id="bpy.types.ParticleInstanceModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ParticleInstanceModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ParticleInstanceModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ParticleInstanceModifier.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, Modifier.name, Modifier.type, Modifier.show_viewport, Modifier.show_render, Modifier.show_in_editmode, Modifier.show_on_cage, Modifier.show_expanded, Modifier.is_active, Modifier.use_pin_to_last, Modifier.is_override_data, Modifier.use_apply_on_spline, Modifier.execution_time, Modifier.persistent_uid

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, Modifier.bl_rna_get_subclass, Modifier.bl_rna_get_subclass_py
