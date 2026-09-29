<!-- source: Blender Python API reference 5.2 / bpy.types.Function.html -->

<a id="function-bpy-struct"></a>

# Function(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.Function"></a>

### class bpy.types.Function(bpy_struct)

RNA function definition

<a id="bpy.types.Function.description"></a>

#### bpy.types.Function.description

Description of the Function’s purpose (default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.Function.identifier"></a>

#### bpy.types.Function.identifier

Unique name used in the code and scripting (default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.Function.is_registered"></a>

#### bpy.types.Function.is_registered

Function is registered as callback as part of type registration (default False, readonly)

**Type:**

bool

<a id="bpy.types.Function.is_registered_optional"></a>

#### bpy.types.Function.is_registered_optional

Function is optionally registered as callback part of type registration (default False, readonly)

**Type:**

bool

<a id="bpy.types.Function.parameters"></a>

#### bpy.types.Function.parameters

Parameters for the function (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`Property`](bpy.types.Property.md#bpy.types.Property "bpy.types.Property")]

<a id="bpy.types.Function.use_self"></a>

#### bpy.types.Function.use_self

Function does not pass itself as an argument (becomes a static method in Python) (default False, readonly)

**Type:**

bool

<a id="bpy.types.Function.use_self_type"></a>

#### bpy.types.Function.use_self_type

Function passes itself type as an argument (becomes a class method in Python if use_self is false) (default False, readonly)

**Type:**

bool

<a id="bpy.types.Function.bl_rna_get_subclass"></a>

#### classmethod bpy.types.Function.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.Function.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.Function.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Struct.functions`](bpy.types.Struct.md#bpy.types.Struct.functions "bpy.types.Struct.functions") |  |
