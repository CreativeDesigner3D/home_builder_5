<!-- source: Blender Python API reference 5.2 / bpy.types.OperatorProperties.html -->

<a id="operatorproperties-bpy-struct"></a>

# OperatorProperties(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.OperatorProperties"></a>

### class bpy.types.OperatorProperties(bpy_struct)

Input properties of an operator

<a id="bpy.types.OperatorProperties.bl_system_properties_get"></a>

#### bpy.types.OperatorProperties.bl_system_properties_get(*, do_create=False)

DEBUG ONLY. Internal access to runtime-defined RNA data storage, intended solely for testing and debugging purposes. Do not access it in regular scripting work, and in particular, do not assume that it contains writable data

**Parameters:**

**do_create** (bool) – Ensure that system properties are created if they do not exist yet (optional)

**Returns:**

The system properties root container, or None if there are no system properties stored in this data yet, and its creation was not requested

**Return type:**

[`PropertyGroup`](bpy.types.PropertyGroup.md#bpy.types.PropertyGroup "bpy.types.PropertyGroup")

<a id="bpy.types.OperatorProperties.bl_rna_get_subclass"></a>

#### classmethod bpy.types.OperatorProperties.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.OperatorProperties.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.OperatorProperties.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Gizmo.target_set_operator`](bpy.types.Gizmo.md#bpy.types.Gizmo.target_set_operator "bpy.types.Gizmo.target_set_operator") - [`KeyConfigurations.find_item_from_operator`](bpy.types.KeyConfigurations.md#bpy.types.KeyConfigurations.find_item_from_operator "bpy.types.KeyConfigurations.find_item_from_operator") - [`KeyMapItem.properties`](bpy.types.KeyMapItem.md#bpy.types.KeyMapItem.properties "bpy.types.KeyMapItem.properties") - [`KeyMapItems.find_from_operator`](bpy.types.KeyMapItems.md#bpy.types.KeyMapItems.find_from_operator "bpy.types.KeyMapItems.find_from_operator") - [`Macro.properties`](bpy.types.Macro.md#bpy.types.Macro.properties "bpy.types.Macro.properties") - [`Operator.description`](bpy.types.Operator.md#bpy.types.Operator.description "bpy.types.Operator.description") - [`Operator.properties`](bpy.types.Operator.md#bpy.types.Operator.properties "bpy.types.Operator.properties") - [`OperatorMacro.properties`](bpy.types.OperatorMacro.md#bpy.types.OperatorMacro.properties "bpy.types.OperatorMacro.properties") | - [`UILayout.operator`](bpy.types.UILayout.md#bpy.types.UILayout.operator "bpy.types.UILayout.operator") - [`UILayout.operator_menu_enum`](bpy.types.UILayout.md#bpy.types.UILayout.operator_menu_enum "bpy.types.UILayout.operator_menu_enum") - [`UILayout.operator_menu_hold`](bpy.types.UILayout.md#bpy.types.UILayout.operator_menu_hold "bpy.types.UILayout.operator_menu_hold") - [`UILayout.template_popup_confirm`](bpy.types.UILayout.md#bpy.types.UILayout.template_popup_confirm "bpy.types.UILayout.template_popup_confirm") - [`WindowManager.operator_properties_last`](bpy.types.WindowManager.md#bpy.types.WindowManager.operator_properties_last "bpy.types.WindowManager.operator_properties_last") - [`WorkSpaceTool.operator_properties`](bpy.types.WorkSpaceTool.md#bpy.types.WorkSpaceTool.operator_properties "bpy.types.WorkSpaceTool.operator_properties") - [`XrActionMapItem.op_properties`](bpy.types.XrActionMapItem.md#bpy.types.XrActionMapItem.op_properties "bpy.types.XrActionMapItem.op_properties") |
