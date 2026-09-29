<!-- source: Blender Python API reference 5.2 / bpy.ops.html -->

<a id="module-bpy.ops"></a>

# Operators (bpy.ops)

<a id="calling-operators"></a>

## Calling Operators

Provides Python access to calling operators, this includes operators written in
C++, Python or macros.

Only keyword arguments can be used to pass operator properties.

Operators don’t have return values as you might expect,
instead they return a set() which is made up of:
`{'RUNNING_MODAL', 'CANCELLED', 'FINISHED', 'PASS_THROUGH'}`.
Common return values are `{'FINISHED'}` and `{'CANCELLED'}`, the latter
meaning that the operator execution was aborted without making any changes or
saving an undo history entry.

If operator was cancelled but there wasn’t any reports from it with `{'ERROR'}` type,
it will just return `{'CANCELLED'}` without raising any exceptions.
However, if there are error reports, a `RuntimeError` will be raised
after the operator finishes execution, including all error report messages,
regardless of the return status (even if it was `{'FINISHED'}`).

Calling an operator in the wrong context will raise a `RuntimeError`,
there is a poll() method to avoid this problem.

Note that the operator ID (bl_idname) in this example is `mesh.subdivide`,
`bpy.ops` is just the access path for Python.

<a id="keywords-and-positional-arguments"></a>

### Keywords and Positional Arguments

For calling operators keywords are used for operator properties and
positional arguments are used to define how the operator is called.

There are 2 optional positional arguments (documented in detail below).

```python
bpy.ops.test.operator(execution_context, undo)
```

- execution_context - `str` (enum).
- undo - `bool` type.

Each of these arguments is optional, but must be given in the order above.

```python
import bpy

# Calling an operator.
bpy.ops.mesh.subdivide(number_cuts=3, smoothness=0.5)

# Check poll() to avoid exception.
if bpy.ops.object.mode_set.poll():
    bpy.ops.object.mode_set(mode='EDIT')
```

<a id="overriding-context"></a>

## Overriding Context

It is possible to override context members that the operator sees, so that they
act on specified rather than the selected or active data, or to execute an
operator in the different part of the user interface.

