<!-- source: Blender Python API reference 5.2 / bpy.types.Preferences.html -->

<a id="preferences-bpy-struct"></a>

# Preferences(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.Preferences"></a>

### class bpy.types.Preferences(bpy_struct)

Global preferences

<a id="bpy.types.Preferences.active_section"></a>

#### bpy.types.Preferences.active_section

Preferences (default `'INTERFACE'`)

**Type:**

Literal[[Preference Section Items](bpy_types_enum_items/preference_section_items.md#rna-enum-preference-section-items)]

<a id="bpy.types.Preferences.addons"></a>

#### bpy.types.Preferences.addons

(default None, readonly)

**Type:**

[`Addons`](bpy.types.Addons.md#bpy.types.Addons "bpy.types.Addons")[[`Addon`](bpy.types.Addon.md#bpy.types.Addon "bpy.types.Addon")]

<a id="bpy.types.Preferences.app_template"></a>

#### bpy.types.Preferences.app_template

(default “”, never None)

**Type:**

str

<a id="bpy.types.Preferences.apps"></a>

#### bpy.types.Preferences.apps

Preferences that work only for apps (readonly, never None)

**Type:**

[`PreferencesApps`](bpy.types.PreferencesApps.md#bpy.types.PreferencesApps "bpy.types.PreferencesApps")

<a id="bpy.types.Preferences.asset_libraries"></a>

#### bpy.types.Preferences.asset_libraries

Setup for custom and builtin asset libraries (readonly, never None)

**Type:**

[`PreferencesAssetLibraries`](bpy.types.PreferencesAssetLibraries.md#bpy.types.PreferencesAssetLibraries "bpy.types.PreferencesAssetLibraries")

<a id="bpy.types.Preferences.autoexec_paths"></a>

#### bpy.types.Preferences.autoexec_paths

(default None, readonly)

**Type:**

[`PathCompareCollection`](bpy.types.PathCompareCollection.md#bpy.types.PathCompareCollection "bpy.types.PathCompareCollection")[[`PathCompare`](bpy.types.PathCompare.md#bpy.types.PathCompare "bpy.types.PathCompare")]

<a id="bpy.types.Preferences.edit"></a>

#### bpy.types.Preferences.edit

Settings for interacting with Blender data (readonly, never None)

**Type:**

[`PreferencesEdit`](bpy.types.PreferencesEdit.md#bpy.types.PreferencesEdit "bpy.types.PreferencesEdit")

<a id="bpy.types.Preferences.experimental"></a>

#### bpy.types.Preferences.experimental

Settings for features that are still early in their development stage (readonly, never None)

**Type:**

[`PreferencesExperimental`](bpy.types.PreferencesExperimental.md#bpy.types.PreferencesExperimental "bpy.types.PreferencesExperimental")

<a id="bpy.types.Preferences.extensions"></a>

#### bpy.types.Preferences.extensions

Settings for extensions (readonly, never None)

**Type:**

[`PreferencesExtensions`](bpy.types.PreferencesExtensions.md#bpy.types.PreferencesExtensions "bpy.types.PreferencesExtensions")

<a id="bpy.types.Preferences.filepaths"></a>

#### bpy.types.Preferences.filepaths

Default paths for external files (readonly, never None)

**Type:**

[`PreferencesFilePaths`](bpy.types.PreferencesFilePaths.md#bpy.types.PreferencesFilePaths "bpy.types.PreferencesFilePaths")

<a id="bpy.types.Preferences.inputs"></a>

#### bpy.types.Preferences.inputs

Settings for input devices (readonly, never None)

**Type:**

[`PreferencesInput`](bpy.types.PreferencesInput.md#bpy.types.PreferencesInput "bpy.types.PreferencesInput")

<a id="bpy.types.Preferences.is_dirty"></a>

#### bpy.types.Preferences.is_dirty

Preferences have changed (default False)

**Type:**

bool

<a id="bpy.types.Preferences.keymap"></a>

#### bpy.types.Preferences.keymap

Shortcut setup for keyboards and other input devices (readonly, never None)

**Type:**

[`PreferencesKeymap`](bpy.types.PreferencesKeymap.md#bpy.types.PreferencesKeymap "bpy.types.PreferencesKeymap")

<a id="bpy.types.Preferences.show_hidden_ids"></a>

#### bpy.types.Preferences.show_hidden_ids

Show data-blocks with dot-prefixed names in search menus (default False)

**Type:**

bool

<a id="bpy.types.Preferences.studio_lights"></a>

#### bpy.types.Preferences.studio_lights

(default None, readonly)

**Type:**

[`StudioLights`](bpy.types.StudioLights.md#bpy.types.StudioLights "bpy.types.StudioLights")[[`StudioLight`](bpy.types.StudioLight.md#bpy.types.StudioLight "bpy.types.StudioLight")]

<a id="bpy.types.Preferences.system"></a>

#### bpy.types.Preferences.system

Graphics driver and operating system settings (readonly, never None)

**Type:**

[`PreferencesSystem`](bpy.types.PreferencesSystem.md#bpy.types.PreferencesSystem "bpy.types.PreferencesSystem")

<a id="bpy.types.Preferences.themes"></a>

#### bpy.types.Preferences.themes

(default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`Theme`](bpy.types.Theme.md#bpy.types.Theme "bpy.types.Theme")]

<a id="bpy.types.Preferences.ui_styles"></a>

#### bpy.types.Preferences.ui_styles

(default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`ThemeStyle`](bpy.types.ThemeStyle.md#bpy.types.ThemeStyle "bpy.types.ThemeStyle")]

<a id="bpy.types.Preferences.use_preferences_save"></a>

#### bpy.types.Preferences.use_preferences_save

Save preferences on exit when modified (unless factory settings have been loaded) (default True)

**Type:**

bool

<a id="bpy.types.Preferences.use_recent_searches"></a>

#### bpy.types.Preferences.use_recent_searches

Sort the recently searched items at the top (default True)

**Type:**

bool

<a id="bpy.types.Preferences.version"></a>

#### bpy.types.Preferences.version

Version of Blender the userpref.blend was saved with (array of 3 items, in [0, inf], default (0, 0, 0), readonly)

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[int]

<a id="bpy.types.Preferences.view"></a>

#### bpy.types.Preferences.view

Preferences related to viewing data (readonly, never None)

**Type:**

[`PreferencesView`](bpy.types.PreferencesView.md#bpy.types.PreferencesView "bpy.types.PreferencesView")

<a id="bpy.types.Preferences.bl_rna_get_subclass"></a>

#### classmethod bpy.types.Preferences.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.Preferences.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.Preferences.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Context.preferences`](bpy.types.Context.md#bpy.types.Context.preferences "bpy.types.Context.preferences") |  |
