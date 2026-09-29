<!-- source: Blender Python API reference 5.2 / idprop.types.html -->

<a id="module-idprop.types"></a>

# ID Property Access (idprop.types)

<a id="idprop.types.IDPropertyArray"></a>

### class idprop.types.IDPropertyArray

An array of values with a fixed type, supporting indexing and slicing.

<a id="idprop.types.IDPropertyArray.to_list"></a>

#### idprop.types.IDPropertyArray.to_list()

Return the array as a list.

**Returns:**

The array as a list.

**Return type:**

list[int] | list[float] | list[bool]

<a id="idprop.types.IDPropertyArray.typecode"></a>

#### idprop.types.IDPropertyArray.typecode

The type of the data in the array {‘f’: float (32-bit), ‘d’: double (64-bit), ‘i’: int, ‘b’: bool}. Both ‘f’ and ‘d’ use Python’s `float` type but differ in storage precision.

**Type:**

Literal[‘f’, ‘d’, ‘i’, ‘b’]

Special Methods

<a id="idprop.types.IDPropertyArray.__getitem__"></a>

#### idprop.types.IDPropertyArray.__getitem__(key)

**Parameters:**

**key** (int) – Index or key.

**Return type:**

float | int | bool

#### __getitem__(key)

**Parameters:**

**key** (slice) – Index or key.

**Return type:**

list[float] | list[int] | list[bool]

<a id="idprop.types.IDPropertyArray.__len__"></a>

#### idprop.types.IDPropertyArray.__len__()

**Return type:**

int

<a id="idprop.types.IDPropertyArray.__repr__"></a>

#### idprop.types.IDPropertyArray.__repr__()

**Return type:**

str

<a id="idprop.types.IDPropertyArray.__setitem__"></a>

#### idprop.types.IDPropertyArray.__setitem__(key, value)

**Parameters:**

- **key** (int) – Index.
- **value** (float | int | bool) – Value to assign.

<a id="idprop.types.IDPropertyGroup"></a>

### class idprop.types.IDPropertyGroup

A dictionary-like group of ID properties, supporting key access, iteration, and membership testing.

> **Note:**
>
> Only supports a maximum of 1024 levels of nesting.

<a id="idprop.types.IDPropertyGroup.clear"></a>

#### idprop.types.IDPropertyGroup.clear()

Clear all members from this group.

<a id="idprop.types.IDPropertyGroup.get"></a>

#### idprop.types.IDPropertyGroup.get(key, default=None)

Return the value for key, if it exists, else default.

**Parameters:**

- **key** (str) – The key to look up.
- **default** (Any) – Value to return if key is not found.

**Returns:**

The value for the key, or default if not found.

**Return type:**

Any

<a id="idprop.types.IDPropertyGroup.items"></a>

#### idprop.types.IDPropertyGroup.items()

Return a view of the items in the group, behaves like dictionary method items.

**Returns:**

A view of the items.

**Return type:**

