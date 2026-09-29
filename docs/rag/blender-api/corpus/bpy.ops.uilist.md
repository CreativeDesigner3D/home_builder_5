<!-- source: Blender Python API reference 5.2 / bpy.ops.uilist.html -->

<a id="module-bpy.ops.uilist"></a>

# Uilist Operators

<a id="bpy.ops.uilist.entry_add"></a>

### bpy.ops.uilist.entry_add(*, list_path='', active_index_path='')

Add an entry to the list after the current active item

**Parameters:**

- **list_path** (str) – list_path, (optional, never None)
- **active_index_path** (str) – active_index_path, (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_ui/generic_ui_list.py:208](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_ui/generic_ui_list.py#L208)

<a id="bpy.ops.uilist.entry_move"></a>

### bpy.ops.uilist.entry_move(*, list_path='', active_index_path='', direction='UP')

Move an entry in the list up or down

**Parameters:**

- **list_path** (str) – list_path, (optional, never None)
- **active_index_path** (str) – active_index_path, (optional, never None)
- **direction** (Literal['UP', 'DOWN']) –

  Direction, (optional)

  - `UP`
    Up – Move the active entry up.
  - `DOWN`
    Down – Move the active entry down.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_ui/generic_ui_list.py:236](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_ui/generic_ui_list.py#L236)

<a id="bpy.ops.uilist.entry_remove"></a>

### bpy.ops.uilist.entry_remove(*, list_path='', active_index_path='')

Remove the selected entry from the list

**Parameters:**

- **list_path** (str) – list_path, (optional, never None)
- **active_index_path** (str) – active_index_path, (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_ui/generic_ui_list.py:191](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_ui/generic_ui_list.py#L191)
