<!-- source: Blender Python API reference 5.2 / bpy.types.NlaStrip.html -->

<a id="nlastrip-bpy-struct"></a>

# NlaStrip(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.NlaStrip"></a>

### class bpy.types.NlaStrip(bpy_struct)

A container referencing an existing Action

<a id="bpy.types.NlaStrip.action"></a>

#### bpy.types.NlaStrip.action

Action referenced by this strip

**Type:**

[`Action`](bpy.types.Action.md#bpy.types.Action "bpy.types.Action") | None

<a id="bpy.types.NlaStrip.action_frame_end"></a>

#### bpy.types.NlaStrip.action_frame_end

Last frame from action to use (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.NlaStrip.action_frame_start"></a>

#### bpy.types.NlaStrip.action_frame_start

First frame from action to use (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.NlaStrip.action_slot"></a>

#### bpy.types.NlaStrip.action_slot

The slot identifies which sub-set of the Action is considered to be for this strip, and its name is used to find the right slot when assigning another Action

**Type:**

[`ActionSlot`](bpy.types.ActionSlot.md#bpy.types.ActionSlot "bpy.types.ActionSlot") | None

<a id="bpy.types.NlaStrip.action_slot_handle"></a>

#### bpy.types.NlaStrip.action_slot_handle

A number that identifies which sub-set of the Action is considered to be for this NLA strip (in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.NlaStrip.action_suitable_slots"></a>

#### bpy.types.NlaStrip.action_suitable_slots

The list of action slots suitable for this NLA strip (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`ActionSlot`](bpy.types.ActionSlot.md#bpy.types.ActionSlot "bpy.types.ActionSlot")]

<a id="bpy.types.NlaStrip.active"></a>

#### bpy.types.NlaStrip.active

NLA Strip is active (default False, readonly)

**Type:**

bool

<a id="bpy.types.NlaStrip.blend_in"></a>

#### bpy.types.NlaStrip.blend_in

Number of frames at start of strip to fade in influence (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.NlaStrip.blend_out"></a>

#### bpy.types.NlaStrip.blend_out

(in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.NlaStrip.blend_type"></a>

#### bpy.types.NlaStrip.blend_type

Method used for combining strip’s result with accumulated result (default `'REPLACE'`)

- `REPLACE`
  Replace – The strip values replace the accumulated results by amount specified by influence.
- `COMBINE`
  Combine – The strip values are combined with accumulated results by appropriately using addition, multiplication, or quaternion math, based on channel type.
- `ADD`
  Add – Weighted result of strip is added to the accumulated results.
- `SUBTRACT`
  Subtract – Weighted result of strip is removed from the accumulated results.
- `MULTIPLY`
  Multiply – Weighted result of strip is multiplied with the accumulated results.

**Type:**

Literal[‘REPLACE’, ‘COMBINE’, ‘ADD’, ‘SUBTRACT’, ‘MULTIPLY’]

<a id="bpy.types.NlaStrip.extrapolation"></a>

#### bpy.types.NlaStrip.extrapolation

Action to take for gaps past the strip extents (default `'HOLD'`)

- `NOTHING`
  Nothing – Strip has no influence past its extents.
- `HOLD`
  Hold – Hold the first frame if no previous strips in track, and always hold last frame.
- `HOLD_FORWARD`
  Hold Forward – Only hold last frame.

**Type:**

Literal[‘NOTHING’, ‘HOLD’, ‘HOLD_FORWARD’]

<a id="bpy.types.NlaStrip.fcurves"></a>

#### bpy.types.NlaStrip.fcurves

F-Curves for controlling the strip’s influence and timing (default None, readonly)

**Type:**

[`NlaStripFCurves`](bpy.types.NlaStripFCurves.md#bpy.types.NlaStripFCurves "bpy.types.NlaStripFCurves")[[`FCurve`](bpy.types.FCurve.md#bpy.types.FCurve "bpy.types.FCurve")]

<a id="bpy.types.NlaStrip.frame_end"></a>

#### bpy.types.NlaStrip.frame_end

(in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.NlaStrip.frame_end_raw"></a>

#### bpy.types.NlaStrip.frame_end_raw

Same as frame_end, except that any value can be set, including ones that create an invalid state (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.NlaStrip.frame_end_ui"></a>

#### bpy.types.NlaStrip.frame_end_ui

End frame of the NLA strip. Note: changing this value also updates the value of the strip’s repeats or its action’s end frame. If only the end frame should be changed, see the “frame_end” property instead. (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.NlaStrip.frame_start"></a>

#### bpy.types.NlaStrip.frame_start

(in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.NlaStrip.frame_start_raw"></a>

#### bpy.types.NlaStrip.frame_start_raw

Same as frame_start, except that any value can be set, including ones that create an invalid state (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.NlaStrip.frame_start_ui"></a>

#### bpy.types.NlaStrip.frame_start_ui

Start frame of the NLA strip. Note: changing this value also updates the value of the strip’s end frame. If only the start frame should be changed, see the “frame_start” property instead. (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.NlaStrip.influence"></a>

#### bpy.types.NlaStrip.influence

Amount the strip contributes to the current result (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.NlaStrip.last_slot_identifier"></a>

#### bpy.types.NlaStrip.last_slot_identifier

The identifier of the most recently assigned action slot. The slot identifies which sub-set of the Action is considered to be for this strip, and its identifier is used to find the right slot when assigning an Action. (default “”, never None)

**Type:**

str

<a id="bpy.types.NlaStrip.modifiers"></a>

#### bpy.types.NlaStrip.modifiers

Modifiers affecting all the F-Curves in the referenced Action (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`FModifier`](bpy.types.FModifier.md#bpy.types.FModifier "bpy.types.FModifier")]

<a id="bpy.types.NlaStrip.mute"></a>

#### bpy.types.NlaStrip.mute

Disable NLA Strip evaluation (default False)

**Type:**

bool

<a id="bpy.types.NlaStrip.name"></a>

#### bpy.types.NlaStrip.name

(default “”, never None)

**Type:**

str

<a id="bpy.types.NlaStrip.repeat"></a>

#### bpy.types.NlaStrip.repeat

Number of times to repeat the action range (in [0.1, 1000], default 1.0)

**Type:**

float

<a id="bpy.types.NlaStrip.scale"></a>

#### bpy.types.NlaStrip.scale

Scaling factor for action (in [0.0001, 1000], default 1.0)

**Type:**

float

<a id="bpy.types.NlaStrip.select"></a>

#### bpy.types.NlaStrip.select

NLA Strip is selected (default False)

**Type:**

bool

<a id="bpy.types.NlaStrip.strip_time"></a>

#### bpy.types.NlaStrip.strip_time

Frame of referenced Action to evaluate (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.NlaStrip.strips"></a>

#### bpy.types.NlaStrip.strips

NLA Strips that this strip acts as a container for (if it is of type Meta) (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`NlaStrip`](#bpy.types.NlaStrip "bpy.types.NlaStrip")]

<a id="bpy.types.NlaStrip.type"></a>

#### bpy.types.NlaStrip.type

Type of NLA Strip (default `'CLIP'`, readonly)

- `CLIP`
  Action Clip – NLA Strip references some Action.
- `TRANSITION`
  Transition – NLA Strip ‘transitions’ between adjacent strips.
- `META`
  Meta – NLA Strip acts as a container for adjacent strips.
- `SOUND`
  Sound Clip – NLA Strip representing a sound event for speakers.

**Type:**

Literal[‘CLIP’, ‘TRANSITION’, ‘META’, ‘SOUND’]

<a id="bpy.types.NlaStrip.use_animated_influence"></a>

#### bpy.types.NlaStrip.use_animated_influence

Influence setting is controlled by an F-Curve rather than automatically determined (default False)

**Type:**

bool

<a id="bpy.types.NlaStrip.use_animated_time"></a>

#### bpy.types.NlaStrip.use_animated_time

Strip time is controlled by an F-Curve rather than automatically determined (default False)

**Type:**

bool

<a id="bpy.types.NlaStrip.use_animated_time_cyclic"></a>

#### bpy.types.NlaStrip.use_animated_time_cyclic

Cycle the animated time within the action start and end (default False)

**Type:**

bool

<a id="bpy.types.NlaStrip.use_auto_blend"></a>

#### bpy.types.NlaStrip.use_auto_blend

Number of frames for Blending In/Out is automatically determined from overlapping strips (default False)

**Type:**

bool

<a id="bpy.types.NlaStrip.use_reverse"></a>

#### bpy.types.NlaStrip.use_reverse

NLA Strip is played back in reverse order (only when timing is automatically determined) (default False)

**Type:**

bool

<a id="bpy.types.NlaStrip.use_sync_length"></a>

#### bpy.types.NlaStrip.use_sync_length

Update range of frames referenced from action after tweaking strip and its keyframes (default False)

**Type:**

bool

<a id="bpy.types.NlaStrip.bl_rna_get_subclass"></a>

#### classmethod bpy.types.NlaStrip.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.NlaStrip.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.NlaStrip.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([type](#bpy.types.NlaStrip.type "bpy.types.NlaStrip.type") | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

[type](#bpy.types.NlaStrip.type "bpy.types.NlaStrip.type")

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
| - `bpy.context.active_nla_strip` - `bpy.context.selected_nla_strips` - [`NlaStrip.strips`](#bpy.types.NlaStrip.strips "bpy.types.NlaStrip.strips") | - [`NlaStrips.new`](bpy.types.NlaStrips.md#bpy.types.NlaStrips.new "bpy.types.NlaStrips.new") - [`NlaStrips.remove`](bpy.types.NlaStrips.md#bpy.types.NlaStrips.remove "bpy.types.NlaStrips.remove") - [`NlaTrack.strips`](bpy.types.NlaTrack.md#bpy.types.NlaTrack.strips "bpy.types.NlaTrack.strips") |
