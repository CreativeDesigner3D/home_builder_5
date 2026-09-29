<!-- source: Blender Python API reference 5.2 / bpy.ops.gizmogroup.html -->

<a id="module-bpy.ops.gizmogroup"></a>

# Gizmogroup Operators

<a id="bpy.ops.gizmogroup.gizmo_select"></a>

### bpy.ops.gizmogroup.gizmo_select(*, extend=False, deselect=False, toggle=False, deselect_all=False, select_passthrough=False)

Select the currently highlighted gizmo

**Parameters:**

- **extend** (bool) – Extend, Extend selection instead of deselecting everything first (optional)
- **deselect** (bool) – Deselect, Remove from selection (optional)
- **toggle** (bool) – Toggle Selection, Toggle the selection (optional)
- **deselect_all** (bool) – Deselect On Nothing, Deselect all when nothing under the cursor (optional)
- **select_passthrough** (bool) – Only Select Unselected, Ignore the select action when the element is already selected (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.gizmogroup.gizmo_tweak"></a>

### bpy.ops.gizmogroup.gizmo_tweak()

Tweak the active gizmo

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]
