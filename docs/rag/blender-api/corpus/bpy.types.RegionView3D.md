<!-- source: Blender Python API reference 5.2 / bpy.types.RegionView3D.html -->

<a id="regionview3d-bpy-struct"></a>

# RegionView3D(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.RegionView3D"></a>

### class bpy.types.RegionView3D(bpy_struct)

3D View region data

<a id="bpy.types.RegionView3D.clip_planes"></a>

#### bpy.types.RegionView3D.clip_planes

(multi-dimensional array of 6 * 4 items, in [-inf, inf], default ((0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0)))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]]

<a id="bpy.types.RegionView3D.is_orthographic_side_view"></a>

#### bpy.types.RegionView3D.is_orthographic_side_view

Whether the current view is aligned to an axis (does not check whether the view is orthographic, use “is_perspective” for that). Setting this will rotate the view to the closest axis (default False)

**Type:**

bool

<a id="bpy.types.RegionView3D.is_perspective"></a>

#### bpy.types.RegionView3D.is_perspective

(default False)

**Type:**

bool

<a id="bpy.types.RegionView3D.lock_rotation"></a>

#### bpy.types.RegionView3D.lock_rotation

Lock view rotation of side views to Top/Front/Right (default False)

**Type:**

bool

<a id="bpy.types.RegionView3D.perspective_matrix"></a>

#### bpy.types.RegionView3D.perspective_matrix

Current perspective matrix (`window_matrix * view_matrix`) (multi-dimensional array of 4 * 4 items, in [-inf, inf], default ((0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0)), readonly)

**Type:**

[`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")

<a id="bpy.types.RegionView3D.show_sync_view"></a>

#### bpy.types.RegionView3D.show_sync_view

Sync view position between side views (default False)

**Type:**

bool

<a id="bpy.types.RegionView3D.use_box_clip"></a>

#### bpy.types.RegionView3D.use_box_clip

Clip view contents based on what is visible in other side views (default False)

**Type:**

bool

<a id="bpy.types.RegionView3D.use_clip_planes"></a>

#### bpy.types.RegionView3D.use_clip_planes

(default False)

**Type:**

bool

<a id="bpy.types.RegionView3D.view_camera_offset"></a>

#### bpy.types.RegionView3D.view_camera_offset

View shift in camera view (array of 2 items, in [-inf, inf], default (0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.RegionView3D.view_camera_zoom"></a>

#### bpy.types.RegionView3D.view_camera_zoom

Zoom factor in camera view (in [-30, 600], default 0.0)

**Type:**

float

<a id="bpy.types.RegionView3D.view_distance"></a>

#### bpy.types.RegionView3D.view_distance

Distance to the view location (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.RegionView3D.view_location"></a>

#### bpy.types.RegionView3D.view_location

View pivot location (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.RegionView3D.view_matrix"></a>

#### bpy.types.RegionView3D.view_matrix

Current view matrix (multi-dimensional array of 4 * 4 items, in [-inf, inf], default ((0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0)))

**Type:**

[`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")

<a id="bpy.types.RegionView3D.view_perspective"></a>

#### bpy.types.RegionView3D.view_perspective

View Perspective (default `'ORTHO'`)

**Type:**

Literal[‘PERSP’, ‘ORTHO’, ‘CAMERA’]

<a id="bpy.types.RegionView3D.view_rotation"></a>

#### bpy.types.RegionView3D.view_rotation

Rotation in quaternions (keep normalized) (array of 4 items, in [-inf, inf], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`mathutils.Quaternion`](mathutils.md#mathutils.Quaternion "mathutils.Quaternion")

<a id="bpy.types.RegionView3D.window_matrix"></a>

#### bpy.types.RegionView3D.window_matrix

Current window matrix (multi-dimensional array of 4 * 4 items, in [-inf, inf], default ((0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0)), readonly)

**Type:**

[`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")

<a id="bpy.types.RegionView3D.update"></a>

#### bpy.types.RegionView3D.update()

Recalculate the view matrices

<a id="bpy.types.RegionView3D.bl_rna_get_subclass"></a>

#### classmethod bpy.types.RegionView3D.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.RegionView3D.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.RegionView3D.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Context.region_data`](bpy.types.Context.md#bpy.types.Context.region_data "bpy.types.Context.region_data") - [`SpaceView3D.region_3d`](bpy.types.SpaceView3D.md#bpy.types.SpaceView3D.region_3d "bpy.types.SpaceView3D.region_3d") | - [`SpaceView3D.region_quadviews`](bpy.types.SpaceView3D.md#bpy.types.SpaceView3D.region_quadviews "bpy.types.SpaceView3D.region_quadviews") |
