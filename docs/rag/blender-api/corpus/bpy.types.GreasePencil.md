<!-- source: Blender Python API reference 5.2 / bpy.types.GreasePencil.html -->

<a id="greasepencil-id"></a>

# GreasePencil(ID)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")

<a id="bpy.types.GreasePencil"></a>

### class bpy.types.GreasePencil(ID)

Grease Pencil data-block

<a id="bpy.types.GreasePencil.after_color"></a>

#### bpy.types.GreasePencil.after_color

Base color for ghosts after the active frame (array of 3 items, in [0, 1], default (0.12549, 0.082353, 0.529412))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.GreasePencil.animation_data"></a>

#### bpy.types.GreasePencil.animation_data

Animation data for this data-block (readonly)

**Type:**

[`AnimData`](bpy.types.AnimData.md#bpy.types.AnimData "bpy.types.AnimData") | None

<a id="bpy.types.GreasePencil.attributes"></a>

#### bpy.types.GreasePencil.attributes

Geometry attributes (default None, readonly)

**Type:**

[`AttributeGroupGreasePencil`](bpy.types.AttributeGroupGreasePencil.md#bpy.types.AttributeGroupGreasePencil "bpy.types.AttributeGroupGreasePencil")[[`Attribute`](bpy.types.Attribute.md#bpy.types.Attribute "bpy.types.Attribute")]

<a id="bpy.types.GreasePencil.before_color"></a>

#### bpy.types.GreasePencil.before_color

Base color for ghosts before the active frame (array of 3 items, in [0, 1], default (0.145098, 0.419608, 0.137255))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.GreasePencil.color_attributes"></a>

#### bpy.types.GreasePencil.color_attributes

Geometry color attributes (default None, readonly)

**Type:**

[`AttributeGroupGreasePencil`](bpy.types.AttributeGroupGreasePencil.md#bpy.types.AttributeGroupGreasePencil "bpy.types.AttributeGroupGreasePencil")[[`Attribute`](bpy.types.Attribute.md#bpy.types.Attribute "bpy.types.Attribute")]

<a id="bpy.types.GreasePencil.ghost_after_range"></a>

#### bpy.types.GreasePencil.ghost_after_range

Maximum number of frames to show after current frame (0 = don’t show any frames after current) (in [0, 120], default 1)

**Type:**

int

<a id="bpy.types.GreasePencil.ghost_before_range"></a>

#### bpy.types.GreasePencil.ghost_before_range

Maximum number of frames to show before current frame (0 = don’t show any frames before current) (in [0, 120], default 1)

**Type:**

int

<a id="bpy.types.GreasePencil.layer_groups"></a>

#### bpy.types.GreasePencil.layer_groups

Grease Pencil layer groups (default None, readonly)

**Type:**

[`GreasePencilv3LayerGroup`](bpy.types.GreasePencilv3LayerGroup.md#bpy.types.GreasePencilv3LayerGroup "bpy.types.GreasePencilv3LayerGroup")[[`GreasePencilLayerGroup`](bpy.types.GreasePencilLayerGroup.md#bpy.types.GreasePencilLayerGroup "bpy.types.GreasePencilLayerGroup")]

<a id="bpy.types.GreasePencil.layers"></a>

#### bpy.types.GreasePencil.layers

Grease Pencil layers (default None, readonly)

**Type:**

[`GreasePencilv3Layers`](bpy.types.GreasePencilv3Layers.md#bpy.types.GreasePencilv3Layers "bpy.types.GreasePencilv3Layers")[[`GreasePencilLayer`](bpy.types.GreasePencilLayer.md#bpy.types.GreasePencilLayer "bpy.types.GreasePencilLayer")]

<a id="bpy.types.GreasePencil.materials"></a>

#### bpy.types.GreasePencil.materials

(default None, readonly)

**Type:**

[`IDMaterials`](bpy.types.IDMaterials.md#bpy.types.IDMaterials "bpy.types.IDMaterials")[[`Material`](bpy.types.Material.md#bpy.types.Material "bpy.types.Material")]

<a id="bpy.types.GreasePencil.onion_factor"></a>

#### bpy.types.GreasePencil.onion_factor

Change fade opacity of displayed onion frames (in [0, 1], default 0.5)

**Type:**

float

<a id="bpy.types.GreasePencil.onion_keyframe_type"></a>

#### bpy.types.GreasePencil.onion_keyframe_type

Type of keyframe (for filtering) (default `'ALL'`)

- `ALL`
  All – Include all Keyframe types.
- `KEYFRAME`
  Keyframe – Normal keyframe, e.g. for key poses.
- `BREAKDOWN`
  Breakdown – A breakdown pose, e.g. for transitions between key poses.
- `MOVING_HOLD`
  Moving Hold – A keyframe that is part of a moving hold.
- `EXTREME`
  Extreme – An ‘extreme’ pose, or some other purpose as needed.
- `JITTER`
  Jitter – A filler or baked keyframe for keying on ones, or some other purpose as needed.
- `GENERATED`
  Generated – A key generated automatically by a tool, not manually created.

**Type:**

Literal[‘ALL’, ‘KEYFRAME’, ‘BREAKDOWN’, ‘MOVING_HOLD’, ‘EXTREME’, ‘JITTER’, ‘GENERATED’]

<a id="bpy.types.GreasePencil.onion_mode"></a>

#### bpy.types.GreasePencil.onion_mode

Mode to display frames (default `'ABSOLUTE'`)

- `ABSOLUTE`
  Frames – Frames in absolute range of the scene frame.
- `RELATIVE`
  Keyframes – Frames in relative range of the Grease Pencil keyframes.
- `SELECTED`
  Selected – Only selected keyframes.

**Type:**

Literal[‘ABSOLUTE’, ‘RELATIVE’, ‘SELECTED’]

<a id="bpy.types.GreasePencil.root_nodes"></a>

#### bpy.types.GreasePencil.root_nodes

The root nodes of the layer tree. Ordered by stack order, meaning the first node is the bottom most node in the layer tree. (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`GreasePencilTreeNode`](bpy.types.GreasePencilTreeNode.md#bpy.types.GreasePencilTreeNode "bpy.types.GreasePencilTreeNode")]

<a id="bpy.types.GreasePencil.stroke_depth_order"></a>

#### bpy.types.GreasePencil.stroke_depth_order

Defines how the strokes are ordered in 3D space (for objects not displayed ‘In Front’) (default `'2D'`)

**Type:**

Literal[[Stroke Depth Order Items](bpy_types_enum_items/stroke_depth_order_items.md#rna-enum-stroke-depth-order-items)]

<a id="bpy.types.GreasePencil.use_autolock_layers"></a>

#### bpy.types.GreasePencil.use_autolock_layers

Automatically lock all layers except the active one to avoid accidental changes (default False)

**Type:**

bool

<a id="bpy.types.GreasePencil.use_ghost_custom_colors"></a>

#### bpy.types.GreasePencil.use_ghost_custom_colors

Use custom colors for ghost frames (default False)

**Type:**

bool

<a id="bpy.types.GreasePencil.use_onion_fade"></a>

#### bpy.types.GreasePencil.use_onion_fade

Display onion keyframes with a fade in color transparency (default False)

**Type:**

bool

<a id="bpy.types.GreasePencil.use_onion_loop"></a>

#### bpy.types.GreasePencil.use_onion_loop

Display onion keyframes for looping animations (default False)

**Type:**

bool

<a id="bpy.types.GreasePencil.unit_test_compare"></a>

#### bpy.types.GreasePencil.unit_test_compare(*, grease_pencil=None, threshold=7.1526e-06)

unit_test_compare

**Parameters:**

- **grease_pencil** ([`GreasePencil`](#bpy.types.GreasePencil "bpy.types.GreasePencil") | None) – Grease Pencil to compare to (optional)
- **threshold** (float) – Threshold, Comparison tolerance threshold (in [0, inf], optional)

**Returns:**

Return value, String description of result of comparison (never None)

**Return type:**

str

<a id="bpy.types.GreasePencil.bl_rna_get_subclass"></a>

#### classmethod bpy.types.GreasePencil.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.GreasePencil.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.GreasePencil.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, ID.name, ID.name_full, ID.id_type, ID.session_uid, ID.is_evaluated, ID.original, ID.users, ID.use_fake_user, ID.use_extra_user, ID.is_embedded_data, ID.is_linked_packed, ID.is_missing, ID.is_runtime_data, ID.is_editable, ID.tag, ID.is_library_indirect, ID.library, ID.library_weak_reference, ID.asset_data, ID.override_library, ID.preview

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, ID.bl_system_properties_get, ID.rename, ID.evaluated_get, ID.copy, ID.asset_mark, ID.asset_clear, ID.asset_generate_preview, ID.override_create, ID.override_hierarchy_create, ID.user_clear, ID.user_remap, ID.make_local, ID.user_of_id, ID.animation_data_create, ID.animation_data_clear, ID.update_tag, ID.preview_ensure, ID.bl_rna_get_subclass, ID.bl_rna_get_subclass_py

<a id="references"></a>

## References

|  |  |
| --- | --- |
| - `bpy.context.annotation_data` - `bpy.context.gpencil` - `bpy.context.grease_pencil` - [`BlendData.grease_pencils`](bpy.types.BlendData.md#bpy.types.BlendData.grease_pencils "bpy.types.BlendData.grease_pencils") | - [`BlendDataGreasePencilsV3.new`](bpy.types.BlendDataGreasePencilsV3.md#bpy.types.BlendDataGreasePencilsV3.new "bpy.types.BlendDataGreasePencilsV3.new") - [`BlendDataGreasePencilsV3.remove`](bpy.types.BlendDataGreasePencilsV3.md#bpy.types.BlendDataGreasePencilsV3.remove "bpy.types.BlendDataGreasePencilsV3.remove") - [`GreasePencil.unit_test_compare`](#bpy.types.GreasePencil.unit_test_compare "bpy.types.GreasePencil.unit_test_compare") |
