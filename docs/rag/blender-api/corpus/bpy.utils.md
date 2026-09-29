<!-- source: Blender Python API reference 5.2 / bpy.utils.html -->

<a id="module-bpy.utils"></a>

# Utilities (bpy.utils)

This module contains utility functions specific to blender but
not associated with blenders internal data.

Submodules

- [bpy.utils submodule (bpy.utils.previews)](bpy.utils.previews.md)
- [bpy.utils submodule (bpy.utils.units)](bpy.utils.units.md)

<a id="bpy.utils.blend_paths"></a>

### bpy.utils.blend_paths(*, absolute=False, packed=False, local=False)

Returns a list of paths to external files referenced by the loaded .blend file.

**Parameters:**

- **absolute** (bool) – When true the paths returned are made absolute.
- **packed** (bool) – When true include file paths for packed data.
- **local** (bool) – When true skip linked library paths.

**Returns:**

path list.

**Return type:**

list[str]

<a id="bpy.utils.escape_identifier"></a>

### bpy.utils.escape_identifier(string)

Simple string escaping function used for animation paths.

**Parameters:**

**string** (str) – text

**Returns:**

The escaped string.

**Return type:**

str

<a id="bpy.utils.flip_name"></a>

### bpy.utils.flip_name(name, *, strip_digits=False)

Flip a name between left/right sides, useful for
mirroring bone names.

**Parameters:**

- **name** (str) – Bone name to flip.
- **strip_digits** (bool) – Whether to remove `.###` suffix.

**Returns:**

The flipped name.

**Return type:**

str

<a id="bpy.utils.unescape_identifier"></a>

### bpy.utils.unescape_identifier(string)

