<!-- source: Blender Python API reference 5.2 / bpy.types.SoftBodySettings.html -->

<a id="softbodysettings-bpy-struct"></a>

# SoftBodySettings(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.SoftBodySettings"></a>

### class bpy.types.SoftBodySettings(bpy_struct)

Soft body simulation settings for an object

<a id="bpy.types.SoftBodySettings.aero"></a>

#### bpy.types.SoftBodySettings.aero

Make edges ‘sail’ (in [0, 30000], default 0)

**Type:**

int

<a id="bpy.types.SoftBodySettings.aerodynamics_type"></a>

#### bpy.types.SoftBodySettings.aerodynamics_type

Method of calculating aerodynamic interaction (default `'SIMPLE'`)

- `SIMPLE`
  Simple – Edges receive a drag force from surrounding media.
- `LIFT_FORCE`
  Lift Force – Edges receive a lift force when passing through surrounding media.

**Type:**

Literal[‘SIMPLE’, ‘LIFT_FORCE’]

<a id="bpy.types.SoftBodySettings.ball_damp"></a>

#### bpy.types.SoftBodySettings.ball_damp

Blending to inelastic collision (in [0.001, 1], default 0.0)

**Type:**

float

<a id="bpy.types.SoftBodySettings.ball_size"></a>

#### bpy.types.SoftBodySettings.ball_size

Absolute ball size or factor if not manually adjusted (in [-10, 10], default 0.0)

**Type:**

float

<a id="bpy.types.SoftBodySettings.ball_stiff"></a>

#### bpy.types.SoftBodySettings.ball_stiff

Ball inflating pressure (in [0.001, 100], default 0.0)

**Type:**

float

<a id="bpy.types.SoftBodySettings.bend"></a>

#### bpy.types.SoftBodySettings.bend

Bending Stiffness (in [0, 10], default 0.0)

**Type:**

float

<a id="bpy.types.SoftBodySettings.choke"></a>

#### bpy.types.SoftBodySettings.choke

‘Viscosity’ inside collision target (in [0, 100], default 0)

**Type:**

int

<a id="bpy.types.SoftBodySettings.collision_collection"></a>

#### bpy.types.SoftBodySettings.collision_collection

Limit colliders to this collection

**Type:**

