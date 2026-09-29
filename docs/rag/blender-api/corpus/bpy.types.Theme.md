<!-- source: Blender Python API reference 5.2 / bpy.types.Theme.html -->

<a id="theme-bpy-struct"></a>

# Theme(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.Theme"></a>

### class bpy.types.Theme(bpy_struct)

User interface styling and color settings

<a id="bpy.types.Theme.bone_color_sets"></a>

#### bpy.types.Theme.bone_color_sets

(default None, readonly, never None)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`ThemeBoneColorSet`](bpy.types.ThemeBoneColorSet.md#bpy.types.ThemeBoneColorSet "bpy.types.ThemeBoneColorSet")]

<a id="bpy.types.Theme.clip_editor"></a>

#### bpy.types.Theme.clip_editor

(readonly, never None)

**Type:**

[`ThemeClipEditor`](bpy.types.ThemeClipEditor.md#bpy.types.ThemeClipEditor "bpy.types.ThemeClipEditor")

<a id="bpy.types.Theme.collection_color"></a>

#### bpy.types.Theme.collection_color

(default None, readonly, never None)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`ThemeCollectionColor`](bpy.types.ThemeCollectionColor.md#bpy.types.ThemeCollectionColor "bpy.types.ThemeCollectionColor")]

<a id="bpy.types.Theme.common"></a>

#### bpy.types.Theme.common

Theme properties shared by different editors (readonly, never None)

**Type:**

[`ThemeCommon`](bpy.types.ThemeCommon.md#bpy.types.ThemeCommon "bpy.types.ThemeCommon")

<a id="bpy.types.Theme.console"></a>

#### bpy.types.Theme.console

(readonly, never None)

**Type:**

[`ThemeConsole`](bpy.types.ThemeConsole.md#bpy.types.ThemeConsole "bpy.types.ThemeConsole")

<a id="bpy.types.Theme.dopesheet_editor"></a>

#### bpy.types.Theme.dopesheet_editor

(readonly, never None)

**Type:**

[`ThemeDopeSheet`](bpy.types.ThemeDopeSheet.md#bpy.types.ThemeDopeSheet "bpy.types.ThemeDopeSheet")

<a id="bpy.types.Theme.file_browser"></a>

#### bpy.types.Theme.file_browser

(readonly, never None)

**Type:**

[`ThemeFileBrowser`](bpy.types.ThemeFileBrowser.md#bpy.types.ThemeFileBrowser "bpy.types.ThemeFileBrowser")

<a id="bpy.types.Theme.filepath"></a>

#### bpy.types.Theme.filepath

The path to the preset loaded into this theme (if any) (default “”, never None)

**Type:**

str

<a id="bpy.types.Theme.graph_editor"></a>

#### bpy.types.Theme.graph_editor

(readonly, never None)

**Type:**

[`ThemeGraphEditor`](bpy.types.ThemeGraphEditor.md#bpy.types.ThemeGraphEditor "bpy.types.ThemeGraphEditor")

<a id="bpy.types.Theme.image_editor"></a>

#### bpy.types.Theme.image_editor

(readonly, never None)

**Type:**

[`ThemeImageEditor`](bpy.types.ThemeImageEditor.md#bpy.types.ThemeImageEditor "bpy.types.ThemeImageEditor")

<a id="bpy.types.Theme.info"></a>

#### bpy.types.Theme.info

(readonly, never None)

**Type:**

[`ThemeInfo`](bpy.types.ThemeInfo.md#bpy.types.ThemeInfo "bpy.types.ThemeInfo")

<a id="bpy.types.Theme.name"></a>

#### bpy.types.Theme.name

Name of the theme (default “Default”, never None)

**Type:**

str

<a id="bpy.types.Theme.nla_editor"></a>

#### bpy.types.Theme.nla_editor

(readonly, never None)

**Type:**

[`ThemeNLAEditor`](bpy.types.ThemeNLAEditor.md#bpy.types.ThemeNLAEditor "bpy.types.ThemeNLAEditor")

<a id="bpy.types.Theme.node_editor"></a>

#### bpy.types.Theme.node_editor

(readonly, never None)

**Type:**

[`ThemeNodeEditor`](bpy.types.ThemeNodeEditor.md#bpy.types.ThemeNodeEditor "bpy.types.ThemeNodeEditor")

<a id="bpy.types.Theme.outliner"></a>

#### bpy.types.Theme.outliner

(readonly, never None)

**Type:**

[`ThemeOutliner`](bpy.types.ThemeOutliner.md#bpy.types.ThemeOutliner "bpy.types.ThemeOutliner")

<a id="bpy.types.Theme.preferences"></a>

#### bpy.types.Theme.preferences

(readonly, never None)

**Type:**

[`ThemePreferences`](bpy.types.ThemePreferences.md#bpy.types.ThemePreferences "bpy.types.ThemePreferences")

<a id="bpy.types.Theme.properties"></a>

#### bpy.types.Theme.properties

(readonly, never None)

**Type:**

[`ThemeProperties`](bpy.types.ThemeProperties.md#bpy.types.ThemeProperties "bpy.types.ThemeProperties")

<a id="bpy.types.Theme.regions"></a>

#### bpy.types.Theme.regions

Theme properties for common editor regions (readonly, never None)

**Type:**

[`ThemeRegions`](bpy.types.ThemeRegions.md#bpy.types.ThemeRegions "bpy.types.ThemeRegions")

<a id="bpy.types.Theme.sequence_editor"></a>

#### bpy.types.Theme.sequence_editor

(readonly, never None)

**Type:**

[`ThemeSequenceEditor`](bpy.types.ThemeSequenceEditor.md#bpy.types.ThemeSequenceEditor "bpy.types.ThemeSequenceEditor")

<a id="bpy.types.Theme.spreadsheet"></a>

#### bpy.types.Theme.spreadsheet

(readonly, never None)

**Type:**

[`ThemeSpreadsheet`](bpy.types.ThemeSpreadsheet.md#bpy.types.ThemeSpreadsheet "bpy.types.ThemeSpreadsheet")

<a id="bpy.types.Theme.statusbar"></a>

#### bpy.types.Theme.statusbar

(readonly, never None)

**Type:**

[`ThemeStatusBar`](bpy.types.ThemeStatusBar.md#bpy.types.ThemeStatusBar "bpy.types.ThemeStatusBar")

<a id="bpy.types.Theme.strip_color"></a>

#### bpy.types.Theme.strip_color

(default None, readonly, never None)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`ThemeStripColor`](bpy.types.ThemeStripColor.md#bpy.types.ThemeStripColor "bpy.types.ThemeStripColor")]

<a id="bpy.types.Theme.text_editor"></a>

#### bpy.types.Theme.text_editor

(readonly, never None)

**Type:**

[`ThemeTextEditor`](bpy.types.ThemeTextEditor.md#bpy.types.ThemeTextEditor "bpy.types.ThemeTextEditor")

<a id="bpy.types.Theme.theme_area"></a>

#### bpy.types.Theme.theme_area

(default `'USER_INTERFACE'`)

**Type:**

Literal[‘USER_INTERFACE’, ‘STYLE’, ‘REGIONS’, ‘COMMON’, ‘VIEW_3D’, ‘DOPESHEET_EDITOR’, ‘FILE_BROWSER’, ‘GRAPH_EDITOR’, ‘IMAGE_EDITOR’, ‘INFO’, ‘CLIP_EDITOR’, ‘NODE_EDITOR’, ‘NLA_EDITOR’, ‘OUTLINER’, ‘PREFERENCES’, ‘PROPERTIES’, ‘CONSOLE’, ‘SPREADSHEET’, ‘STATUSBAR’, ‘TEXT_EDITOR’, ‘TOPBAR’, ‘SEQUENCE_EDITOR’, ‘BONE_COLOR_SETS’]

<a id="bpy.types.Theme.topbar"></a>

#### bpy.types.Theme.topbar

(readonly, never None)

**Type:**

[`ThemeTopBar`](bpy.types.ThemeTopBar.md#bpy.types.ThemeTopBar "bpy.types.ThemeTopBar")

<a id="bpy.types.Theme.user_interface"></a>

#### bpy.types.Theme.user_interface

(readonly, never None)

**Type:**

[`ThemeUserInterface`](bpy.types.ThemeUserInterface.md#bpy.types.ThemeUserInterface "bpy.types.ThemeUserInterface")

<a id="bpy.types.Theme.view_3d"></a>

#### bpy.types.Theme.view_3d

(readonly, never None)

**Type:**

[`ThemeView3D`](bpy.types.ThemeView3D.md#bpy.types.ThemeView3D "bpy.types.ThemeView3D")

<a id="bpy.types.Theme.bl_rna_get_subclass"></a>

#### classmethod bpy.types.Theme.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.Theme.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.Theme.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Preferences.themes`](bpy.types.Preferences.md#bpy.types.Preferences.themes "bpy.types.Preferences.themes") |  |
