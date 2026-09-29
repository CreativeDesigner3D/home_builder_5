<!-- source: Blender Python API reference 5.2 / bpy.app.handlers.html -->

<a id="module-bpy.app.handlers"></a>

# Application Handlers (bpy.app.handlers)

This module contains callback lists

<a id="basic-handler-example"></a>

## Basic Handler Example

This script shows the most simple example of adding a handler.

```python
import bpy

def my_handler(scene):
    print("Frame Change", scene.frame_current)

bpy.app.handlers.frame_change_pre.append(my_handler)
```

<a id="persistent-handler-example"></a>

## Persistent Handler Example

By default handlers are freed when loading new files, in some cases you may
want the handler stay running across multiple files (when the handler is
part of an add-on for example).

For this the [`bpy.app.handlers.persistent`](#bpy.app.handlers.persistent "bpy.app.handlers.persistent") decorator needs to be used.

```python
import bpy
from bpy.app.handlers import persistent

@persistent
def load_handler(dummy):
    print("Load Handler:", bpy.data.filepath)

bpy.app.handlers.load_post.append(load_handler)
```

<a id="note-on-altering-data"></a>

## Note on Altering Data

Altering data from handlers should be done carefully. While rendering the
`frame_change_pre` and `frame_change_post` handlers are called from one
thread and the viewport updates from a different thread. If the handler changes
data that is accessed by the viewport, this can cause a crash of Blender. In
such cases, lock the interface (Render → Lock Interface or
[`bpy.types.RenderSettings.use_lock_interface`](bpy.types.RenderSettings.md#bpy.types.RenderSettings.use_lock_interface "bpy.types.RenderSettings.use_lock_interface")) before starting a render.

Below is an example of a mesh that is altered from a handler:

```python
def frame_change_pre(scene):
    # A triangle that shifts in the z direction.
    zshift = scene.frame_current * 0.1
    vertices = [(-1, -1, zshift), (1, -1, zshift), (0, 1, zshift)]
    triangles = [(0, 1, 2)]

    object = bpy.data.objects["The Object"]
    object.data.clear_geometry()
    object.data.from_pydata(vertices, [], triangles)
```

<a id="bpy.app.handlers.animation_playback_post"></a>

### bpy.app.handlers.animation_playback_post

on ending animation playback. Accepts one or two arguments: The scene data-block, and optionally the dependency graph being updated

**Type:**

list[Callable[[[bpy.types.Scene](bpy.types.Scene.md#bpy.types.Scene "bpy.types.Scene"), [bpy.types.Depsgraph](bpy.types.Depsgraph.md#bpy.types.Depsgraph "bpy.types.Depsgraph")], None] | Callable[[[bpy.types.Scene](bpy.types.Scene.md#bpy.types.Scene "bpy.types.Scene")], None]]

<a id="bpy.app.handlers.animation_playback_pre"></a>

### bpy.app.handlers.animation_playback_pre

on starting animation playback. Accepts one or two arguments: The scene data-block, and optionally the dependency graph being updated

**Type:**

list[Callable[[[bpy.types.Scene](bpy.types.Scene.md#bpy.types.Scene "bpy.types.Scene"), [bpy.types.Depsgraph](bpy.types.Depsgraph.md#bpy.types.Depsgraph "bpy.types.Depsgraph")], None] | Callable[[[bpy.types.Scene](bpy.types.Scene.md#bpy.types.Scene "bpy.types.Scene")], None]]

<a id="bpy.app.handlers.annotation_post"></a>

### bpy.app.handlers.annotation_post

on drawing an annotation (after). Accepts two arguments: the annotation data-block and dependency graph

**Type:**

list[Callable[[[bpy.types.GreasePencil](bpy.types.GreasePencil.md#bpy.types.GreasePencil "bpy.types.GreasePencil"), [bpy.types.Depsgraph](bpy.types.Depsgraph.md#bpy.types.Depsgraph "bpy.types.Depsgraph")], None]]

<a id="bpy.app.handlers.annotation_pre"></a>

### bpy.app.handlers.annotation_pre

on drawing an annotation (before). Accepts two arguments: the annotation data-block and dependency graph

**Type:**

list[Callable[[[bpy.types.GreasePencil](bpy.types.GreasePencil.md#bpy.types.GreasePencil "bpy.types.GreasePencil"), [bpy.types.Depsgraph](bpy.types.Depsgraph.md#bpy.types.Depsgraph "bpy.types.Depsgraph")], None]]

<a id="bpy.app.handlers.blend_import_post"></a>

### bpy.app.handlers.blend_import_post

on linking or appending data (after). Accepts one argument: a BlendImportContext

**Type:**

list[Callable[[[bpy.types.BlendImportContext](bpy.types.BlendImportContext.md#bpy.types.BlendImportContext "bpy.types.BlendImportContext")], None]]

<a id="bpy.app.handlers.blend_import_pre"></a>

### bpy.app.handlers.blend_import_pre

on linking or appending data (before). Accepts one argument: a BlendImportContext

**Type:**

list[Callable[[[bpy.types.BlendImportContext](bpy.types.BlendImportContext.md#bpy.types.BlendImportContext "bpy.types.BlendImportContext")], None]]

<a id="bpy.app.handlers.composite_cancel"></a>

### bpy.app.handlers.composite_cancel

on a compositing background job (cancel). Accepts one argument: the scene data-block

**Type:**

list[Callable[[[bpy.types.Scene](bpy.types.Scene.md#bpy.types.Scene "bpy.types.Scene")], None]]

<a id="bpy.app.handlers.composite_post"></a>

### bpy.app.handlers.composite_post

on a compositing background job (after). Accepts one argument: the scene data-block

**Type:**

list[Callable[[[bpy.types.Scene](bpy.types.Scene.md#bpy.types.Scene "bpy.types.Scene")], None]]

<a id="bpy.app.handlers.composite_pre"></a>

### bpy.app.handlers.composite_pre

on a compositing background job (before). Accepts one argument: the scene data-block

**Type:**

list[Callable[[[bpy.types.Scene](bpy.types.Scene.md#bpy.types.Scene "bpy.types.Scene")], None]]

<a id="bpy.app.handlers.depsgraph_update_post"></a>

### bpy.app.handlers.depsgraph_update_post

on depsgraph update (post). Accepts one or two arguments: The scene data-block, and optionally the dependency graph being updated

**Type:**

list[Callable[[[bpy.types.Scene](bpy.types.Scene.md#bpy.types.Scene "bpy.types.Scene"), [bpy.types.Depsgraph](bpy.types.Depsgraph.md#bpy.types.Depsgraph "bpy.types.Depsgraph")], None] | Callable[[[bpy.types.Scene](bpy.types.Scene.md#bpy.types.Scene "bpy.types.Scene")], None]]

<a id="bpy.app.handlers.depsgraph_update_pre"></a>

### bpy.app.handlers.depsgraph_update_pre

on depsgraph update (pre). Accepts one or two arguments: The scene data-block, and optionally the dependency graph being updated

**Type:**

list[Callable[[[bpy.types.Scene](bpy.types.Scene.md#bpy.types.Scene "bpy.types.Scene"), [bpy.types.Depsgraph](bpy.types.Depsgraph.md#bpy.types.Depsgraph "bpy.types.Depsgraph")], None] | Callable[[[bpy.types.Scene](bpy.types.Scene.md#bpy.types.Scene "bpy.types.Scene")], None]]

<a id="bpy.app.handlers.exit_pre"></a>

### bpy.app.handlers.exit_pre

just before Blender shuts down, while all data is still valid. Accepts one boolean argument. True indicates either that a user has been using Blender and exited, or that Blender is exiting in a circumstance that should be treated as if that were the case. False indicates that Blender is running in background mode, or is exiting due to failed command line arguments, etc.

**Type:**

list[Callable[[bool], None]]

<a id="bpy.app.handlers.frame_change_post"></a>

### bpy.app.handlers.frame_change_post

Called after frame change for playback and rendering, after the data has been evaluated for the new frame. Accepts one or two arguments: The scene data-block, and optionally the dependency graph being updated

**Type:**

list[Callable[[[bpy.types.Scene](bpy.types.Scene.md#bpy.types.Scene "bpy.types.Scene"), [bpy.types.Depsgraph](bpy.types.Depsgraph.md#bpy.types.Depsgraph "bpy.types.Depsgraph")], None] | Callable[[[bpy.types.Scene](bpy.types.Scene.md#bpy.types.Scene "bpy.types.Scene")], None]]

<a id="bpy.app.handlers.frame_change_pre"></a>

### bpy.app.handlers.frame_change_pre

Called when a frame change is triggered for playback and rendering, before any data is evaluated for the new frame. This makes it possible to change data and relations (for example swap an object to another mesh) for the new frame. Note that this handler is **not** to be used as ‘before the frame changes’ event. The dependency graph is not available in this handler, as data and relations may have been altered and the dependency graph has not yet been updated for that. Accepts one or two arguments: The scene data-block, and optionally the dependency graph being updated

**Type:**

list[Callable[[[bpy.types.Scene](bpy.types.Scene.md#bpy.types.Scene "bpy.types.Scene"), [bpy.types.Depsgraph](bpy.types.Depsgraph.md#bpy.types.Depsgraph "bpy.types.Depsgraph")], None] | Callable[[[bpy.types.Scene](bpy.types.Scene.md#bpy.types.Scene "bpy.types.Scene")], None]]

<a id="bpy.app.handlers.load_factory_preferences_post"></a>

### bpy.app.handlers.load_factory_preferences_post

on loading factory preferences (after)

**Type:**

list[Callable[[], None]]

<a id="bpy.app.handlers.load_factory_startup_post"></a>

### bpy.app.handlers.load_factory_startup_post

on loading factory startup (after)

**Type:**

list[Callable[[], None]]

<a id="bpy.app.handlers.load_post"></a>

### bpy.app.handlers.load_post

on loading a new blend file (after). Accepts one argument: the file being loaded, an empty string for the startup-file.

**Type:**

list[Callable[[str], None]]

<a id="bpy.app.handlers.load_post_fail"></a>

### bpy.app.handlers.load_post_fail

on failure to load a new blend file (after). Accepts one argument: the file being loaded, an empty string for the startup-file.

**Type:**

list[Callable[[str], None]]

<a id="bpy.app.handlers.load_pre"></a>

### bpy.app.handlers.load_pre

on loading a new blend file (before). Accepts one argument: the file being loaded, an empty string for the startup-file.

**Type:**

list[Callable[[str], None]]

<a id="bpy.app.handlers.object_bake_cancel"></a>

### bpy.app.handlers.object_bake_cancel

on canceling a bake job; will be called in the main thread. Accepts one argument: the object data-block being baked

**Type:**

list[Callable[[[bpy.types.Object](bpy.types.Object.md#bpy.types.Object "bpy.types.Object")], None]]

<a id="bpy.app.handlers.object_bake_complete"></a>

### bpy.app.handlers.object_bake_complete

on completing a bake job; will be called in the main thread. Accepts one argument: the object data-block being baked

**Type:**

list[Callable[[[bpy.types.Object](bpy.types.Object.md#bpy.types.Object "bpy.types.Object")], None]]

<a id="bpy.app.handlers.object_bake_pre"></a>

### bpy.app.handlers.object_bake_pre

before starting a bake job. Accepts one argument: the object data-block being baked

**Type:**

list[Callable[[[bpy.types.Object](bpy.types.Object.md#bpy.types.Object "bpy.types.Object")], None]]

<a id="bpy.app.handlers.redo_post"></a>

### bpy.app.handlers.redo_post

on loading a redo step (after). Accepts one argument: the scene data-block

**Type:**

list[Callable[[[bpy.types.Scene](bpy.types.Scene.md#bpy.types.Scene "bpy.types.Scene")], None]]

<a id="bpy.app.handlers.redo_pre"></a>

### bpy.app.handlers.redo_pre

on loading a redo step (before). Accepts one argument: the scene data-block

**Type:**

list[Callable[[[bpy.types.Scene](bpy.types.Scene.md#bpy.types.Scene "bpy.types.Scene")], None]]

<a id="bpy.app.handlers.render_cancel"></a>

### bpy.app.handlers.render_cancel

on canceling a render job. Accepts one argument: the scene data-block being rendered

**Type:**

list[Callable[[[bpy.types.Scene](bpy.types.Scene.md#bpy.types.Scene "bpy.types.Scene")], None]]

<a id="bpy.app.handlers.render_complete"></a>

### bpy.app.handlers.render_complete

on completion of render job. Accepts one argument: the scene data-block being rendered

**Type:**

list[Callable[[[bpy.types.Scene](bpy.types.Scene.md#bpy.types.Scene "bpy.types.Scene")], None]]

<a id="bpy.app.handlers.render_init"></a>

### bpy.app.handlers.render_init

on initialization of a render job. Accepts one argument: the scene data-block being rendered

**Type:**

list[Callable[[[bpy.types.Scene](bpy.types.Scene.md#bpy.types.Scene "bpy.types.Scene")], None]]

<a id="bpy.app.handlers.render_post"></a>

### bpy.app.handlers.render_post

on render (after). Accepts one argument: the scene data-block being rendered

**Type:**

list[Callable[[[bpy.types.Scene](bpy.types.Scene.md#bpy.types.Scene "bpy.types.Scene")], None]]

<a id="bpy.app.handlers.render_pre"></a>

### bpy.app.handlers.render_pre

on render (before). Accepts one argument: the scene data-block being rendered

**Type:**

list[Callable[[[bpy.types.Scene](bpy.types.Scene.md#bpy.types.Scene "bpy.types.Scene")], None]]

<a id="bpy.app.handlers.render_stats"></a>

### bpy.app.handlers.render_stats

on printing render statistics. Accepts one argument: the render progress as a string containing current frame, current sample, render time and saving time.

**Type:**

list[Callable[[str], None]]

<a id="bpy.app.handlers.render_write"></a>

### bpy.app.handlers.render_write

on writing a render frame (directly after the frame is written). Accepts one argument: the scene data-block being rendered

**Type:**

list[Callable[[[bpy.types.Scene](bpy.types.Scene.md#bpy.types.Scene "bpy.types.Scene")], None]]

<a id="bpy.app.handlers.save_post"></a>

### bpy.app.handlers.save_post

on saving a blend file (after). Accepts one argument: the file being saved, an empty string for the startup-file.

**Type:**

list[Callable[[str], None]]

<a id="bpy.app.handlers.save_post_fail"></a>

### bpy.app.handlers.save_post_fail

on failure to save a blend file (after). Accepts one argument: the file being saved, an empty string for the startup-file.

**Type:**

list[Callable[[str], None]]

<a id="bpy.app.handlers.save_pre"></a>

### bpy.app.handlers.save_pre

on saving a blend file (before). Accepts one argument: the file being saved, an empty string for the startup-file.

**Type:**

list[Callable[[str], None]]

<a id="bpy.app.handlers.translation_update_post"></a>

### bpy.app.handlers.translation_update_post

on translation settings update

**Type:**

list[Callable[[], None]]

<a id="bpy.app.handlers.undo_post"></a>

### bpy.app.handlers.undo_post

on loading an undo step (after). Accepts one argument: the scene data-block

**Type:**

list[Callable[[[bpy.types.Scene](bpy.types.Scene.md#bpy.types.Scene "bpy.types.Scene")], None]]

<a id="bpy.app.handlers.undo_pre"></a>

### bpy.app.handlers.undo_pre

on loading an undo step (before). Accepts one argument: the scene data-block

**Type:**

list[Callable[[[bpy.types.Scene](bpy.types.Scene.md#bpy.types.Scene "bpy.types.Scene")], None]]

<a id="bpy.app.handlers.version_update"></a>

### bpy.app.handlers.version_update

on ending the versioning code

**Type:**

list[Callable[[], None]]

<a id="bpy.app.handlers.xr_session_start_pre"></a>

### bpy.app.handlers.xr_session_start_pre

on starting an xr session (before)

**Type:**

list[Callable[[], None]]

<a id="bpy.app.handlers.persistent"></a>

### bpy.app.handlers.persistent

Function decorator for callback functions not to be removed when loading new files

**Type:**

type
