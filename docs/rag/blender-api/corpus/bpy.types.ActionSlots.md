<!-- source: Blender Python API reference 5.2 / bpy.types.ActionSlots.html -->

<a id="actionslots-bpy-prop-collection"></a>

# ActionSlots(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.ActionSlots"></a>

### class bpy.types.ActionSlots(bpy_prop_collection)

Collection of action slots

<a id="bpy.types.ActionSlots.active"></a>

#### bpy.types.ActionSlots.active

Active slot for this action

**Type:**

[`ActionSlot`](bpy.types.ActionSlot.md#bpy.types.ActionSlot "bpy.types.ActionSlot") | None

<a id="bpy.types.ActionSlots.new"></a>

#### bpy.types.ActionSlots.new(id_type, name)

Add a slot to the Action

**Parameters:**

- **id_type** (Literal[[Id Type Items](bpy_types_enum_items/id_type_items.md#rna-enum-id-type-items)]) – Data-block Type, The data-block type that the slot is intended for. This is combined with the slot name to create the slot’s unique identifier, and is also used to limit (on a best-effort basis) which data-blocks the slot can be assigned to.
- **name** (str) – Name, Name of the slot. This will be made unique within the Action among slots of the same type (never None)

**Returns:**

Newly created action slot

**Return type:**

[`ActionSlot`](bpy.types.ActionSlot.md#bpy.types.ActionSlot "bpy.types.ActionSlot")

<a id="bpy.types.ActionSlots.remove"></a>

#### bpy.types.ActionSlots.remove(action_slot)

Remove the slot from the Action, including all animation that is associated with that slot

**Parameters:**

**action_slot** ([`ActionSlot`](bpy.types.ActionSlot.md#bpy.types.ActionSlot "bpy.types.ActionSlot") | None) – Action Slot, The slot to remove

<a id="bpy.types.ActionSlots.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ActionSlots.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ActionSlots.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ActionSlots.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Action.slots`](bpy.types.Action.md#bpy.types.Action.slots "bpy.types.Action.slots") |  |
