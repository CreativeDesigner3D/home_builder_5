<!-- source: Blender Python API reference 5.2 / bpy.types.World.html -->

<a id="world-id"></a>

# World(ID)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")

<a id="bpy.types.World"></a>

### class bpy.types.World(ID)

World data-block describing the environment and ambient lighting of a scene

<a id="bpy.types.World.animation_data"></a>

#### bpy.types.World.animation_data

Animation data for this data-block (readonly)

**Type:**

[`AnimData`](bpy.types.AnimData.md#bpy.types.AnimData "bpy.types.AnimData") | None

<a id="bpy.types.World.color"></a>

#### bpy.types.World.color

Color of the background (array of 3 items, in [0, inf], default (0.05, 0.05, 0.05))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.World.cycles"></a>

#### bpy.types.World.cycles

Cycles world settings (readonly)

**Type:**

`CyclesWorldSettings` | None

<a id="bpy.types.World.cycles_visibility"></a>

#### bpy.types.World.cycles_visibility

Cycles visibility settings (readonly)

**Type:**

`CyclesVisibilitySettings` | None

<a id="bpy.types.World.light_settings"></a>

#### bpy.types.World.light_settings

World lighting settings (readonly, never None)

**Type:**

[`WorldLighting`](bpy.types.WorldLighting.md#bpy.types.WorldLighting "bpy.types.WorldLighting")

<a id="bpy.types.World.lightgroup"></a>

#### bpy.types.World.lightgroup

Lightgroup that the world belongs to (default “”, never None)

**Type:**

str

<a id="bpy.types.World.mist_settings"></a>

#### bpy.types.World.mist_settings

World mist settings (readonly, never None)

**Type:**

[`WorldMistSettings`](bpy.types.WorldMistSettings.md#bpy.types.WorldMistSettings "bpy.types.WorldMistSettings")

<a id="bpy.types.World.node_tree"></a>

#### bpy.types.World.node_tree

Node tree for node based worlds (readonly)

**Type:**

[`NodeTree`](bpy.types.NodeTree.md#bpy.types.NodeTree "bpy.types.NodeTree") | None

<a id="bpy.types.World.probe_resolution"></a>

#### bpy.types.World.probe_resolution

Resolution when baked to a texture (default `'1024'`)

**Type:**

Literal[‘128’, ‘256’, ‘512’, ‘1024’, ‘2048’, ‘4096’]

<a id="bpy.types.World.sun_angle"></a>

#### bpy.types.World.sun_angle

Angular diameter of the Sun as seen from the Earth (in [0, 3.14159], default 0.00918043)

**Type:**

float

<a id="bpy.types.World.sun_shadow_filter_radius"></a>

#### bpy.types.World.sun_shadow_filter_radius

Blur shadow aliasing using Percentage Closer Filtering (in [0, inf], default 1.0)

**Type:**

float

<a id="bpy.types.World.sun_shadow_jitter_overblur"></a>

#### bpy.types.World.sun_shadow_jitter_overblur

Apply shadow tracing to each jittered sample to reduce under-sampling artifacts (in [0, 100], default 10.0)

**Type:**

float

<a id="bpy.types.World.sun_shadow_maximum_resolution"></a>

#### bpy.types.World.sun_shadow_maximum_resolution

Maximum size of a shadow map pixel. Higher values use less memory at the cost of shadow quality. (in [0, inf], default 0.001)

**Type:**

float

<a id="bpy.types.World.sun_threshold"></a>

#### bpy.types.World.sun_threshold

If non-zero, the maximum value for world contribution that will be recorded inside the world light probe. The excess contribution is converted to a sun light. This reduces the light bleeding caused by very bright light sources. (in [0, inf], default 10.0)

**Type:**

float

<a id="bpy.types.World.use_eevee_finite_volume"></a>

#### bpy.types.World.use_eevee_finite_volume

The world’s volume used to be rendered by EEVEE Legacy. Conversion is needed for it to render properly. (default False)

**Type:**

bool

<a id="bpy.types.World.use_nodes"></a>

#### bpy.types.World.use_nodes

Use shader nodes to render the world (default False)

Deprecated since version 5.0: removal planned in version 6.0

Unused but kept for compatibility reasons. Setting the property has no effect, and getting it always returns True.

**Type:**

bool

<a id="bpy.types.World.use_sun_shadow"></a>

#### bpy.types.World.use_sun_shadow

Enable sun shadow casting (default True)

**Type:**

bool

<a id="bpy.types.World.use_sun_shadow_jitter"></a>

#### bpy.types.World.use_sun_shadow_jitter

Enable jittered soft shadows to increase shadow precision (disabled in viewport unless enabled in the render settings). Has a high performance impact. (default False)

**Type:**

bool

<a id="bpy.types.World.inline_shader_nodes"></a>

#### bpy.types.World.inline_shader_nodes()

Get the inlined shader nodes of this world. This preprocesses the node tree
to remove nested groups, repeat zones and more.

**Returns:**

The inlined shader nodes.

**Return type:**

[`InlineShaderNodes`](bpy.types.InlineShaderNodes.md#bpy.types.InlineShaderNodes "bpy.types.InlineShaderNodes")

<a id="bpy.types.World.bl_rna_get_subclass"></a>

#### classmethod bpy.types.World.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.World.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.World.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

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
| - `bpy.context.world` - [`BlendData.worlds`](bpy.types.BlendData.md#bpy.types.BlendData.worlds "bpy.types.BlendData.worlds") - [`BlendDataWorlds.new`](bpy.types.BlendDataWorlds.md#bpy.types.BlendDataWorlds.new "bpy.types.BlendDataWorlds.new") | - [`BlendDataWorlds.remove`](bpy.types.BlendDataWorlds.md#bpy.types.BlendDataWorlds.remove "bpy.types.BlendDataWorlds.remove") - [`Scene.world`](bpy.types.Scene.md#bpy.types.Scene.world "bpy.types.Scene.world") - [`ViewLayer.world_override`](bpy.types.ViewLayer.md#bpy.types.ViewLayer.world_override "bpy.types.ViewLayer.world_override") |
