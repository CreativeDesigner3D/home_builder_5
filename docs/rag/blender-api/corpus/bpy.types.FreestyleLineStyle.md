<!-- source: Blender Python API reference 5.2 / bpy.types.FreestyleLineStyle.html -->

<a id="freestylelinestyle-id"></a>

# FreestyleLineStyle(ID)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")

<a id="bpy.types.FreestyleLineStyle"></a>

### class bpy.types.FreestyleLineStyle(ID)

Freestyle line style, reusable by multiple line sets

<a id="bpy.types.FreestyleLineStyle.active_texture"></a>

#### bpy.types.FreestyleLineStyle.active_texture

Active texture slot being displayed

**Type:**

[`Texture`](bpy.types.Texture.md#bpy.types.Texture "bpy.types.Texture") | None

<a id="bpy.types.FreestyleLineStyle.active_texture_index"></a>

#### bpy.types.FreestyleLineStyle.active_texture_index

Index of active texture slot (in [0, 17], default 0)

**Type:**

int

<a id="bpy.types.FreestyleLineStyle.alpha"></a>

#### bpy.types.FreestyleLineStyle.alpha

Base alpha transparency, possibly modified by alpha transparency modifiers (in [0, 1], default 1.0)

**Type:**

float

<a id="bpy.types.FreestyleLineStyle.alpha_modifiers"></a>

#### bpy.types.FreestyleLineStyle.alpha_modifiers

List of alpha transparency modifiers (default None, readonly)

**Type:**

[`LineStyleAlphaModifiers`](bpy.types.LineStyleAlphaModifiers.md#bpy.types.LineStyleAlphaModifiers "bpy.types.LineStyleAlphaModifiers")[[`LineStyleAlphaModifier`](bpy.types.LineStyleAlphaModifier.md#bpy.types.LineStyleAlphaModifier "bpy.types.LineStyleAlphaModifier")]

<a id="bpy.types.FreestyleLineStyle.angle_max"></a>

#### bpy.types.FreestyleLineStyle.angle_max

Maximum 2D angle for splitting chains (in [0, 3.14159], default 0.0)

**Type:**

float

<a id="bpy.types.FreestyleLineStyle.angle_min"></a>

#### bpy.types.FreestyleLineStyle.angle_min

Minimum 2D angle for splitting chains (in [0, 3.14159], default 0.0)

**Type:**

float

<a id="bpy.types.FreestyleLineStyle.animation_data"></a>

#### bpy.types.FreestyleLineStyle.animation_data

Animation data for this data-block (readonly)

**Type:**

[`AnimData`](bpy.types.AnimData.md#bpy.types.AnimData "bpy.types.AnimData") | None

<a id="bpy.types.FreestyleLineStyle.caps"></a>

#### bpy.types.FreestyleLineStyle.caps

Select the shape of both ends of strokes (default `'BUTT'`)

- `BUTT`
  Butt – Butt cap (flat).
- `ROUND`
  Round – Round cap (half-circle).
- `SQUARE`
  Square – Square cap (flat and extended).

**Type:**

Literal[‘BUTT’, ‘ROUND’, ‘SQUARE’]

<a id="bpy.types.FreestyleLineStyle.chain_count"></a>

#### bpy.types.FreestyleLineStyle.chain_count

Chain count for the selection of first N chains (in [0, inf], default 10)

**Type:**

int

<a id="bpy.types.FreestyleLineStyle.chaining"></a>

#### bpy.types.FreestyleLineStyle.chaining

Select the way how feature edges are jointed to form chains (default `'PLAIN'`)

- `PLAIN`
  Plain – Plain chaining.
- `SKETCHY`
  Sketchy – Sketchy chaining with a multiple touch.

**Type:**

Literal[‘PLAIN’, ‘SKETCHY’]

<a id="bpy.types.FreestyleLineStyle.color"></a>

#### bpy.types.FreestyleLineStyle.color

Base line color, possibly modified by line color modifiers (array of 3 items, in [0, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.FreestyleLineStyle.color_modifiers"></a>

#### bpy.types.FreestyleLineStyle.color_modifiers

List of line color modifiers (default None, readonly)

**Type:**

[`LineStyleColorModifiers`](bpy.types.LineStyleColorModifiers.md#bpy.types.LineStyleColorModifiers "bpy.types.LineStyleColorModifiers")[[`LineStyleColorModifier`](bpy.types.LineStyleColorModifier.md#bpy.types.LineStyleColorModifier "bpy.types.LineStyleColorModifier")]

<a id="bpy.types.FreestyleLineStyle.dash1"></a>

#### bpy.types.FreestyleLineStyle.dash1

Length of the 1st dash for dashed lines (in [0, 65535], default 0)

**Type:**

int

<a id="bpy.types.FreestyleLineStyle.dash2"></a>

#### bpy.types.FreestyleLineStyle.dash2

Length of the 2nd dash for dashed lines (in [0, 65535], default 0)

**Type:**

int

<a id="bpy.types.FreestyleLineStyle.dash3"></a>

#### bpy.types.FreestyleLineStyle.dash3

Length of the 3rd dash for dashed lines (in [0, 65535], default 0)

**Type:**

int

<a id="bpy.types.FreestyleLineStyle.gap1"></a>

#### bpy.types.FreestyleLineStyle.gap1

Length of the 1st gap for dashed lines (in [0, 65535], default 0)

**Type:**

int

<a id="bpy.types.FreestyleLineStyle.gap2"></a>

#### bpy.types.FreestyleLineStyle.gap2

Length of the 2nd gap for dashed lines (in [0, 65535], default 0)

**Type:**

int

<a id="bpy.types.FreestyleLineStyle.gap3"></a>

#### bpy.types.FreestyleLineStyle.gap3

Length of the 3rd gap for dashed lines (in [0, 65535], default 0)

**Type:**

int

<a id="bpy.types.FreestyleLineStyle.geometry_modifiers"></a>

#### bpy.types.FreestyleLineStyle.geometry_modifiers

List of stroke geometry modifiers (default None, readonly)

**Type:**

[`LineStyleGeometryModifiers`](bpy.types.LineStyleGeometryModifiers.md#bpy.types.LineStyleGeometryModifiers "bpy.types.LineStyleGeometryModifiers")[[`LineStyleGeometryModifier`](bpy.types.LineStyleGeometryModifier.md#bpy.types.LineStyleGeometryModifier "bpy.types.LineStyleGeometryModifier")]

<a id="bpy.types.FreestyleLineStyle.integration_type"></a>

#### bpy.types.FreestyleLineStyle.integration_type

Select the way how the sort key is computed for each chain (default `'MEAN'`)

- `MEAN`
  Mean – The value computed for the chain is the mean of the values obtained for chain vertices.
- `MIN`
  Min – The value computed for the chain is the minimum of the values obtained for chain vertices.
- `MAX`
  Max – The value computed for the chain is the maximum of the values obtained for chain vertices.
- `FIRST`
  First – The value computed for the chain is the value obtained for the first chain vertex.
- `LAST`
  Last – The value computed for the chain is the value obtained for the last chain vertex.

**Type:**

Literal[‘MEAN’, ‘MIN’, ‘MAX’, ‘FIRST’, ‘LAST’]

<a id="bpy.types.FreestyleLineStyle.length_max"></a>

#### bpy.types.FreestyleLineStyle.length_max

Maximum curvilinear 2D length for the selection of chains (in [0, 10000], default 10000.0)

**Type:**

float

<a id="bpy.types.FreestyleLineStyle.length_min"></a>

#### bpy.types.FreestyleLineStyle.length_min

Minimum curvilinear 2D length for the selection of chains (in [0, 10000], default 0.0)

**Type:**

float

<a id="bpy.types.FreestyleLineStyle.material_boundary"></a>

#### bpy.types.FreestyleLineStyle.material_boundary

If true, chains of feature edges are split at material boundaries (default False)

**Type:**

bool

<a id="bpy.types.FreestyleLineStyle.node_tree"></a>

#### bpy.types.FreestyleLineStyle.node_tree

Node tree for node-based shaders (readonly)

**Type:**

[`NodeTree`](bpy.types.NodeTree.md#bpy.types.NodeTree "bpy.types.NodeTree") | None

<a id="bpy.types.FreestyleLineStyle.panel"></a>

#### bpy.types.FreestyleLineStyle.panel

Select the property panel to be shown (default `'STROKES'`)

- `STROKES`
  Strokes – Show the panel for stroke construction.
- `COLOR`
  Color – Show the panel for line color options.
- `ALPHA`
  Alpha – Show the panel for alpha transparency options.
- `THICKNESS`
  Thickness – Show the panel for line thickness options.
- `GEOMETRY`
  Geometry – Show the panel for stroke geometry options.
- `TEXTURE`
  Texture – Show the panel for stroke texture options.

**Type:**

Literal[‘STROKES’, ‘COLOR’, ‘ALPHA’, ‘THICKNESS’, ‘GEOMETRY’, ‘TEXTURE’]

<a id="bpy.types.FreestyleLineStyle.rounds"></a>

#### bpy.types.FreestyleLineStyle.rounds

Number of rounds in a sketchy multiple touch (in [1, 1000], default 3)

**Type:**

int

<a id="bpy.types.FreestyleLineStyle.sort_key"></a>

#### bpy.types.FreestyleLineStyle.sort_key

Select the sort key to determine the stacking order of chains (default `'DISTANCE_FROM_CAMERA'`)

- `DISTANCE_FROM_CAMERA`
  Distance from Camera – Sort by distance from camera (closer lines lie on top of further lines).
- `2D_LENGTH`
  2D Length – Sort by curvilinear 2D length (longer lines lie on top of shorter lines).
- `PROJECTED_X`
  Projected X – Sort by the projected X value in the image coordinate system.
- `PROJECTED_Y`
  Projected Y – Sort by the projected Y value in the image coordinate system.

**Type:**

Literal[‘DISTANCE_FROM_CAMERA’, ‘2D_LENGTH’, ‘PROJECTED_X’, ‘PROJECTED_Y’]

<a id="bpy.types.FreestyleLineStyle.sort_order"></a>

#### bpy.types.FreestyleLineStyle.sort_order

Select the sort order (default `'DEFAULT'`)

- `DEFAULT`
  Default – Default order of the sort key.
- `REVERSE`
  Reverse – Reverse order.

**Type:**

Literal[‘DEFAULT’, ‘REVERSE’]

<a id="bpy.types.FreestyleLineStyle.split_dash1"></a>

#### bpy.types.FreestyleLineStyle.split_dash1

Length of the 1st dash for splitting (in [0, 65535], default 0)

**Type:**

int

<a id="bpy.types.FreestyleLineStyle.split_dash2"></a>

#### bpy.types.FreestyleLineStyle.split_dash2

Length of the 2nd dash for splitting (in [0, 65535], default 0)

**Type:**

int

<a id="bpy.types.FreestyleLineStyle.split_dash3"></a>

#### bpy.types.FreestyleLineStyle.split_dash3

Length of the 3rd dash for splitting (in [0, 65535], default 0)

**Type:**

int

<a id="bpy.types.FreestyleLineStyle.split_gap1"></a>

#### bpy.types.FreestyleLineStyle.split_gap1

Length of the 1st gap for splitting (in [0, 65535], default 0)

**Type:**

int

<a id="bpy.types.FreestyleLineStyle.split_gap2"></a>

#### bpy.types.FreestyleLineStyle.split_gap2

Length of the 2nd gap for splitting (in [0, 65535], default 0)

**Type:**

int

<a id="bpy.types.FreestyleLineStyle.split_gap3"></a>

#### bpy.types.FreestyleLineStyle.split_gap3

Length of the 3rd gap for splitting (in [0, 65535], default 0)

**Type:**

int

<a id="bpy.types.FreestyleLineStyle.split_length"></a>

#### bpy.types.FreestyleLineStyle.split_length

Curvilinear 2D length for chain splitting (in [0, 10000], default 100.0)

**Type:**

float

<a id="bpy.types.FreestyleLineStyle.texture_slots"></a>

#### bpy.types.FreestyleLineStyle.texture_slots

Texture slots defining the mapping and influence of textures (default None, readonly)

**Type:**

[`LineStyleTextureSlots`](bpy.types.LineStyleTextureSlots.md#bpy.types.LineStyleTextureSlots "bpy.types.LineStyleTextureSlots")[[`LineStyleTextureSlot`](bpy.types.LineStyleTextureSlot.md#bpy.types.LineStyleTextureSlot "bpy.types.LineStyleTextureSlot")]

<a id="bpy.types.FreestyleLineStyle.texture_spacing"></a>

#### bpy.types.FreestyleLineStyle.texture_spacing

Spacing for textures along stroke length (in [0.01, 100], default 1.0)

**Type:**

float

<a id="bpy.types.FreestyleLineStyle.thickness"></a>

#### bpy.types.FreestyleLineStyle.thickness

Base line thickness, possibly modified by line thickness modifiers (in [0, 10000], default 3.0)

**Type:**

float

<a id="bpy.types.FreestyleLineStyle.thickness_modifiers"></a>

#### bpy.types.FreestyleLineStyle.thickness_modifiers

List of line thickness modifiers (default None, readonly)

**Type:**

[`LineStyleThicknessModifiers`](bpy.types.LineStyleThicknessModifiers.md#bpy.types.LineStyleThicknessModifiers "bpy.types.LineStyleThicknessModifiers")[[`LineStyleThicknessModifier`](bpy.types.LineStyleThicknessModifier.md#bpy.types.LineStyleThicknessModifier "bpy.types.LineStyleThicknessModifier")]

<a id="bpy.types.FreestyleLineStyle.thickness_position"></a>

#### bpy.types.FreestyleLineStyle.thickness_position

Thickness position of silhouettes and border edges (applicable when plain chaining is used with the Same Object option) (default `'CENTER'`)

- `CENTER`
  Center – Silhouettes and border edges are centered along stroke geometry.
- `INSIDE`
  Inside – Silhouettes and border edges are drawn inside of stroke geometry.
- `OUTSIDE`
  Outside – Silhouettes and border edges are drawn outside of stroke geometry.
- `RELATIVE`
  Relative – Silhouettes and border edges are shifted by a user-defined ratio.

**Type:**

Literal[‘CENTER’, ‘INSIDE’, ‘OUTSIDE’, ‘RELATIVE’]

<a id="bpy.types.FreestyleLineStyle.thickness_ratio"></a>

#### bpy.types.FreestyleLineStyle.thickness_ratio

A number between 0 (inside) and 1 (outside) specifying the relative position of stroke thickness (in [0, 1], default 0.5)

**Type:**

float

<a id="bpy.types.FreestyleLineStyle.use_angle_max"></a>

#### bpy.types.FreestyleLineStyle.use_angle_max

Split chains at points with angles larger than the maximum 2D angle (default False)

**Type:**

bool

<a id="bpy.types.FreestyleLineStyle.use_angle_min"></a>

#### bpy.types.FreestyleLineStyle.use_angle_min

Split chains at points with angles smaller than the minimum 2D angle (default False)

**Type:**

bool

<a id="bpy.types.FreestyleLineStyle.use_chain_count"></a>

#### bpy.types.FreestyleLineStyle.use_chain_count

Enable the selection of first N chains (default False)

**Type:**

bool

<a id="bpy.types.FreestyleLineStyle.use_chaining"></a>

#### bpy.types.FreestyleLineStyle.use_chaining

Enable chaining of feature edges (default True)

**Type:**

bool

<a id="bpy.types.FreestyleLineStyle.use_dashed_line"></a>

#### bpy.types.FreestyleLineStyle.use_dashed_line

Enable or disable dashed line (default False)

**Type:**

bool

<a id="bpy.types.FreestyleLineStyle.use_length_max"></a>

#### bpy.types.FreestyleLineStyle.use_length_max

Enable the selection of chains by a maximum 2D length (default False)

**Type:**

bool

<a id="bpy.types.FreestyleLineStyle.use_length_min"></a>

#### bpy.types.FreestyleLineStyle.use_length_min

Enable the selection of chains by a minimum 2D length (default False)

**Type:**

bool

<a id="bpy.types.FreestyleLineStyle.use_nodes"></a>

#### bpy.types.FreestyleLineStyle.use_nodes

Use shader nodes for the line style (default False)

**Type:**

bool

<a id="bpy.types.FreestyleLineStyle.use_same_object"></a>

#### bpy.types.FreestyleLineStyle.use_same_object

If true, only feature edges of the same object are joined (default True)

**Type:**

bool

<a id="bpy.types.FreestyleLineStyle.use_sorting"></a>

#### bpy.types.FreestyleLineStyle.use_sorting

Arrange the stacking order of strokes (default False)

**Type:**

bool

<a id="bpy.types.FreestyleLineStyle.use_split_length"></a>

#### bpy.types.FreestyleLineStyle.use_split_length

Enable chain splitting by curvilinear 2D length (default False)

**Type:**

bool

<a id="bpy.types.FreestyleLineStyle.use_split_pattern"></a>

#### bpy.types.FreestyleLineStyle.use_split_pattern

Enable chain splitting by dashed line patterns (default False)

**Type:**

bool

<a id="bpy.types.FreestyleLineStyle.use_texture"></a>

#### bpy.types.FreestyleLineStyle.use_texture

Enable or disable textured strokes (default True)

**Type:**

bool

<a id="bpy.types.FreestyleLineStyle.bl_rna_get_subclass"></a>

#### classmethod bpy.types.FreestyleLineStyle.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.FreestyleLineStyle.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.FreestyleLineStyle.bl_rna_get_subclass_py(id, default=None, /)

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
| - `bpy.context.line_style` - [`BlendData.linestyles`](bpy.types.BlendData.md#bpy.types.BlendData.linestyles "bpy.types.BlendData.linestyles") - [`BlendDataLineStyles.new`](bpy.types.BlendDataLineStyles.md#bpy.types.BlendDataLineStyles.new "bpy.types.BlendDataLineStyles.new") | - [`BlendDataLineStyles.remove`](bpy.types.BlendDataLineStyles.md#bpy.types.BlendDataLineStyles.remove "bpy.types.BlendDataLineStyles.remove") - [`FreestyleLineSet.linestyle`](bpy.types.FreestyleLineSet.md#bpy.types.FreestyleLineSet.linestyle "bpy.types.FreestyleLineSet.linestyle") |
