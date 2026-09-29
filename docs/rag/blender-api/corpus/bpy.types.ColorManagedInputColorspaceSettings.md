<!-- source: Blender Python API reference 5.2 / bpy.types.ColorManagedInputColorspaceSettings.html -->

<a id="colormanagedinputcolorspacesettings-bpy-struct"></a>

# ColorManagedInputColorspaceSettings(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.ColorManagedInputColorspaceSettings"></a>

### class bpy.types.ColorManagedInputColorspaceSettings(bpy_struct)

Input color space settings

<a id="bpy.types.ColorManagedInputColorspaceSettings.is_data"></a>

#### bpy.types.ColorManagedInputColorspaceSettings.is_data

Treat image as non-color data without color management, like normal or displacement maps (default False)

**Type:**

bool

<a id="bpy.types.ColorManagedInputColorspaceSettings.name"></a>

#### bpy.types.ColorManagedInputColorspaceSettings.name

Color space in the image file, to convert to and from when saving and loading the image (default `'NONE'`)

**Type:**

Literal[[Color Space Convert Default Items](bpy_types_enum_items/color_space_convert_default_items.md#rna-enum-color-space-convert-default-items)]

<a id="bpy.types.ColorManagedInputColorspaceSettings.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ColorManagedInputColorspaceSettings.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ColorManagedInputColorspaceSettings.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ColorManagedInputColorspaceSettings.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Image.colorspace_settings`](bpy.types.Image.md#bpy.types.Image.colorspace_settings "bpy.types.Image.colorspace_settings") - [`ImageStrip.colorspace_settings`](bpy.types.ImageStrip.md#bpy.types.ImageStrip.colorspace_settings "bpy.types.ImageStrip.colorspace_settings") - [`MovieClip.colorspace_settings`](bpy.types.MovieClip.md#bpy.types.MovieClip.colorspace_settings "bpy.types.MovieClip.colorspace_settings") | - [`MovieStrip.colorspace_settings`](bpy.types.MovieStrip.md#bpy.types.MovieStrip.colorspace_settings "bpy.types.MovieStrip.colorspace_settings") - [`ImageFormatSettings.linear_colorspace_settings`](bpy.types.ImageFormatSettings.md#bpy.types.ImageFormatSettings.linear_colorspace_settings "bpy.types.ImageFormatSettings.linear_colorspace_settings") |
