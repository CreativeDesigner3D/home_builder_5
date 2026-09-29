<!-- source: Blender Python API reference 5.2 / bmesh.ops.html -->

<a id="module-bmesh.ops"></a>

# BMesh Operators (bmesh.ops)

This module gives access to low level bmesh operations.

Most operators take input and return output, they can be chained together
to perform useful operations.

<a id="operator-example"></a>

## Operator Example

This script shows how operators can be used to model a link of a chain.

```python
# This script uses bmesh operators to make 2 links of a chain.

import bpy
import bmesh
import math
import mathutils

# Make a new BMesh
bm = bmesh.new()

# Add a circle XXX, should return all geometry created, not just verts.
bmesh.ops.create_circle(
    bm,
    cap_ends=False,
    radius=0.2,
    segments=8)

# Spin and deal with geometry on side 'a'
edges_start_a = bm.edges[:]
geom_start_a = bm.verts[:] + edges_start_a
ret = bmesh.ops.spin(
    bm,
    geom=geom_start_a,
    angle=math.radians(180.0),
    steps=8,
    axis=(1.0, 0.0, 0.0),
    cent=(0.0, 1.0, 0.0))
edges_end_a = [ele for ele in ret["geom_last"]
               if isinstance(ele, bmesh.types.BMEdge)]
del ret

# Extrude and create geometry on side 'b'
ret = bmesh.ops.extrude_edge_only(
    bm,
    edges=edges_start_a)
geom_extrude_mid = ret["geom"]
del ret

# Collect the edges to spin XXX, 'extrude_edge_only' could return this.
verts_extrude_b = [ele for ele in geom_extrude_mid
                   if isinstance(ele, bmesh.types.BMVert)]
edges_extrude_b = [ele for ele in geom_extrude_mid
                   if isinstance(ele, bmesh.types.BMEdge) and ele.is_boundary]
bmesh.ops.translate(
    bm,
    verts=verts_extrude_b,
    vec=(0.0, 0.0, 1.0))

# Create the circle on side 'b'
ret = bmesh.ops.spin(
    bm,
    geom=verts_extrude_b + edges_extrude_b,
    angle=-math.radians(180.0),
    steps=8,
    axis=(1.0, 0.0, 0.0),
    cent=(0.0, 1.0, 1.0))
edges_end_b = [ele for ele in ret["geom_last"]
               if isinstance(ele, bmesh.types.BMEdge)]
del ret

# Bridge the resulting edge loops of both spins 'a & b'
bmesh.ops.bridge_loops(
    bm,
    edges=edges_end_a + edges_end_b)

# Now we have made a links of the chain, make a copy and rotate it
# (so this looks something like a chain)

ret = bmesh.ops.duplicate(
    bm,
    geom=bm.verts[:] + bm.edges[:] + bm.faces[:])
geom_dupe = ret["geom"]
verts_dupe = [ele for ele in geom_dupe if isinstance(ele, bmesh.types.BMVert)]
del ret

# position the new link
bmesh.ops.translate(
    bm,
    verts=verts_dupe,
    vec=(0.0, 0.0, 2.0))
bmesh.ops.rotate(
    bm,
    verts=verts_dupe,
    cent=(0.0, 1.0, 0.0),
    matrix=mathutils.Matrix.Rotation(math.radians(90.0), 3, 'Z'))

# Done with creating the mesh, simply link it into the scene so we can see it

# Finish up, write the bmesh into a new mesh
me = bpy.data.meshes.new("Mesh")
bm.to_mesh(me)
bm.free()

# Add the mesh to the scene
obj = bpy.data.objects.new("Object", me)
bpy.context.collection.objects.link(obj)

# Select and make active
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
```

<a id="bmesh.ops.smooth_vert"></a>

### bmesh.ops.smooth_vert(bm, verts=[], factor=0, mirror_clip_x=False, mirror_clip_y=False, mirror_clip_z=False, clip_dist=0, use_axis_x=False, use_axis_y=False, use_axis_z=False)

Vertex Smooth.

Smooths vertices by using a basic vertex averaging scheme.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **verts** (list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert")]) – Input vertices.
- **factor** (float) – Smoothing factor.
- **mirror_clip_x** (bool) – Set vertices close to the x axis before the operation to 0.
- **mirror_clip_y** (bool) – Set vertices close to the y axis before the operation to 0.
- **mirror_clip_z** (bool) – Set vertices close to the z axis before the operation to 0.
- **clip_dist** (float) – Clipping threshold for the above three slots.
- **use_axis_x** (bool) – Smooth vertices along X axis.
- **use_axis_y** (bool) – Smooth vertices along Y axis.
- **use_axis_z** (bool) – Smooth vertices along Z axis.

<a id="bmesh.ops.smooth_laplacian_vert"></a>

### bmesh.ops.smooth_laplacian_vert(bm, verts=[], lambda_factor=0, lambda_border=0, use_x=False, use_y=False, use_z=False, preserve_volume=False)

Vertex Smooth Laplacian.

Smooths vertices by using Laplacian smoothing proposed by
Desbrun, et al. Implicit Fairing of Irregular Meshes using Diffusion and Curvature Flow.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **verts** (list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert")]) – Input vertices.
- **lambda_factor** (float) – Lambda parameter.
- **lambda_border** (float) – Lambda param in border.
- **use_x** (bool) – Smooth object along X axis.
- **use_y** (bool) – Smooth object along Y axis.
- **use_z** (bool) – Smooth object along Z axis.
- **preserve_volume** (bool) – Apply volume preservation after smooth.

<a id="bmesh.ops.recalc_face_normals"></a>

### bmesh.ops.recalc_face_normals(bm, faces=[])

Right-Hand Faces.

Computes an “outside” normal for the specified input faces.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **faces** (list[[`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]) – Input faces.

<a id="bmesh.ops.planar_faces"></a>

### bmesh.ops.planar_faces(bm, faces=[], iterations=0, factor=0)

Planar Faces.

Iteratively flatten faces.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **faces** (list[[`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]) – Input geometry.
- **iterations** (int) – Number of times to flatten faces (for when connected faces are used)
- **factor** (float) – Influence for making planar each iteration

**Returns:**

- `geom`:
  Output slot, computed boundary geometry.

  **type** list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]

**Return type:**

dict[str, Any]

<a id="bmesh.ops.region_extend"></a>

### bmesh.ops.region_extend(bm, geom=[], use_contract=False, use_faces=False, use_face_step=False)

Region Extend.

Used to implement the select more/less tools.
Puts geometry surrounding regions of geometry in `geom` into `geom.out`.

If `use_faces` is 0 then `geom.out` spits out verts and edges,
otherwise it spits out faces.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **geom** (list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]) – Input geometry.
- **use_contract** (bool) – Find boundary inside the regions, not outside.
- **use_faces** (bool) – Extend from faces instead of edges.
- **use_face_step** (bool) – Step over connected faces.

**Returns:**

- `geom`:
  Output slot, computed boundary geometry.

  **type** list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]

**Return type:**

dict[str, Any]

<a id="bmesh.ops.rotate_edges"></a>

### bmesh.ops.rotate_edges(bm, edges=[], use_ccw=False)

Edge Rotate.

