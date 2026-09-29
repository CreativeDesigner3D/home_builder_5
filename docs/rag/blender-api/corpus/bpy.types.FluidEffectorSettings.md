<!-- source: Blender Python API reference 5.2 / bpy.types.FluidEffectorSettings.html -->

<a id="fluideffectorsettings-bpy-struct"></a>

# FluidEffectorSettings(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.FluidEffectorSettings"></a>

### class bpy.types.FluidEffectorSettings(bpy_struct)

Smoke collision settings

<a id="bpy.types.FluidEffectorSettings.effector_type"></a>

#### bpy.types.FluidEffectorSettings.effector_type

Change type of effector in the simulation (default `'COLLISION'`)

- `COLLISION`
  Collision – Create collision object.
- `GUIDE`
  Guide – Create guide object.

**Type:**

Literal[‘COLLISION’, ‘GUIDE’]

<a id="bpy.types.FluidEffectorSettings.guide_mode"></a>

#### bpy.types.FluidEffectorSettings.guide_mode

How to create guiding velocities (default `'OVERRIDE'`)

- `MAXIMUM`
  Maximize – Compare velocities from previous frame with new velocities from current frame and keep the maximum.
- `MINIMUM`
  Minimize – Compare velocities from previous frame with new velocities from current frame and keep the minimum.
- `OVERRIDE`
  Override – Always write new guide velocities for every frame (each frame only contains current velocities from guiding objects).
- `AVERAGED`
  Averaged – Take average of velocities from previous frame and new velocities from current frame.

**Type:**

Literal[‘MAXIMUM’, ‘MINIMUM’, ‘OVERRIDE’, ‘AVERAGED’]

<a id="bpy.types.FluidEffectorSettings.subframes"></a>

#### bpy.types.FluidEffectorSettings.subframes

Number of additional samples to take between frames to improve quality of fast moving effector objects (in [0, 200], default 0)

**Type:**

int

<a id="bpy.types.FluidEffectorSettings.surface_distance"></a>

#### bpy.types.FluidEffectorSettings.surface_distance

Additional distance around mesh surface to consider as effector (in [0, 10], default 0.0)

**Type:**

float

<a id="bpy.types.FluidEffectorSettings.use_effector"></a>

#### bpy.types.FluidEffectorSettings.use_effector

Control when to apply the effector (default True)

**Type:**

bool

<a id="bpy.types.FluidEffectorSettings.use_plane_init"></a>

#### bpy.types.FluidEffectorSettings.use_plane_init

Treat this object as a planar, unclosed mesh (default False)

**Type:**

bool

<a id="bpy.types.FluidEffectorSettings.velocity_factor"></a>

#### bpy.types.FluidEffectorSettings.velocity_factor

Multiplier of obstacle velocity (in [-100, 100], default 1.0)

**Type:**

float

<a id="bpy.types.FluidEffectorSettings.bl_rna_get_subclass"></a>

#### classmethod bpy.types.FluidEffectorSettings.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.FluidEffectorSettings.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.FluidEffectorSettings.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`FluidModifier.effector_settings`](bpy.types.FluidModifier.md#bpy.types.FluidModifier.effector_settings "bpy.types.FluidModifier.effector_settings") |  |
