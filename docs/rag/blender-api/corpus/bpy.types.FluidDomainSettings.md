<!-- source: Blender Python API reference 5.2 / bpy.types.FluidDomainSettings.html -->

<a id="fluiddomainsettings-bpy-struct"></a>

# FluidDomainSettings(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.FluidDomainSettings"></a>

### class bpy.types.FluidDomainSettings(bpy_struct)

Fluid domain settings

<a id="bpy.types.FluidDomainSettings.adapt_margin"></a>

#### bpy.types.FluidDomainSettings.adapt_margin

Margin added around fluid to minimize boundary interference (in [2, 24], default 4)

**Type:**

int

<a id="bpy.types.FluidDomainSettings.adapt_threshold"></a>

#### bpy.types.FluidDomainSettings.adapt_threshold

Minimum amount of fluid grid values (smoke density, fuel and heat) a cell can contain, before it is considered empty (in [0, 1], default 0.002)

**Type:**

float

<a id="bpy.types.FluidDomainSettings.additional_res"></a>

#### bpy.types.FluidDomainSettings.additional_res

Maximum number of additional cells (in [0, 512], default 0)

**Type:**

int

<a id="bpy.types.FluidDomainSettings.alpha"></a>

#### bpy.types.FluidDomainSettings.alpha

Buoyant force based on smoke density (higher value results in faster rising smoke) (in [-5, 5], default 1.0)

**Type:**

float

<a id="bpy.types.FluidDomainSettings.beta"></a>

#### bpy.types.FluidDomainSettings.beta

Buoyant force based on smoke heat (higher value results in faster rising smoke) (in [-5, 5], default 1.0)

**Type:**

float

<a id="bpy.types.FluidDomainSettings.burning_rate"></a>

#### bpy.types.FluidDomainSettings.burning_rate

Speed of the burning reaction (higher value results in smaller flames) (in [0.01, 4], default 0.75)

**Type:**

float

<a id="bpy.types.FluidDomainSettings.cache_data_format"></a>

#### bpy.types.FluidDomainSettings.cache_data_format

Select the file format to be used for caching volumetric data (default `'OPENVDB'`)

- `UNI`
  Uni Cache – Uni file format (.uni).
- `OPENVDB`
  OpenVDB – OpenVDB file format (.vdb).
- `RAW`
  Raw Cache – Raw file format (.raw).

**Type:**

Literal[‘UNI’, ‘OPENVDB’, ‘RAW’]

<a id="bpy.types.FluidDomainSettings.cache_directory"></a>

#### bpy.types.FluidDomainSettings.cache_directory

Directory that contains fluid cache files (default “”, never None, blend relative `//` prefix supported)

**Type:**

str

<a id="bpy.types.FluidDomainSettings.cache_frame_end"></a>

#### bpy.types.FluidDomainSettings.cache_frame_end

Frame on which the simulation stops (last frame baked) (in [-1048574, 1048574], default 250)

**Type:**

int

<a id="bpy.types.FluidDomainSettings.cache_frame_offset"></a>

#### bpy.types.FluidDomainSettings.cache_frame_offset

Frame offset that is used when loading the simulation from the cache. It is not considered when baking the simulation, only when loading it. (in [-1048574, 1048574], default 0)

**Type:**

int

<a id="bpy.types.FluidDomainSettings.cache_frame_pause_data"></a>

#### bpy.types.FluidDomainSettings.cache_frame_pause_data

