<!-- source: Blender Python API reference 5.2 / bpy.types.SequencerPreviewOverlay.html -->

<a id="sequencerpreviewoverlay-bpy-struct"></a>

# SequencerPreviewOverlay(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.SequencerPreviewOverlay"></a>

### class bpy.types.SequencerPreviewOverlay(bpy_struct)

<a id="bpy.types.SequencerPreviewOverlay.composition_guide_color"></a>

#### bpy.types.SequencerPreviewOverlay.composition_guide_color

Color and alpha for compositional guide overlays (array of 4 items, in [0, inf], default (0.5, 0.5, 0.5, 1.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.SequencerPreviewOverlay.show_annotation"></a>

#### bpy.types.SequencerPreviewOverlay.show_annotation

Show annotations for this view (default False)

**Type:**

bool

<a id="bpy.types.SequencerPreviewOverlay.show_composition_center"></a>

#### bpy.types.SequencerPreviewOverlay.show_composition_center

Display center composition guide (default False)

**Type:**

bool

<a id="bpy.types.SequencerPreviewOverlay.show_composition_center_diagonal"></a>

#### bpy.types.SequencerPreviewOverlay.show_composition_center_diagonal

Display diagonal center composition guide (default False)

**Type:**

bool

<a id="bpy.types.SequencerPreviewOverlay.show_composition_golden"></a>

#### bpy.types.SequencerPreviewOverlay.show_composition_golden

Display golden ratio composition guide (default False)

**Type:**

bool

<a id="bpy.types.SequencerPreviewOverlay.show_composition_golden_tria_a"></a>

#### bpy.types.SequencerPreviewOverlay.show_composition_golden_tria_a

Display golden triangle A composition guide (default False)

**Type:**

bool

<a id="bpy.types.SequencerPreviewOverlay.show_composition_golden_tria_b"></a>

#### bpy.types.SequencerPreviewOverlay.show_composition_golden_tria_b

Display golden triangle B composition guide (default False)

**Type:**

bool

<a id="bpy.types.SequencerPreviewOverlay.show_composition_guides"></a>

#### bpy.types.SequencerPreviewOverlay.show_composition_guides

Display composition guides over the preview (default False)

**Type:**

bool

<a id="bpy.types.SequencerPreviewOverlay.show_composition_harmony_tri_a"></a>

#### bpy.types.SequencerPreviewOverlay.show_composition_harmony_tri_a

Display harmony A composition guide (default False)

**Type:**

bool

<a id="bpy.types.SequencerPreviewOverlay.show_composition_harmony_tri_b"></a>

#### bpy.types.SequencerPreviewOverlay.show_composition_harmony_tri_b

Display harmony B composition guide (default False)

**Type:**

bool

<a id="bpy.types.SequencerPreviewOverlay.show_composition_thirds"></a>

#### bpy.types.SequencerPreviewOverlay.show_composition_thirds

Display rule of thirds composition guide (default False)

**Type:**

bool

<a id="bpy.types.SequencerPreviewOverlay.show_cursor"></a>

#### bpy.types.SequencerPreviewOverlay.show_cursor

(default False)

**Type:**

bool

<a id="bpy.types.SequencerPreviewOverlay.show_image_outline"></a>

#### bpy.types.SequencerPreviewOverlay.show_image_outline

(default False)

**Type:**

bool

<a id="bpy.types.SequencerPreviewOverlay.show_metadata"></a>

#### bpy.types.SequencerPreviewOverlay.show_metadata

Show metadata of first visible strip (default False)

**Type:**

bool

<a id="bpy.types.SequencerPreviewOverlay.show_safe_areas"></a>

#### bpy.types.SequencerPreviewOverlay.show_safe_areas

Show TV title safe and action safe areas in preview (default False)

**Type:**

bool

<a id="bpy.types.SequencerPreviewOverlay.show_safe_center"></a>

#### bpy.types.SequencerPreviewOverlay.show_safe_center

Show safe areas to fit content in a different aspect ratio (default False)

**Type:**

bool

<a id="bpy.types.SequencerPreviewOverlay.bl_rna_get_subclass"></a>

#### classmethod bpy.types.SequencerPreviewOverlay.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.SequencerPreviewOverlay.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.SequencerPreviewOverlay.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`SpaceSequenceEditor.preview_overlay`](bpy.types.SpaceSequenceEditor.md#bpy.types.SpaceSequenceEditor.preview_overlay "bpy.types.SpaceSequenceEditor.preview_overlay") |  |
