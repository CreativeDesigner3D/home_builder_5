<!-- source: Blender Python API reference 5.2 / bpy.types.ShaderNodeMapRange.html -->

<a id="shadernodemaprange-shadernode"></a>

# ShaderNodeMapRange(ShaderNode)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Node`](bpy.types.Node.md#bpy.types.Node "bpy.types.Node"), [`NodeInternal`](bpy.types.NodeInternal.md#bpy.types.NodeInternal "bpy.types.NodeInternal"), [`ShaderNode`](bpy.types.ShaderNode.md#bpy.types.ShaderNode "bpy.types.ShaderNode")

<a id="bpy.types.ShaderNodeMapRange"></a>

### class bpy.types.ShaderNodeMapRange(ShaderNode)

Remap a value from a range to a target range

<a id="bpy.types.ShaderNodeMapRange.clamp"></a>

#### bpy.types.ShaderNodeMapRange.clamp

Clamp the result to the target range [To Min, To Max] (default False)

**Type:**

bool

<a id="bpy.types.ShaderNodeMapRange.data_type"></a>

#### bpy.types.ShaderNodeMapRange.data_type

(default `'FLOAT'`)

- `FLOAT`
  Float – Floating-point value.
- `FLOAT_VECTOR`
  Vector – 3D vector with floating-point values.

**Type:**

Literal[‘FLOAT’, ‘FLOAT_VECTOR’]

<a id="bpy.types.ShaderNodeMapRange.interpolation_type"></a>

#### bpy.types.ShaderNodeMapRange.interpolation_type

(default `'LINEAR'`)

**Type:**

Literal[[Node Map Range Items](bpy_types_enum_items/node_map_range_items.md#rna-enum-node-map-range-items)]

<a id="bpy.types.ShaderNodeMapRange.is_registered_node_type"></a>

#### classmethod bpy.types.ShaderNodeMapRange.is_registered_node_type()

True if a registered node type

**Returns:**

Result

**Return type:**

bool

<a id="bpy.types.ShaderNodeMapRange.input_template"></a>

#### classmethod bpy.types.ShaderNodeMapRange.input_template(index)

Input socket template

**Parameters:**

**index** (int) – Index, (in [0, inf])

**Returns:**

result

**Return type:**

[`NodeInternalSocketTemplate`](bpy.types.NodeInternalSocketTemplate.md#bpy.types.NodeInternalSocketTemplate "bpy.types.NodeInternalSocketTemplate")

<a id="bpy.types.ShaderNodeMapRange.output_template"></a>

#### classmethod bpy.types.ShaderNodeMapRange.output_template(index)

Output socket template

**Parameters:**

**index** (int) – Index, (in [0, inf])

**Returns:**

result

**Return type:**

[`NodeInternalSocketTemplate`](bpy.types.NodeInternalSocketTemplate.md#bpy.types.NodeInternalSocketTemplate "bpy.types.NodeInternalSocketTemplate")

<a id="bpy.types.ShaderNodeMapRange.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ShaderNodeMapRange.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ShaderNodeMapRange.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ShaderNodeMapRange.bl_rna_get_subclass_py(id, default=None, /)

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

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, Node.bl_system_properties_get, Node.socket_value_update, Node.is_registered_node_type, Node.poll, Node.poll_instance, Node.update, Node.insert_link, Node.init, Node.copy, Node.free, Node.draw_buttons, Node.draw_buttons_ext, Node.draw_label, Node.debug_zone_body_lazy_function_graph, Node.debug_zone_lazy_function_graph, Node.bl_rna_get_subclass, Node.bl_rna_get_subclass_py, NodeInternal.poll, NodeInternal.poll_instance, NodeInternal.update, NodeInternal.draw_buttons, NodeInternal.draw_buttons_ext, NodeInternal.bl_rna_get_subclass, NodeInternal.bl_rna_get_subclass_py, ShaderNode.poll, ShaderNode.bl_rna_get_subclass, ShaderNode.bl_rna_get_subclass_py
