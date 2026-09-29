<!-- source: Blender Python API reference 5.2 / bpy.types.LineStyleThicknessModifier_CreaseAngle.html -->

<a id="linestylethicknessmodifier-creaseangle-linestylethicknessmodifier"></a>

# LineStyleThicknessModifier_CreaseAngle(LineStyleThicknessModifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`LineStyleModifier`](bpy.types.LineStyleModifier.md#bpy.types.LineStyleModifier "bpy.types.LineStyleModifier"), [`LineStyleThicknessModifier`](bpy.types.LineStyleThicknessModifier.md#bpy.types.LineStyleThicknessModifier "bpy.types.LineStyleThicknessModifier")

<a id="bpy.types.LineStyleThicknessModifier_CreaseAngle"></a>

### class bpy.types.LineStyleThicknessModifier_CreaseAngle(LineStyleThicknessModifier)

Line thickness based on the angle between two adjacent faces

<a id="bpy.types.LineStyleThicknessModifier_CreaseAngle.angle_max"></a>

#### bpy.types.LineStyleThicknessModifier_CreaseAngle.angle_max

Maximum angle to modify thickness (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.LineStyleThicknessModifier_CreaseAngle.angle_min"></a>

#### bpy.types.LineStyleThicknessModifier_CreaseAngle.angle_min

Minimum angle to modify thickness (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.LineStyleThicknessModifier_CreaseAngle.blend"></a>

#### bpy.types.LineStyleThicknessModifier_CreaseAngle.blend

Specify how the modifier value is blended into the base value (default `'MIX'`)

**Type:**

Literal[‘MIX’, ‘ADD’, ‘SUBTRACT’, ‘MULTIPLY’, ‘DIVIDE’, ‘DIFFERENCE’, ‘MINIMUM’, ‘MAXIMUM’]

<a id="bpy.types.LineStyleThicknessModifier_CreaseAngle.curve"></a>

#### bpy.types.LineStyleThicknessModifier_CreaseAngle.curve

Curve used for the curve mapping (readonly)

**Type:**

[`CurveMapping`](bpy.types.CurveMapping.md#bpy.types.CurveMapping "bpy.types.CurveMapping") | None

<a id="bpy.types.LineStyleThicknessModifier_CreaseAngle.expanded"></a>

#### bpy.types.LineStyleThicknessModifier_CreaseAngle.expanded

True if the modifier tab is expanded (default False)

**Type:**

bool

<a id="bpy.types.LineStyleThicknessModifier_CreaseAngle.influence"></a>

#### bpy.types.LineStyleThicknessModifier_CreaseAngle.influence

Influence factor by which the modifier changes the property (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.LineStyleThicknessModifier_CreaseAngle.invert"></a>

#### bpy.types.LineStyleThicknessModifier_CreaseAngle.invert

Invert the fade-out direction of the linear mapping (default False)

**Type:**

bool

<a id="bpy.types.LineStyleThicknessModifier_CreaseAngle.mapping"></a>

#### bpy.types.LineStyleThicknessModifier_CreaseAngle.mapping

Select the mapping type (default `'LINEAR'`)

- `LINEAR`
  Linear – Use linear mapping.
- `CURVE`
  Curve – Use curve mapping.

**Type:**

Literal[‘LINEAR’, ‘CURVE’]

<a id="bpy.types.LineStyleThicknessModifier_CreaseAngle.thickness_max"></a>

#### bpy.types.LineStyleThicknessModifier_CreaseAngle.thickness_max

Maximum thickness (in [0, 10000], default 0.0)

**Type:**

float

<a id="bpy.types.LineStyleThicknessModifier_CreaseAngle.thickness_min"></a>

#### bpy.types.LineStyleThicknessModifier_CreaseAngle.thickness_min

Minimum thickness (in [0, 10000], default 0.0)

**Type:**

float

<a id="bpy.types.LineStyleThicknessModifier_CreaseAngle.type"></a>

#### bpy.types.LineStyleThicknessModifier_CreaseAngle.type

Type of the modifier (default `'ALONG_STROKE'`, readonly)

**Type:**

Literal[[Linestyle Thickness Modifier Type Items](bpy_types_enum_items/linestyle_thickness_modifier_type_items.md#rna-enum-linestyle-thickness-modifier-type-items)]

<a id="bpy.types.LineStyleThicknessModifier_CreaseAngle.use"></a>

#### bpy.types.LineStyleThicknessModifier_CreaseAngle.use

Enable or disable this modifier during stroke rendering (default False)

**Type:**

bool

<a id="bpy.types.LineStyleThicknessModifier_CreaseAngle.bl_rna_get_subclass"></a>

#### classmethod bpy.types.LineStyleThicknessModifier_CreaseAngle.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.LineStyleThicknessModifier_CreaseAngle.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.LineStyleThicknessModifier_CreaseAngle.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([type](#bpy.types.LineStyleThicknessModifier_CreaseAngle.type "bpy.types.LineStyleThicknessModifier_CreaseAngle.type") | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

[type](#bpy.types.LineStyleThicknessModifier_CreaseAngle.type "bpy.types.LineStyleThicknessModifier_CreaseAngle.type")

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, LineStyleThicknessModifier.name

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, LineStyleModifier.bl_rna_get_subclass, LineStyleModifier.bl_rna_get_subclass_py, LineStyleThicknessModifier.bl_rna_get_subclass, LineStyleThicknessModifier.bl_rna_get_subclass_py
