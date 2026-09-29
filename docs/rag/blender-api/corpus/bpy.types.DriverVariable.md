<!-- source: Blender Python API reference 5.2 / bpy.types.DriverVariable.html -->

<a id="drivervariable-bpy-struct"></a>

# DriverVariable(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.DriverVariable"></a>

### class bpy.types.DriverVariable(bpy_struct)

Variable from some source/target for driver relationship

<a id="bpy.types.DriverVariable.is_name_valid"></a>

#### bpy.types.DriverVariable.is_name_valid

Is this a valid name for a driver variable (default True, readonly)

**Type:**

bool

<a id="bpy.types.DriverVariable.name"></a>

#### bpy.types.DriverVariable.name

Name to use in scripted expressions/functions (no spaces or dots are allowed, and must start with a letter) (default “”, never None)

**Type:**

str

<a id="bpy.types.DriverVariable.targets"></a>

#### bpy.types.DriverVariable.targets

Sources of input data for evaluating this variable (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`DriverTarget`](bpy.types.DriverTarget.md#bpy.types.DriverTarget "bpy.types.DriverTarget")]

<a id="bpy.types.DriverVariable.type"></a>

#### bpy.types.DriverVariable.type

Driver variable type (default `'SINGLE_PROP'`)

- `SINGLE_PROP`
  Single Property – Use the value from some RNA property.
- `TRANSFORMS`
  Transform Channel – Final transformation value of object or bone.
- `ROTATION_DIFF`
  Rotational Difference – Use the angle between two bones.
- `LOC_DIFF`
  Distance – Distance between two bones or objects.
- `CONTEXT_PROP`
  Context Property – Use the value from some RNA property within the current evaluation context.

**Type:**

Literal[‘SINGLE_PROP’, ‘TRANSFORMS’, ‘ROTATION_DIFF’, ‘LOC_DIFF’, ‘CONTEXT_PROP’]

<a id="bpy.types.DriverVariable.bl_rna_get_subclass"></a>

#### classmethod bpy.types.DriverVariable.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.DriverVariable.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.DriverVariable.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([type](#bpy.types.DriverVariable.type "bpy.types.DriverVariable.type") | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

[type](#bpy.types.DriverVariable.type "bpy.types.DriverVariable.type")

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
| - [`ChannelDriverVariables.new`](bpy.types.ChannelDriverVariables.md#bpy.types.ChannelDriverVariables.new "bpy.types.ChannelDriverVariables.new") - [`ChannelDriverVariables.remove`](bpy.types.ChannelDriverVariables.md#bpy.types.ChannelDriverVariables.remove "bpy.types.ChannelDriverVariables.remove") | - [`Driver.variables`](bpy.types.Driver.md#bpy.types.Driver.variables "bpy.types.Driver.variables") |
