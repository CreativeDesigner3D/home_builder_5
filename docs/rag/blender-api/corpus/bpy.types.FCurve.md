<!-- source: Blender Python API reference 5.2 / bpy.types.FCurve.html -->

<a id="fcurve-bpy-struct"></a>

# FCurve(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.FCurve"></a>

### class bpy.types.FCurve(bpy_struct)

F-Curve defining values of a period of time

<a id="bpy.types.FCurve.array_index"></a>

#### bpy.types.FCurve.array_index

Index to the specific property affected by F-Curve if applicable (in [0, inf], default 0)

**Type:**

int

<a id="bpy.types.FCurve.auto_smoothing"></a>

#### bpy.types.FCurve.auto_smoothing

Algorithm used to compute automatic handles (default `'NONE'`)

**Type:**

Literal[[Fcurve Auto Smoothing Items](bpy_types_enum_items/fcurve_auto_smoothing_items.md#rna-enum-fcurve-auto-smoothing-items)]

<a id="bpy.types.FCurve.color"></a>

#### bpy.types.FCurve.color

Color of the F-Curve in the Graph Editor (array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.FCurve.color_mode"></a>

#### bpy.types.FCurve.color_mode

Method used to determine color of F-Curve in Graph Editor (default `'AUTO_RAINBOW'`)

- `AUTO_RAINBOW`
  Auto Rainbow – Cycle through the rainbow, trying to give each curve a unique color.
- `AUTO_RGB`
  Auto XYZ to RGB – Use axis colors for transform and color properties, and auto-rainbow for the rest.
- `AUTO_YRGB`
  Auto WXYZ to YRGB – Use WXYZ axis colors for quaternion/axis-angle rotations, XYZ axis colors for other transform and color properties, and auto-rainbow for the rest.
- `CUSTOM`
  User Defined – Use custom hand-picked color for F-Curve.

**Type:**

Literal[‘AUTO_RAINBOW’, ‘AUTO_RGB’, ‘AUTO_YRGB’, ‘CUSTOM’]

<a id="bpy.types.FCurve.data_path"></a>

#### bpy.types.FCurve.data_path

RNA Path to property affected by F-Curve (default “”, never None)

**Type:**

str

<a id="bpy.types.FCurve.driver"></a>

#### bpy.types.FCurve.driver

Channel Driver (only set for Driver F-Curves) (readonly)

**Type:**

[`Driver`](bpy.types.Driver.md#bpy.types.Driver "bpy.types.Driver") | None

<a id="bpy.types.FCurve.extrapolation"></a>

#### bpy.types.FCurve.extrapolation

Method used for evaluating value of F-Curve outside first and last keyframes (default `'CONSTANT'`)

- `CONSTANT`
  Constant – Hold values of endpoint keyframes.
- `LINEAR`
  Linear – Use slope of curve leading in/out of endpoint keyframes.

**Type:**

Literal[‘CONSTANT’, ‘LINEAR’]

<a id="bpy.types.FCurve.group"></a>

#### bpy.types.FCurve.group

Action Group that this F-Curve belongs to

**Type:**

[`ActionGroup`](bpy.types.ActionGroup.md#bpy.types.ActionGroup "bpy.types.ActionGroup") | None

<a id="bpy.types.FCurve.hide"></a>

#### bpy.types.FCurve.hide

F-Curve and its keyframes are hidden in the Graph Editor graphs (default True)

**Type:**

bool

<a id="bpy.types.FCurve.is_empty"></a>

#### bpy.types.FCurve.is_empty

True if the curve contributes no animation due to lack of keyframes or useful modifiers, and should be deleted (default False, readonly)

**Type:**

bool

<a id="bpy.types.FCurve.is_valid"></a>

#### bpy.types.FCurve.is_valid

False when F-Curve could not be evaluated in past, so should be skipped when evaluating (default True)

**Type:**

bool

<a id="bpy.types.FCurve.keyframe_points"></a>

#### bpy.types.FCurve.keyframe_points

User-editable keyframes (default None, readonly)

**Type:**

[`FCurveKeyframePoints`](bpy.types.FCurveKeyframePoints.md#bpy.types.FCurveKeyframePoints "bpy.types.FCurveKeyframePoints")[[`Keyframe`](bpy.types.Keyframe.md#bpy.types.Keyframe "bpy.types.Keyframe")]

<a id="bpy.types.FCurve.lock"></a>

#### bpy.types.FCurve.lock

F-Curve’s settings cannot be edited (default False)

**Type:**

bool

<a id="bpy.types.FCurve.modifiers"></a>

#### bpy.types.FCurve.modifiers

Modifiers affecting the shape of the F-Curve (default None, readonly)

**Type:**

[`FCurveModifiers`](bpy.types.FCurveModifiers.md#bpy.types.FCurveModifiers "bpy.types.FCurveModifiers")[[`FModifier`](bpy.types.FModifier.md#bpy.types.FModifier "bpy.types.FModifier")]

<a id="bpy.types.FCurve.mute"></a>

#### bpy.types.FCurve.mute

Disable F-Curve evaluation (default False)

**Type:**

bool

<a id="bpy.types.FCurve.sampled_points"></a>

#### bpy.types.FCurve.sampled_points

Sampled animation data (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`FCurveSample`](bpy.types.FCurveSample.md#bpy.types.FCurveSample "bpy.types.FCurveSample")]

<a id="bpy.types.FCurve.select"></a>

#### bpy.types.FCurve.select

F-Curve is selected for editing (default False)

**Type:**

bool

<a id="bpy.types.FCurve.evaluate"></a>

#### bpy.types.FCurve.evaluate(frame)

Evaluate F-Curve

**Parameters:**

**frame** (float) – Frame, Evaluate F-Curve at given frame (in [-inf, inf])

**Returns:**

Value, Value of F-Curve specific frame (in [-inf, inf])

**Return type:**

float

<a id="bpy.types.FCurve.update"></a>

#### bpy.types.FCurve.update()

Ensure keyframes are sorted in chronological order and handles are set correctly

<a id="bpy.types.FCurve.range"></a>

#### bpy.types.FCurve.range()

Get the time extents for F-Curve

**Returns:**

Range, Min/Max values (array of 2 items, in [-inf, inf])

**Return type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.FCurve.update_autoflags"></a>

#### bpy.types.FCurve.update_autoflags(data)

Update FCurve flags set automatically from affected property (currently, integer/discrete flags set when the property is not a float)

**Parameters:**

**data** ([`AnyType`](bpy.types.AnyType.md#bpy.types.AnyType "bpy.types.AnyType") | None) – Data, Data containing the property controlled by given FCurve (never None)

<a id="bpy.types.FCurve.convert_to_samples"></a>

#### bpy.types.FCurve.convert_to_samples(start, end)

Convert current FCurve from keyframes to sample points, if necessary

**Parameters:**

- **start** (int) – Start Frame, (in [-1048574, 1048574])
- **end** (int) – End Frame, (in [-1048574, 1048574])

<a id="bpy.types.FCurve.convert_to_keyframes"></a>

#### bpy.types.FCurve.convert_to_keyframes(start, end)

Convert current FCurve from sample points to keyframes (linear interpolation), if necessary

**Parameters:**

- **start** (int) – Start Frame, (in [-1048574, 1048574])
- **end** (int) – End Frame, (in [-1048574, 1048574])

<a id="bpy.types.FCurve.bake"></a>

#### bpy.types.FCurve.bake(start, end, *, step=1.0, remove='IN_RANGE')

Place keys at even intervals on the existing curve.

**Parameters:**

- **start** (int) – Start Frame, Frame at which to start baking (in [-1048574, 1048574])
- **end** (int) – End Frame, Frame at which to end baking (inclusive) (in [-1048574, 1048574])
- **step** (float) – Step, At which interval to add keys (in [0.01, inf], optional)
- **remove** (Literal['NONE', 'IN_RANGE', 'OUT_RANGE', 'ALL']) –

  Remove Options, Choose which keys should be automatically removed by the bake (optional)

  - `NONE`
    None – Keep all keys.
  - `IN_RANGE`
    In Range – Remove all keys within the defined range.
  - `OUT_RANGE`
    Outside Range – Remove all keys outside the defined range.
  - `ALL`
    All – Remove all existing keys.

<a id="bpy.types.FCurve.bl_rna_get_subclass"></a>

#### classmethod bpy.types.FCurve.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.FCurve.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.FCurve.bl_rna_get_subclass_py(id, default=None, /)

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
| - `bpy.context.active_editable_fcurve` - `bpy.context.editable_fcurves` - `bpy.context.selected_editable_fcurves` - `bpy.context.selected_visible_fcurves` - `bpy.context.visible_fcurves` - [`Action.fcurve_ensure_for_datablock`](bpy.types.Action.md#bpy.types.Action.fcurve_ensure_for_datablock "bpy.types.Action.fcurve_ensure_for_datablock") - [`ActionChannelbag.fcurves`](bpy.types.ActionChannelbag.md#bpy.types.ActionChannelbag.fcurves "bpy.types.ActionChannelbag.fcurves") - [`ActionChannelbagFCurves.ensure`](bpy.types.ActionChannelbagFCurves.md#bpy.types.ActionChannelbagFCurves.ensure "bpy.types.ActionChannelbagFCurves.ensure") - [`ActionChannelbagFCurves.find`](bpy.types.ActionChannelbagFCurves.md#bpy.types.ActionChannelbagFCurves.find "bpy.types.ActionChannelbagFCurves.find") - [`ActionChannelbagFCurves.new`](bpy.types.ActionChannelbagFCurves.md#bpy.types.ActionChannelbagFCurves.new "bpy.types.ActionChannelbagFCurves.new") - [`ActionChannelbagFCurves.new_from_fcurve`](bpy.types.ActionChannelbagFCurves.md#bpy.types.ActionChannelbagFCurves.new_from_fcurve "bpy.types.ActionChannelbagFCurves.new_from_fcurve") | - [`ActionChannelbagFCurves.new_from_fcurve`](bpy.types.ActionChannelbagFCurves.md#bpy.types.ActionChannelbagFCurves.new_from_fcurve "bpy.types.ActionChannelbagFCurves.new_from_fcurve") - [`ActionChannelbagFCurves.remove`](bpy.types.ActionChannelbagFCurves.md#bpy.types.ActionChannelbagFCurves.remove "bpy.types.ActionChannelbagFCurves.remove") - [`ActionGroup.channels`](bpy.types.ActionGroup.md#bpy.types.ActionGroup.channels "bpy.types.ActionGroup.channels") - [`AnimData.drivers`](bpy.types.AnimData.md#bpy.types.AnimData.drivers "bpy.types.AnimData.drivers") - [`AnimDataDrivers.find`](bpy.types.AnimDataDrivers.md#bpy.types.AnimDataDrivers.find "bpy.types.AnimDataDrivers.find") - [`AnimDataDrivers.from_existing`](bpy.types.AnimDataDrivers.md#bpy.types.AnimDataDrivers.from_existing "bpy.types.AnimDataDrivers.from_existing") - [`AnimDataDrivers.from_existing`](bpy.types.AnimDataDrivers.md#bpy.types.AnimDataDrivers.from_existing "bpy.types.AnimDataDrivers.from_existing") - [`AnimDataDrivers.new`](bpy.types.AnimDataDrivers.md#bpy.types.AnimDataDrivers.new "bpy.types.AnimDataDrivers.new") - [`AnimDataDrivers.remove`](bpy.types.AnimDataDrivers.md#bpy.types.AnimDataDrivers.remove "bpy.types.AnimDataDrivers.remove") - [`NlaStrip.fcurves`](bpy.types.NlaStrip.md#bpy.types.NlaStrip.fcurves "bpy.types.NlaStrip.fcurves") - [`NlaStripFCurves.find`](bpy.types.NlaStripFCurves.md#bpy.types.NlaStripFCurves.find "bpy.types.NlaStripFCurves.find") |