The context overrides are passed in as keyword arguments,
with keywords matching the context member names in `bpy.context`.
For example to override `bpy.context.active_object`,
you would pass `active_object=object` to [`bpy.types.Context.temp_override`](bpy.types.Context.md#bpy.types.Context.temp_override "bpy.types.Context.temp_override").

> **Note:**
>
> You will nearly always want to use a copy of the actual current context as basis
> (otherwise, you’ll have to find and gather all needed data yourself).

> **Note:**
>
> Context members are names which Blender uses for data access,
> overrides do not extend to overriding methods or any Python specific functionality.

```python
# Remove all objects in scene rather than the selected ones.
import bpy
from bpy import context
context_override = context.copy()
context_override["selected_objects"] = list(context.scene.objects)
with context.temp_override(**context_override):
    bpy.ops.object.delete()
```

<a id="execution-context"></a>

## Execution Context

When calling an operator you may want to pass the execution context.

This determines the context that is given for the operator to run in, and whether
invoke() is called or only execute().

`EXEC_DEFAULT` is used by default, running only the `execute()` method, but you may
want the operator to take user interaction with `INVOKE_DEFAULT` which will also
call invoke() if existing.

The execution context is one of:

- `INVOKE_DEFAULT`
- `INVOKE_REGION_WIN`
- `INVOKE_REGION_CHANNELS`
- `INVOKE_REGION_PREVIEW`
- `INVOKE_AREA`
- `INVOKE_SCREEN`
- `EXEC_DEFAULT`
- `EXEC_REGION_WIN`
- `EXEC_REGION_CHANNELS`
- `EXEC_REGION_PREVIEW`
- `EXEC_AREA`
- `EXEC_SCREEN`

```python
# Collection add popup.
import bpy
bpy.ops.object.collection_instance_add('INVOKE_DEFAULT')
```

It is also possible to run an operator in a particular part of the user
interface. For this we need to pass the window, area and sometimes a region.

```python
# Maximize 3d view in all windows.
import bpy
from bpy import context

for window in context.window_manager.windows:
    screen = window.screen
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            with context.temp_override(window=window, area=area):
                bpy.ops.screen.screen_full_area()
            break
```

Submodules

- [Action Operators](bpy.ops.action.md)
- [Anim Operators](bpy.ops.anim.md)
- [Armature Operators](bpy.ops.armature.md)
- [Asset Operators](bpy.ops.asset.md)
- [Boid Operators](bpy.ops.boid.md)
- [Brush Operators](bpy.ops.brush.md)
- [Buttons Operators](bpy.ops.buttons.md)
- [Cachefile Operators](bpy.ops.cachefile.md)
- [Camera Operators](bpy.ops.camera.md)
- [Clip Operators](bpy.ops.clip.md)
- [Cloth Operators](bpy.ops.cloth.md)
- [Collection Operators](bpy.ops.collection.md)
- [Console Operators](bpy.ops.console.md)
- [Constraint Operators](bpy.ops.constraint.md)
- [Curve Operators](bpy.ops.curve.md)
- [Curves Operators](bpy.ops.curves.md)
- [Cycles Operators](bpy.ops.cycles.md)
- [Dpaint Operators](bpy.ops.dpaint.md)
- [Ed Operators](bpy.ops.ed.md)
- [Export Anim Operators](bpy.ops.export_anim.md)
- [Export Scene Operators](bpy.ops.export_scene.md)
- [Extensions Operators](bpy.ops.extensions.md)
- [File Operators](bpy.ops.file.md)
- [Fluid Operators](bpy.ops.fluid.md)
- [Font Operators](bpy.ops.font.md)
- [Geometry Operators](bpy.ops.geometry.md)
- [Gizmogroup Operators](bpy.ops.gizmogroup.md)
- [Gpencil Operators](bpy.ops.gpencil.md)
- [Graph Operators](bpy.ops.graph.md)
- [Grease Pencil Operators](bpy.ops.grease_pencil.md)
- [Image Operators](bpy.ops.image.md)
- [Import Anim Operators](bpy.ops.import_anim.md)
- [Import Curve Operators](bpy.ops.import_curve.md)
- [Import Scene Operators](bpy.ops.import_scene.md)
- [Info Operators](bpy.ops.info.md)
- [Lattice Operators](bpy.ops.lattice.md)
- [Marker Operators](bpy.ops.marker.md)
- [Mask Operators](bpy.ops.mask.md)
- [Material Operators](bpy.ops.material.md)
- [Mball Operators](bpy.ops.mball.md)
- [Mesh Operators](bpy.ops.mesh.md)
- [Nla Operators](bpy.ops.nla.md)
- [Node Operators](bpy.ops.node.md)
- [Object Operators](bpy.ops.object.md)
- [Outliner Operators](bpy.ops.outliner.md)
- [Paint Operators](bpy.ops.paint.md)
- [Paintcurve Operators](bpy.ops.paintcurve.md)
- [Palette Operators](bpy.ops.palette.md)
- [Particle Operators](bpy.ops.particle.md)
- [Pointcloud Operators](bpy.ops.pointcloud.md)
- [Pose Operators](bpy.ops.pose.md)
- [Poselib Operators](bpy.ops.poselib.md)
- [Preferences Operators](bpy.ops.preferences.md)
- [Ptcache Operators](bpy.ops.ptcache.md)
- [Render Operators](bpy.ops.render.md)
- [Rigidbody Operators](bpy.ops.rigidbody.md)
- [Scene Operators](bpy.ops.scene.md)
- [Screen Operators](bpy.ops.screen.md)
- [Script Operators](bpy.ops.script.md)
- [Sculpt Operators](bpy.ops.sculpt.md)
- [Sculpt Curves Operators](bpy.ops.sculpt_curves.md)
- [Sequencer Operators](bpy.ops.sequencer.md)
- [Sound Operators](bpy.ops.sound.md)
- [Spreadsheet Operators](bpy.ops.spreadsheet.md)
- [Surface Operators](bpy.ops.surface.md)
- [Text Operators](bpy.ops.text.md)
- [Text Editor Operators](bpy.ops.text_editor.md)
- [Texture Operators](bpy.ops.texture.md)
- [Transform Operators](bpy.ops.transform.md)
- [Ui Operators](bpy.ops.ui.md)
- [Uilist Operators](bpy.ops.uilist.md)
- [Uv Operators](bpy.ops.uv.md)
- [View2D Operators](bpy.ops.view2d.md)
- [View3D Operators](bpy.ops.view3d.md)
- [Wm Operators](bpy.ops.wm.md)
- [Workspace Operators](bpy.ops.workspace.md)
- [World Operators](bpy.ops.world.md)
