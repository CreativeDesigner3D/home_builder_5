<!-- source: Blender Python API reference 5.2 / bpy.types.TextureSlot.html -->

<a id="textureslot-bpy-struct"></a>

# TextureSlot(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

Subclasses

- [BrushTextureSlot(TextureSlot)](bpy.types.BrushTextureSlot.md)
- [LineStyleTextureSlot(TextureSlot)](bpy.types.LineStyleTextureSlot.md)
- [ParticleSettingsTextureSlot(TextureSlot)](bpy.types.ParticleSettingsTextureSlot.md)

<a id="bpy.types.TextureSlot"></a>

### class bpy.types.TextureSlot(bpy_struct)

Texture slot defining the mapping and influence of a texture

<a id="bpy.types.TextureSlot.blend_type"></a>

#### bpy.types.TextureSlot.blend_type

Mode used to apply the texture (default `'MIX'`)

**Type:**

Literal[‘MIX’, ‘DARKEN’, ‘MULTIPLY’, ‘LIGHTEN’, ‘SCREEN’, ‘ADD’, ‘OVERLAY’, ‘SOFT_LIGHT’, ‘LINEAR_LIGHT’, ‘DIFFERENCE’, ‘SUBTRACT’, ‘DIVIDE’, ‘HUE’, ‘SATURATION’, ‘COLOR’, ‘VALUE’]

<a id="bpy.types.TextureSlot.color"></a>

#### bpy.types.TextureSlot.color

Default color for textures that don’t return RGB or when RGB to intensity is enabled (array of 3 items, in [0, inf], default (1.0, 1.0, 1.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.TextureSlot.default_value"></a>

#### bpy.types.TextureSlot.default_value

Value to use for Ref, Spec, Amb, Emit, Alpha, RayMir, TransLu and Hard (in [-inf, inf], default 1.0)

**Type:**

float

<a id="bpy.types.TextureSlot.name"></a>

#### bpy.types.TextureSlot.name

Texture slot name (default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.TextureSlot.offset"></a>

#### bpy.types.TextureSlot.offset

Fine tune of the texture mapping X, Y and Z locations (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.TextureSlot.output_node"></a>

#### bpy.types.TextureSlot.output_node

Which output node to use, for node-based textures (default `'DEFAULT'`)

**Type:**

Literal[‘DEFAULT’]

<a id="bpy.types.TextureSlot.scale"></a>

#### bpy.types.TextureSlot.scale

Set scaling for the texture’s X, Y and Z sizes (array of 3 items, in [-inf, inf], default (1.0, 1.0, 1.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.TextureSlot.texture"></a>

#### bpy.types.TextureSlot.texture

Texture data-block used by this texture slot

**Type:**

[`Texture`](bpy.types.Texture.md#bpy.types.Texture "bpy.types.Texture") | None

<a id="bpy.types.TextureSlot.bl_rna_get_subclass"></a>

#### classmethod bpy.types.TextureSlot.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.TextureSlot.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.TextureSlot.bl_rna_get_subclass_py(id, default=None, /)

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
| - `bpy.context.texture_slot` | - [`UILayout.template_preview`](bpy.types.UILayout.md#bpy.types.UILayout.template_preview "bpy.types.UILayout.template_preview") |
