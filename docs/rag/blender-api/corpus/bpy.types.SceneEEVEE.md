<!-- source: Blender Python API reference 5.2 / bpy.types.SceneEEVEE.html -->

<a id="sceneeevee-bpy-struct"></a>

# SceneEEVEE(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.SceneEEVEE"></a>

### class bpy.types.SceneEEVEE(bpy_struct)

Scene display settings for 3D viewport

<a id="bpy.types.SceneEEVEE.bokeh_max_size"></a>

#### bpy.types.SceneEEVEE.bokeh_max_size

Max size of the bokeh shape for the depth of field (lower is faster) (in [0, 2000], default 100.0)

**Type:**

float

<a id="bpy.types.SceneEEVEE.bokeh_neighbor_max"></a>

#### bpy.types.SceneEEVEE.bokeh_neighbor_max

Maximum brightness to consider when rejecting bokeh sprites based on neighborhood (lower is faster) (in [0, 100000], default 10.0)

**Type:**

float

<a id="bpy.types.SceneEEVEE.bokeh_overblur"></a>

#### bpy.types.SceneEEVEE.bokeh_overblur

Apply blur to each jittered sample to reduce under-sampling artifacts (in [0, 100], default 5.0)

**Type:**

float

<a id="bpy.types.SceneEEVEE.bokeh_threshold"></a>

#### bpy.types.SceneEEVEE.bokeh_threshold

Brightness threshold for using sprite base depth of field (in [0, 100000], default 1.0)

**Type:**

float

<a id="bpy.types.SceneEEVEE.clamp_surface_direct"></a>

#### bpy.types.SceneEEVEE.clamp_surface_direct

