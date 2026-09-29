<!-- source: Blender Python API reference 5.2 / bpy.types.NodeTreeInterface.html -->

<a id="nodetreeinterface-bpy-struct"></a>

# NodeTreeInterface(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.NodeTreeInterface"></a>

### class bpy.types.NodeTreeInterface(bpy_struct)

Declaration of sockets and ui panels of a node group

<a id="bpy.types.NodeTreeInterface.active"></a>

#### bpy.types.NodeTreeInterface.active

Active item

**Type:**

[`NodeTreeInterfaceItem`](bpy.types.NodeTreeInterfaceItem.md#bpy.types.NodeTreeInterfaceItem "bpy.types.NodeTreeInterfaceItem") | None

<a id="bpy.types.NodeTreeInterface.active_index"></a>

#### bpy.types.NodeTreeInterface.active_index

Index of the active item (in [0, inf], default 0)

**Type:**

int

<a id="bpy.types.NodeTreeInterface.items_tree"></a>

#### bpy.types.NodeTreeInterface.items_tree

Items in the node interface (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`NodeTreeInterfaceItem`](bpy.types.NodeTreeInterfaceItem.md#bpy.types.NodeTreeInterfaceItem "bpy.types.NodeTreeInterfaceItem")]

<a id="bpy.types.NodeTreeInterface.new_socket"></a>

#### bpy.types.NodeTreeInterface.new_socket(name, *, description='', in_out='INPUT', socket_type='DEFAULT', parent=None)

Add a new socket to the interface

**Parameters:**

- **name** (str) – Name, Name of the socket (never None)
- **description** (str) – Description, Description of the socket (optional, never None)
- **in_out** (Literal['INPUT', 'OUTPUT']) –

  Input/Output Type, Create an input or output socket (optional)

  - `INPUT`
    Input – Generate a input node socket.
  - `OUTPUT`
    Output – Generate a output node socket.
- **socket_type** (Literal['DEFAULT']) – Socket Type, Type of socket generated on nodes (optional)
- **parent** ([`NodeTreeInterfacePanel`](bpy.types.NodeTreeInterfacePanel.md#bpy.types.NodeTreeInterfacePanel "bpy.types.NodeTreeInterfacePanel") | None) – Parent, Panel to add the socket in (optional)

**Returns:**

Socket, New socket

**Return type:**

[`NodeTreeInterfaceSocket`](bpy.types.NodeTreeInterfaceSocket.md#bpy.types.NodeTreeInterfaceSocket "bpy.types.NodeTreeInterfaceSocket")

<a id="bpy.types.NodeTreeInterface.new_panel"></a>

#### bpy.types.NodeTreeInterface.new_panel(name, *, description='', default_closed=False)

Add a new panel to the interface

**Parameters:**

- **name** (str) – Name, Name of the new panel (never None)
- **description** (str) – Description, Description of the panel (optional, never None)
- **default_closed** (bool) – Default Closed, Panel is closed by default on new nodes (optional)

**Returns:**

Panel, New panel

**Return type:**

[`NodeTreeInterfacePanel`](bpy.types.NodeTreeInterfacePanel.md#bpy.types.NodeTreeInterfacePanel "bpy.types.NodeTreeInterfacePanel")

<a id="bpy.types.NodeTreeInterface.copy"></a>

#### bpy.types.NodeTreeInterface.copy(item)

Add a copy of an item to the interface

**Parameters:**

**item** ([`NodeTreeInterfaceItem`](bpy.types.NodeTreeInterfaceItem.md#bpy.types.NodeTreeInterfaceItem "bpy.types.NodeTreeInterfaceItem") | None) – Item, Item to copy (never None)

**Returns:**

Item Copy, Copy of the item

**Return type:**

[`NodeTreeInterfaceItem`](bpy.types.NodeTreeInterfaceItem.md#bpy.types.NodeTreeInterfaceItem "bpy.types.NodeTreeInterfaceItem")

<a id="bpy.types.NodeTreeInterface.remove"></a>

#### bpy.types.NodeTreeInterface.remove(item, *, move_content_to_parent=True)

Remove an item from the interface

**Parameters:**

- **item** ([`NodeTreeInterfaceItem`](bpy.types.NodeTreeInterfaceItem.md#bpy.types.NodeTreeInterfaceItem "bpy.types.NodeTreeInterfaceItem") | None) – Item, The item to remove (never None)
- **move_content_to_parent** (bool) – Move Content, If the item is a panel, move the contents to the parent instead of deleting it (optional)

<a id="bpy.types.NodeTreeInterface.clear"></a>

#### bpy.types.NodeTreeInterface.clear()

Remove all items from the interface

<a id="bpy.types.NodeTreeInterface.move"></a>

#### bpy.types.NodeTreeInterface.move(item, to_position)

Move an item to another position

**Parameters:**

- **item** ([`NodeTreeInterfaceItem`](bpy.types.NodeTreeInterfaceItem.md#bpy.types.NodeTreeInterfaceItem "bpy.types.NodeTreeInterfaceItem") | None) – Item, The item to move (never None)
- **to_position** (int) – To Position, Target position for the item in its current panel (in [0, inf])

<a id="bpy.types.NodeTreeInterface.move_to_parent"></a>

#### bpy.types.NodeTreeInterface.move_to_parent(item, parent, to_position)

Move an item to a new panel and/or position.

**Parameters:**

- **item** ([`NodeTreeInterfaceItem`](bpy.types.NodeTreeInterfaceItem.md#bpy.types.NodeTreeInterfaceItem "bpy.types.NodeTreeInterfaceItem") | None) – Item, The item to move (never None)
- **parent** ([`NodeTreeInterfacePanel`](bpy.types.NodeTreeInterfacePanel.md#bpy.types.NodeTreeInterfacePanel "bpy.types.NodeTreeInterfacePanel") | None) – Parent, New parent of the item
- **to_position** (int) – To Position, Target position for the item in the new parent panel (in [0, inf])

<a id="bpy.types.NodeTreeInterface.bl_rna_get_subclass"></a>

#### classmethod bpy.types.NodeTreeInterface.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.NodeTreeInterface.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.NodeTreeInterface.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`NodeTree.interface`](bpy.types.NodeTree.md#bpy.types.NodeTree.interface "bpy.types.NodeTree.interface") | - [`UILayout.template_node_tree_interface`](bpy.types.UILayout.md#bpy.types.UILayout.template_node_tree_interface "bpy.types.UILayout.template_node_tree_interface") |
