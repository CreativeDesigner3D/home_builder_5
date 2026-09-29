<!-- source: Blender Python API reference 5.2 / bpy.types.XrSessionState.html -->

<a id="xrsessionstate-bpy-struct"></a>

# XrSessionState(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.XrSessionState"></a>

### class bpy.types.XrSessionState(bpy_struct)

Runtime state information about the VR session

<a id="bpy.types.XrSessionState.actionmaps"></a>

#### bpy.types.XrSessionState.actionmaps

(default None, readonly)

**Type:**

[`XrActionMaps`](bpy.types.XrActionMaps.md#bpy.types.XrActionMaps "bpy.types.XrActionMaps")[[`XrActionMap`](bpy.types.XrActionMap.md#bpy.types.XrActionMap "bpy.types.XrActionMap")]

<a id="bpy.types.XrSessionState.active_actionmap"></a>

#### bpy.types.XrSessionState.active_actionmap

(in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.XrSessionState.navigation_location"></a>

#### bpy.types.XrSessionState.navigation_location

Location offset to apply to base pose when determining viewer location (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.XrSessionState.navigation_rotation"></a>

#### bpy.types.XrSessionState.navigation_rotation

Rotation offset to apply to base pose when determining viewer rotation (array of 4 items, in [-inf, inf], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`mathutils.Quaternion`](mathutils.md#mathutils.Quaternion "mathutils.Quaternion")

<a id="bpy.types.XrSessionState.navigation_scale"></a>

#### bpy.types.XrSessionState.navigation_scale

Navigation scale multiplier applied when determining viewer scale (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.XrSessionState.selected_actionmap"></a>

#### bpy.types.XrSessionState.selected_actionmap

(in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.XrSessionState.viewer_pose_location"></a>

#### bpy.types.XrSessionState.viewer_pose_location

Last known location of the viewer pose (center between the eyes) in world space (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0), readonly)

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.XrSessionState.viewer_pose_rotation"></a>

#### bpy.types.XrSessionState.viewer_pose_rotation

Last known rotation of the viewer pose (center between the eyes) in world space (array of 4 items, in [-inf, inf], default (0.0, 0.0, 0.0, 0.0), readonly)

**Type:**

[`mathutils.Quaternion`](mathutils.md#mathutils.Quaternion "mathutils.Quaternion")

<a id="bpy.types.XrSessionState.viewer_scale"></a>

#### bpy.types.XrSessionState.viewer_scale

Viewer XR scale factor, computed from the navigation scale, view scale session setting, and active scene unit scale (in [-inf, inf], default 0.0, readonly)

**Type:**

float

<a id="bpy.types.XrSessionState.viewfinder"></a>

#### bpy.types.XrSessionState.viewfinder

Viewfinder State (readonly)

**Type:**

[`XrViewfinderState`](bpy.types.XrViewfinderState.md#bpy.types.XrViewfinderState "bpy.types.XrViewfinderState") | None

<a id="bpy.types.XrSessionState.is_running"></a>

#### classmethod bpy.types.XrSessionState.is_running(context)

Query if the VR session is currently running

**Parameters:**

**context** ([`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context") | None) – (never None)

**Returns:**

Result

**Return type:**

bool

<a id="bpy.types.XrSessionState.reset_to_base_pose"></a>

#### classmethod bpy.types.XrSessionState.reset_to_base_pose(context)

Force resetting of position and rotation deltas

**Parameters:**

**context** ([`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context") | None) – (never None)

<a id="bpy.types.XrSessionState.action_set_create"></a>

#### classmethod bpy.types.XrSessionState.action_set_create(context, actionmap)

Create a VR action set

**Parameters:**

- **context** ([`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context") | None) – (never None)
- **actionmap** ([`XrActionMap`](bpy.types.XrActionMap.md#bpy.types.XrActionMap "bpy.types.XrActionMap") | None) – (never None)

**Returns:**

Result

**Return type:**

bool

<a id="bpy.types.XrSessionState.action_create"></a>

#### classmethod bpy.types.XrSessionState.action_create(context, actionmap, actionmap_item)

Create a VR action

**Parameters:**

- **context** ([`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context") | None) – (never None)
- **actionmap** ([`XrActionMap`](bpy.types.XrActionMap.md#bpy.types.XrActionMap "bpy.types.XrActionMap") | None) – (never None)
- **actionmap_item** ([`XrActionMapItem`](bpy.types.XrActionMapItem.md#bpy.types.XrActionMapItem "bpy.types.XrActionMapItem") | None) – (never None)

**Returns:**

Result

**Return type:**

bool

<a id="bpy.types.XrSessionState.action_binding_create"></a>

#### classmethod bpy.types.XrSessionState.action_binding_create(context, actionmap, actionmap_item, actionmap_binding)

Create a VR action binding

**Parameters:**

- **context** ([`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context") | None) – (never None)
- **actionmap** ([`XrActionMap`](bpy.types.XrActionMap.md#bpy.types.XrActionMap "bpy.types.XrActionMap") | None) – (never None)
- **actionmap_item** ([`XrActionMapItem`](bpy.types.XrActionMapItem.md#bpy.types.XrActionMapItem "bpy.types.XrActionMapItem") | None) – (never None)
- **actionmap_binding** ([`XrActionMapBinding`](bpy.types.XrActionMapBinding.md#bpy.types.XrActionMapBinding "bpy.types.XrActionMapBinding") | None) – (never None)

**Returns:**

Result

**Return type:**

bool

<a id="bpy.types.XrSessionState.active_action_set_set"></a>

#### classmethod bpy.types.XrSessionState.active_action_set_set(context, action_set)

Set the active VR action set

**Parameters:**

- **context** ([`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context") | None) – (never None)
- **action_set** (str) – Action Set, Action set name (never None)

**Returns:**

Result

**Return type:**

bool

<a id="bpy.types.XrSessionState.controller_pose_actions_set"></a>

#### classmethod bpy.types.XrSessionState.controller_pose_actions_set(context, action_set, grip_action, aim_action)

Set the actions that determine the VR controller poses

**Parameters:**

- **context** ([`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context") | None) – (never None)
- **action_set** (str) – Action Set, Action set name (never None)
- **grip_action** (str) – Grip Action, Name of the action representing the controller grips (never None)
- **aim_action** (str) – Aim Action, Name of the action representing the controller aims (never None)

**Returns:**

Result

**Return type:**

bool

<a id="bpy.types.XrSessionState.action_state_get"></a>

#### classmethod bpy.types.XrSessionState.action_state_get(context, action_set_name, action_name, user_path)

Get the current state of a VR action

**Parameters:**

- **context** ([`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context") | None) – (never None)
- **action_set_name** (str) – Action Set, Action set name (never None)
- **action_name** (str) – Action, Action name (never None)
- **user_path** (str) – User Path, OpenXR user path (never None)

**Returns:**

Action State, Current state of the VR action. Second float value is only set for 2D vector type actions. (array of 2 items, in [-inf, inf], never None)

**Return type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.XrSessionState.haptic_action_apply"></a>

#### classmethod bpy.types.XrSessionState.haptic_action_apply(context, action_set_name, action_name, user_path, duration, frequency, amplitude)

Apply a VR haptic action

**Parameters:**

- **context** ([`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context") | None) – (never None)
- **action_set_name** (str) – Action Set, Action set name (never None)
- **action_name** (str) – Action, Action name (never None)
- **user_path** (str) – User Path, Optional OpenXR user path. If not set, the action will be applied to all paths. (never None)
- **duration** (float) – Duration, Haptic duration in seconds. 0.0 is the minimum supported duration. (in [0, inf])
- **frequency** (float) – Frequency, Frequency of the haptic vibration in hertz. 0.0 specifies the OpenXR runtime’s default frequency. (in [0, inf])
- **amplitude** (float) – Amplitude, Haptic amplitude, ranging from 0.0 to 1.0 (in [0, 1])

**Returns:**

Result

**Return type:**

bool

<a id="bpy.types.XrSessionState.haptic_action_stop"></a>

#### classmethod bpy.types.XrSessionState.haptic_action_stop(context, action_set_name, action_name, user_path)

Stop a VR haptic action

**Parameters:**

- **context** ([`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context") | None) – (never None)
- **action_set_name** (str) – Action Set, Action set name (never None)
- **action_name** (str) – Action, Action name (never None)
- **user_path** (str) – User Path, Optional OpenXR user path. If not set, the action will be stopped for all paths. (never None)

<a id="bpy.types.XrSessionState.controller_grip_location_get"></a>

#### classmethod bpy.types.XrSessionState.controller_grip_location_get(context, index)

Get the last known controller grip location in world space

**Parameters:**

- **context** ([`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context") | None) – (never None)
- **index** (int) – Index, Controller index (in [0, 255])

**Returns:**

Location, Controller grip location (array of 3 items, in [-inf, inf], never None)

**Return type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.XrSessionState.controller_grip_rotation_get"></a>

#### classmethod bpy.types.XrSessionState.controller_grip_rotation_get(context, index)

Get the last known controller grip rotation (quaternion) in world space

**Parameters:**

- **context** ([`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context") | None) – (never None)
- **index** (int) – Index, Controller index (in [0, 255])

**Returns:**

Rotation, Controller grip quaternion rotation (array of 4 items, in [-inf, inf], never None)

**Return type:**

[`mathutils.Quaternion`](mathutils.md#mathutils.Quaternion "mathutils.Quaternion")

<a id="bpy.types.XrSessionState.controller_aim_location_get"></a>

#### classmethod bpy.types.XrSessionState.controller_aim_location_get(context, index)

Get the last known controller aim location in world space

**Parameters:**

- **context** ([`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context") | None) – (never None)
- **index** (int) – Index, Controller index (in [0, 255])

**Returns:**

Location, Controller aim location (array of 3 items, in [-inf, inf], never None)

**Return type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.XrSessionState.controller_aim_rotation_get"></a>

#### classmethod bpy.types.XrSessionState.controller_aim_rotation_get(context, index)

Get the last known controller aim rotation (quaternion) in world space

**Parameters:**

- **context** ([`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context") | None) – (never None)
- **index** (int) – Index, Controller index (in [0, 255])

**Returns:**

Rotation, Controller aim quaternion rotation (array of 4 items, in [-inf, inf], never None)

**Return type:**

[`mathutils.Quaternion`](mathutils.md#mathutils.Quaternion "mathutils.Quaternion")

<a id="bpy.types.XrSessionState.bl_rna_get_subclass"></a>

#### classmethod bpy.types.XrSessionState.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.XrSessionState.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.XrSessionState.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`WindowManager.xr_session_state`](bpy.types.WindowManager.md#bpy.types.WindowManager.xr_session_state "bpy.types.WindowManager.xr_session_state") - [`XrActionMaps.find`](bpy.types.XrActionMaps.md#bpy.types.XrActionMaps.find "bpy.types.XrActionMaps.find") - [`XrActionMaps.new`](bpy.types.XrActionMaps.md#bpy.types.XrActionMaps.new "bpy.types.XrActionMaps.new") | - [`XrActionMaps.new_from_actionmap`](bpy.types.XrActionMaps.md#bpy.types.XrActionMaps.new_from_actionmap "bpy.types.XrActionMaps.new_from_actionmap") - [`XrActionMaps.remove`](bpy.types.XrActionMaps.md#bpy.types.XrActionMaps.remove "bpy.types.XrActionMaps.remove") |
