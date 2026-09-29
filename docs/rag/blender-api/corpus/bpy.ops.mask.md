<!-- source: Blender Python API reference 5.2 / bpy.ops.mask.html -->

<a id="module-bpy.ops.mask"></a>

# Mask Operators

<a id="bpy.ops.mask.add_feather_vertex"></a>

### bpy.ops.mask.add_feather_vertex(*, location=(0.0, 0.0))

Add vertex to feather

**Parameters:**

**location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Location of vertex in normalized space (array of 2 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mask.add_feather_vertex_slide"></a>

### bpy.ops.mask.add_feather_vertex_slide(*, MASK_OT_add_feather_vertex={}, MASK_OT_slide_point={})

Add new vertex to feather and slide it

**Parameters:**

- **MASK_OT_add_feather_vertex** (dict[str, Any]) – Add Feather Vertex, Add vertex to feather (optional, [`bpy.ops.mask.add_feather_vertex()`](#bpy.ops.mask.add_feather_vertex "bpy.ops.mask.add_feather_vertex") keyword arguments)
- **MASK_OT_slide_point** (dict[str, Any]) – Slide Point, Slide control points (optional, [`bpy.ops.mask.slide_point()`](#bpy.ops.mask.slide_point "bpy.ops.mask.slide_point") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mask.add_vertex"></a>

### bpy.ops.mask.add_vertex(*, location=(0.0, 0.0))

Add vertex to active spline

**Parameters:**

**location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Location of vertex in normalized space (array of 2 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mask.add_vertex_slide"></a>

### bpy.ops.mask.add_vertex_slide(*, MASK_OT_add_vertex={}, MASK_OT_slide_point={})

Add new vertex and slide it

**Parameters:**

- **MASK_OT_add_vertex** (dict[str, Any]) – Add Vertex, Add vertex to active spline (optional, [`bpy.ops.mask.add_vertex()`](#bpy.ops.mask.add_vertex "bpy.ops.mask.add_vertex") keyword arguments)
- **MASK_OT_slide_point** (dict[str, Any]) – Slide Point, Slide control points (optional, [`bpy.ops.mask.slide_point()`](#bpy.ops.mask.slide_point "bpy.ops.mask.slide_point") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mask.copy_splines"></a>

### bpy.ops.mask.copy_splines()

Copy the selected splines to the internal clipboard

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mask.cyclic_toggle"></a>

### bpy.ops.mask.cyclic_toggle()

Toggle cyclic for selected splines

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mask.delete"></a>

### bpy.ops.mask.delete(*, confirm=True)

Delete selected control points or splines

**Parameters:**

**confirm** (bool) – Confirm, Prompt for confirmation (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mask.duplicate"></a>

### bpy.ops.mask.duplicate()

Duplicate selected control points and segments between them

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mask.duplicate_move"></a>

### bpy.ops.mask.duplicate_move(*, MASK_OT_duplicate={}, TRANSFORM_OT_translate={})

Duplicate mask and move

**Parameters:**

- **MASK_OT_duplicate** (dict[str, Any]) – Duplicate Mask, Duplicate selected control points and segments between them (optional, [`bpy.ops.mask.duplicate()`](#bpy.ops.mask.duplicate "bpy.ops.mask.duplicate") keyword arguments)
- **TRANSFORM_OT_translate** (dict[str, Any]) – Move, Move selected items (optional, [`bpy.ops.transform.translate()`](bpy.ops.transform.md#bpy.ops.transform.translate "bpy.ops.transform.translate") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mask.feather_weight_clear"></a>

### bpy.ops.mask.feather_weight_clear()

Reset the feather weight to zero

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mask.handle_type_set"></a>

### bpy.ops.mask.handle_type_set(*, type='AUTO')

Set type of handles for selected control points

**Parameters:**

**type** (Literal['AUTO', 'VECTOR', 'ALIGNED', 'ALIGNED_DOUBLESIDE', 'FREE']) – Type, Spline type (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mask.hide_view_clear"></a>

### bpy.ops.mask.hide_view_clear(*, select=True)

Reveal temporarily hidden mask layers

**Parameters:**

**select** (bool) – Select, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mask.hide_view_set"></a>

### bpy.ops.mask.hide_view_set(*, unselected=False)

Temporarily hide mask layers

**Parameters:**

**unselected** (bool) – Unselected, Hide unselected rather than selected layers (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mask.layer_move"></a>

### bpy.ops.mask.layer_move(*, direction='UP')

Move the active layer up/down in the list

**Parameters:**

**direction** (Literal['UP', 'DOWN']) – Direction, Direction to move the active layer (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mask.layer_new"></a>

### bpy.ops.mask.layer_new(*, name='')

Add new mask layer for masking

**Parameters:**

**name** (str) – Name, Name of new mask layer (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mask.layer_remove"></a>

### bpy.ops.mask.layer_remove()

Remove mask layer

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mask.move_to_layer"></a>

### bpy.ops.mask.move_to_layer(*, target_layer_name='', add_new_layer=False)

Move the active spline to layer

**Parameters:**

- **target_layer_name** (str) – Name, Target Mask Layer (optional, never None)
- **add_new_layer** (bool) – New Layer, Move selection to a new layer (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mask.new"></a>

### bpy.ops.mask.new(*, name='')

Create new mask

**Parameters:**

**name** (str) – Name, Name of new mask (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mask.normals_make_consistent"></a>

### bpy.ops.mask.normals_make_consistent()

Recalculate the direction of selected handles

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mask.parent_clear"></a>

### bpy.ops.mask.parent_clear()

Clear the mask’s parenting

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mask.parent_set"></a>

### bpy.ops.mask.parent_set()

Set the mask’s parenting

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mask.paste_splines"></a>

### bpy.ops.mask.paste_splines()

Paste splines from the internal clipboard

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mask.primitive_circle_add"></a>

### bpy.ops.mask.primitive_circle_add(*, size=100.0, location=(0.0, 0.0))

Add new circle-shaped spline

**Parameters:**

- **size** (float) – Size, Size of new primitive (in [-inf, inf], optional)
- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Location of new primitive (array of 2 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mask.primitive_square_add"></a>

### bpy.ops.mask.primitive_square_add(*, size=100.0, location=(0.0, 0.0))

Add new square-shaped spline

**Parameters:**

- **size** (float) – Size, Size of new primitive (in [-inf, inf], optional)
- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Location of new primitive (array of 2 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mask.select"></a>

### bpy.ops.mask.select(*, extend=False, deselect=False, toggle=False, deselect_all=False, select_passthrough=False, location=(0.0, 0.0))

Select spline points

**Parameters:**

- **extend** (bool) – Extend, Extend selection instead of deselecting everything first (optional)
- **deselect** (bool) – Deselect, Remove from selection (optional)
- **toggle** (bool) – Toggle Selection, Toggle the selection (optional)
- **deselect_all** (bool) – Deselect On Nothing, Deselect all when nothing under the cursor (optional)
- **select_passthrough** (bool) – Only Select Unselected, Ignore the select action when the element is already selected (optional)
- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Location of vertex in normalized space (array of 2 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mask.select_all"></a>

### bpy.ops.mask.select_all(*, action='TOGGLE')

Change selection of all curve points

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

<a id="bpy.ops.mask.select_box"></a>

### bpy.ops.mask.select_box(*, xmin=0, xmax=0, ymin=0, ymax=0, wait_for_input=True, mode='SET')

Select curve points using box selection

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

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mask.select_circle"></a>

### bpy.ops.mask.select_circle(*, x=0, y=0, radius=25, wait_for_input=True, mode='SET')

Select curve points using circle selection

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

<a id="bpy.ops.mask.select_lasso"></a>

### bpy.ops.mask.select_lasso(*, path=None, use_smooth_stroke=False, smooth_stroke_factor=0.75, smooth_stroke_radius=35, mode='SET')

Select curve points using lasso selection

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

<a id="bpy.ops.mask.select_less"></a>

### bpy.ops.mask.select_less()

Deselect spline points at the boundary of each selection region

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mask.select_linked"></a>

### bpy.ops.mask.select_linked()

Select all curve points linked to already selected ones

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mask.select_linked_pick"></a>

### bpy.ops.mask.select_linked_pick(*, deselect=False)

(De)select all points linked to the curve under the mouse cursor

**Parameters:**

**deselect** (bool) – Deselect, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mask.select_more"></a>

### bpy.ops.mask.select_more()

Select more spline points connected to initial selection

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mask.shape_key_clear"></a>

### bpy.ops.mask.shape_key_clear()

Remove mask shape keyframe for active mask layer at the current frame

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mask.shape_key_feather_reset"></a>

### bpy.ops.mask.shape_key_feather_reset()

Reset feather weights on all selected points animation values

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mask.shape_key_insert"></a>

### bpy.ops.mask.shape_key_insert()

Insert mask shape keyframe for active mask layer at the current frame

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mask.shape_key_rekey"></a>

### bpy.ops.mask.shape_key_rekey(*, location=True, feather=True)

Recalculate animation data on selected points for frames selected in the dopesheet

**Parameters:**

- **location** (bool) – Location, (optional)
- **feather** (bool) – Feather, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mask.slide_point"></a>

### bpy.ops.mask.slide_point(*, slide_feather=False, is_new_point=False)

Slide control points

**Parameters:**

- **slide_feather** (bool) – Slide Feather, First try to slide feather instead of vertex (optional)
- **is_new_point** (bool) – Slide New Point, Newly created vertex is being slid (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mask.slide_spline_curvature"></a>

### bpy.ops.mask.slide_spline_curvature()

Slide a point on the spline to define its curvature

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mask.switch_direction"></a>

### bpy.ops.mask.switch_direction()

Switch direction of selected splines

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]
