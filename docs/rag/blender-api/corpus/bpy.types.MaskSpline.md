<!-- source: Blender Python API reference 5.2 / bpy.types.MaskSpline.html -->

<a id="maskspline-bpy-struct"></a>

# MaskSpline(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.MaskSpline"></a>

### class bpy.types.MaskSpline(bpy_struct)

Single spline used for defining mask shape

<a id="bpy.types.MaskSpline.offset_mode"></a>

#### bpy.types.MaskSpline.offset_mode

The method used for calculating the feather offset (default `'EVEN'`)

- `EVEN`
  Even – Calculate even feather offset.
- `SMOOTH`
  Smooth – Calculate feather offset as a second curve.

**Type:**

Literal[‘EVEN’, ‘SMOOTH’]

<a id="bpy.types.MaskSpline.points"></a>

#### bpy.types.MaskSpline.points

Collection of points (default None, readonly)

**Type:**

[`MaskSplinePoints`](bpy.types.MaskSplinePoints.md#bpy.types.MaskSplinePoints "bpy.types.MaskSplinePoints")[[`MaskSplinePoint`](bpy.types.MaskSplinePoint.md#bpy.types.MaskSplinePoint "bpy.types.MaskSplinePoint")]

<a id="bpy.types.MaskSpline.use_cyclic"></a>

#### bpy.types.MaskSpline.use_cyclic

Make this spline a closed loop (default False)

**Type:**

bool

<a id="bpy.types.MaskSpline.use_fill"></a>

#### bpy.types.MaskSpline.use_fill

Make this spline filled (default True)

**Type:**

bool

<a id="bpy.types.MaskSpline.use_self_intersection_check"></a>

#### bpy.types.MaskSpline.use_self_intersection_check

Prevent feather from self-intersections (default False)

**Type:**

bool

<a id="bpy.types.MaskSpline.weight_interpolation"></a>

#### bpy.types.MaskSpline.weight_interpolation

The type of weight interpolation for spline (default `'LINEAR'`)

**Type:**

Literal[‘LINEAR’, ‘EASE’]

<a id="bpy.types.MaskSpline.bl_rna_get_subclass"></a>

#### classmethod bpy.types.MaskSpline.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.MaskSpline.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.MaskSpline.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`MaskLayer.splines`](bpy.types.MaskLayer.md#bpy.types.MaskLayer.splines "bpy.types.MaskLayer.splines") - [`MaskSplines.active`](bpy.types.MaskSplines.md#bpy.types.MaskSplines.active "bpy.types.MaskSplines.active") | - [`MaskSplines.new`](bpy.types.MaskSplines.md#bpy.types.MaskSplines.new "bpy.types.MaskSplines.new") - [`MaskSplines.remove`](bpy.types.MaskSplines.md#bpy.types.MaskSplines.remove "bpy.types.MaskSplines.remove") |
