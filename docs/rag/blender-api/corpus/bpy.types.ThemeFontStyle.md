<!-- source: Blender Python API reference 5.2 / bpy.types.ThemeFontStyle.html -->

<a id="themefontstyle-bpy-struct"></a>

# ThemeFontStyle(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.ThemeFontStyle"></a>

### class bpy.types.ThemeFontStyle(bpy_struct)

Theme settings for Font

<a id="bpy.types.ThemeFontStyle.character_weight"></a>

#### bpy.types.ThemeFontStyle.character_weight

Weight of the characters. 100-900, 400 is normal. (in [100, 900], default 400)

**Type:**

int

<a id="bpy.types.ThemeFontStyle.points"></a>

#### bpy.types.ThemeFontStyle.points

Font size in points (in [6, 32], default 0.0)

**Type:**

float

<a id="bpy.types.ThemeFontStyle.shadow"></a>

#### bpy.types.ThemeFontStyle.shadow

Shadow type (0 none, 3, 5 blur, 6 outline) (in [0, 6], default 0)

**Type:**

int

<a id="bpy.types.ThemeFontStyle.shadow_alpha"></a>

#### bpy.types.ThemeFontStyle.shadow_alpha

(in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.ThemeFontStyle.shadow_offset_x"></a>

#### bpy.types.ThemeFontStyle.shadow_offset_x

Shadow offset in pixels (in [-10, 10], default 0)

**Type:**

int

<a id="bpy.types.ThemeFontStyle.shadow_offset_y"></a>

#### bpy.types.ThemeFontStyle.shadow_offset_y

Shadow offset in pixels (in [-10, 10], default 0)

**Type:**

int

<a id="bpy.types.ThemeFontStyle.shadow_value"></a>

#### bpy.types.ThemeFontStyle.shadow_value

Shadow color in gray value (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.ThemeFontStyle.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ThemeFontStyle.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ThemeFontStyle.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ThemeFontStyle.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`ThemeStyle.panel_title`](bpy.types.ThemeStyle.md#bpy.types.ThemeStyle.panel_title "bpy.types.ThemeStyle.panel_title") - [`ThemeStyle.tooltip`](bpy.types.ThemeStyle.md#bpy.types.ThemeStyle.tooltip "bpy.types.ThemeStyle.tooltip") | - [`ThemeStyle.widget`](bpy.types.ThemeStyle.md#bpy.types.ThemeStyle.widget "bpy.types.ThemeStyle.widget") |
