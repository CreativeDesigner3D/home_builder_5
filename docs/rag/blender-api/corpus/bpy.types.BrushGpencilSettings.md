<!-- source: Blender Python API reference 5.2 / bpy.types.BrushGpencilSettings.html -->

<a id="brushgpencilsettings-bpy-struct"></a>

# BrushGpencilSettings(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.BrushGpencilSettings"></a>

### class bpy.types.BrushGpencilSettings(bpy_struct)

Settings for Grease Pencil brush

<a id="bpy.types.BrushGpencilSettings.active_smooth_factor"></a>

#### bpy.types.BrushGpencilSettings.active_smooth_factor

Amount of smoothing while drawing (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.BrushGpencilSettings.angle"></a>

#### bpy.types.BrushGpencilSettings.angle

Direction of the stroke at which brush gives maximal thickness (0° for horizontal) (in [-1.5708, 1.5708], default 0.0)

**Type:**

float

<a id="bpy.types.BrushGpencilSettings.angle_factor"></a>

#### bpy.types.BrushGpencilSettings.angle_factor

Reduce brush thickness by this factor when stroke is perpendicular to ‘Angle’ direction (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.BrushGpencilSettings.aspect"></a>

#### bpy.types.BrushGpencilSettings.aspect

(array of 2 items, in [0.01, 1], default (0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.BrushGpencilSettings.brush_draw_mode"></a>

#### bpy.types.BrushGpencilSettings.brush_draw_mode

Preselected mode when using this brush (default `'ACTIVE'`)

- `ACTIVE`
  Active – Use current mode.
- `MATERIAL`
  Material – Use always material mode.
- `VERTEXCOLOR`
  Vertex Color – Use always Vertex Color mode.

**Type:**

Literal[‘ACTIVE’, ‘MATERIAL’, ‘VERTEXCOLOR’]

<a id="bpy.types.BrushGpencilSettings.caps_type"></a>

#### bpy.types.BrushGpencilSettings.caps_type

The shape of the start and end of the stroke (default `'ROUND'`)

**Type:**

Literal[‘ROUND’, ‘FLAT’]

<a id="bpy.types.BrushGpencilSettings.conversion_threshold"></a>

#### bpy.types.BrushGpencilSettings.conversion_threshold

Threshold distance between points for conversion (in [0, inf], default 0.001)

**Type:**

float

<a id="bpy.types.BrushGpencilSettings.curve_jitter"></a>

#### bpy.types.BrushGpencilSettings.curve_jitter

Curve used for the jitter effect (readonly)

**Type:**

[`CurveMapping`](bpy.types.CurveMapping.md#bpy.types.CurveMapping "bpy.types.CurveMapping") | None

<a id="bpy.types.BrushGpencilSettings.curve_random_hue"></a>

#### bpy.types.BrushGpencilSettings.curve_random_hue

Curve used for modulating effect (readonly)

**Type:**

[`CurveMapping`](bpy.types.CurveMapping.md#bpy.types.CurveMapping "bpy.types.CurveMapping") | None

<a id="bpy.types.BrushGpencilSettings.curve_random_pressure"></a>

#### bpy.types.BrushGpencilSettings.curve_random_pressure

Curve used for modulating effect (readonly)

**Type:**

[`CurveMapping`](bpy.types.CurveMapping.md#bpy.types.CurveMapping "bpy.types.CurveMapping") | None

<a id="bpy.types.BrushGpencilSettings.curve_random_saturation"></a>

#### bpy.types.BrushGpencilSettings.curve_random_saturation

Curve used for modulating effect (readonly)

**Type:**

[`CurveMapping`](bpy.types.CurveMapping.md#bpy.types.CurveMapping "bpy.types.CurveMapping") | None

<a id="bpy.types.BrushGpencilSettings.curve_random_strength"></a>

#### bpy.types.BrushGpencilSettings.curve_random_strength

Curve used for modulating effect (readonly)

**Type:**

[`CurveMapping`](bpy.types.CurveMapping.md#bpy.types.CurveMapping "bpy.types.CurveMapping") | None

<a id="bpy.types.BrushGpencilSettings.curve_random_uv"></a>

#### bpy.types.BrushGpencilSettings.curve_random_uv

Curve used for modulating effect (readonly)

**Type:**

[`CurveMapping`](bpy.types.CurveMapping.md#bpy.types.CurveMapping "bpy.types.CurveMapping") | None

<a id="bpy.types.BrushGpencilSettings.curve_random_value"></a>

#### bpy.types.BrushGpencilSettings.curve_random_value

Curve used for modulating effect (readonly)

**Type:**

[`CurveMapping`](bpy.types.CurveMapping.md#bpy.types.CurveMapping "bpy.types.CurveMapping") | None

<a id="bpy.types.BrushGpencilSettings.curve_sensitivity"></a>

#### bpy.types.BrushGpencilSettings.curve_sensitivity

Curve used for the sensitivity (readonly)

**Type:**

[`CurveMapping`](bpy.types.CurveMapping.md#bpy.types.CurveMapping "bpy.types.CurveMapping") | None

<a id="bpy.types.BrushGpencilSettings.curve_strength"></a>

#### bpy.types.BrushGpencilSettings.curve_strength

Curve used for the strength (readonly)

**Type:**

[`CurveMapping`](bpy.types.CurveMapping.md#bpy.types.CurveMapping "bpy.types.CurveMapping") | None

<a id="bpy.types.BrushGpencilSettings.curve_type"></a>

#### bpy.types.BrushGpencilSettings.curve_type

Type of curves (default `'CATMULL_ROM'`)

**Type:**

Literal[[Curves Type Items](bpy_types_enum_items/curves_type_items.md#rna-enum-curves-type-items)]

<a id="bpy.types.BrushGpencilSettings.dilate"></a>

#### bpy.types.BrushGpencilSettings.dilate

Number of pixels to expand or contract fill area (in [-40, 40], default 1)

**Type:**

int

<a id="bpy.types.BrushGpencilSettings.eraser_mode"></a>

#### bpy.types.BrushGpencilSettings.eraser_mode

Eraser Mode (default `'SOFT'`)

- `SOFT`
  Dissolve – Erase strokes, fading their points strength and thickness.
- `HARD`
  Point – Erase stroke points.
- `STROKE`
  Stroke – Erase entire strokes.

**Type:**

Literal[‘SOFT’, ‘HARD’, ‘STROKE’]

<a id="bpy.types.BrushGpencilSettings.eraser_strength_factor"></a>

#### bpy.types.BrushGpencilSettings.eraser_strength_factor

Amount of erasing for strength (in [0, 100], default 0.0)

**Type:**

float

<a id="bpy.types.BrushGpencilSettings.eraser_thickness_factor"></a>

#### bpy.types.BrushGpencilSettings.eraser_thickness_factor

Amount of erasing for thickness (in [0, 100], default 0.0)

**Type:**

float

<a id="bpy.types.BrushGpencilSettings.extend_stroke_factor"></a>

#### bpy.types.BrushGpencilSettings.extend_stroke_factor

Strokes end extension for closing gaps, use zero to disable (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.BrushGpencilSettings.fill_direction"></a>

#### bpy.types.BrushGpencilSettings.fill_direction

Direction of the fill (default `'NORMAL'`)

- `NORMAL`
  Normal – Fill internal area.
- `INVERT`
  Inverted – Fill inverted area.

**Type:**

Literal[‘NORMAL’, ‘INVERT’]

<a id="bpy.types.BrushGpencilSettings.fill_draw_mode"></a>

#### bpy.types.BrushGpencilSettings.fill_draw_mode

Mode to draw boundary limits (default `'BOTH'`)

- `BOTH`
  All – Use both visible strokes and edit lines as fill boundary limits.
- `STROKE`
  Strokes – Use visible strokes as fill boundary limits.
- `CONTROL`
  Edit Lines – Use edit lines as fill boundary limits.

**Type:**

Literal[‘BOTH’, ‘STROKE’, ‘CONTROL’]

<a id="bpy.types.BrushGpencilSettings.fill_extend_mode"></a>

#### bpy.types.BrushGpencilSettings.fill_extend_mode

Types of stroke extensions used for closing gaps (default `'EXTEND'`)

- `EXTEND`
  Extend – Extend strokes in straight lines.
- `RADIUS`
  Radius – Connect endpoints that are close together.

**Type:**

Literal[‘EXTEND’, ‘RADIUS’]

<a id="bpy.types.BrushGpencilSettings.fill_factor"></a>

#### bpy.types.BrushGpencilSettings.fill_factor

Factor for fill boundary accuracy, higher values are more accurate but slower (in [0.05, 8], default 0.0)

**Type:**

float

<a id="bpy.types.BrushGpencilSettings.fill_gap_factor"></a>

#### bpy.types.BrushGpencilSettings.fill_gap_factor

The sensitivity of the gap detection. Higher values results in more gaps detected and as such can create smaller fills (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.BrushGpencilSettings.fill_internal_gaps"></a>

#### bpy.types.BrushGpencilSettings.fill_internal_gaps

Stop at internal gaps (default False)

**Type:**

bool

<a id="bpy.types.BrushGpencilSettings.fill_layer_mode"></a>

#### bpy.types.BrushGpencilSettings.fill_layer_mode

Layers used as boundaries (default `'VISIBLE'`)

- `VISIBLE`
  Visible – Visible layers.
- `ACTIVE`
  Active – Only active layer.
- `ABOVE`
  Layer Above – Layer above active.
- `BELOW`
  Layer Below – Layer below active.
- `ALL_ABOVE`
  All Above – All layers above active.
- `ALL_BELOW`
  All Below – All layers below active.

**Type:**

Literal[‘VISIBLE’, ‘ACTIVE’, ‘ABOVE’, ‘BELOW’, ‘ALL_ABOVE’, ‘ALL_BELOW’]

<a id="bpy.types.BrushGpencilSettings.fill_simplify_level"></a>

#### bpy.types.BrushGpencilSettings.fill_simplify_level

Number of simplify steps (large values reduce fill accuracy) (in [0, 10], default 0)

**Type:**

int

<a id="bpy.types.BrushGpencilSettings.fill_solver"></a>

#### bpy.types.BrushGpencilSettings.fill_solver

Method used for when filling (default `'DELAUNAY'`)

- `DELAUNAY`
  Delaunay – Use the exact geometry to create fills.
- `PIXEL`
  Pixel – Use pixel based flooding to create fills.

**Type:**

Literal[‘DELAUNAY’, ‘PIXEL’]

<a id="bpy.types.BrushGpencilSettings.fill_threshold"></a>

#### bpy.types.BrushGpencilSettings.fill_threshold

Threshold to consider color transparent for filling (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.BrushGpencilSettings.hardness"></a>

#### bpy.types.BrushGpencilSettings.hardness

Gradient from the center of Dot and Box strokes (set to 1 for a solid stroke) (in [0.001, 1], default 1.0)

**Type:**

float

<a id="bpy.types.BrushGpencilSettings.input_samples"></a>

#### bpy.types.BrushGpencilSettings.input_samples

Generated intermediate points for very fast mouse movements (Set to 0 to disable) (in [0, 10], default 0)

**Type:**

int

<a id="bpy.types.BrushGpencilSettings.material"></a>

#### bpy.types.BrushGpencilSettings.material

Material used for strokes drawn using this brush

**Type:**

[`Material`](bpy.types.Material.md#bpy.types.Material "bpy.types.Material") | None

<a id="bpy.types.BrushGpencilSettings.material_alt"></a>

#### bpy.types.BrushGpencilSettings.material_alt

Material used for secondary uses for this brush

**Type:**

[`Material`](bpy.types.Material.md#bpy.types.Material "bpy.types.Material") | None

<a id="bpy.types.BrushGpencilSettings.outline_thickness_factor"></a>

#### bpy.types.BrushGpencilSettings.outline_thickness_factor

Thickness of the outline stroke relative to current brush thickness (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.BrushGpencilSettings.pen_jitter"></a>

#### bpy.types.BrushGpencilSettings.pen_jitter

Jitter factor of brush radius for new strokes (in [0, 100], default 0.0)

**Type:**

float

<a id="bpy.types.BrushGpencilSettings.pen_smooth_factor"></a>

#### bpy.types.BrushGpencilSettings.pen_smooth_factor

Amount of smoothing to apply after finish newly created strokes, to reduce jitter/noise (in [0, 2], default 0.0)

**Type:**

float

<a id="bpy.types.BrushGpencilSettings.pen_smooth_steps"></a>

#### bpy.types.BrushGpencilSettings.pen_smooth_steps

Number of times to smooth newly created strokes (in [0, 100], default 0)

**Type:**

int

<a id="bpy.types.BrushGpencilSettings.pen_strength"></a>

#### bpy.types.BrushGpencilSettings.pen_strength

Color strength for new strokes (affect alpha factor of color) (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.BrushGpencilSettings.pen_subdivision_steps"></a>

#### bpy.types.BrushGpencilSettings.pen_subdivision_steps

Number of times to subdivide newly created strokes, for less jagged strokes (in [0, 3], default 0)

**Type:**

int

<a id="bpy.types.BrushGpencilSettings.pin_draw_mode"></a>

#### bpy.types.BrushGpencilSettings.pin_draw_mode

Pin the mode to the brush (default False)

**Type:**

bool

<a id="bpy.types.BrushGpencilSettings.random_hue_factor"></a>

#### bpy.types.BrushGpencilSettings.random_hue_factor

Random factor to modify original hue (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.BrushGpencilSettings.random_pressure"></a>

#### bpy.types.BrushGpencilSettings.random_pressure

Randomness factor for pressure in new strokes (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.BrushGpencilSettings.random_saturation_factor"></a>

#### bpy.types.BrushGpencilSettings.random_saturation_factor

Random factor to modify original saturation (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.BrushGpencilSettings.random_strength"></a>

#### bpy.types.BrushGpencilSettings.random_strength

Randomness factor strength in new strokes (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.BrushGpencilSettings.random_value_factor"></a>

#### bpy.types.BrushGpencilSettings.random_value_factor

Random factor to modify original value (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.BrushGpencilSettings.show_fill"></a>

#### bpy.types.BrushGpencilSettings.show_fill

Show transparent lines to use as boundary for filling (default True)

**Type:**

bool

<a id="bpy.types.BrushGpencilSettings.show_fill_boundary"></a>

#### bpy.types.BrushGpencilSettings.show_fill_boundary

Show help lines for filling to see boundaries (default True)

**Type:**

bool

<a id="bpy.types.BrushGpencilSettings.show_fill_extend"></a>

#### bpy.types.BrushGpencilSettings.show_fill_extend

Show help lines for stroke extension (default True)

**Type:**

bool

<a id="bpy.types.BrushGpencilSettings.show_lasso"></a>

#### bpy.types.BrushGpencilSettings.show_lasso

Display fill color while drawing the stroke (default True)

**Type:**

bool

<a id="bpy.types.BrushGpencilSettings.simplify_factor"></a>

#### bpy.types.BrushGpencilSettings.simplify_factor

Factor of Simplify using adaptive algorithm (in [0, 100], default 0.0)

**Type:**

float

<a id="bpy.types.BrushGpencilSettings.simplify_pixel_threshold"></a>

#### bpy.types.BrushGpencilSettings.simplify_pixel_threshold

Threshold in screen space used for the simplify algorithm. Points within this threshold are treated as if they were in a straight line. (in [0, 10], default 0.0)

**Type:**

float

<a id="bpy.types.BrushGpencilSettings.stroke_type"></a>

#### bpy.types.BrushGpencilSettings.stroke_type

Mode to use when creating strokes (default `'STROKE'`)

**Type:**

Literal[‘STROKE’, ‘FILL’, ‘BOTH’]

<a id="bpy.types.BrushGpencilSettings.use_active_layer_only"></a>

#### bpy.types.BrushGpencilSettings.use_active_layer_only

Only edit the active layer of the object (default False)

**Type:**

bool

<a id="bpy.types.BrushGpencilSettings.use_auto_remove_fill_guides"></a>

#### bpy.types.BrushGpencilSettings.use_auto_remove_fill_guides

Automatically remove fill guide strokes after fill operation (default True)

**Type:**

bool

<a id="bpy.types.BrushGpencilSettings.use_collide_strokes"></a>

#### bpy.types.BrushGpencilSettings.use_collide_strokes

Check if extend lines collide with strokes (default False)

**Type:**

bool

<a id="bpy.types.BrushGpencilSettings.use_edit_position"></a>

#### bpy.types.BrushGpencilSettings.use_edit_position

The brush affects the position of the point (default False)

**Type:**

bool

<a id="bpy.types.BrushGpencilSettings.use_edit_strength"></a>

#### bpy.types.BrushGpencilSettings.use_edit_strength

The brush affects the color strength of the point (default False)

**Type:**

bool

<a id="bpy.types.BrushGpencilSettings.use_edit_thickness"></a>

#### bpy.types.BrushGpencilSettings.use_edit_thickness

The brush affects the thickness of the point (default False)

**Type:**

bool

<a id="bpy.types.BrushGpencilSettings.use_edit_uv"></a>

#### bpy.types.BrushGpencilSettings.use_edit_uv

The brush affects the UV rotation of the point (default False)

**Type:**

bool

<a id="bpy.types.BrushGpencilSettings.use_fill_limit"></a>

#### bpy.types.BrushGpencilSettings.use_fill_limit

Fill only visible areas in viewport (default True)

**Type:**

bool

<a id="bpy.types.BrushGpencilSettings.use_jitter_pressure"></a>

#### bpy.types.BrushGpencilSettings.use_jitter_pressure

Use tablet pressure for jitter (default False)

**Type:**

bool

<a id="bpy.types.BrushGpencilSettings.use_keep_caps_eraser"></a>

#### bpy.types.BrushGpencilSettings.use_keep_caps_eraser

Keep the caps as they are and don’t flatten them when erasing (default False)

**Type:**

bool

<a id="bpy.types.BrushGpencilSettings.use_material_pin"></a>

#### bpy.types.BrushGpencilSettings.use_material_pin

Keep material assigned to brush (default False)

**Type:**

bool

<a id="bpy.types.BrushGpencilSettings.use_occlude_eraser"></a>

#### bpy.types.BrushGpencilSettings.use_occlude_eraser

Erase only strokes visible and not occluded (default False)

**Type:**

bool

<a id="bpy.types.BrushGpencilSettings.use_pressure"></a>

#### bpy.types.BrushGpencilSettings.use_pressure

Use tablet pressure (default False)

**Type:**

bool

<a id="bpy.types.BrushGpencilSettings.use_random_press_hue"></a>

#### bpy.types.BrushGpencilSettings.use_random_press_hue

Use pressure to modulate randomness (default False)

**Type:**

bool

<a id="bpy.types.BrushGpencilSettings.use_random_press_radius"></a>

#### bpy.types.BrushGpencilSettings.use_random_press_radius

Use pressure to modulate randomness (default False)

**Type:**

bool

<a id="bpy.types.BrushGpencilSettings.use_random_press_sat"></a>

#### bpy.types.BrushGpencilSettings.use_random_press_sat

Use pressure to modulate randomness (default False)

**Type:**

bool

<a id="bpy.types.BrushGpencilSettings.use_random_press_strength"></a>

#### bpy.types.BrushGpencilSettings.use_random_press_strength

Use pressure to modulate randomness (default False)

**Type:**

bool

<a id="bpy.types.BrushGpencilSettings.use_random_press_uv"></a>

#### bpy.types.BrushGpencilSettings.use_random_press_uv

Use pressure to modulate randomness (default False)

**Type:**

bool

<a id="bpy.types.BrushGpencilSettings.use_random_press_val"></a>

#### bpy.types.BrushGpencilSettings.use_random_press_val

Use pressure to modulate randomness (default False)

**Type:**

bool

<a id="bpy.types.BrushGpencilSettings.use_settings_outline"></a>

#### bpy.types.BrushGpencilSettings.use_settings_outline

Convert stroke to outline (default False)

**Type:**

bool

<a id="bpy.types.BrushGpencilSettings.use_settings_postprocess"></a>

#### bpy.types.BrushGpencilSettings.use_settings_postprocess

Additional post processing options for new strokes (default False)

**Type:**

bool

<a id="bpy.types.BrushGpencilSettings.use_settings_random"></a>

#### bpy.types.BrushGpencilSettings.use_settings_random

Random brush settings (default False)

**Type:**

bool

<a id="bpy.types.BrushGpencilSettings.use_settings_stabilizer"></a>

#### bpy.types.BrushGpencilSettings.use_settings_stabilizer

Draw lines with a delay to allow smooth strokes (press Shift key to override while drawing) (default True)

**Type:**

bool

<a id="bpy.types.BrushGpencilSettings.use_strength_pressure"></a>

#### bpy.types.BrushGpencilSettings.use_strength_pressure

Use tablet pressure for color strength (default False)

**Type:**

bool

<a id="bpy.types.BrushGpencilSettings.use_stroke_random_hue"></a>

#### bpy.types.BrushGpencilSettings.use_stroke_random_hue

Use randomness at stroke level (default False)

**Type:**

bool

<a id="bpy.types.BrushGpencilSettings.use_stroke_random_radius"></a>

#### bpy.types.BrushGpencilSettings.use_stroke_random_radius

Use randomness at stroke level (default False)

**Type:**

bool

<a id="bpy.types.BrushGpencilSettings.use_stroke_random_sat"></a>

#### bpy.types.BrushGpencilSettings.use_stroke_random_sat

Use randomness at stroke level (default False)

**Type:**

bool

<a id="bpy.types.BrushGpencilSettings.use_stroke_random_strength"></a>

#### bpy.types.BrushGpencilSettings.use_stroke_random_strength

Use randomness at stroke level (default False)

**Type:**

bool

<a id="bpy.types.BrushGpencilSettings.use_stroke_random_uv"></a>

#### bpy.types.BrushGpencilSettings.use_stroke_random_uv

Use randomness at stroke level (default False)

**Type:**

bool

<a id="bpy.types.BrushGpencilSettings.use_stroke_random_val"></a>

#### bpy.types.BrushGpencilSettings.use_stroke_random_val

Use randomness at stroke level (default False)

**Type:**

bool

<a id="bpy.types.BrushGpencilSettings.use_trim"></a>

#### bpy.types.BrushGpencilSettings.use_trim

Trim intersecting stroke ends (default False)

**Type:**

bool

<a id="bpy.types.BrushGpencilSettings.uv_random"></a>

#### bpy.types.BrushGpencilSettings.uv_random

Random factor for auto-generated UV rotation (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.BrushGpencilSettings.vertex_color_factor"></a>

#### bpy.types.BrushGpencilSettings.vertex_color_factor

Factor used to mix vertex color to get final color (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.BrushGpencilSettings.vertex_mode"></a>

#### bpy.types.BrushGpencilSettings.vertex_mode

Defines how vertex color affect to the strokes (default `'STROKE'`)

- `STROKE`
  Stroke – Painting affects only strokes, not fills.
- `FILL`
  Fill – Painting affects only fills, not strokes.
- `BOTH`
  Both – Painting affects both strokes and fills.

**Type:**

Literal[‘STROKE’, ‘FILL’, ‘BOTH’]

<a id="bpy.types.BrushGpencilSettings.bl_rna_get_subclass"></a>

#### classmethod bpy.types.BrushGpencilSettings.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.BrushGpencilSettings.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.BrushGpencilSettings.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Brush.gpencil_settings`](bpy.types.Brush.md#bpy.types.Brush.gpencil_settings "bpy.types.Brush.gpencil_settings") |  |
