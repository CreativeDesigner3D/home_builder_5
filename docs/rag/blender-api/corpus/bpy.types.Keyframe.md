<!-- source: Blender Python API reference 5.2 / bpy.types.Keyframe.html -->

<a id="keyframe-bpy-struct"></a>

# Keyframe(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.Keyframe"></a>

### class bpy.types.Keyframe(bpy_struct)

Bézier curve point with two handles defining a Keyframe on an F-Curve

<a id="bpy.types.Keyframe.amplitude"></a>

#### bpy.types.Keyframe.amplitude

Amount to boost elastic bounces for ‘elastic’ easing (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.Keyframe.back"></a>

#### bpy.types.Keyframe.back

Amount of overshoot for ‘back’ easing (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.Keyframe.co"></a>

#### bpy.types.Keyframe.co

Coordinates of the control point (array of 2 items, in [-inf, inf], default (0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.Keyframe.co_ui"></a>

#### bpy.types.Keyframe.co_ui

Coordinates of the control point. Note: Changing this value also updates the handles similar to using the graph editor transform operator (array of 2 items, in [-inf, inf], default (0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.Keyframe.easing"></a>

#### bpy.types.Keyframe.easing

Which ends of the segment between this and the next keyframe easing interpolation is applied to (default `'AUTO'`)

**Type:**

Literal[[Beztriple Interpolation Easing Items](bpy_types_enum_items/beztriple_interpolation_easing_items.md#rna-enum-beztriple-interpolation-easing-items)]

<a id="bpy.types.Keyframe.handle_left"></a>

#### bpy.types.Keyframe.handle_left

Coordinates of the left handle (before the control point) (array of 2 items, in [-inf, inf], default (0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.Keyframe.handle_left_type"></a>

#### bpy.types.Keyframe.handle_left_type

Handle types (default `'FREE'`)

**Type:**

Literal[[Keyframe Handle Type Items](bpy_types_enum_items/keyframe_handle_type_items.md#rna-enum-keyframe-handle-type-items)]

<a id="bpy.types.Keyframe.handle_right"></a>

#### bpy.types.Keyframe.handle_right

Coordinates of the right handle (after the control point) (array of 2 items, in [-inf, inf], default (0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.Keyframe.handle_right_type"></a>

#### bpy.types.Keyframe.handle_right_type

Handle types (default `'FREE'`)

**Type:**

Literal[[Keyframe Handle Type Items](bpy_types_enum_items/keyframe_handle_type_items.md#rna-enum-keyframe-handle-type-items)]

<a id="bpy.types.Keyframe.interpolation"></a>

#### bpy.types.Keyframe.interpolation

Interpolation method to use for segment of the F-Curve from this Keyframe until the next Keyframe (default `'CONSTANT'`)

**Type:**

Literal[[Beztriple Interpolation Mode Items](bpy_types_enum_items/beztriple_interpolation_mode_items.md#rna-enum-beztriple-interpolation-mode-items)]

<a id="bpy.types.Keyframe.period"></a>

#### bpy.types.Keyframe.period

Time between bounces for elastic easing (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.Keyframe.select_control_point"></a>

#### bpy.types.Keyframe.select_control_point

Control point selection status (default False)

**Type:**

bool

<a id="bpy.types.Keyframe.select_left_handle"></a>

#### bpy.types.Keyframe.select_left_handle

Left handle selection status (default False)

**Type:**

bool

<a id="bpy.types.Keyframe.select_right_handle"></a>

#### bpy.types.Keyframe.select_right_handle

Right handle selection status (default False)

**Type:**

bool

<a id="bpy.types.Keyframe.type"></a>

#### bpy.types.Keyframe.type

Type of keyframe (for visual purposes only) (default `'KEYFRAME'`)

**Type:**

Literal[[Beztriple Keyframe Type Items](bpy_types_enum_items/beztriple_keyframe_type_items.md#rna-enum-beztriple-keyframe-type-items)]

<a id="bpy.types.Keyframe.bl_rna_get_subclass"></a>

#### classmethod bpy.types.Keyframe.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.Keyframe.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.Keyframe.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([type](#bpy.types.Keyframe.type "bpy.types.Keyframe.type") | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

[type](#bpy.types.Keyframe.type "bpy.types.Keyframe.type")

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
| - `bpy.context.selected_editable_keyframes` - [`FCurve.keyframe_points`](bpy.types.FCurve.md#bpy.types.FCurve.keyframe_points "bpy.types.FCurve.keyframe_points") | - [`FCurveKeyframePoints.insert`](bpy.types.FCurveKeyframePoints.md#bpy.types.FCurveKeyframePoints.insert "bpy.types.FCurveKeyframePoints.insert") - [`FCurveKeyframePoints.remove`](bpy.types.FCurveKeyframePoints.md#bpy.types.FCurveKeyframePoints.remove "bpy.types.FCurveKeyframePoints.remove") |
