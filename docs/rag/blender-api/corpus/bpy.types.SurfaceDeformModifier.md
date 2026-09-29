<!-- source: Blender Python API reference 5.2 / bpy.types.SurfaceDeformModifier.html -->

<a id="surfacedeformmodifier-modifier"></a>

# SurfaceDeformModifier(Modifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Modifier`](bpy.types.Modifier.md#bpy.types.Modifier "bpy.types.Modifier")

<a id="bpy.types.SurfaceDeformModifier"></a>

### class bpy.types.SurfaceDeformModifier(Modifier)

<a id="bpy.types.SurfaceDeformModifier.falloff"></a>

#### bpy.types.SurfaceDeformModifier.falloff

Controls how much nearby polygons influence deformation (in [2, 16], default 4.0)

**Type:**

float

<a id="bpy.types.SurfaceDeformModifier.invert_vertex_group"></a>

#### bpy.types.SurfaceDeformModifier.invert_vertex_group

Invert vertex group influence (default False)

**Type:**

bool

<a id="bpy.types.SurfaceDeformModifier.is_bound"></a>

#### bpy.types.SurfaceDeformModifier.is_bound

Whether geometry has been bound to target mesh (default False, readonly)

**Type:**

bool

<a id="bpy.types.SurfaceDeformModifier.strength"></a>

#### bpy.types.SurfaceDeformModifier.strength

Strength of modifier deformations (in [-100, 100], default 1.0)

**Type:**

float

<a id="bpy.types.SurfaceDeformModifier.target"></a>

#### bpy.types.SurfaceDeformModifier.target

Mesh object to deform with

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.SurfaceDeformModifier.use_sparse_bind"></a>

#### bpy.types.SurfaceDeformModifier.use_sparse_bind

Only record binding data for vertices matching the vertex group at the time of bind (default False)

**Type:**

bool

<a id="bpy.types.SurfaceDeformModifier.vertex_group"></a>

#### bpy.types.SurfaceDeformModifier.vertex_group

Vertex group name for selecting/weighting the affected areas (default “”, never None)

**Type:**

str

<a id="bpy.types.SurfaceDeformModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.SurfaceDeformModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.SurfaceDeformModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.SurfaceDeformModifier.bl_rna_get_subclass_py(id, default=None, /)

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
