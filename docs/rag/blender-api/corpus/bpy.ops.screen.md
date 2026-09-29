<!-- source: Blender Python API reference 5.2 / bpy.ops.screen.html -->

<a id="module-bpy.ops.screen"></a>

# Screen Operators

<a id="bpy.ops.screen.actionzone"></a>

### bpy.ops.screen.actionzone(*, modifier=0)

Handle area action zones for mouse actions/gestures

**Parameters:**

**modifier** (int) – Modifier, Modifier state (in [0, 2], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.screen.animation_cancel"></a>

### bpy.ops.screen.animation_cancel(*, restore_frame=True)

Cancel animation, returning to the original frame

**Parameters:**

**restore_frame** (bool) – Restore Frame, Restore the frame when animation was initialized (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.screen.animation_pause"></a>

### bpy.ops.screen.animation_pause()

Pause animation, stopping at the current frame

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.screen.animation_play"></a>

### bpy.ops.screen.animation_play(*, reverse=False, sync=False)

Play animation

**Parameters:**

- **reverse** (bool) – Play in Reverse, Animation is played backwards (optional)
- **sync** (bool) – Sync, Drop frames to maintain framerate (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.screen.animation_step"></a>

### bpy.ops.screen.animation_step()

Step through animation by position

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.screen.area_close"></a>

### bpy.ops.screen.area_close()

Close selected area

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.screen.area_dupli"></a>

### bpy.ops.screen.area_dupli()

Duplicate selected area into new window

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.screen.area_join"></a>

### bpy.ops.screen.area_join(*, source_xy=(0, 0), target_xy=(0, 0))

Join selected areas into new window

**Parameters:**

- **source_xy** (Sequence[int]) – Source location, (array of 2 items, in [-inf, inf], optional)
- **target_xy** (Sequence[int]) – Target location, (array of 2 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.screen.area_move"></a>

### bpy.ops.screen.area_move(*, x=0, y=0, delta=0, snap=False)

Move selected area edges

**Parameters:**

- **x** (int) – X, (in [-inf, inf], optional)
- **y** (int) – Y, (in [-inf, inf], optional)
- **delta** (int) – Delta, (in [-inf, inf], optional)
- **snap** (bool) – Snapping, Enable snapping (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.screen.area_options"></a>

### bpy.ops.screen.area_options()

Operations for splitting and merging

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.screen.area_split"></a>

### bpy.ops.screen.area_split(*, direction='HORIZONTAL', factor=0.5, cursor=(0, 0))

Split selected area into new windows

**Parameters:**

- **direction** (Literal['HORIZONTAL', 'VERTICAL']) – Direction, (optional)
- **factor** (float) – Factor, (in [0, 1], optional)
- **cursor** (Sequence[int]) – Cursor, (array of 2 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.screen.area_swap"></a>

### bpy.ops.screen.area_swap(*, cursor=(0, 0))

Swap selected areas screen positions

**Parameters:**

**cursor** (Sequence[int]) – Cursor, (array of 2 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.screen.back_to_previous"></a>

### bpy.ops.screen.back_to_previous()

Revert back to the original screen layout, before fullscreen area overlay

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.screen.delete"></a>

### bpy.ops.screen.delete()

Delete active screen

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.screen.drivers_editor_show"></a>

### bpy.ops.screen.drivers_editor_show()

Show drivers editor in a separate window

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.screen.edge_merge"></a>

### bpy.ops.screen.edge_merge(*, cursor=(0, 0))

Merge aligned area edges

**Parameters:**

**cursor** (Sequence[int]) – Cursor, (array of 2 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.screen.frame_jump"></a>

### bpy.ops.screen.frame_jump(*, end=False)

Jump to first/last frame in frame range

**Parameters:**

**end** (bool) – Last Frame, Jump to the last frame of the frame range (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.screen.frame_offset"></a>

### bpy.ops.screen.frame_offset(*, delta=0)

Move current frame forward/backward by a given number

**Parameters:**

**delta** (int) – Delta, (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.screen.header_toggle_menus"></a>

### bpy.ops.screen.header_toggle_menus()

Expand or collapse the header pull-down menus

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.screen.info_log_show"></a>

### bpy.ops.screen.info_log_show()

Show info log in a separate window

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.screen.keyframe_jump"></a>

### bpy.ops.screen.keyframe_jump(*, next=True)

Jump to previous/next keyframe

**Parameters:**

**next** (bool) – Next Keyframe, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.screen.marker_jump"></a>

### bpy.ops.screen.marker_jump(*, next=True)

Jump to previous/next marker

**Parameters:**

**next** (bool) – Next Marker, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.screen.new"></a>

### bpy.ops.screen.new()

Add a new screen

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.screen.quadview_size"></a>

### bpy.ops.screen.quadview_size()

Resize Quad View areas

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.screen.redo_last"></a>

### bpy.ops.screen.redo_last()

Display parameters for last action performed

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.screen.region_blend"></a>

### bpy.ops.screen.region_blend()

Blend in and out overlapping region

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.screen.region_context_menu"></a>

### bpy.ops.screen.region_context_menu()

Display region context menu

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.screen.region_flip"></a>

### bpy.ops.screen.region_flip()

Toggle the region’s alignment (left/right or top/bottom)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.screen.region_quadview"></a>

### bpy.ops.screen.region_quadview()

Split selected area into camera, front, right, and top views

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.screen.region_scale"></a>

### bpy.ops.screen.region_scale()

Scale selected area

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.screen.region_toggle"></a>

### bpy.ops.screen.region_toggle(*, region_type='WINDOW')

Hide or unhide the region

**Parameters:**

**region_type** (Literal[[Region Type Items](bpy_types_enum_items/region_type_items.md#rna-enum-region-type-items)]) – Region Type, Type of the region to toggle (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.screen.repeat_history"></a>

### bpy.ops.screen.repeat_history(*, index=0)

Display menu for previous actions performed

**Parameters:**

**index** (int) – Index, (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.screen.repeat_last"></a>

### bpy.ops.screen.repeat_last()

Repeat last action

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.screen.screen_full_area"></a>

### bpy.ops.screen.screen_full_area(*, use_hide_panels=False)

Toggle display selected area as fullscreen/maximized

**Parameters:**

**use_hide_panels** (bool) – Hide Panels, Hide all the panels (Focus Mode) (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.screen.screen_set"></a>

### bpy.ops.screen.screen_set(*, delta=1)

Cycle through available screens

**Parameters:**

**delta** (int) – Delta, (in [-1, 1], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.screen.screenshot"></a>

### bpy.ops.screen.screenshot(*, filepath='', hide_props_region=True, check_existing=True, filter_blender=False, filter_backup=False, filter_image=True, filter_movie=False, filter_python=False, filter_font=False, filter_sound=False, filter_text=False, filter_archive=False, filter_btx=False, filter_alembic=False, filter_usd=False, filter_obj=False, filter_volume=False, filter_folder=True, filter_blenlib=False, filemode=9, show_multiview=False, use_multiview=False, display_type='DEFAULT', sort_method='')

Capture a picture of the whole Blender window

**Parameters:**

- **filepath** (str) – File Path, Path to file (optional, never None)
- **hide_props_region** (bool) – Hide Operator Properties, Collapse the region displaying the operator settings (optional)
- **check_existing** (bool) – Check Existing, Check and warn on overwriting existing files (optional)
- **filter_blender** (bool) – Filter .blend files, (optional)
- **filter_backup** (bool) – Filter backup .blend files, (optional)
- **filter_image** (bool) – Filter image files, (optional)
- **filter_movie** (bool) – Filter movie files, (optional)
- **filter_python** (bool) – Filter Python files, (optional)
- **filter_font** (bool) – Filter font files, (optional)
- **filter_sound** (bool) – Filter sound files, (optional)
- **filter_text** (bool) – Filter text files, (optional)
- **filter_archive** (bool) – Filter archive files, (optional)
- **filter_btx** (bool) – Filter btx files, (optional)
- **filter_alembic** (bool) – Filter Alembic files, (optional)
- **filter_usd** (bool) – Filter USD files, (optional)
- **filter_obj** (bool) – Filter OBJ files, (optional)
- **filter_volume** (bool) – Filter OpenVDB volume files, (optional)
- **filter_folder** (bool) – Filter folders, (optional)
- **filter_blenlib** (bool) – Filter Blender IDs, (optional)
- **filemode** (int) – File Browser Mode, The setting for the file browser mode to load a .blend file, a library or a special file (in [1, 9], optional)
- **show_multiview** (bool) – Enable Multi-View, (optional)
- **use_multiview** (bool) – Use Multi-View, (optional)
- **display_type** (Literal['DEFAULT', 'LIST_VERTICAL', 'LIST_HORIZONTAL', 'THUMBNAIL']) –

  Display Type, (optional)

  - `DEFAULT`
    Default – Automatically determine display type for files.
  - `LIST_VERTICAL`
    Short List – Display files as short list.
  - `LIST_HORIZONTAL`
    Long List – Display files as a detailed list.
  - `THUMBNAIL`
    Thumbnails – Display files as thumbnails.
- **sort_method** (str) – File sorting mode, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.screen.screenshot_area"></a>

### bpy.ops.screen.screenshot_area(*, filepath='', hide_props_region=True, check_existing=True, filter_blender=False, filter_backup=False, filter_image=True, filter_movie=False, filter_python=False, filter_font=False, filter_sound=False, filter_text=False, filter_archive=False, filter_btx=False, filter_alembic=False, filter_usd=False, filter_obj=False, filter_volume=False, filter_folder=True, filter_blenlib=False, filemode=9, show_multiview=False, use_multiview=False, display_type='DEFAULT', sort_method='')

Capture a picture of an editor

**Parameters:**

- **filepath** (str) – File Path, Path to file (optional, never None)
- **hide_props_region** (bool) – Hide Operator Properties, Collapse the region displaying the operator settings (optional)
- **check_existing** (bool) – Check Existing, Check and warn on overwriting existing files (optional)
- **filter_blender** (bool) – Filter .blend files, (optional)
- **filter_backup** (bool) – Filter backup .blend files, (optional)
- **filter_image** (bool) – Filter image files, (optional)
- **filter_movie** (bool) – Filter movie files, (optional)
- **filter_python** (bool) – Filter Python files, (optional)
- **filter_font** (bool) – Filter font files, (optional)
- **filter_sound** (bool) – Filter sound files, (optional)
- **filter_text** (bool) – Filter text files, (optional)
- **filter_archive** (bool) – Filter archive files, (optional)
- **filter_btx** (bool) – Filter btx files, (optional)
- **filter_alembic** (bool) – Filter Alembic files, (optional)
- **filter_usd** (bool) – Filter USD files, (optional)
- **filter_obj** (bool) – Filter OBJ files, (optional)
- **filter_volume** (bool) – Filter OpenVDB volume files, (optional)
- **filter_folder** (bool) – Filter folders, (optional)
- **filter_blenlib** (bool) – Filter Blender IDs, (optional)
- **filemode** (int) – File Browser Mode, The setting for the file browser mode to load a .blend file, a library or a special file (in [1, 9], optional)
- **show_multiview** (bool) – Enable Multi-View, (optional)
- **use_multiview** (bool) – Use Multi-View, (optional)
- **display_type** (Literal['DEFAULT', 'LIST_VERTICAL', 'LIST_HORIZONTAL', 'THUMBNAIL']) –

  Display Type, (optional)

  - `DEFAULT`
    Default – Automatically determine display type for files.
  - `LIST_VERTICAL`
    Short List – Display files as short list.
  - `LIST_HORIZONTAL`
    Long List – Display files as a detailed list.
  - `THUMBNAIL`
    Thumbnails – Display files as thumbnails.
- **sort_method** (str) – File sorting mode, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.screen.space_context_cycle"></a>

### bpy.ops.screen.space_context_cycle(*, direction='NEXT')

Cycle through the editor context by activating the next/previous one

**Parameters:**

**direction** (Literal['PREV', 'NEXT']) – Direction, Direction to cycle through (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.screen.space_type_set_or_cycle"></a>

### bpy.ops.screen.space_type_set_or_cycle(*, space_type='EMPTY')

Set the space type or cycle subtype

**Parameters:**

**space_type** (Literal[[Space Type Items](bpy_types_enum_items/space_type_items.md#rna-enum-space-type-items)]) – Type, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.screen.spacedata_cleanup"></a>

### bpy.ops.screen.spacedata_cleanup()

Remove unused settings for invisible editors

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.screen.time_jump"></a>

### bpy.ops.screen.time_jump(*, backward=False)

Jump forward/backward by a given number of frames or seconds

**Parameters:**

**backward** (bool) – Backwards, Jump backwards in time (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.screen.userpref_show"></a>

### bpy.ops.screen.userpref_show(*, section='INTERFACE')

Edit user preferences and system settings

**Parameters:**

**section** (Literal[[Preference Section Items](bpy_types_enum_items/preference_section_items.md#rna-enum-preference-section-items)]) – Section to activate in the Preferences (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.screen.workspace_cycle"></a>

### bpy.ops.screen.workspace_cycle(*, direction='NEXT')

Cycle through workspaces

**Parameters:**

**direction** (Literal['PREV', 'NEXT']) – Direction, Direction to cycle through (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]
