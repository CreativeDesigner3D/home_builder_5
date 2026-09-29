<!-- source: Blender Python API reference 5.2 / bpy.types.FluidFlowSettings.html -->

<a id="fluidflowsettings-bpy-struct"></a>

# FluidFlowSettings(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.FluidFlowSettings"></a>

### class bpy.types.FluidFlowSettings(bpy_struct)

Fluid flow settings

<a id="bpy.types.FluidFlowSettings.density"></a>

#### bpy.types.FluidFlowSettings.density

(in [0, 10], default 1.0)

**Type:**

float

<a id="bpy.types.FluidFlowSettings.density_vertex_group"></a>

#### bpy.types.FluidFlowSettings.density_vertex_group

Name of vertex group which determines surface emission rate (default “”, never None)

**Type:**

str

<a id="bpy.types.FluidFlowSettings.flow_behavior"></a>

#### bpy.types.FluidFlowSettings.flow_behavior

Change flow behavior in the simulation (default `'GEOMETRY'`)

- `INFLOW`
  Inflow – Add fluid to simulation.
- `OUTFLOW`
  Outflow – Delete fluid from simulation.
- `GEOMETRY`
  Geometry – Only use given geometry for fluid.

**Type:**

Literal[‘INFLOW’, ‘OUTFLOW’, ‘GEOMETRY’]

<a id="bpy.types.FluidFlowSettings.flow_source"></a>

#### bpy.types.FluidFlowSettings.flow_source

Change how fluid is emitted (default `'NONE'`)

**Type:**

Literal[‘NONE’]

<a id="bpy.types.FluidFlowSettings.flow_type"></a>

#### bpy.types.FluidFlowSettings.flow_type

Change type of fluid in the simulation (default `'SMOKE'`)

- `SMOKE`
  Smoke – Add smoke.
- `BOTH`
  Fire + Smoke – Add fire and smoke.
- `FIRE`
  Fire – Add fire.
- `LIQUID`
  Liquid – Add liquid.

**Type:**

Literal[‘SMOKE’, ‘BOTH’, ‘FIRE’, ‘LIQUID’]

<a id="bpy.types.FluidFlowSettings.fuel_amount"></a>

#### bpy.types.FluidFlowSettings.fuel_amount

(in [0, 10], default 1.0)

**Type:**

float

<a id="bpy.types.FluidFlowSettings.noise_texture"></a>

#### bpy.types.FluidFlowSettings.noise_texture

Texture that controls emission strength

**Type:**

