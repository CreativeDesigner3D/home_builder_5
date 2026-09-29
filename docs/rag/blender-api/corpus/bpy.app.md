<!-- source: Blender Python API reference 5.2 / bpy.app.html -->

<a id="module-bpy.app"></a>

# Application Data (bpy.app)

This module contains application values that remain unchanged during runtime.

Submodules

- [Application Handlers (bpy.app.handlers)](bpy.app.handlers.md)
- [Application Translations (bpy.app.translations)](bpy.app.translations.md)
- [Application Icons (bpy.app.icons)](bpy.app.icons.md)
- [Application Timers (bpy.app.timers)](bpy.app.timers.md)

<a id="bpy.app.autoexec_fail"></a>

### bpy.app.autoexec_fail

Boolean, True when auto-execution of scripts failed (read-only).

**Type:**

bool

<a id="bpy.app.autoexec_fail_message"></a>

### bpy.app.autoexec_fail_message

String, message describing the auto-execution failure (read-only).

**Type:**

str

<a id="bpy.app.autoexec_fail_quiet"></a>

### bpy.app.autoexec_fail_quiet

Boolean, True when auto-execution failure should be quiet, set after the warning is shown once for the current blend file (read-only).

**Type:**

bool

<a id="bpy.app.binary_path"></a>

### bpy.app.binary_path

The location of Blender’s executable, useful for utilities that open new instances. Read-only unless Blender is built as a Python module - in this case the value is an empty string which script authors may point to a Blender binary.

**Type:**

str

<a id="bpy.app.cachedir"></a>

### bpy.app.cachedir

String, the cache directory used by blender (read-only).

In rare cases the default cache directory may not be available;
in this case a temporary directory is used.

**Type:**

str

<a id="bpy.app.debug"></a>

### bpy.app.debug

Boolean, for debug info (started with `--debug` / `--debug-*` matching this attribute name).

**Type:**

bool

<a id="bpy.app.debug_depsgraph"></a>

### bpy.app.debug_depsgraph

Boolean, for debug info (started with `--debug` / `--debug-*` matching this attribute name).

**Type:**

bool

<a id="bpy.app.debug_depsgraph_build"></a>

### bpy.app.debug_depsgraph_build

Boolean, for debug info (started with `--debug` / `--debug-*` matching this attribute name).

**Type:**

bool

<a id="bpy.app.debug_depsgraph_eval"></a>

### bpy.app.debug_depsgraph_eval

Boolean, for debug info (started with `--debug` / `--debug-*` matching this attribute name).

**Type:**

bool

<a id="bpy.app.debug_depsgraph_pretty"></a>

### bpy.app.debug_depsgraph_pretty

Boolean, for debug info (started with `--debug` / `--debug-*` matching this attribute name).

**Type:**

bool

<a id="bpy.app.debug_depsgraph_tag"></a>

### bpy.app.debug_depsgraph_tag

Boolean, for debug info (started with `--debug` / `--debug-*` matching this attribute name).

**Type:**

bool

<a id="bpy.app.debug_depsgraph_time"></a>

### bpy.app.debug_depsgraph_time

Boolean, for debug info (started with `--debug` / `--debug-*` matching this attribute name).

**Type:**

bool

<a id="bpy.app.debug_events"></a>

### bpy.app.debug_events

Boolean, for debug info (started with `--debug` / `--debug-*` matching this attribute name).

**Type:**

bool

<a id="bpy.app.debug_freestyle"></a>

### bpy.app.debug_freestyle

Boolean, for debug info (started with `--debug` / `--debug-*` matching this attribute name).

**Type:**

bool

<a id="bpy.app.debug_handlers"></a>

### bpy.app.debug_handlers

Boolean, for debug info (started with `--debug` / `--debug-*` matching this attribute name).

**Type:**

bool

<a id="bpy.app.debug_io"></a>

### bpy.app.debug_io

Boolean, for debug info (started with `--debug` / `--debug-*` matching this attribute name).

