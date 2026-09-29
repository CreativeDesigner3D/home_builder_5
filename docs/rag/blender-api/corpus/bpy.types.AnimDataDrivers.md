<!-- source: Blender Python API reference 5.2 / bpy.types.AnimDataDrivers.html -->

<a id="animdatadrivers-bpy-prop-collection"></a>

# AnimDataDrivers(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.AnimDataDrivers"></a>

### class bpy.types.AnimDataDrivers(bpy_prop_collection)

Collection of Driver F-Curves

<a id="bpy.types.AnimDataDrivers.new"></a>

#### bpy.types.AnimDataDrivers.new(data_path, *, index=0)

new

**Parameters:**

- **data_path** (str) – Data Path, F-Curve data path to use (never None)
- **index** (int) – Index, Array index (in [0, inf], optional)

**Returns:**

Newly Driver F-Curve

**Return type:**

[`FCurve`](bpy.types.FCurve.md#bpy.types.FCurve "bpy.types.FCurve")

<a id="bpy.types.AnimDataDrivers.remove"></a>

#### bpy.types.AnimDataDrivers.remove(driver)

remove

**Parameters:**

**driver** ([`FCurve`](bpy.types.FCurve.md#bpy.types.FCurve "bpy.types.FCurve") | None) – (never None)

<a id="bpy.types.AnimDataDrivers.from_existing"></a>

#### bpy.types.AnimDataDrivers.from_existing(*, src_driver=None)

Add a new driver given an existing one

**Parameters:**

**src_driver** ([`FCurve`](bpy.types.FCurve.md#bpy.types.FCurve "bpy.types.FCurve") | None) – Existing Driver F-Curve to use as template for a new one (optional)

**Returns:**

New Driver F-Curve

**Return type:**

[`FCurve`](bpy.types.FCurve.md#bpy.types.FCurve "bpy.types.FCurve")

<a id="bpy.types.AnimDataDrivers.find"></a>

#### bpy.types.AnimDataDrivers.find(data_path, *, index=0)

Find a driver F-Curve. Note that this function performs a linear scan of all driver F-Curves.

**Parameters:**

- **data_path** (str) – Data Path, F-Curve data path (never None)
- **index** (int) – Index, Array index (in [0, inf], optional)

**Returns:**

The found F-Curve, or None if it doesn’t exist

**Return type:**

[`FCurve`](bpy.types.FCurve.md#bpy.types.FCurve "bpy.types.FCurve")

<a id="bpy.types.AnimDataDrivers.bl_rna_get_subclass"></a>

#### classmethod bpy.types.AnimDataDrivers.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.AnimDataDrivers.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.AnimDataDrivers.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`AnimData.drivers`](bpy.types.AnimData.md#bpy.types.AnimData.drivers "bpy.types.AnimData.drivers") |  |
