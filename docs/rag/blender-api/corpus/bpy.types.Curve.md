<!-- source: Blender Python API reference 5.2 / bpy.types.Curve.html -->

<a id="curve-id"></a>

# Curve(ID)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")

Subclasses

- [SurfaceCurve(Curve)](bpy.types.SurfaceCurve.md)
- [TextCurve(Curve)](bpy.types.TextCurve.md)

<a id="bpy.types.Curve"></a>

### class bpy.types.Curve(ID)

Curve data-block storing curves, splines and NURBS

<a id="bpy.types.Curve.animation_data"></a>

#### bpy.types.Curve.animation_data

Animation data for this data-block (readonly)

**Type:**

[`AnimData`](bpy.types.AnimData.md#bpy.types.AnimData "bpy.types.AnimData") | None

<a id="bpy.types.Curve.bevel_depth"></a>

#### bpy.types.Curve.bevel_depth

Radius of the bevel geometry, not including extrusion (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.Curve.bevel_factor_end"></a>

#### bpy.types.Curve.bevel_factor_end

Define where along the spline the curve geometry ends (0 for the beginning, 1 for the end) (in [0, 1], default 1.0)

**Type:**

float

<a id="bpy.types.Curve.bevel_factor_mapping_end"></a>

#### bpy.types.Curve.bevel_factor_mapping_end

Determine how the geometry end factor is mapped to a spline (default `'RESOLUTION'`)

- `RESOLUTION`
  Resolution – Map the geometry factor to the number of subdivisions of a spline (U resolution).
- `SEGMENTS`
  Segments – Map the geometry factor to the length of a segment and to the number of subdivisions of a segment.
- `SPLINE`
  Spline – Map the geometry factor to the length of a spline.

**Type:**

Literal[‘RESOLUTION’, ‘SEGMENTS’, ‘SPLINE’]

<a id="bpy.types.Curve.bevel_factor_mapping_start"></a>

#### bpy.types.Curve.bevel_factor_mapping_start

Determine how the geometry start factor is mapped to a spline (default `'RESOLUTION'`)

- `RESOLUTION`
  Resolution – Map the geometry factor to the number of subdivisions of a spline (U resolution).
- `SEGMENTS`
  Segments – Map the geometry factor to the length of a segment and to the number of subdivisions of a segment.
- `SPLINE`
  Spline – Map the geometry factor to the length of a spline.

**Type:**

Literal[‘RESOLUTION’, ‘SEGMENTS’, ‘SPLINE’]

<a id="bpy.types.Curve.bevel_factor_start"></a>

#### bpy.types.Curve.bevel_factor_start

Define where along the spline the curve geometry starts (0 for the beginning, 1 for the end) (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.Curve.bevel_mode"></a>

#### bpy.types.Curve.bevel_mode

Determine how to build the curve’s bevel geometry (default `'ROUND'`)

- `ROUND`
  Round – Use circle for the section of the curve’s bevel geometry.
- `OBJECT`
  Object – Use an object for the section of the curve’s bevel geometry segment.
- `PROFILE`
  Profile – Use a custom profile for each quarter of curve’s bevel geometry.

**Type:**

Literal[‘ROUND’, ‘OBJECT’, ‘PROFILE’]

<a id="bpy.types.Curve.bevel_object"></a>

#### bpy.types.Curve.bevel_object

The name of the Curve object that defines the bevel shape

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.Curve.bevel_profile"></a>

#### bpy.types.Curve.bevel_profile

The path for the curve’s custom profile (readonly)

**Type:**

[`CurveProfile`](bpy.types.CurveProfile.md#bpy.types.CurveProfile "bpy.types.CurveProfile") | None

<a id="bpy.types.Curve.bevel_resolution"></a>

#### bpy.types.Curve.bevel_resolution

The number of segments in each quarter-circle of the bevel (in [0, 32], default 4)

**Type:**

int

<a id="bpy.types.Curve.cycles"></a>

#### bpy.types.Curve.cycles

Cycles mesh settings (readonly)

**Type:**

`CyclesMeshSettings` | None

<a id="bpy.types.Curve.dimensions"></a>

#### bpy.types.Curve.dimensions

Select 2D or 3D curve type (default `'2D'`)

- `2D`
  2D – Clamp the Z axis of the curve.
- `3D`
  3D – Allow editing on the Z axis of this curve, also allows tilt and curve radius to be used.

**Type:**

Literal[‘2D’, ‘3D’]

<a id="bpy.types.Curve.eval_time"></a>

#### bpy.types.Curve.eval_time

Parametric position along the length of the curve that Objects ‘following’ it should be at (position is evaluated by dividing by the ‘Path Length’ value) (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.Curve.extrude"></a>

#### bpy.types.Curve.extrude

Length of the depth added in the local Z direction along the curve, perpendicular to its normals (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.Curve.fill_mode"></a>

#### bpy.types.Curve.fill_mode

Mode of filling curve (default `'FULL'`)

**Type:**

Literal[‘FULL’, ‘BACK’, ‘FRONT’, ‘HALF’]

<a id="bpy.types.Curve.fill_rule"></a>

#### bpy.types.Curve.fill_rule

Fill rule for Delaunay fill solver (default `'EVEN_ODD'`)

- `EVEN_ODD`
  Even-Odd – Alternate inside/outside based on crossing count.
- `NONZERO`
  Non-Zero – Overlapping curves with the same winding direction are filled as a union.

**Type:**

Literal[‘EVEN_ODD’, ‘NONZERO’]

<a id="bpy.types.Curve.fill_solver"></a>

#### bpy.types.Curve.fill_solver

Triangulation solver for filling 2D curves (default `'SWEEP_LINE'`)

- `SWEEP_LINE`
  Sweep Line – Fast without support for self-intersection.
- `CDT`
  Delaunay – Constrained Delaunay Triangulation (CDT), robust with support for self-intersections.

**Type:**

Literal[‘SWEEP_LINE’, ‘CDT’]

<a id="bpy.types.Curve.is_editmode"></a>

#### bpy.types.Curve.is_editmode

True when used in editmode (default False, readonly)

**Type:**

bool

<a id="bpy.types.Curve.materials"></a>

#### bpy.types.Curve.materials

(default None, readonly)

**Type:**

[`IDMaterials`](bpy.types.IDMaterials.md#bpy.types.IDMaterials "bpy.types.IDMaterials")[[`Material`](bpy.types.Material.md#bpy.types.Material "bpy.types.Material")]

<a id="bpy.types.Curve.offset"></a>

#### bpy.types.Curve.offset

Distance to move the curve parallel to its normals (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.Curve.path_duration"></a>

#### bpy.types.Curve.path_duration

The number of frames that are needed to traverse the path, defining the maximum value for the ‘Evaluation Time’ setting (in [1, 1048574], default 100)

**Type:**

int

<a id="bpy.types.Curve.render_resolution_u"></a>

#### bpy.types.Curve.render_resolution_u

Surface resolution in U direction used while rendering (zero uses preview resolution) (in [0, 1024], default 0)

**Type:**

int

<a id="bpy.types.Curve.render_resolution_v"></a>

#### bpy.types.Curve.render_resolution_v

Surface resolution in V direction used while rendering (zero uses preview resolution) (in [0, 1024], default 0)

**Type:**

int

<a id="bpy.types.Curve.resolution_u"></a>

#### bpy.types.Curve.resolution_u

Number of computed points in the U direction between every pair of control points (in [1, 1024], default 12)

**Type:**

int

<a id="bpy.types.Curve.resolution_v"></a>

#### bpy.types.Curve.resolution_v

The number of computed points in the V direction between every pair of control points (in [1, 1024], default 12)

**Type:**

int

<a id="bpy.types.Curve.shape_keys"></a>

#### bpy.types.Curve.shape_keys

(readonly)

**Type:**

[`Key`](bpy.types.Key.md#bpy.types.Key "bpy.types.Key") | None

<a id="bpy.types.Curve.splines"></a>

#### bpy.types.Curve.splines

Collection of splines in this curve data object (default None, readonly)

**Type:**

[`CurveSplines`](bpy.types.CurveSplines.md#bpy.types.CurveSplines "bpy.types.CurveSplines")[[`Spline`](bpy.types.Spline.md#bpy.types.Spline "bpy.types.Spline")]

<a id="bpy.types.Curve.taper_object"></a>

#### bpy.types.Curve.taper_object

Curve object name that defines the taper (width)

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.Curve.taper_radius_mode"></a>

#### bpy.types.Curve.taper_radius_mode

Determine how the effective radius of the spline point is computed when a taper object is specified (default `'OVERRIDE'`)

- `OVERRIDE`
  Override – Override the radius of the spline point with the taper radius.
- `MULTIPLY`
  Multiply – Multiply the radius of the spline point by the taper radius.
- `ADD`
  Add – Add the radius of the bevel point to the taper radius.

**Type:**

Literal[‘OVERRIDE’, ‘MULTIPLY’, ‘ADD’]

<a id="bpy.types.Curve.texspace_location"></a>

#### bpy.types.Curve.texspace_location

(array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.Curve.texspace_size"></a>

#### bpy.types.Curve.texspace_size

(array of 3 items, in [-inf, inf], default (1.0, 1.0, 1.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.Curve.twist_mode"></a>

#### bpy.types.Curve.twist_mode

The type of tilt calculation for 3D Curves (default `'MINIMUM'`)

- `Z_UP`
  Z-Up – Use Z-Up axis to calculate the curve twist at each point.
- `MINIMUM`
  Minimum – Use the least twist over the entire curve.
- `TANGENT`
  Tangent – Use the tangent to calculate twist.

**Type:**

Literal[‘Z_UP’, ‘MINIMUM’, ‘TANGENT’]

<a id="bpy.types.Curve.twist_smooth"></a>

#### bpy.types.Curve.twist_smooth

Smoothing iteration for tangents (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.Curve.use_auto_texspace"></a>

#### bpy.types.Curve.use_auto_texspace

Adjust active object’s texture space automatically when transforming object (default True)

**Type:**

bool

<a id="bpy.types.Curve.use_deform_bounds"></a>

#### bpy.types.Curve.use_deform_bounds

Option for curve-deform: Use the mesh bounds to clamp the deformation (default False)

**Type:**

bool

<a id="bpy.types.Curve.use_fill_caps"></a>

#### bpy.types.Curve.use_fill_caps

Fill caps for beveled curves (default False)

**Type:**

bool

<a id="bpy.types.Curve.use_map_taper"></a>

#### bpy.types.Curve.use_map_taper

Map effect of the taper object to the beveled part of the curve (default False)

**Type:**

bool

<a id="bpy.types.Curve.use_path"></a>

#### bpy.types.Curve.use_path

Enable the curve to become a translation path (default False)

**Type:**

bool

<a id="bpy.types.Curve.use_path_clamp"></a>

#### bpy.types.Curve.use_path_clamp

Clamp the curve path children so they cannot travel past the start/end point of the curve (default False)

**Type:**

bool

<a id="bpy.types.Curve.use_path_follow"></a>

#### bpy.types.Curve.use_path_follow

Make curve path children rotate along the path (default False)

**Type:**

bool

<a id="bpy.types.Curve.use_radius"></a>

#### bpy.types.Curve.use_radius

Option for paths and curve-deform: apply the curve radius to objects following it and to deformed objects (default True)

**Type:**

bool

<a id="bpy.types.Curve.use_stretch"></a>

#### bpy.types.Curve.use_stretch

Option for curve-deform: make deformed child stretch along entire path (default False)

**Type:**

bool

<a id="bpy.types.Curve.transform"></a>

#### bpy.types.Curve.transform(matrix, *, shape_keys=False)

Transform curve by a matrix

**Parameters:**

- **matrix** ([`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix") | Sequence[Sequence[float]]) – Matrix (multi-dimensional array of 4 * 4 items, in [-inf, inf])
- **shape_keys** (bool) – Transform Shape Keys (optional)

<a id="bpy.types.Curve.validate_material_indices"></a>

#### bpy.types.Curve.validate_material_indices()

Validate material indices of splines or letters, return True when the curve has had invalid indices corrected (to default 0)

**Returns:**

Result

**Return type:**

bool

<a id="bpy.types.Curve.update_gpu_tag"></a>

#### bpy.types.Curve.update_gpu_tag()

update_gpu_tag

<a id="bpy.types.Curve.bl_rna_get_subclass"></a>

#### classmethod bpy.types.Curve.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.Curve.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.Curve.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, ID.name, ID.name_full, ID.id_type, ID.session_uid, ID.is_evaluated, ID.original, ID.users, ID.use_fake_user, ID.use_extra_user, ID.is_embedded_data, ID.is_linked_packed, ID.is_missing, ID.is_runtime_data, ID.is_editable, ID.tag, ID.is_library_indirect, ID.library, ID.library_weak_reference, ID.asset_data, ID.override_library, ID.preview

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, ID.bl_system_properties_get, ID.rename, ID.evaluated_get, ID.copy, ID.asset_mark, ID.asset_clear, ID.asset_generate_preview, ID.override_create, ID.override_hierarchy_create, ID.user_clear, ID.user_remap, ID.make_local, ID.user_of_id, ID.animation_data_create, ID.animation_data_clear, ID.update_tag, ID.preview_ensure, ID.bl_rna_get_subclass, ID.bl_rna_get_subclass_py

<a id="references"></a>

## References

|  |  |
| --- | --- |
| - `bpy.context.curve` - [`BlendData.curves`](bpy.types.BlendData.md#bpy.types.BlendData.curves "bpy.types.BlendData.curves") - [`BlendDataCurves.new`](bpy.types.BlendDataCurves.md#bpy.types.BlendDataCurves.new "bpy.types.BlendDataCurves.new") | - [`BlendDataCurves.remove`](bpy.types.BlendDataCurves.md#bpy.types.BlendDataCurves.remove "bpy.types.BlendDataCurves.remove") - [`Object.to_curve`](bpy.types.Object.md#bpy.types.Object.to_curve "bpy.types.Object.to_curve") |
