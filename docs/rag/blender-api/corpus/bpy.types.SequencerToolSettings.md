<!-- source: Blender Python API reference 5.2 / bpy.types.SequencerToolSettings.html -->

<a id="sequencertoolsettings-bpy-struct"></a>

# SequencerToolSettings(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.SequencerToolSettings"></a>

### class bpy.types.SequencerToolSettings(bpy_struct)

<a id="bpy.types.SequencerToolSettings.fit_method"></a>

#### bpy.types.SequencerToolSettings.fit_method

Scale fit method (default `'FIT'`)

**Type:**

Literal[[Strip Scale Method Items](bpy_types_enum_items/strip_scale_method_items.md#rna-enum-strip-scale-method-items)]

<a id="bpy.types.SequencerToolSettings.overlap_mode"></a>

#### bpy.types.SequencerToolSettings.overlap_mode

How to resolve overlap after transformation (default `'EXPAND'`)

- `EXPAND`
  Expand – Move strips so transformed strips fit.
- `OVERWRITE`
  Overwrite – Trim or split strips to resolve overlap.
- `SHUFFLE`
  Shuffle – Move transformed strips to nearest free space to resolve overlap.

**Type:**

Literal[‘EXPAND’, ‘OVERWRITE’, ‘SHUFFLE’]

<a id="bpy.types.SequencerToolSettings.pivot_point"></a>

#### bpy.types.SequencerToolSettings.pivot_point

Rotation or scaling pivot point (default `'CENTER'`)

- `CENTER`
  Bounding Box Center.
- `MEDIAN`
  Median Point.
- `CURSOR`
  2D Cursor – Pivot around the 2D cursor.
- `INDIVIDUAL_ORIGINS`
  Individual Origins – Pivot around each selected island’s own median point.

**Type:**

Literal[‘CENTER’, ‘MEDIAN’, ‘CURSOR’, ‘INDIVIDUAL_ORIGINS’]

<a id="bpy.types.SequencerToolSettings.snap_distance"></a>

#### bpy.types.SequencerToolSettings.snap_distance

Maximum distance for snapping in pixels (in [-inf, inf], default 15)

**Type:**

int

<a id="bpy.types.SequencerToolSettings.snap_ignore_muted"></a>

#### bpy.types.SequencerToolSettings.snap_ignore_muted

Don’t snap to hidden strips (default False)

**Type:**

bool

<a id="bpy.types.SequencerToolSettings.snap_ignore_sound"></a>

#### bpy.types.SequencerToolSettings.snap_ignore_sound

Don’t snap to sound strips (default False)

**Type:**

bool

<a id="bpy.types.SequencerToolSettings.snap_to_all_channels"></a>

#### bpy.types.SequencerToolSettings.snap_to_all_channels

Allow snapping to any channel. If disabled, only snap to strips currently on the same channel as transformed strips (default False)

**Type:**

bool

<a id="bpy.types.SequencerToolSettings.snap_to_borders"></a>

#### bpy.types.SequencerToolSettings.snap_to_borders

Snap to preview borders (default False)

**Type:**

bool

<a id="bpy.types.SequencerToolSettings.snap_to_center"></a>

#### bpy.types.SequencerToolSettings.snap_to_center

Snap to preview center (default False)

**Type:**

bool

<a id="bpy.types.SequencerToolSettings.snap_to_current_frame"></a>

#### bpy.types.SequencerToolSettings.snap_to_current_frame

Snap to current frame (default False)

**Type:**

bool

<a id="bpy.types.SequencerToolSettings.snap_to_frame_range"></a>

#### bpy.types.SequencerToolSettings.snap_to_frame_range

Snap to preview or scene start and end frame (default False)

**Type:**

bool

<a id="bpy.types.SequencerToolSettings.snap_to_hold_offset"></a>

#### bpy.types.SequencerToolSettings.snap_to_hold_offset

Snap to underlying strip content start and end in cases where the strip length extends beyond this range, producing holds (default False)

**Type:**

bool

<a id="bpy.types.SequencerToolSettings.snap_to_markers"></a>

#### bpy.types.SequencerToolSettings.snap_to_markers

Snap to markers (default False)

**Type:**

bool

<a id="bpy.types.SequencerToolSettings.snap_to_retiming_keys"></a>

#### bpy.types.SequencerToolSettings.snap_to_retiming_keys

Snap to retiming keys (default False)

**Type:**

bool

<a id="bpy.types.SequencerToolSettings.snap_to_strips_preview"></a>

#### bpy.types.SequencerToolSettings.snap_to_strips_preview

Snap to borders and origins of deselected, visible strips (default False)

**Type:**

bool

<a id="bpy.types.SequencerToolSettings.use_snap_current_frame_to_strips"></a>

#### bpy.types.SequencerToolSettings.use_snap_current_frame_to_strips

Snap current frame to strip start or end (default False)

**Type:**

bool

<a id="bpy.types.SequencerToolSettings.bl_rna_get_subclass"></a>

#### classmethod bpy.types.SequencerToolSettings.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.SequencerToolSettings.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.SequencerToolSettings.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values

<a id="references"></a>

## References

|  |  |
| --- | --- |
| - [`ToolSettings.sequencer_tool_settings`](bpy.types.ToolSettings.md#bpy.types.ToolSettings.sequencer_tool_settings "bpy.types.ToolSettings.sequencer_tool_settings") |  |
