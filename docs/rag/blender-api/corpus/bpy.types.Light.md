<!-- source: Blender Python API reference 5.2 / bpy.types.Light.html -->

<a id="light-id"></a>

# Light(ID)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")

Subclasses

- [AreaLight(Light)](bpy.types.AreaLight.md)
- [PointLight(Light)](bpy.types.PointLight.md)
- [SpotLight(Light)](bpy.types.SpotLight.md)
- [SunLight(Light)](bpy.types.SunLight.md)

<a id="bpy.types.Light"></a>

### class bpy.types.Light(ID)

Light data-block for lighting a scene

<a id="bpy.types.Light.animation_data"></a>

#### bpy.types.Light.animation_data

Animation data for this data-block (readonly)

**Type:**

[`AnimData`](bpy.types.AnimData.md#bpy.types.AnimData "bpy.types.AnimData") | None

<a id="bpy.types.Light.color"></a>

#### bpy.types.Light.color

Light color (array of 3 items, in [0, inf], default (1.0, 1.0, 1.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.Light.cutoff_distance"></a>

#### bpy.types.Light.cutoff_distance

Distance at which the light influence will be set to 0 (in [0, inf], default 40.0)

**Type:**

float

<a id="bpy.types.Light.cycles"></a>

#### bpy.types.Light.cycles

Cycles light settings (readonly)

**Type:**

`CyclesLightSettings` | None

<a id="bpy.types.Light.diffuse_factor"></a>

#### bpy.types.Light.diffuse_factor

Diffuse reflection multiplier (in [0, inf], default 1.0)

**Type:**

float

<a id="bpy.types.Light.exposure"></a>

#### bpy.types.Light.exposure

Scales the power of the light exponentially, multiplying the intensity by 2^exposure (in [-32, 32], default 0.0)

**Type:**

float

<a id="bpy.types.Light.node_tree"></a>

#### bpy.types.Light.node_tree

Node tree for node based lights (readonly)

**Type:**

[`NodeTree`](bpy.types.NodeTree.md#bpy.types.NodeTree "bpy.types.NodeTree") | None

<a id="bpy.types.Light.normalize"></a>

#### bpy.types.Light.normalize

Normalize intensity by light area, for consistent total light output regardless of size and shape (default True)

**Type:**

bool

<a id="bpy.types.Light.specular_factor"></a>

#### bpy.types.Light.specular_factor

Specular reflection multiplier (in [0, inf], default 1.0)

**Type:**

float

<a id="bpy.types.Light.temperature"></a>

#### bpy.types.Light.temperature

Light color temperature in Kelvin (in [800, 20000], default 6500.0)

**Type:**

float

<a id="bpy.types.Light.temperature_color"></a>

#### bpy.types.Light.temperature_color

Color from Temperature (array of 3 items, in [0, inf], default (0.0, 0.0, 0.0), readonly)

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.Light.transmission_factor"></a>

#### bpy.types.Light.transmission_factor

Transmission light multiplier (in [0, inf], default 1.0)

**Type:**

float

<a id="bpy.types.Light.type"></a>

#### bpy.types.Light.type

Type of light (default `'POINT'`)

**Type:**

Literal[[Light Type Items](bpy_types_enum_items/light_type_items.md#rna-enum-light-type-items)]

<a id="bpy.types.Light.use_custom_distance"></a>

#### bpy.types.Light.use_custom_distance

Use custom attenuation distance instead of global light threshold (default False)

**Type:**

bool

<a id="bpy.types.Light.use_nodes"></a>

#### bpy.types.Light.use_nodes

Use shader nodes to render the light (default False)

Deprecated since version 5.10: removal planned in version 6.0

Unused but kept for compatibility reasons. Setting the property has no effect, and getting it always returns True.

**Type:**

bool

<a id="bpy.types.Light.use_shadow"></a>

#### bpy.types.Light.use_shadow

(default True)

**Type:**

bool

<a id="bpy.types.Light.use_temperature"></a>

#### bpy.types.Light.use_temperature

Use blackbody temperature to define a natural light color (default False)

**Type:**

bool

<a id="bpy.types.Light.volume_factor"></a>

#### bpy.types.Light.volume_factor

Volume light multiplier (in [0, inf], default 1.0)

**Type:**

float

<a id="bpy.types.Light.area"></a>

#### bpy.types.Light.area(*, matrix_world=((0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0)))

Compute light area based on type and shape. The normalize option divides light intensity by this area

**Parameters:**

**matrix_world** ([`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix") | Sequence[Sequence[float]]) – Object to world space transformation matrix (multi-dimensional array of 4 * 4 items, in [-inf, inf], optional)

**Returns:**

area, (in [-inf, inf])

**Return type:**

float

<a id="bpy.types.Light.inline_shader_nodes"></a>

#### bpy.types.Light.inline_shader_nodes()

Get the inlined shader nodes of this light. This preprocesses the node tree
to remove nested groups, repeat zones and more.

**Returns:**

The inlined shader nodes.

**Return type:**

[`InlineShaderNodes`](bpy.types.InlineShaderNodes.md#bpy.types.InlineShaderNodes "bpy.types.InlineShaderNodes")

<a id="bpy.types.Light.bl_rna_get_subclass"></a>

#### classmethod bpy.types.Light.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.Light.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.Light.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([type](#bpy.types.Light.type "bpy.types.Light.type") | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

[type](#bpy.types.Light.type "bpy.types.Light.type")

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
| - `bpy.context.light` - [`BlendData.lights`](bpy.types.BlendData.md#bpy.types.BlendData.lights "bpy.types.BlendData.lights") | - [`BlendDataLights.new`](bpy.types.BlendDataLights.md#bpy.types.BlendDataLights.new "bpy.types.BlendDataLights.new") - [`BlendDataLights.remove`](bpy.types.BlendDataLights.md#bpy.types.BlendDataLights.remove "bpy.types.BlendDataLights.remove") |
