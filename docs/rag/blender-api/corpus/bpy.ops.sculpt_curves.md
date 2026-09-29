<!-- source: Blender Python API reference 5.2 / bpy.ops.sculpt_curves.html -->

<a id="module-bpy.ops.sculpt_curves"></a>

# Sculpt Curves Operators

<a id="bpy.ops.sculpt_curves.brush_stroke"></a>

### bpy.ops.sculpt_curves.brush_stroke(*, stroke=None, mode='NORMAL', brush_toggle='None', pen_flip=False)

Sculpt curves using a brush

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

<a id="bpy.ops.sculpt_curves.min_distance_edit"></a>

### bpy.ops.sculpt_curves.min_distance_edit()

Change the minimum distance used by the density brush

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sculpt_curves.select_grow"></a>

### bpy.ops.sculpt_curves.select_grow(*, distance=0.1)

Select curves which are close to curves that are selected already

**Parameters:**

**distance** (float) – Distance, By how much to grow the selection (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.sculpt_curves.select_random"></a>

### bpy.ops.sculpt_curves.select_random(*, seed=0, partial=False, probability=0.5, min=0.0, constant_per_curve=True)

Randomizes existing selection or create new random selection

**Parameters:**

- **seed** (int) – Seed, Source of randomness (in [-inf, inf], optional)
- **partial** (bool) – Partial, Allow points or curves to be selected partially (optional)
- **probability** (float) – Probability, Chance of every point or curve being included in the selection (in [0, 1], optional)
- **min** (float) – Min, Minimum value for the random selection (in [0, 1], optional)
- **constant_per_curve** (bool) – Constant per Curve, The generated random number is the same for every control point of a curve (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]
