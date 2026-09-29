<!-- source: Blender Python API reference 5.2 / bpy.types.HookModifier.html -->

<a id="hookmodifier-modifier"></a>

# HookModifier(Modifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Modifier`](bpy.types.Modifier.md#bpy.types.Modifier "bpy.types.Modifier")

<a id="bpy.types.HookModifier"></a>

### class bpy.types.HookModifier(Modifier)

Hook modifier to modify the location of vertices

<a id="bpy.types.HookModifier.center"></a>

#### bpy.types.HookModifier.center

Center of the hook, used for falloff and display (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.HookModifier.falloff_curve"></a>

#### bpy.types.HookModifier.falloff_curve

Custom falloff curve (readonly)

**Type:**

[`CurveMapping`](bpy.types.CurveMapping.md#bpy.types.CurveMapping "bpy.types.CurveMapping") | None

<a id="bpy.types.HookModifier.falloff_radius"></a>

#### bpy.types.HookModifier.falloff_radius

If not zero, the distance from the hook where influence ends (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.HookModifier.falloff_type"></a>

#### bpy.types.HookModifier.falloff_type

(default `'SMOOTH'`)

**Type:**

Literal[‘NONE’, ‘CURVE’, ‘SMOOTH’, ‘SPHERE’, ‘ROOT’, ‘INVERSE_SQUARE’, ‘SHARP’, ‘LINEAR’, ‘CONSTANT’]

<a id="bpy.types.HookModifier.invert_vertex_group"></a>

#### bpy.types.HookModifier.invert_vertex_group

Invert vertex group influence (default False)

**Type:**

bool

<a id="bpy.types.HookModifier.matrix_inverse"></a>

#### bpy.types.HookModifier.matrix_inverse

Reverse the transformation between this object and its target (multi-dimensional array of 4 * 4 items, in [-inf, inf], default ((1.0, 0.0, 0.0, 0.0), (0.0, 1.0, 0.0, 0.0), (0.0, 0.0, 1.0, 0.0), (0.0, 0.0, 0.0, 1.0)))

**Type:**

[`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")

<a id="bpy.types.HookModifier.object"></a>

#### bpy.types.HookModifier.object

Parent Object for hook, also recalculates and clears offset

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.HookModifier.strength"></a>

#### bpy.types.HookModifier.strength

Relative force of the hook (in [0, 1], default 1.0)

**Type:**

float

<a id="bpy.types.HookModifier.subtarget"></a>

#### bpy.types.HookModifier.subtarget

Name of Parent Bone for hook (if applicable), also recalculates and clears offset (default “”, never None)

**Type:**

str

<a id="bpy.types.HookModifier.use_falloff_uniform"></a>

#### bpy.types.HookModifier.use_falloff_uniform

Compensate for non-uniform object scale (default False)

**Type:**

bool

<a id="bpy.types.HookModifier.vertex_group"></a>

#### bpy.types.HookModifier.vertex_group

Name of Vertex Group which determines influence of modifier per point (default “”, never None)

**Type:**

str

<a id="bpy.types.HookModifier.vertex_indices"></a>

#### bpy.types.HookModifier.vertex_indices

Indices of vertices bound to the modifier. For Bézier curves, handles count as additional vertices. (array of 64 items, in [0, inf], default (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0), readonly)

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[int]

<a id="bpy.types.HookModifier.vertex_indices_set"></a>

#### bpy.types.HookModifier.vertex_indices_set(indices)

Validates and assigns the array of vertex indices bound to the modifier

**Parameters:**

**indices** (Sequence[int]) – Vertex Indices (array of 64 items, in [-inf, inf])

<a id="bpy.types.HookModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.HookModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.HookModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.HookModifier.bl_rna_get_subclass_py(id, default=None, /)

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
