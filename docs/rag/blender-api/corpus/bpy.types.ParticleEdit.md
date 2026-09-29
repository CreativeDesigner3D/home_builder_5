<!-- source: Blender Python API reference 5.2 / bpy.types.ParticleEdit.html -->

<a id="particleedit-bpy-struct"></a>

# ParticleEdit(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.ParticleEdit"></a>

### class bpy.types.ParticleEdit(bpy_struct)

Properties of particle editing mode

<a id="bpy.types.ParticleEdit.brush"></a>

#### bpy.types.ParticleEdit.brush

(readonly)

**Type:**

[`ParticleBrush`](bpy.types.ParticleBrush.md#bpy.types.ParticleBrush "bpy.types.ParticleBrush") | None

<a id="bpy.types.ParticleEdit.default_key_count"></a>

#### bpy.types.ParticleEdit.default_key_count

How many keys to make new particles with (in [2, 32767], default 5)

**Type:**

int

<a id="bpy.types.ParticleEdit.display_step"></a>

#### bpy.types.ParticleEdit.display_step

How many steps to display the path with (in [1, 10], default 2)

**Type:**

int

<a id="bpy.types.ParticleEdit.emitter_distance"></a>

#### bpy.types.ParticleEdit.emitter_distance

Distance to keep particles away from the emitter (in [-inf, inf], default 0.25)

**Type:**

float

<a id="bpy.types.ParticleEdit.fade_frames"></a>

#### bpy.types.ParticleEdit.fade_frames

How many frames to fade (in [1, 100], default 2)

**Type:**

int

<a id="bpy.types.ParticleEdit.is_editable"></a>

#### bpy.types.ParticleEdit.is_editable

A valid edit mode exists (default False, readonly)

**Type:**

bool

<a id="bpy.types.ParticleEdit.is_hair"></a>

#### bpy.types.ParticleEdit.is_hair

Editing hair (default False, readonly)

**Type:**

bool

<a id="bpy.types.ParticleEdit.object"></a>

#### bpy.types.ParticleEdit.object

The edited object (readonly)

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.ParticleEdit.select_mode"></a>

#### bpy.types.ParticleEdit.select_mode

Particle select and display mode (default `'PATH'`)

- `PATH`
  Path – Path edit mode.
- `POINT`
  Point – Point select mode.
- `TIP`
  Tip – Tip select mode.

**Type:**

Literal[‘PATH’, ‘POINT’, ‘TIP’]

<a id="bpy.types.ParticleEdit.shape_object"></a>

#### bpy.types.ParticleEdit.shape_object

Outer shape to use for tools

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.ParticleEdit.show_particles"></a>

#### bpy.types.ParticleEdit.show_particles

Display actual particles (default False)

**Type:**

bool

<a id="bpy.types.ParticleEdit.tool"></a>

#### bpy.types.ParticleEdit.tool

(default `'COMB'`)

- `COMB`
  Comb – Comb hairs.
- `SMOOTH`
  Smooth – Smooth hairs.
- `ADD`
  Add – Add hairs.
- `LENGTH`
  Length – Make hairs longer or shorter.
- `PUFF`
  Puff – Make hairs stand up.
- `CUT`
  Cut – Cut hairs.
- `WEIGHT`
  Weight – Weight hair particles.

**Type:**

Literal[‘COMB’, ‘SMOOTH’, ‘ADD’, ‘LENGTH’, ‘PUFF’, ‘CUT’, ‘WEIGHT’]

<a id="bpy.types.ParticleEdit.type"></a>

#### bpy.types.ParticleEdit.type

(default `'PARTICLES'`)

**Type:**

Literal[‘PARTICLES’, ‘SOFT_BODY’, ‘CLOTH’]

<a id="bpy.types.ParticleEdit.use_auto_velocity"></a>

#### bpy.types.ParticleEdit.use_auto_velocity

Calculate point velocities automatically (default True)

**Type:**

bool

<a id="bpy.types.ParticleEdit.use_default_interpolate"></a>

#### bpy.types.ParticleEdit.use_default_interpolate

Interpolate new particles from the existing ones (default False)

**Type:**

bool

<a id="bpy.types.ParticleEdit.use_emitter_deflect"></a>

#### bpy.types.ParticleEdit.use_emitter_deflect

Keep paths from intersecting the emitter (default True)

**Type:**

bool

<a id="bpy.types.ParticleEdit.use_fade_time"></a>

#### bpy.types.ParticleEdit.use_fade_time

Fade paths and keys further away from current frame (default False)

**Type:**

bool

<a id="bpy.types.ParticleEdit.use_preserve_length"></a>

#### bpy.types.ParticleEdit.use_preserve_length

Keep path lengths constant (default True)

**Type:**

bool

<a id="bpy.types.ParticleEdit.use_preserve_root"></a>

#### bpy.types.ParticleEdit.use_preserve_root

Keep root keys unmodified (default True)

**Type:**

bool

<a id="bpy.types.ParticleEdit.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ParticleEdit.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ParticleEdit.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ParticleEdit.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([type](#bpy.types.ParticleEdit.type "bpy.types.ParticleEdit.type") | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

[type](#bpy.types.ParticleEdit.type "bpy.types.ParticleEdit.type")

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
| - [`ToolSettings.particle_edit`](bpy.types.ToolSettings.md#bpy.types.ToolSettings.particle_edit "bpy.types.ToolSettings.particle_edit") |  |
