<!-- source: Blender Python API reference 5.2 / bpy.types.GreasePencilShrinkwrapModifier.html -->

<a id="greasepencilshrinkwrapmodifier-modifier"></a>

# GreasePencilShrinkwrapModifier(Modifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Modifier`](bpy.types.Modifier.md#bpy.types.Modifier "bpy.types.Modifier")

<a id="bpy.types.GreasePencilShrinkwrapModifier"></a>

### class bpy.types.GreasePencilShrinkwrapModifier(Modifier)

Shrink wrapping modifier to shrink wrap an object to a target

<a id="bpy.types.GreasePencilShrinkwrapModifier.auxiliary_target"></a>

#### bpy.types.GreasePencilShrinkwrapModifier.auxiliary_target

Additional mesh target to shrink to

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.GreasePencilShrinkwrapModifier.cull_face"></a>

#### bpy.types.GreasePencilShrinkwrapModifier.cull_face

Stop vertices from projecting to a face on the target when facing towards/away (default `'OFF'`)

**Type:**

Literal[[Shrinkwrap Face Cull Items](bpy_types_enum_items/shrinkwrap_face_cull_items.md#rna-enum-shrinkwrap-face-cull-items)]

<a id="bpy.types.GreasePencilShrinkwrapModifier.invert_layer_filter"></a>

#### bpy.types.GreasePencilShrinkwrapModifier.invert_layer_filter

Invert layer filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilShrinkwrapModifier.invert_layer_pass_filter"></a>

#### bpy.types.GreasePencilShrinkwrapModifier.invert_layer_pass_filter

Invert layer pass filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilShrinkwrapModifier.invert_material_filter"></a>

#### bpy.types.GreasePencilShrinkwrapModifier.invert_material_filter

Invert material filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilShrinkwrapModifier.invert_material_pass_filter"></a>

#### bpy.types.GreasePencilShrinkwrapModifier.invert_material_pass_filter

Invert material pass filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilShrinkwrapModifier.invert_vertex_group"></a>

#### bpy.types.GreasePencilShrinkwrapModifier.invert_vertex_group

Invert vertex group weights (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilShrinkwrapModifier.layer_pass_filter"></a>

#### bpy.types.GreasePencilShrinkwrapModifier.layer_pass_filter

Layer pass filter (in [0, 100], default 0)

**Type:**

int

<a id="bpy.types.GreasePencilShrinkwrapModifier.material_filter"></a>

#### bpy.types.GreasePencilShrinkwrapModifier.material_filter

Material used for filtering

**Type:**

[`Material`](bpy.types.Material.md#bpy.types.Material "bpy.types.Material") | None

<a id="bpy.types.GreasePencilShrinkwrapModifier.material_pass_filter"></a>

#### bpy.types.GreasePencilShrinkwrapModifier.material_pass_filter

Material pass (in [0, 100], default 0)

**Type:**

int

<a id="bpy.types.GreasePencilShrinkwrapModifier.offset"></a>

#### bpy.types.GreasePencilShrinkwrapModifier.offset

Distance to keep from the target (in [-inf, inf], default 0.05)

**Type:**

float

<a id="bpy.types.GreasePencilShrinkwrapModifier.open_influence_panel"></a>

#### bpy.types.GreasePencilShrinkwrapModifier.open_influence_panel

(default False)

**Type:**

bool

<a id="bpy.types.GreasePencilShrinkwrapModifier.project_limit"></a>

#### bpy.types.GreasePencilShrinkwrapModifier.project_limit

Limit the distance used for projection (zero disables) (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.GreasePencilShrinkwrapModifier.smooth_factor"></a>

#### bpy.types.GreasePencilShrinkwrapModifier.smooth_factor

Amount of smoothing to apply (in [0, 1], default 0.05)

**Type:**

float

<a id="bpy.types.GreasePencilShrinkwrapModifier.smooth_step"></a>

#### bpy.types.GreasePencilShrinkwrapModifier.smooth_step

Number of times to apply smooth (high numbers can reduce FPS) (in [1, 10], default 1)

**Type:**

int

<a id="bpy.types.GreasePencilShrinkwrapModifier.subsurf_levels"></a>

#### bpy.types.GreasePencilShrinkwrapModifier.subsurf_levels

Number of subdivisions that must be performed before extracting vertices’ positions and normals (in [0, 6], default 0)

**Type:**

int

<a id="bpy.types.GreasePencilShrinkwrapModifier.target"></a>

#### bpy.types.GreasePencilShrinkwrapModifier.target

Mesh target to shrink to

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.GreasePencilShrinkwrapModifier.tree_node_filter"></a>

#### bpy.types.GreasePencilShrinkwrapModifier.tree_node_filter

Layer name (default “”, never None)

**Type:**

str

<a id="bpy.types.GreasePencilShrinkwrapModifier.use_invert_cull"></a>

#### bpy.types.GreasePencilShrinkwrapModifier.use_invert_cull

When projecting in the negative direction invert the face cull mode (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilShrinkwrapModifier.use_layer_group_filter"></a>

#### bpy.types.GreasePencilShrinkwrapModifier.use_layer_group_filter

Filter by layer group name (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilShrinkwrapModifier.use_layer_pass_filter"></a>

#### bpy.types.GreasePencilShrinkwrapModifier.use_layer_pass_filter

Use layer pass filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilShrinkwrapModifier.use_material_pass_filter"></a>

#### bpy.types.GreasePencilShrinkwrapModifier.use_material_pass_filter

Use material pass filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilShrinkwrapModifier.use_negative_direction"></a>

#### bpy.types.GreasePencilShrinkwrapModifier.use_negative_direction

Allow vertices to move in the negative direction of axis (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilShrinkwrapModifier.use_positive_direction"></a>

#### bpy.types.GreasePencilShrinkwrapModifier.use_positive_direction

Allow vertices to move in the positive direction of axis (default True)

**Type:**

bool

<a id="bpy.types.GreasePencilShrinkwrapModifier.use_project_x"></a>

#### bpy.types.GreasePencilShrinkwrapModifier.use_project_x

(default False)

**Type:**

bool

<a id="bpy.types.GreasePencilShrinkwrapModifier.use_project_y"></a>

#### bpy.types.GreasePencilShrinkwrapModifier.use_project_y

(default False)

**Type:**

bool

<a id="bpy.types.GreasePencilShrinkwrapModifier.use_project_z"></a>

#### bpy.types.GreasePencilShrinkwrapModifier.use_project_z

(default False)

**Type:**

bool

<a id="bpy.types.GreasePencilShrinkwrapModifier.vertex_group_name"></a>

#### bpy.types.GreasePencilShrinkwrapModifier.vertex_group_name

Vertex group name for modulating the deform (default “”, never None)

**Type:**

str

<a id="bpy.types.GreasePencilShrinkwrapModifier.wrap_method"></a>

#### bpy.types.GreasePencilShrinkwrapModifier.wrap_method

(default `'NEAREST_SURFACEPOINT'`)

**Type:**

Literal[[Shrinkwrap Type Items](bpy_types_enum_items/shrinkwrap_type_items.md#rna-enum-shrinkwrap-type-items)]

<a id="bpy.types.GreasePencilShrinkwrapModifier.wrap_mode"></a>

#### bpy.types.GreasePencilShrinkwrapModifier.wrap_mode

Select how vertices are constrained to the target surface (default `'ON_SURFACE'`)

**Type:**

Literal[[Modifier Shrinkwrap Mode Items](bpy_types_enum_items/modifier_shrinkwrap_mode_items.md#rna-enum-modifier-shrinkwrap-mode-items)]

<a id="bpy.types.GreasePencilShrinkwrapModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.GreasePencilShrinkwrapModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.GreasePencilShrinkwrapModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.GreasePencilShrinkwrapModifier.bl_rna_get_subclass_py(id, default=None, /)

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
