<!-- source: Blender Python API reference 5.2 / bpy.types.DopeSheet.html -->

<a id="dopesheet-bpy-struct"></a>

# DopeSheet(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.DopeSheet"></a>

### class bpy.types.DopeSheet(bpy_struct)

Settings for filtering the channels shown in animation editors

<a id="bpy.types.DopeSheet.filter_collection"></a>

#### bpy.types.DopeSheet.filter_collection

Collection that included object should be a member of

**Type:**

[`Collection`](bpy.types.Collection.md#bpy.types.Collection "bpy.types.Collection") | None

<a id="bpy.types.DopeSheet.filter_fcurve_name"></a>

#### bpy.types.DopeSheet.filter_fcurve_name

F-Curve live filtering string (default “”, never None)

**Type:**

str

<a id="bpy.types.DopeSheet.filter_text"></a>

#### bpy.types.DopeSheet.filter_text

Live filtering string (default “”, never None)

**Type:**

str

<a id="bpy.types.DopeSheet.show_armatures"></a>

#### bpy.types.DopeSheet.show_armatures

Include visualization of armature related animation data (default True)

**Type:**

bool

<a id="bpy.types.DopeSheet.show_cache_files"></a>

#### bpy.types.DopeSheet.show_cache_files

Include visualization of cache file related animation data (default True)

**Type:**

bool

<a id="bpy.types.DopeSheet.show_cameras"></a>

#### bpy.types.DopeSheet.show_cameras

Include visualization of camera related animation data (default True)

**Type:**

bool

<a id="bpy.types.DopeSheet.show_curves"></a>

#### bpy.types.DopeSheet.show_curves

Include visualization of curve related animation data (default True)

**Type:**

bool

<a id="bpy.types.DopeSheet.show_datablock_filters"></a>

#### bpy.types.DopeSheet.show_datablock_filters

Show options for whether channels related to certain types of data are included (default False)

**Type:**

bool

<a id="bpy.types.DopeSheet.show_driver_fallback_as_error"></a>

#### bpy.types.DopeSheet.show_driver_fallback_as_error

Include drivers that relied on any fallback values for their evaluation in the Only Show Errors filter, even if the driver evaluation succeeded (default False)

**Type:**

bool

<a id="bpy.types.DopeSheet.show_expanded_summary"></a>

#### bpy.types.DopeSheet.show_expanded_summary

Collapse summary when shown, so all other channels get hidden (Dope Sheet editors only) (default True)

**Type:**

bool

<a id="bpy.types.DopeSheet.show_gpencil"></a>

#### bpy.types.DopeSheet.show_gpencil

Include visualization of Grease Pencil related animation data and frames (default True)

**Type:**

bool

<a id="bpy.types.DopeSheet.show_hair_curves"></a>

#### bpy.types.DopeSheet.show_hair_curves

Include visualization of hair related animation data (default True)

**Type:**

bool

<a id="bpy.types.DopeSheet.show_hidden"></a>

#### bpy.types.DopeSheet.show_hidden

Include channels from objects/bone that are not visible (default False)

**Type:**

bool

<a id="bpy.types.DopeSheet.show_lattices"></a>

#### bpy.types.DopeSheet.show_lattices

Include visualization of lattice related animation data (default True)

**Type:**

bool

<a id="bpy.types.DopeSheet.show_lightprobes"></a>

#### bpy.types.DopeSheet.show_lightprobes

Include visualization of light probe related animation data (default True)

**Type:**

bool

<a id="bpy.types.DopeSheet.show_lights"></a>

#### bpy.types.DopeSheet.show_lights

Include visualization of light related animation data (default True)

**Type:**

bool

<a id="bpy.types.DopeSheet.show_linestyles"></a>

#### bpy.types.DopeSheet.show_linestyles

Include visualization of Line Style related Animation data (default True)

**Type:**

bool

<a id="bpy.types.DopeSheet.show_materials"></a>

#### bpy.types.DopeSheet.show_materials

Include visualization of material related animation data (default True)

**Type:**

bool

<a id="bpy.types.DopeSheet.show_meshes"></a>

#### bpy.types.DopeSheet.show_meshes

Include visualization of mesh related animation data (default True)

**Type:**

bool

<a id="bpy.types.DopeSheet.show_metaballs"></a>

#### bpy.types.DopeSheet.show_metaballs

Include visualization of metaball related animation data (default True)

**Type:**

bool

<a id="bpy.types.DopeSheet.show_missing_nla"></a>

#### bpy.types.DopeSheet.show_missing_nla

Include animation data-blocks with no NLA data (NLA editor only) (default True)

**Type:**

bool

<a id="bpy.types.DopeSheet.show_modifiers"></a>

#### bpy.types.DopeSheet.show_modifiers

Include visualization of animation data related to data-blocks linked to modifiers (default True)

**Type:**

bool

<a id="bpy.types.DopeSheet.show_movieclips"></a>

#### bpy.types.DopeSheet.show_movieclips

Include visualization of movie clip related animation data (default True)

**Type:**

bool

<a id="bpy.types.DopeSheet.show_nodes"></a>

#### bpy.types.DopeSheet.show_nodes

Include visualization of node related animation data (default True)

**Type:**

bool

<a id="bpy.types.DopeSheet.show_only_errors"></a>

#### bpy.types.DopeSheet.show_only_errors

Only include F-Curves and drivers that are disabled or have errors (default False)

**Type:**

bool

<a id="bpy.types.DopeSheet.show_only_selected"></a>

#### bpy.types.DopeSheet.show_only_selected

Only include channels relating to selected objects and data (default False)

**Type:**

bool

<a id="bpy.types.DopeSheet.show_only_slot_of_active_object"></a>

#### bpy.types.DopeSheet.show_only_slot_of_active_object

Only show the slot of the active Object. Otherwise show all the Action’s Slots (default False)

**Type:**

bool

<a id="bpy.types.DopeSheet.show_particles"></a>

#### bpy.types.DopeSheet.show_particles

Include visualization of particle related animation data (default True)

**Type:**

bool

<a id="bpy.types.DopeSheet.show_pointclouds"></a>

#### bpy.types.DopeSheet.show_pointclouds

Include visualization of point cloud related animation data (default True)

**Type:**

bool

<a id="bpy.types.DopeSheet.show_scenes"></a>

#### bpy.types.DopeSheet.show_scenes

Include visualization of scene related animation data (default True)

**Type:**

bool

<a id="bpy.types.DopeSheet.show_shapekeys"></a>

#### bpy.types.DopeSheet.show_shapekeys

Include visualization of shape key related animation data (default True)

**Type:**

bool

<a id="bpy.types.DopeSheet.show_speakers"></a>

#### bpy.types.DopeSheet.show_speakers

Include visualization of speaker related animation data (default True)

**Type:**

bool

<a id="bpy.types.DopeSheet.show_summary"></a>

#### bpy.types.DopeSheet.show_summary

Display an additional ‘summary’ line (Dope Sheet editors only) (default False)

**Type:**

bool

<a id="bpy.types.DopeSheet.show_textures"></a>

#### bpy.types.DopeSheet.show_textures

Include visualization of texture related animation data (default True)

**Type:**

bool

<a id="bpy.types.DopeSheet.show_transforms"></a>

#### bpy.types.DopeSheet.show_transforms

Include visualization of object-level animation data (mostly transforms) (default True)

**Type:**

bool

<a id="bpy.types.DopeSheet.show_volumes"></a>

#### bpy.types.DopeSheet.show_volumes

Include visualization of volume related animation data (default True)

**Type:**

bool

<a id="bpy.types.DopeSheet.show_worlds"></a>

#### bpy.types.DopeSheet.show_worlds

Include visualization of world related animation data (default True)

**Type:**

bool

<a id="bpy.types.DopeSheet.source"></a>

#### bpy.types.DopeSheet.source

ID-Block representing source data, usually ID_SCE (i.e. Scene) (readonly)

**Type:**

[`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID") | None

<a id="bpy.types.DopeSheet.use_datablock_sort"></a>

#### bpy.types.DopeSheet.use_datablock_sort

Alphabetically sorts data-blocks - mainly objects in the scene (disable to increase viewport speed) (default True)

**Type:**

bool

<a id="bpy.types.DopeSheet.use_filter_invert"></a>

#### bpy.types.DopeSheet.use_filter_invert

Invert filter search (default False)

**Type:**

bool

<a id="bpy.types.DopeSheet.use_multi_word_filter"></a>

#### bpy.types.DopeSheet.use_multi_word_filter

Perform fuzzy/multi-word matching.
Warning: May be slow

(default False)

**Type:**

bool

<a id="bpy.types.DopeSheet.bl_rna_get_subclass"></a>

#### classmethod bpy.types.DopeSheet.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.DopeSheet.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.DopeSheet.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`SpaceDopeSheetEditor.dopesheet`](bpy.types.SpaceDopeSheetEditor.md#bpy.types.SpaceDopeSheetEditor.dopesheet "bpy.types.SpaceDopeSheetEditor.dopesheet") - [`SpaceGraphEditor.dopesheet`](bpy.types.SpaceGraphEditor.md#bpy.types.SpaceGraphEditor.dopesheet "bpy.types.SpaceGraphEditor.dopesheet") | - [`SpaceNLA.dopesheet`](bpy.types.SpaceNLA.md#bpy.types.SpaceNLA.dopesheet "bpy.types.SpaceNLA.dopesheet") |
