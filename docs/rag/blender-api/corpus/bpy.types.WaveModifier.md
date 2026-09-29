<!-- source: Blender Python API reference 5.2 / bpy.types.WaveModifier.html -->

<a id="wavemodifier-modifier"></a>

# WaveModifier(Modifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Modifier`](bpy.types.Modifier.md#bpy.types.Modifier "bpy.types.Modifier")

<a id="bpy.types.WaveModifier"></a>

### class bpy.types.WaveModifier(Modifier)

Wave effect modifier

<a id="bpy.types.WaveModifier.damping_time"></a>

#### bpy.types.WaveModifier.damping_time

Number of frames in which the wave damps out after it dies (in [-1.04857e+06, 1.04857e+06], default 10.0)

**Type:**

float

<a id="bpy.types.WaveModifier.falloff_radius"></a>

#### bpy.types.WaveModifier.falloff_radius

Distance after which it fades out (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.WaveModifier.height"></a>

#### bpy.types.WaveModifier.height

Height of the wave (in [-inf, inf], default 0.5)

**Type:**

float

<a id="bpy.types.WaveModifier.invert_vertex_group"></a>

#### bpy.types.WaveModifier.invert_vertex_group

Invert vertex group influence (default False)

**Type:**

bool

<a id="bpy.types.WaveModifier.lifetime"></a>

#### bpy.types.WaveModifier.lifetime

Lifetime of the wave in frames, zero means infinite (in [-1.04857e+06, 1.04857e+06], default 0.0)

**Type:**

float

<a id="bpy.types.WaveModifier.narrowness"></a>

#### bpy.types.WaveModifier.narrowness

Distance between the top and the base of a wave, the higher the value, the more narrow the wave (in [0, inf], default 1.5)

**Type:**

float

<a id="bpy.types.WaveModifier.speed"></a>

#### bpy.types.WaveModifier.speed

Speed of the wave, towards the starting point when negative (in [-inf, inf], default 0.25)

**Type:**

float

<a id="bpy.types.WaveModifier.start_position_object"></a>

#### bpy.types.WaveModifier.start_position_object

Object which defines the wave center

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.WaveModifier.start_position_x"></a>

#### bpy.types.WaveModifier.start_position_x

X coordinate of the start position (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.WaveModifier.start_position_y"></a>

#### bpy.types.WaveModifier.start_position_y

Y coordinate of the start position (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.WaveModifier.texture"></a>

#### bpy.types.WaveModifier.texture

**Type:**

[`Texture`](bpy.types.Texture.md#bpy.types.Texture "bpy.types.Texture") | None

<a id="bpy.types.WaveModifier.texture_coords"></a>

#### bpy.types.WaveModifier.texture_coords

(default `'LOCAL'`)

- `LOCAL`
  Local – Use the local coordinate system for the texture coordinates.
- `GLOBAL`
  Global – Use the global coordinate system for the texture coordinates.
- `OBJECT`
  Object – Use the linked object’s local coordinate system for the texture coordinates.
- `UV`
  UV – Use UV coordinates for the texture coordinates.

**Type:**

Literal[‘LOCAL’, ‘GLOBAL’, ‘OBJECT’, ‘UV’]

<a id="bpy.types.WaveModifier.texture_coords_bone"></a>

#### bpy.types.WaveModifier.texture_coords_bone

Bone to set the texture coordinates (default “”, never None)

**Type:**

str

<a id="bpy.types.WaveModifier.texture_coords_object"></a>

#### bpy.types.WaveModifier.texture_coords_object

Object to set the texture coordinates

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.WaveModifier.time_offset"></a>

#### bpy.types.WaveModifier.time_offset

Either the starting frame (for positive speed) or ending frame (for negative speed) (in [-1.04857e+06, 1.04857e+06], default 0.0)

**Type:**

float

<a id="bpy.types.WaveModifier.use_cyclic"></a>

#### bpy.types.WaveModifier.use_cyclic

Cyclic wave effect (default True)

**Type:**

bool

<a id="bpy.types.WaveModifier.use_normal"></a>

#### bpy.types.WaveModifier.use_normal

Displace along normals (default False)

**Type:**

bool

<a id="bpy.types.WaveModifier.use_normal_x"></a>

#### bpy.types.WaveModifier.use_normal_x

Enable displacement along the X normal (default True)

**Type:**

bool

<a id="bpy.types.WaveModifier.use_normal_y"></a>

#### bpy.types.WaveModifier.use_normal_y

Enable displacement along the Y normal (default True)

**Type:**

bool

<a id="bpy.types.WaveModifier.use_normal_z"></a>

#### bpy.types.WaveModifier.use_normal_z

Enable displacement along the Z normal (default True)

**Type:**

bool

<a id="bpy.types.WaveModifier.use_x"></a>

#### bpy.types.WaveModifier.use_x

X axis motion (default True)

**Type:**

bool

<a id="bpy.types.WaveModifier.use_y"></a>

#### bpy.types.WaveModifier.use_y

Y axis motion (default True)

**Type:**

bool

<a id="bpy.types.WaveModifier.uv_layer"></a>

#### bpy.types.WaveModifier.uv_layer

UV map name (default “”, never None)

**Type:**

str

<a id="bpy.types.WaveModifier.vertex_group"></a>

#### bpy.types.WaveModifier.vertex_group

Vertex group name for modulating the wave (default “”, never None)

**Type:**

str

<a id="bpy.types.WaveModifier.width"></a>

#### bpy.types.WaveModifier.width

Distance between the waves (in [0, inf], default 1.5)

**Type:**

float

<a id="bpy.types.WaveModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.WaveModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.WaveModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.WaveModifier.bl_rna_get_subclass_py(id, default=None, /)

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
