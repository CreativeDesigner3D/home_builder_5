<!-- source: Blender Python API reference 5.2 / freestyle.utils.html -->

<a id="module-freestyle.utils"></a>

# Freestyle Utilities (freestyle.utils)

This module contains helper functions used for Freestyle style module
writing.

Submodules

- [freestyle.utils submodule (freestyle.utils.ContextFunctions)](freestyle.utils.ContextFunctions.md)

<a id="freestyle.utils.getCurrentScene"></a>

### freestyle.utils.getCurrentScene()

Returns the current scene.

**Returns:**

The current scene.

**Return type:**

[`bpy.types.Scene`](bpy.types.Scene.md#bpy.types.Scene "bpy.types.Scene")

<a id="freestyle.utils.integrate"></a>

### freestyle.utils.integrate(func, it, it_end, integration_type)

Returns a single value from a set of values evaluated at each 0D
element of this 1D element.

**Parameters:**

- **func** (`UnaryFunction0D`) – The UnaryFunction0D used to compute a value at each
  Interface0D.
- **it** (`Interface0DIterator`) – The Interface0DIterator used to iterate over the 0D
  elements of this 1D element. The integration will occur over
  the 0D elements starting from the one pointed by it.
- **it_end** (`Interface0DIterator`) – The Interface0DIterator pointing the end of the 0D
  elements of the 1D element.
- **integration_type** (`IntegrationType`) – The integration method used to compute a
  single value from a set of values.

**Returns:**

The single value obtained for the 1D element. The return
value type is float if func is of the `UnaryFunction0DDouble`
or `UnaryFunction0DFloat` type, and int if func is of the
`UnaryFunction0DUnsigned` type.

**Return type:**

int | float

<a id="freestyle.utils.angle_x_normal"></a>

### freestyle.utils.angle_x_normal(it: Interface0DIterator)

unsigned angle between a Point’s normal and the X axis, in radians

**Parameters:**

**it** (`Interface0DIterator`) – An iterator over Interface0D objects.

**Return type:**

float

<a id="freestyle.utils.bound"></a>

### freestyle.utils.bound(lower, x, higher)

Returns x bounded by a maximum and minimum value. Equivalent to:
return min(max(x, lower), higher)

**Parameters:**

- **lower** (float) – Lower bound.
- **x** (float) – Value to clamp.
- **higher** (float) – Upper bound.

**Return type:**

float

<a id="freestyle.utils.bounding_box"></a>

### freestyle.utils.bounding_box(stroke)

Returns the maximum and minimum coordinates (the bounding box) of the stroke’s vertices

**Parameters:**

**stroke** (`Stroke`) – A stroke.

**Return type:**

tuple[[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector"), [`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")]

<a id="freestyle.utils.curvature_from_stroke_vertex"></a>

### freestyle.utils.curvature_from_stroke_vertex(svert)

The 3D curvature of an stroke vertex’ underlying geometry
:   The result is None or in the range [-inf, inf]

**Parameters:**

**svert** (`StrokeVertex`) – A stroke vertex.

**Return type:**

float | None

<a id="freestyle.utils.find_matching_vertex"></a>

### freestyle.utils.find_matching_vertex(id, it)

Finds the matching vertex, or returns None.

**Parameters:**

- **id** (`Id`) – The ID to match.
- **it** (`AdjacencyIterator`) – An iterator over candidate ViewEdges.

**Return type:**

`ViewEdge` | None

<a id="freestyle.utils.get_chain_length"></a>

### freestyle.utils.get_chain_length(ve, orientation)

Returns the 2d length of a given ViewEdge.

**Parameters:**

- **ve** (`ViewEdge`) – The ViewEdge whose chain length to compute.
- **orientation** (bool) – Direction in which to traverse the chain.

**Return type:**

float

<a id="freestyle.utils.get_object_name"></a>

### freestyle.utils.get_object_name(stroke)

Returns the name of the object that this stroke is drawn on.

**Parameters:**

**stroke** (`Stroke`) – A stroke.

**Return type:**

str | None

<a id="freestyle.utils.get_strokes"></a>

### freestyle.utils.get_strokes()

Get all strokes that are currently available

<a id="freestyle.utils.get_test_stroke"></a>

### freestyle.utils.get_test_stroke()

Returns a static stroke object for testing

<a id="freestyle.utils.is_poly_clockwise"></a>

### freestyle.utils.is_poly_clockwise(stroke)

True if the stroke is orientated in a clockwise way, False otherwise

**Parameters:**

**stroke** (`Stroke`) – A stroke whose orientation is tested.

**Return type:**

bool

<a id="freestyle.utils.iter_distance_along_stroke"></a>

### freestyle.utils.iter_distance_along_stroke(stroke)

Yields the absolute distance along the stroke up to the current vertex.

**Parameters:**

**stroke** (`Stroke`) – A stroke.

<a id="freestyle.utils.iter_distance_from_camera"></a>

### freestyle.utils.iter_distance_from_camera(stroke, range_min, range_max, normfac)

Yields the distance to the camera relative to the maximum
possible distance for every stroke vertex, constrained by
given minimum and maximum values.

**Parameters:**

- **stroke** (`Stroke`) – A stroke.
- **range_min** (float) – Distances below this value are clamped to 0.
- **range_max** (float) – Distances above this value are clamped to 1.
- **normfac** (float) – Normalization factor applied to `distance - range_min`.

<a id="freestyle.utils.iter_distance_from_object"></a>

### freestyle.utils.iter_distance_from_object(stroke, location, range_min, range_max, normfac)

yields the distance to the given object relative to the maximum
possible distance for every stroke vertex, constrained by
given minimum and maximum values.

**Parameters:**

- **stroke** (`Stroke`) – A stroke.
- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – Reference location in 3D space.
- **range_min** (float) – Distances below this value are clamped to 0.
- **range_max** (float) – Distances above this value are clamped to 1.
- **normfac** (float) – Normalization factor applied to `distance - range_min`.

<a id="freestyle.utils.iter_material_value"></a>

### freestyle.utils.iter_material_value(stroke, func, attribute)

Yields a specific material attribute from the vertex’ underlying material.

**Parameters:**

- **stroke** (`Stroke`) – A stroke.
- **func** (Callable[[`Interface0DIterator`], `Material`]) – A function returning a material for the iterator’s current vertex.
- **attribute** (str) – The material attribute name (e.g. `LINE`, `DIFF`, `ALPHA`).

<a id="freestyle.utils.iter_t2d_along_stroke"></a>

### freestyle.utils.iter_t2d_along_stroke(stroke)

Yields the progress along the stroke.

**Parameters:**

**stroke** (`Stroke`) – A stroke.

<a id="freestyle.utils.material_from_fedge"></a>

### freestyle.utils.material_from_fedge(fe)

Get the diffuse RGBA color from an FEdge.

**Parameters:**

**fe** (`FEdge`) – An FEdge.

**Return type:**

`Material` | None

<a id="freestyle.utils.normal_at_I0D"></a>

### freestyle.utils.normal_at_I0D(it: Interface0DIterator) → Vector

Normal at an Interface0D object. In contrast to Normal2DF0D this
:   function uses the actual data instead of underlying Fedge objects.

**Parameters:**

**it** (`Interface0DIterator`) – An iterator over Interface0D objects.

**Return type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="freestyle.utils.pairwise"></a>

### freestyle.utils.pairwise(iterable, types=None)

Yields a tuple containing the previous and current object.

**Parameters:**

- **iterable** (Iterable[Any]) – An iterable of items.
- **types** (tuple[type, ...] | None) – Container types for which the iterator’s `incremented()`
  method is used instead of standard tee-based pairing. When `None`
  defaults to `(Stroke, StrokeVertexIterator)`.

<a id="freestyle.utils.rgb_to_bw"></a>

### freestyle.utils.rgb_to_bw(r, g, b)

Method to convert rgb to a bw intensity value.

**Parameters:**

- **r** (float) – Red channel (0..1).
- **g** (float) – Green channel (0..1).
- **b** (float) – Blue channel (0..1).

**Return type:**

float

<a id="freestyle.utils.simplify"></a>

### freestyle.utils.simplify(points, tolerance)

Simplifies a set of points.

**Parameters:**

- **points** (Sequence[[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")]) – Points to simplify.
- **tolerance** (float) – Maximum allowed deviation from the original curve.

**Return type:**

tuple

<a id="freestyle.utils.stroke_curvature"></a>

### freestyle.utils.stroke_curvature(it)

Compute the 2D curvature at the stroke vertex pointed by the iterator ‘it’.
K = 1 / R
where R is the radius of the circle going through the current vertex and its neighbors

**Parameters:**

**it** (`StrokeVertexIterator`) – An iterator over a stroke’s vertices.

<a id="freestyle.utils.stroke_normal"></a>

### freestyle.utils.stroke_normal(stroke)

Compute the 2D normal at the stroke vertex pointed by the iterator
‘it’. It is noted that Normal2DF0D computes normals based on
underlying FEdges instead, which is inappropriate for strokes when
they have already been modified by stroke geometry modifiers.

The returned normals are dynamic: they update when the
vertex position (and therefore the vertex normal) changes.
for use in geometry modifiers it is advised to
cast this generator function to a tuple or list

**Parameters:**

**stroke** (`Stroke`) – A stroke.

<a id="freestyle.utils.tripplewise"></a>

### freestyle.utils.tripplewise(iterable)

Yields a tuple containing the current object and its immediate neighbors.

**Parameters:**

**iterable** (Iterable[Any]) – An iterable of items.

<a id="freestyle.utils.BoundingBox"></a>

### class freestyle.utils.BoundingBox

Object representing a bounding box consisting out of 2 2D vectors

<a id="freestyle.utils.BoundingBox.inside"></a>

#### freestyle.utils.BoundingBox.inside(other)

True if self inside other, False otherwise.

**Parameters:**

**other** ([`BoundingBox`](#freestyle.utils.BoundingBox "freestyle.utils.BoundingBox")) – Another bounding box to test containment against.

**Return type:**

bool

<a id="freestyle.utils.BoundingBox.from_sequence"></a>

#### classmethod freestyle.utils.BoundingBox.from_sequence(sequence)

BoundingBox from sequence of 2D or 3D Vector objects.

**Parameters:**

**sequence** (Iterable[[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")]) – An iterable of vectors to compute the box from.

**Return type:**

[`BoundingBox`](#freestyle.utils.BoundingBox "freestyle.utils.BoundingBox")

Special Methods

<a id="freestyle.utils.BoundingBox.__repr__"></a>

#### freestyle.utils.BoundingBox.__repr__()

**Return type:**

str

<a id="freestyle.utils.StrokeCollector"></a>

### class freestyle.utils.StrokeCollector

Collects and Stores stroke objects

<a id="freestyle.utils.StrokeCollector.shade"></a>

#### freestyle.utils.StrokeCollector.shade(stroke)

**Parameters:**

**stroke** (`Stroke`) – The stroke to collect.
