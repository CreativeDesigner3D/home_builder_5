<!-- source: Blender Python API reference 5.2 / bpy.types.ShrinkwrapConstraint.html -->

<a id="shrinkwrapconstraint-constraint"></a>

# ShrinkwrapConstraint(Constraint)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Constraint`](bpy.types.Constraint.md#bpy.types.Constraint "bpy.types.Constraint")

<a id="bpy.types.ShrinkwrapConstraint"></a>

### class bpy.types.ShrinkwrapConstraint(Constraint)

Create constraint-based shrinkwrap relationship

<a id="bpy.types.ShrinkwrapConstraint.cull_face"></a>

#### bpy.types.ShrinkwrapConstraint.cull_face

Stop vertices from projecting to a face on the target when facing towards/away (default `'OFF'`)

- `OFF`
  Off – No culling.
- `FRONT`
  Front – No projection when in front of the face.
- `BACK`
  Back – No projection when behind the face.

**Type:**

Literal[‘OFF’, ‘FRONT’, ‘BACK’]

<a id="bpy.types.ShrinkwrapConstraint.distance"></a>

#### bpy.types.ShrinkwrapConstraint.distance

Distance to Target (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.ShrinkwrapConstraint.project_axis"></a>

#### bpy.types.ShrinkwrapConstraint.project_axis

Axis constrain to (default `'POS_X'`)

**Type:**

Literal[[Object Axis Items](bpy_types_enum_items/object_axis_items.md#rna-enum-object-axis-items)]

<a id="bpy.types.ShrinkwrapConstraint.project_axis_space"></a>

#### bpy.types.ShrinkwrapConstraint.project_axis_space

Space for the projection axis (default `'WORLD'`)

- `WORLD`
  World Space – The constraint is applied relative to the world coordinate system.
- `CUSTOM`
  Custom Space – The constraint is applied in local space of a custom object/bone/vertex group.
- `POSE`
  Pose Space – The constraint is applied in Pose Space, the object transformation is ignored.
- `LOCAL_WITH_PARENT`
  Local With Parent – The constraint is applied relative to the rest pose local coordinate system of the bone, thus including the parent-induced transformation.
- `LOCAL`
  Local Space – The constraint is applied relative to the local coordinate system of the object.

**Type:**

Literal[‘WORLD’, ‘CUSTOM’, ‘POSE’, ‘LOCAL_WITH_PARENT’, ‘LOCAL’]

<a id="bpy.types.ShrinkwrapConstraint.project_limit"></a>

#### bpy.types.ShrinkwrapConstraint.project_limit

Limit the distance used for projection (zero disables) (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.ShrinkwrapConstraint.shrinkwrap_type"></a>

#### bpy.types.ShrinkwrapConstraint.shrinkwrap_type

Select type of shrinkwrap algorithm for target position (default `'NEAREST_SURFACE'`)

- `NEAREST_SURFACE`
  Nearest Surface Point – Shrink the location to the nearest target surface.
- `PROJECT`
  Project – Shrink the location to the nearest target surface along a given axis.
- `NEAREST_VERTEX`
  Nearest Vertex – Shrink the location to the nearest target vertex.
- `TARGET_PROJECT`
  Target Normal Project – Shrink the location to the nearest target surface along the interpolated vertex normals of the target.

**Type:**

Literal[‘NEAREST_SURFACE’, ‘PROJECT’, ‘NEAREST_VERTEX’, ‘TARGET_PROJECT’]

<a id="bpy.types.ShrinkwrapConstraint.target"></a>

#### bpy.types.ShrinkwrapConstraint.target

Target Mesh object

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.ShrinkwrapConstraint.track_axis"></a>

#### bpy.types.ShrinkwrapConstraint.track_axis

Axis that is aligned to the normal (default `'TRACK_X'`)

**Type:**

Literal[‘TRACK_X’, ‘TRACK_Y’, ‘TRACK_Z’, ‘TRACK_NEGATIVE_X’, ‘TRACK_NEGATIVE_Y’, ‘TRACK_NEGATIVE_Z’]

<a id="bpy.types.ShrinkwrapConstraint.use_invert_cull"></a>

#### bpy.types.ShrinkwrapConstraint.use_invert_cull

When projecting in the opposite direction invert the face cull mode (default False)

**Type:**

bool

<a id="bpy.types.ShrinkwrapConstraint.use_project_opposite"></a>

#### bpy.types.ShrinkwrapConstraint.use_project_opposite

Project in both specified and opposite directions (default False)

**Type:**

bool

<a id="bpy.types.ShrinkwrapConstraint.use_track_normal"></a>

#### bpy.types.ShrinkwrapConstraint.use_track_normal

Align the specified axis to the surface normal (default False)

**Type:**

bool

<a id="bpy.types.ShrinkwrapConstraint.wrap_mode"></a>

#### bpy.types.ShrinkwrapConstraint.wrap_mode

Select how to constrain the object to the target surface (default `'ON_SURFACE'`)

**Type:**

Literal[[Modifier Shrinkwrap Mode Items](bpy_types_enum_items/modifier_shrinkwrap_mode_items.md#rna-enum-modifier-shrinkwrap-mode-items)]

<a id="bpy.types.ShrinkwrapConstraint.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ShrinkwrapConstraint.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ShrinkwrapConstraint.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ShrinkwrapConstraint.bl_rna_get_subclass_py(id, default=None, /)

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
