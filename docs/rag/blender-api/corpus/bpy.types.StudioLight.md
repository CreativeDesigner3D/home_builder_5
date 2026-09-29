<!-- source: Blender Python API reference 5.2 / bpy.types.StudioLight.html -->

<a id="studiolight-bpy-struct"></a>

# StudioLight(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.StudioLight"></a>

### class bpy.types.StudioLight(bpy_struct)

Studio light

<a id="bpy.types.StudioLight.has_specular_highlight_pass"></a>

#### bpy.types.StudioLight.has_specular_highlight_pass

Studio light image file has separate “diffuse” and “specular” passes (default False, readonly)

**Type:**

bool

<a id="bpy.types.StudioLight.index"></a>

#### bpy.types.StudioLight.index

(in [-inf, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.StudioLight.is_user_defined"></a>

#### bpy.types.StudioLight.is_user_defined

(default False, readonly)

**Type:**

bool

<a id="bpy.types.StudioLight.light_ambient"></a>

#### bpy.types.StudioLight.light_ambient

Color of the ambient light that uniformly lit the scene (array of 3 items, in [0, inf], default (0.0, 0.0, 0.0), readonly)

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.StudioLight.name"></a>

#### bpy.types.StudioLight.name

(default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.StudioLight.path"></a>

#### bpy.types.StudioLight.path

(default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.StudioLight.solid_lights"></a>

#### bpy.types.StudioLight.solid_lights

Lights used to display objects in solid draw mode (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`UserSolidLight`](bpy.types.UserSolidLight.md#bpy.types.UserSolidLight "bpy.types.UserSolidLight")]

<a id="bpy.types.StudioLight.type"></a>

#### bpy.types.StudioLight.type

(default `'STUDIO'`, readonly)

**Type:**

Literal[‘STUDIO’, ‘WORLD’, ‘MATCAP’]

<a id="bpy.types.StudioLight.bl_rna_get_subclass"></a>

#### classmethod bpy.types.StudioLight.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.StudioLight.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.StudioLight.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([type](#bpy.types.StudioLight.type "bpy.types.StudioLight.type") | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

[type](#bpy.types.StudioLight.type "bpy.types.StudioLight.type")

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
| - [`Preferences.studio_lights`](bpy.types.Preferences.md#bpy.types.Preferences.studio_lights "bpy.types.Preferences.studio_lights") - [`StudioLights.load`](bpy.types.StudioLights.md#bpy.types.StudioLights.load "bpy.types.StudioLights.load") - [`StudioLights.new`](bpy.types.StudioLights.md#bpy.types.StudioLights.new "bpy.types.StudioLights.new") | - [`StudioLights.remove`](bpy.types.StudioLights.md#bpy.types.StudioLights.remove "bpy.types.StudioLights.remove") - [`View3DShading.selected_studio_light`](bpy.types.View3DShading.md#bpy.types.View3DShading.selected_studio_light "bpy.types.View3DShading.selected_studio_light") |
