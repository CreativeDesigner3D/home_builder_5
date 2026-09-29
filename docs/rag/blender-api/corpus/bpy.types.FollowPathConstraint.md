<!-- source: Blender Python API reference 5.2 / bpy.types.FollowPathConstraint.html -->

<a id="followpathconstraint-constraint"></a>

# FollowPathConstraint(Constraint)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Constraint`](bpy.types.Constraint.md#bpy.types.Constraint "bpy.types.Constraint")

<a id="bpy.types.FollowPathConstraint"></a>

### class bpy.types.FollowPathConstraint(Constraint)

Lock motion to the target path

<a id="bpy.types.FollowPathConstraint.forward_axis"></a>

#### bpy.types.FollowPathConstraint.forward_axis

Axis that points forward along the path (default `'FORWARD_X'`)

**Type:**

Literal[‘FORWARD_X’, ‘FORWARD_Y’, ‘FORWARD_Z’, ‘TRACK_NEGATIVE_X’, ‘TRACK_NEGATIVE_Y’, ‘TRACK_NEGATIVE_Z’]

<a id="bpy.types.FollowPathConstraint.offset"></a>

#### bpy.types.FollowPathConstraint.offset

Offset from the position corresponding to the time frame (in [-1.04857e+06, 1.04857e+06], default 0.0)

**Type:**

float

<a id="bpy.types.FollowPathConstraint.offset_factor"></a>

#### bpy.types.FollowPathConstraint.offset_factor

Percentage value defining target position along length of curve (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.FollowPathConstraint.target"></a>

#### bpy.types.FollowPathConstraint.target

Target Curve object

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.FollowPathConstraint.up_axis"></a>

#### bpy.types.FollowPathConstraint.up_axis

Axis that points upward (default `'UP_X'`)

**Type:**

Literal[‘UP_X’, ‘UP_Y’, ‘UP_Z’]

<a id="bpy.types.FollowPathConstraint.use_curve_follow"></a>

#### bpy.types.FollowPathConstraint.use_curve_follow

Object will follow the heading and banking of the curve (default False)

**Type:**

bool

<a id="bpy.types.FollowPathConstraint.use_curve_radius"></a>

#### bpy.types.FollowPathConstraint.use_curve_radius

Object is scaled by the curve radius (default False)

**Type:**

bool

<a id="bpy.types.FollowPathConstraint.use_fixed_location"></a>

#### bpy.types.FollowPathConstraint.use_fixed_location

Object will stay locked to a single point somewhere along the length of the curve regardless of time (default False)

**Type:**

bool

<a id="bpy.types.FollowPathConstraint.bl_rna_get_subclass"></a>

#### classmethod bpy.types.FollowPathConstraint.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.FollowPathConstraint.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.FollowPathConstraint.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, Constraint.name, Constraint.type, Constraint.is_override_data, Constraint.owner_space, Constraint.target_space, Constraint.space_object, Constraint.space_subtarget, Constraint.mute, Constraint.enabled, Constraint.show_expanded, Constraint.is_valid, Constraint.active, Constraint.influence, Constraint.error_location, Constraint.error_rotation

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, Constraint.bl_rna_get_subclass, Constraint.bl_rna_get_subclass_py
