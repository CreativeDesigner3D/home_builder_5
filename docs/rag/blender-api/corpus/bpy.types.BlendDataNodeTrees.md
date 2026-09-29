<!-- source: Blender Python API reference 5.2 / bpy.types.BlendDataNodeTrees.html -->

<a id="blenddatanodetrees-bpy-prop-collection"></a>

# BlendDataNodeTrees(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.BlendDataNodeTrees"></a>

### class bpy.types.BlendDataNodeTrees(bpy_prop_collection)

Collection of node trees

<a id="bpy.types.BlendDataNodeTrees.new"></a>

#### bpy.types.BlendDataNodeTrees.new(name, type)

Add a new node tree to the main database

**Parameters:**

- **name** (str) – New name for the data-block (never None)
- **type** (Literal['GeometryNodeTree', 'CompositorNodeTree', 'ShaderNodeTree', 'TextureNodeTree']) –

  Type, The type of node_group to add

  - `GeometryNodeTree`
    Geometry Node Editor – Advanced geometry editing and tools creation using nodes.
  - `CompositorNodeTree`
    Compositor – Create effects and post-process renders, images, and the 3D Viewport.
  - `ShaderNodeTree`
    Shader Editor – Edit materials, lights, and world shading using nodes.
  - `TextureNodeTree`
    Texture Node Editor – Edit textures using nodes.

**Returns:**

New node tree data-block

**Return type:**

[`NodeTree`](bpy.types.NodeTree.md#bpy.types.NodeTree "bpy.types.NodeTree")

<a id="bpy.types.BlendDataNodeTrees.remove"></a>

#### bpy.types.BlendDataNodeTrees.remove(tree, *, do_unlink=True, do_id_user=True, do_ui_user=True)

Remove a node tree from the current blendfile

**Parameters:**

- **tree** ([`NodeTree`](bpy.types.NodeTree.md#bpy.types.NodeTree "bpy.types.NodeTree") | None) – Node tree to remove (never None)
- **do_unlink** (bool) – Unlink all usages of this node tree before deleting it (optional)
- **do_id_user** (bool) – Decrement user counter of all data-blocks used by this node tree (optional)
- **do_ui_user** (bool) – Make sure interface does not reference this node tree (optional)

<a id="bpy.types.BlendDataNodeTrees.tag"></a>

#### bpy.types.BlendDataNodeTrees.tag(value)

tag

**Parameters:**

**value** (bool) – Value

<a id="bpy.types.BlendDataNodeTrees.bl_rna_get_subclass"></a>

#### classmethod bpy.types.BlendDataNodeTrees.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.BlendDataNodeTrees.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.BlendDataNodeTrees.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`BlendData.node_groups`](bpy.types.BlendData.md#bpy.types.BlendData.node_groups "bpy.types.BlendData.node_groups") |  |
