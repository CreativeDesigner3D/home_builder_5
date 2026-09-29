<!-- source: Blender Python API reference 5.2 / bpy.types.UVWarpModifier.html -->

<a id="uvwarpmodifier-modifier"></a>

# UVWarpModifier(Modifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Modifier`](bpy.types.Modifier.md#bpy.types.Modifier "bpy.types.Modifier")

<a id="bpy.types.UVWarpModifier"></a>

### class bpy.types.UVWarpModifier(Modifier)

Add target position to UV coordinates

<a id="bpy.types.UVWarpModifier.axis_u"></a>

#### bpy.types.UVWarpModifier.axis_u

Pole axis for rotation (default `'X'`)

**Type:**

Literal[[Axis Xyz Items](bpy_types_enum_items/axis_xyz_items.md#rna-enum-axis-xyz-items)]

<a id="bpy.types.UVWarpModifier.axis_v"></a>

#### bpy.types.UVWarpModifier.axis_v

Pole axis for rotation (default `'Y'`)

**Type:**

Literal[[Axis Xyz Items](bpy_types_enum_items/axis_xyz_items.md#rna-enum-axis-xyz-items)]

<a id="bpy.types.UVWarpModifier.bone_from"></a>

#### bpy.types.UVWarpModifier.bone_from

Bone defining offset (default “”, never None)

**Type:**

str

<a id="bpy.types.UVWarpModifier.bone_to"></a>

#### bpy.types.UVWarpModifier.bone_to

Bone defining offset (default “”, never None)

**Type:**

str

<a id="bpy.types.UVWarpModifier.center"></a>

#### bpy.types.UVWarpModifier.center

Center point for rotate/scale (array of 2 items, in [-inf, inf], default (0.5, 0.5))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.UVWarpModifier.invert_vertex_group"></a>

#### bpy.types.UVWarpModifier.invert_vertex_group

Invert vertex group influence (default False)

**Type:**

bool

<a id="bpy.types.UVWarpModifier.object_from"></a>

#### bpy.types.UVWarpModifier.object_from

Object defining offset

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.UVWarpModifier.object_to"></a>

#### bpy.types.UVWarpModifier.object_to

Object defining offset

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.UVWarpModifier.offset"></a>

#### bpy.types.UVWarpModifier.offset

2D Offset for the warp (array of 2 items, in [-inf, inf], default (0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.UVWarpModifier.rotation"></a>

#### bpy.types.UVWarpModifier.rotation

2D Rotation for the warp (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.UVWarpModifier.scale"></a>

#### bpy.types.UVWarpModifier.scale

2D Scale for the warp (array of 2 items, in [-inf, inf], default (1.0, 1.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.UVWarpModifier.uv_layer"></a>

#### bpy.types.UVWarpModifier.uv_layer

UV map name (default “”, never None)

**Type:**

str

<a id="bpy.types.UVWarpModifier.vertex_group"></a>

#### bpy.types.UVWarpModifier.vertex_group

Vertex group name (default “”, never None)

**Type:**

str

<a id="bpy.types.UVWarpModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.UVWarpModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.UVWarpModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.UVWarpModifier.bl_rna_get_subclass_py(id, default=None, /)

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
