<!-- source: Blender Python API reference 5.2 / bpy.types.Constraint.html -->

<a id="constraint-bpy-struct"></a>

# Constraint(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

Subclasses

- [ActionConstraint(Constraint)](bpy.types.ActionConstraint.md)
- [ArmatureConstraint(Constraint)](bpy.types.ArmatureConstraint.md)
- [CameraSolverConstraint(Constraint)](bpy.types.CameraSolverConstraint.md)
- [ChildOfConstraint(Constraint)](bpy.types.ChildOfConstraint.md)
- [ClampToConstraint(Constraint)](bpy.types.ClampToConstraint.md)
- [CopyLocationConstraint(Constraint)](bpy.types.CopyLocationConstraint.md)
- [CopyRotationConstraint(Constraint)](bpy.types.CopyRotationConstraint.md)
- [CopyScaleConstraint(Constraint)](bpy.types.CopyScaleConstraint.md)
- [CopyTransformsConstraint(Constraint)](bpy.types.CopyTransformsConstraint.md)
- [DampedTrackConstraint(Constraint)](bpy.types.DampedTrackConstraint.md)
- [FloorConstraint(Constraint)](bpy.types.FloorConstraint.md)
- [FollowPathConstraint(Constraint)](bpy.types.FollowPathConstraint.md)
- [FollowTrackConstraint(Constraint)](bpy.types.FollowTrackConstraint.md)
- [GeometryAttributeConstraint(Constraint)](bpy.types.GeometryAttributeConstraint.md)
- [KinematicConstraint(Constraint)](bpy.types.KinematicConstraint.md)
- [LimitDistanceConstraint(Constraint)](bpy.types.LimitDistanceConstraint.md)
- [LimitLocationConstraint(Constraint)](bpy.types.LimitLocationConstraint.md)
- [LimitRotationConstraint(Constraint)](bpy.types.LimitRotationConstraint.md)
- [LimitScaleConstraint(Constraint)](bpy.types.LimitScaleConstraint.md)
- [LockedTrackConstraint(Constraint)](bpy.types.LockedTrackConstraint.md)
- [MaintainVolumeConstraint(Constraint)](bpy.types.MaintainVolumeConstraint.md)
- [ObjectSolverConstraint(Constraint)](bpy.types.ObjectSolverConstraint.md)
- [PivotConstraint(Constraint)](bpy.types.PivotConstraint.md)
- [ShrinkwrapConstraint(Constraint)](bpy.types.ShrinkwrapConstraint.md)
- [SplineIKConstraint(Constraint)](bpy.types.SplineIKConstraint.md)
- [StretchToConstraint(Constraint)](bpy.types.StretchToConstraint.md)
- [TrackToConstraint(Constraint)](bpy.types.TrackToConstraint.md)
- [TransformCacheConstraint(Constraint)](bpy.types.TransformCacheConstraint.md)
- [TransformConstraint(Constraint)](bpy.types.TransformConstraint.md)

<a id="bpy.types.Constraint"></a>

### class bpy.types.Constraint(bpy_struct)

Constraint modifying the transformation of objects and bones

<a id="bpy.types.Constraint.active"></a>

#### bpy.types.Constraint.active

Constraint is the one being edited (default False)

**Type:**

bool

<a id="bpy.types.Constraint.enabled"></a>

#### bpy.types.Constraint.enabled

Use the results of this constraint (default True)

**Type:**

bool

<a id="bpy.types.Constraint.error_location"></a>

#### bpy.types.Constraint.error_location

Amount of residual error in Blender space unit for constraints that work on position (in [-inf, inf], default 0.0, readonly)

**Type:**

float

<a id="bpy.types.Constraint.error_rotation"></a>

#### bpy.types.Constraint.error_rotation

Amount of residual error in radians for constraints that work on orientation (in [-inf, inf], default 0.0, readonly)

**Type:**

float

<a id="bpy.types.Constraint.influence"></a>

#### bpy.types.Constraint.influence

