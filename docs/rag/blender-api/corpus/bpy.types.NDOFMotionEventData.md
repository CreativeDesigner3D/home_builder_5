<!-- source: Blender Python API reference 5.2 / bpy.types.NDOFMotionEventData.html -->

<a id="ndofmotioneventdata-bpy-struct"></a>

# NDOFMotionEventData(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.NDOFMotionEventData"></a>

### class bpy.types.NDOFMotionEventData(bpy_struct)

NDOF motion data for window manager events

<a id="bpy.types.NDOFMotionEventData.progress"></a>

#### bpy.types.NDOFMotionEventData.progress

Indicates the gesture phase (default `'STARTING'`, readonly)

**Type:**

Literal[‘STARTING’, ‘IN_PROGRESS’, ‘FINISHING’]

<a id="bpy.types.NDOFMotionEventData.rotation"></a>

#### bpy.types.NDOFMotionEventData.rotation

Axis-angle rotation of this motion event. The vector magnitude is the angle where 1.0 represents 360 degrees. The angle is typically scaled by the time-delta before use. (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0), readonly)

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.NDOFMotionEventData.time_delta"></a>

#### bpy.types.NDOFMotionEventData.time_delta

Time since previous motion event (in seconds) (in [-inf, inf], default 0.0, readonly)

**Type:**

float

<a id="bpy.types.NDOFMotionEventData.translation"></a>

#### bpy.types.NDOFMotionEventData.translation

The translation of this motion event. The range on each axis is [-1 to 1], before being multiplied by the sensitivity preference. This is typically scaled by the time-delta before use. (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0), readonly)

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.NDOFMotionEventData.bl_rna_get_subclass"></a>

#### classmethod bpy.types.NDOFMotionEventData.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.NDOFMotionEventData.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.NDOFMotionEventData.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Event.ndof_motion`](bpy.types.Event.md#bpy.types.Event.ndof_motion "bpy.types.Event.ndof_motion") |  |
