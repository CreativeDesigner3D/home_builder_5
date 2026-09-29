<!-- source: Blender Python API reference 5.2 / freestyle.chainingiterators.html -->

<a id="module-freestyle.chainingiterators"></a>

# Freestyle Chaining Iterators (freestyle.chainingiterators)

This module contains chaining iterators used for the chaining
operation to construct long strokes by concatenating feature edges
according to selected chaining rules. The module is also intended to
be a collection of examples for defining chaining iterators in Python.

<a id="freestyle.chainingiterators.ChainPredicateIterator"></a>

### class freestyle.chainingiterators.ChainPredicateIterator

Class hierarchy: [`freestyle.types.Iterator`](freestyle.types.md#freestyle.types.Iterator "freestyle.types.Iterator") >
[`freestyle.types.ViewEdgeIterator`](freestyle.types.md#freestyle.types.ViewEdgeIterator "freestyle.types.ViewEdgeIterator") >
[`freestyle.types.ChainingIterator`](freestyle.types.md#freestyle.types.ChainingIterator "freestyle.types.ChainingIterator") >
[`ChainPredicateIterator`](#freestyle.chainingiterators.ChainPredicateIterator "freestyle.chainingiterators.ChainPredicateIterator")

A “generic” user-controlled ViewEdge iterator. This iterator is in
particular built from a unary predicate and a binary predicate.
First, the unary predicate is evaluated for all potential next
ViewEdges in order to only keep the ones respecting a certain
constraint. Then, the binary predicate is evaluated on the current
ViewEdge together with each ViewEdge of the previous selection. The
first ViewEdge respecting both the unary predicate and the binary
predicate is kept as the next one. If none of the potential next
ViewEdge respects these two predicates, None is returned.

<a id="freestyle.chainingiterators.ChainPredicateIterator.__init__"></a>

#### freestyle.chainingiterators.ChainPredicateIterator.__init__(*args)

Accepted call signatures:

- `__init__(upred, bpred, restrict_to_selection=True, restrict_to_unvisited=True, begin=None, orientation=True)`
- `__init__(brother)`

Builds a ChainPredicateIterator from a unary predicate, a binary
predicate, a starting ViewEdge and its orientation or using the copy constructor.

**Parameters:**

- **upred** ([`freestyle.types.UnaryPredicate1D`](freestyle.types.md#freestyle.types.UnaryPredicate1D "freestyle.types.UnaryPredicate1D")) – The unary predicate that the next ViewEdge must satisfy.
- **bpred** ([`freestyle.types.BinaryPredicate1D`](freestyle.types.md#freestyle.types.BinaryPredicate1D "freestyle.types.BinaryPredicate1D")) – The binary predicate that the next ViewEdge must
  satisfy together with the actual pointed ViewEdge.
- **restrict_to_selection** (bool) – Indicates whether to force the chaining
  to stay within the set of selected ViewEdges or not.
- **restrict_to_unvisited** (bool) – Indicates whether a ViewEdge that has
  already been chained must be ignored ot not.
- **begin** ([`freestyle.types.ViewEdge`](freestyle.types.md#freestyle.types.ViewEdge "freestyle.types.ViewEdge") | None) – The ViewEdge from where to start the iteration.
- **orientation** (bool) – If true, we’ll look for the next ViewEdge among
  the ViewEdges that surround the ending ViewVertex of begin. If
  false, we’ll search over the ViewEdges surrounding the ending
  ViewVertex of begin.
- **brother** ([`ChainPredicateIterator`](#freestyle.chainingiterators.ChainPredicateIterator "freestyle.chainingiterators.ChainPredicateIterator")) – A ChainPredicateIterator object.

<a id="freestyle.chainingiterators.ChainSilhouetteIterator"></a>

### class freestyle.chainingiterators.ChainSilhouetteIterator

Class hierarchy: [`freestyle.types.Iterator`](freestyle.types.md#freestyle.types.Iterator "freestyle.types.Iterator") >
[`freestyle.types.ViewEdgeIterator`](freestyle.types.md#freestyle.types.ViewEdgeIterator "freestyle.types.ViewEdgeIterator") >
[`freestyle.types.ChainingIterator`](freestyle.types.md#freestyle.types.ChainingIterator "freestyle.types.ChainingIterator") >
[`ChainSilhouetteIterator`](#freestyle.chainingiterators.ChainSilhouetteIterator "freestyle.chainingiterators.ChainSilhouetteIterator")

A ViewEdge Iterator used to follow ViewEdges the most naturally. For
example, it will follow visible ViewEdges of same nature. As soon, as
the nature or the visibility changes, the iteration stops (by setting
the pointed ViewEdge to 0). In the case of an iteration over a set of
ViewEdge that are both Silhouette and Crease, there will be a
precedence of the silhouette over the crease criterion.

<a id="freestyle.chainingiterators.ChainSilhouetteIterator.__init__"></a>

#### freestyle.chainingiterators.ChainSilhouetteIterator.__init__(*args)

Accepted call signatures:

- `__init__(restrict_to_selection=True, begin=None, orientation=True)`
- `__init__(brother)`

Builds a ChainSilhouetteIterator from the first ViewEdge used for
iteration and its orientation or the copy constructor.

**Parameters:**

- **restrict_to_selection** (bool) – Indicates whether to force the chaining
  to stay within the set of selected ViewEdges or not.
- **begin** ([`freestyle.types.ViewEdge`](freestyle.types.md#freestyle.types.ViewEdge "freestyle.types.ViewEdge") | None) – The ViewEdge from where to start the iteration.
- **orientation** (bool) – If true, we’ll look for the next ViewEdge among
  the ViewEdges that surround the ending ViewVertex of begin. If
  false, we’ll search over the ViewEdges surrounding the ending
  ViewVertex of begin.
- **brother** ([`ChainSilhouetteIterator`](#freestyle.chainingiterators.ChainSilhouetteIterator "freestyle.chainingiterators.ChainSilhouetteIterator")) – A ChainSilhouetteIterator object.

<a id="freestyle.chainingiterators.pyChainSilhouetteIterator"></a>

### class freestyle.chainingiterators.pyChainSilhouetteIterator

Natural chaining iterator that follows the edges of the same nature
following the topology of objects, with decreasing priority for
silhouettes, then borders, then suggestive contours, then all other edge
types. A ViewEdge is only chained once.

<a id="freestyle.chainingiterators.pyChainSilhouetteIterator.init"></a>

#### freestyle.chainingiterators.pyChainSilhouetteIterator.init()

<a id="freestyle.chainingiterators.pyChainSilhouetteIterator.traverse"></a>

#### freestyle.chainingiterators.pyChainSilhouetteIterator.traverse(iter)

Returns the next ViewEdge to chain.

**Parameters:**

**iter** (`AdjacencyIterator`) – An adjacency iterator over the candidate ViewEdges.

**Returns:**

The next ViewEdge, or None to stop chaining.

**Return type:**

`ViewEdge` | None

<a id="freestyle.chainingiterators.pyChainSilhouetteGenericIterator"></a>

### class freestyle.chainingiterators.pyChainSilhouetteGenericIterator

Natural chaining iterator that follows the edges of the same nature
following the topology of objects, with decreasing priority for
silhouettes, then borders, then suggestive contours, then all other
edge types.

<a id="freestyle.chainingiterators.pyChainSilhouetteGenericIterator.__init__"></a>

#### freestyle.chainingiterators.pyChainSilhouetteGenericIterator.__init__(stayInSelection=True, stayInUnvisited=True)

Builds a pyChainSilhouetteGenericIterator object.

**Parameters:**

- **stayInSelection** (bool) – True if it is allowed to go out of the selection
- **stayInUnvisited** (bool) – May the same ViewEdge be chained twice

<a id="freestyle.chainingiterators.pyChainSilhouetteGenericIterator.init"></a>

#### freestyle.chainingiterators.pyChainSilhouetteGenericIterator.init()

<a id="freestyle.chainingiterators.pyChainSilhouetteGenericIterator.traverse"></a>

#### freestyle.chainingiterators.pyChainSilhouetteGenericIterator.traverse(iter)

Returns the next ViewEdge to chain.

**Parameters:**

**iter** (`AdjacencyIterator`) – An adjacency iterator over the candidate ViewEdges.

**Returns:**

The next ViewEdge, or None to stop chaining.

**Return type:**

`ViewEdge` | None

<a id="freestyle.chainingiterators.pyExternalContourChainingIterator"></a>

### class freestyle.chainingiterators.pyExternalContourChainingIterator

Chains by external contour

<a id="freestyle.chainingiterators.pyExternalContourChainingIterator.checkViewEdge"></a>

#### freestyle.chainingiterators.pyExternalContourChainingIterator.checkViewEdge(ve, orientation)

Tests whether a ViewEdge belongs to the external contour.

**Parameters:**

- **ve** (`ViewEdge`) – The ViewEdge to test.
- **orientation** (bool) – Iteration orientation.

**Return type:**

bool

<a id="freestyle.chainingiterators.pyExternalContourChainingIterator.init"></a>

#### freestyle.chainingiterators.pyExternalContourChainingIterator.init()

<a id="freestyle.chainingiterators.pyExternalContourChainingIterator.traverse"></a>

#### freestyle.chainingiterators.pyExternalContourChainingIterator.traverse(iter)

Returns the next ViewEdge to chain.

**Parameters:**

**iter** (`AdjacencyIterator`) – An adjacency iterator over the candidate ViewEdges.

**Returns:**

The next ViewEdge, or None to stop chaining.

**Return type:**

`ViewEdge` | None

<a id="freestyle.chainingiterators.pySketchyChainSilhouetteIterator"></a>

### class freestyle.chainingiterators.pySketchyChainSilhouetteIterator

Natural chaining iterator with a sketchy multiple touch. It chains the
same ViewEdge multiple times to achieve a sketchy effect.

<a id="freestyle.chainingiterators.pySketchyChainSilhouetteIterator.__init__"></a>

#### freestyle.chainingiterators.pySketchyChainSilhouetteIterator.__init__(nRounds=3, stayInSelection=True)

Builds a pySketchyChainSilhouetteIterator object.

**Parameters:**

- **nRounds** (int) – Number of times every Viewedge is chained.
- **stayInSelection** (bool) – if False, edges outside of the selection can be chained.

<a id="freestyle.chainingiterators.pySketchyChainSilhouetteIterator.init"></a>

#### freestyle.chainingiterators.pySketchyChainSilhouetteIterator.init()

<a id="freestyle.chainingiterators.pySketchyChainSilhouetteIterator.make_sketchy"></a>

#### freestyle.chainingiterators.pySketchyChainSilhouetteIterator.make_sketchy(ve)

Creates the sketchy effect by causing the chain to run from
the start again. (loop over itself again)

**Parameters:**

**ve** (`ViewEdge` | None) – The candidate ViewEdge, or None to fall back to the current edge.

**Return type:**

`ViewEdge` | None

<a id="freestyle.chainingiterators.pySketchyChainSilhouetteIterator.traverse"></a>

#### freestyle.chainingiterators.pySketchyChainSilhouetteIterator.traverse(iter)

Returns the next ViewEdge to chain.

**Parameters:**

**iter** (`AdjacencyIterator`) – An adjacency iterator over the candidate ViewEdges.

**Returns:**

The next ViewEdge, or None to stop chaining.

**Return type:**

`ViewEdge` | None

<a id="freestyle.chainingiterators.pySketchyChainingIterator"></a>

### class freestyle.chainingiterators.pySketchyChainingIterator

Chaining iterator designed for sketchy style. It chains the same
ViewEdge several times in order to produce multiple strokes per
ViewEdge.

<a id="freestyle.chainingiterators.pySketchyChainingIterator.init"></a>

#### freestyle.chainingiterators.pySketchyChainingIterator.init()

<a id="freestyle.chainingiterators.pySketchyChainingIterator.traverse"></a>

#### freestyle.chainingiterators.pySketchyChainingIterator.traverse(iter)

Returns the next ViewEdge to chain.

**Parameters:**

**iter** (`AdjacencyIterator`) – An adjacency iterator over the candidate ViewEdges.

**Returns:**

The next ViewEdge, or None to stop chaining.

**Return type:**

`ViewEdge` | None

<a id="freestyle.chainingiterators.pyFillOcclusionsRelativeChainingIterator"></a>

### class freestyle.chainingiterators.pyFillOcclusionsRelativeChainingIterator

Chaining iterator that fills small occlusions

<a id="freestyle.chainingiterators.pyFillOcclusionsRelativeChainingIterator.__init__"></a>

#### freestyle.chainingiterators.pyFillOcclusionsRelativeChainingIterator.__init__(percent)

Builds a pyFillOcclusionsRelativeChainingIterator object.

**Parameters:**

**percent** (float) – The maximal length of the occluded part, expressed
in a percentage of the total chain length.

<a id="freestyle.chainingiterators.pyFillOcclusionsRelativeChainingIterator.init"></a>

#### freestyle.chainingiterators.pyFillOcclusionsRelativeChainingIterator.init()

<a id="freestyle.chainingiterators.pyFillOcclusionsRelativeChainingIterator.traverse"></a>

#### freestyle.chainingiterators.pyFillOcclusionsRelativeChainingIterator.traverse(iter)

Returns the next ViewEdge to chain.

**Parameters:**

**iter** (`AdjacencyIterator`) – An adjacency iterator over the candidate ViewEdges.

**Returns:**

The next ViewEdge, or None to stop chaining.

**Return type:**

`ViewEdge` | None

<a id="freestyle.chainingiterators.pyFillOcclusionsAbsoluteChainingIterator"></a>

### class freestyle.chainingiterators.pyFillOcclusionsAbsoluteChainingIterator

Chaining iterator that fills small occlusions

<a id="freestyle.chainingiterators.pyFillOcclusionsAbsoluteChainingIterator.__init__"></a>

#### freestyle.chainingiterators.pyFillOcclusionsAbsoluteChainingIterator.__init__(length)

Builds a pyFillOcclusionsAbsoluteChainingIterator object.

**Parameters:**

**length** (int) – The maximum length of the occluded part in pixels.

<a id="freestyle.chainingiterators.pyFillOcclusionsAbsoluteChainingIterator.init"></a>

#### freestyle.chainingiterators.pyFillOcclusionsAbsoluteChainingIterator.init()

<a id="freestyle.chainingiterators.pyFillOcclusionsAbsoluteChainingIterator.traverse"></a>

#### freestyle.chainingiterators.pyFillOcclusionsAbsoluteChainingIterator.traverse(iter)

Returns the next ViewEdge to chain.

**Parameters:**

**iter** (`AdjacencyIterator`) – An adjacency iterator over the candidate ViewEdges.

**Returns:**

The next ViewEdge, or None to stop chaining.

**Return type:**

`ViewEdge` | None

<a id="freestyle.chainingiterators.pyFillOcclusionsAbsoluteAndRelativeChainingIterator"></a>

### class freestyle.chainingiterators.pyFillOcclusionsAbsoluteAndRelativeChainingIterator

Chaining iterator that fills small occlusions regardless of the
selection.

<a id="freestyle.chainingiterators.pyFillOcclusionsAbsoluteAndRelativeChainingIterator.__init__"></a>

#### freestyle.chainingiterators.pyFillOcclusionsAbsoluteAndRelativeChainingIterator.__init__(percent, l)

Builds a pyFillOcclusionsAbsoluteAndRelativeChainingIterator object.

**Parameters:**

- **percent** (float) – The maximal length of the occluded part as a
  percentage of the total chain length.
- **l** (float) – Absolute length.

<a id="freestyle.chainingiterators.pyFillOcclusionsAbsoluteAndRelativeChainingIterator.init"></a>

#### freestyle.chainingiterators.pyFillOcclusionsAbsoluteAndRelativeChainingIterator.init()

<a id="freestyle.chainingiterators.pyFillOcclusionsAbsoluteAndRelativeChainingIterator.traverse"></a>

#### freestyle.chainingiterators.pyFillOcclusionsAbsoluteAndRelativeChainingIterator.traverse(iter)

Returns the next ViewEdge to chain.

**Parameters:**

**iter** (`AdjacencyIterator`) – An adjacency iterator over the candidate ViewEdges.

**Returns:**

The next ViewEdge, or None to stop chaining.

**Return type:**

`ViewEdge` | None

<a id="freestyle.chainingiterators.pyFillQi0AbsoluteAndRelativeChainingIterator"></a>

### class freestyle.chainingiterators.pyFillQi0AbsoluteAndRelativeChainingIterator

Chaining iterator that fills small occlusions regardless of the
selection.

<a id="freestyle.chainingiterators.pyFillQi0AbsoluteAndRelativeChainingIterator.__init__"></a>

#### freestyle.chainingiterators.pyFillQi0AbsoluteAndRelativeChainingIterator.__init__(percent, l)

Builds a pyFillQi0AbsoluteAndRelativeChainingIterator object.

**Parameters:**

- **percent** (float) – The maximal length of the occluded part as a
  percentage of the total chain length.
- **l** (float) – Absolute length.

<a id="freestyle.chainingiterators.pyFillQi0AbsoluteAndRelativeChainingIterator.init"></a>

#### freestyle.chainingiterators.pyFillQi0AbsoluteAndRelativeChainingIterator.init()

<a id="freestyle.chainingiterators.pyFillQi0AbsoluteAndRelativeChainingIterator.traverse"></a>

#### freestyle.chainingiterators.pyFillQi0AbsoluteAndRelativeChainingIterator.traverse(iter)

Returns the next ViewEdge to chain.

**Parameters:**

**iter** (`AdjacencyIterator`) – An adjacency iterator over the candidate ViewEdges.

**Returns:**

The next ViewEdge, or None to stop chaining.

**Return type:**

`ViewEdge` | None

<a id="freestyle.chainingiterators.pyNoIdChainSilhouetteIterator"></a>

### class freestyle.chainingiterators.pyNoIdChainSilhouetteIterator

Natural chaining iterator that follows the edges of the same nature
following the topology of objects, with decreasing priority for
silhouettes, then borders, then suggestive contours, then all other edge
types. It won’t chain the same ViewEdge twice.

<a id="freestyle.chainingiterators.pyNoIdChainSilhouetteIterator.__init__"></a>

#### freestyle.chainingiterators.pyNoIdChainSilhouetteIterator.__init__(stayInSelection=True)

Builds a pyNoIdChainSilhouetteIterator object.

**Parameters:**

**stayInSelection** (bool) – True if it is allowed to go out of the selection

<a id="freestyle.chainingiterators.pyNoIdChainSilhouetteIterator.init"></a>

#### freestyle.chainingiterators.pyNoIdChainSilhouetteIterator.init()

<a id="freestyle.chainingiterators.pyNoIdChainSilhouetteIterator.traverse"></a>

#### freestyle.chainingiterators.pyNoIdChainSilhouetteIterator.traverse(iter)

Returns the next ViewEdge to chain.

**Parameters:**

**iter** (`AdjacencyIterator`) – An adjacency iterator over the candidate ViewEdges.

**Returns:**

The next ViewEdge, or None to stop chaining.

**Return type:**

`ViewEdge` | None
