<!-- source: Blender Python API reference 5.2 / bpy.ops.text.html -->

<a id="module-bpy.ops.text"></a>

# Text Operators

<a id="bpy.ops.text.autocomplete"></a>

### bpy.ops.text.autocomplete()

Show a list of used text in the open document

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.text.comment_toggle"></a>

### bpy.ops.text.comment_toggle(*, type='TOGGLE')

Undocumented, consider [contributing](https://developer.blender.org/).

**Parameters:**

**type** (Literal['TOGGLE', 'COMMENT', 'UNCOMMENT']) – Type, Add or remove comments (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.text.convert_whitespace"></a>

### bpy.ops.text.convert_whitespace(*, type='SPACES')

Convert whitespaces by type

**Parameters:**

**type** (Literal['SPACES', 'TABS']) – Type, Type of whitespace to convert to (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.text.copy"></a>

### bpy.ops.text.copy()

Copy selected text to clipboard

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.text.cursor_set"></a>

### bpy.ops.text.cursor_set(*, x=0, y=0)

Set cursor position

**Parameters:**

- **x** (int) – X, (in [-inf, inf], optional)
- **y** (int) – Y, (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.text.cut"></a>

### bpy.ops.text.cut()

Cut selected text to clipboard

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.text.delete"></a>

### bpy.ops.text.delete(*, type='NEXT_CHARACTER')

Delete text by cursor position

**Parameters:**

**type** (Literal['NEXT_CHARACTER', 'PREVIOUS_CHARACTER', 'NEXT_WORD', 'PREVIOUS_WORD']) – Type, Which part of the text to delete (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.text.duplicate_line"></a>

### bpy.ops.text.duplicate_line()

Duplicate the current line

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.text.find"></a>

### bpy.ops.text.find()

Find specified text

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.text.find_set_selected"></a>

### bpy.ops.text.find_set_selected()

Find specified text and set as selected

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.text.indent"></a>

### bpy.ops.text.indent()

Indent selected text

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.text.indent_or_autocomplete"></a>

### bpy.ops.text.indent_or_autocomplete()

Indent selected text or autocomplete

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.text.insert"></a>

### bpy.ops.text.insert(*, text='')

Insert text at cursor position

**Parameters:**

**text** (str) – Text, Text to insert at the cursor position (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.text.jump"></a>

### bpy.ops.text.jump(*, line=1)

Jump cursor to line

**Parameters:**

**line** (int) – Line, Line number to jump to (in [1, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.text.jump_to_file_at_point"></a>

### bpy.ops.text.jump_to_file_at_point(*, filepath='', line=0, column=0)

Jump to a file for the text editor

**Parameters:**

- **filepath** (str) – Filepath, (optional, never None)
- **line** (int) – Line, Line to jump to (in [0, inf], optional)
- **column** (int) – Column, Column to jump to (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.text.line_break"></a>

### bpy.ops.text.line_break()

Insert line break at cursor position

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.text.line_number"></a>

### bpy.ops.text.line_number()

The current line number

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.text.make_internal"></a>

### bpy.ops.text.make_internal()

Make active text file internal

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.text.move"></a>

### bpy.ops.text.move(*, type='LINE_BEGIN')

Move cursor to position type

**Parameters:**

**type** (Literal['LINE_BEGIN', 'LINE_END', 'FILE_TOP', 'FILE_BOTTOM', 'PREVIOUS_CHARACTER', 'NEXT_CHARACTER', 'PREVIOUS_WORD', 'NEXT_WORD', 'PREVIOUS_LINE', 'NEXT_LINE', 'PREVIOUS_PAGE', 'NEXT_PAGE']) – Type, Where to move cursor to (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.text.move_lines"></a>

### bpy.ops.text.move_lines(*, direction='DOWN')

Move the currently selected line(s) up/down

**Parameters:**

**direction** (Literal['UP', 'DOWN']) – Direction, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.text.move_select"></a>

### bpy.ops.text.move_select(*, type='LINE_BEGIN')

Move the cursor while selecting

**Parameters:**

**type** (Literal['LINE_BEGIN', 'LINE_END', 'FILE_TOP', 'FILE_BOTTOM', 'PREVIOUS_CHARACTER', 'NEXT_CHARACTER', 'PREVIOUS_WORD', 'NEXT_WORD', 'PREVIOUS_LINE', 'NEXT_LINE', 'PREVIOUS_PAGE', 'NEXT_PAGE']) – Type, Where to move cursor to, to make a selection (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.text.new"></a>

### bpy.ops.text.new()

Create a new text data-block

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.text.open"></a>

### bpy.ops.text.open(*, filepath='', hide_props_region=True, check_existing=False, filter_blender=False, filter_backup=False, filter_image=False, filter_movie=False, filter_python=True, filter_font=False, filter_sound=False, filter_text=True, filter_archive=False, filter_btx=False, filter_alembic=False, filter_usd=False, filter_obj=False, filter_volume=False, filter_folder=True, filter_blenlib=False, filemode=9, relative_path=True, display_type='DEFAULT', sort_method='', internal=False)

Open a new text data-block

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
- **internal** (bool) – Make Internal, Make text file internal after loading (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.text.overwrite_toggle"></a>

### bpy.ops.text.overwrite_toggle()

Toggle overwrite while typing

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.text.paste"></a>

### bpy.ops.text.paste(*, selection=False)

Paste text from clipboard

**Parameters:**

**selection** (bool) – Selection, Paste text selected elsewhere rather than copied (X11/Wayland only) (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.text.reload"></a>

### bpy.ops.text.reload()

Reload active text data-block from its file

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.text.replace"></a>

### bpy.ops.text.replace(*, all=False)

Replace text with the specified text

**Parameters:**

**all** (bool) – Replace All, Replace all occurrences (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.text.replace_set_selected"></a>

### bpy.ops.text.replace_set_selected()

Replace text with specified text and set as selected

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.text.resolve_conflict"></a>

### bpy.ops.text.resolve_conflict(*, resolution='IGNORE')

When external text is out of sync, resolve the conflict

**Parameters:**

**resolution** (Literal['IGNORE', 'RELOAD', 'SAVE', 'MAKE_INTERNAL']) – Resolution, How to solve conflict due to differences in internal and external text (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.text.run_script"></a>

### bpy.ops.text.run_script()

Run active script

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.text.save"></a>

### bpy.ops.text.save()

Save active text data-block

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.text.save_as"></a>

### bpy.ops.text.save_as(*, filepath='', hide_props_region=True, check_existing=True, filter_blender=False, filter_backup=False, filter_image=False, filter_movie=False, filter_python=True, filter_font=False, filter_sound=False, filter_text=True, filter_archive=False, filter_btx=False, filter_alembic=False, filter_usd=False, filter_obj=False, filter_volume=False, filter_folder=True, filter_blenlib=False, filemode=9, display_type='DEFAULT', sort_method='')

Save active text file with options

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

<a id="bpy.ops.text.scroll"></a>

### bpy.ops.text.scroll(*, lines=1)

Undocumented, consider [contributing](https://developer.blender.org/).

**Parameters:**

**lines** (int) – Lines, Number of lines to scroll (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.text.scroll_bar"></a>

### bpy.ops.text.scroll_bar(*, lines=1)

Undocumented, consider [contributing](https://developer.blender.org/).

**Parameters:**

**lines** (int) – Lines, Number of lines to scroll (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.text.select_all"></a>

### bpy.ops.text.select_all()

Select all text

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.text.select_line"></a>

### bpy.ops.text.select_line()

Select text by line

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.text.select_word"></a>

### bpy.ops.text.select_word()

Select word under cursor

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.text.selection_set"></a>

### bpy.ops.text.selection_set()

Set text selection

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.text.start_find"></a>

### bpy.ops.text.start_find()

Start searching text

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.text.to_3d_object"></a>

### bpy.ops.text.to_3d_object(*, split_lines=False)

Create 3D text object from active text data-block

**Parameters:**

**split_lines** (bool) – Split Lines, Create one object per line in the text (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.text.unindent"></a>

### bpy.ops.text.unindent()

Unindent selected text

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.text.unlink"></a>

### bpy.ops.text.unlink()

Unlink active text data-block

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.text.update_shader"></a>

### bpy.ops.text.update_shader()

Update users of this shader, such as custom cameras and script nodes, with its new sockets and options

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]
