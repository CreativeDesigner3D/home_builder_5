<!-- source: Blender Python API reference 5.2 / bpy.types.NormalEditModifier.html -->

<a id="normaleditmodifier-modifier"></a>

# NormalEditModifier(Modifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Modifier`](bpy.types.Modifier.md#bpy.types.Modifier "bpy.types.Modifier")

<a id="bpy.types.NormalEditModifier"></a>

### class bpy.types.NormalEditModifier(Modifier)

Modifier affecting/generating custom normals

<a id="bpy.types.NormalEditModifier.invert_vertex_group"></a>

#### bpy.types.NormalEditModifier.invert_vertex_group

Invert vertex group influence (default False)

**Type:**

bool

<a id="bpy.types.NormalEditModifier.mix_factor"></a>

#### bpy.types.NormalEditModifier.mix_factor

How much of generated normals to mix with existing ones (in [0, 1], default 1.0)

**Type:**

float

<a id="bpy.types.NormalEditModifier.mix_limit"></a>

#### bpy.types.NormalEditModifier.mix_limit

Maximum angle between old and new normals (in [0, 3.14159], default 3.14159)

**Type:**

float

<a id="bpy.types.NormalEditModifier.mix_mode"></a>

#### bpy.types.NormalEditModifier.mix_mode

How to mix generated normals with existing ones (default `'COPY'`)

- `COPY`
  Copy – Copy new normals (overwrite existing).
- `ADD`
  Add – Copy sum of new and old normals.
- `SUB`
  Subtract – Copy new normals minus old normals.
- `MUL`
  Multiply – Copy product of old and new normals (not cross product).

**Type:**

Literal[‘COPY’, ‘ADD’, ‘SUB’, ‘MUL’]

<a id="bpy.types.NormalEditModifier.mode"></a>

#### bpy.types.NormalEditModifier.mode

How to affect (generate) normals (default `'RADIAL'`)

- `RADIAL`
  Radial – From an ellipsoid (shape defined by the boundbox’s dimensions, target is optional).
- `DIRECTIONAL`
  Directional – Normals ‘track’ (point to) the target object.

**Type:**

Literal[‘RADIAL’, ‘DIRECTIONAL’]

<a id="bpy.types.NormalEditModifier.no_polynors_fix"></a>

#### bpy.types.NormalEditModifier.no_polynors_fix

Do not flip polygons when their normals are not consistent with their newly computed custom vertex normals (default False)

**Type:**

bool

<a id="bpy.types.NormalEditModifier.offset"></a>

#### bpy.types.NormalEditModifier.offset

Offset from object’s center (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.NormalEditModifier.target"></a>

#### bpy.types.NormalEditModifier.target

Target object used to affect normals

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.NormalEditModifier.use_direction_parallel"></a>

#### bpy.types.NormalEditModifier.use_direction_parallel

Use same direction for all normals, from origin to target’s center (Directional mode only) (default True)

**Type:**

bool

<a id="bpy.types.NormalEditModifier.vertex_group"></a>

#### bpy.types.NormalEditModifier.vertex_group

Vertex group name for selecting/weighting the affected areas (default “”, never None)

**Type:**

str

<a id="bpy.types.NormalEditModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.NormalEditModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.NormalEditModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.NormalEditModifier.bl_rna_get_subclass_py(id, default=None, /)

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
