<!-- source: Blender Python API reference 5.2 / bpy.ops.pose.html -->

<a id="module-bpy.ops.pose"></a>

# Pose Operators

<a id="bpy.ops.pose.armature_apply"></a>

### bpy.ops.pose.armature_apply(*, selected=False)

Apply the current pose as the new rest pose

**Parameters:**

**selected** (bool) – Selected Only, Only apply the selected bones (with propagation to children) (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.pose.autoside_names"></a>

### bpy.ops.pose.autoside_names(*, axis='XAXIS')

Automatically renames the selected bones according to which side of the target axis they fall on

**Parameters:**

**axis** (Literal['XAXIS', 'YAXIS', 'ZAXIS']) –

Axis, Axis to tag names with (optional)

- `XAXIS`
  X-Axis – Left/Right.
- `YAXIS`
  Y-Axis – Front/Back.
- `ZAXIS`
  Z-Axis – Top/Bottom.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.pose.blend_to_neighbor"></a>

### bpy.ops.pose.blend_to_neighbor(*, factor=0.5, prev_frame=0, next_frame=0, channels='ALL', axis_lock='FREE')

Blend from current position to previous or next keyframe

**Parameters:**

- **factor** (float) – Factor, Weighting factor for which keyframe is favored more (in [0, 1], optional)
- **prev_frame** (int) – Previous Keyframe, Frame number of keyframe immediately before the current frame (in [-1048574, 1048574], optional)
- **next_frame** (int) – Next Keyframe, Frame number of keyframe immediately after the current frame (in [-1048574, 1048574], optional)
- **channels** (Literal['ALL', 'LOC', 'ROT', 'SIZE', 'BBONE', 'CUSTOM']) –

  Channels, Set of properties that are affected (optional)

  - `ALL`
    All Properties – All properties, including transforms, bendy bone shape, and custom properties.
  - `LOC`
    Location – Location only.
  - `ROT`
    Rotation – Rotation only.
  - `SIZE`
    Scale – Scale only.
  - `BBONE`
    Bendy Bone – Bendy Bone shape properties.
  - `CUSTOM`
    Custom Properties – Custom properties.
- **axis_lock** (Literal['FREE', 'X', 'Y', 'Z']) –

  Axis Lock, Transform axis to restrict effects to (optional)

  - `FREE`
    Free – All axes are affected.
  - `X`
    X – Only X-axis transforms are affected.
  - `Y`
    Y – Only Y-axis transforms are affected.
  - `Z`
    Z – Only Z-axis transforms are affected.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.pose.blend_with_rest"></a>

### bpy.ops.pose.blend_with_rest(*, factor=0.5, prev_frame=0, next_frame=0, channels='ALL', axis_lock='FREE')

Make the current pose more similar to, or further away from, the rest pose

**Parameters:**

- **factor** (float) – Factor, Weighting factor for which keyframe is favored more (in [0, 1], optional)
- **prev_frame** (int) – Previous Keyframe, Frame number of keyframe immediately before the current frame (in [-1048574, 1048574], optional)
- **next_frame** (int) – Next Keyframe, Frame number of keyframe immediately after the current frame (in [-1048574, 1048574], optional)
- **channels** (Literal['ALL', 'LOC', 'ROT', 'SIZE', 'BBONE', 'CUSTOM']) –

  Channels, Set of properties that are affected (optional)

  - `ALL`
    All Properties – All properties, including transforms, bendy bone shape, and custom properties.
  - `LOC`
    Location – Location only.
  - `ROT`
    Rotation – Rotation only.
  - `SIZE`
    Scale – Scale only.
  - `BBONE`
    Bendy Bone – Bendy Bone shape properties.
  - `CUSTOM`
    Custom Properties – Custom properties.
- **axis_lock** (Literal['FREE', 'X', 'Y', 'Z']) –

  Axis Lock, Transform axis to restrict effects to (optional)

  - `FREE`
    Free – All axes are affected.
  - `X`
    X – Only X-axis transforms are affected.
  - `Y`
    Y – Only Y-axis transforms are affected.
  - `Z`
    Z – Only Z-axis transforms are affected.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.pose.breakdown"></a>

### bpy.ops.pose.breakdown(*, factor=0.5, prev_frame=0, next_frame=0, channels='ALL', axis_lock='FREE')

Create a suitable breakdown pose on the current frame

**Parameters:**

- **factor** (float) – Factor, Weighting factor for which keyframe is favored more (in [0, 1], optional)
- **prev_frame** (int) – Previous Keyframe, Frame number of keyframe immediately before the current frame (in [-1048574, 1048574], optional)
- **next_frame** (int) – Next Keyframe, Frame number of keyframe immediately after the current frame (in [-1048574, 1048574], optional)
- **channels** (Literal['ALL', 'LOC', 'ROT', 'SIZE', 'BBONE', 'CUSTOM']) –

  Channels, Set of properties that are affected (optional)

  - `ALL`
    All Properties – All properties, including transforms, bendy bone shape, and custom properties.
  - `LOC`
    Location – Location only.
  - `ROT`
    Rotation – Rotation only.
  - `SIZE`
    Scale – Scale only.
  - `BBONE`
    Bendy Bone – Bendy Bone shape properties.
  - `CUSTOM`
    Custom Properties – Custom properties.
- **axis_lock** (Literal['FREE', 'X', 'Y', 'Z']) –

  Axis Lock, Transform axis to restrict effects to (optional)

  - `FREE`
    Free – All axes are affected.
  - `X`
    X – Only X-axis transforms are affected.
  - `Y`
    Y – Only Y-axis transforms are affected.
  - `Z`
    Z – Only Z-axis transforms are affected.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.pose.constraint_add"></a>

### bpy.ops.pose.constraint_add(*, type='CHILD_OF')

Add a constraint to the active bone

**Parameters:**

**type** (Literal[[Constraint Type Items](bpy_types_enum_items/constraint_type_items.md#rna-enum-constraint-type-items)]) – Type, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.pose.constraint_add_with_targets"></a>

### bpy.ops.pose.constraint_add_with_targets(*, type='CHILD_OF')

Add a constraint to the active bone, with target (where applicable) set to the selected Objects/Bones

**Parameters:**

**type** (Literal[[Constraint Type Items](bpy_types_enum_items/constraint_type_items.md#rna-enum-constraint-type-items)]) – Type, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.pose.constraints_clear"></a>

### bpy.ops.pose.constraints_clear()

Clear all constraints from the selected bones

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.pose.constraints_copy"></a>

### bpy.ops.pose.constraints_copy()

Copy constraints to other selected bones

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.pose.copy"></a>

### bpy.ops.pose.copy()

Copy the current pose of the selected bones to the internal clipboard

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.pose.flip_names"></a>

### bpy.ops.pose.flip_names(*, do_strip_numbers=False)

Flips (and corrects) the axis suffixes of the names of selected bones

**Parameters:**

**do_strip_numbers** (bool) – Strip Numbers, Try to remove right-most dot-number from flipped names.Warning: May result in incoherent naming in some cases(optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.pose.hide"></a>

### bpy.ops.pose.hide(*, unselected=False)

Tag selected bones to not be visible in Pose Mode

**Parameters:**

**unselected** (bool) – Unselected, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.pose.ik_add"></a>

### bpy.ops.pose.ik_add(*, with_targets=True)

Add an IK Constraint to the active Bone. The target can be a selected bone or object

**Parameters:**

**with_targets** (bool) – With Targets, Assign IK Constraint with targets derived from the select bones/objects (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.pose.ik_clear"></a>

### bpy.ops.pose.ik_clear()

Remove all IK Constraints from selected bones

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.pose.loc_clear"></a>

### bpy.ops.pose.loc_clear()

Reset locations of selected bones to their default values

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.pose.paste"></a>

### bpy.ops.pose.paste(*, flipped=False, selected_mask=False)

Paste the stored pose on to the current pose

**Parameters:**

- **flipped** (bool) – Flipped on X-Axis, Paste the stored pose flipped on to current pose (optional)
- **selected_mask** (bool) – On Selected Only, Only paste the stored pose on to selected bones in the current pose (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.pose.paths_calculate"></a>

### bpy.ops.pose.paths_calculate(*, display_type='RANGE', range='SCENE', bake_location='HEADS')

Calculate paths for the selected bones

**Parameters:**

- **display_type** (Literal[[Motionpath Display Type Items](bpy_types_enum_items/motionpath_display_type_items.md#rna-enum-motionpath-display-type-items)]) – Display Type, (optional)
- **range** (Literal[[Motionpath Range Items](bpy_types_enum_items/motionpath_range_items.md#rna-enum-motionpath-range-items)]) – Computation Range, (optional)
- **bake_location** (Literal[[Motionpath Bake Location Items](bpy_types_enum_items/motionpath_bake_location_items.md#rna-enum-motionpath-bake-location-items)]) – Bake Location, Which point on the bones is used when calculating paths (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.pose.paths_clear"></a>

### bpy.ops.pose.paths_clear(*, only_selected=False)

Undocumented, consider [contributing](https://developer.blender.org/).

**Parameters:**

**only_selected** (bool) – Only Selected, Only clear motion paths of selected bones (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.pose.paths_range_update"></a>

### bpy.ops.pose.paths_range_update()

Update frame range for motion paths from the Scene’s current frame range

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.pose.paths_update"></a>

### bpy.ops.pose.paths_update()

Recalculate paths for bones that already have them

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.pose.propagate"></a>

### bpy.ops.pose.propagate(*, mode='NEXT_KEY', end_frame=250.0)

Copy selected aspects of the current pose to subsequent poses already keyframed

**Parameters:**

- **mode** (Literal['NEXT_KEY', 'LAST_KEY', 'BEFORE_FRAME', 'BEFORE_END', 'SELECTED_KEYS', 'SELECTED_MARKERS']) –

  Terminate Mode, Method used to determine when to stop propagating pose to keyframes (optional)

  - `NEXT_KEY`
    To Next Keyframe – Propagate pose to first keyframe following the current frame only.
  - `LAST_KEY`
    To Last Keyframe – Propagate pose to the last keyframe only (i.e. making action cyclic).
  - `BEFORE_FRAME`
    Before Frame – Propagate pose to all keyframes between current frame and ‘Frame’ property.
  - `BEFORE_END`
    Before Last Keyframe – Propagate pose to all keyframes from current frame until no more are found.
  - `SELECTED_KEYS`
    On Selected Keyframes – Propagate pose to all selected keyframes.
  - `SELECTED_MARKERS`
    On Selected Markers – Propagate pose to all keyframes occurring on frames with Scene Markers after the current frame.
- **end_frame** (float) – End Frame, Frame to stop propagating frames to (for ‘Before Frame’ mode) (in [1.17549e-38, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.pose.push"></a>

### bpy.ops.pose.push(*, factor=0.5, prev_frame=0, next_frame=0, channels='ALL', axis_lock='FREE')

Exaggerate the current pose in regards to the breakdown pose

**Parameters:**

- **factor** (float) – Factor, Weighting factor for which keyframe is favored more (in [0, 1], optional)
- **prev_frame** (int) – Previous Keyframe, Frame number of keyframe immediately before the current frame (in [-1048574, 1048574], optional)
- **next_frame** (int) – Next Keyframe, Frame number of keyframe immediately after the current frame (in [-1048574, 1048574], optional)
- **channels** (Literal['ALL', 'LOC', 'ROT', 'SIZE', 'BBONE', 'CUSTOM']) –

  Channels, Set of properties that are affected (optional)

  - `ALL`
    All Properties – All properties, including transforms, bendy bone shape, and custom properties.
  - `LOC`
    Location – Location only.
  - `ROT`
    Rotation – Rotation only.
  - `SIZE`
    Scale – Scale only.
  - `BBONE`
    Bendy Bone – Bendy Bone shape properties.
  - `CUSTOM`
    Custom Properties – Custom properties.
- **axis_lock** (Literal['FREE', 'X', 'Y', 'Z']) –

  Axis Lock, Transform axis to restrict effects to (optional)

  - `FREE`
    Free – All axes are affected.
  - `X`
    X – Only X-axis transforms are affected.
  - `Y`
    Y – Only Y-axis transforms are affected.
  - `Z`
    Z – Only Z-axis transforms are affected.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.pose.quaternions_flip"></a>

### bpy.ops.pose.quaternions_flip()

Flip quaternion values to achieve desired rotations, while maintaining the same orientations

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.pose.relax"></a>

### bpy.ops.pose.relax(*, factor=0.5, prev_frame=0, next_frame=0, channels='ALL', axis_lock='FREE')

Make the current pose more similar to its breakdown pose

**Parameters:**

- **factor** (float) – Factor, Weighting factor for which keyframe is favored more (in [0, 1], optional)
- **prev_frame** (int) – Previous Keyframe, Frame number of keyframe immediately before the current frame (in [-1048574, 1048574], optional)
- **next_frame** (int) – Next Keyframe, Frame number of keyframe immediately after the current frame (in [-1048574, 1048574], optional)
- **channels** (Literal['ALL', 'LOC', 'ROT', 'SIZE', 'BBONE', 'CUSTOM']) –

  Channels, Set of properties that are affected (optional)

  - `ALL`
    All Properties – All properties, including transforms, bendy bone shape, and custom properties.
  - `LOC`
    Location – Location only.
  - `ROT`
    Rotation – Rotation only.
  - `SIZE`
    Scale – Scale only.
  - `BBONE`
    Bendy Bone – Bendy Bone shape properties.
  - `CUSTOM`
    Custom Properties – Custom properties.
- **axis_lock** (Literal['FREE', 'X', 'Y', 'Z']) –

  Axis Lock, Transform axis to restrict effects to (optional)

  - `FREE`
    Free – All axes are affected.
  - `X`
    X – Only X-axis transforms are affected.
  - `Y`
    Y – Only Y-axis transforms are affected.
  - `Z`
    Z – Only Z-axis transforms are affected.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.pose.reveal"></a>

### bpy.ops.pose.reveal(*, select=True)

Reveal all bones hidden in Pose Mode

**Parameters:**

**select** (bool) – Select, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.pose.rot_clear"></a>

### bpy.ops.pose.rot_clear()

Reset rotations of selected bones to their default values

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.pose.rotation_mode_set"></a>

### bpy.ops.pose.rotation_mode_set(*, type='QUATERNION')

Set the rotation representation used by selected bones

**Parameters:**

**type** (Literal[[Object Rotation Mode Items](bpy_types_enum_items/object_rotation_mode_items.md#rna-enum-object-rotation-mode-items)]) – Rotation Mode, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.pose.scale_clear"></a>

### bpy.ops.pose.scale_clear()

Reset scaling of selected bones to their default values

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.pose.select_all"></a>

### bpy.ops.pose.select_all(*, action='TOGGLE')

Toggle selection status of all bones

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

<a id="bpy.ops.pose.select_constraint_target"></a>

### bpy.ops.pose.select_constraint_target()

Select bones used as targets for the currently selected bones

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.pose.select_grouped"></a>

### bpy.ops.pose.select_grouped(*, extend=False, type='COLLECTION')

Select all visible bones grouped by similar properties

**Parameters:**

- **extend** (bool) – Extend, Extend selection instead of deselecting everything first (optional)
- **type** (Literal['COLLECTION', 'COLOR', 'KEYINGSET', 'CHILDREN', 'CHILDREN_IMMEDIATE', 'PARENT', 'SIBLINGS']) –

  Type, (optional)

  - `COLLECTION`
    Collection – Same collections as the active bone.
  - `COLOR`
    Color – Same color as the active bone.
  - `KEYINGSET`
    Keying Set – All bones affected by active Keying Set.
  - `CHILDREN`
    Children – Select all children of currently selected bones.
  - `CHILDREN_IMMEDIATE`
    Immediate Children – Select direct children of currently selected bones.
  - `PARENT`
    Parents – Select the parents of currently selected bones.
  - `SIBLINGS`
    Siblings – Select all bones that have the same parent as currently selected bones.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.pose.select_hierarchy"></a>

### bpy.ops.pose.select_hierarchy(*, direction='PARENT', extend=False)

Select immediate parent/children of selected bones

**Parameters:**

- **direction** (Literal['PARENT', 'CHILD']) – Direction, (optional)
- **extend** (bool) – Extend, Extend the selection (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.pose.select_linked"></a>

### bpy.ops.pose.select_linked()

Select all bones linked by connected parent/child relationships from the current selection

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.pose.select_linked_pick"></a>

### bpy.ops.pose.select_linked_pick(*, extend=False)

Select bones linked by connected parent/child relationships under the mouse cursor

**Parameters:**

**extend** (bool) – Extend, Extend selection instead of deselecting everything first (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.pose.select_mirror"></a>

### bpy.ops.pose.select_mirror(*, only_active=False, extend=False)

Mirror the bone selection

**Parameters:**

- **only_active** (bool) – Active Only, Only operate on the active bone (optional)
- **extend** (bool) – Extend, Extend the selection (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.pose.select_parent"></a>

### bpy.ops.pose.select_parent()

Select bones that are parents of the currently selected bones

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.pose.selection_set_add"></a>

### bpy.ops.pose.selection_set_add()

Create a new empty Selection Set

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/bone_selection_sets.py:147](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/bone_selection_sets.py#L147)

<a id="bpy.ops.pose.selection_set_add_and_assign"></a>

### bpy.ops.pose.selection_set_add_and_assign()

Create a new Selection Set with the currently selected bones

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/bone_selection_sets.py:278](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/bone_selection_sets.py#L278)

<a id="bpy.ops.pose.selection_set_assign"></a>

### bpy.ops.pose.selection_set_assign()

Add selected bones to Selection Set

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/bone_selection_sets.py:194](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/bone_selection_sets.py#L194)

<a id="bpy.ops.pose.selection_set_copy"></a>

### bpy.ops.pose.selection_set_copy()

Copy the selected Selection Set(s) to the clipboard

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/bone_selection_sets.py:290](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/bone_selection_sets.py#L290)

<a id="bpy.ops.pose.selection_set_delete_all"></a>

### bpy.ops.pose.selection_set_delete_all()

Remove all Selection Sets from this Armature

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/bone_selection_sets.py:77](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/bone_selection_sets.py#L77)

<a id="bpy.ops.pose.selection_set_deselect"></a>

### bpy.ops.pose.selection_set_deselect()

Remove Selection Set bones from current selection

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/bone_selection_sets.py:261](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/bone_selection_sets.py#L261)

<a id="bpy.ops.pose.selection_set_move"></a>

### bpy.ops.pose.selection_set_move(*, direction='UP')

Move the active Selection Set up/down the list of sets

**Parameters:**

**direction** (Literal['UP', 'DOWN']) – Move Direction, Direction to move the active Selection Set: UP (default) or DOWN (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/bone_selection_sets.py:126](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/bone_selection_sets.py#L126)

<a id="bpy.ops.pose.selection_set_paste"></a>

### bpy.ops.pose.selection_set_paste()

Add new Selection Set(s) from the clipboard

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/bone_selection_sets.py:302](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/bone_selection_sets.py#L302)

<a id="bpy.ops.pose.selection_set_remove"></a>

### bpy.ops.pose.selection_set_remove()

Remove a Selection Set from this Armature

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/bone_selection_sets.py:165](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/bone_selection_sets.py#L165)

<a id="bpy.ops.pose.selection_set_remove_bones"></a>

### bpy.ops.pose.selection_set_remove_bones()

Remove the selected bones from all Selection Sets

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/bone_selection_sets.py:89](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/bone_selection_sets.py#L89)

<a id="bpy.ops.pose.selection_set_select"></a>

### bpy.ops.pose.selection_set_select(*, selection_set_index=-1)

Select the bones from this Selection Set

**Parameters:**

**selection_set_index** (int) – Selection Set Index, Which Selection Set to select; -1 uses the active Selection Set (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/bone_selection_sets.py:239](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/bone_selection_sets.py#L239)

<a id="bpy.ops.pose.selection_set_unassign"></a>

### bpy.ops.pose.selection_set_unassign()

Remove selected bones from Selection Set

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/bone_selection_sets.py:213](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/bone_selection_sets.py#L213)

<a id="bpy.ops.pose.transforms_clear"></a>

### bpy.ops.pose.transforms_clear()

Reset location, rotation, and scaling of selected bones to their default values

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.pose.user_transforms_clear"></a>

### bpy.ops.pose.user_transforms_clear(*, only_selected=True)

Reset pose bone transforms to keyframed state

**Parameters:**

**only_selected** (bool) – Only Selected, Only visible/selected bones (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.pose.visual_transform_apply"></a>

### bpy.ops.pose.visual_transform_apply()

Apply final constrained position of pose bones to their transform

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]
