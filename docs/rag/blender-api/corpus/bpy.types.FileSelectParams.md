<!-- source: Blender Python API reference 5.2 / bpy.types.FileSelectParams.html -->

<a id="fileselectparams-bpy-struct"></a>

# FileSelectParams(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

Subclasses

- [FileAssetSelectParams(FileSelectParams)](bpy.types.FileAssetSelectParams.md)

<a id="bpy.types.FileSelectParams"></a>

### class bpy.types.FileSelectParams(bpy_struct)

File Select Parameters

<a id="bpy.types.FileSelectParams.directory"></a>

#### bpy.types.FileSelectParams.directory

Directory displayed in the file browser (default b””, never None)

**Type:**

bytes

<a id="bpy.types.FileSelectParams.display_size"></a>

#### bpy.types.FileSelectParams.display_size

Change the size of thumbnails (in [16, 256], default 96)

**Type:**

int

<a id="bpy.types.FileSelectParams.display_size_discrete"></a>

#### bpy.types.FileSelectParams.display_size_discrete

Change the size of thumbnails in discrete steps (default `'TINY'`)

**Type:**

Literal[‘TINY’, ‘SMALL’, ‘NORMAL’, ‘BIG’, ‘LARGE’]

<a id="bpy.types.FileSelectParams.display_type"></a>

#### bpy.types.FileSelectParams.display_type

Display mode for the file list (default `'LIST_VERTICAL'`)

- `LIST_VERTICAL`
  Vertical List – Display files as a vertical list.
- `LIST_HORIZONTAL`
  Horizontal List – Display files as a horizontal list.
- `THUMBNAIL`
  Thumbnails – Display files as thumbnails.

**Type:**

Literal[‘LIST_VERTICAL’, ‘LIST_HORIZONTAL’, ‘THUMBNAIL’]

<a id="bpy.types.FileSelectParams.filename"></a>

#### bpy.types.FileSelectParams.filename

Active file in the file browser (default “”, never None)

**Type:**

str

<a id="bpy.types.FileSelectParams.filter_glob"></a>

#### bpy.types.FileSelectParams.filter_glob

UNIX shell-like filename patterns matching, supports wildcards (‘*’) and list of patterns separated by ‘;’ (default “”, never None)

**Type:**

str

<a id="bpy.types.FileSelectParams.filter_id"></a>

#### bpy.types.FileSelectParams.filter_id

Which ID types to show/hide, when browsing a library (readonly, never None)

**Type:**

