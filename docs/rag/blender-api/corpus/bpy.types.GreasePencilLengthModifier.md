<!-- source: Blender Python API reference 5.2 / bpy.types.GreasePencilLengthModifier.html -->

<a id="greasepencillengthmodifier-modifier"></a>

# GreasePencilLengthModifier(Modifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Modifier`](bpy.types.Modifier.md#bpy.types.Modifier "bpy.types.Modifier")

<a id="bpy.types.GreasePencilLengthModifier"></a>

### class bpy.types.GreasePencilLengthModifier(Modifier)

Stretch or shrink strokes

<a id="bpy.types.GreasePencilLengthModifier.end_factor"></a>

#### bpy.types.GreasePencilLengthModifier.end_factor

Added length to the end of each stroke relative to its length (in [-inf, inf], default 0.1)

**Type:**

float

<a id="bpy.types.GreasePencilLengthModifier.end_length"></a>

#### bpy.types.GreasePencilLengthModifier.end_length

Absolute added length to the end of each stroke (in [-inf, inf], default 0.1)

**Type:**

float

<a id="bpy.types.GreasePencilLengthModifier.invert_curvature"></a>

#### bpy.types.GreasePencilLengthModifier.invert_curvature

Invert the curvature of the stroke’s extension (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilLengthModifier.invert_layer_filter"></a>

#### bpy.types.GreasePencilLengthModifier.invert_layer_filter

Invert layer filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilLengthModifier.invert_layer_pass_filter"></a>

#### bpy.types.GreasePencilLengthModifier.invert_layer_pass_filter

Invert layer pass filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilLengthModifier.invert_material_filter"></a>

#### bpy.types.GreasePencilLengthModifier.invert_material_filter

Invert material filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilLengthModifier.invert_material_pass_filter"></a>

#### bpy.types.GreasePencilLengthModifier.invert_material_pass_filter

Invert material pass filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilLengthModifier.layer_pass_filter"></a>

#### bpy.types.GreasePencilLengthModifier.layer_pass_filter

Layer pass filter (in [0, 100], default 0)

**Type:**

int

<a id="bpy.types.GreasePencilLengthModifier.material_filter"></a>

#### bpy.types.GreasePencilLengthModifier.material_filter

Material used for filtering

**Type:**

[`Material`](bpy.types.Material.md#bpy.types.Material "bpy.types.Material") | None

<a id="bpy.types.GreasePencilLengthModifier.material_pass_filter"></a>

#### bpy.types.GreasePencilLengthModifier.material_pass_filter

Material pass (in [0, 100], default 0)

**Type:**

int

<a id="bpy.types.GreasePencilLengthModifier.max_angle"></a>

#### bpy.types.GreasePencilLengthModifier.max_angle

Ignore points on the stroke that deviate from their neighbors by more than this angle when determining the extrapolation shape (in [0, 3.14159], default 2.96706)

**Type:**

float

<a id="bpy.types.GreasePencilLengthModifier.mode"></a>

#### bpy.types.GreasePencilLengthModifier.mode

Mode to define length (default `'RELATIVE'`)

- `RELATIVE`
  Relative – Length in ratio to the stroke’s length.
- `ABSOLUTE`
  Absolute – Length in geometry space.

**Type:**

Literal[‘RELATIVE’, ‘ABSOLUTE’]

<a id="bpy.types.GreasePencilLengthModifier.open_curvature_panel"></a>

#### bpy.types.GreasePencilLengthModifier.open_curvature_panel

(default False)

**Type:**

bool

<a id="bpy.types.GreasePencilLengthModifier.open_influence_panel"></a>

#### bpy.types.GreasePencilLengthModifier.open_influence_panel

(default False)

**Type:**

bool

<a id="bpy.types.GreasePencilLengthModifier.open_random_panel"></a>

#### bpy.types.GreasePencilLengthModifier.open_random_panel

(default False)

**Type:**

bool

<a id="bpy.types.GreasePencilLengthModifier.overshoot_factor"></a>

#### bpy.types.GreasePencilLengthModifier.overshoot_factor

Defines what portion of the stroke is used for the calculation of the extension (in [0, 1], default 0.1)

**Type:**

float

<a id="bpy.types.GreasePencilLengthModifier.point_density"></a>

#### bpy.types.GreasePencilLengthModifier.point_density

Multiplied by Start/End for the total added point count (in [0.1, 1000], default 30.0)

**Type:**

float

<a id="bpy.types.GreasePencilLengthModifier.random_end_factor"></a>

#### bpy.types.GreasePencilLengthModifier.random_end_factor

Size of random length added to the end of each stroke (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.GreasePencilLengthModifier.random_offset"></a>

#### bpy.types.GreasePencilLengthModifier.random_offset

Smoothly offset each stroke’s random value (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.GreasePencilLengthModifier.random_start_factor"></a>

#### bpy.types.GreasePencilLengthModifier.random_start_factor

Size of random length added to the start of each stroke (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.GreasePencilLengthModifier.seed"></a>

#### bpy.types.GreasePencilLengthModifier.seed

Random seed (in [0, inf], default 0)

**Type:**

int

<a id="bpy.types.GreasePencilLengthModifier.segment_influence"></a>

#### bpy.types.GreasePencilLengthModifier.segment_influence

Factor to determine how much the length of the individual segments should influence the final computed curvature. Higher factors makes small segments influence the overall curvature less. (in [-2, 3], default 0.0)

**Type:**

float

<a id="bpy.types.GreasePencilLengthModifier.start_factor"></a>

#### bpy.types.GreasePencilLengthModifier.start_factor

Added length to the start of each stroke relative to its length (in [-inf, inf], default 0.1)

**Type:**

float

<a id="bpy.types.GreasePencilLengthModifier.start_length"></a>

#### bpy.types.GreasePencilLengthModifier.start_length

Absolute added length to the start of each stroke (in [-inf, inf], default 0.1)

**Type:**

float

<a id="bpy.types.GreasePencilLengthModifier.step"></a>

#### bpy.types.GreasePencilLengthModifier.step

Number of frames between randomization steps (in [1, 100], default 4)

**Type:**

int

<a id="bpy.types.GreasePencilLengthModifier.tree_node_filter"></a>

#### bpy.types.GreasePencilLengthModifier.tree_node_filter

Layer name (default “”, never None)

**Type:**

str

<a id="bpy.types.GreasePencilLengthModifier.use_curvature"></a>

#### bpy.types.GreasePencilLengthModifier.use_curvature

Follow the curvature of the stroke (default True)

**Type:**

bool

<a id="bpy.types.GreasePencilLengthModifier.use_layer_group_filter"></a>

#### bpy.types.GreasePencilLengthModifier.use_layer_group_filter

Filter by layer group name (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilLengthModifier.use_layer_pass_filter"></a>

#### bpy.types.GreasePencilLengthModifier.use_layer_pass_filter

Use layer pass filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilLengthModifier.use_material_pass_filter"></a>

#### bpy.types.GreasePencilLengthModifier.use_material_pass_filter

Use material pass filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilLengthModifier.use_random"></a>

#### bpy.types.GreasePencilLengthModifier.use_random

Use random values over time (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilLengthModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.GreasePencilLengthModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.GreasePencilLengthModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.GreasePencilLengthModifier.bl_rna_get_subclass_py(id, default=None, /)

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
