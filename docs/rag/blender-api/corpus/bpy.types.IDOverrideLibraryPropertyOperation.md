<!-- source: Blender Python API reference 5.2 / bpy.types.IDOverrideLibraryPropertyOperation.html -->

<a id="idoverridelibrarypropertyoperation-bpy-struct"></a>

# IDOverrideLibraryPropertyOperation(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.IDOverrideLibraryPropertyOperation"></a>

### class bpy.types.IDOverrideLibraryPropertyOperation(bpy_struct)

Description of an override operation over an overridden property

<a id="bpy.types.IDOverrideLibraryPropertyOperation.flag"></a>

#### bpy.types.IDOverrideLibraryPropertyOperation.flag

Status flags (default set(), readonly)

- `MANDATORY`
  Mandatory – For templates, prevents the user from removing predefined operation (NOT USED).
- `LOCKED`
  Locked – Prevents the user from modifying that override operation (NOT USED).
- `IDPOINTER_MATCH_REFERENCE`
  Match Reference – The ID pointer overridden by this operation is expected to match the reference hierarchy.
- `IDPOINTER_ITEM_USE_ID`
  ID Item Use ID Pointer – RNA collections of IDs only, the reference to the item also uses the ID pointer itself, not only its name.

**Type:**

set[Literal[‘MANDATORY’, ‘LOCKED’, ‘IDPOINTER_MATCH_REFERENCE’, ‘IDPOINTER_ITEM_USE_ID’]]

<a id="bpy.types.IDOverrideLibraryPropertyOperation.label"></a>

#### bpy.types.IDOverrideLibraryPropertyOperation.label

UI label to display in dedicated view of the Outliner, in place of the actual UI widget to edit the value (default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.IDOverrideLibraryPropertyOperation.operation"></a>

#### bpy.types.IDOverrideLibraryPropertyOperation.operation

What override operation is performed (default `'REPLACE'`, readonly)

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

**Type:**

Literal[‘NOOP’, ‘REPLACE’, ‘DIFF_ADD’, ‘DIFF_SUB’, ‘FACT_MULTIPLY’, ‘INSERT_AFTER’, ‘INSERT_BEFORE’, ‘CUSTOM’]

<a id="bpy.types.IDOverrideLibraryPropertyOperation.subitem_local_id"></a>

#### bpy.types.IDOverrideLibraryPropertyOperation.subitem_local_id

Collection of IDs only, used to disambiguate between potential IDs with same name from different libraries (readonly)

**Type:**

[`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID") | None

<a id="bpy.types.IDOverrideLibraryPropertyOperation.subitem_local_index"></a>

#### bpy.types.IDOverrideLibraryPropertyOperation.subitem_local_index

Used to handle changes into collection (in [-1, inf], default -1, readonly)

**Type:**

int

<a id="bpy.types.IDOverrideLibraryPropertyOperation.subitem_local_name"></a>

#### bpy.types.IDOverrideLibraryPropertyOperation.subitem_local_name

Used to handle changes into collection (default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.IDOverrideLibraryPropertyOperation.subitem_reference_id"></a>

#### bpy.types.IDOverrideLibraryPropertyOperation.subitem_reference_id

Collection of IDs only, used to disambiguate between potential IDs with same name from different libraries (readonly)

**Type:**

[`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID") | None

<a id="bpy.types.IDOverrideLibraryPropertyOperation.subitem_reference_index"></a>

#### bpy.types.IDOverrideLibraryPropertyOperation.subitem_reference_index

Used to handle changes into collection (in [-1, inf], default -1, readonly)

**Type:**

int

<a id="bpy.types.IDOverrideLibraryPropertyOperation.subitem_reference_name"></a>

#### bpy.types.IDOverrideLibraryPropertyOperation.subitem_reference_name

Used to handle changes into collection (default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.IDOverrideLibraryPropertyOperation.tooltip"></a>

#### bpy.types.IDOverrideLibraryPropertyOperation.tooltip

UI tooltip to display in dedicated view of the Outliner, when the label itself cannot provide all required information (default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.IDOverrideLibraryPropertyOperation.bl_rna_get_subclass"></a>

#### classmethod bpy.types.IDOverrideLibraryPropertyOperation.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.IDOverrideLibraryPropertyOperation.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.IDOverrideLibraryPropertyOperation.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`IDOverrideLibraryProperty.operations`](bpy.types.IDOverrideLibraryProperty.md#bpy.types.IDOverrideLibraryProperty.operations "bpy.types.IDOverrideLibraryProperty.operations") - [`IDOverrideLibraryPropertyOperations.add`](bpy.types.IDOverrideLibraryPropertyOperations.md#bpy.types.IDOverrideLibraryPropertyOperations.add "bpy.types.IDOverrideLibraryPropertyOperations.add") | - [`IDOverrideLibraryPropertyOperations.remove`](bpy.types.IDOverrideLibraryPropertyOperations.md#bpy.types.IDOverrideLibraryPropertyOperations.remove "bpy.types.IDOverrideLibraryPropertyOperations.remove") |
