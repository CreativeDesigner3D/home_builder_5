<!-- source: Blender Python API reference 5.2 / bpy.types.ShaderFxShadow.html -->

<a id="shaderfxshadow-shaderfx"></a>

# ShaderFxShadow(ShaderFx)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`ShaderFx`](bpy.types.ShaderFx.md#bpy.types.ShaderFx "bpy.types.ShaderFx")

<a id="bpy.types.ShaderFxShadow"></a>

### class bpy.types.ShaderFxShadow(ShaderFx)

Shadow effect

<a id="bpy.types.ShaderFxShadow.amplitude"></a>

#### bpy.types.ShaderFxShadow.amplitude

Amplitude of Wave (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.ShaderFxShadow.blur"></a>

#### bpy.types.ShaderFxShadow.blur

Number of pixels for blurring shadow (set to 0 to disable) (array of 2 items, in [0, 32767], default (0, 0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[int]

<a id="bpy.types.ShaderFxShadow.object"></a>

#### bpy.types.ShaderFxShadow.object

Object to determine center of rotation

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.ShaderFxShadow.offset"></a>

#### bpy.types.ShaderFxShadow.offset

Offset of the shadow (array of 2 items, in [-32768, 32767], default (0, 0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[int]

<a id="bpy.types.ShaderFxShadow.orientation"></a>

#### bpy.types.ShaderFxShadow.orientation

Direction of the wave (default `'HORIZONTAL'`)

**Type:**

Literal[‘HORIZONTAL’, ‘VERTICAL’]

<a id="bpy.types.ShaderFxShadow.period"></a>

#### bpy.types.ShaderFxShadow.period

Period of Wave (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.ShaderFxShadow.phase"></a>

#### bpy.types.ShaderFxShadow.phase

Phase Shift of Wave (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.ShaderFxShadow.rotation"></a>

#### bpy.types.ShaderFxShadow.rotation

Rotation around center or object (in [-6.28319, 6.28319], default 0.0)

**Type:**

float

<a id="bpy.types.ShaderFxShadow.samples"></a>

#### bpy.types.ShaderFxShadow.samples

Number of Blur Samples (zero, disable blur) (in [0, 32], default 4)

**Type:**

int

<a id="bpy.types.ShaderFxShadow.scale"></a>

#### bpy.types.ShaderFxShadow.scale

Scale of the shadow (array of 2 items, in [-inf, inf], default (0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.ShaderFxShadow.shadow_color"></a>

#### bpy.types.ShaderFxShadow.shadow_color

Color used for Shadow (array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.ShaderFxShadow.use_object"></a>

#### bpy.types.ShaderFxShadow.use_object

Use object as center of rotation (default False)

**Type:**

bool

<a id="bpy.types.ShaderFxShadow.use_wave"></a>

#### bpy.types.ShaderFxShadow.use_wave

Use wave effect (default False)

**Type:**

bool

<a id="bpy.types.ShaderFxShadow.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ShaderFxShadow.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ShaderFxShadow.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ShaderFxShadow.bl_rna_get_subclass_py(id, default=None, /)

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
