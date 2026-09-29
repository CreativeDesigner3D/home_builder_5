<!-- source: Blender Python API reference 5.2 / bpy.types.CopyRotationConstraint.html -->

<a id="copyrotationconstraint-constraint"></a>

# CopyRotationConstraint(Constraint)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Constraint`](bpy.types.Constraint.md#bpy.types.Constraint "bpy.types.Constraint")

<a id="bpy.types.CopyRotationConstraint"></a>

### class bpy.types.CopyRotationConstraint(Constraint)

Copy the rotation of the target

<a id="bpy.types.CopyRotationConstraint.euler_order"></a>

#### bpy.types.CopyRotationConstraint.euler_order

Explicitly specify the euler rotation order (default `'AUTO'`)

- `AUTO`
  Default – Euler using the default rotation order.
- `XYZ`
  XYZ Euler – Euler using the XYZ rotation order.
- `XZY`
  XZY Euler – Euler using the XZY rotation order.
- `YXZ`
  YXZ Euler – Euler using the YXZ rotation order.
- `YZX`
  YZX Euler – Euler using the YZX rotation order.
- `ZXY`
  ZXY Euler – Euler using the ZXY rotation order.
- `ZYX`
  ZYX Euler – Euler using the ZYX rotation order.

**Type:**

Literal[‘AUTO’, ‘XYZ’, ‘XZY’, ‘YXZ’, ‘YZX’, ‘ZXY’, ‘ZYX’]

<a id="bpy.types.CopyRotationConstraint.invert_x"></a>

#### bpy.types.CopyRotationConstraint.invert_x

Invert the X rotation (default False)

**Type:**

bool

<a id="bpy.types.CopyRotationConstraint.invert_y"></a>

#### bpy.types.CopyRotationConstraint.invert_y

Invert the Y rotation (default False)

**Type:**

bool

<a id="bpy.types.CopyRotationConstraint.invert_z"></a>

#### bpy.types.CopyRotationConstraint.invert_z

Invert the Z rotation (default False)

**Type:**

bool

<a id="bpy.types.CopyRotationConstraint.mix_mode"></a>

#### bpy.types.CopyRotationConstraint.mix_mode

Specify how the copied and existing rotations are combined (default `'REPLACE'`)

- `REPLACE`
  Replace – Replace the original rotation with copied.
- `ADD`
  Add – Add euler component values together.
- `BEFORE`
  Before Original – Apply copied rotation before original, as if the constraint target is a parent.
- `AFTER`
  After Original – Apply copied rotation after original, as if the constraint target is a child.
- `OFFSET`
  Offset (Legacy) – Combine rotations like the original Offset checkbox. Does not work well for multiple axis rotations..

**Type:**

Literal[‘REPLACE’, ‘ADD’, ‘BEFORE’, ‘AFTER’, ‘OFFSET’]

<a id="bpy.types.CopyRotationConstraint.subtarget"></a>

#### bpy.types.CopyRotationConstraint.subtarget

Armature bone, mesh or lattice vertex group, … (default “”, never None)

**Type:**

str

<a id="bpy.types.CopyRotationConstraint.target"></a>

#### bpy.types.CopyRotationConstraint.target

Target object

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.CopyRotationConstraint.use_offset"></a>

#### bpy.types.CopyRotationConstraint.use_offset

DEPRECATED: Add original rotation into copied rotation (default False)

**Type:**

bool

<a id="bpy.types.CopyRotationConstraint.use_x"></a>

#### bpy.types.CopyRotationConstraint.use_x

Copy the target’s X rotation (default False)

**Type:**

bool

<a id="bpy.types.CopyRotationConstraint.use_y"></a>

#### bpy.types.CopyRotationConstraint.use_y

Copy the target’s Y rotation (default False)

**Type:**

bool

<a id="bpy.types.CopyRotationConstraint.use_z"></a>

#### bpy.types.CopyRotationConstraint.use_z

Copy the target’s Z rotation (default False)

**Type:**

bool

<a id="bpy.types.CopyRotationConstraint.bl_rna_get_subclass"></a>

#### classmethod bpy.types.CopyRotationConstraint.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.CopyRotationConstraint.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.CopyRotationConstraint.bl_rna_get_subclass_py(id, default=None, /)

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
