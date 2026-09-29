<!-- source: Blender Python API reference 5.2 / mathutils.kdtree.html -->

<a id="module-mathutils.kdtree"></a>

# KDTree Utilities (mathutils.kdtree)

Generic 3-dimensional kd-tree to perform spatial searches.

```python
import mathutils

# Create a KD-tree from a mesh.
from bpy import context
obj = context.object

mesh = obj.data
size = len(mesh.vertices)
kd = mathutils.kdtree.KDTree(size)

for i, v in enumerate(mesh.vertices):
    kd.insert(v.co, i)

kd.balance()

# Find the closest point to the center.
co_find = (0.0, 0.0, 0.0)
co, index, dist = kd.find(co_find)
print("Close to center:", co, index, dist)

# 3D cursor relative to the object data.
co_find = obj.matrix_world.inverted() @ context.scene.cursor.location

# Find the closest 10 points to the 3D cursor.
print("Close 10 points")
for (co, index, dist) in kd.find_n(co_find, 10):
    print("    ", co, index, dist)

# Find points within a radius of the 3D cursor.
print("Close points within 0.5 distance")
for (co, index, dist) in kd.find_range(co_find, 0.5):
    print("    ", co, index, dist)
```

<a id="mathutils.kdtree.KDTree"></a>

### class mathutils.kdtree.KDTree(size)

KDTree(size) -> new kd-tree initialized to hold up to `size` items.

**Parameters:**

**size** (int) – Maximum number of items.

> **Note:**
>
> [`KDTree.balance()`](#mathutils.kdtree.KDTree.balance "mathutils.kdtree.KDTree.balance") must have been called before using any of the `find` methods.

<a id="mathutils.kdtree.KDTree.balance"></a>

#### mathutils.kdtree.KDTree.balance()

Balance the tree.

> **Note:**
>
> This builds the entire tree, avoid calling after each insertion.

<a id="mathutils.kdtree.KDTree.find"></a>

#### mathutils.kdtree.KDTree.find(co, *, filter=None)

Find nearest point to `co`.

**Parameters:**

- **co** (Sequence[float]) – 3D coordinate.
- **filter** (Callable[[int], bool] | None) – function which takes an index and returns True for indices to include in the search.

**Returns:**

Returns (position, index, distance),
or (None, None, None) when no match is found.

**Return type:**

tuple[`Vector`, int, float] | tuple[None, None, None]

<a id="mathutils.kdtree.KDTree.find_n"></a>

#### mathutils.kdtree.KDTree.find_n(co, n)

Find nearest `n` points to `co`.

**Parameters:**

- **co** (Sequence[float]) – 3D coordinate.
- **n** (int) – Number of points to find.

**Returns:**

Returns a list of tuples (position, index, distance).

**Return type:**

list[tuple[`Vector`, int, float]]

<a id="mathutils.kdtree.KDTree.find_range"></a>

#### mathutils.kdtree.KDTree.find_range(co, radius)

Find all points within `radius` of `co`.

**Parameters:**

- **co** (Sequence[float]) – 3D coordinate.
- **radius** (float) – Maximum distance to search for points.

**Returns:**

Returns a list of tuples (position, index, distance).

**Return type:**

list[tuple[`Vector`, int, float]]

<a id="mathutils.kdtree.KDTree.insert"></a>

#### mathutils.kdtree.KDTree.insert(co, index)

Insert a point into the KDTree.

**Parameters:**

- **co** (Sequence[float]) – Point 3d position.
- **index** (int) – The index of the point (must be non-negative).
