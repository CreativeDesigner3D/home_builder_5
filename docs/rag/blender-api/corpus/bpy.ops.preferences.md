<!-- source: Blender Python API reference 5.2 / bpy.ops.preferences.html -->

<a id="module-bpy.ops.preferences"></a>

# Preferences Operators

<a id="bpy.ops.preferences.addon_disable"></a>

### bpy.ops.preferences.addon_disable(*, module='')

Turn off this add-on

**Parameters:**

**module** (str) – Module, Module name of the add-on to disable (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/userpref.py:547](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/userpref.py#L547)

<a id="bpy.ops.preferences.addon_enable"></a>

### bpy.ops.preferences.addon_enable(*, module='')

Turn on this add-on

**Parameters:**

**module** (str) – Module, Module name of the add-on to enable (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/userpref.py:483](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/userpref.py#L483)

<a id="bpy.ops.preferences.addon_expand"></a>

### bpy.ops.preferences.addon_expand(*, module='')

Display information and preferences for this add-on

**Parameters:**

**module** (str) – Module, Module name of the add-on to expand (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/userpref.py:924](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/userpref.py#L924)

<a id="bpy.ops.preferences.addon_install"></a>

### bpy.ops.preferences.addon_install(*, overwrite=True, enable_on_install=False, target='', filepath='', filter_folder=True, filter_python=True, filter_glob='*.py;*.zip')

Install an add-on

**Parameters:**

- **overwrite** (bool) – Overwrite, Remove existing add-ons with the same ID (optional)
- **enable_on_install** (bool) – Enable on Install, Enable after installing (optional)
- **target** (str) – Target Path, (optional)
- **filepath** (str) – filepath, (optional, never None)
- **filter_folder** (bool) – Filter folders, (optional)
- **filter_python** (bool) – Filter Python, (optional)
- **filter_glob** (str) – filter_glob, (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/userpref.py:712](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/userpref.py#L712)

<a id="bpy.ops.preferences.addon_refresh"></a>

### bpy.ops.preferences.addon_refresh()

Scan add-on directories for new modules

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/userpref.py:645](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/userpref.py#L645)

<a id="bpy.ops.preferences.addon_remove"></a>

### bpy.ops.preferences.addon_remove(*, module='')

Delete the add-on from the file system

**Parameters:**

**module** (str) – Module, Module name of the add-on to remove (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/userpref.py:873](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/userpref.py#L873)

<a id="bpy.ops.preferences.addon_show"></a>

### bpy.ops.preferences.addon_show(*, module='')

Show add-on preferences

**Parameters:**

**module** (str) – Module, Module name of the add-on to expand (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/userpref.py:950](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/userpref.py#L950)

<a id="bpy.ops.preferences.app_template_install"></a>

### bpy.ops.preferences.app_template_install(*, overwrite=True, filepath='', filter_folder=True, filter_glob='*.zip')

Install an application template

**Parameters:**

- **overwrite** (bool) – Overwrite, Remove existing template with the same ID (optional)
- **filepath** (str) – filepath, (optional, never None)
- **filter_folder** (bool) – Filter folders, (optional)
- **filter_glob** (str) – filter_glob, (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/userpref.py:1000](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/userpref.py#L1000)

<a id="bpy.ops.preferences.asset_library_add"></a>

### bpy.ops.preferences.asset_library_add(*, directory='', hide_props_region=True, check_existing=False, filter_blender=False, filter_backup=False, filter_image=False, filter_movie=False, filter_python=False, filter_font=False, filter_sound=False, filter_text=False, filter_archive=False, filter_btx=False, filter_alembic=False, filter_usd=False, filter_obj=False, filter_volume=False, filter_folder=True, filter_blenlib=False, filemode=9, display_type='DEFAULT', sort_method='', name='', remote_url='', type='LOCAL')

Add a directory to be used by the Asset Browser as source of assets

**Parameters:**

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
- **name** (str) – Name, Identifier (not necessarily unique) for the asset library (optional, never None)
- **remote_url** (str) – URL, Remote URL to the asset library (optional, never None)
- **type** (Literal['REMOTE', 'LOCAL']) –

  Type, The kind of asset library to add (optional)

  - `REMOTE`
    Add Remote Asset Library – Add an asset library referencing a remote repository with support for listing and updating asset libraries.
  - `LOCAL`
    Add Local Asset Library – Add an asset library managed via the file system without referencing an external repository.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.preferences.asset_library_remove"></a>

### bpy.ops.preferences.asset_library_remove(*, index=0)

Remove a path to a .blend file, so the Asset Browser will not attempt to show it anymore

**Parameters:**

**index** (int) – Index, (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.preferences.associate_blend"></a>

### bpy.ops.preferences.associate_blend()

Use this installation for .blend files and to display thumbnails

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.preferences.autoexec_path_add"></a>

### bpy.ops.preferences.autoexec_path_add()

Add path to exclude from auto-execution

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.preferences.autoexec_path_remove"></a>

### bpy.ops.preferences.autoexec_path_remove(*, index=0)

Remove path to exclude from auto-execution

**Parameters:**

**index** (int) – Index, (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.preferences.clear_filter"></a>

### bpy.ops.preferences.clear_filter()

Clear the search filter

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.preferences.copy_prev"></a>

### bpy.ops.preferences.copy_prev()

Copy settings from previous version

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/userpref.py:170](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/userpref.py#L170)

<a id="bpy.ops.preferences.extension_repo_add"></a>

### bpy.ops.preferences.extension_repo_add(*, name='', remote_url='', use_access_token=False, access_token='', use_sync_on_startup=False, use_custom_directory=False, custom_directory='', type='REMOTE')

Add a new repository used to store extensions

**Parameters:**

- **name** (str) – Name, Unique repository name (optional, never None)
- **remote_url** (str) – URL, Remote URL to the extension repository, the file-system may be referenced using the file URI scheme: “<file://>” (optional, never None)
- **use_access_token** (bool) – Requires Access Token, Repository requires an access token (optional)
- **access_token** (str) – Secret, Personal access token, may be required by some repositories (optional, never None)
- **use_sync_on_startup** (bool) – Check for Updates on Startup, Allow Blender to check for updates upon launch (optional)
- **use_custom_directory** (bool) – Custom Directory, Manually set the path for extensions to be stored. When disabled a user’s extensions directory is created. (optional)
- **custom_directory** (str) – Custom Directory, The local directory containing extensions (optional, never None)
- **type** (Literal['REMOTE', 'LOCAL']) –

  Type, The kind of repository to add (optional)

  - `REMOTE`
    Add Remote Repository – Add a repository referencing a remote repository with support for listing and updating extensions.
  - `LOCAL`
    Add Local Repository – Add a repository managed manually without referencing an external repository.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.preferences.extension_repo_remove"></a>

### bpy.ops.preferences.extension_repo_remove(*, index=0, remove_files=False)

Remove an extension repository

**Parameters:**

- **index** (int) – Index, (in [0, inf], optional)
- **remove_files** (bool) – Remove Files, Remove extension files when removing the repository (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.preferences.extension_url_drop"></a>

### bpy.ops.preferences.extension_url_drop(*, url='')

Handle dropping an extension URL

**Parameters:**

**url** (str) – URL, Location of the extension to install (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.preferences.keyconfig_activate"></a>

### bpy.ops.preferences.keyconfig_activate(*, filepath='')

Undocumented, consider [contributing](https://developer.blender.org/).

**Parameters:**

**filepath** (str) – filepath, (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/userpref.py:91](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/userpref.py#L91)

<a id="bpy.ops.preferences.keyconfig_export"></a>

### bpy.ops.preferences.keyconfig_export(*, all=False, filepath='', filter_folder=True, filter_text=True, filter_python=True)

Export key configuration to a Python script

**Parameters:**

- **all** (bool) – All Keymaps, Write all keymaps (not just user modified) (optional)
- **filepath** (str) – filepath, (optional, never None)
- **filter_folder** (bool) – Filter folders, (optional)
- **filter_text** (bool) – Filter text, (optional)
- **filter_python** (bool) – Filter Python, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/userpref.py:324](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/userpref.py#L324)

<a id="bpy.ops.preferences.keyconfig_import"></a>

### bpy.ops.preferences.keyconfig_import(*, filepath='keymap.py', filter_folder=True, filter_text=True, filter_python=True, keep_original=True)

Import key configuration from a Python script

**Parameters:**

- **filepath** (str) – filepath, (optional, never None)
- **filter_folder** (bool) – Filter folders, (optional)
- **filter_text** (bool) – Filter text, (optional)
- **filter_python** (bool) – Filter Python, (optional)
- **keep_original** (bool) – Keep Original, Keep original file after copying to configuration folder (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/userpref.py:259](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/userpref.py#L259)

<a id="bpy.ops.preferences.keyconfig_remove"></a>

### bpy.ops.preferences.keyconfig_remove()

Remove key config

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/userpref.py:463](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/userpref.py#L463)

<a id="bpy.ops.preferences.keyconfig_test"></a>

### bpy.ops.preferences.keyconfig_test()

Test key configuration for conflicts

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/userpref.py:194](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/userpref.py#L194)

<a id="bpy.ops.preferences.keyitem_add"></a>

### bpy.ops.preferences.keyitem_add()

Add key map item

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/userpref.py:411](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/userpref.py#L411)

<a id="bpy.ops.preferences.keyitem_remove"></a>

### bpy.ops.preferences.keyitem_remove(*, item_id=0)

Remove key map item

**Parameters:**

**item_id** (int) – Item Identifier, Identifier of the item to remove (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/userpref.py:443](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/userpref.py#L443)

<a id="bpy.ops.preferences.keyitem_restore"></a>

### bpy.ops.preferences.keyitem_restore(*, item_id=0)

Restore key map item

**Parameters:**

**item_id** (int) – Item Identifier, Identifier of the item to restore (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/userpref.py:395](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/userpref.py#L395)

<a id="bpy.ops.preferences.keymap_restore"></a>

### bpy.ops.preferences.keymap_restore(*, all=False)

Restore key map(s)

**Parameters:**

**all** (bool) – All Keymaps, Restore all keymaps to default (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/userpref.py:366](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/userpref.py#L366)

<a id="bpy.ops.preferences.reset_default_theme"></a>

### bpy.ops.preferences.reset_default_theme()

Reset to the default theme colors

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.preferences.script_directory_add"></a>

### bpy.ops.preferences.script_directory_add(*, directory='', filter_folder=True)

Undocumented, consider [contributing](https://developer.blender.org/).

**Parameters:**

- **directory** (str) – directory, (optional, never None)
- **filter_folder** (bool) – Filter Folders, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/userpref.py:1256](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/userpref.py#L1256)

<a id="bpy.ops.preferences.script_directory_remove"></a>

### bpy.ops.preferences.script_directory_remove(*, index=0)

Undocumented, consider [contributing](https://developer.blender.org/).

**Parameters:**

**index** (int) – Index, Index of the script directory to remove (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/userpref.py:1286](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/userpref.py#L1286)

<a id="bpy.ops.preferences.start_filter"></a>

### bpy.ops.preferences.start_filter()

Start entering filter text

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.preferences.studiolight_copy_settings"></a>

### bpy.ops.preferences.studiolight_copy_settings(*, index=0)

Copy Studio Light settings to the Studio Light editor

**Parameters:**

**index** (int) – index, (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/userpref.py:1227](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/userpref.py#L1227)

<a id="bpy.ops.preferences.studiolight_install"></a>

### bpy.ops.preferences.studiolight_install(*, files=None, directory='', filter_folder=True, filter_glob='*.png;*.jpg;*.hdr;*.exr', type='MATCAP')

Install a user defined light

**Parameters:**

- **files** (`bpy_prop_collection`[`OperatorFileListElement`] | None) – File Path, (optional)
- **directory** (str) – directory, (optional, never None)
- **filter_folder** (bool) – Filter Folders, (optional)
- **filter_glob** (str) – filter_glob, (optional, never None)
- **type** (Literal['MATCAP', 'WORLD', 'STUDIO']) –

  Type, (optional)

  - `MATCAP`
    MatCap – Install custom MatCaps.
  - `WORLD`
    World – Install custom HDRIs.
  - `STUDIO`
    Studio – Install custom Studio Lights.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/userpref.py:1110](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/userpref.py#L1110)

<a id="bpy.ops.preferences.studiolight_new"></a>

### bpy.ops.preferences.studiolight_new(*, filename='StudioLight')

Save custom studio light from the studio light editor settings

**Parameters:**

**filename** (str) – Name, (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/userpref.py:1157](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/userpref.py#L1157)

<a id="bpy.ops.preferences.studiolight_uninstall"></a>

### bpy.ops.preferences.studiolight_uninstall(*, index=0)

Delete Studio Light

**Parameters:**

**index** (int) – index, (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/userpref.py:1208](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/userpref.py#L1208)

<a id="bpy.ops.preferences.theme_install"></a>

### bpy.ops.preferences.theme_install(*, overwrite=True, filepath='', filter_folder=True, filter_glob='*.xml')

Load and apply a Blender XML theme file

**Parameters:**

- **overwrite** (bool) – Overwrite, Remove existing theme file if exists (optional)
- **filepath** (str) – filepath, (optional, never None)
- **filter_folder** (bool) – Filter folders, (optional)
- **filter_glob** (str) – filter_glob, (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/userpref.py:598](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/userpref.py#L598)

<a id="bpy.ops.preferences.unassociate_blend"></a>

### bpy.ops.preferences.unassociate_blend()

Remove this installation’s associations with .blend files

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]
