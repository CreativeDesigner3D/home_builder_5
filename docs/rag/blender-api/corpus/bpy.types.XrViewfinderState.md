<!-- source: Blender Python API reference 5.2 / bpy.types.XrViewfinderState.html -->

<a id="xrviewfinderstate-bpy-struct"></a>

# XrViewfinderState(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.XrViewfinderState"></a>

### class bpy.types.XrViewfinderState(bpy_struct)

Runtime state information about the VR Location Scouting Viewfinder

<a id="bpy.types.XrViewfinderState.active_action_confirm"></a>

#### bpy.types.XrViewfinderState.active_action_confirm

Active viewfinder confirm action (default `'CONFIRM'`)

**Type:**

Literal[‘CANCEL’, ‘CONFIRM’]

<a id="bpy.types.XrViewfinderState.active_action_live"></a>

#### bpy.types.XrViewfinderState.active_action_live

Active viewfinder live action (default `'LENS'`)

**Type:**

Literal[‘LENS’, ‘DOF’, ‘FOCUS’, ‘APERTURE’]

<a id="bpy.types.XrViewfinderState.active_action_playback"></a>

#### bpy.types.XrViewfinderState.active_action_playback

Active viewfinder playback action (default `'BROWSE'`)

**Type:**

Literal[‘BROWSE’, ‘PREVIEW’, ‘DELETE’]

<a id="bpy.types.XrViewfinderState.active_mode"></a>

#### bpy.types.XrViewfinderState.active_mode

Active viewfinder mode, live or playback (default `'LIVE'`)

- `LIVE`
  Live Mode – Capture a shot using the viewfinder.
- `PLAYBACK`
  Playback Mode – Preview and playback captured shots in the viewfinder.
- `CONFIRM`
  Confirmation Mode – Confirm user action.

**Type:**

Literal[‘LIVE’, ‘PLAYBACK’, ‘CONFIRM’]

<a id="bpy.types.XrViewfinderState.capture_dof_distance"></a>

#### bpy.types.XrViewfinderState.capture_dof_distance

Viewfinder capture distance to the focus point for depth of field (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.XrViewfinderState.capture_dof_enabled"></a>

#### bpy.types.XrViewfinderState.capture_dof_enabled

Enable viewfinder capture depth of field (default False)

**Type:**

bool

<a id="bpy.types.XrViewfinderState.capture_dof_fstop"></a>

#### bpy.types.XrViewfinderState.capture_dof_fstop

Viewfinder capture f-stop ratio (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.XrViewfinderState.capture_lens_focal"></a>

#### bpy.types.XrViewfinderState.capture_lens_focal

Viewfinder capture focal length value in millimeters (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.XrViewfinderState.location"></a>

#### bpy.types.XrViewfinderState.location

Last known location of the viewfinder in world space (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0), readonly)

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.XrViewfinderState.orientation"></a>

#### bpy.types.XrViewfinderState.orientation

Last known orientation of the viewfinder in world space (array of 4 items, in [-inf, inf], default (0.0, 0.0, 0.0, 0.0), readonly)

**Type:**

[`mathutils.Quaternion`](mathutils.md#mathutils.Quaternion "mathutils.Quaternion")

<a id="bpy.types.XrViewfinderState.playback_show_active_capture_in_space_enabled"></a>

#### bpy.types.XrViewfinderState.playback_show_active_capture_in_space_enabled

Display active capture in space when in Viewfinder Playback mode (default False)

**Type:**

bool

<a id="bpy.types.XrViewfinderState.trigger_flash"></a>

#### bpy.types.XrViewfinderState.trigger_flash()

Trigger the Viewfinder flash to indicate a shot was captured

<a id="bpy.types.XrViewfinderState.trigger_focus_indicator"></a>

#### bpy.types.XrViewfinderState.trigger_focus_indicator(hit_success)

Blink the Viewfinder crosshair to indicate whether a focus action hit a target

**Parameters:**

**hit_success** (bool) – Hit success, True to blink the success color, False to blink the miss color

<a id="bpy.types.XrViewfinderState.reset_view_smoothing"></a>

#### bpy.types.XrViewfinderState.reset_view_smoothing()

Reset the Viewfinder continuous view smoothing

<a id="bpy.types.XrViewfinderState.bl_rna_get_subclass"></a>

#### classmethod bpy.types.XrViewfinderState.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.XrViewfinderState.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.XrViewfinderState.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

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
| - [`XrSessionState.viewfinder`](bpy.types.XrSessionState.md#bpy.types.XrSessionState.viewfinder "bpy.types.XrSessionState.viewfinder") |  |
