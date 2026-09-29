<!-- source: Blender Python API reference 5.2 / bpy.types.SpaceSequenceEditor.html -->

<a id="spacesequenceeditor-space"></a>

# SpaceSequenceEditor(Space)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Space`](bpy.types.Space.md#bpy.types.Space "bpy.types.Space")

<a id="bpy.types.SpaceSequenceEditor"></a>

### class bpy.types.SpaceSequenceEditor(Space)

Sequence editor space data

<a id="bpy.types.SpaceSequenceEditor.annotation"></a>

#### bpy.types.SpaceSequenceEditor.annotation

Annotation data for this Preview region

**Type:**

[`Annotation`](bpy.types.Annotation.md#bpy.types.Annotation "bpy.types.Annotation") | None

<a id="bpy.types.SpaceSequenceEditor.cache_overlay"></a>

#### bpy.types.SpaceSequenceEditor.cache_overlay

Settings for display of overlays (readonly, never None)

**Type:**

[`SequencerCacheOverlay`](bpy.types.SequencerCacheOverlay.md#bpy.types.SequencerCacheOverlay "bpy.types.SequencerCacheOverlay")

<a id="bpy.types.SpaceSequenceEditor.cursor_location"></a>

#### bpy.types.SpaceSequenceEditor.cursor_location

2D cursor location for this view (array of 2 items, in [-inf, inf], default (0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.SpaceSequenceEditor.display_channel"></a>

#### bpy.types.SpaceSequenceEditor.display_channel

Preview all channels less than or equal to this value. 0 shows every channel, and negative values climb that many meta-strip levels if applicable, showing every channel there. (in [-5, 128], default 0)

**Type:**

int

<a id="bpy.types.SpaceSequenceEditor.display_mode"></a>

#### bpy.types.SpaceSequenceEditor.display_mode

View mode to use for displaying sequencer output (default `'IMAGE'`)

**Type:**

Literal[‘IMAGE’, ‘WAVEFORM’, ‘RGB_PARADE’, ‘VECTOR_SCOPE’, ‘HISTOGRAM’]

<a id="bpy.types.SpaceSequenceEditor.overlay_frame_type"></a>

#### bpy.types.SpaceSequenceEditor.overlay_frame_type

Overlay display method (default `'RECTANGLE'`)

- `RECTANGLE`
  Rectangle – Show rectangle area overlay.
- `REFERENCE`
  Reference – Show reference frame only.
- `CURRENT`
  Current – Show current frame only.

**Type:**

Literal[‘RECTANGLE’, ‘REFERENCE’, ‘CURRENT’]

<a id="bpy.types.SpaceSequenceEditor.preview_channels"></a>

#### bpy.types.SpaceSequenceEditor.preview_channels

Channels of the preview to display (default `'COLOR'`)

- `COLOR_ALPHA`
  Color & Alpha – Display image with RGB colors and alpha transparency.
- `COLOR`
  Color – Display image with RGB colors.

**Type:**

Literal[‘COLOR_ALPHA’, ‘COLOR’]

<a id="bpy.types.SpaceSequenceEditor.preview_overlay"></a>

#### bpy.types.SpaceSequenceEditor.preview_overlay

Settings for display of overlays (readonly, never None)

**Type:**

[`SequencerPreviewOverlay`](bpy.types.SequencerPreviewOverlay.md#bpy.types.SequencerPreviewOverlay "bpy.types.SequencerPreviewOverlay")

<a id="bpy.types.SpaceSequenceEditor.proxy_render_size"></a>

#### bpy.types.SpaceSequenceEditor.proxy_render_size

Display preview using full resolution or different proxy resolutions (default `'SCENE'`)

**Type:**

Literal[‘NONE’, ‘SCENE’, ‘PROXY_25’, ‘PROXY_50’, ‘PROXY_75’, ‘PROXY_100’]

<a id="bpy.types.SpaceSequenceEditor.show_frames"></a>

#### bpy.types.SpaceSequenceEditor.show_frames

Display frames rather than seconds (default False)

**Type:**

bool

<a id="bpy.types.SpaceSequenceEditor.show_gizmo"></a>

#### bpy.types.SpaceSequenceEditor.show_gizmo

Show gizmos of all types (default True)

**Type:**

bool

<a id="bpy.types.SpaceSequenceEditor.show_gizmo_context"></a>

#### bpy.types.SpaceSequenceEditor.show_gizmo_context

Context sensitive gizmos for the active item (default True)

**Type:**

bool

<a id="bpy.types.SpaceSequenceEditor.show_gizmo_navigate"></a>

#### bpy.types.SpaceSequenceEditor.show_gizmo_navigate

Viewport navigation gizmo (default True)

**Type:**

bool

<a id="bpy.types.SpaceSequenceEditor.show_gizmo_tool"></a>

#### bpy.types.SpaceSequenceEditor.show_gizmo_tool

Active tool gizmo (default True)

**Type:**

bool

<a id="bpy.types.SpaceSequenceEditor.show_markers"></a>

#### bpy.types.SpaceSequenceEditor.show_markers

If any exists, show markers in a separate row at the bottom of the editor (default False)

**Type:**

bool

<a id="bpy.types.SpaceSequenceEditor.show_overexposed"></a>

#### bpy.types.SpaceSequenceEditor.show_overexposed

Show overexposed areas with zebra stripes (in [0, 110], default 0)

**Type:**

int

<a id="bpy.types.SpaceSequenceEditor.show_overlays"></a>

#### bpy.types.SpaceSequenceEditor.show_overlays

(default False)

**Type:**

bool

<a id="bpy.types.SpaceSequenceEditor.show_region_channels"></a>

#### bpy.types.SpaceSequenceEditor.show_region_channels

(default False)

**Type:**

bool

<a id="bpy.types.SpaceSequenceEditor.show_region_footer"></a>

#### bpy.types.SpaceSequenceEditor.show_region_footer

(default False)

**Type:**

bool

<a id="bpy.types.SpaceSequenceEditor.show_region_hud"></a>

#### bpy.types.SpaceSequenceEditor.show_region_hud

(default False)

**Type:**

bool

<a id="bpy.types.SpaceSequenceEditor.show_region_tool_header"></a>

#### bpy.types.SpaceSequenceEditor.show_region_tool_header

(default False)

**Type:**

bool

<a id="bpy.types.SpaceSequenceEditor.show_region_toolbar"></a>

#### bpy.types.SpaceSequenceEditor.show_region_toolbar

(default False)

**Type:**

bool

<a id="bpy.types.SpaceSequenceEditor.show_region_ui"></a>

#### bpy.types.SpaceSequenceEditor.show_region_ui

(default False)

**Type:**

bool

<a id="bpy.types.SpaceSequenceEditor.show_scrubbing_region"></a>

#### bpy.types.SpaceSequenceEditor.show_scrubbing_region

Region with full playback range for scrubbing in the sequencer (default False)

**Type:**

bool

<a id="bpy.types.SpaceSequenceEditor.show_seconds"></a>

#### bpy.types.SpaceSequenceEditor.show_seconds

Show timing as a timecode instead of frames (default True)

**Type:**

bool

<a id="bpy.types.SpaceSequenceEditor.show_transform_preview"></a>

#### bpy.types.SpaceSequenceEditor.show_transform_preview

Show a preview of the start or end frame of a strip while transforming its respective handle (default False)

**Type:**

bool

<a id="bpy.types.SpaceSequenceEditor.timeline_overlay"></a>

#### bpy.types.SpaceSequenceEditor.timeline_overlay

Settings for display of overlays (readonly, never None)

**Type:**

[`SequencerTimelineOverlay`](bpy.types.SequencerTimelineOverlay.md#bpy.types.SequencerTimelineOverlay "bpy.types.SequencerTimelineOverlay")

<a id="bpy.types.SpaceSequenceEditor.use_clamp_view"></a>

#### bpy.types.SpaceSequenceEditor.use_clamp_view

Limit timeline height to maximum used channel slot (default False)

**Type:**

bool

<a id="bpy.types.SpaceSequenceEditor.use_marker_sync"></a>

#### bpy.types.SpaceSequenceEditor.use_marker_sync

Transform markers as well as strips (default False)

**Type:**

bool

<a id="bpy.types.SpaceSequenceEditor.use_proxies"></a>

#### bpy.types.SpaceSequenceEditor.use_proxies

Use optimized files for faster scrubbing when available (default False)

**Type:**

bool

<a id="bpy.types.SpaceSequenceEditor.use_zoom_to_fit"></a>

#### bpy.types.SpaceSequenceEditor.use_zoom_to_fit

Automatically zoom preview image to make it fully fit the region (default False)

**Type:**

bool

<a id="bpy.types.SpaceSequenceEditor.view_type"></a>

#### bpy.types.SpaceSequenceEditor.view_type

Type of the Sequencer view (sequencer, preview or both) (default `'SEQUENCER'`)

**Type:**

Literal[[Space Sequencer View Type Items](bpy_types_enum_items/space_sequencer_view_type_items.md#rna-enum-space-sequencer-view-type-items)]

<a id="bpy.types.SpaceSequenceEditor.zoom_percentage"></a>

#### bpy.types.SpaceSequenceEditor.zoom_percentage

Zoom percentage (in [0.4, 80000], default 100.0)

**Type:**

float

<a id="bpy.types.SpaceSequenceEditor.bl_rna_get_subclass"></a>

#### classmethod bpy.types.SpaceSequenceEditor.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.SpaceSequenceEditor.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.SpaceSequenceEditor.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="bpy.types.SpaceSequenceEditor.draw_handler_add"></a>

#### classmethod bpy.types.SpaceSequenceEditor.draw_handler_add(callback, args, region_type, draw_type)

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

<a id="bpy.types.SpaceSequenceEditor.draw_handler_remove"></a>

#### classmethod bpy.types.SpaceSequenceEditor.draw_handler_remove(handler, region_type)

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
