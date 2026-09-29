<!-- source: Blender Python API reference 5.2 / bpy.types.CompositorNodeTree.html -->

<a id="compositornodetree-nodetree"></a>

# CompositorNodeTree(NodeTree)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID"), [`NodeTree`](bpy.types.NodeTree.md#bpy.types.NodeTree "bpy.types.NodeTree")

<a id="bpy.types.CompositorNodeTree"></a>

### class bpy.types.CompositorNodeTree(NodeTree)

Node tree consisting of linked nodes used for compositing

<a id="bpy.types.CompositorNodeTree.is_strip_modifier"></a>

#### bpy.types.CompositorNodeTree.is_strip_modifier

The node group is used as a sequencer strip modifier (default False)

**Type:**

bool

<a id="bpy.types.CompositorNodeTree.use_viewer_border"></a>

#### bpy.types.CompositorNodeTree.use_viewer_border

Unused but kept for compatibility reasons. Use boundaries for viewer nodes and composite backdrop (default False)

**Type:**

bool

<a id="bpy.types.CompositorNodeTree.bl_rna_get_subclass"></a>

#### classmethod bpy.types.CompositorNodeTree.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.CompositorNodeTree.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.CompositorNodeTree.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, ID.name, ID.name_full, ID.id_type, ID.session_uid, ID.is_evaluated, ID.original, ID.users, ID.use_fake_user, ID.use_extra_user, ID.is_embedded_data, ID.is_linked_packed, ID.is_missing, ID.is_runtime_data, ID.is_editable, ID.tag, ID.is_library_indirect, ID.library, ID.library_weak_reference, ID.asset_data, ID.override_library, ID.preview, NodeTree.color_tag, NodeTree.default_group_node_width, NodeTree.view_center, NodeTree.description, NodeTree.animation_data, NodeTree.nodes, NodeTree.links, NodeTree.annotation, NodeTree.type, NodeTree.interface, NodeTree.bl_idname, NodeTree.bl_label, NodeTree.bl_description, NodeTree.bl_icon, NodeTree.bl_use_group_interface

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, ID.bl_system_properties_get, ID.rename, ID.evaluated_get, ID.copy, ID.asset_mark, ID.asset_clear, ID.asset_generate_preview, ID.override_create, ID.override_hierarchy_create, ID.user_clear, ID.user_remap, ID.make_local, ID.user_of_id, ID.animation_data_create, ID.animation_data_clear, ID.update_tag, ID.preview_ensure, ID.bl_rna_get_subclass, ID.bl_rna_get_subclass_py, NodeTree.interface_update, NodeTree.contains_tree, NodeTree.poll, NodeTree.update, NodeTree.get_from_context, NodeTree.valid_socket_type, NodeTree.debug_lazy_function_graph, NodeTree.bl_rna_get_subclass, NodeTree.bl_rna_get_subclass_py
