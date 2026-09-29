<!-- source: Blender Python API reference 5.2 / bpy.types.NodeCompositorFileOutputItems.html -->

<a id="nodecompositorfileoutputitems-bpy-prop-collection"></a>

# NodeCompositorFileOutputItems(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.NodeCompositorFileOutputItems"></a>

### class bpy.types.NodeCompositorFileOutputItems(bpy_prop_collection)

Collection of file output items

<a id="bpy.types.NodeCompositorFileOutputItems.new"></a>

#### bpy.types.NodeCompositorFileOutputItems.new(socket_type, name)

Add an item at the end

**Parameters:**

- **socket_type** (Literal[[Node Socket Data Type Items](bpy_types_enum_items/node_socket_data_type_items.md#rna-enum-node-socket-data-type-items)]) – Socket Type, Socket type of the item
- **name** (str) – Name, (never None)

**Returns:**

Item, New item

**Return type:**

[`NodeCompositorFileOutputItem`](bpy.types.NodeCompositorFileOutputItem.md#bpy.types.NodeCompositorFileOutputItem "bpy.types.NodeCompositorFileOutputItem")

<a id="bpy.types.NodeCompositorFileOutputItems.remove"></a>

#### bpy.types.NodeCompositorFileOutputItems.remove(item)

Remove an item

**Parameters:**

**item** ([`NodeCompositorFileOutputItem`](bpy.types.NodeCompositorFileOutputItem.md#bpy.types.NodeCompositorFileOutputItem "bpy.types.NodeCompositorFileOutputItem") | None) – Item, The item to remove (never None)

<a id="bpy.types.NodeCompositorFileOutputItems.clear"></a>

#### bpy.types.NodeCompositorFileOutputItems.clear()

Remove all items

<a id="bpy.types.NodeCompositorFileOutputItems.move"></a>

#### bpy.types.NodeCompositorFileOutputItems.move(from_index, to_index)

Move an item to another position

**Parameters:**

- **from_index** (int) – From Index, Index of the item to move (in [0, inf])
- **to_index** (int) – To Index, Target index for the item (in [0, inf])

<a id="bpy.types.NodeCompositorFileOutputItems.bl_rna_get_subclass"></a>

#### classmethod bpy.types.NodeCompositorFileOutputItems.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.NodeCompositorFileOutputItems.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.NodeCompositorFileOutputItems.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`CompositorNodeOutputFile.file_output_items`](bpy.types.CompositorNodeOutputFile.md#bpy.types.CompositorNodeOutputFile.file_output_items "bpy.types.CompositorNodeOutputFile.file_output_items") |  |
