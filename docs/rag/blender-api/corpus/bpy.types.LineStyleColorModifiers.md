<!-- source: Blender Python API reference 5.2 / bpy.types.LineStyleColorModifiers.html -->

<a id="linestylecolormodifiers-bpy-prop-collection"></a>

# LineStyleColorModifiers(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.LineStyleColorModifiers"></a>

### class bpy.types.LineStyleColorModifiers(bpy_prop_collection)

Color modifiers for changing line colors

<a id="bpy.types.LineStyleColorModifiers.new"></a>

#### bpy.types.LineStyleColorModifiers.new(name, type)

Add a color modifier to line style

**Parameters:**

- **name** (str) – New name for the color modifier (not unique) (never None)
- **type** (Literal[[Linestyle Color Modifier Type Items](bpy_types_enum_items/linestyle_color_modifier_type_items.md#rna-enum-linestyle-color-modifier-type-items)]) – Color modifier type to add

**Returns:**

Newly added color modifier

**Return type:**

[`LineStyleColorModifier`](bpy.types.LineStyleColorModifier.md#bpy.types.LineStyleColorModifier "bpy.types.LineStyleColorModifier")

<a id="bpy.types.LineStyleColorModifiers.remove"></a>

#### bpy.types.LineStyleColorModifiers.remove(modifier)

Remove a color modifier from line style

**Parameters:**

**modifier** ([`LineStyleColorModifier`](bpy.types.LineStyleColorModifier.md#bpy.types.LineStyleColorModifier "bpy.types.LineStyleColorModifier") | None) – Color modifier to remove (never None)

<a id="bpy.types.LineStyleColorModifiers.bl_rna_get_subclass"></a>

#### classmethod bpy.types.LineStyleColorModifiers.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.LineStyleColorModifiers.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.LineStyleColorModifiers.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`FreestyleLineStyle.color_modifiers`](bpy.types.FreestyleLineStyle.md#bpy.types.FreestyleLineStyle.color_modifiers "bpy.types.FreestyleLineStyle.color_modifiers") |  |
