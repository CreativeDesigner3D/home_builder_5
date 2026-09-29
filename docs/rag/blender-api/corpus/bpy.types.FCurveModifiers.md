<!-- source: Blender Python API reference 5.2 / bpy.types.FCurveModifiers.html -->

<a id="fcurvemodifiers-bpy-prop-collection"></a>

# FCurveModifiers(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.FCurveModifiers"></a>

### class bpy.types.FCurveModifiers(bpy_prop_collection)

Collection of F-Curve Modifiers

<a id="bpy.types.FCurveModifiers.active"></a>

#### bpy.types.FCurveModifiers.active

Active F-Curve Modifier

**Type:**

[`FModifier`](bpy.types.FModifier.md#bpy.types.FModifier "bpy.types.FModifier") | None

<a id="bpy.types.FCurveModifiers.new"></a>

#### bpy.types.FCurveModifiers.new(type)

Add a constraint to this object

**Parameters:**

**type** (Literal[[Fmodifier Type Items](bpy_types_enum_items/fmodifier_type_items.md#rna-enum-fmodifier-type-items)]) – Constraint type to add

**Returns:**

New fmodifier

**Return type:**

[`FModifier`](bpy.types.FModifier.md#bpy.types.FModifier "bpy.types.FModifier")

<a id="bpy.types.FCurveModifiers.remove"></a>

#### bpy.types.FCurveModifiers.remove(modifier)

Remove a modifier from this F-Curve

**Parameters:**

**modifier** ([`FModifier`](bpy.types.FModifier.md#bpy.types.FModifier "bpy.types.FModifier") | None) – Removed modifier (never None)

<a id="bpy.types.FCurveModifiers.bl_rna_get_subclass"></a>

#### classmethod bpy.types.FCurveModifiers.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.FCurveModifiers.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.FCurveModifiers.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`FCurve.modifiers`](bpy.types.FCurve.md#bpy.types.FCurve.modifiers "bpy.types.FCurve.modifiers") |  |
