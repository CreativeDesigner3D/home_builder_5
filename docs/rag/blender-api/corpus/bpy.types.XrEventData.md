<!-- source: Blender Python API reference 5.2 / bpy.types.XrEventData.html -->

<a id="xreventdata-bpy-struct"></a>

# XrEventData(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.XrEventData"></a>

### class bpy.types.XrEventData(bpy_struct)

XR Data for Window Manager Event

<a id="bpy.types.XrEventData.action"></a>

#### bpy.types.XrEventData.action

XR action name (default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.XrEventData.action_set"></a>

#### bpy.types.XrEventData.action_set

XR action set name (default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.XrEventData.bimanual"></a>

#### bpy.types.XrEventData.bimanual

Whether bimanual interaction is occurring (default False, readonly)

**Type:**

bool

<a id="bpy.types.XrEventData.controller_location"></a>

#### bpy.types.XrEventData.controller_location

Location of the action’s corresponding controller aim in world space (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0), readonly)

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.XrEventData.controller_location_other"></a>

#### bpy.types.XrEventData.controller_location_other

Controller aim location of the other user path for bimanual actions (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0), readonly)

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.XrEventData.controller_rotation"></a>

#### bpy.types.XrEventData.controller_rotation

Rotation of the action’s corresponding controller aim in world space (array of 4 items, in [-inf, inf], default (0.0, 0.0, 0.0, 0.0), readonly)

**Type:**

[`mathutils.Quaternion`](mathutils.md#mathutils.Quaternion "mathutils.Quaternion")

<a id="bpy.types.XrEventData.controller_rotation_other"></a>

#### bpy.types.XrEventData.controller_rotation_other

Controller aim rotation of the other user path for bimanual actions (array of 4 items, in [-inf, inf], default (0.0, 0.0, 0.0, 0.0), readonly)

**Type:**

[`mathutils.Quaternion`](mathutils.md#mathutils.Quaternion "mathutils.Quaternion")

<a id="bpy.types.XrEventData.float_threshold"></a>

#### bpy.types.XrEventData.float_threshold

Input threshold for float/2D vector actions (in [-inf, inf], default 0.0, readonly)

**Type:**

float

<a id="bpy.types.XrEventData.state"></a>

#### bpy.types.XrEventData.state

XR action values corresponding to type (array of 2 items, in [-inf, inf], default (0.0, 0.0), readonly)

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.XrEventData.state_other"></a>

#### bpy.types.XrEventData.state_other

State of the other user path for bimanual actions (array of 2 items, in [-inf, inf], default (0.0, 0.0), readonly)

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.XrEventData.type"></a>

#### bpy.types.XrEventData.type

XR action type (default `'FLOAT'`, readonly)

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

<a id="bpy.types.XrEventData.user_path"></a>

#### bpy.types.XrEventData.user_path

User path of the action. E.g. “/user/hand/left” (default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.XrEventData.user_path_other"></a>

#### bpy.types.XrEventData.user_path_other

Other user path, for bimanual actions. E.g. “/user/hand/right” (default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.XrEventData.bl_rna_get_subclass"></a>

#### classmethod bpy.types.XrEventData.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.XrEventData.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.XrEventData.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([type](#bpy.types.XrEventData.type "bpy.types.XrEventData.type") | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

[type](#bpy.types.XrEventData.type "bpy.types.XrEventData.type")

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
| - [`Event.xr`](bpy.types.Event.md#bpy.types.Event.xr "bpy.types.Event.xr") |  |
