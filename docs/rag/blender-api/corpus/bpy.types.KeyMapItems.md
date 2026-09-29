<!-- source: Blender Python API reference 5.2 / bpy.types.KeyMapItems.html -->

<a id="keymapitems-bpy-prop-collection"></a>

# KeyMapItems(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.KeyMapItems"></a>

### class bpy.types.KeyMapItems(bpy_prop_collection)

Collection of keymap items

<a id="bpy.types.KeyMapItems.new"></a>

#### bpy.types.KeyMapItems.new(idname, type, value, *, any=False, shift=0, ctrl=0, alt=0, oskey=0, hyper=0, key_modifier='NONE', direction='ANY', repeat=False, head=False)

new

**Parameters:**

- **idname** (str) – Operator Identifier, (never None)
- **type** (Literal[[Event Type Items](bpy_types_enum_items/event_type_items.md#rna-enum-event-type-items)]) – Type
- **value** (Literal[[Event Value Items](bpy_types_enum_items/event_value_items.md#rna-enum-event-value-items)]) – Value
- **any** (bool) – Any, (optional)
- **shift** (int) – Shift, (in [-1, 1], optional)
- **ctrl** (int) – Ctrl, (in [-1, 1], optional)
- **alt** (int) – Alt, (in [-1, 1], optional)
- **oskey** (int) – OS Key, (in [-1, 1], optional)
- **hyper** (int) – Hyper, (in [-1, 1], optional)
- **key_modifier** (Literal[[Event Type Items](bpy_types_enum_items/event_type_items.md#rna-enum-event-type-items)]) – Key Modifier, (optional)
- **direction** (Literal[[Event Direction Items](bpy_types_enum_items/event_direction_items.md#rna-enum-event-direction-items)]) – Direction, (optional)
- **repeat** (bool) – Repeat, When set, accept key-repeat events (optional)
- **head** (bool) – At Head, Force item to be added at start (not end) of key map so that it doesn’t get blocked by an existing key map item (optional)

**Returns:**

Item, Added key map item

**Return type:**

[`KeyMapItem`](bpy.types.KeyMapItem.md#bpy.types.KeyMapItem "bpy.types.KeyMapItem")

<a id="bpy.types.KeyMapItems.new_modal"></a>

#### bpy.types.KeyMapItems.new_modal(propvalue, type, value, *, any=False, shift=0, ctrl=0, alt=0, oskey=0, hyper=0, key_modifier='NONE', direction='ANY', repeat=False)

new_modal

**Parameters:**

- **propvalue** (str) – Property Value, (never None)
- **type** (Literal[[Event Type Items](bpy_types_enum_items/event_type_items.md#rna-enum-event-type-items)]) – Type
- **value** (Literal[[Event Value Items](bpy_types_enum_items/event_value_items.md#rna-enum-event-value-items)]) – Value
- **any** (bool) – Any, (optional)
- **shift** (int) – Shift, (in [-1, 1], optional)
- **ctrl** (int) – Ctrl, (in [-1, 1], optional)
- **alt** (int) – Alt, (in [-1, 1], optional)
- **oskey** (int) – OS Key, (in [-1, 1], optional)
- **hyper** (int) – Hyper, (in [-1, 1], optional)
- **key_modifier** (Literal[[Event Type Items](bpy_types_enum_items/event_type_items.md#rna-enum-event-type-items)]) – Key Modifier, (optional)
- **direction** (Literal[[Event Direction Items](bpy_types_enum_items/event_direction_items.md#rna-enum-event-direction-items)]) – Direction, (optional)
- **repeat** (bool) – Repeat, When set, accept key-repeat events (optional)

**Returns:**

Item, Added key map item

**Return type:**

[`KeyMapItem`](bpy.types.KeyMapItem.md#bpy.types.KeyMapItem "bpy.types.KeyMapItem")

<a id="bpy.types.KeyMapItems.new_from_item"></a>

#### bpy.types.KeyMapItems.new_from_item(item, *, head=False)

new_from_item

**Parameters:**

- **item** ([`KeyMapItem`](bpy.types.KeyMapItem.md#bpy.types.KeyMapItem "bpy.types.KeyMapItem") | None) – Item, Item to use as a reference (never None)
- **head** (bool) – At Head, (optional)

**Returns:**

Item, Added key map item

**Return type:**

[`KeyMapItem`](bpy.types.KeyMapItem.md#bpy.types.KeyMapItem "bpy.types.KeyMapItem")

<a id="bpy.types.KeyMapItems.remove"></a>

#### bpy.types.KeyMapItems.remove(item)

remove

**Parameters:**

**item** ([`KeyMapItem`](bpy.types.KeyMapItem.md#bpy.types.KeyMapItem "bpy.types.KeyMapItem") | None) – Item, (never None)

<a id="bpy.types.KeyMapItems.from_id"></a>

#### bpy.types.KeyMapItems.from_id(id)

from_id

**Parameters:**

**id** (int) – id, ID of the item (in [-inf, inf])

**Returns:**

Item

**Return type:**

[`KeyMapItem`](bpy.types.KeyMapItem.md#bpy.types.KeyMapItem "bpy.types.KeyMapItem")

<a id="bpy.types.KeyMapItems.find_from_operator"></a>

#### bpy.types.KeyMapItems.find_from_operator(idname, *, properties=None, include={'ACTIONZONE', 'KEYBOARD', 'MOUSE', 'NDOF'}, exclude=set())

find_from_operator

**Parameters:**

- **idname** (str) – Operator Identifier, (never None)
- **properties** ([`OperatorProperties`](bpy.types.OperatorProperties.md#bpy.types.OperatorProperties "bpy.types.OperatorProperties") | None) – (optional)
- **include** (set[Literal[[Event Type Mask Items](bpy_types_enum_items/event_type_mask_items.md#rna-enum-event-type-mask-items)]]) – Include, (optional)
- **exclude** (set[Literal[[Event Type Mask Items](bpy_types_enum_items/event_type_mask_items.md#rna-enum-event-type-mask-items)]]) – Exclude, (optional)

**Return type:**

[`KeyMapItem`](bpy.types.KeyMapItem.md#bpy.types.KeyMapItem "bpy.types.KeyMapItem")

<a id="bpy.types.KeyMapItems.find_match"></a>

#### bpy.types.KeyMapItems.find_match(keymap, item)

find_match

**Parameters:**

- **keymap** ([`KeyMap`](bpy.types.KeyMap.md#bpy.types.KeyMap "bpy.types.KeyMap") | None) – The matching keymap
- **item** ([`KeyMapItem`](bpy.types.KeyMapItem.md#bpy.types.KeyMapItem "bpy.types.KeyMapItem") | None) – The matching keymap item

**Returns:**

The keymap item from this keymap which matches the keymap item from the arguments passed in

**Return type:**

[`KeyMapItem`](bpy.types.KeyMapItem.md#bpy.types.KeyMapItem "bpy.types.KeyMapItem")

<a id="bpy.types.KeyMapItems.match_event"></a>

#### bpy.types.KeyMapItems.match_event(event)

match_event

**Parameters:**

**event** ([`Event`](bpy.types.Event.md#bpy.types.Event "bpy.types.Event") | None) – Event to match against

**Return type:**

[`KeyMapItem`](bpy.types.KeyMapItem.md#bpy.types.KeyMapItem "bpy.types.KeyMapItem")

<a id="bpy.types.KeyMapItems.bl_rna_get_subclass"></a>

#### classmethod bpy.types.KeyMapItems.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.KeyMapItems.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.KeyMapItems.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`KeyMap.keymap_items`](bpy.types.KeyMap.md#bpy.types.KeyMap.keymap_items "bpy.types.KeyMap.keymap_items") |  |
