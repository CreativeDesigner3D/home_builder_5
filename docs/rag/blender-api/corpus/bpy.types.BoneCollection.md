<!-- source: Blender Python API reference 5.2 / bpy.types.BoneCollection.html -->

<a id="bonecollection-bpy-struct"></a>

# BoneCollection(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.BoneCollection"></a>

### class bpy.types.BoneCollection(bpy_struct)

Bone collection in an Armature data-block

<a id="bpy.types.BoneCollection.bones"></a>

#### bpy.types.BoneCollection.bones

Bones assigned to this bone collection. In armature edit mode this will always return an empty list of bones, as the bone collection memberships are only synchronized when exiting edit mode. (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`Bone`](bpy.types.Bone.md#bpy.types.Bone "bpy.types.Bone")]

<a id="bpy.types.BoneCollection.child_number"></a>

#### bpy.types.BoneCollection.child_number

Index of this collection into its parent’s list of children. Note that finding this index requires a scan of all the bone collections, so do access this with care. (in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.BoneCollection.children"></a>

#### bpy.types.BoneCollection.children

(default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`BoneCollection`](#bpy.types.BoneCollection "bpy.types.BoneCollection")]

<a id="bpy.types.BoneCollection.index"></a>

#### bpy.types.BoneCollection.index

Index of this bone collection in the armature.collections_all array. Note that finding this index requires a scan of all the bone collections, so do access this with care. (in [-inf, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.BoneCollection.is_editable"></a>

#### bpy.types.BoneCollection.is_editable

This collection is owned by a local Armature, or was added via a library override in the current blend file (default False, readonly)

**Type:**

bool

<a id="bpy.types.BoneCollection.is_expanded"></a>

#### bpy.types.BoneCollection.is_expanded

This bone collection is expanded in the bone collections tree view (default False)

**Type:**

bool

<a id="bpy.types.BoneCollection.is_local_override"></a>

#### bpy.types.BoneCollection.is_local_override

This collection was added via a library override in the current blend file (default False, readonly)

**Type:**

bool

<a id="bpy.types.BoneCollection.is_solo"></a>

#### bpy.types.BoneCollection.is_solo

Show only this bone collection, and others also marked as ‘solo’ (default False)

**Type:**

bool

<a id="bpy.types.BoneCollection.is_visible"></a>

#### bpy.types.BoneCollection.is_visible

Bones in this collection will be visible in pose/object mode (default False)

**Type:**

bool

<a id="bpy.types.BoneCollection.is_visible_ancestors"></a>

#### bpy.types.BoneCollection.is_visible_ancestors

True when all of the ancestors of this bone collection are marked as visible; always True for root bone collections (default False, readonly)

**Type:**

bool

<a id="bpy.types.BoneCollection.is_visible_effectively"></a>

#### bpy.types.BoneCollection.is_visible_effectively

Whether this bone collection is effectively visible in the viewport. This is True when this bone collection and all of its ancestors are visible, or when it is marked as ‘solo’. (default False, readonly)

**Type:**

bool

<a id="bpy.types.BoneCollection.name"></a>

#### bpy.types.BoneCollection.name

Unique within the Armature (default “”, never None)

**Type:**

str

<a id="bpy.types.BoneCollection.parent"></a>

#### bpy.types.BoneCollection.parent

Parent bone collection. Note that accessing this requires a scan of all the bone collections to find the parent.

**Type:**

[`BoneCollection`](#bpy.types.BoneCollection "bpy.types.BoneCollection") | None

<a id="bpy.types.BoneCollection.bones_recursive"></a>

#### bpy.types.BoneCollection.bones_recursive

A set of all bones assigned to this bone collection and its child collections.

(readonly)

<a id="bpy.types.BoneCollection.bl_system_properties_get"></a>

#### bpy.types.BoneCollection.bl_system_properties_get(*, do_create=False)

DEBUG ONLY. Internal access to runtime-defined RNA data storage, intended solely for testing and debugging purposes. Do not access it in regular scripting work, and in particular, do not assume that it contains writable data

**Parameters:**

**do_create** (bool) – Ensure that system properties are created if they do not exist yet (optional)

**Returns:**

The system properties root container, or None if there are no system properties stored in this data yet, and its creation was not requested

**Return type:**

[`PropertyGroup`](bpy.types.PropertyGroup.md#bpy.types.PropertyGroup "bpy.types.PropertyGroup")

<a id="bpy.types.BoneCollection.assign"></a>

#### bpy.types.BoneCollection.assign(bone)

Assign the given bone to this collection

**Parameters:**

**bone** ([`AnyType`](bpy.types.AnyType.md#bpy.types.AnyType "bpy.types.AnyType") | None) – Bone, PoseBone, or EditBone to assign to this collection

**Returns:**

Assigned, Whether the bone was actually assigned; will be false if the bone was already member of the collection

**Return type:**

bool

<a id="bpy.types.BoneCollection.unassign"></a>

#### bpy.types.BoneCollection.unassign(bone)

Remove the given bone from this collection

**Parameters:**

**bone** ([`AnyType`](bpy.types.AnyType.md#bpy.types.AnyType "bpy.types.AnyType") | None) – Bone, PoseBone, or EditBone to remove from this collection

**Returns:**

Unassigned, Whether the bone was actually removed; will be false if the bone was not a member of the collection to begin with

**Return type:**

bool

<a id="bpy.types.BoneCollection.bl_rna_get_subclass"></a>

#### classmethod bpy.types.BoneCollection.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.BoneCollection.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.BoneCollection.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Armature.collections`](bpy.types.Armature.md#bpy.types.Armature.collections "bpy.types.Armature.collections") - [`Armature.collections_all`](bpy.types.Armature.md#bpy.types.Armature.collections_all "bpy.types.Armature.collections_all") - [`Bone.collections`](bpy.types.Bone.md#bpy.types.Bone.collections "bpy.types.Bone.collections") - [`BoneCollection.children`](#bpy.types.BoneCollection.children "bpy.types.BoneCollection.children") - [`BoneCollection.parent`](#bpy.types.BoneCollection.parent "bpy.types.BoneCollection.parent") | - [`BoneCollections.active`](bpy.types.BoneCollections.md#bpy.types.BoneCollections.active "bpy.types.BoneCollections.active") - [`BoneCollections.new`](bpy.types.BoneCollections.md#bpy.types.BoneCollections.new "bpy.types.BoneCollections.new") - [`BoneCollections.new`](bpy.types.BoneCollections.md#bpy.types.BoneCollections.new "bpy.types.BoneCollections.new") - [`BoneCollections.remove`](bpy.types.BoneCollections.md#bpy.types.BoneCollections.remove "bpy.types.BoneCollections.remove") - [`EditBone.collections`](bpy.types.EditBone.md#bpy.types.EditBone.collections "bpy.types.EditBone.collections") |
