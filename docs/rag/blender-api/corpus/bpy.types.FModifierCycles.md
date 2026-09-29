<!-- source: Blender Python API reference 5.2 / bpy.types.FModifierCycles.html -->

<a id="fmodifiercycles-fmodifier"></a>

# FModifierCycles(FModifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`FModifier`](bpy.types.FModifier.md#bpy.types.FModifier "bpy.types.FModifier")

<a id="bpy.types.FModifierCycles"></a>

### class bpy.types.FModifierCycles(FModifier)

Repeat the values of the modified F-Curve

<a id="bpy.types.FModifierCycles.cycles_after"></a>

#### bpy.types.FModifierCycles.cycles_after

Maximum number of cycles to allow after last keyframe (0 = infinite) (in [-32768, 32767], default 0)

**Type:**

int

<a id="bpy.types.FModifierCycles.cycles_before"></a>

#### bpy.types.FModifierCycles.cycles_before

Maximum number of cycles to allow before first keyframe (0 = infinite) (in [-32768, 32767], default 0)

**Type:**

int

<a id="bpy.types.FModifierCycles.mode_after"></a>

#### bpy.types.FModifierCycles.mode_after

Cycling mode to use after last keyframe (default `'NONE'`)

- `NONE`
  No Cycles – Don’t do anything.
- `REPEAT`
  Repeat Motion – Repeat keyframe range as-is.
- `REPEAT_OFFSET`
  Repeat with Offset – Repeat keyframe range, but with offset based on gradient between start and end values.
- `MIRROR`
  Repeat Mirrored – Alternate between forward and reverse playback of keyframe range.

**Type:**

Literal[‘NONE’, ‘REPEAT’, ‘REPEAT_OFFSET’, ‘MIRROR’]

<a id="bpy.types.FModifierCycles.mode_before"></a>

#### bpy.types.FModifierCycles.mode_before

Cycling mode to use before first keyframe (default `'NONE'`)

- `NONE`
  No Cycles – Don’t do anything.
- `REPEAT`
  Repeat Motion – Repeat keyframe range as-is.
- `REPEAT_OFFSET`
  Repeat with Offset – Repeat keyframe range, but with offset based on gradient between start and end values.
- `MIRROR`
  Repeat Mirrored – Alternate between forward and reverse playback of keyframe range.

**Type:**

Literal[‘NONE’, ‘REPEAT’, ‘REPEAT_OFFSET’, ‘MIRROR’]

<a id="bpy.types.FModifierCycles.bl_rna_get_subclass"></a>

#### classmethod bpy.types.FModifierCycles.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.FModifierCycles.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.FModifierCycles.bl_rna_get_subclass_py(id, default=None, /)

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
