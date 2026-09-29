<!-- source: Blender Python API reference 5.2 / bpy.types.Text.html -->

<a id="text-id"></a>

# Text(ID)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")

<a id="bpy.types.Text"></a>

### class bpy.types.Text(ID)

Text data-block referencing an external or packed text file

<a id="bpy.types.Text.current_character"></a>

#### bpy.types.Text.current_character

Index of current character in current line, and also start index of character in selection if one exists (in [0, inf], default 0)

**Type:**

int

<a id="bpy.types.Text.current_line"></a>

#### bpy.types.Text.current_line

Current line, and start line of selection if one exists (readonly, never None)

**Type:**

[`TextLine`](bpy.types.TextLine.md#bpy.types.TextLine "bpy.types.TextLine")

<a id="bpy.types.Text.current_line_index"></a>

#### bpy.types.Text.current_line_index

Index of current TextLine in TextLine collection (in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.Text.filepath"></a>

#### bpy.types.Text.filepath

Filename of the text file (default “”, never None)

**Type:**

str

<a id="bpy.types.Text.indentation"></a>

#### bpy.types.Text.indentation

Use tabs or spaces for indentation (default `'TABS'`)

- `TABS`
  Tabs – Indent using tabs.
- `SPACES`
  Spaces – Indent using spaces.

**Type:**

Literal[‘TABS’, ‘SPACES’]

<a id="bpy.types.Text.is_dirty"></a>

#### bpy.types.Text.is_dirty

Text file has been edited since last save (default False, readonly)

**Type:**

bool

<a id="bpy.types.Text.is_in_memory"></a>

#### bpy.types.Text.is_in_memory

Text file is in memory, without a corresponding file on disk (default False, readonly)

**Type:**

bool

<a id="bpy.types.Text.is_modified"></a>

#### bpy.types.Text.is_modified

Text file on disk is different than the one in memory (default False, readonly)

**Type:**

bool

<a id="bpy.types.Text.lines"></a>

#### bpy.types.Text.lines

Lines of text (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`TextLine`](bpy.types.TextLine.md#bpy.types.TextLine "bpy.types.TextLine")]

<a id="bpy.types.Text.select_end_character"></a>

#### bpy.types.Text.select_end_character

Index of character after end of selection in the selection end line (in [0, inf], default 0)

**Type:**

int

<a id="bpy.types.Text.select_end_line"></a>

#### bpy.types.Text.select_end_line

End line of selection (readonly, never None)

**Type:**

[`TextLine`](bpy.types.TextLine.md#bpy.types.TextLine "bpy.types.TextLine")

<a id="bpy.types.Text.select_end_line_index"></a>

#### bpy.types.Text.select_end_line_index

Index of last TextLine in selection (in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.Text.use_module"></a>

#### bpy.types.Text.use_module

Run this text as a Python script on loading (default False)

**Type:**

bool

<a id="bpy.types.Text.clear"></a>

#### bpy.types.Text.clear()

clear the text block

<a id="bpy.types.Text.write"></a>

#### bpy.types.Text.write(text)

write text at the cursor location and advance to the end of the text block

**Parameters:**

**text** (str) – New text for this data-block (never None)

<a id="bpy.types.Text.from_string"></a>

#### bpy.types.Text.from_string(text)

Replace text with this string.

**Parameters:**

**text** (str) – (never None)

<a id="bpy.types.Text.as_string"></a>

#### bpy.types.Text.as_string()

Return the text as a string

**Returns:**

(never None)

**Return type:**

str

<a id="bpy.types.Text.is_syntax_highlight_supported"></a>

#### bpy.types.Text.is_syntax_highlight_supported()

Returns True if the editor supports syntax highlighting for the current text data-block

**Return type:**

bool

<a id="bpy.types.Text.select_set"></a>

#### bpy.types.Text.select_set(line_start, char_start, line_end, char_end)

Set selection range by line and character index

**Parameters:**

- **line_start** (int) – Start Line, (in [-inf, inf])
- **char_start** (int) – Start Character, (in [-inf, inf])
- **line_end** (int) – End Line, (in [-inf, inf])
- **char_end** (int) – End Character, (in [-inf, inf])

<a id="bpy.types.Text.cursor_set"></a>

#### bpy.types.Text.cursor_set(line, *, character=0, select=False)

Set cursor by line and (optionally) character index

**Parameters:**

- **line** (int) – Line, (in [0, inf])
- **character** (int) – Character, (in [0, inf], optional)
- **select** (bool) – Select when moving the cursor (optional)

<a id="bpy.types.Text.as_module"></a>

#### bpy.types.Text.as_module()

Compile and execute this text block as a Python module.

**Returns:**

A new module containing the text block’s executed contents.

**Return type:**

ModuleType

<a id="bpy.types.Text.bl_rna_get_subclass"></a>

#### classmethod bpy.types.Text.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.Text.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.Text.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="bpy.types.Text.region_as_string"></a>

#### bpy.types.Text.region_as_string(*, range=None)

**Parameters:**

**range** (tuple[tuple[int, int], tuple[int, int]] | None) – The region of text to be returned, defaulting to the selection when no range is passed.
Each int pair represents a line and column: ((start_line, start_column), (end_line, end_column))
The values match Python’s slicing logic (negative values count backwards from the end, the end value is not inclusive).

**Returns:**

The specified region as a string.

**Return type:**

str

<a id="bpy.types.Text.region_from_string"></a>

#### bpy.types.Text.region_from_string(body, /, *, range=None)

**Parameters:**

- **body** (str) – The text to be inserted.
- **range** (tuple[tuple[int, int], tuple[int, int]] | None) – The region of text to be returned, defaulting to the selection when no range is passed.
  Each int pair represents a line and column: ((start_line, start_column), (end_line, end_column))
  The values match Python’s slicing logic (negative values count backwards from the end, the end value is not inclusive).

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, ID.name, ID.name_full, ID.id_type, ID.session_uid, ID.is_evaluated, ID.original, ID.users, ID.use_fake_user, ID.use_extra_user, ID.is_embedded_data, ID.is_linked_packed, ID.is_missing, ID.is_runtime_data, ID.is_editable, ID.tag, ID.is_library_indirect, ID.library, ID.library_weak_reference, ID.asset_data, ID.override_library, ID.preview

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, ID.bl_system_properties_get, ID.rename, ID.evaluated_get, ID.copy, ID.asset_mark, ID.asset_clear, ID.asset_generate_preview, ID.override_create, ID.override_hierarchy_create, ID.user_clear, ID.user_remap, ID.make_local, ID.user_of_id, ID.animation_data_create, ID.animation_data_clear, ID.update_tag, ID.preview_ensure, ID.bl_rna_get_subclass, ID.bl_rna_get_subclass_py

<a id="references"></a>

## References

|  |  |
| --- | --- |
| - `bpy.context.edit_text` - [`BlendData.texts`](bpy.types.BlendData.md#bpy.types.BlendData.texts "bpy.types.BlendData.texts") - [`BlendDataTexts.load`](bpy.types.BlendDataTexts.md#bpy.types.BlendDataTexts.load "bpy.types.BlendDataTexts.load") - [`BlendDataTexts.new`](bpy.types.BlendDataTexts.md#bpy.types.BlendDataTexts.new "bpy.types.BlendDataTexts.new") - [`BlendDataTexts.remove`](bpy.types.BlendDataTexts.md#bpy.types.BlendDataTexts.remove "bpy.types.BlendDataTexts.remove") - [`Camera.custom_shader`](bpy.types.Camera.md#bpy.types.Camera.custom_shader "bpy.types.Camera.custom_shader") - [`FreestyleModuleSettings.script`](bpy.types.FreestyleModuleSettings.md#bpy.types.FreestyleModuleSettings.script "bpy.types.FreestyleModuleSettings.script") | - [`NodeFrame.text`](bpy.types.NodeFrame.md#bpy.types.NodeFrame.text "bpy.types.NodeFrame.text") - [`NodeSocketText.default_value`](bpy.types.NodeSocketText.md#bpy.types.NodeSocketText.default_value "bpy.types.NodeSocketText.default_value") - [`NodeTreeInterfaceSocketText.default_value`](bpy.types.NodeTreeInterfaceSocketText.md#bpy.types.NodeTreeInterfaceSocketText.default_value "bpy.types.NodeTreeInterfaceSocketText.default_value") - [`ShaderNodeScript.script`](bpy.types.ShaderNodeScript.md#bpy.types.ShaderNodeScript.script "bpy.types.ShaderNodeScript.script") - [`ShaderNodeTexIES.ies`](bpy.types.ShaderNodeTexIES.md#bpy.types.ShaderNodeTexIES.ies "bpy.types.ShaderNodeTexIES.ies") - [`SpaceTextEditor.text`](bpy.types.SpaceTextEditor.md#bpy.types.SpaceTextEditor.text "bpy.types.SpaceTextEditor.text") |
