<!-- source: Blender Python API reference 5.2 / bpy.ops.outliner.html -->

<a id="module-bpy.ops.outliner"></a>

# Outliner Operators

<a id="bpy.ops.outliner.action_set"></a>

### bpy.ops.outliner.action_set(*, action='')

Change the active action used

**Parameters:**

**action** (str) – Action, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.animdata_operation"></a>

### bpy.ops.outliner.animdata_operation(*, type='CLEAR_ANIMDATA')

Undocumented, consider [contributing](https://developer.blender.org/).

**Parameters:**

**type** (Literal['CLEAR_ANIMDATA', 'SET_ACT', 'CLEAR_ACT', 'REFRESH_DRIVERS', 'CLEAR_DRIVERS']) –

Animation Operation, (optional)

- `CLEAR_ANIMDATA`
  Clear Animation Data – Remove this animation data container.
- `SET_ACT`
  Set Action.
- `CLEAR_ACT`
  Unlink Action.
- `REFRESH_DRIVERS`
  Refresh Drivers.
- `CLEAR_DRIVERS`
  Clear Drivers.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.clear_filter"></a>

### bpy.ops.outliner.clear_filter()

Clear the search filter

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.collection_color_tag_set"></a>

### bpy.ops.outliner.collection_color_tag_set(*, color='NONE')

Set a color tag for the selected collections

**Parameters:**

**color** (Literal[[Collection Color Items](bpy_types_enum_items/collection_color_items.md#rna-enum-collection-color-items)]) – Color Tag, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.collection_disable"></a>

### bpy.ops.outliner.collection_disable()

Disable viewport display in the view layers

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.collection_disable_render"></a>

### bpy.ops.outliner.collection_disable_render()

Do not render this collection

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.collection_drop"></a>

### bpy.ops.outliner.collection_drop()

Drag to move to collection in Outliner

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.collection_duplicate"></a>

### bpy.ops.outliner.collection_duplicate()

Recursively duplicate the collection, all its children, objects and object data

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.collection_duplicate_linked"></a>

### bpy.ops.outliner.collection_duplicate_linked()

Recursively duplicate the collection, all its children and objects, with linked object data

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.collection_enable"></a>

### bpy.ops.outliner.collection_enable()

Enable viewport display in the view layers

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.collection_enable_render"></a>

### bpy.ops.outliner.collection_enable_render()

Render the collection

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.collection_exclude_clear"></a>

### bpy.ops.outliner.collection_exclude_clear()

Include collection in the active view layer

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.collection_exclude_set"></a>

### bpy.ops.outliner.collection_exclude_set()

Exclude collection from the active view layer

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.collection_hide"></a>

### bpy.ops.outliner.collection_hide()

Hide the collection in this view layer

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.collection_hide_inside"></a>

### bpy.ops.outliner.collection_hide_inside()

Hide all the objects and collections inside the collection

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.collection_hierarchy_delete"></a>

### bpy.ops.outliner.collection_hierarchy_delete()

Delete selected collection hierarchies

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.collection_holdout_clear"></a>

### bpy.ops.outliner.collection_holdout_clear()

Clear masking of collection in the active view layer

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.collection_holdout_set"></a>

### bpy.ops.outliner.collection_holdout_set()

Mask collection in the active view layer

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.collection_indirect_only_clear"></a>

### bpy.ops.outliner.collection_indirect_only_clear()

Clear collection contributing only indirectly in the view layer

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.collection_indirect_only_set"></a>

### bpy.ops.outliner.collection_indirect_only_set()

Set collection to only contribute indirectly (through shadows and reflections) in the view layer

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.collection_instance"></a>

### bpy.ops.outliner.collection_instance()

Instance selected collections to active scene

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.collection_isolate"></a>

### bpy.ops.outliner.collection_isolate(*, extend=False)

Hide all but this collection and its parents

**Parameters:**

**extend** (bool) – Extend, Extend current visible collections (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.collection_link"></a>

### bpy.ops.outliner.collection_link()

Link selected collections to active scene

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.collection_new"></a>

### bpy.ops.outliner.collection_new(*, nested=True)

Add a new collection inside selected collection

**Parameters:**

**nested** (bool) – Nested, Add as child of selected collection (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.collection_objects_deselect"></a>

### bpy.ops.outliner.collection_objects_deselect()

Deselect objects in collection

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.collection_objects_select"></a>

### bpy.ops.outliner.collection_objects_select()

Select objects in collection

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.collection_show"></a>

### bpy.ops.outliner.collection_show()

Show the collection in this view layer

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.collection_show_inside"></a>

### bpy.ops.outliner.collection_show_inside()

Show all the objects and collections inside the collection

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.constraint_operation"></a>

### bpy.ops.outliner.constraint_operation(*, type='ENABLE')

Undocumented, consider [contributing](https://developer.blender.org/).

**Parameters:**

**type** (Literal['ENABLE', 'DISABLE', 'DELETE']) – Constraint Operation, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.data_operation"></a>

### bpy.ops.outliner.data_operation(*, type='DEFAULT')

Undocumented, consider [contributing](https://developer.blender.org/).

**Parameters:**

**type** (Literal['DEFAULT']) – Data Operation, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.datastack_drop"></a>

### bpy.ops.outliner.datastack_drop()

Copy or reorder modifiers, constraints, and effects

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.delete"></a>

### bpy.ops.outliner.delete(*, hierarchy=False)

Delete selected objects and collections

**Parameters:**

**hierarchy** (bool) – Hierarchy, Delete child objects and collections (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.drivers_add_selected"></a>

### bpy.ops.outliner.drivers_add_selected()

Add drivers to selected items

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.drivers_delete_selected"></a>

### bpy.ops.outliner.drivers_delete_selected()

Delete drivers assigned to selected items

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.expanded_toggle"></a>

### bpy.ops.outliner.expanded_toggle()

Expand/Collapse all items

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.hide"></a>

### bpy.ops.outliner.hide()

Hide selected objects and collections

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.highlight_update"></a>

### bpy.ops.outliner.highlight_update()

Update the item highlight based on the current mouse position

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.id_copy"></a>

### bpy.ops.outliner.id_copy()

Copy the selected data-blocks to the internal clipboard

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.id_delete"></a>

### bpy.ops.outliner.id_delete()

Delete the ID under cursor

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.id_linked_relocate"></a>

### bpy.ops.outliner.id_linked_relocate()

Replace the active linked ID (and its dependencies if any) by another one, from the same or a different library

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.id_operation"></a>

### bpy.ops.outliner.id_operation(*, type='UNLINK')

General data-block management operations

**Parameters:**

**type** (Literal['UNLINK', 'LOCAL', 'SINGLE', 'DELETE', 'REMAP', 'COPY', 'PASTE', 'ADD_FAKE', 'CLEAR_FAKE', 'RENAME', 'SELECT_LINKED']) –

ID Data Operation, (optional)

- `UNLINK`
  Unlink.
- `LOCAL`
  Make Local.
- `SINGLE`
  Make Single User.
- `DELETE`
  Delete.
- `REMAP`
  Remap Users – Make all users of selected data-blocks to use instead current (clicked) one.
- `COPY`
  Copy.
- `PASTE`
  Paste.
- `ADD_FAKE`
  Add Fake User – Ensure data-block gets saved even if it isn’t in use (e.g. for motion and material libraries).
- `CLEAR_FAKE`
  Clear Fake User.
- `RENAME`
  Rename.
- `SELECT_LINKED`
  Select Linked.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.id_paste"></a>

### bpy.ops.outliner.id_paste()

Paste data-blocks from the internal clipboard

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.id_remap"></a>

### bpy.ops.outliner.id_remap(*, id_type='OBJECT', old_id=0, new_id=0)

Undocumented, consider [contributing](https://developer.blender.org/).

**Parameters:**

- **id_type** (Literal[[Id Type Items](bpy_types_enum_items/id_type_items.md#rna-enum-id-type-items)]) – ID Type, (optional)
- **old_id** (int) – Old ID, Old ID’s session uid to remap data from (in [-inf, inf], optional)
- **new_id** (int) – New ID, New ID’s session uid to remap all selected IDs’ users to (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.item_activate"></a>

### bpy.ops.outliner.item_activate(*, extend=False, extend_range=False, deselect_all=False, recurse=False)

Handle mouse clicks to select and activate items

**Parameters:**

- **extend** (bool) – Extend, Extend selection for activation (optional)
- **extend_range** (bool) – Extend Range, Select a range from active element (optional)
- **deselect_all** (bool) – Deselect On Nothing, Deselect all when nothing under the cursor (optional)
- **recurse** (bool) – Recurse, Select objects recursively from active element (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.item_drag_drop"></a>

### bpy.ops.outliner.item_drag_drop()

Drag and drop element to another place

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.item_openclose"></a>

### bpy.ops.outliner.item_openclose(*, all=False)

Toggle whether item under cursor is open or closed

**Parameters:**

**all** (bool) – All, Close or open all items (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.item_rename"></a>

### bpy.ops.outliner.item_rename(*, use_active=False)

Rename the active element

**Parameters:**

**use_active** (bool) – Use Active, Rename the active item, rather than the one the mouse is over (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.keyingset_add_selected"></a>

### bpy.ops.outliner.keyingset_add_selected()

Add selected items (blue-gray rows) to active Keying Set

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.keyingset_remove_selected"></a>

### bpy.ops.outliner.keyingset_remove_selected()

Remove selected items (blue-gray rows) from active Keying Set

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.lib_operation"></a>

### bpy.ops.outliner.lib_operation(*, type='DELETE')

Undocumented, consider [contributing](https://developer.blender.org/).

**Parameters:**

**type** (Literal['DELETE', 'RELOCATE', 'RELOAD']) –

Library Operation, (optional)

- `DELETE`
  Delete – Delete this library and all its items.
- `RELOCATE`
  Relocate – Select a new path for this library, and reload all its data.
- `RELOAD`
  Reload – Reload all data from this library.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.lib_relocate"></a>

### bpy.ops.outliner.lib_relocate()

Relocate the library under cursor

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.liboverride_operation"></a>

### bpy.ops.outliner.liboverride_operation(*, type='OVERRIDE_LIBRARY_CREATE_HIERARCHY', selection_set='SELECTED')

Create, reset or clear library override hierarchies

**Parameters:**

- **type** (Literal['OVERRIDE_LIBRARY_CREATE_HIERARCHY', 'OVERRIDE_LIBRARY_RESET', 'OVERRIDE_LIBRARY_CLEAR_SINGLE']) –

  Library Override Operation, (optional)

  - `OVERRIDE_LIBRARY_CREATE_HIERARCHY`
    Make – Create a local override of the selected linked data-blocks, and their hierarchy of dependencies.
  - `OVERRIDE_LIBRARY_RESET`
    Reset – Reset the selected local overrides to their linked references values.
  - `OVERRIDE_LIBRARY_CLEAR_SINGLE`
    Clear – Delete the selected local overrides and relink their usages to the linked data-blocks if possible, else reset them and mark them as non editable.
- **selection_set** (Literal['SELECTED', 'CONTENT', 'SELECTED_AND_CONTENT']) –

  Selection Set, Over which part of the tree items to apply the operation (optional)

  - `SELECTED`
    Selected – Apply the operation over selected data-blocks only.
  - `CONTENT`
    Content – Apply the operation over content of the selected items only (the data-blocks in their sub-tree).
  - `SELECTED_AND_CONTENT`
    Selected & Content – Apply the operation over selected data-blocks and all their dependencies.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.liboverride_property_remove"></a>

### bpy.ops.outliner.liboverride_property_remove()

Remove the selected library override properties, and reset the relevant data to the linked reference values

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.liboverride_troubleshoot_operation"></a>

### bpy.ops.outliner.liboverride_troubleshoot_operation(*, type='OVERRIDE_LIBRARY_RESYNC_HIERARCHY', selection_set='SELECTED')

Advanced operations over library override to help fix broken hierarchies

**Parameters:**

- **type** (Literal['OVERRIDE_LIBRARY_RESYNC_HIERARCHY', 'OVERRIDE_LIBRARY_RESYNC_HIERARCHY_ENFORCE', 'OVERRIDE_LIBRARY_DELETE_HIERARCHY']) –

  Library Override Troubleshoot Operation, (optional)

  - `OVERRIDE_LIBRARY_RESYNC_HIERARCHY`
    Resync – Rebuild the selected local overrides from their linked references, as well as their hierarchies of dependencies.
  - `OVERRIDE_LIBRARY_RESYNC_HIERARCHY_ENFORCE`
    Resync Enforce – Rebuild the selected local overrides from their linked references, as well as their hierarchies of dependencies, enforcing these hierarchies to match the linked data (i.e. ignoring existing overrides on data-blocks pointer properties).
  - `OVERRIDE_LIBRARY_DELETE_HIERARCHY`
    Delete – Delete the selected local overrides (including their hierarchies of override dependencies) and relink their usages to the linked data-blocks.
- **selection_set** (Literal['SELECTED', 'CONTENT', 'SELECTED_AND_CONTENT']) –

  Selection Set, Over which part of the tree items to apply the operation (optional)

  - `SELECTED`
    Selected – Apply the operation over selected data-blocks only.
  - `CONTENT`
    Content – Apply the operation over content of the selected items only (the data-blocks in their sub-tree).
  - `SELECTED_AND_CONTENT`
    Selected & Content – Apply the operation over selected data-blocks and all their dependencies.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.material_drop"></a>

### bpy.ops.outliner.material_drop()

Drag material to object in Outliner

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.modifier_operation"></a>

### bpy.ops.outliner.modifier_operation(*, type='APPLY')

Undocumented, consider [contributing](https://developer.blender.org/).

**Parameters:**

**type** (Literal['APPLY', 'DELETE', 'TOGVIS', 'TOGREN']) – Modifier Operation, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.object_operation"></a>

### bpy.ops.outliner.object_operation(*, type='SELECT')

Undocumented, consider [contributing](https://developer.blender.org/).

**Parameters:**

**type** (Literal['SELECT', 'DESELECT', 'SELECT_HIERARCHY', 'REMAP', 'RENAME']) –

Object Operation, (optional)

- `SELECT`
  Select.
- `DESELECT`
  Deselect.
- `SELECT_HIERARCHY`
  Select Hierarchy.
- `REMAP`
  Remap Users – Make all users of selected data-blocks to use instead a new chosen one.
- `RENAME`
  Rename.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.operation"></a>

### bpy.ops.outliner.operation()

Context menu for item operations

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.orphans_manage"></a>

### bpy.ops.outliner.orphans_manage()

Open a window to manage unused data

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.orphans_purge"></a>

### bpy.ops.outliner.orphans_purge(*, do_local_ids=True, do_linked_ids=True, do_recursive=True)

Clear all orphaned data-blocks without any users from the file

**Parameters:**

- **do_local_ids** (bool) – Local Data-blocks, Include unused local data-blocks into deletion (optional)
- **do_linked_ids** (bool) – Linked Data-blocks, Include unused linked data-blocks into deletion (optional)
- **do_recursive** (bool) – Recursive Delete, Recursively check for indirectly unused data-blocks, ensuring that no orphaned data-blocks remain after execution (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.parent_clear"></a>

### bpy.ops.outliner.parent_clear()

Drag to clear parent in Outliner

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.parent_drop"></a>

### bpy.ops.outliner.parent_drop()

Drag to parent in Outliner

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.scene_drop"></a>

### bpy.ops.outliner.scene_drop()

Drag object to scene in Outliner

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.scene_operation"></a>

### bpy.ops.outliner.scene_operation(*, type='DELETE')

Context menu for scene operations

**Parameters:**

**type** (Literal['DELETE']) – Scene Operation, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.scroll_page"></a>

### bpy.ops.outliner.scroll_page(*, up=False)

Scroll page up or down

**Parameters:**

**up** (bool) – Up, Scroll up one page (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.select_all"></a>

### bpy.ops.outliner.select_all(*, action='TOGGLE')

Toggle the Outliner selection of items

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

<a id="bpy.ops.outliner.select_box"></a>

### bpy.ops.outliner.select_box(*, tweak=False, xmin=0, xmax=0, ymin=0, ymax=0, wait_for_input=True, mode='SET')

Use box selection to select tree elements

**Parameters:**

- **tweak** (bool) – Tweak, Tweak gesture from empty space for box selection (optional)
- **xmin** (int) – X Min, (in [-inf, inf], optional)
- **xmax** (int) – X Max, (in [-inf, inf], optional)
- **ymin** (int) – Y Min, (in [-inf, inf], optional)
- **ymax** (int) – Y Max, (in [-inf, inf], optional)
- **wait_for_input** (bool) – Wait for Input, (optional)
- **mode** (Literal['SET', 'ADD', 'SUB']) –

  Mode, (optional)

  - `SET`
    Set – Set a new selection.
  - `ADD`
    Extend – Extend existing selection.
  - `SUB`
    Subtract – Subtract existing selection.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.select_walk"></a>

### bpy.ops.outliner.select_walk(*, direction='UP', extend=False, toggle_all=False)

Use walk navigation to select tree elements

**Parameters:**

- **direction** (Literal['UP', 'DOWN', 'LEFT', 'RIGHT']) – Walk Direction, Select/Deselect element in this direction (optional)
- **extend** (bool) – Extend, Extend selection on walk (optional)
- **toggle_all** (bool) – Toggle All, Toggle open/close hierarchy (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.show_active"></a>

### bpy.ops.outliner.show_active()

Open up the tree and adjust the view so that the active object is shown centered

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.show_hierarchy"></a>

### bpy.ops.outliner.show_hierarchy()

Open all object entries and close all others

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.show_one_level"></a>

### bpy.ops.outliner.show_one_level(*, open=True)

Expand/collapse all entries by one level

**Parameters:**

**open** (bool) – Open, Expand all entries one level deep (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.start_filter"></a>

### bpy.ops.outliner.start_filter()

Start entering filter text

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.outliner.unhide_all"></a>

### bpy.ops.outliner.unhide_all()

Unhide all objects and collections

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]
