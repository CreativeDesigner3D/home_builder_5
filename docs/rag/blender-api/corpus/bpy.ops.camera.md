<!-- source: Blender Python API reference 5.2 / bpy.ops.camera.html -->

<a id="module-bpy.ops.camera"></a>

# Camera Operators

<a id="bpy.ops.camera.preset_add"></a>

### bpy.ops.camera.preset_add(*, name='', remove_name=False, remove_active=False, use_focal_length=False)

Add or remove a Camera Preset

**Parameters:**

- **name** (str) – Name, Name of the preset, used to make the path name (optional, never None)
- **remove_name** (bool) – remove_name, (optional)
- **remove_active** (bool) – remove_active, (optional)
- **use_focal_length** (bool) – Include Focal Length, Include focal length into the preset (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/presets.py:119](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/presets.py#L119)

<a id="bpy.ops.camera.safe_areas_preset_add"></a>

### bpy.ops.camera.safe_areas_preset_add(*, name='', remove_name=False, remove_active=False)

Add or remove a Safe Areas Preset

**Parameters:**

- **name** (str) – Name, Name of the preset, used to make the path name (optional, never None)
- **remove_name** (bool) – remove_name, (optional)
- **remove_active** (bool) – remove_active, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/presets.py:119](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/presets.py#L119)
