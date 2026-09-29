<!-- source: Blender Python API reference 5.2 / bpy.types.PreferencesFilePaths.html -->

<a id="preferencesfilepaths-bpy-struct"></a>

# PreferencesFilePaths(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.PreferencesFilePaths"></a>

### class bpy.types.PreferencesFilePaths(bpy_struct)

Default paths for external files

<a id="bpy.types.PreferencesFilePaths.active_asset_library"></a>

#### bpy.types.PreferencesFilePaths.active_asset_library

Index of the asset library being edited in the Preferences UI (in [-32768, 32767], default 0)

**Type:**

int

<a id="bpy.types.PreferencesFilePaths.animation_player"></a>

#### bpy.types.PreferencesFilePaths.animation_player

Path to a custom animation/frame sequence player (default “”, never None)

**Type:**

str

<a id="bpy.types.PreferencesFilePaths.animation_player_preset"></a>

#### bpy.types.PreferencesFilePaths.animation_player_preset

Preset configs for external animation players (default `'INTERNAL'`)

- `INTERNAL`
  Internal – Built-in animation player.
- `DJV`
  DJV – Open source frame player.
- `FRAMECYCLER`
  FrameCycler – Frame player from IRIDAS.
- `RV`
  RV – Frame player from Tweak Software.
- `MPLAYER`
  MPlayer – Media player for video and PNG/JPEG/SGI image sequences.
- `CUSTOM`
  Custom – Custom animation player executable path.

**Type:**

Literal[‘INTERNAL’, ‘DJV’, ‘FRAMECYCLER’, ‘RV’, ‘MPLAYER’, ‘CUSTOM’]

<a id="bpy.types.PreferencesFilePaths.asset_libraries"></a>

#### bpy.types.PreferencesFilePaths.asset_libraries

(default None, readonly)

**Type:**

