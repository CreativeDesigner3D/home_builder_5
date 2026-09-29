<!-- source: Blender Python API reference 5.2 / bpy.types.PivotConstraint.html -->

<a id="pivotconstraint-constraint"></a>

# PivotConstraint(Constraint)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Constraint`](bpy.types.Constraint.md#bpy.types.Constraint "bpy.types.Constraint")

<a id="bpy.types.PivotConstraint"></a>

### class bpy.types.PivotConstraint(Constraint)

Rotate around a different point

<a id="bpy.types.PivotConstraint.head_tail"></a>

#### bpy.types.PivotConstraint.head_tail

Target along length of bone: Head is 0, Tail is 1 (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.PivotConstraint.offset"></a>

#### bpy.types.PivotConstraint.offset

Offset of pivot from target (when set), or from owner’s location (when Fixed Position is off), or the absolute pivot point (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.PivotConstraint.rotation_range"></a>

#### bpy.types.PivotConstraint.rotation_range

Rotation range on which pivoting should occur (default `'ALWAYS_ACTIVE'`)

- `ALWAYS_ACTIVE`
  Always – Use the pivot point in every rotation.
- `NX`
  -X Rotation – Use the pivot point in the negative rotation range around the X-axis.
- `NY`
  -Y Rotation – Use the pivot point in the negative rotation range around the Y-axis.
- `NZ`
  -Z Rotation – Use the pivot point in the negative rotation range around the Z-axis.
- `X`
  X Rotation – Use the pivot point in the positive rotation range around the X-axis.
- `Y`
  Y Rotation – Use the pivot point in the positive rotation range around the Y-axis.
- `Z`
  Z Rotation – Use the pivot point in the positive rotation range around the Z-axis.

**Type:**

Literal[‘ALWAYS_ACTIVE’, ‘NX’, ‘NY’, ‘NZ’, ‘X’, ‘Y’, ‘Z’]

<a id="bpy.types.PivotConstraint.subtarget"></a>

#### bpy.types.PivotConstraint.subtarget

(default “”, never None)

**Type:**

str

<a id="bpy.types.PivotConstraint.target"></a>

#### bpy.types.PivotConstraint.target

Target Object, defining the position of the pivot when defined

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.PivotConstraint.use_bbone_shape"></a>

#### bpy.types.PivotConstraint.use_bbone_shape

Follow shape of B-Bone segments when calculating Head/Tail position (default False)

**Type:**

bool

<a id="bpy.types.PivotConstraint.use_relative_location"></a>

#### bpy.types.PivotConstraint.use_relative_location

Offset will be an absolute point in space instead of relative to the target (default True)

**Type:**

bool

<a id="bpy.types.PivotConstraint.bl_rna_get_subclass"></a>

#### classmethod bpy.types.PivotConstraint.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.PivotConstraint.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.PivotConstraint.bl_rna_get_subclass_py(id, default=None, /)

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
