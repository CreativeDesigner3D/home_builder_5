<!-- source: Blender Python API reference 5.2 / bpy.types.ColorMapping.html -->

<a id="colormapping-bpy-struct"></a>

# ColorMapping(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.ColorMapping"></a>

### class bpy.types.ColorMapping(bpy_struct)

Color mapping settings

<a id="bpy.types.ColorMapping.blend_color"></a>

#### bpy.types.ColorMapping.blend_color

Blend color to mix with texture output color (array of 3 items, in [0, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ColorMapping.blend_factor"></a>

#### bpy.types.ColorMapping.blend_factor

(in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.ColorMapping.blend_type"></a>

#### bpy.types.ColorMapping.blend_type

Mode used to mix with texture output color (default `'MIX'`)

**Type:**

Literal[‘MIX’, ‘DARKEN’, ‘MULTIPLY’, ‘LIGHTEN’, ‘SCREEN’, ‘ADD’, ‘OVERLAY’, ‘SOFT_LIGHT’, ‘LINEAR_LIGHT’, ‘DIFFERENCE’, ‘SUBTRACT’, ‘DIVIDE’, ‘HUE’, ‘SATURATION’, ‘COLOR’, ‘VALUE’]

<a id="bpy.types.ColorMapping.brightness"></a>

#### bpy.types.ColorMapping.brightness

Adjust the brightness of the texture (in [0, 2], default 0.0)

**Type:**

float

<a id="bpy.types.ColorMapping.color_ramp"></a>

#### bpy.types.ColorMapping.color_ramp

(readonly)

**Type:**

[`ColorRamp`](bpy.types.ColorRamp.md#bpy.types.ColorRamp "bpy.types.ColorRamp") | None

<a id="bpy.types.ColorMapping.contrast"></a>

#### bpy.types.ColorMapping.contrast

Adjust the contrast of the texture (in [0, 5], default 0.0)

**Type:**

float

<a id="bpy.types.ColorMapping.saturation"></a>

#### bpy.types.ColorMapping.saturation

Adjust the saturation of colors in the texture (in [0, 2], default 0.0)

**Type:**

float

<a id="bpy.types.ColorMapping.use_color_ramp"></a>

#### bpy.types.ColorMapping.use_color_ramp

Toggle color ramp operations (default False)

**Type:**

bool

<a id="bpy.types.ColorMapping.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ColorMapping.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ColorMapping.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ColorMapping.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`ShaderNodeTexBrick.color_mapping`](bpy.types.ShaderNodeTexBrick.md#bpy.types.ShaderNodeTexBrick.color_mapping "bpy.types.ShaderNodeTexBrick.color_mapping") - [`ShaderNodeTexChecker.color_mapping`](bpy.types.ShaderNodeTexChecker.md#bpy.types.ShaderNodeTexChecker.color_mapping "bpy.types.ShaderNodeTexChecker.color_mapping") - [`ShaderNodeTexEnvironment.color_mapping`](bpy.types.ShaderNodeTexEnvironment.md#bpy.types.ShaderNodeTexEnvironment.color_mapping "bpy.types.ShaderNodeTexEnvironment.color_mapping") - [`ShaderNodeTexGabor.color_mapping`](bpy.types.ShaderNodeTexGabor.md#bpy.types.ShaderNodeTexGabor.color_mapping "bpy.types.ShaderNodeTexGabor.color_mapping") - [`ShaderNodeTexGradient.color_mapping`](bpy.types.ShaderNodeTexGradient.md#bpy.types.ShaderNodeTexGradient.color_mapping "bpy.types.ShaderNodeTexGradient.color_mapping") - [`ShaderNodeTexImage.color_mapping`](bpy.types.ShaderNodeTexImage.md#bpy.types.ShaderNodeTexImage.color_mapping "bpy.types.ShaderNodeTexImage.color_mapping") | - [`ShaderNodeTexMagic.color_mapping`](bpy.types.ShaderNodeTexMagic.md#bpy.types.ShaderNodeTexMagic.color_mapping "bpy.types.ShaderNodeTexMagic.color_mapping") - [`ShaderNodeTexNoise.color_mapping`](bpy.types.ShaderNodeTexNoise.md#bpy.types.ShaderNodeTexNoise.color_mapping "bpy.types.ShaderNodeTexNoise.color_mapping") - [`ShaderNodeTexSky.color_mapping`](bpy.types.ShaderNodeTexSky.md#bpy.types.ShaderNodeTexSky.color_mapping "bpy.types.ShaderNodeTexSky.color_mapping") - [`ShaderNodeTexVoronoi.color_mapping`](bpy.types.ShaderNodeTexVoronoi.md#bpy.types.ShaderNodeTexVoronoi.color_mapping "bpy.types.ShaderNodeTexVoronoi.color_mapping") - [`ShaderNodeTexWave.color_mapping`](bpy.types.ShaderNodeTexWave.md#bpy.types.ShaderNodeTexWave.color_mapping "bpy.types.ShaderNodeTexWave.color_mapping") |
