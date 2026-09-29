<!-- source: Blender Python API reference 5.2 / bpy.types.LaplacianSmoothModifier.html -->

<a id="laplaciansmoothmodifier-modifier"></a>

# LaplacianSmoothModifier(Modifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Modifier`](bpy.types.Modifier.md#bpy.types.Modifier "bpy.types.Modifier")

<a id="bpy.types.LaplacianSmoothModifier"></a>

### class bpy.types.LaplacianSmoothModifier(Modifier)

Smoothing effect modifier

<a id="bpy.types.LaplacianSmoothModifier.invert_vertex_group"></a>

#### bpy.types.LaplacianSmoothModifier.invert_vertex_group

Invert vertex group influence (default False)

**Type:**

bool

<a id="bpy.types.LaplacianSmoothModifier.iterations"></a>

#### bpy.types.LaplacianSmoothModifier.iterations

(in [0, 32767], default 1)

**Type:**

int

<a id="bpy.types.LaplacianSmoothModifier.lambda_border"></a>

#### bpy.types.LaplacianSmoothModifier.lambda_border

Lambda factor in border (in [-inf, inf], default 0.01)

**Type:**

float

<a id="bpy.types.LaplacianSmoothModifier.lambda_factor"></a>

#### bpy.types.LaplacianSmoothModifier.lambda_factor

Smooth effect factor (in [-inf, inf], default 0.01)

**Type:**

float

<a id="bpy.types.LaplacianSmoothModifier.use_normalized"></a>

#### bpy.types.LaplacianSmoothModifier.use_normalized

Improve and stabilize the enhanced shape (default True)

**Type:**

bool

<a id="bpy.types.LaplacianSmoothModifier.use_volume_preserve"></a>

#### bpy.types.LaplacianSmoothModifier.use_volume_preserve

Apply volume preservation after smooth (default True)

**Type:**

bool

<a id="bpy.types.LaplacianSmoothModifier.use_x"></a>

#### bpy.types.LaplacianSmoothModifier.use_x

Smooth object along X axis (default True)

**Type:**

bool

<a id="bpy.types.LaplacianSmoothModifier.use_y"></a>

#### bpy.types.LaplacianSmoothModifier.use_y

Smooth object along Y axis (default True)

**Type:**

bool

<a id="bpy.types.LaplacianSmoothModifier.use_z"></a>

#### bpy.types.LaplacianSmoothModifier.use_z

Smooth object along Z axis (default True)

**Type:**

bool

<a id="bpy.types.LaplacianSmoothModifier.vertex_group"></a>

#### bpy.types.LaplacianSmoothModifier.vertex_group

Name of Vertex Group which determines influence of modifier per point (default “”, never None)

**Type:**

str

<a id="bpy.types.LaplacianSmoothModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.LaplacianSmoothModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.LaplacianSmoothModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.LaplacianSmoothModifier.bl_rna_get_subclass_py(id, default=None, /)

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
