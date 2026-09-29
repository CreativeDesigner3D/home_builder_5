<!-- source: Blender Python API reference 5.2 / bpy.types.KeyMapItem.html -->

<a id="keymapitem-bpy-struct"></a>

# KeyMapItem(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.KeyMapItem"></a>

### class bpy.types.KeyMapItem(bpy_struct)

Item in a Key Map

<a id="bpy.types.KeyMapItem.active"></a>

#### bpy.types.KeyMapItem.active

Activate or deactivate item (default False)

**Type:**

bool

<a id="bpy.types.KeyMapItem.alt"></a>

#### bpy.types.KeyMapItem.alt

Alt key pressed, -1 for any state (in [-1, 1], default 0)

**Type:**

int

<a id="bpy.types.KeyMapItem.alt_ui"></a>

#### bpy.types.KeyMapItem.alt_ui

Alt key pressed (default False)

**Type:**

bool

<a id="bpy.types.KeyMapItem.any"></a>

#### bpy.types.KeyMapItem.any

Any modifier keys pressed (default False)

**Type:**

bool

<a id="bpy.types.KeyMapItem.ctrl"></a>

#### bpy.types.KeyMapItem.ctrl

Control key pressed, -1 for any state (in [-1, 1], default 0)

**Type:**

int

<a id="bpy.types.KeyMapItem.ctrl_ui"></a>

#### bpy.types.KeyMapItem.ctrl_ui

Control key pressed (default False)

**Type:**

bool

<a id="bpy.types.KeyMapItem.direction"></a>

#### bpy.types.KeyMapItem.direction

The direction (only applies to drag events) (default `'ANY'`)

**Type:**

