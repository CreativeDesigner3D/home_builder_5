<!-- source: Blender Python API reference 5.2 / bpy.types.CompositorNodeCryptomatteV2.html -->

<a id="compositornodecryptomattev2-compositornode"></a>

# CompositorNodeCryptomatteV2(CompositorNode)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Node`](bpy.types.Node.md#bpy.types.Node "bpy.types.Node"), [`NodeInternal`](bpy.types.NodeInternal.md#bpy.types.NodeInternal "bpy.types.NodeInternal"), [`CompositorNode`](bpy.types.CompositorNode.md#bpy.types.CompositorNode "bpy.types.CompositorNode")

<a id="bpy.types.CompositorNodeCryptomatteV2"></a>

### class bpy.types.CompositorNodeCryptomatteV2(CompositorNode)

Generate matte for individual objects and materials using Cryptomatte render passes

<a id="bpy.types.CompositorNodeCryptomatteV2.add"></a>

#### bpy.types.CompositorNodeCryptomatteV2.add

Add object or material to matte, by picking a color from the Pick output (array of 3 items, in [-inf, inf], default (1.0, 1.0, 1.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.CompositorNodeCryptomatteV2.entries"></a>

#### bpy.types.CompositorNodeCryptomatteV2.entries

(default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`CryptomatteEntry`](bpy.types.CryptomatteEntry.md#bpy.types.CryptomatteEntry "bpy.types.CryptomatteEntry")]

<a id="bpy.types.CompositorNodeCryptomatteV2.frame_duration"></a>

#### bpy.types.CompositorNodeCryptomatteV2.frame_duration

Number of images of a movie to use (in [0, 1048574], default 0)

**Type:**

int

<a id="bpy.types.CompositorNodeCryptomatteV2.frame_offset"></a>

#### bpy.types.CompositorNodeCryptomatteV2.frame_offset

Offset the number of the frame to use in the animation (in [-1048574, 1048574], default 0)

**Type:**

int

<a id="bpy.types.CompositorNodeCryptomatteV2.frame_start"></a>

#### bpy.types.CompositorNodeCryptomatteV2.frame_start

Global starting frame of the movie/sequence, assuming first picture has a #1 (in [-1048574, 1048574], default 0)

**Type:**

int

<a id="bpy.types.CompositorNodeCryptomatteV2.has_layers"></a>

#### bpy.types.CompositorNodeCryptomatteV2.has_layers

True if this image has any named layer (default False, readonly)

**Type:**

bool

<a id="bpy.types.CompositorNodeCryptomatteV2.has_views"></a>

#### bpy.types.CompositorNodeCryptomatteV2.has_views

True if this image has multiple views (default False, readonly)

**Type:**

bool

<a id="bpy.types.CompositorNodeCryptomatteV2.image"></a>

#### bpy.types.CompositorNodeCryptomatteV2.image

**Type:**

[`Image`](bpy.types.Image.md#bpy.types.Image "bpy.types.Image") | None

<a id="bpy.types.CompositorNodeCryptomatteV2.layer"></a>

#### bpy.types.CompositorNodeCryptomatteV2.layer

(default `'PLACEHOLDER'`)

**Type:**

Literal[‘PLACEHOLDER’]

<a id="bpy.types.CompositorNodeCryptomatteV2.layer_name"></a>

#### bpy.types.CompositorNodeCryptomatteV2.layer_name

What Cryptomatte layer is used (default `'CryptoObject'`)

- `CryptoObject`
  Object – Use Object layer.
- `CryptoMaterial`
  Material – Use Material layer.
- `CryptoAsset`
  Asset – Use Asset layer.

**Type:**

Literal[‘CryptoObject’, ‘CryptoMaterial’, ‘CryptoAsset’]

<a id="bpy.types.CompositorNodeCryptomatteV2.matte_id"></a>

#### bpy.types.CompositorNodeCryptomatteV2.matte_id

List of object and material crypto IDs to include in matte (default “”, never None)

**Type:**

str

<a id="bpy.types.CompositorNodeCryptomatteV2.remove"></a>

#### bpy.types.CompositorNodeCryptomatteV2.remove

Remove object or material from matte, by picking a color from the Pick output (array of 3 items, in [-inf, inf], default (1.0, 1.0, 1.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.CompositorNodeCryptomatteV2.scene"></a>

#### bpy.types.CompositorNodeCryptomatteV2.scene

**Type:**

[`Scene`](bpy.types.Scene.md#bpy.types.Scene "bpy.types.Scene") | None

<a id="bpy.types.CompositorNodeCryptomatteV2.source"></a>

#### bpy.types.CompositorNodeCryptomatteV2.source

Where the Cryptomatte passes are loaded from (default `'RENDER'`)

- `RENDER`
  Render – Use Cryptomatte passes from a render.
- `IMAGE`
  Image – Use Cryptomatte passes from an image.

**Type:**

Literal[‘RENDER’, ‘IMAGE’]

<a id="bpy.types.CompositorNodeCryptomatteV2.use_auto_refresh"></a>

#### bpy.types.CompositorNodeCryptomatteV2.use_auto_refresh

Always refresh image on frame changes (default False)

**Type:**

bool

<a id="bpy.types.CompositorNodeCryptomatteV2.use_cyclic"></a>

#### bpy.types.CompositorNodeCryptomatteV2.use_cyclic

Cycle the images in the movie (default False)

**Type:**

bool

<a id="bpy.types.CompositorNodeCryptomatteV2.view"></a>

#### bpy.types.CompositorNodeCryptomatteV2.view

(default `'ALL'`)

**Type:**

Literal[‘ALL’]

<a id="bpy.types.CompositorNodeCryptomatteV2.is_registered_node_type"></a>

#### classmethod bpy.types.CompositorNodeCryptomatteV2.is_registered_node_type()

True if a registered node type

**Returns:**

Result

**Return type:**

bool

<a id="bpy.types.CompositorNodeCryptomatteV2.input_template"></a>

#### classmethod bpy.types.CompositorNodeCryptomatteV2.input_template(index)

Input socket template

**Parameters:**

**index** (int) – Index, (in [0, inf])

**Returns:**

result

**Return type:**

[`NodeInternalSocketTemplate`](bpy.types.NodeInternalSocketTemplate.md#bpy.types.NodeInternalSocketTemplate "bpy.types.NodeInternalSocketTemplate")

<a id="bpy.types.CompositorNodeCryptomatteV2.output_template"></a>

#### classmethod bpy.types.CompositorNodeCryptomatteV2.output_template(index)

Output socket template

**Parameters:**

**index** (int) – Index, (in [0, inf])

**Returns:**

result

**Return type:**

[`NodeInternalSocketTemplate`](bpy.types.NodeInternalSocketTemplate.md#bpy.types.NodeInternalSocketTemplate "bpy.types.NodeInternalSocketTemplate")

<a id="bpy.types.CompositorNodeCryptomatteV2.bl_rna_get_subclass"></a>

#### classmethod bpy.types.CompositorNodeCryptomatteV2.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.CompositorNodeCryptomatteV2.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.CompositorNodeCryptomatteV2.bl_rna_get_subclass_py(id, default=None, /)

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
