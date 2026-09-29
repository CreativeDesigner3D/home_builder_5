<!-- source: Blender Python API reference 5.2 / bpy.types.CompositorNodeDefocus.html -->

<a id="compositornodedefocus-compositornode"></a>

# CompositorNodeDefocus(CompositorNode)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Node`](bpy.types.Node.md#bpy.types.Node "bpy.types.Node"), [`NodeInternal`](bpy.types.NodeInternal.md#bpy.types.NodeInternal "bpy.types.NodeInternal"), [`CompositorNode`](bpy.types.CompositorNode.md#bpy.types.CompositorNode "bpy.types.CompositorNode")

<a id="bpy.types.CompositorNodeDefocus"></a>

### class bpy.types.CompositorNodeDefocus(CompositorNode)

Apply depth of field in 2D, using a Z depth map or mask

<a id="bpy.types.CompositorNodeDefocus.angle"></a>

#### bpy.types.CompositorNodeDefocus.angle

Bokeh shape rotation offset (in [0, 1.5708], default 0.0)

**Type:**

float

<a id="bpy.types.CompositorNodeDefocus.blur_max"></a>

#### bpy.types.CompositorNodeDefocus.blur_max

Blur limit, maximum CoC radius (in [0, 10000], default 0.0)

**Type:**

float

<a id="bpy.types.CompositorNodeDefocus.bokeh"></a>

#### bpy.types.CompositorNodeDefocus.bokeh

(default `'CIRCLE'`)

- `OCTAGON`
  Octagonal – 8 sides.
- `HEPTAGON`
  Heptagonal – 7 sides.
- `HEXAGON`
  Hexagonal – 6 sides.
- `PENTAGON`
  Pentagonal – 5 sides.
- `SQUARE`
  Square – 4 sides.
- `TRIANGLE`
  Triangular – 3 sides.
- `CIRCLE`
  Circular.

**Type:**

Literal[‘OCTAGON’, ‘HEPTAGON’, ‘HEXAGON’, ‘PENTAGON’, ‘SQUARE’, ‘TRIANGLE’, ‘CIRCLE’]

<a id="bpy.types.CompositorNodeDefocus.f_stop"></a>

#### bpy.types.CompositorNodeDefocus.f_stop

Amount of focal blur, 128 (infinity) is perfect focus, half the value doubles the blur radius (in [0, 128], default 0.0)

**Type:**

float

<a id="bpy.types.CompositorNodeDefocus.scene"></a>

#### bpy.types.CompositorNodeDefocus.scene

Scene from which to select the active camera (render scene if undefined)

**Type:**

[`Scene`](bpy.types.Scene.md#bpy.types.Scene "bpy.types.Scene") | None

<a id="bpy.types.CompositorNodeDefocus.use_zbuffer"></a>

#### bpy.types.CompositorNodeDefocus.use_zbuffer

Disable when using an image as input instead of actual z-buffer (auto enabled if node not image based, eg. time node) (default True)

**Type:**

bool

<a id="bpy.types.CompositorNodeDefocus.z_scale"></a>

#### bpy.types.CompositorNodeDefocus.z_scale

Scale the Z input when not using a z-buffer, controls maximum blur designated by the color white or input value 1 (in [0, 1000], default 0.0)

**Type:**

float

<a id="bpy.types.CompositorNodeDefocus.is_registered_node_type"></a>

#### classmethod bpy.types.CompositorNodeDefocus.is_registered_node_type()

True if a registered node type

**Returns:**

Result

**Return type:**

bool

<a id="bpy.types.CompositorNodeDefocus.input_template"></a>

#### classmethod bpy.types.CompositorNodeDefocus.input_template(index)

Input socket template

**Parameters:**

**index** (int) – Index, (in [0, inf])

**Returns:**

result

**Return type:**

[`NodeInternalSocketTemplate`](bpy.types.NodeInternalSocketTemplate.md#bpy.types.NodeInternalSocketTemplate "bpy.types.NodeInternalSocketTemplate")

<a id="bpy.types.CompositorNodeDefocus.output_template"></a>

#### classmethod bpy.types.CompositorNodeDefocus.output_template(index)

Output socket template

**Parameters:**

**index** (int) – Index, (in [0, inf])

**Returns:**

result

**Return type:**

[`NodeInternalSocketTemplate`](bpy.types.NodeInternalSocketTemplate.md#bpy.types.NodeInternalSocketTemplate "bpy.types.NodeInternalSocketTemplate")

<a id="bpy.types.CompositorNodeDefocus.bl_rna_get_subclass"></a>

#### classmethod bpy.types.CompositorNodeDefocus.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.CompositorNodeDefocus.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.CompositorNodeDefocus.bl_rna_get_subclass_py(id, default=None, /)

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

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, Node.bl_system_properties_get, Node.socket_value_update, Node.is_registered_node_type, Node.poll, Node.poll_instance, Node.update, Node.insert_link, Node.init, Node.copy, Node.free, Node.draw_buttons, Node.draw_buttons_ext, Node.draw_label, Node.debug_zone_body_lazy_function_graph, Node.debug_zone_lazy_function_graph, Node.bl_rna_get_subclass, Node.bl_rna_get_subclass_py, NodeInternal.poll, NodeInternal.poll_instance, NodeInternal.update, NodeInternal.draw_buttons, NodeInternal.draw_buttons_ext, NodeInternal.bl_rna_get_subclass, NodeInternal.bl_rna_get_subclass_py, CompositorNode.poll, CompositorNode.bl_rna_get_subclass, CompositorNode.bl_rna_get_subclass_py
