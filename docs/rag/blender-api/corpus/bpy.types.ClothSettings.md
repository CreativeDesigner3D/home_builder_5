<!-- source: Blender Python API reference 5.2 / bpy.types.ClothSettings.html -->

<a id="clothsettings-bpy-struct"></a>

# ClothSettings(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.ClothSettings"></a>

### class bpy.types.ClothSettings(bpy_struct)

Cloth simulation settings for an object

<a id="bpy.types.ClothSettings.air_damping"></a>

#### bpy.types.ClothSettings.air_damping

Air has normally some thickness which slows falling things down (in [0, 10], default 1.0)

**Type:**

float

<a id="bpy.types.ClothSettings.bending_damping"></a>

#### bpy.types.ClothSettings.bending_damping

Amount of damping in bending behavior (in [0, 1000], default 0.5)

**Type:**

float

<a id="bpy.types.ClothSettings.bending_model"></a>

#### bpy.types.ClothSettings.bending_model

Physical model for simulating bending forces (default `'ANGULAR'`)

- `ANGULAR`
  Angular – Cloth model with angular bending springs.
- `LINEAR`
  Linear – Cloth model with linear bending springs (legacy).

**Type:**

Literal[‘ANGULAR’, ‘LINEAR’]

<a id="bpy.types.ClothSettings.bending_stiffness"></a>

#### bpy.types.ClothSettings.bending_stiffness

How much the material resists bending (in [0, 10000], default 0.5)

**Type:**

float

<a id="bpy.types.ClothSettings.bending_stiffness_max"></a>

#### bpy.types.ClothSettings.bending_stiffness_max

Maximum bending stiffness value (in [0, 10000], default 0.5)

**Type:**

float

<a id="bpy.types.ClothSettings.collider_friction"></a>

#### bpy.types.ClothSettings.collider_friction

