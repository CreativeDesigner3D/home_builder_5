<!-- source: Blender Python API reference 5.2 / bpy.types.WireframeModifier.html -->

<a id="wireframemodifier-modifier"></a>

# WireframeModifier(Modifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Modifier`](bpy.types.Modifier.md#bpy.types.Modifier "bpy.types.Modifier")

<a id="bpy.types.WireframeModifier"></a>

### class bpy.types.WireframeModifier(Modifier)

Wireframe effect modifier

<a id="bpy.types.WireframeModifier.crease_weight"></a>

#### bpy.types.WireframeModifier.crease_weight

Crease weight (if active) (in [-inf, inf], default 1.0)

**Type:**

float

<a id="bpy.types.WireframeModifier.invert_vertex_group"></a>

#### bpy.types.WireframeModifier.invert_vertex_group

Invert vertex group influence (default False)

**Type:**

bool

<a id="bpy.types.WireframeModifier.material_offset"></a>

#### bpy.types.WireframeModifier.material_offset

Offset material index of generated faces (in [-32768, 32767], default 0)

**Type:**

int

<a id="bpy.types.WireframeModifier.offset"></a>

#### bpy.types.WireframeModifier.offset

Offset the thickness from the center (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.WireframeModifier.thickness"></a>

#### bpy.types.WireframeModifier.thickness

Thickness factor (in [-inf, inf], default 0.02)

**Type:**

float

<a id="bpy.types.WireframeModifier.thickness_vertex_group"></a>

#### bpy.types.WireframeModifier.thickness_vertex_group

Thickness factor to use for zero vertex group influence (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.WireframeModifier.use_boundary"></a>

#### bpy.types.WireframeModifier.use_boundary

Support face boundaries (default False)

**Type:**

bool

<a id="bpy.types.WireframeModifier.use_crease"></a>

#### bpy.types.WireframeModifier.use_crease

Crease hub edges for improved subdivision surface (default False)

**Type:**

bool

<a id="bpy.types.WireframeModifier.use_even_offset"></a>

#### bpy.types.WireframeModifier.use_even_offset

Scale the offset to give more even thickness (default True)

**Type:**

bool

<a id="bpy.types.WireframeModifier.use_relative_offset"></a>

#### bpy.types.WireframeModifier.use_relative_offset

Scale the offset by surrounding geometry (default False)

**Type:**

bool

<a id="bpy.types.WireframeModifier.use_replace"></a>

#### bpy.types.WireframeModifier.use_replace

Remove original geometry (default True)

**Type:**

bool

<a id="bpy.types.WireframeModifier.vertex_group"></a>

#### bpy.types.WireframeModifier.vertex_group

Vertex group name for selecting the affected areas (default “”, never None)

**Type:**

str

<a id="bpy.types.WireframeModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.WireframeModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.WireframeModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.WireframeModifier.bl_rna_get_subclass_py(id, default=None, /)

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
