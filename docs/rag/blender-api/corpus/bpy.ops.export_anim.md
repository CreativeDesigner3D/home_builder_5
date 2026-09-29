<!-- source: Blender Python API reference 5.2 / bpy.ops.export_anim.html -->

<a id="module-bpy.ops.export_anim"></a>

# Export Anim Operators

<a id="bpy.ops.export_anim.bvh"></a>

### bpy.ops.export_anim.bvh(*, filepath='', check_existing=True, filter_glob='*.bvh', global_scale=1.0, frame_start=0, frame_end=0, rotate_mode='NATIVE', root_transform_only=False, sort_children_by_names=False)

Save a BVH motion capture file from an armature

**Parameters:**

- **filepath** (str) – File Path, Filepath used for exporting the file (optional, never None)
- **check_existing** (bool) – Check Existing, Check and warn on overwriting existing files (optional)
- **filter_glob** (str) – filter_glob, (optional, never None)
- **global_scale** (float) – Scale, Scale the BVH by this value (in [0.0001, 1e+06], optional)
- **frame_start** (int) – Start Frame, Starting frame to export (in [-inf, inf], optional)
- **frame_end** (int) – End Frame, End frame to export (in [-inf, inf], optional)
- **rotate_mode** (Literal['NATIVE', 'XYZ', 'XZY', 'YXZ', 'YZX', 'ZXY', 'ZYX']) –

  Rotation, Rotation conversion (optional)

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
- **root_transform_only** (bool) – Root Translation Only, Only write out translation channels for the root bone (optional)
- **sort_children_by_names** (bool) – Sort Children By Name, Sort the children of each bone alphabetically (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[addons_core/io_anim_bvh/__init__.py:286](https://projects.blender.org/blender/blender/src/branch/main/scripts/addons_core/io_anim_bvh/__init__.py#L286)
