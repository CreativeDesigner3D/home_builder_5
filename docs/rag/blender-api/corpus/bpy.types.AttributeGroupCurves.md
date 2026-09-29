<!-- source: Blender Python API reference 5.2 / bpy.types.AttributeGroupCurves.html -->

<a id="attributegroupcurves-bpy-prop-collection"></a>

# AttributeGroupCurves(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.AttributeGroupCurves"></a>

### class bpy.types.AttributeGroupCurves(bpy_prop_collection)

Group of geometry attributes

<a id="bpy.types.AttributeGroupCurves.active"></a>

#### bpy.types.AttributeGroupCurves.active

Active attribute

**Type:**

[`Attribute`](bpy.types.Attribute.md#bpy.types.Attribute "bpy.types.Attribute") | None

<a id="bpy.types.AttributeGroupCurves.active_index"></a>

#### bpy.types.AttributeGroupCurves.active_index

Active attribute index or -1 when none are active (in [-1, inf], default 0)

**Type:**

int

<a id="bpy.types.AttributeGroupCurves.new"></a>

#### bpy.types.AttributeGroupCurves.new(name, type, domain)

Add attribute to geometry

**Parameters:**

- **name** (str) – Name, Name of geometry attribute (never None)
- **type** (Literal[[Attribute Type Items](bpy_types_enum_items/attribute_type_items.md#rna-enum-attribute-type-items)]) – Type, Attribute type
- **domain** (Literal[[Attribute Domain Items](bpy_types_enum_items/attribute_domain_items.md#rna-enum-attribute-domain-items)]) – Domain, Type of element that attribute is stored on

**Returns:**

New geometry attribute

**Return type:**

[`Attribute`](bpy.types.Attribute.md#bpy.types.Attribute "bpy.types.Attribute")

<a id="bpy.types.AttributeGroupCurves.remove"></a>

#### bpy.types.AttributeGroupCurves.remove(attribute)

Remove attribute from geometry

**Parameters:**

**attribute** ([`Attribute`](bpy.types.Attribute.md#bpy.types.Attribute "bpy.types.Attribute") | None) – Geometry Attribute (never None)

<a id="bpy.types.AttributeGroupCurves.domain_size"></a>

#### bpy.types.AttributeGroupCurves.domain_size(domain)

Get the size of a given domain

**Parameters:**

**domain** (Literal[[Attribute Domain Items](bpy_types_enum_items/attribute_domain_items.md#rna-enum-attribute-domain-items)]) – Domain, Type of element that attribute is stored on

**Returns:**

Size, Size of the domain (in [0, inf])

**Return type:**

int

<a id="bpy.types.AttributeGroupCurves.bl_rna_get_subclass"></a>

#### classmethod bpy.types.AttributeGroupCurves.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.AttributeGroupCurves.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.AttributeGroupCurves.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Curves.attributes`](bpy.types.Curves.md#bpy.types.Curves.attributes "bpy.types.Curves.attributes") | - [`Curves.color_attributes`](bpy.types.Curves.md#bpy.types.Curves.color_attributes "bpy.types.Curves.color_attributes") |
