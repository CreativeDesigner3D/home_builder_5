<!-- source: Blender Python API reference 5.2 / bpy.types.LineStyleGeometryModifier.html -->

<a id="linestylegeometrymodifier-linestylemodifier"></a>

# LineStyleGeometryModifier(LineStyleModifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`LineStyleModifier`](bpy.types.LineStyleModifier.md#bpy.types.LineStyleModifier "bpy.types.LineStyleModifier")

Subclasses

- [LineStyleGeometryModifier_2DOffset(LineStyleGeometryModifier)](bpy.types.LineStyleGeometryModifier_2DOffset.md)
- [LineStyleGeometryModifier_2DTransform(LineStyleGeometryModifier)](bpy.types.LineStyleGeometryModifier_2DTransform.md)
- [LineStyleGeometryModifier_BackboneStretcher(LineStyleGeometryModifier)](bpy.types.LineStyleGeometryModifier_BackboneStretcher.md)
- [LineStyleGeometryModifier_BezierCurve(LineStyleGeometryModifier)](bpy.types.LineStyleGeometryModifier_BezierCurve.md)
- [LineStyleGeometryModifier_Blueprint(LineStyleGeometryModifier)](bpy.types.LineStyleGeometryModifier_Blueprint.md)
- [LineStyleGeometryModifier_GuidingLines(LineStyleGeometryModifier)](bpy.types.LineStyleGeometryModifier_GuidingLines.md)
- [LineStyleGeometryModifier_PerlinNoise1D(LineStyleGeometryModifier)](bpy.types.LineStyleGeometryModifier_PerlinNoise1D.md)
- [LineStyleGeometryModifier_PerlinNoise2D(LineStyleGeometryModifier)](bpy.types.LineStyleGeometryModifier_PerlinNoise2D.md)
- [LineStyleGeometryModifier_Polygonalization(LineStyleGeometryModifier)](bpy.types.LineStyleGeometryModifier_Polygonalization.md)
- [LineStyleGeometryModifier_Sampling(LineStyleGeometryModifier)](bpy.types.LineStyleGeometryModifier_Sampling.md)
- [LineStyleGeometryModifier_Simplification(LineStyleGeometryModifier)](bpy.types.LineStyleGeometryModifier_Simplification.md)
- [LineStyleGeometryModifier_SinusDisplacement(LineStyleGeometryModifier)](bpy.types.LineStyleGeometryModifier_SinusDisplacement.md)
- [LineStyleGeometryModifier_SpatialNoise(LineStyleGeometryModifier)](bpy.types.LineStyleGeometryModifier_SpatialNoise.md)
- [LineStyleGeometryModifier_TipRemover(LineStyleGeometryModifier)](bpy.types.LineStyleGeometryModifier_TipRemover.md)

<a id="bpy.types.LineStyleGeometryModifier"></a>

### class bpy.types.LineStyleGeometryModifier(LineStyleModifier)

Base type to define stroke geometry modifiers

<a id="bpy.types.LineStyleGeometryModifier.name"></a>

#### bpy.types.LineStyleGeometryModifier.name

Name of the modifier (default “”, never None)

**Type:**

str

<a id="bpy.types.LineStyleGeometryModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.LineStyleGeometryModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.LineStyleGeometryModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.LineStyleGeometryModifier.bl_rna_get_subclass_py(id, default=None, /)

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

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, LineStyleModifier.bl_rna_get_subclass, LineStyleModifier.bl_rna_get_subclass_py

<a id="references"></a>

## References

|  |  |
| --- | --- |
| - [`FreestyleLineStyle.geometry_modifiers`](bpy.types.FreestyleLineStyle.md#bpy.types.FreestyleLineStyle.geometry_modifiers "bpy.types.FreestyleLineStyle.geometry_modifiers") - [`LineStyleGeometryModifiers.new`](bpy.types.LineStyleGeometryModifiers.md#bpy.types.LineStyleGeometryModifiers.new "bpy.types.LineStyleGeometryModifiers.new") | - [`LineStyleGeometryModifiers.remove`](bpy.types.LineStyleGeometryModifiers.md#bpy.types.LineStyleGeometryModifiers.remove "bpy.types.LineStyleGeometryModifiers.remove") |
