<!-- source: Blender Python API reference 5.2 / bpy.types.FModifierNoise.html -->

<a id="fmodifiernoise-fmodifier"></a>

# FModifierNoise(FModifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`FModifier`](bpy.types.FModifier.md#bpy.types.FModifier "bpy.types.FModifier")

<a id="bpy.types.FModifierNoise"></a>

### class bpy.types.FModifierNoise(FModifier)

Give randomness to the modified F-Curve

<a id="bpy.types.FModifierNoise.blend_type"></a>

#### bpy.types.FModifierNoise.blend_type

Method of modifying the existing F-Curve (default `'REPLACE'`)

**Type:**

Literal[‘REPLACE’, ‘ADD’, ‘SUBTRACT’, ‘MULTIPLY’]

<a id="bpy.types.FModifierNoise.depth"></a>

#### bpy.types.FModifierNoise.depth

Amount of fine level detail present in the noise (in [0, 32767], default 0)

**Type:**

int

<a id="bpy.types.FModifierNoise.lacunarity"></a>

#### bpy.types.FModifierNoise.lacunarity

Gap between successive frequencies. Depth needs to be greater than 0 for this to have an effect (in [-inf, inf], default 2.0)

**Type:**

float

<a id="bpy.types.FModifierNoise.offset"></a>

#### bpy.types.FModifierNoise.offset

Time offset for the noise effect (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.FModifierNoise.phase"></a>

#### bpy.types.FModifierNoise.phase

A random seed for the noise effect (in [-inf, inf], default 1.0)

**Type:**

float

<a id="bpy.types.FModifierNoise.roughness"></a>

#### bpy.types.FModifierNoise.roughness

Amount of high frequency detail. Depth needs to be greater than 0 for this to have an effect (in [-inf, inf], default 0.5)

**Type:**

float

<a id="bpy.types.FModifierNoise.scale"></a>

#### bpy.types.FModifierNoise.scale

Scaling (in time) of the noise (in [-inf, inf], default 1.0)

**Type:**

float

<a id="bpy.types.FModifierNoise.strength"></a>

#### bpy.types.FModifierNoise.strength

Amplitude of the noise - the amount that it modifies the underlying curve (in [-inf, inf], default 1.0)

**Type:**

float

<a id="bpy.types.FModifierNoise.use_legacy_noise"></a>

#### bpy.types.FModifierNoise.use_legacy_noise

Use the legacy way of generating noise. Has the issue that it can produce values outside of -1/1 (default False)

**Type:**

bool

<a id="bpy.types.FModifierNoise.bl_rna_get_subclass"></a>

#### classmethod bpy.types.FModifierNoise.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.FModifierNoise.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.FModifierNoise.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, FModifier.name, FModifier.type, FModifier.show_expanded, FModifier.mute, FModifier.is_valid, FModifier.active, FModifier.use_restricted_range, FModifier.frame_start, FModifier.frame_end, FModifier.blend_in, FModifier.blend_out, FModifier.use_influence, FModifier.influence

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, FModifier.bl_rna_get_subclass, FModifier.bl_rna_get_subclass_py
