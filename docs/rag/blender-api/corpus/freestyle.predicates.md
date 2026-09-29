<!-- source: Blender Python API reference 5.2 / freestyle.predicates.html -->

<a id="module-freestyle.predicates"></a>

# Freestyle Predicates (freestyle.predicates)

This module contains predicates operating on vertices (0D elements)
and polylines (1D elements). It is also intended to be a collection
of examples for predicate definition in Python.

User-defined predicates inherit one of the following base classes,
depending on the object type (0D or 1D) to operate on and the arity
(unary or binary):

- [`freestyle.types.BinaryPredicate0D`](freestyle.types.md#freestyle.types.BinaryPredicate0D "freestyle.types.BinaryPredicate0D")
- [`freestyle.types.BinaryPredicate1D`](freestyle.types.md#freestyle.types.BinaryPredicate1D "freestyle.types.BinaryPredicate1D")
- [`freestyle.types.UnaryPredicate0D`](freestyle.types.md#freestyle.types.UnaryPredicate0D "freestyle.types.UnaryPredicate0D")
- [`freestyle.types.UnaryPredicate1D`](freestyle.types.md#freestyle.types.UnaryPredicate1D "freestyle.types.UnaryPredicate1D")

<a id="freestyle.predicates.AndBP1D"></a>

### class freestyle.predicates.AndBP1D

<a id="freestyle.predicates.AndUP1D"></a>

### class freestyle.predicates.AndUP1D

<a id="freestyle.predicates.ContourUP1D"></a>

### class freestyle.predicates.ContourUP1D

Class hierarchy: [`freestyle.types.UnaryPredicate1D`](freestyle.types.md#freestyle.types.UnaryPredicate1D "freestyle.types.UnaryPredicate1D") > [`ContourUP1D`](#freestyle.predicates.ContourUP1D "freestyle.predicates.ContourUP1D")

<a id="freestyle.predicates.ContourUP1D.__call__"></a>

#### freestyle.predicates.ContourUP1D.__call__(inter)

Returns true if the Interface1D is a contour. An Interface1D is a
contour if it is bordered by a different shape on each of its sides.

**Parameters:**

**inter** ([`freestyle.types.Interface1D`](freestyle.types.md#freestyle.types.Interface1D "freestyle.types.Interface1D")) – An Interface1D object.

**Returns:**

True if the Interface1D is a contour, false otherwise.

**Return type:**

bool

<a id="freestyle.predicates.DensityLowerThanUP1D"></a>

### class freestyle.predicates.DensityLowerThanUP1D

Class hierarchy: [`freestyle.types.UnaryPredicate1D`](freestyle.types.md#freestyle.types.UnaryPredicate1D "freestyle.types.UnaryPredicate1D") > [`DensityLowerThanUP1D`](#freestyle.predicates.DensityLowerThanUP1D "freestyle.predicates.DensityLowerThanUP1D")

<a id="freestyle.predicates.DensityLowerThanUP1D.__init__"></a>

#### freestyle.predicates.DensityLowerThanUP1D.__init__(threshold, sigma=2.0)

Builds a DensityLowerThanUP1D object.

**Parameters:**

- **threshold** (float) – The value of the threshold density. Any Interface1D
  having a density lower than this threshold will match.
- **sigma** (float) – The sigma value defining the density evaluation window
  size used in the [`freestyle.functions.DensityF0D`](freestyle.functions.md#freestyle.functions.DensityF0D "freestyle.functions.DensityF0D") functor.

<a id="freestyle.predicates.DensityLowerThanUP1D.__call__"></a>

#### freestyle.predicates.DensityLowerThanUP1D.__call__(inter)

Returns true if the density evaluated for the Interface1D is less
than a user-defined density value.

**Parameters:**

**inter** ([`freestyle.types.Interface1D`](freestyle.types.md#freestyle.types.Interface1D "freestyle.types.Interface1D")) – An Interface1D object.

**Returns:**

True if the density is lower than a threshold.

**Return type:**

bool

<a id="freestyle.predicates.EqualToChainingTimeStampUP1D"></a>

### class freestyle.predicates.EqualToChainingTimeStampUP1D

Class hierarchy: [`freestyle.types.UnaryPredicate1D`](freestyle.types.md#freestyle.types.UnaryPredicate1D "freestyle.types.UnaryPredicate1D") > `freestyle.types.EqualToChainingTimeStampUP1D`

<a id="freestyle.predicates.EqualToChainingTimeStampUP1D.__init__"></a>

#### freestyle.predicates.EqualToChainingTimeStampUP1D.__init__(ts)

Builds a EqualToChainingTimeStampUP1D object.

**Parameters:**

**ts** (int) – A time stamp value.

<a id="freestyle.predicates.EqualToChainingTimeStampUP1D.__call__"></a>

#### freestyle.predicates.EqualToChainingTimeStampUP1D.__call__(inter)

Returns true if the Interface1D’s time stamp is equal to a certain
user-defined value.

**Parameters:**

**inter** ([`freestyle.types.Interface1D`](freestyle.types.md#freestyle.types.Interface1D "freestyle.types.Interface1D")) – An Interface1D object.

**Returns:**

True if the time stamp is equal to a user-defined value.

**Return type:**

bool

<a id="freestyle.predicates.EqualToTimeStampUP1D"></a>

### class freestyle.predicates.EqualToTimeStampUP1D

Class hierarchy: [`freestyle.types.UnaryPredicate1D`](freestyle.types.md#freestyle.types.UnaryPredicate1D "freestyle.types.UnaryPredicate1D") > [`EqualToTimeStampUP1D`](#freestyle.predicates.EqualToTimeStampUP1D "freestyle.predicates.EqualToTimeStampUP1D")

<a id="freestyle.predicates.EqualToTimeStampUP1D.__init__"></a>

#### freestyle.predicates.EqualToTimeStampUP1D.__init__(ts)

Builds a EqualToTimeStampUP1D object.

**Parameters:**

**ts** (int) – A time stamp value.

<a id="freestyle.predicates.EqualToTimeStampUP1D.__call__"></a>

#### freestyle.predicates.EqualToTimeStampUP1D.__call__(inter)

Returns true if the Interface1D’s time stamp is equal to a certain
user-defined value.

**Parameters:**

**inter** ([`freestyle.types.Interface1D`](freestyle.types.md#freestyle.types.Interface1D "freestyle.types.Interface1D")) – An Interface1D object.

**Returns:**

True if the time stamp is equal to a user-defined value.

**Return type:**

bool

<a id="freestyle.predicates.ExternalContourUP1D"></a>

### class freestyle.predicates.ExternalContourUP1D

Class hierarchy: [`freestyle.types.UnaryPredicate1D`](freestyle.types.md#freestyle.types.UnaryPredicate1D "freestyle.types.UnaryPredicate1D") > [`ExternalContourUP1D`](#freestyle.predicates.ExternalContourUP1D "freestyle.predicates.ExternalContourUP1D")

<a id="freestyle.predicates.ExternalContourUP1D.__call__"></a>

#### freestyle.predicates.ExternalContourUP1D.__call__(inter)

Returns true if the Interface1D is an external contour.
An Interface1D is an external contour if it is bordered by no shape on
one of its sides.

**Parameters:**

**inter** ([`freestyle.types.Interface1D`](freestyle.types.md#freestyle.types.Interface1D "freestyle.types.Interface1D")) – An Interface1D object.

**Returns:**

True if the Interface1D is an external contour, false
otherwise.

**Return type:**

bool

<a id="freestyle.predicates.FalseBP1D"></a>

### class freestyle.predicates.FalseBP1D

Class hierarchy: [`freestyle.types.BinaryPredicate1D`](freestyle.types.md#freestyle.types.BinaryPredicate1D "freestyle.types.BinaryPredicate1D") > [`FalseBP1D`](#freestyle.predicates.FalseBP1D "freestyle.predicates.FalseBP1D")

<a id="freestyle.predicates.FalseBP1D.__call__"></a>

#### freestyle.predicates.FalseBP1D.__call__(inter1, inter2)

Always returns false.

**Parameters:**

- **inter1** ([`freestyle.types.Interface1D`](freestyle.types.md#freestyle.types.Interface1D "freestyle.types.Interface1D")) – The first Interface1D object.
- **inter2** ([`freestyle.types.Interface1D`](freestyle.types.md#freestyle.types.Interface1D "freestyle.types.Interface1D")) – The second Interface1D object.

**Returns:**

False.

**Return type:**

bool

<a id="freestyle.predicates.FalseUP0D"></a>

### class freestyle.predicates.FalseUP0D

Class hierarchy: [`freestyle.types.UnaryPredicate0D`](freestyle.types.md#freestyle.types.UnaryPredicate0D "freestyle.types.UnaryPredicate0D") > [`FalseUP0D`](#freestyle.predicates.FalseUP0D "freestyle.predicates.FalseUP0D")

<a id="freestyle.predicates.FalseUP0D.__call__"></a>

#### freestyle.predicates.FalseUP0D.__call__(it)

Always returns false.

**Parameters:**

**it** ([`freestyle.types.Interface0DIterator`](freestyle.types.md#freestyle.types.Interface0DIterator "freestyle.types.Interface0DIterator")) – An Interface0DIterator object.

**Returns:**

False.

**Return type:**

bool

<a id="freestyle.predicates.FalseUP1D"></a>

### class freestyle.predicates.FalseUP1D

Class hierarchy: [`freestyle.types.UnaryPredicate1D`](freestyle.types.md#freestyle.types.UnaryPredicate1D "freestyle.types.UnaryPredicate1D") > [`FalseUP1D`](#freestyle.predicates.FalseUP1D "freestyle.predicates.FalseUP1D")

<a id="freestyle.predicates.FalseUP1D.__call__"></a>

#### freestyle.predicates.FalseUP1D.__call__(inter)

Always returns false.

**Parameters:**

**inter** ([`freestyle.types.Interface1D`](freestyle.types.md#freestyle.types.Interface1D "freestyle.types.Interface1D")) – An Interface1D object.

**Returns:**

False.

**Return type:**

bool

<a id="freestyle.predicates.Length2DBP1D"></a>

### class freestyle.predicates.Length2DBP1D

Class hierarchy: [`freestyle.types.BinaryPredicate1D`](freestyle.types.md#freestyle.types.BinaryPredicate1D "freestyle.types.BinaryPredicate1D") > [`Length2DBP1D`](#freestyle.predicates.Length2DBP1D "freestyle.predicates.Length2DBP1D")

<a id="freestyle.predicates.Length2DBP1D.__call__"></a>

#### freestyle.predicates.Length2DBP1D.__call__(inter1, inter2)

Returns true if the 2D length of inter1 is less than the 2D length
of inter2.

**Parameters:**

- **inter1** ([`freestyle.types.Interface1D`](freestyle.types.md#freestyle.types.Interface1D "freestyle.types.Interface1D")) – The first Interface1D object.
- **inter2** ([`freestyle.types.Interface1D`](freestyle.types.md#freestyle.types.Interface1D "freestyle.types.Interface1D")) – The second Interface1D object.

**Returns:**

True or false.

**Return type:**

bool

<a id="freestyle.predicates.MaterialBP1D"></a>

### class freestyle.predicates.MaterialBP1D

Checks whether the two supplied ViewEdges have the same material.

<a id="freestyle.predicates.NotBP1D"></a>

### class freestyle.predicates.NotBP1D

<a id="freestyle.predicates.NotUP1D"></a>

### class freestyle.predicates.NotUP1D

<a id="freestyle.predicates.ObjectNamesUP1D"></a>

### class freestyle.predicates.ObjectNamesUP1D

<a id="freestyle.predicates.OrBP1D"></a>

### class freestyle.predicates.OrBP1D

<a id="freestyle.predicates.OrUP1D"></a>

### class freestyle.predicates.OrUP1D

<a id="freestyle.predicates.QuantitativeInvisibilityRangeUP1D"></a>

### class freestyle.predicates.QuantitativeInvisibilityRangeUP1D

<a id="freestyle.predicates.QuantitativeInvisibilityUP1D"></a>

### class freestyle.predicates.QuantitativeInvisibilityUP1D

Class hierarchy: [`freestyle.types.UnaryPredicate1D`](freestyle.types.md#freestyle.types.UnaryPredicate1D "freestyle.types.UnaryPredicate1D") > [`QuantitativeInvisibilityUP1D`](#freestyle.predicates.QuantitativeInvisibilityUP1D "freestyle.predicates.QuantitativeInvisibilityUP1D")

<a id="freestyle.predicates.QuantitativeInvisibilityUP1D.__init__"></a>

#### freestyle.predicates.QuantitativeInvisibilityUP1D.__init__(qi=0)

Builds a QuantitativeInvisibilityUP1D object.

**Parameters:**

**qi** (int) – The Quantitative Invisibility you want the Interface1D to
have.

<a id="freestyle.predicates.QuantitativeInvisibilityUP1D.__call__"></a>

#### freestyle.predicates.QuantitativeInvisibilityUP1D.__call__(inter)

Returns true if the Quantitative Invisibility evaluated at an
Interface1D, using the
[`freestyle.functions.QuantitativeInvisibilityF1D`](freestyle.functions.md#freestyle.functions.QuantitativeInvisibilityF1D "freestyle.functions.QuantitativeInvisibilityF1D") functor,
equals a certain user-defined value.

**Parameters:**

**inter** ([`freestyle.types.Interface1D`](freestyle.types.md#freestyle.types.Interface1D "freestyle.types.Interface1D")) – An Interface1D object.

**Returns:**

True if Quantitative Invisibility equals a user-defined
value.

**Return type:**

bool

<a id="freestyle.predicates.SameShapeIdBP1D"></a>

### class freestyle.predicates.SameShapeIdBP1D

Class hierarchy: [`freestyle.types.BinaryPredicate1D`](freestyle.types.md#freestyle.types.BinaryPredicate1D "freestyle.types.BinaryPredicate1D") > [`SameShapeIdBP1D`](#freestyle.predicates.SameShapeIdBP1D "freestyle.predicates.SameShapeIdBP1D")

<a id="freestyle.predicates.SameShapeIdBP1D.__call__"></a>

#### freestyle.predicates.SameShapeIdBP1D.__call__(inter1, inter2)

Returns true if inter1 and inter2 belong to the same shape.

**Parameters:**

- **inter1** ([`freestyle.types.Interface1D`](freestyle.types.md#freestyle.types.Interface1D "freestyle.types.Interface1D")) – The first Interface1D object.
- **inter2** ([`freestyle.types.Interface1D`](freestyle.types.md#freestyle.types.Interface1D "freestyle.types.Interface1D")) – The second Interface1D object.

**Returns:**

True or false.

**Return type:**

bool

<a id="freestyle.predicates.ShapeUP1D"></a>

### class freestyle.predicates.ShapeUP1D

Class hierarchy: [`freestyle.types.UnaryPredicate1D`](freestyle.types.md#freestyle.types.UnaryPredicate1D "freestyle.types.UnaryPredicate1D") > [`ShapeUP1D`](#freestyle.predicates.ShapeUP1D "freestyle.predicates.ShapeUP1D")

<a id="freestyle.predicates.ShapeUP1D.__init__"></a>

#### freestyle.predicates.ShapeUP1D.__init__(first, second=0)

Builds a ShapeUP1D object.

**Parameters:**

- **first** (int) – The first Id component.
- **second** (int) – The second Id component.

<a id="freestyle.predicates.ShapeUP1D.__call__"></a>

#### freestyle.predicates.ShapeUP1D.__call__(inter)

Returns true if the shape to which the Interface1D belongs to has the
same [`freestyle.types.Id`](freestyle.types.md#freestyle.types.Id "freestyle.types.Id") as the one specified by the user.

**Parameters:**

**inter** ([`freestyle.types.Interface1D`](freestyle.types.md#freestyle.types.Interface1D "freestyle.types.Interface1D")) – An Interface1D object.

**Returns:**

True if Interface1D belongs to the shape of the
user-specified Id.

**Return type:**

bool

<a id="freestyle.predicates.TrueBP1D"></a>

### class freestyle.predicates.TrueBP1D

Class hierarchy: [`freestyle.types.BinaryPredicate1D`](freestyle.types.md#freestyle.types.BinaryPredicate1D "freestyle.types.BinaryPredicate1D") > [`TrueBP1D`](#freestyle.predicates.TrueBP1D "freestyle.predicates.TrueBP1D")

<a id="freestyle.predicates.TrueBP1D.__call__"></a>

#### freestyle.predicates.TrueBP1D.__call__(inter1, inter2)

Always returns true.

**Parameters:**

- **inter1** ([`freestyle.types.Interface1D`](freestyle.types.md#freestyle.types.Interface1D "freestyle.types.Interface1D")) – The first Interface1D object.
- **inter2** ([`freestyle.types.Interface1D`](freestyle.types.md#freestyle.types.Interface1D "freestyle.types.Interface1D")) – The second Interface1D object.

**Returns:**

True.

**Return type:**

bool

<a id="freestyle.predicates.TrueUP0D"></a>

### class freestyle.predicates.TrueUP0D

Class hierarchy: [`freestyle.types.UnaryPredicate0D`](freestyle.types.md#freestyle.types.UnaryPredicate0D "freestyle.types.UnaryPredicate0D") > [`TrueUP0D`](#freestyle.predicates.TrueUP0D "freestyle.predicates.TrueUP0D")

<a id="freestyle.predicates.TrueUP0D.__call__"></a>

#### freestyle.predicates.TrueUP0D.__call__(it)

Always returns true.

**Parameters:**

**it** ([`freestyle.types.Interface0DIterator`](freestyle.types.md#freestyle.types.Interface0DIterator "freestyle.types.Interface0DIterator")) – An Interface0DIterator object.

**Returns:**

True.

**Return type:**

bool

<a id="freestyle.predicates.TrueUP1D"></a>

### class freestyle.predicates.TrueUP1D

Class hierarchy: [`freestyle.types.UnaryPredicate1D`](freestyle.types.md#freestyle.types.UnaryPredicate1D "freestyle.types.UnaryPredicate1D") > [`TrueUP1D`](#freestyle.predicates.TrueUP1D "freestyle.predicates.TrueUP1D")

<a id="freestyle.predicates.TrueUP1D.__call__"></a>

#### freestyle.predicates.TrueUP1D.__call__(inter)

Always returns true.

**Parameters:**

**inter** ([`freestyle.types.Interface1D`](freestyle.types.md#freestyle.types.Interface1D "freestyle.types.Interface1D")) – An Interface1D object.

**Returns:**

True.

**Return type:**

bool

<a id="freestyle.predicates.ViewMapGradientNormBP1D"></a>

### class freestyle.predicates.ViewMapGradientNormBP1D

Class hierarchy: [`freestyle.types.BinaryPredicate1D`](freestyle.types.md#freestyle.types.BinaryPredicate1D "freestyle.types.BinaryPredicate1D") > [`ViewMapGradientNormBP1D`](#freestyle.predicates.ViewMapGradientNormBP1D "freestyle.predicates.ViewMapGradientNormBP1D")

<a id="freestyle.predicates.ViewMapGradientNormBP1D.__init__"></a>

#### freestyle.predicates.ViewMapGradientNormBP1D.__init__(level, integration_type=IntegrationType.MEAN, sampling=2.0)

Builds a ViewMapGradientNormBP1D object.

**Parameters:**

- **level** (int) – The level of the pyramid from which the pixel must be
  read.
- **integration_type** ([`freestyle.types.IntegrationType`](freestyle.types.md#freestyle.types.IntegrationType "freestyle.types.IntegrationType")) – The integration method used to compute a single value
  from a set of values.
- **sampling** (float) – The resolution used to sample the chain:
  GetViewMapGradientNormF0D is evaluated at each sample point and
  the result is obtained by combining the resulting values into a
  single one, following the method specified by integration_type.

<a id="freestyle.predicates.ViewMapGradientNormBP1D.__call__"></a>

#### freestyle.predicates.ViewMapGradientNormBP1D.__call__(inter1, inter2)

Returns true if the evaluation of the Gradient norm Function is
higher for inter1 than for inter2.

**Parameters:**

- **inter1** ([`freestyle.types.Interface1D`](freestyle.types.md#freestyle.types.Interface1D "freestyle.types.Interface1D")) – The first Interface1D object.
- **inter2** ([`freestyle.types.Interface1D`](freestyle.types.md#freestyle.types.Interface1D "freestyle.types.Interface1D")) – The second Interface1D object.

**Returns:**

True or false.

**Return type:**

bool

<a id="freestyle.predicates.WithinImageBoundaryUP1D"></a>

### class freestyle.predicates.WithinImageBoundaryUP1D

Class hierarchy: [`freestyle.types.UnaryPredicate1D`](freestyle.types.md#freestyle.types.UnaryPredicate1D "freestyle.types.UnaryPredicate1D") > [`WithinImageBoundaryUP1D`](#freestyle.predicates.WithinImageBoundaryUP1D "freestyle.predicates.WithinImageBoundaryUP1D")

<a id="freestyle.predicates.WithinImageBoundaryUP1D.__init__"></a>

#### freestyle.predicates.WithinImageBoundaryUP1D.__init__(xmin, ymin, xmax, ymax)

Builds an WithinImageBoundaryUP1D object.

**Parameters:**

- **xmin** (float) – X lower bound of the image boundary.
- **ymin** (float) – Y lower bound of the image boundary.
- **xmax** (float) – X upper bound of the image boundary.
- **ymax** (float) – Y upper bound of the image boundary.

<a id="freestyle.predicates.WithinImageBoundaryUP1D.__call__"></a>

#### freestyle.predicates.WithinImageBoundaryUP1D.__call__(inter)

Returns true if the Interface1D intersects with image boundary.

**Parameters:**

**inter** ([`freestyle.types.Interface1D`](freestyle.types.md#freestyle.types.Interface1D "freestyle.types.Interface1D")) – The Interface1D to test.

**Return type:**

bool

<a id="freestyle.predicates.pyBackTVertexUP0D"></a>

### class freestyle.predicates.pyBackTVertexUP0D

Check whether an Interface0DIterator references a TVertex and is
the one that is hidden (inferred from the context).

<a id="freestyle.predicates.pyClosedCurveUP1D"></a>

### class freestyle.predicates.pyClosedCurveUP1D

<a id="freestyle.predicates.pyDensityFunctorUP1D"></a>

### class freestyle.predicates.pyDensityFunctorUP1D

<a id="freestyle.predicates.pyDensityUP1D"></a>

### class freestyle.predicates.pyDensityUP1D

<a id="freestyle.predicates.pyDensityVariableSigmaUP1D"></a>

### class freestyle.predicates.pyDensityVariableSigmaUP1D

<a id="freestyle.predicates.pyHighDensityAnisotropyUP1D"></a>

### class freestyle.predicates.pyHighDensityAnisotropyUP1D

<a id="freestyle.predicates.pyHighDirectionalViewMapDensityUP1D"></a>

### class freestyle.predicates.pyHighDirectionalViewMapDensityUP1D

<a id="freestyle.predicates.pyHighSteerableViewMapDensityUP1D"></a>

### class freestyle.predicates.pyHighSteerableViewMapDensityUP1D

<a id="freestyle.predicates.pyHighViewMapDensityUP1D"></a>

### class freestyle.predicates.pyHighViewMapDensityUP1D

<a id="freestyle.predicates.pyHighViewMapGradientNormUP1D"></a>

### class freestyle.predicates.pyHighViewMapGradientNormUP1D

<a id="freestyle.predicates.pyHigherCurvature2DAngleUP0D"></a>

### class freestyle.predicates.pyHigherCurvature2DAngleUP0D

<a id="freestyle.predicates.pyHigherLengthUP1D"></a>

### class freestyle.predicates.pyHigherLengthUP1D

<a id="freestyle.predicates.pyHigherNumberOfTurnsUP1D"></a>

### class freestyle.predicates.pyHigherNumberOfTurnsUP1D

<a id="freestyle.predicates.pyIsInOccludersListUP1D"></a>

### class freestyle.predicates.pyIsInOccludersListUP1D

<a id="freestyle.predicates.pyIsOccludedByIdListUP1D"></a>

### class freestyle.predicates.pyIsOccludedByIdListUP1D

<a id="freestyle.predicates.pyIsOccludedByItselfUP1D"></a>

### class freestyle.predicates.pyIsOccludedByItselfUP1D

<a id="freestyle.predicates.pyIsOccludedByUP1D"></a>

### class freestyle.predicates.pyIsOccludedByUP1D

<a id="freestyle.predicates.pyLengthBP1D"></a>

### class freestyle.predicates.pyLengthBP1D

<a id="freestyle.predicates.pyLowDirectionalViewMapDensityUP1D"></a>

### class freestyle.predicates.pyLowDirectionalViewMapDensityUP1D

<a id="freestyle.predicates.pyLowSteerableViewMapDensityUP1D"></a>

### class freestyle.predicates.pyLowSteerableViewMapDensityUP1D

<a id="freestyle.predicates.pyNFirstUP1D"></a>

### class freestyle.predicates.pyNFirstUP1D

<a id="freestyle.predicates.pyNatureBP1D"></a>

### class freestyle.predicates.pyNatureBP1D

<a id="freestyle.predicates.pyNatureUP1D"></a>

### class freestyle.predicates.pyNatureUP1D

<a id="freestyle.predicates.pyParameterUP0D"></a>

### class freestyle.predicates.pyParameterUP0D

<a id="freestyle.predicates.pyParameterUP0DGoodOne"></a>

### class freestyle.predicates.pyParameterUP0DGoodOne

<a id="freestyle.predicates.pyProjectedXBP1D"></a>

### class freestyle.predicates.pyProjectedXBP1D

<a id="freestyle.predicates.pyProjectedYBP1D"></a>

### class freestyle.predicates.pyProjectedYBP1D

<a id="freestyle.predicates.pyShapeIdListUP1D"></a>

### class freestyle.predicates.pyShapeIdListUP1D

<a id="freestyle.predicates.pyShapeIdUP1D"></a>

### class freestyle.predicates.pyShapeIdUP1D

<a id="freestyle.predicates.pyShuffleBP1D"></a>

### class freestyle.predicates.pyShuffleBP1D

<a id="freestyle.predicates.pySilhouetteFirstBP1D"></a>

### class freestyle.predicates.pySilhouetteFirstBP1D

<a id="freestyle.predicates.pyUEqualsUP0D"></a>

### class freestyle.predicates.pyUEqualsUP0D

<a id="freestyle.predicates.pyVertexNatureUP0D"></a>

### class freestyle.predicates.pyVertexNatureUP0D

<a id="freestyle.predicates.pyViewMapGradientNormBP1D"></a>

### class freestyle.predicates.pyViewMapGradientNormBP1D

<a id="freestyle.predicates.pyZBP1D"></a>

### class freestyle.predicates.pyZBP1D

<a id="freestyle.predicates.pyZDiscontinuityBP1D"></a>

### class freestyle.predicates.pyZDiscontinuityBP1D

<a id="freestyle.predicates.pyZSmallerUP1D"></a>

### class freestyle.predicates.pyZSmallerUP1D
