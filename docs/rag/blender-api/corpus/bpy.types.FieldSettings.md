<!-- source: Blender Python API reference 5.2 / bpy.types.FieldSettings.html -->

<a id="fieldsettings-bpy-struct"></a>

# FieldSettings(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.FieldSettings"></a>

### class bpy.types.FieldSettings(bpy_struct)

Field settings for an object in physics simulation

<a id="bpy.types.FieldSettings.apply_to_location"></a>

#### bpy.types.FieldSettings.apply_to_location

Affect particle’s location (default False)

**Type:**

bool

<a id="bpy.types.FieldSettings.apply_to_rotation"></a>

#### bpy.types.FieldSettings.apply_to_rotation

Affect particle’s dynamic rotation (default False)

**Type:**

bool

<a id="bpy.types.FieldSettings.distance_max"></a>

#### bpy.types.FieldSettings.distance_max

Maximum distance for the field to work (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.FieldSettings.distance_min"></a>

#### bpy.types.FieldSettings.distance_min

Minimum distance for the field’s falloff (in [0, 1000], default 0.0)

**Type:**

float

<a id="bpy.types.FieldSettings.falloff_power"></a>

#### bpy.types.FieldSettings.falloff_power

How quickly strength falls off with distance from the force field (in [0, 10], default 0.0)

**Type:**

float

<a id="bpy.types.FieldSettings.falloff_type"></a>

#### bpy.types.FieldSettings.falloff_type

(default `'SPHERE'`)

**Type:**

Literal[‘CONE’, ‘SPHERE’, ‘TUBE’]

<a id="bpy.types.FieldSettings.flow"></a>

#### bpy.types.FieldSettings.flow

Convert effector force into air flow velocity (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.FieldSettings.guide_clump_amount"></a>

#### bpy.types.FieldSettings.guide_clump_amount

Amount of clumping (in [-1, 1], default 0.0)

**Type:**

float

<a id="bpy.types.FieldSettings.guide_clump_shape"></a>

#### bpy.types.FieldSettings.guide_clump_shape

Shape of clumping (in [-0.999, 0.999], default 0.0)

**Type:**

float

<a id="bpy.types.FieldSettings.guide_free"></a>

#### bpy.types.FieldSettings.guide_free

Guide-free time from particle life’s end (in [0, 0.99], default 0.0)

**Type:**

float

<a id="bpy.types.FieldSettings.guide_kink_amplitude"></a>

#### bpy.types.FieldSettings.guide_kink_amplitude

The amplitude of the offset (in [0, 10], default 0.0)

**Type:**

float

<a id="bpy.types.FieldSettings.guide_kink_axis"></a>

#### bpy.types.FieldSettings.guide_kink_axis

Which axis to use for offset (default `'X'`)

**Type:**

Literal[[Axis Xyz Items](bpy_types_enum_items/axis_xyz_items.md#rna-enum-axis-xyz-items)]

<a id="bpy.types.FieldSettings.guide_kink_frequency"></a>

#### bpy.types.FieldSettings.guide_kink_frequency

The frequency of the offset (1/total length) (in [0, 10], default 0.0)

**Type:**

float

<a id="bpy.types.FieldSettings.guide_kink_shape"></a>

#### bpy.types.FieldSettings.guide_kink_shape

Adjust the offset to the beginning/end (in [-0.999, 0.999], default 0.0)

**Type:**

float

<a id="bpy.types.FieldSettings.guide_kink_type"></a>

#### bpy.types.FieldSettings.guide_kink_type

Type of periodic offset on the curve (default `'NONE'`)

**Type:**

Literal[‘NONE’, ‘BRAID’, ‘CURL’, ‘RADIAL’, ‘ROLL’, ‘ROTATION’, ‘WAVE’]

<a id="bpy.types.FieldSettings.guide_minimum"></a>

#### bpy.types.FieldSettings.guide_minimum

The distance from which particles are affected fully (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.FieldSettings.harmonic_damping"></a>

#### bpy.types.FieldSettings.harmonic_damping

Damping of the harmonic force (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.FieldSettings.inflow"></a>

#### bpy.types.FieldSettings.inflow

Inwards component of the vortex force (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.FieldSettings.linear_drag"></a>

#### bpy.types.FieldSettings.linear_drag

Drag component proportional to velocity (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.FieldSettings.noise"></a>

#### bpy.types.FieldSettings.noise

Amount of noise for the force strength (in [0, 10], default 0.0)

**Type:**

float

<a id="bpy.types.FieldSettings.quadratic_drag"></a>

#### bpy.types.FieldSettings.quadratic_drag

Drag component proportional to the square of velocity (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.FieldSettings.radial_falloff"></a>

#### bpy.types.FieldSettings.radial_falloff

Radial falloff power (real gravitational falloff = 2) (in [0, 10], default 0.0)

**Type:**

float

<a id="bpy.types.FieldSettings.radial_max"></a>

#### bpy.types.FieldSettings.radial_max

Maximum radial distance for the field to work (in [0, 1000], default 0.0)

**Type:**

float

<a id="bpy.types.FieldSettings.radial_min"></a>

#### bpy.types.FieldSettings.radial_min

Minimum radial distance for the field’s falloff (in [0, 1000], default 0.0)

**Type:**

float

<a id="bpy.types.FieldSettings.rest_length"></a>

#### bpy.types.FieldSettings.rest_length

Rest length of the harmonic force (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.FieldSettings.seed"></a>

#### bpy.types.FieldSettings.seed

Seed of the noise (in [1, 128], default 0)

**Type:**

int

<a id="bpy.types.FieldSettings.shape"></a>

#### bpy.types.FieldSettings.shape

Which direction is used to calculate the effector force (default `'POINT'`)

- `POINT`
  Point – Field originates from the object center.
- `LINE`
  Line – Field originates from the local Z axis of the object.
- `PLANE`
  Plane – Field originates from the local XY plane of the object.
- `SURFACE`
  Surface – Field originates from the surface of the object.
- `POINTS`
  Every Point – Field originates from all of the vertices of the object.

**Type:**

Literal[‘POINT’, ‘LINE’, ‘PLANE’, ‘SURFACE’, ‘POINTS’]

<a id="bpy.types.FieldSettings.size"></a>

#### bpy.types.FieldSettings.size

Size of the turbulence (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.FieldSettings.source_object"></a>

#### bpy.types.FieldSettings.source_object

Select domain object of the smoke simulation

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.FieldSettings.strength"></a>

#### bpy.types.FieldSettings.strength

Strength of force field (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.FieldSettings.texture"></a>

#### bpy.types.FieldSettings.texture

Texture to use as force

**Type:**

[`Texture`](bpy.types.Texture.md#bpy.types.Texture "bpy.types.Texture") | None

<a id="bpy.types.FieldSettings.texture_mode"></a>

#### bpy.types.FieldSettings.texture_mode

How the texture effect is calculated (RGB and Curl need a RGB texture, else Gradient will be used instead) (default `'RGB'`)

**Type:**

Literal[‘CURL’, ‘GRADIENT’, ‘RGB’]

<a id="bpy.types.FieldSettings.texture_nabla"></a>

#### bpy.types.FieldSettings.texture_nabla

Defines size of derivative offset used for calculating gradient and curl (in [0.0001, 1], default 0.0)

**Type:**

float

<a id="bpy.types.FieldSettings.type"></a>

#### bpy.types.FieldSettings.type

Type of field (default `'NONE'`)

- `NONE`
  None.
- `BOID`
  Boid – Create a force that acts as a boid’s predators or target.
- `CHARGE`
  Charge – Spherical forcefield based on the charge of particles, only influences other charge force fields.
- `GUIDE`
  Curve Guide – Create a force along a curve object.
- `DRAG`
  Drag – Create a force that dampens motion.
- `FLUID_FLOW`
  Fluid Flow – Create a force based on fluid simulation velocities.
- `FORCE`
  Force – Radial field toward the center of object.
- `HARMONIC`
  Harmonic – The source of this force field is the zero point of a harmonic oscillator.
- `LENNARDJ`
  Lennard-Jones – Forcefield based on the Lennard-Jones potential.
- `MAGNET`
  Magnetic – Forcefield depends on the speed of the particles.
- `TEXTURE`
  Texture – Force field based on a texture.
- `TURBULENCE`
  Turbulence – Create turbulence with a noise field.
- `VORTEX`
  Vortex – Spiraling force that twists the force object’s local Z axis.
- `WIND`
  Wind – Constant force along the force object’s local Z axis.

**Type:**

Literal[‘NONE’, ‘BOID’, ‘CHARGE’, ‘GUIDE’, ‘DRAG’, ‘FLUID_FLOW’, ‘FORCE’, ‘HARMONIC’, ‘LENNARDJ’, ‘MAGNET’, ‘TEXTURE’, ‘TURBULENCE’, ‘VORTEX’, ‘WIND’]

<a id="bpy.types.FieldSettings.use_2d_force"></a>

#### bpy.types.FieldSettings.use_2d_force

Apply force only in 2D (default False)

**Type:**

bool

<a id="bpy.types.FieldSettings.use_absorption"></a>

#### bpy.types.FieldSettings.use_absorption

Force gets absorbed by collision objects (default False)

**Type:**

bool

<a id="bpy.types.FieldSettings.use_global_coords"></a>

#### bpy.types.FieldSettings.use_global_coords

Use effector/global coordinates for turbulence (default False)

**Type:**

bool

<a id="bpy.types.FieldSettings.use_gravity_falloff"></a>

#### bpy.types.FieldSettings.use_gravity_falloff

Multiply force by 1/distance² (default False)

**Type:**

bool

<a id="bpy.types.FieldSettings.use_guide_path_add"></a>

#### bpy.types.FieldSettings.use_guide_path_add

Based on distance/falloff it adds a portion of the entire path (default False)

**Type:**

bool

<a id="bpy.types.FieldSettings.use_guide_path_weight"></a>

#### bpy.types.FieldSettings.use_guide_path_weight

Use curve weights to influence the particle influence along the curve (default False)

**Type:**

bool

<a id="bpy.types.FieldSettings.use_max_distance"></a>

#### bpy.types.FieldSettings.use_max_distance

Use a maximum distance for the field to work (default False)

**Type:**

bool

<a id="bpy.types.FieldSettings.use_min_distance"></a>

#### bpy.types.FieldSettings.use_min_distance

Use a minimum distance for the field’s falloff (default False)

**Type:**

bool

<a id="bpy.types.FieldSettings.use_multiple_springs"></a>

#### bpy.types.FieldSettings.use_multiple_springs

Every point is affected by multiple springs (default False)

**Type:**

bool

<a id="bpy.types.FieldSettings.use_object_coords"></a>

#### bpy.types.FieldSettings.use_object_coords

Use object/global coordinates for texture (default False)

**Type:**

bool

<a id="bpy.types.FieldSettings.use_radial_max"></a>

#### bpy.types.FieldSettings.use_radial_max

Use a maximum radial distance for the field to work (default False)

**Type:**

bool

<a id="bpy.types.FieldSettings.use_radial_min"></a>

#### bpy.types.FieldSettings.use_radial_min

Use a minimum radial distance for the field’s falloff (default False)

**Type:**

bool

<a id="bpy.types.FieldSettings.use_root_coords"></a>

#### bpy.types.FieldSettings.use_root_coords

Texture coordinates from root particle locations (default False)

**Type:**

bool

<a id="bpy.types.FieldSettings.use_smoke_density"></a>

#### bpy.types.FieldSettings.use_smoke_density

Adjust force strength based on smoke density (default False)

**Type:**

bool

<a id="bpy.types.FieldSettings.wind_factor"></a>

#### bpy.types.FieldSettings.wind_factor

How much the force is reduced when acting parallel to a surface, e.g. cloth (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.FieldSettings.z_direction"></a>

#### bpy.types.FieldSettings.z_direction

Effect in full or only positive/negative Z direction (default `'BOTH'`)

**Type:**

Literal[‘POSITIVE’, ‘NEGATIVE’, ‘BOTH’]

<a id="bpy.types.FieldSettings.bl_rna_get_subclass"></a>

#### classmethod bpy.types.FieldSettings.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.FieldSettings.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.FieldSettings.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([type](#bpy.types.FieldSettings.type "bpy.types.FieldSettings.type") | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

[type](#bpy.types.FieldSettings.type "bpy.types.FieldSettings.type")

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
| - [`Object.field`](bpy.types.Object.md#bpy.types.Object.field "bpy.types.Object.field") - [`ParticleSettings.force_field_1`](bpy.types.ParticleSettings.md#bpy.types.ParticleSettings.force_field_1 "bpy.types.ParticleSettings.force_field_1") | - [`ParticleSettings.force_field_2`](bpy.types.ParticleSettings.md#bpy.types.ParticleSettings.force_field_2 "bpy.types.ParticleSettings.force_field_2") |
