<!-- source: Blender Python API reference 5.2 / bpy.ops.scene.html -->

<a id="module-bpy.ops.scene"></a>

# Scene Operators

<a id="bpy.ops.scene.delete"></a>

### bpy.ops.scene.delete()

Delete active scene

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.scene.drop_scene_asset"></a>

### bpy.ops.scene.drop_scene_asset(*, session_uid=0)

Import scene and set it as the active one in the window

**Parameters:**

**session_uid** (int) – Session UID, Session UID of the data-block to use by the operator (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.scene.freestyle_add_edge_marks_to_keying_set"></a>

### bpy.ops.scene.freestyle_add_edge_marks_to_keying_set()

Add the data paths to the Freestyle Edge Mark property of selected edges to the active keying set

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/freestyle.py:139](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/freestyle.py#L139)

<a id="bpy.ops.scene.freestyle_add_face_marks_to_keying_set"></a>

### bpy.ops.scene.freestyle_add_face_marks_to_keying_set()

Add the data paths to the Freestyle Face Mark property of selected polygons to the active keying set

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/freestyle.py:170](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/freestyle.py#L170)

<a id="bpy.ops.scene.freestyle_alpha_modifier_add"></a>

### bpy.ops.scene.freestyle_alpha_modifier_add(*, type='ALONG_STROKE')

Add an alpha transparency modifier to the line style associated with the active lineset

**Parameters:**

**type** (Literal[[Linestyle Alpha Modifier Type Items](bpy_types_enum_items/linestyle_alpha_modifier_type_items.md#rna-enum-linestyle-alpha-modifier-type-items)]) – Type, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.scene.freestyle_color_modifier_add"></a>

### bpy.ops.scene.freestyle_color_modifier_add(*, type='ALONG_STROKE')

Add a line color modifier to the line style associated with the active lineset

**Parameters:**

**type** (Literal[[Linestyle Color Modifier Type Items](bpy_types_enum_items/linestyle_color_modifier_type_items.md#rna-enum-linestyle-color-modifier-type-items)]) – Type, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.scene.freestyle_fill_range_by_selection"></a>

### bpy.ops.scene.freestyle_fill_range_by_selection(*, type='COLOR', name='')

Fill the Range Min/Max entries by the min/max distance between selected mesh objects and the source object (either a user-specified object or the active camera)

**Parameters:**

- **type** (Literal['COLOR', 'ALPHA', 'THICKNESS']) –

  Type, Type of the modifier to work on (optional)

  - `COLOR`
    Color – Color modifier type.
  - `ALPHA`
    Alpha – Alpha modifier type.
  - `THICKNESS`
    Thickness – Thickness modifier type.
- **name** (str) – Name, Name of the modifier to work on (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/freestyle.py:45](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/freestyle.py#L45)

<a id="bpy.ops.scene.freestyle_geometry_modifier_add"></a>

### bpy.ops.scene.freestyle_geometry_modifier_add(*, type='2D_OFFSET')

Add a stroke geometry modifier to the line style associated with the active lineset

**Parameters:**

**type** (Literal[[Linestyle Geometry Modifier Type Items](bpy_types_enum_items/linestyle_geometry_modifier_type_items.md#rna-enum-linestyle-geometry-modifier-type-items)]) – Type, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.scene.freestyle_lineset_add"></a>

### bpy.ops.scene.freestyle_lineset_add()

Add a line set into the list of line sets

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.scene.freestyle_lineset_copy"></a>

### bpy.ops.scene.freestyle_lineset_copy()

Copy the active line set to the internal clipboard

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.scene.freestyle_lineset_move"></a>

### bpy.ops.scene.freestyle_lineset_move(*, direction='UP')

Change the position of the active line set within the list of line sets

**Parameters:**

**direction** (Literal['UP', 'DOWN']) – Direction, Direction to move the active line set towards (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.scene.freestyle_lineset_paste"></a>

### bpy.ops.scene.freestyle_lineset_paste()

Paste the internal clipboard content to the active line set

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.scene.freestyle_lineset_remove"></a>

### bpy.ops.scene.freestyle_lineset_remove()

Remove the active line set from the list of line sets

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.scene.freestyle_linestyle_new"></a>

### bpy.ops.scene.freestyle_linestyle_new()

Create a new line style, reusable by multiple line sets

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.scene.freestyle_modifier_copy"></a>

### bpy.ops.scene.freestyle_modifier_copy()

Duplicate the modifier within the list of modifiers

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.scene.freestyle_modifier_move"></a>

### bpy.ops.scene.freestyle_modifier_move(*, direction='UP')

Move the modifier within the list of modifiers

**Parameters:**

**direction** (Literal['UP', 'DOWN']) – Direction, Direction to move the chosen modifier towards (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.scene.freestyle_modifier_remove"></a>

### bpy.ops.scene.freestyle_modifier_remove()

Remove the modifier from the list of modifiers

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.scene.freestyle_module_add"></a>

### bpy.ops.scene.freestyle_module_add()

Add a style module into the list of modules

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.scene.freestyle_module_move"></a>

### bpy.ops.scene.freestyle_module_move(*, direction='UP')

Change the position of the style module within in the list of style modules

**Parameters:**

**direction** (Literal['UP', 'DOWN']) – Direction, Direction to move the chosen style module towards (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.scene.freestyle_module_open"></a>

### bpy.ops.scene.freestyle_module_open(*, filepath='', make_internal=True)

Open a style module file

**Parameters:**

- **filepath** (str) – filepath, (optional, never None)
- **make_internal** (bool) – Make internal, Make module file internal after loading (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/freestyle.py:215](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/freestyle.py#L215)

<a id="bpy.ops.scene.freestyle_module_remove"></a>

### bpy.ops.scene.freestyle_module_remove()

Remove the style module from the stack

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.scene.freestyle_stroke_material_create"></a>

### bpy.ops.scene.freestyle_stroke_material_create()

Create Freestyle stroke material for testing

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.scene.freestyle_thickness_modifier_add"></a>

### bpy.ops.scene.freestyle_thickness_modifier_add(*, type='ALONG_STROKE')

Add a line thickness modifier to the line style associated with the active lineset

**Parameters:**

**type** (Literal[[Linestyle Thickness Modifier Type Items](bpy_types_enum_items/linestyle_thickness_modifier_type_items.md#rna-enum-linestyle-thickness-modifier-type-items)]) – Type, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.scene.gltf2_action_filter_refresh"></a>

### bpy.ops.scene.gltf2_action_filter_refresh()

Refresh list of actions

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[addons_core/io_scene_gltf2/blender/com/gltf2_blender_ui.py:681](https://projects.blender.org/blender/blender/src/branch/main/scripts/addons_core/io_scene_gltf2/blender/com/gltf2_blender_ui.py#L681)

<a id="bpy.ops.scene.gpencil_brush_preset_add"></a>

### bpy.ops.scene.gpencil_brush_preset_add(*, name='', remove_name=False, remove_active=False)

Add or remove Grease Pencil brush preset

**Parameters:**

- **name** (str) – Name, Name of the preset, used to make the path name (optional, never None)
- **remove_name** (bool) – remove_name, (optional)
- **remove_active** (bool) – remove_active, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/presets.py:119](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/presets.py#L119)

<a id="bpy.ops.scene.gpencil_material_preset_add"></a>

### bpy.ops.scene.gpencil_material_preset_add(*, name='', remove_name=False, remove_active=False)

Add or remove Grease Pencil material preset

**Parameters:**

- **name** (str) – Name, Name of the preset, used to make the path name (optional, never None)
- **remove_name** (bool) – remove_name, (optional)
- **remove_active** (bool) – remove_active, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/presets.py:119](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/presets.py#L119)

<a id="bpy.ops.scene.new"></a>

### bpy.ops.scene.new(*, type='NEW')

Add new scene by type

**Parameters:**

**type** (Literal['NEW', 'EMPTY', 'LINK_COPY', 'FULL_COPY']) –

Type, (optional)

- `NEW`
  New – Add a new, empty scene with default settings.
- `EMPTY`
  Copy Settings – Add a new, empty scene, and copy settings from the current scene.
- `LINK_COPY`
  Linked Copy – Link in the collections from the current scene (shallow copy).
- `FULL_COPY`
  Full Copy – Make a full copy of the current scene.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.scene.new_sequencer"></a>

### bpy.ops.scene.new_sequencer(*, type='NEW')

Add new scene by type in the sequence editor and assign to active strip

**Parameters:**

**type** (Literal['NEW', 'EMPTY', 'LINK_COPY', 'FULL_COPY']) –

Type, (optional)

- `NEW`
  New – Add a new, empty scene with default settings.
- `EMPTY`
  Copy Settings – Add a new, empty scene, and copy settings from the current scene.
- `LINK_COPY`
  Linked Copy – Link in the collections from the current scene (shallow copy).
- `FULL_COPY`
  Full Copy – Make a full copy of the current scene.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.scene.new_sequencer_scene"></a>

### bpy.ops.scene.new_sequencer_scene(*, type='NEW')

Add new scene to be used by the sequencer

**Parameters:**

**type** (Literal['NEW', 'EMPTY', 'LINK_COPY', 'FULL_COPY']) –

Type, (optional)

- `NEW`
  New – Add a new, empty scene with default settings.
- `EMPTY`
  Copy Settings – Add a new, empty scene, and copy settings from the current scene.
- `LINK_COPY`
  Linked Copy – Link in the collections from the current scene (shallow copy).
- `FULL_COPY`
  Full Copy – Make a full copy of the current scene.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.scene.render_view_add"></a>

### bpy.ops.scene.render_view_add()

Add a render view

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.scene.render_view_remove"></a>

### bpy.ops.scene.render_view_remove()

Remove the selected render view

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.scene.view_layer_add"></a>

### bpy.ops.scene.view_layer_add(*, type='NEW')

Add a view layer

**Parameters:**

**type** (Literal['NEW', 'COPY', 'EMPTY']) –

Type, (optional)

- `NEW`
  New – Add a new view layer.
- `COPY`
  Copy Settings – Copy settings of current view layer.
- `EMPTY`
  Blank – Add a new view layer with all collections disabled.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.scene.view_layer_add_aov"></a>

### bpy.ops.scene.view_layer_add_aov()

Add a Shader AOV

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.scene.view_layer_add_lightgroup"></a>

### bpy.ops.scene.view_layer_add_lightgroup(*, name='')

Add a Light Group

**Parameters:**

**name** (str) – Name, Name of newly created lightgroup (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.scene.view_layer_add_used_lightgroups"></a>

### bpy.ops.scene.view_layer_add_used_lightgroups()

Add all used Light Groups

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.scene.view_layer_remove"></a>

### bpy.ops.scene.view_layer_remove()

Remove the selected view layer

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.scene.view_layer_remove_aov"></a>

### bpy.ops.scene.view_layer_remove_aov()

Remove Active AOV

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.scene.view_layer_remove_lightgroup"></a>

### bpy.ops.scene.view_layer_remove_lightgroup()

Remove Active Lightgroup

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.scene.view_layer_remove_unused_lightgroups"></a>

### bpy.ops.scene.view_layer_remove_unused_lightgroups()

Remove all unused Light Groups

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]
