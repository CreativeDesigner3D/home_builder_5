<!-- source: Blender Python API reference 5.2 / bpy.types.ShaderFxRim.html -->

<a id="shaderfxrim-shaderfx"></a>

# ShaderFxRim(ShaderFx)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`ShaderFx`](bpy.types.ShaderFx.md#bpy.types.ShaderFx "bpy.types.ShaderFx")

<a id="bpy.types.ShaderFxRim"></a>

### class bpy.types.ShaderFxRim(ShaderFx)

Rim effect

<a id="bpy.types.ShaderFxRim.blur"></a>

#### bpy.types.ShaderFxRim.blur

Number of pixels for blurring rim (set to 0 to disable) (array of 2 items, in [0, 32767], default (0, 0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[int]

<a id="bpy.types.ShaderFxRim.mask_color"></a>

#### bpy.types.ShaderFxRim.mask_color

Color that must be kept (array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ShaderFxRim.mode"></a>

#### bpy.types.ShaderFxRim.mode

Blend mode (default `'NORMAL'`)

**Type:**

Literal[‘NORMAL’, ‘OVERLAY’, ‘ADD’, ‘SUBTRACT’, ‘MULTIPLY’, ‘DIVIDE’]

<a id="bpy.types.ShaderFxRim.offset"></a>

#### bpy.types.ShaderFxRim.offset

Offset of the rim (array of 2 items, in [-32768, 32767], default (0, 0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[int]

<a id="bpy.types.ShaderFxRim.rim_color"></a>

#### bpy.types.ShaderFxRim.rim_color

Color used for Rim (array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ShaderFxRim.samples"></a>

#### bpy.types.ShaderFxRim.samples

Number of Blur Samples (zero, disable blur) (in [0, 32], default 4)

**Type:**

int

<a id="bpy.types.ShaderFxRim.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ShaderFxRim.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ShaderFxRim.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ShaderFxRim.bl_rna_get_subclass_py(id, default=None, /)

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
