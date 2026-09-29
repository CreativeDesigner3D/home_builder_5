<!-- source: Blender Python API reference 5.2 / bpy.types.CurveProfilePoint.html -->

<a id="curveprofilepoint-bpy-struct"></a>

# CurveProfilePoint(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.CurveProfilePoint"></a>

### class bpy.types.CurveProfilePoint(bpy_struct)

Point of a path used to define a profile

<a id="bpy.types.CurveProfilePoint.handle_type_1"></a>

#### bpy.types.CurveProfilePoint.handle_type_1

Path interpolation at this point (default `'FREE'`)

**Type:**

Literal[‘AUTO’, ‘VECTOR’, ‘FREE’, ‘ALIGN’]

<a id="bpy.types.CurveProfilePoint.handle_type_2"></a>

#### bpy.types.CurveProfilePoint.handle_type_2

Path interpolation at this point (default `'FREE'`)

**Type:**

Literal[‘AUTO’, ‘VECTOR’, ‘FREE’, ‘ALIGN’]

<a id="bpy.types.CurveProfilePoint.location"></a>

#### bpy.types.CurveProfilePoint.location

X/Y coordinates of the path point (array of 2 items, in [-inf, inf], default (0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.CurveProfilePoint.select"></a>

#### bpy.types.CurveProfilePoint.select

Selection state of the path point (default False)

**Type:**

bool

<a id="bpy.types.CurveProfilePoint.bl_rna_get_subclass"></a>

#### classmethod bpy.types.CurveProfilePoint.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.CurveProfilePoint.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.CurveProfilePoint.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`CurveProfile.points`](bpy.types.CurveProfile.md#bpy.types.CurveProfile.points "bpy.types.CurveProfile.points") - [`CurveProfile.segments`](bpy.types.CurveProfile.md#bpy.types.CurveProfile.segments "bpy.types.CurveProfile.segments") | - [`CurveProfilePoints.add`](bpy.types.CurveProfilePoints.md#bpy.types.CurveProfilePoints.add "bpy.types.CurveProfilePoints.add") - [`CurveProfilePoints.remove`](bpy.types.CurveProfilePoints.md#bpy.types.CurveProfilePoints.remove "bpy.types.CurveProfilePoints.remove") |
