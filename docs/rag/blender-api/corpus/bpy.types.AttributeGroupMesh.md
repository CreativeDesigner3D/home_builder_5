<!-- source: Blender Python API reference 5.2 / bpy.types.AttributeGroupMesh.html -->

<a id="attributegroupmesh-bpy-prop-collection"></a>

# AttributeGroupMesh(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.AttributeGroupMesh"></a>

### class bpy.types.AttributeGroupMesh(bpy_prop_collection)

Group of geometry attributes

<a id="bpy.types.AttributeGroupMesh.active"></a>

#### bpy.types.AttributeGroupMesh.active

Active attribute

**Type:**

[`Attribute`](bpy.types.Attribute.md#bpy.types.Attribute "bpy.types.Attribute") | None

<a id="bpy.types.AttributeGroupMesh.active_color"></a>

#### bpy.types.AttributeGroupMesh.active_color

Active color attribute for display and editing

**Type:**

[`Attribute`](bpy.types.Attribute.md#bpy.types.Attribute "bpy.types.Attribute") | None

<a id="bpy.types.AttributeGroupMesh.active_color_index"></a>

#### bpy.types.AttributeGroupMesh.active_color_index

Active color attribute index (in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.AttributeGroupMesh.active_color_name"></a>

#### bpy.types.AttributeGroupMesh.active_color_name

The name of the active color attribute for display and editing (default “”, never None)

**Type:**

str

<a id="bpy.types.AttributeGroupMesh.active_index"></a>

#### bpy.types.AttributeGroupMesh.active_index

Active attribute index or -1 when none are active (in [-1, inf], default 0)

**Type:**

int

<a id="bpy.types.AttributeGroupMesh.default_color_name"></a>

#### bpy.types.AttributeGroupMesh.default_color_name

The name of the default color attribute used as a fallback for rendering (default “”, never None)

**Type:**

str

<a id="bpy.types.AttributeGroupMesh.render_color_index"></a>

#### bpy.types.AttributeGroupMesh.render_color_index

The index of the color attribute used as a fallback for rendering (in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.AttributeGroupMesh.new"></a>

#### bpy.types.AttributeGroupMesh.new(name, type, domain)

Add attribute to geometry

**Parameters:**

- **name** (str) – Name, Name of geometry attribute (never None)
- **type** (Literal[[Attribute Type Items](bpy_types_enum_items/attribute_type_items.md#rna-enum-attribute-type-items)]) – Type, Attribute type
- **domain** (Literal[[Attribute Domain Items](bpy_types_enum_items/attribute_domain_items.md#rna-enum-attribute-domain-items)]) – Domain, Type of element that attribute is stored on

**Returns:**

New geometry attribute

**Return type:**

[`Attribute`](bpy.types.Attribute.md#bpy.types.Attribute "bpy.types.Attribute")

<a id="bpy.types.AttributeGroupMesh.remove"></a>

#### bpy.types.AttributeGroupMesh.remove(attribute)

Remove attribute from geometry

**Parameters:**

**attribute** ([`Attribute`](bpy.types.Attribute.md#bpy.types.Attribute "bpy.types.Attribute") | None) – Geometry Attribute (never None)

<a id="bpy.types.AttributeGroupMesh.domain_size"></a>

#### bpy.types.AttributeGroupMesh.domain_size(domain)

Get the size of a given domain

**Parameters:**

**domain** (Literal[[Attribute Domain Items](bpy_types_enum_items/attribute_domain_items.md#rna-enum-attribute-domain-items)]) – Domain, Type of element that attribute is stored on

**Returns:**

Size, Size of the domain (in [0, inf])

**Return type:**

int

<a id="bpy.types.AttributeGroupMesh.bl_rna_get_subclass"></a>

#### classmethod bpy.types.AttributeGroupMesh.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.AttributeGroupMesh.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.AttributeGroupMesh.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Mesh.attributes`](bpy.types.Mesh.md#bpy.types.Mesh.attributes "bpy.types.Mesh.attributes") | - [`Mesh.color_attributes`](bpy.types.Mesh.md#bpy.types.Mesh.color_attributes "bpy.types.Mesh.color_attributes") |
