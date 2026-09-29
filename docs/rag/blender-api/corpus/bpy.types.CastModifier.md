<!-- source: Blender Python API reference 5.2 / bpy.types.CastModifier.html -->

<a id="castmodifier-modifier"></a>

# CastModifier(Modifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Modifier`](bpy.types.Modifier.md#bpy.types.Modifier "bpy.types.Modifier")

<a id="bpy.types.CastModifier"></a>

### class bpy.types.CastModifier(Modifier)

Modifier to cast to other shapes

<a id="bpy.types.CastModifier.cast_type"></a>

#### bpy.types.CastModifier.cast_type

Target object shape (default `'SPHERE'`)

**Type:**

Literal[‘SPHERE’, ‘CYLINDER’, ‘CUBOID’]

<a id="bpy.types.CastModifier.factor"></a>

#### bpy.types.CastModifier.factor

(in [-inf, inf], default 0.5)

**Type:**

float

<a id="bpy.types.CastModifier.invert_vertex_group"></a>

#### bpy.types.CastModifier.invert_vertex_group

Invert vertex group influence (default False)

**Type:**

bool

<a id="bpy.types.CastModifier.object"></a>

#### bpy.types.CastModifier.object

Control object: if available, its location determines the center of the effect

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.CastModifier.radius"></a>

#### bpy.types.CastModifier.radius

Only deform vertices within this distance from the center of the effect (leave as 0 for infinite.) (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.CastModifier.size"></a>

#### bpy.types.CastModifier.size

Size of projection shape (leave as 0 for auto) (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.CastModifier.use_radius_as_size"></a>

#### bpy.types.CastModifier.use_radius_as_size

Use radius as size of projection shape (0 = auto) (default True)

**Type:**

bool

<a id="bpy.types.CastModifier.use_transform"></a>

#### bpy.types.CastModifier.use_transform

Use object transform to control projection shape (default False)

**Type:**

bool

<a id="bpy.types.CastModifier.use_x"></a>

#### bpy.types.CastModifier.use_x

(default True)

**Type:**

bool

<a id="bpy.types.CastModifier.use_y"></a>

#### bpy.types.CastModifier.use_y

(default True)

**Type:**

bool

<a id="bpy.types.CastModifier.use_z"></a>

#### bpy.types.CastModifier.use_z

(default True)

**Type:**

bool

<a id="bpy.types.CastModifier.vertex_group"></a>

#### bpy.types.CastModifier.vertex_group

Vertex group name (default “”, never None)

**Type:**

str

<a id="bpy.types.CastModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.CastModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.CastModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.CastModifier.bl_rna_get_subclass_py(id, default=None, /)

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
