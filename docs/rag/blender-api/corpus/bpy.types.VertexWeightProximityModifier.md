<!-- source: Blender Python API reference 5.2 / bpy.types.VertexWeightProximityModifier.html -->

<a id="vertexweightproximitymodifier-modifier"></a>

# VertexWeightProximityModifier(Modifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Modifier`](bpy.types.Modifier.md#bpy.types.Modifier "bpy.types.Modifier")

<a id="bpy.types.VertexWeightProximityModifier"></a>

### class bpy.types.VertexWeightProximityModifier(Modifier)

Set the weights of vertices in a group from a target object’s distance

<a id="bpy.types.VertexWeightProximityModifier.falloff_type"></a>

#### bpy.types.VertexWeightProximityModifier.falloff_type

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

<a id="bpy.types.VertexWeightProximityModifier.invert_falloff"></a>

#### bpy.types.VertexWeightProximityModifier.invert_falloff

Invert the resulting falloff weight (default False)

**Type:**

bool

<a id="bpy.types.VertexWeightProximityModifier.invert_mask_vertex_group"></a>

#### bpy.types.VertexWeightProximityModifier.invert_mask_vertex_group

Invert vertex group mask influence (default False)

**Type:**

bool

<a id="bpy.types.VertexWeightProximityModifier.map_curve"></a>

#### bpy.types.VertexWeightProximityModifier.map_curve

Custom mapping curve (readonly)

**Type:**

[`CurveMapping`](bpy.types.CurveMapping.md#bpy.types.CurveMapping "bpy.types.CurveMapping") | None

<a id="bpy.types.VertexWeightProximityModifier.mask_constant"></a>

#### bpy.types.VertexWeightProximityModifier.mask_constant

Global influence of current modifications on vgroup (in [-inf, inf], default 1.0)

**Type:**

float

<a id="bpy.types.VertexWeightProximityModifier.mask_tex_map_bone"></a>

#### bpy.types.VertexWeightProximityModifier.mask_tex_map_bone

Which bone to take texture coordinates from (default “”, never None)

**Type:**

str

<a id="bpy.types.VertexWeightProximityModifier.mask_tex_map_object"></a>

#### bpy.types.VertexWeightProximityModifier.mask_tex_map_object

Which object to take texture coordinates from

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.VertexWeightProximityModifier.mask_tex_mapping"></a>

#### bpy.types.VertexWeightProximityModifier.mask_tex_mapping

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

<a id="bpy.types.VertexWeightProximityModifier.mask_tex_use_channel"></a>

#### bpy.types.VertexWeightProximityModifier.mask_tex_use_channel

Which texture channel to use for masking (default `'INT'`)

**Type:**

Literal[‘INT’, ‘RED’, ‘GREEN’, ‘BLUE’, ‘HUE’, ‘SAT’, ‘VAL’, ‘ALPHA’]

<a id="bpy.types.VertexWeightProximityModifier.mask_tex_uv_layer"></a>

#### bpy.types.VertexWeightProximityModifier.mask_tex_uv_layer

UV map name (default “”, never None)

**Type:**

str

<a id="bpy.types.VertexWeightProximityModifier.mask_texture"></a>

#### bpy.types.VertexWeightProximityModifier.mask_texture

Masking texture

**Type:**

[`Texture`](bpy.types.Texture.md#bpy.types.Texture "bpy.types.Texture") | None

<a id="bpy.types.VertexWeightProximityModifier.mask_vertex_group"></a>

#### bpy.types.VertexWeightProximityModifier.mask_vertex_group

Masking vertex group name (default “”, never None)

**Type:**

str

<a id="bpy.types.VertexWeightProximityModifier.max_dist"></a>

#### bpy.types.VertexWeightProximityModifier.max_dist

Distance mapping to weight 1.0 (in [0, inf], default 1.0)

**Type:**

float

<a id="bpy.types.VertexWeightProximityModifier.min_dist"></a>

#### bpy.types.VertexWeightProximityModifier.min_dist

Distance mapping to weight 0.0 (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.VertexWeightProximityModifier.normalize"></a>

#### bpy.types.VertexWeightProximityModifier.normalize

Normalize the resulting weights (otherwise they are only clamped within 0.0 to 1.0 range) (default False)

**Type:**

bool

<a id="bpy.types.VertexWeightProximityModifier.proximity_geometry"></a>

#### bpy.types.VertexWeightProximityModifier.proximity_geometry

Use the shortest computed distance to target object’s geometry as weight (default {`'FACE'`})

- `VERTEX`
  Vertex – Compute distance to nearest vertex.
- `EDGE`
  Edge – Compute distance to nearest edge.
- `FACE`
  Face – Compute distance to nearest face.

**Type:**

set[Literal[‘VERTEX’, ‘EDGE’, ‘FACE’]]

<a id="bpy.types.VertexWeightProximityModifier.proximity_mode"></a>

#### bpy.types.VertexWeightProximityModifier.proximity_mode

Which distances to target object to use (default `'GEOMETRY'`)

- `OBJECT`
  Object – Use distance between affected and target objects.
- `GEOMETRY`
  Geometry – Use distance between affected object’s vertices and target object, or target object’s geometry.

**Type:**

Literal[‘OBJECT’, ‘GEOMETRY’]

<a id="bpy.types.VertexWeightProximityModifier.target"></a>

#### bpy.types.VertexWeightProximityModifier.target

Object to calculate vertices distances from

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.VertexWeightProximityModifier.vertex_group"></a>

#### bpy.types.VertexWeightProximityModifier.vertex_group

Vertex group name (default “”, never None)

**Type:**

str

<a id="bpy.types.VertexWeightProximityModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.VertexWeightProximityModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.VertexWeightProximityModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.VertexWeightProximityModifier.bl_rna_get_subclass_py(id, default=None, /)

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
