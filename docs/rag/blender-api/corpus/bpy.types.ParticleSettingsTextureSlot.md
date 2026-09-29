<!-- source: Blender Python API reference 5.2 / bpy.types.ParticleSettingsTextureSlot.html -->

<a id="particlesettingstextureslot-textureslot"></a>

# ParticleSettingsTextureSlot(TextureSlot)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`TextureSlot`](bpy.types.TextureSlot.md#bpy.types.TextureSlot "bpy.types.TextureSlot")

<a id="bpy.types.ParticleSettingsTextureSlot"></a>

### class bpy.types.ParticleSettingsTextureSlot(TextureSlot)

Texture slot for textures in a Particle Settings data-block

<a id="bpy.types.ParticleSettingsTextureSlot.clump_factor"></a>

#### bpy.types.ParticleSettingsTextureSlot.clump_factor

Amount texture affects child clump (in [-inf, inf], default 1.0)

**Type:**

float

<a id="bpy.types.ParticleSettingsTextureSlot.damp_factor"></a>

#### bpy.types.ParticleSettingsTextureSlot.damp_factor

Amount texture affects particle damping (in [-inf, inf], default 1.0)

**Type:**

float

<a id="bpy.types.ParticleSettingsTextureSlot.density_factor"></a>

#### bpy.types.ParticleSettingsTextureSlot.density_factor

Amount texture affects particle density (in [-inf, inf], default 1.0)

**Type:**

float

<a id="bpy.types.ParticleSettingsTextureSlot.field_factor"></a>

#### bpy.types.ParticleSettingsTextureSlot.field_factor

Amount texture affects particle force fields (in [-inf, inf], default 1.0)

**Type:**

float

<a id="bpy.types.ParticleSettingsTextureSlot.gravity_factor"></a>

#### bpy.types.ParticleSettingsTextureSlot.gravity_factor

Amount texture affects particle gravity (in [-inf, inf], default 1.0)

**Type:**

float

<a id="bpy.types.ParticleSettingsTextureSlot.kink_amp_factor"></a>

#### bpy.types.ParticleSettingsTextureSlot.kink_amp_factor

Amount texture affects child kink amplitude (in [-inf, inf], default 1.0)

**Type:**

float

<a id="bpy.types.ParticleSettingsTextureSlot.kink_freq_factor"></a>

#### bpy.types.ParticleSettingsTextureSlot.kink_freq_factor

Amount texture affects child kink frequency (in [-inf, inf], default 1.0)

**Type:**

float

<a id="bpy.types.ParticleSettingsTextureSlot.length_factor"></a>

#### bpy.types.ParticleSettingsTextureSlot.length_factor

Amount texture affects child hair length (in [-inf, inf], default 1.0)

**Type:**

float

<a id="bpy.types.ParticleSettingsTextureSlot.life_factor"></a>

#### bpy.types.ParticleSettingsTextureSlot.life_factor

Amount texture affects particle life time (in [-inf, inf], default 1.0)

**Type:**

float

<a id="bpy.types.ParticleSettingsTextureSlot.mapping"></a>

#### bpy.types.ParticleSettingsTextureSlot.mapping

(default `'FLAT'`)

- `FLAT`
  Flat – Map X and Y coordinates directly.
- `CUBE`
  Cube – Map using the normal vector.
- `TUBE`
  Tube – Map with Z as central axis.
- `SPHERE`
  Sphere – Map with Z as central axis.

**Type:**

Literal[‘FLAT’, ‘CUBE’, ‘TUBE’, ‘SPHERE’]

<a id="bpy.types.ParticleSettingsTextureSlot.mapping_x"></a>

#### bpy.types.ParticleSettingsTextureSlot.mapping_x

(default `'X'`)

**Type:**

Literal[‘NONE’, ‘X’, ‘Y’, ‘Z’]

<a id="bpy.types.ParticleSettingsTextureSlot.mapping_y"></a>

#### bpy.types.ParticleSettingsTextureSlot.mapping_y

(default `'Y'`)

**Type:**

Literal[‘NONE’, ‘X’, ‘Y’, ‘Z’]

<a id="bpy.types.ParticleSettingsTextureSlot.mapping_z"></a>

#### bpy.types.ParticleSettingsTextureSlot.mapping_z

(default `'Z'`)

**Type:**

Literal[‘NONE’, ‘X’, ‘Y’, ‘Z’]

<a id="bpy.types.ParticleSettingsTextureSlot.object"></a>

#### bpy.types.ParticleSettingsTextureSlot.object

Object to use for mapping with Object texture coordinates

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.ParticleSettingsTextureSlot.rough_factor"></a>

#### bpy.types.ParticleSettingsTextureSlot.rough_factor

Amount texture affects child roughness (in [-inf, inf], default 1.0)

**Type:**

float

<a id="bpy.types.ParticleSettingsTextureSlot.size_factor"></a>

#### bpy.types.ParticleSettingsTextureSlot.size_factor

Amount texture affects physical particle size (in [-inf, inf], default 1.0)

**Type:**

float

<a id="bpy.types.ParticleSettingsTextureSlot.texture_coords"></a>

#### bpy.types.ParticleSettingsTextureSlot.texture_coords

Texture coordinates used to map the texture onto the background (default `'UV'`)

- `GLOBAL`
  Global – Use global coordinates for the texture coordinates.
- `OBJECT`
  Object – Use linked object’s coordinates for texture coordinates.
- `UV`
  UV – Use UV coordinates for texture coordinates.
- `ORCO`
  Generated – Use the original undeformed coordinates of the object.
