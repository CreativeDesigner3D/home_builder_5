<!-- source: Blender Python API reference 5.2 / bpy.types.LineStyleTextureSlot.html -->

<a id="linestyletextureslot-textureslot"></a>

# LineStyleTextureSlot(TextureSlot)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`TextureSlot`](bpy.types.TextureSlot.md#bpy.types.TextureSlot "bpy.types.TextureSlot")

<a id="bpy.types.LineStyleTextureSlot"></a>

### class bpy.types.LineStyleTextureSlot(TextureSlot)

Texture slot for textures in a LineStyle data-block

<a id="bpy.types.LineStyleTextureSlot.alpha_factor"></a>

#### bpy.types.LineStyleTextureSlot.alpha_factor

Amount texture affects alpha (in [-inf, inf], default 1.0)

**Type:**

float

<a id="bpy.types.LineStyleTextureSlot.diffuse_color_factor"></a>

#### bpy.types.LineStyleTextureSlot.diffuse_color_factor

Amount texture affects diffuse color (in [-inf, inf], default 1.0)

**Type:**

float

<a id="bpy.types.LineStyleTextureSlot.mapping"></a>

#### bpy.types.LineStyleTextureSlot.mapping

(default `'FLAT'`)

- `FLAT`
  Flat – Map X and Y coordinates directly.
- `CUBE`
  Cube – Map using the normal vector.
- `TUBE`
  Tube – Map with Z as central axis.
- `SPHERE`
  Sphere – Map with Z as central axis.

**Type:**

Literal[‘FLAT’, ‘CUBE’, ‘TUBE’, ‘SPHERE’]

<a id="bpy.types.LineStyleTextureSlot.mapping_x"></a>

#### bpy.types.LineStyleTextureSlot.mapping_x

(default `'X'`)

**Type:**

Literal[‘NONE’, ‘X’, ‘Y’, ‘Z’]

<a id="bpy.types.LineStyleTextureSlot.mapping_y"></a>

#### bpy.types.LineStyleTextureSlot.mapping_y

(default `'Y'`)

**Type:**

Literal[‘NONE’, ‘X’, ‘Y’, ‘Z’]

<a id="bpy.types.LineStyleTextureSlot.mapping_z"></a>

#### bpy.types.LineStyleTextureSlot.mapping_z

(default `'Z'`)

**Type:**

Literal[‘NONE’, ‘X’, ‘Y’, ‘Z’]

<a id="bpy.types.LineStyleTextureSlot.texture_coords"></a>

#### bpy.types.LineStyleTextureSlot.texture_coords

Texture coordinates used to map the texture onto the background (default `'ALONG_STROKE'`)

- `WINDOW`
  Window – Use screen coordinates as texture coordinates.
- `GLOBAL`
  Global – Use global coordinates for the texture coordinates.
- `ALONG_STROKE`
  Along stroke – Use stroke length for texture coordinates.
- `ORCO`
  Generated – Use the original undeformed coordinates of the object.

**Type:**

Literal[‘WINDOW’, ‘GLOBAL’, ‘ALONG_STROKE’, ‘ORCO’]

<a id="bpy.types.LineStyleTextureSlot.use_map_alpha"></a>

#### bpy.types.LineStyleTextureSlot.use_map_alpha

The texture affects the alpha value (default False)

**Type:**

bool

<a id="bpy.types.LineStyleTextureSlot.use_map_color_diffuse"></a>

#### bpy.types.LineStyleTextureSlot.use_map_color_diffuse

The texture affects basic color of the stroke (default True)

**Type:**

bool

<a id="bpy.types.LineStyleTextureSlot.bl_rna_get_subclass"></a>

#### classmethod bpy.types.LineStyleTextureSlot.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.LineStyleTextureSlot.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.LineStyleTextureSlot.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`FreestyleLineStyle.texture_slots`](bpy.types.FreestyleLineStyle.md#bpy.types.FreestyleLineStyle.texture_slots "bpy.types.FreestyleLineStyle.texture_slots") - [`LineStyleTextureSlots.add`](bpy.types.LineStyleTextureSlots.md#bpy.types.LineStyleTextureSlots.add "bpy.types.LineStyleTextureSlots.add") | - [`LineStyleTextureSlots.create`](bpy.types.LineStyleTextureSlots.md#bpy.types.LineStyleTextureSlots.create "bpy.types.LineStyleTextureSlots.create") |
