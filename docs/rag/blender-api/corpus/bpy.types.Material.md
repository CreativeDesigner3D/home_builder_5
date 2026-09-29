<!-- source: Blender Python API reference 5.2 / bpy.types.Material.html -->

<a id="material-id"></a>

# Material(ID)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")

<a id="bpy.types.Material"></a>

### class bpy.types.Material(ID)

Material data-block to define the appearance of geometric objects for rendering

<a id="bpy.types.Material.alpha_threshold"></a>

#### bpy.types.Material.alpha_threshold

A pixel is rendered only if its alpha value is above this threshold (in [0, 1], default 0.5)

**Type:**

float

<a id="bpy.types.Material.animation_data"></a>

#### bpy.types.Material.animation_data

Animation data for this data-block (readonly)

**Type:**

[`AnimData`](bpy.types.AnimData.md#bpy.types.AnimData "bpy.types.AnimData") | None

<a id="bpy.types.Material.blend_method"></a>

#### bpy.types.Material.blend_method

Blend Mode for Transparent Faces (Deprecated: use ‘surface_render_method’) (default `'OPAQUE'`)

- `OPAQUE`
  Opaque – Render surface without transparency.
- `CLIP`
  Alpha Clip – Use the alpha threshold to clip the visibility (binary visibility).
- `HASHED`
  Alpha Hashed – Use noise to dither the binary visibility (works well with multi-samples).
- `BLEND`
  Alpha Blend – Render polygon transparent, depending on alpha channel of the texture.

**Type:**

Literal[‘OPAQUE’, ‘CLIP’, ‘HASHED’, ‘BLEND’]

<a id="bpy.types.Material.cycles"></a>

#### bpy.types.Material.cycles

Cycles material settings (readonly)

**Type:**

`CyclesMaterialSettings` | None

<a id="bpy.types.Material.diffuse_color"></a>

#### bpy.types.Material.diffuse_color

Diffuse color of the material (array of 4 items, in [0, inf], default (0.8, 0.8, 0.8, 1.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.Material.displacement_method"></a>

#### bpy.types.Material.displacement_method

Method to use for the displacement (default `'BUMP'`)

- `BUMP`
  Bump Only – Bump mapping to simulate the appearance of displacement.
- `DISPLACEMENT`
  Displacement Only – Use true displacement of surface only, requires fine subdivision.
- `BOTH`
  Displacement and Bump – Combination of true displacement and bump mapping for finer detail.

**Type:**

Literal[‘BUMP’, ‘DISPLACEMENT’, ‘BOTH’]

<a id="bpy.types.Material.grease_pencil"></a>

#### bpy.types.Material.grease_pencil

Grease Pencil color settings for material (readonly)

**Type:**

[`MaterialGPencilStyle`](bpy.types.MaterialGPencilStyle.md#bpy.types.MaterialGPencilStyle "bpy.types.MaterialGPencilStyle") | None

<a id="bpy.types.Material.is_grease_pencil"></a>

#### bpy.types.Material.is_grease_pencil

True if this material has Grease Pencil data (default False, readonly)

**Type:**

bool

<a id="bpy.types.Material.line_color"></a>

#### bpy.types.Material.line_color

Line color used for Freestyle line rendering (array of 4 items, in [0, inf], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.Material.line_priority"></a>

#### bpy.types.Material.line_priority

The line color of a higher priority is used at material boundaries (in [0, 32767], default 0)

**Type:**

int

<a id="bpy.types.Material.lineart"></a>

#### bpy.types.Material.lineart

Line Art settings for material (readonly)

**Type:**

[`MaterialLineArt`](bpy.types.MaterialLineArt.md#bpy.types.MaterialLineArt "bpy.types.MaterialLineArt") | None

<a id="bpy.types.Material.max_vertex_displacement"></a>

#### bpy.types.Material.max_vertex_displacement

The max distance a vertex can be displaced. Displacements over this threshold may cause visibility issues. (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.Material.metallic"></a>

#### bpy.types.Material.metallic

Amount of mirror reflection for raytrace (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.Material.node_tree"></a>

#### bpy.types.Material.node_tree

Node tree for node based materials (readonly)

**Type:**

[`NodeTree`](bpy.types.NodeTree.md#bpy.types.NodeTree "bpy.types.NodeTree") | None

<a id="bpy.types.Material.paint_active_slot"></a>

#### bpy.types.Material.paint_active_slot

Index of active texture paint slot (in [0, 32767], default 0)

**Type:**

int

<a id="bpy.types.Material.paint_clone_slot"></a>

#### bpy.types.Material.paint_clone_slot

Index of clone texture paint slot (in [0, 32767], default 0)

**Type:**

int

<a id="bpy.types.Material.pass_index"></a>

#### bpy.types.Material.pass_index

Index number for the “Material Index” render pass (in [0, 32767], default 0)

**Type:**

int

<a id="bpy.types.Material.preview_render_type"></a>

#### bpy.types.Material.preview_render_type

Type of preview render (default `'SPHERE'`)

- `FLAT`
  Flat – Flat XY plane.
- `SPHERE`
  Sphere – Sphere.
- `CUBE`
  Cube – Cube.
- `HAIR`
  Hair – Hair strands.
- `SHADERBALL`
  Shader Ball – Shader ball.
- `CLOTH`
  Cloth – Cloth.
- `FLUID`
  Fluid – Fluid.

**Type:**

Literal[‘FLAT’, ‘SPHERE’, ‘CUBE’, ‘HAIR’, ‘SHADERBALL’, ‘CLOTH’, ‘FLUID’]

<a id="bpy.types.Material.refraction_depth"></a>

#### bpy.types.Material.refraction_depth

Approximate the thickness of the object to compute two refraction events (0 is disabled) (Deprecated) (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.Material.roughness"></a>

#### bpy.types.Material.roughness

Roughness of the material (in [0, 1], default 0.4)

**Type:**

float

<a id="bpy.types.Material.show_transparent_back"></a>

#### bpy.types.Material.show_transparent_back

Render multiple transparent layers (may introduce transparency sorting problems) (Deprecated: use ‘use_tranparency_overlap’) (default True)

**Type:**

bool

<a id="bpy.types.Material.specular_color"></a>

#### bpy.types.Material.specular_color

Specular color of the material (array of 3 items, in [0, inf], default (1.0, 1.0, 1.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.Material.specular_intensity"></a>

#### bpy.types.Material.specular_intensity

How intense (bright) the specular reflection is (in [0, 1], default 0.5)

**Type:**

float

<a id="bpy.types.Material.surface_render_method"></a>

#### bpy.types.Material.surface_render_method

Controls the blending and the compatibility with certain features (default `'DITHERED'`)

- `DITHERED`
  Dithered – Allows for grayscale hashed transparency, and compatible with render passes and raytracing. Also known as deferred rendering..
- `BLENDED`
  Blended – Allows for colored transparency, but incompatible with render passes and raytracing. Also known as forward rendering..

**Type:**

Literal[‘DITHERED’, ‘BLENDED’]

<a id="bpy.types.Material.texture_paint_images"></a>

#### bpy.types.Material.texture_paint_images

Texture images used for texture painting (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`Image`](bpy.types.Image.md#bpy.types.Image "bpy.types.Image")]

<a id="bpy.types.Material.texture_paint_slots"></a>

#### bpy.types.Material.texture_paint_slots

Texture slots defining the mapping and influence of textures (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`TexPaintSlot`](bpy.types.TexPaintSlot.md#bpy.types.TexPaintSlot "bpy.types.TexPaintSlot")]

<a id="bpy.types.Material.thickness_mode"></a>

#### bpy.types.Material.thickness_mode

Approximation used to model the light interactions inside the object (default `'SPHERE'`)

- `SPHERE`
  Sphere – Approximate the object as a sphere whose diameter is equal to the thickness defined by the node tree.
- `SLAB`
  Slab – Approximate the object as an infinite slab of thickness defined by the node tree.

**Type:**

Literal[‘SPHERE’, ‘SLAB’]

<a id="bpy.types.Material.use_backface_culling"></a>

#### bpy.types.Material.use_backface_culling

Use back face culling to hide the back side of faces (default False)

**Type:**

bool

<a id="bpy.types.Material.use_backface_culling_lightprobe_volume"></a>

#### bpy.types.Material.use_backface_culling_lightprobe_volume

Consider material single sided for light probe volume capture. Additionally helps rejecting probes inside the object to avoid light leaks. (default True)

**Type:**

bool

<a id="bpy.types.Material.use_backface_culling_shadow"></a>

#### bpy.types.Material.use_backface_culling_shadow

Use back face culling when casting shadows (default False)

**Type:**

bool

<a id="bpy.types.Material.use_nodes"></a>

#### bpy.types.Material.use_nodes

Use shader nodes to render the material (default False)

Deprecated since version 5.0: removal planned in version 6.0

Unused but kept for compatibility reasons. Setting the property has no effect, and getting it always returns True.

**Type:**

bool

<a id="bpy.types.Material.use_preview_world"></a>

#### bpy.types.Material.use_preview_world

Use the current world background to light the preview render (default False)

**Type:**

bool

<a id="bpy.types.Material.use_raytrace_refraction"></a>

#### bpy.types.Material.use_raytrace_refraction

Use raytracing to determine transmitted color instead of using only light probes. This prevents the surface from contributing to the lighting of surfaces not using this setting. (default False)

**Type:**

bool

<a id="bpy.types.Material.use_screen_refraction"></a>

#### bpy.types.Material.use_screen_refraction

Use raytracing to determine transmitted color instead of using only light probes. This prevents the surface from contributing to the lighting of surfaces not using this setting. Deprecated: use ‘use_raytrace_refraction’. (default False)

**Type:**

bool

<a id="bpy.types.Material.use_sss_translucency"></a>

#### bpy.types.Material.use_sss_translucency

Add translucency effect to subsurface (Deprecated) (default False)

**Type:**

bool

<a id="bpy.types.Material.use_thickness_from_shadow"></a>

#### bpy.types.Material.use_thickness_from_shadow

Use the shadow maps from shadow casting lights to refine the thickness defined by the material node tree (default False)

**Type:**

bool

<a id="bpy.types.Material.use_transparency_overlap"></a>

#### bpy.types.Material.use_transparency_overlap

Render multiple transparent layers (may introduce transparency sorting problems) (default True)

**Type:**

bool

<a id="bpy.types.Material.use_transparent_shadow"></a>

#### bpy.types.Material.use_transparent_shadow

Use transparent shadows for this material if it contains a Transparent BSDF, disabling will render faster but not give accurate shadows (default True)

**Type:**

bool

<a id="bpy.types.Material.volume_intersection_method"></a>

#### bpy.types.Material.volume_intersection_method

Determines which inner part of the mesh will produce volumetric effect (default `'FAST'`)

- `FAST`
  Fast – Each face is considered as a medium interface. Gives correct results for manifold geometry that contains no inner parts..
- `ACCURATE`
  Accurate – Faces are considered as medium interface only when they have different consecutive facing. Gives correct results as long as the max ray depth is not exceeded. Have significant memory overhead compared to the fast method..

**Type:**

Literal[‘FAST’, ‘ACCURATE’]

<a id="bpy.types.Material.inline_shader_nodes"></a>

#### bpy.types.Material.inline_shader_nodes()

Get the inlined shader nodes of this material. This preprocesses the node tree
to remove nested groups, repeat zones and more.

**Returns:**

The inlined shader nodes.

**Return type:**

[`InlineShaderNodes`](bpy.types.InlineShaderNodes.md#bpy.types.InlineShaderNodes "bpy.types.InlineShaderNodes")

<a id="bpy.types.Material.bl_rna_get_subclass"></a>

#### classmethod bpy.types.Material.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.Material.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.Material.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

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
| - `bpy.context.material` - [`BlendData.materials`](bpy.types.BlendData.md#bpy.types.BlendData.materials "bpy.types.BlendData.materials") - [`BlendDataMaterials.create_gpencil_data`](bpy.types.BlendDataMaterials.md#bpy.types.BlendDataMaterials.create_gpencil_data "bpy.types.BlendDataMaterials.create_gpencil_data") - [`BlendDataMaterials.new`](bpy.types.BlendDataMaterials.md#bpy.types.BlendDataMaterials.new "bpy.types.BlendDataMaterials.new") - [`BlendDataMaterials.remove`](bpy.types.BlendDataMaterials.md#bpy.types.BlendDataMaterials.remove "bpy.types.BlendDataMaterials.remove") - [`BlendDataMaterials.remove_gpencil_data`](bpy.types.BlendDataMaterials.md#bpy.types.BlendDataMaterials.remove_gpencil_data "bpy.types.BlendDataMaterials.remove_gpencil_data") - [`BrushGpencilSettings.material`](bpy.types.BrushGpencilSettings.md#bpy.types.BrushGpencilSettings.material "bpy.types.BrushGpencilSettings.material") - [`BrushGpencilSettings.material_alt`](bpy.types.BrushGpencilSettings.md#bpy.types.BrushGpencilSettings.material_alt "bpy.types.BrushGpencilSettings.material_alt") - [`Curve.materials`](bpy.types.Curve.md#bpy.types.Curve.materials "bpy.types.Curve.materials") - [`Curves.materials`](bpy.types.Curves.md#bpy.types.Curves.materials "bpy.types.Curves.materials") - [`GeometryNodeInputMaterial.material`](bpy.types.GeometryNodeInputMaterial.md#bpy.types.GeometryNodeInputMaterial.material "bpy.types.GeometryNodeInputMaterial.material") - [`GreasePencil.materials`](bpy.types.GreasePencil.md#bpy.types.GreasePencil.materials "bpy.types.GreasePencil.materials") - [`GreasePencilArrayModifier.material_filter`](bpy.types.GreasePencilArrayModifier.md#bpy.types.GreasePencilArrayModifier.material_filter "bpy.types.GreasePencilArrayModifier.material_filter") - [`GreasePencilBuildModifier.material_filter`](bpy.types.GreasePencilBuildModifier.md#bpy.types.GreasePencilBuildModifier.material_filter "bpy.types.GreasePencilBuildModifier.material_filter") - [`GreasePencilColorModifier.material_filter`](bpy.types.GreasePencilColorModifier.md#bpy.types.GreasePencilColorModifier.material_filter "bpy.types.GreasePencilColorModifier.material_filter") - [`GreasePencilDashModifierData.material_filter`](bpy.types.GreasePencilDashModifierData.md#bpy.types.GreasePencilDashModifierData.material_filter "bpy.types.GreasePencilDashModifierData.material_filter") - [`GreasePencilEnvelopeModifier.material_filter`](bpy.types.GreasePencilEnvelopeModifier.md#bpy.types.GreasePencilEnvelopeModifier.material_filter "bpy.types.GreasePencilEnvelopeModifier.material_filter") - [`GreasePencilHookModifier.material_filter`](bpy.types.GreasePencilHookModifier.md#bpy.types.GreasePencilHookModifier.material_filter "bpy.types.GreasePencilHookModifier.material_filter") - [`GreasePencilLatticeModifier.material_filter`](bpy.types.GreasePencilLatticeModifier.md#bpy.types.GreasePencilLatticeModifier.material_filter "bpy.types.GreasePencilLatticeModifier.material_filter") - [`GreasePencilLengthModifier.material_filter`](bpy.types.GreasePencilLengthModifier.md#bpy.types.GreasePencilLengthModifier.material_filter "bpy.types.GreasePencilLengthModifier.material_filter") - [`GreasePencilLineartModifier.target_material`](bpy.types.GreasePencilLineartModifier.md#bpy.types.GreasePencilLineartModifier.target_material "bpy.types.GreasePencilLineartModifier.target_material") - [`GreasePencilMirrorModifier.material_filter`](bpy.types.GreasePencilMirrorModifier.md#bpy.types.GreasePencilMirrorModifier.material_filter "bpy.types.GreasePencilMirrorModifier.material_filter") - [`GreasePencilMultiplyModifier.material_filter`](bpy.types.GreasePencilMultiplyModifier.md#bpy.types.GreasePencilMultiplyModifier.material_filter "bpy.types.GreasePencilMultiplyModifier.material_filter") - [`GreasePencilNoiseModifier.material_filter`](bpy.types.GreasePencilNoiseModifier.md#bpy.types.GreasePencilNoiseModifier.material_filter "bpy.types.GreasePencilNoiseModifier.material_filter") | - [`GreasePencilOffsetModifier.material_filter`](bpy.types.GreasePencilOffsetModifier.md#bpy.types.GreasePencilOffsetModifier.material_filter "bpy.types.GreasePencilOffsetModifier.material_filter") - [`GreasePencilOpacityModifier.material_filter`](bpy.types.GreasePencilOpacityModifier.md#bpy.types.GreasePencilOpacityModifier.material_filter "bpy.types.GreasePencilOpacityModifier.material_filter") - [`GreasePencilOutlineModifier.material_filter`](bpy.types.GreasePencilOutlineModifier.md#bpy.types.GreasePencilOutlineModifier.material_filter "bpy.types.GreasePencilOutlineModifier.material_filter") - [`GreasePencilOutlineModifier.outline_material`](bpy.types.GreasePencilOutlineModifier.md#bpy.types.GreasePencilOutlineModifier.outline_material "bpy.types.GreasePencilOutlineModifier.outline_material") - [`GreasePencilShrinkwrapModifier.material_filter`](bpy.types.GreasePencilShrinkwrapModifier.md#bpy.types.GreasePencilShrinkwrapModifier.material_filter "bpy.types.GreasePencilShrinkwrapModifier.material_filter") - [`GreasePencilSimplifyModifier.material_filter`](bpy.types.GreasePencilSimplifyModifier.md#bpy.types.GreasePencilSimplifyModifier.material_filter "bpy.types.GreasePencilSimplifyModifier.material_filter") - [`GreasePencilSmoothModifier.material_filter`](bpy.types.GreasePencilSmoothModifier.md#bpy.types.GreasePencilSmoothModifier.material_filter "bpy.types.GreasePencilSmoothModifier.material_filter") - [`GreasePencilSubdivModifier.material_filter`](bpy.types.GreasePencilSubdivModifier.md#bpy.types.GreasePencilSubdivModifier.material_filter "bpy.types.GreasePencilSubdivModifier.material_filter") - [`GreasePencilTextureModifier.material_filter`](bpy.types.GreasePencilTextureModifier.md#bpy.types.GreasePencilTextureModifier.material_filter "bpy.types.GreasePencilTextureModifier.material_filter") - [`GreasePencilThickModifierData.material_filter`](bpy.types.GreasePencilThickModifierData.md#bpy.types.GreasePencilThickModifierData.material_filter "bpy.types.GreasePencilThickModifierData.material_filter") - [`GreasePencilTintModifier.material_filter`](bpy.types.GreasePencilTintModifier.md#bpy.types.GreasePencilTintModifier.material_filter "bpy.types.GreasePencilTintModifier.material_filter") - [`GreasePencilWeightAngleModifier.material_filter`](bpy.types.GreasePencilWeightAngleModifier.md#bpy.types.GreasePencilWeightAngleModifier.material_filter "bpy.types.GreasePencilWeightAngleModifier.material_filter") - [`GreasePencilWeightProximityModifier.material_filter`](bpy.types.GreasePencilWeightProximityModifier.md#bpy.types.GreasePencilWeightProximityModifier.material_filter "bpy.types.GreasePencilWeightProximityModifier.material_filter") - [`IDMaterials.append`](bpy.types.IDMaterials.md#bpy.types.IDMaterials.append "bpy.types.IDMaterials.append") - [`IDMaterials.pop`](bpy.types.IDMaterials.md#bpy.types.IDMaterials.pop "bpy.types.IDMaterials.pop") - [`MaterialSlot.material`](bpy.types.MaterialSlot.md#bpy.types.MaterialSlot.material "bpy.types.MaterialSlot.material") - [`Mesh.materials`](bpy.types.Mesh.md#bpy.types.Mesh.materials "bpy.types.Mesh.materials") - [`MetaBall.materials`](bpy.types.MetaBall.md#bpy.types.MetaBall.materials "bpy.types.MetaBall.materials") - [`NodeSocketMaterial.default_value`](bpy.types.NodeSocketMaterial.md#bpy.types.NodeSocketMaterial.default_value "bpy.types.NodeSocketMaterial.default_value") - [`NodeTreeInterfaceSocketMaterial.default_value`](bpy.types.NodeTreeInterfaceSocketMaterial.md#bpy.types.NodeTreeInterfaceSocketMaterial.default_value "bpy.types.NodeTreeInterfaceSocketMaterial.default_value") - [`Object.active_material`](bpy.types.Object.md#bpy.types.Object.active_material "bpy.types.Object.active_material") - [`PointCloud.materials`](bpy.types.PointCloud.md#bpy.types.PointCloud.materials "bpy.types.PointCloud.materials") - [`ViewLayer.material_override`](bpy.types.ViewLayer.md#bpy.types.ViewLayer.material_override "bpy.types.ViewLayer.material_override") - [`Volume.materials`](bpy.types.Volume.md#bpy.types.Volume.materials "bpy.types.Volume.materials") |
