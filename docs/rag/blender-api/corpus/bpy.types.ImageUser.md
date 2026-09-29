<!-- source: Blender Python API reference 5.2 / bpy.types.ImageUser.html -->

<a id="imageuser-bpy-struct"></a>

# ImageUser(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.ImageUser"></a>

### class bpy.types.ImageUser(bpy_struct)

Parameters defining how an Image data-block is used by another data-block

<a id="bpy.types.ImageUser.frame_current"></a>

#### bpy.types.ImageUser.frame_current

Current frame number in image sequence or movie (in [-1048574, 1048574], default 0)

**Type:**

int

<a id="bpy.types.ImageUser.frame_duration"></a>

#### bpy.types.ImageUser.frame_duration

Number of images of a movie to use (in [0, 1048574], default 0)

**Type:**

int

<a id="bpy.types.ImageUser.frame_offset"></a>

#### bpy.types.ImageUser.frame_offset

Offset the number of the frame to use in the animation (in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.ImageUser.frame_start"></a>

#### bpy.types.ImageUser.frame_start

Global starting frame of the movie/sequence, assuming first picture has a #1 (in [-1048574, 1048574], default 0)

**Type:**

int

<a id="bpy.types.ImageUser.multilayer_layer"></a>

#### bpy.types.ImageUser.multilayer_layer

Layer in multilayer image (in [0, 32767], default 0, readonly)

**Type:**

int

<a id="bpy.types.ImageUser.multilayer_pass"></a>

#### bpy.types.ImageUser.multilayer_pass

Pass in multilayer image (in [0, 32767], default 0, readonly)

**Type:**

int

<a id="bpy.types.ImageUser.multilayer_view"></a>

#### bpy.types.ImageUser.multilayer_view

View in multilayer image (in [0, 32767], default 0, readonly)

**Type:**

int

<a id="bpy.types.ImageUser.tile"></a>

#### bpy.types.ImageUser.tile

Tile in tiled image (in [0, inf], default 0)

**Type:**

int

<a id="bpy.types.ImageUser.use_auto_refresh"></a>

#### bpy.types.ImageUser.use_auto_refresh

Always refresh image on frame changes (default False)

**Type:**

bool

<a id="bpy.types.ImageUser.use_cyclic"></a>

#### bpy.types.ImageUser.use_cyclic

Cycle the images in the movie (default False)

**Type:**

bool

<a id="bpy.types.ImageUser.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ImageUser.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ImageUser.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ImageUser.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`CameraBackgroundImage.image_user`](bpy.types.CameraBackgroundImage.md#bpy.types.CameraBackgroundImage.image_user "bpy.types.CameraBackgroundImage.image_user") - [`Image.filepath_from_user`](bpy.types.Image.md#bpy.types.Image.filepath_from_user "bpy.types.Image.filepath_from_user") - [`ImageTexture.image_user`](bpy.types.ImageTexture.md#bpy.types.ImageTexture.image_user "bpy.types.ImageTexture.image_user") - [`Object.image_user`](bpy.types.Object.md#bpy.types.Object.image_user "bpy.types.Object.image_user") - [`RenderSlot.clear`](bpy.types.RenderSlot.md#bpy.types.RenderSlot.clear "bpy.types.RenderSlot.clear") - [`ShaderNodeTexEnvironment.image_user`](bpy.types.ShaderNodeTexEnvironment.md#bpy.types.ShaderNodeTexEnvironment.image_user "bpy.types.ShaderNodeTexEnvironment.image_user") | - [`ShaderNodeTexImage.image_user`](bpy.types.ShaderNodeTexImage.md#bpy.types.ShaderNodeTexImage.image_user "bpy.types.ShaderNodeTexImage.image_user") - [`SpaceImageEditor.image_user`](bpy.types.SpaceImageEditor.md#bpy.types.SpaceImageEditor.image_user "bpy.types.SpaceImageEditor.image_user") - [`TextureNodeImage.image_user`](bpy.types.TextureNodeImage.md#bpy.types.TextureNodeImage.image_user "bpy.types.TextureNodeImage.image_user") - [`UILayout.template_image`](bpy.types.UILayout.md#bpy.types.UILayout.template_image "bpy.types.UILayout.template_image") - [`UILayout.template_image_layers`](bpy.types.UILayout.md#bpy.types.UILayout.template_image_layers "bpy.types.UILayout.template_image_layers") |