**Type:**

bool

<a id="bpy.app.debug_python"></a>

### bpy.app.debug_python

Boolean, for debug info (started with `--debug` / `--debug-*` matching this attribute name).

**Type:**

bool

<a id="bpy.app.debug_simdata"></a>

### bpy.app.debug_simdata

Boolean, for debug info (started with `--debug` / `--debug-*` matching this attribute name).

**Type:**

bool

<a id="bpy.app.debug_value"></a>

### bpy.app.debug_value

Integer value which can be set to non-zero values for testing purposes.

**Type:**

int

<a id="bpy.app.debug_wm"></a>

### bpy.app.debug_wm

Boolean, for debug info (started with `--debug` / `--debug-*` matching this attribute name).

**Type:**

bool

<a id="bpy.app.driver_namespace"></a>

### bpy.app.driver_namespace

Dictionary for drivers namespace, editable in-place, reset on file load (read-only).

**Type:**

dict[str, Any]

File Loading & Order of Initialization
:   Since drivers may be evaluated immediately after loading a blend-file it is necessary
    to ensure the driver name-space is initialized beforehand.

    This can be done by registering text data-blocks to execute on startup,
    which executes the scripts before drivers are evaluated.
    See *Text -> Register* from Blender’s text editor.

    > **Hint:**
    >
    > You may prefer to use external files instead of Blender’s text-blocks.
    > This can be done using a text-block which executes an external file.
    >
    > This example runs `driver_namespace.py` located in the same directory as the text-blocks blend-file:
    >
    > ```python
    > import os
    > import bpy
    > blend_dir = os.path.normpath(os.path.join(__file__, "..", ".."))
    > bpy.utils.execfile(os.path.join(blend_dir, "driver_namespace.py"))
    > ```
    >
    > Using `__file__` ensures the text resolves to the expected path even when library-linked from another file.

    Other methods of populating the drivers name-space can be made to work but tend to be error prone:

    Using The `--python` command line argument to populate name-space often fails to achieve the desired goal
    because the initial evaluation will lookup a function that doesn’t exist yet,
    marking the driver as invalid - preventing further evaluation.

    Populating the driver name-space before the blend-file loads also doesn’t work
    since opening a file clears the name-space.

    It is possible to run a script via the `--python` command line argument, before the blend file.
    This can register a load-post handler ([`bpy.app.handlers.load_post`](bpy.app.handlers.md#bpy.app.handlers.load_post "bpy.app.handlers.load_post")) that initializes the name-space.
    While this works for background tasks it has the downside that opening the file from the file selector
    won’t setup the name-space.

<a id="bpy.app.online_access"></a>

### bpy.app.online_access

Boolean, true when internet access is allowed by Blender & 3rd party scripts (read-only).

**Type:**

bool

<a id="bpy.app.online_access_override"></a>

### bpy.app.online_access_override

Boolean, true when internet access preference is overridden by the command line (read-only).

**Type:**

bool

<a id="bpy.app.python_args"></a>

### bpy.app.python_args

Leading arguments to use when calling Python directly (via `sys.executable`). These arguments match settings Blender uses to ensure Python runs with a compatible environment (read-only).

**Type:**

tuple[str, …]

<a id="bpy.app.render_icon_size"></a>

### bpy.app.render_icon_size

Reference size for icon renders (read-only).

**Type:**

int

<a id="bpy.app.render_preview_size"></a>

### bpy.app.render_preview_size

Reference size for preview renders (read-only).

**Type:**

int

<a id="bpy.app.tempdir"></a>

### bpy.app.tempdir

String, the temp directory used by blender (read-only).

**Type:**

str

<a id="bpy.app.use_event_simulate"></a>

### bpy.app.use_event_simulate

Boolean, for application behavior (started with `--enable-*` matching this attribute name)

**Type:**

bool

<a id="bpy.app.use_userpref_skip_save_on_exit"></a>

### bpy.app.use_userpref_skip_save_on_exit

Boolean, for application behavior (started with `--enable-*` matching this attribute name)

**Type:**

bool

<a id="bpy.app.background"></a>

### bpy.app.background

Boolean, True when blender is running without a user interface (started with -b)

**Type:**

bool

<a id="bpy.app.factory_startup"></a>

### bpy.app.factory_startup

Boolean, True when blender is running with –factory-startup

**Type:**

bool

<a id="bpy.app.module"></a>

### bpy.app.module

Boolean, True when running Blender as a python module

**Type:**

bool

<a id="bpy.app.portable"></a>

### bpy.app.portable

Boolean, True unless blender was built to reference absolute paths (on UNIX).

**Type:**

bool

<a id="bpy.app.build_branch"></a>

### bpy.app.build_branch

The branch this blender instance was built from

**Type:**

bytes

<a id="bpy.app.build_cflags"></a>

### bpy.app.build_cflags

C compiler flags

**Type:**

bytes

<a id="bpy.app.build_commit_date"></a>

### bpy.app.build_commit_date

The date of the commit this Blender instance was built from

**Type:**

bytes

<a id="bpy.app.build_commit_time"></a>

### bpy.app.build_commit_time

The time of the commit this Blender instance was built from

**Type:**

bytes

<a id="bpy.app.build_cxxflags"></a>

### bpy.app.build_cxxflags

C++ compiler flags

**Type:**

bytes

<a id="bpy.app.build_date"></a>

### bpy.app.build_date

The date this Blender instance was built

**Type:**

bytes

<a id="bpy.app.build_hash"></a>

### bpy.app.build_hash

The commit hash this Blender instance was built with

**Type:**

bytes

<a id="bpy.app.build_linkflags"></a>

### bpy.app.build_linkflags

Binary linking flags

**Type:**

bytes

<a id="bpy.app.build_platform"></a>

### bpy.app.build_platform

The platform this blender instance was built for

**Type:**

bytes

<a id="bpy.app.build_system"></a>

### bpy.app.build_system

Build system used

**Type:**

bytes

<a id="bpy.app.build_time"></a>

### bpy.app.build_time

The time this Blender instance was built

**Type:**

bytes

<a id="bpy.app.build_type"></a>

### bpy.app.build_type

The type of build (Release, Debug)

**Type:**

bytes

<a id="bpy.app.build_commit_timestamp"></a>

### bpy.app.build_commit_timestamp

The unix timestamp of the commit this Blender instance was built from

**Type:**

int

<a id="bpy.app.version_cycle"></a>

### bpy.app.version_cycle

The release status of this build alpha/beta/rc/release

**Type:**

str

<a id="bpy.app.version_string"></a>

### bpy.app.version_string

The Blender version formatted as a string

**Type:**

str

<a id="bpy.app.version"></a>

### bpy.app.version

The Blender version as a tuple of 3 numbers (major, minor, micro). eg. (4, 3, 1)

**Type:**

tuple[int, int, int]

<a id="bpy.app.version_file"></a>

### bpy.app.version_file

The Blender File version, as a tuple of 3 numbers (major, minor, file sub-version), that will be used to save a .blend file. The last item in this tuple indicates the file sub-version, which is different from the release micro version (the last item of the `bpy.app.version` tuple). The file sub-version can be incremented multiple times while a Blender version is under development. This value is, and should be, used for handling compatibility changes between Blender versions

**Type:**

tuple[int, int, int]

<a id="bpy.app.alembic"></a>

### bpy.app.alembic

Constant value bpy.app.alembic(supported=True, version=(1, 8, 3), version_string=’ 1, 8, 3’)

**Type:**

[alembic](#bpy.app.alembic "bpy.app.alembic")

<a id="bpy.app.build_options"></a>

### bpy.app.build_options

Constant value bpy.app.build_options(bullet=True, codec_avi=False, codec_ffmpeg=True, codec_sndfile=True, compositor_cpu=True, cycles=True, cycles_osl=True, freestyle=True, image_cineon=True, image_dds=True, image_hdr=True, image_openexr=True, image_openjpeg=True, image_tiff=True, image_webp=True, input_ndof=True, audaspace=True, international=True, openal=True, opensubdiv=True, sdl=False, coreaudio=False, jack=True, pulseaudio=True, wasapi=False, libmv=True, mod_oceansim=True, mod_remesh=True, io_wavefront_obj=True, io_ply=True, io_stl=True, io_fbx=True, io_gpencil=True, opencolorio=True, openmp=False, openvdb=True, alembic=True, usd=True, fluid=True, xr_openxr=True, potrace=True, pugixml=True, haru=True, experimental_features=False)

**Type:**

[build_options](#bpy.app.build_options "bpy.app.build_options")

<a id="bpy.app.ffmpeg"></a>

### bpy.app.ffmpeg

Constant value bpy.app.ffmpeg(supported=True, avcodec_version=(62, 28, 100), avcodec_version_string=’62, 28, 100’, avdevice_version=(62, 3, 100), avdevice_version_string=’62, 3, 100’, avformat_version=(62, 12, 100), avformat_version_string=’62, 12, 100’, avutil_version=(60, 26, 100), avutil_version_string=’60, 26, 100’, swscale_version=(9, 5, 100), swscale_version_string=’ 9, 5, 100’)

**Type:**

[ffmpeg](#bpy.app.ffmpeg "bpy.app.ffmpeg")

<a id="bpy.app.ocio"></a>

### bpy.app.ocio

Constant value bpy.app.ocio(supported=True, version=(2, 5, 0), version_string=’ 2, 5, 0’)

**Type:**

[ocio](#bpy.app.ocio "bpy.app.ocio")

<a id="bpy.app.oiio"></a>

### bpy.app.oiio

Constant value bpy.app.oiio(supported=True, version=(3, 1, 13), version_string=’ 3, 1, 13’)

**Type:**

[oiio](#bpy.app.oiio "bpy.app.oiio")

<a id="bpy.app.opensubdiv"></a>

### bpy.app.opensubdiv

Constant value bpy.app.opensubdiv(supported=True, version=(3, 7, 0), version_string=’ 3, 7, 0’)

**Type:**

[opensubdiv](#bpy.app.opensubdiv "bpy.app.opensubdiv")

<a id="bpy.app.openvdb"></a>

### bpy.app.openvdb

Constant value bpy.app.openvdb(supported=True, version=(13, 0, 0), version_string=’13, 0, 0’)

**Type:**

[openvdb](#bpy.app.openvdb "bpy.app.openvdb")

<a id="bpy.app.sdl"></a>

### bpy.app.sdl

Constant value bpy.app.sdl(supported=False, version=(0, 0, 0), version_string=’Unknown’)

**Type:**

[sdl](#bpy.app.sdl "bpy.app.sdl")

<a id="bpy.app.usd"></a>

### bpy.app.usd

Constant value bpy.app.usd(supported=True, version=(0, 26, 3), version_string=’ 0, 26, 3’)

**Type:**

[usd](#bpy.app.usd "bpy.app.usd")

<a id="bpy.app.help_text"></a>

### bpy.app.help_text(*, all=False)

Return the help text as a string.

**Parameters:**

**all** (bool) – Return all arguments, even those which aren’t available for the current platform.

**Returns:**

Help text.

**Return type:**

str

<a id="bpy.app.is_job_running"></a>

### bpy.app.is_job_running(job_type)

Check whether a job of the given type is running.

**Parameters:**

**job_type** (str) – job type in [Wm Job Type Items](bpy_types_enum_items/wm_job_type_items.md#rna-enum-wm-job-type-items).

**Returns:**

Whether a job of the given type is currently running.

**Return type:**

bool

<a id="bpy.app.memory_usage_undo"></a>

### bpy.app.memory_usage_undo()

Get undo memory usage information.

**Returns:**

Memory usage of the undo stack in bytes.

**Return type:**

int
