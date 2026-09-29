<!-- source: Blender Python API reference 5.2 / bpy.types.Bone.html -->

<a id="bone-bpy-struct"></a>

# Bone(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.Bone"></a>

### class bpy.types.Bone(bpy_struct)

Bone in an Armature data-block

<a id="bpy.types.Bone.bbone_curveinx"></a>

#### bpy.types.Bone.bbone_curveinx

X-axis handle offset for start of the B-Bone’s curve, adjusts curvature (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.Bone.bbone_curveinz"></a>

#### bpy.types.Bone.bbone_curveinz

Z-axis handle offset for start of the B-Bone’s curve, adjusts curvature (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.Bone.bbone_curveoutx"></a>

#### bpy.types.Bone.bbone_curveoutx

X-axis handle offset for end of the B-Bone’s curve, adjusts curvature (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.Bone.bbone_curveoutz"></a>

#### bpy.types.Bone.bbone_curveoutz

Z-axis handle offset for end of the B-Bone’s curve, adjusts curvature (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.Bone.bbone_custom_handle_end"></a>

#### bpy.types.Bone.bbone_custom_handle_end

Bone that serves as the end handle for the B-Bone curve

**Type:**

[`Bone`](#bpy.types.Bone "bpy.types.Bone") | None

<a id="bpy.types.Bone.bbone_custom_handle_start"></a>

#### bpy.types.Bone.bbone_custom_handle_start

Bone that serves as the start handle for the B-Bone curve

**Type:**

[`Bone`](#bpy.types.Bone "bpy.types.Bone") | None

<a id="bpy.types.Bone.bbone_easein"></a>

#### bpy.types.Bone.bbone_easein

Length of first Bézier Handle (for B-Bones only) (in [-inf, inf], default 1.0)

**Type:**

float

<a id="bpy.types.Bone.bbone_easeout"></a>

#### bpy.types.Bone.bbone_easeout

Length of second Bézier Handle (for B-Bones only) (in [-inf, inf], default 1.0)

**Type:**

float

<a id="bpy.types.Bone.bbone_handle_type_end"></a>

#### bpy.types.Bone.bbone_handle_type_end

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

<a id="bpy.types.Bone.bbone_handle_type_start"></a>

#### bpy.types.Bone.bbone_handle_type_start

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

<a id="bpy.types.Bone.bbone_handle_use_ease_end"></a>

#### bpy.types.Bone.bbone_handle_use_ease_end

Multiply the B-Bone Ease Out channel by the local Y scale value of the end handle. This is done after the Scale Easing option and isn’t affected by it. (default False)

**Type:**

bool

<a id="bpy.types.Bone.bbone_handle_use_ease_start"></a>

#### bpy.types.Bone.bbone_handle_use_ease_start

Multiply the B-Bone Ease In channel by the local Y scale value of the start handle. This is done after the Scale Easing option and isn’t affected by it. (default False)

**Type:**

bool

<a id="bpy.types.Bone.bbone_handle_use_scale_end"></a>

#### bpy.types.Bone.bbone_handle_use_scale_end

Multiply B-Bone Scale Out channels by the local scale values of the end handle. This is done after the Scale Easing option and isn’t affected by it. (array of 3 items, default (False, False, False))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[bool]

<a id="bpy.types.Bone.bbone_handle_use_scale_start"></a>

#### bpy.types.Bone.bbone_handle_use_scale_start

Multiply B-Bone Scale In channels by the local scale values of the start handle. This is done after the Scale Easing option and isn’t affected by it. (array of 3 items, default (False, False, False))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[bool]

<a id="bpy.types.Bone.bbone_mapping_mode"></a>

#### bpy.types.Bone.bbone_mapping_mode

Selects how the vertices are mapped to B-Bone segments based on their position (default `'STRAIGHT'`)

- `STRAIGHT`
  Straight – Fast mapping that is good for most situations, but ignores the rest pose curvature of the B-Bone.
- `CURVED`
  Curved – Slower mapping that gives better deformation for B-Bones that are sharply curved in rest pose.

**Type:**

Literal[‘STRAIGHT’, ‘CURVED’]

<a id="bpy.types.Bone.bbone_rollin"></a>

#### bpy.types.Bone.bbone_rollin

Roll offset for the start of the B-Bone, adjusts twist (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.Bone.bbone_rollout"></a>

#### bpy.types.Bone.bbone_rollout

Roll offset for the end of the B-Bone, adjusts twist (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.Bone.bbone_scalein"></a>

#### bpy.types.Bone.bbone_scalein

Scale factors for the start of the B-Bone, adjusts thickness (for tapering effects) (array of 3 items, in [-inf, inf], default (1.0, 1.0, 1.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.Bone.bbone_scaleout"></a>

#### bpy.types.Bone.bbone_scaleout

Scale factors for the end of the B-Bone, adjusts thickness (for tapering effects) (array of 3 items, in [-inf, inf], default (1.0, 1.0, 1.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.Bone.bbone_segments"></a>

#### bpy.types.Bone.bbone_segments

Number of subdivisions of bone (for B-Bones only) (in [1, 32], default 0)

**Type:**

int

<a id="bpy.types.Bone.bbone_x"></a>

#### bpy.types.Bone.bbone_x

B-Bone X size (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.Bone.bbone_z"></a>

#### bpy.types.Bone.bbone_z

B-Bone Z size (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.Bone.children"></a>

#### bpy.types.Bone.children

Bones which are children of this bone (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`Bone`](#bpy.types.Bone "bpy.types.Bone")]

<a id="bpy.types.Bone.collections"></a>

#### bpy.types.Bone.collections

Bone Collections that contain this bone (default None, readonly)

**Type:**

[`BoneCollectionMemberships`](bpy.types.BoneCollectionMemberships.md#bpy.types.BoneCollectionMemberships "bpy.types.BoneCollectionMemberships")[[`BoneCollection`](bpy.types.BoneCollection.md#bpy.types.BoneCollection "bpy.types.BoneCollection")]

<a id="bpy.types.Bone.color"></a>

#### bpy.types.Bone.color

(readonly)

**Type:**

[`BoneColor`](bpy.types.BoneColor.md#bpy.types.BoneColor "bpy.types.BoneColor") | None

<a id="bpy.types.Bone.display_type"></a>

#### bpy.types.Bone.display_type

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

<a id="bpy.types.Bone.envelope_distance"></a>

#### bpy.types.Bone.envelope_distance

Bone deformation distance (for Envelope deform only) (in [0, 1000], default 0.0)

**Type:**

float

<a id="bpy.types.Bone.envelope_weight"></a>

#### bpy.types.Bone.envelope_weight

Bone deformation weight (for Envelope deform only) (in [0, 1000], default 0.0)

**Type:**

float

<a id="bpy.types.Bone.head"></a>

#### bpy.types.Bone.head

Location of head end of the bone relative to its parent (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0), readonly)

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.Bone.head_local"></a>

#### bpy.types.Bone.head_local

Location of head end of the bone relative to armature (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0), readonly)

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.Bone.head_radius"></a>

#### bpy.types.Bone.head_radius

Radius of head of bone (for Envelope deform only) (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.Bone.hide"></a>

#### bpy.types.Bone.hide

Bone is not visible when it is in Edit Mode (default False)

**Type:**

bool

<a id="bpy.types.Bone.hide_select"></a>

#### bpy.types.Bone.hide_select

Bone is able to be selected (default False)

**Type:**

bool

<a id="bpy.types.Bone.inherit_scale"></a>

#### bpy.types.Bone.inherit_scale

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

<a id="bpy.types.Bone.length"></a>

#### bpy.types.Bone.length

Length of the bone (in [-inf, inf], default 0.0, readonly)

**Type:**

float

<a id="bpy.types.Bone.matrix"></a>

#### bpy.types.Bone.matrix

3×3 bone matrix (multi-dimensional array of 3 * 3 items, in [-inf, inf], default ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)), readonly)

**Type:**

[`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")

<a id="bpy.types.Bone.matrix_local"></a>

#### bpy.types.Bone.matrix_local

4×4 bone matrix relative to armature (multi-dimensional array of 4 * 4 items, in [-inf, inf], default ((0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0)), readonly)

**Type:**

[`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")

<a id="bpy.types.Bone.name"></a>

#### bpy.types.Bone.name

(default “”, never None)

**Type:**

str

<a id="bpy.types.Bone.parent"></a>

#### bpy.types.Bone.parent

Parent bone (in same Armature) (readonly)

**Type:**

[`Bone`](#bpy.types.Bone "bpy.types.Bone") | None

<a id="bpy.types.Bone.show_wire"></a>

#### bpy.types.Bone.show_wire

Bone is always displayed in wireframe regardless of viewport shading mode (useful for non-obstructive custom bone shapes) (default False)

**Type:**

bool

<a id="bpy.types.Bone.tail"></a>

#### bpy.types.Bone.tail

Location of tail end of the bone relative to its parent (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0), readonly)

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.Bone.tail_local"></a>

#### bpy.types.Bone.tail_local

Location of tail end of the bone relative to armature (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0), readonly)

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.Bone.tail_radius"></a>

#### bpy.types.Bone.tail_radius

Radius of tail of bone (for Envelope deform only) (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.Bone.use_connect"></a>

#### bpy.types.Bone.use_connect

When bone has a parent, bone’s head is stuck to the parent’s tail (default False, readonly)

**Type:**

bool

<a id="bpy.types.Bone.use_cyclic_offset"></a>

#### bpy.types.Bone.use_cyclic_offset

When bone does not have a parent, it receives cyclic offset effects (Deprecated) (default True)

**Type:**

bool

<a id="bpy.types.Bone.use_deform"></a>

#### bpy.types.Bone.use_deform

Enable Bone to deform geometry (default True)

**Type:**

bool

<a id="bpy.types.Bone.use_endroll_as_inroll"></a>

#### bpy.types.Bone.use_endroll_as_inroll

Add Roll Out of the Start Handle bone to the Roll In value (default False)

**Type:**

bool

<a id="bpy.types.Bone.use_envelope_multiply"></a>

#### bpy.types.Bone.use_envelope_multiply

When deforming bone, multiply effects of Vertex Group weights with Envelope influence (default False)

**Type:**

bool

<a id="bpy.types.Bone.use_inherit_rotation"></a>

#### bpy.types.Bone.use_inherit_rotation

Bone inherits rotation or scale from parent bone (default True)

**Type:**

bool

<a id="bpy.types.Bone.use_local_location"></a>

#### bpy.types.Bone.use_local_location

Bone location is set in local space (default True)

**Type:**

bool

<a id="bpy.types.Bone.use_relative_parent"></a>

#### bpy.types.Bone.use_relative_parent

Object children will use relative transform, like deform (default False)

**Type:**

bool

<a id="bpy.types.Bone.use_scale_easing"></a>

#### bpy.types.Bone.use_scale_easing

Multiply the final easing values by the Scale In/Out Y factors (default False)

**Type:**

bool

<a id="bpy.types.Bone.basename"></a>

#### bpy.types.Bone.basename

The name of this bone before any `.` character.

(readonly)

<a id="bpy.types.Bone.center"></a>

#### bpy.types.Bone.center

The midpoint between the head and the tail.

(readonly)

<a id="bpy.types.Bone.children_recursive"></a>

#### bpy.types.Bone.children_recursive

A list of all children from this bone.

> **Note:**
>
> Takes `O(len(bones)**2)` time.

(readonly)

<a id="bpy.types.Bone.children_recursive_basename"></a>

#### bpy.types.Bone.children_recursive_basename

Returns a chain of children with the same base name as this bone.
Only direct chains are supported, forks caused by multiple children
with matching base names will terminate the function
and not be returned.

> **Note:**
>
> Takes `O(len(bones)**2)` time.

(readonly)

<a id="bpy.types.Bone.parent_recursive"></a>

#### bpy.types.Bone.parent_recursive

A list of parents, starting with the immediate parent.

(readonly)

<a id="bpy.types.Bone.vector"></a>

#### bpy.types.Bone.vector

The direction this bone is pointing.
Utility function for (tail - head)

(readonly)

<a id="bpy.types.Bone.x_axis"></a>

#### bpy.types.Bone.x_axis

Vector pointing down the x-axis of the bone.

(readonly)

<a id="bpy.types.Bone.y_axis"></a>

#### bpy.types.Bone.y_axis

Vector pointing down the y-axis of the bone.

(readonly)

<a id="bpy.types.Bone.z_axis"></a>

#### bpy.types.Bone.z_axis

Vector pointing down the z-axis of the bone.

(readonly)

<a id="bpy.types.Bone.bl_system_properties_get"></a>

#### bpy.types.Bone.bl_system_properties_get(*, do_create=False)

DEBUG ONLY. Internal access to runtime-defined RNA data storage, intended solely for testing and debugging purposes. Do not access it in regular scripting work, and in particular, do not assume that it contains writable data

**Parameters:**

**do_create** (bool) – Ensure that system properties are created if they do not exist yet (optional)

**Returns:**

The system properties root container, or None if there are no system properties stored in this data yet, and its creation was not requested

**Return type:**

[`PropertyGroup`](bpy.types.PropertyGroup.md#bpy.types.PropertyGroup "bpy.types.PropertyGroup")

<a id="bpy.types.Bone.evaluate_envelope"></a>

#### bpy.types.Bone.evaluate_envelope(point)

Calculate bone envelope at given point

**Parameters:**

**point** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Point, Position in 3d space to evaluate (array of 3 items, in [-inf, inf])

**Returns:**

Factor, Envelope factor (in [-inf, inf])

**Return type:**

float

<a id="bpy.types.Bone.convert_local_to_pose"></a>

#### bpy.types.Bone.convert_local_to_pose(matrix, matrix_local, *, parent_matrix=((0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0)), parent_matrix_local=((0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0)), invert=False)

Transform a matrix from Local to Pose space (or back), taking into account options like Inherit Scale and Local Location. Unlike Object.convert_space, this uses custom rest and pose matrices provided by the caller. If the parent matrices are omitted, the bone is assumed to have no parent.

**Parameters:**

- **matrix** ([`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix") | Sequence[Sequence[float]]) – The matrix to transform (multi-dimensional array of 4 * 4 items, in [-inf, inf])
- **matrix_local** ([`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix") | Sequence[Sequence[float]]) – The custom rest matrix of this bone (Bone.matrix_local) (multi-dimensional array of 4 * 4 items, in [-inf, inf])
- **parent_matrix** ([`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix") | Sequence[Sequence[float]]) – The custom pose matrix of the parent bone (PoseBone.matrix) (multi-dimensional array of 4 * 4 items, in [-inf, inf], optional)
- **parent_matrix_local** ([`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix") | Sequence[Sequence[float]]) – The custom rest matrix of the parent bone (Bone.matrix_local) (multi-dimensional array of 4 * 4 items, in [-inf, inf], optional)
- **invert** (bool) – Convert from Pose to Local space (optional)

**Returns:**

The transformed matrix (multi-dimensional array of 4 * 4 items, in [-inf, inf])

**Return type:**

[`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")

This method enables conversions between Local and Pose space for bones in
the middle of updating the armature without having to update dependencies
after each change, by manually carrying updated matrices in a recursive walk.

```python
def set_pose_matrices(obj, matrix_map):
    "Assign pose space matrices of all bones at once, ignoring constraints."

    def rec(pbone, parent_matrix):
        if pbone.name in matrix_map:
            matrix = matrix_map[pbone.name]

            # # Instead of:
            # pbone.matrix = matrix
            # bpy.context.view_layer.update()

            # Compute and assign local matrix, using the new parent matrix.
            if pbone.parent:
                pbone.matrix_basis = pbone.bone.convert_local_to_pose(
                    matrix,
                    pbone.bone.matrix_local,
                    parent_matrix=parent_matrix,
                    parent_matrix_local=pbone.parent.bone.matrix_local,
                    invert=True
                )
            else:
                pbone.matrix_basis = pbone.bone.convert_local_to_pose(
                    matrix,
                    pbone.bone.matrix_local,
                    invert=True
                )
        else:
            # Compute the updated pose matrix from local and new parent matrix.
            if pbone.parent:
                matrix = pbone.bone.convert_local_to_pose(
                    pbone.matrix_basis,
                    pbone.bone.matrix_local,
                    parent_matrix=parent_matrix,
                    parent_matrix_local=pbone.parent.bone.matrix_local,
                )
            else:
                matrix = pbone.bone.convert_local_to_pose(
                    pbone.matrix_basis,
                    pbone.bone.matrix_local,
                )

        # Recursively process children, passing the new matrix through.
        for child in pbone.children:
            rec(child, matrix)

    # Scan all bone trees from their roots.
    for pbone in obj.pose.bones:
        if not pbone.parent:
            rec(pbone, None)
```

<a id="bpy.types.Bone.MatrixFromAxisRoll"></a>

#### classmethod bpy.types.Bone.MatrixFromAxisRoll(axis, roll)

Convert the axis + roll representation to a matrix

**Parameters:**

- **axis** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – The main axis of the bone (tail - head) (array of 3 items, in [-inf, inf], never None)
- **roll** (float) – The roll of the bone (in [-inf, inf])

**Returns:**

The resulting orientation matrix (multi-dimensional array of 3 * 3 items, in [-inf, inf])

**Return type:**

[`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")

<a id="bpy.types.Bone.AxisRollFromMatrix"></a>

#### classmethod bpy.types.Bone.AxisRollFromMatrix(matrix, *, axis=(0.0, 0.0, 0.0))

Convert a rotational matrix to the axis + roll representation. Note that the resulting value of the roll may not be as expected if the matrix has shear or negative determinant.

**Parameters:**

- **matrix** ([`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix") | Sequence[Sequence[float]]) – The orientation matrix of the bone (multi-dimensional array of 3 * 3 items, in [-inf, inf], never None)
- **axis** (Sequence[float]) – The optional override for the axis (finds closest approximation for the matrix) (array of 3 items, in [-inf, inf], optional)

**Returns:**

`result_axis`, The main axis of the bone, [`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

`result_roll`, The roll of the bone, float

**Return type:**

tuple[[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector"), float]

<a id="bpy.types.Bone.parent_index"></a>

#### bpy.types.Bone.parent_index(parent_test)

The same as ‘bone in other_bone.parent_recursive’
but saved generating a list.

**Parameters:**

**parent_test** (Self) – Bone to search for among this bone’s ancestors.

**Returns:**

1-based depth of parent_test in the parent chain, or 0 if not found.

**Return type:**

int

<a id="bpy.types.Bone.translate"></a>

#### bpy.types.Bone.translate(vec)

Utility function to add *vec* to the head and tail of this bone.

**Parameters:**

**vec** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – Translation vector.

<a id="bpy.types.Bone.bl_rna_get_subclass"></a>

#### classmethod bpy.types.Bone.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.Bone.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.Bone.bl_rna_get_subclass_py(id, default=None, /)

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
| - `bpy.context.active_bone` - `bpy.context.bone` - [`Armature.bones`](bpy.types.Armature.md#bpy.types.Armature.bones "bpy.types.Armature.bones") - [`ArmatureBones.active`](bpy.types.ArmatureBones.md#bpy.types.ArmatureBones.active "bpy.types.ArmatureBones.active") - [`Bone.bbone_custom_handle_end`](#bpy.types.Bone.bbone_custom_handle_end "bpy.types.Bone.bbone_custom_handle_end") | - [`Bone.bbone_custom_handle_start`](#bpy.types.Bone.bbone_custom_handle_start "bpy.types.Bone.bbone_custom_handle_start") - [`Bone.children`](#bpy.types.Bone.children "bpy.types.Bone.children") - [`Bone.parent`](#bpy.types.Bone.parent "bpy.types.Bone.parent") - [`BoneCollection.bones`](bpy.types.BoneCollection.md#bpy.types.BoneCollection.bones "bpy.types.BoneCollection.bones") - [`PoseBone.bone`](bpy.types.PoseBone.md#bpy.types.PoseBone.bone "bpy.types.PoseBone.bone") |
