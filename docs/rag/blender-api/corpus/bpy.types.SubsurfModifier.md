<!-- source: Blender Python API reference 5.2 / bpy.types.SubsurfModifier.html -->

<a id="subsurfmodifier-modifier"></a>

# SubsurfModifier(Modifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Modifier`](bpy.types.Modifier.md#bpy.types.Modifier "bpy.types.Modifier")

<a id="bpy.types.SubsurfModifier"></a>

### class bpy.types.SubsurfModifier(Modifier)

Subdivision surface modifier

<a id="bpy.types.SubsurfModifier.adaptive_object_edge_length"></a>

#### bpy.types.SubsurfModifier.adaptive_object_edge_length

Target object space edge length for adaptive subdivision (in [0.0001, 1000], default 0.01)

**Type:**

float

<a id="bpy.types.SubsurfModifier.adaptive_pixel_size"></a>

#### bpy.types.SubsurfModifier.adaptive_pixel_size

Target polygon pixel size for adaptive subdivision (in [0.1, 1000], default 1.0)

**Type:**

float

<a id="bpy.types.SubsurfModifier.adaptive_space"></a>

#### bpy.types.SubsurfModifier.adaptive_space

How to adaptively subdivide the mesh (default `'PIXEL'`)

- `PIXEL`
  Pixel – Subdivide polygons to reach a specified pixel size on screen.
- `OBJECT`
  Object – Subdivide to reach a specified edge length in object space. This is required to use adaptive subdivision for instanced meshes.

**Type:**

Literal[‘PIXEL’, ‘OBJECT’]

<a id="bpy.types.SubsurfModifier.boundary_smooth"></a>

#### bpy.types.SubsurfModifier.boundary_smooth

Controls how open boundaries are smoothed (default `'ALL'`)

**Type:**

Literal[[Subdivision Boundary Smooth Items](bpy_types_enum_items/subdivision_boundary_smooth_items.md#rna-enum-subdivision-boundary-smooth-items)]

<a id="bpy.types.SubsurfModifier.levels"></a>

#### bpy.types.SubsurfModifier.levels

Number of subdivisions to perform in the 3D viewport (in [0, 11], default 1)

**Type:**

int

<a id="bpy.types.SubsurfModifier.open_adaptive_subdivision_panel"></a>

#### bpy.types.SubsurfModifier.open_adaptive_subdivision_panel

(default False)

**Type:**

bool

<a id="bpy.types.SubsurfModifier.open_advanced_panel"></a>

#### bpy.types.SubsurfModifier.open_advanced_panel

(default False)

**Type:**

bool

<a id="bpy.types.SubsurfModifier.quality"></a>

#### bpy.types.SubsurfModifier.quality

Accuracy of vertex positions, lower value is faster but less precise (in [1, 10], default 3)

**Type:**

int

<a id="bpy.types.SubsurfModifier.render_levels"></a>

#### bpy.types.SubsurfModifier.render_levels

Number of subdivisions to perform when rendering (in [0, 11], default 2)

**Type:**

int

<a id="bpy.types.SubsurfModifier.show_only_control_edges"></a>

#### bpy.types.SubsurfModifier.show_only_control_edges

Skip displaying interior subdivided edges (default True)

**Type:**

bool

<a id="bpy.types.SubsurfModifier.subdivision_type"></a>

#### bpy.types.SubsurfModifier.subdivision_type

Select type of subdivision algorithm (default `'CATMULL_CLARK'`)

- `CATMULL_CLARK`
  Catmull-Clark – Create a smooth curved surface using the Catmull-Clark subdivision scheme.
- `SIMPLE`
  Simple – Subdivide faces without changing shape.

**Type:**

Literal[‘CATMULL_CLARK’, ‘SIMPLE’]

<a id="bpy.types.SubsurfModifier.use_adaptive_subdivision"></a>

#### bpy.types.SubsurfModifier.use_adaptive_subdivision

Adaptively subdivide mesh based on camera distance (default False)

**Type:**

bool

<a id="bpy.types.SubsurfModifier.use_creases"></a>

#### bpy.types.SubsurfModifier.use_creases

Use mesh crease information to sharpen edges or corners (default True)

**Type:**

bool

<a id="bpy.types.SubsurfModifier.use_custom_normals"></a>

#### bpy.types.SubsurfModifier.use_custom_normals

Interpolates existing custom normals to resulting mesh (default False)

**Type:**

bool

<a id="bpy.types.SubsurfModifier.use_limit_surface"></a>

#### bpy.types.SubsurfModifier.use_limit_surface

Place vertices at the surface that would be produced with infinite levels of subdivision (smoothest possible shape) (default True)

**Type:**

bool

<a id="bpy.types.SubsurfModifier.uv_smooth"></a>

#### bpy.types.SubsurfModifier.uv_smooth

Controls how smoothing is applied to UVs (default `'PRESERVE_BOUNDARIES'`)

**Type:**

Literal[[Subdivision Uv Smooth Items](bpy_types_enum_items/subdivision_uv_smooth_items.md#rna-enum-subdivision-uv-smooth-items)]

<a id="bpy.types.SubsurfModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.SubsurfModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.SubsurfModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.SubsurfModifier.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, Modifier.name, Modifier.type, Modifier.show_viewport, Modifier.show_render, Modifier.show_in_editmode, Modifier.show_on_cage, Modifier.show_expanded, Modifier.is_active, Modifier.use_pin_to_last, Modifier.is_override_data, Modifier.use_apply_on_spline, Modifier.execution_time, Modifier.persistent_uid

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, Modifier.bl_rna_get_subclass, Modifier.bl_rna_get_subclass_py
