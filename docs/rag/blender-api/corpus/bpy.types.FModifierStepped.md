<!-- source: Blender Python API reference 5.2 / bpy.types.FModifierStepped.html -->

<a id="fmodifierstepped-fmodifier"></a>

# FModifierStepped(FModifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`FModifier`](bpy.types.FModifier.md#bpy.types.FModifier "bpy.types.FModifier")

<a id="bpy.types.FModifierStepped"></a>

### class bpy.types.FModifierStepped(FModifier)

Hold each interpolated value from the F-Curve for several frames without changing the timing

<a id="bpy.types.FModifierStepped.frame_end"></a>

#### bpy.types.FModifierStepped.frame_end

Frame that modifier’s influence ends (if applicable) (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.FModifierStepped.frame_offset"></a>

#### bpy.types.FModifierStepped.frame_offset

Reference number of frames before frames get held (use to get hold for ‘1-3’ vs ‘5-7’ holding patterns) (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.FModifierStepped.frame_start"></a>

#### bpy.types.FModifierStepped.frame_start

Frame that modifier’s influence starts (if applicable) (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.FModifierStepped.frame_step"></a>

#### bpy.types.FModifierStepped.frame_step

Number of frames to hold each value (in [-inf, inf], default 2.0)

**Type:**

float

<a id="bpy.types.FModifierStepped.use_frame_end"></a>

#### bpy.types.FModifierStepped.use_frame_end

Restrict modifier to only act before its ‘end’ frame (default False)

**Type:**

bool

<a id="bpy.types.FModifierStepped.use_frame_start"></a>

#### bpy.types.FModifierStepped.use_frame_start

Restrict modifier to only act after its ‘start’ frame (default False)

**Type:**

bool

<a id="bpy.types.FModifierStepped.bl_rna_get_subclass"></a>

#### classmethod bpy.types.FModifierStepped.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.FModifierStepped.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.FModifierStepped.bl_rna_get_subclass_py(id, default=None, /)

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
