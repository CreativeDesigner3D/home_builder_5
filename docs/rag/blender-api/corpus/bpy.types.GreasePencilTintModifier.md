<!-- source: Blender Python API reference 5.2 / bpy.types.GreasePencilTintModifier.html -->

<a id="greasepenciltintmodifier-modifier"></a>

# GreasePencilTintModifier(Modifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Modifier`](bpy.types.Modifier.md#bpy.types.Modifier "bpy.types.Modifier")

<a id="bpy.types.GreasePencilTintModifier"></a>

### class bpy.types.GreasePencilTintModifier(Modifier)

<a id="bpy.types.GreasePencilTintModifier.color"></a>

#### bpy.types.GreasePencilTintModifier.color

Color used for tinting (array of 3 items, in [0, 1], default (1.0, 1.0, 1.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.GreasePencilTintModifier.color_mode"></a>

#### bpy.types.GreasePencilTintModifier.color_mode

Attributes to modify (default `'BOTH'`)

- `BOTH`
  Stroke & Fill – Modify fill and stroke colors.
- `STROKE`
  Stroke – Modify stroke color only.
- `FILL`
  Fill – Modify fill color only.

**Type:**

Literal[‘BOTH’, ‘STROKE’, ‘FILL’]

<a id="bpy.types.GreasePencilTintModifier.color_ramp"></a>

#### bpy.types.GreasePencilTintModifier.color_ramp

Gradient tinting colors (readonly)

**Type:**

[`ColorRamp`](bpy.types.ColorRamp.md#bpy.types.ColorRamp "bpy.types.ColorRamp") | None

<a id="bpy.types.GreasePencilTintModifier.custom_curve"></a>

#### bpy.types.GreasePencilTintModifier.custom_curve

Custom curve to apply effect (readonly)

**Type:**

[`CurveMapping`](bpy.types.CurveMapping.md#bpy.types.CurveMapping "bpy.types.CurveMapping") | None

<a id="bpy.types.GreasePencilTintModifier.factor"></a>

#### bpy.types.GreasePencilTintModifier.factor

Factor for tinting (in [0, 2], default 0.5)

**Type:**

float

<a id="bpy.types.GreasePencilTintModifier.invert_layer_filter"></a>

#### bpy.types.GreasePencilTintModifier.invert_layer_filter

Invert layer filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilTintModifier.invert_layer_pass_filter"></a>

#### bpy.types.GreasePencilTintModifier.invert_layer_pass_filter

Invert layer pass filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilTintModifier.invert_material_filter"></a>

#### bpy.types.GreasePencilTintModifier.invert_material_filter

Invert material filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilTintModifier.invert_material_pass_filter"></a>

#### bpy.types.GreasePencilTintModifier.invert_material_pass_filter

Invert material pass filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilTintModifier.invert_vertex_group"></a>

#### bpy.types.GreasePencilTintModifier.invert_vertex_group

Invert vertex group weights (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilTintModifier.layer_pass_filter"></a>

#### bpy.types.GreasePencilTintModifier.layer_pass_filter

Layer pass filter (in [0, 100], default 0)

**Type:**

int

<a id="bpy.types.GreasePencilTintModifier.material_filter"></a>

#### bpy.types.GreasePencilTintModifier.material_filter

Material used for filtering

**Type:**

[`Material`](bpy.types.Material.md#bpy.types.Material "bpy.types.Material") | None

<a id="bpy.types.GreasePencilTintModifier.material_pass_filter"></a>

#### bpy.types.GreasePencilTintModifier.material_pass_filter

Material pass (in [0, 100], default 0)

**Type:**

int

<a id="bpy.types.GreasePencilTintModifier.object"></a>

#### bpy.types.GreasePencilTintModifier.object

Object used for the gradient direction

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.GreasePencilTintModifier.open_influence_panel"></a>

#### bpy.types.GreasePencilTintModifier.open_influence_panel

(default False)

**Type:**

bool

<a id="bpy.types.GreasePencilTintModifier.radius"></a>

#### bpy.types.GreasePencilTintModifier.radius

Influence distance from the object (in [1e-06, inf], default 1.0)

**Type:**

float

<a id="bpy.types.GreasePencilTintModifier.tint_mode"></a>

#### bpy.types.GreasePencilTintModifier.tint_mode

(default `'UNIFORM'`)

**Type:**

Literal[‘UNIFORM’, ‘GRADIENT’]

<a id="bpy.types.GreasePencilTintModifier.tree_node_filter"></a>

#### bpy.types.GreasePencilTintModifier.tree_node_filter

Layer name (default “”, never None)

**Type:**

str

<a id="bpy.types.GreasePencilTintModifier.use_custom_curve"></a>

#### bpy.types.GreasePencilTintModifier.use_custom_curve

Use a custom curve to define a factor along the strokes (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilTintModifier.use_layer_group_filter"></a>

#### bpy.types.GreasePencilTintModifier.use_layer_group_filter

Filter by layer group name (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilTintModifier.use_layer_pass_filter"></a>

#### bpy.types.GreasePencilTintModifier.use_layer_pass_filter

Use layer pass filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilTintModifier.use_material_pass_filter"></a>

#### bpy.types.GreasePencilTintModifier.use_material_pass_filter

Use material pass filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilTintModifier.use_weight_as_factor"></a>

#### bpy.types.GreasePencilTintModifier.use_weight_as_factor

Use vertex group weight as factor instead of influence (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilTintModifier.vertex_group_name"></a>

#### bpy.types.GreasePencilTintModifier.vertex_group_name

Vertex group name for modulating the deform (default “”, never None)

**Type:**

str

<a id="bpy.types.GreasePencilTintModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.GreasePencilTintModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.GreasePencilTintModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.GreasePencilTintModifier.bl_rna_get_subclass_py(id, default=None, /)

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
