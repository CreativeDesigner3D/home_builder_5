<!-- source: Blender Python API reference 5.2 / bpy.ops.cycles.html -->

<a id="module-bpy.ops.cycles"></a>

# Cycles Operators

<a id="bpy.ops.cycles.denoise_animation"></a>

### bpy.ops.cycles.denoise_animation(*, input_filepath='', output_filepath='')

Denoise rendered animation sequence using current scene and view layer settings. Requires denoising data passes and output to OpenEXR multilayer files

**Parameters:**

- **input_filepath** (str) – Input Filepath, File path for image to denoise. If not specified, uses the render file path and frame range from the scene (optional, never None)
- **output_filepath** (str) – Output Filepath, If not specified, renders will be denoised in-place (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[addons_core/cycles/operators.py:49](https://projects.blender.org/blender/blender/src/branch/main/scripts/addons_core/cycles/operators.py#L49)

<a id="bpy.ops.cycles.merge_images"></a>

### bpy.ops.cycles.merge_images(*, input_filepath1='', input_filepath2='', output_filepath='')

Combine OpenEXR multi-layer images rendered with different sample ranges into one image with reduced noise

**Parameters:**

- **input_filepath1** (str) – Input Filepath, File path for image to merge (optional, never None)
- **input_filepath2** (str) – Input Filepath, File path for image to merge (optional, never None)
- **output_filepath** (str) – Output Filepath, File path for merged image (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[addons_core/cycles/operators.py:137](https://projects.blender.org/blender/blender/src/branch/main/scripts/addons_core/cycles/operators.py#L137)

<a id="bpy.ops.cycles.use_shading_nodes"></a>

### bpy.ops.cycles.use_shading_nodes()

Enable nodes on a light

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[addons_core/cycles/operators.py:23](https://projects.blender.org/blender/blender/src/branch/main/scripts/addons_core/cycles/operators.py#L23)
