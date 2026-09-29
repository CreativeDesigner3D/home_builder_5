<!-- source: Blender Python API reference 5.2 / bpy.types.PropertyGroupItem.html -->

<a id="propertygroupitem-bpy-struct"></a>

# PropertyGroupItem(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.PropertyGroupItem"></a>

### class bpy.types.PropertyGroupItem(bpy_struct)

Property that stores arbitrary, user defined properties

<a id="bpy.types.PropertyGroupItem.bool"></a>

#### bpy.types.PropertyGroupItem.bool

(default False)

**Type:**

[bool](#bpy.types.PropertyGroupItem.bool "bpy.types.PropertyGroupItem.bool")

<a id="bpy.types.PropertyGroupItem.bool_array"></a>

#### bpy.types.PropertyGroupItem.bool_array

(array of 1 items, default (False,))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[bool]

<a id="bpy.types.PropertyGroupItem.collection"></a>

#### bpy.types.PropertyGroupItem.collection

(default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`PropertyGroup`](bpy.types.PropertyGroup.md#bpy.types.PropertyGroup "bpy.types.PropertyGroup")]

<a id="bpy.types.PropertyGroupItem.double"></a>

#### bpy.types.PropertyGroupItem.double

(in [-inf, inf], default 0.0)

**Type:**

[float](#bpy.types.PropertyGroupItem.float "bpy.types.PropertyGroupItem.float")

<a id="bpy.types.PropertyGroupItem.double_array"></a>

#### bpy.types.PropertyGroupItem.double_array

(array of 1 items, in [-inf, inf], default (0.0,))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.PropertyGroupItem.enum"></a>

#### bpy.types.PropertyGroupItem.enum

(default `'DEFAULT'`)

**Type:**

Literal[‘DEFAULT’]

<a id="bpy.types.PropertyGroupItem.float"></a>

#### bpy.types.PropertyGroupItem.float

(in [-inf, inf], default 0.0)

**Type:**

[float](#bpy.types.PropertyGroupItem.float "bpy.types.PropertyGroupItem.float")

<a id="bpy.types.PropertyGroupItem.float_array"></a>

#### bpy.types.PropertyGroupItem.float_array

(array of 1 items, in [-inf, inf], default (0.0,))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.PropertyGroupItem.group"></a>

#### bpy.types.PropertyGroupItem.group

(readonly)

**Type:**

[`PropertyGroup`](bpy.types.PropertyGroup.md#bpy.types.PropertyGroup "bpy.types.PropertyGroup") | None

<a id="bpy.types.PropertyGroupItem.id"></a>

#### bpy.types.PropertyGroupItem.id

**Type:**

[`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID") | None

<a id="bpy.types.PropertyGroupItem.idp_array"></a>

#### bpy.types.PropertyGroupItem.idp_array

(default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`PropertyGroup`](bpy.types.PropertyGroup.md#bpy.types.PropertyGroup "bpy.types.PropertyGroup")]

<a id="bpy.types.PropertyGroupItem.int"></a>

#### bpy.types.PropertyGroupItem.int

(in [-inf, inf], default 0)

**Type:**

[int](#bpy.types.PropertyGroupItem.int "bpy.types.PropertyGroupItem.int")

<a id="bpy.types.PropertyGroupItem.int_array"></a>

#### bpy.types.PropertyGroupItem.int_array

(array of 1 items, in [-inf, inf], default (0,))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[int]

<a id="bpy.types.PropertyGroupItem.string"></a>

#### bpy.types.PropertyGroupItem.string

(default “”, never None)

**Type:**

str

<a id="bpy.types.PropertyGroupItem.bl_rna_get_subclass"></a>

#### classmethod bpy.types.PropertyGroupItem.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.PropertyGroupItem.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.PropertyGroupItem.bl_rna_get_subclass_py(id, default=None, /)

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
