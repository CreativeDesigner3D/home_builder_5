<!-- source: Blender Python API reference 5.2 / bpy.types.WorkSpace.html -->

<a id="workspace-id"></a>

# WorkSpace(ID)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")

<a id="bpy.types.WorkSpace"></a>

### class bpy.types.WorkSpace(ID)

Workspace data-block, defining the working environment for the user

<a id="bpy.types.WorkSpace.active_addon"></a>

#### bpy.types.WorkSpace.active_addon

Active Add-on in the Workspace Add-ons filter (in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.WorkSpace.asset_library_reference"></a>

#### bpy.types.WorkSpace.asset_library_reference

Active asset library to show in the UI, not used by the Asset Browser (which has its own active asset library) (default `'ALL'`)

- `ALL`
  All Libraries – Show assets from all of the listed asset libraries.
- `LOCAL`
  Current File – Show the assets currently available in this Blender session.
- `ESSENTIALS`
  Essentials – Show basic building blocks and utilities coming with Blender.
- `ONLINE_ESSENTIALS`
  Online Essentials – Show additional building blocks and utilities available online.
- `CUSTOM`
  Custom – Show assets from the asset libraries configured in the Preferences.

**Type:**

Literal[‘ALL’, ‘LOCAL’, ‘ESSENTIALS’, ‘ONLINE_ESSENTIALS’, ‘CUSTOM’]

<a id="bpy.types.WorkSpace.object_mode"></a>

#### bpy.types.WorkSpace.object_mode

Switch to this object mode when activating the workspace (default `'OBJECT'`)

**Type:**

Literal[[Workspace Object Mode Items](bpy_types_enum_items/workspace_object_mode_items.md#rna-enum-workspace-object-mode-items)]

<a id="bpy.types.WorkSpace.owner_ids"></a>

#### bpy.types.WorkSpace.owner_ids

(default None, readonly)

**Type:**

[`wmOwnerIDs`](bpy.types.wmOwnerIDs.md#bpy.types.wmOwnerIDs "bpy.types.wmOwnerIDs")[[`wmOwnerID`](bpy.types.wmOwnerID.md#bpy.types.wmOwnerID "bpy.types.wmOwnerID")]

<a id="bpy.types.WorkSpace.screens"></a>

#### bpy.types.WorkSpace.screens

Screen layouts of a workspace (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`Screen`](bpy.types.Screen.md#bpy.types.Screen "bpy.types.Screen")]

<a id="bpy.types.WorkSpace.sequencer_scene"></a>

#### bpy.types.WorkSpace.sequencer_scene

**Type:**

[`Scene`](bpy.types.Scene.md#bpy.types.Scene "bpy.types.Scene") | None

<a id="bpy.types.WorkSpace.tools"></a>

#### bpy.types.WorkSpace.tools

(default None, readonly)

**Type:**

[`wmTools`](bpy.types.wmTools.md#bpy.types.wmTools "bpy.types.wmTools")[[`WorkSpaceTool`](bpy.types.WorkSpaceTool.md#bpy.types.WorkSpaceTool "bpy.types.WorkSpaceTool")]

<a id="bpy.types.WorkSpace.use_filter_by_owner"></a>

#### bpy.types.WorkSpace.use_filter_by_owner

Filter the UI by tags (default False)

**Type:**

bool

<a id="bpy.types.WorkSpace.use_pin_scene"></a>

#### bpy.types.WorkSpace.use_pin_scene

Remember the last used scene for the workspace and switch to it whenever this workspace is activated again (default False)

**Type:**

bool

<a id="bpy.types.WorkSpace.use_scene_time_sync"></a>

#### bpy.types.WorkSpace.use_scene_time_sync

Set the active scene and time based on the current scene strip (default False)

**Type:**

bool

<a id="bpy.types.WorkSpace.status_text_set_internal"></a>

#### classmethod bpy.types.WorkSpace.status_text_set_internal(text)

Set the status bar text, typically key shortcuts for modal operators

**Parameters:**

**text** (str) – Text, New string for the status bar, None clears the text

<a id="bpy.types.WorkSpace.status_text_set"></a>

#### bpy.types.WorkSpace.status_text_set(text)

Set the status text or None to clear,
When text is a function, this will be called with the (header, context) arguments.

**Parameters:**

**text** (str | None | Callable[[[`Header`](bpy.types.Header.md#bpy.types.Header "bpy.types.Header"), [`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context")], None]) – Status text to display, `None` to clear, or a callable
to install as the status bar’s draw function.

<a id="bpy.types.WorkSpace.bl_rna_get_subclass"></a>

#### classmethod bpy.types.WorkSpace.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.WorkSpace.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.WorkSpace.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`BlendData.workspaces`](bpy.types.BlendData.md#bpy.types.BlendData.workspaces "bpy.types.BlendData.workspaces") - [`Context.workspace`](bpy.types.Context.md#bpy.types.Context.workspace "bpy.types.Context.workspace") | - [`Window.workspace`](bpy.types.Window.md#bpy.types.Window.workspace "bpy.types.Window.workspace") |
