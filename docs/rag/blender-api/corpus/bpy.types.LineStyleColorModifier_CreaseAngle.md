<!-- source: Blender Python API reference 5.2 / bpy.types.LineStyleColorModifier_CreaseAngle.html -->

<a id="linestylecolormodifier-creaseangle-linestylecolormodifier"></a>

# LineStyleColorModifier_CreaseAngle(LineStyleColorModifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`LineStyleModifier`](bpy.types.LineStyleModifier.md#bpy.types.LineStyleModifier "bpy.types.LineStyleModifier"), [`LineStyleColorModifier`](bpy.types.LineStyleColorModifier.md#bpy.types.LineStyleColorModifier "bpy.types.LineStyleColorModifier")

<a id="bpy.types.LineStyleColorModifier_CreaseAngle"></a>

### class bpy.types.LineStyleColorModifier_CreaseAngle(LineStyleColorModifier)

Change line color based on the underlying crease angle

<a id="bpy.types.LineStyleColorModifier_CreaseAngle.angle_max"></a>

#### bpy.types.LineStyleColorModifier_CreaseAngle.angle_max

Maximum angle to modify thickness (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.LineStyleColorModifier_CreaseAngle.angle_min"></a>

#### bpy.types.LineStyleColorModifier_CreaseAngle.angle_min

Minimum angle to modify thickness (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.LineStyleColorModifier_CreaseAngle.blend"></a>

#### bpy.types.LineStyleColorModifier_CreaseAngle.blend

Specify how the modifier value is blended into the base value (default `'MIX'`)

**Type:**

Literal[[Ramp Blend Items](bpy_types_enum_items/ramp_blend_items.md#rna-enum-ramp-blend-items)]

<a id="bpy.types.LineStyleColorModifier_CreaseAngle.color_ramp"></a>

#### bpy.types.LineStyleColorModifier_CreaseAngle.color_ramp

Color ramp used to change line color (readonly)

**Type:**

[`ColorRamp`](bpy.types.ColorRamp.md#bpy.types.ColorRamp "bpy.types.ColorRamp") | None

<a id="bpy.types.LineStyleColorModifier_CreaseAngle.expanded"></a>

#### bpy.types.LineStyleColorModifier_CreaseAngle.expanded

True if the modifier tab is expanded (default False)

**Type:**

bool

<a id="bpy.types.LineStyleColorModifier_CreaseAngle.influence"></a>

#### bpy.types.LineStyleColorModifier_CreaseAngle.influence

Influence factor by which the modifier changes the property (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.LineStyleColorModifier_CreaseAngle.type"></a>

#### bpy.types.LineStyleColorModifier_CreaseAngle.type

Type of the modifier (default `'ALONG_STROKE'`, readonly)

**Type:**

Literal[[Linestyle Color Modifier Type Items](bpy_types_enum_items/linestyle_color_modifier_type_items.md#rna-enum-linestyle-color-modifier-type-items)]

<a id="bpy.types.LineStyleColorModifier_CreaseAngle.use"></a>

#### bpy.types.LineStyleColorModifier_CreaseAngle.use

Enable or disable this modifier during stroke rendering (default False)

**Type:**

bool

<a id="bpy.types.LineStyleColorModifier_CreaseAngle.bl_rna_get_subclass"></a>

#### classmethod bpy.types.LineStyleColorModifier_CreaseAngle.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.LineStyleColorModifier_CreaseAngle.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.LineStyleColorModifier_CreaseAngle.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([type](#bpy.types.LineStyleColorModifier_CreaseAngle.type "bpy.types.LineStyleColorModifier_CreaseAngle.type") | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

[type](#bpy.types.LineStyleColorModifier_CreaseAngle.type "bpy.types.LineStyleColorModifier_CreaseAngle.type")

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, LineStyleColorModifier.name

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, LineStyleModifier.bl_rna_get_subclass, LineStyleModifier.bl_rna_get_subclass_py, LineStyleColorModifier.bl_rna_get_subclass, LineStyleColorModifier.bl_rna_get_subclass_py
