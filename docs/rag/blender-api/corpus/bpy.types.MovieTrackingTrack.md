<!-- source: Blender Python API reference 5.2 / bpy.types.MovieTrackingTrack.html -->

<a id="movietrackingtrack-bpy-struct"></a>

# MovieTrackingTrack(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.MovieTrackingTrack"></a>

### class bpy.types.MovieTrackingTrack(bpy_struct)

Match-moving track data for tracking

<a id="bpy.types.MovieTrackingTrack.annotation"></a>

#### bpy.types.MovieTrackingTrack.annotation

Annotation data for this track

**Type:**

[`Annotation`](bpy.types.Annotation.md#bpy.types.Annotation "bpy.types.Annotation") | None

<a id="bpy.types.MovieTrackingTrack.average_error"></a>

#### bpy.types.MovieTrackingTrack.average_error

Average error of re-projection (in [-inf, inf], default 0.0, readonly)

**Type:**

float

<a id="bpy.types.MovieTrackingTrack.bundle"></a>

#### bpy.types.MovieTrackingTrack.bundle

Position of bundle reconstructed from this track (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0), readonly)

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.MovieTrackingTrack.color"></a>

#### bpy.types.MovieTrackingTrack.color

Color of the track in the Movie Clip Editor and the 3D viewport after a solve (array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.MovieTrackingTrack.correlation_min"></a>

#### bpy.types.MovieTrackingTrack.correlation_min

Minimal value of correlation between matched pattern and reference that is still treated as successful tracking (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.MovieTrackingTrack.frames_limit"></a>

#### bpy.types.MovieTrackingTrack.frames_limit

Every tracking cycle, this number of frames are tracked (in [0, 32767], default 0)

**Type:**

int

<a id="bpy.types.MovieTrackingTrack.has_bundle"></a>

#### bpy.types.MovieTrackingTrack.has_bundle

True if track has a valid bundle (default False, readonly)

**Type:**

bool

<a id="bpy.types.MovieTrackingTrack.hide"></a>

#### bpy.types.MovieTrackingTrack.hide

Track is hidden (default False)

**Type:**

bool

<a id="bpy.types.MovieTrackingTrack.lock"></a>

#### bpy.types.MovieTrackingTrack.lock

Track is locked and all changes to it are disabled (default False)

**Type:**

bool

<a id="bpy.types.MovieTrackingTrack.margin"></a>

#### bpy.types.MovieTrackingTrack.margin

Distance from image boundary at which marker stops tracking (in [0, 300], default 0)

**Type:**

int

<a id="bpy.types.MovieTrackingTrack.markers"></a>

#### bpy.types.MovieTrackingTrack.markers

Collection of markers in track (default None, readonly)

**Type:**

[`MovieTrackingMarkers`](bpy.types.MovieTrackingMarkers.md#bpy.types.MovieTrackingMarkers "bpy.types.MovieTrackingMarkers")[[`MovieTrackingMarker`](bpy.types.MovieTrackingMarker.md#bpy.types.MovieTrackingMarker "bpy.types.MovieTrackingMarker")]

<a id="bpy.types.MovieTrackingTrack.motion_model"></a>

#### bpy.types.MovieTrackingTrack.motion_model

Default motion model to use for tracking (default `'Loc'`)

- `Perspective`
  Perspective – Search for markers that are perspectively deformed (homography) between frames.
- `Affine`
  Affine – Search for markers that are affine-deformed (t, r, k, and skew) between frames.
- `LocRotScale`
  Location, Rotation & Scale – Search for markers that are translated, rotated, and scaled between frames.
- `LocScale`
  Location & Scale – Search for markers that are translated and scaled between frames.
- `LocRot`
  Location & Rotation – Search for markers that are translated and rotated between frames.
- `Loc`
  Location – Search for markers that are translated between frames.

**Type:**

Literal[‘Perspective’, ‘Affine’, ‘LocRotScale’, ‘LocScale’, ‘LocRot’, ‘Loc’]

<a id="bpy.types.MovieTrackingTrack.name"></a>

#### bpy.types.MovieTrackingTrack.name

Unique name of track (default “”, never None)

**Type:**

str

<a id="bpy.types.MovieTrackingTrack.offset"></a>

#### bpy.types.MovieTrackingTrack.offset

Offset of track from the parenting point (array of 2 items, in [-inf, inf], default (0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.MovieTrackingTrack.pattern_match"></a>

#### bpy.types.MovieTrackingTrack.pattern_match

Track pattern from given frame when tracking marker to next frame (default `'KEYFRAME'`)

- `KEYFRAME`
  Keyframe – Track pattern from keyframe to next frame.
- `PREV_FRAME`
  Previous frame – Track pattern from current frame to next frame.

**Type:**

Literal[‘KEYFRAME’, ‘PREV_FRAME’]

<a id="bpy.types.MovieTrackingTrack.select"></a>

#### bpy.types.MovieTrackingTrack.select

Track is selected (default False)

**Type:**

bool

<a id="bpy.types.MovieTrackingTrack.select_anchor"></a>

#### bpy.types.MovieTrackingTrack.select_anchor

Track’s anchor point is selected (default False)

**Type:**

bool

<a id="bpy.types.MovieTrackingTrack.select_pattern"></a>

#### bpy.types.MovieTrackingTrack.select_pattern

Track’s pattern area is selected (default False)

**Type:**

bool

<a id="bpy.types.MovieTrackingTrack.select_search"></a>

#### bpy.types.MovieTrackingTrack.select_search

Track’s search area is selected (default False)

**Type:**

bool

<a id="bpy.types.MovieTrackingTrack.use_alpha_preview"></a>

#### bpy.types.MovieTrackingTrack.use_alpha_preview

Apply track’s mask on displaying preview (default False)

**Type:**

bool

<a id="bpy.types.MovieTrackingTrack.use_blue_channel"></a>

#### bpy.types.MovieTrackingTrack.use_blue_channel

Use blue channel from footage for tracking (default True)

**Type:**

bool

<a id="bpy.types.MovieTrackingTrack.use_brute"></a>

#### bpy.types.MovieTrackingTrack.use_brute

Use a brute-force translation only pre-track before refinement (default False)

**Type:**

bool

<a id="bpy.types.MovieTrackingTrack.use_custom_color"></a>

#### bpy.types.MovieTrackingTrack.use_custom_color

Use custom color instead of theme-defined (default False)

**Type:**

bool

<a id="bpy.types.MovieTrackingTrack.use_grayscale_preview"></a>

#### bpy.types.MovieTrackingTrack.use_grayscale_preview

Display what the tracking algorithm sees in the preview (default False)

**Type:**

bool

<a id="bpy.types.MovieTrackingTrack.use_green_channel"></a>

#### bpy.types.MovieTrackingTrack.use_green_channel

Use green channel from footage for tracking (default True)

**Type:**

bool

<a id="bpy.types.MovieTrackingTrack.use_mask"></a>

#### bpy.types.MovieTrackingTrack.use_mask

Use a Grease Pencil data-block as a mask to use only specified areas of pattern when tracking (default False)

**Type:**

bool

<a id="bpy.types.MovieTrackingTrack.use_normalization"></a>

#### bpy.types.MovieTrackingTrack.use_normalization

Normalize light intensities while tracking (slower) (default False)

**Type:**

bool

<a id="bpy.types.MovieTrackingTrack.use_red_channel"></a>

#### bpy.types.MovieTrackingTrack.use_red_channel

Use red channel from footage for tracking (default True)

**Type:**

bool

<a id="bpy.types.MovieTrackingTrack.weight"></a>

#### bpy.types.MovieTrackingTrack.weight

Influence of this track on a final solution (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.MovieTrackingTrack.weight_stab"></a>

#### bpy.types.MovieTrackingTrack.weight_stab

Influence of this track on 2D stabilization (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.MovieTrackingTrack.bl_rna_get_subclass"></a>

#### classmethod bpy.types.MovieTrackingTrack.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.MovieTrackingTrack.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.MovieTrackingTrack.bl_rna_get_subclass_py(id, default=None, /)

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
| - `bpy.context.selected_movieclip_tracks` - [`MovieTracking.tracks`](bpy.types.MovieTracking.md#bpy.types.MovieTracking.tracks "bpy.types.MovieTracking.tracks") - [`MovieTrackingObject.tracks`](bpy.types.MovieTrackingObject.md#bpy.types.MovieTrackingObject.tracks "bpy.types.MovieTrackingObject.tracks") - [`MovieTrackingObjectPlaneTracks.active`](bpy.types.MovieTrackingObjectPlaneTracks.md#bpy.types.MovieTrackingObjectPlaneTracks.active "bpy.types.MovieTrackingObjectPlaneTracks.active") - [`MovieTrackingObjectTracks.active`](bpy.types.MovieTrackingObjectTracks.md#bpy.types.MovieTrackingObjectTracks.active "bpy.types.MovieTrackingObjectTracks.active") - [`MovieTrackingObjectTracks.new`](bpy.types.MovieTrackingObjectTracks.md#bpy.types.MovieTrackingObjectTracks.new "bpy.types.MovieTrackingObjectTracks.new") | - [`MovieTrackingStabilization.rotation_tracks`](bpy.types.MovieTrackingStabilization.md#bpy.types.MovieTrackingStabilization.rotation_tracks "bpy.types.MovieTrackingStabilization.rotation_tracks") - [`MovieTrackingStabilization.tracks`](bpy.types.MovieTrackingStabilization.md#bpy.types.MovieTrackingStabilization.tracks "bpy.types.MovieTrackingStabilization.tracks") - [`MovieTrackingTracks.active`](bpy.types.MovieTrackingTracks.md#bpy.types.MovieTrackingTracks.active "bpy.types.MovieTrackingTracks.active") - [`MovieTrackingTracks.new`](bpy.types.MovieTrackingTracks.md#bpy.types.MovieTrackingTracks.new "bpy.types.MovieTrackingTracks.new") - [`UILayout.template_marker`](bpy.types.UILayout.md#bpy.types.UILayout.template_marker "bpy.types.UILayout.template_marker") |
