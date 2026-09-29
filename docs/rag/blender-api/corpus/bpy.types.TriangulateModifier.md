<!-- source: Blender Python API reference 5.2 / bpy.types.TriangulateModifier.html -->

<a id="triangulatemodifier-modifier"></a>

# TriangulateModifier(Modifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Modifier`](bpy.types.Modifier.md#bpy.types.Modifier "bpy.types.Modifier")

<a id="bpy.types.TriangulateModifier"></a>

### class bpy.types.TriangulateModifier(Modifier)

Triangulate Mesh

<a id="bpy.types.TriangulateModifier.keep_custom_normals"></a>

#### bpy.types.TriangulateModifier.keep_custom_normals

Try to preserve custom normals.
Warning: Depending on chosen triangulation method, shading may not be fully preserved, “Fixed” method usually gives the best result here

(default False)

**Type:**

bool

<a id="bpy.types.TriangulateModifier.min_vertices"></a>

#### bpy.types.TriangulateModifier.min_vertices

Triangulate only polygons with vertex count greater than or equal to this number (in [4, inf], default 4)

**Type:**

int

<a id="bpy.types.TriangulateModifier.ngon_method"></a>

#### bpy.types.TriangulateModifier.ngon_method

Method for splitting the n-gons into triangles (default `'BEAUTY'`)

**Type:**

Literal[[Modifier Triangulate Ngon Method Items](bpy_types_enum_items/modifier_triangulate_ngon_method_items.md#rna-enum-modifier-triangulate-ngon-method-items)]

<a id="bpy.types.TriangulateModifier.quad_method"></a>

#### bpy.types.TriangulateModifier.quad_method

Method for splitting the quads into triangles (default `'SHORTEST_DIAGONAL'`)

**Type:**

Literal[[Modifier Triangulate Quad Method Items](bpy_types_enum_items/modifier_triangulate_quad_method_items.md#rna-enum-modifier-triangulate-quad-method-items)]

<a id="bpy.types.TriangulateModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.TriangulateModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.TriangulateModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.TriangulateModifier.bl_rna_get_subclass_py(id, default=None, /)

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
