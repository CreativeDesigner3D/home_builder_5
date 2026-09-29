<!-- source: Blender Python API reference 5.2 / bpy.ops.file.html -->

<a id="module-bpy.ops.file"></a>

# File Operators

<a id="bpy.ops.file.autopack_toggle"></a>

### bpy.ops.file.autopack_toggle()

Automatically pack all external files into the .blend file

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.file.bookmark_add"></a>

### bpy.ops.file.bookmark_add()

Add a bookmark for the selected/active directory

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.file.bookmark_cleanup"></a>

### bpy.ops.file.bookmark_cleanup()

Delete all invalid bookmarks

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.file.bookmark_delete"></a>

### bpy.ops.file.bookmark_delete(*, index=-1)

Delete selected bookmark

**Parameters:**

**index** (int) – Index, (in [-1, 20000], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.file.bookmark_move"></a>

### bpy.ops.file.bookmark_move(*, direction='TOP')

Move the active bookmark up/down in the list

**Parameters:**

**direction** (Literal['TOP', 'UP', 'DOWN', 'BOTTOM']) –

Direction, Direction to move the active bookmark towards (optional)

- `TOP`
  Top – Top of the list.
- `UP`
  Up.
- `DOWN`
  Down.
- `BOTTOM`
  Bottom – Bottom of the list.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.file.cancel"></a>

### bpy.ops.file.cancel()

Cancel file operation

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.file.delete"></a>

### bpy.ops.file.delete()

Move selected files to the trash or recycle bin

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.file.directory_new"></a>

### bpy.ops.file.directory_new(*, directory='', open=False, confirm=True)

Create a new directory

**Parameters:**

- **directory** (str) – Directory, Name of new directory (optional, never None)
- **open** (bool) – Open, Open new directory (optional)
- **confirm** (bool) – Confirm, Prompt for confirmation (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.file.edit_directory_path"></a>

### bpy.ops.file.edit_directory_path()

Start editing directory field

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.file.execute"></a>

### bpy.ops.file.execute()

Execute selected file

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.file.external_operation"></a>

### bpy.ops.file.external_operation(*, operation='OPEN')

Perform external operation on a file or folder

**Parameters:**

**operation** (Literal['OPEN', 'FOLDER_OPEN', 'EDIT', 'NEW', 'FIND', 'SHOW', 'PLAY', 'BROWSE', 'PREVIEW', 'PRINT', 'INSTALL', 'RUNAS', 'PROPERTIES', 'FOLDER_FIND', 'CMD']) –

Operation, Operation to perform on the selected file or path (optional)

- `OPEN`
  Open – Open the file.
- `FOLDER_OPEN`
  Open Folder – Open the folder.
- `EDIT`
  Edit – Edit the file.
- `NEW`
  New – Create a new file of this type.
- `FIND`
  Find File – Search for files of this type.
- `SHOW`
  Show – Show this file.
- `PLAY`
  Play – Play this file.
- `BROWSE`
  Browse – Browse this file.
- `PREVIEW`
  Preview – Preview this file.
- `PRINT`
  Print – Print this file.
- `INSTALL`
  Install – Install this file.
- `RUNAS`
  Run As User – Run as specific user.
- `PROPERTIES`
  Properties – Show OS Properties for this item.
- `FOLDER_FIND`
  Find in Folder – Search for items in this folder.
- `CMD`
  Command Prompt Here – Open a command prompt here.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.file.filenum"></a>

### bpy.ops.file.filenum(*, increment=1)

Increment number in filename

**Parameters:**

**increment** (int) – Increment, (in [-100, 100], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.file.filepath_drop"></a>

### bpy.ops.file.filepath_drop(*, filepath='Path')

Undocumented, consider [contributing](https://developer.blender.org/).

**Parameters:**

**filepath** (str) – (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.file.find_missing_files"></a>

### bpy.ops.file.find_missing_files(*, find_all=False, directory='', hide_props_region=True, check_existing=False, filter_blender=False, filter_backup=False, filter_image=False, filter_movie=False, filter_python=False, filter_font=False, filter_sound=False, filter_text=False, filter_archive=False, filter_btx=False, filter_alembic=False, filter_usd=False, filter_obj=False, filter_volume=False, filter_folder=False, filter_blenlib=False, filemode=9, display_type='DEFAULT', sort_method='')

Try to find missing external files

**Parameters:**

- **find_all** (bool) – Find All, Find all files in the search path (not just missing) (optional)
- **directory** (str) – Directory, Directory of the file (optional, never None)
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

<a id="bpy.ops.file.hidedot"></a>

### bpy.ops.file.hidedot()

Toggle hide hidden dot files

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.file.highlight"></a>

### bpy.ops.file.highlight()

Highlight selected file(s)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.file.make_paths_absolute"></a>

### bpy.ops.file.make_paths_absolute()

Make all paths to external files absolute

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.file.make_paths_relative"></a>

### bpy.ops.file.make_paths_relative()

Make all paths to external files relative to current .blend

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.file.mouse_execute"></a>

### bpy.ops.file.mouse_execute()

Perform the current execute action for the file under the cursor (e.g. open the file)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.file.next"></a>

### bpy.ops.file.next()

Move to next folder

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.file.pack_all"></a>

### bpy.ops.file.pack_all()

Pack all used external files into this .blend

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.file.pack_libraries"></a>

### bpy.ops.file.pack_libraries()

Store all data-blocks linked from other .blend files in the current .blend file. Library references are preserved so the linked data-blocks can be unpacked again

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.file.parent"></a>

### bpy.ops.file.parent()

Move to parent directory

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.file.previous"></a>

### bpy.ops.file.previous()

Move to previous folder

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.file.refresh"></a>

### bpy.ops.file.refresh()

Refresh the file list

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.file.rename"></a>

### bpy.ops.file.rename()

Rename file or file directory

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.file.report_missing_files"></a>

### bpy.ops.file.report_missing_files()

Report all missing external files

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.file.reset_recent"></a>

### bpy.ops.file.reset_recent()

Reset recent files

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.file.select"></a>

### bpy.ops.file.select(*, wait_to_deselect_others=False, use_select_on_click=False, mouse_x=0, mouse_y=0, extend=False, fill=False, open=True, deselect_all=False, only_activate_if_selected=False, pass_through=False)

Handle mouse clicks to select and activate items

**Parameters:**

- **wait_to_deselect_others** (bool) – Wait to Deselect Others, (optional)
- **use_select_on_click** (bool) – Act on Click, Instead of selecting on mouse press, wait to see if there’s drag event. Otherwise select on mouse release (optional)
- **mouse_x** (int) – Mouse X, (in [-inf, inf], optional)
- **mouse_y** (int) – Mouse Y, (in [-inf, inf], optional)
- **extend** (bool) – Extend, Extend selection instead of deselecting everything first (optional)
- **fill** (bool) – Fill, Select everything beginning with the last selection (optional)
- **open** (bool) – Open, Open a directory when selecting it (optional)
- **deselect_all** (bool) – Deselect On Nothing, Deselect all when nothing under the cursor (optional)
- **only_activate_if_selected** (bool) – Only Activate if Selected, Do not change selection if the item under the cursor is already selected, only activate it (optional)
- **pass_through** (bool) – Pass Through, Even on successful execution, pass the event on so other operators can execute on it as well (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.file.select_all"></a>

### bpy.ops.file.select_all(*, action='TOGGLE')

Select or deselect all files

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

<a id="bpy.ops.file.select_bookmark"></a>

### bpy.ops.file.select_bookmark(*, dir='')

Select a bookmarked directory

**Parameters:**

**dir** (str) – Directory, (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.file.select_box"></a>

### bpy.ops.file.select_box(*, xmin=0, xmax=0, ymin=0, ymax=0, wait_for_input=True, mode='SET')

Activate/select the file(s) contained in the border

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

<a id="bpy.ops.file.select_walk"></a>

### bpy.ops.file.select_walk(*, direction='UP', extend=False, fill=False)

Select/Deselect files by walking through them

**Parameters:**

- **direction** (Literal['UP', 'DOWN', 'LEFT', 'RIGHT']) – Walk Direction, Select/Deselect element in this direction (optional)
- **extend** (bool) – Extend, Extend selection instead of deselecting everything first (optional)
- **fill** (bool) – Fill, Select everything beginning with the last selection (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.file.smoothscroll"></a>

### bpy.ops.file.smoothscroll()

Smooth scroll to make editable file visible

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.file.sort_column_ui_context"></a>

### bpy.ops.file.sort_column_ui_context()

Change sorting to use column under cursor

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.file.start_filter"></a>

### bpy.ops.file.start_filter()

Start entering filter text

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.file.unpack_all"></a>

### bpy.ops.file.unpack_all(*, method='USE_LOCAL')

Unpack all files packed into this .blend to external ones

**Parameters:**

**method** (Literal['USE_LOCAL', 'WRITE_LOCAL', 'USE_ORIGINAL', 'WRITE_ORIGINAL', 'KEEP', 'REMOVE']) – Method, How to unpack (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.file.unpack_item"></a>

### bpy.ops.file.unpack_item(*, method='USE_LOCAL', id_name='', id_type=19785)

Unpack this file to an external file

**Parameters:**

- **method** (Literal['USE_LOCAL', 'WRITE_LOCAL', 'USE_ORIGINAL', 'WRITE_ORIGINAL']) – Method, How to unpack (optional)
- **id_name** (str) – ID Name, Name of ID block to unpack (optional, never None)
- **id_type** (int) – ID Type, Identifier type of ID block (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.file.unpack_libraries"></a>

### bpy.ops.file.unpack_libraries()

Restore all packed linked data-blocks to their original locations

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.file.view_selected"></a>

### bpy.ops.file.view_selected()

Scroll the selected files into view

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]
