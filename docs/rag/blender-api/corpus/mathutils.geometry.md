<!-- source: Blender Python API reference 5.2 / mathutils.geometry.html -->

<a id="module-mathutils.geometry"></a>

# Geometry Utilities (mathutils.geometry)

The Blender geometry module.

<a id="mathutils.geometry.area_tri"></a>

### mathutils.geometry.area_tri(v1, v2, v3, /)

Returns the area of the 2D or 3D triangle defined.

**Parameters:**

- **v1** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – Point1
- **v2** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – Point2
- **v3** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – Point3

**Returns:**

The area of the triangle.

**Return type:**

float

<a id="mathutils.geometry.barycentric_transform"></a>

### mathutils.geometry.barycentric_transform(point, tri_a1, tri_a2, tri_a3, tri_b1, tri_b2, tri_b3, /)

Return a transformed point, the transformation is defined by 2 triangles.

**Parameters:**

- **point** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – The point to transform.
- **tri_a1** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – source triangle vertex.
- **tri_a2** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – source triangle vertex.
- **tri_a3** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – source triangle vertex.
- **tri_b1** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – target triangle vertex.
- **tri_b2** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – target triangle vertex.
- **tri_b3** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – target triangle vertex.

**Returns:**

The transformed point

**Return type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="mathutils.geometry.box_fit_2d"></a>

### mathutils.geometry.box_fit_2d(points, /)

Returns an angle that best fits the points to an axis aligned rectangle

**Parameters:**

**points** (Sequence[Sequence[float]]) – Sequence of 2D points.

**Returns:**

The rotation angle in radians for the best axis-aligned bounding box fit.

**Return type:**

float

<a id="mathutils.geometry.box_pack_2d"></a>

### mathutils.geometry.box_pack_2d(boxes, /)

Returns a tuple with the width and height of the packed bounding box.

**Parameters:**

**boxes** (list[list[float]]) – list of boxes, each box is a list where the first 4 items are [X, Y, width, height, …] other items are ignored. The X & Y values in this list are modified to set the packed positions.

**Returns:**

The width and height of the packed bounding box.

**Return type:**

tuple[float, float]

<a id="mathutils.geometry.closest_point_on_tri"></a>

### mathutils.geometry.closest_point_on_tri(pt, tri_p1, tri_p2, tri_p3, /)

Takes 4 vectors: one is the point and the next 3 define the triangle.

**Parameters:**

- **pt** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – Point
- **tri_p1** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – First point of the triangle
- **tri_p2** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – Second point of the triangle
- **tri_p3** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – Third point of the triangle

**Returns:**

The closest point of the triangle.

**Return type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="mathutils.geometry.convex_hull_2d"></a>

### mathutils.geometry.convex_hull_2d(points, /)

Returns the indices of the points forming the convex hull, in counter-clockwise order.

**Parameters:**

**points** (Sequence[Sequence[float]]) – Sequence of 2D points.

**Returns:**

Indices of convex hull vertices in counter-clockwise order.

**Return type:**

list[int]

<a id="mathutils.geometry.delaunay_2d_cdt"></a>

### mathutils.geometry.delaunay_2d_cdt(vert_coords, edges, faces, output_type, epsilon, need_ids=True, /)

Computes the Constrained Delaunay Triangulation of a set of vertices,
with edges and faces that must appear in the triangulation.
Some triangles may be eaten away, or combined with other triangles,
according to output type.
The returned verts may be in a different order from input verts, may be moved
slightly, and may be merged with other nearby verts.
The three returned orig lists give, for each of verts, edges, and faces, the list of
input element indices corresponding to the positionally same output element.
For edges, the orig indices start with the input edges and then continue
with the edges implied by each of the faces (n of them for an n-gon).
If the need_ids argument is supplied, and False, then the code skips the preparation
of the orig arrays, which may save some time.

**Parameters:**

