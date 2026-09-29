<!-- source: Blender Python API reference 5.2 / bpy.types.MeshLoop.html -->

<a id="meshloop-bpy-struct"></a>

# MeshLoop(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.MeshLoop"></a>

### class bpy.types.MeshLoop(bpy_struct)

Loop in a Mesh data-block

<a id="bpy.types.MeshLoop.bitangent"></a>

#### bpy.types.MeshLoop.bitangent

Bitangent vector of this vertex for this face (must be computed beforehand using calc_tangents, use it only if really needed, slower access than bitangent_sign) (array of 3 items, in [-1, 1], default (0.0, 0.0, 0.0), readonly)

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.MeshLoop.bitangent_sign"></a>

#### bpy.types.MeshLoop.bitangent_sign

Sign of the bitangent vector of this vertex for this face (must be computed beforehand using calc_tangents, bitangent = bitangent_sign * cross(normal, tangent)) (in [-1, 1], default 0.0, readonly)

**Type:**

float

<a id="bpy.types.MeshLoop.edge_index"></a>

#### bpy.types.MeshLoop.edge_index

Edge index (in [0, inf], default 0)

**Type:**

int

<a id="bpy.types.MeshLoop.index"></a>

#### bpy.types.MeshLoop.index

Index of this loop (in [0, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.MeshLoop.normal"></a>

#### bpy.types.MeshLoop.normal

The normal direction of the face corner, taking into account sharp faces, sharp edges, and custom normal data (array of 3 items, in [-1, 1], default (0.0, 0.0, 0.0), readonly)

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.MeshLoop.tangent"></a>

#### bpy.types.MeshLoop.tangent

Local space unit length tangent vector of this vertex for this face (must be computed beforehand using calc_tangents) (array of 3 items, in [-1, 1], default (0.0, 0.0, 0.0), readonly)

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.MeshLoop.vertex_index"></a>

#### bpy.types.MeshLoop.vertex_index

Vertex index (in [0, inf], default 0)

**Type:**

int

<a id="bpy.types.MeshLoop.bl_rna_get_subclass"></a>

#### classmethod bpy.types.MeshLoop.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.MeshLoop.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.MeshLoop.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Mesh.loops`](bpy.types.Mesh.md#bpy.types.Mesh.loops "bpy.types.Mesh.loops") |  |
