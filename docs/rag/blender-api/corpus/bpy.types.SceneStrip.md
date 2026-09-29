<!-- source: Blender Python API reference 5.2 / bpy.types.SceneStrip.html -->

<a id="scenestrip-strip"></a>

# SceneStrip(Strip)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Strip`](bpy.types.Strip.md#bpy.types.Strip "bpy.types.Strip")

<a id="bpy.types.SceneStrip"></a>

### class bpy.types.SceneStrip(Strip)

Sequence strip using the rendered image of a scene

<a id="bpy.types.SceneStrip.alpha_mode"></a>

#### bpy.types.SceneStrip.alpha_mode

Representation of alpha information in the RGBA pixels (default `'STRAIGHT'`)

- `STRAIGHT`
  Straight – RGB channels in transparent pixels are unaffected by the alpha channel.
- `PREMUL`
  Premultiplied – RGB channels in transparent pixels are multiplied by the alpha channel.

**Type:**

Literal[‘STRAIGHT’, ‘PREMUL’]

<a id="bpy.types.SceneStrip.animation_offset_end"></a>

#### bpy.types.SceneStrip.animation_offset_end

Animation end offset (trim end) (in [0, inf], default 0)

Deprecated since version 5.10: removal planned in version 6.0

Replaced by ‘.content_trim_end’.

**Type:**

int

<a id="bpy.types.SceneStrip.animation_offset_start"></a>

#### bpy.types.SceneStrip.animation_offset_start

Animation start offset (trim start) (in [0, inf], default 0)

Deprecated since version 5.10: removal planned in version 6.0

Replaced by ‘.content_trim_start’.

**Type:**

int

<a id="bpy.types.SceneStrip.color_multiply"></a>

#### bpy.types.SceneStrip.color_multiply

(in [0, 20], default 1.0)

**Type:**

float

<a id="bpy.types.SceneStrip.color_saturation"></a>

#### bpy.types.SceneStrip.color_saturation

Adjust the intensity of the input’s color (in [0, 20], default 1.0)

**Type:**

float

<a id="bpy.types.SceneStrip.content_trim_end"></a>

#### bpy.types.SceneStrip.content_trim_end

Number of frames to ignore from the end of the underlying source. The source content is trimmed, and future frames are turned into holds (in [0, inf], default 0)

**Type:**

int

<a id="bpy.types.SceneStrip.content_trim_start"></a>

#### bpy.types.SceneStrip.content_trim_start

Number of frames to ignore from the start of the underlying source. The source content is trimmed, and previous frames are turned into holds (in [0, inf], default 0)

**Type:**

int

<a id="bpy.types.SceneStrip.crop"></a>

#### bpy.types.SceneStrip.crop

(readonly)

**Type:**

[`StripCrop`](bpy.types.StripCrop.md#bpy.types.StripCrop "bpy.types.StripCrop") | None

<a id="bpy.types.SceneStrip.fps"></a>

#### bpy.types.SceneStrip.fps

Frames per second (in [-inf, inf], default 0.0, readonly)

**Type:**

float

<a id="bpy.types.SceneStrip.multiply_alpha"></a>

#### bpy.types.SceneStrip.multiply_alpha

Multiply alpha along with color channels (default False)

**Type:**

bool

<a id="bpy.types.SceneStrip.proxy"></a>

#### bpy.types.SceneStrip.proxy

(readonly)

**Type:**

[`StripProxy`](bpy.types.StripProxy.md#bpy.types.StripProxy "bpy.types.StripProxy") | None

<a id="bpy.types.SceneStrip.retiming_keys"></a>

#### bpy.types.SceneStrip.retiming_keys

(default None, readonly)

**Type:**

[`RetimingKeys`](bpy.types.RetimingKeys.md#bpy.types.RetimingKeys "bpy.types.RetimingKeys")[[`RetimingKey`](bpy.types.RetimingKey.md#bpy.types.RetimingKey "bpy.types.RetimingKey")]

<a id="bpy.types.SceneStrip.scene"></a>

#### bpy.types.SceneStrip.scene

Scene that this strip uses

**Type:**

[`Scene`](bpy.types.Scene.md#bpy.types.Scene "bpy.types.Scene") | None

<a id="bpy.types.SceneStrip.scene_camera"></a>

#### bpy.types.SceneStrip.scene_camera

Override the scene’s active camera

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.SceneStrip.scene_input"></a>

#### bpy.types.SceneStrip.scene_input

Input type to use for the Scene strip (default `'CAMERA'`)

- `CAMERA`
  Camera – Use the Scene’s 3D camera as input.
- `SEQUENCER`
  Sequencer – Use the Scene’s Sequencer timeline as input.

**Type:**

Literal[‘CAMERA’, ‘SEQUENCER’]

<a id="bpy.types.SceneStrip.strobe"></a>

#### bpy.types.SceneStrip.strobe

Only display every nth frame (in [1, 30], default 0.0)

**Type:**

float

<a id="bpy.types.SceneStrip.transform"></a>

#### bpy.types.SceneStrip.transform

(readonly)

**Type:**

[`StripTransform`](bpy.types.StripTransform.md#bpy.types.StripTransform "bpy.types.StripTransform") | None

<a id="bpy.types.SceneStrip.use_annotations"></a>

#### bpy.types.SceneStrip.use_annotations

Show Annotations in OpenGL previews (default True)

**Type:**

bool

<a id="bpy.types.SceneStrip.use_deinterlace"></a>

#### bpy.types.SceneStrip.use_deinterlace

Remove fields from video movies (default False)

**Type:**

bool

<a id="bpy.types.SceneStrip.use_flip_x"></a>

#### bpy.types.SceneStrip.use_flip_x

Flip on the X axis (default False)

**Type:**

bool

<a id="bpy.types.SceneStrip.use_flip_y"></a>

#### bpy.types.SceneStrip.use_flip_y

Flip on the Y axis (default False)

**Type:**

bool

<a id="bpy.types.SceneStrip.use_float"></a>

#### bpy.types.SceneStrip.use_float

Convert input to float data (default False)

**Type:**

bool

<a id="bpy.types.SceneStrip.use_proxy"></a>

#### bpy.types.SceneStrip.use_proxy

Use a preview proxy for this strip (default False)

**Type:**

bool

<a id="bpy.types.SceneStrip.use_reverse_frames"></a>

#### bpy.types.SceneStrip.use_reverse_frames

Reverse frame order (default False)

**Type:**

bool

<a id="bpy.types.SceneStrip.view_layer"></a>

#### bpy.types.SceneStrip.view_layer

View Layer of the scene to render (uses the default if unset)

**Type:**

[`ViewLayer`](bpy.types.ViewLayer.md#bpy.types.ViewLayer "bpy.types.ViewLayer") | None

<a id="bpy.types.SceneStrip.volume"></a>

#### bpy.types.SceneStrip.volume

Playback volume of the sound (in [0, 100], default 1.0)

**Type:**

float

<a id="bpy.types.SceneStrip.bl_rna_get_subclass"></a>

#### classmethod bpy.types.SceneStrip.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.SceneStrip.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.SceneStrip.bl_rna_get_subclass_py(id, default=None, /)

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
