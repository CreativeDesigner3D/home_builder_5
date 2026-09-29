<!-- source: Blender Python API reference 5.2 / bpy.types.View3DShading.html -->

<a id="view3dshading-bpy-struct"></a>

# View3DShading(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.View3DShading"></a>

### class bpy.types.View3DShading(bpy_struct)

Settings for shading in the 3D viewport

<a id="bpy.types.View3DShading.aov_name"></a>

#### bpy.types.View3DShading.aov_name

Name of the active Shader AOV (default “”, never None)

**Type:**

str

<a id="bpy.types.View3DShading.background_color"></a>

#### bpy.types.View3DShading.background_color

Color for custom background color (array of 3 items, in [0, 1], default (0.05, 0.05, 0.05))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.View3DShading.background_type"></a>

#### bpy.types.View3DShading.background_type

Way to display the background (default `'THEME'`)

- `THEME`
  Theme – Use the theme for background color.
- `WORLD`
  World – Use the world for background color.
- `VIEWPORT`
  Custom – Use a custom color limited to this viewport only.

**Type:**

Literal[‘THEME’, ‘WORLD’, ‘VIEWPORT’]

<a id="bpy.types.View3DShading.cavity_ridge_factor"></a>

#### bpy.types.View3DShading.cavity_ridge_factor

Factor for the cavity ridges (in [0, 250], default 1.0)

**Type:**

float

<a id="bpy.types.View3DShading.cavity_type"></a>

#### bpy.types.View3DShading.cavity_type

Way to display the cavity shading (default `'SCREEN'`)

- `WORLD`
  World – Cavity shading computed in world space, useful for larger-scale occlusion.
- `SCREEN`
  Screen – Curvature-based shading, useful for making fine details more visible.
- `BOTH`
  Both – Use both effects simultaneously.

**Type:**

Literal[‘WORLD’, ‘SCREEN’, ‘BOTH’]

<a id="bpy.types.View3DShading.cavity_valley_factor"></a>

#### bpy.types.View3DShading.cavity_valley_factor

Factor for the cavity valleys (in [0, 250], default 1.0)

**Type:**

float

<a id="bpy.types.View3DShading.color_type"></a>

#### bpy.types.View3DShading.color_type

Color Type (default `'MATERIAL'`)

- `MATERIAL`
  Material – Show material color.
- `OBJECT`
  Object – Show object color.
- `RANDOM`
  Random – Show random object color.
- `VERTEX`
  Attribute – Show active color attribute.
- `TEXTURE`
  Texture – Show the texture from the active image texture node using the active UV map coordinates.
- `SINGLE`
  Custom – Show scene in a single custom color.

**Type:**

Literal[‘MATERIAL’, ‘OBJECT’, ‘RANDOM’, ‘VERTEX’, ‘TEXTURE’, ‘SINGLE’]

<a id="bpy.types.View3DShading.curvature_ridge_factor"></a>

#### bpy.types.View3DShading.curvature_ridge_factor

Factor for the curvature ridges (in [0, 2], default 1.0)

**Type:**

float

<a id="bpy.types.View3DShading.curvature_valley_factor"></a>

#### bpy.types.View3DShading.curvature_valley_factor

Factor for the curvature valleys (in [0, 2], default 1.0)

**Type:**

float

<a id="bpy.types.View3DShading.cycles"></a>

#### bpy.types.View3DShading.cycles

(readonly)

**Type:**

`CyclesView3DShadingSettings` | None

<a id="bpy.types.View3DShading.light"></a>

#### bpy.types.View3DShading.light

Lighting Method for Solid/Texture Viewport Shading (default `'STUDIO'`)

- `STUDIO`
  Studio – Display using studio lighting.
- `MATCAP`
  MatCap – Display using matcap material and lighting.
- `FLAT`
  Flat – Display using flat lighting.

**Type:**

Literal[‘STUDIO’, ‘MATCAP’, ‘FLAT’]

<a id="bpy.types.View3DShading.object_outline_color"></a>

#### bpy.types.View3DShading.object_outline_color

