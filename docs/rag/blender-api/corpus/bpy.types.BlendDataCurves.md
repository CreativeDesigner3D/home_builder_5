<!-- source: Blender Python API reference 5.2 / bpy.types.BlendDataCurves.html -->

<a id="blenddatacurves-bpy-prop-collection"></a>

# BlendDataCurves(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.BlendDataCurves"></a>

### class bpy.types.BlendDataCurves(bpy_prop_collection)

Collection of curves

<a id="bpy.types.BlendDataCurves.new"></a>

#### bpy.types.BlendDataCurves.new(name, type)

Add a new curve to the main database

**Parameters:**

- **name** (str) – New name for the data-block (never None)
- **type** (Literal[[Object Type Curve Items](bpy_types_enum_items/object_type_curve_items.md#rna-enum-object-type-curve-items)]) – Type, The type of curve to add

**Returns:**

New curve data-block

**Return type:**

[`Curve`](bpy.types.Curve.md#bpy.types.Curve "bpy.types.Curve")

<a id="bpy.types.BlendDataCurves.remove"></a>

#### bpy.types.BlendDataCurves.remove(curve, *, do_unlink=True, do_id_user=True, do_ui_user=True)

Remove a curve from the current blendfile

**Parameters:**

- **curve** ([`Curve`](bpy.types.Curve.md#bpy.types.Curve "bpy.types.Curve") | None) – Curve to remove (never None)
- **do_unlink** (bool) – Unlink all usages of this curve before deleting it (WARNING: will also delete objects instancing that curve data) (optional)
- **do_id_user** (bool) – Decrement user counter of all data-blocks used by this curve data (optional)
- **do_ui_user** (bool) – Make sure interface does not reference this curve data (optional)

<a id="bpy.types.BlendDataCurves.tag"></a>

#### bpy.types.BlendDataCurves.tag(value)

tag

**Parameters:**

**value** (bool) – Value

<a id="bpy.types.BlendDataCurves.bl_rna_get_subclass"></a>

#### classmethod bpy.types.BlendDataCurves.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.BlendDataCurves.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.BlendDataCurves.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`BlendData.curves`](bpy.types.BlendData.md#bpy.types.BlendData.curves "bpy.types.BlendData.curves") |  |
