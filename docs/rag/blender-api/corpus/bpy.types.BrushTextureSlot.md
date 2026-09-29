<!-- source: Blender Python API reference 5.2 / bpy.types.BrushTextureSlot.html -->

<a id="brushtextureslot-textureslot"></a>

# BrushTextureSlot(TextureSlot)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`TextureSlot`](bpy.types.TextureSlot.md#bpy.types.TextureSlot "bpy.types.TextureSlot")

<a id="bpy.types.BrushTextureSlot"></a>

### class bpy.types.BrushTextureSlot(TextureSlot)

Texture slot for textures in a Brush data-block

<a id="bpy.types.BrushTextureSlot.angle"></a>

#### bpy.types.BrushTextureSlot.angle

Brush texture rotation (in [0, 6.28319], default 0.0)

**Type:**

float

<a id="bpy.types.BrushTextureSlot.has_random_texture_angle"></a>

#### bpy.types.BrushTextureSlot.has_random_texture_angle

(default False, readonly)

**Type:**

bool

<a id="bpy.types.BrushTextureSlot.has_texture_angle"></a>

#### bpy.types.BrushTextureSlot.has_texture_angle

(default False, readonly)

**Type:**

bool

<a id="bpy.types.BrushTextureSlot.has_texture_angle_source"></a>

#### bpy.types.BrushTextureSlot.has_texture_angle_source

(default False, readonly)

**Type:**

bool

<a id="bpy.types.BrushTextureSlot.map_mode"></a>

#### bpy.types.BrushTextureSlot.map_mode

(default `'VIEW_PLANE'`)

**Type:**

Literal[‘VIEW_PLANE’, ‘AREA_PLANE’, ‘TILED’, ‘3D’, ‘RANDOM’, ‘STENCIL’]

<a id="bpy.types.BrushTextureSlot.mask_map_mode"></a>

#### bpy.types.BrushTextureSlot.mask_map_mode

(default `'VIEW_PLANE'`)

**Type:**

Literal[‘VIEW_PLANE’, ‘TILED’, ‘RANDOM’, ‘STENCIL’]

<a id="bpy.types.BrushTextureSlot.random_angle"></a>

#### bpy.types.BrushTextureSlot.random_angle

Brush texture random angle (in [0, 6.28319], default 6.28319)

**Type:**

float

<a id="bpy.types.BrushTextureSlot.use_rake"></a>

#### bpy.types.BrushTextureSlot.use_rake

(default False)

**Type:**

bool

<a id="bpy.types.BrushTextureSlot.use_random"></a>

#### bpy.types.BrushTextureSlot.use_random

(default False)

**Type:**

bool

<a id="bpy.types.BrushTextureSlot.bl_rna_get_subclass"></a>

#### classmethod bpy.types.BrushTextureSlot.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.BrushTextureSlot.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.BrushTextureSlot.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, TextureSlot.texture, TextureSlot.name, TextureSlot.offset, TextureSlot.scale, TextureSlot.color, TextureSlot.blend_type, TextureSlot.default_value, TextureSlot.output_node

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, TextureSlot.bl_rna_get_subclass, TextureSlot.bl_rna_get_subclass_py

<a id="references"></a>

## References

|  |  |
| --- | --- |
| - [`Brush.mask_texture_slot`](bpy.types.Brush.md#bpy.types.Brush.mask_texture_slot "bpy.types.Brush.mask_texture_slot") | - [`Brush.texture_slot`](bpy.types.Brush.md#bpy.types.Brush.texture_slot "bpy.types.Brush.texture_slot") |
