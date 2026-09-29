<!-- source: Blender Python API reference 5.2 / bpy.types.FModifierEnvelope.html -->

<a id="fmodifierenvelope-fmodifier"></a>

# FModifierEnvelope(FModifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`FModifier`](bpy.types.FModifier.md#bpy.types.FModifier "bpy.types.FModifier")

<a id="bpy.types.FModifierEnvelope"></a>

### class bpy.types.FModifierEnvelope(FModifier)

Scale the values of the modified F-Curve

<a id="bpy.types.FModifierEnvelope.control_points"></a>

#### bpy.types.FModifierEnvelope.control_points

Control points defining the shape of the envelope (default None, readonly)

**Type:**

[`FModifierEnvelopeControlPoints`](bpy.types.FModifierEnvelopeControlPoints.md#bpy.types.FModifierEnvelopeControlPoints "bpy.types.FModifierEnvelopeControlPoints")[[`FModifierEnvelopeControlPoint`](bpy.types.FModifierEnvelopeControlPoint.md#bpy.types.FModifierEnvelopeControlPoint "bpy.types.FModifierEnvelopeControlPoint")]

<a id="bpy.types.FModifierEnvelope.default_max"></a>

#### bpy.types.FModifierEnvelope.default_max

Upper distance from Reference Value for 1:1 default influence (in [-inf, inf], default 1.0)

**Type:**

float

<a id="bpy.types.FModifierEnvelope.default_min"></a>

#### bpy.types.FModifierEnvelope.default_min

Lower distance from Reference Value for 1:1 default influence (in [-inf, inf], default -1.0)

**Type:**

float

<a id="bpy.types.FModifierEnvelope.reference_value"></a>

#### bpy.types.FModifierEnvelope.reference_value

Value that envelope’s influence is centered around / based on (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.FModifierEnvelope.bl_rna_get_subclass"></a>

#### classmethod bpy.types.FModifierEnvelope.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.FModifierEnvelope.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.FModifierEnvelope.bl_rna_get_subclass_py(id, default=None, /)

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
