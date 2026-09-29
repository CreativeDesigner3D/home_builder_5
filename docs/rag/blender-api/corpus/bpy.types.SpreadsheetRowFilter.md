<!-- source: Blender Python API reference 5.2 / bpy.types.SpreadsheetRowFilter.html -->

<a id="spreadsheetrowfilter-bpy-struct"></a>

# SpreadsheetRowFilter(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.SpreadsheetRowFilter"></a>

### class bpy.types.SpreadsheetRowFilter(bpy_struct)

<a id="bpy.types.SpreadsheetRowFilter.column_name"></a>

#### bpy.types.SpreadsheetRowFilter.column_name

(default “”, never None)

**Type:**

str

<a id="bpy.types.SpreadsheetRowFilter.enabled"></a>

#### bpy.types.SpreadsheetRowFilter.enabled

(default False)

**Type:**

bool

<a id="bpy.types.SpreadsheetRowFilter.operation"></a>

#### bpy.types.SpreadsheetRowFilter.operation

(default `'EQUAL'`)

**Type:**

Literal[‘EQUAL’, ‘GREATER’, ‘LESS’]

<a id="bpy.types.SpreadsheetRowFilter.show_expanded"></a>

#### bpy.types.SpreadsheetRowFilter.show_expanded

(default False)

**Type:**

bool

<a id="bpy.types.SpreadsheetRowFilter.threshold"></a>

#### bpy.types.SpreadsheetRowFilter.threshold

How close float values need to be to be equal (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.SpreadsheetRowFilter.value_boolean"></a>

#### bpy.types.SpreadsheetRowFilter.value_boolean

(default False)

**Type:**

bool

<a id="bpy.types.SpreadsheetRowFilter.value_color"></a>

#### bpy.types.SpreadsheetRowFilter.value_color

(array of 4 items, in [-inf, inf], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.SpreadsheetRowFilter.value_float"></a>

#### bpy.types.SpreadsheetRowFilter.value_float

(in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.SpreadsheetRowFilter.value_float2"></a>

#### bpy.types.SpreadsheetRowFilter.value_float2

(array of 2 items, in [-inf, inf], default (0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.SpreadsheetRowFilter.value_float3"></a>

#### bpy.types.SpreadsheetRowFilter.value_float3

(array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.SpreadsheetRowFilter.value_float4"></a>

#### bpy.types.SpreadsheetRowFilter.value_float4

(array of 4 items, in [-inf, inf], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.SpreadsheetRowFilter.value_int"></a>

#### bpy.types.SpreadsheetRowFilter.value_int

(in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.SpreadsheetRowFilter.value_int2"></a>

#### bpy.types.SpreadsheetRowFilter.value_int2

(array of 2 items, in [-inf, inf], default (0, 0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[int]

<a id="bpy.types.SpreadsheetRowFilter.value_int3"></a>

#### bpy.types.SpreadsheetRowFilter.value_int3

(array of 3 items, in [-inf, inf], default (0, 0, 0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[int]

<a id="bpy.types.SpreadsheetRowFilter.value_int8"></a>

#### bpy.types.SpreadsheetRowFilter.value_int8

(in [-128, 127], default 0)

**Type:**

int

<a id="bpy.types.SpreadsheetRowFilter.value_string"></a>

#### bpy.types.SpreadsheetRowFilter.value_string

(default “”, never None)

**Type:**

str

<a id="bpy.types.SpreadsheetRowFilter.bl_rna_get_subclass"></a>

#### classmethod bpy.types.SpreadsheetRowFilter.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.SpreadsheetRowFilter.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.SpreadsheetRowFilter.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`SpaceSpreadsheet.row_filters`](bpy.types.SpaceSpreadsheet.md#bpy.types.SpaceSpreadsheet.row_filters "bpy.types.SpaceSpreadsheet.row_filters") |  |
