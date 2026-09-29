<!-- source: Blender Python API reference 5.2 / bpy.types.Screen.html -->

<a id="screen-id"></a>

# Screen(ID)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")

<a id="bpy.types.Screen"></a>

### class bpy.types.Screen(ID)

Screen data-block, defining the layout of areas in a window

<a id="bpy.types.Screen.areas"></a>

#### bpy.types.Screen.areas

Areas the screen is subdivided into (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`Area`](bpy.types.Area.md#bpy.types.Area "bpy.types.Area")]

<a id="bpy.types.Screen.is_animation_playing"></a>

#### bpy.types.Screen.is_animation_playing

Animation playback is active (default False, readonly)

**Type:**

bool

<a id="bpy.types.Screen.is_scrubbing"></a>

#### bpy.types.Screen.is_scrubbing

True when the user is scrubbing through time (default False, readonly)

**Type:**

bool

<a id="bpy.types.Screen.is_temporary"></a>

#### bpy.types.Screen.is_temporary

(default False, readonly)

**Type:**

bool

<a id="bpy.types.Screen.show_fullscreen"></a>

#### bpy.types.Screen.show_fullscreen

An area is maximized, filling this screen (default False, readonly)

**Type:**

bool

<a id="bpy.types.Screen.show_statusbar"></a>

#### bpy.types.Screen.show_statusbar

Show status bar (default True)

**Type:**

bool

<a id="bpy.types.Screen.use_follow"></a>

#### bpy.types.Screen.use_follow

Follow current frame in editors (default False)

**Type:**

bool

<a id="bpy.types.Screen.use_play_3d_editors"></a>

#### bpy.types.Screen.use_play_3d_editors

(default False)

**Type:**

bool

<a id="bpy.types.Screen.use_play_animation_editors"></a>

#### bpy.types.Screen.use_play_animation_editors

(default False)

**Type:**

bool

<a id="bpy.types.Screen.use_play_clip_editors"></a>

#### bpy.types.Screen.use_play_clip_editors

(default False)

**Type:**

bool

<a id="bpy.types.Screen.use_play_image_editors"></a>

#### bpy.types.Screen.use_play_image_editors

(default False)

**Type:**

bool

<a id="bpy.types.Screen.use_play_node_editors"></a>

#### bpy.types.Screen.use_play_node_editors

(default False)

**Type:**

bool

<a id="bpy.types.Screen.use_play_properties_editors"></a>

#### bpy.types.Screen.use_play_properties_editors

(default False)

**Type:**

bool

<a id="bpy.types.Screen.use_play_sequence_editors"></a>

#### bpy.types.Screen.use_play_sequence_editors

(default False)

**Type:**

bool

<a id="bpy.types.Screen.use_play_spreadsheet_editors"></a>

#### bpy.types.Screen.use_play_spreadsheet_editors

(default False)

**Type:**

bool

<a id="bpy.types.Screen.use_play_top_left_3d_editor"></a>

#### bpy.types.Screen.use_play_top_left_3d_editor

(default False)

**Type:**

bool

<a id="bpy.types.Screen.statusbar_info"></a>

#### bpy.types.Screen.statusbar_info()

statusbar_info

**Returns:**

Status Bar Info, (never None)

**Return type:**

str

<a id="bpy.types.Screen.bl_rna_get_subclass"></a>

#### classmethod bpy.types.Screen.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.Screen.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.Screen.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

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
| - [`BlendData.screens`](bpy.types.BlendData.md#bpy.types.BlendData.screens "bpy.types.BlendData.screens") - [`Context.screen`](bpy.types.Context.md#bpy.types.Context.screen "bpy.types.Context.screen") | - [`Window.screen`](bpy.types.Window.md#bpy.types.Window.screen "bpy.types.Window.screen") - [`WorkSpace.screens`](bpy.types.WorkSpace.md#bpy.types.WorkSpace.screens "bpy.types.WorkSpace.screens") |
