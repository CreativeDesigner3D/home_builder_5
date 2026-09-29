<!-- source: Blender Python API reference 5.2 / bpy.types.SceneDisplay.html -->

<a id="scenedisplay-bpy-struct"></a>

# SceneDisplay(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.SceneDisplay"></a>

### class bpy.types.SceneDisplay(bpy_struct)

Scene display settings for 3D viewport

<a id="bpy.types.SceneDisplay.light_direction"></a>

#### bpy.types.SceneDisplay.light_direction

Direction of the light for shadows and highlights (array of 3 items, in [-inf, inf], default (0.57735, 0.57735, 0.57735))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.SceneDisplay.matcap_ssao_attenuation"></a>

#### bpy.types.SceneDisplay.matcap_ssao_attenuation

Attenuation constant (in [0, 100000], default 1.0)

**Type:**

float

<a id="bpy.types.SceneDisplay.matcap_ssao_distance"></a>

#### bpy.types.SceneDisplay.matcap_ssao_distance

Distance of object that contribute to the cavity/edge effect (in [0, 100000], default 0.2)

**Type:**

float

<a id="bpy.types.SceneDisplay.matcap_ssao_samples"></a>

#### bpy.types.SceneDisplay.matcap_ssao_samples

Number of samples (in [1, 500], default 16)

**Type:**

int

<a id="bpy.types.SceneDisplay.render_aa"></a>

#### bpy.types.SceneDisplay.render_aa

Method of anti-aliasing when rendering final image (default `'8'`)

- `OFF`
  No Anti-Aliasing – Scene will be rendering without any anti-aliasing.
- `FXAA`
  Single Pass Anti-Aliasing – Scene will be rendered using a single pass anti-aliasing method (FXAA).
- `5`
  5 Samples – Scene will be rendered using 5 anti-aliasing samples.
- `8`
  8 Samples – Scene will be rendered using 8 anti-aliasing samples.
- `11`
  11 Samples – Scene will be rendered using 11 anti-aliasing samples.
- `16`
  16 Samples – Scene will be rendered using 16 anti-aliasing samples.
- `32`
  32 Samples – Scene will be rendered using 32 anti-aliasing samples.

**Type:**

Literal[‘OFF’, ‘FXAA’, ‘5’, ‘8’, ‘11’, ‘16’, ‘32’]

<a id="bpy.types.SceneDisplay.shading"></a>

#### bpy.types.SceneDisplay.shading

Shading settings for OpenGL render engine (readonly)

**Type:**

[`View3DShading`](bpy.types.View3DShading.md#bpy.types.View3DShading "bpy.types.View3DShading") | None

<a id="bpy.types.SceneDisplay.shadow_focus"></a>

#### bpy.types.SceneDisplay.shadow_focus

Shadow factor hardness (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.SceneDisplay.shadow_shift"></a>

#### bpy.types.SceneDisplay.shadow_shift

Shadow termination angle (in [0, 1], default 0.1)

**Type:**

float

<a id="bpy.types.SceneDisplay.viewport_aa"></a>

#### bpy.types.SceneDisplay.viewport_aa

Method of anti-aliasing when rendering 3d viewport (default `'FXAA'`)

- `OFF`
  No Anti-Aliasing – Scene will be rendering without any anti-aliasing.
- `FXAA`
  Single Pass Anti-Aliasing – Scene will be rendered using a single pass anti-aliasing method (FXAA).
- `5`
  5 Samples – Scene will be rendered using 5 anti-aliasing samples.
- `8`
  8 Samples – Scene will be rendered using 8 anti-aliasing samples.
- `11`
  11 Samples – Scene will be rendered using 11 anti-aliasing samples.
- `16`
  16 Samples – Scene will be rendered using 16 anti-aliasing samples.
- `32`
  32 Samples – Scene will be rendered using 32 anti-aliasing samples.

**Type:**

Literal[‘OFF’, ‘FXAA’, ‘5’, ‘8’, ‘11’, ‘16’, ‘32’]

<a id="bpy.types.SceneDisplay.bl_rna_get_subclass"></a>

#### classmethod bpy.types.SceneDisplay.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.SceneDisplay.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.SceneDisplay.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Scene.display`](bpy.types.Scene.md#bpy.types.Scene.display "bpy.types.Scene.display") |  |
