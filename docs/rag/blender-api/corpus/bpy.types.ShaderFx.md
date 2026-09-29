<!-- source: Blender Python API reference 5.2 / bpy.types.ShaderFx.html -->

<a id="shaderfx-bpy-struct"></a>

# ShaderFx(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

Subclasses

- [ShaderFxBlur(ShaderFx)](bpy.types.ShaderFxBlur.md)
- [ShaderFxColorize(ShaderFx)](bpy.types.ShaderFxColorize.md)
- [ShaderFxFlip(ShaderFx)](bpy.types.ShaderFxFlip.md)
- [ShaderFxGlow(ShaderFx)](bpy.types.ShaderFxGlow.md)
- [ShaderFxPixel(ShaderFx)](bpy.types.ShaderFxPixel.md)
- [ShaderFxRim(ShaderFx)](bpy.types.ShaderFxRim.md)
- [ShaderFxShadow(ShaderFx)](bpy.types.ShaderFxShadow.md)
- [ShaderFxSwirl(ShaderFx)](bpy.types.ShaderFxSwirl.md)
- [ShaderFxWave(ShaderFx)](bpy.types.ShaderFxWave.md)

<a id="bpy.types.ShaderFx"></a>

### class bpy.types.ShaderFx(bpy_struct)

Effect affecting the Grease Pencil object

<a id="bpy.types.ShaderFx.name"></a>

#### bpy.types.ShaderFx.name

Effect name (default “”, never None)

**Type:**

str

<a id="bpy.types.ShaderFx.show_expanded"></a>

#### bpy.types.ShaderFx.show_expanded

Set effect expansion in the user interface (default False)

**Type:**

bool

<a id="bpy.types.ShaderFx.show_in_editmode"></a>

#### bpy.types.ShaderFx.show_in_editmode

Display effect in Edit mode (default False)

**Type:**

bool

<a id="bpy.types.ShaderFx.show_render"></a>

#### bpy.types.ShaderFx.show_render

Use effect during render (default False)

**Type:**

bool

<a id="bpy.types.ShaderFx.show_viewport"></a>

#### bpy.types.ShaderFx.show_viewport

Display effect in viewport (default False)

**Type:**

bool

<a id="bpy.types.ShaderFx.type"></a>

#### bpy.types.ShaderFx.type

(default `'FX_BLUR'`, readonly)

**Type:**

Literal[[Object Shaderfx Type Items](bpy_types_enum_items/object_shaderfx_type_items.md#rna-enum-object-shaderfx-type-items)]

<a id="bpy.types.ShaderFx.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ShaderFx.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ShaderFx.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ShaderFx.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([type](#bpy.types.ShaderFx.type "bpy.types.ShaderFx.type") | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

[type](#bpy.types.ShaderFx.type "bpy.types.ShaderFx.type")

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
| - [`Object.shader_effects`](bpy.types.Object.md#bpy.types.Object.shader_effects "bpy.types.Object.shader_effects") - [`ObjectShaderFx.new`](bpy.types.ObjectShaderFx.md#bpy.types.ObjectShaderFx.new "bpy.types.ObjectShaderFx.new") | - [`ObjectShaderFx.remove`](bpy.types.ObjectShaderFx.md#bpy.types.ObjectShaderFx.remove "bpy.types.ObjectShaderFx.remove") |
