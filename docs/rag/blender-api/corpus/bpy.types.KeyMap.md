<!-- source: Blender Python API reference 5.2 / bpy.types.KeyMap.html -->

<a id="keymap-bpy-struct"></a>

# KeyMap(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.KeyMap"></a>

### class bpy.types.KeyMap(bpy_struct)

Input configuration, including keymaps

<a id="bpy.types.KeyMap.bl_owner_id"></a>

#### bpy.types.KeyMap.bl_owner_id

Internal owner (default “”, never None)

**Type:**

str

<a id="bpy.types.KeyMap.is_modal"></a>

#### bpy.types.KeyMap.is_modal

Indicates that a keymap is used for translate modal events for an operator (default False, readonly)

**Type:**

bool

<a id="bpy.types.KeyMap.is_user_modified"></a>

#### bpy.types.KeyMap.is_user_modified

Keymap is defined by the user (default False)

**Type:**

bool

<a id="bpy.types.KeyMap.keymap_items"></a>

#### bpy.types.KeyMap.keymap_items

Items in the keymap, linking an operator to an input event (default None, readonly)

**Type:**

[`KeyMapItems`](bpy.types.KeyMapItems.md#bpy.types.KeyMapItems "bpy.types.KeyMapItems")[[`KeyMapItem`](bpy.types.KeyMapItem.md#bpy.types.KeyMapItem "bpy.types.KeyMapItem")]

<a id="bpy.types.KeyMap.modal_event_values"></a>

#### bpy.types.KeyMap.modal_event_values

Give access to the possible event values of this modal keymap’s items (#KeyMapItem.propvalue), for API introspection (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`EnumPropertyItem`](bpy.types.EnumPropertyItem.md#bpy.types.EnumPropertyItem "bpy.types.EnumPropertyItem")]

<a id="bpy.types.KeyMap.name"></a>

#### bpy.types.KeyMap.name

Name of the key map (default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.KeyMap.region_type"></a>

#### bpy.types.KeyMap.region_type

Optional region type keymap is associated with (default `'WINDOW'`, readonly)

**Type:**

Literal[[Region Type Items](bpy_types_enum_items/region_type_items.md#rna-enum-region-type-items)]

<a id="bpy.types.KeyMap.show_expanded_children"></a>

#### bpy.types.KeyMap.show_expanded_children

Children expanded in the user interface (default False)

**Type:**

bool

<a id="bpy.types.KeyMap.show_expanded_items"></a>

#### bpy.types.KeyMap.show_expanded_items

Expanded in the user interface (default False)

**Type:**

bool

<a id="bpy.types.KeyMap.space_type"></a>

#### bpy.types.KeyMap.space_type

Optional space type keymap is associated with (default `'EMPTY'`, readonly)

**Type:**

Literal[[Space Type Items](bpy_types_enum_items/space_type_items.md#rna-enum-space-type-items)]

<a id="bpy.types.KeyMap.active"></a>

#### bpy.types.KeyMap.active()

active

**Returns:**

Key Map, Active key map

**Return type:**

[`KeyMap`](#bpy.types.KeyMap "bpy.types.KeyMap")

<a id="bpy.types.KeyMap.restore_to_default"></a>

#### bpy.types.KeyMap.restore_to_default()

restore_to_default

<a id="bpy.types.KeyMap.restore_item_to_default"></a>

#### bpy.types.KeyMap.restore_item_to_default(item)

restore_item_to_default

**Parameters:**

**item** ([`KeyMapItem`](bpy.types.KeyMapItem.md#bpy.types.KeyMapItem "bpy.types.KeyMapItem") | None) – Item, (never None)

<a id="bpy.types.KeyMap.bl_rna_get_subclass"></a>

#### classmethod bpy.types.KeyMap.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.KeyMap.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.KeyMap.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`GizmoGroup.setup_keymap`](bpy.types.GizmoGroup.md#bpy.types.GizmoGroup.setup_keymap "bpy.types.GizmoGroup.setup_keymap") - [`KeyConfig.keymaps`](bpy.types.KeyConfig.md#bpy.types.KeyConfig.keymaps "bpy.types.KeyConfig.keymaps") - [`KeyConfigurations.find_item_from_operator`](bpy.types.KeyConfigurations.md#bpy.types.KeyConfigurations.find_item_from_operator "bpy.types.KeyConfigurations.find_item_from_operator") - [`KeyMap.active`](#bpy.types.KeyMap.active "bpy.types.KeyMap.active") - [`KeyMapItems.find_match`](bpy.types.KeyMapItems.md#bpy.types.KeyMapItems.find_match "bpy.types.KeyMapItems.find_match") - [`KeyMaps.find`](bpy.types.KeyMaps.md#bpy.types.KeyMaps.find "bpy.types.KeyMaps.find") | - [`KeyMaps.find_match`](bpy.types.KeyMaps.md#bpy.types.KeyMaps.find_match "bpy.types.KeyMaps.find_match") - [`KeyMaps.find_match`](bpy.types.KeyMaps.md#bpy.types.KeyMaps.find_match "bpy.types.KeyMaps.find_match") - [`KeyMaps.find_modal`](bpy.types.KeyMaps.md#bpy.types.KeyMaps.find_modal "bpy.types.KeyMaps.find_modal") - [`KeyMaps.new`](bpy.types.KeyMaps.md#bpy.types.KeyMaps.new "bpy.types.KeyMaps.new") - [`KeyMaps.remove`](bpy.types.KeyMaps.md#bpy.types.KeyMaps.remove "bpy.types.KeyMaps.remove") - [`WindowManager.popover_end__internal`](bpy.types.WindowManager.md#bpy.types.WindowManager.popover_end__internal "bpy.types.WindowManager.popover_end__internal") |
