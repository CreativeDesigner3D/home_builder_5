<!-- source: Blender Python API reference 5.2 / bpy.types.bpy_prop_collection.html -->

<a id="bpy-prop-collection"></a>

# bpy_prop_collection

base classes — [`bpy_prop`](bpy.types.bpy_prop.md#bpy.types.bpy_prop "bpy.types.bpy_prop")

<a id="bpy.types.bpy_prop_collection"></a>

### class bpy.types.bpy_prop_collection(bpy_prop)

built-in class used for all collections.

<a id="bpy.types.bpy_prop_collection.find"></a>

#### bpy.types.bpy_prop_collection.find(key)

Returns the index of a key in a collection or -1 when not found
(matches Python’s string find function of the same name).

**Parameters:**

**key** (str) – The identifier for the collection member.

**Returns:**

index of the key.

**Return type:**

int

<a id="bpy.types.bpy_prop_collection.foreach_get"></a>

#### bpy.types.bpy_prop_collection.foreach_get(attr, seq)

Fast access to a basic-type attribute within a collection.

**Parameters:**

- **attr** (str) –

  Name of the item attribute to read (for example `co`, `normal` or
  `select`). The attribute must be a basic type (bool, int or float).

  For geometry attribute types, see [`Attribute.data_type`](bpy.types.Attribute.md#bpy.types.Attribute.data_type "bpy.types.Attribute.data_type").
- **seq** (MutableSequence[bool | int | float] | buffer) – Writable sequence or buffer receiving flattened values.
  For array attributes, the length must be `len(collection) * array_length`.

Only works for ‘basic type’ properties (bool, int and float)!
Multi-dimensional arrays (like array of vectors) will be flattened into seq.

```python
import bpy

mesh = bpy.context.object.data
collection = mesh.vertices

# Allocate a flat list for the `co` property (X, Y, Z per vertex).
coords = [0.0] * len(collection) * 3

# Fast access.
collection.foreach_get("co", coords)

# Python equivalent (per-element iteration is much slower).
for i, vert in enumerate(collection):
    coords[i * 3], coords[i * 3 + 1], coords[i * 3 + 2] = vert.co
```

<a id="bpy.types.bpy_prop_collection.foreach_set"></a>

#### bpy.types.bpy_prop_collection.foreach_set(attr, seq)

Fast access to a basic-type attribute within a collection.

**Parameters:**

- **attr** (str) –

  Name of the item attribute to write (for example `co` or
  `select`). The attribute must be a basic type (bool, int or float).

  For geometry attribute types, see [`Attribute.data_type`](bpy.types.Attribute.md#bpy.types.Attribute.data_type "bpy.types.Attribute.data_type").
- **seq** (Sequence[bool | int | float] | buffer) – Sequence or buffer containing flattened values.
  For array attributes, the length must be `len(collection) * array_length`.

Only works for ‘basic type’ properties (bool, int and float)!
seq must be uni-dimensional, multi-dimensional arrays (like array of vectors) will be re-created from it.

```python
import bpy

mesh = bpy.context.object.data
collection = mesh.vertices

# Flatten all Z coordinates to zero (X, Y, Z per vertex).
coords = [0.0] * len(collection) * 3
collection.foreach_get("co", coords)
for i in range(2, len(coords), 3):
    coords[i] = 0.0

# Fast assignment.
collection.foreach_set("co", coords)

# Python equivalent (per-element iteration is much slower).
for i, vert in enumerate(collection):
    vert.co = (coords[i * 3], coords[i * 3 + 1], coords[i * 3 + 2])
```

<a id="bpy.types.bpy_prop_collection.get"></a>

#### bpy.types.bpy_prop_collection.get(key, default=None)

Returns the value of the item assigned to key or default when not found
(matches Python’s dictionary function of the same name).

**Parameters:**

- **key** (str) – The identifier for the collection member.
- **default** (Any) – Optional argument for the value to return if
  key is not found.

**Returns:**

The collection member or default.

**Return type:**

[`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.bpy_prop_collection.items"></a>

#### bpy.types.bpy_prop_collection.items()

Return the identifiers of collection members
(matching Python’s dict.items() functionality).

**Returns:**

(key, value) pairs for each member of this collection.

**Return type:**

list[tuple[str, [`bpy.types.bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")]]

<a id="bpy.types.bpy_prop_collection.keys"></a>

#### bpy.types.bpy_prop_collection.keys()

Return the identifiers of collection members
(matching Python’s dict.keys() functionality).

**Returns:**

the identifiers for each member of this collection.

**Return type:**

list[str]

<a id="bpy.types.bpy_prop_collection.values"></a>

#### bpy.types.bpy_prop_collection.values()

Return the values of collection
(matching Python’s dict.values() functionality).

**Returns:**

The members of this collection.

**Return type:**

list[[`bpy.types.bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct") | None]

Special Methods

<a id="bpy.types.bpy_prop_collection.__contains__"></a>

#### bpy.types.bpy_prop_collection.__contains__(item)

**Parameters:**

**item** (object) – Item to test for membership.

**Return type:**

bool

<a id="bpy.types.bpy_prop_collection.__getitem__"></a>

#### bpy.types.bpy_prop_collection.__getitem__(key)

**Parameters:**

**key** (int) – Index or key.

**Return type:**

[`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.bpy_prop_collection.__iter__"></a>

#### bpy.types.bpy_prop_collection.__iter__()

**Return type:**

typing.Iterator[[`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")]

<a id="bpy.types.bpy_prop_collection.__len__"></a>

#### bpy.types.bpy_prop_collection.__len__()

**Return type:**

int

<a id="bpy.types.bpy_prop_collection.__setitem__"></a>

#### bpy.types.bpy_prop_collection.__setitem__(key, value)

**Parameters:**

- **key** (int) – Index or key.
- **value** (object) – Value to assign.
