<!-- source: Blender Python API reference 5.2 / bpy.types.NodeInternal.html -->

<a id="nodeinternal-node"></a>

# NodeInternal(Node)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Node`](bpy.types.Node.md#bpy.types.Node "bpy.types.Node")

Subclasses

- [CompositorNode(NodeInternal)](bpy.types.CompositorNode.md)
- [FunctionNode(NodeInternal)](bpy.types.FunctionNode.md)
- [GeometryNode(NodeInternal)](bpy.types.GeometryNode.md)
- [NodeClosureInput(NodeInternal)](bpy.types.NodeClosureInput.md)
- [NodeClosureOutput(NodeInternal)](bpy.types.NodeClosureOutput.md)
- [NodeCombineBundle(NodeInternal)](bpy.types.NodeCombineBundle.md)
- [NodeEnableOutput(NodeInternal)](bpy.types.NodeEnableOutput.md)
- [NodeEvaluateClosure(NodeInternal)](bpy.types.NodeEvaluateClosure.md)
- [NodeFrame(NodeInternal)](bpy.types.NodeFrame.md)
- [NodeGetBundleItem(NodeInternal)](bpy.types.NodeGetBundleItem.md)
- [NodeGetNestedBundlePaths(NodeInternal)](bpy.types.NodeGetNestedBundlePaths.md)
- [NodeGroup(NodeInternal)](bpy.types.NodeGroup.md)
- [NodeGroupInput(NodeInternal)](bpy.types.NodeGroupInput.md)
- [NodeGroupOutput(NodeInternal)](bpy.types.NodeGroupOutput.md)
- [NodeImplicitConversion(NodeInternal)](bpy.types.NodeImplicitConversion.md)
- [NodeJoinBundle(NodeInternal)](bpy.types.NodeJoinBundle.md)
- [NodeReroute(NodeInternal)](bpy.types.NodeReroute.md)
- [NodeSeparateBundle(NodeInternal)](bpy.types.NodeSeparateBundle.md)
- [NodeStoreBundleItem(NodeInternal)](bpy.types.NodeStoreBundleItem.md)
- [ShaderNode(NodeInternal)](bpy.types.ShaderNode.md)
- [TextureNode(NodeInternal)](bpy.types.TextureNode.md)

<a id="bpy.types.NodeInternal"></a>

### class bpy.types.NodeInternal(Node)

<a id="bpy.types.NodeInternal.poll"></a>

#### classmethod bpy.types.NodeInternal.poll(node_tree)

If non-null output is returned, the node type can be added to the tree

**Parameters:**

**node_tree** ([`NodeTree`](bpy.types.NodeTree.md#bpy.types.NodeTree "bpy.types.NodeTree") | None) – Node Tree

**Return type:**

bool

<a id="bpy.types.NodeInternal.poll_instance"></a>

#### bpy.types.NodeInternal.poll_instance(node_tree)

If non-null output is returned, the node can be added to the tree

**Parameters:**

**node_tree** ([`NodeTree`](bpy.types.NodeTree.md#bpy.types.NodeTree "bpy.types.NodeTree") | None) – Node Tree

**Return type:**

bool

<a id="bpy.types.NodeInternal.update"></a>

#### bpy.types.NodeInternal.update()

Update on node graph topology changes (adding or removing nodes and links)

<a id="bpy.types.NodeInternal.draw_buttons"></a>

#### bpy.types.NodeInternal.draw_buttons(context, layout)

Draw node buttons

**Parameters:**

- **context** ([`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context") | None) – (never None)
- **layout** ([`UILayout`](bpy.types.UILayout.md#bpy.types.UILayout "bpy.types.UILayout") | None) – Layout, Layout in the UI (never None)

<a id="bpy.types.NodeInternal.draw_buttons_ext"></a>

#### bpy.types.NodeInternal.draw_buttons_ext(context, layout)

Draw node buttons in the sidebar

**Parameters:**

- **context** ([`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context") | None) – (never None)
- **layout** ([`UILayout`](bpy.types.UILayout.md#bpy.types.UILayout "bpy.types.UILayout") | None) – Layout, Layout in the UI (never None)

<a id="bpy.types.NodeInternal.bl_rna_get_subclass"></a>

#### classmethod bpy.types.NodeInternal.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.NodeInternal.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.NodeInternal.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, Node.type, Node.location, Node.location_absolute, Node.width, Node.height, Node.dimensions, Node.name, Node.label, Node.inputs, Node.outputs, Node.panel_states, Node.internal_links, Node.parent, Node.warning_propagation, Node.use_custom_color, Node.color, Node.color_tag, Node.select, Node.show_options, Node.show_preview, Node.hide, Node.mute, Node.show_texture, Node.bl_idname, Node.bl_label, Node.bl_description, Node.bl_icon, Node.bl_static_type, Node.bl_width_default, Node.bl_width_min, Node.bl_width_max, Node.bl_height_default, Node.bl_height_min, Node.bl_height_max

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, Node.bl_system_properties_get, Node.socket_value_update, Node.is_registered_node_type, Node.poll, Node.poll_instance, Node.update, Node.insert_link, Node.init, Node.copy, Node.free, Node.draw_buttons, Node.draw_buttons_ext, Node.draw_label, Node.debug_zone_body_lazy_function_graph, Node.debug_zone_lazy_function_graph, Node.bl_rna_get_subclass, Node.bl_rna_get_subclass_py

<a id="references"></a>

## References

|  |  |
| --- | --- |
| - [`GeometryNodeForeachGeometryElementInput.pair_with_output`](bpy.types.GeometryNodeForeachGeometryElementInput.md#bpy.types.GeometryNodeForeachGeometryElementInput.pair_with_output "bpy.types.GeometryNodeForeachGeometryElementInput.pair_with_output") - [`GeometryNodeRepeatInput.pair_with_output`](bpy.types.GeometryNodeRepeatInput.md#bpy.types.GeometryNodeRepeatInput.pair_with_output "bpy.types.GeometryNodeRepeatInput.pair_with_output") | - [`GeometryNodeSimulationInput.pair_with_output`](bpy.types.GeometryNodeSimulationInput.md#bpy.types.GeometryNodeSimulationInput.pair_with_output "bpy.types.GeometryNodeSimulationInput.pair_with_output") - [`NodeClosureInput.pair_with_output`](bpy.types.NodeClosureInput.md#bpy.types.NodeClosureInput.pair_with_output "bpy.types.NodeClosureInput.pair_with_output") |
