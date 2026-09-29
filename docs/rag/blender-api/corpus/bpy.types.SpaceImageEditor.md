<!-- source: Blender Python API reference 5.2 / bpy.types.SpaceImageEditor.html -->

<a id="spaceimageeditor-space"></a>

# SpaceImageEditor(Space)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Space`](bpy.types.Space.md#bpy.types.Space "bpy.types.Space")

<a id="bpy.types.SpaceImageEditor"></a>

### class bpy.types.SpaceImageEditor(Space)

Image and UV editor space data

<a id="bpy.types.SpaceImageEditor.annotation"></a>

#### bpy.types.SpaceImageEditor.annotation

Annotation data for this space

**Type:**

[`Annotation`](bpy.types.Annotation.md#bpy.types.Annotation "bpy.types.Annotation") | None

<a id="bpy.types.SpaceImageEditor.blend_factor"></a>

#### bpy.types.SpaceImageEditor.blend_factor

Overlay blending factor of rasterized mask (in [0, 1], default 0.7)

**Type:**

float

<a id="bpy.types.SpaceImageEditor.cursor_location"></a>

#### bpy.types.SpaceImageEditor.cursor_location

2D cursor location for this view (array of 2 items, in [-inf, inf], default (0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.SpaceImageEditor.display_channels"></a>

#### bpy.types.SpaceImageEditor.display_channels

Channels of the image to display (default `'COLOR'`)

- `COLOR_ALPHA`
  Color & Alpha – Display image with RGB colors and alpha transparency.
- `COLOR`
  Color – Display image with RGB colors.
- `ALPHA`
  Alpha – Display alpha transparency channel.
- `Z_BUFFER`
  Z-Buffer – Display Z-buffer associated with image (mapped from camera clip start to end).
- `RED`
  Red.
- `GREEN`
  Green.
- `BLUE`
  Blue.

**Type:**

Literal[‘COLOR_ALPHA’, ‘COLOR’, ‘ALPHA’, ‘Z_BUFFER’, ‘RED’, ‘GREEN’, ‘BLUE’]

<a id="bpy.types.SpaceImageEditor.image"></a>

#### bpy.types.SpaceImageEditor.image

Image displayed and edited in this space

**Type:**

[`Image`](bpy.types.Image.md#bpy.types.Image "bpy.types.Image") | None

<a id="bpy.types.SpaceImageEditor.image_user"></a>

#### bpy.types.SpaceImageEditor.image_user

Parameters defining which layer, pass and frame of the image is displayed (readonly, never None)

**Type:**

[`ImageUser`](bpy.types.ImageUser.md#bpy.types.ImageUser "bpy.types.ImageUser")

<a id="bpy.types.SpaceImageEditor.mask"></a>

#### bpy.types.SpaceImageEditor.mask

Mask displayed and edited in this space

**Type:**

[`Mask`](bpy.types.Mask.md#bpy.types.Mask "bpy.types.Mask") | None

<a id="bpy.types.SpaceImageEditor.mask_display_type"></a>

#### bpy.types.SpaceImageEditor.mask_display_type

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

<a id="bpy.types.SpaceImageEditor.mask_overlay_mode"></a>

#### bpy.types.SpaceImageEditor.mask_overlay_mode

Overlay mode of rasterized mask (default `'ALPHACHANNEL'`)

- `ALPHACHANNEL`
  Alpha Channel – Show alpha channel of the mask.
- `COMBINED`
  Combined – Combine space background image with the mask.

**Type:**

Literal[‘ALPHACHANNEL’, ‘COMBINED’]

<a id="bpy.types.SpaceImageEditor.mode"></a>

#### bpy.types.SpaceImageEditor.mode

Editing context being displayed (default `'VIEW'`)

**Type:**

Literal[[Space Image Mode All Items](bpy_types_enum_items/space_image_mode_all_items.md#rna-enum-space-image-mode-all-items)]

<a id="bpy.types.SpaceImageEditor.overlay"></a>

#### bpy.types.SpaceImageEditor.overlay

Settings for display of overlays in the UV/Image editor (readonly, never None)

**Type:**

[`SpaceImageOverlay`](bpy.types.SpaceImageOverlay.md#bpy.types.SpaceImageOverlay "bpy.types.SpaceImageOverlay")

<a id="bpy.types.SpaceImageEditor.pivot_point"></a>

#### bpy.types.SpaceImageEditor.pivot_point

Rotation/Scaling Pivot (default `'BOUNDING_BOX_CENTER'`)

- `BOUNDING_BOX_CENTER`
  Bounding Box Center – Pivot around bounding box center of selected object(s).
- `CURSOR`
  3D Cursor – Pivot around the 3D cursor.
- `INDIVIDUAL_ORIGINS`
  Individual Origins – Pivot around each object’s own origin.
- `MEDIAN_POINT`
  Median Point – Pivot around the median point of selected objects.
- `ACTIVE_ELEMENT`
  Active Element – Pivot around active object.

**Type:**

Literal[‘BOUNDING_BOX_CENTER’, ‘CURSOR’, ‘INDIVIDUAL_ORIGINS’, ‘MEDIAN_POINT’, ‘ACTIVE_ELEMENT’]

<a id="bpy.types.SpaceImageEditor.sample_histogram"></a>

#### bpy.types.SpaceImageEditor.sample_histogram

Sampled colors along line (readonly)

**Type:**

[`Histogram`](bpy.types.Histogram.md#bpy.types.Histogram "bpy.types.Histogram") | None

<a id="bpy.types.SpaceImageEditor.scopes"></a>

#### bpy.types.SpaceImageEditor.scopes

Scopes to visualize image statistics (readonly)

**Type:**

[`Scopes`](bpy.types.Scopes.md#bpy.types.Scopes "bpy.types.Scopes") | None

<a id="bpy.types.SpaceImageEditor.show_annotation"></a>

#### bpy.types.SpaceImageEditor.show_annotation

Show annotations for this view (default False)

**Type:**

bool

<a id="bpy.types.SpaceImageEditor.show_gizmo"></a>

#### bpy.types.SpaceImageEditor.show_gizmo

Show gizmos of all types (default True)

**Type:**

bool

<a id="bpy.types.SpaceImageEditor.show_gizmo_active_node"></a>

#### bpy.types.SpaceImageEditor.show_gizmo_active_node

Context sensitive gizmo for the active node (default True)

**Type:**

bool

<a id="bpy.types.SpaceImageEditor.show_gizmo_navigate"></a>

#### bpy.types.SpaceImageEditor.show_gizmo_navigate

Viewport navigation gizmo (default True)

**Type:**

bool

<a id="bpy.types.SpaceImageEditor.show_mask_overlay"></a>

#### bpy.types.SpaceImageEditor.show_mask_overlay

(default False)

**Type:**

bool

<a id="bpy.types.SpaceImageEditor.show_mask_spline"></a>

#### bpy.types.SpaceImageEditor.show_mask_spline

(default True)

**Type:**

bool

<a id="bpy.types.SpaceImageEditor.show_maskedit"></a>

#### bpy.types.SpaceImageEditor.show_maskedit

Show Mask editing related properties (default False, readonly)

**Type:**

bool

<a id="bpy.types.SpaceImageEditor.show_paint"></a>

#### bpy.types.SpaceImageEditor.show_paint

Show paint related properties (default False, readonly)

**Type:**

bool

<a id="bpy.types.SpaceImageEditor.show_region_asset_shelf"></a>

#### bpy.types.SpaceImageEditor.show_region_asset_shelf

Display a region with assets that may currently be relevant (such as brushes in paint modes, or poses in Pose Mode) (default False)

**Type:**

bool

<a id="bpy.types.SpaceImageEditor.show_region_hud"></a>

#### bpy.types.SpaceImageEditor.show_region_hud

(default False)

**Type:**

bool

<a id="bpy.types.SpaceImageEditor.show_region_tool_header"></a>

#### bpy.types.SpaceImageEditor.show_region_tool_header

(default False)

**Type:**

bool

<a id="bpy.types.SpaceImageEditor.show_region_toolbar"></a>

#### bpy.types.SpaceImageEditor.show_region_toolbar

(default False)

**Type:**

bool

<a id="bpy.types.SpaceImageEditor.show_region_ui"></a>

#### bpy.types.SpaceImageEditor.show_region_ui

(default False)

**Type:**

bool

<a id="bpy.types.SpaceImageEditor.show_render"></a>

#### bpy.types.SpaceImageEditor.show_render

Show render related properties (default False, readonly)

**Type:**

bool

<a id="bpy.types.SpaceImageEditor.show_repeat"></a>

#### bpy.types.SpaceImageEditor.show_repeat

Display the image repeated outside of the main view (default False)

**Type:**

bool

<a id="bpy.types.SpaceImageEditor.show_sequencer_scene"></a>

#### bpy.types.SpaceImageEditor.show_sequencer_scene

Display the render result for the sequencer scene instead of the active scene (default False)

**Type:**

bool

<a id="bpy.types.SpaceImageEditor.show_stereo_3d"></a>

#### bpy.types.SpaceImageEditor.show_stereo_3d

Display the image in Stereo 3D (default False)

**Type:**

bool

<a id="bpy.types.SpaceImageEditor.show_uvedit"></a>

#### bpy.types.SpaceImageEditor.show_uvedit

Show UV editing related properties (default False, readonly)

**Type:**

bool

<a id="bpy.types.SpaceImageEditor.ui_mode"></a>

#### bpy.types.SpaceImageEditor.ui_mode

Editing context being displayed (default `'VIEW'`)

- `VIEW`
  View – Inspect images or render results.
- `PAINT`
  Paint – Paint images in 2D.
- `MASK`
  Mask – View and edit masks.

**Type:**

Literal[‘VIEW’, ‘PAINT’, ‘MASK’]

<a id="bpy.types.SpaceImageEditor.use_image_pin"></a>

#### bpy.types.SpaceImageEditor.use_image_pin

Display current image regardless of object selection (default False)

**Type:**

bool

<a id="bpy.types.SpaceImageEditor.use_realtime_update"></a>

#### bpy.types.SpaceImageEditor.use_realtime_update

Update other affected window spaces automatically to reflect changes during interactive operations such as transform (default False)

**Type:**

bool

<a id="bpy.types.SpaceImageEditor.uv_editor"></a>

#### bpy.types.SpaceImageEditor.uv_editor

UV editor settings (readonly, never None)

**Type:**

[`SpaceUVEditor`](bpy.types.SpaceUVEditor.md#bpy.types.SpaceUVEditor "bpy.types.SpaceUVEditor")

<a id="bpy.types.SpaceImageEditor.zoom"></a>

#### bpy.types.SpaceImageEditor.zoom

Zoom factor (array of 2 items, in [-inf, inf], default (0.0, 0.0), readonly)

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.SpaceImageEditor.zoom_percentage"></a>

#### bpy.types.SpaceImageEditor.zoom_percentage

Zoom percentage (in [0.4, 80000], default 100.0)

**Type:**

float

<a id="bpy.types.SpaceImageEditor.bl_rna_get_subclass"></a>

#### classmethod bpy.types.SpaceImageEditor.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.SpaceImageEditor.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.SpaceImageEditor.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="bpy.types.SpaceImageEditor.draw_handler_add"></a>

#### classmethod bpy.types.SpaceImageEditor.draw_handler_add(callback, args, region_type, draw_type)

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

<a id="bpy.types.SpaceImageEditor.draw_handler_remove"></a>

#### classmethod bpy.types.SpaceImageEditor.draw_handler_remove(handler, region_type)

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
