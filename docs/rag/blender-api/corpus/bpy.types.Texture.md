<!-- source: Blender Python API reference 5.2 / bpy.types.Texture.html -->

<a id="texture-id"></a>

# Texture(ID)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")

Subclasses

- [BlendTexture(Texture)](bpy.types.BlendTexture.md)
- [CloudsTexture(Texture)](bpy.types.CloudsTexture.md)
- [DistortedNoiseTexture(Texture)](bpy.types.DistortedNoiseTexture.md)
- [ImageTexture(Texture)](bpy.types.ImageTexture.md)
- [MagicTexture(Texture)](bpy.types.MagicTexture.md)
- [MarbleTexture(Texture)](bpy.types.MarbleTexture.md)
- [MusgraveTexture(Texture)](bpy.types.MusgraveTexture.md)
- [NoiseTexture(Texture)](bpy.types.NoiseTexture.md)
- [StucciTexture(Texture)](bpy.types.StucciTexture.md)
- [VoronoiTexture(Texture)](bpy.types.VoronoiTexture.md)
- [WoodTexture(Texture)](bpy.types.WoodTexture.md)

<a id="bpy.types.Texture"></a>

### class bpy.types.Texture(ID)

Texture data-block used by materials, lights, worlds and brushes

<a id="bpy.types.Texture.animation_data"></a>

#### bpy.types.Texture.animation_data

Animation data for this data-block (readonly)

**Type:**

