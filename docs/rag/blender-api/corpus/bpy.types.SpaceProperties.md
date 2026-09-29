<!-- source: Blender Python API reference 5.2 / bpy.types.SpaceProperties.html -->

<a id="spaceproperties-space"></a>

# SpaceProperties(Space)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Space`](bpy.types.Space.md#bpy.types.Space "bpy.types.Space")

<a id="bpy.types.SpaceProperties"></a>

### class bpy.types.SpaceProperties(Space)

Properties space data

<a id="bpy.types.SpaceProperties.context"></a>

#### bpy.types.SpaceProperties.context

(default `'RENDER'`)

- `TOOL`
  Tool – Active Tool and Workspace settings.
- `SCENE`
  Scene – Scene Properties.
- `RENDER`
  Render – Render Properties.
- `OUTPUT`
  Output – Output Properties.
- `VIEW_LAYER`
  View Layer – View Layer Properties.
- `WORLD`
  World – World Properties.
- `COLLECTION`
  Collection – Collection Properties.
- `OBJECT`
  Object – Object Properties.
- `CONSTRAINT`
  Constraints – Object Constraint Properties.
- `MODIFIER`
  Modifiers – Modifier Properties.
- `DATA`
  Data – Object Data Properties.
- `BONE`
  Bone – Bone Properties.
- `BONE_CONSTRAINT`
  Bone Constraints – Bone Constraint Properties.
- `MATERIAL`
  Material – Material Properties.
- `TEXTURE`
  Texture – Texture Properties.
- `PARTICLES`
  Particles – Particle Properties.
- `PHYSICS`
  Physics – Physics Properties.
- `SHADERFX`
  Effects – Visual Effects Properties.
- `STRIP`
  Strip – Strip Properties.
- `STRIP_MODIFIER`
  Strip Modifiers – Strip Modifier Properties.

**Type:**

Literal[‘TOOL’, ‘SCENE’, ‘RENDER’, ‘OUTPUT’, ‘VIEW_LAYER’, ‘WORLD’, ‘COLLECTION’, ‘OBJECT’, ‘CONSTRAINT’, ‘MODIFIER’, ‘DATA’, ‘BONE’, ‘BONE_CONSTRAINT’, ‘MATERIAL’, ‘TEXTURE’, ‘PARTICLES’, ‘PHYSICS’, ‘SHADERFX’, ‘STRIP’, ‘STRIP_MODIFIER’]

<a id="bpy.types.SpaceProperties.outliner_sync"></a>

#### bpy.types.SpaceProperties.outliner_sync

Change to the corresponding tab when outliner data icons are clicked (default `'AUTO'`)

- `ALWAYS`
  Always – Always change tabs when clicking an icon in an outliner.
- `NEVER`
  Never – Never change tabs when clicking an icon in an outliner.
- `AUTO`
  Auto – Change tabs only when this editor shares a border with an outliner.

**Type:**

Literal[‘ALWAYS’, ‘NEVER’, ‘AUTO’]

<a id="bpy.types.SpaceProperties.pin_id"></a>

#### bpy.types.SpaceProperties.pin_id

**Type:**

