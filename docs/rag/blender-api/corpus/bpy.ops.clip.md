<!-- source: Blender Python API reference 5.2 / bpy.ops.clip.html -->

<a id="module-bpy.ops.clip"></a>

# Clip Operators

<a id="bpy.ops.clip.add_marker"></a>

### bpy.ops.clip.add_marker(*, location=(0.0, 0.0))

Place new marker at specified location

**Parameters:**

**location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Location of marker on frame (array of 2 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.add_marker_at_click"></a>

### bpy.ops.clip.add_marker_at_click()

Place new marker at the desired (clicked) position

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.add_marker_move"></a>

### bpy.ops.clip.add_marker_move(*, CLIP_OT_add_marker={}, TRANSFORM_OT_translate={})

Add new marker and move it on movie

**Parameters:**

- **CLIP_OT_add_marker** (dict[str, Any]) – Add Marker, Place new marker at specified location (optional, [`bpy.ops.clip.add_marker()`](#bpy.ops.clip.add_marker "bpy.ops.clip.add_marker") keyword arguments)
- **TRANSFORM_OT_translate** (dict[str, Any]) – Move, Move selected items (optional, [`bpy.ops.transform.translate()`](bpy.ops.transform.md#bpy.ops.transform.translate "bpy.ops.transform.translate") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.add_marker_slide"></a>

### bpy.ops.clip.add_marker_slide(*, CLIP_OT_add_marker={}, TRANSFORM_OT_translate={})

Add new marker and slide it with mouse until mouse button release

**Parameters:**

- **CLIP_OT_add_marker** (dict[str, Any]) – Add Marker, Place new marker at specified location (optional, [`bpy.ops.clip.add_marker()`](#bpy.ops.clip.add_marker "bpy.ops.clip.add_marker") keyword arguments)
- **TRANSFORM_OT_translate** (dict[str, Any]) – Move, Move selected items (optional, [`bpy.ops.transform.translate()`](bpy.ops.transform.md#bpy.ops.transform.translate "bpy.ops.transform.translate") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.apply_solution_scale"></a>

### bpy.ops.clip.apply_solution_scale(*, distance=0.0)

Apply scale on solution itself to make distance between selected tracks equals to desired

**Parameters:**

**distance** (float) – Distance, Distance between selected tracks (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.average_tracks"></a>

### bpy.ops.clip.average_tracks(*, keep_original=True)

Average selected tracks into active

**Parameters:**

**keep_original** (bool) – Keep Original, Keep original tracks (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.bundles_to_mesh"></a>

### bpy.ops.clip.bundles_to_mesh()

Create vertex cloud using coordinates of reconstructed tracks

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/clip.py:292](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/clip.py#L292)

<a id="bpy.ops.clip.camera_preset_add"></a>

### bpy.ops.clip.camera_preset_add(*, name='', remove_name=False, remove_active=False, use_focal_length=True)

Add or remove a Tracking Camera Intrinsics Preset

**Parameters:**

- **name** (str) – Name, Name of the preset, used to make the path name (optional, never None)
- **remove_name** (bool) – remove_name, (optional)
- **remove_active** (bool) – remove_active, (optional)
- **use_focal_length** (bool) – Include Focal Length, Include focal length into the preset (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/presets.py:119](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/presets.py#L119)

<a id="bpy.ops.clip.change_frame"></a>

### bpy.ops.clip.change_frame(*, frame=0)

Interactively change the current frame number

**Parameters:**

**frame** (int) – Frame, (in [-1048574, 1048574], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.clean_tracks"></a>

### bpy.ops.clip.clean_tracks(*, frames=0, error=0.0, action='SELECT')

Clean tracks with high error values or few frames

**Parameters:**

- **frames** (int) – Tracked Frames, Affect tracks which are tracked less than the specified number of frames (in [0, inf], optional)
- **error** (float) – Reprojection Error, Affect tracks which have a larger reprojection error (in [0, inf], optional)
- **action** (Literal['SELECT', 'DELETE_TRACK', 'DELETE_SEGMENTS']) –

  Action, Cleanup action to execute (optional)

  - `SELECT`
    Select – Select unclean tracks.
  - `DELETE_TRACK`
    Delete Track – Delete unclean tracks.
  - `DELETE_SEGMENTS`
    Delete Segments – Delete unclean segments of tracks.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.clear_solution"></a>

### bpy.ops.clip.clear_solution()

Clear all calculated data

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.clear_track_path"></a>

### bpy.ops.clip.clear_track_path(*, action='REMAINED', clear_active=False)

Clear tracks after/before current position or clear the whole track

**Parameters:**

- **action** (Literal['UPTO', 'REMAINED', 'ALL']) –

  Action, Clear action to execute (optional)

  - `UPTO`
    Clear Up To – Clear path up to current frame.
  - `REMAINED`
    Clear Remained – Clear path at remaining frames (after current).
  - `ALL`
    Clear All – Clear the whole path.
- **clear_active** (bool) – Clear Active, Clear active track only instead of all selected tracks (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.constraint_to_fcurve"></a>

### bpy.ops.clip.constraint_to_fcurve()

Create F-Curves for object which will copy object’s movement caused by this constraint

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/clip.py:520](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/clip.py#L520)

<a id="bpy.ops.clip.copy_tracks"></a>

### bpy.ops.clip.copy_tracks()

Copy the selected tracks to the internal clipboard

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.create_plane_track"></a>

### bpy.ops.clip.create_plane_track()

Create new plane track out of selected point tracks

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.cursor_set"></a>

### bpy.ops.clip.cursor_set(*, location=(0.0, 0.0))

Set 2D cursor location

**Parameters:**

**location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Cursor location in normalized clip coordinates (array of 2 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.delete_marker"></a>

### bpy.ops.clip.delete_marker(*, confirm=True)

Delete marker for current frame from selected tracks

**Parameters:**

**confirm** (bool) – Confirm, Prompt for confirmation (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.delete_proxy"></a>

### bpy.ops.clip.delete_proxy()

Delete movie clip proxy files from the hard drive

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/clip.py:359](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/clip.py#L359)

<a id="bpy.ops.clip.delete_track"></a>

### bpy.ops.clip.delete_track(*, confirm=True)

Delete selected tracks

**Parameters:**

**confirm** (bool) – Confirm, Prompt for confirmation (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.detect_features"></a>

### bpy.ops.clip.detect_features(*, placement='FRAME', margin=16, threshold=0.5, min_distance=120)

Automatically detect features and place markers to track

**Parameters:**

- **placement** (Literal['FRAME', 'INSIDE_GPENCIL', 'OUTSIDE_GPENCIL']) –

  Placement, Placement for detected features (optional)

  - `FRAME`
    Whole Frame – Place markers across the whole frame.
  - `INSIDE_GPENCIL`
    Inside Annotated Area – Place markers only inside areas outlined with the Annotation tool.
  - `OUTSIDE_GPENCIL`
    Outside Annotated Area – Place markers only outside areas outlined with the Annotation tool.
- **margin** (int) – Margin, Only features further than margin pixels from the image edges are considered (in [0, inf], optional)
- **threshold** (float) – Threshold, Threshold level to consider feature good enough for tracking (in [0.0001, inf], optional)
- **min_distance** (int) – Distance, Minimal distance accepted between two features (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.disable_markers"></a>

### bpy.ops.clip.disable_markers(*, action='DISABLE')

Disable/enable selected markers

**Parameters:**

**action** (Literal['DISABLE', 'ENABLE', 'TOGGLE']) –

Action, Disable action to execute (optional)

- `DISABLE`
  Disable – Disable selected markers.
- `ENABLE`
  Enable – Enable selected markers.
- `TOGGLE`
  Toggle – Toggle disabled flag for selected markers.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.dopesheet_select_channel"></a>

### bpy.ops.clip.dopesheet_select_channel(*, location=(0.0, 0.0), extend=False)

Select movie tracking channel

**Parameters:**

- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Mouse location to select channel (array of 2 items, in [-inf, inf], optional)
- **extend** (bool) – Extend, Extend selection rather than clearing the existing selection (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.dopesheet_view_all"></a>

### bpy.ops.clip.dopesheet_view_all()

Reset viewable area to show full keyframe range

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.filter_tracks"></a>

### bpy.ops.clip.filter_tracks(*, track_threshold=5.0)

Filter tracks which has weirdly looking spikes in motion curves

**Parameters:**

**track_threshold** (float) – Track Threshold, Filter Threshold to select problematic tracks (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/clip.py:206](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/clip.py#L206)

<a id="bpy.ops.clip.frame_jump"></a>

### bpy.ops.clip.frame_jump(*, position='PATHSTART')

Jump to special frame

**Parameters:**

**position** (Literal['PATHSTART', 'PATHEND', 'FAILEDPREV', 'FAILNEXT']) –

Position, Position to jump to (optional)

- `PATHSTART`
  Path Start – Jump to start of current path.
- `PATHEND`
  Path End – Jump to end of current path.
- `FAILEDPREV`
  Previous Failed – Jump to previous failed frame.
- `FAILNEXT`
  Next Failed – Jump to next failed frame.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.graph_center_current_frame"></a>

### bpy.ops.clip.graph_center_current_frame()

Scroll view so current frame would be centered

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.graph_delete_curve"></a>

### bpy.ops.clip.graph_delete_curve(*, confirm=True)

Delete track corresponding to the selected curve

**Parameters:**

**confirm** (bool) – Confirm, Prompt for confirmation (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.graph_delete_knot"></a>

### bpy.ops.clip.graph_delete_knot()

Delete curve knots

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.graph_disable_markers"></a>

### bpy.ops.clip.graph_disable_markers(*, action='DISABLE')

Disable/enable selected markers

**Parameters:**

**action** (Literal['DISABLE', 'ENABLE', 'TOGGLE']) –

Action, Disable action to execute (optional)

- `DISABLE`
  Disable – Disable selected markers.
- `ENABLE`
  Enable – Enable selected markers.
- `TOGGLE`
  Toggle – Toggle disabled flag for selected markers.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.graph_select"></a>

### bpy.ops.clip.graph_select(*, location=(0.0, 0.0), extend=False)

Select graph curves

**Parameters:**

- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Mouse location to select nearest entity (array of 2 items, in [-inf, inf], optional)
- **extend** (bool) – Extend, Extend selection rather than clearing the existing selection (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.graph_select_all_markers"></a>

### bpy.ops.clip.graph_select_all_markers(*, action='TOGGLE')

Change selection of all markers of active track

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

<a id="bpy.ops.clip.graph_select_box"></a>

### bpy.ops.clip.graph_select_box(*, xmin=0, xmax=0, ymin=0, ymax=0, wait_for_input=True, deselect=False, extend=True)

Select curve points using box selection

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

<a id="bpy.ops.clip.graph_view_all"></a>

### bpy.ops.clip.graph_view_all()

View all curves in editor

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.hide_tracks"></a>

### bpy.ops.clip.hide_tracks(*, unselected=False)

Hide selected tracks

**Parameters:**

**unselected** (bool) – Unselected, Hide unselected tracks (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.hide_tracks_clear"></a>

### bpy.ops.clip.hide_tracks_clear()

Clear hide selected tracks

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.join_tracks"></a>

### bpy.ops.clip.join_tracks()

Join selected tracks

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.keyframe_delete"></a>

### bpy.ops.clip.keyframe_delete()

Delete a keyframe from selected tracks at current frame

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.keyframe_insert"></a>

### bpy.ops.clip.keyframe_insert()

Insert a keyframe to selected tracks at current frame

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.lock_selection_toggle"></a>

### bpy.ops.clip.lock_selection_toggle()

Toggle Lock Selection option of the current clip editor

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.lock_tracks"></a>

### bpy.ops.clip.lock_tracks(*, action='LOCK')

Lock/unlock selected tracks

**Parameters:**

**action** (Literal['LOCK', 'UNLOCK', 'TOGGLE']) –

Action, Lock action to execute (optional)

- `LOCK`
  Lock – Lock selected tracks.
- `UNLOCK`
  Unlock – Unlock selected tracks.
- `TOGGLE`
  Toggle – Toggle locked flag for selected tracks.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.mode_set"></a>

### bpy.ops.clip.mode_set(*, mode='TRACKING')

Set the clip interaction mode

**Parameters:**

**mode** (Literal[[Clip Editor Mode Items](bpy_types_enum_items/clip_editor_mode_items.md#rna-enum-clip-editor-mode-items)]) – Mode, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.new_image_from_plane_marker"></a>

### bpy.ops.clip.new_image_from_plane_marker()

Create new image from the content of the plane marker

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.open"></a>

### bpy.ops.clip.open(*, directory='', files=None, hide_props_region=True, check_existing=False, filter_blender=False, filter_backup=False, filter_image=True, filter_movie=True, filter_python=False, filter_font=False, filter_sound=False, filter_text=False, filter_archive=False, filter_btx=False, filter_alembic=False, filter_usd=False, filter_obj=False, filter_volume=False, filter_folder=True, filter_blenlib=False, filemode=9, relative_path=True, show_multiview=False, use_multiview=False, display_type='DEFAULT', sort_method='')

Load a sequence of frames or a movie file

**Parameters:**

- **directory** (str) – Directory, Directory of the file (optional, never None)
- **files** (`bpy_prop_collection`[`OperatorFileListElement`] | None) – Files, (optional)
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
- **relative_path** (bool) – Relative Path, Select the file relative to the blend file (optional)
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
- **sort_method** (Literal['', 'DEFAULT', 'FILE_SORT_ALPHA', 'FILE_SORT_EXTENSION', 'FILE_SORT_TIME', 'FILE_SORT_SIZE', 'ASSET_CATALOG']) –

  File sorting mode, (optional)

  - `DEFAULT`
    Default – Automatically determine sort method for files.
  - `FILE_SORT_ALPHA`
    Name – Sort the file list alphabetically.
  - `FILE_SORT_EXTENSION`
    Extension – Sort the file list by extension/type.
  - `FILE_SORT_TIME`
    Modified Date – Sort files by modification time.
  - `FILE_SORT_SIZE`
    Size – Sort files by size.
  - `ASSET_CATALOG`
    Asset Catalog – Sort the asset list so that assets in the same catalog are kept together. Within a single catalog, assets are ordered by name. The catalogs are in order of the flattened catalog hierarchy..

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.paste_tracks"></a>

### bpy.ops.clip.paste_tracks()

Paste tracks from the internal clipboard

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.prefetch"></a>

### bpy.ops.clip.prefetch()

Prefetch frames from disk for faster playback/tracking

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.rebuild_proxy"></a>

### bpy.ops.clip.rebuild_proxy()

Rebuild all selected proxies in the background

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.refine_markers"></a>

### bpy.ops.clip.refine_markers(*, backwards=False)

Refine selected markers positions by running the tracker from track’s reference to current frame

**Parameters:**

**backwards** (bool) – Backwards, Do backwards tracking (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.reload"></a>

### bpy.ops.clip.reload()

Reload clip

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.select"></a>

### bpy.ops.clip.select(*, extend=False, deselect_all=False, location=(0.0, 0.0))

Select tracking markers

**Parameters:**

- **extend** (bool) – Extend, Extend selection rather than clearing the existing selection (optional)
- **deselect_all** (bool) – Deselect On Nothing, Deselect all when nothing under the cursor (optional)
- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Mouse location in normalized coordinates, 0.0 to 1.0 is within the image bounds (array of 2 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.select_all"></a>

### bpy.ops.clip.select_all(*, action='TOGGLE')

Change selection of all tracking markers

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

<a id="bpy.ops.clip.select_box"></a>

### bpy.ops.clip.select_box(*, xmin=0, xmax=0, ymin=0, ymax=0, wait_for_input=True, mode='SET')

Select markers using box selection

**Parameters:**

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

<a id="bpy.ops.clip.select_circle"></a>

### bpy.ops.clip.select_circle(*, x=0, y=0, radius=25, wait_for_input=True, mode='SET')

Select markers using circle selection

**Parameters:**

- **x** (int) – X, (in [-inf, inf], optional)
- **y** (int) – Y, (in [-inf, inf], optional)
- **radius** (int) – Radius, (in [1, inf], optional)
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

<a id="bpy.ops.clip.select_grouped"></a>

### bpy.ops.clip.select_grouped(*, group='ESTIMATED')

Select all tracks from specified group

**Parameters:**

**group** (Literal['KEYFRAMED', 'ESTIMATED', 'TRACKED', 'LOCKED', 'DISABLED', 'COLOR', 'FAILED']) –

Group, Select tracks by group (optional)

- `KEYFRAMED`
  Keyframed Tracks – Select all keyframed tracks.
- `ESTIMATED`
  Estimated Tracks – Select all estimated tracks.
- `TRACKED`
  Tracked Tracks – Select all tracked tracks.
- `LOCKED`
  Locked Tracks – Select all locked tracks.
- `DISABLED`
  Disabled Tracks – Select all disabled tracks.
- `COLOR`
  Tracks with Same Color – Select all tracks with same color as active track.
- `FAILED`
  Failed Tracks – Select all tracks which failed to be reconstructed.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.select_lasso"></a>

### bpy.ops.clip.select_lasso(*, path=None, use_smooth_stroke=False, smooth_stroke_factor=0.75, smooth_stroke_radius=35, mode='SET')

Select markers using lasso selection

**Parameters:**

- **path** (`bpy_prop_collection`[`OperatorMousePath`] | None) – Path, (optional)
- **use_smooth_stroke** (bool) – Stabilize Stroke, Selection lags behind mouse and follows a smoother path (optional)
- **smooth_stroke_factor** (float) – Smooth Stroke Factor, Higher values give a smoother stroke (in [0.5, 0.99], optional)
- **smooth_stroke_radius** (int) – Smooth Stroke Radius, Minimum distance from last point before selection continues (in [10, 200], optional)
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

<a id="bpy.ops.clip.set_active_clip"></a>

### bpy.ops.clip.set_active_clip()

Undocumented, consider [contributing](https://developer.blender.org/).

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/clip.py:221](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/clip.py#L221)

<a id="bpy.ops.clip.set_axis"></a>

### bpy.ops.clip.set_axis(*, axis='X')

Set the direction of a scene axis by rotating the camera (or its parent if present). This assumes that the selected track lies on a real axis connecting it to the origin

**Parameters:**

**axis** (Literal['X', 'Y']) –

Axis, Axis to use to align bundle along (optional)

- `X`
  X – Align bundle to X axis.
- `Y`
  Y – Align bundle to Y axis.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.set_origin"></a>

### bpy.ops.clip.set_origin(*, use_median=False)

Set active marker as origin by moving camera (or its parent if present) in 3D space

**Parameters:**

**use_median** (bool) – Use Median, Set origin to median point of selected bundles (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.set_plane"></a>

### bpy.ops.clip.set_plane(*, plane='FLOOR')

Set plane based on 3 selected bundles by moving camera (or its parent if present) in 3D space

**Parameters:**

**plane** (Literal['FLOOR', 'WALL']) –

Plane, Plane to be used for orientation (optional)

- `FLOOR`
  Floor – Set floor plane.
- `WALL`
  Wall – Set wall plane.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.set_scale"></a>

### bpy.ops.clip.set_scale(*, distance=0.0)

Set scale of scene by scaling camera (or its parent if present)

**Parameters:**

**distance** (float) – Distance, Distance between selected tracks (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.set_scene_frames"></a>

### bpy.ops.clip.set_scene_frames()

Set scene’s start and end frame to match clip’s start frame and length

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.set_solution_scale"></a>

### bpy.ops.clip.set_solution_scale(*, distance=0.0)

Set object solution scale using distance between two selected tracks

**Parameters:**

**distance** (float) – Distance, Distance between selected tracks (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.set_solver_keyframe"></a>

### bpy.ops.clip.set_solver_keyframe(*, keyframe='KEYFRAME_A')

Set keyframe used by solver

**Parameters:**

**keyframe** (Literal['KEYFRAME_A', 'KEYFRAME_B']) – Keyframe, Keyframe to set (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.set_viewport_background"></a>

### bpy.ops.clip.set_viewport_background()

Set current movie clip as a camera background in 3D Viewport (works only when a 3D Viewport is visible)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/clip.py:410](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/clip.py#L410)

<a id="bpy.ops.clip.setup_tracking_scene"></a>

### bpy.ops.clip.setup_tracking_scene()

Prepare scene for compositing 3D objects into this footage

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/clip.py:926](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/clip.py#L926)

<a id="bpy.ops.clip.slide_marker"></a>

### bpy.ops.clip.slide_marker(*, offset=(0.0, 0.0))

Slide marker areas

**Parameters:**

**offset** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Offset, Offset in floating-point units, 1.0 is the width and height of the image (array of 2 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.slide_plane_marker"></a>

### bpy.ops.clip.slide_plane_marker()

Slide plane marker areas

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.solve_camera"></a>

### bpy.ops.clip.solve_camera()

Solve camera motion from tracks

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.stabilize_2d_add"></a>

### bpy.ops.clip.stabilize_2d_add()

Add selected tracks to 2D translation stabilization

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.stabilize_2d_remove"></a>

### bpy.ops.clip.stabilize_2d_remove()

Remove selected track from translation stabilization

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.stabilize_2d_rotation_add"></a>

### bpy.ops.clip.stabilize_2d_rotation_add()

Add selected tracks to 2D rotation stabilization

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.stabilize_2d_rotation_remove"></a>

### bpy.ops.clip.stabilize_2d_rotation_remove()

Remove selected track from rotation stabilization

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.stabilize_2d_rotation_select"></a>

### bpy.ops.clip.stabilize_2d_rotation_select()

Select tracks which are used for rotation stabilization

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.stabilize_2d_select"></a>

### bpy.ops.clip.stabilize_2d_select()

Select tracks which are used for translation stabilization

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.track_color_preset_add"></a>

### bpy.ops.clip.track_color_preset_add(*, name='', remove_name=False, remove_active=False)

Add or remove a Clip Track Color Preset

**Parameters:**

- **name** (str) – Name, Name of the preset, used to make the path name (optional, never None)
- **remove_name** (bool) – remove_name, (optional)
- **remove_active** (bool) – remove_active, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/presets.py:119](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/presets.py#L119)

<a id="bpy.ops.clip.track_copy_color"></a>

### bpy.ops.clip.track_copy_color()

Copy color to all selected tracks

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.track_markers"></a>

### bpy.ops.clip.track_markers(*, backwards=False, sequence=False)

Track selected markers

**Parameters:**

- **backwards** (bool) – Backwards, Do backwards tracking (optional)
- **sequence** (bool) – Track Sequence, Track marker during image sequence rather than single image (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.track_settings_as_default"></a>

### bpy.ops.clip.track_settings_as_default()

Copy tracking settings from active track to default settings

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/clip.py:955](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/clip.py#L955)

<a id="bpy.ops.clip.track_settings_to_track"></a>

### bpy.ops.clip.track_settings_to_track()

Copy tracking settings from active track to selected tracks

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/clip.py:1004](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/clip.py#L1004)

<a id="bpy.ops.clip.track_to_empty"></a>

### bpy.ops.clip.track_to_empty()

Create an Empty object which will be copying movement of active track

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/clip.py:268](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/clip.py#L268)

<a id="bpy.ops.clip.tracking_object_new"></a>

### bpy.ops.clip.tracking_object_new()

Add new object for tracking

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.tracking_object_remove"></a>

### bpy.ops.clip.tracking_object_remove()

Remove object for tracking

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.tracking_settings_preset_add"></a>

### bpy.ops.clip.tracking_settings_preset_add(*, name='', remove_name=False, remove_active=False)

Add or remove a motion tracking settings preset

**Parameters:**

- **name** (str) – Name, Name of the preset, used to make the path name (optional, never None)
- **remove_name** (bool) – remove_name, (optional)
- **remove_active** (bool) – remove_active, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/presets.py:119](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/presets.py#L119)

<a id="bpy.ops.clip.update_image_from_plane_marker"></a>

### bpy.ops.clip.update_image_from_plane_marker()

Update current image used by plane marker from the content of the plane marker

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.view_all"></a>

### bpy.ops.clip.view_all(*, fit_view=False)

View whole image with markers

**Parameters:**

**fit_view** (bool) – Fit View, Fit frame to the viewport (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.view_center_cursor"></a>

### bpy.ops.clip.view_center_cursor()

Center the view so that the cursor is in the middle of the view

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.view_ndof"></a>

### bpy.ops.clip.view_ndof()

Use a 3D mouse device to pan/zoom the view

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.view_pan"></a>

### bpy.ops.clip.view_pan(*, offset=(0.0, 0.0))

Pan the view

**Parameters:**

**offset** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Offset, Offset in floating-point units, 1.0 is the width and height of the image (array of 2 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.view_selected"></a>

### bpy.ops.clip.view_selected()

View all selected elements

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.view_zoom"></a>

### bpy.ops.clip.view_zoom(*, factor=0.0, use_cursor_init=True)

Zoom in/out the view

**Parameters:**

- **factor** (float) – Factor, Zoom factor, values higher than 1.0 zoom in, lower values zoom out (in [-inf, inf], optional)
- **use_cursor_init** (bool) – Use Mouse Position, Allow the initial mouse position to be used (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.view_zoom_in"></a>

### bpy.ops.clip.view_zoom_in(*, location=(0.0, 0.0))

Zoom in the view

**Parameters:**

**location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Cursor location in screen coordinates (array of 2 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.view_zoom_out"></a>

### bpy.ops.clip.view_zoom_out(*, location=(0.0, 0.0))

Zoom out the view

**Parameters:**

**location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Cursor location in normalized (0.0 to 1.0) coordinates (array of 2 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.clip.view_zoom_ratio"></a>

### bpy.ops.clip.view_zoom_ratio(*, ratio=0.0)

Set the zoom ratio (based on clip size)

**Parameters:**

**ratio** (float) – Ratio, Zoom ratio, 1.0 is 1:1, higher is zoomed in, lower is zoomed out (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]
