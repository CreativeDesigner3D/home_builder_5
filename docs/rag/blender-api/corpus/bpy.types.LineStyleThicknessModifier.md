<!-- source: Blender Python API reference 5.2 / bpy.types.LineStyleThicknessModifier.html -->

<a id="linestylethicknessmodifier-linestylemodifier"></a>

# LineStyleThicknessModifier(LineStyleModifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`LineStyleModifier`](bpy.types.LineStyleModifier.md#bpy.types.LineStyleModifier "bpy.types.LineStyleModifier")

Subclasses

- [LineStyleThicknessModifier_AlongStroke(LineStyleThicknessModifier)](bpy.types.LineStyleThicknessModifier_AlongStroke.md)
- [LineStyleThicknessModifier_Calligraphy(LineStyleThicknessModifier)](bpy.types.LineStyleThicknessModifier_Calligraphy.md)
- [LineStyleThicknessModifier_CreaseAngle(LineStyleThicknessModifier)](bpy.types.LineStyleThicknessModifier_CreaseAngle.md)
- [LineStyleThicknessModifier_Curvature_3D(LineStyleThicknessModifier)](bpy.types.LineStyleThicknessModifier_Curvature_3D.md)
- [LineStyleThicknessModifier_DistanceFromCamera(LineStyleThicknessModifier)](bpy.types.LineStyleThicknessModifier_DistanceFromCamera.md)
- [LineStyleThicknessModifier_DistanceFromObject(LineStyleThicknessModifier)](bpy.types.LineStyleThicknessModifier_DistanceFromObject.md)
- [LineStyleThicknessModifier_Material(LineStyleThicknessModifier)](bpy.types.LineStyleThicknessModifier_Material.md)
- [LineStyleThicknessModifier_Noise(LineStyleThicknessModifier)](bpy.types.LineStyleThicknessModifier_Noise.md)
- [LineStyleThicknessModifier_Tangent(LineStyleThicknessModifier)](bpy.types.LineStyleThicknessModifier_Tangent.md)

<a id="bpy.types.LineStyleThicknessModifier"></a>

### class bpy.types.LineStyleThicknessModifier(LineStyleModifier)

Base type to define line thickness modifiers

<a id="bpy.types.LineStyleThicknessModifier.name"></a>

#### bpy.types.LineStyleThicknessModifier.name

Name of the modifier (default “”, never None)

**Type:**

str

<a id="bpy.types.LineStyleThicknessModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.LineStyleThicknessModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.LineStyleThicknessModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.LineStyleThicknessModifier.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`FreestyleLineStyle.thickness_modifiers`](bpy.types.FreestyleLineStyle.md#bpy.types.FreestyleLineStyle.thickness_modifiers "bpy.types.FreestyleLineStyle.thickness_modifiers") - [`LineStyleThicknessModifiers.new`](bpy.types.LineStyleThicknessModifiers.md#bpy.types.LineStyleThicknessModifiers.new "bpy.types.LineStyleThicknessModifiers.new") | - [`LineStyleThicknessModifiers.remove`](bpy.types.LineStyleThicknessModifiers.md#bpy.types.LineStyleThicknessModifiers.remove "bpy.types.LineStyleThicknessModifiers.remove") |
