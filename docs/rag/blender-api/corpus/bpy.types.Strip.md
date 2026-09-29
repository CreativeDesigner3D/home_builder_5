<!-- source: Blender Python API reference 5.2 / bpy.types.Strip.html -->

<a id="strip-bpy-struct"></a>

# Strip(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

Subclasses

- [EffectStrip(Strip)](bpy.types.EffectStrip.md)
- [ImageStrip(Strip)](bpy.types.ImageStrip.md)
- [MaskStrip(Strip)](bpy.types.MaskStrip.md)
- [MetaStrip(Strip)](bpy.types.MetaStrip.md)
- [MovieClipStrip(Strip)](bpy.types.MovieClipStrip.md)
- [MovieStrip(Strip)](bpy.types.MovieStrip.md)
- [SceneStrip(Strip)](bpy.types.SceneStrip.md)
- [SoundStrip(Strip)](bpy.types.SoundStrip.md)

<a id="bpy.types.Strip"></a>

### class bpy.types.Strip(bpy_struct)

A single container for content in the Video Sequence Editor

<a id="bpy.types.Strip.blend_alpha"></a>

#### bpy.types.Strip.blend_alpha

Percentage of how much the strip’s colors affect other strips (in [0, 1], default 1.0)

**Type:**

float

<a id="bpy.types.Strip.blend_type"></a>

#### bpy.types.Strip.blend_type

Method for controlling how the strip combines with other strips (default `'ALPHA_OVER'`)

**Type:**

Literal[‘REPLACE’, ‘CROSS’, ‘DARKEN’, ‘MULTIPLY’, ‘BURN’, ‘LINEAR_BURN’, ‘LIGHTEN’, ‘SCREEN’, ‘DODGE’, ‘ADD’, ‘OVERLAY’, ‘SOFT_LIGHT’, ‘HARD_LIGHT’, ‘VIVID_LIGHT’, ‘LINEAR_LIGHT’, ‘PIN_LIGHT’, ‘DIFFERENCE’, ‘EXCLUSION’, ‘SUBTRACT’, ‘HUE’, ‘SATURATION’, ‘COLOR’, ‘VALUE’, ‘ALPHA_OVER’, ‘ALPHA_UNDER’, ‘GAMMA_CROSS’]

<a id="bpy.types.Strip.channel"></a>

#### bpy.types.Strip.channel

Vertical position of the strip (in [1, 128], default 0)

**Type:**

int

<a id="bpy.types.Strip.color_tag"></a>

#### bpy.types.Strip.color_tag

Color tag for a strip (default `'COLOR_01'`)

**Type:**

