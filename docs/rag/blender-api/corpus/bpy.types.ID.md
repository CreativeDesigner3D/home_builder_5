<!-- source: Blender Python API reference 5.2 / bpy.types.ID.html -->

<a id="id-bpy-struct"></a>

# ID(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

Subclasses

- [Action(ID)](bpy.types.Action.md)
- [Annotation(ID)](bpy.types.Annotation.md)
- [Armature(ID)](bpy.types.Armature.md)
- [Brush(ID)](bpy.types.Brush.md)
- [CacheFile(ID)](bpy.types.CacheFile.md)
- [Camera(ID)](bpy.types.Camera.md)
- [Collection(ID)](bpy.types.Collection.md)
- [Curve(ID)](bpy.types.Curve.md)
- [Curves(ID)](bpy.types.Curves.md)
- [FreestyleLineStyle(ID)](bpy.types.FreestyleLineStyle.md)
- [GreasePencil(ID)](bpy.types.GreasePencil.md)
- [Image(ID)](bpy.types.Image.md)
- [Key(ID)](bpy.types.Key.md)
- [Lattice(ID)](bpy.types.Lattice.md)
- [Library(ID)](bpy.types.Library.md)
- [Light(ID)](bpy.types.Light.md)
- [LightProbe(ID)](bpy.types.LightProbe.md)
- [Mask(ID)](bpy.types.Mask.md)
- [Material(ID)](bpy.types.Material.md)
- [Mesh(ID)](bpy.types.Mesh.md)
- [MetaBall(ID)](bpy.types.MetaBall.md)
- [MovieClip(ID)](bpy.types.MovieClip.md)
- [NodeTree(ID)](bpy.types.NodeTree.md)
- [Object(ID)](bpy.types.Object.md)
- [PaintCurve(ID)](bpy.types.PaintCurve.md)
- [Palette(ID)](bpy.types.Palette.md)
- [ParticleSettings(ID)](bpy.types.ParticleSettings.md)
- [PointCloud(ID)](bpy.types.PointCloud.md)
- [Scene(ID)](bpy.types.Scene.md)
- [Screen(ID)](bpy.types.Screen.md)
- [Sound(ID)](bpy.types.Sound.md)
- [Speaker(ID)](bpy.types.Speaker.md)
- [Text(ID)](bpy.types.Text.md)
- [Texture(ID)](bpy.types.Texture.md)
- [VectorFont(ID)](bpy.types.VectorFont.md)
- [Volume(ID)](bpy.types.Volume.md)
- [WindowManager(ID)](bpy.types.WindowManager.md)
- [WorkSpace(ID)](bpy.types.WorkSpace.md)
- [World(ID)](bpy.types.World.md)

<a id="bpy.types.ID"></a>

### class bpy.types.ID(bpy_struct)

Base type for data-blocks, defining a unique name, linking from other libraries and garbage collection

<a id="bpy.types.ID.asset_data"></a>

#### bpy.types.ID.asset_data

Additional data for an asset data-block

**Type:**

