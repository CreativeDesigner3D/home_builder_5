<!-- source: Blender Python API reference 5.2 / bpy.types.KeyConfigurations.html -->

<a id="keyconfigurations-bpy-prop-collection"></a>

# KeyConfigurations(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.KeyConfigurations"></a>

### class bpy.types.KeyConfigurations(bpy_prop_collection)

Collection of KeyConfigs

<a id="bpy.types.KeyConfigurations.active"></a>

#### bpy.types.KeyConfigurations.active

Active key configuration (preset)

**Type:**

[`KeyConfig`](bpy.types.KeyConfig.md#bpy.types.KeyConfig "bpy.types.KeyConfig") | None

<a id="bpy.types.KeyConfigurations.addon"></a>

#### bpy.types.KeyConfigurations.addon

Key configuration that can be extended by add-ons, and is added to the active configuration when handling events (readonly)

**Type:**

[`KeyConfig`](bpy.types.KeyConfig.md#bpy.types.KeyConfig "bpy.types.KeyConfig") | None

<a id="bpy.types.KeyConfigurations.default"></a>

#### bpy.types.KeyConfigurations.default

Default builtin key configuration (readonly)

**Type:**

[`KeyConfig`](bpy.types.KeyConfig.md#bpy.types.KeyConfig "bpy.types.KeyConfig") | None

<a id="bpy.types.KeyConfigurations.user"></a>

#### bpy.types.KeyConfigurations.user

Final key configuration that combines keymaps from the active and add-on configurations, and can be edited by the user (readonly)

**Type:**

[`KeyConfig`](bpy.types.KeyConfig.md#bpy.types.KeyConfig "bpy.types.KeyConfig") | None

<a id="bpy.types.KeyConfigurations.new"></a>

#### bpy.types.KeyConfigurations.new(name)

new

**Parameters:**

**name** (str) – Name, (never None)

**Returns:**

Key Configuration, Added key configuration

**Return type:**

[`KeyConfig`](bpy.types.KeyConfig.md#bpy.types.KeyConfig "bpy.types.KeyConfig")

<a id="bpy.types.KeyConfigurations.remove"></a>

#### bpy.types.KeyConfigurations.remove(keyconfig)

remove

**Parameters:**

**keyconfig** ([`KeyConfig`](bpy.types.KeyConfig.md#bpy.types.KeyConfig "bpy.types.KeyConfig") | None) – Key Configuration, Removed key configuration (never None)

<a id="bpy.types.KeyConfigurations.find_item_from_operator"></a>

#### bpy.types.KeyConfigurations.find_item_from_operator(idname, *, context='INVOKE_DEFAULT', properties=None, include={'ACTIONZONE', 'KEYBOARD', 'MOUSE', 'NDOF'}, exclude=set())

find_item_from_operator

**Parameters:**

- **idname** (str) – Operator Identifier, (never None)
- **context** (Literal[[Operator Context Items](bpy_types_enum_items/operator_context_items.md#rna-enum-operator-context-items)]) – context, (optional)
- **properties** ([`OperatorProperties`](bpy.types.OperatorProperties.md#bpy.types.OperatorProperties "bpy.types.OperatorProperties") | None) – (optional)
- **include** (set[Literal[[Event Type Mask Items](bpy_types_enum_items/event_type_mask_items.md#rna-enum-event-type-mask-items)]]) – Include, (optional)
- **exclude** (set[Literal[[Event Type Mask Items](bpy_types_enum_items/event_type_mask_items.md#rna-enum-event-type-mask-items)]]) – Exclude, (optional)

**Returns:**

`keymap`, [`KeyMap`](bpy.types.KeyMap.md#bpy.types.KeyMap "bpy.types.KeyMap")

`item`, [`KeyMapItem`](bpy.types.KeyMapItem.md#bpy.types.KeyMapItem "bpy.types.KeyMapItem")

**Return type:**

tuple[[`KeyMap`](bpy.types.KeyMap.md#bpy.types.KeyMap "bpy.types.KeyMap"), [`KeyMapItem`](bpy.types.KeyMapItem.md#bpy.types.KeyMapItem "bpy.types.KeyMapItem")]

<a id="bpy.types.KeyConfigurations.update"></a>

#### bpy.types.KeyConfigurations.update(*, keep_properties=False)

update

**Parameters:**

**keep_properties** (bool) – Keep Properties, Operator properties are kept to allow the operators to be registered again in the future (optional)

<a id="bpy.types.KeyConfigurations.bl_rna_get_subclass"></a>

#### classmethod bpy.types.KeyConfigurations.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.KeyConfigurations.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.KeyConfigurations.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`WindowManager.keyconfigs`](bpy.types.WindowManager.md#bpy.types.WindowManager.keyconfigs "bpy.types.WindowManager.keyconfigs") |  |
