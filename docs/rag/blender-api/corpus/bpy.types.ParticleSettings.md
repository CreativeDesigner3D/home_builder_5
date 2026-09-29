<!-- source: Blender Python API reference 5.2 / bpy.types.ParticleSettings.html -->

<a id="particlesettings-id"></a>

# ParticleSettings(ID)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")

<a id="bpy.types.ParticleSettings"></a>

### class bpy.types.ParticleSettings(ID)

Particle settings, reusable by multiple particle systems

<a id="bpy.types.ParticleSettings.active_instanceweight"></a>

#### bpy.types.ParticleSettings.active_instanceweight

(readonly)

**Type:**

[`ParticleDupliWeight`](bpy.types.ParticleDupliWeight.md#bpy.types.ParticleDupliWeight "bpy.types.ParticleDupliWeight") | None

<a id="bpy.types.ParticleSettings.active_instanceweight_index"></a>

#### bpy.types.ParticleSettings.active_instanceweight_index

(in [0, inf], default 0)

**Type:**

int

<a id="bpy.types.ParticleSettings.active_texture"></a>

#### bpy.types.ParticleSettings.active_texture

Active texture slot being displayed

**Type:**

[`Texture`](bpy.types.Texture.md#bpy.types.Texture "bpy.types.Texture") | None

<a id="bpy.types.ParticleSettings.active_texture_index"></a>

#### bpy.types.ParticleSettings.active_texture_index

Index of active texture slot (in [0, 17], default 0)

**Type:**

int

<a id="bpy.types.ParticleSettings.adaptive_angle"></a>

#### bpy.types.ParticleSettings.adaptive_angle

How many degrees path has to curve to make another render segment (in [0, 45], default 5)

**Type:**

int

<a id="bpy.types.ParticleSettings.adaptive_pixel"></a>

#### bpy.types.ParticleSettings.adaptive_pixel

How many pixels path has to cover to make another render segment (in [0, 50], default 3)

**Type:**

int

<a id="bpy.types.ParticleSettings.angular_velocity_factor"></a>

#### bpy.types.ParticleSettings.angular_velocity_factor

Angular velocity amount (in radians per second) (in [-200, 200], default 0.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.angular_velocity_mode"></a>

#### bpy.types.ParticleSettings.angular_velocity_mode

What axis is used to change particle rotation with time (default `'VELOCITY'`)

**Type:**

Literal[‘NONE’, ‘VELOCITY’, ‘HORIZONTAL’, ‘VERTICAL’, ‘GLOBAL_X’, ‘GLOBAL_Y’, ‘GLOBAL_Z’, ‘RAND’]

<a id="bpy.types.ParticleSettings.animation_data"></a>

#### bpy.types.ParticleSettings.animation_data

Animation data for this data-block (readonly)

**Type:**

[`AnimData`](bpy.types.AnimData.md#bpy.types.AnimData "bpy.types.AnimData") | None

<a id="bpy.types.ParticleSettings.apply_effector_to_children"></a>

#### bpy.types.ParticleSettings.apply_effector_to_children

Apply effectors to children (default False)

**Type:**

bool

<a id="bpy.types.ParticleSettings.apply_guide_to_children"></a>

#### bpy.types.ParticleSettings.apply_guide_to_children

(default False)

**Type:**

bool

<a id="bpy.types.ParticleSettings.bending_random"></a>

#### bpy.types.ParticleSettings.bending_random

Random stiffness of hairs (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.boids"></a>

#### bpy.types.ParticleSettings.boids

(readonly)

**Type:**

[`BoidSettings`](bpy.types.BoidSettings.md#bpy.types.BoidSettings "bpy.types.BoidSettings") | None

<a id="bpy.types.ParticleSettings.branch_threshold"></a>

#### bpy.types.ParticleSettings.branch_threshold

Threshold of branching (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.brownian_factor"></a>

#### bpy.types.ParticleSettings.brownian_factor

Amount of random, erratic particle movement (in [0, 200], default 0.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.child_length"></a>

#### bpy.types.ParticleSettings.child_length

Length of child paths (in [0, 1], default 1.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.child_length_threshold"></a>

#### bpy.types.ParticleSettings.child_length_threshold

Amount of particles left untouched by child path length (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.child_parting_factor"></a>

#### bpy.types.ParticleSettings.child_parting_factor

Create parting in the children based on parent strands (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.child_parting_max"></a>

#### bpy.types.ParticleSettings.child_parting_max

Maximum root to tip angle (tip distance/root distance for long hair) (in [0, 180], default 0.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.child_parting_min"></a>

#### bpy.types.ParticleSettings.child_parting_min

Minimum root to tip angle (tip distance/root distance for long hair) (in [0, 180], default 0.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.child_percent"></a>

#### bpy.types.ParticleSettings.child_percent

Number of children per parent (in [0, 100000], default 10)

**Type:**

int

<a id="bpy.types.ParticleSettings.child_radius"></a>

#### bpy.types.ParticleSettings.child_radius

Radius of children around parent (in [0, 100000], default 0.2)

**Type:**

float

<a id="bpy.types.ParticleSettings.child_roundness"></a>

#### bpy.types.ParticleSettings.child_roundness

Roundness of children around parent (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.child_size"></a>

#### bpy.types.ParticleSettings.child_size

A multiplier for the child particle size (in [0.001, 100000], default 1.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.child_size_random"></a>

#### bpy.types.ParticleSettings.child_size_random

Random variation to the size of the child particles (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.child_type"></a>

#### bpy.types.ParticleSettings.child_type

Create child particles (default `'NONE'`)

**Type:**

Literal[‘NONE’, ‘SIMPLE’, ‘INTERPOLATED’]

<a id="bpy.types.ParticleSettings.clump_curve"></a>

#### bpy.types.ParticleSettings.clump_curve

Curve defining clump tapering (readonly)

**Type:**

[`CurveMapping`](bpy.types.CurveMapping.md#bpy.types.CurveMapping "bpy.types.CurveMapping") | None

<a id="bpy.types.ParticleSettings.clump_factor"></a>

#### bpy.types.ParticleSettings.clump_factor

Amount of clumping (in [-1, 1], default 0.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.clump_noise_size"></a>

#### bpy.types.ParticleSettings.clump_noise_size

Size of clump noise (in [1e-05, 100000], default 1.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.clump_shape"></a>

#### bpy.types.ParticleSettings.clump_shape

Shape of clumping (in [-0.999, 0.999], default 0.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.collision_collection"></a>

#### bpy.types.ParticleSettings.collision_collection

Limit colliders to this collection

**Type:**

[`Collection`](bpy.types.Collection.md#bpy.types.Collection "bpy.types.Collection") | None

<a id="bpy.types.ParticleSettings.color_maximum"></a>

#### bpy.types.ParticleSettings.color_maximum

Maximum length of the particle color vector (in [0.01, 100], default 1.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.count"></a>

#### bpy.types.ParticleSettings.count

Total number of particles (in [0, inf], default 1000)

**Type:**

int

<a id="bpy.types.ParticleSettings.courant_target"></a>

#### bpy.types.ParticleSettings.courant_target

The relative distance a particle can move before requiring more subframes (target Courant number); 0.01 to 0.3 is the recommended range (in [0.0001, 10], default 0.2)

**Type:**

float

<a id="bpy.types.ParticleSettings.create_long_hair_children"></a>

#### bpy.types.ParticleSettings.create_long_hair_children

Calculate children that suit long hair well (default False)

**Type:**

bool

<a id="bpy.types.ParticleSettings.damping"></a>

#### bpy.types.ParticleSettings.damping

Amount of damping (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.display_color"></a>

#### bpy.types.ParticleSettings.display_color

Display additional particle data as a color (default `'MATERIAL'`)

**Type:**

Literal[‘NONE’, ‘MATERIAL’, ‘VELOCITY’, ‘ACCELERATION’]

<a id="bpy.types.ParticleSettings.display_method"></a>

#### bpy.types.ParticleSettings.display_method

How particles are displayed in viewport (default `'RENDER'`)

**Type:**

Literal[‘NONE’, ‘RENDER’, ‘DOT’, ‘CIRC’, ‘CROSS’, ‘AXIS’]

<a id="bpy.types.ParticleSettings.display_percentage"></a>

#### bpy.types.ParticleSettings.display_percentage

Percentage of particles to display in 3D view (in [0, 100], default 100)

**Type:**

int

<a id="bpy.types.ParticleSettings.display_size"></a>

#### bpy.types.ParticleSettings.display_size

Size of particles on viewport (in [0, 1000], default 0.1)

**Type:**

float

<a id="bpy.types.ParticleSettings.display_step"></a>

#### bpy.types.ParticleSettings.display_step

How many steps paths are displayed with (power of 2) (in [0, 10], default 2)

**Type:**

int

<a id="bpy.types.ParticleSettings.distribution"></a>

#### bpy.types.ParticleSettings.distribution

How to distribute particles on selected element (default `'JIT'`)

**Type:**

Literal[‘JIT’, ‘RAND’, ‘GRID’]

<a id="bpy.types.ParticleSettings.drag_factor"></a>

#### bpy.types.ParticleSettings.drag_factor

Amount of air drag (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.effect_hair"></a>

#### bpy.types.ParticleSettings.effect_hair

Hair stiffness for effectors (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.effector_amount"></a>

#### bpy.types.ParticleSettings.effector_amount

How many particles are effectors (0 is all particles) (in [0, 10000], default 0)

**Type:**

int

<a id="bpy.types.ParticleSettings.effector_weights"></a>

#### bpy.types.ParticleSettings.effector_weights

(readonly)

**Type:**

[`EffectorWeights`](bpy.types.EffectorWeights.md#bpy.types.EffectorWeights "bpy.types.EffectorWeights") | None

<a id="bpy.types.ParticleSettings.emit_from"></a>

#### bpy.types.ParticleSettings.emit_from

Where to emit particles from (default `'FACE'`)

**Type:**

Literal[‘VERT’, ‘FACE’, ‘VOLUME’]

<a id="bpy.types.ParticleSettings.factor_random"></a>

#### bpy.types.ParticleSettings.factor_random

Give the starting velocity a random variation (in [0, 200], default 0.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.fluid"></a>

#### bpy.types.ParticleSettings.fluid

(readonly)

**Type:**

[`SPHFluidSettings`](bpy.types.SPHFluidSettings.md#bpy.types.SPHFluidSettings "bpy.types.SPHFluidSettings") | None

<a id="bpy.types.ParticleSettings.force_field_1"></a>

#### bpy.types.ParticleSettings.force_field_1

(readonly)

**Type:**

[`FieldSettings`](bpy.types.FieldSettings.md#bpy.types.FieldSettings "bpy.types.FieldSettings") | None

<a id="bpy.types.ParticleSettings.force_field_2"></a>

#### bpy.types.ParticleSettings.force_field_2

(readonly)

**Type:**

[`FieldSettings`](bpy.types.FieldSettings.md#bpy.types.FieldSettings "bpy.types.FieldSettings") | None

<a id="bpy.types.ParticleSettings.frame_end"></a>

#### bpy.types.ParticleSettings.frame_end

Frame number to stop emitting particles (in [-1.04857e+06, 1.04857e+06], default 200.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.frame_start"></a>

#### bpy.types.ParticleSettings.frame_start

Frame number to start emitting particles (in [-1.04857e+06, 1.04857e+06], default 1.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.grid_random"></a>

#### bpy.types.ParticleSettings.grid_random

Add random offset to the grid locations (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.grid_resolution"></a>

#### bpy.types.ParticleSettings.grid_resolution

The resolution of the particle grid (in [1, 250], default 10)

**Type:**

int

<a id="bpy.types.ParticleSettings.hair_length"></a>

#### bpy.types.ParticleSettings.hair_length

Length of the hair (in [0, 1000], default 0.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.hair_step"></a>

#### bpy.types.ParticleSettings.hair_step

Number of hair segments (in [2, 32767], default 5)

**Type:**

int

<a id="bpy.types.ParticleSettings.hexagonal_grid"></a>

#### bpy.types.ParticleSettings.hexagonal_grid

Create the grid in a hexagonal pattern (default False)

**Type:**

bool

<a id="bpy.types.ParticleSettings.instance_collection"></a>

#### bpy.types.ParticleSettings.instance_collection

Show objects in this collection in place of particles

**Type:**

[`Collection`](bpy.types.Collection.md#bpy.types.Collection "bpy.types.Collection") | None

<a id="bpy.types.ParticleSettings.instance_object"></a>

#### bpy.types.ParticleSettings.instance_object

Show this object in place of particles

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.ParticleSettings.instance_weights"></a>

#### bpy.types.ParticleSettings.instance_weights

Weights for all of the objects in the instance collection (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`ParticleDupliWeight`](bpy.types.ParticleDupliWeight.md#bpy.types.ParticleDupliWeight "bpy.types.ParticleDupliWeight")]

<a id="bpy.types.ParticleSettings.integrator"></a>

#### bpy.types.ParticleSettings.integrator

Algorithm used to calculate physics, from the fastest to the most stable and accurate: Midpoint, Euler, Verlet, RK4 (default `'MIDPOINT'`)

**Type:**

Literal[‘EULER’, ‘VERLET’, ‘MIDPOINT’, ‘RK4’]

<a id="bpy.types.ParticleSettings.invert_grid"></a>

#### bpy.types.ParticleSettings.invert_grid

Invert what is considered object and what is not (default False)

**Type:**

bool

<a id="bpy.types.ParticleSettings.is_fluid"></a>

#### bpy.types.ParticleSettings.is_fluid

Particles were created by a fluid simulation (default False, readonly)

**Type:**

bool

<a id="bpy.types.ParticleSettings.jitter_factor"></a>

#### bpy.types.ParticleSettings.jitter_factor

Amount of jitter applied to the sampling (in [0, 2], default 1.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.keyed_loops"></a>

#### bpy.types.ParticleSettings.keyed_loops

Number of times the keys are looped (in [1, 10000], default 1)

**Type:**

int

<a id="bpy.types.ParticleSettings.keys_step"></a>

#### bpy.types.ParticleSettings.keys_step

(in [0, 32767], default 5)

**Type:**

int

<a id="bpy.types.ParticleSettings.kink"></a>

#### bpy.types.ParticleSettings.kink

Type of periodic offset on the path (default `'NO'`)

**Type:**

Literal[‘NO’, ‘CURL’, ‘RADIAL’, ‘WAVE’, ‘BRAID’, ‘SPIRAL’]

<a id="bpy.types.ParticleSettings.kink_amplitude"></a>

#### bpy.types.ParticleSettings.kink_amplitude

The amplitude of the offset (in [-100000, 100000], default 0.2)

**Type:**

float

<a id="bpy.types.ParticleSettings.kink_amplitude_clump"></a>

#### bpy.types.ParticleSettings.kink_amplitude_clump

How much clump affects kink amplitude (in [0, 1], default 1.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.kink_amplitude_random"></a>

#### bpy.types.ParticleSettings.kink_amplitude_random

Random variation of the amplitude (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.kink_axis"></a>

#### bpy.types.ParticleSettings.kink_axis

Which axis to use for offset (default `'Z'`)

**Type:**

Literal[[Axis Xyz Items](bpy_types_enum_items/axis_xyz_items.md#rna-enum-axis-xyz-items)]

<a id="bpy.types.ParticleSettings.kink_axis_random"></a>

#### bpy.types.ParticleSettings.kink_axis_random

Random variation of the orientation (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.kink_extra_steps"></a>

#### bpy.types.ParticleSettings.kink_extra_steps

Extra steps for resolution of special kink features (in [1, inf], default 4)

**Type:**

int

<a id="bpy.types.ParticleSettings.kink_flat"></a>

#### bpy.types.ParticleSettings.kink_flat

How flat the hairs are (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.kink_frequency"></a>

#### bpy.types.ParticleSettings.kink_frequency

The frequency of the offset (1/total length) (in [-100000, 100000], default 2.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.kink_shape"></a>

#### bpy.types.ParticleSettings.kink_shape

Adjust the offset to the beginning/end (in [-0.999, 0.999], default 0.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.length_random"></a>

#### bpy.types.ParticleSettings.length_random

Give path length a random variation (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.lifetime"></a>

#### bpy.types.ParticleSettings.lifetime

Life span of the particles (in [1, 1.04857e+06], default 50.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.lifetime_random"></a>

#### bpy.types.ParticleSettings.lifetime_random

Give the particle life a random variation (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.line_length_head"></a>

#### bpy.types.ParticleSettings.line_length_head

Length of the line’s head (in [0, 100000], default 0.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.line_length_tail"></a>

#### bpy.types.ParticleSettings.line_length_tail

Length of the line’s tail (in [0, 100000], default 0.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.lock_boids_to_surface"></a>

#### bpy.types.ParticleSettings.lock_boids_to_surface

Constrain boids to a surface (default False)

**Type:**

bool

<a id="bpy.types.ParticleSettings.mass"></a>

#### bpy.types.ParticleSettings.mass

Mass of the particles (in [1e-08, 100000], default 1.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.material"></a>

#### bpy.types.ParticleSettings.material

Index of material slot used for rendering particles (in [1, 32767], default 1)

**Type:**

int

<a id="bpy.types.ParticleSettings.material_slot"></a>

#### bpy.types.ParticleSettings.material_slot

Material slot used for rendering particles (default `'DEFAULT'`)

**Type:**

Literal[‘DEFAULT’]

<a id="bpy.types.ParticleSettings.normal_factor"></a>

#### bpy.types.ParticleSettings.normal_factor

Let the surface normal give the particle a starting velocity (in [-1000, 1000], default 1.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.object_align_factor"></a>

#### bpy.types.ParticleSettings.object_align_factor

Let the emitter object orientation give the particle a starting velocity (array of 3 items, in [-200, 200], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.ParticleSettings.object_factor"></a>

#### bpy.types.ParticleSettings.object_factor

Let the object give the particle a starting velocity (in [-200, 200], default 0.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.particle_factor"></a>

#### bpy.types.ParticleSettings.particle_factor

Let the target particle give the particle a starting velocity (in [-200, 200], default 0.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.particle_size"></a>

#### bpy.types.ParticleSettings.particle_size

The size of the particles (in [0.001, 100000], default 0.05)

**Type:**

float

<a id="bpy.types.ParticleSettings.path_end"></a>

#### bpy.types.ParticleSettings.path_end

End time of path (in [-inf, inf], default 1.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.path_start"></a>

#### bpy.types.ParticleSettings.path_start

Starting time of path (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.phase_factor"></a>

#### bpy.types.ParticleSettings.phase_factor

Rotation around the chosen orientation axis (in [-1, 1], default 0.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.phase_factor_random"></a>

#### bpy.types.ParticleSettings.phase_factor_random

Randomize rotation around the chosen orientation axis (in [0, 2], default 0.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.physics_type"></a>

#### bpy.types.ParticleSettings.physics_type

Particle physics type (default `'NEWTON'`)

**Type:**

Literal[‘NO’, ‘NEWTON’, ‘KEYED’, ‘BOIDS’, ‘FLUID’]

<a id="bpy.types.ParticleSettings.radius_scale"></a>

#### bpy.types.ParticleSettings.radius_scale

Multiplier of diameter properties (in [0, inf], default 0.01)

**Type:**

float

<a id="bpy.types.ParticleSettings.react_event"></a>

#### bpy.types.ParticleSettings.react_event

The event of target particles to react on (default `'DEATH'`)

**Type:**

Literal[‘DEATH’, ‘COLLIDE’, ‘NEAR’]

<a id="bpy.types.ParticleSettings.reactor_factor"></a>

#### bpy.types.ParticleSettings.reactor_factor

Let the vector away from the target particle’s location give the particle a starting velocity (in [-10, 10], default 0.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.render_step"></a>

#### bpy.types.ParticleSettings.render_step

How many steps paths are rendered with (power of 2) (in [0, 20], default 3)

**Type:**

int

<a id="bpy.types.ParticleSettings.render_type"></a>

#### bpy.types.ParticleSettings.render_type

How particles are rendered (default `'HALO'`)

**Type:**

Literal[‘NONE’, ‘HALO’, ‘LINE’, ‘PATH’, ‘OBJECT’, ‘COLLECTION’]

<a id="bpy.types.ParticleSettings.rendered_child_count"></a>

#### bpy.types.ParticleSettings.rendered_child_count

Number of children per parent for rendering (in [0, 100000], default 100)

**Type:**

int

<a id="bpy.types.ParticleSettings.root_radius"></a>

#### bpy.types.ParticleSettings.root_radius

Strand diameter width at the root (in [0, inf], default 1.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.rotation_factor_random"></a>

#### bpy.types.ParticleSettings.rotation_factor_random

Randomize particle orientation (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.rotation_mode"></a>

#### bpy.types.ParticleSettings.rotation_mode

Particle orientation axis (does not affect Explode modifier’s results) (default `'VEL'`)

**Type:**

Literal[‘NONE’, ‘NOR’, ‘NOR_TAN’, ‘VEL’, ‘GLOB_X’, ‘GLOB_Y’, ‘GLOB_Z’, ‘OB_X’, ‘OB_Y’, ‘OB_Z’]

<a id="bpy.types.ParticleSettings.roughness_1"></a>

#### bpy.types.ParticleSettings.roughness_1

Amount of location dependent roughness (in [0, 100000], default 0.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.roughness_1_size"></a>

#### bpy.types.ParticleSettings.roughness_1_size

Size of location dependent roughness (in [0.01, 100000], default 1.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.roughness_2"></a>

#### bpy.types.ParticleSettings.roughness_2

Amount of random roughness (in [0, 100000], default 0.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.roughness_2_size"></a>

#### bpy.types.ParticleSettings.roughness_2_size

Size of random roughness (in [0.01, 100000], default 1.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.roughness_2_threshold"></a>

#### bpy.types.ParticleSettings.roughness_2_threshold

Amount of particles left untouched by random roughness (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.roughness_curve"></a>

#### bpy.types.ParticleSettings.roughness_curve

Curve defining roughness (readonly)

**Type:**

[`CurveMapping`](bpy.types.CurveMapping.md#bpy.types.CurveMapping "bpy.types.CurveMapping") | None

<a id="bpy.types.ParticleSettings.roughness_end_shape"></a>

#### bpy.types.ParticleSettings.roughness_end_shape

Shape of endpoint roughness (in [0, 10], default 1.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.roughness_endpoint"></a>

#### bpy.types.ParticleSettings.roughness_endpoint

Amount of endpoint roughness (in [0, 100000], default 0.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.shape"></a>

#### bpy.types.ParticleSettings.shape

Strand shape parameter (in [-1, 1], default 0.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.show_guide_hairs"></a>

#### bpy.types.ParticleSettings.show_guide_hairs

Show guide hairs (default False)

**Type:**

bool

<a id="bpy.types.ParticleSettings.show_hair_grid"></a>

#### bpy.types.ParticleSettings.show_hair_grid

Show hair simulation grid (default False)

**Type:**

bool

<a id="bpy.types.ParticleSettings.show_health"></a>

#### bpy.types.ParticleSettings.show_health

Display boid health (default False)

**Type:**

bool

<a id="bpy.types.ParticleSettings.show_number"></a>

#### bpy.types.ParticleSettings.show_number

Show particle number (default False)

**Type:**

bool

<a id="bpy.types.ParticleSettings.show_size"></a>

#### bpy.types.ParticleSettings.show_size

Show particle size (default False)

**Type:**

bool

<a id="bpy.types.ParticleSettings.show_unborn"></a>

#### bpy.types.ParticleSettings.show_unborn

Show particles before they are emitted (default False)

**Type:**

bool

<a id="bpy.types.ParticleSettings.show_velocity"></a>

#### bpy.types.ParticleSettings.show_velocity

Show particle velocity (default False)

**Type:**

bool

<a id="bpy.types.ParticleSettings.size_random"></a>

#### bpy.types.ParticleSettings.size_random

Give the particle size a random variation (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.subframes"></a>

#### bpy.types.ParticleSettings.subframes

Subframes to simulate for improved stability and finer granularity simulations (dt = timestep / (subframes + 1)) (in [0, 1000], default 0)

**Type:**

int

<a id="bpy.types.ParticleSettings.tangent_factor"></a>

#### bpy.types.ParticleSettings.tangent_factor

Let the surface tangent give the particle a starting velocity (in [-1000, 1000], default 0.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.tangent_phase"></a>

#### bpy.types.ParticleSettings.tangent_phase

Rotate the surface tangent (in [-1, 1], default 0.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.texture_slots"></a>

#### bpy.types.ParticleSettings.texture_slots

Texture slots defining the mapping and influence of textures (default None, readonly)

**Type:**

[`ParticleSettingsTextureSlots`](bpy.types.ParticleSettingsTextureSlots.md#bpy.types.ParticleSettingsTextureSlots "bpy.types.ParticleSettingsTextureSlots")[[`ParticleSettingsTextureSlot`](bpy.types.ParticleSettingsTextureSlot.md#bpy.types.ParticleSettingsTextureSlot "bpy.types.ParticleSettingsTextureSlot")]

<a id="bpy.types.ParticleSettings.time_tweak"></a>

#### bpy.types.ParticleSettings.time_tweak

A multiplier for physics timestep (1.0 means one frame = 1/25 seconds) (in [0, 100], default 1.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.timestep"></a>

#### bpy.types.ParticleSettings.timestep

The simulation timestep per frame (seconds per frame) (in [0.0001, 100], default 0.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.tip_radius"></a>

#### bpy.types.ParticleSettings.tip_radius

Strand diameter width at the tip (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.trail_count"></a>

#### bpy.types.ParticleSettings.trail_count

Number of trail particles (in [1, 100000], default 0)

**Type:**

int

<a id="bpy.types.ParticleSettings.twist"></a>

#### bpy.types.ParticleSettings.twist

Number of turns around parent along the strand (in [-100000, 100000], default 0.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.twist_curve"></a>

#### bpy.types.ParticleSettings.twist_curve

Curve defining twist (readonly)

**Type:**

[`CurveMapping`](bpy.types.CurveMapping.md#bpy.types.CurveMapping "bpy.types.CurveMapping") | None

<a id="bpy.types.ParticleSettings.type"></a>

#### bpy.types.ParticleSettings.type

Particle type (default `'EMITTER'`)

**Type:**

Literal[‘EMITTER’, ‘HAIR’]

<a id="bpy.types.ParticleSettings.use_absolute_path_time"></a>

#### bpy.types.ParticleSettings.use_absolute_path_time

Path timing is in absolute frames (default False)

**Type:**

bool

<a id="bpy.types.ParticleSettings.use_adaptive_subframes"></a>

#### bpy.types.ParticleSettings.use_adaptive_subframes

Automatically set the number of subframes (default False)

**Type:**

bool

<a id="bpy.types.ParticleSettings.use_advanced_hair"></a>

#### bpy.types.ParticleSettings.use_advanced_hair

Use full physics calculations for growing hair (default False)

**Type:**

bool

<a id="bpy.types.ParticleSettings.use_close_tip"></a>

#### bpy.types.ParticleSettings.use_close_tip

Set tip radius to zero (default True)

**Type:**

bool

<a id="bpy.types.ParticleSettings.use_clump_curve"></a>

#### bpy.types.ParticleSettings.use_clump_curve

Use a curve to define clump tapering (default False)

**Type:**

bool

<a id="bpy.types.ParticleSettings.use_clump_noise"></a>

#### bpy.types.ParticleSettings.use_clump_noise

Create random clumps around the parent (default False)

**Type:**

bool

<a id="bpy.types.ParticleSettings.use_collection_count"></a>

#### bpy.types.ParticleSettings.use_collection_count

Use object multiple times in the same collection (default False)

**Type:**

bool

<a id="bpy.types.ParticleSettings.use_collection_pick_random"></a>

#### bpy.types.ParticleSettings.use_collection_pick_random

Pick objects from collection randomly (default False)

**Type:**

bool

<a id="bpy.types.ParticleSettings.use_dead"></a>

#### bpy.types.ParticleSettings.use_dead

Show particles after they have died (default False)

**Type:**

bool

<a id="bpy.types.ParticleSettings.use_die_on_collision"></a>

#### bpy.types.ParticleSettings.use_die_on_collision

Particles die when they collide with a deflector object (default False)

**Type:**

bool

<a id="bpy.types.ParticleSettings.use_dynamic_rotation"></a>

#### bpy.types.ParticleSettings.use_dynamic_rotation

Particle rotations are affected by collisions and effectors (default False)

**Type:**

bool

<a id="bpy.types.ParticleSettings.use_emit_random"></a>

#### bpy.types.ParticleSettings.use_emit_random

Emit in random order of elements (default True)

**Type:**

bool

<a id="bpy.types.ParticleSettings.use_even_distribution"></a>

#### bpy.types.ParticleSettings.use_even_distribution

Use even distribution from faces based on face areas or edge lengths (default True)

**Type:**

bool

<a id="bpy.types.ParticleSettings.use_global_instance"></a>

#### bpy.types.ParticleSettings.use_global_instance

Use object’s global coordinates for duplication (default False)

**Type:**

bool

<a id="bpy.types.ParticleSettings.use_hair_bspline"></a>

#### bpy.types.ParticleSettings.use_hair_bspline

Interpolate hair using B-Splines (default False)

**Type:**

bool

<a id="bpy.types.ParticleSettings.use_modifier_stack"></a>

#### bpy.types.ParticleSettings.use_modifier_stack

Emit particles from mesh with modifiers applied (must use same subdivision surface level for viewport and render for correct results) (default False)

**Type:**

bool

<a id="bpy.types.ParticleSettings.use_multiply_size_mass"></a>

#### bpy.types.ParticleSettings.use_multiply_size_mass

Multiply mass by particle size (default False)

**Type:**

bool

<a id="bpy.types.ParticleSettings.use_parent_particles"></a>

#### bpy.types.ParticleSettings.use_parent_particles

Render parent particles (default False)

**Type:**

bool

<a id="bpy.types.ParticleSettings.use_react_multiple"></a>

#### bpy.types.ParticleSettings.use_react_multiple

React multiple times (default False)

**Type:**

bool

<a id="bpy.types.ParticleSettings.use_react_start_end"></a>

#### bpy.types.ParticleSettings.use_react_start_end

Give birth to unreacted particles eventually (default False)

**Type:**

bool

<a id="bpy.types.ParticleSettings.use_regrow_hair"></a>

#### bpy.types.ParticleSettings.use_regrow_hair

Regrow hair for each frame (default False)

**Type:**

bool

<a id="bpy.types.ParticleSettings.use_render_adaptive"></a>

#### bpy.types.ParticleSettings.use_render_adaptive

Display steps of the particle path (default False)

**Type:**

bool

<a id="bpy.types.ParticleSettings.use_rotation_instance"></a>

#### bpy.types.ParticleSettings.use_rotation_instance

Use object’s rotation for duplication (global x-axis is aligned particle rotation axis) (default False)

**Type:**

bool

<a id="bpy.types.ParticleSettings.use_rotations"></a>

#### bpy.types.ParticleSettings.use_rotations

Calculate particle rotations (default False)

**Type:**

bool

<a id="bpy.types.ParticleSettings.use_roughness_curve"></a>

#### bpy.types.ParticleSettings.use_roughness_curve

Use a curve to define roughness (default False)

**Type:**

bool

<a id="bpy.types.ParticleSettings.use_scale_instance"></a>

#### bpy.types.ParticleSettings.use_scale_instance

Use object’s scale for duplication (default True)

**Type:**

bool

<a id="bpy.types.ParticleSettings.use_self_effect"></a>

#### bpy.types.ParticleSettings.use_self_effect

Particle effectors affect themselves (default False)

**Type:**

bool

<a id="bpy.types.ParticleSettings.use_size_deflect"></a>

#### bpy.types.ParticleSettings.use_size_deflect

Use particle’s size in deflection (default False)

**Type:**

bool

<a id="bpy.types.ParticleSettings.use_strand_primitive"></a>

#### bpy.types.ParticleSettings.use_strand_primitive

Use the strand primitive for rendering (default False)

**Type:**

bool

<a id="bpy.types.ParticleSettings.use_twist_curve"></a>

#### bpy.types.ParticleSettings.use_twist_curve

Use a curve to define twist (default False)

**Type:**

bool

<a id="bpy.types.ParticleSettings.use_velocity_length"></a>

#### bpy.types.ParticleSettings.use_velocity_length

Multiply line length by particle speed (default False)

**Type:**

bool

<a id="bpy.types.ParticleSettings.use_whole_collection"></a>

#### bpy.types.ParticleSettings.use_whole_collection

Use whole collection at once (default False)

**Type:**

bool

<a id="bpy.types.ParticleSettings.userjit"></a>

#### bpy.types.ParticleSettings.userjit

Emission locations per face (0 = automatic) (in [0, 1000], default 0)

**Type:**

int

<a id="bpy.types.ParticleSettings.virtual_parents"></a>

#### bpy.types.ParticleSettings.virtual_parents

Relative amount of virtual parents (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.ParticleSettings.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ParticleSettings.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ParticleSettings.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ParticleSettings.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([type](#bpy.types.ParticleSettings.type "bpy.types.ParticleSettings.type") | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

[type](#bpy.types.ParticleSettings.type "bpy.types.ParticleSettings.type")

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, ID.name, ID.name_full, ID.id_type, ID.session_uid, ID.is_evaluated, ID.original, ID.users, ID.use_fake_user, ID.use_extra_user, ID.is_embedded_data, ID.is_linked_packed, ID.is_missing, ID.is_runtime_data, ID.is_editable, ID.tag, ID.is_library_indirect, ID.library, ID.library_weak_reference, ID.asset_data, ID.override_library, ID.preview

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, ID.bl_system_properties_get, ID.rename, ID.evaluated_get, ID.copy, ID.asset_mark, ID.asset_clear, ID.asset_generate_preview, ID.override_create, ID.override_hierarchy_create, ID.user_clear, ID.user_remap, ID.make_local, ID.user_of_id, ID.animation_data_create, ID.animation_data_clear, ID.update_tag, ID.preview_ensure, ID.bl_rna_get_subclass, ID.bl_rna_get_subclass_py

<a id="references"></a>

## References

|  |  |
| --- | --- |
| - `bpy.context.particle_settings` - [`BlendData.particles`](bpy.types.BlendData.md#bpy.types.BlendData.particles "bpy.types.BlendData.particles") - [`BlendDataParticles.new`](bpy.types.BlendDataParticles.md#bpy.types.BlendDataParticles.new "bpy.types.BlendDataParticles.new") | - [`BlendDataParticles.remove`](bpy.types.BlendDataParticles.md#bpy.types.BlendDataParticles.remove "bpy.types.BlendDataParticles.remove") - [`ParticleSystem.settings`](bpy.types.ParticleSystem.md#bpy.types.ParticleSystem.settings "bpy.types.ParticleSystem.settings") |
