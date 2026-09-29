<!-- source: Blender Python API reference 5.2 / bpy.types.DecimateModifier.html -->

<a id="decimatemodifier-modifier"></a>

# DecimateModifier(Modifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Modifier`](bpy.types.Modifier.md#bpy.types.Modifier "bpy.types.Modifier")

<a id="bpy.types.DecimateModifier"></a>

### class bpy.types.DecimateModifier(Modifier)

Decimation modifier

<a id="bpy.types.DecimateModifier.angle_limit"></a>

#### bpy.types.DecimateModifier.angle_limit

Only dissolve angles below this (planar only) (in [0, 3.14159], default 0.0872665)

**Type:**

float

<a id="bpy.types.DecimateModifier.decimate_type"></a>

#### bpy.types.DecimateModifier.decimate_type

(default `'COLLAPSE'`)

- `COLLAPSE`
  Collapse – Use edge collapsing.
- `UNSUBDIV`
  Un-Subdivide – Use un-subdivide face reduction.
- `DISSOLVE`
  Planar – Dissolve geometry to form planar polygons.

**Type:**

Literal[‘COLLAPSE’, ‘UNSUBDIV’, ‘DISSOLVE’]

<a id="bpy.types.DecimateModifier.delimit"></a>

#### bpy.types.DecimateModifier.delimit

Limit merging geometry (default set())

**Type:**

set[Literal[[Mesh Delimit Mode Items](bpy_types_enum_items/mesh_delimit_mode_items.md#rna-enum-mesh-delimit-mode-items)]]

<a id="bpy.types.DecimateModifier.face_count"></a>

#### bpy.types.DecimateModifier.face_count

The current number of faces in the decimated mesh (in [-inf, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.DecimateModifier.invert_vertex_group"></a>

#### bpy.types.DecimateModifier.invert_vertex_group

Invert vertex group influence (collapse only) (default False)

**Type:**

bool

<a id="bpy.types.DecimateModifier.iterations"></a>

#### bpy.types.DecimateModifier.iterations

Number of times reduce the geometry (unsubdivide only) (in [0, 32767], default 0)

**Type:**

int

<a id="bpy.types.DecimateModifier.ratio"></a>

#### bpy.types.DecimateModifier.ratio

Ratio of triangles to reduce to (collapse only) (in [0, 1], default 1.0)

**Type:**

float

<a id="bpy.types.DecimateModifier.symmetry_axis"></a>

#### bpy.types.DecimateModifier.symmetry_axis

Axis of symmetry (default `'X'`)

**Type:**

Literal[[Axis Xyz Items](bpy_types_enum_items/axis_xyz_items.md#rna-enum-axis-xyz-items)]

<a id="bpy.types.DecimateModifier.use_collapse_triangulate"></a>

#### bpy.types.DecimateModifier.use_collapse_triangulate

Keep triangulated faces resulting from decimation (collapse only) (default False)

**Type:**

bool

<a id="bpy.types.DecimateModifier.use_dissolve_boundaries"></a>

#### bpy.types.DecimateModifier.use_dissolve_boundaries

Dissolve all vertices in between face boundaries (planar only) (default False)

**Type:**

bool

<a id="bpy.types.DecimateModifier.use_symmetry"></a>

#### bpy.types.DecimateModifier.use_symmetry

Maintain symmetry on an axis (default False)

**Type:**

bool

<a id="bpy.types.DecimateModifier.vertex_group"></a>

#### bpy.types.DecimateModifier.vertex_group

Vertex group name (collapse only) (default “”, never None)

**Type:**

str

<a id="bpy.types.DecimateModifier.vertex_group_factor"></a>

#### bpy.types.DecimateModifier.vertex_group_factor

Vertex group strength (in [0, 1000], default 1.0)

**Type:**

float

<a id="bpy.types.DecimateModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.DecimateModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.DecimateModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.DecimateModifier.bl_rna_get_subclass_py(id, default=None, /)

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
