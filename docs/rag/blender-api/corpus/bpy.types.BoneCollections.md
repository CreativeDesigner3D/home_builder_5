<!-- source: Blender Python API reference 5.2 / bpy.types.BoneCollections.html -->

<a id="bonecollections-bpy-prop-collection"></a>

# BoneCollections(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.BoneCollections"></a>

### class bpy.types.BoneCollections(bpy_prop_collection)

The Bone Collections of this Armature

<a id="bpy.types.BoneCollections.active"></a>

#### bpy.types.BoneCollections.active

Armature’s active bone collection

**Type:**

[`BoneCollection`](bpy.types.BoneCollection.md#bpy.types.BoneCollection "bpy.types.BoneCollection") | None

<a id="bpy.types.BoneCollections.active_index"></a>

#### bpy.types.BoneCollections.active_index

The index of the Armature’s active bone collection; -1 when there is no active collection. Note that this is indexing the underlying array of bone collections, which may not be in the order you expect. Root collections are listed first, and siblings are always sequential. Apart from that, bone collections can be in any order, and thus incrementing or decrementing this index can make the active bone collection jump around in unexpected ways. For a more predictable interface, use `active` or `active_name`. (in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.BoneCollections.active_name"></a>

#### bpy.types.BoneCollections.active_name

The name of the Armature’s active bone collection; empty when there is no active collection (default “”, never None)

**Type:**

str

<a id="bpy.types.BoneCollections.is_solo_active"></a>

#### bpy.types.BoneCollections.is_solo_active

Read-only flag that indicates there is at least one bone collection marked as ‘solo’ (default False, readonly)

**Type:**

bool

<a id="bpy.types.BoneCollections.new"></a>

#### bpy.types.BoneCollections.new(name, *, parent=None)

Add a new empty bone collection to the armature

**Parameters:**

- **name** (str) – Name, Name of the new collection. Blender will ensure it is unique within the collections of the Armature. (never None)
- **parent** ([`BoneCollection`](bpy.types.BoneCollection.md#bpy.types.BoneCollection "bpy.types.BoneCollection") | None) – Parent Collection, If not None, the new bone collection becomes a child of this collection (optional)

**Returns:**

Newly created bone collection

**Return type:**

[`BoneCollection`](bpy.types.BoneCollection.md#bpy.types.BoneCollection "bpy.types.BoneCollection")

<a id="bpy.types.BoneCollections.remove"></a>

#### bpy.types.BoneCollections.remove(bone_collection)

Remove the bone collection from the armature. If this bone collection has any children, they will be reassigned to their grandparent; in other words, the children will take the place of the removed bone collection.

**Parameters:**

**bone_collection** ([`BoneCollection`](bpy.types.BoneCollection.md#bpy.types.BoneCollection "bpy.types.BoneCollection") | None) – Bone Collection, The bone collection to remove

<a id="bpy.types.BoneCollections.move"></a>

#### bpy.types.BoneCollections.move(from_index, to_index)

Move a bone collection to a different position in the collection list. This can only be used to reorder siblings, and not to change parent-child relationships.

**Parameters:**

- **from_index** (int) – From Index, Index to move (in [-inf, inf])
- **to_index** (int) – To Index, Target index (in [-inf, inf])

<a id="bpy.types.BoneCollections.bl_rna_get_subclass"></a>

#### classmethod bpy.types.BoneCollections.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.BoneCollections.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.BoneCollections.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Armature.collections`](bpy.types.Armature.md#bpy.types.Armature.collections "bpy.types.Armature.collections") |  |
