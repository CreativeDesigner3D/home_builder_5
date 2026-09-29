<!-- source: Blender Python API reference 5.2 / bpy.types.POSE_UL_selection_set.html -->

<a id="pose-ul-selection-set-uilist"></a>

# POSE_UL_selection_set(UIList)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`UIList`](bpy.types.UIList.md#bpy.types.UIList "bpy.types.UIList")

<a id="bpy.types.POSE_UL_selection_set"></a>

### class bpy.types.POSE_UL_selection_set(UIList)

<a id="bpy.types.POSE_UL_selection_set.bl_rna_get_subclass"></a>

#### classmethod bpy.types.POSE_UL_selection_set.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.POSE_UL_selection_set.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.POSE_UL_selection_set.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, UIList.bl_idname, UIList.list_id, UIList.layout_type, UIList.use_filter_show, UIList.filter_name, UIList.use_filter_invert, UIList.use_filter_sort_alpha, UIList.use_filter_sort_reverse, UIList.use_filter_sort_lock, UIList.bitflag_filter_item, UIList.bitflag_item_never_show

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, UIList.bl_system_properties_get, UIList.draw_item, UIList.draw_filter, UIList.filter_items, UIList.append, UIList.is_extended, UIList.prepend, UIList.remove, UIList.bl_rna_get_subclass, UIList.bl_rna_get_subclass_py
