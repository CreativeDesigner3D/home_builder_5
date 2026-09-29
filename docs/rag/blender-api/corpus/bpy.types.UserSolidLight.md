<!-- source: Blender Python API reference 5.2 / bpy.types.UserSolidLight.html -->

<a id="usersolidlight-bpy-struct"></a>

# UserSolidLight(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.UserSolidLight"></a>

### class bpy.types.UserSolidLight(bpy_struct)

Light used for Studio lighting in solid shading mode

<a id="bpy.types.UserSolidLight.diffuse_color"></a>

#### bpy.types.UserSolidLight.diffuse_color

Color of the light’s diffuse highlight (array of 3 items, in [0, inf], default (0.8, 0.8, 0.8))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.UserSolidLight.direction"></a>

#### bpy.types.UserSolidLight.direction

Direction that the light is shining (array of 3 items, in [-inf, inf], default (0.0, 0.0, 1.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.UserSolidLight.smooth"></a>

#### bpy.types.UserSolidLight.smooth

Smooth the lighting from this light (in [0, 1], default 0.5)

**Type:**

float

<a id="bpy.types.UserSolidLight.specular_color"></a>

#### bpy.types.UserSolidLight.specular_color

Color of the light’s specular highlight (array of 3 items, in [0, inf], default (0.8, 0.8, 0.8))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.UserSolidLight.use"></a>

#### bpy.types.UserSolidLight.use

Enable this light in solid shading mode (default True)

**Type:**

bool

<a id="bpy.types.UserSolidLight.bl_rna_get_subclass"></a>

#### classmethod bpy.types.UserSolidLight.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.UserSolidLight.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.UserSolidLight.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`PreferencesSystem.solid_lights`](bpy.types.PreferencesSystem.md#bpy.types.PreferencesSystem.solid_lights "bpy.types.PreferencesSystem.solid_lights") | - [`StudioLight.solid_lights`](bpy.types.StudioLight.md#bpy.types.StudioLight.solid_lights "bpy.types.StudioLight.solid_lights") |
