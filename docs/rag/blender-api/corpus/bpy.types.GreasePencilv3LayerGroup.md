<!-- source: Blender Python API reference 5.2 / bpy.types.GreasePencilv3LayerGroup.html -->

<a id="greasepencilv3layergroup-bpy-prop-collection"></a>

# GreasePencilv3LayerGroup(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.GreasePencilv3LayerGroup"></a>

### class bpy.types.GreasePencilv3LayerGroup(bpy_prop_collection)

Collection of Grease Pencil layers

<a id="bpy.types.GreasePencilv3LayerGroup.active"></a>

#### bpy.types.GreasePencilv3LayerGroup.active

Active Grease Pencil layer group

**Type:**

[`GreasePencilLayerGroup`](bpy.types.GreasePencilLayerGroup.md#bpy.types.GreasePencilLayerGroup "bpy.types.GreasePencilLayerGroup") | None

<a id="bpy.types.GreasePencilv3LayerGroup.new"></a>

#### bpy.types.GreasePencilv3LayerGroup.new(name, *, parent_group=None)

Add a new Grease Pencil layer group

**Parameters:**

- **name** (str) – Name, Name of the layer group (never None)
- **parent_group** ([`GreasePencilLayerGroup`](bpy.types.GreasePencilLayerGroup.md#bpy.types.GreasePencilLayerGroup "bpy.types.GreasePencilLayerGroup") | None) – The parent layer group the new group will be created in (use None for the main stack) (optional)

**Returns:**

The newly created layer group

**Return type:**

[`GreasePencilLayerGroup`](bpy.types.GreasePencilLayerGroup.md#bpy.types.GreasePencilLayerGroup "bpy.types.GreasePencilLayerGroup")

<a id="bpy.types.GreasePencilv3LayerGroup.remove"></a>

#### bpy.types.GreasePencilv3LayerGroup.remove(layer_group, *, keep_children=False)

Remove a new Grease Pencil layer group

**Parameters:**

- **layer_group** ([`GreasePencilLayerGroup`](bpy.types.GreasePencilLayerGroup.md#bpy.types.GreasePencilLayerGroup "bpy.types.GreasePencilLayerGroup") | None) – The layer group to remove (never None)
- **keep_children** (bool) – Keep the children nodes of the group and only delete the group itself (optional)

<a id="bpy.types.GreasePencilv3LayerGroup.move"></a>

#### bpy.types.GreasePencilv3LayerGroup.move(layer_group, type)

Move a layer group in the parent layer group or main stack

**Parameters:**

- **layer_group** ([`GreasePencilLayerGroup`](bpy.types.GreasePencilLayerGroup.md#bpy.types.GreasePencilLayerGroup "bpy.types.GreasePencilLayerGroup") | None) – The layer group to move (never None)
- **type** (Literal['DOWN', 'UP']) – Direction of movement

<a id="bpy.types.GreasePencilv3LayerGroup.move_top"></a>

#### bpy.types.GreasePencilv3LayerGroup.move_top(layer_group)

Move a layer group to the top of the parent layer group or main stack

**Parameters:**

**layer_group** ([`GreasePencilLayerGroup`](bpy.types.GreasePencilLayerGroup.md#bpy.types.GreasePencilLayerGroup "bpy.types.GreasePencilLayerGroup") | None) – The layer group to move (never None)

<a id="bpy.types.GreasePencilv3LayerGroup.move_bottom"></a>

#### bpy.types.GreasePencilv3LayerGroup.move_bottom(layer_group)

Move a layer group to the bottom of the parent layer group or main stack

**Parameters:**

**layer_group** ([`GreasePencilLayerGroup`](bpy.types.GreasePencilLayerGroup.md#bpy.types.GreasePencilLayerGroup "bpy.types.GreasePencilLayerGroup") | None) – The layer group to move (never None)

<a id="bpy.types.GreasePencilv3LayerGroup.move_to_layer_group"></a>

#### bpy.types.GreasePencilv3LayerGroup.move_to_layer_group(layer_group, parent_group)

Move a layer group into a parent layer group

**Parameters:**

- **layer_group** ([`GreasePencilLayerGroup`](bpy.types.GreasePencilLayerGroup.md#bpy.types.GreasePencilLayerGroup "bpy.types.GreasePencilLayerGroup") | None) – The layer group to move (never None)
- **parent_group** ([`GreasePencilLayerGroup`](bpy.types.GreasePencilLayerGroup.md#bpy.types.GreasePencilLayerGroup "bpy.types.GreasePencilLayerGroup") | None) – The parent layer group the layer group will be moved into (use None for the main stack)

<a id="bpy.types.GreasePencilv3LayerGroup.bl_rna_get_subclass"></a>

#### classmethod bpy.types.GreasePencilv3LayerGroup.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.GreasePencilv3LayerGroup.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.GreasePencilv3LayerGroup.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`GreasePencil.layer_groups`](bpy.types.GreasePencil.md#bpy.types.GreasePencil.layer_groups "bpy.types.GreasePencil.layer_groups") |  |
