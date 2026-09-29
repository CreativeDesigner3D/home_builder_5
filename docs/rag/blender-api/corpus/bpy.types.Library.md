<!-- source: Blender Python API reference 5.2 / bpy.types.Library.html -->

<a id="library-id"></a>

# Library(ID)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")

<a id="bpy.types.Library"></a>

### class bpy.types.Library(ID)

External .blend file from which data is linked

<a id="bpy.types.Library.archive_libraries"></a>

#### bpy.types.Library.archive_libraries

Archive libraries of packed IDs, generated (and owned) by this source library (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`Library`](#bpy.types.Library "bpy.types.Library")]

<a id="bpy.types.Library.archive_parent_library"></a>

#### bpy.types.Library.archive_parent_library

Source library from which this archive of packed IDs was generated (readonly)

**Type:**

[`Library`](#bpy.types.Library "bpy.types.Library") | None

<a id="bpy.types.Library.filepath"></a>

#### bpy.types.Library.filepath

Path to the library .blend file (default “”, never None, blend relative `//` prefix supported)

**Type:**

str

<a id="bpy.types.Library.is_archive"></a>

#### bpy.types.Library.is_archive

This library is an ‘archive’ storage for packed linked IDs originally linked from its ‘archive parent’ library. (default False, readonly)

**Type:**

bool

<a id="bpy.types.Library.is_editable"></a>

#### bpy.types.Library.is_editable

Data-blocks in this library are editable despite being linked. Used by brush assets and their dependencies. (default False, readonly)

**Type:**

bool

<a id="bpy.types.Library.needs_liboverride_resync"></a>

#### bpy.types.Library.needs_liboverride_resync

True if this library contains library overrides that are linked in current blendfile, and that had to be recursively resynced on load (it is recommended to open and re-save that library blendfile then) (default False)

**Type:**

bool

<a id="bpy.types.Library.packed_file"></a>

#### bpy.types.Library.packed_file

(readonly)

**Type:**

[`PackedFile`](bpy.types.PackedFile.md#bpy.types.PackedFile "bpy.types.PackedFile") | None

<a id="bpy.types.Library.parent"></a>

#### bpy.types.Library.parent

(readonly)

**Type:**

[`Library`](#bpy.types.Library "bpy.types.Library") | None

<a id="bpy.types.Library.version"></a>

#### bpy.types.Library.version

Version of Blender the library .blend was saved with (array of 3 items, in [0, inf], default (0, 0, 0), readonly)

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[int]

<a id="bpy.types.Library.users_id"></a>

#### bpy.types.Library.users_id

ID data-blocks that use this library

**Type:**

tuple[[`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID"), …]

> **Note:**
>
> Takes `O(n)` time, where `n` is the total number of all
> linkable ID types in `bpy.data`.

(readonly)

<a id="bpy.types.Library.reload"></a>

#### bpy.types.Library.reload()

Reload this library and all its linked data-blocks

<a id="bpy.types.Library.bl_rna_get_subclass"></a>

#### classmethod bpy.types.Library.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.Library.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.Library.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, ID.name, ID.name_full, ID.id_type, ID.session_uid, ID.is_evaluated, ID.original, ID.users, ID.use_fake_user, ID.use_extra_user, ID.is_embedded_data, ID.is_linked_packed, ID.is_missing, ID.is_runtime_data, ID.is_editable, ID.tag, ID.is_library_indirect, ID.library, ID.library_weak_reference, ID.asset_data, ID.override_library, ID.preview

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, ID.bl_system_properties_get, ID.rename, ID.evaluated_get, ID.copy, ID.asset_mark, ID.asset_clear, ID.asset_generate_preview, ID.override_create, ID.override_hierarchy_create, ID.user_clear, ID.user_remap, ID.make_local, ID.user_of_id, ID.animation_data_create, ID.animation_data_clear, ID.update_tag, ID.preview_ensure, ID.bl_rna_get_subclass, ID.bl_rna_get_subclass_py

<a id="references"></a>

## References

|  |  |
| --- | --- |
| - [`BlendData.libraries`](bpy.types.BlendData.md#bpy.types.BlendData.libraries "bpy.types.BlendData.libraries") - [`BlendDataLibraries.remove`](bpy.types.BlendDataLibraries.md#bpy.types.BlendDataLibraries.remove "bpy.types.BlendDataLibraries.remove") - [`BlendImportContextItem.source_library`](bpy.types.BlendImportContextItem.md#bpy.types.BlendImportContextItem.source_library "bpy.types.BlendImportContextItem.source_library") - [`ID.library`](bpy.types.ID.md#bpy.types.ID.library "bpy.types.ID.library") | - [`Library.archive_libraries`](#bpy.types.Library.archive_libraries "bpy.types.Library.archive_libraries") - [`Library.archive_parent_library`](#bpy.types.Library.archive_parent_library "bpy.types.Library.archive_parent_library") - [`Library.parent`](#bpy.types.Library.parent "bpy.types.Library.parent") |
