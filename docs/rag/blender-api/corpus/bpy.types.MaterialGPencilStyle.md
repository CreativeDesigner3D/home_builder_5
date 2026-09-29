<!-- source: Blender Python API reference 5.2 / bpy.types.MaterialGPencilStyle.html -->

<a id="materialgpencilstyle-bpy-struct"></a>

# MaterialGPencilStyle(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.MaterialGPencilStyle"></a>

### class bpy.types.MaterialGPencilStyle(bpy_struct)

<a id="bpy.types.MaterialGPencilStyle.alignment_mode"></a>

#### bpy.types.MaterialGPencilStyle.alignment_mode

Defines how align Dots and Boxes with drawing path and object rotation (default `'PATH'`)

- `PATH`
  Path – Follow stroke drawing path and object rotation.
- `OBJECT`
  Object – Follow object rotation only.
- `FIXED`
  Fixed – Do not follow drawing path or object rotation and keeps aligned with viewport.

**Type:**

Literal[‘PATH’, ‘OBJECT’, ‘FIXED’]

<a id="bpy.types.MaterialGPencilStyle.alignment_rotation"></a>

#### bpy.types.MaterialGPencilStyle.alignment_rotation

Additional rotation applied to dots and square texture of strokes (in [-1.5708, 1.5708], default 0.0)

**Type:**

float

<a id="bpy.types.MaterialGPencilStyle.color"></a>

#### bpy.types.MaterialGPencilStyle.color

