<!-- source: Blender Python API reference 5.2 / bpy.ops.curve.html -->

<a id="module-bpy.ops.curve"></a>

# Curve Operators

<a id="bpy.ops.curve.cyclic_toggle"></a>

### bpy.ops.curve.cyclic_toggle(*, direction='CYCLIC_U')

Make active spline closed/open loop

**Parameters:**

**direction** (Literal['CYCLIC_U', 'CYCLIC_V']) – Direction, Direction to make surface cyclic in (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curve.de_select_first"></a>

### bpy.ops.curve.de_select_first()

(De)select first of visible part of each NURBS

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curve.de_select_last"></a>

### bpy.ops.curve.de_select_last()

(De)select last of visible part of each NURBS

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curve.decimate"></a>

### bpy.ops.curve.decimate(*, ratio=1.0)

Simplify selected curves

**Parameters:**

**ratio** (float) – Ratio, (in [0, 1], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curve.delete"></a>

### bpy.ops.curve.delete(*, type='VERT')

Delete selected control points or segments

**Parameters:**

**type** (Literal['VERT', 'SEGMENT']) – Type, Which elements to delete (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curve.dissolve_verts"></a>

### bpy.ops.curve.dissolve_verts()

Delete selected control points, correcting surrounding handles

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curve.draw"></a>

### bpy.ops.curve.draw(*, error_threshold=0.0, fit_method='REFIT', corner_angle=1.22173, use_cyclic=True, stroke=None, wait_for_input=True)

Draw a freehand spline

**Parameters:**

- **error_threshold** (float) – Error, Error distance threshold (in object units) (in [0, 10], optional)
- **fit_method** (Literal[[Curve Fit Method Items](bpy_types_enum_items/curve_fit_method_items.md#rna-enum-curve-fit-method-items)]) – Fit Method, (optional)
- **corner_angle** (float) – Corner Angle, (in [0, 3.14159], optional)
- **use_cyclic** (bool) – Cyclic, (optional)
- **stroke** (`bpy_prop_collection`[`OperatorStrokeElement`] | None) – Stroke, (optional)
- **wait_for_input** (bool) – Wait for Input, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curve.duplicate"></a>

### bpy.ops.curve.duplicate()

Duplicate selected control points

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curve.duplicate_move"></a>

### bpy.ops.curve.duplicate_move(*, CURVE_OT_duplicate={}, TRANSFORM_OT_translate={})

Duplicate curve and move

**Parameters:**

- **CURVE_OT_duplicate** (dict[str, Any]) – Duplicate Curve, Duplicate selected control points (optional, [`bpy.ops.curve.duplicate()`](#bpy.ops.curve.duplicate "bpy.ops.curve.duplicate") keyword arguments)
- **TRANSFORM_OT_translate** (dict[str, Any]) – Move, Move selected items (optional, [`bpy.ops.transform.translate()`](bpy.ops.transform.md#bpy.ops.transform.translate "bpy.ops.transform.translate") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curve.extrude"></a>

### bpy.ops.curve.extrude(*, mode='TRANSLATION')

Extrude selected control point(s)

**Parameters:**

**mode** (Literal[[Transform Mode Type Items](bpy_types_enum_items/transform_mode_type_items.md#rna-enum-transform-mode-type-items)]) – Mode, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curve.extrude_move"></a>

### bpy.ops.curve.extrude_move(*, CURVE_OT_extrude={}, TRANSFORM_OT_translate={})

Extrude curve and move result

**Parameters:**

- **CURVE_OT_extrude** (dict[str, Any]) – Extrude, Extrude selected control point(s) (optional, [`bpy.ops.curve.extrude()`](#bpy.ops.curve.extrude "bpy.ops.curve.extrude") keyword arguments)
- **TRANSFORM_OT_translate** (dict[str, Any]) – Move, Move selected items (optional, [`bpy.ops.transform.translate()`](bpy.ops.transform.md#bpy.ops.transform.translate "bpy.ops.transform.translate") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curve.handle_type_set"></a>

### bpy.ops.curve.handle_type_set(*, type='AUTOMATIC')

Set type of handles for selected control points

**Parameters:**

**type** (Literal['AUTOMATIC', 'VECTOR', 'ALIGNED', 'FREE_ALIGN', 'TOGGLE_FREE_ALIGN']) – Type, Spline type (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curve.hide"></a>

### bpy.ops.curve.hide(*, unselected=False)

Hide (un)selected control points

**Parameters:**

**unselected** (bool) – Unselected, Hide unselected rather than selected (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curve.make_segment"></a>

### bpy.ops.curve.make_segment()

Join two curves by their selected ends

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curve.match_texture_space"></a>

### bpy.ops.curve.match_texture_space()

Match texture space to object’s bounding box

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curve.normals_make_consistent"></a>

### bpy.ops.curve.normals_make_consistent(*, calc_length=False)

Recalculate the direction of selected handles

**Parameters:**

**calc_length** (bool) – Length, Recalculate handle length (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curve.pen"></a>

### bpy.ops.curve.pen(*, extend=False, deselect=False, toggle=False, deselect_all=False, select_passthrough=False, extrude_point=False, extrude_handle='VECTOR', delete_point=False, insert_point=False, move_segment=False, select_point=False, move_point=False, close_spline=True, close_spline_method='OFF', toggle_vector=False, cycle_handle_type=False)

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
- **close_spline** (bool) – Close Spline, Make a spline cyclic by clicking endpoints (optional)
- **close_spline_method** (Literal['OFF', 'ON_PRESS', 'ON_CLICK']) –

  Close Spline Method, The condition for close spline to activate (optional)

  - `OFF`
    None.
  - `ON_PRESS`
    On Press – Move handles after closing the spline.
  - `ON_CLICK`
    On Click – Spline closes on release if not dragged.
- **toggle_vector** (bool) – Toggle Vector, Toggle between Vector and Auto handles (optional)
- **cycle_handle_type** (bool) – Cycle Handle Type, Cycle between all four handle types (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curve.primitive_bezier_circle_add"></a>

### bpy.ops.curve.primitive_bezier_circle_add(*, radius=1.0, enter_editmode=False, align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(0.0, 0.0, 0.0))

Construct a Bézier Circle

**Parameters:**

- **radius** (float) – Radius, (in [0, inf], optional)
- **enter_editmode** (bool) – Enter Edit Mode, Enter edit mode when adding this object (optional)
- **align** (Literal['WORLD', 'VIEW', 'CURSOR']) –

  Align, The alignment of the new object (optional)

  - `WORLD`
    World – Align the new object to the world.
  - `VIEW`
    View – Align the new object to the view.
  - `CURSOR`
    3D Cursor – Use the 3D cursor orientation for the new object.
- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Location for the newly added object (array of 3 items, in [-inf, inf], optional)
- **rotation** ([`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler") | Sequence[float]) – Rotation, Rotation for the newly added object (array of 3 items, in [-inf, inf], optional)
- **scale** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Scale, Scale for the newly added object (array of 3 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curve.primitive_bezier_curve_add"></a>

### bpy.ops.curve.primitive_bezier_curve_add(*, radius=1.0, enter_editmode=False, align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(0.0, 0.0, 0.0))

Construct a Bézier Curve

**Parameters:**

- **radius** (float) – Radius, (in [0, inf], optional)
- **enter_editmode** (bool) – Enter Edit Mode, Enter edit mode when adding this object (optional)
- **align** (Literal['WORLD', 'VIEW', 'CURSOR']) –

  Align, The alignment of the new object (optional)

  - `WORLD`
    World – Align the new object to the world.
  - `VIEW`
    View – Align the new object to the view.
  - `CURSOR`
    3D Cursor – Use the 3D cursor orientation for the new object.
- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Location for the newly added object (array of 3 items, in [-inf, inf], optional)
- **rotation** ([`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler") | Sequence[float]) – Rotation, Rotation for the newly added object (array of 3 items, in [-inf, inf], optional)
- **scale** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Scale, Scale for the newly added object (array of 3 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curve.primitive_nurbs_circle_add"></a>

### bpy.ops.curve.primitive_nurbs_circle_add(*, radius=1.0, enter_editmode=False, align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(0.0, 0.0, 0.0))

Construct a Nurbs Circle

**Parameters:**

- **radius** (float) – Radius, (in [0, inf], optional)
- **enter_editmode** (bool) – Enter Edit Mode, Enter edit mode when adding this object (optional)
- **align** (Literal['WORLD', 'VIEW', 'CURSOR']) –

  Align, The alignment of the new object (optional)

  - `WORLD`
    World – Align the new object to the world.
  - `VIEW`
    View – Align the new object to the view.
  - `CURSOR`
    3D Cursor – Use the 3D cursor orientation for the new object.
- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Location for the newly added object (array of 3 items, in [-inf, inf], optional)
- **rotation** ([`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler") | Sequence[float]) – Rotation, Rotation for the newly added object (array of 3 items, in [-inf, inf], optional)
- **scale** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Scale, Scale for the newly added object (array of 3 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curve.primitive_nurbs_curve_add"></a>

### bpy.ops.curve.primitive_nurbs_curve_add(*, radius=1.0, enter_editmode=False, align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(0.0, 0.0, 0.0))

Construct a Nurbs Curve

**Parameters:**

- **radius** (float) – Radius, (in [0, inf], optional)
- **enter_editmode** (bool) – Enter Edit Mode, Enter edit mode when adding this object (optional)
- **align** (Literal['WORLD', 'VIEW', 'CURSOR']) –

  Align, The alignment of the new object (optional)

  - `WORLD`
    World – Align the new object to the world.
  - `VIEW`
    View – Align the new object to the view.
  - `CURSOR`
    3D Cursor – Use the 3D cursor orientation for the new object.
- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Location for the newly added object (array of 3 items, in [-inf, inf], optional)
- **rotation** ([`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler") | Sequence[float]) – Rotation, Rotation for the newly added object (array of 3 items, in [-inf, inf], optional)
- **scale** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Scale, Scale for the newly added object (array of 3 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curve.primitive_nurbs_path_add"></a>

### bpy.ops.curve.primitive_nurbs_path_add(*, radius=1.0, enter_editmode=False, align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(0.0, 0.0, 0.0))

Construct a Path

**Parameters:**

- **radius** (float) – Radius, (in [0, inf], optional)
- **enter_editmode** (bool) – Enter Edit Mode, Enter edit mode when adding this object (optional)
- **align** (Literal['WORLD', 'VIEW', 'CURSOR']) –

  Align, The alignment of the new object (optional)

  - `WORLD`
    World – Align the new object to the world.
  - `VIEW`
    View – Align the new object to the view.
  - `CURSOR`
    3D Cursor – Use the 3D cursor orientation for the new object.
- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Location for the newly added object (array of 3 items, in [-inf, inf], optional)
- **rotation** ([`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler") | Sequence[float]) – Rotation, Rotation for the newly added object (array of 3 items, in [-inf, inf], optional)
- **scale** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Scale, Scale for the newly added object (array of 3 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curve.radius_set"></a>

### bpy.ops.curve.radius_set(*, radius=1.0)

Set per-point radius which is used for bevel tapering

**Parameters:**

**radius** (float) – Radius, (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curve.reveal"></a>

### bpy.ops.curve.reveal(*, select=True)

Reveal hidden control points

**Parameters:**

**select** (bool) – Select, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curve.select_all"></a>

### bpy.ops.curve.select_all(*, action='TOGGLE')

(De)select all control points

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

<a id="bpy.ops.curve.select_less"></a>

### bpy.ops.curve.select_less()

Deselect control points at the boundary of each selection region

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curve.select_linked"></a>

### bpy.ops.curve.select_linked()

Select all control points linked to the current selection

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curve.select_linked_pick"></a>

### bpy.ops.curve.select_linked_pick(*, deselect=False)

Select all control points linked to already selected ones

**Parameters:**

**deselect** (bool) – Deselect, Deselect linked control points rather than selecting them (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curve.select_more"></a>

### bpy.ops.curve.select_more()

Select control points at the boundary of each selection region

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curve.select_next"></a>

### bpy.ops.curve.select_next()

Select control points following already selected ones along the curves

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curve.select_nth"></a>

### bpy.ops.curve.select_nth(*, skip=1, nth=1, offset=0)

Deselect every Nth point starting from the active one

**Parameters:**

- **skip** (int) – Deselected, Number of deselected elements in the repetitive sequence (in [1, inf], optional)
- **nth** (int) – Selected, Number of selected elements in the repetitive sequence (in [1, inf], optional)
- **offset** (int) – Offset, Offset from the starting point (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curve.select_previous"></a>

### bpy.ops.curve.select_previous()

Select control points preceding already selected ones along the curves

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curve.select_random"></a>

### bpy.ops.curve.select_random(*, ratio=0.5, seed=0, action='SELECT')

Randomly select some control points

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

<a id="bpy.ops.curve.select_row"></a>

### bpy.ops.curve.select_row()

Select a row of control points including active one. Successive use on the same point switches between U/V directions

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curve.select_similar"></a>

### bpy.ops.curve.select_similar(*, type='WEIGHT', compare='EQUAL', threshold=0.1)

Select similar curve points by property type

**Parameters:**

- **type** (Literal['TYPE', 'RADIUS', 'WEIGHT', 'DIRECTION']) – Type, (optional)
- **compare** (Literal['EQUAL', 'GREATER', 'LESS']) – Compare, (optional)
- **threshold** (float) – Threshold, (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curve.separate"></a>

### bpy.ops.curve.separate()

Separate selected points from connected unselected points into a new object

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curve.shade_flat"></a>

### bpy.ops.curve.shade_flat()

Set shading to flat

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curve.shade_smooth"></a>

### bpy.ops.curve.shade_smooth()

Set shading to smooth

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curve.shortest_path_pick"></a>

### bpy.ops.curve.shortest_path_pick()

Select shortest path between two selections

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curve.smooth"></a>

### bpy.ops.curve.smooth()

Flatten angles of selected points

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curve.smooth_radius"></a>

### bpy.ops.curve.smooth_radius()

Interpolate radii of selected points

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curve.smooth_tilt"></a>

### bpy.ops.curve.smooth_tilt()

Interpolate tilt of selected points

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curve.smooth_weight"></a>

### bpy.ops.curve.smooth_weight()

Interpolate weight of selected points

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curve.spin"></a>

### bpy.ops.curve.spin(*, center=(0.0, 0.0, 0.0), axis=(0.0, 0.0, 0.0))

Extrude selected boundary row around pivot point and current view axis

**Parameters:**

- **center** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Center, Center in global view space (array of 3 items, in [-inf, inf], optional)
- **axis** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Axis, Axis in global view space (array of 3 items, in [-1, 1], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curve.spline_type_set"></a>

### bpy.ops.curve.spline_type_set(*, type='POLY', use_handles=False)

Set type of active spline

**Parameters:**

- **type** (Literal['POLY', 'BEZIER', 'NURBS']) – Type, Spline type (optional)
- **use_handles** (bool) – Handles, Use handles when converting Bézier curves into polygons (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curve.spline_weight_set"></a>

### bpy.ops.curve.spline_weight_set(*, weight=1.0)

Set softbody goal weight for selected points

**Parameters:**

**weight** (float) – Weight, (in [0, 1], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curve.split"></a>

### bpy.ops.curve.split()

Split off selected points from connected unselected points

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curve.subdivide"></a>

### bpy.ops.curve.subdivide(*, number_cuts=1)

Subdivide selected segments

**Parameters:**

**number_cuts** (int) – Number of Cuts, (in [1, 1000], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curve.switch_direction"></a>

### bpy.ops.curve.switch_direction()

Switch direction of selected splines

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curve.tilt_clear"></a>

### bpy.ops.curve.tilt_clear()

Clear the tilt of selected control points

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curve.vertex_add"></a>

### bpy.ops.curve.vertex_add(*, location=(0.0, 0.0, 0.0))

Add a new control point (linked to only selected end-curve one, if any)

**Parameters:**

**location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Location to add new vertex at (array of 3 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]
