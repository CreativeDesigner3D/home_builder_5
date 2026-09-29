<!-- source: Blender Python API reference 5.2 / bpy.types.TextStrip.html -->

<a id="textstrip-effectstrip"></a>

# TextStrip(EffectStrip)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Strip`](bpy.types.Strip.md#bpy.types.Strip "bpy.types.Strip"), [`EffectStrip`](bpy.types.EffectStrip.md#bpy.types.EffectStrip "bpy.types.EffectStrip")

<a id="bpy.types.TextStrip"></a>

### class bpy.types.TextStrip(EffectStrip)

Sequence strip creating text

<a id="bpy.types.TextStrip.abs_space_line"></a>

#### bpy.types.TextStrip.abs_space_line

Distance between lines of text in pixels (in [0, 5000], default 1.0)

**Type:**

float

<a id="bpy.types.TextStrip.alignment_x"></a>

#### bpy.types.TextStrip.alignment_x

Horizontal text alignment (default `'LEFT'`)

**Type:**

Literal[‘LEFT’, ‘CENTER’, ‘RIGHT’]

<a id="bpy.types.TextStrip.anchor_x"></a>

#### bpy.types.TextStrip.anchor_x

Horizontal position of the text box relative to Location (default `'LEFT'`)

**Type:**

Literal[‘LEFT’, ‘CENTER’, ‘RIGHT’]

<a id="bpy.types.TextStrip.anchor_y"></a>

#### bpy.types.TextStrip.anchor_y

Vertical position of the text box relative to Location (default `'TOP'`)

**Type:**

Literal[‘TOP’, ‘CENTER’, ‘BOTTOM’]

<a id="bpy.types.TextStrip.box_color"></a>

#### bpy.types.TextStrip.box_color

(array of 4 items, in [0, inf], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.TextStrip.box_margin"></a>

#### bpy.types.TextStrip.box_margin

Box margin as factor of image width (in [0, 1], default 0.01)

**Type:**

float

<a id="bpy.types.TextStrip.box_roundness"></a>

#### bpy.types.TextStrip.box_roundness

Box corner radius as a factor of box height (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.TextStrip.color"></a>

#### bpy.types.TextStrip.color

Text color (array of 4 items, in [0, inf], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.TextStrip.font"></a>

#### bpy.types.TextStrip.font

Font of the text. Falls back to the UI font by default.

**Type:**

[`VectorFont`](bpy.types.VectorFont.md#bpy.types.VectorFont "bpy.types.VectorFont") | None

<a id="bpy.types.TextStrip.font_size"></a>

#### bpy.types.TextStrip.font_size

Size of the text (in [0, 2000], default 0.0)

**Type:**

float

<a id="bpy.types.TextStrip.input_count"></a>

#### bpy.types.TextStrip.input_count

(in [0, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.TextStrip.location"></a>

#### bpy.types.TextStrip.location

Location of the text (array of 2 items, in [-inf, inf], default (0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.TextStrip.outline_color"></a>

#### bpy.types.TextStrip.outline_color

(array of 4 items, in [0, inf], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.TextStrip.outline_width"></a>

#### bpy.types.TextStrip.outline_width

(in [0, 1], default 0.05)

**Type:**

float

<a id="bpy.types.TextStrip.shadow_angle"></a>

#### bpy.types.TextStrip.shadow_angle

(in [0, 6.28319], default 1.13446)

**Type:**

float

<a id="bpy.types.TextStrip.shadow_blur"></a>

#### bpy.types.TextStrip.shadow_blur

(in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.TextStrip.shadow_color"></a>

#### bpy.types.TextStrip.shadow_color

(array of 4 items, in [0, inf], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.TextStrip.shadow_offset"></a>

#### bpy.types.TextStrip.shadow_offset

(in [0, 1], default 0.04)

**Type:**

float

<a id="bpy.types.TextStrip.space_line"></a>

#### bpy.types.TextStrip.space_line

Distance between lines of text in proportion to text size (in [0, 50], default 1.0)

**Type:**

float

<a id="bpy.types.TextStrip.text"></a>

#### bpy.types.TextStrip.text

Text that will be displayed (default “”, never None)

**Type:**

str

<a id="bpy.types.TextStrip.textbox_state"></a>

#### bpy.types.TextStrip.textbox_state

Textbox state in the UI (readonly)

**Type:**

[`TextboxState`](bpy.types.TextboxState.md#bpy.types.TextboxState "bpy.types.TextboxState") | None

<a id="bpy.types.TextStrip.use_absolute_line_spacing"></a>

#### bpy.types.TextStrip.use_absolute_line_spacing

Define spacing using pixel values instead of relative scaling based on font size (default False)

**Type:**

bool

<a id="bpy.types.TextStrip.use_bold"></a>

#### bpy.types.TextStrip.use_bold

Display text as bold (default False)

**Type:**

bool

<a id="bpy.types.TextStrip.use_box"></a>

#### bpy.types.TextStrip.use_box

Display colored box behind text (default False)

**Type:**

bool

<a id="bpy.types.TextStrip.use_italic"></a>

#### bpy.types.TextStrip.use_italic

Display text as italic (default False)

**Type:**

bool

<a id="bpy.types.TextStrip.use_outline"></a>

#### bpy.types.TextStrip.use_outline

Display outline around text (default False)

**Type:**

bool

<a id="bpy.types.TextStrip.use_shadow"></a>

#### bpy.types.TextStrip.use_shadow

Display shadow behind text (default False)

**Type:**

bool

<a id="bpy.types.TextStrip.wrap_width"></a>

#### bpy.types.TextStrip.wrap_width

Word wrap width as factor, zero disables (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.TextStrip.bl_rna_get_subclass"></a>

#### classmethod bpy.types.TextStrip.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.TextStrip.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.TextStrip.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, Strip.name, Strip.type, Strip.select, Strip.select_left_handle, Strip.select_right_handle, Strip.mute, Strip.lock, Strip.frame_final_duration, Strip.duration, Strip.frame_duration, Strip.content_duration, Strip.frame_start, Strip.content_start, Strip.content_end, Strip.frame_final_start, Strip.left_handle, Strip.frame_final_end, Strip.right_handle, Strip.frame_offset_start, Strip.left_handle_offset, Strip.frame_offset_end, Strip.right_handle_offset, Strip.channel, Strip.blend_type, Strip.blend_alpha, Strip.effect_fader, Strip.use_default_fade, Strip.color_tag, Strip.modifiers, Strip.show_retiming_keys, Strip.connections, EffectStrip.use_deinterlace, EffectStrip.alpha_mode, EffectStrip.use_flip_x, EffectStrip.use_flip_y, EffectStrip.use_float, EffectStrip.use_reverse_frames, EffectStrip.color_multiply, EffectStrip.multiply_alpha, EffectStrip.color_saturation, EffectStrip.strobe, EffectStrip.transform, EffectStrip.crop, EffectStrip.use_proxy, EffectStrip.proxy

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, Strip.bl_system_properties_get, Strip.strip_elem_from_frame, Strip.swap, Strip.move_to_meta, Strip.parent_meta, Strip.invalidate_cache, Strip.split, Strip.bl_rna_get_subclass, Strip.bl_rna_get_subclass_py, EffectStrip.bl_rna_get_subclass, EffectStrip.bl_rna_get_subclass_py
