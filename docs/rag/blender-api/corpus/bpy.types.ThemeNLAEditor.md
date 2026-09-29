<!-- source: Blender Python API reference 5.2 / bpy.types.ThemeNLAEditor.html -->

<a id="themenlaeditor-bpy-struct"></a>

# ThemeNLAEditor(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.ThemeNLAEditor"></a>

### class bpy.types.ThemeNLAEditor(bpy_struct)

Theme settings for the NLA Editor

<a id="bpy.types.ThemeNLAEditor.active_action"></a>

#### bpy.types.ThemeNLAEditor.active_action

Animation data-block has active action (array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.ThemeNLAEditor.active_action_unset"></a>

#### bpy.types.ThemeNLAEditor.active_action_unset

Animation data-block does not have active action (array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.ThemeNLAEditor.grid"></a>

#### bpy.types.ThemeNLAEditor.grid

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeNLAEditor.keyframe_border"></a>

#### bpy.types.ThemeNLAEditor.keyframe_border

Color of keyframe border (array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.ThemeNLAEditor.keyframe_border_selected"></a>

#### bpy.types.ThemeNLAEditor.keyframe_border_selected

Color of selected keyframe border (array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.ThemeNLAEditor.meta_strips"></a>

#### bpy.types.ThemeNLAEditor.meta_strips

Unselected Meta Strip (for grouping related strips) (array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeNLAEditor.meta_strips_selected"></a>

#### bpy.types.ThemeNLAEditor.meta_strips_selected

Selected Meta Strip (for grouping related strips) (array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeNLAEditor.sound_strips"></a>

#### bpy.types.ThemeNLAEditor.sound_strips

Unselected Sound Strip (for timing speaker sounds) (array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeNLAEditor.sound_strips_selected"></a>

#### bpy.types.ThemeNLAEditor.sound_strips_selected

Selected Sound Strip (for timing speaker sounds) (array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeNLAEditor.space"></a>

#### bpy.types.ThemeNLAEditor.space

Settings for space (readonly, never None)

**Type:**

[`ThemeSpaceGeneric`](bpy.types.ThemeSpaceGeneric.md#bpy.types.ThemeSpaceGeneric "bpy.types.ThemeSpaceGeneric")

<a id="bpy.types.ThemeNLAEditor.strips"></a>

#### bpy.types.ThemeNLAEditor.strips

Unselected Action-Clip Strip (array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeNLAEditor.strips_selected"></a>

#### bpy.types.ThemeNLAEditor.strips_selected

Selected Action-Clip Strip (array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeNLAEditor.transition_strips"></a>

#### bpy.types.ThemeNLAEditor.transition_strips

Unselected Transition Strip (array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeNLAEditor.transition_strips_selected"></a>

#### bpy.types.ThemeNLAEditor.transition_strips_selected

Selected Transition Strip (array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeNLAEditor.tweak"></a>

#### bpy.types.ThemeNLAEditor.tweak

Color for strip/action being “tweaked” or edited (array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeNLAEditor.tweak_duplicate"></a>

#### bpy.types.ThemeNLAEditor.tweak_duplicate

Warning/error indicator color for strips referencing the strip being tweaked (array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeNLAEditor.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ThemeNLAEditor.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ThemeNLAEditor.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ThemeNLAEditor.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Theme.nla_editor`](bpy.types.Theme.md#bpy.types.Theme.nla_editor "bpy.types.Theme.nla_editor") |  |
