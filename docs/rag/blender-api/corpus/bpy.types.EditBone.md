<!-- source: Blender Python API reference 5.2 / bpy.types.EditBone.html -->

<a id="editbone-bpy-struct"></a>

# EditBone(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.EditBone"></a>

### class bpy.types.EditBone(bpy_struct)

Edit mode bone in an armature data-block

<a id="bpy.types.EditBone.bbone_curveinx"></a>

#### bpy.types.EditBone.bbone_curveinx

X-axis handle offset for start of the B-Bone’s curve, adjusts curvature (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.EditBone.bbone_curveinz"></a>

#### bpy.types.EditBone.bbone_curveinz

Z-axis handle offset for start of the B-Bone’s curve, adjusts curvature (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.EditBone.bbone_curveoutx"></a>

#### bpy.types.EditBone.bbone_curveoutx

X-axis handle offset for end of the B-Bone’s curve, adjusts curvature (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.EditBone.bbone_curveoutz"></a>

#### bpy.types.EditBone.bbone_curveoutz

Z-axis handle offset for end of the B-Bone’s curve, adjusts curvature (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.EditBone.bbone_custom_handle_end"></a>

#### bpy.types.EditBone.bbone_custom_handle_end

Bone that serves as the end handle for the B-Bone curve

**Type:**

[`EditBone`](#bpy.types.EditBone "bpy.types.EditBone") | None

<a id="bpy.types.EditBone.bbone_custom_handle_start"></a>

#### bpy.types.EditBone.bbone_custom_handle_start

Bone that serves as the start handle for the B-Bone curve

**Type:**

[`EditBone`](#bpy.types.EditBone "bpy.types.EditBone") | None

<a id="bpy.types.EditBone.bbone_easein"></a>

#### bpy.types.EditBone.bbone_easein

Length of first Bézier Handle (for B-Bones only) (in [-inf, inf], default 1.0)

**Type:**

float

<a id="bpy.types.EditBone.bbone_easeout"></a>

#### bpy.types.EditBone.bbone_easeout

Length of second Bézier Handle (for B-Bones only) (in [-inf, inf], default 1.0)

**Type:**

float

<a id="bpy.types.EditBone.bbone_handle_type_end"></a>

#### bpy.types.EditBone.bbone_handle_type_end

Selects how the end handle of the B-Bone is computed (default `'AUTO'`)

- `AUTO`
  Automatic – Use connected parent and children to compute the handle.
- `ABSOLUTE`
  Absolute – Use the position of the specified bone to compute the handle.
- `RELATIVE`
  Relative – Use the offset of the specified bone from rest pose to compute the handle.
- `TANGENT`
  Tangent – Use the orientation of the specified bone to compute the handle, ignoring the location.

**Type:**

Literal[‘AUTO’, ‘ABSOLUTE’, ‘RELATIVE’, ‘TANGENT’]

<a id="bpy.types.EditBone.bbone_handle_type_start"></a>

#### bpy.types.EditBone.bbone_handle_type_start

Selects how the start handle of the B-Bone is computed (default `'AUTO'`)

- `AUTO`
  Automatic – Use connected parent and children to compute the handle.
- `ABSOLUTE`
  Absolute – Use the position of the specified bone to compute the handle.
- `RELATIVE`
  Relative – Use the offset of the specified bone from rest pose to compute the handle.
- `TANGENT`
  Tangent – Use the orientation of the specified bone to compute the handle, ignoring the location.

**Type:**

Literal[‘AUTO’, ‘ABSOLUTE’, ‘RELATIVE’, ‘TANGENT’]

<a id="bpy.types.EditBone.bbone_handle_use_ease_end"></a>

#### bpy.types.EditBone.bbone_handle_use_ease_end

Multiply the B-Bone Ease Out channel by the local Y scale value of the end handle. This is done after the Scale Easing option and isn’t affected by it. (default False)

**Type:**

bool

<a id="bpy.types.EditBone.bbone_handle_use_ease_start"></a>

#### bpy.types.EditBone.bbone_handle_use_ease_start

Multiply the B-Bone Ease In channel by the local Y scale value of the start handle. This is done after the Scale Easing option and isn’t affected by it. (default False)

**Type:**

bool

<a id="bpy.types.EditBone.bbone_handle_use_scale_end"></a>

#### bpy.types.EditBone.bbone_handle_use_scale_end

Multiply B-Bone Scale Out channels by the local scale values of the end handle. This is done after the Scale Easing option and isn’t affected by it. (array of 3 items, default (False, False, False))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[bool]

<a id="bpy.types.EditBone.bbone_handle_use_scale_start"></a>

#### bpy.types.EditBone.bbone_handle_use_scale_start

Multiply B-Bone Scale In channels by the local scale values of the start handle. This is done after the Scale Easing option and isn’t affected by it. (array of 3 items, default (False, False, False))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[bool]

<a id="bpy.types.EditBone.bbone_mapping_mode"></a>

#### bpy.types.EditBone.bbone_mapping_mode

Selects how the vertices are mapped to B-Bone segments based on their position (default `'STRAIGHT'`)

- `STRAIGHT`
  Straight – Fast mapping that is good for most situations, but ignores the rest pose curvature of the B-Bone.
- `CURVED`
  Curved – Slower mapping that gives better deformation for B-Bones that are sharply curved in rest pose.

**Type:**

Literal[‘STRAIGHT’, ‘CURVED’]

<a id="bpy.types.EditBone.bbone_rollin"></a>

#### bpy.types.EditBone.bbone_rollin

Roll offset for the start of the B-Bone, adjusts twist (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.EditBone.bbone_rollout"></a>

#### bpy.types.EditBone.bbone_rollout

Roll offset for the end of the B-Bone, adjusts twist (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.EditBone.bbone_scalein"></a>

#### bpy.types.EditBone.bbone_scalein

Scale factors for the start of the B-Bone, adjusts thickness (for tapering effects) (array of 3 items, in [-inf, inf], default (1.0, 1.0, 1.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.EditBone.bbone_scaleout"></a>

#### bpy.types.EditBone.bbone_scaleout

Scale factors for the end of the B-Bone, adjusts thickness (for tapering effects) (array of 3 items, in [-inf, inf], default (1.0, 1.0, 1.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.EditBone.bbone_segments"></a>

#### bpy.types.EditBone.bbone_segments

Number of subdivisions of bone (for B-Bones only) (in [1, 32], default 0)

**Type:**

int

<a id="bpy.types.EditBone.bbone_x"></a>

#### bpy.types.EditBone.bbone_x

B-Bone X size (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.EditBone.bbone_z"></a>

#### bpy.types.EditBone.bbone_z

B-Bone Z size (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.EditBone.collections"></a>

#### bpy.types.EditBone.collections

Bone Collections that contain this bone (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`BoneCollection`](bpy.types.BoneCollection.md#bpy.types.BoneCollection "bpy.types.BoneCollection")]

<a id="bpy.types.EditBone.color"></a>

#### bpy.types.EditBone.color

(readonly)

**Type:**

[`BoneColor`](bpy.types.BoneColor.md#bpy.types.BoneColor "bpy.types.BoneColor") | None

<a id="bpy.types.EditBone.display_type"></a>

#### bpy.types.EditBone.display_type

(default `'OCTAHEDRAL'`)

- `ARMATURE_DEFINED`
  Armature Defined – Use display mode from armature (default).
- `OCTAHEDRAL`
  Octahedral – Display bones as octahedral shape.
- `STICK`
  Stick – Display bones as simple 2D lines with dots.
- `BBONE`
  B-Bone – Display bones as boxes, showing subdivision and B-Splines.
- `ENVELOPE`
  Envelope – Display bones as extruded spheres, showing deformation influence volume.
- `WIRE`
  Wire – Display bones as thin wires, showing subdivision and B-Splines.

**Type:**

Literal[‘ARMATURE_DEFINED’, ‘OCTAHEDRAL’, ‘STICK’, ‘BBONE’, ‘ENVELOPE’, ‘WIRE’]

<a id="bpy.types.EditBone.envelope_distance"></a>

#### bpy.types.EditBone.envelope_distance

Bone deformation distance (for Envelope deform only) (in [0, 1000], default 0.0)

**Type:**

float

<a id="bpy.types.EditBone.envelope_weight"></a>

#### bpy.types.EditBone.envelope_weight

Bone deformation weight (for Envelope deform only) (in [0, 1000], default 0.0)

**Type:**

float

<a id="bpy.types.EditBone.head"></a>

#### bpy.types.EditBone.head

Location of head end of the bone (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.EditBone.head_radius"></a>

#### bpy.types.EditBone.head_radius

Radius of head of bone (for Envelope deform only) (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.EditBone.hide"></a>

#### bpy.types.EditBone.hide

Bone is not visible when in Edit Mode (default False)

**Type:**

bool

<a id="bpy.types.EditBone.hide_select"></a>

#### bpy.types.EditBone.hide_select

Bone is able to be selected (default False)

**Type:**

bool

<a id="bpy.types.EditBone.inherit_scale"></a>

#### bpy.types.EditBone.inherit_scale

Specifies how the bone inherits scaling from the parent bone (default `'FULL'`)

- `FULL`
  Full – Inherit all effects of parent scaling.
- `FIX_SHEAR`
  Fix Shear – Inherit scaling, but remove shearing of the child in the rest orientation.
- `ALIGNED`
  Aligned – Rotate non-uniform parent scaling to align with the child, applying parent X scale to child X axis, and so forth.
- `AVERAGE`
  Average – Inherit uniform scaling representing the overall change in the volume of the parent.
- `NONE`
  None – Completely ignore parent scaling.
- `NONE_LEGACY`
  None (Legacy) – Ignore parent scaling without compensating for parent shear. Replicates the effect of disabling the original Inherit Scale checkbox..

**Type:**

Literal[‘FULL’, ‘FIX_SHEAR’, ‘ALIGNED’, ‘AVERAGE’, ‘NONE’, ‘NONE_LEGACY’]

<a id="bpy.types.EditBone.length"></a>

#### bpy.types.EditBone.length

Length of the bone. Changing moves the tail end. (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.EditBone.lock"></a>

#### bpy.types.EditBone.lock

Bone is not able to be transformed when in Edit Mode (default False)

**Type:**

bool

<a id="bpy.types.EditBone.matrix"></a>

#### bpy.types.EditBone.matrix

Matrix combining location and rotation of the bone (head position, direction and roll), in armature space (does not include/support bone’s length/size) (multi-dimensional array of 4 * 4 items, in [-inf, inf], default ((0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0)))

**Type:**

[`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")

<a id="bpy.types.EditBone.name"></a>

#### bpy.types.EditBone.name

(default “”, never None)

**Type:**

str

<a id="bpy.types.EditBone.parent"></a>

#### bpy.types.EditBone.parent

Parent edit bone (in same Armature)

**Type:**

[`EditBone`](#bpy.types.EditBone "bpy.types.EditBone") | None

<a id="bpy.types.EditBone.roll"></a>

#### bpy.types.EditBone.roll

Bone rotation around head-tail axis (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.EditBone.select"></a>

#### bpy.types.EditBone.select

(default False)

**Type:**

bool

<a id="bpy.types.EditBone.select_head"></a>

#### bpy.types.EditBone.select_head

(default False)

**Type:**

bool

<a id="bpy.types.EditBone.select_tail"></a>

#### bpy.types.EditBone.select_tail

(default False)

**Type:**

bool

<a id="bpy.types.EditBone.show_wire"></a>

#### bpy.types.EditBone.show_wire

Bone is always displayed in wireframe regardless of viewport shading mode (useful for non-obstructive custom bone shapes) (default False)

**Type:**

bool

<a id="bpy.types.EditBone.tail"></a>

#### bpy.types.EditBone.tail

Location of tail end of the bone (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.EditBone.tail_radius"></a>

#### bpy.types.EditBone.tail_radius

Radius of tail of bone (for Envelope deform only) (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.EditBone.use_connect"></a>

#### bpy.types.EditBone.use_connect

When bone has a parent, bone’s head is stuck to the parent’s tail (default False)

**Type:**

bool

<a id="bpy.types.EditBone.use_cyclic_offset"></a>

#### bpy.types.EditBone.use_cyclic_offset

When bone does not have a parent, it receives cyclic offset effects (Deprecated) (default False)

**Type:**

bool

<a id="bpy.types.EditBone.use_deform"></a>

#### bpy.types.EditBone.use_deform

Enable Bone to deform geometry (default False)

**Type:**

bool

<a id="bpy.types.EditBone.use_endroll_as_inroll"></a>

#### bpy.types.EditBone.use_endroll_as_inroll

Add Roll Out of the Start Handle bone to the Roll In value (default False)

**Type:**

bool

<a id="bpy.types.EditBone.use_envelope_multiply"></a>

#### bpy.types.EditBone.use_envelope_multiply

When deforming bone, multiply effects of Vertex Group weights with Envelope influence (default False)

**Type:**

bool

<a id="bpy.types.EditBone.use_inherit_rotation"></a>

#### bpy.types.EditBone.use_inherit_rotation

Bone inherits rotation or scale from parent bone (default False)

**Type:**

bool

<a id="bpy.types.EditBone.use_local_location"></a>

#### bpy.types.EditBone.use_local_location

Bone location is set in local space (default False)

**Type:**

bool

<a id="bpy.types.EditBone.use_relative_parent"></a>

#### bpy.types.EditBone.use_relative_parent

Object children will use relative transform, like deform (default False)

**Type:**

bool

<a id="bpy.types.EditBone.use_scale_easing"></a>

#### bpy.types.EditBone.use_scale_easing

Multiply the final easing values by the Scale In/Out Y factors (default False)

**Type:**

bool

<a id="bpy.types.EditBone.basename"></a>

#### bpy.types.EditBone.basename

The name of this bone before any `.` character.

(readonly)

<a id="bpy.types.EditBone.center"></a>

#### bpy.types.EditBone.center

The midpoint between the head and the tail.

(readonly)

<a id="bpy.types.EditBone.children"></a>

#### bpy.types.EditBone.children

A list of all the bones children.

> **Note:**
>
> Takes `O(len(bones))` time.

(readonly)

<a id="bpy.types.EditBone.children_recursive"></a>

#### bpy.types.EditBone.children_recursive

A list of all children from this bone.

> **Note:**
>
> Takes `O(len(bones)**2)` time.

(readonly)

<a id="bpy.types.EditBone.children_recursive_basename"></a>

#### bpy.types.EditBone.children_recursive_basename

Returns a chain of children with the same base name as this bone.
Only direct chains are supported, forks caused by multiple children
with matching base names will terminate the function
and not be returned.

> **Note:**
>
> Takes `O(len(bones)**2)` time.

(readonly)

<a id="bpy.types.EditBone.parent_recursive"></a>

#### bpy.types.EditBone.parent_recursive

A list of parents, starting with the immediate parent.

(readonly)

<a id="bpy.types.EditBone.vector"></a>

#### bpy.types.EditBone.vector

The direction this bone is pointing.
Utility function for (tail - head)

(readonly)

<a id="bpy.types.EditBone.x_axis"></a>

#### bpy.types.EditBone.x_axis

Vector pointing down the x-axis of the bone.

(readonly)

<a id="bpy.types.EditBone.y_axis"></a>

#### bpy.types.EditBone.y_axis

Vector pointing down the y-axis of the bone.

(readonly)

<a id="bpy.types.EditBone.z_axis"></a>

#### bpy.types.EditBone.z_axis

Vector pointing down the z-axis of the bone.

(readonly)

<a id="bpy.types.EditBone.bl_system_properties_get"></a>

#### bpy.types.EditBone.bl_system_properties_get(*, do_create=False)

DEBUG ONLY. Internal access to runtime-defined RNA data storage, intended solely for testing and debugging purposes. Do not access it in regular scripting work, and in particular, do not assume that it contains writable data

**Parameters:**

**do_create** (bool) – Ensure that system properties are created if they do not exist yet (optional)

**Returns:**

The system properties root container, or None if there are no system properties stored in this data yet, and its creation was not requested

**Return type:**

[`PropertyGroup`](bpy.types.PropertyGroup.md#bpy.types.PropertyGroup "bpy.types.PropertyGroup")

<a id="bpy.types.EditBone.align_roll"></a>

#### bpy.types.EditBone.align_roll(vector)

Align the bone to a local-space roll so the Z axis points in the direction of the vector given

**Parameters:**

**vector** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Vector, (array of 3 items, in [-inf, inf])

<a id="bpy.types.EditBone.align_orientation"></a>

#### bpy.types.EditBone.align_orientation(other)

Align this bone to another by moving its tail and settings its roll
the length of the other bone is not used.

**Parameters:**

**other** (Self) – Bone to copy orientation from.

<a id="bpy.types.EditBone.parent_index"></a>

#### bpy.types.EditBone.parent_index(parent_test)

The same as ‘bone in other_bone.parent_recursive’
but saved generating a list.

**Parameters:**

**parent_test** (Self) – Bone to search for among this bone’s ancestors.

**Returns:**

1-based depth of parent_test in the parent chain, or 0 if not found.

**Return type:**

int

<a id="bpy.types.EditBone.transform"></a>

#### bpy.types.EditBone.transform(matrix, *, scale=True, roll=True)

Transform the bones head, tail, roll and envelope
(when the matrix has a scale component).

**Parameters:**

- **matrix** ([`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")) – 3x3 or 4x4 transformation matrix.
- **scale** (bool) – Scale the bone envelope by the matrix.
- **roll** (bool) – Correct the roll to point in the same relative
  direction to the head and tail.

<a id="bpy.types.EditBone.translate"></a>

#### bpy.types.EditBone.translate(vec)

Utility function to add *vec* to the head and tail of this bone.

**Parameters:**

**vec** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – Translation vector.

<a id="bpy.types.EditBone.bl_rna_get_subclass"></a>

#### classmethod bpy.types.EditBone.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.EditBone.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.EditBone.bl_rna_get_subclass_py(id, default=None, /)

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
| - `bpy.context.active_bone` - `bpy.context.edit_bone` - `bpy.context.editable_bones` - `bpy.context.selected_bones` - `bpy.context.selected_editable_bones` - `bpy.context.visible_bones` - [`Armature.edit_bones`](bpy.types.Armature.md#bpy.types.Armature.edit_bones "bpy.types.Armature.edit_bones") | - [`ArmatureEditBones.active`](bpy.types.ArmatureEditBones.md#bpy.types.ArmatureEditBones.active "bpy.types.ArmatureEditBones.active") - [`ArmatureEditBones.new`](bpy.types.ArmatureEditBones.md#bpy.types.ArmatureEditBones.new "bpy.types.ArmatureEditBones.new") - [`ArmatureEditBones.remove`](bpy.types.ArmatureEditBones.md#bpy.types.ArmatureEditBones.remove "bpy.types.ArmatureEditBones.remove") - [`EditBone.bbone_custom_handle_end`](#bpy.types.EditBone.bbone_custom_handle_end "bpy.types.EditBone.bbone_custom_handle_end") - [`EditBone.bbone_custom_handle_start`](#bpy.types.EditBone.bbone_custom_handle_start "bpy.types.EditBone.bbone_custom_handle_start") - [`EditBone.parent`](#bpy.types.EditBone.parent "bpy.types.EditBone.parent") |
