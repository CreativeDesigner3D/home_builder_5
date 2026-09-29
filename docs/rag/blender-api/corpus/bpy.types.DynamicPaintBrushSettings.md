<!-- source: Blender Python API reference 5.2 / bpy.types.DynamicPaintBrushSettings.html -->

<a id="dynamicpaintbrushsettings-bpy-struct"></a>

# DynamicPaintBrushSettings(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.DynamicPaintBrushSettings"></a>

### class bpy.types.DynamicPaintBrushSettings(bpy_struct)

Brush settings

<a id="bpy.types.DynamicPaintBrushSettings.invert_proximity"></a>

#### bpy.types.DynamicPaintBrushSettings.invert_proximity

Proximity falloff is applied inside the volume (default False)

**Type:**

bool

<a id="bpy.types.DynamicPaintBrushSettings.paint_alpha"></a>

#### bpy.types.DynamicPaintBrushSettings.paint_alpha

Paint alpha (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.DynamicPaintBrushSettings.paint_color"></a>

#### bpy.types.DynamicPaintBrushSettings.paint_color

Color of the paint (array of 3 items, in [0, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.DynamicPaintBrushSettings.paint_distance"></a>

#### bpy.types.DynamicPaintBrushSettings.paint_distance

Maximum distance from brush to mesh surface to affect paint (in [0, 500], default 0.0)

**Type:**

float

<a id="bpy.types.DynamicPaintBrushSettings.paint_ramp"></a>

#### bpy.types.DynamicPaintBrushSettings.paint_ramp

Color ramp used to define proximity falloff (readonly)

**Type:**

[`ColorRamp`](bpy.types.ColorRamp.md#bpy.types.ColorRamp "bpy.types.ColorRamp") | None

<a id="bpy.types.DynamicPaintBrushSettings.paint_source"></a>

#### bpy.types.DynamicPaintBrushSettings.paint_source

(default `'VOLUME'`)

**Type:**

Literal[‘PARTICLE_SYSTEM’, ‘POINT’, ‘DISTANCE’, ‘VOLUME_DISTANCE’, ‘VOLUME’]

<a id="bpy.types.DynamicPaintBrushSettings.paint_wetness"></a>

#### bpy.types.DynamicPaintBrushSettings.paint_wetness

Paint wetness, visible in wetmap (some effects only affect wet paint) (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.DynamicPaintBrushSettings.particle_system"></a>

#### bpy.types.DynamicPaintBrushSettings.particle_system

The particle system to paint with

**Type:**

[`ParticleSystem`](bpy.types.ParticleSystem.md#bpy.types.ParticleSystem "bpy.types.ParticleSystem") | None

<a id="bpy.types.DynamicPaintBrushSettings.proximity_falloff"></a>

#### bpy.types.DynamicPaintBrushSettings.proximity_falloff

Proximity falloff type (default `'CONSTANT'`)

**Type:**

Literal[‘SMOOTH’, ‘CONSTANT’, ‘RAMP’]

<a id="bpy.types.DynamicPaintBrushSettings.ray_direction"></a>

#### bpy.types.DynamicPaintBrushSettings.ray_direction

Ray direction to use for projection (if brush object is located in that direction it’s painted) (default `'CANVAS'`)

**Type:**

Literal[‘CANVAS’, ‘BRUSH’, ‘Z_AXIS’]

<a id="bpy.types.DynamicPaintBrushSettings.smooth_radius"></a>

#### bpy.types.DynamicPaintBrushSettings.smooth_radius

Smooth falloff added after solid radius (in [0, 10], default 0.0)

**Type:**

float

<a id="bpy.types.DynamicPaintBrushSettings.smudge_strength"></a>

#### bpy.types.DynamicPaintBrushSettings.smudge_strength

Smudge effect strength (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.DynamicPaintBrushSettings.solid_radius"></a>

#### bpy.types.DynamicPaintBrushSettings.solid_radius

Radius that will be painted solid (in [0.01, 10], default 0.0)

**Type:**

float

<a id="bpy.types.DynamicPaintBrushSettings.use_absolute_alpha"></a>

#### bpy.types.DynamicPaintBrushSettings.use_absolute_alpha

Only increase alpha value if paint alpha is higher than existing (default False)

**Type:**

bool

<a id="bpy.types.DynamicPaintBrushSettings.use_negative_volume"></a>

#### bpy.types.DynamicPaintBrushSettings.use_negative_volume

Negate influence inside the volume (default False)

**Type:**

bool

<a id="bpy.types.DynamicPaintBrushSettings.use_paint_erase"></a>

#### bpy.types.DynamicPaintBrushSettings.use_paint_erase

Erase / remove paint instead of adding it (default False)

**Type:**

bool

<a id="bpy.types.DynamicPaintBrushSettings.use_particle_radius"></a>

#### bpy.types.DynamicPaintBrushSettings.use_particle_radius

Use radius from particle settings (default False)

**Type:**

bool

<a id="bpy.types.DynamicPaintBrushSettings.use_proximity_project"></a>

#### bpy.types.DynamicPaintBrushSettings.use_proximity_project

Brush is projected to canvas from defined direction within brush proximity (default False)

**Type:**

bool

<a id="bpy.types.DynamicPaintBrushSettings.use_proximity_ramp_alpha"></a>

#### bpy.types.DynamicPaintBrushSettings.use_proximity_ramp_alpha

Only read color ramp alpha (default False)

**Type:**

bool

<a id="bpy.types.DynamicPaintBrushSettings.use_smudge"></a>

#### bpy.types.DynamicPaintBrushSettings.use_smudge

Make this brush to smudge existing paint as it moves (default False)

**Type:**

bool

<a id="bpy.types.DynamicPaintBrushSettings.use_velocity_alpha"></a>

#### bpy.types.DynamicPaintBrushSettings.use_velocity_alpha

Multiply brush influence by velocity color ramp alpha (default False)

**Type:**

bool

<a id="bpy.types.DynamicPaintBrushSettings.use_velocity_color"></a>

#### bpy.types.DynamicPaintBrushSettings.use_velocity_color

Replace brush color by velocity color ramp (default False)

**Type:**

bool

<a id="bpy.types.DynamicPaintBrushSettings.use_velocity_depth"></a>

#### bpy.types.DynamicPaintBrushSettings.use_velocity_depth

Multiply brush intersection depth (displace, waves) by velocity ramp alpha (default False)

**Type:**

bool

<a id="bpy.types.DynamicPaintBrushSettings.velocity_max"></a>

#### bpy.types.DynamicPaintBrushSettings.velocity_max

Velocity considered as maximum influence (Blender units per frame) (in [0.0001, 10], default 0.0)

**Type:**

float

<a id="bpy.types.DynamicPaintBrushSettings.velocity_ramp"></a>

#### bpy.types.DynamicPaintBrushSettings.velocity_ramp

Color ramp used to define brush velocity effect (readonly)

**Type:**

[`ColorRamp`](bpy.types.ColorRamp.md#bpy.types.ColorRamp "bpy.types.ColorRamp") | None

<a id="bpy.types.DynamicPaintBrushSettings.wave_clamp"></a>

#### bpy.types.DynamicPaintBrushSettings.wave_clamp

Maximum level of surface intersection used to influence waves (use 0.0 to disable) (in [0, 50], default 0.0)

**Type:**

float

<a id="bpy.types.DynamicPaintBrushSettings.wave_factor"></a>

#### bpy.types.DynamicPaintBrushSettings.wave_factor

Multiplier for wave influence of this brush (in [-2, 2], default 0.0)

**Type:**

float

<a id="bpy.types.DynamicPaintBrushSettings.wave_type"></a>

#### bpy.types.DynamicPaintBrushSettings.wave_type

(default `'DEPTH'`)

**Type:**

Literal[‘CHANGE’, ‘DEPTH’, ‘FORCE’, ‘REFLECT’]

<a id="bpy.types.DynamicPaintBrushSettings.bl_rna_get_subclass"></a>

#### classmethod bpy.types.DynamicPaintBrushSettings.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.DynamicPaintBrushSettings.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.DynamicPaintBrushSettings.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`DynamicPaintModifier.brush_settings`](bpy.types.DynamicPaintModifier.md#bpy.types.DynamicPaintModifier.brush_settings "bpy.types.DynamicPaintModifier.brush_settings") |  |
