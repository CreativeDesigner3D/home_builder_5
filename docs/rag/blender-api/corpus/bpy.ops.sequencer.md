<!-- source: Blender Python API reference 5.2 / bpy.ops.sequencer.html -->

<a id="module-bpy.ops.sequencer"></a>

# Sequencer Operators

<a id="bpy.ops.sequencer.add_scene_strip_from_scene_asset"></a>

### bpy.ops.sequencer.add_scene_strip_from_scene_asset(*, move_strips=True, frame_start=0, channel=1, replace_sel=True, overlap=False, overlap_shuffle_override=False, skip_locked_or_muted_channels=True, asset_library_type='LOCAL', asset_library_identifier='', relative_asset_identifier='')

Add a strip using a duplicate of this scene asset as the source

**Parameters:**

- **move_strips** (bool) – Move Strips, Automatically begin translating strips with the mouse after adding them to the timeline (optional)
- **frame_start** (int) – Start Frame, Start frame of the strip (in [-inf, inf], optional)
- **channel** (int) – Channel, Channel to place this strip into (in [1, 128], optional)
- **replace_sel** (bool) – Replace Selection, Deselect previously selected strips after add operation completes (optional)
- **overlap** (bool) – Allow Overlap, Don’t correct overlap on new strips (optional)
- **overlap_shuffle_override** (bool) – Override Overlap Shuffle Behavior, Use the overlap_mode tool settings to determine how to shuffle overlapping strips (optional)
- **skip_locked_or_muted_channels** (bool) – Skip Locked/Muted Channels, Make strips occupy nearest unmuted and unlocked channels (optional)
- **asset_library_type** (Literal[[Asset Library Type Items](bpy_types_enum_items/asset_library_type_items.md#rna-enum-asset-library-type-items)]) – Asset Library Type, (optional)
- **asset_library_identifier** (str) – Asset Library Identifier, (optional, never None)
- **relative_asset_identifier** (str) – Relative Asset Identifier, (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.box_blade"></a>

### bpy.ops.sequencer.box_blade(*, xmin=0, xmax=0, ymin=0, ymax=0, wait_for_input=True, mode='SET', type='SOFT', ignore_selection=True, ignore_connections=False, remove_gaps=True)

Draw a box around the parts of strips you want to cut away

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
- **type** (Literal['SOFT', 'HARD']) – Type, The type of split operation to perform on strips (optional)
- **ignore_selection** (bool) – Ignore Selection, In box blade mode, make cuts to all strips, even if they are not selected (optional)
- **ignore_connections** (bool) – Ignore Connections, Don’t propagate split to connected strips (optional)
- **remove_gaps** (bool) – Remove Gaps, In box blade mode, close gaps between cut strips, rippling later strips on the same channel (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.change_effect_type"></a>

### bpy.ops.sequencer.change_effect_type(*, type='CROSS')

Replace effect strip with another that takes the same number of inputs

**Parameters:**

**type** (Literal['CROSS', 'ADD', 'SUBTRACT', 'ALPHA_OVER', 'ALPHA_UNDER', 'GAMMA_CROSS', 'MULTIPLY', 'WIPE', 'GLOW', 'COLOR', 'SPEED', 'MULTICAM', 'ADJUSTMENT', 'GAUSSIAN_BLUR', 'TEXT', 'COLORMIX', 'COMPOSITOR']) –

Type, Strip effect type (optional)

- `CROSS`
  Crossfade – Fade out of one video, fading into another.
- `ADD`
  Add – Add together color channels from two videos.
- `SUBTRACT`
  Subtract – Subtract one strip’s color from another.
- `ALPHA_OVER`
  Alpha Over – Blend alpha on top of another video.
- `ALPHA_UNDER`
  Alpha Under – Blend alpha below another video.
- `GAMMA_CROSS`
  Gamma Crossfade – Crossfade with color correction.
- `MULTIPLY`
  Multiply – Multiply color channels from two videos.
- `WIPE`
  Wipe – Sweep a transition line across the frame.
- `GLOW`
  Glow – Add blur and brightness to light areas.
- `COLOR`
  Color – Add a simple color strip.
- `SPEED`
  Speed – Timewarp video strips, modifying playback speed.
- `MULTICAM`
  Multicam Selector – Control active camera angles.
- `ADJUSTMENT`
  Adjustment Layer – Apply nondestructive effects.
- `GAUSSIAN_BLUR`
  Gaussian Blur – Soften details along axes.
- `TEXT`
  Text – Add a simple text strip.
- `COLORMIX`
  Color Mix – Combine two strips using blend modes.
- `COMPOSITOR`
  Compositor – Compositor based effect.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.change_path"></a>

### bpy.ops.sequencer.change_path(*, filepath='', directory='', files=None, hide_props_region=True, check_existing=False, filter_blender=False, filter_backup=False, filter_image=False, filter_movie=False, filter_python=False, filter_font=False, filter_sound=False, filter_text=False, filter_archive=False, filter_btx=False, filter_alembic=False, filter_usd=False, filter_obj=False, filter_volume=False, filter_folder=True, filter_blenlib=False, filemode=9, relative_path=True, display_type='DEFAULT', sort_method='', use_sequence_detection=True, use_placeholders=False)

Undocumented, consider [contributing](https://developer.blender.org/).

**Parameters:**

- **filepath** (str) – File Path, Path to file (optional, never None)
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
- **use_sequence_detection** (bool) – Detect Sequences, Automatically detect animated sequences in selected images (based on file names) (optional)
- **use_placeholders** (bool) – Use Placeholders, Use placeholders for missing frames of the strip (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.change_scene"></a>

### bpy.ops.sequencer.change_scene(*, scene='')

Change Scene assigned to Strip

**Parameters:**

**scene** (str) – Scene, Scene to assign to the strip (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.connect"></a>

### bpy.ops.sequencer.connect(*, toggle=True)

Link selected strips together for simplified group selection

**Parameters:**

**toggle** (bool) – Toggle, Toggle strip connections (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.copy"></a>

### bpy.ops.sequencer.copy()

Copy the selected strips to the internal clipboard

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.crossfade_sounds"></a>

### bpy.ops.sequencer.crossfade_sounds()

Do cross-fading volume animation of two selected sound strips

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/sequencer.py:43](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/sequencer.py#L43)

<a id="bpy.ops.sequencer.cursor_set"></a>

### bpy.ops.sequencer.cursor_set(*, location=(0.0, 0.0))

Set 2D cursor location

**Parameters:**

**location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Cursor location in normalized preview coordinates (array of 2 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.deinterlace_selected_movies"></a>

### bpy.ops.sequencer.deinterlace_selected_movies()

Deinterlace all selected movie sources

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/sequencer.py:129](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/sequencer.py#L129)

<a id="bpy.ops.sequencer.delete"></a>

### bpy.ops.sequencer.delete(*, delete_data=False)

Delete selected strips from the sequencer

**Parameters:**

**delete_data** (bool) – Delete Data, After removing the Strip, delete the associated data also (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.disconnect"></a>

### bpy.ops.sequencer.disconnect()

Unlink selected strips so that they can be selected individually

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.duplicate"></a>

### bpy.ops.sequencer.duplicate(*, linked=False)

Duplicate the selected strips

**Parameters:**

**linked** (bool) – Linked, Duplicate strip but not strip data, linking to the original data (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.duplicate_move"></a>

### bpy.ops.sequencer.duplicate_move(*, SEQUENCER_OT_duplicate={}, TRANSFORM_OT_seq_slide={})

Duplicate selected strips and move them

**Parameters:**

- **SEQUENCER_OT_duplicate** (dict[str, Any]) – Duplicate Strips, Duplicate the selected strips (optional, [`bpy.ops.sequencer.duplicate()`](#bpy.ops.sequencer.duplicate "bpy.ops.sequencer.duplicate") keyword arguments)
- **TRANSFORM_OT_seq_slide** (dict[str, Any]) – Sequence Slide, Slide a sequence strip in time (optional, [`bpy.ops.transform.seq_slide()`](bpy.ops.transform.md#bpy.ops.transform.seq_slide "bpy.ops.transform.seq_slide") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.duplicate_move_linked"></a>

### bpy.ops.sequencer.duplicate_move_linked(*, SEQUENCER_OT_duplicate={}, TRANSFORM_OT_seq_slide={})

Duplicate selected strips, but not their data, and move them

**Parameters:**

- **SEQUENCER_OT_duplicate** (dict[str, Any]) – Duplicate Strips, Duplicate the selected strips (optional, [`bpy.ops.sequencer.duplicate()`](#bpy.ops.sequencer.duplicate "bpy.ops.sequencer.duplicate") keyword arguments)
- **TRANSFORM_OT_seq_slide** (dict[str, Any]) – Sequence Slide, Slide a sequence strip in time (optional, [`bpy.ops.transform.seq_slide()`](bpy.ops.transform.md#bpy.ops.transform.seq_slide "bpy.ops.transform.seq_slide") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.effect_strip_add"></a>

### bpy.ops.sequencer.effect_strip_add(*, type='CROSS', move_strips=True, frame_start=0, length=0, channel=1, replace_sel=True, overlap=False, overlap_shuffle_override=False, skip_locked_or_muted_channels=True, width=0, height=0, color=(0.0, 0.0, 0.0))

Add an effect to the sequencer, most are applied on top of existing strips

**Parameters:**

- **type** (Literal['CROSS', 'ADD', 'SUBTRACT', 'ALPHA_OVER', 'ALPHA_UNDER', 'GAMMA_CROSS', 'MULTIPLY', 'WIPE', 'GLOW', 'COLOR', 'SPEED', 'MULTICAM', 'ADJUSTMENT', 'GAUSSIAN_BLUR', 'TEXT', 'COLORMIX', 'COMPOSITOR']) –

  Type, Sequencer effect type (optional)

  - `CROSS`
    Crossfade – Fade out of one video, fading into another.
  - `ADD`
    Add – Add together color channels from two videos.
  - `SUBTRACT`
    Subtract – Subtract one strip’s color from another.
  - `ALPHA_OVER`
    Alpha Over – Blend alpha on top of another video.
  - `ALPHA_UNDER`
    Alpha Under – Blend alpha below another video.
  - `GAMMA_CROSS`
    Gamma Crossfade – Crossfade with color correction.
  - `MULTIPLY`
    Multiply – Multiply color channels from two videos.
  - `WIPE`
    Wipe – Sweep a transition line across the frame.
  - `GLOW`
    Glow – Add blur and brightness to light areas.
  - `COLOR`
    Color – Add a simple color strip.
  - `SPEED`
    Speed – Timewarp video strips, modifying playback speed.
  - `MULTICAM`
    Multicam Selector – Control active camera angles.
  - `ADJUSTMENT`
    Adjustment Layer – Apply nondestructive effects.
  - `GAUSSIAN_BLUR`
    Gaussian Blur – Soften details along axes.
  - `TEXT`
    Text – Add a simple text strip.
  - `COLORMIX`
    Color Mix – Combine two strips using blend modes.
  - `COMPOSITOR`
    Compositor – Compositor based effect.
- **move_strips** (bool) – Move Strips, Automatically begin translating strips with the mouse after adding them to the timeline (optional)
- **frame_start** (int) – Start Frame, Start frame of the strip (in [-inf, inf], optional)
- **length** (int) – Length, Length of the strip in frames, or the length of each strip if multiple are added (in [-inf, inf], optional)
- **channel** (int) – Channel, Channel to place this strip into (in [1, 128], optional)
- **replace_sel** (bool) – Replace Selection, Deselect previously selected strips after add operation completes (optional)
- **overlap** (bool) – Allow Overlap, Don’t correct overlap on new strips (optional)
- **overlap_shuffle_override** (bool) – Override Overlap Shuffle Behavior, Use the overlap_mode tool settings to determine how to shuffle overlapping strips (optional)
- **skip_locked_or_muted_channels** (bool) – Skip Locked/Muted Channels, Make strips occupy nearest unmuted and unlocked channels (optional)
- **width** (int) – Width, Width of the color strip in pixels (in [1, inf], optional)
- **height** (int) – Height, Height of the color strip in pixels (in [1, 32767], optional)
- **color** ([`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color") | Sequence[float]) – Color, Initialize the strip with this color (array of 3 items, in [0, 1], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.enable_proxies"></a>

### bpy.ops.sequencer.enable_proxies(*, proxy_25=False, proxy_50=False, proxy_75=False, proxy_100=False, overwrite=False)

Enable selected proxies on all selected Movie and Image strips

**Parameters:**

- **proxy_25** (bool) – 25%, Build proxy at 25% resolution (optional)
- **proxy_50** (bool) – 50%, Build proxy at 50% resolution (optional)
- **proxy_75** (bool) – 75%, Build proxy at 75% resolution (optional)
- **proxy_100** (bool) – 100%, Build proxy at 100% resolution (optional)
- **overwrite** (bool) – Overwrite, Overwrite existing proxy files (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.export_subtitles"></a>

### bpy.ops.sequencer.export_subtitles(*, filepath='', hide_props_region=True, check_existing=True, filter_blender=False, filter_backup=False, filter_image=False, filter_movie=False, filter_python=False, filter_font=False, filter_sound=False, filter_text=False, filter_archive=False, filter_btx=False, filter_alembic=False, filter_usd=False, filter_obj=False, filter_volume=False, filter_folder=True, filter_blenlib=False, filemode=8, display_type='DEFAULT', sort_method='')

Export .srt file containing text strips

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

<a id="bpy.ops.sequencer.fades_add"></a>

### bpy.ops.sequencer.fades_add(*, duration_seconds=1.0, type='IN_OUT')

Adds or updates a fade animation for either visual or audio strips

**Parameters:**

- **duration_seconds** (float) – Fade Duration, Duration of the fade in seconds (in [0.01, inf], optional)
- **type** (Literal['IN_OUT', 'IN', 'OUT', 'CURSOR_FROM', 'CURSOR_TO']) –

  Fade Type, Fade in, out, both in and out, to, or from the current frame. Default is both in and out (optional)

  - `IN_OUT`
    Fade In and Out – Fade selected strips in and out.
  - `IN`
    Fade In – Fade in selected strips.
  - `OUT`
    Fade Out – Fade out selected strips.
  - `CURSOR_FROM`
    From Current Frame – Fade from the time cursor to the end of overlapping strips.
  - `CURSOR_TO`
    To Current Frame – Fade from the start of strips under the time cursor to the current frame.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/sequencer.py:216](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/sequencer.py#L216)

<a id="bpy.ops.sequencer.fades_clear"></a>

### bpy.ops.sequencer.fades_clear()

Removes fade animation from selected strips

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/sequencer.py:152](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/sequencer.py#L152)

<a id="bpy.ops.sequencer.gap_insert"></a>

### bpy.ops.sequencer.gap_insert(*, frames=10)

Insert gap at current frame to first strips at the right, independent of selection or locked state of strips

**Parameters:**

**frames** (int) – Frames, Frames to insert after current strip (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.gap_remove"></a>

### bpy.ops.sequencer.gap_remove(*, all=False)

Remove gap at current frame to first strip at the right, independent of selection or locked state of strips

**Parameters:**

**all** (bool) – All Gaps, Do all gaps to right of current frame (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.image_strip_add"></a>

### bpy.ops.sequencer.image_strip_add(*, directory='', files=None, check_existing=False, filter_blender=False, filter_backup=False, filter_image=True, filter_movie=False, filter_python=False, filter_font=False, filter_sound=False, filter_text=False, filter_archive=False, filter_btx=False, filter_alembic=False, filter_usd=False, filter_obj=False, filter_volume=False, filter_folder=True, filter_blenlib=False, filemode=9, relative_path=True, show_multiview=False, use_multiview=False, display_type='DEFAULT', sort_method='', move_strips=True, frame_start=0, length=0, channel=1, replace_sel=True, overlap=False, overlap_shuffle_override=False, skip_locked_or_muted_channels=True, fit_method='FIT', set_view_transform=True, image_import_type='DETECT', use_sequence_detection=True, use_placeholders=False)

Add an image or image sequence to the sequencer

**Parameters:**

- **directory** (str) – Directory, Directory of the file (optional, never None)
- **files** (`bpy_prop_collection`[`OperatorFileListElement`] | None) – Files, (optional)
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
- **move_strips** (bool) – Move Strips, Automatically begin translating strips with the mouse after adding them to the timeline (optional)
- **frame_start** (int) – Start Frame, Start frame of the strip (in [-inf, inf], optional)
- **length** (int) – Length, Length of the strip in frames, or the length of each strip if multiple are added (in [-inf, inf], optional)
- **channel** (int) – Channel, Channel to place this strip into (in [1, 128], optional)
- **replace_sel** (bool) – Replace Selection, Deselect previously selected strips after add operation completes (optional)
- **overlap** (bool) – Allow Overlap, Don’t correct overlap on new strips (optional)
- **overlap_shuffle_override** (bool) – Override Overlap Shuffle Behavior, Use the overlap_mode tool settings to determine how to shuffle overlapping strips (optional)
- **skip_locked_or_muted_channels** (bool) – Skip Locked/Muted Channels, Make strips occupy nearest unmuted and unlocked channels (optional)
- **fit_method** (Literal[[Strip Scale Method Items](bpy_types_enum_items/strip_scale_method_items.md#rna-enum-strip-scale-method-items)]) – Fit Method, Mode for fitting the image to the canvas (optional)
- **set_view_transform** (bool) – Set View Transform, Set appropriate view transform based on media color space (optional)
- **image_import_type** (Literal['DETECT', 'SEQUENCE', 'INDIVIDUAL']) –

  Import As, Mode for importing selected images (optional)

  - `DETECT`
    Auto Detect – Add images as individual strips, unless their filenames match Blender’s numbered sequence pattern, in which case they are grouped into a single image sequence.
  - `SEQUENCE`
    Image Sequence – Import all selected images as a single image sequence. The sequence of images does not have to match Blender’s numbered sequence pattern, so placeholders cannot be inferred.
  - `INDIVIDUAL`
    Individual Images – Add each selected image as an individual strip.
- **use_sequence_detection** (bool) – Detect Sequences, Automatically detect animated sequences in selected images (based on file names) (optional)
- **use_placeholders** (bool) – Use Placeholders, Reserve placeholder frames for missing frames of the image sequence (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.images_separate"></a>

### bpy.ops.sequencer.images_separate(*, length=1)

On image sequence strips, it returns a strip for each image

**Parameters:**

**length** (int) – Length, Length of each frame (in [1, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.lock"></a>

### bpy.ops.sequencer.lock()

Lock strips so they cannot be transformed

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.mask_strip_add"></a>

### bpy.ops.sequencer.mask_strip_add(*, move_strips=True, frame_start=0, channel=1, replace_sel=True, overlap=False, overlap_shuffle_override=False, skip_locked_or_muted_channels=True, mask='')

Add a mask strip to the sequencer

**Parameters:**

- **move_strips** (bool) – Move Strips, Automatically begin translating strips with the mouse after adding them to the timeline (optional)
- **frame_start** (int) – Start Frame, Start frame of the strip (in [-inf, inf], optional)
- **channel** (int) – Channel, Channel to place this strip into (in [1, 128], optional)
- **replace_sel** (bool) – Replace Selection, Deselect previously selected strips after add operation completes (optional)
- **overlap** (bool) – Allow Overlap, Don’t correct overlap on new strips (optional)
- **overlap_shuffle_override** (bool) – Override Overlap Shuffle Behavior, Use the overlap_mode tool settings to determine how to shuffle overlapping strips (optional)
- **skip_locked_or_muted_channels** (bool) – Skip Locked/Muted Channels, Make strips occupy nearest unmuted and unlocked channels (optional)
- **mask** (str) – Mask, Mask to add as a strip (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.meta_make"></a>

### bpy.ops.sequencer.meta_make()

Group selected strips into a meta-strip

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.meta_separate"></a>

### bpy.ops.sequencer.meta_separate()

Put the contents of a meta-strip back in the sequencer

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.meta_toggle"></a>

### bpy.ops.sequencer.meta_toggle()

Toggle a meta-strip (to edit enclosed strips)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.movie_strip_add"></a>

### bpy.ops.sequencer.movie_strip_add(*, filepath='', directory='', files=None, check_existing=False, filter_blender=False, filter_backup=False, filter_image=False, filter_movie=True, filter_python=False, filter_font=False, filter_sound=False, filter_text=False, filter_archive=False, filter_btx=False, filter_alembic=False, filter_usd=False, filter_obj=False, filter_volume=False, filter_folder=True, filter_blenlib=False, filemode=9, relative_path=True, show_multiview=False, use_multiview=False, display_type='DEFAULT', sort_method='', move_strips=True, frame_start=0, channel=1, replace_sel=True, overlap=False, overlap_shuffle_override=False, skip_locked_or_muted_channels=True, fit_method='FIT', set_view_transform=True, adjust_playback_rate=True, sound=True, use_framerate=True)

Add a movie strip to the sequencer

**Parameters:**

- **filepath** (str) – File Path, Path to file (optional, never None)
- **directory** (str) – Directory, Directory of the file (optional, never None)
- **files** (`bpy_prop_collection`[`OperatorFileListElement`] | None) – Files, (optional)
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
- **move_strips** (bool) – Move Strips, Automatically begin translating strips with the mouse after adding them to the timeline (optional)
- **frame_start** (int) – Start Frame, Start frame of the strip (in [-inf, inf], optional)
- **channel** (int) – Channel, Channel to place this strip into (in [1, 128], optional)
- **replace_sel** (bool) – Replace Selection, Deselect previously selected strips after add operation completes (optional)
- **overlap** (bool) – Allow Overlap, Don’t correct overlap on new strips (optional)
- **overlap_shuffle_override** (bool) – Override Overlap Shuffle Behavior, Use the overlap_mode tool settings to determine how to shuffle overlapping strips (optional)
- **skip_locked_or_muted_channels** (bool) – Skip Locked/Muted Channels, Make strips occupy nearest unmuted and unlocked channels (optional)
- **fit_method** (Literal[[Strip Scale Method Items](bpy_types_enum_items/strip_scale_method_items.md#rna-enum-strip-scale-method-items)]) – Fit Method, Mode for fitting the image to the canvas (optional)
- **set_view_transform** (bool) – Set View Transform, Set appropriate view transform based on media color space (optional)
- **adjust_playback_rate** (bool) – Adjust Playback Rate, Play at normal speed regardless of scene FPS (optional)
- **sound** (bool) – Sound, Load sound with the movie (optional)
- **use_framerate** (bool) – Set Scene Frame Rate, Set frame rate of the current scene to the frame rate of the movie (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.movieclip_strip_add"></a>

### bpy.ops.sequencer.movieclip_strip_add(*, move_strips=True, frame_start=0, channel=1, replace_sel=True, overlap=False, overlap_shuffle_override=False, skip_locked_or_muted_channels=True, clip='')

Add a movieclip strip to the sequencer

**Parameters:**

- **move_strips** (bool) – Move Strips, Automatically begin translating strips with the mouse after adding them to the timeline (optional)
- **frame_start** (int) – Start Frame, Start frame of the strip (in [-inf, inf], optional)
- **channel** (int) – Channel, Channel to place this strip into (in [1, 128], optional)
- **replace_sel** (bool) – Replace Selection, Deselect previously selected strips after add operation completes (optional)
- **overlap** (bool) – Allow Overlap, Don’t correct overlap on new strips (optional)
- **overlap_shuffle_override** (bool) – Override Overlap Shuffle Behavior, Use the overlap_mode tool settings to determine how to shuffle overlapping strips (optional)
- **skip_locked_or_muted_channels** (bool) – Skip Locked/Muted Channels, Make strips occupy nearest unmuted and unlocked channels (optional)
- **clip** (str) – Clip, Movie clip to add as a strip (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.mute"></a>

### bpy.ops.sequencer.mute(*, unselected=False)

Mute (un)selected strips

**Parameters:**

**unselected** (bool) – Unselected, Mute unselected rather than selected strips (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.offset_clear"></a>

### bpy.ops.sequencer.offset_clear()

Clear strip in/out offsets from the start and end of content

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.paste"></a>

### bpy.ops.sequencer.paste(*, keep_offset=False, x=0, y=0)

Paste strips from the internal clipboard

**Parameters:**

- **keep_offset** (bool) – Keep Offset, Keep strip offset relative to the current frame when pasting (optional)
- **x** (int) – X, (in [-inf, inf], optional)
- **y** (int) – Y, (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.preview_duplicate_move"></a>

### bpy.ops.sequencer.preview_duplicate_move(*, SEQUENCER_OT_duplicate={}, TRANSFORM_OT_translate={})

Duplicate selected strips and move them

**Parameters:**

- **SEQUENCER_OT_duplicate** (dict[str, Any]) – Duplicate Strips, Duplicate the selected strips (optional, [`bpy.ops.sequencer.duplicate()`](#bpy.ops.sequencer.duplicate "bpy.ops.sequencer.duplicate") keyword arguments)
- **TRANSFORM_OT_translate** (dict[str, Any]) – Move, Move selected items (optional, [`bpy.ops.transform.translate()`](bpy.ops.transform.md#bpy.ops.transform.translate "bpy.ops.transform.translate") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.preview_duplicate_move_linked"></a>

### bpy.ops.sequencer.preview_duplicate_move_linked(*, SEQUENCER_OT_duplicate={}, TRANSFORM_OT_translate={})

Duplicate selected strips, but not their data, and move them

**Parameters:**

- **SEQUENCER_OT_duplicate** (dict[str, Any]) – Duplicate Strips, Duplicate the selected strips (optional, [`bpy.ops.sequencer.duplicate()`](#bpy.ops.sequencer.duplicate "bpy.ops.sequencer.duplicate") keyword arguments)
- **TRANSFORM_OT_translate** (dict[str, Any]) – Move, Move selected items (optional, [`bpy.ops.transform.translate()`](bpy.ops.transform.md#bpy.ops.transform.translate "bpy.ops.transform.translate") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.reassign_inputs"></a>

### bpy.ops.sequencer.reassign_inputs()

Reassign the inputs for the effect strip

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.rebuild_proxy"></a>

### bpy.ops.sequencer.rebuild_proxy()

Rebuild all selected proxies

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.refresh_all"></a>

### bpy.ops.sequencer.refresh_all()

Refresh the sequencer editor

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.reload"></a>

### bpy.ops.sequencer.reload(*, adjust_length=False)

Reload strips in the sequencer

**Parameters:**

**adjust_length** (bool) – Adjust Length, Adjust length of strips to their data length (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.rename_channel"></a>

### bpy.ops.sequencer.rename_channel()

Undocumented, consider [contributing](https://developer.blender.org/).

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.rendersize"></a>

### bpy.ops.sequencer.rendersize()

Set render size and aspect from active strip

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.retiming_add_freeze_frame_slide"></a>

### bpy.ops.sequencer.retiming_add_freeze_frame_slide(*, SEQUENCER_OT_retiming_freeze_frame_add={}, TRANSFORM_OT_seq_slide={})

Add freeze frame and move it

**Parameters:**

- **SEQUENCER_OT_retiming_freeze_frame_add** (dict[str, Any]) – Add Freeze Frame, Add freeze frame (optional, [`bpy.ops.sequencer.retiming_freeze_frame_add()`](#bpy.ops.sequencer.retiming_freeze_frame_add "bpy.ops.sequencer.retiming_freeze_frame_add") keyword arguments)
- **TRANSFORM_OT_seq_slide** (dict[str, Any]) – Sequence Slide, Slide a sequence strip in time (optional, [`bpy.ops.transform.seq_slide()`](bpy.ops.transform.md#bpy.ops.transform.seq_slide "bpy.ops.transform.seq_slide") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.retiming_add_transition_slide"></a>

### bpy.ops.sequencer.retiming_add_transition_slide(*, SEQUENCER_OT_retiming_transition_add={}, TRANSFORM_OT_seq_slide={})

Add smooth transition between 2 retimed segments and change its duration

**Parameters:**

- **SEQUENCER_OT_retiming_transition_add** (dict[str, Any]) – Add Speed Transition, Add smooth transition between 2 retimed segments (optional, [`bpy.ops.sequencer.retiming_transition_add()`](#bpy.ops.sequencer.retiming_transition_add "bpy.ops.sequencer.retiming_transition_add") keyword arguments)
- **TRANSFORM_OT_seq_slide** (dict[str, Any]) – Sequence Slide, Slide a sequence strip in time (optional, [`bpy.ops.transform.seq_slide()`](bpy.ops.transform.md#bpy.ops.transform.seq_slide "bpy.ops.transform.seq_slide") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.retiming_freeze_frame_add"></a>

### bpy.ops.sequencer.retiming_freeze_frame_add(*, duration=0)

Add freeze frame

**Parameters:**

**duration** (int) – Duration, Duration of freeze frame segment (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.retiming_key_add"></a>

### bpy.ops.sequencer.retiming_key_add(*, timeline_frame=0)

Add retiming Key

**Parameters:**

**timeline_frame** (int) – Timeline Frame, Frame where key will be added (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.retiming_key_delete"></a>

### bpy.ops.sequencer.retiming_key_delete()

Delete selected retiming keys from the sequencer

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.retiming_reset"></a>

### bpy.ops.sequencer.retiming_reset()

Reset strip retiming

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.retiming_segment_speed_set"></a>

### bpy.ops.sequencer.retiming_segment_speed_set(*, speed=100.0)

Set speed of retimed segment

**Parameters:**

**speed** (float) – Speed, New speed of retimed segment (in [0.001, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.retiming_show"></a>

### bpy.ops.sequencer.retiming_show()

Show retiming keys in selected strips

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.retiming_transition_add"></a>

### bpy.ops.sequencer.retiming_transition_add(*, duration=0)

Add smooth transition between 2 retimed segments

**Parameters:**

**duration** (int) – Duration, Duration of freeze frame segment (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.sample"></a>

### bpy.ops.sequencer.sample(*, size=1)

Use mouse to sample color in current frame

**Parameters:**

**size** (int) – Sample Size, (in [1, 128], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.scene_frame_range_update"></a>

### bpy.ops.sequencer.scene_frame_range_update()

Update frame range of scene strip

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.scene_strip_add"></a>

### bpy.ops.sequencer.scene_strip_add(*, move_strips=True, frame_start=0, channel=1, replace_sel=True, overlap=False, overlap_shuffle_override=False, skip_locked_or_muted_channels=True, scene='')

Add a strip re-using this scene as the source

**Parameters:**

- **move_strips** (bool) – Move Strips, Automatically begin translating strips with the mouse after adding them to the timeline (optional)
- **frame_start** (int) – Start Frame, Start frame of the strip (in [-inf, inf], optional)
- **channel** (int) – Channel, Channel to place this strip into (in [1, 128], optional)
- **replace_sel** (bool) – Replace Selection, Deselect previously selected strips after add operation completes (optional)
- **overlap** (bool) – Allow Overlap, Don’t correct overlap on new strips (optional)
- **overlap_shuffle_override** (bool) – Override Overlap Shuffle Behavior, Use the overlap_mode tool settings to determine how to shuffle overlapping strips (optional)
- **skip_locked_or_muted_channels** (bool) – Skip Locked/Muted Channels, Make strips occupy nearest unmuted and unlocked channels (optional)
- **scene** (str) – Scene, Scene to add as a strip (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.scene_strip_add_new"></a>

### bpy.ops.sequencer.scene_strip_add_new(*, move_strips=True, frame_start=0, channel=1, replace_sel=True, overlap=False, overlap_shuffle_override=False, skip_locked_or_muted_channels=True, type='NEW')

Add a strip using a new scene as the source

**Parameters:**

- **move_strips** (bool) – Move Strips, Automatically begin translating strips with the mouse after adding them to the timeline (optional)
- **frame_start** (int) – Start Frame, Start frame of the strip (in [-inf, inf], optional)
- **channel** (int) – Channel, Channel to place this strip into (in [1, 128], optional)
- **replace_sel** (bool) – Replace Selection, Deselect previously selected strips after add operation completes (optional)
- **overlap** (bool) – Allow Overlap, Don’t correct overlap on new strips (optional)
- **overlap_shuffle_override** (bool) – Override Overlap Shuffle Behavior, Use the overlap_mode tool settings to determine how to shuffle overlapping strips (optional)
- **skip_locked_or_muted_channels** (bool) – Skip Locked/Muted Channels, Make strips occupy nearest unmuted and unlocked channels (optional)
- **type** (Literal['NEW', 'EMPTY', 'LINK_COPY', 'FULL_COPY']) –

  Type, Method for creating the new scene (optional)

  - `NEW`
    New – Add new Strip with a new empty Scene with default settings.
  - `EMPTY`
    Copy Settings – Add a new Strip, with an empty scene, and copy settings from the current scene.
  - `LINK_COPY`
    Linked Copy – Add a Strip and link in the collections from the current scene (shallow copy).
  - `FULL_COPY`
    Full Copy – Add a Strip and make a full copy of the current scene.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.select"></a>

### bpy.ops.sequencer.select(*, wait_to_deselect_others=False, use_select_on_click=False, mouse_x=0, mouse_y=0, extend=False, deselect=False, toggle=False, deselect_all=False, select_passthrough=False, center=False, linked_handle=False, linked_time=False, side_of_frame=False, ignore_connections=False)

Select a strip (last selected becomes the “active strip”)

**Parameters:**

- **wait_to_deselect_others** (bool) – Wait to Deselect Others, (optional)
- **use_select_on_click** (bool) – Act on Click, Instead of selecting on mouse press, wait to see if there’s drag event. Otherwise select on mouse release (optional)
- **mouse_x** (int) – Mouse X, (in [-inf, inf], optional)
- **mouse_y** (int) – Mouse Y, (in [-inf, inf], optional)
- **extend** (bool) – Extend, Extend selection instead of deselecting everything first (optional)
- **deselect** (bool) – Deselect, Remove from selection (optional)
- **toggle** (bool) – Toggle Selection, Toggle the selection (optional)
- **deselect_all** (bool) – Deselect On Nothing, Deselect all when nothing under the cursor (optional)
- **select_passthrough** (bool) – Only Select Unselected, Ignore the select action when the element is already selected (optional)
- **center** (bool) – Center, Use the object center when selecting, in edit mode used to extend object selection (optional)
- **linked_handle** (bool) – Linked Handle, Select handles next to the active strip (optional)
- **linked_time** (bool) – Linked Time, Select other strips or handles at the same time, or all retiming keys after the current in retiming mode (optional)
- **side_of_frame** (bool) – Side of Frame, Select all strips on same side of the current frame as the mouse cursor (optional)
- **ignore_connections** (bool) – Ignore Connections, Select strips individually whether or not they are connected (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.select_all"></a>

### bpy.ops.sequencer.select_all(*, action='TOGGLE')

Select or deselect all strips

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

<a id="bpy.ops.sequencer.select_box"></a>

### bpy.ops.sequencer.select_box(*, xmin=0, xmax=0, ymin=0, ymax=0, wait_for_input=True, mode='SET', tweak=False, include_handles=False, ignore_connections=False)

Select strips using box selection

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
- **tweak** (bool) – Tweak, Make box select pass through to sequence slide when the cursor is hovering on a strip (optional)
- **include_handles** (bool) – Select Handles, Select the strips and their handles (optional)
- **ignore_connections** (bool) – Ignore Connections, Select strips individually whether or not they are connected (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.select_circle"></a>

### bpy.ops.sequencer.select_circle(*, x=0, y=0, radius=25, wait_for_input=True, mode='SET', ignore_connections=False)

Select strips using circle selection

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
- **ignore_connections** (bool) – Ignore Connections, Select strips individually whether or not they are connected (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.select_grouped"></a>

### bpy.ops.sequencer.select_grouped(*, type='TYPE', extend=False, use_active_channel=False)

Select all strips grouped by various properties

**Parameters:**

- **type** (Literal['TYPE', 'TYPE_BASIC', 'TYPE_EFFECT', 'DATA', 'EFFECT', 'EFFECT_LINK', 'OVERLAP']) –

  Type, (optional)

  - `TYPE`
    Type – Shared strip type.
  - `TYPE_BASIC`
    Global Type – All strips of same basic type (graphical or sound).
  - `TYPE_EFFECT`
    Effect Type – Shared strip effect type (if active strip is not an effect one, select all non-effect strips).
  - `DATA`
    Data – Shared data (scene, image, sound, etc.).
  - `EFFECT`
    Effect – Shared effects.
  - `EFFECT_LINK`
    Effect/Linked – Other strips affected by the active one (sharing some time, and below or effect-assigned).
  - `OVERLAP`
    Overlap – Overlapping time.
- **extend** (bool) – Extend, Extend selection instead of deselecting everything first (optional)
- **use_active_channel** (bool) – Same Channel, Only consider strips on the same channel as the active one (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.select_handle"></a>

### bpy.ops.sequencer.select_handle(*, wait_to_deselect_others=False, use_select_on_click=False, mouse_x=0, mouse_y=0, ignore_connections=False)

Select strip handle

**Parameters:**

- **wait_to_deselect_others** (bool) – Wait to Deselect Others, (optional)
- **use_select_on_click** (bool) – Act on Click, Instead of selecting on mouse press, wait to see if there’s drag event. Otherwise select on mouse release (optional)
- **mouse_x** (int) – Mouse X, (in [-inf, inf], optional)
- **mouse_y** (int) – Mouse Y, (in [-inf, inf], optional)
- **ignore_connections** (bool) – Ignore Connections, Select strips individually whether or not they are connected (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.select_handles"></a>

### bpy.ops.sequencer.select_handles(*, side='BOTH')

Select gizmo handles on the sides of the selected strip

**Parameters:**

**side** (Literal['LEFT', 'RIGHT', 'BOTH', 'LEFT_NEIGHBOR', 'RIGHT_NEIGHBOR', 'BOTH_NEIGHBORS']) – Side, The side of the handle that is selected (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.select_lasso"></a>

### bpy.ops.sequencer.select_lasso(*, path=None, use_smooth_stroke=False, smooth_stroke_factor=0.75, smooth_stroke_radius=35, mode='SET')

Select strips using lasso selection

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

<a id="bpy.ops.sequencer.select_less"></a>

### bpy.ops.sequencer.select_less()

Shrink the current selection of adjacent selected strips

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.select_linked"></a>

### bpy.ops.sequencer.select_linked()

Select all strips adjacent to the current selection

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.select_linked_pick"></a>

### bpy.ops.sequencer.select_linked_pick(*, extend=False)

Select a chain of linked strips nearest to the mouse pointer

**Parameters:**

**extend** (bool) – Extend, Extend the selection (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.select_more"></a>

### bpy.ops.sequencer.select_more()

Select more strips adjacent to the current selection

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.select_side"></a>

### bpy.ops.sequencer.select_side(*, side='BOTH')

Select strips on the nominated side of the selected strips

**Parameters:**

**side** (Literal['MOUSE', 'LEFT', 'RIGHT', 'BOTH', 'NO_CHANGE']) – Side, The side to which the selection is applied (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.select_side_of_frame"></a>

### bpy.ops.sequencer.select_side_of_frame(*, extend=False, side='LEFT')

Select strips relative to the current frame

**Parameters:**

- **extend** (bool) – Extend, Extend the selection (optional)
- **side** (Literal['LEFT', 'RIGHT', 'CURRENT']) –

  Side, Whether to select all strips to the left or right of the current frame, or just those intersecting with it (optional)

  - `LEFT`
    Left – Select to the left of the current frame.
  - `RIGHT`
    Right – Select to the right of the current frame.
  - `CURRENT`
    Current Frame – Select intersecting with the current frame.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.set_range_to_strips"></a>

### bpy.ops.sequencer.set_range_to_strips(*, preview=False)

Set the frame range to the selected strips start and end

**Parameters:**

**preview** (bool) – Preview, Set the preview range instead (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.slip"></a>

### bpy.ops.sequencer.slip(*, offset=0.0, slip_keyframes=False, use_cursor_position=False, ignore_connections=False)

Slip the contents of selected strips

**Parameters:**

- **offset** (float) – Offset, Offset to the data of the strip (in [-inf, inf], optional)
- **slip_keyframes** (bool) – Slip Keyframes, Move the keyframes alongside the media (optional)
- **use_cursor_position** (bool) – Use Cursor Position, Slip strips under mouse cursor instead of all selected strips (optional)
- **ignore_connections** (bool) – Ignore Connections, Do not slip connected strips if using cursor position (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.snap"></a>

### bpy.ops.sequencer.snap(*, frame=0, side='LEFT', keep_offset=True)

Snap strips to the current frame, using the active (or closest) strip as the anchor, and the mouse cursor relative to the playhead to determine the side of the playhead to snap to

**Parameters:**

- **frame** (int) – Frame, Frame where selected strips will be snapped (in [-inf, inf], optional)
- **side** (Literal['LEFT', 'RIGHT']) – Snap Side, Which side of the playhead strips should snap to when no handles are selected (optional)
- **keep_offset** (bool) – Keep Offset, Whether the selection should be snapped as a whole or by each individual strip (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.sound_strip_add"></a>

### bpy.ops.sequencer.sound_strip_add(*, filepath='', directory='', files=None, check_existing=False, filter_blender=False, filter_backup=False, filter_image=False, filter_movie=False, filter_python=False, filter_font=False, filter_sound=True, filter_text=False, filter_archive=False, filter_btx=False, filter_alembic=False, filter_usd=False, filter_obj=False, filter_volume=False, filter_folder=True, filter_blenlib=False, filemode=9, relative_path=True, display_type='DEFAULT', sort_method='', move_strips=True, frame_start=0, channel=1, replace_sel=True, overlap=False, overlap_shuffle_override=False, skip_locked_or_muted_channels=True, cache=False, mono=False)

Add a sound strip to the sequencer

**Parameters:**

- **filepath** (str) – File Path, Path to file (optional, never None)
- **directory** (str) – Directory, Directory of the file (optional, never None)
- **files** (`bpy_prop_collection`[`OperatorFileListElement`] | None) – Files, (optional)
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
- **move_strips** (bool) – Move Strips, Automatically begin translating strips with the mouse after adding them to the timeline (optional)
- **frame_start** (int) – Start Frame, Start frame of the strip (in [-inf, inf], optional)
- **channel** (int) – Channel, Channel to place this strip into (in [1, 128], optional)
- **replace_sel** (bool) – Replace Selection, Deselect previously selected strips after add operation completes (optional)
- **overlap** (bool) – Allow Overlap, Don’t correct overlap on new strips (optional)
- **overlap_shuffle_override** (bool) – Override Overlap Shuffle Behavior, Use the overlap_mode tool settings to determine how to shuffle overlapping strips (optional)
- **skip_locked_or_muted_channels** (bool) – Skip Locked/Muted Channels, Make strips occupy nearest unmuted and unlocked channels (optional)
- **cache** (bool) – Cache, Cache the sound in memory (optional)
- **mono** (bool) – Mono, Merge all the sound’s channels into one (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.split"></a>

### bpy.ops.sequencer.split(*, frame=0, channel=0, type='SOFT', use_cursor_position=False, side='MOUSE', ignore_selection=False, ignore_connections=False)

Split the selected strips in two

**Parameters:**

- **frame** (int) – Frame, Frame where selected strips will be split (in [-inf, inf], optional)
- **channel** (int) – Channel, Channel in which strip will be cut (in [-inf, inf], optional)
- **type** (Literal['SOFT', 'HARD']) – Type, The type of split operation to perform on strips (optional)
- **use_cursor_position** (bool) – Use Cursor Position, Split at position of the cursor instead of current frame (optional)
- **side** (Literal['MOUSE', 'LEFT', 'RIGHT', 'BOTH', 'NO_CHANGE']) – Side, The side that remains selected after splitting (optional)
- **ignore_selection** (bool) – Ignore Selection, Make cut even if strip is not selected preserving selection state after cut (optional)
- **ignore_connections** (bool) – Ignore Connections, Don’t propagate split to connected strips (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.split_multicam"></a>

### bpy.ops.sequencer.split_multicam(*, camera=1)

Split multicam strip and select camera

**Parameters:**

**camera** (int) – Camera, (in [1, 32], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/sequencer.py:96](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/sequencer.py#L96)

<a id="bpy.ops.sequencer.strip_color_tag_set"></a>

### bpy.ops.sequencer.strip_color_tag_set(*, color='NONE')

Set a color tag for the selected strips

**Parameters:**

**color** (Literal[[Strip Color Items](bpy_types_enum_items/strip_color_items.md#rna-enum-strip-color-items)]) – Color Tag, Color used to tag strips for organizing them in the timeline (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.strip_jump"></a>

### bpy.ops.sequencer.strip_jump(*, next=True, center=True)

Move playhead to the next or previous edit point, which may be a strip handle or its center

**Parameters:**

- **next** (bool) – Next Strip, Jump to the next handle or center, else the previous (optional)
- **center** (bool) – Use Strip Center, Jump to the center of the strip rather than its handles (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.strip_modifier_add"></a>

### bpy.ops.sequencer.strip_modifier_add(*, type='')

Add a modifier to the strip

**Parameters:**

**type** (str) – Type, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.strip_modifier_add_node_group"></a>

### bpy.ops.sequencer.strip_modifier_add_node_group(*, asset_library_type='LOCAL', asset_library_identifier='', relative_asset_identifier='', session_uid=0)

Add a modifier to the strip

**Parameters:**

- **asset_library_type** (Literal[[Asset Library Type Items](bpy_types_enum_items/asset_library_type_items.md#rna-enum-asset-library-type-items)]) – Asset Library Type, (optional)
- **asset_library_identifier** (str) – Asset Library Identifier, (optional, never None)
- **relative_asset_identifier** (str) – Relative Asset Identifier, (optional, never None)
- **session_uid** (int) – Session UID, Session UID of the data-block to use by the operator (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.strip_modifier_copy"></a>

### bpy.ops.sequencer.strip_modifier_copy(*, type='REPLACE', modifier='')

Copy modifiers of the active strip to all selected strips

**Parameters:**

- **type** (Literal['REPLACE', 'APPEND']) –

  Type, Whether to replace all modifiers on the selected strips or append to their existing modifier stack (optional)

  - `REPLACE`
    Replace – Replace modifiers in destination.
  - `APPEND`
    Append – Append active modifiers to selected strips.
- **modifier** (str) – Modifier, Name of the modifier to copy. If empty, copy all modifiers (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.strip_modifier_duplicate"></a>

### bpy.ops.sequencer.strip_modifier_duplicate(*, modifier='')

Duplicate (active) modifier of the active strip

**Parameters:**

**modifier** (str) – Modifier, Name of the modifier to duplicate. If empty duplicate the active modifier (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.strip_modifier_equalizer_redefine"></a>

### bpy.ops.sequencer.strip_modifier_equalizer_redefine(*, graphs='SIMPLE', name='Name')

Redefine equalizer graphs

**Parameters:**

- **graphs** (Literal['SIMPLE', 'DOUBLE', 'TRIPLE']) –

  Graphs, Number of graphs (optional)

  - `SIMPLE`
    Unique – One unique graphical definition.
  - `DOUBLE`
    Double – Graphical definition in 2 sections.
  - `TRIPLE`
    Triplet – Graphical definition in 3 sections.
- **name** (str) – Name, Name of modifier to redefine (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.strip_modifier_move"></a>

### bpy.ops.sequencer.strip_modifier_move(*, name='Name', direction='UP')

Move modifier up and down in the stack

**Parameters:**

- **name** (str) – Name, Name of modifier to remove (optional, never None)
- **direction** (Literal['UP', 'DOWN']) –

  Type, (optional)

  - `UP`
    Up – Move modifier up in the stack.
  - `DOWN`
    Down – Move modifier down in the stack.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.strip_modifier_move_to_index"></a>

### bpy.ops.sequencer.strip_modifier_move_to_index(*, modifier='', index=0)

Change the strip modifier’s index in the stack so it evaluates after the set number of others

**Parameters:**

- **modifier** (str) – Modifier, Name of the modifier to edit (optional, never None)
- **index** (int) – Index, The index to move the modifier to (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.strip_modifier_remove"></a>

### bpy.ops.sequencer.strip_modifier_remove(*, name='Name')

Remove a modifier from the strip

**Parameters:**

**name** (str) – Name, Name of modifier to remove (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.strip_modifier_set_active"></a>

### bpy.ops.sequencer.strip_modifier_set_active(*, modifier='')

Activate the strip modifier to use as the context

**Parameters:**

**modifier** (str) – Modifier, Name of the strip modifier to edit (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.strip_transform_clear"></a>

### bpy.ops.sequencer.strip_transform_clear(*, property='ALL')

Reset image transformation to default value

**Parameters:**

**property** (Literal['POSITION', 'SCALE', 'ROTATION', 'ALL']) –

Property, Strip transform property to be reset (optional)

- `POSITION`
  Position – Reset strip transform location.
- `SCALE`
  Scale – Reset strip transform scale.
- `ROTATION`
  Rotation – Reset strip transform rotation.
- `ALL`
  All – Reset strip transform location, scale and rotation.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.strip_transform_fit"></a>

### bpy.ops.sequencer.strip_transform_fit(*, fit_method='FIT')

Undocumented, consider [contributing](https://developer.blender.org/).

**Parameters:**

**fit_method** (Literal[[Strip Scale Method Items](bpy_types_enum_items/strip_scale_method_items.md#rna-enum-strip-scale-method-items)]) – Fit Method, Mode for fitting the image to the canvas (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.swap"></a>

### bpy.ops.sequencer.swap(*, side='RIGHT')

Swap active strip with strip to the right or left

**Parameters:**

**side** (Literal['LEFT', 'RIGHT']) – Side, Side of the strip to swap (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.swap_data"></a>

### bpy.ops.sequencer.swap_data()

Swap 2 sequencer strips

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.swap_inputs"></a>

### bpy.ops.sequencer.swap_inputs()

Swap the two inputs of the effect strip

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.text_cursor_move"></a>

### bpy.ops.sequencer.text_cursor_move(*, type='LINE_BEGIN', select_text=False)

Move cursor in text

**Parameters:**

- **type** (Literal['LINE_BEGIN', 'LINE_END', 'TEXT_BEGIN', 'TEXT_END', 'PREVIOUS_CHARACTER', 'NEXT_CHARACTER', 'PREVIOUS_WORD', 'NEXT_WORD', 'PREVIOUS_LINE', 'NEXT_LINE']) – Type, Where to move cursor to, to make a selection (optional)
- **select_text** (bool) – Select Text, Select text while moving cursor (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.text_cursor_set"></a>

### bpy.ops.sequencer.text_cursor_set(*, select_text=False)

Set cursor position in text

**Parameters:**

**select_text** (bool) – Select Text, Select text while moving cursor (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.text_delete"></a>

### bpy.ops.sequencer.text_delete(*, type='NEXT_OR_SELECTION')

Delete text at cursor position

**Parameters:**

**type** (Literal['NEXT_OR_SELECTION', 'PREVIOUS_OR_SELECTION']) – Type, Which part of the text to delete (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.text_deselect_all"></a>

### bpy.ops.sequencer.text_deselect_all()

Deselect all characters

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.text_edit_copy"></a>

### bpy.ops.sequencer.text_edit_copy()

Copy text to clipboard

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.text_edit_cut"></a>

### bpy.ops.sequencer.text_edit_cut()

Cut text to clipboard

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.text_edit_mode_toggle"></a>

### bpy.ops.sequencer.text_edit_mode_toggle()

Toggle text editing

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.text_edit_paste"></a>

### bpy.ops.sequencer.text_edit_paste()

Paste text from clipboard

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.text_insert"></a>

### bpy.ops.sequencer.text_insert(*, string='')

Insert text at cursor position

**Parameters:**

**string** (str) – String, String to be inserted at cursor position (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.text_line_break"></a>

### bpy.ops.sequencer.text_line_break()

Insert line break at cursor position

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.text_select_all"></a>

### bpy.ops.sequencer.text_select_all()

Select all characters

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.text_strip_style_preset_add"></a>

### bpy.ops.sequencer.text_strip_style_preset_add(*, name='', remove_name=False, remove_active=False)

Add or remove a text strip style and layout preset

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

<a id="bpy.ops.sequencer.unlock"></a>

### bpy.ops.sequencer.unlock()

Unlock strips so they can be transformed

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.unmute"></a>

### bpy.ops.sequencer.unmute(*, unselected=False)

Unmute (un)selected strips

**Parameters:**

**unselected** (bool) – Unselected, Unmute unselected rather than selected strips (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.view_all"></a>

### bpy.ops.sequencer.view_all()

View all the strips in the sequencer

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.view_all_preview"></a>

### bpy.ops.sequencer.view_all_preview()

Zoom preview to fit in the area

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.view_frame"></a>

### bpy.ops.sequencer.view_frame()

Move the view to the current frame

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.view_ghost_border"></a>

### bpy.ops.sequencer.view_ghost_border(*, xmin=0, xmax=0, ymin=0, ymax=0, wait_for_input=True)

Set the boundaries of the border used for offset view

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

<a id="bpy.ops.sequencer.view_selected"></a>

### bpy.ops.sequencer.view_selected()

Zoom the sequencer on the selected strips

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sequencer.view_zoom_ratio"></a>

### bpy.ops.sequencer.view_zoom_ratio(*, ratio=1.0)

Change zoom ratio of sequencer preview

**Parameters:**

**ratio** (float) – Ratio, Zoom ratio, 1.0 is 1:1, higher is zoomed in, lower is zoomed out (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]
