<!-- source: Blender Python API reference 5.2 / bpy.types.VertexWeightEditModifier.html -->

<a id="vertexweighteditmodifier-modifier"></a>

# VertexWeightEditModifier(Modifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Modifier`](bpy.types.Modifier.md#bpy.types.Modifier "bpy.types.Modifier")

<a id="bpy.types.VertexWeightEditModifier"></a>

### class bpy.types.VertexWeightEditModifier(Modifier)

Edit the weights of vertices in a group

<a id="bpy.types.VertexWeightEditModifier.add_threshold"></a>

#### bpy.types.VertexWeightEditModifier.add_threshold

Lower (inclusive) bound for a vertex’s weight to be added to the vgroup (in [-1000, 1000], default 0.01)

**Type:**

float

<a id="bpy.types.VertexWeightEditModifier.default_weight"></a>

#### bpy.types.VertexWeightEditModifier.default_weight

Default weight a vertex will have if it is not in the vgroup (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.VertexWeightEditModifier.falloff_type"></a>

#### bpy.types.VertexWeightEditModifier.falloff_type

How weights are mapped to their new values (default `'LINEAR'`)

- `LINEAR`
  Linear – Null action.
- `CURVE`
  Custom Curve.
- `SHARP`
  Sharp.
- `SMOOTH`
  Smooth.
- `ROOT`
  Root.
- `ICON_SPHERECURVE`
  Sphere.
- `RANDOM`
  Random.
- `STEP`
  Median Step – Map all values below 0.5 to 0.0, and all others to 1.0.

**Type:**

Literal[‘LINEAR’, ‘CURVE’, ‘SHARP’, ‘SMOOTH’, ‘ROOT’, ‘ICON_SPHERECURVE’, ‘RANDOM’, ‘STEP’]

<a id="bpy.types.VertexWeightEditModifier.invert_falloff"></a>

#### bpy.types.VertexWeightEditModifier.invert_falloff

Invert the resulting falloff weight (default False)

**Type:**

bool

<a id="bpy.types.VertexWeightEditModifier.invert_mask_vertex_group"></a>

#### bpy.types.VertexWeightEditModifier.invert_mask_vertex_group

Invert vertex group mask influence (default False)

**Type:**

bool

<a id="bpy.types.VertexWeightEditModifier.map_curve"></a>

#### bpy.types.VertexWeightEditModifier.map_curve

Custom mapping curve (readonly)

**Type:**

[`CurveMapping`](bpy.types.CurveMapping.md#bpy.types.CurveMapping "bpy.types.CurveMapping") | None

<a id="bpy.types.VertexWeightEditModifier.mask_constant"></a>

#### bpy.types.VertexWeightEditModifier.mask_constant

Global influence of current modifications on vgroup (in [-inf, inf], default 1.0)

**Type:**

float

<a id="bpy.types.VertexWeightEditModifier.mask_tex_map_bone"></a>

#### bpy.types.VertexWeightEditModifier.mask_tex_map_bone

Which bone to take texture coordinates from (default “”, never None)

**Type:**

str

<a id="bpy.types.VertexWeightEditModifier.mask_tex_map_object"></a>

#### bpy.types.VertexWeightEditModifier.mask_tex_map_object

Which object to take texture coordinates from

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.VertexWeightEditModifier.mask_tex_mapping"></a>

#### bpy.types.VertexWeightEditModifier.mask_tex_mapping

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

<a id="bpy.types.VertexWeightEditModifier.mask_tex_use_channel"></a>

#### bpy.types.VertexWeightEditModifier.mask_tex_use_channel

Which texture channel to use for masking (default `'INT'`)

**Type:**

Literal[‘INT’, ‘RED’, ‘GREEN’, ‘BLUE’, ‘HUE’, ‘SAT’, ‘VAL’, ‘ALPHA’]

<a id="bpy.types.VertexWeightEditModifier.mask_tex_uv_layer"></a>

#### bpy.types.VertexWeightEditModifier.mask_tex_uv_layer

UV map name (default “”, never None)

**Type:**

str

<a id="bpy.types.VertexWeightEditModifier.mask_texture"></a>

#### bpy.types.VertexWeightEditModifier.mask_texture

Masking texture

**Type:**

[`Texture`](bpy.types.Texture.md#bpy.types.Texture "bpy.types.Texture") | None

<a id="bpy.types.VertexWeightEditModifier.mask_vertex_group"></a>

#### bpy.types.VertexWeightEditModifier.mask_vertex_group

Masking vertex group name (default “”, never None)

**Type:**

str

<a id="bpy.types.VertexWeightEditModifier.normalize"></a>

#### bpy.types.VertexWeightEditModifier.normalize

Normalize the resulting weights (otherwise they are only clamped within 0.0 to 1.0 range) (default False)

**Type:**

bool

<a id="bpy.types.VertexWeightEditModifier.remove_threshold"></a>

#### bpy.types.VertexWeightEditModifier.remove_threshold

Upper (inclusive) bound for a vertex’s weight to be removed from the vgroup (in [-1000, 1000], default 0.01)

**Type:**

float

<a id="bpy.types.VertexWeightEditModifier.use_add"></a>

#### bpy.types.VertexWeightEditModifier.use_add

Add vertices with weight over threshold to vgroup (default False)

**Type:**

bool

<a id="bpy.types.VertexWeightEditModifier.use_remove"></a>

#### bpy.types.VertexWeightEditModifier.use_remove

Remove vertices with weight below threshold from vgroup (default False)

**Type:**

bool

<a id="bpy.types.VertexWeightEditModifier.vertex_group"></a>

#### bpy.types.VertexWeightEditModifier.vertex_group

Vertex group name (default “”, never None)

**Type:**

str

<a id="bpy.types.VertexWeightEditModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.VertexWeightEditModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.VertexWeightEditModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.VertexWeightEditModifier.bl_rna_get_subclass_py(id, default=None, /)

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
