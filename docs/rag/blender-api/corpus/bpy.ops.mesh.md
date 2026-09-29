<!-- source: Blender Python API reference 5.2 / bpy.ops.mesh.html -->

<a id="module-bpy.ops.mesh"></a>

# Mesh Operators

<a id="bpy.ops.mesh.attribute_set"></a>

### bpy.ops.mesh.attribute_set(*, value_float=0.0, value_float_vector_2d=(0.0, 0.0), value_float_vector_3d=(0.0, 0.0, 0.0), value_float_vector_4d=(0.0, 0.0, 0.0, 0.0), value_int=0, value_int_vector_2d=(0, 0), value_color=(1.0, 1.0, 1.0, 1.0), value_bool=False)

Set values of the active attribute for selected elements

**Parameters:**

- **value_float** (float) – Value, (in [-inf, inf], optional)
- **value_float_vector_2d** (Sequence[float]) – Value, (array of 2 items, in [-inf, inf], optional)
- **value_float_vector_3d** (Sequence[float]) – Value, (array of 3 items, in [-inf, inf], optional)
- **value_float_vector_4d** (Sequence[float]) – Value, (array of 4 items, in [-inf, inf], optional)
- **value_int** (int) – Value, (in [-inf, inf], optional)
- **value_int_vector_2d** (Sequence[int]) – Value, (array of 2 items, in [-inf, inf], optional)
- **value_color** (Sequence[float]) – Value, (array of 4 items, in [-inf, inf], optional)
- **value_bool** (bool) – Value, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.average_normals"></a>

### bpy.ops.mesh.average_normals(*, average_type='CUSTOM_NORMAL', weight=50, threshold=0.01)

Average custom normals of selected vertices

**Parameters:**

- **average_type** (Literal['CUSTOM_NORMAL', 'FACE_AREA', 'CORNER_ANGLE']) –

  Type, Averaging method (optional)

  - `CUSTOM_NORMAL`
    Custom Normal – Take average of vertex normals.
  - `FACE_AREA`
    Face Area – Set all vertex normals by face area.
  - `CORNER_ANGLE`
    Corner Angle – Set all vertex normals by corner angle.
