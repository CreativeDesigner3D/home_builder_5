<!-- source: Blender Python API reference 5.2 / bpy.ops.ui.html -->

<a id="module-bpy.ops.ui"></a>

# Ui Operators

<a id="bpy.ops.ui.assign_default_button"></a>

### bpy.ops.ui.assign_default_button()

Set this property’s current value as the new default

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.ui.button_execute"></a>

### bpy.ops.ui.button_execute(*, skip_depressed=False)

Presses active button

**Parameters:**

**skip_depressed** (bool) – Skip Depressed, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.ui.button_string_clear"></a>

### bpy.ops.ui.button_string_clear()

Unsets the text of the active button

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.ui.copy_as_driver_button"></a>

### bpy.ops.ui.copy_as_driver_button()

Create a new driver with this property as input, and copy it to the internal clipboard. Use Paste Driver to add it to the target property, or Paste Driver Variables to extend an existing driver

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.ui.copy_data_path_button"></a>

### bpy.ops.ui.copy_data_path_button(*, full_path=False)

Copy the RNA data path for this property to the clipboard

**Parameters:**

**full_path** (bool) – full_path, Copy full data path (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.ui.copy_driver_to_selected_button"></a>

### bpy.ops.ui.copy_driver_to_selected_button(*, all=False)

Copy the property’s driver from the active item to the same property of all selected items, if the same property exists

**Parameters:**

**all** (bool) – All, Copy to selected the drivers of all elements of the array (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.ui.copy_python_command_button"></a>

### bpy.ops.ui.copy_python_command_button()

Copy the Python command matching this button

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.ui.copy_to_selected_button"></a>

### bpy.ops.ui.copy_to_selected_button(*, all=True)

Copy the property’s value from the active item to the same property of all selected items if the same property exists

**Parameters:**

**all** (bool) – All, Copy to selected all elements of the array (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.ui.drop_color"></a>

### bpy.ops.ui.drop_color(*, color=(0.0, 0.0, 0.0, 0.0), gamma=False, has_alpha=False)

Drop colors to buttons

**Parameters:**

- **color** (Sequence[float]) – Color, Source color (array of 4 items, in [0, inf], optional)
- **gamma** (bool) – Gamma Corrected, The source color is gamma corrected (optional)
- **has_alpha** (bool) – Has Alpha, The source color contains an Alpha component (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.ui.drop_material"></a>

### bpy.ops.ui.drop_material(*, session_uid=0)

Drag material to Material slots in Properties

**Parameters:**

**session_uid** (int) – Session UID, Session UID of the data-block to use by the operator (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.ui.drop_name"></a>

### bpy.ops.ui.drop_name(*, string='')

Drop name to button

**Parameters:**

**string** (str) – String, The string value to drop into the button (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.ui.editsource"></a>

### bpy.ops.ui.editsource()

Edit UI source code of the active button

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.ui.eyedropper_bone"></a>

### bpy.ops.ui.eyedropper_bone()

Sample a bone from the 3D View or the Outliner to store in a property

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.ui.eyedropper_color"></a>

### bpy.ops.ui.eyedropper_color(*, prop_data_path='')

Sample a color from the Blender window to store in a property

**Parameters:**

**prop_data_path** (str) – Data Path, Path of property to be set with the depth (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.ui.eyedropper_colorramp"></a>

### bpy.ops.ui.eyedropper_colorramp()

Sample a color band

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.ui.eyedropper_colorramp_point"></a>

### bpy.ops.ui.eyedropper_colorramp_point()

Point-sample a color band

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.ui.eyedropper_depth"></a>

### bpy.ops.ui.eyedropper_depth(*, prop_data_path='')

Sample depth from the 3D view

**Parameters:**

**prop_data_path** (str) – Data Path, Path of property to be set with the depth (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.ui.eyedropper_driver"></a>

### bpy.ops.ui.eyedropper_driver(*, mapping_type='SINGLE_MANY')

Pick a property to use as a driver target

**Parameters:**

**mapping_type** (Literal['SINGLE_MANY', 'DIRECT', 'MATCH', 'NONE_ALL', 'NONE_SINGLE']) –

Mapping Type, Method used to match target and driven properties (optional)

- `SINGLE_MANY`
  All from Target – Drive all components of this property using the target picked.
- `DIRECT`
  Single from Target – Drive this component of this property using the target picked.
- `MATCH`
  Match Indices – Create drivers for each pair of corresponding elements.
- `NONE_ALL`
  Manually Create Later – Create drivers for all properties without assigning any targets yet.
- `NONE_SINGLE`
  Manually Create Later (Single) – Create driver for this property only and without assigning any targets yet.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.ui.eyedropper_grease_pencil_color"></a>

### bpy.ops.ui.eyedropper_grease_pencil_color(*, mode='MATERIAL', material_mode='STROKE')

Sample a color from the Blender Window and create Grease Pencil material

**Parameters:**

- **mode** (Literal['MATERIAL', 'PALETTE', 'BRUSH']) – Mode, (optional)
- **material_mode** (Literal['STROKE', 'FILL', 'BOTH']) – Material Mode, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.ui.eyedropper_id"></a>

### bpy.ops.ui.eyedropper_id()

Sample a data-block from the 3D View to store in a property

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.ui.jump_to_target_button"></a>

### bpy.ops.ui.jump_to_target_button()

Switch to the target object or bone

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.ui.list_start_filter"></a>

### bpy.ops.ui.list_start_filter()

Start entering filter text for the list in focus

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.ui.override_add_button"></a>

### bpy.ops.ui.override_add_button(*, all=True)

Create an override operation

**Parameters:**

**all** (bool) – All, Add overrides for all elements of the array (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.ui.override_idtemplate_clear"></a>

### bpy.ops.ui.override_idtemplate_clear()

Delete the selected local override and relink its usages to the linked data-block if possible, else reset it and mark it as non editable

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.ui.override_idtemplate_make"></a>

### bpy.ops.ui.override_idtemplate_make()

Create a local override of the selected linked data-block, and its hierarchy of dependencies

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.ui.override_idtemplate_reset"></a>

### bpy.ops.ui.override_idtemplate_reset()

Reset the selected local override to its linked reference values

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.ui.override_remove_button"></a>

### bpy.ops.ui.override_remove_button(*, all=True)

Remove an override operation

**Parameters:**

**all** (bool) – All, Reset to default values all elements of the array (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.ui.reloadtranslation"></a>

### bpy.ops.ui.reloadtranslation()

Force a full reload of UI translation

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.ui.reset_default_button"></a>

### bpy.ops.ui.reset_default_button(*, all=True)

Reset this property’s value to its default value

**Parameters:**

**all** (bool) – All, Reset to default values all elements of the array (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.ui.unset_property_button"></a>

### bpy.ops.ui.unset_property_button()

Clear the property and use default or generated value in operators

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.ui.view_drop"></a>

### bpy.ops.ui.view_drop()

Drag and drop onto a data-set or item within the data-set

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.ui.view_item_delete"></a>

### bpy.ops.ui.view_item_delete()

Delete selected list item

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.ui.view_item_focus"></a>

### bpy.ops.ui.view_item_focus()

Bring active item into focus by scrolling the view

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.ui.view_item_navigate"></a>

### bpy.ops.ui.view_item_navigate(*, direction='UP')

Walk and select view items in given direction

**Parameters:**

**direction** (Literal['UP', 'DOWN', 'LEFT', 'RIGHT']) –

Navigation Direction, Direction in which to navigate and select next element. (optional)

- `UP`
  Up – Select item above the active.
- `DOWN`
  Down – Select item below the active.
- `LEFT`
  Left – Collapse or walk towards left of the active item.
- `RIGHT`
  Right – Uncollapse or walk towards right of the active item.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.ui.view_item_rename"></a>

### bpy.ops.ui.view_item_rename()

Rename the active item in the data-set view

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.ui.view_item_select"></a>

### bpy.ops.ui.view_item_select(*, wait_to_deselect_others=False, use_select_on_click=False, mouse_x=0, mouse_y=0, extend=False, range_select=False)

Activate selected view item

**Parameters:**

- **wait_to_deselect_others** (bool) – Wait to Deselect Others, (optional)
- **use_select_on_click** (bool) – Act on Click, Instead of selecting on mouse press, wait to see if there’s drag event. Otherwise select on mouse release (optional)
- **mouse_x** (int) – Mouse X, (in [-inf, inf], optional)
- **mouse_y** (int) – Mouse Y, (in [-inf, inf], optional)
- **extend** (bool) – extend, Extend Selection (optional)
- **range_select** (bool) – Range Select, Select all between clicked and active items (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.ui.view_scroll"></a>

### bpy.ops.ui.view_scroll()

Undocumented, consider [contributing](https://developer.blender.org/).

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.ui.view_start_filter"></a>

### bpy.ops.ui.view_start_filter()

Start entering filter text for the data-set in focus

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]
