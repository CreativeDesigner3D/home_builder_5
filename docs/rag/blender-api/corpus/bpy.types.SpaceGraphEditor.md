<!-- source: Blender Python API reference 5.2 / bpy.types.SpaceGraphEditor.html -->

<a id="spacegrapheditor-space"></a>

# SpaceGraphEditor(Space)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Space`](bpy.types.Space.md#bpy.types.Space "bpy.types.Space")

<a id="bpy.types.SpaceGraphEditor"></a>

### class bpy.types.SpaceGraphEditor(Space)

Graph Editor space data

<a id="bpy.types.SpaceGraphEditor.cursor_position_x"></a>

#### bpy.types.SpaceGraphEditor.cursor_position_x

Graph Editor 2D-Value cursor - X-Value component (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.SpaceGraphEditor.cursor_position_y"></a>

#### bpy.types.SpaceGraphEditor.cursor_position_y

Graph Editor 2D-Value cursor - Y-Value component (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.SpaceGraphEditor.dopesheet"></a>

#### bpy.types.SpaceGraphEditor.dopesheet

Settings for filtering animation data (readonly)

**Type:**

[`DopeSheet`](bpy.types.DopeSheet.md#bpy.types.DopeSheet "bpy.types.DopeSheet") | None

<a id="bpy.types.SpaceGraphEditor.has_ghost_curves"></a>

#### bpy.types.SpaceGraphEditor.has_ghost_curves

Graph Editor instance has some ghost curves stored (default False, readonly)

**Type:**

bool

<a id="bpy.types.SpaceGraphEditor.mode"></a>

#### bpy.types.SpaceGraphEditor.mode

Editing context being displayed (default `'FCURVES'`)

**Type:**

Literal[[Space Graph Mode Items](bpy_types_enum_items/space_graph_mode_items.md#rna-enum-space-graph-mode-items)]

<a id="bpy.types.SpaceGraphEditor.pivot_point"></a>

#### bpy.types.SpaceGraphEditor.pivot_point

Pivot center for rotation/scaling (default `'BOUNDING_BOX_CENTER'`)

**Type:**

Literal[‘BOUNDING_BOX_CENTER’, ‘CURSOR’, ‘INDIVIDUAL_ORIGINS’]

<a id="bpy.types.SpaceGraphEditor.show_cursor"></a>

#### bpy.types.SpaceGraphEditor.show_cursor

Show 2D cursor (default True)

**Type:**

bool

<a id="bpy.types.SpaceGraphEditor.show_extrapolation"></a>

#### bpy.types.SpaceGraphEditor.show_extrapolation

(default True)

**Type:**

bool

<a id="bpy.types.SpaceGraphEditor.show_handles"></a>

#### bpy.types.SpaceGraphEditor.show_handles

Show handles of Bézier control points (default True)

**Type:**

bool

<a id="bpy.types.SpaceGraphEditor.show_markers"></a>

#### bpy.types.SpaceGraphEditor.show_markers

If any exists, show markers in a separate row at the bottom of the editor (default False)

**Type:**

bool

<a id="bpy.types.SpaceGraphEditor.show_region_channels"></a>

#### bpy.types.SpaceGraphEditor.show_region_channels

(default False)

**Type:**

bool

<a id="bpy.types.SpaceGraphEditor.show_region_footer"></a>

#### bpy.types.SpaceGraphEditor.show_region_footer

(default False)

**Type:**

bool

<a id="bpy.types.SpaceGraphEditor.show_region_hud"></a>

#### bpy.types.SpaceGraphEditor.show_region_hud

(default False)

**Type:**

bool

<a id="bpy.types.SpaceGraphEditor.show_region_ui"></a>

#### bpy.types.SpaceGraphEditor.show_region_ui

(default False)

**Type:**

bool

<a id="bpy.types.SpaceGraphEditor.show_seconds"></a>

#### bpy.types.SpaceGraphEditor.show_seconds

Show timing as a timecode instead of frames (default False)

**Type:**

bool

<a id="bpy.types.SpaceGraphEditor.show_sliders"></a>

#### bpy.types.SpaceGraphEditor.show_sliders

Show sliders beside F-Curve channels (default False)

**Type:**

bool

<a id="bpy.types.SpaceGraphEditor.use_auto_lock_translation_axis"></a>

#### bpy.types.SpaceGraphEditor.use_auto_lock_translation_axis

Automatically locks the movement of keyframes to the dominant axis (default False)

**Type:**

bool

<a id="bpy.types.SpaceGraphEditor.use_auto_merge_keyframes"></a>

#### bpy.types.SpaceGraphEditor.use_auto_merge_keyframes

Automatically merge nearby keyframes (default True)

**Type:**

bool

<a id="bpy.types.SpaceGraphEditor.use_auto_normalization"></a>

#### bpy.types.SpaceGraphEditor.use_auto_normalization

Automatically recalculate curve normalization on every curve edit (default True)

**Type:**

bool

<a id="bpy.types.SpaceGraphEditor.use_normalization"></a>

#### bpy.types.SpaceGraphEditor.use_normalization

Display curves in normalized range from -1 to 1, for easier editing of multiple curves with different ranges (default False)

**Type:**

bool

<a id="bpy.types.SpaceGraphEditor.use_only_selected_keyframe_handles"></a>

#### bpy.types.SpaceGraphEditor.use_only_selected_keyframe_handles

Only show and edit handles of selected keyframes (default False)

**Type:**

bool

<a id="bpy.types.SpaceGraphEditor.use_realtime_update"></a>

#### bpy.types.SpaceGraphEditor.use_realtime_update

When transforming keyframes, changes to the animation data are flushed to other views (default True)

**Type:**

bool

<a id="bpy.types.SpaceGraphEditor.bl_rna_get_subclass"></a>

#### classmethod bpy.types.SpaceGraphEditor.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.SpaceGraphEditor.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.SpaceGraphEditor.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="bpy.types.SpaceGraphEditor.draw_handler_add"></a>

#### classmethod bpy.types.SpaceGraphEditor.draw_handler_add(callback, args, region_type, draw_type)

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

<a id="bpy.types.SpaceGraphEditor.draw_handler_remove"></a>

#### classmethod bpy.types.SpaceGraphEditor.draw_handler_remove(handler, region_type)

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
