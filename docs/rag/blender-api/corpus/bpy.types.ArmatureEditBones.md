<!-- source: Blender Python API reference 5.2 / bpy.types.ArmatureEditBones.html -->

<a id="armatureeditbones-bpy-prop-collection"></a>

# ArmatureEditBones(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.ArmatureEditBones"></a>

### class bpy.types.ArmatureEditBones(bpy_prop_collection)

Collection of armature edit bones

<a id="bpy.types.ArmatureEditBones.active"></a>

#### bpy.types.ArmatureEditBones.active

Armatures active edit bone

**Type:**

[`EditBone`](bpy.types.EditBone.md#bpy.types.EditBone "bpy.types.EditBone") | None

<a id="bpy.types.ArmatureEditBones.new"></a>

#### bpy.types.ArmatureEditBones.new(name)

Add a new bone

**Parameters:**

**name** (str) – New name for the bone (never None)

**Returns:**

Newly created edit bone

**Return type:**

[`EditBone`](bpy.types.EditBone.md#bpy.types.EditBone "bpy.types.EditBone")

<a id="bpy.types.ArmatureEditBones.remove"></a>

#### bpy.types.ArmatureEditBones.remove(bone)

Remove an existing bone from the armature

**Parameters:**

**bone** ([`EditBone`](bpy.types.EditBone.md#bpy.types.EditBone "bpy.types.EditBone") | None) – EditBone to remove (never None)

<a id="bpy.types.ArmatureEditBones.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ArmatureEditBones.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ArmatureEditBones.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ArmatureEditBones.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Armature.edit_bones`](bpy.types.Armature.md#bpy.types.Armature.edit_bones "bpy.types.Armature.edit_bones") |  |