[`AssetMetaData`](bpy.types.AssetMetaData.md#bpy.types.AssetMetaData "bpy.types.AssetMetaData") | None

<a id="bpy.types.ID.id_type"></a>

#### bpy.types.ID.id_type

Type identifier of this data-block (default `'ACTION'`, readonly)

**Type:**

Literal[[Id Type Items](bpy_types_enum_items/id_type_items.md#rna-enum-id-type-items)]

<a id="bpy.types.ID.is_editable"></a>

#### bpy.types.ID.is_editable

This data-block is editable in the user interface. Linked data-blocks are not editable, except if they were loaded as editable assets. (default False, readonly)

**Type:**

bool

<a id="bpy.types.ID.is_embedded_data"></a>

#### bpy.types.ID.is_embedded_data

This data-block is not an independent one, but is actually a sub-data of another ID (typical example: root node trees or master collections) (default False, readonly)

**Type:**

bool

<a id="bpy.types.ID.is_evaluated"></a>

#### bpy.types.ID.is_evaluated

Whether this ID is runtime-only, evaluated data-block, or actual data from .blend file (default False, readonly)

**Type:**

bool

<a id="bpy.types.ID.is_library_indirect"></a>

#### bpy.types.ID.is_library_indirect

Is this ID block linked indirectly (default False, readonly)

**Type:**

bool

<a id="bpy.types.ID.is_linked_packed"></a>

#### bpy.types.ID.is_linked_packed

This data-block is linked and packed into the .blend file (default False, readonly)

**Type:**

bool

<a id="bpy.types.ID.is_missing"></a>

#### bpy.types.ID.is_missing

This data-block is a place-holder for missing linked data (i.e. it is [an override of] a linked data that could not be found anymore) (default False, readonly)

**Type:**

bool

<a id="bpy.types.ID.is_runtime_data"></a>

#### bpy.types.ID.is_runtime_data

This data-block is runtime data, i.e. it won’t be saved in .blend file. Note that e.g. evaluated IDs are always runtime, so this value is only editable for data-blocks in Main data-base. (default False)

**Type:**

bool

<a id="bpy.types.ID.library"></a>

#### bpy.types.ID.library

Library file the data-block is linked from (readonly)

**Type:**

[`Library`](bpy.types.Library.md#bpy.types.Library "bpy.types.Library") | None

<a id="bpy.types.ID.library_weak_reference"></a>

#### bpy.types.ID.library_weak_reference

Weak reference to a data-block in another library .blend file (used to re-use already appended data instead of appending new copies) (readonly)

**Type:**

[`LibraryWeakReference`](bpy.types.LibraryWeakReference.md#bpy.types.LibraryWeakReference "bpy.types.LibraryWeakReference") | None

<a id="bpy.types.ID.name"></a>

#### bpy.types.ID.name

Unique data-block ID name (within a same type and library) (default “”, never None)

**Type:**

str

<a id="bpy.types.ID.name_full"></a>

#### bpy.types.ID.name_full

Unique data-block ID name, including library one if any (default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.ID.original"></a>

#### bpy.types.ID.original

Actual data-block from .blend file (Main database) that generated that evaluated one (readonly)

**Type:**

[`ID`](#bpy.types.ID "bpy.types.ID") | None

<a id="bpy.types.ID.override_library"></a>

#### bpy.types.ID.override_library

Library override data (readonly)

**Type:**

[`IDOverrideLibrary`](bpy.types.IDOverrideLibrary.md#bpy.types.IDOverrideLibrary "bpy.types.IDOverrideLibrary") | None

<a id="bpy.types.ID.preview"></a>

#### bpy.types.ID.preview

Preview image and icon of this data-block (always None if not supported for this type of data) (readonly)

**Type:**

[`ImagePreview`](bpy.types.ImagePreview.md#bpy.types.ImagePreview "bpy.types.ImagePreview") | None

<a id="bpy.types.ID.session_uid"></a>

#### bpy.types.ID.session_uid

A session-wide unique identifier for the data block that remains the same across renames and internal reallocations, unchanged when reloading the file (in [-inf, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.ID.tag"></a>

#### bpy.types.ID.tag

Tools can use this to tag data for their own purposes (initial state is undefined) (default False)

**Type:**

bool

<a id="bpy.types.ID.use_extra_user"></a>

#### bpy.types.ID.use_extra_user

Indicates whether an extra user is set or not (mainly for internal/debug usages) (default False)

**Type:**

bool

<a id="bpy.types.ID.use_fake_user"></a>

#### bpy.types.ID.use_fake_user

Save this data-block even if it has no users (default False)

**Type:**

bool

<a id="bpy.types.ID.users"></a>

#### bpy.types.ID.users

Number of times this data-block is referenced (in [0, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.ID.bl_system_properties_get"></a>

#### bpy.types.ID.bl_system_properties_get(*, do_create=False)

DEBUG ONLY. Internal access to runtime-defined RNA data storage, intended solely for testing and debugging purposes. Do not access it in regular scripting work, and in particular, do not assume that it contains writable data

**Parameters:**

**do_create** (bool) – Ensure that system properties are created if they do not exist yet (optional)

**Returns:**

The system properties root container, or None if there are no system properties stored in this data yet, and its creation was not requested

**Return type:**

[`PropertyGroup`](bpy.types.PropertyGroup.md#bpy.types.PropertyGroup "bpy.types.PropertyGroup")

<a id="bpy.types.ID.rename"></a>

#### bpy.types.ID.rename(name, *, mode='NEVER')

More refined handling in case the new name collides with another ID’s name

**Parameters:**

- **name** (str) – New name to rename the ID to, if empty will re-use the current ID name (never None)
- **mode** (Literal['NEVER', 'ALWAYS', 'SAME_ROOT']) –

  How to handle name collision, in case the requested new name is already used by another ID of the same type (optional)

  - `NEVER`
    Never Rename – Never rename an existing ID whose name would conflict, the currently renamed ID will get a numeric suffix appended to its new name.
  - `ALWAYS`
    Always Rename – Always rename an existing ID whose name would conflict, ensuring that the currently renamed ID will get requested name.
  - `SAME_ROOT`
    Rename If Same Root – Only rename an existing ID whose name would conflict if its name root (everything besides the numerical suffix) is the same as the existing name of the currently renamed ID.

**Returns:**

How did the renaming of the data-block went on

- `UNCHANGED`
  Unchanged – The ID was not renamed, e.g. because it is already named as requested.
- `UNCHANGED_COLLISION`
  Unchanged Due to Collision – The ID was not renamed, because requested name would have collided with another existing ID’s name, and the automatically adjusted name was the same as the current ID’s name.
- `RENAMED_NO_COLLISION`
  Renamed Without Collision – The ID was renamed as requested, without creating any name collision.
- `RENAMED_COLLISION_ADJUSTED`
  Renamed With Collision – The ID was renamed with adjustment of the requested name, to avoid a name collision.
- `RENAMED_COLLISION_FORCED`
  Renamed Enforced With Collision – The ID was renamed as requested, also renaming another ID to avoid a name collision.

**Return type:**

Literal[‘UNCHANGED’, ‘UNCHANGED_COLLISION’, ‘RENAMED_NO_COLLISION’, ‘RENAMED_COLLISION_ADJUSTED’, ‘RENAMED_COLLISION_FORCED’]

<a id="bpy.types.ID.evaluated_get"></a>

#### bpy.types.ID.evaluated_get(depsgraph)

Get corresponding evaluated ID from the given dependency graph. Note that this does not ensure the dependency graph is fully evaluated, it just returns the result of the last evaluation.

**Parameters:**

**depsgraph** ([`Depsgraph`](bpy.types.Depsgraph.md#bpy.types.Depsgraph "bpy.types.Depsgraph") | None) – Dependency graph to perform lookup in (never None)

**Returns:**

New copy of the ID

**Return type:**

[`ID`](#bpy.types.ID "bpy.types.ID")

<a id="bpy.types.ID.copy"></a>

#### bpy.types.ID.copy()

Create a copy of this data-block (not supported for all data-blocks). The result is added to the Blend-File Data (Main database), with all references to other data-blocks ensured to be from within the same Blend-File Data.

**Returns:**

New copy of the ID

**Return type:**

[`ID`](#bpy.types.ID "bpy.types.ID")

<a id="bpy.types.ID.asset_mark"></a>

#### bpy.types.ID.asset_mark()

Enable easier reuse of the data-block through the Asset Browser, with the help of customizable metadata (like previews, descriptions and tags)

<a id="bpy.types.ID.asset_clear"></a>

#### bpy.types.ID.asset_clear()

Delete all asset metadata and turn the asset data-block back into a normal data-block

<a id="bpy.types.ID.asset_generate_preview"></a>

#### bpy.types.ID.asset_generate_preview()

Generate preview image (might be scheduled in a background thread)

<a id="bpy.types.ID.override_create"></a>

#### bpy.types.ID.override_create(*, remap_local_usages=False)

Create an overridden local copy of this linked data-block (not supported for all data-blocks)

**Parameters:**

**remap_local_usages** (bool) – Whether local usages of the linked ID should be remapped to the new library override of it (optional)

**Returns:**

New overridden local copy of the ID

**Return type:**

[`ID`](#bpy.types.ID "bpy.types.ID")

<a id="bpy.types.ID.override_hierarchy_create"></a>

#### bpy.types.ID.override_hierarchy_create(scene, view_layer, *, reference=None, do_fully_editable=False)

Create an overridden local copy of this linked data-block, and most of its dependencies when it is a Collection or and Object

**Parameters:**

- **scene** ([`Scene`](bpy.types.Scene.md#bpy.types.Scene "bpy.types.Scene") | None) – In which scene the new overrides should be instantiated (never None)
- **view_layer** ([`ViewLayer`](bpy.types.ViewLayer.md#bpy.types.ViewLayer "bpy.types.ViewLayer") | None) – In which view layer the new overrides should be instantiated (never None)
- **reference** ([`ID`](#bpy.types.ID "bpy.types.ID") | None) – Another ID (usually an Object or Collection) used as a hint to decide where to instantiate the new overrides (optional)
- **do_fully_editable** (bool) – Make all library overrides generated by this call fully editable by the user (none will be ‘system overrides’) (optional)

**Returns:**

New overridden local copy of the root ID

**Return type:**

[`ID`](#bpy.types.ID "bpy.types.ID")

<a id="bpy.types.ID.user_clear"></a>

#### bpy.types.ID.user_clear()

Clear the user count of a data-block so its not saved, on reload the data will be removed

This function is for advanced use only, misuse can crash Blender since the user
count is used to prevent data being removed when it is used.

```python
# This example shows what _not_ to do, and will crash Blender.
import bpy

# Object which is in the scene.
obj = bpy.data.objects["Cube"]

# Without this, removal would raise an error.
obj.user_clear()

# Runs without an exception but will crash on redraw.
bpy.data.objects.remove(obj)
```

<a id="bpy.types.ID.user_remap"></a>

#### bpy.types.ID.user_remap(new_id)

Replace all usage in the .blend file of this ID by new given one

**Parameters:**

**new_id** ([`ID`](#bpy.types.ID "bpy.types.ID") | None) – New ID to use (never None)

<a id="bpy.types.ID.make_local"></a>

#### bpy.types.ID.make_local(*, clear_proxy=True, clear_liboverride=False, clear_asset_data=True)

Make this data-block local, return local one (may be a copy of the original, in case it is also indirectly used)

**Parameters:**

- **clear_proxy** (bool) – Deprecated, has no effect (optional)
- **clear_liboverride** (bool) – Remove potential library override data from the newly made local data (optional)
- **clear_asset_data** (bool) – Remove potential asset metadata so the newly local data-block is not treated as asset data-block and won’t show up in asset libraries (optional)

**Returns:**

This ID, or the new ID if it was copied

**Return type:**

[`ID`](#bpy.types.ID "bpy.types.ID")

<a id="bpy.types.ID.user_of_id"></a>

#### bpy.types.ID.user_of_id(id)

Count the number of times that ID uses/references given one

**Parameters:**

**id** ([`ID`](#bpy.types.ID "bpy.types.ID") | None) – ID to count usages (never None)

**Returns:**

Number of usages/references of given id by current data-block (in [0, inf])

**Return type:**

int

<a id="bpy.types.ID.animation_data_create"></a>

#### bpy.types.ID.animation_data_create()

Create animation data to this ID, note that not all ID types support this

**Returns:**

New animation data or None

**Return type:**

[`AnimData`](bpy.types.AnimData.md#bpy.types.AnimData "bpy.types.AnimData")

<a id="bpy.types.ID.animation_data_clear"></a>

#### bpy.types.ID.animation_data_clear()

Clear animation on this ID

<a id="bpy.types.ID.update_tag"></a>

#### bpy.types.ID.update_tag(*, refresh=set())

Tag the ID to update its display data, e.g. when calling `bpy.types.Scene.update`

**Parameters:**

**refresh** (set[Literal['OBJECT', 'DATA', 'TIME']]) – Type of updates to perform (optional)

<a id="bpy.types.ID.preview_ensure"></a>

#### bpy.types.ID.preview_ensure()

Ensure that this ID has preview data (if ID type supports it)

**Returns:**

The existing or created preview

**Return type:**

[`ImagePreview`](bpy.types.ImagePreview.md#bpy.types.ImagePreview "bpy.types.ImagePreview")

<a id="bpy.types.ID.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ID.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ID.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ID.bl_rna_get_subclass_py(id, default=None, /)

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
| - `bpy.context.annotation_data_owner` - `bpy.context.id` - `bpy.context.selected_ids` - `bpy.context.texture_user` - [`Action.fcurve_ensure_for_datablock`](bpy.types.Action.md#bpy.types.Action.fcurve_ensure_for_datablock "bpy.types.Action.fcurve_ensure_for_datablock") - [`ActionSlot.users`](bpy.types.ActionSlot.md#bpy.types.ActionSlot.users "bpy.types.ActionSlot.users") - [`AssetRepresentation.local_id`](bpy.types.AssetRepresentation.md#bpy.types.AssetRepresentation.local_id "bpy.types.AssetRepresentation.local_id") - [`BlendData.all_ids`](bpy.types.BlendData.md#bpy.types.BlendData.all_ids "bpy.types.BlendData.all_ids") - [`BlendData.pack_linked_ids_hierarchy`](bpy.types.BlendData.md#bpy.types.BlendData.pack_linked_ids_hierarchy "bpy.types.BlendData.pack_linked_ids_hierarchy") - [`BlendData.pack_linked_ids_hierarchy`](bpy.types.BlendData.md#bpy.types.BlendData.pack_linked_ids_hierarchy "bpy.types.BlendData.pack_linked_ids_hierarchy") - [`BlendDataObjects.new`](bpy.types.BlendDataObjects.md#bpy.types.BlendDataObjects.new "bpy.types.BlendDataObjects.new") - [`BlendImportContextItem.id`](bpy.types.BlendImportContextItem.md#bpy.types.BlendImportContextItem.id "bpy.types.BlendImportContextItem.id") - [`BlendImportContextItem.library_override_id`](bpy.types.BlendImportContextItem.md#bpy.types.BlendImportContextItem.library_override_id "bpy.types.BlendImportContextItem.library_override_id") - [`BlendImportContextItem.reusable_local_id`](bpy.types.BlendImportContextItem.md#bpy.types.BlendImportContextItem.reusable_local_id "bpy.types.BlendImportContextItem.reusable_local_id") - [`Depsgraph.id_eval_get`](bpy.types.Depsgraph.md#bpy.types.Depsgraph.id_eval_get "bpy.types.Depsgraph.id_eval_get") - [`Depsgraph.id_eval_get`](bpy.types.Depsgraph.md#bpy.types.Depsgraph.id_eval_get "bpy.types.Depsgraph.id_eval_get") - [`Depsgraph.ids`](bpy.types.Depsgraph.md#bpy.types.Depsgraph.ids "bpy.types.Depsgraph.ids") - [`DepsgraphUpdate.id`](bpy.types.DepsgraphUpdate.md#bpy.types.DepsgraphUpdate.id "bpy.types.DepsgraphUpdate.id") - [`DopeSheet.source`](bpy.types.DopeSheet.md#bpy.types.DopeSheet.source "bpy.types.DopeSheet.source") - [`DriverTarget.id`](bpy.types.DriverTarget.md#bpy.types.DriverTarget.id "bpy.types.DriverTarget.id") - [`ID.copy`](#bpy.types.ID.copy "bpy.types.ID.copy") - [`ID.evaluated_get`](#bpy.types.ID.evaluated_get "bpy.types.ID.evaluated_get") - [`ID.make_local`](#bpy.types.ID.make_local "bpy.types.ID.make_local") - [`ID.original`](#bpy.types.ID.original "bpy.types.ID.original") - [`ID.override_create`](#bpy.types.ID.override_create "bpy.types.ID.override_create") - [`ID.override_hierarchy_create`](#bpy.types.ID.override_hierarchy_create "bpy.types.ID.override_hierarchy_create") - [`ID.override_hierarchy_create`](#bpy.types.ID.override_hierarchy_create "bpy.types.ID.override_hierarchy_create") | - [`ID.user_of_id`](#bpy.types.ID.user_of_id "bpy.types.ID.user_of_id") - [`ID.user_remap`](#bpy.types.ID.user_remap "bpy.types.ID.user_remap") - [`IDOverrideLibrary.hierarchy_root`](bpy.types.IDOverrideLibrary.md#bpy.types.IDOverrideLibrary.hierarchy_root "bpy.types.IDOverrideLibrary.hierarchy_root") - [`IDOverrideLibrary.reference`](bpy.types.IDOverrideLibrary.md#bpy.types.IDOverrideLibrary.reference "bpy.types.IDOverrideLibrary.reference") - [`IDOverrideLibraryPropertyOperation.subitem_local_id`](bpy.types.IDOverrideLibraryPropertyOperation.md#bpy.types.IDOverrideLibraryPropertyOperation.subitem_local_id "bpy.types.IDOverrideLibraryPropertyOperation.subitem_local_id") - [`IDOverrideLibraryPropertyOperation.subitem_reference_id`](bpy.types.IDOverrideLibraryPropertyOperation.md#bpy.types.IDOverrideLibraryPropertyOperation.subitem_reference_id "bpy.types.IDOverrideLibraryPropertyOperation.subitem_reference_id") - [`IDOverrideLibraryPropertyOperations.add`](bpy.types.IDOverrideLibraryPropertyOperations.md#bpy.types.IDOverrideLibraryPropertyOperations.add "bpy.types.IDOverrideLibraryPropertyOperations.add") - [`IDOverrideLibraryPropertyOperations.add`](bpy.types.IDOverrideLibraryPropertyOperations.md#bpy.types.IDOverrideLibraryPropertyOperations.add "bpy.types.IDOverrideLibraryPropertyOperations.add") - [`IDViewerPathElem.id`](bpy.types.IDViewerPathElem.md#bpy.types.IDViewerPathElem.id "bpy.types.IDViewerPathElem.id") - [`Key.user`](bpy.types.Key.md#bpy.types.Key.user "bpy.types.Key.user") - [`KeyingSetPath.id`](bpy.types.KeyingSetPath.md#bpy.types.KeyingSetPath.id "bpy.types.KeyingSetPath.id") - [`KeyingSetPaths.add`](bpy.types.KeyingSetPaths.md#bpy.types.KeyingSetPaths.add "bpy.types.KeyingSetPaths.add") - [`MaskParent.id`](bpy.types.MaskParent.md#bpy.types.MaskParent.id "bpy.types.MaskParent.id") - [`NodeTree.get_from_context`](bpy.types.NodeTree.md#bpy.types.NodeTree.get_from_context "bpy.types.NodeTree.get_from_context") - [`NodeTree.get_from_context`](bpy.types.NodeTree.md#bpy.types.NodeTree.get_from_context "bpy.types.NodeTree.get_from_context") - [`NodesModifierDataBlock.id`](bpy.types.NodesModifierDataBlock.md#bpy.types.NodesModifierDataBlock.id "bpy.types.NodesModifierDataBlock.id") - [`Object.data`](bpy.types.Object.md#bpy.types.Object.data "bpy.types.Object.data") - [`PropertyGroupItem.id`](bpy.types.PropertyGroupItem.md#bpy.types.PropertyGroupItem.id "bpy.types.PropertyGroupItem.id") - [`SpaceFileBrowser.activate_asset_by_id`](bpy.types.SpaceFileBrowser.md#bpy.types.SpaceFileBrowser.activate_asset_by_id "bpy.types.SpaceFileBrowser.activate_asset_by_id") - [`SpaceNodeEditor.id`](bpy.types.SpaceNodeEditor.md#bpy.types.SpaceNodeEditor.id "bpy.types.SpaceNodeEditor.id") - [`SpaceNodeEditor.id_from`](bpy.types.SpaceNodeEditor.md#bpy.types.SpaceNodeEditor.id_from "bpy.types.SpaceNodeEditor.id_from") - [`SpaceProperties.pin_id`](bpy.types.SpaceProperties.md#bpy.types.SpaceProperties.pin_id "bpy.types.SpaceProperties.pin_id") - [`UILayout.template_action`](bpy.types.UILayout.md#bpy.types.UILayout.template_action "bpy.types.UILayout.template_action") - [`UILayout.template_path_builder`](bpy.types.UILayout.md#bpy.types.UILayout.template_path_builder "bpy.types.UILayout.template_path_builder") - [`UILayout.template_preview`](bpy.types.UILayout.md#bpy.types.UILayout.template_preview "bpy.types.UILayout.template_preview") - [`UILayout.template_preview`](bpy.types.UILayout.md#bpy.types.UILayout.template_preview "bpy.types.UILayout.template_preview") |
