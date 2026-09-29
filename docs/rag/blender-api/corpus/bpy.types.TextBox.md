<!-- source: Blender Python API reference 5.2 / bpy.types.TextBox.html -->

<a id="textbox-bpy-struct"></a>

# TextBox(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.TextBox"></a>

### class bpy.types.TextBox(bpy_struct)

Text bounding box for layout

<a id="bpy.types.TextBox.height"></a>

#### bpy.types.TextBox.height

(in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.TextBox.width"></a>

#### bpy.types.TextBox.width

(in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.TextBox.x"></a>

#### bpy.types.TextBox.x

(in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.TextBox.y"></a>

#### bpy.types.TextBox.y

(in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.TextBox.bl_rna_get_subclass"></a>

#### classmethod bpy.types.TextBox.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.TextBox.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.TextBox.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`TextCurve.text_boxes`](bpy.types.TextCurve.md#bpy.types.TextCurve.text_boxes "bpy.types.TextCurve.text_boxes") |  |
