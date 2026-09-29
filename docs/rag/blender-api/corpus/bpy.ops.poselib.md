<!-- source: Blender Python API reference 5.2 / bpy.ops.poselib.html -->

<a id="module-bpy.ops.poselib"></a>

# Poselib Operators

<a id="bpy.ops.poselib.apply_pose_asset"></a>

### bpy.ops.poselib.apply_pose_asset(*, asset_library_type='LOCAL', asset_library_identifier='', relative_asset_identifier='', blend_factor=1.0, flipped=False)

Apply the given Pose Action to the rig

**Parameters:**

- **asset_library_type** (Literal[[Asset Library Type Items](bpy_types_enum_items/asset_library_type_items.md#rna-enum-asset-library-type-items)]) – Asset Library Type, (optional)
- **asset_library_identifier** (str) – Asset Library Identifier, (optional, never None)
- **relative_asset_identifier** (str) – Relative Asset Identifier, (optional, never None)
- **blend_factor** (float) – Blend Factor, Amount that the pose is applied on top of the existing poses. A negative value will subtract the pose instead of adding it (in [-inf, inf], optional)
- **flipped** (bool) – Apply Flipped, When enabled, applies the pose flipped over the X-axis (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.poselib.asset_delete"></a>

### bpy.ops.poselib.asset_delete()

Delete the selected Pose Asset

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.poselib.asset_modify"></a>

### bpy.ops.poselib.asset_modify(*, mode='ADJUST')

Update the selected pose asset in the asset library from the currently selected bones. The mode defines how the asset is updated

**Parameters:**

**mode** (Literal['ADJUST', 'REPLACE', 'ADD', 'REMOVE']) –

Overwrite Mode, Specify which parts of the pose asset are overwritten (optional)

- `ADJUST`
  Adjust – Update existing channels in the pose asset but don’t remove or add any channels.
- `REPLACE`
  Replace with Selection – Completely replace all channels in the pose asset with the current selection.
- `ADD`
  Add Selected Bones – Add channels of the selection to the pose asset. Existing channels will be updated.
- `REMOVE`
  Remove Selected Bones – Remove channels of the selection from the pose asset.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.poselib.blend_pose_asset"></a>

### bpy.ops.poselib.blend_pose_asset(*, asset_library_type='LOCAL', asset_library_identifier='', relative_asset_identifier='', blend_factor=0.0, flipped=False, release_confirm=False)

Blend the given Pose Action to the rig

**Parameters:**

- **asset_library_type** (Literal[[Asset Library Type Items](bpy_types_enum_items/asset_library_type_items.md#rna-enum-asset-library-type-items)]) – Asset Library Type, (optional)
- **asset_library_identifier** (str) – Asset Library Identifier, (optional, never None)
- **relative_asset_identifier** (str) – Relative Asset Identifier, (optional, never None)
- **blend_factor** (float) – Blend Factor, Amount that the pose is applied on top of the existing poses. A negative value will subtract the pose instead of adding it (in [-inf, inf], optional)
- **flipped** (bool) – Apply Flipped, When enabled, applies the pose flipped over the X-axis (optional)
- **release_confirm** (bool) – Confirm on Release, Always confirm operation when releasing button (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.poselib.copy_as_asset"></a>

### bpy.ops.poselib.copy_as_asset()

Create a new pose asset on the clipboard, to be pasted into an Asset Browser

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[addons_core/pose_library/operators.py:116](https://projects.blender.org/blender/blender/src/branch/main/scripts/addons_core/pose_library/operators.py#L116)

<a id="bpy.ops.poselib.create_pose_asset"></a>

### bpy.ops.poselib.create_pose_asset(*, pose_name='', asset_library_reference='LOCAL', catalog_path='')

Create a new asset from the selected bones in the scene

**Parameters:**

- **pose_name** (str) – Pose Name, Name for the new pose asset (optional, never None)
- **asset_library_reference** (str) – Library, Asset library used to store the new pose (optional)
- **catalog_path** (str) – Catalog, Catalog to use for the new asset (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.poselib.paste_asset"></a>

### bpy.ops.poselib.paste_asset()

Paste the Asset that was previously copied using Copy As Asset

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[addons_core/pose_library/operators.py:190](https://projects.blender.org/blender/blender/src/branch/main/scripts/addons_core/pose_library/operators.py#L190)

<a id="bpy.ops.poselib.pose_asset_select_bones"></a>

### bpy.ops.poselib.pose_asset_select_bones(*, select=True, flipped=False)

Select those bones that are used in this pose

**Parameters:**

- **select** (bool) – Select, (optional)
- **flipped** (bool) – Flipped, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[addons_core/pose_library/operators.py:228](https://projects.blender.org/blender/blender/src/branch/main/scripts/addons_core/pose_library/operators.py#L228)

<a id="bpy.ops.poselib.restore_previous_action"></a>

### bpy.ops.poselib.restore_previous_action()

Switch back to the previous Action, after creating a pose asset

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[addons_core/pose_library/operators.py:65](https://projects.blender.org/blender/blender/src/branch/main/scripts/addons_core/pose_library/operators.py#L65)
