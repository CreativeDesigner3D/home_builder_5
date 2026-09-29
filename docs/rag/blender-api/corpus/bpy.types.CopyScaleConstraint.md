<!-- source: Blender Python API reference 5.2 / bpy.types.CopyScaleConstraint.html -->

<a id="copyscaleconstraint-constraint"></a>

# CopyScaleConstraint(Constraint)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Constraint`](bpy.types.Constraint.md#bpy.types.Constraint "bpy.types.Constraint")

<a id="bpy.types.CopyScaleConstraint"></a>

### class bpy.types.CopyScaleConstraint(Constraint)

Copy the scale of the target

<a id="bpy.types.CopyScaleConstraint.power"></a>

#### bpy.types.CopyScaleConstraint.power

Raise the target’s scale to the specified power (in [-inf, inf], default 1.0)

**Type:**

float

<a id="bpy.types.CopyScaleConstraint.subtarget"></a>

#### bpy.types.CopyScaleConstraint.subtarget

Armature bone, mesh or lattice vertex group, … (default “”, never None)

**Type:**

str

<a id="bpy.types.CopyScaleConstraint.target"></a>

#### bpy.types.CopyScaleConstraint.target

Target object

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.CopyScaleConstraint.use_add"></a>

#### bpy.types.CopyScaleConstraint.use_add

Use addition instead of multiplication to combine scale (2.7 compatibility) (default True)

**Type:**

bool

<a id="bpy.types.CopyScaleConstraint.use_make_uniform"></a>

#### bpy.types.CopyScaleConstraint.use_make_uniform

Redistribute the copied change in volume equally between the three axes of the owner (default False)

**Type:**

bool

<a id="bpy.types.CopyScaleConstraint.use_offset"></a>

#### bpy.types.CopyScaleConstraint.use_offset

Combine original scale with copied scale (default False)

**Type:**

bool

<a id="bpy.types.CopyScaleConstraint.use_x"></a>

#### bpy.types.CopyScaleConstraint.use_x

Copy the target’s X scale (default False)

**Type:**

bool

<a id="bpy.types.CopyScaleConstraint.use_y"></a>

#### bpy.types.CopyScaleConstraint.use_y

Copy the target’s Y scale (default False)

**Type:**

bool

<a id="bpy.types.CopyScaleConstraint.use_z"></a>

#### bpy.types.CopyScaleConstraint.use_z

Copy the target’s Z scale (default False)

**Type:**

bool

<a id="bpy.types.CopyScaleConstraint.bl_rna_get_subclass"></a>

#### classmethod bpy.types.CopyScaleConstraint.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.CopyScaleConstraint.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.CopyScaleConstraint.bl_rna_get_subclass_py(id, default=None, /)

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
