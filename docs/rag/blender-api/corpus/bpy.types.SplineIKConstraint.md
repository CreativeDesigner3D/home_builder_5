<!-- source: Blender Python API reference 5.2 / bpy.types.SplineIKConstraint.html -->

<a id="splineikconstraint-constraint"></a>

# SplineIKConstraint(Constraint)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Constraint`](bpy.types.Constraint.md#bpy.types.Constraint "bpy.types.Constraint")

<a id="bpy.types.SplineIKConstraint"></a>

### class bpy.types.SplineIKConstraint(Constraint)

Align ‘n’ bones along a curve

<a id="bpy.types.SplineIKConstraint.bulge"></a>

#### bpy.types.SplineIKConstraint.bulge

Factor between volume variation and stretching (in [0, 100], default 0.0)

**Type:**

float

<a id="bpy.types.SplineIKConstraint.bulge_max"></a>

#### bpy.types.SplineIKConstraint.bulge_max

Maximum volume stretching factor (in [1, 100], default 0.0)

**Type:**

float

<a id="bpy.types.SplineIKConstraint.bulge_min"></a>

#### bpy.types.SplineIKConstraint.bulge_min

Minimum volume stretching factor (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.SplineIKConstraint.bulge_smooth"></a>

#### bpy.types.SplineIKConstraint.bulge_smooth

Strength of volume stretching clamping (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.SplineIKConstraint.chain_count"></a>

#### bpy.types.SplineIKConstraint.chain_count

How many bones are included in the chain (in [1, 255], default 0)

**Type:**

int

<a id="bpy.types.SplineIKConstraint.joint_bindings"></a>

#### bpy.types.SplineIKConstraint.joint_bindings

(EXPERIENCED USERS ONLY) The relative positions of the joints along the chain, as percentages (array of 32 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.SplineIKConstraint.target"></a>

#### bpy.types.SplineIKConstraint.target

Curve that controls this relationship

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.SplineIKConstraint.use_bulge_max"></a>

#### bpy.types.SplineIKConstraint.use_bulge_max

Use upper limit for volume variation (default False)

**Type:**

bool

<a id="bpy.types.SplineIKConstraint.use_bulge_min"></a>

#### bpy.types.SplineIKConstraint.use_bulge_min

Use lower limit for volume variation (default False)

**Type:**

bool

<a id="bpy.types.SplineIKConstraint.use_chain_offset"></a>

#### bpy.types.SplineIKConstraint.use_chain_offset

Offset the entire chain relative to the root joint (default False)

**Type:**

bool

<a id="bpy.types.SplineIKConstraint.use_curve_radius"></a>

#### bpy.types.SplineIKConstraint.use_curve_radius

Average radius of the endpoints is used to tweak the X and Z Scaling of the bones, on top of XZ Scale mode (default True)

**Type:**

bool

<a id="bpy.types.SplineIKConstraint.use_even_divisions"></a>

#### bpy.types.SplineIKConstraint.use_even_divisions

Ignore the relative lengths of the bones when fitting to the curve (default False)

**Type:**

bool

<a id="bpy.types.SplineIKConstraint.use_original_scale"></a>

#### bpy.types.SplineIKConstraint.use_original_scale

Apply volume preservation over the original scaling (default False)

**Type:**

bool

<a id="bpy.types.SplineIKConstraint.xz_scale_mode"></a>

#### bpy.types.SplineIKConstraint.xz_scale_mode

Method used for determining the scaling of the X and Z axes of the bones (default `'NONE'`)

- `NONE`
  None – Don’t scale the X and Z axes.
- `BONE_ORIGINAL`
  Bone Original – Use the original scaling of the bones.
- `INVERSE_PRESERVE`
  Inverse Scale – Scale of the X and Z axes is the inverse of the Y-Scale.
- `VOLUME_PRESERVE`
  Volume Preservation – Scale of the X and Z axes are adjusted to preserve the volume of the bones.

**Type:**

Literal[‘NONE’, ‘BONE_ORIGINAL’, ‘INVERSE_PRESERVE’, ‘VOLUME_PRESERVE’]

<a id="bpy.types.SplineIKConstraint.y_scale_mode"></a>

#### bpy.types.SplineIKConstraint.y_scale_mode

Method used for determining the scaling of the Y axis of the bones, on top of the shape and scaling of the curve itself (default `'NONE'`)

- `NONE`
  None – Don’t scale in the Y axis.
- `FIT_CURVE`
  Fit Curve – Scale the bones to fit the entire length of the curve.
- `BONE_ORIGINAL`
  Bone Original – Use the original Y scale of the bone.

**Type:**

Literal[‘NONE’, ‘FIT_CURVE’, ‘BONE_ORIGINAL’]

<a id="bpy.types.SplineIKConstraint.bl_rna_get_subclass"></a>

#### classmethod bpy.types.SplineIKConstraint.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.SplineIKConstraint.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.SplineIKConstraint.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, Constraint.name, Constraint.type, Constraint.is_override_data, Constraint.owner_space, Constraint.target_space, Constraint.space_object, Constraint.space_subtarget, Constraint.mute, Constraint.enabled, Constraint.show_expanded, Constraint.is_valid, Constraint.active, Constraint.influence, Constraint.error_location, Constraint.error_rotation

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, Constraint.bl_rna_get_subclass, Constraint.bl_rna_get_subclass_py
