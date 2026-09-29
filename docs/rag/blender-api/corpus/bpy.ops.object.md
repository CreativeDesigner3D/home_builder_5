<!-- source: Blender Python API reference 5.2 / bpy.ops.object.html -->

<a id="module-bpy.ops.object"></a>

# Object Operators

<a id="bpy.ops.object.add"></a>

### bpy.ops.object.add(*, radius=1.0, type='EMPTY', enter_editmode=False, align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(0.0, 0.0, 0.0))

Add an object to the scene

**Parameters:**

- **radius** (float) – Radius, (in [0, inf], optional)
- **type** (Literal[[Object Type Items](bpy_types_enum_items/object_type_items.md#rna-enum-object-type-items)]) – Type, (optional)
- **enter_editmode** (bool) – Enter Edit Mode, Enter edit mode when adding this object (optional)
- **align** (Literal['WORLD', 'VIEW', 'CURSOR']) –

  Align, The alignment of the new object (optional)

  - `WORLD`
    World – Align the new object to the world.
  - `VIEW`
    View – Align the new object to the view.
  - `CURSOR`
    3D Cursor – Use the 3D cursor orientation for the new object.
- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Location for the newly added object (array of 3 items, in [-inf, inf], optional)
- **rotation** ([`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler") | Sequence[float]) – Rotation, Rotation for the newly added object (array of 3 items, in [-inf, inf], optional)
- **scale** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Scale, Scale for the newly added object (array of 3 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.add_modifier_menu"></a>

### bpy.ops.object.add_modifier_menu()

Undocumented, consider [contributing](https://developer.blender.org/).

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_ui/properties_data_modifier.py:303](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_ui/properties_data_modifier.py#L303)

<a id="bpy.ops.object.add_named"></a>

### bpy.ops.object.add_named(*, linked=False, name='', session_uid=0, matrix=((0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0)), drop_x=0, drop_y=0)

Add named object

**Parameters:**

- **linked** (bool) – Linked, Duplicate object but not object data, linking to the original data (optional)
- **name** (str) – Name, Name of the data-block to use by the operator (optional, never None)
- **session_uid** (int) – Session UID, Session UID of the data-block to use by the operator (in [-inf, inf], optional)
- **matrix** ([`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix") | Sequence[Sequence[float]]) – Matrix, (multi-dimensional array of 4 * 4 items, in [-inf, inf], optional)
- **drop_x** (int) – Drop X, X-coordinate (screen space) to place the new object under (in [-inf, inf], optional)
- **drop_y** (int) – Drop Y, Y-coordinate (screen space) to place the new object under (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.align"></a>

### bpy.ops.object.align(*, bb_quality=True, align_mode='OPT_2', relative_to='OPT_4', align_axis=set())

Align objects

**Parameters:**

- **bb_quality** (bool) – High Quality, Enables high quality but slow calculation of the bounding box for perfect results on complex shape meshes with rotation/scale (optional)
- **align_mode** (Literal['OPT_1', 'OPT_2', 'OPT_3']) – Align Mode, Side of object to use for alignment (optional)
- **relative_to** (Literal['OPT_1', 'OPT_2', 'OPT_3', 'OPT_4']) –

  Relative To, Reference location to align to (optional)

  - `OPT_1`
    Scene Origin – Use the scene origin as the position for the selected objects to align to.
  - `OPT_2`
    3D Cursor – Use the 3D cursor as the position for the selected objects to align to.
  - `OPT_3`
    Selection – Use the selected objects as the position for the selected objects to align to.
  - `OPT_4`
    Active – Use the active object as the position for the selected objects to align to.
- **align_axis** (set[Literal['X', 'Y', 'Z']]) – Align, Align to axis (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/object_align.py:386](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/object_align.py#L386)

<a id="bpy.ops.object.anim_transforms_to_deltas"></a>

### bpy.ops.object.anim_transforms_to_deltas()

Convert object animation for normal transforms to delta transforms

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/object.py:839](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/object.py#L839)

<a id="bpy.ops.object.armature_add"></a>

### bpy.ops.object.armature_add(*, radius=1.0, enter_editmode=False, align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(0.0, 0.0, 0.0))

Add an armature object to the scene

**Parameters:**

- **radius** (float) – Radius, (in [0, inf], optional)
- **enter_editmode** (bool) – Enter Edit Mode, Enter edit mode when adding this object (optional)
- **align** (Literal['WORLD', 'VIEW', 'CURSOR']) –

  Align, The alignment of the new object (optional)

  - `WORLD`
    World – Align the new object to the world.
  - `VIEW`
    View – Align the new object to the view.
  - `CURSOR`
    3D Cursor – Use the 3D cursor orientation for the new object.
- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Location for the newly added object (array of 3 items, in [-inf, inf], optional)
- **rotation** ([`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler") | Sequence[float]) – Rotation, Rotation for the newly added object (array of 3 items, in [-inf, inf], optional)
- **scale** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Scale, Scale for the newly added object (array of 3 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.assign_property_defaults"></a>

### bpy.ops.object.assign_property_defaults(*, process_data=True, process_bones=True)

Assign the current values of custom properties as their defaults, for use as part of the rest pose state in NLA track mixing

**Parameters:**

- **process_data** (bool) – Process data properties, (optional)
- **process_bones** (bool) – Process bone properties, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/object.py:1001](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/object.py#L1001)

<a id="bpy.ops.object.bake"></a>

### bpy.ops.object.bake(*, type='COMBINED', pass_filter=set(), filepath='', width=512, height=512, margin=16, margin_type='EXTEND', use_selected_to_active=False, max_ray_distance=0.0, cage_extrusion=0.0, cage_object='', normal_space='TANGENT', normal_r='POS_X', normal_g='POS_Y', normal_b='POS_Z', target='IMAGE_TEXTURES', save_mode='INTERNAL', use_clear=False, use_cage=False, use_split_materials=False, use_automatic_name=False, uv_layer='')

Bake image textures of selected objects

**Parameters:**

- **type** (Literal[[Bake Pass Type Items](bpy_types_enum_items/bake_pass_type_items.md#rna-enum-bake-pass-type-items)]) – Type, Type of pass to bake, some of them may not be supported by the current render engine (optional)
- **pass_filter** (set[Literal[[Bake Pass Filter Type Items](bpy_types_enum_items/bake_pass_filter_type_items.md#rna-enum-bake-pass-filter-type-items)]]) – Pass Filter, Filter to combined, diffuse, glossy, transmission and subsurface passes (optional)
- **filepath** (str) – File Path, Image filepath to use when saving externally (optional, never None)
- **width** (int) – Width, Horizontal dimension of the baking map (external only) (in [1, inf], optional)
- **height** (int) – Height, Vertical dimension of the baking map (external only) (in [1, inf], optional)
- **margin** (int) – Margin, Extends the baked result as a post process filter (in [0, inf], optional)
- **margin_type** (Literal[[Bake Margin Type Items](bpy_types_enum_items/bake_margin_type_items.md#rna-enum-bake-margin-type-items)]) – Margin Type, Which algorithm to use to generate the margin (optional)
- **use_selected_to_active** (bool) – Selected to Active, Bake shading on the surface of selected objects to the active object (optional)
- **max_ray_distance** (float) – Max Ray Distance, The maximum ray distance for matching points between the active and selected objects. If zero, there is no limit (in [0, inf], optional)
- **cage_extrusion** (float) – Cage Extrusion, Inflate the active object by the specified distance for baking. This helps matching to points nearer to the outside of the selected object meshes (in [0, inf], optional)
- **cage_object** (str) – Cage Object, Object to use as cage, instead of calculating the cage from the active object with cage extrusion (optional, never None)
- **normal_space** (Literal[[Normal Space Items](bpy_types_enum_items/normal_space_items.md#rna-enum-normal-space-items)]) – Normal Space, Choose normal space for baking (optional)
- **normal_r** (Literal[[Normal Swizzle Items](bpy_types_enum_items/normal_swizzle_items.md#rna-enum-normal-swizzle-items)]) – R, Axis to bake in red channel (optional)
- **normal_g** (Literal[[Normal Swizzle Items](bpy_types_enum_items/normal_swizzle_items.md#rna-enum-normal-swizzle-items)]) – G, Axis to bake in green channel (optional)
- **normal_b** (Literal[[Normal Swizzle Items](bpy_types_enum_items/normal_swizzle_items.md#rna-enum-normal-swizzle-items)]) – B, Axis to bake in blue channel (optional)
- **target** (Literal[[Bake Target Items](bpy_types_enum_items/bake_target_items.md#rna-enum-bake-target-items)]) – Target, Where to output the baked map (optional)
- **save_mode** (Literal[[Bake Save Mode Items](bpy_types_enum_items/bake_save_mode_items.md#rna-enum-bake-save-mode-items)]) – Save Mode, Where to save baked image textures (optional)
- **use_clear** (bool) – Clear, Clear images before baking (only for internal saving) (optional)
- **use_cage** (bool) – Cage, Cast rays to active object from a cage (optional)
- **use_split_materials** (bool) – Split Materials, Split baked maps per material, using material name in output file (external only) (optional)
- **use_automatic_name** (bool) – Automatic Name, Automatically name the output file with the pass type (optional)
- **uv_layer** (str) – UV Layer, UV layer to override active (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.bake_image"></a>

### bpy.ops.object.bake_image()

Bake image textures of selected objects

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.camera_add"></a>

### bpy.ops.object.camera_add(*, enter_editmode=False, align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(0.0, 0.0, 0.0))

Add a camera object to the scene

**Parameters:**

- **enter_editmode** (bool) – Enter Edit Mode, Enter edit mode when adding this object (optional)
- **align** (Literal['WORLD', 'VIEW', 'CURSOR']) –

  Align, The alignment of the new object (optional)

  - `WORLD`
    World – Align the new object to the world.
  - `VIEW`
    View – Align the new object to the view.
  - `CURSOR`
    3D Cursor – Use the 3D cursor orientation for the new object.
- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Location for the newly added object (array of 3 items, in [-inf, inf], optional)
- **rotation** ([`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler") | Sequence[float]) – Rotation, Rotation for the newly added object (array of 3 items, in [-inf, inf], optional)
- **scale** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Scale, Scale for the newly added object (array of 3 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.camera_custom_update"></a>

### bpy.ops.object.camera_custom_update()

Update custom camera with new parameters from the shader

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.clear_override_library"></a>

### bpy.ops.object.clear_override_library()

Delete the selected local overrides and relink their usages to the linked data-blocks if possible, else reset them and mark them as non editable

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.collection_add"></a>

### bpy.ops.object.collection_add()

Add an object to a new collection

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.collection_external_asset_drop"></a>

### bpy.ops.object.collection_external_asset_drop(*, session_uid=0, align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(0.0, 0.0, 0.0), use_instance=True, drop_x=0, drop_y=0, collection='')

Add the dragged collection to the scene

**Parameters:**

- **session_uid** (int) – Session UID, Session UID of the data-block to use by the operator (in [-inf, inf], optional)
- **align** (Literal['WORLD', 'VIEW', 'CURSOR']) –

  Align, The alignment of the new object (optional)

  - `WORLD`
    World – Align the new object to the world.
  - `VIEW`
    View – Align the new object to the view.
  - `CURSOR`
    3D Cursor – Use the 3D cursor orientation for the new object.
- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Location for the newly added object (array of 3 items, in [-inf, inf], optional)
- **rotation** ([`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler") | Sequence[float]) – Rotation, Rotation for the newly added object (array of 3 items, in [-inf, inf], optional)
- **scale** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Scale, Scale for the newly added object (array of 3 items, in [-inf, inf], optional)
- **use_instance** (bool) – Instance, Add the dropped collection as collection instance (optional)
- **drop_x** (int) – Drop X, X-coordinate (screen space) to place the new object under (in [-inf, inf], optional)
- **drop_y** (int) – Drop Y, Y-coordinate (screen space) to place the new object under (in [-inf, inf], optional)
- **collection** (str) – Collection, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.collection_instance_add"></a>

### bpy.ops.object.collection_instance_add(*, name='Collection', collection='', align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(0.0, 0.0, 0.0), session_uid=0, drop_x=0, drop_y=0)

Add a collection instance

**Parameters:**

- **name** (str) – Name, Collection name to add (optional, never None)
- **collection** (str) – Collection, (optional)
- **align** (Literal['WORLD', 'VIEW', 'CURSOR']) –

  Align, The alignment of the new object (optional)

  - `WORLD`
    World – Align the new object to the world.
  - `VIEW`
    View – Align the new object to the view.
  - `CURSOR`
    3D Cursor – Use the 3D cursor orientation for the new object.
- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Location for the newly added object (array of 3 items, in [-inf, inf], optional)
- **rotation** ([`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler") | Sequence[float]) – Rotation, Rotation for the newly added object (array of 3 items, in [-inf, inf], optional)
- **scale** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Scale, Scale for the newly added object (array of 3 items, in [-inf, inf], optional)
- **session_uid** (int) – Session UID, Session UID of the data-block to use by the operator (in [-inf, inf], optional)
- **drop_x** (int) – Drop X, X-coordinate (screen space) to place the new object under (in [-inf, inf], optional)
- **drop_y** (int) – Drop Y, Y-coordinate (screen space) to place the new object under (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.collection_link"></a>

### bpy.ops.object.collection_link(*, collection='')

Add an object to an existing collection

**Parameters:**

**collection** (str) – Collection, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.collection_objects_select"></a>

### bpy.ops.object.collection_objects_select()

Select all objects in collection

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.collection_remove"></a>

### bpy.ops.object.collection_remove()

Remove the active object from this collection

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.collection_unlink"></a>

### bpy.ops.object.collection_unlink()

Unlink the collection from all objects

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.constraint_add"></a>

### bpy.ops.object.constraint_add(*, type='')

Add a constraint to the active object

**Parameters:**

**type** (str) – Type, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.constraint_add_with_targets"></a>

### bpy.ops.object.constraint_add_with_targets(*, type='')

Add a constraint to the active object, with target (where applicable) set to the selected objects/bones

**Parameters:**

**type** (str) – Type, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.constraints_clear"></a>

### bpy.ops.object.constraints_clear()

Clear all constraints from the selected objects

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.constraints_copy"></a>

### bpy.ops.object.constraints_copy()

Copy constraints to other selected objects

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.convert"></a>

### bpy.ops.object.convert(*, target='MESH', keep_original=False, merge_customdata=True, thickness=5, faces=True, offset=0.01)

Convert selected objects to another type

**Parameters:**

- **target** (Literal['CURVE', 'MESH', 'POINTCLOUD', 'CURVES', 'GREASEPENCIL']) –

  Target, Type of object to convert to (optional)

  - `CURVE`
    Curve – Curve from Mesh or Text objects.
  - `MESH`
    Mesh – Mesh from Curve, Surface, Metaball, Text, or Point Cloud objects.
  - `POINTCLOUD`
    Point Cloud – Point Cloud from Mesh objects.
  - `CURVES`
    Curves – Curves from evaluated curve data.
  - `GREASEPENCIL`
    Grease Pencil – Grease Pencil from Curve or Mesh objects.
- **keep_original** (bool) – Keep Original, Keep original objects instead of replacing them (optional)
- **merge_customdata** (bool) – Merge UVs, Merge UV coordinates that share a vertex to account for imprecision in some modifiers (optional)
- **thickness** (int) – Thickness, (in [1, 100], optional)
- **faces** (bool) – Export Faces, Export faces as filled strokes (optional)
- **offset** (float) – Stroke Offset, Offset strokes from fill (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.copy_global_transform"></a>

### bpy.ops.object.copy_global_transform()

Copies the matrix of the currently active object or pose bone to the clipboard. Uses world-space matrices

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/copy_global_transform.py:150](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/copy_global_transform.py#L150)

<a id="bpy.ops.object.copy_relative_transform"></a>

### bpy.ops.object.copy_relative_transform()

Copies the matrix of the currently active object or pose bone to the clipboard. Uses matrices relative to a specific object or the active scene camera

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/copy_global_transform.py:180](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/copy_global_transform.py#L180)

<a id="bpy.ops.object.correctivesmooth_bind"></a>

### bpy.ops.object.correctivesmooth_bind(*, modifier='')

Bind base pose in Corrective Smooth modifier

**Parameters:**

**modifier** (str) – Modifier, Name of the modifier to edit (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.curves_empty_hair_add"></a>

### bpy.ops.object.curves_empty_hair_add(*, align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(0.0, 0.0, 0.0))

Add an empty curve object to the scene with the selected mesh as surface

**Parameters:**

- **align** (Literal['WORLD', 'VIEW', 'CURSOR']) –

  Align, The alignment of the new object (optional)

  - `WORLD`
    World – Align the new object to the world.
  - `VIEW`
    View – Align the new object to the view.
  - `CURSOR`
    3D Cursor – Use the 3D cursor orientation for the new object.
- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Location for the newly added object (array of 3 items, in [-inf, inf], optional)
- **rotation** ([`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler") | Sequence[float]) – Rotation, Rotation for the newly added object (array of 3 items, in [-inf, inf], optional)
- **scale** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Scale, Scale for the newly added object (array of 3 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.curves_random_add"></a>

### bpy.ops.object.curves_random_add(*, align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(0.0, 0.0, 0.0))

Add a curves object with random curves to the scene

**Parameters:**

- **align** (Literal['WORLD', 'VIEW', 'CURSOR']) –

  Align, The alignment of the new object (optional)

  - `WORLD`
    World – Align the new object to the world.
  - `VIEW`
    View – Align the new object to the view.
  - `CURSOR`
    3D Cursor – Use the 3D cursor orientation for the new object.
- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Location for the newly added object (array of 3 items, in [-inf, inf], optional)
- **rotation** ([`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler") | Sequence[float]) – Rotation, Rotation for the newly added object (array of 3 items, in [-inf, inf], optional)
- **scale** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Scale, Scale for the newly added object (array of 3 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.data_instance_add"></a>

### bpy.ops.object.data_instance_add(*, name='', session_uid=0, type='ACTION', align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(0.0, 0.0, 0.0), drop_x=0, drop_y=0)

Add an object data instance

**Parameters:**

- **name** (str) – Name, Name of the data-block to use by the operator (optional, never None)
- **session_uid** (int) – Session UID, Session UID of the data-block to use by the operator (in [-inf, inf], optional)
- **type** (Literal[[Id Type Items](bpy_types_enum_items/id_type_items.md#rna-enum-id-type-items)]) – Type, (optional)
- **align** (Literal['WORLD', 'VIEW', 'CURSOR']) –

  Align, The alignment of the new object (optional)

  - `WORLD`
    World – Align the new object to the world.
  - `VIEW`
    View – Align the new object to the view.
  - `CURSOR`
    3D Cursor – Use the 3D cursor orientation for the new object.
- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Location for the newly added object (array of 3 items, in [-inf, inf], optional)
- **rotation** ([`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler") | Sequence[float]) – Rotation, Rotation for the newly added object (array of 3 items, in [-inf, inf], optional)
- **scale** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Scale, Scale for the newly added object (array of 3 items, in [-inf, inf], optional)
- **drop_x** (int) – Drop X, X-coordinate (screen space) to place the new object under (in [-inf, inf], optional)
- **drop_y** (int) – Drop Y, Y-coordinate (screen space) to place the new object under (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.data_transfer"></a>

### bpy.ops.object.data_transfer(*, use_reverse_transfer=False, use_freeze=False, data_type='VGROUP_WEIGHTS', use_create=True, vert_mapping='NEAREST', edge_mapping='NEAREST', loop_mapping='NEAREST_POLYNOR', poly_mapping='NEAREST', use_auto_transform=False, use_object_transform=True, use_max_distance=False, max_distance=1.0, ray_radius=0.0, islands_precision=0.1, layers_select_src='ACTIVE', layers_select_dst='ACTIVE', mix_mode='REPLACE', mix_factor=1.0)

Transfer data layer(s) (weights, edge sharp, etc.) from active to selected meshes

**Parameters:**

- **use_reverse_transfer** (bool) – Reverse Transfer, Transfer from selected objects to active one (optional)
- **use_freeze** (bool) – Freeze Operator, Prevent changes to settings to re-run the operator, handy to change several things at once with heavy geometry (optional)
- **data_type** (Literal['VGROUP_WEIGHTS', 'BEVEL_WEIGHT_VERT', 'COLOR_VERTEX', 'SHARP_EDGE', 'SEAM', 'CREASE', 'BEVEL_WEIGHT_EDGE', 'FREESTYLE_EDGE', 'CUSTOM_NORMAL', 'COLOR_CORNER', 'UV', 'SMOOTH', 'FREESTYLE_FACE']) –

  Data Type, Which data to transfer (optional)

  - `VGROUP_WEIGHTS`
    Vertex Group(s) – Transfer active or all vertex groups.
  - `BEVEL_WEIGHT_VERT`
    Bevel Weight – Transfer bevel weights.
  - `COLOR_VERTEX`
    Colors – Color Attributes.
  - `SHARP_EDGE`
    Sharp – Transfer sharp mark.
  - `SEAM`
    UV Seam – Transfer UV seam mark.
  - `CREASE`
    Subdivision Crease – Transfer crease values.
  - `BEVEL_WEIGHT_EDGE`
    Bevel Weight – Transfer bevel weights.
  - `FREESTYLE_EDGE`
    Freestyle Mark – Transfer Freestyle edge mark.
  - `CUSTOM_NORMAL`
    Custom Normals – Transfer custom normals.
  - `COLOR_CORNER`
    Colors – Color Attributes.
  - `UV`
    UVs – Transfer UV layers.
  - `SMOOTH`
    Smooth – Transfer flat/smooth mark.
  - `FREESTYLE_FACE`
    Freestyle Mark – Transfer Freestyle face mark.
- **use_create** (bool) – Create Data, Add data layers on destination meshes if needed (optional)
- **vert_mapping** (Literal[[Dt Method Vertex Items](bpy_types_enum_items/dt_method_vertex_items.md#rna-enum-dt-method-vertex-items)]) – Vertex Mapping, Method used to map source vertices to destination ones (optional)
- **edge_mapping** (Literal[[Dt Method Edge Items](bpy_types_enum_items/dt_method_edge_items.md#rna-enum-dt-method-edge-items)]) – Edge Mapping, Method used to map source edges to destination ones (optional)
- **loop_mapping** (Literal[[Dt Method Loop Items](bpy_types_enum_items/dt_method_loop_items.md#rna-enum-dt-method-loop-items)]) – Face Corner Mapping, Method used to map source faces’ corners to destination ones (optional)
- **poly_mapping** (Literal[[Dt Method Poly Items](bpy_types_enum_items/dt_method_poly_items.md#rna-enum-dt-method-poly-items)]) – Face Mapping, Method used to map source faces to destination ones (optional)
- **use_auto_transform** (bool) – Auto Transform, Automatically compute transformation to get the best possible match between source and destination meshes.Warning: Results will never be as good as manual matching of objects(optional)
- **use_object_transform** (bool) – Object Transform, Evaluate source and destination meshes in global space (optional)
- **use_max_distance** (bool) – Only Neighbor Geometry, Source elements must be closer than given distance from destination one (optional)
- **max_distance** (float) – Max Distance, Maximum allowed distance between source and destination element, for non-topology mappings (in [0, inf], optional)
- **ray_radius** (float) – Ray Radius, ‘Width’ of rays (especially useful when raycasting against vertices or edges) (in [0, inf], optional)
- **islands_precision** (float) – Islands Precision, Factor controlling precision of islands handling (the higher, the better the results) (in [0, 10], optional)
- **layers_select_src** (Literal[[Dt Layers Select Src Items](bpy_types_enum_items/dt_layers_select_src_items.md#rna-enum-dt-layers-select-src-items)]) – Source Layers Selection, Which layers to transfer, in case of multi-layers types (optional)
- **layers_select_dst** (Literal[[Dt Layers Select Dst Items](bpy_types_enum_items/dt_layers_select_dst_items.md#rna-enum-dt-layers-select-dst-items)]) – Destination Layers Matching, How to match source and destination layers (optional)
- **mix_mode** (Literal[[Dt Mix Mode Items](bpy_types_enum_items/dt_mix_mode_items.md#rna-enum-dt-mix-mode-items)]) – Mix Mode, How to affect destination elements with source values (optional)
- **mix_factor** (float) – Mix Factor, Factor to use when applying data to destination (exact behavior depends on mix mode) (in [0, 1], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.datalayout_transfer"></a>

### bpy.ops.object.datalayout_transfer(*, modifier='', data_type='', use_delete=False, layers_select_src='ACTIVE', layers_select_dst='ACTIVE')

Transfer layout of data layer(s) from active to selected meshes

**Parameters:**

- **modifier** (str) – Modifier, Name of the modifier to edit (optional, never None)
- **data_type** (Literal['', 'VGROUP_WEIGHTS', 'BEVEL_WEIGHT_VERT', 'COLOR_VERTEX', 'SHARP_EDGE', 'SEAM', 'CREASE', 'BEVEL_WEIGHT_EDGE', 'FREESTYLE_EDGE', 'CUSTOM_NORMAL', 'COLOR_CORNER', 'UV', 'SMOOTH', 'FREESTYLE_FACE']) –

  Data Type, Which data to transfer (optional)

  - `VGROUP_WEIGHTS`
    Vertex Group(s) – Transfer active or all vertex groups.
  - `BEVEL_WEIGHT_VERT`
    Bevel Weight – Transfer bevel weights.
  - `COLOR_VERTEX`
    Colors – Color Attributes.
  - `SHARP_EDGE`
    Sharp – Transfer sharp mark.
  - `SEAM`
    UV Seam – Transfer UV seam mark.
  - `CREASE`
    Subdivision Crease – Transfer crease values.
  - `BEVEL_WEIGHT_EDGE`
    Bevel Weight – Transfer bevel weights.
  - `FREESTYLE_EDGE`
    Freestyle Mark – Transfer Freestyle edge mark.
  - `CUSTOM_NORMAL`
    Custom Normals – Transfer custom normals.
  - `COLOR_CORNER`
    Colors – Color Attributes.
  - `UV`
    UVs – Transfer UV layers.
  - `SMOOTH`
    Smooth – Transfer flat/smooth mark.
  - `FREESTYLE_FACE`
    Freestyle Mark – Transfer Freestyle face mark.
- **use_delete** (bool) – Exact Match, Also delete some data layers from destination if necessary, so that it matches exactly source (optional)
- **layers_select_src** (Literal[[Dt Layers Select Src Items](bpy_types_enum_items/dt_layers_select_src_items.md#rna-enum-dt-layers-select-src-items)]) – Source Layers Selection, Which layers to transfer, in case of multi-layers types (optional)
- **layers_select_dst** (Literal[[Dt Layers Select Dst Items](bpy_types_enum_items/dt_layers_select_dst_items.md#rna-enum-dt-layers-select-dst-items)]) – Destination Layers Matching, How to match source and destination layers (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.delete"></a>

### bpy.ops.object.delete(*, use_global=False, confirm=True)

Delete selected objects

**Parameters:**

- **use_global** (bool) – Delete Globally, Remove object from all scenes (optional)
- **confirm** (bool) – Confirm, Prompt for confirmation (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.delete_fix_to_camera_keys"></a>

### bpy.ops.object.delete_fix_to_camera_keys()

Delete all keys that were generated by the ‘Fix to Scene Camera’ operator

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/copy_global_transform.py:639](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/copy_global_transform.py#L639)

<a id="bpy.ops.object.drop_geometry_nodes"></a>

### bpy.ops.object.drop_geometry_nodes(*, session_uid=0, show_datablock_in_modifier=True)

Undocumented, consider [contributing](https://developer.blender.org/).

**Parameters:**

- **session_uid** (int) – Session UID, Session UID of the geometry node group being dropped (in [-inf, inf], optional)
- **show_datablock_in_modifier** (bool) – Show the data-block selector in the modifier, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.drop_named_material"></a>

### bpy.ops.object.drop_named_material(*, name='', session_uid=0)

Undocumented, consider [contributing](https://developer.blender.org/).

**Parameters:**

- **name** (str) – Name, Name of the data-block to use by the operator (optional, never None)
- **session_uid** (int) – Session UID, Session UID of the data-block to use by the operator (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.duplicate"></a>

### bpy.ops.object.duplicate(*, linked=False, mode='TRANSLATION')

Duplicate selected objects

**Parameters:**

- **linked** (bool) – Linked, Duplicate object but not object data, linking to the original data (optional)
- **mode** (Literal[[Transform Mode Type Items](bpy_types_enum_items/transform_mode_type_items.md#rna-enum-transform-mode-type-items)]) – Mode, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.duplicate_move"></a>

### bpy.ops.object.duplicate_move(*, OBJECT_OT_duplicate={}, TRANSFORM_OT_translate={})

Duplicate the selected objects and move them

**Parameters:**

- **OBJECT_OT_duplicate** (dict[str, Any]) – Duplicate Objects, Duplicate selected objects (optional, [`bpy.ops.object.duplicate()`](#bpy.ops.object.duplicate "bpy.ops.object.duplicate") keyword arguments)
- **TRANSFORM_OT_translate** (dict[str, Any]) – Move, Move selected items (optional, [`bpy.ops.transform.translate()`](bpy.ops.transform.md#bpy.ops.transform.translate "bpy.ops.transform.translate") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.duplicate_move_linked"></a>

### bpy.ops.object.duplicate_move_linked(*, OBJECT_OT_duplicate={}, TRANSFORM_OT_translate={})

Duplicate the selected objects, but not their object data, and move them

**Parameters:**

- **OBJECT_OT_duplicate** (dict[str, Any]) – Duplicate Objects, Duplicate selected objects (optional, [`bpy.ops.object.duplicate()`](#bpy.ops.object.duplicate "bpy.ops.object.duplicate") keyword arguments)
- **TRANSFORM_OT_translate** (dict[str, Any]) – Move, Move selected items (optional, [`bpy.ops.transform.translate()`](bpy.ops.transform.md#bpy.ops.transform.translate "bpy.ops.transform.translate") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.duplicates_make_real"></a>

### bpy.ops.object.duplicates_make_real(*, use_base_parent=False, use_hierarchy=False)

Make instanced objects attached to this object real

**Parameters:**

- **use_base_parent** (bool) – Parent, Parent newly created objects to the original instancer (optional)
- **use_hierarchy** (bool) – Keep Hierarchy, Maintain parent child relationships (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.editmode_toggle"></a>

### bpy.ops.object.editmode_toggle()

Toggle object’s edit mode

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.effector_add"></a>

### bpy.ops.object.effector_add(*, type='FORCE', radius=1.0, enter_editmode=False, align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(0.0, 0.0, 0.0))

Add an empty object with a physics effector to the scene

**Parameters:**

- **type** (Literal['FORCE', 'WIND', 'VORTEX', 'MAGNET', 'HARMONIC', 'CHARGE', 'LENNARDJ', 'TEXTURE', 'GUIDE', 'BOID', 'TURBULENCE', 'DRAG', 'FLUID']) – Type, (optional)
- **radius** (float) – Radius, (in [0, inf], optional)
- **enter_editmode** (bool) – Enter Edit Mode, Enter edit mode when adding this object (optional)
- **align** (Literal['WORLD', 'VIEW', 'CURSOR']) –

  Align, The alignment of the new object (optional)

  - `WORLD`
    World – Align the new object to the world.
  - `VIEW`
    View – Align the new object to the view.
  - `CURSOR`
    3D Cursor – Use the 3D cursor orientation for the new object.
- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Location for the newly added object (array of 3 items, in [-inf, inf], optional)
- **rotation** ([`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler") | Sequence[float]) – Rotation, Rotation for the newly added object (array of 3 items, in [-inf, inf], optional)
- **scale** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Scale, Scale for the newly added object (array of 3 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.empty_add"></a>

### bpy.ops.object.empty_add(*, type='PLAIN_AXES', radius=1.0, align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(0.0, 0.0, 0.0))

Add an empty object to the scene

**Parameters:**

- **type** (Literal[[Object Empty Drawtype Items](bpy_types_enum_items/object_empty_drawtype_items.md#rna-enum-object-empty-drawtype-items)]) – Type, (optional)
- **radius** (float) – Radius, (in [0, inf], optional)
- **align** (Literal['WORLD', 'VIEW', 'CURSOR']) –

  Align, The alignment of the new object (optional)

  - `WORLD`
    World – Align the new object to the world.
  - `VIEW`
    View – Align the new object to the view.
  - `CURSOR`
    3D Cursor – Use the 3D cursor orientation for the new object.
- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Location for the newly added object (array of 3 items, in [-inf, inf], optional)
- **rotation** ([`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler") | Sequence[float]) – Rotation, Rotation for the newly added object (array of 3 items, in [-inf, inf], optional)
- **scale** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Scale, Scale for the newly added object (array of 3 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.empty_image_add"></a>

### bpy.ops.object.empty_image_add(*, filepath='', hide_props_region=True, check_existing=False, filter_blender=False, filter_backup=False, filter_image=True, filter_movie=True, filter_python=False, filter_font=False, filter_sound=False, filter_text=False, filter_archive=False, filter_btx=False, filter_alembic=False, filter_usd=False, filter_obj=False, filter_volume=False, filter_folder=True, filter_blenlib=False, filemode=9, relative_path=True, show_multiview=False, use_multiview=False, display_type='DEFAULT', sort_method='', name='', session_uid=0, align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(0.0, 0.0, 0.0), background=False)

Add an empty image type to scene with data

**Parameters:**

- **filepath** (str) – File Path, Path to file (optional, never None)
- **hide_props_region** (bool) – Hide Operator Properties, Collapse the region displaying the operator settings (optional)
- **check_existing** (bool) – Check Existing, Check and warn on overwriting existing files (optional)
- **filter_blender** (bool) – Filter .blend files, (optional)
- **filter_backup** (bool) – Filter backup .blend files, (optional)
- **filter_image** (bool) – Filter image files, (optional)
- **filter_movie** (bool) – Filter movie files, (optional)
- **filter_python** (bool) – Filter Python files, (optional)
- **filter_font** (bool) – Filter font files, (optional)
- **filter_sound** (bool) – Filter sound files, (optional)
- **filter_text** (bool) – Filter text files, (optional)
- **filter_archive** (bool) – Filter archive files, (optional)
- **filter_btx** (bool) – Filter btx files, (optional)
- **filter_alembic** (bool) – Filter Alembic files, (optional)
- **filter_usd** (bool) – Filter USD files, (optional)
- **filter_obj** (bool) – Filter OBJ files, (optional)
- **filter_volume** (bool) – Filter OpenVDB volume files, (optional)
- **filter_folder** (bool) – Filter folders, (optional)
- **filter_blenlib** (bool) – Filter Blender IDs, (optional)
- **filemode** (int) – File Browser Mode, The setting for the file browser mode to load a .blend file, a library or a special file (in [1, 9], optional)
- **relative_path** (bool) – Relative Path, Select the file relative to the blend file (optional)
- **show_multiview** (bool) – Enable Multi-View, (optional)
- **use_multiview** (bool) – Use Multi-View, (optional)
- **display_type** (Literal['DEFAULT', 'LIST_VERTICAL', 'LIST_HORIZONTAL', 'THUMBNAIL']) –

  Display Type, (optional)

  - `DEFAULT`
    Default – Automatically determine display type for files.
  - `LIST_VERTICAL`
    Short List – Display files as short list.
  - `LIST_HORIZONTAL`
    Long List – Display files as a detailed list.
  - `THUMBNAIL`
    Thumbnails – Display files as thumbnails.
- **sort_method** (Literal['', 'DEFAULT', 'FILE_SORT_ALPHA', 'FILE_SORT_EXTENSION', 'FILE_SORT_TIME', 'FILE_SORT_SIZE', 'ASSET_CATALOG']) –

  File sorting mode, (optional)

  - `DEFAULT`
    Default – Automatically determine sort method for files.
  - `FILE_SORT_ALPHA`
    Name – Sort the file list alphabetically.
  - `FILE_SORT_EXTENSION`
    Extension – Sort the file list by extension/type.
  - `FILE_SORT_TIME`
    Modified Date – Sort files by modification time.
  - `FILE_SORT_SIZE`
    Size – Sort files by size.
  - `ASSET_CATALOG`
    Asset Catalog – Sort the asset list so that assets in the same catalog are kept together. Within a single catalog, assets are ordered by name. The catalogs are in order of the flattened catalog hierarchy..
- **name** (str) – Name, Name of the data-block to use by the operator (optional, never None)
- **session_uid** (int) – Session UID, Session UID of the data-block to use by the operator (in [-inf, inf], optional)
- **align** (Literal['WORLD', 'VIEW', 'CURSOR']) –

  Align, The alignment of the new object (optional)

  - `WORLD`
    World – Align the new object to the world.
  - `VIEW`
    View – Align the new object to the view.
  - `CURSOR`
    3D Cursor – Use the 3D cursor orientation for the new object.
- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Location for the newly added object (array of 3 items, in [-inf, inf], optional)
- **rotation** ([`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler") | Sequence[float]) – Rotation, Rotation for the newly added object (array of 3 items, in [-inf, inf], optional)
- **scale** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Scale, Scale for the newly added object (array of 3 items, in [-inf, inf], optional)
- **background** (bool) – Put in Background, Make the image render behind all objects (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.explode_refresh"></a>

### bpy.ops.object.explode_refresh(*, modifier='')

Refresh data in the Explode modifier

**Parameters:**

**modifier** (str) – Modifier, Name of the modifier to edit (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.fix_to_camera"></a>

### bpy.ops.object.fix_to_camera(*, use_location=True, use_rotation=True, use_scale=True)

Generate new keys to fix the selected object/bone to the camera on unkeyed frames

**Parameters:**

- **use_location** (bool) – Location, Create Location keys when fixing to the scene camera (optional)
- **use_rotation** (bool) – Rotation, Create Rotation keys when fixing to the scene camera (optional)
- **use_scale** (bool) – Scale, Create Scale keys when fixing to the scene camera (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/copy_global_transform.py:639](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/copy_global_transform.py#L639)

<a id="bpy.ops.object.forcefield_toggle"></a>

### bpy.ops.object.forcefield_toggle()

Toggle object’s force field

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.geometry_node_bake_delete_single"></a>

### bpy.ops.object.geometry_node_bake_delete_single(*, session_uid=0, modifier_name='', bake_id=0)

Delete baked data of a single bake node or simulation

**Parameters:**

- **session_uid** (int) – Session UID, Session UID of the data-block to use by the operator (in [-inf, inf], optional)
- **modifier_name** (str) – Modifier Name, Name of the modifier that contains the node (optional, never None)
- **bake_id** (int) – Bake ID, Nested node id of the node (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.geometry_node_bake_pack_single"></a>

### bpy.ops.object.geometry_node_bake_pack_single(*, session_uid=0, modifier_name='', bake_id=0)

Pack baked data from disk into the .blend file

**Parameters:**

- **session_uid** (int) – Session UID, Session UID of the data-block to use by the operator (in [-inf, inf], optional)
- **modifier_name** (str) – Modifier Name, Name of the modifier that contains the node (optional, never None)
- **bake_id** (int) – Bake ID, Nested node id of the node (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.geometry_node_bake_single"></a>

### bpy.ops.object.geometry_node_bake_single(*, session_uid=0, modifier_name='', bake_id=0)

Bake a single bake node or simulation

**Parameters:**

- **session_uid** (int) – Session UID, Session UID of the data-block to use by the operator (in [-inf, inf], optional)
- **modifier_name** (str) – Modifier Name, Name of the modifier that contains the node (optional, never None)
- **bake_id** (int) – Bake ID, Nested node id of the node (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.geometry_node_bake_unpack_single"></a>

### bpy.ops.object.geometry_node_bake_unpack_single(*, session_uid=0, modifier_name='', bake_id=0, method='USE_LOCAL')

Unpack baked data from the .blend file to disk

**Parameters:**

- **session_uid** (int) – Session UID, Session UID of the data-block to use by the operator (in [-inf, inf], optional)
- **modifier_name** (str) – Modifier Name, Name of the modifier that contains the node (optional, never None)
- **bake_id** (int) – Bake ID, Nested node id of the node (in [0, inf], optional)
- **method** (Literal['USE_LOCAL', 'WRITE_LOCAL', 'USE_ORIGINAL', 'WRITE_ORIGINAL']) – Method, How to unpack (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.geometry_node_tree_copy_assign"></a>

### bpy.ops.object.geometry_node_tree_copy_assign()

Duplicate the active geometry node group and assign it to the active modifier

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.geometry_nodes_input_attribute_toggle"></a>

### bpy.ops.object.geometry_nodes_input_attribute_toggle(*, input_name='', modifier_name='')

Switch between an attribute and a single value to define the data for every element

**Parameters:**

- **input_name** (str) – Input Name, (optional, never None)
- **modifier_name** (str) – Modifier Name, (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.geometry_nodes_move_to_nodes"></a>

### bpy.ops.object.geometry_nodes_move_to_nodes(*, use_selected_objects=False)

Move inputs and outputs from in the modifier to a new node group

**Parameters:**

**use_selected_objects** (bool) – Selected Objects, Affect all selected objects instead of just the active object (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/geometry_nodes.py:262](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/geometry_nodes.py#L262)

<a id="bpy.ops.object.grease_pencil_add"></a>

### bpy.ops.object.grease_pencil_add(*, type='EMPTY', use_in_front=True, stroke_depth_offset=0.05, use_lights=True, stroke_depth_order='3D', radius=1.0, align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(0.0, 0.0, 0.0))

Add a Grease Pencil object to the scene

**Parameters:**

- **type** (Literal[[Object Gpencil Type Items](bpy_types_enum_items/object_gpencil_type_items.md#rna-enum-object-gpencil-type-items)]) – Type, (optional)
- **use_in_front** (bool) – Show In Front, Show Line Art Grease Pencil in front of everything (optional)
- **stroke_depth_offset** (float) – Stroke Offset, Stroke offset for the Line Art modifier (in [0, inf], optional)
- **use_lights** (bool) – Use Lights, Use lights for this Grease Pencil object (optional)
- **stroke_depth_order** (Literal['2D', '3D']) –

  Stroke Depth Order, Defines how the strokes are ordered in 3D space (for objects not displayed ‘In Front’) (optional)

  - `2D`
    2D Layers – Display strokes using Grease Pencil layers to define order.
  - `3D`
    3D Location – Display strokes using real 3D position in 3D space.
- **radius** (float) – Radius, (in [0, inf], optional)
- **align** (Literal['WORLD', 'VIEW', 'CURSOR']) –

  Align, The alignment of the new object (optional)

  - `WORLD`
    World – Align the new object to the world.
  - `VIEW`
    View – Align the new object to the view.
  - `CURSOR`
    3D Cursor – Use the 3D cursor orientation for the new object.
- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Location for the newly added object (array of 3 items, in [-inf, inf], optional)
- **rotation** ([`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler") | Sequence[float]) – Rotation, Rotation for the newly added object (array of 3 items, in [-inf, inf], optional)
- **scale** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Scale, Scale for the newly added object (array of 3 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.grease_pencil_dash_modifier_segment_add"></a>

### bpy.ops.object.grease_pencil_dash_modifier_segment_add(*, modifier='')

Add a segment to the dash modifier

**Parameters:**

**modifier** (str) – Modifier, Name of the modifier to edit (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.grease_pencil_dash_modifier_segment_move"></a>

### bpy.ops.object.grease_pencil_dash_modifier_segment_move(*, modifier='', type='UP')

Move the active dash segment up or down

**Parameters:**

- **modifier** (str) – Modifier, Name of the modifier to edit (optional, never None)
- **type** (Literal['UP', 'DOWN']) – Type, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.grease_pencil_dash_modifier_segment_remove"></a>

### bpy.ops.object.grease_pencil_dash_modifier_segment_remove(*, modifier='', index=0)

Remove the active segment from the dash modifier

**Parameters:**

- **modifier** (str) – Modifier, Name of the modifier to edit (optional, never None)
- **index** (int) – Index, Index of the segment to remove (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.grease_pencil_time_modifier_segment_add"></a>

### bpy.ops.object.grease_pencil_time_modifier_segment_add(*, modifier='')

Add a segment to the time modifier

**Parameters:**

**modifier** (str) – Modifier, Name of the modifier to edit (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.grease_pencil_time_modifier_segment_move"></a>

### bpy.ops.object.grease_pencil_time_modifier_segment_move(*, modifier='', type='UP')

Move the active time segment up or down

**Parameters:**

- **modifier** (str) – Modifier, Name of the modifier to edit (optional, never None)
- **type** (Literal['UP', 'DOWN']) – Type, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.grease_pencil_time_modifier_segment_remove"></a>

### bpy.ops.object.grease_pencil_time_modifier_segment_remove(*, modifier='', index=0)

Remove the active segment from the time modifier

**Parameters:**

- **modifier** (str) – Modifier, Name of the modifier to edit (optional, never None)
- **index** (int) – Index, Index of the segment to remove (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.hide_collection"></a>

### bpy.ops.object.hide_collection(*, collection_index=-1, toggle=False, extend=False)

Show only objects in collection (Shift to extend)

**Parameters:**

- **collection_index** (int) – Collection Index, Index of the collection to change visibility (in [-1, inf], optional)
- **toggle** (bool) – Toggle, Toggle visibility (optional)
- **extend** (bool) – Extend, Extend visibility (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.hide_render_clear_all"></a>

### bpy.ops.object.hide_render_clear_all()

Reveal all render objects by setting the hide render flag

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/object.py:743](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/object.py#L743)

<a id="bpy.ops.object.hide_view_clear"></a>

### bpy.ops.object.hide_view_clear(*, select=True)

Reveal temporarily hidden objects

**Parameters:**

**select** (bool) – Select, Select revealed objects (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.hide_view_set"></a>

### bpy.ops.object.hide_view_set(*, unselected=False)

Temporarily hide objects from the viewport

**Parameters:**

**unselected** (bool) – Unselected, Hide unselected rather than selected objects (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.hook_add_newob"></a>

### bpy.ops.object.hook_add_newob()

Hook selected vertices to a newly created object

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.hook_add_selob"></a>

### bpy.ops.object.hook_add_selob(*, use_bone=False)

Hook selected vertices to the first selected object

**Parameters:**

**use_bone** (bool) – Active Bone, Assign the hook to the hook object’s active bone (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.hook_assign"></a>

### bpy.ops.object.hook_assign(*, modifier='')

Assign the selected vertices to a hook

**Parameters:**

**modifier** (str) – Modifier, Modifier number to assign to (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.hook_recenter"></a>

### bpy.ops.object.hook_recenter(*, modifier='')

Set hook center to cursor position

**Parameters:**

**modifier** (str) – Modifier, Modifier number to assign to (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.hook_remove"></a>

### bpy.ops.object.hook_remove(*, modifier='')

Remove a hook from the active object

**Parameters:**

**modifier** (str) – Modifier, Modifier number to remove (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.hook_reset"></a>

### bpy.ops.object.hook_reset(*, modifier='')

Recalculate and clear offset transformation

**Parameters:**

**modifier** (str) – Modifier, Modifier number to assign to (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.hook_select"></a>

### bpy.ops.object.hook_select(*, modifier='')

Select affected vertices on mesh

**Parameters:**

**modifier** (str) – Modifier, Modifier number to remove (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.instance_offset_from_cursor"></a>

### bpy.ops.object.instance_offset_from_cursor()

Set offset used for collection instances based on cursor position

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/object.py:936](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/object.py#L936)

<a id="bpy.ops.object.instance_offset_from_object"></a>

### bpy.ops.object.instance_offset_from_object()

Set offset used for collection instances based on the active object position

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/object.py:968](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/object.py#L968)

<a id="bpy.ops.object.instance_offset_to_cursor"></a>

### bpy.ops.object.instance_offset_to_cursor()

Set cursor position to the offset used for collection instances

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/object.py:951](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/object.py#L951)

<a id="bpy.ops.object.isolate_type_render"></a>

### bpy.ops.object.isolate_type_render()

Hide unselected render objects of same type as active by setting the hide render flag

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/object.py:723](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/object.py#L723)

<a id="bpy.ops.object.join"></a>

### bpy.ops.object.join()

Join selected objects into active object

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.join_shapes"></a>

### bpy.ops.object.join_shapes(*, use_mirror=False)

Add the vertex positions of selected objects as shape keys or update existing shape keys with matching names

**Parameters:**

**use_mirror** (bool) – Mirror, Mirror the new shape key values (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.join_uvs"></a>

### bpy.ops.object.join_uvs()

Transfer UV Maps from active to selected objects (needs matching geometry)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/object.py:623](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/object.py#L623)

<a id="bpy.ops.object.laplaciandeform_bind"></a>

### bpy.ops.object.laplaciandeform_bind(*, modifier='')

Bind mesh to system in laplacian deform modifier

**Parameters:**

**modifier** (str) – Modifier, Name of the modifier to edit (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.lattice_add_to_selected"></a>

### bpy.ops.object.lattice_add_to_selected(*, fit_to_selected=True, radius=1.0, margin=0.0, add_modifiers=True, resolution_u=2, resolution_v=2, resolution_w=2, enter_editmode=False, align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(0.0, 0.0, 0.0))

Add a lattice and use it to deform selected objects

**Parameters:**

- **fit_to_selected** (bool) – Fit to Selected, Resize lattice to fit selected deformable objects (optional)
- **radius** (float) – Radius, (in [0, inf], optional)
- **margin** (float) – Margin, Add margin to lattice dimensions (in [0, inf], optional)
- **add_modifiers** (bool) – Add Modifiers, Automatically add lattice modifiers to selected objects (optional)
- **resolution_u** (int) – Resolution U, Lattice resolution in U direction (in [1, 64], optional)
- **resolution_v** (int) – V, Lattice resolution in V direction (in [1, 64], optional)
- **resolution_w** (int) – W, Lattice resolution in W direction (in [1, 64], optional)
- **enter_editmode** (bool) – Enter Edit Mode, Enter edit mode when adding this object (optional)
- **align** (Literal['WORLD', 'VIEW', 'CURSOR']) –

  Align, The alignment of the new object (optional)

  - `WORLD`
    World – Align the new object to the world.
  - `VIEW`
    View – Align the new object to the view.
  - `CURSOR`
    3D Cursor – Use the 3D cursor orientation for the new object.
- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Location for the newly added object (array of 3 items, in [-inf, inf], optional)
- **rotation** ([`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler") | Sequence[float]) – Rotation, Rotation for the newly added object (array of 3 items, in [-inf, inf], optional)
- **scale** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Scale, Scale for the newly added object (array of 3 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.light_add"></a>

### bpy.ops.object.light_add(*, type='POINT', radius=1.0, align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(0.0, 0.0, 0.0))

Add a light object to the scene

**Parameters:**

- **type** (Literal[[Light Type Items](bpy_types_enum_items/light_type_items.md#rna-enum-light-type-items)]) – Type, (optional)
- **radius** (float) – Radius, (in [0, inf], optional)
- **align** (Literal['WORLD', 'VIEW', 'CURSOR']) –

  Align, The alignment of the new object (optional)

  - `WORLD`
    World – Align the new object to the world.
  - `VIEW`
    View – Align the new object to the view.
  - `CURSOR`
    3D Cursor – Use the 3D cursor orientation for the new object.
- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Location for the newly added object (array of 3 items, in [-inf, inf], optional)
- **rotation** ([`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler") | Sequence[float]) – Rotation, Rotation for the newly added object (array of 3 items, in [-inf, inf], optional)
- **scale** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Scale, Scale for the newly added object (array of 3 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.light_linking_blocker_collection_new"></a>

### bpy.ops.object.light_linking_blocker_collection_new()

Create new light linking collection used by the active emitter

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.light_linking_blockers_link"></a>

### bpy.ops.object.light_linking_blockers_link(*, link_state='INCLUDE')

Light link selected blockers to the active emitter object

**Parameters:**

**link_state** (Literal['INCLUDE', 'EXCLUDE']) –

Link State, State of the shadow linking (optional)

- `INCLUDE`
  Include – Include selected blockers to cast shadows from the active emitter.
- `EXCLUDE`
  Exclude – Exclude selected blockers from casting shadows from the active emitter.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.light_linking_blockers_select"></a>

### bpy.ops.object.light_linking_blockers_select()

Select all objects which block light from this emitter

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.light_linking_receiver_collection_new"></a>

### bpy.ops.object.light_linking_receiver_collection_new()

Create new light linking collection used by the active emitter

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.light_linking_receivers_link"></a>

### bpy.ops.object.light_linking_receivers_link(*, link_state='INCLUDE')

Light link selected receivers to the active emitter object

**Parameters:**

**link_state** (Literal['INCLUDE', 'EXCLUDE']) –

Link State, State of the light linking (optional)

- `INCLUDE`
  Include – Include selected receivers to receive light from the active emitter.
- `EXCLUDE`
  Exclude – Exclude selected receivers from receiving light from the active emitter.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.light_linking_receivers_select"></a>

### bpy.ops.object.light_linking_receivers_select()

Select all objects which receive light from this emitter

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.light_linking_unlink_from_collection"></a>

### bpy.ops.object.light_linking_unlink_from_collection()

Remove this object or collection from the light linking collection

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.lightprobe_add"></a>

### bpy.ops.object.lightprobe_add(*, type='SPHERE', radius=1.0, enter_editmode=False, align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(0.0, 0.0, 0.0))

Add a light probe object

**Parameters:**

- **type** (Literal['SPHERE', 'PLANE', 'VOLUME']) –

  Type, (optional)

  - `SPHERE`
    Sphere – Light probe that captures precise lighting from all directions at a single point in space.
  - `PLANE`
    Plane – Light probe that captures incoming light from a single direction on a plane.
  - `VOLUME`
    Volume – Light probe that captures low frequency lighting inside a volume.
- **radius** (float) – Radius, (in [0, inf], optional)
- **enter_editmode** (bool) – Enter Edit Mode, Enter edit mode when adding this object (optional)
- **align** (Literal['WORLD', 'VIEW', 'CURSOR']) –

  Align, The alignment of the new object (optional)

  - `WORLD`
    World – Align the new object to the world.
  - `VIEW`
    View – Align the new object to the view.
  - `CURSOR`
    3D Cursor – Use the 3D cursor orientation for the new object.
- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Location for the newly added object (array of 3 items, in [-inf, inf], optional)
- **rotation** ([`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler") | Sequence[float]) – Rotation, Rotation for the newly added object (array of 3 items, in [-inf, inf], optional)
- **scale** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Scale, Scale for the newly added object (array of 3 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.lightprobe_cache_bake"></a>

### bpy.ops.object.lightprobe_cache_bake(*, subset='ALL')

Bake irradiance volume light cache

**Parameters:**

**subset** (Literal['ALL', 'SELECTED', 'ACTIVE']) –

Subset, Subset of probes to update (optional)

- `ALL`
  All Volumes – Bake all light probe volumes.
- `SELECTED`
  Selected Only – Only bake selected light probe volumes.
- `ACTIVE`
  Active Only – Only bake the active light probe volume.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.lightprobe_cache_free"></a>

### bpy.ops.object.lightprobe_cache_free(*, subset='SELECTED')

Delete cached indirect lighting

**Parameters:**

**subset** (Literal['ALL', 'SELECTED', 'ACTIVE']) –

Subset, Subset of probes to update (optional)

- `ALL`
  All Light Probes – Delete all light probes’ baked lighting data.
- `SELECTED`
  Selected Only – Only delete selected light probes’ baked lighting data.
- `ACTIVE`
  Active Only – Only delete the active light probe’s baked lighting data.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.lineart_bake_strokes"></a>

### bpy.ops.object.lineart_bake_strokes(*, bake_all=False)

Bake Line Art for current Grease Pencil object

**Parameters:**

**bake_all** (bool) – Bake All, Bake all Line Art modifiers (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.lineart_clear"></a>

### bpy.ops.object.lineart_clear(*, clear_all=False)

Clear all strokes in current Grease Pencil object

**Parameters:**

**clear_all** (bool) – Clear All, Clear all Line Art modifier bakes (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.link_to_collection"></a>

### bpy.ops.object.link_to_collection(*, collection_uid=-1, is_new=False, new_collection_name='')

Link objects to a collection

**Parameters:**

- **collection_uid** (int) – Collection UID, Session UID of the collection to link to (in [-1, inf], optional)
- **is_new** (bool) – New, Link objects to a new collection (optional)
- **new_collection_name** (str) – Name, Name of the newly added collection (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.location_clear"></a>

### bpy.ops.object.location_clear(*, clear_delta=False)

Clear the object’s location

**Parameters:**

**clear_delta** (bool) – Clear Delta, Clear delta location in addition to clearing the normal location transform (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.make_dupli_face"></a>

### bpy.ops.object.make_dupli_face()

Convert objects into instanced faces

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/object.py:706](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/object.py#L706)

<a id="bpy.ops.object.make_links_data"></a>

### bpy.ops.object.make_links_data(*, type='OBDATA')

Transfer data from active object to selected objects

**Parameters:**

**type** (Literal['OBDATA', 'MATERIAL', 'ANIMATION', 'GROUPS', 'DUPLICOLLECTION', 'FONTS', 'MODIFIERS', 'CONSTRAINTS', 'EFFECTS', 'LIGHT_LINKING', 'SHADOW_LINKING']) –

Type, (optional)

- `OBDATA`
  Link Object Data – Replace assigned Object Data.
- `MATERIAL`
  Link Materials – Replace assigned Materials.
- `ANIMATION`
  Link Animation Data – Replace assigned Animation Data.
- `GROUPS`
  Link Collections – Replace assigned Collections.
- `DUPLICOLLECTION`
  Link Instance Collection – Replace assigned Collection Instance.
- `FONTS`
  Link Fonts to Text – Replace Text object Fonts.
- `MODIFIERS`
  Copy Modifiers – Replace Modifiers.
- `CONSTRAINTS`
  Copy Constraints – Replace Constraints.
- `EFFECTS`
  Copy Grease Pencil Effects – Replace Grease Pencil Effects.
- `LIGHT_LINKING`
  Copy Light Linking – Replace assigned Light Linking collection.
- `SHADOW_LINKING`
  Copy Shadow Linking – Replace assigned Shadow Linking collection.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.make_links_scene"></a>

### bpy.ops.object.make_links_scene(*, scene='')

Link selection to another scene

**Parameters:**

**scene** (str) – Scene, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.make_local"></a>

### bpy.ops.object.make_local(*, type='SELECT_OBJECT')

Make library linked data-blocks local to this file

**Parameters:**

**type** (Literal['SELECT_OBJECT', 'SELECT_OBDATA', 'SELECT_OBDATA_MATERIAL', 'ALL']) – Type, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.make_override_library"></a>

### bpy.ops.object.make_override_library(*, collection=0)

Create a local override of the selected linked objects, and their hierarchy of dependencies

**Parameters:**

**collection** (int) – Override Collection, Session UID of the directly linked collection containing the selected object, to make an override from (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.make_single_user"></a>

### bpy.ops.object.make_single_user(*, type='SELECTED_OBJECTS', object=False, obdata=False, material=False, animation=False, obdata_animation=False)

Make linked data local to each object

**Parameters:**

- **type** (Literal['SELECTED_OBJECTS', 'ALL']) – Type, (optional)
- **object** (bool) – Object, Make single user objects (optional)
- **obdata** (bool) – Object Data, Make single user object data (optional)
- **material** (bool) – Materials, Make materials local to each data-block (optional)
- **animation** (bool) – Object Animation, Make object animation data local to each object (optional)
- **obdata_animation** (bool) – Object Data Animation, Make object data (mesh, curve etc.) animation data local to each object (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.material_slot_add"></a>

### bpy.ops.object.material_slot_add()

Add a new material slot

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.material_slot_assign"></a>

### bpy.ops.object.material_slot_assign()

Assign active material slot to selection

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.material_slot_copy"></a>

### bpy.ops.object.material_slot_copy()

Copy material to selected objects

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.material_slot_deselect"></a>

### bpy.ops.object.material_slot_deselect()

Deselect by active material slot

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.material_slot_move"></a>

### bpy.ops.object.material_slot_move(*, direction='UP')

Move the active material up/down in the list

**Parameters:**

**direction** (Literal['UP', 'DOWN']) – Direction, Direction to move the active material towards (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.material_slot_remove"></a>

### bpy.ops.object.material_slot_remove()

Remove the selected material slot

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.material_slot_remove_all"></a>

### bpy.ops.object.material_slot_remove_all()

Remove all materials

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.material_slot_remove_unused"></a>

### bpy.ops.object.material_slot_remove_unused()

Remove unused material slots

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.material_slot_select"></a>

### bpy.ops.object.material_slot_select()

Select by active material slot

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.meshdeform_bind"></a>

### bpy.ops.object.meshdeform_bind(*, modifier='')

Bind mesh to cage in mesh deform modifier

**Parameters:**

**modifier** (str) – Modifier, Name of the modifier to edit (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.metaball_add"></a>

### bpy.ops.object.metaball_add(*, type='BALL', radius=2.0, enter_editmode=False, align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(0.0, 0.0, 0.0))

Add a metaball object to the scene

**Parameters:**

- **type** (Literal[[Metaelem Type Items](bpy_types_enum_items/metaelem_type_items.md#rna-enum-metaelem-type-items)]) – Primitive, (optional)
- **radius** (float) – Radius, (in [0, inf], optional)
- **enter_editmode** (bool) – Enter Edit Mode, Enter edit mode when adding this object (optional)
- **align** (Literal['WORLD', 'VIEW', 'CURSOR']) –

  Align, The alignment of the new object (optional)

  - `WORLD`
    World – Align the new object to the world.
  - `VIEW`
    View – Align the new object to the view.
  - `CURSOR`
    3D Cursor – Use the 3D cursor orientation for the new object.
- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Location for the newly added object (array of 3 items, in [-inf, inf], optional)
- **rotation** ([`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler") | Sequence[float]) – Rotation, Rotation for the newly added object (array of 3 items, in [-inf, inf], optional)
- **scale** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Scale, Scale for the newly added object (array of 3 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.mode_set"></a>

### bpy.ops.object.mode_set(*, mode='OBJECT', toggle=False)

Sets the object interaction mode

**Parameters:**

- **mode** (Literal[[Object Mode Items](bpy_types_enum_items/object_mode_items.md#rna-enum-object-mode-items)]) – Mode, (optional)
- **toggle** (bool) – Toggle, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.mode_set_with_submode"></a>

### bpy.ops.object.mode_set_with_submode(*, mode='OBJECT', toggle=False, mesh_select_mode=set())

Sets the object interaction mode

**Parameters:**

- **mode** (Literal[[Object Mode Items](bpy_types_enum_items/object_mode_items.md#rna-enum-object-mode-items)]) – Mode, (optional)
- **toggle** (bool) – Toggle, (optional)
- **mesh_select_mode** (set[Literal[[Mesh Select Mode Items](bpy_types_enum_items/mesh_select_mode_items.md#rna-enum-mesh-select-mode-items)]]) – Mesh Mode, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.modifier_add"></a>

### bpy.ops.object.modifier_add(*, type='SUBSURF', use_selected_objects=False)

Add a procedural operation/effect to the active object

**Parameters:**

- **type** (Literal[[Object Modifier Type Items](bpy_types_enum_items/object_modifier_type_items.md#rna-enum-object-modifier-type-items)]) – Type, (optional)
- **use_selected_objects** (bool) – Selected Objects, Affect all selected objects instead of just the active object (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.modifier_add_node_group"></a>

### bpy.ops.object.modifier_add_node_group(*, asset_library_type='LOCAL', asset_library_identifier='', relative_asset_identifier='', session_uid=0, use_selected_objects=False)

Add a procedural operation/effect to the active object

**Parameters:**

- **asset_library_type** (Literal[[Asset Library Type Items](bpy_types_enum_items/asset_library_type_items.md#rna-enum-asset-library-type-items)]) – Asset Library Type, (optional)
- **asset_library_identifier** (str) – Asset Library Identifier, (optional, never None)
- **relative_asset_identifier** (str) – Relative Asset Identifier, (optional, never None)
- **session_uid** (int) – Session UID, Session UID of the data-block to use by the operator (in [-inf, inf], optional)
- **use_selected_objects** (bool) – Selected Objects, Affect all selected objects instead of just the active object (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.modifier_apply"></a>

### bpy.ops.object.modifier_apply(*, modifier='', report=False, merge_customdata=True, single_user=False, all_keyframes=False, use_selected_objects=False)

Apply modifier and remove from the stack

**Parameters:**

- **modifier** (str) – Modifier, Name of the modifier to edit (optional, never None)
- **report** (bool) – Report, Create a notification after the operation (optional)
- **merge_customdata** (bool) – Merge UVs, For mesh objects, merge UV coordinates that share a vertex to account for imprecision in some modifiers (optional)
- **single_user** (bool) – Make Data Single User, Make the object’s data single user if needed (optional)
- **all_keyframes** (bool) – Apply to all keyframes, For Grease Pencil objects, apply the modifier to all the keyframes (optional)
- **use_selected_objects** (bool) – Selected Objects, Affect all selected objects instead of just the active object (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.modifier_apply_as_shapekey"></a>

### bpy.ops.object.modifier_apply_as_shapekey(*, keep_modifier=False, modifier='', report=False, use_selected_objects=False)

Apply modifier as a new shape key and remove from the stack

**Parameters:**

- **keep_modifier** (bool) – Keep Modifier, Do not remove the modifier from stack (optional)
- **modifier** (str) – Modifier, Name of the modifier to edit (optional, never None)
- **report** (bool) – Report, Create a notification after the operation (optional)
- **use_selected_objects** (bool) – Selected Objects, Affect all selected objects instead of just the active object (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.modifier_convert"></a>

### bpy.ops.object.modifier_convert(*, modifier='')

Convert particles to a mesh object

**Parameters:**

**modifier** (str) – Modifier, Name of the modifier to edit (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.modifier_copy"></a>

### bpy.ops.object.modifier_copy(*, modifier='', use_selected_objects=False)

Duplicate modifier at the same position in the stack

**Parameters:**

- **modifier** (str) – Modifier, Name of the modifier to edit (optional, never None)
- **use_selected_objects** (bool) – Selected Objects, Affect all selected objects instead of just the active object (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.modifier_copy_to_selected"></a>

### bpy.ops.object.modifier_copy_to_selected(*, modifier='')

Copy the modifier from the active object to all selected objects

**Parameters:**

**modifier** (str) – Modifier, Name of the modifier to edit (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.modifier_move_down"></a>

### bpy.ops.object.modifier_move_down(*, modifier='')

Move modifier down in the stack

**Parameters:**

**modifier** (str) – Modifier, Name of the modifier to edit (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.modifier_move_to_index"></a>

### bpy.ops.object.modifier_move_to_index(*, modifier='', index=0, use_selected_objects=False)

Change the modifier’s index in the stack so it evaluates after the set number of others

**Parameters:**

- **modifier** (str) – Modifier, Name of the modifier to edit (optional, never None)
- **index** (int) – Index, The index to move the modifier to (in [0, inf], optional)
- **use_selected_objects** (bool) – Selected Objects, Affect all selected objects instead of just the active object (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.modifier_move_up"></a>

### bpy.ops.object.modifier_move_up(*, modifier='')

Move modifier up in the stack

**Parameters:**

**modifier** (str) – Modifier, Name of the modifier to edit (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.modifier_remove"></a>

### bpy.ops.object.modifier_remove(*, modifier='', report=False, use_selected_objects=False)

Remove a modifier from the active object

**Parameters:**

- **modifier** (str) – Modifier, Name of the modifier to edit (optional, never None)
- **report** (bool) – Report, Create a notification after the operation (optional)
- **use_selected_objects** (bool) – Selected Objects, Affect all selected objects instead of just the active object (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.modifier_set_active"></a>

### bpy.ops.object.modifier_set_active(*, modifier='')

Activate the modifier to use as the context

**Parameters:**

**modifier** (str) – Modifier, Name of the modifier to edit (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.modifiers_clear"></a>

### bpy.ops.object.modifiers_clear()

Clear all modifiers from the selected objects

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.modifiers_copy_to_selected"></a>

### bpy.ops.object.modifiers_copy_to_selected()

Copy modifiers to other selected objects

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.move_to_collection"></a>

### bpy.ops.object.move_to_collection(*, collection_uid=-1, is_new=False, new_collection_name='')

Move objects to a collection

**Parameters:**

- **collection_uid** (int) – Collection UID, Session UID of the collection to move to (in [-1, inf], optional)
- **is_new** (bool) – New, Move objects to a new collection (optional)
- **new_collection_name** (str) – Name, Name of the newly added collection (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.multires_base_apply"></a>

### bpy.ops.object.multires_base_apply(*, modifier='', apply_heuristic=True)

Modify the base mesh to conform to the displaced mesh

**Parameters:**

- **modifier** (str) – Modifier, Name of the modifier to edit (optional, never None)
- **apply_heuristic** (bool) – Apply Subdivision Heuristic, Whether or not the final base mesh positions will be slightly altered to account for a new subdivision modifier being added (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.multires_external_pack"></a>

### bpy.ops.object.multires_external_pack()

Pack displacements from an external file

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.multires_external_save"></a>

### bpy.ops.object.multires_external_save(*, filepath='', hide_props_region=True, check_existing=True, filter_blender=False, filter_backup=False, filter_image=False, filter_movie=False, filter_python=False, filter_font=False, filter_sound=False, filter_text=False, filter_archive=False, filter_btx=True, filter_alembic=False, filter_usd=False, filter_obj=False, filter_volume=False, filter_folder=True, filter_blenlib=False, filemode=9, relative_path=True, display_type='DEFAULT', sort_method='', modifier='')

Save displacements to an external file

**Parameters:**

- **filepath** (str) – File Path, Path to file (optional, never None)
- **hide_props_region** (bool) – Hide Operator Properties, Collapse the region displaying the operator settings (optional)
- **check_existing** (bool) – Check Existing, Check and warn on overwriting existing files (optional)
- **filter_blender** (bool) – Filter .blend files, (optional)
- **filter_backup** (bool) – Filter backup .blend files, (optional)
- **filter_image** (bool) – Filter image files, (optional)
- **filter_movie** (bool) – Filter movie files, (optional)
- **filter_python** (bool) – Filter Python files, (optional)
- **filter_font** (bool) – Filter font files, (optional)
- **filter_sound** (bool) – Filter sound files, (optional)
- **filter_text** (bool) – Filter text files, (optional)
- **filter_archive** (bool) – Filter archive files, (optional)
- **filter_btx** (bool) – Filter btx files, (optional)
- **filter_alembic** (bool) – Filter Alembic files, (optional)
- **filter_usd** (bool) – Filter USD files, (optional)
- **filter_obj** (bool) – Filter OBJ files, (optional)
- **filter_volume** (bool) – Filter OpenVDB volume files, (optional)
- **filter_folder** (bool) – Filter folders, (optional)
- **filter_blenlib** (bool) – Filter Blender IDs, (optional)
- **filemode** (int) – File Browser Mode, The setting for the file browser mode to load a .blend file, a library or a special file (in [1, 9], optional)
- **relative_path** (bool) – Relative Path, Select the file relative to the blend file (optional)
- **display_type** (Literal['DEFAULT', 'LIST_VERTICAL', 'LIST_HORIZONTAL', 'THUMBNAIL']) –

  Display Type, (optional)

  - `DEFAULT`
    Default – Automatically determine display type for files.
  - `LIST_VERTICAL`
    Short List – Display files as short list.
  - `LIST_HORIZONTAL`
    Long List – Display files as a detailed list.
  - `THUMBNAIL`
    Thumbnails – Display files as thumbnails.
- **sort_method** (str) – File sorting mode, (optional)
- **modifier** (str) – Modifier, Name of the modifier to edit (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.multires_higher_levels_delete"></a>

### bpy.ops.object.multires_higher_levels_delete(*, modifier='')

Deletes the higher resolution mesh, potential loss of detail

**Parameters:**

**modifier** (str) – Modifier, Name of the modifier to edit (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.multires_rebuild_subdiv"></a>

### bpy.ops.object.multires_rebuild_subdiv(*, modifier='')

Rebuilds all possible subdivisions levels to generate a lower resolution base mesh

**Parameters:**

**modifier** (str) – Modifier, Name of the modifier to edit (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.multires_reshape"></a>

### bpy.ops.object.multires_reshape(*, modifier='')

Copy vertex coordinates from other object

**Parameters:**

**modifier** (str) – Modifier, Name of the modifier to edit (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.multires_subdivide"></a>

### bpy.ops.object.multires_subdivide(*, modifier='', mode='CATMULL_CLARK')

Add a new level of subdivision

**Parameters:**

- **modifier** (str) – Modifier, Name of the modifier to edit (optional, never None)
- **mode** (Literal['CATMULL_CLARK', 'SIMPLE', 'LINEAR']) –

  Subdivision Mode, How the mesh is going to be subdivided to create a new level (optional)

  - `CATMULL_CLARK`
    Catmull-Clark – Create a new level using Catmull-Clark subdivisions.
  - `SIMPLE`
    Simple – Create a new level using simple subdivisions.
  - `LINEAR`
    Linear – Create a new level using linear interpolation of the sculpted displacement.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.multires_unsubdivide"></a>

### bpy.ops.object.multires_unsubdivide(*, modifier='')

Rebuild a lower subdivision level of the current base mesh

**Parameters:**

**modifier** (str) – Modifier, Name of the modifier to edit (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.ocean_bake"></a>

### bpy.ops.object.ocean_bake(*, modifier='', free=False)

Bake an image sequence of ocean data

**Parameters:**

- **modifier** (str) – Modifier, Name of the modifier to edit (optional, never None)
- **free** (bool) – Free, Free the bake, rather than generating it (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.origin_clear"></a>

### bpy.ops.object.origin_clear()

Clear the object’s origin

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.origin_set"></a>

### bpy.ops.object.origin_set(*, type='GEOMETRY_ORIGIN', center='MEDIAN')

Set the object’s origin, by either moving the data, or set to center of data, or use 3D cursor

**Parameters:**

- **type** (Literal['GEOMETRY_ORIGIN', 'ORIGIN_GEOMETRY', 'ORIGIN_CURSOR', 'ORIGIN_CENTER_OF_MASS', 'ORIGIN_CENTER_OF_VOLUME']) –

  Type, (optional)

  - `GEOMETRY_ORIGIN`
    Geometry to Origin – Move object geometry to object origin.
  - `ORIGIN_GEOMETRY`
    Origin to Geometry – Calculate the center of geometry based on the current pivot point (median, otherwise bounding box).
  - `ORIGIN_CURSOR`
    Origin to 3D Cursor – Move object origin to position of the 3D cursor.
  - `ORIGIN_CENTER_OF_MASS`
    Origin to Center of Mass (Surface) – Calculate the center of mass from the surface area.
  - `ORIGIN_CENTER_OF_VOLUME`
    Origin to Center of Mass (Volume) – Calculate the center of mass from the volume (must be manifold geometry with consistent normals).
- **center** (Literal['MEDIAN', 'BOUNDS']) – Center, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.parent_clear"></a>

### bpy.ops.object.parent_clear(*, type='CLEAR')

Clear the object’s parenting

**Parameters:**

**type** (Literal['CLEAR', 'CLEAR_KEEP_TRANSFORM', 'CLEAR_INVERSE']) –

Type, (optional)

- `CLEAR`
  Clear Parent – Completely clear the parenting relationship, including involved modifiers if any.
- `CLEAR_KEEP_TRANSFORM`
  Clear and Keep Transformation – As ‘Clear Parent’, but keep the current visual transformations of the object.
- `CLEAR_INVERSE`
  Clear Parent Inverse – Reset the transform corrections applied to the parenting relationship, does not remove parenting itself.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.parent_inverse_apply"></a>

### bpy.ops.object.parent_inverse_apply()

Apply the object’s parent inverse to its data

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.parent_no_inverse_set"></a>

### bpy.ops.object.parent_no_inverse_set(*, keep_transform=False)

Set the object’s parenting without setting the inverse parent correction

**Parameters:**

**keep_transform** (bool) – Keep Transform, Preserve the world transform throughout parenting (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.parent_set"></a>

### bpy.ops.object.parent_set(*, type='OBJECT', xmirror=False, keep_transform=False)

Set the object’s parenting

**Parameters:**

- **type** (Literal['OBJECT', 'ARMATURE', 'ARMATURE_NAME', 'ARMATURE_AUTO', 'ARMATURE_ENVELOPE', 'BONE', 'BONE_RELATIVE', 'CURVE', 'FOLLOW', 'PATH_CONST', 'LATTICE', 'VERTEX', 'VERTEX_TRI']) – Type, (optional)
- **xmirror** (bool) – X Mirror, Apply weights symmetrically along X axis, for Envelope/Automatic vertex groups creation (optional)
- **keep_transform** (bool) – Keep Transform, Apply transformation before parenting (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.particle_system_add"></a>

### bpy.ops.object.particle_system_add()

Add a particle system

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.particle_system_remove"></a>

### bpy.ops.object.particle_system_remove()

Remove the selected particle system

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.paste_transform"></a>

### bpy.ops.object.paste_transform(*, method='CURRENT', bake_step=0, use_mirror=False, mirror_axis_loc='x', mirror_axis_rot='z', use_relative=False)

Pastes the matrix from the clipboard to the currently active pose bone or object. Uses world-space matrices

**Parameters:**

- **method** (Literal['CURRENT', 'EXISTING_KEYS', 'BAKE']) –

  Paste Method, Update the current transform, selected keyframes, or even create new keys (optional)

  - `CURRENT`
    Current Transform – Paste onto the current values only, only manipulating the animation data if auto-keying is enabled.
  - `EXISTING_KEYS`
    Selected Keys – Paste onto frames that have a selected key, potentially creating new keys on those frames.
  - `BAKE`
    Bake on Key Range – Paste onto all frames between the first and last selected key, creating new keyframes if necessary.
- **bake_step** (int) – Frame Step, Only used for baking. Step=1 creates a key on every frame, step=2 bakes on 2s, etc (in [1, inf], optional)
- **use_mirror** (bool) – Mirror Transform, When pasting, mirror the transform relative to a specific object or bone (optional)
- **mirror_axis_loc** (Literal['x', 'y', 'z']) – Location Axis, Coordinate axis used to mirror the location part of the transform (optional)
- **mirror_axis_rot** (Literal['x', 'y', 'z']) – Rotation Axis, Coordinate axis used to mirror the rotation part of the transform (optional)
- **use_relative** (bool) – Use Relative Paste, When pasting, assume the pasted matrix is relative to another object (set in the user interface) (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/copy_global_transform.py:325](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/copy_global_transform.py#L325)

<a id="bpy.ops.object.paths_calculate"></a>

### bpy.ops.object.paths_calculate(*, display_type='RANGE', range='SCENE')

Generate motion paths for the selected objects

**Parameters:**

- **display_type** (Literal[[Motionpath Display Type Items](bpy_types_enum_items/motionpath_display_type_items.md#rna-enum-motionpath-display-type-items)]) – Display Type, (optional)
- **range** (Literal[[Motionpath Range Items](bpy_types_enum_items/motionpath_range_items.md#rna-enum-motionpath-range-items)]) – Computation Range, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.paths_clear"></a>

### bpy.ops.object.paths_clear(*, only_selected=False)

Undocumented, consider [contributing](https://developer.blender.org/).

**Parameters:**

**only_selected** (bool) – Only Selected, Only clear motion paths of selected objects (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.paths_update"></a>

### bpy.ops.object.paths_update()

Recalculate motion paths for selected objects

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.paths_update_visible"></a>

### bpy.ops.object.paths_update_visible()

Recalculate all visible motion paths for objects and poses

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.pointcloud_random_add"></a>

### bpy.ops.object.pointcloud_random_add(*, align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(0.0, 0.0, 0.0))

Add a point cloud object to the scene

**Parameters:**

- **align** (Literal['WORLD', 'VIEW', 'CURSOR']) –

  Align, The alignment of the new object (optional)

  - `WORLD`
    World – Align the new object to the world.
  - `VIEW`
    View – Align the new object to the view.
  - `CURSOR`
    3D Cursor – Use the 3D cursor orientation for the new object.
- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Location for the newly added object (array of 3 items, in [-inf, inf], optional)
- **rotation** ([`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler") | Sequence[float]) – Rotation, Rotation for the newly added object (array of 3 items, in [-inf, inf], optional)
- **scale** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Scale, Scale for the newly added object (array of 3 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.posemode_toggle"></a>

### bpy.ops.object.posemode_toggle()

Enable or disable posing/selecting bones

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.quadriflow_remesh"></a>

### bpy.ops.object.quadriflow_remesh(*, use_mesh_symmetry=True, use_preserve_sharp=False, use_preserve_boundary=False, preserve_attributes=False, smooth_normals=False, mode='FACES', target_ratio=1.0, target_edge_length=0.1, target_faces=4000, mesh_area=-1.0, seed=0)

Create a new quad based mesh using the surface data of the current mesh. All data layers will be lost

**Parameters:**

- **use_mesh_symmetry** (bool) – Use Mesh Symmetry, Generates a symmetrical mesh using the mesh symmetry configuration (optional)
- **use_preserve_sharp** (bool) – Preserve Sharp, Try to preserve sharp features on the mesh (optional)
- **use_preserve_boundary** (bool) – Preserve Mesh Boundary, Try to preserve mesh boundary on the mesh (optional)
- **preserve_attributes** (bool) – Preserve Attributes, Reproject attributes onto the new mesh (optional)
- **smooth_normals** (bool) – Smooth Normals, Set the output mesh normals to smooth (optional)
- **mode** (Literal['RATIO', 'EDGE', 'FACES']) –

  Mode, How to specify the amount of detail for the new mesh (optional)

  - `RATIO`
    Ratio – Specify target number of faces relative to the current mesh.
  - `EDGE`
    Edge Length – Input target edge length in the new mesh.
  - `FACES`
    Faces – Input target number of faces in the new mesh.
- **target_ratio** (float) – Ratio, Relative number of faces compared to the current mesh (in [0, inf], optional)
- **target_edge_length** (float) – Edge Length, Target edge length in the new mesh (in [1e-07, inf], optional)
- **target_faces** (int) – Number of Faces, Approximate number of faces (quads) in the new mesh (in [1, inf], optional)
- **mesh_area** (float) – Old Object Face Area, This property is only used to cache the object area for later calculations (in [-inf, inf], optional)
- **seed** (int) – Seed, Random seed to use with the solver. Different seeds will cause the remesher to come up with different quad layouts on the mesh (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.quick_explode"></a>

### bpy.ops.object.quick_explode(*, style='EXPLODE', amount=100, frame_duration=50, frame_start=1, frame_end=10, velocity=1.0, fade=True)

Make selected objects explode

**Parameters:**

- **style** (Literal['EXPLODE', 'BLEND']) – Explode Style, (optional)
- **amount** (int) – Number of Pieces, (in [2, 10000], optional)
- **frame_duration** (int) – Duration, (in [1, 300000], optional)
- **frame_start** (int) – Start Frame, (in [1, 300000], optional)
- **frame_end** (int) – End Frame, (in [1, 300000], optional)
- **velocity** (float) – Outwards Velocity, (in [0, 300000], optional)
- **fade** (bool) – Fade, Fade the pieces over time (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/object_quick_effects.py:280](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/object_quick_effects.py#L280)

<a id="bpy.ops.object.quick_fur"></a>

### bpy.ops.object.quick_fur(*, density='MEDIUM', length=0.1, radius=0.001, view_percentage=1.0, apply_hair_guides=True, use_noise=True, use_frizz=True)

Add a fur setup to the selected objects

**Parameters:**

- **density** (Literal['LOW', 'MEDIUM', 'HIGH']) – Density, (optional)
- **length** (float) – Length, (in [0.001, 100], optional)
- **radius** (float) – Hair Radius, (in [0, 10], optional)
- **view_percentage** (float) – View Percentage, (in [0, 1], optional)
- **apply_hair_guides** (bool) – Apply Hair Guides, (optional)
- **use_noise** (bool) – Noise, (optional)
- **use_frizz** (bool) – Frizz, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/object_quick_effects.py:103](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/object_quick_effects.py#L103)

<a id="bpy.ops.object.quick_liquid"></a>

### bpy.ops.object.quick_liquid(*, show_flows=False)

Make selected objects liquid

**Parameters:**

**show_flows** (bool) – Render Liquid Objects, Keep the liquid objects visible during rendering (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/object_quick_effects.py:556](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/object_quick_effects.py#L556)

<a id="bpy.ops.object.quick_smoke"></a>

### bpy.ops.object.quick_smoke(*, style='SMOKE', show_flows=False)

Use selected objects as smoke emitters

**Parameters:**

- **style** (Literal['SMOKE', 'FIRE', 'BOTH']) – Smoke Style, (optional)
- **show_flows** (bool) – Render Smoke Objects, Keep the smoke objects visible during rendering (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/object_quick_effects.py:454](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/object_quick_effects.py#L454)

<a id="bpy.ops.object.randomize_transform"></a>

### bpy.ops.object.randomize_transform(*, random_seed=0, use_delta=False, use_loc=True, loc=(0.0, 0.0, 0.0), use_rot=True, rot=(0.0, 0.0, 0.0), use_scale=True, scale_even=False, scale=(1.0, 1.0, 1.0))

Randomize objects location, rotation, and scale

**Parameters:**

- **random_seed** (int) – Random Seed, Seed value for the random generator (in [0, 10000], optional)
- **use_delta** (bool) – Transform Delta, Randomize delta transform values instead of regular transform (optional)
- **use_loc** (bool) – Randomize Location, Randomize the location values (optional)
- **loc** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Maximum distance the objects can spread over each axis (array of 3 items, in [-100, 100], optional)
- **use_rot** (bool) – Randomize Rotation, Randomize the rotation values (optional)
- **rot** ([`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler") | Sequence[float]) – Rotation, Maximum rotation over each axis (array of 3 items, in [-3.14159, 3.14159], optional)
- **use_scale** (bool) – Randomize Scale, Randomize the scale values (optional)
- **scale_even** (bool) – Scale Even, Use the same scale value for all axis (optional)
- **scale** (Sequence[float]) – Scale, Maximum scale randomization over each axis (array of 3 items, in [-100, 100], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/object_randomize_transform.py:163](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/object_randomize_transform.py#L163)

<a id="bpy.ops.object.reset_override_library"></a>

### bpy.ops.object.reset_override_library()

Reset the selected local overrides to their linked references values

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.rotation_clear"></a>

### bpy.ops.object.rotation_clear(*, clear_delta=False)

Clear the object’s rotation

**Parameters:**

**clear_delta** (bool) – Clear Delta, Clear delta rotation in addition to clearing the normal rotation transform (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.scale_clear"></a>

### bpy.ops.object.scale_clear(*, clear_delta=False)

Clear the object’s scale

**Parameters:**

**clear_delta** (bool) – Clear Delta, Clear delta scale in addition to clearing the normal scale transform (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.select_all"></a>

### bpy.ops.object.select_all(*, action='TOGGLE')

Change selection of all visible objects in scene

**Parameters:**

**action** (Literal['TOGGLE', 'SELECT', 'DESELECT', 'INVERT']) –

Action, Selection action to execute (optional)

- `TOGGLE`
  Toggle – Toggle selection for all elements.
- `SELECT`
  Select – Select all elements.
- `DESELECT`
  Deselect – Deselect all elements.
- `INVERT`
  Invert – Invert selection of all elements.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.select_by_type"></a>

### bpy.ops.object.select_by_type(*, extend=False, type='MESH')

Select all visible objects that are of a type

**Parameters:**

- **extend** (bool) – Extend, Extend selection instead of deselecting everything first (optional)
- **type** (Literal[[Object Type Items](bpy_types_enum_items/object_type_items.md#rna-enum-object-type-items)]) – Type, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.select_camera"></a>

### bpy.ops.object.select_camera(*, extend=False)

Select the active camera

**Parameters:**

**extend** (bool) – Extend, Extend the selection (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/object.py:124](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/object.py#L124)

<a id="bpy.ops.object.select_grouped"></a>

### bpy.ops.object.select_grouped(*, extend=False, type='CHILDREN_RECURSIVE')

Select all visible objects grouped by various properties

**Parameters:**

- **extend** (bool) – Extend, Extend selection instead of deselecting everything first (optional)
- **type** (Literal['CHILDREN_RECURSIVE', 'CHILDREN', 'PARENT', 'SIBLINGS', 'TYPE', 'COLLECTION', 'HOOK', 'PASS', 'COLOR', 'KEYINGSET', 'LIGHT_TYPE']) –

  Type, (optional)

  - `CHILDREN_RECURSIVE`
    Children.
  - `CHILDREN`
    Immediate Children.
  - `PARENT`
    Parent.
  - `SIBLINGS`
    Siblings – Shared parent.
  - `TYPE`
    Type – Shared object type.
  - `COLLECTION`
    Collection – Shared collection.
  - `HOOK`
    Hook.
  - `PASS`
    Pass – Render pass index.
  - `COLOR`
    Color – Object color.
  - `KEYINGSET`
    Keying Set – Objects included in active Keying Set.
  - `LIGHT_TYPE`
    Light Type – Matching light types.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.select_hierarchy"></a>

### bpy.ops.object.select_hierarchy(*, direction='PARENT', extend=False)

Select object relative to the active object’s position in the hierarchy

**Parameters:**

- **direction** (Literal['PARENT', 'CHILD']) – Direction, Direction to select in the hierarchy (optional)
- **extend** (bool) – Extend, Extend the existing selection (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/object.py:174](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/object.py#L174)

<a id="bpy.ops.object.select_less"></a>

### bpy.ops.object.select_less()

Deselect objects at the boundaries of parent/child relationships

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.select_linked"></a>

### bpy.ops.object.select_linked(*, extend=False, type='OBDATA')

Select all visible objects that are linked

**Parameters:**

- **extend** (bool) – Extend, Extend selection instead of deselecting everything first (optional)
- **type** (Literal['OBDATA', 'MATERIAL', 'DUPGROUP', 'PARTICLE', 'LIBRARY', 'LIBRARY_OBDATA']) – Type, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.select_mirror"></a>

### bpy.ops.object.select_mirror(*, extend=False)

Select the mirror objects of the selected object e.g. “L.sword” and “R.sword”

**Parameters:**

**extend** (bool) – Extend, Extend selection instead of deselecting everything first (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.select_more"></a>

### bpy.ops.object.select_more()

Select connected parent/child objects

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.select_pattern"></a>

### bpy.ops.object.select_pattern(*, pattern='*', case_sensitive=False, extend=True)

Select objects matching a naming pattern

**Parameters:**

- **pattern** (str) – Pattern, Name filter using ‘*’, ‘?’ and ‘[abc]’ unix style wildcards (optional, never None)
- **case_sensitive** (bool) – Case Sensitive, Do a case sensitive compare (optional)
- **extend** (bool) – Extend, Extend the existing selection (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/object.py:45](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/object.py#L45)

<a id="bpy.ops.object.select_random"></a>

### bpy.ops.object.select_random(*, ratio=0.5, seed=0, action='SELECT')

Select or deselect random visible objects

**Parameters:**

- **ratio** (float) – Ratio, Portion of items to select randomly (in [0, 1], optional)
- **seed** (int) – Random Seed, Seed for the random number generator (in [0, inf], optional)
- **action** (Literal['SELECT', 'DESELECT']) –

  Action, Selection action to execute (optional)

  - `SELECT`
    Select – Select all elements.
  - `DESELECT`
    Deselect – Deselect all elements.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.select_same_collection"></a>

### bpy.ops.object.select_same_collection(*, collection='')

Select object in the same collection

**Parameters:**

**collection** (str) – Collection, Name of the collection to select (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.shade_auto_smooth"></a>

### bpy.ops.object.shade_auto_smooth(*, use_auto_smooth=True, angle=0.523599)

Add modifier to automatically set the sharpness of mesh edges based on the angle between the neighboring faces

**Parameters:**

- **use_auto_smooth** (bool) – Auto Smooth, Add modifier to set edge sharpness automatically (optional)
- **angle** (float) – Angle, Maximum angle between face normals that will be considered as smooth (in [0, 3.14159], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.shade_flat"></a>

### bpy.ops.object.shade_flat(*, keep_sharp_edges=True)

Render and display faces uniform, using face normals

**Parameters:**

**keep_sharp_edges** (bool) – Keep Sharp Edges, Don’t remove sharp edges, which are redundant with faces shaded smooth (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.shade_smooth"></a>

### bpy.ops.object.shade_smooth(*, keep_sharp_edges=True)

Render and display faces smooth, using interpolated vertex normals

**Parameters:**

**keep_sharp_edges** (bool) – Keep Sharp Edges, Don’t remove sharp edges. Tagged edges will remain sharp (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.shade_smooth_by_angle"></a>

### bpy.ops.object.shade_smooth_by_angle(*, angle=0.523599, keep_sharp_edges=True)

Set the sharpness of mesh edges based on the angle between the neighboring faces

**Parameters:**

- **angle** (float) – Angle, Maximum angle between face normals that will be considered as smooth (in [0, 3.14159], optional)
- **keep_sharp_edges** (bool) – Keep Sharp Edges, Only add sharp edges instead of clearing existing tags first (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.shaderfx_add"></a>

### bpy.ops.object.shaderfx_add(*, type='FX_BLUR')

Add a visual effect to the active object

**Parameters:**

**type** (Literal[[Object Shaderfx Type Items](bpy_types_enum_items/object_shaderfx_type_items.md#rna-enum-object-shaderfx-type-items)]) – Type, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.shaderfx_copy"></a>

### bpy.ops.object.shaderfx_copy(*, shaderfx='')

Duplicate effect at the same position in the stack

**Parameters:**

**shaderfx** (str) – Shader, Name of the shaderfx to edit (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.shaderfx_move_down"></a>

### bpy.ops.object.shaderfx_move_down(*, shaderfx='')

Move effect down in the stack

**Parameters:**

**shaderfx** (str) – Shader, Name of the shaderfx to edit (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.shaderfx_move_to_index"></a>

### bpy.ops.object.shaderfx_move_to_index(*, shaderfx='', index=0)

Change the effect’s position in the list so it evaluates after the set number of others

**Parameters:**

- **shaderfx** (str) – Shader, Name of the shaderfx to edit (optional, never None)
- **index** (int) – Index, The index to move the effect to (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.shaderfx_move_up"></a>

### bpy.ops.object.shaderfx_move_up(*, shaderfx='')

Move effect up in the stack

**Parameters:**

**shaderfx** (str) – Shader, Name of the shaderfx to edit (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.shaderfx_remove"></a>

### bpy.ops.object.shaderfx_remove(*, shaderfx='', report=False)

Remove a effect from the active Grease Pencil object

**Parameters:**

- **shaderfx** (str) – Shader, Name of the shaderfx to edit (optional, never None)
- **report** (bool) – Report, Create a notification after the operation (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.shape_key_add"></a>

### bpy.ops.object.shape_key_add(*, from_mix=True)

Add shape key to the object

**Parameters:**

**from_mix** (bool) – From Mix, Create the new shape key from the existing mix of keys (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.shape_key_apply_to_basis"></a>

### bpy.ops.object.shape_key_apply_to_basis()

Apply deformations of selected shape keys to the basis key, removing them

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.shape_key_clear"></a>

### bpy.ops.object.shape_key_clear()

Reset the weights of all shape keys to 0 or to the closest value respecting the limits

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.shape_key_copy"></a>

### bpy.ops.object.shape_key_copy()

Duplicate the active shape key

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.shape_key_lock"></a>

### bpy.ops.object.shape_key_lock(*, action='LOCK')

Change the lock state of all shape keys of active object

**Parameters:**

**action** (Literal['LOCK', 'UNLOCK']) –

Action, Lock action to execute on vertex groups (optional)

- `LOCK`
  Lock – Lock all shape keys.
- `UNLOCK`
  Unlock – Unlock all shape keys.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.shape_key_make_basis"></a>

### bpy.ops.object.shape_key_make_basis()

Make this shape key the new basis key, effectively applying it to the mesh. Note that this applies the shape key at its 100% value

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.shape_key_mirror"></a>

### bpy.ops.object.shape_key_mirror(*, use_topology=False)

Mirror the current shape key along the local X axis

**Parameters:**

**use_topology** (bool) – Topology Mirror, Use topology based mirroring (for when both sides of mesh have matching, unique topology) (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.shape_key_move"></a>

### bpy.ops.object.shape_key_move(*, type='TOP')

Move selected shape keys up/down in the list

**Parameters:**

**type** (Literal['TOP', 'UP', 'DOWN', 'BOTTOM']) –

Type, (optional)

- `TOP`
  Top – Top of the list.
- `UP`
  Up.
- `DOWN`
  Down.
- `BOTTOM`
  Bottom – Bottom of the list.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.shape_key_remove"></a>

### bpy.ops.object.shape_key_remove(*, all=False, apply_mix=False)

Remove shape key from the object

**Parameters:**

- **all** (bool) – All, Remove all shape keys (optional)
- **apply_mix** (bool) – Apply Mix, Apply current mix of shape keys to the geometry before removing them (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.shape_key_retime"></a>

### bpy.ops.object.shape_key_retime()

Resets the timing for absolute shape keys

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.shape_key_transfer"></a>

### bpy.ops.object.shape_key_transfer(*, mode='OFFSET', use_clamp=False)

Copy the active shape key of another selected object to this one

**Parameters:**

- **mode** (Literal['OFFSET', 'RELATIVE_FACE', 'RELATIVE_EDGE']) –

  Transformation Mode, Relative shape positions to the new shape method (optional)

  - `OFFSET`
    Offset – Apply the relative positional offset.
  - `RELATIVE_FACE`
    Relative Face – Calculate relative position (using faces).
  - `RELATIVE_EDGE`
    Relative Edge – Calculate relative position (using edges).
- **use_clamp** (bool) – Clamp Offset, Clamp the transformation to the distance each vertex moves in the original shape (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/object.py:515](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/object.py#L515)

<a id="bpy.ops.object.simulation_nodes_cache_bake"></a>

### bpy.ops.object.simulation_nodes_cache_bake(*, selected=False)

Bake simulations in geometry nodes modifiers

**Parameters:**

**selected** (bool) – Selected, Bake cache on all selected objects (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.simulation_nodes_cache_calculate_to_frame"></a>

### bpy.ops.object.simulation_nodes_cache_calculate_to_frame(*, selected=False)

Calculate simulations in geometry nodes modifiers from the start to current frame

**Parameters:**

**selected** (bool) – Selected, Calculate all selected objects instead of just the active object (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.simulation_nodes_cache_delete"></a>

### bpy.ops.object.simulation_nodes_cache_delete(*, selected=False)

Delete cached/baked simulations in geometry nodes modifiers

**Parameters:**

**selected** (bool) – Selected, Delete cache on all selected objects (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.skin_armature_create"></a>

### bpy.ops.object.skin_armature_create(*, modifier='')

Create an armature that parallels the skin layout

**Parameters:**

**modifier** (str) – Modifier, Name of the modifier to edit (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.skin_loose_mark_clear"></a>

### bpy.ops.object.skin_loose_mark_clear(*, action='MARK')

Mark/clear selected vertices as loose

**Parameters:**

**action** (Literal['MARK', 'CLEAR']) –

Action, (optional)

- `MARK`
  Mark – Mark selected vertices as loose.
- `CLEAR`
  Clear – Set selected vertices as not loose.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.skin_radii_equalize"></a>

### bpy.ops.object.skin_radii_equalize()

Make skin radii of selected vertices equal on each axis

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.skin_root_mark"></a>

### bpy.ops.object.skin_root_mark()

Mark selected vertices as roots

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.speaker_add"></a>

### bpy.ops.object.speaker_add(*, enter_editmode=False, align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(0.0, 0.0, 0.0))

Add a speaker object to the scene

**Parameters:**

- **enter_editmode** (bool) – Enter Edit Mode, Enter edit mode when adding this object (optional)
- **align** (Literal['WORLD', 'VIEW', 'CURSOR']) –

  Align, The alignment of the new object (optional)

  - `WORLD`
    World – Align the new object to the world.
  - `VIEW`
    View – Align the new object to the view.
  - `CURSOR`
    3D Cursor – Use the 3D cursor orientation for the new object.
- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Location for the newly added object (array of 3 items, in [-inf, inf], optional)
- **rotation** ([`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler") | Sequence[float]) – Rotation, Rotation for the newly added object (array of 3 items, in [-inf, inf], optional)
- **scale** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Scale, Scale for the newly added object (array of 3 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.subdivision_set"></a>

### bpy.ops.object.subdivision_set(*, level=1, relative=False, ensure_modifier=True)

Sets a Subdivision Surface level (1 to 5)

**Parameters:**

- **level** (int) – Level, (in [-100, 100], optional)
- **relative** (bool) – Relative, Apply the subdivision surface level as an offset relative to the current level (optional)
- **ensure_modifier** (bool) – Ensure Modifier, Create the corresponding modifier if it does not exist (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/object.py:242](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/object.py#L242)

<a id="bpy.ops.object.surfacedeform_bind"></a>

### bpy.ops.object.surfacedeform_bind(*, modifier='')

Bind mesh to target in surface deform modifier

**Parameters:**

**modifier** (str) – Modifier, Name of the modifier to edit (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.text_add"></a>

### bpy.ops.object.text_add(*, radius=1.0, enter_editmode=False, align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(0.0, 0.0, 0.0))

Add a text object to the scene

**Parameters:**

- **radius** (float) – Radius, (in [0, inf], optional)
- **enter_editmode** (bool) – Enter Edit Mode, Enter edit mode when adding this object (optional)
- **align** (Literal['WORLD', 'VIEW', 'CURSOR']) –

  Align, The alignment of the new object (optional)

  - `WORLD`
    World – Align the new object to the world.
  - `VIEW`
    View – Align the new object to the view.
  - `CURSOR`
    3D Cursor – Use the 3D cursor orientation for the new object.
- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Location for the newly added object (array of 3 items, in [-inf, inf], optional)
- **rotation** ([`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler") | Sequence[float]) – Rotation, Rotation for the newly added object (array of 3 items, in [-inf, inf], optional)
- **scale** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Scale, Scale for the newly added object (array of 3 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.track_clear"></a>

### bpy.ops.object.track_clear(*, type='CLEAR')

Clear tracking constraint or flag from object

**Parameters:**

**type** (Literal['CLEAR', 'CLEAR_KEEP_TRANSFORM']) – Type, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.track_set"></a>

### bpy.ops.object.track_set(*, type='DAMPTRACK')

Make the object track another object, using various methods/constraints

**Parameters:**

**type** (Literal['DAMPTRACK', 'TRACKTO', 'LOCKTRACK']) – Type, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.transfer_mode"></a>

### bpy.ops.object.transfer_mode(*, use_flash_on_transfer=True)

Switches the active object and assigns the same mode to a new one under the mouse cursor, leaving the active mode in the current one

**Parameters:**

**use_flash_on_transfer** (bool) – Flash On Transfer, Flash the target object when transferring the mode (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.transform_apply"></a>

### bpy.ops.object.transform_apply(*, location=True, rotation=True, scale=True, properties=True, corrective_flip_normals=True, isolate_users=False)

Apply the object’s transformation to its data

**Parameters:**

- **location** (bool) – Location, (optional)
- **rotation** (bool) – Rotation, (optional)
- **scale** (bool) – Scale, (optional)
- **properties** (bool) – Apply Properties, Modify properties such as curve vertex radius, font size and bone envelope (optional)
- **corrective_flip_normals** (bool) – Corrective Flip Normals, Invert normals for negative scaled objects. (optional)
- **isolate_users** (bool) – Isolate Multi User Data, Create new object-data users if needed (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.transform_axis_target"></a>

### bpy.ops.object.transform_axis_target()

Interactively point cameras and lights to the surface under the pointer (Ctrl to translate)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.transform_to_mouse"></a>

### bpy.ops.object.transform_to_mouse(*, name='', session_uid=0, matrix=((0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0)), drop_x=0, drop_y=0)

Snap selected item(s) to the mouse location

**Parameters:**

- **name** (str) – Name, Object name to place (uses the active object when this and ‘session_uid’ are unset) (optional, never None)
- **session_uid** (int) – Session UUID, Session UUID of the object to place (uses the active object when this and ‘name’ are unset) (in [-inf, inf], optional)
- **matrix** ([`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix") | Sequence[Sequence[float]]) – Matrix, (multi-dimensional array of 4 * 4 items, in [-inf, inf], optional)
- **drop_x** (int) – Drop X, X-coordinate (screen space) to place the new object under (in [-inf, inf], optional)
- **drop_y** (int) – Drop Y, Y-coordinate (screen space) to place the new object under (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.transforms_to_deltas"></a>

### bpy.ops.object.transforms_to_deltas(*, mode='ALL', reset_values=True)

Convert normal object transforms to delta transforms, any existing delta transforms will be included as well

**Parameters:**

- **mode** (Literal['ALL', 'LOC', 'ROT', 'SCALE']) –

  Mode, Which transforms to transfer (optional)

  - `ALL`
    All Transforms – Transfer location, rotation, and scale transforms.
  - `LOC`
    Location – Transfer location transforms only.
  - `ROT`
    Rotation – Transfer rotation transforms only.
  - `SCALE`
    Scale – Transfer scale transforms only.
- **reset_values** (bool) – Reset Values, Clear transform values after transferring to deltas (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/object.py:777](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/object.py#L777)

<a id="bpy.ops.object.unlink_data"></a>

### bpy.ops.object.unlink_data()

Undocumented, consider [contributing](https://developer.blender.org/).

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.update_shapes"></a>

### bpy.ops.object.update_shapes(*, use_mirror=False)

Update existing shape keys with the vertex positions of selected objects with matching names

**Parameters:**

**use_mirror** (bool) – Mirror, Mirror the new shape key values (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.vertex_group_add"></a>

### bpy.ops.object.vertex_group_add()

Add a new vertex group to the active object

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.vertex_group_assign"></a>

### bpy.ops.object.vertex_group_assign()

Assign the selected vertices to the active vertex group

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.vertex_group_assign_new"></a>

### bpy.ops.object.vertex_group_assign_new()

Assign the selected vertices to a new vertex group

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.vertex_group_clean"></a>

### bpy.ops.object.vertex_group_clean(*, group_select_mode='', limit=0.0, keep_single=False)

Remove vertex group assignments which are not required

**Parameters:**

- **group_select_mode** (str) – Subset, Define which subset of groups shall be used (optional)
- **limit** (float) – Limit, Remove vertices which weight is below or equal to this limit (in [0, 1], optional)
- **keep_single** (bool) – Keep Single, Keep verts assigned to at least one group when cleaning (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.vertex_group_copy"></a>

### bpy.ops.object.vertex_group_copy()

Make a copy of the active vertex group

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.vertex_group_copy_to_selected"></a>

### bpy.ops.object.vertex_group_copy_to_selected()

Replace vertex groups of selected objects by vertex groups of active object

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.vertex_group_deselect"></a>

### bpy.ops.object.vertex_group_deselect()

Deselect all selected vertices assigned to the active vertex group

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.vertex_group_invert"></a>

### bpy.ops.object.vertex_group_invert(*, group_select_mode='', auto_assign=True, auto_remove=True)

Invert active vertex group’s weights

**Parameters:**

- **group_select_mode** (str) – Subset, Define which subset of groups shall be used (optional)
- **auto_assign** (bool) – Add Weights, Add vertices from groups that have zero weight before inverting (optional)
- **auto_remove** (bool) – Remove Weights, Remove vertices from groups that have zero weight after inverting (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.vertex_group_levels"></a>

### bpy.ops.object.vertex_group_levels(*, group_select_mode='', offset=0.0, gain=1.0)

Add some offset and multiply with some gain the weights of the active vertex group

**Parameters:**

- **group_select_mode** (str) – Subset, Define which subset of groups shall be used (optional)
- **offset** (float) – Offset, Value to add to weights (in [-1, 1], optional)
- **gain** (float) – Gain, Value to multiply weights by (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.vertex_group_limit_total"></a>

### bpy.ops.object.vertex_group_limit_total(*, group_select_mode='', limit=4)

Limit deform weights associated with a vertex to a specified number by removing lowest weights

**Parameters:**

- **group_select_mode** (str) – Subset, Define which subset of groups shall be used (optional)
- **limit** (int) – Limit, Maximum number of deform weights (in [1, 32], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.vertex_group_lock"></a>

### bpy.ops.object.vertex_group_lock(*, action='TOGGLE', mask='ALL')

Change the lock state of all or some vertex groups of active object

**Parameters:**

- **action** (Literal['TOGGLE', 'LOCK', 'UNLOCK', 'INVERT']) –

  Action, Lock action to execute on vertex groups (optional)

  - `TOGGLE`
    Toggle – Unlock all vertex groups if there is at least one locked group, lock all in other case.
  - `LOCK`
    Lock – Lock all vertex groups.
  - `UNLOCK`
    Unlock – Unlock all vertex groups.
  - `INVERT`
    Invert – Invert the lock state of all vertex groups.
- **mask** (Literal['ALL', 'SELECTED', 'UNSELECTED', 'INVERT_UNSELECTED']) –

  Mask, Apply the action based on vertex group selection (optional)

  - `ALL`
    All – Apply action to all vertex groups.
  - `SELECTED`
    Selected – Apply to selected vertex groups.
  - `UNSELECTED`
    Unselected – Apply to unselected vertex groups.
  - `INVERT_UNSELECTED`
    Invert Unselected – Apply the opposite of Lock/Unlock to unselected vertex groups.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.vertex_group_mirror"></a>

### bpy.ops.object.vertex_group_mirror(*, mirror_weights=True, flip_group_names=True, all_groups=False, use_topology=False)

Mirror vertex group, flip weights and/or names, editing only selected vertices, flipping when both sides are selected otherwise copy from unselected

**Parameters:**

- **mirror_weights** (bool) – Mirror Weights, Mirror weights (optional)
- **flip_group_names** (bool) – Flip Group Names, Flip vertex group names (optional)
- **all_groups** (bool) – All Groups, Mirror all vertex groups weights (optional)
- **use_topology** (bool) – Topology Mirror, Use topology based mirroring (for when both sides of mesh have matching, unique topology) (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.vertex_group_move"></a>

### bpy.ops.object.vertex_group_move(*, direction='UP')

Move the active vertex group up/down in the list

**Parameters:**

**direction** (Literal['UP', 'DOWN']) – Direction, Direction to move the active vertex group towards (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.vertex_group_normalize"></a>

### bpy.ops.object.vertex_group_normalize()

Normalize weights of the active vertex group, so that the highest ones are now 1.0

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.vertex_group_normalize_all"></a>

### bpy.ops.object.vertex_group_normalize_all(*, group_select_mode='', lock_active=True)

Normalize all weights of all vertex groups, so that for each vertex, the sum of all weights is 1.0

**Parameters:**

- **group_select_mode** (str) – Subset, Define which subset of groups shall be used (optional)
- **lock_active** (bool) – Lock Active, Keep the values of the active group while normalizing others (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.vertex_group_quantize"></a>

### bpy.ops.object.vertex_group_quantize(*, group_select_mode='', steps=4)

Set weights to a fixed number of steps

**Parameters:**

- **group_select_mode** (str) – Subset, Define which subset of groups shall be used (optional)
- **steps** (int) – Steps, Number of steps between 0 and 1 (in [1, 1000], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.vertex_group_remove"></a>

### bpy.ops.object.vertex_group_remove(*, all=False, all_unlocked=False)

Delete the active or all vertex groups from the active object

**Parameters:**

- **all** (bool) – All, Remove all vertex groups (optional)
- **all_unlocked** (bool) – All Unlocked, Remove all unlocked vertex groups (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.vertex_group_remove_from"></a>

### bpy.ops.object.vertex_group_remove_from(*, use_all_groups=False, use_all_verts=False)

Remove the selected vertices from active or all vertex group(s)

**Parameters:**

- **use_all_groups** (bool) – All Groups, Remove from all groups (optional)
- **use_all_verts** (bool) – All Vertices, Clear the active group (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.vertex_group_select"></a>

### bpy.ops.object.vertex_group_select()

Select all the vertices assigned to the active vertex group

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.vertex_group_set_active"></a>

### bpy.ops.object.vertex_group_set_active(*, group='')

Set the active vertex group

**Parameters:**

**group** (str) – Group, Vertex group to set as active (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.vertex_group_smooth"></a>

### bpy.ops.object.vertex_group_smooth(*, group_select_mode='', factor=0.5, repeat=1, expand=0.0)

Smooth weights for selected vertices

**Parameters:**

- **group_select_mode** (str) – Subset, Define which subset of groups shall be used (optional)
- **factor** (float) – Factor, (in [0, 1], optional)
- **repeat** (int) – Iterations, (in [1, 10000], optional)
- **expand** (float) – Expand/Contract, Expand/contract weights (in [-1, 1], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.vertex_group_sort"></a>

### bpy.ops.object.vertex_group_sort(*, sort_type='NAME')

Sort vertex groups

**Parameters:**

**sort_type** (Literal['NAME', 'BONE_HIERARCHY']) – Sort Type, Sort type (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.vertex_parent_set"></a>

### bpy.ops.object.vertex_parent_set()

Parent selected objects to the selected vertices

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.vertex_weight_copy"></a>

### bpy.ops.object.vertex_weight_copy()

Copy weights from active to selected

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.vertex_weight_delete"></a>

### bpy.ops.object.vertex_weight_delete(*, weight_group=-1)

Delete this weight from the vertex (disabled if vertex group is locked)

**Parameters:**

**weight_group** (int) – Weight Index, Index of source weight in active vertex group (in [-1, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.vertex_weight_normalize_active_vertex"></a>

### bpy.ops.object.vertex_weight_normalize_active_vertex()

Normalize active vertex’s weights

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.vertex_weight_paste"></a>

### bpy.ops.object.vertex_weight_paste(*, weight_group=-1)

Copy this group’s weight to other selected vertices (disabled if vertex group is locked)

**Parameters:**

**weight_group** (int) – Weight Index, Index of source weight in active vertex group (in [-1, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.vertex_weight_set_active"></a>

### bpy.ops.object.vertex_weight_set_active(*, weight_group=-1)

Set as active vertex group

**Parameters:**

**weight_group** (int) – Weight Index, Index of source weight in active vertex group (in [-1, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.visual_geometry_to_objects"></a>

### bpy.ops.object.visual_geometry_to_objects()

Convert geometry and instances into editable objects and collections

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.visual_transform_apply"></a>

### bpy.ops.object.visual_transform_apply()

Apply the object’s visual transformation to its data

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.volume_add"></a>

### bpy.ops.object.volume_add(*, align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(0.0, 0.0, 0.0))

Add a volume object to the scene

**Parameters:**

- **align** (Literal['WORLD', 'VIEW', 'CURSOR']) –

  Align, The alignment of the new object (optional)

  - `WORLD`
    World – Align the new object to the world.
  - `VIEW`
    View – Align the new object to the view.
  - `CURSOR`
    3D Cursor – Use the 3D cursor orientation for the new object.
- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Location for the newly added object (array of 3 items, in [-inf, inf], optional)
- **rotation** ([`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler") | Sequence[float]) – Rotation, Rotation for the newly added object (array of 3 items, in [-inf, inf], optional)
- **scale** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Scale, Scale for the newly added object (array of 3 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.volume_import"></a>

### bpy.ops.object.volume_import(*, filepath='', directory='', files=None, hide_props_region=True, check_existing=False, filter_blender=False, filter_backup=False, filter_image=False, filter_movie=False, filter_python=False, filter_font=False, filter_sound=False, filter_text=False, filter_archive=False, filter_btx=False, filter_alembic=False, filter_usd=False, filter_obj=False, filter_volume=True, filter_folder=True, filter_blenlib=False, filemode=9, relative_path=True, display_type='DEFAULT', sort_method='', use_sequence_detection=True, align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(0.0, 0.0, 0.0))

Import OpenVDB volume file

**Parameters:**

- **filepath** (str) – File Path, Path to file (optional, never None)
- **directory** (str) – Directory, Directory of the file (optional, never None)
- **files** (`bpy_prop_collection`[`OperatorFileListElement`] | None) – Files, (optional)
- **hide_props_region** (bool) – Hide Operator Properties, Collapse the region displaying the operator settings (optional)
- **check_existing** (bool) – Check Existing, Check and warn on overwriting existing files (optional)
- **filter_blender** (bool) – Filter .blend files, (optional)
- **filter_backup** (bool) – Filter backup .blend files, (optional)
- **filter_image** (bool) – Filter image files, (optional)
- **filter_movie** (bool) – Filter movie files, (optional)
- **filter_python** (bool) – Filter Python files, (optional)
- **filter_font** (bool) – Filter font files, (optional)
- **filter_sound** (bool) – Filter sound files, (optional)
- **filter_text** (bool) – Filter text files, (optional)
- **filter_archive** (bool) – Filter archive files, (optional)
- **filter_btx** (bool) – Filter btx files, (optional)
- **filter_alembic** (bool) – Filter Alembic files, (optional)
- **filter_usd** (bool) – Filter USD files, (optional)
- **filter_obj** (bool) – Filter OBJ files, (optional)
- **filter_volume** (bool) – Filter OpenVDB volume files, (optional)
- **filter_folder** (bool) – Filter folders, (optional)
- **filter_blenlib** (bool) – Filter Blender IDs, (optional)
- **filemode** (int) – File Browser Mode, The setting for the file browser mode to load a .blend file, a library or a special file (in [1, 9], optional)
- **relative_path** (bool) – Relative Path, Select the file relative to the blend file (optional)
- **display_type** (Literal['DEFAULT', 'LIST_VERTICAL', 'LIST_HORIZONTAL', 'THUMBNAIL']) –

  Display Type, (optional)

  - `DEFAULT`
    Default – Automatically determine display type for files.
  - `LIST_VERTICAL`
    Short List – Display files as short list.
  - `LIST_HORIZONTAL`
    Long List – Display files as a detailed list.
  - `THUMBNAIL`
    Thumbnails – Display files as thumbnails.
- **sort_method** (str) – File sorting mode, (optional)
- **use_sequence_detection** (bool) – Detect Sequences, Automatically detect animated sequences in selected volume files (based on file names) (optional)
- **align** (Literal['WORLD', 'VIEW', 'CURSOR']) –

  Align, The alignment of the new object (optional)

  - `WORLD`
    World – Align the new object to the world.
  - `VIEW`
    View – Align the new object to the view.
  - `CURSOR`
    3D Cursor – Use the 3D cursor orientation for the new object.
- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Location for the newly added object (array of 3 items, in [-inf, inf], optional)
- **rotation** ([`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler") | Sequence[float]) – Rotation, Rotation for the newly added object (array of 3 items, in [-inf, inf], optional)
- **scale** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Scale, Scale for the newly added object (array of 3 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.voxel_remesh"></a>

### bpy.ops.object.voxel_remesh()

Calculates a new manifold mesh based on the volume of the current mesh. All data layers will be lost

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.object.voxel_size_edit"></a>

### bpy.ops.object.voxel_size_edit()

Modify the mesh voxel size interactively used in the voxel remesher

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]
