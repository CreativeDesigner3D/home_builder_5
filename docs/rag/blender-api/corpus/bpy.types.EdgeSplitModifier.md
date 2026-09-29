<!-- source: Blender Python API reference 5.2 / bpy.types.EdgeSplitModifier.html -->

<a id="edgesplitmodifier-modifier"></a>

# EdgeSplitModifier(Modifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Modifier`](bpy.types.Modifier.md#bpy.types.Modifier "bpy.types.Modifier")

<a id="bpy.types.EdgeSplitModifier"></a>

### class bpy.types.EdgeSplitModifier(Modifier)

Edge splitting modifier to create sharp edges

<a id="bpy.types.EdgeSplitModifier.split_angle"></a>

#### bpy.types.EdgeSplitModifier.split_angle

Angle above which to split edges (in [0, 3.14159], default 0.523599)

**Type:**

float

<a id="bpy.types.EdgeSplitModifier.use_edge_angle"></a>

#### bpy.types.EdgeSplitModifier.use_edge_angle

Split edges with high angle between faces (default True)

**Type:**

bool

<a id="bpy.types.EdgeSplitModifier.use_edge_sharp"></a>

#### bpy.types.EdgeSplitModifier.use_edge_sharp

Split edges that are marked as sharp (default True)

**Type:**

bool

<a id="bpy.types.EdgeSplitModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.EdgeSplitModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.EdgeSplitModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.EdgeSplitModifier.bl_rna_get_subclass_py(id, default=None, /)

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
