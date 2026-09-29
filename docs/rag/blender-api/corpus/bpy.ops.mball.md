<!-- source: Blender Python API reference 5.2 / bpy.ops.mball.html -->

<a id="module-bpy.ops.mball"></a>

# Mball Operators

<a id="bpy.ops.mball.delete_metaelems"></a>

### bpy.ops.mball.delete_metaelems(*, confirm=True)

Delete selected metaball element(s)

**Parameters:**

**confirm** (bool) – Confirm, Prompt for confirmation (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mball.duplicate_metaelems"></a>

### bpy.ops.mball.duplicate_metaelems()

Duplicate selected metaball element(s)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mball.duplicate_move"></a>

### bpy.ops.mball.duplicate_move(*, MBALL_OT_duplicate_metaelems={}, TRANSFORM_OT_translate={})

Make copies of the selected metaball elements and move them

**Parameters:**

- **MBALL_OT_duplicate_metaelems** (dict[str, Any]) – Duplicate Metaball Elements, Duplicate selected metaball element(s) (optional, [`bpy.ops.mball.duplicate_metaelems()`](#bpy.ops.mball.duplicate_metaelems "bpy.ops.mball.duplicate_metaelems") keyword arguments)
- **TRANSFORM_OT_translate** (dict[str, Any]) – Move, Move selected items (optional, [`bpy.ops.transform.translate()`](bpy.ops.transform.md#bpy.ops.transform.translate "bpy.ops.transform.translate") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mball.hide_metaelems"></a>

### bpy.ops.mball.hide_metaelems(*, unselected=False)

Hide (un)selected metaball element(s)

**Parameters:**

**unselected** (bool) – Unselected, Hide unselected rather than selected (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mball.reveal_metaelems"></a>

### bpy.ops.mball.reveal_metaelems(*, select=True)

Reveal all hidden metaball elements

**Parameters:**

**select** (bool) – Select, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mball.select_all"></a>

### bpy.ops.mball.select_all(*, action='TOGGLE')

Change selection of all metaball elements

**Parameters:**

**action** (Literal['TOGGLE', 'SELECT', 'DESELECT', 'INVERT']) –

Action, Selection action to execute (optional)

- `TOGGLE`
  Toggle – Toggle selection for all elements.
- `SELECT`
  Select – Select all elements.
- `DESELECT`
  Deselect – Deselect all elements.
- `INVERT`
  Invert – Invert selection of all elements.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mball.select_random_metaelems"></a>

### bpy.ops.mball.select_random_metaelems(*, ratio=0.5, seed=0, action='SELECT')

Randomly select metaball elements

**Parameters:**

- **ratio** (float) – Ratio, Portion of items to select randomly (in [0, 1], optional)
- **seed** (int) – Random Seed, Seed for the random number generator (in [0, inf], optional)
- **action** (Literal['SELECT', 'DESELECT']) –

  Action, Selection action to execute (optional)

  - `SELECT`
    Select – Select all elements.
  - `DESELECT`
    Deselect – Deselect all elements.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.mball.select_similar"></a>

### bpy.ops.mball.select_similar(*, type='TYPE', threshold=0.1)

Select similar metaballs by property types

**Parameters:**

- **type** (Literal['TYPE', 'RADIUS', 'STIFFNESS', 'ROTATION']) – Type, (optional)
- **threshold** (float) – Threshold, (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]
