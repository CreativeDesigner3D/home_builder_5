<!-- source: Blender Python API reference 5.2 / bpy.types.SpaceDopeSheetEditor.html -->

<a id="spacedopesheeteditor-space"></a>

# SpaceDopeSheetEditor(Space)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Space`](bpy.types.Space.md#bpy.types.Space "bpy.types.Space")

<a id="bpy.types.SpaceDopeSheetEditor"></a>

### class bpy.types.SpaceDopeSheetEditor(Space)

Dope Sheet space data

<a id="bpy.types.SpaceDopeSheetEditor.cache_cloth"></a>

#### bpy.types.SpaceDopeSheetEditor.cache_cloth

Show the active object’s cloth point cache (default False)

**Type:**

bool

<a id="bpy.types.SpaceDopeSheetEditor.cache_dynamicpaint"></a>

#### bpy.types.SpaceDopeSheetEditor.cache_dynamicpaint

Show the active object’s Dynamic Paint cache (default False)

**Type:**

bool

<a id="bpy.types.SpaceDopeSheetEditor.cache_particles"></a>

#### bpy.types.SpaceDopeSheetEditor.cache_particles

Show the active object’s particle point cache (default False)

**Type:**

bool

<a id="bpy.types.SpaceDopeSheetEditor.cache_rigidbody"></a>

#### bpy.types.SpaceDopeSheetEditor.cache_rigidbody

Show the active object’s Rigid Body cache (default False)

**Type:**

bool

<a id="bpy.types.SpaceDopeSheetEditor.cache_simulation_nodes"></a>

#### bpy.types.SpaceDopeSheetEditor.cache_simulation_nodes

Show the active object’s simulation nodes cache and bake data (default False)

**Type:**

bool

<a id="bpy.types.SpaceDopeSheetEditor.cache_smoke"></a>

#### bpy.types.SpaceDopeSheetEditor.cache_smoke

Show the active object’s smoke cache (default False)

**Type:**

bool

<a id="bpy.types.SpaceDopeSheetEditor.cache_softbody"></a>

#### bpy.types.SpaceDopeSheetEditor.cache_softbody

Show the active object’s softbody point cache (default False)

**Type:**

bool

<a id="bpy.types.SpaceDopeSheetEditor.dopesheet"></a>

#### bpy.types.SpaceDopeSheetEditor.dopesheet

Settings for filtering animation data (readonly)

**Type:**

