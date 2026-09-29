<!-- source: Blender Python API reference 5.2 / bpy.types.Window.html -->

<a id="window-bpy-struct"></a>

# Window(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.Window"></a>

### class bpy.types.Window(bpy_struct)

Open window

<a id="bpy.types.Window.height"></a>

#### bpy.types.Window.height

Window height (in [0, 32767], default 0, readonly)

**Type:**

int

<a id="bpy.types.Window.modal_operators"></a>

#### bpy.types.Window.modal_operators

A list of currently running modal operators (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`Operator`](bpy.types.Operator.md#bpy.types.Operator "bpy.types.Operator")]

<a id="bpy.types.Window.parent"></a>

#### bpy.types.Window.parent

Active workspace and scene follow this window (readonly)

**Type:**

[`Window`](#bpy.types.Window "bpy.types.Window") | None

<a id="bpy.types.Window.scene"></a>

#### bpy.types.Window.scene

Active scene to be edited in the window (never None)

**Type:**

[`Scene`](bpy.types.Scene.md#bpy.types.Scene "bpy.types.Scene")

<a id="bpy.types.Window.screen"></a>

#### bpy.types.Window.screen

Active workspace screen showing in the window (never None)

**Type:**

[`Screen`](bpy.types.Screen.md#bpy.types.Screen "bpy.types.Screen")

<a id="bpy.types.Window.stereo_3d_display"></a>

#### bpy.types.Window.stereo_3d_display

Settings for stereo 3D display (readonly, never None)

**Type:**

[`Stereo3dDisplay`](bpy.types.Stereo3dDisplay.md#bpy.types.Stereo3dDisplay "bpy.types.Stereo3dDisplay")

<a id="bpy.types.Window.support_hdr_color"></a>

#### bpy.types.Window.support_hdr_color

The window has a HDR graphics buffer that wide gamut and high dynamic range colors can be written to, in extended sRGB color space. (default False, readonly)

**Type:**

bool

<a id="bpy.types.Window.view_layer"></a>

#### bpy.types.Window.view_layer

The active workspace view layer showing in the window (never None)

**Type:**

[`ViewLayer`](bpy.types.ViewLayer.md#bpy.types.ViewLayer "bpy.types.ViewLayer")

<a id="bpy.types.Window.width"></a>

#### bpy.types.Window.width

Window width (in [0, 32767], default 0, readonly)

**Type:**

int

<a id="bpy.types.Window.workspace"></a>

#### bpy.types.Window.workspace

Active workspace showing in the window (never None)

**Type:**

[`WorkSpace`](bpy.types.WorkSpace.md#bpy.types.WorkSpace "bpy.types.WorkSpace")

<a id="bpy.types.Window.x"></a>

#### bpy.types.Window.x

Horizontal location of the window (in [-32768, 32767], default 0, readonly)

**Type:**

int

<a id="bpy.types.Window.y"></a>

#### bpy.types.Window.y

Vertical location of the window (in [-32768, 32767], default 0, readonly)

**Type:**

int

<a id="bpy.types.Window.cursor_warp"></a>

#### bpy.types.Window.cursor_warp(x, y)

Set the cursor position

**Parameters:**

- **x** (int) – (in [-inf, inf])
- **y** (int) – (in [-inf, inf])

<a id="bpy.types.Window.cursor_set"></a>

#### bpy.types.Window.cursor_set(cursor)

Set the cursor

**Parameters:**

**cursor** (Literal[[Window Cursor Items](bpy_types_enum_items/window_cursor_items.md#rna-enum-window-cursor-items)]) – cursor

<a id="bpy.types.Window.cursor_modal_set"></a>

#### bpy.types.Window.cursor_modal_set(cursor)

Set the cursor, so the previous cursor can be restored

**Parameters:**

**cursor** (Literal[[Window Cursor Items](bpy_types_enum_items/window_cursor_items.md#rna-enum-window-cursor-items)]) – cursor

<a id="bpy.types.Window.cursor_modal_restore"></a>

#### bpy.types.Window.cursor_modal_restore()

Restore the previous cursor after calling `cursor_modal_set`

<a id="bpy.types.Window.event_simulate"></a>

#### bpy.types.Window.event_simulate(type, value, *, unicode='', x=0, y=0, shift=False, ctrl=False, alt=False, oskey=False, hyper=False)

event_simulate

**Parameters:**

- **type** (Literal[[Event Type Items](bpy_types_enum_items/event_type_items.md#rna-enum-event-type-items)]) – Type
- **value** (Literal[[Event Value Items](bpy_types_enum_items/event_value_items.md#rna-enum-event-value-items)]) – Value
- **unicode** (str) – (optional)
- **x** (int) – (in [-inf, inf], optional)
- **y** (int) – (in [-inf, inf], optional)
- **shift** (bool) – Shift, (optional)
- **ctrl** (bool) – Ctrl, (optional)
- **alt** (bool) – Alt, (optional)
- **oskey** (bool) – OS Key, (optional)
- **hyper** (bool) – Hyper, (optional)

**Returns:**

Item, Added key map item

**Return type:**

[`Event`](bpy.types.Event.md#bpy.types.Event "bpy.types.Event")

<a id="bpy.types.Window.find_playing_scene"></a>

#### bpy.types.Window.find_playing_scene(*, scrub=False)

find_playing_scene

**Parameters:**

**scrub** (bool) – Scrubbing, Check if time in the scene is being scrubbed (optional)

**Returns:**

Scene, Scene that is currently playing

**Return type:**

[`Scene`](bpy.types.Scene.md#bpy.types.Scene "bpy.types.Scene")

<a id="bpy.types.Window.bl_rna_get_subclass"></a>

#### classmethod bpy.types.Window.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.Window.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.Window.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="bpy.types.Window.screenshot"></a>

#### bpy.types.Window.screenshot(*, region=None, use_alpha=False)

Capture the windows pixel data.

**Parameters:**

- **region** (tuple[tuple[int, int], tuple[int, int]] | None) – The region to capture, or `None` to capture all.
  Each int pair represents a pixel coordinate (the end value is not inclusive, matching Python slicing): ((min_x, min_y), (max_x, max_y))
- **use_alpha** (bool) – When false the alpha channel is fully opaque. Otherwise alpha values from the window’s frame-buffer are returned as-is.

**Returns:**

A read-only `memoryview` of shape `(height, width, 4)` and format `'B'`, viewing the captured RGBA pixels (rows ordered from bottom to top).

**Return type:**

memoryview

**Save 3D Viewport to a PNG**

Capture the 3D viewport’s main region from the current window
and write it to a PNG file using [`imbuf`](imbuf.md#module-imbuf "imbuf").

```python
import bpy
import imbuf

window = bpy.context.window

# Locate the 3D viewport (if any).
region = None
for area in window.screen.areas:
    if area.type == 'VIEW_3D':
        for region_iter in area.regions:
            if region_iter.type == 'WINDOW':
                region = region_iter
                break
        break

if region is not None:
    # The end coordinate is not inclusive, like Python slicing.
    region_rect = (
        (region.x, region.y),
        (region.x + region.width, region.y + region.height),
    )
    pixels = window.screenshot(region=region_rect)
    height, width = pixels.shape[0], pixels.shape[1]

    ibuf = imbuf.new((width, height))
    ibuf.file_type = 'PNG'
    with ibuf.with_buffer(write=True) as buf:
        # The cast produces a zero-copy 1-D view of the same bytes.
        # Currently only 1-D copies are supported by Python.
        buf.cast('B')[:] = pixels.cast('B')

    imbuf.write(ibuf, filepath="/tmp/viewport.png")
```

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
| - [`Context.window`](bpy.types.Context.md#bpy.types.Context.window "bpy.types.Context.window") - [`Window.parent`](#bpy.types.Window.parent "bpy.types.Window.parent") - [`WindowManager.event_timer_add`](bpy.types.WindowManager.md#bpy.types.WindowManager.event_timer_add "bpy.types.WindowManager.event_timer_add") | - [`WindowManager.windows`](bpy.types.WindowManager.md#bpy.types.WindowManager.windows "bpy.types.WindowManager.windows") - [`Windows.find_playing`](bpy.types.Windows.md#bpy.types.Windows.find_playing "bpy.types.Windows.find_playing") |
