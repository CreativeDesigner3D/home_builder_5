<!-- source: Blender Python API reference 5.2 / bpy.types.NodeTreeInterfaceItem.html -->

<a id="nodetreeinterfaceitem-bpy-struct"></a>

# NodeTreeInterfaceItem(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

Subclasses

- [NodeTreeInterfacePanel(NodeTreeInterfaceItem)](bpy.types.NodeTreeInterfacePanel.md)
- [NodeTreeInterfaceSocket(NodeTreeInterfaceItem)](bpy.types.NodeTreeInterfaceSocket.md)

<a id="bpy.types.NodeTreeInterfaceItem"></a>

### class bpy.types.NodeTreeInterfaceItem(bpy_struct)

Item in a node tree interface

<a id="bpy.types.NodeTreeInterfaceItem.index"></a>

#### bpy.types.NodeTreeInterfaceItem.index

Global index of the item among all items in the interface (in [-1, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.NodeTreeInterfaceItem.item_type"></a>

#### bpy.types.NodeTreeInterfaceItem.item_type

Type of interface item (default `'PANEL'`, readonly)

**Type:**

Literal[[Node Tree Interface Item Type Items](bpy_types_enum_items/node_tree_interface_item_type_items.md#rna-enum-node-tree-interface-item-type-items)]

<a id="bpy.types.NodeTreeInterfaceItem.parent"></a>

#### bpy.types.NodeTreeInterfaceItem.parent

Panel that contains the item (readonly)

**Type:**

[`NodeTreeInterfacePanel`](bpy.types.NodeTreeInterfacePanel.md#bpy.types.NodeTreeInterfacePanel "bpy.types.NodeTreeInterfacePanel") | None

<a id="bpy.types.NodeTreeInterfaceItem.position"></a>

#### bpy.types.NodeTreeInterfaceItem.position

Position of the item in its parent panel (in [-1, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.NodeTreeInterfaceItem.bl_rna_get_subclass"></a>

#### classmethod bpy.types.NodeTreeInterfaceItem.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.NodeTreeInterfaceItem.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.NodeTreeInterfaceItem.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`NodeTreeInterface.active`](bpy.types.NodeTreeInterface.md#bpy.types.NodeTreeInterface.active "bpy.types.NodeTreeInterface.active") - [`NodeTreeInterface.copy`](bpy.types.NodeTreeInterface.md#bpy.types.NodeTreeInterface.copy "bpy.types.NodeTreeInterface.copy") - [`NodeTreeInterface.copy`](bpy.types.NodeTreeInterface.md#bpy.types.NodeTreeInterface.copy "bpy.types.NodeTreeInterface.copy") - [`NodeTreeInterface.items_tree`](bpy.types.NodeTreeInterface.md#bpy.types.NodeTreeInterface.items_tree "bpy.types.NodeTreeInterface.items_tree") | - [`NodeTreeInterface.move`](bpy.types.NodeTreeInterface.md#bpy.types.NodeTreeInterface.move "bpy.types.NodeTreeInterface.move") - [`NodeTreeInterface.move_to_parent`](bpy.types.NodeTreeInterface.md#bpy.types.NodeTreeInterface.move_to_parent "bpy.types.NodeTreeInterface.move_to_parent") - [`NodeTreeInterface.remove`](bpy.types.NodeTreeInterface.md#bpy.types.NodeTreeInterface.remove "bpy.types.NodeTreeInterface.remove") - [`NodeTreeInterfacePanel.interface_items`](bpy.types.NodeTreeInterfacePanel.md#bpy.types.NodeTreeInterfacePanel.interface_items "bpy.types.NodeTreeInterfacePanel.interface_items") |
