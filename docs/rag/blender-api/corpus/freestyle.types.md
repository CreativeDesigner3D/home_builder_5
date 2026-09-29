<!-- source: Blender Python API reference 5.2 / freestyle.types.html -->

<a id="module-freestyle.types"></a>

# Freestyle Types (freestyle.types)

This module contains core classes of the Freestyle Python API,
including data types of view map components (0D and 1D elements), base
classes for user-defined line stylization rules (predicates,
functions, chaining iterators, and stroke shaders), and operators.

Class hierarchy:

- [`BBox`](#freestyle.types.BBox "freestyle.types.BBox")
- [`BinaryPredicate0D`](#freestyle.types.BinaryPredicate0D "freestyle.types.BinaryPredicate0D")
- [`BinaryPredicate1D`](#freestyle.types.BinaryPredicate1D "freestyle.types.BinaryPredicate1D")
- [`Id`](#freestyle.types.Id "freestyle.types.Id")
- [`Interface0D`](#freestyle.types.Interface0D "freestyle.types.Interface0D")

  - [`CurvePoint`](#freestyle.types.CurvePoint "freestyle.types.CurvePoint")

    - [`StrokeVertex`](#freestyle.types.StrokeVertex "freestyle.types.StrokeVertex")
  - [`SVertex`](#freestyle.types.SVertex "freestyle.types.SVertex")
  - [`ViewVertex`](#freestyle.types.ViewVertex "freestyle.types.ViewVertex")

    - [`NonTVertex`](#freestyle.types.NonTVertex "freestyle.types.NonTVertex")
    - [`TVertex`](#freestyle.types.TVertex "freestyle.types.TVertex")
- [`Interface1D`](#freestyle.types.Interface1D "freestyle.types.Interface1D")

  - [`Curve`](#freestyle.types.Curve "freestyle.types.Curve")

    - [`Chain`](#freestyle.types.Chain "freestyle.types.Chain")
  - [`FEdge`](#freestyle.types.FEdge "freestyle.types.FEdge")

    - [`FEdgeSharp`](#freestyle.types.FEdgeSharp "freestyle.types.FEdgeSharp")
    - [`FEdgeSmooth`](#freestyle.types.FEdgeSmooth "freestyle.types.FEdgeSmooth")
  - [`Stroke`](#freestyle.types.Stroke "freestyle.types.Stroke")
  - [`ViewEdge`](#freestyle.types.ViewEdge "freestyle.types.ViewEdge")
- [`Iterator`](#freestyle.types.Iterator "freestyle.types.Iterator")

  - [`AdjacencyIterator`](#freestyle.types.AdjacencyIterator "freestyle.types.AdjacencyIterator")
  - [`CurvePointIterator`](#freestyle.types.CurvePointIterator "freestyle.types.CurvePointIterator")
  - [`Interface0DIterator`](#freestyle.types.Interface0DIterator "freestyle.types.Interface0DIterator")
  - [`SVertexIterator`](#freestyle.types.SVertexIterator "freestyle.types.SVertexIterator")
  - [`StrokeVertexIterator`](#freestyle.types.StrokeVertexIterator "freestyle.types.StrokeVertexIterator")
  - [`ViewEdgeIterator`](#freestyle.types.ViewEdgeIterator "freestyle.types.ViewEdgeIterator")

    - [`ChainingIterator`](#freestyle.types.ChainingIterator "freestyle.types.ChainingIterator")
  - [`orientedViewEdgeIterator`](#freestyle.types.orientedViewEdgeIterator "freestyle.types.orientedViewEdgeIterator")
- [`Material`](#freestyle.types.Material "freestyle.types.Material")
- [`Noise`](#freestyle.types.Noise "freestyle.types.Noise")
- [`Operators`](#freestyle.types.Operators "freestyle.types.Operators")
- [`SShape`](#freestyle.types.SShape "freestyle.types.SShape")
- [`StrokeAttribute`](#freestyle.types.StrokeAttribute "freestyle.types.StrokeAttribute")
- [`StrokeShader`](#freestyle.types.StrokeShader "freestyle.types.StrokeShader")
- [`UnaryFunction0D`](#freestyle.types.UnaryFunction0D "freestyle.types.UnaryFunction0D")

  - [`UnaryFunction0DDouble`](#freestyle.types.UnaryFunction0DDouble "freestyle.types.UnaryFunction0DDouble")
  - [`UnaryFunction0DEdgeNature`](#freestyle.types.UnaryFunction0DEdgeNature "freestyle.types.UnaryFunction0DEdgeNature")
  - [`UnaryFunction0DFloat`](#freestyle.types.UnaryFunction0DFloat "freestyle.types.UnaryFunction0DFloat")
  - [`UnaryFunction0DId`](#freestyle.types.UnaryFunction0DId "freestyle.types.UnaryFunction0DId")
  - [`UnaryFunction0DMaterial`](#freestyle.types.UnaryFunction0DMaterial "freestyle.types.UnaryFunction0DMaterial")
  - [`UnaryFunction0DUnsigned`](#freestyle.types.UnaryFunction0DUnsigned "freestyle.types.UnaryFunction0DUnsigned")
  - [`UnaryFunction0DVec2f`](#freestyle.types.UnaryFunction0DVec2f "freestyle.types.UnaryFunction0DVec2f")
  - [`UnaryFunction0DVec3f`](#freestyle.types.UnaryFunction0DVec3f "freestyle.types.UnaryFunction0DVec3f")
  - [`UnaryFunction0DVectorViewShape`](#freestyle.types.UnaryFunction0DVectorViewShape "freestyle.types.UnaryFunction0DVectorViewShape")
  - [`UnaryFunction0DViewShape`](#freestyle.types.UnaryFunction0DViewShape "freestyle.types.UnaryFunction0DViewShape")
- [`UnaryFunction1D`](#freestyle.types.UnaryFunction1D "freestyle.types.UnaryFunction1D")

  - [`UnaryFunction1DDouble`](#freestyle.types.UnaryFunction1DDouble "freestyle.types.UnaryFunction1DDouble")
  - [`UnaryFunction1DEdgeNature`](#freestyle.types.UnaryFunction1DEdgeNature "freestyle.types.UnaryFunction1DEdgeNature")
  - [`UnaryFunction1DFloat`](#freestyle.types.UnaryFunction1DFloat "freestyle.types.UnaryFunction1DFloat")
  - [`UnaryFunction1DUnsigned`](#freestyle.types.UnaryFunction1DUnsigned "freestyle.types.UnaryFunction1DUnsigned")
  - [`UnaryFunction1DVec2f`](#freestyle.types.UnaryFunction1DVec2f "freestyle.types.UnaryFunction1DVec2f")
  - [`UnaryFunction1DVec3f`](#freestyle.types.UnaryFunction1DVec3f "freestyle.types.UnaryFunction1DVec3f")
  - [`UnaryFunction1DVectorViewShape`](#freestyle.types.UnaryFunction1DVectorViewShape "freestyle.types.UnaryFunction1DVectorViewShape")
  - [`UnaryFunction1DVoid`](#freestyle.types.UnaryFunction1DVoid "freestyle.types.UnaryFunction1DVoid")
- [`UnaryPredicate0D`](#freestyle.types.UnaryPredicate0D "freestyle.types.UnaryPredicate0D")
- [`UnaryPredicate1D`](#freestyle.types.UnaryPredicate1D "freestyle.types.UnaryPredicate1D")
- [`ViewMap`](#freestyle.types.ViewMap "freestyle.types.ViewMap")
- [`ViewShape`](#freestyle.types.ViewShape "freestyle.types.ViewShape")
- [`IntegrationType`](#freestyle.types.IntegrationType "freestyle.types.IntegrationType")
- [`MediumType`](#freestyle.types.MediumType "freestyle.types.MediumType")
- [`Nature`](#freestyle.types.Nature "freestyle.types.Nature")

<a id="freestyle.types.AdjacencyIterator"></a>

### class freestyle.types.AdjacencyIterator

Class hierarchy: [`Iterator`](#freestyle.types.Iterator "freestyle.types.Iterator") > [`AdjacencyIterator`](#freestyle.types.AdjacencyIterator "freestyle.types.AdjacencyIterator")

Class for representing adjacency iterators used in the chaining
process. An AdjacencyIterator is created in the increment() and
decrement() methods of a [`ChainingIterator`](#freestyle.types.ChainingIterator "freestyle.types.ChainingIterator") and passed to the
traverse() method of the ChainingIterator.

<a id="freestyle.types.AdjacencyIterator.__init__"></a>

#### freestyle.types.AdjacencyIterator.__init__(*args, **kwargs)

Accepted call signatures:

- `__init__()`
- `__init__(brother)`
- `__init__(vertex, restrict_to_selection=True, restrict_to_unvisited=True)`

Builds an [`AdjacencyIterator`](#freestyle.types.AdjacencyIterator "freestyle.types.AdjacencyIterator") using the default constructor,
copy constructor or the overloaded constructor.

**Parameters:**

- **brother** ([`AdjacencyIterator`](#freestyle.types.AdjacencyIterator "freestyle.types.AdjacencyIterator")) – An AdjacencyIterator object.
- **vertex** ([`ViewVertex`](#freestyle.types.ViewVertex "freestyle.types.ViewVertex")) – The vertex which is the next crossing.
- **restrict_to_selection** (bool) – Indicates whether to force the chaining
  to stay within the set of selected ViewEdges or not.
- **restrict_to_unvisited** (bool) – Indicates whether a ViewEdge that has
  already been chained must be ignored ot not.

<a id="freestyle.types.AdjacencyIterator.is_incoming"></a>

#### freestyle.types.AdjacencyIterator.is_incoming

True if the current ViewEdge is coming towards the iteration vertex, and
False otherwise.

**Type:**

bool

<a id="freestyle.types.AdjacencyIterator.object"></a>

#### freestyle.types.AdjacencyIterator.object

The ViewEdge object currently pointed to by this iterator.

**Type:**

[`ViewEdge`](#freestyle.types.ViewEdge "freestyle.types.ViewEdge")

Special Methods

<a id="freestyle.types.AdjacencyIterator.__iter__"></a>

#### freestyle.types.AdjacencyIterator.__iter__()

**Return type:**

[`AdjacencyIterator`](#freestyle.types.AdjacencyIterator "freestyle.types.AdjacencyIterator")

<a id="freestyle.types.AdjacencyIterator.__next__"></a>

#### freestyle.types.AdjacencyIterator.__next__()

**Return type:**

Any

<a id="freestyle.types.BBox"></a>

### class freestyle.types.BBox

Class for representing a bounding box.

<a id="freestyle.types.BBox.__init__"></a>

#### freestyle.types.BBox.__init__()

Default constructor.

Special Methods

<a id="freestyle.types.BBox.__repr__"></a>

#### freestyle.types.BBox.__repr__()

**Return type:**

str

<a id="freestyle.types.BinaryPredicate0D"></a>

### class freestyle.types.BinaryPredicate0D

Base class for binary predicates working on [`Interface0D`](#freestyle.types.Interface0D "freestyle.types.Interface0D")
objects. A BinaryPredicate0D is typically an ordering relation
between two Interface0D objects. The predicate evaluates a relation
between the two Interface0D instances and returns a boolean value (true
or false). It is used by invoking the __call__() method.

<a id="freestyle.types.BinaryPredicate0D.__init__"></a>

#### freestyle.types.BinaryPredicate0D.__init__()

Default constructor.

<a id="freestyle.types.BinaryPredicate0D.__call__"></a>

#### freestyle.types.BinaryPredicate0D.__call__(inter1, inter2)

Must be overload by inherited classes. It evaluates a relation
between two Interface0D objects.

**Parameters:**

- **inter1** ([`Interface0D`](#freestyle.types.Interface0D "freestyle.types.Interface0D")) – The first Interface0D object.
- **inter2** ([`Interface0D`](#freestyle.types.Interface0D "freestyle.types.Interface0D")) – The second Interface0D object.

**Returns:**

True or false.

**Return type:**

bool

<a id="freestyle.types.BinaryPredicate0D.name"></a>

#### freestyle.types.BinaryPredicate0D.name

The name of the binary 0D predicate.

**Type:**

str

Special Methods

<a id="freestyle.types.BinaryPredicate0D.__repr__"></a>

#### freestyle.types.BinaryPredicate0D.__repr__()

**Return type:**

str

<a id="freestyle.types.BinaryPredicate1D"></a>

### class freestyle.types.BinaryPredicate1D

Base class for binary predicates working on [`Interface1D`](#freestyle.types.Interface1D "freestyle.types.Interface1D")
objects. A BinaryPredicate1D is typically an ordering relation
between two Interface1D objects. The predicate evaluates a relation
between the two Interface1D instances and returns a boolean value (true
or false). It is used by invoking the __call__() method.

<a id="freestyle.types.BinaryPredicate1D.__init__"></a>

#### freestyle.types.BinaryPredicate1D.__init__()

Default constructor.

<a id="freestyle.types.BinaryPredicate1D.__call__"></a>

#### freestyle.types.BinaryPredicate1D.__call__(inter1, inter2)

Must be overload by inherited classes. It evaluates a relation
between two Interface1D objects.

**Parameters:**

- **inter1** ([`Interface1D`](#freestyle.types.Interface1D "freestyle.types.Interface1D")) – The first Interface1D object.
- **inter2** ([`Interface1D`](#freestyle.types.Interface1D "freestyle.types.Interface1D")) – The second Interface1D object.

**Returns:**

True or false.

**Return type:**

bool

<a id="freestyle.types.BinaryPredicate1D.name"></a>

#### freestyle.types.BinaryPredicate1D.name

The name of the binary 1D predicate.

**Type:**

str

Special Methods

<a id="freestyle.types.BinaryPredicate1D.__repr__"></a>

#### freestyle.types.BinaryPredicate1D.__repr__()

**Return type:**

str

<a id="freestyle.types.Chain"></a>

### class freestyle.types.Chain

Class hierarchy: [`Interface1D`](#freestyle.types.Interface1D "freestyle.types.Interface1D") > [`Curve`](#freestyle.types.Curve "freestyle.types.Curve") > [`Chain`](#freestyle.types.Chain "freestyle.types.Chain")

Class to represent a 1D elements issued from the chaining process. A
Chain is the last step before the [`Stroke`](#freestyle.types.Stroke "freestyle.types.Stroke") and is used in the
Splitting and Creation processes.

<a id="freestyle.types.Chain.__init__"></a>

#### freestyle.types.Chain.__init__(*args)

Accepted call signatures:

- `__init__()`
- `__init__(brother)`
- `__init__(id)`

Builds a [`Chain`](#freestyle.types.Chain "freestyle.types.Chain") using the default constructor,
copy constructor or from an [`Id`](#freestyle.types.Id "freestyle.types.Id").

**Parameters:**

- **brother** ([`Chain`](#freestyle.types.Chain "freestyle.types.Chain")) – A Chain object.
- **id** ([`Id`](#freestyle.types.Id "freestyle.types.Id")) – An Id object.

<a id="freestyle.types.Chain.push_viewedge_back"></a>

#### freestyle.types.Chain.push_viewedge_back(viewedge, orientation)

Adds a ViewEdge at the end of the Chain.

**Parameters:**

- **viewedge** ([`ViewEdge`](#freestyle.types.ViewEdge "freestyle.types.ViewEdge")) – The ViewEdge that must be added.
- **orientation** (bool) – The orientation with which the ViewEdge must be processed.

<a id="freestyle.types.Chain.push_viewedge_front"></a>

#### freestyle.types.Chain.push_viewedge_front(viewedge, orientation)

Adds a ViewEdge at the beginning of the Chain.

**Parameters:**

- **viewedge** ([`ViewEdge`](#freestyle.types.ViewEdge "freestyle.types.ViewEdge")) – The ViewEdge that must be added.
- **orientation** (bool) – The orientation with which the ViewEdge must be
  processed.

<a id="freestyle.types.ChainingIterator"></a>

### class freestyle.types.ChainingIterator

Class hierarchy: [`Iterator`](#freestyle.types.Iterator "freestyle.types.Iterator") > [`ViewEdgeIterator`](#freestyle.types.ViewEdgeIterator "freestyle.types.ViewEdgeIterator") > [`ChainingIterator`](#freestyle.types.ChainingIterator "freestyle.types.ChainingIterator")

Base class for chaining iterators. This class is designed to be
overloaded in order to describe chaining rules. It makes the
description of chaining rules easier. The two main methods that need
to overloaded are traverse() and init(). traverse() tells which
[`ViewEdge`](#freestyle.types.ViewEdge "freestyle.types.ViewEdge") to follow, among the adjacent ones. If you specify
restriction rules (such as “Chain only ViewEdges of the selection”),
they will be included in the adjacency iterator (i.e, the adjacent
iterator will only stop on “valid” edges).

<a id="freestyle.types.ChainingIterator.__init__"></a>

#### freestyle.types.ChainingIterator.__init__(*args)

Accepted call signatures:

- `__init__(restrict_to_selection=True, restrict_to_unvisited=True, begin=None, orientation=True)`
- `__init__(brother)`

Builds a Chaining Iterator from the first ViewEdge used for
iteration and its orientation or by using the copy constructor.

**Parameters:**

- **restrict_to_selection** (bool) – Indicates whether to force the chaining
  to stay within the set of selected ViewEdges or not.
- **restrict_to_unvisited** (bool) – Indicates whether a ViewEdge that has
  already been chained must be ignored ot not.
- **begin** ([`ViewEdge`](#freestyle.types.ViewEdge "freestyle.types.ViewEdge") | None) – The ViewEdge from which to start the chain.
- **orientation** (bool) – The direction to follow to explore the graph. If
  true, the direction indicated by the first ViewEdge is used.
- **brother** ([ChainingIterator](#freestyle.types.ChainingIterator "freestyle.types.ChainingIterator"))

<a id="freestyle.types.ChainingIterator.init"></a>

#### freestyle.types.ChainingIterator.init()

Initializes the iterator context. This method is called each
time a new chain is started. It can be used to reset some
history information that you might want to keep.

<a id="freestyle.types.ChainingIterator.traverse"></a>

#### freestyle.types.ChainingIterator.traverse(it)

This method iterates over the potential next ViewEdges and returns
the one that will be followed next. Returns the next ViewEdge to
follow or None when the end of the chain is reached.

**Parameters:**

**it** ([`AdjacencyIterator`](#freestyle.types.AdjacencyIterator "freestyle.types.AdjacencyIterator")) – The iterator over the ViewEdges adjacent to the end vertex
of the current ViewEdge. The adjacency iterator reflects the
restriction rules by only iterating over the valid ViewEdges.

**Returns:**

Returns the next ViewEdge to follow, or None if chaining ends.

**Return type:**

[`ViewEdge`](#freestyle.types.ViewEdge "freestyle.types.ViewEdge") | None

<a id="freestyle.types.ChainingIterator.is_incrementing"></a>

#### freestyle.types.ChainingIterator.is_incrementing

True if the current iteration is an incrementation.

**Type:**

bool

<a id="freestyle.types.ChainingIterator.next_vertex"></a>

#### freestyle.types.ChainingIterator.next_vertex

The ViewVertex that is the next crossing.

**Type:**

[`ViewVertex`](#freestyle.types.ViewVertex "freestyle.types.ViewVertex")

<a id="freestyle.types.ChainingIterator.object"></a>

#### freestyle.types.ChainingIterator.object

The ViewEdge object currently pointed by this iterator.

**Type:**

[`ViewEdge`](#freestyle.types.ViewEdge "freestyle.types.ViewEdge")

<a id="freestyle.types.Curve"></a>

### class freestyle.types.Curve

Class hierarchy: [`Interface1D`](#freestyle.types.Interface1D "freestyle.types.Interface1D") > [`Curve`](#freestyle.types.Curve "freestyle.types.Curve")

Base class for curves made of CurvePoints. [`SVertex`](#freestyle.types.SVertex "freestyle.types.SVertex") is the
type of the initial curve vertices. A [`Chain`](#freestyle.types.Chain "freestyle.types.Chain") is a
specialization of a Curve.

<a id="freestyle.types.Curve.__init__"></a>

#### freestyle.types.Curve.__init__(*args)

Accepted call signatures:

- `__init__()`
- `__init__(brother)`
- `__init__(id)`

Builds a `FrsCurve` using a default constructor,
copy constructor or from an [`Id`](#freestyle.types.Id "freestyle.types.Id").

**Parameters:**

- **brother** ([`Curve`](#freestyle.types.Curve "freestyle.types.Curve")) – A Curve object.
- **id** ([`Id`](#freestyle.types.Id "freestyle.types.Id")) – An Id object.

<a id="freestyle.types.Curve.push_vertex_back"></a>

#### freestyle.types.Curve.push_vertex_back(vertex)

Adds a single vertex at the end of the Curve.

**Parameters:**

**vertex** ([`SVertex`](#freestyle.types.SVertex "freestyle.types.SVertex") | [`CurvePoint`](#freestyle.types.CurvePoint "freestyle.types.CurvePoint")) – A vertex object.

<a id="freestyle.types.Curve.push_vertex_front"></a>

#### freestyle.types.Curve.push_vertex_front(vertex)

Adds a single vertex at the front of the Curve.

**Parameters:**

**vertex** ([`SVertex`](#freestyle.types.SVertex "freestyle.types.SVertex") | [`CurvePoint`](#freestyle.types.CurvePoint "freestyle.types.CurvePoint")) – A vertex object.

<a id="freestyle.types.Curve.is_empty"></a>

#### freestyle.types.Curve.is_empty

True if the Curve doesn’t have any Vertex yet.

**Type:**

bool

<a id="freestyle.types.Curve.segments_size"></a>

#### freestyle.types.Curve.segments_size

The number of segments in the polyline constituting the Curve.

**Type:**

int

<a id="freestyle.types.CurvePoint"></a>

### class freestyle.types.CurvePoint

Class hierarchy: [`Interface0D`](#freestyle.types.Interface0D "freestyle.types.Interface0D") > [`CurvePoint`](#freestyle.types.CurvePoint "freestyle.types.CurvePoint")

Class to represent a point of a curve. A CurvePoint can be any point
of a 1D curve (it doesn’t have to be a vertex of the curve). Any
[`Interface1D`](#freestyle.types.Interface1D "freestyle.types.Interface1D") is built upon ViewEdges, themselves built upon
FEdges. Therefore, a curve is basically a polyline made of a list of
[`SVertex`](#freestyle.types.SVertex "freestyle.types.SVertex") objects. Thus, a CurvePoint is built by linearly
interpolating two [`SVertex`](#freestyle.types.SVertex "freestyle.types.SVertex") instances. CurvePoint can be used
as virtual points while querying 0D information along a curve at a
given resolution.

<a id="freestyle.types.CurvePoint.__init__"></a>

#### freestyle.types.CurvePoint.__init__(*args)

Accepted call signatures:

- `__init__()`
- `__init__(brother)`
- `__init__(first_vertex, second_vertex, t2d)`
- `__init__(first_point, second_point, t2d)`

Builds a CurvePoint using the default constructor, copy constructor,
or one of the overloaded constructors. The over loaded constructors
can either take two [`SVertex`](#freestyle.types.SVertex "freestyle.types.SVertex") or two [`CurvePoint`](#freestyle.types.CurvePoint "freestyle.types.CurvePoint")
objects and an interpolation parameter

**Parameters:**

- **brother** ([`CurvePoint`](#freestyle.types.CurvePoint "freestyle.types.CurvePoint")) – A CurvePoint object.
- **first_vertex** ([`SVertex`](#freestyle.types.SVertex "freestyle.types.SVertex")) – The first SVertex.
- **second_vertex** ([`SVertex`](#freestyle.types.SVertex "freestyle.types.SVertex")) – The second SVertex.
- **first_point** ([`CurvePoint`](#freestyle.types.CurvePoint "freestyle.types.CurvePoint")) – The first CurvePoint.
- **second_point** ([`CurvePoint`](#freestyle.types.CurvePoint "freestyle.types.CurvePoint")) – The second CurvePoint.
- **t2d** (float) – A 2D interpolation parameter used to linearly interpolate
  first_vertex and second_vertex or first_point and second_point.

<a id="freestyle.types.CurvePoint.fedge"></a>

#### freestyle.types.CurvePoint.fedge

Gets the FEdge for the two SVertices that given CurvePoints consists out of.
A shortcut for CurvePoint.first_svertex.get_fedge(CurvePoint.second_svertex).

**Type:**

[`FEdge`](#freestyle.types.FEdge "freestyle.types.FEdge")

<a id="freestyle.types.CurvePoint.first_svertex"></a>

#### freestyle.types.CurvePoint.first_svertex

The first SVertex upon which the CurvePoint is built.

**Type:**

[`SVertex`](#freestyle.types.SVertex "freestyle.types.SVertex")

<a id="freestyle.types.CurvePoint.second_svertex"></a>

#### freestyle.types.CurvePoint.second_svertex

The second SVertex upon which the CurvePoint is built.

**Type:**

[`SVertex`](#freestyle.types.SVertex "freestyle.types.SVertex")

<a id="freestyle.types.CurvePoint.t2d"></a>

#### freestyle.types.CurvePoint.t2d

The 2D interpolation parameter.

**Type:**

float

<a id="freestyle.types.CurvePointIterator"></a>

### class freestyle.types.CurvePointIterator

Class hierarchy: [`Iterator`](#freestyle.types.Iterator "freestyle.types.Iterator") > [`CurvePointIterator`](#freestyle.types.CurvePointIterator "freestyle.types.CurvePointIterator")

Class representing an iterator on a curve. Allows an iterating
outside initial vertices. A CurvePoint is instantiated and returned
through the .object attribute.

<a id="freestyle.types.CurvePointIterator.__init__"></a>

#### freestyle.types.CurvePointIterator.__init__(*args, **kwargs)

Accepted call signatures:

- `__init__()`
- `__init__(brother)`
- `__init__(step=0.0)`

Builds a CurvePointIterator object using either the default constructor,
copy constructor, or the overloaded constructor.

**Parameters:**

- **brother** ([`CurvePointIterator`](#freestyle.types.CurvePointIterator "freestyle.types.CurvePointIterator")) – A CurvePointIterator object.
- **step** (float) – A resampling resolution with which the curve is resampled.
  If zero, no resampling is done (i.e., the iterator iterates over
  initial vertices).

<a id="freestyle.types.CurvePointIterator.object"></a>

#### freestyle.types.CurvePointIterator.object

The CurvePoint object currently pointed by this iterator.

**Type:**

[`CurvePoint`](#freestyle.types.CurvePoint "freestyle.types.CurvePoint")

<a id="freestyle.types.CurvePointIterator.t"></a>

#### freestyle.types.CurvePointIterator.t

The curvilinear abscissa of the current point.

**Type:**

float

<a id="freestyle.types.CurvePointIterator.u"></a>

#### freestyle.types.CurvePointIterator.u

The point parameter at the current point in the stroke (0 <= u <= 1).

**Type:**

float

<a id="freestyle.types.FEdge"></a>

### class freestyle.types.FEdge

Class hierarchy: [`Interface1D`](#freestyle.types.Interface1D "freestyle.types.Interface1D") > [`FEdge`](#freestyle.types.FEdge "freestyle.types.FEdge")

Base Class for feature edges. This FEdge can represent a silhouette,
a crease, a ridge/valley, a border or a suggestive contour. For
silhouettes, the FEdge is oriented so that the visible face lies on
the left of the edge. For borders, the FEdge is oriented so that the
face lies on the left of the edge. An FEdge can represent an initial
edge of the mesh or runs across a face of the initial mesh depending
on the smoothness or sharpness of the mesh. This class is specialized
into a smooth and a sharp version since their properties slightly vary
from one to the other.

<a id="freestyle.types.FEdge.FEdge"></a>

#### freestyle.types.FEdge.FEdge(*args)

Accepted call signatures:

- `FEdge()`
- `FEdge(brother)`

Builds an [`FEdge`](#freestyle.types.FEdge "freestyle.types.FEdge") using the default constructor,
copy constructor, or between two [`SVertex`](#freestyle.types.SVertex "freestyle.types.SVertex") objects.

**Parameters:**

- **brother** ([`FEdge`](#freestyle.types.FEdge "freestyle.types.FEdge")) – An FEdge object.
- **first_vertex** ([`SVertex`](#freestyle.types.SVertex "freestyle.types.SVertex")) – The first SVertex.
- **second_vertex** ([`SVertex`](#freestyle.types.SVertex "freestyle.types.SVertex")) – The second SVertex.

<a id="freestyle.types.FEdge.first_svertex"></a>

#### freestyle.types.FEdge.first_svertex

The first SVertex constituting this FEdge.

**Type:**

[`SVertex`](#freestyle.types.SVertex "freestyle.types.SVertex")

<a id="freestyle.types.FEdge.id"></a>

#### freestyle.types.FEdge.id

The Id of this FEdge.

**Type:**

[`Id`](#freestyle.types.Id "freestyle.types.Id")

<a id="freestyle.types.FEdge.is_smooth"></a>

#### freestyle.types.FEdge.is_smooth

True if this FEdge is a smooth FEdge.

**Type:**

bool

<a id="freestyle.types.FEdge.nature"></a>

#### freestyle.types.FEdge.nature

The nature of this FEdge.

**Type:**

[`Nature`](#freestyle.types.Nature "freestyle.types.Nature")

<a id="freestyle.types.FEdge.next_fedge"></a>

#### freestyle.types.FEdge.next_fedge

The FEdge following this one in the ViewEdge. The value is None if
this FEdge is the last of the ViewEdge.

**Type:**

[`FEdge`](#freestyle.types.FEdge "freestyle.types.FEdge")

<a id="freestyle.types.FEdge.previous_fedge"></a>

#### freestyle.types.FEdge.previous_fedge

The FEdge preceding this one in the ViewEdge. The value is None if
this FEdge is the first one of the ViewEdge.

**Type:**

[`FEdge`](#freestyle.types.FEdge "freestyle.types.FEdge")

<a id="freestyle.types.FEdge.second_svertex"></a>

#### freestyle.types.FEdge.second_svertex

The second SVertex constituting this FEdge.

**Type:**

[`SVertex`](#freestyle.types.SVertex "freestyle.types.SVertex")

<a id="freestyle.types.FEdge.viewedge"></a>

#### freestyle.types.FEdge.viewedge

The ViewEdge to which this FEdge belongs to.

**Type:**

[`ViewEdge`](#freestyle.types.ViewEdge "freestyle.types.ViewEdge")

Special Methods

<a id="freestyle.types.FEdge.__getitem__"></a>

#### freestyle.types.FEdge.__getitem__(key)

**Parameters:**

**key** (int) – Index or key.

**Return type:**

float

<a id="freestyle.types.FEdge.__len__"></a>

#### freestyle.types.FEdge.__len__()

**Return type:**

int

<a id="freestyle.types.FEdgeSharp"></a>

### class freestyle.types.FEdgeSharp

Class hierarchy: [`Interface1D`](#freestyle.types.Interface1D "freestyle.types.Interface1D") > [`FEdge`](#freestyle.types.FEdge "freestyle.types.FEdge") > [`FEdgeSharp`](#freestyle.types.FEdgeSharp "freestyle.types.FEdgeSharp")

Class defining a sharp FEdge. A Sharp FEdge corresponds to an initial
edge of the input mesh. It can be a silhouette, a crease or a border.
If it is a crease edge, then it is bordered by two faces of the mesh.
Face a lies on its right whereas Face b lies on its left. If it is a
border edge, then it doesn’t have any face on its right, and thus Face
a is None.

<a id="freestyle.types.FEdgeSharp.__init__"></a>

#### freestyle.types.FEdgeSharp.__init__(*args)

Accepted call signatures:

- `__init__()`
- `__init__(brother)`
- `__init__(first_vertex, second_vertex)`

Builds an [`FEdgeSharp`](#freestyle.types.FEdgeSharp "freestyle.types.FEdgeSharp") using the default constructor,
copy constructor, or between two [`SVertex`](#freestyle.types.SVertex "freestyle.types.SVertex") objects.

**Parameters:**

- **brother** ([`FEdgeSharp`](#freestyle.types.FEdgeSharp "freestyle.types.FEdgeSharp")) – An FEdgeSharp object.
- **first_vertex** ([`SVertex`](#freestyle.types.SVertex "freestyle.types.SVertex")) – The first SVertex object.
- **second_vertex** ([`SVertex`](#freestyle.types.SVertex "freestyle.types.SVertex")) – The second SVertex object.

<a id="freestyle.types.FEdgeSharp.face_mark_left"></a>

#### freestyle.types.FEdgeSharp.face_mark_left

The face mark of the face lying on the left of the FEdge.

**Type:**

bool

<a id="freestyle.types.FEdgeSharp.face_mark_right"></a>

#### freestyle.types.FEdgeSharp.face_mark_right

The face mark of the face lying on the right of the FEdge. If this FEdge
is a border, it has no face on the right and thus this property is set to
false.

**Type:**

bool

<a id="freestyle.types.FEdgeSharp.material_index_left"></a>

#### freestyle.types.FEdgeSharp.material_index_left

The index of the material of the face lying on the left of the FEdge.

**Type:**

int

<a id="freestyle.types.FEdgeSharp.material_index_right"></a>

#### freestyle.types.FEdgeSharp.material_index_right

The index of the material of the face lying on the right of the FEdge.
If this FEdge is a border, it has no Face on its right and therefore
no material.

**Type:**

int

<a id="freestyle.types.FEdgeSharp.material_left"></a>

#### freestyle.types.FEdgeSharp.material_left

The material of the face lying on the left of the FEdge.

**Type:**

[`Material`](#freestyle.types.Material "freestyle.types.Material")

<a id="freestyle.types.FEdgeSharp.material_right"></a>

#### freestyle.types.FEdgeSharp.material_right

The material of the face lying on the right of the FEdge. If this FEdge
is a border, it has no Face on its right and therefore no material.

**Type:**

[`Material`](#freestyle.types.Material "freestyle.types.Material")

<a id="freestyle.types.FEdgeSharp.normal_left"></a>

#### freestyle.types.FEdgeSharp.normal_left

The normal to the face lying on the left of the FEdge.

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="freestyle.types.FEdgeSharp.normal_right"></a>

#### freestyle.types.FEdgeSharp.normal_right

The normal to the face lying on the right of the FEdge. If this FEdge
is a border, it has no Face on its right and therefore no normal.

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="freestyle.types.FEdgeSmooth"></a>

### class freestyle.types.FEdgeSmooth

Class hierarchy: [`Interface1D`](#freestyle.types.Interface1D "freestyle.types.Interface1D") > [`FEdge`](#freestyle.types.FEdge "freestyle.types.FEdge") > [`FEdgeSmooth`](#freestyle.types.FEdgeSmooth "freestyle.types.FEdgeSmooth")

Class defining a smooth edge. This kind of edge typically runs across
a face of the input mesh. It can be a silhouette, a ridge or valley,
a suggestive contour.

<a id="freestyle.types.FEdgeSmooth.__init__"></a>

#### freestyle.types.FEdgeSmooth.__init__(*args)

Accepted call signatures:

- `__init__()`
- `__init__(brother)`
- `__init__(first_vertex, second_vertex)`

Builds an [`FEdgeSmooth`](#freestyle.types.FEdgeSmooth "freestyle.types.FEdgeSmooth") using the default constructor,
copy constructor, or between two [`SVertex`](#freestyle.types.SVertex "freestyle.types.SVertex").

**Parameters:**

- **brother** ([`FEdgeSmooth`](#freestyle.types.FEdgeSmooth "freestyle.types.FEdgeSmooth")) – An FEdgeSmooth object.
- **first_vertex** ([`SVertex`](#freestyle.types.SVertex "freestyle.types.SVertex")) – The first SVertex object.
- **second_vertex** ([`SVertex`](#freestyle.types.SVertex "freestyle.types.SVertex")) – The second SVertex object.

<a id="freestyle.types.FEdgeSmooth.face_mark"></a>

#### freestyle.types.FEdgeSmooth.face_mark

The face mark of the face that this FEdge is running across.

**Type:**

bool

<a id="freestyle.types.FEdgeSmooth.material"></a>

#### freestyle.types.FEdgeSmooth.material

The material of the face that this FEdge is running across.

**Type:**

[`Material`](#freestyle.types.Material "freestyle.types.Material")

<a id="freestyle.types.FEdgeSmooth.material_index"></a>

#### freestyle.types.FEdgeSmooth.material_index

The index of the material of the face that this FEdge is running across.

**Type:**

int

<a id="freestyle.types.FEdgeSmooth.normal"></a>

#### freestyle.types.FEdgeSmooth.normal

The normal of the face that this FEdge is running across.

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="freestyle.types.Id"></a>

### class freestyle.types.Id

Class for representing an object Id.

<a id="freestyle.types.Id.__init__"></a>

#### freestyle.types.Id.__init__(*args, **kwargs)

Accepted call signatures:

- `__init__(brother)`
- `__init__(first=0, second=0)`

Build the Id from two numbers or another [`Id`](#freestyle.types.Id "freestyle.types.Id") using the copy constructor.

**Parameters:**

- **brother** ([`Id`](#freestyle.types.Id "freestyle.types.Id")) – An Id object.
- **first** (int) – The first number.
- **second** (int) – The second number.

<a id="freestyle.types.Id.first"></a>

#### freestyle.types.Id.first

The first number constituting the Id.

**Type:**

int

<a id="freestyle.types.Id.second"></a>

#### freestyle.types.Id.second

The second number constituting the Id.

**Type:**

int

Special Methods

<a id="freestyle.types.Id.__eq__"></a>

#### freestyle.types.Id.__eq__(other)

**Parameters:**

**other** (object) – The other operand.

**Return type:**

bool

<a id="freestyle.types.Id.__ge__"></a>

#### freestyle.types.Id.__ge__(other)

**Parameters:**

**other** (Self) – The other operand.

**Return type:**

bool

<a id="freestyle.types.Id.__gt__"></a>

#### freestyle.types.Id.__gt__(other)

**Parameters:**

**other** (Self) – The other operand.

**Return type:**

bool

<a id="freestyle.types.Id.__le__"></a>

#### freestyle.types.Id.__le__(other)

**Parameters:**

**other** (Self) – The other operand.

**Return type:**

bool

<a id="freestyle.types.Id.__lt__"></a>

#### freestyle.types.Id.__lt__(other)

**Parameters:**

**other** (Self) – The other operand.

**Return type:**

bool

<a id="freestyle.types.Id.__ne__"></a>

#### freestyle.types.Id.__ne__(other)

**Parameters:**

**other** (object) – The other operand.

**Return type:**

bool

<a id="freestyle.types.Id.__repr__"></a>

#### freestyle.types.Id.__repr__()

**Return type:**

str

<a id="freestyle.types.IntegrationType"></a>

### class freestyle.types.IntegrationType

Class hierarchy: int > [`IntegrationType`](#freestyle.types.IntegrationType "freestyle.types.IntegrationType")

Different integration methods that can be invoked to integrate into a
single value the set of values obtained from each 0D element of an 1D
element.

<a id="freestyle.types.IntegrationType.MEAN"></a>

#### freestyle.types.IntegrationType.MEAN

The value computed for the 1D element is the mean of the values
obtained for the 0D elements.

<a id="freestyle.types.IntegrationType.MIN"></a>

#### freestyle.types.IntegrationType.MIN

The value computed for the 1D element is the minimum of the values
obtained for the 0D elements.

<a id="freestyle.types.IntegrationType.MAX"></a>

#### freestyle.types.IntegrationType.MAX

The value computed for the 1D element is the maximum of the values
obtained for the 0D elements.

<a id="freestyle.types.IntegrationType.FIRST"></a>

#### freestyle.types.IntegrationType.FIRST

The value computed for the 1D element is the first of the values
obtained for the 0D elements.

<a id="freestyle.types.IntegrationType.LAST"></a>

#### freestyle.types.IntegrationType.LAST

The value computed for the 1D element is the last of the values
obtained for the 0D elements.

<a id="freestyle.types.Interface0D"></a>

### class freestyle.types.Interface0D

Base class for any 0D element.

<a id="freestyle.types.Interface0D.__init__"></a>

#### freestyle.types.Interface0D.__init__()

Default constructor.

<a id="freestyle.types.Interface0D.get_fedge"></a>

#### freestyle.types.Interface0D.get_fedge(inter)

Returns the FEdge that lies between this 0D element and the 0D
element given as the argument.

**Parameters:**

**inter** ([`Interface0D`](#freestyle.types.Interface0D "freestyle.types.Interface0D")) – A 0D element.

**Returns:**

The FEdge lying between the two 0D elements.

**Return type:**

[`FEdge`](#freestyle.types.FEdge "freestyle.types.FEdge")

<a id="freestyle.types.Interface0D.id"></a>

#### freestyle.types.Interface0D.id

The Id of this 0D element.

**Type:**

[`Id`](#freestyle.types.Id "freestyle.types.Id")

<a id="freestyle.types.Interface0D.name"></a>

#### freestyle.types.Interface0D.name

The string of the name of this 0D element.

**Type:**

str

<a id="freestyle.types.Interface0D.nature"></a>

#### freestyle.types.Interface0D.nature

The nature of this 0D element.

**Type:**

[`Nature`](#freestyle.types.Nature "freestyle.types.Nature")

<a id="freestyle.types.Interface0D.point_2d"></a>

#### freestyle.types.Interface0D.point_2d

The 2D point of this 0D element.

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="freestyle.types.Interface0D.point_3d"></a>

#### freestyle.types.Interface0D.point_3d

The 3D point of this 0D element.

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="freestyle.types.Interface0D.projected_x"></a>

#### freestyle.types.Interface0D.projected_x

The X coordinate of the projected 3D point of this 0D element.

**Type:**

float

<a id="freestyle.types.Interface0D.projected_y"></a>

#### freestyle.types.Interface0D.projected_y

The Y coordinate of the projected 3D point of this 0D element.

**Type:**

float

<a id="freestyle.types.Interface0D.projected_z"></a>

#### freestyle.types.Interface0D.projected_z

The Z coordinate of the projected 3D point of this 0D element.

**Type:**

float

Special Methods

<a id="freestyle.types.Interface0D.__repr__"></a>

#### freestyle.types.Interface0D.__repr__()

**Return type:**

str

<a id="freestyle.types.Interface0DIterator"></a>

### class freestyle.types.Interface0DIterator

Class hierarchy: [`Iterator`](#freestyle.types.Iterator "freestyle.types.Iterator") > [`Interface0DIterator`](#freestyle.types.Interface0DIterator "freestyle.types.Interface0DIterator")

Class defining an iterator over Interface0D elements. An instance of
this iterator is always obtained from a 1D element.

<a id="freestyle.types.Interface0DIterator.__init__"></a>

#### freestyle.types.Interface0DIterator.__init__(*args)

Accepted call signatures:

- `__init__(brother)`
- `__init__(it)`

Construct a nested Interface0DIterator using either the copy constructor
or the constructor that takes an argument of a Function0D.

**Parameters:**

- **brother** ([`Interface0DIterator`](#freestyle.types.Interface0DIterator "freestyle.types.Interface0DIterator")) – An Interface0DIterator object.
- **it** ([`SVertexIterator`](#freestyle.types.SVertexIterator "freestyle.types.SVertexIterator") | [`CurvePointIterator`](#freestyle.types.CurvePointIterator "freestyle.types.CurvePointIterator") | [`StrokeVertexIterator`](#freestyle.types.StrokeVertexIterator "freestyle.types.StrokeVertexIterator")) – An iterator object to be nested.

<a id="freestyle.types.Interface0DIterator.at_last"></a>

#### freestyle.types.Interface0DIterator.at_last

True if the iterator points to the last valid element.
For its counterpart (pointing to the first valid element), use it.is_begin.

**Type:**

bool

<a id="freestyle.types.Interface0DIterator.object"></a>

#### freestyle.types.Interface0DIterator.object

The 0D object currently pointed to by this iterator. The object may be an
instance of [`Interface0D`](#freestyle.types.Interface0D "freestyle.types.Interface0D") or one of its subclasses. For example if
the iterator has been created from the vertices_begin() method of the
[`Stroke`](#freestyle.types.Stroke "freestyle.types.Stroke") class, the .object property refers to a [`StrokeVertex`](#freestyle.types.StrokeVertex "freestyle.types.StrokeVertex")
object.

**Type:**

[`Interface0D`](#freestyle.types.Interface0D "freestyle.types.Interface0D")

<a id="freestyle.types.Interface0DIterator.t"></a>

#### freestyle.types.Interface0DIterator.t

The curvilinear abscissa of the current point.

**Type:**

float

<a id="freestyle.types.Interface0DIterator.u"></a>

#### freestyle.types.Interface0DIterator.u

The point parameter at the current point in the 1D element (0 <= u <= 1).

**Type:**

float

Special Methods

<a id="freestyle.types.Interface0DIterator.__iter__"></a>

#### freestyle.types.Interface0DIterator.__iter__()

**Return type:**

[`Interface0DIterator`](#freestyle.types.Interface0DIterator "freestyle.types.Interface0DIterator")

<a id="freestyle.types.Interface0DIterator.__next__"></a>

#### freestyle.types.Interface0DIterator.__next__()

**Return type:**

Any

<a id="freestyle.types.Interface1D"></a>

### class freestyle.types.Interface1D

Base class for any 1D element.

<a id="freestyle.types.Interface1D.__init__"></a>

#### freestyle.types.Interface1D.__init__()

Default constructor.

<a id="freestyle.types.Interface1D.points_begin"></a>

#### freestyle.types.Interface1D.points_begin(t=0.0)

Returns an iterator over the Interface1D points, pointing to the
first point. The difference with vertices_begin() is that here we can
iterate over points of the 1D element at a any given sampling.
Indeed, for each iteration, a virtual point is created.

**Parameters:**

**t** (float) – A sampling with which we want to iterate over points of
this 1D element.

**Returns:**

An Interface0DIterator pointing to the first point.

**Return type:**

[`Interface0DIterator`](#freestyle.types.Interface0DIterator "freestyle.types.Interface0DIterator")

<a id="freestyle.types.Interface1D.points_end"></a>

#### freestyle.types.Interface1D.points_end(t=0.0)

Returns an iterator over the Interface1D points, pointing after the
last point. The difference with vertices_end() is that here we can
iterate over points of the 1D element at a given sampling. Indeed,
for each iteration, a virtual point is created.

**Parameters:**

**t** (float) – A sampling with which we want to iterate over points of
this 1D element.

**Returns:**

An Interface0DIterator pointing after the last point.

**Return type:**

[`Interface0DIterator`](#freestyle.types.Interface0DIterator "freestyle.types.Interface0DIterator")

<a id="freestyle.types.Interface1D.vertices_begin"></a>

#### freestyle.types.Interface1D.vertices_begin()

Returns an iterator over the Interface1D vertices, pointing to the
first vertex.

**Returns:**

An Interface0DIterator pointing to the first vertex.

**Return type:**

[`Interface0DIterator`](#freestyle.types.Interface0DIterator "freestyle.types.Interface0DIterator")

<a id="freestyle.types.Interface1D.vertices_end"></a>

#### freestyle.types.Interface1D.vertices_end()

Returns an iterator over the Interface1D vertices, pointing after
the last vertex.

**Returns:**

An Interface0DIterator pointing after the last vertex.

**Return type:**

[`Interface0DIterator`](#freestyle.types.Interface0DIterator "freestyle.types.Interface0DIterator")

<a id="freestyle.types.Interface1D.id"></a>

#### freestyle.types.Interface1D.id

The Id of this Interface1D.

**Type:**

[`Id`](#freestyle.types.Id "freestyle.types.Id")

<a id="freestyle.types.Interface1D.length_2d"></a>

#### freestyle.types.Interface1D.length_2d

The 2D length of this Interface1D.

**Type:**

float

<a id="freestyle.types.Interface1D.name"></a>

#### freestyle.types.Interface1D.name

The string of the name of the 1D element.

**Type:**

str

<a id="freestyle.types.Interface1D.nature"></a>

#### freestyle.types.Interface1D.nature

The nature of this Interface1D.

**Type:**

[`Nature`](#freestyle.types.Nature "freestyle.types.Nature")

<a id="freestyle.types.Interface1D.time_stamp"></a>

#### freestyle.types.Interface1D.time_stamp

The time stamp of the 1D element, mainly used for selection.

**Type:**

int

Special Methods

<a id="freestyle.types.Interface1D.__repr__"></a>

#### freestyle.types.Interface1D.__repr__()

**Return type:**

str

<a id="freestyle.types.Iterator"></a>

### class freestyle.types.Iterator

Base class to define iterators.

<a id="freestyle.types.Iterator.__init__"></a>

#### freestyle.types.Iterator.__init__()

Default constructor.

<a id="freestyle.types.Iterator.decrement"></a>

#### freestyle.types.Iterator.decrement()

Makes the iterator point the previous element.

<a id="freestyle.types.Iterator.increment"></a>

#### freestyle.types.Iterator.increment()

Makes the iterator point the next element.

<a id="freestyle.types.Iterator.is_begin"></a>

#### freestyle.types.Iterator.is_begin

True if the iterator points to the first element.

**Type:**

bool

<a id="freestyle.types.Iterator.is_end"></a>

#### freestyle.types.Iterator.is_end

True if the iterator points to the last element.

**Type:**

bool

<a id="freestyle.types.Iterator.name"></a>

#### freestyle.types.Iterator.name

The string of the name of this iterator.

**Type:**

str

Special Methods

<a id="freestyle.types.Iterator.__repr__"></a>

#### freestyle.types.Iterator.__repr__()

**Return type:**

str

<a id="freestyle.types.Material"></a>

### class freestyle.types.Material

Class defining a material.

<a id="freestyle.types.Material.__init__"></a>

#### freestyle.types.Material.__init__(*args)

Accepted call signatures:

- `__init__()`
- `__init__(brother)`
- `__init__(line, diffuse, ambient, specular, emission, shininess, priority)`

Creates a `FrsMaterial` using either default constructor,
copy constructor, or an overloaded constructor

**Parameters:**

- **brother** ([`Material`](#freestyle.types.Material "freestyle.types.Material")) – A Material object to be used as a copy constructor.
- **line** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | tuple[float, float, float, float] | list[float]) – The line color.
- **diffuse** – The diffuse color.
- **ambient** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | tuple[float, float, float, float] | list[float]) – The ambient color.
- **specular** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | tuple[float, float, float, float] | list[float]) – The specular color.
- **emission** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | tuple[float, float, float, float] | list[float]) – The emissive color.
- **shininess** (float) – The shininess coefficient.
- **priority** (int) – The line color priority.

<a id="freestyle.types.Material.ambient"></a>

#### freestyle.types.Material.ambient

RGBA components of the ambient color of the material.

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="freestyle.types.Material.diffuse"></a>

#### freestyle.types.Material.diffuse

RGBA components of the diffuse color of the material.

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="freestyle.types.Material.emission"></a>

#### freestyle.types.Material.emission

RGBA components of the emissive color of the material.

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="freestyle.types.Material.line"></a>

#### freestyle.types.Material.line

RGBA components of the line color of the material.

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="freestyle.types.Material.priority"></a>

#### freestyle.types.Material.priority

Line color priority of the material.

**Type:**

int

<a id="freestyle.types.Material.shininess"></a>

#### freestyle.types.Material.shininess

Shininess coefficient of the material.

**Type:**

float

<a id="freestyle.types.Material.specular"></a>

#### freestyle.types.Material.specular

RGBA components of the specular color of the material.

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

Special Methods

<a id="freestyle.types.Material.__eq__"></a>

#### freestyle.types.Material.__eq__(other)

**Parameters:**

**other** (object) – The other operand.

**Return type:**

bool

<a id="freestyle.types.Material.__ge__"></a>

#### freestyle.types.Material.__ge__(other)

**Parameters:**

**other** (Self) – The other operand.

**Return type:**

bool

<a id="freestyle.types.Material.__gt__"></a>

#### freestyle.types.Material.__gt__(other)

**Parameters:**

**other** (Self) – The other operand.

**Return type:**

bool

<a id="freestyle.types.Material.__hash__"></a>

#### freestyle.types.Material.__hash__()

**Return type:**

int

<a id="freestyle.types.Material.__le__"></a>

#### freestyle.types.Material.__le__(other)

**Parameters:**

**other** (Self) – The other operand.

**Return type:**

bool

<a id="freestyle.types.Material.__lt__"></a>

#### freestyle.types.Material.__lt__(other)

**Parameters:**

**other** (Self) – The other operand.

**Return type:**

bool

<a id="freestyle.types.Material.__ne__"></a>

#### freestyle.types.Material.__ne__(other)

**Parameters:**

**other** (object) – The other operand.

**Return type:**

bool

<a id="freestyle.types.Material.__repr__"></a>

#### freestyle.types.Material.__repr__()

**Return type:**

str

<a id="freestyle.types.MediumType"></a>

### class freestyle.types.MediumType

Class hierarchy: int > [`MediumType`](#freestyle.types.MediumType "freestyle.types.MediumType")

The different blending modes available to simulate the interaction
media-medium:

- Stroke.DRY_MEDIUM: To simulate a dry medium such as Pencil or Charcoal.
- Stroke.HUMID_MEDIUM: To simulate ink painting (color subtraction blending).
- Stroke.OPAQUE_MEDIUM: To simulate an opaque medium (oil, spray…).

<a id="freestyle.types.Nature"></a>

### class freestyle.types.Nature

Class hierarchy: int > [`Nature`](#freestyle.types.Nature "freestyle.types.Nature")

Different possible natures of 0D and 1D elements of the ViewMap.

Vertex natures:

<a id="freestyle.types.Nature.POINT"></a>

#### freestyle.types.Nature.POINT

True for any 0D element.

<a id="freestyle.types.Nature.S_VERTEX"></a>

#### freestyle.types.Nature.S_VERTEX

True for SVertex.

<a id="freestyle.types.Nature.VIEW_VERTEX"></a>

#### freestyle.types.Nature.VIEW_VERTEX

True for ViewVertex.

<a id="freestyle.types.Nature.NON_T_VERTEX"></a>

#### freestyle.types.Nature.NON_T_VERTEX

True for NonTVertex.

<a id="freestyle.types.Nature.T_VERTEX"></a>

#### freestyle.types.Nature.T_VERTEX

True for TVertex.

<a id="freestyle.types.Nature.CUSP"></a>

#### freestyle.types.Nature.CUSP

True for CUSP.

Edge natures:

<a id="freestyle.types.Nature.NO_FEATURE"></a>

#### freestyle.types.Nature.NO_FEATURE

True for non feature edges (always false for 1D elements of the ViewMap).

<a id="freestyle.types.Nature.SILHOUETTE"></a>

#### freestyle.types.Nature.SILHOUETTE

True for silhouettes.

<a id="freestyle.types.Nature.BORDER"></a>

#### freestyle.types.Nature.BORDER

True for borders.

<a id="freestyle.types.Nature.CREASE"></a>

#### freestyle.types.Nature.CREASE

True for creases.

<a id="freestyle.types.Nature.RIDGE"></a>

#### freestyle.types.Nature.RIDGE

True for ridges.

<a id="freestyle.types.Nature.VALLEY"></a>

#### freestyle.types.Nature.VALLEY

True for valleys.

<a id="freestyle.types.Nature.SUGGESTIVE_CONTOUR"></a>

#### freestyle.types.Nature.SUGGESTIVE_CONTOUR

True for suggestive contours.

<a id="freestyle.types.Nature.MATERIAL_BOUNDARY"></a>

#### freestyle.types.Nature.MATERIAL_BOUNDARY

True for edges at material boundaries.

<a id="freestyle.types.Nature.EDGE_MARK"></a>

#### freestyle.types.Nature.EDGE_MARK

True for edges having user-defined edge marks.

<a id="freestyle.types.Noise"></a>

### class freestyle.types.Noise

Class to provide Perlin noise functionalities.

<a id="freestyle.types.Noise.__init__"></a>

#### freestyle.types.Noise.__init__(seed=-1)

Builds a Noise object. Seed is an optional argument. The seed value is used
as a seed for random number generation if it is equal to or greater than zero;
otherwise, time is used as a seed.

**Parameters:**

**seed** (int) – Seed for random number generation.

Undocumented, consider [contributing](https://developer.blender.org/).

<a id="freestyle.types.Noise.smoothNoise1"></a>

#### freestyle.types.Noise.smoothNoise1(v)

Returns a smooth noise value for a 1D element.

**Parameters:**

**v** (float) – One-dimensional sample point.

**Returns:**

A smooth noise value.

**Return type:**

float

<a id="freestyle.types.Noise.smoothNoise2"></a>

#### freestyle.types.Noise.smoothNoise2(v)

Returns a smooth noise value for a 2D element.

**Parameters:**

**v** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | tuple[float, float] | list[float]) – Two-dimensional sample point.

**Returns:**

A smooth noise value.

**Return type:**

float

<a id="freestyle.types.Noise.smoothNoise3"></a>

#### freestyle.types.Noise.smoothNoise3(v)

Returns a smooth noise value for a 3D element.

**Parameters:**

**v** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | tuple[float, float, float] | list[float]) – Three-dimensional sample point.

**Returns:**

A smooth noise value.

**Return type:**

float

<a id="freestyle.types.Noise.turbulence1"></a>

#### freestyle.types.Noise.turbulence1(v, freq, amp, oct=4)

Returns a noise value for a 1D element.

**Parameters:**

- **v** (float) – One-dimensional sample point.
- **freq** (float) – Noise frequency.
- **amp** (float) – Amplitude.
- **oct** (int) – Number of octaves.

**Returns:**

A noise value.

**Return type:**

float

<a id="freestyle.types.Noise.turbulence2"></a>

#### freestyle.types.Noise.turbulence2(v, freq, amp, oct=4)

Returns a noise value for a 2D element.

**Parameters:**

- **v** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | tuple[float, float] | list[float]) – Two-dimensional sample point.
- **freq** (float) – Noise frequency.
- **amp** (float) – Amplitude.
- **oct** (int) – Number of octaves.

**Returns:**

A noise value.

**Return type:**

float

<a id="freestyle.types.Noise.turbulence3"></a>

#### freestyle.types.Noise.turbulence3(v, freq, amp, oct=4)

Returns a noise value for a 3D element.

**Parameters:**

- **v** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | tuple[float, float, float] | list[float]) – Three-dimensional sample point.
- **freq** (float) – Noise frequency.
- **amp** (float) – Amplitude.
- **oct** (int) – Number of octaves.

**Returns:**

A noise value.

**Return type:**

float

Undocumented, consider [contributing](https://developer.blender.org/).

Special Methods

<a id="freestyle.types.Noise.__repr__"></a>

#### freestyle.types.Noise.__repr__()

**Return type:**

str

<a id="freestyle.types.NonTVertex"></a>

### class freestyle.types.NonTVertex

Class hierarchy: [`Interface0D`](#freestyle.types.Interface0D "freestyle.types.Interface0D") > [`ViewVertex`](#freestyle.types.ViewVertex "freestyle.types.ViewVertex") > [`NonTVertex`](#freestyle.types.NonTVertex "freestyle.types.NonTVertex")

View vertex for corners, cusps, etc. associated to a single SVertex.
Can be associated to 2 or more view edges.

<a id="freestyle.types.NonTVertex.__init__"></a>

#### freestyle.types.NonTVertex.__init__(*args)

Accepted call signatures:

- `__init__()`
- `__init__(svertex)`

Builds a [`NonTVertex`](#freestyle.types.NonTVertex "freestyle.types.NonTVertex") using the default constructor or a [`SVertex`](#freestyle.types.SVertex "freestyle.types.SVertex").

**Parameters:**

**svertex** ([`SVertex`](#freestyle.types.SVertex "freestyle.types.SVertex")) – An SVertex object.

<a id="freestyle.types.NonTVertex.svertex"></a>

#### freestyle.types.NonTVertex.svertex

The SVertex on top of which this NonTVertex is built.

**Type:**

[`SVertex`](#freestyle.types.SVertex "freestyle.types.SVertex")

<a id="freestyle.types.Operators"></a>

### class freestyle.types.Operators

Class defining the operators used in a style module. There are five
types of operators: Selection, chaining, splitting, sorting and
creation. All these operators are user controlled through functors,
predicates and shaders that are taken as arguments.

<a id="freestyle.types.Operators.bidirectional_chain"></a>

#### static freestyle.types.Operators.bidirectional_chain(*args)

Accepted call signatures:

- `bidirectional_chain(it, pred)`
- `bidirectional_chain(it)`

Builds a set of chains from the current set of ViewEdges. Each
ViewEdge of the current list potentially starts a new chain. The
chaining operator then iterates over the ViewEdges of the ViewMap
using the user specified iterator. This operator iterates both using
the increment and decrement operators and is therefore bidirectional.
This operator works with a ChainingIterator which contains the
chaining rules. It is this last one which can be told to chain only
edges that belong to the selection or not to process twice a ViewEdge
during the chaining. Each time a ViewEdge is added to a chain, its
chaining time stamp is incremented. This allows you to keep track of
the number of chains to which a ViewEdge belongs to.

**Parameters:**

- **it** ([`ChainingIterator`](#freestyle.types.ChainingIterator "freestyle.types.ChainingIterator")) – The ChainingIterator on the ViewEdges of the ViewMap. It
  contains the chaining rule.
- **pred** ([`UnaryPredicate1D`](#freestyle.types.UnaryPredicate1D "freestyle.types.UnaryPredicate1D")) – The predicate on the ViewEdge that expresses the stopping condition.
  This parameter is optional, you make not want to pass a stopping criterion
  when the stopping criterion is already contained in the iterator definition.

<a id="freestyle.types.Operators.chain"></a>

#### static freestyle.types.Operators.chain(*args)

Accepted call signatures:

- `chain(it, pred, modifier)`
- `chain(it, pred)`

Builds a set of chains from the current set of ViewEdges. Each
ViewEdge of the current list starts a new chain. The chaining
operator then iterates over the ViewEdges of the ViewMap using the
user specified iterator. This operator only iterates using the
increment operator and is therefore unidirectional.

**Parameters:**

- **it** ([`ViewEdgeIterator`](#freestyle.types.ViewEdgeIterator "freestyle.types.ViewEdgeIterator")) – The iterator on the ViewEdges of the ViewMap. It contains
  the chaining rule.
- **pred** ([`UnaryPredicate1D`](#freestyle.types.UnaryPredicate1D "freestyle.types.UnaryPredicate1D")) – The predicate on the ViewEdge that expresses the
  stopping condition.
- **modifier** ([`UnaryFunction1DVoid`](#freestyle.types.UnaryFunction1DVoid "freestyle.types.UnaryFunction1DVoid")) – A function that takes a ViewEdge as argument and
  that is used to modify the processed ViewEdge state (the
  timestamp incrementation is a typical illustration of such a modifier).
  If this argument is not given, the time stamp is automatically managed.

<a id="freestyle.types.Operators.create"></a>

#### static freestyle.types.Operators.create(pred, shaders)

Creates and shades the strokes from the current set of chains. A
predicate can be specified to make a selection pass on the chains.

**Parameters:**

- **pred** ([`UnaryPredicate1D`](#freestyle.types.UnaryPredicate1D "freestyle.types.UnaryPredicate1D")) – The predicate that a chain must verify in order to be
  transform as a stroke.
- **shaders** (list[[`StrokeShader`](#freestyle.types.StrokeShader "freestyle.types.StrokeShader")]) – The list of shaders used to shade the strokes.

<a id="freestyle.types.Operators.get_chain_from_index"></a>

#### static freestyle.types.Operators.get_chain_from_index(i)

Returns the Chain at the index in the current set of Chains.

**Parameters:**

**i** (int) – index (0 <= i < Operators.get_chains_size()).

**Returns:**

The Chain object.

**Return type:**

[`Chain`](#freestyle.types.Chain "freestyle.types.Chain")

<a id="freestyle.types.Operators.get_chains_size"></a>

#### static freestyle.types.Operators.get_chains_size()

Returns the number of Chains.

**Returns:**

The number of Chains.

**Return type:**

int

<a id="freestyle.types.Operators.get_stroke_from_index"></a>

#### static freestyle.types.Operators.get_stroke_from_index(i)

Returns the Stroke at the index in the current set of Strokes.

**Parameters:**

**i** (int) – index (0 <= i < Operators.get_strokes_size()).

**Returns:**

The Stroke object.

**Return type:**

[`Stroke`](#freestyle.types.Stroke "freestyle.types.Stroke")

<a id="freestyle.types.Operators.get_strokes_size"></a>

#### static freestyle.types.Operators.get_strokes_size()

Returns the number of Strokes.

**Returns:**

The number of Strokes.

**Return type:**

int

<a id="freestyle.types.Operators.get_view_edges_size"></a>

#### static freestyle.types.Operators.get_view_edges_size()

Returns the number of ViewEdges.

**Returns:**

The number of ViewEdges.

**Return type:**

int

<a id="freestyle.types.Operators.get_viewedge_from_index"></a>

#### static freestyle.types.Operators.get_viewedge_from_index(i)

Returns the ViewEdge at the index in the current set of ViewEdges.

**Parameters:**

**i** (int) – index (0 <= i < Operators.get_view_edges_size()).

**Returns:**

The ViewEdge object.

**Return type:**

[`ViewEdge`](#freestyle.types.ViewEdge "freestyle.types.ViewEdge")

<a id="freestyle.types.Operators.recursive_split"></a>

#### static freestyle.types.Operators.recursive_split(*args, **kwargs)

Accepted call signatures:

- `recursive_split(func, pred_1d, sampling=0.0)`
- `recursive_split(func, pred_0d, pred_1d, sampling=0.0)`

Splits the current set of chains in a recursive way. We process the
points of each chain (with a specified sampling) to find the point
minimizing a specified function. The chain is split in two at this
point and the two new chains are processed in the same way. The
recursivity level is controlled through a predicate 1D that expresses
a stopping condition on the chain that is about to be processed.

The user can also specify a 0D predicate to make a first selection on the points
that can potentially be split. A point that doesn’t verify the 0D
predicate won’t be candidate in realizing the min.

**Parameters:**

- **func** ([`UnaryFunction0DDouble`](#freestyle.types.UnaryFunction0DDouble "freestyle.types.UnaryFunction0DDouble")) – The Unary Function evaluated at each point of the chain.
  The splitting point is the point minimizing this function.
- **pred_0d** ([`UnaryPredicate0D`](#freestyle.types.UnaryPredicate0D "freestyle.types.UnaryPredicate0D")) – The Unary Predicate 0D used to select the candidate
  points where the split can occur. For example, it is very likely
  that would rather have your chain splitting around its middle
  point than around one of its extremities. A 0D predicate working
  on the curvilinear abscissa allows to add this kind of constraints.
- **pred_1d** ([`UnaryPredicate1D`](#freestyle.types.UnaryPredicate1D "freestyle.types.UnaryPredicate1D")) – The Unary Predicate expressing the recursivity stopping
  condition. This predicate is evaluated for each curve before it
  actually gets split. If pred_1d(chain) is true, the curve won’t be
  split anymore.
- **sampling** (float) – The resolution used to sample the chain for the
  predicates evaluation. (The chain is not actually resampled; a
  virtual point only progresses along the curve using this
  resolution.)

<a id="freestyle.types.Operators.reset"></a>

#### static freestyle.types.Operators.reset(delete_strokes=True)

Resets the line stylization process to the initial state. The results of
stroke creation are accumulated if **delete_strokes** is set to False.

**Parameters:**

**delete_strokes** (bool) – Delete the strokes that are currently stored.

<a id="freestyle.types.Operators.select"></a>

#### static freestyle.types.Operators.select(pred)

Selects the ViewEdges of the ViewMap verifying a specified
condition.

**Parameters:**

**pred** ([`UnaryPredicate1D`](#freestyle.types.UnaryPredicate1D "freestyle.types.UnaryPredicate1D")) – The predicate expressing this condition.

<a id="freestyle.types.Operators.sequential_split"></a>

#### static freestyle.types.Operators.sequential_split(*args, **kwargs)

Accepted call signatures:

- `sequential_split(starting_pred, stopping_pred, sampling=0.0)`
- `sequential_split(pred, sampling=0.0)`

Splits each chain of the current set of chains in a sequential way.
The points of each chain are processed (with a specified sampling)
sequentially. The first point of the initial chain is the
first point of one of the resulting chains. The splitting ends when
no more chain can start.

> **Tip:**
>
> By specifying a starting and stopping predicate allows
> the chains to overlap rather than chains partitioning.

**Parameters:**

- **starting_pred** ([`UnaryPredicate0D`](#freestyle.types.UnaryPredicate0D "freestyle.types.UnaryPredicate0D")) – The predicate on a point that expresses the
  starting condition. Each time this condition is verified, a new chain begins
- **stopping_pred** ([`UnaryPredicate0D`](#freestyle.types.UnaryPredicate0D "freestyle.types.UnaryPredicate0D")) – The predicate on a point that expresses the
  stopping condition. The chain ends as soon as this predicate is verified.
- **pred** ([`UnaryPredicate0D`](#freestyle.types.UnaryPredicate0D "freestyle.types.UnaryPredicate0D")) – The predicate on a point that expresses the splitting condition.
  Each time the condition is verified, the chain is split into two chains.
  The resulting set of chains is a partition of the initial chain
- **sampling** (float) – The resolution used to sample the chain for the
  predicates evaluation. (The chain is not actually resampled;
  a virtual point only progresses along the curve using this
  resolution.)

<a id="freestyle.types.Operators.sort"></a>

#### static freestyle.types.Operators.sort(pred)

Sorts the current set of chains (or viewedges) according to the
comparison predicate given as argument.

**Parameters:**

**pred** ([`BinaryPredicate1D`](#freestyle.types.BinaryPredicate1D "freestyle.types.BinaryPredicate1D")) – The binary predicate used for the comparison.

<a id="freestyle.types.SShape"></a>

### class freestyle.types.SShape

Class to define a feature shape. It is the gathering of feature
elements from an identified input shape.

<a id="freestyle.types.SShape.__init__"></a>

#### freestyle.types.SShape.__init__(*args)

Accepted call signatures:

- `__init__()`
- `__init__(brother)`

Creates a [`SShape`](#freestyle.types.SShape "freestyle.types.SShape") class using either a default constructor or copy constructor.

**Parameters:**

**brother** ([`SShape`](#freestyle.types.SShape "freestyle.types.SShape")) – An SShape object.

<a id="freestyle.types.SShape.add_edge"></a>

#### freestyle.types.SShape.add_edge(edge)

Adds an FEdge to the list of FEdges.

**Parameters:**

**edge** ([`FEdge`](#freestyle.types.FEdge "freestyle.types.FEdge")) – An FEdge object.

<a id="freestyle.types.SShape.add_vertex"></a>

#### freestyle.types.SShape.add_vertex(vertex)

Adds an SVertex to the list of SVertex of this Shape. The SShape
attribute of the SVertex is also set to this SShape.

**Parameters:**

**vertex** ([`SVertex`](#freestyle.types.SVertex "freestyle.types.SVertex")) – An SVertex object.

<a id="freestyle.types.SShape.compute_bbox"></a>

#### freestyle.types.SShape.compute_bbox()

Compute the bbox of the SShape.

<a id="freestyle.types.SShape.bbox"></a>

#### freestyle.types.SShape.bbox

The bounding box of the SShape.

**Type:**

[`BBox`](#freestyle.types.BBox "freestyle.types.BBox")

<a id="freestyle.types.SShape.edges"></a>

#### freestyle.types.SShape.edges

The list of edges constituting this SShape.

**Type:**

list[[`FEdge`](#freestyle.types.FEdge "freestyle.types.FEdge")]

<a id="freestyle.types.SShape.id"></a>

#### freestyle.types.SShape.id

The Id of this SShape.

**Type:**

[`Id`](#freestyle.types.Id "freestyle.types.Id")

<a id="freestyle.types.SShape.name"></a>

#### freestyle.types.SShape.name

The name of the SShape.

**Type:**

str

<a id="freestyle.types.SShape.vertices"></a>

#### freestyle.types.SShape.vertices

The list of vertices constituting this SShape.

**Type:**

list[[`SVertex`](#freestyle.types.SVertex "freestyle.types.SVertex")]

Special Methods

<a id="freestyle.types.SShape.__repr__"></a>

#### freestyle.types.SShape.__repr__()

**Return type:**

str

<a id="freestyle.types.SVertex"></a>

### class freestyle.types.SVertex

Class hierarchy: [`Interface0D`](#freestyle.types.Interface0D "freestyle.types.Interface0D") > [`SVertex`](#freestyle.types.SVertex "freestyle.types.SVertex")

Class to define a vertex of the embedding.

<a id="freestyle.types.SVertex.__init__"></a>

#### freestyle.types.SVertex.__init__(*args)

Accepted call signatures:

- `__init__()`
- `__init__(brother)`
- `__init__(point_3d, id)`

Builds a [`SVertex`](#freestyle.types.SVertex "freestyle.types.SVertex") using the default constructor,
copy constructor or the overloaded constructor which builds a [`SVertex`](#freestyle.types.SVertex "freestyle.types.SVertex") from 3D coordinates and an Id.

**Parameters:**

- **brother** ([`SVertex`](#freestyle.types.SVertex "freestyle.types.SVertex")) – A SVertex object.
- **point_3d** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – A three-dimensional vector.
- **id** ([`Id`](#freestyle.types.Id "freestyle.types.Id")) – An Id object.

<a id="freestyle.types.SVertex.add_fedge"></a>

#### freestyle.types.SVertex.add_fedge(fedge)

Add an FEdge to the list of edges emanating from this SVertex.

**Parameters:**

**fedge** ([`FEdge`](#freestyle.types.FEdge "freestyle.types.FEdge")) – An FEdge.

<a id="freestyle.types.SVertex.add_normal"></a>

#### freestyle.types.SVertex.add_normal(normal)

Adds a normal to the SVertex’s set of normals. If the same normal
is already in the set, nothing changes.

**Parameters:**

**normal** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | tuple[float, float, float] | list[float]) – A three-dimensional vector.

<a id="freestyle.types.SVertex.curvatures"></a>

#### freestyle.types.SVertex.curvatures

Curvature information expressed in the form of a seven-element tuple
(K1, e1, K2, e2, Kr, er, dKr), where K1 and K2 are scalar values
representing the first (maximum) and second (minimum) principal
curvatures at this SVertex, respectively; e1 and e2 are
three-dimensional vectors representing the first and second principal
directions, i.e. the directions of the normal plane where the
curvature takes its maximum and minimum values, respectively; and Kr,
er and dKr are the radial curvature, radial direction, and the
derivative of the radial curvature at this SVertex, respectively.

**Type:**

tuple

<a id="freestyle.types.SVertex.id"></a>

#### freestyle.types.SVertex.id

The Id of this SVertex.

**Type:**

[`Id`](#freestyle.types.Id "freestyle.types.Id")

<a id="freestyle.types.SVertex.normals"></a>

#### freestyle.types.SVertex.normals

The normals for this Vertex as a list. In a sharp surface, an SVertex
has exactly one normal. In a smooth surface, an SVertex can have any
number of normals.

**Type:**

list[[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")]

<a id="freestyle.types.SVertex.normals_size"></a>

#### freestyle.types.SVertex.normals_size

The number of different normals for this SVertex.

**Type:**

int

<a id="freestyle.types.SVertex.point_2d"></a>

#### freestyle.types.SVertex.point_2d

The projected 3D coordinates of the SVertex.

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="freestyle.types.SVertex.point_3d"></a>

#### freestyle.types.SVertex.point_3d

The 3D coordinates of the SVertex.

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="freestyle.types.SVertex.viewvertex"></a>

#### freestyle.types.SVertex.viewvertex

If this SVertex is also a ViewVertex, this property refers to the
ViewVertex, and None otherwise.

**Type:**

[`ViewVertex`](#freestyle.types.ViewVertex "freestyle.types.ViewVertex")

<a id="freestyle.types.SVertexIterator"></a>

### class freestyle.types.SVertexIterator

Class hierarchy: [`Iterator`](#freestyle.types.Iterator "freestyle.types.Iterator") > [`SVertexIterator`](#freestyle.types.SVertexIterator "freestyle.types.SVertexIterator")

Class representing an iterator over [`SVertex`](#freestyle.types.SVertex "freestyle.types.SVertex") of a
[`ViewEdge`](#freestyle.types.ViewEdge "freestyle.types.ViewEdge"). An instance of an SVertexIterator can be obtained
from a ViewEdge by calling verticesBegin() or verticesEnd().

<a id="freestyle.types.SVertexIterator.__init__"></a>

#### freestyle.types.SVertexIterator.__init__(*args)

Accepted call signatures:

- `__init__()`
- `__init__(brother)`
- `__init__(vertex, begin, previous_edge, next_edge, t)`

Build an SVertexIterator using either the default constructor, copy constructor,
or the overloaded constructor that starts iteration from an SVertex object vertex.

**Parameters:**

- **brother** ([`SVertexIterator`](#freestyle.types.SVertexIterator "freestyle.types.SVertexIterator")) – An SVertexIterator object.
- **vertex** ([`SVertex`](#freestyle.types.SVertex "freestyle.types.SVertex")) – The SVertex from which the iterator starts iteration.
- **begin** ([`SVertex`](#freestyle.types.SVertex "freestyle.types.SVertex")) – The first SVertex of a ViewEdge.
- **previous_edge** ([`FEdge`](#freestyle.types.FEdge "freestyle.types.FEdge")) – The previous FEdge coming to vertex.
- **next_edge** ([`FEdge`](#freestyle.types.FEdge "freestyle.types.FEdge")) – The next FEdge going out from vertex.
- **t** (float) – The curvilinear abscissa at vertex.

<a id="freestyle.types.SVertexIterator.object"></a>

#### freestyle.types.SVertexIterator.object

The SVertex object currently pointed by this iterator.

**Type:**

[`SVertex`](#freestyle.types.SVertex "freestyle.types.SVertex")

<a id="freestyle.types.SVertexIterator.t"></a>

#### freestyle.types.SVertexIterator.t

The curvilinear abscissa of the current point.

**Type:**

float

<a id="freestyle.types.SVertexIterator.u"></a>

#### freestyle.types.SVertexIterator.u

The point parameter at the current point in the 1D element (0 <= u <= 1).

**Type:**

float

<a id="freestyle.types.Stroke"></a>

### class freestyle.types.Stroke

Class hierarchy: [`Interface1D`](#freestyle.types.Interface1D "freestyle.types.Interface1D") > [`Stroke`](#freestyle.types.Stroke "freestyle.types.Stroke")

Class to define a stroke. A stroke is made of a set of 2D vertices
([`StrokeVertex`](#freestyle.types.StrokeVertex "freestyle.types.StrokeVertex")), regularly spaced out. This set of vertices
defines the stroke’s backbone geometry. Each of these stroke vertices
defines the stroke’s shape and appearance at this vertex position.

<a id="freestyle.types.Stroke.Stroke"></a>

#### freestyle.types.Stroke.Stroke(*args)

Accepted call signatures:

- `Stroke()`
- `Stroke(brother)`

Creates a [`Stroke`](#freestyle.types.Stroke "freestyle.types.Stroke") using the default constructor or copy constructor

<a id="freestyle.types.Stroke.compute_sampling"></a>

#### freestyle.types.Stroke.compute_sampling(n)

Compute the sampling needed to get N vertices. If the
specified number of vertices is less than the actual number of
vertices, the actual sampling value is returned. (To remove Vertices,
use the RemoveVertex() method of this class.)

**Parameters:**

**n** (int) – The number of stroke vertices we eventually want
in our Stroke.

**Returns:**

The sampling that must be used in the Resample(float)
method.

**Return type:**

float

<a id="freestyle.types.Stroke.insert_vertex"></a>

#### freestyle.types.Stroke.insert_vertex(vertex, next)

Inserts the StrokeVertex given as argument into the Stroke before the
point specified by next. The length and curvilinear abscissa are
updated consequently.

**Parameters:**

- **vertex** ([`StrokeVertex`](#freestyle.types.StrokeVertex "freestyle.types.StrokeVertex")) – The StrokeVertex to insert in the Stroke.
- **next** ([`StrokeVertexIterator`](#freestyle.types.StrokeVertexIterator "freestyle.types.StrokeVertexIterator")) – A StrokeVertexIterator pointing to the StrokeVertex
  before which vertex must be inserted.

<a id="freestyle.types.Stroke.remove_all_vertices"></a>

#### freestyle.types.Stroke.remove_all_vertices()

Removes all vertices from the Stroke.

<a id="freestyle.types.Stroke.remove_vertex"></a>

#### freestyle.types.Stroke.remove_vertex(vertex)

Removes the StrokeVertex given as argument from the Stroke. The length
and curvilinear abscissa are updated consequently.

**Parameters:**

**vertex** ([`StrokeVertex`](#freestyle.types.StrokeVertex "freestyle.types.StrokeVertex")) – the StrokeVertex to remove from the Stroke.

<a id="freestyle.types.Stroke.resample"></a>

#### freestyle.types.Stroke.resample(*args)

Accepted call signatures:

- `resample(n)`
- `resample(sampling)`

Resamples the stroke so using one of two methods with the goal
of creating a stroke with fewer points and the same shape.

**Parameters:**

- **n** (int) – Resamples the stroke so that it eventually has N points. That means
  it is going to add N-vertices_size, where vertices_size is the
  number of points we already have. If vertices_size >= N, no
  resampling is done.
- **sampling** (float) – Resamples the stroke with a given sampling value. If the
  sampling is smaller than the actual sampling value, no resampling is done.

<a id="freestyle.types.Stroke.stroke_vertices_begin"></a>

#### freestyle.types.Stroke.stroke_vertices_begin(t=0.0)

Returns a StrokeVertexIterator pointing on the first StrokeVertex of
the Stroke. One can specify a sampling value to re-sample the Stroke
on the fly if needed.

**Parameters:**

**t** (float) – The resampling value with which we want our Stroke to be
resampled. If 0 is specified, no resampling is done.

**Returns:**

A StrokeVertexIterator pointing on the first StrokeVertex.

**Return type:**

[`StrokeVertexIterator`](#freestyle.types.StrokeVertexIterator "freestyle.types.StrokeVertexIterator")

<a id="freestyle.types.Stroke.stroke_vertices_end"></a>

#### freestyle.types.Stroke.stroke_vertices_end()

Returns a StrokeVertexIterator pointing after the last StrokeVertex
of the Stroke.

**Returns:**

A StrokeVertexIterator pointing after the last StrokeVertex.

**Return type:**

[`StrokeVertexIterator`](#freestyle.types.StrokeVertexIterator "freestyle.types.StrokeVertexIterator")

<a id="freestyle.types.Stroke.stroke_vertices_size"></a>

#### freestyle.types.Stroke.stroke_vertices_size()

Returns the number of StrokeVertex constituting the Stroke.

**Returns:**

The number of stroke vertices.

**Return type:**

int

<a id="freestyle.types.Stroke.update_length"></a>

#### freestyle.types.Stroke.update_length()

Updates the 2D length of the Stroke.

<a id="freestyle.types.Stroke.id"></a>

#### freestyle.types.Stroke.id

The Id of this Stroke.

**Type:**

[`Id`](#freestyle.types.Id "freestyle.types.Id")

<a id="freestyle.types.Stroke.length_2d"></a>

#### freestyle.types.Stroke.length_2d

The 2D length of the Stroke.

**Type:**

float

<a id="freestyle.types.Stroke.medium_type"></a>

#### freestyle.types.Stroke.medium_type

The MediumType used for this Stroke.

**Type:**

[`MediumType`](#freestyle.types.MediumType "freestyle.types.MediumType")

<a id="freestyle.types.Stroke.texture_id"></a>

#### freestyle.types.Stroke.texture_id

The ID of the texture used to simulate th marks system for this Stroke.

**Type:**

int

<a id="freestyle.types.Stroke.tips"></a>

#### freestyle.types.Stroke.tips

True if this Stroke uses a texture with tips, and false otherwise.

**Type:**

bool

Special Methods

<a id="freestyle.types.Stroke.__getitem__"></a>

#### freestyle.types.Stroke.__getitem__(key)

**Parameters:**

**key** (int) – Index or key.

**Return type:**

float

<a id="freestyle.types.Stroke.__iter__"></a>

#### freestyle.types.Stroke.__iter__()

**Return type:**

[`Stroke`](#freestyle.types.Stroke "freestyle.types.Stroke")

<a id="freestyle.types.Stroke.__len__"></a>

#### freestyle.types.Stroke.__len__()

**Return type:**

int

<a id="freestyle.types.StrokeAttribute"></a>

### class freestyle.types.StrokeAttribute

Class to define a set of attributes associated with a [`StrokeVertex`](#freestyle.types.StrokeVertex "freestyle.types.StrokeVertex").
The attribute set stores the color, alpha and thickness values for a Stroke
Vertex.

<a id="freestyle.types.StrokeAttribute.__init__"></a>

#### freestyle.types.StrokeAttribute.__init__(*args)

Accepted call signatures:

- `__init__()`
- `__init__(brother)`
- `__init__(red, green, blue, alpha, thickness_right, thickness_left)`
- `__init__(attribute1, attribute2, t)`

Creates a [`StrokeAttribute`](#freestyle.types.StrokeAttribute "freestyle.types.StrokeAttribute") object using either a default constructor,
copy constructor, overloaded constructor, or and interpolation constructor
to interpolate between two [`StrokeAttribute`](#freestyle.types.StrokeAttribute "freestyle.types.StrokeAttribute") objects.

**Parameters:**

- **brother** ([`StrokeAttribute`](#freestyle.types.StrokeAttribute "freestyle.types.StrokeAttribute")) – A StrokeAttribute object to be used as a copy constructor.
- **red** (float) – Red component of a stroke color.
- **green** (float) – Green component of a stroke color.
- **blue** (float) – Blue component of a stroke color.
- **alpha** (float) – Alpha component of a stroke color.
- **thickness_right** (float) – Stroke thickness on the right.
- **thickness_left** (float) – Stroke thickness on the left.
- **attribute1** ([`StrokeAttribute`](#freestyle.types.StrokeAttribute "freestyle.types.StrokeAttribute")) – The first StrokeAttribute object.
- **attribute2** ([`StrokeAttribute`](#freestyle.types.StrokeAttribute "freestyle.types.StrokeAttribute")) – The second StrokeAttribute object.
- **t** (float) – The interpolation parameter (0 <= t <= 1).

<a id="freestyle.types.StrokeAttribute.get_attribute_real"></a>

#### freestyle.types.StrokeAttribute.get_attribute_real(name)

Returns an attribute of float type.

**Parameters:**

**name** (str) – The name of the attribute.

**Returns:**

The attribute value.

**Return type:**

float

<a id="freestyle.types.StrokeAttribute.get_attribute_vec2"></a>

#### freestyle.types.StrokeAttribute.get_attribute_vec2(name)

Returns an attribute of two-dimensional vector type.

**Parameters:**

**name** (str) – The name of the attribute.

**Returns:**

The attribute value.

**Return type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="freestyle.types.StrokeAttribute.get_attribute_vec3"></a>

#### freestyle.types.StrokeAttribute.get_attribute_vec3(name)

Returns an attribute of three-dimensional vector type.

**Parameters:**

**name** (str) – The name of the attribute.

**Returns:**

The attribute value.

**Return type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="freestyle.types.StrokeAttribute.has_attribute_real"></a>

#### freestyle.types.StrokeAttribute.has_attribute_real(name)

Checks whether the attribute name of float type is available.

**Parameters:**

**name** (str) – The name of the attribute.

**Returns:**

True if the attribute is available.

**Return type:**

bool

<a id="freestyle.types.StrokeAttribute.has_attribute_vec2"></a>

#### freestyle.types.StrokeAttribute.has_attribute_vec2(name)

Checks whether the attribute name of two-dimensional vector type
is available.

**Parameters:**

**name** (str) – The name of the attribute.

**Returns:**

True if the attribute is available.

**Return type:**

bool

<a id="freestyle.types.StrokeAttribute.has_attribute_vec3"></a>

#### freestyle.types.StrokeAttribute.has_attribute_vec3(name)

Checks whether the attribute name of three-dimensional vector
type is available.

**Parameters:**

**name** (str) – The name of the attribute.

**Returns:**

True if the attribute is available.

**Return type:**

bool

<a id="freestyle.types.StrokeAttribute.set_attribute_real"></a>

#### freestyle.types.StrokeAttribute.set_attribute_real(name, value)

Adds a user-defined attribute of float type. If there is no
attribute of the given name, it is added. Otherwise, the new value
replaces the old one.

**Parameters:**

- **name** (str) – The name of the attribute.
- **value** (float) – The attribute value.

<a id="freestyle.types.StrokeAttribute.set_attribute_vec2"></a>

#### freestyle.types.StrokeAttribute.set_attribute_vec2(name, value)

Adds a user-defined attribute of two-dimensional vector type. If
there is no attribute of the given name, it is added. Otherwise,
the new value replaces the old one.

**Parameters:**

- **name** (str) – The name of the attribute.
- **value** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | tuple[float, float, float] | list[float]) – The attribute value.

<a id="freestyle.types.StrokeAttribute.set_attribute_vec3"></a>

#### freestyle.types.StrokeAttribute.set_attribute_vec3(name, value)

Adds a user-defined attribute of three-dimensional vector type.
If there is no attribute of the given name, it is added.
Otherwise, the new value replaces the old one.

**Parameters:**

- **name** (str) – The name of the attribute.
- **value** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | tuple[float, float, float] | list[float]) – The attribute value as a 3D vector.

<a id="freestyle.types.StrokeAttribute.alpha"></a>

#### freestyle.types.StrokeAttribute.alpha

Alpha component of the stroke color.

**Type:**

float

<a id="freestyle.types.StrokeAttribute.color"></a>

#### freestyle.types.StrokeAttribute.color

RGB components of the stroke color.

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="freestyle.types.StrokeAttribute.thickness"></a>

#### freestyle.types.StrokeAttribute.thickness

Right and left components of the stroke thickness.
The right (left) component is the thickness on the right (left) of the vertex
when following the stroke.

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="freestyle.types.StrokeAttribute.visible"></a>

#### freestyle.types.StrokeAttribute.visible

The visibility flag. True if the StrokeVertex is visible.

**Type:**

bool

Special Methods

<a id="freestyle.types.StrokeAttribute.__repr__"></a>

#### freestyle.types.StrokeAttribute.__repr__()

**Return type:**

str

<a id="freestyle.types.StrokeShader"></a>

### class freestyle.types.StrokeShader

Base class for stroke shaders. Any stroke shader must inherit from
this class and overload the shade() method. A StrokeShader is
designed to modify stroke attributes such as thickness, color,
geometry, texture, blending mode, and so on. The basic way for this
operation is to iterate over the stroke vertices of the [`Stroke`](#freestyle.types.Stroke "freestyle.types.Stroke")
and to modify the [`StrokeAttribute`](#freestyle.types.StrokeAttribute "freestyle.types.StrokeAttribute") of each vertex. Here is a
code example of such an iteration:

```python
it = ioStroke.strokeVerticesBegin()
while not it.is_end:
    att = it.object.attribute
    ## perform here any attribute modification
    it.increment()
```

<a id="freestyle.types.StrokeShader.__init__"></a>

#### freestyle.types.StrokeShader.__init__()

Default constructor.

<a id="freestyle.types.StrokeShader.shade"></a>

#### freestyle.types.StrokeShader.shade(stroke)

The shading method. Must be overloaded by inherited classes.

**Parameters:**

**stroke** ([`Stroke`](#freestyle.types.Stroke "freestyle.types.Stroke")) – A Stroke object.

<a id="freestyle.types.StrokeShader.name"></a>

#### freestyle.types.StrokeShader.name

The name of the stroke shader.

**Type:**

str

Special Methods

<a id="freestyle.types.StrokeShader.__repr__"></a>

#### freestyle.types.StrokeShader.__repr__()

**Return type:**

str

<a id="freestyle.types.StrokeVertex"></a>

### class freestyle.types.StrokeVertex

Class hierarchy: [`Interface0D`](#freestyle.types.Interface0D "freestyle.types.Interface0D") > [`CurvePoint`](#freestyle.types.CurvePoint "freestyle.types.CurvePoint") > [`StrokeVertex`](#freestyle.types.StrokeVertex "freestyle.types.StrokeVertex")

Class to define a stroke vertex.

<a id="freestyle.types.StrokeVertex.__init__"></a>

#### freestyle.types.StrokeVertex.__init__(*args)

Accepted call signatures:

- `__init__()`
- `__init__(brother)`
- `__init__(first_vertex, second_vertex, t3d)`
- `__init__(point)`
- `__init__(svertex)`
- `__init__(svertex, attribute)`

Builds a [`StrokeVertex`](#freestyle.types.StrokeVertex "freestyle.types.StrokeVertex") using the default constructor,
copy constructor, from 2 [`StrokeVertex`](#freestyle.types.StrokeVertex "freestyle.types.StrokeVertex") and an interpolation parameter,
from a CurvePoint, from a SVertex, or a [`SVertex`](#freestyle.types.SVertex "freestyle.types.SVertex") and a [`StrokeAttribute`](#freestyle.types.StrokeAttribute "freestyle.types.StrokeAttribute") object.

**Parameters:**

- **brother** ([`StrokeVertex`](#freestyle.types.StrokeVertex "freestyle.types.StrokeVertex")) – A StrokeVertex object.
- **first_vertex** ([`StrokeVertex`](#freestyle.types.StrokeVertex "freestyle.types.StrokeVertex")) – The first StrokeVertex.
- **second_vertex** ([`StrokeVertex`](#freestyle.types.StrokeVertex "freestyle.types.StrokeVertex")) – The second StrokeVertex.
- **t3d** (float) – An interpolation parameter.
- **point** ([`CurvePoint`](#freestyle.types.CurvePoint "freestyle.types.CurvePoint")) – A CurvePoint object.
- **svertex** ([`SVertex`](#freestyle.types.SVertex "freestyle.types.SVertex")) – An SVertex object.
- **svertex** – An SVertex object.
- **attribute** ([`StrokeAttribute`](#freestyle.types.StrokeAttribute "freestyle.types.StrokeAttribute")) – A StrokeAttribute object.

<a id="freestyle.types.StrokeVertex.attribute"></a>

#### freestyle.types.StrokeVertex.attribute

StrokeAttribute for this StrokeVertex.

**Type:**

[`StrokeAttribute`](#freestyle.types.StrokeAttribute "freestyle.types.StrokeAttribute")

<a id="freestyle.types.StrokeVertex.curvilinear_abscissa"></a>

#### freestyle.types.StrokeVertex.curvilinear_abscissa

Curvilinear abscissa of this StrokeVertex in the Stroke.

**Type:**

float

<a id="freestyle.types.StrokeVertex.point"></a>

#### freestyle.types.StrokeVertex.point

2D point coordinates.

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="freestyle.types.StrokeVertex.stroke_length"></a>

#### freestyle.types.StrokeVertex.stroke_length

Stroke length (it is only a value retained by the StrokeVertex,
and it won’t change the real stroke length).

**Type:**

float

<a id="freestyle.types.StrokeVertex.u"></a>

#### freestyle.types.StrokeVertex.u

Curvilinear abscissa of this StrokeVertex in the Stroke.

**Type:**

float

<a id="freestyle.types.StrokeVertexIterator"></a>

### class freestyle.types.StrokeVertexIterator

Class hierarchy: [`Iterator`](#freestyle.types.Iterator "freestyle.types.Iterator") > [`StrokeVertexIterator`](#freestyle.types.StrokeVertexIterator "freestyle.types.StrokeVertexIterator")

Class defining an iterator designed to iterate over the
[`StrokeVertex`](#freestyle.types.StrokeVertex "freestyle.types.StrokeVertex") of a [`Stroke`](#freestyle.types.Stroke "freestyle.types.Stroke"). An instance of a
StrokeVertexIterator can be obtained from a Stroke by calling
iter(), stroke_vertices_begin() or stroke_vertices_begin(). It is iterating
over the same vertices as an [`Interface0DIterator`](#freestyle.types.Interface0DIterator "freestyle.types.Interface0DIterator"). The difference
resides in the object access: an Interface0DIterator only allows
access to an Interface0D while one might need to access the
specialized StrokeVertex type. In this case, one should use a
StrokeVertexIterator. To call functions of the UnaryFuntion0D type,
a StrokeVertexIterator can be converted to an Interface0DIterator by
by calling Interface0DIterator(it).

<a id="freestyle.types.StrokeVertexIterator.__init__"></a>

#### freestyle.types.StrokeVertexIterator.__init__(*args)

Accepted call signatures:

- `__init__()`
- `__init__(brother)`

Creates a [`StrokeVertexIterator`](#freestyle.types.StrokeVertexIterator "freestyle.types.StrokeVertexIterator") using either the
default constructor or the copy constructor.

**Parameters:**

**brother** ([`StrokeVertexIterator`](#freestyle.types.StrokeVertexIterator "freestyle.types.StrokeVertexIterator")) – A StrokeVertexIterator object.

<a id="freestyle.types.StrokeVertexIterator.decremented"></a>

#### freestyle.types.StrokeVertexIterator.decremented()

Returns a copy of a decremented StrokeVertexIterator.

**Returns:**

A StrokeVertexIterator pointing the previous StrokeVertex.

**Return type:**

[`StrokeVertexIterator`](#freestyle.types.StrokeVertexIterator "freestyle.types.StrokeVertexIterator")

<a id="freestyle.types.StrokeVertexIterator.incremented"></a>

#### freestyle.types.StrokeVertexIterator.incremented()

Returns a copy of an incremented StrokeVertexIterator.

**Returns:**

A StrokeVertexIterator pointing the next StrokeVertex.

**Return type:**

[`StrokeVertexIterator`](#freestyle.types.StrokeVertexIterator "freestyle.types.StrokeVertexIterator")

<a id="freestyle.types.StrokeVertexIterator.reversed"></a>

#### freestyle.types.StrokeVertexIterator.reversed()

Returns a StrokeVertexIterator that traverses stroke vertices in the
reversed order.

**Returns:**

A StrokeVertexIterator traversing stroke vertices backward.

**Return type:**

[`StrokeVertexIterator`](#freestyle.types.StrokeVertexIterator "freestyle.types.StrokeVertexIterator")

<a id="freestyle.types.StrokeVertexIterator.at_last"></a>

#### freestyle.types.StrokeVertexIterator.at_last

True if the iterator points to the last valid element.
For its counterpart (pointing to the first valid element), use it.is_begin.

**Type:**

bool

<a id="freestyle.types.StrokeVertexIterator.object"></a>

#### freestyle.types.StrokeVertexIterator.object

The StrokeVertex object currently pointed to by this iterator.

**Type:**

[`StrokeVertex`](#freestyle.types.StrokeVertex "freestyle.types.StrokeVertex")

<a id="freestyle.types.StrokeVertexIterator.t"></a>

#### freestyle.types.StrokeVertexIterator.t

The curvilinear abscissa of the current point.

**Type:**

float

<a id="freestyle.types.StrokeVertexIterator.u"></a>

#### freestyle.types.StrokeVertexIterator.u

The point parameter at the current point in the stroke (0 <= u <= 1).

**Type:**

float

Special Methods

<a id="freestyle.types.StrokeVertexIterator.__iter__"></a>

#### freestyle.types.StrokeVertexIterator.__iter__()

**Return type:**

[`StrokeVertexIterator`](#freestyle.types.StrokeVertexIterator "freestyle.types.StrokeVertexIterator")

<a id="freestyle.types.StrokeVertexIterator.__next__"></a>

#### freestyle.types.StrokeVertexIterator.__next__()

**Return type:**

Any

<a id="freestyle.types.TVertex"></a>

### class freestyle.types.TVertex

Class hierarchy: [`Interface0D`](#freestyle.types.Interface0D "freestyle.types.Interface0D") > [`ViewVertex`](#freestyle.types.ViewVertex "freestyle.types.ViewVertex") > [`TVertex`](#freestyle.types.TVertex "freestyle.types.TVertex")

Class to define a T vertex, i.e. an intersection between two edges.
It points towards two SVertex and four ViewEdges. Among the
ViewEdges, two are front and the other two are back. Basically a
front edge hides part of a back edge. So, among the back edges, one
is of invisibility N and the other of invisibility N+1.

<a id="freestyle.types.TVertex.__init__"></a>

#### freestyle.types.TVertex.__init__()

Default constructor.

<a id="freestyle.types.TVertex.get_mate"></a>

#### freestyle.types.TVertex.get_mate(viewedge)

Returns the mate edge of the ViewEdge given as argument. If the
ViewEdge is frontEdgeA, frontEdgeB is returned. If the ViewEdge is
frontEdgeB, frontEdgeA is returned. Same for back edges.

**Parameters:**

**viewedge** ([`ViewEdge`](#freestyle.types.ViewEdge "freestyle.types.ViewEdge")) – A ViewEdge object.

**Returns:**

The mate edge of the given ViewEdge.

**Return type:**

[`ViewEdge`](#freestyle.types.ViewEdge "freestyle.types.ViewEdge")

<a id="freestyle.types.TVertex.get_svertex"></a>

#### freestyle.types.TVertex.get_svertex(fedge)

Returns the SVertex (among the 2) belonging to the given FEdge.

**Parameters:**

**fedge** ([`FEdge`](#freestyle.types.FEdge "freestyle.types.FEdge")) – An FEdge object.

**Returns:**

The SVertex belonging to the given FEdge.

**Return type:**

[`SVertex`](#freestyle.types.SVertex "freestyle.types.SVertex")

<a id="freestyle.types.TVertex.back_svertex"></a>

#### freestyle.types.TVertex.back_svertex

The SVertex that is further away from the viewpoint.

**Type:**

[`SVertex`](#freestyle.types.SVertex "freestyle.types.SVertex")

<a id="freestyle.types.TVertex.front_svertex"></a>

#### freestyle.types.TVertex.front_svertex

The SVertex that is closer to the viewpoint.

**Type:**

[`SVertex`](#freestyle.types.SVertex "freestyle.types.SVertex")

<a id="freestyle.types.TVertex.id"></a>

#### freestyle.types.TVertex.id

The Id of this TVertex.

**Type:**

[`Id`](#freestyle.types.Id "freestyle.types.Id")

<a id="freestyle.types.UnaryFunction0D"></a>

### class freestyle.types.UnaryFunction0D

Base class for Unary Functions (functors) working on
[`Interface0DIterator`](#freestyle.types.Interface0DIterator "freestyle.types.Interface0DIterator"). A unary function will be used by
invoking __call__() on an Interface0DIterator. In Python, several
different subclasses of UnaryFunction0D are used depending on the
types of functors’ return values. For example, you would inherit from
a [`UnaryFunction0DDouble`](#freestyle.types.UnaryFunction0DDouble "freestyle.types.UnaryFunction0DDouble") if you wish to define a function that
returns a double value. Available UnaryFunction0D subclasses are:

- [`UnaryFunction0DDouble`](#freestyle.types.UnaryFunction0DDouble "freestyle.types.UnaryFunction0DDouble")
- [`UnaryFunction0DEdgeNature`](#freestyle.types.UnaryFunction0DEdgeNature "freestyle.types.UnaryFunction0DEdgeNature")
- [`UnaryFunction0DFloat`](#freestyle.types.UnaryFunction0DFloat "freestyle.types.UnaryFunction0DFloat")
- [`UnaryFunction0DId`](#freestyle.types.UnaryFunction0DId "freestyle.types.UnaryFunction0DId")
- [`UnaryFunction0DMaterial`](#freestyle.types.UnaryFunction0DMaterial "freestyle.types.UnaryFunction0DMaterial")
- [`UnaryFunction0DUnsigned`](#freestyle.types.UnaryFunction0DUnsigned "freestyle.types.UnaryFunction0DUnsigned")
- [`UnaryFunction0DVec2f`](#freestyle.types.UnaryFunction0DVec2f "freestyle.types.UnaryFunction0DVec2f")
- [`UnaryFunction0DVec3f`](#freestyle.types.UnaryFunction0DVec3f "freestyle.types.UnaryFunction0DVec3f")
- [`UnaryFunction0DVectorViewShape`](#freestyle.types.UnaryFunction0DVectorViewShape "freestyle.types.UnaryFunction0DVectorViewShape")
- [`UnaryFunction0DViewShape`](#freestyle.types.UnaryFunction0DViewShape "freestyle.types.UnaryFunction0DViewShape")

<a id="freestyle.types.UnaryFunction0D.name"></a>

#### freestyle.types.UnaryFunction0D.name

The name of the unary 0D function.

**Type:**

str

Special Methods

<a id="freestyle.types.UnaryFunction0D.__repr__"></a>

#### freestyle.types.UnaryFunction0D.__repr__()

**Return type:**

str

<a id="freestyle.types.UnaryFunction0DDouble"></a>

### class freestyle.types.UnaryFunction0DDouble

Class hierarchy: [`UnaryFunction0D`](#freestyle.types.UnaryFunction0D "freestyle.types.UnaryFunction0D") > [`UnaryFunction0DDouble`](#freestyle.types.UnaryFunction0DDouble "freestyle.types.UnaryFunction0DDouble")

Base class for unary functions (functors) that work on
[`Interface0DIterator`](#freestyle.types.Interface0DIterator "freestyle.types.Interface0DIterator") and return a float value.

<a id="freestyle.types.UnaryFunction0DDouble.__init__"></a>

#### freestyle.types.UnaryFunction0DDouble.__init__()

Default constructor.

Special Methods

<a id="freestyle.types.UnaryFunction0DDouble.__repr__"></a>

#### freestyle.types.UnaryFunction0DDouble.__repr__()

**Return type:**

str

<a id="freestyle.types.UnaryFunction0DEdgeNature"></a>

### class freestyle.types.UnaryFunction0DEdgeNature

Class hierarchy: [`UnaryFunction0D`](#freestyle.types.UnaryFunction0D "freestyle.types.UnaryFunction0D") > [`UnaryFunction0DEdgeNature`](#freestyle.types.UnaryFunction0DEdgeNature "freestyle.types.UnaryFunction0DEdgeNature")

Base class for unary functions (functors) that work on
[`Interface0DIterator`](#freestyle.types.Interface0DIterator "freestyle.types.Interface0DIterator") and return a [`Nature`](#freestyle.types.Nature "freestyle.types.Nature") object.

<a id="freestyle.types.UnaryFunction0DEdgeNature.__init__"></a>

#### freestyle.types.UnaryFunction0DEdgeNature.__init__()

Default constructor.

Special Methods

<a id="freestyle.types.UnaryFunction0DEdgeNature.__repr__"></a>

#### freestyle.types.UnaryFunction0DEdgeNature.__repr__()

**Return type:**

str

<a id="freestyle.types.UnaryFunction0DFloat"></a>

### class freestyle.types.UnaryFunction0DFloat

Class hierarchy: [`UnaryFunction0D`](#freestyle.types.UnaryFunction0D "freestyle.types.UnaryFunction0D") > [`UnaryFunction0DFloat`](#freestyle.types.UnaryFunction0DFloat "freestyle.types.UnaryFunction0DFloat")

Base class for unary functions (functors) that work on
[`Interface0DIterator`](#freestyle.types.Interface0DIterator "freestyle.types.Interface0DIterator") and return a float value.

<a id="freestyle.types.UnaryFunction0DFloat.__init__"></a>

#### freestyle.types.UnaryFunction0DFloat.__init__()

Default constructor.

Special Methods

<a id="freestyle.types.UnaryFunction0DFloat.__repr__"></a>

#### freestyle.types.UnaryFunction0DFloat.__repr__()

**Return type:**

str

<a id="freestyle.types.UnaryFunction0DId"></a>

### class freestyle.types.UnaryFunction0DId

Class hierarchy: [`UnaryFunction0D`](#freestyle.types.UnaryFunction0D "freestyle.types.UnaryFunction0D") > [`UnaryFunction0DId`](#freestyle.types.UnaryFunction0DId "freestyle.types.UnaryFunction0DId")

Base class for unary functions (functors) that work on
[`Interface0DIterator`](#freestyle.types.Interface0DIterator "freestyle.types.Interface0DIterator") and return an [`Id`](#freestyle.types.Id "freestyle.types.Id") object.

<a id="freestyle.types.UnaryFunction0DId.__init__"></a>

#### freestyle.types.UnaryFunction0DId.__init__()

Default constructor.

Special Methods

<a id="freestyle.types.UnaryFunction0DId.__repr__"></a>

#### freestyle.types.UnaryFunction0DId.__repr__()

**Return type:**

str

<a id="freestyle.types.UnaryFunction0DMaterial"></a>

### class freestyle.types.UnaryFunction0DMaterial

Class hierarchy: [`UnaryFunction0D`](#freestyle.types.UnaryFunction0D "freestyle.types.UnaryFunction0D") > [`UnaryFunction0DMaterial`](#freestyle.types.UnaryFunction0DMaterial "freestyle.types.UnaryFunction0DMaterial")

Base class for unary functions (functors) that work on
[`Interface0DIterator`](#freestyle.types.Interface0DIterator "freestyle.types.Interface0DIterator") and return a [`Material`](#freestyle.types.Material "freestyle.types.Material") object.

<a id="freestyle.types.UnaryFunction0DMaterial.__init__"></a>

#### freestyle.types.UnaryFunction0DMaterial.__init__()

Default constructor.

Special Methods

<a id="freestyle.types.UnaryFunction0DMaterial.__repr__"></a>

#### freestyle.types.UnaryFunction0DMaterial.__repr__()

**Return type:**

str

<a id="freestyle.types.UnaryFunction0DUnsigned"></a>

### class freestyle.types.UnaryFunction0DUnsigned

Class hierarchy: [`UnaryFunction0D`](#freestyle.types.UnaryFunction0D "freestyle.types.UnaryFunction0D") > [`UnaryFunction0DUnsigned`](#freestyle.types.UnaryFunction0DUnsigned "freestyle.types.UnaryFunction0DUnsigned")

Base class for unary functions (functors) that work on
[`Interface0DIterator`](#freestyle.types.Interface0DIterator "freestyle.types.Interface0DIterator") and return an int value.

<a id="freestyle.types.UnaryFunction0DUnsigned.__init__"></a>

#### freestyle.types.UnaryFunction0DUnsigned.__init__()

Default constructor.

Special Methods

<a id="freestyle.types.UnaryFunction0DUnsigned.__repr__"></a>

#### freestyle.types.UnaryFunction0DUnsigned.__repr__()

**Return type:**

str

<a id="freestyle.types.UnaryFunction0DVec2f"></a>

### class freestyle.types.UnaryFunction0DVec2f

Class hierarchy: [`UnaryFunction0D`](#freestyle.types.UnaryFunction0D "freestyle.types.UnaryFunction0D") > [`UnaryFunction0DVec2f`](#freestyle.types.UnaryFunction0DVec2f "freestyle.types.UnaryFunction0DVec2f")

Base class for unary functions (functors) that work on
[`Interface0DIterator`](#freestyle.types.Interface0DIterator "freestyle.types.Interface0DIterator") and return a 2D vector.

<a id="freestyle.types.UnaryFunction0DVec2f.__init__"></a>

#### freestyle.types.UnaryFunction0DVec2f.__init__()

Default constructor.

Special Methods

<a id="freestyle.types.UnaryFunction0DVec2f.__repr__"></a>

#### freestyle.types.UnaryFunction0DVec2f.__repr__()

**Return type:**

str

<a id="freestyle.types.UnaryFunction0DVec3f"></a>

### class freestyle.types.UnaryFunction0DVec3f

Class hierarchy: [`UnaryFunction0D`](#freestyle.types.UnaryFunction0D "freestyle.types.UnaryFunction0D") > [`UnaryFunction0DVec3f`](#freestyle.types.UnaryFunction0DVec3f "freestyle.types.UnaryFunction0DVec3f")

Base class for unary functions (functors) that work on
[`Interface0DIterator`](#freestyle.types.Interface0DIterator "freestyle.types.Interface0DIterator") and return a 3D vector.

<a id="freestyle.types.UnaryFunction0DVec3f.__init__"></a>

#### freestyle.types.UnaryFunction0DVec3f.__init__()

Default constructor.

Special Methods

<a id="freestyle.types.UnaryFunction0DVec3f.__repr__"></a>

#### freestyle.types.UnaryFunction0DVec3f.__repr__()

**Return type:**

str

<a id="freestyle.types.UnaryFunction0DVectorViewShape"></a>

### class freestyle.types.UnaryFunction0DVectorViewShape

Class hierarchy: [`UnaryFunction0D`](#freestyle.types.UnaryFunction0D "freestyle.types.UnaryFunction0D") > [`UnaryFunction0DVectorViewShape`](#freestyle.types.UnaryFunction0DVectorViewShape "freestyle.types.UnaryFunction0DVectorViewShape")

Base class for unary functions (functors) that work on
[`Interface0DIterator`](#freestyle.types.Interface0DIterator "freestyle.types.Interface0DIterator") and return a list of [`ViewShape`](#freestyle.types.ViewShape "freestyle.types.ViewShape")
objects.

<a id="freestyle.types.UnaryFunction0DVectorViewShape.__init__"></a>

#### freestyle.types.UnaryFunction0DVectorViewShape.__init__()

Default constructor.

Special Methods

<a id="freestyle.types.UnaryFunction0DVectorViewShape.__repr__"></a>

#### freestyle.types.UnaryFunction0DVectorViewShape.__repr__()

**Return type:**

str

<a id="freestyle.types.UnaryFunction0DViewShape"></a>

### class freestyle.types.UnaryFunction0DViewShape

Class hierarchy: [`UnaryFunction0D`](#freestyle.types.UnaryFunction0D "freestyle.types.UnaryFunction0D") > [`UnaryFunction0DViewShape`](#freestyle.types.UnaryFunction0DViewShape "freestyle.types.UnaryFunction0DViewShape")

Base class for unary functions (functors) that work on
[`Interface0DIterator`](#freestyle.types.Interface0DIterator "freestyle.types.Interface0DIterator") and return a [`ViewShape`](#freestyle.types.ViewShape "freestyle.types.ViewShape") object.

<a id="freestyle.types.UnaryFunction0DViewShape.__init__"></a>

#### freestyle.types.UnaryFunction0DViewShape.__init__()

Default constructor.

Special Methods

<a id="freestyle.types.UnaryFunction0DViewShape.__repr__"></a>

#### freestyle.types.UnaryFunction0DViewShape.__repr__()

**Return type:**

str

<a id="freestyle.types.UnaryFunction1D"></a>

### class freestyle.types.UnaryFunction1D

Base class for Unary Functions (functors) working on
[`Interface1D`](#freestyle.types.Interface1D "freestyle.types.Interface1D"). A unary function will be used by invoking
__call__() on an Interface1D. In Python, several different subclasses
of UnaryFunction1D are used depending on the types of functors’ return
values. For example, you would inherit from a
[`UnaryFunction1DDouble`](#freestyle.types.UnaryFunction1DDouble "freestyle.types.UnaryFunction1DDouble") if you wish to define a function that
returns a double value. Available UnaryFunction1D subclasses are:

- [`UnaryFunction1DDouble`](#freestyle.types.UnaryFunction1DDouble "freestyle.types.UnaryFunction1DDouble")
- [`UnaryFunction1DEdgeNature`](#freestyle.types.UnaryFunction1DEdgeNature "freestyle.types.UnaryFunction1DEdgeNature")
- [`UnaryFunction1DFloat`](#freestyle.types.UnaryFunction1DFloat "freestyle.types.UnaryFunction1DFloat")
- [`UnaryFunction1DUnsigned`](#freestyle.types.UnaryFunction1DUnsigned "freestyle.types.UnaryFunction1DUnsigned")
- [`UnaryFunction1DVec2f`](#freestyle.types.UnaryFunction1DVec2f "freestyle.types.UnaryFunction1DVec2f")
- [`UnaryFunction1DVec3f`](#freestyle.types.UnaryFunction1DVec3f "freestyle.types.UnaryFunction1DVec3f")
- [`UnaryFunction1DVectorViewShape`](#freestyle.types.UnaryFunction1DVectorViewShape "freestyle.types.UnaryFunction1DVectorViewShape")
- [`UnaryFunction1DVoid`](#freestyle.types.UnaryFunction1DVoid "freestyle.types.UnaryFunction1DVoid")

<a id="freestyle.types.UnaryFunction1D.name"></a>

#### freestyle.types.UnaryFunction1D.name

The name of the unary 1D function.

**Type:**

str

Special Methods

<a id="freestyle.types.UnaryFunction1D.__repr__"></a>

#### freestyle.types.UnaryFunction1D.__repr__()

**Return type:**

str

<a id="freestyle.types.UnaryFunction1DDouble"></a>

### class freestyle.types.UnaryFunction1DDouble

Class hierarchy: [`UnaryFunction1D`](#freestyle.types.UnaryFunction1D "freestyle.types.UnaryFunction1D") > [`UnaryFunction1DDouble`](#freestyle.types.UnaryFunction1DDouble "freestyle.types.UnaryFunction1DDouble")

Base class for unary functions (functors) that work on
[`Interface1D`](#freestyle.types.Interface1D "freestyle.types.Interface1D") and return a float value.

<a id="freestyle.types.UnaryFunction1DDouble.__init__"></a>

#### freestyle.types.UnaryFunction1DDouble.__init__(*args)

Accepted call signatures:

- `__init__()`
- `__init__(integration_type)`

Builds a unary 1D function using the default constructor
or the integration method given as an argument.

**Parameters:**

**integration_type** ([`IntegrationType`](#freestyle.types.IntegrationType "freestyle.types.IntegrationType")) – An integration method.

<a id="freestyle.types.UnaryFunction1DDouble.integration_type"></a>

#### freestyle.types.UnaryFunction1DDouble.integration_type

The integration method.

**Type:**

[`IntegrationType`](#freestyle.types.IntegrationType "freestyle.types.IntegrationType")

Special Methods

<a id="freestyle.types.UnaryFunction1DDouble.__repr__"></a>

#### freestyle.types.UnaryFunction1DDouble.__repr__()

**Return type:**

str

<a id="freestyle.types.UnaryFunction1DEdgeNature"></a>

### class freestyle.types.UnaryFunction1DEdgeNature

Class hierarchy: [`UnaryFunction1D`](#freestyle.types.UnaryFunction1D "freestyle.types.UnaryFunction1D") > [`UnaryFunction1DEdgeNature`](#freestyle.types.UnaryFunction1DEdgeNature "freestyle.types.UnaryFunction1DEdgeNature")

Base class for unary functions (functors) that work on
[`Interface1D`](#freestyle.types.Interface1D "freestyle.types.Interface1D") and return a [`Nature`](#freestyle.types.Nature "freestyle.types.Nature") object.

<a id="freestyle.types.UnaryFunction1DEdgeNature.__init__"></a>

#### freestyle.types.UnaryFunction1DEdgeNature.__init__(*args)

Accepted call signatures:

- `__init__()`
- `__init__(integration_type)`

Builds a unary 1D function using the default constructor
or the integration method given as an argument.

**Parameters:**

**integration_type** ([`IntegrationType`](#freestyle.types.IntegrationType "freestyle.types.IntegrationType")) – An integration method.

<a id="freestyle.types.UnaryFunction1DEdgeNature.integration_type"></a>

#### freestyle.types.UnaryFunction1DEdgeNature.integration_type

The integration method.

**Type:**

[`IntegrationType`](#freestyle.types.IntegrationType "freestyle.types.IntegrationType")

Special Methods

<a id="freestyle.types.UnaryFunction1DEdgeNature.__repr__"></a>

#### freestyle.types.UnaryFunction1DEdgeNature.__repr__()

**Return type:**

str

<a id="freestyle.types.UnaryFunction1DFloat"></a>

### class freestyle.types.UnaryFunction1DFloat

Class hierarchy: [`UnaryFunction1D`](#freestyle.types.UnaryFunction1D "freestyle.types.UnaryFunction1D") > [`UnaryFunction1DFloat`](#freestyle.types.UnaryFunction1DFloat "freestyle.types.UnaryFunction1DFloat")

Base class for unary functions (functors) that work on
[`Interface1D`](#freestyle.types.Interface1D "freestyle.types.Interface1D") and return a float value.

<a id="freestyle.types.UnaryFunction1DFloat.__init__"></a>

#### freestyle.types.UnaryFunction1DFloat.__init__(*args)

Accepted call signatures:

- `__init__()`
- `__init__(integration_type)`

Builds a unary 1D function using the default constructor
or the integration method given as an argument.

**Parameters:**

**integration_type** ([`IntegrationType`](#freestyle.types.IntegrationType "freestyle.types.IntegrationType")) – An integration method.

<a id="freestyle.types.UnaryFunction1DFloat.integration_type"></a>

#### freestyle.types.UnaryFunction1DFloat.integration_type

The integration method.

**Type:**

[`IntegrationType`](#freestyle.types.IntegrationType "freestyle.types.IntegrationType")

Special Methods

<a id="freestyle.types.UnaryFunction1DFloat.__repr__"></a>

#### freestyle.types.UnaryFunction1DFloat.__repr__()

**Return type:**

str

<a id="freestyle.types.UnaryFunction1DUnsigned"></a>

### class freestyle.types.UnaryFunction1DUnsigned

Class hierarchy: [`UnaryFunction1D`](#freestyle.types.UnaryFunction1D "freestyle.types.UnaryFunction1D") > [`UnaryFunction1DUnsigned`](#freestyle.types.UnaryFunction1DUnsigned "freestyle.types.UnaryFunction1DUnsigned")

Base class for unary functions (functors) that work on
[`Interface1D`](#freestyle.types.Interface1D "freestyle.types.Interface1D") and return an int value.

<a id="freestyle.types.UnaryFunction1DUnsigned.__init__"></a>

#### freestyle.types.UnaryFunction1DUnsigned.__init__(*args)

Accepted call signatures:

- `__init__()`
- `__init__(integration_type)`

Builds a unary 1D function using the default constructor
or the integration method given as an argument.

**Parameters:**

**integration_type** ([`IntegrationType`](#freestyle.types.IntegrationType "freestyle.types.IntegrationType")) – An integration method.

<a id="freestyle.types.UnaryFunction1DUnsigned.integration_type"></a>

#### freestyle.types.UnaryFunction1DUnsigned.integration_type

The integration method.

**Type:**

[`IntegrationType`](#freestyle.types.IntegrationType "freestyle.types.IntegrationType")

Special Methods

<a id="freestyle.types.UnaryFunction1DUnsigned.__repr__"></a>

#### freestyle.types.UnaryFunction1DUnsigned.__repr__()

**Return type:**

str

<a id="freestyle.types.UnaryFunction1DVec2f"></a>

### class freestyle.types.UnaryFunction1DVec2f

Class hierarchy: [`UnaryFunction1D`](#freestyle.types.UnaryFunction1D "freestyle.types.UnaryFunction1D") > [`UnaryFunction1DVec2f`](#freestyle.types.UnaryFunction1DVec2f "freestyle.types.UnaryFunction1DVec2f")

Base class for unary functions (functors) that work on
[`Interface1D`](#freestyle.types.Interface1D "freestyle.types.Interface1D") and return a 2D vector.

<a id="freestyle.types.UnaryFunction1DVec2f.__init__"></a>

#### freestyle.types.UnaryFunction1DVec2f.__init__(*args)

Accepted call signatures:

- `__init__()`
- `__init__(integration_type)`

Builds a unary 1D function using the default constructor
or the integration method given as an argument.

**Parameters:**

**integration_type** ([`IntegrationType`](#freestyle.types.IntegrationType "freestyle.types.IntegrationType")) – An integration method.

<a id="freestyle.types.UnaryFunction1DVec2f.integration_type"></a>

#### freestyle.types.UnaryFunction1DVec2f.integration_type

The integration method.

**Type:**

[`IntegrationType`](#freestyle.types.IntegrationType "freestyle.types.IntegrationType")

Special Methods

<a id="freestyle.types.UnaryFunction1DVec2f.__repr__"></a>

#### freestyle.types.UnaryFunction1DVec2f.__repr__()

**Return type:**

str

<a id="freestyle.types.UnaryFunction1DVec3f"></a>

### class freestyle.types.UnaryFunction1DVec3f

Class hierarchy: [`UnaryFunction1D`](#freestyle.types.UnaryFunction1D "freestyle.types.UnaryFunction1D") > [`UnaryFunction1DVec3f`](#freestyle.types.UnaryFunction1DVec3f "freestyle.types.UnaryFunction1DVec3f")

Base class for unary functions (functors) that work on
[`Interface1D`](#freestyle.types.Interface1D "freestyle.types.Interface1D") and return a 3D vector.

<a id="freestyle.types.UnaryFunction1DVec3f.__init__"></a>

#### freestyle.types.UnaryFunction1DVec3f.__init__(*args)

Accepted call signatures:

- `__init__()`
- `__init__(integration_type)`

Builds a unary 1D function using the default constructor
or the integration method given as an argument.

**Parameters:**

**integration_type** ([`IntegrationType`](#freestyle.types.IntegrationType "freestyle.types.IntegrationType")) – An integration method.

<a id="freestyle.types.UnaryFunction1DVec3f.integration_type"></a>

#### freestyle.types.UnaryFunction1DVec3f.integration_type

The integration method.

**Type:**

[`IntegrationType`](#freestyle.types.IntegrationType "freestyle.types.IntegrationType")

Special Methods

<a id="freestyle.types.UnaryFunction1DVec3f.__repr__"></a>

#### freestyle.types.UnaryFunction1DVec3f.__repr__()

**Return type:**

str

<a id="freestyle.types.UnaryFunction1DVectorViewShape"></a>

### class freestyle.types.UnaryFunction1DVectorViewShape

Class hierarchy: [`UnaryFunction1D`](#freestyle.types.UnaryFunction1D "freestyle.types.UnaryFunction1D") > [`UnaryFunction1DVectorViewShape`](#freestyle.types.UnaryFunction1DVectorViewShape "freestyle.types.UnaryFunction1DVectorViewShape")

Base class for unary functions (functors) that work on
[`Interface1D`](#freestyle.types.Interface1D "freestyle.types.Interface1D") and return a list of [`ViewShape`](#freestyle.types.ViewShape "freestyle.types.ViewShape")
objects.

<a id="freestyle.types.UnaryFunction1DVectorViewShape.__init__"></a>

#### freestyle.types.UnaryFunction1DVectorViewShape.__init__(*args)

Accepted call signatures:

- `__init__()`
- `__init__(integration_type)`

Builds a unary 1D function using the default constructor
or the integration method given as an argument.

**Parameters:**

**integration_type** ([`IntegrationType`](#freestyle.types.IntegrationType "freestyle.types.IntegrationType")) – An integration method.

<a id="freestyle.types.UnaryFunction1DVectorViewShape.integration_type"></a>

#### freestyle.types.UnaryFunction1DVectorViewShape.integration_type

The integration method.

**Type:**

[`IntegrationType`](#freestyle.types.IntegrationType "freestyle.types.IntegrationType")

Special Methods

<a id="freestyle.types.UnaryFunction1DVectorViewShape.__repr__"></a>

#### freestyle.types.UnaryFunction1DVectorViewShape.__repr__()

**Return type:**

str

<a id="freestyle.types.UnaryFunction1DVoid"></a>

### class freestyle.types.UnaryFunction1DVoid

Class hierarchy: [`UnaryFunction1D`](#freestyle.types.UnaryFunction1D "freestyle.types.UnaryFunction1D") > [`UnaryFunction1DVoid`](#freestyle.types.UnaryFunction1DVoid "freestyle.types.UnaryFunction1DVoid")

Base class for unary functions (functors) working on
[`Interface1D`](#freestyle.types.Interface1D "freestyle.types.Interface1D").

<a id="freestyle.types.UnaryFunction1DVoid.__init__"></a>

#### freestyle.types.UnaryFunction1DVoid.__init__(*args)

Accepted call signatures:

- `__init__()`
- `__init__(integration_type)`

Builds a unary 1D function using either a default constructor
or the integration method given as an argument.

**Parameters:**

**integration_type** ([`IntegrationType`](#freestyle.types.IntegrationType "freestyle.types.IntegrationType")) – An integration method.

<a id="freestyle.types.UnaryFunction1DVoid.integration_type"></a>

#### freestyle.types.UnaryFunction1DVoid.integration_type

The integration method.

**Type:**

[`IntegrationType`](#freestyle.types.IntegrationType "freestyle.types.IntegrationType")

Special Methods

<a id="freestyle.types.UnaryFunction1DVoid.__repr__"></a>

#### freestyle.types.UnaryFunction1DVoid.__repr__()

**Return type:**

str

<a id="freestyle.types.UnaryPredicate0D"></a>

### class freestyle.types.UnaryPredicate0D

Base class for unary predicates that work on
[`Interface0DIterator`](#freestyle.types.Interface0DIterator "freestyle.types.Interface0DIterator"). A UnaryPredicate0D is a functor that
evaluates a condition on an Interface0DIterator and returns true or
false depending on whether this condition is satisfied or not. The
UnaryPredicate0D is used by invoking its __call__() method. Any
inherited class must overload the __call__() method.

<a id="freestyle.types.UnaryPredicate0D.__init__"></a>

#### freestyle.types.UnaryPredicate0D.__init__()

Default constructor.

<a id="freestyle.types.UnaryPredicate0D.__call__"></a>

#### freestyle.types.UnaryPredicate0D.__call__(it)

Must be overload by inherited classes.

**Parameters:**

**it** ([`Interface0DIterator`](#freestyle.types.Interface0DIterator "freestyle.types.Interface0DIterator")) – The Interface0DIterator pointing onto the Interface0D at
which we wish to evaluate the predicate.

**Returns:**

True if the condition is satisfied, false otherwise.

**Return type:**

bool

<a id="freestyle.types.UnaryPredicate0D.name"></a>

#### freestyle.types.UnaryPredicate0D.name

The name of the unary 0D predicate.

**Type:**

str

Special Methods

<a id="freestyle.types.UnaryPredicate0D.__repr__"></a>

#### freestyle.types.UnaryPredicate0D.__repr__()

**Return type:**

str

<a id="freestyle.types.UnaryPredicate1D"></a>

### class freestyle.types.UnaryPredicate1D

Base class for unary predicates that work on [`Interface1D`](#freestyle.types.Interface1D "freestyle.types.Interface1D"). A
UnaryPredicate1D is a functor that evaluates a condition on a
Interface1D and returns true or false depending on whether this
condition is satisfied or not. The UnaryPredicate1D is used by
invoking its __call__() method. Any inherited class must overload the
__call__() method.

<a id="freestyle.types.UnaryPredicate1D.__init__"></a>

#### freestyle.types.UnaryPredicate1D.__init__()

Default constructor.

<a id="freestyle.types.UnaryPredicate1D.__call__"></a>

#### freestyle.types.UnaryPredicate1D.__call__(inter)

Must be overload by inherited classes.

**Parameters:**

**inter** ([`Interface1D`](#freestyle.types.Interface1D "freestyle.types.Interface1D")) – The Interface1D on which we wish to evaluate the predicate.

**Returns:**

True if the condition is satisfied, false otherwise.

**Return type:**

bool

<a id="freestyle.types.UnaryPredicate1D.name"></a>

#### freestyle.types.UnaryPredicate1D.name

The name of the unary 1D predicate.

**Type:**

str

Special Methods

<a id="freestyle.types.UnaryPredicate1D.__repr__"></a>

#### freestyle.types.UnaryPredicate1D.__repr__()

**Return type:**

str

<a id="freestyle.types.ViewEdge"></a>

### class freestyle.types.ViewEdge

Class hierarchy: [`Interface1D`](#freestyle.types.Interface1D "freestyle.types.Interface1D") > [`ViewEdge`](#freestyle.types.ViewEdge "freestyle.types.ViewEdge")

Class defining a ViewEdge. A ViewEdge in an edge of the image graph.
it connects two [`ViewVertex`](#freestyle.types.ViewVertex "freestyle.types.ViewVertex") objects. It is made by connecting
a set of FEdges.

<a id="freestyle.types.ViewEdge.__init__"></a>

#### freestyle.types.ViewEdge.__init__(*args)

Accepted call signatures:

- `__init__()`
- `__init__(brother)`

Builds a [`ViewEdge`](#freestyle.types.ViewEdge "freestyle.types.ViewEdge") using the default constructor or the copy constructor.

**Parameters:**

**brother** ([`ViewEdge`](#freestyle.types.ViewEdge "freestyle.types.ViewEdge")) – A ViewEdge object.

<a id="freestyle.types.ViewEdge.update_fedges"></a>

#### freestyle.types.ViewEdge.update_fedges()

Sets Viewedge to this for all embedded fedges.

<a id="freestyle.types.ViewEdge.chaining_time_stamp"></a>

#### freestyle.types.ViewEdge.chaining_time_stamp

The time stamp of this ViewEdge.

**Type:**

int

<a id="freestyle.types.ViewEdge.first_fedge"></a>

#### freestyle.types.ViewEdge.first_fedge

The first FEdge that constitutes this ViewEdge.

**Type:**

[`FEdge`](#freestyle.types.FEdge "freestyle.types.FEdge")

<a id="freestyle.types.ViewEdge.first_viewvertex"></a>

#### freestyle.types.ViewEdge.first_viewvertex

The first ViewVertex.

**Type:**

[`ViewVertex`](#freestyle.types.ViewVertex "freestyle.types.ViewVertex")

<a id="freestyle.types.ViewEdge.id"></a>

#### freestyle.types.ViewEdge.id

The Id of this ViewEdge.

**Type:**

[`Id`](#freestyle.types.Id "freestyle.types.Id")

<a id="freestyle.types.ViewEdge.is_closed"></a>

#### freestyle.types.ViewEdge.is_closed

True if this ViewEdge forms a closed loop.

**Type:**

bool

<a id="freestyle.types.ViewEdge.last_fedge"></a>

#### freestyle.types.ViewEdge.last_fedge

The last FEdge that constitutes this ViewEdge.

**Type:**

[`FEdge`](#freestyle.types.FEdge "freestyle.types.FEdge")

<a id="freestyle.types.ViewEdge.last_viewvertex"></a>

#### freestyle.types.ViewEdge.last_viewvertex

The second ViewVertex.

**Type:**

[`ViewVertex`](#freestyle.types.ViewVertex "freestyle.types.ViewVertex")

<a id="freestyle.types.ViewEdge.nature"></a>

#### freestyle.types.ViewEdge.nature

The nature of this ViewEdge.

**Type:**

[`Nature`](#freestyle.types.Nature "freestyle.types.Nature")

<a id="freestyle.types.ViewEdge.occludee"></a>

#### freestyle.types.ViewEdge.occludee

The shape that is occluded by the ViewShape to which this ViewEdge
belongs to. If no object is occluded, this property is set to None.

**Type:**

[`ViewShape`](#freestyle.types.ViewShape "freestyle.types.ViewShape")

<a id="freestyle.types.ViewEdge.qi"></a>

#### freestyle.types.ViewEdge.qi

The quantitative invisibility.

**Type:**

int

<a id="freestyle.types.ViewEdge.viewshape"></a>

#### freestyle.types.ViewEdge.viewshape

The ViewShape to which this ViewEdge belongs to.

**Type:**

[`ViewShape`](#freestyle.types.ViewShape "freestyle.types.ViewShape")

<a id="freestyle.types.ViewEdgeIterator"></a>

### class freestyle.types.ViewEdgeIterator

Class hierarchy: [`Iterator`](#freestyle.types.Iterator "freestyle.types.Iterator") > [`ViewEdgeIterator`](#freestyle.types.ViewEdgeIterator "freestyle.types.ViewEdgeIterator")

Base class for iterators over ViewEdges of the [`ViewMap`](#freestyle.types.ViewMap "freestyle.types.ViewMap") Graph.
Basically the increment() operator of this class should be able to
take the decision of “where” (on which ViewEdge) to go when pointing
on a given ViewEdge.

<a id="freestyle.types.ViewEdgeIterator.__init__"></a>

#### freestyle.types.ViewEdgeIterator.__init__(*args)

Accepted call signatures:

- `__init__(begin=None, orientation=True)`
- `__init__(brother)`

Builds a ViewEdgeIterator from a starting ViewEdge and its
orientation or the copy constructor.

**Parameters:**

- **begin** ([`ViewEdge`](#freestyle.types.ViewEdge "freestyle.types.ViewEdge") | None) – The ViewEdge from where to start the iteration.
- **orientation** (bool) – If true, we’ll look for the next ViewEdge among
  the ViewEdges that surround the ending ViewVertex of begin. If
  false, we’ll search over the ViewEdges surrounding the ending
  ViewVertex of begin.
- **brother** ([`ViewEdgeIterator`](#freestyle.types.ViewEdgeIterator "freestyle.types.ViewEdgeIterator")) – A ViewEdgeIterator object.

<a id="freestyle.types.ViewEdgeIterator.change_orientation"></a>

#### freestyle.types.ViewEdgeIterator.change_orientation()

Changes the current orientation.

<a id="freestyle.types.ViewEdgeIterator.begin"></a>

#### freestyle.types.ViewEdgeIterator.begin

The first ViewEdge used for the iteration.

**Type:**

[`ViewEdge`](#freestyle.types.ViewEdge "freestyle.types.ViewEdge")

<a id="freestyle.types.ViewEdgeIterator.current_edge"></a>

#### freestyle.types.ViewEdgeIterator.current_edge

The ViewEdge object currently pointed by this iterator.

**Type:**

[`ViewEdge`](#freestyle.types.ViewEdge "freestyle.types.ViewEdge")

<a id="freestyle.types.ViewEdgeIterator.object"></a>

#### freestyle.types.ViewEdgeIterator.object

The ViewEdge object currently pointed by this iterator.

**Type:**

[`ViewEdge`](#freestyle.types.ViewEdge "freestyle.types.ViewEdge")

<a id="freestyle.types.ViewEdgeIterator.orientation"></a>

#### freestyle.types.ViewEdgeIterator.orientation

The orientation of the pointed ViewEdge in the iteration.
If true, the iterator looks for the next ViewEdge among those ViewEdges
that surround the ending ViewVertex of the “begin” ViewEdge. If false,
the iterator searches over the ViewEdges surrounding the ending ViewVertex
of the “begin” ViewEdge.

**Type:**

bool

<a id="freestyle.types.ViewMap"></a>

### class freestyle.types.ViewMap

Class defining the ViewMap.

<a id="freestyle.types.ViewMap.__init__"></a>

#### freestyle.types.ViewMap.__init__()

Default constructor.

<a id="freestyle.types.ViewMap.get_closest_fedge"></a>

#### freestyle.types.ViewMap.get_closest_fedge(x, y)

Gets the FEdge nearest to the 2D point specified as arguments.

**Parameters:**

- **x** (float) – X coordinate of a 2D point.
- **y** (float) – Y coordinate of a 2D point.

**Returns:**

The FEdge nearest to the specified 2D point.

**Return type:**

[`FEdge`](#freestyle.types.FEdge "freestyle.types.FEdge")

<a id="freestyle.types.ViewMap.get_closest_viewedge"></a>

#### freestyle.types.ViewMap.get_closest_viewedge(x, y)

Gets the ViewEdge nearest to the 2D point specified as arguments.

**Parameters:**

- **x** (float) – X coordinate of a 2D point.
- **y** (float) – Y coordinate of a 2D point.

**Returns:**

The ViewEdge nearest to the specified 2D point.

**Return type:**

[`ViewEdge`](#freestyle.types.ViewEdge "freestyle.types.ViewEdge")

<a id="freestyle.types.ViewMap.scene_bbox"></a>

#### freestyle.types.ViewMap.scene_bbox

The 3D bounding box of the scene.

**Type:**

[`BBox`](#freestyle.types.BBox "freestyle.types.BBox")

Special Methods

<a id="freestyle.types.ViewMap.__repr__"></a>

#### freestyle.types.ViewMap.__repr__()

**Return type:**

str

<a id="freestyle.types.ViewShape"></a>

### class freestyle.types.ViewShape

Class gathering the elements of the ViewMap (i.e., [`ViewVertex`](#freestyle.types.ViewVertex "freestyle.types.ViewVertex")
and [`ViewEdge`](#freestyle.types.ViewEdge "freestyle.types.ViewEdge")) that are issued from the same input shape.

<a id="freestyle.types.ViewShape.__init__"></a>

#### freestyle.types.ViewShape.__init__(*args)

Accepted call signatures:

- `__init__()`
- `__init__(brother)`
- `__init__(sshape)`

Builds a [`ViewShape`](#freestyle.types.ViewShape "freestyle.types.ViewShape") using the default constructor,
copy constructor, or from a [`SShape`](#freestyle.types.SShape "freestyle.types.SShape").

**Parameters:**

- **brother** ([`ViewShape`](#freestyle.types.ViewShape "freestyle.types.ViewShape")) – A ViewShape object.
- **sshape** ([`SShape`](#freestyle.types.SShape "freestyle.types.SShape")) – An SShape object.

<a id="freestyle.types.ViewShape.add_edge"></a>

#### freestyle.types.ViewShape.add_edge(edge)

Adds a ViewEdge to the list of ViewEdge objects.

**Parameters:**

**edge** ([`ViewEdge`](#freestyle.types.ViewEdge "freestyle.types.ViewEdge")) – A ViewEdge object.

<a id="freestyle.types.ViewShape.add_vertex"></a>

#### freestyle.types.ViewShape.add_vertex(vertex)

Adds a ViewVertex to the list of the ViewVertex objects.

**Parameters:**

**vertex** ([`ViewVertex`](#freestyle.types.ViewVertex "freestyle.types.ViewVertex")) – A ViewVertex object.

<a id="freestyle.types.ViewShape.edges"></a>

#### freestyle.types.ViewShape.edges

The list of ViewEdge objects contained in this ViewShape.

**Type:**

list[[`ViewEdge`](#freestyle.types.ViewEdge "freestyle.types.ViewEdge")]

<a id="freestyle.types.ViewShape.id"></a>

#### freestyle.types.ViewShape.id

The Id of this ViewShape.

**Type:**

[`Id`](#freestyle.types.Id "freestyle.types.Id")

<a id="freestyle.types.ViewShape.library_path"></a>

#### freestyle.types.ViewShape.library_path

The library path of the ViewShape, or None if the ViewShape is not part of
a library.

**Type:**

str | None

<a id="freestyle.types.ViewShape.name"></a>

#### freestyle.types.ViewShape.name

The name of the ViewShape.

**Type:**

str

<a id="freestyle.types.ViewShape.sshape"></a>

#### freestyle.types.ViewShape.sshape

The SShape on top of which this ViewShape is built.

**Type:**

[`SShape`](#freestyle.types.SShape "freestyle.types.SShape")

<a id="freestyle.types.ViewShape.vertices"></a>

#### freestyle.types.ViewShape.vertices

The list of ViewVertex objects contained in this ViewShape.

**Type:**

list[[`ViewVertex`](#freestyle.types.ViewVertex "freestyle.types.ViewVertex")]

Special Methods

<a id="freestyle.types.ViewShape.__repr__"></a>

#### freestyle.types.ViewShape.__repr__()

**Return type:**

str

<a id="freestyle.types.ViewVertex"></a>

### class freestyle.types.ViewVertex

Class hierarchy: [`Interface0D`](#freestyle.types.Interface0D "freestyle.types.Interface0D") > [`ViewVertex`](#freestyle.types.ViewVertex "freestyle.types.ViewVertex")

Class to define a view vertex. A view vertex is a feature vertex
corresponding to a point of the image graph, where the characteristics
of an edge (e.g., nature and visibility) might change. A
[`ViewVertex`](#freestyle.types.ViewVertex "freestyle.types.ViewVertex") can be of two kinds: A [`TVertex`](#freestyle.types.TVertex "freestyle.types.TVertex") when it
corresponds to the intersection between two ViewEdges or a
[`NonTVertex`](#freestyle.types.NonTVertex "freestyle.types.NonTVertex") when it corresponds to a vertex of the initial
input mesh (it is the case for vertices such as corners for example).
Thus, this class can be specialized into two classes, the
[`TVertex`](#freestyle.types.TVertex "freestyle.types.TVertex") class and the [`NonTVertex`](#freestyle.types.NonTVertex "freestyle.types.NonTVertex") class.

<a id="freestyle.types.ViewVertex.edges_begin"></a>

#### freestyle.types.ViewVertex.edges_begin()

Returns an iterator over the ViewEdges that goes to or comes from
this ViewVertex pointing to the first ViewEdge of the list. The
orientedViewEdgeIterator allows to iterate in CCW order over these
ViewEdges and to get the orientation for each ViewEdge
(incoming/outgoing).

**Returns:**

An orientedViewEdgeIterator pointing to the first ViewEdge.

**Return type:**

[`orientedViewEdgeIterator`](#freestyle.types.orientedViewEdgeIterator "freestyle.types.orientedViewEdgeIterator")

<a id="freestyle.types.ViewVertex.edges_end"></a>

#### freestyle.types.ViewVertex.edges_end()

Returns an orientedViewEdgeIterator over the ViewEdges around this
ViewVertex, pointing after the last ViewEdge.

**Returns:**

An orientedViewEdgeIterator pointing after the last ViewEdge.

**Return type:**

[`orientedViewEdgeIterator`](#freestyle.types.orientedViewEdgeIterator "freestyle.types.orientedViewEdgeIterator")

<a id="freestyle.types.ViewVertex.edges_iterator"></a>

#### freestyle.types.ViewVertex.edges_iterator(edge)

Returns an orientedViewEdgeIterator pointing to the ViewEdge given
as argument.

**Parameters:**

**edge** ([`ViewEdge`](#freestyle.types.ViewEdge "freestyle.types.ViewEdge")) – A ViewEdge object.

**Returns:**

An orientedViewEdgeIterator pointing to the given ViewEdge.

**Return type:**

[`orientedViewEdgeIterator`](#freestyle.types.orientedViewEdgeIterator "freestyle.types.orientedViewEdgeIterator")

<a id="freestyle.types.ViewVertex.nature"></a>

#### freestyle.types.ViewVertex.nature

The nature of this ViewVertex.

**Type:**

[`Nature`](#freestyle.types.Nature "freestyle.types.Nature")

<a id="freestyle.types.orientedViewEdgeIterator"></a>

### class freestyle.types.orientedViewEdgeIterator

Class hierarchy: [`Iterator`](#freestyle.types.Iterator "freestyle.types.Iterator") > [`orientedViewEdgeIterator`](#freestyle.types.orientedViewEdgeIterator "freestyle.types.orientedViewEdgeIterator")

Class representing an iterator over oriented ViewEdges around a
[`ViewVertex`](#freestyle.types.ViewVertex "freestyle.types.ViewVertex"). This iterator allows a CCW iteration (in the image
plane). An instance of an orientedViewEdgeIterator can only be
obtained from a ViewVertex by calling edges_begin() or edges_end().

<a id="freestyle.types.orientedViewEdgeIterator.__init__"></a>

#### freestyle.types.orientedViewEdgeIterator.__init__(*args)

Accepted call signatures:

- `__init__()`
- `__init__(iBrother)`

Creates an [`orientedViewEdgeIterator`](#freestyle.types.orientedViewEdgeIterator "freestyle.types.orientedViewEdgeIterator") using either the
default constructor or the copy constructor.

**Parameters:**

**iBrother** ([`orientedViewEdgeIterator`](#freestyle.types.orientedViewEdgeIterator "freestyle.types.orientedViewEdgeIterator")) – An orientedViewEdgeIterator object.

<a id="freestyle.types.orientedViewEdgeIterator.object"></a>

#### freestyle.types.orientedViewEdgeIterator.object

The oriented ViewEdge (i.e., a tuple of the pointed ViewEdge and a boolean
value) currently pointed to by this iterator. If the boolean value is true,
the ViewEdge is incoming.

**Type:**

tuple[[`ViewEdge`](#freestyle.types.ViewEdge "freestyle.types.ViewEdge"), bool]

Special Methods

<a id="freestyle.types.orientedViewEdgeIterator.__iter__"></a>

#### freestyle.types.orientedViewEdgeIterator.__iter__()

**Return type:**

[`orientedViewEdgeIterator`](#freestyle.types.orientedViewEdgeIterator "freestyle.types.orientedViewEdgeIterator")

<a id="freestyle.types.orientedViewEdgeIterator.__next__"></a>

#### freestyle.types.orientedViewEdgeIterator.__next__()

**Return type:**

Any