[`FileSelectIDFilter`](bpy.types.FileSelectIDFilter.md#bpy.types.FileSelectIDFilter "bpy.types.FileSelectIDFilter")

<a id="bpy.types.FileSelectParams.filter_search"></a>

#### bpy.types.FileSelectParams.filter_search

Filter by name or tag, supports ‘*’ wildcard (default “”, never None)

**Type:**

str

<a id="bpy.types.FileSelectParams.list_column_size"></a>

#### bpy.types.FileSelectParams.list_column_size

The width of columns in horizontal list views (in [32, 750], default 32)

**Type:**

int

<a id="bpy.types.FileSelectParams.list_display_size"></a>

#### bpy.types.FileSelectParams.list_display_size

Change the size of thumbnails in list views (in [16, 128], default 32)

**Type:**

int

<a id="bpy.types.FileSelectParams.recursion_level"></a>

#### bpy.types.FileSelectParams.recursion_level

Numbers of dirtree levels to show simultaneously (default `'NONE'`)

- `NONE`
  None – Only list current directory’s content, with no recursion.
- `BLEND`
  Blend File – List .blend files’ content.
- `ALL_1`
  One Level – List all sub-directories’ content, one level of recursion.
- `ALL_2`
  Two Levels – List all sub-directories’ content, two levels of recursion.
- `ALL_3`
  Three Levels – List all sub-directories’ content, three levels of recursion.

**Type:**

Literal[‘NONE’, ‘BLEND’, ‘ALL_1’, ‘ALL_2’, ‘ALL_3’]

<a id="bpy.types.FileSelectParams.show_details_datetime"></a>

#### bpy.types.FileSelectParams.show_details_datetime

Show a column listing the date and time of modification for each file (default False)

**Type:**

bool

<a id="bpy.types.FileSelectParams.show_details_size"></a>

#### bpy.types.FileSelectParams.show_details_size

Show a column listing the size of each file (default False)

**Type:**

bool

<a id="bpy.types.FileSelectParams.show_hidden"></a>

#### bpy.types.FileSelectParams.show_hidden

Show hidden dot files (default True)

**Type:**

bool

<a id="bpy.types.FileSelectParams.sort_method"></a>

#### bpy.types.FileSelectParams.sort_method

(default `'FILE_SORT_ALPHA'`)

**Type:**

Literal[[Fileselect Params Sort Items](bpy_types_enum_items/fileselect_params_sort_items.md#rna-enum-fileselect-params-sort-items)]

<a id="bpy.types.FileSelectParams.title"></a>

#### bpy.types.FileSelectParams.title

Title for the file browser (default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.FileSelectParams.use_filter"></a>

#### bpy.types.FileSelectParams.use_filter

Enable filtering of files (default False)

**Type:**

bool

<a id="bpy.types.FileSelectParams.use_filter_asset_only"></a>

#### bpy.types.FileSelectParams.use_filter_asset_only

Hide .blend files items that are not data-blocks with asset metadata (default False)

**Type:**

bool

<a id="bpy.types.FileSelectParams.use_filter_backup"></a>

#### bpy.types.FileSelectParams.use_filter_backup

Show .blend1, .blend2, etc. files (default False)

**Type:**

bool

<a id="bpy.types.FileSelectParams.use_filter_blender"></a>

#### bpy.types.FileSelectParams.use_filter_blender

Show .blend files (default False)

**Type:**

bool

<a id="bpy.types.FileSelectParams.use_filter_blendid"></a>

#### bpy.types.FileSelectParams.use_filter_blendid

Show .blend files items (objects, materials, etc.) (default False)

**Type:**

bool

<a id="bpy.types.FileSelectParams.use_filter_folder"></a>

#### bpy.types.FileSelectParams.use_filter_folder

Show folders (default False)

**Type:**

bool

<a id="bpy.types.FileSelectParams.use_filter_font"></a>

#### bpy.types.FileSelectParams.use_filter_font

Show font files (default False)

**Type:**

bool

<a id="bpy.types.FileSelectParams.use_filter_image"></a>

#### bpy.types.FileSelectParams.use_filter_image

Show image files (default False)

**Type:**

bool

<a id="bpy.types.FileSelectParams.use_filter_movie"></a>

#### bpy.types.FileSelectParams.use_filter_movie

Show movie files (default False)

**Type:**

bool

<a id="bpy.types.FileSelectParams.use_filter_script"></a>

#### bpy.types.FileSelectParams.use_filter_script

Show script files (default False)

**Type:**

bool

<a id="bpy.types.FileSelectParams.use_filter_sound"></a>

#### bpy.types.FileSelectParams.use_filter_sound

Show sound files (default False)

**Type:**

bool

<a id="bpy.types.FileSelectParams.use_filter_text"></a>

#### bpy.types.FileSelectParams.use_filter_text

Show text files (default False)

**Type:**

bool

<a id="bpy.types.FileSelectParams.use_filter_volume"></a>

#### bpy.types.FileSelectParams.use_filter_volume

Show 3D volume files (default False)

**Type:**

bool

<a id="bpy.types.FileSelectParams.use_library_browsing"></a>

#### bpy.types.FileSelectParams.use_library_browsing

Whether we may browse Blender files’ content or not (default False, readonly)

**Type:**

bool

<a id="bpy.types.FileSelectParams.use_sort_invert"></a>

#### bpy.types.FileSelectParams.use_sort_invert

Sort items descending, from highest value to lowest (default False)

**Type:**

bool

<a id="bpy.types.FileSelectParams.bl_rna_get_subclass"></a>

#### classmethod bpy.types.FileSelectParams.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.FileSelectParams.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.FileSelectParams.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`SpaceFileBrowser.params`](bpy.types.SpaceFileBrowser.md#bpy.types.SpaceFileBrowser.params "bpy.types.SpaceFileBrowser.params") | - [`UILayout.template_file_select_path`](bpy.types.UILayout.md#bpy.types.UILayout.template_file_select_path "bpy.types.UILayout.template_file_select_path") |
