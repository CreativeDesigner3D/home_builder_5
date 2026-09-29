<!-- source: Blender Python API reference 5.2 / bpy.ops.ed.html -->

<a id="module-bpy.ops.ed"></a>

# Ed Operators

<a id="bpy.ops.ed.flush_edits"></a>

### bpy.ops.ed.flush_edits()

Flush edit data from active editing modes

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.ed.lib_id_fake_user_toggle"></a>

### bpy.ops.ed.lib_id_fake_user_toggle()

Save this data-block even if it has no users

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.ed.lib_id_generate_preview"></a>

### bpy.ops.ed.lib_id_generate_preview()

Create an automatic preview for the selected data-block

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.ed.lib_id_generate_preview_from_object"></a>

### bpy.ops.ed.lib_id_generate_preview_from_object()

Create a preview for this asset by rendering the active object

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.ed.lib_id_load_custom_preview"></a>

### bpy.ops.ed.lib_id_load_custom_preview(*, filepath='', hide_props_region=True, check_existing=False, filter_blender=False, filter_backup=False, filter_image=True, filter_movie=False, filter_python=False, filter_font=False, filter_sound=False, filter_text=False, filter_archive=False, filter_btx=False, filter_alembic=False, filter_usd=False, filter_obj=False, filter_volume=False, filter_folder=True, filter_blenlib=False, filemode=9, show_multiview=False, use_multiview=False, display_type='DEFAULT', sort_method='')

Choose an image to help identify the data-block visually

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

<a id="bpy.ops.ed.lib_id_override_editable_toggle"></a>

### bpy.ops.ed.lib_id_override_editable_toggle()

Set if this library override data-block can be edited

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.ed.lib_id_remove_preview"></a>

### bpy.ops.ed.lib_id_remove_preview()

Remove the preview of this data-block

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.ed.lib_id_unlink"></a>

### bpy.ops.ed.lib_id_unlink()

Remove a usage of a data-block, clearing the assignment

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.ed.redo"></a>

### bpy.ops.ed.redo()

Redo previous action

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.ed.undo"></a>

### bpy.ops.ed.undo()

Undo previous action

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.ed.undo_history"></a>

### bpy.ops.ed.undo_history(*, item=0)

Undo or redo specific action in history

**Parameters:**

**item** (int) – Item, (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.ed.undo_push"></a>

### bpy.ops.ed.undo_push(*, message='Add an undo step *function may be moved*')

Add an undo state (internal use only)

**Parameters:**

**message** (str) – Undo Message, (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.ed.undo_redo"></a>

### bpy.ops.ed.undo_redo()

Undo and redo previous action

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]
