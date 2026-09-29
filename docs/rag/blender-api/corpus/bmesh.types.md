<!-- source: Blender Python API reference 5.2 / bmesh.types.html -->

<a id="module-bmesh.types"></a>

# BMesh Types (bmesh.types)

<a id="base-mesh-type"></a>

## Base Mesh Type

<a id="bmesh.types.BMesh"></a>

### class bmesh.types.BMesh

The BMesh data structure

<a id="bmesh.types.BMesh.calc_loop_triangles"></a>

#### bmesh.types.BMesh.calc_loop_triangles()

Calculate triangle tessellation from quads/ngons.

**Returns:**

The triangulated faces.

**Return type:**

list[tuple[[`bmesh.types.BMLoop`](#bmesh.types.BMLoop "bmesh.types.BMLoop"), [`bmesh.types.BMLoop`](#bmesh.types.BMLoop "bmesh.types.BMLoop"), [`bmesh.types.BMLoop`](#bmesh.types.BMLoop "bmesh.types.BMLoop")]]

<a id="bmesh.types.BMesh.calc_volume"></a>

#### bmesh.types.BMesh.calc_volume(*, signed=False)

Calculate mesh volume based on face normals.

**Parameters:**

**signed** (bool) – when signed is true, negative values may be returned.

**Returns:**

The volume of the mesh.

**Return type:**

float

<a id="bmesh.types.BMesh.clear"></a>

#### bmesh.types.BMesh.clear()

Clear all mesh data.

<a id="bmesh.types.BMesh.copy"></a>

#### bmesh.types.BMesh.copy()

**Returns:**

A copy of this BMesh.

**Return type:**

[`bmesh.types.BMesh`](#bmesh.types.BMesh "bmesh.types.BMesh")

<a id="bmesh.types.BMesh.free"></a>

#### bmesh.types.BMesh.free()

Explicitly free the BMesh data from memory, causing exceptions on further access.

> **Note:**
>
> The BMesh is freed automatically, typically when the script finishes executing.
> However in some cases it’s hard to predict when this will be and it’s useful to
> explicitly free the data.

<a id="bmesh.types.BMesh.from_mesh"></a>

#### bmesh.types.BMesh.from_mesh(mesh, *, face_normals=True, vertex_normals=True, use_shape_key=False, shape_key_index=0)

Initialize this bmesh from existing mesh data-block.

**Parameters:**

- **mesh** ([`bpy.types.Mesh`](bpy.types.Mesh.md#bpy.types.Mesh "bpy.types.Mesh")) – The mesh data to load.
- **face_normals** (bool) – Calculate face normals.
- **vertex_normals** (bool) – Calculate vertex normals.
- **use_shape_key** (bool) – Use the locations from a shape key.
- **shape_key_index** (int) – The shape key index to use.

> **Note:**
>
> Multiple calls can be used to join multiple meshes.
>
> Custom-data layers are only copied from `mesh` on initialization.
> Further calls will copy custom-data to matching layers, layers missing on the target mesh won’t be added.

<a id="bmesh.types.BMesh.from_object"></a>

#### bmesh.types.BMesh.from_object(object, depsgraph, *, cage=False, face_normals=True, vertex_normals=True)

Initialize this bmesh from existing object data-block (only meshes are currently supported).

**Parameters:**

- **object** ([`bpy.types.Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object")) – The object data to load.
- **depsgraph** ([`bpy.types.Depsgraph`](bpy.types.Depsgraph.md#bpy.types.Depsgraph "bpy.types.Depsgraph")) – The dependency graph for evaluated data.
- **cage** (bool) – Get the mesh as a deformed cage.
- **face_normals** (bool) – Calculate face normals.
- **vertex_normals** (bool) – Calculate vertex normals.

<a id="bmesh.types.BMesh.normal_update"></a>

#### bmesh.types.BMesh.normal_update()

Update normals of mesh faces and verts.

> **Note:**
>
> The normal of any vertex where `is_wire` is True will be a zero vector.

<a id="bmesh.types.BMesh.select_flush"></a>

#### bmesh.types.BMesh.select_flush(select)

Flush selection from vertices, independent of the current selection mode.

**Parameters:**

**select** (bool) – flush selection or de-selected elements.

<a id="bmesh.types.BMesh.select_flush_mode"></a>

#### bmesh.types.BMesh.select_flush_mode(*, flush_down=False)

Flush selection based on the current mode [`bmesh.types.BMesh.select_mode`](#bmesh.types.BMesh.select_mode "bmesh.types.BMesh.select_mode").

**Parameters:**

**flush_down** (bool) – Flush selection down from faces to edges & verts or from edges to verts. This option is ignored when vertex selection mode is enabled.

<a id="bmesh.types.BMesh.to_mesh"></a>

#### bmesh.types.BMesh.to_mesh(mesh)

Writes this BMesh data into an existing Mesh data-block.

**Parameters:**

**mesh** ([`bpy.types.Mesh`](bpy.types.Mesh.md#bpy.types.Mesh "bpy.types.Mesh")) – The mesh data to write into.

<a id="bmesh.types.BMesh.transform"></a>

#### bmesh.types.BMesh.transform(matrix, *, filter=None)

Transform the mesh (optionally filtering flagged data only).

**Parameters:**

- **matrix** ([`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")) – 4x4 transform matrix.
- **filter** (set[Literal['SELECT', 'HIDE', 'SEAM', 'SMOOTH', 'TAG']] | None) – Flag to filter vertices.

<a id="bmesh.types.BMesh.uv_select_flush"></a>

#### bmesh.types.BMesh.uv_select_flush(select)

Flush selection from UV vertices to edges & faces independent of the selection mode.

**Parameters:**

**select** (bool) – Flush selection or de-selected elements.

> **Note:**
>
> - This function doesn’t flush the selection to the mesh, typically [`bmesh.types.BMesh.uv_select_sync_to_mesh()`](#bmesh.types.BMesh.uv_select_sync_to_mesh "bmesh.types.BMesh.uv_select_sync_to_mesh") should be called afterwards.

<a id="bmesh.types.BMesh.uv_select_flush_mode"></a>

#### bmesh.types.BMesh.uv_select_flush_mode(*, flush_down=False)

Flush UV selection based on the current mode [`bmesh.types.BMesh.select_mode`](#bmesh.types.BMesh.select_mode "bmesh.types.BMesh.select_mode").

**Parameters:**

**flush_down** (bool) – Flush selection down from faces to edges & verts or from edges to verts. This option is ignored when vertex selection mode is enabled.

<a id="bmesh.types.BMesh.uv_select_flush_shared"></a>

#### bmesh.types.BMesh.uv_select_flush_shared(select)

Flush selection from UV vertices to contiguous UV’s independent of the selection mode.

**Parameters:**

**select** (bool) – Flush selection or de-selected elements.

> **Note:**
>
> - This function doesn’t flush the selection to the mesh, typically [`bmesh.types.BMesh.uv_select_sync_to_mesh()`](#bmesh.types.BMesh.uv_select_sync_to_mesh "bmesh.types.BMesh.uv_select_sync_to_mesh") should be called afterwards.

<a id="bmesh.types.BMesh.uv_select_foreach_set"></a>

#### bmesh.types.BMesh.uv_select_foreach_set(select, /, *, loop_verts=(), loop_edges=(), faces=(), sticky_select_mode='SHARED_LOCATION')

Set the UV selection state for loop-vertices, loop-edges & faces.

This is a close equivalent to selecting in the UV editor.

**Parameters:**

- **select** (bool) – The selection state to set.
- **loop_verts** (Iterable[[`bmesh.types.BMLoop`](#bmesh.types.BMLoop "bmesh.types.BMLoop")]) – Loop verts to operate on.
- **loop_edges** (Iterable[[`bmesh.types.BMLoop`](#bmesh.types.BMLoop "bmesh.types.BMLoop")]) – Loop edges to operate on.
- **faces** (Iterable[[`bmesh.types.BMFace`](#bmesh.types.BMFace "bmesh.types.BMFace")]) – Faces to operate on.
- **sticky_select_mode** (Literal[‘SHARED_LOCATION’, ‘DISABLED’, ‘SHARED_VERTEX’]) – See ([`bpy.types.ToolSettings.uv_sticky_select_mode`](bpy.types.ToolSettings.md#bpy.types.ToolSettings.uv_sticky_select_mode "bpy.types.ToolSettings.uv_sticky_select_mode") which may be passed in directly)..

> **Note:**
>
> - This function is selection-mode independent, typically [`bmesh.types.BMesh.uv_select_flush_mode()`](#bmesh.types.BMesh.uv_select_flush_mode "bmesh.types.BMesh.uv_select_flush_mode") should be called afterwards.
> - This function doesn’t flush the selection to the mesh, typically [`bmesh.types.BMesh.uv_select_sync_to_mesh()`](#bmesh.types.BMesh.uv_select_sync_to_mesh "bmesh.types.BMesh.uv_select_sync_to_mesh") should be called afterwards.

<a id="bmesh.types.BMesh.uv_select_foreach_set_from_mesh"></a>

#### bmesh.types.BMesh.uv_select_foreach_set_from_mesh(select, /, *, verts=(), edges=(), faces=(), sticky_select_mode='SHARED_LOCATION')

Select or de-select mesh elements, updating the UV selection.

An equivalent to selecting from the 3D viewport for selection operations that support maintaining a synchronized UV selection.

**Parameters:**

- **select** (bool) – The selection state to set.
- **verts** (Iterable[[`bmesh.types.BMVert`](#bmesh.types.BMVert "bmesh.types.BMVert")]) – Verts to operate on.
- **edges** (Iterable[[`bmesh.types.BMEdge`](#bmesh.types.BMEdge "bmesh.types.BMEdge")]) – Edges to operate on.
- **faces** (Iterable[[`bmesh.types.BMFace`](#bmesh.types.BMFace "bmesh.types.BMFace")]) – Faces to operate on.
- **sticky_select_mode** (Literal[‘SHARED_LOCATION’, ‘DISABLED’, ‘SHARED_VERTEX’]) – See ([`bpy.types.ToolSettings.uv_sticky_select_mode`](bpy.types.ToolSettings.md#bpy.types.ToolSettings.uv_sticky_select_mode "bpy.types.ToolSettings.uv_sticky_select_mode") which may be passed in directly)..

<a id="bmesh.types.BMesh.uv_select_sync_from_mesh"></a>

#### bmesh.types.BMesh.uv_select_sync_from_mesh(*, sticky_select_mode='SHARED_LOCATION')

Sync selection from mesh to UVs.

**Parameters:**

**sticky_select_mode** (Literal[‘SHARED_LOCATION’, ‘DISABLED’, ‘SHARED_VERTEX’]) – Behavior when flushing from the mesh to UV selection ([`bpy.types.ToolSettings.uv_sticky_select_mode`](bpy.types.ToolSettings.md#bpy.types.ToolSettings.uv_sticky_select_mode "bpy.types.ToolSettings.uv_sticky_select_mode") which may be passed in directly).. This should only be used when preparing to create a UV selection.

> **Note:**
>
> - This function doesn’t flush the selection to the mesh, typically [`bmesh.types.BMesh.uv_select_sync_to_mesh()`](#bmesh.types.BMesh.uv_select_sync_to_mesh "bmesh.types.BMesh.uv_select_sync_to_mesh") should be called afterwards.

<a id="bmesh.types.BMesh.uv_select_sync_to_mesh"></a>

#### bmesh.types.BMesh.uv_select_sync_to_mesh()

Sync selection from UVs to the mesh.

<a id="bmesh.types.BMesh.edges"></a>

#### bmesh.types.BMesh.edges

This mesh’s edge sequence (read-only).

**Type:**

[`bmesh.types.BMEdgeSeq`](#bmesh.types.BMEdgeSeq "bmesh.types.BMEdgeSeq")

<a id="bmesh.types.BMesh.faces"></a>

#### bmesh.types.BMesh.faces

This mesh’s face sequence (read-only).

**Type:**

[`bmesh.types.BMFaceSeq`](#bmesh.types.BMFaceSeq "bmesh.types.BMFaceSeq")

<a id="bmesh.types.BMesh.is_valid"></a>

#### bmesh.types.BMesh.is_valid

True when this element is valid (hasn’t been freed or removed).

**Type:**

bool

<a id="bmesh.types.BMesh.is_wrapped"></a>

#### bmesh.types.BMesh.is_wrapped

True when this mesh is owned by blender (typically the editmode BMesh).

**Type:**

bool

<a id="bmesh.types.BMesh.loops"></a>

#### bmesh.types.BMesh.loops

This mesh’s loops (read-only).

**Type:**

[`bmesh.types.BMLoopSeq`](#bmesh.types.BMLoopSeq "bmesh.types.BMLoopSeq")

> **Note:**
>
> Loops must be accessed via faces, this is only exposed for layer access.

<a id="bmesh.types.BMesh.select_history"></a>

#### bmesh.types.BMesh.select_history

Sequence of selected items (the last is displayed as active).

**Type:**

[`bmesh.types.BMEditSelSeq`](#bmesh.types.BMEditSelSeq "bmesh.types.BMEditSelSeq")

<a id="bmesh.types.BMesh.select_mode"></a>

#### bmesh.types.BMesh.select_mode

The selection mode, cannot be assigned an empty set.

**Type:**

set[Literal[‘VERT’, ‘EDGE’, ‘FACE’]]

<a id="bmesh.types.BMesh.uv_select_sync_valid"></a>

#### bmesh.types.BMesh.uv_select_sync_valid

When true, the UV selection has been synchronized. Setting to False means the UV selection will be ignored. While setting to true is supported it is up to the script author to ensure a correct selection state before doing so.

**Type:**

bool

<a id="bmesh.types.BMesh.verts"></a>

#### bmesh.types.BMesh.verts

This mesh’s vert sequence (read-only).

**Type:**

[`bmesh.types.BMVertSeq`](#bmesh.types.BMVertSeq "bmesh.types.BMVertSeq")

Special Methods

<a id="bmesh.types.BMesh.__hash__"></a>

#### bmesh.types.BMesh.__hash__()

**Return type:**

int

<a id="bmesh.types.BMesh.__repr__"></a>

#### bmesh.types.BMesh.__repr__()

**Return type:**

str

<a id="mesh-elements"></a>

## Mesh Elements

<a id="bmesh.types.BMVert"></a>

### class bmesh.types.BMVert

The BMesh vertex type

<a id="bmesh.types.BMVert.calc_edge_angle"></a>

#### bmesh.types.BMVert.calc_edge_angle(fallback=None)

Return the angle between this vert’s two connected edges.

**Parameters:**

**fallback** (Any) – return this when the vert doesn’t have 2 edges
(instead of raising a `ValueError`).

**Returns:**

Angle between edges in radians.

**Return type:**

float

<a id="bmesh.types.BMVert.calc_shell_factor"></a>

#### bmesh.types.BMVert.calc_shell_factor()

Return a multiplier calculated based on the sharpness of the vertex.
Where a flat surface gives 1.0, and higher values sharper edges.
This is used to maintain shell thickness when offsetting verts along their normals.

**Returns:**

offset multiplier

**Return type:**

float

<a id="bmesh.types.BMVert.copy_from"></a>

#### bmesh.types.BMVert.copy_from(other)

Copy values from another element of matching type.

**Parameters:**

**other** (Self) – Another element of the same type to copy from.

<a id="bmesh.types.BMVert.copy_from_face_interp"></a>

#### bmesh.types.BMVert.copy_from_face_interp(face)

Interpolate the customdata from a face onto this vert (the vert should overlap the face).

**Parameters:**

**face** ([`bmesh.types.BMFace`](#bmesh.types.BMFace "bmesh.types.BMFace")) – The face to interpolate data from.

<a id="bmesh.types.BMVert.copy_from_vert_interp"></a>

#### bmesh.types.BMVert.copy_from_vert_interp(vert_pair, fac)

Interpolate the customdata from a vert between 2 other verts.

**Parameters:**

- **vert_pair** (Sequence[[`bmesh.types.BMVert`](#bmesh.types.BMVert "bmesh.types.BMVert")]) – The verts between which to interpolate data from.
- **fac** (float) – The interpolation factor.

<a id="bmesh.types.BMVert.hide_set"></a>

#### bmesh.types.BMVert.hide_set(hide)

Set the hide state.
This is different from the *hide* attribute because it updates the selection and hide state of associated geometry.

**Parameters:**

**hide** (bool) – Hidden or visible.

<a id="bmesh.types.BMVert.normal_update"></a>

#### bmesh.types.BMVert.normal_update()

Update vertex normal.
This does not update the normals of adjoining faces.

> **Note:**
>
> The vertex normal will be a zero vector if vertex [`is_wire`](#bmesh.types.BMVert.is_wire "bmesh.types.BMVert.is_wire") is True.

<a id="bmesh.types.BMVert.select_set"></a>

#### bmesh.types.BMVert.select_set(select)

Set the selection.
This is different from the *select* attribute because it updates the selection state of associated geometry.

**Parameters:**

**select** (bool) – Select or de-select.

> **Note:**
>
> This flushes selection down (e.g. selecting a face also selects its edges and vertices), but not up (e.g. de-selecting a vertex won’t de-select faces that use it). Before finishing with a mesh, flushing is typically still needed.

<a id="bmesh.types.BMVert.co"></a>

#### bmesh.types.BMVert.co

The coordinates for this vertex as a 3D, wrapped vector.

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bmesh.types.BMVert.hide"></a>

#### bmesh.types.BMVert.hide

Hidden state of this element.

**Type:**

bool

<a id="bmesh.types.BMVert.index"></a>

#### bmesh.types.BMVert.index

Index of this element.

**Type:**

int

> **Note:**
>
> This value is not necessarily valid, while editing the mesh it can become *dirty*.
>
> It’s also possible to assign any number to this attribute for a scripts internal logic.
>
> To ensure the value is up to date - see [`bmesh.types.BMElemSeq.index_update()`](#bmesh.types.BMElemSeq.index_update "bmesh.types.BMElemSeq.index_update").

<a id="bmesh.types.BMVert.is_boundary"></a>

#### bmesh.types.BMVert.is_boundary

True when this vertex is connected to boundary edges (read-only).

**Type:**

bool

<a id="bmesh.types.BMVert.is_manifold"></a>

#### bmesh.types.BMVert.is_manifold

True when this vertex is manifold (read-only).

**Type:**

bool

<a id="bmesh.types.BMVert.is_valid"></a>

#### bmesh.types.BMVert.is_valid

True when this element is valid (hasn’t been freed or removed).

**Type:**

bool

<a id="bmesh.types.BMVert.is_wire"></a>

#### bmesh.types.BMVert.is_wire

True when this vertex is not connected to any faces (read-only).

**Type:**

bool

<a id="bmesh.types.BMVert.link_edges"></a>

#### bmesh.types.BMVert.link_edges

Edges connected to this vertex (read-only).

**Type:**

[`bmesh.types.BMElemSeq`](#bmesh.types.BMElemSeq "bmesh.types.BMElemSeq")[[`bmesh.types.BMEdge`](#bmesh.types.BMEdge "bmesh.types.BMEdge")]

<a id="bmesh.types.BMVert.link_faces"></a>

#### bmesh.types.BMVert.link_faces

Faces connected to this vertex (read-only).

**Type:**

[`bmesh.types.BMElemSeq`](#bmesh.types.BMElemSeq "bmesh.types.BMElemSeq")[[`bmesh.types.BMFace`](#bmesh.types.BMFace "bmesh.types.BMFace")]

<a id="bmesh.types.BMVert.link_loops"></a>

#### bmesh.types.BMVert.link_loops

Loops that use this vertex (read-only).

**Type:**

[`bmesh.types.BMElemSeq`](#bmesh.types.BMElemSeq "bmesh.types.BMElemSeq")[[`bmesh.types.BMLoop`](#bmesh.types.BMLoop "bmesh.types.BMLoop")]

<a id="bmesh.types.BMVert.normal"></a>

#### bmesh.types.BMVert.normal

The normal for this vertex as a 3D, wrapped vector.

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bmesh.types.BMVert.select"></a>

#### bmesh.types.BMVert.select

Selected state of this element.

**Type:**

bool

<a id="bmesh.types.BMVert.tag"></a>

#### bmesh.types.BMVert.tag

Generic attribute scripts can use for own logic

**Type:**

bool

Special Methods

<a id="bmesh.types.BMVert.__getitem__"></a>

#### bmesh.types.BMVert.__getitem__(key)

**Parameters:**

**key** (int) – Index or key.

**Return type:**

float

<a id="bmesh.types.BMVert.__hash__"></a>

#### bmesh.types.BMVert.__hash__()

**Return type:**

int

<a id="bmesh.types.BMVert.__repr__"></a>

#### bmesh.types.BMVert.__repr__()

**Return type:**

str

<a id="bmesh.types.BMVert.__setitem__"></a>

#### bmesh.types.BMVert.__setitem__(key, value)

**Parameters:**

- **key** (int) – Index or key.
- **value** (object) – Value to assign.

<a id="bmesh.types.BMEdge"></a>

### class bmesh.types.BMEdge

The BMesh edge connecting 2 verts

<a id="bmesh.types.BMEdge.calc_face_angle"></a>

#### bmesh.types.BMEdge.calc_face_angle(fallback=None)

Return the angle between this edge’s two connected faces.

**Parameters:**

**fallback** (Any) – return this when the edge doesn’t have 2 faces
(instead of raising a `ValueError`).

**Returns:**

The angle between 2 connected faces in radians.

**Return type:**

float

<a id="bmesh.types.BMEdge.calc_face_angle_signed"></a>

#### bmesh.types.BMEdge.calc_face_angle_signed(fallback=None)

Return the signed angle between this edge’s two connected faces.

**Parameters:**

**fallback** (Any) – return this when the edge doesn’t have 2 faces
(instead of raising a `ValueError`).

**Returns:**

The angle between 2 connected faces in radians (negative for concave join).

**Return type:**

float

<a id="bmesh.types.BMEdge.calc_length"></a>

#### bmesh.types.BMEdge.calc_length()

Return the length of the edge.

**Returns:**

The length between both verts.

**Return type:**

float

<a id="bmesh.types.BMEdge.calc_tangent"></a>

#### bmesh.types.BMEdge.calc_tangent(loop)

Return the tangent at this edge relative to a face (pointing inward into the face).
This uses the face normal for calculation.

**Parameters:**

**loop** ([`bmesh.types.BMLoop`](#bmesh.types.BMLoop "bmesh.types.BMLoop")) – The loop used for tangent calculation.

**Returns:**

a normalized vector.

**Return type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bmesh.types.BMEdge.copy_from"></a>

#### bmesh.types.BMEdge.copy_from(other)

Copy values from another element of matching type.

**Parameters:**

**other** (Self) – Another element of the same type to copy from.

<a id="bmesh.types.BMEdge.hide_set"></a>

#### bmesh.types.BMEdge.hide_set(hide)

Set the hide state.
This is different from the *hide* attribute because it updates the selection and hide state of associated geometry.

**Parameters:**

**hide** (bool) – Hidden or visible.

<a id="bmesh.types.BMEdge.normal_update"></a>

#### bmesh.types.BMEdge.normal_update()

Update normals of all connected faces and the edge verts.

> **Note:**
>
> The normal of edge vertex will be a zero vector if vertex [`is_wire`](#bmesh.types.BMEdge.is_wire "bmesh.types.BMEdge.is_wire") is True.

<a id="bmesh.types.BMEdge.other_vert"></a>

#### bmesh.types.BMEdge.other_vert(vert)

Return the other vertex on this edge or None if the vertex is not used by this edge.

**Parameters:**

**vert** ([`bmesh.types.BMVert`](#bmesh.types.BMVert "bmesh.types.BMVert")) – a vert in this edge.

**Returns:**

The edge’s other vert.

**Return type:**

[`bmesh.types.BMVert`](#bmesh.types.BMVert "bmesh.types.BMVert") | None

<a id="bmesh.types.BMEdge.select_set"></a>

#### bmesh.types.BMEdge.select_set(select)

Set the selection.
This is different from the *select* attribute because it updates the selection state of associated geometry.

**Parameters:**

**select** (bool) – Select or de-select.

> **Note:**
>
> This flushes selection down (e.g. selecting a face also selects its edges and vertices), but not up (e.g. de-selecting a vertex won’t de-select faces that use it). Before finishing with a mesh, flushing is typically still needed.

<a id="bmesh.types.BMEdge.hide"></a>

#### bmesh.types.BMEdge.hide

Hidden state of this element.

**Type:**

bool

<a id="bmesh.types.BMEdge.index"></a>

#### bmesh.types.BMEdge.index

Index of this element.

**Type:**

int

> **Note:**
>
> This value is not necessarily valid, while editing the mesh it can become *dirty*.
>
> It’s also possible to assign any number to this attribute for a scripts internal logic.
>
> To ensure the value is up to date - see [`bmesh.types.BMElemSeq.index_update()`](#bmesh.types.BMElemSeq.index_update "bmesh.types.BMElemSeq.index_update").

<a id="bmesh.types.BMEdge.is_boundary"></a>

#### bmesh.types.BMEdge.is_boundary

True when this edge is at the boundary of a face (read-only).

**Type:**

bool

<a id="bmesh.types.BMEdge.is_contiguous"></a>

#### bmesh.types.BMEdge.is_contiguous

True when this edge is manifold, between two faces with the same winding (read-only).

**Type:**

bool

<a id="bmesh.types.BMEdge.is_convex"></a>

#### bmesh.types.BMEdge.is_convex

True when this edge joins two convex faces, depends on a valid face normal (read-only).

**Type:**

bool

<a id="bmesh.types.BMEdge.is_manifold"></a>

#### bmesh.types.BMEdge.is_manifold

True when this edge is manifold (read-only).

**Type:**

bool

<a id="bmesh.types.BMEdge.is_valid"></a>

#### bmesh.types.BMEdge.is_valid

True when this element is valid (hasn’t been freed or removed).

**Type:**

bool

<a id="bmesh.types.BMEdge.is_wire"></a>

#### bmesh.types.BMEdge.is_wire

True when this edge is not connected to any faces (read-only).

**Type:**

bool

<a id="bmesh.types.BMEdge.link_faces"></a>

#### bmesh.types.BMEdge.link_faces

Faces connected to this edge, (read-only).

**Type:**

[`bmesh.types.BMElemSeq`](#bmesh.types.BMElemSeq "bmesh.types.BMElemSeq")[[`bmesh.types.BMFace`](#bmesh.types.BMFace "bmesh.types.BMFace")]

<a id="bmesh.types.BMEdge.link_loops"></a>

#### bmesh.types.BMEdge.link_loops

Loops connected to this edge, (read-only).

**Type:**

[`bmesh.types.BMElemSeq`](#bmesh.types.BMElemSeq "bmesh.types.BMElemSeq")[[`bmesh.types.BMLoop`](#bmesh.types.BMLoop "bmesh.types.BMLoop")]

<a id="bmesh.types.BMEdge.seam"></a>

#### bmesh.types.BMEdge.seam

Seam for UV unwrapping.

**Type:**

bool

<a id="bmesh.types.BMEdge.select"></a>

#### bmesh.types.BMEdge.select

Selected state of this element.

**Type:**

bool

<a id="bmesh.types.BMEdge.smooth"></a>

#### bmesh.types.BMEdge.smooth

Smooth state of this element.

**Type:**

bool

<a id="bmesh.types.BMEdge.tag"></a>

#### bmesh.types.BMEdge.tag

Generic attribute scripts can use for own logic

**Type:**

bool

<a id="bmesh.types.BMEdge.verts"></a>

#### bmesh.types.BMEdge.verts

Verts this edge uses (always 2), (read-only).

**Type:**

[`bmesh.types.BMElemSeq`](#bmesh.types.BMElemSeq "bmesh.types.BMElemSeq")[[`bmesh.types.BMVert`](#bmesh.types.BMVert "bmesh.types.BMVert")]

Special Methods

<a id="bmesh.types.BMEdge.__getitem__"></a>

#### bmesh.types.BMEdge.__getitem__(key)

**Parameters:**

**key** (int) – Index or key.

**Return type:**

float

<a id="bmesh.types.BMEdge.__hash__"></a>

#### bmesh.types.BMEdge.__hash__()

**Return type:**

int

<a id="bmesh.types.BMEdge.__repr__"></a>

#### bmesh.types.BMEdge.__repr__()

**Return type:**

str

<a id="bmesh.types.BMEdge.__setitem__"></a>

#### bmesh.types.BMEdge.__setitem__(key, value)

**Parameters:**

- **key** (int) – Index or key.
- **value** (object) – Value to assign.

<a id="bmesh.types.BMFace"></a>

### class bmesh.types.BMFace

The BMesh face with 3 or more sides

<a id="bmesh.types.BMFace.calc_area"></a>

#### bmesh.types.BMFace.calc_area()

Return the area of the face.

**Returns:**

The area of the face.

**Return type:**

float

<a id="bmesh.types.BMFace.calc_center_bounds"></a>

#### bmesh.types.BMFace.calc_center_bounds()

Return bounds center of the face.

**Returns:**

a 3D vector.

**Return type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bmesh.types.BMFace.calc_center_median"></a>

#### bmesh.types.BMFace.calc_center_median()

Return median center of the face.

**Returns:**

a 3D vector.

**Return type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bmesh.types.BMFace.calc_center_median_weighted"></a>

#### bmesh.types.BMFace.calc_center_median_weighted()

Return median center of the face weighted by edge lengths.

**Returns:**

a 3D vector.

**Return type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bmesh.types.BMFace.calc_perimeter"></a>

#### bmesh.types.BMFace.calc_perimeter()

Return the perimeter of the face.

**Returns:**

The perimeter of the face.

**Return type:**

float

<a id="bmesh.types.BMFace.calc_tangent_edge"></a>

#### bmesh.types.BMFace.calc_tangent_edge()

Return face tangent based on longest edge.

**Returns:**

a normalized vector.

**Return type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bmesh.types.BMFace.calc_tangent_edge_diagonal"></a>

#### bmesh.types.BMFace.calc_tangent_edge_diagonal()

Return face tangent based on the edge farthest from any vertex.

**Returns:**

a normalized vector.

**Return type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bmesh.types.BMFace.calc_tangent_edge_pair"></a>

#### bmesh.types.BMFace.calc_tangent_edge_pair()

Return face tangent based on the two longest disconnected edges.

- Tris: Use the edge pair with the most similar lengths.
- Quads: Use the longest edge pair.
- NGons: Use the two longest disconnected edges.

**Returns:**

a normalized vector.

**Return type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bmesh.types.BMFace.calc_tangent_vert_diagonal"></a>

#### bmesh.types.BMFace.calc_tangent_vert_diagonal()

Return face tangent based on the two most distant vertices.

**Returns:**

a normalized vector.

**Return type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bmesh.types.BMFace.copy"></a>

#### bmesh.types.BMFace.copy(*, verts=True, edges=True)

Make a copy of this face.

**Parameters:**

- **verts** (bool) – When set, the faces verts will be duplicated too.
- **edges** (bool) – When set, the faces edges will be duplicated too.

**Returns:**

The newly created face.

**Return type:**

[`bmesh.types.BMFace`](#bmesh.types.BMFace "bmesh.types.BMFace")

<a id="bmesh.types.BMFace.copy_from"></a>

#### bmesh.types.BMFace.copy_from(other)

Copy values from another element of matching type.

**Parameters:**

**other** (Self) – Another element of the same type to copy from.

<a id="bmesh.types.BMFace.copy_from_face_interp"></a>

#### bmesh.types.BMFace.copy_from_face_interp(face, vert=True)

Interpolate the customdata from another face onto this one (faces should overlap).

**Parameters:**

- **face** ([`bmesh.types.BMFace`](#bmesh.types.BMFace "bmesh.types.BMFace")) – The face to interpolate data from.
- **vert** (bool) – When True, also copy vertex data.

<a id="bmesh.types.BMFace.hide_set"></a>

#### bmesh.types.BMFace.hide_set(hide)

Set the hide state.
This is different from the *hide* attribute because it updates the selection and hide state of associated geometry.

**Parameters:**

**hide** (bool) – Hidden or visible.

<a id="bmesh.types.BMFace.normal_flip"></a>

#### bmesh.types.BMFace.normal_flip()

Reverses winding of a face, which flips its normal.

<a id="bmesh.types.BMFace.normal_update"></a>

#### bmesh.types.BMFace.normal_update()

Update face normal based on the positions of the face verts.
This does not update the normals of face verts.

<a id="bmesh.types.BMFace.select_set"></a>

#### bmesh.types.BMFace.select_set(select)

Set the selection.
This is different from the *select* attribute because it updates the selection state of associated geometry.

**Parameters:**

**select** (bool) – Select or de-select.

> **Note:**
>
> This flushes selection down (e.g. selecting a face also selects its edges and vertices), but not up (e.g. de-selecting a vertex won’t de-select faces that use it). Before finishing with a mesh, flushing is typically still needed.

<a id="bmesh.types.BMFace.uv_select_set"></a>

#### bmesh.types.BMFace.uv_select_set(select)

Set the UV face selection state.

**Parameters:**

**select** (bool) – Select or de-select.

> **Note:**
>
> This flushes selection down (selecting a face also selects its edges and vertices), but not up. Before finishing with a mesh, flushing with [`bmesh.types.BMesh.uv_select_flush_mode()`](#bmesh.types.BMesh.uv_select_flush_mode "bmesh.types.BMesh.uv_select_flush_mode") is still needed.

<a id="bmesh.types.BMFace.edges"></a>

#### bmesh.types.BMFace.edges

Edges of this face, (read-only).

**Type:**

[`bmesh.types.BMElemSeq`](#bmesh.types.BMElemSeq "bmesh.types.BMElemSeq")[[`bmesh.types.BMEdge`](#bmesh.types.BMEdge "bmesh.types.BMEdge")]

<a id="bmesh.types.BMFace.hide"></a>

#### bmesh.types.BMFace.hide

Hidden state of this element.

**Type:**

bool

<a id="bmesh.types.BMFace.index"></a>

#### bmesh.types.BMFace.index

Index of this element.

**Type:**

int

> **Note:**
>
> This value is not necessarily valid, while editing the mesh it can become *dirty*.
>
> It’s also possible to assign any number to this attribute for a scripts internal logic.
>
> To ensure the value is up to date - see [`bmesh.types.BMElemSeq.index_update()`](#bmesh.types.BMElemSeq.index_update "bmesh.types.BMElemSeq.index_update").

<a id="bmesh.types.BMFace.is_valid"></a>

#### bmesh.types.BMFace.is_valid

True when this element is valid (hasn’t been freed or removed).

**Type:**

bool

<a id="bmesh.types.BMFace.loops"></a>

#### bmesh.types.BMFace.loops

Loops of this face, (read-only).

**Type:**

[`bmesh.types.BMElemSeq`](#bmesh.types.BMElemSeq "bmesh.types.BMElemSeq")[[`bmesh.types.BMLoop`](#bmesh.types.BMLoop "bmesh.types.BMLoop")]

<a id="bmesh.types.BMFace.material_index"></a>

#### bmesh.types.BMFace.material_index

The face’s material index.

**Type:**

int

<a id="bmesh.types.BMFace.normal"></a>

#### bmesh.types.BMFace.normal

The normal for this face as a 3D, wrapped vector.

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bmesh.types.BMFace.select"></a>

#### bmesh.types.BMFace.select

Selected state of this element.

**Type:**

bool

<a id="bmesh.types.BMFace.smooth"></a>

#### bmesh.types.BMFace.smooth

Smooth state of this element.

**Type:**

bool

<a id="bmesh.types.BMFace.tag"></a>

#### bmesh.types.BMFace.tag

Generic attribute scripts can use for own logic

**Type:**

bool

<a id="bmesh.types.BMFace.uv_select"></a>

#### bmesh.types.BMFace.uv_select

UV selected state of this element.

**Type:**

bool

<a id="bmesh.types.BMFace.verts"></a>

#### bmesh.types.BMFace.verts

Verts of this face, (read-only).

**Type:**

[`bmesh.types.BMElemSeq`](#bmesh.types.BMElemSeq "bmesh.types.BMElemSeq")[[`bmesh.types.BMVert`](#bmesh.types.BMVert "bmesh.types.BMVert")]

Special Methods

<a id="bmesh.types.BMFace.__getitem__"></a>

#### bmesh.types.BMFace.__getitem__(key)

**Parameters:**

**key** (int) – Index or key.

**Return type:**

float

<a id="bmesh.types.BMFace.__hash__"></a>

#### bmesh.types.BMFace.__hash__()

**Return type:**

int

<a id="bmesh.types.BMFace.__repr__"></a>

#### bmesh.types.BMFace.__repr__()

**Return type:**

str

<a id="bmesh.types.BMFace.__setitem__"></a>

#### bmesh.types.BMFace.__setitem__(key, value)

**Parameters:**

- **key** (int) – Index or key.
- **value** (object) – Value to assign.

<a id="bmesh.types.BMLoop"></a>

### class bmesh.types.BMLoop

This is normally accessed from [`bmesh.types.BMFace.loops`](#bmesh.types.BMFace.loops "bmesh.types.BMFace.loops") where each face loop represents a corner of the face.

<a id="bmesh.types.BMLoop.calc_angle"></a>

#### bmesh.types.BMLoop.calc_angle()

Return the angle at this loops corner of the face.
This is calculated so sharper corners give lower angles.

**Returns:**

The angle in radians.

**Return type:**

float

<a id="bmesh.types.BMLoop.calc_normal"></a>

#### bmesh.types.BMLoop.calc_normal()

Return normal at this loops corner of the face.
Falls back to the face normal for straight lines.

**Returns:**

a normalized vector.

**Return type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bmesh.types.BMLoop.calc_tangent"></a>

#### bmesh.types.BMLoop.calc_tangent()

Return the tangent at this loops corner of the face (pointing inward into the face).
Falls back to the face normal for straight lines.

**Returns:**

a normalized vector.

**Return type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bmesh.types.BMLoop.copy_from"></a>

#### bmesh.types.BMLoop.copy_from(other)

Copy values from another element of matching type.

**Parameters:**

**other** (Self) – Another element of the same type to copy from.

<a id="bmesh.types.BMLoop.copy_from_face_interp"></a>

#### bmesh.types.BMLoop.copy_from_face_interp(face, vert=True, multires=True)

Interpolate the customdata from a face onto this loop (the loop’s vert should overlap the face).

**Parameters:**

- **face** ([`bmesh.types.BMFace`](#bmesh.types.BMFace "bmesh.types.BMFace")) – The face to interpolate data from.
- **vert** (bool) – When enabled, interpolate the loop’s vertex data (optional).
- **multires** (bool) – When enabled, interpolate the loop’s multires data (optional).

<a id="bmesh.types.BMLoop.uv_select_edge_set"></a>

#### bmesh.types.BMLoop.uv_select_edge_set(select)

Set the UV edge selection state.

**Parameters:**

**select** (bool) – Select or de-select.

> **Note:**
>
> This flushes selection down (selecting an edge also selects its vertices), but not up (de-selecting a vertex won’t de-select the edges & faces that use it). Before finishing with a mesh, flushing with [`bmesh.types.BMesh.uv_select_flush_mode()`](#bmesh.types.BMesh.uv_select_flush_mode "bmesh.types.BMesh.uv_select_flush_mode") is still needed.

<a id="bmesh.types.BMLoop.uv_select_vert_set"></a>

#### bmesh.types.BMLoop.uv_select_vert_set(select)

Set the UV vertex selection state.

**Parameters:**

**select** (bool) – Select or de-select.

> **Note:**
>
> This does not flush selection, so selecting a vertex won’t select the edges & faces that use it. Before finishing with a mesh, flushing with [`bmesh.types.BMesh.uv_select_flush_mode()`](#bmesh.types.BMesh.uv_select_flush_mode "bmesh.types.BMesh.uv_select_flush_mode") is still needed.

<a id="bmesh.types.BMLoop.edge"></a>

#### bmesh.types.BMLoop.edge

The loop’s edge (between this loop and the next), (read-only).

**Type:**

[`bmesh.types.BMEdge`](#bmesh.types.BMEdge "bmesh.types.BMEdge")

<a id="bmesh.types.BMLoop.face"></a>

#### bmesh.types.BMLoop.face

The face this loop belongs to (read-only).

**Type:**

[`bmesh.types.BMFace`](#bmesh.types.BMFace "bmesh.types.BMFace")

<a id="bmesh.types.BMLoop.index"></a>

#### bmesh.types.BMLoop.index

Index of this element.

**Type:**

int

> **Note:**
>
> This value is not necessarily valid, while editing the mesh it can become *dirty*.
>
> It’s also possible to assign any number to this attribute for a scripts internal logic.
>
> To ensure the value is up to date - see [`bmesh.types.BMElemSeq.index_update()`](#bmesh.types.BMElemSeq.index_update "bmesh.types.BMElemSeq.index_update").

<a id="bmesh.types.BMLoop.is_convex"></a>

#### bmesh.types.BMLoop.is_convex

True when this loop is at the convex corner of a face, depends on a valid face normal (read-only).

**Type:**

bool

<a id="bmesh.types.BMLoop.is_valid"></a>

#### bmesh.types.BMLoop.is_valid

True when this element is valid (hasn’t been freed or removed).

**Type:**

bool

<a id="bmesh.types.BMLoop.link_loop_next"></a>

#### bmesh.types.BMLoop.link_loop_next

The next face corner (read-only).

**Type:**

[`bmesh.types.BMLoop`](#bmesh.types.BMLoop "bmesh.types.BMLoop")

<a id="bmesh.types.BMLoop.link_loop_prev"></a>

#### bmesh.types.BMLoop.link_loop_prev

The previous face corner (read-only).

**Type:**

[`bmesh.types.BMLoop`](#bmesh.types.BMLoop "bmesh.types.BMLoop")

<a id="bmesh.types.BMLoop.link_loop_radial_next"></a>

#### bmesh.types.BMLoop.link_loop_radial_next

The next loop around the edge (read-only).

**Type:**

[`bmesh.types.BMLoop`](#bmesh.types.BMLoop "bmesh.types.BMLoop")

<a id="bmesh.types.BMLoop.link_loop_radial_prev"></a>

#### bmesh.types.BMLoop.link_loop_radial_prev

The previous loop around the edge (read-only).

**Type:**

[`bmesh.types.BMLoop`](#bmesh.types.BMLoop "bmesh.types.BMLoop")

<a id="bmesh.types.BMLoop.link_loops"></a>

#### bmesh.types.BMLoop.link_loops

Loops connected to this loop, (read-only).

**Type:**

[`bmesh.types.BMElemSeq`](#bmesh.types.BMElemSeq "bmesh.types.BMElemSeq")[[`bmesh.types.BMLoop`](#bmesh.types.BMLoop "bmesh.types.BMLoop")]

<a id="bmesh.types.BMLoop.tag"></a>

#### bmesh.types.BMLoop.tag

Generic attribute scripts can use for own logic

**Type:**

bool

<a id="bmesh.types.BMLoop.uv_select_edge"></a>

#### bmesh.types.BMLoop.uv_select_edge

UV edge selected state of this loop.

**Type:**

bool

<a id="bmesh.types.BMLoop.uv_select_vert"></a>

#### bmesh.types.BMLoop.uv_select_vert

UV vertex selected state of this loop.

**Type:**

bool

<a id="bmesh.types.BMLoop.vert"></a>

#### bmesh.types.BMLoop.vert

The loop’s vertex (read-only).

**Type:**

[`bmesh.types.BMVert`](#bmesh.types.BMVert "bmesh.types.BMVert")

Special Methods

<a id="bmesh.types.BMLoop.__getitem__"></a>

#### bmesh.types.BMLoop.__getitem__(key)

**Parameters:**

**key** (int) – Index or key.

**Return type:**

float

<a id="bmesh.types.BMLoop.__hash__"></a>

#### bmesh.types.BMLoop.__hash__()

**Return type:**

int

<a id="bmesh.types.BMLoop.__repr__"></a>

#### bmesh.types.BMLoop.__repr__()

**Return type:**

str

<a id="bmesh.types.BMLoop.__setitem__"></a>

#### bmesh.types.BMLoop.__setitem__(key, value)

**Parameters:**

- **key** (int) – Index or key.
- **value** (object) – Value to assign.

<a id="sequence-accessors"></a>

## Sequence Accessors

<a id="bmesh.types.BMElemSeq"></a>

### class bmesh.types.BMElemSeq

General sequence type used for accessing any sequence of
[`bmesh.types.BMVert`](#bmesh.types.BMVert "bmesh.types.BMVert"), [`bmesh.types.BMEdge`](#bmesh.types.BMEdge "bmesh.types.BMEdge"), [`bmesh.types.BMFace`](#bmesh.types.BMFace "bmesh.types.BMFace"), [`bmesh.types.BMLoop`](#bmesh.types.BMLoop "bmesh.types.BMLoop").

When accessed via [`bmesh.types.BMesh.verts`](#bmesh.types.BMesh.verts "bmesh.types.BMesh.verts"), [`bmesh.types.BMesh.edges`](#bmesh.types.BMesh.edges "bmesh.types.BMesh.edges"), [`bmesh.types.BMesh.faces`](#bmesh.types.BMesh.faces "bmesh.types.BMesh.faces")
there are also functions to create/remove items.

<a id="bmesh.types.BMElemSeq.index_update"></a>

#### bmesh.types.BMElemSeq.index_update()

Initialize the index values of this sequence.

This is the equivalent of looping over all elements and assigning the index values.

```python
for index, ele in enumerate(sequence):
    ele.index = index
```

> **Note:**
>
> Running this on sequences besides [`bmesh.types.BMesh.verts`](#bmesh.types.BMesh.verts "bmesh.types.BMesh.verts"), [`bmesh.types.BMesh.edges`](#bmesh.types.BMesh.edges "bmesh.types.BMesh.edges"), [`bmesh.types.BMesh.faces`](#bmesh.types.BMesh.faces "bmesh.types.BMesh.faces")
> works but won’t result in each element having a valid index, instead its order in the sequence will be set.

Special Methods

<a id="bmesh.types.BMElemSeq.__contains__"></a>

#### bmesh.types.BMElemSeq.__contains__(item)

**Parameters:**

**item** (object) – Item to test for membership.

**Return type:**

bool

<a id="bmesh.types.BMElemSeq.__getitem__"></a>

#### bmesh.types.BMElemSeq.__getitem__(key)

**Parameters:**

**key** (int) – Index or key.

**Return type:**

[`BMVert`](#bmesh.types.BMVert "bmesh.types.BMVert") | [`BMEdge`](#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`BMFace`](#bmesh.types.BMFace "bmesh.types.BMFace")

<a id="bmesh.types.BMElemSeq.__iter__"></a>

#### bmesh.types.BMElemSeq.__iter__()

**Return type:**

[`BMElemSeq`](#bmesh.types.BMElemSeq "bmesh.types.BMElemSeq")

<a id="bmesh.types.BMElemSeq.__len__"></a>

#### bmesh.types.BMElemSeq.__len__()

**Return type:**

int

<a id="bmesh.types.BMVertSeq"></a>

### class bmesh.types.BMVertSeq

<a id="bmesh.types.BMVertSeq.ensure_lookup_table"></a>

#### bmesh.types.BMVertSeq.ensure_lookup_table()

Ensure internal data needed for int subscript access is initialized with verts/edges/faces, eg `bm.verts[index]`.

This needs to be called again after adding/removing data in this sequence.

<a id="bmesh.types.BMVertSeq.index_update"></a>

#### bmesh.types.BMVertSeq.index_update()

Initialize the index values of this sequence.

This is the equivalent of looping over all elements and assigning the index values.

```python
for index, ele in enumerate(sequence):
    ele.index = index
```

> **Note:**
>
> Running this on sequences besides [`bmesh.types.BMesh.verts`](#bmesh.types.BMesh.verts "bmesh.types.BMesh.verts"), [`bmesh.types.BMesh.edges`](#bmesh.types.BMesh.edges "bmesh.types.BMesh.edges"), [`bmesh.types.BMesh.faces`](#bmesh.types.BMesh.faces "bmesh.types.BMesh.faces")
> works but won’t result in each element having a valid index, instead its order in the sequence will be set.

<a id="bmesh.types.BMVertSeq.new"></a>

#### bmesh.types.BMVertSeq.new(co=(0.0, 0.0, 0.0), source=None)

Create a new vertex.

**Parameters:**

- **co** (tuple[float, float, float] | Sequence[float]) – The initial location of the vertex (optional argument).
- **source** ([`bmesh.types.BMVert`](#bmesh.types.BMVert "bmesh.types.BMVert") | None) – Existing vert to initialize settings.

**Returns:**

The newly created vertex.

**Return type:**

[`bmesh.types.BMVert`](#bmesh.types.BMVert "bmesh.types.BMVert")

<a id="bmesh.types.BMVertSeq.remove"></a>

#### bmesh.types.BMVertSeq.remove(vert)

Remove a vert.

**Parameters:**

**vert** ([`bmesh.types.BMVert`](#bmesh.types.BMVert "bmesh.types.BMVert")) – The vert to remove.

<a id="bmesh.types.BMVertSeq.sort"></a>

#### bmesh.types.BMVertSeq.sort(*, key=None, reverse=False)

Sort the elements of this sequence, using an optional custom sort key.
Indices of elements are not changed, [`bmesh.types.BMElemSeq.index_update()`](#bmesh.types.BMElemSeq.index_update "bmesh.types.BMElemSeq.index_update") can be used for that.

**Parameters:**

- **key** (Callable[[[`bmesh.types.BMVert`](#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](#bmesh.types.BMFace "bmesh.types.BMFace")], int] | None) – The key that sets the ordering of the elements.
- **reverse** (bool) – Reverse the order of the elements

> **Note:**
>
> When the ‘key’ argument is not provided, the elements are reordered following their current index value.
> In particular this can be used by setting indices manually before calling this method.

> **Warning:**
>
> Existing references to the N’th element, will continue to point the data at that index.

<a id="bmesh.types.BMVertSeq.layers"></a>

#### bmesh.types.BMVertSeq.layers

custom-data layers (read-only).

**Type:**

[`bmesh.types.BMLayerAccessVert`](#bmesh.types.BMLayerAccessVert "bmesh.types.BMLayerAccessVert")

Special Methods

<a id="bmesh.types.BMVertSeq.__contains__"></a>

#### bmesh.types.BMVertSeq.__contains__(item)

**Parameters:**

**item** (object) – Item to test for membership.

**Return type:**

bool

<a id="bmesh.types.BMVertSeq.__getitem__"></a>

#### bmesh.types.BMVertSeq.__getitem__(key)

**Parameters:**

**key** (int) – Index or key.

**Return type:**

[`BMVert`](#bmesh.types.BMVert "bmesh.types.BMVert")

<a id="bmesh.types.BMVertSeq.__iter__"></a>

#### bmesh.types.BMVertSeq.__iter__()

**Return type:**

[`BMVertSeq`](#bmesh.types.BMVertSeq "bmesh.types.BMVertSeq")

<a id="bmesh.types.BMVertSeq.__len__"></a>

#### bmesh.types.BMVertSeq.__len__()

**Return type:**

int

<a id="bmesh.types.BMEdgeSeq"></a>

### class bmesh.types.BMEdgeSeq

<a id="bmesh.types.BMEdgeSeq.ensure_lookup_table"></a>

#### bmesh.types.BMEdgeSeq.ensure_lookup_table()

Ensure internal data needed for int subscript access is initialized with verts/edges/faces, eg `bm.verts[index]`.

This needs to be called again after adding/removing data in this sequence.

<a id="bmesh.types.BMEdgeSeq.get"></a>

#### bmesh.types.BMEdgeSeq.get(verts, fallback=None)

Return an edge which uses the **verts** passed.

**Parameters:**

- **verts** (Sequence[[`bmesh.types.BMVert`](#bmesh.types.BMVert "bmesh.types.BMVert")]) – Pair of verts (exactly 2).
- **fallback** (Any) – Return this value if nothing is found.

**Returns:**

The edge found or the fallback value.

**Return type:**

[`bmesh.types.BMEdge`](#bmesh.types.BMEdge "bmesh.types.BMEdge") | None

<a id="bmesh.types.BMEdgeSeq.index_update"></a>

#### bmesh.types.BMEdgeSeq.index_update()

Initialize the index values of this sequence.

This is the equivalent of looping over all elements and assigning the index values.

```python
for index, ele in enumerate(sequence):
    ele.index = index
```

> **Note:**
>
> Running this on sequences besides [`bmesh.types.BMesh.verts`](#bmesh.types.BMesh.verts "bmesh.types.BMesh.verts"), [`bmesh.types.BMesh.edges`](#bmesh.types.BMesh.edges "bmesh.types.BMesh.edges"), [`bmesh.types.BMesh.faces`](#bmesh.types.BMesh.faces "bmesh.types.BMesh.faces")
> works but won’t result in each element having a valid index, instead its order in the sequence will be set.

<a id="bmesh.types.BMEdgeSeq.new"></a>

#### bmesh.types.BMEdgeSeq.new(verts, source=None)

Create a new edge from a given pair of verts.

**Parameters:**

- **verts** (Sequence[[`bmesh.types.BMVert`](#bmesh.types.BMVert "bmesh.types.BMVert")]) – Vertex pair.
- **source** ([`bmesh.types.BMEdge`](#bmesh.types.BMEdge "bmesh.types.BMEdge") | None) – Existing edge to initialize settings (optional argument).

**Returns:**

The newly created edge.

**Return type:**

[`bmesh.types.BMEdge`](#bmesh.types.BMEdge "bmesh.types.BMEdge")

<a id="bmesh.types.BMEdgeSeq.remove"></a>

#### bmesh.types.BMEdgeSeq.remove(edge)

Remove an edge.

**Parameters:**

**edge** ([`bmesh.types.BMEdge`](#bmesh.types.BMEdge "bmesh.types.BMEdge")) – The edge to remove.

<a id="bmesh.types.BMEdgeSeq.sort"></a>

#### bmesh.types.BMEdgeSeq.sort(*, key=None, reverse=False)

Sort the elements of this sequence, using an optional custom sort key.
Indices of elements are not changed, [`bmesh.types.BMElemSeq.index_update()`](#bmesh.types.BMElemSeq.index_update "bmesh.types.BMElemSeq.index_update") can be used for that.

**Parameters:**

- **key** (Callable[[[`bmesh.types.BMVert`](#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](#bmesh.types.BMFace "bmesh.types.BMFace")], int] | None) – The key that sets the ordering of the elements.
- **reverse** (bool) – Reverse the order of the elements

> **Note:**
>
> When the ‘key’ argument is not provided, the elements are reordered following their current index value.
> In particular this can be used by setting indices manually before calling this method.

> **Warning:**
>
> Existing references to the N’th element, will continue to point the data at that index.

<a id="bmesh.types.BMEdgeSeq.layers"></a>

#### bmesh.types.BMEdgeSeq.layers

custom-data layers (read-only).

**Type:**

[`bmesh.types.BMLayerAccessEdge`](#bmesh.types.BMLayerAccessEdge "bmesh.types.BMLayerAccessEdge")

Special Methods

<a id="bmesh.types.BMEdgeSeq.__contains__"></a>

#### bmesh.types.BMEdgeSeq.__contains__(item)

**Parameters:**

**item** (object) – Item to test for membership.

**Return type:**

bool

<a id="bmesh.types.BMEdgeSeq.__getitem__"></a>

#### bmesh.types.BMEdgeSeq.__getitem__(key)

**Parameters:**

**key** (int) – Index or key.

**Return type:**

[`BMEdge`](#bmesh.types.BMEdge "bmesh.types.BMEdge")

<a id="bmesh.types.BMEdgeSeq.__iter__"></a>

#### bmesh.types.BMEdgeSeq.__iter__()

**Return type:**

[`BMEdgeSeq`](#bmesh.types.BMEdgeSeq "bmesh.types.BMEdgeSeq")

<a id="bmesh.types.BMEdgeSeq.__len__"></a>

#### bmesh.types.BMEdgeSeq.__len__()

**Return type:**

int

<a id="bmesh.types.BMFaceSeq"></a>

### class bmesh.types.BMFaceSeq

<a id="bmesh.types.BMFaceSeq.ensure_lookup_table"></a>

#### bmesh.types.BMFaceSeq.ensure_lookup_table()

Ensure internal data needed for int subscript access is initialized with verts/edges/faces, eg `bm.verts[index]`.

This needs to be called again after adding/removing data in this sequence.

<a id="bmesh.types.BMFaceSeq.get"></a>

#### bmesh.types.BMFaceSeq.get(verts, fallback=None)

Return a face which uses the **verts** passed.

**Parameters:**

- **verts** (Sequence[[`bmesh.types.BMVert`](#bmesh.types.BMVert "bmesh.types.BMVert")]) – Sequence of verts.
- **fallback** (Any) – Return this value if nothing is found.

**Returns:**

The face found or the fallback value.

**Return type:**

[`bmesh.types.BMFace`](#bmesh.types.BMFace "bmesh.types.BMFace") | None

<a id="bmesh.types.BMFaceSeq.index_update"></a>

#### bmesh.types.BMFaceSeq.index_update()

Initialize the index values of this sequence.

This is the equivalent of looping over all elements and assigning the index values.

```python
for index, ele in enumerate(sequence):
    ele.index = index
```

> **Note:**
>
> Running this on sequences besides [`bmesh.types.BMesh.verts`](#bmesh.types.BMesh.verts "bmesh.types.BMesh.verts"), [`bmesh.types.BMesh.edges`](#bmesh.types.BMesh.edges "bmesh.types.BMesh.edges"), [`bmesh.types.BMesh.faces`](#bmesh.types.BMesh.faces "bmesh.types.BMesh.faces")
> works but won’t result in each element having a valid index, instead its order in the sequence will be set.

<a id="bmesh.types.BMFaceSeq.new"></a>

#### bmesh.types.BMFaceSeq.new(verts, source=None)

Create a new face from a given set of verts.

**Parameters:**

- **verts** (Sequence[[`bmesh.types.BMVert`](#bmesh.types.BMVert "bmesh.types.BMVert")]) – Sequence of 3 or more verts.
- **source** ([`bmesh.types.BMFace`](#bmesh.types.BMFace "bmesh.types.BMFace") | None) – Existing face to initialize settings (optional argument).

**Returns:**

The newly created face.

**Return type:**

[`bmesh.types.BMFace`](#bmesh.types.BMFace "bmesh.types.BMFace")

<a id="bmesh.types.BMFaceSeq.remove"></a>

#### bmesh.types.BMFaceSeq.remove(face)

Remove a face.

**Parameters:**

**face** ([`bmesh.types.BMFace`](#bmesh.types.BMFace "bmesh.types.BMFace")) – The face to remove.

<a id="bmesh.types.BMFaceSeq.sort"></a>

#### bmesh.types.BMFaceSeq.sort(*, key=None, reverse=False)

Sort the elements of this sequence, using an optional custom sort key.
Indices of elements are not changed, [`bmesh.types.BMElemSeq.index_update()`](#bmesh.types.BMElemSeq.index_update "bmesh.types.BMElemSeq.index_update") can be used for that.

**Parameters:**

- **key** (Callable[[[`bmesh.types.BMVert`](#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](#bmesh.types.BMFace "bmesh.types.BMFace")], int] | None) – The key that sets the ordering of the elements.
- **reverse** (bool) – Reverse the order of the elements

> **Note:**
>
> When the ‘key’ argument is not provided, the elements are reordered following their current index value.
> In particular this can be used by setting indices manually before calling this method.

> **Warning:**
>
> Existing references to the N’th element, will continue to point the data at that index.

<a id="bmesh.types.BMFaceSeq.active"></a>

#### bmesh.types.BMFaceSeq.active

active face.

**Type:**

[`bmesh.types.BMFace`](#bmesh.types.BMFace "bmesh.types.BMFace") | None

<a id="bmesh.types.BMFaceSeq.layers"></a>

#### bmesh.types.BMFaceSeq.layers

custom-data layers (read-only).

**Type:**

[`bmesh.types.BMLayerAccessFace`](#bmesh.types.BMLayerAccessFace "bmesh.types.BMLayerAccessFace")

Special Methods

<a id="bmesh.types.BMFaceSeq.__contains__"></a>

#### bmesh.types.BMFaceSeq.__contains__(item)

**Parameters:**

**item** (object) – Item to test for membership.

**Return type:**

bool

<a id="bmesh.types.BMFaceSeq.__getitem__"></a>

#### bmesh.types.BMFaceSeq.__getitem__(key)

**Parameters:**

**key** (int) – Index or key.

**Return type:**

[`BMFace`](#bmesh.types.BMFace "bmesh.types.BMFace")

<a id="bmesh.types.BMFaceSeq.__iter__"></a>

#### bmesh.types.BMFaceSeq.__iter__()

**Return type:**

[`BMFaceSeq`](#bmesh.types.BMFaceSeq "bmesh.types.BMFaceSeq")

<a id="bmesh.types.BMFaceSeq.__len__"></a>

#### bmesh.types.BMFaceSeq.__len__()

**Return type:**

int

<a id="bmesh.types.BMLoopSeq"></a>

### class bmesh.types.BMLoopSeq

<a id="bmesh.types.BMLoopSeq.layers"></a>

#### bmesh.types.BMLoopSeq.layers

custom-data layers (read-only).

**Type:**

[`bmesh.types.BMLayerAccessLoop`](#bmesh.types.BMLayerAccessLoop "bmesh.types.BMLayerAccessLoop")

<a id="bmesh.types.BMIter"></a>

### class bmesh.types.BMIter

Internal BMesh type for looping over verts/faces/edges,
used for iterating over [`bmesh.types.BMElemSeq`](#bmesh.types.BMElemSeq "bmesh.types.BMElemSeq") types.

Special Methods

<a id="bmesh.types.BMIter.__iter__"></a>

#### bmesh.types.BMIter.__iter__()

**Return type:**

[`BMIter`](#bmesh.types.BMIter "bmesh.types.BMIter")

<a id="bmesh.types.BMIter.__next__"></a>

#### bmesh.types.BMIter.__next__()

**Return type:**

Any

<a id="selection-history"></a>

## Selection History

<a id="bmesh.types.BMEditSelSeq"></a>

### class bmesh.types.BMEditSelSeq

<a id="bmesh.types.BMEditSelSeq.add"></a>

#### bmesh.types.BMEditSelSeq.add(element)

Add an element to the selection history (no action taken if its already added).

**Parameters:**

**element** ([`BMVert`](#bmesh.types.BMVert "bmesh.types.BMVert") | [`BMEdge`](#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`BMFace`](#bmesh.types.BMFace "bmesh.types.BMFace")) – The element to add.

<a id="bmesh.types.BMEditSelSeq.clear"></a>

#### bmesh.types.BMEditSelSeq.clear()

Empties the selection history.

<a id="bmesh.types.BMEditSelSeq.discard"></a>

#### bmesh.types.BMEditSelSeq.discard(element)

Discard an element from the selection history.

Like remove but doesn’t raise an error when the element is not in the selection list.

**Parameters:**

**element** ([`BMVert`](#bmesh.types.BMVert "bmesh.types.BMVert") | [`BMEdge`](#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`BMFace`](#bmesh.types.BMFace "bmesh.types.BMFace")) – The element to discard.

<a id="bmesh.types.BMEditSelSeq.remove"></a>

#### bmesh.types.BMEditSelSeq.remove(element)

Remove an element from the selection history.

**Parameters:**

**element** ([`BMVert`](#bmesh.types.BMVert "bmesh.types.BMVert") | [`BMEdge`](#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`BMFace`](#bmesh.types.BMFace "bmesh.types.BMFace")) – The element to remove.

<a id="bmesh.types.BMEditSelSeq.validate"></a>

#### bmesh.types.BMEditSelSeq.validate()

Ensures all elements in the selection history are selected.

<a id="bmesh.types.BMEditSelSeq.active"></a>

#### bmesh.types.BMEditSelSeq.active

The last selected element or None (read-only).

**Type:**

[`bmesh.types.BMVert`](#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](#bmesh.types.BMFace "bmesh.types.BMFace") | None

Special Methods

<a id="bmesh.types.BMEditSelSeq.__contains__"></a>

#### bmesh.types.BMEditSelSeq.__contains__(item)

**Parameters:**

**item** (object) – Item to test for membership.

**Return type:**

bool

<a id="bmesh.types.BMEditSelSeq.__getitem__"></a>

#### bmesh.types.BMEditSelSeq.__getitem__(key)

**Parameters:**

**key** (int) – Index or key.

**Return type:**

[`BMVert`](#bmesh.types.BMVert "bmesh.types.BMVert") | [`BMEdge`](#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`BMFace`](#bmesh.types.BMFace "bmesh.types.BMFace")

<a id="bmesh.types.BMEditSelSeq.__iter__"></a>

#### bmesh.types.BMEditSelSeq.__iter__()

**Return type:**

[`BMEditSelSeq`](#bmesh.types.BMEditSelSeq "bmesh.types.BMEditSelSeq")

<a id="bmesh.types.BMEditSelSeq.__len__"></a>

#### bmesh.types.BMEditSelSeq.__len__()

**Return type:**

int

<a id="bmesh.types.BMEditSelIter"></a>

### class bmesh.types.BMEditSelIter

Special Methods

<a id="bmesh.types.BMEditSelIter.__iter__"></a>

#### bmesh.types.BMEditSelIter.__iter__()

**Return type:**

[`BMEditSelIter`](#bmesh.types.BMEditSelIter "bmesh.types.BMEditSelIter")

<a id="bmesh.types.BMEditSelIter.__next__"></a>

#### bmesh.types.BMEditSelIter.__next__()

**Return type:**

Any

<a id="custom-data-layer-access"></a>

## Custom-Data Layer Access

<a id="bmesh.types.BMLayerAccessVert"></a>

### class bmesh.types.BMLayerAccessVert

Exposes custom-data layer attributes.

<a id="bmesh.types.BMLayerAccessVert.bool"></a>

#### bmesh.types.BMLayerAccessVert.bool

Generic boolean custom-data layer.

**Type:**

[`bmesh.types.BMLayerCollection`](#bmesh.types.BMLayerCollection "bmesh.types.BMLayerCollection")[bool]

<a id="bmesh.types.BMLayerAccessVert.color"></a>

#### bmesh.types.BMLayerAccessVert.color

Generic RGBA color with 8-bit precision custom-data layer.

**Type:**

[`bmesh.types.BMLayerCollection`](#bmesh.types.BMLayerCollection "bmesh.types.BMLayerCollection")[[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")]

<a id="bmesh.types.BMLayerAccessVert.deform"></a>

#### bmesh.types.BMLayerAccessVert.deform

Vertex deform weight [`bmesh.types.BMDeformVert`](#bmesh.types.BMDeformVert "bmesh.types.BMDeformVert") (TODO).

**Type:**

[`bmesh.types.BMLayerCollection`](#bmesh.types.BMLayerCollection "bmesh.types.BMLayerCollection")[[`bmesh.types.BMDeformVert`](#bmesh.types.BMDeformVert "bmesh.types.BMDeformVert")]

<a id="bmesh.types.BMLayerAccessVert.float"></a>

#### bmesh.types.BMLayerAccessVert.float

Generic float custom-data layer.

**Type:**

[`bmesh.types.BMLayerCollection`](#bmesh.types.BMLayerCollection "bmesh.types.BMLayerCollection")[float]

<a id="bmesh.types.BMLayerAccessVert.float_color"></a>

#### bmesh.types.BMLayerAccessVert.float_color

Generic RGBA color with float precision custom-data layer.

**Type:**

[`bmesh.types.BMLayerCollection`](#bmesh.types.BMLayerCollection "bmesh.types.BMLayerCollection")[[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")]

<a id="bmesh.types.BMLayerAccessVert.float_vector"></a>

#### bmesh.types.BMLayerAccessVert.float_vector

Generic 3D vector with float precision custom-data layer.

**Type:**

[`bmesh.types.BMLayerCollection`](#bmesh.types.BMLayerCollection "bmesh.types.BMLayerCollection")[[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")]

<a id="bmesh.types.BMLayerAccessVert.int"></a>

#### bmesh.types.BMLayerAccessVert.int

Generic int custom-data layer.

**Type:**

[`bmesh.types.BMLayerCollection`](#bmesh.types.BMLayerCollection "bmesh.types.BMLayerCollection")[int]

<a id="bmesh.types.BMLayerAccessVert.shape"></a>

#### bmesh.types.BMLayerAccessVert.shape

Vertex shape-key absolute location (as a 3D Vector).

**Type:**

[`bmesh.types.BMLayerCollection`](#bmesh.types.BMLayerCollection "bmesh.types.BMLayerCollection")[[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")]

<a id="bmesh.types.BMLayerAccessVert.skin"></a>

#### bmesh.types.BMLayerAccessVert.skin

Accessor for skin layer.

**Type:**

[`bmesh.types.BMLayerCollection`](#bmesh.types.BMLayerCollection "bmesh.types.BMLayerCollection")[`bmesh.types.BMVertSkin`]

<a id="bmesh.types.BMLayerAccessVert.string"></a>

#### bmesh.types.BMLayerAccessVert.string

Generic string custom-data layer (exposed as bytes, 255 max length).

**Type:**

[`bmesh.types.BMLayerCollection`](#bmesh.types.BMLayerCollection "bmesh.types.BMLayerCollection")[bytes]

<a id="bmesh.types.BMLayerAccessEdge"></a>

### class bmesh.types.BMLayerAccessEdge

Exposes custom-data layer attributes.

<a id="bmesh.types.BMLayerAccessEdge.bool"></a>

#### bmesh.types.BMLayerAccessEdge.bool

Generic boolean custom-data layer.

**Type:**

[`bmesh.types.BMLayerCollection`](#bmesh.types.BMLayerCollection "bmesh.types.BMLayerCollection")[bool]

<a id="bmesh.types.BMLayerAccessEdge.color"></a>

#### bmesh.types.BMLayerAccessEdge.color

Generic RGBA color with 8-bit precision custom-data layer.

**Type:**

[`bmesh.types.BMLayerCollection`](#bmesh.types.BMLayerCollection "bmesh.types.BMLayerCollection")[[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")]

<a id="bmesh.types.BMLayerAccessEdge.float"></a>

#### bmesh.types.BMLayerAccessEdge.float

Generic float custom-data layer.

**Type:**

[`bmesh.types.BMLayerCollection`](#bmesh.types.BMLayerCollection "bmesh.types.BMLayerCollection")[float]

<a id="bmesh.types.BMLayerAccessEdge.float_color"></a>

#### bmesh.types.BMLayerAccessEdge.float_color

Generic RGBA color with float precision custom-data layer.

**Type:**

[`bmesh.types.BMLayerCollection`](#bmesh.types.BMLayerCollection "bmesh.types.BMLayerCollection")[[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")]

<a id="bmesh.types.BMLayerAccessEdge.float_vector"></a>

#### bmesh.types.BMLayerAccessEdge.float_vector

Generic 3D vector with float precision custom-data layer.

**Type:**

[`bmesh.types.BMLayerCollection`](#bmesh.types.BMLayerCollection "bmesh.types.BMLayerCollection")[[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")]

<a id="bmesh.types.BMLayerAccessEdge.int"></a>

#### bmesh.types.BMLayerAccessEdge.int

Generic int custom-data layer.

**Type:**

[`bmesh.types.BMLayerCollection`](#bmesh.types.BMLayerCollection "bmesh.types.BMLayerCollection")[int]

<a id="bmesh.types.BMLayerAccessEdge.string"></a>

#### bmesh.types.BMLayerAccessEdge.string

Generic string custom-data layer (exposed as bytes, 255 max length).

**Type:**

[`bmesh.types.BMLayerCollection`](#bmesh.types.BMLayerCollection "bmesh.types.BMLayerCollection")[bytes]

<a id="bmesh.types.BMLayerAccessFace"></a>

### class bmesh.types.BMLayerAccessFace

Exposes custom-data layer attributes.

<a id="bmesh.types.BMLayerAccessFace.bool"></a>

#### bmesh.types.BMLayerAccessFace.bool

Generic boolean custom-data layer.

**Type:**

[`bmesh.types.BMLayerCollection`](#bmesh.types.BMLayerCollection "bmesh.types.BMLayerCollection")[bool]

<a id="bmesh.types.BMLayerAccessFace.color"></a>

#### bmesh.types.BMLayerAccessFace.color

Generic RGBA color with 8-bit precision custom-data layer.

**Type:**

[`bmesh.types.BMLayerCollection`](#bmesh.types.BMLayerCollection "bmesh.types.BMLayerCollection")[[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")]

<a id="bmesh.types.BMLayerAccessFace.float"></a>

#### bmesh.types.BMLayerAccessFace.float

Generic float custom-data layer.

**Type:**

[`bmesh.types.BMLayerCollection`](#bmesh.types.BMLayerCollection "bmesh.types.BMLayerCollection")[float]

<a id="bmesh.types.BMLayerAccessFace.float_color"></a>

#### bmesh.types.BMLayerAccessFace.float_color

Generic RGBA color with float precision custom-data layer.

**Type:**

[`bmesh.types.BMLayerCollection`](#bmesh.types.BMLayerCollection "bmesh.types.BMLayerCollection")[[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")]

<a id="bmesh.types.BMLayerAccessFace.float_vector"></a>

#### bmesh.types.BMLayerAccessFace.float_vector

Generic 3D vector with float precision custom-data layer.

**Type:**

[`bmesh.types.BMLayerCollection`](#bmesh.types.BMLayerCollection "bmesh.types.BMLayerCollection")[[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")]

<a id="bmesh.types.BMLayerAccessFace.int"></a>

#### bmesh.types.BMLayerAccessFace.int

Generic int custom-data layer.

**Type:**

[`bmesh.types.BMLayerCollection`](#bmesh.types.BMLayerCollection "bmesh.types.BMLayerCollection")[int]

<a id="bmesh.types.BMLayerAccessFace.string"></a>

#### bmesh.types.BMLayerAccessFace.string

Generic string custom-data layer (exposed as bytes, 255 max length).

**Type:**

[`bmesh.types.BMLayerCollection`](#bmesh.types.BMLayerCollection "bmesh.types.BMLayerCollection")[bytes]

<a id="bmesh.types.BMLayerAccessLoop"></a>

### class bmesh.types.BMLayerAccessLoop

Exposes custom-data layer attributes.

<a id="bmesh.types.BMLayerAccessLoop.bool"></a>

#### bmesh.types.BMLayerAccessLoop.bool

Generic boolean custom-data layer.

**Type:**

[`bmesh.types.BMLayerCollection`](#bmesh.types.BMLayerCollection "bmesh.types.BMLayerCollection")[bool]

<a id="bmesh.types.BMLayerAccessLoop.color"></a>

#### bmesh.types.BMLayerAccessLoop.color

Generic RGBA color with 8-bit precision custom-data layer.

**Type:**

[`bmesh.types.BMLayerCollection`](#bmesh.types.BMLayerCollection "bmesh.types.BMLayerCollection")[[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")]

<a id="bmesh.types.BMLayerAccessLoop.float"></a>

#### bmesh.types.BMLayerAccessLoop.float

Generic float custom-data layer.

**Type:**

[`bmesh.types.BMLayerCollection`](#bmesh.types.BMLayerCollection "bmesh.types.BMLayerCollection")[float]

<a id="bmesh.types.BMLayerAccessLoop.float_color"></a>

#### bmesh.types.BMLayerAccessLoop.float_color

Generic RGBA color with float precision custom-data layer.

**Type:**

[`bmesh.types.BMLayerCollection`](#bmesh.types.BMLayerCollection "bmesh.types.BMLayerCollection")[[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")]

<a id="bmesh.types.BMLayerAccessLoop.float_vector"></a>

#### bmesh.types.BMLayerAccessLoop.float_vector

Generic 3D vector with float precision custom-data layer.

**Type:**

[`bmesh.types.BMLayerCollection`](#bmesh.types.BMLayerCollection "bmesh.types.BMLayerCollection")[[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")]

<a id="bmesh.types.BMLayerAccessLoop.int"></a>

#### bmesh.types.BMLayerAccessLoop.int

Generic int custom-data layer.

**Type:**

[`bmesh.types.BMLayerCollection`](#bmesh.types.BMLayerCollection "bmesh.types.BMLayerCollection")[int]

<a id="bmesh.types.BMLayerAccessLoop.string"></a>

#### bmesh.types.BMLayerAccessLoop.string

Generic string custom-data layer (exposed as bytes, 255 max length).

**Type:**

[`bmesh.types.BMLayerCollection`](#bmesh.types.BMLayerCollection "bmesh.types.BMLayerCollection")[bytes]

<a id="bmesh.types.BMLayerAccessLoop.uv"></a>

#### bmesh.types.BMLayerAccessLoop.uv

Accessor for [`bmesh.types.BMLoopUV`](#bmesh.types.BMLoopUV "bmesh.types.BMLoopUV") UV (as a 2D Vector).

**Type:**

[`bmesh.types.BMLayerCollection`](#bmesh.types.BMLayerCollection "bmesh.types.BMLayerCollection")[[`bmesh.types.BMLoopUV`](#bmesh.types.BMLoopUV "bmesh.types.BMLoopUV")]

<a id="bmesh.types.BMLayerCollection"></a>

### class bmesh.types.BMLayerCollection

Gives access to a collection of custom-data layers of the same type and behaves like Python dictionaries, except for the ability to do list like index access.

<a id="bmesh.types.BMLayerCollection.get"></a>

#### bmesh.types.BMLayerCollection.get(key, default=None)

Returns the value of the layer matching the key or default
when not found (matches Python’s dictionary function of the same name).

**Parameters:**

- **key** (str) – The key associated with the layer.
- **default** (Any) – Optional argument for the value to return if
  key is not found.

**Returns:**

The layer matching the key or the default value.

**Return type:**

[`bmesh.types.BMLayerItem`](#bmesh.types.BMLayerItem "bmesh.types.BMLayerItem") | Any

<a id="bmesh.types.BMLayerCollection.items"></a>

#### bmesh.types.BMLayerCollection.items()

Return the (key, value) pairs of collection members
(matching Python’s dict.items() functionality).

**Returns:**

(key, value) pairs for each member of this collection.

**Return type:**

list[tuple[str, [`bmesh.types.BMLayerItem`](#bmesh.types.BMLayerItem "bmesh.types.BMLayerItem")]]

<a id="bmesh.types.BMLayerCollection.keys"></a>

#### bmesh.types.BMLayerCollection.keys()

Return the identifiers of collection members
(matching Python’s dict.keys() functionality).

**Returns:**

the identifiers for each member of this collection.

**Return type:**

list[str]

<a id="bmesh.types.BMLayerCollection.new"></a>

#### bmesh.types.BMLayerCollection.new(name='')

Create a new layer

**Parameters:**

**name** (str) – Optional name argument (will be made unique).

**Returns:**

The newly created layer.

**Return type:**

[`bmesh.types.BMLayerItem`](#bmesh.types.BMLayerItem "bmesh.types.BMLayerItem")

<a id="bmesh.types.BMLayerCollection.remove"></a>

#### bmesh.types.BMLayerCollection.remove(layer)

Remove a layer

**Parameters:**

**layer** ([`bmesh.types.BMLayerItem`](#bmesh.types.BMLayerItem "bmesh.types.BMLayerItem")) – The layer to remove.

<a id="bmesh.types.BMLayerCollection.values"></a>

#### bmesh.types.BMLayerCollection.values()

Return the values of collection
(matching Python’s dict.values() functionality).

**Returns:**

the members of this collection.

**Return type:**

list[[`bmesh.types.BMLayerItem`](#bmesh.types.BMLayerItem "bmesh.types.BMLayerItem")]

<a id="bmesh.types.BMLayerCollection.verify"></a>

#### bmesh.types.BMLayerCollection.verify()

Create a new layer or return an existing active layer

**Returns:**

The newly created layer, or the existing active layer.

**Return type:**

[`bmesh.types.BMLayerItem`](#bmesh.types.BMLayerItem "bmesh.types.BMLayerItem")

<a id="bmesh.types.BMLayerCollection.active"></a>

#### bmesh.types.BMLayerCollection.active

The active layer of this type (read-only).

**Type:**

[`bmesh.types.BMLayerItem`](#bmesh.types.BMLayerItem "bmesh.types.BMLayerItem") | None

<a id="bmesh.types.BMLayerCollection.is_singleton"></a>

#### bmesh.types.BMLayerCollection.is_singleton

True if there can exist only one layer of this type (read-only).

**Type:**

bool

Special Methods

<a id="bmesh.types.BMLayerCollection.__contains__"></a>

#### bmesh.types.BMLayerCollection.__contains__(item)

**Parameters:**

**item** (object) – Item to test for membership.

**Return type:**

bool

<a id="bmesh.types.BMLayerCollection.__getitem__"></a>

#### bmesh.types.BMLayerCollection.__getitem__(key)

**Parameters:**

**key** (int) – Index or key.

**Return type:**

[`BMLayerItem`](#bmesh.types.BMLayerItem "bmesh.types.BMLayerItem")

<a id="bmesh.types.BMLayerCollection.__iter__"></a>

#### bmesh.types.BMLayerCollection.__iter__()

**Return type:**

[`BMLayerCollection`](#bmesh.types.BMLayerCollection "bmesh.types.BMLayerCollection")

<a id="bmesh.types.BMLayerCollection.__len__"></a>

#### bmesh.types.BMLayerCollection.__len__()

**Return type:**

int

<a id="bmesh.types.BMLayerItem"></a>

### class bmesh.types.BMLayerItem

Exposes a single custom data layer, its main purpose is for use as an item accessor to custom-data when used with vert/edge/face/loop data.

<a id="bmesh.types.BMLayerItem.copy_from"></a>

#### bmesh.types.BMLayerItem.copy_from(other)

Copy data from another layer.

**Parameters:**

**other** ([`bmesh.types.BMLayerItem`](#bmesh.types.BMLayerItem "bmesh.types.BMLayerItem")) – Another layer to copy from.

<a id="bmesh.types.BMLayerItem.name"></a>

#### bmesh.types.BMLayerItem.name

The layer’s unique name (read-only).

**Type:**

str

<a id="custom-data-layer-types"></a>

## Custom-Data Layer Types

<a id="bmesh.types.BMLoopUV"></a>

### class bmesh.types.BMLoopUV

<a id="bmesh.types.BMLoopUV.pin_uv"></a>

#### bmesh.types.BMLoopUV.pin_uv

UV pin state.

**Type:**

bool

<a id="bmesh.types.BMLoopUV.uv"></a>

#### bmesh.types.BMLoopUV.uv

Loop UV (as a 2D Vector).

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bmesh.types.BMDeformVert"></a>

### class bmesh.types.BMDeformVert

<a id="bmesh.types.BMDeformVert.clear"></a>

#### bmesh.types.BMDeformVert.clear()

Clears all weights.

<a id="bmesh.types.BMDeformVert.get"></a>

#### bmesh.types.BMDeformVert.get(key, default=None)

Returns the deform weight matching the key or default
when not found (matches Python’s dictionary function of the same name).

**Parameters:**

- **key** (int) – The vertex group index.
- **default** (Any) – Optional argument for the value to return if
  key is not found.

**Returns:**

The deform weight or the default when not found.

**Return type:**

float | Any

<a id="bmesh.types.BMDeformVert.items"></a>

#### bmesh.types.BMDeformVert.items()

Return (group, weight) pairs for this vertex
(matching Python’s dict.items() functionality).

**Returns:**

(key, value) pairs for each deform weight of this vertex.

**Return type:**

list[tuple[int, float]]

<a id="bmesh.types.BMDeformVert.keys"></a>

#### bmesh.types.BMDeformVert.keys()

Return the group indices used by this vertex
(matching Python’s dict.keys() functionality).

**Returns:**

The deform group indices this vertex uses.

**Return type:**

list[int]

<a id="bmesh.types.BMDeformVert.values"></a>

#### bmesh.types.BMDeformVert.values()

Return the weights of the deform vertex
(matching Python’s dict.values() functionality).

**Returns:**

The weights that influence this vertex

**Return type:**

list[float]

Special Methods

<a id="bmesh.types.BMDeformVert.__contains__"></a>

#### bmesh.types.BMDeformVert.__contains__(item)

**Parameters:**

**item** (object) – Item to test for membership.

**Return type:**

bool

<a id="bmesh.types.BMDeformVert.__getitem__"></a>

#### bmesh.types.BMDeformVert.__getitem__(key)

**Parameters:**

**key** (int) – Index or key.

**Return type:**

float

<a id="bmesh.types.BMDeformVert.__len__"></a>

#### bmesh.types.BMDeformVert.__len__()

**Return type:**

int

<a id="bmesh.types.BMDeformVert.__setitem__"></a>

#### bmesh.types.BMDeformVert.__setitem__(key, value)

**Parameters:**

- **key** (int) – Index or key.
- **value** (object) – Value to assign.