Rotates edges topologically. Also known as “spin edge” to some people.
Simple example: `[/] becomes [|] then [\]`.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **edges** (list[[`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge")]) – Input edges.
- **use_ccw** (bool) – Rotate edge counter-clockwise if true, otherwise clockwise.

**Returns:**

- `edges`:
  Newly spun edges.

  **type** list[[`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge")]

**Return type:**

dict[str, Any]

<a id="bmesh.ops.reverse_faces"></a>

### bmesh.ops.reverse_faces(bm, faces=[], flip_multires=False)

Reverse Faces.

Reverses the winding (vertex order) of faces.
This has the effect of flipping the normal.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **faces** (list[[`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]) – Input faces.
- **flip_multires** (bool) – Maintain multi-res offset.

<a id="bmesh.ops.flip_quad_tessellation"></a>

### bmesh.ops.flip_quad_tessellation(bm, faces=[])

Flip Quad Tessellation

Flip the tessellation direction of the selected quads.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **faces** (list[[`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]) – Input faces.

<a id="bmesh.ops.bisect_edges"></a>

### bmesh.ops.bisect_edges(bm, edges=[], cuts=0, edge_percents={})

Edge Bisect.

Splits input edges (but doesn’t do anything else).
This creates a 2-valence vert.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **edges** (list[[`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge")]) – Input edges.
- **cuts** (int) – Number of cuts.
- **edge_percents** (dict[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace"), float]) – Undocumented.

**Returns:**

- `geom_split`:
  Newly created vertices and edges.

  **type** list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]

**Return type:**

dict[str, Any]

<a id="bmesh.ops.mirror"></a>

### bmesh.ops.mirror(bm, geom=[], matrix=((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)), merge_dist=0, axis='X', mirror_u=False, mirror_v=False, mirror_udim=False, use_shapekey=False)

Mirror.

Mirrors geometry along an axis. The resulting geometry is welded on using
`merge_dist`. Pairs of original/mirrored vertices are welded using the `merge_dist`
parameter (which defines the minimum distance for welding to happen).

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **geom** (list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]) – Input geometry.
- **matrix** ([`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")) – Matrix defining the mirror transformation.
- **merge_dist** (float) – Maximum distance for merging. does no merging if 0.
- **axis** (Literal['X', 'Y', 'Z']) – The axis to use.
- **mirror_u** (bool) – Mirror UVs across the u axis.
- **mirror_v** (bool) – Mirror UVs across the v axis.
- **mirror_udim** (bool) – Mirror UVs in each tile.
- **use_shapekey** (bool) – Transform shape keys too.

**Returns:**

- `geom`:
  Output geometry, mirrored.

  **type** list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]

**Return type:**

dict[str, Any]

<a id="bmesh.ops.find_doubles"></a>

### bmesh.ops.find_doubles(bm, verts=[], keep_verts=[], use_connected=False, dist=0)

Find Doubles.

Takes input verts and finds vertices they should weld to.
Outputs a mapping slot suitable for use with the weld verts BMOP.

If `keep_verts` is used, vertices outside that set can only be merged
with vertices in that set.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **verts** (list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert")]) – Input vertices.
- **keep_verts** (list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert")]) – List of verts to keep.
- **use_connected** (bool) – Limit the search for doubles by connected geometry.
- **dist** (float) – Maximum distance.

**Returns:**

- `targetmap`:

  **type** dict[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace"), [`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]

**Return type:**

dict[str, Any]

<a id="bmesh.ops.remove_doubles"></a>

### bmesh.ops.remove_doubles(bm, verts=[], use_connected=False, dist=0)

Remove Doubles.

Finds groups of vertices closer than dist and merges them together,
using the weld verts BMOP.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **verts** (list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert")]) – Input verts.
- **use_connected** (bool) – Limit the search for doubles by connected geometry.
- **dist** (float) – Maximum distance.

<a id="bmesh.ops.circularize"></a>

### bmesh.ops.circularize(bm, geom=[], factor=0, custom_radius=0, angle=0, fit_method=0, flatten=0, regular=False, lock_x=False, lock_y=False, lock_z=False, mirror_x=False, mirror_y=False, mirror_z=False)

Circularize.

Shape selected geometry into a circle.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **geom** (list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]) – Input geometry.
- **factor** (float) – Influence factor: spans from 0.0 to 1.0.
- **custom_radius** (float) – Custom radius.
- **angle** (float) – Rotation angle.
- **fit_method** (int) – Method to fit the circle.
- **flatten** (float) – Flatten factor: 0.0 projects onto the mesh, 1.0 flattens on the optimal plane.
- **regular** (bool) – Distributes vertices at constant distances, otherwise preserves original spacing.
- **lock_x** (bool) – Lock X-axis editing.
- **lock_y** (bool) – Lock Y-axis editing.
- **lock_z** (bool) – Lock Z-axis editing.
- **mirror_x** (bool) – Use X axis of the mirror modifier.
- **mirror_y** (bool) – Use Y axis of the mirror modifier.
- **mirror_z** (bool) – Use Z axis of the mirror modifier.

<a id="bmesh.ops.flatten"></a>

### bmesh.ops.flatten(bm, geom=[], factor=0, method=0, view_normal=(0.0, 0.0, 0.0), lock_x=False, lock_y=False, lock_z=False)

Flatten.

Flatten vertices on a best-fitting plane.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **geom** (list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]) – Input geometry.
- **factor** (float) – Influence factor: spans from 0.0 to 1.0.
- **method** (int) – Plane on which vertices are flattened.
- **view_normal** (Sequence[float]) – View direction in object local space.
- **lock_x** (bool) – Lock X axis editing.
- **lock_y** (bool) – Lock Y axis editing.
- **lock_z** (bool) – Lock Z axis editing.

<a id="bmesh.ops.collapse"></a>

### bmesh.ops.collapse(bm, edges=[], uvs=False)

Collapse Connected.

Collapses connected vertices

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **edges** (list[[`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge")]) – Input edges.
- **uvs** (bool) – Also collapse UVs and such.

<a id="bmesh.ops.pointmerge_facedata"></a>

### bmesh.ops.pointmerge_facedata(bm, verts=[], vert_target=None)

Face-Data Point Merge.

Merge uv/vcols at a specific vertex.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **verts** (list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert")]) – Input vertices.
- **vert_target** ([`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | None) – Target vertex to merge into.

<a id="bmesh.ops.average_vert_facedata"></a>

### bmesh.ops.average_vert_facedata(bm, verts=[])

Average Vertices Face-vert Data.

Merge uv/vcols associated with the input vertices at
the bounding box center.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **verts** (list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert")]) – Input vertices.

<a id="bmesh.ops.pointmerge"></a>

### bmesh.ops.pointmerge(bm, verts=[], merge_co=(0.0, 0.0, 0.0), vert_target=None)

Point Merge.

Merge verts together at a point.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **verts** (list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert")]) – Input vertices (all verts will be merged into the first).
- **merge_co** (Sequence[float]) – Position to merge at.
- **vert_target** ([`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | None) – Optional target vertex to merge into. Does not override merge_co.
  Set this to preserve the custom data of the target vertex.

<a id="bmesh.ops.collapse_uvs"></a>

### bmesh.ops.collapse_uvs(bm, edges=[])

Collapse Connected UVs.

Collapses connected UV vertices.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **edges** (list[[`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge")]) – Input edges.

<a id="bmesh.ops.weld_verts"></a>

### bmesh.ops.weld_verts(bm, targetmap={}, use_centroid=False, average_vert_data=False)

Weld Verts.

Welds verts together (kind-of like remove doubles, merge, etc, all of which
use or will use this BMOP). You pass in mappings from vertices to the vertices
they weld with.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **targetmap** (dict[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace"), [`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]) – Maps welded vertices to verts they should weld to.
- **use_centroid** (bool) – Merge vertices to their centroid position,
  otherwise use the position of the target vertex.
- **average_vert_data** (bool) – Whether to average custom data of merged vertices.

<a id="bmesh.ops.create_vert"></a>

### bmesh.ops.create_vert(bm, co=(0.0, 0.0, 0.0))

Make Vertex.

Creates a single vertex; this BMOP was necessary
for click-create-vertex.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **co** (Sequence[float]) – The coordinate of the new vert.

**Returns:**

- `vert`:
  The new vert.

  **type** list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert")]

**Return type:**

dict[str, Any]

<a id="bmesh.ops.join_triangles"></a>

### bmesh.ops.join_triangles(bm, faces=[], cmp_seam=False, cmp_sharp=False, cmp_uvs=False, cmp_vcols=False, cmp_materials=False, angle_face_threshold=0, angle_shape_threshold=0, topology_influence=0, deselect_joined=False, merge_limit=0, neighbor_debug=0)

Join Triangles.

Tries to intelligently join triangles according
to angle threshold and delimiters.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **faces** (list[[`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]) – Input geometry.
- **cmp_seam** (bool) – Compare seam
- **cmp_sharp** (bool) – Compare sharp
- **cmp_uvs** (bool) – Compare UVs
- **cmp_vcols** (bool) – Compare VCols.
- **cmp_materials** (bool) – Compare materials.
- **angle_face_threshold** (float) – Undocumented.
- **angle_shape_threshold** (float) – Undocumented.
- **topology_influence** (float) – Undocumented.
- **deselect_joined** (bool) – Undocumented.
- **merge_limit** (int) – Undocumented.
- **neighbor_debug** (int) – Undocumented.

**Returns:**

- `faces`:
  Joined faces.

  **type** list[[`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]

**Return type:**

dict[str, Any]

<a id="bmesh.ops.contextual_create"></a>

### bmesh.ops.contextual_create(bm, geom=[], mat_nr=0, use_smooth=False)

Contextual Create.

This is basically F-key, it creates
new faces from vertices, makes stuff from edge nets,
makes wire edges, etc. It also dissolves faces.

Three verts become a triangle, four become a quad. Two
become a wire edge.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **geom** (list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]) – Input geometry.
- **mat_nr** (int) – Material to use.
- **use_smooth** (bool) – Set smooth shading on newly created faces.

**Returns:**

- `faces`:
  Newly-made face(s).

  **type** list[[`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]
- `edges`:
  Newly-made edge(s).

  **type** list[[`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge")]

**Return type:**

dict[str, Any]

<a id="bmesh.ops.bridge_loops"></a>

### bmesh.ops.bridge_loops(bm, edges=[], use_pairs=False, use_cyclic=False, use_merge=False, merge_factor=0, twist_offset=0)

Bridge edge loops with faces.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **edges** (list[[`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge")]) – Input edges.
- **use_pairs** (bool) – Undocumented.
- **use_cyclic** (bool) – Undocumented.
- **use_merge** (bool) – Merge rather than creating faces.
- **merge_factor** (float) – Merge factor.
- **twist_offset** (int) – Twist offset for closed loops.

**Returns:**

- `faces`:
  New faces.

  **type** list[[`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]
- `edges`:
  New edges.

  **type** list[[`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge")]

**Return type:**

dict[str, Any]

<a id="bmesh.ops.grid_fill"></a>

### bmesh.ops.grid_fill(bm, edges=[], mat_nr=0, use_smooth=False, use_interp_simple=False)

Grid Fill.

Create faces defined by 2 disconnected edge loops (which share edges).

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **edges** (list[[`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge")]) – Input edges.
- **mat_nr** (int) – Material to use.
- **use_smooth** (bool) – Smooth state to use.
- **use_interp_simple** (bool) – Use simple interpolation.

**Returns:**

- `faces`:
  New faces.

  **type** list[[`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]

**Return type:**

dict[str, Any]

<a id="bmesh.ops.holes_fill"></a>

### bmesh.ops.holes_fill(bm, edges=[], sides=0)

Fill Holes.

Fill boundary edges with faces, copying surrounding custom-data.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **edges** (list[[`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge")]) – Input edges.
- **sides** (int) – Maximum number of sides for holes to fill (holes with more edges are skipped).

**Returns:**

- `faces`:
  New faces.

  **type** list[[`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]

**Return type:**

dict[str, Any]

<a id="bmesh.ops.face_attribute_fill"></a>

### bmesh.ops.face_attribute_fill(bm, faces=[], use_normals=False, use_data=False)

Face Attribute Fill.

Fill in faces with data from adjacent faces.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **faces** (list[[`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]) – Input faces.
- **use_normals** (bool) – Copy face winding.
- **use_data** (bool) – Copy face data.

**Returns:**

- `faces_fail`:
  Faces that could not be handled.

  **type** list[[`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]

**Return type:**

dict[str, Any]

<a id="bmesh.ops.edgeloop_fill"></a>

### bmesh.ops.edgeloop_fill(bm, edges=[], mat_nr=0, use_smooth=False)

Edge Loop Fill.

Create faces defined by one or more non overlapping edge loops.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **edges** (list[[`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge")]) – Input edges.
- **mat_nr** (int) – Material to use.
- **use_smooth** (bool) – Smooth state to use.

**Returns:**

- `faces`:
  New faces.

  **type** list[[`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]

**Return type:**

dict[str, Any]

<a id="bmesh.ops.edgenet_fill"></a>

### bmesh.ops.edgenet_fill(bm, edges=[], mat_nr=0, use_smooth=False, sides=0)

Edge Net Fill.

Create faces defined by enclosed edges.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **edges** (list[[`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge")]) – Input edges.
- **mat_nr** (int) – Material to use.
- **use_smooth** (bool) – Smooth state to use.
- **sides** (int) – Maximum number of sides for created faces.

**Returns:**

- `faces`:
  New faces.

  **type** list[[`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]

**Return type:**

dict[str, Any]

<a id="bmesh.ops.edgenet_prepare"></a>

### bmesh.ops.edgenet_prepare(bm, edges=[])

Edge-net Prepare.

Identifies several useful edge loop cases and modifies them so
they’ll become a face when edgenet_fill is called. The cases covered are:

- One single loop; an edge is added to connect the ends
- Two loops; two edges are added to connect the endpoints (based on the
  shortest distance between each endpoint).

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **edges** (list[[`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge")]) – Input edges.

**Returns:**

- `edges`:
  New edges.

  **type** list[[`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge")]

**Return type:**

dict[str, Any]

<a id="bmesh.ops.rotate"></a>

### bmesh.ops.rotate(bm, cent=(0.0, 0.0, 0.0), matrix=((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)), verts=[], space=((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)), use_shapekey=False)

Rotate.

Rotate vertices around a center, using a 3x3 rotation matrix.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **cent** (Sequence[float]) – Center of rotation.
- **matrix** ([`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")) – Matrix defining rotation.
- **verts** (list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert")]) – Input vertices.
- **space** ([`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")) – Matrix to define the space (typically object matrix).
- **use_shapekey** (bool) – Transform shape keys too.

<a id="bmesh.ops.translate"></a>

### bmesh.ops.translate(bm, vec=(0.0, 0.0, 0.0), space=((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)), verts=[], use_shapekey=False)

Translate.

Translate vertices by an offset.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **vec** (Sequence[float]) – Translation offset.
- **space** ([`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")) – Matrix to define the space (typically object matrix).
- **verts** (list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert")]) – Input vertices.
- **use_shapekey** (bool) – Transform shape keys too.

<a id="bmesh.ops.scale"></a>

### bmesh.ops.scale(bm, vec=(0.0, 0.0, 0.0), space=((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)), verts=[], use_shapekey=False)

Scale.

Scales vertices by a factor.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **vec** (Sequence[float]) – Scale factor.
- **space** ([`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")) – Matrix to define the space (typically object matrix).
- **verts** (list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert")]) – Input vertices.
- **use_shapekey** (bool) – Transform shape keys too.

<a id="bmesh.ops.transform"></a>

### bmesh.ops.transform(bm, matrix=((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)), space=((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)), verts=[], use_shapekey=False)

Transform.

Transforms a set of vertices by a matrix. Multiplies
the vertex coordinates with the matrix.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **matrix** ([`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")) – Transform matrix.
- **space** ([`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")) – Matrix to define the space (typically object matrix).
- **verts** (list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert")]) – Input vertices.
- **use_shapekey** (bool) – Transform shape keys too.

<a id="bmesh.ops.object_load_bmesh"></a>

### bmesh.ops.object_load_bmesh(bm, scene, object)

Object Load BMesh.

Loads a bmesh into an object/mesh. This is a “private”
BMOP.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **scene** ([`bpy.types.Scene`](bpy.types.Scene.md#bpy.types.Scene "bpy.types.Scene")) – The scene.
- **object** ([`bpy.types.Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object")) – The object.

<a id="bmesh.ops.bmesh_to_mesh"></a>

### bmesh.ops.bmesh_to_mesh(bm, mesh, object)

BMesh to Mesh.

Converts a bmesh to a Mesh. This is reserved for exiting edit-mode.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **mesh** ([`bpy.types.Mesh`](bpy.types.Mesh.md#bpy.types.Mesh "bpy.types.Mesh")) – The mesh to write into.
- **object** ([`bpy.types.Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object")) – The object.

<a id="bmesh.ops.mesh_to_bmesh"></a>

### bmesh.ops.mesh_to_bmesh(bm, mesh, object, use_shapekey=False)

Mesh to BMesh.

Load the contents of a mesh into the bmesh. this BMOP is private, it’s
reserved exclusively for entering edit-mode.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **mesh** ([`bpy.types.Mesh`](bpy.types.Mesh.md#bpy.types.Mesh "bpy.types.Mesh")) – The mesh to read from.
- **object** ([`bpy.types.Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object")) – The object.
- **use_shapekey** (bool) – Load active shapekey coordinates into verts.

<a id="bmesh.ops.extrude_discrete_faces"></a>

### bmesh.ops.extrude_discrete_faces(bm, faces=[], use_normal_flip=False, use_select_history=False)

Individual Face Extrude.

Extrudes faces individually.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **faces** (list[[`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]) – Input faces.
- **use_normal_flip** (bool) – Create faces with reversed direction.
- **use_select_history** (bool) – Preserve the selection history in the extruded geometry.

**Returns:**

- `faces`:
  Output faces.

  **type** list[[`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]

**Return type:**

dict[str, Any]

<a id="bmesh.ops.extrude_edge_only"></a>

### bmesh.ops.extrude_edge_only(bm, edges=[], use_normal_flip=False, use_select_history=False)

Extrude Only Edges.

Extrudes Edges into faces, note that this is very simple, there’s no fancy
winged extrusion.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **edges** (list[[`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge")]) – Input edges.
- **use_normal_flip** (bool) – Create faces with reversed direction.
- **use_select_history** (bool) – Preserve the selection history in the extruded geometry.

**Returns:**

- `geom`:
  Output geometry.

  **type** list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]

**Return type:**

dict[str, Any]

<a id="bmesh.ops.extrude_vert_indiv"></a>

### bmesh.ops.extrude_vert_indiv(bm, verts=[], use_select_history=False)

Individual Vertex Extrude.

Extrudes individual vertices, creating new vertices connected by wire edges.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **verts** (list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert")]) – Input vertices.
- **use_select_history** (bool) – Preserve the selection history in the extruded geometry.

**Returns:**

- `edges`:
  Output wire edges.

  **type** list[[`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge")]
- `verts`:
  Output vertices.

  **type** list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert")]

**Return type:**

dict[str, Any]

<a id="bmesh.ops.connect_verts"></a>

### bmesh.ops.connect_verts(bm, verts=[], faces_exclude=[], check_degenerate=False)

Connect Verts.

Split faces by adding edges that connect `verts`.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **verts** (list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert")]) – Input vertices.
- **faces_exclude** (list[[`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]) – Input faces to explicitly exclude from connecting.
- **check_degenerate** (bool) – Prevent splits with overlaps & intersections.

**Returns:**

- `edges`:

  **type** list[[`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge")]

**Return type:**

dict[str, Any]

<a id="bmesh.ops.connect_verts_concave"></a>

### bmesh.ops.connect_verts_concave(bm, faces=[])

Connect Verts to form Convex Faces.

Splits concave faces into convex faces.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **faces** (list[[`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]) – Input faces.

**Returns:**

- `edges`:

  **type** list[[`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge")]
- `faces`:

  **type** list[[`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]

**Return type:**

dict[str, Any]

<a id="bmesh.ops.connect_verts_nonplanar"></a>

### bmesh.ops.connect_verts_nonplanar(bm, angle_limit=0, faces=[])

Connect Verts Across non Planar Faces.

Split faces by connecting edges along non planar `faces`.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **angle_limit** (float) – Maximum angle of non-planarity before splitting (radians).
- **faces** (list[[`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]) – Input faces.

**Returns:**

- `edges`:

  **type** list[[`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge")]
- `faces`:

  **type** list[[`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]

**Return type:**

dict[str, Any]

<a id="bmesh.ops.connect_vert_pair"></a>

### bmesh.ops.connect_vert_pair(bm, verts=[], verts_exclude=[], faces_exclude=[])

Connect Vert Pair.

Connect a pair of vertices by splitting faces along the shortest path between them.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **verts** (list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert")]) – Input vertices.
- **verts_exclude** (list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert")]) – Input vertices to explicitly exclude from connecting.
- **faces_exclude** (list[[`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]) – Input faces to explicitly exclude from connecting.

**Returns:**

- `edges`:

  **type** list[[`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge")]

**Return type:**

dict[str, Any]

<a id="bmesh.ops.extrude_face_region"></a>

### bmesh.ops.extrude_face_region(bm, geom=[], edges_exclude=set(), use_keep_orig=False, use_normal_flip=False, use_normal_from_adjacent=False, use_dissolve_ortho_edges=False, use_select_history=False, skip_input_flip=False)

Extrude Faces.

Extrude operator (does not transform)

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **geom** (list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]) – Edges and faces.
- **edges_exclude** (set[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]) – Input edges to explicitly exclude from extrusion.
- **use_keep_orig** (bool) – Keep original geometry (requires geom to include edges).
- **use_normal_flip** (bool) – Create faces with reversed direction.
- **use_normal_from_adjacent** (bool) – Use winding from surrounding faces instead of this region.
- **use_dissolve_ortho_edges** (bool) – Dissolve edges whose faces form a flat surface.
- **use_select_history** (bool) – Preserve the selection history in the extruded geometry.
- **skip_input_flip** (bool) – Skip flipping of input faces to preserve original orientation.

**Returns:**

- `geom`:

  **type** list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]

**Return type:**

dict[str, Any]

<a id="bmesh.ops.dissolve_verts"></a>

### bmesh.ops.dissolve_verts(bm, verts=[], use_face_split=False, use_boundary_tear=False)

Dissolve Verts.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **verts** (list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert")]) – Input vertices.
- **use_face_split** (bool) – Split off face corners to maintain surrounding geometry.
- **use_boundary_tear** (bool) – Split off face corners instead of merging faces.

<a id="bmesh.ops.dissolve_edges"></a>

### bmesh.ops.dissolve_edges(bm, edges=[], use_verts=False, use_face_split=False, angle_threshold=0, use_preserve_quads=False)

Dissolve Edges.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **edges** (list[[`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge")]) – Input edges.
- **use_verts** (bool) – Dissolve verts left between only 2 edges.
- **use_face_split** (bool) – Split off face corners to maintain surrounding geometry.
- **angle_threshold** (float) – Do not dissolve verts between 2 edges when their angle exceeds this threshold.
  Disabled by default.
- **use_preserve_quads** (bool) – When dissolving the edge between 2 triangles, don’t dissolve the verts.

**Returns:**

- `region`:

  **type** list[[`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]

**Return type:**

dict[str, Any]

<a id="bmesh.ops.dissolve_faces"></a>

### bmesh.ops.dissolve_faces(bm, faces=[], use_verts=False)

Dissolve Faces.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **faces** (list[[`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]) – Input faces.
- **use_verts** (bool) – Dissolve verts left between only 2 edges.

**Returns:**

- `region`:

  **type** list[[`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]

**Return type:**

dict[str, Any]

<a id="bmesh.ops.dissolve_limit"></a>

### bmesh.ops.dissolve_limit(bm, angle_limit=0, use_dissolve_boundaries=False, verts=[], edges=[], delimit=set())

Limited Dissolve.

Dissolve planar faces and co-linear edges.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **angle_limit** (float) – Maximum angle (radians) between face normals for dissolving.
- **use_dissolve_boundaries** (bool) – Dissolve all vertices in between face boundaries.
- **verts** (list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert")]) – Input vertices.
- **edges** (list[[`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge")]) – Input edges.
- **delimit** (set[Literal['NORMAL', 'MATERIAL', 'SEAM', 'SHARP', 'UV']]) – Delimit dissolve operation.

**Returns:**

- `region`:

  **type** list[[`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]

**Return type:**

dict[str, Any]

<a id="bmesh.ops.dissolve_degenerate"></a>

### bmesh.ops.dissolve_degenerate(bm, dist=0, edges=[])

Degenerate Dissolve.

Dissolve edges with no length, faces with no area.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **dist** (float) – Maximum distance to consider degenerate.
- **edges** (list[[`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge")]) – Input edges.

<a id="bmesh.ops.triangulate"></a>

### bmesh.ops.triangulate(bm, faces=[], quad_method='BEAUTY', ngon_method='BEAUTY')

Triangulate.

Triangulate faces, splitting quads and n-gons into triangles.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **faces** (list[[`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]) – Input faces.
- **quad_method** (Literal['BEAUTY', 'FIXED', 'ALTERNATE', 'SHORT_EDGE', 'LONG_EDGE']) – Method for splitting the quads into triangles.
- **ngon_method** (Literal['BEAUTY', 'EAR_CLIP']) – Method for splitting the polygons into triangles.

**Returns:**

- `edges`:

  **type** list[[`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge")]
- `faces`:

  **type** list[[`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]
- `face_map`:

  **type** dict[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace"), [`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]
- `face_map_double`:
  Duplicate faces.

  **type** dict[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace"), [`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]

**Return type:**

dict[str, Any]

<a id="bmesh.ops.unsubdivide"></a>

### bmesh.ops.unsubdivide(bm, verts=[], iterations=0)

Un-Subdivide.

Reduce detail in geometry containing grids.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **verts** (list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert")]) – Input vertices.
- **iterations** (int) – Number of times to unsubdivide.

<a id="bmesh.ops.subdivide_edges"></a>

### bmesh.ops.subdivide_edges(bm, edges=[], smooth=0, smooth_falloff='SMOOTH', fractal=0, along_normal=0, cuts=0, seed=0, custom_patterns={}, edge_percents={}, quad_corner_type='STRAIGHT_CUT', use_grid_fill=False, use_single_edge=False, use_only_quads=False, use_sphere=False, use_smooth_even=False)

Subdivide Edges.

Advanced operator for subdividing edges
with options for face patterns, smoothing and randomization.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **edges** (list[[`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge")]) – Input edges.
- **smooth** (float) – Smoothness factor.
- **smooth_falloff** (Literal['SMOOTH', 'SPHERE', 'ROOT', 'SHARP', 'LINEAR', 'INVERSE_SQUARE']) – Smooth falloff type.
- **fractal** (float) – Fractal randomness factor.
- **along_normal** (float) – Factor (0 to 1) controlling how much fractal displacement is restricted to the normal.
- **cuts** (int) – Number of cuts.
- **seed** (int) – Seed for the random number generator.
- **custom_patterns** (dict) – Internal use only, not accessible from Python.
- **edge_percents** (dict[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace"), float]) – Mapping of edges to a float (0 to 1) controlling the cut position along each edge.
- **quad_corner_type** (Literal['STRAIGHT_CUT', 'INNER_VERT', 'PATH', 'FAN']) – Quad corner type.
- **use_grid_fill** (bool) – Fill in fully-selected faces with a grid.
- **use_single_edge** (bool) – Tessellate the case of one edge selected in a quad or triangle.
- **use_only_quads** (bool) – Only subdivide quads (for loop-cut).
- **use_sphere** (bool) – Project new vertices onto a sphere (used for spherical primitives).
- **use_smooth_even** (bool) – Maintain even offset when smoothing.

**Returns:**

- `geom_inner`:

  **type** list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]
- `geom_split`:

  **type** list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]
- `geom`:
  Contains all output geometry.

  **type** list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]

**Return type:**

dict[str, Any]

<a id="bmesh.ops.subdivide_edgering"></a>

### bmesh.ops.subdivide_edgering(bm, edges=[], interp_mode='LINEAR', smooth=0, cuts=0, profile_shape='SMOOTH', profile_shape_factor=0)

Subdivide Edge-Ring.

Take an edge-ring, and subdivide with interpolation options.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **edges** (list[[`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge")]) – Input edges.
- **interp_mode** (Literal['LINEAR', 'PATH', 'SURFACE']) – Interpolation method.
- **smooth** (float) – Smoothness factor.
- **cuts** (int) – Number of cuts.
- **profile_shape** (Literal['SMOOTH', 'SPHERE', 'ROOT', 'SHARP', 'LINEAR', 'INVERSE_SQUARE']) – Profile shape type.
- **profile_shape_factor** (float) – How much intermediary new edges are shrunk/expanded.

**Returns:**

- `faces`:
  Output faces.

  **type** list[[`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]

**Return type:**

dict[str, Any]

<a id="bmesh.ops.bisect_plane"></a>

### bmesh.ops.bisect_plane(bm, geom=[], dist=0, plane_co=(0.0, 0.0, 0.0), plane_no=(0.0, 0.0, 0.0), use_snap_center=False, clear_outer=False, clear_inner=False)

Bisect Plane.

Bisects the mesh by a plane (cut the mesh in half).

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **geom** (list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]) – Input geometry.
- **dist** (float) – Minimum distance when testing if a vert is exactly on the plane.
- **plane_co** (Sequence[float]) – Point on the plane.
- **plane_no** (Sequence[float]) – Normal of the plane.
- **use_snap_center** (bool) – Snap axis aligned verts to the center.
- **clear_outer** (bool) – When enabled, remove all geometry on the positive side of the plane.
- **clear_inner** (bool) – When enabled, remove all geometry on the negative side of the plane.

**Returns:**

- `geom_cut`:
  Output geometry aligned with the plane (new and existing).

  **type** list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge")]
- `geom`:
  Input and output geometry (result of cut).

  **type** list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]

**Return type:**

dict[str, Any]

<a id="bmesh.ops.delete"></a>

### bmesh.ops.delete(bm, geom=[], context='VERTS')

Delete Geometry.

Utility operator to delete geometry.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **geom** (list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]) – Input geometry.
- **context** (Literal['VERTS', 'EDGES', 'FACES_ONLY', 'EDGES_FACES', 'FACES', 'FACES_KEEP_BOUNDARY', 'TAGGED_ONLY']) – Geometry types to delete.

<a id="bmesh.ops.duplicate"></a>

### bmesh.ops.duplicate(bm, geom=[], dest=None, use_select_history=False, use_edge_flip_from_face=False)

Duplicate Geometry.

Utility operator to duplicate geometry,
optionally into a destination mesh.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **geom** (list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]) – Input geometry.
- **dest** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh") | None) – Destination bmesh, if None will use current one.
- **use_select_history** (bool) – Preserve the selection history in the duplicated geometry.
- **use_edge_flip_from_face** (bool) – Copy edge flip state from connected faces.

**Returns:**

- `geom_orig`:

  **type** list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]
- `geom`:

  **type** list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]
- `vert_map`:

  **type** dict[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace"), [`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]
- `edge_map`:

  **type** dict[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace"), [`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]
- `face_map`:

  **type** dict[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace"), [`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]
- `boundary_map`:
  Boundary edges from the split geometry that maps edges from the original geometry
  to the destination edges.

  **type** dict[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace"), [`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]
- `isovert_map`:

  **type** dict[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace"), [`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]

**Return type:**

dict[str, Any]

<a id="bmesh.ops.split"></a>

### bmesh.ops.split(bm, geom=[], dest=None, use_only_faces=False)

Split Off Geometry.

Disconnect geometry from adjacent edges and faces,
optionally into a destination mesh.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **geom** (list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]) – Input geometry.
- **dest** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh") | None) – Destination bmesh, if None will use current one.
- **use_only_faces** (bool) – When enabled, don’t duplicate loose verts/edges.

**Returns:**

- `geom`:

  **type** list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]
- `boundary_map`:
  Boundary edges from the split geometry that maps edges from the original geometry
  to the destination edges.

  When the source edges have been deleted, the destination edge will be used
  for both the key and the value.

  **type** dict[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace"), [`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]
- `isovert_map`:

  **type** dict[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace"), [`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]

**Return type:**

dict[str, Any]

<a id="bmesh.ops.spin"></a>

### bmesh.ops.spin(bm, geom=[], cent=(0.0, 0.0, 0.0), axis=(0.0, 0.0, 0.0), dvec=(0.0, 0.0, 0.0), angle=0, space=((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)), steps=0, use_merge=False, use_normal_flip=False, use_duplicate=False)

Spin.

Extrude or duplicate geometry a number of times,
rotating and possibly translating after each step

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **geom** (list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]) – Input geometry.
- **cent** (Sequence[float]) – Rotation center.
- **axis** (Sequence[float]) – Rotation axis.
- **dvec** (Sequence[float]) – Translation delta per step.
- **angle** (float) – Total rotation angle (radians).
- **space** ([`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")) – Matrix to define the space (typically object matrix).
- **steps** (int) – Number of steps.
- **use_merge** (bool) – Merge first/last when the angle is a full revolution.
- **use_normal_flip** (bool) – Create faces with reversed direction.
- **use_duplicate** (bool) – Duplicate the geometry, otherwise extrude.

**Returns:**

- `geom_last`:
  Result of last step.

  **type** list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]

**Return type:**

dict[str, Any]

<a id="bmesh.ops.rotate_uvs"></a>

### bmesh.ops.rotate_uvs(bm, faces=[], use_ccw=False)

UV Rotation.

Cycle the loop UVs

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **faces** (list[[`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]) – Input faces.
- **use_ccw** (bool) – Rotate counter-clockwise if true, otherwise clockwise.

<a id="bmesh.ops.reverse_uvs"></a>

### bmesh.ops.reverse_uvs(bm, faces=[])

UV Reverse.

Reverse the UVs

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **faces** (list[[`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]) – Input faces.

<a id="bmesh.ops.rotate_colors"></a>

### bmesh.ops.rotate_colors(bm, faces=[], use_ccw=False, color_index=0)

Color Rotation.

Cycle the loop colors

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **faces** (list[[`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]) – Input faces.
- **use_ccw** (bool) – Rotate counter-clockwise if true, otherwise clockwise.
- **color_index** (int) – Index into color attribute list.

<a id="bmesh.ops.reverse_colors"></a>

### bmesh.ops.reverse_colors(bm, faces=[], color_index=0)

Color Reverse

Reverse the loop colors.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **faces** (list[[`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]) – Input faces.
- **color_index** (int) – Index into color attribute list.

<a id="bmesh.ops.split_edges"></a>

### bmesh.ops.split_edges(bm, edges=[], verts=[], use_verts=False)

Edge Split.

Disconnects faces along input edges.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **edges** (list[[`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge")]) – Input edges.
- **verts** (list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert")]) – Optional tag verts, use to have greater control of splits.
- **use_verts** (bool) – Use verts for splitting, else just find verts to split from edges.

**Returns:**

- `edges`:
  The original edges that were disconnected.

  **type** list[[`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge")]

**Return type:**

dict[str, Any]

<a id="bmesh.ops.create_grid"></a>

### bmesh.ops.create_grid(bm, x_segments=0, y_segments=0, size=0, matrix=((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)), calc_uvs=False)

Create Grid.

Creates a grid with a variable number of subdivisions

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **x_segments** (int) – Number of x segments.
- **y_segments** (int) – Number of y segments.
- **size** (float) – Size of the grid.
- **matrix** ([`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")) – Matrix to multiply the new geometry with.
- **calc_uvs** (bool) – Calculate default UVs.

**Returns:**

- `verts`:
  Output verts.

  **type** list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert")]

**Return type:**

dict[str, Any]

<a id="bmesh.ops.create_uvsphere"></a>

### bmesh.ops.create_uvsphere(bm, u_segments=0, v_segments=0, radius=0, matrix=((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)), calc_uvs=False)

Create UV Sphere.

Creates a UV sphere with a variable number of subdivisions.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **u_segments** (int) – Number of u segments.
- **v_segments** (int) – Number of v segments.
- **radius** (float) – Radius.
- **matrix** ([`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")) – Matrix to multiply the new geometry with.
- **calc_uvs** (bool) – Calculate default UVs.

**Returns:**

- `verts`:
  Output verts.

  **type** list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert")]

**Return type:**

dict[str, Any]

<a id="bmesh.ops.create_icosphere"></a>

### bmesh.ops.create_icosphere(bm, subdivisions=0, radius=0, matrix=((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)), calc_uvs=False)

Create Ico-Sphere.

Creates an ico-sphere with a variable number of subdivisions.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **subdivisions** (int) – How many times to recursively subdivide the sphere.
- **radius** (float) – Radius.
- **matrix** ([`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")) – Matrix to multiply the new geometry with.
- **calc_uvs** (bool) – Calculate default UVs.

**Returns:**

- `verts`:
  Output verts.

  **type** list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert")]

**Return type:**

dict[str, Any]

<a id="bmesh.ops.create_monkey"></a>

### bmesh.ops.create_monkey(bm, matrix=((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)), calc_uvs=False)

Create Suzanne.

Creates a monkey (standard blender primitive).

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **matrix** ([`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")) – Matrix to multiply the new geometry with.
- **calc_uvs** (bool) – Calculate default UVs.

**Returns:**

- `verts`:
  Output verts.

  **type** list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert")]

**Return type:**

dict[str, Any]

<a id="bmesh.ops.create_cone"></a>

### bmesh.ops.create_cone(bm, cap_ends=False, cap_tris=False, segments=0, radius1=0, radius2=0, depth=0, matrix=((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)), calc_uvs=False)

Create Cone.

Creates a cone with variable radius at both ends

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **cap_ends** (bool) – Whether or not to fill in the ends with faces.
- **cap_tris** (bool) – Fill ends with triangles instead of ngons.
- **segments** (int) – Number of vertices in the base circle.
- **radius1** (float) – Radius of one end.
- **radius2** (float) – Radius of the opposite end.
- **depth** (float) – Distance between ends.
- **matrix** ([`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")) – Matrix to multiply the new geometry with.
- **calc_uvs** (bool) – Calculate default UVs.

**Returns:**

- `verts`:
  Output verts.

  **type** list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert")]

**Return type:**

dict[str, Any]

<a id="bmesh.ops.create_circle"></a>

### bmesh.ops.create_circle(bm, cap_ends=False, cap_tris=False, segments=0, radius=0, matrix=((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)), calc_uvs=False)

Creates a Circle.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **cap_ends** (bool) – Whether or not to fill in the circle with a face.
- **cap_tris** (bool) – Fill the circle with triangles instead of an n-gon.
- **segments** (int) – Number of vertices in the circle.
- **radius** (float) – Radius of the circle.
- **matrix** ([`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")) – Matrix to multiply the new geometry with.
- **calc_uvs** (bool) – Calculate default UVs.

**Returns:**

- `verts`:
  Output verts.

  **type** list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert")]

**Return type:**

dict[str, Any]

<a id="bmesh.ops.create_cube"></a>

### bmesh.ops.create_cube(bm, size=0, matrix=((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)), calc_uvs=False)

Create Cube

Creates a cube.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **size** (float) – Size of the cube.
- **matrix** ([`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")) – Matrix to multiply the new geometry with.
- **calc_uvs** (bool) – Calculate default UVs.

**Returns:**

- `verts`:
  Output verts.

  **type** list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert")]

**Return type:**

dict[str, Any]

<a id="bmesh.ops.bevel"></a>

### bmesh.ops.bevel(bm, geom=[], offset=0, offset_type='OFFSET', profile_type='SUPERELLIPSE', segments=0, profile=0, affect='VERTICES', clamp_overlap=False, material=0, loop_slide=False, mark_seam=False, mark_sharp=False, harden_normals=False, face_strength_mode='NONE', miter_outer='SHARP', miter_inner='SHARP', spread=0, custom_profile=None, vmesh_method='ADJ')

Bevel.

Bevels edges and vertices

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **geom** (list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]) – Input edges and vertices.
- **offset** (float) – Amount to offset beveled edge.
- **offset_type** (Literal['OFFSET', 'WIDTH', 'DEPTH', 'PERCENT', 'ABSOLUTE']) – How to measure the offset.
- **profile_type** (Literal['SUPERELLIPSE', 'CUSTOM']) – The profile type to use for bevel.
- **segments** (int) – Number of segments in bevel.
- **profile** (float) – Profile shape, 0->1 (.5=>round).
- **affect** (Literal['VERTICES', 'EDGES']) – Whether to bevel vertices or edges.
- **clamp_overlap** (bool) – Do not allow beveled edges/vertices to overlap each other.
- **material** (int) – Material for bevel faces, -1 means get from adjacent faces.
- **loop_slide** (bool) – Prefer to slide along edges to having even widths.
- **mark_seam** (bool) – Extend edge data to allow seams to run across bevels.
- **mark_sharp** (bool) – Extend edge data to allow sharp edges to run across bevels.
- **harden_normals** (bool) – Harden normals.
- **face_strength_mode** (Literal['NONE', 'NEW', 'AFFECTED', 'ALL']) – Whether to set face strength, and which faces to set if so.
- **miter_outer** (Literal['SHARP', 'PATCH', 'ARC']) – Outer miter kind.
- **miter_inner** (Literal['SHARP', 'PATCH', 'ARC']) – Inner miter kind.
- **spread** (float) – Amount to spread the miter.
- **custom_profile** ([`bpy.types.bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct") | None) – CurveProfile, if None ignored
- **vmesh_method** (Literal['ADJ', 'CUTOFF']) – The method to use to create meshes at intersections.

**Returns:**

- `faces`:
  Output faces.

  **type** list[[`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]
- `edges`:
  Output edges.

  **type** list[[`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge")]
- `verts`:
  Output verts.

  **type** list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert")]

**Return type:**

dict[str, Any]

<a id="bmesh.ops.beautify_fill"></a>

### bmesh.ops.beautify_fill(bm, faces=[], edges=[], use_restrict_tag=False, method='AREA')

Beautify Fill.

Rotate edges to create more evenly spaced triangles.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **faces** (list[[`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]) – Input faces.
- **edges** (list[[`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge")]) – Edges that can be flipped.
- **use_restrict_tag** (bool) – Restrict edge rotation to mixed tagged vertices.
- **method** (Literal['AREA', 'ANGLE']) – Method to define what is beautiful.

**Returns:**

- `geom`:
  New flipped faces and edges.

  **type** list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]

**Return type:**

dict[str, Any]

<a id="bmesh.ops.triangle_fill"></a>

### bmesh.ops.triangle_fill(bm, use_beauty=False, use_dissolve=False, edges=[], normal=(0.0, 0.0, 0.0))

Triangle Fill.

Fill edges with triangles

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **use_beauty** (bool) – Use best triangulation division.
- **use_dissolve** (bool) – Dissolve resulting faces.
- **edges** (list[[`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge")]) – Input edges.
- **normal** (Sequence[float]) – Optionally pass the fill normal to use.

**Returns:**

- `geom`:
  New faces and edges.

  **type** list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]

**Return type:**

dict[str, Any]

<a id="bmesh.ops.solidify"></a>

### bmesh.ops.solidify(bm, geom=[], thickness=0)

Solidify.

Turns a mesh into a shell with thickness

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **geom** (list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]) – Input geometry.
- **thickness** (float) – Thickness of the solidified shell.

**Returns:**

- `geom`:
  Output geometry (new shell faces, edges, and vertices).

  **type** list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]

**Return type:**

dict[str, Any]

<a id="bmesh.ops.inset_individual"></a>

### bmesh.ops.inset_individual(bm, faces=[], thickness=0, depth=0, use_even_offset=False, use_interpolate=False, use_relative_offset=False)

Face Inset (Individual).

Insets individual faces.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **faces** (list[[`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]) – Input faces.
- **thickness** (float) – Inset distance from the boundary.
- **depth** (float) – Distance to raise or lower the inset face along its normal.
- **use_even_offset** (bool) – Scale the offset to give more even thickness.
- **use_interpolate** (bool) – Blend face data across the inset.
- **use_relative_offset** (bool) – Scale the offset by surrounding geometry.

**Returns:**

- `faces`:
  Output faces.

  **type** list[[`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]

**Return type:**

dict[str, Any]

<a id="bmesh.ops.inset_region"></a>

### bmesh.ops.inset_region(bm, faces=[], faces_exclude=[], use_boundary=False, use_even_offset=False, use_interpolate=False, use_relative_offset=False, use_edge_rail=False, thickness=0, depth=0, use_outset=False)

Face Inset (Regions).

Inset or outset face regions.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **faces** (list[[`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]) – Input faces.
- **faces_exclude** (list[[`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]) – Input faces to explicitly exclude from inset.
- **use_boundary** (bool) – Inset face boundaries.
- **use_even_offset** (bool) – Scale the offset to give more even thickness.
- **use_interpolate** (bool) – Blend face data across the inset.
- **use_relative_offset** (bool) – Scale the offset by surrounding geometry.
- **use_edge_rail** (bool) – Inset the region along existing edges.
- **thickness** (float) – Inset distance from the boundary.
- **depth** (float) – Distance to raise or lower the inset face along its normal.
- **use_outset** (bool) – Outset rather than inset.

**Returns:**

- `faces`:
  Output faces.

  **type** list[[`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]

**Return type:**

dict[str, Any]

<a id="bmesh.ops.offset_edgeloops"></a>

### bmesh.ops.offset_edgeloops(bm, edges=[], use_cap_endpoint=False)

Edge-loop Offset.

Creates edge loops based on simple edge-outset method.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **edges** (list[[`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge")]) – Input edges.
- **use_cap_endpoint** (bool) – Extend loop around end-points.

**Returns:**

- `edges`:
  Output edges.

  **type** list[[`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge")]

**Return type:**

dict[str, Any]

<a id="bmesh.ops.wireframe"></a>

### bmesh.ops.wireframe(bm, faces=[], thickness=0, offset=0, use_replace=False, use_boundary=False, use_even_offset=False, use_crease=False, crease_weight=0, use_relative_offset=False, material_offset=0)

Wire Frame.

Makes a wire-frame copy of faces.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **faces** (list[[`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]) – Input faces.
- **thickness** (float) – Wire thickness.
- **offset** (float) – Offset the thickness from the center.
- **use_replace** (bool) – Remove original geometry.
- **use_boundary** (bool) – Inset face boundaries.
- **use_even_offset** (bool) – Scale the offset to give more even thickness.
- **use_crease** (bool) – Crease hub edges for improved subdivision surface.
- **crease_weight** (float) – The mean crease weight for resulting edges.
- **use_relative_offset** (bool) – Scale the offset by surrounding geometry.
- **material_offset** (int) – Offset material index of generated faces.

**Returns:**

- `faces`:
  Output faces.

  **type** list[[`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]

**Return type:**

dict[str, Any]

<a id="bmesh.ops.poke"></a>

### bmesh.ops.poke(bm, faces=[], offset=0, center_mode='MEAN_WEIGHTED', use_relative_offset=False)

Pokes a face.

Splits a face into a triangle fan.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **faces** (list[[`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]) – Input faces.
- **offset** (float) – Center vertex offset along normal.
- **center_mode** (Literal['MEAN_WEIGHTED', 'MEAN', 'BOUNDS']) – Calculation mode for center vertex.
- **use_relative_offset** (bool) – Apply offset.

**Returns:**

- `verts`:
  Output verts.

  **type** list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert")]
- `faces`:
  Output faces.

  **type** list[[`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]

**Return type:**

dict[str, Any]

<a id="bmesh.ops.convex_hull"></a>

### bmesh.ops.convex_hull(bm, input=[], use_existing_faces=False)

Convex Hull

Builds a convex hull from the vertices in `input`.

If `use_existing_faces` is true, the hull will not output triangles
that are covered by a pre-existing face.

All hull vertices, faces, and edges are added to `geom.out`. Any
input elements that end up inside the hull (i.e. are not used by an
output face) are added to the `geom_interior.out` slot. The
`geom_unused.out` slot will contain all interior geometry that is
completely unused. Lastly, `geom_holes.out` contains edges and faces
that were in the input and are part of the hull.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **input** (list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]) – Input geometry.
- **use_existing_faces** (bool) – Skip hull triangles that are covered by a pre-existing face.

**Returns:**

- `geom`:

  **type** list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]
- `geom_interior`:

  **type** list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]
- `geom_unused`:

  **type** list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]
- `geom_holes`:

  **type** list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]

**Return type:**

dict[str, Any]

<a id="bmesh.ops.space_edge_loops_evenly"></a>

### bmesh.ops.space_edge_loops_evenly(bm, geom=[], interpolation='CUBIC', factor=0, lock_x=False, lock_y=False, lock_z=False)

Space Evenly.

Space the vertices in a regular distribution on the loop.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **geom** (list[[`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge")]) – Input geometry.
- **interpolation** (Literal['CUBIC', 'LINEAR']) – Method used for interpolation.
- **factor** (float) – Influence factor: spans from 0.0 to 1.0.
- **lock_x** (bool) – Lock X-axis editing.
- **lock_y** (bool) – Lock Y-axis editing.
- **lock_z** (bool) – Lock Z-axis editing.

<a id="bmesh.ops.symmetrize"></a>

### bmesh.ops.symmetrize(bm, input=[], direction='-X', dist=0, use_shapekey=False)

Symmetrize.

Makes the mesh elements in the `input` slot symmetrical. Unlike
normal mirroring, it only copies in one direction, as specified by
the `direction` slot. The edges and faces that cross the plane of
symmetry are split as needed to enforce symmetry.

All new vertices, edges, and faces are added to the `geom.out` slot.

**Parameters:**

- **bm** ([`bmesh.types.BMesh`](bmesh.types.md#bmesh.types.BMesh "bmesh.types.BMesh")) – The bmesh to operate on.
- **input** (list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]) – Input geometry.
- **direction** (Literal['-X', '-Y', '-Z', 'X', 'Y', 'Z']) – Axis to use.
- **dist** (float) – Minimum distance.
- **use_shapekey** (bool) – Transform shape keys too.

**Returns:**

- `geom`:

  **type** list[[`bmesh.types.BMVert`](bmesh.types.md#bmesh.types.BMVert "bmesh.types.BMVert") | [`bmesh.types.BMEdge`](bmesh.types.md#bmesh.types.BMEdge "bmesh.types.BMEdge") | [`bmesh.types.BMFace`](bmesh.types.md#bmesh.types.BMFace "bmesh.types.BMFace")]

**Return type:**

dict[str, Any]
