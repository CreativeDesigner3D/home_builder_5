<!-- source: Blender Python API reference 5.2 / bpy.ops.view2d.html -->

<a id="module-bpy.ops.view2d"></a>

# View2D Operators

<a id="bpy.ops.view2d.edge_pan"></a>

### bpy.ops.view2d.edge_pan(*, inside_padding=1.0, outside_padding=0.0, speed_ramp=1.0, max_speed=500.0, delay=1.0, zoom_influence=0.0)

Pan the view when the mouse is held at an edge

**Parameters:**

- **inside_padding** (float) – Inside Padding, Inside distance in UI units from the edge of the region within which to start panning (in [0, 100], optional)
- **outside_padding** (float) – Outside Padding, Outside distance in UI units from the edge of the region at which to stop panning (in [0, 100], optional)
- **speed_ramp** (float) – Speed Ramp, Width of the zone in UI units where speed increases with distance from the edge (in [0, 100], optional)
- **max_speed** (float) – Max Speed, Maximum speed in UI units per second (in [0, 10000], optional)
- **delay** (float) – Delay, Delay in seconds before maximum speed is reached (in [0, 10], optional)
- **zoom_influence** (float) – Zoom Influence, Influence of the zoom factor on scroll speed (in [0, 1], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view2d.ndof"></a>

### bpy.ops.view2d.ndof()

Use a 3D mouse device to pan/zoom the view

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view2d.pan"></a>

### bpy.ops.view2d.pan(*, deltax=0, deltay=0)

Pan the view

**Parameters:**

- **deltax** (int) – Delta X, (in [-inf, inf], optional)
- **deltay** (int) – Delta Y, (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view2d.reset"></a>

### bpy.ops.view2d.reset()

Reset the view

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view2d.scroll_down"></a>

### bpy.ops.view2d.scroll_down(*, deltax=0, deltay=0, page=False)

Scroll the view down

**Parameters:**

- **deltax** (int) – Delta X, (in [-inf, inf], optional)
- **deltay** (int) – Delta Y, (in [-inf, inf], optional)
- **page** (bool) – Page, Scroll down one page (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view2d.scroll_left"></a>

### bpy.ops.view2d.scroll_left(*, deltax=0, deltay=0)

Scroll the view left

**Parameters:**

- **deltax** (int) – Delta X, (in [-inf, inf], optional)
- **deltay** (int) – Delta Y, (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view2d.scroll_right"></a>

### bpy.ops.view2d.scroll_right(*, deltax=0, deltay=0)

Scroll the view right

**Parameters:**

- **deltax** (int) – Delta X, (in [-inf, inf], optional)
- **deltay** (int) – Delta Y, (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view2d.scroll_up"></a>

### bpy.ops.view2d.scroll_up(*, deltax=0, deltay=0, page=False)

Scroll the view up

**Parameters:**

- **deltax** (int) – Delta X, (in [-inf, inf], optional)
- **deltay** (int) – Delta Y, (in [-inf, inf], optional)
- **page** (bool) – Page, Scroll up one page (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view2d.scroller_activate"></a>

### bpy.ops.view2d.scroller_activate()

Scroll view by mouse click and drag

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view2d.smoothview"></a>

### bpy.ops.view2d.smoothview(*, xmin=0, xmax=0, ymin=0, ymax=0, wait_for_input=True)

Undocumented, consider [contributing](https://developer.blender.org/).

**Parameters:**

- **xmin** (int) – X Min, (in [-inf, inf], optional)
- **xmax** (int) – X Max, (in [-inf, inf], optional)
- **ymin** (int) – Y Min, (in [-inf, inf], optional)
- **ymax** (int) – Y Max, (in [-inf, inf], optional)
- **wait_for_input** (bool) – Wait for Input, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view2d.zoom"></a>

### bpy.ops.view2d.zoom(*, deltax=0.0, deltay=0.0, use_cursor_init=True)

Zoom in/out the view

**Parameters:**

- **deltax** (float) – Delta X, (in [-inf, inf], optional)
- **deltay** (float) – Delta Y, (in [-inf, inf], optional)
- **use_cursor_init** (bool) – Use Mouse Position, Allow the initial mouse position to be used (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view2d.zoom_border"></a>

### bpy.ops.view2d.zoom_border(*, xmin=0, xmax=0, ymin=0, ymax=0, wait_for_input=True, zoom_out=False)

Zoom in the view to the nearest item contained in the border

**Parameters:**

- **xmin** (int) – X Min, (in [-inf, inf], optional)
- **xmax** (int) – X Max, (in [-inf, inf], optional)
- **ymin** (int) – Y Min, (in [-inf, inf], optional)
- **ymax** (int) – Y Max, (in [-inf, inf], optional)
- **wait_for_input** (bool) – Wait for Input, (optional)
- **zoom_out** (bool) – Zoom Out, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view2d.zoom_in"></a>

### bpy.ops.view2d.zoom_in(*, zoomfacx=0.0375, zoomfacy=0.0375)

Zoom in the view

**Parameters:**

- **zoomfacx** (float) – Zoom Factor X, (in [-inf, inf], optional)
- **zoomfacy** (float) – Zoom Factor Y, (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view2d.zoom_out"></a>

### bpy.ops.view2d.zoom_out(*, zoomfacx=-0.0375, zoomfacy=-0.0375)

Zoom out the view

**Parameters:**

- **zoomfacx** (float) – Zoom Factor X, (in [-inf, inf], optional)
- **zoomfacy** (float) – Zoom Factor Y, (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]
