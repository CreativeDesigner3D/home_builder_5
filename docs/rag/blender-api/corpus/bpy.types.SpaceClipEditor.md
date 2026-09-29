<!-- source: Blender Python API reference 5.2 / bpy.types.SpaceClipEditor.html -->

<a id="spaceclipeditor-space"></a>

# SpaceClipEditor(Space)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Space`](bpy.types.Space.md#bpy.types.Space "bpy.types.Space")

<a id="bpy.types.SpaceClipEditor"></a>

### class bpy.types.SpaceClipEditor(Space)

Clip editor space data

<a id="bpy.types.SpaceClipEditor.annotation_source"></a>

#### bpy.types.SpaceClipEditor.annotation_source

Where the annotation comes from (default `'CLIP'`)

- `CLIP`
  Clip – Show annotation data-block which belongs to movie clip.
- `TRACK`
  Track – Show annotation data-block which belongs to active track.

**Type:**

Literal[‘CLIP’, ‘TRACK’]

<a id="bpy.types.SpaceClipEditor.blend_factor"></a>

#### bpy.types.SpaceClipEditor.blend_factor

Overlay blending factor of rasterized mask (in [0, 1], default 0.7)

**Type:**

float

<a id="bpy.types.SpaceClipEditor.clip"></a>

#### bpy.types.SpaceClipEditor.clip

Movie clip displayed and edited in this space

**Type:**

