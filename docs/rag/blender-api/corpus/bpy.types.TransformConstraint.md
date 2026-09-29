<!-- source: Blender Python API reference 5.2 / bpy.types.TransformConstraint.html -->

<a id="transformconstraint-constraint"></a>

# TransformConstraint(Constraint)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Constraint`](bpy.types.Constraint.md#bpy.types.Constraint "bpy.types.Constraint")

<a id="bpy.types.TransformConstraint"></a>

### class bpy.types.TransformConstraint(Constraint)

Map transformations of the target to the object

<a id="bpy.types.TransformConstraint.from_max_x"></a>

#### bpy.types.TransformConstraint.from_max_x

Top range of X axis source motion (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.TransformConstraint.from_max_x_rot"></a>

#### bpy.types.TransformConstraint.from_max_x_rot

Top range of X axis source motion (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.TransformConstraint.from_max_x_scale"></a>

#### bpy.types.TransformConstraint.from_max_x_scale

Top range of X axis source motion (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.TransformConstraint.from_max_y"></a>

#### bpy.types.TransformConstraint.from_max_y

Top range of Y axis source motion (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.TransformConstraint.from_max_y_rot"></a>

#### bpy.types.TransformConstraint.from_max_y_rot

Top range of Y axis source motion (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.TransformConstraint.from_max_y_scale"></a>

#### bpy.types.TransformConstraint.from_max_y_scale

Top range of Y axis source motion (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.TransformConstraint.from_max_z"></a>

#### bpy.types.TransformConstraint.from_max_z

Top range of Z axis source motion (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.TransformConstraint.from_max_z_rot"></a>

#### bpy.types.TransformConstraint.from_max_z_rot

Top range of Z axis source motion (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.TransformConstraint.from_max_z_scale"></a>

#### bpy.types.TransformConstraint.from_max_z_scale

Top range of Z axis source motion (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.TransformConstraint.from_min_x"></a>

#### bpy.types.TransformConstraint.from_min_x

Bottom range of X axis source motion (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.TransformConstraint.from_min_x_rot"></a>

#### bpy.types.TransformConstraint.from_min_x_rot

Bottom range of X axis source motion (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.TransformConstraint.from_min_x_scale"></a>

#### bpy.types.TransformConstraint.from_min_x_scale

Bottom range of X axis source motion (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.TransformConstraint.from_min_y"></a>

#### bpy.types.TransformConstraint.from_min_y

Bottom range of Y axis source motion (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.TransformConstraint.from_min_y_rot"></a>

#### bpy.types.TransformConstraint.from_min_y_rot

Bottom range of Y axis source motion (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.TransformConstraint.from_min_y_scale"></a>

#### bpy.types.TransformConstraint.from_min_y_scale

Bottom range of Y axis source motion (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.TransformConstraint.from_min_z"></a>

#### bpy.types.TransformConstraint.from_min_z

Bottom range of Z axis source motion (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.TransformConstraint.from_min_z_rot"></a>

#### bpy.types.TransformConstraint.from_min_z_rot

Bottom range of Z axis source motion (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.TransformConstraint.from_min_z_scale"></a>

#### bpy.types.TransformConstraint.from_min_z_scale

Bottom range of Z axis source motion (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.TransformConstraint.from_rotation_mode"></a>

#### bpy.types.TransformConstraint.from_rotation_mode

Specify the type of rotation channels to use (default `'AUTO'`)

**Type:**

Literal[[Driver Target Rotation Mode Items](bpy_types_enum_items/driver_target_rotation_mode_items.md#rna-enum-driver-target-rotation-mode-items)]

<a id="bpy.types.TransformConstraint.map_from"></a>

#### bpy.types.TransformConstraint.map_from

The transformation type to use from the target (default `'LOCATION'`)

**Type:**

Literal[‘LOCATION’, ‘ROTATION’, ‘SCALE’]

<a id="bpy.types.TransformConstraint.map_to"></a>

#### bpy.types.TransformConstraint.map_to

The transformation type to affect on the constrained object (default `'LOCATION'`)

**Type:**

Literal[‘LOCATION’, ‘ROTATION’, ‘SCALE’]

<a id="bpy.types.TransformConstraint.map_to_x_from"></a>

#### bpy.types.TransformConstraint.map_to_x_from

The source axis constrained object’s X axis uses (default `'X'`)

**Type:**

Literal[[Axis Xyz Items](bpy_types_enum_items/axis_xyz_items.md#rna-enum-axis-xyz-items)]

<a id="bpy.types.TransformConstraint.map_to_y_from"></a>

#### bpy.types.TransformConstraint.map_to_y_from

The source axis constrained object’s Y axis uses (default `'X'`)

**Type:**

Literal[[Axis Xyz Items](bpy_types_enum_items/axis_xyz_items.md#rna-enum-axis-xyz-items)]

<a id="bpy.types.TransformConstraint.map_to_z_from"></a>

#### bpy.types.TransformConstraint.map_to_z_from

The source axis constrained object’s Z axis uses (default `'X'`)

**Type:**

Literal[[Axis Xyz Items](bpy_types_enum_items/axis_xyz_items.md#rna-enum-axis-xyz-items)]

<a id="bpy.types.TransformConstraint.mix_mode"></a>

#### bpy.types.TransformConstraint.mix_mode

Specify how to combine the new location with original (default `'ADD'`)

- `REPLACE`
  Replace – Replace component values.
- `ADD`
  Add – Add component values together.

**Type:**

Literal[‘REPLACE’, ‘ADD’]

<a id="bpy.types.TransformConstraint.mix_mode_rot"></a>

#### bpy.types.TransformConstraint.mix_mode_rot

Specify how to combine the new rotation with original (default `'ADD'`)

- `REPLACE`
  Replace – Replace component values.
- `ADD`
  Add – Add component values together.
- `BEFORE`
  Before Original – Apply new rotation before original, as if it was on a parent.
- `AFTER`
  After Original – Apply new rotation after original, as if it was on a child.

**Type:**

Literal[‘REPLACE’, ‘ADD’, ‘BEFORE’, ‘AFTER’]

<a id="bpy.types.TransformConstraint.mix_mode_scale"></a>

#### bpy.types.TransformConstraint.mix_mode_scale

Specify how to combine the new scale with original (default `'REPLACE'`)

- `REPLACE`
  Replace – Replace component values.
- `MULTIPLY`
  Multiply – Multiply component values together.

**Type:**

Literal[‘REPLACE’, ‘MULTIPLY’]

<a id="bpy.types.TransformConstraint.subtarget"></a>

#### bpy.types.TransformConstraint.subtarget

Armature bone, mesh or lattice vertex group, … (default “”, never None)

**Type:**

str

<a id="bpy.types.TransformConstraint.target"></a>

#### bpy.types.TransformConstraint.target

Target object

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.TransformConstraint.to_euler_order"></a>

#### bpy.types.TransformConstraint.to_euler_order

Explicitly specify the output euler rotation order (default `'AUTO'`)

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

<a id="bpy.types.TransformConstraint.to_max_x"></a>

#### bpy.types.TransformConstraint.to_max_x

Top range of X axis destination motion (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.TransformConstraint.to_max_x_rot"></a>

#### bpy.types.TransformConstraint.to_max_x_rot

Top range of X axis destination motion (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.TransformConstraint.to_max_x_scale"></a>

#### bpy.types.TransformConstraint.to_max_x_scale

Top range of X axis destination motion (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.TransformConstraint.to_max_y"></a>

#### bpy.types.TransformConstraint.to_max_y

Top range of Y axis destination motion (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.TransformConstraint.to_max_y_rot"></a>

#### bpy.types.TransformConstraint.to_max_y_rot

Top range of Y axis destination motion (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.TransformConstraint.to_max_y_scale"></a>

#### bpy.types.TransformConstraint.to_max_y_scale

Top range of Y axis destination motion (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.TransformConstraint.to_max_z"></a>

#### bpy.types.TransformConstraint.to_max_z

Top range of Z axis destination motion (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.TransformConstraint.to_max_z_rot"></a>

#### bpy.types.TransformConstraint.to_max_z_rot

Top range of Z axis destination motion (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.TransformConstraint.to_max_z_scale"></a>

#### bpy.types.TransformConstraint.to_max_z_scale

Top range of Z axis destination motion (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.TransformConstraint.to_min_x"></a>

#### bpy.types.TransformConstraint.to_min_x

Bottom range of X axis destination motion (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.TransformConstraint.to_min_x_rot"></a>

#### bpy.types.TransformConstraint.to_min_x_rot

Bottom range of X axis destination motion (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.TransformConstraint.to_min_x_scale"></a>

#### bpy.types.TransformConstraint.to_min_x_scale

Bottom range of X axis destination motion (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.TransformConstraint.to_min_y"></a>

#### bpy.types.TransformConstraint.to_min_y

Bottom range of Y axis destination motion (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.TransformConstraint.to_min_y_rot"></a>

#### bpy.types.TransformConstraint.to_min_y_rot

Bottom range of Y axis destination motion (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.TransformConstraint.to_min_y_scale"></a>

#### bpy.types.TransformConstraint.to_min_y_scale

Bottom range of Y axis destination motion (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.TransformConstraint.to_min_z"></a>

#### bpy.types.TransformConstraint.to_min_z

Bottom range of Z axis destination motion (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.TransformConstraint.to_min_z_rot"></a>

#### bpy.types.TransformConstraint.to_min_z_rot

Bottom range of Z axis destination motion (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.TransformConstraint.to_min_z_scale"></a>

#### bpy.types.TransformConstraint.to_min_z_scale

Bottom range of Z axis destination motion (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.TransformConstraint.use_motion_extrapolate"></a>

#### bpy.types.TransformConstraint.use_motion_extrapolate

Extrapolate ranges (default False)

**Type:**

bool

<a id="bpy.types.TransformConstraint.bl_rna_get_subclass"></a>

#### classmethod bpy.types.TransformConstraint.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.TransformConstraint.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.TransformConstraint.bl_rna_get_subclass_py(id, default=None, /)

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
