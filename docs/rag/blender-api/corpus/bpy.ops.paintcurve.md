<!-- source: Blender Python API reference 5.2 / bpy.ops.paintcurve.html -->

<a id="module-bpy.ops.paintcurve"></a>

# Paintcurve Operators

<a id="bpy.ops.paintcurve.add_point"></a>

### bpy.ops.paintcurve.add_point(*, location=(0, 0))

Add New Paint Curve Point

**Parameters:**

**location** (Sequence[int]) – Location, Location of vertex in area space (array of 2 items, in [0, 32767], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paintcurve.add_point_slide"></a>

### bpy.ops.paintcurve.add_point_slide(*, PAINTCURVE_OT_add_point={}, PAINTCURVE_OT_slide={})

Add new curve point and slide it

**Parameters:**

- **PAINTCURVE_OT_add_point** (dict[str, Any]) – Add New Paint Curve Point, Add New Paint Curve Point (optional, [`bpy.ops.paintcurve.add_point()`](#bpy.ops.paintcurve.add_point "bpy.ops.paintcurve.add_point") keyword arguments)
- **PAINTCURVE_OT_slide** (dict[str, Any]) – Slide Paint Curve Point, Select and slide paint curve point (optional, [`bpy.ops.paintcurve.slide()`](#bpy.ops.paintcurve.slide "bpy.ops.paintcurve.slide") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paintcurve.cursor"></a>

### bpy.ops.paintcurve.cursor()

Place cursor

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paintcurve.delete_point"></a>

### bpy.ops.paintcurve.delete_point()

Remove Paint Curve Point

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paintcurve.draw"></a>

### bpy.ops.paintcurve.draw()

Draw curve

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paintcurve.new"></a>

### bpy.ops.paintcurve.new()

Add new paint curve

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paintcurve.select"></a>

### bpy.ops.paintcurve.select(*, location=(0, 0), toggle=False, extend=False)

Select a paint curve point

**Parameters:**

- **location** (Sequence[int]) – Location, Location of vertex in area space (array of 2 items, in [0, 32767], optional)
- **toggle** (bool) – Toggle, (De)select all (optional)
- **extend** (bool) – Extend, Extend selection (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.paintcurve.slide"></a>

### bpy.ops.paintcurve.slide(*, align=False, select=True)

Select and slide paint curve point

**Parameters:**

- **align** (bool) – Align Handles, Aligns opposite point handle during transform (optional)
- **select** (bool) – Select, Attempt to select a point handle before transform (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]
