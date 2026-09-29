<!-- source: Blender Python API reference 5.2 / bpy.types.NodesModifierWarning.html -->

<a id="nodesmodifierwarning-bpy-struct"></a>

# NodesModifierWarning(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.NodesModifierWarning"></a>

### class bpy.types.NodesModifierWarning(bpy_struct)

Warning created during evaluation of a geometry nodes modifier

<a id="bpy.types.NodesModifierWarning.message"></a>

#### bpy.types.NodesModifierWarning.message

(default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.NodesModifierWarning.type"></a>

#### bpy.types.NodesModifierWarning.type

(default `'ERROR'`, readonly)

**Type:**

Literal[[Node Warning Type Items](bpy_types_enum_items/node_warning_type_items.md#rna-enum-node-warning-type-items)]

<a id="bpy.types.NodesModifierWarning.bl_rna_get_subclass"></a>

#### classmethod bpy.types.NodesModifierWarning.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.NodesModifierWarning.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.NodesModifierWarning.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([type](#bpy.types.NodesModifierWarning.type "bpy.types.NodesModifierWarning.type") | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

[type](#bpy.types.NodesModifierWarning.type "bpy.types.NodesModifierWarning.type")

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
| - [`NodesModifier.node_warnings`](bpy.types.NodesModifier.md#bpy.types.NodesModifier.node_warnings "bpy.types.NodesModifier.node_warnings") |  |
