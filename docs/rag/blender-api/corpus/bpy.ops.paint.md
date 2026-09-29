<!-- source: Blender Python API reference 5.2 / bpy.ops.paint.html -->

<a id="module-bpy.ops.paint"></a>

# Paint Operators

<a id="bpy.ops.paint.add_simple_uvs"></a>

### bpy.ops.paint.add_simple_uvs()

Add cube map UVs on mesh

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paint.add_texture_paint_slot"></a>

### bpy.ops.paint.add_texture_paint_slot(*, type='BASE_COLOR', slot_type='IMAGE', name='Untitled', color=(0.0, 0.0, 0.0, 1.0), width=1024, height=1024, alpha=True, generated_type='BLANK', float=False, tiled=False, domain='POINT', data_type='FLOAT_COLOR')

Add a paint slot

**Parameters:**

- **type** (Literal['BASE_COLOR', 'SPECULAR', 'ROUGHNESS', 'METALLIC', 'NORMAL', 'BUMP', 'DISPLACEMENT']) – Material Layer Type, Material layer type of new paint slot (optional)
- **slot_type** (Literal['IMAGE', 'COLOR_ATTRIBUTE']) – Slot Type, Type of new paint slot (optional)
- **name** (str) – Name, Name for new paint slot source (optional, never None)
- **color** (Sequence[float]) – Color, Default fill color (array of 4 items, in [0, inf], optional)
- **width** (int) – Width, Image width (in [1, inf], optional)
- **height** (int) – Height, Image height (in [1, inf], optional)
- **alpha** (bool) – Alpha, Create an image with an alpha channel (optional)
- **generated_type** (Literal[[Image Generated Type Items](bpy_types_enum_items/image_generated_type_items.md#rna-enum-image-generated-type-items)]) – Generated Type, Fill the image with a grid for UV map testing (optional)
- **float** (bool) – 32-bit Float, Create image with 32-bit floating-point bit depth (optional)
- **tiled** (bool) – Tiled, Create a tiled image (optional)
- **domain** (Literal[[Color Attribute Domain Items](bpy_types_enum_items/color_attribute_domain_items.md#rna-enum-color-attribute-domain-items)]) – Domain, Type of element that attribute is stored on (optional)
- **data_type** (Literal[[Color Attribute Type Items](bpy_types_enum_items/color_attribute_type_items.md#rna-enum-color-attribute-type-items)]) – Data Type, Type of data stored in attribute (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paint.brush_colors_flip"></a>

### bpy.ops.paint.brush_colors_flip()

Swap primary and secondary brush colors

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paint.face_select_all"></a>

### bpy.ops.paint.face_select_all(*, action='TOGGLE')

Change selection for all faces

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

<a id="bpy.ops.paint.face_select_hide"></a>

### bpy.ops.paint.face_select_hide(*, unselected=False)

Hide selected faces

**Parameters:**

**unselected** (bool) – Unselected, Hide unselected rather than selected objects (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paint.face_select_less"></a>

### bpy.ops.paint.face_select_less(*, face_step=True)

Deselect Faces connected to existing selection

**Parameters:**

**face_step** (bool) – Face Step, Also deselect faces that only touch on a corner (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paint.face_select_linked"></a>

### bpy.ops.paint.face_select_linked()

Select linked faces

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paint.face_select_linked_pick"></a>

### bpy.ops.paint.face_select_linked_pick(*, deselect=False)

Select linked faces under the cursor

**Parameters:**

**deselect** (bool) – Deselect, Deselect rather than select items (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paint.face_select_loop"></a>

### bpy.ops.paint.face_select_loop(*, select=True, extend=False)

Select face loop under the cursor

**Parameters:**

- **select** (bool) – Select, If false, faces will be deselected (optional)
- **extend** (bool) – Extend, Extend the selection (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paint.face_select_more"></a>

### bpy.ops.paint.face_select_more(*, face_step=True)

Select Faces connected to existing selection

**Parameters:**

**face_step** (bool) – Face Step, Also select faces that only touch on a corner (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paint.face_vert_reveal"></a>

### bpy.ops.paint.face_vert_reveal(*, select=True)

Reveal hidden faces and vertices

**Parameters:**

**select** (bool) – Select, Specifies whether the newly revealed geometry should be selected (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paint.grab_clone"></a>

### bpy.ops.paint.grab_clone(*, delta=(0.0, 0.0))

Move the clone source image

**Parameters:**

**delta** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Delta, Delta offset of clone image in 0.0 to 1.0 coordinates (array of 2 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paint.hide_show"></a>

### bpy.ops.paint.hide_show(*, xmin=0, xmax=0, ymin=0, ymax=0, wait_for_input=True, action='HIDE', area='Inside', use_front_faces_only=False)

Hide/show some vertices

**Parameters:**

- **xmin** (int) – X Min, (in [-inf, inf], optional)
- **xmax** (int) – X Max, (in [-inf, inf], optional)
- **ymin** (int) – Y Min, (in [-inf, inf], optional)
- **ymax** (int) – Y Max, (in [-inf, inf], optional)
- **wait_for_input** (bool) – Wait for Input, (optional)
- **action** (Literal['HIDE', 'SHOW']) –

  Visibility Action, Whether to hide or show vertices (optional)

  - `HIDE`
    Hide – Hide vertices.
  - `SHOW`
    Show – Show vertices.
- **area** (Literal['OUTSIDE', 'Inside']) –

  Visibility Area, Which vertices to hide or show (optional)

  - `OUTSIDE`
    Outside – Hide or show vertices outside the selection.
  - `Inside`
    Inside – Hide or show vertices inside the selection.
- **use_front_faces_only** (bool) – Front Faces Only, Affect only faces facing towards the view (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paint.hide_show_all"></a>

### bpy.ops.paint.hide_show_all(*, action='HIDE')

Hide/show all vertices

**Parameters:**

**action** (Literal['HIDE', 'SHOW']) –

Visibility Action, Whether to hide or show vertices (optional)

- `HIDE`
  Hide – Hide vertices.
- `SHOW`
  Show – Show vertices.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paint.hide_show_lasso_gesture"></a>

### bpy.ops.paint.hide_show_lasso_gesture(*, path=None, use_smooth_stroke=False, smooth_stroke_factor=0.75, smooth_stroke_radius=35, action='HIDE', area='Inside', use_front_faces_only=False)

Hide/show some vertices

**Parameters:**

- **path** (`bpy_prop_collection`[`OperatorMousePath`] | None) – Path, (optional)
- **use_smooth_stroke** (bool) – Stabilize Stroke, Selection lags behind mouse and follows a smoother path (optional)
- **smooth_stroke_factor** (float) – Smooth Stroke Factor, Higher values give a smoother stroke (in [0.5, 0.99], optional)
- **smooth_stroke_radius** (int) – Smooth Stroke Radius, Minimum distance from last point before selection continues (in [10, 200], optional)
- **action** (Literal['HIDE', 'SHOW']) –

  Visibility Action, Whether to hide or show vertices (optional)

  - `HIDE`
    Hide – Hide vertices.
  - `SHOW`
    Show – Show vertices.
- **area** (Literal['OUTSIDE', 'Inside']) –

  Visibility Area, Which vertices to hide or show (optional)

  - `OUTSIDE`
    Outside – Hide or show vertices outside the selection.
  - `Inside`
    Inside – Hide or show vertices inside the selection.
- **use_front_faces_only** (bool) – Front Faces Only, Affect only faces facing towards the view (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paint.hide_show_line_gesture"></a>

### bpy.ops.paint.hide_show_line_gesture(*, xstart=0, xend=0, ystart=0, yend=0, flip=False, cursor=5, action='HIDE', area='Inside', use_front_faces_only=False, use_limit_to_segment=False)

Hide/show some vertices

**Parameters:**

- **xstart** (int) – X Start, (in [-inf, inf], optional)
- **xend** (int) – X End, (in [-inf, inf], optional)
- **ystart** (int) – Y Start, (in [-inf, inf], optional)
- **yend** (int) – Y End, (in [-inf, inf], optional)
- **flip** (bool) – Flip, (optional)
- **cursor** (int) – Cursor, Mouse cursor style to use during the modal operator (in [0, inf], optional)
- **action** (Literal['HIDE', 'SHOW']) –

  Visibility Action, Whether to hide or show vertices (optional)

  - `HIDE`
    Hide – Hide vertices.
  - `SHOW`
    Show – Show vertices.
- **area** (Literal['OUTSIDE', 'Inside']) –

  Visibility Area, Which vertices to hide or show (optional)

  - `OUTSIDE`
    Outside – Hide or show vertices outside the selection.
  - `Inside`
    Inside – Hide or show vertices inside the selection.
- **use_front_faces_only** (bool) – Front Faces Only, Affect only faces facing towards the view (optional)
- **use_limit_to_segment** (bool) – Limit to Segment, Apply the gesture action only to the area that is contained within the segment without extending its effect to the entire line (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paint.hide_show_masked"></a>

### bpy.ops.paint.hide_show_masked(*, action='HIDE')

Hide/show all masked vertices above a threshold

**Parameters:**

**action** (Literal['HIDE', 'SHOW']) –

Visibility Action, Whether to hide or show vertices (optional)

- `HIDE`
  Hide – Hide vertices.
- `SHOW`
  Show – Show vertices.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paint.hide_show_polyline_gesture"></a>

### bpy.ops.paint.hide_show_polyline_gesture(*, path=None, action='HIDE', area='Inside', use_front_faces_only=False)

Hide/show some vertices

**Parameters:**

- **path** (`bpy_prop_collection`[`OperatorMousePath`] | None) – Path, (optional)
- **action** (Literal['HIDE', 'SHOW']) –

  Visibility Action, Whether to hide or show vertices (optional)

  - `HIDE`
    Hide – Hide vertices.
  - `SHOW`
    Show – Show vertices.
- **area** (Literal['OUTSIDE', 'Inside']) –

  Visibility Area, Which vertices to hide or show (optional)

  - `OUTSIDE`
    Outside – Hide or show vertices outside the selection.
  - `Inside`
    Inside – Hide or show vertices inside the selection.
- **use_front_faces_only** (bool) – Front Faces Only, Affect only faces facing towards the view (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paint.image_from_view"></a>

### bpy.ops.paint.image_from_view(*, filepath='')

Make an image from biggest 3D view for reprojection

**Parameters:**

**filepath** (str) – File Path, Name of the file (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paint.image_paint"></a>

### bpy.ops.paint.image_paint(*, stroke=None, mode='NORMAL', brush_toggle='None', pen_flip=False)

Paint a stroke into the image

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

<a id="bpy.ops.paint.mask_box_gesture"></a>

### bpy.ops.paint.mask_box_gesture(*, xmin=0, xmax=0, ymin=0, ymax=0, wait_for_input=True, use_front_faces_only=False, mode='VALUE', value=1.0)

Mask within a rectangle defined by the cursor

**Parameters:**

- **xmin** (int) – X Min, (in [-inf, inf], optional)
- **xmax** (int) – X Max, (in [-inf, inf], optional)
- **ymin** (int) – Y Min, (in [-inf, inf], optional)
- **ymax** (int) – Y Max, (in [-inf, inf], optional)
- **wait_for_input** (bool) – Wait for Input, (optional)
- **use_front_faces_only** (bool) – Front Faces Only, Affect only faces facing towards the view (optional)
- **mode** (Literal['VALUE', 'VALUE_INVERSE', 'INVERT']) –

  Mode, (optional)

  - `VALUE`
    Value – Set mask to the level specified by the ‘value’ property.
  - `VALUE_INVERSE`
    Value Inverted – Set mask to the level specified by the inverted ‘value’ property.
  - `INVERT`
    Invert – Invert the mask.
- **value** (float) – Value, Mask level to use when mode is ‘Value’; zero means no masking and one is fully masked (in [0, 1], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paint.mask_flood_fill"></a>

### bpy.ops.paint.mask_flood_fill(*, mode='VALUE', value=0.0)

Fill the whole mask with a given value, or invert its values

**Parameters:**

- **mode** (Literal['VALUE', 'VALUE_INVERSE', 'INVERT']) –

  Mode, (optional)

  - `VALUE`
    Value – Set mask to the level specified by the ‘value’ property.
  - `VALUE_INVERSE`
    Value Inverted – Set mask to the level specified by the inverted ‘value’ property.
  - `INVERT`
    Invert – Invert the mask.
- **value** (float) – Value, Mask level to use when mode is ‘Value’; zero means no masking and one is fully masked (in [0, 1], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paint.mask_lasso_gesture"></a>

### bpy.ops.paint.mask_lasso_gesture(*, path=None, use_smooth_stroke=False, smooth_stroke_factor=0.75, smooth_stroke_radius=35, use_front_faces_only=False, mode='VALUE', value=1.0)

Mask within a shape defined by the cursor

**Parameters:**

- **path** (`bpy_prop_collection`[`OperatorMousePath`] | None) – Path, (optional)
- **use_smooth_stroke** (bool) – Stabilize Stroke, Selection lags behind mouse and follows a smoother path (optional)
- **smooth_stroke_factor** (float) – Smooth Stroke Factor, Higher values give a smoother stroke (in [0.5, 0.99], optional)
- **smooth_stroke_radius** (int) – Smooth Stroke Radius, Minimum distance from last point before selection continues (in [10, 200], optional)
- **use_front_faces_only** (bool) – Front Faces Only, Affect only faces facing towards the view (optional)
- **mode** (Literal['VALUE', 'VALUE_INVERSE', 'INVERT']) –

  Mode, (optional)

  - `VALUE`
    Value – Set mask to the level specified by the ‘value’ property.
  - `VALUE_INVERSE`
    Value Inverted – Set mask to the level specified by the inverted ‘value’ property.
  - `INVERT`
    Invert – Invert the mask.
- **value** (float) – Value, Mask level to use when mode is ‘Value’; zero means no masking and one is fully masked (in [0, 1], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paint.mask_line_gesture"></a>

### bpy.ops.paint.mask_line_gesture(*, xstart=0, xend=0, ystart=0, yend=0, flip=False, cursor=5, use_front_faces_only=False, use_limit_to_segment=False, mode='VALUE', value=1.0)

Mask to one side of a line defined by the cursor

**Parameters:**

- **xstart** (int) – X Start, (in [-inf, inf], optional)
- **xend** (int) – X End, (in [-inf, inf], optional)
- **ystart** (int) – Y Start, (in [-inf, inf], optional)
- **yend** (int) – Y End, (in [-inf, inf], optional)
- **flip** (bool) – Flip, (optional)
- **cursor** (int) – Cursor, Mouse cursor style to use during the modal operator (in [0, inf], optional)
- **use_front_faces_only** (bool) – Front Faces Only, Affect only faces facing towards the view (optional)
- **use_limit_to_segment** (bool) – Limit to Segment, Apply the gesture action only to the area that is contained within the segment without extending its effect to the entire line (optional)
- **mode** (Literal['VALUE', 'VALUE_INVERSE', 'INVERT']) –

  Mode, (optional)

  - `VALUE`
    Value – Set mask to the level specified by the ‘value’ property.
  - `VALUE_INVERSE`
    Value Inverted – Set mask to the level specified by the inverted ‘value’ property.
  - `INVERT`
    Invert – Invert the mask.
- **value** (float) – Value, Mask level to use when mode is ‘Value’; zero means no masking and one is fully masked (in [0, 1], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paint.mask_polyline_gesture"></a>

### bpy.ops.paint.mask_polyline_gesture(*, path=None, use_front_faces_only=False, mode='VALUE', value=1.0)

Mask within a shape defined by the cursor

**Parameters:**

- **path** (`bpy_prop_collection`[`OperatorMousePath`] | None) – Path, (optional)
- **use_front_faces_only** (bool) – Front Faces Only, Affect only faces facing towards the view (optional)
- **mode** (Literal['VALUE', 'VALUE_INVERSE', 'INVERT']) –

  Mode, (optional)

  - `VALUE`
    Value – Set mask to the level specified by the ‘value’ property.
  - `VALUE_INVERSE`
    Value Inverted – Set mask to the level specified by the inverted ‘value’ property.
  - `INVERT`
    Invert – Invert the mask.
- **value** (float) – Value, Mask level to use when mode is ‘Value’; zero means no masking and one is fully masked (in [0, 1], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paint.project_image"></a>

### bpy.ops.paint.project_image(*, image='')

Project an edited render from the active camera back onto the object

**Parameters:**

**image** (str) – Image, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paint.sample_color"></a>

### bpy.ops.paint.sample_color(*, location=(0, 0), merged=False, palette=False)

Use the mouse to sample a color in the image

**Parameters:**

- **location** (Sequence[int]) – Location, (array of 2 items, in [0, inf], optional)
- **merged** (bool) – Sample Merged, Sample the output display color (optional)
- **palette** (bool) – Add to Palette, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paint.texture_paint_toggle"></a>

### bpy.ops.paint.texture_paint_toggle()

Toggle texture paint mode in 3D view

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paint.vert_select_all"></a>

### bpy.ops.paint.vert_select_all(*, action='TOGGLE')

Change selection for all vertices

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

<a id="bpy.ops.paint.vert_select_hide"></a>

### bpy.ops.paint.vert_select_hide(*, unselected=False)

Hide selected vertices

**Parameters:**

**unselected** (bool) – Unselected, Hide unselected rather than selected vertices (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paint.vert_select_less"></a>

### bpy.ops.paint.vert_select_less(*, face_step=True)

Deselect Vertices connected to existing selection

**Parameters:**

**face_step** (bool) – Face Step, Also deselect faces that only touch on a corner (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paint.vert_select_linked"></a>

### bpy.ops.paint.vert_select_linked()

Select linked vertices

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paint.vert_select_linked_pick"></a>

### bpy.ops.paint.vert_select_linked_pick(*, select=True)

Select linked vertices under the cursor

**Parameters:**

**select** (bool) – Select, Whether to select or deselect linked vertices under the cursor (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paint.vert_select_loop"></a>

### bpy.ops.paint.vert_select_loop(*, select=True, extend=False)

Select vertex loop under the cursor

**Parameters:**

- **select** (bool) – Select, If false, vertices will be deselected (optional)
- **extend** (bool) – Extend, Extend the selection (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paint.vert_select_more"></a>

### bpy.ops.paint.vert_select_more(*, face_step=True)

Select Vertices connected to existing selection

**Parameters:**

**face_step** (bool) – Face Step, Also select faces that only touch on a corner (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paint.vert_select_ungrouped"></a>

### bpy.ops.paint.vert_select_ungrouped(*, extend=False)

Select vertices without a group

**Parameters:**

**extend** (bool) – Extend, Extend the selection (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paint.vertex_color_brightness_contrast"></a>

### bpy.ops.paint.vertex_color_brightness_contrast(*, brightness=0.0, contrast=0.0)

Adjust vertex color brightness/contrast

**Parameters:**

- **brightness** (float) – Brightness, (in [-100, 100], optional)
- **contrast** (float) – Contrast, (in [-100, 100], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paint.vertex_color_dirt"></a>

### bpy.ops.paint.vertex_color_dirt(*, blur_strength=1.0, blur_iterations=1, clean_angle=3.14159, dirt_angle=0.0, dirt_only=False, normalize=True)

Generate a dirt map gradient based on cavity

**Parameters:**

- **blur_strength** (float) – Blur Strength, Blur strength per iteration (in [0.01, 1], optional)
- **blur_iterations** (int) – Blur Iterations, Number of times to blur the colors (higher blurs more) (in [0, 40], optional)
- **clean_angle** (float) – Highlight Angle, Less than 90 limits the angle used in the tonal range (in [0, 3.14159], optional)
- **dirt_angle** (float) – Dirt Angle, Less than 90 limits the angle used in the tonal range (in [0, 3.14159], optional)
- **dirt_only** (bool) – Dirt Only, Don’t calculate cleans for convex areas (optional)
- **normalize** (bool) – Normalize, Normalize the colors, increasing the contrast (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/vertexpaint_dirt.py:182](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/vertexpaint_dirt.py#L182)

<a id="bpy.ops.paint.vertex_color_from_weight"></a>

### bpy.ops.paint.vertex_color_from_weight()

Convert active weight into gray scale vertex colors

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paint.vertex_color_hsv"></a>

### bpy.ops.paint.vertex_color_hsv(*, h=0.5, s=1.0, v=1.0)

Adjust vertex color Hue/Saturation/Value

**Parameters:**

- **h** (float) – Hue, (in [0, 1], optional)
- **s** (float) – Saturation, (in [0, 2], optional)
- **v** (float) – Value, (in [0, 2], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paint.vertex_color_invert"></a>

### bpy.ops.paint.vertex_color_invert()

Invert RGB values

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paint.vertex_color_levels"></a>

### bpy.ops.paint.vertex_color_levels(*, offset=0.0, gain=1.0)

Adjust levels of vertex colors

**Parameters:**

- **offset** (float) – Offset, Value to add to colors (in [-1, 1], optional)
- **gain** (float) – Gain, Value to multiply colors by (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paint.vertex_color_set"></a>

### bpy.ops.paint.vertex_color_set(*, use_alpha=True)

Fill the active vertex color layer with the current paint color

**Parameters:**

**use_alpha** (bool) – Affect Alpha, Set color completely opaque instead of reusing existing alpha (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paint.vertex_color_smooth"></a>

### bpy.ops.paint.vertex_color_smooth()

Smooth colors across vertices

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paint.vertex_paint"></a>

### bpy.ops.paint.vertex_paint(*, stroke=None, mode='NORMAL', brush_toggle='None', pen_flip=False, override_location=False)

Paint a stroke in the active color attribute layer

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

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paint.vertex_paint_toggle"></a>

### bpy.ops.paint.vertex_paint_toggle()

Toggle the vertex paint mode in 3D view

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paint.visibility_filter"></a>

### bpy.ops.paint.visibility_filter(*, action='GROW', iterations=1, auto_iteration_count=True)

Edit the visibility of the current mesh

**Parameters:**

- **action** (Literal['GROW', 'SHRINK']) –

  Action, (optional)

  - `GROW`
    Grow Visibility – Grow the visibility by one face based on mesh topology.
  - `SHRINK`
    Shrink Visibility – Shrink the visibility by one face based on mesh topology.
- **iterations** (int) – Iterations, Number of times that the filter is going to be applied (in [1, 100], optional)
- **auto_iteration_count** (bool) – Auto Iteration Count, Use an automatic number of iterations based on the number of vertices of the sculpt (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paint.visibility_invert"></a>

### bpy.ops.paint.visibility_invert()

Invert the visibility of all vertices

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paint.weight_from_bones"></a>

### bpy.ops.paint.weight_from_bones(*, type='AUTOMATIC')

Set the weights of the groups matching the attached armature’s bones that have “Deform” option enabled, using the distance between the vertices and the bones

**Parameters:**

**type** (Literal['AUTOMATIC', 'ENVELOPES']) –

Type, Method to use for assigning weights (optional)

- `AUTOMATIC`
  Automatic – Automatic weights from bones.
- `ENVELOPES`
  From Envelopes – Weights from envelopes with user defined radius.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paint.weight_gradient"></a>

### bpy.ops.paint.weight_gradient(*, type='LINEAR', xstart=0, xend=0, ystart=0, yend=0, flip=False, cursor=5)

Draw a line to apply a weight gradient to selected vertices

**Parameters:**

- **type** (Literal['LINEAR', 'RADIAL']) – Type, (optional)
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

<a id="bpy.ops.paint.weight_paint"></a>

### bpy.ops.paint.weight_paint(*, stroke=None, mode='NORMAL', brush_toggle='None', pen_flip=False, override_location=False)

Paint a stroke in the current vertex group’s weights

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

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paint.weight_paint_toggle"></a>

### bpy.ops.paint.weight_paint_toggle()

Toggle weight paint mode in 3D view

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paint.weight_sample"></a>

### bpy.ops.paint.weight_sample()

Use the mouse to sample a weight in the 3D view

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paint.weight_sample_group"></a>

### bpy.ops.paint.weight_sample_group()

Select one of the vertex groups available under current mouse position

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paint.weight_set"></a>

### bpy.ops.paint.weight_set()

Fill the active vertex group with the current paint weight

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]