(in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.FluidDomainSettings.cache_frame_pause_guide"></a>

#### bpy.types.FluidDomainSettings.cache_frame_pause_guide

(in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.FluidDomainSettings.cache_frame_pause_mesh"></a>

#### bpy.types.FluidDomainSettings.cache_frame_pause_mesh

(in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.FluidDomainSettings.cache_frame_pause_noise"></a>

#### bpy.types.FluidDomainSettings.cache_frame_pause_noise

(in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.FluidDomainSettings.cache_frame_pause_particles"></a>

#### bpy.types.FluidDomainSettings.cache_frame_pause_particles

(in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.FluidDomainSettings.cache_frame_start"></a>

#### bpy.types.FluidDomainSettings.cache_frame_start

Frame on which the simulation starts (first frame baked) (in [-1048574, 1048574], default 1)

**Type:**

int

<a id="bpy.types.FluidDomainSettings.cache_mesh_format"></a>

#### bpy.types.FluidDomainSettings.cache_mesh_format

Select the file format to be used for caching surface data (default `'UNI'`)

- `UNI`
  Uni Cache – Uni file format (.uni).
- `OPENVDB`
  OpenVDB – OpenVDB file format (.vdb).
- `RAW`
  Raw Cache – Raw file format (.raw).

**Type:**

Literal[‘UNI’, ‘OPENVDB’, ‘RAW’]

<a id="bpy.types.FluidDomainSettings.cache_noise_format"></a>

#### bpy.types.FluidDomainSettings.cache_noise_format

Select the file format to be used for caching noise data (default `'OPENVDB'`)

- `UNI`
  Uni Cache – Uni file format (.uni).
- `OPENVDB`
  OpenVDB – OpenVDB file format (.vdb).
- `RAW`
  Raw Cache – Raw file format (.raw).

**Type:**

Literal[‘UNI’, ‘OPENVDB’, ‘RAW’]

<a id="bpy.types.FluidDomainSettings.cache_particle_format"></a>

#### bpy.types.FluidDomainSettings.cache_particle_format

Select the file format to be used for caching particle data (default `'OPENVDB'`)

- `UNI`
  Uni Cache – Uni file format (.uni).
- `OPENVDB`
  OpenVDB – OpenVDB file format (.vdb).
- `RAW`
  Raw Cache – Raw file format (.raw).

**Type:**

Literal[‘UNI’, ‘OPENVDB’, ‘RAW’]

<a id="bpy.types.FluidDomainSettings.cache_resumable"></a>

#### bpy.types.FluidDomainSettings.cache_resumable

Additional data will be saved so that the bake jobs can be resumed after pausing. Because more data will be written to disk it is recommended to avoid enabling this option when baking at high resolutions. (default False)

**Type:**

bool

<a id="bpy.types.FluidDomainSettings.cache_type"></a>

#### bpy.types.FluidDomainSettings.cache_type

Change the cache type of the simulation (default `'REPLAY'`)

- `REPLAY`
  Replay – Use the timeline to bake the scene.
- `MODULAR`
  Modular – Bake every stage of the simulation separately.
- `ALL`
  All – Bake all simulation settings at once.

**Type:**

Literal[‘REPLAY’, ‘MODULAR’, ‘ALL’]

<a id="bpy.types.FluidDomainSettings.cell_size"></a>

#### bpy.types.FluidDomainSettings.cell_size

Cell Size (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0), readonly)

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.FluidDomainSettings.cfl_condition"></a>

#### bpy.types.FluidDomainSettings.cfl_condition

Maximal velocity per cell (greater CFL numbers will minimize the number of simulation steps and the computation time.) (in [0, 10], default 2.0)

**Type:**

float

<a id="bpy.types.FluidDomainSettings.clipping"></a>

#### bpy.types.FluidDomainSettings.clipping

Value under which voxels are considered empty space to optimize rendering (in [0, 1], default 1e-06)

**Type:**

float

<a id="bpy.types.FluidDomainSettings.color_grid"></a>

#### bpy.types.FluidDomainSettings.color_grid

Smoke color grid (array of 32 items, in [-inf, inf], default (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0), readonly)

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.FluidDomainSettings.color_ramp"></a>

#### bpy.types.FluidDomainSettings.color_ramp

(readonly)

**Type:**

[`ColorRamp`](bpy.types.ColorRamp.md#bpy.types.ColorRamp "bpy.types.ColorRamp") | None

<a id="bpy.types.FluidDomainSettings.color_ramp_field"></a>

#### bpy.types.FluidDomainSettings.color_ramp_field

Simulation field to color map (default `'NONE'`)

**Type:**

Literal[‘NONE’]

<a id="bpy.types.FluidDomainSettings.color_ramp_field_scale"></a>

#### bpy.types.FluidDomainSettings.color_ramp_field_scale

Multiplier for scaling the selected field to color map (in [0.001, 100000], default 1.0)

**Type:**

float

<a id="bpy.types.FluidDomainSettings.delete_in_obstacle"></a>

#### bpy.types.FluidDomainSettings.delete_in_obstacle

Delete fluid inside obstacles (default False)

**Type:**

bool

<a id="bpy.types.FluidDomainSettings.density_grid"></a>

#### bpy.types.FluidDomainSettings.density_grid

Smoke density grid (array of 32 items, in [-inf, inf], default (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0), readonly)

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.FluidDomainSettings.display_interpolation"></a>

#### bpy.types.FluidDomainSettings.display_interpolation

Interpolation method to use for smoke/fire volumes in solid mode (default `'LINEAR'`)

- `LINEAR`
  Linear – Good smoothness and speed.
- `CUBIC`
  Cubic – Smoothed high quality interpolation, but slower.
- `CLOSEST`
  Closest – No interpolation.

**Type:**

Literal[‘LINEAR’, ‘CUBIC’, ‘CLOSEST’]

<a id="bpy.types.FluidDomainSettings.display_thickness"></a>

#### bpy.types.FluidDomainSettings.display_thickness

Thickness of smoke display in the viewport (in [0.001, 1000], default 1.0)

**Type:**

float

<a id="bpy.types.FluidDomainSettings.dissolve_speed"></a>

#### bpy.types.FluidDomainSettings.dissolve_speed

Determine how quickly the smoke dissolves (lower value makes smoke disappear faster) (in [1, 10000], default 5)

**Type:**

int

<a id="bpy.types.FluidDomainSettings.domain_resolution"></a>

#### bpy.types.FluidDomainSettings.domain_resolution

Smoke Grid Resolution (array of 3 items, in [-inf, inf], default (0, 0, 0), readonly)

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[int]

<a id="bpy.types.FluidDomainSettings.domain_type"></a>

#### bpy.types.FluidDomainSettings.domain_type

Change domain type of the simulation (default `'GAS'`)

- `GAS`
  Gas – Create domain for gases.
- `LIQUID`
  Liquid – Create domain for liquids.

**Type:**

Literal[‘GAS’, ‘LIQUID’]

<a id="bpy.types.FluidDomainSettings.effector_group"></a>

#### bpy.types.FluidDomainSettings.effector_group

Limit effectors to this collection

**Type:**

[`Collection`](bpy.types.Collection.md#bpy.types.Collection "bpy.types.Collection") | None

<a id="bpy.types.FluidDomainSettings.effector_weights"></a>

#### bpy.types.FluidDomainSettings.effector_weights

(readonly)

**Type:**

[`EffectorWeights`](bpy.types.EffectorWeights.md#bpy.types.EffectorWeights "bpy.types.EffectorWeights") | None

<a id="bpy.types.FluidDomainSettings.export_manta_script"></a>

#### bpy.types.FluidDomainSettings.export_manta_script

Generate and export Mantaflow script from current domain settings during bake. This is only needed if you plan to analyze the cache (e.g. view grids, velocity vectors, particles) in Mantaflow directly (outside of Blender) after baking the simulation. (default False)

**Type:**

bool

<a id="bpy.types.FluidDomainSettings.flame_grid"></a>

#### bpy.types.FluidDomainSettings.flame_grid

Smoke flame grid (array of 32 items, in [-inf, inf], default (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0), readonly)

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.FluidDomainSettings.flame_ignition"></a>

#### bpy.types.FluidDomainSettings.flame_ignition

Minimum temperature of the flames (higher value results in faster rising flames) (in [0.5, 5], default 1.5)

**Type:**

float

<a id="bpy.types.FluidDomainSettings.flame_max_temp"></a>

#### bpy.types.FluidDomainSettings.flame_max_temp

Maximum temperature of the flames (higher value results in faster rising flames) (in [1, 10], default 3.0)

**Type:**

float

<a id="bpy.types.FluidDomainSettings.flame_smoke"></a>

#### bpy.types.FluidDomainSettings.flame_smoke

Amount of smoke created by burning fuel (in [0, 8], default 1.0)

**Type:**

float

<a id="bpy.types.FluidDomainSettings.flame_smoke_color"></a>

#### bpy.types.FluidDomainSettings.flame_smoke_color

Color of smoke emitted from burning fuel (array of 3 items, in [0, inf], default (0.7, 0.7, 0.7))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.FluidDomainSettings.flame_vorticity"></a>

#### bpy.types.FluidDomainSettings.flame_vorticity

Additional vorticity for the flames (in [0, 2], default 0.5)

**Type:**

float

<a id="bpy.types.FluidDomainSettings.flip_ratio"></a>

#### bpy.types.FluidDomainSettings.flip_ratio

PIC/FLIP Ratio. A value of 1.0 will result in a completely FLIP based simulation. Use a lower value for simulations which should produce smaller splashes. (in [0, 1], default 0.97)

**Type:**

float

<a id="bpy.types.FluidDomainSettings.fluid_group"></a>

#### bpy.types.FluidDomainSettings.fluid_group

Limit fluid objects to this collection

**Type:**

[`Collection`](bpy.types.Collection.md#bpy.types.Collection "bpy.types.Collection") | None

<a id="bpy.types.FluidDomainSettings.force_collection"></a>

#### bpy.types.FluidDomainSettings.force_collection

Limit forces to this collection

**Type:**

[`Collection`](bpy.types.Collection.md#bpy.types.Collection "bpy.types.Collection") | None

<a id="bpy.types.FluidDomainSettings.fractions_distance"></a>

#### bpy.types.FluidDomainSettings.fractions_distance

Determines how far apart fluid and obstacle are (higher values will result in fluid being further away from obstacles, smaller values will let fluid move towards the inside of obstacles) (in [-5, 5], default 0.5)

**Type:**

float

<a id="bpy.types.FluidDomainSettings.fractions_threshold"></a>

#### bpy.types.FluidDomainSettings.fractions_threshold

Determines how much fluid is allowed in an obstacle cell (higher values will tag a boundary cell as an obstacle easier and reduce the boundary smoothening effect) (in [0.001, 1], default 0.05)

**Type:**

float

<a id="bpy.types.FluidDomainSettings.gravity"></a>

#### bpy.types.FluidDomainSettings.gravity

Gravity in X, Y and Z direction (array of 3 items, in [-1000.1, 1000.1], default (0.0, 0.0, -9.81))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.FluidDomainSettings.gridlines_cell_filter"></a>

#### bpy.types.FluidDomainSettings.gridlines_cell_filter

Cell type to be highlighted (default `'NONE'`)

- `NONE`
  None – Highlight the cells regardless of their type.
- `FLUID`
  Fluid – Highlight only the cells of type Fluid.
- `OBSTACLE`
  Obstacle – Highlight only the cells of type Obstacle.
- `EMPTY`
  Empty – Highlight only the cells of type Empty.
- `INFLOW`
  Inflow – Highlight only the cells of type Inflow.
- `OUTFLOW`
  Outflow – Highlight only the cells of type Outflow.

**Type:**

Literal[‘NONE’, ‘FLUID’, ‘OBSTACLE’, ‘EMPTY’, ‘INFLOW’, ‘OUTFLOW’]

<a id="bpy.types.FluidDomainSettings.gridlines_color_field"></a>

#### bpy.types.FluidDomainSettings.gridlines_color_field

Simulation field to color map onto gridlines (default `'NONE'`)

- `NONE`
  None – None.
- `FLAGS`
  Flags – Flag grid of the fluid domain.
- `RANGE`
  Highlight Range – Highlight the voxels with values of the color mapped field within the range.

**Type:**

Literal[‘NONE’, ‘FLAGS’, ‘RANGE’]

<a id="bpy.types.FluidDomainSettings.gridlines_lower_bound"></a>

#### bpy.types.FluidDomainSettings.gridlines_lower_bound

Lower bound of the highlighting range (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.FluidDomainSettings.gridlines_range_color"></a>

#### bpy.types.FluidDomainSettings.gridlines_range_color

Color used to highlight the range (array of 4 items, in [0, inf], default (1.0, 0.0, 0.0, 1.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.FluidDomainSettings.gridlines_upper_bound"></a>

#### bpy.types.FluidDomainSettings.gridlines_upper_bound

Upper bound of the highlighting range (in [-inf, inf], default 1.0)

**Type:**

float

<a id="bpy.types.FluidDomainSettings.guide_alpha"></a>

#### bpy.types.FluidDomainSettings.guide_alpha

Guiding weight (higher value results in greater lag) (in [1, 100], default 2.0)

**Type:**

float

<a id="bpy.types.FluidDomainSettings.guide_beta"></a>

#### bpy.types.FluidDomainSettings.guide_beta

Guiding size (higher value results in larger vortices) (in [1, 50], default 5)

**Type:**

int

<a id="bpy.types.FluidDomainSettings.guide_parent"></a>

#### bpy.types.FluidDomainSettings.guide_parent

Use velocities from this object for the guiding effect (object needs to have fluid modifier and be of type domain))

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.FluidDomainSettings.guide_source"></a>

#### bpy.types.FluidDomainSettings.guide_source

Choose where to get guiding velocities from (default `'DOMAIN'`)

- `DOMAIN`
  Domain – Use a fluid domain for guiding (domain needs to be baked already so that velocities can be extracted). Guiding domain can be of any type (i.e. gas or liquid)..
- `EFFECTOR`
  Effector – Use guiding (effector) objects to create fluid guiding (guiding objects should be animated and baked once set up completely).

**Type:**

Literal[‘DOMAIN’, ‘EFFECTOR’]

<a id="bpy.types.FluidDomainSettings.guide_vel_factor"></a>

#### bpy.types.FluidDomainSettings.guide_vel_factor

Guiding velocity factor (higher value results in greater guiding velocities) (in [0, 100], default 2.0)

**Type:**

float

<a id="bpy.types.FluidDomainSettings.has_cache_baked_any"></a>

#### bpy.types.FluidDomainSettings.has_cache_baked_any

(default False)

**Type:**

bool

<a id="bpy.types.FluidDomainSettings.has_cache_baked_data"></a>

#### bpy.types.FluidDomainSettings.has_cache_baked_data

(default False)

**Type:**

bool

<a id="bpy.types.FluidDomainSettings.has_cache_baked_guide"></a>

#### bpy.types.FluidDomainSettings.has_cache_baked_guide

(default False)

**Type:**

bool

<a id="bpy.types.FluidDomainSettings.has_cache_baked_mesh"></a>

#### bpy.types.FluidDomainSettings.has_cache_baked_mesh

(default False)

**Type:**

bool

<a id="bpy.types.FluidDomainSettings.has_cache_baked_noise"></a>

#### bpy.types.FluidDomainSettings.has_cache_baked_noise

(default False)

**Type:**

bool

<a id="bpy.types.FluidDomainSettings.has_cache_baked_particles"></a>

#### bpy.types.FluidDomainSettings.has_cache_baked_particles

(default False)

**Type:**

bool

<a id="bpy.types.FluidDomainSettings.heat_grid"></a>

#### bpy.types.FluidDomainSettings.heat_grid

Smoke heat grid (array of 32 items, in [-inf, inf], default (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0), readonly)

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.FluidDomainSettings.highres_sampling"></a>

#### bpy.types.FluidDomainSettings.highres_sampling

Method for sampling the high resolution flow (default `'FULLSAMPLE'`)

**Type:**

Literal[‘FULLSAMPLE’, ‘LINEAR’, ‘NEAREST’]

<a id="bpy.types.FluidDomainSettings.is_cache_baking_any"></a>

#### bpy.types.FluidDomainSettings.is_cache_baking_any

(default False)

**Type:**

bool

<a id="bpy.types.FluidDomainSettings.is_cache_baking_data"></a>

#### bpy.types.FluidDomainSettings.is_cache_baking_data

(default False)

**Type:**

bool

<a id="bpy.types.FluidDomainSettings.is_cache_baking_guide"></a>

#### bpy.types.FluidDomainSettings.is_cache_baking_guide

(default False)

**Type:**

bool

<a id="bpy.types.FluidDomainSettings.is_cache_baking_mesh"></a>

#### bpy.types.FluidDomainSettings.is_cache_baking_mesh

(default False)

**Type:**

bool

<a id="bpy.types.FluidDomainSettings.is_cache_baking_noise"></a>

#### bpy.types.FluidDomainSettings.is_cache_baking_noise

(default False)

**Type:**

bool

<a id="bpy.types.FluidDomainSettings.is_cache_baking_particles"></a>

#### bpy.types.FluidDomainSettings.is_cache_baking_particles

(default False)

**Type:**

bool

<a id="bpy.types.FluidDomainSettings.mesh_concave_lower"></a>

#### bpy.types.FluidDomainSettings.mesh_concave_lower

Lower mesh concavity bound (high values tend to smoothen and fill out concave regions) (in [0, 10], default 0.4)

**Type:**

float

<a id="bpy.types.FluidDomainSettings.mesh_concave_upper"></a>

#### bpy.types.FluidDomainSettings.mesh_concave_upper

Upper mesh concavity bound (high values tend to smoothen and fill out concave regions) (in [0, 10], default 3.5)

**Type:**

float

<a id="bpy.types.FluidDomainSettings.mesh_generator"></a>

#### bpy.types.FluidDomainSettings.mesh_generator

Which particle level set generator to use (default `'IMPROVED'`)

- `IMPROVED`
  Final – Use improved particle level set (slower but more precise and with mesh smoothening options).
- `UNION`
  Preview – Use union particle level set (faster but lower quality).

**Type:**

Literal[‘IMPROVED’, ‘UNION’]

<a id="bpy.types.FluidDomainSettings.mesh_particle_radius"></a>

#### bpy.types.FluidDomainSettings.mesh_particle_radius

Particle radius factor (higher value results in larger (meshed) particles). Needs to be adjusted after changing the mesh scale. (in [0, 10], default 2.0)

**Type:**

float

<a id="bpy.types.FluidDomainSettings.mesh_scale"></a>

#### bpy.types.FluidDomainSettings.mesh_scale

The mesh simulation is scaled up by this factor (compared to the base resolution of the domain). For best meshing, it is recommended to adjust the mesh particle radius alongside this value. (in [1, 100], default 2)

**Type:**

int

<a id="bpy.types.FluidDomainSettings.mesh_smoothen_neg"></a>

#### bpy.types.FluidDomainSettings.mesh_smoothen_neg

Negative mesh smoothening (in [0, 100], default 1)

**Type:**

int

<a id="bpy.types.FluidDomainSettings.mesh_smoothen_pos"></a>

#### bpy.types.FluidDomainSettings.mesh_smoothen_pos

Positive mesh smoothening (in [0, 100], default 1)

**Type:**

int

<a id="bpy.types.FluidDomainSettings.noise_pos_scale"></a>

#### bpy.types.FluidDomainSettings.noise_pos_scale

Scale of noise (higher value results in larger vortices) (in [0.0001, 10], default 2.0)

**Type:**

float

<a id="bpy.types.FluidDomainSettings.noise_scale"></a>

#### bpy.types.FluidDomainSettings.noise_scale

The noise simulation is scaled up by this factor (compared to the base resolution of the domain) (in [1, 100], default 2)

**Type:**

int

<a id="bpy.types.FluidDomainSettings.noise_strength"></a>

#### bpy.types.FluidDomainSettings.noise_strength

Strength of noise (in [0, 10], default 1.0)

**Type:**

float

<a id="bpy.types.FluidDomainSettings.noise_time_anim"></a>

#### bpy.types.FluidDomainSettings.noise_time_anim

Animation time of noise (in [0.0001, 10], default 0.1)

**Type:**

float

<a id="bpy.types.FluidDomainSettings.openvdb_cache_compress_type"></a>

#### bpy.types.FluidDomainSettings.openvdb_cache_compress_type

Compression method to be used (default `'BLOSC'`)

- `ZIP`
  Zip – Effective but slow compression.
- `BLOSC`
  Blosc – Multithreaded compression, similar in size and quality as ‘Zip’.
- `NONE`
  None – Do not use any compression.

**Type:**

Literal[‘ZIP’, ‘BLOSC’, ‘NONE’]

<a id="bpy.types.FluidDomainSettings.openvdb_data_depth"></a>

#### bpy.types.FluidDomainSettings.openvdb_data_depth

Bit depth for fluid particles and grids (lower bit values reduce file size) (default `'NONE'`)

**Type:**

Literal[‘NONE’]

<a id="bpy.types.FluidDomainSettings.particle_band_width"></a>

#### bpy.types.FluidDomainSettings.particle_band_width

Particle (narrow) band width (higher value results in thicker band and more particles) (in [0, 1000], default 3.0)

**Type:**

float

<a id="bpy.types.FluidDomainSettings.particle_max"></a>

#### bpy.types.FluidDomainSettings.particle_max

Maximum number of particles per cell (ensures that each cell has at most this amount of particles) (in [0, 1000], default 16)

**Type:**

int

<a id="bpy.types.FluidDomainSettings.particle_min"></a>

#### bpy.types.FluidDomainSettings.particle_min

Minimum number of particles per cell (ensures that each cell has at least this amount of particles) (in [0, 1000], default 8)

**Type:**

int

<a id="bpy.types.FluidDomainSettings.particle_number"></a>

#### bpy.types.FluidDomainSettings.particle_number

Particle number factor (higher value results in more particles) (in [1, 5], default 2)

**Type:**

int

<a id="bpy.types.FluidDomainSettings.particle_radius"></a>

#### bpy.types.FluidDomainSettings.particle_radius

Particle radius factor. Increase this value if the simulation appears to leak volume, decrease it if the simulation seems to gain volume. (in [0, 10], default 1.0)

**Type:**

float

<a id="bpy.types.FluidDomainSettings.particle_randomness"></a>

#### bpy.types.FluidDomainSettings.particle_randomness

Randomness factor for particle sampling (in [0, 10], default 0.1)

**Type:**

float

<a id="bpy.types.FluidDomainSettings.particle_scale"></a>

#### bpy.types.FluidDomainSettings.particle_scale

The particle simulation is scaled up by this factor (compared to the base resolution of the domain) (in [1, 100], default 1)

**Type:**

int

<a id="bpy.types.FluidDomainSettings.resolution_max"></a>

#### bpy.types.FluidDomainSettings.resolution_max

Resolution used for the fluid domain. Value corresponds to the longest domain side (resolution for other domain sides is calculated automatically). (in [6, 10000], default 32)

**Type:**

int

<a id="bpy.types.FluidDomainSettings.show_gridlines"></a>

#### bpy.types.FluidDomainSettings.show_gridlines

Show gridlines (default False)

**Type:**

bool

<a id="bpy.types.FluidDomainSettings.show_velocity"></a>

#### bpy.types.FluidDomainSettings.show_velocity

Visualize vector fields (default False)

**Type:**

bool

<a id="bpy.types.FluidDomainSettings.simulation_method"></a>

#### bpy.types.FluidDomainSettings.simulation_method

Change the underlying simulation method (default `'FLIP'`)

- `FLIP`
  FLIP – Use FLIP as the simulation method (more splashy behavior).
- `APIC`
  APIC – Use APIC as the simulation method (more energetic and stable behavior).

**Type:**

Literal[‘FLIP’, ‘APIC’]

<a id="bpy.types.FluidDomainSettings.slice_axis"></a>

#### bpy.types.FluidDomainSettings.slice_axis

(default `'AUTO'`)

- `AUTO`
  Auto – Adjust slice direction according to the view direction.
- `X`
  X – Slice along the X axis.
- `Y`
  Y – Slice along the Y axis.
- `Z`
  Z – Slice along the Z axis.

**Type:**

Literal[‘AUTO’, ‘X’, ‘Y’, ‘Z’]

<a id="bpy.types.FluidDomainSettings.slice_depth"></a>

#### bpy.types.FluidDomainSettings.slice_depth

Position of the slice (in [0, 1], default 0.5)

**Type:**

float

<a id="bpy.types.FluidDomainSettings.slice_per_voxel"></a>

#### bpy.types.FluidDomainSettings.slice_per_voxel

How many slices per voxel should be generated (in [0, 100], default 5.0)

**Type:**

float

<a id="bpy.types.FluidDomainSettings.sndparticle_boundary"></a>

#### bpy.types.FluidDomainSettings.sndparticle_boundary

How particles that left the domain are treated (default `'DELETE'`)

- `DELETE`
  Delete – Delete secondary particles that are inside obstacles or left the domain.
- `PUSHOUT`
  Push Out – Push secondary particles that left the domain back into the domain.

**Type:**

Literal[‘DELETE’, ‘PUSHOUT’]

<a id="bpy.types.FluidDomainSettings.sndparticle_bubble_buoyancy"></a>

#### bpy.types.FluidDomainSettings.sndparticle_bubble_buoyancy

Amount of buoyancy force that rises bubbles (high value results in bubble movement mainly upwards) (in [0, 100], default 0.5)

**Type:**

float

<a id="bpy.types.FluidDomainSettings.sndparticle_bubble_drag"></a>

#### bpy.types.FluidDomainSettings.sndparticle_bubble_drag

Amount of drag force that moves bubbles along with the fluid (high value results in bubble movement mainly along with the fluid) (in [0, 100], default 0.6)

**Type:**

float

<a id="bpy.types.FluidDomainSettings.sndparticle_combined_export"></a>

#### bpy.types.FluidDomainSettings.sndparticle_combined_export

Determines which particle systems are created from secondary particles (default `'OFF'`)

- `OFF`
  Off – Create a separate particle system for every secondary particle type.
- `SPRAY_FOAM`
  Spray + Foam – Spray and foam particles are saved in the same particle system.
- `SPRAY_BUBBLES`
  Spray + Bubbles – Spray and bubble particles are saved in the same particle system.
- `FOAM_BUBBLES`
  Foam + Bubbles – Foam and bubbles particles are saved in the same particle system.
- `SPRAY_FOAM_BUBBLES`
  Spray + Foam + Bubbles – Create one particle system that contains all three secondary particle types.

**Type:**

Literal[‘OFF’, ‘SPRAY_FOAM’, ‘SPRAY_BUBBLES’, ‘FOAM_BUBBLES’, ‘SPRAY_FOAM_BUBBLES’]

<a id="bpy.types.FluidDomainSettings.sndparticle_life_max"></a>

#### bpy.types.FluidDomainSettings.sndparticle_life_max

Highest possible particle lifetime (in [0, 10000], default 25.0)

**Type:**

float

<a id="bpy.types.FluidDomainSettings.sndparticle_life_min"></a>

#### bpy.types.FluidDomainSettings.sndparticle_life_min

Lowest possible particle lifetime (in [0, 10000], default 10.0)

**Type:**

float

<a id="bpy.types.FluidDomainSettings.sndparticle_potential_max_energy"></a>

#### bpy.types.FluidDomainSettings.sndparticle_potential_max_energy

Upper clamping threshold that indicates the fluid speed where cells no longer emit more particles (higher value results in generally less particles) (in [0, 1000], default 5.0)

**Type:**

float

<a id="bpy.types.FluidDomainSettings.sndparticle_potential_max_trappedair"></a>

#### bpy.types.FluidDomainSettings.sndparticle_potential_max_trappedair

Upper clamping threshold for marking fluid cells where air is trapped (higher value results in less marked cells) (in [0, 1000], default 20.0)

**Type:**

float

<a id="bpy.types.FluidDomainSettings.sndparticle_potential_max_wavecrest"></a>

#### bpy.types.FluidDomainSettings.sndparticle_potential_max_wavecrest

Upper clamping threshold for marking fluid cells as wave crests (higher value results in less marked cells) (in [0, 1000], default 8.0)

**Type:**

float

<a id="bpy.types.FluidDomainSettings.sndparticle_potential_min_energy"></a>

#### bpy.types.FluidDomainSettings.sndparticle_potential_min_energy

Lower clamping threshold that indicates the fluid speed where cells start to emit particles (lower values result in generally more particles) (in [0, 1000], default 1.0)

**Type:**

float

<a id="bpy.types.FluidDomainSettings.sndparticle_potential_min_trappedair"></a>

#### bpy.types.FluidDomainSettings.sndparticle_potential_min_trappedair

Lower clamping threshold for marking fluid cells where air is trapped (lower value results in more marked cells) (in [0, 1000], default 5.0)

**Type:**

float

<a id="bpy.types.FluidDomainSettings.sndparticle_potential_min_wavecrest"></a>

#### bpy.types.FluidDomainSettings.sndparticle_potential_min_wavecrest

Lower clamping threshold for marking fluid cells as wave crests (lower value results in more marked cells) (in [0, 1000], default 2.0)

**Type:**

float

<a id="bpy.types.FluidDomainSettings.sndparticle_potential_radius"></a>

#### bpy.types.FluidDomainSettings.sndparticle_potential_radius

Radius to compute potential for each cell (higher values are slower but create smoother potential grids) (in [1, 4], default 2)

**Type:**

int

<a id="bpy.types.FluidDomainSettings.sndparticle_sampling_trappedair"></a>

#### bpy.types.FluidDomainSettings.sndparticle_sampling_trappedair

Maximum number of particles generated per trapped air cell per frame (in [0, 10000], default 40)

**Type:**

int

<a id="bpy.types.FluidDomainSettings.sndparticle_sampling_wavecrest"></a>

#### bpy.types.FluidDomainSettings.sndparticle_sampling_wavecrest

Maximum number of particles generated per wave crest cell per frame (in [0, 10000], default 200)

**Type:**

int

<a id="bpy.types.FluidDomainSettings.sndparticle_update_radius"></a>

#### bpy.types.FluidDomainSettings.sndparticle_update_radius

Radius to compute position update for each particle (higher values are slower but particles move less chaotic) (in [1, 4], default 2)

**Type:**

int

<a id="bpy.types.FluidDomainSettings.start_point"></a>

#### bpy.types.FluidDomainSettings.start_point

Start point (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0), readonly)

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.FluidDomainSettings.surface_tension"></a>

#### bpy.types.FluidDomainSettings.surface_tension

Surface tension of liquid (higher value results in greater hydrophobic behavior) (in [0, 100], default 0.0)

**Type:**

float

<a id="bpy.types.FluidDomainSettings.sys_particle_maximum"></a>

#### bpy.types.FluidDomainSettings.sys_particle_maximum

Maximum number of fluid particles that are allowed in this simulation (in [0, inf], default 0)

**Type:**

int

<a id="bpy.types.FluidDomainSettings.temperature_grid"></a>

#### bpy.types.FluidDomainSettings.temperature_grid

Smoke temperature grid, range 0 to 1 represents 0 to 1000K (array of 32 items, in [-inf, inf], default (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0), readonly)

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.FluidDomainSettings.time_scale"></a>

#### bpy.types.FluidDomainSettings.time_scale

Adjust simulation speed (in [0.0001, 10], default 1.0)

**Type:**

float

<a id="bpy.types.FluidDomainSettings.timesteps_max"></a>

#### bpy.types.FluidDomainSettings.timesteps_max

Maximum number of simulation steps to perform for one frame (in [1, 100], default 4)

**Type:**

int

<a id="bpy.types.FluidDomainSettings.timesteps_min"></a>

#### bpy.types.FluidDomainSettings.timesteps_min

Minimum number of simulation steps to perform for one frame (in [1, 100], default 1)

**Type:**

int

<a id="bpy.types.FluidDomainSettings.use_adaptive_domain"></a>

#### bpy.types.FluidDomainSettings.use_adaptive_domain

Adapt simulation resolution and size to fluid (default False)

**Type:**

bool

<a id="bpy.types.FluidDomainSettings.use_adaptive_timesteps"></a>

#### bpy.types.FluidDomainSettings.use_adaptive_timesteps

Automatically decide when to perform multiple simulation steps per frame (default True)

**Type:**

bool

<a id="bpy.types.FluidDomainSettings.use_bubble_particles"></a>

#### bpy.types.FluidDomainSettings.use_bubble_particles

Create bubble particle system (default False)

**Type:**

bool

<a id="bpy.types.FluidDomainSettings.use_collision_border_back"></a>

#### bpy.types.FluidDomainSettings.use_collision_border_back

Enable collisions with back domain border (default False)

**Type:**

bool

<a id="bpy.types.FluidDomainSettings.use_collision_border_bottom"></a>

#### bpy.types.FluidDomainSettings.use_collision_border_bottom

Enable collisions with bottom domain border (default False)

**Type:**

bool

<a id="bpy.types.FluidDomainSettings.use_collision_border_front"></a>

#### bpy.types.FluidDomainSettings.use_collision_border_front

Enable collisions with front domain border (default False)

**Type:**

bool

<a id="bpy.types.FluidDomainSettings.use_collision_border_left"></a>

#### bpy.types.FluidDomainSettings.use_collision_border_left

Enable collisions with left domain border (default False)

**Type:**

bool

<a id="bpy.types.FluidDomainSettings.use_collision_border_right"></a>

#### bpy.types.FluidDomainSettings.use_collision_border_right

Enable collisions with right domain border (default False)

**Type:**

bool

<a id="bpy.types.FluidDomainSettings.use_collision_border_top"></a>

#### bpy.types.FluidDomainSettings.use_collision_border_top

Enable collisions with top domain border (default False)

**Type:**

bool

<a id="bpy.types.FluidDomainSettings.use_color_ramp"></a>

#### bpy.types.FluidDomainSettings.use_color_ramp

Render a simulation field while mapping its voxels values to the colors of a ramp or using a predefined color code (default False)

**Type:**

bool

<a id="bpy.types.FluidDomainSettings.use_diffusion"></a>

#### bpy.types.FluidDomainSettings.use_diffusion

Enable fluid diffusion settings (e.g. viscosity, surface tension) (default False)

**Type:**

bool

<a id="bpy.types.FluidDomainSettings.use_dissolve_smoke"></a>

#### bpy.types.FluidDomainSettings.use_dissolve_smoke

Let smoke disappear over time (default False)

**Type:**

bool

<a id="bpy.types.FluidDomainSettings.use_dissolve_smoke_log"></a>

#### bpy.types.FluidDomainSettings.use_dissolve_smoke_log

Dissolve smoke in a logarithmic fashion. Dissolves quickly at first, but lingers longer. (default True)

**Type:**

bool

<a id="bpy.types.FluidDomainSettings.use_flip_particles"></a>

#### bpy.types.FluidDomainSettings.use_flip_particles

Create liquid particle system (default False)

**Type:**

bool

<a id="bpy.types.FluidDomainSettings.use_foam_particles"></a>

#### bpy.types.FluidDomainSettings.use_foam_particles

Create foam particle system (default False)

**Type:**

bool

<a id="bpy.types.FluidDomainSettings.use_fractions"></a>

#### bpy.types.FluidDomainSettings.use_fractions

Fractional obstacles improve and smoothen the fluid-obstacle boundary (default False)

**Type:**

bool

<a id="bpy.types.FluidDomainSettings.use_guide"></a>

#### bpy.types.FluidDomainSettings.use_guide

Enable fluid guiding (default False)

**Type:**

bool

<a id="bpy.types.FluidDomainSettings.use_mesh"></a>

#### bpy.types.FluidDomainSettings.use_mesh

Enable fluid mesh (using amplification) (default True)

**Type:**

bool

<a id="bpy.types.FluidDomainSettings.use_noise"></a>

#### bpy.types.FluidDomainSettings.use_noise

Enable fluid noise (using amplification) (default False)

**Type:**

bool

<a id="bpy.types.FluidDomainSettings.use_slice"></a>

#### bpy.types.FluidDomainSettings.use_slice

Perform a single slice of the domain object (default False)

**Type:**

bool

<a id="bpy.types.FluidDomainSettings.use_speed_vectors"></a>

#### bpy.types.FluidDomainSettings.use_speed_vectors

Caches velocities of mesh vertices. These will be used (automatically) when rendering with motion blur enabled. (default False)

**Type:**

bool

<a id="bpy.types.FluidDomainSettings.use_spray_particles"></a>

#### bpy.types.FluidDomainSettings.use_spray_particles

Create spray particle system (default False)

**Type:**

bool

<a id="bpy.types.FluidDomainSettings.use_tracer_particles"></a>

#### bpy.types.FluidDomainSettings.use_tracer_particles

Create tracer particle system (default False)

**Type:**

bool

<a id="bpy.types.FluidDomainSettings.use_viscosity"></a>

#### bpy.types.FluidDomainSettings.use_viscosity

Simulate fluids with high viscosity using a special solver (default False)

**Type:**

bool

<a id="bpy.types.FluidDomainSettings.vector_display_type"></a>

#### bpy.types.FluidDomainSettings.vector_display_type

(default `'NEEDLE'`)

- `NEEDLE`
  Needle – Display vectors as needles.
- `STREAMLINE`
  Streamlines – Display vectors as streamlines.
- `MAC`
  MAC Grid – Display vector field as MAC grid.

**Type:**

Literal[‘NEEDLE’, ‘STREAMLINE’, ‘MAC’]

<a id="bpy.types.FluidDomainSettings.vector_field"></a>

#### bpy.types.FluidDomainSettings.vector_field

Vector field to be represented by the display vectors (default `'FLUID_VELOCITY'`)

- `FLUID_VELOCITY`
  Fluid Velocity – Velocity field of the fluid domain.
- `GUIDE_VELOCITY`
  Guide Velocity – Guide velocity field of the fluid domain.
- `FORCE`
  Force – Force field of the fluid domain.

**Type:**

Literal[‘FLUID_VELOCITY’, ‘GUIDE_VELOCITY’, ‘FORCE’]

<a id="bpy.types.FluidDomainSettings.vector_scale"></a>

#### bpy.types.FluidDomainSettings.vector_scale

Multiplier for scaling the vectors (in [0, 1000], default 1.0)

**Type:**

float

<a id="bpy.types.FluidDomainSettings.vector_scale_with_magnitude"></a>

#### bpy.types.FluidDomainSettings.vector_scale_with_magnitude

Scale vectors with their magnitudes (default False)

**Type:**

bool

<a id="bpy.types.FluidDomainSettings.vector_show_mac_x"></a>

#### bpy.types.FluidDomainSettings.vector_show_mac_x

Show X-component of MAC Grid (default True)

**Type:**

bool

<a id="bpy.types.FluidDomainSettings.vector_show_mac_y"></a>

#### bpy.types.FluidDomainSettings.vector_show_mac_y

Show Y-component of MAC Grid (default True)

**Type:**

bool

<a id="bpy.types.FluidDomainSettings.vector_show_mac_z"></a>

#### bpy.types.FluidDomainSettings.vector_show_mac_z

Show Z-component of MAC Grid (default True)

**Type:**

bool

<a id="bpy.types.FluidDomainSettings.velocity_grid"></a>

#### bpy.types.FluidDomainSettings.velocity_grid

Smoke velocity grid (array of 32 items, in [-inf, inf], default (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0), readonly)

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.FluidDomainSettings.velocity_scale"></a>

#### bpy.types.FluidDomainSettings.velocity_scale

Factor to control the amount of motion blur (in [0, inf], default 1.0)

**Type:**

float

<a id="bpy.types.FluidDomainSettings.viscosity_base"></a>

#### bpy.types.FluidDomainSettings.viscosity_base

Viscosity setting: value that is multiplied by 10 to the power of (exponent*-1) (in [0, 10], default 1.0)

**Type:**

float

<a id="bpy.types.FluidDomainSettings.viscosity_exponent"></a>

#### bpy.types.FluidDomainSettings.viscosity_exponent

Negative exponent for the viscosity value (to simplify entering small values e.g. 5*10^-6) (in [0, 10], default 6)

**Type:**

int

<a id="bpy.types.FluidDomainSettings.viscosity_value"></a>

#### bpy.types.FluidDomainSettings.viscosity_value

Viscosity of liquid (higher values result in more viscous fluids, a value of 0 will still apply some viscosity) (in [0, 10], default 0.05)

**Type:**

float

<a id="bpy.types.FluidDomainSettings.vorticity"></a>

#### bpy.types.FluidDomainSettings.vorticity

Amount of turbulence and rotation in smoke (in [0, 4], default 0.0)

**Type:**

float

<a id="bpy.types.FluidDomainSettings.bl_rna_get_subclass"></a>

#### classmethod bpy.types.FluidDomainSettings.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.FluidDomainSettings.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.FluidDomainSettings.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`FluidModifier.domain_settings`](bpy.types.FluidModifier.md#bpy.types.FluidModifier.domain_settings "bpy.types.FluidModifier.domain_settings") |  |
