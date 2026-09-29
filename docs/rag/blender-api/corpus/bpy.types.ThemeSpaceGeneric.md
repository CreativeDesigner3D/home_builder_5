<!-- source: Blender Python API reference 5.2 / bpy.types.ThemeSpaceGeneric.html -->

<a id="themespacegeneric-bpy-struct"></a>

# ThemeSpaceGeneric(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.ThemeSpaceGeneric"></a>

### class bpy.types.ThemeSpaceGeneric(bpy_struct)

<a id="bpy.types.ThemeSpaceGeneric.back"></a>

#### bpy.types.ThemeSpaceGeneric.back

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeSpaceGeneric.header"></a>

#### bpy.types.ThemeSpaceGeneric.header

(array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.ThemeSpaceGeneric.header_text"></a>

#### bpy.types.ThemeSpaceGeneric.header_text

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeSpaceGeneric.header_text_hi"></a>

#### bpy.types.ThemeSpaceGeneric.header_text_hi

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeSpaceGeneric.text"></a>

#### bpy.types.ThemeSpaceGeneric.text

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeSpaceGeneric.text_hi"></a>

#### bpy.types.ThemeSpaceGeneric.text_hi

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeSpaceGeneric.title"></a>

#### bpy.types.ThemeSpaceGeneric.title

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeSpaceGeneric.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ThemeSpaceGeneric.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ThemeSpaceGeneric.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ThemeSpaceGeneric.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`ThemeClipEditor.space`](bpy.types.ThemeClipEditor.md#bpy.types.ThemeClipEditor.space "bpy.types.ThemeClipEditor.space") - [`ThemeConsole.space`](bpy.types.ThemeConsole.md#bpy.types.ThemeConsole.space "bpy.types.ThemeConsole.space") - [`ThemeDopeSheet.space`](bpy.types.ThemeDopeSheet.md#bpy.types.ThemeDopeSheet.space "bpy.types.ThemeDopeSheet.space") - [`ThemeFileBrowser.space`](bpy.types.ThemeFileBrowser.md#bpy.types.ThemeFileBrowser.space "bpy.types.ThemeFileBrowser.space") - [`ThemeGraphEditor.space`](bpy.types.ThemeGraphEditor.md#bpy.types.ThemeGraphEditor.space "bpy.types.ThemeGraphEditor.space") - [`ThemeImageEditor.space`](bpy.types.ThemeImageEditor.md#bpy.types.ThemeImageEditor.space "bpy.types.ThemeImageEditor.space") - [`ThemeInfo.space`](bpy.types.ThemeInfo.md#bpy.types.ThemeInfo.space "bpy.types.ThemeInfo.space") - [`ThemeNLAEditor.space`](bpy.types.ThemeNLAEditor.md#bpy.types.ThemeNLAEditor.space "bpy.types.ThemeNLAEditor.space") - [`ThemeNodeEditor.space`](bpy.types.ThemeNodeEditor.md#bpy.types.ThemeNodeEditor.space "bpy.types.ThemeNodeEditor.space") | - [`ThemeOutliner.space`](bpy.types.ThemeOutliner.md#bpy.types.ThemeOutliner.space "bpy.types.ThemeOutliner.space") - [`ThemePreferences.space`](bpy.types.ThemePreferences.md#bpy.types.ThemePreferences.space "bpy.types.ThemePreferences.space") - [`ThemeProperties.space`](bpy.types.ThemeProperties.md#bpy.types.ThemeProperties.space "bpy.types.ThemeProperties.space") - [`ThemeSequenceEditor.space`](bpy.types.ThemeSequenceEditor.md#bpy.types.ThemeSequenceEditor.space "bpy.types.ThemeSequenceEditor.space") - [`ThemeSpreadsheet.space`](bpy.types.ThemeSpreadsheet.md#bpy.types.ThemeSpreadsheet.space "bpy.types.ThemeSpreadsheet.space") - [`ThemeStatusBar.space`](bpy.types.ThemeStatusBar.md#bpy.types.ThemeStatusBar.space "bpy.types.ThemeStatusBar.space") - [`ThemeTextEditor.space`](bpy.types.ThemeTextEditor.md#bpy.types.ThemeTextEditor.space "bpy.types.ThemeTextEditor.space") - [`ThemeTopBar.space`](bpy.types.ThemeTopBar.md#bpy.types.ThemeTopBar.space "bpy.types.ThemeTopBar.space") |
