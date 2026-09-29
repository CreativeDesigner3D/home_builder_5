<!-- source: Blender Python API reference 5.2 / bpy.ops.export_scene.html -->

<a id="module-bpy.ops.export_scene"></a>

# Export Scene Operators

<a id="bpy.ops.export_scene.fbx"></a>

### bpy.ops.export_scene.fbx(*, filepath='', check_existing=True, filter_glob='*.fbx', use_selection=False, use_visible=False, use_active_collection=False, collection='', global_scale=1.0, apply_unit_scale=True, apply_scale_options='FBX_SCALE_NONE', use_space_transform=True, bake_space_transform=False, object_types={'ARMATURE', 'CAMERA', 'EMPTY', 'LIGHT', 'MESH', 'OTHER'}, use_mesh_modifiers=True, use_mesh_modifiers_render=True, mesh_smooth_type='OFF', colors_type='SRGB', prioritize_active_color=False, use_subsurf=False, use_mesh_edges=False, use_tspace=False, use_triangles=False, use_custom_props=False, add_leaf_bones=True, primary_bone_axis='Y', secondary_bone_axis='X', use_armature_deform_only=False, armature_nodetype='NULL', bake_anim=True, bake_anim_use_all_bones=True, bake_anim_use_nla_strips=True, bake_anim_use_all_actions=True, bake_anim_force_startend_keying=True, bake_anim_step=1.0, bake_anim_simplify_factor=1.0, path_mode='AUTO', embed_textures=False, batch_mode='OFF', use_batch_own_dir=True, use_metadata=True, axis_forward='-Z', axis_up='Y')

Write a FBX file

**Parameters:**

- **filepath** (str) – File Path, Filepath used for exporting the file (optional, never None)
- **check_existing** (bool) – Check Existing, Check and warn on overwriting existing files (optional)
- **filter_glob** (str) – filter_glob, (optional, never None)
- **use_selection** (bool) – Selected Objects, Export selected and visible objects only (optional)
- **use_visible** (bool) – Visible Objects, Export visible objects only (optional)
- **use_active_collection** (bool) – Active Collection, Export only objects from the active collection (and its children) (optional)
- **collection** (str) – Source Collection, Export only objects from this collection (and its children) (optional, never None)
- **global_scale** (float) – Scale, Scale all data (Some importers do not support scaled armatures!) (in [0.001, 1000], optional)
- **apply_unit_scale** (bool) – Apply Unit, Take into account current Blender units settings (if unset, raw Blender Units values are used as-is) (optional)
- **apply_scale_options** (Literal['FBX_SCALE_NONE', 'FBX_SCALE_UNITS', 'FBX_SCALE_CUSTOM', 'FBX_SCALE_ALL']) –

  Apply Scalings, How to apply custom and units scalings in generated FBX file (Blender uses FBX scale to detect units on import, but many other applications do not handle the same way) (optional)

  - `FBX_SCALE_NONE`
    All Local – Apply custom scaling and units scaling to each object transformation, FBX scale remains at 1.0.
  - `FBX_SCALE_UNITS`
    FBX Units Scale – Apply custom scaling to each object transformation, and units scaling to FBX scale.
  - `FBX_SCALE_CUSTOM`
    FBX Custom Scale – Apply custom scaling to FBX scale, and units scaling to each object transformation.
  - `FBX_SCALE_ALL`
    FBX All – Apply custom scaling and units scaling to FBX scale.
- **use_space_transform** (bool) – Use Space Transform, Apply global space transform to the object rotations. When disabled only the axis space is written to the file and all object transforms are left as-is (optional)
- **bake_space_transform** (bool) – Apply Transform, Bake space transform into object data, avoids getting unwanted rotations to objects when target space is not aligned with Blender’s space (WARNING! experimental option, use at own risk, known to be broken with armatures/animations) (optional)
- **object_types** (set[Literal['EMPTY', 'CAMERA', 'LIGHT', 'ARMATURE', 'MESH', 'OTHER']]) –

  Object Types, Which kind of object to export (optional)

  - `EMPTY`
    Empty.
  - `CAMERA`
    Camera.
  - `LIGHT`
    Lamp.
  - `ARMATURE`
    Armature – WARNING: not supported in dupli/group instances.
  - `MESH`
    Mesh.
  - `OTHER`
    Other – Other geometry types, like curve, meta-ball, etc. (converted to meshes).
