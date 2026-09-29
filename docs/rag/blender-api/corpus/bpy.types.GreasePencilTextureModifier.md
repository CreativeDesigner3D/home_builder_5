<!-- source: Blender Python API reference 5.2 / bpy.types.GreasePencilTextureModifier.html -->

<a id="greasepenciltexturemodifier-modifier"></a>

# GreasePencilTextureModifier(Modifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Modifier`](bpy.types.Modifier.md#bpy.types.Modifier "bpy.types.Modifier")

<a id="bpy.types.GreasePencilTextureModifier"></a>

### class bpy.types.GreasePencilTextureModifier(Modifier)

Transform stroke texture coordinates Modifier

<a id="bpy.types.GreasePencilTextureModifier.alignment_rotation"></a>

#### bpy.types.GreasePencilTextureModifier.alignment_rotation

Additional rotation applied to dots and square strokes (in [-1.5708, 1.5708], default 0.0)

**Type:**

float

<a id="bpy.types.GreasePencilTextureModifier.fill_offset"></a>

#### bpy.types.GreasePencilTextureModifier.fill_offset

Additional offset of the fill UV (array of 2 items, in [-inf, inf], default (0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.GreasePencilTextureModifier.fill_rotation"></a>

#### bpy.types.GreasePencilTextureModifier.fill_rotation

Additional rotation of the fill UV (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.GreasePencilTextureModifier.fill_scale"></a>

#### bpy.types.GreasePencilTextureModifier.fill_scale

Additional scale of the fill UV (in [0.01, 100], default 1.0)

**Type:**

float

<a id="bpy.types.GreasePencilTextureModifier.fit_method"></a>

#### bpy.types.GreasePencilTextureModifier.fit_method

(default `'CONSTANT_LENGTH'`)

- `CONSTANT_LENGTH`
  Constant Length – Keep the texture at a constant length regardless of the length of each stroke.
- `FIT_STROKE`
  Stroke Length – Scale the texture to fit the length of each stroke.

**Type:**

Literal[‘CONSTANT_LENGTH’, ‘FIT_STROKE’]

<a id="bpy.types.GreasePencilTextureModifier.invert_layer_filter"></a>

#### bpy.types.GreasePencilTextureModifier.invert_layer_filter

Invert layer filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilTextureModifier.invert_layer_pass_filter"></a>

#### bpy.types.GreasePencilTextureModifier.invert_layer_pass_filter

Invert layer pass filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilTextureModifier.invert_material_filter"></a>

#### bpy.types.GreasePencilTextureModifier.invert_material_filter

Invert material filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilTextureModifier.invert_material_pass_filter"></a>

#### bpy.types.GreasePencilTextureModifier.invert_material_pass_filter

Invert material pass filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilTextureModifier.layer_pass_filter"></a>

#### bpy.types.GreasePencilTextureModifier.layer_pass_filter

Layer pass filter (in [0, 100], default 0)

**Type:**

int

<a id="bpy.types.GreasePencilTextureModifier.material_filter"></a>

#### bpy.types.GreasePencilTextureModifier.material_filter

Material used for filtering

**Type:**

[`Material`](bpy.types.Material.md#bpy.types.Material "bpy.types.Material") | None

<a id="bpy.types.GreasePencilTextureModifier.material_pass_filter"></a>

#### bpy.types.GreasePencilTextureModifier.material_pass_filter

Material pass (in [0, 100], default 0)

**Type:**

int

<a id="bpy.types.GreasePencilTextureModifier.mode"></a>

#### bpy.types.GreasePencilTextureModifier.mode

(default `'STROKE'`)

- `STROKE`
  Stroke – Manipulate only stroke texture coordinates.
- `FILL`
  Fill – Manipulate only fill texture coordinates.
- `STROKE_AND_FILL`
  Stroke & Fill – Manipulate both stroke and fill texture coordinates.

**Type:**

Literal[‘STROKE’, ‘FILL’, ‘STROKE_AND_FILL’]

<a id="bpy.types.GreasePencilTextureModifier.open_influence_panel"></a>

#### bpy.types.GreasePencilTextureModifier.open_influence_panel

(default False)

**Type:**

bool

<a id="bpy.types.GreasePencilTextureModifier.tree_node_filter"></a>

#### bpy.types.GreasePencilTextureModifier.tree_node_filter

Layer name (default “”, never None)

**Type:**

str

<a id="bpy.types.GreasePencilTextureModifier.use_layer_group_filter"></a>

#### bpy.types.GreasePencilTextureModifier.use_layer_group_filter

Filter by layer group name (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilTextureModifier.use_layer_pass_filter"></a>

#### bpy.types.GreasePencilTextureModifier.use_layer_pass_filter

Use layer pass filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilTextureModifier.use_material_pass_filter"></a>

#### bpy.types.GreasePencilTextureModifier.use_material_pass_filter

Use material pass filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilTextureModifier.uv_offset"></a>

#### bpy.types.GreasePencilTextureModifier.uv_offset

Offset value to add to stroke UVs (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.GreasePencilTextureModifier.uv_scale"></a>

#### bpy.types.GreasePencilTextureModifier.uv_scale

Factor to scale the UVs (in [0, inf], default 1.0)

**Type:**

float

<a id="bpy.types.GreasePencilTextureModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.GreasePencilTextureModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.GreasePencilTextureModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.GreasePencilTextureModifier.bl_rna_get_subclass_py(id, default=None, /)

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
