<!-- source: Blender Python API reference 5.2 / bpy.types.GreasePencilv3Layers.html -->

<a id="greasepencilv3layers-bpy-prop-collection"></a>

# GreasePencilv3Layers(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.GreasePencilv3Layers"></a>

### class bpy.types.GreasePencilv3Layers(bpy_prop_collection)

Collection of Grease Pencil layers

<a id="bpy.types.GreasePencilv3Layers.active"></a>

#### bpy.types.GreasePencilv3Layers.active

Active Grease Pencil layer

**Type:**

[`GreasePencilLayer`](bpy.types.GreasePencilLayer.md#bpy.types.GreasePencilLayer "bpy.types.GreasePencilLayer") | None

<a id="bpy.types.GreasePencilv3Layers.new"></a>

#### bpy.types.GreasePencilv3Layers.new(name, *, set_active=True, layer_group=None)

Add a new Grease Pencil layer

**Parameters:**

- **name** (str) – Name, Name of the layer (never None)
- **set_active** (bool) – Set Active, Set the newly created layer as the active layer (optional)
- **layer_group** ([`GreasePencilLayerGroup`](bpy.types.GreasePencilLayerGroup.md#bpy.types.GreasePencilLayerGroup "bpy.types.GreasePencilLayerGroup") | None) – The layer group the new layer will be created in (use None for the main stack) (optional)

**Returns:**

The newly created layer

**Return type:**

[`GreasePencilLayer`](bpy.types.GreasePencilLayer.md#bpy.types.GreasePencilLayer "bpy.types.GreasePencilLayer")

<a id="bpy.types.GreasePencilv3Layers.remove"></a>

#### bpy.types.GreasePencilv3Layers.remove(layer)

Remove a Grease Pencil layer

**Parameters:**

**layer** ([`GreasePencilLayer`](bpy.types.GreasePencilLayer.md#bpy.types.GreasePencilLayer "bpy.types.GreasePencilLayer") | None) – The layer to remove (never None)

<a id="bpy.types.GreasePencilv3Layers.move"></a>

#### bpy.types.GreasePencilv3Layers.move(layer, type)

Move a Grease Pencil layer in the layer group or main stack

**Parameters:**

- **layer** ([`GreasePencilLayer`](bpy.types.GreasePencilLayer.md#bpy.types.GreasePencilLayer "bpy.types.GreasePencilLayer") | None) – The layer to move (never None)
- **type** (Literal['DOWN', 'UP']) – Direction of movement

<a id="bpy.types.GreasePencilv3Layers.move_top"></a>

#### bpy.types.GreasePencilv3Layers.move_top(layer)

Move a Grease Pencil layer to the top of the layer group or main stack

**Parameters:**

**layer** ([`GreasePencilLayer`](bpy.types.GreasePencilLayer.md#bpy.types.GreasePencilLayer "bpy.types.GreasePencilLayer") | None) – The layer to move (never None)

<a id="bpy.types.GreasePencilv3Layers.move_bottom"></a>

#### bpy.types.GreasePencilv3Layers.move_bottom(layer)

Move a Grease Pencil layer to the bottom of the layer group or main stack

**Parameters:**

**layer** ([`GreasePencilLayer`](bpy.types.GreasePencilLayer.md#bpy.types.GreasePencilLayer "bpy.types.GreasePencilLayer") | None) – The layer to move (never None)

<a id="bpy.types.GreasePencilv3Layers.move_to_layer_group"></a>

#### bpy.types.GreasePencilv3Layers.move_to_layer_group(layer, layer_group)

Move a Grease Pencil layer into a layer group

**Parameters:**

- **layer** ([`GreasePencilLayer`](bpy.types.GreasePencilLayer.md#bpy.types.GreasePencilLayer "bpy.types.GreasePencilLayer") | None) – The layer to move (never None)
- **layer_group** ([`GreasePencilLayerGroup`](bpy.types.GreasePencilLayerGroup.md#bpy.types.GreasePencilLayerGroup "bpy.types.GreasePencilLayerGroup") | None) – The layer group the layer will be moved into (use None for the main stack)

<a id="bpy.types.GreasePencilv3Layers.bl_rna_get_subclass"></a>

#### classmethod bpy.types.GreasePencilv3Layers.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.GreasePencilv3Layers.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.GreasePencilv3Layers.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`GreasePencil.layers`](bpy.types.GreasePencil.md#bpy.types.GreasePencil.layers "bpy.types.GreasePencil.layers") |  |
