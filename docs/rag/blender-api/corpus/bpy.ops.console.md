<!-- source: Blender Python API reference 5.2 / bpy.ops.console.html -->

<a id="module-bpy.ops.console"></a>

# Console Operators

<a id="bpy.ops.console.autocomplete"></a>

### bpy.ops.console.autocomplete()

Evaluate the namespace up until the cursor and give a list of options or complete the name if there is only one

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/console.py:61](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/console.py#L61)

<a id="bpy.ops.console.banner"></a>

### bpy.ops.console.banner()

Print a message when the terminal initializes

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/console.py:104](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/console.py#L104)

<a id="bpy.ops.console.clear"></a>

### bpy.ops.console.clear(*, scrollback=True, history=False)

Clear text by type

**Parameters:**

- **scrollback** (bool) – Scrollback, Clear the scrollback history (optional)
- **history** (bool) – History, Clear the command history (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.console.clear_line"></a>

### bpy.ops.console.clear_line()

Clear the line and store in history

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.console.copy"></a>

### bpy.ops.console.copy(*, delete=False)

Copy selected text to clipboard

**Parameters:**

**delete** (bool) – Delete Selection, Whether to delete the selection after copying (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.console.copy_as_script"></a>

### bpy.ops.console.copy_as_script()

Copy the console contents for use in a script

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/console.py:82](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/console.py#L82)

<a id="bpy.ops.console.delete"></a>

### bpy.ops.console.delete(*, type='NEXT_CHARACTER')

Delete text by cursor position

**Parameters:**

**type** (Literal['NEXT_CHARACTER', 'PREVIOUS_CHARACTER', 'NEXT_WORD', 'PREVIOUS_WORD']) – Type, Which part of the text to delete (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.console.execute"></a>

### bpy.ops.console.execute(*, interactive=False)

Execute the current console line as a Python expression

**Parameters:**

**interactive** (bool) – interactive, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/console.py:38](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/console.py#L38)

<a id="bpy.ops.console.history_append"></a>

### bpy.ops.console.history_append(*, text='', current_character=0, remove_duplicates=False)

Append history at cursor position

**Parameters:**

- **text** (str) – Text, Text to insert at the cursor position (optional, never None)
- **current_character** (int) – Cursor, The index of the cursor (in [0, inf], optional)
- **remove_duplicates** (bool) – Remove Duplicates, Remove duplicate items in the history (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.console.history_cycle"></a>

### bpy.ops.console.history_cycle(*, reverse=False)

Cycle through history

**Parameters:**

**reverse** (bool) – Reverse, Reverse cycle history (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.console.indent"></a>

### bpy.ops.console.indent()

Add 4 spaces at line beginning

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.console.indent_or_autocomplete"></a>

### bpy.ops.console.indent_or_autocomplete()

Indent selected text or autocomplete

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.console.insert"></a>

### bpy.ops.console.insert(*, text='')

Insert text at cursor position

**Parameters:**

**text** (str) – Text, Text to insert at the cursor position (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.console.language"></a>

### bpy.ops.console.language(*, language='')

Set the current language for this console

**Parameters:**

**language** (str) – Language, (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/console.py:136](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/console.py#L136)

<a id="bpy.ops.console.move"></a>

### bpy.ops.console.move(*, type='LINE_BEGIN', select=False)

Move cursor position

**Parameters:**

- **type** (Literal['LINE_BEGIN', 'LINE_END', 'PREVIOUS_CHARACTER', 'NEXT_CHARACTER', 'PREVIOUS_WORD', 'NEXT_WORD']) – Type, Where to move cursor to (optional)
- **select** (bool) – Select, Whether to select while moving (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.console.paste"></a>

### bpy.ops.console.paste(*, selection=False)

Paste text from clipboard

**Parameters:**

**selection** (bool) – Selection, Paste text selected elsewhere rather than copied (X11/Wayland only) (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.console.scrollback_append"></a>

### bpy.ops.console.scrollback_append(*, text='', type='OUTPUT')

Append scrollback text by type

**Parameters:**

- **text** (str) – Text, Text to insert at the cursor position (optional, never None)
- **type** (Literal['OUTPUT', 'INPUT', 'INFO', 'ERROR']) – Type, Console output type (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.console.select_all"></a>

### bpy.ops.console.select_all()

Select all the text

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.console.select_set"></a>

### bpy.ops.console.select_set()

Set the console selection

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.console.select_word"></a>

### bpy.ops.console.select_word()

Select word at cursor position

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.console.unindent"></a>

### bpy.ops.console.unindent()

Delete 4 spaces from line beginning

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]
