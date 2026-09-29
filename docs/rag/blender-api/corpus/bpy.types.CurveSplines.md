<!-- source: Blender Python API reference 5.2 / bpy.types.CurveSplines.html -->

<a id="curvesplines-bpy-prop-collection"></a>

# CurveSplines(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.CurveSplines"></a>

### class bpy.types.CurveSplines(bpy_prop_collection)

Collection of curve splines

<a id="bpy.types.CurveSplines.active"></a>

#### bpy.types.CurveSplines.active

Active curve spline

**Type:**

[`Spline`](bpy.types.Spline.md#bpy.types.Spline "bpy.types.Spline") | None

<a id="bpy.types.CurveSplines.new"></a>

#### bpy.types.CurveSplines.new(type)

Add a new spline to the curve

**Parameters:**

**type** (Literal['POLY', 'BEZIER', 'NURBS']) – type for the new spline

**Returns:**

The newly created spline

**Return type:**

[`Spline`](bpy.types.Spline.md#bpy.types.Spline "bpy.types.Spline")

<a id="bpy.types.CurveSplines.remove"></a>

#### bpy.types.CurveSplines.remove(spline)

Remove a spline from a curve

**Parameters:**

**spline** ([`Spline`](bpy.types.Spline.md#bpy.types.Spline "bpy.types.Spline") | None) – The spline to remove (never None)

<a id="bpy.types.CurveSplines.clear"></a>

#### bpy.types.CurveSplines.clear()

Remove all splines from a curve

<a id="bpy.types.CurveSplines.bl_rna_get_subclass"></a>

#### classmethod bpy.types.CurveSplines.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.CurveSplines.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.CurveSplines.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Curve.splines`](bpy.types.Curve.md#bpy.types.Curve.splines "bpy.types.Curve.splines") |  |
