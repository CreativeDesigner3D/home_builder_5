<!-- source: Blender Python API reference 5.2 / bpy.types.GeometryNodeTree.html -->

<a id="geometrynodetree-nodetree"></a>

# GeometryNodeTree(NodeTree)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID"), [`NodeTree`](bpy.types.NodeTree.md#bpy.types.NodeTree "bpy.types.NodeTree")

<a id="bpy.types.GeometryNodeTree"></a>

### class bpy.types.GeometryNodeTree(NodeTree)

Node tree consisting of linked nodes used for geometries

<a id="bpy.types.GeometryNodeTree.is_mode_edit"></a>

#### bpy.types.GeometryNodeTree.is_mode_edit

The node group is used in edit mode (default False)

**Type:**

bool

<a id="bpy.types.GeometryNodeTree.is_mode_object"></a>

#### bpy.types.GeometryNodeTree.is_mode_object

The node group is used in object mode (default False)

**Type:**

bool

<a id="bpy.types.GeometryNodeTree.is_mode_paint"></a>

#### bpy.types.GeometryNodeTree.is_mode_paint

The node group is used in paint mode (default False)

**Type:**

bool

<a id="bpy.types.GeometryNodeTree.is_mode_sculpt"></a>

#### bpy.types.GeometryNodeTree.is_mode_sculpt

The node group is used in sculpt mode (default False)

**Type:**

bool

<a id="bpy.types.GeometryNodeTree.is_modifier"></a>

#### bpy.types.GeometryNodeTree.is_modifier

The node group is used as a geometry modifier (default False)

**Type:**

bool

<a id="bpy.types.GeometryNodeTree.is_tool"></a>

#### bpy.types.GeometryNodeTree.is_tool

The node group is used as a tool (default False)

**Type:**

bool

<a id="bpy.types.GeometryNodeTree.is_type_curve"></a>

#### bpy.types.GeometryNodeTree.is_type_curve

The node group is used for curves (default False)

**Type:**

bool

<a id="bpy.types.GeometryNodeTree.is_type_grease_pencil"></a>

#### bpy.types.GeometryNodeTree.is_type_grease_pencil

The node group is used for Grease Pencil (default False)

**Type:**

bool

<a id="bpy.types.GeometryNodeTree.is_type_mesh"></a>

#### bpy.types.GeometryNodeTree.is_type_mesh

The node group is used for meshes (default False)

**Type:**

bool

<a id="bpy.types.GeometryNodeTree.is_type_pointcloud"></a>

#### bpy.types.GeometryNodeTree.is_type_pointcloud

The node group is used for point clouds (default False)

**Type:**

bool

<a id="bpy.types.GeometryNodeTree.node_tool_idname"></a>

#### bpy.types.GeometryNodeTree.node_tool_idname

Unique operator identifier for the node tool (default “”, never None)

**Type:**

str

<a id="bpy.types.GeometryNodeTree.show_modifier_manage_panel"></a>

#### bpy.types.GeometryNodeTree.show_modifier_manage_panel

Turn on the option to display the manage panel when creating a modifier (default True)

**Type:**

bool

<a id="bpy.types.GeometryNodeTree.use_wait_for_click"></a>

#### bpy.types.GeometryNodeTree.use_wait_for_click

Wait for mouse click input before running the operator from a menu (default False)

**Type:**

bool

<a id="bpy.types.GeometryNodeTree.bl_rna_get_subclass"></a>

#### classmethod bpy.types.GeometryNodeTree.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.GeometryNodeTree.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.GeometryNodeTree.bl_rna_get_subclass_py(id, default=None, /)

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
