<!-- source: Blender Python API reference 5.2 / bpy.types.Brush.html -->

<a id="brush-id"></a>

# Brush(ID)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")

<a id="bpy.types.Brush"></a>

### class bpy.types.Brush(ID)

Brush data-block for storing brush settings for painting and sculpting

<a id="bpy.types.Brush.area_radius_factor"></a>

#### bpy.types.Brush.area_radius_factor

Ratio between the brush radius and the radius that is going to be used to sample the area center (in [0, 2], default 0.5)

**Type:**

float

<a id="bpy.types.Brush.auto_smooth_factor"></a>

#### bpy.types.Brush.auto_smooth_factor

Amount of smoothing to automatically apply to each stroke (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.Brush.blend"></a>

#### bpy.types.Brush.blend

Brush blending mode (default `'MIX'`)

- `MIX`
  Mix – Use Mix blending mode while painting.
- `DARKEN`
  Darken – Use Darken blending mode while painting.
- `MUL`
  Multiply – Use Multiply blending mode while painting.
- `COLORBURN`
  Color Burn – Use Color Burn blending mode while painting.
- `LINEARBURN`
  Linear Burn – Use Linear Burn blending mode while painting.
- `LIGHTEN`
  Lighten – Use Lighten blending mode while painting.
- `SCREEN`
  Screen – Use Screen blending mode while painting.
- `COLORDODGE`
  Color Dodge – Use Color Dodge blending mode while painting.
- `ADD`
  Add – Use Add blending mode while painting.
- `OVERLAY`
  Overlay – Use Overlay blending mode while painting.
- `SOFTLIGHT`
  Soft Light – Use Soft Light blending mode while painting.
- `HARDLIGHT`
  Hard Light – Use Hard Light blending mode while painting.
- `VIVIDLIGHT`
  Vivid Light – Use Vivid Light blending mode while painting.
- `LINEARLIGHT`
  Linear Light – Use Linear Light blending mode while painting.
- `PINLIGHT`
  Pin Light – Use Pin Light blending mode while painting.
- `DIFFERENCE`
  Difference – Use Difference blending mode while painting.
- `EXCLUSION`
  Exclusion – Use Exclusion blending mode while painting.
- `SUB`
  Subtract – Use Subtract blending mode while painting.
- `HUE`
  Hue – Use Hue blending mode while painting.
- `SATURATION`
  Saturation – Use Saturation blending mode while painting.
- `COLOR`
  Color – Use Color blending mode while painting.
- `LUMINOSITY`
  Value – Use Value blending mode while painting.
- `ERASE_ALPHA`
  Erase Alpha – Erase alpha while painting.
- `ADD_ALPHA`
  Add Alpha – Add alpha while painting.

**Type:**

Literal[‘MIX’, ‘DARKEN’, ‘MUL’, ‘COLORBURN’, ‘LINEARBURN’, ‘LIGHTEN’, ‘SCREEN’, ‘COLORDODGE’, ‘ADD’, ‘OVERLAY’, ‘SOFTLIGHT’, ‘HARDLIGHT’, ‘VIVIDLIGHT’, ‘LINEARLIGHT’, ‘PINLIGHT’, ‘DIFFERENCE’, ‘EXCLUSION’, ‘SUB’, ‘HUE’, ‘SATURATION’, ‘COLOR’, ‘LUMINOSITY’, ‘ERASE_ALPHA’, ‘ADD_ALPHA’]

<a id="bpy.types.Brush.blur_kernel_radius"></a>

#### bpy.types.Brush.blur_kernel_radius

Radius of kernel used for soften and sharpen in pixels (in [1, 10000], default 2)

**Type:**

int

<a id="bpy.types.Brush.blur_mode"></a>

#### bpy.types.Brush.blur_mode

(default `'GAUSSIAN'`)

**Type:**

Literal[‘BOX’, ‘GAUSSIAN’]

<a id="bpy.types.Brush.boundary_deform_type"></a>

#### bpy.types.Brush.boundary_deform_type

Deformation type that is used in the brush (default `'BEND'`)

**Type:**

Literal[‘BEND’, ‘EXPAND’, ‘INFLATE’, ‘GRAB’, ‘TWIST’, ‘SMOOTH’]

<a id="bpy.types.Brush.boundary_falloff_type"></a>

#### bpy.types.Brush.boundary_falloff_type

How the brush falloff is applied across the boundary (default `'CONSTANT'`)

- `CONSTANT`
  Constant – Applies the same deformation in the entire boundary.
- `RADIUS`
  Brush Radius – Applies the deformation in a localized area limited by the brush radius.
- `LOOP`
  Loop – Applies the brush falloff in a loop pattern.
- `LOOP_INVERT`
  Loop and Invert – Applies the falloff radius in a loop pattern, inverting the displacement direction in each pattern repetition.

**Type:**

Literal[‘CONSTANT’, ‘RADIUS’, ‘LOOP’, ‘LOOP_INVERT’]

<a id="bpy.types.Brush.boundary_offset"></a>

#### bpy.types.Brush.boundary_offset

Offset of the boundary origin in relation to the brush radius (in [0, 30], default 0.0)

**Type:**

float

<a id="bpy.types.Brush.brush_capabilities"></a>

#### bpy.types.Brush.brush_capabilities

Brush’s capabilities (readonly, never None)

**Type:**

[`BrushCapabilities`](bpy.types.BrushCapabilities.md#bpy.types.BrushCapabilities "bpy.types.BrushCapabilities")

<a id="bpy.types.Brush.cloth_constraint_softbody_strength"></a>

#### bpy.types.Brush.cloth_constraint_softbody_strength

How much the cloth preserves the original shape, acting as a soft body (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.Brush.cloth_damping"></a>

#### bpy.types.Brush.cloth_damping

How much the applied forces are propagated through the cloth (in [0.01, 1], default 0.01)

**Type:**

float

<a id="bpy.types.Brush.cloth_deform_type"></a>

#### bpy.types.Brush.cloth_deform_type

Deformation type that is used in the brush (default `'DRAG'`)

**Type:**

Literal[‘DRAG’, ‘PUSH’, ‘PINCH_POINT’, ‘PINCH_PERPENDICULAR’, ‘INFLATE’, ‘GRAB’, ‘EXPAND’, ‘SNAKE_HOOK’]

<a id="bpy.types.Brush.cloth_force_falloff_type"></a>

#### bpy.types.Brush.cloth_force_falloff_type

Shape used in the brush to apply force to the cloth (default `'RADIAL'`)

**Type:**

Literal[‘RADIAL’, ‘PLANE’]

<a id="bpy.types.Brush.cloth_mass"></a>

#### bpy.types.Brush.cloth_mass

Mass of each simulation particle (in [0.01, 2], default 1.0)

**Type:**

float

<a id="bpy.types.Brush.cloth_sim_falloff"></a>

#### bpy.types.Brush.cloth_sim_falloff

Area to apply deformation falloff to the effects of the simulation (in [0, 1], default 0.75)

**Type:**

float

<a id="bpy.types.Brush.cloth_sim_limit"></a>

#### bpy.types.Brush.cloth_sim_limit

Factor added relative to the size of the radius to limit the cloth simulation effects (in [0.1, 10], default 2.5)

**Type:**

float

<a id="bpy.types.Brush.cloth_simulation_area_type"></a>

#### bpy.types.Brush.cloth_simulation_area_type

Part of the mesh that is going to be simulated when the stroke is active (default `'LOCAL'`)

- `LOCAL`
  Local – Simulates only a specific area around the brush limited by a fixed radius.
- `GLOBAL`
  Global – Simulates the entire mesh.
- `DYNAMIC`
  Dynamic – The active simulation area moves with the brush.

**Type:**

Literal[‘LOCAL’, ‘GLOBAL’, ‘DYNAMIC’]

<a id="bpy.types.Brush.color"></a>

#### bpy.types.Brush.color

(array of 3 items, in [0, inf], default (1.0, 1.0, 1.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.Brush.color_type"></a>

#### bpy.types.Brush.color_type

Use single color or gradient when painting (default `'COLOR'`)

- `COLOR`
  Color – Paint with a single color.
- `GRADIENT`
  Gradient – Paint with a gradient.

**Type:**

Literal[‘COLOR’, ‘GRADIENT’]

<a id="bpy.types.Brush.crease_pinch_factor"></a>

#### bpy.types.Brush.crease_pinch_factor

How much the crease brush pinches (in [0, 1], default 0.5)

**Type:**

float

<a id="bpy.types.Brush.cursor_color_add"></a>

#### bpy.types.Brush.cursor_color_add

Color of cursor when adding (array of 4 items, in [0, inf], default (1.0, 0.39, 0.39, 0.9))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.Brush.cursor_color_subtract"></a>

#### bpy.types.Brush.cursor_color_subtract

Color of cursor when subtracting (array of 4 items, in [0, inf], default (0.39, 0.39, 1.0, 0.9))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.Brush.cursor_overlay_alpha"></a>

#### bpy.types.Brush.cursor_overlay_alpha

(in [0, 100], default 33)

**Type:**

int

<a id="bpy.types.Brush.curve_distance_falloff"></a>

#### bpy.types.Brush.curve_distance_falloff

Editable falloff curve (readonly, never None)

**Type:**

[`CurveMapping`](bpy.types.CurveMapping.md#bpy.types.CurveMapping "bpy.types.CurveMapping")

<a id="bpy.types.Brush.curve_distance_falloff_preset"></a>

#### bpy.types.Brush.curve_distance_falloff_preset

(default `'CUSTOM'`)

**Type:**

Literal[[Brush Curve Preset Items](bpy_types_enum_items/brush_curve_preset_items.md#rna-enum-brush-curve-preset-items)]

<a id="bpy.types.Brush.curve_jitter"></a>

#### bpy.types.Brush.curve_jitter

Curve used to map pressure to brush jitter (readonly)

**Type:**

[`CurveMapping`](bpy.types.CurveMapping.md#bpy.types.CurveMapping "bpy.types.CurveMapping") | None

<a id="bpy.types.Brush.curve_random_hue"></a>

#### bpy.types.Brush.curve_random_hue

Curve used for modulating effect (readonly)

**Type:**

[`CurveMapping`](bpy.types.CurveMapping.md#bpy.types.CurveMapping "bpy.types.CurveMapping") | None

<a id="bpy.types.Brush.curve_random_saturation"></a>

#### bpy.types.Brush.curve_random_saturation

Curve used for modulating effect (readonly)

**Type:**

[`CurveMapping`](bpy.types.CurveMapping.md#bpy.types.CurveMapping "bpy.types.CurveMapping") | None

<a id="bpy.types.Brush.curve_random_value"></a>

#### bpy.types.Brush.curve_random_value

Curve used for modulating effect (readonly)

**Type:**

[`CurveMapping`](bpy.types.CurveMapping.md#bpy.types.CurveMapping "bpy.types.CurveMapping") | None

<a id="bpy.types.Brush.curve_size"></a>

#### bpy.types.Brush.curve_size

Curve used to map pressure to brush size (readonly)

**Type:**

[`CurveMapping`](bpy.types.CurveMapping.md#bpy.types.CurveMapping "bpy.types.CurveMapping") | None

<a id="bpy.types.Brush.curve_strength"></a>

#### bpy.types.Brush.curve_strength

Curve used to map pressure to brush strength (readonly)

**Type:**

[`CurveMapping`](bpy.types.CurveMapping.md#bpy.types.CurveMapping "bpy.types.CurveMapping") | None

<a id="bpy.types.Brush.curves_sculpt_brush_type"></a>

#### bpy.types.Brush.curves_sculpt_brush_type

(default `'COMB'`)

**Type:**

Literal[[Brush Curves Sculpt Brush Type Items](bpy_types_enum_items/brush_curves_sculpt_brush_type_items.md#rna-enum-brush-curves-sculpt-brush-type-items)]

<a id="bpy.types.Brush.curves_sculpt_settings"></a>

#### bpy.types.Brush.curves_sculpt_settings

(readonly)

**Type:**

[`BrushCurvesSculptSettings`](bpy.types.BrushCurvesSculptSettings.md#bpy.types.BrushCurvesSculptSettings "bpy.types.BrushCurvesSculptSettings") | None

<a id="bpy.types.Brush.dash_ratio"></a>

#### bpy.types.Brush.dash_ratio

Ratio of samples in a cycle that the brush is enabled (in [0, 1], default 1.0)

**Type:**

float

<a id="bpy.types.Brush.dash_samples"></a>

#### bpy.types.Brush.dash_samples

Length of a dash cycle measured in stroke samples (in [1, 10000], default 20)

**Type:**

int

<a id="bpy.types.Brush.deform_target"></a>

#### bpy.types.Brush.deform_target

How the deformation of the brush will affect the object (default `'GEOMETRY'`)

- `GEOMETRY`
  Geometry – Brush deformation displaces the vertices of the mesh.
- `CLOTH_SIM`
  Cloth Simulation – Brush deforms the mesh by deforming the constraints of a cloth simulation.

**Type:**

Literal[‘GEOMETRY’, ‘CLOTH_SIM’]

<a id="bpy.types.Brush.density"></a>

#### bpy.types.Brush.density

Amount of random elements that are going to be affected by the brush (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.Brush.direction"></a>

#### bpy.types.Brush.direction

(default `'ADD'`)

- `ADD`
  Add – Add effect of brush.
- `SUBTRACT`
  Subtract – Subtract effect of brush.

**Type:**

Literal[‘ADD’, ‘SUBTRACT’]

<a id="bpy.types.Brush.disconnected_distance_max"></a>

#### bpy.types.Brush.disconnected_distance_max

Maximum distance to search for disconnected loose parts in the mesh (in [0, 10], default 0.1)

**Type:**

float

<a id="bpy.types.Brush.elastic_deform_type"></a>

#### bpy.types.Brush.elastic_deform_type

Deformation type that is used in the brush (default `'GRAB'`)

**Type:**

Literal[‘GRAB’, ‘GRAB_BISCALE’, ‘GRAB_TRISCALE’, ‘SCALE’, ‘TWIST’]

<a id="bpy.types.Brush.elastic_deform_volume_preservation"></a>

#### bpy.types.Brush.elastic_deform_volume_preservation

Poisson ratio for elastic deformation. Higher values preserve volume more, but also lead to more bulging. (in [0, 0.9], default 0.0)

**Type:**

float

<a id="bpy.types.Brush.falloff_angle"></a>

#### bpy.types.Brush.falloff_angle

Paint most on faces pointing towards the view according to this angle (in [0, 1.5708], default 0.0)

**Type:**

float

<a id="bpy.types.Brush.falloff_shape"></a>

#### bpy.types.Brush.falloff_shape

Use projected or spherical falloff (default `'SPHERE'`)

- `SPHERE`
  Sphere – Apply brush influence in a Sphere, outwards from the center.
- `PROJECTED`
  Projected – Apply brush influence in a 2D circle, projected from the view.

**Type:**

Literal[‘SPHERE’, ‘PROJECTED’]

<a id="bpy.types.Brush.fill_threshold"></a>

#### bpy.types.Brush.fill_threshold

Threshold above which filling is not propagated (in [0, 100], default 0.2)

**Type:**

float

<a id="bpy.types.Brush.flow"></a>

#### bpy.types.Brush.flow

Amount of paint that is applied per stroke sample (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.Brush.gpencil_brush_type"></a>

#### bpy.types.Brush.gpencil_brush_type

(default `'DRAW'`)

**Type:**

Literal[[Brush Gpencil Types Items](bpy_types_enum_items/brush_gpencil_types_items.md#rna-enum-brush-gpencil-types-items)]

<a id="bpy.types.Brush.gpencil_sculpt_brush_type"></a>

#### bpy.types.Brush.gpencil_sculpt_brush_type

(default `'SMOOTH'`)

**Type:**

Literal[[Brush Gpencil Sculpt Types Items](bpy_types_enum_items/brush_gpencil_sculpt_types_items.md#rna-enum-brush-gpencil-sculpt-types-items)]

<a id="bpy.types.Brush.gpencil_settings"></a>

#### bpy.types.Brush.gpencil_settings

(readonly)

**Type:**

[`BrushGpencilSettings`](bpy.types.BrushGpencilSettings.md#bpy.types.BrushGpencilSettings "bpy.types.BrushGpencilSettings") | None

<a id="bpy.types.Brush.gpencil_vertex_brush_type"></a>

#### bpy.types.Brush.gpencil_vertex_brush_type

(default `'DRAW'`)

**Type:**

Literal[[Brush Gpencil Vertex Types Items](bpy_types_enum_items/brush_gpencil_vertex_types_items.md#rna-enum-brush-gpencil-vertex-types-items)]

<a id="bpy.types.Brush.gpencil_weight_brush_type"></a>

#### bpy.types.Brush.gpencil_weight_brush_type

(default `'WEIGHT'`)

**Type:**

Literal[[Brush Gpencil Weight Types Items](bpy_types_enum_items/brush_gpencil_weight_types_items.md#rna-enum-brush-gpencil-weight-types-items)]

<a id="bpy.types.Brush.grad_spacing"></a>

#### bpy.types.Brush.grad_spacing

Spacing before brush gradient goes full circle (in [1, 10000], default 0)

**Type:**

int

<a id="bpy.types.Brush.gradient"></a>

#### bpy.types.Brush.gradient

(readonly)

**Type:**

[`ColorRamp`](bpy.types.ColorRamp.md#bpy.types.ColorRamp "bpy.types.ColorRamp") | None

<a id="bpy.types.Brush.gradient_fill_mode"></a>

#### bpy.types.Brush.gradient_fill_mode

(default `'LINEAR'`)

**Type:**

Literal[‘LINEAR’, ‘RADIAL’]

<a id="bpy.types.Brush.gradient_stroke_mode"></a>

#### bpy.types.Brush.gradient_stroke_mode

(default `'PRESSURE'`)

**Type:**

Literal[‘PRESSURE’, ‘SPACING_REPEAT’, ‘SPACING_CLAMP’]

<a id="bpy.types.Brush.hardness"></a>

#### bpy.types.Brush.hardness

How close the brush falloff starts from the edge of the brush (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.Brush.has_unsaved_changes"></a>

#### bpy.types.Brush.has_unsaved_changes

Indicates that there are any user visible changes since the brush has been imported or read from the file (default False, readonly)

**Type:**

bool

<a id="bpy.types.Brush.height"></a>

#### bpy.types.Brush.height

Affectable height of brush (i.e. the layer height for the layer tool) (in [0, 1], default 0.5)

**Type:**

float

<a id="bpy.types.Brush.hue_jitter"></a>

#### bpy.types.Brush.hue_jitter

Color jitter effect on hue (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.Brush.image_brush_type"></a>

#### bpy.types.Brush.image_brush_type

(default `'DRAW'`)

**Type:**

Literal[[Brush Image Brush Type Items](bpy_types_enum_items/brush_image_brush_type_items.md#rna-enum-brush-image-brush-type-items)]

<a id="bpy.types.Brush.image_paint_capabilities"></a>

#### bpy.types.Brush.image_paint_capabilities

(readonly, never None)

**Type:**

[`BrushCapabilitiesImagePaint`](bpy.types.BrushCapabilitiesImagePaint.md#bpy.types.BrushCapabilitiesImagePaint "bpy.types.BrushCapabilitiesImagePaint")

<a id="bpy.types.Brush.input_samples"></a>

#### bpy.types.Brush.input_samples

Number of input samples to average together to smooth the brush stroke (in [1, 64], default 1)

**Type:**

int

<a id="bpy.types.Brush.invert_density_pressure"></a>

#### bpy.types.Brush.invert_density_pressure

Invert the modulation of pressure in density (default False)

**Type:**

bool

<a id="bpy.types.Brush.invert_flow_pressure"></a>

#### bpy.types.Brush.invert_flow_pressure

Invert the modulation of pressure in flow (default False)

**Type:**

bool

<a id="bpy.types.Brush.invert_hardness_pressure"></a>

#### bpy.types.Brush.invert_hardness_pressure

Invert the modulation of pressure in hardness (default False)

**Type:**

bool

<a id="bpy.types.Brush.invert_to_scrape_fill"></a>

#### bpy.types.Brush.invert_to_scrape_fill

Use Scrape or Fill brush when inverting this brush instead of inverting its displacement direction (default False)

**Type:**

bool

<a id="bpy.types.Brush.invert_wet_mix_pressure"></a>

#### bpy.types.Brush.invert_wet_mix_pressure

Invert the modulation of pressure in wet mix (default False)

**Type:**

bool

<a id="bpy.types.Brush.invert_wet_persistence_pressure"></a>

#### bpy.types.Brush.invert_wet_persistence_pressure

Invert the modulation of pressure in wet persistence (default False)

**Type:**

bool

<a id="bpy.types.Brush.jitter"></a>

#### bpy.types.Brush.jitter

Jitter the position of the brush while painting (in [0, 1000], default 0.0)

**Type:**

float

<a id="bpy.types.Brush.jitter_absolute"></a>

#### bpy.types.Brush.jitter_absolute

Jitter the position of the brush in pixels while painting (in [0, 1000000], default 0)

**Type:**

int

<a id="bpy.types.Brush.jitter_unit"></a>

#### bpy.types.Brush.jitter_unit

Jitter in screen space or relative to brush size (default `'VIEW'`)

- `VIEW`
  View – Jittering happens in screen space, in pixels.
- `BRUSH`
  Brush – Jittering happens relative to the brush size.

**Type:**

Literal[‘VIEW’, ‘BRUSH’]

<a id="bpy.types.Brush.mask_overlay_alpha"></a>

#### bpy.types.Brush.mask_overlay_alpha

(in [0, 100], default 33)

**Type:**

int

<a id="bpy.types.Brush.mask_stencil_dimension"></a>

#### bpy.types.Brush.mask_stencil_dimension

Dimensions of mask stencil in viewport (array of 2 items, in [-inf, inf], default (256.0, 256.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.Brush.mask_stencil_pos"></a>

#### bpy.types.Brush.mask_stencil_pos

Position of mask stencil in viewport (array of 2 items, in [-inf, inf], default (256.0, 256.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.Brush.mask_texture"></a>

#### bpy.types.Brush.mask_texture

**Type:**

[`Texture`](bpy.types.Texture.md#bpy.types.Texture "bpy.types.Texture") | None

<a id="bpy.types.Brush.mask_texture_slot"></a>

#### bpy.types.Brush.mask_texture_slot

(readonly)

**Type:**

[`BrushTextureSlot`](bpy.types.BrushTextureSlot.md#bpy.types.BrushTextureSlot "bpy.types.BrushTextureSlot") | None

<a id="bpy.types.Brush.mask_tool"></a>

#### bpy.types.Brush.mask_tool

(default `'DRAW'`)

**Type:**

Literal[‘DRAW’, ‘SMOOTH’]

<a id="bpy.types.Brush.mesh_automasking_settings"></a>

#### bpy.types.Brush.mesh_automasking_settings

(readonly)

**Type:**

[`MeshAutomaskingSettings`](bpy.types.MeshAutomaskingSettings.md#bpy.types.MeshAutomaskingSettings "bpy.types.MeshAutomaskingSettings") | None

<a id="bpy.types.Brush.minimum_distance"></a>

#### bpy.types.Brush.minimum_distance

Minimum distance to other scene objects after projecting onto them (in [0, 10], default 0.0)

**Type:**

float

<a id="bpy.types.Brush.multiplane_scrape_angle"></a>

#### bpy.types.Brush.multiplane_scrape_angle

Angle between the planes of the crease (in [0, 160], default 0.0)

**Type:**

float

<a id="bpy.types.Brush.normal_radius_factor"></a>

#### bpy.types.Brush.normal_radius_factor

Ratio between the brush radius and the radius that is going to be used to sample the normal (in [0, 2], default 0.5)

**Type:**

float

<a id="bpy.types.Brush.normal_weight"></a>

#### bpy.types.Brush.normal_weight

How much grab will pull vertices out of surface during a grab (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.Brush.paint_curve"></a>

#### bpy.types.Brush.paint_curve

Active paint curve

**Type:**

[`PaintCurve`](bpy.types.PaintCurve.md#bpy.types.PaintCurve "bpy.types.PaintCurve") | None

<a id="bpy.types.Brush.plane_depth"></a>

#### bpy.types.Brush.plane_depth

The maximum distance below the plane for affected vertices. Increasing the depth affects vertices farther below the plane. (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.Brush.plane_height"></a>

#### bpy.types.Brush.plane_height

The maximum distance above the plane for affected vertices. Increasing the height affects vertices farther above the plane. (in [0, 1], default 1.0)

**Type:**

float

<a id="bpy.types.Brush.plane_inversion_mode"></a>

#### bpy.types.Brush.plane_inversion_mode

Inversion Mode (default `'INVERT_DISPLACEMENT'`)

- `INVERT_DISPLACEMENT`
  Invert Displacement – Displace the vertices away from the plane..
- `SWAP_DEPTH_AND_HEIGHT`
  Swap Height and Depth – Swap the roles of Height and Depth..

**Type:**

Literal[‘INVERT_DISPLACEMENT’, ‘SWAP_DEPTH_AND_HEIGHT’]

<a id="bpy.types.Brush.plane_offset"></a>

#### bpy.types.Brush.plane_offset

Adjust plane on which the brush acts towards or away from the object surface (in [-2, 2], default 0.0)

**Type:**

float

<a id="bpy.types.Brush.plane_trim"></a>

#### bpy.types.Brush.plane_trim

If a vertex is further away from offset plane than this, then it is not affected (in [0, 1], default 0.5)

**Type:**

float

<a id="bpy.types.Brush.pose_deform_type"></a>

#### bpy.types.Brush.pose_deform_type

Deformation type that is used in the brush (default `'ROTATE_TWIST'`)

**Type:**

Literal[‘ROTATE_TWIST’, ‘SCALE_TRANSLATE’, ‘SQUASH_STRETCH’]

<a id="bpy.types.Brush.pose_ik_segments"></a>

#### bpy.types.Brush.pose_ik_segments

Number of segments of the inverse kinematics chain that will deform the mesh (in [1, 20], default 1)

**Type:**

int

<a id="bpy.types.Brush.pose_offset"></a>

#### bpy.types.Brush.pose_offset

Offset of the pose origin in relation to the brush radius (in [0, 2], default 0.0)

**Type:**

float

<a id="bpy.types.Brush.pose_origin_type"></a>

#### bpy.types.Brush.pose_origin_type

Method to set the rotation origins for the segments of the brush (default `'TOPOLOGY'`)

- `TOPOLOGY`
  Topology – Sets the rotation origin automatically using the topology and shape of the mesh as a guide.
- `FACE_SETS`
  Face Sets – Creates a pose segment per face set, starting from the active face set.
- `FACE_SETS_FK`
  Face Sets FK – Simulates an FK deformation using the face set under the cursor as control.

**Type:**

Literal[‘TOPOLOGY’, ‘FACE_SETS’, ‘FACE_SETS_FK’]

<a id="bpy.types.Brush.pose_smooth_iterations"></a>

#### bpy.types.Brush.pose_smooth_iterations

Smooth iterations applied after calculating the pose factor of each vertex (in [0, 100], default 4)

**Type:**

int

<a id="bpy.types.Brush.project_ray_direction_type"></a>

#### bpy.types.Brush.project_ray_direction_type

Ray Direction (default `'VIEW_NORMAL'`)

- `VIEW_NORMAL`
  View Normal – Project the vertices along the view normal..
- `PLANE_NORMAL`
  Plane Normal – Project the vertices along the plane normal..

**Type:**

Literal[‘VIEW_NORMAL’, ‘PLANE_NORMAL’]

<a id="bpy.types.Brush.rake_factor"></a>

#### bpy.types.Brush.rake_factor

How much grab will follow cursor rotation (in [0, 10], default 0.0)

**Type:**

float

<a id="bpy.types.Brush.rate"></a>

#### bpy.types.Brush.rate

Interval between paints for Airbrush (in [0.0001, 10000], default 0.1)

**Type:**

float

<a id="bpy.types.Brush.saturation_jitter"></a>

#### bpy.types.Brush.saturation_jitter

Color jitter effect on saturation (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.Brush.sculpt_brush_type"></a>

#### bpy.types.Brush.sculpt_brush_type

(default `'DRAW'`)

**Type:**

Literal[[Brush Sculpt Brush Type Items](bpy_types_enum_items/brush_sculpt_brush_type_items.md#rna-enum-brush-sculpt-brush-type-items)]

<a id="bpy.types.Brush.sculpt_capabilities"></a>

#### bpy.types.Brush.sculpt_capabilities

(readonly, never None)

**Type:**

[`BrushCapabilitiesSculpt`](bpy.types.BrushCapabilitiesSculpt.md#bpy.types.BrushCapabilitiesSculpt "bpy.types.BrushCapabilitiesSculpt")

<a id="bpy.types.Brush.sculpt_plane"></a>

#### bpy.types.Brush.sculpt_plane

(default `'AREA'`)

**Type:**

Literal[‘AREA’, ‘VIEW’, ‘X’, ‘Y’, ‘Z’]

<a id="bpy.types.Brush.secondary_color"></a>

#### bpy.types.Brush.secondary_color

(array of 3 items, in [0, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.Brush.sharp_threshold"></a>

#### bpy.types.Brush.sharp_threshold

Threshold below which, no sharpening is done (in [0, 100], default 0.0)

**Type:**

float

<a id="bpy.types.Brush.show_multiplane_scrape_planes_preview"></a>

#### bpy.types.Brush.show_multiplane_scrape_planes_preview

Preview the scrape planes in the cursor during the stroke (default False)

**Type:**

bool

<a id="bpy.types.Brush.size"></a>

#### bpy.types.Brush.size

Diameter of the brush in pixels (in [1, 10000], default 70)

**Type:**

int

<a id="bpy.types.Brush.slide_deform_type"></a>

#### bpy.types.Brush.slide_deform_type

Deformation type that is used in the brush (default `'DRAG'`)

**Type:**

Literal[‘DRAG’, ‘PINCH’, ‘EXPAND’]

<a id="bpy.types.Brush.smear_deform_type"></a>

#### bpy.types.Brush.smear_deform_type

Deformation type that is used in the brush (default `'DRAG'`)

**Type:**

Literal[‘DRAG’, ‘PINCH’, ‘EXPAND’]

<a id="bpy.types.Brush.smooth_deform_type"></a>

#### bpy.types.Brush.smooth_deform_type

Deformation type that is used in the brush (default `'LAPLACIAN'`)

- `LAPLACIAN`
  Laplacian – Smooths the surface and the volume.
- `SURFACE`
  Surface – Smooths the surface of the mesh, preserving the volume.

**Type:**

Literal[‘LAPLACIAN’, ‘SURFACE’]

<a id="bpy.types.Brush.smooth_stroke_factor"></a>

#### bpy.types.Brush.smooth_stroke_factor

Higher values give a smoother stroke (in [0.5, 0.99], default 0.9)

**Type:**

float

<a id="bpy.types.Brush.smooth_stroke_radius"></a>

#### bpy.types.Brush.smooth_stroke_radius

Minimum distance from last point before stroke continues (in [10, 200], default 75)

**Type:**

int

<a id="bpy.types.Brush.snake_hook_deform_type"></a>

#### bpy.types.Brush.snake_hook_deform_type

Deformation type that is used in the brush (default `'FALLOFF'`)

- `FALLOFF`
  Radius Falloff – Applies the brush falloff in the tip of the brush.
- `ELASTIC`
  Elastic – Modifies the entire mesh using elastic deform.

**Type:**

Literal[‘FALLOFF’, ‘ELASTIC’]

<a id="bpy.types.Brush.spacing"></a>

#### bpy.types.Brush.spacing

Spacing between brush daubs as a percentage of brush diameter (in [1, 1000], default 10)

**Type:**

int

<a id="bpy.types.Brush.stabilize_normal"></a>

#### bpy.types.Brush.stabilize_normal

How stable the plane normal is over the course of the stroke. A value of 0 corresponds to using the current normal, and a value of 1 corresponds to using the initial normal. (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.Brush.stabilize_plane"></a>

#### bpy.types.Brush.stabilize_plane

How stable the plane center is over the course of the stroke. A value of 0 corresponds to using the current center, and a value of 1 corresponds to using the initial center. (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.Brush.stencil_dimension"></a>

#### bpy.types.Brush.stencil_dimension

Dimensions of stencil in viewport (array of 2 items, in [-inf, inf], default (256.0, 256.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.Brush.stencil_pos"></a>

#### bpy.types.Brush.stencil_pos

Position of stencil in viewport (array of 2 items, in [-inf, inf], default (256.0, 256.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.Brush.strength"></a>

#### bpy.types.Brush.strength

How powerful the effect of the brush is when applied (in [0, 10], default 1.0)

**Type:**

float

<a id="bpy.types.Brush.stroke_method"></a>

#### bpy.types.Brush.stroke_method

(default `'DOTS'`)

- `DOTS`
  Dots – Apply paint on each mouse move step.
- `DRAG_DOT`
  Drag Dot – Allows a single dot to be carefully positioned.
- `SPACE`
  Space – Limit brush application to the distance specified by spacing.
- `AIRBRUSH`
  Airbrush – Keep applying paint effect while holding mouse (spray).
- `ANCHORED`
  Anchored – Keep the brush anchored to the initial location.
- `LINE`
  Line – Draw a line with dabs separated according to spacing.
- `CURVE`
  Curve – Define the stroke curve with a Bézier curve (dabs are separated according to spacing).

**Type:**

Literal[‘DOTS’, ‘DRAG_DOT’, ‘SPACE’, ‘AIRBRUSH’, ‘ANCHORED’, ‘LINE’, ‘CURVE’]

<a id="bpy.types.Brush.surface_smooth_current_vertex"></a>

#### bpy.types.Brush.surface_smooth_current_vertex

How much the position of each individual vertex influences the final result (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.Brush.surface_smooth_iterations"></a>

#### bpy.types.Brush.surface_smooth_iterations

Number of smoothing iterations per brush step (in [1, 10], default 0)

**Type:**

int

<a id="bpy.types.Brush.surface_smooth_shape_preservation"></a>

#### bpy.types.Brush.surface_smooth_shape_preservation

How much of the original shape is preserved when smoothing (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.Brush.texture"></a>

#### bpy.types.Brush.texture

**Type:**

[`Texture`](bpy.types.Texture.md#bpy.types.Texture "bpy.types.Texture") | None

<a id="bpy.types.Brush.texture_overlay_alpha"></a>

#### bpy.types.Brush.texture_overlay_alpha

(in [0, 100], default 33)

**Type:**

int

<a id="bpy.types.Brush.texture_sample_bias"></a>

#### bpy.types.Brush.texture_sample_bias

Value added to texture samples (in [-1, 1], default 0.0)

**Type:**

float

<a id="bpy.types.Brush.texture_slot"></a>

#### bpy.types.Brush.texture_slot

(readonly)

**Type:**

[`BrushTextureSlot`](bpy.types.BrushTextureSlot.md#bpy.types.BrushTextureSlot "bpy.types.BrushTextureSlot") | None

<a id="bpy.types.Brush.tilt_strength_factor"></a>

#### bpy.types.Brush.tilt_strength_factor

How much the tilt of the pen will affect the brush. Negative values indicate inverting the tilt directions. (in [-1, 1], default 0.0)

**Type:**

float

<a id="bpy.types.Brush.tip_roundness"></a>

#### bpy.types.Brush.tip_roundness

Roundness of the brush tip (in [0, 1], default 1.0)

**Type:**

float

<a id="bpy.types.Brush.tip_scale_x"></a>

#### bpy.types.Brush.tip_scale_x

Scale of the brush tip in the X axis (in [0.0001, 1], default 1.0)

**Type:**

float

<a id="bpy.types.Brush.topology_rake_factor"></a>

#### bpy.types.Brush.topology_rake_factor

Automatically align edges to the brush direction to generate cleaner topology and define sharp features. Best used on low-poly meshes as it has a performance impact. (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.Brush.unprojected_size"></a>

#### bpy.types.Brush.unprojected_size

Diameter of brush in Blender units (in [0.001, inf], default 0.1)

**Type:**

float

<a id="bpy.types.Brush.use_accumulate"></a>

#### bpy.types.Brush.use_accumulate

Accumulate stroke daubs on top of each other (default False)

**Type:**

bool

<a id="bpy.types.Brush.use_adaptive_space"></a>

#### bpy.types.Brush.use_adaptive_space

Space daubs according to surface orientation instead of screen space (default False)

**Type:**

bool

<a id="bpy.types.Brush.use_alpha"></a>

#### bpy.types.Brush.use_alpha

When this is disabled, lock alpha while painting (default True)

**Type:**

bool

<a id="bpy.types.Brush.use_bidirectional"></a>

#### bpy.types.Brush.use_bidirectional

Project vertices both along the projection direction and its inverse, choosing the closest intersection. (default False)

**Type:**

bool

<a id="bpy.types.Brush.use_cloth_collision"></a>

#### bpy.types.Brush.use_cloth_collision

Collide with objects during the simulation (default False)

**Type:**

bool

<a id="bpy.types.Brush.use_cloth_pin_simulation_boundary"></a>

#### bpy.types.Brush.use_cloth_pin_simulation_boundary

Lock the position of the vertices in the simulation falloff area to avoid artifacts and create a softer transition with unaffected areas (default False)

**Type:**

bool

<a id="bpy.types.Brush.use_color_as_displacement"></a>

#### bpy.types.Brush.use_color_as_displacement

Handle each pixel color as individual vector for displacement (area plane mapping only) (default False)

**Type:**

bool

<a id="bpy.types.Brush.use_color_jitter"></a>

#### bpy.types.Brush.use_color_jitter

Jitter brush color (default False)

**Type:**

bool

<a id="bpy.types.Brush.use_connected_only"></a>

#### bpy.types.Brush.use_connected_only

Affect only topologically connected elements (default False)

**Type:**

bool

<a id="bpy.types.Brush.use_cursor_overlay"></a>

#### bpy.types.Brush.use_cursor_overlay

Show cursor in viewport (default False)

**Type:**

bool

<a id="bpy.types.Brush.use_cursor_overlay_override"></a>

#### bpy.types.Brush.use_cursor_overlay_override

Don’t show overlay during a stroke (default False)

**Type:**

bool

<a id="bpy.types.Brush.use_density_pressure"></a>

#### bpy.types.Brush.use_density_pressure

Use pressure to modulate density (default False)

**Type:**

bool

<a id="bpy.types.Brush.use_edge_to_edge"></a>

#### bpy.types.Brush.use_edge_to_edge

Drag anchor brush from edge-to-edge (default False)

**Type:**

bool

<a id="bpy.types.Brush.use_flow_pressure"></a>

#### bpy.types.Brush.use_flow_pressure

Use pressure to modulate flow (default False)

**Type:**

bool

<a id="bpy.types.Brush.use_frontface"></a>

#### bpy.types.Brush.use_frontface

Brush only affects vertices that face the viewer (default False)

**Type:**

bool

<a id="bpy.types.Brush.use_frontface_falloff"></a>

#### bpy.types.Brush.use_frontface_falloff

Blend brush influence by how much they face the front (default False)

**Type:**

bool

<a id="bpy.types.Brush.use_grab_active_vertex"></a>

#### bpy.types.Brush.use_grab_active_vertex

Apply the maximum grab strength to the active vertex instead of the cursor location (default False)

**Type:**

bool

<a id="bpy.types.Brush.use_grab_silhouette"></a>

#### bpy.types.Brush.use_grab_silhouette

Grabs trying to automask the silhouette of the object (default False)

**Type:**

bool

<a id="bpy.types.Brush.use_hardness_pressure"></a>

#### bpy.types.Brush.use_hardness_pressure

Use pressure to modulate hardness (default False)

**Type:**

bool

<a id="bpy.types.Brush.use_inverse_smooth_pressure"></a>

#### bpy.types.Brush.use_inverse_smooth_pressure

Lighter pressure causes more smoothing to be applied (default False)

**Type:**

bool

<a id="bpy.types.Brush.use_locked_size"></a>

#### bpy.types.Brush.use_locked_size

Measure brush size relative to the view or the scene (default `'VIEW'`)

- `VIEW`
  View – Measure brush size relative to the view.
- `SCENE`
  Scene – Measure brush size relative to the scene.

**Type:**

Literal[‘VIEW’, ‘SCENE’]

<a id="bpy.types.Brush.use_multiplane_scrape_dynamic"></a>

#### bpy.types.Brush.use_multiplane_scrape_dynamic

The angle between the planes changes during the stroke to fit the surface under the cursor (default False)

**Type:**

bool

<a id="bpy.types.Brush.use_offset_pressure"></a>

#### bpy.types.Brush.use_offset_pressure

Enable tablet pressure sensitivity for offset (default False)

**Type:**

bool

<a id="bpy.types.Brush.use_original_normal"></a>

#### bpy.types.Brush.use_original_normal

When locked keep using normal of surface where stroke was initiated (default False)

**Type:**

bool

<a id="bpy.types.Brush.use_original_plane"></a>

#### bpy.types.Brush.use_original_plane

When locked keep using the plane origin of surface where stroke was initiated (default False)

**Type:**

bool

<a id="bpy.types.Brush.use_paint_antialiasing"></a>

#### bpy.types.Brush.use_paint_antialiasing

Smooths the edges of the strokes (default True)

**Type:**

bool

<a id="bpy.types.Brush.use_paint_grease_pencil"></a>

#### bpy.types.Brush.use_paint_grease_pencil

Use this brush in Grease Pencil drawing mode (default False)

**Type:**

bool

<a id="bpy.types.Brush.use_paint_image"></a>

#### bpy.types.Brush.use_paint_image

Use this brush in texture paint mode (default True)

**Type:**

bool

<a id="bpy.types.Brush.use_paint_sculpt"></a>

#### bpy.types.Brush.use_paint_sculpt

Use this brush in sculpt mode (default True)

**Type:**

bool

<a id="bpy.types.Brush.use_paint_sculpt_curves"></a>

#### bpy.types.Brush.use_paint_sculpt_curves

Use this brush in sculpt curves mode (default False)

**Type:**

bool

<a id="bpy.types.Brush.use_paint_uv_sculpt"></a>

#### bpy.types.Brush.use_paint_uv_sculpt

Use this brush in UV sculpt mode (default False)

**Type:**

bool

<a id="bpy.types.Brush.use_paint_vertex"></a>

#### bpy.types.Brush.use_paint_vertex

Use this brush in vertex paint mode (default True)

**Type:**

bool

<a id="bpy.types.Brush.use_paint_weight"></a>

#### bpy.types.Brush.use_paint_weight

Use this brush in weight paint mode (default True)

**Type:**

bool

<a id="bpy.types.Brush.use_persistent"></a>

#### bpy.types.Brush.use_persistent

Sculpt on a persistent layer of the mesh (default False)

**Type:**

bool

<a id="bpy.types.Brush.use_plane_trim"></a>

#### bpy.types.Brush.use_plane_trim

Limit the distance from the offset plane that a vertex can be affected (default False)

**Type:**

bool

<a id="bpy.types.Brush.use_pose_ik_anchored"></a>

#### bpy.types.Brush.use_pose_ik_anchored

Keep the position of the last segment in the IK chain fixed (default False)

**Type:**

bool

<a id="bpy.types.Brush.use_pose_lock_rotation"></a>

#### bpy.types.Brush.use_pose_lock_rotation

Do not rotate the segment when using the scale deform mode (default False)

**Type:**

bool

<a id="bpy.types.Brush.use_pressure_area_radius"></a>

#### bpy.types.Brush.use_pressure_area_radius

Enable tablet pressure sensitivity for area radius (default False)

**Type:**

bool

<a id="bpy.types.Brush.use_pressure_jitter"></a>

#### bpy.types.Brush.use_pressure_jitter

Enable tablet pressure sensitivity for jitter (default False)

**Type:**

bool

<a id="bpy.types.Brush.use_pressure_masking"></a>

#### bpy.types.Brush.use_pressure_masking

Pen pressure makes texture influence smaller (default `'NONE'`)

**Type:**

Literal[‘NONE’, ‘RAMP’, ‘CUTOFF’]

<a id="bpy.types.Brush.use_pressure_size"></a>

#### bpy.types.Brush.use_pressure_size

Enable tablet pressure sensitivity for size (default False)

**Type:**

bool

<a id="bpy.types.Brush.use_pressure_spacing"></a>

#### bpy.types.Brush.use_pressure_spacing

Enable tablet pressure sensitivity for spacing (default False)

**Type:**

bool

<a id="bpy.types.Brush.use_pressure_strength"></a>

#### bpy.types.Brush.use_pressure_strength

Enable tablet pressure sensitivity for strength (default True)

**Type:**

bool

<a id="bpy.types.Brush.use_primary_overlay"></a>

#### bpy.types.Brush.use_primary_overlay

Show texture in viewport (default False)

**Type:**

bool

<a id="bpy.types.Brush.use_primary_overlay_override"></a>

#### bpy.types.Brush.use_primary_overlay_override

Don’t show overlay during a stroke (default False)

**Type:**

bool

<a id="bpy.types.Brush.use_random_press_hue"></a>

#### bpy.types.Brush.use_random_press_hue

Use pressure to modulate randomness (default False)

**Type:**

bool

<a id="bpy.types.Brush.use_random_press_sat"></a>

#### bpy.types.Brush.use_random_press_sat

Use pressure to modulate randomness (default False)

**Type:**

bool

<a id="bpy.types.Brush.use_random_press_val"></a>

#### bpy.types.Brush.use_random_press_val

Use pressure to modulate randomness (default False)

**Type:**

bool

<a id="bpy.types.Brush.use_scene_spacing"></a>

#### bpy.types.Brush.use_scene_spacing

Calculate the brush spacing using view or scene distance (default `'VIEW'`)

- `VIEW`
  View – Calculate brush spacing relative to the view.
- `SCENE`
  Scene – Calculate brush spacing relative to the scene using the stroke location.

**Type:**

Literal[‘VIEW’, ‘SCENE’]

<a id="bpy.types.Brush.use_secondary_overlay"></a>

#### bpy.types.Brush.use_secondary_overlay

Show texture in viewport (default False)

**Type:**

bool

<a id="bpy.types.Brush.use_secondary_overlay_override"></a>

#### bpy.types.Brush.use_secondary_overlay_override

Don’t show overlay during a stroke (default False)

**Type:**

bool

<a id="bpy.types.Brush.use_smooth_stroke"></a>

#### bpy.types.Brush.use_smooth_stroke

Brush lags behind mouse and follows a smoother path (default False)

**Type:**

bool

<a id="bpy.types.Brush.use_space_attenuation"></a>

#### bpy.types.Brush.use_space_attenuation

Automatically adjust strength to give consistent results for different spacings (default True)

**Type:**

bool

<a id="bpy.types.Brush.use_stroke_random_hue"></a>

#### bpy.types.Brush.use_stroke_random_hue

Use randomness at stroke level (default False)

**Type:**

bool

<a id="bpy.types.Brush.use_stroke_random_sat"></a>

#### bpy.types.Brush.use_stroke_random_sat

Use randomness at stroke level (default False)

**Type:**

bool

<a id="bpy.types.Brush.use_stroke_random_val"></a>

#### bpy.types.Brush.use_stroke_random_val

Use randomness at stroke level (default False)

**Type:**

bool

<a id="bpy.types.Brush.use_vertex_grease_pencil"></a>

#### bpy.types.Brush.use_vertex_grease_pencil

Use this brush in Grease Pencil vertex color mode (default False)

**Type:**

bool

<a id="bpy.types.Brush.use_wet_mix_pressure"></a>

#### bpy.types.Brush.use_wet_mix_pressure

Use pressure to modulate wet mix (default False)

**Type:**

bool

<a id="bpy.types.Brush.use_wet_persistence_pressure"></a>

#### bpy.types.Brush.use_wet_persistence_pressure

Use pressure to modulate wet persistence (default False)

**Type:**

bool

<a id="bpy.types.Brush.value_jitter"></a>

#### bpy.types.Brush.value_jitter

Color jitter effect on value (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.Brush.vertex_brush_type"></a>

#### bpy.types.Brush.vertex_brush_type

(default `'DRAW'`)

**Type:**

Literal[[Brush Vertex Brush Type Items](bpy_types_enum_items/brush_vertex_brush_type_items.md#rna-enum-brush-vertex-brush-type-items)]

<a id="bpy.types.Brush.vertex_paint_capabilities"></a>

#### bpy.types.Brush.vertex_paint_capabilities

(readonly, never None)

**Type:**

[`BrushCapabilitiesVertexPaint`](bpy.types.BrushCapabilitiesVertexPaint.md#bpy.types.BrushCapabilitiesVertexPaint "bpy.types.BrushCapabilitiesVertexPaint")

<a id="bpy.types.Brush.weight"></a>

#### bpy.types.Brush.weight

Vertex weight when brush is applied (in [0, 1], default 1.0)

**Type:**

float

<a id="bpy.types.Brush.weight_brush_type"></a>

#### bpy.types.Brush.weight_brush_type

(default `'DRAW'`)

**Type:**

Literal[[Brush Weight Brush Type Items](bpy_types_enum_items/brush_weight_brush_type_items.md#rna-enum-brush-weight-brush-type-items)]

<a id="bpy.types.Brush.weight_paint_capabilities"></a>

#### bpy.types.Brush.weight_paint_capabilities

(readonly, never None)

**Type:**

[`BrushCapabilitiesWeightPaint`](bpy.types.BrushCapabilitiesWeightPaint.md#bpy.types.BrushCapabilitiesWeightPaint "bpy.types.BrushCapabilitiesWeightPaint")

<a id="bpy.types.Brush.wet_mix"></a>

#### bpy.types.Brush.wet_mix

Amount of paint that is picked from the surface into the brush color (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.Brush.wet_paint_radius_factor"></a>

#### bpy.types.Brush.wet_paint_radius_factor

Ratio between the brush radius and the radius that is going to be used to sample the color to blend in wet paint (in [0, 2], default 0.5)

**Type:**

float

<a id="bpy.types.Brush.wet_persistence"></a>

#### bpy.types.Brush.wet_persistence

Amount of wet paint that stays in the brush after applying paint to the surface (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.Brush.bl_rna_get_subclass"></a>

#### classmethod bpy.types.Brush.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.Brush.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.Brush.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, ID.name, ID.name_full, ID.id_type, ID.session_uid, ID.is_evaluated, ID.original, ID.users, ID.use_fake_user, ID.use_extra_user, ID.is_embedded_data, ID.is_linked_packed, ID.is_missing, ID.is_runtime_data, ID.is_editable, ID.tag, ID.is_library_indirect, ID.library, ID.library_weak_reference, ID.asset_data, ID.override_library, ID.preview

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, ID.bl_system_properties_get, ID.rename, ID.evaluated_get, ID.copy, ID.asset_mark, ID.asset_clear, ID.asset_generate_preview, ID.override_create, ID.override_hierarchy_create, ID.user_clear, ID.user_remap, ID.make_local, ID.user_of_id, ID.animation_data_create, ID.animation_data_clear, ID.update_tag, ID.preview_ensure, ID.bl_rna_get_subclass, ID.bl_rna_get_subclass_py

<a id="references"></a>

## References

|  |  |
| --- | --- |
| - `bpy.context.brush` - [`BlendData.brushes`](bpy.types.BlendData.md#bpy.types.BlendData.brushes "bpy.types.BlendData.brushes") - [`BlendDataBrushes.create_gpencil_data`](bpy.types.BlendDataBrushes.md#bpy.types.BlendDataBrushes.create_gpencil_data "bpy.types.BlendDataBrushes.create_gpencil_data") | - [`BlendDataBrushes.new`](bpy.types.BlendDataBrushes.md#bpy.types.BlendDataBrushes.new "bpy.types.BlendDataBrushes.new") - [`BlendDataBrushes.remove`](bpy.types.BlendDataBrushes.md#bpy.types.BlendDataBrushes.remove "bpy.types.BlendDataBrushes.remove") - [`Paint.brush`](bpy.types.Paint.md#bpy.types.Paint.brush "bpy.types.Paint.brush") |
