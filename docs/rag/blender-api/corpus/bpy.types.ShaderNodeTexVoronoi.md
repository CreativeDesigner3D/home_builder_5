<!-- source: Blender Python API reference 5.2 / bpy.types.ShaderNodeTexVoronoi.html -->

<a id="shadernodetexvoronoi-shadernode"></a>

# ShaderNodeTexVoronoi(ShaderNode)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Node`](bpy.types.Node.md#bpy.types.Node "bpy.types.Node"), [`NodeInternal`](bpy.types.NodeInternal.md#bpy.types.NodeInternal "bpy.types.NodeInternal"), [`ShaderNode`](bpy.types.ShaderNode.md#bpy.types.ShaderNode "bpy.types.ShaderNode")

<a id="bpy.types.ShaderNodeTexVoronoi"></a>

### class bpy.types.ShaderNodeTexVoronoi(ShaderNode)

Generate Worley noise based on the distance to random points. Typically used to generate textures such as stones, water, or biological cells

<a id="bpy.types.ShaderNodeTexVoronoi.color_mapping"></a>

#### bpy.types.ShaderNodeTexVoronoi.color_mapping

Color mapping settings (readonly, never None)

**Type:**

[`ColorMapping`](bpy.types.ColorMapping.md#bpy.types.ColorMapping "bpy.types.ColorMapping")

<a id="bpy.types.ShaderNodeTexVoronoi.distance"></a>

#### bpy.types.ShaderNodeTexVoronoi.distance

The distance metric used to compute the texture (default `'EUCLIDEAN'`)

- `EUCLIDEAN`
  Euclidean – Euclidean distance.
- `MANHATTAN`
  Manhattan – Manhattan distance.
- `CHEBYCHEV`
  Chebychev – Chebychev distance.
- `MINKOWSKI`
  Minkowski – Minkowski distance.

**Type:**

Literal[‘EUCLIDEAN’, ‘MANHATTAN’, ‘CHEBYCHEV’, ‘MINKOWSKI’]

<a id="bpy.types.ShaderNodeTexVoronoi.feature"></a>

#### bpy.types.ShaderNodeTexVoronoi.feature

The Voronoi feature that the node will compute (default `'F1'`)

- `F1`
  F1 – Computes the distance to the closest point as well as its position and color.
- `F2`
  F2 – Computes the distance to the second closest point as well as its position and color.
- `SMOOTH_F1`
  Smooth F1 – Smoothed version of F1. Weighted sum of neighbor voronoi cells..
- `DISTANCE_TO_EDGE`
  Distance to Edge – Computes the distance to the edge of the voronoi cell.
- `N_SPHERE_RADIUS`
  N-Sphere Radius – Computes the radius of the n-sphere inscribed in the voronoi cell.

**Type:**

Literal[‘F1’, ‘F2’, ‘SMOOTH_F1’, ‘DISTANCE_TO_EDGE’, ‘N_SPHERE_RADIUS’]

<a id="bpy.types.ShaderNodeTexVoronoi.normalize"></a>

#### bpy.types.ShaderNodeTexVoronoi.normalize

Normalize output Distance to 0.0 to 1.0 range (default False)

**Type:**

bool

<a id="bpy.types.ShaderNodeTexVoronoi.texture_mapping"></a>

#### bpy.types.ShaderNodeTexVoronoi.texture_mapping

Texture coordinate mapping settings (readonly, never None)

**Type:**

[`TexMapping`](bpy.types.TexMapping.md#bpy.types.TexMapping "bpy.types.TexMapping")

<a id="bpy.types.ShaderNodeTexVoronoi.voronoi_dimensions"></a>

#### bpy.types.ShaderNodeTexVoronoi.voronoi_dimensions

Number of dimensions to output noise for (default `'1D'`)

- `1D`
  1D – Use the scalar value W as input.
- `2D`
  2D – Use the 2D vector (X, Y) as input. The Z component is ignored..
- `3D`
  3D – Use the 3D vector (X, Y, Z) as input.
- `4D`
  4D – Use the 4D vector (X, Y, Z, W) as input.

**Type:**

Literal[‘1D’, ‘2D’, ‘3D’, ‘4D’]

<a id="bpy.types.ShaderNodeTexVoronoi.is_registered_node_type"></a>

#### classmethod bpy.types.ShaderNodeTexVoronoi.is_registered_node_type()

True if a registered node type

**Returns:**

Result

**Return type:**

bool

<a id="bpy.types.ShaderNodeTexVoronoi.input_template"></a>

#### classmethod bpy.types.ShaderNodeTexVoronoi.input_template(index)

Input socket template

**Parameters:**

**index** (int) – Index, (in [0, inf])

**Returns:**

result

**Return type:**

[`NodeInternalSocketTemplate`](bpy.types.NodeInternalSocketTemplate.md#bpy.types.NodeInternalSocketTemplate "bpy.types.NodeInternalSocketTemplate")

<a id="bpy.types.ShaderNodeTexVoronoi.output_template"></a>

#### classmethod bpy.types.ShaderNodeTexVoronoi.output_template(index)

Output socket template

**Parameters:**

**index** (int) – Index, (in [0, inf])

**Returns:**

result

**Return type:**

[`NodeInternalSocketTemplate`](bpy.types.NodeInternalSocketTemplate.md#bpy.types.NodeInternalSocketTemplate "bpy.types.NodeInternalSocketTemplate")

<a id="bpy.types.ShaderNodeTexVoronoi.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ShaderNodeTexVoronoi.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ShaderNodeTexVoronoi.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ShaderNodeTexVoronoi.bl_rna_get_subclass_py(id, default=None, /)

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
