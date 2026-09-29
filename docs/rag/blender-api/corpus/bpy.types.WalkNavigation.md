<!-- source: Blender Python API reference 5.2 / bpy.types.WalkNavigation.html -->

<a id="walknavigation-bpy-struct"></a>

# WalkNavigation(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.WalkNavigation"></a>

### class bpy.types.WalkNavigation(bpy_struct)

Walk navigation settings

<a id="bpy.types.WalkNavigation.jump_height"></a>

#### bpy.types.WalkNavigation.jump_height

Maximum height of a jump (in [0.1, 100], default 0.4)

**Type:**

float

<a id="bpy.types.WalkNavigation.mouse_speed"></a>

#### bpy.types.WalkNavigation.mouse_speed

Speed factor for when looking around, high values mean faster mouse movement (in [0.01, 10], default 1.0)

**Type:**

float

<a id="bpy.types.WalkNavigation.teleport_time"></a>

#### bpy.types.WalkNavigation.teleport_time

Interval of time warp when teleporting in navigation mode (in [0, 10], default 0.2)

**Type:**

float

<a id="bpy.types.WalkNavigation.use_gravity"></a>

#### bpy.types.WalkNavigation.use_gravity

Walk with gravity, or free navigate (default False)

**Type:**

bool

<a id="bpy.types.WalkNavigation.use_mouse_reverse"></a>

#### bpy.types.WalkNavigation.use_mouse_reverse

Reverse the vertical movement of the mouse (default False)

**Type:**

bool

<a id="bpy.types.WalkNavigation.view_height"></a>

#### bpy.types.WalkNavigation.view_height

View distance from the floor when walking (in [0, 1000], default 1.6)

**Type:**

float

<a id="bpy.types.WalkNavigation.walk_speed"></a>

#### bpy.types.WalkNavigation.walk_speed

Base speed for walking and flying (in [0.01, 100], default 2.5)

**Type:**

float

<a id="bpy.types.WalkNavigation.walk_speed_factor"></a>

#### bpy.types.WalkNavigation.walk_speed_factor

Multiplication factor when using the fast or slow modifiers (in [0.01, 10], default 5.0)

**Type:**

float

<a id="bpy.types.WalkNavigation.bl_rna_get_subclass"></a>

#### classmethod bpy.types.WalkNavigation.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.WalkNavigation.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.WalkNavigation.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`PreferencesInput.walk_navigation`](bpy.types.PreferencesInput.md#bpy.types.PreferencesInput.walk_navigation "bpy.types.PreferencesInput.walk_navigation") |  |
