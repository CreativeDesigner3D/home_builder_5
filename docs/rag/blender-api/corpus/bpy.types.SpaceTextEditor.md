<!-- source: Blender Python API reference 5.2 / bpy.types.SpaceTextEditor.html -->

<a id="spacetexteditor-space"></a>

# SpaceTextEditor(Space)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Space`](bpy.types.Space.md#bpy.types.Space "bpy.types.Space")

<a id="bpy.types.SpaceTextEditor"></a>

### class bpy.types.SpaceTextEditor(Space)

Text editor space data

<a id="bpy.types.SpaceTextEditor.find_text"></a>

#### bpy.types.SpaceTextEditor.find_text

Text to search for with the find tool (default “”, never None)

**Type:**

str

<a id="bpy.types.SpaceTextEditor.font_size"></a>

#### bpy.types.SpaceTextEditor.font_size

Font size to use for displaying the text (in [1, 256], default 0)

**Type:**

int

<a id="bpy.types.SpaceTextEditor.margin_column"></a>

#### bpy.types.SpaceTextEditor.margin_column

Column number to show right margin at (in [0, 1024], default 0)

**Type:**

int

<a id="bpy.types.SpaceTextEditor.replace_text"></a>

#### bpy.types.SpaceTextEditor.replace_text

Text to replace selected text with using the replace tool (default “”, never None)

**Type:**

str

<a id="bpy.types.SpaceTextEditor.show_line_highlight"></a>

#### bpy.types.SpaceTextEditor.show_line_highlight

Highlight the current line (default False)

**Type:**

bool

<a id="bpy.types.SpaceTextEditor.show_line_numbers"></a>

#### bpy.types.SpaceTextEditor.show_line_numbers

Show line numbers next to the text (default False)

**Type:**

bool

<a id="bpy.types.SpaceTextEditor.show_margin"></a>

#### bpy.types.SpaceTextEditor.show_margin

Show right margin (default False)

**Type:**

bool

<a id="bpy.types.SpaceTextEditor.show_region_footer"></a>

#### bpy.types.SpaceTextEditor.show_region_footer

(default False)

**Type:**

bool

<a id="bpy.types.SpaceTextEditor.show_region_ui"></a>

#### bpy.types.SpaceTextEditor.show_region_ui

(default False)

**Type:**

bool

<a id="bpy.types.SpaceTextEditor.show_syntax_highlight"></a>

#### bpy.types.SpaceTextEditor.show_syntax_highlight

Syntax highlight for scripting (default False)

**Type:**

bool

<a id="bpy.types.SpaceTextEditor.show_word_wrap"></a>

#### bpy.types.SpaceTextEditor.show_word_wrap

Wrap words if there is not enough horizontal space (default False)

**Type:**

bool

<a id="bpy.types.SpaceTextEditor.tab_width"></a>

#### bpy.types.SpaceTextEditor.tab_width

Number of spaces to display tabs with (in [2, 8], default 0)

**Type:**

int

<a id="bpy.types.SpaceTextEditor.text"></a>

#### bpy.types.SpaceTextEditor.text

Text displayed and edited in this space

**Type:**

[`Text`](bpy.types.Text.md#bpy.types.Text "bpy.types.Text") | None

<a id="bpy.types.SpaceTextEditor.top"></a>

#### bpy.types.SpaceTextEditor.top

Top line visible (in [0, inf], default 0)

**Type:**

int

<a id="bpy.types.SpaceTextEditor.use_find_all"></a>

#### bpy.types.SpaceTextEditor.use_find_all

Search in all text data-blocks, instead of only the active one (default False)

**Type:**

bool

<a id="bpy.types.SpaceTextEditor.use_find_wrap"></a>

#### bpy.types.SpaceTextEditor.use_find_wrap

Search again from the start of the file when reaching the end (default False)

**Type:**

bool

<a id="bpy.types.SpaceTextEditor.use_live_edit"></a>

#### bpy.types.SpaceTextEditor.use_live_edit

Run Python while editing (default False)

**Type:**

bool

<a id="bpy.types.SpaceTextEditor.use_match_case"></a>

#### bpy.types.SpaceTextEditor.use_match_case

Search string is sensitive to uppercase and lowercase letters (default False)

**Type:**

bool

<a id="bpy.types.SpaceTextEditor.use_overwrite"></a>

#### bpy.types.SpaceTextEditor.use_overwrite

Overwrite characters when typing rather than inserting them (default False)

**Type:**

bool

<a id="bpy.types.SpaceTextEditor.visible_lines"></a>

#### bpy.types.SpaceTextEditor.visible_lines

Amount of lines that can be visible in current editor (in [-inf, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.SpaceTextEditor.is_syntax_highlight_supported"></a>

#### bpy.types.SpaceTextEditor.is_syntax_highlight_supported()

Returns True if the editor supports syntax highlighting for the current text data-block

**Return type:**

bool

<a id="bpy.types.SpaceTextEditor.region_location_from_cursor"></a>

#### bpy.types.SpaceTextEditor.region_location_from_cursor(line, column)

Retrieve the region position from the given line and character position

**Parameters:**

- **line** (int) – Line, Line index (in [-inf, inf])
- **column** (int) – Column, Column index (in [-inf, inf])

**Returns:**

Region coordinates (array of 2 items, in [-1, inf])

**Return type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[int]

<a id="bpy.types.SpaceTextEditor.bl_rna_get_subclass"></a>

#### classmethod bpy.types.SpaceTextEditor.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.SpaceTextEditor.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.SpaceTextEditor.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="bpy.types.SpaceTextEditor.draw_handler_add"></a>

#### classmethod bpy.types.SpaceTextEditor.draw_handler_add(callback, args, region_type, draw_type)

Add a new draw handler to this space type.
It will be called every time the specified region in the space type will be drawn.
Note: All arguments are positional only for now.

**Parameters:**

- **callback** (Callable[..., Any]) – A function that will be called when the region is drawn.
  It gets the specified arguments as input, it’s return value is ignored.
- **args** (tuple[Any, ...]) – Arguments that will be passed to the callback.
- **region_type** (str) – The region type the callback draws in; usually `WINDOW`. ([`bpy.types.Region.type`](bpy.types.Region.md#bpy.types.Region.type "bpy.types.Region.type"))
- **draw_type** (str) – Usually `POST_PIXEL` for 2D drawing and `POST_VIEW` for 3D drawing. In some cases `PRE_VIEW` can be used. `BACKDROP` can be used for backdrops in the node editor.

**Returns:**

Handler that can be removed later on.

**Return type:**

object

<a id="bpy.types.SpaceTextEditor.draw_handler_remove"></a>

#### classmethod bpy.types.SpaceTextEditor.draw_handler_remove(handler, region_type)

Remove a draw handler that was added previously.

**Parameters:**

- **handler** (object) – The draw handler that should be removed.
- **region_type** (str) – Region type the callback was added to.

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, Space.type, Space.show_locked_time, Space.show_region_header

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, Space.bl_rna_get_subclass, Space.bl_rna_get_subclass_py, Space.draw_handler_add, Space.draw_handler_remove