Literal[[Strip Color Items](bpy_types_enum_items/strip_color_items.md#rna-enum-strip-color-items)]

<a id="bpy.types.Strip.connections"></a>

#### bpy.types.Strip.connections

Other strips currently connected to this strip (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`Strip`](#bpy.types.Strip "bpy.types.Strip")]

<a id="bpy.types.Strip.content_duration"></a>

#### bpy.types.Strip.content_duration

Length of the underlying strip source in frames, excluding handles (in [1, 1048574], default 0, readonly)

**Type:**

int

<a id="bpy.types.Strip.content_end"></a>

#### bpy.types.Strip.content_end

Timeline frame where underlying strip source ends (in [-inf, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.Strip.content_start"></a>

#### bpy.types.Strip.content_start

Timeline frame where underlying strip source begins (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.Strip.duration"></a>

#### bpy.types.Strip.duration

Length of the strip in frames from left handle to right handle (in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.Strip.effect_fader"></a>

#### bpy.types.Strip.effect_fader

Custom fade value (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.Strip.frame_duration"></a>

#### bpy.types.Strip.frame_duration

The length of the contents of this strip before the handles are applied (in [1, 1048574], default 0, readonly)

Deprecated since version 5.10: removal planned in version 6.0

Replaced by ‘.content_duration’.

**Type:**

int

<a id="bpy.types.Strip.frame_final_duration"></a>

#### bpy.types.Strip.frame_final_duration

The length of the contents of this strip after the handles are applied (in [-inf, inf], default 0)

Deprecated since version 5.10: removal planned in version 6.0

Replaced by ‘.duration’.

**Type:**

int

<a id="bpy.types.Strip.frame_final_end"></a>

#### bpy.types.Strip.frame_final_end

End frame displayed in the sequence editor after offsets are applied (in [-inf, inf], default 0)

Deprecated since version 5.10: removal planned in version 6.0

Replaced by ‘.right_handle’.

**Type:**

int

<a id="bpy.types.Strip.frame_final_start"></a>

#### bpy.types.Strip.frame_final_start

Start frame displayed in the sequence editor after offsets are applied, setting this is equivalent to moving the handle, not the actual start frame (in [-inf, inf], default 0)

Deprecated since version 5.10: removal planned in version 6.0

Replaced by ‘.left_handle’.

**Type:**

int

<a id="bpy.types.Strip.frame_offset_end"></a>

#### bpy.types.Strip.frame_offset_end

Offset from the end of the strip in frames (in [-inf, inf], default 0.0)

Deprecated since version 5.10: removal planned in version 6.0

Replaced by ‘.right_handle_offset’.

**Type:**

float

<a id="bpy.types.Strip.frame_offset_start"></a>

#### bpy.types.Strip.frame_offset_start

Offset from the start of the strip in frames (in [-inf, inf], default 0.0)

Deprecated since version 5.10: removal planned in version 6.0

Replaced by ‘.left_handle_offset’.

**Type:**

float

<a id="bpy.types.Strip.frame_start"></a>

#### bpy.types.Strip.frame_start

X position where the strip begins (in [-inf, inf], default 0.0)

Deprecated since version 5.10: removal planned in version 6.0

Replaced by ‘.content_start’.

**Type:**

float

<a id="bpy.types.Strip.left_handle"></a>

#### bpy.types.Strip.left_handle

Timeline frame of the left handle and the start frame of the strip (in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.Strip.left_handle_offset"></a>

#### bpy.types.Strip.left_handle_offset

Rightward frame offset of the left handle from the start of the strip content (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.Strip.lock"></a>

#### bpy.types.Strip.lock

Lock strip so that it cannot be transformed (default False)

**Type:**

bool

<a id="bpy.types.Strip.modifiers"></a>

#### bpy.types.Strip.modifiers

Modifiers affecting this strip (default None, readonly)

**Type:**

[`StripModifiers`](bpy.types.StripModifiers.md#bpy.types.StripModifiers "bpy.types.StripModifiers")[[`StripModifier`](bpy.types.StripModifier.md#bpy.types.StripModifier "bpy.types.StripModifier")]

<a id="bpy.types.Strip.mute"></a>

#### bpy.types.Strip.mute

Disable strip so that it does not contribute any output (default False)

**Type:**

bool

<a id="bpy.types.Strip.name"></a>

#### bpy.types.Strip.name

(default “”, never None)

**Type:**

str

<a id="bpy.types.Strip.right_handle"></a>

#### bpy.types.Strip.right_handle

Timeline frame of the right handle, which is the first frame where the strip no longer contributes to the output (in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.Strip.right_handle_offset"></a>

#### bpy.types.Strip.right_handle_offset

Leftward frame offset of the right handle from the end of the strip content (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.Strip.select"></a>

#### bpy.types.Strip.select

Whether the strip is selected (default False)

**Type:**

bool

<a id="bpy.types.Strip.select_left_handle"></a>

#### bpy.types.Strip.select_left_handle

Whether the left handle is selected (default False)

**Type:**

bool

<a id="bpy.types.Strip.select_right_handle"></a>

#### bpy.types.Strip.select_right_handle

Whether the right handle is selected (default False)

**Type:**

bool

<a id="bpy.types.Strip.show_retiming_keys"></a>

#### bpy.types.Strip.show_retiming_keys

Show retiming keys, so they can be moved (default False)

**Type:**

bool

<a id="bpy.types.Strip.type"></a>

#### bpy.types.Strip.type

(default `'IMAGE'`, readonly)

**Type:**

Literal[‘IMAGE’, ‘META’, ‘SCENE’, ‘MOVIE’, ‘MOVIECLIP’, ‘MASK’, ‘SOUND’, ‘CROSS’, ‘ADD’, ‘SUBTRACT’, ‘ALPHA_OVER’, ‘ALPHA_UNDER’, ‘GAMMA_CROSS’, ‘COMPOSITOR’, ‘MULTIPLY’, ‘WIPE’, ‘GLOW’, ‘COLOR’, ‘SPEED’, ‘MULTICAM’, ‘ADJUSTMENT’, ‘GAUSSIAN_BLUR’, ‘TEXT’, ‘COLORMIX’]

<a id="bpy.types.Strip.use_default_fade"></a>

#### bpy.types.Strip.use_default_fade

Fade effect using the built-in default (usually makes the transition as long as the effect strip) (default False)

**Type:**

bool

<a id="bpy.types.Strip.bl_system_properties_get"></a>

#### bpy.types.Strip.bl_system_properties_get(*, do_create=False)

DEBUG ONLY. Internal access to runtime-defined RNA data storage, intended solely for testing and debugging purposes. Do not access it in regular scripting work, and in particular, do not assume that it contains writable data

**Parameters:**

**do_create** (bool) – Ensure that system properties are created if they do not exist yet (optional)

**Returns:**

The system properties root container, or None if there are no system properties stored in this data yet, and its creation was not requested

**Return type:**

[`PropertyGroup`](bpy.types.PropertyGroup.md#bpy.types.PropertyGroup "bpy.types.PropertyGroup")

<a id="bpy.types.Strip.strip_elem_from_frame"></a>

#### bpy.types.Strip.strip_elem_from_frame(frame)

Return the strip element from a given frame or None

**Parameters:**

**frame** (int) – Frame, The frame to get the strip element from (in [-1048574, 1048574])

**Returns:**

strip element of the current frame

**Return type:**

[`StripElement`](bpy.types.StripElement.md#bpy.types.StripElement "bpy.types.StripElement")

<a id="bpy.types.Strip.swap"></a>

#### bpy.types.Strip.swap(other)

Swap the position of this strip with another

**Parameters:**

**other** ([`Strip`](#bpy.types.Strip "bpy.types.Strip") | None) – Other, Other strip to swap with (never None)

<a id="bpy.types.Strip.move_to_meta"></a>

#### bpy.types.Strip.move_to_meta(meta_sequence)

Move this strip into a meta Strip

**Parameters:**

**meta_sequence** ([`Strip`](#bpy.types.Strip "bpy.types.Strip") | None) – Destination Meta Strip, Meta to move the strip into (never None)

<a id="bpy.types.Strip.parent_meta"></a>

#### bpy.types.Strip.parent_meta()

Returns parent meta Strip

**Returns:**

Parent meta strip

**Return type:**

[`Strip`](#bpy.types.Strip "bpy.types.Strip")

<a id="bpy.types.Strip.invalidate_cache"></a>

#### bpy.types.Strip.invalidate_cache(type)

Invalidate cached images for strip and all dependent strips

**Parameters:**

**type** (Literal['RAW', 'COMPOSITE']) – Type, Cache Type (never None)

<a id="bpy.types.Strip.split"></a>

#### bpy.types.Strip.split(frame, split_method, *, ignore_connections=False)

Split Strip

**Parameters:**

- **frame** (int) – Frame where to split the strip (in [-inf, inf])
- **split_method** (Literal['SOFT', 'HARD']) – Split Method, The type of split operation to perform on strips (never None)
- **ignore_connections** (bool) – Don’t propagate split to connected strips (optional)

**Returns:**

Right side Strip

**Return type:**

[`Strip`](#bpy.types.Strip "bpy.types.Strip")

<a id="bpy.types.Strip.bl_rna_get_subclass"></a>

#### classmethod bpy.types.Strip.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.Strip.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.Strip.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([type](#bpy.types.Strip.type "bpy.types.Strip.type") | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

[type](#bpy.types.Strip.type "bpy.types.Strip.type")

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values

<a id="references"></a>

## References

|  |  |
| --- | --- |
| - `bpy.context.active_strip` - `bpy.context.selected_editable_strips` - `bpy.context.selected_strips` - `bpy.context.strip` - `bpy.context.strips` - [`AddStrip.input_1`](bpy.types.AddStrip.md#bpy.types.AddStrip.input_1 "bpy.types.AddStrip.input_1") - [`AddStrip.input_2`](bpy.types.AddStrip.md#bpy.types.AddStrip.input_2 "bpy.types.AddStrip.input_2") - [`AlphaOverStrip.input_1`](bpy.types.AlphaOverStrip.md#bpy.types.AlphaOverStrip.input_1 "bpy.types.AlphaOverStrip.input_1") - [`AlphaOverStrip.input_2`](bpy.types.AlphaOverStrip.md#bpy.types.AlphaOverStrip.input_2 "bpy.types.AlphaOverStrip.input_2") - [`AlphaUnderStrip.input_1`](bpy.types.AlphaUnderStrip.md#bpy.types.AlphaUnderStrip.input_1 "bpy.types.AlphaUnderStrip.input_1") - [`AlphaUnderStrip.input_2`](bpy.types.AlphaUnderStrip.md#bpy.types.AlphaUnderStrip.input_2 "bpy.types.AlphaUnderStrip.input_2") - [`ColorMixStrip.input_1`](bpy.types.ColorMixStrip.md#bpy.types.ColorMixStrip.input_1 "bpy.types.ColorMixStrip.input_1") - [`ColorMixStrip.input_2`](bpy.types.ColorMixStrip.md#bpy.types.ColorMixStrip.input_2 "bpy.types.ColorMixStrip.input_2") - [`CompositorStrip.input_1`](bpy.types.CompositorStrip.md#bpy.types.CompositorStrip.input_1 "bpy.types.CompositorStrip.input_1") - [`CompositorStrip.input_2`](bpy.types.CompositorStrip.md#bpy.types.CompositorStrip.input_2 "bpy.types.CompositorStrip.input_2") - [`CrossStrip.input_1`](bpy.types.CrossStrip.md#bpy.types.CrossStrip.input_1 "bpy.types.CrossStrip.input_1") - [`CrossStrip.input_2`](bpy.types.CrossStrip.md#bpy.types.CrossStrip.input_2 "bpy.types.CrossStrip.input_2") - [`GammaCrossStrip.input_1`](bpy.types.GammaCrossStrip.md#bpy.types.GammaCrossStrip.input_1 "bpy.types.GammaCrossStrip.input_1") - [`GammaCrossStrip.input_2`](bpy.types.GammaCrossStrip.md#bpy.types.GammaCrossStrip.input_2 "bpy.types.GammaCrossStrip.input_2") - [`GaussianBlurStrip.input_1`](bpy.types.GaussianBlurStrip.md#bpy.types.GaussianBlurStrip.input_1 "bpy.types.GaussianBlurStrip.input_1") - [`GlowStrip.input_1`](bpy.types.GlowStrip.md#bpy.types.GlowStrip.input_1 "bpy.types.GlowStrip.input_1") - [`MetaStrip.strips`](bpy.types.MetaStrip.md#bpy.types.MetaStrip.strips "bpy.types.MetaStrip.strips") - [`MultiplyStrip.input_1`](bpy.types.MultiplyStrip.md#bpy.types.MultiplyStrip.input_1 "bpy.types.MultiplyStrip.input_1") - [`MultiplyStrip.input_2`](bpy.types.MultiplyStrip.md#bpy.types.MultiplyStrip.input_2 "bpy.types.MultiplyStrip.input_2") - [`SequenceEditor.active_strip`](bpy.types.SequenceEditor.md#bpy.types.SequenceEditor.active_strip "bpy.types.SequenceEditor.active_strip") - [`SequenceEditor.display_stack`](bpy.types.SequenceEditor.md#bpy.types.SequenceEditor.display_stack "bpy.types.SequenceEditor.display_stack") - [`SequenceEditor.meta_stack`](bpy.types.SequenceEditor.md#bpy.types.SequenceEditor.meta_stack "bpy.types.SequenceEditor.meta_stack") - [`SequenceEditor.strips`](bpy.types.SequenceEditor.md#bpy.types.SequenceEditor.strips "bpy.types.SequenceEditor.strips") - [`SequenceEditor.strips_all`](bpy.types.SequenceEditor.md#bpy.types.SequenceEditor.strips_all "bpy.types.SequenceEditor.strips_all") - [`SpeedControlStrip.input_1`](bpy.types.SpeedControlStrip.md#bpy.types.SpeedControlStrip.input_1 "bpy.types.SpeedControlStrip.input_1") - [`Strip.connections`](#bpy.types.Strip.connections "bpy.types.Strip.connections") | - [`Strip.move_to_meta`](#bpy.types.Strip.move_to_meta "bpy.types.Strip.move_to_meta") - [`Strip.parent_meta`](#bpy.types.Strip.parent_meta "bpy.types.Strip.parent_meta") - [`Strip.split`](#bpy.types.Strip.split "bpy.types.Strip.split") - [`Strip.swap`](#bpy.types.Strip.swap "bpy.types.Strip.swap") - [`StripModifier.input_mask_strip`](bpy.types.StripModifier.md#bpy.types.StripModifier.input_mask_strip "bpy.types.StripModifier.input_mask_strip") - [`StripsMeta.new_clip`](bpy.types.StripsMeta.md#bpy.types.StripsMeta.new_clip "bpy.types.StripsMeta.new_clip") - [`StripsMeta.new_effect`](bpy.types.StripsMeta.md#bpy.types.StripsMeta.new_effect "bpy.types.StripsMeta.new_effect") - [`StripsMeta.new_effect`](bpy.types.StripsMeta.md#bpy.types.StripsMeta.new_effect "bpy.types.StripsMeta.new_effect") - [`StripsMeta.new_effect`](bpy.types.StripsMeta.md#bpy.types.StripsMeta.new_effect "bpy.types.StripsMeta.new_effect") - [`StripsMeta.new_image`](bpy.types.StripsMeta.md#bpy.types.StripsMeta.new_image "bpy.types.StripsMeta.new_image") - [`StripsMeta.new_mask`](bpy.types.StripsMeta.md#bpy.types.StripsMeta.new_mask "bpy.types.StripsMeta.new_mask") - [`StripsMeta.new_meta`](bpy.types.StripsMeta.md#bpy.types.StripsMeta.new_meta "bpy.types.StripsMeta.new_meta") - [`StripsMeta.new_movie`](bpy.types.StripsMeta.md#bpy.types.StripsMeta.new_movie "bpy.types.StripsMeta.new_movie") - [`StripsMeta.new_scene`](bpy.types.StripsMeta.md#bpy.types.StripsMeta.new_scene "bpy.types.StripsMeta.new_scene") - [`StripsMeta.new_sound`](bpy.types.StripsMeta.md#bpy.types.StripsMeta.new_sound "bpy.types.StripsMeta.new_sound") - [`StripsMeta.remove`](bpy.types.StripsMeta.md#bpy.types.StripsMeta.remove "bpy.types.StripsMeta.remove") - [`StripsTopLevel.new_clip`](bpy.types.StripsTopLevel.md#bpy.types.StripsTopLevel.new_clip "bpy.types.StripsTopLevel.new_clip") - [`StripsTopLevel.new_effect`](bpy.types.StripsTopLevel.md#bpy.types.StripsTopLevel.new_effect "bpy.types.StripsTopLevel.new_effect") - [`StripsTopLevel.new_effect`](bpy.types.StripsTopLevel.md#bpy.types.StripsTopLevel.new_effect "bpy.types.StripsTopLevel.new_effect") - [`StripsTopLevel.new_effect`](bpy.types.StripsTopLevel.md#bpy.types.StripsTopLevel.new_effect "bpy.types.StripsTopLevel.new_effect") - [`StripsTopLevel.new_image`](bpy.types.StripsTopLevel.md#bpy.types.StripsTopLevel.new_image "bpy.types.StripsTopLevel.new_image") - [`StripsTopLevel.new_mask`](bpy.types.StripsTopLevel.md#bpy.types.StripsTopLevel.new_mask "bpy.types.StripsTopLevel.new_mask") - [`StripsTopLevel.new_meta`](bpy.types.StripsTopLevel.md#bpy.types.StripsTopLevel.new_meta "bpy.types.StripsTopLevel.new_meta") - [`StripsTopLevel.new_movie`](bpy.types.StripsTopLevel.md#bpy.types.StripsTopLevel.new_movie "bpy.types.StripsTopLevel.new_movie") - [`StripsTopLevel.new_scene`](bpy.types.StripsTopLevel.md#bpy.types.StripsTopLevel.new_scene "bpy.types.StripsTopLevel.new_scene") - [`StripsTopLevel.new_sound`](bpy.types.StripsTopLevel.md#bpy.types.StripsTopLevel.new_sound "bpy.types.StripsTopLevel.new_sound") - [`StripsTopLevel.remove`](bpy.types.StripsTopLevel.md#bpy.types.StripsTopLevel.remove "bpy.types.StripsTopLevel.remove") - [`SubtractStrip.input_1`](bpy.types.SubtractStrip.md#bpy.types.SubtractStrip.input_1 "bpy.types.SubtractStrip.input_1") - [`SubtractStrip.input_2`](bpy.types.SubtractStrip.md#bpy.types.SubtractStrip.input_2 "bpy.types.SubtractStrip.input_2") - [`WipeStrip.input_1`](bpy.types.WipeStrip.md#bpy.types.WipeStrip.input_1 "bpy.types.WipeStrip.input_1") - [`WipeStrip.input_2`](bpy.types.WipeStrip.md#bpy.types.WipeStrip.input_2 "bpy.types.WipeStrip.input_2") |
