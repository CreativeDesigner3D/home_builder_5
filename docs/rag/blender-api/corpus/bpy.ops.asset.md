<!-- source: Blender Python API reference 5.2 / bpy.ops.asset.html -->

<a id="module-bpy.ops.asset"></a>

# Asset Operators

<a id="bpy.ops.asset.asset_download"></a>

### bpy.ops.asset.asset_download(*, asset_library_type='LOCAL', asset_library_identifier='', relative_asset_identifier='')

Make the asset available without internet access

**Parameters:**

- **asset_library_type** (Literal[[Asset Library Type Items](bpy_types_enum_items/asset_library_type_items.md#rna-enum-asset-library-type-items)]) – Asset Library Type, (optional)
- **asset_library_identifier** (str) – Asset Library Identifier, (optional, never None)
- **relative_asset_identifier** (str) – Relative Asset Identifier, (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.asset.assets_download"></a>

### bpy.ops.asset.assets_download()

Download the selected asset(s)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.asset.assign_action"></a>

### bpy.ops.asset.assign_action()

Set this pose Action as active Action on the active Object

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[addons_core/pose_library/operators.py:103](https://projects.blender.org/blender/blender/src/branch/main/scripts/addons_core/pose_library/operators.py#L103)

<a id="bpy.ops.asset.browse_containing_blend_file"></a>

### bpy.ops.asset.browse_containing_blend_file()

Open the system’s file browser with the blend file that contains the active asset

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/assets.py:183](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/assets.py#L183)

<a id="bpy.ops.asset.bundle_install"></a>

### bpy.ops.asset.bundle_install(*, asset_library_reference='', filepath='', hide_props_region=True, check_existing=True, filter_blender=True, filter_backup=False, filter_image=False, filter_movie=False, filter_python=False, filter_font=False, filter_sound=False, filter_text=False, filter_archive=False, filter_btx=False, filter_alembic=False, filter_usd=False, filter_obj=False, filter_volume=False, filter_folder=True, filter_blenlib=False, filemode=8, display_type='DEFAULT', sort_method='')

Copy the current .blend file into an Asset Library. Only works on standalone .blend files (i.e. when no other files are referenced)

**Parameters:**

- **asset_library_reference** (str) – asset_library_reference, (optional)
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

<a id="bpy.ops.asset.catalog_delete"></a>

### bpy.ops.asset.catalog_delete(*, catalog_id='')

Remove an asset catalog from the asset library (contained assets will not be affected and show up as unassigned)

**Parameters:**

**catalog_id** (str) – Catalog ID, ID of the catalog to delete (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.asset.catalog_new"></a>

### bpy.ops.asset.catalog_new(*, parent_path='')

Create a new catalog to put assets in

**Parameters:**

**parent_path** (str) – Parent Path, Optional path defining the location to put the new catalog under (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.asset.catalog_redo"></a>

### bpy.ops.asset.catalog_redo()

Redo the last undone edit to the asset catalogs

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.asset.catalog_undo"></a>

### bpy.ops.asset.catalog_undo()

Undo the last edit to the asset catalogs

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.asset.catalog_undo_push"></a>

### bpy.ops.asset.catalog_undo_push()

Store the current state of the asset catalogs in the undo buffer

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.asset.catalogs_save"></a>

### bpy.ops.asset.catalogs_save()

Make any edits to any catalogs permanent by writing the current set up to the asset library

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.asset.clear"></a>

### bpy.ops.asset.clear(*, set_fake_user=False)

Delete all asset metadata and turn the selected asset data-blocks back into normal data-blocks

**Parameters:**

**set_fake_user** (bool) – Set Fake User, Ensure the data-block is saved, even when it is no longer marked as asset (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.asset.clear_single"></a>

### bpy.ops.asset.clear_single(*, set_fake_user=False)

Delete all asset metadata and turn the asset data-block back into a normal data-block

**Parameters:**

**set_fake_user** (bool) – Set Fake User, Ensure the data-block is saved, even when it is no longer marked as asset (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.asset.library_refresh"></a>

### bpy.ops.asset.library_refresh(*, use_remote_listing=False, use_shift_for_remote_listing=False)

Reread assets and asset catalogs from the asset library on disk

**Parameters:**

- **use_remote_listing** (bool) – Remote Listing, Re-download the asset listing of a remote library. Only supported when the active asset library is remote or has a remote component (the Essentials library) (optional)
- **use_shift_for_remote_listing** (bool) – Use Shift for Remote Listing, When this operator is invoked and the Shift key is pressed, download the remote asset library listing (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.asset.library_reload_listing"></a>

### bpy.ops.asset.library_reload_listing()

Re-download the asset listing of a remote library. Only supported when the active asset library is remote or has a remote component (the Essentials library)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.asset.mark"></a>

### bpy.ops.asset.mark()

Enable easier reuse of selected data-blocks through the Asset Browser, with the help of customizable metadata (like previews, descriptions and tags)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.asset.mark_single"></a>

### bpy.ops.asset.mark_single()

Enable easier reuse of a data-block through the Asset Browser, with the help of customizable metadata (like previews, descriptions and tags)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.asset.open_containing_blend_file"></a>

### bpy.ops.asset.open_containing_blend_file()

Open the blend file that contains the active asset

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/assets.py:111](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/assets.py#L111)

<a id="bpy.ops.asset.screenshot_preview"></a>

### bpy.ops.asset.screenshot_preview(*, p1=(0, 0), p2=(0, 0), force_square=True)

Capture a screenshot to use as a preview for the selected asset

**Parameters:**

- **p1** (Sequence[int]) – Point 1, First point of the screenshot in screenspace (array of 2 items, in [0, inf], optional)
- **p2** (Sequence[int]) – Point 2, Second point of the screenshot in screenspace (array of 2 items, in [0, inf], optional)
- **force_square** (bool) – Force Square, If enabled, the screenshot will have the same height as width (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.asset.tag_add"></a>

### bpy.ops.asset.tag_add()

Add a new keyword tag to the active asset

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/assets.py:42](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/assets.py#L42)

<a id="bpy.ops.asset.tag_remove"></a>

### bpy.ops.asset.tag_remove()

Remove an existing keyword tag from the active asset

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/assets.py:65](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/assets.py#L65)
