<!-- source: Blender Python API reference 5.2 / bpy.types.GreasePencilTimeModifier.html -->

<a id="greasepenciltimemodifier-modifier"></a>

# GreasePencilTimeModifier(Modifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Modifier`](bpy.types.Modifier.md#bpy.types.Modifier "bpy.types.Modifier")

<a id="bpy.types.GreasePencilTimeModifier"></a>

### class bpy.types.GreasePencilTimeModifier(Modifier)

Offset keyframes

<a id="bpy.types.GreasePencilTimeModifier.frame_end"></a>

#### bpy.types.GreasePencilTimeModifier.frame_end

Final frame of the range (in [-1048574, 1048574], default 250)

**Type:**

int

<a id="bpy.types.GreasePencilTimeModifier.frame_scale"></a>

#### bpy.types.GreasePencilTimeModifier.frame_scale

Evaluation time in seconds (in [0.001, 100], default 1.0)

**Type:**

float

<a id="bpy.types.GreasePencilTimeModifier.frame_start"></a>

#### bpy.types.GreasePencilTimeModifier.frame_start

First frame of the range (in [-1048574, 1048574], default 1)

**Type:**

int

<a id="bpy.types.GreasePencilTimeModifier.invert_layer_filter"></a>

#### bpy.types.GreasePencilTimeModifier.invert_layer_filter

Invert layer filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilTimeModifier.invert_layer_pass_filter"></a>

#### bpy.types.GreasePencilTimeModifier.invert_layer_pass_filter

Invert layer pass filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilTimeModifier.layer_pass_filter"></a>

#### bpy.types.GreasePencilTimeModifier.layer_pass_filter

Layer pass filter (in [0, 100], default 0)

**Type:**

int

<a id="bpy.types.GreasePencilTimeModifier.mode"></a>

#### bpy.types.GreasePencilTimeModifier.mode

(default `'NORMAL'`)

- `NORMAL`
  Regular – Apply offset in usual animation direction.
- `REVERSE`
  Reverse – Apply offset in reverse animation direction.
- `FIX`
  Fixed Frame – Keep frame and do not change with time.
- `PINGPONG`
  Ping Pong – Loop back and forth starting in reverse.
- `CHAIN`
  Chain – List of chained animation segments.

**Type:**

Literal[‘NORMAL’, ‘REVERSE’, ‘FIX’, ‘PINGPONG’, ‘CHAIN’]

<a id="bpy.types.GreasePencilTimeModifier.offset"></a>

#### bpy.types.GreasePencilTimeModifier.offset

Number of frames to offset original keyframe number or frame to fix (in [-32768, 32767], default 1)

**Type:**

int

<a id="bpy.types.GreasePencilTimeModifier.open_custom_range_panel"></a>

#### bpy.types.GreasePencilTimeModifier.open_custom_range_panel

(default False)

**Type:**

bool

<a id="bpy.types.GreasePencilTimeModifier.open_influence_panel"></a>

#### bpy.types.GreasePencilTimeModifier.open_influence_panel

(default False)

**Type:**

bool

<a id="bpy.types.GreasePencilTimeModifier.segment_active_index"></a>

#### bpy.types.GreasePencilTimeModifier.segment_active_index

Active index in the segment list (in [0, inf], default 0)

**Type:**

int

<a id="bpy.types.GreasePencilTimeModifier.segments"></a>

#### bpy.types.GreasePencilTimeModifier.segments

(default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`GreasePencilTimeModifierSegment`](bpy.types.GreasePencilTimeModifierSegment.md#bpy.types.GreasePencilTimeModifierSegment "bpy.types.GreasePencilTimeModifierSegment")]

<a id="bpy.types.GreasePencilTimeModifier.tree_node_filter"></a>

#### bpy.types.GreasePencilTimeModifier.tree_node_filter

Layer name (default “”, never None)

**Type:**

str

<a id="bpy.types.GreasePencilTimeModifier.use_custom_frame_range"></a>

#### bpy.types.GreasePencilTimeModifier.use_custom_frame_range

Define a custom range of frames to use in modifier (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilTimeModifier.use_keep_loop"></a>

#### bpy.types.GreasePencilTimeModifier.use_keep_loop

Retiming end frames and move to start of animation to keep loop (default True)

**Type:**

bool

<a id="bpy.types.GreasePencilTimeModifier.use_layer_group_filter"></a>

#### bpy.types.GreasePencilTimeModifier.use_layer_group_filter

Filter by layer group name (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilTimeModifier.use_layer_pass_filter"></a>

#### bpy.types.GreasePencilTimeModifier.use_layer_pass_filter

Use layer pass filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilTimeModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.GreasePencilTimeModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.GreasePencilTimeModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.GreasePencilTimeModifier.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, Modifier.name, Modifier.type, Modifier.show_viewport, Modifier.show_render, Modifier.show_in_editmode, Modifier.show_on_cage, Modifier.show_expanded, Modifier.is_active, Modifier.use_pin_to_last, Modifier.is_override_data, Modifier.use_apply_on_spline, Modifier.execution_time, Modifier.persistent_uid

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, Modifier.bl_rna_get_subclass, Modifier.bl_rna_get_subclass_py
