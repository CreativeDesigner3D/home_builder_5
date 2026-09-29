<!-- source: Blender Python API reference 5.2 / bpy.ops.import_anim.html -->

<a id="module-bpy.ops.import_anim"></a>

# Import Anim Operators

<a id="bpy.ops.import_anim.bvh"></a>

### bpy.ops.import_anim.bvh(*, filepath='', filter_glob='*.bvh', target='ARMATURE', global_scale=1.0, frame_start=1, use_fps_scale=False, update_scene_fps=False, update_scene_duration=False, use_cyclic=False, rotate_mode='NATIVE', axis_forward='-Z', axis_up='Y')

Load a BVH motion capture file

**Parameters:**

- **filepath** (str) – File Path, Filepath used for importing the file (optional, never None)
- **filter_glob** (str) – filter_glob, (optional, never None)
- **target** (Literal['ARMATURE', 'OBJECT']) – Target, Import target type (optional)
- **global_scale** (float) – Scale, Scale the BVH by this value (in [0.0001, 1e+06], optional)
- **frame_start** (int) – Start Frame, Starting frame for the animation (in [-inf, inf], optional)
- **use_fps_scale** (bool) – Scale FPS, Scale the frame-rate from the BVH to the current scenes, otherwise each BVH frame maps directly to a Blender frame (optional)
- **update_scene_fps** (bool) – Update Scene FPS, Set the scene frame-rate to that of the BVH file (note that this nullifies the ‘Scale FPS’ option, as the scale will be 1:1) (optional)
- **update_scene_duration** (bool) – Update Scene Duration, Extend the scene’s duration to the BVH duration (never shortens the scene) (optional)
- **use_cyclic** (bool) – Loop, Loop the animation playback (optional)
- **rotate_mode** (Literal['QUATERNION', 'NATIVE', 'XYZ', 'XZY', 'YXZ', 'YZX', 'ZXY', 'ZYX']) –

  Rotation, Rotation conversion (optional)

  - `QUATERNION`
    Quaternion – Convert rotations to quaternions.
  - `NATIVE`
    Euler (Native) – Use the rotation order defined in the BVH file.
  - `XYZ`
    Euler (XYZ) – Convert rotations to euler XYZ.
  - `XZY`
    Euler (XZY) – Convert rotations to euler XZY.
  - `YXZ`
    Euler (YXZ) – Convert rotations to euler YXZ.
  - `YZX`
    Euler (YZX) – Convert rotations to euler YZX.
  - `ZXY`
    Euler (ZXY) – Convert rotations to euler ZXY.
  - `ZYX`
    Euler (ZYX) – Convert rotations to euler ZYX.
- **axis_forward** (Literal['X', 'Y', 'Z', '-X', '-Y', '-Z']) – Forward, (optional)
- **axis_up** (Literal['X', 'Y', 'Z', '-X', '-Y', '-Z']) – Up, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[addons_core/io_anim_bvh/__init__.py:118](https://projects.blender.org/blender/blender/src/branch/main/scripts/addons_core/io_anim_bvh/__init__.py#L118)
