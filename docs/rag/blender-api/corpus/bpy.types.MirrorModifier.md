<!-- source: Blender Python API reference 5.2 / bpy.types.MirrorModifier.html -->

<a id="mirrormodifier-modifier"></a>

# MirrorModifier(Modifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Modifier`](bpy.types.Modifier.md#bpy.types.Modifier "bpy.types.Modifier")

<a id="bpy.types.MirrorModifier"></a>

### class bpy.types.MirrorModifier(Modifier)

Mirroring modifier

<a id="bpy.types.MirrorModifier.bisect_threshold"></a>

#### bpy.types.MirrorModifier.bisect_threshold

Distance from the bisect plane within which vertices are removed (in [0, inf], default 0.001)

**Type:**

float

<a id="bpy.types.MirrorModifier.merge_threshold"></a>

#### bpy.types.MirrorModifier.merge_threshold

Distance within which mirrored vertices are merged (in [0, inf], default 0.001)

**Type:**

float

<a id="bpy.types.MirrorModifier.mirror_object"></a>

#### bpy.types.MirrorModifier.mirror_object

Object to use as mirror

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.MirrorModifier.mirror_offset_u"></a>

#### bpy.types.MirrorModifier.mirror_offset_u

Amount to offset mirrored UVs flipping point from the 0.5 on the U axis (in [-1, 1], default 0.0)

**Type:**

float

<a id="bpy.types.MirrorModifier.mirror_offset_v"></a>

#### bpy.types.MirrorModifier.mirror_offset_v

Amount to offset mirrored UVs flipping point from the 0.5 point on the V axis (in [-1, 1], default 0.0)

**Type:**

float

<a id="bpy.types.MirrorModifier.offset_u"></a>

#### bpy.types.MirrorModifier.offset_u

Mirrored UV offset on the U axis (in [-10000, 10000], default 0.0)

**Type:**

float

<a id="bpy.types.MirrorModifier.offset_v"></a>

#### bpy.types.MirrorModifier.offset_v

Mirrored UV offset on the V axis (in [-10000, 10000], default 0.0)

**Type:**

float

<a id="bpy.types.MirrorModifier.use_axis"></a>

#### bpy.types.MirrorModifier.use_axis

Enable axis mirror (array of 3 items, default (False, False, False))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[bool]

<a id="bpy.types.MirrorModifier.use_bisect_axis"></a>

#### bpy.types.MirrorModifier.use_bisect_axis

Cuts the mesh across the mirror plane (array of 3 items, default (False, False, False))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[bool]

<a id="bpy.types.MirrorModifier.use_bisect_flip_axis"></a>

#### bpy.types.MirrorModifier.use_bisect_flip_axis

Flips the direction of the slice (array of 3 items, default (False, False, False))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[bool]

<a id="bpy.types.MirrorModifier.use_clip"></a>

#### bpy.types.MirrorModifier.use_clip

Prevent vertices from going through the mirror during transform (default False)

**Type:**

bool

<a id="bpy.types.MirrorModifier.use_mirror_merge"></a>

#### bpy.types.MirrorModifier.use_mirror_merge

Merge vertices within the merge threshold (default True)

**Type:**

bool

<a id="bpy.types.MirrorModifier.use_mirror_u"></a>

#### bpy.types.MirrorModifier.use_mirror_u

Mirror the U texture coordinate around the flip offset point (default False)

**Type:**

bool

<a id="bpy.types.MirrorModifier.use_mirror_udim"></a>

#### bpy.types.MirrorModifier.use_mirror_udim

Mirror the texture coordinate around each tile center (default False)

**Type:**

bool

<a id="bpy.types.MirrorModifier.use_mirror_v"></a>

#### bpy.types.MirrorModifier.use_mirror_v

Mirror the V texture coordinate around the flip offset point (default False)

**Type:**

bool

<a id="bpy.types.MirrorModifier.use_mirror_vertex_groups"></a>

#### bpy.types.MirrorModifier.use_mirror_vertex_groups

Mirror vertex groups (e.g. .R->.L) (default True)

**Type:**

bool

<a id="bpy.types.MirrorModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.MirrorModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.MirrorModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.MirrorModifier.bl_rna_get_subclass_py(id, default=None, /)

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
