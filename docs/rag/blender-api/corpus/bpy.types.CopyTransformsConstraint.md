<!-- source: Blender Python API reference 5.2 / bpy.types.CopyTransformsConstraint.html -->

<a id="copytransformsconstraint-constraint"></a>

# CopyTransformsConstraint(Constraint)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Constraint`](bpy.types.Constraint.md#bpy.types.Constraint "bpy.types.Constraint")

<a id="bpy.types.CopyTransformsConstraint"></a>

### class bpy.types.CopyTransformsConstraint(Constraint)

Copy all the transforms of the target

<a id="bpy.types.CopyTransformsConstraint.head_tail"></a>

#### bpy.types.CopyTransformsConstraint.head_tail

Target along length of bone: Head is 0, Tail is 1 (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.CopyTransformsConstraint.mix_mode"></a>

#### bpy.types.CopyTransformsConstraint.mix_mode

Specify how the copied and existing transformations are combined (default `'REPLACE'`)

- `REPLACE`
  Replace – Replace the original transformation with copied.
- `BEFORE_FULL`
  Before Original (Full) – Apply copied transformation before original, using simple matrix multiplication as if the constraint target is a parent in Full Inherit Scale mode. Will create shear when combining rotation and non-uniform scale..
- `BEFORE`
  Before Original (Aligned) – Apply copied transformation before original, as if the constraint target is a parent in Aligned Inherit Scale mode. This effectively uses Full for location and Split Channels for rotation and scale..
- `BEFORE_SPLIT`
  Before Original (Split Channels) – Apply copied transformation before original, handling location, rotation and scale separately, similar to a sequence of three Copy constraints.
- `AFTER_FULL`
  After Original (Full) – Apply copied transformation after original, using simple matrix multiplication as if the constraint target is a child in Full Inherit Scale mode. Will create shear when combining rotation and non-uniform scale..
- `AFTER`
  After Original (Aligned) – Apply copied transformation after original, as if the constraint target is a child in Aligned Inherit Scale mode. This effectively uses Full for location and Split Channels for rotation and scale..
- `AFTER_SPLIT`
  After Original (Split Channels) – Apply copied transformation after original, handling location, rotation and scale separately, similar to a sequence of three Copy constraints.

**Type:**

Literal[‘REPLACE’, ‘BEFORE_FULL’, ‘BEFORE’, ‘BEFORE_SPLIT’, ‘AFTER_FULL’, ‘AFTER’, ‘AFTER_SPLIT’]

<a id="bpy.types.CopyTransformsConstraint.remove_target_shear"></a>

#### bpy.types.CopyTransformsConstraint.remove_target_shear

Remove shear from the target transformation before combining (default False)

**Type:**

bool

<a id="bpy.types.CopyTransformsConstraint.subtarget"></a>

#### bpy.types.CopyTransformsConstraint.subtarget

Armature bone, mesh or lattice vertex group, … (default “”, never None)

**Type:**

str

<a id="bpy.types.CopyTransformsConstraint.target"></a>

#### bpy.types.CopyTransformsConstraint.target

Target object

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.CopyTransformsConstraint.use_bbone_shape"></a>

#### bpy.types.CopyTransformsConstraint.use_bbone_shape

Follow shape of B-Bone segments when calculating Head/Tail position (default False)

**Type:**

bool

<a id="bpy.types.CopyTransformsConstraint.bl_rna_get_subclass"></a>

#### classmethod bpy.types.CopyTransformsConstraint.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.CopyTransformsConstraint.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.CopyTransformsConstraint.bl_rna_get_subclass_py(id, default=None, /)

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
