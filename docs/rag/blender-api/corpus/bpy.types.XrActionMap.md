<!-- source: Blender Python API reference 5.2 / bpy.types.XrActionMap.html -->

<a id="xractionmap-bpy-struct"></a>

# XrActionMap(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.XrActionMap"></a>

### class bpy.types.XrActionMap(bpy_struct)

<a id="bpy.types.XrActionMap.actionmap_items"></a>

#### bpy.types.XrActionMap.actionmap_items

Items in the action map, mapping an XR event to an operator, pose, or haptic output (default None, readonly)

**Type:**

[`XrActionMapItems`](bpy.types.XrActionMapItems.md#bpy.types.XrActionMapItems "bpy.types.XrActionMapItems")[[`XrActionMapItem`](bpy.types.XrActionMapItem.md#bpy.types.XrActionMapItem "bpy.types.XrActionMapItem")]

<a id="bpy.types.XrActionMap.name"></a>

#### bpy.types.XrActionMap.name

Name of the action map (default “”, never None)

**Type:**

str

<a id="bpy.types.XrActionMap.selected_item"></a>

#### bpy.types.XrActionMap.selected_item

(in [-32768, 32767], default 0)

**Type:**

int

<a id="bpy.types.XrActionMap.bl_rna_get_subclass"></a>

#### classmethod bpy.types.XrActionMap.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.XrActionMap.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.XrActionMap.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`XrActionMaps.find`](bpy.types.XrActionMaps.md#bpy.types.XrActionMaps.find "bpy.types.XrActionMaps.find") - [`XrActionMaps.new`](bpy.types.XrActionMaps.md#bpy.types.XrActionMaps.new "bpy.types.XrActionMaps.new") - [`XrActionMaps.new_from_actionmap`](bpy.types.XrActionMaps.md#bpy.types.XrActionMaps.new_from_actionmap "bpy.types.XrActionMaps.new_from_actionmap") - [`XrActionMaps.new_from_actionmap`](bpy.types.XrActionMaps.md#bpy.types.XrActionMaps.new_from_actionmap "bpy.types.XrActionMaps.new_from_actionmap") - [`XrActionMaps.remove`](bpy.types.XrActionMaps.md#bpy.types.XrActionMaps.remove "bpy.types.XrActionMaps.remove") | - [`XrSessionState.action_binding_create`](bpy.types.XrSessionState.md#bpy.types.XrSessionState.action_binding_create "bpy.types.XrSessionState.action_binding_create") - [`XrSessionState.action_create`](bpy.types.XrSessionState.md#bpy.types.XrSessionState.action_create "bpy.types.XrSessionState.action_create") - [`XrSessionState.action_set_create`](bpy.types.XrSessionState.md#bpy.types.XrSessionState.action_set_create "bpy.types.XrSessionState.action_set_create") - [`XrSessionState.actionmaps`](bpy.types.XrSessionState.md#bpy.types.XrSessionState.actionmaps "bpy.types.XrSessionState.actionmaps") |
