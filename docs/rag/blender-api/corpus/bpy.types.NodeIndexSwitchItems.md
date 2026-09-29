<!-- source: Blender Python API reference 5.2 / bpy.types.NodeIndexSwitchItems.html -->

<a id="nodeindexswitchitems-bpy-prop-collection"></a>

# NodeIndexSwitchItems(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.NodeIndexSwitchItems"></a>

### class bpy.types.NodeIndexSwitchItems(bpy_prop_collection)

Collection of index_switch items

<a id="bpy.types.NodeIndexSwitchItems.new"></a>

#### bpy.types.NodeIndexSwitchItems.new()

Add an item at the end

**Returns:**

Item, New item

**Return type:**

[`IndexSwitchItem`](bpy.types.IndexSwitchItem.md#bpy.types.IndexSwitchItem "bpy.types.IndexSwitchItem")

<a id="bpy.types.NodeIndexSwitchItems.remove"></a>

#### bpy.types.NodeIndexSwitchItems.remove(item)

Remove an item

**Parameters:**

**item** ([`IndexSwitchItem`](bpy.types.IndexSwitchItem.md#bpy.types.IndexSwitchItem "bpy.types.IndexSwitchItem") | None) – Item, The item to remove (never None)

<a id="bpy.types.NodeIndexSwitchItems.clear"></a>

#### bpy.types.NodeIndexSwitchItems.clear()

Remove all items

<a id="bpy.types.NodeIndexSwitchItems.move"></a>

#### bpy.types.NodeIndexSwitchItems.move(from_index, to_index)

Move an item to another position

**Parameters:**

- **from_index** (int) – From Index, Index of the item to move (in [0, inf])
- **to_index** (int) – To Index, Target index for the item (in [0, inf])

<a id="bpy.types.NodeIndexSwitchItems.bl_rna_get_subclass"></a>

#### classmethod bpy.types.NodeIndexSwitchItems.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.NodeIndexSwitchItems.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.NodeIndexSwitchItems.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`GeometryNodeIndexSwitch.index_switch_items`](bpy.types.GeometryNodeIndexSwitch.md#bpy.types.GeometryNodeIndexSwitch.index_switch_items "bpy.types.GeometryNodeIndexSwitch.index_switch_items") |  |
