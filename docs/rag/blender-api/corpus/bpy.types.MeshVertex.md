<!-- source: Blender Python API reference 5.2 / bpy.types.MeshVertex.html -->

<a id="meshvertex-bpy-struct"></a>

# MeshVertex(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.MeshVertex"></a>

### class bpy.types.MeshVertex(bpy_struct)

Vertex in a Mesh data-block

<a id="bpy.types.MeshVertex.co"></a>

#### bpy.types.MeshVertex.co

(array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.MeshVertex.groups"></a>

#### bpy.types.MeshVertex.groups

Weights for the vertex groups this vertex is member of (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`VertexGroupElement`](bpy.types.VertexGroupElement.md#bpy.types.VertexGroupElement "bpy.types.VertexGroupElement")]

<a id="bpy.types.MeshVertex.hide"></a>

#### bpy.types.MeshVertex.hide

(default False)

**Type:**

bool

<a id="bpy.types.MeshVertex.index"></a>

#### bpy.types.MeshVertex.index

Index of this vertex (in [0, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.MeshVertex.normal"></a>

#### bpy.types.MeshVertex.normal

Vertex Normal (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0), readonly)

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.MeshVertex.select"></a>

#### bpy.types.MeshVertex.select

(default False)

**Type:**

bool

<a id="bpy.types.MeshVertex.undeformed_co"></a>

#### bpy.types.MeshVertex.undeformed_co

For meshes with modifiers applied, the coordinate of the vertex with no deforming modifiers applied, as used for generated texture coordinates (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0), readonly)

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.MeshVertex.bl_rna_get_subclass"></a>

#### classmethod bpy.types.MeshVertex.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.MeshVertex.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.MeshVertex.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Mesh.vertices`](bpy.types.Mesh.md#bpy.types.Mesh.vertices "bpy.types.Mesh.vertices") |  |
