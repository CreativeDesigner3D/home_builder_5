<!-- source: Blender Python API reference 5.2 / bpy.types.InlineShaderNodes.html -->

<a id="inlineshadernodes"></a>

# InlineShaderNodes

<a id="inline-shader-nodes"></a>

## Inline Shader Nodes

```python
import bpy

# The materials should be retrieved from the evaluated object to make sure that
# e.g. edits of Geometry Nodes are applied.
depsgraph = bpy.context.view_layer.depsgraph
ob = bpy.context.active_object
ob_eval = depsgraph.id_eval_get(ob)
material_eval = ob_eval.material_slots[0].material

# Compute the inlined shader nodes.
# Important: Do not loose the reference to this object while accessing the inlined
#   node tree. Otherwise there will be a crash due to a dangling pointer.
inline_shader_nodes = material_eval.inline_shader_nodes()

# Get the actual inlined `bpy.types.NodeTree`.
tree = inline_shader_nodes.node_tree

for node in tree.nodes:
    print(node.name)
```

<a id="bpy.types.InlineShaderNodes"></a>

### class bpy.types.InlineShaderNodes

An inlined shader node tree.

<a id="bpy.types.InlineShaderNodes.node_tree"></a>

#### bpy.types.InlineShaderNodes.node_tree

The inlined node tree.

**Type:**

[`bpy.types.NodeTree`](bpy.types.NodeTree.md#bpy.types.NodeTree "bpy.types.NodeTree")

<a id="bpy.types.InlineShaderNodes.from_light"></a>

#### static bpy.types.InlineShaderNodes.from_light(light)

Create an inlined shader node tree from a light.

**Parameters:**

**light** ([bpy.types.Light](bpy.types.Light.md#bpy.types.Light "bpy.types.Light")) – The light to online the node tree of.

<a id="bpy.types.InlineShaderNodes.from_material"></a>

#### static bpy.types.InlineShaderNodes.from_material(material)

Create an inlined shader node tree from a material.

**Parameters:**

**material** ([bpy.types.Material](bpy.types.Material.md#bpy.types.Material "bpy.types.Material")) – The material to inline the node tree of.

<a id="bpy.types.InlineShaderNodes.from_world"></a>

#### static bpy.types.InlineShaderNodes.from_world(world)

Create an inlined shader node tree from a world.

**Parameters:**

**world** ([bpy.types.World](bpy.types.World.md#bpy.types.World "bpy.types.World")) – The world to inline the node tree of.
