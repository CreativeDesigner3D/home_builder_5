<!-- source: Blender Python API reference 5.2 / bpy.types.ColorRampElement.html -->

<a id="colorrampelement-bpy-struct"></a>

# ColorRampElement(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.ColorRampElement"></a>

### class bpy.types.ColorRampElement(bpy_struct)

Element defining a color at a position in the color ramp

<a id="bpy.types.ColorRampElement.alpha"></a>

#### bpy.types.ColorRampElement.alpha

Set alpha of selected color stop (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.ColorRampElement.color"></a>

#### bpy.types.ColorRampElement.color

Set color of selected color stop (array of 4 items, in [0, inf], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.ColorRampElement.position"></a>

#### bpy.types.ColorRampElement.position

Set position of selected color stop (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.ColorRampElement.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ColorRampElement.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ColorRampElement.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ColorRampElement.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`ColorRamp.elements`](bpy.types.ColorRamp.md#bpy.types.ColorRamp.elements "bpy.types.ColorRamp.elements") - [`ColorRampElements.new`](bpy.types.ColorRampElements.md#bpy.types.ColorRampElements.new "bpy.types.ColorRampElements.new") | - [`ColorRampElements.remove`](bpy.types.ColorRampElements.md#bpy.types.ColorRampElements.remove "bpy.types.ColorRampElements.remove") |
