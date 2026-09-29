<!-- source: Blender Python API reference 5.2 / bpy.ops.action.html -->

<a id="module-bpy.ops.action"></a>

# Action Operators

<a id="bpy.ops.action.bake_keys"></a>

### bpy.ops.action.bake_keys()

Add keyframes on every frame between the selected keyframes

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.action.clean"></a>

### bpy.ops.action.clean(*, threshold=0.001, channels=False)

Simplify F-Curves by removing closely spaced keyframes

**Parameters:**

- **threshold** (float) – Threshold, (in [0, inf], optional)
- **channels** (bool) – Channels, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.action.clickselect"></a>

### bpy.ops.action.clickselect(*, wait_to_deselect_others=False, use_select_on_click=False, mouse_x=0, mouse_y=0, extend=False, deselect_all=False, column=False, channel=False)

Select keyframes by clicking on them

**Parameters:**

- **wait_to_deselect_others** (bool) – Wait to Deselect Others, (optional)
- **use_select_on_click** (bool) – Act on Click, Instead of selecting on mouse press, wait to see if there’s drag event. Otherwise select on mouse release (optional)
- **mouse_x** (int) – Mouse X, (in [-inf, inf], optional)
- **mouse_y** (int) – Mouse Y, (in [-inf, inf], optional)
- **extend** (bool) – Extend Select, Toggle keyframe selection instead of leaving newly selected keyframes only (optional)
- **deselect_all** (bool) – Deselect On Nothing, Deselect all when nothing under the cursor (optional)
- **column** (bool) – Column Select, Select all keyframes that occur on the same frame as the one under the mouse (optional)
- **channel** (bool) – Only Channel, Select all the keyframes in the channel under the mouse (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.action.copy"></a>

### bpy.ops.action.copy()

Copy selected keyframes to the internal clipboard

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.action.delete"></a>

### bpy.ops.action.delete(*, confirm=True)

Remove all selected keyframes

**Parameters:**

**confirm** (bool) – Confirm, Prompt for confirmation (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.action.duplicate"></a>

### bpy.ops.action.duplicate()

Make a copy of all selected keyframes

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.action.duplicate_move"></a>

### bpy.ops.action.duplicate_move(*, ACTION_OT_duplicate={}, TRANSFORM_OT_transform={})

Make a copy of all selected keyframes and move them

**Parameters:**

- **ACTION_OT_duplicate** (dict[str, Any]) – Duplicate Keyframes, Make a copy of all selected keyframes (optional, [`bpy.ops.action.duplicate()`](#bpy.ops.action.duplicate "bpy.ops.action.duplicate") keyword arguments)
- **TRANSFORM_OT_transform** (dict[str, Any]) – Transform, Transform selected items by mode type (optional, [`bpy.ops.transform.transform()`](bpy.ops.transform.md#bpy.ops.transform.transform "bpy.ops.transform.transform") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.action.easing_type"></a>

### bpy.ops.action.easing_type(*, type='AUTO')

Set easing type for the F-Curve segments starting from the selected keyframes

**Parameters:**

**type** (Literal[[Beztriple Interpolation Easing Items](bpy_types_enum_items/beztriple_interpolation_easing_items.md#rna-enum-beztriple-interpolation-easing-items)]) – Type, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.action.extrapolation_type"></a>

### bpy.ops.action.extrapolation_type(*, type='CONSTANT')

Set extrapolation mode for selected F-Curves

**Parameters:**

**type** (Literal['CONSTANT', 'LINEAR', 'MAKE_CYCLIC', 'CLEAR_CYCLIC']) –

Type, (optional)

- `CONSTANT`
  Constant Extrapolation – Values on endpoint keyframes are held.
- `LINEAR`
  Linear Extrapolation – Straight-line slope of end segments are extended past the endpoint keyframes.
- `MAKE_CYCLIC`
  Make Cyclic (F-Modifier) – Add Cycles F-Modifier if one does not exist already.
- `CLEAR_CYCLIC`
  Clear Cyclic (F-Modifier) – Remove Cycles F-Modifier if not needed anymore.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.action.frame_jump"></a>

### bpy.ops.action.frame_jump()

Set the current frame to the average frame value of selected keyframes

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.action.handle_type"></a>

### bpy.ops.action.handle_type(*, type='FREE')

Set type of handle for selected keyframes

**Parameters:**

**type** (Literal[[Keyframe Handle Type Items](bpy_types_enum_items/keyframe_handle_type_items.md#rna-enum-keyframe-handle-type-items)]) – Type, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.action.interpolation_type"></a>

### bpy.ops.action.interpolation_type(*, type='CONSTANT')

Set interpolation mode for the F-Curve segments starting from the selected keyframes

**Parameters:**

**type** (Literal[[Beztriple Interpolation Mode Items](bpy_types_enum_items/beztriple_interpolation_mode_items.md#rna-enum-beztriple-interpolation-mode-items)]) – Type, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.action.keyframe_insert"></a>

### bpy.ops.action.keyframe_insert(*, type='ALL')

Insert keyframes for the specified channels

**Parameters:**

**type** (Literal['ALL', 'SEL', 'GROUP']) – Type, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.action.keyframe_type"></a>

### bpy.ops.action.keyframe_type(*, type='KEYFRAME')

Set type of keyframe for the selected keyframes

**Parameters:**

**type** (Literal[[Beztriple Keyframe Type Items](bpy_types_enum_items/beztriple_keyframe_type_items.md#rna-enum-beztriple-keyframe-type-items)]) – Type, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.action.markers_make_local"></a>

### bpy.ops.action.markers_make_local()

Move selected scene markers to the active Action as local ‘pose’ markers

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.action.mirror"></a>

### bpy.ops.action.mirror(*, type='CFRA')

Flip selected keyframes over the selected mirror line

**Parameters:**

**type** (Literal['CFRA', 'MARKER', 'XAXIS']) –

Type, (optional)

- `CFRA`
  By Times Over Current Frame – Flip times of selected keyframes using the current frame as the mirror line.
- `MARKER`
  By Times Over First Selected Marker – Flip times of selected keyframes using the first selected marker as the reference point.
- `XAXIS`
  By Values Over Zero Value – Flip values of selected keyframes (i.e. negative values become positive, and vice versa).

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.action.new"></a>

### bpy.ops.action.new()

Create new action

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.action.paste"></a>

### bpy.ops.action.paste(*, offset='START', merge='MIX', flipped=False)

Paste keyframes from the internal clipboard for the selected channels, starting on the current frame

**Parameters:**

- **offset** (Literal[[Keyframe Paste Offset Items](bpy_types_enum_items/keyframe_paste_offset_items.md#rna-enum-keyframe-paste-offset-items)]) – Offset, Paste time offset of keys (optional)
- **merge** (Literal[[Keyframe Paste Merge Items](bpy_types_enum_items/keyframe_paste_merge_items.md#rna-enum-keyframe-paste-merge-items)]) – Type, Method of merging pasted keys and existing (optional)
- **flipped** (bool) – Flipped, Paste keyframes from mirrored bones if they exist (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.action.previewrange_set"></a>

### bpy.ops.action.previewrange_set()

Set Preview Range based on extents of selected Keyframes

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.action.push_down"></a>

### bpy.ops.action.push_down()

Push action down on to the NLA stack as a new strip

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.action.select_all"></a>

### bpy.ops.action.select_all(*, action='TOGGLE')

Toggle selection of all keyframes

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

<a id="bpy.ops.action.select_box"></a>

### bpy.ops.action.select_box(*, axis_range=False, xmin=0, xmax=0, ymin=0, ymax=0, wait_for_input=True, mode='SET', tweak=False)

Select all keyframes within the specified region

**Parameters:**

- **axis_range** (bool) – Axis Range, (optional)
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

<a id="bpy.ops.action.select_by_type"></a>

### bpy.ops.action.select_by_type(*, extend=True, type='KEYFRAME')

Select all keyframes of the given type

**Parameters:**

- **extend** (bool) – Extend Selection, Keeps the current selection and adds the given type to it. If disabled, only keys of the type will be selected (optional)
- **type** (Literal[[Beztriple Keyframe Type Items](bpy_types_enum_items/beztriple_keyframe_type_items.md#rna-enum-beztriple-keyframe-type-items)]) – Type, The type of keyframe to select (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.action.select_circle"></a>

### bpy.ops.action.select_circle(*, x=0, y=0, radius=25, wait_for_input=True, mode='SET')

Select keyframe points using circle selection

**Parameters:**

- **x** (int) – X, (in [-inf, inf], optional)
- **y** (int) – Y, (in [-inf, inf], optional)
- **radius** (int) – Radius, (in [1, inf], optional)
- **wait_for_input** (bool) – Wait for Input, (optional)
- **mode** (Literal['SET', 'ADD', 'SUB']) –

  Mode, (optional)

  - `SET`
    Set – Set a new selection.
  - `ADD`
    Extend – Extend existing selection.
  - `SUB`
    Subtract – Subtract existing selection.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.action.select_column"></a>

### bpy.ops.action.select_column(*, mode='KEYS')

Select all keyframes on the specified frame(s)

**Parameters:**

**mode** (Literal['KEYS', 'CFRA', 'MARKERS_COLUMN', 'MARKERS_BETWEEN']) – Mode, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.action.select_lasso"></a>

### bpy.ops.action.select_lasso(*, path=None, use_smooth_stroke=False, smooth_stroke_factor=0.75, smooth_stroke_radius=35, mode='SET')

Select keyframe points using lasso selection

**Parameters:**

- **path** (`bpy_prop_collection`[`OperatorMousePath`] | None) – Path, (optional)
- **use_smooth_stroke** (bool) – Stabilize Stroke, Selection lags behind mouse and follows a smoother path (optional)
- **smooth_stroke_factor** (float) – Smooth Stroke Factor, Higher values give a smoother stroke (in [0.5, 0.99], optional)
- **smooth_stroke_radius** (int) – Smooth Stroke Radius, Minimum distance from last point before selection continues (in [10, 200], optional)
- **mode** (Literal['SET', 'ADD', 'SUB']) –

  Mode, (optional)

  - `SET`
    Set – Set a new selection.
  - `ADD`
    Extend – Extend existing selection.
  - `SUB`
    Subtract – Subtract existing selection.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.action.select_leftright"></a>

### bpy.ops.action.select_leftright(*, mode='CHECK', extend=False)

Select keyframes to the left or the right of the current frame

**Parameters:**

- **mode** (Literal['CHECK', 'LEFT', 'RIGHT']) – Mode, (optional)
- **extend** (bool) – Extend Select, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.action.select_less"></a>

### bpy.ops.action.select_less()

Deselect keyframes on ends of selection islands

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.action.select_linked"></a>

### bpy.ops.action.select_linked()

Select keyframes occurring in the same F-Curves as selected ones

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.action.select_more"></a>

### bpy.ops.action.select_more()

Select keyframes beside already selected ones

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.action.snap"></a>

### bpy.ops.action.snap(*, type='CFRA')

Snap selected keyframes to the times specified

**Parameters:**

**type** (Literal['CFRA', 'NEAREST_FRAME', 'NEAREST_SECOND', 'NEAREST_MARKER']) –

Type, (optional)

- `CFRA`
  Selection to Current Frame – Snap selected keyframes to the current frame.
- `NEAREST_FRAME`
  Selection to Nearest Frame – Snap selected keyframes to the nearest (whole) frame (use to fix accidental subframe offsets).
- `NEAREST_SECOND`
  Selection to Nearest Second – Snap selected keyframes to the nearest second.
- `NEAREST_MARKER`
  Selection to Nearest Marker – Snap selected keyframes to the nearest marker.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.action.stash"></a>

### bpy.ops.action.stash(*, create_new=True)

Store this action in the NLA stack as a non-contributing strip for later use

**Parameters:**

**create_new** (bool) – Create New Action, Create a new action once the existing one has been safely stored (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.action.stash_and_create"></a>

### bpy.ops.action.stash_and_create()

Store this action in the NLA stack as a non-contributing strip for later use, and create a new action

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.action.unlink"></a>

### bpy.ops.action.unlink(*, force_delete=False)

Unlink this action from the active action slot (and/or exit Tweak Mode)

**Parameters:**

**force_delete** (bool) – Force Delete, Clear Fake User and remove copy stashed in this data-block’s NLA stack (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.action.view_all"></a>

### bpy.ops.action.view_all()

Reset viewable area to show full keyframe range

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.action.view_frame"></a>

### bpy.ops.action.view_frame()

Move the view to the current frame

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.action.view_selected"></a>

### bpy.ops.action.view_selected()

Reset viewable area to show selected keyframes range

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]
