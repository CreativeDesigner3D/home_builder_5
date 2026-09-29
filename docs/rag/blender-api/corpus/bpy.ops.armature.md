<!-- source: Blender Python API reference 5.2 / bpy.ops.armature.html -->

<a id="module-bpy.ops.armature"></a>

# Armature Operators

<a id="bpy.ops.armature.align"></a>

### bpy.ops.armature.align()

Align selected bones to the active bone (or to their parent)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.armature.assign_to_collection"></a>

### bpy.ops.armature.assign_to_collection(*, collection_index=-1, new_collection_name='')

Assign all selected bones to a collection, or unassign them, depending on whether the active bone is already assigned or not

**Parameters:**

- **collection_index** (int) – Collection Index, Index of the collection to assign selected bones to. When the operator should create a new bone collection, use new_collection_name to define the collection name, and set this parameter to the parent index of the new bone collection (in [-1, inf], optional)
- **new_collection_name** (str) – Name, Name of a to-be-added bone collection. Only pass this if you want to create a new bone collection and assign the selected bones to it. To assign to an existing collection, do not include this parameter and use collection_index (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.armature.autoside_names"></a>

### bpy.ops.armature.autoside_names(*, type='XAXIS')

Automatically renames the selected bones according to which side of the target axis they fall on

**Parameters:**

**type** (Literal['XAXIS', 'YAXIS', 'ZAXIS']) –

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

<a id="bpy.ops.armature.bone_primitive_add"></a>

### bpy.ops.armature.bone_primitive_add(*, name='Bone', space='OBJECT', align='UP', length=1.0, use_deform=True)

Add a new bone located at the 3D cursor

**Parameters:**

- **name** (str) – Name, Name of the newly created bone (optional, never None)
- **space** (Literal['OBJECT', 'WORLD']) –

  Space, Co-ordinate system the new bone will be created in (optional)

  - `OBJECT`
    Object – The newly created bone will use Object Space co-ordinate system.
  - `WORLD`
    World – The newly created bone will use World Space co-ordinate system.
- **align** (Literal['UP', 'AXES', '3D_CURSOR', '3D_VIEW']) –

  Align, Initial orientation of the new bone (optional)

  - `UP`
    Up – Make the bone visually point upwards so the long axis is aligned with the World/Object positive Z axis (depending on the choice above).
  - `AXES`
    Axes – Align the new bone to match the axes of the World/Object (depending on the choice above).
  - `3D_CURSOR`
    3D Cursor – Align new bone to match the axes of the 3D cursor.
  - `3D_VIEW`
    Viewport – Align new bone to match the axes of the 3D viewport.
- **length** (float) – Length, Length of the new bone (in [0.001, inf], optional)
- **use_deform** (bool) – Deform, Enable bone to deform geometry (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.armature.calculate_roll"></a>

### bpy.ops.armature.calculate_roll(*, type='POS_X', axis_flip=False, axis_only=False)

Automatically fix alignment of select bones’ axes

**Parameters:**

- **type** (Literal['POS_X', 'POS_Z', 'GLOBAL_POS_X', 'GLOBAL_POS_Y', 'GLOBAL_POS_Z', 'NEG_X', 'NEG_Z', 'GLOBAL_NEG_X', 'GLOBAL_NEG_Y', 'GLOBAL_NEG_Z', 'ACTIVE', 'VIEW', 'CURSOR']) – Type, (optional)
- **axis_flip** (bool) – Flip Axis, Negate the alignment axis (optional)
- **axis_only** (bool) – Shortest Rotation, Ignore the axis direction, use the shortest rotation to align (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.armature.click_extrude"></a>

### bpy.ops.armature.click_extrude()

Create a new bone going from the last selected joint to the mouse position

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.armature.collection_add"></a>

### bpy.ops.armature.collection_add()

Add a new bone collection

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.armature.collection_assign"></a>

### bpy.ops.armature.collection_assign(*, name='')

Add selected bones to the chosen bone collection

**Parameters:**

**name** (str) – Bone Collection, Name of the bone collection to assign this bone to; empty to assign to the active bone collection (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.armature.collection_create_and_assign"></a>

### bpy.ops.armature.collection_create_and_assign(*, name='')

Create a new bone collection and assign all selected bones

**Parameters:**

**name** (str) – Bone Collection, Name of the bone collection to create (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.armature.collection_deselect"></a>

### bpy.ops.armature.collection_deselect()

Deselect bones of active Bone Collection

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.armature.collection_move"></a>

### bpy.ops.armature.collection_move(*, direction='UP')

Change position of active Bone Collection in list of Bone collections

**Parameters:**

**direction** (Literal['UP', 'DOWN']) – Direction, Direction to move the active Bone Collection towards (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.armature.collection_remove"></a>

### bpy.ops.armature.collection_remove()

Remove the active bone collection

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.armature.collection_remove_unused"></a>

### bpy.ops.armature.collection_remove_unused()

Remove all bone collections that have neither bones nor children. This is done recursively, so bone collections that only have unused children are also removed

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/anim.py:619](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/anim.py#L619)

<a id="bpy.ops.armature.collection_select"></a>

### bpy.ops.armature.collection_select()

Select bones in active Bone Collection

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.armature.collection_show_all"></a>

### bpy.ops.armature.collection_show_all()

Show all bone collections

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/anim.py:574](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/anim.py#L574)

<a id="bpy.ops.armature.collection_unassign"></a>

### bpy.ops.armature.collection_unassign(*, name='')

Remove selected bones from the active bone collection

**Parameters:**

**name** (str) – Bone Collection, Name of the bone collection to unassign this bone from; empty to unassign from the active bone collection (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.armature.collection_unassign_named"></a>

### bpy.ops.armature.collection_unassign_named(*, name='', bone_name='')

Unassign the named bone from this bone collection

**Parameters:**

- **name** (str) – Bone Collection, Name of the bone collection to unassign this bone from; empty to unassign from the active bone collection (optional, never None)
- **bone_name** (str) – Bone Name, Name of the bone to unassign from the collection; empty to use the active bone (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.armature.collection_unsolo_all"></a>

### bpy.ops.armature.collection_unsolo_all()

Clear the ‘solo’ setting on all bone collections

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/anim.py:597](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/anim.py#L597)

<a id="bpy.ops.armature.copy_bone_color_to_selected"></a>

### bpy.ops.armature.copy_bone_color_to_selected(*, bone_type='EDIT')

Copy the bone color of the active bone to all selected bones

**Parameters:**

**bone_type** (Literal['EDIT', 'POSE']) –

Type, (optional)

- `EDIT`
  Bone – Copy Bone colors from the active bone to all selected bones.
- `POSE`
  Pose Bone – Copy Pose Bone colors from the active pose bone to all selected pose bones.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/anim.py:493](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/anim.py#L493)

<a id="bpy.ops.armature.delete"></a>

### bpy.ops.armature.delete(*, confirm=True)

Remove selected bones from the armature

**Parameters:**

**confirm** (bool) – Confirm, Prompt for confirmation (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.armature.dissolve"></a>

### bpy.ops.armature.dissolve()

Dissolve selected bones from the armature

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.armature.duplicate"></a>

### bpy.ops.armature.duplicate(*, do_flip_names=False)

Make copies of the selected bones within the same armature

**Parameters:**

**do_flip_names** (bool) – Flip Names, Try to flip names of the bones, if possible, instead of adding a number extension (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.armature.duplicate_move"></a>

### bpy.ops.armature.duplicate_move(*, ARMATURE_OT_duplicate={}, TRANSFORM_OT_translate={})

Make copies of the selected bones within the same armature and move them

**Parameters:**

- **ARMATURE_OT_duplicate** (dict[str, Any]) – Duplicate Selected Bone(s), Make copies of the selected bones within the same armature (optional, [`bpy.ops.armature.duplicate()`](#bpy.ops.armature.duplicate "bpy.ops.armature.duplicate") keyword arguments)
- **TRANSFORM_OT_translate** (dict[str, Any]) – Move, Move selected items (optional, [`bpy.ops.transform.translate()`](bpy.ops.transform.md#bpy.ops.transform.translate "bpy.ops.transform.translate") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.armature.duplicate_rename"></a>

### bpy.ops.armature.duplicate_rename(*, do_flip_names=False, search='', replace='')

Make copies of the selected bones within the same armature and replace a part of their name

**Parameters:**

- **do_flip_names** (bool) – Flip Names, Try to flip names of the bones, if possible, instead of adding a number extension (optional)
- **search** (str) – Search, A part of the current bone name that will be replaced (optional, never None)
- **replace** (str) – Replace, The substitute to be inserted into the place of the given search term. If left empty the search term will be removed (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.armature.extrude"></a>

### bpy.ops.armature.extrude(*, forked=False)

Create new bones from the selected joints

**Parameters:**

**forked** (bool) – Forked, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.armature.extrude_forked"></a>

### bpy.ops.armature.extrude_forked(*, ARMATURE_OT_extrude={}, TRANSFORM_OT_translate={})

Create new bones from the selected joints and move them

**Parameters:**

- **ARMATURE_OT_extrude** (dict[str, Any]) – Extrude, Create new bones from the selected joints (optional, [`bpy.ops.armature.extrude()`](#bpy.ops.armature.extrude "bpy.ops.armature.extrude") keyword arguments)
- **TRANSFORM_OT_translate** (dict[str, Any]) – Move, Move selected items (optional, [`bpy.ops.transform.translate()`](bpy.ops.transform.md#bpy.ops.transform.translate "bpy.ops.transform.translate") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.armature.extrude_move"></a>

### bpy.ops.armature.extrude_move(*, ARMATURE_OT_extrude={}, TRANSFORM_OT_translate={})

Create new bones from the selected joints and move them

**Parameters:**

- **ARMATURE_OT_extrude** (dict[str, Any]) – Extrude, Create new bones from the selected joints (optional, [`bpy.ops.armature.extrude()`](#bpy.ops.armature.extrude "bpy.ops.armature.extrude") keyword arguments)
- **TRANSFORM_OT_translate** (dict[str, Any]) – Move, Move selected items (optional, [`bpy.ops.transform.translate()`](bpy.ops.transform.md#bpy.ops.transform.translate "bpy.ops.transform.translate") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.armature.fill"></a>

### bpy.ops.armature.fill()

Add bone between selected joint(s) and/or 3D cursor

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.armature.flip_names"></a>

### bpy.ops.armature.flip_names(*, do_strip_numbers=False)

Flips (and corrects) the axis suffixes of the names of selected bones

**Parameters:**

**do_strip_numbers** (bool) – Strip Numbers, Try to remove right-most dot-number from flipped names.Warning: May result in incoherent naming in some cases(optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.armature.hide"></a>

### bpy.ops.armature.hide(*, unselected=False)

Tag selected bones to not be visible in Edit Mode

**Parameters:**

**unselected** (bool) – Unselected, Hide unselected rather than selected (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.armature.move_to_collection"></a>

### bpy.ops.armature.move_to_collection(*, collection_index=-1, new_collection_name='')

Move bones to a collection

**Parameters:**

- **collection_index** (int) – Collection Index, Index of the collection to move selected bones to. When the operator should create a new bone collection, do not include this parameter and pass new_collection_name (in [-1, inf], optional)
- **new_collection_name** (str) – Name, Name of a to-be-added bone collection. Only pass this if you want to create a new bone collection and move the selected bones to it. To move to an existing collection, do not include this parameter and use collection_index (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.armature.parent_clear"></a>

### bpy.ops.armature.parent_clear(*, type='CLEAR')

Remove the parent-child relationship between selected bones and their parents

**Parameters:**

**type** (Literal['CLEAR', 'DISCONNECT']) – Clear Type, What way to clear parenting (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.armature.parent_set"></a>

### bpy.ops.armature.parent_set(*, type='CONNECTED')

Set the active bone as the parent of the selected bones

**Parameters:**

**type** (Literal['CONNECTED', 'OFFSET']) – Parent Type, Type of parenting (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.armature.reveal"></a>

### bpy.ops.armature.reveal(*, select=True)

Reveal all bones hidden in Edit Mode

**Parameters:**

**select** (bool) – Select, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.armature.roll_clear"></a>

### bpy.ops.armature.roll_clear(*, roll=0.0)

Clear roll for selected bones

**Parameters:**

**roll** (float) – Roll, (in [-6.28319, 6.28319], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.armature.select_all"></a>

### bpy.ops.armature.select_all(*, action='TOGGLE')

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

<a id="bpy.ops.armature.select_hierarchy"></a>

### bpy.ops.armature.select_hierarchy(*, direction='PARENT', extend=False)

Select immediate parent/children of selected bones

**Parameters:**

- **direction** (Literal['PARENT', 'CHILD']) – Direction, (optional)
- **extend** (bool) – Extend, Extend the selection (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.armature.select_less"></a>

### bpy.ops.armature.select_less()

Deselect those bones at the boundary of each selection region

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.armature.select_linked"></a>

### bpy.ops.armature.select_linked(*, all_forks=False)

Select all bones linked by parent/child connections to the current selection

**Parameters:**

**all_forks** (bool) – All Forks, Follow forks in the parents chain (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.armature.select_linked_pick"></a>

### bpy.ops.armature.select_linked_pick(*, deselect=False, all_forks=False)

(De)select bones linked by parent/child connections under the mouse cursor

**Parameters:**

- **deselect** (bool) – Deselect, (optional)
- **all_forks** (bool) – All Forks, Follow forks in the parents chain (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.armature.select_mirror"></a>

### bpy.ops.armature.select_mirror(*, only_active=False, extend=False)

Mirror the bone selection

**Parameters:**

- **only_active** (bool) – Active Only, Only operate on the active bone (optional)
- **extend** (bool) – Extend, Extend the selection (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.armature.select_more"></a>

### bpy.ops.armature.select_more()

Select those bones connected to the initial selection

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.armature.select_similar"></a>

### bpy.ops.armature.select_similar(*, type='LENGTH', threshold=0.1)

Select similar bones by property types

**Parameters:**

- **type** (Literal['CHILDREN', 'CHILDREN_IMMEDIATE', 'SIBLINGS', 'LENGTH', 'DIRECTION', 'PREFIX', 'SUFFIX', 'BONE_COLLECTION', 'COLOR', 'SHAPE']) – Type, (optional)
- **threshold** (float) – Threshold, (in [0, 1], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.armature.separate"></a>

### bpy.ops.armature.separate()

Isolate selected bones into a separate armature

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.armature.shortest_path_pick"></a>

### bpy.ops.armature.shortest_path_pick()

Select shortest path between two bones

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.armature.split"></a>

### bpy.ops.armature.split()

Split off selected bones from connected unselected bones

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.armature.subdivide"></a>

### bpy.ops.armature.subdivide(*, number_cuts=1)

Break selected bones into chains of smaller bones

**Parameters:**

**number_cuts** (int) – Number of Cuts, (in [1, 1000], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.armature.switch_direction"></a>

### bpy.ops.armature.switch_direction()

Change the direction that a chain of bones points in (head and tail swap)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.armature.symmetrize"></a>

### bpy.ops.armature.symmetrize(*, direction='NEGATIVE_X', copy_bone_colors=False)

Enforce symmetry, make copies of the selection or use existing

**Parameters:**

- **direction** (Literal['NEGATIVE_X', 'POSITIVE_X']) – Direction, Which sides to copy from and to (when both are selected) (optional)
- **copy_bone_colors** (bool) – Bone Colors, Copy colors to existing bones (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]
