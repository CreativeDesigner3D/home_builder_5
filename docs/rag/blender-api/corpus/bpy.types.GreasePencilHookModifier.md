<!-- source: Blender Python API reference 5.2 / bpy.types.GreasePencilHookModifier.html -->

<a id="greasepencilhookmodifier-modifier"></a>

# GreasePencilHookModifier(Modifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Modifier`](bpy.types.Modifier.md#bpy.types.Modifier "bpy.types.Modifier")

<a id="bpy.types.GreasePencilHookModifier"></a>

### class bpy.types.GreasePencilHookModifier(Modifier)

Hook modifier to modify the location of stroke points

<a id="bpy.types.GreasePencilHookModifier.center"></a>

#### bpy.types.GreasePencilHookModifier.center

(array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.GreasePencilHookModifier.custom_curve"></a>

#### bpy.types.GreasePencilHookModifier.custom_curve

Custom curve to apply effect (readonly)

**Type:**

[`CurveMapping`](bpy.types.CurveMapping.md#bpy.types.CurveMapping "bpy.types.CurveMapping") | None

<a id="bpy.types.GreasePencilHookModifier.falloff_radius"></a>

#### bpy.types.GreasePencilHookModifier.falloff_radius

If not zero, the distance from the hook where influence ends (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.GreasePencilHookModifier.falloff_type"></a>

#### bpy.types.GreasePencilHookModifier.falloff_type

(default `'SMOOTH'`)

**Type:**

Literal[‘NONE’, ‘CURVE’, ‘SMOOTH’, ‘SPHERE’, ‘ROOT’, ‘INVERSE_SQUARE’, ‘SHARP’, ‘LINEAR’, ‘CONSTANT’]

<a id="bpy.types.GreasePencilHookModifier.invert_layer_filter"></a>

#### bpy.types.GreasePencilHookModifier.invert_layer_filter

Invert layer filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilHookModifier.invert_layer_pass_filter"></a>

#### bpy.types.GreasePencilHookModifier.invert_layer_pass_filter

Invert layer pass filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilHookModifier.invert_material_filter"></a>

#### bpy.types.GreasePencilHookModifier.invert_material_filter

Invert material filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilHookModifier.invert_material_pass_filter"></a>

#### bpy.types.GreasePencilHookModifier.invert_material_pass_filter

Invert material pass filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilHookModifier.invert_vertex_group"></a>

#### bpy.types.GreasePencilHookModifier.invert_vertex_group

Invert vertex group weights (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilHookModifier.layer_pass_filter"></a>

#### bpy.types.GreasePencilHookModifier.layer_pass_filter

Layer pass filter (in [0, 100], default 0)

**Type:**

int

<a id="bpy.types.GreasePencilHookModifier.material_filter"></a>

#### bpy.types.GreasePencilHookModifier.material_filter

Material used for filtering

**Type:**

[`Material`](bpy.types.Material.md#bpy.types.Material "bpy.types.Material") | None

<a id="bpy.types.GreasePencilHookModifier.material_pass_filter"></a>

#### bpy.types.GreasePencilHookModifier.material_pass_filter

Material pass (in [0, 100], default 0)

**Type:**

int

<a id="bpy.types.GreasePencilHookModifier.matrix_inverse"></a>

#### bpy.types.GreasePencilHookModifier.matrix_inverse

Reverse the transformation between this object and its target (multi-dimensional array of 4 * 4 items, in [-inf, inf], default ((1.0, 0.0, 0.0, 0.0), (0.0, 1.0, 0.0, 0.0), (0.0, 0.0, 1.0, 0.0), (0.0, 0.0, 0.0, 1.0)))

**Type:**

[`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")

<a id="bpy.types.GreasePencilHookModifier.object"></a>

#### bpy.types.GreasePencilHookModifier.object

Parent Object for hook, also recalculates and clears offset

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.GreasePencilHookModifier.open_falloff_panel"></a>

#### bpy.types.GreasePencilHookModifier.open_falloff_panel

(default False)

**Type:**

bool

<a id="bpy.types.GreasePencilHookModifier.open_influence_panel"></a>

#### bpy.types.GreasePencilHookModifier.open_influence_panel

(default False)

**Type:**

bool

<a id="bpy.types.GreasePencilHookModifier.strength"></a>

#### bpy.types.GreasePencilHookModifier.strength

Relative force of the hook (in [0, 1], default 0.5)

**Type:**

float

<a id="bpy.types.GreasePencilHookModifier.subtarget"></a>

#### bpy.types.GreasePencilHookModifier.subtarget

Name of Parent Bone for hook (if applicable), also recalculates and clears offset (default “”, never None)

**Type:**

str

<a id="bpy.types.GreasePencilHookModifier.tree_node_filter"></a>

#### bpy.types.GreasePencilHookModifier.tree_node_filter

Layer name (default “”, never None)

**Type:**

str

<a id="bpy.types.GreasePencilHookModifier.use_custom_curve"></a>

#### bpy.types.GreasePencilHookModifier.use_custom_curve

Use a custom curve to define a factor along the strokes (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilHookModifier.use_falloff_uniform"></a>

#### bpy.types.GreasePencilHookModifier.use_falloff_uniform

Compensate for non-uniform object scale (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilHookModifier.use_layer_group_filter"></a>

#### bpy.types.GreasePencilHookModifier.use_layer_group_filter

Filter by layer group name (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilHookModifier.use_layer_pass_filter"></a>

#### bpy.types.GreasePencilHookModifier.use_layer_pass_filter

Use layer pass filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilHookModifier.use_material_pass_filter"></a>

#### bpy.types.GreasePencilHookModifier.use_material_pass_filter

Use material pass filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilHookModifier.vertex_group_name"></a>

#### bpy.types.GreasePencilHookModifier.vertex_group_name

Vertex group name for modulating the deform (default “”, never None)

**Type:**

str

<a id="bpy.types.GreasePencilHookModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.GreasePencilHookModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.GreasePencilHookModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.GreasePencilHookModifier.bl_rna_get_subclass_py(id, default=None, /)

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
