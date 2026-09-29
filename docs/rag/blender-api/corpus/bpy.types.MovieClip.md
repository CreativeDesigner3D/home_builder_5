<!-- source: Blender Python API reference 5.2 / bpy.types.MovieClip.html -->

<a id="movieclip-id"></a>

# MovieClip(ID)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")

<a id="bpy.types.MovieClip"></a>

### class bpy.types.MovieClip(ID)

MovieClip data-block referencing an external movie file

<a id="bpy.types.MovieClip.animation_data"></a>

#### bpy.types.MovieClip.animation_data

Animation data for this data-block (readonly)

**Type:**

[`AnimData`](bpy.types.AnimData.md#bpy.types.AnimData "bpy.types.AnimData") | None

<a id="bpy.types.MovieClip.annotation"></a>

#### bpy.types.MovieClip.annotation

Annotation data for this movie clip

**Type:**

[`Annotation`](bpy.types.Annotation.md#bpy.types.Annotation "bpy.types.Annotation") | None

<a id="bpy.types.MovieClip.colorspace_settings"></a>

#### bpy.types.MovieClip.colorspace_settings

Input color space settings (readonly)

**Type:**

[`ColorManagedInputColorspaceSettings`](bpy.types.ColorManagedInputColorspaceSettings.md#bpy.types.ColorManagedInputColorspaceSettings "bpy.types.ColorManagedInputColorspaceSettings") | None

<a id="bpy.types.MovieClip.display_aspect"></a>

#### bpy.types.MovieClip.display_aspect

Display Aspect for this clip, does not affect rendering (array of 2 items, in [0.1, inf], default (1.0, 1.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.MovieClip.filepath"></a>

#### bpy.types.MovieClip.filepath

Filename of the movie or sequence file (default “”, never None, blend relative `//` prefix supported)

**Type:**

str

<a id="bpy.types.MovieClip.fps"></a>

#### bpy.types.MovieClip.fps

Detected frame rate of the movie clip in frames per second (in [-inf, inf], default 0.0, readonly)

**Type:**

float

<a id="bpy.types.MovieClip.frame_duration"></a>

#### bpy.types.MovieClip.frame_duration

Detected duration of movie clip in frames (in [-inf, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.MovieClip.frame_offset"></a>

#### bpy.types.MovieClip.frame_offset

Offset of footage first frame relative to its file name (affects only how footage is loading, does not change data associated with a clip) (in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.MovieClip.frame_start"></a>

#### bpy.types.MovieClip.frame_start

Global scene frame number at which this movie starts playing (affects all data associated with a clip) (in [-inf, inf], default 1)

**Type:**

int

<a id="bpy.types.MovieClip.proxy"></a>

#### bpy.types.MovieClip.proxy

(readonly)

**Type:**

[`MovieClipProxy`](bpy.types.MovieClipProxy.md#bpy.types.MovieClipProxy "bpy.types.MovieClipProxy") | None

<a id="bpy.types.MovieClip.size"></a>

#### bpy.types.MovieClip.size

Width and height in pixels, zero when image data cannot be loaded (array of 2 items, in [-inf, inf], default (0, 0), readonly)

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[int]

<a id="bpy.types.MovieClip.source"></a>

#### bpy.types.MovieClip.source

Where the clip comes from (default `'SEQUENCE'`, readonly)

- `SEQUENCE`
  Image Sequence – Multiple image files, as a sequence.
- `MOVIE`
  Movie File – Movie file.

**Type:**

Literal[‘SEQUENCE’, ‘MOVIE’]

<a id="bpy.types.MovieClip.tracking"></a>

#### bpy.types.MovieClip.tracking

(readonly)

**Type:**

[`MovieTracking`](bpy.types.MovieTracking.md#bpy.types.MovieTracking "bpy.types.MovieTracking") | None

<a id="bpy.types.MovieClip.use_proxy"></a>

#### bpy.types.MovieClip.use_proxy

Use a preview proxy for this clip (default False)

**Type:**

bool

<a id="bpy.types.MovieClip.use_proxy_custom_directory"></a>

#### bpy.types.MovieClip.use_proxy_custom_directory

Create proxy images in a custom directory (default is movie location) (default False)

**Type:**

bool

<a id="bpy.types.MovieClip.metadata"></a>

#### bpy.types.MovieClip.metadata()

Retrieve metadata of the movie file

**Returns:**

Dict-like object containing the metadata

**Return type:**

[`IDPropertyWrapPtr`](bpy.types.IDPropertyWrapPtr.md#bpy.types.IDPropertyWrapPtr "bpy.types.IDPropertyWrapPtr")

<a id="bpy.types.MovieClip.bl_rna_get_subclass"></a>

#### classmethod bpy.types.MovieClip.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.MovieClip.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.MovieClip.bl_rna_get_subclass_py(id, default=None, /)

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
| - `bpy.context.edit_movieclip` - [`BlendData.movieclips`](bpy.types.BlendData.md#bpy.types.BlendData.movieclips "bpy.types.BlendData.movieclips") - [`BlendDataMovieClips.load`](bpy.types.BlendDataMovieClips.md#bpy.types.BlendDataMovieClips.load "bpy.types.BlendDataMovieClips.load") - [`BlendDataMovieClips.remove`](bpy.types.BlendDataMovieClips.md#bpy.types.BlendDataMovieClips.remove "bpy.types.BlendDataMovieClips.remove") - [`CameraBackgroundImage.clip`](bpy.types.CameraBackgroundImage.md#bpy.types.CameraBackgroundImage.clip "bpy.types.CameraBackgroundImage.clip") - [`CameraSolverConstraint.clip`](bpy.types.CameraSolverConstraint.md#bpy.types.CameraSolverConstraint.clip "bpy.types.CameraSolverConstraint.clip") - [`CompositorNodeKeyingScreen.clip`](bpy.types.CompositorNodeKeyingScreen.md#bpy.types.CompositorNodeKeyingScreen.clip "bpy.types.CompositorNodeKeyingScreen.clip") - [`CompositorNodeMovieClip.clip`](bpy.types.CompositorNodeMovieClip.md#bpy.types.CompositorNodeMovieClip.clip "bpy.types.CompositorNodeMovieClip.clip") - [`CompositorNodeMovieDistortion.clip`](bpy.types.CompositorNodeMovieDistortion.md#bpy.types.CompositorNodeMovieDistortion.clip "bpy.types.CompositorNodeMovieDistortion.clip") - [`CompositorNodePlaneTrackDeform.clip`](bpy.types.CompositorNodePlaneTrackDeform.md#bpy.types.CompositorNodePlaneTrackDeform.clip "bpy.types.CompositorNodePlaneTrackDeform.clip") | - [`CompositorNodeStabilize.clip`](bpy.types.CompositorNodeStabilize.md#bpy.types.CompositorNodeStabilize.clip "bpy.types.CompositorNodeStabilize.clip") - [`CompositorNodeTrackPos.clip`](bpy.types.CompositorNodeTrackPos.md#bpy.types.CompositorNodeTrackPos.clip "bpy.types.CompositorNodeTrackPos.clip") - [`FollowTrackConstraint.clip`](bpy.types.FollowTrackConstraint.md#bpy.types.FollowTrackConstraint.clip "bpy.types.FollowTrackConstraint.clip") - [`MovieClipStrip.clip`](bpy.types.MovieClipStrip.md#bpy.types.MovieClipStrip.clip "bpy.types.MovieClipStrip.clip") - [`ObjectSolverConstraint.clip`](bpy.types.ObjectSolverConstraint.md#bpy.types.ObjectSolverConstraint.clip "bpy.types.ObjectSolverConstraint.clip") - [`Scene.active_clip`](bpy.types.Scene.md#bpy.types.Scene.active_clip "bpy.types.Scene.active_clip") - [`SpaceClipEditor.clip`](bpy.types.SpaceClipEditor.md#bpy.types.SpaceClipEditor.clip "bpy.types.SpaceClipEditor.clip") - [`StripsMeta.new_clip`](bpy.types.StripsMeta.md#bpy.types.StripsMeta.new_clip "bpy.types.StripsMeta.new_clip") - [`StripsTopLevel.new_clip`](bpy.types.StripsTopLevel.md#bpy.types.StripsTopLevel.new_clip "bpy.types.StripsTopLevel.new_clip") |
