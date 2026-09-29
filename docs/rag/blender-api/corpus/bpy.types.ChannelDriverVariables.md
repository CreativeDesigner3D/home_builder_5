<!-- source: Blender Python API reference 5.2 / bpy.types.ChannelDriverVariables.html -->

<a id="channeldrivervariables-bpy-prop-collection"></a>

# ChannelDriverVariables(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.ChannelDriverVariables"></a>

### class bpy.types.ChannelDriverVariables(bpy_prop_collection)

Collection of channel driver Variables

<a id="bpy.types.ChannelDriverVariables.new"></a>

#### bpy.types.ChannelDriverVariables.new()

Add a new variable for the driver

**Returns:**

Newly created Driver Variable

**Return type:**

[`DriverVariable`](bpy.types.DriverVariable.md#bpy.types.DriverVariable "bpy.types.DriverVariable")

<a id="bpy.types.ChannelDriverVariables.remove"></a>

#### bpy.types.ChannelDriverVariables.remove(variable)

Remove an existing variable from the driver

**Parameters:**

**variable** ([`DriverVariable`](bpy.types.DriverVariable.md#bpy.types.DriverVariable "bpy.types.DriverVariable") | None) – Variable to remove from the driver (never None)

<a id="bpy.types.ChannelDriverVariables.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ChannelDriverVariables.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ChannelDriverVariables.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ChannelDriverVariables.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Driver.variables`](bpy.types.Driver.md#bpy.types.Driver.variables "bpy.types.Driver.variables") |  |
