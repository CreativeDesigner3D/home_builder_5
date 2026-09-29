<!-- source: Blender Python API reference 5.2 / bpy.types.SpaceView3D.html -->

<a id="spaceview3d-space"></a>

# SpaceView3D(Space)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Space`](bpy.types.Space.md#bpy.types.Space "bpy.types.Space")

<a id="bpy.types.SpaceView3D"></a>

### class bpy.types.SpaceView3D(Space)

3D View space data

<a id="bpy.types.SpaceView3D.camera"></a>

#### bpy.types.SpaceView3D.camera

Active camera used in this view (when unlocked from the scene’s active camera)

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.SpaceView3D.clip_end"></a>

#### bpy.types.SpaceView3D.clip_end

3D View far clipping distance (in [1e-06, inf], default 1000.0)

**Type:**

float

<a id="bpy.types.SpaceView3D.clip_start"></a>

#### bpy.types.SpaceView3D.clip_start

3D View near clipping distance (perspective view only) (in [1e-06, inf], default 0.01)

**Type:**

float

<a id="bpy.types.SpaceView3D.icon_from_show_object_viewport"></a>

#### bpy.types.SpaceView3D.icon_from_show_object_viewport

(in [-inf, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.SpaceView3D.lens"></a>

#### bpy.types.SpaceView3D.lens

Viewport lens angle (in [1, 250], default 50.0)

**Type:**

float

<a id="bpy.types.SpaceView3D.local_view"></a>

#### bpy.types.SpaceView3D.local_view

Display an isolated subset of objects, apart from the scene visibility (readonly)

**Type:**

[`SpaceView3D`](#bpy.types.SpaceView3D "bpy.types.SpaceView3D") | None

<a id="bpy.types.SpaceView3D.lock_bone"></a>

#### bpy.types.SpaceView3D.lock_bone

3D View center is locked to this bone’s position (default “”, never None)

**Type:**

str

<a id="bpy.types.SpaceView3D.lock_camera"></a>

#### bpy.types.SpaceView3D.lock_camera

Enable view navigation within the camera view (default False)

**Type:**

bool

<a id="bpy.types.SpaceView3D.lock_cursor"></a>

#### bpy.types.SpaceView3D.lock_cursor

3D View center is locked to the cursor’s position (default False)

**Type:**

bool

<a id="bpy.types.SpaceView3D.lock_object"></a>

#### bpy.types.SpaceView3D.lock_object

3D View center is locked to this object’s position

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.SpaceView3D.mirror_xr_session"></a>

#### bpy.types.SpaceView3D.mirror_xr_session

Synchronize the viewer perspective of virtual reality sessions with this 3D viewport (default False)

**Type:**

bool

<a id="bpy.types.SpaceView3D.overlay"></a>

#### bpy.types.SpaceView3D.overlay

Settings for display of overlays in the 3D viewport (readonly, never None)

**Type:**

[`View3DOverlay`](bpy.types.View3DOverlay.md#bpy.types.View3DOverlay "bpy.types.View3DOverlay")

<a id="bpy.types.SpaceView3D.region_3d"></a>

#### bpy.types.SpaceView3D.region_3d

3D region for this space. When the space is in quad view, the camera region (readonly)

**Type:**

[`RegionView3D`](bpy.types.RegionView3D.md#bpy.types.RegionView3D "bpy.types.RegionView3D") | None

<a id="bpy.types.SpaceView3D.region_quadviews"></a>

#### bpy.types.SpaceView3D.region_quadviews

3D regions (the third one defines quad view settings, the fourth one is same as ‘region_3d’) (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`RegionView3D`](bpy.types.RegionView3D.md#bpy.types.RegionView3D "bpy.types.RegionView3D")]

<a id="bpy.types.SpaceView3D.render_border_max_x"></a>

#### bpy.types.SpaceView3D.render_border_max_x

Maximum X value for the render region (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.SpaceView3D.render_border_max_y"></a>

#### bpy.types.SpaceView3D.render_border_max_y

Maximum Y value for the render region (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.SpaceView3D.render_border_min_x"></a>

#### bpy.types.SpaceView3D.render_border_min_x

Minimum X value for the render region (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.SpaceView3D.render_border_min_y"></a>

#### bpy.types.SpaceView3D.render_border_min_y

Minimum Y value for the render region (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.SpaceView3D.shading"></a>

#### bpy.types.SpaceView3D.shading

Settings for shading in the 3D viewport (readonly, never None)

**Type:**

[`View3DShading`](bpy.types.View3DShading.md#bpy.types.View3DShading "bpy.types.View3DShading")

<a id="bpy.types.SpaceView3D.show_bundle_names"></a>

#### bpy.types.SpaceView3D.show_bundle_names

Show names for reconstructed tracks objects (default False)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_camera_path"></a>

#### bpy.types.SpaceView3D.show_camera_path

Show reconstructed camera path (default False)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_gizmo"></a>

#### bpy.types.SpaceView3D.show_gizmo

Show gizmos of all types (default True)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_gizmo_camera_dof_distance"></a>

#### bpy.types.SpaceView3D.show_gizmo_camera_dof_distance

Gizmo to adjust camera focus distance (depends on limits display) (default False)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_gizmo_camera_lens"></a>

#### bpy.types.SpaceView3D.show_gizmo_camera_lens

Gizmo to adjust camera focal length or orthographic scale (default False)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_gizmo_context"></a>

#### bpy.types.SpaceView3D.show_gizmo_context

Context sensitive gizmos for the active item (default True)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_gizmo_empty_force_field"></a>

#### bpy.types.SpaceView3D.show_gizmo_empty_force_field

Gizmo to adjust the force field (default False)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_gizmo_empty_image"></a>

#### bpy.types.SpaceView3D.show_gizmo_empty_image

Gizmo to adjust image size and position (default False)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_gizmo_light_look_at"></a>

#### bpy.types.SpaceView3D.show_gizmo_light_look_at

Gizmo to adjust the direction of the light (default False)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_gizmo_light_size"></a>

#### bpy.types.SpaceView3D.show_gizmo_light_size

Gizmo to adjust spot and area size (default False)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_gizmo_modifier"></a>

#### bpy.types.SpaceView3D.show_gizmo_modifier

Gizmos for the active modifier (default True)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_gizmo_navigate"></a>

#### bpy.types.SpaceView3D.show_gizmo_navigate

Viewport navigation gizmo (default True)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_gizmo_object_rotate"></a>

#### bpy.types.SpaceView3D.show_gizmo_object_rotate

Gizmo to adjust rotation (default False)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_gizmo_object_scale"></a>

#### bpy.types.SpaceView3D.show_gizmo_object_scale

Gizmo to adjust scale (default False)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_gizmo_object_translate"></a>

#### bpy.types.SpaceView3D.show_gizmo_object_translate

Gizmo to adjust location (default False)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_gizmo_tool"></a>

#### bpy.types.SpaceView3D.show_gizmo_tool

Active tool gizmo (default True)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_object_select_armature"></a>

#### bpy.types.SpaceView3D.show_object_select_armature

Allow selection of armatures (default True)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_object_select_camera"></a>

#### bpy.types.SpaceView3D.show_object_select_camera

Allow selection of cameras (default True)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_object_select_curve"></a>

#### bpy.types.SpaceView3D.show_object_select_curve

Allow selection of curves (default True)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_object_select_curves"></a>

#### bpy.types.SpaceView3D.show_object_select_curves

Allow selection of hair curves (default True)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_object_select_empty"></a>

#### bpy.types.SpaceView3D.show_object_select_empty

Allow selection of empties (default True)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_object_select_font"></a>

#### bpy.types.SpaceView3D.show_object_select_font

Allow selection of text objects (default True)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_object_select_grease_pencil"></a>

#### bpy.types.SpaceView3D.show_object_select_grease_pencil

Allow selection of Grease Pencil objects (default True)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_object_select_lattice"></a>

#### bpy.types.SpaceView3D.show_object_select_lattice

Allow selection of lattices (default True)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_object_select_light"></a>

#### bpy.types.SpaceView3D.show_object_select_light

Allow selection of lights (default True)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_object_select_light_probe"></a>

#### bpy.types.SpaceView3D.show_object_select_light_probe

Allow selection of light probes (default True)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_object_select_mesh"></a>

#### bpy.types.SpaceView3D.show_object_select_mesh

Allow selection of mesh objects (default True)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_object_select_meta"></a>

#### bpy.types.SpaceView3D.show_object_select_meta

Allow selection of metaballs (default True)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_object_select_pointcloud"></a>

#### bpy.types.SpaceView3D.show_object_select_pointcloud

Allow selection of point clouds (default True)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_object_select_speaker"></a>

#### bpy.types.SpaceView3D.show_object_select_speaker

Allow selection of speakers (default True)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_object_select_surf"></a>

#### bpy.types.SpaceView3D.show_object_select_surf

Allow selection of surfaces (default True)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_object_select_volume"></a>

#### bpy.types.SpaceView3D.show_object_select_volume

Allow selection of volumes (default True)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_object_viewport_armature"></a>

#### bpy.types.SpaceView3D.show_object_viewport_armature

Show armatures (default True)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_object_viewport_camera"></a>

#### bpy.types.SpaceView3D.show_object_viewport_camera

Show cameras (default True)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_object_viewport_curve"></a>

#### bpy.types.SpaceView3D.show_object_viewport_curve

Show curves (default True)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_object_viewport_curves"></a>

#### bpy.types.SpaceView3D.show_object_viewport_curves

Show hair curves (default True)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_object_viewport_empty"></a>

#### bpy.types.SpaceView3D.show_object_viewport_empty

Show empties (default True)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_object_viewport_font"></a>

#### bpy.types.SpaceView3D.show_object_viewport_font

Show text objects (default True)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_object_viewport_grease_pencil"></a>

#### bpy.types.SpaceView3D.show_object_viewport_grease_pencil

Show Grease Pencil objects (default True)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_object_viewport_lattice"></a>

#### bpy.types.SpaceView3D.show_object_viewport_lattice

Show lattices (default True)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_object_viewport_light"></a>

#### bpy.types.SpaceView3D.show_object_viewport_light

Show lights (default True)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_object_viewport_light_probe"></a>

#### bpy.types.SpaceView3D.show_object_viewport_light_probe

Show light probes (default True)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_object_viewport_mesh"></a>

#### bpy.types.SpaceView3D.show_object_viewport_mesh

Show mesh objects (default True)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_object_viewport_meta"></a>

#### bpy.types.SpaceView3D.show_object_viewport_meta

Show metaballs (default True)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_object_viewport_pointcloud"></a>

#### bpy.types.SpaceView3D.show_object_viewport_pointcloud

Show point clouds (default True)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_object_viewport_speaker"></a>

#### bpy.types.SpaceView3D.show_object_viewport_speaker

Show speakers (default True)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_object_viewport_surf"></a>

#### bpy.types.SpaceView3D.show_object_viewport_surf

Show surfaces (default True)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_object_viewport_volume"></a>

#### bpy.types.SpaceView3D.show_object_viewport_volume

Show volumes (default True)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_reconstruction"></a>

#### bpy.types.SpaceView3D.show_reconstruction

Display reconstruction data from active movie clip (default True)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_region_asset_shelf"></a>

#### bpy.types.SpaceView3D.show_region_asset_shelf

Display a region with assets that may currently be relevant (such as brushes in paint modes, or poses in Pose Mode) (default False)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_region_hud"></a>

#### bpy.types.SpaceView3D.show_region_hud

(default False)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_region_tool_header"></a>

#### bpy.types.SpaceView3D.show_region_tool_header

(default False)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_region_toolbar"></a>

#### bpy.types.SpaceView3D.show_region_toolbar

(default False)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_region_ui"></a>

#### bpy.types.SpaceView3D.show_region_ui

(default False)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_stereo_3d_cameras"></a>

#### bpy.types.SpaceView3D.show_stereo_3d_cameras

Show the left and right cameras (default False)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_stereo_3d_convergence_plane"></a>

#### bpy.types.SpaceView3D.show_stereo_3d_convergence_plane

Show the stereo 3D convergence plane (default True)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_stereo_3d_volume"></a>

#### bpy.types.SpaceView3D.show_stereo_3d_volume

Show the stereo 3D frustum volume (default False)

**Type:**

bool

<a id="bpy.types.SpaceView3D.show_viewer"></a>

#### bpy.types.SpaceView3D.show_viewer

Display non-final geometry from viewer nodes (default True)

**Type:**

bool

<a id="bpy.types.SpaceView3D.stereo_3d_camera"></a>

#### bpy.types.SpaceView3D.stereo_3d_camera

(default `'S3D'`)

**Type:**

Literal[‘LEFT’, ‘RIGHT’, ‘S3D’]

<a id="bpy.types.SpaceView3D.stereo_3d_convergence_plane_alpha"></a>

#### bpy.types.SpaceView3D.stereo_3d_convergence_plane_alpha

Opacity (alpha) of the convergence plane (in [0, 1], default 0.15)

**Type:**

float

<a id="bpy.types.SpaceView3D.stereo_3d_eye"></a>

#### bpy.types.SpaceView3D.stereo_3d_eye

Current stereo eye being displayed (default `'LEFT_EYE'`, readonly)

**Type:**

Literal[‘LEFT_EYE’, ‘RIGHT_EYE’]

<a id="bpy.types.SpaceView3D.stereo_3d_volume_alpha"></a>

#### bpy.types.SpaceView3D.stereo_3d_volume_alpha

Opacity (alpha) of the cameras’ frustum volume (in [0, 1], default 0.05)

**Type:**

float

<a id="bpy.types.SpaceView3D.tracks_display_size"></a>

#### bpy.types.SpaceView3D.tracks_display_size

Display size of tracks from reconstructed data (in [0, inf], default 0.2)

**Type:**

float

<a id="bpy.types.SpaceView3D.tracks_display_type"></a>

#### bpy.types.SpaceView3D.tracks_display_type

Viewport display style for tracks (default `'PLAIN_AXES'`)

**Type:**

Literal[‘PLAIN_AXES’, ‘ARROWS’, ‘SINGLE_ARROW’, ‘CIRCLE’, ‘CUBE’, ‘SPHERE’, ‘CONE’]

<a id="bpy.types.SpaceView3D.use_local_camera"></a>

#### bpy.types.SpaceView3D.use_local_camera

Use a local camera in this view, rather than scene’s active camera (default False)

**Type:**

bool

<a id="bpy.types.SpaceView3D.use_local_collections"></a>

#### bpy.types.SpaceView3D.use_local_collections

Display a different set of collections in this viewport (default False)

**Type:**

bool

<a id="bpy.types.SpaceView3D.use_render_border"></a>

#### bpy.types.SpaceView3D.use_render_border

Use a region within the frame size for rendered viewport (when not viewing through the camera) (default False)

**Type:**

bool

<a id="bpy.types.SpaceView3D.bl_rna_get_subclass"></a>

#### classmethod bpy.types.SpaceView3D.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.SpaceView3D.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.SpaceView3D.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="bpy.types.SpaceView3D.draw_handler_add"></a>

#### classmethod bpy.types.SpaceView3D.draw_handler_add(callback, args, region_type, draw_type)

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

<a id="bpy.types.SpaceView3D.draw_handler_remove"></a>

#### classmethod bpy.types.SpaceView3D.draw_handler_remove(handler, region_type)

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

<a id="references"></a>

## References

|  |  |
| --- | --- |
| - [`Object.local_view_get`](bpy.types.Object.md#bpy.types.Object.local_view_get "bpy.types.Object.local_view_get") - [`Object.local_view_set`](bpy.types.Object.md#bpy.types.Object.local_view_set "bpy.types.Object.local_view_set") - [`Object.visible_get`](bpy.types.Object.md#bpy.types.Object.visible_get "bpy.types.Object.visible_get") | - [`Object.visible_in_viewport_get`](bpy.types.Object.md#bpy.types.Object.visible_in_viewport_get "bpy.types.Object.visible_in_viewport_get") - [`SpaceView3D.local_view`](#bpy.types.SpaceView3D.local_view "bpy.types.SpaceView3D.local_view") |
