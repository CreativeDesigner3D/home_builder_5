<!-- source: Blender Python API reference 5.2 / bpy.types.UserExtensionRepoCollection.html -->

<a id="userextensionrepocollection-bpy-prop-collection"></a>

# UserExtensionRepoCollection(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.UserExtensionRepoCollection"></a>

### class bpy.types.UserExtensionRepoCollection(bpy_prop_collection)

Collection of user extension repositories

<a id="bpy.types.UserExtensionRepoCollection.new"></a>

#### classmethod bpy.types.UserExtensionRepoCollection.new(*, name='', module='', custom_directory='', remote_url='', source='USER')

Add a new repository

**Parameters:**

- **name** (str) – Name, (optional, never None)
- **module** (str) – Module, (optional, never None)
- **custom_directory** (str) – Custom Directory, (optional, never None)
- **remote_url** (str) – Remote URL, (optional, never None)
- **source** (Literal['USER', 'SYSTEM']) –

  Source, How the repository is managed (optional)

  - `USER`
    User – Repository managed by the user, stored in user directories.
  - `SYSTEM`
    System – Read-only repository provided by the system.

**Returns:**

Newly added repository

**Return type:**

[`UserExtensionRepo`](bpy.types.UserExtensionRepo.md#bpy.types.UserExtensionRepo "bpy.types.UserExtensionRepo")

<a id="bpy.types.UserExtensionRepoCollection.remove"></a>

#### classmethod bpy.types.UserExtensionRepoCollection.remove(repo)

Remove repos

**Parameters:**

**repo** ([`UserExtensionRepo`](bpy.types.UserExtensionRepo.md#bpy.types.UserExtensionRepo "bpy.types.UserExtensionRepo") | None) – Repository to remove (never None)

<a id="bpy.types.UserExtensionRepoCollection.bl_rna_get_subclass"></a>

#### classmethod bpy.types.UserExtensionRepoCollection.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.UserExtensionRepoCollection.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.UserExtensionRepoCollection.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`PreferencesExtensions.repos`](bpy.types.PreferencesExtensions.md#bpy.types.PreferencesExtensions.repos "bpy.types.PreferencesExtensions.repos") |  |
