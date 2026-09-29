<!-- source: Blender Python API reference 5.2 / bpy.types.OceanModifier.html -->

<a id="oceanmodifier-modifier"></a>

# OceanModifier(Modifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Modifier`](bpy.types.Modifier.md#bpy.types.Modifier "bpy.types.Modifier")

<a id="bpy.types.OceanModifier"></a>

### class bpy.types.OceanModifier(Modifier)

Simulate an ocean surface

<a id="bpy.types.OceanModifier.bake_foam_fade"></a>

#### bpy.types.OceanModifier.bake_foam_fade

How much foam accumulates over time (baked ocean only) (in [0, inf], default 0.98)

**Type:**

float

<a id="bpy.types.OceanModifier.choppiness"></a>

#### bpy.types.OceanModifier.choppiness

Choppiness of the wave’s crest (adds some horizontal component to the displacement) (in [0, inf], default 1.0)

**Type:**

float

<a id="bpy.types.OceanModifier.damping"></a>

#### bpy.types.OceanModifier.damping

Damp reflected waves going in opposite direction to the wind (in [0, 1], default 0.5)

**Type:**

float

<a id="bpy.types.OceanModifier.depth"></a>

#### bpy.types.OceanModifier.depth

Depth of the solid ground below the water surface (in [-inf, inf], default 200.0)

**Type:**

float

<a id="bpy.types.OceanModifier.fetch_jonswap"></a>

#### bpy.types.OceanModifier.fetch_jonswap

This is the distance from a lee shore, called the fetch, or the distance over which the wind blows with constant velocity. Used by ‘JONSWAP’ and ‘TMA’ models. (in [0, inf], default 120.0)

**Type:**

float

<a id="bpy.types.OceanModifier.filepath"></a>

#### bpy.types.OceanModifier.filepath

Path to a folder to store external baked images (default “”, never None, blend relative `//` prefix supported)

**Type:**

str

<a id="bpy.types.OceanModifier.foam_coverage"></a>

#### bpy.types.OceanModifier.foam_coverage

