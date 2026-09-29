<!-- source: Blender Python API reference 5.2 / bpy.types.UnifiedPaintSettings.html -->

<a id="unifiedpaintsettings-bpy-struct"></a>

# UnifiedPaintSettings(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.UnifiedPaintSettings"></a>

### class bpy.types.UnifiedPaintSettings(bpy_struct)

Overrides for some of the active brush’s settings

<a id="bpy.types.UnifiedPaintSettings.color"></a>

#### bpy.types.UnifiedPaintSettings.color

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.UnifiedPaintSettings.hue_jitter"></a>

#### bpy.types.UnifiedPaintSettings.hue_jitter

Color jitter effect on hue (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.UnifiedPaintSettings.input_samples"></a>

#### bpy.types.UnifiedPaintSettings.input_samples

Number of input samples to average together to smooth the brush stroke (in [1, 64], default 1)

**Type:**

int

<a id="bpy.types.UnifiedPaintSettings.saturation_jitter"></a>

#### bpy.types.UnifiedPaintSettings.saturation_jitter

Color jitter effect on saturation (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.UnifiedPaintSettings.secondary_color"></a>

#### bpy.types.UnifiedPaintSettings.secondary_color

(array of 3 items, in [0, 1], default (1.0, 1.0, 1.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.UnifiedPaintSettings.size"></a>

#### bpy.types.UnifiedPaintSettings.size

Diameter of the brush (in [1, 10000], default 100)

**Type:**

int

<a id="bpy.types.UnifiedPaintSettings.strength"></a>

#### bpy.types.UnifiedPaintSettings.strength

How powerful the effect of the brush is when applied (in [0, 10], default 0.5)

**Type:**

float

<a id="bpy.types.UnifiedPaintSettings.unprojected_size"></a>

#### bpy.types.UnifiedPaintSettings.unprojected_size

Diameter of brush in Blender units (in [0.001, inf], default 0.58)

**Type:**

float

<a id="bpy.types.UnifiedPaintSettings.use_color_jitter"></a>

#### bpy.types.UnifiedPaintSettings.use_color_jitter

Jitter brush color (default False)

**Type:**

bool

<a id="bpy.types.UnifiedPaintSettings.use_locked_size"></a>

#### bpy.types.UnifiedPaintSettings.use_locked_size

Measure brush size relative to the view or the scene (default `'VIEW'`)

- `VIEW`
  View – Measure brush size relative to the view.
- `SCENE`
  Scene – Measure brush size relative to the scene.

**Type:**

Literal[‘VIEW’, ‘SCENE’]

<a id="bpy.types.UnifiedPaintSettings.use_random_press_hue"></a>

#### bpy.types.UnifiedPaintSettings.use_random_press_hue

Use pressure to modulate randomness (default False)

**Type:**

bool

<a id="bpy.types.UnifiedPaintSettings.use_random_press_sat"></a>

#### bpy.types.UnifiedPaintSettings.use_random_press_sat

Use pressure to modulate randomness (default False)

**Type:**

bool

<a id="bpy.types.UnifiedPaintSettings.use_random_press_val"></a>

#### bpy.types.UnifiedPaintSettings.use_random_press_val

Use pressure to modulate randomness (default False)

**Type:**

bool

<a id="bpy.types.UnifiedPaintSettings.use_stroke_random_hue"></a>

#### bpy.types.UnifiedPaintSettings.use_stroke_random_hue

Use randomness at stroke level (default False)

**Type:**

bool

<a id="bpy.types.UnifiedPaintSettings.use_stroke_random_sat"></a>

#### bpy.types.UnifiedPaintSettings.use_stroke_random_sat

Use randomness at stroke level (default False)

**Type:**

bool

<a id="bpy.types.UnifiedPaintSettings.use_stroke_random_val"></a>

#### bpy.types.UnifiedPaintSettings.use_stroke_random_val

Use randomness at stroke level (default False)

**Type:**

bool

<a id="bpy.types.UnifiedPaintSettings.use_unified_color"></a>

#### bpy.types.UnifiedPaintSettings.use_unified_color

Instead of per-brush color, the color is shared across brushes (default True)

**Type:**

bool

<a id="bpy.types.UnifiedPaintSettings.use_unified_input_samples"></a>

#### bpy.types.UnifiedPaintSettings.use_unified_input_samples

Instead of per-brush input samples, the value is shared across brushes (default False)

**Type:**

bool

<a id="bpy.types.UnifiedPaintSettings.use_unified_size"></a>

#### bpy.types.UnifiedPaintSettings.use_unified_size

Instead of per-brush size, the size is shared across brushes (default True)

**Type:**

bool

<a id="bpy.types.UnifiedPaintSettings.use_unified_strength"></a>

#### bpy.types.UnifiedPaintSettings.use_unified_strength

Instead of per-brush strength, the strength is shared across brushes (default False)

**Type:**

bool

<a id="bpy.types.UnifiedPaintSettings.use_unified_weight"></a>

#### bpy.types.UnifiedPaintSettings.use_unified_weight

Instead of per-brush weight, the weight is shared across brushes (default False)

**Type:**

bool

<a id="bpy.types.UnifiedPaintSettings.value_jitter"></a>

#### bpy.types.UnifiedPaintSettings.value_jitter

Color jitter effect on value (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.UnifiedPaintSettings.weight"></a>

#### bpy.types.UnifiedPaintSettings.weight

Weight to assign in vertex groups (in [0, 1], default 0.5)

**Type:**

float

<a id="bpy.types.UnifiedPaintSettings.bl_rna_get_subclass"></a>

#### classmethod bpy.types.UnifiedPaintSettings.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.UnifiedPaintSettings.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.UnifiedPaintSettings.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Paint.unified_paint_settings`](bpy.types.Paint.md#bpy.types.Paint.unified_paint_settings "bpy.types.Paint.unified_paint_settings") |  |
