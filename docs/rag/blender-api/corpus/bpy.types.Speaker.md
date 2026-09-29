<!-- source: Blender Python API reference 5.2 / bpy.types.Speaker.html -->

<a id="speaker-id"></a>

# Speaker(ID)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")

<a id="bpy.types.Speaker"></a>

### class bpy.types.Speaker(ID)

Speaker data-block for 3D audio speaker objects

<a id="bpy.types.Speaker.animation_data"></a>

#### bpy.types.Speaker.animation_data

Animation data for this data-block (readonly)

**Type:**

[`AnimData`](bpy.types.AnimData.md#bpy.types.AnimData "bpy.types.AnimData") | None

<a id="bpy.types.Speaker.attenuation"></a>

#### bpy.types.Speaker.attenuation

How strong the distance affects volume, depending on distance model (in [0, inf], default 1.0)

**Type:**

float

<a id="bpy.types.Speaker.cone_angle_inner"></a>

#### bpy.types.Speaker.cone_angle_inner

Angle of the inner cone, in degrees, inside the cone the volume is 100% (in [0, 360], default 360.0)

**Type:**

float

<a id="bpy.types.Speaker.cone_angle_outer"></a>

#### bpy.types.Speaker.cone_angle_outer

Angle of the outer cone, in degrees, outside this cone the volume is the outer cone volume, between inner and outer cone the volume is interpolated (in [0, 360], default 360.0)

**Type:**

float

<a id="bpy.types.Speaker.cone_volume_outer"></a>

#### bpy.types.Speaker.cone_volume_outer

Volume outside the outer cone (in [0, 1], default 1.0)

**Type:**

float

<a id="bpy.types.Speaker.distance_max"></a>

#### bpy.types.Speaker.distance_max

Maximum distance for volume calculation, no matter how far away the object is (in [0, inf], default 3.40282e+38)

**Type:**

float

<a id="bpy.types.Speaker.distance_reference"></a>

#### bpy.types.Speaker.distance_reference

Reference distance at which volume is 100% (in [0, inf], default 1.0)

**Type:**

float

<a id="bpy.types.Speaker.muted"></a>

#### bpy.types.Speaker.muted

Mute the speaker (default False)

**Type:**

bool

<a id="bpy.types.Speaker.pitch"></a>

#### bpy.types.Speaker.pitch

Playback pitch of the sound (in [0.1, 10], default 1.0)

**Type:**

float

<a id="bpy.types.Speaker.sound"></a>

#### bpy.types.Speaker.sound

Sound data-block used by this speaker

**Type:**

[`Sound`](bpy.types.Sound.md#bpy.types.Sound "bpy.types.Sound") | None

<a id="bpy.types.Speaker.volume"></a>

#### bpy.types.Speaker.volume

How loud the sound is (in [0, 1], default 1.0)

**Type:**

float

<a id="bpy.types.Speaker.volume_max"></a>

#### bpy.types.Speaker.volume_max

Maximum volume, no matter how near the object is (in [0, 1], default 1.0)

**Type:**

float

<a id="bpy.types.Speaker.volume_min"></a>

#### bpy.types.Speaker.volume_min

Minimum volume, no matter how far away the object is (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.Speaker.bl_rna_get_subclass"></a>

#### classmethod bpy.types.Speaker.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.Speaker.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.Speaker.bl_rna_get_subclass_py(id, default=None, /)

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
| - `bpy.context.speaker` - [`BlendData.speakers`](bpy.types.BlendData.md#bpy.types.BlendData.speakers "bpy.types.BlendData.speakers") | - [`BlendDataSpeakers.new`](bpy.types.BlendDataSpeakers.md#bpy.types.BlendDataSpeakers.new "bpy.types.BlendDataSpeakers.new") - [`BlendDataSpeakers.remove`](bpy.types.BlendDataSpeakers.md#bpy.types.BlendDataSpeakers.remove "bpy.types.BlendDataSpeakers.remove") |
