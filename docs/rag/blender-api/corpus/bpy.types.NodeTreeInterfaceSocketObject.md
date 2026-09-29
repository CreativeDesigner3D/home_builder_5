<!-- source: Blender Python API reference 5.2 / bpy.types.NodeTreeInterfaceSocketObject.html -->

<a id="nodetreeinterfacesocketobject-nodetreeinterfacesocket"></a>

# NodeTreeInterfaceSocketObject(NodeTreeInterfaceSocket)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`NodeTreeInterfaceItem`](bpy.types.NodeTreeInterfaceItem.md#bpy.types.NodeTreeInterfaceItem "bpy.types.NodeTreeInterfaceItem"), [`NodeTreeInterfaceSocket`](bpy.types.NodeTreeInterfaceSocket.md#bpy.types.NodeTreeInterfaceSocket "bpy.types.NodeTreeInterfaceSocket")

<a id="bpy.types.NodeTreeInterfaceSocketObject"></a>

### class bpy.types.NodeTreeInterfaceSocketObject(NodeTreeInterfaceSocket)

Object socket of a node

<a id="bpy.types.NodeTreeInterfaceSocketObject.default_value"></a>

#### bpy.types.NodeTreeInterfaceSocketObject.default_value

Input value used for unconnected socket

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.NodeTreeInterfaceSocketObject.draw"></a>

#### bpy.types.NodeTreeInterfaceSocketObject.draw(context, layout)

Draw interface socket settings

**Parameters:**

- **context** ([`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context") | None) – (never None)
- **layout** ([`UILayout`](bpy.types.UILayout.md#bpy.types.UILayout "bpy.types.UILayout") | None) – Layout, Layout in the UI (never None)

<a id="bpy.types.NodeTreeInterfaceSocketObject.init_socket"></a>

#### bpy.types.NodeTreeInterfaceSocketObject.init_socket(node, socket, data_path)

Initialize a node socket instance

**Parameters:**

- **node** ([`Node`](bpy.types.Node.md#bpy.types.Node "bpy.types.Node") | None) – Node, Node of the socket to initialize (never None)
- **socket** ([`NodeSocket`](bpy.types.NodeSocket.md#bpy.types.NodeSocket "bpy.types.NodeSocket") | None) – Socket, Socket to initialize (never None)
- **data_path** (str) – Data Path, Path to specialized socket data (never None)

<a id="bpy.types.NodeTreeInterfaceSocketObject.from_socket"></a>

#### bpy.types.NodeTreeInterfaceSocketObject.from_socket(node, socket)

Setup template parameters from an existing socket

**Parameters:**

- **node** ([`Node`](bpy.types.Node.md#bpy.types.Node "bpy.types.Node") | None) – Node, Node of the original socket (never None)
- **socket** ([`NodeSocket`](bpy.types.NodeSocket.md#bpy.types.NodeSocket "bpy.types.NodeSocket") | None) – Socket, Original socket (never None)

<a id="bpy.types.NodeTreeInterfaceSocketObject.bl_rna_get_subclass"></a>

#### classmethod bpy.types.NodeTreeInterfaceSocketObject.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.NodeTreeInterfaceSocketObject.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.NodeTreeInterfaceSocketObject.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, NodeTreeInterfaceItem.item_type, NodeTreeInterfaceItem.parent, NodeTreeInterfaceItem.position, NodeTreeInterfaceItem.index, NodeTreeInterfaceSocket.name, NodeTreeInterfaceSocket.identifier, NodeTreeInterfaceSocket.description, NodeTreeInterfaceSocket.socket_type, NodeTreeInterfaceSocket.in_out, NodeTreeInterfaceSocket.hide_value, NodeTreeInterfaceSocket.hide_in_modifier, NodeTreeInterfaceSocket.force_non_field, NodeTreeInterfaceSocket.is_inspect_output, NodeTreeInterfaceSocket.is_panel_toggle, NodeTreeInterfaceSocket.layer_selection_field, NodeTreeInterfaceSocket.menu_expanded, NodeTreeInterfaceSocket.optional_label, NodeTreeInterfaceSocket.select, NodeTreeInterfaceSocket.attribute_domain, NodeTreeInterfaceSocket.default_attribute_name, NodeTreeInterfaceSocket.structure_type, NodeTreeInterfaceSocket.default_input, NodeTreeInterfaceSocket.bl_socket_idname

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, NodeTreeInterfaceItem.bl_rna_get_subclass, NodeTreeInterfaceItem.bl_rna_get_subclass_py, NodeTreeInterfaceSocket.bl_system_properties_get, NodeTreeInterfaceSocket.draw, NodeTreeInterfaceSocket.init_socket, NodeTreeInterfaceSocket.from_socket, NodeTreeInterfaceSocket.bl_rna_get_subclass, NodeTreeInterfaceSocket.bl_rna_get_subclass_py
