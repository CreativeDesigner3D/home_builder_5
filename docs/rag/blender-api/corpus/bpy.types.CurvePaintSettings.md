<!-- source: Blender Python API reference 5.2 / bpy.types.CurvePaintSettings.html -->

<a id="curvepaintsettings-bpy-struct"></a>

# CurvePaintSettings(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.CurvePaintSettings"></a>

### class bpy.types.CurvePaintSettings(bpy_struct)

<a id="bpy.types.CurvePaintSettings.corner_angle"></a>

#### bpy.types.CurvePaintSettings.corner_angle

Angles above this are considered corners (in [0, 3.14159], default 1.22173)

**Type:**

float

<a id="bpy.types.CurvePaintSettings.curve_type"></a>

#### bpy.types.CurvePaintSettings.curve_type

Type of curve to use for new strokes (default `'BEZIER'`)

**Type:**

Literal[‘POLY’, ‘BEZIER’]

<a id="bpy.types.CurvePaintSettings.depth_mode"></a>

#### bpy.types.CurvePaintSettings.depth_mode

Method of projecting depth (default `'CURSOR'`)

**Type:**

Literal[‘CURSOR’, ‘SURFACE’]

<a id="bpy.types.CurvePaintSettings.error_threshold"></a>

#### bpy.types.CurvePaintSettings.error_threshold

Allow deviation for a smoother, less precise line (in [1, 100], default 8)

**Type:**

int

<a id="bpy.types.CurvePaintSettings.fit_method"></a>

#### bpy.types.CurvePaintSettings.fit_method

Curve fitting method (default `'REFIT'`)

**Type:**

Literal[[Curve Fit Method Items](bpy_types_enum_items/curve_fit_method_items.md#rna-enum-curve-fit-method-items)]

<a id="bpy.types.CurvePaintSettings.radius_max"></a>

#### bpy.types.CurvePaintSettings.radius_max

Radius to use when the maximum pressure is applied (or when a tablet isn’t used) (in [0, 100], default 1.0)

**Type:**

float

<a id="bpy.types.CurvePaintSettings.radius_min"></a>

#### bpy.types.CurvePaintSettings.radius_min

Minimum radius when the minimum pressure is applied (also the minimum when tapering) (in [0, 100], default 0.0)

**Type:**

float

<a id="bpy.types.CurvePaintSettings.radius_taper_end"></a>

#### bpy.types.CurvePaintSettings.radius_taper_end

Taper factor for the radius of each point along the curve (in [0, 10], default 0.0)

**Type:**

float

<a id="bpy.types.CurvePaintSettings.radius_taper_start"></a>

#### bpy.types.CurvePaintSettings.radius_taper_start

Taper factor for the radius of each point along the curve (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.CurvePaintSettings.surface_offset"></a>

#### bpy.types.CurvePaintSettings.surface_offset

Offset the stroke from the surface (in [-10, 10], default 0.0)

**Type:**

float

<a id="bpy.types.CurvePaintSettings.surface_plane"></a>

#### bpy.types.CurvePaintSettings.surface_plane

Plane for projected stroke (default `'NORMAL_VIEW'`)

- `NORMAL_VIEW`
  Normal to Surface – Draw in a plane perpendicular to the surface.
- `NORMAL_SURFACE`
  Tangent to Surface – Draw in the surface plane.
- `VIEW`
  View – Draw in a plane aligned to the viewport.

**Type:**

Literal[‘NORMAL_VIEW’, ‘NORMAL_SURFACE’, ‘VIEW’]

<a id="bpy.types.CurvePaintSettings.use_corners_detect"></a>

#### bpy.types.CurvePaintSettings.use_corners_detect

Detect corners and use non-aligned handles (default True)

**Type:**

bool

<a id="bpy.types.CurvePaintSettings.use_offset_absolute"></a>

#### bpy.types.CurvePaintSettings.use_offset_absolute

Apply a fixed offset (don’t scale by the radius) (default False)

**Type:**

bool

<a id="bpy.types.CurvePaintSettings.use_pressure_radius"></a>

#### bpy.types.CurvePaintSettings.use_pressure_radius

Map tablet pressure to curve radius (default False)

**Type:**

bool

<a id="bpy.types.CurvePaintSettings.use_project_only_selected"></a>

#### bpy.types.CurvePaintSettings.use_project_only_selected

Project the strokes only onto selected objects (default False)

**Type:**

bool

<a id="bpy.types.CurvePaintSettings.use_stroke_endpoints"></a>

#### bpy.types.CurvePaintSettings.use_stroke_endpoints

Use the start of the stroke for the depth (default False)

**Type:**

bool

<a id="bpy.types.CurvePaintSettings.bl_rna_get_subclass"></a>

#### classmethod bpy.types.CurvePaintSettings.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.CurvePaintSettings.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.CurvePaintSettings.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`ToolSettings.curve_paint_settings`](bpy.types.ToolSettings.md#bpy.types.ToolSettings.curve_paint_settings "bpy.types.ToolSettings.curve_paint_settings") |  |
