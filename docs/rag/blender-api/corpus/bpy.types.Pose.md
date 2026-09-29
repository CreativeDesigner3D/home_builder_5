<!-- source: Blender Python API reference 5.2 / bpy.types.Pose.html -->

<a id="pose-bpy-struct"></a>

# Pose(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.Pose"></a>

### class bpy.types.Pose(bpy_struct)

A collection of pose channels, including settings for animating bones

<a id="bpy.types.Pose.animation_visualization"></a>

#### bpy.types.Pose.animation_visualization

Animation data for this data-block (readonly, never None)

**Type:**

[`AnimViz`](bpy.types.AnimViz.md#bpy.types.AnimViz "bpy.types.AnimViz")

<a id="bpy.types.Pose.bones"></a>

#### bpy.types.Pose.bones

Individual pose bones for the armature (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`PoseBone`](bpy.types.PoseBone.md#bpy.types.PoseBone "bpy.types.PoseBone")]

<a id="bpy.types.Pose.ik_param"></a>

#### bpy.types.Pose.ik_param

Parameters for IK solver (readonly)

**Type:**

[`IKParam`](bpy.types.IKParam.md#bpy.types.IKParam "bpy.types.IKParam") | None

<a id="bpy.types.Pose.ik_solver"></a>

#### bpy.types.Pose.ik_solver

Selection of IK solver for IK chain (default `'LEGACY'`)

- `LEGACY`
  Standard – Original IK solver.
- `ITASC`
  iTaSC – Multi constraint, stateful IK solver.

**Type:**

Literal[‘LEGACY’, ‘ITASC’]

<a id="bpy.types.Pose.use_auto_ik"></a>

#### bpy.types.Pose.use_auto_ik

Add temporary IK constraints while grabbing bones in Pose Mode (default False)

**Type:**

bool

<a id="bpy.types.Pose.use_mirror_relative"></a>

#### bpy.types.Pose.use_mirror_relative

Apply relative transformations in X-mirror mode (not supported with Auto IK) (default False)

**Type:**

bool

<a id="bpy.types.Pose.use_mirror_x"></a>

#### bpy.types.Pose.use_mirror_x

Apply changes to matching bone on opposite side of X-Axis (default False)

**Type:**

bool

<a id="bpy.types.Pose.apply_pose_from_action"></a>

#### classmethod bpy.types.Pose.apply_pose_from_action(action, *, evaluation_time=0.0)

Apply the given action to this pose by evaluating it at a specific time. Only updates the pose of selected bones, or all bones if none are selected.

**Parameters:**

- **action** ([`Action`](bpy.types.Action.md#bpy.types.Action "bpy.types.Action") | None) – Action, The Action containing the pose
- **evaluation_time** (float) – Evaluation Time, Time at which the given action is evaluated to obtain the pose (in [-inf, inf], optional)

<a id="bpy.types.Pose.blend_pose_from_action"></a>

#### classmethod bpy.types.Pose.blend_pose_from_action(action, *, blend_factor=1.0, evaluation_time=0.0)

Blend the given action into this pose by evaluating it at a specific time. Only updates the pose of selected bones, or all bones if none are selected.

**Parameters:**

- **action** ([`Action`](bpy.types.Action.md#bpy.types.Action "bpy.types.Action") | None) – Action, The Action containing the pose
- **blend_factor** (float) – Blend Factor, How much the given Action affects the final pose (in [0, 1], optional)
- **evaluation_time** (float) – Evaluation Time, Time at which the given action is evaluated to obtain the pose (in [-inf, inf], optional)

<a id="bpy.types.Pose.backup_create"></a>

#### classmethod bpy.types.Pose.backup_create(action)

Create a backup of the current pose. Only those bones that are animated in the Action are backed up. The object owns the backup, and each object can have only one backup at a time. When you no longer need it, it must be freed use `backup_clear()`.

**Parameters:**

**action** ([`Action`](bpy.types.Action.md#bpy.types.Action "bpy.types.Action") | None) – Action, An Action with animation data for the bones. Only the animated bones will be included in the backup.

<a id="bpy.types.Pose.backup_restore"></a>

#### classmethod bpy.types.Pose.backup_restore()

Restore the previously made pose backup. This can be called multiple times. See `Pose.backup_create()` for more info.

**Returns:**

`True` when the backup was restored, `False` if there was no backup to restore

**Return type:**

bool

<a id="bpy.types.Pose.backup_clear"></a>

#### classmethod bpy.types.Pose.backup_clear()

Free a previously made pose backup. See `Pose.backup_create()` for more info.

<a id="bpy.types.Pose.bl_rna_get_subclass"></a>

#### classmethod bpy.types.Pose.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.Pose.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.Pose.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Object.pose`](bpy.types.Object.md#bpy.types.Object.pose "bpy.types.Object.pose") |  |