[`IDPropertyGroupViewItems`](#idprop.types.IDPropertyGroupViewItems "idprop.types.IDPropertyGroupViewItems")

<a id="idprop.types.IDPropertyGroup.keys"></a>

#### idprop.types.IDPropertyGroup.keys()

Return a view of the keys in the group.

**Returns:**

A view of the keys.

**Return type:**

[`IDPropertyGroupViewKeys`](#idprop.types.IDPropertyGroupViewKeys "idprop.types.IDPropertyGroupViewKeys")

<a id="idprop.types.IDPropertyGroup.pop"></a>

#### idprop.types.IDPropertyGroup.pop(key, default)

Remove an item from the group, returning a Python representation.

**Raises:**

**KeyError** – When the item doesn’t exist and no default is given.

**Parameters:**

- **key** (str) – Name of item to remove.
- **default** (Any) – Value to return when key isn’t found (optional, a `KeyError` is raised when omitted and the key is not found).

**Returns:**

A Python representation of the removed item, or default.

**Return type:**

Any

<a id="idprop.types.IDPropertyGroup.to_dict"></a>

#### idprop.types.IDPropertyGroup.to_dict()

Return a purely Python version of the group.

**Returns:**

A dictionary representation of the group.

**Return type:**

dict[str, Any]

<a id="idprop.types.IDPropertyGroup.update"></a>

#### idprop.types.IDPropertyGroup.update(other)

Update key-value pairs from *other*, overwriting existing keys.

> **Note:**
>
> Unlike `dict.update()`, keyword arguments are not supported.

**Parameters:**

**other** ([`IDPropertyGroup`](#idprop.types.IDPropertyGroup "idprop.types.IDPropertyGroup") | dict[str, Any]) – Updates the values in the group with this.

<a id="idprop.types.IDPropertyGroup.values"></a>

#### idprop.types.IDPropertyGroup.values()

Return the values associated with this group.

**Returns:**

A view of the values.

**Return type:**

[`IDPropertyGroupViewValues`](#idprop.types.IDPropertyGroupViewValues "idprop.types.IDPropertyGroupViewValues")

<a id="idprop.types.IDPropertyGroup.name"></a>

#### idprop.types.IDPropertyGroup.name

The name of this Group.

**Type:**

str

Special Methods

<a id="idprop.types.IDPropertyGroup.__contains__"></a>

#### idprop.types.IDPropertyGroup.__contains__(item)

**Parameters:**

**item** (object) – Item to test for membership.

**Return type:**

bool

<a id="idprop.types.IDPropertyGroup.__getitem__"></a>

#### idprop.types.IDPropertyGroup.__getitem__(key)

**Parameters:**

**key** (str) – Property name.

**Return type:**

Any

<a id="idprop.types.IDPropertyGroup.__hash__"></a>

#### idprop.types.IDPropertyGroup.__hash__()

**Return type:**

int

<a id="idprop.types.IDPropertyGroup.__iter__"></a>

#### idprop.types.IDPropertyGroup.__iter__()

**Return type:**

[`IDPropertyGroupIterKeys`](#idprop.types.IDPropertyGroupIterKeys "idprop.types.IDPropertyGroupIterKeys")

<a id="idprop.types.IDPropertyGroup.__len__"></a>

#### idprop.types.IDPropertyGroup.__len__()

**Return type:**

int

<a id="idprop.types.IDPropertyGroup.__repr__"></a>

#### idprop.types.IDPropertyGroup.__repr__()

**Return type:**

str

<a id="idprop.types.IDPropertyGroup.__setitem__"></a>

#### idprop.types.IDPropertyGroup.__setitem__(key, value)

**Parameters:**

- **key** (str) – Property name.
- **value** (Any) – Value to assign.

<a id="idprop.types.IDPropertyGroupIterItems"></a>

### class idprop.types.IDPropertyGroupIterItems

Iterator over [`IDPropertyGroup`](#idprop.types.IDPropertyGroup "idprop.types.IDPropertyGroup") items (key/value pairs).

Special Methods

<a id="idprop.types.IDPropertyGroupIterItems.__eq__"></a>

#### idprop.types.IDPropertyGroupIterItems.__eq__(other)

**Parameters:**

**other** (object) – The other operand.

**Return type:**

bool

<a id="idprop.types.IDPropertyGroupIterItems.__hash__"></a>

#### idprop.types.IDPropertyGroupIterItems.__hash__()

**Return type:**

int

<a id="idprop.types.IDPropertyGroupIterItems.__iter__"></a>

#### idprop.types.IDPropertyGroupIterItems.__iter__()

**Return type:**

[`IDPropertyGroupIterItems`](#idprop.types.IDPropertyGroupIterItems "idprop.types.IDPropertyGroupIterItems")

<a id="idprop.types.IDPropertyGroupIterItems.__ne__"></a>

#### idprop.types.IDPropertyGroupIterItems.__ne__(other)

**Parameters:**

**other** (object) – The other operand.

**Return type:**

bool

<a id="idprop.types.IDPropertyGroupIterItems.__next__"></a>

#### idprop.types.IDPropertyGroupIterItems.__next__()

**Return type:**

tuple[str, Any]

<a id="idprop.types.IDPropertyGroupIterItems.__repr__"></a>

#### idprop.types.IDPropertyGroupIterItems.__repr__()

**Return type:**

str

<a id="idprop.types.IDPropertyGroupIterItems.__str__"></a>

#### idprop.types.IDPropertyGroupIterItems.__str__()

**Return type:**

str

<a id="idprop.types.IDPropertyGroupIterKeys"></a>

### class idprop.types.IDPropertyGroupIterKeys

Iterator over [`IDPropertyGroup`](#idprop.types.IDPropertyGroup "idprop.types.IDPropertyGroup") keys.

Special Methods

<a id="idprop.types.IDPropertyGroupIterKeys.__eq__"></a>

#### idprop.types.IDPropertyGroupIterKeys.__eq__(other)

**Parameters:**

**other** (object) – The other operand.

**Return type:**

bool

<a id="idprop.types.IDPropertyGroupIterKeys.__hash__"></a>

#### idprop.types.IDPropertyGroupIterKeys.__hash__()

**Return type:**

int

<a id="idprop.types.IDPropertyGroupIterKeys.__iter__"></a>

#### idprop.types.IDPropertyGroupIterKeys.__iter__()

**Return type:**

[`IDPropertyGroupIterKeys`](#idprop.types.IDPropertyGroupIterKeys "idprop.types.IDPropertyGroupIterKeys")

<a id="idprop.types.IDPropertyGroupIterKeys.__ne__"></a>

#### idprop.types.IDPropertyGroupIterKeys.__ne__(other)

**Parameters:**

**other** (object) – The other operand.

**Return type:**

bool

<a id="idprop.types.IDPropertyGroupIterKeys.__next__"></a>

#### idprop.types.IDPropertyGroupIterKeys.__next__()

**Return type:**

str

<a id="idprop.types.IDPropertyGroupIterKeys.__repr__"></a>

#### idprop.types.IDPropertyGroupIterKeys.__repr__()

**Return type:**

str

<a id="idprop.types.IDPropertyGroupIterKeys.__str__"></a>

#### idprop.types.IDPropertyGroupIterKeys.__str__()

**Return type:**

str

<a id="idprop.types.IDPropertyGroupIterValues"></a>

### class idprop.types.IDPropertyGroupIterValues

Iterator over [`IDPropertyGroup`](#idprop.types.IDPropertyGroup "idprop.types.IDPropertyGroup") values.

Special Methods

<a id="idprop.types.IDPropertyGroupIterValues.__eq__"></a>

#### idprop.types.IDPropertyGroupIterValues.__eq__(other)

**Parameters:**

**other** (object) – The other operand.

**Return type:**

bool

<a id="idprop.types.IDPropertyGroupIterValues.__hash__"></a>

#### idprop.types.IDPropertyGroupIterValues.__hash__()

**Return type:**

int

<a id="idprop.types.IDPropertyGroupIterValues.__iter__"></a>

#### idprop.types.IDPropertyGroupIterValues.__iter__()

**Return type:**

[`IDPropertyGroupIterValues`](#idprop.types.IDPropertyGroupIterValues "idprop.types.IDPropertyGroupIterValues")

<a id="idprop.types.IDPropertyGroupIterValues.__ne__"></a>

#### idprop.types.IDPropertyGroupIterValues.__ne__(other)

**Parameters:**

**other** (object) – The other operand.

**Return type:**

bool

<a id="idprop.types.IDPropertyGroupIterValues.__next__"></a>

#### idprop.types.IDPropertyGroupIterValues.__next__()

**Return type:**

Any

<a id="idprop.types.IDPropertyGroupIterValues.__repr__"></a>

#### idprop.types.IDPropertyGroupIterValues.__repr__()

**Return type:**

str

<a id="idprop.types.IDPropertyGroupIterValues.__str__"></a>

#### idprop.types.IDPropertyGroupIterValues.__str__()

**Return type:**

str

<a id="idprop.types.IDPropertyGroupViewItems"></a>

### class idprop.types.IDPropertyGroupViewItems

A view of [`IDPropertyGroup`](#idprop.types.IDPropertyGroup "idprop.types.IDPropertyGroup") items as key/value pairs (supports `len()`, `in`, iteration, and `reversed()`).

Special Methods

<a id="idprop.types.IDPropertyGroupViewItems.__contains__"></a>

#### idprop.types.IDPropertyGroupViewItems.__contains__(item)

**Parameters:**

**item** (object) – Item to test for membership.

**Return type:**

bool

<a id="idprop.types.IDPropertyGroupViewItems.__eq__"></a>

#### idprop.types.IDPropertyGroupViewItems.__eq__(other)

**Parameters:**

**other** (object) – The other operand.

**Return type:**

bool

<a id="idprop.types.IDPropertyGroupViewItems.__hash__"></a>

#### idprop.types.IDPropertyGroupViewItems.__hash__()

**Return type:**

int

<a id="idprop.types.IDPropertyGroupViewItems.__iter__"></a>

#### idprop.types.IDPropertyGroupViewItems.__iter__()

**Return type:**

[`IDPropertyGroupIterItems`](#idprop.types.IDPropertyGroupIterItems "idprop.types.IDPropertyGroupIterItems")

<a id="idprop.types.IDPropertyGroupViewItems.__len__"></a>

#### idprop.types.IDPropertyGroupViewItems.__len__()

**Return type:**

int

<a id="idprop.types.IDPropertyGroupViewItems.__ne__"></a>

#### idprop.types.IDPropertyGroupViewItems.__ne__(other)

**Parameters:**

**other** (object) – The other operand.

**Return type:**

bool

<a id="idprop.types.IDPropertyGroupViewItems.__repr__"></a>

#### idprop.types.IDPropertyGroupViewItems.__repr__()

**Return type:**

str

<a id="idprop.types.IDPropertyGroupViewItems.__str__"></a>

#### idprop.types.IDPropertyGroupViewItems.__str__()

**Return type:**

str

<a id="idprop.types.IDPropertyGroupViewKeys"></a>

### class idprop.types.IDPropertyGroupViewKeys

A view of [`IDPropertyGroup`](#idprop.types.IDPropertyGroup "idprop.types.IDPropertyGroup") keys (supports `len()`, `in`, iteration, and `reversed()`).

Special Methods

<a id="idprop.types.IDPropertyGroupViewKeys.__contains__"></a>

#### idprop.types.IDPropertyGroupViewKeys.__contains__(item)

**Parameters:**

**item** (object) – Item to test for membership.

**Return type:**

bool

<a id="idprop.types.IDPropertyGroupViewKeys.__eq__"></a>

#### idprop.types.IDPropertyGroupViewKeys.__eq__(other)

**Parameters:**

**other** (object) – The other operand.

**Return type:**

bool

<a id="idprop.types.IDPropertyGroupViewKeys.__hash__"></a>

#### idprop.types.IDPropertyGroupViewKeys.__hash__()

**Return type:**

int

<a id="idprop.types.IDPropertyGroupViewKeys.__iter__"></a>

#### idprop.types.IDPropertyGroupViewKeys.__iter__()

**Return type:**

[`IDPropertyGroupIterKeys`](#idprop.types.IDPropertyGroupIterKeys "idprop.types.IDPropertyGroupIterKeys")

<a id="idprop.types.IDPropertyGroupViewKeys.__len__"></a>

#### idprop.types.IDPropertyGroupViewKeys.__len__()

**Return type:**

int

<a id="idprop.types.IDPropertyGroupViewKeys.__ne__"></a>

#### idprop.types.IDPropertyGroupViewKeys.__ne__(other)

**Parameters:**

**other** (object) – The other operand.

**Return type:**

bool

<a id="idprop.types.IDPropertyGroupViewKeys.__repr__"></a>

#### idprop.types.IDPropertyGroupViewKeys.__repr__()

**Return type:**

str

<a id="idprop.types.IDPropertyGroupViewKeys.__str__"></a>

#### idprop.types.IDPropertyGroupViewKeys.__str__()

**Return type:**

str

<a id="idprop.types.IDPropertyGroupViewValues"></a>

### class idprop.types.IDPropertyGroupViewValues

A view of [`IDPropertyGroup`](#idprop.types.IDPropertyGroup "idprop.types.IDPropertyGroup") values (supports `len()`, `in`, iteration, and `reversed()`).

Special Methods

<a id="idprop.types.IDPropertyGroupViewValues.__contains__"></a>

#### idprop.types.IDPropertyGroupViewValues.__contains__(item)

**Parameters:**

**item** (object) – Item to test for membership.

**Return type:**

bool

<a id="idprop.types.IDPropertyGroupViewValues.__eq__"></a>

#### idprop.types.IDPropertyGroupViewValues.__eq__(other)

**Parameters:**

**other** (object) – The other operand.

**Return type:**

bool

<a id="idprop.types.IDPropertyGroupViewValues.__hash__"></a>

#### idprop.types.IDPropertyGroupViewValues.__hash__()

**Return type:**

int

<a id="idprop.types.IDPropertyGroupViewValues.__iter__"></a>

#### idprop.types.IDPropertyGroupViewValues.__iter__()

**Return type:**

[`IDPropertyGroupIterValues`](#idprop.types.IDPropertyGroupIterValues "idprop.types.IDPropertyGroupIterValues")

<a id="idprop.types.IDPropertyGroupViewValues.__len__"></a>

#### idprop.types.IDPropertyGroupViewValues.__len__()

**Return type:**

int

<a id="idprop.types.IDPropertyGroupViewValues.__ne__"></a>

#### idprop.types.IDPropertyGroupViewValues.__ne__(other)

**Parameters:**

**other** (object) – The other operand.

**Return type:**

bool

<a id="idprop.types.IDPropertyGroupViewValues.__repr__"></a>

#### idprop.types.IDPropertyGroupViewValues.__repr__()

**Return type:**

str

<a id="idprop.types.IDPropertyGroupViewValues.__str__"></a>

#### idprop.types.IDPropertyGroupViewValues.__str__()

**Return type:**

str
