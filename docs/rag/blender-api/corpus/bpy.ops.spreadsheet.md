<!-- source: Blender Python API reference 5.2 / bpy.ops.spreadsheet.html -->

<a id="module-bpy.ops.spreadsheet"></a>

# Spreadsheet Operators

<a id="bpy.ops.spreadsheet.add_row_filter_rule"></a>

### bpy.ops.spreadsheet.add_row_filter_rule()

Add a filter to remove rows from the displayed data

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.spreadsheet.change_spreadsheet_data_source"></a>

### bpy.ops.spreadsheet.change_spreadsheet_data_source(*, component_type=0, attribute_domain_type=0)

Change visible data source in the spreadsheet

**Parameters:**

- **component_type** (int) – Component Type, (in [0, 32767], optional)
- **attribute_domain_type** (int) – Attribute Domain Type, (in [0, 32767], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.spreadsheet.fit_column"></a>

### bpy.ops.spreadsheet.fit_column()

Resize a spreadsheet column to the width of the data

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.spreadsheet.remove_row_filter_rule"></a>

### bpy.ops.spreadsheet.remove_row_filter_rule(*, index=0)

Remove a row filter from the rules

**Parameters:**

**index** (int) – Index, (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.spreadsheet.reorder_columns"></a>

### bpy.ops.spreadsheet.reorder_columns()

Change the order of columns

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.spreadsheet.resize_column"></a>

### bpy.ops.spreadsheet.resize_column()

Resize a spreadsheet column

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.spreadsheet.toggle_pin"></a>

### bpy.ops.spreadsheet.toggle_pin()

Turn on or off pinning

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/spreadsheet.py:21](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/spreadsheet.py#L21)
