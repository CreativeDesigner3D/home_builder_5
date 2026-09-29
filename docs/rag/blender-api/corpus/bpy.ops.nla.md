<!-- source: Blender Python API reference 5.2 / bpy.ops.nla.html -->

<a id="module-bpy.ops.nla"></a>

# Nla Operators

<a id="bpy.ops.nla.action_pushdown"></a>

### bpy.ops.nla.action_pushdown(*, track_index=-1)

Push action down onto the top of the NLA stack as a new strip

**Parameters:**

**track_index** (int) – Track Index, Index of NLA action track to perform pushdown operation on (in [-1, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.nla.action_sync_length"></a>

### bpy.ops.nla.action_sync_length(*, active=True)

Synchronize the length of the referenced Action with the length used in the strip

**Parameters:**

**active** (bool) – Active Strip Only, Only sync the active length for the active strip (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.nla.action_unlink"></a>

### bpy.ops.nla.action_unlink(*, force_delete=False)

Unlink this action from the active action slot (and/or exit Tweak Mode)

**Parameters:**

**force_delete** (bool) – Force Delete, Clear Fake User and remove copy stashed in this data-block’s NLA stack (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.nla.actionclip_add"></a>

### bpy.ops.nla.actionclip_add(*, action='')

Add an Action-Clip strip (i.e. an NLA Strip referencing an Action) to the active track

**Parameters:**

**action** (str) – Action, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.nla.apply_scale"></a>

### bpy.ops.nla.apply_scale()

Apply scaling of selected strips to their referenced Actions

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.nla.bake"></a>

### bpy.ops.nla.bake(*, frame_start=1, frame_end=250, step=1, only_selected=True, visual_keying=False, clear_constraints=False, clear_parents=False, use_current_action=False, clean_curves=False, bake_types={'POSE'}, channel_types={'BBONE', 'LOCATION', 'PROPS', 'ROTATION', 'SCALE'})

Bake all selected objects location/scale/rotation animation to an action

**Parameters:**

- **frame_start** (int) – Start Frame, Start frame for baking (in [0, 300000], optional)
- **frame_end** (int) – End Frame, End frame for baking (in [1, 300000], optional)
- **step** (int) – Frame Step, Number of frames to skip forward while baking each frame (in [1, 120], optional)
- **only_selected** (bool) – Only Selected Bones, Only key selected bones (Pose baking only) (optional)
- **visual_keying** (bool) – Visual Keying, Keyframe from the final transformations (with constraints applied) (optional)
- **clear_constraints** (bool) – Clear Local Constraints, Remove all constraints from keyed object/bones. To get a correct bake with this setting Visual Keying should be enabled (optional)
- **clear_parents** (bool) – Clear Parents, Bake animation onto the object then clear parents (objects only) (optional)
- **use_current_action** (bool) – Overwrite Current Action, Bake animation into current action, instead of creating a new one (useful for baking only part of bones in an armature) (optional)
- **clean_curves** (bool) – Clean Curves, After baking curves, remove redundant keys (optional)
- **bake_types** (set[Literal['POSE', 'OBJECT']]) –

  Bake Data, Which data’s transformations to bake (optional)

  - `POSE`
    Pose – Bake bones transformations.
  - `OBJECT`
    Object – Bake object transformations.
- **channel_types** (set[Literal['LOCATION', 'ROTATION', 'SCALE', 'BBONE', 'PROPS']]) –

  Channels, Which channels to bake (optional)

  - `LOCATION`
    Location – Bake location channels.
  - `ROTATION`
    Rotation – Bake rotation channels.
  - `SCALE`
    Scale – Bake scale channels.
  - `BBONE`
    B-Bone – Bake B-Bone channels.
  - `PROPS`
    Custom Properties – Bake custom properties.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/anim.py:274](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/anim.py#L274)

<a id="bpy.ops.nla.channels_click"></a>

### bpy.ops.nla.channels_click(*, extend=False)

Handle clicks to select NLA tracks

**Parameters:**

**extend** (bool) – Extend Select, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.nla.clear_scale"></a>

### bpy.ops.nla.clear_scale()

Reset scaling of selected strips

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.nla.click_select"></a>

### bpy.ops.nla.click_select(*, wait_to_deselect_others=False, use_select_on_click=False, mouse_x=0, mouse_y=0, extend=False, deselect_all=False)

Handle clicks to select NLA Strips

**Parameters:**

- **wait_to_deselect_others** (bool) – Wait to Deselect Others, (optional)
- **use_select_on_click** (bool) – Act on Click, Instead of selecting on mouse press, wait to see if there’s drag event. Otherwise select on mouse release (optional)
- **mouse_x** (int) – Mouse X, (in [-inf, inf], optional)
- **mouse_y** (int) – Mouse Y, (in [-inf, inf], optional)
- **extend** (bool) – Extend Select, (optional)
- **deselect_all** (bool) – Deselect On Nothing, Deselect all when nothing under the cursor (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.nla.delete"></a>

### bpy.ops.nla.delete()

Delete selected strips

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.nla.duplicate"></a>

### bpy.ops.nla.duplicate(*, linked=False)

Duplicate selected NLA-Strips, adding the new strips to new track(s)

**Parameters:**

**linked** (bool) – Linked, When duplicating strips, assign new copies of the actions they use (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.nla.duplicate_linked_move"></a>

### bpy.ops.nla.duplicate_linked_move(*, NLA_OT_duplicate={}, TRANSFORM_OT_translate={})

Duplicate Linked selected NLA-Strips, adding the new strips to new track(s)

**Parameters:**

- **NLA_OT_duplicate** (dict[str, Any]) – Duplicate Strips, Duplicate selected NLA-Strips, adding the new strips to new track(s) (optional, [`bpy.ops.nla.duplicate()`](#bpy.ops.nla.duplicate "bpy.ops.nla.duplicate") keyword arguments)
- **TRANSFORM_OT_translate** (dict[str, Any]) – Move, Move selected items (optional, [`bpy.ops.transform.translate()`](bpy.ops.transform.md#bpy.ops.transform.translate "bpy.ops.transform.translate") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.nla.duplicate_move"></a>

### bpy.ops.nla.duplicate_move(*, NLA_OT_duplicate={}, TRANSFORM_OT_translate={})

Duplicate selected NLA-Strips, adding the new strips to new track(s)

**Parameters:**

- **NLA_OT_duplicate** (dict[str, Any]) – Duplicate Strips, Duplicate selected NLA-Strips, adding the new strips to new track(s) (optional, [`bpy.ops.nla.duplicate()`](#bpy.ops.nla.duplicate "bpy.ops.nla.duplicate") keyword arguments)
- **TRANSFORM_OT_translate** (dict[str, Any]) – Move, Move selected items (optional, [`bpy.ops.transform.translate()`](bpy.ops.transform.md#bpy.ops.transform.translate "bpy.ops.transform.translate") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.nla.fmodifier_add"></a>

### bpy.ops.nla.fmodifier_add(*, type='NULL', only_active=True)

Add F-Modifier to the active/selected NLA-Strips

**Parameters:**

- **type** (Literal[[Fmodifier Type Items](bpy_types_enum_items/fmodifier_type_items.md#rna-enum-fmodifier-type-items)]) – Type, (optional)
- **only_active** (bool) – Only Active, Only add a F-Modifier of the specified type to the active strip (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.nla.fmodifier_copy"></a>

### bpy.ops.nla.fmodifier_copy()

Copy the F-Modifier(s) of the active NLA-Strip

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.nla.fmodifier_paste"></a>

### bpy.ops.nla.fmodifier_paste(*, only_active=True, replace=False)

Add copied F-Modifiers to the selected NLA-Strips

**Parameters:**

- **only_active** (bool) – Only Active, Only paste F-Modifiers on active strip (optional)
- **replace** (bool) – Replace Existing, Replace existing F-Modifiers, instead of just appending to the end of the existing list (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.nla.make_single_user"></a>

### bpy.ops.nla.make_single_user(*, confirm=True)

Make linked action local to each strip

**Parameters:**

**confirm** (bool) – Confirm, Prompt for confirmation (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.nla.meta_add"></a>

### bpy.ops.nla.meta_add()

Add new meta-strips incorporating the selected strips

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.nla.meta_remove"></a>

### bpy.ops.nla.meta_remove()

Separate out the strips held by the selected meta-strips

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.nla.move_down"></a>

### bpy.ops.nla.move_down()

Move selected strips down a track if there’s room

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.nla.move_up"></a>

### bpy.ops.nla.move_up()

Move selected strips up a track if there’s room

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.nla.mute_toggle"></a>

### bpy.ops.nla.mute_toggle()

Mute or un-mute selected strips

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.nla.previewrange_set"></a>

### bpy.ops.nla.previewrange_set()

Set Preview Range based on extents of selected strips

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.nla.select_all"></a>

### bpy.ops.nla.select_all(*, action='TOGGLE')

Select or deselect all NLA-Strips

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

<a id="bpy.ops.nla.select_box"></a>

### bpy.ops.nla.select_box(*, axis_range=False, tweak=False, xmin=0, xmax=0, ymin=0, ymax=0, wait_for_input=True, mode='SET')

Use box selection to grab NLA-Strips

**Parameters:**

- **axis_range** (bool) – Axis Range, (optional)
- **tweak** (bool) – Tweak, Operator has been activated using a click-drag event (optional)
- **xmin** (int) – X Min, (in [-inf, inf], optional)
- **xmax** (int) – X Max, (in [-inf, inf], optional)
- **ymin** (int) – Y Min, (in [-inf, inf], optional)
- **ymax** (int) – Y Max, (in [-inf, inf], optional)
- **wait_for_input** (bool) – Wait for Input, (optional)
- **mode** (Literal['SET', 'ADD', 'SUB']) –

  Mode, (optional)

  - `SET`
    Set – Set a new selection.
  - `ADD`
    Extend – Extend existing selection.
  - `SUB`
    Subtract – Subtract existing selection.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.nla.select_leftright"></a>

### bpy.ops.nla.select_leftright(*, mode='CHECK', extend=False)

Select strips to the left or the right of the current frame

**Parameters:**

- **mode** (Literal['CHECK', 'LEFT', 'RIGHT']) – Mode, (optional)
- **extend** (bool) – Extend Select, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.nla.selected_objects_add"></a>

### bpy.ops.nla.selected_objects_add()

Make selected objects appear in NLA Editor by adding Animation Data

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.nla.snap"></a>

### bpy.ops.nla.snap(*, type='CFRA')

Move start of strips to specified time

**Parameters:**

**type** (Literal['CFRA', 'NEAREST_FRAME', 'NEAREST_SECOND', 'NEAREST_MARKER']) – Type, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.nla.soundclip_add"></a>

### bpy.ops.nla.soundclip_add()

Add a strip for controlling when speaker plays its sound clip

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.nla.split"></a>

### bpy.ops.nla.split()

Split selected strips at their midpoints

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.nla.swap"></a>

### bpy.ops.nla.swap()

Swap order of selected strips within tracks

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.nla.tracks_add"></a>

### bpy.ops.nla.tracks_add(*, above_selected=False)

Add NLA-Tracks above/after the selected tracks

**Parameters:**

**above_selected** (bool) – Above Selected, Add a new NLA Track above every existing selected one (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.nla.tracks_delete"></a>

### bpy.ops.nla.tracks_delete()

Delete selected NLA-Tracks and the strips they contain

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.nla.transition_add"></a>

### bpy.ops.nla.transition_add()

Add a transition strip between two adjacent selected strips

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.nla.tweakmode_enter"></a>

### bpy.ops.nla.tweakmode_enter(*, isolate_action=False, use_upper_stack_evaluation=False)

Enter tweaking mode for the action referenced by the active strip to edit its keyframes

**Parameters:**

- **isolate_action** (bool) – Isolate Action, Enable ‘solo’ on the NLA Track containing the active strip, to edit it without seeing the effects of the NLA stack (optional)
- **use_upper_stack_evaluation** (bool) – Evaluate Upper Stack, In tweak mode, display the effects of the tracks above the tweak strip (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.nla.tweakmode_exit"></a>

### bpy.ops.nla.tweakmode_exit(*, isolate_action=False)

Exit tweaking mode for the action referenced by the active strip

**Parameters:**

**isolate_action** (bool) – Isolate Action, Disable ‘solo’ on any of the NLA Tracks after exiting tweak mode to get things back to normal (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.nla.view_all"></a>

### bpy.ops.nla.view_all()

Reset viewable area to show full strips range

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.nla.view_frame"></a>

### bpy.ops.nla.view_frame()

Move the view to the current frame

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.nla.view_selected"></a>

### bpy.ops.nla.view_selected()

Reset viewable area to show selected strips range

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]
