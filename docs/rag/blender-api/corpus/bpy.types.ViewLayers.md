<!-- source: Blender Python API reference 5.2 / bpy.types.ViewLayers.html -->

<a id="viewlayers-bpy-prop-collection"></a>

# ViewLayers(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.ViewLayers"></a>

### class bpy.types.ViewLayers(bpy_prop_collection)

Collection of render layers

<a id="bpy.types.ViewLayers.new"></a>

#### bpy.types.ViewLayers.new(name)

Add a view layer to scene

**Parameters:**

**name** (str) – New name for the view layer (not unique) (never None)

**Returns:**

Newly created view layer

**Return type:**

[`ViewLayer`](bpy.types.ViewLayer.md#bpy.types.ViewLayer "bpy.types.ViewLayer")

<a id="bpy.types.ViewLayers.remove"></a>

#### bpy.types.ViewLayers.remove(layer)

Remove a view layer

**Parameters:**

**layer** ([`ViewLayer`](bpy.types.ViewLayer.md#bpy.types.ViewLayer "bpy.types.ViewLayer") | None) – View layer to remove (never None)

<a id="bpy.types.ViewLayers.move"></a>

#### bpy.types.ViewLayers.move(from_index, to_index)

Move a view layer

**Parameters:**

- **from_index** (int) – From Index, Index to move (in [-inf, inf])
- **to_index** (int) – To Index, Target index (in [-inf, inf])

<a id="bpy.types.ViewLayers.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ViewLayers.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ViewLayers.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ViewLayers.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Scene.view_layers`](bpy.types.Scene.md#bpy.types.Scene.view_layers "bpy.types.Scene.view_layers") |  |
