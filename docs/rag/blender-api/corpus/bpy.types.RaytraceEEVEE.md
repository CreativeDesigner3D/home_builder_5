<!-- source: Blender Python API reference 5.2 / bpy.types.RaytraceEEVEE.html -->

<a id="raytraceeevee-bpy-struct"></a>

# RaytraceEEVEE(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.RaytraceEEVEE"></a>

### class bpy.types.RaytraceEEVEE(bpy_struct)

Quality options for the raytracing pipeline

<a id="bpy.types.RaytraceEEVEE.backface_radiance_scale"></a>

#### bpy.types.RaytraceEEVEE.backface_radiance_scale

Amount of the front face lighting to reuse for backface lighting approximation (in [0, 1], default 0.25)

**Type:**

float

<a id="bpy.types.RaytraceEEVEE.denoise_bilateral"></a>

#### bpy.types.RaytraceEEVEE.denoise_bilateral

Blur the resolved radiance using a bilateral filter (default True)

**Type:**

bool

<a id="bpy.types.RaytraceEEVEE.denoise_spatial"></a>

#### bpy.types.RaytraceEEVEE.denoise_spatial

Reuse neighbor pixels’ rays (default True)

**Type:**

bool

<a id="bpy.types.RaytraceEEVEE.denoise_temporal"></a>

#### bpy.types.RaytraceEEVEE.denoise_temporal

Accumulate samples by reprojecting last tracing results (default True)

**Type:**

bool

<a id="bpy.types.RaytraceEEVEE.resolution_scale"></a>

#### bpy.types.RaytraceEEVEE.resolution_scale

Determines the number of rays per pixel. Higher resolution uses more memory. (default `'2'`)

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

<a id="bpy.types.RaytraceEEVEE.screen_trace_quality"></a>

#### bpy.types.RaytraceEEVEE.screen_trace_quality

Precision of the screen space ray-tracing (in [0, 1], default 0.25)

**Type:**

float

<a id="bpy.types.RaytraceEEVEE.screen_trace_thickness"></a>

#### bpy.types.RaytraceEEVEE.screen_trace_thickness

Surface thickness used to detect intersection when using screen-tracing (in [1e-06, inf], default 0.1)

**Type:**

float

<a id="bpy.types.RaytraceEEVEE.trace_max_roughness"></a>

#### bpy.types.RaytraceEEVEE.trace_max_roughness

Maximum roughness to use the tracing pipeline for. Higher roughness surfaces will use fast GI approximation. A value of 1 will disable fast GI approximation. (in [0, 1], default 0.5)

**Type:**

float

<a id="bpy.types.RaytraceEEVEE.use_backface_hit"></a>

#### bpy.types.RaytraceEEVEE.use_backface_hit

Consider rays hitting backfaces as valid (default True)

**Type:**

bool

<a id="bpy.types.RaytraceEEVEE.use_denoise"></a>

#### bpy.types.RaytraceEEVEE.use_denoise

Enable noise reduction techniques for raytraced effects (default True)

**Type:**

bool

<a id="bpy.types.RaytraceEEVEE.bl_rna_get_subclass"></a>

#### classmethod bpy.types.RaytraceEEVEE.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.RaytraceEEVEE.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.RaytraceEEVEE.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`SceneEEVEE.ray_tracing_options`](bpy.types.SceneEEVEE.md#bpy.types.SceneEEVEE.ray_tracing_options "bpy.types.SceneEEVEE.ray_tracing_options") |  |
