<!-- source: Blender Python API reference 5.2 / bpy.types.DynamicPaintSurface.html -->

<a id="dynamicpaintsurface-bpy-struct"></a>

# DynamicPaintSurface(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.DynamicPaintSurface"></a>

### class bpy.types.DynamicPaintSurface(bpy_struct)

A canvas surface layer

<a id="bpy.types.DynamicPaintSurface.brush_collection"></a>

#### bpy.types.DynamicPaintSurface.brush_collection

Only use brush objects from this collection

**Type:**

[`Collection`](bpy.types.Collection.md#bpy.types.Collection "bpy.types.Collection") | None

<a id="bpy.types.DynamicPaintSurface.brush_influence_scale"></a>

#### bpy.types.DynamicPaintSurface.brush_influence_scale

Adjust influence brush objects have on this surface (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.DynamicPaintSurface.brush_radius_scale"></a>

#### bpy.types.DynamicPaintSurface.brush_radius_scale

Adjust radius of proximity brushes or particles for this surface (in [0, 10], default 0.0)

**Type:**

float

<a id="bpy.types.DynamicPaintSurface.color_dry_threshold"></a>

#### bpy.types.DynamicPaintSurface.color_dry_threshold

The wetness level when colors start to shift to the background (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.DynamicPaintSurface.color_spread_speed"></a>

#### bpy.types.DynamicPaintSurface.color_spread_speed

How fast colors get mixed within wet paint (in [0, 2], default 0.0)

**Type:**

float

<a id="bpy.types.DynamicPaintSurface.depth_clamp"></a>

#### bpy.types.DynamicPaintSurface.depth_clamp

Maximum level of depth intersection in object space (use 0.0 to disable) (in [0, 50], default 0.0)

**Type:**

float

<a id="bpy.types.DynamicPaintSurface.displace_factor"></a>

#### bpy.types.DynamicPaintSurface.displace_factor

Strength of displace when applied to the mesh (in [-50, 50], default 0.0)

**Type:**

float

<a id="bpy.types.DynamicPaintSurface.displace_type"></a>

#### bpy.types.DynamicPaintSurface.displace_type

(default `'DISPLACE'`)

**Type:**

Literal[‘DISPLACE’, ‘DEPTH’]

<a id="bpy.types.DynamicPaintSurface.dissolve_speed"></a>

#### bpy.types.DynamicPaintSurface.dissolve_speed

Approximately in how many frames should dissolve happen (in [1, 10000], default 0)

**Type:**

int

<a id="bpy.types.DynamicPaintSurface.drip_acceleration"></a>

#### bpy.types.DynamicPaintSurface.drip_acceleration

How much surface acceleration affects dripping (in [-200, 200], default 0.0)

**Type:**

float

<a id="bpy.types.DynamicPaintSurface.drip_velocity"></a>

#### bpy.types.DynamicPaintSurface.drip_velocity

How much surface velocity affects dripping (in [-200, 200], default 0.0)

**Type:**

float

<a id="bpy.types.DynamicPaintSurface.dry_speed"></a>

#### bpy.types.DynamicPaintSurface.dry_speed

Approximately in how many frames should drying happen (in [1, 10000], default 0)

**Type:**

int

<a id="bpy.types.DynamicPaintSurface.effect_ui"></a>

#### bpy.types.DynamicPaintSurface.effect_ui

(default `'SPREAD'`)

**Type:**

Literal[‘SPREAD’, ‘DRIP’, ‘SHRINK’]

<a id="bpy.types.DynamicPaintSurface.effector_weights"></a>

#### bpy.types.DynamicPaintSurface.effector_weights

(readonly)

**Type:**

[`EffectorWeights`](bpy.types.EffectorWeights.md#bpy.types.EffectorWeights "bpy.types.EffectorWeights") | None

<a id="bpy.types.DynamicPaintSurface.frame_end"></a>

#### bpy.types.DynamicPaintSurface.frame_end

Simulation end frame (in [1, 1048574], default 0)

**Type:**

int

<a id="bpy.types.DynamicPaintSurface.frame_start"></a>

#### bpy.types.DynamicPaintSurface.frame_start

Simulation start frame (in [1, 1048574], default 0)

**Type:**

int

<a id="bpy.types.DynamicPaintSurface.frame_substeps"></a>

#### bpy.types.DynamicPaintSurface.frame_substeps

Do extra frames between scene frames to ensure smooth motion (in [0, 20], default 0)

**Type:**

int

<a id="bpy.types.DynamicPaintSurface.image_fileformat"></a>

#### bpy.types.DynamicPaintSurface.image_fileformat

(default `'PNG'`)

**Type:**

Literal[‘PNG’, ‘OPENEXR’]

<a id="bpy.types.DynamicPaintSurface.image_output_path"></a>

#### bpy.types.DynamicPaintSurface.image_output_path

Directory to save the textures (default “”, never None, blend relative `//` prefix supported)

**Type:**

str

<a id="bpy.types.DynamicPaintSurface.image_resolution"></a>

#### bpy.types.DynamicPaintSurface.image_resolution

Output image resolution (in [16, 4096], default 0)

**Type:**

int

<a id="bpy.types.DynamicPaintSurface.init_color"></a>

#### bpy.types.DynamicPaintSurface.init_color

Initial color of the surface (array of 4 items, in [0, inf], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.DynamicPaintSurface.init_color_type"></a>

#### bpy.types.DynamicPaintSurface.init_color_type

(default `'NONE'`)

**Type:**

Literal[‘NONE’, ‘COLOR’, ‘TEXTURE’, ‘VERTEX_COLOR’]

<a id="bpy.types.DynamicPaintSurface.init_layername"></a>

#### bpy.types.DynamicPaintSurface.init_layername

(default “”, never None)

**Type:**

str

<a id="bpy.types.DynamicPaintSurface.init_texture"></a>

#### bpy.types.DynamicPaintSurface.init_texture

**Type:**

[`Texture`](bpy.types.Texture.md#bpy.types.Texture "bpy.types.Texture") | None

<a id="bpy.types.DynamicPaintSurface.is_active"></a>

#### bpy.types.DynamicPaintSurface.is_active

Toggle whether surface is processed or ignored (default False)

**Type:**

bool

<a id="bpy.types.DynamicPaintSurface.is_cache_user"></a>

#### bpy.types.DynamicPaintSurface.is_cache_user

(default False, readonly)

**Type:**

bool

<a id="bpy.types.DynamicPaintSurface.name"></a>

#### bpy.types.DynamicPaintSurface.name

Surface name (default “”, never None)

**Type:**

str

<a id="bpy.types.DynamicPaintSurface.output_name_a"></a>

#### bpy.types.DynamicPaintSurface.output_name_a

Name used to save output from this surface (default “”, never None)

**Type:**

str

<a id="bpy.types.DynamicPaintSurface.output_name_b"></a>

#### bpy.types.DynamicPaintSurface.output_name_b

Name used to save output from this surface (default “”, never None)

**Type:**

str

<a id="bpy.types.DynamicPaintSurface.point_cache"></a>

#### bpy.types.DynamicPaintSurface.point_cache

(readonly, never None)

**Type:**

[`PointCache`](bpy.types.PointCache.md#bpy.types.PointCache "bpy.types.PointCache")

<a id="bpy.types.DynamicPaintSurface.shrink_speed"></a>

#### bpy.types.DynamicPaintSurface.shrink_speed

How fast shrink effect moves on the canvas surface (in [0.001, 10], default 0.0)

**Type:**

float

<a id="bpy.types.DynamicPaintSurface.spread_speed"></a>

#### bpy.types.DynamicPaintSurface.spread_speed

How fast spread effect moves on the canvas surface (in [0.001, 10], default 0.0)

**Type:**

float

<a id="bpy.types.DynamicPaintSurface.surface_format"></a>

#### bpy.types.DynamicPaintSurface.surface_format

Surface Format (default `'VERTEX'`)

**Type:**

Literal[‘VERTEX’, ‘IMAGE’]

<a id="bpy.types.DynamicPaintSurface.surface_type"></a>

#### bpy.types.DynamicPaintSurface.surface_type

Surface Type (default `'PAINT'`)

**Type:**

Literal[‘PAINT’]

<a id="bpy.types.DynamicPaintSurface.use_antialiasing"></a>

#### bpy.types.DynamicPaintSurface.use_antialiasing

Use 5× multisampling to smooth paint edges (default False)

**Type:**

bool

<a id="bpy.types.DynamicPaintSurface.use_dissolve"></a>

#### bpy.types.DynamicPaintSurface.use_dissolve

Enable to make surface changes disappear over time (default False)

**Type:**

bool

<a id="bpy.types.DynamicPaintSurface.use_dissolve_log"></a>

#### bpy.types.DynamicPaintSurface.use_dissolve_log

Use logarithmic dissolve (makes high values to fade faster than low values) (default False)

**Type:**

bool

<a id="bpy.types.DynamicPaintSurface.use_drip"></a>

#### bpy.types.DynamicPaintSurface.use_drip

Process drip effect (drip wet paint to gravity direction) (default False)

**Type:**

bool

<a id="bpy.types.DynamicPaintSurface.use_dry_log"></a>

#### bpy.types.DynamicPaintSurface.use_dry_log

Use logarithmic drying (makes high values to dry faster than low values) (default False)

**Type:**

bool

<a id="bpy.types.DynamicPaintSurface.use_drying"></a>

#### bpy.types.DynamicPaintSurface.use_drying

Enable to make surface wetness dry over time (default False)

**Type:**

bool

<a id="bpy.types.DynamicPaintSurface.use_incremental_displace"></a>

#### bpy.types.DynamicPaintSurface.use_incremental_displace

New displace is added cumulatively on top of existing (default False)

**Type:**

bool

<a id="bpy.types.DynamicPaintSurface.use_output_a"></a>

#### bpy.types.DynamicPaintSurface.use_output_a

Save this output layer (default False)

**Type:**

bool

<a id="bpy.types.DynamicPaintSurface.use_output_b"></a>

#### bpy.types.DynamicPaintSurface.use_output_b

Save this output layer (default False)

**Type:**

bool

<a id="bpy.types.DynamicPaintSurface.use_premultiply"></a>

#### bpy.types.DynamicPaintSurface.use_premultiply

Multiply color by alpha (recommended for Blender input) (default False)

**Type:**

bool

<a id="bpy.types.DynamicPaintSurface.use_shrink"></a>

#### bpy.types.DynamicPaintSurface.use_shrink

Process shrink effect (shrink paint areas) (default False)

**Type:**

bool

<a id="bpy.types.DynamicPaintSurface.use_spread"></a>

#### bpy.types.DynamicPaintSurface.use_spread

Process spread effect (spread wet paint around surface) (default False)

**Type:**

bool

<a id="bpy.types.DynamicPaintSurface.use_wave_open_border"></a>

#### bpy.types.DynamicPaintSurface.use_wave_open_border

Pass waves through mesh edges (default False)

**Type:**

bool

<a id="bpy.types.DynamicPaintSurface.uv_layer"></a>

#### bpy.types.DynamicPaintSurface.uv_layer

UV map name (default “”, never None)

**Type:**

str

<a id="bpy.types.DynamicPaintSurface.wave_damping"></a>

#### bpy.types.DynamicPaintSurface.wave_damping

Wave damping factor (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.DynamicPaintSurface.wave_smoothness"></a>

#### bpy.types.DynamicPaintSurface.wave_smoothness

Limit maximum steepness of wave slope between simulation points (use higher values for smoother waves at expense of reduced detail) (in [0, 10], default 0.0)

**Type:**

float

<a id="bpy.types.DynamicPaintSurface.wave_speed"></a>

#### bpy.types.DynamicPaintSurface.wave_speed

Wave propagation speed (in [0.01, 5], default 0.0)

**Type:**

float

<a id="bpy.types.DynamicPaintSurface.wave_spring"></a>

#### bpy.types.DynamicPaintSurface.wave_spring

Spring force that pulls water level back to zero (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.DynamicPaintSurface.wave_timescale"></a>

#### bpy.types.DynamicPaintSurface.wave_timescale

Wave time scaling factor (in [0.01, 3], default 0.0)

**Type:**

float

<a id="bpy.types.DynamicPaintSurface.output_exists"></a>

#### bpy.types.DynamicPaintSurface.output_exists(object, index)

Checks if surface output layer of given name exists

**Parameters:**

- **object** ([`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None) – (never None)
- **index** (int) – Index, (in [0, 1])

**Return type:**

bool

<a id="bpy.types.DynamicPaintSurface.bl_rna_get_subclass"></a>

#### classmethod bpy.types.DynamicPaintSurface.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.DynamicPaintSurface.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.DynamicPaintSurface.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`DynamicPaintCanvasSettings.canvas_surfaces`](bpy.types.DynamicPaintCanvasSettings.md#bpy.types.DynamicPaintCanvasSettings.canvas_surfaces "bpy.types.DynamicPaintCanvasSettings.canvas_surfaces") | - [`DynamicPaintSurfaces.active`](bpy.types.DynamicPaintSurfaces.md#bpy.types.DynamicPaintSurfaces.active "bpy.types.DynamicPaintSurfaces.active") |
