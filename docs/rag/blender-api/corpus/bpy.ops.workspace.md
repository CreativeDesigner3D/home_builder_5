<!-- source: Blender Python API reference 5.2 / bpy.ops.workspace.html -->

<a id="module-bpy.ops.workspace"></a>

# Workspace Operators

<a id="bpy.ops.workspace.add"></a>

### bpy.ops.workspace.add()

Add a new workspace by duplicating the current one or appending one from the user configuration

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.workspace.append_activate"></a>

### bpy.ops.workspace.append_activate(*, idname='', filepath='')

Append a workspace and make it the active one in the current window

**Parameters:**

- **idname** (str) – Identifier, Name of the workspace to append and activate (optional, never None)
- **filepath** (str) – Filepath, Path to the library (optional, never None, blend relative `//` prefix supported)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.workspace.delete"></a>

### bpy.ops.workspace.delete()

Delete the active workspace

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.workspace.delete_all_others"></a>

### bpy.ops.workspace.delete_all_others()

Delete all workspaces except this one

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.workspace.duplicate"></a>

### bpy.ops.workspace.duplicate()

Add a new workspace

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.workspace.reorder_to_back"></a>

### bpy.ops.workspace.reorder_to_back()

Reorder workspace to be last in the list

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.workspace.reorder_to_front"></a>

### bpy.ops.workspace.reorder_to_front()

Reorder workspace to be first in the list

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.workspace.scene_pin_toggle"></a>

### bpy.ops.workspace.scene_pin_toggle()

Remember the last used scene for the current workspace and switch to it whenever this workspace is activated again

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]