Amount of generated foam (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.OceanModifier.foam_layer_name"></a>

#### bpy.types.OceanModifier.foam_layer_name

Name of the vertex color layer used for foam (default “”, never None)

**Type:**

str

<a id="bpy.types.OceanModifier.frame_end"></a>

#### bpy.types.OceanModifier.frame_end

End frame of the ocean baking (in [-inf, inf], default 250)

**Type:**

int

<a id="bpy.types.OceanModifier.frame_start"></a>

#### bpy.types.OceanModifier.frame_start

Start frame of the ocean baking (in [-inf, inf], default 1)

**Type:**

int

<a id="bpy.types.OceanModifier.geometry_mode"></a>

#### bpy.types.OceanModifier.geometry_mode

Method of modifying geometry (default `'GENERATE'`)

- `GENERATE`
  Generate – Generate ocean surface geometry at the specified resolution.
- `DISPLACE`
  Displace – Displace existing geometry according to simulation.

**Type:**

Literal[‘GENERATE’, ‘DISPLACE’]

<a id="bpy.types.OceanModifier.invert_spray"></a>

#### bpy.types.OceanModifier.invert_spray

Invert the spray direction map (default False)

**Type:**

bool

<a id="bpy.types.OceanModifier.is_cached"></a>

#### bpy.types.OceanModifier.is_cached

Whether the ocean is using cached data or simulating (default False, readonly)

**Type:**

bool

<a id="bpy.types.OceanModifier.random_seed"></a>

#### bpy.types.OceanModifier.random_seed

Seed of the random generator (in [0, inf], default 0)

**Type:**

int

<a id="bpy.types.OceanModifier.repeat_x"></a>

#### bpy.types.OceanModifier.repeat_x

Repetitions of the generated surface in X (in [1, 1024], default 1)

**Type:**

int

<a id="bpy.types.OceanModifier.repeat_y"></a>

#### bpy.types.OceanModifier.repeat_y

Repetitions of the generated surface in Y (in [1, 1024], default 1)

**Type:**

int

<a id="bpy.types.OceanModifier.resolution"></a>

#### bpy.types.OceanModifier.resolution

Resolution of the generated surface for rendering and baking (in [1, 1024], default 7)

**Type:**

int

<a id="bpy.types.OceanModifier.sharpen_peak_jonswap"></a>

#### bpy.types.OceanModifier.sharpen_peak_jonswap

Peak sharpening for ‘JONSWAP’ and ‘TMA’ models (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.OceanModifier.size"></a>

#### bpy.types.OceanModifier.size

Surface scale factor (does not affect the height of the waves) (in [0, inf], default 1.0)

**Type:**

float

<a id="bpy.types.OceanModifier.spatial_size"></a>

#### bpy.types.OceanModifier.spatial_size

Size of the simulation domain (in meters), and of the generated geometry (in BU) (in [-inf, inf], default 50)

**Type:**

int

<a id="bpy.types.OceanModifier.spectrum"></a>

#### bpy.types.OceanModifier.spectrum

Spectrum to use (default `'PHILLIPS'`)

- `PHILLIPS`
  Turbulent Ocean – Use for turbulent seas with foam.
- `PIERSON_MOSKOWITZ`
  Established Ocean – Use for a large area, established ocean (Pierson-Moskowitz method).
- `JONSWAP`
  Established Ocean (Sharp Peaks) – Use for established oceans (‘JONSWAP’, Pierson-Moskowitz method) with peak sharpening.
- `TEXEL_MARSEN_ARSLOE`
  Shallow Water – Use for shallow water (‘JONSWAP’, ‘TMA’ - Texel-Marsen-Arsloe method).

**Type:**

Literal[‘PHILLIPS’, ‘PIERSON_MOSKOWITZ’, ‘JONSWAP’, ‘TEXEL_MARSEN_ARSLOE’]

<a id="bpy.types.OceanModifier.spray_layer_name"></a>

#### bpy.types.OceanModifier.spray_layer_name

Name of the vertex color layer used for the spray direction map (default “”, never None)

**Type:**

str

<a id="bpy.types.OceanModifier.time"></a>

#### bpy.types.OceanModifier.time

Current time of the simulation (in [0, inf], default 1.0)

**Type:**

float

<a id="bpy.types.OceanModifier.use_foam"></a>

#### bpy.types.OceanModifier.use_foam

Generate foam mask as a vertex color channel (default False)

**Type:**

bool

<a id="bpy.types.OceanModifier.use_normals"></a>

#### bpy.types.OceanModifier.use_normals

Output normals for bump mapping - disabling can speed up performance if it’s not needed (default False)

**Type:**

bool

<a id="bpy.types.OceanModifier.use_spray"></a>

#### bpy.types.OceanModifier.use_spray

Generate map of spray direction as a vertex color channel (default False)

**Type:**

bool

<a id="bpy.types.OceanModifier.viewport_resolution"></a>

#### bpy.types.OceanModifier.viewport_resolution

Viewport resolution of the generated surface (in [1, 1024], default 7)

**Type:**

int

<a id="bpy.types.OceanModifier.wave_alignment"></a>

#### bpy.types.OceanModifier.wave_alignment

How much the waves are aligned to each other (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.OceanModifier.wave_direction"></a>

#### bpy.types.OceanModifier.wave_direction

Main direction of the waves when they are (partially) aligned (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.OceanModifier.wave_scale"></a>

#### bpy.types.OceanModifier.wave_scale

Scale of the displacement effect (in [0, inf], default 1.0)

**Type:**

float

<a id="bpy.types.OceanModifier.wave_scale_min"></a>

#### bpy.types.OceanModifier.wave_scale_min

Shortest allowed wavelength (in [0, inf], default 0.01)

**Type:**

float

<a id="bpy.types.OceanModifier.wind_velocity"></a>

#### bpy.types.OceanModifier.wind_velocity

Wind speed (in [-inf, inf], default 30.0)

**Type:**

float

<a id="bpy.types.OceanModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.OceanModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.OceanModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.OceanModifier.bl_rna_get_subclass_py(id, default=None, /)

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
