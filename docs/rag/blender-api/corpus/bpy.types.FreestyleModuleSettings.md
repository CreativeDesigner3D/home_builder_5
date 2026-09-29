<!-- source: Blender Python API reference 5.2 / bpy.types.FreestyleModuleSettings.html -->

<a id="freestylemodulesettings-bpy-struct"></a>

# FreestyleModuleSettings(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.FreestyleModuleSettings"></a>

### class bpy.types.FreestyleModuleSettings(bpy_struct)

Style module configuration for specifying a style module

<a id="bpy.types.FreestyleModuleSettings.script"></a>

#### bpy.types.FreestyleModuleSettings.script

Python script to define a style module

**Type:**

[`Text`](bpy.types.Text.md#bpy.types.Text "bpy.types.Text") | None

<a id="bpy.types.FreestyleModuleSettings.use"></a>

#### bpy.types.FreestyleModuleSettings.use

Enable or disable this style module during stroke rendering (default False)

**Type:**

bool

<a id="bpy.types.FreestyleModuleSettings.bl_rna_get_subclass"></a>

#### classmethod bpy.types.FreestyleModuleSettings.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.FreestyleModuleSettings.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.FreestyleModuleSettings.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`FreestyleModules.new`](bpy.types.FreestyleModules.md#bpy.types.FreestyleModules.new "bpy.types.FreestyleModules.new") - [`FreestyleModules.remove`](bpy.types.FreestyleModules.md#bpy.types.FreestyleModules.remove "bpy.types.FreestyleModules.remove") | - [`FreestyleSettings.modules`](bpy.types.FreestyleSettings.md#bpy.types.FreestyleSettings.modules "bpy.types.FreestyleSettings.modules") |
