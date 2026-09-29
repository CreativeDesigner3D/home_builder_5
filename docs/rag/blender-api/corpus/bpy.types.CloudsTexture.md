<!-- source: Blender Python API reference 5.2 / bpy.types.CloudsTexture.html -->

<a id="cloudstexture-texture"></a>

# CloudsTexture(Texture)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID"), [`Texture`](bpy.types.Texture.md#bpy.types.Texture "bpy.types.Texture")

<a id="bpy.types.CloudsTexture"></a>

### class bpy.types.CloudsTexture(Texture)

Procedural noise texture

<a id="bpy.types.CloudsTexture.cloud_type"></a>

#### bpy.types.CloudsTexture.cloud_type

Determine whether Noise returns grayscale or RGB values (default `'GRAYSCALE'`)

**Type:**

Literal[‘GRAYSCALE’, ‘COLOR’]

<a id="bpy.types.CloudsTexture.nabla"></a>

#### bpy.types.CloudsTexture.nabla

Size of derivative offset used for calculating normal (in [0.001, 0.1], default 0.025)

**Type:**

float

<a id="bpy.types.CloudsTexture.noise_basis"></a>

#### bpy.types.CloudsTexture.noise_basis

Noise basis used for turbulence (default `'BLENDER_ORIGINAL'`)

- `BLENDER_ORIGINAL`
  Blender Original – Noise algorithm - Blender original: Smooth interpolated noise.
- `ORIGINAL_PERLIN`
  Original Perlin – Noise algorithm - Original Perlin: Smooth interpolated noise.
- `IMPROVED_PERLIN`
  Improved Perlin – Noise algorithm - Improved Perlin: Smooth interpolated noise.
- `VORONOI_F1`
  Voronoi F1 – Noise algorithm - Voronoi F1: Returns distance to the closest feature point.
- `VORONOI_F2`
  Voronoi F2 – Noise algorithm - Voronoi F2: Returns distance to the 2nd closest feature point.
- `VORONOI_F3`
  Voronoi F3 – Noise algorithm - Voronoi F3: Returns distance to the 3rd closest feature point.
- `VORONOI_F4`
  Voronoi F4 – Noise algorithm - Voronoi F4: Returns distance to the 4th closest feature point.
- `VORONOI_F2_F1`
  Voronoi F2-F1 – Noise algorithm - Voronoi F1-F2.
- `VORONOI_CRACKLE`
  Voronoi Crackle – Noise algorithm - Voronoi Crackle: Voronoi tessellation with sharp edges.
- `CELL_NOISE`
  Cell Noise – Noise algorithm - Cell Noise: Square cell tessellation.

**Type:**

Literal[‘BLENDER_ORIGINAL’, ‘ORIGINAL_PERLIN’, ‘IMPROVED_PERLIN’, ‘VORONOI_F1’, ‘VORONOI_F2’, ‘VORONOI_F3’, ‘VORONOI_F4’, ‘VORONOI_F2_F1’, ‘VORONOI_CRACKLE’, ‘CELL_NOISE’]

<a id="bpy.types.CloudsTexture.noise_depth"></a>

#### bpy.types.CloudsTexture.noise_depth

Depth of the cloud calculation (in [0, 30], default 2)

**Type:**

int

<a id="bpy.types.CloudsTexture.noise_scale"></a>

#### bpy.types.CloudsTexture.noise_scale

Scaling for noise input (in [0.0001, inf], default 0.25)

**Type:**

float

<a id="bpy.types.CloudsTexture.noise_type"></a>

#### bpy.types.CloudsTexture.noise_type

(default `'SOFT_NOISE'`)

- `SOFT_NOISE`
  Soft – Generate soft noise (smooth transitions).
- `HARD_NOISE`
  Hard – Generate hard noise (sharp transitions).

**Type:**

Literal[‘SOFT_NOISE’, ‘HARD_NOISE’]

<a id="bpy.types.CloudsTexture.users_material"></a>

#### bpy.types.CloudsTexture.users_material

Materials that use this texture

**Type:**

tuple[[`Material`](bpy.types.Material.md#bpy.types.Material "bpy.types.Material"), …]

> **Note:**
>
> Takes `O(len(bpy.data.materials) * len(material.texture_slots))` time.

(readonly)

<a id="bpy.types.CloudsTexture.users_object_modifier"></a>

#### bpy.types.CloudsTexture.users_object_modifier

Object modifiers that use this texture

**Type:**

tuple[[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object"), …]

> **Note:**
>
> Takes `O(len(bpy.data.objects) * len(obj.modifiers))` time.

(readonly)

<a id="bpy.types.CloudsTexture.bl_rna_get_subclass"></a>

#### classmethod bpy.types.CloudsTexture.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.CloudsTexture.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.CloudsTexture.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, ID.name, ID.name_full, ID.id_type, ID.session_uid, ID.is_evaluated, ID.original, ID.users, ID.use_fake_user, ID.use_extra_user, ID.is_embedded_data, ID.is_linked_packed, ID.is_missing, ID.is_runtime_data, ID.is_editable, ID.tag, ID.is_library_indirect, ID.library, ID.library_weak_reference, ID.asset_data, ID.override_library, ID.preview, Texture.type, Texture.use_clamp, Texture.use_color_ramp, Texture.color_ramp, Texture.intensity, Texture.contrast, Texture.saturation, Texture.factor_red, Texture.factor_green, Texture.factor_blue, Texture.use_preview_alpha, Texture.use_nodes, Texture.node_tree, Texture.animation_data, Texture.users_material, Texture.users_object_modifier

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, ID.bl_system_properties_get, ID.rename, ID.evaluated_get, ID.copy, ID.asset_mark, ID.asset_clear, ID.asset_generate_preview, ID.override_create, ID.override_hierarchy_create, ID.user_clear, ID.user_remap, ID.make_local, ID.user_of_id, ID.animation_data_create, ID.animation_data_clear, ID.update_tag, ID.preview_ensure, ID.bl_rna_get_subclass, ID.bl_rna_get_subclass_py, Texture.evaluate, Texture.bl_rna_get_subclass, Texture.bl_rna_get_subclass_py
