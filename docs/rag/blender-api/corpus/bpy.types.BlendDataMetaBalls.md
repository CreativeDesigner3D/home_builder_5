<!-- source: Blender Python API reference 5.2 / bpy.types.BlendDataMetaBalls.html -->

<a id="blenddatametaballs-bpy-prop-collection"></a>

# BlendDataMetaBalls(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.BlendDataMetaBalls"></a>

### class bpy.types.BlendDataMetaBalls(bpy_prop_collection)

Collection of metaballs

<a id="bpy.types.BlendDataMetaBalls.new"></a>

#### bpy.types.BlendDataMetaBalls.new(name)

Add a new metaball to the main database

**Parameters:**

**name** (str) – New name for the data-block (never None)

**Returns:**

New metaball data-block

**Return type:**

[`MetaBall`](bpy.types.MetaBall.md#bpy.types.MetaBall "bpy.types.MetaBall")

<a id="bpy.types.BlendDataMetaBalls.remove"></a>

#### bpy.types.BlendDataMetaBalls.remove(metaball, *, do_unlink=True, do_id_user=True, do_ui_user=True)

Remove a metaball from the current blendfile

**Parameters:**

- **metaball** ([`MetaBall`](bpy.types.MetaBall.md#bpy.types.MetaBall "bpy.types.MetaBall") | None) – Metaball to remove (never None)
- **do_unlink** (bool) – Unlink all usages of this metaball before deleting it (WARNING: will also delete objects instancing that metaball data) (optional)
- **do_id_user** (bool) – Decrement user counter of all data-blocks used by this metaball data (optional)
- **do_ui_user** (bool) – Make sure interface does not reference this metaball data (optional)

<a id="bpy.types.BlendDataMetaBalls.tag"></a>

#### bpy.types.BlendDataMetaBalls.tag(value)

tag

**Parameters:**

**value** (bool) – Value

<a id="bpy.types.BlendDataMetaBalls.bl_rna_get_subclass"></a>

#### classmethod bpy.types.BlendDataMetaBalls.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.BlendDataMetaBalls.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.BlendDataMetaBalls.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`BlendData.metaballs`](bpy.types.BlendData.md#bpy.types.BlendData.metaballs "bpy.types.BlendData.metaballs") |  |
