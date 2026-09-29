<!-- source: Blender Python API reference 5.2 / bpy.types.CopyLocationConstraint.html -->

<a id="copylocationconstraint-constraint"></a>

# CopyLocationConstraint(Constraint)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Constraint`](bpy.types.Constraint.md#bpy.types.Constraint "bpy.types.Constraint")

<a id="bpy.types.CopyLocationConstraint"></a>

### class bpy.types.CopyLocationConstraint(Constraint)

Copy the location of the target

<a id="bpy.types.CopyLocationConstraint.head_tail"></a>

#### bpy.types.CopyLocationConstraint.head_tail

Target along length of bone: Head is 0, Tail is 1 (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.CopyLocationConstraint.invert_x"></a>

#### bpy.types.CopyLocationConstraint.invert_x

Invert the X location (default False)

**Type:**

bool

<a id="bpy.types.CopyLocationConstraint.invert_y"></a>

#### bpy.types.CopyLocationConstraint.invert_y

Invert the Y location (default False)

**Type:**

bool

<a id="bpy.types.CopyLocationConstraint.invert_z"></a>

#### bpy.types.CopyLocationConstraint.invert_z

Invert the Z location (default False)

**Type:**

bool

<a id="bpy.types.CopyLocationConstraint.subtarget"></a>

#### bpy.types.CopyLocationConstraint.subtarget

Armature bone, mesh or lattice vertex group, … (default “”, never None)

**Type:**

str

<a id="bpy.types.CopyLocationConstraint.target"></a>

#### bpy.types.CopyLocationConstraint.target

Target object

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.CopyLocationConstraint.use_bbone_shape"></a>

#### bpy.types.CopyLocationConstraint.use_bbone_shape

Follow shape of B-Bone segments when calculating Head/Tail position (default False)

**Type:**

bool

<a id="bpy.types.CopyLocationConstraint.use_offset"></a>

#### bpy.types.CopyLocationConstraint.use_offset

Add original location into copied location (default False)

**Type:**

bool

<a id="bpy.types.CopyLocationConstraint.use_x"></a>

#### bpy.types.CopyLocationConstraint.use_x

Copy the target’s X location (default False)

**Type:**

bool

<a id="bpy.types.CopyLocationConstraint.use_y"></a>

#### bpy.types.CopyLocationConstraint.use_y

Copy the target’s Y location (default False)

**Type:**

bool

<a id="bpy.types.CopyLocationConstraint.use_z"></a>

#### bpy.types.CopyLocationConstraint.use_z

Copy the target’s Z location (default False)

**Type:**

bool

<a id="bpy.types.CopyLocationConstraint.bl_rna_get_subclass"></a>

#### classmethod bpy.types.CopyLocationConstraint.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.CopyLocationConstraint.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.CopyLocationConstraint.bl_rna_get_subclass_py(id, default=None, /)

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
