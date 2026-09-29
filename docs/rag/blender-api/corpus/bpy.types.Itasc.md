<!-- source: Blender Python API reference 5.2 / bpy.types.Itasc.html -->

<a id="itasc-ikparam"></a>

# Itasc(IKParam)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`IKParam`](bpy.types.IKParam.md#bpy.types.IKParam "bpy.types.IKParam")

<a id="bpy.types.Itasc"></a>

### class bpy.types.Itasc(IKParam)

Parameters for the iTaSC IK solver

<a id="bpy.types.Itasc.damping_epsilon"></a>

#### bpy.types.Itasc.damping_epsilon

Singular value under which damping is progressively applied (higher values produce results with more stability, less reactivity) (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.Itasc.damping_max"></a>

#### bpy.types.Itasc.damping_max

Maximum damping coefficient when singular value is nearly 0 (higher values produce results with more stability, less reactivity) (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.Itasc.feedback"></a>

#### bpy.types.Itasc.feedback

Feedback coefficient for error correction, average response time is 1/feedback (in [0, 100], default 0.0)

**Type:**

float

<a id="bpy.types.Itasc.iterations"></a>

#### bpy.types.Itasc.iterations

Maximum number of iterations for convergence in case of reiteration (in [0, 1000], default 0)

**Type:**

int

<a id="bpy.types.Itasc.mode"></a>

#### bpy.types.Itasc.mode

(default `'ANIMATION'`)

- `ANIMATION`
  Animation – Stateless solver computing pose starting from current action and non-IK constraints.
- `SIMULATION`
  Simulation – State-full solver running in real-time context and ignoring actions and non-IK constraints.

**Type:**

Literal[‘ANIMATION’, ‘SIMULATION’]

<a id="bpy.types.Itasc.precision"></a>

#### bpy.types.Itasc.precision

Precision of convergence in case of reiteration (in [0, 0.1], default 0.0)

**Type:**

float

<a id="bpy.types.Itasc.reiteration_method"></a>

#### bpy.types.Itasc.reiteration_method

Defines if the solver is allowed to reiterate (converge until precision is met) on none, first or all frames (default `'NEVER'`)

- `NEVER`
  Never – The solver does not reiterate, not even on first frame (starts from rest pose).
- `INITIAL`
  Initial – The solver reiterates (converges) on the first frame but not on subsequent frame.
- `ALWAYS`
  Always – The solver reiterates (converges) on all frames.

**Type:**

Literal[‘NEVER’, ‘INITIAL’, ‘ALWAYS’]

<a id="bpy.types.Itasc.solver"></a>

#### bpy.types.Itasc.solver

Solving method selection: automatic damping or manual damping (default `'SDLS'`)

- `SDLS`
  SDLS – Selective Damped Least Square.
- `DLS`
  DLS – Damped Least Square with Numerical Filtering.

**Type:**

Literal[‘SDLS’, ‘DLS’]

<a id="bpy.types.Itasc.step_count"></a>

#### bpy.types.Itasc.step_count

Divide the frame interval into this many steps (in [1, 50], default 0)

**Type:**

int

<a id="bpy.types.Itasc.step_max"></a>

#### bpy.types.Itasc.step_max

Higher bound for timestep in second in case of automatic substeps (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.Itasc.step_min"></a>

#### bpy.types.Itasc.step_min

Lower bound for timestep in second in case of automatic substeps (in [0, 0.1], default 0.0)

**Type:**

float

<a id="bpy.types.Itasc.translate_root_bones"></a>

#### bpy.types.Itasc.translate_root_bones

Translate root (i.e. parentless) bones to the armature origin (default False)

**Type:**

bool

<a id="bpy.types.Itasc.use_auto_step"></a>

#### bpy.types.Itasc.use_auto_step

Automatically determine the optimal number of steps for best performance/accuracy trade off (default False)

**Type:**

bool

<a id="bpy.types.Itasc.velocity_max"></a>

#### bpy.types.Itasc.velocity_max

Maximum joint velocity in radians/second (in [0, 100], default 0.0)

**Type:**

float

<a id="bpy.types.Itasc.bl_rna_get_subclass"></a>

#### classmethod bpy.types.Itasc.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.Itasc.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.Itasc.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, IKParam.ik_solver

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, IKParam.bl_rna_get_subclass, IKParam.bl_rna_get_subclass_py
