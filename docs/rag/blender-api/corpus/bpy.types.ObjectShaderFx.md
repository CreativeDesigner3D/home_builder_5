<!-- source: Blender Python API reference 5.2 / bpy.types.ObjectShaderFx.html -->

<a id="objectshaderfx-bpy-prop-collection"></a>

# ObjectShaderFx(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.ObjectShaderFx"></a>

### class bpy.types.ObjectShaderFx(bpy_prop_collection)

Collection of object effects

<a id="bpy.types.ObjectShaderFx.new"></a>

#### bpy.types.ObjectShaderFx.new(name, type)

Add a new shader fx

**Parameters:**

- **name** (str) – New name for the effect (never None)
- **type** (Literal[[Object Shaderfx Type Items](bpy_types_enum_items/object_shaderfx_type_items.md#rna-enum-object-shaderfx-type-items)]) – Effect type to add

**Returns:**

Newly created effect

**Return type:**

[`ShaderFx`](bpy.types.ShaderFx.md#bpy.types.ShaderFx "bpy.types.ShaderFx")

<a id="bpy.types.ObjectShaderFx.remove"></a>

#### bpy.types.ObjectShaderFx.remove(shader_fx)

Remove an existing effect from the object

**Parameters:**

**shader_fx** ([`ShaderFx`](bpy.types.ShaderFx.md#bpy.types.ShaderFx "bpy.types.ShaderFx") | None) – Effect to remove (never None)

<a id="bpy.types.ObjectShaderFx.clear"></a>

#### bpy.types.ObjectShaderFx.clear()

Remove all effects from the object

<a id="bpy.types.ObjectShaderFx.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ObjectShaderFx.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ObjectShaderFx.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ObjectShaderFx.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Object.shader_effects`](bpy.types.Object.md#bpy.types.Object.shader_effects "bpy.types.Object.shader_effects") |  |
