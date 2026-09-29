<!-- source: Blender Python API reference 5.2 / bpy.types.RepeatItem.html -->

<a id="repeatitem-bpy-struct"></a>

# RepeatItem(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.RepeatItem"></a>

### class bpy.types.RepeatItem(bpy_struct)

<a id="bpy.types.RepeatItem.color"></a>

#### bpy.types.RepeatItem.color

Color of the corresponding socket type in the node editor (array of 4 items, in [0, inf], default (0.0, 0.0, 0.0, 0.0), readonly)

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.RepeatItem.name"></a>

#### bpy.types.RepeatItem.name

(default “”, never None)

**Type:**

str

<a id="bpy.types.RepeatItem.socket_type"></a>

#### bpy.types.RepeatItem.socket_type

(default `'FLOAT'`)

**Type:**

Literal[[Node Socket Data Type Items](bpy_types_enum_items/node_socket_data_type_items.md#rna-enum-node-socket-data-type-items)]

<a id="bpy.types.RepeatItem.bl_rna_get_subclass"></a>

#### classmethod bpy.types.RepeatItem.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.RepeatItem.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.RepeatItem.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`GeometryNodeBake.active_item`](bpy.types.GeometryNodeBake.md#bpy.types.GeometryNodeBake.active_item "bpy.types.GeometryNodeBake.active_item") - [`GeometryNodeCaptureAttribute.active_item`](bpy.types.GeometryNodeCaptureAttribute.md#bpy.types.GeometryNodeCaptureAttribute.active_item "bpy.types.GeometryNodeCaptureAttribute.active_item") - [`GeometryNodeClosureToList.active_item`](bpy.types.GeometryNodeClosureToList.md#bpy.types.GeometryNodeClosureToList.active_item "bpy.types.GeometryNodeClosureToList.active_item") - [`GeometryNodeFieldToGrid.active_item`](bpy.types.GeometryNodeFieldToGrid.md#bpy.types.GeometryNodeFieldToGrid.active_item "bpy.types.GeometryNodeFieldToGrid.active_item") - [`GeometryNodeRepeatOutput.active_item`](bpy.types.GeometryNodeRepeatOutput.md#bpy.types.GeometryNodeRepeatOutput.active_item "bpy.types.GeometryNodeRepeatOutput.active_item") | - [`GeometryNodeRepeatOutput.repeat_items`](bpy.types.GeometryNodeRepeatOutput.md#bpy.types.GeometryNodeRepeatOutput.repeat_items "bpy.types.GeometryNodeRepeatOutput.repeat_items") - [`NodeGeometryRepeatOutputItems.new`](bpy.types.NodeGeometryRepeatOutputItems.md#bpy.types.NodeGeometryRepeatOutputItems.new "bpy.types.NodeGeometryRepeatOutputItems.new") - [`NodeGeometryRepeatOutputItems.remove`](bpy.types.NodeGeometryRepeatOutputItems.md#bpy.types.NodeGeometryRepeatOutputItems.remove "bpy.types.NodeGeometryRepeatOutputItems.remove") - [`ShaderNodeRaycast.active_item`](bpy.types.ShaderNodeRaycast.md#bpy.types.ShaderNodeRaycast.active_item "bpy.types.ShaderNodeRaycast.active_item") |