(array of 4 items, in [0, inf], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.MaterialGPencilStyle.fill_color"></a>

#### bpy.types.MaterialGPencilStyle.fill_color

Color for filling region bounded by each stroke (array of 4 items, in [0, inf], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.MaterialGPencilStyle.fill_image"></a>

#### bpy.types.MaterialGPencilStyle.fill_image

**Type:**

[`Image`](bpy.types.Image.md#bpy.types.Image "bpy.types.Image") | None

<a id="bpy.types.MaterialGPencilStyle.fill_style"></a>

#### bpy.types.MaterialGPencilStyle.fill_style

Select style used to fill strokes (default `'SOLID'`)

- `SOLID`
  Solid – Fill area with solid color.
- `GRADIENT`
  Gradient – Fill area with gradient color.
- `TEXTURE`
  Texture – Fill area with image texture.

**Type:**

Literal[‘SOLID’, ‘GRADIENT’, ‘TEXTURE’]

<a id="bpy.types.MaterialGPencilStyle.flip"></a>

#### bpy.types.MaterialGPencilStyle.flip

Flip filling colors (default False)

**Type:**

bool

<a id="bpy.types.MaterialGPencilStyle.ghost"></a>

#### bpy.types.MaterialGPencilStyle.ghost

Display strokes using this color when showing onion skins (default False)

**Type:**

bool

<a id="bpy.types.MaterialGPencilStyle.gradient_type"></a>

#### bpy.types.MaterialGPencilStyle.gradient_type

Select type of gradient used to fill strokes (default `'LINEAR'`)

- `LINEAR`
  Linear – Fill area with gradient color.
- `RADIAL`
  Radial – Fill area with radial gradient.

**Type:**

Literal[‘LINEAR’, ‘RADIAL’]

<a id="bpy.types.MaterialGPencilStyle.hide"></a>

#### bpy.types.MaterialGPencilStyle.hide

Set color Visibility (default False)

**Type:**

bool

<a id="bpy.types.MaterialGPencilStyle.is_fill_visible"></a>

#### bpy.types.MaterialGPencilStyle.is_fill_visible

True when opacity of fill is set high enough to be visible (default False, readonly)

**Type:**

bool

<a id="bpy.types.MaterialGPencilStyle.is_stroke_visible"></a>

#### bpy.types.MaterialGPencilStyle.is_stroke_visible

True when opacity of stroke is set high enough to be visible (default False, readonly)

**Type:**

bool

<a id="bpy.types.MaterialGPencilStyle.lock"></a>

#### bpy.types.MaterialGPencilStyle.lock

Protect color from further editing and/or frame changes (default False)

**Type:**

bool

<a id="bpy.types.MaterialGPencilStyle.mix_color"></a>

#### bpy.types.MaterialGPencilStyle.mix_color

Color for mixing with primary filling color (array of 4 items, in [0, inf], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.MaterialGPencilStyle.mix_factor"></a>

#### bpy.types.MaterialGPencilStyle.mix_factor

Mix Factor (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.MaterialGPencilStyle.mix_stroke_factor"></a>

#### bpy.types.MaterialGPencilStyle.mix_stroke_factor

Mix Stroke Factor (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.MaterialGPencilStyle.mode"></a>

#### bpy.types.MaterialGPencilStyle.mode

Select line type for strokes (default `'LINE'`)

- `LINE`
  Line – Draw strokes using a continuous line.
- `DOTS`
  Dots – Draw strokes using separated dots.
- `BOX`
  Squares – Draw strokes using separated squares.

**Type:**

Literal[‘LINE’, ‘DOTS’, ‘BOX’]

<a id="bpy.types.MaterialGPencilStyle.pass_index"></a>

#### bpy.types.MaterialGPencilStyle.pass_index

Index number for the “Color Index” pass (in [0, 32767], default 0)

**Type:**

int

<a id="bpy.types.MaterialGPencilStyle.pixel_size"></a>

#### bpy.types.MaterialGPencilStyle.pixel_size

Texture Pixel Size factor along the stroke (in [1, 5000], default 0.0)

**Type:**

float

<a id="bpy.types.MaterialGPencilStyle.placement_count"></a>

#### bpy.types.MaterialGPencilStyle.placement_count

Number of dots placed per segment (in [1, inf], default 0)

**Type:**

int

<a id="bpy.types.MaterialGPencilStyle.placement_density"></a>

#### bpy.types.MaterialGPencilStyle.placement_density

Density of dots along the stroke (in [0, inf], default 10.0)

**Type:**

float

<a id="bpy.types.MaterialGPencilStyle.placement_mode"></a>

#### bpy.types.MaterialGPencilStyle.placement_mode

Defines how Dots or Squares are placed along strokes (default `'RADIUS'`)

- `COUNT`
  Count – Place dots evenly along each segment of the stroke.
- `RADIUS`
  Radius – Place dots evenly with respect to radius.
- `DENSITY`
  Density – Place dots evenly along the length of the stroke.

**Type:**

Literal[‘COUNT’, ‘RADIUS’, ‘DENSITY’]

<a id="bpy.types.MaterialGPencilStyle.placement_radius_spacing"></a>

#### bpy.types.MaterialGPencilStyle.placement_radius_spacing

Spacing between dots as a percentage of the diameter (in [0, inf], default 100.0)

**Type:**

float

<a id="bpy.types.MaterialGPencilStyle.random_hue_factor"></a>

#### bpy.types.MaterialGPencilStyle.random_hue_factor

Randomize color hue (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.MaterialGPencilStyle.random_noise_scale"></a>

#### bpy.types.MaterialGPencilStyle.random_noise_scale

Scale the noise frequency (in [0, inf], default 1.0)

**Type:**

float

<a id="bpy.types.MaterialGPencilStyle.random_rotation_factor"></a>

#### bpy.types.MaterialGPencilStyle.random_rotation_factor

Randomize texture rotation (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.MaterialGPencilStyle.random_saturation_factor"></a>

#### bpy.types.MaterialGPencilStyle.random_saturation_factor

Randomize color saturation (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.MaterialGPencilStyle.random_size_factor"></a>

#### bpy.types.MaterialGPencilStyle.random_size_factor

Randomize the size (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.MaterialGPencilStyle.random_strength_factor"></a>

#### bpy.types.MaterialGPencilStyle.random_strength_factor

Randomize strength (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.MaterialGPencilStyle.random_value_factor"></a>

#### bpy.types.MaterialGPencilStyle.random_value_factor

Randomize color value (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.MaterialGPencilStyle.show_fill"></a>

#### bpy.types.MaterialGPencilStyle.show_fill

Show stroke fills of this material (default False)

Deprecated since version 5.10: removal planned in version 6.0

Unused but kept for compatibility with older versions of Blender.

**Type:**

bool

<a id="bpy.types.MaterialGPencilStyle.show_stroke"></a>

#### bpy.types.MaterialGPencilStyle.show_stroke

Show stroke lines of this material (default False)

Deprecated since version 5.10: removal planned in version 6.0

Unused but kept for compatibility with older versions of Blender.

**Type:**

bool

<a id="bpy.types.MaterialGPencilStyle.stroke_image"></a>

#### bpy.types.MaterialGPencilStyle.stroke_image

**Type:**

[`Image`](bpy.types.Image.md#bpy.types.Image "bpy.types.Image") | None

<a id="bpy.types.MaterialGPencilStyle.stroke_style"></a>

#### bpy.types.MaterialGPencilStyle.stroke_style

Select style used to draw strokes (default `'SOLID'`)

- `SOLID`
  Solid – Draw strokes with solid color.
- `TEXTURE`
  Texture – Draw strokes using texture.

**Type:**

Literal[‘SOLID’, ‘TEXTURE’]

<a id="bpy.types.MaterialGPencilStyle.texture_angle"></a>

#### bpy.types.MaterialGPencilStyle.texture_angle

Texture Orientation Angle (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.MaterialGPencilStyle.texture_clamp"></a>

#### bpy.types.MaterialGPencilStyle.texture_clamp

Do not repeat texture and clamp to one instance only (default False)

**Type:**

bool

<a id="bpy.types.MaterialGPencilStyle.texture_offset"></a>

#### bpy.types.MaterialGPencilStyle.texture_offset

Shift Texture in 2d Space (array of 2 items, in [-inf, inf], default (0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.MaterialGPencilStyle.texture_scale"></a>

#### bpy.types.MaterialGPencilStyle.texture_scale

Scale Factor for Texture (array of 2 items, in [-inf, inf], default (0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.MaterialGPencilStyle.use_fill_holdout"></a>

#### bpy.types.MaterialGPencilStyle.use_fill_holdout

Remove the color from underneath this stroke by using it as a mask (default False)

**Type:**

bool

<a id="bpy.types.MaterialGPencilStyle.use_overlap_strokes"></a>

#### bpy.types.MaterialGPencilStyle.use_overlap_strokes

Disable stencil and overlap self intersections with alpha materials (default False)

**Type:**

bool

<a id="bpy.types.MaterialGPencilStyle.use_randomization"></a>

#### bpy.types.MaterialGPencilStyle.use_randomization

Use material randomization (default False)

**Type:**

bool

<a id="bpy.types.MaterialGPencilStyle.use_stroke_holdout"></a>

#### bpy.types.MaterialGPencilStyle.use_stroke_holdout

Remove the color from underneath this stroke by using it as a mask (default False)

**Type:**

bool

<a id="bpy.types.MaterialGPencilStyle.bl_rna_get_subclass"></a>

#### classmethod bpy.types.MaterialGPencilStyle.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.MaterialGPencilStyle.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.MaterialGPencilStyle.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Material.grease_pencil`](bpy.types.Material.md#bpy.types.Material.grease_pencil "bpy.types.Material.grease_pencil") |  |
