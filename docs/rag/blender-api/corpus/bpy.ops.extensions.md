<!-- source: Blender Python API reference 5.2 / bpy.ops.extensions.html -->

<a id="module-bpy.ops.extensions"></a>

# Extensions Operators

<a id="bpy.ops.extensions.package_disable"></a>

### bpy.ops.extensions.package_disable()

Turn off this extension

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[addons_core/bl_pkg/bl_extension_ops.py:3593](https://projects.blender.org/blender/blender/src/branch/main/scripts/addons_core/bl_pkg/bl_extension_ops.py#L3593)

<a id="bpy.ops.extensions.package_install"></a>

### bpy.ops.extensions.package_install(*, repo_directory='', repo_index=-1, pkg_id='', enable_on_install=True, url='', do_legacy_replace=False)

Download and install the extension

**Parameters:**

- **repo_directory** (str) – Repo Directory, (optional, never None)
- **repo_index** (int) – Repo Index, (in [-inf, inf], optional)
- **pkg_id** (str) – Package ID, (optional, never None)
- **enable_on_install** (bool) – Enable on Install, Enable after installing (optional)
- **url** (str) – URL, (optional, never None)
- **do_legacy_replace** (bool) – Do Legacy Replace, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[addons_core/bl_pkg/bl_extension_ops.py:1502](https://projects.blender.org/blender/blender/src/branch/main/scripts/addons_core/bl_pkg/bl_extension_ops.py#L1502)

<a id="bpy.ops.extensions.package_install_files"></a>

### bpy.ops.extensions.package_install_files(*, filter_glob='*.zip;*.py', directory='', files=None, filepath='', repo='', enable_on_install=True, target='', overwrite=True, url='')

Install extensions from files into a locally managed repository

**Parameters:**

- **filter_glob** (str) – filter_glob, (optional, never None)
- **directory** (str) – Directory, (optional, never None)
- **files** (`bpy_prop_collection`[`OperatorFileListElement`] | None) – files, (optional)
- **filepath** (str) – filepath, (optional, never None)
- **repo** (str) – User Repository, The user repository to install extensions into (optional)
- **enable_on_install** (bool) – Enable on Install, Enable after installing (optional)
- **target** (str) – Legacy Target Path, Path to install legacy add-on packages to (optional)
- **overwrite** (bool) – Legacy Overwrite, Remove existing add-ons with the same ID (optional)
- **url** (str) – URL, (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[addons_core/bl_pkg/bl_extension_ops.py:1502](https://projects.blender.org/blender/blender/src/branch/main/scripts/addons_core/bl_pkg/bl_extension_ops.py#L1502)

<a id="bpy.ops.extensions.package_install_marked"></a>

### bpy.ops.extensions.package_install_marked(*, enable_on_install=True)

Undocumented, consider [contributing](https://developer.blender.org/).

**Parameters:**

**enable_on_install** (bool) – Enable on Install, Enable after installing (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[addons_core/bl_pkg/bl_extension_ops.py:1502](https://projects.blender.org/blender/blender/src/branch/main/scripts/addons_core/bl_pkg/bl_extension_ops.py#L1502)

<a id="bpy.ops.extensions.package_mark_clear"></a>

### bpy.ops.extensions.package_mark_clear(*, pkg_id='', repo_index=-1)

Undocumented, consider [contributing](https://developer.blender.org/).

**Parameters:**

- **pkg_id** (str) – Package ID, (optional, never None)
- **repo_index** (int) – Repo Index, (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[addons_core/bl_pkg/bl_extension_ops.py:3680](https://projects.blender.org/blender/blender/src/branch/main/scripts/addons_core/bl_pkg/bl_extension_ops.py#L3680)

<a id="bpy.ops.extensions.package_mark_clear_all"></a>

### bpy.ops.extensions.package_mark_clear_all()

Undocumented, consider [contributing](https://developer.blender.org/).

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[addons_core/bl_pkg/bl_extension_ops.py:3727](https://projects.blender.org/blender/blender/src/branch/main/scripts/addons_core/bl_pkg/bl_extension_ops.py#L3727)

<a id="bpy.ops.extensions.package_mark_set"></a>

### bpy.ops.extensions.package_mark_set(*, pkg_id='', repo_index=-1)

Undocumented, consider [contributing](https://developer.blender.org/).

**Parameters:**

- **pkg_id** (str) – Package ID, (optional, never None)
- **repo_index** (int) – Repo Index, (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[addons_core/bl_pkg/bl_extension_ops.py:3666](https://projects.blender.org/blender/blender/src/branch/main/scripts/addons_core/bl_pkg/bl_extension_ops.py#L3666)

<a id="bpy.ops.extensions.package_mark_set_all"></a>

### bpy.ops.extensions.package_mark_set_all()

Undocumented, consider [contributing](https://developer.blender.org/).

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[addons_core/bl_pkg/bl_extension_ops.py:3691](https://projects.blender.org/blender/blender/src/branch/main/scripts/addons_core/bl_pkg/bl_extension_ops.py#L3691)

<a id="bpy.ops.extensions.package_obsolete_marked"></a>

### bpy.ops.extensions.package_obsolete_marked()

Zeroes package versions, useful for development - to test upgrading

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[addons_core/bl_pkg/bl_extension_ops.py:3784](https://projects.blender.org/blender/blender/src/branch/main/scripts/addons_core/bl_pkg/bl_extension_ops.py#L3784)

<a id="bpy.ops.extensions.package_show_clear"></a>

### bpy.ops.extensions.package_show_clear(*, pkg_id='', repo_index=-1)

Undocumented, consider [contributing](https://developer.blender.org/).

**Parameters:**

- **pkg_id** (str) – Package ID, (optional, never None)
- **repo_index** (int) – Repo Index, (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[addons_core/bl_pkg/bl_extension_ops.py:3753](https://projects.blender.org/blender/blender/src/branch/main/scripts/addons_core/bl_pkg/bl_extension_ops.py#L3753)

<a id="bpy.ops.extensions.package_show_set"></a>

### bpy.ops.extensions.package_show_set(*, pkg_id='', repo_index=-1)

Undocumented, consider [contributing](https://developer.blender.org/).

**Parameters:**

- **pkg_id** (str) – Package ID, (optional, never None)
- **repo_index** (int) – Repo Index, (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[addons_core/bl_pkg/bl_extension_ops.py:3739](https://projects.blender.org/blender/blender/src/branch/main/scripts/addons_core/bl_pkg/bl_extension_ops.py#L3739)

<a id="bpy.ops.extensions.package_show_settings"></a>

### bpy.ops.extensions.package_show_settings(*, pkg_id='', repo_index=-1)

Undocumented, consider [contributing](https://developer.blender.org/).

**Parameters:**

- **pkg_id** (str) – Package ID, (optional, never None)
- **repo_index** (int) – Repo Index, (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[addons_core/bl_pkg/bl_extension_ops.py:3767](https://projects.blender.org/blender/blender/src/branch/main/scripts/addons_core/bl_pkg/bl_extension_ops.py#L3767)

<a id="bpy.ops.extensions.package_theme_disable"></a>

### bpy.ops.extensions.package_theme_disable(*, pkg_id='', repo_index=-1)

Reset to the default theme if this theme is active

**Parameters:**

- **pkg_id** (str) – Package ID, (optional, never None)
- **repo_index** (int) – Repo Index, (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[addons_core/bl_pkg/bl_extension_ops.py:3621](https://projects.blender.org/blender/blender/src/branch/main/scripts/addons_core/bl_pkg/bl_extension_ops.py#L3621)

<a id="bpy.ops.extensions.package_theme_enable"></a>

### bpy.ops.extensions.package_theme_enable(*, pkg_id='', repo_index=-1)

Turn on this theme

**Parameters:**

- **pkg_id** (str) – Package ID, (optional, never None)
- **repo_index** (int) – Repo Index, (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[addons_core/bl_pkg/bl_extension_ops.py:3607](https://projects.blender.org/blender/blender/src/branch/main/scripts/addons_core/bl_pkg/bl_extension_ops.py#L3607)

<a id="bpy.ops.extensions.package_uninstall"></a>

### bpy.ops.extensions.package_uninstall(*, repo_directory='', repo_index=-1, pkg_id='')

Disable and uninstall the extension

**Parameters:**

- **repo_directory** (str) – Repo Directory, (optional, never None)
- **repo_index** (int) – Repo Index, (in [-inf, inf], optional)
- **pkg_id** (str) – Package ID, (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[addons_core/bl_pkg/bl_extension_ops.py:1502](https://projects.blender.org/blender/blender/src/branch/main/scripts/addons_core/bl_pkg/bl_extension_ops.py#L1502)

<a id="bpy.ops.extensions.package_uninstall_marked"></a>

### bpy.ops.extensions.package_uninstall_marked()

Undocumented, consider [contributing](https://developer.blender.org/).

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[addons_core/bl_pkg/bl_extension_ops.py:1502](https://projects.blender.org/blender/blender/src/branch/main/scripts/addons_core/bl_pkg/bl_extension_ops.py#L1502)

<a id="bpy.ops.extensions.package_uninstall_system"></a>

### bpy.ops.extensions.package_uninstall_system()

Undocumented, consider [contributing](https://developer.blender.org/).

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[addons_core/bl_pkg/bl_extension_ops.py:3584](https://projects.blender.org/blender/blender/src/branch/main/scripts/addons_core/bl_pkg/bl_extension_ops.py#L3584)

<a id="bpy.ops.extensions.package_upgrade_all"></a>

### bpy.ops.extensions.package_upgrade_all(*, use_active_only=False)

Upgrade installed extensions to their latest version from remote repositories

**Parameters:**

**use_active_only** (bool) – Active Only, Only upgrade the active repository (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[addons_core/bl_pkg/bl_extension_ops.py:1502](https://projects.blender.org/blender/blender/src/branch/main/scripts/addons_core/bl_pkg/bl_extension_ops.py#L1502)

<a id="bpy.ops.extensions.repo_enable_from_drop"></a>

### bpy.ops.extensions.repo_enable_from_drop(*, repo_index=-1)

Undocumented, consider [contributing](https://developer.blender.org/).

**Parameters:**

**repo_index** (int) – Repo Index, (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[addons_core/bl_pkg/bl_extension_ops.py:1835](https://projects.blender.org/blender/blender/src/branch/main/scripts/addons_core/bl_pkg/bl_extension_ops.py#L1835)

<a id="bpy.ops.extensions.repo_lock_all"></a>

### bpy.ops.extensions.repo_lock_all()

Lock repositories - to test locking

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[addons_core/bl_pkg/bl_extension_ops.py:3853](https://projects.blender.org/blender/blender/src/branch/main/scripts/addons_core/bl_pkg/bl_extension_ops.py#L3853)

<a id="bpy.ops.extensions.repo_refresh_all"></a>

### bpy.ops.extensions.repo_refresh_all(*, use_active_only=False)

Refresh extension & legacy add-ons, reloading modules & meta-data (similar to restarting)

**Parameters:**

**use_active_only** (bool) – Active Only, Only refresh the active repository (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[addons_core/bl_pkg/bl_extension_ops.py:1744](https://projects.blender.org/blender/blender/src/branch/main/scripts/addons_core/bl_pkg/bl_extension_ops.py#L1744)

<a id="bpy.ops.extensions.repo_sync"></a>

### bpy.ops.extensions.repo_sync(*, repo_directory='', repo_index=-1)

Undocumented, consider [contributing](https://developer.blender.org/).

**Parameters:**

- **repo_directory** (str) – Repo Directory, (optional, never None)
- **repo_index** (int) – Repo Index, (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[addons_core/bl_pkg/bl_extension_ops.py:1502](https://projects.blender.org/blender/blender/src/branch/main/scripts/addons_core/bl_pkg/bl_extension_ops.py#L1502)

<a id="bpy.ops.extensions.repo_sync_all"></a>

### bpy.ops.extensions.repo_sync_all(*, use_active_only=False)

Refresh the list of extensions for all the remote repositories

**Parameters:**

**use_active_only** (bool) – Active Only, Only sync the active repository (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[addons_core/bl_pkg/bl_extension_ops.py:1502](https://projects.blender.org/blender/blender/src/branch/main/scripts/addons_core/bl_pkg/bl_extension_ops.py#L1502)

<a id="bpy.ops.extensions.repo_unlock"></a>

### bpy.ops.extensions.repo_unlock()

Remove the repository file-system lock

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[addons_core/bl_pkg/bl_extension_ops.py:1922](https://projects.blender.org/blender/blender/src/branch/main/scripts/addons_core/bl_pkg/bl_extension_ops.py#L1922)

<a id="bpy.ops.extensions.repo_unlock_all"></a>

### bpy.ops.extensions.repo_unlock_all()

Unlock repositories - to test unlocking

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[addons_core/bl_pkg/bl_extension_ops.py:3879](https://projects.blender.org/blender/blender/src/branch/main/scripts/addons_core/bl_pkg/bl_extension_ops.py#L3879)

<a id="bpy.ops.extensions.status_clear"></a>

### bpy.ops.extensions.status_clear()

Undocumented, consider [contributing](https://developer.blender.org/).

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[addons_core/bl_pkg/bl_extension_ops.py:3652](https://projects.blender.org/blender/blender/src/branch/main/scripts/addons_core/bl_pkg/bl_extension_ops.py#L3652)

<a id="bpy.ops.extensions.status_clear_errors"></a>

### bpy.ops.extensions.status_clear_errors()

Undocumented, consider [contributing](https://developer.blender.org/).

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[addons_core/bl_pkg/bl_extension_ops.py:3641](https://projects.blender.org/blender/blender/src/branch/main/scripts/addons_core/bl_pkg/bl_extension_ops.py#L3641)

<a id="bpy.ops.extensions.userpref_allow_online"></a>

### bpy.ops.extensions.userpref_allow_online()

Allow Blender to access the internet. Add-ons that follow this setting will only connect to the internet if enabled. However, Blender cannot prevent third-party add-ons from violating this rule.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[addons_core/bl_pkg/bl_extension_ops.py:4005](https://projects.blender.org/blender/blender/src/branch/main/scripts/addons_core/bl_pkg/bl_extension_ops.py#L4005)

<a id="bpy.ops.extensions.userpref_allow_online_popup"></a>

### bpy.ops.extensions.userpref_allow_online_popup()

Allow Blender to access the internet. Add-ons that follow this setting will only connect to the internet if enabled. However, Blender cannot prevent third-party add-ons from violating this rule.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[addons_core/bl_pkg/bl_extension_ops.py:4020](https://projects.blender.org/blender/blender/src/branch/main/scripts/addons_core/bl_pkg/bl_extension_ops.py#L4020)

<a id="bpy.ops.extensions.userpref_show_for_update"></a>

### bpy.ops.extensions.userpref_show_for_update()

Open extensions preferences

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[addons_core/bl_pkg/bl_extension_ops.py:3944](https://projects.blender.org/blender/blender/src/branch/main/scripts/addons_core/bl_pkg/bl_extension_ops.py#L3944)

<a id="bpy.ops.extensions.userpref_show_online"></a>

### bpy.ops.extensions.userpref_show_online()

Show system preferences “Network” panel to allow online access

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[addons_core/bl_pkg/bl_extension_ops.py:3984](https://projects.blender.org/blender/blender/src/branch/main/scripts/addons_core/bl_pkg/bl_extension_ops.py#L3984)

<a id="bpy.ops.extensions.userpref_tags_set"></a>

### bpy.ops.extensions.userpref_tags_set(*, value=False, data_path='')

Set the value of all tags

**Parameters:**

- **value** (bool) – Value, Enable or disable all tags (optional)
- **data_path** (str) – Data Path, (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[addons_core/bl_pkg/bl_extension_ops.py:3913](https://projects.blender.org/blender/blender/src/branch/main/scripts/addons_core/bl_pkg/bl_extension_ops.py#L3913)
