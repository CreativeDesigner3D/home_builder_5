<!-- source: Blender Python API reference 5.2 / bpy.types.Action.html -->

<a id="action-id"></a>

# Action(ID)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")

<a id="bpy.types.Action"></a>

### class bpy.types.Action(ID)

A collection of F-Curves for animation

<a id="bpy.types.Action.curve_frame_range"></a>

#### bpy.types.Action.curve_frame_range

The combined frame range of all F-Curves within this action (array of 2 items, in [-inf, inf], default (0.0, 0.0), readonly)

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.Action.frame_end"></a>

#### bpy.types.Action.frame_end

The end frame of the manually set intended playback range (in [-1.04857e+06, 1.04857e+06], default 0.0)

**Type:**

float

<a id="bpy.types.Action.frame_range"></a>

#### bpy.types.Action.frame_range

The intended playback frame range of this action, using the manually set range if available, or the combined frame range of all F-Curves within this action if not (assigning sets the manual frame range) (array of 2 items, in [-inf, inf], default (0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.Action.frame_start"></a>

#### bpy.types.Action.frame_start

The start frame of the manually set intended playback range (in [-1.04857e+06, 1.04857e+06], default 0.0)

**Type:**

float

<a id="bpy.types.Action.is_action_layered"></a>

#### bpy.types.Action.is_action_layered

Return whether this is a layered Action. At this point all actions are layered through versioning and this function will always return true (default False, readonly)

**Type:**

bool

<a id="bpy.types.Action.is_action_legacy"></a>

#### bpy.types.Action.is_action_legacy

Return whether this is a legacy Action. Legacy Actions have no layers or slots. Since Blender 4.4 actions are automatically updated to layered actions. This will only return true on empty actions (default False, readonly)

**Type:**

bool

<a id="bpy.types.Action.is_empty"></a>

#### bpy.types.Action.is_empty

False when there is any Layer, Slot, or legacy F-Curve (default False, readonly)

**Type:**

bool

<a id="bpy.types.Action.layers"></a>

#### bpy.types.Action.layers

The list of layers that make up this Action (default None, readonly)

**Type:**

[`ActionLayers`](bpy.types.ActionLayers.md#bpy.types.ActionLayers "bpy.types.ActionLayers")[[`ActionLayer`](bpy.types.ActionLayer.md#bpy.types.ActionLayer "bpy.types.ActionLayer")]

<a id="bpy.types.Action.pose_markers"></a>

#### bpy.types.Action.pose_markers

Markers specific to this action, for labeling poses (default None, readonly)

**Type:**

[`ActionPoseMarkers`](bpy.types.ActionPoseMarkers.md#bpy.types.ActionPoseMarkers "bpy.types.ActionPoseMarkers")[[`TimelineMarker`](bpy.types.TimelineMarker.md#bpy.types.TimelineMarker "bpy.types.TimelineMarker")]

<a id="bpy.types.Action.slots"></a>

#### bpy.types.Action.slots

The list of slots in this Action (default None, readonly)

**Type:**

[`ActionSlots`](bpy.types.ActionSlots.md#bpy.types.ActionSlots "bpy.types.ActionSlots")[[`ActionSlot`](bpy.types.ActionSlot.md#bpy.types.ActionSlot "bpy.types.ActionSlot")]

<a id="bpy.types.Action.use_cyclic"></a>

#### bpy.types.Action.use_cyclic

The action is intended to be used as a cycle looping over its manually set playback frame range (enabling this does not automatically make it loop) (default False)

**Type:**

bool

<a id="bpy.types.Action.use_frame_range"></a>

#### bpy.types.Action.use_frame_range

Manually specify the intended playback frame range for the action (this range is used by some tools, but does not affect animation evaluation) (default False)

**Type:**

bool

<a id="bpy.types.Action.deselect_keys"></a>

#### bpy.types.Action.deselect_keys()

Deselects all keys of the Action. The selection status of F-Curves is unchanged.

<a id="bpy.types.Action.fcurve_ensure_for_datablock"></a>

#### bpy.types.Action.fcurve_ensure_for_datablock(datablock, data_path, *, index=0, group_name='')

Ensure that an F-Curve exists, with the given data path and array index, for the given data-block. This action must already be assigned to the data-block. This function will also create the layer, keyframe strip, and action slot if necessary, and take care of assigning the action slot too

**Parameters:**

- **datablock** ([`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID") | None) – The data-block animated by this action, for which to ensure the F-Curve exists. This action must already be assigned to the data-block (never None)
- **data_path** (str) – Data Path, F-Curve data path (never None)
- **index** (int) – Index, Array index (in [0, inf], optional)
- **group_name** (str) – Group Name, Name of the group for this F-Curve, if any. If the F-Curve already exists, this parameter is ignored (optional, never None)

**Returns:**

The found or created F-Curve

**Return type:**

[`FCurve`](bpy.types.FCurve.md#bpy.types.FCurve "bpy.types.FCurve")

<a id="bpy.types.Action.flip_with_pose"></a>

#### bpy.types.Action.flip_with_pose(object)

Flip the action around the X axis using a pose

**Parameters:**

**object** ([`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None) – The reference armature object to use when flipping (never None)

<a id="bpy.types.Action.bl_rna_get_subclass"></a>

#### classmethod bpy.types.Action.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.Action.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.Action.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, ID.name, ID.name_full, ID.id_type, ID.session_uid, ID.is_evaluated, ID.original, ID.users, ID.use_fake_user, ID.use_extra_user, ID.is_embedded_data, ID.is_linked_packed, ID.is_missing, ID.is_runtime_data, ID.is_editable, ID.tag, ID.is_library_indirect, ID.library, ID.library_weak_reference, ID.asset_data, ID.override_library, ID.preview

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, ID.bl_system_properties_get, ID.rename, ID.evaluated_get, ID.copy, ID.asset_mark, ID.asset_clear, ID.asset_generate_preview, ID.override_create, ID.override_hierarchy_create, ID.user_clear, ID.user_remap, ID.make_local, ID.user_of_id, ID.animation_data_create, ID.animation_data_clear, ID.update_tag, ID.preview_ensure, ID.bl_rna_get_subclass, ID.bl_rna_get_subclass_py

<a id="references"></a>

## References

|  |  |
| --- | --- |
| - `bpy.context.active_action` - `bpy.context.selected_editable_actions` - `bpy.context.selected_visible_actions` - [`ActionConstraint.action`](bpy.types.ActionConstraint.md#bpy.types.ActionConstraint.action "bpy.types.ActionConstraint.action") - [`AnimData.action`](bpy.types.AnimData.md#bpy.types.AnimData.action "bpy.types.AnimData.action") - [`AnimData.action_tweak_storage`](bpy.types.AnimData.md#bpy.types.AnimData.action_tweak_storage "bpy.types.AnimData.action_tweak_storage") - [`BlendData.actions`](bpy.types.BlendData.md#bpy.types.BlendData.actions "bpy.types.BlendData.actions") - [`BlendDataActions.new`](bpy.types.BlendDataActions.md#bpy.types.BlendDataActions.new "bpy.types.BlendDataActions.new") | - [`BlendDataActions.remove`](bpy.types.BlendDataActions.md#bpy.types.BlendDataActions.remove "bpy.types.BlendDataActions.remove") - `GLTF2_filter_action.action` - [`NlaStrip.action`](bpy.types.NlaStrip.md#bpy.types.NlaStrip.action "bpy.types.NlaStrip.action") - [`NlaStrips.new`](bpy.types.NlaStrips.md#bpy.types.NlaStrips.new "bpy.types.NlaStrips.new") - [`Pose.apply_pose_from_action`](bpy.types.Pose.md#bpy.types.Pose.apply_pose_from_action "bpy.types.Pose.apply_pose_from_action") - [`Pose.backup_create`](bpy.types.Pose.md#bpy.types.Pose.backup_create "bpy.types.Pose.backup_create") - [`Pose.blend_pose_from_action`](bpy.types.Pose.md#bpy.types.Pose.blend_pose_from_action "bpy.types.Pose.blend_pose_from_action") - [`WindowManager.poselib_previous_action`](bpy.types.WindowManager.md#bpy.types.WindowManager.poselib_previous_action "bpy.types.WindowManager.poselib_previous_action") |
