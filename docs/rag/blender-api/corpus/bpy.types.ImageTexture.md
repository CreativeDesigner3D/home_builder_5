<!-- source: Blender Python API reference 5.2 / bpy.types.ImageTexture.html -->

<a id="imagetexture-texture"></a>

# ImageTexture(Texture)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID"), [`Texture`](bpy.types.Texture.md#bpy.types.Texture "bpy.types.Texture")

<a id="bpy.types.ImageTexture"></a>

### class bpy.types.ImageTexture(Texture)

<a id="bpy.types.ImageTexture.checker_distance"></a>

#### bpy.types.ImageTexture.checker_distance

Distance between checker tiles (in [0, 0.99], default 0.0)

**Type:**

float

<a id="bpy.types.ImageTexture.crop_max_x"></a>

#### bpy.types.ImageTexture.crop_max_x

Maximum X value to crop the image (in [-10, 10], default 1.0)

**Type:**

float

<a id="bpy.types.ImageTexture.crop_max_y"></a>

#### bpy.types.ImageTexture.crop_max_y

Maximum Y value to crop the image (in [-10, 10], default 1.0)

**Type:**

float

<a id="bpy.types.ImageTexture.crop_min_x"></a>

#### bpy.types.ImageTexture.crop_min_x

Minimum X value to crop the image (in [-10, 10], default 0.0)

**Type:**

float

<a id="bpy.types.ImageTexture.crop_min_y"></a>

#### bpy.types.ImageTexture.crop_min_y

Minimum Y value to crop the image (in [-10, 10], default 0.0)

**Type:**

float

<a id="bpy.types.ImageTexture.extension"></a>

#### bpy.types.ImageTexture.extension

How the image is extrapolated past its original bounds (default `'REPEAT'`)

- `EXTEND`
  Extend – Extend by repeating edge pixels of the image.
- `CLIP`
  Clip – Clip to image size and set exterior pixels as transparent.
- `CLIP_CUBE`
  Clip Cube – Clip to cubic-shaped area around the image and set exterior pixels as transparent.
- `REPEAT`
  Repeat – Cause the image to repeat horizontally and vertically.
- `CHECKER`
  Checker – Cause the image to repeat in checker board pattern.

**Type:**

Literal[‘EXTEND’, ‘CLIP’, ‘CLIP_CUBE’, ‘REPEAT’, ‘CHECKER’]

<a id="bpy.types.ImageTexture.filter_size"></a>

#### bpy.types.ImageTexture.filter_size

Multiply the filter size used by interpolation (in [0.1, 50], default 1.0)

**Type:**

float

<a id="bpy.types.ImageTexture.image"></a>

#### bpy.types.ImageTexture.image

**Type:**

[`Image`](bpy.types.Image.md#bpy.types.Image "bpy.types.Image") | None

<a id="bpy.types.ImageTexture.image_user"></a>

#### bpy.types.ImageTexture.image_user

Parameters defining which layer, pass and frame of the image is displayed (readonly)

**Type:**

[`ImageUser`](bpy.types.ImageUser.md#bpy.types.ImageUser "bpy.types.ImageUser") | None

<a id="bpy.types.ImageTexture.invert_alpha"></a>

#### bpy.types.ImageTexture.invert_alpha

Invert all the alpha values in the image (default False)

**Type:**

bool

<a id="bpy.types.ImageTexture.repeat_x"></a>

#### bpy.types.ImageTexture.repeat_x

Repetition multiplier in the X direction (in [1, 512], default 1)

**Type:**

int

<a id="bpy.types.ImageTexture.repeat_y"></a>

#### bpy.types.ImageTexture.repeat_y

Repetition multiplier in the Y direction (in [1, 512], default 1)

**Type:**

int

<a id="bpy.types.ImageTexture.use_alpha"></a>

#### bpy.types.ImageTexture.use_alpha

Use the alpha channel information in the image (default True)

**Type:**

bool

<a id="bpy.types.ImageTexture.use_calculate_alpha"></a>

#### bpy.types.ImageTexture.use_calculate_alpha

Calculate an alpha channel based on RGB values in the image (default False)

**Type:**

bool

<a id="bpy.types.ImageTexture.use_checker_even"></a>

#### bpy.types.ImageTexture.use_checker_even

Even checker tiles (default False)

**Type:**

bool

<a id="bpy.types.ImageTexture.use_checker_odd"></a>

#### bpy.types.ImageTexture.use_checker_odd

Odd checker tiles (default True)

**Type:**

bool

<a id="bpy.types.ImageTexture.use_flip_axis"></a>

#### bpy.types.ImageTexture.use_flip_axis

Flip the texture’s X and Y axis (default False)

**Type:**

bool

<a id="bpy.types.ImageTexture.use_interpolation"></a>

#### bpy.types.ImageTexture.use_interpolation

Interpolate pixels using selected filter (default True)

**Type:**

bool

<a id="bpy.types.ImageTexture.use_mirror_x"></a>

#### bpy.types.ImageTexture.use_mirror_x

Mirror the image repetition on the X direction (default False)

**Type:**

bool

<a id="bpy.types.ImageTexture.use_mirror_y"></a>

#### bpy.types.ImageTexture.use_mirror_y

Mirror the image repetition on the Y direction (default False)

**Type:**

bool

<a id="bpy.types.ImageTexture.use_normal_map"></a>

#### bpy.types.ImageTexture.use_normal_map

Use image RGB values for normal mapping (default False)

**Type:**

bool

<a id="bpy.types.ImageTexture.users_material"></a>

#### bpy.types.ImageTexture.users_material

Materials that use this texture

**Type:**

tuple[[`Material`](bpy.types.Material.md#bpy.types.Material "bpy.types.Material"), …]

> **Note:**
>
> Takes `O(len(bpy.data.materials) * len(material.texture_slots))` time.

(readonly)

<a id="bpy.types.ImageTexture.users_object_modifier"></a>

#### bpy.types.ImageTexture.users_object_modifier

Object modifiers that use this texture

**Type:**

tuple[[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object"), …]

> **Note:**
>
> Takes `O(len(bpy.data.objects) * len(obj.modifiers))` time.

(readonly)

<a id="bpy.types.ImageTexture.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ImageTexture.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ImageTexture.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ImageTexture.bl_rna_get_subclass_py(id, default=None, /)

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
