<!-- source: Blender Python API reference 5.2 / bpy.types.ConstraintTargetBone.html -->

<a id="constrainttargetbone-bpy-struct"></a>

# ConstraintTargetBone(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.ConstraintTargetBone"></a>

### class bpy.types.ConstraintTargetBone(bpy_struct)

Target bone for multi-target constraints

<a id="bpy.types.ConstraintTargetBone.subtarget"></a>

#### bpy.types.ConstraintTargetBone.subtarget

Target armature bone (default “”, never None)

**Type:**

str

<a id="bpy.types.ConstraintTargetBone.target"></a>

#### bpy.types.ConstraintTargetBone.target

Target armature

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.ConstraintTargetBone.weight"></a>

#### bpy.types.ConstraintTargetBone.weight

Blending weight of this bone (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.ConstraintTargetBone.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ConstraintTargetBone.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ConstraintTargetBone.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ConstraintTargetBone.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`ArmatureConstraint.targets`](bpy.types.ArmatureConstraint.md#bpy.types.ArmatureConstraint.targets "bpy.types.ArmatureConstraint.targets") - [`ArmatureConstraintTargets.new`](bpy.types.ArmatureConstraintTargets.md#bpy.types.ArmatureConstraintTargets.new "bpy.types.ArmatureConstraintTargets.new") | - [`ArmatureConstraintTargets.remove`](bpy.types.ArmatureConstraintTargets.md#bpy.types.ArmatureConstraintTargets.remove "bpy.types.ArmatureConstraintTargets.remove") |
