<!-- source: Blender Python API reference 5.2 / bpy.types.ActionChannelbagFCurves.html -->

<a id="actionchannelbagfcurves-bpy-prop-collection"></a>

# ActionChannelbagFCurves(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.ActionChannelbagFCurves"></a>

### class bpy.types.ActionChannelbagFCurves(bpy_prop_collection)

Collection of F-Curves for a specific action slot, on a specific strip

<a id="bpy.types.ActionChannelbagFCurves.new"></a>

#### bpy.types.ActionChannelbagFCurves.new(data_path, *, index=0, group_name='')

Add an F-Curve to the channelbag

**Parameters:**

- **data_path** (str) – Data Path, F-Curve data path to use (never None)
- **index** (int) – Index, Array index (in [0, inf], optional)
- **group_name** (str) – Group Name, Name of the Group for this F-Curve, will be created if it does not exist yet (optional, never None)

**Returns:**

Newly created F-Curve

**Return type:**

[`FCurve`](bpy.types.FCurve.md#bpy.types.FCurve "bpy.types.FCurve")

<a id="bpy.types.ActionChannelbagFCurves.new_from_fcurve"></a>

#### bpy.types.ActionChannelbagFCurves.new_from_fcurve(source, *, data_path='')

Copy an F-Curve into the channelbag. The original F-Curve is unchanged

**Parameters:**

- **source** ([`FCurve`](bpy.types.FCurve.md#bpy.types.FCurve "bpy.types.FCurve") | None) – Source F-Curve, The F-Curve to copy (never None)
- **data_path** (str) – Data Path, F-Curve data path to use. If not provided, this will use the same data path as the given F-Curve (optional, never None)

**Returns:**

Newly created F-Curve

**Return type:**

[`FCurve`](bpy.types.FCurve.md#bpy.types.FCurve "bpy.types.FCurve")

<a id="bpy.types.ActionChannelbagFCurves.ensure"></a>

#### bpy.types.ActionChannelbagFCurves.ensure(data_path, *, index=0, group_name='')

Returns the F-Curve if it already exists, and creates it if necessary

**Parameters:**

- **data_path** (str) – Data Path, F-Curve data path to use (never None)
- **index** (int) – Index, Array index (in [0, inf], optional)
- **group_name** (str) – Group Name, Name of the Group for this F-Curve, will be created if it does not exist yet. This parameter is ignored if the F-Curve already exists (optional, never None)

**Returns:**

Found or newly created F-Curve

**Return type:**

[`FCurve`](bpy.types.FCurve.md#bpy.types.FCurve "bpy.types.FCurve")

<a id="bpy.types.ActionChannelbagFCurves.find"></a>

#### bpy.types.ActionChannelbagFCurves.find(data_path, *, index=0)

Find an F-Curve. Note that this function performs a linear scan of all F-Curves in the channelbag.

**Parameters:**

- **data_path** (str) – Data Path, F-Curve data path (never None)
- **index** (int) – Index, Array index (in [0, inf], optional)

**Returns:**

The found F-Curve, or None if it does not exist

**Return type:**

[`FCurve`](bpy.types.FCurve.md#bpy.types.FCurve "bpy.types.FCurve")

<a id="bpy.types.ActionChannelbagFCurves.remove"></a>

#### bpy.types.ActionChannelbagFCurves.remove(fcurve)

Remove F-Curve

**Parameters:**

**fcurve** ([`FCurve`](bpy.types.FCurve.md#bpy.types.FCurve "bpy.types.FCurve") | None) – F-Curve to remove (never None)

<a id="bpy.types.ActionChannelbagFCurves.clear"></a>

#### bpy.types.ActionChannelbagFCurves.clear()

Remove all F-Curves from this channelbag

<a id="bpy.types.ActionChannelbagFCurves.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ActionChannelbagFCurves.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ActionChannelbagFCurves.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ActionChannelbagFCurves.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`ActionChannelbag.fcurves`](bpy.types.ActionChannelbag.md#bpy.types.ActionChannelbag.fcurves "bpy.types.ActionChannelbag.fcurves") |  |
