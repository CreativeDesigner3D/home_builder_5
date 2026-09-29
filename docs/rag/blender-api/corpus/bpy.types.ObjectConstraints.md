<!-- source: Blender Python API reference 5.2 / bpy.types.ObjectConstraints.html -->

<a id="objectconstraints-bpy-prop-collection"></a>

# ObjectConstraints(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.ObjectConstraints"></a>

### class bpy.types.ObjectConstraints(bpy_prop_collection)

Collection of object constraints

<a id="bpy.types.ObjectConstraints.active"></a>

#### bpy.types.ObjectConstraints.active

Active Object constraint

**Type:**

[`Constraint`](bpy.types.Constraint.md#bpy.types.Constraint "bpy.types.Constraint") | None

<a id="bpy.types.ObjectConstraints.new"></a>

#### bpy.types.ObjectConstraints.new(type)

Add a new constraint to this object

**Parameters:**

**type** (Literal[[Constraint Type Items](bpy_types_enum_items/constraint_type_items.md#rna-enum-constraint-type-items)]) – Constraint type to add

**Returns:**

New constraint

**Return type:**

[`Constraint`](bpy.types.Constraint.md#bpy.types.Constraint "bpy.types.Constraint")

<a id="bpy.types.ObjectConstraints.remove"></a>

#### bpy.types.ObjectConstraints.remove(constraint)

Remove a constraint from this object

**Parameters:**

**constraint** ([`Constraint`](bpy.types.Constraint.md#bpy.types.Constraint "bpy.types.Constraint") | None) – Removed constraint (never None)

<a id="bpy.types.ObjectConstraints.clear"></a>

#### bpy.types.ObjectConstraints.clear()

Remove all constraint from this object

<a id="bpy.types.ObjectConstraints.move"></a>

#### bpy.types.ObjectConstraints.move(from_index, to_index)

Move a constraint to a different position

**Parameters:**

- **from_index** (int) – From Index, Index to move (in [-inf, inf])
- **to_index** (int) – To Index, Target index (in [-inf, inf])

<a id="bpy.types.ObjectConstraints.copy"></a>

#### bpy.types.ObjectConstraints.copy(constraint)

Add a new constraint that is a copy of the given one

**Parameters:**

**constraint** ([`Constraint`](bpy.types.Constraint.md#bpy.types.Constraint "bpy.types.Constraint") | None) – Constraint to copy - may belong to a different object (never None)

**Returns:**

New constraint

**Return type:**

[`Constraint`](bpy.types.Constraint.md#bpy.types.Constraint "bpy.types.Constraint")

<a id="bpy.types.ObjectConstraints.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ObjectConstraints.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ObjectConstraints.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ObjectConstraints.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Object.constraints`](bpy.types.Object.md#bpy.types.Object.constraints "bpy.types.Object.constraints") |  |
