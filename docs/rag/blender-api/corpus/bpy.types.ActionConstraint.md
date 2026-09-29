<!-- source: Blender Python API reference 5.2 / bpy.types.ActionConstraint.html -->

<a id="actionconstraint-constraint"></a>

# ActionConstraint(Constraint)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Constraint`](bpy.types.Constraint.md#bpy.types.Constraint "bpy.types.Constraint")

<a id="bpy.types.ActionConstraint"></a>

### class bpy.types.ActionConstraint(Constraint)

Map an action to the transform axes of a bone

<a id="bpy.types.ActionConstraint.action"></a>

#### bpy.types.ActionConstraint.action

The constraining action

**Type:**

[`Action`](bpy.types.Action.md#bpy.types.Action "bpy.types.Action") | None

<a id="bpy.types.ActionConstraint.action_slot"></a>

#### bpy.types.ActionConstraint.action_slot

The slot identifies which sub-set of the Action is considered to be for this strip, and its name is used to find the right slot when assigning another Action

**Type:**

[`ActionSlot`](bpy.types.ActionSlot.md#bpy.types.ActionSlot "bpy.types.ActionSlot") | None

<a id="bpy.types.ActionConstraint.action_slot_handle"></a>

#### bpy.types.ActionConstraint.action_slot_handle

A number that identifies which sub-set of the Action is considered to be for this Action Constraint (in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.ActionConstraint.action_suitable_slots"></a>

#### bpy.types.ActionConstraint.action_suitable_slots

The list of action slots suitable for this NLA strip (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`ActionSlot`](bpy.types.ActionSlot.md#bpy.types.ActionSlot "bpy.types.ActionSlot")]

<a id="bpy.types.ActionConstraint.eval_time"></a>

#### bpy.types.ActionConstraint.eval_time

Interpolates between Action Start and End frames (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.ActionConstraint.frame_end"></a>

#### bpy.types.ActionConstraint.frame_end

Last frame of the Action to use (in [-1048574, 1048574], default 0)

**Type:**

int

<a id="bpy.types.ActionConstraint.frame_start"></a>

#### bpy.types.ActionConstraint.frame_start

First frame of the Action to use (in [-1048574, 1048574], default 0)

**Type:**

int

<a id="bpy.types.ActionConstraint.last_slot_identifier"></a>

#### bpy.types.ActionConstraint.last_slot_identifier

The identifier of the most recently assigned action slot. The slot identifies which sub-set of the Action is considered to be for this constraint, and its identifier is used to find the right slot when assigning an Action. (default “”, never None)

**Type:**

str

<a id="bpy.types.ActionConstraint.max"></a>

#### bpy.types.ActionConstraint.max

Maximum value for target channel range (in [-1000, 1000], default 0.0)

**Type:**

float

<a id="bpy.types.ActionConstraint.min"></a>

#### bpy.types.ActionConstraint.min

Minimum value for target channel range (in [-1000, 1000], default 0.0)

**Type:**

float

<a id="bpy.types.ActionConstraint.mix_mode"></a>

#### bpy.types.ActionConstraint.mix_mode

Specify how existing transformations and the action channels are combined (default `'AFTER_FULL'`)

- `REPLACE`
  Replace – Replace the original transformation with the action channels.
- `BEFORE_FULL`
  Before Original (Full) – Apply the action channels before the original transformation, as if applied to an imaginary parent in Full Inherit Scale mode. Will create shear when combining rotation and non-uniform scale..
- `BEFORE`
  Before Original (Aligned) – Apply the action channels before the original transformation, as if applied to an imaginary parent in Aligned Inherit Scale mode. This effectively uses Full for location and Split Channels for rotation and scale..
- `BEFORE_SPLIT`
  Before Original (Split Channels) – Apply the action channels before the original transformation, handling location, rotation and scale separately.
- `AFTER_FULL`
  After Original (Full) – Apply the action channels after the original transformation, as if applied to an imaginary child in Full Inherit Scale mode. Will create shear when combining rotation and non-uniform scale..
- `AFTER`
  After Original (Aligned) – Apply the action channels after the original transformation, as if applied to an imaginary child in Aligned Inherit Scale mode. This effectively uses Full for location and Split Channels for rotation and scale..
- `AFTER_SPLIT`
  After Original (Split Channels) – Apply the action channels after the original transformation, handling location, rotation and scale separately.

**Type:**

Literal[‘REPLACE’, ‘BEFORE_FULL’, ‘BEFORE’, ‘BEFORE_SPLIT’, ‘AFTER_FULL’, ‘AFTER’, ‘AFTER_SPLIT’]

<a id="bpy.types.ActionConstraint.subtarget"></a>

#### bpy.types.ActionConstraint.subtarget

Armature bone, mesh or lattice vertex group, … (default “”, never None)

**Type:**

str

<a id="bpy.types.ActionConstraint.target"></a>

#### bpy.types.ActionConstraint.target

Target object

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.ActionConstraint.transform_channel"></a>

#### bpy.types.ActionConstraint.transform_channel

Transformation channel from the target that is used to key the Action (default `'ROTATION_X'`)

**Type:**

Literal[‘LOCATION_X’, ‘LOCATION_Y’, ‘LOCATION_Z’, ‘ROTATION_X’, ‘ROTATION_Y’, ‘ROTATION_Z’, ‘SCALE_X’, ‘SCALE_Y’, ‘SCALE_Z’]

<a id="bpy.types.ActionConstraint.use_bone_object_action"></a>

#### bpy.types.ActionConstraint.use_bone_object_action

Bones only: apply the object’s transformation channels of the action to the constrained bone, instead of bone’s channels (default False)

**Type:**

bool

<a id="bpy.types.ActionConstraint.use_eval_time"></a>

#### bpy.types.ActionConstraint.use_eval_time

Interpolate between Action Start and End frames, with the Evaluation Time slider instead of the Target object/bone (default False)

**Type:**

bool

<a id="bpy.types.ActionConstraint.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ActionConstraint.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ActionConstraint.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ActionConstraint.bl_rna_get_subclass_py(id, default=None, /)

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
