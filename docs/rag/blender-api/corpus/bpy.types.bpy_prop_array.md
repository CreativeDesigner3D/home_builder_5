<!-- source: Blender Python API reference 5.2 / bpy.types.bpy_prop_array.html -->

<a id="bpy-prop-array"></a>

# bpy_prop_array

base classes — [`bpy_prop`](bpy.types.bpy_prop.md#bpy.types.bpy_prop "bpy.types.bpy_prop")

<a id="bpy.types.bpy_prop_array"></a>

### class bpy.types.bpy_prop_array(bpy_prop)

built-in class used for array properties.

<a id="bpy.types.bpy_prop_array.foreach_get"></a>

#### bpy.types.bpy_prop_array.foreach_get(seq)

This is a function to give fast access to array data.

**Parameters:**

**seq** (MutableSequence[Any]) – Buffer to read element values into, must match the length of this array.

<a id="bpy.types.bpy_prop_array.foreach_set"></a>

#### bpy.types.bpy_prop_array.foreach_set(seq)

This is a function to give fast access to array data.

**Parameters:**

**seq** (Sequence[Any]) – Element values to write, must match the length of this array.

Special Methods

<a id="bpy.types.bpy_prop_array.__contains__"></a>

#### bpy.types.bpy_prop_array.__contains__(item)

**Parameters:**

**item** (object) – Item to test for membership.

**Return type:**

bool

<a id="bpy.types.bpy_prop_array.__getitem__"></a>

#### bpy.types.bpy_prop_array.__getitem__(key)

**Parameters:**

**key** (int) – Index or key.

**Return type:**

float

<a id="bpy.types.bpy_prop_array.__iter__"></a>

#### bpy.types.bpy_prop_array.__iter__()

**Return type:**

[`bpy_prop_array`](#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")

<a id="bpy.types.bpy_prop_array.__len__"></a>

#### bpy.types.bpy_prop_array.__len__()

**Return type:**

int

<a id="bpy.types.bpy_prop_array.__repr__"></a>

#### bpy.types.bpy_prop_array.__repr__()

**Return type:**

str

<a id="bpy.types.bpy_prop_array.__setitem__"></a>

#### bpy.types.bpy_prop_array.__setitem__(key, value)

**Parameters:**

- **key** (int) – Index or key.
- **value** (object) – Value to assign.
