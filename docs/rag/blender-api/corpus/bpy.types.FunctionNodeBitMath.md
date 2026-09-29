<!-- source: Blender Python API reference 5.2 / bpy.types.FunctionNodeBitMath.html -->

<a id="functionnodebitmath-functionnode"></a>

# FunctionNodeBitMath(FunctionNode)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Node`](bpy.types.Node.md#bpy.types.Node "bpy.types.Node"), [`NodeInternal`](bpy.types.NodeInternal.md#bpy.types.NodeInternal "bpy.types.NodeInternal"), [`FunctionNode`](bpy.types.FunctionNode.md#bpy.types.FunctionNode "bpy.types.FunctionNode")

<a id="bpy.types.FunctionNodeBitMath"></a>

### class bpy.types.FunctionNodeBitMath(FunctionNode)

Perform bitwise operations on 32-bit integers

<a id="bpy.types.FunctionNodeBitMath.operation"></a>

#### bpy.types.FunctionNodeBitMath.operation

(default `'AND'`)

- `AND`
  And – Returns a value where the bits of A and B are both set.
- `OR`
  Or – Returns a value where the bits of either A or B are set.
- `XOR`
  Exclusive Or – Returns a value where only one bit from A and B is set.
- `NOT`
  Not – Returns the opposite bit value of A, in decimal it is equivalent of A = -A - 1.
- `SHIFT`
  Shift – Shifts the bit values of A by the specified Shift amount. Positive values shift left, negative values shift right..
- `ROTATE`
  Rotate – Rotates the bit values of A by the specified Shift amount. Positive values rotate left, negative values rotate right..

**Type:**

Literal[‘AND’, ‘OR’, ‘XOR’, ‘NOT’, ‘SHIFT’, ‘ROTATE’]

<a id="bpy.types.FunctionNodeBitMath.is_registered_node_type"></a>

#### classmethod bpy.types.FunctionNodeBitMath.is_registered_node_type()

True if a registered node type

**Returns:**

Result

**Return type:**

bool

<a id="bpy.types.FunctionNodeBitMath.input_template"></a>

#### classmethod bpy.types.FunctionNodeBitMath.input_template(index)

Input socket template

**Parameters:**

**index** (int) – Index, (in [0, inf])

**Returns:**

result

**Return type:**

[`NodeInternalSocketTemplate`](bpy.types.NodeInternalSocketTemplate.md#bpy.types.NodeInternalSocketTemplate "bpy.types.NodeInternalSocketTemplate")

<a id="bpy.types.FunctionNodeBitMath.output_template"></a>

#### classmethod bpy.types.FunctionNodeBitMath.output_template(index)

Output socket template

**Parameters:**

**index** (int) – Index, (in [0, inf])

**Returns:**

result

**Return type:**

[`NodeInternalSocketTemplate`](bpy.types.NodeInternalSocketTemplate.md#bpy.types.NodeInternalSocketTemplate "bpy.types.NodeInternalSocketTemplate")

<a id="bpy.types.FunctionNodeBitMath.bl_rna_get_subclass"></a>

#### classmethod bpy.types.FunctionNodeBitMath.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.FunctionNodeBitMath.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.FunctionNodeBitMath.bl_rna_get_subclass_py(id, default=None, /)

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

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, Node.bl_system_properties_get, Node.socket_value_update, Node.is_registered_node_type, Node.poll, Node.poll_instance, Node.update, Node.insert_link, Node.init, Node.copy, Node.free, Node.draw_buttons, Node.draw_buttons_ext, Node.draw_label, Node.debug_zone_body_lazy_function_graph, Node.debug_zone_lazy_function_graph, Node.bl_rna_get_subclass, Node.bl_rna_get_subclass_py, NodeInternal.poll, NodeInternal.poll_instance, NodeInternal.update, NodeInternal.draw_buttons, NodeInternal.draw_buttons_ext, NodeInternal.bl_rna_get_subclass, NodeInternal.bl_rna_get_subclass_py, FunctionNode.bl_rna_get_subclass, FunctionNode.bl_rna_get_subclass_py