[`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID") | None

<a id="bpy.types.SpaceProperties.search_filter"></a>

#### bpy.types.SpaceProperties.search_filter

Live search filtering string (default “”, never None)

**Type:**

str

<a id="bpy.types.SpaceProperties.show_properties_bone"></a>

#### bpy.types.SpaceProperties.show_properties_bone

(default False)

**Type:**

bool

<a id="bpy.types.SpaceProperties.show_properties_bone_constraints"></a>

#### bpy.types.SpaceProperties.show_properties_bone_constraints

(default False)

**Type:**

bool

<a id="bpy.types.SpaceProperties.show_properties_collection"></a>

#### bpy.types.SpaceProperties.show_properties_collection

(default False)

**Type:**

bool

<a id="bpy.types.SpaceProperties.show_properties_constraints"></a>

#### bpy.types.SpaceProperties.show_properties_constraints

(default False)

**Type:**

bool

<a id="bpy.types.SpaceProperties.show_properties_data"></a>

#### bpy.types.SpaceProperties.show_properties_data

(default False)

**Type:**

bool

<a id="bpy.types.SpaceProperties.show_properties_effects"></a>

#### bpy.types.SpaceProperties.show_properties_effects

(default False)

**Type:**

bool

<a id="bpy.types.SpaceProperties.show_properties_material"></a>

#### bpy.types.SpaceProperties.show_properties_material

(default False)

**Type:**

bool

<a id="bpy.types.SpaceProperties.show_properties_modifiers"></a>

#### bpy.types.SpaceProperties.show_properties_modifiers

(default False)

**Type:**

bool

<a id="bpy.types.SpaceProperties.show_properties_object"></a>

#### bpy.types.SpaceProperties.show_properties_object

(default False)

**Type:**

bool

<a id="bpy.types.SpaceProperties.show_properties_output"></a>

#### bpy.types.SpaceProperties.show_properties_output

(default False)

**Type:**

bool

<a id="bpy.types.SpaceProperties.show_properties_particles"></a>

#### bpy.types.SpaceProperties.show_properties_particles

(default False)

**Type:**

bool

<a id="bpy.types.SpaceProperties.show_properties_physics"></a>

#### bpy.types.SpaceProperties.show_properties_physics

(default False)

**Type:**

bool

<a id="bpy.types.SpaceProperties.show_properties_render"></a>

#### bpy.types.SpaceProperties.show_properties_render

(default False)

**Type:**

bool

<a id="bpy.types.SpaceProperties.show_properties_scene"></a>

#### bpy.types.SpaceProperties.show_properties_scene

(default False)

**Type:**

bool

<a id="bpy.types.SpaceProperties.show_properties_strip"></a>

#### bpy.types.SpaceProperties.show_properties_strip

(default False)

**Type:**

bool

<a id="bpy.types.SpaceProperties.show_properties_strip_modifier"></a>

#### bpy.types.SpaceProperties.show_properties_strip_modifier

(default False)

**Type:**

bool

<a id="bpy.types.SpaceProperties.show_properties_texture"></a>

#### bpy.types.SpaceProperties.show_properties_texture

(default False)

**Type:**

bool

<a id="bpy.types.SpaceProperties.show_properties_tool"></a>

#### bpy.types.SpaceProperties.show_properties_tool

(default False)

**Type:**

bool

<a id="bpy.types.SpaceProperties.show_properties_view_layer"></a>

#### bpy.types.SpaceProperties.show_properties_view_layer

(default False)

**Type:**

bool

<a id="bpy.types.SpaceProperties.show_properties_world"></a>

#### bpy.types.SpaceProperties.show_properties_world

(default False)

**Type:**

bool

<a id="bpy.types.SpaceProperties.tab_search_results"></a>

#### bpy.types.SpaceProperties.tab_search_results

Whether or not each visible tab has a search result (dynamic array, default False, readonly)

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[bool]

<a id="bpy.types.SpaceProperties.use_pin_id"></a>

#### bpy.types.SpaceProperties.use_pin_id

Use the pinned context (default False)

**Type:**

bool

<a id="bpy.types.SpaceProperties.bl_rna_get_subclass"></a>

#### classmethod bpy.types.SpaceProperties.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.SpaceProperties.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.SpaceProperties.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="bpy.types.SpaceProperties.draw_handler_add"></a>

#### classmethod bpy.types.SpaceProperties.draw_handler_add(callback, args, region_type, draw_type)

Add a new draw handler to this space type.
It will be called every time the specified region in the space type will be drawn.
Note: All arguments are positional only for now.

**Parameters:**

- **callback** (Callable[..., Any]) – A function that will be called when the region is drawn.
  It gets the specified arguments as input, it’s return value is ignored.
- **args** (tuple[Any, ...]) – Arguments that will be passed to the callback.
- **region_type** (str) – The region type the callback draws in; usually `WINDOW`. ([`bpy.types.Region.type`](bpy.types.Region.md#bpy.types.Region.type "bpy.types.Region.type"))
- **draw_type** (str) – Usually `POST_PIXEL` for 2D drawing and `POST_VIEW` for 3D drawing. In some cases `PRE_VIEW` can be used. `BACKDROP` can be used for backdrops in the node editor.

**Returns:**

Handler that can be removed later on.

**Return type:**

object

<a id="bpy.types.SpaceProperties.draw_handler_remove"></a>

#### classmethod bpy.types.SpaceProperties.draw_handler_remove(handler, region_type)

Remove a draw handler that was added previously.

**Parameters:**

- **handler** (object) – The draw handler that should be removed.
- **region_type** (str) – Region type the callback was added to.

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, Space.type, Space.show_locked_time, Space.show_region_header

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, Space.bl_rna_get_subclass, Space.bl_rna_get_subclass_py, Space.draw_handler_add, Space.draw_handler_remove
