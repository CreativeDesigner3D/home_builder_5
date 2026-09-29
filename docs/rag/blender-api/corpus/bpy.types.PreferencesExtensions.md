<!-- source: Blender Python API reference 5.2 / bpy.types.PreferencesExtensions.html -->

<a id="preferencesextensions-bpy-struct"></a>

# PreferencesExtensions(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.PreferencesExtensions"></a>

### class bpy.types.PreferencesExtensions(bpy_struct)

Settings for extensions

<a id="bpy.types.PreferencesExtensions.active_repo"></a>

#### bpy.types.PreferencesExtensions.active_repo

Index of the extensions repository being edited in the Preferences UI (in [-32768, 32767], default 0)

**Type:**

int

<a id="bpy.types.PreferencesExtensions.repos"></a>

#### bpy.types.PreferencesExtensions.repos

(default None, readonly)

**Type:**

[`UserExtensionRepoCollection`](bpy.types.UserExtensionRepoCollection.md#bpy.types.UserExtensionRepoCollection "bpy.types.UserExtensionRepoCollection")[[`UserExtensionRepo`](bpy.types.UserExtensionRepo.md#bpy.types.UserExtensionRepo "bpy.types.UserExtensionRepo")]

<a id="bpy.types.PreferencesExtensions.use_online_access_handled"></a>

#### bpy.types.PreferencesExtensions.use_online_access_handled

The user has been shown the “Online Access” prompt and made a choice (default False)

**Type:**

bool

<a id="bpy.types.PreferencesExtensions.bl_rna_get_subclass"></a>

#### classmethod bpy.types.PreferencesExtensions.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.PreferencesExtensions.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.PreferencesExtensions.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Preferences.extensions`](bpy.types.Preferences.md#bpy.types.Preferences.extensions "bpy.types.Preferences.extensions") |  |
