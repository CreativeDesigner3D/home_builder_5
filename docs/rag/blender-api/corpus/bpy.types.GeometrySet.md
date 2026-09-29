<!-- source: Blender Python API reference 5.2 / bpy.types.GeometrySet.html -->

<a id="geometryset"></a>

# GeometrySet

<a id="accessing-evaluated-geometry"></a>

## Accessing Evaluated Geometry

```python
import bpy

# The GeometrySet can only be retrieved from an evaluated object. So one always
# needs a depsgraph that has evaluated the object.
depsgraph = bpy.context.view_layer.depsgraph
ob = bpy.context.active_object
ob_eval = depsgraph.id_eval_get(ob)

# Get the final evaluated geometry of an object.
geometry = ob_eval.evaluated_geometry()

# Print basic information like the number of elements.
print(geometry)

# A geometry set may have a name. It can be set with the Set Geometry Name node.
print(geometry.name)

# Access "realized" geometry components.
print(geometry.mesh)
print(geometry.pointcloud)
print(geometry.curves)
print(geometry.volume)
print(geometry.grease_pencil)

# Access the mesh without final subdivision applied.
print(geometry.mesh_base)

# Accessing instances is a bit more tricky, because there is no specific
# mechanism to expose instances. Instead, two accessors are provided which
# are easy to keep working in the future even if we get a proper Instances type.

# This is a pointcloud that provides access to all the instance attributes.
# There is a point per instances. May return None if there is no instances data.
instances_pointcloud = geometry.instances_pointcloud()

if instances_pointcloud is not None:
    # This is a list containing the data that is instanced. The list may contain
    # None, objects, collections or other GeometrySets. If the geometry does not
    # have instances, the list is empty.
    references = geometry.instance_references()

    # Besides normal generic attributes, there are also two important
    # instance-specific attributes. "instance_transform" is a 4x4 matrix attribute
    # containing the transforms of each instance.
    instance_transforms = instances_pointcloud.attributes["instance_transform"]

    # ".reference_index" contains indices into the `references` list above and
    # determines what geometry each instance uses.
    reference_indices = instances_pointcloud.attributes[".reference_index"]
```

<a id="bpy.types.GeometrySet"></a>

### class bpy.types.GeometrySet

Stores potentially multiple geometry components of different types.
For example, it might contain a mesh, curves and nested instances.

<a id="bpy.types.GeometrySet.instance_references"></a>

#### bpy.types.GeometrySet.instance_references()

This returns a list of geometries that is indexed by the `.reference_index`
attribute of the pointcloud returned by
[`bpy.types.GeometrySet.instances_pointcloud()`](#bpy.types.GeometrySet.instances_pointcloud "bpy.types.GeometrySet.instances_pointcloud").
It may contain other geometry sets, objects, collections and None values.

**Return type:**

list[None | [bpy.types.Object](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | [bpy.types.Collection](bpy.types.Collection.md#bpy.types.Collection "bpy.types.Collection") | [bpy.types.GeometrySet](#bpy.types.GeometrySet "bpy.types.GeometrySet")]

<a id="bpy.types.GeometrySet.instances_pointcloud"></a>

#### bpy.types.GeometrySet.instances_pointcloud()

Get a pointcloud that encodes information about the instances of the geometry.
The returned pointcloud should not be modified.
There is a point per instance and per-instance data is stored in point attributes.
The local transforms are stored in the `instance_transform` attribute.
The data instanced by each point is referenced by the `.reference_index` attribute,
indexing into the list returned by [`bpy.types.GeometrySet.instance_references()`](#bpy.types.GeometrySet.instance_references "bpy.types.GeometrySet.instance_references").

**Return type:**

[bpy.types.PointCloud](bpy.types.PointCloud.md#bpy.types.PointCloud "bpy.types.PointCloud")

<a id="bpy.types.GeometrySet.curves"></a>

#### bpy.types.GeometrySet.curves

The curves data-block in the geometry set.

**Type:**

[`bpy.types.Curves`](bpy.types.Curves.md#bpy.types.Curves "bpy.types.Curves")

<a id="bpy.types.GeometrySet.grease_pencil"></a>

#### bpy.types.GeometrySet.grease_pencil

The Grease Pencil data-block in the geometry set.

**Type:**

[`bpy.types.GreasePencil`](bpy.types.GreasePencil.md#bpy.types.GreasePencil "bpy.types.GreasePencil")

<a id="bpy.types.GeometrySet.mesh"></a>

#### bpy.types.GeometrySet.mesh

The mesh data-block in the geometry set.

**Type:**

[`bpy.types.Mesh`](bpy.types.Mesh.md#bpy.types.Mesh "bpy.types.Mesh")

<a id="bpy.types.GeometrySet.mesh_base"></a>

#### bpy.types.GeometrySet.mesh_base

The mesh data-block in the geometry set without final subdivision.

**Type:**

[`bpy.types.Mesh`](bpy.types.Mesh.md#bpy.types.Mesh "bpy.types.Mesh")

<a id="bpy.types.GeometrySet.name"></a>

#### bpy.types.GeometrySet.name

The name of the geometry set. It can be used for debugging purposes and is not unique.

**Type:**

str

<a id="bpy.types.GeometrySet.pointcloud"></a>

#### bpy.types.GeometrySet.pointcloud

The point cloud data-block in the geometry set.

**Type:**

[`bpy.types.PointCloud`](bpy.types.PointCloud.md#bpy.types.PointCloud "bpy.types.PointCloud")

<a id="bpy.types.GeometrySet.volume"></a>

#### bpy.types.GeometrySet.volume

The volume data-block in the geometry set.

**Type:**

[`bpy.types.Volume`](bpy.types.Volume.md#bpy.types.Volume "bpy.types.Volume")

<a id="bpy.types.GeometrySet.from_evaluated_object"></a>

#### static bpy.types.GeometrySet.from_evaluated_object(evaluated_object)

Create a geometry set from the evaluated geometry of an evaluated object.
Typically, it’s more convenient to use [`bpy.types.Object.evaluated_geometry()`](bpy.types.Object.md#bpy.types.Object.evaluated_geometry "bpy.types.Object.evaluated_geometry").

**Parameters:**

**evaluated_object** ([bpy.types.Object](bpy.types.Object.md#bpy.types.Object "bpy.types.Object")) – The evaluated object to create a geometry set from.

Special Methods

<a id="bpy.types.GeometrySet.__repr__"></a>

#### bpy.types.GeometrySet.__repr__()

**Return type:**

str