If non-zero, the maximum value for lights contribution on a surface. Higher values will be scaled down to avoid too much noise and slow convergence at the cost of accuracy. Used by light objects. (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.SceneEEVEE.clamp_surface_indirect"></a>

#### bpy.types.SceneEEVEE.clamp_surface_indirect

If non-zero, the maximum value for indirect lighting on surface. Higher values will be scaled down to avoid too much noise and slow convergence at the cost of accuracy. Used by ray-tracing and light-probes. (in [0, inf], default 10.0)

**Type:**

float

<a id="bpy.types.SceneEEVEE.clamp_volume_direct"></a>

#### bpy.types.SceneEEVEE.clamp_volume_direct

If non-zero, the maximum value for lights contribution in volumes. Higher values will be scaled down to avoid too much noise and slow convergence at the cost of accuracy. Used by light objects. (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.SceneEEVEE.clamp_volume_indirect"></a>

#### bpy.types.SceneEEVEE.clamp_volume_indirect

If non-zero, the maximum value for indirect lighting in volumes. Higher values will be scaled down to avoid too much noise and slow convergence at the cost of accuracy. Used by light-probes. (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.SceneEEVEE.direct_light_intensity"></a>

#### bpy.types.SceneEEVEE.direct_light_intensity

Scale the contribution of direct lighting (in [0, inf], default 1.0)

**Type:**

float

<a id="bpy.types.SceneEEVEE.fast_gi_bias"></a>

#### bpy.types.SceneEEVEE.fast_gi_bias

Bias the shading normal to reduce self intersection artifacts (in [0, 1], default 0.05)

**Type:**

float

<a id="bpy.types.SceneEEVEE.fast_gi_distance"></a>

#### bpy.types.SceneEEVEE.fast_gi_distance

If non-zero, the maximum distance at which other surfaces will contribute to the fast GI approximation (in [0, 100000], default 0.0)

**Type:**

float

<a id="bpy.types.SceneEEVEE.fast_gi_method"></a>

#### bpy.types.SceneEEVEE.fast_gi_method

Fast GI approximation method (default `'GLOBAL_ILLUMINATION'`)

- `AMBIENT_OCCLUSION_ONLY`
  Ambient Occlusion – Use ambient occlusion instead of full global illumination.
- `GLOBAL_ILLUMINATION`
  Global Illumination – Compute global illumination taking into account light bouncing off surrounding objects.

**Type:**

Literal[‘AMBIENT_OCCLUSION_ONLY’, ‘GLOBAL_ILLUMINATION’]

<a id="bpy.types.SceneEEVEE.fast_gi_quality"></a>

#### bpy.types.SceneEEVEE.fast_gi_quality

Precision of the fast GI ray marching (in [0, 1], default 0.25)

**Type:**

float

<a id="bpy.types.SceneEEVEE.fast_gi_ray_count"></a>

#### bpy.types.SceneEEVEE.fast_gi_ray_count

Amount of GI ray to trace for each pixel (in [1, 16], default 2)

**Type:**

int

<a id="bpy.types.SceneEEVEE.fast_gi_resolution"></a>

#### bpy.types.SceneEEVEE.fast_gi_resolution

Control the quality of the fast GI lighting. Higher resolution uses more memory. (default `'2'`)

- `1`
  1:1 – Full resolution.
- `2`
  1:2 – Render this effect at 50% render resolution.
- `4`
  1:4 – Render this effect at 25% render resolution.
- `8`
  1:8 – Render this effect at 12.5% render resolution.
- `16`
  1:16 – Render this effect at 6.25% render resolution.

**Type:**

Literal[‘1’, ‘2’, ‘4’, ‘8’, ‘16’]

<a id="bpy.types.SceneEEVEE.fast_gi_step_count"></a>

#### bpy.types.SceneEEVEE.fast_gi_step_count

Amount of screen sample per GI ray (in [1, 64], default 8)

**Type:**

int

<a id="bpy.types.SceneEEVEE.fast_gi_thickness_near"></a>

#### bpy.types.SceneEEVEE.fast_gi_thickness_near

Geometric thickness of the surfaces when computing fast GI and ambient occlusion. Reduces light leaking and missing contact occlusion. (in [0, 100000], default 0.1)

**Type:**

float

<a id="bpy.types.SceneEEVEE.gi_cubemap_resolution"></a>

#### bpy.types.SceneEEVEE.gi_cubemap_resolution

Size of every cubemaps (default `'512'`)

**Type:**

Literal[‘128’, ‘256’, ‘512’, ‘1024’, ‘2048’, ‘4096’]

<a id="bpy.types.SceneEEVEE.gi_diffuse_bounces"></a>

#### bpy.types.SceneEEVEE.gi_diffuse_bounces

Number of times the light is reinjected inside light grids, 0 disable indirect diffuse light (in [0, inf], default 3)

**Type:**

int

<a id="bpy.types.SceneEEVEE.gi_glossy_clamp"></a>

#### bpy.types.SceneEEVEE.gi_glossy_clamp

Clamp pixel intensity to reduce noise inside glossy reflections from reflection cubemaps (0 to disable) (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.SceneEEVEE.gi_irradiance_pool_size"></a>

#### bpy.types.SceneEEVEE.gi_irradiance_pool_size

Size of the irradiance pool, a bigger pool size allows for more irradiance grid in the scene but might not fit into GPU memory and decrease performance (default `'16'`)

**Type:**

Literal[‘16’, ‘32’, ‘64’, ‘128’, ‘256’, ‘512’, ‘1024’]

<a id="bpy.types.SceneEEVEE.gi_visibility_resolution"></a>

#### bpy.types.SceneEEVEE.gi_visibility_resolution

Size of the shadow map applied to each irradiance sample (default `'32'`)

**Type:**

Literal[‘8’, ‘16’, ‘32’, ‘64’]

<a id="bpy.types.SceneEEVEE.indirect_light_intensity"></a>

#### bpy.types.SceneEEVEE.indirect_light_intensity

Scale the contribution of indirect lighting (in [0, inf], default 1.0)

**Type:**

float

<a id="bpy.types.SceneEEVEE.light_threshold"></a>

#### bpy.types.SceneEEVEE.light_threshold

Minimum light intensity for a light to contribute to the lighting (in [0, inf], default 0.01)

**Type:**

float

<a id="bpy.types.SceneEEVEE.motion_blur_depth_scale"></a>

#### bpy.types.SceneEEVEE.motion_blur_depth_scale

Lower values will reduce background bleeding onto foreground elements (in [0, inf], default 100.0)

**Type:**

float

<a id="bpy.types.SceneEEVEE.motion_blur_max"></a>

#### bpy.types.SceneEEVEE.motion_blur_max

Maximum blur distance a pixel can spread over (in [0, 2048], default 32)

**Type:**

int

<a id="bpy.types.SceneEEVEE.motion_blur_steps"></a>

#### bpy.types.SceneEEVEE.motion_blur_steps

Controls accuracy of motion blur, more steps means longer render time (in [1, inf], default 1)

**Type:**

int

<a id="bpy.types.SceneEEVEE.overscan_size"></a>

#### bpy.types.SceneEEVEE.overscan_size

Percentage of render size to add as overscan to the internal render buffers (in [0, 50], default 3.0)

**Type:**

float

<a id="bpy.types.SceneEEVEE.ray_tracing_method"></a>

#### bpy.types.SceneEEVEE.ray_tracing_method

Select the tracing method used to find scene-ray intersections (default `'SCREEN'`)

- `PROBE`
  Light Probe – Use light probes to find scene intersection.
- `SCREEN`
  Screen-Trace – Raytrace against the depth buffer. Fallback to light probes for invalid rays..

**Type:**

Literal[‘PROBE’, ‘SCREEN’]

<a id="bpy.types.SceneEEVEE.ray_tracing_options"></a>

#### bpy.types.SceneEEVEE.ray_tracing_options

EEVEE settings for tracing reflections (readonly)

**Type:**

[`RaytraceEEVEE`](bpy.types.RaytraceEEVEE.md#bpy.types.RaytraceEEVEE "bpy.types.RaytraceEEVEE") | None

<a id="bpy.types.SceneEEVEE.shadow_pool_size"></a>

#### bpy.types.SceneEEVEE.shadow_pool_size

Size of the shadow pool, a bigger pool size allows for more shadows in the scene but might not fit into GPU memory (default `'512'`)

**Type:**

Literal[‘16’, ‘32’, ‘64’, ‘128’, ‘256’, ‘512’, ‘1024’, ‘1536’, ‘2048’]

<a id="bpy.types.SceneEEVEE.shadow_ray_count"></a>

#### bpy.types.SceneEEVEE.shadow_ray_count

Amount of shadow ray to trace for each light (in [1, 4], default 1)

**Type:**

int

<a id="bpy.types.SceneEEVEE.shadow_resolution_scale"></a>

#### bpy.types.SceneEEVEE.shadow_resolution_scale

Resolution percentage of shadow maps (in [0, 1], default 1.0)

**Type:**

float

<a id="bpy.types.SceneEEVEE.shadow_step_count"></a>

#### bpy.types.SceneEEVEE.shadow_step_count

Amount of shadow map sample per shadow ray (in [1, 16], default 6)

**Type:**

int

<a id="bpy.types.SceneEEVEE.taa_render_samples"></a>

#### bpy.types.SceneEEVEE.taa_render_samples

Number of samples per pixel for rendering (in [1, inf], default 64)

**Type:**

int

<a id="bpy.types.SceneEEVEE.taa_samples"></a>

#### bpy.types.SceneEEVEE.taa_samples

Number of samples, unlimited if 0 (in [0, inf], default 16)

**Type:**

int

<a id="bpy.types.SceneEEVEE.use_bokeh_jittered"></a>

#### bpy.types.SceneEEVEE.use_bokeh_jittered

Jitter camera position to create accurate blurring using render samples (only for final render) (default False)

**Type:**

bool

<a id="bpy.types.SceneEEVEE.use_fast_gi"></a>

#### bpy.types.SceneEEVEE.use_fast_gi

Use faster global illumination technique for high roughness surfaces (default False)

**Type:**

bool

<a id="bpy.types.SceneEEVEE.use_overscan"></a>

#### bpy.types.SceneEEVEE.use_overscan

Internally render past the image border to avoid screen-space effects disappearing (default False)

**Type:**

bool

<a id="bpy.types.SceneEEVEE.use_raytracing"></a>

#### bpy.types.SceneEEVEE.use_raytracing

Enable the ray-tracing module (default False)

**Type:**

bool

<a id="bpy.types.SceneEEVEE.use_shadow_jitter_viewport"></a>

#### bpy.types.SceneEEVEE.use_shadow_jitter_viewport

Enable jittered shadows on the viewport. (Jittered shadows are always enabled for final renders). (default False)

**Type:**

bool

<a id="bpy.types.SceneEEVEE.use_shadows"></a>

#### bpy.types.SceneEEVEE.use_shadows

Enable shadow casting from lights (default True)

**Type:**

bool

<a id="bpy.types.SceneEEVEE.use_taa_reprojection"></a>

#### bpy.types.SceneEEVEE.use_taa_reprojection

Denoise image using temporal reprojection (can leave some ghosting) (default True)

**Type:**

bool

<a id="bpy.types.SceneEEVEE.use_volume_custom_range"></a>

#### bpy.types.SceneEEVEE.use_volume_custom_range

Enable custom start and end clip distances for volume computation (default False)

**Type:**

bool

<a id="bpy.types.SceneEEVEE.use_volumetric_shadows"></a>

#### bpy.types.SceneEEVEE.use_volumetric_shadows

Cast shadows from volumetric materials onto volumetric materials (Very expensive) (default False)

**Type:**

bool

<a id="bpy.types.SceneEEVEE.volumetric_end"></a>

#### bpy.types.SceneEEVEE.volumetric_end

End distance of the volumetric effect (in [1e-06, inf], default 100.0)

**Type:**

float

<a id="bpy.types.SceneEEVEE.volumetric_light_clamp"></a>

#### bpy.types.SceneEEVEE.volumetric_light_clamp

Maximum light contribution, reducing noise (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.SceneEEVEE.volumetric_ray_depth"></a>

#### bpy.types.SceneEEVEE.volumetric_ray_depth

Maximum surface intersection count used by the accurate volume intersection method. Will create artifact if it is exceeded. Higher count increases VRAM usage. (in [1, 16], default 16)

**Type:**

int

<a id="bpy.types.SceneEEVEE.volumetric_sample_distribution"></a>

#### bpy.types.SceneEEVEE.volumetric_sample_distribution

Distribute more samples closer to the camera (in [0, 1], default 0.8)

**Type:**

float

<a id="bpy.types.SceneEEVEE.volumetric_samples"></a>

#### bpy.types.SceneEEVEE.volumetric_samples

Number of steps to compute volumetric effects. Higher step count increase VRAM usage and quality. (in [1, 256], default 64)

**Type:**

int

<a id="bpy.types.SceneEEVEE.volumetric_shadow_samples"></a>

#### bpy.types.SceneEEVEE.volumetric_shadow_samples

Number of samples to compute volumetric shadowing (in [1, 128], default 16)

**Type:**

int

<a id="bpy.types.SceneEEVEE.volumetric_start"></a>

#### bpy.types.SceneEEVEE.volumetric_start

Start distance of the volumetric effect (in [1e-06, inf], default 0.1)

**Type:**

float

<a id="bpy.types.SceneEEVEE.volumetric_tile_size"></a>

#### bpy.types.SceneEEVEE.volumetric_tile_size

Control the quality of the volumetric effects. Higher resolution uses more memory. (default `'8'`)

- `1`
  1:1 – Full resolution.
- `2`
  1:2 – Render this effect at 50% render resolution.
- `4`
  1:4 – Render this effect at 25% render resolution.
- `8`
  1:8 – Render this effect at 12.5% render resolution.
- `16`
  1:16 – Render this effect at 6.25% render resolution.

**Type:**

Literal[‘1’, ‘2’, ‘4’, ‘8’, ‘16’]

<a id="bpy.types.SceneEEVEE.bl_rna_get_subclass"></a>

#### classmethod bpy.types.SceneEEVEE.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.SceneEEVEE.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.SceneEEVEE.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Scene.eevee`](bpy.types.Scene.md#bpy.types.Scene.eevee "bpy.types.Scene.eevee") |  |
