<!-- source: Blender Python API reference 5.2 / bpy.types.Mesh.html -->

<a id="mesh-id"></a>

# Mesh(ID)

<a id="mesh-data"></a>

## Mesh Data

The mesh data is accessed in object mode and intended for compact storage,
for more flexible mesh editing from Python see [`bmesh`](bmesh.md#module-bmesh "bmesh").

Blender stores 4 main arrays to define mesh geometry.

- [`Mesh.vertices`](#bpy.types.Mesh.vertices "bpy.types.Mesh.vertices") (3 points in space)
- [`Mesh.edges`](#bpy.types.Mesh.edges "bpy.types.Mesh.edges") (reference 2 vertices)
- [`Mesh.loops`](#bpy.types.Mesh.loops "bpy.types.Mesh.loops") (reference a single vertex and edge)
- [`Mesh.polygons`](#bpy.types.Mesh.polygons "bpy.types.Mesh.polygons"): (reference a range of loops)

Each polygon references a slice in the loop array, this way,
polygons do not store vertices or corner data such as UVs directly,
only a reference to loops that the polygon uses.

[`Mesh.loops`](#bpy.types.Mesh.loops "bpy.types.Mesh.loops"), [`Mesh.uv_layers`](#bpy.types.Mesh.uv_layers "bpy.types.Mesh.uv_layers") [`Mesh.vertex_colors`](#bpy.types.Mesh.vertex_colors "bpy.types.Mesh.vertex_colors") are all aligned so the same polygon loop
indices can be used to find the UVs and vertex colors as with as the vertices.

To compare mesh API options see: [NGons and Tessellation Faces](info_gotchas_meshes.md#info-gotcha-mesh-faces)

This example script prints the vertices and UVs for each polygon, assumes the active object is a mesh with UVs.

```python
import bpy

me = bpy.context.object.data
uv_layer = me.uv_layers.active.data

for poly in me.polygons:
    print("Polygon index: {:d}, length: {:d}".format(poly.index, poly.loop_total))

    # Range is used here to show how the polygons reference loops,
    # for convenience 'poly.loop_indices' can be used instead.
    for loop_index in range(poly.loop_start, poly.loop_start + poly.loop_total):
        print("    Vertex: {:d}".format(me.loops[loop_index].vertex_index))
        print("    UV: {!r}".format(uv_layer[loop_index].uv))
```

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")

<a id="bpy.types.Mesh"></a>

### class bpy.types.Mesh(ID)

Mesh data-block defining geometric surfaces

<a id="bpy.types.Mesh.animation_data"></a>

#### bpy.types.Mesh.animation_data

Animation data for this data-block (readonly)

**Type:**

[`AnimData`](bpy.types.AnimData.md#bpy.types.AnimData "bpy.types.AnimData") | None

<a id="bpy.types.Mesh.attributes"></a>

#### bpy.types.Mesh.attributes

Geometry attributes (default None, readonly)

**Type:**

[`AttributeGroupMesh`](bpy.types.AttributeGroupMesh.md#bpy.types.AttributeGroupMesh "bpy.types.AttributeGroupMesh")[[`Attribute`](bpy.types.Attribute.md#bpy.types.Attribute "bpy.types.Attribute")]

<a id="bpy.types.Mesh.auto_texspace"></a>

#### bpy.types.Mesh.auto_texspace

Adjust active object’s texture space automatically when transforming object (default True)

**Type:**

bool

<a id="bpy.types.Mesh.color_attributes"></a>

#### bpy.types.Mesh.color_attributes

Geometry color attributes (default None, readonly)

**Type:**

[`AttributeGroupMesh`](bpy.types.AttributeGroupMesh.md#bpy.types.AttributeGroupMesh "bpy.types.AttributeGroupMesh")[[`Attribute`](bpy.types.Attribute.md#bpy.types.Attribute "bpy.types.Attribute")]

<a id="bpy.types.Mesh.corner_normals"></a>

#### bpy.types.Mesh.corner_normals

The “slit” normal direction of each face corner, influenced by vertex normals, sharp faces, sharp edges, and custom normals. May be empty. (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`MeshNormalValue`](bpy.types.MeshNormalValue.md#bpy.types.MeshNormalValue "bpy.types.MeshNormalValue")]

<a id="bpy.types.Mesh.cycles"></a>

#### bpy.types.Mesh.cycles

Cycles mesh settings (readonly)

**Type:**

`CyclesMeshSettings` | None

<a id="bpy.types.Mesh.edges"></a>

#### bpy.types.Mesh.edges

Edges of the mesh (default None, readonly)

**Type:**

[`MeshEdges`](bpy.types.MeshEdges.md#bpy.types.MeshEdges "bpy.types.MeshEdges")[[`MeshEdge`](bpy.types.MeshEdge.md#bpy.types.MeshEdge "bpy.types.MeshEdge")]

<a id="bpy.types.Mesh.has_custom_normals"></a>

#### bpy.types.Mesh.has_custom_normals

True if there is custom normal data for this mesh (default False, readonly)

**Type:**

bool

<a id="bpy.types.Mesh.is_editmode"></a>

#### bpy.types.Mesh.is_editmode

True when used in editmode (default False, readonly)

**Type:**

bool

<a id="bpy.types.Mesh.loop_triangle_polygons"></a>

#### bpy.types.Mesh.loop_triangle_polygons

The face index for each loop triangle (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`ReadOnlyInteger`](bpy.types.ReadOnlyInteger.md#bpy.types.ReadOnlyInteger "bpy.types.ReadOnlyInteger")]

<a id="bpy.types.Mesh.loop_triangles"></a>

#### bpy.types.Mesh.loop_triangles

Tessellation of mesh polygons into triangles (default None, readonly)

**Type:**

[`MeshLoopTriangles`](bpy.types.MeshLoopTriangles.md#bpy.types.MeshLoopTriangles "bpy.types.MeshLoopTriangles")[[`MeshLoopTriangle`](bpy.types.MeshLoopTriangle.md#bpy.types.MeshLoopTriangle "bpy.types.MeshLoopTriangle")]

<a id="bpy.types.Mesh.loops"></a>

#### bpy.types.Mesh.loops

Loops of the mesh (face corners) (default None, readonly)

**Type:**

[`MeshLoops`](bpy.types.MeshLoops.md#bpy.types.MeshLoops "bpy.types.MeshLoops")[[`MeshLoop`](bpy.types.MeshLoop.md#bpy.types.MeshLoop "bpy.types.MeshLoop")]

<a id="bpy.types.Mesh.materials"></a>

#### bpy.types.Mesh.materials

(default None, readonly)

**Type:**

[`IDMaterials`](bpy.types.IDMaterials.md#bpy.types.IDMaterials "bpy.types.IDMaterials")[[`Material`](bpy.types.Material.md#bpy.types.Material "bpy.types.Material")]

<a id="bpy.types.Mesh.normals_domain"></a>

#### bpy.types.Mesh.normals_domain

The attribute domain that gives enough information to represent the mesh’s normals (default `'FACE'`, readonly)

**Type:**

Literal[‘POINT’, ‘FACE’, ‘CORNER’]

<a id="bpy.types.Mesh.polygon_normals"></a>

#### bpy.types.Mesh.polygon_normals

The normal direction of each face, defined by the winding order and position of its vertices (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`MeshNormalValue`](bpy.types.MeshNormalValue.md#bpy.types.MeshNormalValue "bpy.types.MeshNormalValue")]

<a id="bpy.types.Mesh.polygons"></a>

#### bpy.types.Mesh.polygons

Polygons of the mesh (default None, readonly)

**Type:**

[`MeshPolygons`](bpy.types.MeshPolygons.md#bpy.types.MeshPolygons "bpy.types.MeshPolygons")[[`MeshPolygon`](bpy.types.MeshPolygon.md#bpy.types.MeshPolygon "bpy.types.MeshPolygon")]

<a id="bpy.types.Mesh.radial_symmetry"></a>

#### bpy.types.Mesh.radial_symmetry

Number of mirrored regions around a central axis (array of 3 items, in [1, 64], default (1, 1, 1))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[int]

<a id="bpy.types.Mesh.remesh_mode"></a>

#### bpy.types.Mesh.remesh_mode

(default `'VOXEL'`)

- `VOXEL`
  Voxel – Use the voxel remesher.
- `QUAD`
  Quad – Use the quad remesher.

**Type:**

Literal[‘VOXEL’, ‘QUAD’]

<a id="bpy.types.Mesh.remesh_voxel_adaptivity"></a>

#### bpy.types.Mesh.remesh_voxel_adaptivity

Reduces the final face count by simplifying geometry where detail is not needed, generating triangles. A value greater than 0 disables Fix Poles. (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.Mesh.remesh_voxel_size"></a>

#### bpy.types.Mesh.remesh_voxel_size

Size of the voxel in object space used for volume evaluation. Lower values preserve finer details. (in [0, inf], default 0.1)

**Type:**

float

<a id="bpy.types.Mesh.shape_keys"></a>

#### bpy.types.Mesh.shape_keys

(readonly)

**Type:**

[`Key`](bpy.types.Key.md#bpy.types.Key "bpy.types.Key") | None

<a id="bpy.types.Mesh.skin_vertices"></a>

#### bpy.types.Mesh.skin_vertices

All skin vertices (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`MeshSkinVertexLayer`](bpy.types.MeshSkinVertexLayer.md#bpy.types.MeshSkinVertexLayer "bpy.types.MeshSkinVertexLayer")]

<a id="bpy.types.Mesh.texco_mesh"></a>

#### bpy.types.Mesh.texco_mesh

Derive texture coordinates from another mesh

**Type:**

[`Mesh`](#bpy.types.Mesh "bpy.types.Mesh") | None

<a id="bpy.types.Mesh.texspace_location"></a>

#### bpy.types.Mesh.texspace_location

Texture space location (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.Mesh.texspace_size"></a>

#### bpy.types.Mesh.texspace_size

Texture space size (array of 3 items, in [-inf, inf], default (1.0, 1.0, 1.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.Mesh.texture_mesh"></a>

#### bpy.types.Mesh.texture_mesh

Use another mesh for texture indices (vertex indices must be aligned)

**Type:**

[`Mesh`](#bpy.types.Mesh "bpy.types.Mesh") | None

<a id="bpy.types.Mesh.total_edge_sel"></a>

#### bpy.types.Mesh.total_edge_sel

Selected edge count in editmode (in [0, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.Mesh.total_face_sel"></a>

#### bpy.types.Mesh.total_face_sel

Selected face count in editmode (in [0, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.Mesh.total_vert_sel"></a>

#### bpy.types.Mesh.total_vert_sel

Selected vertex count in editmode (in [0, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.Mesh.use_auto_texspace"></a>

#### bpy.types.Mesh.use_auto_texspace

Adjust active object’s texture space automatically when transforming object (default True)

**Type:**

bool

<a id="bpy.types.Mesh.use_mirror_topology"></a>

#### bpy.types.Mesh.use_mirror_topology

Use topology based mirroring (for when both sides of mesh have matching, unique topology) (default False)

**Type:**

bool

<a id="bpy.types.Mesh.use_mirror_vertex_groups"></a>

#### bpy.types.Mesh.use_mirror_vertex_groups

Mirror the left/right vertex groups when painting. The symmetry axis is determined by the symmetry settings. (default True)

**Type:**

bool

<a id="bpy.types.Mesh.use_mirror_x"></a>

#### bpy.types.Mesh.use_mirror_x

Enable symmetry in the X axis (default False)

**Type:**

bool

<a id="bpy.types.Mesh.use_mirror_y"></a>

#### bpy.types.Mesh.use_mirror_y

Enable symmetry in the Y axis (default False)

**Type:**

bool

<a id="bpy.types.Mesh.use_mirror_z"></a>

#### bpy.types.Mesh.use_mirror_z

Enable symmetry in the Z axis (default False)

**Type:**

bool

<a id="bpy.types.Mesh.use_paint_bone_selection"></a>

#### bpy.types.Mesh.use_paint_bone_selection

Bone selection during painting (default True)

**Type:**

bool

<a id="bpy.types.Mesh.use_paint_mask"></a>

#### bpy.types.Mesh.use_paint_mask

Face selection masking for painting (default False)

**Type:**

bool

<a id="bpy.types.Mesh.use_paint_mask_vertex"></a>

#### bpy.types.Mesh.use_paint_mask_vertex

Vertex selection masking for painting (default False)

**Type:**

bool

<a id="bpy.types.Mesh.use_remesh_fix_poles"></a>

#### bpy.types.Mesh.use_remesh_fix_poles

Produces fewer poles and a better topology flow (default False)

**Type:**

bool

<a id="bpy.types.Mesh.use_remesh_preserve_attributes"></a>

#### bpy.types.Mesh.use_remesh_preserve_attributes

Transfer all attributes to the new mesh (default False)

**Type:**

bool

<a id="bpy.types.Mesh.use_remesh_preserve_volume"></a>

#### bpy.types.Mesh.use_remesh_preserve_volume

Projects the mesh to preserve the volume and details of the original mesh (default False)

**Type:**

bool

<a id="bpy.types.Mesh.uv_layer_clone"></a>

#### bpy.types.Mesh.uv_layer_clone

UV loop layer to be used as cloning source

**Type:**

[`MeshUVLoopLayer`](bpy.types.MeshUVLoopLayer.md#bpy.types.MeshUVLoopLayer "bpy.types.MeshUVLoopLayer") | None

<a id="bpy.types.Mesh.uv_layer_clone_index"></a>

#### bpy.types.Mesh.uv_layer_clone_index

Clone UV loop layer index (in [0, inf], default 0)

**Type:**

int

<a id="bpy.types.Mesh.uv_layer_stencil"></a>

#### bpy.types.Mesh.uv_layer_stencil

UV loop layer to mask the painted area

**Type:**

[`MeshUVLoopLayer`](bpy.types.MeshUVLoopLayer.md#bpy.types.MeshUVLoopLayer "bpy.types.MeshUVLoopLayer") | None

<a id="bpy.types.Mesh.uv_layer_stencil_index"></a>

#### bpy.types.Mesh.uv_layer_stencil_index

Mask UV loop layer index (in [0, inf], default 0)

**Type:**

int

<a id="bpy.types.Mesh.uv_layers"></a>

#### bpy.types.Mesh.uv_layers

All UV loop layers (default None, readonly)

**Type:**

[`UVLoopLayers`](bpy.types.UVLoopLayers.md#bpy.types.UVLoopLayers "bpy.types.UVLoopLayers")[[`MeshUVLoopLayer`](bpy.types.MeshUVLoopLayer.md#bpy.types.MeshUVLoopLayer "bpy.types.MeshUVLoopLayer")]

<a id="bpy.types.Mesh.vertex_colors"></a>

#### bpy.types.Mesh.vertex_colors

Legacy vertex color layers. Deprecated, use color attributes instead. (default None, readonly)

**Type:**

[`LoopColors`](bpy.types.LoopColors.md#bpy.types.LoopColors "bpy.types.LoopColors")[[`MeshLoopColorLayer`](bpy.types.MeshLoopColorLayer.md#bpy.types.MeshLoopColorLayer "bpy.types.MeshLoopColorLayer")]

<a id="bpy.types.Mesh.vertex_normals"></a>

#### bpy.types.Mesh.vertex_normals

The normal direction of each vertex, defined as the average of the surrounding face normals (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`MeshNormalValue`](bpy.types.MeshNormalValue.md#bpy.types.MeshNormalValue "bpy.types.MeshNormalValue")]

<a id="bpy.types.Mesh.vertices"></a>

#### bpy.types.Mesh.vertices

Vertices of the mesh (default None, readonly)

**Type:**

[`MeshVertices`](bpy.types.MeshVertices.md#bpy.types.MeshVertices "bpy.types.MeshVertices")[[`MeshVertex`](bpy.types.MeshVertex.md#bpy.types.MeshVertex "bpy.types.MeshVertex")]

<a id="bpy.types.Mesh.edge_creases"></a>

#### bpy.types.Mesh.edge_creases

Edge crease values for subdivision surface, corresponding to the “crease_edge” attribute.

(readonly)

<a id="bpy.types.Mesh.edge_keys"></a>

#### bpy.types.Mesh.edge_keys

(readonly)

<a id="bpy.types.Mesh.vertex_creases"></a>

#### bpy.types.Mesh.vertex_creases

Vertex crease values for subdivision surface, corresponding to the “crease_vert” attribute.

(readonly)

<a id="bpy.types.Mesh.vertex_paint_mask"></a>

#### bpy.types.Mesh.vertex_paint_mask

Mask values for sculpting and painting, corresponding to the “.sculpt_mask” attribute.

(readonly)

<a id="bpy.types.Mesh.transform"></a>

#### bpy.types.Mesh.transform(matrix, *, shape_keys=False)

Transform mesh vertices by a matrix (Warning: inverts normals if matrix is negative)

**Parameters:**

- **matrix** ([`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix") | Sequence[Sequence[float]]) – Matrix (multi-dimensional array of 4 * 4 items, in [-inf, inf])
- **shape_keys** (bool) – Transform Shape Keys (optional)

<a id="bpy.types.Mesh.flip_normals"></a>

#### bpy.types.Mesh.flip_normals()

Invert winding of all polygons (clears tessellation, does not handle custom normals)

<a id="bpy.types.Mesh.set_sharp_from_angle"></a>

#### bpy.types.Mesh.set_sharp_from_angle(*, angle=3.14159)

Reset and fill the “sharp_edge” attribute based on the angle of faces neighboring manifold edges

**Parameters:**

**angle** (float) – Angle, Angle between faces beyond which edges are marked sharp (in [0, 3.14159], optional)

<a id="bpy.types.Mesh.split_faces"></a>

#### bpy.types.Mesh.split_faces()

Split faces based on the edge angle

<a id="bpy.types.Mesh.calc_tangents"></a>

#### bpy.types.Mesh.calc_tangents(*, uvmap='')

Compute tangents and bitangent signs, to be used together with the custom normals to get a complete tangent space for normal mapping (custom normals are also computed if not yet present)

**Parameters:**

**uvmap** (str) – Name of the UV map to use for tangent space computation (optional, never None)

<a id="bpy.types.Mesh.free_tangents"></a>

#### bpy.types.Mesh.free_tangents()

Free tangents

<a id="bpy.types.Mesh.calc_loop_triangles"></a>

#### bpy.types.Mesh.calc_loop_triangles()

Calculate loop triangle tessellation (supports editmode too)

<a id="bpy.types.Mesh.calc_smooth_groups"></a>

#### bpy.types.Mesh.calc_smooth_groups(*, use_bitflags=False, use_boundary_vertices_for_bitflags=False)

Calculate smooth groups from sharp edges

**Parameters:**

- **use_bitflags** (bool) – Produce bitflags groups instead of simple numeric values (optional)
- **use_boundary_vertices_for_bitflags** (bool) – Also consider different smoothgroups sharing only vertices (but without any common edge) as neighbors, preventing them from sharing the same bitflag value. Only effective when `use_bitflags` is set. WARNING: Will overflow (run out of available bits) easily with some types of topology, e.g. large fans of sharp edges (optional)

**Returns:**

`poly_groups`, Smooth Groups, [`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[int]

`groups`, Total number of groups, int

**Return type:**

tuple[[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[int], int]

<a id="bpy.types.Mesh.normals_split_custom_set"></a>

#### bpy.types.Mesh.normals_split_custom_set(normals)

Define custom normals of this mesh (use zero-vectors to keep auto ones)

**Parameters:**

**normals** (Sequence[Sequence[float]]) – Normals (multi-dimensional array of 1 * 3 items, in [-1, 1])

<a id="bpy.types.Mesh.normals_split_custom_set_from_vertices"></a>

#### bpy.types.Mesh.normals_split_custom_set_from_vertices(normals)

Define custom normals of this mesh, from vertices’ normals (use zero-vectors to keep auto ones)

**Parameters:**

**normals** (Sequence[Sequence[float]]) – Normals (multi-dimensional array of 1 * 3 items, in [-1, 1])

<a id="bpy.types.Mesh.update"></a>

#### bpy.types.Mesh.update(*, calc_edges=False, calc_edges_loose=False)

update

**Parameters:**

- **calc_edges** (bool) – Calculate Edges, Force recalculation of edges (optional)
- **calc_edges_loose** (bool) – Calculate Loose Edges, Calculate the loose state of each edge (optional)

<a id="bpy.types.Mesh.update_gpu_tag"></a>

#### bpy.types.Mesh.update_gpu_tag()

update_gpu_tag

<a id="bpy.types.Mesh.unit_test_compare"></a>

#### bpy.types.Mesh.unit_test_compare(*, mesh=None, threshold=7.1526e-06)

unit_test_compare

**Parameters:**

- **mesh** ([`Mesh`](#bpy.types.Mesh "bpy.types.Mesh") | None) – Mesh to compare to (optional)
- **threshold** (float) – Threshold, Comparison tolerance threshold (in [0, inf], optional)

**Returns:**

Return value, String description of result of comparison (never None)

**Return type:**

str

<a id="bpy.types.Mesh.clear_geometry"></a>

#### bpy.types.Mesh.clear_geometry()

Remove all geometry from the mesh. Note that this does not free shape keys or materials.

<a id="bpy.types.Mesh.validate"></a>

#### bpy.types.Mesh.validate(*, verbose=False, clean_customdata=True)

Validate geometry, return True when the mesh has had invalid geometry corrected/removed

**Parameters:**

- **verbose** (bool) – Verbose, Output information about the errors found (optional)
- **clean_customdata** (bool) – Clean Custom Data, Deprecated, has no effect (optional)

**Returns:**

Result

**Return type:**

bool

<a id="bpy.types.Mesh.validate_material_indices"></a>

#### bpy.types.Mesh.validate_material_indices()

Validate material indices of polygons, return True when the mesh has had invalid indices corrected (to default 0)

**Returns:**

Result

**Return type:**

bool

<a id="bpy.types.Mesh.count_selected_items"></a>

#### bpy.types.Mesh.count_selected_items()

Return the number of selected items (vert, edge, face)

**Returns:**

Result, (array of 3 items, in [0, inf])

**Return type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[int]

<a id="bpy.types.Mesh.edge_creases_ensure"></a>

#### bpy.types.Mesh.edge_creases_ensure()

Ensure the “crease_edge” attribute exists, creating it if needed.

**Returns:**

The edge crease attribute.

**Return type:**

[`FloatAttribute`](bpy.types.FloatAttribute.md#bpy.types.FloatAttribute "bpy.types.FloatAttribute")

<a id="bpy.types.Mesh.edge_creases_remove"></a>

#### bpy.types.Mesh.edge_creases_remove()

<a id="bpy.types.Mesh.from_pydata"></a>

#### bpy.types.Mesh.from_pydata(vertices, edges, faces, shade_flat=True)

Make a mesh from a list of vertices/edges/faces
Until we have a nicer way to make geometry, use this.

**Parameters:**

- **vertices** (Iterable[Sequence[float]]) – float triplets each representing (X, Y, Z)
  eg: [(0.0, 1.0, 0.5), …].
- **edges** (Iterable[Sequence[int]]) –

  int pairs, each pair contains two indices to the
  vertices argument. eg: [(1, 2), …]

  When an empty iterable is passed in, the edges are inferred from the polygons.
- **faces** (Iterable[Sequence[int]]) – iterator of faces, each faces contains three or more indices to
  the vertices argument. eg: [(5, 6, 8, 9), (1, 2, 3), …]
- **shade_flat** (bool) – When true, mark new faces as flat-shaded.

> **Warning:**
>
> Invalid mesh data
> *(out of range indices, edges with matching indices,
> 2 sided faces… etc)* are **not** prevented.
> If the data used for mesh creation isn’t known to be valid,
> run [`Mesh.validate`](#bpy.types.Mesh.validate "bpy.types.Mesh.validate") after this function.

<a id="bpy.types.Mesh.shade_flat"></a>

#### bpy.types.Mesh.shade_flat()

Render and display faces uniform, using face normals,
setting the “sharp_face” attribute true for every face

<a id="bpy.types.Mesh.shade_smooth"></a>

#### bpy.types.Mesh.shade_smooth()

Render and display faces smooth, using interpolated vertex normals,
removing the “sharp_face” attribute

<a id="bpy.types.Mesh.vertex_creases_ensure"></a>

#### bpy.types.Mesh.vertex_creases_ensure()

Ensure the “crease_vert” attribute exists, creating it if needed.

**Returns:**

The vertex crease attribute.

**Return type:**

[`FloatAttribute`](bpy.types.FloatAttribute.md#bpy.types.FloatAttribute "bpy.types.FloatAttribute")

<a id="bpy.types.Mesh.vertex_creases_remove"></a>

#### bpy.types.Mesh.vertex_creases_remove()

<a id="bpy.types.Mesh.vertex_paint_mask_ensure"></a>

#### bpy.types.Mesh.vertex_paint_mask_ensure()

Ensure the “.sculpt_mask” attribute exists, creating it if needed.

**Returns:**

The vertex paint mask attribute.

**Return type:**

[`FloatAttribute`](bpy.types.FloatAttribute.md#bpy.types.FloatAttribute "bpy.types.FloatAttribute")

<a id="bpy.types.Mesh.vertex_paint_mask_remove"></a>

#### bpy.types.Mesh.vertex_paint_mask_remove()

<a id="bpy.types.Mesh.bl_rna_get_subclass"></a>

#### classmethod bpy.types.Mesh.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.Mesh.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.Mesh.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

### Inherited Properties

bpy_struct.id_data, ID.name, ID.name_full, ID.id_type, ID.session_uid, ID.is_evaluated, ID.original, ID.users, ID.use_fake_user, ID.use_extra_user, ID.is_embedded_data, ID.is_linked_packed, ID.is_missing, ID.is_runtime_data, ID.is_editable, ID.tag, ID.is_library_indirect, ID.library, ID.library_weak_reference, ID.asset_data, ID.override_library, ID.preview

<a id="inherited-functions"></a>

### Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, ID.bl_system_properties_get, ID.rename, ID.evaluated_get, ID.copy, ID.asset_mark, ID.asset_clear, ID.asset_generate_preview, ID.override_create, ID.override_hierarchy_create, ID.user_clear, ID.user_remap, ID.make_local, ID.user_of_id, ID.animation_data_create, ID.animation_data_clear, ID.update_tag, ID.preview_ensure, ID.bl_rna_get_subclass, ID.bl_rna_get_subclass_py

<a id="references"></a>

### References

|  |  |
| --- | --- |
| - `bpy.context.mesh` - [`BlendData.meshes`](bpy.types.BlendData.md#bpy.types.BlendData.meshes "bpy.types.BlendData.meshes") - [`BlendDataMeshes.new`](bpy.types.BlendDataMeshes.md#bpy.types.BlendDataMeshes.new "bpy.types.BlendDataMeshes.new") - [`BlendDataMeshes.new_from_object`](bpy.types.BlendDataMeshes.md#bpy.types.BlendDataMeshes.new_from_object "bpy.types.BlendDataMeshes.new_from_object") - [`BlendDataMeshes.remove`](bpy.types.BlendDataMeshes.md#bpy.types.BlendDataMeshes.remove "bpy.types.BlendDataMeshes.remove") | - [`Mesh.texco_mesh`](#bpy.types.Mesh.texco_mesh "bpy.types.Mesh.texco_mesh") - [`Mesh.texture_mesh`](#bpy.types.Mesh.texture_mesh "bpy.types.Mesh.texture_mesh") - [`Mesh.unit_test_compare`](#bpy.types.Mesh.unit_test_compare "bpy.types.Mesh.unit_test_compare") - [`Object.to_mesh`](bpy.types.Object.md#bpy.types.Object.to_mesh "bpy.types.Object.to_mesh") |
