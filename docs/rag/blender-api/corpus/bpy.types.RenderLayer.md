<!-- source: Blender Python API reference 5.2 / bpy.types.RenderLayer.html -->

<a id="renderlayer-bpy-struct"></a>

# RenderLayer(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.RenderLayer"></a>

### class bpy.types.RenderLayer(bpy_struct)

<a id="bpy.types.RenderLayer.name"></a>

#### bpy.types.RenderLayer.name

View layer name (default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.RenderLayer.passes"></a>

#### bpy.types.RenderLayer.passes

(default None, readonly)

**Type:**

[`RenderPasses`](bpy.types.RenderPasses.md#bpy.types.RenderPasses "bpy.types.RenderPasses")[[`RenderPass`](bpy.types.RenderPass.md#bpy.types.RenderPass "bpy.types.RenderPass")]

<a id="bpy.types.RenderLayer.use_ao"></a>

#### bpy.types.RenderLayer.use_ao

Render Ambient Occlusion in this Layer (default False, readonly)

**Type:**

bool

<a id="bpy.types.RenderLayer.use_grease_pencil"></a>

#### bpy.types.RenderLayer.use_grease_pencil

Render Grease Pencil on this layer (default False, readonly)

**Type:**

bool

<a id="bpy.types.RenderLayer.use_motion_blur"></a>

#### bpy.types.RenderLayer.use_motion_blur

Render motion blur in this Layer, if enabled in the scene (default False, readonly)

**Type:**

bool

<a id="bpy.types.RenderLayer.use_pass_ambient_occlusion"></a>

#### bpy.types.RenderLayer.use_pass_ambient_occlusion

Deliver Ambient Occlusion pass (default False, readonly)

**Type:**

bool

<a id="bpy.types.RenderLayer.use_pass_combined"></a>

#### bpy.types.RenderLayer.use_pass_combined

Deliver full combined RGBA buffer (default False, readonly)

**Type:**

bool

<a id="bpy.types.RenderLayer.use_pass_diffuse_color"></a>

#### bpy.types.RenderLayer.use_pass_diffuse_color

Deliver diffuse color pass (default False, readonly)

**Type:**

bool

<a id="bpy.types.RenderLayer.use_pass_diffuse_direct"></a>

#### bpy.types.RenderLayer.use_pass_diffuse_direct

Deliver diffuse direct pass (default False, readonly)

**Type:**

bool

<a id="bpy.types.RenderLayer.use_pass_diffuse_indirect"></a>

#### bpy.types.RenderLayer.use_pass_diffuse_indirect

Deliver diffuse indirect pass (default False, readonly)

**Type:**

bool

<a id="bpy.types.RenderLayer.use_pass_emit"></a>

#### bpy.types.RenderLayer.use_pass_emit

Deliver emission pass (default False, readonly)

**Type:**

bool

<a id="bpy.types.RenderLayer.use_pass_environment"></a>

#### bpy.types.RenderLayer.use_pass_environment

Deliver environment lighting pass (default False, readonly)

**Type:**

bool

<a id="bpy.types.RenderLayer.use_pass_glossy_color"></a>

#### bpy.types.RenderLayer.use_pass_glossy_color

Deliver glossy color pass (default False, readonly)

**Type:**

bool

<a id="bpy.types.RenderLayer.use_pass_glossy_direct"></a>

#### bpy.types.RenderLayer.use_pass_glossy_direct

Deliver glossy direct pass (default False, readonly)

**Type:**

bool

<a id="bpy.types.RenderLayer.use_pass_glossy_indirect"></a>

#### bpy.types.RenderLayer.use_pass_glossy_indirect

Deliver glossy indirect pass (default False, readonly)

**Type:**

bool

<a id="bpy.types.RenderLayer.use_pass_material_index"></a>

#### bpy.types.RenderLayer.use_pass_material_index

Deliver material index pass (default False, readonly)

**Type:**

bool

<a id="bpy.types.RenderLayer.use_pass_mist"></a>

#### bpy.types.RenderLayer.use_pass_mist

Deliver mist factor pass (0.0 to 1.0) (default False, readonly)

**Type:**

bool

<a id="bpy.types.RenderLayer.use_pass_normal"></a>

#### bpy.types.RenderLayer.use_pass_normal

Deliver normal pass (default False, readonly)

**Type:**

bool

<a id="bpy.types.RenderLayer.use_pass_object_index"></a>

#### bpy.types.RenderLayer.use_pass_object_index

Deliver object index pass (default False, readonly)

**Type:**

bool

<a id="bpy.types.RenderLayer.use_pass_position"></a>

#### bpy.types.RenderLayer.use_pass_position

Deliver position pass (default False, readonly)

**Type:**

bool

<a id="bpy.types.RenderLayer.use_pass_shadow"></a>

#### bpy.types.RenderLayer.use_pass_shadow

Deliver shadow pass (default False, readonly)

**Type:**

bool

<a id="bpy.types.RenderLayer.use_pass_subsurface_color"></a>

#### bpy.types.RenderLayer.use_pass_subsurface_color

Deliver subsurface color pass (default False, readonly)

**Type:**

bool

<a id="bpy.types.RenderLayer.use_pass_subsurface_direct"></a>

#### bpy.types.RenderLayer.use_pass_subsurface_direct

Deliver subsurface direct pass (default False, readonly)

**Type:**

bool

<a id="bpy.types.RenderLayer.use_pass_subsurface_indirect"></a>

#### bpy.types.RenderLayer.use_pass_subsurface_indirect

Deliver subsurface indirect pass (default False, readonly)

**Type:**

bool

<a id="bpy.types.RenderLayer.use_pass_transmission_color"></a>

#### bpy.types.RenderLayer.use_pass_transmission_color

Deliver transmission color pass (default False, readonly)

**Type:**

bool

<a id="bpy.types.RenderLayer.use_pass_transmission_direct"></a>

#### bpy.types.RenderLayer.use_pass_transmission_direct

Deliver transmission direct pass (default False, readonly)

**Type:**

bool

<a id="bpy.types.RenderLayer.use_pass_transmission_indirect"></a>

#### bpy.types.RenderLayer.use_pass_transmission_indirect

Deliver transmission indirect pass (default False, readonly)

**Type:**

bool

<a id="bpy.types.RenderLayer.use_pass_uv"></a>

#### bpy.types.RenderLayer.use_pass_uv

Deliver texture UV pass (default False, readonly)

**Type:**

bool

<a id="bpy.types.RenderLayer.use_pass_vector"></a>

#### bpy.types.RenderLayer.use_pass_vector

Deliver speed vector pass (default False, readonly)

**Type:**

bool

<a id="bpy.types.RenderLayer.use_pass_z"></a>

#### bpy.types.RenderLayer.use_pass_z

Deliver depth values pass (default False, readonly)

**Type:**

bool

<a id="bpy.types.RenderLayer.use_sky"></a>

#### bpy.types.RenderLayer.use_sky

Render Sky in this Layer (default False, readonly)

**Type:**

bool

<a id="bpy.types.RenderLayer.use_solid"></a>

#### bpy.types.RenderLayer.use_solid

Render Solid faces in this Layer (default False, readonly)

**Type:**

bool

<a id="bpy.types.RenderLayer.use_strand"></a>

#### bpy.types.RenderLayer.use_strand

Render Strands in this Layer (default False, readonly)

**Type:**

bool

<a id="bpy.types.RenderLayer.use_volumes"></a>

#### bpy.types.RenderLayer.use_volumes

Render volumes in this Layer (default False, readonly)

**Type:**

bool

<a id="bpy.types.RenderLayer.load_from_file"></a>

#### bpy.types.RenderLayer.load_from_file(filepath, *, x=0, y=0)

Copies the pixels of this renderlayer from an image file

**Parameters:**

- **filepath** (str) – File Path, File path to load into this render tile, must be no smaller than the renderlayer (never None)
- **x** (int) – Offset X, Offset the position to copy from if the image is larger than the render layer (in [0, inf], optional)
- **y** (int) – Offset Y, Offset the position to copy from if the image is larger than the render layer (in [0, inf], optional)

<a id="bpy.types.RenderLayer.bl_rna_get_subclass"></a>

#### classmethod bpy.types.RenderLayer.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.RenderLayer.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.RenderLayer.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`RenderResult.layers`](bpy.types.RenderResult.md#bpy.types.RenderResult.layers "bpy.types.RenderResult.layers") |  |
