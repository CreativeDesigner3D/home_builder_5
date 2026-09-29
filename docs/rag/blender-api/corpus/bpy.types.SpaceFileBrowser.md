<!-- source: Blender Python API reference 5.2 / bpy.types.SpaceFileBrowser.html -->

<a id="spacefilebrowser-space"></a>

# SpaceFileBrowser(Space)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Space`](bpy.types.Space.md#bpy.types.Space "bpy.types.Space")

<a id="bpy.types.SpaceFileBrowser"></a>

### class bpy.types.SpaceFileBrowser(Space)

File browser space data

<a id="bpy.types.SpaceFileBrowser.active_operator"></a>

#### bpy.types.SpaceFileBrowser.active_operator

(readonly)

**Type:**

[`Operator`](bpy.types.Operator.md#bpy.types.Operator "bpy.types.Operator") | None

<a id="bpy.types.SpaceFileBrowser.bookmarks"></a>

#### bpy.types.SpaceFileBrowser.bookmarks

User’s bookmarks (default None)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`FileBrowserFSMenuEntry`](bpy.types.FileBrowserFSMenuEntry.md#bpy.types.FileBrowserFSMenuEntry "bpy.types.FileBrowserFSMenuEntry")]

<a id="bpy.types.SpaceFileBrowser.bookmarks_active"></a>

#### bpy.types.SpaceFileBrowser.bookmarks_active

Index of active bookmark (-1 if none) (in [-32768, 32767], default 0)

**Type:**

int

<a id="bpy.types.SpaceFileBrowser.browse_mode"></a>

#### bpy.types.SpaceFileBrowser.browse_mode

Type of the File Editor view (regular file browsing or asset browsing) (default `'FILES'`)

**Type:**

Literal[[Space File Browse Mode Items](bpy_types_enum_items/space_file_browse_mode_items.md#rna-enum-space-file-browse-mode-items)]

<a id="bpy.types.SpaceFileBrowser.operator"></a>

#### bpy.types.SpaceFileBrowser.operator

(readonly)

**Type:**

[`Operator`](bpy.types.Operator.md#bpy.types.Operator "bpy.types.Operator") | None

<a id="bpy.types.SpaceFileBrowser.params"></a>

#### bpy.types.SpaceFileBrowser.params

Parameters and Settings for the Filebrowser (readonly)

**Type:**

[`FileSelectParams`](bpy.types.FileSelectParams.md#bpy.types.FileSelectParams "bpy.types.FileSelectParams") | None

<a id="bpy.types.SpaceFileBrowser.recent_folders"></a>

#### bpy.types.SpaceFileBrowser.recent_folders

(default None)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`FileBrowserFSMenuEntry`](bpy.types.FileBrowserFSMenuEntry.md#bpy.types.FileBrowserFSMenuEntry "bpy.types.FileBrowserFSMenuEntry")]

<a id="bpy.types.SpaceFileBrowser.recent_folders_active"></a>

#### bpy.types.SpaceFileBrowser.recent_folders_active

Index of active recent folder (-1 if none) (in [-32768, 32767], default 0)

**Type:**

int

<a id="bpy.types.SpaceFileBrowser.show_region_tool_props"></a>

#### bpy.types.SpaceFileBrowser.show_region_tool_props

(default False)

**Type:**

bool

<a id="bpy.types.SpaceFileBrowser.show_region_toolbar"></a>

#### bpy.types.SpaceFileBrowser.show_region_toolbar

(default False)

**Type:**

bool

<a id="bpy.types.SpaceFileBrowser.show_region_ui"></a>

#### bpy.types.SpaceFileBrowser.show_region_ui

(default False)

**Type:**

bool

<a id="bpy.types.SpaceFileBrowser.system_bookmarks"></a>

#### bpy.types.SpaceFileBrowser.system_bookmarks

System’s bookmarks (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`FileBrowserFSMenuEntry`](bpy.types.FileBrowserFSMenuEntry.md#bpy.types.FileBrowserFSMenuEntry "bpy.types.FileBrowserFSMenuEntry")]

<a id="bpy.types.SpaceFileBrowser.system_bookmarks_active"></a>

#### bpy.types.SpaceFileBrowser.system_bookmarks_active

Index of active system bookmark (-1 if none) (in [-32768, 32767], default 0)

**Type:**

int

<a id="bpy.types.SpaceFileBrowser.system_folders"></a>

#### bpy.types.SpaceFileBrowser.system_folders

System’s folders (usually root, available hard drives, etc) (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`FileBrowserFSMenuEntry`](bpy.types.FileBrowserFSMenuEntry.md#bpy.types.FileBrowserFSMenuEntry "bpy.types.FileBrowserFSMenuEntry")]

<a id="bpy.types.SpaceFileBrowser.system_folders_active"></a>

#### bpy.types.SpaceFileBrowser.system_folders_active

Index of active system folder (-1 if none) (in [-32768, 32767], default 0)

**Type:**

int

<a id="bpy.types.SpaceFileBrowser.activate_asset_by_id"></a>

#### bpy.types.SpaceFileBrowser.activate_asset_by_id(id_to_activate, *, deferred=False)

Activate and select the asset entry that represents the given ID

**Parameters:**

- **id_to_activate** ([`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID") | None) – id_to_activate
- **deferred** (bool) – Whether to activate the ID immediately (false) or after the file browser refreshes (true) (optional)

<a id="bpy.types.SpaceFileBrowser.activate_file_by_relative_path"></a>

#### bpy.types.SpaceFileBrowser.activate_file_by_relative_path(*, relative_path='')

Set active file and add to selection based on relative path to current File Browser directory

**Parameters:**

**relative_path** (str) – relative_path, (optional, never None)

<a id="bpy.types.SpaceFileBrowser.deselect_all"></a>

#### bpy.types.SpaceFileBrowser.deselect_all()

Deselect all files

<a id="bpy.types.SpaceFileBrowser.bl_rna_get_subclass"></a>

#### classmethod bpy.types.SpaceFileBrowser.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.SpaceFileBrowser.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.SpaceFileBrowser.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="bpy.types.SpaceFileBrowser.draw_handler_add"></a>

#### classmethod bpy.types.SpaceFileBrowser.draw_handler_add(callback, args, region_type, draw_type)

Add a new draw handler to this space type.
It will be called every time the specified region in the space type will be drawn.
Note: All arguments are positional only for now.

**Parameters:**

- **callback** (Callable[..., Any]) – A function that will be called when the region is drawn.
  It gets the specified arguments as input, it’s return value is ignored.
- **args** (tuple[Any, ...]) – Arguments that will be passed to the callback.
- **region_type** (str) – The region type the callback draws in; usually `WINDOW`. ([`bpy.types.Region.type`](bpy.types.Region.md#bpy.types.Region.type "bpy.types.Region.type"))
- **draw_type** (str) – Usually `POST_PIXEL` for 2D drawing and `POST_VIEW` for 3D drawing. In some cases `PRE_VIEW` can be used. `BACKDROP` can be used for backdrops in the node editor.

**Returns:**

Handler that can be removed later on.

**Return type:**

object

<a id="bpy.types.SpaceFileBrowser.draw_handler_remove"></a>

#### classmethod bpy.types.SpaceFileBrowser.draw_handler_remove(handler, region_type)

Remove a draw handler that was added previously.

**Parameters:**

- **handler** (object) – The draw handler that should be removed.
- **region_type** (str) – Region type the callback was added to.

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, Space.type, Space.show_locked_time, Space.show_region_header

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, Space.bl_rna_get_subclass, Space.bl_rna_get_subclass_py, Space.draw_handler_add, Space.draw_handler_remove
