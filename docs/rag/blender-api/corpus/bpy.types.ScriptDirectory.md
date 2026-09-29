<!-- source: Blender Python API reference 5.2 / bpy.types.ScriptDirectory.html -->

<a id="scriptdirectory-bpy-struct"></a>

# ScriptDirectory(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.ScriptDirectory"></a>

### class bpy.types.ScriptDirectory(bpy_struct)

<a id="bpy.types.ScriptDirectory.directory"></a>

#### bpy.types.ScriptDirectory.directory

Alternate script path, matching the default layout with sub-directories: startup, add-ons, modules, and presets (requires restart) (default “”, never None)

**Type:**

str

<a id="bpy.types.ScriptDirectory.name"></a>

#### bpy.types.ScriptDirectory.name

Identifier for the Python scripts directory (default “”, never None)

**Type:**

str

<a id="bpy.types.ScriptDirectory.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ScriptDirectory.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ScriptDirectory.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ScriptDirectory.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`PreferencesFilePaths.script_directories`](bpy.types.PreferencesFilePaths.md#bpy.types.PreferencesFilePaths.script_directories "bpy.types.PreferencesFilePaths.script_directories") - [`ScriptDirectoryCollection.new`](bpy.types.ScriptDirectoryCollection.md#bpy.types.ScriptDirectoryCollection.new "bpy.types.ScriptDirectoryCollection.new") | - [`ScriptDirectoryCollection.remove`](bpy.types.ScriptDirectoryCollection.md#bpy.types.ScriptDirectoryCollection.remove "bpy.types.ScriptDirectoryCollection.remove") |
