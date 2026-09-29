<!-- source: Blender Python API reference 5.2 / bpy.types.GreasePencilNoiseModifier.html -->

<a id="greasepencilnoisemodifier-modifier"></a>

# GreasePencilNoiseModifier(Modifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Modifier`](bpy.types.Modifier.md#bpy.types.Modifier "bpy.types.Modifier")

<a id="bpy.types.GreasePencilNoiseModifier"></a>

### class bpy.types.GreasePencilNoiseModifier(Modifier)

Noise effect modifier

<a id="bpy.types.GreasePencilNoiseModifier.custom_curve"></a>

#### bpy.types.GreasePencilNoiseModifier.custom_curve

Custom curve to apply effect (readonly)

**Type:**

[`CurveMapping`](bpy.types.CurveMapping.md#bpy.types.CurveMapping "bpy.types.CurveMapping") | None

<a id="bpy.types.GreasePencilNoiseModifier.factor"></a>

#### bpy.types.GreasePencilNoiseModifier.factor

Amount of noise to apply (in [0, inf], default 0.5)

**Type:**

float

<a id="bpy.types.GreasePencilNoiseModifier.factor_strength"></a>

#### bpy.types.GreasePencilNoiseModifier.factor_strength

Amount of noise to apply to opacity (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.GreasePencilNoiseModifier.factor_thickness"></a>

#### bpy.types.GreasePencilNoiseModifier.factor_thickness

Amount of noise to apply to thickness (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.GreasePencilNoiseModifier.factor_uvs"></a>

#### bpy.types.GreasePencilNoiseModifier.factor_uvs

Amount of noise to apply to UV rotation (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.GreasePencilNoiseModifier.invert_layer_filter"></a>

#### bpy.types.GreasePencilNoiseModifier.invert_layer_filter

Invert layer filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilNoiseModifier.invert_layer_pass_filter"></a>

#### bpy.types.GreasePencilNoiseModifier.invert_layer_pass_filter

Invert layer pass filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilNoiseModifier.invert_material_filter"></a>

#### bpy.types.GreasePencilNoiseModifier.invert_material_filter

Invert material filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilNoiseModifier.invert_material_pass_filter"></a>

#### bpy.types.GreasePencilNoiseModifier.invert_material_pass_filter

Invert material pass filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilNoiseModifier.invert_vertex_group"></a>

#### bpy.types.GreasePencilNoiseModifier.invert_vertex_group

Invert vertex group weights (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilNoiseModifier.layer_pass_filter"></a>

#### bpy.types.GreasePencilNoiseModifier.layer_pass_filter

Layer pass filter (in [0, 100], default 0)

**Type:**

int

<a id="bpy.types.GreasePencilNoiseModifier.material_filter"></a>

#### bpy.types.GreasePencilNoiseModifier.material_filter

Material used for filtering

**Type:**

[`Material`](bpy.types.Material.md#bpy.types.Material "bpy.types.Material") | None

<a id="bpy.types.GreasePencilNoiseModifier.material_pass_filter"></a>

#### bpy.types.GreasePencilNoiseModifier.material_pass_filter

Material pass (in [0, 100], default 0)

**Type:**

int

<a id="bpy.types.GreasePencilNoiseModifier.noise_offset"></a>

#### bpy.types.GreasePencilNoiseModifier.noise_offset

Offset the noise along the strokes (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.GreasePencilNoiseModifier.noise_scale"></a>

#### bpy.types.GreasePencilNoiseModifier.noise_scale

Scale the noise frequency (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.GreasePencilNoiseModifier.open_influence_panel"></a>

#### bpy.types.GreasePencilNoiseModifier.open_influence_panel

(default False)

**Type:**

bool

<a id="bpy.types.GreasePencilNoiseModifier.open_random_panel"></a>

#### bpy.types.GreasePencilNoiseModifier.open_random_panel

(default False)

**Type:**

bool

<a id="bpy.types.GreasePencilNoiseModifier.random_mode"></a>

#### bpy.types.GreasePencilNoiseModifier.random_mode

Where to perform randomization (default `'STEP'`)

- `STEP`
  Steps – Randomize every number of frames.
- `KEYFRAME`
  Keyframes – Randomize on keyframes only.

**Type:**

Literal[‘STEP’, ‘KEYFRAME’]

<a id="bpy.types.GreasePencilNoiseModifier.seed"></a>

#### bpy.types.GreasePencilNoiseModifier.seed

Random seed (in [0, inf], default 1)

**Type:**

int

<a id="bpy.types.GreasePencilNoiseModifier.step"></a>

#### bpy.types.GreasePencilNoiseModifier.step

Number of frames between randomization steps (in [1, 100], default 4)

**Type:**

int

<a id="bpy.types.GreasePencilNoiseModifier.tree_node_filter"></a>

#### bpy.types.GreasePencilNoiseModifier.tree_node_filter

Layer name (default “”, never None)

**Type:**

str

<a id="bpy.types.GreasePencilNoiseModifier.use_custom_curve"></a>

#### bpy.types.GreasePencilNoiseModifier.use_custom_curve

Use a custom curve to define a factor along the strokes (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilNoiseModifier.use_layer_group_filter"></a>

#### bpy.types.GreasePencilNoiseModifier.use_layer_group_filter

Filter by layer group name (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilNoiseModifier.use_layer_pass_filter"></a>

#### bpy.types.GreasePencilNoiseModifier.use_layer_pass_filter

Use layer pass filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilNoiseModifier.use_material_pass_filter"></a>

#### bpy.types.GreasePencilNoiseModifier.use_material_pass_filter

Use material pass filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilNoiseModifier.use_random"></a>

#### bpy.types.GreasePencilNoiseModifier.use_random

Use random values over time (default True)

**Type:**

bool

<a id="bpy.types.GreasePencilNoiseModifier.vertex_group_name"></a>

#### bpy.types.GreasePencilNoiseModifier.vertex_group_name

Vertex group name for modulating the deform (default “”, never None)

**Type:**

str

<a id="bpy.types.GreasePencilNoiseModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.GreasePencilNoiseModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.GreasePencilNoiseModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.GreasePencilNoiseModifier.bl_rna_get_subclass_py(id, default=None, /)

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