Amount of influence constraint will have on the final solution (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.Constraint.is_override_data"></a>

#### bpy.types.Constraint.is_override_data

In a local override object, whether this constraint comes from the linked reference object, or is local to the override (default True, readonly)

**Type:**

bool

<a id="bpy.types.Constraint.is_valid"></a>

#### bpy.types.Constraint.is_valid

Constraint has valid settings and can be evaluated (default True, readonly)

**Type:**

bool

<a id="bpy.types.Constraint.mute"></a>

#### bpy.types.Constraint.mute

Enable/Disable Constraint (default False)

**Type:**

bool

<a id="bpy.types.Constraint.name"></a>

#### bpy.types.Constraint.name

Constraint name (default “”, never None)

**Type:**

str

<a id="bpy.types.Constraint.owner_space"></a>

#### bpy.types.Constraint.owner_space

Space that owner is evaluated in (default `'WORLD'`)

- `WORLD`
  World Space – The constraint is applied relative to the world coordinate system.
- `CUSTOM`
  Custom Space – The constraint is applied in local space of a custom object/bone/vertex group.
- `POSE`
  Pose Space – The constraint is applied in Pose Space, the object transformation is ignored.
- `LOCAL_WITH_PARENT`
  Local With Parent – The constraint is applied relative to the rest pose local coordinate system of the bone, thus including the parent-induced transformation.
- `LOCAL`
  Local Space – The constraint is applied relative to the local coordinate system of the object.

**Type:**

Literal[‘WORLD’, ‘CUSTOM’, ‘POSE’, ‘LOCAL_WITH_PARENT’, ‘LOCAL’]

<a id="bpy.types.Constraint.show_expanded"></a>

#### bpy.types.Constraint.show_expanded

Constraint’s panel is expanded in UI (default False)

**Type:**

bool

<a id="bpy.types.Constraint.space_object"></a>

#### bpy.types.Constraint.space_object

Object for Custom Space

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.Constraint.space_subtarget"></a>

#### bpy.types.Constraint.space_subtarget

Armature bone, mesh or lattice vertex group, … (default “”, never None)

**Type:**

str

<a id="bpy.types.Constraint.target_space"></a>

#### bpy.types.Constraint.target_space

Space that target is evaluated in (default `'WORLD'`)

- `WORLD`
  World Space – The transformation of the target is evaluated relative to the world coordinate system.
- `CUSTOM`
  Custom Space – The transformation of the target is evaluated relative to a custom object/bone/vertex group.
- `POSE`
  Pose Space – The transformation of the target is only evaluated in the Pose Space, the target armature object transformation is ignored.
- `LOCAL_WITH_PARENT`
  Local With Parent – The transformation of the target bone is evaluated relative to its rest pose local coordinate system, thus including the parent-induced transformation.
- `LOCAL`
  Local Space – The transformation of the target is evaluated relative to its local coordinate system.
- `LOCAL_OWNER_ORIENT`
  Local Space (Owner Orientation) – The transformation of the target bone is evaluated relative to its local coordinate system, followed by a correction for the difference in target and owner rest pose orientations. When applied as local transform to the owner produces the same global motion as the target if the parents are still in rest pose..

**Type:**

Literal[‘WORLD’, ‘CUSTOM’, ‘POSE’, ‘LOCAL_WITH_PARENT’, ‘LOCAL’, ‘LOCAL_OWNER_ORIENT’]

<a id="bpy.types.Constraint.type"></a>

#### bpy.types.Constraint.type

(default `'CAMERA_SOLVER'`, readonly)

**Type:**

Literal[[Constraint Type Items](bpy_types_enum_items/constraint_type_items.md#rna-enum-constraint-type-items)]

<a id="bpy.types.Constraint.bl_rna_get_subclass"></a>

#### classmethod bpy.types.Constraint.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.Constraint.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.Constraint.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([type](#bpy.types.Constraint.type "bpy.types.Constraint.type") | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

[type](#bpy.types.Constraint.type "bpy.types.Constraint.type")

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
| - [`Object.constraints`](bpy.types.Object.md#bpy.types.Object.constraints "bpy.types.Object.constraints") - [`ObjectConstraints.active`](bpy.types.ObjectConstraints.md#bpy.types.ObjectConstraints.active "bpy.types.ObjectConstraints.active") - [`ObjectConstraints.copy`](bpy.types.ObjectConstraints.md#bpy.types.ObjectConstraints.copy "bpy.types.ObjectConstraints.copy") - [`ObjectConstraints.copy`](bpy.types.ObjectConstraints.md#bpy.types.ObjectConstraints.copy "bpy.types.ObjectConstraints.copy") - [`ObjectConstraints.new`](bpy.types.ObjectConstraints.md#bpy.types.ObjectConstraints.new "bpy.types.ObjectConstraints.new") - [`ObjectConstraints.remove`](bpy.types.ObjectConstraints.md#bpy.types.ObjectConstraints.remove "bpy.types.ObjectConstraints.remove") - [`Panel.custom_data`](bpy.types.Panel.md#bpy.types.Panel.custom_data "bpy.types.Panel.custom_data") | - [`PoseBone.constraints`](bpy.types.PoseBone.md#bpy.types.PoseBone.constraints "bpy.types.PoseBone.constraints") - [`PoseBoneConstraints.active`](bpy.types.PoseBoneConstraints.md#bpy.types.PoseBoneConstraints.active "bpy.types.PoseBoneConstraints.active") - [`PoseBoneConstraints.copy`](bpy.types.PoseBoneConstraints.md#bpy.types.PoseBoneConstraints.copy "bpy.types.PoseBoneConstraints.copy") - [`PoseBoneConstraints.copy`](bpy.types.PoseBoneConstraints.md#bpy.types.PoseBoneConstraints.copy "bpy.types.PoseBoneConstraints.copy") - [`PoseBoneConstraints.new`](bpy.types.PoseBoneConstraints.md#bpy.types.PoseBoneConstraints.new "bpy.types.PoseBoneConstraints.new") - [`PoseBoneConstraints.remove`](bpy.types.PoseBoneConstraints.md#bpy.types.PoseBoneConstraints.remove "bpy.types.PoseBoneConstraints.remove") - [`UILayout.template_constraint_header`](bpy.types.UILayout.md#bpy.types.UILayout.template_constraint_header "bpy.types.UILayout.template_constraint_header") |
