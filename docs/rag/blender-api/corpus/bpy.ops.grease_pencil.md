<!-- source: Blender Python API reference 5.2 / bpy.ops.grease_pencil.html -->

<a id="module-bpy.ops.grease_pencil"></a>

# Grease Pencil Operators

<a id="bpy.ops.grease_pencil.active_frame_delete"></a>

### bpy.ops.grease_pencil.active_frame_delete(*, all=False)

Delete the active Grease Pencil frame(s)

**Parameters:**

**all** (bool) – Delete all, Delete active keyframes of all layers (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.bake_grease_pencil_animation"></a>

### bpy.ops.grease_pencil.bake_grease_pencil_animation(*, frame_start=1, frame_end=250, step=1, only_selected=False, frame_target=1, project_type='KEEP')

Bake Grease Pencil object transform to Grease Pencil keyframes

**Parameters:**

- **frame_start** (int) – Start Frame, The start frame (in [1, 100000], optional)
- **frame_end** (int) – End Frame, The end frame of animation (in [1, 100000], optional)
- **step** (int) – Step, Step between generated frames (in [1, 100], optional)
- **only_selected** (bool) – Only Selected Keyframes, Convert only selected keyframes (optional)
- **frame_target** (int) – Target Frame, Destination frame (in [1, 100000], optional)
- **project_type** (Literal['KEEP', 'FRONT', 'SIDE', 'TOP', 'VIEW', 'CURSOR']) –

  Projection Type, (optional)

  - `KEEP`
    No Reproject.
  - `FRONT`
    Front – Reproject the strokes using the X-Z plane.
  - `SIDE`
    Side – Reproject the strokes using the Y-Z plane.
  - `TOP`
    Top – Reproject the strokes using the X-Y plane.
  - `VIEW`
    View – Reproject the strokes to end up on the same plane, as if drawn from the current viewpoint using ‘Cursor’ Stroke Placement.
  - `CURSOR`
    Cursor – Reproject the strokes using the orientation of 3D cursor.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.brush_stroke"></a>

### bpy.ops.grease_pencil.brush_stroke(*, stroke=None, mode='NORMAL', brush_toggle='None', pen_flip=False)

Draw a new stroke in the active Grease Pencil object

**Parameters:**

- **stroke** (`bpy_prop_collection`[`OperatorStrokeElement`] | None) – Stroke, (optional)
- **mode** (Literal['NORMAL', 'INVERT']) –

  Stroke Mode, Action taken when a paint stroke is made (optional)

  - `NORMAL`
    Regular – Apply brush normally.
  - `INVERT`
    Invert – Invert action of brush for duration of stroke.
- **brush_toggle** (Literal['None', 'SMOOTH', 'ERASE', 'MASK']) –

  Temporary Brush Toggle Type, Brush to use for duration of stroke (optional)

  - `None`
    None – Apply brush normally.
  - `SMOOTH`
    Smooth – Switch to smooth brush for duration of stroke.
  - `ERASE`
    Erase – Switch to erase brush for duration of stroke.
  - `MASK`
    Mask – Switch to mask brush for duration of stroke.
- **pen_flip** (bool) – Pen Flip, Whether a tablet’s eraser mode is being used (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.caps_set"></a>

### bpy.ops.grease_pencil.caps_set(*, type='ROUND')

Change curve caps mode (rounded or flat)

**Parameters:**

**type** (Literal['ROUND', 'FLAT', 'START', 'END']) –

Type, (optional)

- `ROUND`
  Rounded – Set as default rounded.
- `FLAT`
  Flat.
- `START`
  Toggle Start.
- `END`
  Toggle End.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.clean_loose"></a>

### bpy.ops.grease_pencil.clean_loose(*, limit=1)

Remove loose points

**Parameters:**

**limit** (int) – Limit, Number of points to consider stroke as loose (in [1, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.convert_curve_type"></a>

### bpy.ops.grease_pencil.convert_curve_type(*, type='POLY', threshold=0.01)

Convert type of selected curves

**Parameters:**

- **type** (Literal[[Curves Type Items](bpy_types_enum_items/curves_type_items.md#rna-enum-curves-type-items)]) – Type, (optional)
- **threshold** (float) – Threshold, The distance that the resulting points are allowed to be within (in [0, 100], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.copy"></a>

### bpy.ops.grease_pencil.copy()

Copy the selected Grease Pencil points or strokes to the internal clipboard

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.cyclical_set"></a>

### bpy.ops.grease_pencil.cyclical_set(*, type='TOGGLE', subdivide_cyclic_segment=True)

Close or open the selected stroke adding a segment from last to first point

**Parameters:**

- **type** (Literal['CLOSE', 'OPEN', 'TOGGLE']) – Type, (optional)
- **subdivide_cyclic_segment** (bool) – Match Point Density, Add point in the new segment to keep the same density (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.delete"></a>

### bpy.ops.grease_pencil.delete(*, mode='ALL')

Delete selected strokes or points

**Parameters:**

**mode** (Literal['ALL', 'STROKES', 'FILLS']) –

Mode, The kind of strokes or fills to delete (optional)

- `ALL`
  All – Delete all selected strokes or points.
- `STROKES`
  Only Strokes – Delete only strokes and not fills.
- `FILLS`
  Only Fills – Delete only fills and not strokes.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.delete_breakdown"></a>

### bpy.ops.grease_pencil.delete_breakdown()

Remove breakdown frames generated by interpolating between two Grease Pencil frames

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.delete_frame"></a>

### bpy.ops.grease_pencil.delete_frame(*, type='ACTIVE_FRAME')

Delete Grease Pencil Frame(s)

**Parameters:**

**type** (Literal['ACTIVE_FRAME', 'ALL_FRAMES']) –

Type, Method used for deleting Grease Pencil frames (optional)

- `ACTIVE_FRAME`
  Active Frame – Deletes current frame in the active layer.
- `ALL_FRAMES`
  All Active Frames – Delete active frames for all layers.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.dissolve"></a>

### bpy.ops.grease_pencil.dissolve(*, type='POINTS')

Delete selected points without splitting strokes

**Parameters:**

**type** (Literal['POINTS', 'BETWEEN', 'UNSELECT']) –

Type, Method used for dissolving stroke points (optional)

- `POINTS`
  Dissolve – Dissolve selected points.
- `BETWEEN`
  Dissolve Between – Dissolve points between selected points.
- `UNSELECT`
  Dissolve Unselect – Dissolve all unselected points.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.duplicate"></a>

### bpy.ops.grease_pencil.duplicate()

Duplicate the selected points

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.duplicate_move"></a>

### bpy.ops.grease_pencil.duplicate_move(*, GREASE_PENCIL_OT_duplicate={}, TRANSFORM_OT_translate={})

Make copies of the selected Grease Pencil strokes and move them

**Parameters:**

- **GREASE_PENCIL_OT_duplicate** (dict[str, Any]) – Duplicate, Duplicate the selected points (optional, [`bpy.ops.grease_pencil.duplicate()`](#bpy.ops.grease_pencil.duplicate "bpy.ops.grease_pencil.duplicate") keyword arguments)
- **TRANSFORM_OT_translate** (dict[str, Any]) – Move, Move selected items (optional, [`bpy.ops.transform.translate()`](bpy.ops.transform.md#bpy.ops.transform.translate "bpy.ops.transform.translate") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.erase_box"></a>

### bpy.ops.grease_pencil.erase_box(*, xmin=0, xmax=0, ymin=0, ymax=0, wait_for_input=True)

Erase points in the box region

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

<a id="bpy.ops.grease_pencil.erase_lasso"></a>

### bpy.ops.grease_pencil.erase_lasso(*, path=None, use_smooth_stroke=False, smooth_stroke_factor=0.75, smooth_stroke_radius=35)

Erase points in the lasso region

**Parameters:**

- **path** (`bpy_prop_collection`[`OperatorMousePath`] | None) – Path, (optional)
- **use_smooth_stroke** (bool) – Stabilize Stroke, Selection lags behind mouse and follows a smoother path (optional)
- **smooth_stroke_factor** (float) – Smooth Stroke Factor, Higher values give a smoother stroke (in [0.5, 0.99], optional)
- **smooth_stroke_radius** (int) – Smooth Stroke Radius, Minimum distance from last point before selection continues (in [10, 200], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.extrude"></a>

### bpy.ops.grease_pencil.extrude()

Extrude the selected points

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.extrude_move"></a>

### bpy.ops.grease_pencil.extrude_move(*, GREASE_PENCIL_OT_extrude={}, TRANSFORM_OT_translate={})

Extrude selected points and move them

**Parameters:**

- **GREASE_PENCIL_OT_extrude** (dict[str, Any]) – Extrude Stroke Points, Extrude the selected points (optional, [`bpy.ops.grease_pencil.extrude()`](#bpy.ops.grease_pencil.extrude "bpy.ops.grease_pencil.extrude") keyword arguments)
- **TRANSFORM_OT_translate** (dict[str, Any]) – Move, Move selected items (optional, [`bpy.ops.transform.translate()`](bpy.ops.transform.md#bpy.ops.transform.translate "bpy.ops.transform.translate") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.fill"></a>

### bpy.ops.grease_pencil.fill(*, invert=False, precision=False)

Fill with color the shape formed by strokes

**Parameters:**

- **invert** (bool) – Invert, Find boundary of unfilled instead of filled regions (optional)
- **precision** (bool) – Precision, Use precision movement for extension lines (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.frame_clean_duplicate"></a>

### bpy.ops.grease_pencil.frame_clean_duplicate(*, selected=False)

Remove any keyframe that is a duplicate of the previous one

**Parameters:**

**selected** (bool) – Selected, Only delete selected keyframes (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.frame_duplicate"></a>

### bpy.ops.grease_pencil.frame_duplicate(*, all=False)

Make a copy of the active Grease Pencil frame(s)

**Parameters:**

**all** (bool) – Duplicate all, Duplicate active keyframes of all layer (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.insert_blank_frame"></a>

### bpy.ops.grease_pencil.insert_blank_frame(*, all_layers=False, duration=0)

Insert a blank frame on the current scene frame

**Parameters:**

- **all_layers** (bool) – All Layers, Insert a blank frame in all editable layers (optional)
- **duration** (int) – Duration, (in [0, 1048574], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.interpolate"></a>

### bpy.ops.grease_pencil.interpolate(*, shift=0.0, layers='ACTIVE', exclude_breakdowns=False, use_selection=False, flip='AUTO', smooth_steps=1, smooth_factor=0.0)

Interpolate Grease Pencil strokes between frames

**Parameters:**

- **shift** (float) – Shift, Bias factor for which frame has more influence on the interpolated strokes (in [-1, 1], optional)
- **layers** (Literal['ACTIVE', 'ALL']) – Layer, Layers included in the interpolation (optional)
- **exclude_breakdowns** (bool) – Exclude Breakdowns, Exclude existing Breakdowns keyframes as interpolation extremes (optional)
- **use_selection** (bool) – Use Selection, Use only selected strokes for interpolating (optional)
- **flip** (Literal['NONE', 'FLIP', 'AUTO']) – Flip Mode, Invert destination stroke to match start and end with source stroke (optional)
- **smooth_steps** (int) – Iterations, Number of times to smooth newly created strokes (in [1, 3], optional)
- **smooth_factor** (float) – Smooth, Amount of smoothing to apply to interpolated strokes, to reduce jitter/noise (in [0, 2], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.interpolate_sequence"></a>

### bpy.ops.grease_pencil.interpolate_sequence(*, step=1, layers='ACTIVE', exclude_breakdowns=False, use_selection=False, flip='AUTO', smooth_steps=1, smooth_factor=0.0, type='LINEAR', easing='EASE_IN', back=1.702, amplitude=0.15, period=0.15)

Generate ‘in-betweens’ to smoothly interpolate between Grease Pencil frames

**Parameters:**

- **step** (int) – Step, Number of frames between generated interpolated frames (in [1, 1048574], optional)
- **layers** (Literal['ACTIVE', 'ALL']) – Layer, Layers included in the interpolation (optional)
- **exclude_breakdowns** (bool) – Exclude Breakdowns, Exclude existing Breakdowns keyframes as interpolation extremes (optional)
- **use_selection** (bool) – Use Selection, Use only selected strokes for interpolating (optional)
- **flip** (Literal['NONE', 'FLIP', 'AUTO']) – Flip Mode, Invert destination stroke to match start and end with source stroke (optional)
- **smooth_steps** (int) – Iterations, Number of times to smooth newly created strokes (in [1, 3], optional)
- **smooth_factor** (float) – Smooth, Amount of smoothing to apply to interpolated strokes, to reduce jitter/noise (in [0, 2], optional)
- **type** (Literal['LINEAR', 'CUSTOM', 'SINE', 'QUAD', 'CUBIC', 'QUART', 'QUINT', 'EXPO', 'CIRC', 'BACK', 'BOUNCE', 'ELASTIC']) –

  Type, Interpolation method to use the next time ‘Interpolate Sequence’ is run (optional)

  - `LINEAR`
    Linear – Straight-line interpolation between A and B (i.e. no ease in/out).
  - `CUSTOM`
    Custom – Custom interpolation defined using a curve map.
  - `SINE`
    Sinusoidal – Sinusoidal easing (weakest, almost linear but with a slight curvature).
  - `QUAD`
    Quadratic – Quadratic easing.
  - `CUBIC`
    Cubic – Cubic easing.
  - `QUART`
    Quartic – Quartic easing.
  - `QUINT`
    Quintic – Quintic easing.
  - `EXPO`
    Exponential – Exponential easing (dramatic).
  - `CIRC`
    Circular – Circular easing (strongest and most dynamic).
  - `BACK`
    Back – Cubic easing with overshoot and settle.
  - `BOUNCE`
    Bounce – Exponentially decaying parabolic bounce, like when objects collide.
  - `ELASTIC`
    Elastic – Exponentially decaying sine wave, like an elastic band.
- **easing** (Literal[[Beztriple Interpolation Easing Items](bpy_types_enum_items/beztriple_interpolation_easing_items.md#rna-enum-beztriple-interpolation-easing-items)]) – Easing, Which ends of the segment between the preceding and following Grease Pencil frames easing interpolation is applied to (optional)
- **back** (float) – Back, Amount of overshoot for ‘back’ easing (in [0, inf], optional)
- **amplitude** (float) – Amplitude, Amount to boost elastic bounces for ‘elastic’ easing (in [0, inf], optional)
- **period** (float) – Period, Time between bounces for elastic easing (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.join_fills"></a>

### bpy.ops.grease_pencil.join_fills()

Join selected strokes into one fill to create holes

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.join_selection"></a>

### bpy.ops.grease_pencil.join_selection(*, type='JOINSTROKES')

New stroke from selected points/strokes

**Parameters:**

**type** (Literal['JOINSTROKES', 'SPLITCOPY', 'SPLIT']) –

Type, Defines how the operator will behave on the selection in the active layer (optional)

- `JOINSTROKES`
  Join Strokes – Join the selected strokes into one stroke.
- `SPLITCOPY`
  Split and Copy – Copy the selected points to a new stroke.
- `SPLIT`
  Split – Split the selected point to a new stroke.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.layer_active"></a>

### bpy.ops.grease_pencil.layer_active(*, layer=0)

Set the active Grease Pencil layer

**Parameters:**

**layer** (int) – Grease Pencil Layer, (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.layer_add"></a>

### bpy.ops.grease_pencil.layer_add(*, new_layer_name='Layer')

Add a new Grease Pencil layer in the active object

**Parameters:**

**new_layer_name** (str) – Name, Name of the new layer (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.layer_duplicate"></a>

### bpy.ops.grease_pencil.layer_duplicate(*, empty_keyframes=False)

Make a copy of the active Grease Pencil layer

**Parameters:**

**empty_keyframes** (bool) – Empty Keyframes, Add Empty Keyframes (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.layer_duplicate_object"></a>

### bpy.ops.grease_pencil.layer_duplicate_object(*, only_active=True, mode='ALL')

Make a copy of the active Grease Pencil layer to selected object

**Parameters:**

- **only_active** (bool) – Only Active, Copy only active Layer, uncheck to append all layers (optional)
- **mode** (Literal['ALL', 'ACTIVE']) – Mode, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.layer_group_add"></a>

### bpy.ops.grease_pencil.layer_group_add(*, new_layer_group_name='')

Add a new Grease Pencil layer group in the active object

**Parameters:**

**new_layer_group_name** (str) – Name, Name of the new layer group (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.layer_group_color_tag"></a>

### bpy.ops.grease_pencil.layer_group_color_tag(*, color_tag='COLOR1')

Change layer group icon

**Parameters:**

**color_tag** (Literal['NONE', 'COLOR1', 'COLOR2', 'COLOR3', 'COLOR4', 'COLOR5', 'COLOR6', 'COLOR7', 'COLOR8']) – Color Tag, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.layer_group_remove"></a>

### bpy.ops.grease_pencil.layer_group_remove(*, keep_children=False)

Remove Grease Pencil layer group in the active object

**Parameters:**

**keep_children** (bool) – Keep children nodes, Keep the children nodes of the group and only delete the group itself (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.layer_hide"></a>

### bpy.ops.grease_pencil.layer_hide(*, unselected=False)

Hide selected/unselected Grease Pencil layers

**Parameters:**

**unselected** (bool) – Unselected, Hide unselected rather than selected layers (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.layer_isolate"></a>

### bpy.ops.grease_pencil.layer_isolate(*, affect_visibility=False)

Make only active layer visible/editable

**Parameters:**

**affect_visibility** (bool) – Affect Visibility, Also affect the visibility (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.layer_lock_all"></a>

### bpy.ops.grease_pencil.layer_lock_all(*, lock=True)

Lock all Grease Pencil layers to prevent them from being accidentally modified

**Parameters:**

**lock** (bool) – Lock Value, Lock/Unlock all layers (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.layer_mask_add"></a>

### bpy.ops.grease_pencil.layer_mask_add(*, name='')

Add new layer as masking

**Parameters:**

**name** (str) – Layer, Name of the layer (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.layer_mask_remove"></a>

### bpy.ops.grease_pencil.layer_mask_remove()

Remove Layer Mask

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.layer_mask_reorder"></a>

### bpy.ops.grease_pencil.layer_mask_reorder(*, direction='UP')

Reorder the active Grease Pencil mask layer up/down in the list

**Parameters:**

**direction** (Literal['UP', 'DOWN']) – Direction, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.layer_merge"></a>

### bpy.ops.grease_pencil.layer_merge(*, mode='ACTIVE')

Combine layers based on the mode into one layer

**Parameters:**

**mode** (Literal['ACTIVE', 'GROUP', 'ALL']) –

Mode, (optional)

- `ACTIVE`
  Active – Combine the active layer with the layer just below (if it exists).
- `GROUP`
  Group – Combine layers in the active group into a single layer.
- `ALL`
  All – Combine all layers into a single layer.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.layer_move"></a>

### bpy.ops.grease_pencil.layer_move(*, direction='UP')

Move the active Grease Pencil layer or Group

**Parameters:**

**direction** (Literal['UP', 'DOWN']) – Direction, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.layer_remove"></a>

### bpy.ops.grease_pencil.layer_remove()

Remove the active Grease Pencil layer

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.layer_reveal"></a>

### bpy.ops.grease_pencil.layer_reveal()

Show all Grease Pencil layers

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.material_copy_to_object"></a>

### bpy.ops.grease_pencil.material_copy_to_object(*, only_active=True)

Append Materials of the active Grease Pencil to other object

**Parameters:**

**only_active** (bool) – Only Active, Append only active material, uncheck to append all materials (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.material_hide"></a>

### bpy.ops.grease_pencil.material_hide(*, invert=False)

Hide active/inactive Grease Pencil material(s)

**Parameters:**

**invert** (bool) – Invert, Hide inactive materials instead of the active one (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.material_isolate"></a>

### bpy.ops.grease_pencil.material_isolate(*, affect_visibility=False)

Toggle whether the active material is the only one that is editable and/or visible

**Parameters:**

**affect_visibility** (bool) – Affect Visibility, In addition to toggling the editability, also affect the visibility (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.material_lock_all"></a>

### bpy.ops.grease_pencil.material_lock_all()

Lock all Grease Pencil materials to prevent them from being accidentally modified

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.material_lock_unselected"></a>

### bpy.ops.grease_pencil.material_lock_unselected()

Lock any material not used in any selected stroke

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.material_lock_unused"></a>

### bpy.ops.grease_pencil.material_lock_unused()

Lock and hide any material not used

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.material_reveal"></a>

### bpy.ops.grease_pencil.material_reveal()

Unhide all hidden Grease Pencil materials

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.material_select"></a>

### bpy.ops.grease_pencil.material_select(*, deselect=False)

Select/Deselect all Grease Pencil strokes using current material

**Parameters:**

**deselect** (bool) – Deselect, Unselect strokes (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.material_unlock_all"></a>

### bpy.ops.grease_pencil.material_unlock_all()

Unlock all Grease Pencil materials so that they can be edited

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.move_to_layer"></a>

### bpy.ops.grease_pencil.move_to_layer(*, target_layer_name='', target_group_name='', add_new_layer=False)

Move selected strokes to another layer

**Parameters:**

- **target_layer_name** (str) – Name, Target Grease Pencil Layer (optional, never None)
- **target_group_name** (str) – Target Group, Group to add the new layer to (optional, never None)
- **add_new_layer** (bool) – New Layer, Move selection to a new layer (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.outline"></a>

### bpy.ops.grease_pencil.outline(*, type='VIEW', radius=0.01, offset_factor=-1.0, corner_subdivisions=2)

Convert selected strokes to perimeter

**Parameters:**

- **type** (Literal['VIEW', 'FRONT', 'SIDE', 'TOP', 'CURSOR', 'CAMERA']) – Projection Mode, (optional)
- **radius** (float) – Radius, (in [0, 10], optional)
- **offset_factor** (float) – Offset Factor, (in [-1, 1], optional)
- **corner_subdivisions** (int) – Corner Subdivisions, (in [0, 10], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.paintmode_toggle"></a>

### bpy.ops.grease_pencil.paintmode_toggle(*, back=False)

Enter/Exit paint mode for Grease Pencil strokes

**Parameters:**

**back** (bool) – Return to Previous Mode, Return to previous mode (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.paste"></a>

### bpy.ops.grease_pencil.paste(*, type='ACTIVE', paste_back=False, keep_world_transform=False)

Paste Grease Pencil points or strokes from the internal clipboard to the active layer

**Parameters:**

- **type** (Literal['ACTIVE', 'LAYER']) – Type, (optional)
- **paste_back** (bool) – Paste on Back, Add pasted strokes behind all strokes (optional)
- **keep_world_transform** (bool) – Keep World Transform, Keep the world transform of strokes from the clipboard unchanged (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.pen"></a>

### bpy.ops.grease_pencil.pen(*, extend=False, deselect=False, toggle=False, deselect_all=False, select_passthrough=False, extrude_point=False, extrude_handle='VECTOR', delete_point=False, insert_point=False, move_segment=False, select_point=False, move_point=False, cycle_handle_type=False, size=0.01)

Construct and edit splines

**Parameters:**

- **extend** (bool) – Extend, Extend selection instead of deselecting everything first (optional)
- **deselect** (bool) – Deselect, Remove from selection (optional)
- **toggle** (bool) – Toggle Selection, Toggle the selection (optional)
- **deselect_all** (bool) – Deselect On Nothing, Deselect all when nothing under the cursor (optional)
- **select_passthrough** (bool) – Only Select Unselected, Ignore the select action when the element is already selected (optional)
- **extrude_point** (bool) – Extrude Point, Add a point connected to the last selected point (optional)
- **extrude_handle** (Literal['AUTO', 'VECTOR']) – Extrude Handle Type, Type of the extruded handle (optional)
- **delete_point** (bool) – Delete Point, Delete an existing point (optional)
- **insert_point** (bool) – Insert Point, Insert Point into a curve segment (optional)
- **move_segment** (bool) – Move Segment, Move an existing curve segment (optional)
- **select_point** (bool) – Select Point, Select a point or its handles (optional)
- **move_point** (bool) – Move Point, Move a point or its handles (optional)
- **cycle_handle_type** (bool) – Cycle Handle Type, Cycle between all four handle types (optional)
- **size** (float) – Size, Diameter of new points (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.primitive_arc"></a>

### bpy.ops.grease_pencil.primitive_arc(*, subdivision=62, type='ARC')

Create predefined Grease Pencil stroke arcs

**Parameters:**

- **subdivision** (int) – Subdivisions, Number of subdivisions per segment (in [0, inf], optional)
- **type** (Literal['BOX', 'LINE', 'POLYLINE', 'CIRCLE', 'ARC', 'CURVE']) – Type, Type of shape (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.primitive_box"></a>

### bpy.ops.grease_pencil.primitive_box(*, subdivision=3, type='BOX')

Create predefined Grease Pencil stroke boxes

**Parameters:**

- **subdivision** (int) – Subdivisions, Number of subdivisions per segment (in [0, inf], optional)
- **type** (Literal['BOX', 'LINE', 'POLYLINE', 'CIRCLE', 'ARC', 'CURVE']) – Type, Type of shape (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.primitive_circle"></a>

### bpy.ops.grease_pencil.primitive_circle(*, subdivision=94, type='CIRCLE')

Create predefined Grease Pencil stroke circles

**Parameters:**

- **subdivision** (int) – Subdivisions, Number of subdivisions per segment (in [0, inf], optional)
- **type** (Literal['BOX', 'LINE', 'POLYLINE', 'CIRCLE', 'ARC', 'CURVE']) – Type, Type of shape (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.primitive_curve"></a>

### bpy.ops.grease_pencil.primitive_curve(*, subdivision=62, type='CURVE')

Create predefined Grease Pencil stroke curve shapes

**Parameters:**

- **subdivision** (int) – Subdivisions, Number of subdivisions per segment (in [0, inf], optional)
- **type** (Literal['BOX', 'LINE', 'POLYLINE', 'CIRCLE', 'ARC', 'CURVE']) – Type, Type of shape (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.primitive_line"></a>

### bpy.ops.grease_pencil.primitive_line(*, subdivision=6, type='LINE')

Create predefined Grease Pencil stroke lines

**Parameters:**

- **subdivision** (int) – Subdivisions, Number of subdivisions per segment (in [0, inf], optional)
- **type** (Literal['BOX', 'LINE', 'POLYLINE', 'CIRCLE', 'ARC', 'CURVE']) – Type, Type of shape (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.primitive_polyline"></a>

### bpy.ops.grease_pencil.primitive_polyline(*, subdivision=6, type='POLYLINE')

Create predefined Grease Pencil stroke polylines

**Parameters:**

- **subdivision** (int) – Subdivisions, Number of subdivisions per segment (in [0, inf], optional)
- **type** (Literal['BOX', 'LINE', 'POLYLINE', 'CIRCLE', 'ARC', 'CURVE']) – Type, Type of shape (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.relative_layer_mask_add"></a>

### bpy.ops.grease_pencil.relative_layer_mask_add(*, mode='ABOVE')

Mask active layer with layer above or below

**Parameters:**

**mode** (Literal['ABOVE', 'BELOW']) – Mode, Which relative layer (above or below) to use as a mask (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/grease_pencil.py:39](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/grease_pencil.py#L39)

<a id="bpy.ops.grease_pencil.remove_fill_guides"></a>

### bpy.ops.grease_pencil.remove_fill_guides(*, mode='ALL_FRAMES')

Remove all the strokes that were created from the fill tool as guides

**Parameters:**

**mode** (Literal['ACTIVE_FRAME', 'ALL_FRAMES']) – Mode, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.reorder"></a>

### bpy.ops.grease_pencil.reorder(*, direction='TOP')

Change the display order of the selected strokes

**Parameters:**

**direction** (Literal['TOP', 'UP', 'DOWN', 'BOTTOM']) – Direction, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.reproject"></a>

### bpy.ops.grease_pencil.reproject(*, type='VIEW', keep_original=False, offset=0.0)

Reproject the selected strokes from the current viewpoint as if they had been newly drawn (e.g. to fix problems from accidental 3D cursor movement or accidental viewport changes, or for matching deforming geometry)

**Parameters:**

- **type** (Literal['FRONT', 'SIDE', 'TOP', 'VIEW', 'SURFACE', 'CURSOR']) –

  Projection Type, (optional)

  - `FRONT`
    Front – Reproject the strokes using the X-Z plane.
  - `SIDE`
    Side – Reproject the strokes using the Y-Z plane.
  - `TOP`
    Top – Reproject the strokes using the X-Y plane.
  - `VIEW`
    View – Reproject the strokes to end up on the same plane, as if drawn from the current viewpoint using ‘Cursor’ Stroke Placement.
  - `SURFACE`
    Surface – Reproject the strokes on to the scene geometry, as if drawn using ‘Surface’ placement.
  - `CURSOR`
    Cursor – Reproject the strokes using the orientation of 3D cursor.
- **keep_original** (bool) – Keep Original, Keep original strokes and create a copy before reprojecting (optional)
- **offset** (float) – Surface Offset, (in [0, 10], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.reset_uvs"></a>

### bpy.ops.grease_pencil.reset_uvs()

Reset UV transformation to default values

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.sculpt_paint"></a>

### bpy.ops.grease_pencil.sculpt_paint(*, stroke=None, mode='NORMAL', brush_toggle='None', pen_flip=False)

Sculpt strokes in the active Grease Pencil object

**Parameters:**

- **stroke** (`bpy_prop_collection`[`OperatorStrokeElement`] | None) – Stroke, (optional)
- **mode** (Literal['NORMAL', 'INVERT']) –

  Stroke Mode, Action taken when a paint stroke is made (optional)

  - `NORMAL`
    Regular – Apply brush normally.
  - `INVERT`
    Invert – Invert action of brush for duration of stroke.
- **brush_toggle** (Literal['None', 'SMOOTH', 'ERASE', 'MASK']) –

  Temporary Brush Toggle Type, Brush to use for duration of stroke (optional)

  - `None`
    None – Apply brush normally.
  - `SMOOTH`
    Smooth – Switch to smooth brush for duration of stroke.
  - `ERASE`
    Erase – Switch to erase brush for duration of stroke.
  - `MASK`
    Mask – Switch to mask brush for duration of stroke.
- **pen_flip** (bool) – Pen Flip, Whether a tablet’s eraser mode is being used (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.sculptmode_toggle"></a>

### bpy.ops.grease_pencil.sculptmode_toggle(*, back=False)

Enter/Exit sculpt mode for Grease Pencil strokes

**Parameters:**

**back** (bool) – Return to Previous Mode, Return to previous mode (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.select_all"></a>

### bpy.ops.grease_pencil.select_all(*, action='TOGGLE')

(De)select all visible strokes

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

<a id="bpy.ops.grease_pencil.select_alternate"></a>

### bpy.ops.grease_pencil.select_alternate(*, deselect_ends=False)

Select alternated points in strokes with already selected points

**Parameters:**

**deselect_ends** (bool) – Deselect Ends, (De)select the first and last point of each stroke (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.select_by_stroke_type"></a>

### bpy.ops.grease_pencil.select_by_stroke_type(*, type='STROKE', deselect=False)

Select/Deselect all strokes or fills

**Parameters:**

- **type** (Literal['STROKE', 'FILL']) – Type, (optional)
- **deselect** (bool) – Deselect, Unselect strokes (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.select_ends"></a>

### bpy.ops.grease_pencil.select_ends(*, amount_start=0, amount_end=1)

Select end points of strokes

**Parameters:**

- **amount_start** (int) – Amount Start, Number of points to select from the start (in [0, inf], optional)
- **amount_end** (int) – Amount End, Number of points to select from the end (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.select_fill"></a>

### bpy.ops.grease_pencil.select_fill()

Select all curves in a fill

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.select_less"></a>

### bpy.ops.grease_pencil.select_less()

Shrink the selection by one point

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.select_linked"></a>

### bpy.ops.grease_pencil.select_linked(*, deselect=False)

Select all points in curves with any point selection

**Parameters:**

**deselect** (bool) – Deselect linked, Deselect linked strokes (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.select_more"></a>

### bpy.ops.grease_pencil.select_more()

Grow the selection by one point

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.select_random"></a>

### bpy.ops.grease_pencil.select_random(*, ratio=0.5, seed=0, action='SELECT')

Selects random points from the current strokes selection

**Parameters:**

- **ratio** (float) – Ratio, Portion of items to select randomly (in [0, 1], optional)
- **seed** (int) – Random Seed, Seed for the random number generator (in [0, inf], optional)
- **action** (Literal['SELECT', 'DESELECT']) –

  Action, Selection action to execute (optional)

  - `SELECT`
    Select – Select all elements.
  - `DESELECT`
    Deselect – Deselect all elements.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.select_similar"></a>

### bpy.ops.grease_pencil.select_similar(*, mode='LAYER', threshold=0.1)

Select all strokes with similar characteristics

**Parameters:**

- **mode** (Literal['LAYER', 'MATERIAL', 'VERTEX_COLOR', 'RADIUS', 'OPACITY']) – Mode, (optional)
- **threshold** (float) – Threshold, (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.separate"></a>

### bpy.ops.grease_pencil.separate(*, mode='SELECTED')

Separate the selected geometry into a new Grease Pencil object

**Parameters:**

**mode** (Literal['SELECTED', 'MATERIAL', 'LAYER']) –

Mode, (optional)

- `SELECTED`
  Selection – Separate selected geometry.
- `MATERIAL`
  By Material – Separate by material.
- `LAYER`
  By Layer – Separate by layer.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.separate_fills"></a>

### bpy.ops.grease_pencil.separate_fills(*, individual=True)

Separate the selected strokes from current fill

**Parameters:**

**individual** (bool) – Individual, Create a separate fill for each individual stroke (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.set_active_material"></a>

### bpy.ops.grease_pencil.set_active_material()

Set the selected stroke material as the active material

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.set_corner_type"></a>

### bpy.ops.grease_pencil.set_corner_type(*, corner_type='SHARP', miter_angle=0.785398)

Set the corner type of the selected points

**Parameters:**

- **corner_type** (Literal['ROUND', 'FLAT', 'SHARP']) – Corner Type, (optional)
- **miter_angle** (float) – Miter Cut Angle, All corners sharper than the Miter angle will be cut flat (in [0, 3.14159], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.set_curve_resolution"></a>

### bpy.ops.grease_pencil.set_curve_resolution(*, resolution=12)

Set resolution of selected curves

**Parameters:**

**resolution** (int) – Resolution, The resolution to use for each curve segment (in [0, 10000], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.set_curve_type"></a>

### bpy.ops.grease_pencil.set_curve_type(*, type='POLY', use_handles=False)

Set type of selected curves

**Parameters:**

- **type** (Literal[[Curves Type Items](bpy_types_enum_items/curves_type_items.md#rna-enum-curves-type-items)]) – Type, Curve type (optional)
- **use_handles** (bool) – Handles, Take handle information into account in the conversion (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.set_handle_type"></a>

### bpy.ops.grease_pencil.set_handle_type(*, type='AUTO')

Set the handle type for Bézier curves

**Parameters:**

**type** (Literal['AUTO', 'VECTOR', 'ALIGN', 'FREE_ALIGN', 'TOGGLE_FREE_ALIGN']) –

Type, (optional)

- `AUTO`
  Auto – The location is automatically calculated to be smooth.
- `VECTOR`
  Vector – The location is calculated to point to the next/previous control point.
- `ALIGN`
  Align – The location is constrained to point in the opposite direction as the other handle.
- `FREE_ALIGN`
  Free – The handle can be moved anywhere, and does not influence the point’s other handle.
- `TOGGLE_FREE_ALIGN`
  Toggle Free/Align – Replace Free handles with Align, and all Align with Free handles.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.set_material"></a>

### bpy.ops.grease_pencil.set_material(*, slot='DEFAULT')

Set active material

**Parameters:**

**slot** (Literal['DEFAULT']) – Material Slot, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.set_selection_mode"></a>

### bpy.ops.grease_pencil.set_selection_mode(*, mode='POINT')

Change the selection mode for Grease Pencil strokes

**Parameters:**

**mode** (Literal[[Grease Pencil Selectmode Items](bpy_types_enum_items/grease_pencil_selectmode_items.md#rna-enum-grease-pencil-selectmode-items)]) – Mode, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.set_start_point"></a>

### bpy.ops.grease_pencil.set_start_point()

Select which point is the beginning of the curve

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.set_stroke_type"></a>

### bpy.ops.grease_pencil.set_stroke_type(*, type='STROKE')

Set the stroke type (stroke, fill, or both) of the selected strokes

**Parameters:**

**type** (Literal['STROKE', 'FILL', 'BOTH']) – Type, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.set_uniform_opacity"></a>

### bpy.ops.grease_pencil.set_uniform_opacity(*, opacity_stroke=1.0, opacity_fill=0.5)

Set all stroke points to same opacity

**Parameters:**

- **opacity_stroke** (float) – Stroke Opacity, (in [0, 1], optional)
- **opacity_fill** (float) – Fill Opacity, (in [0, 1], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.set_uniform_thickness"></a>

### bpy.ops.grease_pencil.set_uniform_thickness(*, thickness=0.1)

Set all stroke points to same thickness

**Parameters:**

**thickness** (float) – Thickness, Thickness (in [0, 1000], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.snap_cursor_to_selected"></a>

### bpy.ops.grease_pencil.snap_cursor_to_selected()

Snap cursor to center of selected points

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.snap_to_cursor"></a>

### bpy.ops.grease_pencil.snap_to_cursor(*, use_offset=True)

Snap selected points/strokes to the cursor

**Parameters:**

**use_offset** (bool) – With Offset, Offset the entire stroke instead of selected points only (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.snap_to_grid"></a>

### bpy.ops.grease_pencil.snap_to_grid()

Snap selected points to the nearest grid points

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.stroke_material_set"></a>

### bpy.ops.grease_pencil.stroke_material_set(*, material='')

Assign the active material slot to the selected strokes

**Parameters:**

**material** (str) – Material, Name of the material (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.stroke_merge_by_distance"></a>

### bpy.ops.grease_pencil.stroke_merge_by_distance(*, threshold=0.001, use_unselected=False)

Merge points by distance

**Parameters:**

- **threshold** (float) – Threshold, (in [0, 100], optional)
- **use_unselected** (bool) – Unselected, Use whole stroke, not only selected points (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.stroke_reset_vertex_color"></a>

### bpy.ops.grease_pencil.stroke_reset_vertex_color(*, mode='BOTH')

Reset vertex color for all or selected strokes

**Parameters:**

**mode** (Literal['STROKE', 'FILL', 'BOTH']) – Mode, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.stroke_simplify"></a>

### bpy.ops.grease_pencil.stroke_simplify(*, factor=0.01, length=0.05, distance=0.01, steps=1, mode='FIXED')

Simplify selected strokes

**Parameters:**

- **factor** (float) – Factor, (in [0, 100], optional)
- **length** (float) – Length, (in [0, 100], optional)
- **distance** (float) – Distance, (in [0, 100], optional)
- **steps** (int) – Steps, (in [0, 50], optional)
- **mode** (Literal['FIXED', 'ADAPTIVE', 'SAMPLE', 'MERGE']) –

  Mode, Method used for simplifying stroke points (optional)

  - `FIXED`
    Fixed – Delete alternating vertices in the stroke, except extremes.
  - `ADAPTIVE`
    Adaptive – Use a Ramer-Douglas-Peucker algorithm to simplify the stroke preserving main shape.
  - `SAMPLE`
    Sample – Re-sample the stroke with segments of the specified length.
  - `MERGE`
    Merge – Simplify the stroke by merging vertices closer than a given distance.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.stroke_smooth"></a>

### bpy.ops.grease_pencil.stroke_smooth(*, iterations=10, factor=1.0, smooth_ends=False, keep_shape=False, smooth_position=True, smooth_radius=True, smooth_opacity=False)

Smooth selected strokes

**Parameters:**

- **iterations** (int) – Iterations, (in [1, 100], optional)
- **factor** (float) – Factor, (in [0, 1], optional)
- **smooth_ends** (bool) – Smooth Endpoints, (optional)
- **keep_shape** (bool) – Keep Shape, (optional)
- **smooth_position** (bool) – Position, (optional)
- **smooth_radius** (bool) – Radius, (optional)
- **smooth_opacity** (bool) – Opacity, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.stroke_split"></a>

### bpy.ops.grease_pencil.stroke_split()

Split selected points to a new stroke

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.stroke_subdivide"></a>

### bpy.ops.grease_pencil.stroke_subdivide(*, number_cuts=1, only_selected=True)

Subdivide between continuous selected points of the stroke adding a point half way between them

**Parameters:**

- **number_cuts** (int) – Number of Cuts, (in [1, 32], optional)
- **only_selected** (bool) – Selected Points, Smooth only selected points in the stroke (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.stroke_subdivide_smooth"></a>

### bpy.ops.grease_pencil.stroke_subdivide_smooth(*, GREASE_PENCIL_OT_stroke_subdivide={}, GREASE_PENCIL_OT_stroke_smooth={})

Subdivide strokes and smooth them

**Parameters:**

- **GREASE_PENCIL_OT_stroke_subdivide** (dict[str, Any]) – Subdivide Stroke, Subdivide between continuous selected points of the stroke adding a point half way between them (optional, [`bpy.ops.grease_pencil.stroke_subdivide()`](#bpy.ops.grease_pencil.stroke_subdivide "bpy.ops.grease_pencil.stroke_subdivide") keyword arguments)
- **GREASE_PENCIL_OT_stroke_smooth** (dict[str, Any]) – Smooth Stroke, Smooth selected strokes (optional, [`bpy.ops.grease_pencil.stroke_smooth()`](#bpy.ops.grease_pencil.stroke_smooth "bpy.ops.grease_pencil.stroke_smooth") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.stroke_switch_direction"></a>

### bpy.ops.grease_pencil.stroke_switch_direction()

Change direction of the points of the selected strokes

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.stroke_trim"></a>

### bpy.ops.grease_pencil.stroke_trim(*, path=None, use_smooth_stroke=False, smooth_stroke_factor=0.75, smooth_stroke_radius=35)

Delete stroke points in between intersecting strokes

**Parameters:**

- **path** (`bpy_prop_collection`[`OperatorMousePath`] | None) – Path, (optional)
- **use_smooth_stroke** (bool) – Stabilize Stroke, Selection lags behind mouse and follows a smoother path (optional)
- **smooth_stroke_factor** (float) – Smooth Stroke Factor, Higher values give a smoother stroke (in [0.5, 0.99], optional)
- **smooth_stroke_radius** (int) – Smooth Stroke Radius, Minimum distance from last point before selection continues (in [10, 200], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.texture_gradient"></a>

### bpy.ops.grease_pencil.texture_gradient(*, xstart=0, xend=0, ystart=0, yend=0, flip=False, cursor=5)

Draw a line to set the fill material gradient for the selected strokes

**Parameters:**

- **xstart** (int) – X Start, (in [-inf, inf], optional)
- **xend** (int) – X End, (in [-inf, inf], optional)
- **ystart** (int) – Y Start, (in [-inf, inf], optional)
- **yend** (int) – Y End, (in [-inf, inf], optional)
- **flip** (bool) – Flip, (optional)
- **cursor** (int) – Cursor, Mouse cursor style to use during the modal operator (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.trace_image"></a>

### bpy.ops.grease_pencil.trace_image(*, target='NEW', threshold=0.5, turnpolicy='MINORITY', mode='SINGLE', use_current_frame=True, frame_number=0)

Extract Grease Pencil strokes from image

**Parameters:**

- **target** (Literal['NEW', 'SELECTED']) – Target Object, Target Grease Pencil (optional)
- **threshold** (float) – Color Threshold, Determine the lightness threshold above which strokes are generated (in [0, 1], optional)
- **turnpolicy** (Literal['FOREGROUND', 'BACKGROUND', 'LEFT', 'RIGHT', 'MINORITY', 'MAJORITY', 'RANDOM']) –

  Turn Policy, Determines how to resolve ambiguities during decomposition of bitmaps into paths (optional)

  - `FOREGROUND`
    Foreground – Prefers to connect foreground components.
  - `BACKGROUND`
    Background – Prefers to connect background components.
  - `LEFT`
    Left – Always take a left turn.
  - `RIGHT`
    Right – Always take a right turn.
  - `MINORITY`
    Minority – Prefers to connect the color that occurs least frequently in the local neighborhood of the current position.
  - `MAJORITY`
    Majority – Prefers to connect the color that occurs most frequently in the local neighborhood of the current position.
  - `RANDOM`
    Random – Choose pseudo-randomly.
- **mode** (Literal['SINGLE', 'SEQUENCE']) –

  Mode, Determines if trace simple image or full sequence (optional)

  - `SINGLE`
    Single – Trace the current frame of the image.
  - `SEQUENCE`
    Sequence – Trace full sequence.
- **use_current_frame** (bool) – Start At Current Frame, Trace Image starting in current image frame (optional)
- **frame_number** (int) – Trace Frame, Used to trace only one frame of the image sequence, set to zero to trace all (in [0, 9999], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.vertex_brush_stroke"></a>

### bpy.ops.grease_pencil.vertex_brush_stroke(*, stroke=None, mode='NORMAL', brush_toggle='None', pen_flip=False)

Draw on vertex colors in the active Grease Pencil object

**Parameters:**

- **stroke** (`bpy_prop_collection`[`OperatorStrokeElement`] | None) – Stroke, (optional)
- **mode** (Literal['NORMAL', 'INVERT']) –

  Stroke Mode, Action taken when a paint stroke is made (optional)

  - `NORMAL`
    Regular – Apply brush normally.
  - `INVERT`
    Invert – Invert action of brush for duration of stroke.
- **brush_toggle** (Literal['None', 'SMOOTH', 'ERASE', 'MASK']) –

  Temporary Brush Toggle Type, Brush to use for duration of stroke (optional)

  - `None`
    None – Apply brush normally.
  - `SMOOTH`
    Smooth – Switch to smooth brush for duration of stroke.
  - `ERASE`
    Erase – Switch to erase brush for duration of stroke.
  - `MASK`
    Mask – Switch to mask brush for duration of stroke.
- **pen_flip** (bool) – Pen Flip, Whether a tablet’s eraser mode is being used (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.vertex_color_brightness_contrast"></a>

### bpy.ops.grease_pencil.vertex_color_brightness_contrast(*, mode='BOTH', brightness=0.0, contrast=0.0)

Adjust vertex color brightness/contrast

**Parameters:**

- **mode** (Literal['STROKE', 'FILL', 'BOTH']) – Mode, (optional)
- **brightness** (float) – Brightness, (in [-1, 1], optional)
- **contrast** (float) – Contrast, (in [-1, 1], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.vertex_color_hsv"></a>

### bpy.ops.grease_pencil.vertex_color_hsv(*, mode='BOTH', h=0.5, s=1.0, v=1.0)

Adjust vertex color HSV values

**Parameters:**

- **mode** (Literal['STROKE', 'FILL', 'BOTH']) – Mode, (optional)
- **h** (float) – Hue, (in [0, 1], optional)
- **s** (float) – Saturation, (in [0, 2], optional)
- **v** (float) – Value, (in [0, 2], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.vertex_color_invert"></a>

### bpy.ops.grease_pencil.vertex_color_invert(*, mode='BOTH')

Invert RGB values

**Parameters:**

**mode** (Literal['STROKE', 'FILL', 'BOTH']) – Mode, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.vertex_color_levels"></a>

### bpy.ops.grease_pencil.vertex_color_levels(*, mode='BOTH', offset=0.0, gain=1.0)

Adjust levels of vertex colors

**Parameters:**

- **mode** (Literal['STROKE', 'FILL', 'BOTH']) – Mode, (optional)
- **offset** (float) – Offset, Value to add to colors (in [-1, 1], optional)
- **gain** (float) – Gain, Value to multiply colors by (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.vertex_color_set"></a>

### bpy.ops.grease_pencil.vertex_color_set(*, mode='BOTH', factor=1.0)

Set active color to all selected vertices

**Parameters:**

- **mode** (Literal['STROKE', 'FILL', 'BOTH']) – Mode, (optional)
- **factor** (float) – Factor, Mix Factor (in [0, 1], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.vertex_group_normalize"></a>

### bpy.ops.grease_pencil.vertex_group_normalize()

Normalize weights of the active vertex group

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.vertex_group_normalize_all"></a>

### bpy.ops.grease_pencil.vertex_group_normalize_all(*, lock_active=True)

Normalize the weights of all vertex groups, so that for each vertex, the sum of all weights is 1.0

**Parameters:**

**lock_active** (bool) – Lock Active, Keep the values of the active group while normalizing others (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.vertex_group_smooth"></a>

### bpy.ops.grease_pencil.vertex_group_smooth(*, factor=0.5, repeat=1)

Smooth the weights of the active vertex group

**Parameters:**

- **factor** (float) – Factor, (in [0, 1], optional)
- **repeat** (int) – Iterations, (in [1, 10000], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.vertexmode_toggle"></a>

### bpy.ops.grease_pencil.vertexmode_toggle(*, back=False)

Enter/Exit vertex paint mode for Grease Pencil strokes

**Parameters:**

**back** (bool) – Return to Previous Mode, Return to previous mode (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.weight_brush_stroke"></a>

### bpy.ops.grease_pencil.weight_brush_stroke(*, stroke=None, mode='NORMAL', brush_toggle='None', pen_flip=False)

Draw weight on stroke points in the active Grease Pencil object

**Parameters:**

- **stroke** (`bpy_prop_collection`[`OperatorStrokeElement`] | None) – Stroke, (optional)
- **mode** (Literal['NORMAL', 'INVERT']) –

  Stroke Mode, Action taken when a paint stroke is made (optional)

  - `NORMAL`
    Regular – Apply brush normally.
  - `INVERT`
    Invert – Invert action of brush for duration of stroke.
- **brush_toggle** (Literal['None', 'SMOOTH', 'ERASE', 'MASK']) –

  Temporary Brush Toggle Type, Brush to use for duration of stroke (optional)

  - `None`
    None – Apply brush normally.
  - `SMOOTH`
    Smooth – Switch to smooth brush for duration of stroke.
  - `ERASE`
    Erase – Switch to erase brush for duration of stroke.
  - `MASK`
    Mask – Switch to mask brush for duration of stroke.
- **pen_flip** (bool) – Pen Flip, Whether a tablet’s eraser mode is being used (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.weight_invert"></a>

### bpy.ops.grease_pencil.weight_invert()

Invert the weight of active vertex group

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.weight_sample"></a>

### bpy.ops.grease_pencil.weight_sample()

Set the weight of the Draw tool to the weight of the vertex under the mouse cursor

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.weight_toggle_direction"></a>

### bpy.ops.grease_pencil.weight_toggle_direction()

Toggle Add/Subtract for the weight paint draw tool

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.grease_pencil.weightmode_toggle"></a>

### bpy.ops.grease_pencil.weightmode_toggle(*, back=False)

Enter/Exit weight paint mode for Grease Pencil strokes

**Parameters:**

**back** (bool) – Return to Previous Mode, Return to previous mode (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]
