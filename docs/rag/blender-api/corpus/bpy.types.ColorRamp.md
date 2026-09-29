<!-- source: Blender Python API reference 5.2 / bpy.types.ColorRamp.html -->

<a id="colorramp-bpy-struct"></a>

# ColorRamp(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.ColorRamp"></a>

### class bpy.types.ColorRamp(bpy_struct)

Color ramp mapping a scalar value to a color

<a id="bpy.types.ColorRamp.color_mode"></a>

#### bpy.types.ColorRamp.color_mode

Set color mode to use for interpolation (default `'RGB'`)

**Type:**

Literal[‘RGB’, ‘HSV’, ‘HSL’]

<a id="bpy.types.ColorRamp.elements"></a>

#### bpy.types.ColorRamp.elements

(default None, readonly)

**Type:**

[`ColorRampElements`](bpy.types.ColorRampElements.md#bpy.types.ColorRampElements "bpy.types.ColorRampElements")[[`ColorRampElement`](bpy.types.ColorRampElement.md#bpy.types.ColorRampElement "bpy.types.ColorRampElement")]

<a id="bpy.types.ColorRamp.hue_interpolation"></a>

#### bpy.types.ColorRamp.hue_interpolation

Set color interpolation (default `'NEAR'`)

**Type:**

Literal[‘NEAR’, ‘FAR’, ‘CW’, ‘CCW’]

<a id="bpy.types.ColorRamp.interpolation"></a>

#### bpy.types.ColorRamp.interpolation

Set interpolation between color stops (default `'LINEAR'`)

**Type:**

Literal[‘EASE’, ‘CARDINAL’, ‘LINEAR’, ‘B_SPLINE’, ‘CONSTANT’]

<a id="bpy.types.ColorRamp.evaluate"></a>

#### bpy.types.ColorRamp.evaluate(position)

Evaluate Color Ramp

**Parameters:**

**position** (float) – Position, Evaluate Color Ramp at position (in [0, 1])

**Returns:**

Color, Color at given position (array of 4 items, in [-inf, inf])

**Return type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.ColorRamp.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ColorRamp.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ColorRamp.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ColorRamp.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

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
| - [`Brush.gradient`](bpy.types.Brush.md#bpy.types.Brush.gradient "bpy.types.Brush.gradient") - [`ColorMapping.color_ramp`](bpy.types.ColorMapping.md#bpy.types.ColorMapping.color_ramp "bpy.types.ColorMapping.color_ramp") - [`DynamicPaintBrushSettings.paint_ramp`](bpy.types.DynamicPaintBrushSettings.md#bpy.types.DynamicPaintBrushSettings.paint_ramp "bpy.types.DynamicPaintBrushSettings.paint_ramp") - [`DynamicPaintBrushSettings.velocity_ramp`](bpy.types.DynamicPaintBrushSettings.md#bpy.types.DynamicPaintBrushSettings.velocity_ramp "bpy.types.DynamicPaintBrushSettings.velocity_ramp") - [`FluidDomainSettings.color_ramp`](bpy.types.FluidDomainSettings.md#bpy.types.FluidDomainSettings.color_ramp "bpy.types.FluidDomainSettings.color_ramp") - [`GreasePencilTintModifier.color_ramp`](bpy.types.GreasePencilTintModifier.md#bpy.types.GreasePencilTintModifier.color_ramp "bpy.types.GreasePencilTintModifier.color_ramp") - [`LineStyleColorModifier_AlongStroke.color_ramp`](bpy.types.LineStyleColorModifier_AlongStroke.md#bpy.types.LineStyleColorModifier_AlongStroke.color_ramp "bpy.types.LineStyleColorModifier_AlongStroke.color_ramp") - [`LineStyleColorModifier_CreaseAngle.color_ramp`](bpy.types.LineStyleColorModifier_CreaseAngle.md#bpy.types.LineStyleColorModifier_CreaseAngle.color_ramp "bpy.types.LineStyleColorModifier_CreaseAngle.color_ramp") - [`LineStyleColorModifier_Curvature_3D.color_ramp`](bpy.types.LineStyleColorModifier_Curvature_3D.md#bpy.types.LineStyleColorModifier_Curvature_3D.color_ramp "bpy.types.LineStyleColorModifier_Curvature_3D.color_ramp") | - [`LineStyleColorModifier_DistanceFromCamera.color_ramp`](bpy.types.LineStyleColorModifier_DistanceFromCamera.md#bpy.types.LineStyleColorModifier_DistanceFromCamera.color_ramp "bpy.types.LineStyleColorModifier_DistanceFromCamera.color_ramp") - [`LineStyleColorModifier_DistanceFromObject.color_ramp`](bpy.types.LineStyleColorModifier_DistanceFromObject.md#bpy.types.LineStyleColorModifier_DistanceFromObject.color_ramp "bpy.types.LineStyleColorModifier_DistanceFromObject.color_ramp") - [`LineStyleColorModifier_Material.color_ramp`](bpy.types.LineStyleColorModifier_Material.md#bpy.types.LineStyleColorModifier_Material.color_ramp "bpy.types.LineStyleColorModifier_Material.color_ramp") - [`LineStyleColorModifier_Noise.color_ramp`](bpy.types.LineStyleColorModifier_Noise.md#bpy.types.LineStyleColorModifier_Noise.color_ramp "bpy.types.LineStyleColorModifier_Noise.color_ramp") - [`LineStyleColorModifier_Tangent.color_ramp`](bpy.types.LineStyleColorModifier_Tangent.md#bpy.types.LineStyleColorModifier_Tangent.color_ramp "bpy.types.LineStyleColorModifier_Tangent.color_ramp") - [`PreferencesView.weight_color_range`](bpy.types.PreferencesView.md#bpy.types.PreferencesView.weight_color_range "bpy.types.PreferencesView.weight_color_range") - [`ShaderNodeValToRGB.color_ramp`](bpy.types.ShaderNodeValToRGB.md#bpy.types.ShaderNodeValToRGB.color_ramp "bpy.types.ShaderNodeValToRGB.color_ramp") - [`Texture.color_ramp`](bpy.types.Texture.md#bpy.types.Texture.color_ramp "bpy.types.Texture.color_ramp") - [`TextureNodeValToRGB.color_ramp`](bpy.types.TextureNodeValToRGB.md#bpy.types.TextureNodeValToRGB.color_ramp "bpy.types.TextureNodeValToRGB.color_ramp") |
