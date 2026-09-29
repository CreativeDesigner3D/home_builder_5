<!-- source: Blender Python API reference 5.2 / bpy.types.ActionLayers.html -->

<a id="actionlayers-bpy-prop-collection"></a>

# ActionLayers(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.ActionLayers"></a>

### class bpy.types.ActionLayers(bpy_prop_collection)

Collection of animation layers

<a id="bpy.types.ActionLayers.new"></a>

#### bpy.types.ActionLayers.new(name)

Add a layer to the Animation. Currently an Animation can only have at most one layer.

**Parameters:**

**name** (str) – Name, Name of the layer, will be made unique within the Action (never None)

**Returns:**

Newly created animation layer

**Return type:**

[`ActionLayer`](bpy.types.ActionLayer.md#bpy.types.ActionLayer "bpy.types.ActionLayer")

<a id="bpy.types.ActionLayers.remove"></a>

#### bpy.types.ActionLayers.remove(anim_layer)

Remove the layer from the animation

**Parameters:**

**anim_layer** ([`ActionLayer`](bpy.types.ActionLayer.md#bpy.types.ActionLayer "bpy.types.ActionLayer") | None) – Animation Layer, The layer to remove

<a id="bpy.types.ActionLayers.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ActionLayers.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ActionLayers.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ActionLayers.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Action.layers`](bpy.types.Action.md#bpy.types.Action.layers "bpy.types.Action.layers") |  |
