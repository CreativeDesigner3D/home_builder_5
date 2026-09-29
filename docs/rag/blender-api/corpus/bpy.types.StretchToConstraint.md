<!-- source: Blender Python API reference 5.2 / bpy.types.StretchToConstraint.html -->

<a id="stretchtoconstraint-constraint"></a>

# StretchToConstraint(Constraint)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Constraint`](bpy.types.Constraint.md#bpy.types.Constraint "bpy.types.Constraint")

<a id="bpy.types.StretchToConstraint"></a>

### class bpy.types.StretchToConstraint(Constraint)

Stretch to meet the target object

<a id="bpy.types.StretchToConstraint.bulge"></a>

#### bpy.types.StretchToConstraint.bulge

Factor between volume variation and stretching (in [0, 100], default 0.0)

**Type:**

float

<a id="bpy.types.StretchToConstraint.bulge_max"></a>

#### bpy.types.StretchToConstraint.bulge_max

Maximum volume stretching factor (in [1, 100], default 0.0)

**Type:**

float

<a id="bpy.types.StretchToConstraint.bulge_min"></a>

#### bpy.types.StretchToConstraint.bulge_min

Minimum volume stretching factor (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.StretchToConstraint.bulge_smooth"></a>

#### bpy.types.StretchToConstraint.bulge_smooth

Strength of volume stretching clamping (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.StretchToConstraint.head_tail"></a>

#### bpy.types.StretchToConstraint.head_tail

Target along length of bone: Head is 0, Tail is 1 (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.StretchToConstraint.keep_axis"></a>

#### bpy.types.StretchToConstraint.keep_axis

The rotation type and axis order to use (default `'PLANE_X'`)

- `PLANE_X`
  XZ – Rotate around local X, then Z.
- `PLANE_Z`
  ZX – Rotate around local Z, then X.
- `SWING_Y`
  Swing – Use the smallest single axis rotation, similar to Damped Track.

**Type:**

Literal[‘PLANE_X’, ‘PLANE_Z’, ‘SWING_Y’]

<a id="bpy.types.StretchToConstraint.rest_length"></a>

#### bpy.types.StretchToConstraint.rest_length

Length at rest position (in [0, 1000], default 0.0)

**Type:**

float

<a id="bpy.types.StretchToConstraint.subtarget"></a>

#### bpy.types.StretchToConstraint.subtarget

Armature bone, mesh or lattice vertex group, … (default “”, never None)

**Type:**

str

<a id="bpy.types.StretchToConstraint.target"></a>

#### bpy.types.StretchToConstraint.target

Target object

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.StretchToConstraint.use_bbone_shape"></a>

#### bpy.types.StretchToConstraint.use_bbone_shape

Follow shape of B-Bone segments when calculating Head/Tail position (default False)

**Type:**

bool

<a id="bpy.types.StretchToConstraint.use_bulge_max"></a>

#### bpy.types.StretchToConstraint.use_bulge_max

Use upper limit for volume variation (default False)

**Type:**

bool

<a id="bpy.types.StretchToConstraint.use_bulge_min"></a>

#### bpy.types.StretchToConstraint.use_bulge_min

Use lower limit for volume variation (default False)

**Type:**

bool

<a id="bpy.types.StretchToConstraint.volume"></a>

#### bpy.types.StretchToConstraint.volume

Maintain the object’s volume as it stretches (default `'VOLUME_XZX'`)

**Type:**

Literal[‘VOLUME_XZX’, ‘VOLUME_X’, ‘VOLUME_Z’, ‘NO_VOLUME’]

<a id="bpy.types.StretchToConstraint.bl_rna_get_subclass"></a>

#### classmethod bpy.types.StretchToConstraint.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.StretchToConstraint.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.StretchToConstraint.bl_rna_get_subclass_py(id, default=None, /)

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
