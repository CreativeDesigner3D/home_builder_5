<!-- source: Blender Python API reference 5.2 / bpy.types.MaskLayers.html -->

<a id="masklayers-bpy-prop-collection"></a>

# MaskLayers(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.MaskLayers"></a>

### class bpy.types.MaskLayers(bpy_prop_collection)

Collection of layers used by mask

<a id="bpy.types.MaskLayers.active"></a>

#### bpy.types.MaskLayers.active

Active layer in this mask

**Type:**

[`MaskLayer`](bpy.types.MaskLayer.md#bpy.types.MaskLayer "bpy.types.MaskLayer") | None

<a id="bpy.types.MaskLayers.new"></a>

#### bpy.types.MaskLayers.new(*, name='')

Add layer to this mask

**Parameters:**

**name** (str) – Name, Name of new layer (optional, never None)

**Returns:**

New mask layer

**Return type:**

[`MaskLayer`](bpy.types.MaskLayer.md#bpy.types.MaskLayer "bpy.types.MaskLayer")

<a id="bpy.types.MaskLayers.remove"></a>

#### bpy.types.MaskLayers.remove(layer)

Remove layer from this mask

**Parameters:**

**layer** ([`MaskLayer`](bpy.types.MaskLayer.md#bpy.types.MaskLayer "bpy.types.MaskLayer") | None) – Shape to be removed (never None)

<a id="bpy.types.MaskLayers.clear"></a>

#### bpy.types.MaskLayers.clear()

Remove all mask layers

<a id="bpy.types.MaskLayers.bl_rna_get_subclass"></a>

#### classmethod bpy.types.MaskLayers.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.MaskLayers.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.MaskLayers.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Mask.layers`](bpy.types.Mask.md#bpy.types.Mask.layers "bpy.types.Mask.layers") |  |