Literal[[Event Direction Items](bpy_types_enum_items/event_direction_items.md#rna-enum-event-direction-items)]

<a id="bpy.types.KeyMapItem.hyper"></a>

#### bpy.types.KeyMapItem.hyper

Hyper key pressed, -1 for any state (in [-1, 1], default 0)

**Type:**

int

<a id="bpy.types.KeyMapItem.hyper_ui"></a>

#### bpy.types.KeyMapItem.hyper_ui

Hyper key pressed. An additional modifier which can be configured on Linux, typically replacing CapsLock (default False)

**Type:**

bool

<a id="bpy.types.KeyMapItem.id"></a>

#### bpy.types.KeyMapItem.id

ID of the item (in [-32768, 32767], default 0, readonly)

**Type:**

int

<a id="bpy.types.KeyMapItem.idname"></a>

#### bpy.types.KeyMapItem.idname

Identifier of operator to call on input event (default “”, never None)

**Type:**

str

<a id="bpy.types.KeyMapItem.is_user_defined"></a>

#### bpy.types.KeyMapItem.is_user_defined

Is this keymap item user defined (does not just replace a builtin item) (default False, readonly)

**Type:**

bool

<a id="bpy.types.KeyMapItem.is_user_modified"></a>

#### bpy.types.KeyMapItem.is_user_modified

Is this keymap item modified by the user (default False, readonly)

**Type:**

bool

<a id="bpy.types.KeyMapItem.key_modifier"></a>

#### bpy.types.KeyMapItem.key_modifier

Regular key pressed as a modifier (default `'NONE'`)

**Type:**

Literal[[Event Type Items](bpy_types_enum_items/event_type_items.md#rna-enum-event-type-items)]

<a id="bpy.types.KeyMapItem.map_type"></a>

#### bpy.types.KeyMapItem.map_type

Type of event mapping (default `'KEYBOARD'`)

**Type:**

Literal[‘KEYBOARD’, ‘MOUSE’, ‘NDOF’, ‘TEXTINPUT’, ‘TIMER’]

<a id="bpy.types.KeyMapItem.name"></a>

#### bpy.types.KeyMapItem.name

Name of operator (translated) to call on input event (default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.KeyMapItem.oskey"></a>

#### bpy.types.KeyMapItem.oskey

Operating system key pressed, -1 for any state (in [-1, 1], default 0)

**Type:**

int

<a id="bpy.types.KeyMapItem.oskey_ui"></a>

#### bpy.types.KeyMapItem.oskey_ui

Operating system key pressed (default False)

**Type:**

bool

<a id="bpy.types.KeyMapItem.properties"></a>

#### bpy.types.KeyMapItem.properties

Properties to set when the operator is called (readonly)

**Type:**

[`OperatorProperties`](bpy.types.OperatorProperties.md#bpy.types.OperatorProperties "bpy.types.OperatorProperties") | None

<a id="bpy.types.KeyMapItem.propvalue"></a>

#### bpy.types.KeyMapItem.propvalue

The value this event translates to in a modal keymap (default `'NONE'`)

**Type:**

Literal[[Keymap Propvalue Items](bpy_types_enum_items/keymap_propvalue_items.md#rna-enum-keymap-propvalue-items)]

<a id="bpy.types.KeyMapItem.repeat"></a>

#### bpy.types.KeyMapItem.repeat

Active on key-repeat events (when a key is held) (default False)

**Type:**

bool

<a id="bpy.types.KeyMapItem.shift"></a>

#### bpy.types.KeyMapItem.shift

Shift key pressed, -1 for any state (in [-1, 1], default 0)

**Type:**

int

<a id="bpy.types.KeyMapItem.shift_ui"></a>

#### bpy.types.KeyMapItem.shift_ui

Shift key pressed (default False)

**Type:**

bool

<a id="bpy.types.KeyMapItem.show_expanded"></a>

#### bpy.types.KeyMapItem.show_expanded

Show key map event and property details in the user interface (default False)

**Type:**

bool

<a id="bpy.types.KeyMapItem.type"></a>

#### bpy.types.KeyMapItem.type

Type of event (default `'NONE'`)

**Type:**

Literal[[Event Type Items](bpy_types_enum_items/event_type_items.md#rna-enum-event-type-items)]

<a id="bpy.types.KeyMapItem.value"></a>

#### bpy.types.KeyMapItem.value

(default `'NOTHING'`)

**Type:**

Literal[[Event Value Items](bpy_types_enum_items/event_value_items.md#rna-enum-event-value-items)]

<a id="bpy.types.KeyMapItem.compare"></a>

#### bpy.types.KeyMapItem.compare(item)

compare

**Parameters:**

**item** ([`KeyMapItem`](#bpy.types.KeyMapItem "bpy.types.KeyMapItem") | None) – Item

**Returns:**

Comparison result

**Return type:**

bool

<a id="bpy.types.KeyMapItem.to_string"></a>

#### bpy.types.KeyMapItem.to_string(*, compact=False)

to_string

**Parameters:**

**compact** (bool) – Compact, (optional)

**Returns:**

result, (never None)

**Return type:**

str

<a id="bpy.types.KeyMapItem.bl_rna_get_subclass"></a>

#### classmethod bpy.types.KeyMapItem.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.KeyMapItem.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.KeyMapItem.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([type](#bpy.types.KeyMapItem.type "bpy.types.KeyMapItem.type") | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

[type](#bpy.types.KeyMapItem.type "bpy.types.KeyMapItem.type")

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
| - [`KeyConfigurations.find_item_from_operator`](bpy.types.KeyConfigurations.md#bpy.types.KeyConfigurations.find_item_from_operator "bpy.types.KeyConfigurations.find_item_from_operator") - [`KeyMap.keymap_items`](bpy.types.KeyMap.md#bpy.types.KeyMap.keymap_items "bpy.types.KeyMap.keymap_items") - [`KeyMap.restore_item_to_default`](bpy.types.KeyMap.md#bpy.types.KeyMap.restore_item_to_default "bpy.types.KeyMap.restore_item_to_default") - [`KeyMapItem.compare`](#bpy.types.KeyMapItem.compare "bpy.types.KeyMapItem.compare") - [`KeyMapItems.find_from_operator`](bpy.types.KeyMapItems.md#bpy.types.KeyMapItems.find_from_operator "bpy.types.KeyMapItems.find_from_operator") - [`KeyMapItems.find_match`](bpy.types.KeyMapItems.md#bpy.types.KeyMapItems.find_match "bpy.types.KeyMapItems.find_match") - [`KeyMapItems.find_match`](bpy.types.KeyMapItems.md#bpy.types.KeyMapItems.find_match "bpy.types.KeyMapItems.find_match") - [`KeyMapItems.from_id`](bpy.types.KeyMapItems.md#bpy.types.KeyMapItems.from_id "bpy.types.KeyMapItems.from_id") | - [`KeyMapItems.match_event`](bpy.types.KeyMapItems.md#bpy.types.KeyMapItems.match_event "bpy.types.KeyMapItems.match_event") - [`KeyMapItems.new`](bpy.types.KeyMapItems.md#bpy.types.KeyMapItems.new "bpy.types.KeyMapItems.new") - [`KeyMapItems.new_from_item`](bpy.types.KeyMapItems.md#bpy.types.KeyMapItems.new_from_item "bpy.types.KeyMapItems.new_from_item") - [`KeyMapItems.new_from_item`](bpy.types.KeyMapItems.md#bpy.types.KeyMapItems.new_from_item "bpy.types.KeyMapItems.new_from_item") - [`KeyMapItems.new_modal`](bpy.types.KeyMapItems.md#bpy.types.KeyMapItems.new_modal "bpy.types.KeyMapItems.new_modal") - [`KeyMapItems.remove`](bpy.types.KeyMapItems.md#bpy.types.KeyMapItems.remove "bpy.types.KeyMapItems.remove") - [`UILayout.template_event_from_keymap_item`](bpy.types.UILayout.md#bpy.types.UILayout.template_event_from_keymap_item "bpy.types.UILayout.template_event_from_keymap_item") - [`UILayout.template_keymap_item_properties`](bpy.types.UILayout.md#bpy.types.UILayout.template_keymap_item_properties "bpy.types.UILayout.template_keymap_item_properties") |
