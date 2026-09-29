<!-- source: Blender Python API reference 5.2 / bpy.types.CameraStereoData.html -->

<a id="camerastereodata-bpy-struct"></a>

# CameraStereoData(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.CameraStereoData"></a>

### class bpy.types.CameraStereoData(bpy_struct)

Stereoscopy settings for a Camera data-block

<a id="bpy.types.CameraStereoData.convergence_distance"></a>

#### bpy.types.CameraStereoData.convergence_distance

The converge point for the stereo cameras (often the distance between a projector and the projection screen) (in [1e-05, inf], default 1.95)

**Type:**

float

<a id="bpy.types.CameraStereoData.convergence_mode"></a>

#### bpy.types.CameraStereoData.convergence_mode

(default `'OFFAXIS'`)

- `OFFAXIS`
  Off-Axis – Off-axis frustums converging in a plane.
- `PARALLEL`
  Parallel – Parallel cameras with no convergence.
- `TOE`
  Toe-in – Rotated cameras, looking at the same point at the convergence distance.

**Type:**

Literal[‘OFFAXIS’, ‘PARALLEL’, ‘TOE’]

<a id="bpy.types.CameraStereoData.interocular_distance"></a>

#### bpy.types.CameraStereoData.interocular_distance

Set the distance between the eyes - the stereo plane distance / 30 should be fine (in [0, inf], default 0.065)

**Type:**

float

<a id="bpy.types.CameraStereoData.pivot"></a>

#### bpy.types.CameraStereoData.pivot

(default `'LEFT'`)

**Type:**

Literal[‘LEFT’, ‘RIGHT’, ‘CENTER’]

<a id="bpy.types.CameraStereoData.pole_merge_angle_from"></a>

#### bpy.types.CameraStereoData.pole_merge_angle_from

Angle at which interocular distance starts to fade to 0 (in [0, 1.5708], default 1.0472)

**Type:**

float

<a id="bpy.types.CameraStereoData.pole_merge_angle_to"></a>

#### bpy.types.CameraStereoData.pole_merge_angle_to

Angle at which interocular distance is 0 (in [0, 1.5708], default 1.309)

**Type:**

float

<a id="bpy.types.CameraStereoData.use_pole_merge"></a>

#### bpy.types.CameraStereoData.use_pole_merge

Fade interocular distance to 0 after the given cutoff angle (default False)

**Type:**

bool

<a id="bpy.types.CameraStereoData.use_spherical_stereo"></a>

#### bpy.types.CameraStereoData.use_spherical_stereo

Render every pixel rotating the camera around the middle of the interocular distance (default False)

**Type:**

bool

<a id="bpy.types.CameraStereoData.bl_rna_get_subclass"></a>

#### classmethod bpy.types.CameraStereoData.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.CameraStereoData.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.CameraStereoData.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Camera.stereo`](bpy.types.Camera.md#bpy.types.Camera.stereo "bpy.types.Camera.stereo") |  |
