<!-- source: Blender Python API reference 5.2 / bpy.types.ChildOfConstraint.html -->

<a id="childofconstraint-constraint"></a>

# ChildOfConstraint(Constraint)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Constraint`](bpy.types.Constraint.md#bpy.types.Constraint "bpy.types.Constraint")

<a id="bpy.types.ChildOfConstraint"></a>

### class bpy.types.ChildOfConstraint(Constraint)

Create constraint-based parent-child relationship

<a id="bpy.types.ChildOfConstraint.inverse_matrix"></a>

#### bpy.types.ChildOfConstraint.inverse_matrix

Transformation matrix to apply before (multi-dimensional array of 4 * 4 items, in [-inf, inf], default ((0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0)))

**Type:**

[`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")

<a id="bpy.types.ChildOfConstraint.set_inverse_pending"></a>

#### bpy.types.ChildOfConstraint.set_inverse_pending

Set to true to request recalculation of the inverse matrix (default False)

**Type:**

bool

<a id="bpy.types.ChildOfConstraint.subtarget"></a>

#### bpy.types.ChildOfConstraint.subtarget

Armature bone, mesh or lattice vertex group, … (default “”, never None)

**Type:**

str

<a id="bpy.types.ChildOfConstraint.target"></a>

#### bpy.types.ChildOfConstraint.target

Target object

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.ChildOfConstraint.use_location_x"></a>

#### bpy.types.ChildOfConstraint.use_location_x

Use X Location of Parent (default True)

**Type:**

bool

<a id="bpy.types.ChildOfConstraint.use_location_y"></a>

#### bpy.types.ChildOfConstraint.use_location_y

Use Y Location of Parent (default True)

**Type:**

bool

<a id="bpy.types.ChildOfConstraint.use_location_z"></a>

#### bpy.types.ChildOfConstraint.use_location_z

Use Z Location of Parent (default True)

**Type:**

bool

<a id="bpy.types.ChildOfConstraint.use_rotation_x"></a>

#### bpy.types.ChildOfConstraint.use_rotation_x

Use X Rotation of Parent (default True)

**Type:**

bool

<a id="bpy.types.ChildOfConstraint.use_rotation_y"></a>

#### bpy.types.ChildOfConstraint.use_rotation_y

Use Y Rotation of Parent (default True)

**Type:**

bool

<a id="bpy.types.ChildOfConstraint.use_rotation_z"></a>

#### bpy.types.ChildOfConstraint.use_rotation_z

Use Z Rotation of Parent (default True)

**Type:**

bool

<a id="bpy.types.ChildOfConstraint.use_scale_x"></a>

#### bpy.types.ChildOfConstraint.use_scale_x

Use X Scale of Parent (default True)

**Type:**

bool

<a id="bpy.types.ChildOfConstraint.use_scale_y"></a>

#### bpy.types.ChildOfConstraint.use_scale_y

Use Y Scale of Parent (default True)

**Type:**

bool

<a id="bpy.types.ChildOfConstraint.use_scale_z"></a>

#### bpy.types.ChildOfConstraint.use_scale_z

Use Z Scale of Parent (default True)

**Type:**

bool

<a id="bpy.types.ChildOfConstraint.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ChildOfConstraint.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ChildOfConstraint.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ChildOfConstraint.bl_rna_get_subclass_py(id, default=None, /)

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
