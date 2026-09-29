<!-- source: Blender Python API reference 5.2 / bpy.types.CurveMap.html -->

<a id="curvemap-bpy-struct"></a>

# CurveMap(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.CurveMap"></a>

### class bpy.types.CurveMap(bpy_struct)

Curve in a curve mapping

<a id="bpy.types.CurveMap.points"></a>

#### bpy.types.CurveMap.points

(default None, readonly)

**Type:**

[`CurveMapPoints`](bpy.types.CurveMapPoints.md#bpy.types.CurveMapPoints "bpy.types.CurveMapPoints")[[`CurveMapPoint`](bpy.types.CurveMapPoint.md#bpy.types.CurveMapPoint "bpy.types.CurveMapPoint")]

<a id="bpy.types.CurveMap.bl_rna_get_subclass"></a>

#### classmethod bpy.types.CurveMap.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.CurveMap.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.CurveMap.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`CurveMapping.curves`](bpy.types.CurveMapping.md#bpy.types.CurveMapping.curves "bpy.types.CurveMapping.curves") | - [`CurveMapping.evaluate`](bpy.types.CurveMapping.md#bpy.types.CurveMapping.evaluate "bpy.types.CurveMapping.evaluate") |
