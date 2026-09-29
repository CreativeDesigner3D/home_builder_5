<!-- source: Blender Python API reference 5.2 / bpy.types.Attribute.html -->

<a id="attribute-bpy-struct"></a>

# Attribute(bpy_struct)

Attributes are used to store data that corresponds to geometry elements.
Geometry elements are items in one of the geometry domains like points, curves, or faces.

An attribute has a `name`, a `type`, and is stored on a `domain`.

`name`
:   The name of this attribute. Names have to be unique within the same geometry.
    If the name starts with a `.`, the attribute is hidden from the UI.

`type`
:   The type of data that this attribute stores, e.g. a float, integer, color, etc.
    See [Attribute Type Items](bpy_types_enum_items/attribute_type_items.md).

`domain`
:   The geometry domain that the attribute is stored on.
    See [Attribute Domain Items](bpy_types_enum_items/attribute_domain_items.md).

<a id="using-attributes"></a>

## Using Attributes

Attributes can be stored on geometries like [`Mesh`](bpy.types.Mesh.md#bpy.types.Mesh "bpy.types.Mesh"), [`Curves`](bpy.types.Curves.md#bpy.types.Curves "bpy.types.Curves"), [`PointCloud`](bpy.types.PointCloud.md#bpy.types.PointCloud "bpy.types.PointCloud"), etc.
These geometries have attribute groups (usually called `attributes`).
Using the groups, attributes can then be accessed by their name:

```python
radii = curves.attributes["radius"]
```

Creating and storing custom attributes is done using the `attributes.new` function:

```python
# Add a new attribute named `my_attribute_name` of type `float` on the point domain of the geometry.
my_attribute = curves.attributes.new("my_attribute_name", 'FLOAT', 'POINT')
```

Removing attributes can be done like so:

```python
attribute = drawing.attributes["some_attribute"]
drawing.attributes.remove(attribute)
```

> **Note:**
>
> Some attributes are required and cannot be removed, like `"position"`.

Attribute values are read by accessing their `attribute.data` collection property.
However, in cases where multiple values should be read at once,
it is better to use the [`bpy_prop_collection.foreach_get`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection.foreach_get "bpy.types.bpy_prop_collection.foreach_get") function and read the values into a `numpy` buffer.

```python
import numpy as np

# Get the radius attribute.
radii = curves.attributes["radius"]
# Print the radius of the first point.
print(radii.data[0].value)
# Output: 0.005

# Get the total number of points.
num_points = attributes.domain_size('POINT')
# Create an empty buffer to read all the radii into.
radii_data = np.zeros(num_points, dtype=np.float32)
# Read all the radii of the curves into `radii_data` at once.
radii.data.foreach_get('value', radii_data)
# Print all the radii.
print(radii_data)
# Output: [0.1, 0.2, 0.3, 0.4, ... ]
```

> **Note:**
>
> Some attribute types use different named properties to access their value.
> Instead of `value`, vectors use `vector`, and colors use `color`.

Writing to different attribute types is very similar. You can simply assign to a value directly.
Again, when writing to multiple values, it is recommended to use the [`bpy_prop_collection.foreach_set`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection.foreach_set "bpy.types.bpy_prop_collection.foreach_set") function
to write the values from a `numpy` buffer.

```python
import numpy as np

radii = curves.attributes["radius"]
# Write a radius with a value of 0.5 to the first point.
radii.data[0].value = 0.5
print(radii.data[0].value)
# Output: 0.5

num_points = attributes.domain_size('POINT')
# Generate random radii with values between 0.001 and 0.05 using numpy.
new_radii = np.random.uniform(0.001, 0.05, num_points)
# Write the new radii to the radius attribute.
radii.data.foreach_set('value', new_radii)
```

The [`bpy_prop_collection.foreach_get`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection.foreach_get "bpy.types.bpy_prop_collection.foreach_get") / [`bpy_prop_collection.foreach_set`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection.foreach_set "bpy.types.bpy_prop_collection.foreach_set") methods require a flat array.
This is sometimes not desirable, e.g. when reading/writing positions, which are 3D vectors.
In these cases, it’s possible to use `np.ravel` to pass the data as a flat array:

```python
num_points = attributes.domain_size('POINT')
positions = curves.attributes['position']
# Here, we're using a numpy array with shape (num_points, 3) so that each
# element is a 3d vector.
positions_data = np.zeros((num_points, 3), dtype=np.float32)
# The `np.ravel` function will pass the `positions_data` as a flat array
# without changing the original shape.
positions.data.foreach_get('vector', np.ravel(positions_data))
print(positions_data)
# Output: [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6], ...]
```

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

Subclasses

- [BoolAttribute(Attribute)](bpy.types.BoolAttribute.md)
- [ByteColorAttribute(Attribute)](bpy.types.ByteColorAttribute.md)
- [ByteIntAttribute(Attribute)](bpy.types.ByteIntAttribute.md)
- [Float2Attribute(Attribute)](bpy.types.Float2Attribute.md)
- [Float4Attribute(Attribute)](bpy.types.Float4Attribute.md)
- [Float4x4Attribute(Attribute)](bpy.types.Float4x4Attribute.md)
- [FloatAttribute(Attribute)](bpy.types.FloatAttribute.md)
- [FloatColorAttribute(Attribute)](bpy.types.FloatColorAttribute.md)
- [FloatVectorAttribute(Attribute)](bpy.types.FloatVectorAttribute.md)
- [Int2Attribute(Attribute)](bpy.types.Int2Attribute.md)
- [IntAttribute(Attribute)](bpy.types.IntAttribute.md)
- [QuaternionAttribute(Attribute)](bpy.types.QuaternionAttribute.md)
- [Short2Attribute(Attribute)](bpy.types.Short2Attribute.md)
- [StringAttribute(Attribute)](bpy.types.StringAttribute.md)

<a id="bpy.types.Attribute"></a>

### class bpy.types.Attribute(bpy_struct)

Geometry attribute

<a id="bpy.types.Attribute.data_type"></a>

#### bpy.types.Attribute.data_type

Type of data stored in attribute (default `'FLOAT'`, readonly)

**Type:**

Literal[[Attribute Type Items](bpy_types_enum_items/attribute_type_items.md#rna-enum-attribute-type-items)]

<a id="bpy.types.Attribute.domain"></a>

#### bpy.types.Attribute.domain

Domain of the Attribute (default `'POINT'`, readonly)

**Type:**

Literal[[Attribute Domain Items](bpy_types_enum_items/attribute_domain_items.md#rna-enum-attribute-domain-items)]

<a id="bpy.types.Attribute.is_internal"></a>

#### bpy.types.Attribute.is_internal

The attribute is meant for internal use by Blender (default False, readonly)

**Type:**

bool

<a id="bpy.types.Attribute.is_required"></a>

#### bpy.types.Attribute.is_required

Whether the attribute can be removed or renamed (default False, readonly)

**Type:**

bool

<a id="bpy.types.Attribute.name"></a>

#### bpy.types.Attribute.name

Name of the Attribute (default “”, never None)

**Type:**

str

<a id="bpy.types.Attribute.storage_type"></a>

#### bpy.types.Attribute.storage_type

Method used to store the data (default `'ARRAY'`, readonly)

**Type:**

Literal[[Attr Storage Type Items](bpy_types_enum_items/attr_storage_type_items.md#rna-enum-attr-storage-type-items)]

<a id="bpy.types.Attribute.bl_rna_get_subclass"></a>

#### classmethod bpy.types.Attribute.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.Attribute.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.Attribute.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

### Inherited Properties

bpy_struct.id_data

<a id="inherited-functions"></a>

### Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values

<a id="references"></a>

### References

|  |  |
| --- | --- |
| - [`AttributeGroupCurves.active`](bpy.types.AttributeGroupCurves.md#bpy.types.AttributeGroupCurves.active "bpy.types.AttributeGroupCurves.active") - [`AttributeGroupCurves.new`](bpy.types.AttributeGroupCurves.md#bpy.types.AttributeGroupCurves.new "bpy.types.AttributeGroupCurves.new") - [`AttributeGroupCurves.remove`](bpy.types.AttributeGroupCurves.md#bpy.types.AttributeGroupCurves.remove "bpy.types.AttributeGroupCurves.remove") - [`AttributeGroupGreasePencil.active`](bpy.types.AttributeGroupGreasePencil.md#bpy.types.AttributeGroupGreasePencil.active "bpy.types.AttributeGroupGreasePencil.active") - [`AttributeGroupGreasePencil.new`](bpy.types.AttributeGroupGreasePencil.md#bpy.types.AttributeGroupGreasePencil.new "bpy.types.AttributeGroupGreasePencil.new") - [`AttributeGroupGreasePencil.remove`](bpy.types.AttributeGroupGreasePencil.md#bpy.types.AttributeGroupGreasePencil.remove "bpy.types.AttributeGroupGreasePencil.remove") - [`AttributeGroupGreasePencilDrawing.active`](bpy.types.AttributeGroupGreasePencilDrawing.md#bpy.types.AttributeGroupGreasePencilDrawing.active "bpy.types.AttributeGroupGreasePencilDrawing.active") - [`AttributeGroupGreasePencilDrawing.new`](bpy.types.AttributeGroupGreasePencilDrawing.md#bpy.types.AttributeGroupGreasePencilDrawing.new "bpy.types.AttributeGroupGreasePencilDrawing.new") - [`AttributeGroupGreasePencilDrawing.remove`](bpy.types.AttributeGroupGreasePencilDrawing.md#bpy.types.AttributeGroupGreasePencilDrawing.remove "bpy.types.AttributeGroupGreasePencilDrawing.remove") - [`AttributeGroupMesh.active`](bpy.types.AttributeGroupMesh.md#bpy.types.AttributeGroupMesh.active "bpy.types.AttributeGroupMesh.active") - [`AttributeGroupMesh.active_color`](bpy.types.AttributeGroupMesh.md#bpy.types.AttributeGroupMesh.active_color "bpy.types.AttributeGroupMesh.active_color") - [`AttributeGroupMesh.new`](bpy.types.AttributeGroupMesh.md#bpy.types.AttributeGroupMesh.new "bpy.types.AttributeGroupMesh.new") - [`AttributeGroupMesh.remove`](bpy.types.AttributeGroupMesh.md#bpy.types.AttributeGroupMesh.remove "bpy.types.AttributeGroupMesh.remove") | - [`AttributeGroupPointCloud.active`](bpy.types.AttributeGroupPointCloud.md#bpy.types.AttributeGroupPointCloud.active "bpy.types.AttributeGroupPointCloud.active") - [`AttributeGroupPointCloud.new`](bpy.types.AttributeGroupPointCloud.md#bpy.types.AttributeGroupPointCloud.new "bpy.types.AttributeGroupPointCloud.new") - [`AttributeGroupPointCloud.remove`](bpy.types.AttributeGroupPointCloud.md#bpy.types.AttributeGroupPointCloud.remove "bpy.types.AttributeGroupPointCloud.remove") - [`Curves.attributes`](bpy.types.Curves.md#bpy.types.Curves.attributes "bpy.types.Curves.attributes") - [`Curves.color_attributes`](bpy.types.Curves.md#bpy.types.Curves.color_attributes "bpy.types.Curves.color_attributes") - [`GreasePencil.attributes`](bpy.types.GreasePencil.md#bpy.types.GreasePencil.attributes "bpy.types.GreasePencil.attributes") - [`GreasePencil.color_attributes`](bpy.types.GreasePencil.md#bpy.types.GreasePencil.color_attributes "bpy.types.GreasePencil.color_attributes") - [`GreasePencilDrawing.attributes`](bpy.types.GreasePencilDrawing.md#bpy.types.GreasePencilDrawing.attributes "bpy.types.GreasePencilDrawing.attributes") - [`GreasePencilDrawing.color_attributes`](bpy.types.GreasePencilDrawing.md#bpy.types.GreasePencilDrawing.color_attributes "bpy.types.GreasePencilDrawing.color_attributes") - [`Mesh.attributes`](bpy.types.Mesh.md#bpy.types.Mesh.attributes "bpy.types.Mesh.attributes") - [`Mesh.color_attributes`](bpy.types.Mesh.md#bpy.types.Mesh.color_attributes "bpy.types.Mesh.color_attributes") - [`PointCloud.attributes`](bpy.types.PointCloud.md#bpy.types.PointCloud.attributes "bpy.types.PointCloud.attributes") - [`PointCloud.color_attributes`](bpy.types.PointCloud.md#bpy.types.PointCloud.color_attributes "bpy.types.PointCloud.color_attributes") |
