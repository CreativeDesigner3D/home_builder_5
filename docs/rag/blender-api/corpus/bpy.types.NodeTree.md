<!-- source: Blender Python API reference 5.2 / bpy.types.NodeTree.html -->

<a id="nodetree-id"></a>

# NodeTree(ID)

<a id="poll-function"></a>

## Poll Function

The [`NodeTree.poll`](#bpy.types.NodeTree.poll "bpy.types.NodeTree.poll") function determines if a node tree is visible
in the given context (similar to how [`Panel.poll`](bpy.types.Panel.md#bpy.types.Panel.poll "bpy.types.Panel.poll")
and [`Menu.poll`](bpy.types.Menu.md#bpy.types.Menu.poll "bpy.types.Menu.poll") define visibility). If it returns False,
the node tree type will not be selectable in the node editor.

A typical condition for shader nodes would be to check the active render engine
of the scene and only show nodes of the renderer they are designed for.

```python
import bpy

class CyclesNodeTree(bpy.types.NodeTree):
    """ This operator is only visible when Cycles is the selected render engine"""
    bl_label = "Cycles Node Tree"
    bl_icon = 'NONE'

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'CYCLES'

bpy.utils.register_class(CyclesNodeTree)
```

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")

Subclasses

- [CompositorNodeTree(NodeTree)](bpy.types.CompositorNodeTree.md)
- [GeometryNodeTree(NodeTree)](bpy.types.GeometryNodeTree.md)
- [ShaderNodeTree(NodeTree)](bpy.types.ShaderNodeTree.md)
- [TextureNodeTree(NodeTree)](bpy.types.TextureNodeTree.md)

<a id="bpy.types.NodeTree"></a>

### class bpy.types.NodeTree(ID)

Node tree consisting of linked nodes used for shading, textures and compositing

<a id="bpy.types.NodeTree.animation_data"></a>

#### bpy.types.NodeTree.animation_data

Animation data for this data-block (readonly)

**Type:**

[`AnimData`](bpy.types.AnimData.md#bpy.types.AnimData "bpy.types.AnimData") | None

<a id="bpy.types.NodeTree.annotation"></a>

#### bpy.types.NodeTree.annotation

Annotation data

**Type:**

[`Annotation`](bpy.types.Annotation.md#bpy.types.Annotation "bpy.types.Annotation") | None

<a id="bpy.types.NodeTree.bl_description"></a>

#### bpy.types.NodeTree.bl_description

(default “”, never None)

**Type:**

str

<a id="bpy.types.NodeTree.bl_icon"></a>

#### bpy.types.NodeTree.bl_icon

The node tree icon (default `'NODETREE'`)

**Type:**

Literal[[Icon Items](bpy_types_enum_items/icon_items.md#rna-enum-icon-items)]

<a id="bpy.types.NodeTree.bl_idname"></a>

#### bpy.types.NodeTree.bl_idname

(default “”, never None)

**Type:**

str

<a id="bpy.types.NodeTree.bl_label"></a>

#### bpy.types.NodeTree.bl_label

The node tree label (default “”, never None)

**Type:**

str

<a id="bpy.types.NodeTree.bl_use_group_interface"></a>

#### bpy.types.NodeTree.bl_use_group_interface

Determines the visibility of some UI elements related to node groups (default True)

**Type:**

bool

<a id="bpy.types.NodeTree.color_tag"></a>

#### bpy.types.NodeTree.color_tag

Color tag of the node group which influences the header color (default `'NONE'`)

- `NONE`
  None – Default color tag for new nodes and node groups.
- `ATTRIBUTE`
  Attribute.
- `COLOR`
  Color.
- `CONVERTER`
  Converter.
- `DISTORT`
  Distort.
- `FILTER`
  Filter.
- `GEOMETRY`
  Geometry.
- `INPUT`
  Input.
- `MATTE`
  Matte.
- `OUTPUT`
  Output.
- `SCRIPT`
  Script.
- `SHADER`
  Shader.
- `TEXTURE`
  Texture.
- `VECTOR`
  Vector.
- `PATTERN`
  Pattern.
- `INTERFACE`
  Interface.
- `GROUP`
  Group.

**Type:**

Literal[‘NONE’, ‘ATTRIBUTE’, ‘COLOR’, ‘CONVERTER’, ‘DISTORT’, ‘FILTER’, ‘GEOMETRY’, ‘INPUT’, ‘MATTE’, ‘OUTPUT’, ‘SCRIPT’, ‘SHADER’, ‘TEXTURE’, ‘VECTOR’, ‘PATTERN’, ‘INTERFACE’, ‘GROUP’]

<a id="bpy.types.NodeTree.default_group_node_width"></a>

#### bpy.types.NodeTree.default_group_node_width

The width for newly created group nodes (in [60, 700], default 140)

**Type:**

int

<a id="bpy.types.NodeTree.description"></a>

#### bpy.types.NodeTree.description

Description of the node tree (default “”, never None)

**Type:**

str

<a id="bpy.types.NodeTree.interface"></a>

#### bpy.types.NodeTree.interface

Interface declaration for this node tree (readonly)

**Type:**

[`NodeTreeInterface`](bpy.types.NodeTreeInterface.md#bpy.types.NodeTreeInterface "bpy.types.NodeTreeInterface") | None

<a id="bpy.types.NodeTree.links"></a>

#### bpy.types.NodeTree.links

(default None, readonly)

**Type:**

[`NodeLinks`](bpy.types.NodeLinks.md#bpy.types.NodeLinks "bpy.types.NodeLinks")[[`NodeLink`](bpy.types.NodeLink.md#bpy.types.NodeLink "bpy.types.NodeLink")]

<a id="bpy.types.NodeTree.nodes"></a>

#### bpy.types.NodeTree.nodes

(default None, readonly)

**Type:**

[`Nodes`](bpy.types.Nodes.md#bpy.types.Nodes "bpy.types.Nodes")[[`Node`](bpy.types.Node.md#bpy.types.Node "bpy.types.Node")]

<a id="bpy.types.NodeTree.type"></a>

#### bpy.types.NodeTree.type

Node Tree type (deprecated, bl_idname is the actual node tree type identifier) (default `'SHADER'`, readonly)

- `UNDEFINED`
  Undefined – Undefined type of nodes (can happen e.g. when a linked node tree goes missing).
- `CUSTOM`
  Custom – Custom nodes.
- `SHADER`
  Shader – Shader nodes.
- `TEXTURE`
  Texture – Texture nodes.
- `COMPOSITING`
  Compositing – Compositing nodes.
- `GEOMETRY`
  Geometry – Geometry nodes.

**Type:**

Literal[‘UNDEFINED’, ‘CUSTOM’, ‘SHADER’, ‘TEXTURE’, ‘COMPOSITING’, ‘GEOMETRY’]

<a id="bpy.types.NodeTree.view_center"></a>

#### bpy.types.NodeTree.view_center

The current location (offset) of the view for this Node Tree (array of 2 items, in [-inf, inf], default (0.0, 0.0), readonly)

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.NodeTree.interface_update"></a>

#### bpy.types.NodeTree.interface_update(context)

Updated node group interface

**Parameters:**

**context** ([`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context") | None) – (never None)

<a id="bpy.types.NodeTree.contains_tree"></a>

#### bpy.types.NodeTree.contains_tree(sub_tree)

Check if the node tree contains another. Used to avoid creating recursive node groups.

**Parameters:**

**sub_tree** ([`NodeTree`](#bpy.types.NodeTree "bpy.types.NodeTree") | None) – Node Tree, Node tree for recursive check (never None)

**Returns:**

contained

**Return type:**

bool

<a id="bpy.types.NodeTree.poll"></a>

#### classmethod bpy.types.NodeTree.poll(context)

Check visibility in the editor

**Parameters:**

**context** ([`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context") | None) – (never None)

**Return type:**

bool

<a id="bpy.types.NodeTree.update"></a>

#### bpy.types.NodeTree.update()

Update on editor changes

<a id="bpy.types.NodeTree.get_from_context"></a>

#### classmethod bpy.types.NodeTree.get_from_context(context)

Get a node tree from the context

**Parameters:**

**context** ([`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context") | None) – (never None)

**Returns:**

`result_1`, Active node tree from context, [`NodeTree`](#bpy.types.NodeTree "bpy.types.NodeTree")

`result_2`, ID data-block that owns the node tree, [`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")

`result_3`, Original ID data-block selected from the context, [`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")

**Return type:**

tuple[[`NodeTree`](#bpy.types.NodeTree "bpy.types.NodeTree"), [`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID"), [`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")]

<a id="bpy.types.NodeTree.valid_socket_type"></a>

#### classmethod bpy.types.NodeTree.valid_socket_type(idname)

Check if the socket type is valid for the node tree

**Parameters:**

**idname** (str) – Socket Type, Identifier of the socket type (never None)

**Return type:**

bool

<a id="bpy.types.NodeTree.debug_lazy_function_graph"></a>

#### bpy.types.NodeTree.debug_lazy_function_graph()

Get the internal lazy-function graph for this node tree

**Returns:**

Dot Graph, Graph in dot format

**Return type:**

str

<a id="bpy.types.NodeTree.bl_rna_get_subclass"></a>

#### classmethod bpy.types.NodeTree.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.NodeTree.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.NodeTree.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([type](#bpy.types.NodeTree.type "bpy.types.NodeTree.type") | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

[type](#bpy.types.NodeTree.type "bpy.types.NodeTree.type")

<a id="inherited-properties"></a>

### Inherited Properties

bpy_struct.id_data, ID.name, ID.name_full, ID.id_type, ID.session_uid, ID.is_evaluated, ID.original, ID.users, ID.use_fake_user, ID.use_extra_user, ID.is_embedded_data, ID.is_linked_packed, ID.is_missing, ID.is_runtime_data, ID.is_editable, ID.tag, ID.is_library_indirect, ID.library, ID.library_weak_reference, ID.asset_data, ID.override_library, ID.preview

<a id="inherited-functions"></a>

### Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, ID.bl_system_properties_get, ID.rename, ID.evaluated_get, ID.copy, ID.asset_mark, ID.asset_clear, ID.asset_generate_preview, ID.override_create, ID.override_hierarchy_create, ID.user_clear, ID.user_remap, ID.make_local, ID.user_of_id, ID.animation_data_create, ID.animation_data_clear, ID.update_tag, ID.preview_ensure, ID.bl_rna_get_subclass, ID.bl_rna_get_subclass_py

<a id="references"></a>

### References

|  |  |
| --- | --- |
| - [`BlendData.node_groups`](bpy.types.BlendData.md#bpy.types.BlendData.node_groups "bpy.types.BlendData.node_groups") - [`BlendDataNodeTrees.new`](bpy.types.BlendDataNodeTrees.md#bpy.types.BlendDataNodeTrees.new "bpy.types.BlendDataNodeTrees.new") - [`BlendDataNodeTrees.remove`](bpy.types.BlendDataNodeTrees.md#bpy.types.BlendDataNodeTrees.remove "bpy.types.BlendDataNodeTrees.remove") - [`CompositorNodeCustomGroup.node_tree`](bpy.types.CompositorNodeCustomGroup.md#bpy.types.CompositorNodeCustomGroup.node_tree "bpy.types.CompositorNodeCustomGroup.node_tree") - [`CompositorNodeGroup.node_tree`](bpy.types.CompositorNodeGroup.md#bpy.types.CompositorNodeGroup.node_tree "bpy.types.CompositorNodeGroup.node_tree") - [`CompositorStrip.node_group`](bpy.types.CompositorStrip.md#bpy.types.CompositorStrip.node_group "bpy.types.CompositorStrip.node_group") - [`EvaluateClosureNodeViewerPathElem.source_node_tree`](bpy.types.EvaluateClosureNodeViewerPathElem.md#bpy.types.EvaluateClosureNodeViewerPathElem.source_node_tree "bpy.types.EvaluateClosureNodeViewerPathElem.source_node_tree") - [`FreestyleLineStyle.node_tree`](bpy.types.FreestyleLineStyle.md#bpy.types.FreestyleLineStyle.node_tree "bpy.types.FreestyleLineStyle.node_tree") - [`GeometryNodeCustomGroup.node_tree`](bpy.types.GeometryNodeCustomGroup.md#bpy.types.GeometryNodeCustomGroup.node_tree "bpy.types.GeometryNodeCustomGroup.node_tree") - [`GeometryNodeGroup.node_tree`](bpy.types.GeometryNodeGroup.md#bpy.types.GeometryNodeGroup.node_tree "bpy.types.GeometryNodeGroup.node_tree") - [`Light.node_tree`](bpy.types.Light.md#bpy.types.Light.node_tree "bpy.types.Light.node_tree") - [`Material.node_tree`](bpy.types.Material.md#bpy.types.Material.node_tree "bpy.types.Material.node_tree") - [`Node.poll`](bpy.types.Node.md#bpy.types.Node.poll "bpy.types.Node.poll") - [`Node.poll_instance`](bpy.types.Node.md#bpy.types.Node.poll_instance "bpy.types.Node.poll_instance") - [`NodeCustomGroup.node_tree`](bpy.types.NodeCustomGroup.md#bpy.types.NodeCustomGroup.node_tree "bpy.types.NodeCustomGroup.node_tree") - [`NodeGroup.node_tree`](bpy.types.NodeGroup.md#bpy.types.NodeGroup.node_tree "bpy.types.NodeGroup.node_tree") - [`NodeInternal.poll`](bpy.types.NodeInternal.md#bpy.types.NodeInternal.poll "bpy.types.NodeInternal.poll") - [`NodeInternal.poll_instance`](bpy.types.NodeInternal.md#bpy.types.NodeInternal.poll_instance "bpy.types.NodeInternal.poll_instance") | - [`NodeTree.contains_tree`](#bpy.types.NodeTree.contains_tree "bpy.types.NodeTree.contains_tree") - [`NodeTree.get_from_context`](#bpy.types.NodeTree.get_from_context "bpy.types.NodeTree.get_from_context") - [`NodeTreePath.node_tree`](bpy.types.NodeTreePath.md#bpy.types.NodeTreePath.node_tree "bpy.types.NodeTreePath.node_tree") - [`NodesModifier.node_group`](bpy.types.NodesModifier.md#bpy.types.NodesModifier.node_group "bpy.types.NodesModifier.node_group") - [`Scene.compositing_node_group`](bpy.types.Scene.md#bpy.types.Scene.compositing_node_group "bpy.types.Scene.compositing_node_group") - [`SequencerCompositorModifierData.node_group`](bpy.types.SequencerCompositorModifierData.md#bpy.types.SequencerCompositorModifierData.node_group "bpy.types.SequencerCompositorModifierData.node_group") - [`ShaderNodeCustomGroup.node_tree`](bpy.types.ShaderNodeCustomGroup.md#bpy.types.ShaderNodeCustomGroup.node_tree "bpy.types.ShaderNodeCustomGroup.node_tree") - [`ShaderNodeGroup.node_tree`](bpy.types.ShaderNodeGroup.md#bpy.types.ShaderNodeGroup.node_tree "bpy.types.ShaderNodeGroup.node_tree") - [`SpaceNodeEditor.edit_tree`](bpy.types.SpaceNodeEditor.md#bpy.types.SpaceNodeEditor.edit_tree "bpy.types.SpaceNodeEditor.edit_tree") - [`SpaceNodeEditor.node_tree`](bpy.types.SpaceNodeEditor.md#bpy.types.SpaceNodeEditor.node_tree "bpy.types.SpaceNodeEditor.node_tree") - [`SpaceNodeEditor.selected_node_group`](bpy.types.SpaceNodeEditor.md#bpy.types.SpaceNodeEditor.selected_node_group "bpy.types.SpaceNodeEditor.selected_node_group") - [`SpaceNodeEditorPath.append`](bpy.types.SpaceNodeEditorPath.md#bpy.types.SpaceNodeEditorPath.append "bpy.types.SpaceNodeEditorPath.append") - [`SpaceNodeEditorPath.start`](bpy.types.SpaceNodeEditorPath.md#bpy.types.SpaceNodeEditorPath.start "bpy.types.SpaceNodeEditorPath.start") - [`Texture.node_tree`](bpy.types.Texture.md#bpy.types.Texture.node_tree "bpy.types.Texture.node_tree") - [`TextureNodeGroup.node_tree`](bpy.types.TextureNodeGroup.md#bpy.types.TextureNodeGroup.node_tree "bpy.types.TextureNodeGroup.node_tree") - [`UILayout.template_node_link`](bpy.types.UILayout.md#bpy.types.UILayout.template_node_link "bpy.types.UILayout.template_node_link") - [`UILayout.template_node_view`](bpy.types.UILayout.md#bpy.types.UILayout.template_node_view "bpy.types.UILayout.template_node_view") - [`World.node_tree`](bpy.types.World.md#bpy.types.World.node_tree "bpy.types.World.node_tree") |
