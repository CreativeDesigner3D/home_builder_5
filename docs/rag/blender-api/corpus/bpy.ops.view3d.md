<!-- source: Blender Python API reference 5.2 / bpy.ops.view3d.html -->

<a id="module-bpy.ops.view3d"></a>

# View3D Operators

<a id="bpy.ops.view3d.bone_select_menu"></a>

### bpy.ops.view3d.bone_select_menu(*, name='', extend=False, deselect=False, toggle=False)

Menu bone selection

**Parameters:**

- **name** (str) – Bone Name, (optional)
- **extend** (bool) – Extend, (optional)
- **deselect** (bool) – Deselect, (optional)
- **toggle** (bool) – Toggle, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.camera_background_image_add"></a>

### bpy.ops.view3d.camera_background_image_add(*, filepath='', relative_path=True, name='', session_uid=0)

Add a new background image to the active camera

**Parameters:**

- **filepath** (str) – Filepath, Path to image file (optional, never None, blend relative `//` prefix supported)
- **relative_path** (bool) – Relative Path, Select the file relative to the blend file (optional)
- **name** (str) – Name, Name of the data-block to use by the operator (optional, never None)
- **session_uid** (int) – Session UID, Session UID of the data-block to use by the operator (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.camera_background_image_remove"></a>

### bpy.ops.view3d.camera_background_image_remove(*, index=0)

Remove a background image from the camera

**Parameters:**

**index** (int) – Index, Background image index to remove (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.camera_to_view"></a>

### bpy.ops.view3d.camera_to_view()

Set camera view to active view

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.camera_to_view_selected"></a>

### bpy.ops.view3d.camera_to_view_selected()

Move the camera so selected objects are framed

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.clear_render_border"></a>

### bpy.ops.view3d.clear_render_border()

Clear the boundaries of the border render and disable border render

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.clip_border"></a>

### bpy.ops.view3d.clip_border(*, xmin=0, xmax=0, ymin=0, ymax=0, wait_for_input=True)

Set the view clipping region

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

<a id="bpy.ops.view3d.copybuffer"></a>

### bpy.ops.view3d.copybuffer()

Copy the selected objects to the internal clipboard

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.cursor3d"></a>

### bpy.ops.view3d.cursor3d(*, use_depth=True, orientation='VIEW')

Set the location of the 3D cursor

**Parameters:**

- **use_depth** (bool) – Surface Project, Project onto the surface (optional)
- **orientation** (Literal['NONE', 'VIEW', 'XFORM', 'GEOM']) –

  Orientation, Preset viewpoint to use (optional)

  - `NONE`
    None – Leave orientation unchanged.
  - `VIEW`
    View – Orient to the viewport.
  - `XFORM`
    Transform – Orient to the current transform setting.
  - `GEOM`
    Geometry – Match the surface normal.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.dolly"></a>

### bpy.ops.view3d.dolly(*, mx=0, my=0, delta=0, use_cursor_init=True)

Dolly in/out in the view

**Parameters:**

- **mx** (int) – Region Position X, (in [0, inf], optional)
- **my** (int) – Region Position Y, (in [0, inf], optional)
- **delta** (int) – Delta, (in [-inf, inf], optional)
- **use_cursor_init** (bool) – Use Mouse Position, Allow the initial mouse position to be used (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.drop_world"></a>

### bpy.ops.view3d.drop_world(*, name='', session_uid=0)

Drop a world into the scene

**Parameters:**

- **name** (str) – Name, Name of the data-block to use by the operator (optional, never None)
- **session_uid** (int) – Session UID, Session UID of the data-block to use by the operator (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.edit_mesh_extrude_individual_move"></a>

### bpy.ops.view3d.edit_mesh_extrude_individual_move()

Extrude each individual face separately along local normals

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/view3d.py:30](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/view3d.py#L30)

<a id="bpy.ops.view3d.edit_mesh_extrude_manifold_normal"></a>

### bpy.ops.view3d.edit_mesh_extrude_manifold_normal()

Extrude manifold region along normals

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/view3d.py:198](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/view3d.py#L198)

<a id="bpy.ops.view3d.edit_mesh_extrude_move_normal"></a>

### bpy.ops.view3d.edit_mesh_extrude_move_normal(*, dissolve_and_intersect=False)

Extrude region together along the average normal

**Parameters:**

**dissolve_and_intersect** (bool) – Dissolve and Intersect, Dissolves adjacent faces and intersects new geometry (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/view3d.py:166](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/view3d.py#L166)

<a id="bpy.ops.view3d.edit_mesh_extrude_move_shrink_fatten"></a>

### bpy.ops.view3d.edit_mesh_extrude_move_shrink_fatten()

Extrude region together along local normals

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/view3d.py:182](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/view3d.py#L182)

<a id="bpy.ops.view3d.fly"></a>

### bpy.ops.view3d.fly()

Interactively fly around the scene

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.interactive_add"></a>

### bpy.ops.view3d.interactive_add(*, primitive_type='CUBE', plane_origin_base='EDGE', plane_origin_depth='EDGE', plane_aspect_base='FREE', plane_aspect_depth='FREE', wait_for_input=True)

Interactively add an object

**Parameters:**

- **primitive_type** (Literal['CUBE', 'CYLINDER', 'CONE', 'SPHERE_UV', 'SPHERE_ICO']) – Primitive, (optional)
- **plane_origin_base** (Literal['EDGE', 'CENTER']) –

  Origin, The initial position for placement (optional)

  - `EDGE`
    Edge – Start placing the edge position.
  - `CENTER`
    Center – Start placing the center position.
- **plane_origin_depth** (Literal['EDGE', 'CENTER']) –

  Origin, The initial position for placement (optional)

  - `EDGE`
    Edge – Start placing the edge position.
  - `CENTER`
    Center – Start placing the center position.
- **plane_aspect_base** (Literal['FREE', 'FIXED']) –

  Aspect, The initial aspect setting (optional)

  - `FREE`
    Free – Use an unconstrained aspect.
  - `FIXED`
    Fixed – Use a fixed 1:1 aspect.
- **plane_aspect_depth** (Literal['FREE', 'FIXED']) –

  Aspect, The initial aspect setting (optional)

  - `FREE`
    Free – Use an unconstrained aspect.
  - `FIXED`
    Fixed – Use a fixed 1:1 aspect.
- **wait_for_input** (bool) – Wait for Input, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.localview"></a>

### bpy.ops.view3d.localview(*, frame_selected=True)

Toggle display of selected object(s) separately and centered in view

**Parameters:**

**frame_selected** (bool) – Frame Selected, Move the view to frame the selected objects (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.localview_remove_from"></a>

### bpy.ops.view3d.localview_remove_from()

Move selected objects out of local view

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.move"></a>

### bpy.ops.view3d.move(*, use_cursor_init=True)

Move the view

**Parameters:**

**use_cursor_init** (bool) – Use Mouse Position, Allow the initial mouse position to be used (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.navigate"></a>

### bpy.ops.view3d.navigate()

Interactively navigate around the scene (uses the mode (walk/fly) preference)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.ndof_all"></a>

### bpy.ops.view3d.ndof_all()

Pan and rotate the view with the 3D mouse

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.ndof_orbit"></a>

### bpy.ops.view3d.ndof_orbit()

Orbit the view using the 3D mouse

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.ndof_orbit_zoom"></a>

### bpy.ops.view3d.ndof_orbit_zoom()

Orbit and zoom the view using the 3D mouse

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.ndof_pan"></a>

### bpy.ops.view3d.ndof_pan()

Pan the view with the 3D mouse

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.object_as_camera"></a>

### bpy.ops.view3d.object_as_camera()

Set the active object as the active camera for this view or scene

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.object_mode_pie_or_toggle"></a>

### bpy.ops.view3d.object_mode_pie_or_toggle()

Undocumented, consider [contributing](https://developer.blender.org/).

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.pastebuffer"></a>

### bpy.ops.view3d.pastebuffer(*, autoselect=True, active_collection=True)

Paste objects from the internal clipboard

**Parameters:**

- **autoselect** (bool) – Select, Select pasted objects (optional)
- **active_collection** (bool) – Active Collection, Put pasted objects in the active collection (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.render_border"></a>

### bpy.ops.view3d.render_border(*, xmin=0, xmax=0, ymin=0, ymax=0, wait_for_input=True)

Set the boundaries of the border render and enable border render

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

<a id="bpy.ops.view3d.rotate"></a>

### bpy.ops.view3d.rotate(*, use_cursor_init=True)

Rotate the view

**Parameters:**

**use_cursor_init** (bool) – Use Mouse Position, Allow the initial mouse position to be used (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.ruler_add"></a>

### bpy.ops.view3d.ruler_add()

Add ruler

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.ruler_remove"></a>

### bpy.ops.view3d.ruler_remove()

Undocumented, consider [contributing](https://developer.blender.org/).

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.select"></a>

### bpy.ops.view3d.select(*, extend=False, deselect=False, toggle=False, deselect_all=False, select_passthrough=False, center=False, enumerate=False, object=False, location=(0, 0))

Select and activate item(s)

**Parameters:**

- **extend** (bool) – Extend, Extend selection instead of deselecting everything first (optional)
- **deselect** (bool) – Deselect, Remove from selection (optional)
- **toggle** (bool) – Toggle Selection, Toggle the selection (optional)
- **deselect_all** (bool) – Deselect On Nothing, Deselect all when nothing under the cursor (optional)
- **select_passthrough** (bool) – Only Select Unselected, Ignore the select action when the element is already selected (optional)
- **center** (bool) – Center, Use the object center when selecting, in edit mode used to extend object selection (optional)
- **enumerate** (bool) – Enumerate, List objects under the mouse (object mode only) (optional)
- **object** (bool) – Object, Use object selection (edit mode only) (optional)
- **location** (Sequence[int]) – Location, Mouse location (array of 2 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.select_box"></a>

### bpy.ops.view3d.select_box(*, xmin=0, xmax=0, ymin=0, ymax=0, wait_for_input=True, mode='SET')

Select items using box selection

**Parameters:**

- **xmin** (int) – X Min, (in [-inf, inf], optional)
- **xmax** (int) – X Max, (in [-inf, inf], optional)
- **ymin** (int) – Y Min, (in [-inf, inf], optional)
- **ymax** (int) – Y Max, (in [-inf, inf], optional)
- **wait_for_input** (bool) – Wait for Input, (optional)
- **mode** (Literal['SET', 'ADD', 'SUB', 'XOR', 'AND']) –

  Mode, (optional)

  - `SET`
    Set – Set a new selection.
  - `ADD`
    Extend – Extend existing selection.
  - `SUB`
    Subtract – Subtract existing selection.
  - `XOR`
    Difference – Invert existing selection.
  - `AND`
    Intersect – Intersect existing selection.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.select_circle"></a>

### bpy.ops.view3d.select_circle(*, x=0, y=0, radius=25, wait_for_input=True, mode='SET')

Select items using circle selection

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

<a id="bpy.ops.view3d.select_lasso"></a>

### bpy.ops.view3d.select_lasso(*, path=None, use_smooth_stroke=False, smooth_stroke_factor=0.75, smooth_stroke_radius=35, mode='SET')

Select items using lasso selection

**Parameters:**

- **path** (`bpy_prop_collection`[`OperatorMousePath`] | None) – Path, (optional)
- **use_smooth_stroke** (bool) – Stabilize Stroke, Selection lags behind mouse and follows a smoother path (optional)
- **smooth_stroke_factor** (float) – Smooth Stroke Factor, Higher values give a smoother stroke (in [0.5, 0.99], optional)
- **smooth_stroke_radius** (int) – Smooth Stroke Radius, Minimum distance from last point before selection continues (in [10, 200], optional)
- **mode** (Literal['SET', 'ADD', 'SUB', 'XOR', 'AND']) –

  Mode, (optional)

  - `SET`
    Set – Set a new selection.
  - `ADD`
    Extend – Extend existing selection.
  - `SUB`
    Subtract – Subtract existing selection.
  - `XOR`
    Difference – Invert existing selection.
  - `AND`
    Intersect – Intersect existing selection.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.select_menu"></a>

### bpy.ops.view3d.select_menu(*, name='', extend=False, deselect=False, toggle=False)

Menu object selection

**Parameters:**

- **name** (str) – Object Name, (optional)
- **extend** (bool) – Extend, (optional)
- **deselect** (bool) – Deselect, (optional)
- **toggle** (bool) – Toggle, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.smoothview"></a>

### bpy.ops.view3d.smoothview()

Undocumented, consider [contributing](https://developer.blender.org/).

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.snap_cursor_to_active"></a>

### bpy.ops.view3d.snap_cursor_to_active()

Snap 3D cursor to the active item

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.snap_cursor_to_center"></a>

### bpy.ops.view3d.snap_cursor_to_center()

Snap 3D cursor to the world origin

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.snap_cursor_to_grid"></a>

### bpy.ops.view3d.snap_cursor_to_grid()

Snap 3D cursor to the nearest grid division

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.snap_cursor_to_selected"></a>

### bpy.ops.view3d.snap_cursor_to_selected()

Snap 3D cursor to the middle of the selected item(s)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.snap_selected_to_active"></a>

### bpy.ops.view3d.snap_selected_to_active()

Snap selected item(s) to the active item

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.snap_selected_to_cursor"></a>

### bpy.ops.view3d.snap_selected_to_cursor(*, use_offset=True, use_rotation=False)

Snap selected item(s) to the 3D cursor

**Parameters:**

- **use_offset** (bool) – Offset, If the selection should be snapped as a whole or by each object center (optional)
- **use_rotation** (bool) – Rotation, If the selection should be rotated to match the cursor (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.snap_selected_to_grid"></a>

### bpy.ops.view3d.snap_selected_to_grid()

Snap selected item(s) to their nearest grid division

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.toggle_matcap_flip"></a>

### bpy.ops.view3d.toggle_matcap_flip()

Flip MatCap

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.toggle_shading"></a>

### bpy.ops.view3d.toggle_shading(*, type='WIREFRAME')

Toggle shading type in 3D viewport

**Parameters:**

**type** (Literal['WIREFRAME', 'SOLID', 'MATERIAL', 'RENDERED']) –

Type, Shading type to toggle (optional)

- `WIREFRAME`
  Wireframe – Toggle wireframe shading.
- `SOLID`
  Solid – Toggle solid shading.
- `MATERIAL`
  Material Preview – Toggle material preview shading.
- `RENDERED`
  Rendered – Toggle rendered shading.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.toggle_xray"></a>

### bpy.ops.view3d.toggle_xray()

Transparent scene display. Allow selecting through items

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.transform_gizmo_set"></a>

### bpy.ops.view3d.transform_gizmo_set(*, extend=False, type=set())

Set the current transform gizmo

**Parameters:**

- **extend** (bool) – Extend, (optional)
- **type** (set[Literal['TRANSLATE', 'ROTATE', 'SCALE']]) – Type, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/view3d.py:245](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/view3d.py#L245)

<a id="bpy.ops.view3d.view_all"></a>

### bpy.ops.view3d.view_all(*, use_all_regions=False, center=False)

View all objects in scene

**Parameters:**

- **use_all_regions** (bool) – All Regions, View selected for all regions (optional)
- **center** (bool) – Center, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.view_axis"></a>

### bpy.ops.view3d.view_axis(*, type='LEFT', align_active=False, relative=False)

Use a preset viewpoint

**Parameters:**

- **type** (Literal['LEFT', 'RIGHT', 'BOTTOM', 'TOP', 'FRONT', 'BACK']) –

  View, Preset viewpoint to use (optional)

  - `LEFT`
    Left – View from the left.
  - `RIGHT`
    Right – View from the right.
  - `BOTTOM`
    Bottom – View from the bottom.
  - `TOP`
    Top – View from the top.
  - `FRONT`
    Front – View from the front.
  - `BACK`
    Back – View from the back.
- **align_active** (bool) – Align Active, Align to the active object’s axis (optional)
- **relative** (bool) – Relative, Rotate relative to the current orientation (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.view_camera"></a>

### bpy.ops.view3d.view_camera()

Toggle the camera view

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.view_center_camera"></a>

### bpy.ops.view3d.view_center_camera()

Center the camera view, resizing the view to fit its bounds

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.view_center_cursor"></a>

### bpy.ops.view3d.view_center_cursor()

Center the view so that the cursor is in the middle of the view

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.view_center_lock"></a>

### bpy.ops.view3d.view_center_lock()

Center the view lock offset

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.view_center_pick"></a>

### bpy.ops.view3d.view_center_pick()

Center the view to the Z-depth position under the mouse cursor

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.view_lock_clear"></a>

### bpy.ops.view3d.view_lock_clear()

Clear all view locking

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.view_lock_to_active"></a>

### bpy.ops.view3d.view_lock_to_active()

Lock the view to the active object/bone

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.view_orbit"></a>

### bpy.ops.view3d.view_orbit(*, angle=0.0, type='ORBITLEFT')

Orbit the view

**Parameters:**

- **angle** (float) – Roll, (in [-inf, inf], optional)
- **type** (Literal['ORBITLEFT', 'ORBITRIGHT', 'ORBITUP', 'ORBITDOWN']) –

  Orbit, Direction of View Orbit (optional)

  - `ORBITLEFT`
    Orbit Left – Orbit the view around to the left.
  - `ORBITRIGHT`
    Orbit Right – Orbit the view around to the right.
  - `ORBITUP`
    Orbit Up – Orbit the view up.
  - `ORBITDOWN`
    Orbit Down – Orbit the view down.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.view_pan"></a>

### bpy.ops.view3d.view_pan(*, type='PANLEFT')

Pan the view in a given direction

**Parameters:**

**type** (Literal['PANLEFT', 'PANRIGHT', 'PANUP', 'PANDOWN']) –

Pan, Direction of View Pan (optional)

- `PANLEFT`
  Pan Left – Pan the view to the left.
- `PANRIGHT`
  Pan Right – Pan the view to the right.
- `PANUP`
  Pan Up – Pan the view up.
- `PANDOWN`
  Pan Down – Pan the view down.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.view_persportho"></a>

### bpy.ops.view3d.view_persportho()

Switch the current view from perspective/orthographic projection

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.view_roll"></a>

### bpy.ops.view3d.view_roll(*, angle=0.0, type='ANGLE')

Roll the view

**Parameters:**

- **angle** (float) – Roll, (in [-inf, inf], optional)
- **type** (Literal['ANGLE', 'LEFT', 'RIGHT']) –

  Roll Angle Source, How roll angle is calculated (optional)

  - `ANGLE`
    Roll Angle – Roll the view using an angle value.
  - `LEFT`
    Roll Left – Roll the view around to the left.
  - `RIGHT`
    Roll Right – Roll the view around to the right.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.view_selected"></a>

### bpy.ops.view3d.view_selected(*, use_all_regions=False)

Move the view to the selection center

**Parameters:**

**use_all_regions** (bool) – All Regions, View selected for all regions (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.vr_location_scouting_capture_review"></a>

### bpy.ops.view3d.vr_location_scouting_capture_review()

Interactively review Location Scouting VR Captures

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.walk"></a>

### bpy.ops.view3d.walk()

Interactively walk around the scene

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.zoom"></a>

### bpy.ops.view3d.zoom(*, mx=0, my=0, delta=0, use_cursor_init=True)

Zoom in/out in the view

**Parameters:**

- **mx** (int) – Region Position X, (in [0, inf], optional)
- **my** (int) – Region Position Y, (in [0, inf], optional)
- **delta** (int) – Delta, (in [-inf, inf], optional)
- **use_cursor_init** (bool) – Use Mouse Position, Allow the initial mouse position to be used (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.view3d.zoom_border"></a>

### bpy.ops.view3d.zoom_border(*, xmin=0, xmax=0, ymin=0, ymax=0, wait_for_input=True, zoom_out=False)

Zoom in the view to the nearest object contained in the border

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

<a id="bpy.ops.view3d.zoom_camera_1_to_1"></a>

### bpy.ops.view3d.zoom_camera_1_to_1()

Match the camera to 1:1 to the render output

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]