[`Collection`](bpy.types.Collection.md#bpy.types.Collection "bpy.types.Collection") | None

<a id="bpy.types.SoftBodySettings.collision_type"></a>

#### bpy.types.SoftBodySettings.collision_type

Choose Collision Type (default `'MANUAL'`)

- `MANUAL`
  Manual – Manual adjust.
- `AVERAGE`
  Average – Average Spring length * Ball Size.
- `MINIMAL`
  Minimal – Minimal Spring length * Ball Size.
- `MAXIMAL`
  Maximal – Maximal Spring length * Ball Size.
- `MINMAX`
  AvMinMax – (Min+Max)/2 * Ball Size.

**Type:**

Literal[‘MANUAL’, ‘AVERAGE’, ‘MINIMAL’, ‘MAXIMAL’, ‘MINMAX’]

<a id="bpy.types.SoftBodySettings.damping"></a>

#### bpy.types.SoftBodySettings.damping

Edge spring friction (in [0, 50], default 0.0)

**Type:**

float

<a id="bpy.types.SoftBodySettings.effector_weights"></a>

#### bpy.types.SoftBodySettings.effector_weights

(readonly)

**Type:**

[`EffectorWeights`](bpy.types.EffectorWeights.md#bpy.types.EffectorWeights "bpy.types.EffectorWeights") | None

<a id="bpy.types.SoftBodySettings.error_threshold"></a>

#### bpy.types.SoftBodySettings.error_threshold

The Runge-Kutta ODE solver error limit, low value gives more precision, high values speed (in [0.001, 10], default 0.0)

**Type:**

float

<a id="bpy.types.SoftBodySettings.friction"></a>

#### bpy.types.SoftBodySettings.friction

General media friction for point movements (in [0, 50], default 0.0)

**Type:**

float

<a id="bpy.types.SoftBodySettings.fuzzy"></a>

#### bpy.types.SoftBodySettings.fuzzy

Fuzziness while on collision, high values make collision handling faster but less stable (in [1, 100], default 0)

**Type:**

int

<a id="bpy.types.SoftBodySettings.goal_default"></a>

#### bpy.types.SoftBodySettings.goal_default

Default Goal (vertex target position) value (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.SoftBodySettings.goal_friction"></a>

#### bpy.types.SoftBodySettings.goal_friction

Goal (vertex target position) friction (in [0, 50], default 0.0)

**Type:**

float

<a id="bpy.types.SoftBodySettings.goal_max"></a>

#### bpy.types.SoftBodySettings.goal_max

Goal maximum, vertex weights are scaled to match this range (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.SoftBodySettings.goal_min"></a>

#### bpy.types.SoftBodySettings.goal_min

Goal minimum, vertex weights are scaled to match this range (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.SoftBodySettings.goal_spring"></a>

#### bpy.types.SoftBodySettings.goal_spring

Goal (vertex target position) spring stiffness (in [0, 0.999], default 0.0)

**Type:**

float

<a id="bpy.types.SoftBodySettings.gravity"></a>

#### bpy.types.SoftBodySettings.gravity

Apply gravitation to point movement (in [-10, 10], default 0.0)

**Type:**

float

<a id="bpy.types.SoftBodySettings.location_mass_center"></a>

#### bpy.types.SoftBodySettings.location_mass_center

Location of center of mass (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.SoftBodySettings.mass"></a>

#### bpy.types.SoftBodySettings.mass

General Mass value (in [0, 50000], default 0.0)

**Type:**

float

<a id="bpy.types.SoftBodySettings.plastic"></a>

#### bpy.types.SoftBodySettings.plastic

Permanent deform (in [0, 100], default 0)

**Type:**

int

<a id="bpy.types.SoftBodySettings.pull"></a>

#### bpy.types.SoftBodySettings.pull

Edge spring stiffness when longer than rest length (in [0, 0.999], default 0.0)

**Type:**

float

<a id="bpy.types.SoftBodySettings.push"></a>

#### bpy.types.SoftBodySettings.push

Edge spring stiffness when shorter than rest length (in [0, 0.999], default 0.0)

**Type:**

float

<a id="bpy.types.SoftBodySettings.rotation_estimate"></a>

#### bpy.types.SoftBodySettings.rotation_estimate

Estimated rotation matrix (multi-dimensional array of 3 * 3 items, in [-inf, inf], default ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)))

**Type:**

[`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")

<a id="bpy.types.SoftBodySettings.scale_estimate"></a>

#### bpy.types.SoftBodySettings.scale_estimate

Estimated scale matrix (multi-dimensional array of 3 * 3 items, in [-inf, inf], default ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)))

**Type:**

[`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")

<a id="bpy.types.SoftBodySettings.shear"></a>

#### bpy.types.SoftBodySettings.shear

Shear Stiffness (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.SoftBodySettings.speed"></a>

#### bpy.types.SoftBodySettings.speed

Tweak timing for physics to control frequency and speed (in [0.01, 100], default 0.0)

**Type:**

float

<a id="bpy.types.SoftBodySettings.spring_length"></a>

#### bpy.types.SoftBodySettings.spring_length

Alter spring length to shrink/blow up (unit %) 0 to disable (in [0, 200], default 0)

**Type:**

int

<a id="bpy.types.SoftBodySettings.step_max"></a>

#### bpy.types.SoftBodySettings.step_max

Maximal # solver steps/frame (in [0, 30000], default 0)

**Type:**

int

<a id="bpy.types.SoftBodySettings.step_min"></a>

#### bpy.types.SoftBodySettings.step_min

Minimal # solver steps/frame (in [0, 30000], default 0)

**Type:**

int

<a id="bpy.types.SoftBodySettings.use_auto_step"></a>

#### bpy.types.SoftBodySettings.use_auto_step

Use velocities for automagic step sizes (default False)

**Type:**

bool

<a id="bpy.types.SoftBodySettings.use_diagnose"></a>

#### bpy.types.SoftBodySettings.use_diagnose

Turn on SB diagnose console prints (default False)

**Type:**

bool

<a id="bpy.types.SoftBodySettings.use_edge_collision"></a>

#### bpy.types.SoftBodySettings.use_edge_collision

Edges collide too (default False)

**Type:**

bool

<a id="bpy.types.SoftBodySettings.use_edges"></a>

#### bpy.types.SoftBodySettings.use_edges

Use Edges as springs (default False)

**Type:**

bool

<a id="bpy.types.SoftBodySettings.use_estimate_matrix"></a>

#### bpy.types.SoftBodySettings.use_estimate_matrix

Store the estimated transforms in the soft body settings (default False)

**Type:**

bool

<a id="bpy.types.SoftBodySettings.use_face_collision"></a>

#### bpy.types.SoftBodySettings.use_face_collision

Faces collide too, can be very slow (default False)

**Type:**

bool

<a id="bpy.types.SoftBodySettings.use_goal"></a>

#### bpy.types.SoftBodySettings.use_goal

Define forces for vertices to stick to animated position (default False)

**Type:**

bool

<a id="bpy.types.SoftBodySettings.use_self_collision"></a>

#### bpy.types.SoftBodySettings.use_self_collision

Enable naive vertex ball self collision (default False)

**Type:**

bool

<a id="bpy.types.SoftBodySettings.use_stiff_quads"></a>

#### bpy.types.SoftBodySettings.use_stiff_quads

Add diagonal springs on 4-gons (default False)

**Type:**

bool

<a id="bpy.types.SoftBodySettings.vertex_group_goal"></a>

#### bpy.types.SoftBodySettings.vertex_group_goal

Control point weight values (default “”, never None)

**Type:**

str

<a id="bpy.types.SoftBodySettings.vertex_group_mass"></a>

#### bpy.types.SoftBodySettings.vertex_group_mass

Control point mass values (default “”, never None)

**Type:**

str

<a id="bpy.types.SoftBodySettings.vertex_group_spring"></a>

#### bpy.types.SoftBodySettings.vertex_group_spring

Control point spring strength values (default “”, never None)

**Type:**

str

<a id="bpy.types.SoftBodySettings.bl_rna_get_subclass"></a>

#### classmethod bpy.types.SoftBodySettings.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.SoftBodySettings.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.SoftBodySettings.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Object.soft_body`](bpy.types.Object.md#bpy.types.Object.soft_body "bpy.types.Object.soft_body") | - [`SoftBodyModifier.settings`](bpy.types.SoftBodyModifier.md#bpy.types.SoftBodyModifier.settings "bpy.types.SoftBodyModifier.settings") |
