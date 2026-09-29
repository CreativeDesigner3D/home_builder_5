<!-- source: Blender Python API reference 5.2 / bpy.ops.geometry.html -->

<a id="module-bpy.ops.geometry"></a>

# Geometry Operators

<a id="bpy.ops.geometry.attribute_add"></a>

### bpy.ops.geometry.attribute_add(*, name='', domain='POINT', data_type='FLOAT')

Add attribute to geometry

**Parameters:**

- **name** (str) – Name, Name of new attribute (optional, never None)
- **domain** (Literal[[Attribute Domain Items](bpy_types_enum_items/attribute_domain_items.md#rna-enum-attribute-domain-items)]) – Domain, Type of element that attribute is stored on (optional)
- **data_type** (Literal[[Attribute Type Items](bpy_types_enum_items/attribute_type_items.md#rna-enum-attribute-type-items)]) – Data Type, Type of data stored in attribute (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.geometry.attribute_convert"></a>

### bpy.ops.geometry.attribute_convert(*, mode='GENERIC', domain='POINT', data_type='FLOAT')

Change how the attribute is stored

**Parameters:**

- **mode** (Literal['GENERIC', 'VERTEX_GROUP']) – Mode, (optional)
- **domain** (Literal[[Attribute Domain Items](bpy_types_enum_items/attribute_domain_items.md#rna-enum-attribute-domain-items)]) – Domain, Which geometry element to move the attribute to (optional)
- **data_type** (Literal[[Attribute Type Items](bpy_types_enum_items/attribute_type_items.md#rna-enum-attribute-type-items)]) – Data Type, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.geometry.attribute_remove"></a>

### bpy.ops.geometry.attribute_remove()

Remove attribute from geometry

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.geometry.color_attribute_add"></a>

### bpy.ops.geometry.color_attribute_add(*, name='', domain='POINT', data_type='FLOAT_COLOR', color=(0.0, 0.0, 0.0, 1.0))

Add color attribute to geometry

**Parameters:**

- **name** (str) – Name, Name of new color attribute (optional, never None)
- **domain** (Literal[[Color Attribute Domain Items](bpy_types_enum_items/color_attribute_domain_items.md#rna-enum-color-attribute-domain-items)]) – Domain, Type of element that attribute is stored on (optional)
- **data_type** (Literal[[Color Attribute Type Items](bpy_types_enum_items/color_attribute_type_items.md#rna-enum-color-attribute-type-items)]) – Data Type, Type of data stored in attribute (optional)
- **color** (Sequence[float]) – Color, Default fill color (array of 4 items, in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.geometry.color_attribute_convert"></a>

### bpy.ops.geometry.color_attribute_convert(*, domain='POINT', data_type='FLOAT_COLOR')

Change how the color attribute is stored

**Parameters:**

- **domain** (Literal[[Color Attribute Domain Items](bpy_types_enum_items/color_attribute_domain_items.md#rna-enum-color-attribute-domain-items)]) – Domain, Type of element that attribute is stored on (optional)
- **data_type** (Literal[[Color Attribute Type Items](bpy_types_enum_items/color_attribute_type_items.md#rna-enum-color-attribute-type-items)]) – Data Type, Type of data stored in attribute (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.geometry.color_attribute_duplicate"></a>

### bpy.ops.geometry.color_attribute_duplicate()

Duplicate color attribute

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.geometry.color_attribute_remove"></a>

### bpy.ops.geometry.color_attribute_remove()

Remove color attribute from geometry

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.geometry.color_attribute_render_set"></a>

### bpy.ops.geometry.color_attribute_render_set(*, name='Color')

Set default color attribute used for rendering

**Parameters:**

**name** (str) – Name, Name of color attribute (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.geometry.geometry_randomization"></a>

### bpy.ops.geometry.geometry_randomization(*, value=False)

Toggle geometry randomization for debugging purposes

**Parameters:**

**value** (bool) – Value, Randomize the order of geometry elements (e.g. vertices or edges) after some operations where there are no guarantees about the order. This avoids accidentally depending on something that may change in the future (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]