- **vert_coords** (Sequence[[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")]) – Vertex coordinates (2d)
- **edges** (Sequence[tuple[int, int]]) – Edges, as pairs of indices in `vert_coords`
- **faces** (Sequence[Sequence[int]]) – Faces, each sublist is a face, as indices in `vert_coords` (CCW oriented).
- **output_type** (int) – What output looks like. 0 => triangles with convex hull. 1 => triangles inside constraints. 2 => the input constraints, intersected. 3 => like 2 but detect holes and omit them from output. 4 => like 2 but with extra edges to make valid BMesh faces. 5 => like 4 but detect holes and omit them from output.
- **epsilon** (float) – For nearness tests; should not be zero
- **need_ids** (bool) – are the orig output arrays needed?

**Returns:**

Output tuple, (vert_coords, edges, faces, orig_verts, orig_edges, orig_faces)

**Return type:**

tuple[list[[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")], list[tuple[int, int]], list[list[int]], list[list[int]], list[list[int]], list[list[int]]]

<a id="mathutils.geometry.distance_point_to_plane"></a>

### mathutils.geometry.distance_point_to_plane(pt, plane_co, plane_no, /)

Returns the signed distance between a point and a plane (negative when below the normal).

**Parameters:**

- **pt** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – Point
- **plane_co** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – A point on the plane
- **plane_no** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – The direction the plane is facing

**Returns:**

The signed distance.

**Return type:**

float

<a id="mathutils.geometry.interpolate_bezier"></a>

### mathutils.geometry.interpolate_bezier(knot1, handle1, handle2, knot2, resolution, /)

Interpolate a bezier spline segment.

**Parameters:**

- **knot1** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – First bezier spline point.
- **handle1** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – First bezier spline handle.
- **handle2** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – Second bezier spline handle.
- **knot2** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – Second bezier spline point.
- **resolution** (int) – Number of points to return.

**Returns:**

The interpolated points.

**Return type:**

list[[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")]

<a id="mathutils.geometry.intersect_line_line"></a>

### mathutils.geometry.intersect_line_line(v1, v2, v3, v4, /)

Returns a tuple with the points on each line respectively closest to the other.

**Parameters:**

- **v1** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – First point of the first line
- **v2** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – Second point of the first line
- **v3** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – First point of the second line
- **v4** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – Second point of the second line

**Returns:**

The intersection on each line or None when the lines are parallel.

**Return type:**

tuple[[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector"), [`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")] | None

<a id="mathutils.geometry.intersect_line_line_2d"></a>

### mathutils.geometry.intersect_line_line_2d(lineA_p1, lineA_p2, lineB_p1, lineB_p2, /)

Takes 2 segments (defined by 4 vectors) and returns a vector for their point of intersection or None.

> **Warning:**
>
> Despite its name, this function works on segments, and not on lines.

**Parameters:**

- **lineA_p1** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – First point of the first segment
- **lineA_p2** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – Second point of the first segment
- **lineB_p1** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – First point of the second segment
- **lineB_p2** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – Second point of the second segment

**Returns:**

The point of intersection or None when not found

**Return type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | None

<a id="mathutils.geometry.intersect_line_plane"></a>

### mathutils.geometry.intersect_line_plane(line_a, line_b, plane_co, plane_no, no_flip=False, /)

Calculate the intersection between a line (as 2 vectors) and a plane.
Returns a vector for the intersection or None.

**Parameters:**

- **line_a** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – First point of the line
- **line_b** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – Second point of the line
- **plane_co** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – A point on the plane
- **plane_no** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – The direction the plane is facing
- **no_flip** (bool) – Currently ignored.

**Returns:**

The point of intersection or None when not found

**Return type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | None

<a id="mathutils.geometry.intersect_line_sphere"></a>

### mathutils.geometry.intersect_line_sphere(line_a, line_b, sphere_co, sphere_radius, clip=True, /)

Takes a line (as 2 points) and a sphere (as a point and a radius) and
returns the intersection

**Parameters:**

- **line_a** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – First point of the line
- **line_b** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – Second point of the line
- **sphere_co** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – The center of the sphere
- **sphere_radius** (float) – Radius of the sphere
- **clip** (bool) – When False, don’t restrict the intersection to the line segment.

**Returns:**

The intersection points as a pair of vectors (each is None when not found).

**Return type:**

tuple[[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | None, [`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | None]

<a id="mathutils.geometry.intersect_line_sphere_2d"></a>

### mathutils.geometry.intersect_line_sphere_2d(line_a, line_b, sphere_co, sphere_radius, clip=True, /)

Takes a line (as 2 points) and a circle (as a point and a radius) and
returns the intersection

**Parameters:**

- **line_a** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – First point of the line
- **line_b** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – Second point of the line
- **sphere_co** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – The center of the circle
- **sphere_radius** (float) – Radius of the circle
- **clip** (bool) – When False, don’t restrict the intersection to the line segment.

**Returns:**

The intersection points as a pair of vectors (each is None when not found).

**Return type:**

tuple[[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | None, [`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | None]

<a id="mathutils.geometry.intersect_plane_plane"></a>

### mathutils.geometry.intersect_plane_plane(plane_a_co, plane_a_no, plane_b_co, plane_b_no, /)

Return the intersection between two planes

**Parameters:**

- **plane_a_co** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – Point on the first plane
- **plane_a_no** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – Normal of the first plane
- **plane_b_co** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – Point on the second plane
- **plane_b_no** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – Normal of the second plane

**Returns:**

The line of the intersection represented as a point and a vector or None if the intersection can’t be calculated

**Return type:**

tuple[[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector"), [`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")] | tuple[None, None]

<a id="mathutils.geometry.intersect_point_line"></a>

### mathutils.geometry.intersect_point_line(pt, line_p1, line_p2, /)

Takes a point and a line and returns the closest point on the line and its parametric distance from the first point of the line. A value of 0.0 is the first point, 1.0 is the second, values outside [0, 1] are extrapolated.

**Parameters:**

- **pt** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – Point
- **line_p1** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – First point of the line
- **line_p2** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – Second point of the line

**Returns:**

The closest point on the line and its parametric distance from the first point.

**Return type:**

tuple[[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector"), float]

<a id="mathutils.geometry.intersect_point_line_segment"></a>

### mathutils.geometry.intersect_point_line_segment(pt, seg_p1, seg_p2, /)

Takes a point and a segment and returns the closest point on the segment and the distance to the segment.

**Parameters:**

- **pt** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – Point
- **seg_p1** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – First point of the segment
- **seg_p2** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – Second point of the segment

**Returns:**

The closest point on the segment and the distance to the segment.

**Return type:**

tuple[[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector"), float]

<a id="mathutils.geometry.intersect_point_quad_2d"></a>

### mathutils.geometry.intersect_point_quad_2d(pt, quad_p1, quad_p2, quad_p3, quad_p4, /)

Takes 5 vectors (using only the x and y coordinates): one is the point and the next 4 define the quad,
only the x and y are used from the vectors. Returns a non-zero value if the point is within the quad, otherwise 0.
Works only with convex quads without singular edges.

**Parameters:**

- **pt** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – Point
- **quad_p1** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – First point of the quad
- **quad_p2** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – Second point of the quad
- **quad_p3** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – Third point of the quad
- **quad_p4** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – Fourth point of the quad

**Returns:**

1 if inside with CCW winding, -1 if inside with CW winding, otherwise 0.

**Return type:**

int

<a id="mathutils.geometry.intersect_point_tri"></a>

### mathutils.geometry.intersect_point_tri(pt, tri_p1, tri_p2, tri_p3, /)

Takes 4 vectors: one is the point and the next 3 define the triangle. Projects the point onto the triangle plane and checks if it is within the triangle.

**Parameters:**

- **pt** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – Point
- **tri_p1** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – First point of the triangle
- **tri_p2** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – Second point of the triangle
- **tri_p3** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – Third point of the triangle

**Returns:**

Point on the triangle’s plane or None if it’s outside the triangle

**Return type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | None

<a id="mathutils.geometry.intersect_point_tri_2d"></a>

### mathutils.geometry.intersect_point_tri_2d(pt, tri_p1, tri_p2, tri_p3, /)

Takes 4 vectors (using only the x and y coordinates): one is the point and the next 3 define the triangle. Returns a non-zero value if the point is within the triangle, otherwise 0.

**Parameters:**

- **pt** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – Point
- **tri_p1** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – First point of the triangle
- **tri_p2** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – Second point of the triangle
- **tri_p3** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – Third point of the triangle

**Returns:**

1 if inside with CCW winding, -1 if inside with CW winding, otherwise 0.

**Return type:**

int

<a id="mathutils.geometry.intersect_ray_tri"></a>

### mathutils.geometry.intersect_ray_tri(v1, v2, v3, ray, orig, clip=True, /)

Returns the intersection between a ray and a triangle, if possible, returns None otherwise.

**Parameters:**

- **v1** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – Point1
- **v2** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – Point2
- **v3** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – Point3
- **ray** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – Direction of the ray
- **orig** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – Origin
- **clip** (bool) – When False, don’t restrict the intersection to the area of the triangle, use the infinite plane defined by the triangle.

**Returns:**

The point of intersection or None if no intersection is found

**Return type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | None

<a id="mathutils.geometry.intersect_sphere_sphere_2d"></a>

### mathutils.geometry.intersect_sphere_sphere_2d(p_a, radius_a, p_b, radius_b, /)

Returns the 2 intersection points of two circles.

**Parameters:**

- **p_a** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – Center of the first circle
- **radius_a** (float) – Radius of the first circle
- **p_b** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – Center of the second circle
- **radius_b** (float) – Radius of the second circle

**Returns:**

The 2 intersection points or None when there is no intersection.

**Return type:**

tuple[[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector"), [`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")] | tuple[None, None]

<a id="mathutils.geometry.intersect_tri_tri_2d"></a>

### mathutils.geometry.intersect_tri_tri_2d(tri_a1, tri_a2, tri_a3, tri_b1, tri_b2, tri_b3, /)

Check if two 2D triangles intersect.

**Parameters:**

- **tri_a1** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – First vertex of the first triangle.
- **tri_a2** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – Second vertex of the first triangle.
- **tri_a3** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – Third vertex of the first triangle.
- **tri_b1** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – First vertex of the second triangle.
- **tri_b2** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – Second vertex of the second triangle.
- **tri_b3** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – Third vertex of the second triangle.

**Returns:**

True if the triangles intersect.

**Return type:**

bool

<a id="mathutils.geometry.normal"></a>

### mathutils.geometry.normal(*vectors)

Returns the normal of a 3D polygon.

**Parameters:**

**vectors** (Sequence[Sequence[float]]) – 3 or more vectors to calculate normals.

**Returns:**

The normal vector.

**Return type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="mathutils.geometry.points_in_planes"></a>

### mathutils.geometry.points_in_planes(planes, epsilon_coplanar=1e-4, epsilon_isect=1e-6, /)

Returns a list of points inside all planes given and a list of index values for the planes used.

**Parameters:**

- **planes** (list[[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")]) – List of planes (4D vectors).
- **epsilon_coplanar** (float) – Epsilon value for interpreting plane pairs as co-planar.
- **epsilon_isect** (float) – Epsilon value for intersection.

**Returns:**

Two lists, one containing the 3D coordinates inside the planes, another containing the plane indices used.

**Return type:**

tuple[list[[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")], list[int]]

<a id="mathutils.geometry.tessellate_polygon"></a>

### mathutils.geometry.tessellate_polygon(polylines, /)

Takes a list of polylines (each point a pair or triplet of numbers) and returns the point indices for a polyline filled with triangles. Does not handle degenerate geometry (such as zero-length lines due to consecutive identical points).

**Parameters:**

**polylines** (Sequence[Sequence[Sequence[float]]]) – Polygons where each polygon is a sequence of 2D or 3D points.

**Returns:**

A list of triangles.

**Return type:**

list[tuple[int, int, int]]

<a id="mathutils.geometry.volume_tetrahedron"></a>

### mathutils.geometry.volume_tetrahedron(v1, v2, v3, v4, /)

Return the absolute (unsigned) volume formed by a tetrahedron (points can be in any order).

**Parameters:**

- **v1** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – Point1
- **v2** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – Point2
- **v3** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – Point3
- **v4** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – Point4

**Returns:**

The volume of the tetrahedron.

**Return type:**

float
