<!-- source: Blender Python API reference 5.2 / bpy.types.View3DOverlay.html -->

<a id="view3doverlay-bpy-struct"></a>

# View3DOverlay(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.View3DOverlay"></a>

### class bpy.types.View3DOverlay(bpy_struct)

Settings for display of overlays in the 3D viewport

<a id="bpy.types.View3DOverlay.bone_wire_alpha"></a>

#### bpy.types.View3DOverlay.bone_wire_alpha

Maximum opacity of bones in wireframe display mode (in [0, inf], default 1.0)

**Type:**

float

<a id="bpy.types.View3DOverlay.display_handle"></a>

#### bpy.types.View3DOverlay.display_handle

Limit the display of curve handles in Edit Mode (default `'SELECTED'`)

**Type:**

Literal[‘NONE’, ‘SELECTED’, ‘ALL’]

<a id="bpy.types.View3DOverlay.fade_inactive_alpha"></a>

#### bpy.types.View3DOverlay.fade_inactive_alpha

Strength of the fade effect (in [0, 1], default 0.4)

**Type:**

float

<a id="bpy.types.View3DOverlay.gpencil_fade_layer"></a>

#### bpy.types.View3DOverlay.gpencil_fade_layer

Fade layer opacity for Grease Pencil layers except the active one (in [0, 1], default 0.5)

**Type:**

float

<a id="bpy.types.View3DOverlay.gpencil_fade_objects"></a>

#### bpy.types.View3DOverlay.gpencil_fade_objects

Fade factor (in [0, 1], default 0.5)

**Type:**

float

<a id="bpy.types.View3DOverlay.gpencil_grid_color"></a>

#### bpy.types.View3DOverlay.gpencil_grid_color

Canvas grid color (array of 3 items, in [0, 1], default (0.5, 0.5, 0.5))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.View3DOverlay.gpencil_grid_offset"></a>

#### bpy.types.View3DOverlay.gpencil_grid_offset

