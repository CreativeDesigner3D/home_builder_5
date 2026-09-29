<!-- source: Blender Python API reference 5.2 / bpy_extras.mesh_utils.html -->

<a id="module-bpy_extras.mesh_utils"></a>

# bpy_extras submodule (bpy_extras.mesh_utils)

<a id="bpy_extras.mesh_utils.mesh_linked_uv_islands"></a>

### bpy_extras.mesh_utils.mesh_linked_uv_islands(mesh)

Returns lists of polygon indices connected by UV islands.

**Parameters:**

**mesh** ([`bpy.types.Mesh`](bpy.types.Mesh.md#bpy.types.Mesh "bpy.types.Mesh")) – the mesh used to group with.

**Returns:**

list of lists containing polygon indices

**Return type:**

list[list[int]]

<a id="bpy_extras.mesh_utils.mesh_linked_triangles"></a>

### bpy_extras.mesh_utils.mesh_linked_triangles(mesh)

Splits the mesh into connected triangles, use this for separating cubes from
other mesh elements within 1 mesh data-block.

**Parameters:**

**mesh** ([`bpy.types.Mesh`](bpy.types.Mesh.md#bpy.types.Mesh "bpy.types.Mesh")) – the mesh used to group with.

**Returns:**

Lists of lists containing triangles.

**Return type:**

list[list[[`bpy.types.MeshLoopTriangle`](bpy.types.MeshLoopTriangle.md#bpy.types.MeshLoopTriangle "bpy.types.MeshLoopTriangle")]]

<a id="bpy_extras.mesh_utils.edge_face_count_dict"></a>

### bpy_extras.mesh_utils.edge_face_count_dict(mesh)

**Parameters:**

**mesh** ([`bpy.types.Mesh`](bpy.types.Mesh.md#bpy.types.Mesh "bpy.types.Mesh")) – The mesh to count edges for.

**Returns:**

Dictionary of edge keys with their value set to the number of faces using each edge.

**Return type:**

dict[tuple[int, int], int]

<a id="bpy_extras.mesh_utils.edge_face_count"></a>

### bpy_extras.mesh_utils.edge_face_count(mesh)

**Parameters:**

**mesh** ([`bpy.types.Mesh`](bpy.types.Mesh.md#bpy.types.Mesh "bpy.types.Mesh")) – The mesh to count edges for.

**Returns:**

list of face users for each item in mesh.edges.

**Return type:**

list[int]

<a id="bpy_extras.mesh_utils.edge_loops_from_edges"></a>

### bpy_extras.mesh_utils.edge_loops_from_edges(mesh, edges=None)

Edge loops defined by edges.

Takes mesh.edges or a list of edges and returns the edge loops
as a list of vertex indices.
Closed loops have matching start and end values.

**Parameters:**

- **mesh** ([`bpy.types.Mesh`](bpy.types.Mesh.md#bpy.types.Mesh "bpy.types.Mesh")) – The mesh to extract edge loops from.
- **edges** (list[[`bpy.types.MeshEdge`](bpy.types.MeshEdge.md#bpy.types.MeshEdge "bpy.types.MeshEdge")] | None) – Edges to use, or None to use all edges in the mesh.

**Returns:**

A list of edge loops, each a list of vertex indices.

**Return type:**

list[list[int]]

<a id="bpy_extras.mesh_utils.ngon_tessellate"></a>

### bpy_extras.mesh_utils.ngon_tessellate(from_data, indices, fix_loops=True, debug_print=True)

Takes a poly-line of indices (ngon) and returns a list of face
index lists. Designed to be used for importers that need indices for an
ngon to create from existing verts.

**Parameters:**

- **from_data** ([`bpy.types.Mesh`](bpy.types.Mesh.md#bpy.types.Mesh "bpy.types.Mesh") | list[Sequence[float]] | tuple[Sequence[float]]) – Either a mesh, or a list/tuple of 3D vectors.
- **indices** (list[int]) – a list of indices to use.
  This list is the ordered closed poly-line to fill, and can be a subset of the data given.
- **fix_loops** (bool) – If this is enabled poly-lines
  that use loops to make multiple
  poly-lines are dealt with correctly.
- **debug_print** (bool) – Print debug information to the console.

**Returns:**

Tessellated faces as a list of triangle index tuples.

**Return type:**

list[tuple[int, int, int]]

<a id="bpy_extras.mesh_utils.triangle_random_points"></a>

### bpy_extras.mesh_utils.triangle_random_points(num_points, loop_triangles)

Generates a list of random points over mesh loop triangles.

**Parameters:**

- **num_points** (int) – The number of random points to generate on each triangle.
- **loop_triangles** (Sequence[[`bpy.types.MeshLoopTriangle`](bpy.types.MeshLoopTriangle.md#bpy.types.MeshLoopTriangle "bpy.types.MeshLoopTriangle")]) – Sequence of the triangles to generate points on.

**Returns:**

List of random points over all triangles.

**Return type:**

list[[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")]
