<!-- source: Blender Python API reference 5.2 / bpy.types.GreasePencilLayerGroup.html -->

<a id="greasepencillayergroup-greasepenciltreenode"></a>

# GreasePencilLayerGroup(GreasePencilTreeNode)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`GreasePencilTreeNode`](bpy.types.GreasePencilTreeNode.md#bpy.types.GreasePencilTreeNode "bpy.types.GreasePencilTreeNode")

<a id="bpy.types.GreasePencilLayerGroup"></a>

### class bpy.types.GreasePencilLayerGroup(GreasePencilTreeNode)

Group of Grease Pencil layers

<a id="bpy.types.GreasePencilLayerGroup.children"></a>

#### bpy.types.GreasePencilLayerGroup.children

The direct children of this layer group. Ordered by stack order, meaning the first child is the bottom most child in the layer tree. (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`GreasePencilTreeNode`](bpy.types.GreasePencilTreeNode.md#bpy.types.GreasePencilTreeNode "bpy.types.GreasePencilTreeNode")]

<a id="bpy.types.GreasePencilLayerGroup.color_tag"></a>

#### bpy.types.GreasePencilLayerGroup.color_tag

(default `'COLOR1'`)

**Type:**

Literal[‘NONE’, ‘COLOR1’, ‘COLOR2’, ‘COLOR3’, ‘COLOR4’, ‘COLOR5’, ‘COLOR6’, ‘COLOR7’, ‘COLOR8’]

<a id="bpy.types.GreasePencilLayerGroup.is_expanded"></a>

#### bpy.types.GreasePencilLayerGroup.is_expanded

The layer group is expanded in the UI (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilLayerGroup.bl_rna_get_subclass"></a>

#### classmethod bpy.types.GreasePencilLayerGroup.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.GreasePencilLayerGroup.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.GreasePencilLayerGroup.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, GreasePencilTreeNode.name, GreasePencilTreeNode.hide, GreasePencilTreeNode.lock, GreasePencilTreeNode.select, GreasePencilTreeNode.use_onion_skinning, GreasePencilTreeNode.use_masks, GreasePencilTreeNode.channel_color, GreasePencilTreeNode.next_node, GreasePencilTreeNode.prev_node, GreasePencilTreeNode.parent_group

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, GreasePencilTreeNode.bl_rna_get_subclass, GreasePencilTreeNode.bl_rna_get_subclass_py

<a id="references"></a>

## References

|  |  |
| --- | --- |
| - [`GreasePencil.layer_groups`](bpy.types.GreasePencil.md#bpy.types.GreasePencil.layer_groups "bpy.types.GreasePencil.layer_groups") - [`GreasePencilTreeNode.parent_group`](bpy.types.GreasePencilTreeNode.md#bpy.types.GreasePencilTreeNode.parent_group "bpy.types.GreasePencilTreeNode.parent_group") - [`GreasePencilv3LayerGroup.active`](bpy.types.GreasePencilv3LayerGroup.md#bpy.types.GreasePencilv3LayerGroup.active "bpy.types.GreasePencilv3LayerGroup.active") - [`GreasePencilv3LayerGroup.move`](bpy.types.GreasePencilv3LayerGroup.md#bpy.types.GreasePencilv3LayerGroup.move "bpy.types.GreasePencilv3LayerGroup.move") - [`GreasePencilv3LayerGroup.move_bottom`](bpy.types.GreasePencilv3LayerGroup.md#bpy.types.GreasePencilv3LayerGroup.move_bottom "bpy.types.GreasePencilv3LayerGroup.move_bottom") - [`GreasePencilv3LayerGroup.move_to_layer_group`](bpy.types.GreasePencilv3LayerGroup.md#bpy.types.GreasePencilv3LayerGroup.move_to_layer_group "bpy.types.GreasePencilv3LayerGroup.move_to_layer_group") - [`GreasePencilv3LayerGroup.move_to_layer_group`](bpy.types.GreasePencilv3LayerGroup.md#bpy.types.GreasePencilv3LayerGroup.move_to_layer_group "bpy.types.GreasePencilv3LayerGroup.move_to_layer_group") | - [`GreasePencilv3LayerGroup.move_top`](bpy.types.GreasePencilv3LayerGroup.md#bpy.types.GreasePencilv3LayerGroup.move_top "bpy.types.GreasePencilv3LayerGroup.move_top") - [`GreasePencilv3LayerGroup.new`](bpy.types.GreasePencilv3LayerGroup.md#bpy.types.GreasePencilv3LayerGroup.new "bpy.types.GreasePencilv3LayerGroup.new") - [`GreasePencilv3LayerGroup.new`](bpy.types.GreasePencilv3LayerGroup.md#bpy.types.GreasePencilv3LayerGroup.new "bpy.types.GreasePencilv3LayerGroup.new") - [`GreasePencilv3LayerGroup.remove`](bpy.types.GreasePencilv3LayerGroup.md#bpy.types.GreasePencilv3LayerGroup.remove "bpy.types.GreasePencilv3LayerGroup.remove") - [`GreasePencilv3Layers.move_to_layer_group`](bpy.types.GreasePencilv3Layers.md#bpy.types.GreasePencilv3Layers.move_to_layer_group "bpy.types.GreasePencilv3Layers.move_to_layer_group") - [`GreasePencilv3Layers.new`](bpy.types.GreasePencilv3Layers.md#bpy.types.GreasePencilv3Layers.new "bpy.types.GreasePencilv3Layers.new") |
