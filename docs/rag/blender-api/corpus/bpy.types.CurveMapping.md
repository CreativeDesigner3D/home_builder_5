<!-- source: Blender Python API reference 5.2 / bpy.types.CurveMapping.html -->

<a id="curvemapping-bpy-struct"></a>

# CurveMapping(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.CurveMapping"></a>

### class bpy.types.CurveMapping(bpy_struct)

Curve mapping to map color, vector and scalar values to other values using a user defined curve

<a id="bpy.types.CurveMapping.black_level"></a>

#### bpy.types.CurveMapping.black_level

For RGB curves, the color that black is mapped to (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.CurveMapping.clip_max_x"></a>

#### bpy.types.CurveMapping.clip_max_x

(in [-100, 100], default 0.0)

**Type:**

float

<a id="bpy.types.CurveMapping.clip_max_y"></a>

#### bpy.types.CurveMapping.clip_max_y

(in [-100, 100], default 0.0)

**Type:**

float

<a id="bpy.types.CurveMapping.clip_min_x"></a>

#### bpy.types.CurveMapping.clip_min_x

(in [-100, 100], default 0.0)

**Type:**

float

<a id="bpy.types.CurveMapping.clip_min_y"></a>

#### bpy.types.CurveMapping.clip_min_y

(in [-100, 100], default 0.0)

**Type:**

float

<a id="bpy.types.CurveMapping.curves"></a>

#### bpy.types.CurveMapping.curves

(default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`CurveMap`](bpy.types.CurveMap.md#bpy.types.CurveMap "bpy.types.CurveMap")]

<a id="bpy.types.CurveMapping.extend"></a>

#### bpy.types.CurveMapping.extend

Extrapolate the curve or extend it horizontally (default `'HORIZONTAL'`)

**Type:**

Literal[‘HORIZONTAL’, ‘EXTRAPOLATED’]

<a id="bpy.types.CurveMapping.tone"></a>

#### bpy.types.CurveMapping.tone

Tone of the curve (default `'STANDARD'`)

- `STANDARD`
  Standard – Combined curve is applied to each channel individually, which may result in a change of hue.
- `FILMLIKE`
  Filmlike – Keeps the hue constant.

**Type:**

Literal[‘STANDARD’, ‘FILMLIKE’]

<a id="bpy.types.CurveMapping.use_clip"></a>

#### bpy.types.CurveMapping.use_clip

Force the curve view to fit a defined boundary (default False)

**Type:**

bool

<a id="bpy.types.CurveMapping.white_level"></a>

#### bpy.types.CurveMapping.white_level

For RGB curves, the color that white is mapped to (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.CurveMapping.update"></a>

#### bpy.types.CurveMapping.update()

Update curve mapping after making changes

<a id="bpy.types.CurveMapping.reset_view"></a>

#### bpy.types.CurveMapping.reset_view()

Reset the curve mapping grid to its clipping size

<a id="bpy.types.CurveMapping.initialize"></a>

#### bpy.types.CurveMapping.initialize()

Initialize curve

<a id="bpy.types.CurveMapping.evaluate"></a>

#### bpy.types.CurveMapping.evaluate(curve, position)

Evaluate curve at given location

**Parameters:**

- **curve** ([`CurveMap`](bpy.types.CurveMap.md#bpy.types.CurveMap "bpy.types.CurveMap") | None) – curve, Curve to evaluate (never None)
- **position** (float) – Position, Position to evaluate curve at (in [-inf, inf])

**Returns:**

Value, Value of curve at given location (in [-inf, inf])

**Return type:**

float

<a id="bpy.types.CurveMapping.bl_rna_get_subclass"></a>

#### classmethod bpy.types.CurveMapping.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.CurveMapping.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.CurveMapping.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Brush.curve_distance_falloff`](bpy.types.Brush.md#bpy.types.Brush.curve_distance_falloff "bpy.types.Brush.curve_distance_falloff") - [`Brush.curve_jitter`](bpy.types.Brush.md#bpy.types.Brush.curve_jitter "bpy.types.Brush.curve_jitter") - [`Brush.curve_random_hue`](bpy.types.Brush.md#bpy.types.Brush.curve_random_hue "bpy.types.Brush.curve_random_hue") - [`Brush.curve_random_saturation`](bpy.types.Brush.md#bpy.types.Brush.curve_random_saturation "bpy.types.Brush.curve_random_saturation") - [`Brush.curve_random_value`](bpy.types.Brush.md#bpy.types.Brush.curve_random_value "bpy.types.Brush.curve_random_value") - [`Brush.curve_size`](bpy.types.Brush.md#bpy.types.Brush.curve_size "bpy.types.Brush.curve_size") - [`Brush.curve_strength`](bpy.types.Brush.md#bpy.types.Brush.curve_strength "bpy.types.Brush.curve_strength") - [`BrushCurvesSculptSettings.curve_parameter_falloff`](bpy.types.BrushCurvesSculptSettings.md#bpy.types.BrushCurvesSculptSettings.curve_parameter_falloff "bpy.types.BrushCurvesSculptSettings.curve_parameter_falloff") - [`BrushGpencilSettings.curve_jitter`](bpy.types.BrushGpencilSettings.md#bpy.types.BrushGpencilSettings.curve_jitter "bpy.types.BrushGpencilSettings.curve_jitter") - [`BrushGpencilSettings.curve_random_hue`](bpy.types.BrushGpencilSettings.md#bpy.types.BrushGpencilSettings.curve_random_hue "bpy.types.BrushGpencilSettings.curve_random_hue") - [`BrushGpencilSettings.curve_random_pressure`](bpy.types.BrushGpencilSettings.md#bpy.types.BrushGpencilSettings.curve_random_pressure "bpy.types.BrushGpencilSettings.curve_random_pressure") - [`BrushGpencilSettings.curve_random_saturation`](bpy.types.BrushGpencilSettings.md#bpy.types.BrushGpencilSettings.curve_random_saturation "bpy.types.BrushGpencilSettings.curve_random_saturation") - [`BrushGpencilSettings.curve_random_strength`](bpy.types.BrushGpencilSettings.md#bpy.types.BrushGpencilSettings.curve_random_strength "bpy.types.BrushGpencilSettings.curve_random_strength") - [`BrushGpencilSettings.curve_random_uv`](bpy.types.BrushGpencilSettings.md#bpy.types.BrushGpencilSettings.curve_random_uv "bpy.types.BrushGpencilSettings.curve_random_uv") - [`BrushGpencilSettings.curve_random_value`](bpy.types.BrushGpencilSettings.md#bpy.types.BrushGpencilSettings.curve_random_value "bpy.types.BrushGpencilSettings.curve_random_value") - [`BrushGpencilSettings.curve_sensitivity`](bpy.types.BrushGpencilSettings.md#bpy.types.BrushGpencilSettings.curve_sensitivity "bpy.types.BrushGpencilSettings.curve_sensitivity") - [`BrushGpencilSettings.curve_strength`](bpy.types.BrushGpencilSettings.md#bpy.types.BrushGpencilSettings.curve_strength "bpy.types.BrushGpencilSettings.curve_strength") - [`ColorManagedViewSettings.curve_mapping`](bpy.types.ColorManagedViewSettings.md#bpy.types.ColorManagedViewSettings.curve_mapping "bpy.types.ColorManagedViewSettings.curve_mapping") - [`CompositorNodeCurveRGB.mapping`](bpy.types.CompositorNodeCurveRGB.md#bpy.types.CompositorNodeCurveRGB.mapping "bpy.types.CompositorNodeCurveRGB.mapping") - [`CompositorNodeHueCorrect.mapping`](bpy.types.CompositorNodeHueCorrect.md#bpy.types.CompositorNodeHueCorrect.mapping "bpy.types.CompositorNodeHueCorrect.mapping") - [`CompositorNodeTime.curve`](bpy.types.CompositorNodeTime.md#bpy.types.CompositorNodeTime.curve "bpy.types.CompositorNodeTime.curve") - [`CurvesModifier.curve_mapping`](bpy.types.CurvesModifier.md#bpy.types.CurvesModifier.curve_mapping "bpy.types.CurvesModifier.curve_mapping") - [`EQCurveMappingData.curve_mapping`](bpy.types.EQCurveMappingData.md#bpy.types.EQCurveMappingData.curve_mapping "bpy.types.EQCurveMappingData.curve_mapping") - [`GPencilInterpolateSettings.interpolation_curve`](bpy.types.GPencilInterpolateSettings.md#bpy.types.GPencilInterpolateSettings.interpolation_curve "bpy.types.GPencilInterpolateSettings.interpolation_curve") - [`GPencilSculptSettings.multiframe_falloff_curve`](bpy.types.GPencilSculptSettings.md#bpy.types.GPencilSculptSettings.multiframe_falloff_curve "bpy.types.GPencilSculptSettings.multiframe_falloff_curve") - [`GPencilSculptSettings.thickness_primitive_curve`](bpy.types.GPencilSculptSettings.md#bpy.types.GPencilSculptSettings.thickness_primitive_curve "bpy.types.GPencilSculptSettings.thickness_primitive_curve") - [`GreasePencilColorModifier.custom_curve`](bpy.types.GreasePencilColorModifier.md#bpy.types.GreasePencilColorModifier.custom_curve "bpy.types.GreasePencilColorModifier.custom_curve") - [`GreasePencilHookModifier.custom_curve`](bpy.types.GreasePencilHookModifier.md#bpy.types.GreasePencilHookModifier.custom_curve "bpy.types.GreasePencilHookModifier.custom_curve") - [`GreasePencilNoiseModifier.custom_curve`](bpy.types.GreasePencilNoiseModifier.md#bpy.types.GreasePencilNoiseModifier.custom_curve "bpy.types.GreasePencilNoiseModifier.custom_curve") - [`GreasePencilOpacityModifier.custom_curve`](bpy.types.GreasePencilOpacityModifier.md#bpy.types.GreasePencilOpacityModifier.custom_curve "bpy.types.GreasePencilOpacityModifier.custom_curve") - [`GreasePencilSmoothModifier.custom_curve`](bpy.types.GreasePencilSmoothModifier.md#bpy.types.GreasePencilSmoothModifier.custom_curve "bpy.types.GreasePencilSmoothModifier.custom_curve") - [`GreasePencilThickModifierData.custom_curve`](bpy.types.GreasePencilThickModifierData.md#bpy.types.GreasePencilThickModifierData.custom_curve "bpy.types.GreasePencilThickModifierData.custom_curve") - [`GreasePencilTintModifier.custom_curve`](bpy.types.GreasePencilTintModifier.md#bpy.types.GreasePencilTintModifier.custom_curve "bpy.types.GreasePencilTintModifier.custom_curve") - [`HookModifier.falloff_curve`](bpy.types.HookModifier.md#bpy.types.HookModifier.falloff_curve "bpy.types.HookModifier.falloff_curve") | - [`HueCorrectModifier.curve_mapping`](bpy.types.HueCorrectModifier.md#bpy.types.HueCorrectModifier.curve_mapping "bpy.types.HueCorrectModifier.curve_mapping") - [`LineStyleAlphaModifier_AlongStroke.curve`](bpy.types.LineStyleAlphaModifier_AlongStroke.md#bpy.types.LineStyleAlphaModifier_AlongStroke.curve "bpy.types.LineStyleAlphaModifier_AlongStroke.curve") - [`LineStyleAlphaModifier_CreaseAngle.curve`](bpy.types.LineStyleAlphaModifier_CreaseAngle.md#bpy.types.LineStyleAlphaModifier_CreaseAngle.curve "bpy.types.LineStyleAlphaModifier_CreaseAngle.curve") - [`LineStyleAlphaModifier_Curvature_3D.curve`](bpy.types.LineStyleAlphaModifier_Curvature_3D.md#bpy.types.LineStyleAlphaModifier_Curvature_3D.curve "bpy.types.LineStyleAlphaModifier_Curvature_3D.curve") - [`LineStyleAlphaModifier_DistanceFromCamera.curve`](bpy.types.LineStyleAlphaModifier_DistanceFromCamera.md#bpy.types.LineStyleAlphaModifier_DistanceFromCamera.curve "bpy.types.LineStyleAlphaModifier_DistanceFromCamera.curve") - [`LineStyleAlphaModifier_DistanceFromObject.curve`](bpy.types.LineStyleAlphaModifier_DistanceFromObject.md#bpy.types.LineStyleAlphaModifier_DistanceFromObject.curve "bpy.types.LineStyleAlphaModifier_DistanceFromObject.curve") - [`LineStyleAlphaModifier_Material.curve`](bpy.types.LineStyleAlphaModifier_Material.md#bpy.types.LineStyleAlphaModifier_Material.curve "bpy.types.LineStyleAlphaModifier_Material.curve") - [`LineStyleAlphaModifier_Noise.curve`](bpy.types.LineStyleAlphaModifier_Noise.md#bpy.types.LineStyleAlphaModifier_Noise.curve "bpy.types.LineStyleAlphaModifier_Noise.curve") - [`LineStyleAlphaModifier_Tangent.curve`](bpy.types.LineStyleAlphaModifier_Tangent.md#bpy.types.LineStyleAlphaModifier_Tangent.curve "bpy.types.LineStyleAlphaModifier_Tangent.curve") - [`LineStyleThicknessModifier_AlongStroke.curve`](bpy.types.LineStyleThicknessModifier_AlongStroke.md#bpy.types.LineStyleThicknessModifier_AlongStroke.curve "bpy.types.LineStyleThicknessModifier_AlongStroke.curve") - [`LineStyleThicknessModifier_CreaseAngle.curve`](bpy.types.LineStyleThicknessModifier_CreaseAngle.md#bpy.types.LineStyleThicknessModifier_CreaseAngle.curve "bpy.types.LineStyleThicknessModifier_CreaseAngle.curve") - [`LineStyleThicknessModifier_Curvature_3D.curve`](bpy.types.LineStyleThicknessModifier_Curvature_3D.md#bpy.types.LineStyleThicknessModifier_Curvature_3D.curve "bpy.types.LineStyleThicknessModifier_Curvature_3D.curve") - [`LineStyleThicknessModifier_DistanceFromCamera.curve`](bpy.types.LineStyleThicknessModifier_DistanceFromCamera.md#bpy.types.LineStyleThicknessModifier_DistanceFromCamera.curve "bpy.types.LineStyleThicknessModifier_DistanceFromCamera.curve") - [`LineStyleThicknessModifier_DistanceFromObject.curve`](bpy.types.LineStyleThicknessModifier_DistanceFromObject.md#bpy.types.LineStyleThicknessModifier_DistanceFromObject.curve "bpy.types.LineStyleThicknessModifier_DistanceFromObject.curve") - [`LineStyleThicknessModifier_Material.curve`](bpy.types.LineStyleThicknessModifier_Material.md#bpy.types.LineStyleThicknessModifier_Material.curve "bpy.types.LineStyleThicknessModifier_Material.curve") - [`LineStyleThicknessModifier_Tangent.curve`](bpy.types.LineStyleThicknessModifier_Tangent.md#bpy.types.LineStyleThicknessModifier_Tangent.curve "bpy.types.LineStyleThicknessModifier_Tangent.curve") - [`MeshAutomaskingSettings.cavity_curve`](bpy.types.MeshAutomaskingSettings.md#bpy.types.MeshAutomaskingSettings.cavity_curve "bpy.types.MeshAutomaskingSettings.cavity_curve") - [`MeshAutomaskingSettings.cavity_curve_op`](bpy.types.MeshAutomaskingSettings.md#bpy.types.MeshAutomaskingSettings.cavity_curve_op "bpy.types.MeshAutomaskingSettings.cavity_curve_op") - [`Paint.cavity_curve`](bpy.types.Paint.md#bpy.types.Paint.cavity_curve "bpy.types.Paint.cavity_curve") - [`ParticleBrush.curve`](bpy.types.ParticleBrush.md#bpy.types.ParticleBrush.curve "bpy.types.ParticleBrush.curve") - [`ParticleSettings.clump_curve`](bpy.types.ParticleSettings.md#bpy.types.ParticleSettings.clump_curve "bpy.types.ParticleSettings.clump_curve") - [`ParticleSettings.roughness_curve`](bpy.types.ParticleSettings.md#bpy.types.ParticleSettings.roughness_curve "bpy.types.ParticleSettings.roughness_curve") - [`ParticleSettings.twist_curve`](bpy.types.ParticleSettings.md#bpy.types.ParticleSettings.twist_curve "bpy.types.ParticleSettings.twist_curve") - [`RenderSettings.motion_blur_shutter_curve`](bpy.types.RenderSettings.md#bpy.types.RenderSettings.motion_blur_shutter_curve "bpy.types.RenderSettings.motion_blur_shutter_curve") - [`ShaderNodeFloatCurve.mapping`](bpy.types.ShaderNodeFloatCurve.md#bpy.types.ShaderNodeFloatCurve.mapping "bpy.types.ShaderNodeFloatCurve.mapping") - [`ShaderNodeRGBCurve.mapping`](bpy.types.ShaderNodeRGBCurve.md#bpy.types.ShaderNodeRGBCurve.mapping "bpy.types.ShaderNodeRGBCurve.mapping") - [`ShaderNodeVectorCurve.mapping`](bpy.types.ShaderNodeVectorCurve.md#bpy.types.ShaderNodeVectorCurve.mapping "bpy.types.ShaderNodeVectorCurve.mapping") - [`TextureNodeCurveRGB.mapping`](bpy.types.TextureNodeCurveRGB.md#bpy.types.TextureNodeCurveRGB.mapping "bpy.types.TextureNodeCurveRGB.mapping") - [`TextureNodeCurveTime.curve`](bpy.types.TextureNodeCurveTime.md#bpy.types.TextureNodeCurveTime.curve "bpy.types.TextureNodeCurveTime.curve") - [`UvSculpt.curve_distance_falloff`](bpy.types.UvSculpt.md#bpy.types.UvSculpt.curve_distance_falloff "bpy.types.UvSculpt.curve_distance_falloff") - [`VertexWeightEditModifier.map_curve`](bpy.types.VertexWeightEditModifier.md#bpy.types.VertexWeightEditModifier.map_curve "bpy.types.VertexWeightEditModifier.map_curve") - [`VertexWeightProximityModifier.map_curve`](bpy.types.VertexWeightProximityModifier.md#bpy.types.VertexWeightProximityModifier.map_curve "bpy.types.VertexWeightProximityModifier.map_curve") - [`WarpModifier.falloff_curve`](bpy.types.WarpModifier.md#bpy.types.WarpModifier.falloff_curve "bpy.types.WarpModifier.falloff_curve") |
