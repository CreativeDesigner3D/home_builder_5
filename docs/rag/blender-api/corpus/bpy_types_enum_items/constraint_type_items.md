<!-- source: Blender Python API reference 5.2 / bpy_types_enum_items/constraint_type_items.html -->

<a id="constraint-type-items"></a>

# Constraint Type Items

**Motion Tracking**

**CAMERA_SOLVER:**

Camera Solver.

**FOLLOW_TRACK:**

Follow Track.

**OBJECT_SOLVER:**

Object Solver.

**Transform**

**COPY_LOCATION:**

Copy Location.

Copy the location of a target (with an optional offset), so that they move together.

**COPY_ROTATION:**

Copy Rotation.

Copy the rotation of a target (with an optional offset), so that they rotate together.

**COPY_SCALE:**

Copy Scale.

Copy the scale factors of a target (with an optional offset), so that they are scaled by the same amount.

**COPY_TRANSFORMS:**

Copy Transforms.

Copy all the transformations of a target, so that they move together.

**LIMIT_DISTANCE:**

Limit Distance.

Restrict movements to within a certain distance of a target (at the time of constraint evaluation only).

**LIMIT_LOCATION:**

Limit Location.

Restrict movement along each axis within given ranges.

**LIMIT_ROTATION:**

Limit Rotation.

Restrict rotation along each axis within given ranges.

**LIMIT_SCALE:**

Limit Scale.

Restrict scaling along each axis with given ranges.

**MAINTAIN_VOLUME:**

Maintain Volume.

Compensate for scaling one axis by applying suitable scaling to the other two axes.

**TRANSFORM:**

Transformation.

Use one transform property from target to control another (or same) property on owner.

**TRANSFORM_CACHE:**

Transform Cache.

Look up the transformation matrix from an external file.

**Tracking**

**CLAMP_TO:**

Clamp To.

Restrict movements to lie along a curve by remapping location along curve’s longest axis.

**DAMPED_TRACK:**

Damped Track.

Point towards a target by performing the smallest rotation necessary.

**IK:**

Inverse Kinematics.

Control a chain of bones by specifying the endpoint target (Bones only).

**LOCKED_TRACK:**

Locked Track.

Rotate around the specified (‘locked’) axis to point towards a target.

**SPLINE_IK:**

Spline IK.

Align chain of bones along a curve (Bones only).

**STRETCH_TO:**

Stretch To.

Stretch along Y-Axis to point towards a target.

**TRACK_TO:**

Track To.

Legacy tracking constraint prone to twisting artifacts.

**Relationship**

**ACTION:**

Action.

Use transform property of target to look up pose for owner from an Action.

**ARMATURE:**

Armature.

Apply weight-blended transformation from multiple bones like the Armature modifier.

**CHILD_OF:**

Child Of.

Make target the ‘detachable’ parent of owner.

**FLOOR:**

Floor.

Use position (and optionally rotation) of target to define a ‘wall’ or ‘floor’ that the owner cannot cross.

**FOLLOW_PATH:**

Follow Path.

Use to animate an object/bone following a path.

**GEOMETRY_ATTRIBUTE:**

Geometry Attribute.

Retrieve transform from target geometry attribute data.

**PIVOT:**

Pivot.

Change pivot point for transforms (buggy).

**SHRINKWRAP:**

Shrinkwrap.

Restrict movements to surface of target mesh.