Color for object outline (array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.View3DShading.render_pass"></a>

#### bpy.types.View3DShading.render_pass

Render Pass to show in the viewport (default `'COMBINED'`)

**Type:**

Literal[‘COMBINED’, ‘EMISSION’, ‘ENVIRONMENT’, ‘AO’, ‘SHADOW’, ‘TRANSPARENT’, ‘DIFFUSE_LIGHT’, ‘DIFFUSE_COLOR’, ‘SPECULAR_LIGHT’, ‘SPECULAR_COLOR’, ‘VOLUME_LIGHT’, ‘POSITION’, ‘NORMAL’, ‘MIST’, ‘CryptoObject’, ‘CryptoAsset’, ‘CryptoMaterial’, ‘AOV’]

<a id="bpy.types.View3DShading.selected_studio_light"></a>

#### bpy.types.View3DShading.selected_studio_light

Selected StudioLight (readonly)

**Type:**

[`StudioLight`](bpy.types.StudioLight.md#bpy.types.StudioLight "bpy.types.StudioLight") | None

<a id="bpy.types.View3DShading.shadow_intensity"></a>

#### bpy.types.View3DShading.shadow_intensity

Darkness of shadows (in [0, 1], default 0.5)

**Type:**

float

<a id="bpy.types.View3DShading.show_backface_culling"></a>

#### bpy.types.View3DShading.show_backface_culling

Use back face culling to hide the back side of faces (default False)

**Type:**

bool

<a id="bpy.types.View3DShading.show_cavity"></a>

#### bpy.types.View3DShading.show_cavity

Show Cavity (default False)

**Type:**

bool

<a id="bpy.types.View3DShading.show_object_outline"></a>

#### bpy.types.View3DShading.show_object_outline

Show Object Outline (default False)

**Type:**

bool

<a id="bpy.types.View3DShading.show_shadows"></a>

#### bpy.types.View3DShading.show_shadows

Show Shadow (default False)

**Type:**

bool

<a id="bpy.types.View3DShading.show_specular_highlight"></a>

#### bpy.types.View3DShading.show_specular_highlight

Render specular highlights (default True)

**Type:**

bool

<a id="bpy.types.View3DShading.show_xray"></a>

#### bpy.types.View3DShading.show_xray

Show whole scene transparent (default False)

**Type:**

bool

<a id="bpy.types.View3DShading.show_xray_wireframe"></a>

#### bpy.types.View3DShading.show_xray_wireframe

Show whole scene transparent (default True)

**Type:**

bool

<a id="bpy.types.View3DShading.single_color"></a>

#### bpy.types.View3DShading.single_color

Color for single color mode (array of 3 items, in [0, 1], default (0.8, 0.8, 0.8))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.View3DShading.studio_light"></a>

#### bpy.types.View3DShading.studio_light

Studio lighting setup (default `'DEFAULT'`)

**Type:**

Literal[‘DEFAULT’]

<a id="bpy.types.View3DShading.studiolight_background_alpha"></a>

#### bpy.types.View3DShading.studiolight_background_alpha

Show the studiolight in the background (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.View3DShading.studiolight_background_blur"></a>

#### bpy.types.View3DShading.studiolight_background_blur

Blur the studiolight in the background (in [0, 1], default 0.5)

**Type:**

float

<a id="bpy.types.View3DShading.studiolight_intensity"></a>

#### bpy.types.View3DShading.studiolight_intensity

Strength of the studiolight (in [0, inf], default 1.0)

**Type:**

float

<a id="bpy.types.View3DShading.studiolight_rotate_z"></a>

#### bpy.types.View3DShading.studiolight_rotate_z

Rotation of the studiolight around the Z-Axis (in [-3.14159, 3.14159], default 0.0)

**Type:**

float

<a id="bpy.types.View3DShading.type"></a>

#### bpy.types.View3DShading.type

Method to display/shade objects in the 3D View (default `'SOLID'`)

**Type:**

Literal[[Shading Type Items](bpy_types_enum_items/shading_type_items.md#rna-enum-shading-type-items)]

<a id="bpy.types.View3DShading.use_compositor"></a>

#### bpy.types.View3DShading.use_compositor

When to preview the compositor output inside the viewport (default `'DISABLED'`)

- `DISABLED`
  Disabled – The compositor is disabled.
- `CAMERA`
  Camera – The compositor is enabled only in camera view.
- `ALWAYS`
  Always – The compositor is always enabled regardless of the view.

**Type:**

Literal[‘DISABLED’, ‘CAMERA’, ‘ALWAYS’]

<a id="bpy.types.View3DShading.use_dof"></a>

#### bpy.types.View3DShading.use_dof

Use depth of field on viewport using the values from the active camera (default False)

**Type:**

bool

<a id="bpy.types.View3DShading.use_scene_lights"></a>

#### bpy.types.View3DShading.use_scene_lights

Render lights and light probes of the scene (default False)

**Type:**

bool

<a id="bpy.types.View3DShading.use_scene_lights_render"></a>

#### bpy.types.View3DShading.use_scene_lights_render

Render lights and light probes of the scene (default True)

**Type:**

bool

<a id="bpy.types.View3DShading.use_scene_world"></a>

#### bpy.types.View3DShading.use_scene_world

Use scene world for lighting (default False)

**Type:**

bool

<a id="bpy.types.View3DShading.use_scene_world_render"></a>

#### bpy.types.View3DShading.use_scene_world_render

Use scene world for lighting (default True)

**Type:**

bool

<a id="bpy.types.View3DShading.use_studiolight_view_rotation"></a>

#### bpy.types.View3DShading.use_studiolight_view_rotation

Make the HDR rotation fixed and not follow the camera (default True)

**Type:**

bool

<a id="bpy.types.View3DShading.use_world_space_lighting"></a>

#### bpy.types.View3DShading.use_world_space_lighting

Make the lighting fixed and not follow the camera (default False)

**Type:**

bool

<a id="bpy.types.View3DShading.wireframe_color_type"></a>

#### bpy.types.View3DShading.wireframe_color_type

Wire Color Type (default `'THEME'`)

- `THEME`
  Theme – Show scene wireframes with the theme’s wire color.
- `OBJECT`
  Object – Show object color on wireframe.
- `RANDOM`
  Random – Show random object color on wireframe.

**Type:**

Literal[‘THEME’, ‘OBJECT’, ‘RANDOM’]

<a id="bpy.types.View3DShading.xray_alpha"></a>

#### bpy.types.View3DShading.xray_alpha

Amount of opacity to use (in [0, 1], default 0.5)

**Type:**

float

<a id="bpy.types.View3DShading.xray_alpha_wireframe"></a>

#### bpy.types.View3DShading.xray_alpha_wireframe

Amount of opacity to use (in [0, 1], default 0.5)

**Type:**

float

<a id="bpy.types.View3DShading.bl_system_properties_get"></a>

#### bpy.types.View3DShading.bl_system_properties_get(*, do_create=False)

DEBUG ONLY. Internal access to runtime-defined RNA data storage, intended solely for testing and debugging purposes. Do not access it in regular scripting work, and in particular, do not assume that it contains writable data

**Parameters:**

**do_create** (bool) – Ensure that system properties are created if they do not exist yet (optional)

**Returns:**

The system properties root container, or None if there are no system properties stored in this data yet, and its creation was not requested

**Return type:**

[`PropertyGroup`](bpy.types.PropertyGroup.md#bpy.types.PropertyGroup "bpy.types.PropertyGroup")

<a id="bpy.types.View3DShading.bl_rna_get_subclass"></a>

#### classmethod bpy.types.View3DShading.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.View3DShading.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.View3DShading.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([type](#bpy.types.View3DShading.type "bpy.types.View3DShading.type") | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

[type](#bpy.types.View3DShading.type "bpy.types.View3DShading.type")

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
| - [`SceneDisplay.shading`](bpy.types.SceneDisplay.md#bpy.types.SceneDisplay.shading "bpy.types.SceneDisplay.shading") - [`SpaceView3D.shading`](bpy.types.SpaceView3D.md#bpy.types.SpaceView3D.shading "bpy.types.SpaceView3D.shading") | - [`XrSessionSettings.shading`](bpy.types.XrSessionSettings.md#bpy.types.XrSessionSettings.shading "bpy.types.XrSessionSettings.shading") |
