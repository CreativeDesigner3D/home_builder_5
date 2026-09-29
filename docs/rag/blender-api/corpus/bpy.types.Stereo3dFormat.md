<!-- source: Blender Python API reference 5.2 / bpy.types.Stereo3dFormat.html -->

<a id="stereo3dformat-bpy-struct"></a>

# Stereo3dFormat(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.Stereo3dFormat"></a>

### class bpy.types.Stereo3dFormat(bpy_struct)

Settings for stereo output

<a id="bpy.types.Stereo3dFormat.anaglyph_type"></a>

#### bpy.types.Stereo3dFormat.anaglyph_type

(default `'RED_CYAN'`)

**Type:**

Literal[[Stereo3D Anaglyph Type Items](bpy_types_enum_items/stereo3d_anaglyph_type_items.md#rna-enum-stereo3d-anaglyph-type-items)]

<a id="bpy.types.Stereo3dFormat.display_mode"></a>

#### bpy.types.Stereo3dFormat.display_mode

(default `'ANAGLYPH'`)

- `ANAGLYPH`
  Anaglyph – Render views for left and right eyes as two differently filtered colors in a single image (anaglyph glasses are required).
- `INTERLACE`
  Interlace – Render views for left and right eyes interlaced in a single image (3D-ready monitor is required).
- `SIDEBYSIDE`
  Side-by-Side – Render views for left and right eyes side-by-side.
- `TOPBOTTOM`
  Top-Bottom – Render views for left and right eyes one above another.

**Type:**

Literal[‘ANAGLYPH’, ‘INTERLACE’, ‘SIDEBYSIDE’, ‘TOPBOTTOM’]

<a id="bpy.types.Stereo3dFormat.interlace_type"></a>

#### bpy.types.Stereo3dFormat.interlace_type

(default `'ROW_INTERLEAVED'`)

**Type:**

Literal[[Stereo3D Interlace Type Items](bpy_types_enum_items/stereo3d_interlace_type_items.md#rna-enum-stereo3d-interlace-type-items)]

<a id="bpy.types.Stereo3dFormat.use_interlace_swap"></a>

#### bpy.types.Stereo3dFormat.use_interlace_swap

Swap left and right stereo channels (default False)

**Type:**

bool

<a id="bpy.types.Stereo3dFormat.use_sidebyside_crosseyed"></a>

#### bpy.types.Stereo3dFormat.use_sidebyside_crosseyed

Right eye should see left image and vice versa (default False)

**Type:**

bool

<a id="bpy.types.Stereo3dFormat.use_squeezed_frame"></a>

#### bpy.types.Stereo3dFormat.use_squeezed_frame

Combine both views in a squeezed image (default False)

**Type:**

bool

<a id="bpy.types.Stereo3dFormat.bl_rna_get_subclass"></a>

#### classmethod bpy.types.Stereo3dFormat.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.Stereo3dFormat.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.Stereo3dFormat.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Image.stereo_3d_format`](bpy.types.Image.md#bpy.types.Image.stereo_3d_format "bpy.types.Image.stereo_3d_format") - [`ImageStrip.stereo_3d_format`](bpy.types.ImageStrip.md#bpy.types.ImageStrip.stereo_3d_format "bpy.types.ImageStrip.stereo_3d_format") - [`MovieStrip.stereo_3d_format`](bpy.types.MovieStrip.md#bpy.types.MovieStrip.stereo_3d_format "bpy.types.MovieStrip.stereo_3d_format") | - [`ImageFormatSettings.stereo_3d_format`](bpy.types.ImageFormatSettings.md#bpy.types.ImageFormatSettings.stereo_3d_format "bpy.types.ImageFormatSettings.stereo_3d_format") - [`UILayout.template_image_stereo_3d`](bpy.types.UILayout.md#bpy.types.UILayout.template_image_stereo_3d "bpy.types.UILayout.template_image_stereo_3d") |
