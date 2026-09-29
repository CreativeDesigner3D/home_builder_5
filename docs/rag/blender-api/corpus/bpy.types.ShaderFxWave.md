<!-- source: Blender Python API reference 5.2 / bpy.types.ShaderFxWave.html -->

<a id="shaderfxwave-shaderfx"></a>

# ShaderFxWave(ShaderFx)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`ShaderFx`](bpy.types.ShaderFx.md#bpy.types.ShaderFx "bpy.types.ShaderFx")

<a id="bpy.types.ShaderFxWave"></a>

### class bpy.types.ShaderFxWave(ShaderFx)

Wave Deformation effect

<a id="bpy.types.ShaderFxWave.amplitude"></a>

#### bpy.types.ShaderFxWave.amplitude

Amplitude of Wave (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.ShaderFxWave.orientation"></a>

#### bpy.types.ShaderFxWave.orientation

Direction of the wave (default `'HORIZONTAL'`)

**Type:**

Literal[‘HORIZONTAL’, ‘VERTICAL’]

<a id="bpy.types.ShaderFxWave.period"></a>

#### bpy.types.ShaderFxWave.period

Period of Wave (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.ShaderFxWave.phase"></a>

#### bpy.types.ShaderFxWave.phase

Phase Shift of Wave (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.ShaderFxWave.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ShaderFxWave.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ShaderFxWave.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ShaderFxWave.bl_rna_get_subclass_py(id, default=None, /)

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
