<!-- source: Blender Python API reference 5.2 / bpy.types.CurveProfile.html -->

<a id="curveprofile-bpy-struct"></a>

# CurveProfile(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.CurveProfile"></a>

### class bpy.types.CurveProfile(bpy_struct)

Profile Path editor used to build a profile path

<a id="bpy.types.CurveProfile.points"></a>

#### bpy.types.CurveProfile.points

Profile control points (default None, readonly)

**Type:**

[`CurveProfilePoints`](bpy.types.CurveProfilePoints.md#bpy.types.CurveProfilePoints "bpy.types.CurveProfilePoints")[[`CurveProfilePoint`](bpy.types.CurveProfilePoint.md#bpy.types.CurveProfilePoint "bpy.types.CurveProfilePoint")]

<a id="bpy.types.CurveProfile.preset"></a>

#### bpy.types.CurveProfile.preset

(default `'LINE'`)

- `LINE`
  Line – Default.
- `SUPPORTS`
  Support Loops – Loops on each side of the profile.
- `CORNICE`
  Cornice Molding.
- `CROWN`
  Crown Molding.
- `STEPS`
  Steps – A number of steps defined by the segments.

**Type:**

Literal[‘LINE’, ‘SUPPORTS’, ‘CORNICE’, ‘CROWN’, ‘STEPS’]

<a id="bpy.types.CurveProfile.segments"></a>

#### bpy.types.CurveProfile.segments

Segments sampled from control points (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`CurveProfilePoint`](bpy.types.CurveProfilePoint.md#bpy.types.CurveProfilePoint "bpy.types.CurveProfilePoint")]

<a id="bpy.types.CurveProfile.use_clip"></a>

#### bpy.types.CurveProfile.use_clip

Force the path view to fit a defined boundary (default False)

**Type:**

bool

<a id="bpy.types.CurveProfile.use_sample_even_lengths"></a>

#### bpy.types.CurveProfile.use_sample_even_lengths

Sample edges with even lengths (default False)

**Type:**

bool

<a id="bpy.types.CurveProfile.use_sample_straight_edges"></a>

#### bpy.types.CurveProfile.use_sample_straight_edges

Sample edges with vector handles (default False)

**Type:**

bool

<a id="bpy.types.CurveProfile.update"></a>

#### bpy.types.CurveProfile.update()

Refresh internal data, remove doubles and clip points

<a id="bpy.types.CurveProfile.reset_view"></a>

#### bpy.types.CurveProfile.reset_view()

Reset the curve profile grid to its clipping size

<a id="bpy.types.CurveProfile.initialize"></a>

#### bpy.types.CurveProfile.initialize(totsegments)

Set the number of display segments and fill tables

**Parameters:**

**totsegments** (int) – The number of segment values to initialize the segments table with (in [1, 1000], never None)

<a id="bpy.types.CurveProfile.evaluate"></a>

#### bpy.types.CurveProfile.evaluate(length_portion)

Evaluate the at the given portion of the path length

**Parameters:**

**length_portion** (float) – Length Portion, Portion of the path length to travel before evaluation (in [0, 1])

**Returns:**

Location, The location at the given portion of the profile (array of 2 items, in [-100, 100])

**Return type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.CurveProfile.bl_rna_get_subclass"></a>

#### classmethod bpy.types.CurveProfile.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.CurveProfile.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.CurveProfile.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`BevelModifier.custom_profile`](bpy.types.BevelModifier.md#bpy.types.BevelModifier.custom_profile "bpy.types.BevelModifier.custom_profile") - [`Curve.bevel_profile`](bpy.types.Curve.md#bpy.types.Curve.bevel_profile "bpy.types.Curve.bevel_profile") | - [`ToolSettings.custom_bevel_profile_preset`](bpy.types.ToolSettings.md#bpy.types.ToolSettings.custom_bevel_profile_preset "bpy.types.ToolSettings.custom_bevel_profile_preset") |
