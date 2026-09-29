<!-- source: Blender Python API reference 5.2 / bpy.types.bpy_prop_collection_idprop.html -->

<a id="bpy-prop-collection-idprop"></a>

# bpy_prop_collection_idprop

base classes — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.bpy_prop_collection_idprop"></a>

### class bpy.types.bpy_prop_collection_idprop(bpy_prop_collection)

built-in class used for user defined collections.

<a id="bpy.types.bpy_prop_collection_idprop.add"></a>

#### bpy.types.bpy_prop_collection_idprop.add()

This is a function to add a new item to a collection.

**Returns:**

A newly created item.

**Return type:**

Any

<a id="bpy.types.bpy_prop_collection_idprop.clear"></a>

#### bpy.types.bpy_prop_collection_idprop.clear()

This is a function to remove all items from a collection.

<a id="bpy.types.bpy_prop_collection_idprop.move"></a>

#### bpy.types.bpy_prop_collection_idprop.move(src_index, dst_index)

This is a function to move an item in a collection.

**Parameters:**

- **src_index** (int) – Source item index.
- **dst_index** (int) – Destination item index.

<a id="bpy.types.bpy_prop_collection_idprop.remove"></a>

#### bpy.types.bpy_prop_collection_idprop.remove(index)

This is a function to remove an item from a collection.

**Parameters:**

**index** (int) – Index of the item to be removed.
