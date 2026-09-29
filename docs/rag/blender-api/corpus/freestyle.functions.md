<!-- source: Blender Python API reference 5.2 / freestyle.functions.html -->

<a id="module-freestyle.functions"></a>

# Freestyle Functions (freestyle.functions)

This module contains functions operating on vertices (0D elements) and
polylines (1D elements). The module is also intended to be a
collection of examples for function definition in Python.

User-defined functions inherit one of the following base classes,
depending on the object type (0D or 1D) to operate on and the return
value type:

- [`freestyle.types.UnaryFunction0DDouble`](freestyle.types.md#freestyle.types.UnaryFunction0DDouble "freestyle.types.UnaryFunction0DDouble")
- [`freestyle.types.UnaryFunction0DEdgeNature`](freestyle.types.md#freestyle.types.UnaryFunction0DEdgeNature "freestyle.types.UnaryFunction0DEdgeNature")
- [`freestyle.types.UnaryFunction0DFloat`](freestyle.types.md#freestyle.types.UnaryFunction0DFloat "freestyle.types.UnaryFunction0DFloat")
- [`freestyle.types.UnaryFunction0DId`](freestyle.types.md#freestyle.types.UnaryFunction0DId "freestyle.types.UnaryFunction0DId")
- [`freestyle.types.UnaryFunction0DMaterial`](freestyle.types.md#freestyle.types.UnaryFunction0DMaterial "freestyle.types.UnaryFunction0DMaterial")
- [`freestyle.types.UnaryFunction0DUnsigned`](freestyle.types.md#freestyle.types.UnaryFunction0DUnsigned "freestyle.types.UnaryFunction0DUnsigned")
- [`freestyle.types.UnaryFunction0DVec2f`](freestyle.types.md#freestyle.types.UnaryFunction0DVec2f "freestyle.types.UnaryFunction0DVec2f")
- [`freestyle.types.UnaryFunction0DVec3f`](freestyle.types.md#freestyle.types.UnaryFunction0DVec3f "freestyle.types.UnaryFunction0DVec3f")
- [`freestyle.types.UnaryFunction0DVectorViewShape`](freestyle.types.md#freestyle.types.UnaryFunction0DVectorViewShape "freestyle.types.UnaryFunction0DVectorViewShape")
- [`freestyle.types.UnaryFunction0DViewShape`](freestyle.types.md#freestyle.types.UnaryFunction0DViewShape "freestyle.types.UnaryFunction0DViewShape")
- [`freestyle.types.UnaryFunction1DDouble`](freestyle.types.md#freestyle.types.UnaryFunction1DDouble "freestyle.types.UnaryFunction1DDouble")
- [`freestyle.types.UnaryFunction1DEdgeNature`](freestyle.types.md#freestyle.types.UnaryFunction1DEdgeNature "freestyle.types.UnaryFunction1DEdgeNature")
- [`freestyle.types.UnaryFunction1DFloat`](freestyle.types.md#freestyle.types.UnaryFunction1DFloat "freestyle.types.UnaryFunction1DFloat")
- [`freestyle.types.UnaryFunction1DUnsigned`](freestyle.types.md#freestyle.types.UnaryFunction1DUnsigned "freestyle.types.UnaryFunction1DUnsigned")
- [`freestyle.types.UnaryFunction1DVec2f`](freestyle.types.md#freestyle.types.UnaryFunction1DVec2f "freestyle.types.UnaryFunction1DVec2f")
- [`freestyle.types.UnaryFunction1DVec3f`](freestyle.types.md#freestyle.types.UnaryFunction1DVec3f "freestyle.types.UnaryFunction1DVec3f")
- [`freestyle.types.UnaryFunction1DVectorViewShape`](freestyle.types.md#freestyle.types.UnaryFunction1DVectorViewShape "freestyle.types.UnaryFunction1DVectorViewShape")
- [`freestyle.types.UnaryFunction1DVoid`](freestyle.types.md#freestyle.types.UnaryFunction1DVoid "freestyle.types.UnaryFunction1DVoid")

<a id="freestyle.functions.ChainingTimeStampF1D"></a>

### class freestyle.functions.ChainingTimeStampF1D

Class hierarchy: [`freestyle.types.UnaryFunction1D`](freestyle.types.md#freestyle.types.UnaryFunction1D "freestyle.types.UnaryFunction1D") > [`freestyle.types.UnaryFunction1DVoid`](freestyle.types.md#freestyle.types.UnaryFunction1DVoid "freestyle.types.UnaryFunction1DVoid") > [`ChainingTimeStampF1D`](#freestyle.functions.ChainingTimeStampF1D "freestyle.functions.ChainingTimeStampF1D")

<a id="freestyle.functions.ChainingTimeStampF1D.__init__"></a>

#### freestyle.functions.ChainingTimeStampF1D.__init__()

Builds a ChainingTimeStampF1D object.

<a id="freestyle.functions.ChainingTimeStampF1D.__call__"></a>

#### freestyle.functions.ChainingTimeStampF1D.__call__(inter)

Sets the chaining time stamp of the Interface1D.

**Parameters:**

**inter** ([`freestyle.types.Interface1D`](freestyle.types.md#freestyle.types.Interface1D "freestyle.types.Interface1D")) – An Interface1D object.

<a id="freestyle.functions.Curvature2DAngleF0D"></a>

### class freestyle.functions.Curvature2DAngleF0D

Class hierarchy: [`freestyle.types.UnaryFunction0D`](freestyle.types.md#freestyle.types.UnaryFunction0D "freestyle.types.UnaryFunction0D") > [`freestyle.types.UnaryFunction0DDouble`](freestyle.types.md#freestyle.types.UnaryFunction0DDouble "freestyle.types.UnaryFunction0DDouble") > [`Curvature2DAngleF0D`](#freestyle.functions.Curvature2DAngleF0D "freestyle.functions.Curvature2DAngleF0D")

<a id="freestyle.functions.Curvature2DAngleF0D.__init__"></a>

#### freestyle.functions.Curvature2DAngleF0D.__init__()

Builds a Curvature2DAngleF0D object.

<a id="freestyle.functions.Curvature2DAngleF0D.__call__"></a>

#### freestyle.functions.Curvature2DAngleF0D.__call__(it)

Returns a real value giving the 2D curvature (as an angle) of the 1D
element to which the [`freestyle.types.Interface0D`](freestyle.types.md#freestyle.types.Interface0D "freestyle.types.Interface0D") pointed by
the Interface0DIterator belongs. The 2D curvature is evaluated at the
Interface0D.

**Parameters:**

**it** ([`freestyle.types.Interface0DIterator`](freestyle.types.md#freestyle.types.Interface0DIterator "freestyle.types.Interface0DIterator")) – An Interface0DIterator object.

**Returns:**

The 2D curvature of the 1D element evaluated at the
pointed Interface0D.

**Return type:**

float

<a id="freestyle.functions.Curvature2DAngleF1D"></a>

### class freestyle.functions.Curvature2DAngleF1D

Class hierarchy: [`freestyle.types.UnaryFunction1D`](freestyle.types.md#freestyle.types.UnaryFunction1D "freestyle.types.UnaryFunction1D") > [`freestyle.types.UnaryFunction1DDouble`](freestyle.types.md#freestyle.types.UnaryFunction1DDouble "freestyle.types.UnaryFunction1DDouble") > [`Curvature2DAngleF1D`](#freestyle.functions.Curvature2DAngleF1D "freestyle.functions.Curvature2DAngleF1D")

<a id="freestyle.functions.Curvature2DAngleF1D.__init__"></a>

#### freestyle.functions.Curvature2DAngleF1D.__init__(integration_type=IntegrationType.MEAN)

Builds a Curvature2DAngleF1D object.

**Parameters:**

**integration_type** ([`freestyle.types.IntegrationType`](freestyle.types.md#freestyle.types.IntegrationType "freestyle.types.IntegrationType")) – The integration method used to compute a single value
from a set of values.

<a id="freestyle.functions.Curvature2DAngleF1D.__call__"></a>

#### freestyle.functions.Curvature2DAngleF1D.__call__(inter)

Returns the 2D curvature as an angle for an Interface1D.

**Parameters:**

**inter** ([`freestyle.types.Interface1D`](freestyle.types.md#freestyle.types.Interface1D "freestyle.types.Interface1D")) – An Interface1D object.

**Returns:**

The 2D curvature as an angle.

**Return type:**

float

<a id="freestyle.functions.CurveMaterialF0D"></a>

### class freestyle.functions.CurveMaterialF0D

A replacement of the built-in MaterialF0D for stroke creation.
MaterialF0D does not work with Curves and Strokes. Line color
priority is used to pick one of the two materials at material
boundaries.

Notes: expects instances of CurvePoint to be iterated over
:   can return None if no fedge can be found

<a id="freestyle.functions.CurveNatureF0D"></a>

### class freestyle.functions.CurveNatureF0D

Class hierarchy: [`freestyle.types.UnaryFunction0D`](freestyle.types.md#freestyle.types.UnaryFunction0D "freestyle.types.UnaryFunction0D") > [`freestyle.types.UnaryFunction0DEdgeNature`](freestyle.types.md#freestyle.types.UnaryFunction0DEdgeNature "freestyle.types.UnaryFunction0DEdgeNature") > [`CurveNatureF0D`](#freestyle.functions.CurveNatureF0D "freestyle.functions.CurveNatureF0D")

<a id="freestyle.functions.CurveNatureF0D.__init__"></a>

#### freestyle.functions.CurveNatureF0D.__init__()

Builds a CurveNatureF0D object.

<a id="freestyle.functions.CurveNatureF0D.__call__"></a>

#### freestyle.functions.CurveNatureF0D.__call__(it)

Returns the [`freestyle.types.Nature`](freestyle.types.md#freestyle.types.Nature "freestyle.types.Nature") of the 1D element the
Interface0D pointed by the Interface0DIterator belongs to.

**Parameters:**

**it** ([`freestyle.types.Interface0DIterator`](freestyle.types.md#freestyle.types.Interface0DIterator "freestyle.types.Interface0DIterator")) – An Interface0DIterator object.

**Returns:**

The nature of the 1D element to which the pointed Interface0D
belongs.

**Return type:**

[`freestyle.types.Nature`](freestyle.types.md#freestyle.types.Nature "freestyle.types.Nature")

<a id="freestyle.functions.CurveNatureF1D"></a>

### class freestyle.functions.CurveNatureF1D

Class hierarchy: [`freestyle.types.UnaryFunction1D`](freestyle.types.md#freestyle.types.UnaryFunction1D "freestyle.types.UnaryFunction1D") > [`freestyle.types.UnaryFunction1DEdgeNature`](freestyle.types.md#freestyle.types.UnaryFunction1DEdgeNature "freestyle.types.UnaryFunction1DEdgeNature") > [`CurveNatureF1D`](#freestyle.functions.CurveNatureF1D "freestyle.functions.CurveNatureF1D")

<a id="freestyle.functions.CurveNatureF1D.__init__"></a>

#### freestyle.functions.CurveNatureF1D.__init__(integration_type=IntegrationType.MEAN)

Builds a CurveNatureF1D object.

**Parameters:**

**integration_type** ([`freestyle.types.IntegrationType`](freestyle.types.md#freestyle.types.IntegrationType "freestyle.types.IntegrationType")) – The integration method used to compute a single value
from a set of values.

<a id="freestyle.functions.CurveNatureF1D.__call__"></a>

#### freestyle.functions.CurveNatureF1D.__call__(inter)

Returns the nature of the Interface1D (silhouette, ridge, crease, and
so on). Except if the Interface1D is a
[`freestyle.types.ViewEdge`](freestyle.types.md#freestyle.types.ViewEdge "freestyle.types.ViewEdge"), this result might be ambiguous.
Indeed, the Interface1D might result from the gathering of several 1D
elements, each one being of a different nature. An integration
method, such as the MEAN, might give, in this case, irrelevant
results.

**Parameters:**

**inter** ([`freestyle.types.Interface1D`](freestyle.types.md#freestyle.types.Interface1D "freestyle.types.Interface1D")) – An Interface1D object.

**Returns:**

The nature of the Interface1D.

**Return type:**

[`freestyle.types.Nature`](freestyle.types.md#freestyle.types.Nature "freestyle.types.Nature")

<a id="freestyle.functions.DensityF0D"></a>

### class freestyle.functions.DensityF0D

Class hierarchy: [`freestyle.types.UnaryFunction0D`](freestyle.types.md#freestyle.types.UnaryFunction0D "freestyle.types.UnaryFunction0D") > [`freestyle.types.UnaryFunction0DDouble`](freestyle.types.md#freestyle.types.UnaryFunction0DDouble "freestyle.types.UnaryFunction0DDouble") > [`DensityF0D`](#freestyle.functions.DensityF0D "freestyle.functions.DensityF0D")

<a id="freestyle.functions.DensityF0D.__init__"></a>

#### freestyle.functions.DensityF0D.__init__(sigma=2.0)

Builds a DensityF0D object.

**Parameters:**

**sigma** (float) – The gaussian sigma value indicating the X value for
which the gaussian function is 0.5. It leads to the window size
value (the larger, the smoother).

<a id="freestyle.functions.DensityF0D.__call__"></a>

#### freestyle.functions.DensityF0D.__call__(it)

Returns the density of the (result) image evaluated at the
[`freestyle.types.Interface0D`](freestyle.types.md#freestyle.types.Interface0D "freestyle.types.Interface0D") pointed by the
Interface0DIterator. This density is evaluated using a pixels square
window around the evaluation point and integrating these values using
a gaussian.

**Parameters:**

**it** ([`freestyle.types.Interface0DIterator`](freestyle.types.md#freestyle.types.Interface0DIterator "freestyle.types.Interface0DIterator")) – An Interface0DIterator object.

**Returns:**

The density of the image evaluated at the pointed
Interface0D.

**Return type:**

float

<a id="freestyle.functions.DensityF1D"></a>

### class freestyle.functions.DensityF1D

Class hierarchy: [`freestyle.types.UnaryFunction1D`](freestyle.types.md#freestyle.types.UnaryFunction1D "freestyle.types.UnaryFunction1D") > [`freestyle.types.UnaryFunction1DDouble`](freestyle.types.md#freestyle.types.UnaryFunction1DDouble "freestyle.types.UnaryFunction1DDouble") > [`DensityF1D`](#freestyle.functions.DensityF1D "freestyle.functions.DensityF1D")

<a id="freestyle.functions.DensityF1D.__init__"></a>

#### freestyle.functions.DensityF1D.__init__(sigma=2.0, integration_type=IntegrationType.MEAN, sampling=2.0)

Builds a DensityF1D object.

**Parameters:**

- **sigma** (float) – The sigma used in DensityF0D and determining the window size
  used in each density query.
- **integration_type** ([`freestyle.types.IntegrationType`](freestyle.types.md#freestyle.types.IntegrationType "freestyle.types.IntegrationType")) – The integration method used to compute a single value
  from a set of values.
- **sampling** (float) – The resolution used to sample the chain: the
  corresponding 0D function is evaluated at each sample point and
  the result is obtained by combining the resulting values into a
  single one, following the method specified by integration_type.

<a id="freestyle.functions.DensityF1D.__call__"></a>

#### freestyle.functions.DensityF1D.__call__(inter)

Returns the density evaluated for an Interface1D. The density is
evaluated for a set of points along the Interface1D (using the
[`freestyle.functions.DensityF0D`](#freestyle.functions.DensityF0D "freestyle.functions.DensityF0D") functor) with a user-defined
sampling and then integrated into a single value using a user-defined
integration method.

**Parameters:**

**inter** ([`freestyle.types.Interface1D`](freestyle.types.md#freestyle.types.Interface1D "freestyle.types.Interface1D")) – An Interface1D object.

**Returns:**

The density evaluated for an Interface1D.

**Return type:**

float

<a id="freestyle.functions.GetCompleteViewMapDensityF1D"></a>

### class freestyle.functions.GetCompleteViewMapDensityF1D

Class hierarchy: [`freestyle.types.UnaryFunction1D`](freestyle.types.md#freestyle.types.UnaryFunction1D "freestyle.types.UnaryFunction1D") > [`freestyle.types.UnaryFunction1DDouble`](freestyle.types.md#freestyle.types.UnaryFunction1DDouble "freestyle.types.UnaryFunction1DDouble") > [`GetCompleteViewMapDensityF1D`](#freestyle.functions.GetCompleteViewMapDensityF1D "freestyle.functions.GetCompleteViewMapDensityF1D")

<a id="freestyle.functions.GetCompleteViewMapDensityF1D.__init__"></a>

#### freestyle.functions.GetCompleteViewMapDensityF1D.__init__(level, integration_type=IntegrationType.MEAN, sampling=2.0)

Builds a GetCompleteViewMapDensityF1D object.

**Parameters:**

- **level** (int) – The level of the pyramid from which the pixel must be
  read.
- **integration_type** ([`freestyle.types.IntegrationType`](freestyle.types.md#freestyle.types.IntegrationType "freestyle.types.IntegrationType")) – The integration method used to compute a single value
  from a set of values.
- **sampling** (float) – The resolution used to sample the chain: the
  corresponding 0D function is evaluated at each sample point and
  the result is obtained by combining the resulting values into a
  single one, following the method specified by integration_type.

<a id="freestyle.functions.GetCompleteViewMapDensityF1D.__call__"></a>

#### freestyle.functions.GetCompleteViewMapDensityF1D.__call__(inter)

Returns the density evaluated for an Interface1D in the complete
viewmap image. The density is evaluated for a set of points along the
Interface1D (using the
[`freestyle.functions.ReadCompleteViewMapPixelF0D`](#freestyle.functions.ReadCompleteViewMapPixelF0D "freestyle.functions.ReadCompleteViewMapPixelF0D") functor) and
then integrated into a single value using a user-defined integration
method.

**Parameters:**

**inter** ([`freestyle.types.Interface1D`](freestyle.types.md#freestyle.types.Interface1D "freestyle.types.Interface1D")) – An Interface1D object.

**Returns:**

The density evaluated for the Interface1D in the complete
viewmap image.

**Return type:**

float

<a id="freestyle.functions.GetCurvilinearAbscissaF0D"></a>

### class freestyle.functions.GetCurvilinearAbscissaF0D

Class hierarchy: [`freestyle.types.UnaryFunction0D`](freestyle.types.md#freestyle.types.UnaryFunction0D "freestyle.types.UnaryFunction0D") > [`freestyle.types.UnaryFunction0DFloat`](freestyle.types.md#freestyle.types.UnaryFunction0DFloat "freestyle.types.UnaryFunction0DFloat") > [`GetCurvilinearAbscissaF0D`](#freestyle.functions.GetCurvilinearAbscissaF0D "freestyle.functions.GetCurvilinearAbscissaF0D")

<a id="freestyle.functions.GetCurvilinearAbscissaF0D.__init__"></a>

#### freestyle.functions.GetCurvilinearAbscissaF0D.__init__()

Builds a GetCurvilinearAbscissaF0D object.

<a id="freestyle.functions.GetCurvilinearAbscissaF0D.__call__"></a>

#### freestyle.functions.GetCurvilinearAbscissaF0D.__call__(it)

Returns the curvilinear abscissa of the
[`freestyle.types.Interface0D`](freestyle.types.md#freestyle.types.Interface0D "freestyle.types.Interface0D") pointed by the
Interface0DIterator in the context of its 1D element.

**Parameters:**

**it** ([`freestyle.types.Interface0DIterator`](freestyle.types.md#freestyle.types.Interface0DIterator "freestyle.types.Interface0DIterator")) – An Interface0DIterator object.

**Returns:**

The curvilinear abscissa of the pointed Interface0D.

**Return type:**

float

<a id="freestyle.functions.GetDirectionalViewMapDensityF1D"></a>

### class freestyle.functions.GetDirectionalViewMapDensityF1D

Class hierarchy: [`freestyle.types.UnaryFunction1D`](freestyle.types.md#freestyle.types.UnaryFunction1D "freestyle.types.UnaryFunction1D") > [`freestyle.types.UnaryFunction1DDouble`](freestyle.types.md#freestyle.types.UnaryFunction1DDouble "freestyle.types.UnaryFunction1DDouble") > [`GetDirectionalViewMapDensityF1D`](#freestyle.functions.GetDirectionalViewMapDensityF1D "freestyle.functions.GetDirectionalViewMapDensityF1D")

<a id="freestyle.functions.GetDirectionalViewMapDensityF1D.__init__"></a>

#### freestyle.functions.GetDirectionalViewMapDensityF1D.__init__(orientation, level, integration_type=IntegrationType.MEAN, sampling=2.0)

Builds a GetDirectionalViewMapDensityF1D object.

**Parameters:**

- **orientation** (int) – The number of the directional map we must work
  with.
- **level** (int) – The level of the pyramid from which the pixel must be
  read.
- **integration_type** ([`freestyle.types.IntegrationType`](freestyle.types.md#freestyle.types.IntegrationType "freestyle.types.IntegrationType")) – The integration method used to compute a single value
  from a set of values.
- **sampling** (float) – The resolution used to sample the chain: the
  corresponding 0D function is evaluated at each sample point and
  the result is obtained by combining the resulting values into a
  single one, following the method specified by integration_type.

<a id="freestyle.functions.GetDirectionalViewMapDensityF1D.__call__"></a>

#### freestyle.functions.GetDirectionalViewMapDensityF1D.__call__(inter)

Returns the density evaluated for an Interface1D in of the steerable
viewmaps image. The direction telling which Directional map to choose
is explicitly specified by the user. The density is evaluated for a
set of points along the Interface1D (using the
[`freestyle.functions.ReadSteerableViewMapPixelF0D`](#freestyle.functions.ReadSteerableViewMapPixelF0D "freestyle.functions.ReadSteerableViewMapPixelF0D") functor) and
then integrated into a single value using a user-defined integration
method.

**Parameters:**

**inter** ([`freestyle.types.Interface1D`](freestyle.types.md#freestyle.types.Interface1D "freestyle.types.Interface1D")) – An Interface1D object.

**Returns:**

the density evaluated for an Interface1D in of the
steerable viewmaps image.

**Return type:**

float

<a id="freestyle.functions.GetOccludeeF0D"></a>

### class freestyle.functions.GetOccludeeF0D

Class hierarchy: [`freestyle.types.UnaryFunction0D`](freestyle.types.md#freestyle.types.UnaryFunction0D "freestyle.types.UnaryFunction0D") > [`freestyle.types.UnaryFunction0DViewShape`](freestyle.types.md#freestyle.types.UnaryFunction0DViewShape "freestyle.types.UnaryFunction0DViewShape") > [`GetOccludeeF0D`](#freestyle.functions.GetOccludeeF0D "freestyle.functions.GetOccludeeF0D")

<a id="freestyle.functions.GetOccludeeF0D.__init__"></a>

#### freestyle.functions.GetOccludeeF0D.__init__()

Builds a GetOccludeeF0D object.

<a id="freestyle.functions.GetOccludeeF0D.__call__"></a>

#### freestyle.functions.GetOccludeeF0D.__call__(it)

Returns the [`freestyle.types.ViewShape`](freestyle.types.md#freestyle.types.ViewShape "freestyle.types.ViewShape") that the Interface0D
pointed by the Interface0DIterator occludes.

**Parameters:**

**it** ([`freestyle.types.Interface0DIterator`](freestyle.types.md#freestyle.types.Interface0DIterator "freestyle.types.Interface0DIterator")) – An Interface0DIterator object.

**Returns:**

The ViewShape occluded by the pointed Interface0D.

**Return type:**

[`freestyle.types.ViewShape`](freestyle.types.md#freestyle.types.ViewShape "freestyle.types.ViewShape")

<a id="freestyle.functions.GetOccludeeF1D"></a>

### class freestyle.functions.GetOccludeeF1D

Class hierarchy: [`freestyle.types.UnaryFunction1D`](freestyle.types.md#freestyle.types.UnaryFunction1D "freestyle.types.UnaryFunction1D") > [`freestyle.types.UnaryFunction1DVectorViewShape`](freestyle.types.md#freestyle.types.UnaryFunction1DVectorViewShape "freestyle.types.UnaryFunction1DVectorViewShape") > [`GetOccludeeF1D`](#freestyle.functions.GetOccludeeF1D "freestyle.functions.GetOccludeeF1D")

<a id="freestyle.functions.GetOccludeeF1D.__init__"></a>

#### freestyle.functions.GetOccludeeF1D.__init__()

Builds a GetOccludeeF1D object.

<a id="freestyle.functions.GetOccludeeF1D.__call__"></a>

#### freestyle.functions.GetOccludeeF1D.__call__(inter)

Returns a list of occluded shapes covered by this Interface1D.

**Parameters:**

**inter** ([`freestyle.types.Interface1D`](freestyle.types.md#freestyle.types.Interface1D "freestyle.types.Interface1D")) – An Interface1D object.

**Returns:**

A list of occluded shapes covered by the Interface1D.

**Return type:**

list[[`freestyle.types.ViewShape`](freestyle.types.md#freestyle.types.ViewShape "freestyle.types.ViewShape")]

<a id="freestyle.functions.GetOccludersF0D"></a>

### class freestyle.functions.GetOccludersF0D

Class hierarchy: [`freestyle.types.UnaryFunction0D`](freestyle.types.md#freestyle.types.UnaryFunction0D "freestyle.types.UnaryFunction0D") > [`freestyle.types.UnaryFunction0DVectorViewShape`](freestyle.types.md#freestyle.types.UnaryFunction0DVectorViewShape "freestyle.types.UnaryFunction0DVectorViewShape") > [`GetOccludersF0D`](#freestyle.functions.GetOccludersF0D "freestyle.functions.GetOccludersF0D")

<a id="freestyle.functions.GetOccludersF0D.__init__"></a>

#### freestyle.functions.GetOccludersF0D.__init__()

Builds a GetOccludersF0D object.

<a id="freestyle.functions.GetOccludersF0D.__call__"></a>

#### freestyle.functions.GetOccludersF0D.__call__(it)

Returns a list of [`freestyle.types.ViewShape`](freestyle.types.md#freestyle.types.ViewShape "freestyle.types.ViewShape") occluding the
[`freestyle.types.Interface0D`](freestyle.types.md#freestyle.types.Interface0D "freestyle.types.Interface0D") pointed by the Interface0DIterator.

**Parameters:**

**it** ([`freestyle.types.Interface0DIterator`](freestyle.types.md#freestyle.types.Interface0DIterator "freestyle.types.Interface0DIterator")) – An Interface0DIterator object.

**Returns:**

A list of ViewShape objects occluding the pointed
Interface0D.

**Return type:**

list[[`freestyle.types.ViewShape`](freestyle.types.md#freestyle.types.ViewShape "freestyle.types.ViewShape")]

<a id="freestyle.functions.GetOccludersF1D"></a>

### class freestyle.functions.GetOccludersF1D

Class hierarchy: [`freestyle.types.UnaryFunction1D`](freestyle.types.md#freestyle.types.UnaryFunction1D "freestyle.types.UnaryFunction1D") > [`freestyle.types.UnaryFunction1DVectorViewShape`](freestyle.types.md#freestyle.types.UnaryFunction1DVectorViewShape "freestyle.types.UnaryFunction1DVectorViewShape") > [`GetOccludersF1D`](#freestyle.functions.GetOccludersF1D "freestyle.functions.GetOccludersF1D")

<a id="freestyle.functions.GetOccludersF1D.__init__"></a>

#### freestyle.functions.GetOccludersF1D.__init__()

Builds a GetOccludersF1D object.

<a id="freestyle.functions.GetOccludersF1D.__call__"></a>

#### freestyle.functions.GetOccludersF1D.__call__(inter)

Returns a list of occluding shapes that cover this Interface1D.

**Parameters:**

**inter** ([`freestyle.types.Interface1D`](freestyle.types.md#freestyle.types.Interface1D "freestyle.types.Interface1D")) – An Interface1D object.

**Returns:**

A list of occluding shapes that cover the Interface1D.

**Return type:**

list[[`freestyle.types.ViewShape`](freestyle.types.md#freestyle.types.ViewShape "freestyle.types.ViewShape")]

<a id="freestyle.functions.GetParameterF0D"></a>

### class freestyle.functions.GetParameterF0D

Class hierarchy: [`freestyle.types.UnaryFunction0D`](freestyle.types.md#freestyle.types.UnaryFunction0D "freestyle.types.UnaryFunction0D") > [`freestyle.types.UnaryFunction0DFloat`](freestyle.types.md#freestyle.types.UnaryFunction0DFloat "freestyle.types.UnaryFunction0DFloat") > [`GetParameterF0D`](#freestyle.functions.GetParameterF0D "freestyle.functions.GetParameterF0D")

<a id="freestyle.functions.GetParameterF0D.__init__"></a>

#### freestyle.functions.GetParameterF0D.__init__()

Builds a GetParameterF0D object.

<a id="freestyle.functions.GetParameterF0D.__call__"></a>

#### freestyle.functions.GetParameterF0D.__call__(it)

Returns the parameter of the [`freestyle.types.Interface0D`](freestyle.types.md#freestyle.types.Interface0D "freestyle.types.Interface0D")
pointed by the Interface0DIterator in the context of its 1D element.

**Parameters:**

**it** ([`freestyle.types.Interface0DIterator`](freestyle.types.md#freestyle.types.Interface0DIterator "freestyle.types.Interface0DIterator")) – An Interface0DIterator object.

**Returns:**

The parameter of an Interface0D.

**Return type:**

float

<a id="freestyle.functions.GetProjectedXF0D"></a>

### class freestyle.functions.GetProjectedXF0D

Class hierarchy: [`freestyle.types.UnaryFunction0D`](freestyle.types.md#freestyle.types.UnaryFunction0D "freestyle.types.UnaryFunction0D") > [`freestyle.types.UnaryFunction0DDouble`](freestyle.types.md#freestyle.types.UnaryFunction0DDouble "freestyle.types.UnaryFunction0DDouble") > [`GetProjectedXF0D`](#freestyle.functions.GetProjectedXF0D "freestyle.functions.GetProjectedXF0D")

<a id="freestyle.functions.GetProjectedXF0D.__init__"></a>

#### freestyle.functions.GetProjectedXF0D.__init__()

Builds a GetProjectedXF0D object.

<a id="freestyle.functions.GetProjectedXF0D.__call__"></a>

#### freestyle.functions.GetProjectedXF0D.__call__(it)

Returns the X 3D projected coordinate of the [`freestyle.types.Interface0D`](freestyle.types.md#freestyle.types.Interface0D "freestyle.types.Interface0D")
pointed by the Interface0DIterator.

**Parameters:**

**it** ([`freestyle.types.Interface0DIterator`](freestyle.types.md#freestyle.types.Interface0DIterator "freestyle.types.Interface0DIterator")) – An Interface0DIterator object.

**Returns:**

The X 3D projected coordinate of the pointed Interface0D.

**Return type:**

float

<a id="freestyle.functions.GetProjectedXF1D"></a>

### class freestyle.functions.GetProjectedXF1D

Class hierarchy: [`freestyle.types.UnaryFunction1D`](freestyle.types.md#freestyle.types.UnaryFunction1D "freestyle.types.UnaryFunction1D") > [`freestyle.types.UnaryFunction1DDouble`](freestyle.types.md#freestyle.types.UnaryFunction1DDouble "freestyle.types.UnaryFunction1DDouble") > [`GetProjectedXF1D`](#freestyle.functions.GetProjectedXF1D "freestyle.functions.GetProjectedXF1D")

<a id="freestyle.functions.GetProjectedXF1D.__init__"></a>

#### freestyle.functions.GetProjectedXF1D.__init__(integration_type=IntegrationType.MEAN)

Builds a GetProjectedXF1D object.

**Parameters:**

**integration_type** ([`freestyle.types.IntegrationType`](freestyle.types.md#freestyle.types.IntegrationType "freestyle.types.IntegrationType")) – The integration method used to compute a single value
from a set of values.

<a id="freestyle.functions.GetProjectedXF1D.__call__"></a>

#### freestyle.functions.GetProjectedXF1D.__call__(inter)

Returns the projected X 3D coordinate of an Interface1D.

**Parameters:**

**inter** ([`freestyle.types.Interface1D`](freestyle.types.md#freestyle.types.Interface1D "freestyle.types.Interface1D")) – An Interface1D object.

**Returns:**

The projected X 3D coordinate of an Interface1D.

**Return type:**

float

<a id="freestyle.functions.GetProjectedYF0D"></a>

### class freestyle.functions.GetProjectedYF0D

Class hierarchy: [`freestyle.types.UnaryFunction0D`](freestyle.types.md#freestyle.types.UnaryFunction0D "freestyle.types.UnaryFunction0D") > [`freestyle.types.UnaryFunction0DDouble`](freestyle.types.md#freestyle.types.UnaryFunction0DDouble "freestyle.types.UnaryFunction0DDouble") > [`GetProjectedYF0D`](#freestyle.functions.GetProjectedYF0D "freestyle.functions.GetProjectedYF0D")

<a id="freestyle.functions.GetProjectedYF0D.__init__"></a>

#### freestyle.functions.GetProjectedYF0D.__init__()

Builds a GetProjectedYF0D object.

<a id="freestyle.functions.GetProjectedYF0D.__call__"></a>

#### freestyle.functions.GetProjectedYF0D.__call__(it)

Returns the Y 3D projected coordinate of the [`freestyle.types.Interface0D`](freestyle.types.md#freestyle.types.Interface0D "freestyle.types.Interface0D")
pointed by the Interface0DIterator.

**Parameters:**

**it** ([`freestyle.types.Interface0DIterator`](freestyle.types.md#freestyle.types.Interface0DIterator "freestyle.types.Interface0DIterator")) – An Interface0DIterator object.

**Returns:**

The Y 3D projected coordinate of the pointed Interface0D.

**Return type:**

float

<a id="freestyle.functions.GetProjectedYF1D"></a>

### class freestyle.functions.GetProjectedYF1D

Class hierarchy: [`freestyle.types.UnaryFunction1D`](freestyle.types.md#freestyle.types.UnaryFunction1D "freestyle.types.UnaryFunction1D") > [`freestyle.types.UnaryFunction1DDouble`](freestyle.types.md#freestyle.types.UnaryFunction1DDouble "freestyle.types.UnaryFunction1DDouble") > [`GetProjectedYF1D`](#freestyle.functions.GetProjectedYF1D "freestyle.functions.GetProjectedYF1D")

<a id="freestyle.functions.GetProjectedYF1D.__init__"></a>

#### freestyle.functions.GetProjectedYF1D.__init__(integration_type=IntegrationType.MEAN)

Builds a GetProjectedYF1D object.

**Parameters:**

**integration_type** ([`freestyle.types.IntegrationType`](freestyle.types.md#freestyle.types.IntegrationType "freestyle.types.IntegrationType")) – The integration method used to compute a single value
from a set of values.

<a id="freestyle.functions.GetProjectedYF1D.__call__"></a>

#### freestyle.functions.GetProjectedYF1D.__call__(inter)

Returns the projected Y 3D coordinate of an Interface1D.

**Parameters:**

**inter** ([`freestyle.types.Interface1D`](freestyle.types.md#freestyle.types.Interface1D "freestyle.types.Interface1D")) – An Interface1D object.

**Returns:**

The projected Y 3D coordinate of an Interface1D.

**Return type:**

float

<a id="freestyle.functions.GetProjectedZF0D"></a>

### class freestyle.functions.GetProjectedZF0D

Class hierarchy: [`freestyle.types.UnaryFunction0D`](freestyle.types.md#freestyle.types.UnaryFunction0D "freestyle.types.UnaryFunction0D") > [`freestyle.types.UnaryFunction0DDouble`](freestyle.types.md#freestyle.types.UnaryFunction0DDouble "freestyle.types.UnaryFunction0DDouble") > [`GetProjectedZF0D`](#freestyle.functions.GetProjectedZF0D "freestyle.functions.GetProjectedZF0D")

<a id="freestyle.functions.GetProjectedZF0D.__init__"></a>

#### freestyle.functions.GetProjectedZF0D.__init__()

Builds a GetProjectedZF0D object.

<a id="freestyle.functions.GetProjectedZF0D.__call__"></a>

#### freestyle.functions.GetProjectedZF0D.__call__(it)

Returns the Z 3D projected coordinate of the [`freestyle.types.Interface0D`](freestyle.types.md#freestyle.types.Interface0D "freestyle.types.Interface0D")
pointed by the Interface0DIterator.

**Parameters:**

**it** ([`freestyle.types.Interface0DIterator`](freestyle.types.md#freestyle.types.Interface0DIterator "freestyle.types.Interface0DIterator")) – An Interface0DIterator object.

**Returns:**

The Z 3D projected coordinate of the pointed Interface0D.

**Return type:**

float

<a id="freestyle.functions.GetProjectedZF1D"></a>

### class freestyle.functions.GetProjectedZF1D

Class hierarchy: [`freestyle.types.UnaryFunction1D`](freestyle.types.md#freestyle.types.UnaryFunction1D "freestyle.types.UnaryFunction1D") > [`freestyle.types.UnaryFunction1DDouble`](freestyle.types.md#freestyle.types.UnaryFunction1DDouble "freestyle.types.UnaryFunction1DDouble") > [`GetProjectedZF1D`](#freestyle.functions.GetProjectedZF1D "freestyle.functions.GetProjectedZF1D")

<a id="freestyle.functions.GetProjectedZF1D.__init__"></a>

#### freestyle.functions.GetProjectedZF1D.__init__(integration_type=IntegrationType.MEAN)

Builds a GetProjectedZF1D object.

**Parameters:**

**integration_type** ([`freestyle.types.IntegrationType`](freestyle.types.md#freestyle.types.IntegrationType "freestyle.types.IntegrationType")) – The integration method used to compute a single value
from a set of values.

<a id="freestyle.functions.GetProjectedZF1D.__call__"></a>

#### freestyle.functions.GetProjectedZF1D.__call__(inter)

Returns the projected Z 3D coordinate of an Interface1D.

**Parameters:**

**inter** ([`freestyle.types.Interface1D`](freestyle.types.md#freestyle.types.Interface1D "freestyle.types.Interface1D")) – An Interface1D object.

**Returns:**

The projected Z 3D coordinate of an Interface1D.

**Return type:**

float

<a id="freestyle.functions.GetShapeF0D"></a>

### class freestyle.functions.GetShapeF0D

Class hierarchy: [`freestyle.types.UnaryFunction0D`](freestyle.types.md#freestyle.types.UnaryFunction0D "freestyle.types.UnaryFunction0D") > [`freestyle.types.UnaryFunction0DViewShape`](freestyle.types.md#freestyle.types.UnaryFunction0DViewShape "freestyle.types.UnaryFunction0DViewShape") > [`GetShapeF0D`](#freestyle.functions.GetShapeF0D "freestyle.functions.GetShapeF0D")

<a id="freestyle.functions.GetShapeF0D.__init__"></a>

#### freestyle.functions.GetShapeF0D.__init__()

Builds a GetShapeF0D object.

<a id="freestyle.functions.GetShapeF0D.__call__"></a>

#### freestyle.functions.GetShapeF0D.__call__(it)

Returns the [`freestyle.types.ViewShape`](freestyle.types.md#freestyle.types.ViewShape "freestyle.types.ViewShape") containing the
Interface0D pointed by the Interface0DIterator.

**Parameters:**

**it** ([`freestyle.types.Interface0DIterator`](freestyle.types.md#freestyle.types.Interface0DIterator "freestyle.types.Interface0DIterator")) – An Interface0DIterator object.

**Returns:**

The ViewShape containing the pointed Interface0D.

**Return type:**

[`freestyle.types.ViewShape`](freestyle.types.md#freestyle.types.ViewShape "freestyle.types.ViewShape")

<a id="freestyle.functions.GetShapeF1D"></a>

### class freestyle.functions.GetShapeF1D

Class hierarchy: [`freestyle.types.UnaryFunction1D`](freestyle.types.md#freestyle.types.UnaryFunction1D "freestyle.types.UnaryFunction1D") > [`freestyle.types.UnaryFunction1DVectorViewShape`](freestyle.types.md#freestyle.types.UnaryFunction1DVectorViewShape "freestyle.types.UnaryFunction1DVectorViewShape") > [`GetShapeF1D`](#freestyle.functions.GetShapeF1D "freestyle.functions.GetShapeF1D")

<a id="freestyle.functions.GetShapeF1D.__init__"></a>

#### freestyle.functions.GetShapeF1D.__init__()

Builds a GetShapeF1D object.

<a id="freestyle.functions.GetShapeF1D.__call__"></a>

#### freestyle.functions.GetShapeF1D.__call__(inter)

Returns a list of shapes covered by this Interface1D.

**Parameters:**

**inter** ([`freestyle.types.Interface1D`](freestyle.types.md#freestyle.types.Interface1D "freestyle.types.Interface1D")) – An Interface1D object.

**Returns:**

A list of shapes covered by the Interface1D.

**Return type:**

list[[`freestyle.types.ViewShape`](freestyle.types.md#freestyle.types.ViewShape "freestyle.types.ViewShape")]

<a id="freestyle.functions.GetSteerableViewMapDensityF1D"></a>

### class freestyle.functions.GetSteerableViewMapDensityF1D

Class hierarchy: [`freestyle.types.UnaryFunction1D`](freestyle.types.md#freestyle.types.UnaryFunction1D "freestyle.types.UnaryFunction1D") > [`freestyle.types.UnaryFunction1DDouble`](freestyle.types.md#freestyle.types.UnaryFunction1DDouble "freestyle.types.UnaryFunction1DDouble") > [`GetSteerableViewMapDensityF1D`](#freestyle.functions.GetSteerableViewMapDensityF1D "freestyle.functions.GetSteerableViewMapDensityF1D")

<a id="freestyle.functions.GetSteerableViewMapDensityF1D.__init__"></a>

#### freestyle.functions.GetSteerableViewMapDensityF1D.__init__(level, integration_type=IntegrationType.MEAN, sampling=2.0)

Builds a GetSteerableViewMapDensityF1D object.

**Parameters:**

- **level** (int) – The level of the pyramid from which the pixel must be
  read.
- **integration_type** ([`freestyle.types.IntegrationType`](freestyle.types.md#freestyle.types.IntegrationType "freestyle.types.IntegrationType")) – The integration method used to compute a single value
  from a set of values.
- **sampling** (float) – The resolution used to sample the chain: the
  corresponding 0D function is evaluated at each sample point and
  the result is obtained by combining the resulting values into a
  single one, following the method specified by integration_type.

<a id="freestyle.functions.GetSteerableViewMapDensityF1D.__call__"></a>

#### freestyle.functions.GetSteerableViewMapDensityF1D.__call__(inter)

Returns the density of the ViewMap for a given Interface1D. The
density of each [`freestyle.types.FEdge`](freestyle.types.md#freestyle.types.FEdge "freestyle.types.FEdge") is evaluated in the
proper steerable [`freestyle.types.ViewMap`](freestyle.types.md#freestyle.types.ViewMap "freestyle.types.ViewMap") depending on its
orientation.

**Parameters:**

**inter** ([`freestyle.types.Interface1D`](freestyle.types.md#freestyle.types.Interface1D "freestyle.types.Interface1D")) – An Interface1D object.

**Returns:**

The density of the ViewMap for a given Interface1D.

**Return type:**

float

<a id="freestyle.functions.GetViewMapGradientNormF0D"></a>

### class freestyle.functions.GetViewMapGradientNormF0D

Class hierarchy: [`freestyle.types.UnaryFunction0D`](freestyle.types.md#freestyle.types.UnaryFunction0D "freestyle.types.UnaryFunction0D") > [`freestyle.types.UnaryFunction0DFloat`](freestyle.types.md#freestyle.types.UnaryFunction0DFloat "freestyle.types.UnaryFunction0DFloat") > [`GetViewMapGradientNormF0D`](#freestyle.functions.GetViewMapGradientNormF0D "freestyle.functions.GetViewMapGradientNormF0D")

<a id="freestyle.functions.GetViewMapGradientNormF0D.__init__"></a>

#### freestyle.functions.GetViewMapGradientNormF0D.__init__(level)

Builds a GetViewMapGradientNormF0D object.

**Parameters:**

**level** (int) – The level of the pyramid from which the pixel must be
read.

<a id="freestyle.functions.GetViewMapGradientNormF0D.__call__"></a>

#### freestyle.functions.GetViewMapGradientNormF0D.__call__(it)

Returns the norm of the gradient of the global viewmap density
image.

**Parameters:**

**it** ([`freestyle.types.Interface0DIterator`](freestyle.types.md#freestyle.types.Interface0DIterator "freestyle.types.Interface0DIterator")) – An Interface0DIterator object.

**Returns:**

The norm of the gradient of the global viewmap density
image.

**Return type:**

float

<a id="freestyle.functions.GetViewMapGradientNormF1D"></a>

### class freestyle.functions.GetViewMapGradientNormF1D

Class hierarchy: [`freestyle.types.UnaryFunction1D`](freestyle.types.md#freestyle.types.UnaryFunction1D "freestyle.types.UnaryFunction1D") > [`freestyle.types.UnaryFunction1DDouble`](freestyle.types.md#freestyle.types.UnaryFunction1DDouble "freestyle.types.UnaryFunction1DDouble") > [`GetViewMapGradientNormF1D`](#freestyle.functions.GetViewMapGradientNormF1D "freestyle.functions.GetViewMapGradientNormF1D")

<a id="freestyle.functions.GetViewMapGradientNormF1D.__init__"></a>

#### freestyle.functions.GetViewMapGradientNormF1D.__init__(level, integration_type=IntegrationType.MEAN, sampling=2.0)

Builds a GetViewMapGradientNormF1D object.

**Parameters:**

- **level** (int) – The level of the pyramid from which the pixel must be
  read.
- **integration_type** ([`freestyle.types.IntegrationType`](freestyle.types.md#freestyle.types.IntegrationType "freestyle.types.IntegrationType")) – The integration method used to compute a single value
  from a set of values.
- **sampling** (float) – The resolution used to sample the chain: the
  corresponding 0D function is evaluated at each sample point and
  the result is obtained by combining the resulting values into a
  single one, following the method specified by integration_type.

<a id="freestyle.functions.GetViewMapGradientNormF1D.__call__"></a>

#### freestyle.functions.GetViewMapGradientNormF1D.__call__(inter)

Returns the density of the ViewMap for a given Interface1D. The
density of each [`freestyle.types.FEdge`](freestyle.types.md#freestyle.types.FEdge "freestyle.types.FEdge") is evaluated in the
proper steerable [`freestyle.types.ViewMap`](freestyle.types.md#freestyle.types.ViewMap "freestyle.types.ViewMap") depending on its
orientation.

**Parameters:**

**inter** ([`freestyle.types.Interface1D`](freestyle.types.md#freestyle.types.Interface1D "freestyle.types.Interface1D")) – An Interface1D object.

**Returns:**

The density of the ViewMap for a given Interface1D.

**Return type:**

float

<a id="freestyle.functions.GetXF0D"></a>

### class freestyle.functions.GetXF0D

Class hierarchy: [`freestyle.types.UnaryFunction0D`](freestyle.types.md#freestyle.types.UnaryFunction0D "freestyle.types.UnaryFunction0D") > [`freestyle.types.UnaryFunction0DDouble`](freestyle.types.md#freestyle.types.UnaryFunction0DDouble "freestyle.types.UnaryFunction0DDouble") > [`GetXF0D`](#freestyle.functions.GetXF0D "freestyle.functions.GetXF0D")

<a id="freestyle.functions.GetXF0D.__init__"></a>

#### freestyle.functions.GetXF0D.__init__()

Builds a GetXF0D object.

<a id="freestyle.functions.GetXF0D.__call__"></a>

#### freestyle.functions.GetXF0D.__call__(it)

Returns the X 3D coordinate of the [`freestyle.types.Interface0D`](freestyle.types.md#freestyle.types.Interface0D "freestyle.types.Interface0D") pointed by
the Interface0DIterator.

**Parameters:**

**it** ([`freestyle.types.Interface0DIterator`](freestyle.types.md#freestyle.types.Interface0DIterator "freestyle.types.Interface0DIterator")) – An Interface0DIterator object.

**Returns:**

The X 3D coordinate of the pointed Interface0D.

**Return type:**

float

<a id="freestyle.functions.GetXF1D"></a>

### class freestyle.functions.GetXF1D

Class hierarchy: [`freestyle.types.UnaryFunction1D`](freestyle.types.md#freestyle.types.UnaryFunction1D "freestyle.types.UnaryFunction1D") > [`freestyle.types.UnaryFunction1DDouble`](freestyle.types.md#freestyle.types.UnaryFunction1DDouble "freestyle.types.UnaryFunction1DDouble") > [`GetXF1D`](#freestyle.functions.GetXF1D "freestyle.functions.GetXF1D")

<a id="freestyle.functions.GetXF1D.__init__"></a>

#### freestyle.functions.GetXF1D.__init__(integration_type=IntegrationType.MEAN)

Builds a GetXF1D object.

**Parameters:**

**integration_type** ([`freestyle.types.IntegrationType`](freestyle.types.md#freestyle.types.IntegrationType "freestyle.types.IntegrationType")) – The integration method used to compute a single value
from a set of values.

<a id="freestyle.functions.GetXF1D.__call__"></a>

#### freestyle.functions.GetXF1D.__call__(inter)

Returns the X 3D coordinate of an Interface1D.

**Parameters:**

**inter** ([`freestyle.types.Interface1D`](freestyle.types.md#freestyle.types.Interface1D "freestyle.types.Interface1D")) – An Interface1D object.

**Returns:**

The X 3D coordinate of the Interface1D.

**Return type:**

float

<a id="freestyle.functions.GetYF0D"></a>

### class freestyle.functions.GetYF0D

Class hierarchy: [`freestyle.types.UnaryFunction0D`](freestyle.types.md#freestyle.types.UnaryFunction0D "freestyle.types.UnaryFunction0D") > [`freestyle.types.UnaryFunction0DDouble`](freestyle.types.md#freestyle.types.UnaryFunction0DDouble "freestyle.types.UnaryFunction0DDouble") > [`GetYF0D`](#freestyle.functions.GetYF0D "freestyle.functions.GetYF0D")

<a id="freestyle.functions.GetYF0D.__init__"></a>

#### freestyle.functions.GetYF0D.__init__()

Builds a GetYF0D object.

<a id="freestyle.functions.GetYF0D.__call__"></a>

#### freestyle.functions.GetYF0D.__call__(it)

Returns the Y 3D coordinate of the [`freestyle.types.Interface0D`](freestyle.types.md#freestyle.types.Interface0D "freestyle.types.Interface0D") pointed by
the Interface0DIterator.

**Parameters:**

**it** ([`freestyle.types.Interface0DIterator`](freestyle.types.md#freestyle.types.Interface0DIterator "freestyle.types.Interface0DIterator")) – An Interface0DIterator object.

**Returns:**

The Y 3D coordinate of the pointed Interface0D.

**Return type:**

float

<a id="freestyle.functions.GetYF1D"></a>

### class freestyle.functions.GetYF1D

Class hierarchy: [`freestyle.types.UnaryFunction1D`](freestyle.types.md#freestyle.types.UnaryFunction1D "freestyle.types.UnaryFunction1D") > [`freestyle.types.UnaryFunction1DDouble`](freestyle.types.md#freestyle.types.UnaryFunction1DDouble "freestyle.types.UnaryFunction1DDouble") > [`GetYF1D`](#freestyle.functions.GetYF1D "freestyle.functions.GetYF1D")

<a id="freestyle.functions.GetYF1D.__init__"></a>

#### freestyle.functions.GetYF1D.__init__(integration_type=IntegrationType.MEAN)

Builds a GetYF1D object.

**Parameters:**

**integration_type** ([`freestyle.types.IntegrationType`](freestyle.types.md#freestyle.types.IntegrationType "freestyle.types.IntegrationType")) – The integration method used to compute a single value
from a set of values.

<a id="freestyle.functions.GetYF1D.__call__"></a>

#### freestyle.functions.GetYF1D.__call__(inter)

Returns the Y 3D coordinate of an Interface1D.

**Parameters:**

**inter** ([`freestyle.types.Interface1D`](freestyle.types.md#freestyle.types.Interface1D "freestyle.types.Interface1D")) – An Interface1D object.

**Returns:**

The Y 3D coordinate of the Interface1D.

**Return type:**

float

<a id="freestyle.functions.GetZF0D"></a>

### class freestyle.functions.GetZF0D

Class hierarchy: [`freestyle.types.UnaryFunction0D`](freestyle.types.md#freestyle.types.UnaryFunction0D "freestyle.types.UnaryFunction0D") > [`freestyle.types.UnaryFunction0DDouble`](freestyle.types.md#freestyle.types.UnaryFunction0DDouble "freestyle.types.UnaryFunction0DDouble") > [`GetZF0D`](#freestyle.functions.GetZF0D "freestyle.functions.GetZF0D")

<a id="freestyle.functions.GetZF0D.__init__"></a>

#### freestyle.functions.GetZF0D.__init__()

Builds a GetZF0D object.

<a id="freestyle.functions.GetZF0D.__call__"></a>

#### freestyle.functions.GetZF0D.__call__(it)

Returns the Z 3D coordinate of the [`freestyle.types.Interface0D`](freestyle.types.md#freestyle.types.Interface0D "freestyle.types.Interface0D") pointed by
the Interface0DIterator.

**Parameters:**

**it** ([`freestyle.types.Interface0DIterator`](freestyle.types.md#freestyle.types.Interface0DIterator "freestyle.types.Interface0DIterator")) – An Interface0DIterator object.

**Returns:**

The Z 3D coordinate of the pointed Interface0D.

**Return type:**

float

<a id="freestyle.functions.GetZF1D"></a>

### class freestyle.functions.GetZF1D

Class hierarchy: [`freestyle.types.UnaryFunction1D`](freestyle.types.md#freestyle.types.UnaryFunction1D "freestyle.types.UnaryFunction1D") > [`freestyle.types.UnaryFunction1DDouble`](freestyle.types.md#freestyle.types.UnaryFunction1DDouble "freestyle.types.UnaryFunction1DDouble") > [`GetZF1D`](#freestyle.functions.GetZF1D "freestyle.functions.GetZF1D")

<a id="freestyle.functions.GetZF1D.__init__"></a>

#### freestyle.functions.GetZF1D.__init__(integration_type=IntegrationType.MEAN)

Builds a GetZF1D object.

**Parameters:**

**integration_type** ([`freestyle.types.IntegrationType`](freestyle.types.md#freestyle.types.IntegrationType "freestyle.types.IntegrationType")) – The integration method used to compute a single value
from a set of values.

<a id="freestyle.functions.GetZF1D.__call__"></a>

#### freestyle.functions.GetZF1D.__call__(inter)

Returns the Z 3D coordinate of an Interface1D.

**Parameters:**

**inter** ([`freestyle.types.Interface1D`](freestyle.types.md#freestyle.types.Interface1D "freestyle.types.Interface1D")) – An Interface1D object.

**Returns:**

The Z 3D coordinate of the Interface1D.

**Return type:**

float

<a id="freestyle.functions.IncrementChainingTimeStampF1D"></a>

### class freestyle.functions.IncrementChainingTimeStampF1D

Class hierarchy: [`freestyle.types.UnaryFunction1D`](freestyle.types.md#freestyle.types.UnaryFunction1D "freestyle.types.UnaryFunction1D") > [`freestyle.types.UnaryFunction1DVoid`](freestyle.types.md#freestyle.types.UnaryFunction1DVoid "freestyle.types.UnaryFunction1DVoid") > [`IncrementChainingTimeStampF1D`](#freestyle.functions.IncrementChainingTimeStampF1D "freestyle.functions.IncrementChainingTimeStampF1D")

<a id="freestyle.functions.IncrementChainingTimeStampF1D.__init__"></a>

#### freestyle.functions.IncrementChainingTimeStampF1D.__init__()

Builds an IncrementChainingTimeStampF1D object.

<a id="freestyle.functions.IncrementChainingTimeStampF1D.__call__"></a>

#### freestyle.functions.IncrementChainingTimeStampF1D.__call__(inter)

Increments the chaining time stamp of the Interface1D.

**Parameters:**

**inter** ([`freestyle.types.Interface1D`](freestyle.types.md#freestyle.types.Interface1D "freestyle.types.Interface1D")) – An Interface1D object.

<a id="freestyle.functions.LocalAverageDepthF0D"></a>

### class freestyle.functions.LocalAverageDepthF0D

Class hierarchy: [`freestyle.types.UnaryFunction0D`](freestyle.types.md#freestyle.types.UnaryFunction0D "freestyle.types.UnaryFunction0D") > [`freestyle.types.UnaryFunction0DDouble`](freestyle.types.md#freestyle.types.UnaryFunction0DDouble "freestyle.types.UnaryFunction0DDouble") > [`LocalAverageDepthF0D`](#freestyle.functions.LocalAverageDepthF0D "freestyle.functions.LocalAverageDepthF0D")

<a id="freestyle.functions.LocalAverageDepthF0D.__init__"></a>

#### freestyle.functions.LocalAverageDepthF0D.__init__(mask_size=5.0)

Builds a LocalAverageDepthF0D object.

**Parameters:**

**mask_size** (float) – The size of the mask.

<a id="freestyle.functions.LocalAverageDepthF0D.__call__"></a>

#### freestyle.functions.LocalAverageDepthF0D.__call__(it)

Returns the average depth around the
[`freestyle.types.Interface0D`](freestyle.types.md#freestyle.types.Interface0D "freestyle.types.Interface0D") pointed by the
Interface0DIterator. The result is obtained by querying the depth
buffer on a window around that point.

**Parameters:**

**it** ([`freestyle.types.Interface0DIterator`](freestyle.types.md#freestyle.types.Interface0DIterator "freestyle.types.Interface0DIterator")) – An Interface0DIterator object.

**Returns:**

The average depth around the pointed Interface0D.

**Return type:**

float

<a id="freestyle.functions.LocalAverageDepthF1D"></a>

### class freestyle.functions.LocalAverageDepthF1D

Class hierarchy: [`freestyle.types.UnaryFunction1D`](freestyle.types.md#freestyle.types.UnaryFunction1D "freestyle.types.UnaryFunction1D") > [`freestyle.types.UnaryFunction1DDouble`](freestyle.types.md#freestyle.types.UnaryFunction1DDouble "freestyle.types.UnaryFunction1DDouble") > [`LocalAverageDepthF1D`](#freestyle.functions.LocalAverageDepthF1D "freestyle.functions.LocalAverageDepthF1D")

<a id="freestyle.functions.LocalAverageDepthF1D.__init__"></a>

#### freestyle.functions.LocalAverageDepthF1D.__init__(sigma, integration_type=IntegrationType.MEAN)

Builds a LocalAverageDepthF1D object.

**Parameters:**

- **sigma** (float) – The sigma used in DensityF0D and determining the window
  size used in each density query.
- **integration_type** ([`freestyle.types.IntegrationType`](freestyle.types.md#freestyle.types.IntegrationType "freestyle.types.IntegrationType")) – The integration method used to compute a single value
  from a set of values.

<a id="freestyle.functions.LocalAverageDepthF1D.__call__"></a>

#### freestyle.functions.LocalAverageDepthF1D.__call__(inter)

Returns the average depth evaluated for an Interface1D. The average
depth is evaluated for a set of points along the Interface1D (using
the [`freestyle.functions.LocalAverageDepthF0D`](#freestyle.functions.LocalAverageDepthF0D "freestyle.functions.LocalAverageDepthF0D") functor) with a
user-defined sampling and then integrated into a single value using a
user-defined integration method.

**Parameters:**

**inter** ([`freestyle.types.Interface1D`](freestyle.types.md#freestyle.types.Interface1D "freestyle.types.Interface1D")) – An Interface1D object.

**Returns:**

The average depth evaluated for the Interface1D.

**Return type:**

float

<a id="freestyle.functions.MaterialF0D"></a>

### class freestyle.functions.MaterialF0D

Class hierarchy: [`freestyle.types.UnaryFunction0D`](freestyle.types.md#freestyle.types.UnaryFunction0D "freestyle.types.UnaryFunction0D") > [`freestyle.types.UnaryFunction0DMaterial`](freestyle.types.md#freestyle.types.UnaryFunction0DMaterial "freestyle.types.UnaryFunction0DMaterial") > [`MaterialF0D`](#freestyle.functions.MaterialF0D "freestyle.functions.MaterialF0D")

<a id="freestyle.functions.MaterialF0D.__init__"></a>

#### freestyle.functions.MaterialF0D.__init__()

Builds a MaterialF0D object.

<a id="freestyle.functions.MaterialF0D.__call__"></a>

#### freestyle.functions.MaterialF0D.__call__(it)

Returns the material of the object evaluated at the
[`freestyle.types.Interface0D`](freestyle.types.md#freestyle.types.Interface0D "freestyle.types.Interface0D") pointed by the
Interface0DIterator. This evaluation can be ambiguous (in the case of
a [`freestyle.types.TVertex`](freestyle.types.md#freestyle.types.TVertex "freestyle.types.TVertex") for example. This functor tries to
remove this ambiguity using the context offered by the 1D element to
which the Interface0DIterator belongs to and by arbitrary choosing the
material of the face that lies on its left when following the 1D
element if there are two different materials on each side of the
point. However, there still can be problematic cases, and the user
willing to deal with this cases in a specific way should implement its
own getMaterial functor.

**Parameters:**

**it** ([`freestyle.types.Interface0DIterator`](freestyle.types.md#freestyle.types.Interface0DIterator "freestyle.types.Interface0DIterator")) – An Interface0DIterator object.

**Returns:**

The material of the object evaluated at the pointed
Interface0D.

**Return type:**

[`freestyle.types.Material`](freestyle.types.md#freestyle.types.Material "freestyle.types.Material")

<a id="freestyle.functions.Normal2DF0D"></a>

### class freestyle.functions.Normal2DF0D

Class hierarchy: [`freestyle.types.UnaryFunction0D`](freestyle.types.md#freestyle.types.UnaryFunction0D "freestyle.types.UnaryFunction0D") > [`freestyle.types.UnaryFunction0DVec2f`](freestyle.types.md#freestyle.types.UnaryFunction0DVec2f "freestyle.types.UnaryFunction0DVec2f") > [`Normal2DF0D`](#freestyle.functions.Normal2DF0D "freestyle.functions.Normal2DF0D")

<a id="freestyle.functions.Normal2DF0D.__init__"></a>

#### freestyle.functions.Normal2DF0D.__init__()

Builds a Normal2DF0D object.

<a id="freestyle.functions.Normal2DF0D.__call__"></a>

#### freestyle.functions.Normal2DF0D.__call__(it)

Returns a two-dimensional vector giving the normalized 2D normal to
the 1D element to which the [`freestyle.types.Interface0D`](freestyle.types.md#freestyle.types.Interface0D "freestyle.types.Interface0D")
pointed by the Interface0DIterator belongs. The normal is evaluated
at the pointed Interface0D.

**Parameters:**

**it** ([`freestyle.types.Interface0DIterator`](freestyle.types.md#freestyle.types.Interface0DIterator "freestyle.types.Interface0DIterator")) – An Interface0DIterator object.

**Returns:**

The 2D normal of the 1D element evaluated at the pointed
Interface0D.

**Return type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="freestyle.functions.Normal2DF1D"></a>

### class freestyle.functions.Normal2DF1D

Class hierarchy: [`freestyle.types.UnaryFunction1D`](freestyle.types.md#freestyle.types.UnaryFunction1D "freestyle.types.UnaryFunction1D") > [`freestyle.types.UnaryFunction1DVec2f`](freestyle.types.md#freestyle.types.UnaryFunction1DVec2f "freestyle.types.UnaryFunction1DVec2f") > [`Normal2DF1D`](#freestyle.functions.Normal2DF1D "freestyle.functions.Normal2DF1D")

<a id="freestyle.functions.Normal2DF1D.__init__"></a>

#### freestyle.functions.Normal2DF1D.__init__(integration_type=IntegrationType.MEAN)

Builds a Normal2DF1D object.

**Parameters:**

**integration_type** ([`freestyle.types.IntegrationType`](freestyle.types.md#freestyle.types.IntegrationType "freestyle.types.IntegrationType")) – The integration method used to compute a single value
from a set of values.

<a id="freestyle.functions.Normal2DF1D.__call__"></a>

#### freestyle.functions.Normal2DF1D.__call__(inter)

Returns the 2D normal for the Interface1D.

**Parameters:**

**inter** ([`freestyle.types.Interface1D`](freestyle.types.md#freestyle.types.Interface1D "freestyle.types.Interface1D")) – An Interface1D object.

**Returns:**

The 2D normal for the Interface1D.

**Return type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="freestyle.functions.Orientation2DF1D"></a>

### class freestyle.functions.Orientation2DF1D

Class hierarchy: [`freestyle.types.UnaryFunction1D`](freestyle.types.md#freestyle.types.UnaryFunction1D "freestyle.types.UnaryFunction1D") > [`freestyle.types.UnaryFunction1DVec2f`](freestyle.types.md#freestyle.types.UnaryFunction1DVec2f "freestyle.types.UnaryFunction1DVec2f") > [`Orientation2DF1D`](#freestyle.functions.Orientation2DF1D "freestyle.functions.Orientation2DF1D")

<a id="freestyle.functions.Orientation2DF1D.__init__"></a>

#### freestyle.functions.Orientation2DF1D.__init__(integration_type=IntegrationType.MEAN)

Builds an Orientation2DF1D object.

**Parameters:**

**integration_type** ([`freestyle.types.IntegrationType`](freestyle.types.md#freestyle.types.IntegrationType "freestyle.types.IntegrationType")) – The integration method used to compute a single value
from a set of values.

<a id="freestyle.functions.Orientation2DF1D.__call__"></a>

#### freestyle.functions.Orientation2DF1D.__call__(inter)

Returns the 2D orientation of the Interface1D.

**Parameters:**

**inter** ([`freestyle.types.Interface1D`](freestyle.types.md#freestyle.types.Interface1D "freestyle.types.Interface1D")) – An Interface1D object.

**Returns:**

The 2D orientation of the Interface1D.

**Return type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="freestyle.functions.Orientation3DF1D"></a>

### class freestyle.functions.Orientation3DF1D

Class hierarchy: [`freestyle.types.UnaryFunction1D`](freestyle.types.md#freestyle.types.UnaryFunction1D "freestyle.types.UnaryFunction1D") > [`freestyle.types.UnaryFunction1DVec3f`](freestyle.types.md#freestyle.types.UnaryFunction1DVec3f "freestyle.types.UnaryFunction1DVec3f") > [`Orientation3DF1D`](#freestyle.functions.Orientation3DF1D "freestyle.functions.Orientation3DF1D")

<a id="freestyle.functions.Orientation3DF1D.__init__"></a>

#### freestyle.functions.Orientation3DF1D.__init__(integration_type=IntegrationType.MEAN)

Builds an Orientation3DF1D object.

**Parameters:**

**integration_type** ([`freestyle.types.IntegrationType`](freestyle.types.md#freestyle.types.IntegrationType "freestyle.types.IntegrationType")) – The integration method used to compute a single value
from a set of values.

<a id="freestyle.functions.Orientation3DF1D.__call__"></a>

#### freestyle.functions.Orientation3DF1D.__call__(inter)

Returns the 3D orientation of the Interface1D.

**Parameters:**

**inter** ([`freestyle.types.Interface1D`](freestyle.types.md#freestyle.types.Interface1D "freestyle.types.Interface1D")) – An Interface1D object.

**Returns:**

The 3D orientation of the Interface1D.

**Return type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="freestyle.functions.QuantitativeInvisibilityF0D"></a>

### class freestyle.functions.QuantitativeInvisibilityF0D

Class hierarchy: [`freestyle.types.UnaryFunction0D`](freestyle.types.md#freestyle.types.UnaryFunction0D "freestyle.types.UnaryFunction0D") > [`freestyle.types.UnaryFunction0DUnsigned`](freestyle.types.md#freestyle.types.UnaryFunction0DUnsigned "freestyle.types.UnaryFunction0DUnsigned") > [`QuantitativeInvisibilityF0D`](#freestyle.functions.QuantitativeInvisibilityF0D "freestyle.functions.QuantitativeInvisibilityF0D")

<a id="freestyle.functions.QuantitativeInvisibilityF0D.__init__"></a>

#### freestyle.functions.QuantitativeInvisibilityF0D.__init__()

Builds a QuantitativeInvisibilityF0D object.

<a id="freestyle.functions.QuantitativeInvisibilityF0D.__call__"></a>

#### freestyle.functions.QuantitativeInvisibilityF0D.__call__(it)

Returns the quantitative invisibility of the
[`freestyle.types.Interface0D`](freestyle.types.md#freestyle.types.Interface0D "freestyle.types.Interface0D") pointed by the
Interface0DIterator. This evaluation can be ambiguous (in the case of
a [`freestyle.types.TVertex`](freestyle.types.md#freestyle.types.TVertex "freestyle.types.TVertex") for example). This functor tries
to remove this ambiguity using the context offered by the 1D element
to which the Interface0D belongs to. However, there still can be
problematic cases, and the user willing to deal with this cases in a
specific way should implement its own getQIF0D functor.

**Parameters:**

**it** ([`freestyle.types.Interface0DIterator`](freestyle.types.md#freestyle.types.Interface0DIterator "freestyle.types.Interface0DIterator")) – An Interface0DIterator object.

**Returns:**

The quantitative invisibility of the pointed Interface0D.

**Return type:**

int

<a id="freestyle.functions.QuantitativeInvisibilityF1D"></a>

### class freestyle.functions.QuantitativeInvisibilityF1D

Class hierarchy: [`freestyle.types.UnaryFunction1D`](freestyle.types.md#freestyle.types.UnaryFunction1D "freestyle.types.UnaryFunction1D") > [`freestyle.types.UnaryFunction1DUnsigned`](freestyle.types.md#freestyle.types.UnaryFunction1DUnsigned "freestyle.types.UnaryFunction1DUnsigned") > [`QuantitativeInvisibilityF1D`](#freestyle.functions.QuantitativeInvisibilityF1D "freestyle.functions.QuantitativeInvisibilityF1D")

<a id="freestyle.functions.QuantitativeInvisibilityF1D.__init__"></a>

#### freestyle.functions.QuantitativeInvisibilityF1D.__init__(integration_type=IntegrationType.MEAN)

Builds a QuantitativeInvisibilityF1D object.

**Parameters:**

**integration_type** ([`freestyle.types.IntegrationType`](freestyle.types.md#freestyle.types.IntegrationType "freestyle.types.IntegrationType")) – The integration method used to compute a single value
from a set of values.

<a id="freestyle.functions.QuantitativeInvisibilityF1D.__call__"></a>

#### freestyle.functions.QuantitativeInvisibilityF1D.__call__(inter)

Returns the Quantitative Invisibility of an Interface1D element. If
the Interface1D is a [`freestyle.types.ViewEdge`](freestyle.types.md#freestyle.types.ViewEdge "freestyle.types.ViewEdge"), then there is
no ambiguity concerning the result. But, if the Interface1D results
of a chaining (chain, stroke), then it might be made of several 1D
elements of different Quantitative Invisibilities.

**Parameters:**

**inter** ([`freestyle.types.Interface1D`](freestyle.types.md#freestyle.types.Interface1D "freestyle.types.Interface1D")) – An Interface1D object.

**Returns:**

The Quantitative Invisibility of the Interface1D.

**Return type:**

int

<a id="freestyle.functions.ReadCompleteViewMapPixelF0D"></a>

### class freestyle.functions.ReadCompleteViewMapPixelF0D

Class hierarchy: [`freestyle.types.UnaryFunction0D`](freestyle.types.md#freestyle.types.UnaryFunction0D "freestyle.types.UnaryFunction0D") > [`freestyle.types.UnaryFunction0DFloat`](freestyle.types.md#freestyle.types.UnaryFunction0DFloat "freestyle.types.UnaryFunction0DFloat") > [`ReadCompleteViewMapPixelF0D`](#freestyle.functions.ReadCompleteViewMapPixelF0D "freestyle.functions.ReadCompleteViewMapPixelF0D")

<a id="freestyle.functions.ReadCompleteViewMapPixelF0D.__init__"></a>

#### freestyle.functions.ReadCompleteViewMapPixelF0D.__init__(level)

Builds a ReadCompleteViewMapPixelF0D object.

**Parameters:**

**level** (int) – The level of the pyramid from which the pixel must be
read.

<a id="freestyle.functions.ReadCompleteViewMapPixelF0D.__call__"></a>

#### freestyle.functions.ReadCompleteViewMapPixelF0D.__call__(it)

Reads a pixel in one of the level of the complete viewmap.

**Parameters:**

**it** ([`freestyle.types.Interface0DIterator`](freestyle.types.md#freestyle.types.Interface0DIterator "freestyle.types.Interface0DIterator")) – An Interface0DIterator object.

**Returns:**

A pixel in one of the level of the complete viewmap.

**Return type:**

float

<a id="freestyle.functions.ReadMapPixelF0D"></a>

### class freestyle.functions.ReadMapPixelF0D

Class hierarchy: [`freestyle.types.UnaryFunction0D`](freestyle.types.md#freestyle.types.UnaryFunction0D "freestyle.types.UnaryFunction0D") > [`freestyle.types.UnaryFunction0DFloat`](freestyle.types.md#freestyle.types.UnaryFunction0DFloat "freestyle.types.UnaryFunction0DFloat") > [`ReadMapPixelF0D`](#freestyle.functions.ReadMapPixelF0D "freestyle.functions.ReadMapPixelF0D")

<a id="freestyle.functions.ReadMapPixelF0D.__init__"></a>

#### freestyle.functions.ReadMapPixelF0D.__init__(map_name, level)

Builds a ReadMapPixelF0D object.

**Parameters:**

- **map_name** (str) – The name of the map to be read.
- **level** (int) – The level of the pyramid from which the pixel must be
  read.

<a id="freestyle.functions.ReadMapPixelF0D.__call__"></a>

#### freestyle.functions.ReadMapPixelF0D.__call__(it)

Reads a pixel in a map.

**Parameters:**

**it** ([`freestyle.types.Interface0DIterator`](freestyle.types.md#freestyle.types.Interface0DIterator "freestyle.types.Interface0DIterator")) – An Interface0DIterator object.

**Returns:**

A pixel in a map.

**Return type:**

float

<a id="freestyle.functions.ReadSteerableViewMapPixelF0D"></a>

### class freestyle.functions.ReadSteerableViewMapPixelF0D

Class hierarchy: [`freestyle.types.UnaryFunction0D`](freestyle.types.md#freestyle.types.UnaryFunction0D "freestyle.types.UnaryFunction0D") > [`freestyle.types.UnaryFunction0DFloat`](freestyle.types.md#freestyle.types.UnaryFunction0DFloat "freestyle.types.UnaryFunction0DFloat") > [`ReadSteerableViewMapPixelF0D`](#freestyle.functions.ReadSteerableViewMapPixelF0D "freestyle.functions.ReadSteerableViewMapPixelF0D")

<a id="freestyle.functions.ReadSteerableViewMapPixelF0D.__init__"></a>

#### freestyle.functions.ReadSteerableViewMapPixelF0D.__init__(orientation, level)

Builds a ReadSteerableViewMapPixelF0D object.

**Parameters:**

- **orientation** (int) – The integer belonging to [0, 4] indicating the
  orientation (E, NE, N, NW) we are interested in.
- **level** (int) – The level of the pyramid from which the pixel must be
  read.

<a id="freestyle.functions.ReadSteerableViewMapPixelF0D.__call__"></a>

#### freestyle.functions.ReadSteerableViewMapPixelF0D.__call__(it)

Reads a pixel in one of the level of one of the steerable viewmaps.

**Parameters:**

**it** ([`freestyle.types.Interface0DIterator`](freestyle.types.md#freestyle.types.Interface0DIterator "freestyle.types.Interface0DIterator")) – An Interface0DIterator object.

**Returns:**

A pixel in one of the level of one of the steerable viewmaps.

**Return type:**

float

<a id="freestyle.functions.ShapeIdF0D"></a>

### class freestyle.functions.ShapeIdF0D

Class hierarchy: [`freestyle.types.UnaryFunction0D`](freestyle.types.md#freestyle.types.UnaryFunction0D "freestyle.types.UnaryFunction0D") > [`freestyle.types.UnaryFunction0DId`](freestyle.types.md#freestyle.types.UnaryFunction0DId "freestyle.types.UnaryFunction0DId") > [`ShapeIdF0D`](#freestyle.functions.ShapeIdF0D "freestyle.functions.ShapeIdF0D")

<a id="freestyle.functions.ShapeIdF0D.__init__"></a>

#### freestyle.functions.ShapeIdF0D.__init__()

Builds a ShapeIdF0D object.

<a id="freestyle.functions.ShapeIdF0D.__call__"></a>

#### freestyle.functions.ShapeIdF0D.__call__(it)

Returns the [`freestyle.types.Id`](freestyle.types.md#freestyle.types.Id "freestyle.types.Id") of the Shape the
[`freestyle.types.Interface0D`](freestyle.types.md#freestyle.types.Interface0D "freestyle.types.Interface0D") pointed by the
Interface0DIterator belongs to. This evaluation can be ambiguous (in
the case of a [`freestyle.types.TVertex`](freestyle.types.md#freestyle.types.TVertex "freestyle.types.TVertex") for example). This
functor tries to remove this ambiguity using the context offered by
the 1D element to which the Interface0DIterator belongs to. However,
there still can be problematic cases, and the user willing to deal
with this cases in a specific way should implement its own
getShapeIdF0D functor.

**Parameters:**

**it** ([`freestyle.types.Interface0DIterator`](freestyle.types.md#freestyle.types.Interface0DIterator "freestyle.types.Interface0DIterator")) – An Interface0DIterator object.

**Returns:**

The Id of the Shape the pointed Interface0D belongs to.

**Return type:**

[`freestyle.types.Id`](freestyle.types.md#freestyle.types.Id "freestyle.types.Id")

<a id="freestyle.functions.TimeStampF1D"></a>

### class freestyle.functions.TimeStampF1D

Class hierarchy: [`freestyle.types.UnaryFunction1D`](freestyle.types.md#freestyle.types.UnaryFunction1D "freestyle.types.UnaryFunction1D") > [`freestyle.types.UnaryFunction1DVoid`](freestyle.types.md#freestyle.types.UnaryFunction1DVoid "freestyle.types.UnaryFunction1DVoid") > [`TimeStampF1D`](#freestyle.functions.TimeStampF1D "freestyle.functions.TimeStampF1D")

<a id="freestyle.functions.TimeStampF1D.__init__"></a>

#### freestyle.functions.TimeStampF1D.__init__()

Builds a TimeStampF1D object.

<a id="freestyle.functions.TimeStampF1D.__call__"></a>

#### freestyle.functions.TimeStampF1D.__call__(inter)

Returns the time stamp of the Interface1D.

**Parameters:**

**inter** ([`freestyle.types.Interface1D`](freestyle.types.md#freestyle.types.Interface1D "freestyle.types.Interface1D")) – An Interface1D object.

<a id="freestyle.functions.VertexOrientation2DF0D"></a>

### class freestyle.functions.VertexOrientation2DF0D

Class hierarchy: [`freestyle.types.UnaryFunction0D`](freestyle.types.md#freestyle.types.UnaryFunction0D "freestyle.types.UnaryFunction0D") > [`freestyle.types.UnaryFunction0DVec2f`](freestyle.types.md#freestyle.types.UnaryFunction0DVec2f "freestyle.types.UnaryFunction0DVec2f") > [`VertexOrientation2DF0D`](#freestyle.functions.VertexOrientation2DF0D "freestyle.functions.VertexOrientation2DF0D")

<a id="freestyle.functions.VertexOrientation2DF0D.__init__"></a>

#### freestyle.functions.VertexOrientation2DF0D.__init__()

Builds a VertexOrientation2DF0D object.

<a id="freestyle.functions.VertexOrientation2DF0D.__call__"></a>

#### freestyle.functions.VertexOrientation2DF0D.__call__(it)

Returns a two-dimensional vector giving the 2D oriented tangent to the
1D element to which the [`freestyle.types.Interface0D`](freestyle.types.md#freestyle.types.Interface0D "freestyle.types.Interface0D") pointed
by the Interface0DIterator belongs. The 2D oriented tangent is
evaluated at the pointed Interface0D.

**Parameters:**

**it** ([`freestyle.types.Interface0DIterator`](freestyle.types.md#freestyle.types.Interface0DIterator "freestyle.types.Interface0DIterator")) – An Interface0DIterator object.

**Returns:**

The 2D oriented tangent to the 1D element evaluated at the
pointed Interface0D.

**Return type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="freestyle.functions.VertexOrientation3DF0D"></a>

### class freestyle.functions.VertexOrientation3DF0D

Class hierarchy: [`freestyle.types.UnaryFunction0D`](freestyle.types.md#freestyle.types.UnaryFunction0D "freestyle.types.UnaryFunction0D") > [`freestyle.types.UnaryFunction0DVec3f`](freestyle.types.md#freestyle.types.UnaryFunction0DVec3f "freestyle.types.UnaryFunction0DVec3f") > [`VertexOrientation3DF0D`](#freestyle.functions.VertexOrientation3DF0D "freestyle.functions.VertexOrientation3DF0D")

<a id="freestyle.functions.VertexOrientation3DF0D.__init__"></a>

#### freestyle.functions.VertexOrientation3DF0D.__init__()

Builds a VertexOrientation3DF0D object.

<a id="freestyle.functions.VertexOrientation3DF0D.__call__"></a>

#### freestyle.functions.VertexOrientation3DF0D.__call__(it)

Returns a three-dimensional vector giving the 3D oriented tangent to
the 1D element to which the [`freestyle.types.Interface0D`](freestyle.types.md#freestyle.types.Interface0D "freestyle.types.Interface0D")
pointed by the Interface0DIterator belongs. The 3D oriented tangent
is evaluated at the pointed Interface0D.

**Parameters:**

**it** ([`freestyle.types.Interface0DIterator`](freestyle.types.md#freestyle.types.Interface0DIterator "freestyle.types.Interface0DIterator")) – An Interface0DIterator object.

**Returns:**

The 3D oriented tangent to the 1D element evaluated at the
pointed Interface0D.

**Return type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="freestyle.functions.ZDiscontinuityF0D"></a>

### class freestyle.functions.ZDiscontinuityF0D

Class hierarchy: [`freestyle.types.UnaryFunction0D`](freestyle.types.md#freestyle.types.UnaryFunction0D "freestyle.types.UnaryFunction0D") > [`freestyle.types.UnaryFunction0DDouble`](freestyle.types.md#freestyle.types.UnaryFunction0DDouble "freestyle.types.UnaryFunction0DDouble") > [`ZDiscontinuityF0D`](#freestyle.functions.ZDiscontinuityF0D "freestyle.functions.ZDiscontinuityF0D")

<a id="freestyle.functions.ZDiscontinuityF0D.__init__"></a>

#### freestyle.functions.ZDiscontinuityF0D.__init__()

Builds a ZDiscontinuityF0D object.

<a id="freestyle.functions.ZDiscontinuityF0D.__call__"></a>

#### freestyle.functions.ZDiscontinuityF0D.__call__(it)

Returns a real value giving the distance between the
[`freestyle.types.Interface0D`](freestyle.types.md#freestyle.types.Interface0D "freestyle.types.Interface0D") pointed by the
Interface0DIterator and the shape that lies behind (occludee). This
distance is evaluated in the camera space and normalized between 0 and
1. Therefore, if no object is occluded by the shape to which the
Interface0D belongs to, 1 is returned.

**Parameters:**

**it** ([`freestyle.types.Interface0DIterator`](freestyle.types.md#freestyle.types.Interface0DIterator "freestyle.types.Interface0DIterator")) – An Interface0DIterator object.

**Returns:**

The normalized distance between the pointed Interface0D
and the occludee.

**Return type:**

float

<a id="freestyle.functions.ZDiscontinuityF1D"></a>

### class freestyle.functions.ZDiscontinuityF1D

Class hierarchy: [`freestyle.types.UnaryFunction1D`](freestyle.types.md#freestyle.types.UnaryFunction1D "freestyle.types.UnaryFunction1D") > [`freestyle.types.UnaryFunction1DDouble`](freestyle.types.md#freestyle.types.UnaryFunction1DDouble "freestyle.types.UnaryFunction1DDouble") > [`ZDiscontinuityF1D`](#freestyle.functions.ZDiscontinuityF1D "freestyle.functions.ZDiscontinuityF1D")

<a id="freestyle.functions.ZDiscontinuityF1D.__init__"></a>

#### freestyle.functions.ZDiscontinuityF1D.__init__(integration_type=IntegrationType.MEAN)

Builds a ZDiscontinuityF1D object.

**Parameters:**

**integration_type** ([`freestyle.types.IntegrationType`](freestyle.types.md#freestyle.types.IntegrationType "freestyle.types.IntegrationType")) – The integration method used to compute a single value
from a set of values.

<a id="freestyle.functions.ZDiscontinuityF1D.__call__"></a>

#### freestyle.functions.ZDiscontinuityF1D.__call__(inter)

Returns a real value giving the distance between an Interface1D
and the shape that lies behind (occludee). This distance is
evaluated in the camera space and normalized between 0 and 1.
Therefore, if no object is occluded by the shape to which the
Interface1D belongs to, 1 is returned.

**Parameters:**

**inter** ([`freestyle.types.Interface1D`](freestyle.types.md#freestyle.types.Interface1D "freestyle.types.Interface1D")) – An Interface1D object.

**Returns:**

The normalized distance between the Interface1D and the occludee.

**Return type:**

float

<a id="freestyle.functions.pyCurvilinearLengthF0D"></a>

### class freestyle.functions.pyCurvilinearLengthF0D

<a id="freestyle.functions.pyDensityAnisotropyF0D"></a>

### class freestyle.functions.pyDensityAnisotropyF0D

Estimates the anisotropy of density.

<a id="freestyle.functions.pyDensityAnisotropyF1D"></a>

### class freestyle.functions.pyDensityAnisotropyF1D

<a id="freestyle.functions.pyGetInverseProjectedZF1D"></a>

### class freestyle.functions.pyGetInverseProjectedZF1D

<a id="freestyle.functions.pyGetSquareInverseProjectedZF1D"></a>

### class freestyle.functions.pyGetSquareInverseProjectedZF1D

<a id="freestyle.functions.pyInverseCurvature2DAngleF0D"></a>

### class freestyle.functions.pyInverseCurvature2DAngleF0D

<a id="freestyle.functions.pyViewMapGradientNormF0D"></a>

### class freestyle.functions.pyViewMapGradientNormF0D

<a id="freestyle.functions.pyViewMapGradientNormF1D"></a>

### class freestyle.functions.pyViewMapGradientNormF1D

<a id="freestyle.functions.pyViewMapGradientVectorF0D"></a>

### class freestyle.functions.pyViewMapGradientVectorF0D

Returns the gradient vector for a pixel.

<a id="freestyle.functions.pyViewMapGradientVectorF0D.__init__"></a>

#### freestyle.functions.pyViewMapGradientVectorF0D.__init__(level)

Builds a pyViewMapGradientVectorF0D object.

**Parameters:**

**level** (int) – the level at which to compute the gradient
