<!-- source: Blender Python API reference 5.2 / bpy.types.ColorBalanceModifier.html -->

<a id="colorbalancemodifier-stripmodifier"></a>

# ColorBalanceModifier(StripModifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`StripModifier`](bpy.types.StripModifier.md#bpy.types.StripModifier "bpy.types.StripModifier")

<a id="bpy.types.ColorBalanceModifier"></a>

### class bpy.types.ColorBalanceModifier(StripModifier)

Color balance modifier for sequence strip

<a id="bpy.types.ColorBalanceModifier.color_balance"></a>

#### bpy.types.ColorBalanceModifier.color_balance

(readonly)

**Type:**

[`StripColorBalanceData`](bpy.types.StripColorBalanceData.md#bpy.types.StripColorBalanceData "bpy.types.StripColorBalanceData") | None

<a id="bpy.types.ColorBalanceModifier.color_multiply"></a>

#### bpy.types.ColorBalanceModifier.color_multiply

Multiply the intensity of each pixel (in [0, 20], default 1.0)

**Type:**

float

<a id="bpy.types.ColorBalanceModifier.open_mask_input_panel"></a>

#### bpy.types.ColorBalanceModifier.open_mask_input_panel

(default False)

**Type:**

bool

<a id="bpy.types.ColorBalanceModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ColorBalanceModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ColorBalanceModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ColorBalanceModifier.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, StripModifier.name, StripModifier.type, StripModifier.mute, StripModifier.enable, StripModifier.show_preview, StripModifier.show_expanded, StripModifier.input_mask_type, StripModifier.mask_time, StripModifier.input_mask_strip, StripModifier.input_mask_id, StripModifier.is_active

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, StripModifier.bl_rna_get_subclass, StripModifier.bl_rna_get_subclass_py
