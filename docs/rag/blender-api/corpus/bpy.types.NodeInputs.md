<!-- source: Blender Python API reference 5.2 / bpy.types.NodeInputs.html -->

<a id="nodeinputs-bpy-prop-collection"></a>

# NodeInputs(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.NodeInputs"></a>

### class bpy.types.NodeInputs(bpy_prop_collection)

Collection of Node Sockets

<a id="bpy.types.NodeInputs.new"></a>

#### bpy.types.NodeInputs.new(type, name, *, identifier='', use_multi_input=False)

Add a socket to this node

**Parameters:**

- **type** (str) – Type, Data type (never None)
- **name** (str) – Name, (never None)
- **identifier** (str) – Identifier, Unique socket identifier (optional, never None)
- **use_multi_input** (bool) – Make the socket multi-input (valid for inputs only) (optional)

**Returns:**

New socket

**Return type:**

[`NodeSocket`](bpy.types.NodeSocket.md#bpy.types.NodeSocket "bpy.types.NodeSocket")

<a id="bpy.types.NodeInputs.remove"></a>

#### bpy.types.NodeInputs.remove(socket)

Remove a socket from this node

**Parameters:**

**socket** ([`NodeSocket`](bpy.types.NodeSocket.md#bpy.types.NodeSocket "bpy.types.NodeSocket") | None) – The socket to remove

<a id="bpy.types.NodeInputs.clear"></a>

#### bpy.types.NodeInputs.clear()

Remove all sockets from this node

<a id="bpy.types.NodeInputs.move"></a>

#### bpy.types.NodeInputs.move(from_index, to_index)

Move a socket to another position

**Parameters:**

- **from_index** (int) – From Index, Index of the socket to move (in [0, inf])
- **to_index** (int) – To Index, Target index for the socket (in [0, inf])

<a id="bpy.types.NodeInputs.bl_rna_get_subclass"></a>

#### classmethod bpy.types.NodeInputs.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.NodeInputs.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.NodeInputs.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Node.inputs`](bpy.types.Node.md#bpy.types.Node.inputs "bpy.types.Node.inputs") |  |