[`Texture`](bpy.types.Texture.md#bpy.types.Texture "bpy.types.Texture") | None

<a id="bpy.types.FluidFlowSettings.particle_size"></a>

#### bpy.types.FluidFlowSettings.particle_size

Particle size in simulation cells (in [0.1, inf], default 1.0)

**Type:**

float

<a id="bpy.types.FluidFlowSettings.particle_system"></a>

#### bpy.types.FluidFlowSettings.particle_system

Particle systems emitted from the object

**Type:**

[`ParticleSystem`](bpy.types.ParticleSystem.md#bpy.types.ParticleSystem "bpy.types.ParticleSystem") | None

<a id="bpy.types.FluidFlowSettings.smoke_color"></a>

#### bpy.types.FluidFlowSettings.smoke_color

Color of smoke (array of 3 items, in [0, inf], default (0.7, 0.7, 0.7))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.FluidFlowSettings.subframes"></a>

#### bpy.types.FluidFlowSettings.subframes

Number of additional samples to take between frames to improve quality of fast moving flows (in [0, 200], default 0)

**Type:**

int

<a id="bpy.types.FluidFlowSettings.surface_distance"></a>

#### bpy.types.FluidFlowSettings.surface_distance

Height (in domain grid units) of fluid emission above the mesh surface. Higher values result in emission further away from the mesh surface. If this value and the emitter size are smaller than the domain grid unit, fluid will not be created (in [0, 10], default 1.0)

**Type:**

float

<a id="bpy.types.FluidFlowSettings.temperature"></a>

#### bpy.types.FluidFlowSettings.temperature

Temperature difference to ambient temperature (in [-10, 10], default 1.0)

**Type:**

float

<a id="bpy.types.FluidFlowSettings.texture_map_type"></a>

#### bpy.types.FluidFlowSettings.texture_map_type

Texture mapping type (default `'AUTO'`)

- `AUTO`
  Generated – Generated coordinates centered to flow object.
- `UV`
  UV – Use UV layer for texture coordinates.

**Type:**

Literal[‘AUTO’, ‘UV’]

<a id="bpy.types.FluidFlowSettings.texture_offset"></a>

#### bpy.types.FluidFlowSettings.texture_offset

Z-offset of texture mapping (in [0, 200], default 0.0)

**Type:**

float

<a id="bpy.types.FluidFlowSettings.texture_size"></a>

#### bpy.types.FluidFlowSettings.texture_size

Size of texture mapping (in [0.01, 10], default 1.0)

**Type:**

float

<a id="bpy.types.FluidFlowSettings.use_absolute"></a>

#### bpy.types.FluidFlowSettings.use_absolute

Only allow given density value in emitter area and will not add up (default True)

**Type:**

bool

<a id="bpy.types.FluidFlowSettings.use_inflow"></a>

#### bpy.types.FluidFlowSettings.use_inflow

Control when to apply fluid flow (default True)

**Type:**

bool

<a id="bpy.types.FluidFlowSettings.use_initial_velocity"></a>

#### bpy.types.FluidFlowSettings.use_initial_velocity

Fluid has some initial velocity when it is emitted (default False)

**Type:**

bool

<a id="bpy.types.FluidFlowSettings.use_particle_size"></a>

#### bpy.types.FluidFlowSettings.use_particle_size

Set particle size in simulation cells or use nearest cell (default True)

**Type:**

bool

<a id="bpy.types.FluidFlowSettings.use_plane_init"></a>

#### bpy.types.FluidFlowSettings.use_plane_init

Treat this object as a planar and unclosed mesh. Fluid will only be emitted from the mesh surface and based on the surface emission value. (default False)

**Type:**

bool

<a id="bpy.types.FluidFlowSettings.use_texture"></a>

#### bpy.types.FluidFlowSettings.use_texture

Use a texture to control emission strength (default False)

**Type:**

bool

<a id="bpy.types.FluidFlowSettings.uv_layer"></a>

#### bpy.types.FluidFlowSettings.uv_layer

UV map name (default “”, never None)

**Type:**

str

<a id="bpy.types.FluidFlowSettings.velocity_coord"></a>

#### bpy.types.FluidFlowSettings.velocity_coord

Additional initial velocity in X, Y and Z direction (added to source velocity) (array of 3 items, in [-1000.1, 1000.1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.FluidFlowSettings.velocity_factor"></a>

#### bpy.types.FluidFlowSettings.velocity_factor

Multiplier of source velocity passed to fluid (source velocity is non-zero only if object is moving) (in [-100, 100], default 1.0)

**Type:**

float

<a id="bpy.types.FluidFlowSettings.velocity_normal"></a>

#### bpy.types.FluidFlowSettings.velocity_normal

Amount of normal directional velocity (in [-100, 100], default 0.0)

**Type:**

float

<a id="bpy.types.FluidFlowSettings.velocity_random"></a>

#### bpy.types.FluidFlowSettings.velocity_random

Amount of random velocity (in [0, 10], default 0.0)

**Type:**

float

<a id="bpy.types.FluidFlowSettings.volume_density"></a>

#### bpy.types.FluidFlowSettings.volume_density

Controls fluid emission from within the mesh (higher value results in greater emissions from inside the mesh) (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.FluidFlowSettings.bl_rna_get_subclass"></a>

#### classmethod bpy.types.FluidFlowSettings.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.FluidFlowSettings.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.FluidFlowSettings.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`FluidModifier.flow_settings`](bpy.types.FluidModifier.md#bpy.types.FluidModifier.flow_settings "bpy.types.FluidModifier.flow_settings") |  |