- **use_mesh_modifiers** (bool) – Apply Modifiers, Apply modifiers to mesh objects (except Armature ones) - WARNING: prevents exporting shape keys (optional)
- **use_mesh_modifiers_render** (bool) – Use Modifiers Render Setting, Use render settings when applying modifiers to mesh objects (DISABLED in Blender 2.8) (optional)
- **mesh_smooth_type** (Literal['OFF', 'FACE', 'EDGE', 'SMOOTH_GROUP']) –

  Smoothing, Export smoothing information (prefer ‘Normals Only’ option if your target importer understands custom normals) (optional)

  - `OFF`
    Normals Only – Export only normals instead of writing edge or face smoothing data.
  - `FACE`
    Face – Write face smoothing.
  - `EDGE`
    Edge – Write edge smoothing.
  - `SMOOTH_GROUP`
    Smoothing Groups – Write face smoothing groups.
- **colors_type** (Literal['NONE', 'SRGB', 'LINEAR']) –

  Vertex Colors, Export vertex color attributes (optional)

  - `NONE`
    None – Do not export color attributes.
  - `SRGB`
    sRGB – Export colors in sRGB color space.
  - `LINEAR`
    Linear – Export colors in linear color space.
- **prioritize_active_color** (bool) – Prioritize Active Color, Make sure active color will be exported first. Could be important since some other software can discard other color attributes besides the first one (optional)
- **use_subsurf** (bool) – Export Subdivision Surface, Export the last Catmull-Rom subdivision modifier as FBX subdivision (does not apply the modifier even if ‘Apply Modifiers’ is enabled) (optional)
- **use_mesh_edges** (bool) – Loose Edges, Export loose edges (as two-vertices polygons) (optional)
- **use_tspace** (bool) – Tangent Space, Add binormal and tangent vectors, together with normal they form the tangent space (will only work correctly with tris/quads only meshes!) (optional)
- **use_triangles** (bool) – Triangulate Faces, Convert all faces to triangles (optional)
- **use_custom_props** (bool) – Custom Properties, Export custom properties (optional)
- **add_leaf_bones** (bool) – Add Leaf Bones, Append a final bone to the end of each chain to specify last bone length (use this when you intend to edit the armature from exported data) (optional)
- **primary_bone_axis** (Literal['X', 'Y', 'Z', '-X', '-Y', '-Z']) – Primary Bone Axis, (optional)
- **secondary_bone_axis** (Literal['X', 'Y', 'Z', '-X', '-Y', '-Z']) – Secondary Bone Axis, (optional)
- **use_armature_deform_only** (bool) – Only Deform Bones, Only write deforming bones (and non-deforming ones when they have deforming children) (optional)
- **armature_nodetype** (Literal['NULL', 'ROOT', 'LIMBNODE']) –

  Armature FBXNode Type, FBX type of node (object) used to represent Blender’s armatures (use the Null type unless you experience issues with the other app, as other choices may not import back perfectly into Blender…) (optional)

  - `NULL`
    Null – ‘Null’ FBX node, similar to Blender’s Empty (default).
  - `ROOT`
    Root – ‘Root’ FBX node, supposed to be the root of chains of bones….
  - `LIMBNODE`
    LimbNode – ‘LimbNode’ FBX node, a regular joint between two bones….
