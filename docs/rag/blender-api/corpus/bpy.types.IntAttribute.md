<!-- source: Blender Python API reference 5.2 / bpy.types.IntAttribute.html -->

<a id="intattribute-attribute"></a>

# IntAttribute(Attribute)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Attribute`](bpy.types.Attribute.md#bpy.types.Attribute "bpy.types.Attribute")

<a id="bpy.types.IntAttribute"></a>

### class bpy.types.IntAttribute(Attribute)

Geometry attribute that stores integer values

<a id="bpy.types.IntAttribute.data"></a>

#### bpy.types.IntAttribute.data

(default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`IntAttributeValue`](bpy.types.IntAttributeValue.md#bpy.types.IntAttributeValue "bpy.types.IntAttributeValue")]

<a id="bpy.types.IntAttribute.bl_rna_get_subclass"></a>

#### classmethod bpy.types.IntAttribute.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.IntAttribute.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.IntAttribute.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, Attribute.name, Attribute.data_type, Attribute.storage_type, Attribute.domain, Attribute.is_internal, Attribute.is_required

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, Attribute.bl_rna_get_subclass, Attribute.bl_rna_get_subclass_py
