<!-- source: Blender Python API reference 5.2 / bpy.types.GreasePencilArrayModifier.html -->

<a id="greasepencilarraymodifier-modifier"></a>

# GreasePencilArrayModifier(Modifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Modifier`](bpy.types.Modifier.md#bpy.types.Modifier "bpy.types.Modifier")

<a id="bpy.types.GreasePencilArrayModifier"></a>

### class bpy.types.GreasePencilArrayModifier(Modifier)

Create grid of duplicate instances

<a id="bpy.types.GreasePencilArrayModifier.constant_offset"></a>

#### bpy.types.GreasePencilArrayModifier.constant_offset

Value for the distance between items (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.GreasePencilArrayModifier.count"></a>

#### bpy.types.GreasePencilArrayModifier.count

Number of items (in [1, 32767], default 2)

**Type:**

int

<a id="bpy.types.GreasePencilArrayModifier.invert_layer_filter"></a>

#### bpy.types.GreasePencilArrayModifier.invert_layer_filter

Invert layer filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilArrayModifier.invert_layer_pass_filter"></a>

#### bpy.types.GreasePencilArrayModifier.invert_layer_pass_filter

Invert layer pass filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilArrayModifier.invert_material_filter"></a>

#### bpy.types.GreasePencilArrayModifier.invert_material_filter

Invert material filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilArrayModifier.invert_material_pass_filter"></a>

#### bpy.types.GreasePencilArrayModifier.invert_material_pass_filter

Invert material pass filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilArrayModifier.layer_pass_filter"></a>

#### bpy.types.GreasePencilArrayModifier.layer_pass_filter

Layer pass filter (in [0, 100], default 0)

**Type:**

int

<a id="bpy.types.GreasePencilArrayModifier.material_filter"></a>

#### bpy.types.GreasePencilArrayModifier.material_filter

Material used for filtering

**Type:**

[`Material`](bpy.types.Material.md#bpy.types.Material "bpy.types.Material") | None

<a id="bpy.types.GreasePencilArrayModifier.material_pass_filter"></a>

#### bpy.types.GreasePencilArrayModifier.material_pass_filter

Material pass (in [0, 100], default 0)

**Type:**

int

<a id="bpy.types.GreasePencilArrayModifier.offset_object"></a>

#### bpy.types.GreasePencilArrayModifier.offset_object

Use the location and rotation of another object to determine the distance and rotational change between arrayed items

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.GreasePencilArrayModifier.open_constant_offset_panel"></a>

#### bpy.types.GreasePencilArrayModifier.open_constant_offset_panel

(default False)

**Type:**

bool

<a id="bpy.types.GreasePencilArrayModifier.open_influence_panel"></a>

#### bpy.types.GreasePencilArrayModifier.open_influence_panel

(default False)

**Type:**

bool

<a id="bpy.types.GreasePencilArrayModifier.open_object_offset_panel"></a>

#### bpy.types.GreasePencilArrayModifier.open_object_offset_panel

(default False)

**Type:**

bool

<a id="bpy.types.GreasePencilArrayModifier.open_randomize_panel"></a>

#### bpy.types.GreasePencilArrayModifier.open_randomize_panel

(default False)

**Type:**

bool

<a id="bpy.types.GreasePencilArrayModifier.open_relative_offset_panel"></a>

#### bpy.types.GreasePencilArrayModifier.open_relative_offset_panel

(default False)

**Type:**

bool

<a id="bpy.types.GreasePencilArrayModifier.random_offset"></a>

#### bpy.types.GreasePencilArrayModifier.random_offset

Value for changes in location (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.GreasePencilArrayModifier.random_rotation"></a>

#### bpy.types.GreasePencilArrayModifier.random_rotation

Value for changes in rotation (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler")

<a id="bpy.types.GreasePencilArrayModifier.random_scale"></a>

#### bpy.types.GreasePencilArrayModifier.random_scale

Value for changes in scale (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.GreasePencilArrayModifier.relative_offset"></a>

#### bpy.types.GreasePencilArrayModifier.relative_offset

The size of the geometry will determine the distance between arrayed items (array of 3 items, in [-inf, inf], default (1.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.GreasePencilArrayModifier.replace_material"></a>

#### bpy.types.GreasePencilArrayModifier.replace_material

Index of the material used for generated strokes (0 keep original material) (in [0, 32767], default 0)

**Type:**

int

<a id="bpy.types.GreasePencilArrayModifier.seed"></a>

#### bpy.types.GreasePencilArrayModifier.seed

Random seed (in [0, inf], default 1)

**Type:**

int

<a id="bpy.types.GreasePencilArrayModifier.tree_node_filter"></a>

#### bpy.types.GreasePencilArrayModifier.tree_node_filter

Layer name (default “”, never None)

**Type:**

str

<a id="bpy.types.GreasePencilArrayModifier.use_constant_offset"></a>

#### bpy.types.GreasePencilArrayModifier.use_constant_offset

Enable offset (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilArrayModifier.use_layer_group_filter"></a>

#### bpy.types.GreasePencilArrayModifier.use_layer_group_filter

Filter by layer group name (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilArrayModifier.use_layer_pass_filter"></a>

#### bpy.types.GreasePencilArrayModifier.use_layer_pass_filter

Use layer pass filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilArrayModifier.use_material_pass_filter"></a>

#### bpy.types.GreasePencilArrayModifier.use_material_pass_filter

Use material pass filter (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilArrayModifier.use_object_offset"></a>

#### bpy.types.GreasePencilArrayModifier.use_object_offset

Add another object’s transformation to the total offset (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilArrayModifier.use_relative_offset"></a>

#### bpy.types.GreasePencilArrayModifier.use_relative_offset

Add an offset relative to the object’s bounding box (default True)

**Type:**

bool

<a id="bpy.types.GreasePencilArrayModifier.use_uniform_random_scale"></a>

#### bpy.types.GreasePencilArrayModifier.use_uniform_random_scale

Use the same random seed for each scale axis for a uniform scale (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilArrayModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.GreasePencilArrayModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.GreasePencilArrayModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.GreasePencilArrayModifier.bl_rna_get_subclass_py(id, default=None, /)

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