[`DopeSheet`](bpy.types.DopeSheet.md#bpy.types.DopeSheet "bpy.types.DopeSheet") | None

<a id="bpy.types.SpaceDopeSheetEditor.mode"></a>

#### bpy.types.SpaceDopeSheetEditor.mode

Editing context being displayed (default `'ACTION'`)

- `DOPESHEET`
  Dope Sheet – Edit all keyframes in scene.
- `ACTION`
  Action Editor – Edit keyframes in active object’s Object-level action.
- `SHAPEKEY`
  Shape Key Editor – Edit keyframes in active object’s Shape Keys action.
- `GPENCIL`
  Grease Pencil – Edit timings for all Grease Pencil sketches in file.
- `MASK`
  Mask – Edit timings for Mask Editor splines.
- `CACHEFILE`
  Cache File – Edit timings for Cache File data-blocks.
- `TIMELINE`
  Timeline – Simple timeline view with playback controls in the header, without channel list, side-panel, or footer.

**Type:**

Literal[‘DOPESHEET’, ‘ACTION’, ‘SHAPEKEY’, ‘GPENCIL’, ‘MASK’, ‘CACHEFILE’, ‘TIMELINE’]

<a id="bpy.types.SpaceDopeSheetEditor.overlays"></a>

#### bpy.types.SpaceDopeSheetEditor.overlays

Settings for display of overlays (readonly, never None)

**Type:**

[`SpaceDopeSheetOverlay`](bpy.types.SpaceDopeSheetOverlay.md#bpy.types.SpaceDopeSheetOverlay "bpy.types.SpaceDopeSheetOverlay")

<a id="bpy.types.SpaceDopeSheetEditor.show_cache"></a>

#### bpy.types.SpaceDopeSheetEditor.show_cache

Show the status of cached frames in the timeline (default False)

**Type:**

bool

<a id="bpy.types.SpaceDopeSheetEditor.show_extremes"></a>

#### bpy.types.SpaceDopeSheetEditor.show_extremes

Mark keyframes where the key value flow changes direction, based on comparison with adjacent keys (default False)

**Type:**

bool

<a id="bpy.types.SpaceDopeSheetEditor.show_interpolation"></a>

#### bpy.types.SpaceDopeSheetEditor.show_interpolation

Display keyframe handle types and non-Bézier interpolation modes (default False)

**Type:**

bool

<a id="bpy.types.SpaceDopeSheetEditor.show_markers"></a>

#### bpy.types.SpaceDopeSheetEditor.show_markers

If any exists, show markers in a separate row at the bottom of the editor (default False)

**Type:**

bool

<a id="bpy.types.SpaceDopeSheetEditor.show_pose_markers"></a>

#### bpy.types.SpaceDopeSheetEditor.show_pose_markers

Show markers belonging to the active action instead of Scene markers (Action and Shape Key Editors only) (default False)

**Type:**

bool

<a id="bpy.types.SpaceDopeSheetEditor.show_region_channels"></a>

#### bpy.types.SpaceDopeSheetEditor.show_region_channels

(default False)

**Type:**

bool

<a id="bpy.types.SpaceDopeSheetEditor.show_region_footer"></a>

#### bpy.types.SpaceDopeSheetEditor.show_region_footer

(default False)

**Type:**

bool

<a id="bpy.types.SpaceDopeSheetEditor.show_region_hud"></a>

#### bpy.types.SpaceDopeSheetEditor.show_region_hud

(default False)

**Type:**

bool

<a id="bpy.types.SpaceDopeSheetEditor.show_region_ui"></a>

#### bpy.types.SpaceDopeSheetEditor.show_region_ui

(default False)

**Type:**

bool

<a id="bpy.types.SpaceDopeSheetEditor.show_seconds"></a>

#### bpy.types.SpaceDopeSheetEditor.show_seconds

Show timing as a timecode instead of frames (default False)

**Type:**

bool

<a id="bpy.types.SpaceDopeSheetEditor.show_sliders"></a>

#### bpy.types.SpaceDopeSheetEditor.show_sliders

Show sliders beside F-Curve channels (default False)

**Type:**

bool

<a id="bpy.types.SpaceDopeSheetEditor.ui_mode"></a>

#### bpy.types.SpaceDopeSheetEditor.ui_mode

Editing context being displayed (default `'ACTION'`)

- `DOPESHEET`
  Dope Sheet – Edit all keyframes in scene.
- `ACTION`
  Action Editor – Edit keyframes in active object’s Object-level action.
- `SHAPEKEY`
  Shape Key Editor – Edit keyframes in active object’s Shape Keys action.
- `GPENCIL`
  Grease Pencil – Edit timings for all Grease Pencil sketches in file.
- `MASK`
  Mask – Edit timings for Mask Editor splines.
- `CACHEFILE`
  Cache File – Edit timings for Cache File data-blocks.

**Type:**

Literal[‘DOPESHEET’, ‘ACTION’, ‘SHAPEKEY’, ‘GPENCIL’, ‘MASK’, ‘CACHEFILE’]

<a id="bpy.types.SpaceDopeSheetEditor.use_auto_merge_keyframes"></a>

#### bpy.types.SpaceDopeSheetEditor.use_auto_merge_keyframes

Automatically merge nearby keyframes (default True)

**Type:**

bool

<a id="bpy.types.SpaceDopeSheetEditor.use_marker_sync"></a>

#### bpy.types.SpaceDopeSheetEditor.use_marker_sync

Sync Markers with keyframe edits (default False)

**Type:**

bool

<a id="bpy.types.SpaceDopeSheetEditor.use_realtime_update"></a>

#### bpy.types.SpaceDopeSheetEditor.use_realtime_update

When transforming keyframes, changes to the animation data are flushed to other views (default True)

**Type:**

bool

<a id="bpy.types.SpaceDopeSheetEditor.bl_rna_get_subclass"></a>

#### classmethod bpy.types.SpaceDopeSheetEditor.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.SpaceDopeSheetEditor.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.SpaceDopeSheetEditor.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="bpy.types.SpaceDopeSheetEditor.draw_handler_add"></a>

#### classmethod bpy.types.SpaceDopeSheetEditor.draw_handler_add(callback, args, region_type, draw_type)

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

<a id="bpy.types.SpaceDopeSheetEditor.draw_handler_remove"></a>

#### classmethod bpy.types.SpaceDopeSheetEditor.draw_handler_remove(handler, region_type)

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
