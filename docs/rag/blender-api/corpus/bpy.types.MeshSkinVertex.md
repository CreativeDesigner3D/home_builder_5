<!-- source: Blender Python API reference 5.2 / bpy.types.MeshSkinVertex.html -->

<a id="meshskinvertex-bpy-struct"></a>

# MeshSkinVertex(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.MeshSkinVertex"></a>

### class bpy.types.MeshSkinVertex(bpy_struct)

Per-vertex skin data for use with the Skin modifier

<a id="bpy.types.MeshSkinVertex.radius"></a>

#### bpy.types.MeshSkinVertex.radius

Radius of the skin (array of 2 items, in [0, inf], default (0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.MeshSkinVertex.use_loose"></a>

#### bpy.types.MeshSkinVertex.use_loose

If vertex has multiple adjacent edges, it is hulled to them directly (default False)

**Type:**

bool

<a id="bpy.types.MeshSkinVertex.use_root"></a>

#### bpy.types.MeshSkinVertex.use_root

Vertex is a root for rotation calculations and armature generation, setting this flag does not clear other roots in the same mesh island (default False)

**Type:**

bool

<a id="bpy.types.MeshSkinVertex.bl_rna_get_subclass"></a>

#### classmethod bpy.types.MeshSkinVertex.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.MeshSkinVertex.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.MeshSkinVertex.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values

<a id="references"></a>

## References

|  |  |
| --- | --- |
| - [`MeshSkinVertexLayer.data`](bpy.types.MeshSkinVertexLayer.md#bpy.types.MeshSkinVertexLayer.data "bpy.types.MeshSkinVertexLayer.data") |  |
