<!-- source: Blender Python API reference 5.2 / bpy.ops.curves.html -->

<a id="module-bpy.ops.curves"></a>

# Curves Operators

<a id="bpy.ops.curves.add_bezier"></a>

### bpy.ops.curves.add_bezier(*, radius=1.0, enter_editmode=False, align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(0.0, 0.0, 0.0))

Add new Bézier curve

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

<a id="bpy.ops.curves.add_circle"></a>

### bpy.ops.curves.add_circle(*, radius=1.0, enter_editmode=False, align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(0.0, 0.0, 0.0))

Add new circle curve

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

<a id="bpy.ops.curves.attribute_set"></a>

### bpy.ops.curves.attribute_set(*, value_float=0.0, value_float_vector_2d=(0.0, 0.0), value_float_vector_3d=(0.0, 0.0, 0.0), value_float_vector_4d=(0.0, 0.0, 0.0, 0.0), value_int=0, value_int_vector_2d=(0, 0), value_color=(1.0, 1.0, 1.0, 1.0), value_bool=False)

Set values of the active attribute for selected elements

**Parameters:**

- **value_float** (float) – Value, (in [-inf, inf], optional)
- **value_float_vector_2d** (Sequence[float]) – Value, (array of 2 items, in [-inf, inf], optional)
- **value_float_vector_3d** (Sequence[float]) – Value, (array of 3 items, in [-inf, inf], optional)
- **value_float_vector_4d** (Sequence[float]) – Value, (array of 4 items, in [-inf, inf], optional)
- **value_int** (int) – Value, (in [-inf, inf], optional)
- **value_int_vector_2d** (Sequence[int]) – Value, (array of 2 items, in [-inf, inf], optional)
- **value_color** (Sequence[float]) – Value, (array of 4 items, in [-inf, inf], optional)
- **value_bool** (bool) – Value, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curves.convert_from_particle_system"></a>

### bpy.ops.curves.convert_from_particle_system()

Add a new curves object based on the current state of the particle system

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curves.convert_to_particle_system"></a>

### bpy.ops.curves.convert_to_particle_system()

Add a new or update an existing hair particle system on the surface object

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curves.curve_type_set"></a>

### bpy.ops.curves.curve_type_set(*, type='POLY', use_handles=False)

Set type of selected curves

**Parameters:**

