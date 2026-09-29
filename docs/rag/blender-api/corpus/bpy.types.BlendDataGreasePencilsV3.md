<!-- source: Blender Python API reference 5.2 / bpy.types.BlendDataGreasePencilsV3.html -->

<a id="blenddatagreasepencilsv3-bpy-prop-collection"></a>

# BlendDataGreasePencilsV3(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.BlendDataGreasePencilsV3"></a>

### class bpy.types.BlendDataGreasePencilsV3(bpy_prop_collection)

Collection of Grease Pencils

<a id="bpy.types.BlendDataGreasePencilsV3.tag"></a>

#### bpy.types.BlendDataGreasePencilsV3.tag(value)

tag

**Parameters:**

**value** (bool) – Value

<a id="bpy.types.BlendDataGreasePencilsV3.new"></a>

#### bpy.types.BlendDataGreasePencilsV3.new(name)

Add a new Grease Pencil data-block to the main database

**Parameters:**

**name** (str) – New name for the data-block (never None)

**Returns:**

New Grease Pencil data-block

**Return type:**

[`GreasePencil`](bpy.types.GreasePencil.md#bpy.types.GreasePencil "bpy.types.GreasePencil")

<a id="bpy.types.BlendDataGreasePencilsV3.remove"></a>

#### bpy.types.BlendDataGreasePencilsV3.remove(grease_pencil, *, do_unlink=True, do_id_user=True, do_ui_user=True)

Remove a Grease Pencil instance from the current blendfile

**Parameters:**

- **grease_pencil** ([`GreasePencil`](bpy.types.GreasePencil.md#bpy.types.GreasePencil "bpy.types.GreasePencil") | None) – Grease Pencil to remove (never None)
- **do_unlink** (bool) – Unlink all usages of this Grease Pencil before deleting it (optional)
- **do_id_user** (bool) – Decrement user counter of all data-blocks used by this Grease Pencil (optional)
- **do_ui_user** (bool) – Make sure interface does not reference this Grease Pencil (optional)

<a id="bpy.types.BlendDataGreasePencilsV3.bl_rna_get_subclass"></a>

#### classmethod bpy.types.BlendDataGreasePencilsV3.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.BlendDataGreasePencilsV3.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.BlendDataGreasePencilsV3.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`BlendData.grease_pencils`](bpy.types.BlendData.md#bpy.types.BlendData.grease_pencils "bpy.types.BlendData.grease_pencils") |  |
