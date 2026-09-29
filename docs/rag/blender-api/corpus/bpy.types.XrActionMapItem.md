<!-- source: Blender Python API reference 5.2 / bpy.types.XrActionMapItem.html -->

<a id="xractionmapitem-bpy-struct"></a>

# XrActionMapItem(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.XrActionMapItem"></a>

### class bpy.types.XrActionMapItem(bpy_struct)

<a id="bpy.types.XrActionMapItem.bimanual"></a>

#### bpy.types.XrActionMapItem.bimanual

The action depends on the states/poses of both user paths (default False)

**Type:**

bool

<a id="bpy.types.XrActionMapItem.bindings"></a>

#### bpy.types.XrActionMapItem.bindings

Bindings for the action map item, mapping the action to an XR input (default None, readonly)

**Type:**

[`XrActionMapBindings`](bpy.types.XrActionMapBindings.md#bpy.types.XrActionMapBindings "bpy.types.XrActionMapBindings")[[`XrActionMapBinding`](bpy.types.XrActionMapBinding.md#bpy.types.XrActionMapBinding "bpy.types.XrActionMapBinding")]

<a id="bpy.types.XrActionMapItem.haptic_amplitude"></a>

#### bpy.types.XrActionMapItem.haptic_amplitude

Intensity of the haptic vibration, ranging from 0.0 to 1.0 (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.XrActionMapItem.haptic_duration"></a>

#### bpy.types.XrActionMapItem.haptic_duration

Haptic duration in seconds. 0.0 is the minimum supported duration. (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.XrActionMapItem.haptic_frequency"></a>

#### bpy.types.XrActionMapItem.haptic_frequency

Frequency of the haptic vibration in hertz. 0.0 specifies the OpenXR runtime’s default frequency. (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.XrActionMapItem.haptic_match_user_paths"></a>

#### bpy.types.XrActionMapItem.haptic_match_user_paths

Apply haptics to the same user paths for the haptic action and this action (default False)

**Type:**

bool

<a id="bpy.types.XrActionMapItem.haptic_mode"></a>

#### bpy.types.XrActionMapItem.haptic_mode

Haptic application mode (default `'PRESS'`)

- `PRESS`
  Press – Apply haptics on button press.
- `RELEASE`
  Release – Apply haptics on button release.
- `PRESS_RELEASE`
  Press Release – Apply haptics on button press and release.
- `REPEAT`
  Repeat – Apply haptics repeatedly for the duration of the button press.

**Type:**

Literal[‘PRESS’, ‘RELEASE’, ‘PRESS_RELEASE’, ‘REPEAT’]

<a id="bpy.types.XrActionMapItem.haptic_name"></a>

#### bpy.types.XrActionMapItem.haptic_name

Name of the haptic action to apply when executing this action (default “”, never None)

**Type:**

str

<a id="bpy.types.XrActionMapItem.name"></a>

#### bpy.types.XrActionMapItem.name

Name of the action map item (default “”, never None)

**Type:**

str

<a id="bpy.types.XrActionMapItem.op"></a>

#### bpy.types.XrActionMapItem.op

Identifier of operator to call on action event (default “”, never None)

**Type:**

str

<a id="bpy.types.XrActionMapItem.op_mode"></a>

#### bpy.types.XrActionMapItem.op_mode

Operator execution mode (default `'PRESS'`)

- `PRESS`
  Press – Execute operator on button press (non-modal operators only).
- `RELEASE`
  Release – Execute operator on button release (non-modal operators only).
- `MODAL`
  Modal – Use modal execution (modal operators only).

**Type:**

Literal[‘PRESS’, ‘RELEASE’, ‘MODAL’]

<a id="bpy.types.XrActionMapItem.op_name"></a>

#### bpy.types.XrActionMapItem.op_name

Name of operator (translated) to call on action event (default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.XrActionMapItem.op_properties"></a>

#### bpy.types.XrActionMapItem.op_properties

Properties to set when the operator is called (readonly)

**Type:**

[`OperatorProperties`](bpy.types.OperatorProperties.md#bpy.types.OperatorProperties "bpy.types.OperatorProperties") | None

<a id="bpy.types.XrActionMapItem.pose_is_controller_aim"></a>

#### bpy.types.XrActionMapItem.pose_is_controller_aim

The action poses will be used for the VR controller aims (default False)

**Type:**

bool

<a id="bpy.types.XrActionMapItem.pose_is_controller_grip"></a>

#### bpy.types.XrActionMapItem.pose_is_controller_grip

The action poses will be used for the VR controller grips (default False)

**Type:**

bool

<a id="bpy.types.XrActionMapItem.selected_binding"></a>

#### bpy.types.XrActionMapItem.selected_binding

Currently selected binding (in [-32768, 32767], default 0)

**Type:**

int

<a id="bpy.types.XrActionMapItem.type"></a>

#### bpy.types.XrActionMapItem.type

Action type (default `'FLOAT'`)

- `FLOAT`
  Float – Float action, representing either a digital or analog button.
- `VECTOR2D`
  Vector2D – 2D float vector action, representing a thumbstick or trackpad.
- `POSE`
  Pose – 3D pose action, representing a controller’s location and rotation.
- `VIBRATION`
  Vibration – Haptic vibration output action, to be applied with a duration, frequency, and amplitude.

**Type:**

Literal[‘FLOAT’, ‘VECTOR2D’, ‘POSE’, ‘VIBRATION’]

<a id="bpy.types.XrActionMapItem.user_paths"></a>

#### bpy.types.XrActionMapItem.user_paths

OpenXR user paths (default None, readonly)

**Type:**

[`XrUserPaths`](bpy.types.XrUserPaths.md#bpy.types.XrUserPaths "bpy.types.XrUserPaths")[[`XrUserPath`](bpy.types.XrUserPath.md#bpy.types.XrUserPath "bpy.types.XrUserPath")]

<a id="bpy.types.XrActionMapItem.bl_rna_get_subclass"></a>

#### classmethod bpy.types.XrActionMapItem.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.XrActionMapItem.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.XrActionMapItem.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([type](#bpy.types.XrActionMapItem.type "bpy.types.XrActionMapItem.type") | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

[type](#bpy.types.XrActionMapItem.type "bpy.types.XrActionMapItem.type")

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
| - [`XrActionMap.actionmap_items`](bpy.types.XrActionMap.md#bpy.types.XrActionMap.actionmap_items "bpy.types.XrActionMap.actionmap_items") - [`XrActionMapItems.find`](bpy.types.XrActionMapItems.md#bpy.types.XrActionMapItems.find "bpy.types.XrActionMapItems.find") - [`XrActionMapItems.new`](bpy.types.XrActionMapItems.md#bpy.types.XrActionMapItems.new "bpy.types.XrActionMapItems.new") - [`XrActionMapItems.new_from_item`](bpy.types.XrActionMapItems.md#bpy.types.XrActionMapItems.new_from_item "bpy.types.XrActionMapItems.new_from_item") | - [`XrActionMapItems.new_from_item`](bpy.types.XrActionMapItems.md#bpy.types.XrActionMapItems.new_from_item "bpy.types.XrActionMapItems.new_from_item") - [`XrActionMapItems.remove`](bpy.types.XrActionMapItems.md#bpy.types.XrActionMapItems.remove "bpy.types.XrActionMapItems.remove") - [`XrSessionState.action_binding_create`](bpy.types.XrSessionState.md#bpy.types.XrSessionState.action_binding_create "bpy.types.XrSessionState.action_binding_create") - [`XrSessionState.action_create`](bpy.types.XrSessionState.md#bpy.types.XrSessionState.action_create "bpy.types.XrSessionState.action_create") |
