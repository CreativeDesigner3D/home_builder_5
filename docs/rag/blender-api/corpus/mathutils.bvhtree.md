<!-- source: Blender Python API reference 5.2 / mathutils.bvhtree.html -->

<a id="module-mathutils.bvhtree"></a>

# BVHTree Utilities (mathutils.bvhtree)

BVH tree structures for proximity searches and ray casts on geometry.

<a id="mathutils.bvhtree.BVHTree"></a>

### class mathutils.bvhtree.BVHTree

<a id="mathutils.bvhtree.BVHTree.FromBMesh"></a>

#### classmethod mathutils.bvhtree.BVHTree.FromBMesh(bmesh, *, epsilon=0.0)

BVH tree based on `BMesh` data.

**Parameters:**

- **bmesh** (`BMesh`) – BMesh data.
- **epsilon** (float) – Increase the threshold for detecting overlap and raycast hits.

**Returns:**

BVHTree from BMesh data.

**Return type:**

[`BVHTree`](#mathutils.bvhtree.BVHTree "mathutils.bvhtree.BVHTree")

<a id="mathutils.bvhtree.BVHTree.FromObject"></a>

#### classmethod mathutils.bvhtree.BVHTree.FromObject(object, depsgraph, *, deform=True, cage=False, epsilon=0.0)

BVH tree based on `Object` data.

**Parameters:**

- **object** (`Object`) – Mesh object.
- **depsgraph** (`Depsgraph`) – Depsgraph to use for evaluating the mesh.
- **deform** (bool) – Use mesh with deformations.
- **cage** (bool) – Use modifiers cage.
- **epsilon** (float) – Increase the threshold for detecting overlap and raycast hits.

**Returns:**

BVHTree from Object data.

**Return type:**

[`BVHTree`](#mathutils.bvhtree.BVHTree "mathutils.bvhtree.BVHTree")

<a id="mathutils.bvhtree.BVHTree.FromPolygons"></a>

#### classmethod mathutils.bvhtree.BVHTree.FromPolygons(vertices, polygons, *, all_triangles=False, epsilon=0.0)

BVH tree constructed from geometry passed in as arguments.

**Parameters:**

- **vertices** (Sequence[Sequence[float]]) – float triplets each representing `(x, y, z)` coordinates.
- **polygons** (Sequence[Sequence[int]]) – Sequence of polygons, each containing indices to the vertices argument.
- **all_triangles** (bool) – Use when all **polygons** are triangles for more efficient conversion.
- **epsilon** (float) – Increase the threshold for detecting overlap and raycast hits.

**Returns:**

BVHTree from polygon data.

**Return type:**

[`BVHTree`](#mathutils.bvhtree.BVHTree "mathutils.bvhtree.BVHTree")

<a id="mathutils.bvhtree.BVHTree.find_nearest"></a>

#### mathutils.bvhtree.BVHTree.find_nearest(origin, distance=1.84467e+19, /)

Find the nearest element (typically face index) to a point.

**Parameters:**

- **origin** (`Vector`) – Find nearest element to this point.
- **distance** (float) – Maximum distance threshold.

**Returns:**

Returns a tuple: (position, normal, index, distance),
Values will all be None if no hit is found.

**Return type:**

tuple[`Vector` | None, `Vector` | None, int | None, float | None]

<a id="mathutils.bvhtree.BVHTree.find_nearest_range"></a>

#### mathutils.bvhtree.BVHTree.find_nearest_range(origin, distance=1.84467e+19, /)

Find the nearest elements (typically face index) to a point in the distance range.

**Parameters:**

- **origin** (`Vector`) – Find nearest elements to this point.
- **distance** (float) – Maximum distance threshold.

**Returns:**

Returns a list of tuples (position, normal, index, distance)

**Return type:**

list[tuple[`Vector`, `Vector`, int, float]]

<a id="mathutils.bvhtree.BVHTree.overlap"></a>

#### mathutils.bvhtree.BVHTree.overlap(other_tree, /)

Find overlapping indices between 2 trees.

**Parameters:**

**other_tree** ([`BVHTree`](#mathutils.bvhtree.BVHTree "mathutils.bvhtree.BVHTree")) – Other tree to perform overlap test on.

**Returns:**

Returns a list of unique index pairs, the first index referencing this tree, the second referencing the **other_tree**.

**Return type:**

list[tuple[int, int]]

<a id="mathutils.bvhtree.BVHTree.ray_cast"></a>

#### mathutils.bvhtree.BVHTree.ray_cast(origin, direction, distance=sys.float_info.max, /)

Cast a ray onto the geometry.

**Parameters:**

- **origin** (`Vector`) – Start location of the ray.
- **direction** (`Vector`) – Direction of the ray (normalized internally).
- **distance** (float) – Maximum distance threshold.

**Returns:**

Returns a tuple: (position, normal, index, distance),
Values will all be None if no hit is found.

**Return type:**

tuple[`Vector` | None, `Vector` | None, int | None, float | None]
