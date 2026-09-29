<!-- source: Blender Python API reference 5.2 / bpy.ops.marker.html -->

<a id="module-bpy.ops.marker"></a>

# Marker Operators

<a id="bpy.ops.marker.add"></a>

### bpy.ops.marker.add()

Add a new time marker

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.marker.camera_bind"></a>

### bpy.ops.marker.camera_bind()

Bind the selected camera to a marker on the current frame

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.marker.delete"></a>

### bpy.ops.marker.delete(*, confirm=True)

Delete selected time marker(s)

**Parameters:**

**confirm** (bool) – Confirm, Prompt for confirmation (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.marker.duplicate"></a>

### bpy.ops.marker.duplicate(*, frames=0)

Duplicate selected time marker(s)

**Parameters:**

**frames** (int) – Frames, (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.marker.make_links_scene"></a>

### bpy.ops.marker.make_links_scene(*, scene='')

Copy selected markers to another scene

**Parameters:**

**scene** (str) – Scene, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.marker.move"></a>

### bpy.ops.marker.move(*, frames=0, tweak=False)

Move selected time marker(s)

**Parameters:**

- **frames** (int) – Frames, (in [-inf, inf], optional)
- **tweak** (bool) – Tweak, Operator has been activated using a click-drag event (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.marker.rename"></a>

### bpy.ops.marker.rename(*, name='RenamedMarker')

Rename first selected time marker

**Parameters:**

**name** (str) – Name, New name for marker (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.marker.select"></a>

### bpy.ops.marker.select(*, wait_to_deselect_others=False, use_select_on_click=False, mouse_x=0, mouse_y=0, extend=False, camera=False)

Select time marker(s)

**Parameters:**

- **wait_to_deselect_others** (bool) – Wait to Deselect Others, (optional)
- **use_select_on_click** (bool) – Act on Click, Instead of selecting on mouse press, wait to see if there’s drag event. Otherwise select on mouse release (optional)
- **mouse_x** (int) – Mouse X, (in [-inf, inf], optional)
- **mouse_y** (int) – Mouse Y, (in [-inf, inf], optional)
- **extend** (bool) – Extend, Extend the selection (optional)
- **camera** (bool) – Camera, Select the camera (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.marker.select_all"></a>

### bpy.ops.marker.select_all(*, action='TOGGLE')

Change selection of all time markers

**Parameters:**

**action** (Literal['TOGGLE', 'SELECT', 'DESELECT', 'INVERT']) –

Action, Selection action to execute (optional)

- `TOGGLE`
  Toggle – Toggle selection for all elements.
- `SELECT`
  Select – Select all elements.
- `DESELECT`
  Deselect – Deselect all elements.
- `INVERT`
  Invert – Invert selection of all elements.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.marker.select_box"></a>

### bpy.ops.marker.select_box(*, xmin=0, xmax=0, ymin=0, ymax=0, wait_for_input=True, mode='SET', tweak=False)

Select all time markers using box selection

**Parameters:**

- **xmin** (int) – X Min, (in [-inf, inf], optional)
- **xmax** (int) – X Max, (in [-inf, inf], optional)
- **ymin** (int) – Y Min, (in [-inf, inf], optional)
- **ymax** (int) – Y Max, (in [-inf, inf], optional)
- **wait_for_input** (bool) – Wait for Input, (optional)
- **mode** (Literal['SET', 'ADD', 'SUB']) –

  Mode, (optional)

  - `SET`
    Set – Set a new selection.
  - `ADD`
    Extend – Extend existing selection.
  - `SUB`
    Subtract – Subtract existing selection.
- **tweak** (bool) – Tweak, Operator has been activated using a click-drag event (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.marker.select_leftright"></a>

### bpy.ops.marker.select_leftright(*, mode='LEFT', extend=False)

Select markers on and left/right of the current frame

**Parameters:**

- **mode** (Literal['LEFT', 'RIGHT', 'CLICK_SIDE']) – Mode, (optional)
- **extend** (bool) – Extend Select, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]