- `STRAND`
  Strand / Particle – Use normalized strand texture coordinate (1D) or particle age (X) and trail position (Y).

**Type:**

Literal[‘GLOBAL’, ‘OBJECT’, ‘UV’, ‘ORCO’, ‘STRAND’]

<a id="bpy.types.ParticleSettingsTextureSlot.time_factor"></a>

#### bpy.types.ParticleSettingsTextureSlot.time_factor

Amount texture affects particle emission time (in [-inf, inf], default 1.0)

**Type:**

float

<a id="bpy.types.ParticleSettingsTextureSlot.twist_factor"></a>

#### bpy.types.ParticleSettingsTextureSlot.twist_factor

Amount texture affects child twist (in [-inf, inf], default 1.0)

**Type:**

float

<a id="bpy.types.ParticleSettingsTextureSlot.use_map_clump"></a>

#### bpy.types.ParticleSettingsTextureSlot.use_map_clump

Affect the child clumping (default False)

**Type:**

bool

<a id="bpy.types.ParticleSettingsTextureSlot.use_map_damp"></a>

#### bpy.types.ParticleSettingsTextureSlot.use_map_damp

Affect the particle velocity damping (default False)

**Type:**

bool

<a id="bpy.types.ParticleSettingsTextureSlot.use_map_density"></a>

#### bpy.types.ParticleSettingsTextureSlot.use_map_density

Affect the density of the particles (default False)

**Type:**

bool

<a id="bpy.types.ParticleSettingsTextureSlot.use_map_field"></a>

#### bpy.types.ParticleSettingsTextureSlot.use_map_field

Affect the particle force fields (default False)

**Type:**

bool

<a id="bpy.types.ParticleSettingsTextureSlot.use_map_gravity"></a>

#### bpy.types.ParticleSettingsTextureSlot.use_map_gravity

Affect the particle gravity (default False)

**Type:**

bool

<a id="bpy.types.ParticleSettingsTextureSlot.use_map_kink_amp"></a>

#### bpy.types.ParticleSettingsTextureSlot.use_map_kink_amp

Affect the child kink amplitude (default False)

**Type:**

bool

<a id="bpy.types.ParticleSettingsTextureSlot.use_map_kink_freq"></a>

#### bpy.types.ParticleSettingsTextureSlot.use_map_kink_freq

Affect the child kink frequency (default False)

**Type:**

bool

<a id="bpy.types.ParticleSettingsTextureSlot.use_map_length"></a>

#### bpy.types.ParticleSettingsTextureSlot.use_map_length

Affect the child hair length (default False)

**Type:**

bool

<a id="bpy.types.ParticleSettingsTextureSlot.use_map_life"></a>

#### bpy.types.ParticleSettingsTextureSlot.use_map_life

Affect the life time of the particles (default False)

**Type:**

bool

<a id="bpy.types.ParticleSettingsTextureSlot.use_map_rough"></a>

#### bpy.types.ParticleSettingsTextureSlot.use_map_rough

Affect the child rough (default False)

**Type:**

bool

<a id="bpy.types.ParticleSettingsTextureSlot.use_map_size"></a>

#### bpy.types.ParticleSettingsTextureSlot.use_map_size

Affect the particle size (default False)

**Type:**

bool

<a id="bpy.types.ParticleSettingsTextureSlot.use_map_time"></a>

#### bpy.types.ParticleSettingsTextureSlot.use_map_time

Affect the emission time of the particles (default True)

**Type:**

bool

<a id="bpy.types.ParticleSettingsTextureSlot.use_map_twist"></a>

#### bpy.types.ParticleSettingsTextureSlot.use_map_twist

Affect the child twist (default False)

**Type:**

bool

<a id="bpy.types.ParticleSettingsTextureSlot.use_map_velocity"></a>

#### bpy.types.ParticleSettingsTextureSlot.use_map_velocity

Affect the particle initial velocity (default False)

**Type:**

bool

<a id="bpy.types.ParticleSettingsTextureSlot.uv_layer"></a>

#### bpy.types.ParticleSettingsTextureSlot.uv_layer

UV map to use for mapping with UV texture coordinates (default “”, never None)

**Type:**

str

<a id="bpy.types.ParticleSettingsTextureSlot.velocity_factor"></a>

#### bpy.types.ParticleSettingsTextureSlot.velocity_factor

Amount texture affects particle initial velocity (in [-inf, inf], default 1.0)

**Type:**

float

<a id="bpy.types.ParticleSettingsTextureSlot.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ParticleSettingsTextureSlot.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ParticleSettingsTextureSlot.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ParticleSettingsTextureSlot.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, TextureSlot.texture, TextureSlot.name, TextureSlot.offset, TextureSlot.scale, TextureSlot.color, TextureSlot.blend_type, TextureSlot.default_value, TextureSlot.output_node

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, TextureSlot.bl_rna_get_subclass, TextureSlot.bl_rna_get_subclass_py

<a id="references"></a>

## References

|  |  |
| --- | --- |
| - [`ParticleSettings.texture_slots`](bpy.types.ParticleSettings.md#bpy.types.ParticleSettings.texture_slots "bpy.types.ParticleSettings.texture_slots") - [`ParticleSettingsTextureSlots.add`](bpy.types.ParticleSettingsTextureSlots.md#bpy.types.ParticleSettingsTextureSlots.add "bpy.types.ParticleSettingsTextureSlots.add") | - [`ParticleSettingsTextureSlots.create`](bpy.types.ParticleSettingsTextureSlots.md#bpy.types.ParticleSettingsTextureSlots.create "bpy.types.ParticleSettingsTextureSlots.create") |
