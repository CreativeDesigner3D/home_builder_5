<!-- source: Blender Python API reference 5.2 / bpy.types.SceneGpencil.html -->

<a id="scenegpencil-bpy-struct"></a>

# SceneGpencil(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.SceneGpencil"></a>

### class bpy.types.SceneGpencil(bpy_struct)

Render settings

<a id="bpy.types.SceneGpencil.aa_samples"></a>

#### bpy.types.SceneGpencil.aa_samples

Number of supersampling anti-aliasing samples per pixel for final render (in [1, inf], default 8)

**Type:**

int

<a id="bpy.types.SceneGpencil.antialias_threshold"></a>

#### bpy.types.SceneGpencil.antialias_threshold

Threshold for edge detection algorithm (higher values might over-blur some part of the image) (in [0, inf], default 1.0)

**Type:**

float

<a id="bpy.types.SceneGpencil.antialias_threshold_render"></a>

#### bpy.types.SceneGpencil.antialias_threshold_render

Threshold for edge detection algorithm (higher values might over-blur some part of the image). Only applies to final render (in [0, inf], default 0.25)

**Type:**

float

<a id="bpy.types.SceneGpencil.motion_blur_steps"></a>

#### bpy.types.SceneGpencil.motion_blur_steps

Controls accuracy of motion blur, more steps result in longer render time. Only used when Motion Blur is enabled. Set to 0 to disable motion blur for Grease Pencil (in [0, inf], default 8)

**Type:**

int

<a id="bpy.types.SceneGpencil.bl_rna_get_subclass"></a>

#### classmethod bpy.types.SceneGpencil.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.SceneGpencil.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.SceneGpencil.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values

<a id="references"></a>

## References

|  |  |
| --- | --- |
| - [`Scene.grease_pencil_settings`](bpy.types.Scene.md#bpy.types.Scene.grease_pencil_settings "bpy.types.Scene.grease_pencil_settings") |  |
