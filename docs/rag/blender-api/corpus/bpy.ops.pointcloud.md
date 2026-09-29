<!-- source: Blender Python API reference 5.2 / bpy.ops.pointcloud.html -->

<a id="module-bpy.ops.pointcloud"></a>

# Pointcloud Operators

<a id="bpy.ops.pointcloud.attribute_set"></a>

### bpy.ops.pointcloud.attribute_set(*, value_float=0.0, value_float_vector_2d=(0.0, 0.0), value_float_vector_3d=(0.0, 0.0, 0.0), value_float_vector_4d=(0.0, 0.0, 0.0, 0.0), value_int=0, value_int_vector_2d=(0, 0), value_color=(1.0, 1.0, 1.0, 1.0), value_bool=False)

Set values of the active attribute for selected elements

**Parameters:**

- **value_float** (float) – Value, (in [-inf, inf], optional)
- **value_float_vector_2d** (Sequence[float]) – Value, (array of 2 items, in [-inf, inf], optional)
- **value_float_vector_3d** (Sequence[float]) – Value, (array of 3 items, in [-inf, inf], optional)
- **value_float_vector_4d** (Sequence[float]) – Value, (array of 4 items, in [-inf, inf], optional)
- **value_int** (int) – Value, (in [-inf, inf], optional)
- **value_int_vector_2d** (Sequence[int]) – Value, (array of 2 items, in [-inf, inf], optional)
- **value_color** (Sequence[float]) – Value, (array of 4 items, in [-inf, inf], optional)
- **value_bool** (bool) – Value, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.pointcloud.delete"></a>

### bpy.ops.pointcloud.delete()

Remove selected points

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.pointcloud.duplicate"></a>

### bpy.ops.pointcloud.duplicate()

Copy selected points

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.pointcloud.duplicate_move"></a>

### bpy.ops.pointcloud.duplicate_move(*, POINTCLOUD_OT_duplicate={}, TRANSFORM_OT_translate={})

Make copies of selected elements and move them

**Parameters:**

- **POINTCLOUD_OT_duplicate** (dict[str, Any]) – Duplicate, Copy selected points (optional, [`bpy.ops.pointcloud.duplicate()`](#bpy.ops.pointcloud.duplicate "bpy.ops.pointcloud.duplicate") keyword arguments)
- **TRANSFORM_OT_translate** (dict[str, Any]) – Move, Move selected items (optional, [`bpy.ops.transform.translate()`](bpy.ops.transform.md#bpy.ops.transform.translate "bpy.ops.transform.translate") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.pointcloud.select_all"></a>

### bpy.ops.pointcloud.select_all(*, action='TOGGLE')

(De)select all points

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

<a id="bpy.ops.pointcloud.select_random"></a>

### bpy.ops.pointcloud.select_random(*, seed=0, probability=0.5)

Randomize existing selection or create new random selection

**Parameters:**

- **seed** (int) – Seed, Source of randomness (in [-inf, inf], optional)
- **probability** (float) – Probability, Chance of every point being included in the selection (in [0, 1], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.pointcloud.separate"></a>

### bpy.ops.pointcloud.separate()

Separate selected geometry into a new point cloud

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]
