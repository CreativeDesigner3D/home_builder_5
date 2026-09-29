<!-- source: Blender Python API reference 5.2 / bpy.types.FreestyleModules.html -->

<a id="freestylemodules-bpy-prop-collection"></a>

# FreestyleModules(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.FreestyleModules"></a>

### class bpy.types.FreestyleModules(bpy_prop_collection)

A list of style modules (to be applied from top to bottom)

<a id="bpy.types.FreestyleModules.new"></a>

#### bpy.types.FreestyleModules.new()

Add a style module to scene render layer Freestyle settings

**Returns:**

Newly created style module

**Return type:**

[`FreestyleModuleSettings`](bpy.types.FreestyleModuleSettings.md#bpy.types.FreestyleModuleSettings "bpy.types.FreestyleModuleSettings")

<a id="bpy.types.FreestyleModules.remove"></a>

#### bpy.types.FreestyleModules.remove(module)

Remove a style module from scene render layer Freestyle settings

**Parameters:**

**module** ([`FreestyleModuleSettings`](bpy.types.FreestyleModuleSettings.md#bpy.types.FreestyleModuleSettings "bpy.types.FreestyleModuleSettings") | None) – Style module to remove (never None)

<a id="bpy.types.FreestyleModules.bl_rna_get_subclass"></a>

#### classmethod bpy.types.FreestyleModules.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.FreestyleModules.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.FreestyleModules.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`FreestyleSettings.modules`](bpy.types.FreestyleSettings.md#bpy.types.FreestyleSettings.modules "bpy.types.FreestyleSettings.modules") |  |