[`AnimData`](bpy.types.AnimData.md#bpy.types.AnimData "bpy.types.AnimData") | None

<a id="bpy.types.Texture.color_ramp"></a>

#### bpy.types.Texture.color_ramp

(readonly)

**Type:**

[`ColorRamp`](bpy.types.ColorRamp.md#bpy.types.ColorRamp "bpy.types.ColorRamp") | None

<a id="bpy.types.Texture.contrast"></a>

#### bpy.types.Texture.contrast

Adjust the contrast of the texture (in [0, 5], default 1.0)

**Type:**

float

<a id="bpy.types.Texture.factor_blue"></a>

#### bpy.types.Texture.factor_blue

(in [0, 2], default 1.0)

**Type:**

float

<a id="bpy.types.Texture.factor_green"></a>

#### bpy.types.Texture.factor_green

(in [0, 2], default 1.0)

**Type:**

float

<a id="bpy.types.Texture.factor_red"></a>

#### bpy.types.Texture.factor_red

(in [0, 2], default 1.0)

**Type:**

float

<a id="bpy.types.Texture.intensity"></a>

#### bpy.types.Texture.intensity

Adjust the brightness of the texture (in [0, 2], default 1.0)

**Type:**

float

<a id="bpy.types.Texture.node_tree"></a>

#### bpy.types.Texture.node_tree

Node tree for node-based textures (readonly)

**Type:**

[`NodeTree`](bpy.types.NodeTree.md#bpy.types.NodeTree "bpy.types.NodeTree") | None

<a id="bpy.types.Texture.saturation"></a>

#### bpy.types.Texture.saturation

Adjust the saturation of colors in the texture (in [0, 2], default 1.0)

**Type:**

float

<a id="bpy.types.Texture.type"></a>

#### bpy.types.Texture.type

(default `'IMAGE'`)

**Type:**

Literal[[Texture Type Items](bpy_types_enum_items/texture_type_items.md#rna-enum-texture-type-items)]

<a id="bpy.types.Texture.use_clamp"></a>

#### bpy.types.Texture.use_clamp

Set negative texture RGB and intensity values to zero, for some uses like displacement this option can be disabled to get the full range (default False)

**Type:**

bool

<a id="bpy.types.Texture.use_color_ramp"></a>

#### bpy.types.Texture.use_color_ramp

Map the texture intensity to the color ramp. Note that the alpha value is used for image textures, enable “Calculate Alpha” for images without an alpha channel. (default False)

**Type:**

bool

<a id="bpy.types.Texture.use_nodes"></a>

#### bpy.types.Texture.use_nodes

Make this a node-based texture (default False)

**Type:**

bool

<a id="bpy.types.Texture.use_preview_alpha"></a>

#### bpy.types.Texture.use_preview_alpha

Show Alpha in Preview Render (default False)

**Type:**

bool

<a id="bpy.types.Texture.users_material"></a>

#### bpy.types.Texture.users_material

Materials that use this texture

**Type:**

tuple[[`Material`](bpy.types.Material.md#bpy.types.Material "bpy.types.Material"), …]

> **Note:**
>
> Takes `O(len(bpy.data.materials) * len(material.texture_slots))` time.

(readonly)

<a id="bpy.types.Texture.users_object_modifier"></a>

#### bpy.types.Texture.users_object_modifier

Object modifiers that use this texture

**Type:**

tuple[[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object"), …]

> **Note:**
>
> Takes `O(len(bpy.data.objects) * len(obj.modifiers))` time.

(readonly)

<a id="bpy.types.Texture.evaluate"></a>

#### bpy.types.Texture.evaluate(value)

Evaluate the texture at the given coordinate and returns the result

**Parameters:**

**value** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – The coordinates (x,y,z) of the texture, in case of a 3D texture, the z value is the slice of the texture that is evaluated. For 2D textures such as images, the z value is ignored., (array of 3 items, in [-inf, inf])

**Returns:**

The result of the texture where (x,y,z,w) are (red, green, blue, intensity). For grayscale textures, often intensity only will be used., (array of 4 items, in [-inf, inf])

**Return type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.Texture.bl_rna_get_subclass"></a>

#### classmethod bpy.types.Texture.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.Texture.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.Texture.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([type](#bpy.types.Texture.type "bpy.types.Texture.type") | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

[type](#bpy.types.Texture.type "bpy.types.Texture.type")

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, ID.name, ID.name_full, ID.id_type, ID.session_uid, ID.is_evaluated, ID.original, ID.users, ID.use_fake_user, ID.use_extra_user, ID.is_embedded_data, ID.is_linked_packed, ID.is_missing, ID.is_runtime_data, ID.is_editable, ID.tag, ID.is_library_indirect, ID.library, ID.library_weak_reference, ID.asset_data, ID.override_library, ID.preview

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, ID.bl_system_properties_get, ID.rename, ID.evaluated_get, ID.copy, ID.asset_mark, ID.asset_clear, ID.asset_generate_preview, ID.override_create, ID.override_hierarchy_create, ID.user_clear, ID.user_remap, ID.make_local, ID.user_of_id, ID.animation_data_create, ID.animation_data_clear, ID.update_tag, ID.preview_ensure, ID.bl_rna_get_subclass, ID.bl_rna_get_subclass_py

<a id="references"></a>

## References

|  |  |
| --- | --- |
| - `bpy.context.texture` - [`BlendData.textures`](bpy.types.BlendData.md#bpy.types.BlendData.textures "bpy.types.BlendData.textures") - [`BlendDataTextures.new`](bpy.types.BlendDataTextures.md#bpy.types.BlendDataTextures.new "bpy.types.BlendDataTextures.new") - [`BlendDataTextures.remove`](bpy.types.BlendDataTextures.md#bpy.types.BlendDataTextures.remove "bpy.types.BlendDataTextures.remove") - [`Brush.mask_texture`](bpy.types.Brush.md#bpy.types.Brush.mask_texture "bpy.types.Brush.mask_texture") - [`Brush.texture`](bpy.types.Brush.md#bpy.types.Brush.texture "bpy.types.Brush.texture") - [`DisplaceModifier.texture`](bpy.types.DisplaceModifier.md#bpy.types.DisplaceModifier.texture "bpy.types.DisplaceModifier.texture") - [`DynamicPaintSurface.init_texture`](bpy.types.DynamicPaintSurface.md#bpy.types.DynamicPaintSurface.init_texture "bpy.types.DynamicPaintSurface.init_texture") - [`FieldSettings.texture`](bpy.types.FieldSettings.md#bpy.types.FieldSettings.texture "bpy.types.FieldSettings.texture") - [`FluidFlowSettings.noise_texture`](bpy.types.FluidFlowSettings.md#bpy.types.FluidFlowSettings.noise_texture "bpy.types.FluidFlowSettings.noise_texture") - [`FreestyleLineStyle.active_texture`](bpy.types.FreestyleLineStyle.md#bpy.types.FreestyleLineStyle.active_texture "bpy.types.FreestyleLineStyle.active_texture") | - [`NodeSocketTexture.default_value`](bpy.types.NodeSocketTexture.md#bpy.types.NodeSocketTexture.default_value "bpy.types.NodeSocketTexture.default_value") - [`NodeTreeInterfaceSocketTexture.default_value`](bpy.types.NodeTreeInterfaceSocketTexture.md#bpy.types.NodeTreeInterfaceSocketTexture.default_value "bpy.types.NodeTreeInterfaceSocketTexture.default_value") - [`ParticleSettings.active_texture`](bpy.types.ParticleSettings.md#bpy.types.ParticleSettings.active_texture "bpy.types.ParticleSettings.active_texture") - [`TextureNodeTexture.texture`](bpy.types.TextureNodeTexture.md#bpy.types.TextureNodeTexture.texture "bpy.types.TextureNodeTexture.texture") - [`TextureSlot.texture`](bpy.types.TextureSlot.md#bpy.types.TextureSlot.texture "bpy.types.TextureSlot.texture") - [`VertexWeightEditModifier.mask_texture`](bpy.types.VertexWeightEditModifier.md#bpy.types.VertexWeightEditModifier.mask_texture "bpy.types.VertexWeightEditModifier.mask_texture") - [`VertexWeightMixModifier.mask_texture`](bpy.types.VertexWeightMixModifier.md#bpy.types.VertexWeightMixModifier.mask_texture "bpy.types.VertexWeightMixModifier.mask_texture") - [`VertexWeightProximityModifier.mask_texture`](bpy.types.VertexWeightProximityModifier.md#bpy.types.VertexWeightProximityModifier.mask_texture "bpy.types.VertexWeightProximityModifier.mask_texture") - [`VolumeDisplaceModifier.texture`](bpy.types.VolumeDisplaceModifier.md#bpy.types.VolumeDisplaceModifier.texture "bpy.types.VolumeDisplaceModifier.texture") - [`WarpModifier.texture`](bpy.types.WarpModifier.md#bpy.types.WarpModifier.texture "bpy.types.WarpModifier.texture") - [`WaveModifier.texture`](bpy.types.WaveModifier.md#bpy.types.WaveModifier.texture "bpy.types.WaveModifier.texture") |