Simple string un-escape function used for animation paths.
This performs the reverse of [`escape_identifier()`](#bpy.utils.escape_identifier "bpy.utils.escape_identifier").

**Parameters:**

**string** (str) – text

**Returns:**

The un-escaped string.

**Return type:**

str

<a id="bpy.utils.register_class"></a>

### bpy.utils.register_class(cls)

Register a subclass of a Blender type class.

**Parameters:**

**cls** (type[[`bpy.types.Panel`](bpy.types.Panel.md#bpy.types.Panel "bpy.types.Panel") | [`bpy.types.UIList`](bpy.types.UIList.md#bpy.types.UIList "bpy.types.UIList") | [`bpy.types.Menu`](bpy.types.Menu.md#bpy.types.Menu "bpy.types.Menu") | [`bpy.types.Header`](bpy.types.Header.md#bpy.types.Header "bpy.types.Header") | [`bpy.types.Operator`](bpy.types.Operator.md#bpy.types.Operator "bpy.types.Operator") | [`bpy.types.KeyingSetInfo`](bpy.types.KeyingSetInfo.md#bpy.types.KeyingSetInfo "bpy.types.KeyingSetInfo") | [`bpy.types.RenderEngine`](bpy.types.RenderEngine.md#bpy.types.RenderEngine "bpy.types.RenderEngine") | [`bpy.types.AssetShelf`](bpy.types.AssetShelf.md#bpy.types.AssetShelf "bpy.types.AssetShelf") | [`bpy.types.FileHandler`](bpy.types.FileHandler.md#bpy.types.FileHandler "bpy.types.FileHandler") | [`bpy.types.PropertyGroup`](bpy.types.PropertyGroup.md#bpy.types.PropertyGroup "bpy.types.PropertyGroup") | [`bpy.types.AddonPreferences`](bpy.types.AddonPreferences.md#bpy.types.AddonPreferences "bpy.types.AddonPreferences") | [`bpy.types.NodeTree`](bpy.types.NodeTree.md#bpy.types.NodeTree "bpy.types.NodeTree") | [`bpy.types.Node`](bpy.types.Node.md#bpy.types.Node "bpy.types.Node") | [`bpy.types.NodeSocket`](bpy.types.NodeSocket.md#bpy.types.NodeSocket "bpy.types.NodeSocket") | [`bpy.types.Gizmo`](bpy.types.Gizmo.md#bpy.types.Gizmo "bpy.types.Gizmo") | [`bpy.types.GizmoGroup`](bpy.types.GizmoGroup.md#bpy.types.GizmoGroup "bpy.types.GizmoGroup")]) – Registerable Blender class type.

**Raises:**

**ValueError** – if the class is not a subclass of a registerable blender class.

> **Note:**
>
> If the class has a *register* class method it will be called
> before registration.

<a id="bpy.utils.register_cli_command"></a>

### bpy.utils.register_cli_command(id, execute)

Register a command, accessible via the (`-c` / `--command`) command-line argument.

**Parameters:**

- **id** (str) –

  The command identifier (must pass an `str.isidentifier` check).

  If the `id` is already registered, a warning is printed and the command is inaccessible to prevent accidents invoking the wrong command.
- **execute** (Callable[[list[str]], int]) – Callback, taking a single list of strings and returns an int.
  The arguments are built from all command-line arguments following the command id.
  The return value should be 0 for success, 1 on failure (specific error codes from the `os` module can also be used).

**Returns:**

The command handle which can be passed to [`unregister_cli_command()`](#bpy.utils.unregister_cli_command "bpy.utils.unregister_cli_command").

This uses Python’s capsule type however the result should be considered an opaque handle only used for unregistering.

**Return type:**

Any

**Custom Commands**

Registering commands makes it possible to conveniently expose command line
functionality via commands passed to (`-c` / `--command`).

```python
import os

import bpy

def sysinfo_print():
    """
    Report basic system information.
    """

    import pprint
    import platform
    import textwrap

    width = 80
    indent = 2

    print("Blender {:s}".format(bpy.app.version_string))
    print("Running on: {:s}-{:s}".format(platform.platform(), platform.machine()))
    print("Processors: {!r}".format(os.cpu_count()))
    print()

    # Dump `bpy.app`.
    for attr in dir(bpy.app):
        if attr.startswith("_"):
            continue
        # Overly verbose.
        if attr in {"handlers", "build_cflags", "build_cxxflags"}:
            continue

        value = getattr(bpy.app, attr)
        if attr.startswith("build_"):
            pass
        elif isinstance(value, tuple):
            pass
        else:
            # Otherwise ignore.
            continue

        if isinstance(value, bytes):
            value = value.decode("utf-8", errors="ignore")

        if isinstance(value, str):
            pass
        elif isinstance(value, tuple) and hasattr(value, "__dir__"):
            value = {
                attr_sub: value_sub
                for attr_sub in dir(value)
                # Exclude built-ins.
                if not attr_sub.startswith(("_", "n_"))
                # Exclude methods.
                if not callable(value_sub := getattr(value, attr_sub))
            }
            value = pprint.pformat(value, indent=0, width=width)
        else:
            value = pprint.pformat(value, indent=0, width=width)

        print("{:s}:\n{:s}\n".format(attr, textwrap.indent(value, " " * indent)))

def sysinfo_command(argv):
    if argv and argv[0] == "--help":
        print("Print system information & exit!")
        return 0

    sysinfo_print()
    return 0

cli_commands = []

def register():
    cli_commands.append(bpy.utils.register_cli_command("sysinfo", sysinfo_command))

def unregister():
    for cmd in cli_commands:
        bpy.utils.unregister_cli_command(cmd)
    cli_commands.clear()

if __name__ == "__main__":
    register()
```

**Using Python Argument Parsing**

This example shows how the Python `argparse` module can be used with a custom command.

Using `argparse` is generally recommended as it has many useful utilities and
generates a `--help` message for your command.

```python
import os
import sys

import bpy

def argparse_create():
    import argparse

    parser = argparse.ArgumentParser(
        prog=os.path.basename(sys.argv[0]) + " --command keyconfig_export",
        description="Write key-configuration to a file.",
    )

    parser.add_argument(
        "-o", "--output",
        dest="output",
        metavar='OUTPUT',
        type=str,
        help="The path to write the keymap to.",
        required=True,
    )

    parser.add_argument(
        "-a", "--all",
        dest="all",
        action="store_true",
        help="Write all key-maps (not only customized key-maps).",
        required=False,
    )

    return parser

def keyconfig_export(argv):
    parser = argparse_create()
    args = parser.parse_args(argv)

    # Ensure the key configuration is loaded in background mode.
    bpy.utils.keyconfig_init()

    bpy.ops.preferences.keyconfig_export(
        filepath=args.output,
        all=args.all,
    )

    return 0

cli_commands = []

def register():
    cli_commands.append(bpy.utils.register_cli_command("keyconfig_export", keyconfig_export))

def unregister():
    for cmd in cli_commands:
        bpy.utils.unregister_cli_command(cmd)
    cli_commands.clear()

if __name__ == "__main__":
    register()
```

<a id="bpy.utils.unregister_cli_command"></a>

### bpy.utils.unregister_cli_command(handle)

Unregister a CLI command.

**Parameters:**

**handle** (Any) – The return value of [`register_cli_command()`](#bpy.utils.register_cli_command "bpy.utils.register_cli_command").

<a id="bpy.utils.resource_path"></a>

### bpy.utils.resource_path(type, *, major=None, minor=None)

Return the base path for storing system files.

**Parameters:**

- **type** (Literal['USER', 'LOCAL', 'SYSTEM', 'SYSTEM_LIBS']) – The resource type.
- **major** (int | None) – Major version. None (the default) uses `bpy.app.version[0]`.
- **minor** (int | None) – Minor version. None (the default) uses `bpy.app.version[1]`.

**Returns:**

the resource path (not necessarily existing).

**Return type:**

str

> **Note:**
>
> `SYSTEM_LIBS` mirrors `SYSTEM` but resolves to the directory for architecture-dependent libraries (typically under `/usr/lib/...` rather than `/usr/share/...`). It is an empty string on builds without a separate library directory, such as portable builds and the Python module.

<a id="bpy.utils.unregister_class"></a>

### bpy.utils.unregister_class(cls)

Unload the Python class from blender.

**Parameters:**

**cls** (type[[`bpy.types.Panel`](bpy.types.Panel.md#bpy.types.Panel "bpy.types.Panel") | [`bpy.types.UIList`](bpy.types.UIList.md#bpy.types.UIList "bpy.types.UIList") | [`bpy.types.Menu`](bpy.types.Menu.md#bpy.types.Menu "bpy.types.Menu") | [`bpy.types.Header`](bpy.types.Header.md#bpy.types.Header "bpy.types.Header") | [`bpy.types.Operator`](bpy.types.Operator.md#bpy.types.Operator "bpy.types.Operator") | [`bpy.types.KeyingSetInfo`](bpy.types.KeyingSetInfo.md#bpy.types.KeyingSetInfo "bpy.types.KeyingSetInfo") | [`bpy.types.RenderEngine`](bpy.types.RenderEngine.md#bpy.types.RenderEngine "bpy.types.RenderEngine") | [`bpy.types.AssetShelf`](bpy.types.AssetShelf.md#bpy.types.AssetShelf "bpy.types.AssetShelf") | [`bpy.types.FileHandler`](bpy.types.FileHandler.md#bpy.types.FileHandler "bpy.types.FileHandler") | [`bpy.types.PropertyGroup`](bpy.types.PropertyGroup.md#bpy.types.PropertyGroup "bpy.types.PropertyGroup") | [`bpy.types.AddonPreferences`](bpy.types.AddonPreferences.md#bpy.types.AddonPreferences "bpy.types.AddonPreferences") | [`bpy.types.NodeTree`](bpy.types.NodeTree.md#bpy.types.NodeTree "bpy.types.NodeTree") | [`bpy.types.Node`](bpy.types.Node.md#bpy.types.Node "bpy.types.Node") | [`bpy.types.NodeSocket`](bpy.types.NodeSocket.md#bpy.types.NodeSocket "bpy.types.NodeSocket") | [`bpy.types.Gizmo`](bpy.types.Gizmo.md#bpy.types.Gizmo "bpy.types.Gizmo") | [`bpy.types.GizmoGroup`](bpy.types.GizmoGroup.md#bpy.types.GizmoGroup "bpy.types.GizmoGroup")]) – Blender type class,
see [`bpy.utils.register_class()`](#bpy.utils.register_class "bpy.utils.register_class") for classes which can
be registered.

> **Note:**
>
> If the class has an *unregister* class method it will be called
> before unregistering.

<a id="bpy.utils.keyconfig_init"></a>

### bpy.utils.keyconfig_init()

Initialize and refresh key configurations, called from the Blender
window manager on startup and refresh.

<a id="bpy.utils.keyconfig_set"></a>

### bpy.utils.keyconfig_set(filepath, *, report=None)

Load and activate a key configuration from a file.

**Parameters:**

- **filepath** (str) – The file path to the key configuration preset.
- **report** (Callable[[set[str], str], None] | None) – An optional callable for reporting errors.

<a id="bpy.utils.load_scripts"></a>

### bpy.utils.load_scripts(*, reload_scripts=False, refresh_scripts=False, extensions=True)

Load scripts and run each modules register function.

**Parameters:**

- **reload_scripts** (bool) – Causes all scripts to have their unregister method
  called before loading.
- **refresh_scripts** (bool) – only load scripts which are not already loaded
  as modules.
- **extensions** (bool) – Loads additional scripts (add-ons & app-templates).

<a id="bpy.utils.modules_from_path"></a>

### bpy.utils.modules_from_path(path, loaded_modules)

Load all modules in a path and return them as a list.

**Parameters:**

- **path** (str) – this path is scanned for scripts and packages.
- **loaded_modules** (set[str]) – already loaded module names, files matching these
  names will be ignored.

**Returns:**

all loaded modules.

**Return type:**

list[ModuleType]

<a id="bpy.utils.preset_find"></a>

### bpy.utils.preset_find(name, preset_path, *, display_name=False, ext='.py')

Search for a preset by name.

**Parameters:**

- **name** (str) – The preset name.
- **preset_path** (str) – The preset subdirectory (e.g. `"keyconfig"`).
- **display_name** (bool) – When True, search by display name instead of filename.
- **ext** (str) – The file extension for the preset.

**Returns:**

The file path of the preset or None if not found.

**Return type:**

str | None

<a id="bpy.utils.preset_paths"></a>

### bpy.utils.preset_paths(subdir)

Returns a list of paths for a specific preset.

**Parameters:**

**subdir** (str) – preset subdirectory (must not be an absolute path).

**Returns:**

Script paths.

**Return type:**

list[str]

<a id="bpy.utils.refresh_script_paths"></a>

### bpy.utils.refresh_script_paths()

Run this after creating new script paths to update sys.path

<a id="bpy.utils.app_template_paths"></a>

### bpy.utils.app_template_paths(*, path=None)

Returns valid application template paths.

**Parameters:**

**path** (str | None) – Optional subdir.

**Returns:**

App template paths.

**Return type:**

Iterator[str]

<a id="bpy.utils.time_from_frame"></a>

### bpy.utils.time_from_frame(frame, *, fps=None, fps_base=None)

Returns the time from a frame number.

If *fps* and *fps_base* are not given the current scene is used.

**Parameters:**

- **frame** (int | float) – number.
- **fps** (float | None) – Frames per second, if not given the current scene is used.
- **fps_base** (float | None) – Frames per second base, if not given the current scene is used.

**Returns:**

the time in seconds.

**Return type:**

datetime.timedelta

<a id="bpy.utils.register_manual_map"></a>

### bpy.utils.register_manual_map(manual_hook)

Register a function to provide manual URL mappings.

**Parameters:**

**manual_hook** (Callable[[], tuple[str, list[tuple[str, str]]]]) – A callable that returns `(prefix, mapping)`
where mapping is a sequence of `(pattern, url)` pairs.

<a id="bpy.utils.unregister_manual_map"></a>

### bpy.utils.unregister_manual_map(manual_hook)

Unregister a previously registered manual map hook.

**Parameters:**

**manual_hook** (Callable[[], tuple[str, list[tuple[str, str]]]]) – The hook function to remove.

<a id="bpy.utils.register_preset_path"></a>

### bpy.utils.register_preset_path(path)

Register a preset search path.

**Parameters:**

**path** (str) –

preset directory (must be an absolute path).

This path must contain a “presets” subdirectory which will typically contain presets for add-ons.

You may call `bpy.utils.register_preset_path(os.path.dirname(__file__))` from an add-ons `__init__.py` file.
When the `__init__.py` is in the same location as a `presets` directory.
For example an operators preset would be located under: `presets/operator/{operator.id}/`
where `operator.id` is the `bl_idname` of the operator.

**Returns:**

success

**Return type:**

bool

<a id="bpy.utils.unregister_preset_path"></a>

### bpy.utils.unregister_preset_path(path)

Unregister a preset search path.

**Parameters:**

**path** (str) –

preset directory (must be an absolute path).

This must match the registered path exactly.

**Returns:**

success

**Return type:**

bool

<a id="bpy.utils.register_classes_factory"></a>

### bpy.utils.register_classes_factory(classes)

Utility function to create register and unregister functions
which simply registers and unregisters a sequence of classes.

**Parameters:**

**classes** (Sequence[type]) – Sequence of classes to register and unregister.

**Returns:**

register and unregister functions.

**Return type:**

tuple[Callable[[], None], Callable[[], None]]

<a id="bpy.utils.register_submodule_factory"></a>

### bpy.utils.register_submodule_factory(module_name, submodule_names)

Utility function to create register and unregister functions
which simply load submodules,
calling their register & unregister functions.

> **Note:**
>
> Modules are registered in the order given,
> unregistered in reverse order.

**Parameters:**

- **module_name** (str) – The module name, typically `__name__`.
- **submodule_names** (list[str]) – List of submodule names to load and unload.

**Returns:**

register and unregister functions.

**Return type:**

tuple[Callable[[], None], Callable[[], None]]

<a id="bpy.utils.register_tool"></a>

### bpy.utils.register_tool(tool_cls, *, after=None, separator=False, group=False)

Register a tool in the toolbar.

**Parameters:**

- **tool_cls** (type[[`bpy.types.WorkSpaceTool`](bpy.types.WorkSpaceTool.md#bpy.types.WorkSpaceTool "bpy.types.WorkSpaceTool")]) – A tool subclass.
- **after** (Sequence[str] | set[str] | None) – Optional identifiers this tool will be added after.
- **separator** (bool) – When true, add a separator before this tool.
- **group** (bool) – When true, add a new nested group of tools.

<a id="bpy.utils.make_rna_paths"></a>

### bpy.utils.make_rna_paths(struct_name, prop_name, enum_name)

Create RNA “paths” from given names.

**Parameters:**

- **struct_name** (str) – Name of a RNA struct (like e.g. “Scene”).
- **prop_name** (str) – Name of a RNA struct’s property.
- **enum_name** (str) – Name of a RNA enum identifier.

**Returns:**

A triple of three “RNA paths”
(most_complete_path, “struct.prop”, “struct.prop:’enum’”).
If no enum_name is given, the third element will always be empty.

**Return type:**

tuple[str, str, str]

<a id="bpy.utils.manual_map"></a>

### bpy.utils.manual_map()

Yield manual URL mappings from all registered hooks.

**Returns:**

An iterator of `(prefix, mapping)` pairs.

**Return type:**

Iterator[tuple[str, list[tuple[str, str]]]]

<a id="bpy.utils.manual_language_code"></a>

### bpy.utils.manual_language_code(default='en')

**Parameters:**

**default** (str) – The fallback language code to use when the current language is unavailable.

**Returns:**

The language code used for user manual URL component based on the current language user-preference,
falling back to the `default` when unavailable.

**Return type:**

str

<a id="bpy.utils.script_path_user"></a>

### bpy.utils.script_path_user()

Return the user script path or None.

**Returns:**

The user script path, or None if not found.

**Return type:**

str | None

<a id="bpy.utils.extension_path_user"></a>

### bpy.utils.extension_path_user(package, *, path='', create=False)

Return a user writable directory associated with an extension.

> **Note:**
>
> This allows each extension to have its own user directory to store files.
>
> The location of the extension it self is not a suitable place to store files
> because it is cleared each upgrade and the users may not have write permissions
> to the repository (typically “System” repositories).

**Parameters:**

- **package** (str) – The `__package__` of the extension.
- **path** (str) – Optional subdirectory.
- **create** (bool) – Treat the path as a directory and create it if its not existing.

**Returns:**

a path.

**Return type:**

str

<a id="bpy.utils.script_paths"></a>

### bpy.utils.script_paths(*, subdir=None, user_pref=True, check_all=False, use_user=True, use_system_environment=True)

Returns a list of valid script paths.

**Parameters:**

- **subdir** (str | None) – Optional subdir.
- **user_pref** (bool) – Include the user preference script paths.
- **check_all** (bool) – Include local, user and system paths rather just the paths Blender uses.
- **use_user** (bool) – Include user paths
- **use_system_environment** (bool) – Include BLENDER_SYSTEM_SCRIPTS variable path

**Returns:**

script paths.

**Return type:**

list[str]

<a id="bpy.utils.smpte_from_frame"></a>

### bpy.utils.smpte_from_frame(frame, *, fps=None, fps_base=None)

Returns an SMPTE formatted string from the *frame*:
`HH:MM:SS:FF`.

If *fps* and *fps_base* are not given the current scene is used.

**Parameters:**

- **frame** (int | float) – frame number.
- **fps** (float | None) – Frames per second, if not given the current scene is used.
- **fps_base** (float | None) – Frames per second base, if not given the current scene is used.

**Returns:**

the frame string.

**Return type:**

str

<a id="bpy.utils.smpte_from_seconds"></a>

### bpy.utils.smpte_from_seconds(time, *, fps=None, fps_base=None)

Returns an SMPTE formatted string from the *time*:
`HH:MM:SS:FF`.

If *fps* and *fps_base* are not given the current scene is used.

**Parameters:**

- **time** (int | float | datetime.timedelta) – time in seconds.
- **fps** (float | None) – Frames per second, if not given the current scene is used.
- **fps_base** (float | None) – Frames per second base, if not given the current scene is used.

**Returns:**

the frame string.

**Return type:**

str

<a id="bpy.utils.unregister_tool"></a>

### bpy.utils.unregister_tool(tool_cls)

Unregister a previously registered tool.

**Parameters:**

**tool_cls** (type[[`bpy.types.WorkSpaceTool`](bpy.types.WorkSpaceTool.md#bpy.types.WorkSpaceTool "bpy.types.WorkSpaceTool")]) – The tool class to unregister.

<a id="bpy.utils.user_resource"></a>

### bpy.utils.user_resource(resource_type, *, path='', create=False)

Return a user resource path (normally from the users home directory).

**Parameters:**

- **resource_type** (Literal['DATAFILES', 'CONFIG', 'SCRIPTS', 'EXTENSIONS']) – The resource type.
- **path** (str) – Optional subdirectory.
- **create** (bool) – Treat the path as a directory and create it if its not existing.

**Returns:**

a path.

**Return type:**

str

<a id="bpy.utils.execfile"></a>

### bpy.utils.execfile(filepath, *, mod=None)

Execute a file path as a Python script.

**Parameters:**

- **filepath** (str) – Path of the script to execute.
- **mod** (ModuleType | None) – Optional cached module, the result of a previous execution.

**Returns:**

The module which can be passed back in as `mod`.

**Return type:**

ModuleType

<a id="bpy.utils.expose_bundled_modules"></a>

### bpy.utils.expose_bundled_modules()

For Blender as a Python module, add bundled VFX library python bindings
to `sys.path`. These may be used instead of dedicated packages, to ensure
the libraries are compatible with Blender.
