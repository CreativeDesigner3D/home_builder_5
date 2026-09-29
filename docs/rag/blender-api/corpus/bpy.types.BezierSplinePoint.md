<!-- source: Blender Python API reference 5.2 / bpy.types.BezierSplinePoint.html -->

<a id="beziersplinepoint-bpy-struct"></a>

# BezierSplinePoint(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.BezierSplinePoint"></a>

### class bpy.types.BezierSplinePoint(bpy_struct)

Bézier curve point with two handles

<a id="bpy.types.BezierSplinePoint.co"></a>

#### bpy.types.BezierSplinePoint.co

Coordinates of the control point (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.BezierSplinePoint.handle_left"></a>

#### bpy.types.BezierSplinePoint.handle_left

Coordinates of the first handle (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.BezierSplinePoint.handle_left_type"></a>

#### bpy.types.BezierSplinePoint.handle_left_type

Handle types (default `'FREE'`)

**Type:**

Literal[‘FREE’, ‘VECTOR’, ‘ALIGNED’, ‘AUTO’]

<a id="bpy.types.BezierSplinePoint.handle_right"></a>

#### bpy.types.BezierSplinePoint.handle_right

Coordinates of the second handle (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.BezierSplinePoint.handle_right_type"></a>

#### bpy.types.BezierSplinePoint.handle_right_type

Handle types (default `'FREE'`)

**Type:**

Literal[‘FREE’, ‘VECTOR’, ‘ALIGNED’, ‘AUTO’]

<a id="bpy.types.BezierSplinePoint.hide"></a>

#### bpy.types.BezierSplinePoint.hide

Visibility status (default False)

**Type:**

bool

<a id="bpy.types.BezierSplinePoint.radius"></a>

#### bpy.types.BezierSplinePoint.radius

Radius for beveling (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.BezierSplinePoint.select_control_point"></a>

#### bpy.types.BezierSplinePoint.select_control_point

Control point selection status (default False)

**Type:**

bool

<a id="bpy.types.BezierSplinePoint.select_left_handle"></a>

#### bpy.types.BezierSplinePoint.select_left_handle

Handle 1 selection status (default False)

**Type:**

bool

<a id="bpy.types.BezierSplinePoint.select_right_handle"></a>

#### bpy.types.BezierSplinePoint.select_right_handle

Handle 2 selection status (default False)

**Type:**

bool

<a id="bpy.types.BezierSplinePoint.tilt"></a>

#### bpy.types.BezierSplinePoint.tilt

Tilt in 3D View (in [-376.991, 376.991], default 0.0)

**Type:**

float

<a id="bpy.types.BezierSplinePoint.weight_softbody"></a>

#### bpy.types.BezierSplinePoint.weight_softbody

Softbody goal weight (in [0.01, 100], default 0.0)

**Type:**

float

<a id="bpy.types.BezierSplinePoint.bl_rna_get_subclass"></a>

#### classmethod bpy.types.BezierSplinePoint.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.BezierSplinePoint.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.BezierSplinePoint.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

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
| - [`Spline.bezier_points`](bpy.types.Spline.md#bpy.types.Spline.bezier_points "bpy.types.Spline.bezier_points") |  |
