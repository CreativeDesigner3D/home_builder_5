<!-- source: Blender Python API reference 5.2 / bpy.types.SunLight.html -->

<a id="sunlight-light"></a>

# SunLight(Light)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID"), [`Light`](bpy.types.Light.md#bpy.types.Light "bpy.types.Light")

<a id="bpy.types.SunLight"></a>

### class bpy.types.SunLight(Light)

Constant direction parallel ray Light

<a id="bpy.types.SunLight.angle"></a>

#### bpy.types.SunLight.angle

Angular diameter of the Sun as seen from the Earth (in [0, 3.14159], default 0.00918043)

**Type:**

float

<a id="bpy.types.SunLight.energy"></a>

#### bpy.types.SunLight.energy

Sunlight strength in watts per meter squared (W/m²) (in [-inf, inf], default 10.0)

**Type:**

float

<a id="bpy.types.SunLight.shadow_buffer_clip_start"></a>

#### bpy.types.SunLight.shadow_buffer_clip_start

Shadow map clip start, below which objects will not generate shadows (in [1e-06, inf], default 0.05)

**Type:**

float

<a id="bpy.types.SunLight.shadow_cascade_count"></a>

#### bpy.types.SunLight.shadow_cascade_count

Number of texture used by the cascaded shadow map (in [1, 4], default 4)

**Type:**

int

<a id="bpy.types.SunLight.shadow_cascade_exponent"></a>

#### bpy.types.SunLight.shadow_cascade_exponent

Higher value increase resolution towards the viewpoint (in [0, 1], default 0.8)

**Type:**

float

<a id="bpy.types.SunLight.shadow_cascade_fade"></a>

#### bpy.types.SunLight.shadow_cascade_fade

How smooth is the transition between each cascade (in [0, 1], default 0.1)

**Type:**

float

<a id="bpy.types.SunLight.shadow_cascade_max_distance"></a>

#### bpy.types.SunLight.shadow_cascade_max_distance

End distance of the cascaded shadow map (only in perspective view) (in [0, inf], default 200.0)

**Type:**

float

<a id="bpy.types.SunLight.shadow_filter_radius"></a>

#### bpy.types.SunLight.shadow_filter_radius

Blur shadow aliasing using Percentage Closer Filtering (in [0, inf], default 1.0)

**Type:**

float

<a id="bpy.types.SunLight.shadow_jitter_overblur"></a>

#### bpy.types.SunLight.shadow_jitter_overblur

Apply shadow tracing to each jittered sample to reduce under-sampling artifacts (in [0, 100], default 10.0)

**Type:**

float

<a id="bpy.types.SunLight.shadow_maximum_resolution"></a>

#### bpy.types.SunLight.shadow_maximum_resolution

Minimum size of a shadow map pixel. Higher values use less memory at the cost of shadow quality. (in [0, inf], default 0.001)

**Type:**

float

<a id="bpy.types.SunLight.shadow_soft_size"></a>

#### bpy.types.SunLight.shadow_soft_size

Light size for ray shadow sampling (Raytraced shadows) (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.SunLight.use_shadow_jitter"></a>

#### bpy.types.SunLight.use_shadow_jitter

Enable jittered soft shadows to increase shadow precision (disabled in viewport unless enabled in the render settings). Has a high performance impact. (default False)

**Type:**

bool

<a id="bpy.types.SunLight.bl_rna_get_subclass"></a>

#### classmethod bpy.types.SunLight.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.SunLight.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.SunLight.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, ID.name, ID.name_full, ID.id_type, ID.session_uid, ID.is_evaluated, ID.original, ID.users, ID.use_fake_user, ID.use_extra_user, ID.is_embedded_data, ID.is_linked_packed, ID.is_missing, ID.is_runtime_data, ID.is_editable, ID.tag, ID.is_library_indirect, ID.library, ID.library_weak_reference, ID.asset_data, ID.override_library, ID.preview, Light.type, Light.use_temperature, Light.color, Light.temperature, Light.temperature_color, Light.specular_factor, Light.diffuse_factor, Light.transmission_factor, Light.volume_factor, Light.use_custom_distance, Light.cutoff_distance, Light.use_shadow, Light.exposure, Light.normalize, Light.node_tree, Light.use_nodes, Light.animation_data, Light.cycles

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, ID.bl_system_properties_get, ID.rename, ID.evaluated_get, ID.copy, ID.asset_mark, ID.asset_clear, ID.asset_generate_preview, ID.override_create, ID.override_hierarchy_create, ID.user_clear, ID.user_remap, ID.make_local, ID.user_of_id, ID.animation_data_create, ID.animation_data_clear, ID.update_tag, ID.preview_ensure, ID.bl_rna_get_subclass, ID.bl_rna_get_subclass_py, Light.area, Light.inline_shader_nodes, Light.bl_rna_get_subclass, Light.bl_rna_get_subclass_py
