<!-- source: Blender Python API reference 5.2 / bpy.types.SpaceNodeEditor.html -->

<a id="spacenodeeditor-space"></a>

# SpaceNodeEditor(Space)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Space`](bpy.types.Space.md#bpy.types.Space "bpy.types.Space")

<a id="bpy.types.SpaceNodeEditor"></a>

### class bpy.types.SpaceNodeEditor(Space)

Node editor space data

<a id="bpy.types.SpaceNodeEditor.backdrop_channels"></a>

#### bpy.types.SpaceNodeEditor.backdrop_channels

Channels of the image to draw (default `'COLOR'`)

- `COLOR_ALPHA`
  Color & Alpha – Display image with RGB colors and alpha transparency.
- `COLOR`
  Color – Display image with RGB colors.
- `ALPHA`
  Alpha – Display alpha transparency channel.
- `RED`
  Red.
- `GREEN`
  Green.
- `BLUE`
  Blue.

**Type:**

Literal[‘COLOR_ALPHA’, ‘COLOR’, ‘ALPHA’, ‘RED’, ‘GREEN’, ‘BLUE’]

<a id="bpy.types.SpaceNodeEditor.backdrop_offset"></a>

#### bpy.types.SpaceNodeEditor.backdrop_offset

Backdrop offset (array of 2 items, in [-inf, inf], default (0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.SpaceNodeEditor.backdrop_zoom"></a>

#### bpy.types.SpaceNodeEditor.backdrop_zoom

Backdrop zoom factor (in [0.01, inf], default 1.0)

**Type:**

float

<a id="bpy.types.SpaceNodeEditor.cursor_location"></a>

#### bpy.types.SpaceNodeEditor.cursor_location

Location for adding new nodes (array of 2 items, in [-inf, inf], default (0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.SpaceNodeEditor.edit_tree"></a>

#### bpy.types.SpaceNodeEditor.edit_tree

Node tree being displayed and edited (readonly)

**Type:**

[`NodeTree`](bpy.types.NodeTree.md#bpy.types.NodeTree "bpy.types.NodeTree") | None

<a id="bpy.types.SpaceNodeEditor.id"></a>

#### bpy.types.SpaceNodeEditor.id

Data-block whose nodes are being edited (readonly)

**Type:**

[`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID") | None

<a id="bpy.types.SpaceNodeEditor.id_from"></a>

#### bpy.types.SpaceNodeEditor.id_from

Data-block from which the edited data-block is linked (readonly)

**Type:**

[`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID") | None

<a id="bpy.types.SpaceNodeEditor.insert_offset_direction"></a>

#### bpy.types.SpaceNodeEditor.insert_offset_direction

Direction to offset nodes on insertion (default `'RIGHT'`)

**Type:**

Literal[‘RIGHT’, ‘LEFT’]

<a id="bpy.types.SpaceNodeEditor.node_tree"></a>

#### bpy.types.SpaceNodeEditor.node_tree

Base node tree from context

**Type:**

[`NodeTree`](bpy.types.NodeTree.md#bpy.types.NodeTree "bpy.types.NodeTree") | None

<a id="bpy.types.SpaceNodeEditor.node_tree_sub_type"></a>

#### bpy.types.SpaceNodeEditor.node_tree_sub_type

**Type:**

str

<a id="bpy.types.SpaceNodeEditor.overlay"></a>

#### bpy.types.SpaceNodeEditor.overlay

Settings for display of overlays in the Node Editor (readonly, never None)

**Type:**

[`SpaceNodeOverlay`](bpy.types.SpaceNodeOverlay.md#bpy.types.SpaceNodeOverlay "bpy.types.SpaceNodeOverlay")

<a id="bpy.types.SpaceNodeEditor.path"></a>

#### bpy.types.SpaceNodeEditor.path

Path from the data-block to the currently edited node tree (default None, readonly)

**Type:**

[`SpaceNodeEditorPath`](bpy.types.SpaceNodeEditorPath.md#bpy.types.SpaceNodeEditorPath "bpy.types.SpaceNodeEditorPath")[[`NodeTreePath`](bpy.types.NodeTreePath.md#bpy.types.NodeTreePath "bpy.types.NodeTreePath")]

<a id="bpy.types.SpaceNodeEditor.pin"></a>

#### bpy.types.SpaceNodeEditor.pin

Use the pinned node tree (default False)

**Type:**

bool

<a id="bpy.types.SpaceNodeEditor.selected_node_group"></a>

#### bpy.types.SpaceNodeEditor.selected_node_group

Node group to edit

**Type:**

[`NodeTree`](bpy.types.NodeTree.md#bpy.types.NodeTree "bpy.types.NodeTree") | None

<a id="bpy.types.SpaceNodeEditor.shader_type"></a>

#### bpy.types.SpaceNodeEditor.shader_type

Type of data to take shader from (default `'OBJECT'`)

- `OBJECT`
  Object – Edit shader nodes from Object.
- `WORLD`
  World – Edit shader nodes from World.
- `LINESTYLE`
  Line Style – Edit shader nodes from Line Style.

**Type:**

Literal[‘OBJECT’, ‘WORLD’, ‘LINESTYLE’]

<a id="bpy.types.SpaceNodeEditor.show_annotation"></a>

#### bpy.types.SpaceNodeEditor.show_annotation

Show annotations for this view (default False)

**Type:**

bool

<a id="bpy.types.SpaceNodeEditor.show_backdrop"></a>

#### bpy.types.SpaceNodeEditor.show_backdrop

Use active Viewer Node output as backdrop for compositing nodes (default False)

**Type:**

bool

<a id="bpy.types.SpaceNodeEditor.show_gizmo"></a>

#### bpy.types.SpaceNodeEditor.show_gizmo

Show gizmos of all types (default True)

**Type:**

bool

<a id="bpy.types.SpaceNodeEditor.show_gizmo_active_node"></a>

#### bpy.types.SpaceNodeEditor.show_gizmo_active_node

Context sensitive gizmo for the active node (default True)

**Type:**

bool

<a id="bpy.types.SpaceNodeEditor.show_region_asset_shelf"></a>

#### bpy.types.SpaceNodeEditor.show_region_asset_shelf

Display a region with assets that may currently be relevant (such as brushes in paint modes, or poses in Pose Mode) (default False)

**Type:**

bool

<a id="bpy.types.SpaceNodeEditor.show_region_toolbar"></a>

#### bpy.types.SpaceNodeEditor.show_region_toolbar

(default False)

**Type:**

bool

<a id="bpy.types.SpaceNodeEditor.show_region_ui"></a>

#### bpy.types.SpaceNodeEditor.show_region_ui

(default False)

**Type:**

bool

<a id="bpy.types.SpaceNodeEditor.supports_previews"></a>

#### bpy.types.SpaceNodeEditor.supports_previews

Whether the node editor’s type supports displaying node previews (default False, readonly)

**Type:**

bool

<a id="bpy.types.SpaceNodeEditor.texture_type"></a>

#### bpy.types.SpaceNodeEditor.texture_type

Type of data to take texture from (default `'WORLD'`)

- `WORLD`
  World – Edit texture nodes from World.
- `BRUSH`
  Brush – Edit texture nodes from Brush.
- `LINESTYLE`
  Line Style – Edit texture nodes from Line Style.

**Type:**

Literal[‘WORLD’, ‘BRUSH’, ‘LINESTYLE’]

<a id="bpy.types.SpaceNodeEditor.tree_type"></a>

#### bpy.types.SpaceNodeEditor.tree_type

Node tree type to display and edit (default `'DEFAULT'`)

- `GeometryNodeTree`
  Geometry Node Editor – Advanced geometry editing and tools creation using nodes.
- `CompositorNodeTree`
  Compositor – Create effects and post-process renders, images, and the 3D Viewport.
- `ShaderNodeTree`
  Shader Editor – Edit materials, lights, and world shading using nodes.
- `TextureNodeTree`
  Texture Node Editor – Edit textures using nodes.

**Type:**

Literal[‘GeometryNodeTree’, ‘CompositorNodeTree’, ‘ShaderNodeTree’, ‘TextureNodeTree’]

<a id="bpy.types.SpaceNodeEditor.cursor_location_from_region"></a>

#### bpy.types.SpaceNodeEditor.cursor_location_from_region(x, y)

Set the cursor location using region coordinates

**Parameters:**

- **x** (int) – x, Region x coordinate (in [-inf, inf])
- **y** (int) – y, Region y coordinate (in [-inf, inf])

<a id="bpy.types.SpaceNodeEditor.bl_rna_get_subclass"></a>

#### classmethod bpy.types.SpaceNodeEditor.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.SpaceNodeEditor.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.SpaceNodeEditor.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="bpy.types.SpaceNodeEditor.draw_handler_add"></a>

#### classmethod bpy.types.SpaceNodeEditor.draw_handler_add(callback, args, region_type, draw_type)

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

<a id="bpy.types.SpaceNodeEditor.draw_handler_remove"></a>

#### classmethod bpy.types.SpaceNodeEditor.draw_handler_remove(handler, region_type)

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