- **type** (Literal[[Curves Type Items](bpy_types_enum_items/curves_type_items.md#rna-enum-curves-type-items)]) – Type, Curve type (optional)
- **use_handles** (bool) – Handles, Take handle information into account in the conversion (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curves.cyclic_toggle"></a>

### bpy.ops.curves.cyclic_toggle()

Make active curve closed/open loop

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curves.delete"></a>

### bpy.ops.curves.delete()

Remove selected control points or curves

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curves.draw"></a>

### bpy.ops.curves.draw(*, error_threshold=0.0, fit_method='REFIT', corner_angle=1.22173, use_cyclic=True, stroke=None, wait_for_input=True, is_curve_2d=False, bezier_as_nurbs=False)

Draw a freehand curve

**Parameters:**

- **error_threshold** (float) – Error, Error distance threshold (in object units) (in [0, 10], optional)
- **fit_method** (Literal[[Curve Fit Method Items](bpy_types_enum_items/curve_fit_method_items.md#rna-enum-curve-fit-method-items)]) – Fit Method, (optional)
- **corner_angle** (float) – Corner Angle, (in [0, 3.14159], optional)
- **use_cyclic** (bool) – Cyclic, (optional)
- **stroke** (`bpy_prop_collection`[`OperatorStrokeElement`] | None) – Stroke, (optional)
- **wait_for_input** (bool) – Wait for Input, (optional)
- **is_curve_2d** (bool) – Curve 2D, (optional)
- **bezier_as_nurbs** (bool) – As NURBS, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curves.duplicate"></a>

### bpy.ops.curves.duplicate()

Copy selected points or curves

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curves.duplicate_move"></a>

### bpy.ops.curves.duplicate_move(*, CURVES_OT_duplicate={}, TRANSFORM_OT_translate={})

Make copies of selected elements and move them

**Parameters:**

- **CURVES_OT_duplicate** (dict[str, Any]) – Duplicate, Copy selected points or curves (optional, [`bpy.ops.curves.duplicate()`](#bpy.ops.curves.duplicate "bpy.ops.curves.duplicate") keyword arguments)
- **TRANSFORM_OT_translate** (dict[str, Any]) – Move, Move selected items (optional, [`bpy.ops.transform.translate()`](bpy.ops.transform.md#bpy.ops.transform.translate "bpy.ops.transform.translate") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curves.extrude"></a>

### bpy.ops.curves.extrude()

Extrude selected control point(s)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curves.extrude_move"></a>

### bpy.ops.curves.extrude_move(*, CURVES_OT_extrude={}, TRANSFORM_OT_translate={})

Extrude curve and move result

**Parameters:**

- **CURVES_OT_extrude** (dict[str, Any]) – Extrude, Extrude selected control point(s) (optional, [`bpy.ops.curves.extrude()`](#bpy.ops.curves.extrude "bpy.ops.curves.extrude") keyword arguments)
- **TRANSFORM_OT_translate** (dict[str, Any]) – Move, Move selected items (optional, [`bpy.ops.transform.translate()`](bpy.ops.transform.md#bpy.ops.transform.translate "bpy.ops.transform.translate") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curves.handle_type_set"></a>

### bpy.ops.curves.handle_type_set(*, type='AUTO')

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

<a id="bpy.ops.curves.pen"></a>

### bpy.ops.curves.pen(*, extend=False, deselect=False, toggle=False, deselect_all=False, select_passthrough=False, extrude_point=False, extrude_handle='VECTOR', delete_point=False, insert_point=False, move_segment=False, select_point=False, move_point=False, cycle_handle_type=False, size=0.01)

Construct and edit Bézier curves

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

<a id="bpy.ops.curves.sculptmode_toggle"></a>

### bpy.ops.curves.sculptmode_toggle()

Enter/Exit sculpt mode for curves

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curves.select_all"></a>

### bpy.ops.curves.select_all(*, action='TOGGLE')

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

<a id="bpy.ops.curves.select_ends"></a>

### bpy.ops.curves.select_ends(*, amount_start=0, amount_end=1)

Select end points of curves

**Parameters:**

- **amount_start** (int) – Amount Front, Number of points to select from the front (in [0, inf], optional)
- **amount_end** (int) – Amount Back, Number of points to select from the back (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curves.select_less"></a>

### bpy.ops.curves.select_less()

Shrink the selection by one point

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curves.select_linked"></a>

### bpy.ops.curves.select_linked()

Select all points in curves with any point selection

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curves.select_linked_pick"></a>

### bpy.ops.curves.select_linked_pick(*, deselect=False)

Select all points in the curve under the cursor

**Parameters:**

**deselect** (bool) – Deselect, Deselect linked control points rather than selecting them (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curves.select_more"></a>

### bpy.ops.curves.select_more()

Grow the selection by one point

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curves.select_random"></a>

### bpy.ops.curves.select_random(*, seed=0, probability=0.5)

Randomize existing selection or create new random selection

**Parameters:**

- **seed** (int) – Seed, Source of randomness (in [-inf, inf], optional)
- **probability** (float) – Probability, Chance of every point or curve being included in the selection (in [0, 1], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curves.separate"></a>

### bpy.ops.curves.separate()

Separate selected geometry into a new object

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curves.set_selection_domain"></a>

### bpy.ops.curves.set_selection_domain(*, domain='POINT')

Change the mode used for selection masking in curves sculpt mode

**Parameters:**

**domain** (Literal[[Attribute Curves Domain Items](bpy_types_enum_items/attribute_curves_domain_items.md#rna-enum-attribute-curves-domain-items)]) – Domain, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curves.snap_curves_to_surface"></a>

### bpy.ops.curves.snap_curves_to_surface(*, attach_mode='NEAREST')

Move curves so that the first point is exactly on the surface mesh

**Parameters:**

**attach_mode** (Literal['NEAREST', 'DEFORM']) –

Attach Mode, How to find the point on the surface to attach to (optional)

- `NEAREST`
  Nearest – Find the closest point on the surface for the root point of every curve and move the root there.
- `DEFORM`
  Deform – Re-attach curves to a deformed surface using the existing attachment information. This only works when the topology of the surface mesh has not changed.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curves.split"></a>

### bpy.ops.curves.split()

Split selected points

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curves.subdivide"></a>

### bpy.ops.curves.subdivide(*, number_cuts=1)

Subdivide selected curve segments

**Parameters:**

**number_cuts** (int) – Number of Cuts, (in [1, 1000], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curves.surface_set"></a>

### bpy.ops.curves.surface_set()

Use the active object as surface for selected curves objects and set it as the parent

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curves.switch_direction"></a>

### bpy.ops.curves.switch_direction()

Reverse the direction of the selected curves

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.curves.tilt_clear"></a>

### bpy.ops.curves.tilt_clear()

Clear the tilt of selected control points

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]
