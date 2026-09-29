<!-- source: Blender Python API reference 5.2 / bpy.types.NodeTreeInterfaceSocketSound.html -->

<a id="nodetreeinterfacesocketsound-nodetreeinterfacesocket"></a>

# NodeTreeInterfaceSocketSound(NodeTreeInterfaceSocket)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`NodeTreeInterfaceItem`](bpy.types.NodeTreeInterfaceItem.md#bpy.types.NodeTreeInterfaceItem "bpy.types.NodeTreeInterfaceItem"), [`NodeTreeInterfaceSocket`](bpy.types.NodeTreeInterfaceSocket.md#bpy.types.NodeTreeInterfaceSocket "bpy.types.NodeTreeInterfaceSocket")

<a id="bpy.types.NodeTreeInterfaceSocketSound"></a>

### class bpy.types.NodeTreeInterfaceSocketSound(NodeTreeInterfaceSocket)

Sound socket of a node

<a id="bpy.types.NodeTreeInterfaceSocketSound.default_value"></a>

#### bpy.types.NodeTreeInterfaceSocketSound.default_value

Input value used for unconnected socket

**Type:**

[`Sound`](bpy.types.Sound.md#bpy.types.Sound "bpy.types.Sound") | None

<a id="bpy.types.NodeTreeInterfaceSocketSound.bl_rna_get_subclass"></a>

#### classmethod bpy.types.NodeTreeInterfaceSocketSound.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.NodeTreeInterfaceSocketSound.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.NodeTreeInterfaceSocketSound.bl_rna_get_subclass_py(id, default=None, /)

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
