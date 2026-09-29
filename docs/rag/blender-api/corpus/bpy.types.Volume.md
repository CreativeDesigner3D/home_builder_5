<!-- source: Blender Python API reference 5.2 / bpy.types.Volume.html -->

<a id="volume-id"></a>

# Volume(ID)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")

<a id="bpy.types.Volume"></a>

### class bpy.types.Volume(ID)

Volume data-block for 3D volume grids

<a id="bpy.types.Volume.animation_data"></a>

#### bpy.types.Volume.animation_data

Animation data for this data-block (readonly)

**Type:**

[`AnimData`](bpy.types.AnimData.md#bpy.types.AnimData "bpy.types.AnimData") | None

<a id="bpy.types.Volume.display"></a>

#### bpy.types.Volume.display

Volume display settings for 3D viewport (readonly)

**Type:**

[`VolumeDisplay`](bpy.types.VolumeDisplay.md#bpy.types.VolumeDisplay "bpy.types.VolumeDisplay") | None

<a id="bpy.types.Volume.filepath"></a>

#### bpy.types.Volume.filepath

Volume file used by this Volume data-block (default “”, never None, blend relative `//` prefix supported)

**Type:**

str

<a id="bpy.types.Volume.frame_duration"></a>

#### bpy.types.Volume.frame_duration

Number of frames of the sequence to use (in [0, 1048574], default 0)

**Type:**

int

<a id="bpy.types.Volume.frame_offset"></a>

#### bpy.types.Volume.frame_offset

Offset the number of the frame to use in the animation (in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.Volume.frame_start"></a>

#### bpy.types.Volume.frame_start

Global starting frame of the sequence, assuming first has a #1 (in [-1048574, 1048574], default 1)

**Type:**

int

<a id="bpy.types.Volume.grids"></a>

#### bpy.types.Volume.grids

3D volume grids (default None, readonly)

**Type:**

[`VolumeGrids`](bpy.types.VolumeGrids.md#bpy.types.VolumeGrids "bpy.types.VolumeGrids")[[`VolumeGrid`](bpy.types.VolumeGrid.md#bpy.types.VolumeGrid "bpy.types.VolumeGrid")]

<a id="bpy.types.Volume.is_sequence"></a>

#### bpy.types.Volume.is_sequence

Whether the cache is separated in a series of files (default False)

**Type:**

bool

<a id="bpy.types.Volume.materials"></a>

#### bpy.types.Volume.materials

(default None, readonly)

**Type:**

[`IDMaterials`](bpy.types.IDMaterials.md#bpy.types.IDMaterials "bpy.types.IDMaterials")[[`Material`](bpy.types.Material.md#bpy.types.Material "bpy.types.Material")]

<a id="bpy.types.Volume.packed_file"></a>

#### bpy.types.Volume.packed_file

(readonly)

**Type:**

[`PackedFile`](bpy.types.PackedFile.md#bpy.types.PackedFile "bpy.types.PackedFile") | None

<a id="bpy.types.Volume.render"></a>

#### bpy.types.Volume.render

Volume render settings for 3D viewport (readonly)

**Type:**

[`VolumeRender`](bpy.types.VolumeRender.md#bpy.types.VolumeRender "bpy.types.VolumeRender") | None

<a id="bpy.types.Volume.sequence_mode"></a>

#### bpy.types.Volume.sequence_mode

Sequence playback mode (default `'CLIP'`)

- `CLIP`
  Clip – Hide frames outside the specified frame range.
- `EXTEND`
  Extend – Repeat the start frame before, and the end frame after the frame range.
- `REPEAT`
  Repeat – Cycle the frames in the sequence.
- `PING_PONG`
  Ping-Pong – Repeat the frames, reversing the playback direction every other cycle.

**Type:**

Literal[‘CLIP’, ‘EXTEND’, ‘REPEAT’, ‘PING_PONG’]

<a id="bpy.types.Volume.velocity_grid"></a>

#### bpy.types.Volume.velocity_grid

Name of the velocity field, or the base name if the velocity is split into multiple grids (default “”, never None)

**Type:**

str

<a id="bpy.types.Volume.velocity_scale"></a>

#### bpy.types.Volume.velocity_scale

Factor to control the amount of motion blur (in [0, inf], default 1.0)

**Type:**

float

<a id="bpy.types.Volume.velocity_unit"></a>

#### bpy.types.Volume.velocity_unit

Define how the velocity vectors are interpreted with regard to time, ‘frame’ means the delta time is 1 frame, ‘second’ means the delta time is 1 / FPS (default `'FRAME'`)

**Type:**

Literal[[Velocity Unit Items](bpy_types_enum_items/velocity_unit_items.md#rna-enum-velocity-unit-items)]

<a id="bpy.types.Volume.velocity_x_grid"></a>

#### bpy.types.Volume.velocity_x_grid

Name of the grid for the X axis component of the velocity field if it was split into multiple grids (default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.Volume.velocity_y_grid"></a>

#### bpy.types.Volume.velocity_y_grid

Name of the grid for the Y axis component of the velocity field if it was split into multiple grids (default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.Volume.velocity_z_grid"></a>

#### bpy.types.Volume.velocity_z_grid

Name of the grid for the Z axis component of the velocity field if it was split into multiple grids (default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.Volume.bl_rna_get_subclass"></a>

#### classmethod bpy.types.Volume.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.Volume.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.Volume.bl_rna_get_subclass_py(id, default=None, /)

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
| - `bpy.context.volume` - [`BlendData.volumes`](bpy.types.BlendData.md#bpy.types.BlendData.volumes "bpy.types.BlendData.volumes") | - [`BlendDataVolumes.new`](bpy.types.BlendDataVolumes.md#bpy.types.BlendDataVolumes.new "bpy.types.BlendDataVolumes.new") - [`BlendDataVolumes.remove`](bpy.types.BlendDataVolumes.md#bpy.types.BlendDataVolumes.remove "bpy.types.BlendDataVolumes.remove") |