Canvas grid offset (array of 2 items, in [-inf, inf], default (0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.View3DOverlay.gpencil_grid_opacity"></a>

#### bpy.types.View3DOverlay.gpencil_grid_opacity

Canvas grid opacity (in [0.1, 1], default 0.9)

**Type:**

float

<a id="bpy.types.View3DOverlay.gpencil_grid_scale"></a>

#### bpy.types.View3DOverlay.gpencil_grid_scale

Canvas grid scale (array of 2 items, in [0, inf], default (1.0, 1.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.View3DOverlay.gpencil_grid_subdivisions"></a>

#### bpy.types.View3DOverlay.gpencil_grid_subdivisions

Canvas grid subdivisions (in [1, 100], default 4)

**Type:**

int

<a id="bpy.types.View3DOverlay.gpencil_vertex_paint_opacity"></a>

#### bpy.types.View3DOverlay.gpencil_vertex_paint_opacity

Vertex Paint mix factor (in [0, 1], default 1.0)

**Type:**

float

<a id="bpy.types.View3DOverlay.grid_lines"></a>

#### bpy.types.View3DOverlay.grid_lines

Number of grid lines to display in perspective view (in [0, 1024], default 16)

**Type:**

int

<a id="bpy.types.View3DOverlay.grid_scale"></a>

#### bpy.types.View3DOverlay.grid_scale

Multiplier for the distance between 3D View grid lines (in [0, inf], default 1.0)

**Type:**

float

<a id="bpy.types.View3DOverlay.grid_scale_unit"></a>

#### bpy.types.View3DOverlay.grid_scale_unit

Grid cell size scaled by scene unit system settings (in [-inf, inf], default 0.0, readonly)

**Type:**

float

<a id="bpy.types.View3DOverlay.grid_subdivisions"></a>

#### bpy.types.View3DOverlay.grid_subdivisions

Number of subdivisions between grid lines (in [1, 1024], default 10)

**Type:**

int

<a id="bpy.types.View3DOverlay.normals_constant_screen_size"></a>

#### bpy.types.View3DOverlay.normals_constant_screen_size

Screen size for normals in the 3D view (in [0, 100000], default 7.0)

**Type:**

float

<a id="bpy.types.View3DOverlay.normals_length"></a>

#### bpy.types.View3DOverlay.normals_length

Display size for normals in the 3D view (in [1e-05, 100000], default 0.1)

**Type:**

float

<a id="bpy.types.View3DOverlay.retopology_offset"></a>

#### bpy.types.View3DOverlay.retopology_offset

Offset used to draw edit mesh in front of other geometry (in [0, inf], default 0.01)

**Type:**

float

<a id="bpy.types.View3DOverlay.sculpt_curves_cage_opacity"></a>

#### bpy.types.View3DOverlay.sculpt_curves_cage_opacity

Opacity of the cage overlay in curves sculpt mode (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.View3DOverlay.sculpt_mode_face_sets_opacity"></a>

#### bpy.types.View3DOverlay.sculpt_mode_face_sets_opacity

(in [0, 1], default 1.0)

**Type:**

float

<a id="bpy.types.View3DOverlay.sculpt_mode_mask_opacity"></a>

#### bpy.types.View3DOverlay.sculpt_mode_mask_opacity

(in [0, 1], default 0.75)

**Type:**

float

<a id="bpy.types.View3DOverlay.show_annotation"></a>

#### bpy.types.View3DOverlay.show_annotation

Show annotations for this view (default True)

**Type:**

bool

<a id="bpy.types.View3DOverlay.show_axis_x"></a>

#### bpy.types.View3DOverlay.show_axis_x

Show the X axis line (default True)

**Type:**

bool

<a id="bpy.types.View3DOverlay.show_axis_y"></a>

#### bpy.types.View3DOverlay.show_axis_y

Show the Y axis line (default True)

**Type:**

bool

<a id="bpy.types.View3DOverlay.show_axis_z"></a>

#### bpy.types.View3DOverlay.show_axis_z

Show the Z axis line (default False)

**Type:**

bool

<a id="bpy.types.View3DOverlay.show_bones"></a>

#### bpy.types.View3DOverlay.show_bones

Display bones (disable to show motion paths only) (default True)

**Type:**

bool

<a id="bpy.types.View3DOverlay.show_camera_guides"></a>

#### bpy.types.View3DOverlay.show_camera_guides

Show camera composition guides (default True)

**Type:**

bool

<a id="bpy.types.View3DOverlay.show_camera_passepartout"></a>

#### bpy.types.View3DOverlay.show_camera_passepartout

Show camera passepartout (default True)

**Type:**

bool

<a id="bpy.types.View3DOverlay.show_cursor"></a>

#### bpy.types.View3DOverlay.show_cursor

Display 3D Cursor Overlay (default True)

**Type:**

bool

<a id="bpy.types.View3DOverlay.show_curve_normals"></a>

#### bpy.types.View3DOverlay.show_curve_normals

Display 3D curve normals in Edit Mode (default False)

**Type:**

bool

<a id="bpy.types.View3DOverlay.show_edge_bevel_weight"></a>

#### bpy.types.View3DOverlay.show_edge_bevel_weight

Display weights created for the Bevel modifier (default True)

**Type:**

bool

<a id="bpy.types.View3DOverlay.show_edge_crease"></a>

#### bpy.types.View3DOverlay.show_edge_crease

Display creases created for Subdivision Surface modifier (default True)

**Type:**

bool

<a id="bpy.types.View3DOverlay.show_edge_seams"></a>

#### bpy.types.View3DOverlay.show_edge_seams

Display UV unwrapping seams (default True)

**Type:**

bool

<a id="bpy.types.View3DOverlay.show_edge_sharp"></a>

#### bpy.types.View3DOverlay.show_edge_sharp

Display sharp edges, used with the Edge Split modifier (default True)

**Type:**

bool

<a id="bpy.types.View3DOverlay.show_extra_edge_angle"></a>

#### bpy.types.View3DOverlay.show_extra_edge_angle

Display selected edge angle, using global values when set in the transform panel (default False)

**Type:**

bool

<a id="bpy.types.View3DOverlay.show_extra_edge_length"></a>

#### bpy.types.View3DOverlay.show_extra_edge_length

Display selected edge lengths, using global values when set in the transform panel (default False)

**Type:**

bool

<a id="bpy.types.View3DOverlay.show_extra_face_angle"></a>

#### bpy.types.View3DOverlay.show_extra_face_angle

Display the angles in the selected edges, using global values when set in the transform panel (default False)

**Type:**

bool

<a id="bpy.types.View3DOverlay.show_extra_face_area"></a>

#### bpy.types.View3DOverlay.show_extra_face_area

Display the area of selected faces, using global values when set in the transform panel (default False)

**Type:**

bool

<a id="bpy.types.View3DOverlay.show_extra_indices"></a>

#### bpy.types.View3DOverlay.show_extra_indices

Display the index numbers of selected vertices, edges, and faces (default False)

**Type:**

bool

<a id="bpy.types.View3DOverlay.show_extras"></a>

#### bpy.types.View3DOverlay.show_extras

Object details, including empty wire, cameras and other visual guides (default True)

**Type:**

bool

<a id="bpy.types.View3DOverlay.show_face_center"></a>

#### bpy.types.View3DOverlay.show_face_center

Display face center when face selection is enabled in solid shading modes (default False)

**Type:**

bool

<a id="bpy.types.View3DOverlay.show_face_normals"></a>

#### bpy.types.View3DOverlay.show_face_normals

Display face normals as lines (default False)

**Type:**

bool

<a id="bpy.types.View3DOverlay.show_face_orientation"></a>

#### bpy.types.View3DOverlay.show_face_orientation

Show the Face Orientation Overlay (default False)

**Type:**

bool

<a id="bpy.types.View3DOverlay.show_faces"></a>

#### bpy.types.View3DOverlay.show_faces

Display a face selection overlay (default True)

**Type:**

bool

<a id="bpy.types.View3DOverlay.show_fade_inactive"></a>

#### bpy.types.View3DOverlay.show_fade_inactive

Fade inactive geometry using the viewport background color (default False)

**Type:**

bool

<a id="bpy.types.View3DOverlay.show_floor"></a>

#### bpy.types.View3DOverlay.show_floor

Show the ground plane grid (default True)

**Type:**

bool

<a id="bpy.types.View3DOverlay.show_freestyle_edge_marks"></a>

#### bpy.types.View3DOverlay.show_freestyle_edge_marks

Display Freestyle edge marks, used with the Freestyle renderer (default True)

**Type:**

bool

<a id="bpy.types.View3DOverlay.show_freestyle_face_marks"></a>

#### bpy.types.View3DOverlay.show_freestyle_face_marks

Display Freestyle face marks, used with the Freestyle renderer (default True)

**Type:**

bool

<a id="bpy.types.View3DOverlay.show_light_colors"></a>

#### bpy.types.View3DOverlay.show_light_colors

Show light colors (default False)

**Type:**

bool

<a id="bpy.types.View3DOverlay.show_look_dev"></a>

#### bpy.types.View3DOverlay.show_look_dev

Show reference spheres with neutral shading that react to lighting to assist in look development (default False)

**Type:**

bool

<a id="bpy.types.View3DOverlay.show_motion_paths"></a>

#### bpy.types.View3DOverlay.show_motion_paths

Show the Motion Paths Overlay (default True)

**Type:**

bool

<a id="bpy.types.View3DOverlay.show_object_origins"></a>

#### bpy.types.View3DOverlay.show_object_origins

Show object center dots (default True)

**Type:**

bool

<a id="bpy.types.View3DOverlay.show_object_origins_all"></a>

#### bpy.types.View3DOverlay.show_object_origins_all

Show the object origin center dot for all (selected and unselected) objects (default False)

**Type:**

bool

<a id="bpy.types.View3DOverlay.show_onion_skins"></a>

#### bpy.types.View3DOverlay.show_onion_skins

Show the Onion Skinning Overlay (default False)

**Type:**

bool

<a id="bpy.types.View3DOverlay.show_ortho_grid"></a>

#### bpy.types.View3DOverlay.show_ortho_grid

Show grid in orthographic side view (default True)

**Type:**

bool

<a id="bpy.types.View3DOverlay.show_outline_selected"></a>

#### bpy.types.View3DOverlay.show_outline_selected

Show an outline highlight around selected objects (default True)

**Type:**

bool

<a id="bpy.types.View3DOverlay.show_overlays"></a>

#### bpy.types.View3DOverlay.show_overlays

Display overlays like gizmos and outlines (default True)

**Type:**

bool

<a id="bpy.types.View3DOverlay.show_paint_wire"></a>

#### bpy.types.View3DOverlay.show_paint_wire

Use wireframe display in painting modes (default False)

**Type:**

bool

<a id="bpy.types.View3DOverlay.show_performance"></a>

#### bpy.types.View3DOverlay.show_performance

Display viewport performance timings:
:   - Evaluation: Time to evaluate the dependency graph.
    - Synchronization: Time to build the GPU buffers.

(default False)

**Type:**

bool

<a id="bpy.types.View3DOverlay.show_relationship_lines"></a>

#### bpy.types.View3DOverlay.show_relationship_lines

Show dashed lines indicating parent or constraint relationships (default True)

**Type:**

bool

<a id="bpy.types.View3DOverlay.show_retopology"></a>

#### bpy.types.View3DOverlay.show_retopology

Hide the solid mesh and offset the overlay towards the view. Selection is occluded by inactive geometry, unless X-Ray is enabled (default False)

**Type:**

bool

<a id="bpy.types.View3DOverlay.show_sculpt_curves_cage"></a>

#### bpy.types.View3DOverlay.show_sculpt_curves_cage

Show original curves that are currently being edited (default False)

**Type:**

bool

<a id="bpy.types.View3DOverlay.show_sculpt_face_sets"></a>

#### bpy.types.View3DOverlay.show_sculpt_face_sets

(default True)

**Type:**

bool

<a id="bpy.types.View3DOverlay.show_sculpt_mask"></a>

#### bpy.types.View3DOverlay.show_sculpt_mask

(default True)

**Type:**

bool

<a id="bpy.types.View3DOverlay.show_split_normals"></a>

#### bpy.types.View3DOverlay.show_split_normals

Display vertex-per-face normals as lines (default False)

**Type:**

bool

<a id="bpy.types.View3DOverlay.show_stats"></a>

#### bpy.types.View3DOverlay.show_stats

Display scene statistics overlay text (default False)

**Type:**

bool

<a id="bpy.types.View3DOverlay.show_statvis"></a>

#### bpy.types.View3DOverlay.show_statvis

Display statistical information about the mesh (default False)

**Type:**

bool

<a id="bpy.types.View3DOverlay.show_text"></a>

#### bpy.types.View3DOverlay.show_text

Display overlay text (default True)

**Type:**

bool

<a id="bpy.types.View3DOverlay.show_vertex_normals"></a>

#### bpy.types.View3DOverlay.show_vertex_normals

Display vertex normals as lines (default False)

**Type:**

bool

<a id="bpy.types.View3DOverlay.show_viewer_attribute"></a>

#### bpy.types.View3DOverlay.show_viewer_attribute

Show attribute overlay for active viewer node (default True)

**Type:**

bool

<a id="bpy.types.View3DOverlay.show_viewer_text"></a>

#### bpy.types.View3DOverlay.show_viewer_text

Show attribute values as text in viewport (default False)

**Type:**

bool

<a id="bpy.types.View3DOverlay.show_weight"></a>

#### bpy.types.View3DOverlay.show_weight

Display weights in editmode (default False)

**Type:**

bool

<a id="bpy.types.View3DOverlay.show_wireframes"></a>

#### bpy.types.View3DOverlay.show_wireframes

Show face edges wires (default False)

**Type:**

bool

<a id="bpy.types.View3DOverlay.show_wpaint_contours"></a>

#### bpy.types.View3DOverlay.show_wpaint_contours

Show contour lines formed by points with the same interpolated weight (default False)

**Type:**

bool

<a id="bpy.types.View3DOverlay.show_xray_bone"></a>

#### bpy.types.View3DOverlay.show_xray_bone

Show the bone selection overlay (default False)

**Type:**

bool

<a id="bpy.types.View3DOverlay.texture_paint_mode_opacity"></a>

#### bpy.types.View3DOverlay.texture_paint_mode_opacity

Opacity of the texture paint mode stencil mask overlay (in [0, 1], default 1.0)

**Type:**

float

<a id="bpy.types.View3DOverlay.use_debug_freeze_view_culling"></a>

#### bpy.types.View3DOverlay.use_debug_freeze_view_culling

Freeze view culling bounds (default False)

**Type:**

bool

<a id="bpy.types.View3DOverlay.use_gpencil_canvas_xray"></a>

#### bpy.types.View3DOverlay.use_gpencil_canvas_xray

Show Canvas grid in front (default False)

**Type:**

bool

<a id="bpy.types.View3DOverlay.use_gpencil_edit_lines"></a>

#### bpy.types.View3DOverlay.use_gpencil_edit_lines

Show Edit Lines when editing strokes (default True)

**Type:**

bool

<a id="bpy.types.View3DOverlay.use_gpencil_fade_gp_objects"></a>

#### bpy.types.View3DOverlay.use_gpencil_fade_gp_objects

Fade Grease Pencil Objects, except the active one (default False)

**Type:**

bool

<a id="bpy.types.View3DOverlay.use_gpencil_fade_layers"></a>

#### bpy.types.View3DOverlay.use_gpencil_fade_layers

Toggle fading of Grease Pencil layers except the active one (default False)

**Type:**

bool

<a id="bpy.types.View3DOverlay.use_gpencil_fade_objects"></a>

#### bpy.types.View3DOverlay.use_gpencil_fade_objects

Fade all viewport objects with a full color layer to improve visibility (default False)

**Type:**

bool

<a id="bpy.types.View3DOverlay.use_gpencil_grid"></a>

#### bpy.types.View3DOverlay.use_gpencil_grid

Display a grid over Grease Pencil paper (default False)

**Type:**

bool

<a id="bpy.types.View3DOverlay.use_gpencil_multiedit_line_only"></a>

#### bpy.types.View3DOverlay.use_gpencil_multiedit_line_only

Show Edit Lines only in multiframe (default False)

**Type:**

bool

<a id="bpy.types.View3DOverlay.use_gpencil_onion_skin"></a>

#### bpy.types.View3DOverlay.use_gpencil_onion_skin

Show ghosts of the keyframes before and after the current frame (default False)

**Type:**

bool

<a id="bpy.types.View3DOverlay.use_gpencil_onion_skin_active_object"></a>

#### bpy.types.View3DOverlay.use_gpencil_onion_skin_active_object

Show only the onion skins of the active object (default False)

**Type:**

bool

<a id="bpy.types.View3DOverlay.use_gpencil_show_directions"></a>

#### bpy.types.View3DOverlay.use_gpencil_show_directions

Show stroke drawing direction with a bigger green dot (start) and smaller red dot (end) points (default False)

**Type:**

bool

<a id="bpy.types.View3DOverlay.use_gpencil_show_material_name"></a>

#### bpy.types.View3DOverlay.use_gpencil_show_material_name

Show material name assigned to each stroke (default False)

**Type:**

bool

<a id="bpy.types.View3DOverlay.use_normals_constant_screen_size"></a>

#### bpy.types.View3DOverlay.use_normals_constant_screen_size

Keep size of normals constant in relation to 3D view (default False)

**Type:**

bool

<a id="bpy.types.View3DOverlay.vertex_opacity"></a>

#### bpy.types.View3DOverlay.vertex_opacity

Opacity for edit vertices (in [0, 1], default 1.0)

**Type:**

float

<a id="bpy.types.View3DOverlay.vertex_paint_mode_opacity"></a>

#### bpy.types.View3DOverlay.vertex_paint_mode_opacity

Opacity of the texture paint mode stencil mask overlay (in [0, 1], default 1.0)

**Type:**

float

<a id="bpy.types.View3DOverlay.viewer_attribute_opacity"></a>

#### bpy.types.View3DOverlay.viewer_attribute_opacity

Opacity of the attribute that is currently visualized (in [0, 1], default 1.0)

**Type:**

float

<a id="bpy.types.View3DOverlay.weight_paint_mode_opacity"></a>

#### bpy.types.View3DOverlay.weight_paint_mode_opacity

Opacity of the weight paint mode overlay (in [0, 1], default 1.0)

**Type:**

float

<a id="bpy.types.View3DOverlay.wireframe_opacity"></a>

#### bpy.types.View3DOverlay.wireframe_opacity

Opacity of the displayed edges (1.0 for opaque) (in [0, 1], default 1.0)

**Type:**

float

<a id="bpy.types.View3DOverlay.wireframe_threshold"></a>

#### bpy.types.View3DOverlay.wireframe_threshold

Adjust the angle threshold for displaying edges (1.0 for all) (in [0, 1], default 1.0)

**Type:**

float

<a id="bpy.types.View3DOverlay.xray_alpha_bone"></a>

#### bpy.types.View3DOverlay.xray_alpha_bone

Opacity to use for bone selection (in [0, 1], default 0.5)

**Type:**

float

<a id="bpy.types.View3DOverlay.bl_rna_get_subclass"></a>

#### classmethod bpy.types.View3DOverlay.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.View3DOverlay.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.View3DOverlay.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`SpaceView3D.overlay`](bpy.types.SpaceView3D.md#bpy.types.SpaceView3D.overlay "bpy.types.SpaceView3D.overlay") |  |
