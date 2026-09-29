<!-- source: Blender Python API reference 5.2 / bpy.types.ViewLayer.html -->

<a id="viewlayer-bpy-struct"></a>

# ViewLayer(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.ViewLayer"></a>

### class bpy.types.ViewLayer(bpy_struct)

View layer

<a id="bpy.types.ViewLayer.active_aov"></a>

#### bpy.types.ViewLayer.active_aov

Active AOV (readonly)

**Type:**

[`AOV`](bpy.types.AOV.md#bpy.types.AOV "bpy.types.AOV") | None

<a id="bpy.types.ViewLayer.active_aov_index"></a>

#### bpy.types.ViewLayer.active_aov_index

Index of active AOV (in [0, inf], default 0)

**Type:**

int

<a id="bpy.types.ViewLayer.active_layer_collection"></a>

#### bpy.types.ViewLayer.active_layer_collection

Active layer collection in this view layer’s hierarchy (never None)

**Type:**

[`LayerCollection`](bpy.types.LayerCollection.md#bpy.types.LayerCollection "bpy.types.LayerCollection")

<a id="bpy.types.ViewLayer.active_lightgroup"></a>

#### bpy.types.ViewLayer.active_lightgroup

Active Lightgroup (readonly)

**Type:**

[`Lightgroup`](bpy.types.Lightgroup.md#bpy.types.Lightgroup "bpy.types.Lightgroup") | None

<a id="bpy.types.ViewLayer.active_lightgroup_index"></a>

#### bpy.types.ViewLayer.active_lightgroup_index

Index of active lightgroup (in [0, inf], default 0)

**Type:**

int

<a id="bpy.types.ViewLayer.aovs"></a>

#### bpy.types.ViewLayer.aovs

(default None, readonly)

**Type:**

[`AOVs`](bpy.types.AOVs.md#bpy.types.AOVs "bpy.types.AOVs")[[`AOV`](bpy.types.AOV.md#bpy.types.AOV "bpy.types.AOV")]

<a id="bpy.types.ViewLayer.cycles"></a>

#### bpy.types.ViewLayer.cycles

Cycles ViewLayer Settings (readonly)

**Type:**

`CyclesRenderLayerSettings` | None

<a id="bpy.types.ViewLayer.depsgraph"></a>

#### bpy.types.ViewLayer.depsgraph

Dependencies in the scene data (readonly)

**Type:**

[`Depsgraph`](bpy.types.Depsgraph.md#bpy.types.Depsgraph "bpy.types.Depsgraph") | None

<a id="bpy.types.ViewLayer.eevee"></a>

#### bpy.types.ViewLayer.eevee

View layer settings for EEVEE (readonly, never None)

**Type:**

[`ViewLayerEEVEE`](bpy.types.ViewLayerEEVEE.md#bpy.types.ViewLayerEEVEE "bpy.types.ViewLayerEEVEE")

<a id="bpy.types.ViewLayer.freestyle_settings"></a>

#### bpy.types.ViewLayer.freestyle_settings

(readonly, never None)

**Type:**

[`FreestyleSettings`](bpy.types.FreestyleSettings.md#bpy.types.FreestyleSettings "bpy.types.FreestyleSettings")

<a id="bpy.types.ViewLayer.has_export_collections"></a>

#### bpy.types.ViewLayer.has_export_collections

At least one Collection in this View Layer has an exporter (default False, readonly)

**Type:**

bool

<a id="bpy.types.ViewLayer.layer_collection"></a>

#### bpy.types.ViewLayer.layer_collection

Root of collections hierarchy of this view layer, its ‘collection’ pointer property is the same as the scene’s master collection (readonly, never None)

**Type:**

[`LayerCollection`](bpy.types.LayerCollection.md#bpy.types.LayerCollection "bpy.types.LayerCollection")

<a id="bpy.types.ViewLayer.lightgroups"></a>

#### bpy.types.ViewLayer.lightgroups

(default None, readonly)

**Type:**

[`Lightgroups`](bpy.types.Lightgroups.md#bpy.types.Lightgroups "bpy.types.Lightgroups")[[`Lightgroup`](bpy.types.Lightgroup.md#bpy.types.Lightgroup "bpy.types.Lightgroup")]

<a id="bpy.types.ViewLayer.material_override"></a>

#### bpy.types.ViewLayer.material_override

Material to override all other materials in this view layer

**Type:**

[`Material`](bpy.types.Material.md#bpy.types.Material "bpy.types.Material") | None

<a id="bpy.types.ViewLayer.name"></a>

#### bpy.types.ViewLayer.name

View layer name (default “”, never None)

**Type:**

str

<a id="bpy.types.ViewLayer.objects"></a>

#### bpy.types.ViewLayer.objects

All the objects in this layer (default None, readonly)

**Type:**

[`LayerObjects`](bpy.types.LayerObjects.md#bpy.types.LayerObjects "bpy.types.LayerObjects")[[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object")]

<a id="bpy.types.ViewLayer.pass_alpha_threshold"></a>

#### bpy.types.ViewLayer.pass_alpha_threshold

Z, Index, normal, UV and vector passes are only affected by surfaces with alpha transparency equal to or higher than this threshold (in [0, 1], default 0.5)

**Type:**

float

<a id="bpy.types.ViewLayer.pass_cryptomatte_depth"></a>

#### bpy.types.ViewLayer.pass_cryptomatte_depth

Sets how many unique objects can be distinguished per pixel (in [2, 16], default 6)

**Type:**

int

<a id="bpy.types.ViewLayer.samples"></a>

#### bpy.types.ViewLayer.samples

Override number of render samples for this view layer, 0 will use the scene setting (in [0, inf], default 0)

**Type:**

int

<a id="bpy.types.ViewLayer.use"></a>

#### bpy.types.ViewLayer.use

Enable or disable rendering of this View Layer (default True)

**Type:**

bool

<a id="bpy.types.ViewLayer.use_ao"></a>

#### bpy.types.ViewLayer.use_ao

Render Ambient Occlusion in this Layer (default True)

**Type:**

bool

<a id="bpy.types.ViewLayer.use_freestyle"></a>

#### bpy.types.ViewLayer.use_freestyle

Render stylized strokes in this Layer (default True)

**Type:**

bool

<a id="bpy.types.ViewLayer.use_grease_pencil"></a>

#### bpy.types.ViewLayer.use_grease_pencil

Render Grease Pencil on this layer (default True)

**Type:**

bool

<a id="bpy.types.ViewLayer.use_motion_blur"></a>

#### bpy.types.ViewLayer.use_motion_blur

Render motion blur in this Layer, if enabled in the scene (default True)

**Type:**

bool

<a id="bpy.types.ViewLayer.use_pass_ambient_occlusion"></a>

#### bpy.types.ViewLayer.use_pass_ambient_occlusion

Deliver Ambient Occlusion pass (default False)

**Type:**

bool

<a id="bpy.types.ViewLayer.use_pass_combined"></a>

#### bpy.types.ViewLayer.use_pass_combined

Deliver full combined RGBA buffer (default True)

**Type:**

bool

<a id="bpy.types.ViewLayer.use_pass_cryptomatte_accurate"></a>

#### bpy.types.ViewLayer.use_pass_cryptomatte_accurate

Generate a more accurate cryptomatte pass (default True)

**Type:**

bool

<a id="bpy.types.ViewLayer.use_pass_cryptomatte_asset"></a>

#### bpy.types.ViewLayer.use_pass_cryptomatte_asset

Render cryptomatte asset pass, for isolating groups of objects with the same parent (default False)

**Type:**

bool

<a id="bpy.types.ViewLayer.use_pass_cryptomatte_material"></a>

#### bpy.types.ViewLayer.use_pass_cryptomatte_material

Render cryptomatte material pass, for isolating materials in compositing (default False)

**Type:**

bool

<a id="bpy.types.ViewLayer.use_pass_cryptomatte_object"></a>

#### bpy.types.ViewLayer.use_pass_cryptomatte_object

Render cryptomatte object pass, for isolating objects in compositing (default False)

**Type:**

bool

<a id="bpy.types.ViewLayer.use_pass_diffuse_color"></a>

#### bpy.types.ViewLayer.use_pass_diffuse_color

Deliver diffuse color pass (default False)

**Type:**

bool

<a id="bpy.types.ViewLayer.use_pass_diffuse_direct"></a>

#### bpy.types.ViewLayer.use_pass_diffuse_direct

Deliver diffuse direct pass (default False)

**Type:**

bool

<a id="bpy.types.ViewLayer.use_pass_diffuse_indirect"></a>

#### bpy.types.ViewLayer.use_pass_diffuse_indirect

Deliver diffuse indirect pass (default False)

**Type:**

bool

<a id="bpy.types.ViewLayer.use_pass_emit"></a>

#### bpy.types.ViewLayer.use_pass_emit

Deliver emission pass (default False)

**Type:**

bool

<a id="bpy.types.ViewLayer.use_pass_environment"></a>

#### bpy.types.ViewLayer.use_pass_environment

Deliver environment lighting pass (default False)

**Type:**

bool

<a id="bpy.types.ViewLayer.use_pass_glossy_color"></a>

#### bpy.types.ViewLayer.use_pass_glossy_color

Deliver glossy color pass (default False)

**Type:**

bool

<a id="bpy.types.ViewLayer.use_pass_glossy_direct"></a>

#### bpy.types.ViewLayer.use_pass_glossy_direct

Deliver glossy direct pass (default False)

**Type:**

bool

<a id="bpy.types.ViewLayer.use_pass_glossy_indirect"></a>

#### bpy.types.ViewLayer.use_pass_glossy_indirect

Deliver glossy indirect pass (default False)

**Type:**

bool

<a id="bpy.types.ViewLayer.use_pass_grease_pencil"></a>

#### bpy.types.ViewLayer.use_pass_grease_pencil

Deliver Grease Pencil render result in a separate pass (default False)

**Type:**

bool

<a id="bpy.types.ViewLayer.use_pass_material_index"></a>

#### bpy.types.ViewLayer.use_pass_material_index

Deliver material index pass (default False)

**Type:**

bool

<a id="bpy.types.ViewLayer.use_pass_mist"></a>

#### bpy.types.ViewLayer.use_pass_mist

Deliver mist factor pass (0.0 to 1.0) (default False)

**Type:**

bool

<a id="bpy.types.ViewLayer.use_pass_normal"></a>

#### bpy.types.ViewLayer.use_pass_normal

Deliver normal pass (default False)

**Type:**

bool

<a id="bpy.types.ViewLayer.use_pass_object_index"></a>

#### bpy.types.ViewLayer.use_pass_object_index

Deliver object index pass (default False)

**Type:**

bool

<a id="bpy.types.ViewLayer.use_pass_position"></a>

#### bpy.types.ViewLayer.use_pass_position

Deliver position pass (default False)

**Type:**

bool

<a id="bpy.types.ViewLayer.use_pass_shadow"></a>

#### bpy.types.ViewLayer.use_pass_shadow

Deliver shadow pass (default False)

**Type:**

bool

<a id="bpy.types.ViewLayer.use_pass_subsurface_color"></a>

#### bpy.types.ViewLayer.use_pass_subsurface_color

Deliver subsurface color pass (default False)

**Type:**

bool

<a id="bpy.types.ViewLayer.use_pass_subsurface_direct"></a>

#### bpy.types.ViewLayer.use_pass_subsurface_direct

Deliver subsurface direct pass (default False)

**Type:**

bool

<a id="bpy.types.ViewLayer.use_pass_subsurface_indirect"></a>

#### bpy.types.ViewLayer.use_pass_subsurface_indirect

Deliver subsurface indirect pass (default False)

**Type:**

bool

<a id="bpy.types.ViewLayer.use_pass_transmission_color"></a>

#### bpy.types.ViewLayer.use_pass_transmission_color

Deliver transmission color pass (default False)

**Type:**

bool

<a id="bpy.types.ViewLayer.use_pass_transmission_direct"></a>

#### bpy.types.ViewLayer.use_pass_transmission_direct

Deliver transmission direct pass (default False)

**Type:**

bool

<a id="bpy.types.ViewLayer.use_pass_transmission_indirect"></a>

#### bpy.types.ViewLayer.use_pass_transmission_indirect

Deliver transmission indirect pass (default False)

**Type:**

bool

<a id="bpy.types.ViewLayer.use_pass_uv"></a>

#### bpy.types.ViewLayer.use_pass_uv

Deliver texture UV pass (default False)

**Type:**

bool

<a id="bpy.types.ViewLayer.use_pass_vector"></a>

#### bpy.types.ViewLayer.use_pass_vector

Deliver speed vector pass (default False)

**Type:**

bool

<a id="bpy.types.ViewLayer.use_pass_z"></a>

#### bpy.types.ViewLayer.use_pass_z

Deliver depth values pass (default False)

**Type:**

bool

<a id="bpy.types.ViewLayer.use_sky"></a>

#### bpy.types.ViewLayer.use_sky

Render Sky in this Layer (default True)

**Type:**

bool

<a id="bpy.types.ViewLayer.use_solid"></a>

#### bpy.types.ViewLayer.use_solid

Render Solid faces in this Layer (default True)

**Type:**

bool

<a id="bpy.types.ViewLayer.use_strand"></a>

#### bpy.types.ViewLayer.use_strand

Render Strands in this Layer (default True)

**Type:**

bool

<a id="bpy.types.ViewLayer.use_volumes"></a>

#### bpy.types.ViewLayer.use_volumes

Render volumes in this Layer (default True)

**Type:**

bool

<a id="bpy.types.ViewLayer.world_override"></a>

#### bpy.types.ViewLayer.world_override

Override world in this view layer

**Type:**

[`World`](bpy.types.World.md#bpy.types.World "bpy.types.World") | None

<a id="bpy.types.ViewLayer.bl_system_properties_get"></a>

#### bpy.types.ViewLayer.bl_system_properties_get(*, do_create=False)

DEBUG ONLY. Internal access to runtime-defined RNA data storage, intended solely for testing and debugging purposes. Do not access it in regular scripting work, and in particular, do not assume that it contains writable data

**Parameters:**

**do_create** (bool) – Ensure that system properties are created if they do not exist yet (optional)

**Returns:**

The system properties root container, or None if there are no system properties stored in this data yet, and its creation was not requested

**Return type:**

[`PropertyGroup`](bpy.types.PropertyGroup.md#bpy.types.PropertyGroup "bpy.types.PropertyGroup")

<a id="bpy.types.ViewLayer.update_render_passes"></a>

#### classmethod bpy.types.ViewLayer.update_render_passes()

Requery the enabled render passes from the render engine

<a id="bpy.types.ViewLayer.update"></a>

#### bpy.types.ViewLayer.update()

Update data tagged to be updated from previous access to data or operators

<a id="bpy.types.ViewLayer.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ViewLayer.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ViewLayer.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ViewLayer.bl_rna_get_subclass_py(id, default=None, /)

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
| - `bpy.context.view_layer` - [`Context.view_layer`](bpy.types.Context.md#bpy.types.Context.view_layer "bpy.types.Context.view_layer") - [`Depsgraph.view_layer`](bpy.types.Depsgraph.md#bpy.types.Depsgraph.view_layer "bpy.types.Depsgraph.view_layer") - [`Depsgraph.view_layer_eval`](bpy.types.Depsgraph.md#bpy.types.Depsgraph.view_layer_eval "bpy.types.Depsgraph.view_layer_eval") - [`ID.override_hierarchy_create`](bpy.types.ID.md#bpy.types.ID.override_hierarchy_create "bpy.types.ID.override_hierarchy_create") - [`IDOverrideLibrary.resync`](bpy.types.IDOverrideLibrary.md#bpy.types.IDOverrideLibrary.resync "bpy.types.IDOverrideLibrary.resync") - [`LayerCollection.has_selected_objects`](bpy.types.LayerCollection.md#bpy.types.LayerCollection.has_selected_objects "bpy.types.LayerCollection.has_selected_objects") - [`Object.hide_get`](bpy.types.Object.md#bpy.types.Object.hide_get "bpy.types.Object.hide_get") - [`Object.hide_set`](bpy.types.Object.md#bpy.types.Object.hide_set "bpy.types.Object.hide_set") - [`Object.holdout_get`](bpy.types.Object.md#bpy.types.Object.holdout_get "bpy.types.Object.holdout_get") - [`Object.indirect_only_get`](bpy.types.Object.md#bpy.types.Object.indirect_only_get "bpy.types.Object.indirect_only_get") | - [`Object.select_get`](bpy.types.Object.md#bpy.types.Object.select_get "bpy.types.Object.select_get") - [`Object.select_set`](bpy.types.Object.md#bpy.types.Object.select_set "bpy.types.Object.select_set") - [`Object.visible_get`](bpy.types.Object.md#bpy.types.Object.visible_get "bpy.types.Object.visible_get") - [`RenderEngine.register_pass`](bpy.types.RenderEngine.md#bpy.types.RenderEngine.register_pass "bpy.types.RenderEngine.register_pass") - [`RenderEngine.update_render_passes`](bpy.types.RenderEngine.md#bpy.types.RenderEngine.update_render_passes "bpy.types.RenderEngine.update_render_passes") - [`Scene.statistics`](bpy.types.Scene.md#bpy.types.Scene.statistics "bpy.types.Scene.statistics") - [`Scene.view_layers`](bpy.types.Scene.md#bpy.types.Scene.view_layers "bpy.types.Scene.view_layers") - [`SceneStrip.view_layer`](bpy.types.SceneStrip.md#bpy.types.SceneStrip.view_layer "bpy.types.SceneStrip.view_layer") - [`ViewLayers.new`](bpy.types.ViewLayers.md#bpy.types.ViewLayers.new "bpy.types.ViewLayers.new") - [`ViewLayers.remove`](bpy.types.ViewLayers.md#bpy.types.ViewLayers.remove "bpy.types.ViewLayers.remove") - [`Window.view_layer`](bpy.types.Window.md#bpy.types.Window.view_layer "bpy.types.Window.view_layer") |
