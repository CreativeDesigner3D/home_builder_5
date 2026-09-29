<!-- source: Blender Python API reference 5.2 / bpy.types.Sculpt.html -->

<a id="sculpt-paint"></a>

# Sculpt(Paint)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Paint`](bpy.types.Paint.md#bpy.types.Paint "bpy.types.Paint")

<a id="bpy.types.Sculpt"></a>

### class bpy.types.Sculpt(Paint)

<a id="bpy.types.Sculpt.constant_detail_resolution"></a>

#### bpy.types.Sculpt.constant_detail_resolution

Maximum edge length for dynamic topology sculpting (as divisor of Blender unit - higher value means smaller edge length) (in [0.0001, inf], default 3.0)

**Type:**

float

<a id="bpy.types.Sculpt.detail_percent"></a>

#### bpy.types.Sculpt.detail_percent

Maximum edge length for dynamic topology sculpting (in brush percentage) (in [0.5, 100], default 25.0)

**Type:**

float

<a id="bpy.types.Sculpt.detail_refine_method"></a>

#### bpy.types.Sculpt.detail_refine_method

In dynamic-topology mode, how to add or remove mesh detail (default `'SUBDIVIDE_COLLAPSE'`)

- `SUBDIVIDE`
  Subdivide Edges – Subdivide long edges to add mesh detail where needed.
- `COLLAPSE`
  Collapse Edges – Collapse short edges to remove mesh detail where possible.
- `SUBDIVIDE_COLLAPSE`
  Subdivide Collapse – Both subdivide long edges and collapse short edges to refine mesh detail.

**Type:**

Literal[‘SUBDIVIDE’, ‘COLLAPSE’, ‘SUBDIVIDE_COLLAPSE’]

<a id="bpy.types.Sculpt.detail_size"></a>

#### bpy.types.Sculpt.detail_size

Maximum edge length for dynamic topology sculpting (in pixels) (in [0.5, 40], default 12.0)

**Type:**

float

<a id="bpy.types.Sculpt.detail_type_method"></a>

#### bpy.types.Sculpt.detail_type_method

In dynamic-topology mode, how mesh detail size is calculated (default `'RELATIVE'`)

- `RELATIVE`
  Relative Detail – Mesh detail is relative to the brush size and detail size.
- `CONSTANT`
  Constant Detail – Mesh detail is constant in world space according to detail size.
- `BRUSH`
  Brush Detail – Mesh detail is relative to brush size.
- `MANUAL`
  Manual Detail – Mesh detail does not change on each stroke, only when using Flood Fill.

**Type:**

Literal[‘RELATIVE’, ‘CONSTANT’, ‘BRUSH’, ‘MANUAL’]

<a id="bpy.types.Sculpt.gravity"></a>

#### bpy.types.Sculpt.gravity

Amount of gravity after each dab (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.Sculpt.gravity_object"></a>

#### bpy.types.Sculpt.gravity_object

Object whose Z axis defines orientation of gravity

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.Sculpt.lock_x"></a>

#### bpy.types.Sculpt.lock_x

Disallow changes to the X axis of vertices (default False)

**Type:**

bool

<a id="bpy.types.Sculpt.lock_y"></a>

#### bpy.types.Sculpt.lock_y

Disallow changes to the Y axis of vertices (default False)

**Type:**

bool

<a id="bpy.types.Sculpt.lock_z"></a>

#### bpy.types.Sculpt.lock_z

Disallow changes to the Z axis of vertices (default False)

**Type:**

bool

<a id="bpy.types.Sculpt.symmetrize_direction"></a>

#### bpy.types.Sculpt.symmetrize_direction

Source and destination for symmetrize operator (default `'NEGATIVE_X'`)

**Type:**

Literal[[Symmetrize Direction Items](bpy_types_enum_items/symmetrize_direction_items.md#rna-enum-symmetrize-direction-items)]

<a id="bpy.types.Sculpt.transform_mode"></a>

#### bpy.types.Sculpt.transform_mode

How the transformation is going to be applied to the target (default `'ALL_VERTICES'`)

- `ALL_VERTICES`
  All Vertices – Applies the transformation to all vertices in the mesh.
- `RADIUS_ELASTIC`
  Elastic – Applies the transformation simulating elasticity using the radius of the cursor.

**Type:**

Literal[‘ALL_VERTICES’, ‘RADIUS_ELASTIC’]

<a id="bpy.types.Sculpt.use_deform_only"></a>

#### bpy.types.Sculpt.use_deform_only

Use only deformation modifiers (temporary disable all constructive modifiers except multi-resolution) (default False)

**Type:**

bool

<a id="bpy.types.Sculpt.bl_rna_get_subclass"></a>

#### classmethod bpy.types.Sculpt.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.Sculpt.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.Sculpt.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, Paint.brush, Paint.brush_asset_reference, Paint.palette, Paint.show_brush, Paint.show_brush_on_surface, Paint.show_low_resolution, Paint.use_sculpt_delay_updates, Paint.show_bvh_nodes, Paint.use_symmetry_x, Paint.use_symmetry_y, Paint.use_symmetry_z, Paint.use_symmetry_feather, Paint.cavity_curve, Paint.use_cavity, Paint.tile_offset, Paint.tile_x, Paint.tile_y, Paint.tile_z, Paint.show_strength_curve, Paint.show_size_curve, Paint.show_jitter_curve, Paint.unified_paint_settings, Paint.mesh_automasking_settings

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, Paint.bl_rna_get_subclass, Paint.bl_rna_get_subclass_py

<a id="references"></a>

## References

|  |  |
| --- | --- |
| - [`ToolSettings.sculpt`](bpy.types.ToolSettings.md#bpy.types.ToolSettings.sculpt "bpy.types.ToolSettings.sculpt") |  |
