<!-- source: Blender Python API reference 5.2 / bpy.types.BevelModifier.html -->

<a id="bevelmodifier-modifier"></a>

# BevelModifier(Modifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Modifier`](bpy.types.Modifier.md#bpy.types.Modifier "bpy.types.Modifier")

<a id="bpy.types.BevelModifier"></a>

### class bpy.types.BevelModifier(Modifier)

Bevel modifier to make edges and vertices more rounded

<a id="bpy.types.BevelModifier.affect"></a>

#### bpy.types.BevelModifier.affect

Affect edges or vertices (default `'EDGES'`)

- `VERTICES`
  Vertices – Affect only vertices.
- `EDGES`
  Edges – Affect only edges.

**Type:**

Literal[‘VERTICES’, ‘EDGES’]

<a id="bpy.types.BevelModifier.angle_limit"></a>

#### bpy.types.BevelModifier.angle_limit

Angle above which to bevel edges (in [0, 3.14159], default 0.523599)

**Type:**

float

<a id="bpy.types.BevelModifier.custom_profile"></a>

#### bpy.types.BevelModifier.custom_profile

The path for the custom profile (readonly)

**Type:**

[`CurveProfile`](bpy.types.CurveProfile.md#bpy.types.CurveProfile "bpy.types.CurveProfile") | None

<a id="bpy.types.BevelModifier.edge_weight"></a>

#### bpy.types.BevelModifier.edge_weight

Attribute name for edge weight (default “bevel_weight_edge”, never None)

**Type:**

str

<a id="bpy.types.BevelModifier.face_strength_mode"></a>

#### bpy.types.BevelModifier.face_strength_mode

Whether to set face strength, and which faces to set it on (default `'FSTR_NONE'`)

- `FSTR_NONE`
  None – Do not set face strength.
- `FSTR_NEW`
  New – Set face strength on new faces only.
- `FSTR_AFFECTED`
  Affected – Set face strength on new and affected faces only.
- `FSTR_ALL`
  All – Set face strength on all faces.

**Type:**

Literal[‘FSTR_NONE’, ‘FSTR_NEW’, ‘FSTR_AFFECTED’, ‘FSTR_ALL’]

<a id="bpy.types.BevelModifier.harden_normals"></a>

#### bpy.types.BevelModifier.harden_normals

Match normals of new faces to adjacent faces (default False)

**Type:**

bool

<a id="bpy.types.BevelModifier.invert_vertex_group"></a>

#### bpy.types.BevelModifier.invert_vertex_group

Invert vertex group influence (default False)

**Type:**

bool

<a id="bpy.types.BevelModifier.limit_method"></a>

#### bpy.types.BevelModifier.limit_method

(default `'ANGLE'`)

- `NONE`
  None – Bevel the entire mesh by a constant amount.
- `ANGLE`
  Angle – Only bevel edges with sharp enough angles between faces.
- `WEIGHT`
  Weight – Use bevel weights to determine how much bevel is applied in edge mode.
- `VGROUP`
  Vertex Group – Use vertex group weights to select whether vertex or edge is beveled.

**Type:**

Literal[‘NONE’, ‘ANGLE’, ‘WEIGHT’, ‘VGROUP’]

<a id="bpy.types.BevelModifier.loop_slide"></a>

#### bpy.types.BevelModifier.loop_slide

Prefer sliding along edges to having even widths (default True)

**Type:**

bool

<a id="bpy.types.BevelModifier.mark_seam"></a>

#### bpy.types.BevelModifier.mark_seam

Mark Seams along beveled edges (default False)

**Type:**

bool

<a id="bpy.types.BevelModifier.mark_sharp"></a>

#### bpy.types.BevelModifier.mark_sharp

Mark beveled edges as sharp (default False)

**Type:**

bool

<a id="bpy.types.BevelModifier.material"></a>

#### bpy.types.BevelModifier.material

Material index of generated faces, -1 for automatic (in [-1, 32767], default -1)

**Type:**

int

<a id="bpy.types.BevelModifier.miter_inner"></a>

#### bpy.types.BevelModifier.miter_inner

Pattern to use for inside of miters (default `'MITER_SHARP'`)

- `MITER_SHARP`
  Sharp – Inside of miter is sharp.
- `MITER_ARC`
  Arc – Inside of miter is arc.

**Type:**

Literal[‘MITER_SHARP’, ‘MITER_ARC’]

<a id="bpy.types.BevelModifier.miter_outer"></a>

#### bpy.types.BevelModifier.miter_outer

Pattern to use for outside of miters (default `'MITER_SHARP'`)

- `MITER_SHARP`
  Sharp – Outside of miter is sharp.
- `MITER_PATCH`
  Patch – Outside of miter is squared-off patch.
- `MITER_ARC`
  Arc – Outside of miter is arc.

**Type:**

Literal[‘MITER_SHARP’, ‘MITER_PATCH’, ‘MITER_ARC’]

<a id="bpy.types.BevelModifier.offset_type"></a>

#### bpy.types.BevelModifier.offset_type

What distance Width measures (default `'OFFSET'`)

- `OFFSET`
  Offset – Amount is offset of new edges from original.
- `WIDTH`
  Width – Amount is width of new face.
- `DEPTH`
  Depth – Amount is perpendicular distance from original edge to bevel face.
- `PERCENT`
  Percent – Amount is percent of adjacent edge length.
- `ABSOLUTE`
  Absolute – Amount is absolute distance along adjacent edge.

**Type:**

Literal[‘OFFSET’, ‘WIDTH’, ‘DEPTH’, ‘PERCENT’, ‘ABSOLUTE’]

<a id="bpy.types.BevelModifier.profile"></a>

#### bpy.types.BevelModifier.profile

The profile shape (0.5 = round) (in [0, 1], default 0.5)

**Type:**

float

<a id="bpy.types.BevelModifier.profile_type"></a>

#### bpy.types.BevelModifier.profile_type

The type of shape used to rebuild a beveled section (default `'SUPERELLIPSE'`)

- `SUPERELLIPSE`
  Superellipse – The profile can be a concave or convex curve.
- `CUSTOM`
  Custom – The profile can be any arbitrary path between its endpoints.

**Type:**

Literal[‘SUPERELLIPSE’, ‘CUSTOM’]

<a id="bpy.types.BevelModifier.segments"></a>

#### bpy.types.BevelModifier.segments

Number of segments for round edges/verts (in [1, 1000], default 1)

**Type:**

int

<a id="bpy.types.BevelModifier.spread"></a>

#### bpy.types.BevelModifier.spread

Spread distance for inner miter arcs (in [0, inf], default 0.1)

**Type:**

float

<a id="bpy.types.BevelModifier.use_clamp_overlap"></a>

#### bpy.types.BevelModifier.use_clamp_overlap

Clamp the width to avoid overlap (default True)

**Type:**

bool

<a id="bpy.types.BevelModifier.vertex_group"></a>

#### bpy.types.BevelModifier.vertex_group

Vertex group name (default “”, never None)

**Type:**

str

<a id="bpy.types.BevelModifier.vertex_weight"></a>

#### bpy.types.BevelModifier.vertex_weight

Attribute name for vertex weight (default “bevel_weight_vert”, never None)

**Type:**

str

<a id="bpy.types.BevelModifier.vmesh_method"></a>

#### bpy.types.BevelModifier.vmesh_method

The method to use to create the mesh at intersections (default `'ADJ'`)

- `ADJ`
  Grid Fill – Default patterned fill.
- `CUTOFF`
  Cutoff – A cut-off at the end of each profile before the intersection.

**Type:**

Literal[‘ADJ’, ‘CUTOFF’]

<a id="bpy.types.BevelModifier.width"></a>

#### bpy.types.BevelModifier.width

Bevel amount (in [0, inf], default 0.1)

**Type:**

float

<a id="bpy.types.BevelModifier.width_pct"></a>

#### bpy.types.BevelModifier.width_pct

Bevel amount for percentage method (in [0, inf], default 0.1)

**Type:**

float

<a id="bpy.types.BevelModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.BevelModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.BevelModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.BevelModifier.bl_rna_get_subclass_py(id, default=None, /)

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
