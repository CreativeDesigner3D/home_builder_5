<!-- source: Blender Python API reference 5.2 / bpy.types.ToolSettings.html -->

<a id="toolsettings-bpy-struct"></a>

# ToolSettings(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.ToolSettings"></a>

### class bpy.types.ToolSettings(bpy_struct)

<a id="bpy.types.ToolSettings.anim_fix_to_cam_use_loc"></a>

#### bpy.types.ToolSettings.anim_fix_to_cam_use_loc

Create location keys when fixing to the scene camera (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.anim_fix_to_cam_use_rot"></a>

#### bpy.types.ToolSettings.anim_fix_to_cam_use_rot

Create rotation keys when fixing to the scene camera (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.anim_fix_to_cam_use_scale"></a>

#### bpy.types.ToolSettings.anim_fix_to_cam_use_scale

Create scale keys when fixing to the scene camera (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.anim_mirror_bone"></a>

#### bpy.types.ToolSettings.anim_mirror_bone

Bone to use for the mirroring (default “”, never None)

**Type:**

str

<a id="bpy.types.ToolSettings.anim_mirror_object"></a>

#### bpy.types.ToolSettings.anim_mirror_object

Object to mirror over. Leave empty and name a bone to always mirror over that bone of the active armature

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.ToolSettings.anim_relative_object"></a>

#### bpy.types.ToolSettings.anim_relative_object

Object to which matrices are made relative

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.ToolSettings.annotation_stroke_placement_view2d"></a>

#### bpy.types.ToolSettings.annotation_stroke_placement_view2d

(default `'IMAGE'`)

- `IMAGE`
  Image – Stick stroke to the image.
- `VIEW`
  View – Stick stroke to the view.

**Type:**

Literal[‘IMAGE’, ‘VIEW’]

<a id="bpy.types.ToolSettings.annotation_stroke_placement_view3d"></a>

#### bpy.types.ToolSettings.annotation_stroke_placement_view3d

How annotation strokes are orientated in 3D space (default `'CURSOR'`)

- `CURSOR`
  3D Cursor – Draw stroke at 3D cursor location.
- `VIEW`
  View – Stick stroke to the view.
- `SURFACE`
  Surface – Stick stroke to surfaces.

**Type:**

Literal[‘CURSOR’, ‘VIEW’, ‘SURFACE’]

<a id="bpy.types.ToolSettings.annotation_thickness"></a>

#### bpy.types.ToolSettings.annotation_thickness

Thickness of annotation strokes (in [1, 10], default 3)

**Type:**

int

<a id="bpy.types.ToolSettings.auto_keying_mode"></a>

#### bpy.types.ToolSettings.auto_keying_mode

Can add additional constraints on when auto keying can insert keyframes (default `'ADD_REPLACE_KEYS'`)

**Type:**

Literal[‘ADD_REPLACE_KEYS’, ‘REPLACE_KEYS’]

<a id="bpy.types.ToolSettings.curve_paint_settings"></a>

#### bpy.types.ToolSettings.curve_paint_settings

(readonly, never None)

**Type:**

[`CurvePaintSettings`](bpy.types.CurvePaintSettings.md#bpy.types.CurvePaintSettings "bpy.types.CurvePaintSettings")

<a id="bpy.types.ToolSettings.curves_sculpt"></a>

#### bpy.types.ToolSettings.curves_sculpt

(readonly)

**Type:**

[`CurvesSculpt`](bpy.types.CurvesSculpt.md#bpy.types.CurvesSculpt "bpy.types.CurvesSculpt") | None

<a id="bpy.types.ToolSettings.custom_bevel_profile_preset"></a>

#### bpy.types.ToolSettings.custom_bevel_profile_preset

Used for defining a profile’s path (readonly)

**Type:**

[`CurveProfile`](bpy.types.CurveProfile.md#bpy.types.CurveProfile "bpy.types.CurveProfile") | None

<a id="bpy.types.ToolSettings.double_threshold"></a>

#### bpy.types.ToolSettings.double_threshold

Threshold distance for Auto Merge (in [0, 1], default 0.001)

**Type:**

float

<a id="bpy.types.ToolSettings.gpencil_interpolate"></a>

#### bpy.types.ToolSettings.gpencil_interpolate

Settings for Grease Pencil interpolation tools (readonly)

**Type:**

[`GPencilInterpolateSettings`](bpy.types.GPencilInterpolateSettings.md#bpy.types.GPencilInterpolateSettings "bpy.types.GPencilInterpolateSettings") | None

<a id="bpy.types.ToolSettings.gpencil_paint"></a>

#### bpy.types.ToolSettings.gpencil_paint

(readonly)

**Type:**

[`GpPaint`](bpy.types.GpPaint.md#bpy.types.GpPaint "bpy.types.GpPaint") | None

<a id="bpy.types.ToolSettings.gpencil_sculpt"></a>

#### bpy.types.ToolSettings.gpencil_sculpt

Settings for stroke sculpting tools and brushes (readonly)

**Type:**

[`GPencilSculptSettings`](bpy.types.GPencilSculptSettings.md#bpy.types.GPencilSculptSettings "bpy.types.GPencilSculptSettings") | None

<a id="bpy.types.ToolSettings.gpencil_sculpt_paint"></a>

#### bpy.types.ToolSettings.gpencil_sculpt_paint

(readonly)

**Type:**

[`GpSculptPaint`](bpy.types.GpSculptPaint.md#bpy.types.GpSculptPaint "bpy.types.GpSculptPaint") | None

<a id="bpy.types.ToolSettings.gpencil_selectmode_edit"></a>

#### bpy.types.ToolSettings.gpencil_selectmode_edit

(default `'POINT'`)

**Type:**

Literal[[Grease Pencil Selectmode Items](bpy_types_enum_items/grease_pencil_selectmode_items.md#rna-enum-grease-pencil-selectmode-items)]

<a id="bpy.types.ToolSettings.gpencil_stroke_placement_view3d"></a>

#### bpy.types.ToolSettings.gpencil_stroke_placement_view3d

(default `'ORIGIN'`)

- `ORIGIN`
  Origin – Draw stroke at Object origin.
- `CURSOR`
  3D Cursor – Draw stroke at 3D cursor location.
- `SURFACE`
  Surface – Stick stroke to surfaces.
- `STROKE`
  Stroke – Stick stroke to other strokes.

**Type:**

Literal[‘ORIGIN’, ‘CURSOR’, ‘SURFACE’, ‘STROKE’]

<a id="bpy.types.ToolSettings.gpencil_stroke_snap_mode"></a>

#### bpy.types.ToolSettings.gpencil_stroke_snap_mode

(default `'NONE'`)

- `NONE`
  All Points – Snap to all points.
- `ENDS`
  End Points – Snap to first and last points and interpolate.
- `FIRST`
  First Point – Snap to first point.

**Type:**

Literal[‘NONE’, ‘ENDS’, ‘FIRST’]

<a id="bpy.types.ToolSettings.gpencil_surface_offset"></a>

#### bpy.types.ToolSettings.gpencil_surface_offset

Offset along the normal when drawing on surfaces (in [-inf, inf], default 0.15)

**Type:**

float

<a id="bpy.types.ToolSettings.gpencil_vertex_paint"></a>

#### bpy.types.ToolSettings.gpencil_vertex_paint

(readonly)

**Type:**

[`GpVertexPaint`](bpy.types.GpVertexPaint.md#bpy.types.GpVertexPaint "bpy.types.GpVertexPaint") | None

<a id="bpy.types.ToolSettings.gpencil_weight_paint"></a>

#### bpy.types.ToolSettings.gpencil_weight_paint

(readonly)

**Type:**

[`GpWeightPaint`](bpy.types.GpWeightPaint.md#bpy.types.GpWeightPaint "bpy.types.GpWeightPaint") | None

<a id="bpy.types.ToolSettings.image_paint"></a>

#### bpy.types.ToolSettings.image_paint

(readonly)

**Type:**

[`ImagePaint`](bpy.types.ImagePaint.md#bpy.types.ImagePaint "bpy.types.ImagePaint") | None

<a id="bpy.types.ToolSettings.keyframe_type"></a>

#### bpy.types.ToolSettings.keyframe_type

Type of keyframes to create when inserting keyframes (default `'KEYFRAME'`)

**Type:**

Literal[[Beztriple Keyframe Type Items](bpy_types_enum_items/beztriple_keyframe_type_items.md#rna-enum-beztriple-keyframe-type-items)]

<a id="bpy.types.ToolSettings.lock_markers"></a>

#### bpy.types.ToolSettings.lock_markers

Prevent marker editing (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.lock_object_mode"></a>

#### bpy.types.ToolSettings.lock_object_mode

Restrict selection to objects using the same mode as the active object, to prevent accidental mode switch when selecting (default True)

**Type:**

bool

<a id="bpy.types.ToolSettings.mesh_select_mode"></a>

#### bpy.types.ToolSettings.mesh_select_mode

Which mesh elements selection works on (array of 3 items, default (False, False, False))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[bool]

<a id="bpy.types.ToolSettings.normal_vector"></a>

#### bpy.types.ToolSettings.normal_vector

Normal vector used to copy, add or multiply (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.ToolSettings.paint_mode"></a>

#### bpy.types.ToolSettings.paint_mode

(readonly)

**Type:**

[`PaintModeSettings`](bpy.types.PaintModeSettings.md#bpy.types.PaintModeSettings "bpy.types.PaintModeSettings") | None

<a id="bpy.types.ToolSettings.particle_edit"></a>

#### bpy.types.ToolSettings.particle_edit

(readonly)

**Type:**

[`ParticleEdit`](bpy.types.ParticleEdit.md#bpy.types.ParticleEdit "bpy.types.ParticleEdit") | None

<a id="bpy.types.ToolSettings.plane_axis"></a>

#### bpy.types.ToolSettings.plane_axis

The axis used for placing the base region (default `'Z'`)

**Type:**

Literal[[Axis Xyz Items](bpy_types_enum_items/axis_xyz_items.md#rna-enum-axis-xyz-items)]

<a id="bpy.types.ToolSettings.plane_axis_auto"></a>

#### bpy.types.ToolSettings.plane_axis_auto

Select the closest axis when placing objects (surface overrides) (default True)

**Type:**

bool

<a id="bpy.types.ToolSettings.plane_depth"></a>

#### bpy.types.ToolSettings.plane_depth

The initial depth used when placing the cursor (default `'SURFACE'`)

- `SURFACE`
  Surface – Start placing on the surface, using the 3D cursor position as a fallback.
- `CURSOR_PLANE`
  Cursor Plane – Start placement using a point projected onto the orientation axis at the 3D cursor position.
- `CURSOR_VIEW`
  Cursor View – Start placement using a point projected onto the view plane at the 3D cursor position.

**Type:**

Literal[‘SURFACE’, ‘CURSOR_PLANE’, ‘CURSOR_VIEW’]

<a id="bpy.types.ToolSettings.plane_orientation"></a>

#### bpy.types.ToolSettings.plane_orientation

The initial depth used when placing the cursor (default `'SURFACE'`)

- `SURFACE`
  Surface – Use the surface normal (using the transform orientation as a fallback).
- `DEFAULT`
  Default – Use the current transform orientation.

**Type:**

Literal[‘SURFACE’, ‘DEFAULT’]

<a id="bpy.types.ToolSettings.playhead_snap_distance"></a>

#### bpy.types.ToolSettings.playhead_snap_distance

Maximum distance for snapping in pixels (in [-inf, inf], default 20)

**Type:**

int

<a id="bpy.types.ToolSettings.proportional_distance"></a>

#### bpy.types.ToolSettings.proportional_distance

Display size for proportional editing circle (in [1e-05, 5000], default 1.0)

**Type:**

float

<a id="bpy.types.ToolSettings.proportional_edit_falloff"></a>

#### bpy.types.ToolSettings.proportional_edit_falloff

Falloff type for proportional editing mode (default `'SMOOTH'`)

**Type:**

Literal[[Proportional Falloff Items](bpy_types_enum_items/proportional_falloff_items.md#rna-enum-proportional-falloff-items)]

<a id="bpy.types.ToolSettings.proportional_size"></a>

#### bpy.types.ToolSettings.proportional_size

Display size for proportional editing circle (in [1e-05, 5000], default 1.0)

**Type:**

float

<a id="bpy.types.ToolSettings.sculpt"></a>

#### bpy.types.ToolSettings.sculpt

(readonly)

**Type:**

[`Sculpt`](bpy.types.Sculpt.md#bpy.types.Sculpt "bpy.types.Sculpt") | None

<a id="bpy.types.ToolSettings.sequencer_tool_settings"></a>

#### bpy.types.ToolSettings.sequencer_tool_settings

(readonly, never None)

**Type:**

[`SequencerToolSettings`](bpy.types.SequencerToolSettings.md#bpy.types.SequencerToolSettings "bpy.types.SequencerToolSettings")

<a id="bpy.types.ToolSettings.show_uv_local_view"></a>

#### bpy.types.ToolSettings.show_uv_local_view

Display only faces with the currently displayed image assigned (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.snap_angle_increment_2d"></a>

#### bpy.types.ToolSettings.snap_angle_increment_2d

Angle used for rotation increments in 2D editors (in [0, 3.14159], default 0.0872665)

**Type:**

float

<a id="bpy.types.ToolSettings.snap_angle_increment_2d_precision"></a>

#### bpy.types.ToolSettings.snap_angle_increment_2d_precision

Precision angle used for rotation increments in 2D editors (in [0, 3.14159], default 0.0174533)

**Type:**

float

<a id="bpy.types.ToolSettings.snap_angle_increment_3d"></a>

#### bpy.types.ToolSettings.snap_angle_increment_3d

Angle used for rotation increments in 3D editors (in [0, 3.14159], default 0.0872665)

**Type:**

float

<a id="bpy.types.ToolSettings.snap_angle_increment_3d_precision"></a>

#### bpy.types.ToolSettings.snap_angle_increment_3d_precision

Precision angle used for rotation increments in 3D editors (in [0, 3.14159], default 0.0174533)

**Type:**

float

<a id="bpy.types.ToolSettings.snap_anim_element"></a>

#### bpy.types.ToolSettings.snap_anim_element

Type of element to snap to (default `'FRAME'`)

**Type:**

Literal[[Snap Animation Element Items](bpy_types_enum_items/snap_animation_element_items.md#rna-enum-snap-animation-element-items)]

<a id="bpy.types.ToolSettings.snap_elements"></a>

#### bpy.types.ToolSettings.snap_elements

Type of element to snap to (default {`'INCREMENT'`})

**Type:**

set[Literal[[Snap Element Items](bpy_types_enum_items/snap_element_items.md#rna-enum-snap-element-items)]]

<a id="bpy.types.ToolSettings.snap_elements_base"></a>

#### bpy.types.ToolSettings.snap_elements_base

Type of element for the “Snap Base” to snap to (default {`'INCREMENT'`})

- `INCREMENT`
  Increment – Snap to increments.
- `GRID`
  Grid – Snap to grid.
- `VERTEX`
  Vertex – Snap to vertices.
- `EDGE`
  Edge – Snap to edges.
- `FACE`
  Face – Snap by projecting onto faces.
- `VOLUME`
  Volume – Snap to volume.
- `EDGE_MIDPOINT`
  Edge Center – Snap to the middle of edges.
- `EDGE_PERPENDICULAR`
  Edge Perpendicular – Snap to the nearest point on an edge.
- `FACE_MIDPOINT`
  Face Center – Snap to the middle of faces.

**Type:**

set[Literal[‘INCREMENT’, ‘GRID’, ‘VERTEX’, ‘EDGE’, ‘FACE’, ‘VOLUME’, ‘EDGE_MIDPOINT’, ‘EDGE_PERPENDICULAR’, ‘FACE_MIDPOINT’]]

<a id="bpy.types.ToolSettings.snap_elements_individual"></a>

#### bpy.types.ToolSettings.snap_elements_individual

Type of element for individual transformed elements to snap to (default set())

- `FACE_PROJECT`
  Face Project – Snap by projecting onto faces.
- `FACE_NEAREST`
  Face Nearest – Snap to nearest point on faces.

**Type:**

set[Literal[‘FACE_PROJECT’, ‘FACE_NEAREST’]]

<a id="bpy.types.ToolSettings.snap_elements_tool"></a>

#### bpy.types.ToolSettings.snap_elements_tool

The target to use while snapping (default `'GEOMETRY'`)

- `GEOMETRY`
  Geometry – Snap to all geometry.
- `DEFAULT`
  Default – Use the current snap settings.

**Type:**

Literal[‘GEOMETRY’, ‘DEFAULT’]

<a id="bpy.types.ToolSettings.snap_face_nearest_steps"></a>

#### bpy.types.ToolSettings.snap_face_nearest_steps

Number of steps to break transformation into for face nearest snapping (in [1, 100], default 1)

**Type:**

int

<a id="bpy.types.ToolSettings.snap_playhead_element"></a>

#### bpy.types.ToolSettings.snap_playhead_element

Type of element to snap to (default {`'KEY'`, `'Strip'`})

- `FRAME`
  Frames – Snap to frame increments.
- `SECOND`
  Seconds – Snap to second increments.
- `MARKER`
  Markers – Snap to markers.
- `KEY`
  Keyframes – Snap to keyframes.
- `Strip`
  Strips – Snap to Strips.

**Type:**

set[Literal[‘FRAME’, ‘SECOND’, ‘MARKER’, ‘KEY’, ‘Strip’]]

<a id="bpy.types.ToolSettings.snap_playhead_frame_step"></a>

#### bpy.types.ToolSettings.snap_playhead_frame_step

At which interval to snap to frames (in [1, 32768], default 2)

**Type:**

int

<a id="bpy.types.ToolSettings.snap_playhead_second_step"></a>

#### bpy.types.ToolSettings.snap_playhead_second_step

At which interval to snap to seconds (in [1, 32768], default 1)

**Type:**

int

<a id="bpy.types.ToolSettings.snap_target"></a>

#### bpy.types.ToolSettings.snap_target

Which part to snap onto the target (default `'CLOSEST'`)

**Type:**

Literal[[Snap Source Items](bpy_types_enum_items/snap_source_items.md#rna-enum-snap-source-items)]

<a id="bpy.types.ToolSettings.snap_uv_element"></a>

#### bpy.types.ToolSettings.snap_uv_element

Type of element to snap to (default {`'INCREMENT'`})

- `INCREMENT`
  Increment – Snap to increments of grid.
- `GRID`
  Grid – Snap to grid.
- `VERTEX`
  Vertex – Snap to vertices.

**Type:**

set[Literal[‘INCREMENT’, ‘GRID’, ‘VERTEX’]]

<a id="bpy.types.ToolSettings.statvis"></a>

#### bpy.types.ToolSettings.statvis

(readonly, never None)

**Type:**

[`MeshStatVis`](bpy.types.MeshStatVis.md#bpy.types.MeshStatVis "bpy.types.MeshStatVis")

<a id="bpy.types.ToolSettings.transform_pivot_point"></a>

#### bpy.types.ToolSettings.transform_pivot_point

Pivot center for rotation/scaling (default `'MEDIAN_POINT'`)

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

<a id="bpy.types.ToolSettings.use_annotation_project_only_selected"></a>

#### bpy.types.ToolSettings.use_annotation_project_only_selected

Project the strokes only onto selected objects (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_annotation_stroke_endpoints"></a>

#### bpy.types.ToolSettings.use_annotation_stroke_endpoints

Only use the first and last parts of the stroke for snapping (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_auto_normalize"></a>

#### bpy.types.ToolSettings.use_auto_normalize

Ensure all bone-deforming vertex groups add up to 1.0 while weight painting or assigning to vertices (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_edge_path_live_unwrap"></a>

#### bpy.types.ToolSettings.use_edge_path_live_unwrap

Changing edge seams recalculates UV unwrap (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_gpencil_automerge_strokes"></a>

#### bpy.types.ToolSettings.use_gpencil_automerge_strokes

Join the last drawn stroke with previous strokes in the active layer by distance (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_gpencil_draw_additive"></a>

#### bpy.types.ToolSettings.use_gpencil_draw_additive

When creating new frames, the strokes from the previous/active frame are included as the basis for the new one (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_gpencil_draw_onback"></a>

#### bpy.types.ToolSettings.use_gpencil_draw_onback

New strokes are drawn below of all strokes in the layer (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_gpencil_project_only_selected"></a>

#### bpy.types.ToolSettings.use_gpencil_project_only_selected

Project the strokes only onto selected objects (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_gpencil_select_mask_point"></a>

#### bpy.types.ToolSettings.use_gpencil_select_mask_point

Only sculpt selected stroke points (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_gpencil_select_mask_segment"></a>

#### bpy.types.ToolSettings.use_gpencil_select_mask_segment

Only sculpt selected stroke points between other strokes (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_gpencil_select_mask_stroke"></a>

#### bpy.types.ToolSettings.use_gpencil_select_mask_stroke

Only sculpt selected strokes (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_gpencil_thumbnail_list"></a>

#### bpy.types.ToolSettings.use_gpencil_thumbnail_list

Show compact list of colors instead of thumbnails (default True)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_gpencil_vertex_select_mask_point"></a>

#### bpy.types.ToolSettings.use_gpencil_vertex_select_mask_point

Only paint selected stroke points (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_gpencil_vertex_select_mask_segment"></a>

#### bpy.types.ToolSettings.use_gpencil_vertex_select_mask_segment

Only paint selected stroke points between other strokes (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_gpencil_vertex_select_mask_stroke"></a>

#### bpy.types.ToolSettings.use_gpencil_vertex_select_mask_stroke

Only paint selected strokes (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_gpencil_weight_data_add"></a>

#### bpy.types.ToolSettings.use_gpencil_weight_data_add

Weight data for new strokes is added according to the current vertex group and weight. If no vertex group selected, weight is not added. (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_grease_pencil_multi_frame_editing"></a>

#### bpy.types.ToolSettings.use_grease_pencil_multi_frame_editing

Enable multi-frame editing (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_keyframe_cycle_aware"></a>

#### bpy.types.ToolSettings.use_keyframe_cycle_aware

For channels with cyclic extrapolation, keyframe insertion is automatically remapped inside the cycle time range, and keeps ends in sync. Curves newly added to actions with a Manual Frame Range and Cyclic Animation are automatically made cyclic. (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_keyframe_insert_auto"></a>

#### bpy.types.ToolSettings.use_keyframe_insert_auto

Automatically insert keyframes on modified properties (default True)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_keyframe_insert_keyingset"></a>

#### bpy.types.ToolSettings.use_keyframe_insert_keyingset

Automatic keyframe insertion using active Keying Set only (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_lock_relative"></a>

#### bpy.types.ToolSettings.use_lock_relative

Display bone-deforming groups as if all locked deform groups were deleted, and the remaining ones were re-normalized (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_mesh_automerge"></a>

#### bpy.types.ToolSettings.use_mesh_automerge

Automatically merge vertices moved to the same location (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_mesh_automerge_and_split"></a>

#### bpy.types.ToolSettings.use_mesh_automerge_and_split

Automatically split edges and faces (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_multipaint"></a>

#### bpy.types.ToolSettings.use_multipaint

Paint across the weights of all selected bones, maintaining their relative influence (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_proportional_action"></a>

#### bpy.types.ToolSettings.use_proportional_action

Proportional editing in action editor (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_proportional_connected"></a>

#### bpy.types.ToolSettings.use_proportional_connected

Proportional Editing using connected geometry only (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_proportional_edit"></a>

#### bpy.types.ToolSettings.use_proportional_edit

Proportional edit mode (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_proportional_edit_mask"></a>

#### bpy.types.ToolSettings.use_proportional_edit_mask

Proportional editing mask mode (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_proportional_edit_objects"></a>

#### bpy.types.ToolSettings.use_proportional_edit_objects

Proportional editing object mode (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_proportional_fcurve"></a>

#### bpy.types.ToolSettings.use_proportional_fcurve

Proportional editing in F-Curve editor (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_proportional_projected"></a>

#### bpy.types.ToolSettings.use_proportional_projected

Proportional Editing using screen space locations (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_record_with_nla"></a>

#### bpy.types.ToolSettings.use_record_with_nla

Add a new NLA Track + Strip for every loop/pass made over the animation to allow non-destructive tweaking (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_snap"></a>

#### bpy.types.ToolSettings.use_snap

Snap during transform (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_snap_align_rotation"></a>

#### bpy.types.ToolSettings.use_snap_align_rotation

Align rotation with the snapping target (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_snap_anim"></a>

#### bpy.types.ToolSettings.use_snap_anim

Enable snapping when transforming keyframes (default True)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_snap_backface_culling"></a>

#### bpy.types.ToolSettings.use_snap_backface_culling

Exclude back facing geometry from snapping (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_snap_driver"></a>

#### bpy.types.ToolSettings.use_snap_driver

Enable snapping when transforming keys in the Driver Editor (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_snap_driver_absolute"></a>

#### bpy.types.ToolSettings.use_snap_driver_absolute

Snap to full values (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_snap_edit"></a>

#### bpy.types.ToolSettings.use_snap_edit

Snap onto non-active objects in edit mode (edit mode only) (default True)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_snap_grid_absolute"></a>

#### bpy.types.ToolSettings.use_snap_grid_absolute

Absolute grid alignment while translating (based on the pivot center) (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_snap_node"></a>

#### bpy.types.ToolSettings.use_snap_node

Snap Node during transform (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_snap_nonedit"></a>

#### bpy.types.ToolSettings.use_snap_nonedit

Snap onto objects not in edit mode (edit mode only) (default True)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_snap_peel_object"></a>

#### bpy.types.ToolSettings.use_snap_peel_object

Consider objects as whole when finding volume center (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_snap_playhead"></a>

#### bpy.types.ToolSettings.use_snap_playhead

Snap playhead when scrubbing (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_snap_rotate"></a>

#### bpy.types.ToolSettings.use_snap_rotate

Rotate is affected by the snapping settings (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_snap_scale"></a>

#### bpy.types.ToolSettings.use_snap_scale

Scale is affected by snapping settings (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_snap_selectable"></a>

#### bpy.types.ToolSettings.use_snap_selectable

Snap only onto objects that are selectable (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_snap_self"></a>

#### bpy.types.ToolSettings.use_snap_self

Snap onto itself only if enabled (edit mode only) (default True)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_snap_sequencer"></a>

#### bpy.types.ToolSettings.use_snap_sequencer

Snap strips during transform (default True)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_snap_time_absolute"></a>

#### bpy.types.ToolSettings.use_snap_time_absolute

Absolute time alignment when transforming keyframes (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_snap_to_same_target"></a>

#### bpy.types.ToolSettings.use_snap_to_same_target

Snap only to target that source was initially near (“Face Nearest” only) (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_snap_translate"></a>

#### bpy.types.ToolSettings.use_snap_translate

Move is affected by snapping settings (default True)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_snap_uv"></a>

#### bpy.types.ToolSettings.use_snap_uv

Snap UV during transform (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_transform_correct_face_attributes"></a>

#### bpy.types.ToolSettings.use_transform_correct_face_attributes

Correct data such as UVs and color attributes when transforming (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_transform_correct_keep_connected"></a>

#### bpy.types.ToolSettings.use_transform_correct_keep_connected

During the Face Attributes correction, merge attributes connected to the same vertex (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_transform_data_origin"></a>

#### bpy.types.ToolSettings.use_transform_data_origin

Transform object origins, while leaving the shape in place (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_transform_pivot_point_align"></a>

#### bpy.types.ToolSettings.use_transform_pivot_point_align

Only transform object locations, without affecting rotation or scaling (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_transform_skip_children"></a>

#### bpy.types.ToolSettings.use_transform_skip_children

Transform the parents, leaving the children in place (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_uv_custom_region"></a>

#### bpy.types.ToolSettings.use_uv_custom_region

Custom defined region (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_uv_select_island"></a>

#### bpy.types.ToolSettings.use_uv_select_island

Island selection (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.use_uv_select_sync"></a>

#### bpy.types.ToolSettings.use_uv_select_sync

Keep UV and edit mode mesh selection in sync (default True)

**Type:**

bool

<a id="bpy.types.ToolSettings.uv_sculpt"></a>

#### bpy.types.ToolSettings.uv_sculpt

(readonly)

**Type:**

[`UvSculpt`](bpy.types.UvSculpt.md#bpy.types.UvSculpt "bpy.types.UvSculpt") | None

<a id="bpy.types.ToolSettings.uv_sculpt_all_islands"></a>

#### bpy.types.ToolSettings.uv_sculpt_all_islands

Brush operates on all islands (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.uv_sculpt_lock_borders"></a>

#### bpy.types.ToolSettings.uv_sculpt_lock_borders

Disable editing of boundary edges (default False)

**Type:**

bool

<a id="bpy.types.ToolSettings.uv_select_mode"></a>

#### bpy.types.ToolSettings.uv_select_mode

UV selection and display mode (default `'VERTEX'`)

**Type:**

Literal[[Mesh Select Mode Uv Items](bpy_types_enum_items/mesh_select_mode_uv_items.md#rna-enum-mesh-select-mode-uv-items)]

<a id="bpy.types.ToolSettings.uv_sticky_select_mode"></a>

#### bpy.types.ToolSettings.uv_sticky_select_mode

Method for extending UV vertex selection (default `'SHARED_LOCATION'`)

- `DISABLED`
  Disabled – Sticky vertex selection disabled.
- `SHARED_LOCATION`
  Shared Location – Select UVs that are at the same location and share a mesh vertex.
- `SHARED_VERTEX`
  Shared Vertex – Select UVs that share a mesh vertex, whether or not they are at the same location.

**Type:**

Literal[‘DISABLED’, ‘SHARED_LOCATION’, ‘SHARED_VERTEX’]

<a id="bpy.types.ToolSettings.vertex_group_subset"></a>

#### bpy.types.ToolSettings.vertex_group_subset

Filter Vertex groups for Display (default `'ALL'`)

- `ALL`
  All – All Vertex Groups.
- `BONE_DEFORM`
  Deform – Vertex Groups assigned to Deform Bones.
- `OTHER_DEFORM`
  Other – Vertex Groups assigned to non Deform Bones.

**Type:**

Literal[‘ALL’, ‘BONE_DEFORM’, ‘OTHER_DEFORM’]

<a id="bpy.types.ToolSettings.vertex_group_user"></a>

#### bpy.types.ToolSettings.vertex_group_user

Display unweighted vertices (default `'ACTIVE'`)

- `NONE`
  None.
- `ACTIVE`
  Active – Show vertices with no weights in the active group.
- `ALL`
  All – Show vertices with no weights in any group.

**Type:**

Literal[‘NONE’, ‘ACTIVE’, ‘ALL’]

<a id="bpy.types.ToolSettings.vertex_group_weight"></a>

#### bpy.types.ToolSettings.vertex_group_weight

Weight to assign in vertex groups (in [0, 1], default 1.0)

**Type:**

float

<a id="bpy.types.ToolSettings.vertex_paint"></a>

#### bpy.types.ToolSettings.vertex_paint

(readonly)

**Type:**

[`VertexPaint`](bpy.types.VertexPaint.md#bpy.types.VertexPaint "bpy.types.VertexPaint") | None

<a id="bpy.types.ToolSettings.weight_paint"></a>

#### bpy.types.ToolSettings.weight_paint

(readonly)

**Type:**

[`VertexPaint`](bpy.types.VertexPaint.md#bpy.types.VertexPaint "bpy.types.VertexPaint") | None

<a id="bpy.types.ToolSettings.workspace_tool_type"></a>

#### bpy.types.ToolSettings.workspace_tool_type

Action when dragging in the viewport (default `'FALLBACK'`)

**Type:**

Literal[‘DEFAULT’, ‘FALLBACK’]

<a id="bpy.types.ToolSettings.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ToolSettings.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ToolSettings.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ToolSettings.bl_rna_get_subclass_py(id, default=None, /)

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
| - `bpy.context.tool_settings` - [`Context.tool_settings`](bpy.types.Context.md#bpy.types.Context.tool_settings "bpy.types.Context.tool_settings") | - [`Scene.tool_settings`](bpy.types.Scene.md#bpy.types.Scene.tool_settings "bpy.types.Scene.tool_settings") |
