<!-- source: Blender Python API reference 5.2 / bpy.path.html -->

<a id="module-bpy.path"></a>

# Path Utilities (bpy.path)

This module has a similar scope to os.path, containing utility
functions for dealing with paths in Blender.

<a id="bpy.path.is_autoexec"></a>

### bpy.path.is_autoexec(path, *, canonicalize=False, strip_filename=False)

Return false when a directory is excluded from running scripts automatically,
see `bpy.types.PreferencesFilePaths.autoexec_paths`.

> **Note:**
>
> The preference to enable automatic script execution is not checked,
> see [`bpy.types.PreferencesFilePaths.use_scripts_auto_execute`](bpy.types.PreferencesFilePaths.md#bpy.types.PreferencesFilePaths.use_scripts_auto_execute "bpy.types.PreferencesFilePaths.use_scripts_auto_execute").

**Parameters:**

- **path** (str | bytes) – The directory to check, expected to end with a path separator.
- **canonicalize** (bool) – Resolve the path first,
  disable when it’s known to be resolved.
- **strip_filename** (bool) – Use the directory of path, otherwise it is a directory already.

**Returns:**

True when blend-files in the directory are trusted to run scripts.

**Return type:**

bool

<a id="bpy.path.abspath"></a>

### bpy.path.abspath(path, *, start=None, library=None)

Returns the absolute path relative to the current blend file
using the “//” prefix.

**Parameters:**

- **path** (str | bytes) – The path to convert to absolute.
- **start** (str | bytes | None) – Relative to this path,
  when not set the current filename is used.
- **library** ([`bpy.types.Library`](bpy.types.Library.md#bpy.types.Library "bpy.types.Library") | None) – The library this path is from. This is only included for
  convenience, when the library is not None its path replaces start.

**Returns:**

The absolute path.

**Return type:**

str

<a id="bpy.path.basename"></a>

### bpy.path.basename(path)

Equivalent to `os.path.basename`, but skips a “//” prefix.

Use for Windows compatibility.

**Parameters:**

**path** (str | bytes) – The path to get the base name of.

**Returns:**

The base name of the given path.

**Return type:**

str

<a id="bpy.path.clean_name"></a>

### bpy.path.clean_name(name, *, replace='_')

Returns a name with characters replaced that
may cause problems under various circumstances,
such as writing to a file.

All characters besides A-Z/a-z, 0-9 are replaced with “_”
or the *replace* argument if defined.

**Parameters:**

- **name** (str | bytes) – The path name.
- **replace** (str) – The replacement for non-valid characters.

**Returns:**

The cleaned name.

**Return type:**

str

<a id="bpy.path.display_name"></a>

### bpy.path.display_name(name, *, has_ext=True, title_case=True)

Creates a display string from name to be used in menus and the user interface.
Intended for use with filenames and module names.

**Parameters:**

- **name** (str) – The name to be used for displaying the user interface.
- **has_ext** (bool) – Remove file extension from name.
- **title_case** (bool) – Convert lowercase names to title case.

**Returns:**

The display string.

**Return type:**

str

<a id="bpy.path.display_name_to_filepath"></a>

### bpy.path.display_name_to_filepath(name)

Performs the reverse of display_name using literal versions of characters
which aren’t supported in a filepath.

**Parameters:**

**name** (str) – The display name to convert.

**Returns:**

The file path.

**Return type:**

str

<a id="bpy.path.display_name_from_filepath"></a>

### bpy.path.display_name_from_filepath(name)

Returns the path stripped of directory and extension,
ensured to be UTF-8 compatible.

**Parameters:**

**name** (str) – The file path to convert.

**Returns:**

The display name.

**Return type:**

str

<a id="bpy.path.ensure_ext"></a>

### bpy.path.ensure_ext(filepath, ext, *, case_sensitive=False)

Return the path with the extension added if it is not already set.

**Parameters:**

- **filepath** (str) – The file path.
- **ext** (str) – The extension to check for, can be a compound extension. Should
  start with a dot, such as `.blend` or `.tar.gz`.
- **case_sensitive** (bool) – Check for matching case when comparing extensions.

**Returns:**

The file path with the given extension.

**Return type:**

str

<a id="bpy.path.is_subdir"></a>

### bpy.path.is_subdir(path, directory)

Returns true if *path* is in a subdirectory of *directory*.
Both paths must be absolute.

**Parameters:**

- **path** (str | bytes) – An absolute path.
- **directory** (str | bytes) – The parent directory to check against.

**Returns:**

Whether or not the path is a subdirectory.

**Return type:**

bool

<a id="bpy.path.module_names"></a>

### bpy.path.module_names(path, *, recursive=False, package='')

Return a list of modules which can be imported from *path*.

**Parameters:**

- **path** (str) – a directory to scan.
- **recursive** (bool) – Also return submodule names for packages.
- **package** (str) – Optional string, used as the prefix for module names (without the trailing “.”).

**Returns:**

a list of string pairs (module_name, module_file).

**Return type:**

list[tuple[str, str]]

<a id="bpy.path.native_pathsep"></a>

### bpy.path.native_pathsep(path)

Replace the path separator with the system’s native `os.sep`.

**Parameters:**

**path** (str) – The path to replace.

**Returns:**

The path with system native separators.

**Return type:**

str

<a id="bpy.path.reduce_dirs"></a>

### bpy.path.reduce_dirs(dirs)

Given a sequence of directories, remove duplicates and
any directories nested in one of the other paths.
(Useful for recursive path searching).

**Parameters:**

**dirs** (Sequence[str]) – Sequence of directory paths.

**Returns:**

A unique list of paths.

**Return type:**

list[str]

<a id="bpy.path.relpath"></a>

### bpy.path.relpath(path, *, start=None)

Returns the path relative to the current blend file using the “//” prefix.

**Parameters:**

- **path** (str | bytes) – An absolute path.
- **start** (str | bytes | None) – Relative to this path,
  when not set the current filename is used.

**Returns:**

The relative path.

**Return type:**

str

<a id="bpy.path.resolve_ncase"></a>

### bpy.path.resolve_ncase(path)

Resolve a case insensitive path on a case sensitive system,
returning a string with the path if found else return the original path.

**Parameters:**

**path** (str) – The path name to resolve.

**Returns:**

The resolved path.

**Return type:**

str
