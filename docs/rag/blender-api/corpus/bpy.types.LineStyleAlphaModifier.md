<!-- source: Blender Python API reference 5.2 / bpy.types.LineStyleAlphaModifier.html -->

<a id="linestylealphamodifier-linestylemodifier"></a>

# LineStyleAlphaModifier(LineStyleModifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`LineStyleModifier`](bpy.types.LineStyleModifier.md#bpy.types.LineStyleModifier "bpy.types.LineStyleModifier")

Subclasses

- [LineStyleAlphaModifier_AlongStroke(LineStyleAlphaModifier)](bpy.types.LineStyleAlphaModifier_AlongStroke.md)
- [LineStyleAlphaModifier_CreaseAngle(LineStyleAlphaModifier)](bpy.types.LineStyleAlphaModifier_CreaseAngle.md)
- [LineStyleAlphaModifier_Curvature_3D(LineStyleAlphaModifier)](bpy.types.LineStyleAlphaModifier_Curvature_3D.md)
- [LineStyleAlphaModifier_DistanceFromCamera(LineStyleAlphaModifier)](bpy.types.LineStyleAlphaModifier_DistanceFromCamera.md)
- [LineStyleAlphaModifier_DistanceFromObject(LineStyleAlphaModifier)](bpy.types.LineStyleAlphaModifier_DistanceFromObject.md)
- [LineStyleAlphaModifier_Material(LineStyleAlphaModifier)](bpy.types.LineStyleAlphaModifier_Material.md)
- [LineStyleAlphaModifier_Noise(LineStyleAlphaModifier)](bpy.types.LineStyleAlphaModifier_Noise.md)
- [LineStyleAlphaModifier_Tangent(LineStyleAlphaModifier)](bpy.types.LineStyleAlphaModifier_Tangent.md)

<a id="bpy.types.LineStyleAlphaModifier"></a>

### class bpy.types.LineStyleAlphaModifier(LineStyleModifier)

Base type to define alpha transparency modifiers

<a id="bpy.types.LineStyleAlphaModifier.name"></a>

#### bpy.types.LineStyleAlphaModifier.name

Name of the modifier (default “”, never None)

**Type:**

str

<a id="bpy.types.LineStyleAlphaModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.LineStyleAlphaModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.LineStyleAlphaModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.LineStyleAlphaModifier.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`FreestyleLineStyle.alpha_modifiers`](bpy.types.FreestyleLineStyle.md#bpy.types.FreestyleLineStyle.alpha_modifiers "bpy.types.FreestyleLineStyle.alpha_modifiers") - [`LineStyleAlphaModifiers.new`](bpy.types.LineStyleAlphaModifiers.md#bpy.types.LineStyleAlphaModifiers.new "bpy.types.LineStyleAlphaModifiers.new") | - [`LineStyleAlphaModifiers.remove`](bpy.types.LineStyleAlphaModifiers.md#bpy.types.LineStyleAlphaModifiers.remove "bpy.types.LineStyleAlphaModifiers.remove") |
