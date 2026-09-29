<!-- source: Blender Python API reference 5.2 / bpy.types.TexMapping.html -->

<a id="texmapping-bpy-struct"></a>

# TexMapping(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.TexMapping"></a>

### class bpy.types.TexMapping(bpy_struct)

Texture coordinate mapping settings

<a id="bpy.types.TexMapping.mapping"></a>

#### bpy.types.TexMapping.mapping

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

<a id="bpy.types.TexMapping.mapping_x"></a>

#### bpy.types.TexMapping.mapping_x

(default `'NONE'`)

**Type:**

Literal[‘NONE’, ‘X’, ‘Y’, ‘Z’]

<a id="bpy.types.TexMapping.mapping_y"></a>

#### bpy.types.TexMapping.mapping_y

(default `'NONE'`)

**Type:**

Literal[‘NONE’, ‘X’, ‘Y’, ‘Z’]

<a id="bpy.types.TexMapping.mapping_z"></a>

#### bpy.types.TexMapping.mapping_z

(default `'NONE'`)

**Type:**

Literal[‘NONE’, ‘X’, ‘Y’, ‘Z’]

<a id="bpy.types.TexMapping.max"></a>

#### bpy.types.TexMapping.max

Maximum value for clipping (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.TexMapping.min"></a>

#### bpy.types.TexMapping.min

Minimum value for clipping (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.TexMapping.rotation"></a>

#### bpy.types.TexMapping.rotation

(array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler")

<a id="bpy.types.TexMapping.scale"></a>

#### bpy.types.TexMapping.scale

(array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.TexMapping.translation"></a>

#### bpy.types.TexMapping.translation

(array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.TexMapping.use_max"></a>

#### bpy.types.TexMapping.use_max

Whether to use maximum clipping value (default False)

**Type:**

bool

<a id="bpy.types.TexMapping.use_min"></a>

#### bpy.types.TexMapping.use_min

Whether to use minimum clipping value (default False)

**Type:**

bool

<a id="bpy.types.TexMapping.vector_type"></a>

#### bpy.types.TexMapping.vector_type

Type of vector that the mapping transforms (default `'POINT'`)

**Type:**

Literal[[Mapping Type Items](bpy_types_enum_items/mapping_type_items.md#rna-enum-mapping-type-items)]

<a id="bpy.types.TexMapping.bl_rna_get_subclass"></a>

#### classmethod bpy.types.TexMapping.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.TexMapping.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.TexMapping.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`ShaderNodeTexBrick.texture_mapping`](bpy.types.ShaderNodeTexBrick.md#bpy.types.ShaderNodeTexBrick.texture_mapping "bpy.types.ShaderNodeTexBrick.texture_mapping") - [`ShaderNodeTexChecker.texture_mapping`](bpy.types.ShaderNodeTexChecker.md#bpy.types.ShaderNodeTexChecker.texture_mapping "bpy.types.ShaderNodeTexChecker.texture_mapping") - [`ShaderNodeTexEnvironment.texture_mapping`](bpy.types.ShaderNodeTexEnvironment.md#bpy.types.ShaderNodeTexEnvironment.texture_mapping "bpy.types.ShaderNodeTexEnvironment.texture_mapping") - [`ShaderNodeTexGabor.texture_mapping`](bpy.types.ShaderNodeTexGabor.md#bpy.types.ShaderNodeTexGabor.texture_mapping "bpy.types.ShaderNodeTexGabor.texture_mapping") - [`ShaderNodeTexGradient.texture_mapping`](bpy.types.ShaderNodeTexGradient.md#bpy.types.ShaderNodeTexGradient.texture_mapping "bpy.types.ShaderNodeTexGradient.texture_mapping") - [`ShaderNodeTexImage.texture_mapping`](bpy.types.ShaderNodeTexImage.md#bpy.types.ShaderNodeTexImage.texture_mapping "bpy.types.ShaderNodeTexImage.texture_mapping") | - [`ShaderNodeTexMagic.texture_mapping`](bpy.types.ShaderNodeTexMagic.md#bpy.types.ShaderNodeTexMagic.texture_mapping "bpy.types.ShaderNodeTexMagic.texture_mapping") - [`ShaderNodeTexNoise.texture_mapping`](bpy.types.ShaderNodeTexNoise.md#bpy.types.ShaderNodeTexNoise.texture_mapping "bpy.types.ShaderNodeTexNoise.texture_mapping") - [`ShaderNodeTexSky.texture_mapping`](bpy.types.ShaderNodeTexSky.md#bpy.types.ShaderNodeTexSky.texture_mapping "bpy.types.ShaderNodeTexSky.texture_mapping") - [`ShaderNodeTexVoronoi.texture_mapping`](bpy.types.ShaderNodeTexVoronoi.md#bpy.types.ShaderNodeTexVoronoi.texture_mapping "bpy.types.ShaderNodeTexVoronoi.texture_mapping") - [`ShaderNodeTexWave.texture_mapping`](bpy.types.ShaderNodeTexWave.md#bpy.types.ShaderNodeTexWave.texture_mapping "bpy.types.ShaderNodeTexWave.texture_mapping") |
