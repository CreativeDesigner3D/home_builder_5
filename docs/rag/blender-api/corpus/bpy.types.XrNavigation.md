<!-- source: Blender Python API reference 5.2 / bpy.types.XrNavigation.html -->

<a id="xrnavigation-bpy-struct"></a>

# XrNavigation(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.XrNavigation"></a>

### class bpy.types.XrNavigation(bpy_struct)

VR navigation settings

<a id="bpy.types.XrNavigation.invert_rotation"></a>

#### bpy.types.XrNavigation.invert_rotation

Reverses the direction of rotation input (default False)

**Type:**

bool

<a id="bpy.types.XrNavigation.snap_turn"></a>

#### bpy.types.XrNavigation.snap_turn

Instantly rotates the camera by a fixed angle instead of smoothly turning (default True)

**Type:**

bool

<a id="bpy.types.XrNavigation.turn_amount"></a>

#### bpy.types.XrNavigation.turn_amount

Amount in degrees per turn when using snap turn (in [0, 6.28319], default 0.523599)

**Type:**

float

<a id="bpy.types.XrNavigation.turn_speed"></a>

#### bpy.types.XrNavigation.turn_speed

Turn speed in degrees per second (in [0, inf], default 1.0472)

**Type:**

float

<a id="bpy.types.XrNavigation.vignette_intensity"></a>

#### bpy.types.XrNavigation.vignette_intensity

Intensity of vignette that appears when moving (in [0, 100], default 70.0)

**Type:**

float

<a id="bpy.types.XrNavigation.bl_rna_get_subclass"></a>

#### classmethod bpy.types.XrNavigation.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.XrNavigation.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.XrNavigation.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`PreferencesInput.xr_navigation`](bpy.types.PreferencesInput.md#bpy.types.PreferencesInput.xr_navigation "bpy.types.PreferencesInput.xr_navigation") |  |
