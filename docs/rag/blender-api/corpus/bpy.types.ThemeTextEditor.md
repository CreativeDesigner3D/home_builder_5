<!-- source: Blender Python API reference 5.2 / bpy.types.ThemeTextEditor.html -->

<a id="themetexteditor-bpy-struct"></a>

# ThemeTextEditor(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.ThemeTextEditor"></a>

### class bpy.types.ThemeTextEditor(bpy_struct)

Theme settings for the Text Editor

<a id="bpy.types.ThemeTextEditor.cursor"></a>

#### bpy.types.ThemeTextEditor.cursor

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeTextEditor.line_numbers"></a>

#### bpy.types.ThemeTextEditor.line_numbers

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeTextEditor.line_numbers_background"></a>

#### bpy.types.ThemeTextEditor.line_numbers_background

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeTextEditor.selected_text"></a>

#### bpy.types.ThemeTextEditor.selected_text

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeTextEditor.space"></a>

#### bpy.types.ThemeTextEditor.space

Settings for space (readonly, never None)

**Type:**

[`ThemeSpaceGeneric`](bpy.types.ThemeSpaceGeneric.md#bpy.types.ThemeSpaceGeneric "bpy.types.ThemeSpaceGeneric")

<a id="bpy.types.ThemeTextEditor.syntax_builtin"></a>

#### bpy.types.ThemeTextEditor.syntax_builtin

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeTextEditor.syntax_comment"></a>

#### bpy.types.ThemeTextEditor.syntax_comment

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeTextEditor.syntax_numbers"></a>

#### bpy.types.ThemeTextEditor.syntax_numbers

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeTextEditor.syntax_preprocessor"></a>

#### bpy.types.ThemeTextEditor.syntax_preprocessor

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeTextEditor.syntax_reserved"></a>

#### bpy.types.ThemeTextEditor.syntax_reserved

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeTextEditor.syntax_special"></a>

#### bpy.types.ThemeTextEditor.syntax_special

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeTextEditor.syntax_string"></a>

#### bpy.types.ThemeTextEditor.syntax_string

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeTextEditor.syntax_symbols"></a>

#### bpy.types.ThemeTextEditor.syntax_symbols

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeTextEditor.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ThemeTextEditor.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ThemeTextEditor.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ThemeTextEditor.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Theme.text_editor`](bpy.types.Theme.md#bpy.types.Theme.text_editor "bpy.types.Theme.text_editor") |  |
