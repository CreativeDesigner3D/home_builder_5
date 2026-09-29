<!-- source: Blender Python API reference 5.2 / bpy.types.LineStyleAlphaModifiers.html -->

<a id="linestylealphamodifiers-bpy-prop-collection"></a>

# LineStyleAlphaModifiers(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.LineStyleAlphaModifiers"></a>

### class bpy.types.LineStyleAlphaModifiers(bpy_prop_collection)

Alpha modifiers for changing line alphas

<a id="bpy.types.LineStyleAlphaModifiers.new"></a>

#### bpy.types.LineStyleAlphaModifiers.new(name, type)

Add a alpha modifier to line style

**Parameters:**

- **name** (str) – New name for the alpha modifier (not unique) (never None)
- **type** (Literal[[Linestyle Alpha Modifier Type Items](bpy_types_enum_items/linestyle_alpha_modifier_type_items.md#rna-enum-linestyle-alpha-modifier-type-items)]) – Alpha modifier type to add

**Returns:**

Newly added alpha modifier

**Return type:**

[`LineStyleAlphaModifier`](bpy.types.LineStyleAlphaModifier.md#bpy.types.LineStyleAlphaModifier "bpy.types.LineStyleAlphaModifier")

<a id="bpy.types.LineStyleAlphaModifiers.remove"></a>

#### bpy.types.LineStyleAlphaModifiers.remove(modifier)

Remove a alpha modifier from line style

**Parameters:**

**modifier** ([`LineStyleAlphaModifier`](bpy.types.LineStyleAlphaModifier.md#bpy.types.LineStyleAlphaModifier "bpy.types.LineStyleAlphaModifier") | None) – Alpha modifier to remove (never None)

<a id="bpy.types.LineStyleAlphaModifiers.bl_rna_get_subclass"></a>

#### classmethod bpy.types.LineStyleAlphaModifiers.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.LineStyleAlphaModifiers.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.LineStyleAlphaModifiers.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`FreestyleLineStyle.alpha_modifiers`](bpy.types.FreestyleLineStyle.md#bpy.types.FreestyleLineStyle.alpha_modifiers "bpy.types.FreestyleLineStyle.alpha_modifiers") |  |
