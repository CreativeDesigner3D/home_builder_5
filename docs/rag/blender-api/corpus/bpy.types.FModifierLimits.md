<!-- source: Blender Python API reference 5.2 / bpy.types.FModifierLimits.html -->

<a id="fmodifierlimits-fmodifier"></a>

# FModifierLimits(FModifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`FModifier`](bpy.types.FModifier.md#bpy.types.FModifier "bpy.types.FModifier")

<a id="bpy.types.FModifierLimits"></a>

### class bpy.types.FModifierLimits(FModifier)

Limit the time/value ranges of the modified F-Curve

<a id="bpy.types.FModifierLimits.max_x"></a>

#### bpy.types.FModifierLimits.max_x

Highest X value to allow (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.FModifierLimits.max_y"></a>

#### bpy.types.FModifierLimits.max_y

Highest Y value to allow (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.FModifierLimits.min_x"></a>

#### bpy.types.FModifierLimits.min_x

Lowest X value to allow (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.FModifierLimits.min_y"></a>

#### bpy.types.FModifierLimits.min_y

Lowest Y value to allow (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.FModifierLimits.use_max_x"></a>

#### bpy.types.FModifierLimits.use_max_x

Use the maximum X value (default False)

**Type:**

bool

<a id="bpy.types.FModifierLimits.use_max_y"></a>

#### bpy.types.FModifierLimits.use_max_y

Use the maximum Y value (default False)

**Type:**

bool

<a id="bpy.types.FModifierLimits.use_min_x"></a>

#### bpy.types.FModifierLimits.use_min_x

Use the minimum X value (default False)

**Type:**

bool

<a id="bpy.types.FModifierLimits.use_min_y"></a>

#### bpy.types.FModifierLimits.use_min_y

Use the minimum Y value (default False)

**Type:**

bool

<a id="bpy.types.FModifierLimits.bl_rna_get_subclass"></a>

#### classmethod bpy.types.FModifierLimits.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.FModifierLimits.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.FModifierLimits.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, FModifier.name, FModifier.type, FModifier.show_expanded, FModifier.mute, FModifier.is_valid, FModifier.active, FModifier.use_restricted_range, FModifier.frame_start, FModifier.frame_end, FModifier.blend_in, FModifier.blend_out, FModifier.use_influence, FModifier.influence

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, FModifier.bl_rna_get_subclass, FModifier.bl_rna_get_subclass_py
