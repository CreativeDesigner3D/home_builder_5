<!-- source: Blender Python API reference 5.2 / bpy.types.BlendDataMeshes.html -->

<a id="blenddatameshes-bpy-prop-collection"></a>

# BlendDataMeshes(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.BlendDataMeshes"></a>

### class bpy.types.BlendDataMeshes(bpy_prop_collection)

Collection of meshes

<a id="bpy.types.BlendDataMeshes.new"></a>

#### bpy.types.BlendDataMeshes.new(name)

Add a new mesh to the main database

**Parameters:**

**name** (str) – New name for the data-block (never None)

**Returns:**

New mesh data-block

**Return type:**

[`Mesh`](bpy.types.Mesh.md#bpy.types.Mesh "bpy.types.Mesh")

<a id="bpy.types.BlendDataMeshes.new_from_object"></a>

#### bpy.types.BlendDataMeshes.new_from_object(object, *, preserve_all_data_layers=False, depsgraph=None)

Add a new mesh created from given object (undeformed geometry if object is original, and final evaluated geometry, with all modifiers etc., if object is evaluated)

**Parameters:**

- **object** ([`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None) – Object to create mesh from (never None)
- **preserve_all_data_layers** (bool) – Preserve all data layers in the mesh, like UV maps and vertex groups. By default Blender only computes the subset of data layers needed for viewport display and rendering, for better performance. (optional)
- **depsgraph** ([`Depsgraph`](bpy.types.Depsgraph.md#bpy.types.Depsgraph "bpy.types.Depsgraph") | None) – Dependency Graph, Evaluated dependency graph which is required when preserve_all_data_layers is true (optional)

**Returns:**

Mesh created from object, remove it if it is only used for export

**Return type:**

[`Mesh`](bpy.types.Mesh.md#bpy.types.Mesh "bpy.types.Mesh")

<a id="bpy.types.BlendDataMeshes.remove"></a>

#### bpy.types.BlendDataMeshes.remove(mesh, *, do_unlink=True, do_id_user=True, do_ui_user=True)

Remove a mesh from the current blendfile

**Parameters:**

- **mesh** ([`Mesh`](bpy.types.Mesh.md#bpy.types.Mesh "bpy.types.Mesh") | None) – Mesh to remove (never None)
- **do_unlink** (bool) – Unlink all usages of this mesh before deleting it (WARNING: will also delete objects instancing that mesh data) (optional)
- **do_id_user** (bool) – Decrement user counter of all data-blocks used by this mesh data (optional)
- **do_ui_user** (bool) – Make sure interface does not reference this mesh data (optional)

<a id="bpy.types.BlendDataMeshes.tag"></a>

#### bpy.types.BlendDataMeshes.tag(value)

tag

**Parameters:**

**value** (bool) – Value

<a id="bpy.types.BlendDataMeshes.bl_rna_get_subclass"></a>

#### classmethod bpy.types.BlendDataMeshes.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.BlendDataMeshes.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.BlendDataMeshes.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`BlendData.meshes`](bpy.types.BlendData.md#bpy.types.BlendData.meshes "bpy.types.BlendData.meshes") |  |
