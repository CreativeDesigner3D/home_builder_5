<!-- source: Blender Python API reference 5.2 / bpy.ops.brush.html -->

<a id="module-bpy.ops.brush"></a>

# Brush Operators

<a id="bpy.ops.brush.asset_activate"></a>

### bpy.ops.brush.asset_activate(*, asset_library_type='LOCAL', asset_library_identifier='', relative_asset_identifier='', use_toggle=False)

Activate a brush asset as current sculpt and paint tool

**Parameters:**

- **asset_library_type** (Literal[[Asset Library Type Items](bpy_types_enum_items/asset_library_type_items.md#rna-enum-asset-library-type-items)]) – Asset Library Type, (optional)
- **asset_library_identifier** (str) – Asset Library Identifier, (optional, never None)
- **relative_asset_identifier** (str) – Relative Asset Identifier, (optional, never None)
- **use_toggle** (bool) – Toggle, Switch between the current and assigned brushes on consecutive uses. (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.brush.asset_delete"></a>

### bpy.ops.brush.asset_delete()

Delete the active brush asset

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.brush.asset_edit_metadata"></a>

### bpy.ops.brush.asset_edit_metadata(*, catalog_path='', author='', description='')

Edit asset information like the catalog, preview image, tags, or author

**Parameters:**

- **catalog_path** (str) – Catalog, The asset’s catalog path (optional, never None)
- **author** (str) – Author, (optional, never None)
- **description** (str) – Description, (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.brush.asset_load_preview"></a>

### bpy.ops.brush.asset_load_preview(*, filepath='', hide_props_region=True, check_existing=False, filter_blender=False, filter_backup=False, filter_image=True, filter_movie=False, filter_python=False, filter_font=False, filter_sound=False, filter_text=False, filter_archive=False, filter_btx=False, filter_alembic=False, filter_usd=False, filter_obj=False, filter_volume=False, filter_folder=True, filter_blenlib=False, filemode=9, show_multiview=False, use_multiview=False, display_type='DEFAULT', sort_method='')

Choose a preview image for the brush

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

<a id="bpy.ops.brush.asset_revert"></a>

### bpy.ops.brush.asset_revert()

Revert the active brush settings to the default values from the asset library

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.brush.asset_save"></a>

### bpy.ops.brush.asset_save()

Update the active brush asset in the asset library with current settings

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.brush.asset_save_as"></a>

### bpy.ops.brush.asset_save_as(*, name='', asset_library_reference='', catalog_path='')

Save a copy of the active brush asset into the default asset library, and make it the active brush

**Parameters:**

- **name** (str) – Name, Name for the new brush asset (optional, never None)
- **asset_library_reference** (str) – Library, Asset library used to store the new brush (optional)
- **catalog_path** (str) – Catalog, Catalog to use for the new asset (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.brush.scale_size"></a>

### bpy.ops.brush.scale_size(*, scalar=1.0)

Change brush size by a scalar

**Parameters:**

**scalar** (float) – Scalar, Factor to scale brush size by (in [0, 2], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.brush.stencil_control"></a>

### bpy.ops.brush.stencil_control(*, mode='TRANSLATION', texmode='PRIMARY')

Control the stencil brush

**Parameters:**

- **mode** (Literal['TRANSLATION', 'SCALE', 'ROTATION']) – Tool, (optional)
- **texmode** (Literal['PRIMARY', 'SECONDARY']) – Tool, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.brush.stencil_fit_image_aspect"></a>

### bpy.ops.brush.stencil_fit_image_aspect(*, use_repeat=True, use_scale=True, mask=False)

When using an image texture, adjust the stencil size to fit the image aspect ratio

**Parameters:**

- **use_repeat** (bool) – Use Repeat, Use repeat mapping values (optional)
- **use_scale** (bool) – Use Scale, Use texture scale values (optional)
- **mask** (bool) – Modify Mask Stencil, Modify either the primary or mask stencil (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.brush.stencil_reset_transform"></a>

### bpy.ops.brush.stencil_reset_transform(*, mask=False)

Reset the stencil transformation to the default

**Parameters:**

**mask** (bool) – Modify Mask Stencil, Modify either the primary or mask stencil (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]
