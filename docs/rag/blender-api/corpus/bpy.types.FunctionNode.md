<!-- source: Blender Python API reference 5.2 / bpy.types.FunctionNode.html -->

<a id="functionnode-nodeinternal"></a>

# FunctionNode(NodeInternal)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Node`](bpy.types.Node.md#bpy.types.Node "bpy.types.Node"), [`NodeInternal`](bpy.types.NodeInternal.md#bpy.types.NodeInternal "bpy.types.NodeInternal")

Subclasses

- [FunctionNodeAlignEulerToVector(FunctionNode)](bpy.types.FunctionNodeAlignEulerToVector.md)
- [FunctionNodeAlignRotationToVector(FunctionNode)](bpy.types.FunctionNodeAlignRotationToVector.md)
- [FunctionNodeAxesToRotation(FunctionNode)](bpy.types.FunctionNodeAxesToRotation.md)
- [FunctionNodeAxisAngleToRotation(FunctionNode)](bpy.types.FunctionNodeAxisAngleToRotation.md)
- [FunctionNodeBitMath(FunctionNode)](bpy.types.FunctionNodeBitMath.md)
- [FunctionNodeBooleanMath(FunctionNode)](bpy.types.FunctionNodeBooleanMath.md)
- [FunctionNodeCombineColor(FunctionNode)](bpy.types.FunctionNodeCombineColor.md)
- [FunctionNodeCombineMatrix(FunctionNode)](bpy.types.FunctionNodeCombineMatrix.md)
- [FunctionNodeCombineTransform(FunctionNode)](bpy.types.FunctionNodeCombineTransform.md)
- [FunctionNodeCompare(FunctionNode)](bpy.types.FunctionNodeCompare.md)
- [FunctionNodeEulerToRotation(FunctionNode)](bpy.types.FunctionNodeEulerToRotation.md)
- [FunctionNodeFindInString(FunctionNode)](bpy.types.FunctionNodeFindInString.md)
- [FunctionNodeFloatToInt(FunctionNode)](bpy.types.FunctionNodeFloatToInt.md)
- [FunctionNodeFormatString(FunctionNode)](bpy.types.FunctionNodeFormatString.md)
- [FunctionNodeHashValue(FunctionNode)](bpy.types.FunctionNodeHashValue.md)
- [FunctionNodeInputBool(FunctionNode)](bpy.types.FunctionNodeInputBool.md)
- [FunctionNodeInputColor(FunctionNode)](bpy.types.FunctionNodeInputColor.md)
- [FunctionNodeInputInt(FunctionNode)](bpy.types.FunctionNodeInputInt.md)
- [FunctionNodeInputIntVector(FunctionNode)](bpy.types.FunctionNodeInputIntVector.md)
- [FunctionNodeInputMenu(FunctionNode)](bpy.types.FunctionNodeInputMenu.md)
- [FunctionNodeInputRotation(FunctionNode)](bpy.types.FunctionNodeInputRotation.md)
- [FunctionNodeInputSpecialCharacters(FunctionNode)](bpy.types.FunctionNodeInputSpecialCharacters.md)
- [FunctionNodeInputString(FunctionNode)](bpy.types.FunctionNodeInputString.md)
- [FunctionNodeInputVector(FunctionNode)](bpy.types.FunctionNodeInputVector.md)
- [FunctionNodeIntegerMath(FunctionNode)](bpy.types.FunctionNodeIntegerMath.md)
- [FunctionNodeInvertMatrix(FunctionNode)](bpy.types.FunctionNodeInvertMatrix.md)
- [FunctionNodeInvertRotation(FunctionNode)](bpy.types.FunctionNodeInvertRotation.md)
- [FunctionNodeMatchString(FunctionNode)](bpy.types.FunctionNodeMatchString.md)
- [FunctionNodeMatrixDeterminant(FunctionNode)](bpy.types.FunctionNodeMatrixDeterminant.md)
- [FunctionNodeMatrixMultiply(FunctionNode)](bpy.types.FunctionNodeMatrixMultiply.md)
- [FunctionNodeMatrixSVD(FunctionNode)](bpy.types.FunctionNodeMatrixSVD.md)
- [FunctionNodeProjectPoint(FunctionNode)](bpy.types.FunctionNodeProjectPoint.md)
- [FunctionNodeQuaternionToRotation(FunctionNode)](bpy.types.FunctionNodeQuaternionToRotation.md)
- [FunctionNodeRandomValue(FunctionNode)](bpy.types.FunctionNodeRandomValue.md)
- [FunctionNodeReplaceString(FunctionNode)](bpy.types.FunctionNodeReplaceString.md)
- [FunctionNodeReverseString(FunctionNode)](bpy.types.FunctionNodeReverseString.md)
- [FunctionNodeRotateEuler(FunctionNode)](bpy.types.FunctionNodeRotateEuler.md)
- [FunctionNodeRotateRotation(FunctionNode)](bpy.types.FunctionNodeRotateRotation.md)
- [FunctionNodeRotateVector(FunctionNode)](bpy.types.FunctionNodeRotateVector.md)
- [FunctionNodeRotationToAxisAngle(FunctionNode)](bpy.types.FunctionNodeRotationToAxisAngle.md)
- [FunctionNodeRotationToEuler(FunctionNode)](bpy.types.FunctionNodeRotationToEuler.md)
- [FunctionNodeRotationToQuaternion(FunctionNode)](bpy.types.FunctionNodeRotationToQuaternion.md)
- [FunctionNodeSeparateColor(FunctionNode)](bpy.types.FunctionNodeSeparateColor.md)
- [FunctionNodeSeparateMatrix(FunctionNode)](bpy.types.FunctionNodeSeparateMatrix.md)
- [FunctionNodeSeparateTransform(FunctionNode)](bpy.types.FunctionNodeSeparateTransform.md)
- [FunctionNodeSetStringCase(FunctionNode)](bpy.types.FunctionNodeSetStringCase.md)
- [FunctionNodeSliceString(FunctionNode)](bpy.types.FunctionNodeSliceString.md)
- [FunctionNodeSplitString(FunctionNode)](bpy.types.FunctionNodeSplitString.md)
- [FunctionNodeStringLength(FunctionNode)](bpy.types.FunctionNodeStringLength.md)
- [FunctionNodeStringToValue(FunctionNode)](bpy.types.FunctionNodeStringToValue.md)
- [FunctionNodeTransformDirection(FunctionNode)](bpy.types.FunctionNodeTransformDirection.md)
- [FunctionNodeTransformPoint(FunctionNode)](bpy.types.FunctionNodeTransformPoint.md)
- [FunctionNodeTransposeMatrix(FunctionNode)](bpy.types.FunctionNodeTransposeMatrix.md)
- [FunctionNodeTrimString(FunctionNode)](bpy.types.FunctionNodeTrimString.md)
- [FunctionNodeValueToString(FunctionNode)](bpy.types.FunctionNodeValueToString.md)

<a id="bpy.types.FunctionNode"></a>

### class bpy.types.FunctionNode(NodeInternal)

<a id="bpy.types.FunctionNode.bl_rna_get_subclass"></a>

#### classmethod bpy.types.FunctionNode.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.FunctionNode.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.FunctionNode.bl_rna_get_subclass_py(id, default=None, /)

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
