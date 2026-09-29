<!-- source: Blender Python API reference 5.2 / bpy.types.VertexGroupElement.html -->

<a id="vertexgroupelement-bpy-struct"></a>

# VertexGroupElement(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.VertexGroupElement"></a>

### class bpy.types.VertexGroupElement(bpy_struct)

Weight value of a vertex in a vertex group

<a id="bpy.types.VertexGroupElement.group"></a>

#### bpy.types.VertexGroupElement.group

(in [0, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.VertexGroupElement.weight"></a>

#### bpy.types.VertexGroupElement.weight

Vertex Weight (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.VertexGroupElement.bl_rna_get_subclass"></a>

#### classmethod bpy.types.VertexGroupElement.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.VertexGroupElement.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.VertexGroupElement.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`LatticePoint.groups`](bpy.types.LatticePoint.md#bpy.types.LatticePoint.groups "bpy.types.LatticePoint.groups") | - [`MeshVertex.groups`](bpy.types.MeshVertex.md#bpy.types.MeshVertex.groups "bpy.types.MeshVertex.groups") |
