<!-- source: Blender Python API reference 5.2 / bpy.types.PoseBone.html -->

<a id="posebone-bpy-struct"></a>

# PoseBone(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.PoseBone"></a>

### class bpy.types.PoseBone(bpy_struct)

Channel defining pose data for a bone in a Pose

<a id="bpy.types.PoseBone.bbone_curveinx"></a>

#### bpy.types.PoseBone.bbone_curveinx

X-axis handle offset for start of the B-Bone’s curve, adjusts curvature (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.PoseBone.bbone_curveinz"></a>

#### bpy.types.PoseBone.bbone_curveinz

Z-axis handle offset for start of the B-Bone’s curve, adjusts curvature (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.PoseBone.bbone_curveoutx"></a>

#### bpy.types.PoseBone.bbone_curveoutx

X-axis handle offset for end of the B-Bone’s curve, adjusts curvature (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.PoseBone.bbone_curveoutz"></a>

#### bpy.types.PoseBone.bbone_curveoutz

Z-axis handle offset for end of the B-Bone’s curve, adjusts curvature (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.PoseBone.bbone_custom_handle_end"></a>

#### bpy.types.PoseBone.bbone_custom_handle_end

Bone that serves as the end handle for the B-Bone curve (readonly)

**Type:**

[`PoseBone`](#bpy.types.PoseBone "bpy.types.PoseBone") | None

<a id="bpy.types.PoseBone.bbone_custom_handle_start"></a>

#### bpy.types.PoseBone.bbone_custom_handle_start

Bone that serves as the start handle for the B-Bone curve (readonly)

**Type:**

[`PoseBone`](#bpy.types.PoseBone "bpy.types.PoseBone") | None

<a id="bpy.types.PoseBone.bbone_easein"></a>

#### bpy.types.PoseBone.bbone_easein

Length of first Bézier Handle (for B-Bones only) (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.PoseBone.bbone_easeout"></a>

#### bpy.types.PoseBone.bbone_easeout

Length of second Bézier Handle (for B-Bones only) (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.PoseBone.bbone_rollin"></a>

#### bpy.types.PoseBone.bbone_rollin

Roll offset for the start of the B-Bone, adjusts twist (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.PoseBone.bbone_rollout"></a>

#### bpy.types.PoseBone.bbone_rollout

Roll offset for the end of the B-Bone, adjusts twist (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.PoseBone.bbone_scalein"></a>

#### bpy.types.PoseBone.bbone_scalein

Scale factors for the start of the B-Bone, adjusts thickness (for tapering effects) (array of 3 items, in [-inf, inf], default (1.0, 1.0, 1.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.PoseBone.bbone_scaleout"></a>

#### bpy.types.PoseBone.bbone_scaleout

Scale factors for the end of the B-Bone, adjusts thickness (for tapering effects) (array of 3 items, in [-inf, inf], default (1.0, 1.0, 1.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.PoseBone.bone"></a>

#### bpy.types.PoseBone.bone

Bone associated with this PoseBone (readonly, never None)

**Type:**

[`Bone`](bpy.types.Bone.md#bpy.types.Bone "bpy.types.Bone")

<a id="bpy.types.PoseBone.child"></a>

#### bpy.types.PoseBone.child

Child of this pose bone (readonly)

**Type:**

[`PoseBone`](#bpy.types.PoseBone "bpy.types.PoseBone") | None

<a id="bpy.types.PoseBone.color"></a>

#### bpy.types.PoseBone.color

(readonly)

**Type:**

[`BoneColor`](bpy.types.BoneColor.md#bpy.types.BoneColor "bpy.types.BoneColor") | None

<a id="bpy.types.PoseBone.constraints"></a>

#### bpy.types.PoseBone.constraints

Constraints that act on this pose channel (default None, readonly)

**Type:**

[`PoseBoneConstraints`](bpy.types.PoseBoneConstraints.md#bpy.types.PoseBoneConstraints "bpy.types.PoseBoneConstraints")[[`Constraint`](bpy.types.Constraint.md#bpy.types.Constraint "bpy.types.Constraint")]

<a id="bpy.types.PoseBone.custom_shape"></a>

#### bpy.types.PoseBone.custom_shape

Object that defines custom display shape for this bone

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.PoseBone.custom_shape_rotation_euler"></a>

#### bpy.types.PoseBone.custom_shape_rotation_euler

Adjust the rotation of the custom shape (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler")

<a id="bpy.types.PoseBone.custom_shape_scale_xyz"></a>

#### bpy.types.PoseBone.custom_shape_scale_xyz

Adjust the size of the custom shape (array of 3 items, in [-inf, inf], default (1.0, 1.0, 1.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.PoseBone.custom_shape_transform"></a>

#### bpy.types.PoseBone.custom_shape_transform

Bone that defines the display transform of this custom shape

**Type:**

[`PoseBone`](#bpy.types.PoseBone "bpy.types.PoseBone") | None

<a id="bpy.types.PoseBone.custom_shape_translation"></a>

#### bpy.types.PoseBone.custom_shape_translation

Adjust the location of the custom shape (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.PoseBone.custom_shape_wire_width"></a>

#### bpy.types.PoseBone.custom_shape_wire_width

Adjust the line thickness of custom shapes (in [1, 16], default 0.0)

**Type:**

float

<a id="bpy.types.PoseBone.head"></a>

#### bpy.types.PoseBone.head

Location of head of the channel’s bone (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0), readonly)

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.PoseBone.hide"></a>

#### bpy.types.PoseBone.hide

Bone is not visible except for Edit Mode (default False)

**Type:**

bool

<a id="bpy.types.PoseBone.ik_linear_weight"></a>

#### bpy.types.PoseBone.ik_linear_weight

Weight of scale constraint for IK (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.PoseBone.ik_max_x"></a>

#### bpy.types.PoseBone.ik_max_x

Maximum angles for IK Limit (in [0, 3.14159], default 0.0)

**Type:**

float

<a id="bpy.types.PoseBone.ik_max_y"></a>

#### bpy.types.PoseBone.ik_max_y

Maximum angles for IK Limit (in [0, 3.14159], default 0.0)

**Type:**

float

<a id="bpy.types.PoseBone.ik_max_z"></a>

#### bpy.types.PoseBone.ik_max_z

Maximum angles for IK Limit (in [0, 3.14159], default 0.0)

**Type:**

float

<a id="bpy.types.PoseBone.ik_min_x"></a>

#### bpy.types.PoseBone.ik_min_x

Minimum angles for IK Limit (in [-3.14159, 0], default 0.0)

**Type:**

float

<a id="bpy.types.PoseBone.ik_min_y"></a>

#### bpy.types.PoseBone.ik_min_y

Minimum angles for IK Limit (in [-3.14159, 0], default 0.0)

**Type:**

float

<a id="bpy.types.PoseBone.ik_min_z"></a>

#### bpy.types.PoseBone.ik_min_z

Minimum angles for IK Limit (in [-3.14159, 0], default 0.0)

**Type:**

float

<a id="bpy.types.PoseBone.ik_rotation_weight"></a>

#### bpy.types.PoseBone.ik_rotation_weight

Weight of rotation constraint for IK (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.PoseBone.ik_stiffness_x"></a>

#### bpy.types.PoseBone.ik_stiffness_x

IK stiffness around the X axis (in [0, 0.99], default 0.0)

**Type:**

float

<a id="bpy.types.PoseBone.ik_stiffness_y"></a>

#### bpy.types.PoseBone.ik_stiffness_y

IK stiffness around the Y axis (in [0, 0.99], default 0.0)

**Type:**

float

<a id="bpy.types.PoseBone.ik_stiffness_z"></a>

#### bpy.types.PoseBone.ik_stiffness_z

IK stiffness around the Z axis (in [0, 0.99], default 0.0)

**Type:**

float

<a id="bpy.types.PoseBone.ik_stretch"></a>

#### bpy.types.PoseBone.ik_stretch

Allow scaling of the bone for IK (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.PoseBone.is_in_ik_chain"></a>

#### bpy.types.PoseBone.is_in_ik_chain

Is part of an IK chain (default False, readonly)

**Type:**

bool

<a id="bpy.types.PoseBone.length"></a>

#### bpy.types.PoseBone.length

Length of the bone (in [-inf, inf], default 0.0, readonly)

**Type:**

float

<a id="bpy.types.PoseBone.location"></a>

#### bpy.types.PoseBone.location

(array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.PoseBone.lock_ik_x"></a>

#### bpy.types.PoseBone.lock_ik_x

Disallow movement around the X axis (default False)

**Type:**

bool

<a id="bpy.types.PoseBone.lock_ik_y"></a>

#### bpy.types.PoseBone.lock_ik_y

Disallow movement around the Y axis (default False)

**Type:**

bool

<a id="bpy.types.PoseBone.lock_ik_z"></a>

#### bpy.types.PoseBone.lock_ik_z

Disallow movement around the Z axis (default False)

**Type:**

bool

<a id="bpy.types.PoseBone.lock_location"></a>

#### bpy.types.PoseBone.lock_location

Lock editing of location when transforming (array of 3 items, default (False, False, False))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[bool]

<a id="bpy.types.PoseBone.lock_rotation"></a>

#### bpy.types.PoseBone.lock_rotation

Lock editing of rotation when transforming (array of 3 items, default (False, False, False))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[bool]

<a id="bpy.types.PoseBone.lock_rotation_w"></a>

#### bpy.types.PoseBone.lock_rotation_w

Lock editing of ‘angle’ component of four-component rotations when transforming (default False)

**Type:**

bool

<a id="bpy.types.PoseBone.lock_rotations_4d"></a>

#### bpy.types.PoseBone.lock_rotations_4d

Lock editing of four component rotations by components (instead of as Eulers) (default False)

**Type:**

bool

<a id="bpy.types.PoseBone.lock_scale"></a>

#### bpy.types.PoseBone.lock_scale

Lock editing of scale when transforming (array of 3 items, default (False, False, False))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[bool]

<a id="bpy.types.PoseBone.matrix"></a>

#### bpy.types.PoseBone.matrix

Final 4×4 matrix after constraints and drivers are applied, in the armature object space (multi-dimensional array of 4 * 4 items, in [-inf, inf], default ((0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0)))

**Type:**

[`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")

<a id="bpy.types.PoseBone.matrix_basis"></a>

#### bpy.types.PoseBone.matrix_basis

Alternative access to location/scale/rotation relative to the parent and own rest bone (multi-dimensional array of 4 * 4 items, in [-inf, inf], default ((0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0)))

**Type:**

[`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")

<a id="bpy.types.PoseBone.matrix_channel"></a>

#### bpy.types.PoseBone.matrix_channel

4×4 matrix of the bone’s location/rotation/scale channels (including animation and drivers) and the effect of bone constraints (multi-dimensional array of 4 * 4 items, in [-inf, inf], default ((0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0)), readonly)

**Type:**

[`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")

<a id="bpy.types.PoseBone.motion_path"></a>

#### bpy.types.PoseBone.motion_path

Motion Path for this element (readonly)

**Type:**

[`MotionPath`](bpy.types.MotionPath.md#bpy.types.MotionPath "bpy.types.MotionPath") | None

<a id="bpy.types.PoseBone.name"></a>

#### bpy.types.PoseBone.name

(default “”, never None)

**Type:**

str

<a id="bpy.types.PoseBone.parent"></a>

#### bpy.types.PoseBone.parent

Parent of this pose bone (readonly)

**Type:**

[`PoseBone`](#bpy.types.PoseBone "bpy.types.PoseBone") | None

<a id="bpy.types.PoseBone.rotation_axis_angle"></a>

#### bpy.types.PoseBone.rotation_axis_angle

Angle of Rotation for Axis-Angle rotation representation (array of 4 items, in [-inf, inf], default (0.0, 0.0, 1.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.PoseBone.rotation_euler"></a>

#### bpy.types.PoseBone.rotation_euler

Rotation in Eulers (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler")

<a id="bpy.types.PoseBone.rotation_mode"></a>

#### bpy.types.PoseBone.rotation_mode

The kind of rotation to apply, values from other rotation modes are not used (default `'QUATERNION'`)

**Type:**

Literal[[Object Rotation Mode Items](bpy_types_enum_items/object_rotation_mode_items.md#rna-enum-object-rotation-mode-items)]

<a id="bpy.types.PoseBone.rotation_quaternion"></a>

#### bpy.types.PoseBone.rotation_quaternion

Rotation in Quaternions (array of 4 items, in [-inf, inf], default (1.0, 0.0, 0.0, 0.0))

**Type:**

[`mathutils.Quaternion`](mathutils.md#mathutils.Quaternion "mathutils.Quaternion")

<a id="bpy.types.PoseBone.scale"></a>

#### bpy.types.PoseBone.scale

(array of 3 items, in [-inf, inf], default (1.0, 1.0, 1.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.PoseBone.select"></a>

#### bpy.types.PoseBone.select

Bone is selected in Pose Mode (default False)

**Type:**

bool

<a id="bpy.types.PoseBone.tail"></a>

#### bpy.types.PoseBone.tail

Location of tail of the channel’s bone (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0), readonly)

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.PoseBone.use_custom_shape_bone_size"></a>

#### bpy.types.PoseBone.use_custom_shape_bone_size

Scale the custom object by the bone length (default True)

**Type:**

bool

<a id="bpy.types.PoseBone.use_ik_limit_x"></a>

#### bpy.types.PoseBone.use_ik_limit_x

Limit movement around the X axis (default False)

**Type:**

bool

<a id="bpy.types.PoseBone.use_ik_limit_y"></a>

#### bpy.types.PoseBone.use_ik_limit_y

Limit movement around the Y axis (default False)

**Type:**

bool

<a id="bpy.types.PoseBone.use_ik_limit_z"></a>

#### bpy.types.PoseBone.use_ik_limit_z

Limit movement around the Z axis (default False)

**Type:**

bool

<a id="bpy.types.PoseBone.use_ik_linear_control"></a>

#### bpy.types.PoseBone.use_ik_linear_control

Apply channel size as IK constraint if stretching is enabled (default False)

**Type:**

bool

<a id="bpy.types.PoseBone.use_ik_rotation_control"></a>

#### bpy.types.PoseBone.use_ik_rotation_control

Apply channel rotation as IK constraint (default False)

**Type:**

bool

<a id="bpy.types.PoseBone.use_transform_around_custom_shape"></a>

#### bpy.types.PoseBone.use_transform_around_custom_shape

Transform the bone as if it was a child of the Custom Shape Transform bone. This can be useful when combining shape-key and armature deformations. (default False)

**Type:**

bool

<a id="bpy.types.PoseBone.use_transform_at_custom_shape"></a>

#### bpy.types.PoseBone.use_transform_at_custom_shape

The location and orientation of the Custom Shape Transform bone will be used for transform gizmos and for other transform operators in the 3D Viewport. When disabled, the 3D Viewport will still use the actual bone transform for these, even when the custom bone shape transform is overridden. (default False)

**Type:**

bool

<a id="bpy.types.PoseBone.basename"></a>

#### bpy.types.PoseBone.basename

The name of this bone before any `.` character.

(readonly)

<a id="bpy.types.PoseBone.center"></a>

#### bpy.types.PoseBone.center

The midpoint between the head and the tail.

(readonly)

<a id="bpy.types.PoseBone.children"></a>

#### bpy.types.PoseBone.children

(readonly)

<a id="bpy.types.PoseBone.children_recursive"></a>

#### bpy.types.PoseBone.children_recursive

A list of all children from this bone.

> **Note:**
>
> Takes `O(len(bones)**2)` time.

(readonly)

<a id="bpy.types.PoseBone.children_recursive_basename"></a>

#### bpy.types.PoseBone.children_recursive_basename

Returns a chain of children with the same base name as this bone.
Only direct chains are supported, forks caused by multiple children
with matching base names will terminate the function
and not be returned.

> **Note:**
>
> Takes `O(len(bones)**2)` time.

(readonly)

<a id="bpy.types.PoseBone.parent_recursive"></a>

#### bpy.types.PoseBone.parent_recursive

A list of parents, starting with the immediate parent.

(readonly)

<a id="bpy.types.PoseBone.vector"></a>

#### bpy.types.PoseBone.vector

The direction this bone is pointing.
Utility function for (tail - head)

(readonly)

<a id="bpy.types.PoseBone.x_axis"></a>

#### bpy.types.PoseBone.x_axis

Vector pointing down the x-axis of the bone.

(readonly)

<a id="bpy.types.PoseBone.y_axis"></a>

#### bpy.types.PoseBone.y_axis

Vector pointing down the y-axis of the bone.

(readonly)

<a id="bpy.types.PoseBone.z_axis"></a>

#### bpy.types.PoseBone.z_axis

Vector pointing down the z-axis of the bone.

(readonly)

<a id="bpy.types.PoseBone.bl_system_properties_get"></a>

#### bpy.types.PoseBone.bl_system_properties_get(*, do_create=False)

DEBUG ONLY. Internal access to runtime-defined RNA data storage, intended solely for testing and debugging purposes. Do not access it in regular scripting work, and in particular, do not assume that it contains writable data

**Parameters:**

**do_create** (bool) – Ensure that system properties are created if they do not exist yet (optional)

**Returns:**

The system properties root container, or None if there are no system properties stored in this data yet, and its creation was not requested

**Return type:**

[`PropertyGroup`](bpy.types.PropertyGroup.md#bpy.types.PropertyGroup "bpy.types.PropertyGroup")

<a id="bpy.types.PoseBone.evaluate_envelope"></a>

#### bpy.types.PoseBone.evaluate_envelope(point)

Calculate bone envelope at given point

**Parameters:**

**point** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Point, Position in 3d space to evaluate (array of 3 items, in [-inf, inf])

**Returns:**

Factor, Envelope factor (in [-inf, inf])

**Return type:**

float

<a id="bpy.types.PoseBone.bbone_segment_index"></a>

#### bpy.types.PoseBone.bbone_segment_index(point)

Retrieve the index and blend factor of the B-Bone segments based on vertex position

**Parameters:**

**point** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Point, Vertex position in armature pose space (array of 3 items, in [-inf, inf])

**Returns:**

`index`, The index of the first segment joint affecting the point, int

`blend_next`, The blend factor between the given and the following joint, float

**Return type:**

tuple[int, float]

<a id="bpy.types.PoseBone.bbone_segment_matrix"></a>

#### bpy.types.PoseBone.bbone_segment_matrix(index, *, rest=False)

Retrieve the matrix of the joint between B-Bone segments if available

**Parameters:**

- **index** (int) – Index of the segment endpoint (in [0, inf])
- **rest** (bool) – Return the rest pose matrix (optional)

**Returns:**

The resulting matrix in bone local space (multi-dimensional array of 4 * 4 items, in [-inf, inf])

**Return type:**

[`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")

This example shows how to use B-Bone segment matrices to emulate deformation
produced by the Armature modifier or constraint when assigned to the given bone
(without Preserve Volume). The coordinates are processed in armature Pose space:

```python
import bpy

def bbone_deform_matrix(pose_bone, point):
    index, blend_next = pose_bone.bbone_segment_index(point)

    rest1 = pose_bone.bbone_segment_matrix(index, rest=True)
    pose1 = pose_bone.bbone_segment_matrix(index, rest=False)
    deform1 = pose1 @ rest1.inverted()

    # `bbone_segment_index` ensures that index + 1 is always valid
    rest2 = pose_bone.bbone_segment_matrix(index + 1, rest=True)
    pose2 = pose_bone.bbone_segment_matrix(index + 1, rest=False)
    deform2 = pose2 @ rest2.inverted()

    deform = deform1 * (1 - blend_next) + deform2 * blend_next

    return pose_bone.matrix @ deform @ pose_bone.bone.matrix_local.inverted()

# Armature modifier deforming vertices:
mesh = bpy.data.objects["Mesh"]
pose_bone = bpy.data.objects["Armature"].pose.bones["Bone"]

for vertex in mesh.data.vertices:
    vertex.co = bbone_deform_matrix(pose_bone, vertex.co) @ vertex.co

# Armature constraint modifying an object transform:
empty = bpy.data.objects["Empty"]
matrix = empty.matrix_world

empty.matrix_world = bbone_deform_matrix(pose_bone, matrix.translation) @ matrix
```

<a id="bpy.types.PoseBone.compute_bbone_handles"></a>

#### bpy.types.PoseBone.compute_bbone_handles(*, rest=False, ease=False, offsets=False)

Retrieve the vectors and rolls coming from B-Bone custom handles

**Parameters:**

- **rest** (bool) – Return the rest pose state (optional)
- **ease** (bool) – Apply scale from ease values (optional)
- **offsets** (bool) – Apply roll and curve offsets from bone properties (optional)

**Returns:**

`handle1`, The direction vector of the start handle in bone local space, [`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

`roll1`, Roll of the start handle, float

`handle2`, The direction vector of the end handle in bone local space, [`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

`roll2`, Roll of the end handle, float

**Return type:**

tuple[[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector"), float, [`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector"), float]

<a id="bpy.types.PoseBone.parent_index"></a>

#### bpy.types.PoseBone.parent_index(parent_test)

The same as ‘bone in other_bone.parent_recursive’
but saved generating a list.

**Parameters:**

**parent_test** (Self) – Bone to search for among this bone’s ancestors.

**Returns:**

1-based depth of parent_test in the parent chain, or 0 if not found.

**Return type:**

int

<a id="bpy.types.PoseBone.translate"></a>

#### bpy.types.PoseBone.translate(vec)

Utility function to add *vec* to the head and tail of this bone.

**Parameters:**

**vec** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – Translation vector.

<a id="bpy.types.PoseBone.bl_rna_get_subclass"></a>

#### classmethod bpy.types.PoseBone.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.PoseBone.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.PoseBone.bl_rna_get_subclass_py(id, default=None, /)

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
| - `bpy.context.active_pose_bone` - `bpy.context.pose_bone` - `bpy.context.selected_pose_bones` - `bpy.context.selected_pose_bones_from_active_object` - `bpy.context.visible_pose_bones` - [`Object.convert_space`](bpy.types.Object.md#bpy.types.Object.convert_space "bpy.types.Object.convert_space") | - [`Pose.bones`](bpy.types.Pose.md#bpy.types.Pose.bones "bpy.types.Pose.bones") - [`PoseBone.bbone_custom_handle_end`](#bpy.types.PoseBone.bbone_custom_handle_end "bpy.types.PoseBone.bbone_custom_handle_end") - [`PoseBone.bbone_custom_handle_start`](#bpy.types.PoseBone.bbone_custom_handle_start "bpy.types.PoseBone.bbone_custom_handle_start") - [`PoseBone.child`](#bpy.types.PoseBone.child "bpy.types.PoseBone.child") - [`PoseBone.custom_shape_transform`](#bpy.types.PoseBone.custom_shape_transform "bpy.types.PoseBone.custom_shape_transform") - [`PoseBone.parent`](#bpy.types.PoseBone.parent "bpy.types.PoseBone.parent") |
