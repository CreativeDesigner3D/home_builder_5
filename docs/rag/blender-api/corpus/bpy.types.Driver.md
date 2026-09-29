<!-- source: Blender Python API reference 5.2 / bpy.types.Driver.html -->

<a id="driver-bpy-struct"></a>

# Driver(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.Driver"></a>

### class bpy.types.Driver(bpy_struct)

Driver for the value of a setting based on an external value

<a id="bpy.types.Driver.expression"></a>

#### bpy.types.Driver.expression

Expression to use for Scripted Expression (default “”, never None)

**Type:**

str

<a id="bpy.types.Driver.is_simple_expression"></a>

#### bpy.types.Driver.is_simple_expression

The scripted expression can be evaluated without using the full Python interpreter (default False, readonly)

**Type:**

bool

<a id="bpy.types.Driver.is_valid"></a>

#### bpy.types.Driver.is_valid

Driver could not be evaluated in past, so should be skipped (default True)

**Type:**

bool

<a id="bpy.types.Driver.type"></a>

#### bpy.types.Driver.type

Driver type (default `'AVERAGE'`)

**Type:**

Literal[‘AVERAGE’, ‘SUM’, ‘SCRIPTED’, ‘MIN’, ‘MAX’]

<a id="bpy.types.Driver.use_self"></a>

#### bpy.types.Driver.use_self

Include a ‘self’ variable in the name-space, so drivers can easily reference the data being modified (object, bone, etc…) (default False)

**Type:**

bool

<a id="bpy.types.Driver.variables"></a>

#### bpy.types.Driver.variables

Properties acting as inputs for this driver (default None, readonly)

**Type:**

[`ChannelDriverVariables`](bpy.types.ChannelDriverVariables.md#bpy.types.ChannelDriverVariables "bpy.types.ChannelDriverVariables")[[`DriverVariable`](bpy.types.DriverVariable.md#bpy.types.DriverVariable "bpy.types.DriverVariable")]

<a id="bpy.types.Driver.bl_rna_get_subclass"></a>

#### classmethod bpy.types.Driver.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.Driver.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.Driver.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([type](#bpy.types.Driver.type "bpy.types.Driver.type") | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

[type](#bpy.types.Driver.type "bpy.types.Driver.type")

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
| - [`FCurve.driver`](bpy.types.FCurve.md#bpy.types.FCurve.driver "bpy.types.FCurve.driver") |  |
