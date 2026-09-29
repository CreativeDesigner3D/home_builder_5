<!-- source: Blender Python API reference 5.2 / bpy.types.GreasePencilTreeNode.html -->

<a id="greasepenciltreenode-bpy-struct"></a>

# GreasePencilTreeNode(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

Subclasses

- [GreasePencilLayer(GreasePencilTreeNode)](bpy.types.GreasePencilLayer.md)
- [GreasePencilLayerGroup(GreasePencilTreeNode)](bpy.types.GreasePencilLayerGroup.md)

<a id="bpy.types.GreasePencilTreeNode"></a>

### class bpy.types.GreasePencilTreeNode(bpy_struct)

Grease Pencil node in the layer tree. Either a layer or a group

<a id="bpy.types.GreasePencilTreeNode.channel_color"></a>

#### bpy.types.GreasePencilTreeNode.channel_color

Color of the channel in the dope sheet (array of 3 items, in [0, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.GreasePencilTreeNode.hide"></a>

#### bpy.types.GreasePencilTreeNode.hide

Set tree node visibility (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilTreeNode.lock"></a>

#### bpy.types.GreasePencilTreeNode.lock

Protect tree node from editing (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilTreeNode.name"></a>

#### bpy.types.GreasePencilTreeNode.name

The name of the tree node (default “”, never None)

**Type:**

str

<a id="bpy.types.GreasePencilTreeNode.next_node"></a>

#### bpy.types.GreasePencilTreeNode.next_node

The layer tree node after (i.e. above) this one (readonly)

**Type:**

[`GreasePencilTreeNode`](#bpy.types.GreasePencilTreeNode "bpy.types.GreasePencilTreeNode") | None

<a id="bpy.types.GreasePencilTreeNode.parent_group"></a>

#### bpy.types.GreasePencilTreeNode.parent_group

The parent group of this layer tree node (readonly)

**Type:**

[`GreasePencilLayerGroup`](bpy.types.GreasePencilLayerGroup.md#bpy.types.GreasePencilLayerGroup "bpy.types.GreasePencilLayerGroup") | None

<a id="bpy.types.GreasePencilTreeNode.prev_node"></a>

#### bpy.types.GreasePencilTreeNode.prev_node

The layer tree node before (i.e. below) this one (readonly)

**Type:**

[`GreasePencilTreeNode`](#bpy.types.GreasePencilTreeNode "bpy.types.GreasePencilTreeNode") | None

<a id="bpy.types.GreasePencilTreeNode.select"></a>

#### bpy.types.GreasePencilTreeNode.select

Tree node is selected (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilTreeNode.use_masks"></a>

#### bpy.types.GreasePencilTreeNode.use_masks

The visibility of drawings in this tree node is affected by the layers in the masks list (default True)

**Type:**

bool

<a id="bpy.types.GreasePencilTreeNode.use_onion_skinning"></a>

#### bpy.types.GreasePencilTreeNode.use_onion_skinning

Display onion skins before and after the current frame (default True)

**Type:**

bool

<a id="bpy.types.GreasePencilTreeNode.bl_rna_get_subclass"></a>

#### classmethod bpy.types.GreasePencilTreeNode.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.GreasePencilTreeNode.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.GreasePencilTreeNode.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`GreasePencil.root_nodes`](bpy.types.GreasePencil.md#bpy.types.GreasePencil.root_nodes "bpy.types.GreasePencil.root_nodes") - [`GreasePencilLayerGroup.children`](bpy.types.GreasePencilLayerGroup.md#bpy.types.GreasePencilLayerGroup.children "bpy.types.GreasePencilLayerGroup.children") | - [`GreasePencilTreeNode.next_node`](#bpy.types.GreasePencilTreeNode.next_node "bpy.types.GreasePencilTreeNode.next_node") - [`GreasePencilTreeNode.prev_node`](#bpy.types.GreasePencilTreeNode.prev_node "bpy.types.GreasePencilTreeNode.prev_node") |
