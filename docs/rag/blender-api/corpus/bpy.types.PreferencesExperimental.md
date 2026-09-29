<!-- source: Blender Python API reference 5.2 / bpy.types.PreferencesExperimental.html -->

<a id="preferencesexperimental-bpy-struct"></a>

# PreferencesExperimental(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.PreferencesExperimental"></a>

### class bpy.types.PreferencesExperimental(bpy_struct)

Experimental features

<a id="bpy.types.PreferencesExperimental.no_data_block_packing"></a>

#### bpy.types.PreferencesExperimental.no_data_block_packing

Fall-back to appending instead of packing data-blocks (default False)

**Type:**

bool

<a id="bpy.types.PreferencesExperimental.override_auto_resync"></a>

#### bpy.types.PreferencesExperimental.override_auto_resync

Disable library overrides automatic resync detection and process on file load (can be useful to help fixing broken files). Also see the “–disable-liboverride-auto-resync” command line option (default False)

**Type:**

bool

<a id="bpy.types.PreferencesExperimental.show_asset_debug_info"></a>

#### bpy.types.PreferencesExperimental.show_asset_debug_info

Enable some extra fields in the Asset Browser to aid in debugging (default False)

**Type:**

bool

<a id="bpy.types.PreferencesExperimental.use_all_linked_data_direct"></a>

#### bpy.types.PreferencesExperimental.use_all_linked_data_direct

Forces all linked data to be considered as directly linked. Workaround for current issues/limitations in BAT (Blender studio pipeline tool) (default False)

**Type:**

bool

<a id="bpy.types.PreferencesExperimental.use_asset_indexing"></a>

#### bpy.types.PreferencesExperimental.use_asset_indexing

Disable the asset indexer, to force every asset library refresh to completely reread assets from disk (default False)

**Type:**

bool

<a id="bpy.types.PreferencesExperimental.use_collection_importer"></a>

#### bpy.types.PreferencesExperimental.use_collection_importer

Enables a file importer to be configured on a Collection (default False)

**Type:**

bool

<a id="bpy.types.PreferencesExperimental.use_cycles_debug"></a>

#### bpy.types.PreferencesExperimental.use_cycles_debug

Enable Cycles debugging options for developers (default False)

**Type:**

bool

<a id="bpy.types.PreferencesExperimental.use_eevee_debug"></a>

#### bpy.types.PreferencesExperimental.use_eevee_debug

Enable EEVEE debugging options for developers (default False)

**Type:**

bool

<a id="bpy.types.PreferencesExperimental.use_extended_asset_browser"></a>

#### bpy.types.PreferencesExperimental.use_extended_asset_browser

Enable Asset Browser editor and operators to manage regular data-blocks as assets, not just poses (default False)

**Type:**

bool

<a id="bpy.types.PreferencesExperimental.use_extensions_debug"></a>

#### bpy.types.PreferencesExperimental.use_extensions_debug

Extra debugging information & developer support utilities for extensions (default False)

**Type:**

bool

<a id="bpy.types.PreferencesExperimental.use_new_curves_tools"></a>

#### bpy.types.PreferencesExperimental.use_new_curves_tools

Enable additional features for the new curves data block (default False)

**Type:**

bool

<a id="bpy.types.PreferencesExperimental.use_paint_debug"></a>

#### bpy.types.PreferencesExperimental.use_paint_debug

Enable paint & sculpt debugging options for developers (default False)

**Type:**

bool

<a id="bpy.types.PreferencesExperimental.use_recompute_usercount_on_save_debug"></a>

#### bpy.types.PreferencesExperimental.use_recompute_usercount_on_save_debug

Recompute all ID user-counts before saving to a blend-file. Allows to work around invalid user-count handling in code that may lead to loss of data due to wrongly detected unused data-blocks (default False)

**Type:**

bool

<a id="bpy.types.PreferencesExperimental.use_remote_asset_libraries"></a>

#### bpy.types.PreferencesExperimental.use_remote_asset_libraries

Enable asset libraries served over HTTP/HTTPS (default False, readonly)

**Type:**

bool

<a id="bpy.types.PreferencesExperimental.use_sculpt_texture_paint"></a>

#### bpy.types.PreferencesExperimental.use_sculpt_texture_paint

Use texture painting in Sculpt Mode (default False)

**Type:**

bool

<a id="bpy.types.PreferencesExperimental.use_shader_node_previews"></a>

#### bpy.types.PreferencesExperimental.use_shader_node_previews

Enables previews in the shader node editor (default False)

**Type:**

bool

<a id="bpy.types.PreferencesExperimental.use_undo_legacy"></a>

#### bpy.types.PreferencesExperimental.use_undo_legacy

Use legacy undo (slower than the new default one, but may be more stable in some cases) (default False)

**Type:**

bool

<a id="bpy.types.PreferencesExperimental.use_viewport_debug"></a>

#### bpy.types.PreferencesExperimental.use_viewport_debug

Enable viewport debugging options for developers in the overlays pop-over (default False)

**Type:**

bool

<a id="bpy.types.PreferencesExperimental.write_legacy_blend_file_format"></a>

#### bpy.types.PreferencesExperimental.write_legacy_blend_file_format

Use file format used before Blender 5.0. This format is more limited but it may have better compatibility with tools that don’t support the new format yet (default False)

**Type:**

bool

<a id="bpy.types.PreferencesExperimental.bl_rna_get_subclass"></a>

#### classmethod bpy.types.PreferencesExperimental.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.PreferencesExperimental.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.PreferencesExperimental.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Preferences.experimental`](bpy.types.Preferences.md#bpy.types.Preferences.experimental "bpy.types.Preferences.experimental") |  |
