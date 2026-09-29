<!-- source: Blender Python API reference 5.2 / bpy.types.SolidifyModifier.html -->

<a id="solidifymodifier-modifier"></a>

# SolidifyModifier(Modifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Modifier`](bpy.types.Modifier.md#bpy.types.Modifier "bpy.types.Modifier")

<a id="bpy.types.SolidifyModifier"></a>

### class bpy.types.SolidifyModifier(Modifier)

Create a solid skin, compensating for sharp angles

<a id="bpy.types.SolidifyModifier.bevel_convex"></a>

#### bpy.types.SolidifyModifier.bevel_convex

Edge bevel weight to be added to outside edges (in [-1, 1], default 0.0)

**Type:**

float

<a id="bpy.types.SolidifyModifier.edge_crease_inner"></a>

#### bpy.types.SolidifyModifier.edge_crease_inner

Assign a crease to inner edges (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.SolidifyModifier.edge_crease_outer"></a>

#### bpy.types.SolidifyModifier.edge_crease_outer

Assign a crease to outer edges (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.SolidifyModifier.edge_crease_rim"></a>

#### bpy.types.SolidifyModifier.edge_crease_rim

Assign a crease to the edges making up the rim (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.SolidifyModifier.invert_vertex_group"></a>

#### bpy.types.SolidifyModifier.invert_vertex_group

Invert the vertex group influence (default False)

**Type:**

bool

<a id="bpy.types.SolidifyModifier.material_offset"></a>

#### bpy.types.SolidifyModifier.material_offset

Offset material index of generated faces (in [-32768, 32767], default 0)

**Type:**

int

<a id="bpy.types.SolidifyModifier.material_offset_rim"></a>

#### bpy.types.SolidifyModifier.material_offset_rim

Offset material index of generated rim faces (in [-32768, 32767], default 0)

**Type:**

int

<a id="bpy.types.SolidifyModifier.nonmanifold_boundary_mode"></a>

#### bpy.types.SolidifyModifier.nonmanifold_boundary_mode

Selects the boundary adjustment algorithm (default `'NONE'`)

- `NONE`
  None – No shape correction.
- `ROUND`
  Round – Round open perimeter shape.
- `FLAT`
  Flat – Flat open perimeter shape.

**Type:**

Literal[‘NONE’, ‘ROUND’, ‘FLAT’]

<a id="bpy.types.SolidifyModifier.nonmanifold_merge_threshold"></a>

#### bpy.types.SolidifyModifier.nonmanifold_merge_threshold

Distance within which degenerated geometry is merged (in [0, 1], default 0.0001)

**Type:**

float

<a id="bpy.types.SolidifyModifier.nonmanifold_thickness_mode"></a>

#### bpy.types.SolidifyModifier.nonmanifold_thickness_mode

Selects the used thickness algorithm (default `'CONSTRAINTS'`)

- `FIXED`
  Fixed – Most basic thickness calculation.
- `EVEN`
  Even – Even thickness calculation which takes the angle between faces into account.
- `CONSTRAINTS`
  Constraints – Thickness calculation using constraints, most advanced.

**Type:**

Literal[‘FIXED’, ‘EVEN’, ‘CONSTRAINTS’]

<a id="bpy.types.SolidifyModifier.offset"></a>

#### bpy.types.SolidifyModifier.offset

Offset the thickness from the center (in [-inf, inf], default -1.0)

**Type:**

float

<a id="bpy.types.SolidifyModifier.rim_vertex_group"></a>

#### bpy.types.SolidifyModifier.rim_vertex_group

Vertex group that the generated rim geometry will be weighted to (default “”, never None)

**Type:**

str

<a id="bpy.types.SolidifyModifier.shell_vertex_group"></a>

#### bpy.types.SolidifyModifier.shell_vertex_group

Vertex group that the generated shell geometry will be weighted to (default “”, never None)

**Type:**

str

<a id="bpy.types.SolidifyModifier.solidify_mode"></a>

#### bpy.types.SolidifyModifier.solidify_mode

Selects the used algorithm (default `'EXTRUDE'`)

- `EXTRUDE`
  Simple – Output a solidified version of a mesh by simple extrusion.
- `NON_MANIFOLD`
  Complex – Output a manifold mesh even if the base mesh is non-manifold, where edges have 3 or more connecting faces. This method is slower..

**Type:**

Literal[‘EXTRUDE’, ‘NON_MANIFOLD’]

<a id="bpy.types.SolidifyModifier.thickness"></a>

#### bpy.types.SolidifyModifier.thickness

Thickness of the shell (in [-inf, inf], default 0.01)

**Type:**

float

<a id="bpy.types.SolidifyModifier.thickness_clamp"></a>

#### bpy.types.SolidifyModifier.thickness_clamp

Offset clamp based on geometry scale (in [0, 100], default 0.0)

**Type:**

float

<a id="bpy.types.SolidifyModifier.thickness_vertex_group"></a>

#### bpy.types.SolidifyModifier.thickness_vertex_group

Thickness factor to use for zero vertex group influence (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.SolidifyModifier.use_even_offset"></a>

#### bpy.types.SolidifyModifier.use_even_offset

Maintain thickness by adjusting for sharp corners (slow, disable when not needed) (default False)

**Type:**

bool

<a id="bpy.types.SolidifyModifier.use_flat_faces"></a>

#### bpy.types.SolidifyModifier.use_flat_faces

Make faces use the minimal vertex weight assigned to their vertices (ensures new faces remain parallel to their original ones, slow, disable when not needed) (default False)

**Type:**

bool

<a id="bpy.types.SolidifyModifier.use_flip_normals"></a>

#### bpy.types.SolidifyModifier.use_flip_normals

Invert the face direction (default False)

**Type:**

bool

<a id="bpy.types.SolidifyModifier.use_quality_normals"></a>

#### bpy.types.SolidifyModifier.use_quality_normals

Calculate normals which result in more even thickness (slow, disable when not needed) (default False)

**Type:**

bool

<a id="bpy.types.SolidifyModifier.use_rim"></a>

#### bpy.types.SolidifyModifier.use_rim

Create edge loops between the inner and outer surfaces on face edges (slow, disable when not needed) (default True)

**Type:**

bool

<a id="bpy.types.SolidifyModifier.use_rim_only"></a>

#### bpy.types.SolidifyModifier.use_rim_only

Only add the rim to the original data (default False)

**Type:**

bool

<a id="bpy.types.SolidifyModifier.use_thickness_angle_clamp"></a>

#### bpy.types.SolidifyModifier.use_thickness_angle_clamp

Clamp thickness based on angles (default False)

**Type:**

bool

<a id="bpy.types.SolidifyModifier.vertex_group"></a>

#### bpy.types.SolidifyModifier.vertex_group

Vertex group name (default “”, never None)

**Type:**

str

<a id="bpy.types.SolidifyModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.SolidifyModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.SolidifyModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.SolidifyModifier.bl_rna_get_subclass_py(id, default=None, /)

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
