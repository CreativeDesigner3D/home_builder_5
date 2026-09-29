<!-- source: Blender Python API reference 5.2 / bpy.types.GreasePencilBuildModifier.html -->

<a id="greasepencilbuildmodifier-modifier"></a>

# GreasePencilBuildModifier(Modifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Modifier`](bpy.types.Modifier.md#bpy.types.Modifier "bpy.types.Modifier")

<a id="bpy.types.GreasePencilBuildModifier"></a>

### class bpy.types.GreasePencilBuildModifier(Modifier)

Animate strokes appearing and disappearing

<a id="bpy.types.GreasePencilBuildModifier.concurrent_time_alignment"></a>

#### bpy.types.GreasePencilBuildModifier.concurrent_time_alignment

How should strokes start to appear/disappear (default `'START'`)

- `START`
  Align Start – All strokes start at same time (i.e. short strokes finish earlier).
- `END`
  Align End – All strokes end at same time (i.e. short strokes start later).

**Type:**

Literal[‘START’, ‘END’]

<a id="bpy.types.GreasePencilBuildModifier.fade_factor"></a>

#### bpy.types.GreasePencilBuildModifier.fade_factor

Defines how much of the stroke is fading in/out (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.GreasePencilBuildModifier.fade_opacity_strength"></a>

#### bpy.types.GreasePencilBuildModifier.fade_opacity_strength

How much strength fading applies on top of stroke opacity (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.GreasePencilBuildModifier.fade_thickness_strength"></a>

#### bpy.types.GreasePencilBuildModifier.fade_thickness_strength

How much strength fading applies on top of stroke thickness (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.GreasePencilBuildModifier.frame_end"></a>

#### bpy.types.GreasePencilBuildModifier.frame_end

End Frame (when Restrict Frame Range is enabled) (in [-1.04857e+06, 1.04857e+06], default 125.0)

**Type:**

float

<a id="bpy.types.GreasePencilBuildModifier.frame_start"></a>

#### bpy.types.GreasePencilBuildModifier.frame_start

Start Frame (when Restrict Frame Range is enabled) (in [-1.04857e+06, 1.04857e+06], default 1.0)

**Type:**

float

<a id="bpy.types.GreasePencilBuildModifier.invert_layer_filter"></a>

#### bpy.types.GreasePencilBuildModifier.invert_layer_filter

Invert layer filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilBuildModifier.invert_layer_pass_filter"></a>

#### bpy.types.GreasePencilBuildModifier.invert_layer_pass_filter

Invert layer pass filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilBuildModifier.invert_material_filter"></a>

#### bpy.types.GreasePencilBuildModifier.invert_material_filter

Invert material filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilBuildModifier.invert_material_pass_filter"></a>

#### bpy.types.GreasePencilBuildModifier.invert_material_pass_filter

Invert material pass filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilBuildModifier.layer_pass_filter"></a>

#### bpy.types.GreasePencilBuildModifier.layer_pass_filter

Layer pass filter (in [0, 100], default 0)

**Type:**

int

<a id="bpy.types.GreasePencilBuildModifier.length"></a>

#### bpy.types.GreasePencilBuildModifier.length

Maximum number of frames that the build effect can run for (unless another GP keyframe occurs before this time has elapsed) (in [1, 1.04857e+06], default 100.0)

**Type:**

float

<a id="bpy.types.GreasePencilBuildModifier.material_filter"></a>

#### bpy.types.GreasePencilBuildModifier.material_filter

Material used for filtering

**Type:**

[`Material`](bpy.types.Material.md#bpy.types.Material "bpy.types.Material") | None

<a id="bpy.types.GreasePencilBuildModifier.material_pass_filter"></a>

#### bpy.types.GreasePencilBuildModifier.material_pass_filter

Material pass (in [0, 100], default 0)

**Type:**

int

<a id="bpy.types.GreasePencilBuildModifier.mode"></a>

#### bpy.types.GreasePencilBuildModifier.mode

How strokes are being built (default `'SEQUENTIAL'`)

- `SEQUENTIAL`
  Sequential – Strokes appear/disappear one after the other, but only a single one changes at a time.
- `CONCURRENT`
  Concurrent – Multiple strokes appear/disappear at once.
- `ADDITIVE`
  Additive – Builds only new strokes (assuming ‘additive’ drawing).

**Type:**

Literal[‘SEQUENTIAL’, ‘CONCURRENT’, ‘ADDITIVE’]

<a id="bpy.types.GreasePencilBuildModifier.object"></a>

#### bpy.types.GreasePencilBuildModifier.object

Object used as build starting position

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.GreasePencilBuildModifier.open_fading_panel"></a>

#### bpy.types.GreasePencilBuildModifier.open_fading_panel

(default False)

**Type:**

bool

<a id="bpy.types.GreasePencilBuildModifier.open_frame_range_panel"></a>

#### bpy.types.GreasePencilBuildModifier.open_frame_range_panel

(default False)

**Type:**

bool

<a id="bpy.types.GreasePencilBuildModifier.open_influence_panel"></a>

#### bpy.types.GreasePencilBuildModifier.open_influence_panel

(default False)

**Type:**

bool

<a id="bpy.types.GreasePencilBuildModifier.percentage_factor"></a>

#### bpy.types.GreasePencilBuildModifier.percentage_factor

Defines how much of the stroke is visible (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.GreasePencilBuildModifier.speed_factor"></a>

#### bpy.types.GreasePencilBuildModifier.speed_factor

Multiply recorded drawing speed by a factor (in [0, 100], default 1.2)

**Type:**

float

<a id="bpy.types.GreasePencilBuildModifier.speed_maxgap"></a>

#### bpy.types.GreasePencilBuildModifier.speed_maxgap

The maximum gap between strokes in seconds (in [0, 100], default 0.5)

**Type:**

float

<a id="bpy.types.GreasePencilBuildModifier.start_delay"></a>

#### bpy.types.GreasePencilBuildModifier.start_delay

Number of frames after each GP keyframe before the modifier has any effect (in [0, 1.04857e+06], default 0.0)

**Type:**

float

<a id="bpy.types.GreasePencilBuildModifier.target_vertex_group"></a>

#### bpy.types.GreasePencilBuildModifier.target_vertex_group

Output Vertex group (default “”, never None)

**Type:**

str

<a id="bpy.types.GreasePencilBuildModifier.time_mode"></a>

#### bpy.types.GreasePencilBuildModifier.time_mode

Use drawing speed, a number of frames, or a manual factor to build strokes (default `'FRAMES'`)

- `DRAWSPEED`
  Natural Drawing Speed – Use recorded speed multiplied by a factor.
- `FRAMES`
  Number of Frames – Set a fixed number of frames for all build animations.
- `PERCENTAGE`
  Percentage Factor – Set a manual percentage to build.

**Type:**

Literal[‘DRAWSPEED’, ‘FRAMES’, ‘PERCENTAGE’]

<a id="bpy.types.GreasePencilBuildModifier.transition"></a>

#### bpy.types.GreasePencilBuildModifier.transition

How are strokes animated (i.e. are they appearing or disappearing) (default `'GROW'`)

- `GROW`
  Grow – Show points in the order they occur in each stroke (e.g. for animating lines being drawn).
- `SHRINK`
  Shrink – Hide points from the end of each stroke to the start (e.g. for animating lines being erased).
- `FADE`
  Vanish – Hide points in the order they occur in each stroke (e.g. for animating ink fading or vanishing after getting drawn).

**Type:**

Literal[‘GROW’, ‘SHRINK’, ‘FADE’]

<a id="bpy.types.GreasePencilBuildModifier.tree_node_filter"></a>

#### bpy.types.GreasePencilBuildModifier.tree_node_filter

Layer name (default “”, never None)

**Type:**

str

<a id="bpy.types.GreasePencilBuildModifier.use_fading"></a>

#### bpy.types.GreasePencilBuildModifier.use_fading

Fade out strokes instead of directly cutting off (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilBuildModifier.use_layer_group_filter"></a>

#### bpy.types.GreasePencilBuildModifier.use_layer_group_filter

Filter by layer group name (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilBuildModifier.use_layer_pass_filter"></a>

#### bpy.types.GreasePencilBuildModifier.use_layer_pass_filter

Use layer pass filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilBuildModifier.use_material_pass_filter"></a>

#### bpy.types.GreasePencilBuildModifier.use_material_pass_filter

Use material pass filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilBuildModifier.use_percentage"></a>

#### bpy.types.GreasePencilBuildModifier.use_percentage

Use a percentage factor to determine the visible points (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilBuildModifier.use_restrict_frame_range"></a>

#### bpy.types.GreasePencilBuildModifier.use_restrict_frame_range

Only modify strokes during the specified frame range (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilBuildModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.GreasePencilBuildModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.GreasePencilBuildModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.GreasePencilBuildModifier.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, Modifier.name, Modifier.type, Modifier.show_viewport, Modifier.show_render, Modifier.show_in_editmode, Modifier.show_on_cage, Modifier.show_expanded, Modifier.is_active, Modifier.use_pin_to_last, Modifier.is_override_data, Modifier.use_apply_on_spline, Modifier.execution_time, Modifier.persistent_uid

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, Modifier.bl_rna_get_subclass, Modifier.bl_rna_get_subclass_py
