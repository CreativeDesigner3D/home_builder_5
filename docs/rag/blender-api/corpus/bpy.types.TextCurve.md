<!-- source: Blender Python API reference 5.2 / bpy.types.TextCurve.html -->

<a id="textcurve-curve"></a>

# TextCurve(Curve)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID"), [`Curve`](bpy.types.Curve.md#bpy.types.Curve "bpy.types.Curve")

<a id="bpy.types.TextCurve"></a>

### class bpy.types.TextCurve(Curve)

Curve data-block used for storing text

<a id="bpy.types.TextCurve.active_textbox"></a>

#### bpy.types.TextCurve.active_textbox

(in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.TextCurve.align_x"></a>

#### bpy.types.TextCurve.align_x

Text horizontal alignment from the object or text box center (default `'LEFT'`)

- `LEFT`
  Left – Align text to the left.
- `CENTER`
  Center – Center text.
- `RIGHT`
  Right – Align text to the right.
- `JUSTIFY`
  Justify – Align to the left and the right.
- `FLUSH`
  Flush – Align to the left and the right, with equal character spacing.

**Type:**

Literal[‘LEFT’, ‘CENTER’, ‘RIGHT’, ‘JUSTIFY’, ‘FLUSH’]

<a id="bpy.types.TextCurve.align_y"></a>

#### bpy.types.TextCurve.align_y

Text vertical alignment from the object center (default `'TOP_BASELINE'`)

- `TOP`
  Top – Align text to the top.
- `TOP_BASELINE`
  Top Baseline – Align text to the top line’s baseline.
- `CENTER`
  Middle – Align text to the middle.
- `BOTTOM_BASELINE`
  Bottom Baseline – Align text to the bottom line’s baseline.
- `BOTTOM`
  Bottom – Align text to the bottom.

**Type:**

Literal[‘TOP’, ‘TOP_BASELINE’, ‘CENTER’, ‘BOTTOM_BASELINE’, ‘BOTTOM’]

<a id="bpy.types.TextCurve.body"></a>

#### bpy.types.TextCurve.body

Content of this text object (default “”, never None)

**Type:**

str

<a id="bpy.types.TextCurve.body_format"></a>

#### bpy.types.TextCurve.body_format

Stores the style of each character (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`TextCharacterFormat`](bpy.types.TextCharacterFormat.md#bpy.types.TextCharacterFormat "bpy.types.TextCharacterFormat")]

<a id="bpy.types.TextCurve.edit_format"></a>

#### bpy.types.TextCurve.edit_format

Editing settings character formatting (readonly)

**Type:**

[`TextCharacterFormat`](bpy.types.TextCharacterFormat.md#bpy.types.TextCharacterFormat "bpy.types.TextCharacterFormat") | None

<a id="bpy.types.TextCurve.family"></a>

#### bpy.types.TextCurve.family

Use objects as font characters (give font objects a common name followed by the character they represent, eg. ‘family-a’, ‘family-b’, etc, set this setting to ‘family-’, and turn on Vertex Instancing) (default “”, never None)

**Type:**

str

<a id="bpy.types.TextCurve.follow_curve"></a>

#### bpy.types.TextCurve.follow_curve

Curve deforming text object

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.TextCurve.font"></a>

#### bpy.types.TextCurve.font

**Type:**

[`VectorFont`](bpy.types.VectorFont.md#bpy.types.VectorFont "bpy.types.VectorFont") | None

<a id="bpy.types.TextCurve.font_bold"></a>

#### bpy.types.TextCurve.font_bold

**Type:**

[`VectorFont`](bpy.types.VectorFont.md#bpy.types.VectorFont "bpy.types.VectorFont") | None

<a id="bpy.types.TextCurve.font_bold_italic"></a>

#### bpy.types.TextCurve.font_bold_italic

**Type:**

[`VectorFont`](bpy.types.VectorFont.md#bpy.types.VectorFont "bpy.types.VectorFont") | None

<a id="bpy.types.TextCurve.font_italic"></a>

#### bpy.types.TextCurve.font_italic

**Type:**

[`VectorFont`](bpy.types.VectorFont.md#bpy.types.VectorFont "bpy.types.VectorFont") | None

<a id="bpy.types.TextCurve.has_selection"></a>

#### bpy.types.TextCurve.has_selection

Whether there is any text selected (default False, readonly)

**Type:**

bool

<a id="bpy.types.TextCurve.is_select_bold"></a>

#### bpy.types.TextCurve.is_select_bold

Whether the selected text is bold (default False, readonly)

**Type:**

bool

<a id="bpy.types.TextCurve.is_select_italic"></a>

#### bpy.types.TextCurve.is_select_italic

Whether the selected text is italics (default False, readonly)

**Type:**

bool

<a id="bpy.types.TextCurve.is_select_smallcaps"></a>

#### bpy.types.TextCurve.is_select_smallcaps

Whether the selected text is small caps (default False, readonly)

**Type:**

bool

<a id="bpy.types.TextCurve.is_select_underline"></a>

#### bpy.types.TextCurve.is_select_underline

Whether the selected text is underlined (default False, readonly)

**Type:**

bool

<a id="bpy.types.TextCurve.offset_x"></a>

#### bpy.types.TextCurve.offset_x

Horizontal offset from the object origin (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.TextCurve.offset_y"></a>

#### bpy.types.TextCurve.offset_y

Vertical offset from the object origin (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.TextCurve.overflow"></a>

#### bpy.types.TextCurve.overflow

Handle the text behavior when it does not fit in the text boxes (default `'NONE'`)

- `NONE`
  Overflow – Let the text overflow outside the text boxes.
- `SCALE`
  Scale to Fit – Scale down the text to fit inside the text boxes.
- `TRUNCATE`
  Truncate – Truncate the text that would go outside the text boxes.

**Type:**

Literal[‘NONE’, ‘SCALE’, ‘TRUNCATE’]

<a id="bpy.types.TextCurve.shear"></a>

#### bpy.types.TextCurve.shear

Italic angle of the characters (in [-1, 1], default 0.0)

**Type:**

float

<a id="bpy.types.TextCurve.size"></a>

#### bpy.types.TextCurve.size

(in [0.0001, 10000], default 1.0)

**Type:**

float

<a id="bpy.types.TextCurve.small_caps_scale"></a>

#### bpy.types.TextCurve.small_caps_scale

Scale of small capitals (in [-inf, inf], default 0.75)

**Type:**

float

<a id="bpy.types.TextCurve.space_character"></a>

#### bpy.types.TextCurve.space_character

(in [0, 10], default 1.0)

**Type:**

float

<a id="bpy.types.TextCurve.space_line"></a>

#### bpy.types.TextCurve.space_line

(in [0, 10], default 1.0)

**Type:**

float

<a id="bpy.types.TextCurve.space_word"></a>

#### bpy.types.TextCurve.space_word

(in [0, 10], default 1.0)

**Type:**

float

<a id="bpy.types.TextCurve.text_boxes"></a>

#### bpy.types.TextCurve.text_boxes

(default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`TextBox`](bpy.types.TextBox.md#bpy.types.TextBox "bpy.types.TextBox")]

<a id="bpy.types.TextCurve.underline_height"></a>

#### bpy.types.TextCurve.underline_height

(in [0, 0.8], default 0.05)

**Type:**

float

<a id="bpy.types.TextCurve.underline_position"></a>

#### bpy.types.TextCurve.underline_position

Vertical position of underline (in [-0.2, 0.8], default 0.0)

**Type:**

float

<a id="bpy.types.TextCurve.use_fast_edit"></a>

#### bpy.types.TextCurve.use_fast_edit

Don’t fill polygons while editing (default False)

**Type:**

bool

<a id="bpy.types.TextCurve.bl_rna_get_subclass"></a>

#### classmethod bpy.types.TextCurve.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.TextCurve.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.TextCurve.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, ID.name, ID.name_full, ID.id_type, ID.session_uid, ID.is_evaluated, ID.original, ID.users, ID.use_fake_user, ID.use_extra_user, ID.is_embedded_data, ID.is_linked_packed, ID.is_missing, ID.is_runtime_data, ID.is_editable, ID.tag, ID.is_library_indirect, ID.library, ID.library_weak_reference, ID.asset_data, ID.override_library, ID.preview, Curve.shape_keys, Curve.splines, Curve.path_duration, Curve.use_path, Curve.use_path_follow, Curve.use_path_clamp, Curve.use_stretch, Curve.use_deform_bounds, Curve.use_radius, Curve.bevel_mode, Curve.bevel_profile, Curve.bevel_resolution, Curve.offset, Curve.extrude, Curve.bevel_depth, Curve.resolution_u, Curve.resolution_v, Curve.render_resolution_u, Curve.render_resolution_v, Curve.eval_time, Curve.bevel_object, Curve.taper_object, Curve.dimensions, Curve.fill_mode, Curve.fill_solver, Curve.fill_rule, Curve.twist_mode, Curve.taper_radius_mode, Curve.bevel_factor_mapping_start, Curve.bevel_factor_mapping_end, Curve.twist_smooth, Curve.use_fill_caps, Curve.use_map_taper, Curve.use_auto_texspace, Curve.texspace_location, Curve.texspace_size, Curve.materials, Curve.bevel_factor_start, Curve.bevel_factor_end, Curve.is_editmode, Curve.animation_data, Curve.cycles

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, ID.bl_system_properties_get, ID.rename, ID.evaluated_get, ID.copy, ID.asset_mark, ID.asset_clear, ID.asset_generate_preview, ID.override_create, ID.override_hierarchy_create, ID.user_clear, ID.user_remap, ID.make_local, ID.user_of_id, ID.animation_data_create, ID.animation_data_clear, ID.update_tag, ID.preview_ensure, ID.bl_rna_get_subclass, ID.bl_rna_get_subclass_py, Curve.transform, Curve.validate_material_indices, Curve.update_gpu_tag, Curve.bl_rna_get_subclass, Curve.bl_rna_get_subclass_py