(in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.ClothSettings.compression_damping"></a>

#### bpy.types.ClothSettings.compression_damping

Amount of damping in compression behavior (in [0, 50], default 5.0)

**Type:**

float

<a id="bpy.types.ClothSettings.compression_stiffness"></a>

#### bpy.types.ClothSettings.compression_stiffness

How much the material resists compression (in [0, 10000], default 15.0)

**Type:**

float

<a id="bpy.types.ClothSettings.compression_stiffness_max"></a>

#### bpy.types.ClothSettings.compression_stiffness_max

Maximum compression stiffness value (in [0, 10000], default 15.0)

**Type:**

float

<a id="bpy.types.ClothSettings.density_strength"></a>

#### bpy.types.ClothSettings.density_strength

Influence of target density on the simulation (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.ClothSettings.density_target"></a>

#### bpy.types.ClothSettings.density_target

Maximum density of hair (in [0, 10000], default 0.0)

**Type:**

float

<a id="bpy.types.ClothSettings.effector_weights"></a>

#### bpy.types.ClothSettings.effector_weights

(readonly)

**Type:**

[`EffectorWeights`](bpy.types.EffectorWeights.md#bpy.types.EffectorWeights "bpy.types.EffectorWeights") | None

<a id="bpy.types.ClothSettings.fluid_density"></a>

#### bpy.types.ClothSettings.fluid_density

Density (kg/l) of the fluid contained inside the object, used to create a hydrostatic pressure gradient simulating the weight of the internal fluid, or buoyancy from the surrounding fluid if negative (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.ClothSettings.goal_default"></a>

#### bpy.types.ClothSettings.goal_default

Default Goal (vertex target position) value, when no Vertex Group used (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.ClothSettings.goal_friction"></a>

#### bpy.types.ClothSettings.goal_friction

Goal (vertex target position) friction (in [0, 50], default 0.0)

**Type:**

float

<a id="bpy.types.ClothSettings.goal_max"></a>

#### bpy.types.ClothSettings.goal_max

Goal maximum, vertex group weights are scaled to match this range (in [0, 1], default 1.0)

**Type:**

float

<a id="bpy.types.ClothSettings.goal_min"></a>

#### bpy.types.ClothSettings.goal_min

Goal minimum, vertex group weights are scaled to match this range (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.ClothSettings.goal_spring"></a>

#### bpy.types.ClothSettings.goal_spring

Goal (vertex target position) spring stiffness (in [0, 0.999], default 1.0)

**Type:**

float

<a id="bpy.types.ClothSettings.gravity"></a>

#### bpy.types.ClothSettings.gravity

Gravity or external force vector (array of 3 items, in [-100, 100], default (0.0, 0.0, -9.81))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.ClothSettings.internal_compression_stiffness"></a>

#### bpy.types.ClothSettings.internal_compression_stiffness

How much the material resists compression (in [0, 10000], default 15.0)

**Type:**

float

<a id="bpy.types.ClothSettings.internal_compression_stiffness_max"></a>

#### bpy.types.ClothSettings.internal_compression_stiffness_max

Maximum compression stiffness value (in [0, 10000], default 15.0)

**Type:**

float

<a id="bpy.types.ClothSettings.internal_friction"></a>

#### bpy.types.ClothSettings.internal_friction

(in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.ClothSettings.internal_spring_max_diversion"></a>

#### bpy.types.ClothSettings.internal_spring_max_diversion

How much the rays used to connect the internal points can diverge from the vertex normal (in [0, 0.785398], default 0.785398)

**Type:**

float

<a id="bpy.types.ClothSettings.internal_spring_max_length"></a>

#### bpy.types.ClothSettings.internal_spring_max_length

The maximum length an internal spring can have during creation. If the distance between internal points is greater than this, no internal spring will be created between these points. A length of zero means that there is no length limit. (in [0, 1000], default 0.0)

**Type:**

float

<a id="bpy.types.ClothSettings.internal_spring_normal_check"></a>

#### bpy.types.ClothSettings.internal_spring_normal_check

Require the points the internal springs connect to have opposite normal directions (default True)

**Type:**

bool

<a id="bpy.types.ClothSettings.internal_tension_stiffness"></a>

#### bpy.types.ClothSettings.internal_tension_stiffness

How much the material resists stretching (in [0, 10000], default 15.0)

**Type:**

float

<a id="bpy.types.ClothSettings.internal_tension_stiffness_max"></a>

#### bpy.types.ClothSettings.internal_tension_stiffness_max

Maximum tension stiffness value (in [0, 10000], default 15.0)

**Type:**

float

<a id="bpy.types.ClothSettings.mass"></a>

#### bpy.types.ClothSettings.mass

The mass of each vertex on the cloth material (in [0, inf], default 0.3)

**Type:**

float

<a id="bpy.types.ClothSettings.pin_stiffness"></a>

#### bpy.types.ClothSettings.pin_stiffness

Pin (vertex target position) spring stiffness (in [0, 50], default 1.0)

**Type:**

float

<a id="bpy.types.ClothSettings.pressure_factor"></a>

#### bpy.types.ClothSettings.pressure_factor

Ambient pressure (kPa) that balances out between the inside and outside of the object when it has the target volume (in [0, 10000], default 1.0)

**Type:**

float

<a id="bpy.types.ClothSettings.quality"></a>

#### bpy.types.ClothSettings.quality

Quality of the simulation in steps per frame (higher is better quality but slower) (in [1, inf], default 5)

**Type:**

int

<a id="bpy.types.ClothSettings.rest_shape_key"></a>

#### bpy.types.ClothSettings.rest_shape_key

Shape key to use the rest spring lengths from

**Type:**

[`ShapeKey`](bpy.types.ShapeKey.md#bpy.types.ShapeKey "bpy.types.ShapeKey") | None

<a id="bpy.types.ClothSettings.sewing_force_max"></a>

#### bpy.types.ClothSettings.sewing_force_max

Maximum sewing force (in [0, 10000], default 0.0)

**Type:**

float

<a id="bpy.types.ClothSettings.shear_damping"></a>

#### bpy.types.ClothSettings.shear_damping

Amount of damping in shearing behavior (in [0, 50], default 5.0)

**Type:**

float

<a id="bpy.types.ClothSettings.shear_stiffness"></a>

#### bpy.types.ClothSettings.shear_stiffness

How much the material resists shearing (in [0, 10000], default 5.0)

**Type:**

float

<a id="bpy.types.ClothSettings.shear_stiffness_max"></a>

#### bpy.types.ClothSettings.shear_stiffness_max

Maximum shear scaling value (in [0, 10000], default 5.0)

**Type:**

float

<a id="bpy.types.ClothSettings.shrink_max"></a>

#### bpy.types.ClothSettings.shrink_max

Max amount to shrink cloth by (in [-inf, 1], default 0.0)

**Type:**

float

<a id="bpy.types.ClothSettings.shrink_min"></a>

#### bpy.types.ClothSettings.shrink_min

Factor by which to shrink cloth (in [-inf, 1], default 0.0)

**Type:**

float

<a id="bpy.types.ClothSettings.target_volume"></a>

#### bpy.types.ClothSettings.target_volume

The mesh volume where the inner/outer pressure will be the same. If set to zero the change in volume will not affect pressure. (in [0, 10000], default 0.0)

**Type:**

float

<a id="bpy.types.ClothSettings.tension_damping"></a>

#### bpy.types.ClothSettings.tension_damping

Amount of damping in stretching behavior (in [0, 50], default 5.0)

**Type:**

float

<a id="bpy.types.ClothSettings.tension_stiffness"></a>

#### bpy.types.ClothSettings.tension_stiffness

How much the material resists stretching (in [0, 10000], default 15.0)

**Type:**

float

<a id="bpy.types.ClothSettings.tension_stiffness_max"></a>

#### bpy.types.ClothSettings.tension_stiffness_max

Maximum tension stiffness value (in [0, 10000], default 15.0)

**Type:**

float

<a id="bpy.types.ClothSettings.time_scale"></a>

#### bpy.types.ClothSettings.time_scale

Cloth speed is multiplied by this value (in [0, inf], default 1.0)

**Type:**

float

<a id="bpy.types.ClothSettings.uniform_pressure_force"></a>

#### bpy.types.ClothSettings.uniform_pressure_force

The uniform pressure that is constantly applied to the mesh, in units of Pressure Scale. Can be negative. (in [-10000, 10000], default 0.0)

**Type:**

float

<a id="bpy.types.ClothSettings.use_dynamic_mesh"></a>

#### bpy.types.ClothSettings.use_dynamic_mesh

Make simulation respect deformations in the base mesh (default False)

**Type:**

bool

<a id="bpy.types.ClothSettings.use_internal_springs"></a>

#### bpy.types.ClothSettings.use_internal_springs

Simulate an internal volume structure by creating springs connecting the opposite sides of the mesh (default False)

**Type:**

bool

<a id="bpy.types.ClothSettings.use_pressure"></a>

#### bpy.types.ClothSettings.use_pressure

Simulate pressure inside a closed cloth mesh (default False)

**Type:**

bool

<a id="bpy.types.ClothSettings.use_pressure_volume"></a>

#### bpy.types.ClothSettings.use_pressure_volume

Use the Target Volume parameter as the initial volume, instead of calculating it from the mesh itself (default False)

**Type:**

bool

<a id="bpy.types.ClothSettings.use_sewing_springs"></a>

#### bpy.types.ClothSettings.use_sewing_springs

Pulls loose edges together (default False)

**Type:**

bool

<a id="bpy.types.ClothSettings.vertex_group_bending"></a>

#### bpy.types.ClothSettings.vertex_group_bending

Vertex group for fine control over bending stiffness (default “”, never None)

**Type:**

str

<a id="bpy.types.ClothSettings.vertex_group_intern"></a>

#### bpy.types.ClothSettings.vertex_group_intern

Vertex group for fine control over the internal spring stiffness (default “”, never None)

**Type:**

str

<a id="bpy.types.ClothSettings.vertex_group_mass"></a>

#### bpy.types.ClothSettings.vertex_group_mass

Vertex Group for pinning of vertices (default “”, never None)

**Type:**

str

<a id="bpy.types.ClothSettings.vertex_group_pressure"></a>

#### bpy.types.ClothSettings.vertex_group_pressure

Vertex Group for where to apply pressure. Zero weight means no pressure while a weight of one means full pressure. Faces with a vertex that has zero weight will be excluded from the volume calculation. (default “”, never None)

**Type:**

str

<a id="bpy.types.ClothSettings.vertex_group_shear_stiffness"></a>

#### bpy.types.ClothSettings.vertex_group_shear_stiffness

Vertex group for fine control over shear stiffness (default “”, never None)

**Type:**

str

<a id="bpy.types.ClothSettings.vertex_group_shrink"></a>

#### bpy.types.ClothSettings.vertex_group_shrink

Vertex Group for shrinking cloth (default “”, never None)

**Type:**

str

<a id="bpy.types.ClothSettings.vertex_group_structural_stiffness"></a>

#### bpy.types.ClothSettings.vertex_group_structural_stiffness

Vertex group for fine control over structural stiffness (default “”, never None)

**Type:**

str

<a id="bpy.types.ClothSettings.voxel_cell_size"></a>

#### bpy.types.ClothSettings.voxel_cell_size

Size of the voxel grid cells for interaction effects (in [0.0001, 10000], default 0.1)

**Type:**

float

<a id="bpy.types.ClothSettings.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ClothSettings.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ClothSettings.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ClothSettings.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`ClothModifier.settings`](bpy.types.ClothModifier.md#bpy.types.ClothModifier.settings "bpy.types.ClothModifier.settings") |  |
