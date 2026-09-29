<!-- source: Blender Python API reference 5.2 / bpy.types.TextureNode.html -->

<a id="texturenode-nodeinternal"></a>

# TextureNode(NodeInternal)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Node`](bpy.types.Node.md#bpy.types.Node "bpy.types.Node"), [`NodeInternal`](bpy.types.NodeInternal.md#bpy.types.NodeInternal "bpy.types.NodeInternal")

Subclasses

- [TextureNodeAt(TextureNode)](bpy.types.TextureNodeAt.md)
- [TextureNodeBricks(TextureNode)](bpy.types.TextureNodeBricks.md)
- [TextureNodeChecker(TextureNode)](bpy.types.TextureNodeChecker.md)
- [TextureNodeCombineColor(TextureNode)](bpy.types.TextureNodeCombineColor.md)
- [TextureNodeCompose(TextureNode)](bpy.types.TextureNodeCompose.md)
- [TextureNodeCoordinates(TextureNode)](bpy.types.TextureNodeCoordinates.md)
- [TextureNodeCurveRGB(TextureNode)](bpy.types.TextureNodeCurveRGB.md)
- [TextureNodeCurveTime(TextureNode)](bpy.types.TextureNodeCurveTime.md)
- [TextureNodeDecompose(TextureNode)](bpy.types.TextureNodeDecompose.md)
- [TextureNodeDistance(TextureNode)](bpy.types.TextureNodeDistance.md)
- [TextureNodeGroup(TextureNode)](bpy.types.TextureNodeGroup.md)
- [TextureNodeHueSaturation(TextureNode)](bpy.types.TextureNodeHueSaturation.md)
- [TextureNodeImage(TextureNode)](bpy.types.TextureNodeImage.md)
- [TextureNodeInvert(TextureNode)](bpy.types.TextureNodeInvert.md)
- [TextureNodeMath(TextureNode)](bpy.types.TextureNodeMath.md)
- [TextureNodeMixRGB(TextureNode)](bpy.types.TextureNodeMixRGB.md)
- [TextureNodeOutput(TextureNode)](bpy.types.TextureNodeOutput.md)
- [TextureNodeRGBToBW(TextureNode)](bpy.types.TextureNodeRGBToBW.md)
- [TextureNodeRotate(TextureNode)](bpy.types.TextureNodeRotate.md)
- [TextureNodeScale(TextureNode)](bpy.types.TextureNodeScale.md)
- [TextureNodeSeparateColor(TextureNode)](bpy.types.TextureNodeSeparateColor.md)
- [TextureNodeTexBlend(TextureNode)](bpy.types.TextureNodeTexBlend.md)
- [TextureNodeTexClouds(TextureNode)](bpy.types.TextureNodeTexClouds.md)
- [TextureNodeTexDistNoise(TextureNode)](bpy.types.TextureNodeTexDistNoise.md)
- [TextureNodeTexMagic(TextureNode)](bpy.types.TextureNodeTexMagic.md)
- [TextureNodeTexMarble(TextureNode)](bpy.types.TextureNodeTexMarble.md)
- [TextureNodeTexMusgrave(TextureNode)](bpy.types.TextureNodeTexMusgrave.md)
- [TextureNodeTexNoise(TextureNode)](bpy.types.TextureNodeTexNoise.md)
- [TextureNodeTexStucci(TextureNode)](bpy.types.TextureNodeTexStucci.md)
- [TextureNodeTexVoronoi(TextureNode)](bpy.types.TextureNodeTexVoronoi.md)
- [TextureNodeTexWood(TextureNode)](bpy.types.TextureNodeTexWood.md)
- [TextureNodeTexture(TextureNode)](bpy.types.TextureNodeTexture.md)
- [TextureNodeTranslate(TextureNode)](bpy.types.TextureNodeTranslate.md)
- [TextureNodeValToNor(TextureNode)](bpy.types.TextureNodeValToNor.md)
- [TextureNodeValToRGB(TextureNode)](bpy.types.TextureNodeValToRGB.md)
- [TextureNodeViewer(TextureNode)](bpy.types.TextureNodeViewer.md)

<a id="bpy.types.TextureNode"></a>

### class bpy.types.TextureNode(NodeInternal)

<a id="bpy.types.TextureNode.bl_rna_get_subclass"></a>

#### classmethod bpy.types.TextureNode.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.TextureNode.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.TextureNode.bl_rna_get_subclass_py(id, default=None, /)

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

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, Node.bl_system_properties_get, Node.socket_value_update, Node.is_registered_node_type, Node.poll, Node.poll_instance, Node.update, Node.insert_link, Node.init, Node.copy, Node.free, Node.draw_buttons, Node.draw_buttons_ext, Node.draw_label, Node.debug_zone_body_lazy_function_graph, Node.debug_zone_lazy_function_graph, Node.bl_rna_get_subclass, Node.bl_rna_get_subclass_py, NodeInternal.poll, NodeInternal.poll_instance, NodeInternal.update, NodeInternal.draw_buttons, NodeInternal.draw_buttons_ext, NodeInternal.bl_rna_get_subclass, NodeInternal.bl_rna_get_subclass_py
