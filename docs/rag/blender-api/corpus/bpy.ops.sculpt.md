<!-- source: Blender Python API reference 5.2 / bpy.ops.sculpt.html -->

<a id="module-bpy.ops.sculpt"></a>

# Sculpt Operators

<a id="bpy.ops.sculpt.brush_stroke"></a>

### bpy.ops.sculpt.brush_stroke(*, stroke=None, mode='NORMAL', brush_toggle='None', pen_flip=False, override_location=False, ignore_background_click=False)

Sculpt a stroke into the geometry

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
- **override_location** (bool) – Override Location, Override the given “location” array by recalculating object space positions from the provided “mouse_event” positions (optional)
- **ignore_background_click** (bool) – Ignore Background Click, Clicks on the background do not start the stroke (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sculpt.cloth_filter"></a>

### bpy.ops.sculpt.cloth_filter(*, start_mouse=(0, 0), area_normal_radius=0.25, strength=1.0, iteration_count=1, event_history=None, type='GRAVITY', force_axis={'X', 'Y', 'Z'}, orientation='LOCAL', cloth_mass=1.0, cloth_damping=0.0, use_face_sets=False, use_collisions=False)

Applies a cloth simulation deformation to the entire mesh

**Parameters:**

- **start_mouse** (Sequence[int]) – Starting Mouse, (array of 2 items, in [0, 16384], optional)
- **area_normal_radius** (float) – Normal Radius, Radius used for calculating area normal on initial click,in percentage of brush radius(in [0.001, 5], optional)
- **strength** (float) – Strength, Filter strength (in [-10, 10], optional)
- **iteration_count** (int) – Repeat, How many times to repeat the filter (in [1, 10000], optional)
- **event_history** (`bpy_prop_collection`[`OperatorStrokeElement`] | None) – (optional)
- **type** (Literal['GRAVITY', 'INFLATE', 'EXPAND', 'PINCH', 'SCALE']) –

  Filter Type, Operation that is going to be applied to the mesh (optional)

  - `GRAVITY`
    Gravity – Applies gravity to the simulation.
  - `INFLATE`
    Inflate – Inflates the cloth.
  - `EXPAND`
    Expand – Expands the cloth’s dimensions.
  - `PINCH`
    Pinch – Pulls the cloth to the cursor’s start position.
  - `SCALE`
    Scale – Scales the mesh as a soft body using the origin of the object as scale.
- **force_axis** (set[Literal['X', 'Y', 'Z']]) –

  Force Axis, Apply the force in the selected axis (optional)

  - `X`
    X – Apply force in the X axis.
  - `Y`
    Y – Apply force in the Y axis.
  - `Z`
    Z – Apply force in the Z axis.
- **orientation** (Literal['LOCAL', 'WORLD', 'VIEW']) –

  Orientation, Orientation of the axis to limit the filter force (optional)

  - `LOCAL`
    Local – Use the local axis to limit the force and set the gravity direction.
  - `WORLD`
    World – Use the global axis to limit the force and set the gravity direction.
  - `VIEW`
    View – Use the view axis to limit the force and set the gravity direction.
- **cloth_mass** (float) – Cloth Mass, Mass of each simulation particle (in [0, 2], optional)
- **cloth_damping** (float) – Cloth Damping, How much the applied forces are propagated through the cloth (in [0, 1], optional)
- **use_face_sets** (bool) – Use Face Sets, Apply the filter only to the face set under the cursor (optional)
- **use_collisions** (bool) – Use Collisions, Collide with other collider objects in the scene (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sculpt.color_filter"></a>

### bpy.ops.sculpt.color_filter(*, start_mouse=(0, 0), area_normal_radius=0.25, strength=1.0, iteration_count=1, event_history=None, type='FILL', fill_color=(1.0, 1.0, 1.0), use_immediate=False, use_secondary_color=False)

Applies a filter to modify the active color attribute

**Parameters:**

- **start_mouse** (Sequence[int]) – Starting Mouse, (array of 2 items, in [0, 16384], optional)
- **area_normal_radius** (float) – Normal Radius, Radius used for calculating area normal on initial click,in percentage of brush radius(in [0.001, 5], optional)
- **strength** (float) – Strength, Filter strength (in [-10, 10], optional)
- **iteration_count** (int) – Repeat, How many times to repeat the filter (in [1, 10000], optional)
- **event_history** (`bpy_prop_collection`[`OperatorStrokeElement`] | None) – (optional)
- **type** (Literal['FILL', 'HUE', 'SATURATION', 'VALUE', 'BRIGHTNESS', 'CONTRAST', 'SMOOTH', 'RED', 'GREEN', 'BLUE']) –

  Filter Type, (optional)

  - `FILL`
    Fill – Fill with a specific color.
  - `HUE`
    Hue – Change hue.
  - `SATURATION`
    Saturation – Change saturation.
  - `VALUE`
    Value – Change value.
  - `BRIGHTNESS`
    Brightness – Change brightness.
  - `CONTRAST`
    Contrast – Change contrast.
  - `SMOOTH`
    Smooth – Smooth colors.
  - `RED`
    Red – Change red channel.
  - `GREEN`
    Green – Change green channel.
  - `BLUE`
    Blue – Change blue channel.
- **fill_color** ([`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color") | Sequence[float]) – Fill Color, (array of 3 items, in [0, inf], optional)
- **use_immediate** (bool) – Immediate Apply, Apply once without entering modal interaction (optional)
- **use_secondary_color** (bool) – Use Secondary Color, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sculpt.detail_flood_fill"></a>

### bpy.ops.sculpt.detail_flood_fill()

Flood fill the mesh with the selected detail setting

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sculpt.dynamic_topology_toggle"></a>

### bpy.ops.sculpt.dynamic_topology_toggle()

Dynamic topology alters the mesh topology while sculpting

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sculpt.dyntopo_detail_size_edit"></a>

### bpy.ops.sculpt.dyntopo_detail_size_edit()

Modify the detail size of dyntopo interactively

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sculpt.expand"></a>

### bpy.ops.sculpt.expand(*, target='MASK', falloff_type='GEODESIC', invert=False, use_mask_preserve=False, use_falloff_gradient=False, use_modify_active=False, use_reposition_pivot=True, max_geodesic_move_preview=10000, use_auto_mask=False, normal_falloff_smooth=2)

Generic sculpt expand operator

**Parameters:**

- **target** (Literal['MASK', 'FACE_SETS', 'COLOR']) – Data Target, Data that is going to be modified in the expand operation (optional)
- **falloff_type** (Literal['GEODESIC', 'TOPOLOGY', 'TOPOLOGY_DIAGONALS', 'NORMALS', 'SPHERICAL', 'BOUNDARY_TOPOLOGY', 'BOUNDARY_FACE_SET', 'ACTIVE_FACE_SET']) – Falloff Type, Initial falloff of the expand operation (optional)
- **invert** (bool) – Invert, Invert the expand active elements (optional)
- **use_mask_preserve** (bool) – Preserve Previous, Preserve the previous state of the target data (optional)
- **use_falloff_gradient** (bool) – Falloff Gradient, Expand Using a linear falloff (optional)
- **use_modify_active** (bool) – Modify Active, Modify the active face set instead of creating a new one (optional)
- **use_reposition_pivot** (bool) – Reposition Pivot, Reposition the sculpt transform pivot to the boundary of the expand active area (optional)
- **max_geodesic_move_preview** (int) – Max Vertex Count for Geodesic Move Preview, Maximum number of vertices in the mesh for using geodesic falloff when moving the origin of expand. If the total number of vertices is greater than this value, the falloff will be set to spherical when moving (in [0, inf], optional)
- **use_auto_mask** (bool) – Auto Create, Fill in mask if nothing is already masked (optional)
- **normal_falloff_smooth** (int) – Normal Smooth, Blurring steps for normal falloff (in [0, 10], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sculpt.face_set_box_gesture"></a>

### bpy.ops.sculpt.face_set_box_gesture(*, xmin=0, xmax=0, ymin=0, ymax=0, wait_for_input=True, use_front_faces_only=False)

Add a face set in a rectangle defined by the cursor

**Parameters:**

- **xmin** (int) – X Min, (in [-inf, inf], optional)
- **xmax** (int) – X Max, (in [-inf, inf], optional)
- **ymin** (int) – Y Min, (in [-inf, inf], optional)
- **ymax** (int) – Y Max, (in [-inf, inf], optional)
- **wait_for_input** (bool) – Wait for Input, (optional)
- **use_front_faces_only** (bool) – Front Faces Only, Affect only faces facing towards the view (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sculpt.face_set_change_visibility"></a>

### bpy.ops.sculpt.face_set_change_visibility(*, mode='TOGGLE', active_face_set=0)

Change the visibility of the face sets of the sculpt

**Parameters:**

- **mode** (Literal['TOGGLE', 'SHOW_ACTIVE', 'HIDE_ACTIVE']) –

  Mode, (optional)

  - `TOGGLE`
    Toggle Visibility – Hide all face sets except for the active one.
  - `SHOW_ACTIVE`
    Show Active Face Set – Show the active face set.
  - `HIDE_ACTIVE`
    Hide Active Face Set – Hide the active face set.
- **active_face_set** (int) – Active Face Set, (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sculpt.face_set_edit"></a>

### bpy.ops.sculpt.face_set_edit(*, active_face_set=1, mode='GROW', strength=1.0, modify_hidden=False)

Edits the current active face set

**Parameters:**

- **active_face_set** (int) – Active Face Set, (in [0, inf], optional)
- **mode** (Literal['GROW', 'SHRINK', 'DELETE_GEOMETRY', 'FAIR_POSITIONS', 'FAIR_TANGENCY']) –

  Mode, (optional)

  - `GROW`
    Grow Face Set – Grows the face set boundary by one face based on mesh topology.
  - `SHRINK`
    Shrink Face Set – Shrinks the face set boundary by one face based on mesh topology.
  - `DELETE_GEOMETRY`
    Delete Geometry – Deletes the faces that are assigned to the face set.
  - `FAIR_POSITIONS`
    Fair Positions – Creates the smoothest possible geometry patch from the face set minimizing changes in vertex positions.
  - `FAIR_TANGENCY`
    Fair Tangency – Creates the smoothest possible geometry patch from the face set minimizing changes in vertex tangents.
- **strength** (float) – Strength, (in [0, 1], optional)
- **modify_hidden** (bool) – Modify Hidden, Apply the edit operation to hidden geometry (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sculpt.face_set_extract"></a>

### bpy.ops.sculpt.face_set_extract(*, add_boundary_loop=True, smooth_iterations=4, apply_shrinkwrap=True, add_solidify=True)

Create a new mesh object from the selected face set

**Parameters:**

- **add_boundary_loop** (bool) – Add Boundary Loop, Add an extra edge loop to better preserve the shape when applying a subdivision surface modifier (optional)
- **smooth_iterations** (int) – Smooth Iterations, Smooth iterations applied to the extracted mesh (in [0, inf], optional)
- **apply_shrinkwrap** (bool) – Project to Sculpt, Project the extracted mesh into the original sculpt (optional)
- **add_solidify** (bool) – Extract as Solid, Extract the mask as a solid object with a solidify modifier (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sculpt.face_set_lasso_gesture"></a>

### bpy.ops.sculpt.face_set_lasso_gesture(*, path=None, use_smooth_stroke=False, smooth_stroke_factor=0.75, smooth_stroke_radius=35, use_front_faces_only=False)

Add a face set in a shape defined by the cursor

**Parameters:**

- **path** (`bpy_prop_collection`[`OperatorMousePath`] | None) – Path, (optional)
- **use_smooth_stroke** (bool) – Stabilize Stroke, Selection lags behind mouse and follows a smoother path (optional)
- **smooth_stroke_factor** (float) – Smooth Stroke Factor, Higher values give a smoother stroke (in [0.5, 0.99], optional)
- **smooth_stroke_radius** (int) – Smooth Stroke Radius, Minimum distance from last point before selection continues (in [10, 200], optional)
- **use_front_faces_only** (bool) – Front Faces Only, Affect only faces facing towards the view (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sculpt.face_set_line_gesture"></a>

### bpy.ops.sculpt.face_set_line_gesture(*, xstart=0, xend=0, ystart=0, yend=0, flip=False, cursor=5, use_front_faces_only=False, use_limit_to_segment=False)

Add a face set to one side of a line defined by the cursor

**Parameters:**

- **xstart** (int) – X Start, (in [-inf, inf], optional)
- **xend** (int) – X End, (in [-inf, inf], optional)
- **ystart** (int) – Y Start, (in [-inf, inf], optional)
- **yend** (int) – Y End, (in [-inf, inf], optional)
- **flip** (bool) – Flip, (optional)
- **cursor** (int) – Cursor, Mouse cursor style to use during the modal operator (in [0, inf], optional)
- **use_front_faces_only** (bool) – Front Faces Only, Affect only faces facing towards the view (optional)
- **use_limit_to_segment** (bool) – Limit to Segment, Apply the gesture action only to the area that is contained within the segment without extending its effect to the entire line (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sculpt.face_set_polyline_gesture"></a>

### bpy.ops.sculpt.face_set_polyline_gesture(*, path=None, use_front_faces_only=False)

Add a face set in a shape defined by the cursor

**Parameters:**

- **path** (`bpy_prop_collection`[`OperatorMousePath`] | None) – Path, (optional)
- **use_front_faces_only** (bool) – Front Faces Only, Affect only faces facing towards the view (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sculpt.face_sets_create"></a>

### bpy.ops.sculpt.face_sets_create(*, mode='MASKED')

Create a new face set

**Parameters:**

**mode** (Literal['MASKED', 'VISIBLE', 'ALL', 'SELECTION']) –

Mode, (optional)

- `MASKED`
  Face Set from Masked – Create a new face set from the masked faces.
- `VISIBLE`
  Face Set from Visible – Create a new face set from the visible vertices.
- `ALL`
  Face Set Full Mesh – Create a unique face set with all faces in the sculpt.
- `SELECTION`
  Face Set from Edit Mode Selection – Create a face set corresponding to the Edit Mode face selection.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sculpt.face_sets_init"></a>

### bpy.ops.sculpt.face_sets_init(*, mode='LOOSE_PARTS', threshold=0.5)

Initializes all face sets in the mesh

**Parameters:**

- **mode** (Literal['LOOSE_PARTS', 'MATERIALS', 'NORMALS', 'UV_SEAMS', 'CREASES', 'BEVEL_WEIGHT', 'SHARP_EDGES', 'FACE_SET_BOUNDARIES']) –

  Mode, (optional)

  - `LOOSE_PARTS`
    Face Sets from Loose Parts – Create a face set per loose part in the mesh.
  - `MATERIALS`
    Face Sets from Material Slots – Create a face set per material slot.
  - `NORMALS`
    Face Sets from Mesh Normals – Create face sets for faces that have similar normal.
  - `UV_SEAMS`
    Face Sets from UV Seams – Create face sets using UV seams as boundaries.
  - `CREASES`
    Face Sets from Edge Creases – Create face sets using edge creases as boundaries.
  - `BEVEL_WEIGHT`
    Face Sets from Bevel Weight – Create face sets using bevel weights as boundaries.
  - `SHARP_EDGES`
    Face Sets from Sharp Edges – Create face sets using sharp edges as boundaries.
  - `FACE_SET_BOUNDARIES`
    Face Sets from Face Set Boundaries – Create a face set per isolated face set.
- **threshold** (float) – Threshold, Minimum value to consider a certain attribute a boundary when creating the face sets (in [0, 1], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sculpt.face_sets_randomize_colors"></a>

### bpy.ops.sculpt.face_sets_randomize_colors()

Generates a new set of random colors to render the face sets in the viewport

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sculpt.mask_by_color"></a>

### bpy.ops.sculpt.mask_by_color(*, contiguous=False, invert=False, preserve_previous_mask=False, threshold=0.35, location=(0, 0))

Creates a mask based on the active color attribute

**Parameters:**

- **contiguous** (bool) – Contiguous, Mask only contiguous color areas (optional)
- **invert** (bool) – Invert, Invert the generated mask (optional)
- **preserve_previous_mask** (bool) – Preserve Previous Mask, Preserve the previous mask and add or subtract the new one generated by the colors (optional)
- **threshold** (float) – Threshold, How much changes in color affect the mask generation (in [0, 1], optional)
- **location** (Sequence[int]) – Location, Region coordinates of sampling (array of 2 items, in [0, 32767], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sculpt.mask_filter"></a>

### bpy.ops.sculpt.mask_filter(*, filter_type='SMOOTH', iterations=1, auto_iteration_count=True)

Applies a filter to modify the current mask

**Parameters:**

- **filter_type** (Literal['SMOOTH', 'SHARPEN', 'GROW', 'SHRINK', 'CONTRAST_INCREASE', 'CONTRAST_DECREASE']) – Type, Filter that is going to be applied to the mask (optional)
- **iterations** (int) – Iterations, Number of times that the filter is going to be applied (in [1, 100], optional)
- **auto_iteration_count** (bool) – Auto Iteration Count, Use an automatic number of iterations based on the number of vertices of the sculpt (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sculpt.mask_from_boundary"></a>

### bpy.ops.sculpt.mask_from_boundary(*, mix_mode='MIX', mix_factor=1.0, settings_source='OPERATOR', boundary_mode='MESH', propagation_steps=1)

Creates a mask based on the boundaries of the surface

**Parameters:**

- **mix_mode** (Literal['MIX', 'MULTIPLY', 'DIVIDE', 'ADD', 'SUBTRACT']) – Mode, Mix mode (optional)
- **mix_factor** (float) – Mix Factor, (in [0, 5], optional)
- **settings_source** (Literal['OPERATOR', 'BRUSH', 'SCENE']) –

  Settings, Use settings from here (optional)

  - `OPERATOR`
    Operator – Use settings from operator properties.
  - `BRUSH`
    Brush – Use settings from brush.
  - `SCENE`
    Scene – Use settings from scene.
- **boundary_mode** (Literal['MESH', 'FACE_SETS']) –

  Mode, Boundary type to mask (optional)

  - `MESH`
    Mesh – Calculate the boundary mask based on disconnected mesh topology islands.
  - `FACE_SETS`
    Face Sets – Calculate the boundary mask between face sets.
- **propagation_steps** (int) – Propagation Steps, (in [1, 20], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sculpt.mask_from_cavity"></a>

### bpy.ops.sculpt.mask_from_cavity(*, mix_mode='MIX', mix_factor=1.0, settings_source='OPERATOR', factor=0.5, blur_steps=2, use_curve=False, invert=False)

Creates a mask based on the curvature of the surface

**Parameters:**

- **mix_mode** (Literal['MIX', 'MULTIPLY', 'DIVIDE', 'ADD', 'SUBTRACT']) – Mode, Mix mode (optional)
- **mix_factor** (float) – Mix Factor, (in [0, 5], optional)
- **settings_source** (Literal['OPERATOR', 'BRUSH', 'SCENE']) –

  Settings, Use settings from here (optional)

  - `OPERATOR`
    Operator – Use settings from operator properties.
  - `BRUSH`
    Brush – Use settings from brush.
  - `SCENE`
    Scene – Use settings from scene.
- **factor** (float) – Factor, The contrast of the cavity mask (in [0, 5], optional)
- **blur_steps** (int) – Blur, The number of times the cavity mask is blurred (in [0, 25], optional)
- **use_curve** (bool) – Custom Curve, (optional)
- **invert** (bool) – Cavity (Inverted), (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sculpt.mask_init"></a>

### bpy.ops.sculpt.mask_init(*, mode='RANDOM_PER_VERTEX')

Creates a new mask for the entire mesh

**Parameters:**

**mode** (Literal['RANDOM_PER_VERTEX', 'RANDOM_PER_FACE_SET', 'RANDOM_PER_LOOSE_PART']) – Mode, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sculpt.mesh_filter"></a>

### bpy.ops.sculpt.mesh_filter(*, start_mouse=(0, 0), area_normal_radius=0.25, strength=1.0, iteration_count=1, event_history=None, type='INFLATE', deform_axis={'X', 'Y', 'Z'}, orientation='LOCAL', surface_smooth_shape_preservation=0.5, surface_smooth_current_vertex=0.5, sharpen_smooth_ratio=0.35, sharpen_intensify_detail_strength=0.0, sharpen_curvature_smooth_iterations=0)

Applies a filter to modify the current mesh

**Parameters:**

- **start_mouse** (Sequence[int]) – Starting Mouse, (array of 2 items, in [0, 16384], optional)
- **area_normal_radius** (float) – Normal Radius, Radius used for calculating area normal on initial click,in percentage of brush radius(in [0.001, 5], optional)
- **strength** (float) – Strength, Filter strength (in [-10, 10], optional)
- **iteration_count** (int) – Repeat, How many times to repeat the filter (in [1, 10000], optional)
- **event_history** (`bpy_prop_collection`[`OperatorStrokeElement`] | None) – (optional)
- **type** (Literal['SMOOTH', 'SCALE', 'INFLATE', 'SPHERE', 'RANDOM', 'RELAX', 'RELAX_FACE_SETS', 'SURFACE_SMOOTH', 'SHARPEN', 'ENHANCE_DETAILS', 'ERASE_DISPLACEMENT']) –

  Filter Type, Operation that is going to be applied to the mesh (optional)

  - `SMOOTH`
    Smooth – Smooth mesh.
  - `SCALE`
    Scale – Scale mesh.
  - `INFLATE`
    Inflate – Inflate mesh.
  - `SPHERE`
    Sphere – Morph into sphere.
  - `RANDOM`
    Random – Randomize vertex positions.
  - `RELAX`
    Relax – Relax mesh.
  - `RELAX_FACE_SETS`
    Relax Face Sets – Smooth the edges of all the face sets.
  - `SURFACE_SMOOTH`
    Surface Smooth – Smooth the surface of the mesh, preserving the volume.
  - `SHARPEN`
    Sharpen – Sharpen the cavities of the mesh.
  - `ENHANCE_DETAILS`
    Enhance Details – Enhance the high frequency surface detail.
  - `ERASE_DISPLACEMENT`
    Erase Displacement – Deletes the displacement of the Multires Modifier.
- **deform_axis** (set[Literal['X', 'Y', 'Z']]) –

  Deform Axis, Apply the deformation in the selected axis (optional)

  - `X`
    X – Deform in the X axis.
  - `Y`
    Y – Deform in the Y axis.
  - `Z`
    Z – Deform in the Z axis.
- **orientation** (Literal['LOCAL', 'WORLD', 'VIEW']) –

  Orientation, Orientation of the axis to limit the filter displacement (optional)

  - `LOCAL`
    Local – Use the local axis to limit the displacement.
  - `WORLD`
    World – Use the global axis to limit the displacement.
  - `VIEW`
    View – Use the view axis to limit the displacement.
- **surface_smooth_shape_preservation** (float) – Shape Preservation, How much of the original shape is preserved when smoothing (in [0, 1], optional)
- **surface_smooth_current_vertex** (float) – Per Vertex Displacement, How much the position of each individual vertex influences the final result (in [0, 1], optional)
- **sharpen_smooth_ratio** (float) – Smooth Ratio, How much smoothing is applied to polished surfaces (in [0, 1], optional)
- **sharpen_intensify_detail_strength** (float) – Intensify Details, How much creases and valleys are intensified (in [0, 10], optional)
- **sharpen_curvature_smooth_iterations** (int) – Curvature Smooth Iterations, How much smooth the resulting shape is, ignoring high frequency details (in [0, 10], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sculpt.optimize"></a>

### bpy.ops.sculpt.optimize()

Recalculate the sculpt BVH to improve performance

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sculpt.paint_mask_extract"></a>

### bpy.ops.sculpt.paint_mask_extract(*, mask_threshold=0.5, add_boundary_loop=True, smooth_iterations=4, apply_shrinkwrap=True, add_solidify=True)

Create a new mesh object from the current paint mask

**Parameters:**

- **mask_threshold** (float) – Threshold, Minimum mask value to consider the vertex valid to extract a face from the original mesh (in [0, 1], optional)
- **add_boundary_loop** (bool) – Add Boundary Loop, Add an extra edge loop to better preserve the shape when applying a subdivision surface modifier (optional)
- **smooth_iterations** (int) – Smooth Iterations, Smooth iterations applied to the extracted mesh (in [0, inf], optional)
- **apply_shrinkwrap** (bool) – Project to Sculpt, Project the extracted mesh into the original sculpt (optional)
- **add_solidify** (bool) – Extract as Solid, Extract the mask as a solid object with a solidify modifier (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sculpt.paint_mask_slice"></a>

### bpy.ops.sculpt.paint_mask_slice(*, mask_threshold=0.5, fill_holes=True, new_object=True)

Slices the paint mask from the mesh

**Parameters:**

- **mask_threshold** (float) – Threshold, Minimum mask value to consider the vertex valid to extract a face from the original mesh (in [0, 1], optional)
- **fill_holes** (bool) – Fill Holes, Fill holes after slicing the mask (optional)
- **new_object** (bool) – Slice to New Object, Create a new object from the sliced mask (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sculpt.project_line_gesture"></a>

### bpy.ops.sculpt.project_line_gesture(*, xstart=0, xend=0, ystart=0, yend=0, flip=False, cursor=5, use_front_faces_only=False, use_limit_to_segment=False)

Project the geometry onto a plane defined by a line

**Parameters:**

- **xstart** (int) – X Start, (in [-inf, inf], optional)
- **xend** (int) – X End, (in [-inf, inf], optional)
- **ystart** (int) – Y Start, (in [-inf, inf], optional)
- **yend** (int) – Y End, (in [-inf, inf], optional)
- **flip** (bool) – Flip, (optional)
- **cursor** (int) – Cursor, Mouse cursor style to use during the modal operator (in [0, inf], optional)
- **use_front_faces_only** (bool) – Front Faces Only, Affect only faces facing towards the view (optional)
- **use_limit_to_segment** (bool) – Limit to Segment, Apply the gesture action only to the area that is contained within the segment without extending its effect to the entire line (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sculpt.sample_detail_size"></a>

### bpy.ops.sculpt.sample_detail_size(*, location=(0, 0), mode='DYNTOPO')

Sample the mesh detail on clicked point

**Parameters:**

- **location** (Sequence[int]) – Location, Screen coordinates of sampling (array of 2 items, in [0, 32767], optional)
- **mode** (Literal['DYNTOPO', 'VOXEL']) –

  Detail Mode, Target sculpting workflow that is going to use the sampled size (optional)

  - `DYNTOPO`
    Dyntopo – Sample dyntopo detail.
  - `VOXEL`
    Voxel – Sample mesh voxel size.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sculpt.sculptmode_toggle"></a>

### bpy.ops.sculpt.sculptmode_toggle()

Toggle sculpt mode in 3D view

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sculpt.set_persistent_base"></a>

### bpy.ops.sculpt.set_persistent_base()

Reset the copy of the mesh that is being sculpted on

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sculpt.set_pivot_position"></a>

### bpy.ops.sculpt.set_pivot_position(*, mode='UNMASKED', mouse_x=0.0, mouse_y=0.0)

Sets the sculpt transform pivot position

**Parameters:**

- **mode** (Literal['ORIGIN', 'UNMASKED', 'BORDER', 'ACTIVE', 'SURFACE']) –

  Mode, (optional)

  - `ORIGIN`
    Origin – Sets the pivot to the origin of the sculpt.
  - `UNMASKED`
    Unmasked – Sets the pivot position to the average position of the unmasked vertices.
  - `BORDER`
    Mask Border – Sets the pivot position to the center of the border of the mask.
  - `ACTIVE`
    Active Vertex – Sets the pivot position to the active vertex position.
  - `SURFACE`
    Surface – Sets the pivot position to the surface under the cursor.
- **mouse_x** (float) – Mouse Position X, Position of the mouse used for “Surface” and “Active Vertex” mode (in [0, inf], optional)
- **mouse_y** (float) – Mouse Position Y, Position of the mouse used for “Surface” and “Active Vertex” mode (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sculpt.symmetrize"></a>

### bpy.ops.sculpt.symmetrize(*, merge_tolerance=0.0005)

Symmetrize the topology modifications

**Parameters:**

**merge_tolerance** (float) – Merge Distance, Distance within which symmetrical vertices are merged (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sculpt.trim_box_gesture"></a>

### bpy.ops.sculpt.trim_box_gesture(*, xmin=0, xmax=0, ymin=0, ymax=0, wait_for_input=True, use_front_faces_only=False, location=(0, 0), trim_mode='DIFFERENCE', use_cursor_depth=False, trim_orientation='VIEW', trim_extrude_mode='FIXED', trim_solver='MANIFOLD')

Execute a boolean operation on the mesh and a rectangle defined by the cursor

**Parameters:**

- **xmin** (int) – X Min, (in [-inf, inf], optional)
- **xmax** (int) – X Max, (in [-inf, inf], optional)
- **ymin** (int) – Y Min, (in [-inf, inf], optional)
- **ymax** (int) – Y Max, (in [-inf, inf], optional)
- **wait_for_input** (bool) – Wait for Input, (optional)
- **use_front_faces_only** (bool) – Front Faces Only, Affect only faces facing towards the view (optional)
- **location** (Sequence[int]) – Location, Mouse location (array of 2 items, in [-inf, inf], optional)
- **trim_mode** (Literal['DIFFERENCE', 'UNION', 'JOIN']) –

  Trim Mode, (optional)

  - `DIFFERENCE`
    Difference – Use a difference boolean operation.
  - `UNION`
    Union – Use a union boolean operation.
  - `JOIN`
    Join – Join the new mesh as separate geometry, without performing any boolean operation.
- **use_cursor_depth** (bool) – Use Cursor for Depth, Use cursor location and radius for the dimensions and position of the trimming shape (optional)
- **trim_orientation** (Literal['VIEW', 'SURFACE']) –

  Shape Orientation, (optional)

  - `VIEW`
    View – Use the view to orientate the trimming shape.
  - `SURFACE`
    Surface – Use the surface normal to orientate the trimming shape.
- **trim_extrude_mode** (Literal['PROJECT', 'FIXED']) –

  Extrude Mode, (optional)

  - `PROJECT`
    Project – Align trim geometry with the perspective of the current view for a tapered shape.
  - `FIXED`
    Fixed – Align trim geometry orthogonally for a shape with 90 degree angles.
- **trim_solver** (Literal['EXACT', 'FLOAT', 'MANIFOLD']) –

  Solver, (optional)

  - `EXACT`
    Exact – Slower solver with the best results for coplanar faces.
  - `FLOAT`
    Float – Simple solver with good performance, without support for overlapping geometry.
  - `MANIFOLD`
    Manifold – Fastest solver that works only on manifold meshes but gives better results.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sculpt.trim_lasso_gesture"></a>

### bpy.ops.sculpt.trim_lasso_gesture(*, path=None, use_smooth_stroke=False, smooth_stroke_factor=0.75, smooth_stroke_radius=35, use_front_faces_only=False, location=(0, 0), trim_mode='DIFFERENCE', use_cursor_depth=False, trim_orientation='VIEW', trim_extrude_mode='FIXED', trim_solver='MANIFOLD')

Execute a boolean operation on the mesh and a shape defined by the cursor

**Parameters:**

- **path** (`bpy_prop_collection`[`OperatorMousePath`] | None) – Path, (optional)
- **use_smooth_stroke** (bool) – Stabilize Stroke, Selection lags behind mouse and follows a smoother path (optional)
- **smooth_stroke_factor** (float) – Smooth Stroke Factor, Higher values give a smoother stroke (in [0.5, 0.99], optional)
- **smooth_stroke_radius** (int) – Smooth Stroke Radius, Minimum distance from last point before selection continues (in [10, 200], optional)
- **use_front_faces_only** (bool) – Front Faces Only, Affect only faces facing towards the view (optional)
- **location** (Sequence[int]) – Location, Mouse location (array of 2 items, in [-inf, inf], optional)
- **trim_mode** (Literal['DIFFERENCE', 'UNION', 'JOIN']) –

  Trim Mode, (optional)

  - `DIFFERENCE`
    Difference – Use a difference boolean operation.
  - `UNION`
    Union – Use a union boolean operation.
  - `JOIN`
    Join – Join the new mesh as separate geometry, without performing any boolean operation.
- **use_cursor_depth** (bool) – Use Cursor for Depth, Use cursor location and radius for the dimensions and position of the trimming shape (optional)
- **trim_orientation** (Literal['VIEW', 'SURFACE']) –

  Shape Orientation, (optional)

  - `VIEW`
    View – Use the view to orientate the trimming shape.
  - `SURFACE`
    Surface – Use the surface normal to orientate the trimming shape.
- **trim_extrude_mode** (Literal['PROJECT', 'FIXED']) –

  Extrude Mode, (optional)

  - `PROJECT`
    Project – Align trim geometry with the perspective of the current view for a tapered shape.
  - `FIXED`
    Fixed – Align trim geometry orthogonally for a shape with 90 degree angles.
- **trim_solver** (Literal['EXACT', 'FLOAT', 'MANIFOLD']) –

  Solver, (optional)

  - `EXACT`
    Exact – Slower solver with the best results for coplanar faces.
  - `FLOAT`
    Float – Simple solver with good performance, without support for overlapping geometry.
  - `MANIFOLD`
    Manifold – Fastest solver that works only on manifold meshes but gives better results.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sculpt.trim_line_gesture"></a>

### bpy.ops.sculpt.trim_line_gesture(*, xstart=0, xend=0, ystart=0, yend=0, flip=False, cursor=5, use_front_faces_only=False, use_limit_to_segment=False, location=(0, 0), trim_mode='DIFFERENCE', use_cursor_depth=False, trim_orientation='VIEW', trim_extrude_mode='FIXED', trim_solver='MANIFOLD')

Remove a portion of the mesh on one side of a line

**Parameters:**

- **xstart** (int) – X Start, (in [-inf, inf], optional)
- **xend** (int) – X End, (in [-inf, inf], optional)
- **ystart** (int) – Y Start, (in [-inf, inf], optional)
- **yend** (int) – Y End, (in [-inf, inf], optional)
- **flip** (bool) – Flip, (optional)
- **cursor** (int) – Cursor, Mouse cursor style to use during the modal operator (in [0, inf], optional)
- **use_front_faces_only** (bool) – Front Faces Only, Affect only faces facing towards the view (optional)
- **use_limit_to_segment** (bool) – Limit to Segment, Apply the gesture action only to the area that is contained within the segment without extending its effect to the entire line (optional)
- **location** (Sequence[int]) – Location, Mouse location (array of 2 items, in [-inf, inf], optional)
- **trim_mode** (Literal['DIFFERENCE', 'UNION', 'JOIN']) –

  Trim Mode, (optional)

  - `DIFFERENCE`
    Difference – Use a difference boolean operation.
  - `UNION`
    Union – Use a union boolean operation.
  - `JOIN`
    Join – Join the new mesh as separate geometry, without performing any boolean operation.
- **use_cursor_depth** (bool) – Use Cursor for Depth, Use cursor location and radius for the dimensions and position of the trimming shape (optional)
- **trim_orientation** (Literal['VIEW', 'SURFACE']) –

  Shape Orientation, (optional)

  - `VIEW`
    View – Use the view to orientate the trimming shape.
  - `SURFACE`
    Surface – Use the surface normal to orientate the trimming shape.
- **trim_extrude_mode** (Literal['PROJECT', 'FIXED']) –

  Extrude Mode, (optional)

  - `PROJECT`
    Project – Align trim geometry with the perspective of the current view for a tapered shape.
  - `FIXED`
    Fixed – Align trim geometry orthogonally for a shape with 90 degree angles.
- **trim_solver** (Literal['EXACT', 'FLOAT', 'MANIFOLD']) –

  Solver, (optional)

  - `EXACT`
    Exact – Slower solver with the best results for coplanar faces.
  - `FLOAT`
    Float – Simple solver with good performance, without support for overlapping geometry.
  - `MANIFOLD`
    Manifold – Fastest solver that works only on manifold meshes but gives better results.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sculpt.trim_polyline_gesture"></a>

### bpy.ops.sculpt.trim_polyline_gesture(*, path=None, use_front_faces_only=False, location=(0, 0), trim_mode='DIFFERENCE', use_cursor_depth=False, trim_orientation='VIEW', trim_extrude_mode='FIXED', trim_solver='MANIFOLD')

Execute a boolean operation on the mesh and a polygonal shape defined by the cursor

**Parameters:**

- **path** (`bpy_prop_collection`[`OperatorMousePath`] | None) – Path, (optional)
- **use_front_faces_only** (bool) – Front Faces Only, Affect only faces facing towards the view (optional)
- **location** (Sequence[int]) – Location, Mouse location (array of 2 items, in [-inf, inf], optional)
- **trim_mode** (Literal['DIFFERENCE', 'UNION', 'JOIN']) –

  Trim Mode, (optional)

  - `DIFFERENCE`
    Difference – Use a difference boolean operation.
  - `UNION`
    Union – Use a union boolean operation.
  - `JOIN`
    Join – Join the new mesh as separate geometry, without performing any boolean operation.
- **use_cursor_depth** (bool) – Use Cursor for Depth, Use cursor location and radius for the dimensions and position of the trimming shape (optional)
- **trim_orientation** (Literal['VIEW', 'SURFACE']) –

  Shape Orientation, (optional)

  - `VIEW`
    View – Use the view to orientate the trimming shape.
  - `SURFACE`
    Surface – Use the surface normal to orientate the trimming shape.
- **trim_extrude_mode** (Literal['PROJECT', 'FIXED']) –

  Extrude Mode, (optional)

  - `PROJECT`
    Project – Align trim geometry with the perspective of the current view for a tapered shape.
  - `FIXED`
    Fixed – Align trim geometry orthogonally for a shape with 90 degree angles.
- **trim_solver** (Literal['EXACT', 'FLOAT', 'MANIFOLD']) –

  Solver, (optional)

  - `EXACT`
    Exact – Slower solver with the best results for coplanar faces.
  - `FLOAT`
    Float – Simple solver with good performance, without support for overlapping geometry.
  - `MANIFOLD`
    Manifold – Fastest solver that works only on manifold meshes but gives better results.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sculpt.uv_sculpt_grab"></a>

### bpy.ops.sculpt.uv_sculpt_grab(*, use_invert=False)

Grab UVs

**Parameters:**

**use_invert** (bool) – Invert, Invert action for the duration of the stroke (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sculpt.uv_sculpt_pinch"></a>

### bpy.ops.sculpt.uv_sculpt_pinch(*, use_invert=False)

Pinch UVs

**Parameters:**

**use_invert** (bool) – Invert, Invert action for the duration of the stroke (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sculpt.uv_sculpt_relax"></a>

### bpy.ops.sculpt.uv_sculpt_relax(*, use_invert=False, relax_method='LAPLACIAN')

Relax UVs

**Parameters:**

- **use_invert** (bool) – Invert, Invert action for the duration of the stroke (optional)
- **relax_method** (Literal['LAPLACIAN', 'HC', 'COTAN']) –

  Relax Method, Algorithm used for UV relaxation (optional)

  - `LAPLACIAN`
    Laplacian – Use Laplacian method for relaxation.
  - `HC`
    HC – Use HC method for relaxation.
  - `COTAN`
    Geometry – Use Geometry (cotangent) relaxation, making UVs follow the underlying 3D geometry.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]
