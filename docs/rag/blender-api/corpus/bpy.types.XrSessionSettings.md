<!-- source: Blender Python API reference 5.2 / bpy.types.XrSessionSettings.html -->

<a id="xrsessionsettings-bpy-struct"></a>

# XrSessionSettings(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.XrSessionSettings"></a>

### class bpy.types.XrSessionSettings(bpy_struct)

<a id="bpy.types.XrSessionSettings.base_pose_angle"></a>

#### bpy.types.XrSessionSettings.base_pose_angle

Rotation angle around the Z-Axis to apply the rotation deltas from the VR headset to (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.XrSessionSettings.base_pose_location"></a>

#### bpy.types.XrSessionSettings.base_pose_location

Coordinates to apply translation deltas from the VR headset to (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.XrSessionSettings.base_pose_object"></a>

#### bpy.types.XrSessionSettings.base_pose_object

Object to take the location and rotation to which translation and rotation deltas from the VR headset will be applied to

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.XrSessionSettings.base_pose_type"></a>

#### bpy.types.XrSessionSettings.base_pose_type

Define where the location and rotation for the VR view come from, to which translation and rotation deltas from the VR headset will be applied to (default `'SCENE_CAMERA'`)

- `SCENE_CAMERA`
  Scene Camera – Follow the active scene camera to define the VR view’s base pose.
- `OBJECT`
  Object – Follow the transformation of an object to define the VR view’s base pose.
- `CUSTOM`
  Custom – Follow a custom transformation to define the VR view’s base pose.

**Type:**

Literal[‘SCENE_CAMERA’, ‘OBJECT’, ‘CUSTOM’]

<a id="bpy.types.XrSessionSettings.base_scale"></a>

#### bpy.types.XrSessionSettings.base_scale

Uniform base pose scale to apply to VR view (in [1e-06, inf], default 1.0)

**Type:**

float

<a id="bpy.types.XrSessionSettings.clip_end"></a>

#### bpy.types.XrSessionSettings.clip_end

VR viewport far clipping distance (in [1e-06, inf], default 0.0)

**Type:**

float

<a id="bpy.types.XrSessionSettings.clip_start"></a>

#### bpy.types.XrSessionSettings.clip_start

VR viewport near clipping distance (in [1e-06, inf], default 0.0)

**Type:**

float

<a id="bpy.types.XrSessionSettings.controller_draw_style"></a>

#### bpy.types.XrSessionSettings.controller_draw_style

Style to use when drawing VR controllers (default `'DARK'`)

- `DARK`
  Dark – Draw dark controller.
- `LIGHT`
  Light – Draw light controller.
- `DARK_RAY`
  Dark + Ray – Draw dark controller with aiming axis ray.
- `LIGHT_RAY`
  Light + Ray – Draw light controller with aiming axis ray.

**Type:**

Literal[‘DARK’, ‘LIGHT’, ‘DARK_RAY’, ‘LIGHT_RAY’]

<a id="bpy.types.XrSessionSettings.fly_speed"></a>

#### bpy.types.XrSessionSettings.fly_speed

Fly speed in meters per second (in [1e-06, inf], default 0.0)

**Type:**

float

<a id="bpy.types.XrSessionSettings.icon_from_show_object_viewport"></a>

#### bpy.types.XrSessionSettings.icon_from_show_object_viewport

(in [-inf, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.XrSessionSettings.shading"></a>

#### bpy.types.XrSessionSettings.shading

(readonly, never None)

**Type:**

[`View3DShading`](bpy.types.View3DShading.md#bpy.types.View3DShading "bpy.types.View3DShading")

<a id="bpy.types.XrSessionSettings.show_annotation"></a>

#### bpy.types.XrSessionSettings.show_annotation

Show annotations for this view (default False)

**Type:**

bool

<a id="bpy.types.XrSessionSettings.show_controllers"></a>

#### bpy.types.XrSessionSettings.show_controllers

Show VR controllers (requires VR actions for controller poses) (default False)

**Type:**

bool

<a id="bpy.types.XrSessionSettings.show_custom_overlays"></a>

#### bpy.types.XrSessionSettings.show_custom_overlays

Show custom VR overlays (default False)

**Type:**

bool

<a id="bpy.types.XrSessionSettings.show_floor"></a>

#### bpy.types.XrSessionSettings.show_floor

Show the ground plane grid (default False)

**Type:**

bool

<a id="bpy.types.XrSessionSettings.show_object_extras"></a>

#### bpy.types.XrSessionSettings.show_object_extras

Show object extras, including empties, lights, and cameras (default False)

**Type:**

bool

<a id="bpy.types.XrSessionSettings.show_object_select_armature"></a>

#### bpy.types.XrSessionSettings.show_object_select_armature

Allow selection of armatures (default True)

**Type:**

bool

<a id="bpy.types.XrSessionSettings.show_object_select_camera"></a>

#### bpy.types.XrSessionSettings.show_object_select_camera

Allow selection of cameras (default True)

**Type:**

bool

<a id="bpy.types.XrSessionSettings.show_object_select_curve"></a>

#### bpy.types.XrSessionSettings.show_object_select_curve

Allow selection of curves (default True)

**Type:**

bool

<a id="bpy.types.XrSessionSettings.show_object_select_curves"></a>

#### bpy.types.XrSessionSettings.show_object_select_curves

Allow selection of hair curves (default True)

**Type:**

bool

<a id="bpy.types.XrSessionSettings.show_object_select_empty"></a>

#### bpy.types.XrSessionSettings.show_object_select_empty

Allow selection of empties (default True)

**Type:**

bool

<a id="bpy.types.XrSessionSettings.show_object_select_font"></a>

#### bpy.types.XrSessionSettings.show_object_select_font

Allow selection of text objects (default True)

**Type:**

bool

<a id="bpy.types.XrSessionSettings.show_object_select_grease_pencil"></a>

#### bpy.types.XrSessionSettings.show_object_select_grease_pencil

Allow selection of Grease Pencil objects (default True)

**Type:**

bool

<a id="bpy.types.XrSessionSettings.show_object_select_lattice"></a>

#### bpy.types.XrSessionSettings.show_object_select_lattice

Allow selection of lattices (default True)

**Type:**

bool

<a id="bpy.types.XrSessionSettings.show_object_select_light"></a>

#### bpy.types.XrSessionSettings.show_object_select_light

Allow selection of lights (default True)

**Type:**

bool

<a id="bpy.types.XrSessionSettings.show_object_select_light_probe"></a>

#### bpy.types.XrSessionSettings.show_object_select_light_probe

Allow selection of light probes (default True)

**Type:**

bool

<a id="bpy.types.XrSessionSettings.show_object_select_mesh"></a>

#### bpy.types.XrSessionSettings.show_object_select_mesh

Allow selection of mesh objects (default True)

**Type:**

bool

<a id="bpy.types.XrSessionSettings.show_object_select_meta"></a>

#### bpy.types.XrSessionSettings.show_object_select_meta

Allow selection of metaballs (default True)

**Type:**

bool

<a id="bpy.types.XrSessionSettings.show_object_select_pointcloud"></a>

#### bpy.types.XrSessionSettings.show_object_select_pointcloud

Allow selection of point clouds (default True)

**Type:**

bool

<a id="bpy.types.XrSessionSettings.show_object_select_speaker"></a>

#### bpy.types.XrSessionSettings.show_object_select_speaker

Allow selection of speakers (default True)

**Type:**

bool

<a id="bpy.types.XrSessionSettings.show_object_select_surf"></a>

#### bpy.types.XrSessionSettings.show_object_select_surf

Allow selection of surfaces (default True)

**Type:**

bool

<a id="bpy.types.XrSessionSettings.show_object_select_volume"></a>

#### bpy.types.XrSessionSettings.show_object_select_volume

Allow selection of volumes (default True)

**Type:**

bool

<a id="bpy.types.XrSessionSettings.show_object_viewport_armature"></a>

#### bpy.types.XrSessionSettings.show_object_viewport_armature

Show armatures (default True)

**Type:**

bool

<a id="bpy.types.XrSessionSettings.show_object_viewport_camera"></a>

#### bpy.types.XrSessionSettings.show_object_viewport_camera

Show cameras (default True)

**Type:**

bool

<a id="bpy.types.XrSessionSettings.show_object_viewport_curve"></a>

#### bpy.types.XrSessionSettings.show_object_viewport_curve

Show curves (default True)

**Type:**

bool

<a id="bpy.types.XrSessionSettings.show_object_viewport_curves"></a>

#### bpy.types.XrSessionSettings.show_object_viewport_curves

Show hair curves (default True)

**Type:**

bool

<a id="bpy.types.XrSessionSettings.show_object_viewport_empty"></a>

#### bpy.types.XrSessionSettings.show_object_viewport_empty

Show empties (default True)

**Type:**

bool

<a id="bpy.types.XrSessionSettings.show_object_viewport_font"></a>

#### bpy.types.XrSessionSettings.show_object_viewport_font

Show text objects (default True)

**Type:**

bool

<a id="bpy.types.XrSessionSettings.show_object_viewport_grease_pencil"></a>

#### bpy.types.XrSessionSettings.show_object_viewport_grease_pencil

Show Grease Pencil objects (default True)

**Type:**

bool

<a id="bpy.types.XrSessionSettings.show_object_viewport_lattice"></a>

#### bpy.types.XrSessionSettings.show_object_viewport_lattice

Show lattices (default True)

**Type:**

bool

<a id="bpy.types.XrSessionSettings.show_object_viewport_light"></a>

#### bpy.types.XrSessionSettings.show_object_viewport_light

Show lights (default True)

**Type:**

bool

<a id="bpy.types.XrSessionSettings.show_object_viewport_light_probe"></a>

#### bpy.types.XrSessionSettings.show_object_viewport_light_probe

Show light probes (default True)

**Type:**

bool

<a id="bpy.types.XrSessionSettings.show_object_viewport_mesh"></a>

#### bpy.types.XrSessionSettings.show_object_viewport_mesh

Show mesh objects (default True)

**Type:**

bool

<a id="bpy.types.XrSessionSettings.show_object_viewport_meta"></a>

#### bpy.types.XrSessionSettings.show_object_viewport_meta

Show metaballs (default True)

**Type:**

bool

<a id="bpy.types.XrSessionSettings.show_object_viewport_pointcloud"></a>

#### bpy.types.XrSessionSettings.show_object_viewport_pointcloud

Show point clouds (default True)

**Type:**

bool

<a id="bpy.types.XrSessionSettings.show_object_viewport_speaker"></a>

#### bpy.types.XrSessionSettings.show_object_viewport_speaker

Show speakers (default True)

**Type:**

bool

<a id="bpy.types.XrSessionSettings.show_object_viewport_surf"></a>

#### bpy.types.XrSessionSettings.show_object_viewport_surf

Show surfaces (default True)

**Type:**

bool

<a id="bpy.types.XrSessionSettings.show_object_viewport_volume"></a>

#### bpy.types.XrSessionSettings.show_object_viewport_volume

Show volumes (default True)

**Type:**

bool

<a id="bpy.types.XrSessionSettings.show_passthrough"></a>

#### bpy.types.XrSessionSettings.show_passthrough

Show the passthrough view (default False)

**Type:**

bool

<a id="bpy.types.XrSessionSettings.show_selection"></a>

#### bpy.types.XrSessionSettings.show_selection

Show selection outlines (default False)

**Type:**

bool

<a id="bpy.types.XrSessionSettings.use_absolute_tracking"></a>

#### bpy.types.XrSessionSettings.use_absolute_tracking

Allow the VR tracking origin to be defined independently of the headset location (default False)

**Type:**

bool

<a id="bpy.types.XrSessionSettings.use_positional_tracking"></a>

#### bpy.types.XrSessionSettings.use_positional_tracking

Allow VR headsets to affect the location in virtual space, in addition to the rotation (default False)

**Type:**

bool

<a id="bpy.types.XrSessionSettings.view_scale"></a>

#### bpy.types.XrSessionSettings.view_scale

Scaling factor applied to the VR view for fine adjustements. Modifying this value will keep the viewer at the same world relative position (in [1e-06, inf], default 1.0)

**Type:**

float

<a id="bpy.types.XrSessionSettings.viewfinder_crosshair_enabled"></a>

#### bpy.types.XrSessionSettings.viewfinder_crosshair_enabled

Enable the Viewfinder Crosshair (default True)

**Type:**

bool

<a id="bpy.types.XrSessionSettings.viewfinder_enabled"></a>

#### bpy.types.XrSessionSettings.viewfinder_enabled

Enable the Location Scouting Viewfinder (default True)

**Type:**

bool

<a id="bpy.types.XrSessionSettings.viewfinder_hand"></a>

#### bpy.types.XrSessionSettings.viewfinder_hand

Hand on which to place the Location Scouting Viewfinder (default `'LEFT'`)

- `LEFT`
  Left – Place the viewfinder on the left hand controller.
- `RIGHT`
  Right – Place the viewfinder on the right hand controller.

**Type:**

Literal[‘LEFT’, ‘RIGHT’]

<a id="bpy.types.XrSessionSettings.viewfinder_passepartout_opacity"></a>

#### bpy.types.XrSessionSettings.viewfinder_passepartout_opacity

Opacity of the darkened Viewfinder Passepartout overlay (in [0, 1], default 0.5)

**Type:**

float

<a id="bpy.types.XrSessionSettings.viewfinder_passepartout_overscan"></a>

#### bpy.types.XrSessionSettings.viewfinder_passepartout_overscan

Border size of the Viewfinder Passepartout overlay (in [0, 1], default 0.5)

**Type:**

float

<a id="bpy.types.XrSessionSettings.viewfinder_scale"></a>

#### bpy.types.XrSessionSettings.viewfinder_scale

Location Scouting Viewfinder size scale (in [-3, inf], default 1.0)

**Type:**

float

<a id="bpy.types.XrSessionSettings.bl_rna_get_subclass"></a>

#### classmethod bpy.types.XrSessionSettings.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.XrSessionSettings.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.XrSessionSettings.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`WindowManager.xr_session_settings`](bpy.types.WindowManager.md#bpy.types.WindowManager.xr_session_settings "bpy.types.WindowManager.xr_session_settings") |  |
