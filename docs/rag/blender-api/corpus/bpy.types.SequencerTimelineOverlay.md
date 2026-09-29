<!-- source: Blender Python API reference 5.2 / bpy.types.SequencerTimelineOverlay.html -->

<a id="sequencertimelineoverlay-bpy-struct"></a>

# SequencerTimelineOverlay(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.SequencerTimelineOverlay"></a>

### class bpy.types.SequencerTimelineOverlay(bpy_struct)

<a id="bpy.types.SequencerTimelineOverlay.show_fcurves"></a>

#### bpy.types.SequencerTimelineOverlay.show_fcurves

Display strip opacity/volume curve (default False)

**Type:**

bool

<a id="bpy.types.SequencerTimelineOverlay.show_grid"></a>

#### bpy.types.SequencerTimelineOverlay.show_grid

Show vertical grid lines (default False)

**Type:**

bool

<a id="bpy.types.SequencerTimelineOverlay.show_strip_duration"></a>

#### bpy.types.SequencerTimelineOverlay.show_strip_duration

(default False)

**Type:**

bool

<a id="bpy.types.SequencerTimelineOverlay.show_strip_name"></a>

#### bpy.types.SequencerTimelineOverlay.show_strip_name

(default False)

**Type:**

bool

<a id="bpy.types.SequencerTimelineOverlay.show_strip_offset"></a>

#### bpy.types.SequencerTimelineOverlay.show_strip_offset

Display strip in/out offsets (default False)

**Type:**

bool

<a id="bpy.types.SequencerTimelineOverlay.show_strip_retiming"></a>

#### bpy.types.SequencerTimelineOverlay.show_strip_retiming

Display retiming keys on top of strips (default False)

**Type:**

bool

<a id="bpy.types.SequencerTimelineOverlay.show_strip_source"></a>

#### bpy.types.SequencerTimelineOverlay.show_strip_source

Display path to source file, or name of source data-block (default False)

**Type:**

bool

<a id="bpy.types.SequencerTimelineOverlay.show_strip_tag_color"></a>

#### bpy.types.SequencerTimelineOverlay.show_strip_tag_color

Display the strip color tags in the sequencer (default False)

**Type:**

bool

<a id="bpy.types.SequencerTimelineOverlay.thumbnail_display_style"></a>

#### bpy.types.SequencerTimelineOverlay.thumbnail_display_style

How thumbnails are displayed (default `'NO_THUMBNAILS'`)

- `NO_THUMBNAILS`
  None – Do not show strip thumbnails.
- `STRIP_ENDS`
  Strip Ends – Show thumbnails only at the beginning and end of the strip.
- `CONTINUOUS`
  Continuous – Display thumbnails as a filmstrip.

**Type:**

Literal[‘NO_THUMBNAILS’, ‘STRIP_ENDS’, ‘CONTINUOUS’]

<a id="bpy.types.SequencerTimelineOverlay.waveform_display_style"></a>

#### bpy.types.SequencerTimelineOverlay.waveform_display_style

How Waveforms are displayed (default `'FULL_WAVEFORMS'`)

- `FULL_WAVEFORMS`
  Full – Display full waveform.
- `HALF_WAVEFORMS`
  Half – Display upper half of the absolute value waveform.

**Type:**

Literal[‘FULL_WAVEFORMS’, ‘HALF_WAVEFORMS’]

<a id="bpy.types.SequencerTimelineOverlay.waveform_display_type"></a>

#### bpy.types.SequencerTimelineOverlay.waveform_display_type

How Waveforms are displayed (default `'DEFAULT_WAVEFORMS'`)

- `ALL_WAVEFORMS`
  On – Display waveforms for all sound strips.
- `DEFAULT_WAVEFORMS`
  Strip – Display waveforms depending on strip setting.
- `NO_WAVEFORMS`
  Off – Don’t display waveforms for any sound strips.

**Type:**

Literal[‘ALL_WAVEFORMS’, ‘DEFAULT_WAVEFORMS’, ‘NO_WAVEFORMS’]

<a id="bpy.types.SequencerTimelineOverlay.bl_rna_get_subclass"></a>

#### classmethod bpy.types.SequencerTimelineOverlay.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.SequencerTimelineOverlay.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.SequencerTimelineOverlay.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`SpaceSequenceEditor.timeline_overlay`](bpy.types.SpaceSequenceEditor.md#bpy.types.SpaceSequenceEditor.timeline_overlay "bpy.types.SpaceSequenceEditor.timeline_overlay") |  |
