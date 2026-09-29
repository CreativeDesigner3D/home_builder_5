<!-- source: Blender Python API reference 5.2 / bpy.types.FModifier.html -->

<a id="fmodifier-bpy-struct"></a>

# FModifier(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

Subclasses

- [FModifierCycles(FModifier)](bpy.types.FModifierCycles.md)
- [FModifierEnvelope(FModifier)](bpy.types.FModifierEnvelope.md)
- [FModifierFunctionGenerator(FModifier)](bpy.types.FModifierFunctionGenerator.md)
- [FModifierGenerator(FModifier)](bpy.types.FModifierGenerator.md)
- [FModifierLimits(FModifier)](bpy.types.FModifierLimits.md)
- [FModifierNoise(FModifier)](bpy.types.FModifierNoise.md)
- [FModifierSmooth(FModifier)](bpy.types.FModifierSmooth.md)
- [FModifierStepped(FModifier)](bpy.types.FModifierStepped.md)

<a id="bpy.types.FModifier"></a>

### class bpy.types.FModifier(bpy_struct)

Modifier for values of F-Curve

<a id="bpy.types.FModifier.active"></a>

#### bpy.types.FModifier.active

F-Curve modifier will show settings in the editor (default False)

**Type:**

bool

<a id="bpy.types.FModifier.blend_in"></a>

#### bpy.types.FModifier.blend_in

Number of frames from start frame for influence to take effect (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.FModifier.blend_out"></a>

#### bpy.types.FModifier.blend_out

Number of frames from end frame for influence to fade out (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.FModifier.frame_end"></a>

#### bpy.types.FModifier.frame_end

Frame that modifier’s influence ends (if Restrict Frame Range is in use) (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.FModifier.frame_start"></a>

#### bpy.types.FModifier.frame_start

Frame that modifier’s influence starts (if Restrict Frame Range is in use) (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.FModifier.influence"></a>

#### bpy.types.FModifier.influence

Amount of influence F-Curve Modifier will have when not fading in/out (in [0, 1], default 1.0)

**Type:**

float

<a id="bpy.types.FModifier.is_valid"></a>

#### bpy.types.FModifier.is_valid

F-Curve Modifier has invalid settings and will not be evaluated (default True, readonly)

**Type:**

bool

<a id="bpy.types.FModifier.mute"></a>

#### bpy.types.FModifier.mute

Enable F-Curve modifier evaluation (default False)

**Type:**

bool

<a id="bpy.types.FModifier.name"></a>

#### bpy.types.FModifier.name

F-Curve Modifier name (default “”, never None)

**Type:**

str

<a id="bpy.types.FModifier.show_expanded"></a>

#### bpy.types.FModifier.show_expanded

F-Curve Modifier’s panel is expanded in UI (default False)

**Type:**

bool

<a id="bpy.types.FModifier.type"></a>

#### bpy.types.FModifier.type

F-Curve Modifier Type (default `'NULL'`, readonly)

**Type:**

Literal[[Fmodifier Type Items](bpy_types_enum_items/fmodifier_type_items.md#rna-enum-fmodifier-type-items)]

<a id="bpy.types.FModifier.use_influence"></a>

#### bpy.types.FModifier.use_influence

F-Curve Modifier’s effects will be tempered by a default factor (default False)

**Type:**

bool

<a id="bpy.types.FModifier.use_restricted_range"></a>

#### bpy.types.FModifier.use_restricted_range

F-Curve Modifier is only applied for the specified frame range to help mask off effects in order to chain them (default False)

**Type:**

bool

<a id="bpy.types.FModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.FModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.FModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.FModifier.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([type](#bpy.types.FModifier.type "bpy.types.FModifier.type") | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

[type](#bpy.types.FModifier.type "bpy.types.FModifier.type")

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values

<a id="references"></a>

## References

|  |  |
| --- | --- |
| - [`FCurve.modifiers`](bpy.types.FCurve.md#bpy.types.FCurve.modifiers "bpy.types.FCurve.modifiers") - [`FCurveModifiers.active`](bpy.types.FCurveModifiers.md#bpy.types.FCurveModifiers.active "bpy.types.FCurveModifiers.active") - [`FCurveModifiers.new`](bpy.types.FCurveModifiers.md#bpy.types.FCurveModifiers.new "bpy.types.FCurveModifiers.new") | - [`FCurveModifiers.remove`](bpy.types.FCurveModifiers.md#bpy.types.FCurveModifiers.remove "bpy.types.FCurveModifiers.remove") - [`NlaStrip.modifiers`](bpy.types.NlaStrip.md#bpy.types.NlaStrip.modifiers "bpy.types.NlaStrip.modifiers") |
