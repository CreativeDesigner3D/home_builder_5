<!-- source: Blender Python API reference 5.2 / bpy_extras.anim_utils.html -->

<a id="module-bpy_extras.anim_utils"></a>

# bpy_extras submodule (bpy_extras.anim_utils)

<a id="bpy_extras.anim_utils.action_get_channelbag_for_slot"></a>

### bpy_extras.anim_utils.action_get_channelbag_for_slot(action, slot)

Returns the first channelbag found for the slot.
In case there are multiple layers or strips they are iterated until a
channelbag for that slot is found. In case no matching channelbag is found, returns None.

**Parameters:**

- **action** ([`bpy.types.Action`](bpy.types.Action.md#bpy.types.Action "bpy.types.Action") | None) – Action to search.
- **slot** ([`bpy.types.ActionSlot`](bpy.types.ActionSlot.md#bpy.types.ActionSlot "bpy.types.ActionSlot") | None) – Slot to look up.

**Returns:**

The first matching channelbag, or None when not found or when action or slot is None.

**Return type:**

[`bpy.types.ActionChannelbag`](bpy.types.ActionChannelbag.md#bpy.types.ActionChannelbag "bpy.types.ActionChannelbag") | None

<a id="bpy_extras.anim_utils.action_get_first_suitable_slot"></a>

### bpy_extras.anim_utils.action_get_first_suitable_slot(action, target_id_type)

Return the first Slot of the given Action that’s suitable for the given ID type.

Typically you should not need this function; when an Action is assigned to a
data-block, just use the slot that was assigned along with it.

**Parameters:**

- **action** ([`bpy.types.Action`](bpy.types.Action.md#bpy.types.Action "bpy.types.Action") | None) – Action to search.
- **target_id_type** (str) – ID type identifier the slot must accept (e.g. `'OBJECT'`).

**Returns:**

The first suitable slot, or None when none match or when action is None.

**Return type:**

[`bpy.types.ActionSlot`](bpy.types.ActionSlot.md#bpy.types.ActionSlot "bpy.types.ActionSlot") | None

<a id="bpy_extras.anim_utils.action_ensure_channelbag_for_slot"></a>

### bpy_extras.anim_utils.action_ensure_channelbag_for_slot(action, slot)

Ensure a layer and a keyframe strip exists, then ensure that strip has a channelbag for the slot.

**Parameters:**

- **action** ([`bpy.types.Action`](bpy.types.Action.md#bpy.types.Action "bpy.types.Action")) – Action to populate.
- **slot** ([`bpy.types.ActionSlot`](bpy.types.ActionSlot.md#bpy.types.ActionSlot "bpy.types.ActionSlot")) – Slot to ensure a channelbag for.

**Returns:**

The channelbag for slot in the first keyframe strip.

**Return type:**

[`bpy.types.ActionChannelbag`](bpy.types.ActionChannelbag.md#bpy.types.ActionChannelbag "bpy.types.ActionChannelbag")

<a id="bpy_extras.anim_utils.animdata_get_channelbag_for_assigned_slot"></a>

### bpy_extras.anim_utils.animdata_get_channelbag_for_assigned_slot(anim_data)

Return the first channelbag used in the given *anim_data* or None if there is no Action + Slot combination defined.

**Parameters:**

**anim_data** ([`bpy.types.AnimData`](bpy.types.AnimData.md#bpy.types.AnimData "bpy.types.AnimData") | None) – Animation data to inspect.

**Returns:**

The first channelbag for the assigned slot, or None.

**Return type:**

[`bpy.types.ActionChannelbag`](bpy.types.ActionChannelbag.md#bpy.types.ActionChannelbag "bpy.types.ActionChannelbag") | None

<a id="bpy_extras.anim_utils.bake_action"></a>

### bpy_extras.anim_utils.bake_action(obj, *, action, frames, bake_options)

**Parameters:**

- **obj** ([`bpy.types.Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object")) – Object to bake.
- **action** ([`bpy.types.Action`](bpy.types.Action.md#bpy.types.Action "bpy.types.Action") | None) – An action to bake the data into, or None for a new action
  to be created.
- **frames** (Iterable[int]) – Frames to bake.
- **bake_options** (`anim_utils.BakeOptions`) – Options for baking.

**Returns:**

Action or None.

**Return type:**

[`bpy.types.Action`](bpy.types.Action.md#bpy.types.Action "bpy.types.Action") | None

<a id="bpy_extras.anim_utils.bake_action_objects"></a>

### bpy_extras.anim_utils.bake_action_objects(object_action_pairs, *, frames, bake_options)

A version of [`bake_action_objects_iter()`](#bpy_extras.anim_utils.bake_action_objects_iter "bpy_extras.anim_utils.bake_action_objects_iter") that takes frames and returns the output.

**Parameters:**

- **object_action_pairs** (Sequence[tuple[[`bpy.types.Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object"), [`bpy.types.Action`](bpy.types.Action.md#bpy.types.Action "bpy.types.Action") | None]]) – Sequence of object action tuples,
  action is the destination for the baked data. When None a new action will be created.
- **frames** (Iterable[int]) – Frames to bake.
- **bake_options** (`anim_utils.BakeOptions`) – Options for baking.

**Returns:**

A sequence of Action or None types (aligned with `object_action_pairs`)

**Return type:**

Sequence[[`bpy.types.Action`](bpy.types.Action.md#bpy.types.Action "bpy.types.Action")]

<a id="bpy_extras.anim_utils.bake_action_iter"></a>

### bpy_extras.anim_utils.bake_action_iter(obj, *, action, bake_options)

A coroutine that bakes action for a single object.

**Parameters:**

- **obj** ([`bpy.types.Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object")) – Object to bake.
- **action** ([`bpy.types.Action`](bpy.types.Action.md#bpy.types.Action "bpy.types.Action") | None) – An action to bake the data into, or None for a new action
  to be created.
- **bake_options** (`anim_utils.BakeOptions`) – Options for baking.

**Returns:**

an action or None

**Return type:**

[`bpy.types.Action`](bpy.types.Action.md#bpy.types.Action "bpy.types.Action") | None

<a id="bpy_extras.anim_utils.bake_action_objects_iter"></a>

### bpy_extras.anim_utils.bake_action_objects_iter(object_action_pairs, bake_options)

A coroutine that bakes actions for multiple objects.

**Parameters:**

- **object_action_pairs** (Sequence[tuple[[`bpy.types.Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object"), [`bpy.types.Action`](bpy.types.Action.md#bpy.types.Action "bpy.types.Action") | None]]) – Sequence of object action tuples,
  action is the destination for the baked data. When None a new action will be created.
- **bake_options** (`anim_utils.BakeOptions`) – Options for baking.

**Returns:**

A generator that yields None for each frame, then finally
yields a tuple of actions (aligned with object_action_pairs).

**Return type:**

Generator

<a id="bpy_extras.anim_utils.AutoKeying"></a>

### class bpy_extras.anim_utils.AutoKeying

Auto-keying support.

<a id="bpy_extras.anim_utils.AutoKeying.active_keyingset"></a>

#### classmethod bpy_extras.anim_utils.AutoKeying.active_keyingset(context)

Return the active keying set, if it should be used.

Only returns the active keying set when the auto-key settings indicate
it should be used, and when it is not using absolute paths (because
that’s not supported by the Copy Global Transform add-on).

**Parameters:**

**context** ([`bpy.types.Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context")) – The context.

**Returns:**

The active keying set, or None when it should not be used.

**Return type:**

[`bpy.types.KeyingSet`](bpy.types.KeyingSet.md#bpy.types.KeyingSet "bpy.types.KeyingSet") | None

<a id="bpy_extras.anim_utils.AutoKeying.autokey_transformation"></a>

#### classmethod bpy_extras.anim_utils.AutoKeying.autokey_transformation(context, target)

Auto-key transformation properties.

**Parameters:**

- **context** ([`bpy.types.Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context")) – The context.
- **target** ([`bpy.types.Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | [`bpy.types.PoseBone`](bpy.types.PoseBone.md#bpy.types.PoseBone "bpy.types.PoseBone")) – The object or pose bone to keyframe.

<a id="bpy_extras.anim_utils.AutoKeying.autokeying_options"></a>

#### classmethod bpy_extras.anim_utils.AutoKeying.autokeying_options(context)

Retrieve the Auto Keyframe options, or None if disabled.

**Parameters:**

**context** ([`bpy.types.Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context")) – The context.

**Returns:**

The keyframing option flags, or None when auto-keying is disabled.

**Return type:**

set[str] | None

<a id="bpy_extras.anim_utils.AutoKeying.key_transformation"></a>

#### classmethod bpy_extras.anim_utils.AutoKeying.key_transformation(target, options)

Keyframe transformation properties, avoiding keying locked channels.

**Parameters:**

- **target** ([`bpy.types.Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | [`bpy.types.PoseBone`](bpy.types.PoseBone.md#bpy.types.PoseBone "bpy.types.PoseBone")) – The object or pose bone to keyframe.
- **options** (set[str]) – Keyframing options.

<a id="bpy_extras.anim_utils.AutoKeying.key_transformation_via_keyingset"></a>

#### classmethod bpy_extras.anim_utils.AutoKeying.key_transformation_via_keyingset(context, target, keyingset)

Auto-key transformation properties with the given keying set.

**Parameters:**

- **context** ([`bpy.types.Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context")) – The context.
- **target** ([`bpy.types.Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | [`bpy.types.PoseBone`](bpy.types.PoseBone.md#bpy.types.PoseBone "bpy.types.PoseBone")) – The object or pose bone to keyframe.
- **keyingset** ([`bpy.types.KeyingSet`](bpy.types.KeyingSet.md#bpy.types.KeyingSet "bpy.types.KeyingSet")) – The keying set to use.

<a id="bpy_extras.anim_utils.AutoKeying.keyframe_channels"></a>

#### classmethod bpy_extras.anim_utils.AutoKeying.keyframe_channels(target, options, data_path, group, locks)

Keyframe channels, avoiding keying locked channels.

**Parameters:**

- **target** ([`bpy.types.Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | [`bpy.types.PoseBone`](bpy.types.PoseBone.md#bpy.types.PoseBone "bpy.types.PoseBone")) – The object or pose bone to keyframe.
- **options** (set[str]) – Keyframing options.
- **data_path** (str) – The data path to keyframe.
- **group** (str) – The group name for the keyframes.
- **locks** (Iterable[bool]) – Per-channel lock status.

<a id="bpy_extras.anim_utils.AutoKeying.keying_options"></a>

#### classmethod bpy_extras.anim_utils.AutoKeying.keying_options(context)

Retrieve the general keyframing options from user preferences.

**Parameters:**

**context** ([`bpy.types.Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context")) – The context.

**Returns:**

The keyframing option flags.

**Return type:**

set[str]

<a id="bpy_extras.anim_utils.AutoKeying.keying_options_from_keyingset"></a>

#### classmethod bpy_extras.anim_utils.AutoKeying.keying_options_from_keyingset(context, keyingset)

Retrieve the general keyframing options from user preferences.

**Parameters:**

- **context** ([`bpy.types.Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context")) – The context.
- **keyingset** ([`bpy.types.KeyingSet`](bpy.types.KeyingSet.md#bpy.types.KeyingSet "bpy.types.KeyingSet")) – The keying set to read options from.

**Returns:**

The keyframing option flags.

**Return type:**

set[str]

<a id="bpy_extras.anim_utils.AutoKeying.keytype"></a>

#### classmethod bpy_extras.anim_utils.AutoKeying.keytype(the_keytype)

Context manager to set the key type that’s inserted.

**Parameters:**

**the_keytype** (str) – The key type to use.

**Returns:**

A context manager that resets the key type on exit.

**Return type:**

Iterator[None]

<a id="bpy_extras.anim_utils.AutoKeying.options"></a>

#### classmethod bpy_extras.anim_utils.AutoKeying.options(*, keytype='', use_loc=True, use_rot=True, use_scale=True, force_autokey=False)

Context manager to set various keyframing options.

**Parameters:**

- **keytype** (str) – The key type to use.
- **use_loc** (bool) – Key location channels.
- **use_rot** (bool) – Key rotation channels.
- **use_scale** (bool) – Key scale channels.
- **force_autokey** (bool) – Allow use without the user activating auto-keying.

**Returns:**

A context manager that resets the options on exit.

**Return type:**

Iterator[None]

<a id="bpy_extras.anim_utils.AutoKeying.get_4d_rotlock"></a>

#### static bpy_extras.anim_utils.AutoKeying.get_4d_rotlock(bone)

Retrieve the lock status for 4D rotation.

**Parameters:**

**bone** ([`bpy.types.PoseBone`](bpy.types.PoseBone.md#bpy.types.PoseBone "bpy.types.PoseBone")) – The pose bone to check.

**Returns:**

Lock status for W, X, Y, Z rotation channels.

**Return type:**

list[bool]

<a id="bpy_extras.anim_utils.BakeOptions"></a>

### class bpy_extras.anim_utils.BakeOptions

BakeOptions(only_selected: bool, do_pose: bool, do_object: bool, do_visual_keying: bool, do_constraint_clear: bool, do_parents_clear: bool, do_clean: bool, do_location: bool, do_rotation: bool, do_scale: bool, do_bbone: bool, do_custom_props: bool)

Special Methods

<a id="bpy_extras.anim_utils.BakeOptions.__eq__"></a>

#### bpy_extras.anim_utils.BakeOptions.__eq__(other)

**Parameters:**

**other** (object) – The other operand.

**Return type:**

bool

<a id="bpy_extras.anim_utils.BakeOptions.__repr__"></a>

#### bpy_extras.anim_utils.BakeOptions.__repr__()

**Return type:**

str