[`MovieClip`](bpy.types.MovieClip.md#bpy.types.MovieClip "bpy.types.MovieClip") | None

<a id="bpy.types.SpaceClipEditor.clip_user"></a>

#### bpy.types.SpaceClipEditor.clip_user

Parameters defining which frame of the movie clip is displayed (readonly, never None)

**Type:**

[`MovieClipUser`](bpy.types.MovieClipUser.md#bpy.types.MovieClipUser "bpy.types.MovieClipUser")

<a id="bpy.types.SpaceClipEditor.cursor_location"></a>

#### bpy.types.SpaceClipEditor.cursor_location

2D cursor location for this view (array of 2 items, in [-inf, inf], default (0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.SpaceClipEditor.lock_selection"></a>

#### bpy.types.SpaceClipEditor.lock_selection

Lock viewport to selected markers during playback (default False)

**Type:**

bool

<a id="bpy.types.SpaceClipEditor.lock_time_cursor"></a>

#### bpy.types.SpaceClipEditor.lock_time_cursor

Lock curves view to time cursor during playback and tracking (default False)

**Type:**

bool

<a id="bpy.types.SpaceClipEditor.mask"></a>

#### bpy.types.SpaceClipEditor.mask

Mask displayed and edited in this space

**Type:**

[`Mask`](bpy.types.Mask.md#bpy.types.Mask "bpy.types.Mask") | None

<a id="bpy.types.SpaceClipEditor.mask_display_type"></a>

#### bpy.types.SpaceClipEditor.mask_display_type

Display type for mask splines (default `'OUTLINE'`)

- `OUTLINE`
  Outline – Display white edges with black outline.
- `DASH`
  Dash – Display dashed black-white edges.
- `BLACK`
  Black – Display black edges.
- `WHITE`
  White – Display white edges.

**Type:**

Literal[‘OUTLINE’, ‘DASH’, ‘BLACK’, ‘WHITE’]

<a id="bpy.types.SpaceClipEditor.mask_overlay_mode"></a>

#### bpy.types.SpaceClipEditor.mask_overlay_mode

Overlay mode of rasterized mask (default `'ALPHACHANNEL'`)

- `ALPHACHANNEL`
  Alpha Channel – Show alpha channel of the mask.
- `COMBINED`
  Combined – Combine space background image with the mask.

**Type:**

Literal[‘ALPHACHANNEL’, ‘COMBINED’]

<a id="bpy.types.SpaceClipEditor.mode"></a>

#### bpy.types.SpaceClipEditor.mode

Editing context being displayed (default `'TRACKING'`)

**Type:**

Literal[[Clip Editor Mode Items](bpy_types_enum_items/clip_editor_mode_items.md#rna-enum-clip-editor-mode-items)]

<a id="bpy.types.SpaceClipEditor.overlay"></a>

#### bpy.types.SpaceClipEditor.overlay

Settings for display of overlays in the Movie Clip editor (readonly, never None)

**Type:**

[`SpaceClipOverlay`](bpy.types.SpaceClipOverlay.md#bpy.types.SpaceClipOverlay "bpy.types.SpaceClipOverlay")

<a id="bpy.types.SpaceClipEditor.path_length"></a>

#### bpy.types.SpaceClipEditor.path_length

Length of displaying path, in frames (in [0, inf], default 20)

**Type:**

int

<a id="bpy.types.SpaceClipEditor.pivot_point"></a>

#### bpy.types.SpaceClipEditor.pivot_point

Pivot center for rotation/scaling (default `'MEDIAN_POINT'`)

- `BOUNDING_BOX_CENTER`
  Bounding Box Center – Pivot around bounding box center of selected object(s).
- `CURSOR`
  2D Cursor – Pivot around the 2D cursor.
- `INDIVIDUAL_ORIGINS`
  Individual Origins – Pivot around each object’s own origin.
- `MEDIAN_POINT`
  Median Point – Pivot around the median point of selected objects.

**Type:**

Literal[‘BOUNDING_BOX_CENTER’, ‘CURSOR’, ‘INDIVIDUAL_ORIGINS’, ‘MEDIAN_POINT’]

<a id="bpy.types.SpaceClipEditor.scopes"></a>

#### bpy.types.SpaceClipEditor.scopes

Scopes to visualize movie clip statistics (readonly)

**Type:**

[`MovieClipScopes`](bpy.types.MovieClipScopes.md#bpy.types.MovieClipScopes "bpy.types.MovieClipScopes") | None

<a id="bpy.types.SpaceClipEditor.show_annotation"></a>

#### bpy.types.SpaceClipEditor.show_annotation

Show annotations for this view (default True)

**Type:**

bool

<a id="bpy.types.SpaceClipEditor.show_blue_channel"></a>

#### bpy.types.SpaceClipEditor.show_blue_channel

Show blue channel in the frame (default True)

**Type:**

bool

<a id="bpy.types.SpaceClipEditor.show_bundles"></a>

#### bpy.types.SpaceClipEditor.show_bundles

Show projection of 3D markers into footage (default False)

**Type:**

bool

<a id="bpy.types.SpaceClipEditor.show_disabled"></a>

#### bpy.types.SpaceClipEditor.show_disabled

Show disabled tracks from the footage (default True)

**Type:**

bool

<a id="bpy.types.SpaceClipEditor.show_filters"></a>

#### bpy.types.SpaceClipEditor.show_filters

Show filters for graph editor (default False)

**Type:**

bool

<a id="bpy.types.SpaceClipEditor.show_gizmo"></a>

#### bpy.types.SpaceClipEditor.show_gizmo

Show gizmos of all types (default True)

**Type:**

bool

<a id="bpy.types.SpaceClipEditor.show_gizmo_navigate"></a>

#### bpy.types.SpaceClipEditor.show_gizmo_navigate

Viewport navigation gizmo (default True)

**Type:**

bool

<a id="bpy.types.SpaceClipEditor.show_graph_frames"></a>

#### bpy.types.SpaceClipEditor.show_graph_frames

Show curve for per-frame average error (camera motion should be solved first) (default True)

**Type:**

bool

<a id="bpy.types.SpaceClipEditor.show_graph_hidden"></a>

#### bpy.types.SpaceClipEditor.show_graph_hidden

Include channels from objects/bone that are not visible (default False)

**Type:**

bool

<a id="bpy.types.SpaceClipEditor.show_graph_only_selected"></a>

#### bpy.types.SpaceClipEditor.show_graph_only_selected

Only include channels relating to selected objects and data (default False)

**Type:**

bool

<a id="bpy.types.SpaceClipEditor.show_graph_tracks_error"></a>

#### bpy.types.SpaceClipEditor.show_graph_tracks_error

Display the reprojection error curve for selected tracks (default False)

**Type:**

bool

<a id="bpy.types.SpaceClipEditor.show_graph_tracks_motion"></a>

#### bpy.types.SpaceClipEditor.show_graph_tracks_motion

Display speed curves for the selected tracks (default True)

**Type:**

bool

<a id="bpy.types.SpaceClipEditor.show_green_channel"></a>

#### bpy.types.SpaceClipEditor.show_green_channel

Show green channel in the frame (default True)

**Type:**

bool

<a id="bpy.types.SpaceClipEditor.show_grid"></a>

#### bpy.types.SpaceClipEditor.show_grid

Show grid showing lens distortion (default False)

**Type:**

bool

<a id="bpy.types.SpaceClipEditor.show_marker_pattern"></a>

#### bpy.types.SpaceClipEditor.show_marker_pattern

Show pattern boundbox for markers (default True)

**Type:**

bool

<a id="bpy.types.SpaceClipEditor.show_marker_search"></a>

#### bpy.types.SpaceClipEditor.show_marker_search

Show search boundbox for markers (default False)

**Type:**

bool

<a id="bpy.types.SpaceClipEditor.show_mask_overlay"></a>

#### bpy.types.SpaceClipEditor.show_mask_overlay

(default False)

**Type:**

bool

<a id="bpy.types.SpaceClipEditor.show_mask_spline"></a>

#### bpy.types.SpaceClipEditor.show_mask_spline

(default True)

**Type:**

bool

<a id="bpy.types.SpaceClipEditor.show_metadata"></a>

#### bpy.types.SpaceClipEditor.show_metadata

Show metadata of clip (default False)

**Type:**

bool

<a id="bpy.types.SpaceClipEditor.show_names"></a>

#### bpy.types.SpaceClipEditor.show_names

Show track names and status (default False)

**Type:**

bool

<a id="bpy.types.SpaceClipEditor.show_red_channel"></a>

#### bpy.types.SpaceClipEditor.show_red_channel

Show red channel in the frame (default True)

**Type:**

bool

<a id="bpy.types.SpaceClipEditor.show_region_channels"></a>

#### bpy.types.SpaceClipEditor.show_region_channels

(default False)

**Type:**

bool

<a id="bpy.types.SpaceClipEditor.show_region_hud"></a>

#### bpy.types.SpaceClipEditor.show_region_hud

(default False)

**Type:**

bool

<a id="bpy.types.SpaceClipEditor.show_region_toolbar"></a>

#### bpy.types.SpaceClipEditor.show_region_toolbar

(default False)

**Type:**

bool

<a id="bpy.types.SpaceClipEditor.show_region_ui"></a>

#### bpy.types.SpaceClipEditor.show_region_ui

(default False)

**Type:**

bool

<a id="bpy.types.SpaceClipEditor.show_seconds"></a>

#### bpy.types.SpaceClipEditor.show_seconds

Show timing as a timecode instead of frames (default False)

**Type:**

bool

<a id="bpy.types.SpaceClipEditor.show_stable"></a>

#### bpy.types.SpaceClipEditor.show_stable

Show stable footage in editor (if stabilization is enabled) (default False)

**Type:**

bool

<a id="bpy.types.SpaceClipEditor.show_tiny_markers"></a>

#### bpy.types.SpaceClipEditor.show_tiny_markers

Show markers in a more compact manner (default False)

**Type:**

bool

<a id="bpy.types.SpaceClipEditor.show_track_path"></a>

#### bpy.types.SpaceClipEditor.show_track_path

Show path of how track moves (default True)

**Type:**

bool

<a id="bpy.types.SpaceClipEditor.use_grayscale_preview"></a>

#### bpy.types.SpaceClipEditor.use_grayscale_preview

Display frame in grayscale mode (default False)

**Type:**

bool

<a id="bpy.types.SpaceClipEditor.use_manual_calibration"></a>

#### bpy.types.SpaceClipEditor.use_manual_calibration

Use manual calibration helpers (default False)

**Type:**

bool

<a id="bpy.types.SpaceClipEditor.use_mute_footage"></a>

#### bpy.types.SpaceClipEditor.use_mute_footage

Mute footage and show black background instead (default False)

**Type:**

bool

<a id="bpy.types.SpaceClipEditor.view"></a>

#### bpy.types.SpaceClipEditor.view

Type of the clip editor view (default `'CLIP'`)

- `CLIP`
  Clip – Show editing clip preview.
- `GRAPH`
  Graph – Show graph view for active element.
- `DOPESHEET`
  Dope Sheet – Dope Sheet view for tracking data.

**Type:**

Literal[‘CLIP’, ‘GRAPH’, ‘DOPESHEET’]

<a id="bpy.types.SpaceClipEditor.zoom_percentage"></a>

#### bpy.types.SpaceClipEditor.zoom_percentage

Zoom percentage (in [0.4, 80000], default 100.0)

**Type:**

float

<a id="bpy.types.SpaceClipEditor.bl_rna_get_subclass"></a>

#### classmethod bpy.types.SpaceClipEditor.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.SpaceClipEditor.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.SpaceClipEditor.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="bpy.types.SpaceClipEditor.draw_handler_add"></a>

#### classmethod bpy.types.SpaceClipEditor.draw_handler_add(callback, args, region_type, draw_type)

Add a new draw handler to this space type.
It will be called every time the specified region in the space type will be drawn.
Note: All arguments are positional only for now.

**Parameters:**

- **callback** (Callable[..., Any]) – A function that will be called when the region is drawn.
  It gets the specified arguments as input, it’s return value is ignored.
- **args** (tuple[Any, ...]) – Arguments that will be passed to the callback.
- **region_type** (str) – The region type the callback draws in; usually `WINDOW`. ([`bpy.types.Region.type`](bpy.types.Region.md#bpy.types.Region.type "bpy.types.Region.type"))
- **draw_type** (str) – Usually `POST_PIXEL` for 2D drawing and `POST_VIEW` for 3D drawing. In some cases `PRE_VIEW` can be used. `BACKDROP` can be used for backdrops in the node editor.

**Returns:**

Handler that can be removed later on.

**Return type:**

object

<a id="bpy.types.SpaceClipEditor.draw_handler_remove"></a>

#### classmethod bpy.types.SpaceClipEditor.draw_handler_remove(handler, region_type)

Remove a draw handler that was added previously.

**Parameters:**

- **handler** (object) – The draw handler that should be removed.
- **region_type** (str) – Region type the callback was added to.

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, Space.type, Space.show_locked_time, Space.show_region_header

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, Space.bl_rna_get_subclass, Space.bl_rna_get_subclass_py, Space.draw_handler_add, Space.draw_handler_remove
