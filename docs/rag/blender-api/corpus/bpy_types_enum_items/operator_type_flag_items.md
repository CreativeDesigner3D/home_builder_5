<!-- source: Blender Python API reference 5.2 / bpy_types_enum_items/operator_type_flag_items.html -->

<a id="operator-type-flag-items"></a>

# Operator Type Flag Items

**REGISTER:**

Register.

Display in the info window and support the redo toolbar panel.

**UNDO:**

Undo.

Push an undo event when the operator returns `FINISHED` (needed for operator redo, mandatory if the operator modifies Blender data).

**UNDO_GROUPED:**

Grouped Undo.

Push a single undo event for repeated instances of this operator.

**BLOCKING:**

Blocking.

Block anything else from using the cursor.

**MACRO:**

Macro.

Use to check if an operator is a macro.

**GRAB_CURSOR:**

Grab Pointer.

Use so the operator grabs the mouse focus, enables wrapping when continuous grab is enabled.

**GRAB_CURSOR_X:**

Grab Pointer X.

Grab, only warping the X axis.

**GRAB_CURSOR_Y:**

Grab Pointer Y.

Grab, only warping the Y axis.

**DEPENDS_ON_CURSOR:**

Depends on Cursor.

The initial cursor location is used, when running from a menus or buttons the user is prompted to place the cursor before beginning the operation.

**PRESET:**

Preset.

Display a preset button with the operators settings.

**INTERNAL:**

Internal.

Removes the operator from search results.

**MODAL_PRIORITY:**

Modal Priority.

Handle events before other modal operators without this option. Use with caution, do not modify data that other modal operators assume is unchanged during their operation..
