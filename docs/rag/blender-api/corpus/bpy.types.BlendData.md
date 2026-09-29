<!-- source: Blender Python API reference 5.2 / bpy.types.BlendData.html -->

<a id="blenddata-bpy-struct"></a>

# BlendData(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.BlendData"></a>

### class bpy.types.BlendData(bpy_struct)

Main data structure representing a .blend file and all its data-blocks

<a id="bpy.types.BlendData.actions"></a>

#### bpy.types.BlendData.actions

Action data-blocks (default None, readonly)

**Type:**

[`BlendDataActions`](bpy.types.BlendDataActions.md#bpy.types.BlendDataActions "bpy.types.BlendDataActions")[[`Action`](bpy.types.Action.md#bpy.types.Action "bpy.types.Action")]

<a id="bpy.types.BlendData.all_ids"></a>

#### bpy.types.BlendData.all_ids

Read-only list of all IDs listed in Blender data-base (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")]

<a id="bpy.types.BlendData.annotations"></a>

#### bpy.types.BlendData.annotations

Annotation data-blocks (legacy Grease Pencil) (default None, readonly)

**Type:**

[`BlendDataAnnotations`](bpy.types.BlendDataAnnotations.md#bpy.types.BlendDataAnnotations "bpy.types.BlendDataAnnotations")[[`Annotation`](bpy.types.Annotation.md#bpy.types.Annotation "bpy.types.Annotation")]

<a id="bpy.types.BlendData.armatures"></a>

#### bpy.types.BlendData.armatures

Armature data-blocks (default None, readonly)

**Type:**

[`BlendDataArmatures`](bpy.types.BlendDataArmatures.md#bpy.types.BlendDataArmatures "bpy.types.BlendDataArmatures")[[`Armature`](bpy.types.Armature.md#bpy.types.Armature "bpy.types.Armature")]

<a id="bpy.types.BlendData.brushes"></a>

#### bpy.types.BlendData.brushes

Brush data-blocks (default None, readonly)

**Type:**

[`BlendDataBrushes`](bpy.types.BlendDataBrushes.md#bpy.types.BlendDataBrushes "bpy.types.BlendDataBrushes")[[`Brush`](bpy.types.Brush.md#bpy.types.Brush "bpy.types.Brush")]

<a id="bpy.types.BlendData.cache_files"></a>

#### bpy.types.BlendData.cache_files

Cache Files data-blocks (default None, readonly)

**Type:**

[`BlendDataCacheFiles`](bpy.types.BlendDataCacheFiles.md#bpy.types.BlendDataCacheFiles "bpy.types.BlendDataCacheFiles")[[`CacheFile`](bpy.types.CacheFile.md#bpy.types.CacheFile "bpy.types.CacheFile")]

<a id="bpy.types.BlendData.cameras"></a>

#### bpy.types.BlendData.cameras

Camera data-blocks (default None, readonly)

**Type:**

[`BlendDataCameras`](bpy.types.BlendDataCameras.md#bpy.types.BlendDataCameras "bpy.types.BlendDataCameras")[[`Camera`](bpy.types.Camera.md#bpy.types.Camera "bpy.types.Camera")]

<a id="bpy.types.BlendData.collections"></a>

#### bpy.types.BlendData.collections

Collection data-blocks (default None, readonly)

**Type:**

[`BlendDataCollections`](bpy.types.BlendDataCollections.md#bpy.types.BlendDataCollections "bpy.types.BlendDataCollections")[[`Collection`](bpy.types.Collection.md#bpy.types.Collection "bpy.types.Collection")]

<a id="bpy.types.BlendData.colorspace"></a>

#### bpy.types.BlendData.colorspace

Information about the color space used for data-blocks in a blend file (readonly, never None)

**Type:**

[`BlendFileColorspace`](bpy.types.BlendFileColorspace.md#bpy.types.BlendFileColorspace "bpy.types.BlendFileColorspace")

<a id="bpy.types.BlendData.curves"></a>

#### bpy.types.BlendData.curves

Curve data-blocks (default None, readonly)

**Type:**

[`BlendDataCurves`](bpy.types.BlendDataCurves.md#bpy.types.BlendDataCurves "bpy.types.BlendDataCurves")[[`Curve`](bpy.types.Curve.md#bpy.types.Curve "bpy.types.Curve")]

<a id="bpy.types.BlendData.filepath"></a>

#### bpy.types.BlendData.filepath

Path to the .blend file (default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.BlendData.fonts"></a>

#### bpy.types.BlendData.fonts

Vector font data-blocks (default None, readonly)

**Type:**

[`BlendDataFonts`](bpy.types.BlendDataFonts.md#bpy.types.BlendDataFonts "bpy.types.BlendDataFonts")[[`VectorFont`](bpy.types.VectorFont.md#bpy.types.VectorFont "bpy.types.VectorFont")]

<a id="bpy.types.BlendData.grease_pencils"></a>

#### bpy.types.BlendData.grease_pencils

Grease Pencil data-blocks (default None, readonly)

**Type:**

[`BlendDataGreasePencilsV3`](bpy.types.BlendDataGreasePencilsV3.md#bpy.types.BlendDataGreasePencilsV3 "bpy.types.BlendDataGreasePencilsV3")[[`GreasePencil`](bpy.types.GreasePencil.md#bpy.types.GreasePencil "bpy.types.GreasePencil")]

<a id="bpy.types.BlendData.hair_curves"></a>

#### bpy.types.BlendData.hair_curves

Hair curve data-blocks (default None, readonly)

**Type:**

[`BlendDataHairCurves`](bpy.types.BlendDataHairCurves.md#bpy.types.BlendDataHairCurves "bpy.types.BlendDataHairCurves")[[`Curves`](bpy.types.Curves.md#bpy.types.Curves "bpy.types.Curves")]

<a id="bpy.types.BlendData.images"></a>

#### bpy.types.BlendData.images

Image data-blocks (default None, readonly)

**Type:**

[`BlendDataImages`](bpy.types.BlendDataImages.md#bpy.types.BlendDataImages "bpy.types.BlendDataImages")[[`Image`](bpy.types.Image.md#bpy.types.Image "bpy.types.Image")]

<a id="bpy.types.BlendData.is_dirty"></a>

#### bpy.types.BlendData.is_dirty

Have recent edits been saved to disk (default False, readonly)

**Type:**

bool

<a id="bpy.types.BlendData.is_saved"></a>

#### bpy.types.BlendData.is_saved

Has the current session been saved to disk as a .blend file (default False, readonly)

**Type:**

bool

<a id="bpy.types.BlendData.lattices"></a>

#### bpy.types.BlendData.lattices

Lattice data-blocks (default None, readonly)

**Type:**

[`BlendDataLattices`](bpy.types.BlendDataLattices.md#bpy.types.BlendDataLattices "bpy.types.BlendDataLattices")[[`Lattice`](bpy.types.Lattice.md#bpy.types.Lattice "bpy.types.Lattice")]

<a id="bpy.types.BlendData.libraries"></a>

#### bpy.types.BlendData.libraries

Library data-blocks (default None, readonly)

**Type:**

[`BlendDataLibraries`](bpy.types.BlendDataLibraries.md#bpy.types.BlendDataLibraries "bpy.types.BlendDataLibraries")[[`Library`](bpy.types.Library.md#bpy.types.Library "bpy.types.Library")]

<a id="bpy.types.BlendData.lightprobes"></a>

#### bpy.types.BlendData.lightprobes

Light Probe data-blocks (default None, readonly)

**Type:**

[`BlendDataProbes`](bpy.types.BlendDataProbes.md#bpy.types.BlendDataProbes "bpy.types.BlendDataProbes")[[`LightProbe`](bpy.types.LightProbe.md#bpy.types.LightProbe "bpy.types.LightProbe")]

<a id="bpy.types.BlendData.lights"></a>

#### bpy.types.BlendData.lights

Light data-blocks (default None, readonly)

**Type:**

[`BlendDataLights`](bpy.types.BlendDataLights.md#bpy.types.BlendDataLights "bpy.types.BlendDataLights")[[`Light`](bpy.types.Light.md#bpy.types.Light "bpy.types.Light")]

<a id="bpy.types.BlendData.linestyles"></a>

#### bpy.types.BlendData.linestyles

Line Style data-blocks (default None, readonly)

**Type:**

[`BlendDataLineStyles`](bpy.types.BlendDataLineStyles.md#bpy.types.BlendDataLineStyles "bpy.types.BlendDataLineStyles")[[`FreestyleLineStyle`](bpy.types.FreestyleLineStyle.md#bpy.types.FreestyleLineStyle "bpy.types.FreestyleLineStyle")]

<a id="bpy.types.BlendData.masks"></a>

#### bpy.types.BlendData.masks

Masks data-blocks (default None, readonly)

**Type:**

[`BlendDataMasks`](bpy.types.BlendDataMasks.md#bpy.types.BlendDataMasks "bpy.types.BlendDataMasks")[[`Mask`](bpy.types.Mask.md#bpy.types.Mask "bpy.types.Mask")]

<a id="bpy.types.BlendData.materials"></a>

#### bpy.types.BlendData.materials

Material data-blocks (default None, readonly)

**Type:**

[`BlendDataMaterials`](bpy.types.BlendDataMaterials.md#bpy.types.BlendDataMaterials "bpy.types.BlendDataMaterials")[[`Material`](bpy.types.Material.md#bpy.types.Material "bpy.types.Material")]

<a id="bpy.types.BlendData.meshes"></a>

#### bpy.types.BlendData.meshes

Mesh data-blocks (default None, readonly)

**Type:**

[`BlendDataMeshes`](bpy.types.BlendDataMeshes.md#bpy.types.BlendDataMeshes "bpy.types.BlendDataMeshes")[[`Mesh`](bpy.types.Mesh.md#bpy.types.Mesh "bpy.types.Mesh")]

<a id="bpy.types.BlendData.metaballs"></a>

#### bpy.types.BlendData.metaballs

Metaball data-blocks (default None, readonly)

**Type:**

[`BlendDataMetaBalls`](bpy.types.BlendDataMetaBalls.md#bpy.types.BlendDataMetaBalls "bpy.types.BlendDataMetaBalls")[[`MetaBall`](bpy.types.MetaBall.md#bpy.types.MetaBall "bpy.types.MetaBall")]

<a id="bpy.types.BlendData.movieclips"></a>

#### bpy.types.BlendData.movieclips

Movie Clip data-blocks (default None, readonly)

**Type:**

[`BlendDataMovieClips`](bpy.types.BlendDataMovieClips.md#bpy.types.BlendDataMovieClips "bpy.types.BlendDataMovieClips")[[`MovieClip`](bpy.types.MovieClip.md#bpy.types.MovieClip "bpy.types.MovieClip")]

<a id="bpy.types.BlendData.node_groups"></a>

#### bpy.types.BlendData.node_groups

Node group data-blocks (default None, readonly)

**Type:**

[`BlendDataNodeTrees`](bpy.types.BlendDataNodeTrees.md#bpy.types.BlendDataNodeTrees "bpy.types.BlendDataNodeTrees")[[`NodeTree`](bpy.types.NodeTree.md#bpy.types.NodeTree "bpy.types.NodeTree")]

<a id="bpy.types.BlendData.objects"></a>

#### bpy.types.BlendData.objects

Object data-blocks (default None, readonly)

**Type:**

[`BlendDataObjects`](bpy.types.BlendDataObjects.md#bpy.types.BlendDataObjects "bpy.types.BlendDataObjects")[[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object")]

<a id="bpy.types.BlendData.paint_curves"></a>

#### bpy.types.BlendData.paint_curves

Paint Curves data-blocks (default None, readonly)

**Type:**

[`BlendDataPaintCurves`](bpy.types.BlendDataPaintCurves.md#bpy.types.BlendDataPaintCurves "bpy.types.BlendDataPaintCurves")[[`PaintCurve`](bpy.types.PaintCurve.md#bpy.types.PaintCurve "bpy.types.PaintCurve")]

<a id="bpy.types.BlendData.palettes"></a>

#### bpy.types.BlendData.palettes

Palette data-blocks (default None, readonly)

**Type:**

[`BlendDataPalettes`](bpy.types.BlendDataPalettes.md#bpy.types.BlendDataPalettes "bpy.types.BlendDataPalettes")[[`Palette`](bpy.types.Palette.md#bpy.types.Palette "bpy.types.Palette")]

<a id="bpy.types.BlendData.particles"></a>

#### bpy.types.BlendData.particles

Particle data-blocks (default None, readonly)

**Type:**

[`BlendDataParticles`](bpy.types.BlendDataParticles.md#bpy.types.BlendDataParticles "bpy.types.BlendDataParticles")[[`ParticleSettings`](bpy.types.ParticleSettings.md#bpy.types.ParticleSettings "bpy.types.ParticleSettings")]

<a id="bpy.types.BlendData.pointclouds"></a>

#### bpy.types.BlendData.pointclouds

Point cloud data-blocks (default None, readonly)

**Type:**

[`BlendDataPointClouds`](bpy.types.BlendDataPointClouds.md#bpy.types.BlendDataPointClouds "bpy.types.BlendDataPointClouds")[[`PointCloud`](bpy.types.PointCloud.md#bpy.types.PointCloud "bpy.types.PointCloud")]

<a id="bpy.types.BlendData.scenes"></a>

#### bpy.types.BlendData.scenes

Scene data-blocks (default None, readonly)

**Type:**

[`BlendDataScenes`](bpy.types.BlendDataScenes.md#bpy.types.BlendDataScenes "bpy.types.BlendDataScenes")[[`Scene`](bpy.types.Scene.md#bpy.types.Scene "bpy.types.Scene")]

<a id="bpy.types.BlendData.screens"></a>

#### bpy.types.BlendData.screens

Screen data-blocks (default None, readonly)

**Type:**

[`BlendDataScreens`](bpy.types.BlendDataScreens.md#bpy.types.BlendDataScreens "bpy.types.BlendDataScreens")[[`Screen`](bpy.types.Screen.md#bpy.types.Screen "bpy.types.Screen")]

<a id="bpy.types.BlendData.shape_keys"></a>

#### bpy.types.BlendData.shape_keys

Shape Key data-blocks (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`Key`](bpy.types.Key.md#bpy.types.Key "bpy.types.Key")]

<a id="bpy.types.BlendData.sounds"></a>

#### bpy.types.BlendData.sounds

Sound data-blocks (default None, readonly)

**Type:**

[`BlendDataSounds`](bpy.types.BlendDataSounds.md#bpy.types.BlendDataSounds "bpy.types.BlendDataSounds")[[`Sound`](bpy.types.Sound.md#bpy.types.Sound "bpy.types.Sound")]

<a id="bpy.types.BlendData.speakers"></a>

#### bpy.types.BlendData.speakers

Speaker data-blocks (default None, readonly)

**Type:**

[`BlendDataSpeakers`](bpy.types.BlendDataSpeakers.md#bpy.types.BlendDataSpeakers "bpy.types.BlendDataSpeakers")[[`Speaker`](bpy.types.Speaker.md#bpy.types.Speaker "bpy.types.Speaker")]

<a id="bpy.types.BlendData.texts"></a>

#### bpy.types.BlendData.texts

Text data-blocks (default None, readonly)

**Type:**

[`BlendDataTexts`](bpy.types.BlendDataTexts.md#bpy.types.BlendDataTexts "bpy.types.BlendDataTexts")[[`Text`](bpy.types.Text.md#bpy.types.Text "bpy.types.Text")]

<a id="bpy.types.BlendData.textures"></a>

#### bpy.types.BlendData.textures

Texture data-blocks (default None, readonly)

**Type:**

[`BlendDataTextures`](bpy.types.BlendDataTextures.md#bpy.types.BlendDataTextures "bpy.types.BlendDataTextures")[[`Texture`](bpy.types.Texture.md#bpy.types.Texture "bpy.types.Texture")]

<a id="bpy.types.BlendData.use_autopack"></a>

#### bpy.types.BlendData.use_autopack

Automatically pack all external data into .blend file (default False)

**Type:**

bool

<a id="bpy.types.BlendData.version"></a>

#### bpy.types.BlendData.version

File format version the .blend file was saved with (array of 3 items, in [0, inf], default (0, 0, 0), readonly)

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[int]

<a id="bpy.types.BlendData.volumes"></a>

#### bpy.types.BlendData.volumes

Volume data-blocks (default None, readonly)

**Type:**

[`BlendDataVolumes`](bpy.types.BlendDataVolumes.md#bpy.types.BlendDataVolumes "bpy.types.BlendDataVolumes")[[`Volume`](bpy.types.Volume.md#bpy.types.Volume "bpy.types.Volume")]

<a id="bpy.types.BlendData.window_managers"></a>

#### bpy.types.BlendData.window_managers

Window manager data-blocks (default None, readonly)

**Type:**

[`BlendDataWindowManagers`](bpy.types.BlendDataWindowManagers.md#bpy.types.BlendDataWindowManagers "bpy.types.BlendDataWindowManagers")[[`WindowManager`](bpy.types.WindowManager.md#bpy.types.WindowManager "bpy.types.WindowManager")]

<a id="bpy.types.BlendData.workspaces"></a>

#### bpy.types.BlendData.workspaces

Workspace data-blocks (default None, readonly)

**Type:**

[`BlendDataWorkSpaces`](bpy.types.BlendDataWorkSpaces.md#bpy.types.BlendDataWorkSpaces "bpy.types.BlendDataWorkSpaces")[[`WorkSpace`](bpy.types.WorkSpace.md#bpy.types.WorkSpace "bpy.types.WorkSpace")]

<a id="bpy.types.BlendData.worlds"></a>

#### bpy.types.BlendData.worlds

World data-blocks (default None, readonly)

**Type:**

[`BlendDataWorlds`](bpy.types.BlendDataWorlds.md#bpy.types.BlendDataWorlds "bpy.types.BlendDataWorlds")[[`World`](bpy.types.World.md#bpy.types.World "bpy.types.World")]

<a id="bpy.types.BlendData.pack_linked_ids_hierarchy"></a>

#### bpy.types.BlendData.pack_linked_ids_hierarchy(root_id)

Pack the given linked ID and its dependencies into current blendfile

**Parameters:**

**root_id** ([`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID") | None) – Root linked ID to pack

**Returns:**

The packed ID matching the given root ID

**Return type:**

[`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")

<a id="bpy.types.BlendData.batch_remove"></a>

#### bpy.types.BlendData.batch_remove(ids)

Remove (delete) several IDs at once.

Note that this function is quicker than individual calls to `remove()` (from [`bpy.types.BlendData`](#bpy.types.BlendData "bpy.types.BlendData")
ID collections), but less safe/versatile (it can break Blender, e.g. by removing all scenes…).

**Parameters:**

**ids** (Sequence[[`bpy.types.ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")]) – Sequence of IDs (types can be mixed).

<a id="bpy.types.BlendData.bl_rna_get_subclass"></a>

#### classmethod bpy.types.BlendData.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.BlendData.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.BlendData.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="bpy.types.BlendData.file_path_foreach"></a>

#### bpy.types.BlendData.file_path_foreach(visit_path_fn, *, subset=None, visit_types=None, flags={'SKIP_PACKED', 'SKIP_WEAK_REFERENCES'})

Call `visit_path_fn` for the file paths used by all ID data-blocks in current `bpy.data`.

For list of valid set members for visit_types, see: [`bpy.types.KeyingSetPath.id_type`](bpy.types.KeyingSetPath.md#bpy.types.KeyingSetPath.id_type "bpy.types.KeyingSetPath.id_type").

**Parameters:**

- **visit_path_fn** (Callable[[[`bpy.types.ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID"), str, [`bpy.types.BlendDataPathMeta`](bpy.types.BlendDataPathMeta.md#bpy.types.BlendDataPathMeta "bpy.types.BlendDataPathMeta")], str|None]) – function that takes three parameters: the data-block, a file path, and a [`bpy.types.BlendDataPathMeta`](bpy.types.BlendDataPathMeta.md#bpy.types.BlendDataPathMeta "bpy.types.BlendDataPathMeta") metadata object. The function should return either `None` or a `str`. In the latter case, the visited file path will be replaced with the returned string.
- **subset** (set[str] | None) – When given, only these data-blocks and their used file paths will be visited.
- **visit_types** (set[str] | None) – When given, only visit data-blocks of these types. Ignored if `subset` is also given.
- **flags** (set[str]) – Set of flags that influence which data-blocks are visited. See [File Path Foreach Flag Items](bpy_types_enum_items/file_path_foreach_flag_items.md#rna-enum-file-path-foreach-flag-items).

<a id="bpy.types.BlendData.file_path_map"></a>

#### bpy.types.BlendData.file_path_map(*, subset=None, key_types=None, include_libraries=False)

Returns a mapping of all ID data-blocks in current `bpy.data` to a set of all file paths used by them.

For list of valid set members for key_types, see: [`bpy.types.KeyingSetPath.id_type`](bpy.types.KeyingSetPath.md#bpy.types.KeyingSetPath.id_type "bpy.types.KeyingSetPath.id_type").

**Parameters:**

- **subset** (Sequence[[`bpy.types.ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")] | None) – When given, only these data-blocks and their used file paths will be included as keys/values in the map.
- **key_types** (set[str] | None) – When given, filter the keys mapped by ID types. Ignored if `subset` is also given.
- **include_libraries** (bool) – Include library file paths of linked data. False by default.

**Returns:**

dictionary of [`bpy.types.ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID") instances, with sets of file path strings as their values.

**Return type:**

dict[[`bpy.types.ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID"), set[str]]

<a id="bpy.types.BlendData.orphans_purge"></a>

#### bpy.types.BlendData.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=False)

Remove (delete) all IDs with no user.

**Parameters:**

- **do_local_ids** (bool) – Include unused local IDs in the deletion, defaults to True
- **do_linked_ids** (bool) – Include unused linked IDs in the deletion, defaults to True
- **do_recursive** (bool) – Recursively check for unused IDs, ensuring no orphaned one remain after a single run of that function, defaults to False

**Returns:**

The number of deleted IDs.

**Return type:**

int

<a id="bpy.types.BlendData.temp_data"></a>

#### static bpy.types.BlendData.temp_data(*, filepath=None)

A context manager that temporarily creates blender file data.

**Parameters:**

**filepath** (str | bytes | None) – The file path for the newly temporary data. When None, the path of the currently open file is used.

**Returns:**

Blend file data which is freed once the context exits.

**Return type:**

[`bpy.types.BlendData`](#bpy.types.BlendData "bpy.types.BlendData")

<a id="bpy.types.BlendData.user_map"></a>

#### bpy.types.BlendData.user_map(*, subset=None, key_types=None, value_types=None)

Returns a mapping of all ID data-blocks in current `bpy.data` to a set of all data-blocks using them.

For list of valid set members for key_types & value_types, see: [`bpy.types.KeyingSetPath.id_type`](bpy.types.KeyingSetPath.md#bpy.types.KeyingSetPath.id_type "bpy.types.KeyingSetPath.id_type").

**Parameters:**

- **subset** (Sequence[[`bpy.types.ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")] | None) – When passed, only these data-blocks and their users will be included as keys/values in the map.
- **key_types** (set[str] | None) – Filter the keys mapped by ID types.
- **value_types** (set[str] | None) – Filter the values in the set by ID types.

**Returns:**

dictionary that maps data-blocks ID’s to their users.

**Return type:**

dict[[`bpy.types.ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID"), set[[`bpy.types.ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")]]

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
| - [`Context.blend_data`](bpy.types.Context.md#bpy.types.Context.blend_data "bpy.types.Context.blend_data") | - [`RenderEngine.update`](bpy.types.RenderEngine.md#bpy.types.RenderEngine.update "bpy.types.RenderEngine.update") |
