<!-- source: Blender Python API reference 5.2 / bpy.types.MeshEdge.html -->

<a id="meshedge-bpy-struct"></a>

# MeshEdge(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.MeshEdge"></a>

### class bpy.types.MeshEdge(bpy_struct)

Edge in a Mesh data-block

<a id="bpy.types.MeshEdge.hide"></a>

#### bpy.types.MeshEdge.hide

(default False)

**Type:**

bool

<a id="bpy.types.MeshEdge.index"></a>

#### bpy.types.MeshEdge.index

Index of this edge (in [0, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.MeshEdge.is_loose"></a>

#### bpy.types.MeshEdge.is_loose

Edge is not connected to any faces (default False, readonly)

**Type:**

bool

<a id="bpy.types.MeshEdge.select"></a>

#### bpy.types.MeshEdge.select

(default False)

**Type:**

bool

<a id="bpy.types.MeshEdge.use_edge_sharp"></a>

#### bpy.types.MeshEdge.use_edge_sharp

Sharp edge for shading (default False)

**Type:**

bool

<a id="bpy.types.MeshEdge.use_seam"></a>

#### bpy.types.MeshEdge.use_seam

Seam edge for UV unwrapping (default False)

**Type:**

bool

<a id="bpy.types.MeshEdge.vertices"></a>

#### bpy.types.MeshEdge.vertices

Vertex indices (array of 2 items, in [0, inf], default (0, 0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[int]

<a id="bpy.types.MeshEdge.key"></a>

#### bpy.types.MeshEdge.key

(readonly)

<a id="bpy.types.MeshEdge.bl_rna_get_subclass"></a>

#### classmethod bpy.types.MeshEdge.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.MeshEdge.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.MeshEdge.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Mesh.edges`](bpy.types.Mesh.md#bpy.types.Mesh.edges "bpy.types.Mesh.edges") |  |
