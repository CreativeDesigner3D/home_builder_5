<!-- source: Blender Python API reference 5.2 / bpy.types.IDOverrideLibraryPropertyOperations.html -->

<a id="idoverridelibrarypropertyoperations-bpy-prop-collection"></a>

# IDOverrideLibraryPropertyOperations(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.IDOverrideLibraryPropertyOperations"></a>

### class bpy.types.IDOverrideLibraryPropertyOperations(bpy_prop_collection)

Collection of override operations

<a id="bpy.types.IDOverrideLibraryPropertyOperations.add"></a>

#### bpy.types.IDOverrideLibraryPropertyOperations.add(operation, *, use_id=False, subitem_reference_name='', subitem_local_name='', subitem_reference_id=None, subitem_local_id=None, subitem_reference_index=-1, subitem_local_index=-1)

Add a new operation

**Parameters:**

- **operation** (Literal['NOOP', 'REPLACE', 'DIFF_ADD', 'DIFF_SUB', 'FACT_MULTIPLY', 'INSERT_AFTER', 'INSERT_BEFORE', 'CUSTOM']) –

  Operation, What override operation is performed

  - `NOOP`
    No-Op – Does nothing, prevents adding actual overrides (NOT USED).
  - `REPLACE`
    Replace – Replace value of reference by overriding one.
  - `DIFF_ADD`
    Differential – Stores and apply difference between reference and local value (NOT USED).
  - `DIFF_SUB`
    Differential – Stores and apply difference between reference and local value (NOT USED).
  - `FACT_MULTIPLY`
    Factor – Stores and apply multiplication factor between reference and local value (NOT USED).
  - `INSERT_AFTER`
    Insert After – Insert a new item into collection after the one referenced in subitem_reference_name/_id or _index.
  - `INSERT_BEFORE`
    Insert Before – Insert a new item into collection before the one referenced in subitem_reference_name/_id or _index (NOT USED).
  - `CUSTOM`
    Custom – Custom operation, specific to a RNA property, and handled through dedicated callbacks (used in specific cases, e.g. to handle data not actually exposed in RNA).
- **use_id** (bool) – Use ID Pointer Subitem, Whether the found or created liboverride operation should use ID pointers or not (optional)
- **subitem_reference_name** (str) – Subitem Reference Name, Used to handle insertions or ID replacements into collection (optional, never None)
- **subitem_local_name** (str) – Subitem Local Name, Used to handle insertions or ID replacements into collection (optional, never None)
- **subitem_reference_id** ([`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID") | None) – Subitem Reference ID, Used to handle ID replacements into collection (optional)
- **subitem_local_id** ([`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID") | None) – Subitem Local ID, Used to handle ID replacements into collection (optional)
- **subitem_reference_index** (int) – Subitem Reference Index, Used to handle insertions or ID replacements into collection (in [-1, inf], optional)
- **subitem_local_index** (int) – Subitem Local Index, Used to handle insertions or ID replacements into collection (in [-1, inf], optional)

**Returns:**

New Operation, Created operation

**Return type:**

[`IDOverrideLibraryPropertyOperation`](bpy.types.IDOverrideLibraryPropertyOperation.md#bpy.types.IDOverrideLibraryPropertyOperation "bpy.types.IDOverrideLibraryPropertyOperation")

<a id="bpy.types.IDOverrideLibraryPropertyOperations.remove"></a>

#### bpy.types.IDOverrideLibraryPropertyOperations.remove(operation)

Remove and delete an operation

**Parameters:**

**operation** ([`IDOverrideLibraryPropertyOperation`](bpy.types.IDOverrideLibraryPropertyOperation.md#bpy.types.IDOverrideLibraryPropertyOperation "bpy.types.IDOverrideLibraryPropertyOperation") | None) – Operation, Override operation to be deleted

<a id="bpy.types.IDOverrideLibraryPropertyOperations.bl_rna_get_subclass"></a>

#### classmethod bpy.types.IDOverrideLibraryPropertyOperations.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.IDOverrideLibraryPropertyOperations.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.IDOverrideLibraryPropertyOperations.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`IDOverrideLibraryProperty.operations`](bpy.types.IDOverrideLibraryProperty.md#bpy.types.IDOverrideLibraryProperty.operations "bpy.types.IDOverrideLibraryProperty.operations") |  |
