<!-- source: Blender Python API reference 5.2 / bpy.types.UserExtensionRepo.html -->

<a id="userextensionrepo-bpy-struct"></a>

# UserExtensionRepo(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.UserExtensionRepo"></a>

### class bpy.types.UserExtensionRepo(bpy_struct)

Settings to define an extension repository

<a id="bpy.types.UserExtensionRepo.access_token"></a>

#### bpy.types.UserExtensionRepo.access_token

Personal access token, may be required by some repositories (default “”, never None)

**Type:**

str

<a id="bpy.types.UserExtensionRepo.custom_directory"></a>

#### bpy.types.UserExtensionRepo.custom_directory

The local directory containing extensions (default “”, never None)

**Type:**

str

<a id="bpy.types.UserExtensionRepo.directory"></a>

#### bpy.types.UserExtensionRepo.directory

The local directory containing extensions (default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.UserExtensionRepo.enabled"></a>

#### bpy.types.UserExtensionRepo.enabled

Enable the repository (default False)

**Type:**

bool

<a id="bpy.types.UserExtensionRepo.module"></a>

#### bpy.types.UserExtensionRepo.module

Unique module identifier (default “”, never None)

**Type:**

str

<a id="bpy.types.UserExtensionRepo.name"></a>

#### bpy.types.UserExtensionRepo.name

Unique repository name (default “”, never None)

**Type:**

str

<a id="bpy.types.UserExtensionRepo.remote_url"></a>

#### bpy.types.UserExtensionRepo.remote_url

Remote URL to the extension repository, the file-system may be referenced using the file URI scheme: “<file://>” (default “”, never None)

**Type:**

str

<a id="bpy.types.UserExtensionRepo.source"></a>

#### bpy.types.UserExtensionRepo.source

Select if the repository is in a user managed or system provided directory (default `'USER'`)

- `USER`
  User – Repository managed by the user, stored in user directories.
- `SYSTEM`
  System – Read-only repository provided by the system.

**Type:**

Literal[‘USER’, ‘SYSTEM’]

<a id="bpy.types.UserExtensionRepo.use_access_token"></a>

#### bpy.types.UserExtensionRepo.use_access_token

Repository requires an access token (default False)

**Type:**

bool

<a id="bpy.types.UserExtensionRepo.use_cache"></a>

#### bpy.types.UserExtensionRepo.use_cache

Downloaded package files are deleted after installation (default False)

**Type:**

bool

<a id="bpy.types.UserExtensionRepo.use_custom_directory"></a>

#### bpy.types.UserExtensionRepo.use_custom_directory

Manually set the path for extensions to be stored. When disabled a user’s extensions directory is created. (default False)

**Type:**

bool

<a id="bpy.types.UserExtensionRepo.use_remote_url"></a>

#### bpy.types.UserExtensionRepo.use_remote_url

Synchronize the repository with a remote URL (default False)

**Type:**

bool

<a id="bpy.types.UserExtensionRepo.use_sync_on_startup"></a>

#### bpy.types.UserExtensionRepo.use_sync_on_startup

Allow Blender to check for updates upon launch (default False)

**Type:**

bool

<a id="bpy.types.UserExtensionRepo.bl_rna_get_subclass"></a>

#### classmethod bpy.types.UserExtensionRepo.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.UserExtensionRepo.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.UserExtensionRepo.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values

<a id="references"></a>

## References

|  |  |
| --- | --- |
| - [`PreferencesExtensions.repos`](bpy.types.PreferencesExtensions.md#bpy.types.PreferencesExtensions.repos "bpy.types.PreferencesExtensions.repos") - [`UserExtensionRepoCollection.new`](bpy.types.UserExtensionRepoCollection.md#bpy.types.UserExtensionRepoCollection.new "bpy.types.UserExtensionRepoCollection.new") | - [`UserExtensionRepoCollection.remove`](bpy.types.UserExtensionRepoCollection.md#bpy.types.UserExtensionRepoCollection.remove "bpy.types.UserExtensionRepoCollection.remove") |
