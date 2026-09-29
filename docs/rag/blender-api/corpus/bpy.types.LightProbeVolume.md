<!-- source: Blender Python API reference 5.2 / bpy.types.LightProbeVolume.html -->

<a id="lightprobevolume-lightprobe"></a>

# LightProbeVolume(LightProbe)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID"), [`LightProbe`](bpy.types.LightProbe.md#bpy.types.LightProbe "bpy.types.LightProbe")

<a id="bpy.types.LightProbeVolume"></a>

### class bpy.types.LightProbeVolume(LightProbe)

Light probe that captures low frequency lighting inside a volume

<a id="bpy.types.LightProbeVolume.bake_samples"></a>

#### bpy.types.LightProbeVolume.bake_samples

Number of ray directions to evaluate when baking (in [1, inf], default 2048)

**Type:**

int

<a id="bpy.types.LightProbeVolume.capture_distance"></a>

#### bpy.types.LightProbeVolume.capture_distance

Distance around the probe volume that will be considered during the bake (in [1e-06, inf], default 20.0)

**Type:**

float

<a id="bpy.types.LightProbeVolume.capture_emission"></a>

#### bpy.types.LightProbeVolume.capture_emission

Bake emissive surfaces for more accurate lighting (default True)

**Type:**

bool

<a id="bpy.types.LightProbeVolume.capture_indirect"></a>

#### bpy.types.LightProbeVolume.capture_indirect

Bake light bounces from light sources for more accurate lighting (default True)

**Type:**

bool

<a id="bpy.types.LightProbeVolume.capture_world"></a>

#### bpy.types.LightProbeVolume.capture_world

Bake incoming light from the world instead of just the visibility for more accurate lighting, but lose correct blending to surrounding irradiance volumes (default False)

**Type:**

bool

<a id="bpy.types.LightProbeVolume.clamp_direct"></a>

#### bpy.types.LightProbeVolume.clamp_direct

Clamp the direct lighting intensity to reduce noise (0 to disable) (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.LightProbeVolume.clamp_indirect"></a>

#### bpy.types.LightProbeVolume.clamp_indirect

Clamp the indirect lighting intensity to reduce noise (0 to disable) (in [0, inf], default 10.0)

**Type:**

float

<a id="bpy.types.LightProbeVolume.dilation_radius"></a>

#### bpy.types.LightProbeVolume.dilation_radius

Radius in grid sample to search valid grid samples to copy into invalid grid samples (in [1, 5], default 1.0)

**Type:**

float

<a id="bpy.types.LightProbeVolume.dilation_threshold"></a>

#### bpy.types.LightProbeVolume.dilation_threshold

Ratio of front-facing surface hits under which a grid sample will reuse neighbors grid sample lighting (in [0, 1], default 0.5)

**Type:**

float

<a id="bpy.types.LightProbeVolume.escape_bias"></a>

#### bpy.types.LightProbeVolume.escape_bias

Distance to search for valid capture positions to prevent lighting artifacts (in [0, 1], default 0.1)

**Type:**

float

<a id="bpy.types.LightProbeVolume.facing_bias"></a>

#### bpy.types.LightProbeVolume.facing_bias

Smoother irradiance interpolation but introduce light bleeding (in [0, inf], default 0.5)

**Type:**

float

<a id="bpy.types.LightProbeVolume.intensity"></a>

#### bpy.types.LightProbeVolume.intensity

Modify the intensity of the lighting captured by this probe (in [0, inf], default 1.0)

**Type:**

float

<a id="bpy.types.LightProbeVolume.normal_bias"></a>

#### bpy.types.LightProbeVolume.normal_bias

Offset sampling of the irradiance grid in the surface normal direction to reduce light bleeding (in [0, inf], default 0.3)

**Type:**

float

<a id="bpy.types.LightProbeVolume.resolution_x"></a>

#### bpy.types.LightProbeVolume.resolution_x

Number of samples along the x axis of the volume (in [1, 256], default 4)

**Type:**

int

<a id="bpy.types.LightProbeVolume.resolution_y"></a>

#### bpy.types.LightProbeVolume.resolution_y

Number of samples along the y axis of the volume (in [1, 256], default 4)

**Type:**

int

<a id="bpy.types.LightProbeVolume.resolution_z"></a>

#### bpy.types.LightProbeVolume.resolution_z

Number of samples along the z axis of the volume (in [1, 256], default 4)

**Type:**

int

<a id="bpy.types.LightProbeVolume.surface_bias"></a>

#### bpy.types.LightProbeVolume.surface_bias

Moves capture points away from surfaces to prevent artifacts (in [0, 1], default 0.05)

**Type:**

float

<a id="bpy.types.LightProbeVolume.surfel_density"></a>

#### bpy.types.LightProbeVolume.surfel_density

Number of surfels to spawn in one local unit distance (higher values improve quality) (in [1, inf], default 20)

**Type:**

int

<a id="bpy.types.LightProbeVolume.validity_threshold"></a>

#### bpy.types.LightProbeVolume.validity_threshold

Ratio of front-facing surface hits under which a grid sample will not be considered for lighting (in [0, 1], default 0.4)

**Type:**

float

<a id="bpy.types.LightProbeVolume.view_bias"></a>

#### bpy.types.LightProbeVolume.view_bias

Offset sampling of the irradiance grid in the viewing direction to reduce light bleeding (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.LightProbeVolume.bl_rna_get_subclass"></a>

#### classmethod bpy.types.LightProbeVolume.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.LightProbeVolume.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.LightProbeVolume.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, ID.name, ID.name_full, ID.id_type, ID.session_uid, ID.is_evaluated, ID.original, ID.users, ID.use_fake_user, ID.use_extra_user, ID.is_embedded_data, ID.is_linked_packed, ID.is_missing, ID.is_runtime_data, ID.is_editable, ID.tag, ID.is_library_indirect, ID.library, ID.library_weak_reference, ID.asset_data, ID.override_library, ID.preview, LightProbe.type, LightProbe.clip_start, LightProbe.show_clip, LightProbe.show_influence, LightProbe.influence_distance, LightProbe.visibility_buffer_bias, LightProbe.visibility_bleed_bias, LightProbe.visibility_blur, LightProbe.visibility_collection, LightProbe.invert_visibility_collection, LightProbe.show_data, LightProbe.use_data_display, LightProbe.data_display_size, LightProbe.animation_data

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, ID.bl_system_properties_get, ID.rename, ID.evaluated_get, ID.copy, ID.asset_mark, ID.asset_clear, ID.asset_generate_preview, ID.override_create, ID.override_hierarchy_create, ID.user_clear, ID.user_remap, ID.make_local, ID.user_of_id, ID.animation_data_create, ID.animation_data_clear, ID.update_tag, ID.preview_ensure, ID.bl_rna_get_subclass, ID.bl_rna_get_subclass_py, LightProbe.bl_rna_get_subclass, LightProbe.bl_rna_get_subclass_py
