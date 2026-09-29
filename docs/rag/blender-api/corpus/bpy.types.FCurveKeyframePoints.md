<!-- source: Blender Python API reference 5.2 / bpy.types.FCurveKeyframePoints.html -->

<a id="fcurvekeyframepoints-bpy-prop-collection"></a>

# FCurveKeyframePoints(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.FCurveKeyframePoints"></a>

### class bpy.types.FCurveKeyframePoints(bpy_prop_collection)

Collection of keyframe points

<a id="bpy.types.FCurveKeyframePoints.insert"></a>

#### bpy.types.FCurveKeyframePoints.insert(frame, value, *, options=set(), keyframe_type='KEYFRAME')

Add a keyframe point to a F-Curve

**Parameters:**

- **frame** (float) – X Value of this keyframe point (in [-inf, inf])
- **value** (float) – Y Value of this keyframe point (in [-inf, inf])
- **options** (set[Literal['REPLACE', 'NEEDED', 'FAST']]) –

  Keyframe options (optional)

  - `REPLACE`
    Replace – Don’t add any new keyframes, but just replace existing ones.
  - `NEEDED`
    Needed – Only adds keyframes that are needed.
  - `FAST`
    Fast – Fast keyframe insertion to avoid recalculating the curve each time.
- **keyframe_type** (Literal[[Beztriple Keyframe Type Items](bpy_types_enum_items/beztriple_keyframe_type_items.md#rna-enum-beztriple-keyframe-type-items)]) – Type of keyframe to insert (optional)

**Returns:**

Newly created keyframe

**Return type:**

[`Keyframe`](bpy.types.Keyframe.md#bpy.types.Keyframe "bpy.types.Keyframe")

<a id="bpy.types.FCurveKeyframePoints.add"></a>

#### bpy.types.FCurveKeyframePoints.add(count)

Add a keyframe point to a F-Curve

**Parameters:**

**count** (int) – Number, Number of points to add to the spline (in [0, inf])

<a id="bpy.types.FCurveKeyframePoints.remove"></a>

#### bpy.types.FCurveKeyframePoints.remove(keyframe, *, fast=False)

Remove keyframe from an F-Curve

**Parameters:**

- **keyframe** ([`Keyframe`](bpy.types.Keyframe.md#bpy.types.Keyframe "bpy.types.Keyframe") | None) – Keyframe to remove (never None)
- **fast** (bool) – Fast, Fast keyframe removal to avoid recalculating the curve each time (optional)

<a id="bpy.types.FCurveKeyframePoints.clear"></a>

#### bpy.types.FCurveKeyframePoints.clear()

Remove all keyframes from an F-Curve

<a id="bpy.types.FCurveKeyframePoints.sort"></a>

#### bpy.types.FCurveKeyframePoints.sort()

Ensure all keyframe points are chronologically sorted

<a id="bpy.types.FCurveKeyframePoints.deduplicate"></a>

#### bpy.types.FCurveKeyframePoints.deduplicate()

Ensure there are no duplicate keys. Assumes that the points have already been sorted

<a id="bpy.types.FCurveKeyframePoints.handles_recalc"></a>

#### bpy.types.FCurveKeyframePoints.handles_recalc()

Update handles after modifications to the keyframe points, to update things like auto-clamping

<a id="bpy.types.FCurveKeyframePoints.bl_rna_get_subclass"></a>

#### classmethod bpy.types.FCurveKeyframePoints.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.FCurveKeyframePoints.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.FCurveKeyframePoints.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`FCurve.keyframe_points`](bpy.types.FCurve.md#bpy.types.FCurve.keyframe_points "bpy.types.FCurve.keyframe_points") |  |
