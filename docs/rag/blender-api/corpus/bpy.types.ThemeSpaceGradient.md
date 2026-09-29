<!-- source: Blender Python API reference 5.2 / bpy.types.ThemeSpaceGradient.html -->

<a id="themespacegradient-bpy-struct"></a>

# ThemeSpaceGradient(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.ThemeSpaceGradient"></a>

### class bpy.types.ThemeSpaceGradient(bpy_struct)

<a id="bpy.types.ThemeSpaceGradient.gradients"></a>

#### bpy.types.ThemeSpaceGradient.gradients

(readonly, never None)

**Type:**

[`ThemeGradientColors`](bpy.types.ThemeGradientColors.md#bpy.types.ThemeGradientColors "bpy.types.ThemeGradientColors")

<a id="bpy.types.ThemeSpaceGradient.header"></a>

#### bpy.types.ThemeSpaceGradient.header

(array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.ThemeSpaceGradient.header_text"></a>

#### bpy.types.ThemeSpaceGradient.header_text

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeSpaceGradient.header_text_hi"></a>

#### bpy.types.ThemeSpaceGradient.header_text_hi

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeSpaceGradient.text"></a>

#### bpy.types.ThemeSpaceGradient.text

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeSpaceGradient.text_hi"></a>

#### bpy.types.ThemeSpaceGradient.text_hi

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeSpaceGradient.title"></a>

#### bpy.types.ThemeSpaceGradient.title

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeSpaceGradient.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ThemeSpaceGradient.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ThemeSpaceGradient.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ThemeSpaceGradient.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`ThemeView3D.space`](bpy.types.ThemeView3D.md#bpy.types.ThemeView3D.space "bpy.types.ThemeView3D.space") |  |
