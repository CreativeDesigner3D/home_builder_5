<!-- source: Blender Python API reference 5.2 / bpy.ops.transform.html -->

<a id="module-bpy.ops.transform"></a>

# Transform Operators

<a id="bpy.ops.transform.bbone_resize"></a>

### bpy.ops.transform.bbone_resize(*, value=(1.0, 1.0, 1.0), orient_type='GLOBAL', orient_matrix=((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)), orient_matrix_type='GLOBAL', constraint_axis=(False, False, False), mirror=False, release_confirm=False, use_accurate=False)

Scale selected bendy bones display size

**Parameters:**

- **value** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Display Size, (array of 3 items, in [-inf, inf], optional)
- **orient_type** (str) – Orientation, Transformation orientation (optional)
- **orient_matrix** ([`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix") | Sequence[Sequence[float]]) – Matrix, (multi-dimensional array of 3 * 3 items, in [-inf, inf], optional)
- **orient_matrix_type** (str) – Matrix Orientation, (optional)
- **constraint_axis** (Sequence[bool]) – Constraint Axis, (array of 3 items, optional)
- **mirror** (bool) – Mirror Editing, (optional)
- **release_confirm** (bool) – Confirm on Release, Always confirm operation when releasing button (optional)
- **use_accurate** (bool) – Accurate, Use accurate transformation (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.transform.bend"></a>

### bpy.ops.transform.bend(*, value=(0.0,), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1.0, use_proportional_connected=False, use_proportional_projected=False, snap=False, gpencil_strokes=False, center_override=(0.0, 0.0, 0.0), release_confirm=False, use_accurate=False)

Bend selected items between the 3D cursor and the mouse

**Parameters:**

- **value** (Sequence[float]) – Angle, (array of 1 items, in [-inf, inf], optional)
- **mirror** (bool) – Mirror Editing, (optional)
- **use_proportional_edit** (bool) – Proportional Editing, (optional)
- **proportional_edit_falloff** (Literal[[Proportional Falloff Items](bpy_types_enum_items/proportional_falloff_items.md#rna-enum-proportional-falloff-items)]) – Proportional Falloff, Falloff type for proportional editing mode (optional)
- **proportional_size** (float) – Proportional Size, (in [1e-06, inf], optional)
- **use_proportional_connected** (bool) – Connected, (optional)
- **use_proportional_projected** (bool) – Projected (2D), (optional)
- **snap** (bool) – Use Snapping Options, (optional)
- **gpencil_strokes** (bool) – Edit Grease Pencil, Edit selected Grease Pencil strokes (optional)
- **center_override** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Center Override, Force using this center value (when set) (array of 3 items, in [-inf, inf], optional)
- **release_confirm** (bool) – Confirm on Release, Always confirm operation when releasing button (optional)
- **use_accurate** (bool) – Accurate, Use accurate transformation (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.transform.create_orientation"></a>

### bpy.ops.transform.create_orientation(*, name='', use_view=False, use=False, overwrite=False)

Create transformation orientation from selection

**Parameters:**

- **name** (str) – Name, Name of the new custom orientation (optional, never None)
- **use_view** (bool) – Use View, Use the current view instead of the active object to create the new orientation (optional)
- **use** (bool) – Use After Creation, Select orientation after its creation (optional)
- **overwrite** (bool) – Overwrite Previous, Overwrite previously created orientation with same name (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.transform.delete_orientation"></a>

### bpy.ops.transform.delete_orientation()

Delete transformation orientation

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.transform.edge_bevelweight"></a>

### bpy.ops.transform.edge_bevelweight(*, value=0.0, snap=False, release_confirm=False, use_accurate=False)

Change the bevel weight of edges

**Parameters:**

- **value** (float) – Factor, (in [-1, 1], optional)
- **snap** (bool) – Use Snapping Options, (optional)
- **release_confirm** (bool) – Confirm on Release, Always confirm operation when releasing button (optional)
- **use_accurate** (bool) – Accurate, Use accurate transformation (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.transform.edge_crease"></a>

### bpy.ops.transform.edge_crease(*, value=0.0, snap=False, release_confirm=False, use_accurate=False)

Change the crease of edges

**Parameters:**

- **value** (float) – Factor, (in [-1, 1], optional)
- **snap** (bool) – Use Snapping Options, (optional)
- **release_confirm** (bool) – Confirm on Release, Always confirm operation when releasing button (optional)
- **use_accurate** (bool) – Accurate, Use accurate transformation (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.transform.edge_slide"></a>

### bpy.ops.transform.edge_slide(*, value=0.0, single_side=False, use_even=False, flipped=False, use_clamp=True, mirror=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False, snap_point=(0.0, 0.0, 0.0), correct_uv=True, release_confirm=False, use_accurate=False)

Slide an edge loop along a mesh

**Parameters:**

- **value** (float) – Factor, (in [-10, 10], optional)
- **single_side** (bool) – Single Side, (optional)
- **use_even** (bool) – Even, Make the edge loop match the shape of the adjacent edge loop (optional)
- **flipped** (bool) – Flipped, When Even mode is active, flips between the two adjacent edge loops (optional)
- **use_clamp** (bool) – Clamp, Clamp within the edge extents (optional)
- **mirror** (bool) – Mirror Editing, (optional)
- **snap** (bool) – Use Snapping Options, (optional)
- **snap_elements** (set[Literal[[Snap Element Items](bpy_types_enum_items/snap_element_items.md#rna-enum-snap-element-items)]]) – Snap to Elements, (optional)
- **use_snap_project** (bool) – Project Individual Elements, (optional)
- **snap_target** (Literal[[Snap Source Items](bpy_types_enum_items/snap_source_items.md#rna-enum-snap-source-items)]) – Snap Base, Point on source that will snap to target (optional)
- **use_snap_self** (bool) – Target: Include Active, (optional)
- **use_snap_edit** (bool) – Target: Include Edit, (optional)
- **use_snap_nonedit** (bool) – Target: Include Non-Edited, (optional)
- **use_snap_selectable** (bool) – Target: Exclude Non-Selectable, (optional)
- **snap_point** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Point, (array of 3 items, in [-inf, inf], optional)
- **correct_uv** (bool) – Correct UVs, Correct UV coordinates when transforming (optional)
- **release_confirm** (bool) – Confirm on Release, Always confirm operation when releasing button (optional)
- **use_accurate** (bool) – Accurate, Use accurate transformation (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.transform.from_gizmo"></a>

### bpy.ops.transform.from_gizmo()

Transform selected items by mode type

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.transform.mirror"></a>

### bpy.ops.transform.mirror(*, orient_type='GLOBAL', orient_matrix=((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)), orient_matrix_type='GLOBAL', constraint_axis=(False, False, False), gpencil_strokes=False, center_override=(0.0, 0.0, 0.0), release_confirm=False, use_accurate=False)

Mirror selected items around one or more axes

**Parameters:**

- **orient_type** (str) – Orientation, Transformation orientation (optional)
- **orient_matrix** ([`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix") | Sequence[Sequence[float]]) – Matrix, (multi-dimensional array of 3 * 3 items, in [-inf, inf], optional)
- **orient_matrix_type** (str) – Matrix Orientation, (optional)
- **constraint_axis** (Sequence[bool]) – Constraint Axis, (array of 3 items, optional)
- **gpencil_strokes** (bool) – Edit Grease Pencil, Edit selected Grease Pencil strokes (optional)
- **center_override** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Center Override, Force using this center value (when set) (array of 3 items, in [-inf, inf], optional)
- **release_confirm** (bool) – Confirm on Release, Always confirm operation when releasing button (optional)
- **use_accurate** (bool) – Accurate, Use accurate transformation (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.transform.push_pull"></a>

### bpy.ops.transform.push_pull(*, value=0.0, mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1.0, use_proportional_connected=False, use_proportional_projected=False, snap=False, center_override=(0.0, 0.0, 0.0), release_confirm=False, use_accurate=False)

Push/Pull selected items

**Parameters:**

- **value** (float) – Distance, (in [-inf, inf], optional)
- **mirror** (bool) – Mirror Editing, (optional)
- **use_proportional_edit** (bool) – Proportional Editing, (optional)
- **proportional_edit_falloff** (Literal[[Proportional Falloff Items](bpy_types_enum_items/proportional_falloff_items.md#rna-enum-proportional-falloff-items)]) – Proportional Falloff, Falloff type for proportional editing mode (optional)
- **proportional_size** (float) – Proportional Size, (in [1e-06, inf], optional)
- **use_proportional_connected** (bool) – Connected, (optional)
- **use_proportional_projected** (bool) – Projected (2D), (optional)
- **snap** (bool) – Use Snapping Options, (optional)
- **center_override** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Center Override, Force using this center value (when set) (array of 3 items, in [-inf, inf], optional)
- **release_confirm** (bool) – Confirm on Release, Always confirm operation when releasing button (optional)
- **use_accurate** (bool) – Accurate, Use accurate transformation (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.transform.resize"></a>

### bpy.ops.transform.resize(*, value=(1.0, 1.0, 1.0), mouse_dir_constraint=(0.0, 0.0, 0.0), orient_type='GLOBAL', orient_matrix=((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)), orient_matrix_type='GLOBAL', constraint_axis=(False, False, False), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1.0, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False, snap_point=(0.0, 0.0, 0.0), gpencil_strokes=False, texture_space=False, remove_on_cancel=False, use_duplicated_keyframes=False, center_override=(0.0, 0.0, 0.0), release_confirm=False, use_accurate=False)

Scale (resize) selected items

**Parameters:**

- **value** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Scale, (array of 3 items, in [-inf, inf], optional)
- **mouse_dir_constraint** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Mouse Directional Constraint, (array of 3 items, in [-inf, inf], optional)
- **orient_type** (str) – Orientation, Transformation orientation (optional)
- **orient_matrix** ([`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix") | Sequence[Sequence[float]]) – Matrix, (multi-dimensional array of 3 * 3 items, in [-inf, inf], optional)
- **orient_matrix_type** (str) – Matrix Orientation, (optional)
- **constraint_axis** (Sequence[bool]) – Constraint Axis, (array of 3 items, optional)
- **mirror** (bool) – Mirror Editing, (optional)
- **use_proportional_edit** (bool) – Proportional Editing, (optional)
- **proportional_edit_falloff** (Literal[[Proportional Falloff Items](bpy_types_enum_items/proportional_falloff_items.md#rna-enum-proportional-falloff-items)]) – Proportional Falloff, Falloff type for proportional editing mode (optional)
- **proportional_size** (float) – Proportional Size, (in [1e-06, inf], optional)
- **use_proportional_connected** (bool) – Connected, (optional)
- **use_proportional_projected** (bool) – Projected (2D), (optional)
- **snap** (bool) – Use Snapping Options, (optional)
- **snap_elements** (set[Literal[[Snap Element Items](bpy_types_enum_items/snap_element_items.md#rna-enum-snap-element-items)]]) – Snap to Elements, (optional)
- **use_snap_project** (bool) – Project Individual Elements, (optional)
- **snap_target** (Literal[[Snap Source Items](bpy_types_enum_items/snap_source_items.md#rna-enum-snap-source-items)]) – Snap Base, Point on source that will snap to target (optional)
- **use_snap_self** (bool) – Target: Include Active, (optional)
- **use_snap_edit** (bool) – Target: Include Edit, (optional)
- **use_snap_nonedit** (bool) – Target: Include Non-Edited, (optional)
- **use_snap_selectable** (bool) – Target: Exclude Non-Selectable, (optional)
- **snap_point** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Point, (array of 3 items, in [-inf, inf], optional)
- **gpencil_strokes** (bool) – Edit Grease Pencil, Edit selected Grease Pencil strokes (optional)
- **texture_space** (bool) – Edit Texture Space, Edit object data texture space (optional)
- **remove_on_cancel** (bool) – Remove on Cancel, Remove elements on cancel (optional)
- **use_duplicated_keyframes** (bool) – Duplicated Keyframes, Transform duplicated keyframes (optional)
- **center_override** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Center Override, Force using this center value (when set) (array of 3 items, in [-inf, inf], optional)
- **release_confirm** (bool) – Confirm on Release, Always confirm operation when releasing button (optional)
- **use_accurate** (bool) – Accurate, Use accurate transformation (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.transform.rotate"></a>

### bpy.ops.transform.rotate(*, value=0.0, orient_axis='Z', orient_type='GLOBAL', orient_matrix=((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)), orient_matrix_type='GLOBAL', constraint_axis=(False, False, False), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1.0, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False, snap_point=(0.0, 0.0, 0.0), gpencil_strokes=False, center_override=(0.0, 0.0, 0.0), release_confirm=False, use_accurate=False)

Rotate selected items

**Parameters:**

- **value** (float) – Angle, (in [-inf, inf], optional)
- **orient_axis** (Literal[[Axis Xyz Items](bpy_types_enum_items/axis_xyz_items.md#rna-enum-axis-xyz-items)]) – Axis, (optional)
- **orient_type** (str) – Orientation, Transformation orientation (optional)
- **orient_matrix** ([`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix") | Sequence[Sequence[float]]) – Matrix, (multi-dimensional array of 3 * 3 items, in [-inf, inf], optional)
- **orient_matrix_type** (str) – Matrix Orientation, (optional)
- **constraint_axis** (Sequence[bool]) – Constraint Axis, (array of 3 items, optional)
- **mirror** (bool) – Mirror Editing, (optional)
- **use_proportional_edit** (bool) – Proportional Editing, (optional)
- **proportional_edit_falloff** (Literal[[Proportional Falloff Items](bpy_types_enum_items/proportional_falloff_items.md#rna-enum-proportional-falloff-items)]) – Proportional Falloff, Falloff type for proportional editing mode (optional)
- **proportional_size** (float) – Proportional Size, (in [1e-06, inf], optional)
- **use_proportional_connected** (bool) – Connected, (optional)
- **use_proportional_projected** (bool) – Projected (2D), (optional)
- **snap** (bool) – Use Snapping Options, (optional)
- **snap_elements** (set[Literal[[Snap Element Items](bpy_types_enum_items/snap_element_items.md#rna-enum-snap-element-items)]]) – Snap to Elements, (optional)
- **use_snap_project** (bool) – Project Individual Elements, (optional)
- **snap_target** (Literal[[Snap Source Items](bpy_types_enum_items/snap_source_items.md#rna-enum-snap-source-items)]) – Snap Base, Point on source that will snap to target (optional)
- **use_snap_self** (bool) – Target: Include Active, (optional)
- **use_snap_edit** (bool) – Target: Include Edit, (optional)
- **use_snap_nonedit** (bool) – Target: Include Non-Edited, (optional)
- **use_snap_selectable** (bool) – Target: Exclude Non-Selectable, (optional)
- **snap_point** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Point, (array of 3 items, in [-inf, inf], optional)
- **gpencil_strokes** (bool) – Edit Grease Pencil, Edit selected Grease Pencil strokes (optional)
- **center_override** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Center Override, Force using this center value (when set) (array of 3 items, in [-inf, inf], optional)
- **release_confirm** (bool) – Confirm on Release, Always confirm operation when releasing button (optional)
- **use_accurate** (bool) – Accurate, Use accurate transformation (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.transform.rotate_normal"></a>

### bpy.ops.transform.rotate_normal(*, value=0.0, orient_axis='Z', orient_type='GLOBAL', orient_matrix=((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)), orient_matrix_type='GLOBAL', constraint_axis=(False, False, False), mirror=False, release_confirm=False, use_accurate=False)

Rotate custom normal of selected items

**Parameters:**

- **value** (float) – Angle, (in [-inf, inf], optional)
- **orient_axis** (Literal[[Axis Xyz Items](bpy_types_enum_items/axis_xyz_items.md#rna-enum-axis-xyz-items)]) – Axis, (optional)
- **orient_type** (str) – Orientation, Transformation orientation (optional)
- **orient_matrix** ([`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix") | Sequence[Sequence[float]]) – Matrix, (multi-dimensional array of 3 * 3 items, in [-inf, inf], optional)
- **orient_matrix_type** (str) – Matrix Orientation, (optional)
- **constraint_axis** (Sequence[bool]) – Constraint Axis, (array of 3 items, optional)
- **mirror** (bool) – Mirror Editing, (optional)
- **release_confirm** (bool) – Confirm on Release, Always confirm operation when releasing button (optional)
- **use_accurate** (bool) – Accurate, Use accurate transformation (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.transform.select_orientation"></a>

### bpy.ops.transform.select_orientation(*, orientation='GLOBAL')

Select transformation orientation

**Parameters:**

**orientation** (str) – Orientation, Transformation orientation (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.transform.seq_slide"></a>

### bpy.ops.transform.seq_slide(*, value=(0.0, 0.0), use_restore_handle_selection=False, snap=False, texture_space=False, remove_on_cancel=False, use_duplicated_keyframes=False, view2d_edge_pan=False, release_confirm=False, use_accurate=False)

Slide a sequence strip in time

**Parameters:**

- **value** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Offset, (array of 2 items, in [-inf, inf], optional)
- **use_restore_handle_selection** (bool) – Restore Handle Selection, Restore handle selection after tweaking (optional)
- **snap** (bool) – Use Snapping Options, (optional)
- **texture_space** (bool) – Edit Texture Space, Edit object data texture space (optional)
- **remove_on_cancel** (bool) – Remove on Cancel, Remove elements on cancel (optional)
- **use_duplicated_keyframes** (bool) – Duplicated Keyframes, Transform duplicated keyframes (optional)
- **view2d_edge_pan** (bool) – Edge Pan, Enable edge panning in 2D view (optional)
- **release_confirm** (bool) – Confirm on Release, Always confirm operation when releasing button (optional)
- **use_accurate** (bool) – Accurate, Use accurate transformation (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.transform.shear"></a>

### bpy.ops.transform.shear(*, angle=0.0, orient_axis='Z', orient_axis_ortho='X', orient_type='GLOBAL', orient_matrix=((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)), orient_matrix_type='GLOBAL', mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1.0, use_proportional_connected=False, use_proportional_projected=False, snap=False, gpencil_strokes=False, release_confirm=False, use_accurate=False)

Shear selected items along the given axis

**Parameters:**

- **angle** (float) – Angle, (in [-inf, inf], optional)
- **orient_axis** (Literal[[Axis Xyz Items](bpy_types_enum_items/axis_xyz_items.md#rna-enum-axis-xyz-items)]) – Axis, (optional)
- **orient_axis_ortho** (Literal[[Axis Xyz Items](bpy_types_enum_items/axis_xyz_items.md#rna-enum-axis-xyz-items)]) – Axis Ortho, (optional)
- **orient_type** (str) – Orientation, Transformation orientation (optional)
- **orient_matrix** ([`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix") | Sequence[Sequence[float]]) – Matrix, (multi-dimensional array of 3 * 3 items, in [-inf, inf], optional)
- **orient_matrix_type** (str) – Matrix Orientation, (optional)
- **mirror** (bool) – Mirror Editing, (optional)
- **use_proportional_edit** (bool) – Proportional Editing, (optional)
- **proportional_edit_falloff** (Literal[[Proportional Falloff Items](bpy_types_enum_items/proportional_falloff_items.md#rna-enum-proportional-falloff-items)]) – Proportional Falloff, Falloff type for proportional editing mode (optional)
- **proportional_size** (float) – Proportional Size, (in [1e-06, inf], optional)
- **use_proportional_connected** (bool) – Connected, (optional)
- **use_proportional_projected** (bool) – Projected (2D), (optional)
- **snap** (bool) – Use Snapping Options, (optional)
- **gpencil_strokes** (bool) – Edit Grease Pencil, Edit selected Grease Pencil strokes (optional)
- **release_confirm** (bool) – Confirm on Release, Always confirm operation when releasing button (optional)
- **use_accurate** (bool) – Accurate, Use accurate transformation (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.transform.shrink_fatten"></a>

### bpy.ops.transform.shrink_fatten(*, value=0.0, use_even_offset=False, mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1.0, use_proportional_connected=False, use_proportional_projected=False, snap=False, release_confirm=False, use_accurate=False)

Shrink/fatten selected vertices along normals

**Parameters:**

- **value** (float) – Offset, (in [-inf, inf], optional)
- **use_even_offset** (bool) – Offset Even, Scale the offset to give more even thickness (optional)
- **mirror** (bool) – Mirror Editing, (optional)
- **use_proportional_edit** (bool) – Proportional Editing, (optional)
- **proportional_edit_falloff** (Literal[[Proportional Falloff Items](bpy_types_enum_items/proportional_falloff_items.md#rna-enum-proportional-falloff-items)]) – Proportional Falloff, Falloff type for proportional editing mode (optional)
- **proportional_size** (float) – Proportional Size, (in [1e-06, inf], optional)
- **use_proportional_connected** (bool) – Connected, (optional)
- **use_proportional_projected** (bool) – Projected (2D), (optional)
- **snap** (bool) – Use Snapping Options, (optional)
- **release_confirm** (bool) – Confirm on Release, Always confirm operation when releasing button (optional)
- **use_accurate** (bool) – Accurate, Use accurate transformation (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.transform.skin_resize"></a>

### bpy.ops.transform.skin_resize(*, value=(1.0, 1.0, 1.0), orient_type='GLOBAL', orient_matrix=((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)), orient_matrix_type='GLOBAL', constraint_axis=(False, False, False), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1.0, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False, snap_point=(0.0, 0.0, 0.0), release_confirm=False, use_accurate=False)

Scale selected vertices’ skin radii

**Parameters:**

- **value** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Scale, (array of 3 items, in [-inf, inf], optional)
- **orient_type** (str) – Orientation, Transformation orientation (optional)
- **orient_matrix** ([`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix") | Sequence[Sequence[float]]) – Matrix, (multi-dimensional array of 3 * 3 items, in [-inf, inf], optional)
- **orient_matrix_type** (str) – Matrix Orientation, (optional)
- **constraint_axis** (Sequence[bool]) – Constraint Axis, (array of 3 items, optional)
- **mirror** (bool) – Mirror Editing, (optional)
- **use_proportional_edit** (bool) – Proportional Editing, (optional)
- **proportional_edit_falloff** (Literal[[Proportional Falloff Items](bpy_types_enum_items/proportional_falloff_items.md#rna-enum-proportional-falloff-items)]) – Proportional Falloff, Falloff type for proportional editing mode (optional)
- **proportional_size** (float) – Proportional Size, (in [1e-06, inf], optional)
- **use_proportional_connected** (bool) – Connected, (optional)
- **use_proportional_projected** (bool) – Projected (2D), (optional)
- **snap** (bool) – Use Snapping Options, (optional)
- **snap_elements** (set[Literal[[Snap Element Items](bpy_types_enum_items/snap_element_items.md#rna-enum-snap-element-items)]]) – Snap to Elements, (optional)
- **use_snap_project** (bool) – Project Individual Elements, (optional)
- **snap_target** (Literal[[Snap Source Items](bpy_types_enum_items/snap_source_items.md#rna-enum-snap-source-items)]) – Snap Base, Point on source that will snap to target (optional)
- **use_snap_self** (bool) – Target: Include Active, (optional)
- **use_snap_edit** (bool) – Target: Include Edit, (optional)
- **use_snap_nonedit** (bool) – Target: Include Non-Edited, (optional)
- **use_snap_selectable** (bool) – Target: Exclude Non-Selectable, (optional)
- **snap_point** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Point, (array of 3 items, in [-inf, inf], optional)
- **release_confirm** (bool) – Confirm on Release, Always confirm operation when releasing button (optional)
- **use_accurate** (bool) – Accurate, Use accurate transformation (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.transform.tilt"></a>

### bpy.ops.transform.tilt(*, value=0.0, mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1.0, use_proportional_connected=False, use_proportional_projected=False, snap=False, release_confirm=False, use_accurate=False)

Tilt selected control vertices of 3D curve

**Parameters:**

- **value** (float) – Angle, (in [-inf, inf], optional)
- **mirror** (bool) – Mirror Editing, (optional)
- **use_proportional_edit** (bool) – Proportional Editing, (optional)
- **proportional_edit_falloff** (Literal[[Proportional Falloff Items](bpy_types_enum_items/proportional_falloff_items.md#rna-enum-proportional-falloff-items)]) – Proportional Falloff, Falloff type for proportional editing mode (optional)
- **proportional_size** (float) – Proportional Size, (in [1e-06, inf], optional)
- **use_proportional_connected** (bool) – Connected, (optional)
- **use_proportional_projected** (bool) – Projected (2D), (optional)
- **snap** (bool) – Use Snapping Options, (optional)
- **release_confirm** (bool) – Confirm on Release, Always confirm operation when releasing button (optional)
- **use_accurate** (bool) – Accurate, Use accurate transformation (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.transform.tosphere"></a>

### bpy.ops.transform.tosphere(*, value=0.0, mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1.0, use_proportional_connected=False, use_proportional_projected=False, snap=False, gpencil_strokes=False, center_override=(0.0, 0.0, 0.0), release_confirm=False, use_accurate=False)

Move selected items outward in a spherical shape around geometric center

**Parameters:**

- **value** (float) – Factor, (in [0, 1], optional)
- **mirror** (bool) – Mirror Editing, (optional)
- **use_proportional_edit** (bool) – Proportional Editing, (optional)
- **proportional_edit_falloff** (Literal[[Proportional Falloff Items](bpy_types_enum_items/proportional_falloff_items.md#rna-enum-proportional-falloff-items)]) – Proportional Falloff, Falloff type for proportional editing mode (optional)
- **proportional_size** (float) – Proportional Size, (in [1e-06, inf], optional)
- **use_proportional_connected** (bool) – Connected, (optional)
- **use_proportional_projected** (bool) – Projected (2D), (optional)
- **snap** (bool) – Use Snapping Options, (optional)
- **gpencil_strokes** (bool) – Edit Grease Pencil, Edit selected Grease Pencil strokes (optional)
- **center_override** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Center Override, Force using this center value (when set) (array of 3 items, in [-inf, inf], optional)
- **release_confirm** (bool) – Confirm on Release, Always confirm operation when releasing button (optional)
- **use_accurate** (bool) – Accurate, Use accurate transformation (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.transform.trackball"></a>

### bpy.ops.transform.trackball(*, value=(0.0, 0.0), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1.0, use_proportional_connected=False, use_proportional_projected=False, snap=False, gpencil_strokes=False, center_override=(0.0, 0.0, 0.0), release_confirm=False, use_accurate=False)

Trackball style rotation of selected items

**Parameters:**

- **value** (Sequence[float]) – Angle, (array of 2 items, in [-inf, inf], optional)
- **mirror** (bool) – Mirror Editing, (optional)
- **use_proportional_edit** (bool) – Proportional Editing, (optional)
- **proportional_edit_falloff** (Literal[[Proportional Falloff Items](bpy_types_enum_items/proportional_falloff_items.md#rna-enum-proportional-falloff-items)]) – Proportional Falloff, Falloff type for proportional editing mode (optional)
- **proportional_size** (float) – Proportional Size, (in [1e-06, inf], optional)
- **use_proportional_connected** (bool) – Connected, (optional)
- **use_proportional_projected** (bool) – Projected (2D), (optional)
- **snap** (bool) – Use Snapping Options, (optional)
- **gpencil_strokes** (bool) – Edit Grease Pencil, Edit selected Grease Pencil strokes (optional)
- **center_override** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Center Override, Force using this center value (when set) (array of 3 items, in [-inf, inf], optional)
- **release_confirm** (bool) – Confirm on Release, Always confirm operation when releasing button (optional)
- **use_accurate** (bool) – Accurate, Use accurate transformation (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.transform.transform"></a>

### bpy.ops.transform.transform(*, mode='TRANSLATION', value=(0.0, 0.0, 0.0, 0.0), orient_axis='Z', orient_type='GLOBAL', orient_matrix=((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)), orient_matrix_type='GLOBAL', constraint_axis=(False, False, False), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1.0, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False, snap_point=(0.0, 0.0, 0.0), snap_align=False, snap_normal=(0.0, 0.0, 0.0), gpencil_strokes=False, texture_space=False, remove_on_cancel=False, use_duplicated_keyframes=False, center_override=(0.0, 0.0, 0.0), release_confirm=False, use_accurate=False, use_automerge_and_split=False)

Transform selected items by mode type

**Parameters:**

- **mode** (Literal[[Transform Mode Type Items](bpy_types_enum_items/transform_mode_type_items.md#rna-enum-transform-mode-type-items)]) – Mode, (optional)
- **value** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Values, (array of 4 items, in [-inf, inf], optional)
- **orient_axis** (Literal[[Axis Xyz Items](bpy_types_enum_items/axis_xyz_items.md#rna-enum-axis-xyz-items)]) – Axis, (optional)
- **orient_type** (Literal[[Transform Orientation Items](bpy_types_enum_items/transform_orientation_items.md#rna-enum-transform-orientation-items)]) – Orientation, Transformation orientation (optional)
- **orient_matrix** ([`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix") | Sequence[Sequence[float]]) – Matrix, (multi-dimensional array of 3 * 3 items, in [-inf, inf], optional)
- **orient_matrix_type** (Literal[[Transform Orientation Items](bpy_types_enum_items/transform_orientation_items.md#rna-enum-transform-orientation-items)]) – Matrix Orientation, (optional)
- **constraint_axis** (Sequence[bool]) – Constraint Axis, (array of 3 items, optional)
- **mirror** (bool) – Mirror Editing, (optional)
- **use_proportional_edit** (bool) – Proportional Editing, (optional)
- **proportional_edit_falloff** (Literal[[Proportional Falloff Items](bpy_types_enum_items/proportional_falloff_items.md#rna-enum-proportional-falloff-items)]) – Proportional Falloff, Falloff type for proportional editing mode (optional)
- **proportional_size** (float) – Proportional Size, (in [1e-06, inf], optional)
- **use_proportional_connected** (bool) – Connected, (optional)
- **use_proportional_projected** (bool) – Projected (2D), (optional)
- **snap** (bool) – Use Snapping Options, (optional)
- **snap_elements** (set[Literal[[Snap Element Items](bpy_types_enum_items/snap_element_items.md#rna-enum-snap-element-items)]]) – Snap to Elements, (optional)
- **use_snap_project** (bool) – Project Individual Elements, (optional)
- **snap_target** (Literal[[Snap Source Items](bpy_types_enum_items/snap_source_items.md#rna-enum-snap-source-items)]) – Snap Base, Point on source that will snap to target (optional)
- **use_snap_self** (bool) – Target: Include Active, (optional)
- **use_snap_edit** (bool) – Target: Include Edit, (optional)
- **use_snap_nonedit** (bool) – Target: Include Non-Edited, (optional)
- **use_snap_selectable** (bool) – Target: Exclude Non-Selectable, (optional)
- **snap_point** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Point, (array of 3 items, in [-inf, inf], optional)
- **snap_align** (bool) – Align with Point Normal, (optional)
- **snap_normal** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Normal, (array of 3 items, in [-inf, inf], optional)
- **gpencil_strokes** (bool) – Edit Grease Pencil, Edit selected Grease Pencil strokes (optional)
- **texture_space** (bool) – Edit Texture Space, Edit object data texture space (optional)
- **remove_on_cancel** (bool) – Remove on Cancel, Remove elements on cancel (optional)
- **use_duplicated_keyframes** (bool) – Duplicated Keyframes, Transform duplicated keyframes (optional)
- **center_override** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Center Override, Force using this center value (when set) (array of 3 items, in [-inf, inf], optional)
- **release_confirm** (bool) – Confirm on Release, Always confirm operation when releasing button (optional)
- **use_accurate** (bool) – Accurate, Use accurate transformation (optional)
- **use_automerge_and_split** (bool) – Auto Merge & Split, Forces the use of Auto Merge and Split (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.transform.translate"></a>

### bpy.ops.transform.translate(*, value=(0.0, 0.0, 0.0), orient_type='GLOBAL', orient_matrix=((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)), orient_matrix_type='GLOBAL', constraint_axis=(False, False, False), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1.0, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False, snap_point=(0.0, 0.0, 0.0), snap_align=False, snap_normal=(0.0, 0.0, 0.0), gpencil_strokes=False, cursor_transform=False, texture_space=False, remove_on_cancel=False, use_duplicated_keyframes=False, view2d_edge_pan=False, release_confirm=False, use_accurate=False, use_automerge_and_split=False, translate_origin=False)

Move selected items

**Parameters:**

- **value** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Move, (array of 3 items, in [-inf, inf], optional)
- **orient_type** (Literal[[Transform Orientation Items](bpy_types_enum_items/transform_orientation_items.md#rna-enum-transform-orientation-items)]) – Orientation, Transformation orientation (optional)
- **orient_matrix** ([`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix") | Sequence[Sequence[float]]) – Matrix, (multi-dimensional array of 3 * 3 items, in [-inf, inf], optional)
- **orient_matrix_type** (Literal[[Transform Orientation Items](bpy_types_enum_items/transform_orientation_items.md#rna-enum-transform-orientation-items)]) – Matrix Orientation, (optional)
- **constraint_axis** (Sequence[bool]) – Constraint Axis, (array of 3 items, optional)
- **mirror** (bool) – Mirror Editing, (optional)
- **use_proportional_edit** (bool) – Proportional Editing, (optional)
- **proportional_edit_falloff** (Literal[[Proportional Falloff Items](bpy_types_enum_items/proportional_falloff_items.md#rna-enum-proportional-falloff-items)]) – Proportional Falloff, Falloff type for proportional editing mode (optional)
- **proportional_size** (float) – Proportional Size, (in [1e-06, inf], optional)
- **use_proportional_connected** (bool) – Connected, (optional)
- **use_proportional_projected** (bool) – Projected (2D), (optional)
- **snap** (bool) – Use Snapping Options, (optional)
- **snap_elements** (set[Literal[[Snap Element Items](bpy_types_enum_items/snap_element_items.md#rna-enum-snap-element-items)]]) – Snap to Elements, (optional)
- **use_snap_project** (bool) – Project Individual Elements, (optional)
- **snap_target** (Literal[[Snap Source Items](bpy_types_enum_items/snap_source_items.md#rna-enum-snap-source-items)]) – Snap Base, Point on source that will snap to target (optional)
- **use_snap_self** (bool) – Target: Include Active, (optional)
- **use_snap_edit** (bool) – Target: Include Edit, (optional)
- **use_snap_nonedit** (bool) – Target: Include Non-Edited, (optional)
- **use_snap_selectable** (bool) – Target: Exclude Non-Selectable, (optional)
- **snap_point** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Point, (array of 3 items, in [-inf, inf], optional)
- **snap_align** (bool) – Align with Point Normal, (optional)
- **snap_normal** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Normal, (array of 3 items, in [-inf, inf], optional)
- **gpencil_strokes** (bool) – Edit Grease Pencil, Edit selected Grease Pencil strokes (optional)
- **cursor_transform** (bool) – Transform Cursor, (optional)
- **texture_space** (bool) – Edit Texture Space, Edit object data texture space (optional)
- **remove_on_cancel** (bool) – Remove on Cancel, Remove elements on cancel (optional)
- **use_duplicated_keyframes** (bool) – Duplicated Keyframes, Transform duplicated keyframes (optional)
- **view2d_edge_pan** (bool) – Edge Pan, Enable edge panning in 2D view (optional)
- **release_confirm** (bool) – Confirm on Release, Always confirm operation when releasing button (optional)
- **use_accurate** (bool) – Accurate, Use accurate transformation (optional)
- **use_automerge_and_split** (bool) – Auto Merge & Split, Forces the use of Auto Merge and Split (optional)
- **translate_origin** (bool) – Translate Origin, Translate origin instead of selection (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.transform.vert_crease"></a>

### bpy.ops.transform.vert_crease(*, value=0.0, snap=False, release_confirm=False, use_accurate=False)

Change the crease of vertices

**Parameters:**

- **value** (float) – Factor, (in [-1, 1], optional)
- **snap** (bool) – Use Snapping Options, (optional)
- **release_confirm** (bool) – Confirm on Release, Always confirm operation when releasing button (optional)
- **use_accurate** (bool) – Accurate, Use accurate transformation (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.transform.vert_slide"></a>

### bpy.ops.transform.vert_slide(*, value=0.0, use_even=False, flipped=False, use_clamp=True, direction=(0.0, 0.0, 0.0), mirror=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False, snap_point=(0.0, 0.0, 0.0), correct_uv=True, release_confirm=False, use_accurate=False)

Slide a vertex along a mesh

**Parameters:**

- **value** (float) – Factor, (in [-10, 10], optional)
- **use_even** (bool) – Even, Make the edge loop match the shape of the adjacent edge loop (optional)
- **flipped** (bool) – Flipped, When Even mode is active, flips between the two adjacent edge loops (optional)
- **use_clamp** (bool) – Clamp, Clamp within the edge extents (optional)
- **direction** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Slide Direction, World-space direction (array of 3 items, in [-inf, inf], optional)
- **mirror** (bool) – Mirror Editing, (optional)
- **snap** (bool) – Use Snapping Options, (optional)
- **snap_elements** (set[Literal[[Snap Element Items](bpy_types_enum_items/snap_element_items.md#rna-enum-snap-element-items)]]) – Snap to Elements, (optional)
- **use_snap_project** (bool) – Project Individual Elements, (optional)
- **snap_target** (Literal[[Snap Source Items](bpy_types_enum_items/snap_source_items.md#rna-enum-snap-source-items)]) – Snap Base, Point on source that will snap to target (optional)
- **use_snap_self** (bool) – Target: Include Active, (optional)
- **use_snap_edit** (bool) – Target: Include Edit, (optional)
- **use_snap_nonedit** (bool) – Target: Include Non-Edited, (optional)
- **use_snap_selectable** (bool) – Target: Exclude Non-Selectable, (optional)
- **snap_point** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Point, (array of 3 items, in [-inf, inf], optional)
- **correct_uv** (bool) – Correct UVs, Correct UV coordinates when transforming (optional)
- **release_confirm** (bool) – Confirm on Release, Always confirm operation when releasing button (optional)
- **use_accurate** (bool) – Accurate, Use accurate transformation (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.transform.vertex_random"></a>

### bpy.ops.transform.vertex_random(*, offset=0.0, uniform=0.0, normal=0.0, seed=0, wait_for_input=True)

Randomize vertices

**Parameters:**

- **offset** (float) – Amount, Distance to offset (in [-inf, inf], optional)
- **uniform** (float) – Uniform, Increase for uniform offset distance (in [0, 1], optional)
- **normal** (float) – Normal, Align offset direction to normals (in [0, 1], optional)
- **seed** (int) – Random Seed, Seed for the random number generator (in [0, 10000], optional)
- **wait_for_input** (bool) – Wait for Input, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.transform.vertex_warp"></a>

### bpy.ops.transform.vertex_warp(*, warp_angle=6.28319, offset_angle=0.0, min=-1.0, max=1.0, viewmat=((0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0)), center=(0.0, 0.0, 0.0))

Warp vertices around the cursor

**Parameters:**

- **warp_angle** (float) – Warp Angle, Amount to warp about the cursor (in [-inf, inf], optional)
- **offset_angle** (float) – Offset Angle, Angle to use as the basis for warping (in [-inf, inf], optional)
- **min** (float) – Min, (in [-inf, inf], optional)
- **max** (float) – Max, (in [-inf, inf], optional)
- **viewmat** ([`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix") | Sequence[Sequence[float]]) – Matrix, (multi-dimensional array of 4 * 4 items, in [-inf, inf], optional)
- **center** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Center, (array of 3 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]
