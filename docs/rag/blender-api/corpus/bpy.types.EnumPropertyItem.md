<!-- source: Blender Python API reference 5.2 / bpy.types.EnumPropertyItem.html -->

<a id="enumpropertyitem-bpy-struct"></a>

# EnumPropertyItem(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.EnumPropertyItem"></a>

### class bpy.types.EnumPropertyItem(bpy_struct)

Definition of a choice in an RNA enum property

<a id="bpy.types.EnumPropertyItem.description"></a>

#### bpy.types.EnumPropertyItem.description

Description of the item’s purpose (default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.EnumPropertyItem.icon"></a>

#### bpy.types.EnumPropertyItem.icon

Icon of the item (default `'NONE'`, readonly)

**Type:**

Literal[[Icon Items](bpy_types_enum_items/icon_items.md#rna-enum-icon-items)]

<a id="bpy.types.EnumPropertyItem.identifier"></a>

#### bpy.types.EnumPropertyItem.identifier

Unique name used in the code and scripting (default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.EnumPropertyItem.name"></a>

#### bpy.types.EnumPropertyItem.name

Human readable name (default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.EnumPropertyItem.value"></a>

#### bpy.types.EnumPropertyItem.value

Value of the item (in [0, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.EnumPropertyItem.bl_rna_get_subclass"></a>

#### classmethod bpy.types.EnumPropertyItem.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.EnumPropertyItem.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.EnumPropertyItem.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`EnumProperty.enum_items`](bpy.types.EnumProperty.md#bpy.types.EnumProperty.enum_items "bpy.types.EnumProperty.enum_items") - [`EnumProperty.enum_items_static`](bpy.types.EnumProperty.md#bpy.types.EnumProperty.enum_items_static "bpy.types.EnumProperty.enum_items_static") - [`EnumProperty.enum_items_static_ui`](bpy.types.EnumProperty.md#bpy.types.EnumProperty.enum_items_static_ui "bpy.types.EnumProperty.enum_items_static_ui") | - [`KeyMap.modal_event_values`](bpy.types.KeyMap.md#bpy.types.KeyMap.modal_event_values "bpy.types.KeyMap.modal_event_values") - [`Struct.property_tags`](bpy.types.Struct.md#bpy.types.Struct.property_tags "bpy.types.Struct.property_tags") |
