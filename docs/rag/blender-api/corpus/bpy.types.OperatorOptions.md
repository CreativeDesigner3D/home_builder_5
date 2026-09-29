<!-- source: Blender Python API reference 5.2 / bpy.types.OperatorOptions.html -->

<a id="operatoroptions-bpy-struct"></a>

# OperatorOptions(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.OperatorOptions"></a>

### class bpy.types.OperatorOptions(bpy_struct)

Runtime options

<a id="bpy.types.OperatorOptions.is_grab_cursor"></a>

#### bpy.types.OperatorOptions.is_grab_cursor

True when the cursor is grabbed (default False, readonly)

**Type:**

bool

<a id="bpy.types.OperatorOptions.is_invoke"></a>

#### bpy.types.OperatorOptions.is_invoke

True when invoked (even if only the execute callbacks available) (default False, readonly)

**Type:**

bool

<a id="bpy.types.OperatorOptions.is_repeat"></a>

#### bpy.types.OperatorOptions.is_repeat

True when run from the ‘Adjust Last Operation’ panel (default False, readonly)

**Type:**

bool

<a id="bpy.types.OperatorOptions.is_repeat_last"></a>

#### bpy.types.OperatorOptions.is_repeat_last

True when run from the operator ‘Repeat Last’ (default False, readonly)

**Type:**

bool

<a id="bpy.types.OperatorOptions.use_cursor_region"></a>

#### bpy.types.OperatorOptions.use_cursor_region

Enable to use the region under the cursor for modal execution (default False)

**Type:**

bool

<a id="bpy.types.OperatorOptions.bl_rna_get_subclass"></a>

#### classmethod bpy.types.OperatorOptions.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.OperatorOptions.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.OperatorOptions.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Operator.options`](bpy.types.Operator.md#bpy.types.Operator.options "bpy.types.Operator.options") |  |
