<!-- source: Blender Python API reference 5.2 / bpy.types.GreasePencilLayer.html -->

<a id="greasepencillayer-greasepenciltreenode"></a>

# GreasePencilLayer(GreasePencilTreeNode)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`GreasePencilTreeNode`](bpy.types.GreasePencilTreeNode.md#bpy.types.GreasePencilTreeNode "bpy.types.GreasePencilTreeNode")

<a id="bpy.types.GreasePencilLayer"></a>

### class bpy.types.GreasePencilLayer(GreasePencilTreeNode)

Collection of related drawings

<a id="bpy.types.GreasePencilLayer.blend_mode"></a>

#### bpy.types.GreasePencilLayer.blend_mode

Blend mode (default `'REGULAR'`)

**Type:**

Literal[‘REGULAR’, ‘HARDLIGHT’, ‘ADD’, ‘SUBTRACT’, ‘MULTIPLY’, ‘DIVIDE’]

<a id="bpy.types.GreasePencilLayer.frames"></a>

#### bpy.types.GreasePencilLayer.frames

Grease Pencil frames (default None, readonly)

**Type:**

[`GreasePencilFrames`](bpy.types.GreasePencilFrames.md#bpy.types.GreasePencilFrames "bpy.types.GreasePencilFrames")[[`GreasePencilFrame`](bpy.types.GreasePencilFrame.md#bpy.types.GreasePencilFrame "bpy.types.GreasePencilFrame")]

<a id="bpy.types.GreasePencilLayer.ignore_locked_materials"></a>

#### bpy.types.GreasePencilLayer.ignore_locked_materials

Allow editing strokes even if they use locked materials (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilLayer.lock_frame"></a>

#### bpy.types.GreasePencilLayer.lock_frame

Lock current frame displayed by layer (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilLayer.mask_layers"></a>

#### bpy.types.GreasePencilLayer.mask_layers

List of Masking Layers (default None, readonly)

**Type:**

[`GreasePencilLayerMasks`](bpy.types.GreasePencilLayerMasks.md#bpy.types.GreasePencilLayerMasks "bpy.types.GreasePencilLayerMasks")[[`GreasePencilLayerMask`](bpy.types.GreasePencilLayerMask.md#bpy.types.GreasePencilLayerMask "bpy.types.GreasePencilLayerMask")]

<a id="bpy.types.GreasePencilLayer.matrix_local"></a>

#### bpy.types.GreasePencilLayer.matrix_local

Local transformation matrix of the layer (multi-dimensional array of 4 * 4 items, in [-inf, inf], default ((0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0)), readonly)

**Type:**

[`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")

<a id="bpy.types.GreasePencilLayer.matrix_parent_inverse"></a>

#### bpy.types.GreasePencilLayer.matrix_parent_inverse

Inverse of layer’s parent transformation matrix (multi-dimensional array of 4 * 4 items, in [-inf, inf], default ((0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0)), readonly)

**Type:**

[`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")

<a id="bpy.types.GreasePencilLayer.opacity"></a>

#### bpy.types.GreasePencilLayer.opacity

Layer Opacity (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.GreasePencilLayer.parent"></a>

#### bpy.types.GreasePencilLayer.parent

Parent object

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.GreasePencilLayer.parent_bone"></a>

#### bpy.types.GreasePencilLayer.parent_bone

Name of parent bone. Only used when the parent object is an armature. (default “”, never None)

**Type:**

str

<a id="bpy.types.GreasePencilLayer.pass_index"></a>

#### bpy.types.GreasePencilLayer.pass_index

Index number for the “Layer Index” pass (in [0, inf], default 0)

**Type:**

int

<a id="bpy.types.GreasePencilLayer.radius_offset"></a>

#### bpy.types.GreasePencilLayer.radius_offset

Radius change to apply to current strokes (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.GreasePencilLayer.rotation"></a>

#### bpy.types.GreasePencilLayer.rotation

Euler rotation of the layer (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler")

<a id="bpy.types.GreasePencilLayer.scale"></a>

#### bpy.types.GreasePencilLayer.scale

Scale of the layer (array of 3 items, in [-inf, inf], default (1.0, 1.0, 1.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.GreasePencilLayer.tint_color"></a>

#### bpy.types.GreasePencilLayer.tint_color

Color for tinting stroke colors (array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.GreasePencilLayer.tint_factor"></a>

#### bpy.types.GreasePencilLayer.tint_factor

Factor of tinting color (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.GreasePencilLayer.translation"></a>

#### bpy.types.GreasePencilLayer.translation

Translation of the layer (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.GreasePencilLayer.use_lights"></a>

#### bpy.types.GreasePencilLayer.use_lights

Enable the use of lights on stroke and fill materials (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilLayer.use_viewlayer_masks"></a>

#### bpy.types.GreasePencilLayer.use_viewlayer_masks

Include the mask layers when rendering the view-layer (default True)

**Type:**

bool

<a id="bpy.types.GreasePencilLayer.viewlayer_render"></a>

#### bpy.types.GreasePencilLayer.viewlayer_render

Only include Layer in this View Layer render output (leave blank to include always) (default “”, never None)

**Type:**

str

<a id="bpy.types.GreasePencilLayer.get_frame_at"></a>

#### bpy.types.GreasePencilLayer.get_frame_at(frame_number)

Get the frame at given frame number

**Parameters:**

**frame_number** (int) – Frame Number, (in [-1048574, 1048574])

**Returns:**

Frame

**Return type:**

[`GreasePencilFrame`](bpy.types.GreasePencilFrame.md#bpy.types.GreasePencilFrame "bpy.types.GreasePencilFrame")

<a id="bpy.types.GreasePencilLayer.current_frame"></a>

#### bpy.types.GreasePencilLayer.current_frame()

The Grease Pencil frame at the current scene time on this layer

**Return type:**

[`GreasePencilFrame`](bpy.types.GreasePencilFrame.md#bpy.types.GreasePencilFrame "bpy.types.GreasePencilFrame")

<a id="bpy.types.GreasePencilLayer.bl_rna_get_subclass"></a>

#### classmethod bpy.types.GreasePencilLayer.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.GreasePencilLayer.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.GreasePencilLayer.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, GreasePencilTreeNode.name, GreasePencilTreeNode.hide, GreasePencilTreeNode.lock, GreasePencilTreeNode.select, GreasePencilTreeNode.use_onion_skinning, GreasePencilTreeNode.use_masks, GreasePencilTreeNode.channel_color, GreasePencilTreeNode.next_node, GreasePencilTreeNode.prev_node, GreasePencilTreeNode.parent_group

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, GreasePencilTreeNode.bl_rna_get_subclass, GreasePencilTreeNode.bl_rna_get_subclass_py

<a id="references"></a>

## References

|  |  |
| --- | --- |
| - [`GreasePencil.layers`](bpy.types.GreasePencil.md#bpy.types.GreasePencil.layers "bpy.types.GreasePencil.layers") - [`GreasePencilLayerMasks.add`](bpy.types.GreasePencilLayerMasks.md#bpy.types.GreasePencilLayerMasks.add "bpy.types.GreasePencilLayerMasks.add") - [`GreasePencilv3Layers.active`](bpy.types.GreasePencilv3Layers.md#bpy.types.GreasePencilv3Layers.active "bpy.types.GreasePencilv3Layers.active") - [`GreasePencilv3Layers.move`](bpy.types.GreasePencilv3Layers.md#bpy.types.GreasePencilv3Layers.move "bpy.types.GreasePencilv3Layers.move") - [`GreasePencilv3Layers.move_bottom`](bpy.types.GreasePencilv3Layers.md#bpy.types.GreasePencilv3Layers.move_bottom "bpy.types.GreasePencilv3Layers.move_bottom") | - [`GreasePencilv3Layers.move_to_layer_group`](bpy.types.GreasePencilv3Layers.md#bpy.types.GreasePencilv3Layers.move_to_layer_group "bpy.types.GreasePencilv3Layers.move_to_layer_group") - [`GreasePencilv3Layers.move_top`](bpy.types.GreasePencilv3Layers.md#bpy.types.GreasePencilv3Layers.move_top "bpy.types.GreasePencilv3Layers.move_top") - [`GreasePencilv3Layers.new`](bpy.types.GreasePencilv3Layers.md#bpy.types.GreasePencilv3Layers.new "bpy.types.GreasePencilv3Layers.new") - [`GreasePencilv3Layers.remove`](bpy.types.GreasePencilv3Layers.md#bpy.types.GreasePencilv3Layers.remove "bpy.types.GreasePencilv3Layers.remove") |
