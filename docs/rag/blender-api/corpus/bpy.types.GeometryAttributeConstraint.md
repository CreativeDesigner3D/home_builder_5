<!-- source: Blender Python API reference 5.2 / bpy.types.GeometryAttributeConstraint.html -->

<a id="geometryattributeconstraint-constraint"></a>

# GeometryAttributeConstraint(Constraint)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Constraint`](bpy.types.Constraint.md#bpy.types.Constraint "bpy.types.Constraint")

<a id="bpy.types.GeometryAttributeConstraint"></a>

### class bpy.types.GeometryAttributeConstraint(Constraint)

Create a constraint-based relationship with an attribute from geometry

<a id="bpy.types.GeometryAttributeConstraint.apply_target_transform"></a>

#### bpy.types.GeometryAttributeConstraint.apply_target_transform

Apply the target object’s world transform on top of the attribute’s transform (default False)

**Type:**

bool

<a id="bpy.types.GeometryAttributeConstraint.attribute_name"></a>

#### bpy.types.GeometryAttributeConstraint.attribute_name

Name of the attribute to retrieve the transform from (default “”, never None)

**Type:**

str

<a id="bpy.types.GeometryAttributeConstraint.data_type"></a>

#### bpy.types.GeometryAttributeConstraint.data_type

Select data type of attribute (default `'VECTOR'`)

- `VECTOR`
  Vector – Vector data type, affects position.
- `QUATERNION`
  Quaternion – Quaternion data type, affects rotation.
- `FLOAT4X4`
  4x4 Matrix – 4x4 Matrix data type, affects transform.

**Type:**

Literal[‘VECTOR’, ‘QUATERNION’, ‘FLOAT4X4’]

<a id="bpy.types.GeometryAttributeConstraint.domain"></a>

#### bpy.types.GeometryAttributeConstraint.domain

Attribute domain (default `'POINT'`)

**Type:**

Literal[‘POINT’, ‘EDGE’, ‘FACE’, ‘FACE_CORNER’, ‘CURVE’, ‘INSTANCE’]

<a id="bpy.types.GeometryAttributeConstraint.mix_loc"></a>

#### bpy.types.GeometryAttributeConstraint.mix_loc

Mix Location (default False)

**Type:**

bool

<a id="bpy.types.GeometryAttributeConstraint.mix_mode"></a>

#### bpy.types.GeometryAttributeConstraint.mix_mode

Specify how the copied and existing transformations are combined (default `'REPLACE'`)

- `REPLACE`
  Replace – Replace the original transformation with the transform from the attribute.
- `BEFORE_FULL`
  Before Original (Full) – Apply copied transformation before original, using simple matrix multiplication as if the constraint target is a parent in Full Inherit Scale mode. Will create shear when combining rotation and non-uniform scale..
- `BEFORE_SPLIT`
  Before Original (Split Channels) – Apply copied transformation before original, handling location, rotation and scale separately, similar to a sequence of three Copy constraints.
- `AFTER_FULL`
  After Original (Full) – Apply copied transformation after original, using simple matrix multiplication as if the constraint target is a child in Full Inherit Scale mode. Will create shear when combining rotation and non-uniform scale..
- `AFTER_SPLIT`
  After Original (Split Channels) – Apply copied transformation after original, handling location, rotation and scale separately, similar to a sequence of three Copy constraints.

**Type:**

Literal[‘REPLACE’, ‘BEFORE_FULL’, ‘BEFORE_SPLIT’, ‘AFTER_FULL’, ‘AFTER_SPLIT’]

<a id="bpy.types.GeometryAttributeConstraint.mix_rot"></a>

#### bpy.types.GeometryAttributeConstraint.mix_rot

Mix Rotation (default False)

**Type:**

bool

<a id="bpy.types.GeometryAttributeConstraint.mix_scl"></a>

#### bpy.types.GeometryAttributeConstraint.mix_scl

Mix Scale (default False)

**Type:**

bool

<a id="bpy.types.GeometryAttributeConstraint.sample_index"></a>

#### bpy.types.GeometryAttributeConstraint.sample_index

Sample Index (in [0, inf], default 0)

**Type:**

int

<a id="bpy.types.GeometryAttributeConstraint.target"></a>

#### bpy.types.GeometryAttributeConstraint.target

Target geometry object

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.GeometryAttributeConstraint.bl_rna_get_subclass"></a>

#### classmethod bpy.types.GeometryAttributeConstraint.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.GeometryAttributeConstraint.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.GeometryAttributeConstraint.bl_rna_get_subclass_py(id, default=None, /)

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
