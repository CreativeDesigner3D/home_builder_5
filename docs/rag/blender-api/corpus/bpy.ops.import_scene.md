<!-- source: Blender Python API reference 5.2 / bpy.ops.import_scene.html -->

<a id="module-bpy.ops.import_scene"></a>

# Import Scene Operators

<a id="bpy.ops.import_scene.fbx"></a>

### bpy.ops.import_scene.fbx(*, filepath='', directory='', filter_glob='*.fbx', files=None, ui_tab='MAIN', use_manual_orientation=False, global_scale=1.0, bake_space_transform=False, use_custom_normals=True, colors_type='SRGB', use_image_search=True, use_alpha_decals=False, decal_offset=0.0, use_anim=True, anim_offset=1.0, use_subsurf=False, use_custom_props=True, use_custom_props_enum_as_string=True, ignore_leaf_bones=False, force_connect_children=False, automatic_bone_orientation=False, primary_bone_axis='Y', secondary_bone_axis='X', use_prepost_rot=True, mtl_name_collision_mode='MAKE_UNIQUE', axis_forward='-Z', axis_up='Y')

Load a FBX file

**Parameters:**

- **filepath** (str) – File Path, Filepath used for importing the file (optional, never None)
- **directory** (str) – directory, (optional, never None)
- **filter_glob** (str) – filter_glob, (optional, never None)
- **files** (`bpy_prop_collection`[`OperatorFileListElement`] | None) – File Path, (optional)
- **ui_tab** (Literal['MAIN', 'ARMATURE']) –

  ui_tab, Import options categories (optional)

  - `MAIN`
    Main – Main basic settings.
  - `ARMATURE`
    Armatures – Armature-related settings.
- **use_manual_orientation** (bool) – Manual Orientation, Specify orientation and scale, instead of using embedded data in FBX file (optional)
- **global_scale** (float) – Scale, (in [0.001, 1000], optional)
- **bake_space_transform** (bool) – Apply Transform, Bake space transform into object data, avoids getting unwanted rotations to objects when target space is not aligned with Blender’s space (WARNING! experimental option, use at own risk, known to be broken with armatures/animations) (optional)
- **use_custom_normals** (bool) – Custom Normals, Import custom normals, if available (otherwise Blender will recompute them) (optional)
- **colors_type** (Literal['NONE', 'SRGB', 'LINEAR']) –

  Vertex Colors, Import vertex color attributes (optional)

  - `NONE`
    None – Do not import color attributes.
  - `SRGB`
    sRGB – Expect file colors in sRGB color space.
  - `LINEAR`
    Linear – Expect file colors in linear color space.
- **use_image_search** (bool) – Image Search, Search subdirs for any associated images (WARNING: may be slow) (optional)
- **use_alpha_decals** (bool) – Alpha Decals, Treat materials with alpha as decals (no shadow casting) (optional)
- **decal_offset** (float) – Decal Offset, Displace geometry of alpha meshes (in [0, 1], optional)
- **use_anim** (bool) – Import Animation, Import FBX animation (optional)
- **anim_offset** (float) – Animation Offset, Offset to apply to animation during import, in frames (in [-inf, inf], optional)
- **use_subsurf** (bool) – Subdivision Data, Import FBX subdivision information as subdivision surface modifiers (optional)
- **use_custom_props** (bool) – Custom Properties, Import user properties as custom properties (optional)
- **use_custom_props_enum_as_string** (bool) – Import Enums As Strings, Store enumeration values as strings (optional)
- **ignore_leaf_bones** (bool) – Ignore Leaf Bones, Ignore the last bone at the end of each chain (used to mark the length of the previous bone) (optional)
- **force_connect_children** (bool) – Force Connect Children, Force connection of children bones to their parent, even if their computed head/tail positions do not match (can be useful with pure-joints-type armatures) (optional)
- **automatic_bone_orientation** (bool) – Automatic Bone Orientation, Try to align the major bone axis with the bone children (optional)
- **primary_bone_axis** (Literal['X', 'Y', 'Z', '-X', '-Y', '-Z']) – Primary Bone Axis, (optional)
- **secondary_bone_axis** (Literal['X', 'Y', 'Z', '-X', '-Y', '-Z']) – Secondary Bone Axis, (optional)
- **use_prepost_rot** (bool) – Use Pre/Post Rotation, Use pre/post rotation from FBX transform (you may have to disable that in some cases) (optional)
- **mtl_name_collision_mode** (Literal['MAKE_UNIQUE', 'REFERENCE_EXISTING']) –

  Material Name Collision, Behavior when the name of an imported material conflicts with an existing material (optional)

  - `MAKE_UNIQUE`
    Make Unique – Import each FBX material as a unique Blender material.
  - `REFERENCE_EXISTING`
    Reference Existing – If a material with the same name already exists, reference that instead of importing.
