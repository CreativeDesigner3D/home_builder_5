<!-- source: Blender Python API reference 5.2 / bpy.types.MeshUVLoopLayer.html -->

<a id="meshuvlooplayer-bpy-struct"></a>

# MeshUVLoopLayer(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.MeshUVLoopLayer"></a>

### class bpy.types.MeshUVLoopLayer(bpy_struct)

<a id="bpy.types.MeshUVLoopLayer.active"></a>

#### bpy.types.MeshUVLoopLayer.active

Set the map as active for display and editing (default False)

**Type:**

bool

<a id="bpy.types.MeshUVLoopLayer.active_clone"></a>

#### bpy.types.MeshUVLoopLayer.active_clone

Set the map as active for cloning (default False)

**Type:**

bool

<a id="bpy.types.MeshUVLoopLayer.active_render"></a>

#### bpy.types.MeshUVLoopLayer.active_render

Set the UV map as active for rendering (default False)

**Type:**

bool

<a id="bpy.types.MeshUVLoopLayer.data"></a>

#### bpy.types.MeshUVLoopLayer.data

Deprecated, use ‘uv’, ‘vertex_select’, ‘edge_select’ or ‘pin’ properties instead (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`MeshUVLoop`](bpy.types.MeshUVLoop.md#bpy.types.MeshUVLoop "bpy.types.MeshUVLoop")]

<a id="bpy.types.MeshUVLoopLayer.name"></a>

#### bpy.types.MeshUVLoopLayer.name

Name of UV map (default “”, never None)

**Type:**

str

<a id="bpy.types.MeshUVLoopLayer.pin"></a>

#### bpy.types.MeshUVLoopLayer.pin

UV pinned state in the UV editor (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`BoolAttributeValue`](bpy.types.BoolAttributeValue.md#bpy.types.BoolAttributeValue "bpy.types.BoolAttributeValue")]

<a id="bpy.types.MeshUVLoopLayer.uv"></a>

#### bpy.types.MeshUVLoopLayer.uv

UV coordinates on face corners (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`Float2AttributeValue`](bpy.types.Float2AttributeValue.md#bpy.types.Float2AttributeValue "bpy.types.Float2AttributeValue")]

<a id="bpy.types.MeshUVLoopLayer.pin_ensure"></a>

#### bpy.types.MeshUVLoopLayer.pin_ensure()

pin_ensure

**Returns:**

The boolean attribute

**Return type:**

[`BoolAttribute`](bpy.types.BoolAttribute.md#bpy.types.BoolAttribute "bpy.types.BoolAttribute")

<a id="bpy.types.MeshUVLoopLayer.bl_rna_get_subclass"></a>

#### classmethod bpy.types.MeshUVLoopLayer.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.MeshUVLoopLayer.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.MeshUVLoopLayer.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Mesh.uv_layer_clone`](bpy.types.Mesh.md#bpy.types.Mesh.uv_layer_clone "bpy.types.Mesh.uv_layer_clone") - [`Mesh.uv_layer_stencil`](bpy.types.Mesh.md#bpy.types.Mesh.uv_layer_stencil "bpy.types.Mesh.uv_layer_stencil") - [`Mesh.uv_layers`](bpy.types.Mesh.md#bpy.types.Mesh.uv_layers "bpy.types.Mesh.uv_layers") - [`UVLoopLayers.active`](bpy.types.UVLoopLayers.md#bpy.types.UVLoopLayers.active "bpy.types.UVLoopLayers.active") | - [`UVLoopLayers.active_render`](bpy.types.UVLoopLayers.md#bpy.types.UVLoopLayers.active_render "bpy.types.UVLoopLayers.active_render") - [`UVLoopLayers.new`](bpy.types.UVLoopLayers.md#bpy.types.UVLoopLayers.new "bpy.types.UVLoopLayers.new") - [`UVLoopLayers.remove`](bpy.types.UVLoopLayers.md#bpy.types.UVLoopLayers.remove "bpy.types.UVLoopLayers.remove") |
