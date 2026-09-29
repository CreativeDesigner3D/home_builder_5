<!-- source: Blender Python API reference 5.2 / bmesh.utils.html -->

<a id="module-bmesh.utils"></a>

# BMesh Utilities (bmesh.utils)

This module provides bmesh utility functions for splitting, joining, and modifying mesh elements.

<a id="bmesh.utils.edge_rotate"></a>

### bmesh.utils.edge_rotate(edge, ccw=False)

Rotate the edge and return the newly created edge.
If rotating the edge fails, None will be returned.

**Parameters:**

- **edge** ([`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge")) – The edge to rotate.
- **ccw** (bool) – When True the edge will be rotated counter clockwise.

**Returns:**

The newly rotated edge.

**Return type:**

[`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | None

<a id="bmesh.utils.edge_split"></a>

### bmesh.utils.edge_split(edge, vert, fac)

Split an edge, return the newly created data.

**Parameters:**

- **edge** ([`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge")) – The edge to split.
- **vert** ([`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert")) – One of the verts on the edge, defines the split direction.
- **fac** (float) – The point on the edge where the new vert will be created [0 - 1].

**Returns:**

The newly created (edge, vert) pair.

**Return type:**

tuple[[`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge"), [`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert")]

<a id="bmesh.utils.face_flip"></a>

### bmesh.utils.face_flip(face)

Flip the face’s direction.

**Parameters:**

**face** ([`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")) – Face to flip.

<a id="bmesh.utils.face_join"></a>

### bmesh.utils.face_join(faces, remove=True)

Joins a sequence of faces.

**Parameters:**

- **faces** (Sequence[[`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]) – Sequence of faces.
- **remove** (bool) – Remove the edges and vertices between the faces.

**Returns:**

The newly created face or None on failure.

**Return type:**

[`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace") | None

<a id="bmesh.utils.face_split"></a>

### bmesh.utils.face_split(face, vert_a, vert_b, *, coords=(), use_exist=True, source=None)

Face split with optional intermediate points.

**Parameters:**

- **face** ([`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")) – The face to cut.
- **vert_a** ([`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert")) – First vertex to cut in the face (face must contain the vert).
- **vert_b** ([`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert")) – Second vertex to cut in the face (face must contain the vert).
- **coords** (Sequence[Sequence[float]]) – Optional sequence of 3D points in between vert_a and vert_b.
- **use_exist** (bool) – Use an existing edge if it exists (only used when coords argument is empty or omitted)
- **source** ([`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | None) – Newly created edge will copy settings from this one.

**Returns:**

The newly created face and loop.

**Return type:**

tuple[[`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace"), [`bmesh.types.BMLoop`](bmesh.types.md#bmesh.types.BMLoop "bmesh.types.BMLoop")]

<a id="bmesh.utils.face_split_edgenet"></a>

### bmesh.utils.face_split_edgenet(face, edgenet)

Splits a face into any number of regions defined by an edgenet.

**Parameters:**

- **face** ([`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")) – The face to split.
- **edgenet** (Sequence[[`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge")]) – Sequence of edges.

**Returns:**

The newly created faces.

**Return type:**

tuple[[`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace"), …]

> **Note:**
>
> Regions defined by edges need to connect to the face, otherwise they’re ignored as loose edges.

<a id="bmesh.utils.face_vert_separate"></a>

### bmesh.utils.face_vert_separate(face, vert)

Rip a vertex in a face away and add a new vertex.

**Parameters:**

- **face** ([`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")) – The face to separate.
- **vert** ([`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert")) – A vertex in the face to separate.

**Returns:**

The newly created vertex or None on failure.

**Return type:**

[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | None

> **Note:**
>
> This is the same as loop_separate, and has only been added for convenience.

<a id="bmesh.utils.loop_separate"></a>

### bmesh.utils.loop_separate(loop)

Rip a vertex in a face away and add a new vertex.

**Parameters:**

**loop** ([`bmesh.types.BMLoop`](bmesh.types.md#bmesh.types.BMLoop "bmesh.types.BMLoop")) – The loop to separate.

**Returns:**

The newly created vertex or None on failure.

**Return type:**

[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | None

<a id="bmesh.utils.uv_select_check"></a>

### bmesh.utils.uv_select_check(bm, /, *, sync=True, flush=False, contiguous=False)

Check UV selection state for consistency issues.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The BMesh to check.
- **sync** (bool) – Check the data is properly synchronized between UV’s and the underlying mesh. Failure to synchronize with the mesh selection may cause tools not to behave properly.
- **flush** (bool) – Check the selection has been properly flushed between elements (based on the current [`bmesh.types.BMesh.select_mode`](bmesh.types.md#bmesh.types.BMesh.select_mode "bmesh.types.BMesh.select_mode")).
- **contiguous** (bool) – Check connected UV’s and edges have a matching selection state.

**Returns:**

An error dictionary or None when there are no errors found.

**Return type:**

dict[str, int] | None

<a id="bmesh.utils.vert_collapse_edge"></a>

### bmesh.utils.vert_collapse_edge(vert, edge)

Collapse a vertex into an edge.

**Parameters:**

- **vert** ([`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert")) – The vert that will be collapsed.
- **edge** ([`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge")) – The edge to collapse into.

**Returns:**

The resulting edge from the collapse operation.

**Return type:**

[`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge")

<a id="bmesh.utils.vert_collapse_faces"></a>

### bmesh.utils.vert_collapse_faces(vert, edge, fac, join_faces)

Collapses a vertex that has only two manifold edges onto a vertex it shares an edge with.

**Parameters:**

- **vert** ([`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert")) – The vert that will be collapsed.
- **edge** ([`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge")) – The edge to collapse into.
- **fac** (float) – The factor to use when merging customdata [0 - 1].
- **join_faces** (bool) – When true the faces around the vertex will be joined otherwise collapse the vertex by merging the 2 edges this vertex connects to into one.

**Returns:**

The resulting edge from the collapse operation.

**Return type:**

[`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge")

<a id="bmesh.utils.vert_dissolve"></a>

### bmesh.utils.vert_dissolve(vert)

Dissolve this vertex (will be removed).

**Parameters:**

**vert** ([`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert")) – The vert to be dissolved.

**Returns:**

True when the vertex dissolve is successful.

**Return type:**

bool

<a id="bmesh.utils.vert_separate"></a>

### bmesh.utils.vert_separate(vert, edges)

Separate this vertex at every edge.

**Parameters:**

- **vert** ([`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert")) – The vert to be separated.
- **edges** (Sequence[[`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge")]) – The edges to separate.

**Returns:**

The newly separated verts (including the vertex passed).

**Return type:**

tuple[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert"), …]

<a id="bmesh.utils.vert_splice"></a>

### bmesh.utils.vert_splice(vert, vert_target)

Splice vert into vert_target, merging them.

**Parameters:**

- **vert** ([`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert")) – The vertex to be removed.
- **vert_target** ([`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert")) – The vertex to merge into.

> **Note:**
>
> The verts mustn’t share an edge or face.
