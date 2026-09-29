<!-- source: Blender Python API reference 5.2 / mathutils.interpolate.html -->

<a id="module-mathutils.interpolate"></a>

# Interpolation Utilities (mathutils.interpolate)

The Blender interpolate module.

<a id="mathutils.interpolate.poly_3d_calc"></a>

### mathutils.interpolate.poly_3d_calc(veclist, pt, /)

Calculate barycentric weights for a point on a polygon.

**Parameters:**

- **veclist** (Sequence[Sequence[float]]) – Sequence of 3D positions.
- **pt** (Sequence[float]) – 2D or 3D position.

**Returns:**

A list of weights, one per vertex in veclist.

**Return type:**

list[float]
