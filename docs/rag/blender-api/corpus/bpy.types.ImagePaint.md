<!-- source: Blender Python API reference 5.2 / bpy.types.ImagePaint.html -->

<a id="imagepaint-paint"></a>

# ImagePaint(Paint)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Paint`](bpy.types.Paint.md#bpy.types.Paint "bpy.types.Paint")

<a id="bpy.types.ImagePaint"></a>

### class bpy.types.ImagePaint(Paint)

Properties of image and texture painting mode

<a id="bpy.types.ImagePaint.canvas"></a>

#### bpy.types.ImagePaint.canvas

Image used as canvas

**Type:**

[`Image`](bpy.types.Image.md#bpy.types.Image "bpy.types.Image") | None

<a id="bpy.types.ImagePaint.clone_alpha"></a>

#### bpy.types.ImagePaint.clone_alpha

Opacity of clone image display (in [0, 1], default 0.5)

**Type:**

float

<a id="bpy.types.ImagePaint.clone_image"></a>

#### bpy.types.ImagePaint.clone_image

Image used as clone source

**Type:**

[`Image`](bpy.types.Image.md#bpy.types.Image "bpy.types.Image") | None

<a id="bpy.types.ImagePaint.clone_offset"></a>

#### bpy.types.ImagePaint.clone_offset

(array of 2 items, in [-inf, inf], default (0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.ImagePaint.dither"></a>

#### bpy.types.ImagePaint.dither

Amount of dithering when painting on byte images (in [0, 2], default 0.0)

**Type:**

float

<a id="bpy.types.ImagePaint.interpolation"></a>

#### bpy.types.ImagePaint.interpolation

Texture filtering type (default `'LINEAR'`)

- `LINEAR`
  Linear – Linear interpolation.
- `CLOSEST`
  Closest – No interpolation (sample closest texel).

**Type:**

Literal[‘LINEAR’, ‘CLOSEST’]

<a id="bpy.types.ImagePaint.invert_stencil"></a>

#### bpy.types.ImagePaint.invert_stencil

Invert the stencil layer (default False)

**Type:**

bool

<a id="bpy.types.ImagePaint.missing_materials"></a>

#### bpy.types.ImagePaint.missing_materials

The mesh is missing materials (default False, readonly)

**Type:**

bool

<a id="bpy.types.ImagePaint.missing_stencil"></a>

#### bpy.types.ImagePaint.missing_stencil

Image Painting does not have a stencil (default False, readonly)

**Type:**

bool

<a id="bpy.types.ImagePaint.missing_texture"></a>

#### bpy.types.ImagePaint.missing_texture

Image Painting does not have a texture to paint on (default False, readonly)

**Type:**

bool

<a id="bpy.types.ImagePaint.missing_uvs"></a>

#### bpy.types.ImagePaint.missing_uvs

A UV layer is missing on the mesh (default False, readonly)

**Type:**

bool

<a id="bpy.types.ImagePaint.mode"></a>

#### bpy.types.ImagePaint.mode

Mode of operation for projection painting (default `'MATERIAL'`)

- `MATERIAL`
  Material – Detect image slots from the material.
- `IMAGE`
  Single Image – Set image for texture painting directly.

**Type:**

Literal[‘MATERIAL’, ‘IMAGE’]

<a id="bpy.types.ImagePaint.normal_angle"></a>

#### bpy.types.ImagePaint.normal_angle

Paint most on faces pointing towards the view according to this angle (in [0, 90], default 80)

**Type:**

int

<a id="bpy.types.ImagePaint.screen_grab_size"></a>

#### bpy.types.ImagePaint.screen_grab_size

Size to capture the image for re-projecting (array of 2 items, in [512, 16384], default (0, 0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[int]

<a id="bpy.types.ImagePaint.seam_bleed"></a>

#### bpy.types.ImagePaint.seam_bleed

Extend paint beyond the faces’ UVs to reduce seams (in pixels, slower) (in [-32768, 32767], default 2)

**Type:**

int

<a id="bpy.types.ImagePaint.stencil_color"></a>

#### bpy.types.ImagePaint.stencil_color

Stencil color in the viewport (array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ImagePaint.stencil_image"></a>

#### bpy.types.ImagePaint.stencil_image

Image used as stencil

**Type:**

[`Image`](bpy.types.Image.md#bpy.types.Image "bpy.types.Image") | None

<a id="bpy.types.ImagePaint.use_backface_culling"></a>

#### bpy.types.ImagePaint.use_backface_culling

Ignore faces pointing away from the view (faster) (default True)

**Type:**

bool

<a id="bpy.types.ImagePaint.use_clone_layer"></a>

#### bpy.types.ImagePaint.use_clone_layer

Use another UV map as clone source, otherwise use the 3D cursor as the source (default False)

**Type:**

bool

<a id="bpy.types.ImagePaint.use_normal_falloff"></a>

#### bpy.types.ImagePaint.use_normal_falloff

Paint most on faces pointing towards the view (default True)

**Type:**

bool

<a id="bpy.types.ImagePaint.use_occlude"></a>

#### bpy.types.ImagePaint.use_occlude

Only paint onto the faces directly under the brush (slower) (default True)

**Type:**

bool

<a id="bpy.types.ImagePaint.use_stencil_layer"></a>

#### bpy.types.ImagePaint.use_stencil_layer

Set the mask layer from the UV map buttons (default False)

**Type:**

bool

<a id="bpy.types.ImagePaint.detect_data"></a>

#### bpy.types.ImagePaint.detect_data()

Check if required texpaint data exist

**Return type:**

bool

<a id="bpy.types.ImagePaint.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ImagePaint.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ImagePaint.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ImagePaint.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, Paint.brush, Paint.brush_asset_reference, Paint.palette, Paint.show_brush, Paint.show_brush_on_surface, Paint.show_low_resolution, Paint.use_sculpt_delay_updates, Paint.show_bvh_nodes, Paint.use_symmetry_x, Paint.use_symmetry_y, Paint.use_symmetry_z, Paint.use_symmetry_feather, Paint.cavity_curve, Paint.use_cavity, Paint.tile_offset, Paint.tile_x, Paint.tile_y, Paint.tile_z, Paint.show_strength_curve, Paint.show_size_curve, Paint.show_jitter_curve, Paint.unified_paint_settings, Paint.mesh_automasking_settings

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, Paint.bl_rna_get_subclass, Paint.bl_rna_get_subclass_py

<a id="references"></a>

## References

|  |  |
| --- | --- |
| - [`ToolSettings.image_paint`](bpy.types.ToolSettings.md#bpy.types.ToolSettings.image_paint "bpy.types.ToolSettings.image_paint") |  |
