<!-- source: Blender Python API reference 5.2 / bpy.types.CurveProfilePoints.html -->

<a id="curveprofilepoints-bpy-prop-collection"></a>

# CurveProfilePoints(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.CurveProfilePoints"></a>

### class bpy.types.CurveProfilePoints(bpy_prop_collection)

Collection of Profile Points

<a id="bpy.types.CurveProfilePoints.add"></a>

#### bpy.types.CurveProfilePoints.add(x, y)

Add point to the profile

**Parameters:**

- **x** (float) – X Position, X Position for new point (in [-inf, inf])
- **y** (float) – Y Position, Y Position for new point (in [-inf, inf])

**Returns:**

New point

**Return type:**

[`CurveProfilePoint`](bpy.types.CurveProfilePoint.md#bpy.types.CurveProfilePoint "bpy.types.CurveProfilePoint")

<a id="bpy.types.CurveProfilePoints.remove"></a>

#### bpy.types.CurveProfilePoints.remove(point)

Delete point from the profile

**Parameters:**

**point** ([`CurveProfilePoint`](bpy.types.CurveProfilePoint.md#bpy.types.CurveProfilePoint "bpy.types.CurveProfilePoint") | None) – Point to remove (never None)

<a id="bpy.types.CurveProfilePoints.bl_rna_get_subclass"></a>

#### classmethod bpy.types.CurveProfilePoints.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.CurveProfilePoints.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.CurveProfilePoints.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`CurveProfile.points`](bpy.types.CurveProfile.md#bpy.types.CurveProfile.points "bpy.types.CurveProfile.points") |  |
