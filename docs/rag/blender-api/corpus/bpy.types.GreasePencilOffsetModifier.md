<!-- source: Blender Python API reference 5.2 / bpy.types.GreasePencilOffsetModifier.html -->

<a id="greasepenciloffsetmodifier-modifier"></a>

# GreasePencilOffsetModifier(Modifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Modifier`](bpy.types.Modifier.md#bpy.types.Modifier "bpy.types.Modifier")

<a id="bpy.types.GreasePencilOffsetModifier"></a>

### class bpy.types.GreasePencilOffsetModifier(Modifier)

<a id="bpy.types.GreasePencilOffsetModifier.invert_layer_filter"></a>

#### bpy.types.GreasePencilOffsetModifier.invert_layer_filter

Invert layer filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilOffsetModifier.invert_layer_pass_filter"></a>

#### bpy.types.GreasePencilOffsetModifier.invert_layer_pass_filter

Invert layer pass filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilOffsetModifier.invert_material_filter"></a>

#### bpy.types.GreasePencilOffsetModifier.invert_material_filter

Invert material filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilOffsetModifier.invert_material_pass_filter"></a>

#### bpy.types.GreasePencilOffsetModifier.invert_material_pass_filter

Invert material pass filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilOffsetModifier.invert_vertex_group"></a>

#### bpy.types.GreasePencilOffsetModifier.invert_vertex_group

Invert vertex group weights (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilOffsetModifier.layer_pass_filter"></a>

#### bpy.types.GreasePencilOffsetModifier.layer_pass_filter

Layer pass filter (in [0, 100], default 0)

**Type:**

int

<a id="bpy.types.GreasePencilOffsetModifier.location"></a>

#### bpy.types.GreasePencilOffsetModifier.location

Values for change location (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.GreasePencilOffsetModifier.material_filter"></a>

#### bpy.types.GreasePencilOffsetModifier.material_filter

Material used for filtering

**Type:**

[`Material`](bpy.types.Material.md#bpy.types.Material "bpy.types.Material") | None

<a id="bpy.types.GreasePencilOffsetModifier.material_pass_filter"></a>

#### bpy.types.GreasePencilOffsetModifier.material_pass_filter

Material pass (in [0, 100], default 0)

**Type:**

int

<a id="bpy.types.GreasePencilOffsetModifier.offset_mode"></a>

#### bpy.types.GreasePencilOffsetModifier.offset_mode

(default `'RANDOM'`)

- `RANDOM`
  Random – Randomize stroke offset.
- `LAYER`
  Layer – Offset layers by the same factor.
- `STROKE`
  Stroke – Offset strokes by the same factor based on stroke draw order.
- `MATERIAL`
  Material – Offset materials by the same factor.

**Type:**

Literal[‘RANDOM’, ‘LAYER’, ‘STROKE’, ‘MATERIAL’]

<a id="bpy.types.GreasePencilOffsetModifier.open_general_panel"></a>

#### bpy.types.GreasePencilOffsetModifier.open_general_panel

(default False)

**Type:**

bool

<a id="bpy.types.GreasePencilOffsetModifier.open_influence_panel"></a>

#### bpy.types.GreasePencilOffsetModifier.open_influence_panel

(default False)

**Type:**

bool

<a id="bpy.types.GreasePencilOffsetModifier.rotation"></a>

#### bpy.types.GreasePencilOffsetModifier.rotation

Values for changes in rotation (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler")

<a id="bpy.types.GreasePencilOffsetModifier.scale"></a>

#### bpy.types.GreasePencilOffsetModifier.scale

Values for changes in scale (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.GreasePencilOffsetModifier.seed"></a>

#### bpy.types.GreasePencilOffsetModifier.seed

Random seed (in [0, inf], default 0)

**Type:**

int

<a id="bpy.types.GreasePencilOffsetModifier.stroke_location"></a>

#### bpy.types.GreasePencilOffsetModifier.stroke_location

Value for changes in location (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.GreasePencilOffsetModifier.stroke_rotation"></a>

#### bpy.types.GreasePencilOffsetModifier.stroke_rotation

Value for changes in rotation (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler")

<a id="bpy.types.GreasePencilOffsetModifier.stroke_scale"></a>

#### bpy.types.GreasePencilOffsetModifier.stroke_scale

Value for changes in scale (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.GreasePencilOffsetModifier.stroke_start_offset"></a>

#### bpy.types.GreasePencilOffsetModifier.stroke_start_offset

Offset starting point (in [0, inf], default 0)

**Type:**

int

<a id="bpy.types.GreasePencilOffsetModifier.stroke_step"></a>

#### bpy.types.GreasePencilOffsetModifier.stroke_step

Number of elements that will be grouped (in [1, 500], default 1)

**Type:**

int

<a id="bpy.types.GreasePencilOffsetModifier.tree_node_filter"></a>

#### bpy.types.GreasePencilOffsetModifier.tree_node_filter

Layer name (default “”, never None)

**Type:**

str

<a id="bpy.types.GreasePencilOffsetModifier.use_layer_group_filter"></a>

#### bpy.types.GreasePencilOffsetModifier.use_layer_group_filter

Filter by layer group name (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilOffsetModifier.use_layer_pass_filter"></a>

#### bpy.types.GreasePencilOffsetModifier.use_layer_pass_filter

Use layer pass filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilOffsetModifier.use_material_pass_filter"></a>

#### bpy.types.GreasePencilOffsetModifier.use_material_pass_filter

Use material pass filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilOffsetModifier.use_uniform_random_scale"></a>

#### bpy.types.GreasePencilOffsetModifier.use_uniform_random_scale

Use the same random seed for each scale axis for a uniform scale (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilOffsetModifier.vertex_group_name"></a>

#### bpy.types.GreasePencilOffsetModifier.vertex_group_name

Vertex group name for modulating the deform (default “”, never None)

**Type:**

str

<a id="bpy.types.GreasePencilOffsetModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.GreasePencilOffsetModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.GreasePencilOffsetModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.GreasePencilOffsetModifier.bl_rna_get_subclass_py(id, default=None, /)

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