- **weight** (int) – Weight, Weight applied per face (in [1, 100], optional)
- **threshold** (float) – Threshold, Threshold value for different weights to be considered equal (in [0, 10], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.beautify_fill"></a>

### bpy.ops.mesh.beautify_fill(*, angle_limit=3.14159)

Rearrange some faces to try to get less degenerated geometry

**Parameters:**

**angle_limit** (float) – Max Angle, Angle limit (in [0, 3.14159], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.bevel"></a>

### bpy.ops.mesh.bevel(*, offset_type='OFFSET', offset=0.0, profile_type='SUPERELLIPSE', offset_pct=0.0, segments=1, profile=0.5, affect='EDGES', clamp_overlap=False, loop_slide=True, mark_seam=False, mark_sharp=False, material=-1, harden_normals=False, face_strength_mode='NONE', miter_outer='SHARP', miter_inner='SHARP', spread=0.1, vmesh_method='ADJ', release_confirm=False)

Cut into selected items at an angle to create bevel or chamfer

**Parameters:**

- **offset_type** (Literal['OFFSET', 'WIDTH', 'DEPTH', 'PERCENT', 'ABSOLUTE']) –

  Width Type, The method for determining the size of the bevel (optional)

  - `OFFSET`
    Offset – Amount is offset of new edges from original.
  - `WIDTH`
    Width – Amount is width of new face.
  - `DEPTH`
    Depth – Amount is perpendicular distance from original edge to bevel face.
  - `PERCENT`
    Percent – Amount is percent of adjacent edge length.
  - `ABSOLUTE`
    Absolute – Amount is absolute distance along adjacent edge.
- **offset** (float) – Width, Bevel amount (in [0, 1e+06], optional)
- **profile_type** (Literal['SUPERELLIPSE', 'CUSTOM']) –

  Profile Type, The type of shape used to rebuild a beveled section (optional)

  - `SUPERELLIPSE`
    Superellipse – The profile can be a concave or convex curve.
  - `CUSTOM`
    Custom – The profile can be any arbitrary path between its endpoints.
- **offset_pct** (float) – Width Percent, Bevel amount for percentage method (in [0, 100], optional)
- **segments** (int) – Segments, Segments for curved edge (in [1, 1000], optional)
- **profile** (float) – Profile, Controls profile shape (0.5 = round) (in [0, 1], optional)
- **affect** (Literal['VERTICES', 'EDGES']) –

  Affect, Affect edges or vertices (optional)

  - `VERTICES`
    Vertices – Affect only vertices.
  - `EDGES`
    Edges – Affect only edges.
- **clamp_overlap** (bool) – Clamp Overlap, Do not allow beveled edges/vertices to overlap each other (optional)
- **loop_slide** (bool) – Loop Slide, Prefer sliding along edges to even widths (optional)
- **mark_seam** (bool) – Mark Seams, Preserve seams along beveled edges (optional)
- **mark_sharp** (bool) – Mark Sharp, Preserve sharp edges along beveled edges (optional)
- **material** (int) – Material Index, Material for bevel faces (-1 means use adjacent faces) (in [-1, inf], optional)
- **harden_normals** (bool) – Harden Normals, Match normals of new faces to adjacent faces (optional)
- **face_strength_mode** (Literal['NONE', 'NEW', 'AFFECTED', 'ALL']) –

  Face Strength Mode, Whether to set face strength, and which faces to set face strength on (optional)

  - `NONE`
    None – Do not set face strength.
  - `NEW`
    New – Set face strength on new faces only.
  - `AFFECTED`
    Affected – Set face strength on new and modified faces only.
  - `ALL`
    All – Set face strength on all faces.
- **miter_outer** (Literal['SHARP', 'PATCH', 'ARC']) –

  Outer Miter, Pattern to use for outside of miters (optional)

  - `SHARP`
    Sharp – Outside of miter is sharp.
  - `PATCH`
    Patch – Outside of miter is squared-off patch.
  - `ARC`
    Arc – Outside of miter is arc.
- **miter_inner** (Literal['SHARP', 'ARC']) –

  Inner Miter, Pattern to use for inside of miters (optional)

  - `SHARP`
    Sharp – Inside of miter is sharp.
  - `ARC`
    Arc – Inside of miter is arc.
- **spread** (float) – Spread, Amount to spread arcs for arc inner miters (in [0, 1e+06], optional)
- **vmesh_method** (Literal['ADJ', 'CUTOFF']) –

  Vertex Mesh Method, The method to use to create meshes at intersections (optional)

  - `ADJ`
    Grid Fill – Default patterned fill.
  - `CUTOFF`
    Cutoff – A cutoff at each profile’s end before the intersection.
- **release_confirm** (bool) – Confirm on Release, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.bisect"></a>

### bpy.ops.mesh.bisect(*, plane_co=(0.0, 0.0, 0.0), plane_no=(0.0, 0.0, 0.0), use_fill=False, clear_inner=False, clear_outer=False, threshold=0.0001, xstart=0, xend=0, ystart=0, yend=0, flip=False, cursor=5)

Cut geometry along a plane (click-drag to define plane)

**Parameters:**

- **plane_co** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Plane Point, A point on the plane (array of 3 items, in [-inf, inf], optional)
- **plane_no** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Plane Normal, The direction the plane points (array of 3 items, in [-1, 1], optional)
- **use_fill** (bool) – Fill, Fill in the cut (optional)
- **clear_inner** (bool) – Clear Inner, Remove geometry behind the plane (optional)
- **clear_outer** (bool) – Clear Outer, Remove geometry in front of the plane (optional)
- **threshold** (float) – Axis Threshold, Preserves the existing geometry along the cut plane (in [0, 10], optional)
- **xstart** (int) – X Start, (in [-inf, inf], optional)
- **xend** (int) – X End, (in [-inf, inf], optional)
- **ystart** (int) – Y Start, (in [-inf, inf], optional)
- **yend** (int) – Y End, (in [-inf, inf], optional)
- **flip** (bool) – Flip, (optional)
- **cursor** (int) – Cursor, Mouse cursor style to use during the modal operator (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.blend_from_shape"></a>

### bpy.ops.mesh.blend_from_shape(*, shape='', blend=1.0, add=True)

Blend in shape from a shape key

**Parameters:**

- **shape** (str) – Shape, Shape key to use for blending (optional)
- **blend** (float) – Blend, Blending factor (in [-1000, 1000], optional)
- **add** (bool) – Add, Add rather than blend between shapes (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.bridge_edge_loops"></a>

### bpy.ops.mesh.bridge_edge_loops(*, type='SINGLE', use_merge=False, merge_factor=0.5, twist_offset=0, number_cuts=0, interpolation='PATH', smoothness=1.0, profile_shape_factor=0.0, profile_shape='SMOOTH')

Create a bridge of faces between two or more selected edge loops

**Parameters:**

- **type** (Literal['SINGLE', 'CLOSED', 'PAIRS']) – Connect Loops, Method of bridging multiple loops (optional)
- **use_merge** (bool) – Merge, Merge rather than creating faces (optional)
- **merge_factor** (float) – Merge Factor, (in [0, 1], optional)
- **twist_offset** (int) – Twist, Twist offset for closed loops (in [-1000, 1000], optional)
- **number_cuts** (int) – Number of Cuts, (in [0, 1000], optional)
- **interpolation** (Literal['LINEAR', 'PATH', 'SURFACE']) – Interpolation, Interpolation method (optional)
- **smoothness** (float) – Smoothness, Smoothness factor (in [0, 1000], optional)
- **profile_shape_factor** (float) – Profile Factor, How much intermediary new edges are shrunk/expanded (in [-1000, 1000], optional)
- **profile_shape** (Literal[[Proportional Falloff Curve Only Items](bpy_types_enum_items/proportional_falloff_curve_only_items.md#rna-enum-proportional-falloff-curve-only-items)]) – Profile Shape, Shape of the profile (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.circularize"></a>

### bpy.ops.mesh.circularize(*, factor=1.0, fit_method='LEAST_SQUARE', angle=0.0, use_custom_radius=False, custom_radius=1.0, regular=True, flatten=1.0, lock=(False, False, False))

Shape selected geometry into a circle

**Parameters:**

- **factor** (float) – Factor, Circularization factor (in [0, 1], optional)
- **fit_method** (Literal['LEAST_SQUARE', 'CONTRACT']) –

  Method, Method used for fitting a circle to the vertices (optional)

  - `LEAST_SQUARE`
    Best Fit – Calculate a best-fit circle using non-linear least squares.
  - `CONTRACT`
    Interior Fit – Only move vertices towards the center.
- **angle** (float) – Rotation, Rotate the circle (in [-6.28319, 6.28319], optional)
- **use_custom_radius** (bool) – Use Custom Radius, Enable custom radius (optional)
- **custom_radius** (float) – Radius, Radius of the circle (in [0, inf], optional)
- **regular** (bool) – Space Evenly, Distribute vertices at constant distances along the circle, otherwise preserves original spacing (optional)
- **flatten** (float) – Flatten, Flatten the circle, instead of projecting it on the mesh (in [0, 1], optional)
- **lock** (Sequence[bool]) – Lock, Lock editing of the axis (array of 3 items, optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.colors_reverse"></a>

### bpy.ops.mesh.colors_reverse()

Flip direction of face corner color attribute inside faces

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.colors_rotate"></a>

### bpy.ops.mesh.colors_rotate(*, use_ccw=False)

Rotate face corner color attribute inside faces

**Parameters:**

**use_ccw** (bool) – Counter Clockwise, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.convex_hull"></a>

### bpy.ops.mesh.convex_hull(*, delete_unused=True, use_existing_faces=True, make_holes=False, join_triangles=True, face_threshold=0.698132, shape_threshold=0.698132, topology_influence=0.0, uvs=False, vcols=False, seam=False, sharp=False, materials=False, deselect_joined=False)

Enclose selected vertices in a convex polyhedron

**Parameters:**

- **delete_unused** (bool) – Delete Unused, Delete selected elements that are not used by the hull (optional)
- **use_existing_faces** (bool) – Use Existing Faces, Skip hull triangles that are covered by a pre-existing face (optional)
- **make_holes** (bool) – Make Holes, Delete selected faces that are used by the hull (optional)
- **join_triangles** (bool) – Join Triangles, Merge adjacent triangles into quads (optional)
- **face_threshold** (float) – Max Face Angle, Face angle limit (in [0, 3.14159], optional)
- **shape_threshold** (float) – Max Shape Angle, Shape angle limit (in [0, 3.14159], optional)
- **topology_influence** (float) – Topology Influence, How much to prioritize regular grids of quads as well as quads that touch existing quads (in [0, 2], optional)
- **uvs** (bool) – Compare UVs, (optional)
- **vcols** (bool) – Compare Color Attributes, (optional)
- **seam** (bool) – Compare Seam, (optional)
- **sharp** (bool) – Compare Sharp, (optional)
- **materials** (bool) – Compare Materials, (optional)
- **deselect_joined** (bool) – Deselect Joined, Only select remaining triangles that were not merged (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.customdata_custom_splitnormals_add"></a>

### bpy.ops.mesh.customdata_custom_splitnormals_add()

Add a custom normals layer, if none exists yet

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.customdata_custom_splitnormals_clear"></a>

### bpy.ops.mesh.customdata_custom_splitnormals_clear()

Remove the custom normals layer, if it exists

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.customdata_face_sets_clear"></a>

### bpy.ops.mesh.customdata_face_sets_clear()

Clear sculpt face set data from the mesh

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.customdata_mask_clear"></a>

### bpy.ops.mesh.customdata_mask_clear()

Clear vertex sculpt masking data from the mesh

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.customdata_skin_add"></a>

### bpy.ops.mesh.customdata_skin_add()

Add a vertex skin layer

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.customdata_skin_clear"></a>

### bpy.ops.mesh.customdata_skin_clear()

Clear vertex skin layer

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.decimate"></a>

### bpy.ops.mesh.decimate(*, ratio=1.0, use_vertex_group=False, vertex_group_factor=1.0, invert_vertex_group=False, use_symmetry=False, symmetry_axis='Y')

Simplify geometry by collapsing edges

**Parameters:**

- **ratio** (float) – Ratio, (in [0, 1], optional)
- **use_vertex_group** (bool) – Vertex Group, Use active vertex group as an influence (optional)
- **vertex_group_factor** (float) – Weight, Vertex group strength (in [0, 1000], optional)
- **invert_vertex_group** (bool) – Invert, Invert vertex group influence (optional)
- **use_symmetry** (bool) – Symmetry, Maintain symmetry on an axis (optional)
- **symmetry_axis** (Literal[[Axis Xyz Items](bpy_types_enum_items/axis_xyz_items.md#rna-enum-axis-xyz-items)]) – Axis, Axis of symmetry (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.delete"></a>

### bpy.ops.mesh.delete(*, type='VERT')

Delete selected vertices, edges or faces

**Parameters:**

**type** (Literal['VERT', 'EDGE', 'FACE', 'EDGE_FACE', 'ONLY_FACE']) – Type, Method used for deleting mesh data (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.delete_edgeloop"></a>

### bpy.ops.mesh.delete_edgeloop(*, use_face_split=True)

Delete an edge loop by merging the faces on each side

**Parameters:**

**use_face_split** (bool) – Face Split, Split off face corners to maintain surrounding geometry (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.delete_loose"></a>

### bpy.ops.mesh.delete_loose(*, use_verts=True, use_edges=True, use_faces=False)

Delete loose vertices, edges or faces

**Parameters:**

- **use_verts** (bool) – Vertices, Remove loose vertices (optional)
- **use_edges** (bool) – Edges, Remove loose edges (optional)
- **use_faces** (bool) – Faces, Remove loose faces (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.dissolve_degenerate"></a>

### bpy.ops.mesh.dissolve_degenerate(*, threshold=0.0001)

Dissolve zero area faces and zero length edges

**Parameters:**

**threshold** (float) – Merge Distance, Maximum distance between elements to merge (in [1e-06, 50], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.dissolve_edges"></a>

### bpy.ops.mesh.dissolve_edges(*, use_verts=True, angle_threshold=3.14159, use_face_split=False, use_preserve_quads=True)

Dissolve edges, merging faces

**Parameters:**

- **use_verts** (bool) – Dissolve Vertices, Dissolve remaining vertices which connect to only two edges (optional)
- **angle_threshold** (float) – Angle Threshold, Remaining vertices which separate edge pairs are preserved if their edge angle exceeds this threshold. (in [0, 3.14159], optional)
- **use_face_split** (bool) – Face Split, Split off face corners to maintain surrounding geometry (optional)
- **use_preserve_quads** (bool) – Preserve Quads, When dissolving the edge between two triangles, don’t dissolve vertices (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.dissolve_faces"></a>

### bpy.ops.mesh.dissolve_faces(*, use_verts=False)

Dissolve faces

**Parameters:**

**use_verts** (bool) – Dissolve Vertices, Dissolve remaining vertices which connect to only two edges (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.dissolve_limited"></a>

### bpy.ops.mesh.dissolve_limited(*, angle_limit=0.0872665, use_dissolve_boundaries=False, delimit={'NORMAL'})

Dissolve selected edges and vertices, limited by the angle of surrounding geometry

**Parameters:**

- **angle_limit** (float) – Max Angle, Angle limit (in [0, 3.14159], optional)
- **use_dissolve_boundaries** (bool) – All Boundaries, Dissolve all vertices in between face boundaries (optional)
- **delimit** (set[Literal[[Mesh Delimit Mode Items](bpy_types_enum_items/mesh_delimit_mode_items.md#rna-enum-mesh-delimit-mode-items)]]) – Delimit, Delimit dissolve operation (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.dissolve_mode"></a>

### bpy.ops.mesh.dissolve_mode(*, use_verts=False, angle_threshold=3.14159, use_preserve_quads=True, use_face_split=False, use_boundary_tear=False)

Dissolve geometry based on the selection mode

**Parameters:**

- **use_verts** (bool) – Dissolve Vertices, Dissolve remaining vertices which connect to only two edges (optional)
- **angle_threshold** (float) – Angle Threshold, Remaining vertices which separate edge pairs are preserved if their edge angle exceeds this threshold. (in [0, 3.14159], optional)
- **use_preserve_quads** (bool) – Preserve Quads, When dissolving the edge between two triangles, don’t dissolve vertices (optional)
- **use_face_split** (bool) – Face Split, Split off face corners to maintain surrounding geometry (optional)
- **use_boundary_tear** (bool) – Tear Boundary, Split off face corners instead of merging faces (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.dissolve_verts"></a>

### bpy.ops.mesh.dissolve_verts(*, use_face_split=False, use_boundary_tear=False)

Dissolve vertices, merge edges and faces

**Parameters:**

- **use_face_split** (bool) – Face Split, Split off face corners to maintain surrounding geometry (optional)
- **use_boundary_tear** (bool) – Tear Boundary, Split off face corners instead of merging faces (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.dupli_extrude_cursor"></a>

### bpy.ops.mesh.dupli_extrude_cursor(*, rotate_source=True)

Duplicate and extrude selected vertices, edges or faces towards the mouse cursor

**Parameters:**

**rotate_source** (bool) – Rotate Source, Rotate initial selection giving better shape (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.duplicate"></a>

### bpy.ops.mesh.duplicate(*, mode=1)

Duplicate selected vertices, edges or faces

**Parameters:**

**mode** (int) – Mode, (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.duplicate_move"></a>

### bpy.ops.mesh.duplicate_move(*, MESH_OT_duplicate={}, TRANSFORM_OT_translate={})

Duplicate mesh and move

**Parameters:**

- **MESH_OT_duplicate** (dict[str, Any]) – Duplicate, Duplicate selected vertices, edges or faces (optional, [`bpy.ops.mesh.duplicate()`](#bpy.ops.mesh.duplicate "bpy.ops.mesh.duplicate") keyword arguments)
- **TRANSFORM_OT_translate** (dict[str, Any]) – Move, Move selected items (optional, [`bpy.ops.transform.translate()`](bpy.ops.transform.md#bpy.ops.transform.translate "bpy.ops.transform.translate") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.edge_collapse"></a>

### bpy.ops.mesh.edge_collapse()

Collapse isolated edge and face regions, merging data such as UVs and color attributes. This can collapse edge-rings as well as regions of connected faces into vertices

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.edge_face_add"></a>

### bpy.ops.mesh.edge_face_add()

Add an edge or face to selected

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.edge_rotate"></a>

### bpy.ops.mesh.edge_rotate(*, use_ccw=False)

Rotate selected edge or adjoining faces

**Parameters:**

**use_ccw** (bool) – Counter Clockwise, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.edge_split"></a>

### bpy.ops.mesh.edge_split(*, type='EDGE')

Split selected edges so that each neighbor face gets its own copy

**Parameters:**

**type** (Literal['EDGE', 'VERT']) –

Type, Method to use for splitting (optional)

- `EDGE`
  Faces by Edges – Split faces along selected edges.
- `VERT`
  Faces & Edges by Vertices – Split faces and edges connected to selected vertices.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.edgering_select"></a>

### bpy.ops.mesh.edgering_select(*, delimit_edge_ring={'NGONS'}, extend=False, deselect=False, toggle=False, object_index=-1, edge_index=-1, vert_index=-1, face_index=-1)

Select an edge ring

**Parameters:**

- **delimit_edge_ring** (set[Literal[[Mesh Walk Delimit Edge Ring Items](bpy_types_enum_items/mesh_walk_delimit_edge_ring_items.md#rna-enum-mesh-walk-delimit-edge-ring-items)]]) – Edge Ring Delimit, Delimit edge ring selection (optional)
- **extend** (bool) – Extend Select, Extend the selection (optional)
- **deselect** (bool) – Deselect, Remove from the selection (optional)
- **toggle** (bool) – Toggle Select, Toggle the selection (optional)
- **object_index** (int) – (in [-1, inf], optional)
- **edge_index** (int) – (in [-1, inf], optional)
- **vert_index** (int) – (in [-1, inf], optional)
- **face_index** (int) – (in [-1, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.edges_select_sharp"></a>

### bpy.ops.mesh.edges_select_sharp(*, sharpness=0.523599)

Select all sharp enough edges

**Parameters:**

**sharpness** (float) – Sharpness, (in [0.000174533, 3.14159], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.extrude_context"></a>

### bpy.ops.mesh.extrude_context(*, use_normal_flip=False, use_dissolve_ortho_edges=False, mirror=False)

Extrude selection

**Parameters:**

- **use_normal_flip** (bool) – Flip Normals, (optional)
- **use_dissolve_ortho_edges** (bool) – Dissolve Orthogonal Edges, (optional)
- **mirror** (bool) – Mirror Editing, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.extrude_context_move"></a>

### bpy.ops.mesh.extrude_context_move(*, MESH_OT_extrude_context={}, TRANSFORM_OT_translate={})

Extrude region together along the average normal

**Parameters:**

- **MESH_OT_extrude_context** (dict[str, Any]) – Extrude Context, Extrude selection (optional, [`bpy.ops.mesh.extrude_context()`](#bpy.ops.mesh.extrude_context "bpy.ops.mesh.extrude_context") keyword arguments)
- **TRANSFORM_OT_translate** (dict[str, Any]) – Move, Move selected items (optional, [`bpy.ops.transform.translate()`](bpy.ops.transform.md#bpy.ops.transform.translate "bpy.ops.transform.translate") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.extrude_edges_indiv"></a>

### bpy.ops.mesh.extrude_edges_indiv(*, use_normal_flip=False, mirror=False)

Extrude individual edges only

**Parameters:**

- **use_normal_flip** (bool) – Flip Normals, (optional)
- **mirror** (bool) – Mirror Editing, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.extrude_edges_move"></a>

### bpy.ops.mesh.extrude_edges_move(*, MESH_OT_extrude_edges_indiv={}, TRANSFORM_OT_translate={})

Extrude edges and move result

**Parameters:**

- **MESH_OT_extrude_edges_indiv** (dict[str, Any]) – Extrude Only Edges, Extrude individual edges only (optional, [`bpy.ops.mesh.extrude_edges_indiv()`](#bpy.ops.mesh.extrude_edges_indiv "bpy.ops.mesh.extrude_edges_indiv") keyword arguments)
- **TRANSFORM_OT_translate** (dict[str, Any]) – Move, Move selected items (optional, [`bpy.ops.transform.translate()`](bpy.ops.transform.md#bpy.ops.transform.translate "bpy.ops.transform.translate") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.extrude_faces_indiv"></a>

### bpy.ops.mesh.extrude_faces_indiv(*, mirror=False)

Extrude individual faces only

**Parameters:**

**mirror** (bool) – Mirror Editing, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.extrude_faces_move"></a>

### bpy.ops.mesh.extrude_faces_move(*, MESH_OT_extrude_faces_indiv={}, TRANSFORM_OT_shrink_fatten={})

Extrude each individual face separately along local normals

**Parameters:**

- **MESH_OT_extrude_faces_indiv** (dict[str, Any]) – Extrude Individual Faces, Extrude individual faces only (optional, [`bpy.ops.mesh.extrude_faces_indiv()`](#bpy.ops.mesh.extrude_faces_indiv "bpy.ops.mesh.extrude_faces_indiv") keyword arguments)
- **TRANSFORM_OT_shrink_fatten** (dict[str, Any]) – Shrink/Fatten, Shrink/fatten selected vertices along normals (optional, [`bpy.ops.transform.shrink_fatten()`](bpy.ops.transform.md#bpy.ops.transform.shrink_fatten "bpy.ops.transform.shrink_fatten") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.extrude_manifold"></a>

### bpy.ops.mesh.extrude_manifold(*, MESH_OT_extrude_region={}, TRANSFORM_OT_translate={})

Extrude, dissolves edges whose faces form a flat surface and intersect new edges

**Parameters:**

- **MESH_OT_extrude_region** (dict[str, Any]) – Extrude Region, Extrude region of faces (optional, [`bpy.ops.mesh.extrude_region()`](#bpy.ops.mesh.extrude_region "bpy.ops.mesh.extrude_region") keyword arguments)
- **TRANSFORM_OT_translate** (dict[str, Any]) – Move, Move selected items (optional, [`bpy.ops.transform.translate()`](bpy.ops.transform.md#bpy.ops.transform.translate "bpy.ops.transform.translate") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.extrude_region"></a>

### bpy.ops.mesh.extrude_region(*, use_normal_flip=False, use_dissolve_ortho_edges=False, mirror=False)

Extrude region of faces

**Parameters:**

- **use_normal_flip** (bool) – Flip Normals, (optional)
- **use_dissolve_ortho_edges** (bool) – Dissolve Orthogonal Edges, (optional)
- **mirror** (bool) – Mirror Editing, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.extrude_region_move"></a>

### bpy.ops.mesh.extrude_region_move(*, MESH_OT_extrude_region={}, TRANSFORM_OT_translate={})

Extrude region and move result

**Parameters:**

- **MESH_OT_extrude_region** (dict[str, Any]) – Extrude Region, Extrude region of faces (optional, [`bpy.ops.mesh.extrude_region()`](#bpy.ops.mesh.extrude_region "bpy.ops.mesh.extrude_region") keyword arguments)
- **TRANSFORM_OT_translate** (dict[str, Any]) – Move, Move selected items (optional, [`bpy.ops.transform.translate()`](bpy.ops.transform.md#bpy.ops.transform.translate "bpy.ops.transform.translate") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.extrude_region_shrink_fatten"></a>

### bpy.ops.mesh.extrude_region_shrink_fatten(*, MESH_OT_extrude_region={}, TRANSFORM_OT_shrink_fatten={})

Extrude region together along local normals

**Parameters:**

- **MESH_OT_extrude_region** (dict[str, Any]) – Extrude Region, Extrude region of faces (optional, [`bpy.ops.mesh.extrude_region()`](#bpy.ops.mesh.extrude_region "bpy.ops.mesh.extrude_region") keyword arguments)
- **TRANSFORM_OT_shrink_fatten** (dict[str, Any]) – Shrink/Fatten, Shrink/fatten selected vertices along normals (optional, [`bpy.ops.transform.shrink_fatten()`](bpy.ops.transform.md#bpy.ops.transform.shrink_fatten "bpy.ops.transform.shrink_fatten") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.extrude_repeat"></a>

### bpy.ops.mesh.extrude_repeat(*, steps=10, offset=(0.0, 0.0, 0.0), scale_offset=1.0)

Extrude selected vertices, edges or faces repeatedly

**Parameters:**

- **steps** (int) – Steps, (in [0, 1000000], optional)
- **offset** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Offset, Offset vector (array of 3 items, in [-100000, 100000], optional)
- **scale_offset** (float) – Scale Offset, (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.extrude_vertices_move"></a>

### bpy.ops.mesh.extrude_vertices_move(*, MESH_OT_extrude_verts_indiv={}, TRANSFORM_OT_translate={})

Extrude vertices and move result

**Parameters:**

- **MESH_OT_extrude_verts_indiv** (dict[str, Any]) – Extrude Only Vertices, Extrude individual vertices only (optional, [`bpy.ops.mesh.extrude_verts_indiv()`](#bpy.ops.mesh.extrude_verts_indiv "bpy.ops.mesh.extrude_verts_indiv") keyword arguments)
- **TRANSFORM_OT_translate** (dict[str, Any]) – Move, Move selected items (optional, [`bpy.ops.transform.translate()`](bpy.ops.transform.md#bpy.ops.transform.translate "bpy.ops.transform.translate") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.extrude_verts_indiv"></a>

### bpy.ops.mesh.extrude_verts_indiv(*, mirror=False)

Extrude individual vertices only

**Parameters:**

**mirror** (bool) – Mirror Editing, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.face_make_planar"></a>

### bpy.ops.mesh.face_make_planar(*, factor=1.0, repeat=1)

Flatten selected faces

**Parameters:**

- **factor** (float) – Factor, (in [-10, 10], optional)
- **repeat** (int) – Iterations, (in [1, 10000], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.face_split_by_edges"></a>

### bpy.ops.mesh.face_split_by_edges()

Weld loose edges into faces (splitting them into new faces)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.faces_select_linked_flat"></a>

### bpy.ops.mesh.faces_select_linked_flat(*, sharpness=0.0174533)

Select linked faces by angle

**Parameters:**

**sharpness** (float) – Sharpness, (in [0.000174533, 3.14159], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.faces_shade_flat"></a>

### bpy.ops.mesh.faces_shade_flat()

Display faces flat

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.faces_shade_smooth"></a>

### bpy.ops.mesh.faces_shade_smooth()

Display faces smooth (using vertex normals)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.fill"></a>

### bpy.ops.mesh.fill(*, use_beauty=True)

Fill a selected edge loop with faces

**Parameters:**

**use_beauty** (bool) – Beauty, Use best triangulation division (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.fill_grid"></a>

### bpy.ops.mesh.fill_grid(*, span=1, offset=0, use_interp_simple=False)

Fill grid from two loops

**Parameters:**

- **span** (int) – Span, Number of grid columns (in [1, 1000], optional)
- **offset** (int) – Offset, Vertex that is the corner of the grid (in [-1000, 1000], optional)
- **use_interp_simple** (bool) – Simple Blending, Use simple interpolation of grid vertices (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.fill_holes"></a>

### bpy.ops.mesh.fill_holes(*, sides=4)

Fill in holes (boundary edge loops)

**Parameters:**

**sides** (int) – Sides, Number of sides in hole required to fill (zero fills all holes) (in [0, 1000], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.flatten"></a>

### bpy.ops.mesh.flatten(*, factor=1.0, method='BEST_FIT', lock=(False, False, False))

Flatten vertices on a best-fitting plane

**Parameters:**

- **factor** (float) – Factor, Flattening factor (in [0, 1], optional)
- **method** (Literal['BEST_FIT', 'NORMAL', 'VIEW']) –

  Method, Plane on which vertices are flattened (optional)

  - `BEST_FIT`
    Best Fit – Calculate a best fitting plane.
  - `NORMAL`
    Normal – Derive plane by averaging face normals.
  - `VIEW`
    View – Flatten on a plane perpendicular to the viewing angle.
- **lock** (Sequence[bool]) – Lock, Lock editing of the axis (array of 3 items, optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.flip_normals"></a>

### bpy.ops.mesh.flip_normals(*, only_clnors=False)

Flip the direction of selected faces’ normals (and of their vertices)

**Parameters:**

**only_clnors** (bool) – Custom Normals Only, Only flip the custom loop normals of the selected elements (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.flip_quad_tessellation"></a>

### bpy.ops.mesh.flip_quad_tessellation()

Flips the tessellation of selected quads

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.hide"></a>

### bpy.ops.mesh.hide(*, unselected=False)

Hide (un)selected vertices, edges or faces

**Parameters:**

**unselected** (bool) – Unselected, Hide unselected rather than selected (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.inset"></a>

### bpy.ops.mesh.inset(*, use_boundary=True, use_even_offset=True, use_relative_offset=False, use_edge_rail=False, thickness=0.0, depth=0.0, use_outset=False, use_select_inset=False, use_individual=False, use_interpolate=True, release_confirm=False)

Inset new faces into selected faces

**Parameters:**

- **use_boundary** (bool) – Boundary, Inset face boundaries (optional)
- **use_even_offset** (bool) – Offset Even, Scale the offset to give more even thickness (optional)
- **use_relative_offset** (bool) – Offset Relative, Scale the offset by surrounding geometry (optional)
- **use_edge_rail** (bool) – Edge Rail, Inset the region along existing edges (optional)
- **thickness** (float) – Thickness, (in [0, inf], optional)
- **depth** (float) – Depth, (in [-inf, inf], optional)
- **use_outset** (bool) – Outset, Outset rather than inset (optional)
- **use_select_inset** (bool) – Select Outer, Select the new inset faces (optional)
- **use_individual** (bool) – Individual, Individual face inset (optional)
- **use_interpolate** (bool) – Interpolate, Blend face data across the inset (optional)
- **release_confirm** (bool) – Confirm on Release, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.intersect"></a>

### bpy.ops.mesh.intersect(*, mode='SELECT_UNSELECT', separate_mode='CUT', threshold=1e-06, solver='EXACT')

Cut an intersection into faces

**Parameters:**

- **mode** (Literal['SELECT', 'SELECT_UNSELECT']) –

  Source, (optional)

  - `SELECT`
    Self Intersect – Self intersect selected faces.
  - `SELECT_UNSELECT`
    Selected/Unselected – Intersect selected with unselected faces.
- **separate_mode** (Literal['ALL', 'CUT', 'NONE']) –

  Separate Mode, (optional)

  - `ALL`
    All – Separate all geometry from intersections.
  - `CUT`
    Cut – Cut into geometry keeping each side separate (Selected/Unselected only).
  - `NONE`
    Merge – Merge all geometry from the intersection.
- **threshold** (float) – Merge Threshold, (in [0, 0.01], optional)
- **solver** (Literal['FLOAT', 'EXACT']) –

  Solver, Which Intersect solver to use (optional)

  - `FLOAT`
    Float – Simple solver with good performance, without support for overlapping geometry.
  - `EXACT`
    Exact – Slower solver with the best results for coplanar faces.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.intersect_boolean"></a>

### bpy.ops.mesh.intersect_boolean(*, operation='DIFFERENCE', use_swap=False, use_self=False, threshold=1e-06, solver='EXACT')

Cut solid geometry from selected to unselected

**Parameters:**

- **operation** (Literal['INTERSECT', 'UNION', 'DIFFERENCE']) – Boolean Operation, Which boolean operation to apply (optional)
- **use_swap** (bool) – Swap, Use with difference intersection to swap which side is kept (optional)
- **use_self** (bool) – Self Intersection, Do self-union or self-intersection (optional)
- **threshold** (float) – Merge Threshold, (in [0, 0.01], optional)
- **solver** (Literal['FLOAT', 'EXACT']) –

  Solver, Which Boolean solver to use (optional)

  - `FLOAT`
    Float – Faster solver, some limitations.
  - `EXACT`
    Exact – Exact solver, slower, handles more cases.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.knife_project"></a>

### bpy.ops.mesh.knife_project(*, cut_through=False)

Use other objects outlines and boundaries to project knife cuts

**Parameters:**

**cut_through** (bool) – Cut Through, Cut through all faces, not just visible ones (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.knife_tool"></a>

### bpy.ops.mesh.knife_tool(*, use_occlude_geometry=True, only_selected=False, xray=True, visible_measurements='NONE', angle_snapping='NONE', angle_snapping_increment=0.523599, wait_for_input=True)

Cut new topology

**Parameters:**

- **use_occlude_geometry** (bool) – Occlude Geometry, Only cut the front most geometry (optional)
- **only_selected** (bool) – Only Selected, Only cut selected geometry (optional)
- **xray** (bool) – X-Ray, Show cuts hidden by geometry (optional)
- **visible_measurements** (Literal['NONE', 'BOTH', 'DISTANCE', 'ANGLE']) –

  Measurements, Visible distance and angle measurements (optional)

  - `NONE`
    None – Show no measurements.
  - `BOTH`
    Both – Show both distances and angles.
  - `DISTANCE`
    Distance – Show just distance measurements.
  - `ANGLE`
    Angle – Show just angle measurements.
- **angle_snapping** (Literal['NONE', 'SCREEN', 'RELATIVE']) –

  Angle Snapping, Angle snapping mode (optional)

  - `NONE`
    None – No angle snapping.
  - `SCREEN`
    Screen – Screen space angle snapping.
  - `RELATIVE`
    Relative – Angle snapping relative to the previous cut edge.
- **angle_snapping_increment** (float) – Angle Snap Increment, The angle snap increment used when in constrained angle mode (in [0, 3.14159], optional)
- **wait_for_input** (bool) – Wait for Input, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.loop_select"></a>

### bpy.ops.mesh.loop_select(*, delimit_edge_loop={'NGONS', 'OUTER_CORNERS'}, delimit_face_loop=set(), extend=False, deselect=False, toggle=False, object_index=-1, edge_index=-1, vert_index=-1, face_index=-1)

Select a loop of connected edges

**Parameters:**

- **delimit_edge_loop** (set[Literal[[Mesh Walk Delimit Edge Loop Items](bpy_types_enum_items/mesh_walk_delimit_edge_loop_items.md#rna-enum-mesh-walk-delimit-edge-loop-items)]]) – Delimit, Delimit edge loop selection (optional)
- **delimit_face_loop** (set[Literal[[Mesh Walk Delimit Face Loop Items](bpy_types_enum_items/mesh_walk_delimit_face_loop_items.md#rna-enum-mesh-walk-delimit-face-loop-items)]]) – Face Loop Delimit, Delimit face loop selection (optional)
- **extend** (bool) – Extend Select, Extend the selection (optional)
- **deselect** (bool) – Deselect, Remove from the selection (optional)
- **toggle** (bool) – Toggle Select, Toggle the selection (optional)
- **object_index** (int) – (in [-1, inf], optional)
- **edge_index** (int) – (in [-1, inf], optional)
- **vert_index** (int) – (in [-1, inf], optional)
- **face_index** (int) – (in [-1, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.loop_to_region"></a>

### bpy.ops.mesh.loop_to_region(*, select_bigger=False)

Select region of faces inside of a selected loop of edges

**Parameters:**

**select_bigger** (bool) – Select Bigger, Select bigger regions instead of smaller ones (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.loopcut"></a>

### bpy.ops.mesh.loopcut(*, number_cuts=1, smoothness=0.0, falloff='INVERSE_SQUARE', object_index=-1, edge_index=-1, mesh_select_mode_init=(False, False, False))

Add a new loop between existing loops

**Parameters:**

- **number_cuts** (int) – Number of Cuts, (in [1, 1000000], optional)
- **smoothness** (float) – Smoothness, Smoothness factor (in [-1000, 1000], optional)
- **falloff** (Literal[[Proportional Falloff Curve Only Items](bpy_types_enum_items/proportional_falloff_curve_only_items.md#rna-enum-proportional-falloff-curve-only-items)]) – Falloff, Falloff type of the feather (optional)
- **object_index** (int) – Object Index, (in [-1, inf], optional)
- **edge_index** (int) – Edge Index, (in [-1, inf], optional)
- **mesh_select_mode_init** (Sequence[bool]) – (array of 3 items, optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.loopcut_slide"></a>

### bpy.ops.mesh.loopcut_slide(*, MESH_OT_loopcut={}, TRANSFORM_OT_edge_slide={})

Cut mesh loop and slide it

**Parameters:**

- **MESH_OT_loopcut** (dict[str, Any]) – Loop Cut, Add a new loop between existing loops (optional, [`bpy.ops.mesh.loopcut()`](#bpy.ops.mesh.loopcut "bpy.ops.mesh.loopcut") keyword arguments)
- **TRANSFORM_OT_edge_slide** (dict[str, Any]) – Edge Slide, Slide an edge loop along a mesh (optional, [`bpy.ops.transform.edge_slide()`](bpy.ops.transform.md#bpy.ops.transform.edge_slide "bpy.ops.transform.edge_slide") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.mark_freestyle_edge"></a>

### bpy.ops.mesh.mark_freestyle_edge(*, clear=False)

(Un)mark selected edges as Freestyle feature edges

**Parameters:**

**clear** (bool) – Clear, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.mark_freestyle_face"></a>

### bpy.ops.mesh.mark_freestyle_face(*, clear=False)

(Un)mark selected faces for exclusion from Freestyle feature edge detection

**Parameters:**

**clear** (bool) – Clear, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.mark_seam"></a>

### bpy.ops.mesh.mark_seam(*, clear=False)

(Un)mark selected edges as a seam

**Parameters:**

**clear** (bool) – Clear, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.mark_sharp"></a>

### bpy.ops.mesh.mark_sharp(*, clear=False, use_verts=False)

(Un)mark selected edges as sharp

**Parameters:**

- **clear** (bool) – Clear, (optional)
- **use_verts** (bool) – Vertices, Consider vertices instead of edges to select which edges to (un)tag as sharp (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.merge"></a>

### bpy.ops.mesh.merge(*, type='CENTER', uvs=False)

Merge selected vertices

**Parameters:**

- **type** (Literal['CENTER', 'CURSOR', 'COLLAPSE', 'FIRST', 'LAST']) – Type, Merge method to use (optional)
- **uvs** (bool) – UVs, Move UVs according to merge (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.merge_normals"></a>

### bpy.ops.mesh.merge_normals()

Merge custom normals of selected vertices

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.mod_weighted_strength"></a>

### bpy.ops.mesh.mod_weighted_strength(*, set=False, face_strength='MEDIUM')

Set/Get strength of face (used in Weighted Normal modifier)

**Parameters:**

- **set** (bool) – Set Value, Set value of faces (optional)
- **face_strength** (Literal['WEAK', 'MEDIUM', 'STRONG']) – Face Strength, Strength to use for assigning or selecting face influence for weighted normal modifier (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.normals_make_consistent"></a>

### bpy.ops.mesh.normals_make_consistent(*, inside=False)

Make face and vertex normals point either outside or inside the mesh

**Parameters:**

**inside** (bool) – Inside, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.normals_tools"></a>

### bpy.ops.mesh.normals_tools(*, mode='COPY', absolute=False)

Custom normals tools using Normal Vector of UI

**Parameters:**

- **mode** (Literal['COPY', 'PASTE', 'ADD', 'MULTIPLY', 'RESET']) –

  Mode, Mode of tools taking input from interface (optional)

  - `COPY`
    Copy Normal – Copy normal to the internal clipboard.
  - `PASTE`
    Paste Normal – Paste normal from the internal clipboard.
  - `ADD`
    Add Normal – Add normal vector with selection.
  - `MULTIPLY`
    Multiply Normal – Multiply normal vector with selection.
  - `RESET`
    Reset Normal – Reset the internal clipboard and/or normal of selected element.
- **absolute** (bool) – Absolute Coordinates, Copy Absolute coordinates of Normal vector (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.offset_edge_loops"></a>

### bpy.ops.mesh.offset_edge_loops(*, use_cap_endpoint=False)

Create offset edge loop from the current selection

**Parameters:**

**use_cap_endpoint** (bool) – Cap Endpoint, Extend loop around end-points (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.offset_edge_loops_slide"></a>

### bpy.ops.mesh.offset_edge_loops_slide(*, MESH_OT_offset_edge_loops={}, TRANSFORM_OT_edge_slide={})

Offset edge loop slide

**Parameters:**

- **MESH_OT_offset_edge_loops** (dict[str, Any]) – Offset Edge Loop, Create offset edge loop from the current selection (optional, [`bpy.ops.mesh.offset_edge_loops()`](#bpy.ops.mesh.offset_edge_loops "bpy.ops.mesh.offset_edge_loops") keyword arguments)
- **TRANSFORM_OT_edge_slide** (dict[str, Any]) – Edge Slide, Slide an edge loop along a mesh (optional, [`bpy.ops.transform.edge_slide()`](bpy.ops.transform.md#bpy.ops.transform.edge_slide "bpy.ops.transform.edge_slide") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.point_normals"></a>

### bpy.ops.mesh.point_normals(*, mode='COORDINATES', invert=False, align=False, target_location=(0.0, 0.0, 0.0), spherize=False, spherize_strength=0.1)

Point selected custom normals to specified Target

**Parameters:**

- **mode** (Literal['COORDINATES', 'MOUSE']) –

  Mode, How to define coordinates to point custom normals to (optional)

  - `COORDINATES`
    Coordinates – Use static coordinates (defined by various means).
  - `MOUSE`
    Mouse – Follow mouse cursor.
- **invert** (bool) – Invert, Invert affected normals (optional)
- **align** (bool) – Align, Make all affected normals parallel (optional)
- **target_location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Target, Target location to which normals will point (array of 3 items, in [-inf, inf], optional)
- **spherize** (bool) – Spherize, Interpolate between original and new normals (optional)
- **spherize_strength** (float) – Spherize Strength, Ratio of spherized normal to original normal (in [0, 1], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.poke"></a>

### bpy.ops.mesh.poke(*, offset=0.0, use_relative_offset=False, center_mode='MEDIAN_WEIGHTED')

Split a face into a fan

**Parameters:**

- **offset** (float) – Poke Offset, Poke Offset (in [-1000, 1000], optional)
- **use_relative_offset** (bool) – Offset Relative, Scale the offset by surrounding geometry (optional)
- **center_mode** (Literal['MEDIAN_WEIGHTED', 'MEDIAN', 'BOUNDS']) –

  Poke Center, Poke face center calculation (optional)

  - `MEDIAN_WEIGHTED`
    Weighted Median – Weighted median face center.
  - `MEDIAN`
    Median – Median face center.
  - `BOUNDS`
    Bounds – Face bounds center.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.polybuild_delete_at_cursor"></a>

### bpy.ops.mesh.polybuild_delete_at_cursor(*, mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1.0, use_proportional_connected=False, use_proportional_projected=False, release_confirm=False, use_accurate=False)

Undocumented, consider [contributing](https://developer.blender.org/).

**Parameters:**

- **mirror** (bool) – Mirror Editing, (optional)
- **use_proportional_edit** (bool) – Proportional Editing, (optional)
- **proportional_edit_falloff** (Literal[[Proportional Falloff Items](bpy_types_enum_items/proportional_falloff_items.md#rna-enum-proportional-falloff-items)]) – Proportional Falloff, Falloff type for proportional editing mode (optional)
- **proportional_size** (float) – Proportional Size, (in [1e-06, inf], optional)
- **use_proportional_connected** (bool) – Connected, (optional)
- **use_proportional_projected** (bool) – Projected (2D), (optional)
- **release_confirm** (bool) – Confirm on Release, Always confirm operation when releasing button (optional)
- **use_accurate** (bool) – Accurate, Use accurate transformation (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.polybuild_dissolve_at_cursor"></a>

### bpy.ops.mesh.polybuild_dissolve_at_cursor()

Undocumented, consider [contributing](https://developer.blender.org/).

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.polybuild_extrude_at_cursor_move"></a>

### bpy.ops.mesh.polybuild_extrude_at_cursor_move(*, MESH_OT_polybuild_transform_at_cursor={}, MESH_OT_extrude_edges_indiv={}, TRANSFORM_OT_translate={})

Undocumented, consider [contributing](https://developer.blender.org/).

**Parameters:**

- **MESH_OT_polybuild_transform_at_cursor** (dict[str, Any]) – Poly Build Transform at Cursor, (optional, [`bpy.ops.mesh.polybuild_transform_at_cursor()`](#bpy.ops.mesh.polybuild_transform_at_cursor "bpy.ops.mesh.polybuild_transform_at_cursor") keyword arguments)
- **MESH_OT_extrude_edges_indiv** (dict[str, Any]) – Extrude Only Edges, Extrude individual edges only (optional, [`bpy.ops.mesh.extrude_edges_indiv()`](#bpy.ops.mesh.extrude_edges_indiv "bpy.ops.mesh.extrude_edges_indiv") keyword arguments)
- **TRANSFORM_OT_translate** (dict[str, Any]) – Move, Move selected items (optional, [`bpy.ops.transform.translate()`](bpy.ops.transform.md#bpy.ops.transform.translate "bpy.ops.transform.translate") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.polybuild_face_at_cursor"></a>

### bpy.ops.mesh.polybuild_face_at_cursor(*, create_quads=True, mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1.0, use_proportional_connected=False, use_proportional_projected=False, release_confirm=False, use_accurate=False)

Undocumented, consider [contributing](https://developer.blender.org/).

**Parameters:**

- **create_quads** (bool) – Create Quads, Automatically split edges in triangles to maintain quad topology (optional)
- **mirror** (bool) – Mirror Editing, (optional)
- **use_proportional_edit** (bool) – Proportional Editing, (optional)
- **proportional_edit_falloff** (Literal[[Proportional Falloff Items](bpy_types_enum_items/proportional_falloff_items.md#rna-enum-proportional-falloff-items)]) – Proportional Falloff, Falloff type for proportional editing mode (optional)
- **proportional_size** (float) – Proportional Size, (in [1e-06, inf], optional)
- **use_proportional_connected** (bool) – Connected, (optional)
- **use_proportional_projected** (bool) – Projected (2D), (optional)
- **release_confirm** (bool) – Confirm on Release, Always confirm operation when releasing button (optional)
- **use_accurate** (bool) – Accurate, Use accurate transformation (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.polybuild_face_at_cursor_move"></a>

### bpy.ops.mesh.polybuild_face_at_cursor_move(*, MESH_OT_polybuild_face_at_cursor={}, TRANSFORM_OT_translate={})

Undocumented, consider [contributing](https://developer.blender.org/).

**Parameters:**

- **MESH_OT_polybuild_face_at_cursor** (dict[str, Any]) – Poly Build Face at Cursor, (optional, [`bpy.ops.mesh.polybuild_face_at_cursor()`](#bpy.ops.mesh.polybuild_face_at_cursor "bpy.ops.mesh.polybuild_face_at_cursor") keyword arguments)
- **TRANSFORM_OT_translate** (dict[str, Any]) – Move, Move selected items (optional, [`bpy.ops.transform.translate()`](bpy.ops.transform.md#bpy.ops.transform.translate "bpy.ops.transform.translate") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.polybuild_split_at_cursor"></a>

### bpy.ops.mesh.polybuild_split_at_cursor(*, mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1.0, use_proportional_connected=False, use_proportional_projected=False, release_confirm=False, use_accurate=False)

Undocumented, consider [contributing](https://developer.blender.org/).

**Parameters:**

- **mirror** (bool) – Mirror Editing, (optional)
- **use_proportional_edit** (bool) – Proportional Editing, (optional)
- **proportional_edit_falloff** (Literal[[Proportional Falloff Items](bpy_types_enum_items/proportional_falloff_items.md#rna-enum-proportional-falloff-items)]) – Proportional Falloff, Falloff type for proportional editing mode (optional)
- **proportional_size** (float) – Proportional Size, (in [1e-06, inf], optional)
- **use_proportional_connected** (bool) – Connected, (optional)
- **use_proportional_projected** (bool) – Projected (2D), (optional)
- **release_confirm** (bool) – Confirm on Release, Always confirm operation when releasing button (optional)
- **use_accurate** (bool) – Accurate, Use accurate transformation (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.polybuild_split_at_cursor_move"></a>

### bpy.ops.mesh.polybuild_split_at_cursor_move(*, MESH_OT_polybuild_split_at_cursor={}, TRANSFORM_OT_translate={})

Undocumented, consider [contributing](https://developer.blender.org/).

**Parameters:**

- **MESH_OT_polybuild_split_at_cursor** (dict[str, Any]) – Poly Build Split at Cursor, (optional, [`bpy.ops.mesh.polybuild_split_at_cursor()`](#bpy.ops.mesh.polybuild_split_at_cursor "bpy.ops.mesh.polybuild_split_at_cursor") keyword arguments)
- **TRANSFORM_OT_translate** (dict[str, Any]) – Move, Move selected items (optional, [`bpy.ops.transform.translate()`](bpy.ops.transform.md#bpy.ops.transform.translate "bpy.ops.transform.translate") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.polybuild_transform_at_cursor"></a>

### bpy.ops.mesh.polybuild_transform_at_cursor(*, mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1.0, use_proportional_connected=False, use_proportional_projected=False, release_confirm=False, use_accurate=False)

Undocumented, consider [contributing](https://developer.blender.org/).

**Parameters:**

- **mirror** (bool) – Mirror Editing, (optional)
- **use_proportional_edit** (bool) – Proportional Editing, (optional)
- **proportional_edit_falloff** (Literal[[Proportional Falloff Items](bpy_types_enum_items/proportional_falloff_items.md#rna-enum-proportional-falloff-items)]) – Proportional Falloff, Falloff type for proportional editing mode (optional)
- **proportional_size** (float) – Proportional Size, (in [1e-06, inf], optional)
- **use_proportional_connected** (bool) – Connected, (optional)
- **use_proportional_projected** (bool) – Projected (2D), (optional)
- **release_confirm** (bool) – Confirm on Release, Always confirm operation when releasing button (optional)
- **use_accurate** (bool) – Accurate, Use accurate transformation (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.polybuild_transform_at_cursor_move"></a>

### bpy.ops.mesh.polybuild_transform_at_cursor_move(*, MESH_OT_polybuild_transform_at_cursor={}, TRANSFORM_OT_translate={})

Undocumented, consider [contributing](https://developer.blender.org/).

**Parameters:**

- **MESH_OT_polybuild_transform_at_cursor** (dict[str, Any]) – Poly Build Transform at Cursor, (optional, [`bpy.ops.mesh.polybuild_transform_at_cursor()`](#bpy.ops.mesh.polybuild_transform_at_cursor "bpy.ops.mesh.polybuild_transform_at_cursor") keyword arguments)
- **TRANSFORM_OT_translate** (dict[str, Any]) – Move, Move selected items (optional, [`bpy.ops.transform.translate()`](bpy.ops.transform.md#bpy.ops.transform.translate "bpy.ops.transform.translate") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.primitive_circle_add"></a>

### bpy.ops.mesh.primitive_circle_add(*, vertices=32, radius=1.0, fill_type='NOTHING', calc_uvs=True, enter_editmode=False, align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(0.0, 0.0, 0.0))

Construct a circle mesh

**Parameters:**

- **vertices** (int) – Vertices, (in [3, 10000000], optional)
- **radius** (float) – Radius, (in [0, inf], optional)
- **fill_type** (Literal['NOTHING', 'NGON', 'TRIFAN']) –

  Fill Type, (optional)

  - `NOTHING`
    Nothing – Don’t fill at all.
  - `NGON`
    N-Gon – Use n-gons.
  - `TRIFAN`
    Triangle Fan – Use triangle fans.
- **calc_uvs** (bool) – Generate UVs, Generate a default UV map (optional)
- **enter_editmode** (bool) – Enter Edit Mode, Enter edit mode when adding this object (optional)
- **align** (Literal['WORLD', 'VIEW', 'CURSOR']) –

  Align, The alignment of the new object (optional)

  - `WORLD`
    World – Align the new object to the world.
  - `VIEW`
    View – Align the new object to the view.
  - `CURSOR`
    3D Cursor – Use the 3D cursor orientation for the new object.
- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Location for the newly added object (array of 3 items, in [-inf, inf], optional)
- **rotation** ([`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler") | Sequence[float]) – Rotation, Rotation for the newly added object (array of 3 items, in [-inf, inf], optional)
- **scale** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Scale, Scale for the newly added object (array of 3 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.primitive_cone_add"></a>

### bpy.ops.mesh.primitive_cone_add(*, vertices=32, radius1=1.0, radius2=0.0, depth=2.0, end_fill_type='NGON', calc_uvs=True, enter_editmode=False, align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(0.0, 0.0, 0.0))

Construct a conic mesh

**Parameters:**

- **vertices** (int) – Vertices, (in [3, 10000000], optional)
- **radius1** (float) – Radius 1, (in [0, inf], optional)
- **radius2** (float) – Radius 2, (in [0, inf], optional)
- **depth** (float) – Depth, (in [0, inf], optional)
- **end_fill_type** (Literal['NOTHING', 'NGON', 'TRIFAN']) –

  Base Fill Type, (optional)

  - `NOTHING`
    Nothing – Don’t fill at all.
  - `NGON`
    N-Gon – Use n-gons.
  - `TRIFAN`
    Triangle Fan – Use triangle fans.
- **calc_uvs** (bool) – Generate UVs, Generate a default UV map (optional)
- **enter_editmode** (bool) – Enter Edit Mode, Enter edit mode when adding this object (optional)
- **align** (Literal['WORLD', 'VIEW', 'CURSOR']) –

  Align, The alignment of the new object (optional)

  - `WORLD`
    World – Align the new object to the world.
  - `VIEW`
    View – Align the new object to the view.
  - `CURSOR`
    3D Cursor – Use the 3D cursor orientation for the new object.
- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Location for the newly added object (array of 3 items, in [-inf, inf], optional)
- **rotation** ([`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler") | Sequence[float]) – Rotation, Rotation for the newly added object (array of 3 items, in [-inf, inf], optional)
- **scale** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Scale, Scale for the newly added object (array of 3 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.primitive_cube_add"></a>

### bpy.ops.mesh.primitive_cube_add(*, size=2.0, calc_uvs=True, enter_editmode=False, align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(0.0, 0.0, 0.0))

Construct a cube mesh that consists of six square faces

**Parameters:**

- **size** (float) – Size, (in [0, inf], optional)
- **calc_uvs** (bool) – Generate UVs, Generate a default UV map (optional)
- **enter_editmode** (bool) – Enter Edit Mode, Enter edit mode when adding this object (optional)
- **align** (Literal['WORLD', 'VIEW', 'CURSOR']) –

  Align, The alignment of the new object (optional)

  - `WORLD`
    World – Align the new object to the world.
  - `VIEW`
    View – Align the new object to the view.
  - `CURSOR`
    3D Cursor – Use the 3D cursor orientation for the new object.
- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Location for the newly added object (array of 3 items, in [-inf, inf], optional)
- **rotation** ([`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler") | Sequence[float]) – Rotation, Rotation for the newly added object (array of 3 items, in [-inf, inf], optional)
- **scale** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Scale, Scale for the newly added object (array of 3 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.primitive_cube_add_gizmo"></a>

### bpy.ops.mesh.primitive_cube_add_gizmo(*, calc_uvs=True, enter_editmode=False, align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(0.0, 0.0, 0.0), matrix=((0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0)))

Construct a cube mesh

**Parameters:**

- **calc_uvs** (bool) – Generate UVs, Generate a default UV map (optional)
- **enter_editmode** (bool) – Enter Edit Mode, Enter edit mode when adding this object (optional)
- **align** (Literal['WORLD', 'VIEW', 'CURSOR']) –

  Align, The alignment of the new object (optional)

  - `WORLD`
    World – Align the new object to the world.
  - `VIEW`
    View – Align the new object to the view.
  - `CURSOR`
    3D Cursor – Use the 3D cursor orientation for the new object.
- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Location for the newly added object (array of 3 items, in [-inf, inf], optional)
- **rotation** ([`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler") | Sequence[float]) – Rotation, Rotation for the newly added object (array of 3 items, in [-inf, inf], optional)
- **scale** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Scale, Scale for the newly added object (array of 3 items, in [-inf, inf], optional)
- **matrix** ([`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix") | Sequence[Sequence[float]]) – Matrix, (multi-dimensional array of 4 * 4 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.primitive_cylinder_add"></a>

### bpy.ops.mesh.primitive_cylinder_add(*, vertices=32, radius=1.0, depth=2.0, end_fill_type='NGON', calc_uvs=True, enter_editmode=False, align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(0.0, 0.0, 0.0))

Construct a cylinder mesh

**Parameters:**

- **vertices** (int) – Vertices, (in [3, 10000000], optional)
- **radius** (float) – Radius, (in [0, inf], optional)
- **depth** (float) – Depth, (in [0, inf], optional)
- **end_fill_type** (Literal['NOTHING', 'NGON', 'TRIFAN']) –

  Cap Fill Type, (optional)

  - `NOTHING`
    Nothing – Don’t fill at all.
  - `NGON`
    N-Gon – Use n-gons.
  - `TRIFAN`
    Triangle Fan – Use triangle fans.
- **calc_uvs** (bool) – Generate UVs, Generate a default UV map (optional)
- **enter_editmode** (bool) – Enter Edit Mode, Enter edit mode when adding this object (optional)
- **align** (Literal['WORLD', 'VIEW', 'CURSOR']) –

  Align, The alignment of the new object (optional)

  - `WORLD`
    World – Align the new object to the world.
  - `VIEW`
    View – Align the new object to the view.
  - `CURSOR`
    3D Cursor – Use the 3D cursor orientation for the new object.
- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Location for the newly added object (array of 3 items, in [-inf, inf], optional)
- **rotation** ([`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler") | Sequence[float]) – Rotation, Rotation for the newly added object (array of 3 items, in [-inf, inf], optional)
- **scale** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Scale, Scale for the newly added object (array of 3 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.primitive_grid_add"></a>

### bpy.ops.mesh.primitive_grid_add(*, x_subdivisions=10, y_subdivisions=10, size=2.0, calc_uvs=True, enter_editmode=False, align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(0.0, 0.0, 0.0))

Construct a subdivided plane mesh

**Parameters:**

- **x_subdivisions** (int) – X Subdivisions, (in [1, 10000000], optional)
- **y_subdivisions** (int) – Y Subdivisions, (in [1, 10000000], optional)
- **size** (float) – Size, (in [0, inf], optional)
- **calc_uvs** (bool) – Generate UVs, Generate a default UV map (optional)
- **enter_editmode** (bool) – Enter Edit Mode, Enter edit mode when adding this object (optional)
- **align** (Literal['WORLD', 'VIEW', 'CURSOR']) –

  Align, The alignment of the new object (optional)

  - `WORLD`
    World – Align the new object to the world.
  - `VIEW`
    View – Align the new object to the view.
  - `CURSOR`
    3D Cursor – Use the 3D cursor orientation for the new object.
- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Location for the newly added object (array of 3 items, in [-inf, inf], optional)
- **rotation** ([`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler") | Sequence[float]) – Rotation, Rotation for the newly added object (array of 3 items, in [-inf, inf], optional)
- **scale** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Scale, Scale for the newly added object (array of 3 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.primitive_ico_sphere_add"></a>

### bpy.ops.mesh.primitive_ico_sphere_add(*, subdivisions=2, radius=1.0, calc_uvs=True, enter_editmode=False, align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(0.0, 0.0, 0.0))

Construct a spherical mesh that consists of equally sized triangles

**Parameters:**

- **subdivisions** (int) – Subdivisions, (in [1, 10], optional)
- **radius** (float) – Radius, (in [0, inf], optional)
- **calc_uvs** (bool) – Generate UVs, Generate a default UV map (optional)
- **enter_editmode** (bool) – Enter Edit Mode, Enter edit mode when adding this object (optional)
- **align** (Literal['WORLD', 'VIEW', 'CURSOR']) –

  Align, The alignment of the new object (optional)

  - `WORLD`
    World – Align the new object to the world.
  - `VIEW`
    View – Align the new object to the view.
  - `CURSOR`
    3D Cursor – Use the 3D cursor orientation for the new object.
- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Location for the newly added object (array of 3 items, in [-inf, inf], optional)
- **rotation** ([`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler") | Sequence[float]) – Rotation, Rotation for the newly added object (array of 3 items, in [-inf, inf], optional)
- **scale** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Scale, Scale for the newly added object (array of 3 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.primitive_monkey_add"></a>

### bpy.ops.mesh.primitive_monkey_add(*, size=2.0, calc_uvs=True, enter_editmode=False, align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(0.0, 0.0, 0.0))

Construct a Suzanne mesh

**Parameters:**

- **size** (float) – Size, (in [0, inf], optional)
- **calc_uvs** (bool) – Generate UVs, Generate a default UV map (optional)
- **enter_editmode** (bool) – Enter Edit Mode, Enter edit mode when adding this object (optional)
- **align** (Literal['WORLD', 'VIEW', 'CURSOR']) –

  Align, The alignment of the new object (optional)

  - `WORLD`
    World – Align the new object to the world.
  - `VIEW`
    View – Align the new object to the view.
  - `CURSOR`
    3D Cursor – Use the 3D cursor orientation for the new object.
- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Location for the newly added object (array of 3 items, in [-inf, inf], optional)
- **rotation** ([`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler") | Sequence[float]) – Rotation, Rotation for the newly added object (array of 3 items, in [-inf, inf], optional)
- **scale** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Scale, Scale for the newly added object (array of 3 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.primitive_plane_add"></a>

### bpy.ops.mesh.primitive_plane_add(*, size=2.0, calc_uvs=True, enter_editmode=False, align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(0.0, 0.0, 0.0))

Construct a filled planar mesh with 4 vertices

**Parameters:**

- **size** (float) – Size, (in [0, inf], optional)
- **calc_uvs** (bool) – Generate UVs, Generate a default UV map (optional)
- **enter_editmode** (bool) – Enter Edit Mode, Enter edit mode when adding this object (optional)
- **align** (Literal['WORLD', 'VIEW', 'CURSOR']) –

  Align, The alignment of the new object (optional)

  - `WORLD`
    World – Align the new object to the world.
  - `VIEW`
    View – Align the new object to the view.
  - `CURSOR`
    3D Cursor – Use the 3D cursor orientation for the new object.
- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Location for the newly added object (array of 3 items, in [-inf, inf], optional)
- **rotation** ([`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler") | Sequence[float]) – Rotation, Rotation for the newly added object (array of 3 items, in [-inf, inf], optional)
- **scale** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Scale, Scale for the newly added object (array of 3 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.primitive_torus_add"></a>

### bpy.ops.mesh.primitive_torus_add(*, align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), major_segments=48, minor_segments=12, mode='MAJOR_MINOR', major_radius=1.0, minor_radius=0.25, abso_major_rad=1.25, abso_minor_rad=0.75, generate_uvs=True)

Construct a torus mesh

**Parameters:**

- **align** (Literal['WORLD', 'VIEW', 'CURSOR']) –

  Align, (optional)

  - `WORLD`
    World – Align the new object to the world.
  - `VIEW`
    View – Align the new object to the view.
  - `CURSOR`
    3D Cursor – Use the 3D cursor orientation for the new object.
- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, (array of 3 items, in [-inf, inf], optional)
- **rotation** ([`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler") | Sequence[float]) – Rotation, (array of 3 items, in [-inf, inf], optional)
- **major_segments** (int) – Major Segments, Number of segments for the main ring of the torus (in [3, 256], optional)
- **minor_segments** (int) – Minor Segments, Number of segments for the minor ring of the torus (in [3, 256], optional)
- **mode** (Literal['MAJOR_MINOR', 'EXT_INT']) –

  Dimensions Mode, (optional)

  - `MAJOR_MINOR`
    Major/Minor – Use the major/minor radii for torus dimensions.
  - `EXT_INT`
    Exterior/Interior – Use the exterior/interior radii for torus dimensions.
- **major_radius** (float) – Major Radius, Radius from the origin to the center of the cross sections (in [0, 10000], optional)
- **minor_radius** (float) – Minor Radius, Radius of the torus’s cross section (in [0, 10000], optional)
- **abso_major_rad** (float) – Exterior Radius, Total Exterior Radius of the torus (in [0, 10000], optional)
- **abso_minor_rad** (float) – Interior Radius, Total Interior Radius of the torus (in [0, 10000], optional)
- **generate_uvs** (bool) – Generate UVs, Generate a default UV map (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/add_mesh_torus.py:222](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/add_mesh_torus.py#L222)

<a id="bpy.ops.mesh.primitive_uv_sphere_add"></a>

### bpy.ops.mesh.primitive_uv_sphere_add(*, segments=32, ring_count=16, radius=1.0, calc_uvs=True, enter_editmode=False, align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(0.0, 0.0, 0.0))

Construct a spherical mesh with quad faces, except for triangle faces at the top and bottom

**Parameters:**

- **segments** (int) – Segments, (in [3, 100000], optional)
- **ring_count** (int) – Rings, (in [3, 100000], optional)
- **radius** (float) – Radius, (in [0, inf], optional)
- **calc_uvs** (bool) – Generate UVs, Generate a default UV map (optional)
- **enter_editmode** (bool) – Enter Edit Mode, Enter edit mode when adding this object (optional)
- **align** (Literal['WORLD', 'VIEW', 'CURSOR']) –

  Align, The alignment of the new object (optional)

  - `WORLD`
    World – Align the new object to the world.
  - `VIEW`
    View – Align the new object to the view.
  - `CURSOR`
    3D Cursor – Use the 3D cursor orientation for the new object.
- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Location for the newly added object (array of 3 items, in [-inf, inf], optional)
- **rotation** ([`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler") | Sequence[float]) – Rotation, Rotation for the newly added object (array of 3 items, in [-inf, inf], optional)
- **scale** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Scale, Scale for the newly added object (array of 3 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.quads_convert_to_tris"></a>

### bpy.ops.mesh.quads_convert_to_tris(*, quad_method='BEAUTY', ngon_method='BEAUTY')

Triangulate selected faces

**Parameters:**

- **quad_method** (Literal[[Modifier Triangulate Quad Method Items](bpy_types_enum_items/modifier_triangulate_quad_method_items.md#rna-enum-modifier-triangulate-quad-method-items)]) – Quad Method, Method for splitting the quads into triangles (optional)
- **ngon_method** (Literal[[Modifier Triangulate Ngon Method Items](bpy_types_enum_items/modifier_triangulate_ngon_method_items.md#rna-enum-modifier-triangulate-ngon-method-items)]) – N-gon Method, Method for splitting the n-gons into triangles (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.region_to_loop"></a>

### bpy.ops.mesh.region_to_loop()

Select boundary edges around the selected faces

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.remove_doubles"></a>

### bpy.ops.mesh.remove_doubles(*, threshold=0.0001, use_centroid=True, use_unselected=False, use_sharp_edge_from_normals=False)

Merge vertices based on their proximity

**Parameters:**

- **threshold** (float) – Merge Distance, Maximum distance between elements to merge (in [1e-06, 50], optional)
- **use_centroid** (bool) – Centroid Merge, Move vertices to the centroid of the duplicate cluster, otherwise the vertex closest to the centroid is used. (optional)
- **use_unselected** (bool) – Unselected, Merge selected to other unselected vertices (optional)
- **use_sharp_edge_from_normals** (bool) – Sharp Edges, Calculate sharp edges using custom normal data (when available) (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.reorder_vertices_spatial"></a>

### bpy.ops.mesh.reorder_vertices_spatial()

Reorder mesh faces and vertices based on their spatial position for better BVH building and sculpting performance.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.reveal"></a>

### bpy.ops.mesh.reveal(*, select=True)

Reveal all hidden vertices, edges and faces

**Parameters:**

**select** (bool) – Select, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.rip"></a>

### bpy.ops.mesh.rip(*, mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1.0, use_proportional_connected=False, use_proportional_projected=False, release_confirm=False, use_accurate=False, use_fill=False)

Disconnect vertices or edges from connected geometry

**Parameters:**

- **mirror** (bool) – Mirror Editing, (optional)
- **use_proportional_edit** (bool) – Proportional Editing, (optional)
- **proportional_edit_falloff** (Literal[[Proportional Falloff Items](bpy_types_enum_items/proportional_falloff_items.md#rna-enum-proportional-falloff-items)]) – Proportional Falloff, Falloff type for proportional editing mode (optional)
- **proportional_size** (float) – Proportional Size, (in [1e-06, inf], optional)
- **use_proportional_connected** (bool) – Connected, (optional)
- **use_proportional_projected** (bool) – Projected (2D), (optional)
- **release_confirm** (bool) – Confirm on Release, Always confirm operation when releasing button (optional)
- **use_accurate** (bool) – Accurate, Use accurate transformation (optional)
- **use_fill** (bool) – Fill, Fill the ripped region (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.rip_edge"></a>

### bpy.ops.mesh.rip_edge(*, location=(0.0, 0.0, 0.0), direction=(0.0, 0.0, 0.0))

Extend vertices along the edge closest to the cursor

**Parameters:**

- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, World-space ray origin for extending vertices (array of 3 items, in [-inf, inf], optional)
- **direction** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Direction, World-space direction vector for extending vertices (array of 3 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.rip_edge_move"></a>

### bpy.ops.mesh.rip_edge_move(*, MESH_OT_rip_edge={}, TRANSFORM_OT_translate={})

Extend vertices and move the result

**Parameters:**

- **MESH_OT_rip_edge** (dict[str, Any]) – Extend Vertices, Extend vertices along the edge closest to the cursor (optional, [`bpy.ops.mesh.rip_edge()`](#bpy.ops.mesh.rip_edge "bpy.ops.mesh.rip_edge") keyword arguments)
- **TRANSFORM_OT_translate** (dict[str, Any]) – Move, Move selected items (optional, [`bpy.ops.transform.translate()`](bpy.ops.transform.md#bpy.ops.transform.translate "bpy.ops.transform.translate") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.rip_move"></a>

### bpy.ops.mesh.rip_move(*, MESH_OT_rip={}, TRANSFORM_OT_translate={})

Rip polygons and move the result

**Parameters:**

- **MESH_OT_rip** (dict[str, Any]) – Rip, Disconnect vertices or edges from connected geometry (optional, [`bpy.ops.mesh.rip()`](#bpy.ops.mesh.rip "bpy.ops.mesh.rip") keyword arguments)
- **TRANSFORM_OT_translate** (dict[str, Any]) – Move, Move selected items (optional, [`bpy.ops.transform.translate()`](bpy.ops.transform.md#bpy.ops.transform.translate "bpy.ops.transform.translate") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.screw"></a>

### bpy.ops.mesh.screw(*, steps=9, turns=1, center=(0.0, 0.0, 0.0), axis=(0.0, 0.0, 0.0))

Extrude selected vertices in screw-shaped rotation around the cursor in indicated viewport

**Parameters:**

- **steps** (int) – Steps, Steps (in [1, 100000], optional)
- **turns** (int) – Turns, Turns (in [1, 100000], optional)
- **center** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Center, Center in global view space (array of 3 items, in [-inf, inf], optional)
- **axis** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Axis, Axis in global view space (array of 3 items, in [-1, 1], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.select_all"></a>

### bpy.ops.mesh.select_all(*, action='TOGGLE')

(De)select all vertices, edges or faces

**Parameters:**

**action** (Literal['TOGGLE', 'SELECT', 'DESELECT', 'INVERT']) –

Action, Selection action to execute (optional)

- `TOGGLE`
  Toggle – Toggle selection for all elements.
- `SELECT`
  Select – Select all elements.
- `DESELECT`
  Deselect – Deselect all elements.
- `INVERT`
  Invert – Invert selection of all elements.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.select_axis"></a>

### bpy.ops.mesh.select_axis(*, orientation='LOCAL', sign='POS', axis='X', threshold=0.0001)

Select all data in the mesh on a single axis

**Parameters:**

- **orientation** (Literal[[Transform Orientation Items](bpy_types_enum_items/transform_orientation_items.md#rna-enum-transform-orientation-items)]) – Axis Mode, Axis orientation (optional)
- **sign** (Literal['POS', 'NEG', 'ALIGN']) – Axis Sign, Side to select (optional)
- **axis** (Literal[[Axis Xyz Items](bpy_types_enum_items/axis_xyz_items.md#rna-enum-axis-xyz-items)]) – Axis, Select the axis to compare each vertex on (optional)
- **threshold** (float) – Threshold, (in [1e-06, 50], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.select_boundary_loop_multi"></a>

### bpy.ops.mesh.select_boundary_loop_multi(*, extend=True, delimit_edge_loop=set())

Select entire boundary loop of each selected boundary edge

**Parameters:**

- **extend** (bool) – Extend, Extend the selection (optional)
- **delimit_edge_loop** (set[Literal[[Mesh Walk Delimit Edge Loop Items](bpy_types_enum_items/mesh_walk_delimit_edge_loop_items.md#rna-enum-mesh-walk-delimit-edge-loop-items)]]) – Delimit, Delimit edge loop selection (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.select_by_attribute"></a>

### bpy.ops.mesh.select_by_attribute()

Select elements based on the active boolean attribute

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.select_by_pole_count"></a>

### bpy.ops.mesh.select_by_pole_count(*, pole_count=4, type='NOTEQUAL', extend=False, exclude_nonmanifold=True)

Select vertices at poles by the number of connected edges. In edge and face mode the geometry connected to the vertices is selected

**Parameters:**

- **pole_count** (int) – Pole Count, (in [0, inf], optional)
- **type** (Literal['LESS', 'EQUAL', 'GREATER', 'NOTEQUAL']) – Type, Type of comparison to make (optional)
- **extend** (bool) – Extend, Extend the selection (optional)
- **exclude_nonmanifold** (bool) – Exclude Non Manifold, Exclude non-manifold poles (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.select_edge_loop_multi"></a>

### bpy.ops.mesh.select_edge_loop_multi(*, delimit_edge_loop={'NGONS', 'OUTER_CORNERS'})

Select loops of connected edges from each selected edge

**Parameters:**

**delimit_edge_loop** (set[Literal[[Mesh Walk Delimit Edge Loop Items](bpy_types_enum_items/mesh_walk_delimit_edge_loop_items.md#rna-enum-mesh-walk-delimit-edge-loop-items)]]) – Delimit, Delimit edge loop selection (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.select_edge_ring_multi"></a>

### bpy.ops.mesh.select_edge_ring_multi(*, delimit_edge_ring={'NGONS'})

Select rings of connected edges from each selected edge

**Parameters:**

**delimit_edge_ring** (set[Literal[[Mesh Walk Delimit Edge Ring Items](bpy_types_enum_items/mesh_walk_delimit_edge_ring_items.md#rna-enum-mesh-walk-delimit-edge-ring-items)]]) – Edge Ring Delimit, Delimit edge ring selection (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.select_face_by_sides"></a>

### bpy.ops.mesh.select_face_by_sides(*, number=4, type='EQUAL', extend=True)

Select vertices or faces by the number of face sides

**Parameters:**

- **number** (int) – Number of Vertices, (in [3, inf], optional)
- **type** (Literal['LESS', 'EQUAL', 'GREATER', 'NOTEQUAL']) – Type, Type of comparison to make (optional)
- **extend** (bool) – Extend, Extend the selection (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.select_interior_faces"></a>

### bpy.ops.mesh.select_interior_faces()

Select faces where all edges have more than 2 face users

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.select_less"></a>

### bpy.ops.mesh.select_less(*, use_face_step=True)

Deselect vertices, edges or faces at the boundary of each selection region

**Parameters:**

**use_face_step** (bool) – Face Step, Connected faces (instead of edges) (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.select_linked"></a>

### bpy.ops.mesh.select_linked(*, delimit={'SEAM'})

Select all vertices connected to the current selection

**Parameters:**

**delimit** (set[Literal[[Mesh Delimit Mode Items](bpy_types_enum_items/mesh_delimit_mode_items.md#rna-enum-mesh-delimit-mode-items)]]) – Delimit, Delimit selected region (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.select_linked_pick"></a>

### bpy.ops.mesh.select_linked_pick(*, deselect=False, delimit={'SEAM'}, object_index=-1, index=-1)

(De)select all vertices linked to the edge under the mouse cursor

**Parameters:**

- **deselect** (bool) – Deselect, (optional)
- **delimit** (set[Literal[[Mesh Delimit Mode Items](bpy_types_enum_items/mesh_delimit_mode_items.md#rna-enum-mesh-delimit-mode-items)]]) – Delimit, Delimit selected region (optional)
- **object_index** (int) – (in [-1, inf], optional)
- **index** (int) – (in [-1, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.select_loose"></a>

### bpy.ops.mesh.select_loose(*, extend=False)

Select loose geometry based on the selection mode

**Parameters:**

**extend** (bool) – Extend, Extend the selection (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.select_mirror"></a>

### bpy.ops.mesh.select_mirror(*, axis={'X'}, extend=False)

Select mesh items at mirrored locations

**Parameters:**

- **axis** (set[Literal[[Axis Flag Xyz Items](bpy_types_enum_items/axis_flag_xyz_items.md#rna-enum-axis-flag-xyz-items)]]) – Axis, (optional)
- **extend** (bool) – Extend, Extend the existing selection (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.select_mode"></a>

### bpy.ops.mesh.select_mode(*, use_extend=False, use_expand=False, type='VERT', action='TOGGLE')

Change selection mode

**Parameters:**

- **use_extend** (bool) – Extend, (optional)
- **use_expand** (bool) – Expand, (optional)
- **type** (Literal[[Mesh Select Mode Items](bpy_types_enum_items/mesh_select_mode_items.md#rna-enum-mesh-select-mode-items)]) – Type, (optional)
- **action** (Literal['DISABLE', 'ENABLE', 'TOGGLE']) –

  Action, Selection action to execute (optional)

  - `DISABLE`
    Disable – Disable the selection mode.
  - `ENABLE`
    Enable – Enable the selection mode.
  - `TOGGLE`
    Toggle – Toggle the selection mode.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.select_more"></a>

### bpy.ops.mesh.select_more(*, use_face_step=True)

Select more vertices, edges or faces connected to initial selection

**Parameters:**

**use_face_step** (bool) – Face Step, Connected faces (instead of edges) (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.select_next_item"></a>

### bpy.ops.mesh.select_next_item()

Select the next element (using selection order)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/mesh.py:18](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/mesh.py#L18)

<a id="bpy.ops.mesh.select_non_manifold"></a>

### bpy.ops.mesh.select_non_manifold(*, extend=True, use_wire=True, use_boundary=True, use_multi_face=True, use_non_contiguous=True, use_verts=True)

Select all non-manifold vertices or edges

**Parameters:**

- **extend** (bool) – Extend, Extend the selection (optional)
- **use_wire** (bool) – Wire, Wire edges (optional)
- **use_boundary** (bool) – Boundaries, Boundary edges (optional)
- **use_multi_face** (bool) – Multiple Faces, Edges shared by more than two faces (optional)
- **use_non_contiguous** (bool) – Non Contiguous, Edges between faces pointing in alternate directions (optional)
- **use_verts** (bool) – Vertices, Vertices connecting multiple face regions (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.select_nth"></a>

### bpy.ops.mesh.select_nth(*, skip=1, nth=1, offset=0)

Deselect every Nth element starting from the active vertex, edge or face

**Parameters:**

- **skip** (int) – Deselected, Number of deselected elements in the repetitive sequence (in [1, inf], optional)
- **nth** (int) – Selected, Number of selected elements in the repetitive sequence (in [1, inf], optional)
- **offset** (int) – Offset, Offset from the starting point (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.select_prev_item"></a>

### bpy.ops.mesh.select_prev_item()

Select the previous element (using selection order)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/mesh.py:43](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/mesh.py#L43)

<a id="bpy.ops.mesh.select_random"></a>

### bpy.ops.mesh.select_random(*, ratio=0.5, seed=0, action='SELECT')

Randomly select vertices

**Parameters:**

- **ratio** (float) – Ratio, Portion of items to select randomly (in [0, 1], optional)
- **seed** (int) – Random Seed, Seed for the random number generator (in [0, inf], optional)
- **action** (Literal['SELECT', 'DESELECT']) –

  Action, Selection action to execute (optional)

  - `SELECT`
    Select – Select all elements.
  - `DESELECT`
    Deselect – Deselect all elements.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.select_similar"></a>

### bpy.ops.mesh.select_similar(*, type='VERT_NORMAL', compare='EQUAL', threshold=0.0)

Select similar vertices, edges or faces by property types

**Parameters:**

- **type** (Literal['VERT_NORMAL', 'VERT_FACES', 'VERT_GROUPS', 'VERT_EDGES', 'VERT_CREASE', 'EDGE_LENGTH', 'EDGE_DIR', 'EDGE_FACES', 'EDGE_FACE_ANGLE', 'EDGE_CREASE', 'EDGE_BEVEL', 'EDGE_SEAM', 'EDGE_SHARP', 'EDGE_FREESTYLE', 'FACE_MATERIAL', 'FACE_AREA', 'FACE_SIDES', 'FACE_PERIMETER', 'FACE_NORMAL', 'FACE_COPLANAR', 'FACE_SMOOTH', 'FACE_FREESTYLE']) – Type, (optional)
- **compare** (Literal['EQUAL', 'GREATER', 'LESS']) – Compare, (optional)
- **threshold** (float) – Threshold, (in [0, 100000], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.select_similar_region"></a>

### bpy.ops.mesh.select_similar_region()

Select similar face regions to the current selection

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.select_ungrouped"></a>

### bpy.ops.mesh.select_ungrouped(*, extend=False)

Select vertices without a group

**Parameters:**

**extend** (bool) – Extend, Extend the selection (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.separate"></a>

### bpy.ops.mesh.separate(*, type='SELECTED')

Separate selected geometry into a new mesh

**Parameters:**

**type** (Literal['SELECTED', 'MATERIAL', 'LOOSE']) – Type, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.set_normals_from_faces"></a>

### bpy.ops.mesh.set_normals_from_faces(*, keep_sharp=False)

Set the custom normals from the selected faces ones

**Parameters:**

**keep_sharp** (bool) – Keep Sharp Edges, Do not set sharp edges to face (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.set_sharpness_by_angle"></a>

### bpy.ops.mesh.set_sharpness_by_angle(*, angle=0.523599, extend=False)

Set edge sharpness based on the angle between neighboring faces

**Parameters:**

- **angle** (float) – Angle, (in [0.000174533, 3.14159], optional)
- **extend** (bool) – Extend, Add new sharp edges without clearing existing sharp edges (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.shape_propagate_to_all"></a>

### bpy.ops.mesh.shape_propagate_to_all()

Apply selected vertex locations to all other shape keys

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.shortest_path_pick"></a>

### bpy.ops.mesh.shortest_path_pick(*, edge_mode='SELECT', use_face_step=False, use_topology_distance=False, use_fill=False, skip=0, nth=1, offset=0, index=-1)

Select shortest path between two selections

**Parameters:**

- **edge_mode** (Literal['SELECT', 'SEAM', 'SHARP', 'CREASE', 'BEVEL', 'FREESTYLE']) – Edge Tag, The edge flag to tag when selecting the shortest path (optional)
- **use_face_step** (bool) – Face Stepping, Traverse connected faces (includes diagonals and edge-rings) (optional)
- **use_topology_distance** (bool) – Topology Distance, Find the minimum number of steps, ignoring spatial distance (optional)
- **use_fill** (bool) – Fill Region, Select all paths between the source/destination elements (optional)
- **skip** (int) – Deselected, Number of deselected elements in the repetitive sequence (in [0, inf], optional)
- **nth** (int) – Selected, Number of selected elements in the repetitive sequence (in [1, inf], optional)
- **offset** (int) – Offset, Offset from the starting point (in [-inf, inf], optional)
- **index** (int) – (in [-1, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.shortest_path_select"></a>

### bpy.ops.mesh.shortest_path_select(*, edge_mode='SELECT', use_face_step=False, use_topology_distance=False, use_fill=False, skip=0, nth=1, offset=0)

Select shortest path between two vertices/edges/faces

**Parameters:**

- **edge_mode** (Literal['SELECT', 'SEAM', 'SHARP', 'CREASE', 'BEVEL', 'FREESTYLE']) – Edge Tag, The edge flag to tag when selecting the shortest path (optional)
- **use_face_step** (bool) – Face Stepping, Traverse connected faces (includes diagonals and edge-rings) (optional)
- **use_topology_distance** (bool) – Topology Distance, Find the minimum number of steps, ignoring spatial distance (optional)
- **use_fill** (bool) – Fill Region, Select all paths between the source/destination elements (optional)
- **skip** (int) – Deselected, Number of deselected elements in the repetitive sequence (in [0, inf], optional)
- **nth** (int) – Selected, Number of selected elements in the repetitive sequence (in [1, inf], optional)
- **offset** (int) – Offset, Offset from the starting point (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.smooth_normals"></a>

### bpy.ops.mesh.smooth_normals(*, factor=0.5)

Smooth custom normals based on adjacent vertex normals

**Parameters:**

**factor** (float) – Factor, Specifies weight of smooth vs original normal (in [0, 1], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.solidify"></a>

### bpy.ops.mesh.solidify(*, thickness=0.01)

Create a solid skin by extruding, compensating for sharp angles

**Parameters:**

**thickness** (float) – Thickness, (in [-10000, 10000], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.sort_elements"></a>

### bpy.ops.mesh.sort_elements(*, type='VIEW_ZAXIS', elements={'VERT'}, reverse=False, seed=0)

The order of selected vertices/edges/faces is modified, based on a given method

**Parameters:**

- **type** (Literal['VIEW_ZAXIS', 'VIEW_XAXIS', 'CURSOR_DISTANCE', 'MATERIAL', 'SELECTED', 'RANDOMIZE', 'REVERSE']) –

  Type, Type of reordering operation to apply (optional)

  - `VIEW_ZAXIS`
    View Z Axis – Sort selected elements from farthest to nearest one in current view.
  - `VIEW_XAXIS`
    View X Axis – Sort selected elements from left to right one in current view.
  - `CURSOR_DISTANCE`
    Cursor Distance – Sort selected elements from nearest to farthest from 3D cursor.
  - `MATERIAL`
    Material – Sort selected faces from smallest to greatest material index.
  - `SELECTED`
    Selected – Move all selected elements in first places, preserving their relative order.
    Warning: This will affect unselected elements’ indices as well.
  - `RANDOMIZE`
    Randomize – Randomize order of selected elements.
  - `REVERSE`
    Reverse – Reverse current order of selected elements.
- **elements** (set[Literal['VERT', 'EDGE', 'FACE']]) – Elements, Which elements to affect (vertices, edges and/or faces) (optional)
- **reverse** (bool) – Reverse, Reverse the sorting effect (optional)
- **seed** (int) – Seed, Seed for random-based operations (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.space_edge_loops_evenly"></a>

### bpy.ops.mesh.space_edge_loops_evenly(*, factor=1.0, interpolation='CUBIC', lock=(False, False, False))

Space the vertices in a regular distribution on the loop

**Parameters:**

- **factor** (float) – Factor, Spacing effect factor (in [0, 1], optional)
- **interpolation** (Literal['CUBIC', 'LINEAR']) –

  Interpolation, Algorithm used for interpolation (optional)

  - `CUBIC`
    Cubic – Natural cubic spline, smooth results.
  - `LINEAR`
    Linear – Vertices are projected on existing edges.
- **lock** (Sequence[bool]) – Lock, Lock editing of the axis (array of 3 items, optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.spin"></a>

### bpy.ops.mesh.spin(*, steps=12, dupli=False, angle=1.5708, use_auto_merge=True, use_normal_flip=False, center=(0.0, 0.0, 0.0), axis=(0.0, 0.0, 0.0))

Extrude selected vertices in a circle around the cursor in indicated viewport

**Parameters:**

- **steps** (int) – Steps, Steps (in [0, 1000000], optional)
- **dupli** (bool) – Use Duplicates, (optional)
- **angle** (float) – Angle, Rotation for each step (in [-inf, inf], optional)
- **use_auto_merge** (bool) – Auto Merge, Merge first/last when the angle is a full revolution (optional)
- **use_normal_flip** (bool) – Flip Normals, (optional)
- **center** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Center, Center in global view space (array of 3 items, in [-inf, inf], optional)
- **axis** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Axis, Axis in global view space (array of 3 items, in [-1, 1], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.split"></a>

### bpy.ops.mesh.split()

Split off selected geometry from connected unselected geometry

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.split_normals"></a>

### bpy.ops.mesh.split_normals()

Split custom normals of selected vertices

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.subdivide"></a>

### bpy.ops.mesh.subdivide(*, number_cuts=1, smoothness=0.0, ngon=True, quadcorner='STRAIGHT_CUT', fractal=0.0, fractal_along_normal=0.0, seed=0)

Subdivide selected edges

**Parameters:**

- **number_cuts** (int) – Number of Cuts, (in [1, 100], optional)
- **smoothness** (float) – Smoothness, Smoothness factor (in [0, 1000], optional)
- **ngon** (bool) – Create N-Gons, When disabled, newly created faces are limited to 3 and 4 sided faces (optional)
- **quadcorner** (Literal['INNERVERT', 'PATH', 'STRAIGHT_CUT', 'FAN']) – Quad Corner Type, How to subdivide quad corners (anything other than Straight Cut will prevent n-gons) (optional)
- **fractal** (float) – Fractal, Fractal randomness factor (in [0, 1e+06], optional)
- **fractal_along_normal** (float) – Along Normal, Apply fractal displacement along normal only (in [0, 1], optional)
- **seed** (int) – Random Seed, Seed for the random number generator (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.subdivide_edgering"></a>

### bpy.ops.mesh.subdivide_edgering(*, number_cuts=10, interpolation='PATH', smoothness=1.0, profile_shape_factor=0.0, profile_shape='SMOOTH')

Subdivide perpendicular edges to the selected edge-ring

**Parameters:**

- **number_cuts** (int) – Number of Cuts, (in [0, 1000], optional)
- **interpolation** (Literal['LINEAR', 'PATH', 'SURFACE']) – Interpolation, Interpolation method (optional)
- **smoothness** (float) – Smoothness, Smoothness factor (in [0, 1000], optional)
- **profile_shape_factor** (float) – Profile Factor, How much intermediary new edges are shrunk/expanded (in [-1000, 1000], optional)
- **profile_shape** (Literal[[Proportional Falloff Curve Only Items](bpy_types_enum_items/proportional_falloff_curve_only_items.md#rna-enum-proportional-falloff-curve-only-items)]) – Profile Shape, Shape of the profile (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.symmetrize"></a>

### bpy.ops.mesh.symmetrize(*, direction='NEGATIVE_X', threshold=0.0001)

Enforce symmetry (both form and topological) across an axis

**Parameters:**

- **direction** (Literal[[Symmetrize Direction Items](bpy_types_enum_items/symmetrize_direction_items.md#rna-enum-symmetrize-direction-items)]) – Direction, Which sides to copy from and to (optional)
- **threshold** (float) – Threshold, Limit for snap middle vertices to the axis center (in [0, 10], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.symmetry_snap"></a>

### bpy.ops.mesh.symmetry_snap(*, direction='NEGATIVE_X', threshold=0.05, factor=0.5, use_center=True, use_topology=False)

Snap vertex pairs to their mirrored locations

**Parameters:**

- **direction** (Literal[[Symmetrize Direction Items](bpy_types_enum_items/symmetrize_direction_items.md#rna-enum-symmetrize-direction-items)]) – Direction, Which sides to copy from and to (optional)
- **threshold** (float) – Threshold, Distance within which matching vertices are searched (in [0, 10], optional)
- **factor** (float) – Factor, Mix factor of the locations of the vertices (in [0, 1], optional)
- **use_center** (bool) – Center, Snap middle vertices to the axis center (optional)
- **use_topology** (bool) – Topology Mirror, Use topology to find mirrored vertices instead of spatial proximity (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.tris_convert_to_quads"></a>

### bpy.ops.mesh.tris_convert_to_quads(*, face_threshold=0.698132, shape_threshold=0.698132, topology_influence=0.0, uvs=False, vcols=False, seam=False, sharp=False, materials=False, deselect_joined=False)

Merge triangles into four sided polygons where possible

**Parameters:**

- **face_threshold** (float) – Max Face Angle, Face angle limit (in [0, 3.14159], optional)
- **shape_threshold** (float) – Max Shape Angle, Shape angle limit (in [0, 3.14159], optional)
- **topology_influence** (float) – Topology Influence, How much to prioritize regular grids of quads as well as quads that touch existing quads (in [0, 2], optional)
- **uvs** (bool) – Compare UVs, (optional)
- **vcols** (bool) – Compare Color Attributes, (optional)
- **seam** (bool) – Compare Seam, (optional)
- **sharp** (bool) – Compare Sharp, (optional)
- **materials** (bool) – Compare Materials, (optional)
- **deselect_joined** (bool) – Deselect Joined, Only select remaining triangles that were not merged (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.unsubdivide"></a>

### bpy.ops.mesh.unsubdivide(*, iterations=2)

Un-subdivide selected edges and faces

**Parameters:**

**iterations** (int) – Iterations, Number of times to un-subdivide (in [1, 1000], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.uv_texture_add"></a>

### bpy.ops.mesh.uv_texture_add()

Add UV map

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.uv_texture_remove"></a>

### bpy.ops.mesh.uv_texture_remove()

Remove UV map

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.uvs_reverse"></a>

### bpy.ops.mesh.uvs_reverse()

Flip direction of UV coordinates inside faces

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.uvs_rotate"></a>

### bpy.ops.mesh.uvs_rotate(*, use_ccw=False)

Rotate UV coordinates inside faces

**Parameters:**

**use_ccw** (bool) – Counter Clockwise, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.vert_connect"></a>

### bpy.ops.mesh.vert_connect()

Connect selected vertices of faces, splitting the face

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.vert_connect_concave"></a>

### bpy.ops.mesh.vert_connect_concave()

Split concave faces by connecting vertices to make them convex

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.vert_connect_nonplanar"></a>

### bpy.ops.mesh.vert_connect_nonplanar(*, angle_limit=0.0872665)

Split non-planar faces that exceed the angle threshold

**Parameters:**

**angle_limit** (float) – Max Angle, Angle limit (in [0, 3.14159], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.vert_connect_path"></a>

### bpy.ops.mesh.vert_connect_path()

Connect vertices by their selection order, creating edges, splitting faces

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.vertices_smooth"></a>

### bpy.ops.mesh.vertices_smooth(*, factor=0.0, repeat=1, xaxis=True, yaxis=True, zaxis=True, wait_for_input=True)

Flatten angles of selected vertices

**Parameters:**

- **factor** (float) – Smoothing, Smoothing factor (in [-10, 10], optional)
- **repeat** (int) – Repeat, Number of times to smooth the mesh (in [1, 1000], optional)
- **xaxis** (bool) – X-Axis, Smooth along the X axis (optional)
- **yaxis** (bool) – Y-Axis, Smooth along the Y axis (optional)
- **zaxis** (bool) – Z-Axis, Smooth along the Z axis (optional)
- **wait_for_input** (bool) – Wait for Input, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.vertices_smooth_laplacian"></a>

### bpy.ops.mesh.vertices_smooth_laplacian(*, repeat=1, lambda_factor=1.0, lambda_border=5e-05, use_x=True, use_y=True, use_z=True, preserve_volume=True)

Laplacian smooth of selected vertices

**Parameters:**

- **repeat** (int) – Number of iterations to smooth the mesh, (in [1, 1000], optional)
- **lambda_factor** (float) – Lambda factor, (in [1e-07, 1000], optional)
- **lambda_border** (float) – Lambda factor in border, (in [1e-07, 1000], optional)
- **use_x** (bool) – Smooth X Axis, Smooth object along X axis (optional)
- **use_y** (bool) – Smooth Y Axis, Smooth object along Y axis (optional)
- **use_z** (bool) – Smooth Z Axis, Smooth object along Z axis (optional)
- **preserve_volume** (bool) – Preserve Volume, Apply volume preservation after smooth (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mesh.wireframe"></a>

### bpy.ops.mesh.wireframe(*, use_boundary=True, use_even_offset=True, use_relative_offset=False, use_replace=True, thickness=0.01, offset=0.01, use_crease=False, crease_weight=0.01)

Create a solid wireframe from faces

**Parameters:**

- **use_boundary** (bool) – Boundary, Inset face boundaries (optional)
- **use_even_offset** (bool) – Offset Even, Scale the offset to give more even thickness (optional)
- **use_relative_offset** (bool) – Offset Relative, Scale the offset by surrounding geometry (optional)
- **use_replace** (bool) – Replace, Remove original faces (optional)
- **thickness** (float) – Thickness, (in [0, 10000], optional)
- **offset** (float) – Offset, (in [0, 10000], optional)
- **use_crease** (bool) – Crease, Crease hub edges for an improved subdivision surface (optional)
- **crease_weight** (float) – Crease Weight, (in [0, 1000], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]
