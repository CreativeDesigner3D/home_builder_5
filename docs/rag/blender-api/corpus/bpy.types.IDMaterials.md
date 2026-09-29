<!-- source: Blender Python API reference 5.2 / bpy.types.IDMaterials.html -->

<a id="idmaterials-bpy-prop-collection"></a>

# IDMaterials(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.IDMaterials"></a>

### class bpy.types.IDMaterials(bpy_prop_collection)

Collection of materials

<a id="bpy.types.IDMaterials.append"></a>

#### bpy.types.IDMaterials.append(material)

Add a new material to the data-block

**Parameters:**

**material** ([`Material`](bpy.types.Material.md#bpy.types.Material "bpy.types.Material") | None) – Material to add

<a id="bpy.types.IDMaterials.pop"></a>

#### bpy.types.IDMaterials.pop(*, index=-1)

Remove a material from the data-block

**Parameters:**

**index** (int) – Index of material to remove (in [-32766, 32766], optional)

**Returns:**

Material to remove

**Return type:**

[`Material`](bpy.types.Material.md#bpy.types.Material "bpy.types.Material")

<a id="bpy.types.IDMaterials.clear"></a>

#### bpy.types.IDMaterials.clear()

Remove all materials from the data-block

<a id="bpy.types.IDMaterials.bl_rna_get_subclass"></a>

#### classmethod bpy.types.IDMaterials.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.IDMaterials.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.IDMaterials.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Curve.materials`](bpy.types.Curve.md#bpy.types.Curve.materials "bpy.types.Curve.materials") - [`Curves.materials`](bpy.types.Curves.md#bpy.types.Curves.materials "bpy.types.Curves.materials") - [`GreasePencil.materials`](bpy.types.GreasePencil.md#bpy.types.GreasePencil.materials "bpy.types.GreasePencil.materials") - [`Mesh.materials`](bpy.types.Mesh.md#bpy.types.Mesh.materials "bpy.types.Mesh.materials") | - [`MetaBall.materials`](bpy.types.MetaBall.md#bpy.types.MetaBall.materials "bpy.types.MetaBall.materials") - [`PointCloud.materials`](bpy.types.PointCloud.md#bpy.types.PointCloud.materials "bpy.types.PointCloud.materials") - [`Volume.materials`](bpy.types.Volume.md#bpy.types.Volume.materials "bpy.types.Volume.materials") |
