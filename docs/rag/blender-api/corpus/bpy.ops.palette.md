<!-- source: Blender Python API reference 5.2 / bpy.ops.palette.html -->

<a id="module-bpy.ops.palette"></a>

# Palette Operators

<a id="bpy.ops.palette.color_add"></a>

### bpy.ops.palette.color_add()

Add new color to active palette

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.palette.color_delete"></a>

### bpy.ops.palette.color_delete()

Remove active color from palette

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.palette.color_move"></a>

### bpy.ops.palette.color_move(*, type='UP')

Move the active Color up/down in the list

**Parameters:**

**type** (Literal['UP', 'DOWN']) – Type, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.palette.extract_from_image"></a>

### bpy.ops.palette.extract_from_image(*, threshold=1)

Extract all colors used in Image and create a Palette

**Parameters:**

**threshold** (int) – Threshold, (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.palette.join"></a>

### bpy.ops.palette.join(*, palette='')

Join Palette Swatches

**Parameters:**

**palette** (str) – Palette, Name of the Palette (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.palette.new"></a>

### bpy.ops.palette.new()

Add new palette

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.palette.sort"></a>

### bpy.ops.palette.sort(*, type='HSV')

Sort Palette Colors

**Parameters:**

**type** (Literal['HSV', 'SVH', 'VHS', 'LUMINANCE']) – Type, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]
