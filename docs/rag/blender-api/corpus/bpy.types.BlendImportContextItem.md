<!-- source: Blender Python API reference 5.2 / bpy.types.BlendImportContextItem.html -->

<a id="blendimportcontextitem-bpy-struct"></a>

# BlendImportContextItem(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.BlendImportContextItem"></a>

### class bpy.types.BlendImportContextItem(bpy_struct)

An item (representing a data-block) in a BlendImportContext data. Currently only exposed as read-only data for the pre/post linking handlers

<a id="bpy.types.BlendImportContextItem.append_action"></a>

#### bpy.types.BlendImportContextItem.append_action

How this item has been handled by the append operation. Only set if the data has been appended (default `'UNSET'`, readonly)

- `UNSET`
  Not yet defined.
- `KEEP_LINKED`
  ID has been kept linked.
- `REUSE_LOCAL`
  An existing matching local ID has been re-used.
- `MAKE_LOCAL`
  The newly linked ID has been made local.
- `COPY_LOCAL`
  The linked ID had other unrelated usages, so it has been duplicated into a local copy.

**Type:**

Literal[‘UNSET’, ‘KEEP_LINKED’, ‘REUSE_LOCAL’, ‘MAKE_LOCAL’, ‘COPY_LOCAL’]

<a id="bpy.types.BlendImportContextItem.id"></a>

#### bpy.types.BlendImportContextItem.id

The imported ID. None until it has been linked or appended. May be the same as `reusable_local_id` when appended (readonly)

**Type:**

[`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID") | None

<a id="bpy.types.BlendImportContextItem.id_type"></a>

#### bpy.types.BlendImportContextItem.id_type

ID type of the item (default `'ACTION'`, readonly)

**Type:**

Literal[[Id Type Items](bpy_types_enum_items/id_type_items.md#rna-enum-id-type-items)]

<a id="bpy.types.BlendImportContextItem.import_info"></a>

#### bpy.types.BlendImportContextItem.import_info

Various status info about an item after it has been imported (default set(), readonly)

- `INDIRECT_USAGE`
  That item was added for an indirectly imported ID, as a dependency of another data-block.
- `LIBOVERRIDE_DEPENDENCY`
  That item represents an ID also used as liboverride dependency (either directly, as a liboverride reference, or indirectly, as data used by a liboverride reference). It should never be directly made local. Mutually exclusive with `LIBOVERRIDE_DEPENDENCY_ONLY`.
- `LIBOVERRIDE_DEPENDENCY_ONLY`
  That item represents an ID only used as liboverride dependency (either directly or indirectly, see `LIBOVERRIDE_DEPENDENCY` for precisions). It should not be considered during the ‘make local’ (append) process, and remain purely linked data. Mutually exclusive with `LIBOVERRIDE_DEPENDENCY`.

**Type:**

set[Literal[‘INDIRECT_USAGE’, ‘LIBOVERRIDE_DEPENDENCY’, ‘LIBOVERRIDE_DEPENDENCY_ONLY’]]

<a id="bpy.types.BlendImportContextItem.library_override_id"></a>

#### bpy.types.BlendImportContextItem.library_override_id

The library override of the linked ID. None until it has been created (readonly)

**Type:**

[`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID") | None

<a id="bpy.types.BlendImportContextItem.name"></a>

#### bpy.types.BlendImportContextItem.name

ID name of the item (default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.BlendImportContextItem.reusable_local_id"></a>

#### bpy.types.BlendImportContextItem.reusable_local_id

The already existing local ID that may be reused in append & reuse case. None until it has been found (readonly)

**Type:**

[`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID") | None

<a id="bpy.types.BlendImportContextItem.source_libraries"></a>

#### bpy.types.BlendImportContextItem.source_libraries

List of libraries to search and import that ID from. The ID will be imported from the first file in that list that contains it (default None, readonly)

**Type:**

[`BlendImportContextLibraries`](bpy.types.BlendImportContextLibraries.md#bpy.types.BlendImportContextLibraries "bpy.types.BlendImportContextLibraries")[[`BlendImportContextLibrary`](bpy.types.BlendImportContextLibrary.md#bpy.types.BlendImportContextLibrary "bpy.types.BlendImportContextLibrary")]

<a id="bpy.types.BlendImportContextItem.source_library"></a>

#### bpy.types.BlendImportContextItem.source_library

Library ID representing the blendfile from which the ID was imported. None until the ID has been linked or appended (readonly)

**Type:**

[`Library`](bpy.types.Library.md#bpy.types.Library "bpy.types.Library") | None

<a id="bpy.types.BlendImportContextItem.bl_rna_get_subclass"></a>

#### classmethod bpy.types.BlendImportContextItem.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.BlendImportContextItem.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.BlendImportContextItem.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`BlendImportContext.import_items`](bpy.types.BlendImportContext.md#bpy.types.BlendImportContext.import_items "bpy.types.BlendImportContext.import_items") |  |
