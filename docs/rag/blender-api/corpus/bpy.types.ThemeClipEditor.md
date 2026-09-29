<!-- source: Blender Python API reference 5.2 / bpy.types.ThemeClipEditor.html -->

<a id="themeclipeditor-bpy-struct"></a>

# ThemeClipEditor(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.ThemeClipEditor"></a>

### class bpy.types.ThemeClipEditor(bpy_struct)

Theme settings for the Movie Clip Editor

<a id="bpy.types.ThemeClipEditor.active_marker"></a>

#### bpy.types.ThemeClipEditor.active_marker

Color of active marker (array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeClipEditor.disabled_marker"></a>

#### bpy.types.ThemeClipEditor.disabled_marker

Color of disabled marker (array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeClipEditor.grid"></a>

#### bpy.types.ThemeClipEditor.grid

(array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.ThemeClipEditor.locked_marker"></a>

#### bpy.types.ThemeClipEditor.locked_marker

Color of locked marker (array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeClipEditor.marker"></a>

#### bpy.types.ThemeClipEditor.marker

Color of marker (array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeClipEditor.marker_outline"></a>

#### bpy.types.ThemeClipEditor.marker_outline

Color of marker’s outline (array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeClipEditor.metadatabg"></a>

#### bpy.types.ThemeClipEditor.metadatabg

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeClipEditor.metadatatext"></a>

#### bpy.types.ThemeClipEditor.metadatatext

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeClipEditor.path_after"></a>

#### bpy.types.ThemeClipEditor.path_after

Color of path after current frame (array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeClipEditor.path_before"></a>

#### bpy.types.ThemeClipEditor.path_before

Color of path before current frame (array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeClipEditor.path_keyframe_after"></a>

#### bpy.types.ThemeClipEditor.path_keyframe_after

Color of keyframes on a path after current frame (array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeClipEditor.path_keyframe_before"></a>

#### bpy.types.ThemeClipEditor.path_keyframe_before

Color of keyframes on a path before current frame (array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeClipEditor.selected_marker"></a>

#### bpy.types.ThemeClipEditor.selected_marker

Color of selected marker (array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeClipEditor.space"></a>

#### bpy.types.ThemeClipEditor.space

Settings for space (readonly, never None)

**Type:**

[`ThemeSpaceGeneric`](bpy.types.ThemeSpaceGeneric.md#bpy.types.ThemeSpaceGeneric "bpy.types.ThemeSpaceGeneric")

<a id="bpy.types.ThemeClipEditor.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ThemeClipEditor.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ThemeClipEditor.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ThemeClipEditor.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Theme.clip_editor`](bpy.types.Theme.md#bpy.types.Theme.clip_editor "bpy.types.Theme.clip_editor") |  |
