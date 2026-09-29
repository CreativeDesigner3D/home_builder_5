<!-- source: Blender Python API reference 5.2 / freestyle.shaders.html -->

<a id="module-freestyle.shaders"></a>

# Freestyle Shaders (freestyle.shaders)

This module contains stroke shaders used for creation of stylized
strokes. It is also intended to be a collection of examples for
shader definition in Python.

User-defined stroke shaders inherit the
[`freestyle.types.StrokeShader`](freestyle.types.md#freestyle.types.StrokeShader "freestyle.types.StrokeShader") class.

<a id="freestyle.shaders.BackboneStretcherShader"></a>

### class freestyle.shaders.BackboneStretcherShader

Class hierarchy: [`freestyle.types.StrokeShader`](freestyle.types.md#freestyle.types.StrokeShader "freestyle.types.StrokeShader") > [`BackboneStretcherShader`](#freestyle.shaders.BackboneStretcherShader "freestyle.shaders.BackboneStretcherShader")

[Geometry shader]

<a id="freestyle.shaders.BackboneStretcherShader.__init__"></a>

#### freestyle.shaders.BackboneStretcherShader.__init__(amount=2.0)

Builds a BackboneStretcherShader object.

**Parameters:**

**amount** (float) – The stretching amount value.

<a id="freestyle.shaders.BackboneStretcherShader.shade"></a>

#### freestyle.shaders.BackboneStretcherShader.shade(stroke)

Stretches the stroke at its two extremities and following the
respective directions: v(1)v(0) and v(n-1)v(n).

**Parameters:**

**stroke** ([`freestyle.types.Stroke`](freestyle.types.md#freestyle.types.Stroke "freestyle.types.Stroke")) – A Stroke object.

<a id="freestyle.shaders.BezierCurveShader"></a>

### class freestyle.shaders.BezierCurveShader

Class hierarchy: [`freestyle.types.StrokeShader`](freestyle.types.md#freestyle.types.StrokeShader "freestyle.types.StrokeShader") > [`BezierCurveShader`](#freestyle.shaders.BezierCurveShader "freestyle.shaders.BezierCurveShader")

[Geometry shader]

<a id="freestyle.shaders.BezierCurveShader.__init__"></a>

#### freestyle.shaders.BezierCurveShader.__init__(error=4.0)

Builds a BezierCurveShader object.

**Parameters:**

**error** (float) – The error we’re allowing for the approximation. This
error is the max distance allowed between the new curve and the
original geometry.

<a id="freestyle.shaders.BezierCurveShader.shade"></a>

#### freestyle.shaders.BezierCurveShader.shade(stroke)

Transforms the stroke backbone geometry so that it corresponds to a
Bezier Curve approximation of the original backbone geometry.

**Parameters:**

**stroke** ([`freestyle.types.Stroke`](freestyle.types.md#freestyle.types.Stroke "freestyle.types.Stroke")) – A Stroke object.

<a id="freestyle.shaders.BlenderTextureShader"></a>

### class freestyle.shaders.BlenderTextureShader

Class hierarchy: [`freestyle.types.StrokeShader`](freestyle.types.md#freestyle.types.StrokeShader "freestyle.types.StrokeShader") > [`BlenderTextureShader`](#freestyle.shaders.BlenderTextureShader "freestyle.shaders.BlenderTextureShader")

[Texture shader]

<a id="freestyle.shaders.BlenderTextureShader.__init__"></a>

#### freestyle.shaders.BlenderTextureShader.__init__(texture)

Builds a BlenderTextureShader object.

**Parameters:**

**texture** ([`bpy.types.LineStyleTextureSlot`](bpy.types.LineStyleTextureSlot.md#bpy.types.LineStyleTextureSlot "bpy.types.LineStyleTextureSlot") | [`bpy.types.ShaderNodeTree`](bpy.types.ShaderNodeTree.md#bpy.types.ShaderNodeTree "bpy.types.ShaderNodeTree")) – A line style texture slot or a shader node tree to define a set of textures.

<a id="freestyle.shaders.BlenderTextureShader.shade"></a>

#### freestyle.shaders.BlenderTextureShader.shade(stroke)

Assigns a blender texture slot to the stroke shading in order to
simulate marks.

**Parameters:**

**stroke** ([`freestyle.types.Stroke`](freestyle.types.md#freestyle.types.Stroke "freestyle.types.Stroke")) – A Stroke object.

<a id="freestyle.shaders.CalligraphicShader"></a>

### class freestyle.shaders.CalligraphicShader

Class hierarchy: [`freestyle.types.StrokeShader`](freestyle.types.md#freestyle.types.StrokeShader "freestyle.types.StrokeShader") > [`CalligraphicShader`](#freestyle.shaders.CalligraphicShader "freestyle.shaders.CalligraphicShader")

[Thickness Shader]

<a id="freestyle.shaders.CalligraphicShader.__init__"></a>

#### freestyle.shaders.CalligraphicShader.__init__(thickness_min, thickness_max, orientation, clamp)

Builds a CalligraphicShader object.

**Parameters:**

- **thickness_min** (float) – The minimum thickness in the direction
  perpendicular to the main direction.
- **thickness_max** (float) – The maximum thickness in the main direction.
- **orientation** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – The 2D vector giving the main direction.
- **clamp** (bool) – If true, the strokes are drawn in black when the stroke
  direction is between -90 and 90 degrees with respect to the main
  direction and drawn in white otherwise. If false, the strokes
  are always drawn in black.

<a id="freestyle.shaders.CalligraphicShader.shade"></a>

#### freestyle.shaders.CalligraphicShader.shade(stroke)

Assigns thicknesses to the stroke vertices so that the stroke looks
like made with a calligraphic tool, i.e. the stroke will be the
thickest in a main direction, and the thinnest in the direction
perpendicular to this one, and an interpolation in between.

**Parameters:**

**stroke** ([`freestyle.types.Stroke`](freestyle.types.md#freestyle.types.Stroke "freestyle.types.Stroke")) – A Stroke object.

<a id="freestyle.shaders.ColorNoiseShader"></a>

### class freestyle.shaders.ColorNoiseShader

Class hierarchy: [`freestyle.types.StrokeShader`](freestyle.types.md#freestyle.types.StrokeShader "freestyle.types.StrokeShader") > [`ColorNoiseShader`](#freestyle.shaders.ColorNoiseShader "freestyle.shaders.ColorNoiseShader")

[Color shader]

<a id="freestyle.shaders.ColorNoiseShader.__init__"></a>

#### freestyle.shaders.ColorNoiseShader.__init__(amplitude, period)

Builds a ColorNoiseShader object.

**Parameters:**

- **amplitude** (float) – The amplitude of the noise signal.
- **period** (float) – The period of the noise signal.

<a id="freestyle.shaders.ColorNoiseShader.shade"></a>

#### freestyle.shaders.ColorNoiseShader.shade(stroke)

Shader to add noise to the stroke colors.

**Parameters:**

**stroke** ([`freestyle.types.Stroke`](freestyle.types.md#freestyle.types.Stroke "freestyle.types.Stroke")) – A Stroke object.

<a id="freestyle.shaders.ConstantColorShader"></a>

### class freestyle.shaders.ConstantColorShader

Class hierarchy: [`freestyle.types.StrokeShader`](freestyle.types.md#freestyle.types.StrokeShader "freestyle.types.StrokeShader") > [`ConstantColorShader`](#freestyle.shaders.ConstantColorShader "freestyle.shaders.ConstantColorShader")

[Color shader]

<a id="freestyle.shaders.ConstantColorShader.__init__"></a>

#### freestyle.shaders.ConstantColorShader.__init__(red, green, blue, alpha=1.0)

Builds a ConstantColorShader object.

**Parameters:**

- **red** (float) – The red component.
- **green** (float) – The green component.
- **blue** (float) – The blue component.
- **alpha** (float) – The alpha value.

<a id="freestyle.shaders.ConstantColorShader.shade"></a>

#### freestyle.shaders.ConstantColorShader.shade(stroke)

Assigns a constant color to every vertex of the Stroke.

**Parameters:**

**stroke** ([`freestyle.types.Stroke`](freestyle.types.md#freestyle.types.Stroke "freestyle.types.Stroke")) – A Stroke object.

<a id="freestyle.shaders.ConstantThicknessShader"></a>

### class freestyle.shaders.ConstantThicknessShader

Class hierarchy: [`freestyle.types.StrokeShader`](freestyle.types.md#freestyle.types.StrokeShader "freestyle.types.StrokeShader") > [`ConstantThicknessShader`](#freestyle.shaders.ConstantThicknessShader "freestyle.shaders.ConstantThicknessShader")

[Thickness shader]

<a id="freestyle.shaders.ConstantThicknessShader.__init__"></a>

#### freestyle.shaders.ConstantThicknessShader.__init__(thickness)

Builds a ConstantThicknessShader object.

**Parameters:**

**thickness** (float) – The thickness that must be assigned to the stroke.

<a id="freestyle.shaders.ConstantThicknessShader.shade"></a>

#### freestyle.shaders.ConstantThicknessShader.shade(stroke)

Assigns an absolute constant thickness to every vertex of the Stroke.

**Parameters:**

**stroke** ([`freestyle.types.Stroke`](freestyle.types.md#freestyle.types.Stroke "freestyle.types.Stroke")) – A Stroke object.

<a id="freestyle.shaders.ConstrainedIncreasingThicknessShader"></a>

### class freestyle.shaders.ConstrainedIncreasingThicknessShader

Class hierarchy: [`freestyle.types.StrokeShader`](freestyle.types.md#freestyle.types.StrokeShader "freestyle.types.StrokeShader") > [`ConstrainedIncreasingThicknessShader`](#freestyle.shaders.ConstrainedIncreasingThicknessShader "freestyle.shaders.ConstrainedIncreasingThicknessShader")

[Thickness shader]

<a id="freestyle.shaders.ConstrainedIncreasingThicknessShader.__init__"></a>

#### freestyle.shaders.ConstrainedIncreasingThicknessShader.__init__(thickness_min, thickness_max, ratio)

Builds a ConstrainedIncreasingThicknessShader object.

**Parameters:**

- **thickness_min** (float) – The minimum thickness.
- **thickness_max** (float) – The maximum thickness.
- **ratio** (float) – The thickness/length ratio that we don’t want to exceed.

<a id="freestyle.shaders.ConstrainedIncreasingThicknessShader.shade"></a>

#### freestyle.shaders.ConstrainedIncreasingThicknessShader.shade(stroke)

Same as the [`IncreasingThicknessShader`](#freestyle.shaders.IncreasingThicknessShader "freestyle.shaders.IncreasingThicknessShader"), but here we allow
the user to control the thickness/length ratio so that we don’t get
fat short lines.

**Parameters:**

**stroke** ([`freestyle.types.Stroke`](freestyle.types.md#freestyle.types.Stroke "freestyle.types.Stroke")) – A Stroke object.

<a id="freestyle.shaders.GuidingLinesShader"></a>

### class freestyle.shaders.GuidingLinesShader

Class hierarchy: [`freestyle.types.StrokeShader`](freestyle.types.md#freestyle.types.StrokeShader "freestyle.types.StrokeShader") > [`GuidingLinesShader`](#freestyle.shaders.GuidingLinesShader "freestyle.shaders.GuidingLinesShader")

[Geometry shader]

<a id="freestyle.shaders.GuidingLinesShader.__init__"></a>

#### freestyle.shaders.GuidingLinesShader.__init__(offset)

Builds a GuidingLinesShader object.

**Parameters:**

**offset** (float) – The line that replaces the stroke is initially in the
middle of the initial stroke bounding box. offset is the value
of the displacement which is applied to this line along its
normal.

<a id="freestyle.shaders.GuidingLinesShader.shade"></a>

#### freestyle.shaders.GuidingLinesShader.shade(stroke)

Shader to modify the Stroke geometry so that it corresponds to its
main direction line. This shader must be used together with the
splitting operator using the curvature criterion. Indeed, the
precision of the approximation will depend on the size of the
stroke’s pieces. The bigger the pieces are, the rougher the
approximation is.

**Parameters:**

**stroke** ([`freestyle.types.Stroke`](freestyle.types.md#freestyle.types.Stroke "freestyle.types.Stroke")) – A Stroke object.

<a id="freestyle.shaders.IncreasingColorShader"></a>

### class freestyle.shaders.IncreasingColorShader

Class hierarchy: [`freestyle.types.StrokeShader`](freestyle.types.md#freestyle.types.StrokeShader "freestyle.types.StrokeShader") > [`IncreasingColorShader`](#freestyle.shaders.IncreasingColorShader "freestyle.shaders.IncreasingColorShader")

[Color shader]

<a id="freestyle.shaders.IncreasingColorShader.__init__"></a>

#### freestyle.shaders.IncreasingColorShader.__init__(red_min, green_min, blue_min, alpha_min, red_max, green_max, blue_max, alpha_max)

Builds an IncreasingColorShader object.

**Parameters:**

- **red_min** (float) – The first color red component.
- **green_min** (float) – The first color green component.
- **blue_min** (float) – The first color blue component.
- **alpha_min** (float) – The first color alpha value.
- **red_max** (float) – The second color red component.
- **green_max** (float) – The second color green component.
- **blue_max** (float) – The second color blue component.
- **alpha_max** (float) – The second color alpha value.

<a id="freestyle.shaders.IncreasingColorShader.shade"></a>

#### freestyle.shaders.IncreasingColorShader.shade(stroke)

Assigns a varying color to the stroke. The user specifies two
colors A and B. The stroke color will change linearly from A to B
between the first and the last vertex.

**Parameters:**

**stroke** ([`freestyle.types.Stroke`](freestyle.types.md#freestyle.types.Stroke "freestyle.types.Stroke")) – A Stroke object.

<a id="freestyle.shaders.IncreasingThicknessShader"></a>

### class freestyle.shaders.IncreasingThicknessShader

Class hierarchy: [`freestyle.types.StrokeShader`](freestyle.types.md#freestyle.types.StrokeShader "freestyle.types.StrokeShader") > [`IncreasingThicknessShader`](#freestyle.shaders.IncreasingThicknessShader "freestyle.shaders.IncreasingThicknessShader")

[Thickness shader]

<a id="freestyle.shaders.IncreasingThicknessShader.__init__"></a>

#### freestyle.shaders.IncreasingThicknessShader.__init__(thickness_A, thickness_B)

Builds an IncreasingThicknessShader object.

**Parameters:**

- **thickness_A** (float) – The first thickness value.
- **thickness_B** (float) – The second thickness value.

<a id="freestyle.shaders.IncreasingThicknessShader.shade"></a>

#### freestyle.shaders.IncreasingThicknessShader.shade(stroke)

Assigns thicknesses values such as the thickness increases from a
thickness value A to a thickness value B between the first vertex
to the midpoint vertex and then decreases from B to a A between
this midpoint vertex and the last vertex. The thickness is
linearly interpolated from A to B.

**Parameters:**

**stroke** ([`freestyle.types.Stroke`](freestyle.types.md#freestyle.types.Stroke "freestyle.types.Stroke")) – A Stroke object.

<a id="freestyle.shaders.PolygonalizationShader"></a>

### class freestyle.shaders.PolygonalizationShader

Class hierarchy: [`freestyle.types.StrokeShader`](freestyle.types.md#freestyle.types.StrokeShader "freestyle.types.StrokeShader") > [`PolygonalizationShader`](#freestyle.shaders.PolygonalizationShader "freestyle.shaders.PolygonalizationShader")

[Geometry shader]

<a id="freestyle.shaders.PolygonalizationShader.__init__"></a>

#### freestyle.shaders.PolygonalizationShader.__init__(error)

Builds a PolygonalizationShader object.

**Parameters:**

**error** (float) – The error we want our polygonal approximation to have
with respect to the original geometry. The smaller, the closer
the new stroke is to the original one. This error corresponds to
the maximum distance between the new stroke and the old one.

<a id="freestyle.shaders.PolygonalizationShader.shade"></a>

#### freestyle.shaders.PolygonalizationShader.shade(stroke)

Modifies the Stroke geometry so that it looks more “polygonal”.
The basic idea is to start from the minimal stroke approximation
consisting in a line joining the first vertex to the last one and
to subdivide using the original stroke vertices until a certain
error is reached.

**Parameters:**

**stroke** ([`freestyle.types.Stroke`](freestyle.types.md#freestyle.types.Stroke "freestyle.types.Stroke")) – A Stroke object.

<a id="freestyle.shaders.RoundCapShader"></a>

### class freestyle.shaders.RoundCapShader

<a id="freestyle.shaders.RoundCapShader.round_cap_thickness"></a>

#### freestyle.shaders.RoundCapShader.round_cap_thickness(x)

**Parameters:**

**x** (float) – A value in [0, 1] along the cap (0 at base, 1 at tip).

**Return type:**

float

<a id="freestyle.shaders.RoundCapShader.shade"></a>

#### freestyle.shaders.RoundCapShader.shade(stroke)

**Parameters:**

**stroke** (`Stroke`) – The stroke to shade.

<a id="freestyle.shaders.SamplingShader"></a>

### class freestyle.shaders.SamplingShader

Class hierarchy: [`freestyle.types.StrokeShader`](freestyle.types.md#freestyle.types.StrokeShader "freestyle.types.StrokeShader") > [`SamplingShader`](#freestyle.shaders.SamplingShader "freestyle.shaders.SamplingShader")

[Geometry shader]

<a id="freestyle.shaders.SamplingShader.__init__"></a>

#### freestyle.shaders.SamplingShader.__init__(sampling)

Builds a SamplingShader object.

**Parameters:**

**sampling** (float) – The sampling to use for the stroke resampling.

<a id="freestyle.shaders.SamplingShader.shade"></a>

#### freestyle.shaders.SamplingShader.shade(stroke)

Resamples the stroke.

**Parameters:**

**stroke** ([`freestyle.types.Stroke`](freestyle.types.md#freestyle.types.Stroke "freestyle.types.Stroke")) – A Stroke object.

<a id="freestyle.shaders.SmoothingShader"></a>

### class freestyle.shaders.SmoothingShader

Class hierarchy: [`freestyle.types.StrokeShader`](freestyle.types.md#freestyle.types.StrokeShader "freestyle.types.StrokeShader") > [`SmoothingShader`](#freestyle.shaders.SmoothingShader "freestyle.shaders.SmoothingShader")

[Geometry shader]

<a id="freestyle.shaders.SmoothingShader.__init__"></a>

#### freestyle.shaders.SmoothingShader.__init__(num_iterations=100, factor_point=0.1, factor_curvature=0.0, factor_curvature_difference=0.2, aniso_point=0.0, aniso_normal=0.0, aniso_curvature=0.0, carricature_factor=1.0)

Builds a SmoothingShader object.

**Parameters:**

- **num_iterations** (int) – The number of iterations.
- **factor_point** (float) – 0.1
- **factor_curvature** (float) – 0.0
- **factor_curvature_difference** (float) – 0.2
- **aniso_point** (float) – 0.0
- **aniso_normal** (float) – 0.0
- **aniso_curvature** (float) – 0.0
- **carricature_factor** (float) – 1.0

<a id="freestyle.shaders.SmoothingShader.shade"></a>

#### freestyle.shaders.SmoothingShader.shade(stroke)

Smooths the stroke by moving the vertices to make the stroke
smoother. Uses curvature flow to converge towards a curve of
constant curvature. The diffusion method we use is anisotropic to
prevent the diffusion across corners.

**Parameters:**

**stroke** ([`freestyle.types.Stroke`](freestyle.types.md#freestyle.types.Stroke "freestyle.types.Stroke")) – A Stroke object.

<a id="freestyle.shaders.SpatialNoiseShader"></a>

### class freestyle.shaders.SpatialNoiseShader

Class hierarchy: [`freestyle.types.StrokeShader`](freestyle.types.md#freestyle.types.StrokeShader "freestyle.types.StrokeShader") > [`SpatialNoiseShader`](#freestyle.shaders.SpatialNoiseShader "freestyle.shaders.SpatialNoiseShader")

[Geometry shader]

<a id="freestyle.shaders.SpatialNoiseShader.__init__"></a>

#### freestyle.shaders.SpatialNoiseShader.__init__(amount, scale, num_octaves, smooth, pure_random)

Builds a SpatialNoiseShader object.

**Parameters:**

- **amount** (float) – The amplitude of the noise.
- **scale** (float) – The noise frequency.
- **num_octaves** (int) – The number of octaves
- **smooth** (bool) – True if you want the noise to be smooth.
- **pure_random** (bool) – True if you don’t want any coherence.

<a id="freestyle.shaders.SpatialNoiseShader.shade"></a>

#### freestyle.shaders.SpatialNoiseShader.shade(stroke)

Spatial Noise stroke shader. Moves the vertices to make the stroke
more noisy.

**Parameters:**

**stroke** ([`freestyle.types.Stroke`](freestyle.types.md#freestyle.types.Stroke "freestyle.types.Stroke")) – A Stroke object.

<a id="freestyle.shaders.SquareCapShader"></a>

### class freestyle.shaders.SquareCapShader

<a id="freestyle.shaders.SquareCapShader.shade"></a>

#### freestyle.shaders.SquareCapShader.shade(stroke)

**Parameters:**

**stroke** (`Stroke`) – The stroke to shade.

<a id="freestyle.shaders.StrokeTextureStepShader"></a>

### class freestyle.shaders.StrokeTextureStepShader

Class hierarchy: [`freestyle.types.StrokeShader`](freestyle.types.md#freestyle.types.StrokeShader "freestyle.types.StrokeShader") > [`StrokeTextureStepShader`](#freestyle.shaders.StrokeTextureStepShader "freestyle.shaders.StrokeTextureStepShader")

[Texture shader]

<a id="freestyle.shaders.StrokeTextureStepShader.__init__"></a>

#### freestyle.shaders.StrokeTextureStepShader.__init__(step)

Builds a StrokeTextureStepShader object.

**Parameters:**

**step** (float) – The spacing along the stroke.

<a id="freestyle.shaders.StrokeTextureStepShader.shade"></a>

#### freestyle.shaders.StrokeTextureStepShader.shade(stroke)

Assigns a spacing factor to the texture coordinates of the Stroke.

**Parameters:**

**stroke** ([`freestyle.types.Stroke`](freestyle.types.md#freestyle.types.Stroke "freestyle.types.Stroke")) – A Stroke object.

<a id="freestyle.shaders.ThicknessNoiseShader"></a>

### class freestyle.shaders.ThicknessNoiseShader

Class hierarchy: [`freestyle.types.StrokeShader`](freestyle.types.md#freestyle.types.StrokeShader "freestyle.types.StrokeShader") > [`ThicknessNoiseShader`](#freestyle.shaders.ThicknessNoiseShader "freestyle.shaders.ThicknessNoiseShader")

[Thickness shader]

<a id="freestyle.shaders.ThicknessNoiseShader.__init__"></a>

#### freestyle.shaders.ThicknessNoiseShader.__init__(amplitude, period)

Builds a ThicknessNoiseShader object.

**Parameters:**

- **amplitude** (float) – The amplitude of the noise signal.
- **period** (float) – The period of the noise signal.

<a id="freestyle.shaders.ThicknessNoiseShader.shade"></a>

#### freestyle.shaders.ThicknessNoiseShader.shade(stroke)

Adds some noise to the stroke thickness.

**Parameters:**

**stroke** ([`freestyle.types.Stroke`](freestyle.types.md#freestyle.types.Stroke "freestyle.types.Stroke")) – A Stroke object.

<a id="freestyle.shaders.TipRemoverShader"></a>

### class freestyle.shaders.TipRemoverShader

Class hierarchy: [`freestyle.types.StrokeShader`](freestyle.types.md#freestyle.types.StrokeShader "freestyle.types.StrokeShader") > [`TipRemoverShader`](#freestyle.shaders.TipRemoverShader "freestyle.shaders.TipRemoverShader")

[Geometry shader]

<a id="freestyle.shaders.TipRemoverShader.__init__"></a>

#### freestyle.shaders.TipRemoverShader.__init__(tip_length)

Builds a TipRemoverShader object.

**Parameters:**

**tip_length** (float) – The length of the piece of stroke we want to remove
at each extremity.

<a id="freestyle.shaders.TipRemoverShader.shade"></a>

#### freestyle.shaders.TipRemoverShader.shade(stroke)

Removes the stroke’s extremities.

**Parameters:**

**stroke** ([`freestyle.types.Stroke`](freestyle.types.md#freestyle.types.Stroke "freestyle.types.Stroke")) – A Stroke object.

<a id="freestyle.shaders.py2DCurvatureColorShader"></a>

### class freestyle.shaders.py2DCurvatureColorShader

Assigns a color (grayscale) to the stroke based on the curvature.
A higher curvature will yield a brighter color.

<a id="freestyle.shaders.py2DCurvatureColorShader.shade"></a>

#### freestyle.shaders.py2DCurvatureColorShader.shade(stroke)

**Parameters:**

**stroke** (`Stroke`) – The stroke to shade.

<a id="freestyle.shaders.pyBackboneStretcherNoCuspShader"></a>

### class freestyle.shaders.pyBackboneStretcherNoCuspShader

Stretches the stroke’s backbone, excluding cusp vertices (end junctions).

<a id="freestyle.shaders.pyBackboneStretcherNoCuspShader.shade"></a>

#### freestyle.shaders.pyBackboneStretcherNoCuspShader.shade(stroke)

**Parameters:**

**stroke** (`Stroke`) – The stroke to shade.

<a id="freestyle.shaders.pyBackboneStretcherShader"></a>

### class freestyle.shaders.pyBackboneStretcherShader

Stretches the stroke’s backbone by a given length (in pixels).

<a id="freestyle.shaders.pyBackboneStretcherShader.shade"></a>

#### freestyle.shaders.pyBackboneStretcherShader.shade(stroke)

**Parameters:**

**stroke** (`Stroke`) – The stroke to shade.

<a id="freestyle.shaders.pyBluePrintCirclesShader"></a>

### class freestyle.shaders.pyBluePrintCirclesShader

Draws the silhouette of the object as a circle.

<a id="freestyle.shaders.pyBluePrintCirclesShader.shade"></a>

#### freestyle.shaders.pyBluePrintCirclesShader.shade(stroke)

**Parameters:**

**stroke** (`Stroke`) – The stroke to shade.

<a id="freestyle.shaders.pyBluePrintDirectedSquaresShader"></a>

### class freestyle.shaders.pyBluePrintDirectedSquaresShader

Replaces the stroke with a directed square.

<a id="freestyle.shaders.pyBluePrintDirectedSquaresShader.shade"></a>

#### freestyle.shaders.pyBluePrintDirectedSquaresShader.shade(stroke)

**Parameters:**

**stroke** (`Stroke`) – The stroke to shade.

<a id="freestyle.shaders.pyBluePrintEllipsesShader"></a>

### class freestyle.shaders.pyBluePrintEllipsesShader

<a id="freestyle.shaders.pyBluePrintEllipsesShader.shade"></a>

#### freestyle.shaders.pyBluePrintEllipsesShader.shade(stroke)

**Parameters:**

**stroke** (`Stroke`) – The stroke to shade.

<a id="freestyle.shaders.pyBluePrintSquaresShader"></a>

### class freestyle.shaders.pyBluePrintSquaresShader

<a id="freestyle.shaders.pyBluePrintSquaresShader.shade"></a>

#### freestyle.shaders.pyBluePrintSquaresShader.shade(stroke)

**Parameters:**

**stroke** (`Stroke`) – The stroke to shade.

<a id="freestyle.shaders.pyConstantColorShader"></a>

### class freestyle.shaders.pyConstantColorShader

Assigns a constant color to the stroke.

<a id="freestyle.shaders.pyConstantColorShader.shade"></a>

#### freestyle.shaders.pyConstantColorShader.shade(stroke)

**Parameters:**

**stroke** (`Stroke`) – The stroke to shade.

<a id="freestyle.shaders.pyConstantThicknessShader"></a>

### class freestyle.shaders.pyConstantThicknessShader

Assigns a constant thickness along the stroke.

<a id="freestyle.shaders.pyConstantThicknessShader.shade"></a>

#### freestyle.shaders.pyConstantThicknessShader.shade(stroke)

**Parameters:**

**stroke** (`Stroke`) – The stroke to shade.

<a id="freestyle.shaders.pyConstrainedIncreasingThicknessShader"></a>

### class freestyle.shaders.pyConstrainedIncreasingThicknessShader

Increasingly thickens the stroke, constrained by a ratio of the
stroke’s length.

<a id="freestyle.shaders.pyConstrainedIncreasingThicknessShader.shade"></a>

#### freestyle.shaders.pyConstrainedIncreasingThicknessShader.shade(stroke)

**Parameters:**

**stroke** (`Stroke`) – The stroke to shade.

<a id="freestyle.shaders.pyDecreasingThicknessShader"></a>

### class freestyle.shaders.pyDecreasingThicknessShader

Inverse of pyIncreasingThicknessShader, decreasingly thickens the stroke.

<a id="freestyle.shaders.pyDecreasingThicknessShader.shade"></a>

#### freestyle.shaders.pyDecreasingThicknessShader.shade(stroke)

**Parameters:**

**stroke** (`Stroke`) – The stroke to shade.

<a id="freestyle.shaders.pyDepthDiscontinuityThicknessShader"></a>

### class freestyle.shaders.pyDepthDiscontinuityThicknessShader

Assigns a thickness to the stroke based on the stroke’s distance
to the camera (Z-value).

<a id="freestyle.shaders.pyDepthDiscontinuityThicknessShader.shade"></a>

#### freestyle.shaders.pyDepthDiscontinuityThicknessShader.shade(stroke)

**Parameters:**

**stroke** (`Stroke`) – The stroke to shade.

<a id="freestyle.shaders.pyDiffusion2Shader"></a>

### class freestyle.shaders.pyDiffusion2Shader

Iteratively adds an offset to the position of each stroke vertex
in the direction perpendicular to the stroke direction at the
point. The offset is scaled by the 2D curvature (i.e. how quickly
the stroke curve is) at the point.

<a id="freestyle.shaders.pyDiffusion2Shader.shade"></a>

#### freestyle.shaders.pyDiffusion2Shader.shade(stroke)

**Parameters:**

**stroke** (`Stroke`) – The stroke to shade.

<a id="freestyle.shaders.pyFXSVaryingThicknessWithDensityShader"></a>

### class freestyle.shaders.pyFXSVaryingThicknessWithDensityShader

Assigns thickness to a stroke based on the density of the diffuse map.

<a id="freestyle.shaders.pyFXSVaryingThicknessWithDensityShader.shade"></a>

#### freestyle.shaders.pyFXSVaryingThicknessWithDensityShader.shade(stroke)

**Parameters:**

**stroke** (`Stroke`) – The stroke to shade.

<a id="freestyle.shaders.pyGuidingLineShader"></a>

### class freestyle.shaders.pyGuidingLineShader

<a id="freestyle.shaders.pyGuidingLineShader.shade"></a>

#### freestyle.shaders.pyGuidingLineShader.shade(stroke)

**Parameters:**

**stroke** (`Stroke`) – The stroke to shade.

<a id="freestyle.shaders.pyHLRShader"></a>

### class freestyle.shaders.pyHLRShader

Controls visibility based upon the quantitative invisibility (QI)
based on hidden line removal (HLR).

<a id="freestyle.shaders.pyHLRShader.shade"></a>

#### freestyle.shaders.pyHLRShader.shade(stroke)

**Parameters:**

**stroke** (`Stroke`) – The stroke to shade.

<a id="freestyle.shaders.pyImportance2DThicknessShader"></a>

### class freestyle.shaders.pyImportance2DThicknessShader

Assigns thickness based on distance to a given point in 2D space.
the thickness is inverted, so the vertices closest to the
specified point have the lowest thickness.

<a id="freestyle.shaders.pyImportance2DThicknessShader.shade"></a>

#### freestyle.shaders.pyImportance2DThicknessShader.shade(stroke)

**Parameters:**

**stroke** (`Stroke`) – The stroke to shade.

<a id="freestyle.shaders.pyImportance3DThicknessShader"></a>

### class freestyle.shaders.pyImportance3DThicknessShader

Assigns thickness based on distance to a given point in 3D space.

<a id="freestyle.shaders.pyImportance3DThicknessShader.shade"></a>

#### freestyle.shaders.pyImportance3DThicknessShader.shade(stroke)

**Parameters:**

**stroke** (`Stroke`) – The stroke to shade.

<a id="freestyle.shaders.pyIncreasingColorShader"></a>

### class freestyle.shaders.pyIncreasingColorShader

Fades from one color to another along the stroke.

<a id="freestyle.shaders.pyIncreasingColorShader.shade"></a>

#### freestyle.shaders.pyIncreasingColorShader.shade(stroke)

**Parameters:**

**stroke** (`Stroke`) – The stroke to shade.

<a id="freestyle.shaders.pyIncreasingThicknessShader"></a>

### class freestyle.shaders.pyIncreasingThicknessShader

Increasingly thickens the stroke.

<a id="freestyle.shaders.pyIncreasingThicknessShader.shade"></a>

#### freestyle.shaders.pyIncreasingThicknessShader.shade(stroke)

**Parameters:**

**stroke** (`Stroke`) – The stroke to shade.

<a id="freestyle.shaders.pyInterpolateColorShader"></a>

### class freestyle.shaders.pyInterpolateColorShader

Fades from one color to another and back.

<a id="freestyle.shaders.pyInterpolateColorShader.shade"></a>

#### freestyle.shaders.pyInterpolateColorShader.shade(stroke)

**Parameters:**

**stroke** (`Stroke`) – The stroke to shade.

<a id="freestyle.shaders.pyLengthDependingBackboneStretcherShader"></a>

### class freestyle.shaders.pyLengthDependingBackboneStretcherShader

Stretches the stroke’s backbone proportional to the stroke’s length
NOTE: you’ll probably want an l somewhere between (0.5 - 0). A value that
is too high may yield unexpected results.

<a id="freestyle.shaders.pyLengthDependingBackboneStretcherShader.shade"></a>

#### freestyle.shaders.pyLengthDependingBackboneStretcherShader.shade(stroke)

**Parameters:**

**stroke** (`Stroke`) – The stroke to shade.

<a id="freestyle.shaders.pyMaterialColorShader"></a>

### class freestyle.shaders.pyMaterialColorShader

Assigns the color of the underlying material to the stroke.

<a id="freestyle.shaders.pyMaterialColorShader.shade"></a>

#### freestyle.shaders.pyMaterialColorShader.shade(stroke)

**Parameters:**

**stroke** (`Stroke`) – The stroke to shade.

<a id="freestyle.shaders.pyModulateAlphaShader"></a>

### class freestyle.shaders.pyModulateAlphaShader

Limits the stroke’s alpha between a min and max value.

<a id="freestyle.shaders.pyModulateAlphaShader.shade"></a>

#### freestyle.shaders.pyModulateAlphaShader.shade(stroke)

**Parameters:**

**stroke** (`Stroke`) – The stroke to shade.

<a id="freestyle.shaders.pyNonLinearVaryingThicknessShader"></a>

### class freestyle.shaders.pyNonLinearVaryingThicknessShader

Assigns thickness to a stroke based on an exponential function.

<a id="freestyle.shaders.pyNonLinearVaryingThicknessShader.shade"></a>

#### freestyle.shaders.pyNonLinearVaryingThicknessShader.shade(stroke)

**Parameters:**

**stroke** (`Stroke`) – The stroke to shade.

<a id="freestyle.shaders.pyPerlinNoise1DShader"></a>

### class freestyle.shaders.pyPerlinNoise1DShader

Displaces the stroke using the curvilinear abscissa. This means
that lines with the same length and sampling interval will be
identically distorted.

<a id="freestyle.shaders.pyPerlinNoise1DShader.shade"></a>

#### freestyle.shaders.pyPerlinNoise1DShader.shade(stroke)

**Parameters:**

**stroke** (`Stroke`) – The stroke to shade.

<a id="freestyle.shaders.pyPerlinNoise2DShader"></a>

### class freestyle.shaders.pyPerlinNoise2DShader

Displaces the stroke using the strokes coordinates. This means
that in a scene no strokes will be distorted identically.

More information on the noise shaders can be found at:
<https://freestyleintegration.wordpress.com/2011/09/25/development-updates-on-september-25/>

<a id="freestyle.shaders.pyPerlinNoise2DShader.shade"></a>

#### freestyle.shaders.pyPerlinNoise2DShader.shade(stroke)

**Parameters:**

**stroke** (`Stroke`) – The stroke to shade.

<a id="freestyle.shaders.pyRandomColorShader"></a>

### class freestyle.shaders.pyRandomColorShader

Assigns a color to the stroke based on given seed.

<a id="freestyle.shaders.pyRandomColorShader.shade"></a>

#### freestyle.shaders.pyRandomColorShader.shade(stroke)

**Parameters:**

**stroke** (`Stroke`) – The stroke to shade.

<a id="freestyle.shaders.pySLERPThicknessShader"></a>

### class freestyle.shaders.pySLERPThicknessShader

Assigns thickness to a stroke based on spherical linear interpolation.

<a id="freestyle.shaders.pySLERPThicknessShader.shade"></a>

#### freestyle.shaders.pySLERPThicknessShader.shade(stroke)

**Parameters:**

**stroke** (`Stroke`) – The stroke to shade.

<a id="freestyle.shaders.pySamplingShader"></a>

### class freestyle.shaders.pySamplingShader

Resamples the stroke, which gives the stroke the amount of
vertices specified.

<a id="freestyle.shaders.pySamplingShader.shade"></a>

#### freestyle.shaders.pySamplingShader.shade(stroke)

**Parameters:**

**stroke** (`Stroke`) – The stroke to shade.

<a id="freestyle.shaders.pySinusDisplacementShader"></a>

### class freestyle.shaders.pySinusDisplacementShader

Displaces the stroke in the shape of a sine wave.

<a id="freestyle.shaders.pySinusDisplacementShader.shade"></a>

#### freestyle.shaders.pySinusDisplacementShader.shade(stroke)

**Parameters:**

**stroke** (`Stroke`) – The stroke to shade.

<a id="freestyle.shaders.pyTVertexRemoverShader"></a>

### class freestyle.shaders.pyTVertexRemoverShader

Removes t-vertices from the stroke.

<a id="freestyle.shaders.pyTVertexRemoverShader.shade"></a>

#### freestyle.shaders.pyTVertexRemoverShader.shade(stroke)

**Parameters:**

**stroke** (`Stroke`) – The stroke to shade.

<a id="freestyle.shaders.pyTVertexThickenerShader"></a>

### class freestyle.shaders.pyTVertexThickenerShader

Thickens TVertices (visual intersections between two edges).

<a id="freestyle.shaders.pyTVertexThickenerShader.shade"></a>

#### freestyle.shaders.pyTVertexThickenerShader.shade(stroke)

**Parameters:**

**stroke** (`Stroke`) – The stroke to shade.

<a id="freestyle.shaders.pyTimeColorShader"></a>

### class freestyle.shaders.pyTimeColorShader

Assigns a grayscale value that increases for every vertex.
The brightness will increase along the stroke.

<a id="freestyle.shaders.pyTimeColorShader.shade"></a>

#### freestyle.shaders.pyTimeColorShader.shade(stroke)

**Parameters:**

**stroke** (`Stroke`) – The stroke to shade.

<a id="freestyle.shaders.pyTipRemoverShader"></a>

### class freestyle.shaders.pyTipRemoverShader

Removes the tips of the stroke.

<a id="freestyle.shaders.pyTipRemoverShader.shade"></a>

#### freestyle.shaders.pyTipRemoverShader.shade(stroke)

**Parameters:**

**stroke** (`Stroke`) – The stroke to shade.

<a id="freestyle.shaders.pyTipRemoverShader.check_vertex"></a>

#### static freestyle.shaders.pyTipRemoverShader.check_vertex(v, length)

**Parameters:**

- **v** (`StrokeVertex`) – A stroke vertex to test.
- **length** (float) – Distance threshold from the stroke ends.

**Return type:**

bool

<a id="freestyle.shaders.pyZDependingThicknessShader"></a>

### class freestyle.shaders.pyZDependingThicknessShader

Assigns thickness based on an object’s local Z depth (point
closest to camera is 1, point furthest from camera is zero).

<a id="freestyle.shaders.pyZDependingThicknessShader.shade"></a>

#### freestyle.shaders.pyZDependingThicknessShader.shade(stroke)

**Parameters:**

**stroke** (`Stroke`) – The stroke to shade.
