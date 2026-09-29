<!-- source: Blender Python API reference 5.2 / bpy.types.VertexWeightMixModifier.html -->

<a id="vertexweightmixmodifier-modifier"></a>

# VertexWeightMixModifier(Modifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Modifier`](bpy.types.Modifier.md#bpy.types.Modifier "bpy.types.Modifier")

<a id="bpy.types.VertexWeightMixModifier"></a>

### class bpy.types.VertexWeightMixModifier(Modifier)

Mix the weights of two vertex groups

<a id="bpy.types.VertexWeightMixModifier.default_weight_a"></a>

#### bpy.types.VertexWeightMixModifier.default_weight_a

Default weight a vertex will have if it is not in the first A vgroup (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.VertexWeightMixModifier.default_weight_b"></a>

#### bpy.types.VertexWeightMixModifier.default_weight_b

Default weight a vertex will have if it is not in the second B vgroup (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.VertexWeightMixModifier.invert_mask_vertex_group"></a>

#### bpy.types.VertexWeightMixModifier.invert_mask_vertex_group

Invert vertex group mask influence (default False)

**Type:**

bool

<a id="bpy.types.VertexWeightMixModifier.invert_vertex_group_a"></a>

#### bpy.types.VertexWeightMixModifier.invert_vertex_group_a

Invert the influence of vertex group A (default False)

**Type:**

bool

<a id="bpy.types.VertexWeightMixModifier.invert_vertex_group_b"></a>

#### bpy.types.VertexWeightMixModifier.invert_vertex_group_b

Invert the influence of vertex group B (default False)

**Type:**

bool

<a id="bpy.types.VertexWeightMixModifier.mask_constant"></a>

#### bpy.types.VertexWeightMixModifier.mask_constant

Global influence of current modifications on vgroup (in [-inf, inf], default 1.0)

**Type:**

float

<a id="bpy.types.VertexWeightMixModifier.mask_tex_map_bone"></a>

#### bpy.types.VertexWeightMixModifier.mask_tex_map_bone

Which bone to take texture coordinates from (default “”, never None)

**Type:**

str

<a id="bpy.types.VertexWeightMixModifier.mask_tex_map_object"></a>

#### bpy.types.VertexWeightMixModifier.mask_tex_map_object

Which object to take texture coordinates from

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.VertexWeightMixModifier.mask_tex_mapping"></a>

#### bpy.types.VertexWeightMixModifier.mask_tex_mapping

Which texture coordinates to use for mapping (default `'LOCAL'`)

- `LOCAL`
  Local – Use local generated coordinates.
- `GLOBAL`
  Global – Use global coordinates.
- `OBJECT`
  Object – Use local generated coordinates of another object.
- `UV`
  UV – Use coordinates from a UV layer.

**Type:**

Literal[‘LOCAL’, ‘GLOBAL’, ‘OBJECT’, ‘UV’]

<a id="bpy.types.VertexWeightMixModifier.mask_tex_use_channel"></a>

#### bpy.types.VertexWeightMixModifier.mask_tex_use_channel

Which texture channel to use for masking (default `'INT'`)

**Type:**

Literal[‘INT’, ‘RED’, ‘GREEN’, ‘BLUE’, ‘HUE’, ‘SAT’, ‘VAL’, ‘ALPHA’]

<a id="bpy.types.VertexWeightMixModifier.mask_tex_uv_layer"></a>

#### bpy.types.VertexWeightMixModifier.mask_tex_uv_layer

UV map name (default “”, never None)

**Type:**

str

<a id="bpy.types.VertexWeightMixModifier.mask_texture"></a>

#### bpy.types.VertexWeightMixModifier.mask_texture

Masking texture

**Type:**

[`Texture`](bpy.types.Texture.md#bpy.types.Texture "bpy.types.Texture") | None

<a id="bpy.types.VertexWeightMixModifier.mask_vertex_group"></a>

#### bpy.types.VertexWeightMixModifier.mask_vertex_group

Masking vertex group name (default “”, never None)

**Type:**

str

<a id="bpy.types.VertexWeightMixModifier.mix_mode"></a>

#### bpy.types.VertexWeightMixModifier.mix_mode

How weights from vgroup B affect weights of vgroup A (default `'SET'`)

- `SET`
  Replace – Replace VGroup A’s weights by VGroup B’s ones.
- `ADD`
  Add – Add VGroup B’s weights to VGroup A’s ones.
- `SUB`
  Subtract – Subtract VGroup B’s weights from VGroup A’s ones.
- `MUL`
  Multiply – Multiply VGroup A’s weights by VGroup B’s ones.
- `DIV`
  Divide – Divide VGroup A’s weights by VGroup B’s ones.
- `DIF`
  Difference – Difference between VGroup A’s and VGroup B’s weights.
- `AVG`
  Average – Average value of VGroup A’s and VGroup B’s weights.
- `MIN`
  Minimum – Minimum of VGroup A’s and VGroup B’s weights.
- `MAX`
  Maximum – Maximum of VGroup A’s and VGroup B’s weights.

**Type:**

Literal[‘SET’, ‘ADD’, ‘SUB’, ‘MUL’, ‘DIV’, ‘DIF’, ‘AVG’, ‘MIN’, ‘MAX’]

<a id="bpy.types.VertexWeightMixModifier.mix_set"></a>

#### bpy.types.VertexWeightMixModifier.mix_set

Which vertices should be affected (default `'AND'`)

- `ALL`
  All – Affect all vertices (might add some to VGroup A).
- `A`
  VGroup A – Affect vertices in VGroup A.
- `B`
  VGroup B – Affect vertices in VGroup B (might add some to VGroup A).
- `OR`
  VGroup A or B – Affect vertices in at least one of both VGroups (might add some to VGroup A).
- `AND`
  VGroup A and B – Affect vertices in both groups.

**Type:**

Literal[‘ALL’, ‘A’, ‘B’, ‘OR’, ‘AND’]

<a id="bpy.types.VertexWeightMixModifier.normalize"></a>

#### bpy.types.VertexWeightMixModifier.normalize

Normalize the resulting weights (otherwise they are only clamped within 0.0 to 1.0 range) (default False)

**Type:**

bool

<a id="bpy.types.VertexWeightMixModifier.vertex_group_a"></a>

#### bpy.types.VertexWeightMixModifier.vertex_group_a

First vertex group name (default “”, never None)

**Type:**

str

<a id="bpy.types.VertexWeightMixModifier.vertex_group_b"></a>

#### bpy.types.VertexWeightMixModifier.vertex_group_b

Second vertex group name (default “”, never None)

**Type:**

str

<a id="bpy.types.VertexWeightMixModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.VertexWeightMixModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.VertexWeightMixModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.VertexWeightMixModifier.bl_rna_get_subclass_py(id, default=None, /)

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
