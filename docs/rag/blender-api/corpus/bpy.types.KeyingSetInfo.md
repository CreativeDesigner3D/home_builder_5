<!-- source: Blender Python API reference 5.2 / bpy.types.KeyingSetInfo.html -->

<a id="keyingsetinfo-bpy-struct"></a>

# KeyingSetInfo(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.KeyingSetInfo"></a>

### class bpy.types.KeyingSetInfo(bpy_struct)

Callback function defines for builtin Keying Sets

<a id="bpy.types.KeyingSetInfo.bl_description"></a>

#### bpy.types.KeyingSetInfo.bl_description

A short description of the keying set (default “”, never None)

**Type:**

str

<a id="bpy.types.KeyingSetInfo.bl_idname"></a>

#### bpy.types.KeyingSetInfo.bl_idname

If this is set, the Keying Set gets a custom ID, otherwise it takes the name of the class used to define the Keying Set (for example, if the class name is “BUILTIN_KSI_location”, and bl_idname is not set by the script, then bl_idname = “BUILTIN_KSI_location”) (default “”, never None)

**Type:**

str

<a id="bpy.types.KeyingSetInfo.bl_label"></a>

#### bpy.types.KeyingSetInfo.bl_label

(default “”, never None)

**Type:**

str

<a id="bpy.types.KeyingSetInfo.bl_options"></a>

#### bpy.types.KeyingSetInfo.bl_options

Keying Set options to use when inserting keyframes (default set())

**Type:**

set[Literal[[Keying Flag Items](bpy_types_enum_items/keying_flag_items.md#rna-enum-keying-flag-items)]]

<a id="bpy.types.KeyingSetInfo.poll"></a>

#### bpy.types.KeyingSetInfo.poll(context)

Test if Keying Set can be used or not

**Parameters:**

**context** ([`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context") | None) – The context

**Return type:**

bool

<a id="bpy.types.KeyingSetInfo.iterator"></a>

#### bpy.types.KeyingSetInfo.iterator(context, ks)

Call generate() on the structs which have properties to be keyframed

**Parameters:**

- **context** ([`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context") | None) – The context
- **ks** ([`KeyingSet`](bpy.types.KeyingSet.md#bpy.types.KeyingSet "bpy.types.KeyingSet") | None) – Keying set this iterator runs on

<a id="bpy.types.KeyingSetInfo.generate"></a>

#### bpy.types.KeyingSetInfo.generate(context, ks, data)

Add Paths to the Keying Set to keyframe the properties of the given data

**Parameters:**

- **context** ([`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context") | None) – The context
- **ks** ([`KeyingSet`](bpy.types.KeyingSet.md#bpy.types.KeyingSet "bpy.types.KeyingSet") | None) – Keying set to add paths to
- **data** ([`AnyType`](bpy.types.AnyType.md#bpy.types.AnyType "bpy.types.AnyType") | None) – Data to add paths from (never None)

<a id="bpy.types.KeyingSetInfo.bl_rna_get_subclass"></a>

#### classmethod bpy.types.KeyingSetInfo.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.KeyingSetInfo.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.KeyingSetInfo.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`KeyingSet.type_info`](bpy.types.KeyingSet.md#bpy.types.KeyingSet.type_info "bpy.types.KeyingSet.type_info") |  |
