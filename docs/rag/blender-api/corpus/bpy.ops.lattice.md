<!-- source: Blender Python API reference 5.2 / bpy.ops.lattice.html -->

<a id="module-bpy.ops.lattice"></a>

# Lattice Operators

<a id="bpy.ops.lattice.flip"></a>

### bpy.ops.lattice.flip(*, axis='U')

Mirror all control points without inverting the lattice deform

**Parameters:**

**axis** (Literal['U', 'V', 'W']) – Flip Axis, Coordinates along this axis get flipped (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.lattice.make_regular"></a>

### bpy.ops.lattice.make_regular()

Set UVW control points a uniform distance apart

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.lattice.select_all"></a>

### bpy.ops.lattice.select_all(*, action='TOGGLE')

Change selection of all UVW control points

**Parameters:**

**action** (Literal['TOGGLE', 'SELECT', 'DESELECT', 'INVERT']) –

Action, Selection action to execute (optional)

- `TOGGLE`
  Toggle – Toggle selection for all elements.
- `SELECT`
  Select – Select all elements.
- `DESELECT`
  Deselect – Deselect all elements.
- `INVERT`
  Invert – Invert selection of all elements.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.lattice.select_less"></a>

### bpy.ops.lattice.select_less()

Deselect vertices at the boundary of each selection region

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.lattice.select_mirror"></a>

### bpy.ops.lattice.select_mirror(*, axis={'X'}, extend=False)

Select mirrored lattice points

**Parameters:**

- **axis** (set[Literal[[Axis Flag Xyz Items](bpy_types_enum_items/axis_flag_xyz_items.md#rna-enum-axis-flag-xyz-items)]]) – Axis, (optional)
- **extend** (bool) – Extend, Extend the selection (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.lattice.select_more"></a>

### bpy.ops.lattice.select_more()

Select vertices directly linked to already selected ones

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.lattice.select_random"></a>

### bpy.ops.lattice.select_random(*, ratio=0.5, seed=0, action='SELECT')

Randomly select UVW control points

**Parameters:**

- **ratio** (float) – Ratio, Portion of items to select randomly (in [0, 1], optional)
- **seed** (int) – Random Seed, Seed for the random number generator (in [0, inf], optional)
- **action** (Literal['SELECT', 'DESELECT']) –

  Action, Selection action to execute (optional)

  - `SELECT`
    Select – Select all elements.
  - `DESELECT`
    Deselect – Deselect all elements.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.lattice.select_ungrouped"></a>

### bpy.ops.lattice.select_ungrouped(*, extend=False)

Select vertices without a group

**Parameters:**

**extend** (bool) – Extend, Extend the selection (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]
