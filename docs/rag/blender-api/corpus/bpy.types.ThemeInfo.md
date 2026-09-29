<!-- source: Blender Python API reference 5.2 / bpy.types.ThemeInfo.html -->

<a id="themeinfo-bpy-struct"></a>

# ThemeInfo(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.ThemeInfo"></a>

### class bpy.types.ThemeInfo(bpy_struct)

Theme settings for Info

<a id="bpy.types.ThemeInfo.info_debug"></a>

#### bpy.types.ThemeInfo.info_debug

Background color of Debug icon (array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.ThemeInfo.info_debug_text"></a>

#### bpy.types.ThemeInfo.info_debug_text

Foreground color of Debug icon (array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeInfo.info_error_text"></a>

#### bpy.types.ThemeInfo.info_error_text

Foreground color of Error icon (array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeInfo.info_info_text"></a>

#### bpy.types.ThemeInfo.info_info_text

Foreground color of Info icon (array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeInfo.info_operator"></a>

#### bpy.types.ThemeInfo.info_operator

Background color of Operator icon (array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.ThemeInfo.info_operator_text"></a>

#### bpy.types.ThemeInfo.info_operator_text

Foreground color of Operator icon (array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeInfo.info_property"></a>

#### bpy.types.ThemeInfo.info_property

Background color of Property icon (array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.ThemeInfo.info_property_text"></a>

#### bpy.types.ThemeInfo.info_property_text

Foreground color of Property icon (array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeInfo.info_selected"></a>

#### bpy.types.ThemeInfo.info_selected

Background color of selected line (array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeInfo.info_selected_text"></a>

#### bpy.types.ThemeInfo.info_selected_text

Text color of selected line (array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeInfo.info_warning_text"></a>

#### bpy.types.ThemeInfo.info_warning_text

Foreground color of Warning icon (array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeInfo.space"></a>

#### bpy.types.ThemeInfo.space

Settings for space (readonly, never None)

**Type:**

[`ThemeSpaceGeneric`](bpy.types.ThemeSpaceGeneric.md#bpy.types.ThemeSpaceGeneric "bpy.types.ThemeSpaceGeneric")

<a id="bpy.types.ThemeInfo.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ThemeInfo.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ThemeInfo.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ThemeInfo.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Theme.info`](bpy.types.Theme.md#bpy.types.Theme.info "bpy.types.Theme.info") |  |
