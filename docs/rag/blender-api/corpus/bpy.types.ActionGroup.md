<!-- source: Blender Python API reference 5.2 / bpy.types.ActionGroup.html -->

<a id="actiongroup-bpy-struct"></a>

# ActionGroup(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.ActionGroup"></a>

### class bpy.types.ActionGroup(bpy_struct)

Groups of F-Curves

<a id="bpy.types.ActionGroup.channels"></a>

#### bpy.types.ActionGroup.channels

F-Curves in this group (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`FCurve`](bpy.types.FCurve.md#bpy.types.FCurve "bpy.types.FCurve")]

<a id="bpy.types.ActionGroup.color_set"></a>

#### bpy.types.ActionGroup.color_set

Custom color set to use (default `'DEFAULT'`)

**Type:**

Literal[[Color Sets Items](bpy_types_enum_items/color_sets_items.md#rna-enum-color-sets-items)]

<a id="bpy.types.ActionGroup.colors"></a>

#### bpy.types.ActionGroup.colors

Copy of the colors associated with the group’s color set (readonly, never None)

**Type:**

[`ThemeBoneColorSet`](bpy.types.ThemeBoneColorSet.md#bpy.types.ThemeBoneColorSet "bpy.types.ThemeBoneColorSet")

<a id="bpy.types.ActionGroup.is_custom_color_set"></a>

#### bpy.types.ActionGroup.is_custom_color_set

Color set is user-defined instead of a fixed theme color set (default False, readonly)

**Type:**

bool

<a id="bpy.types.ActionGroup.lock"></a>

#### bpy.types.ActionGroup.lock

Action group is locked (default False)

**Type:**

bool

<a id="bpy.types.ActionGroup.mute"></a>

#### bpy.types.ActionGroup.mute

Action group is muted (default False)

**Type:**

bool

<a id="bpy.types.ActionGroup.name"></a>

#### bpy.types.ActionGroup.name

(default “”, never None)

**Type:**

str

<a id="bpy.types.ActionGroup.select"></a>

#### bpy.types.ActionGroup.select

Action group is selected (default False)

**Type:**

bool

<a id="bpy.types.ActionGroup.show_expanded"></a>

#### bpy.types.ActionGroup.show_expanded

Action group is expanded except in graph editor (default False)

**Type:**

bool

<a id="bpy.types.ActionGroup.show_expanded_graph"></a>

#### bpy.types.ActionGroup.show_expanded_graph

Action group is expanded in graph editor (default False)

**Type:**

bool

<a id="bpy.types.ActionGroup.use_pin"></a>

#### bpy.types.ActionGroup.use_pin

(default False)

**Type:**

bool

<a id="bpy.types.ActionGroup.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ActionGroup.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ActionGroup.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ActionGroup.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`ActionChannelbag.groups`](bpy.types.ActionChannelbag.md#bpy.types.ActionChannelbag.groups "bpy.types.ActionChannelbag.groups") - [`ActionChannelbagGroups.new`](bpy.types.ActionChannelbagGroups.md#bpy.types.ActionChannelbagGroups.new "bpy.types.ActionChannelbagGroups.new") | - [`ActionChannelbagGroups.remove`](bpy.types.ActionChannelbagGroups.md#bpy.types.ActionChannelbagGroups.remove "bpy.types.ActionChannelbagGroups.remove") - [`FCurve.group`](bpy.types.FCurve.md#bpy.types.FCurve.group "bpy.types.FCurve.group") |
