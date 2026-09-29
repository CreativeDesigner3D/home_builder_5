<!-- source: Blender Python API reference 5.2 / bpy.types.ShaderFxGlow.html -->

<a id="shaderfxglow-shaderfx"></a>

# ShaderFxGlow(ShaderFx)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`ShaderFx`](bpy.types.ShaderFx.md#bpy.types.ShaderFx "bpy.types.ShaderFx")

<a id="bpy.types.ShaderFxGlow"></a>

### class bpy.types.ShaderFxGlow(ShaderFx)

Glow effect

<a id="bpy.types.ShaderFxGlow.blend_mode"></a>

#### bpy.types.ShaderFxGlow.blend_mode

Blend mode (default `'REGULAR'`)

**Type:**

Literal[‘REGULAR’, ‘ADD’, ‘SUBTRACT’, ‘MULTIPLY’, ‘DIVIDE’]

<a id="bpy.types.ShaderFxGlow.glow_color"></a>

#### bpy.types.ShaderFxGlow.glow_color

Color used for generated glow (array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ShaderFxGlow.mode"></a>

#### bpy.types.ShaderFxGlow.mode

Glow mode (default `'LUMINANCE'`)

**Type:**

Literal[‘LUMINANCE’, ‘COLOR’]

<a id="bpy.types.ShaderFxGlow.opacity"></a>

#### bpy.types.ShaderFxGlow.opacity

Effect Opacity (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.ShaderFxGlow.rotation"></a>

#### bpy.types.ShaderFxGlow.rotation

Rotation of the effect (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.ShaderFxGlow.samples"></a>

#### bpy.types.ShaderFxGlow.samples

Number of Blur Samples (in [1, 32], default 4)

**Type:**

int

<a id="bpy.types.ShaderFxGlow.select_color"></a>

#### bpy.types.ShaderFxGlow.select_color

Color selected to apply glow (array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ShaderFxGlow.size"></a>

#### bpy.types.ShaderFxGlow.size

Size of the effect (array of 2 items, in [0, inf], default (0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.ShaderFxGlow.threshold"></a>

#### bpy.types.ShaderFxGlow.threshold

Limit to select color for glow effect (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.ShaderFxGlow.use_glow_under"></a>

#### bpy.types.ShaderFxGlow.use_glow_under

Glow only areas with alpha (not supported with Regular blend mode) (default False)

**Type:**

bool

<a id="bpy.types.ShaderFxGlow.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ShaderFxGlow.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ShaderFxGlow.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ShaderFxGlow.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, ShaderFx.name, ShaderFx.type, ShaderFx.show_viewport, ShaderFx.show_render, ShaderFx.show_in_editmode, ShaderFx.show_expanded

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, ShaderFx.bl_rna_get_subclass, ShaderFx.bl_rna_get_subclass_py
