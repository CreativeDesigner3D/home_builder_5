<!-- source: Blender Python API reference 5.2 / bpy.ops.gpencil.html -->

<a id="module-bpy.ops.gpencil"></a>

# Gpencil Operators

<a id="bpy.ops.gpencil.annotate"></a>

### bpy.ops.gpencil.annotate(*, mode='DRAW', arrowstyle_start='NONE', arrowstyle_end='NONE', use_stabilizer=False, stabilizer_factor=0.75, stabilizer_radius=35, stroke=None, wait_for_input=True)

Make annotations on the active data

**Parameters:**

- **mode** (Literal['DRAW', 'DRAW_STRAIGHT', 'DRAW_POLY', 'ERASER']) –

  Mode, Way to interpret mouse movements (optional)

  - `DRAW`
    Draw Freehand – Draw freehand stroke(s).
  - `DRAW_STRAIGHT`
    Draw Straight Lines – Draw straight line segment(s).
  - `DRAW_POLY`
    Draw Poly Line – Click to place endpoints of straight line segments (connected).
  - `ERASER`
    Eraser – Erase Annotation strokes.
- **arrowstyle_start** (Literal['NONE', 'ARROW', 'ARROW_OPEN', 'ARROW_OPEN_INVERTED', 'DIAMOND']) –

  Start Arrow Style, Stroke start style (optional)

  - `NONE`
    None – Don’t use any arrow/style in corner.
  - `ARROW`
    Arrow – Use closed arrow style.
  - `ARROW_OPEN`
    Open Arrow – Use open arrow style.
  - `ARROW_OPEN_INVERTED`
    Segment – Use perpendicular segment style.
  - `DIAMOND`
    Square – Use square style.
- **arrowstyle_end** (Literal['NONE', 'ARROW', 'ARROW_OPEN', 'ARROW_OPEN_INVERTED', 'DIAMOND']) –

  End Arrow Style, Stroke end style (optional)

  - `NONE`
    None – Don’t use any arrow/style in corner.
  - `ARROW`
    Arrow – Use closed arrow style.
  - `ARROW_OPEN`
    Open Arrow – Use open arrow style.
  - `ARROW_OPEN_INVERTED`
    Segment – Use perpendicular segment style.
  - `DIAMOND`
    Square – Use square style.
- **use_stabilizer** (bool) – Stabilize Stroke, Helper to draw smooth and clean lines. Press Shift for an invert effect (even if this option is not active) (optional)
- **stabilizer_factor** (float) – Stabilizer Stroke Factor, Higher values give a smoother stroke (in [0, 1], optional)
- **stabilizer_radius** (int) – Stabilizer Stroke Radius, Minimum distance from last point before stroke continues (in [0, 200], optional)
- **stroke** (`bpy_prop_collection`[`OperatorStrokeElement`] | None) – Stroke, (optional)
- **wait_for_input** (bool) – Wait for Input, Wait for first click instead of painting immediately (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.gpencil.annotation_active_frame_delete"></a>

### bpy.ops.gpencil.annotation_active_frame_delete()

Delete the active frame for the active Annotation Layer

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.gpencil.annotation_add"></a>

### bpy.ops.gpencil.annotation_add()

Add new Annotation data-block

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.gpencil.data_unlink"></a>

### bpy.ops.gpencil.data_unlink()

Unlink active Annotation data-block

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.gpencil.layer_annotation_add"></a>

### bpy.ops.gpencil.layer_annotation_add()

Add new Annotation layer or note for the active data-block

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.gpencil.layer_annotation_move"></a>

### bpy.ops.gpencil.layer_annotation_move(*, type='UP')

Move the active Annotation layer up/down in the list

**Parameters:**

**type** (Literal['UP', 'DOWN']) – Type, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.gpencil.layer_annotation_remove"></a>

### bpy.ops.gpencil.layer_annotation_remove()

Remove active Annotation layer

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]
