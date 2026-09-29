<!-- source: Blender Python API reference 5.2 / bpy.types.NodeSocketMaterial.html -->

<a id="nodesocketmaterial-nodesocketstandard"></a>

# NodeSocketMaterial(NodeSocketStandard)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`NodeSocket`](bpy.types.NodeSocket.md#bpy.types.NodeSocket "bpy.types.NodeSocket"), [`NodeSocketStandard`](bpy.types.NodeSocketStandard.md#bpy.types.NodeSocketStandard "bpy.types.NodeSocketStandard")

<a id="bpy.types.NodeSocketMaterial"></a>

### class bpy.types.NodeSocketMaterial(NodeSocketStandard)

Material socket of a node

<a id="bpy.types.NodeSocketMaterial.default_value"></a>

#### bpy.types.NodeSocketMaterial.default_value

**Type:**

[`Material`](bpy.types.Material.md#bpy.types.Material "bpy.types.Material") | None

<a id="bpy.types.NodeSocketMaterial.links"></a>

#### bpy.types.NodeSocketMaterial.links

List of node links from or to this socket.

**Type:**

[`NodeLinks`](bpy.types.NodeLinks.md#bpy.types.NodeLinks "bpy.types.NodeLinks")

> **Note:**
>
> Takes `O(len(nodetree.links))` time.

(readonly)

<a id="bpy.types.NodeSocketMaterial.bl_rna_get_subclass"></a>

#### classmethod bpy.types.NodeSocketMaterial.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.NodeSocketMaterial.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.NodeSocketMaterial.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, NodeSocket.name, NodeSocket.label, NodeSocket.identifier, NodeSocket.description, NodeSocket.is_output, NodeSocket.select, NodeSocket.hide, NodeSocket.enabled, NodeSocket.link_limit, NodeSocket.is_linked, NodeSocket.is_unavailable, NodeSocket.is_multi_input, NodeSocket.show_expanded, NodeSocket.is_inactive, NodeSocket.is_icon_visible, NodeSocket.hide_value, NodeSocket.pin_gizmo, NodeSocket.node, NodeSocket.type, NodeSocket.display_shape, NodeSocket.inferred_structure_type, NodeSocket.bl_idname, NodeSocket.bl_label, NodeSocket.bl_subtype_label, NodeSocket.links, NodeSocketStandard.links

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, NodeSocket.bl_system_properties_get, NodeSocket.draw, NodeSocket.draw_color, NodeSocket.draw_color_simple, NodeSocket.bl_rna_get_subclass, NodeSocket.bl_rna_get_subclass_py, NodeSocketStandard.draw, NodeSocketStandard.draw_color, NodeSocketStandard.draw_color_simple, NodeSocketStandard.bl_rna_get_subclass, NodeSocketStandard.bl_rna_get_subclass_py