[`AssetLibraryCollection`](bpy.types.AssetLibraryCollection.md#bpy.types.AssetLibraryCollection "bpy.types.AssetLibraryCollection")[[`UserAssetLibrary`](bpy.types.UserAssetLibrary.md#bpy.types.UserAssetLibrary "bpy.types.UserAssetLibrary")]

<a id="bpy.types.PreferencesFilePaths.auto_save_time"></a>

#### bpy.types.PreferencesFilePaths.auto_save_time

The time (in minutes) to wait between automatic temporary saves (in [1, 60], default 2)

**Type:**

int

<a id="bpy.types.PreferencesFilePaths.file_preview_type"></a>

#### bpy.types.PreferencesFilePaths.file_preview_type

What type of blend preview to create (default `'AUTO'`)

- `NONE`
  None – Do not create blend previews.
- `AUTO`
  Auto – Automatically select best preview type.
- `SCREENSHOT`
  Screenshot – Capture the entire window.
- `CAMERA`
  Camera View – Workbench render of scene.

**Type:**

Literal[‘NONE’, ‘AUTO’, ‘SCREENSHOT’, ‘CAMERA’]

<a id="bpy.types.PreferencesFilePaths.font_directory"></a>

#### bpy.types.PreferencesFilePaths.font_directory

The default directory to search for loading fonts (default “//”, never None, blend relative `//` prefix supported)

**Type:**

str

<a id="bpy.types.PreferencesFilePaths.i18n_branches_directory"></a>

#### bpy.types.PreferencesFilePaths.i18n_branches_directory

The path to the ‘/branches’ directory of your local svn-translation copy, to allow translating from the UI (default “”, never None)

**Type:**

str

<a id="bpy.types.PreferencesFilePaths.image_editor"></a>

#### bpy.types.PreferencesFilePaths.image_editor

Path to an image editor (default “”, never None)

**Type:**

str

<a id="bpy.types.PreferencesFilePaths.recent_files"></a>

#### bpy.types.PreferencesFilePaths.recent_files

Maximum number of recently opened files to remember (in [0, 1000], default 200)

**Type:**

int

<a id="bpy.types.PreferencesFilePaths.render_cache_directory"></a>

#### bpy.types.PreferencesFilePaths.render_cache_directory

Where to cache raw render results (default “”, never None, blend relative `//` prefix supported)

**Type:**

str

<a id="bpy.types.PreferencesFilePaths.render_output_directory"></a>

#### bpy.types.PreferencesFilePaths.render_output_directory

The default directory for rendering output, for new scenes (default “//”, never None, blend relative `//` prefix supported)

**Type:**

str

<a id="bpy.types.PreferencesFilePaths.save_modified_images"></a>

#### bpy.types.PreferencesFilePaths.save_modified_images

How modified images should be handled when saving the .blend file (default `'ASK'`)

- `ASK`
  Ask Every Time – Show dialog to save modified images when saving the .blend file.
- `ALWAYS_SAVE`
  Always Save – Always save modified images when saving the .blend file.
- `NEVER_SAVE`
  Never Save – Never save modified images when saving the .blend file.

**Type:**

Literal[‘ASK’, ‘ALWAYS_SAVE’, ‘NEVER_SAVE’]

<a id="bpy.types.PreferencesFilePaths.save_version"></a>

#### bpy.types.PreferencesFilePaths.save_version

The number of old versions to maintain in the current directory, when manually saving (in [0, 32], default 1)

**Type:**

int

<a id="bpy.types.PreferencesFilePaths.script_directories"></a>

#### bpy.types.PreferencesFilePaths.script_directories

(default None, readonly)

**Type:**

[`ScriptDirectoryCollection`](bpy.types.ScriptDirectoryCollection.md#bpy.types.ScriptDirectoryCollection "bpy.types.ScriptDirectoryCollection")[[`ScriptDirectory`](bpy.types.ScriptDirectory.md#bpy.types.ScriptDirectory "bpy.types.ScriptDirectory")]

<a id="bpy.types.PreferencesFilePaths.show_hidden_files_datablocks"></a>

#### bpy.types.PreferencesFilePaths.show_hidden_files_datablocks

Show files and data-blocks that are normally hidden (default True)

**Type:**

bool

<a id="bpy.types.PreferencesFilePaths.show_recent_locations"></a>

#### bpy.types.PreferencesFilePaths.show_recent_locations

Show Recent locations list in the File Browser (default True)

**Type:**

bool

<a id="bpy.types.PreferencesFilePaths.show_system_bookmarks"></a>

#### bpy.types.PreferencesFilePaths.show_system_bookmarks

Show System locations list in the File Browser (default True)

**Type:**

bool

<a id="bpy.types.PreferencesFilePaths.sound_directory"></a>

#### bpy.types.PreferencesFilePaths.sound_directory

The default directory to search for sounds (default “//”, never None, blend relative `//` prefix supported)

**Type:**

str

<a id="bpy.types.PreferencesFilePaths.temporary_directory"></a>

#### bpy.types.PreferencesFilePaths.temporary_directory

The directory for storing temporary save files. The path must reference an existing directory or it will be ignored (default “”, never None)

**Type:**

str

<a id="bpy.types.PreferencesFilePaths.text_editor"></a>

#### bpy.types.PreferencesFilePaths.text_editor

Command to launch the text editor, either a full path or a command in $PATH.
Use the internal editor when left blank

(default “”, never None)

**Type:**

str

<a id="bpy.types.PreferencesFilePaths.text_editor_args"></a>

#### bpy.types.PreferencesFilePaths.text_editor_args

Defines the specific format of the arguments with which the text editor opens files. The supported expansions are as follows:

$filepath The absolute path of the file.
$line The line to open at (Optional).
$column The column to open from the beginning of the line (Optional).
$line0 & column0 start at zero.
Example: -f $filepath -l $line -c $column

(default “”, never None)

**Type:**

str

<a id="bpy.types.PreferencesFilePaths.texture_cache_directory"></a>

#### bpy.types.PreferencesFilePaths.texture_cache_directory

The directory for storing tx files generated from image files, for more efficient rendering. Paths may be absolute, or relative to the image file. Leave blank to store tx files in the same directory as image files (default “”, never None, blend relative `//` prefix supported)

**Type:**

str

<a id="bpy.types.PreferencesFilePaths.texture_directory"></a>

#### bpy.types.PreferencesFilePaths.texture_directory

The default directory to search for textures (default “//”, never None, blend relative `//` prefix supported)

**Type:**

str

<a id="bpy.types.PreferencesFilePaths.use_auto_save_temporary_files"></a>

#### bpy.types.PreferencesFilePaths.use_auto_save_temporary_files

Automatic saving of temporary files in temp directory, uses process ID.
Warning: Sculpt and edit mode data won’t be saved

(default True)

**Type:**

bool

<a id="bpy.types.PreferencesFilePaths.use_extension_online_access_handled"></a>

#### bpy.types.PreferencesFilePaths.use_extension_online_access_handled

The user has been shown the “Online Access” prompt and made a choice (default False)

**Type:**

bool

<a id="bpy.types.PreferencesFilePaths.use_file_compression"></a>

#### bpy.types.PreferencesFilePaths.use_file_compression

Enable file compression when saving .blend files (default True)

**Type:**

bool

<a id="bpy.types.PreferencesFilePaths.use_filter_files"></a>

#### bpy.types.PreferencesFilePaths.use_filter_files

Enable filtering of files in the File Browser (default True)

**Type:**

bool

<a id="bpy.types.PreferencesFilePaths.use_load_ui"></a>

#### bpy.types.PreferencesFilePaths.use_load_ui

Load user interface setup when loading .blend files (default True)

**Type:**

bool

<a id="bpy.types.PreferencesFilePaths.use_relative_paths"></a>

#### bpy.types.PreferencesFilePaths.use_relative_paths

Default relative path option for the file selector, when no path is defined yet (default True)

**Type:**

bool

<a id="bpy.types.PreferencesFilePaths.use_scripts_auto_execute"></a>

#### bpy.types.PreferencesFilePaths.use_scripts_auto_execute

Allow any .blend file to run scripts automatically (unsafe with blend files from an untrusted source) (default False)

**Type:**

bool

<a id="bpy.types.PreferencesFilePaths.use_tabs_as_spaces"></a>

#### bpy.types.PreferencesFilePaths.use_tabs_as_spaces

Automatically convert all new tabs into spaces for new and loaded text files (default True)

**Type:**

bool

<a id="bpy.types.PreferencesFilePaths.bl_rna_get_subclass"></a>

#### classmethod bpy.types.PreferencesFilePaths.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.PreferencesFilePaths.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.PreferencesFilePaths.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Preferences.filepaths`](bpy.types.Preferences.md#bpy.types.Preferences.filepaths "bpy.types.Preferences.filepaths") |  |
