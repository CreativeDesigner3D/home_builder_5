<!-- source: Blender Python API reference 5.2 / bpy.types.BoidSettings.html -->

<a id="boidsettings-bpy-struct"></a>

# BoidSettings(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.BoidSettings"></a>

### class bpy.types.BoidSettings(bpy_struct)

Settings for boid physics

<a id="bpy.types.BoidSettings.accuracy"></a>

#### bpy.types.BoidSettings.accuracy

Accuracy of attack (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.BoidSettings.active_boid_state"></a>

#### bpy.types.BoidSettings.active_boid_state

(readonly)

**Type:**

[`BoidRule`](bpy.types.BoidRule.md#bpy.types.BoidRule "bpy.types.BoidRule") | None

<a id="bpy.types.BoidSettings.active_boid_state_index"></a>

#### bpy.types.BoidSettings.active_boid_state_index

(in [0, inf], default 0)

**Type:**

int

<a id="bpy.types.BoidSettings.aggression"></a>

#### bpy.types.BoidSettings.aggression

Boid will fight this times stronger enemy (in [0, 100], default 0.0)

**Type:**

float

<a id="bpy.types.BoidSettings.air_acc_max"></a>

#### bpy.types.BoidSettings.air_acc_max

Maximum acceleration in air (relative to maximum speed) (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.BoidSettings.air_ave_max"></a>

#### bpy.types.BoidSettings.air_ave_max

Maximum angular velocity in air (relative to 180 degrees) (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.BoidSettings.air_personal_space"></a>

#### bpy.types.BoidSettings.air_personal_space

Radius of boids personal space in air (% of particle size) (in [0, 10], default 0.0)

**Type:**

float

<a id="bpy.types.BoidSettings.air_speed_max"></a>

#### bpy.types.BoidSettings.air_speed_max

Maximum speed in air (in [0, 100], default 0.0)

**Type:**

float

<a id="bpy.types.BoidSettings.air_speed_min"></a>

#### bpy.types.BoidSettings.air_speed_min

Minimum speed in air (relative to maximum speed) (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.BoidSettings.bank"></a>

#### bpy.types.BoidSettings.bank

Amount of rotation around velocity vector on turns (in [0, 2], default 0.0)

**Type:**

float

<a id="bpy.types.BoidSettings.health"></a>

#### bpy.types.BoidSettings.health

Initial boid health when born (in [0, 100], default 0.0)

**Type:**

float

<a id="bpy.types.BoidSettings.height"></a>

#### bpy.types.BoidSettings.height

Boid height relative to particle size (in [0, 2], default 0.0)

**Type:**

float

<a id="bpy.types.BoidSettings.land_acc_max"></a>

#### bpy.types.BoidSettings.land_acc_max

Maximum acceleration on land (relative to maximum speed) (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.BoidSettings.land_ave_max"></a>

#### bpy.types.BoidSettings.land_ave_max

Maximum angular velocity on land (relative to 180 degrees) (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.BoidSettings.land_jump_speed"></a>

#### bpy.types.BoidSettings.land_jump_speed

Maximum speed for jumping (in [0, 100], default 0.0)

**Type:**

float

<a id="bpy.types.BoidSettings.land_personal_space"></a>

#### bpy.types.BoidSettings.land_personal_space

Radius of boids personal space on land (% of particle size) (in [0, 10], default 0.0)

**Type:**

float

<a id="bpy.types.BoidSettings.land_smooth"></a>

#### bpy.types.BoidSettings.land_smooth

How smoothly the boids land (in [0, 10], default 0.0)

**Type:**

float

<a id="bpy.types.BoidSettings.land_speed_max"></a>

#### bpy.types.BoidSettings.land_speed_max

Maximum speed on land (in [0, 100], default 0.0)

**Type:**

float

<a id="bpy.types.BoidSettings.land_stick_force"></a>

#### bpy.types.BoidSettings.land_stick_force

How strong a force must be to start effecting a boid on land (in [0, 1000], default 0.0)

**Type:**

float

<a id="bpy.types.BoidSettings.pitch"></a>

#### bpy.types.BoidSettings.pitch

Amount of rotation around side vector (in [0, 2], default 0.0)

**Type:**

float

<a id="bpy.types.BoidSettings.range"></a>

#### bpy.types.BoidSettings.range

Maximum distance from which a boid can attack (in [0, 100], default 0.0)

**Type:**

float

<a id="bpy.types.BoidSettings.states"></a>

#### bpy.types.BoidSettings.states

(default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`BoidState`](bpy.types.BoidState.md#bpy.types.BoidState "bpy.types.BoidState")]

<a id="bpy.types.BoidSettings.strength"></a>

#### bpy.types.BoidSettings.strength

Maximum caused damage on attack per second (in [0, 100], default 0.0)

**Type:**

float

<a id="bpy.types.BoidSettings.use_climb"></a>

#### bpy.types.BoidSettings.use_climb

Allow boids to climb goal objects (default False)

**Type:**

bool

<a id="bpy.types.BoidSettings.use_flight"></a>

#### bpy.types.BoidSettings.use_flight

Allow boids to move in air (default False)

**Type:**

bool

<a id="bpy.types.BoidSettings.use_land"></a>

#### bpy.types.BoidSettings.use_land

Allow boids to move on land (default False)

**Type:**

bool

<a id="bpy.types.BoidSettings.bl_rna_get_subclass"></a>

#### classmethod bpy.types.BoidSettings.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.BoidSettings.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.BoidSettings.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`ParticleSettings.boids`](bpy.types.ParticleSettings.md#bpy.types.ParticleSettings.boids "bpy.types.ParticleSettings.boids") |  |
