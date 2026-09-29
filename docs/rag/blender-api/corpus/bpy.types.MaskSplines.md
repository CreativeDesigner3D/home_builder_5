<!-- source: Blender Python API reference 5.2 / bpy.types.MaskSplines.html -->

<a id="masksplines-bpy-prop-collection"></a>

# MaskSplines(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.MaskSplines"></a>

### class bpy.types.MaskSplines(bpy_prop_collection)

Collection of masking splines

<a id="bpy.types.MaskSplines.active"></a>

#### bpy.types.MaskSplines.active

Active spline of masking layer

**Type:**

[`MaskSpline`](bpy.types.MaskSpline.md#bpy.types.MaskSpline "bpy.types.MaskSpline") | None

<a id="bpy.types.MaskSplines.active_point"></a>

#### bpy.types.MaskSplines.active_point

Active point of masking layer

**Type:**

[`MaskSplinePoint`](bpy.types.MaskSplinePoint.md#bpy.types.MaskSplinePoint "bpy.types.MaskSplinePoint") | None

<a id="bpy.types.MaskSplines.new"></a>

#### bpy.types.MaskSplines.new()

Add a new spline to the layer

**Returns:**

The newly created spline

**Return type:**

[`MaskSpline`](bpy.types.MaskSpline.md#bpy.types.MaskSpline "bpy.types.MaskSpline")

<a id="bpy.types.MaskSplines.remove"></a>

#### bpy.types.MaskSplines.remove(spline)

Remove a spline from a layer

**Parameters:**

**spline** ([`MaskSpline`](bpy.types.MaskSpline.md#bpy.types.MaskSpline "bpy.types.MaskSpline") | None) – The spline to remove (never None)

<a id="bpy.types.MaskSplines.bl_rna_get_subclass"></a>

#### classmethod bpy.types.MaskSplines.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.MaskSplines.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.MaskSplines.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`MaskLayer.splines`](bpy.types.MaskLayer.md#bpy.types.MaskLayer.splines "bpy.types.MaskLayer.splines") |  |