- **bake_anim** (bool) – Baked Animation, Export baked keyframe animation (optional)
- **bake_anim_use_all_bones** (bool) – Key All Bones, Force exporting at least one key of animation for all bones (needed with some target applications, like UE4) (optional)
- **bake_anim_use_nla_strips** (bool) – NLA Strips, Export each non-muted NLA strip as a separated FBX’s AnimStack, if any, instead of global scene animation (optional)
- **bake_anim_use_all_actions** (bool) – All Actions, Export each action as a separated FBX’s AnimStack, instead of global scene animation (note that animated objects will get all actions compatible with them, others will get no animation at all) (optional)
- **bake_anim_force_startend_keying** (bool) – Force Start/End Keying, Always add a keyframe at start and end of actions for animated channels (optional)
- **bake_anim_step** (float) – Sampling Rate, How often to evaluate animated values (in frames) (in [0.01, 100], optional)
- **bake_anim_simplify_factor** (float) – Simplify, How much to simplify baked values (0.0 to disable, the higher the more simplified) (in [0, 100], optional)
- **path_mode** (Literal['AUTO', 'ABSOLUTE', 'RELATIVE', 'MATCH', 'STRIP', 'COPY']) –

  Path Mode, Method used to reference paths (optional)

  - `AUTO`
    Auto – Use relative paths with subdirectories only.
  - `ABSOLUTE`
    Absolute – Always write absolute paths.
  - `RELATIVE`
    Relative – Write relative paths where possible.
  - `MATCH`
    Match – Match absolute/relative setting with input path.
  - `STRIP`
    Strip – Filename only.
  - `COPY`
    Copy – Copy the file to the destination path (or subdirectory).
- **embed_textures** (bool) – Embed Textures, Embed textures in FBX binary file (only for “Copy” path mode!) (optional)
- **batch_mode** (Literal['OFF', 'SCENE', 'COLLECTION', 'SCENE_COLLECTION', 'ACTIVE_SCENE_COLLECTION']) –

  Batch Mode, (optional)

  - `OFF`
    Off – Active scene to file.
  - `SCENE`
    Scene – Each scene as a file.
  - `COLLECTION`
    Collection – Each collection (data-block ones) as a file, does not include content of children collections.
  - `SCENE_COLLECTION`
    Scene Collections – Each collection (including master, non-data-block ones) of each scene as a file, including content from children collections.
  - `ACTIVE_SCENE_COLLECTION`
    Active Scene Collections – Each collection (including master, non-data-block one) of the active scene as a file, including content from children collections.
