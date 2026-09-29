<!-- source: Blender Python API reference 5.2 / bpy.types.MetaStrip.html -->

<a id="metastrip-strip"></a>

# MetaStrip(Strip)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Strip`](bpy.types.Strip.md#bpy.types.Strip "bpy.types.Strip")

<a id="bpy.types.MetaStrip"></a>

### class bpy.types.MetaStrip(Strip)

Sequence strip to group other strips as a single sequence strip

<a id="bpy.types.MetaStrip.alpha_mode"></a>

#### bpy.types.MetaStrip.alpha_mode

Representation of alpha information in the RGBA pixels (default `'STRAIGHT'`)

- `STRAIGHT`
  Straight – RGB channels in transparent pixels are unaffected by the alpha channel.
- `PREMUL`
  Premultiplied – RGB channels in transparent pixels are multiplied by the alpha channel.

**Type:**

Literal[‘STRAIGHT’, ‘PREMUL’]

<a id="bpy.types.MetaStrip.animation_offset_end"></a>

#### bpy.types.MetaStrip.animation_offset_end

Animation end offset (trim end) (in [0, inf], default 0)

Deprecated since version 5.10: removal planned in version 6.0

Replaced by ‘.content_trim_end’.

**Type:**

int

<a id="bpy.types.MetaStrip.animation_offset_start"></a>

#### bpy.types.MetaStrip.animation_offset_start

Animation start offset (trim start) (in [0, inf], default 0)

Deprecated since version 5.10: removal planned in version 6.0

Replaced by ‘.content_trim_start’.

**Type:**

int

<a id="bpy.types.MetaStrip.channels"></a>

#### bpy.types.MetaStrip.channels

(default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`SequenceTimelineChannel`](bpy.types.SequenceTimelineChannel.md#bpy.types.SequenceTimelineChannel "bpy.types.SequenceTimelineChannel")]

<a id="bpy.types.MetaStrip.color_multiply"></a>

#### bpy.types.MetaStrip.color_multiply

(in [0, 20], default 1.0)

**Type:**

float

<a id="bpy.types.MetaStrip.color_saturation"></a>

#### bpy.types.MetaStrip.color_saturation

Adjust the intensity of the input’s color (in [0, 20], default 1.0)

**Type:**

float

<a id="bpy.types.MetaStrip.content_trim_end"></a>

#### bpy.types.MetaStrip.content_trim_end

Number of frames to ignore from the end of the underlying source. The source content is trimmed, and future frames are turned into holds (in [0, inf], default 0)

**Type:**

int

<a id="bpy.types.MetaStrip.content_trim_start"></a>

#### bpy.types.MetaStrip.content_trim_start

Number of frames to ignore from the start of the underlying source. The source content is trimmed, and previous frames are turned into holds (in [0, inf], default 0)

**Type:**

int

<a id="bpy.types.MetaStrip.crop"></a>

#### bpy.types.MetaStrip.crop

(readonly)

**Type:**

[`StripCrop`](bpy.types.StripCrop.md#bpy.types.StripCrop "bpy.types.StripCrop") | None

<a id="bpy.types.MetaStrip.multiply_alpha"></a>

#### bpy.types.MetaStrip.multiply_alpha

Multiply alpha along with color channels (default False)

**Type:**

bool

<a id="bpy.types.MetaStrip.proxy"></a>

#### bpy.types.MetaStrip.proxy

(readonly)

**Type:**

[`StripProxy`](bpy.types.StripProxy.md#bpy.types.StripProxy "bpy.types.StripProxy") | None

<a id="bpy.types.MetaStrip.strips"></a>

#### bpy.types.MetaStrip.strips

Strips nested in meta strip (default None, readonly)

**Type:**

[`StripsMeta`](bpy.types.StripsMeta.md#bpy.types.StripsMeta "bpy.types.StripsMeta")[[`Strip`](bpy.types.Strip.md#bpy.types.Strip "bpy.types.Strip")]

<a id="bpy.types.MetaStrip.strobe"></a>

#### bpy.types.MetaStrip.strobe

Only display every nth frame (in [1, 30], default 0.0)

**Type:**

float

<a id="bpy.types.MetaStrip.transform"></a>

#### bpy.types.MetaStrip.transform

(readonly)

**Type:**

[`StripTransform`](bpy.types.StripTransform.md#bpy.types.StripTransform "bpy.types.StripTransform") | None

<a id="bpy.types.MetaStrip.use_deinterlace"></a>

#### bpy.types.MetaStrip.use_deinterlace

Remove fields from video movies (default False)

**Type:**

bool

<a id="bpy.types.MetaStrip.use_flip_x"></a>

#### bpy.types.MetaStrip.use_flip_x

Flip on the X axis (default False)

**Type:**

bool

<a id="bpy.types.MetaStrip.use_flip_y"></a>

#### bpy.types.MetaStrip.use_flip_y

Flip on the Y axis (default False)

**Type:**

bool

<a id="bpy.types.MetaStrip.use_float"></a>

#### bpy.types.MetaStrip.use_float

Convert input to float data (default False)

**Type:**

bool

<a id="bpy.types.MetaStrip.use_proxy"></a>

#### bpy.types.MetaStrip.use_proxy

Use a preview proxy for this strip (default False)

**Type:**

bool

<a id="bpy.types.MetaStrip.use_reverse_frames"></a>

#### bpy.types.MetaStrip.use_reverse_frames

Reverse frame order (default False)

**Type:**

bool

<a id="bpy.types.MetaStrip.volume"></a>

#### bpy.types.MetaStrip.volume

Playback volume of the sound (in [0, 100], default 1.0)

**Type:**

float

<a id="bpy.types.MetaStrip.separate"></a>

#### bpy.types.MetaStrip.separate()

Separate meta

<a id="bpy.types.MetaStrip.bl_rna_get_subclass"></a>

#### classmethod bpy.types.MetaStrip.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.MetaStrip.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.MetaStrip.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, Strip.name, Strip.type, Strip.select, Strip.select_left_handle, Strip.select_right_handle, Strip.mute, Strip.lock, Strip.frame_final_duration, Strip.duration, Strip.frame_duration, Strip.content_duration, Strip.frame_start, Strip.content_start, Strip.content_end, Strip.frame_final_start, Strip.left_handle, Strip.frame_final_end, Strip.right_handle, Strip.frame_offset_start, Strip.left_handle_offset, Strip.frame_offset_end, Strip.right_handle_offset, Strip.channel, Strip.blend_type, Strip.blend_alpha, Strip.effect_fader, Strip.use_default_fade, Strip.color_tag, Strip.modifiers, Strip.show_retiming_keys, Strip.connections

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, Strip.bl_system_properties_get, Strip.strip_elem_from_frame, Strip.swap, Strip.move_to_meta, Strip.parent_meta, Strip.invalidate_cache, Strip.split, Strip.bl_rna_get_subclass, Strip.bl_rna_get_subclass_py
