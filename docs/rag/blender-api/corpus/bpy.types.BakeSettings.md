<!-- source: Blender Python API reference 5.2 / bpy.types.BakeSettings.html -->

<a id="bakesettings-bpy-struct"></a>

# BakeSettings(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.BakeSettings"></a>

### class bpy.types.BakeSettings(bpy_struct)

Bake data for a Scene data-block

<a id="bpy.types.BakeSettings.cage_extrusion"></a>

#### bpy.types.BakeSettings.cage_extrusion

Inflate the active object by the specified distance for baking. This helps matching to points nearer to the outside of the selected object meshes. (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.BakeSettings.cage_object"></a>

#### bpy.types.BakeSettings.cage_object

Object to use as cage instead of calculating the cage from the active object with cage extrusion

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.BakeSettings.displacement_space"></a>

#### bpy.types.BakeSettings.displacement_space

Choose displacement space for baking (default `'OBJECT'`)

- `OBJECT`
  Object – Bake the displacement in object space.
- `TANGENT`
  Tangent – Bake the displacement in tangent space.

**Type:**

Literal[‘OBJECT’, ‘TANGENT’]

<a id="bpy.types.BakeSettings.filepath"></a>

#### bpy.types.BakeSettings.filepath

Image filepath to use when saving externally (default “//”, never None, blend relative `//` prefix supported)

**Type:**

str

<a id="bpy.types.BakeSettings.height"></a>

#### bpy.types.BakeSettings.height

Vertical dimension of the baking map (in [4, 10000], default 512)

**Type:**

int

<a id="bpy.types.BakeSettings.image_settings"></a>

#### bpy.types.BakeSettings.image_settings

(readonly, never None)

**Type:**

[`ImageFormatSettings`](bpy.types.ImageFormatSettings.md#bpy.types.ImageFormatSettings "bpy.types.ImageFormatSettings")

<a id="bpy.types.BakeSettings.margin"></a>

#### bpy.types.BakeSettings.margin

Extends the baked result as a post process filter (in [0, 32767], default 16)

**Type:**

int

<a id="bpy.types.BakeSettings.margin_type"></a>

#### bpy.types.BakeSettings.margin_type

Algorithm to extend the baked result (default `'ADJACENT_FACES'`)

**Type:**

Literal[[Bake Margin Type Items](bpy_types_enum_items/bake_margin_type_items.md#rna-enum-bake-margin-type-items)]

<a id="bpy.types.BakeSettings.max_ray_distance"></a>

#### bpy.types.BakeSettings.max_ray_distance

The maximum ray distance for matching points between the active and selected objects. If zero, there is no limit. (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.BakeSettings.normal_b"></a>

#### bpy.types.BakeSettings.normal_b

Axis to bake in blue channel (default `'POS_X'`)

**Type:**

Literal[[Normal Swizzle Items](bpy_types_enum_items/normal_swizzle_items.md#rna-enum-normal-swizzle-items)]

<a id="bpy.types.BakeSettings.normal_g"></a>

#### bpy.types.BakeSettings.normal_g

Axis to bake in green channel (default `'POS_X'`)

**Type:**

Literal[[Normal Swizzle Items](bpy_types_enum_items/normal_swizzle_items.md#rna-enum-normal-swizzle-items)]

<a id="bpy.types.BakeSettings.normal_r"></a>

#### bpy.types.BakeSettings.normal_r

Axis to bake in red channel (default `'POS_X'`)

**Type:**

Literal[[Normal Swizzle Items](bpy_types_enum_items/normal_swizzle_items.md#rna-enum-normal-swizzle-items)]

<a id="bpy.types.BakeSettings.normal_space"></a>

#### bpy.types.BakeSettings.normal_space

Choose normal space for baking (default `'TANGENT'`)

**Type:**

Literal[[Normal Space Items](bpy_types_enum_items/normal_space_items.md#rna-enum-normal-space-items)]

<a id="bpy.types.BakeSettings.pass_filter"></a>

#### bpy.types.BakeSettings.pass_filter

Passes to include in the active baking pass (default {`'COLOR'`, `'DIFFUSE'`, `'DIRECT'`, `'EMIT'`, `'GLOSSY'`, `'INDIRECT'`, `'TRANSMISSION'`}, readonly)

**Type:**

set[Literal[[Bake Pass Filter Type Items](bpy_types_enum_items/bake_pass_filter_type_items.md#rna-enum-bake-pass-filter-type-items)]]

<a id="bpy.types.BakeSettings.save_mode"></a>

#### bpy.types.BakeSettings.save_mode

Where to save baked image textures (default `'INTERNAL'`)

**Type:**

Literal[[Bake Save Mode Items](bpy_types_enum_items/bake_save_mode_items.md#rna-enum-bake-save-mode-items)]

<a id="bpy.types.BakeSettings.target"></a>

#### bpy.types.BakeSettings.target

Where to output the baked map (default `'IMAGE_TEXTURES'`)

**Type:**

Literal[[Bake Target Items](bpy_types_enum_items/bake_target_items.md#rna-enum-bake-target-items)]

<a id="bpy.types.BakeSettings.type"></a>

#### bpy.types.BakeSettings.type

Choose shading information to bake into the image (default `'NORMALS'`)

- `NORMALS`
  Normals – Bake normals.
- `DISPLACEMENT`
  Displacement – Bake displacement.
- `VECTOR_DISPLACEMENT`
  Vector Displacement – Bake vector displacement.

**Type:**

Literal[‘NORMALS’, ‘DISPLACEMENT’, ‘VECTOR_DISPLACEMENT’]

<a id="bpy.types.BakeSettings.use_automatic_name"></a>

#### bpy.types.BakeSettings.use_automatic_name

Automatically name the output file with the pass type (external only) (default False)

**Type:**

bool

<a id="bpy.types.BakeSettings.use_cage"></a>

#### bpy.types.BakeSettings.use_cage

Cast rays to active object from a cage (default False)

**Type:**

bool

<a id="bpy.types.BakeSettings.use_clear"></a>

#### bpy.types.BakeSettings.use_clear

Clear Images before baking (internal only) (default True)

**Type:**

bool

<a id="bpy.types.BakeSettings.use_lores_mesh"></a>

#### bpy.types.BakeSettings.use_lores_mesh

Calculate heights against unsubdivided low resolution mesh (default False)

**Type:**

bool

<a id="bpy.types.BakeSettings.use_multires"></a>

#### bpy.types.BakeSettings.use_multires

Bake directly from multires object (default False)

**Type:**

bool

<a id="bpy.types.BakeSettings.use_pass_color"></a>

#### bpy.types.BakeSettings.use_pass_color

Color the pass (default True)

**Type:**

bool

<a id="bpy.types.BakeSettings.use_pass_diffuse"></a>

#### bpy.types.BakeSettings.use_pass_diffuse

Add diffuse contribution (default True)

**Type:**

bool

<a id="bpy.types.BakeSettings.use_pass_direct"></a>

#### bpy.types.BakeSettings.use_pass_direct

Add direct lighting contribution (default True)

**Type:**

bool

<a id="bpy.types.BakeSettings.use_pass_emit"></a>

#### bpy.types.BakeSettings.use_pass_emit

Add emission contribution (default True)

**Type:**

bool

<a id="bpy.types.BakeSettings.use_pass_glossy"></a>

#### bpy.types.BakeSettings.use_pass_glossy

Add glossy contribution (default True)

**Type:**

bool

<a id="bpy.types.BakeSettings.use_pass_indirect"></a>

#### bpy.types.BakeSettings.use_pass_indirect

Add indirect lighting contribution (default True)

**Type:**

bool

<a id="bpy.types.BakeSettings.use_pass_transmission"></a>

#### bpy.types.BakeSettings.use_pass_transmission

Add transmission contribution (default True)

**Type:**

bool

<a id="bpy.types.BakeSettings.use_selected_to_active"></a>

#### bpy.types.BakeSettings.use_selected_to_active

Bake shading on the surface of selected objects to the active object (default False)

**Type:**

bool

<a id="bpy.types.BakeSettings.use_split_materials"></a>

#### bpy.types.BakeSettings.use_split_materials

Split external images per material (external only) (default False)

**Type:**

bool

<a id="bpy.types.BakeSettings.view_from"></a>

#### bpy.types.BakeSettings.view_from

Source of reflection ray directions (default `'ABOVE_SURFACE'`)

- `ABOVE_SURFACE`
  Above Surface – Cast rays from above the surface.
- `ACTIVE_CAMERA`
  Active Camera – Use the active camera’s position to cast rays.

**Type:**

Literal[‘ABOVE_SURFACE’, ‘ACTIVE_CAMERA’]

<a id="bpy.types.BakeSettings.width"></a>

#### bpy.types.BakeSettings.width

Horizontal dimension of the baking map (in [4, 10000], default 512)

**Type:**

int

<a id="bpy.types.BakeSettings.bl_rna_get_subclass"></a>

#### classmethod bpy.types.BakeSettings.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.BakeSettings.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.BakeSettings.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([type](#bpy.types.BakeSettings.type "bpy.types.BakeSettings.type") | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

[type](#bpy.types.BakeSettings.type "bpy.types.BakeSettings.type")

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
| - [`RenderSettings.bake`](bpy.types.RenderSettings.md#bpy.types.RenderSettings.bake "bpy.types.RenderSettings.bake") |  |
