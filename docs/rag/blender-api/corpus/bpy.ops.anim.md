<!-- source: Blender Python API reference 5.2 / bpy.ops.anim.html -->

<a id="module-bpy.ops.anim"></a>

# Anim Operators

<a id="bpy.ops.anim.change_frame"></a>

### bpy.ops.anim.change_frame(*, frame=0.0, snap=False, seq_solo_preview=False, pass_through_on_strip_handles=False)

Interactively change the current frame number

**Parameters:**

- **frame** (float) – Frame, (in [-1.04857e+06, 1.04857e+06], optional)
- **snap** (bool) – Snap, (optional)
- **seq_solo_preview** (bool) – Strip Preview, (optional)
- **pass_through_on_strip_handles** (bool) – Pass Through on Strip Handles, Allow another operator to operate on strip handles (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.channel_select_keys"></a>

### bpy.ops.anim.channel_select_keys(*, extend=False)

Select all keyframes of channel under mouse

**Parameters:**

**extend** (bool) – Extend, Extend selection (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.channel_view_pick"></a>

### bpy.ops.anim.channel_view_pick(*, include_handles=True, use_preview_range=True)

Reset viewable area to show the channel under the cursor

**Parameters:**

- **include_handles** (bool) – Include Handles, Include handles of keyframes when calculating extents (optional)
- **use_preview_range** (bool) – Use Preview Range, Ignore frames outside of the preview range (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.channels_bake"></a>

### bpy.ops.anim.channels_bake(*, use_scene_range=True, range=(0, 0), step=1.0, remove_outside_range=False, interpolation_type='BEZIER', bake_modifiers=True)

Create keyframes following the current shape of F-Curves of selected channels

**Parameters:**

- **use_scene_range** (bool) – Use Scene Range, If enabled, the scene start and end frame will be used to determine the bake range (optional)
- **range** (Sequence[int]) – Frame Range, The custom range in which to create new keys. Only used when not using the scene range (array of 2 items, in [-inf, inf], optional)
- **step** (float) – Frame Step, At which interval to add keys (in [0.01, inf], optional)
- **remove_outside_range** (bool) – Remove Outside Range, Removes keys outside the given range, leaving only the newly baked (optional)
- **interpolation_type** (Literal['BEZIER', 'LIN', 'CONST']) –

  Interpolation Type, Choose the interpolation type with which new keys will be added (optional)

  - `BEZIER`
    Bézier – New keys will be Bézier.
  - `LIN`
    Linear – New keys will be linear.
  - `CONST`
    Constant – New keys will be constant.
- **bake_modifiers** (bool) – Bake Modifiers, Bake Modifiers into keyframes and delete them after (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.channels_clean_empty"></a>

### bpy.ops.anim.channels_clean_empty()

Delete all empty animation data containers from visible data-blocks

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.channels_click"></a>

### bpy.ops.anim.channels_click(*, extend=False, extend_range=False, children_only=False)

Handle mouse clicks over animation channels

**Parameters:**

- **extend** (bool) – Extend Select, (optional)
- **extend_range** (bool) – Extend Range, Selection of active channel to clicked channel (optional)
- **children_only** (bool) – Select Children Only, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.channels_collapse"></a>

### bpy.ops.anim.channels_collapse(*, all=True)

Collapse (close) all selected expandable animation channels

**Parameters:**

**all** (bool) – All, Collapse all channels (not just selected ones) (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.channels_delete"></a>

### bpy.ops.anim.channels_delete()

Delete all selected animation channels

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.channels_editable_toggle"></a>

### bpy.ops.anim.channels_editable_toggle(*, mode='TOGGLE', type='PROTECT')

Toggle editability of selected channels

**Parameters:**

- **mode** (Literal['TOGGLE', 'DISABLE', 'ENABLE', 'INVERT']) – Mode, (optional)
- **type** (Literal['PROTECT', 'MUTE']) – Type, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.channels_expand"></a>

### bpy.ops.anim.channels_expand(*, all=True)

Expand (open) all selected expandable animation channels

**Parameters:**

**all** (bool) – All, Expand all channels (not just selected ones) (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.channels_fcurves_enable"></a>

### bpy.ops.anim.channels_fcurves_enable()

Clear ‘disabled’ tag from all F-Curves to get broken F-Curves working again

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.channels_group"></a>

### bpy.ops.anim.channels_group(*, name='')

Add selected F-Curves to a new group

**Parameters:**

**name** (str) – Name, Name of newly created group (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.channels_move"></a>

### bpy.ops.anim.channels_move(*, direction='DOWN')

Rearrange selected animation channels

**Parameters:**

**direction** (Literal['TOP', 'UP', 'DOWN', 'BOTTOM']) – Direction, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.channels_rename"></a>

### bpy.ops.anim.channels_rename()

Rename animation channel under mouse

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.channels_select_all"></a>

### bpy.ops.anim.channels_select_all(*, action='TOGGLE')

Toggle selection of all animation channels

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

<a id="bpy.ops.anim.channels_select_box"></a>

### bpy.ops.anim.channels_select_box(*, xmin=0, xmax=0, ymin=0, ymax=0, wait_for_input=True, deselect=False, extend=True)

Select all animation channels within the specified region

**Parameters:**

- **xmin** (int) – X Min, (in [-inf, inf], optional)
- **xmax** (int) – X Max, (in [-inf, inf], optional)
- **ymin** (int) – Y Min, (in [-inf, inf], optional)
- **ymax** (int) – Y Max, (in [-inf, inf], optional)
- **wait_for_input** (bool) – Wait for Input, (optional)
- **deselect** (bool) – Deselect, Deselect rather than select items (optional)
- **extend** (bool) – Extend, Extend selection instead of deselecting everything first (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.channels_select_filter"></a>

### bpy.ops.anim.channels_select_filter()

Start entering text which filters the set of channels shown to only include those with matching names

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.channels_setting_disable"></a>

### bpy.ops.anim.channels_setting_disable(*, mode='DISABLE', type='PROTECT')

Disable specified setting on all selected animation channels

**Parameters:**

- **mode** (Literal['TOGGLE', 'DISABLE', 'ENABLE', 'INVERT']) – Mode, (optional)
- **type** (Literal['PROTECT', 'MUTE']) – Type, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.channels_setting_enable"></a>

### bpy.ops.anim.channels_setting_enable(*, mode='ENABLE', type='PROTECT')

Enable specified setting on all selected animation channels

**Parameters:**

- **mode** (Literal['TOGGLE', 'DISABLE', 'ENABLE', 'INVERT']) – Mode, (optional)
- **type** (Literal['PROTECT', 'MUTE']) – Type, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.channels_setting_toggle"></a>

### bpy.ops.anim.channels_setting_toggle(*, mode='TOGGLE', type='PROTECT')

Toggle specified setting on all selected animation channels

**Parameters:**

- **mode** (Literal['TOGGLE', 'DISABLE', 'ENABLE', 'INVERT']) – Mode, (optional)
- **type** (Literal['PROTECT', 'MUTE']) – Type, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.channels_ungroup"></a>

### bpy.ops.anim.channels_ungroup()

Remove selected F-Curves from their current groups

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.channels_view_selected"></a>

### bpy.ops.anim.channels_view_selected(*, include_handles=True, use_preview_range=True)

Reset viewable area to show the selected channels

**Parameters:**

- **include_handles** (bool) – Include Handles, Include handles of keyframes when calculating extents (optional)
- **use_preview_range** (bool) – Use Preview Range, Ignore frames outside of the preview range (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.clear_useless_actions"></a>

### bpy.ops.anim.clear_useless_actions(*, only_unused=True)

Mark actions with no F-Curves for deletion after save and reload of file preserving “action libraries”

**Parameters:**

**only_unused** (bool) – Only Unused, Only unused (Fake User only) actions get considered (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/anim.py:365](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/anim.py#L365)

<a id="bpy.ops.anim.copy_driver_button"></a>

### bpy.ops.anim.copy_driver_button()

Copy the driver for the highlighted button

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.driver_button_add"></a>

### bpy.ops.anim.driver_button_add()

Add driver for the property under the cursor

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.driver_button_edit"></a>

### bpy.ops.anim.driver_button_edit()

Edit the drivers for the connected property represented by the highlighted button

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.driver_button_remove"></a>

### bpy.ops.anim.driver_button_remove(*, all=True)

Remove the driver(s) for the connected property(s) represented by the highlighted button

**Parameters:**

**all** (bool) – All, Delete drivers for all elements of the array (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.end_frame_set"></a>

### bpy.ops.anim.end_frame_set()

Set the current frame as the preview or scene end frame

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.keyframe_clear_button"></a>

### bpy.ops.anim.keyframe_clear_button(*, all=True)

Clear all keyframes on the currently active property

**Parameters:**

**all** (bool) – All, Clear keyframes from all elements of the array (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.keyframe_clear_v3d"></a>

### bpy.ops.anim.keyframe_clear_v3d(*, confirm=True)

Remove all keyframe animation for selected objects

**Parameters:**

**confirm** (bool) – Confirm, Prompt for confirmation (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.keyframe_clear_vse"></a>

### bpy.ops.anim.keyframe_clear_vse(*, confirm=True)

Remove all keyframe animation for selected strips

**Parameters:**

**confirm** (bool) – Confirm, Prompt for confirmation (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.keyframe_delete"></a>

### bpy.ops.anim.keyframe_delete(*, type='DEFAULT')

Delete keyframes on the current frame for all properties in the specified Keying Set

**Parameters:**

**type** (Literal['DEFAULT']) – Keying Set, The Keying Set to use (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.keyframe_delete_button"></a>

### bpy.ops.anim.keyframe_delete_button(*, all=True)

Delete current keyframe of current UI-active property

**Parameters:**

**all** (bool) – All, Delete keyframes from all elements of the array (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.keyframe_delete_by_name"></a>

### bpy.ops.anim.keyframe_delete_by_name(*, type='')

Alternate access to ‘Delete Keyframe’ for keymaps to use

**Parameters:**

**type** (str) – Keying Set, The Keying Set to use (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.keyframe_delete_v3d"></a>

### bpy.ops.anim.keyframe_delete_v3d(*, confirm=True)

Remove keyframes on current frame for selected objects and bones

**Parameters:**

**confirm** (bool) – Confirm, Prompt for confirmation (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.keyframe_delete_vse"></a>

### bpy.ops.anim.keyframe_delete_vse(*, confirm=True)

Remove keyframes on current frame for selected strips

**Parameters:**

**confirm** (bool) – Confirm, Prompt for confirmation (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.keyframe_insert"></a>

### bpy.ops.anim.keyframe_insert(*, type='DEFAULT')

Insert keyframes on the current frame using either the active keying set, or the user preferences if no keying set is active

**Parameters:**

**type** (Literal['DEFAULT']) – Keying Set, The Keying Set to use (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.keyframe_insert_button"></a>

### bpy.ops.anim.keyframe_insert_button(*, all=True)

Insert a keyframe for current UI-active property

**Parameters:**

**all** (bool) – All, Insert a keyframe for all element of the array (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.keyframe_insert_by_name"></a>

### bpy.ops.anim.keyframe_insert_by_name(*, type='')

Alternate access to ‘Insert Keyframe’ for keymaps to use

**Parameters:**

**type** (str) – Keying Set, The Keying Set to use (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.keyframe_insert_menu"></a>

### bpy.ops.anim.keyframe_insert_menu(*, type='DEFAULT', always_prompt=False)

Insert Keyframes for specified Keying Set, with menu of available Keying Sets if undefined

**Parameters:**

- **type** (Literal['DEFAULT']) – Keying Set, The Keying Set to use (optional)
- **always_prompt** (bool) – Always Show Menu, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.keying_set_active_set"></a>

### bpy.ops.anim.keying_set_active_set(*, type='DEFAULT')

Set a new active keying set

**Parameters:**

**type** (Literal['DEFAULT']) – Keying Set, The Keying Set to use (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.keying_set_add"></a>

### bpy.ops.anim.keying_set_add()

Add a new (empty) keying set to the active Scene

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.keying_set_export"></a>

### bpy.ops.anim.keying_set_export(*, filepath='', filter_folder=True, filter_text=True, filter_python=True)

Export Keying Set to a Python script

**Parameters:**

- **filepath** (str) – filepath, (optional, never None)
- **filter_folder** (bool) – Filter folders, (optional)
- **filter_text** (bool) – Filter text, (optional)
- **filter_python** (bool) – Filter Python, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/anim.py:46](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/anim.py#L46)

<a id="bpy.ops.anim.keying_set_path_add"></a>

### bpy.ops.anim.keying_set_path_add()

Add empty path to active keying set

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.keying_set_path_remove"></a>

### bpy.ops.anim.keying_set_path_remove()

Remove active Path from active keying set

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.keying_set_remove"></a>

### bpy.ops.anim.keying_set_remove()

Remove the active keying set

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.keyingset_button_add"></a>

### bpy.ops.anim.keyingset_button_add(*, all=True)

Add current UI-active property to current keying set

**Parameters:**

**all** (bool) – All, Add all elements of the array to a Keying Set (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.keyingset_button_remove"></a>

### bpy.ops.anim.keyingset_button_remove()

Remove current UI-active property from current keying set

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.merge_animation"></a>

### bpy.ops.anim.merge_animation()

Merge the animation of the selected objects into the action of the active object. Actions are not deleted by this, but might end up with zero users

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.paste_driver_button"></a>

### bpy.ops.anim.paste_driver_button()

Paste the driver in the internal clipboard to the highlighted button

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.previewrange_clear"></a>

### bpy.ops.anim.previewrange_clear()

Clear preview range

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.previewrange_set"></a>

### bpy.ops.anim.previewrange_set(*, xmin=0, xmax=0, ymin=0, ymax=0, wait_for_input=True)

Interactively define frame range used for playback

**Parameters:**

- **xmin** (int) – X Min, (in [-inf, inf], optional)
- **xmax** (int) – X Max, (in [-inf, inf], optional)
- **ymin** (int) – Y Min, (in [-inf, inf], optional)
- **ymax** (int) – Y Max, (in [-inf, inf], optional)
- **wait_for_input** (bool) – Wait for Input, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.replace_action"></a>

### bpy.ops.anim.replace_action(*, old_session_uid=0, new_session_uid=0)

Swap all users of one action to another one. The normal action slot assignment rules apply. This ignores the NLA and Action Constraints

**Parameters:**

- **old_session_uid** (int) – Old Action, Old Action’s session uid to replace (in [-inf, inf], optional)
- **new_session_uid** (int) – Replacement Action, The replacement Action’s session uid to remap all selected Action’s users to (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.replace_action_new"></a>

### bpy.ops.anim.replace_action_new(*, old_session_uid=0)

Swap all users of one action to a new action. This ignores the NLA and Action Constraints

**Parameters:**

**old_session_uid** (int) – Old Action, Old Action’s session uid to replace (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.scene_range_frame"></a>

### bpy.ops.anim.scene_range_frame()

Reset the horizontal view to the current scene frame range, taking the preview range into account if it is active

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.separate_slots"></a>

### bpy.ops.anim.separate_slots()

Move all slots of the action on the active object into newly created, separate actions. All users of those slots will be reassigned to the new actions. The current action won’t be deleted but will be empty and might end up having zero users

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.slot_channels_move_to_new_action"></a>

### bpy.ops.anim.slot_channels_move_to_new_action()

Move the selected slots into a newly created action

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.slot_new_for_id"></a>

### bpy.ops.anim.slot_new_for_id()

Create a new action slot for this data-block, to hold its animation

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/anim.py:721](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/anim.py#L721)

<a id="bpy.ops.anim.slot_unassign_from_constraint"></a>

### bpy.ops.anim.slot_unassign_from_constraint()

Un-assign the action slot from this constraint

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/anim.py:779](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/anim.py#L779)

<a id="bpy.ops.anim.slot_unassign_from_id"></a>

### bpy.ops.anim.slot_unassign_from_id()

Un-assign the action slot, effectively making this data-block non-animated

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/anim.py:758](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/anim.py#L758)

<a id="bpy.ops.anim.slot_unassign_from_nla_strip"></a>

### bpy.ops.anim.slot_unassign_from_nla_strip()

Un-assign the action slot from this NLA strip, effectively making it non-animated

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/anim.py:779](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/anim.py#L779)

<a id="bpy.ops.anim.start_frame_set"></a>

### bpy.ops.anim.start_frame_set()

Set the current frame as the preview or scene start frame

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.anim.update_animated_transform_constraints"></a>

### bpy.ops.anim.update_animated_transform_constraints(*, use_convert_to_radians=True)

Update f-curves/drivers affecting Transform constraints (use it with files from 2.70 and earlier)

**Parameters:**

**use_convert_to_radians** (bool) – Convert to Radians, Convert f-curves/drivers affecting rotations to radians.Warning: Use this only once(optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/anim.py:402](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/anim.py#L402)

<a id="bpy.ops.anim.version_bone_hide_property"></a>

### bpy.ops.anim.version_bone_hide_property()

Moves any F-Curves for the hide property of selected armatures into the action of the object. This will only operate on the first layer and strip of the action

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/anim.py:842](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/anim.py#L842)

<a id="bpy.ops.anim.view_curve_in_graph_editor"></a>

### bpy.ops.anim.view_curve_in_graph_editor(*, all=False, isolate=False)

Frame the property under the cursor in the Graph Editor

**Parameters:**

- **all** (bool) – Show All, Frame the whole array property instead of only the index under the cursor (optional)
- **isolate** (bool) – Isolate, Hides all F-Curves other than the ones being framed (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]
