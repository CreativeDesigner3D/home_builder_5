<!-- source: Blender Python API reference 5.2 / bpy.ops.dpaint.html -->

<a id="module-bpy.ops.dpaint"></a>

# Dpaint Operators

<a id="bpy.ops.dpaint.bake"></a>

### bpy.ops.dpaint.bake()

Bake dynamic paint image sequence surface

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.dpaint.output_toggle"></a>

### bpy.ops.dpaint.output_toggle(*, output='A')

Add or remove Dynamic Paint output data layer

**Parameters:**

**output** (Literal['A', 'B']) – Output Toggle, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.dpaint.surface_slot_add"></a>

### bpy.ops.dpaint.surface_slot_add()

Add a new Dynamic Paint surface slot

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.dpaint.surface_slot_remove"></a>

### bpy.ops.dpaint.surface_slot_remove()

Remove the selected surface slot

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.dpaint.type_toggle"></a>

### bpy.ops.dpaint.type_toggle(*, type='CANVAS')

Toggle whether given type is active or not

**Parameters:**

**type** (Literal[[Prop Dynamicpaint Type Items](bpy_types_enum_items/prop_dynamicpaint_type_items.md#rna-enum-prop-dynamicpaint-type-items)]) – Type, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]
