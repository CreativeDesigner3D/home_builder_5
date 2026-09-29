<!-- source: Blender Python API reference 5.2 / bpy.types.ColorManagedDisplaySettings.html -->

<a id="colormanageddisplaysettings-bpy-struct"></a>

# ColorManagedDisplaySettings(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.ColorManagedDisplaySettings"></a>

### class bpy.types.ColorManagedDisplaySettings(bpy_struct)

Color management specific to display device

<a id="bpy.types.ColorManagedDisplaySettings.display_device"></a>

#### bpy.types.ColorManagedDisplaySettings.display_device

Display name. For viewing, this is the display device that will be emulated by limiting the gamut and HDR colors. For image and video output, this is the display space used for writing. (default `'NONE'`)

**Type:**

Literal[‘NONE’]

<a id="bpy.types.ColorManagedDisplaySettings.emulation"></a>

#### bpy.types.ColorManagedDisplaySettings.emulation

Control how images in the chosen display are mapped to the physical display (default `'AUTO'`)

- `OFF`
  Off – Directly output image as produced by OpenColorIO. This is not correct in general, but may be used when the system configuration and actual display device is known to match the chosen display.
- `AUTO`
  Automatic – Display images consistent with most other applications, to preview images and video for export. A best effort is made to emulate the chosen display on the actual display device..

**Type:**

Literal[‘OFF’, ‘AUTO’]

<a id="bpy.types.ColorManagedDisplaySettings.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ColorManagedDisplaySettings.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ColorManagedDisplaySettings.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ColorManagedDisplaySettings.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`CompositorNodeConvertToDisplay.display_settings`](bpy.types.CompositorNodeConvertToDisplay.md#bpy.types.CompositorNodeConvertToDisplay.display_settings "bpy.types.CompositorNodeConvertToDisplay.display_settings") - [`ImageFormatSettings.display_settings`](bpy.types.ImageFormatSettings.md#bpy.types.ImageFormatSettings.display_settings "bpy.types.ImageFormatSettings.display_settings") | - [`Scene.display_settings`](bpy.types.Scene.md#bpy.types.Scene.display_settings "bpy.types.Scene.display_settings") |
