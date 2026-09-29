<!-- source: Blender Python API reference 5.2 / bpy.types.Struct.html -->

<a id="struct-bpy-struct"></a>

# Struct(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.Struct"></a>

### class bpy.types.Struct(bpy_struct)

RNA structure definition

<a id="bpy.types.Struct.base"></a>

#### bpy.types.Struct.base

Struct definition this is derived from (readonly)

**Type:**

[`Struct`](#bpy.types.Struct "bpy.types.Struct") | None

<a id="bpy.types.Struct.description"></a>

#### bpy.types.Struct.description

Description of the Struct’s purpose (default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.Struct.functions"></a>

#### bpy.types.Struct.functions

(default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`Function`](bpy.types.Function.md#bpy.types.Function "bpy.types.Function")]

<a id="bpy.types.Struct.identifier"></a>

#### bpy.types.Struct.identifier

Unique name used in the code and scripting (default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.Struct.name"></a>

#### bpy.types.Struct.name

Human readable name (default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.Struct.name_property"></a>

#### bpy.types.Struct.name_property

Property that gives the name of the struct (readonly)

**Type:**

[`StringProperty`](bpy.types.StringProperty.md#bpy.types.StringProperty "bpy.types.StringProperty") | None

<a id="bpy.types.Struct.nested"></a>

#### bpy.types.Struct.nested

Struct in which this struct is always nested, and to which it logically belongs (readonly)

**Type:**

[`Struct`](#bpy.types.Struct "bpy.types.Struct") | None

<a id="bpy.types.Struct.properties"></a>

#### bpy.types.Struct.properties

Properties in the struct (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`Property`](bpy.types.Property.md#bpy.types.Property "bpy.types.Property")]

<a id="bpy.types.Struct.property_tags"></a>

#### bpy.types.Struct.property_tags

Tags that properties can use to influence behavior (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`EnumPropertyItem`](bpy.types.EnumPropertyItem.md#bpy.types.EnumPropertyItem "bpy.types.EnumPropertyItem")]

<a id="bpy.types.Struct.translation_context"></a>

#### bpy.types.Struct.translation_context

Translation context of the struct’s name (default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.Struct.bl_rna_get_subclass"></a>

#### classmethod bpy.types.Struct.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.Struct.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.Struct.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`BlenderRNA.structs`](bpy.types.BlenderRNA.md#bpy.types.BlenderRNA.structs "bpy.types.BlenderRNA.structs") - [`CollectionProperty.fixed_type`](bpy.types.CollectionProperty.md#bpy.types.CollectionProperty.fixed_type "bpy.types.CollectionProperty.fixed_type") - [`PointerProperty.fixed_type`](bpy.types.PointerProperty.md#bpy.types.PointerProperty.fixed_type "bpy.types.PointerProperty.fixed_type") | - [`Property.srna`](bpy.types.Property.md#bpy.types.Property.srna "bpy.types.Property.srna") - [`Struct.base`](#bpy.types.Struct.base "bpy.types.Struct.base") - [`Struct.nested`](#bpy.types.Struct.nested "bpy.types.Struct.nested") |
