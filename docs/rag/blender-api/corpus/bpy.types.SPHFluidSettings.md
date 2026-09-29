<!-- source: Blender Python API reference 5.2 / bpy.types.SPHFluidSettings.html -->

<a id="sphfluidsettings-bpy-struct"></a>

# SPHFluidSettings(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.SPHFluidSettings"></a>

### class bpy.types.SPHFluidSettings(bpy_struct)

Settings for particle fluids physics

<a id="bpy.types.SPHFluidSettings.buoyancy"></a>

#### bpy.types.SPHFluidSettings.buoyancy

Artificial buoyancy force in negative gravity direction based on pressure differences inside the fluid (in [0, 10], default 0.0)

**Type:**

float

<a id="bpy.types.SPHFluidSettings.fluid_radius"></a>

#### bpy.types.SPHFluidSettings.fluid_radius

Fluid interaction radius (in [0, 20], default 0.0)

**Type:**

float

<a id="bpy.types.SPHFluidSettings.linear_viscosity"></a>

#### bpy.types.SPHFluidSettings.linear_viscosity

Linear viscosity (in [0, 100], default 0.0)

**Type:**

float

<a id="bpy.types.SPHFluidSettings.plasticity"></a>

#### bpy.types.SPHFluidSettings.plasticity

How much the spring rest length can change after the elastic limit is crossed (in [0, 100], default 0.0)

**Type:**

float

<a id="bpy.types.SPHFluidSettings.repulsion"></a>

#### bpy.types.SPHFluidSettings.repulsion

How strongly the fluid tries to keep from clustering (factor of stiffness) (in [0, 100], default 0.0)

**Type:**

float

<a id="bpy.types.SPHFluidSettings.rest_density"></a>

#### bpy.types.SPHFluidSettings.rest_density

Fluid rest density (in [0, 10000], default 0.0)

**Type:**

float

<a id="bpy.types.SPHFluidSettings.rest_length"></a>

#### bpy.types.SPHFluidSettings.rest_length

Spring rest length (factor of particle radius) (in [0, 2], default 0.0)

**Type:**

float

<a id="bpy.types.SPHFluidSettings.solver"></a>

#### bpy.types.SPHFluidSettings.solver

The code used to calculate internal forces on particles (default `'DDR'`)

- `DDR`
  Double-Density – An artistic solver with strong surface tension effects (original).
- `CLASSICAL`
  Classical – A more physically-accurate solver.

**Type:**

Literal[‘DDR’, ‘CLASSICAL’]

<a id="bpy.types.SPHFluidSettings.spring_force"></a>

#### bpy.types.SPHFluidSettings.spring_force

Spring force (in [0, 100], default 0.0)

**Type:**

float

<a id="bpy.types.SPHFluidSettings.spring_frames"></a>

#### bpy.types.SPHFluidSettings.spring_frames

Create springs for this number of frames since particles birth (0 is always) (in [0, 100], default 0)

**Type:**

int

<a id="bpy.types.SPHFluidSettings.stiff_viscosity"></a>

#### bpy.types.SPHFluidSettings.stiff_viscosity

Creates viscosity for expanding fluid (in [0, 100], default 0.0)

**Type:**

float

<a id="bpy.types.SPHFluidSettings.stiffness"></a>

#### bpy.types.SPHFluidSettings.stiffness

How incompressible the fluid is (speed of sound) (in [0, 1000], default 0.0)

**Type:**

float

<a id="bpy.types.SPHFluidSettings.use_factor_density"></a>

#### bpy.types.SPHFluidSettings.use_factor_density

Density is calculated as a factor of default density (depends on particle size) (default False)

**Type:**

bool

<a id="bpy.types.SPHFluidSettings.use_factor_radius"></a>

#### bpy.types.SPHFluidSettings.use_factor_radius

Interaction radius is a factor of 4 * particle size (default False)

**Type:**

bool

<a id="bpy.types.SPHFluidSettings.use_factor_repulsion"></a>

#### bpy.types.SPHFluidSettings.use_factor_repulsion

Repulsion is a factor of stiffness (default False)

**Type:**

bool

<a id="bpy.types.SPHFluidSettings.use_factor_rest_length"></a>

#### bpy.types.SPHFluidSettings.use_factor_rest_length

Spring rest length is a factor of 2 * particle size (default False)

**Type:**

bool

<a id="bpy.types.SPHFluidSettings.use_factor_stiff_viscosity"></a>

#### bpy.types.SPHFluidSettings.use_factor_stiff_viscosity

Stiff viscosity is a factor of normal viscosity (default False)

**Type:**

bool

<a id="bpy.types.SPHFluidSettings.use_initial_rest_length"></a>

#### bpy.types.SPHFluidSettings.use_initial_rest_length

Use the initial length as spring rest length instead of 2 * particle size (default False)

**Type:**

bool

<a id="bpy.types.SPHFluidSettings.use_viscoelastic_springs"></a>

#### bpy.types.SPHFluidSettings.use_viscoelastic_springs

Use viscoelastic springs instead of Hooke’s springs (default False)

**Type:**

bool

<a id="bpy.types.SPHFluidSettings.yield_ratio"></a>

#### bpy.types.SPHFluidSettings.yield_ratio

How much the spring has to be stretched/compressed in order to change its rest length (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.SPHFluidSettings.bl_rna_get_subclass"></a>

#### classmethod bpy.types.SPHFluidSettings.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.SPHFluidSettings.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.SPHFluidSettings.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`ParticleSettings.fluid`](bpy.types.ParticleSettings.md#bpy.types.ParticleSettings.fluid "bpy.types.ParticleSettings.fluid") |  |
