<!-- source: Blender Python API reference 5.2 / bpy.types.ShaderNodeTexSky.html -->

<a id="shadernodetexsky-shadernode"></a>

# ShaderNodeTexSky(ShaderNode)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Node`](bpy.types.Node.md#bpy.types.Node "bpy.types.Node"), [`NodeInternal`](bpy.types.NodeInternal.md#bpy.types.NodeInternal "bpy.types.NodeInternal"), [`ShaderNode`](bpy.types.ShaderNode.md#bpy.types.ShaderNode "bpy.types.ShaderNode")

<a id="bpy.types.ShaderNodeTexSky"></a>

### class bpy.types.ShaderNodeTexSky(ShaderNode)

Generate a procedural sky texture

<a id="bpy.types.ShaderNodeTexSky.aerosol_density"></a>

#### bpy.types.ShaderNodeTexSky.aerosol_density

Density of dust, pollution and water droplets.
0 means no aerosols, 1 means urban city aerosols

(in [0, 1000], default 1.0)

**Type:**

float

<a id="bpy.types.ShaderNodeTexSky.air_density"></a>

#### bpy.types.ShaderNodeTexSky.air_density

Density of air molecules.
0 means no air, 1 means urban city air

(in [0, 1000], default 1.0)

**Type:**

float

<a id="bpy.types.ShaderNodeTexSky.altitude"></a>

#### bpy.types.ShaderNodeTexSky.altitude

Height from sea level (in [0, 100000], default 100.0)

**Type:**

float

<a id="bpy.types.ShaderNodeTexSky.color_mapping"></a>

#### bpy.types.ShaderNodeTexSky.color_mapping

Color mapping settings (readonly, never None)

**Type:**

[`ColorMapping`](bpy.types.ColorMapping.md#bpy.types.ColorMapping "bpy.types.ColorMapping")

<a id="bpy.types.ShaderNodeTexSky.ground_albedo"></a>

#### bpy.types.ShaderNodeTexSky.ground_albedo

Ground color that is subtly reflected in the sky (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.ShaderNodeTexSky.ozone_density"></a>

#### bpy.types.ShaderNodeTexSky.ozone_density

Density of ozone layer.
0 means no ozone, 1 means urban city ozone

(in [0, 1000], default 1.0)

**Type:**

float

<a id="bpy.types.ShaderNodeTexSky.sky_type"></a>

#### bpy.types.ShaderNodeTexSky.sky_type

Which sky model should be used (default `'PREETHAM'`)

- `SINGLE_SCATTERING`
  Single Scattering – Single scattering sky model.
- `MULTIPLE_SCATTERING`
  Multiple Scattering – Multiple scattering sky model (more accurate).
- `PREETHAM`
  Preetham – Preetham 1999 (Legacy).
- `HOSEK_WILKIE`
  Hosek / Wilkie – Hosek / Wilkie 2012 (Legacy).

**Type:**

Literal[‘SINGLE_SCATTERING’, ‘MULTIPLE_SCATTERING’, ‘PREETHAM’, ‘HOSEK_WILKIE’]

<a id="bpy.types.ShaderNodeTexSky.sun_direction"></a>

#### bpy.types.ShaderNodeTexSky.sun_direction

Direction from where the sun is shining (array of 3 items, in [-inf, inf], default (0.0, 0.0, 1.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.ShaderNodeTexSky.sun_disc"></a>

#### bpy.types.ShaderNodeTexSky.sun_disc

Include the sun itself in the output (default True)

**Type:**

bool

<a id="bpy.types.ShaderNodeTexSky.sun_elevation"></a>

#### bpy.types.ShaderNodeTexSky.sun_elevation

Sun angle from horizon (in [-inf, inf], default 0.261799)

**Type:**

float

<a id="bpy.types.ShaderNodeTexSky.sun_intensity"></a>

#### bpy.types.ShaderNodeTexSky.sun_intensity

Strength of Sun (in [0, 1000], default 1.0)

**Type:**

float

<a id="bpy.types.ShaderNodeTexSky.sun_rotation"></a>

#### bpy.types.ShaderNodeTexSky.sun_rotation

Rotation of sun around zenith (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.ShaderNodeTexSky.sun_size"></a>

#### bpy.types.ShaderNodeTexSky.sun_size

Size of sun disc (in [0, 1.5708], default 0.00951204)

**Type:**

float

<a id="bpy.types.ShaderNodeTexSky.texture_mapping"></a>

#### bpy.types.ShaderNodeTexSky.texture_mapping

Texture coordinate mapping settings (readonly, never None)

**Type:**

[`TexMapping`](bpy.types.TexMapping.md#bpy.types.TexMapping "bpy.types.TexMapping")

<a id="bpy.types.ShaderNodeTexSky.turbidity"></a>

#### bpy.types.ShaderNodeTexSky.turbidity

Atmospheric turbidity (in [1, 10], default 0.0)

**Type:**

float

<a id="bpy.types.ShaderNodeTexSky.is_registered_node_type"></a>

#### classmethod bpy.types.ShaderNodeTexSky.is_registered_node_type()

True if a registered node type

**Returns:**

Result

**Return type:**

bool

<a id="bpy.types.ShaderNodeTexSky.input_template"></a>

#### classmethod bpy.types.ShaderNodeTexSky.input_template(index)

Input socket template

**Parameters:**

**index** (int) – Index, (in [0, inf])

**Returns:**

result

**Return type:**

[`NodeInternalSocketTemplate`](bpy.types.NodeInternalSocketTemplate.md#bpy.types.NodeInternalSocketTemplate "bpy.types.NodeInternalSocketTemplate")

<a id="bpy.types.ShaderNodeTexSky.output_template"></a>

#### classmethod bpy.types.ShaderNodeTexSky.output_template(index)

Output socket template

**Parameters:**

**index** (int) – Index, (in [0, inf])

**Returns:**

result

**Return type:**

[`NodeInternalSocketTemplate`](bpy.types.NodeInternalSocketTemplate.md#bpy.types.NodeInternalSocketTemplate "bpy.types.NodeInternalSocketTemplate")

<a id="bpy.types.ShaderNodeTexSky.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ShaderNodeTexSky.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ShaderNodeTexSky.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ShaderNodeTexSky.bl_rna_get_subclass_py(id, default=None, /)

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
