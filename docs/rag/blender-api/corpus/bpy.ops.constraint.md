<!-- source: Blender Python API reference 5.2 / bpy.ops.constraint.html -->

<a id="module-bpy.ops.constraint"></a>

# Constraint Operators

<a id="bpy.ops.constraint.add_target"></a>

### bpy.ops.constraint.add_target()

Add a target to the constraint

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/constraint.py:26](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/constraint.py#L26)

<a id="bpy.ops.constraint.apply"></a>

### bpy.ops.constraint.apply(*, constraint='', owner='OBJECT', report=False)

Apply constraint and remove from the stack

**Parameters:**

- **constraint** (str) – Constraint, Name of the constraint to edit (optional, never None)
- **owner** (Literal['OBJECT', 'BONE']) –

  Owner, The owner of this constraint (optional)

  - `OBJECT`
    Object – Edit a constraint on the active object.
  - `BONE`
    Bone – Edit a constraint on the active bone.
- **report** (bool) – Report, Create a notification after the operation (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.constraint.childof_clear_inverse"></a>

### bpy.ops.constraint.childof_clear_inverse(*, constraint='', owner='OBJECT')

Clear inverse correction for Child Of constraint

**Parameters:**

- **constraint** (str) – Constraint, Name of the constraint to edit (optional, never None)
- **owner** (Literal['OBJECT', 'BONE']) –

  Owner, The owner of this constraint (optional)

  - `OBJECT`
    Object – Edit a constraint on the active object.
  - `BONE`
    Bone – Edit a constraint on the active bone.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.constraint.childof_set_inverse"></a>

### bpy.ops.constraint.childof_set_inverse(*, constraint='', owner='OBJECT')

Set inverse correction for Child Of constraint

**Parameters:**

- **constraint** (str) – Constraint, Name of the constraint to edit (optional, never None)
- **owner** (Literal['OBJECT', 'BONE']) –

  Owner, The owner of this constraint (optional)

  - `OBJECT`
    Object – Edit a constraint on the active object.
  - `BONE`
    Bone – Edit a constraint on the active bone.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.constraint.copy"></a>

### bpy.ops.constraint.copy(*, constraint='', owner='OBJECT', report=False)

Duplicate constraint at the same position in the stack

**Parameters:**

- **constraint** (str) – Constraint, Name of the constraint to edit (optional, never None)
- **owner** (Literal['OBJECT', 'BONE']) –

  Owner, The owner of this constraint (optional)

  - `OBJECT`
    Object – Edit a constraint on the active object.
  - `BONE`
    Bone – Edit a constraint on the active bone.
- **report** (bool) – Report, Create a notification after the operation (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.constraint.copy_to_selected"></a>

### bpy.ops.constraint.copy_to_selected(*, constraint='', owner='OBJECT')

Copy constraint to other selected objects/bones

**Parameters:**

- **constraint** (str) – Constraint, Name of the constraint to edit (optional, never None)
- **owner** (Literal['OBJECT', 'BONE']) –

  Owner, The owner of this constraint (optional)

  - `OBJECT`
    Object – Edit a constraint on the active object.
  - `BONE`
    Bone – Edit a constraint on the active bone.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.constraint.delete"></a>

### bpy.ops.constraint.delete(*, constraint='', owner='OBJECT', report=False)

Remove constraint from constraint stack

**Parameters:**

- **constraint** (str) – Constraint, Name of the constraint to edit (optional, never None)
- **owner** (Literal['OBJECT', 'BONE']) –

  Owner, The owner of this constraint (optional)

  - `OBJECT`
    Object – Edit a constraint on the active object.
  - `BONE`
    Bone – Edit a constraint on the active bone.
- **report** (bool) – Report, Create a notification after the operation (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.constraint.disable_keep_transform"></a>

### bpy.ops.constraint.disable_keep_transform()

Set the influence of this constraint to zero while trying to maintain the object’s transformation. Other active constraints can still influence the final transformation

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/constraint.py:86](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/constraint.py#L86)

<a id="bpy.ops.constraint.followpath_path_animate"></a>

### bpy.ops.constraint.followpath_path_animate(*, constraint='', owner='OBJECT', frame_start=1, length=100)

Add default animation for path used by constraint if it isn’t animated already

**Parameters:**

- **constraint** (str) – Constraint, Name of the constraint to edit (optional, never None)
- **owner** (Literal['OBJECT', 'BONE']) –

  Owner, The owner of this constraint (optional)

  - `OBJECT`
    Object – Edit a constraint on the active object.
  - `BONE`
    Bone – Edit a constraint on the active bone.
- **frame_start** (int) – Start Frame, First frame of path animation (in [-1048574, 1048574], optional)
- **length** (int) – Length, Number of frames that path animation should take (in [0, 1048574], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.constraint.limitdistance_reset"></a>

### bpy.ops.constraint.limitdistance_reset(*, constraint='', owner='OBJECT')

Reset limiting distance for Limit Distance Constraint

**Parameters:**

- **constraint** (str) – Constraint, Name of the constraint to edit (optional, never None)
- **owner** (Literal['OBJECT', 'BONE']) –

  Owner, The owner of this constraint (optional)

  - `OBJECT`
    Object – Edit a constraint on the active object.
  - `BONE`
    Bone – Edit a constraint on the active bone.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.constraint.move_down"></a>

### bpy.ops.constraint.move_down(*, constraint='', owner='OBJECT')

Move constraint down in constraint stack

**Parameters:**

- **constraint** (str) – Constraint, Name of the constraint to edit (optional, never None)
- **owner** (Literal['OBJECT', 'BONE']) –

  Owner, The owner of this constraint (optional)

  - `OBJECT`
    Object – Edit a constraint on the active object.
  - `BONE`
    Bone – Edit a constraint on the active bone.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.constraint.move_to_index"></a>

### bpy.ops.constraint.move_to_index(*, constraint='', owner='OBJECT', index=0)

Change the constraint’s position in the list so it evaluates after the set number of others

**Parameters:**

- **constraint** (str) – Constraint, Name of the constraint to edit (optional, never None)
- **owner** (Literal['OBJECT', 'BONE']) –

  Owner, The owner of this constraint (optional)

  - `OBJECT`
    Object – Edit a constraint on the active object.
  - `BONE`
    Bone – Edit a constraint on the active bone.
- **index** (int) – Index, The index to move the constraint to (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.constraint.move_up"></a>

### bpy.ops.constraint.move_up(*, constraint='', owner='OBJECT')

Move constraint up in constraint stack

**Parameters:**

- **constraint** (str) – Constraint, Name of the constraint to edit (optional, never None)
- **owner** (Literal['OBJECT', 'BONE']) –

  Owner, The owner of this constraint (optional)

  - `OBJECT`
    Object – Edit a constraint on the active object.
  - `BONE`
    Bone – Edit a constraint on the active bone.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.constraint.normalize_target_weights"></a>

### bpy.ops.constraint.normalize_target_weights()

Normalize weights of all target bones

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/constraint.py:61](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/constraint.py#L61)

<a id="bpy.ops.constraint.objectsolver_clear_inverse"></a>

### bpy.ops.constraint.objectsolver_clear_inverse(*, constraint='', owner='OBJECT')

Clear inverse correction for Object Solver constraint

**Parameters:**

- **constraint** (str) – Constraint, Name of the constraint to edit (optional, never None)
- **owner** (Literal['OBJECT', 'BONE']) –

  Owner, The owner of this constraint (optional)

  - `OBJECT`
    Object – Edit a constraint on the active object.
  - `BONE`
    Bone – Edit a constraint on the active bone.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.constraint.objectsolver_set_inverse"></a>

### bpy.ops.constraint.objectsolver_set_inverse(*, constraint='', owner='OBJECT')

Set inverse correction for Object Solver constraint

**Parameters:**

- **constraint** (str) – Constraint, Name of the constraint to edit (optional, never None)
- **owner** (Literal['OBJECT', 'BONE']) –

  Owner, The owner of this constraint (optional)

  - `OBJECT`
    Object – Edit a constraint on the active object.
  - `BONE`
    Bone – Edit a constraint on the active bone.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.constraint.remove_target"></a>

### bpy.ops.constraint.remove_target(*, index=0)

Remove the target from the constraint

**Parameters:**

**index** (int) – index, (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/constraint.py:44](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/constraint.py#L44)

<a id="bpy.ops.constraint.stretchto_reset"></a>

### bpy.ops.constraint.stretchto_reset(*, constraint='', owner='OBJECT')

Reset original length of bone for Stretch To Constraint

**Parameters:**

- **constraint** (str) – Constraint, Name of the constraint to edit (optional, never None)
- **owner** (Literal['OBJECT', 'BONE']) –

  Owner, The owner of this constraint (optional)

  - `OBJECT`
    Object – Edit a constraint on the active object.
  - `BONE`
    Bone – Edit a constraint on the active bone.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]
