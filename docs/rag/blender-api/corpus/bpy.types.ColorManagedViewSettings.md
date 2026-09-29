<!-- source: Blender Python API reference 5.2 / bpy.types.ColorManagedViewSettings.html -->

<a id="colormanagedviewsettings-bpy-struct"></a>

# ColorManagedViewSettings(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.ColorManagedViewSettings"></a>

### class bpy.types.ColorManagedViewSettings(bpy_struct)

Color management settings used for displaying images on the display

<a id="bpy.types.ColorManagedViewSettings.curve_mapping"></a>

#### bpy.types.ColorManagedViewSettings.curve_mapping

Color curve mapping applied before display transform (readonly)

**Type:**

[`CurveMapping`](bpy.types.CurveMapping.md#bpy.types.CurveMapping "bpy.types.CurveMapping") | None

<a id="bpy.types.ColorManagedViewSettings.exposure"></a>

#### bpy.types.ColorManagedViewSettings.exposure

Exposure (stops) applied before display transform, multiplying by 2^exposure (in [-32, 32], default 0.0)

**Type:**

float

<a id="bpy.types.ColorManagedViewSettings.gamma"></a>

#### bpy.types.ColorManagedViewSettings.gamma

Additional gamma encoding after display transform, for output with custom gamma (in [0, 5], default 1.0)

**Type:**

float

<a id="bpy.types.ColorManagedViewSettings.is_hdr"></a>

#### bpy.types.ColorManagedViewSettings.is_hdr

The display and view transform supports high dynamic range colors (default False, readonly)

**Type:**

bool

<a id="bpy.types.ColorManagedViewSettings.look"></a>

#### bpy.types.ColorManagedViewSettings.look

Additional transform applied before view transform for artistic needs (default `'NONE'`)

- `NONE`
  None – Do not modify image in an artistic manner.

**Type:**

Literal[‘NONE’]

<a id="bpy.types.ColorManagedViewSettings.support_emulation"></a>

#### bpy.types.ColorManagedViewSettings.support_emulation

The display and view transform supports automatic emulation for another display device, using the display color spaces mechanism in OpenColorIO v2 configurations (default False, readonly)

**Type:**

bool

<a id="bpy.types.ColorManagedViewSettings.use_curve_mapping"></a>

#### bpy.types.ColorManagedViewSettings.use_curve_mapping

Use RGB curved for pre-display transformation (default False)

**Type:**

bool

<a id="bpy.types.ColorManagedViewSettings.use_white_balance"></a>

#### bpy.types.ColorManagedViewSettings.use_white_balance

Perform chromatic adaption from a different white point (default False)

**Type:**

bool

<a id="bpy.types.ColorManagedViewSettings.view_transform"></a>

#### bpy.types.ColorManagedViewSettings.view_transform

View used when converting image to a display space (default `'NONE'`)

- `NONE`
  None – Do not perform any color transform on display, use old non-color managed technique for display.

**Type:**

Literal[‘NONE’]

<a id="bpy.types.ColorManagedViewSettings.white_balance_temperature"></a>

#### bpy.types.ColorManagedViewSettings.white_balance_temperature

Color temperature of the scene’s white point (in [1800, 100000], default 6500.0)

**Type:**

float

<a id="bpy.types.ColorManagedViewSettings.white_balance_tint"></a>

#### bpy.types.ColorManagedViewSettings.white_balance_tint

Color tint of the scene’s white point (the default of 10 matches daylight) (in [-500, 500], default 10.0)

**Type:**

float

<a id="bpy.types.ColorManagedViewSettings.white_balance_whitepoint"></a>

#### bpy.types.ColorManagedViewSettings.white_balance_whitepoint

The color which gets mapped to white (automatically converted to/from temperature and tint) (array of 3 items, in [0, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ColorManagedViewSettings.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ColorManagedViewSettings.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ColorManagedViewSettings.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ColorManagedViewSettings.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`CompositorNodeConvertToDisplay.view_settings`](bpy.types.CompositorNodeConvertToDisplay.md#bpy.types.CompositorNodeConvertToDisplay.view_settings "bpy.types.CompositorNodeConvertToDisplay.view_settings") - [`ImageFormatSettings.view_settings`](bpy.types.ImageFormatSettings.md#bpy.types.ImageFormatSettings.view_settings "bpy.types.ImageFormatSettings.view_settings") | - [`Scene.view_settings`](bpy.types.Scene.md#bpy.types.Scene.view_settings "bpy.types.Scene.view_settings") |
