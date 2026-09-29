<!-- source: Blender Python API reference 5.2 / bpy.types.GreasePencilEnvelopeModifier.html -->

<a id="greasepencilenvelopemodifier-modifier"></a>

# GreasePencilEnvelopeModifier(Modifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Modifier`](bpy.types.Modifier.md#bpy.types.Modifier "bpy.types.Modifier")

<a id="bpy.types.GreasePencilEnvelopeModifier"></a>

### class bpy.types.GreasePencilEnvelopeModifier(Modifier)

Envelope stroke effect modifier

<a id="bpy.types.GreasePencilEnvelopeModifier.invert_layer_filter"></a>

#### bpy.types.GreasePencilEnvelopeModifier.invert_layer_filter

Invert layer filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilEnvelopeModifier.invert_layer_pass_filter"></a>

#### bpy.types.GreasePencilEnvelopeModifier.invert_layer_pass_filter

Invert layer pass filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilEnvelopeModifier.invert_material_filter"></a>

#### bpy.types.GreasePencilEnvelopeModifier.invert_material_filter

Invert material filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilEnvelopeModifier.invert_material_pass_filter"></a>

#### bpy.types.GreasePencilEnvelopeModifier.invert_material_pass_filter

Invert material pass filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilEnvelopeModifier.invert_vertex_group"></a>

#### bpy.types.GreasePencilEnvelopeModifier.invert_vertex_group

Invert vertex group weights (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilEnvelopeModifier.layer_pass_filter"></a>

#### bpy.types.GreasePencilEnvelopeModifier.layer_pass_filter

Layer pass filter (in [0, 100], default 0)

**Type:**

int

<a id="bpy.types.GreasePencilEnvelopeModifier.mat_nr"></a>

#### bpy.types.GreasePencilEnvelopeModifier.mat_nr

The material to use for the new strokes (in [-1, 32767], default -1)

**Type:**

int

<a id="bpy.types.GreasePencilEnvelopeModifier.material_filter"></a>

#### bpy.types.GreasePencilEnvelopeModifier.material_filter

Material used for filtering

**Type:**

[`Material`](bpy.types.Material.md#bpy.types.Material "bpy.types.Material") | None

<a id="bpy.types.GreasePencilEnvelopeModifier.material_pass_filter"></a>

#### bpy.types.GreasePencilEnvelopeModifier.material_pass_filter

Material pass (in [0, 100], default 0)

**Type:**

int

<a id="bpy.types.GreasePencilEnvelopeModifier.mode"></a>

#### bpy.types.GreasePencilEnvelopeModifier.mode

Algorithm to use for generating the envelope (default `'SEGMENTS'`)

- `DEFORM`
  Deform – Deform the stroke to best match the envelope shape.
- `SEGMENTS`
  Segments – Add segments to create the envelope. Keep the original stroke..
- `FILLS`
  Fills – Add fill segments to create the envelope. Don’t keep the original stroke..

**Type:**

Literal[‘DEFORM’, ‘SEGMENTS’, ‘FILLS’]

<a id="bpy.types.GreasePencilEnvelopeModifier.open_influence_panel"></a>

#### bpy.types.GreasePencilEnvelopeModifier.open_influence_panel

(default False)

**Type:**

bool

<a id="bpy.types.GreasePencilEnvelopeModifier.skip"></a>

#### bpy.types.GreasePencilEnvelopeModifier.skip

The number of generated segments to skip to reduce complexity (in [0, inf], default 0)

**Type:**

int

<a id="bpy.types.GreasePencilEnvelopeModifier.spread"></a>

#### bpy.types.GreasePencilEnvelopeModifier.spread

The number of points to skip to create straight segments (in [1, inf], default 10)

**Type:**

int

<a id="bpy.types.GreasePencilEnvelopeModifier.strength"></a>

#### bpy.types.GreasePencilEnvelopeModifier.strength

Multiplier for the strength of the new strokes (in [0, inf], default 1.0)

**Type:**

float

<a id="bpy.types.GreasePencilEnvelopeModifier.thickness"></a>

#### bpy.types.GreasePencilEnvelopeModifier.thickness

Multiplier for the thickness of the new strokes (in [0, inf], default 1.0)

**Type:**

float

<a id="bpy.types.GreasePencilEnvelopeModifier.tree_node_filter"></a>

#### bpy.types.GreasePencilEnvelopeModifier.tree_node_filter

Layer name (default “”, never None)

**Type:**

str

<a id="bpy.types.GreasePencilEnvelopeModifier.use_layer_group_filter"></a>

#### bpy.types.GreasePencilEnvelopeModifier.use_layer_group_filter

Filter by layer group name (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilEnvelopeModifier.use_layer_pass_filter"></a>

#### bpy.types.GreasePencilEnvelopeModifier.use_layer_pass_filter

Use layer pass filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilEnvelopeModifier.use_material_pass_filter"></a>

#### bpy.types.GreasePencilEnvelopeModifier.use_material_pass_filter

Use material pass filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilEnvelopeModifier.vertex_group_name"></a>

#### bpy.types.GreasePencilEnvelopeModifier.vertex_group_name

Vertex group name for modulating the deform (default “”, never None)

**Type:**

str

<a id="bpy.types.GreasePencilEnvelopeModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.GreasePencilEnvelopeModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.GreasePencilEnvelopeModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.GreasePencilEnvelopeModifier.bl_rna_get_subclass_py(id, default=None, /)

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
