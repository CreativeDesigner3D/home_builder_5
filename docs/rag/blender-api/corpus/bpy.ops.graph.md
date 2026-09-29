<!-- source: Blender Python API reference 5.2 / bpy.ops.graph.html -->

<a id="module-bpy.ops.graph"></a>

# Graph Operators

<a id="bpy.ops.graph.bake_keys"></a>

### bpy.ops.graph.bake_keys()

Add keyframes on every frame between the selected keyframes

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.blend_offset"></a>

### bpy.ops.graph.blend_offset(*, factor=0.0)

Shift selected keys to the value of the neighboring keys as a block

**Parameters:**

**factor** (float) – Offset Factor, Control which key to offset towards and how far (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.blend_to_default"></a>

### bpy.ops.graph.blend_to_default(*, factor=0.0)

Blend selected keys to their default value from their current position

**Parameters:**

**factor** (float) – Factor, How much to blend to the default value (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.blend_to_ease"></a>

### bpy.ops.graph.blend_to_ease(*, factor=0.0)

Blends keyframes from current state to an ease-in or ease-out curve

**Parameters:**

**factor** (float) – Blend, Favor either original data or ease curve (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.blend_to_neighbor"></a>

### bpy.ops.graph.blend_to_neighbor(*, factor=0.0)

Blend selected keyframes to their left or right neighbor

**Parameters:**

**factor** (float) – Blend, The blend factor with 0 being the current frame (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.breakdown"></a>

### bpy.ops.graph.breakdown(*, factor=0.0)

Move selected keyframes to an inbetween position relative to adjacent keys

**Parameters:**

**factor** (float) – Factor, Favor either the left or the right key (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.butterworth_smooth"></a>

### bpy.ops.graph.butterworth_smooth(*, cutoff_frequency=3.0, filter_order=4, samples_per_frame=1, blend=1.0, blend_in_out=1)

Smooth an F-Curve while maintaining the general shape of the curve

**Parameters:**

- **cutoff_frequency** (float) – Frequency Cutoff (Hz), Lower values give a smoother curve (in [0, inf], optional)
- **filter_order** (int) – Filter Order, Higher values produce a harder frequency cutoff (in [1, 32], optional)
- **samples_per_frame** (int) – Samples per Frame, How many samples to calculate per frame, helps with subframe data (in [1, 64], optional)
- **blend** (float) – Blend, How much to blend to the smoothed curve (in [0, inf], optional)
- **blend_in_out** (int) – Blend In/Out, Linearly blend the smooth data to the border frames of the selection (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.clean"></a>

### bpy.ops.graph.clean(*, threshold=0.001, channels=False)

Simplify F-Curves by removing closely spaced keyframes

**Parameters:**

- **threshold** (float) – Threshold, (in [0, inf], optional)
- **channels** (bool) – Channels, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.click_insert"></a>

### bpy.ops.graph.click_insert(*, frame=1.0, value=1.0, extend=False)

Insert new keyframe at the cursor position for the active F-Curve

**Parameters:**

- **frame** (float) – Frame Number, Frame to insert keyframe on (in [-inf, inf], optional)
- **value** (float) – Value, Value for keyframe on (in [-inf, inf], optional)
- **extend** (bool) – Extend, Extend selection instead of deselecting everything first (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.clickselect"></a>

### bpy.ops.graph.clickselect(*, wait_to_deselect_others=False, use_select_on_click=False, mouse_x=0, mouse_y=0, extend=False, deselect_all=False, column=False, curves=False)

Select keyframes by clicking on them

**Parameters:**

- **wait_to_deselect_others** (bool) – Wait to Deselect Others, (optional)
- **use_select_on_click** (bool) – Act on Click, Instead of selecting on mouse press, wait to see if there’s drag event. Otherwise select on mouse release (optional)
- **mouse_x** (int) – Mouse X, (in [-inf, inf], optional)
- **mouse_y** (int) – Mouse Y, (in [-inf, inf], optional)
- **extend** (bool) – Extend Select, Toggle keyframe selection instead of leaving newly selected keyframes only (optional)
- **deselect_all** (bool) – Deselect On Nothing, Deselect all when nothing under the cursor (optional)
- **column** (bool) – Column Select, Select all keyframes that occur on the same frame as the one under the mouse (optional)
- **curves** (bool) – Only Curves, Select all the keyframes in the curve (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.copy"></a>

### bpy.ops.graph.copy()

Copy selected keyframes to the internal clipboard

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.cursor_set"></a>

### bpy.ops.graph.cursor_set(*, frame=0.0, value=0.0)

Interactively set the current frame and value cursor

**Parameters:**

- **frame** (float) – Frame, (in [-1.04857e+06, 1.04857e+06], optional)
- **value** (float) – Value, (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.decimate"></a>

### bpy.ops.graph.decimate(*, mode='RATIO', factor=0.333333, remove_error_margin=0.0)

Decimate F-Curves by removing keyframes that influence the curve shape the least

**Parameters:**

- **mode** (Literal['RATIO', 'ERROR']) –

  Mode, Which mode to use for decimation (optional)

  - `RATIO`
    Ratio – Use a percentage to specify how many keyframes you want to remove.
  - `ERROR`
    Error Margin – Use an error margin to specify how much the curve is allowed to deviate from the original path.
- **factor** (float) – Factor, The ratio of keyframes to remove (in [0, 1], optional)
- **remove_error_margin** (float) – Max Error Margin, How much the new decimated curve is allowed to deviate from the original (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.delete"></a>

### bpy.ops.graph.delete(*, confirm=True)

Remove all selected keyframes

**Parameters:**

**confirm** (bool) – Confirm, Prompt for confirmation (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.driver_delete_invalid"></a>

### bpy.ops.graph.driver_delete_invalid()

Delete all visible drivers considered invalid

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.driver_variables_copy"></a>

### bpy.ops.graph.driver_variables_copy()

Copy the driver variables of the active driver

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.driver_variables_paste"></a>

### bpy.ops.graph.driver_variables_paste(*, replace=False)

Add copied driver variables to the active driver

**Parameters:**

**replace** (bool) – Replace Existing, Replace existing driver variables, instead of just appending to the end of the existing list (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.duplicate"></a>

### bpy.ops.graph.duplicate(*, mode='TRANSLATION')

Make a copy of all selected keyframes

**Parameters:**

**mode** (Literal[[Transform Mode Type Items](bpy_types_enum_items/transform_mode_type_items.md#rna-enum-transform-mode-type-items)]) – Mode, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.duplicate_move"></a>

### bpy.ops.graph.duplicate_move(*, GRAPH_OT_duplicate={}, TRANSFORM_OT_translate={})

Make a copy of all selected keyframes and move them

**Parameters:**

- **GRAPH_OT_duplicate** (dict[str, Any]) – Duplicate Keyframes, Make a copy of all selected keyframes (optional, [`bpy.ops.graph.duplicate()`](#bpy.ops.graph.duplicate "bpy.ops.graph.duplicate") keyword arguments)
- **TRANSFORM_OT_translate** (dict[str, Any]) – Move, Move selected items (optional, [`bpy.ops.transform.translate()`](bpy.ops.transform.md#bpy.ops.transform.translate "bpy.ops.transform.translate") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.ease"></a>

### bpy.ops.graph.ease(*, factor=0.0, sharpness=2.0)

Align keyframes on a ease-in or ease-out curve

**Parameters:**

- **factor** (float) – Curve Bend, Defines if the keys should be aligned on an ease-in or ease-out curve (in [-inf, inf], optional)
- **sharpness** (float) – Sharpness, Higher values make the change more abrupt (in [0.001, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.easing_type"></a>

### bpy.ops.graph.easing_type(*, type='AUTO')

Set easing type for the F-Curve segments starting from the selected keyframes

**Parameters:**

**type** (Literal[[Beztriple Interpolation Easing Items](bpy_types_enum_items/beztriple_interpolation_easing_items.md#rna-enum-beztriple-interpolation-easing-items)]) – Type, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.equalize_handles"></a>

### bpy.ops.graph.equalize_handles(*, side='LEFT', handle_length=5.0, flatten=False)

Ensure selected keyframes’ handles have equal length, optionally making them horizontal. Automatic, Automatic Clamped, or Vector handle types will be converted to Aligned

**Parameters:**

- **side** (Literal['LEFT', 'RIGHT', 'BOTH']) –

  Side, Side of the keyframes’ Bézier handles to affect (optional)

  - `LEFT`
    Left – Equalize selected keyframes’ left handles.
  - `RIGHT`
    Right – Equalize selected keyframes’ right handles.
  - `BOTH`
    Both – Equalize both of a keyframe’s handles.
- **handle_length** (float) – Handle Length, Length to make selected keyframes’ Bézier handles (in [0.1, inf], optional)
- **flatten** (bool) – Flatten, Make the values of the selected keyframes’ handles the same as their respective keyframes (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.euler_filter"></a>

### bpy.ops.graph.euler_filter()

Fix large jumps and flips in the selected Euler Rotation F-Curves arising from rotation values being clipped when baking physics

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.extrapolation_type"></a>

### bpy.ops.graph.extrapolation_type(*, type='CONSTANT')

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

<a id="bpy.ops.graph.fmodifier_add"></a>

### bpy.ops.graph.fmodifier_add(*, type='NULL', only_active=False)

Add F-Modifier to the active/selected F-Curves

**Parameters:**

- **type** (Literal[[Fmodifier Type Items](bpy_types_enum_items/fmodifier_type_items.md#rna-enum-fmodifier-type-items)]) – Type, (optional)
- **only_active** (bool) – Only Active, Only add F-Modifier to active F-Curve (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.fmodifier_copy"></a>

### bpy.ops.graph.fmodifier_copy()

Copy the F-Modifier(s) of the active F-Curve

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.fmodifier_delete"></a>

### bpy.ops.graph.fmodifier_delete(*, mode='ALL', type='GENERATOR')

Remove Modifier(s) from the selected F-Curves

**Parameters:**

- **mode** (Literal['ALL', 'FIRST', 'TYPE']) –

  Mode, Decide what the operator will remove (optional)

  - `ALL`
    Remove All – Remove all modifiers from the selected F-Curves.
  - `FIRST`
    Remove First – Only remove the first modifier from each F-Curve regardless of type.
  - `TYPE`
    Remove Type – Only remove the specified type of F-Curve modifier.
- **type** (Literal[[Fmodifier Type Items](bpy_types_enum_items/fmodifier_type_items.md#rna-enum-fmodifier-type-items)]) – Type, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.fmodifier_paste"></a>

### bpy.ops.graph.fmodifier_paste(*, only_active=False, replace=False)

Add copied F-Modifiers to the selected F-Curves

**Parameters:**

- **only_active** (bool) – Only Active, Only paste F-Modifiers on active F-Curve (optional)
- **replace** (bool) – Replace Existing, Replace existing F-Modifiers, instead of just appending to the end of the existing list (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.frame_jump"></a>

### bpy.ops.graph.frame_jump()

Place the cursor on the midpoint of selected keyframes

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.gaussian_smooth"></a>

### bpy.ops.graph.gaussian_smooth(*, factor=1.0, sigma=0.33, filter_width=6)

Smooth the curve using a Gaussian filter

**Parameters:**

- **factor** (float) – Factor, How much to blend to the default value (in [0, inf], optional)
- **sigma** (float) – Sigma, The shape of the gaussian distribution, lower values make it sharper (in [0.001, inf], optional)
- **filter_width** (int) – Filter Width, How far to each side the operator will average the key values (in [1, 64], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.ghost_curves_clear"></a>

### bpy.ops.graph.ghost_curves_clear()

Clear F-Curve snapshots (Ghosts) for active Graph Editor

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.ghost_curves_create"></a>

### bpy.ops.graph.ghost_curves_create()

Create snapshot (Ghosts) of selected F-Curves as background aid for active Graph Editor

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.handle_type"></a>

### bpy.ops.graph.handle_type(*, type='FREE')

Set type of handle for selected keyframes

**Parameters:**

**type** (Literal[[Keyframe Handle Type Items](bpy_types_enum_items/keyframe_handle_type_items.md#rna-enum-keyframe-handle-type-items)]) – Type, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.hide"></a>

### bpy.ops.graph.hide(*, unselected=False)

Hide selected curves from Graph Editor view

**Parameters:**

**unselected** (bool) – Unselected, Hide unselected rather than selected curves (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.interpolation_type"></a>

### bpy.ops.graph.interpolation_type(*, type='CONSTANT')

Set interpolation mode for the F-Curve segments starting from the selected keyframes

**Parameters:**

**type** (Literal[[Beztriple Interpolation Mode Items](bpy_types_enum_items/beztriple_interpolation_mode_items.md#rna-enum-beztriple-interpolation-mode-items)]) – Type, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.keyframe_insert"></a>

### bpy.ops.graph.keyframe_insert(*, type='ALL')

Insert keyframes for the specified channels

**Parameters:**

**type** (Literal['ALL', 'SEL', 'ACTIVE', 'CURSOR_ACTIVE', 'CURSOR_SEL']) –

Type, (optional)

- `ALL`
  All Channels – Insert a keyframe on all visible and editable F-Curves using each curve’s current value.
- `SEL`
  Only Selected Channels – Insert a keyframe on selected F-Curves using each curve’s current value.
- `ACTIVE`
  Only Active F-Curve – Insert a keyframe on the active F-Curve using the curve’s current value.
- `CURSOR_ACTIVE`
  Active Channels at Cursor – Insert a keyframe for the active F-Curve at the cursor point.
- `CURSOR_SEL`
  Selected Channels at Cursor – Insert a keyframe for selected F-Curves at the cursor point.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.keyframe_jump"></a>

### bpy.ops.graph.keyframe_jump(*, next=True)

Jump to previous/next keyframe

**Parameters:**

**next** (bool) – Next Keyframe, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.keys_to_samples"></a>

### bpy.ops.graph.keys_to_samples()

Convert selected channels to an uneditable set of samples to save storage space

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.local_view"></a>

### bpy.ops.graph.local_view(*, frame_selected=True)

Isolate selected F-Curves in Graph Editor view

**Parameters:**

**frame_selected** (bool) – Frame selected, Zoom current view to draw selected fcurves in visible range (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.match_slope"></a>

### bpy.ops.graph.match_slope(*, factor=0.0)

Blend selected keys to the slope of neighboring ones

**Parameters:**

**factor** (float) – Factor, Defines which keys to use as slope and how much to blend towards them (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.mirror"></a>

### bpy.ops.graph.mirror(*, type='CFRA')

Flip selected keyframes over the selected mirror line

**Parameters:**

**type** (Literal['CFRA', 'MARKER', 'YAXIS', 'VALUE', 'XAXIS']) –

Type, (optional)

- `CFRA`
  By Times Over Current Frame – Flip times of selected keyframes using the current frame as the mirror line.
- `MARKER`
  By Times Over First Selected Marker – Flip times of selected keyframes using the first selected marker as the reference point.
- `YAXIS`
  By Times Over Zero Time – Flip times of selected keyframes, effectively reversing the order they appear in.
- `VALUE`
  By Values Over Cursor Value – Flip values of selected keyframes using the cursor value (Y/Horizontal component) as the mirror line.
- `XAXIS`
  By Values Over Zero Value – Flip values of selected keyframes (i.e. negative values become positive, and vice versa).

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.paste"></a>

### bpy.ops.graph.paste(*, offset='START', value_offset='NONE', merge='MIX', flipped=False)

Paste keyframes from the internal clipboard for the selected channels, starting on the current frame

**Parameters:**

- **offset** (Literal[[Keyframe Paste Offset Items](bpy_types_enum_items/keyframe_paste_offset_items.md#rna-enum-keyframe-paste-offset-items)]) – Frame Offset, Paste time offset of keys (optional)
- **value_offset** (Literal[[Keyframe Paste Offset Value Items](bpy_types_enum_items/keyframe_paste_offset_value_items.md#rna-enum-keyframe-paste-offset-value-items)]) – Value Offset, Paste keys with a value offset (optional)
- **merge** (Literal[[Keyframe Paste Merge Items](bpy_types_enum_items/keyframe_paste_merge_items.md#rna-enum-keyframe-paste-merge-items)]) – Type, Method of merging pasted keys and existing (optional)
- **flipped** (bool) – Flipped, Paste keyframes from mirrored bones if they exist (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.previewrange_set"></a>

### bpy.ops.graph.previewrange_set()

Set Preview Range based on range of selected keyframes

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.push_pull"></a>

### bpy.ops.graph.push_pull(*, factor=1.0)

Exaggerate or minimize the value of the selected keys

**Parameters:**

**factor** (float) – Factor, Control how far to push or pull the keys (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.reveal"></a>

### bpy.ops.graph.reveal(*, select=True)

Make previously hidden curves visible again in Graph Editor view

**Parameters:**

**select** (bool) – Select, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.samples_to_keys"></a>

### bpy.ops.graph.samples_to_keys()

Convert selected channels from samples to keyframes

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.scale_average"></a>

### bpy.ops.graph.scale_average(*, factor=1.0)

Scale selected key values by their combined average

**Parameters:**

**factor** (float) – Scale Factor, The scale factor applied to the curve segments (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.scale_from_neighbor"></a>

### bpy.ops.graph.scale_from_neighbor(*, factor=0.0, anchor='LEFT')

Increase or decrease the value of selected keys in relationship to the neighboring one

**Parameters:**

- **factor** (float) – Factor, The factor to scale keys with (in [-inf, inf], optional)
- **anchor** (Literal['LEFT', 'RIGHT']) – Reference Key, Which end of the segment to use as a reference to scale from (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.select_all"></a>

### bpy.ops.graph.select_all(*, action='TOGGLE')

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

<a id="bpy.ops.graph.select_box"></a>

### bpy.ops.graph.select_box(*, axis_range=False, include_handles=True, tweak=False, use_curve_selection=True, xmin=0, xmax=0, ymin=0, ymax=0, wait_for_input=True, mode='SET')

Select all keyframes within the specified region

**Parameters:**

- **axis_range** (bool) – Axis Range, (optional)
- **include_handles** (bool) – Include Handles, Are handles tested individually against the selection criteria, independently from their keys. When unchecked, handles are (de)selected in unison with their keys (optional)
- **tweak** (bool) – Tweak, Operator has been activated using a click-drag event (optional)
- **use_curve_selection** (bool) – Select Curves, Allow selecting all the keyframes of a curve by selecting the calculated F-curve (optional)
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

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.select_circle"></a>

### bpy.ops.graph.select_circle(*, x=0, y=0, radius=25, wait_for_input=True, mode='SET', include_handles=True, use_curve_selection=True)

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
- **include_handles** (bool) – Include Handles, Are handles tested individually against the selection criteria, independently from their keys. When unchecked, handles are (de)selected in unison with their keys (optional)
- **use_curve_selection** (bool) – Select Curves, Allow selecting all the keyframes of a curve by selecting the curve itself (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.select_column"></a>

### bpy.ops.graph.select_column(*, mode='KEYS')

Select all keyframes on the specified frame(s)

**Parameters:**

**mode** (Literal['KEYS', 'CFRA', 'MARKERS_COLUMN', 'MARKERS_BETWEEN']) – Mode, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.select_key_handles"></a>

### bpy.ops.graph.select_key_handles(*, left_handle_action='SELECT', right_handle_action='SELECT', key_action='KEEP')

For selected keyframes, select/deselect any combination of the key itself and its handles

**Parameters:**

- **left_handle_action** (Literal['SELECT', 'DESELECT', 'KEEP']) –

  Left Handle, Effect on the left handle (optional)

  - `SELECT`
    Select.
  - `DESELECT`
    Deselect.
  - `KEEP`
    Keep – Leave as is.
- **right_handle_action** (Literal['SELECT', 'DESELECT', 'KEEP']) –

  Right Handle, Effect on the right handle (optional)

  - `SELECT`
    Select.
  - `DESELECT`
    Deselect.
  - `KEEP`
    Keep – Leave as is.
- **key_action** (Literal['SELECT', 'DESELECT', 'KEEP']) –

  Key, Effect on the key itself (optional)

  - `SELECT`
    Select.
  - `DESELECT`
    Deselect.
  - `KEEP`
    Keep – Leave as is.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.select_lasso"></a>

### bpy.ops.graph.select_lasso(*, path=None, use_smooth_stroke=False, smooth_stroke_factor=0.75, smooth_stroke_radius=35, mode='SET', include_handles=True, use_curve_selection=True)

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
- **include_handles** (bool) – Include Handles, Are handles tested individually against the selection criteria, independently from their keys. When unchecked, handles are (de)selected in unison with their keys (optional)
- **use_curve_selection** (bool) – Select Curves, Allow selecting all the keyframes of a curve by selecting the curve itself (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.select_leftright"></a>

### bpy.ops.graph.select_leftright(*, mode='CHECK', extend=False)

Select keyframes to the left or the right of the current frame

**Parameters:**

- **mode** (Literal['LEFT', 'RIGHT', 'CHECK']) – Mode, (optional)
- **extend** (bool) – Extend Select, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.select_less"></a>

### bpy.ops.graph.select_less()

Deselect keyframes on ends of selection islands

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.select_linked"></a>

### bpy.ops.graph.select_linked()

Select keyframes occurring in the same F-Curves as selected ones

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.select_more"></a>

### bpy.ops.graph.select_more()

Select keyframes beside already selected ones

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.shear"></a>

### bpy.ops.graph.shear(*, factor=0.0, direction='FROM_LEFT')

Affect the value of the keys linearly, keeping the same relationship between them using either the left or the right key as reference

**Parameters:**

- **factor** (float) – Shear Factor, The amount of shear to apply (in [-inf, inf], optional)
- **direction** (Literal['FROM_LEFT', 'FROM_RIGHT']) –

  Direction, Which end of the segment to use as a reference to shear from (optional)

  - `FROM_LEFT`
    From Left – Shear the keys using the left key as reference.
  - `FROM_RIGHT`
    From Right – Shear the keys using the right key as reference.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.smooth"></a>

### bpy.ops.graph.smooth()

Apply weighted moving means to make selected F-Curves less bumpy

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.snap"></a>

### bpy.ops.graph.snap(*, type='CFRA')

Snap selected keyframes to the chosen times/values

**Parameters:**

**type** (Literal['CFRA', 'VALUE', 'NEAREST_FRAME', 'NEAREST_SECOND', 'NEAREST_MARKER', 'HORIZONTAL']) –

Type, (optional)

- `CFRA`
  Selection to Current Frame – Snap selected keyframes to the current frame.
- `VALUE`
  Selection to Cursor Value – Set values of selected keyframes to the cursor value (Y/Horizontal component).
- `NEAREST_FRAME`
  Selection to Nearest Frame – Snap selected keyframes to the nearest (whole) frame (use to fix accidental subframe offsets).
- `NEAREST_SECOND`
  Selection to Nearest Second – Snap selected keyframes to the nearest second.
- `NEAREST_MARKER`
  Selection to Nearest Marker – Snap selected keyframes to the nearest marker.
- `HORIZONTAL`
  Flatten Handles – Flatten handles for a smoother transition.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.snap_cursor_value"></a>

### bpy.ops.graph.snap_cursor_value()

Place the cursor value on the average value of selected keyframes

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.sound_to_samples"></a>

### bpy.ops.graph.sound_to_samples(*, filepath='', check_existing=False, filter_blender=False, filter_backup=False, filter_image=False, filter_movie=True, filter_python=False, filter_font=False, filter_sound=True, filter_text=False, filter_archive=False, filter_btx=False, filter_alembic=False, filter_usd=False, filter_obj=False, filter_volume=False, filter_folder=True, filter_blenlib=False, filemode=9, show_multiview=False, use_multiview=False, display_type='DEFAULT', sort_method='', low=0.0, high=100000.0, attack=0.005, release=0.2, threshold=0.0, use_accumulate=False, use_additive=False, use_square=False, sthreshold=0.1)

Bakes a sound wave to samples on selected channels

**Parameters:**

- **filepath** (str) – File Path, Path to file (optional, never None)
- **check_existing** (bool) – Check Existing, Check and warn on overwriting existing files (optional)
- **filter_blender** (bool) – Filter .blend files, (optional)
- **filter_backup** (bool) – Filter backup .blend files, (optional)
- **filter_image** (bool) – Filter image files, (optional)
- **filter_movie** (bool) – Filter movie files, (optional)
- **filter_python** (bool) – Filter Python files, (optional)
- **filter_font** (bool) – Filter font files, (optional)
- **filter_sound** (bool) – Filter sound files, (optional)
- **filter_text** (bool) – Filter text files, (optional)
- **filter_archive** (bool) – Filter archive files, (optional)
- **filter_btx** (bool) – Filter btx files, (optional)
- **filter_alembic** (bool) – Filter Alembic files, (optional)
- **filter_usd** (bool) – Filter USD files, (optional)
- **filter_obj** (bool) – Filter OBJ files, (optional)
- **filter_volume** (bool) – Filter OpenVDB volume files, (optional)
- **filter_folder** (bool) – Filter folders, (optional)
- **filter_blenlib** (bool) – Filter Blender IDs, (optional)
- **filemode** (int) – File Browser Mode, The setting for the file browser mode to load a .blend file, a library or a special file (in [1, 9], optional)
- **show_multiview** (bool) – Enable Multi-View, (optional)
- **use_multiview** (bool) – Use Multi-View, (optional)
- **display_type** (Literal['DEFAULT', 'LIST_VERTICAL', 'LIST_HORIZONTAL', 'THUMBNAIL']) –

  Display Type, (optional)

  - `DEFAULT`
    Default – Automatically determine display type for files.
  - `LIST_VERTICAL`
    Short List – Display files as short list.
  - `LIST_HORIZONTAL`
    Long List – Display files as a detailed list.
  - `THUMBNAIL`
    Thumbnails – Display files as thumbnails.
- **sort_method** (str) – File sorting mode, (optional)
- **low** (float) – Lowest Frequency, Cutoff frequency of a high-pass filter that is applied to the audio data (in [0, 100000], optional)
- **high** (float) – Highest Frequency, Cutoff frequency of a low-pass filter that is applied to the audio data (in [0, 100000], optional)
- **attack** (float) – Attack Time, Value for the envelope calculation that tells how fast the envelope can rise (the lower the value the steeper it can rise) (in [0, 2], optional)
- **release** (float) – Release Time, Value for the envelope calculation that tells how fast the envelope can fall (the lower the value the steeper it can fall) (in [0, 5], optional)
- **threshold** (float) – Threshold, Minimum amplitude value needed to influence the envelope (in [0, 1], optional)
- **use_accumulate** (bool) – Accumulate, Only the positive differences of the envelope amplitudes are summarized to produce the output (optional)
- **use_additive** (bool) – Additive, The amplitudes of the envelope are summarized (or, when Accumulate is enabled, both positive and negative differences are accumulated) (optional)
- **use_square** (bool) – Square, The output is a square curve (negative values always result in -1, and positive ones in 1) (optional)
- **sthreshold** (float) – Square Threshold, Square only: all values with an absolute amplitude lower than that result in 0 (in [0, 1], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.time_offset"></a>

### bpy.ops.graph.time_offset(*, frame_offset=0.0)

Shifts the value of selected keys in time

**Parameters:**

**frame_offset** (float) – Frame Offset, How far in frames to offset the animation (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.view_all"></a>

### bpy.ops.graph.view_all(*, include_handles=True)

Reset viewable area to show full keyframe range

**Parameters:**

**include_handles** (bool) – Include Handles, Include handles of keyframes when calculating extents (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.view_frame"></a>

### bpy.ops.graph.view_frame()

Move the view to the current frame

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.graph.view_selected"></a>

### bpy.ops.graph.view_selected(*, include_handles=True)

Reset viewable area to show selected keyframe range

**Parameters:**

**include_handles** (bool) – Include Handles, Include handles of keyframes when calculating extents (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]
