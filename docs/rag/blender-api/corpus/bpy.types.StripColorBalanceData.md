<!-- source: Blender Python API reference 5.2 / bpy.types.StripColorBalanceData.html -->

<a id="stripcolorbalancedata-bpy-struct"></a>

# StripColorBalanceData(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

Subclasses

- [StripColorBalance(StripColorBalanceData)](bpy.types.StripColorBalance.md)

<a id="bpy.types.StripColorBalanceData"></a>

### class bpy.types.StripColorBalanceData(bpy_struct)

Color balance parameters for a sequence strip and its modifiers

<a id="bpy.types.StripColorBalanceData.correction_method"></a>

#### bpy.types.StripColorBalanceData.correction_method

(default `'LIFT_GAMMA_GAIN'`)

- `LIFT_GAMMA_GAIN`
  Lift/Gamma/Gain.
- `OFFSET_POWER_SLOPE`
  Offset/Power/Slope (ASC-CDL) – ASC-CDL standard color correction.

**Type:**

Literal[‘LIFT_GAMMA_GAIN’, ‘OFFSET_POWER_SLOPE’]

<a id="bpy.types.StripColorBalanceData.gain"></a>

#### bpy.types.StripColorBalanceData.gain

Color balance gain (highlights) (array of 3 items, in [0, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.StripColorBalanceData.gamma"></a>

#### bpy.types.StripColorBalanceData.gamma

Color balance gamma (midtones) (array of 3 items, in [0, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.StripColorBalanceData.invert_gain"></a>

#### bpy.types.StripColorBalanceData.invert_gain

Invert the gain color (default False)

**Type:**

bool

<a id="bpy.types.StripColorBalanceData.invert_gamma"></a>

#### bpy.types.StripColorBalanceData.invert_gamma

Invert the gamma color (default False)

**Type:**

bool

<a id="bpy.types.StripColorBalanceData.invert_lift"></a>

#### bpy.types.StripColorBalanceData.invert_lift

Invert the lift color (default False)

**Type:**

bool

<a id="bpy.types.StripColorBalanceData.invert_offset"></a>

#### bpy.types.StripColorBalanceData.invert_offset

Invert the offset color (default False)

**Type:**

bool

<a id="bpy.types.StripColorBalanceData.invert_power"></a>

#### bpy.types.StripColorBalanceData.invert_power

Invert the power color (default False)

**Type:**

bool

<a id="bpy.types.StripColorBalanceData.invert_slope"></a>

#### bpy.types.StripColorBalanceData.invert_slope

Invert the slope color (default False)

**Type:**

bool

<a id="bpy.types.StripColorBalanceData.lift"></a>

#### bpy.types.StripColorBalanceData.lift

Color balance lift (shadows) (array of 3 items, in [0, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.StripColorBalanceData.offset"></a>

#### bpy.types.StripColorBalanceData.offset

Correction for entire tonal range (array of 3 items, in [0, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.StripColorBalanceData.power"></a>

#### bpy.types.StripColorBalanceData.power

Correction for midtones (array of 3 items, in [0, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.StripColorBalanceData.slope"></a>

#### bpy.types.StripColorBalanceData.slope

Correction for highlights (array of 3 items, in [0, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.StripColorBalanceData.bl_rna_get_subclass"></a>

#### classmethod bpy.types.StripColorBalanceData.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.StripColorBalanceData.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.StripColorBalanceData.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`ColorBalanceModifier.color_balance`](bpy.types.ColorBalanceModifier.md#bpy.types.ColorBalanceModifier.color_balance "bpy.types.ColorBalanceModifier.color_balance") |  |
