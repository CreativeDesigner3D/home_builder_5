<!-- source: Blender Python API reference 5.2 / bpy.types.SpaceNodeEditorPath.html -->

<a id="spacenodeeditorpath-bpy-prop-collection"></a>

# SpaceNodeEditorPath(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.SpaceNodeEditorPath"></a>

### class bpy.types.SpaceNodeEditorPath(bpy_prop_collection)

Get the node tree path as a string

<a id="bpy.types.SpaceNodeEditorPath.to_string"></a>

#### bpy.types.SpaceNodeEditorPath.to_string

(default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.SpaceNodeEditorPath.clear"></a>

#### bpy.types.SpaceNodeEditorPath.clear()

Reset the node tree path

<a id="bpy.types.SpaceNodeEditorPath.start"></a>

#### bpy.types.SpaceNodeEditorPath.start(node_tree)

Set the root node tree

**Parameters:**

**node_tree** ([`NodeTree`](bpy.types.NodeTree.md#bpy.types.NodeTree "bpy.types.NodeTree") | None) – Node Tree

<a id="bpy.types.SpaceNodeEditorPath.append"></a>

#### bpy.types.SpaceNodeEditorPath.append(node_tree, *, node=None)

Append a node group tree to the path

**Parameters:**

- **node_tree** ([`NodeTree`](bpy.types.NodeTree.md#bpy.types.NodeTree "bpy.types.NodeTree") | None) – Node Tree, Node tree to append to the node editor path
- **node** ([`Node`](bpy.types.Node.md#bpy.types.Node "bpy.types.Node") | None) – Node, Group node linking to this node tree (optional)

<a id="bpy.types.SpaceNodeEditorPath.pop"></a>

#### bpy.types.SpaceNodeEditorPath.pop()

Remove the last node tree from the path

<a id="bpy.types.SpaceNodeEditorPath.bl_rna_get_subclass"></a>

#### classmethod bpy.types.SpaceNodeEditorPath.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.SpaceNodeEditorPath.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.SpaceNodeEditorPath.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`SpaceNodeEditor.path`](bpy.types.SpaceNodeEditor.md#bpy.types.SpaceNodeEditor.path "bpy.types.SpaceNodeEditor.path") |  |
