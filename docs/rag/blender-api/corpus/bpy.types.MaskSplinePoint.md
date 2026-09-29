<!-- source: Blender Python API reference 5.2 / bpy.types.MaskSplinePoint.html -->

<a id="masksplinepoint-bpy-struct"></a>

# MaskSplinePoint(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.MaskSplinePoint"></a>

### class bpy.types.MaskSplinePoint(bpy_struct)

Single point in spline used for defining mask

<a id="bpy.types.MaskSplinePoint.co"></a>

#### bpy.types.MaskSplinePoint.co

Coordinates of the control point (array of 2 items, in [-inf, inf], default (0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.MaskSplinePoint.feather_points"></a>

#### bpy.types.MaskSplinePoint.feather_points

Points defining feather (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`MaskSplinePointUW`](bpy.types.MaskSplinePointUW.md#bpy.types.MaskSplinePointUW "bpy.types.MaskSplinePointUW")]

<a id="bpy.types.MaskSplinePoint.handle_left"></a>

#### bpy.types.MaskSplinePoint.handle_left

Coordinates of the first handle (array of 2 items, in [-inf, inf], default (0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.MaskSplinePoint.handle_left_type"></a>

#### bpy.types.MaskSplinePoint.handle_left_type

Handle type (default `'FREE'`)

**Type:**

Literal[‘AUTO’, ‘VECTOR’, ‘ALIGNED’, ‘ALIGNED_DOUBLESIDE’, ‘FREE’]

<a id="bpy.types.MaskSplinePoint.handle_right"></a>

#### bpy.types.MaskSplinePoint.handle_right

Coordinates of the second handle (array of 2 items, in [-inf, inf], default (0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.MaskSplinePoint.handle_right_type"></a>

#### bpy.types.MaskSplinePoint.handle_right_type

Handle type (default `'FREE'`)

**Type:**

Literal[‘AUTO’, ‘VECTOR’, ‘ALIGNED’, ‘ALIGNED_DOUBLESIDE’, ‘FREE’]

<a id="bpy.types.MaskSplinePoint.handle_type"></a>

#### bpy.types.MaskSplinePoint.handle_type

Handle type (default `'FREE'`)

**Type:**

Literal[‘AUTO’, ‘VECTOR’, ‘ALIGNED’, ‘ALIGNED_DOUBLESIDE’, ‘FREE’]

<a id="bpy.types.MaskSplinePoint.parent"></a>

#### bpy.types.MaskSplinePoint.parent

(readonly)

**Type:**

[`MaskParent`](bpy.types.MaskParent.md#bpy.types.MaskParent "bpy.types.MaskParent") | None

<a id="bpy.types.MaskSplinePoint.select"></a>

#### bpy.types.MaskSplinePoint.select

Selection status of the control point. (Deprecated: use Select Control Point instead) (default False)

**Type:**

bool

<a id="bpy.types.MaskSplinePoint.select_control_point"></a>

#### bpy.types.MaskSplinePoint.select_control_point

Selection status of the control point (default False)

**Type:**

bool

<a id="bpy.types.MaskSplinePoint.select_left_handle"></a>

#### bpy.types.MaskSplinePoint.select_left_handle

Selection status of the left handle (default False)

**Type:**

bool

<a id="bpy.types.MaskSplinePoint.select_right_handle"></a>

#### bpy.types.MaskSplinePoint.select_right_handle

Selection status of the right handle (default False)

**Type:**

bool

<a id="bpy.types.MaskSplinePoint.select_single_handle"></a>

#### bpy.types.MaskSplinePoint.select_single_handle

Selection status of the Aligned Single handle (default False)

**Type:**

bool

<a id="bpy.types.MaskSplinePoint.weight"></a>

#### bpy.types.MaskSplinePoint.weight

Weight of the point (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.MaskSplinePoint.bl_rna_get_subclass"></a>

#### classmethod bpy.types.MaskSplinePoint.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.MaskSplinePoint.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.MaskSplinePoint.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`MaskSpline.points`](bpy.types.MaskSpline.md#bpy.types.MaskSpline.points "bpy.types.MaskSpline.points") - [`MaskSplinePoints.remove`](bpy.types.MaskSplinePoints.md#bpy.types.MaskSplinePoints.remove "bpy.types.MaskSplinePoints.remove") | - [`MaskSplines.active_point`](bpy.types.MaskSplines.md#bpy.types.MaskSplines.active_point "bpy.types.MaskSplines.active_point") |