- **axis_forward** (Literal['X', 'Y', 'Z', '-X', '-Y', '-Z']) – Forward, (optional)
- **axis_up** (Literal['X', 'Y', 'Z', '-X', '-Y', '-Z']) – Up, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[addons_core/io_scene_fbx/__init__.py:222](https://projects.blender.org/blender/blender/src/branch/main/scripts/addons_core/io_scene_fbx/__init__.py#L222)

<a id="bpy.ops.import_scene.gltf"></a>

### bpy.ops.import_scene.gltf(*, filepath='', export_import_convert_lighting_mode='SPEC', filter_glob='*.glb;*.gltf', directory='', files=None, loglevel=0, import_pack_images=True, merge_vertices=False, import_shading='NORMALS', bone_heuristic='BLENDER', disable_bone_shape=False, bone_shape_scale_factor=1.0, guess_original_bind_pose=True, import_webp_texture=False, import_unused_materials=False, import_select_created_objects=True, import_scene_extras=True, import_scene_as_collection=True, import_merge_material_slots=True, import_point_as_pointcloud=False)

Load a glTF 2.0 file

**Parameters:**

- **filepath** (str) – File Path, Filepath used for importing the file (optional, never None)
- **export_import_convert_lighting_mode** (Literal['SPEC', 'COMPAT', 'RAW']) –

  Lighting Mode, Optional backwards compatibility for non-standard render engines. Applies to lights (optional)

  - `SPEC`
    Standard – Physically-based glTF lighting units (cd, lx, nt).
  - `COMPAT`
    Unitless – Non-physical, unitless lighting. Useful when exposure controls are not available.
  - `RAW`
    Raw (Deprecated) – Blender lighting strengths with no conversion.
- **filter_glob** (str) – filter_glob, (optional, never None)
- **directory** (str) – directory, (optional, never None)
- **files** (`bpy_prop_collection`[`OperatorFileListElement`] | None) – File Path, (optional)
- **loglevel** (int) – Log Level, Log Level (in [-inf, inf], optional)
- **import_pack_images** (bool) – Pack Images, Pack all images into .blend file (optional)
- **merge_vertices** (bool) – Merge Vertices, The glTF format requires discontinuous normals, UVs, and other vertex attributes to be stored as separate vertices, as required for rendering on typical graphics hardware. This option attempts to combine co-located vertices where possible. Currently cannot combine verts with different normals (optional)
- **import_shading** (Literal['NORMALS', 'FLAT', 'SMOOTH']) – Shading, How normals are computed during import (optional)
- **bone_heuristic** (Literal['BLENDER', 'TEMPERANCE', 'FORTUNE']) –

  Bone Dir, Heuristic for placing bones. Tries to make bones pretty (optional)

  - `BLENDER`
    Blender (best for import/export round trip) – Good for re-importing glTFs exported from Blender, and re-exporting glTFs to glTFs after Blender editing. Bone tips are placed on their local +Y axis (in glTF space).
  - `TEMPERANCE`
    Temperance (average) – Decent all-around strategy. A bone with one child has its tip placed on the local axis closest to its child.
  - `FORTUNE`
    Fortune (may look better, less accurate) – Might look better than Temperance, but also might have errors. A bone with one child has its tip placed at its child’s root. Non-uniform scalings may get messed up though, so beware.
- **disable_bone_shape** (bool) – Disable Bone Shape, Do not create bone shapes (optional)
- **bone_shape_scale_factor** (float) – Bone Shape Scale, Scale factor for bone shapes (in [-inf, inf], optional)
- **guess_original_bind_pose** (bool) – Guess Original Bind Pose, Try to guess the original bind pose for skinned meshes from the inverse bind matrices. When off, use default/rest pose as bind pose (optional)
- **import_webp_texture** (bool) – Import WebP Textures, If a texture exists in WebP format, loads the WebP texture instead of the fallback PNG/JPEG one (optional)
- **import_unused_materials** (bool) – Import Unused Materials & Images, Import materials & Images not assigned to any mesh (optional)
- **import_select_created_objects** (bool) – Select Imported Objects, Select created objects at the end of the import (optional)
- **import_scene_extras** (bool) – Import Scene Extras, Import scene extras as custom properties. Existing custom properties will be overwritten (optional)
- **import_scene_as_collection** (bool) – Import Scene as Collection, Import the scene as a collection (optional)
- **import_merge_material_slots** (bool) – Merge Material Slot when possible, Merge material slots when possible (optional)
- **import_point_as_pointcloud** (bool) – Import Points as Point Cloud, Import mesh with only POINTS primitives as Point Cloud objects (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[addons_core/io_scene_gltf2/__init__.py:2072](https://projects.blender.org/blender/blender/src/branch/main/scripts/addons_core/io_scene_gltf2/__init__.py#L2072)
