<!-- source: Blender Python API reference 5.2 / bpy.types.bpy_prop.html -->

<a id="bpy-prop"></a>

# bpy_prop

<a id="bpy.types.bpy_prop"></a>

### class bpy.types.bpy_prop

built-in base class for all property classes.

<a id="bpy.types.bpy_prop.as_bytes"></a>

#### bpy.types.bpy_prop.as_bytes()

Returns this string property as a byte rather than a Python string.

**Returns:**

The string as bytes.

**Return type:**

bytes

<a id="bpy.types.bpy_prop.path_from_id"></a>

#### bpy.types.bpy_prop.path_from_id()

Returns the data path from the ID to this property (string).

**Returns:**

The path from [`bpy.types.bpy_struct.id_data`](bpy.types.bpy_struct.md#bpy.types.bpy_struct.id_data "bpy.types.bpy_struct.id_data") to this property.

**Return type:**

str

<a id="bpy.types.bpy_prop.path_from_module"></a>

#### bpy.types.bpy_prop.path_from_module()

Returns the full data path to this struct (as a string) from the bpy module.

**Returns:**

The full path to the data.

**Return type:**

str

**Raises:**

**ValueError** –

if the input data cannot be converted into a full data path.

> **Note:**
>
> Even if all input data is correct, this function might
> error out because Blender cannot derive a valid path.
> The incomplete path will be printed in the error message.

<a id="bpy.types.bpy_prop.update"></a>

#### bpy.types.bpy_prop.update()

Execute the properties update callback.

> **Note:**
>
> This is called when assigning a property,
> however in rare cases it’s useful to call explicitly.

<a id="bpy.types.bpy_prop.data"></a>

#### bpy.types.bpy_prop.data

The data this property is using, (readonly)

**Type:**

[`bpy.types.bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.bpy_prop.id_data"></a>

#### bpy.types.bpy_prop.id_data

The [`bpy.types.ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID") object this data-block is from or None, (not available for all data types) (readonly)

**Type:**

[`bpy.types.ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")

<a id="bpy.types.bpy_prop.rna_type"></a>

#### bpy.types.bpy_prop.rna_type

The property type for introspection.

**Type:**

[`bpy.types.Property`](bpy.types.Property.md#bpy.types.Property "bpy.types.Property")

Special Methods

<a id="bpy.types.bpy_prop.__eq__"></a>

#### bpy.types.bpy_prop.__eq__(other)

**Parameters:**

**other** (object) – The other operand.

**Return type:**

bool

<a id="bpy.types.bpy_prop.__ge__"></a>

#### bpy.types.bpy_prop.__ge__(other)

**Parameters:**

**other** (Self) – The other operand.

**Return type:**

bool

<a id="bpy.types.bpy_prop.__gt__"></a>

#### bpy.types.bpy_prop.__gt__(other)

**Parameters:**

**other** (Self) – The other operand.

**Return type:**

bool

<a id="bpy.types.bpy_prop.__hash__"></a>

#### bpy.types.bpy_prop.__hash__()

**Return type:**

int

<a id="bpy.types.bpy_prop.__le__"></a>

#### bpy.types.bpy_prop.__le__(other)

**Parameters:**

**other** (Self) – The other operand.

**Return type:**

bool

<a id="bpy.types.bpy_prop.__lt__"></a>

#### bpy.types.bpy_prop.__lt__(other)

**Parameters:**

**other** (Self) – The other operand.

**Return type:**

bool

<a id="bpy.types.bpy_prop.__ne__"></a>

#### bpy.types.bpy_prop.__ne__(other)

**Parameters:**

**other** (object) – The other operand.

**Return type:**

bool

<a id="bpy.types.bpy_prop.__repr__"></a>

#### bpy.types.bpy_prop.__repr__()

**Return type:**

str

<a id="bpy.types.bpy_prop.__str__"></a>

#### bpy.types.bpy_prop.__str__()

**Return type:**

str
