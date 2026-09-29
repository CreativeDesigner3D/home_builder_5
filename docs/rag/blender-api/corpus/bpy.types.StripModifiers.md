<!-- source: Blender Python API reference 5.2 / bpy.types.StripModifiers.html -->

<a id="stripmodifiers-bpy-prop-collection"></a>

# StripModifiers(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.StripModifiers"></a>

### class bpy.types.StripModifiers(bpy_prop_collection)

Collection of strip modifiers

<a id="bpy.types.StripModifiers.active"></a>

#### bpy.types.StripModifiers.active

The active strip modifier in the list

**Type:**

[`StripModifier`](bpy.types.StripModifier.md#bpy.types.StripModifier "bpy.types.StripModifier") | None

<a id="bpy.types.StripModifiers.new"></a>

#### bpy.types.StripModifiers.new(name, type)

Add a new modifier

**Parameters:**

- **name** (str) – New name for the modifier (never None)
- **type** (Literal[[Strip Modifier Type Items](bpy_types_enum_items/strip_modifier_type_items.md#rna-enum-strip-modifier-type-items)]) – Modifier type to add

**Returns:**

Newly created modifier

**Return type:**

[`StripModifier`](bpy.types.StripModifier.md#bpy.types.StripModifier "bpy.types.StripModifier")

<a id="bpy.types.StripModifiers.remove"></a>

#### bpy.types.StripModifiers.remove(modifier)

Remove an existing modifier from the strip

**Parameters:**

**modifier** ([`StripModifier`](bpy.types.StripModifier.md#bpy.types.StripModifier "bpy.types.StripModifier") | None) – Modifier to remove (never None)

<a id="bpy.types.StripModifiers.clear"></a>

#### bpy.types.StripModifiers.clear()

Remove all modifiers from the strip

<a id="bpy.types.StripModifiers.bl_rna_get_subclass"></a>

#### classmethod bpy.types.StripModifiers.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.StripModifiers.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.StripModifiers.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Strip.modifiers`](bpy.types.Strip.md#bpy.types.Strip.modifiers "bpy.types.Strip.modifiers") |  |
