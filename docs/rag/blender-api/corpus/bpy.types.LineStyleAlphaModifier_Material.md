<!-- source: Blender Python API reference 5.2 / bpy.types.LineStyleAlphaModifier_Material.html -->

<a id="linestylealphamodifier-material-linestylealphamodifier"></a>

# LineStyleAlphaModifier_Material(LineStyleAlphaModifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`LineStyleModifier`](bpy.types.LineStyleModifier.md#bpy.types.LineStyleModifier "bpy.types.LineStyleModifier"), [`LineStyleAlphaModifier`](bpy.types.LineStyleAlphaModifier.md#bpy.types.LineStyleAlphaModifier "bpy.types.LineStyleAlphaModifier")

<a id="bpy.types.LineStyleAlphaModifier_Material"></a>

### class bpy.types.LineStyleAlphaModifier_Material(LineStyleAlphaModifier)

Change alpha transparency based on a material attribute

<a id="bpy.types.LineStyleAlphaModifier_Material.blend"></a>

#### bpy.types.LineStyleAlphaModifier_Material.blend

Specify how the modifier value is blended into the base value (default `'MIX'`)

**Type:**

Literal[‘MIX’, ‘ADD’, ‘SUBTRACT’, ‘MULTIPLY’, ‘DIVIDE’, ‘DIFFERENCE’, ‘MINIMUM’, ‘MAXIMUM’]

<a id="bpy.types.LineStyleAlphaModifier_Material.curve"></a>

#### bpy.types.LineStyleAlphaModifier_Material.curve

Curve used for the curve mapping (readonly)

**Type:**

[`CurveMapping`](bpy.types.CurveMapping.md#bpy.types.CurveMapping "bpy.types.CurveMapping") | None

<a id="bpy.types.LineStyleAlphaModifier_Material.expanded"></a>

#### bpy.types.LineStyleAlphaModifier_Material.expanded

True if the modifier tab is expanded (default False)

**Type:**

bool

<a id="bpy.types.LineStyleAlphaModifier_Material.influence"></a>

#### bpy.types.LineStyleAlphaModifier_Material.influence

Influence factor by which the modifier changes the property (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.LineStyleAlphaModifier_Material.invert"></a>

#### bpy.types.LineStyleAlphaModifier_Material.invert

Invert the fade-out direction of the linear mapping (default False)

**Type:**

bool

<a id="bpy.types.LineStyleAlphaModifier_Material.mapping"></a>

#### bpy.types.LineStyleAlphaModifier_Material.mapping

Select the mapping type (default `'LINEAR'`)

- `LINEAR`
  Linear – Use linear mapping.
- `CURVE`
  Curve – Use curve mapping.

**Type:**

Literal[‘LINEAR’, ‘CURVE’]

<a id="bpy.types.LineStyleAlphaModifier_Material.material_attribute"></a>

#### bpy.types.LineStyleAlphaModifier_Material.material_attribute

Specify which material attribute is used (default `'LINE'`)

**Type:**

Literal[‘LINE’, ‘LINE_R’, ‘LINE_G’, ‘LINE_B’, ‘LINE_A’, ‘DIFF’, ‘DIFF_R’, ‘DIFF_G’, ‘DIFF_B’, ‘SPEC’, ‘SPEC_R’, ‘SPEC_G’, ‘SPEC_B’, ‘SPEC_HARD’, ‘ALPHA’]

<a id="bpy.types.LineStyleAlphaModifier_Material.type"></a>

#### bpy.types.LineStyleAlphaModifier_Material.type

Type of the modifier (default `'ALONG_STROKE'`, readonly)

**Type:**

Literal[[Linestyle Alpha Modifier Type Items](bpy_types_enum_items/linestyle_alpha_modifier_type_items.md#rna-enum-linestyle-alpha-modifier-type-items)]

<a id="bpy.types.LineStyleAlphaModifier_Material.use"></a>

#### bpy.types.LineStyleAlphaModifier_Material.use

Enable or disable this modifier during stroke rendering (default False)

**Type:**

bool

<a id="bpy.types.LineStyleAlphaModifier_Material.bl_rna_get_subclass"></a>

#### classmethod bpy.types.LineStyleAlphaModifier_Material.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.LineStyleAlphaModifier_Material.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.LineStyleAlphaModifier_Material.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([type](#bpy.types.LineStyleAlphaModifier_Material.type "bpy.types.LineStyleAlphaModifier_Material.type") | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

[type](#bpy.types.LineStyleAlphaModifier_Material.type "bpy.types.LineStyleAlphaModifier_Material.type")

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, LineStyleAlphaModifier.name

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, LineStyleModifier.bl_rna_get_subclass, LineStyleModifier.bl_rna_get_subclass_py, LineStyleAlphaModifier.bl_rna_get_subclass, LineStyleAlphaModifier.bl_rna_get_subclass_py
