<!-- source: Blender Python API reference 5.2 / bpy.types.Armature.html -->

<a id="armature-id"></a>

# Armature(ID)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")

<a id="bpy.types.Armature"></a>

### class bpy.types.Armature(ID)

Armature data-block containing a hierarchy of bones, usually used for rigging characters

<a id="bpy.types.Armature.animation_data"></a>

#### bpy.types.Armature.animation_data

Animation data for this data-block (readonly)

**Type:**

[`AnimData`](bpy.types.AnimData.md#bpy.types.AnimData "bpy.types.AnimData") | None

<a id="bpy.types.Armature.axes_position"></a>

#### bpy.types.Armature.axes_position

The position for the axes on the bone. Increasing the value moves it closer to the tip; decreasing moves it closer to the root. (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.Armature.bones"></a>

#### bpy.types.Armature.bones

(default None, readonly)

**Type:**

[`ArmatureBones`](bpy.types.ArmatureBones.md#bpy.types.ArmatureBones "bpy.types.ArmatureBones")[[`Bone`](bpy.types.Bone.md#bpy.types.Bone "bpy.types.Bone")]

<a id="bpy.types.Armature.collections"></a>

#### bpy.types.Armature.collections

(default None)

**Type:**

[`BoneCollections`](bpy.types.BoneCollections.md#bpy.types.BoneCollections "bpy.types.BoneCollections")[[`BoneCollection`](bpy.types.BoneCollection.md#bpy.types.BoneCollection "bpy.types.BoneCollection")]

<a id="bpy.types.Armature.collections_all"></a>

#### bpy.types.Armature.collections_all

List of all bone collections of the armature (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`BoneCollection`](bpy.types.BoneCollection.md#bpy.types.BoneCollection "bpy.types.BoneCollection")]

<a id="bpy.types.Armature.display_type"></a>

#### bpy.types.Armature.display_type

(default `'OCTAHEDRAL'`)

- `OCTAHEDRAL`
  Octahedral – Display bones as octahedral shape (default).
- `STICK`
  Stick – Display bones as simple 2D lines with dots.
- `BBONE`
  B-Bone – Display bones as boxes, showing subdivision and B-Splines.
- `ENVELOPE`
  Envelope – Display bones as extruded spheres, showing deformation influence volume.
- `WIRE`
  Wire – Display bones as thin wires, showing subdivision and B-Splines.

**Type:**

Literal[‘OCTAHEDRAL’, ‘STICK’, ‘BBONE’, ‘ENVELOPE’, ‘WIRE’]

<a id="bpy.types.Armature.edit_bones"></a>

#### bpy.types.Armature.edit_bones

(default None, readonly)

**Type:**

[`ArmatureEditBones`](bpy.types.ArmatureEditBones.md#bpy.types.ArmatureEditBones "bpy.types.ArmatureEditBones")[[`EditBone`](bpy.types.EditBone.md#bpy.types.EditBone "bpy.types.EditBone")]

<a id="bpy.types.Armature.is_editmode"></a>

#### bpy.types.Armature.is_editmode

True when used in editmode (default False, readonly)

**Type:**

bool

<a id="bpy.types.Armature.pose_position"></a>

#### bpy.types.Armature.pose_position

Show armature in binding pose or final posed state (default `'POSE'`)

- `POSE`
  Pose Position – Show armature in posed state.
- `REST`
  Rest Position – Show Armature in binding pose state (no posing possible).

**Type:**

Literal[‘POSE’, ‘REST’]

<a id="bpy.types.Armature.relation_line_position"></a>

#### bpy.types.Armature.relation_line_position

The start position of the relation lines from parent to child bones (default `'TAIL'`)

- `TAIL`
  Tail – Draw the relationship line from the parent tail to the child head.
- `HEAD`
  Head – Draw the relationship line from the parent head to the child head.

**Type:**

Literal[‘TAIL’, ‘HEAD’]

<a id="bpy.types.Armature.show_axes"></a>

#### bpy.types.Armature.show_axes

Display bone axes (default False)

**Type:**

bool

<a id="bpy.types.Armature.show_bone_colors"></a>

#### bpy.types.Armature.show_bone_colors

Display bone colors (default True)

**Type:**

bool

<a id="bpy.types.Armature.show_bone_custom_shapes"></a>

#### bpy.types.Armature.show_bone_custom_shapes

Display bones with their custom shapes (default True)

**Type:**

bool

<a id="bpy.types.Armature.show_names"></a>

#### bpy.types.Armature.show_names

Display bone names (default False)

**Type:**

bool

<a id="bpy.types.Armature.use_mirror_x"></a>

#### bpy.types.Armature.use_mirror_x

Apply changes to matching bone on opposite side of X-Axis (default False)

**Type:**

bool

<a id="bpy.types.Armature.transform"></a>

#### bpy.types.Armature.transform(matrix)

Transform armature bones by a matrix

**Parameters:**

**matrix** ([`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix") | Sequence[Sequence[float]]) – Matrix (multi-dimensional array of 4 * 4 items, in [-inf, inf])

<a id="bpy.types.Armature.bl_rna_get_subclass"></a>

#### classmethod bpy.types.Armature.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.Armature.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.Armature.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, ID.name, ID.name_full, ID.id_type, ID.session_uid, ID.is_evaluated, ID.original, ID.users, ID.use_fake_user, ID.use_extra_user, ID.is_embedded_data, ID.is_linked_packed, ID.is_missing, ID.is_runtime_data, ID.is_editable, ID.tag, ID.is_library_indirect, ID.library, ID.library_weak_reference, ID.asset_data, ID.override_library, ID.preview

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, ID.bl_system_properties_get, ID.rename, ID.evaluated_get, ID.copy, ID.asset_mark, ID.asset_clear, ID.asset_generate_preview, ID.override_create, ID.override_hierarchy_create, ID.user_clear, ID.user_remap, ID.make_local, ID.user_of_id, ID.animation_data_create, ID.animation_data_clear, ID.update_tag, ID.preview_ensure, ID.bl_rna_get_subclass, ID.bl_rna_get_subclass_py

<a id="references"></a>

## References

|  |  |
| --- | --- |
| - `bpy.context.armature` - [`BlendData.armatures`](bpy.types.BlendData.md#bpy.types.BlendData.armatures "bpy.types.BlendData.armatures") | - [`BlendDataArmatures.new`](bpy.types.BlendDataArmatures.md#bpy.types.BlendDataArmatures.new "bpy.types.BlendDataArmatures.new") - [`BlendDataArmatures.remove`](bpy.types.BlendDataArmatures.md#bpy.types.BlendDataArmatures.remove "bpy.types.BlendDataArmatures.remove") |
