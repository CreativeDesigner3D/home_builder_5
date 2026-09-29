<!-- source: Blender Python API reference 5.2 / bpy.types.Spline.html -->

<a id="spline-bpy-struct"></a>

# Spline(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.Spline"></a>

### class bpy.types.Spline(bpy_struct)

Element of a curve, either NURBS, Bézier or Polyline or a character with text objects

<a id="bpy.types.Spline.bezier_points"></a>

#### bpy.types.Spline.bezier_points

Collection of points for Bézier curves only (default None, readonly)

**Type:**

[`SplineBezierPoints`](bpy.types.SplineBezierPoints.md#bpy.types.SplineBezierPoints "bpy.types.SplineBezierPoints")[[`BezierSplinePoint`](bpy.types.BezierSplinePoint.md#bpy.types.BezierSplinePoint "bpy.types.BezierSplinePoint")]

<a id="bpy.types.Spline.character_index"></a>

#### bpy.types.Spline.character_index

Location of this character in the text data (only for text curves) (in [0, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.Spline.hide"></a>

#### bpy.types.Spline.hide

Hide this curve in Edit mode (default False)

**Type:**

bool

<a id="bpy.types.Spline.material_index"></a>

#### bpy.types.Spline.material_index

Material slot index of this curve (in [0, 32767], default 0)

**Type:**

int

<a id="bpy.types.Spline.order_u"></a>

#### bpy.types.Spline.order_u

NURBS order in the U direction. Higher values make each point influence a greater area, but have worse performance. (in [2, 64], default 0)

**Type:**

int

<a id="bpy.types.Spline.order_v"></a>

#### bpy.types.Spline.order_v

NURBS order in the V direction. Higher values make each point influence a greater area, but have worse performance. (in [2, 64], default 0)

**Type:**

int

<a id="bpy.types.Spline.point_count_u"></a>

#### bpy.types.Spline.point_count_u

Total number points for the curve or surface in the U direction (in [0, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.Spline.point_count_v"></a>

#### bpy.types.Spline.point_count_v

Total number points for the surface on the V direction (in [0, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.Spline.points"></a>

#### bpy.types.Spline.points

Collection of points that make up this poly or nurbs spline (default None, readonly)

**Type:**

[`SplinePoints`](bpy.types.SplinePoints.md#bpy.types.SplinePoints "bpy.types.SplinePoints")[[`SplinePoint`](bpy.types.SplinePoint.md#bpy.types.SplinePoint "bpy.types.SplinePoint")]

<a id="bpy.types.Spline.radius_interpolation"></a>

#### bpy.types.Spline.radius_interpolation

The type of radius interpolation for Bézier curves (default `'LINEAR'`)

**Type:**

Literal[‘LINEAR’, ‘CARDINAL’, ‘BSPLINE’, ‘EASE’]

<a id="bpy.types.Spline.resolution_u"></a>

#### bpy.types.Spline.resolution_u

Curve or Surface subdivisions per segment (in [1, 1024], default 0)

**Type:**

int

<a id="bpy.types.Spline.resolution_v"></a>

#### bpy.types.Spline.resolution_v

Surface subdivisions per segment (in [1, 1024], default 0)

**Type:**

int

<a id="bpy.types.Spline.tilt_interpolation"></a>

#### bpy.types.Spline.tilt_interpolation

The type of tilt interpolation for 3D, Bézier curves (default `'LINEAR'`)

**Type:**

Literal[‘LINEAR’, ‘CARDINAL’, ‘BSPLINE’, ‘EASE’]

<a id="bpy.types.Spline.type"></a>

#### bpy.types.Spline.type

The interpolation type for this curve element (default `'POLY'`)

**Type:**

Literal[‘POLY’, ‘BEZIER’, ‘NURBS’]

<a id="bpy.types.Spline.use_bezier_u"></a>

#### bpy.types.Spline.use_bezier_u

Make this nurbs curve or surface act like a Bézier spline in the U direction (default False)

**Type:**

bool

<a id="bpy.types.Spline.use_bezier_v"></a>

#### bpy.types.Spline.use_bezier_v

Make this nurbs surface act like a Bézier spline in the V direction (default False)

**Type:**

bool

<a id="bpy.types.Spline.use_cyclic_u"></a>

#### bpy.types.Spline.use_cyclic_u

Make this curve or surface a closed loop in the U direction (default False)

**Type:**

bool

<a id="bpy.types.Spline.use_cyclic_v"></a>

#### bpy.types.Spline.use_cyclic_v

Make this surface a closed loop in the V direction (default False)

**Type:**

bool

<a id="bpy.types.Spline.use_endpoint_u"></a>

#### bpy.types.Spline.use_endpoint_u

Make this nurbs curve or surface meet the endpoints in the U direction (default False)

**Type:**

bool

<a id="bpy.types.Spline.use_endpoint_v"></a>

#### bpy.types.Spline.use_endpoint_v

Make this nurbs surface meet the endpoints in the V direction (default False)

**Type:**

bool

<a id="bpy.types.Spline.use_smooth"></a>

#### bpy.types.Spline.use_smooth

Smooth the normals of the surface or beveled curve (default False)

**Type:**

bool

<a id="bpy.types.Spline.calc_length"></a>

#### bpy.types.Spline.calc_length(*, resolution=0)

Calculate spline length

**Parameters:**

**resolution** (int) – Resolution, Spline resolution to be used, 0 defaults to the resolution_u (in [0, 1024], optional)

**Returns:**

Length, Length of the polygonaly approximated spline (in [0, inf])

**Return type:**

float

<a id="bpy.types.Spline.valid_message"></a>

#### bpy.types.Spline.valid_message(direction)

Return the message

**Parameters:**

**direction** (int) – Direction, The direction where 0-1 maps to U-V (in [0, 1])

**Returns:**

Return value, The message or an empty string when there is no error

**Return type:**

str

<a id="bpy.types.Spline.bl_rna_get_subclass"></a>

#### classmethod bpy.types.Spline.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.Spline.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.Spline.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([type](#bpy.types.Spline.type "bpy.types.Spline.type") | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

[type](#bpy.types.Spline.type "bpy.types.Spline.type")

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values

<a id="references"></a>

## References

|  |  |
| --- | --- |
| - [`Curve.splines`](bpy.types.Curve.md#bpy.types.Curve.splines "bpy.types.Curve.splines") - [`CurveSplines.active`](bpy.types.CurveSplines.md#bpy.types.CurveSplines.active "bpy.types.CurveSplines.active") | - [`CurveSplines.new`](bpy.types.CurveSplines.md#bpy.types.CurveSplines.new "bpy.types.CurveSplines.new") - [`CurveSplines.remove`](bpy.types.CurveSplines.md#bpy.types.CurveSplines.remove "bpy.types.CurveSplines.remove") |