- **use_batch_own_dir** (bool) – Batch Own Dir, Create a dir for each exported file (optional)
- **use_metadata** (bool) – Use Metadata, (optional)
- **axis_forward** (Literal['X', 'Y', 'Z', '-X', '-Y', '-Z']) – Forward, (optional)
- **axis_up** (Literal['X', 'Y', 'Z', '-X', '-Y', '-Z']) – Up, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[addons_core/io_scene_fbx/__init__.py:604](https://projects.blender.org/blender/blender/src/branch/main/scripts/addons_core/io_scene_fbx/__init__.py#L604)

<a id="bpy.ops.export_scene.gltf"></a>

### bpy.ops.export_scene.gltf(*, filepath='', check_existing=True, export_import_convert_lighting_mode='SPEC', gltf_export_id='', export_use_gltfpack=False, export_gltfpack_tc=True, export_gltfpack_tq=8, export_gltfpack_si=1.0, export_gltfpack_sa=False, export_gltfpack_slb=False, export_gltfpack_vp=14, export_gltfpack_vt=12, export_gltfpack_vn=8, export_gltfpack_vc=8, export_gltfpack_vpi='Integer', export_gltfpack_noq=True, export_gltfpack_kn=False, export_format='', ui_tab='GENERAL', export_copyright='', export_image_format='AUTO', export_image_add_webp=False, export_image_webp_fallback=False, export_texture_dir='', export_jpeg_quality=75, export_image_quality=75, export_keep_originals=False, export_texcoords=True, export_normals=True, export_gn_mesh=False, export_meshopt_compression_enable=False, export_meshopt_extension='EXT_meshopt_compression', export_draco_mesh_compression_enable=False, export_draco_mesh_compression_level=6, export_draco_position_quantization=14, export_draco_normal_quantization=10, export_draco_texcoord_quantization=12, export_draco_color_quantization=10, export_draco_generic_quantization=12, export_tangents=False, export_materials='EXPORT', export_unused_images=False, export_unused_textures=False, export_vertex_color='MATERIAL', export_vertex_color_name='Color', export_all_vertex_colors=True, export_active_vertex_color_when_no_material=True, export_attributes=False, use_mesh_edges=False, use_mesh_vertices=False, export_cameras=False, use_selection=False, use_visible=False, use_renderable=False, use_active_collection_with_nested=True, use_active_collection=False, use_active_scene=False, collection='', at_collection_center=False, export_extras=False, export_yup=True, export_apply=False, export_shared_accessors=False, export_animations=True, export_frame_range=False, export_frame_step=1, export_force_sampling=True, export_sampling_interpolation_fallback='LINEAR', export_pointer_animation=False, export_animation_mode='ACTIONS', export_nla_strips_merged_animation_name='Animation', export_def_bones=False, export_hierarchy_flatten_bones=False, export_hierarchy_flatten_objs=False, export_armature_object_remove=False, export_leaf_bone=False, export_optimize_animation_size=True, export_optimize_animation_keep_anim_armature=True, export_optimize_animation_keep_anim_object=False, export_optimize_disable_viewport=False, export_negative_frame='SLIDE', export_anim_slide_to_zero=False, export_bake_animation=False, export_merge_animation='ACTION', export_anim_single_armature=True, export_reset_pose_bones=True, export_current_frame=False, export_rest_position_armature=True, export_anim_scene_split_object=True, export_skins=True, export_influence_nb=4, export_all_influences=False, export_morph=True, export_morph_normal=True, export_morph_tangent=False, export_morph_animation=True, export_morph_reset_sk_data=True, export_lights=False, export_try_sparse_sk=True, export_try_omit_sparse_sk=False, export_gpu_instances=False, export_action_filter=False, export_convert_animation_pointer=False, export_nla_strips=True, export_original_specular=False, will_save_settings=False, export_hierarchy_full_collections=False, export_extra_animations=False, export_loglevel=-1, filter_glob='*.glb')

Export scene as glTF 2.0 file

**Parameters:**

- **filepath** (str) – File Path, Filepath used for exporting the file (optional, never None)
- **check_existing** (bool) – Check Existing, Check and warn on overwriting existing files (optional)
- **export_import_convert_lighting_mode** (Literal['SPEC', 'COMPAT', 'RAW']) –

  Lighting Mode, Optional backwards compatibility for non-standard render engines. Applies to lights (optional)

  - `SPEC`
    Standard – Physically-based glTF lighting units (cd, lx, nt).
  - `COMPAT`
    Unitless – Non-physical, unitless lighting. Useful when exposure controls are not available.
  - `RAW`
    Raw (Deprecated) – Blender lighting strengths with no conversion.
- **gltf_export_id** (str) – Identifier, Identifier of caller (in case of add-on calling this exporter). Can be useful in case of Extension added by other add-ons (optional, never None)
- **export_use_gltfpack** (bool) – Use Gltfpack, Use gltfpack to simplify the mesh and/or compress its textures (optional)
- **export_gltfpack_tc** (bool) – KTX2 Compression, Convert all textures to KTX2 with BasisU supercompression (optional)
- **export_gltfpack_tq** (int) – Texture Encoding Quality, Texture encoding quality (in [1, 10], optional)
- **export_gltfpack_si** (float) – Mesh Simplification Ratio, Simplify meshes targeting triangle count ratio (in [0, 1], optional)
- **export_gltfpack_sa** (bool) – Aggressive Mesh Simplification, Aggressively simplify to the target ratio disregarding quality (optional)
- **export_gltfpack_slb** (bool) – Lock Mesh Border Vertices, Lock border vertices during simplification to avoid gaps on connected meshes (optional)
- **export_gltfpack_vp** (int) – Position Quantization, Use N-bit quantization for positions (in [1, 16], optional)
- **export_gltfpack_vt** (int) – Texture Coordinate Quantization, Use N-bit quantization for texture coordinates (in [1, 16], optional)
- **export_gltfpack_vn** (int) – Normal/Tangent Quantization, Use N-bit quantization for normals and tangents (in [1, 16], optional)
- **export_gltfpack_vc** (int) – Vertex Color Quantization, Use N-bit quantization for colors (in [1, 16], optional)
- **export_gltfpack_vpi** (Literal['Integer', 'Normalized', 'Floating-point']) –

  Vertex Position Attributes, Type to use for vertex position attributes (optional)

  - `Integer`
    Integer – Use integer attributes for positions.
  - `Normalized`
    Normalized – Use normalized attributes for positions.
  - `Floating-point`
    Floating-point – Use floating-point attributes for positions.
- **export_gltfpack_noq** (bool) – Disable Quantization, Disable quantization; produces much larger glTF files with no extensions (optional)
- **export_gltfpack_kn** (bool) – Keep Named Nodes, Restrict some optimization to keep named nodes and meshes attached to named nodes so that named nodes can be transformed externally (optional)
- **export_format** (str) – Format, Output format. Binary is most efficient, but JSON may be easier to edit later (optional)
- **ui_tab** (Literal['GENERAL', 'MESHES', 'OBJECTS', 'ANIMATION']) –

  ui_tab, Export setting categories (optional)

  - `GENERAL`
    General – General settings.
  - `MESHES`
    Meshes – Mesh settings.
  - `OBJECTS`
    Objects – Object settings.
  - `ANIMATION`
    Animation – Animation settings.
- **export_copyright** (str) – Copyright, Legal rights and conditions for the model (optional, never None)
- **export_image_format** (Literal['AUTO', 'JPEG', 'WEBP', 'NONE']) –

  Images, Output format for images. PNG is lossless and generally preferred, but JPEG might be preferable for web applications due to the smaller file size. Alternatively they can be omitted if they are not needed (optional)

  - `AUTO`
    Automatic – Save PNGs as PNGs, JPEGs as JPEGs, WebPs as WebPs. For other formats, use PNG.
  - `JPEG`
    JPEG Format (.jpg) – Save images as JPEGs. (Images that need alpha are saved as PNGs though.) Be aware of a possible loss in quality.
  - `WEBP`
    WebP Format – Save images as WebPs as main image (no fallback).
  - `NONE`
    None – Don’t export images.
- **export_image_add_webp** (bool) – Create WebP, Creates WebP textures for every texture. For already WebP textures, nothing happens (optional)
- **export_image_webp_fallback** (bool) – WebP Fallback, For all WebP textures, create a PNG fallback texture (optional)
- **export_texture_dir** (str) – Textures, Folder to place texture files in. Relative to the .gltf file (optional, never None)
- **export_jpeg_quality** (int) – JPEG Quality, Quality of JPEG export (in [0, 100], optional)
- **export_image_quality** (int) – Image Quality, Quality of image export (in [0, 100], optional)
- **export_keep_originals** (bool) – Keep Original, Keep original textures files if possible. WARNING: if you use more than one texture, where pbr standard requires only one, only one texture will be used. This can lead to unexpected results (optional)
- **export_texcoords** (bool) – UVs, Export UVs (texture coordinates) with meshes (optional)
- **export_normals** (bool) – Normals, Export vertex normals with meshes (optional)
- **export_gn_mesh** (bool) – Geometry Nodes Instances (Experimental), Export Geometry nodes instance meshes (optional)
- **export_meshopt_compression_enable** (bool) – Meshopt Compression, Compress mesh using Meshopt (optional)
- **export_meshopt_extension** (Literal['EXT_meshopt_compression', 'KHR_meshopt_compression']) –

  Meshopt Extension, Extension to use for meshopt compression (optional)

  - `EXT_meshopt_compression`
    EXT_meshopt_compression – Use EXT_meshopt_compression extension for mesh compression.
  - `KHR_meshopt_compression`
    KHR_meshopt_compression – Use KHR_meshopt_compression extension for mesh compression.
- **export_draco_mesh_compression_enable** (bool) – Draco Mesh Compression, Compress mesh using Draco (optional)
- **export_draco_mesh_compression_level** (int) – Compression Level, Compression level (0 = most speed, 6 = most compression, higher values currently not supported) (in [0, 10], optional)
- **export_draco_position_quantization** (int) – Position Quantization Bits, Quantization bits for position values (0 = no quantization) (in [0, 30], optional)
- **export_draco_normal_quantization** (int) – Normal Quantization Bits, Quantization bits for normal values (0 = no quantization) (in [0, 30], optional)
- **export_draco_texcoord_quantization** (int) – Texcoord Quantization Bits, Quantization bits for texture coordinate values (0 = no quantization) (in [0, 30], optional)
- **export_draco_color_quantization** (int) – Color Quantization Bits, Quantization bits for color values (0 = no quantization) (in [0, 30], optional)
- **export_draco_generic_quantization** (int) – Generic Quantization Bits, Quantization bits for generic values like weights or joints (0 = no quantization) (in [0, 30], optional)
- **export_tangents** (bool) – Tangents, Export vertex tangents with meshes (optional)
- **export_materials** (Literal['EXPORT', 'PLACEHOLDER', 'VIEWPORT', 'NONE']) –

  Materials, Export materials (optional)

  - `EXPORT`
    Export – Export all materials used by included objects.
  - `PLACEHOLDER`
    Placeholder – Do not export materials, but write multiple primitive groups per mesh, keeping material slot information.
  - `VIEWPORT`
    Viewport – Export minimal materials as defined in Viewport display properties.
  - `NONE`
    No export – Do not export materials, and combine mesh primitive groups, losing material slot information.
- **export_unused_images** (bool) – Unused Images, Export images not assigned to any material (optional)
- **export_unused_textures** (bool) – Prepare Unused Textures, Export image texture nodes not assigned to any material. This feature is not standard and needs an external extension to be included in the glTF file (optional)
- **export_vertex_color** (Literal['MATERIAL', 'ACTIVE', 'NAME', 'NONE']) –

  Use Vertex Color, How to export vertex color (optional)

  - `MATERIAL`
    Material – Export vertex color when used by material.
  - `ACTIVE`
    Active – Export active vertex color.
  - `NAME`
    Name – Export vertex color with this name.
  - `NONE`
    None – Do not export vertex color.
- **export_vertex_color_name** (str) – Vertex Color Name, Name of vertex color to export (optional, never None)
- **export_all_vertex_colors** (bool) – Export All Vertex Colors, Export all vertex colors, even if not used by any material. If no Vertex Color is used in the mesh materials, a fake COLOR_0 will be created, in order to keep material unchanged (optional)
- **export_active_vertex_color_when_no_material** (bool) – Export Active Vertex Color When No Material, When there is no material on object, export active vertex color (optional)
- **export_attributes** (bool) – Attributes, Export Attributes (when starting with underscore) (optional)
- **use_mesh_edges** (bool) – Loose Edges, Export loose edges as lines, using the material from the first material slot (optional)
- **use_mesh_vertices** (bool) – Loose Points, Export loose points as glTF points, using the material from the first material slot (optional)
- **export_cameras** (bool) – Cameras, Export cameras (optional)
- **use_selection** (bool) – Selected Objects, Export selected objects only (optional)
- **use_visible** (bool) – Visible Objects, Export visible objects only (optional)
- **use_renderable** (bool) – Renderable Objects, Export renderable objects only (optional)
- **use_active_collection_with_nested** (bool) – Include Nested Collections, Include active collection and nested collections (optional)
- **use_active_collection** (bool) – Active Collection, Export objects in the active collection only (optional)
- **use_active_scene** (bool) – Active Scene, Export active scene only (optional)
- **collection** (str) – Source Collection, Export only objects from this collection (and its children) (optional, never None)
- **at_collection_center** (bool) – Export at Collection Center, Export at Collection center of mass of root objects of the collection (optional)
- **export_extras** (bool) – Custom Properties, Export custom properties as glTF extras (optional)
- **export_yup** (bool) – +Y Up, Export using glTF convention, +Y up (optional)
- **export_apply** (bool) – Apply Modifiers, Apply modifiers (excluding Armatures) to mesh objects -WARNING: prevents exporting shape keys (optional)
- **export_shared_accessors** (bool) – Shared Accessors, Export Primitives using shared accessors for attributes (optional)
- **export_animations** (bool) – Animations, Exports active actions and NLA tracks as glTF animations (optional)
- **export_frame_range** (bool) – Limit to Playback Range, Clips animations to selected playback range (optional)
- **export_frame_step** (int) – Sampling Rate, How often to evaluate animated values (in frames) (in [1, 120], optional)
- **export_force_sampling** (bool) – Always Sample Animations, Apply sampling to all animations (optional)
- **export_sampling_interpolation_fallback** (Literal['LINEAR', 'STEP']) –

  Sampling Interpolation Fallback, Interpolation fallback for sampled animations, when the property is not keyed (optional)

  - `LINEAR`
    Linear – Linear interpolation between keyframes.
  - `STEP`
    Step – No interpolation between keyframes.
- **export_pointer_animation** (bool) – Export Animation Pointer (Experimental), Export material, Light & Camera animation as Animation Pointer. Available only for baked animation mode ‘NLA Tracks’ and ‘Scene’ (optional)
- **export_animation_mode** (Literal['ACTIONS', 'ACTIVE_ACTIONS', 'BROADCAST', 'NLA_TRACKS', 'SCENE']) –

  Animation Mode, Export Animation mode (optional)

  - `ACTIONS`
    Actions – Export actions (actives and on NLA tracks) as separate animations.
  - `ACTIVE_ACTIONS`
    Active actions merged – All the currently assigned actions become one glTF animation.
  - `BROADCAST`
    Broadcast actions – Broadcast all compatible actions to all objects. Animated objects will get all actions compatible with them, others will get no animation at all.
  - `NLA_TRACKS`
    NLA Tracks – Export individual NLA Tracks as separate animation.
  - `SCENE`
    Scene – Export baked scene as a single animation.
- **export_nla_strips_merged_animation_name** (str) – Merged Animation Name, Name of single glTF animation to be exported (optional, never None)
- **export_def_bones** (bool) – Export Deformation Bones Only, Export Deformation bones only (optional)
- **export_hierarchy_flatten_bones** (bool) – Flatten Bone Hierarchy, Flatten Bone Hierarchy. Useful in case of non decomposable transformation matrix (optional)
- **export_hierarchy_flatten_objs** (bool) – Flatten Object Hierarchy, Flatten Object Hierarchy. Useful in case of non decomposable transformation matrix (optional)
- **export_armature_object_remove** (bool) – Remove Armature Object, Remove Armature object if possible. If Armature has multiple root bones, object will not be removed (optional)
- **export_leaf_bone** (bool) – Add Leaf Bones, Append a final bone to the end of each chain to specify last bone length (use this when you intend to edit the armature from exported data) (optional)
- **export_optimize_animation_size** (bool) – Optimize Animation Size, Reduce exported file size by removing duplicate keyframes (optional)
- **export_optimize_animation_keep_anim_armature** (bool) – Force Keeping Channels for Bones, If all keyframes are identical in a rig, force keeping the minimal animation. When off, all possible channels for the bones will be exported, even if empty (minimal animation, 2 keyframes) (optional)
- **export_optimize_animation_keep_anim_object** (bool) – Force Keeping Channel for Objects, If all keyframes are identical for object transformations, force keeping the minimal animation (optional)
- **export_optimize_disable_viewport** (bool) – Disable Viewport for Other Objects, When exporting animations, disable viewport for other objects, for performance (optional)
- **export_negative_frame** (Literal['SLIDE', 'CROP']) –

  Negative Frames, Negative Frames are slid or cropped (optional)

  - `SLIDE`
    Slide – Slide animation to start at frame 0.
  - `CROP`
    Crop – Keep only frames above frame 0.
- **export_anim_slide_to_zero** (bool) – Set All glTF Animation Starting at 0, Set all glTF animation starting at 0.0s. Can be useful for looping animations (optional)
- **export_bake_animation** (bool) – Bake All Objects Animations, Force exporting animation on every object. Can be useful when using constraints or driver. Also useful when exporting only selection (optional)
- **export_merge_animation** (Literal['NLA_TRACK', 'ACTION', 'NONE']) –

  Merge Animation, Merge Animations (optional)

  - `NLA_TRACK`
    NLA Track Names – Merge by NLA Track Names.
  - `ACTION`
    Actions – Merge by Actions.
  - `NONE`
    No Merge – Do Not Merge Animations.
- **export_anim_single_armature** (bool) – Export all Armature Actions, Export all actions, bound to a single armature. WARNING: Option does not support exports including multiple armatures (optional)
- **export_reset_pose_bones** (bool) – Reset Pose Bones Between Actions, Reset pose bones between each action exported. This is needed when some bones are not keyed on some animations (optional)
- **export_current_frame** (bool) – Use Current Frame as Object Rest Transformations, Export the scene in the current animation frame. When off, frame 0 is used as rest transformations for objects (optional)
- **export_rest_position_armature** (bool) – Use Rest Position Armature, Export armatures using rest position as joints’ rest pose. When off, current frame pose is used as rest pose (optional)
- **export_anim_scene_split_object** (bool) – Split Animation by Object, Export Scene as seen in Viewport, But split animation by Object (optional)
- **export_skins** (bool) – Skinning, Export skinning (armature) data (optional)
- **export_influence_nb** (int) – Bone Influences, Choose how many Bone influences to export (in [1, inf], optional)
- **export_all_influences** (bool) – Include All Bone Influences, Allow export of all joint vertex influences. Models may appear incorrectly in many viewers (optional)
- **export_morph** (bool) – Shape Keys, Export shape keys (morph targets) (optional)
- **export_morph_normal** (bool) – Shape Key Normals, Export vertex normals with shape keys (morph targets) (optional)
- **export_morph_tangent** (bool) – Shape Key Tangents, Export vertex tangents with shape keys (morph targets) (optional)
- **export_morph_animation** (bool) – Shape Key Animations, Export shape keys animations (morph targets) (optional)
- **export_morph_reset_sk_data** (bool) – Reset Shape Keys Between Actions, Reset shape keys between each action exported. This is needed when some SK channels are not keyed on some animations (optional)
- **export_lights** (bool) – Punctual Lights, Export directional, point, and spot lights. Uses “KHR_lights_punctual” glTF extension (optional)
- **export_try_sparse_sk** (bool) – Use Sparse Accessor if Better, Try using Sparse Accessor if it saves space (optional)
- **export_try_omit_sparse_sk** (bool) – Omitting Sparse Accessor if Data is Empty, Omitting Sparse Accessor if data is empty (optional)
- **export_gpu_instances** (bool) – GPU Instances, Export using EXT_mesh_gpu_instancing. Limited to children of a given Empty. Multiple materials might be omitted (optional)
- **export_action_filter** (bool) – Filter Actions, Filter Actions to be exported (optional)
- **export_convert_animation_pointer** (bool) – Convert TRS/Weights to Animation Pointer, Export TRS and weights as Animation Pointer. Using KHR_animation_pointer extension (optional)
- **export_nla_strips** (bool) – Group by NLA Track, When on, multiple actions become part of the same glTF animation if they’re pushed onto NLA tracks with the same name. When off, all the currently assigned actions become one glTF animation (optional)
- **export_original_specular** (bool) – Export Original PBR Specular, Export original glTF PBR Specular, instead of Blender Principled Shader Specular (optional)
- **will_save_settings** (bool) – Remember Export Settings, Store glTF export settings in the Blender project (optional)
- **export_hierarchy_full_collections** (bool) – Full Collection Hierarchy, Export full hierarchy, including intermediate collections (optional)
- **export_extra_animations** (bool) – Prepare Extra Animations, Export additional animations.This feature is not standard and needs an external extension to be included in the glTF file(optional)
- **export_loglevel** (int) – Log Level, Log Level (in [-inf, inf], optional)
- **filter_glob** (str) – filter_glob, (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[addons_core/io_scene_gltf2/__init__.py:1115](https://projects.blender.org/blender/blender/src/branch/main/scripts/addons_core/io_scene_gltf2/__init__.py#L1115)
