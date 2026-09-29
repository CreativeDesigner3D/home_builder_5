<!-- source: Blender Python API reference 5.2 / bpy.types.Node.html -->

<a id="node-bpy-struct"></a>

# Node(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

Subclasses

- [NodeCustomGroup(Node)](bpy.types.NodeCustomGroup.md)
- [NodeInternal(Node)](bpy.types.NodeInternal.md)

<a id="bpy.types.Node"></a>

### class bpy.types.Node(bpy_struct)

Node in a node tree

<a id="bpy.types.Node.bl_description"></a>

#### bpy.types.Node.bl_description

(default “”, never None)

**Type:**

str

<a id="bpy.types.Node.bl_height_default"></a>

#### bpy.types.Node.bl_height_default

Default height of the node when it is created (mostly unused, see Height) (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.Node.bl_height_max"></a>

#### bpy.types.Node.bl_height_max

When changing the node’s size, it can have at most this height (mostly unused, see Height) (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.Node.bl_height_min"></a>

#### bpy.types.Node.bl_height_min

When changing the node’s size, it has at least this height (mostly unused, see Height) (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.Node.bl_icon"></a>

#### bpy.types.Node.bl_icon

The node icon (default `'NODE'`)

**Type:**

Literal[[Icon Items](bpy_types_enum_items/icon_items.md#rna-enum-icon-items)]

<a id="bpy.types.Node.bl_idname"></a>

#### bpy.types.Node.bl_idname

(default “”, never None)

**Type:**

str

<a id="bpy.types.Node.bl_label"></a>

#### bpy.types.Node.bl_label

The node label (default “”, never None)

**Type:**

str

<a id="bpy.types.Node.bl_static_type"></a>

#### bpy.types.Node.bl_static_type

Legacy unique node type identifier, redundant with bl_idname property (default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.Node.bl_width_default"></a>

#### bpy.types.Node.bl_width_default

Default width of the node when it is created (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.Node.bl_width_max"></a>

#### bpy.types.Node.bl_width_max

When changing the node’s size, it can have at most this width (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.Node.bl_width_min"></a>

#### bpy.types.Node.bl_width_min

When changing the node’s size, it has at least this width (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.Node.color"></a>

#### bpy.types.Node.color

Custom color of the node body (array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.Node.color_tag"></a>

#### bpy.types.Node.color_tag

Node header color tag (default `'NONE'`, readonly)

- `NONE`
  None – Default color tag for new nodes and node groups.
- `ATTRIBUTE`
  Attribute.
- `COLOR`
  Color.
- `CONVERTER`
  Converter.
- `DISTORT`
  Distort.
- `FILTER`
  Filter.
- `GEOMETRY`
  Geometry.
- `INPUT`
  Input.
- `MATTE`
  Matte.
- `OUTPUT`
  Output.
- `SCRIPT`
  Script.
- `SHADER`
  Shader.
- `TEXTURE`
  Texture.
- `VECTOR`
  Vector.
- `PATTERN`
  Pattern.
- `INTERFACE`
  Interface.
- `GROUP`
  Group.

**Type:**

Literal[‘NONE’, ‘ATTRIBUTE’, ‘COLOR’, ‘CONVERTER’, ‘DISTORT’, ‘FILTER’, ‘GEOMETRY’, ‘INPUT’, ‘MATTE’, ‘OUTPUT’, ‘SCRIPT’, ‘SHADER’, ‘TEXTURE’, ‘VECTOR’, ‘PATTERN’, ‘INTERFACE’, ‘GROUP’]

<a id="bpy.types.Node.dimensions"></a>

#### bpy.types.Node.dimensions

Absolute bounding box dimensions of the node after it was displayed (array of 2 items, in [-inf, inf], default (0.0, 0.0), readonly)

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.Node.height"></a>

#### bpy.types.Node.height

Height of the node. This property holds true data only under certain circumstances, e.g. for a Frame node after the node graph was displayed. For most types of nodes, the displayed height is based on the node’s contents and not reflected in this property. (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.Node.hide"></a>

#### bpy.types.Node.hide

Node collapsed state (default False)

**Type:**

bool

<a id="bpy.types.Node.inputs"></a>

#### bpy.types.Node.inputs

(default None, readonly)

**Type:**

[`NodeInputs`](bpy.types.NodeInputs.md#bpy.types.NodeInputs "bpy.types.NodeInputs")[[`NodeSocket`](bpy.types.NodeSocket.md#bpy.types.NodeSocket "bpy.types.NodeSocket")]

<a id="bpy.types.Node.internal_links"></a>

#### bpy.types.Node.internal_links

Internal input-to-output connections for muting (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`NodeLink`](bpy.types.NodeLink.md#bpy.types.NodeLink "bpy.types.NodeLink")]

<a id="bpy.types.Node.label"></a>

#### bpy.types.Node.label

Optional custom node label (default “”, never None)

**Type:**

str

<a id="bpy.types.Node.location"></a>

#### bpy.types.Node.location

Location of the node within its parent frame (array of 2 items, in [-1e+06, 1e+06], default (0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.Node.location_absolute"></a>

#### bpy.types.Node.location_absolute

Location of the node in the entire canvas (array of 2 items, in [-1e+06, 1e+06], default (0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.Node.mute"></a>

#### bpy.types.Node.mute

(default False)

**Type:**

bool

<a id="bpy.types.Node.name"></a>

#### bpy.types.Node.name

Unique node identifier (default “”, never None)

**Type:**

str

<a id="bpy.types.Node.outputs"></a>

#### bpy.types.Node.outputs

(default None, readonly)

**Type:**

[`NodeOutputs`](bpy.types.NodeOutputs.md#bpy.types.NodeOutputs "bpy.types.NodeOutputs")[[`NodeSocket`](bpy.types.NodeSocket.md#bpy.types.NodeSocket "bpy.types.NodeSocket")]

<a id="bpy.types.Node.panel_states"></a>

#### bpy.types.Node.panel_states

Expansion state of each panel in the node (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`NodePanelState`](bpy.types.NodePanelState.md#bpy.types.NodePanelState "bpy.types.NodePanelState")]

<a id="bpy.types.Node.parent"></a>

#### bpy.types.Node.parent

Parent this node is attached to, e.g. a Frame node

**Type:**

[`Node`](#bpy.types.Node "bpy.types.Node") | None

<a id="bpy.types.Node.select"></a>

#### bpy.types.Node.select

Node selection state (default False)

**Type:**

bool

<a id="bpy.types.Node.show_options"></a>

#### bpy.types.Node.show_options

Whether the node options are visible, e.g. the selected data-block of a node group node (default False)

**Type:**

bool

<a id="bpy.types.Node.show_preview"></a>

#### bpy.types.Node.show_preview

(default False)

**Type:**

bool

<a id="bpy.types.Node.show_texture"></a>

#### bpy.types.Node.show_texture

Display node in viewport textured shading mode (default False)

**Type:**

bool

<a id="bpy.types.Node.type"></a>

#### bpy.types.Node.type

Legacy unique node type identifier, redundant with bl_idname property (default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.Node.use_custom_color"></a>

#### bpy.types.Node.use_custom_color

Use custom color for the node (default False)

**Type:**

bool

<a id="bpy.types.Node.warning_propagation"></a>

#### bpy.types.Node.warning_propagation

The kinds of messages that should be propagated from this node to the parent group node (default `'ALL'`)

- `ALL`
  All Messages – Propagate every info, error, and warning message upstream.
- `ERRORS_AND_WARNINGS`
  Errors and Warnings – Propagate only error and warning messages upstream.
- `ERRORS`
  Errors – Propagate only error messages upstream.
- `NONE`
  None – Do not propagate any messages upstream.

**Type:**

Literal[‘ALL’, ‘ERRORS_AND_WARNINGS’, ‘ERRORS’, ‘NONE’]

<a id="bpy.types.Node.width"></a>

#### bpy.types.Node.width

Width of the node (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.Node.bl_system_properties_get"></a>

#### bpy.types.Node.bl_system_properties_get(*, do_create=False)

DEBUG ONLY. Internal access to runtime-defined RNA data storage, intended solely for testing and debugging purposes. Do not access it in regular scripting work, and in particular, do not assume that it contains writable data

**Parameters:**

**do_create** (bool) – Ensure that system properties are created if they do not exist yet (optional)

**Returns:**

The system properties root container, or None if there are no system properties stored in this data yet, and its creation was not requested

**Return type:**

[`PropertyGroup`](bpy.types.PropertyGroup.md#bpy.types.PropertyGroup "bpy.types.PropertyGroup")

<a id="bpy.types.Node.socket_value_update"></a>

#### bpy.types.Node.socket_value_update(context)

Update after property changes

**Parameters:**

**context** ([`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context") | None) – (never None)

<a id="bpy.types.Node.is_registered_node_type"></a>

#### classmethod bpy.types.Node.is_registered_node_type()

True if a registered node type

**Returns:**

Result

**Return type:**

bool

<a id="bpy.types.Node.poll"></a>

#### classmethod bpy.types.Node.poll(node_tree)

If non-null output is returned, the node type can be added to the tree

**Parameters:**

**node_tree** ([`NodeTree`](bpy.types.NodeTree.md#bpy.types.NodeTree "bpy.types.NodeTree") | None) – Node Tree

**Return type:**

bool

<a id="bpy.types.Node.poll_instance"></a>

#### bpy.types.Node.poll_instance(node_tree)

If non-null output is returned, the node can be added to the tree

**Parameters:**

**node_tree** ([`NodeTree`](bpy.types.NodeTree.md#bpy.types.NodeTree "bpy.types.NodeTree") | None) – Node Tree

**Return type:**

bool

<a id="bpy.types.Node.update"></a>

#### bpy.types.Node.update()

Update on node graph topology changes (adding or removing nodes and links)

<a id="bpy.types.Node.insert_link"></a>

#### bpy.types.Node.insert_link(link)

Handle creation of a link to or from the node

**Parameters:**

**link** ([`NodeLink`](bpy.types.NodeLink.md#bpy.types.NodeLink "bpy.types.NodeLink") | None) – Link, Node link that will be inserted (never None)

<a id="bpy.types.Node.init"></a>

#### bpy.types.Node.init(context)

Initialize a new instance of this node

**Parameters:**

**context** ([`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context") | None) – (never None)

<a id="bpy.types.Node.copy"></a>

#### bpy.types.Node.copy(node)

Initialize a new instance of this node from an existing node

**Parameters:**

**node** ([`Node`](#bpy.types.Node "bpy.types.Node") | None) – Node, Existing node to copy (never None)

<a id="bpy.types.Node.free"></a>

#### bpy.types.Node.free()

Clean up node on removal

<a id="bpy.types.Node.draw_buttons"></a>

#### bpy.types.Node.draw_buttons(context, layout)

Draw node buttons

**Parameters:**

- **context** ([`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context") | None) – (never None)
- **layout** ([`UILayout`](bpy.types.UILayout.md#bpy.types.UILayout "bpy.types.UILayout") | None) – Layout, Layout in the UI (never None)

<a id="bpy.types.Node.draw_buttons_ext"></a>

#### bpy.types.Node.draw_buttons_ext(context, layout)

Draw node buttons in the sidebar

**Parameters:**

- **context** ([`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context") | None) – (never None)
- **layout** ([`UILayout`](bpy.types.UILayout.md#bpy.types.UILayout "bpy.types.UILayout") | None) – Layout, Layout in the UI (never None)

<a id="bpy.types.Node.draw_label"></a>

#### bpy.types.Node.draw_label()

Returns a dynamic label string

**Returns:**

Label, (never None)

**Return type:**

str

<a id="bpy.types.Node.debug_zone_body_lazy_function_graph"></a>

#### bpy.types.Node.debug_zone_body_lazy_function_graph()

Get the internal lazy-function graph for the body of this zone

**Returns:**

Dot Graph, Graph in dot format

**Return type:**

str

<a id="bpy.types.Node.debug_zone_lazy_function_graph"></a>

#### bpy.types.Node.debug_zone_lazy_function_graph()

Get the internal lazy-function graph for this zone

**Returns:**

Dot Graph, Graph in dot format

**Return type:**

str

<a id="bpy.types.Node.bl_rna_get_subclass"></a>

#### classmethod bpy.types.Node.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.Node.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.Node.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([type](#bpy.types.Node.type "bpy.types.Node.type") | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

[type](#bpy.types.Node.type "bpy.types.Node.type")

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
| - `bpy.context.active_node` - `bpy.context.selected_nodes` - `bpy.context.texture_node` - [`GeometryNodeForeachGeometryElementInput.paired_output`](bpy.types.GeometryNodeForeachGeometryElementInput.md#bpy.types.GeometryNodeForeachGeometryElementInput.paired_output "bpy.types.GeometryNodeForeachGeometryElementInput.paired_output") - [`GeometryNodeMenuSwitch.enum_definition`](bpy.types.GeometryNodeMenuSwitch.md#bpy.types.GeometryNodeMenuSwitch.enum_definition "bpy.types.GeometryNodeMenuSwitch.enum_definition") - [`GeometryNodeRepeatInput.paired_output`](bpy.types.GeometryNodeRepeatInput.md#bpy.types.GeometryNodeRepeatInput.paired_output "bpy.types.GeometryNodeRepeatInput.paired_output") - [`GeometryNodeSimulationInput.paired_output`](bpy.types.GeometryNodeSimulationInput.md#bpy.types.GeometryNodeSimulationInput.paired_output "bpy.types.GeometryNodeSimulationInput.paired_output") - [`Node.copy`](#bpy.types.Node.copy "bpy.types.Node.copy") - [`Node.parent`](#bpy.types.Node.parent "bpy.types.Node.parent") - [`NodeClosureInput.paired_output`](bpy.types.NodeClosureInput.md#bpy.types.NodeClosureInput.paired_output "bpy.types.NodeClosureInput.paired_output") - [`NodeLink.from_node`](bpy.types.NodeLink.md#bpy.types.NodeLink.from_node "bpy.types.NodeLink.from_node") - [`NodeLink.to_node`](bpy.types.NodeLink.md#bpy.types.NodeLink.to_node "bpy.types.NodeLink.to_node") - [`NodeSocket.draw`](bpy.types.NodeSocket.md#bpy.types.NodeSocket.draw "bpy.types.NodeSocket.draw") - [`NodeSocket.draw_color`](bpy.types.NodeSocket.md#bpy.types.NodeSocket.draw_color "bpy.types.NodeSocket.draw_color") - [`NodeSocket.node`](bpy.types.NodeSocket.md#bpy.types.NodeSocket.node "bpy.types.NodeSocket.node") - [`NodeSocketStandard.draw`](bpy.types.NodeSocketStandard.md#bpy.types.NodeSocketStandard.draw "bpy.types.NodeSocketStandard.draw") - [`NodeSocketStandard.draw_color`](bpy.types.NodeSocketStandard.md#bpy.types.NodeSocketStandard.draw_color "bpy.types.NodeSocketStandard.draw_color") - [`NodeTree.nodes`](bpy.types.NodeTree.md#bpy.types.NodeTree.nodes "bpy.types.NodeTree.nodes") - [`NodeTreeInterfaceSocket.from_socket`](bpy.types.NodeTreeInterfaceSocket.md#bpy.types.NodeTreeInterfaceSocket.from_socket "bpy.types.NodeTreeInterfaceSocket.from_socket") - [`NodeTreeInterfaceSocket.init_socket`](bpy.types.NodeTreeInterfaceSocket.md#bpy.types.NodeTreeInterfaceSocket.init_socket "bpy.types.NodeTreeInterfaceSocket.init_socket") - [`NodeTreeInterfaceSocketBool.from_socket`](bpy.types.NodeTreeInterfaceSocketBool.md#bpy.types.NodeTreeInterfaceSocketBool.from_socket "bpy.types.NodeTreeInterfaceSocketBool.from_socket") - [`NodeTreeInterfaceSocketBool.init_socket`](bpy.types.NodeTreeInterfaceSocketBool.md#bpy.types.NodeTreeInterfaceSocketBool.init_socket "bpy.types.NodeTreeInterfaceSocketBool.init_socket") - [`NodeTreeInterfaceSocketBundle.from_socket`](bpy.types.NodeTreeInterfaceSocketBundle.md#bpy.types.NodeTreeInterfaceSocketBundle.from_socket "bpy.types.NodeTreeInterfaceSocketBundle.from_socket") - [`NodeTreeInterfaceSocketBundle.init_socket`](bpy.types.NodeTreeInterfaceSocketBundle.md#bpy.types.NodeTreeInterfaceSocketBundle.init_socket "bpy.types.NodeTreeInterfaceSocketBundle.init_socket") - [`NodeTreeInterfaceSocketClosure.from_socket`](bpy.types.NodeTreeInterfaceSocketClosure.md#bpy.types.NodeTreeInterfaceSocketClosure.from_socket "bpy.types.NodeTreeInterfaceSocketClosure.from_socket") - [`NodeTreeInterfaceSocketClosure.init_socket`](bpy.types.NodeTreeInterfaceSocketClosure.md#bpy.types.NodeTreeInterfaceSocketClosure.init_socket "bpy.types.NodeTreeInterfaceSocketClosure.init_socket") - [`NodeTreeInterfaceSocketCollection.from_socket`](bpy.types.NodeTreeInterfaceSocketCollection.md#bpy.types.NodeTreeInterfaceSocketCollection.from_socket "bpy.types.NodeTreeInterfaceSocketCollection.from_socket") - [`NodeTreeInterfaceSocketCollection.init_socket`](bpy.types.NodeTreeInterfaceSocketCollection.md#bpy.types.NodeTreeInterfaceSocketCollection.init_socket "bpy.types.NodeTreeInterfaceSocketCollection.init_socket") - [`NodeTreeInterfaceSocketColor.from_socket`](bpy.types.NodeTreeInterfaceSocketColor.md#bpy.types.NodeTreeInterfaceSocketColor.from_socket "bpy.types.NodeTreeInterfaceSocketColor.from_socket") - [`NodeTreeInterfaceSocketColor.init_socket`](bpy.types.NodeTreeInterfaceSocketColor.md#bpy.types.NodeTreeInterfaceSocketColor.init_socket "bpy.types.NodeTreeInterfaceSocketColor.init_socket") - [`NodeTreeInterfaceSocketFloat.from_socket`](bpy.types.NodeTreeInterfaceSocketFloat.md#bpy.types.NodeTreeInterfaceSocketFloat.from_socket "bpy.types.NodeTreeInterfaceSocketFloat.from_socket") - [`NodeTreeInterfaceSocketFloat.init_socket`](bpy.types.NodeTreeInterfaceSocketFloat.md#bpy.types.NodeTreeInterfaceSocketFloat.init_socket "bpy.types.NodeTreeInterfaceSocketFloat.init_socket") - [`NodeTreeInterfaceSocketFloatAngle.from_socket`](bpy.types.NodeTreeInterfaceSocketFloatAngle.md#bpy.types.NodeTreeInterfaceSocketFloatAngle.from_socket "bpy.types.NodeTreeInterfaceSocketFloatAngle.from_socket") - [`NodeTreeInterfaceSocketFloatAngle.init_socket`](bpy.types.NodeTreeInterfaceSocketFloatAngle.md#bpy.types.NodeTreeInterfaceSocketFloatAngle.init_socket "bpy.types.NodeTreeInterfaceSocketFloatAngle.init_socket") - [`NodeTreeInterfaceSocketFloatColorTemperature.from_socket`](bpy.types.NodeTreeInterfaceSocketFloatColorTemperature.md#bpy.types.NodeTreeInterfaceSocketFloatColorTemperature.from_socket "bpy.types.NodeTreeInterfaceSocketFloatColorTemperature.from_socket") - [`NodeTreeInterfaceSocketFloatColorTemperature.init_socket`](bpy.types.NodeTreeInterfaceSocketFloatColorTemperature.md#bpy.types.NodeTreeInterfaceSocketFloatColorTemperature.init_socket "bpy.types.NodeTreeInterfaceSocketFloatColorTemperature.init_socket") - [`NodeTreeInterfaceSocketFloatDistance.from_socket`](bpy.types.NodeTreeInterfaceSocketFloatDistance.md#bpy.types.NodeTreeInterfaceSocketFloatDistance.from_socket "bpy.types.NodeTreeInterfaceSocketFloatDistance.from_socket") - [`NodeTreeInterfaceSocketFloatDistance.init_socket`](bpy.types.NodeTreeInterfaceSocketFloatDistance.md#bpy.types.NodeTreeInterfaceSocketFloatDistance.init_socket "bpy.types.NodeTreeInterfaceSocketFloatDistance.init_socket") - [`NodeTreeInterfaceSocketFloatFactor.from_socket`](bpy.types.NodeTreeInterfaceSocketFloatFactor.md#bpy.types.NodeTreeInterfaceSocketFloatFactor.from_socket "bpy.types.NodeTreeInterfaceSocketFloatFactor.from_socket") - [`NodeTreeInterfaceSocketFloatFactor.init_socket`](bpy.types.NodeTreeInterfaceSocketFloatFactor.md#bpy.types.NodeTreeInterfaceSocketFloatFactor.init_socket "bpy.types.NodeTreeInterfaceSocketFloatFactor.init_socket") - [`NodeTreeInterfaceSocketFloatFrequency.from_socket`](bpy.types.NodeTreeInterfaceSocketFloatFrequency.md#bpy.types.NodeTreeInterfaceSocketFloatFrequency.from_socket "bpy.types.NodeTreeInterfaceSocketFloatFrequency.from_socket") - [`NodeTreeInterfaceSocketFloatFrequency.init_socket`](bpy.types.NodeTreeInterfaceSocketFloatFrequency.md#bpy.types.NodeTreeInterfaceSocketFloatFrequency.init_socket "bpy.types.NodeTreeInterfaceSocketFloatFrequency.init_socket") - [`NodeTreeInterfaceSocketFloatMass.from_socket`](bpy.types.NodeTreeInterfaceSocketFloatMass.md#bpy.types.NodeTreeInterfaceSocketFloatMass.from_socket "bpy.types.NodeTreeInterfaceSocketFloatMass.from_socket") - [`NodeTreeInterfaceSocketFloatMass.init_socket`](bpy.types.NodeTreeInterfaceSocketFloatMass.md#bpy.types.NodeTreeInterfaceSocketFloatMass.init_socket "bpy.types.NodeTreeInterfaceSocketFloatMass.init_socket") - [`NodeTreeInterfaceSocketFloatPercentage.from_socket`](bpy.types.NodeTreeInterfaceSocketFloatPercentage.md#bpy.types.NodeTreeInterfaceSocketFloatPercentage.from_socket "bpy.types.NodeTreeInterfaceSocketFloatPercentage.from_socket") - [`NodeTreeInterfaceSocketFloatPercentage.init_socket`](bpy.types.NodeTreeInterfaceSocketFloatPercentage.md#bpy.types.NodeTreeInterfaceSocketFloatPercentage.init_socket "bpy.types.NodeTreeInterfaceSocketFloatPercentage.init_socket") - [`NodeTreeInterfaceSocketFloatPixel.from_socket`](bpy.types.NodeTreeInterfaceSocketFloatPixel.md#bpy.types.NodeTreeInterfaceSocketFloatPixel.from_socket "bpy.types.NodeTreeInterfaceSocketFloatPixel.from_socket") - [`NodeTreeInterfaceSocketFloatPixel.init_socket`](bpy.types.NodeTreeInterfaceSocketFloatPixel.md#bpy.types.NodeTreeInterfaceSocketFloatPixel.init_socket "bpy.types.NodeTreeInterfaceSocketFloatPixel.init_socket") - [`NodeTreeInterfaceSocketFloatTime.from_socket`](bpy.types.NodeTreeInterfaceSocketFloatTime.md#bpy.types.NodeTreeInterfaceSocketFloatTime.from_socket "bpy.types.NodeTreeInterfaceSocketFloatTime.from_socket") - [`NodeTreeInterfaceSocketFloatTime.init_socket`](bpy.types.NodeTreeInterfaceSocketFloatTime.md#bpy.types.NodeTreeInterfaceSocketFloatTime.init_socket "bpy.types.NodeTreeInterfaceSocketFloatTime.init_socket") - [`NodeTreeInterfaceSocketFloatTimeAbsolute.from_socket`](bpy.types.NodeTreeInterfaceSocketFloatTimeAbsolute.md#bpy.types.NodeTreeInterfaceSocketFloatTimeAbsolute.from_socket "bpy.types.NodeTreeInterfaceSocketFloatTimeAbsolute.from_socket") - [`NodeTreeInterfaceSocketFloatTimeAbsolute.init_socket`](bpy.types.NodeTreeInterfaceSocketFloatTimeAbsolute.md#bpy.types.NodeTreeInterfaceSocketFloatTimeAbsolute.init_socket "bpy.types.NodeTreeInterfaceSocketFloatTimeAbsolute.init_socket") - [`NodeTreeInterfaceSocketFloatUnsigned.from_socket`](bpy.types.NodeTreeInterfaceSocketFloatUnsigned.md#bpy.types.NodeTreeInterfaceSocketFloatUnsigned.from_socket "bpy.types.NodeTreeInterfaceSocketFloatUnsigned.from_socket") - [`NodeTreeInterfaceSocketFloatUnsigned.init_socket`](bpy.types.NodeTreeInterfaceSocketFloatUnsigned.md#bpy.types.NodeTreeInterfaceSocketFloatUnsigned.init_socket "bpy.types.NodeTreeInterfaceSocketFloatUnsigned.init_socket") - [`NodeTreeInterfaceSocketFloatWavelength.from_socket`](bpy.types.NodeTreeInterfaceSocketFloatWavelength.md#bpy.types.NodeTreeInterfaceSocketFloatWavelength.from_socket "bpy.types.NodeTreeInterfaceSocketFloatWavelength.from_socket") - [`NodeTreeInterfaceSocketFloatWavelength.init_socket`](bpy.types.NodeTreeInterfaceSocketFloatWavelength.md#bpy.types.NodeTreeInterfaceSocketFloatWavelength.init_socket "bpy.types.NodeTreeInterfaceSocketFloatWavelength.init_socket") - [`NodeTreeInterfaceSocketGeometry.from_socket`](bpy.types.NodeTreeInterfaceSocketGeometry.md#bpy.types.NodeTreeInterfaceSocketGeometry.from_socket "bpy.types.NodeTreeInterfaceSocketGeometry.from_socket") - [`NodeTreeInterfaceSocketGeometry.init_socket`](bpy.types.NodeTreeInterfaceSocketGeometry.md#bpy.types.NodeTreeInterfaceSocketGeometry.init_socket "bpy.types.NodeTreeInterfaceSocketGeometry.init_socket") - [`NodeTreeInterfaceSocketImage.from_socket`](bpy.types.NodeTreeInterfaceSocketImage.md#bpy.types.NodeTreeInterfaceSocketImage.from_socket "bpy.types.NodeTreeInterfaceSocketImage.from_socket") - [`NodeTreeInterfaceSocketImage.init_socket`](bpy.types.NodeTreeInterfaceSocketImage.md#bpy.types.NodeTreeInterfaceSocketImage.init_socket "bpy.types.NodeTreeInterfaceSocketImage.init_socket") - [`NodeTreeInterfaceSocketInt.from_socket`](bpy.types.NodeTreeInterfaceSocketInt.md#bpy.types.NodeTreeInterfaceSocketInt.from_socket "bpy.types.NodeTreeInterfaceSocketInt.from_socket") - [`NodeTreeInterfaceSocketInt.init_socket`](bpy.types.NodeTreeInterfaceSocketInt.md#bpy.types.NodeTreeInterfaceSocketInt.init_socket "bpy.types.NodeTreeInterfaceSocketInt.init_socket") - [`NodeTreeInterfaceSocketIntFactor.from_socket`](bpy.types.NodeTreeInterfaceSocketIntFactor.md#bpy.types.NodeTreeInterfaceSocketIntFactor.from_socket "bpy.types.NodeTreeInterfaceSocketIntFactor.from_socket") - [`NodeTreeInterfaceSocketIntFactor.init_socket`](bpy.types.NodeTreeInterfaceSocketIntFactor.md#bpy.types.NodeTreeInterfaceSocketIntFactor.init_socket "bpy.types.NodeTreeInterfaceSocketIntFactor.init_socket") - [`NodeTreeInterfaceSocketIntPercentage.from_socket`](bpy.types.NodeTreeInterfaceSocketIntPercentage.md#bpy.types.NodeTreeInterfaceSocketIntPercentage.from_socket "bpy.types.NodeTreeInterfaceSocketIntPercentage.from_socket") - [`NodeTreeInterfaceSocketIntPercentage.init_socket`](bpy.types.NodeTreeInterfaceSocketIntPercentage.md#bpy.types.NodeTreeInterfaceSocketIntPercentage.init_socket "bpy.types.NodeTreeInterfaceSocketIntPercentage.init_socket") - [`NodeTreeInterfaceSocketIntPixel.from_socket`](bpy.types.NodeTreeInterfaceSocketIntPixel.md#bpy.types.NodeTreeInterfaceSocketIntPixel.from_socket "bpy.types.NodeTreeInterfaceSocketIntPixel.from_socket") - [`NodeTreeInterfaceSocketIntPixel.init_socket`](bpy.types.NodeTreeInterfaceSocketIntPixel.md#bpy.types.NodeTreeInterfaceSocketIntPixel.init_socket "bpy.types.NodeTreeInterfaceSocketIntPixel.init_socket") - [`NodeTreeInterfaceSocketIntUnsigned.from_socket`](bpy.types.NodeTreeInterfaceSocketIntUnsigned.md#bpy.types.NodeTreeInterfaceSocketIntUnsigned.from_socket "bpy.types.NodeTreeInterfaceSocketIntUnsigned.from_socket") - [`NodeTreeInterfaceSocketIntUnsigned.init_socket`](bpy.types.NodeTreeInterfaceSocketIntUnsigned.md#bpy.types.NodeTreeInterfaceSocketIntUnsigned.init_socket "bpy.types.NodeTreeInterfaceSocketIntUnsigned.init_socket") - [`NodeTreeInterfaceSocketIntVector2D.from_socket`](bpy.types.NodeTreeInterfaceSocketIntVector2D.md#bpy.types.NodeTreeInterfaceSocketIntVector2D.from_socket "bpy.types.NodeTreeInterfaceSocketIntVector2D.from_socket") - [`NodeTreeInterfaceSocketIntVector2D.init_socket`](bpy.types.NodeTreeInterfaceSocketIntVector2D.md#bpy.types.NodeTreeInterfaceSocketIntVector2D.init_socket "bpy.types.NodeTreeInterfaceSocketIntVector2D.init_socket") - [`NodeTreeInterfaceSocketIntVector3D.from_socket`](bpy.types.NodeTreeInterfaceSocketIntVector3D.md#bpy.types.NodeTreeInterfaceSocketIntVector3D.from_socket "bpy.types.NodeTreeInterfaceSocketIntVector3D.from_socket") - [`NodeTreeInterfaceSocketIntVector3D.init_socket`](bpy.types.NodeTreeInterfaceSocketIntVector3D.md#bpy.types.NodeTreeInterfaceSocketIntVector3D.init_socket "bpy.types.NodeTreeInterfaceSocketIntVector3D.init_socket") - [`NodeTreeInterfaceSocketIntVectorFactor2D.from_socket`](bpy.types.NodeTreeInterfaceSocketIntVectorFactor2D.md#bpy.types.NodeTreeInterfaceSocketIntVectorFactor2D.from_socket "bpy.types.NodeTreeInterfaceSocketIntVectorFactor2D.from_socket") - [`NodeTreeInterfaceSocketIntVectorFactor2D.init_socket`](bpy.types.NodeTreeInterfaceSocketIntVectorFactor2D.md#bpy.types.NodeTreeInterfaceSocketIntVectorFactor2D.init_socket "bpy.types.NodeTreeInterfaceSocketIntVectorFactor2D.init_socket") - [`NodeTreeInterfaceSocketIntVectorFactor3D.from_socket`](bpy.types.NodeTreeInterfaceSocketIntVectorFactor3D.md#bpy.types.NodeTreeInterfaceSocketIntVectorFactor3D.from_socket "bpy.types.NodeTreeInterfaceSocketIntVectorFactor3D.from_socket") - [`NodeTreeInterfaceSocketIntVectorFactor3D.init_socket`](bpy.types.NodeTreeInterfaceSocketIntVectorFactor3D.md#bpy.types.NodeTreeInterfaceSocketIntVectorFactor3D.init_socket "bpy.types.NodeTreeInterfaceSocketIntVectorFactor3D.init_socket") - [`NodeTreeInterfaceSocketIntVectorPercentage2D.from_socket`](bpy.types.NodeTreeInterfaceSocketIntVectorPercentage2D.md#bpy.types.NodeTreeInterfaceSocketIntVectorPercentage2D.from_socket "bpy.types.NodeTreeInterfaceSocketIntVectorPercentage2D.from_socket") - [`NodeTreeInterfaceSocketIntVectorPercentage2D.init_socket`](bpy.types.NodeTreeInterfaceSocketIntVectorPercentage2D.md#bpy.types.NodeTreeInterfaceSocketIntVectorPercentage2D.init_socket "bpy.types.NodeTreeInterfaceSocketIntVectorPercentage2D.init_socket") - [`NodeTreeInterfaceSocketIntVectorPercentage3D.from_socket`](bpy.types.NodeTreeInterfaceSocketIntVectorPercentage3D.md#bpy.types.NodeTreeInterfaceSocketIntVectorPercentage3D.from_socket "bpy.types.NodeTreeInterfaceSocketIntVectorPercentage3D.from_socket") - [`NodeTreeInterfaceSocketIntVectorPercentage3D.init_socket`](bpy.types.NodeTreeInterfaceSocketIntVectorPercentage3D.md#bpy.types.NodeTreeInterfaceSocketIntVectorPercentage3D.init_socket "bpy.types.NodeTreeInterfaceSocketIntVectorPercentage3D.init_socket") - [`NodeTreeInterfaceSocketIntVectorPixel2D.from_socket`](bpy.types.NodeTreeInterfaceSocketIntVectorPixel2D.md#bpy.types.NodeTreeInterfaceSocketIntVectorPixel2D.from_socket "bpy.types.NodeTreeInterfaceSocketIntVectorPixel2D.from_socket") - [`NodeTreeInterfaceSocketIntVectorPixel2D.init_socket`](bpy.types.NodeTreeInterfaceSocketIntVectorPixel2D.md#bpy.types.NodeTreeInterfaceSocketIntVectorPixel2D.init_socket "bpy.types.NodeTreeInterfaceSocketIntVectorPixel2D.init_socket") - [`NodeTreeInterfaceSocketIntVectorPixel3D.from_socket`](bpy.types.NodeTreeInterfaceSocketIntVectorPixel3D.md#bpy.types.NodeTreeInterfaceSocketIntVectorPixel3D.from_socket "bpy.types.NodeTreeInterfaceSocketIntVectorPixel3D.from_socket") - [`NodeTreeInterfaceSocketIntVectorPixel3D.init_socket`](bpy.types.NodeTreeInterfaceSocketIntVectorPixel3D.md#bpy.types.NodeTreeInterfaceSocketIntVectorPixel3D.init_socket "bpy.types.NodeTreeInterfaceSocketIntVectorPixel3D.init_socket") - [`NodeTreeInterfaceSocketIntVectorUnsigned2D.from_socket`](bpy.types.NodeTreeInterfaceSocketIntVectorUnsigned2D.md#bpy.types.NodeTreeInterfaceSocketIntVectorUnsigned2D.from_socket "bpy.types.NodeTreeInterfaceSocketIntVectorUnsigned2D.from_socket") - [`NodeTreeInterfaceSocketIntVectorUnsigned2D.init_socket`](bpy.types.NodeTreeInterfaceSocketIntVectorUnsigned2D.md#bpy.types.NodeTreeInterfaceSocketIntVectorUnsigned2D.init_socket "bpy.types.NodeTreeInterfaceSocketIntVectorUnsigned2D.init_socket") - [`NodeTreeInterfaceSocketIntVectorUnsigned3D.from_socket`](bpy.types.NodeTreeInterfaceSocketIntVectorUnsigned3D.md#bpy.types.NodeTreeInterfaceSocketIntVectorUnsigned3D.from_socket "bpy.types.NodeTreeInterfaceSocketIntVectorUnsigned3D.from_socket") | - [`NodeTreeInterfaceSocketIntVectorUnsigned3D.init_socket`](bpy.types.NodeTreeInterfaceSocketIntVectorUnsigned3D.md#bpy.types.NodeTreeInterfaceSocketIntVectorUnsigned3D.init_socket "bpy.types.NodeTreeInterfaceSocketIntVectorUnsigned3D.init_socket") - [`NodeTreeInterfaceSocketMaterial.from_socket`](bpy.types.NodeTreeInterfaceSocketMaterial.md#bpy.types.NodeTreeInterfaceSocketMaterial.from_socket "bpy.types.NodeTreeInterfaceSocketMaterial.from_socket") - [`NodeTreeInterfaceSocketMaterial.init_socket`](bpy.types.NodeTreeInterfaceSocketMaterial.md#bpy.types.NodeTreeInterfaceSocketMaterial.init_socket "bpy.types.NodeTreeInterfaceSocketMaterial.init_socket") - [`NodeTreeInterfaceSocketMatrix.from_socket`](bpy.types.NodeTreeInterfaceSocketMatrix.md#bpy.types.NodeTreeInterfaceSocketMatrix.from_socket "bpy.types.NodeTreeInterfaceSocketMatrix.from_socket") - [`NodeTreeInterfaceSocketMatrix.init_socket`](bpy.types.NodeTreeInterfaceSocketMatrix.md#bpy.types.NodeTreeInterfaceSocketMatrix.init_socket "bpy.types.NodeTreeInterfaceSocketMatrix.init_socket") - [`NodeTreeInterfaceSocketMenu.from_socket`](bpy.types.NodeTreeInterfaceSocketMenu.md#bpy.types.NodeTreeInterfaceSocketMenu.from_socket "bpy.types.NodeTreeInterfaceSocketMenu.from_socket") - [`NodeTreeInterfaceSocketMenu.init_socket`](bpy.types.NodeTreeInterfaceSocketMenu.md#bpy.types.NodeTreeInterfaceSocketMenu.init_socket "bpy.types.NodeTreeInterfaceSocketMenu.init_socket") - [`NodeTreeInterfaceSocketObject.from_socket`](bpy.types.NodeTreeInterfaceSocketObject.md#bpy.types.NodeTreeInterfaceSocketObject.from_socket "bpy.types.NodeTreeInterfaceSocketObject.from_socket") - [`NodeTreeInterfaceSocketObject.init_socket`](bpy.types.NodeTreeInterfaceSocketObject.md#bpy.types.NodeTreeInterfaceSocketObject.init_socket "bpy.types.NodeTreeInterfaceSocketObject.init_socket") - [`NodeTreeInterfaceSocketRotation.from_socket`](bpy.types.NodeTreeInterfaceSocketRotation.md#bpy.types.NodeTreeInterfaceSocketRotation.from_socket "bpy.types.NodeTreeInterfaceSocketRotation.from_socket") - [`NodeTreeInterfaceSocketRotation.init_socket`](bpy.types.NodeTreeInterfaceSocketRotation.md#bpy.types.NodeTreeInterfaceSocketRotation.init_socket "bpy.types.NodeTreeInterfaceSocketRotation.init_socket") - [`NodeTreeInterfaceSocketShader.from_socket`](bpy.types.NodeTreeInterfaceSocketShader.md#bpy.types.NodeTreeInterfaceSocketShader.from_socket "bpy.types.NodeTreeInterfaceSocketShader.from_socket") - [`NodeTreeInterfaceSocketShader.init_socket`](bpy.types.NodeTreeInterfaceSocketShader.md#bpy.types.NodeTreeInterfaceSocketShader.init_socket "bpy.types.NodeTreeInterfaceSocketShader.init_socket") - [`NodeTreeInterfaceSocketString.from_socket`](bpy.types.NodeTreeInterfaceSocketString.md#bpy.types.NodeTreeInterfaceSocketString.from_socket "bpy.types.NodeTreeInterfaceSocketString.from_socket") - [`NodeTreeInterfaceSocketString.init_socket`](bpy.types.NodeTreeInterfaceSocketString.md#bpy.types.NodeTreeInterfaceSocketString.init_socket "bpy.types.NodeTreeInterfaceSocketString.init_socket") - [`NodeTreeInterfaceSocketStringFilePath.from_socket`](bpy.types.NodeTreeInterfaceSocketStringFilePath.md#bpy.types.NodeTreeInterfaceSocketStringFilePath.from_socket "bpy.types.NodeTreeInterfaceSocketStringFilePath.from_socket") - [`NodeTreeInterfaceSocketStringFilePath.init_socket`](bpy.types.NodeTreeInterfaceSocketStringFilePath.md#bpy.types.NodeTreeInterfaceSocketStringFilePath.init_socket "bpy.types.NodeTreeInterfaceSocketStringFilePath.init_socket") - [`NodeTreeInterfaceSocketTexture.from_socket`](bpy.types.NodeTreeInterfaceSocketTexture.md#bpy.types.NodeTreeInterfaceSocketTexture.from_socket "bpy.types.NodeTreeInterfaceSocketTexture.from_socket") - [`NodeTreeInterfaceSocketTexture.init_socket`](bpy.types.NodeTreeInterfaceSocketTexture.md#bpy.types.NodeTreeInterfaceSocketTexture.init_socket "bpy.types.NodeTreeInterfaceSocketTexture.init_socket") - [`NodeTreeInterfaceSocketVector.from_socket`](bpy.types.NodeTreeInterfaceSocketVector.md#bpy.types.NodeTreeInterfaceSocketVector.from_socket "bpy.types.NodeTreeInterfaceSocketVector.from_socket") - [`NodeTreeInterfaceSocketVector.init_socket`](bpy.types.NodeTreeInterfaceSocketVector.md#bpy.types.NodeTreeInterfaceSocketVector.init_socket "bpy.types.NodeTreeInterfaceSocketVector.init_socket") - [`NodeTreeInterfaceSocketVector2D.from_socket`](bpy.types.NodeTreeInterfaceSocketVector2D.md#bpy.types.NodeTreeInterfaceSocketVector2D.from_socket "bpy.types.NodeTreeInterfaceSocketVector2D.from_socket") - [`NodeTreeInterfaceSocketVector2D.init_socket`](bpy.types.NodeTreeInterfaceSocketVector2D.md#bpy.types.NodeTreeInterfaceSocketVector2D.init_socket "bpy.types.NodeTreeInterfaceSocketVector2D.init_socket") - [`NodeTreeInterfaceSocketVector4D.from_socket`](bpy.types.NodeTreeInterfaceSocketVector4D.md#bpy.types.NodeTreeInterfaceSocketVector4D.from_socket "bpy.types.NodeTreeInterfaceSocketVector4D.from_socket") - [`NodeTreeInterfaceSocketVector4D.init_socket`](bpy.types.NodeTreeInterfaceSocketVector4D.md#bpy.types.NodeTreeInterfaceSocketVector4D.init_socket "bpy.types.NodeTreeInterfaceSocketVector4D.init_socket") - [`NodeTreeInterfaceSocketVectorAcceleration.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorAcceleration.md#bpy.types.NodeTreeInterfaceSocketVectorAcceleration.from_socket "bpy.types.NodeTreeInterfaceSocketVectorAcceleration.from_socket") - [`NodeTreeInterfaceSocketVectorAcceleration.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorAcceleration.md#bpy.types.NodeTreeInterfaceSocketVectorAcceleration.init_socket "bpy.types.NodeTreeInterfaceSocketVectorAcceleration.init_socket") - [`NodeTreeInterfaceSocketVectorAcceleration2D.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorAcceleration2D.md#bpy.types.NodeTreeInterfaceSocketVectorAcceleration2D.from_socket "bpy.types.NodeTreeInterfaceSocketVectorAcceleration2D.from_socket") - [`NodeTreeInterfaceSocketVectorAcceleration2D.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorAcceleration2D.md#bpy.types.NodeTreeInterfaceSocketVectorAcceleration2D.init_socket "bpy.types.NodeTreeInterfaceSocketVectorAcceleration2D.init_socket") - [`NodeTreeInterfaceSocketVectorAcceleration4D.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorAcceleration4D.md#bpy.types.NodeTreeInterfaceSocketVectorAcceleration4D.from_socket "bpy.types.NodeTreeInterfaceSocketVectorAcceleration4D.from_socket") - [`NodeTreeInterfaceSocketVectorAcceleration4D.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorAcceleration4D.md#bpy.types.NodeTreeInterfaceSocketVectorAcceleration4D.init_socket "bpy.types.NodeTreeInterfaceSocketVectorAcceleration4D.init_socket") - [`NodeTreeInterfaceSocketVectorDirection.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorDirection.md#bpy.types.NodeTreeInterfaceSocketVectorDirection.from_socket "bpy.types.NodeTreeInterfaceSocketVectorDirection.from_socket") - [`NodeTreeInterfaceSocketVectorDirection.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorDirection.md#bpy.types.NodeTreeInterfaceSocketVectorDirection.init_socket "bpy.types.NodeTreeInterfaceSocketVectorDirection.init_socket") - [`NodeTreeInterfaceSocketVectorDirection2D.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorDirection2D.md#bpy.types.NodeTreeInterfaceSocketVectorDirection2D.from_socket "bpy.types.NodeTreeInterfaceSocketVectorDirection2D.from_socket") - [`NodeTreeInterfaceSocketVectorDirection2D.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorDirection2D.md#bpy.types.NodeTreeInterfaceSocketVectorDirection2D.init_socket "bpy.types.NodeTreeInterfaceSocketVectorDirection2D.init_socket") - [`NodeTreeInterfaceSocketVectorDirection4D.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorDirection4D.md#bpy.types.NodeTreeInterfaceSocketVectorDirection4D.from_socket "bpy.types.NodeTreeInterfaceSocketVectorDirection4D.from_socket") - [`NodeTreeInterfaceSocketVectorDirection4D.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorDirection4D.md#bpy.types.NodeTreeInterfaceSocketVectorDirection4D.init_socket "bpy.types.NodeTreeInterfaceSocketVectorDirection4D.init_socket") - [`NodeTreeInterfaceSocketVectorEuler.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorEuler.md#bpy.types.NodeTreeInterfaceSocketVectorEuler.from_socket "bpy.types.NodeTreeInterfaceSocketVectorEuler.from_socket") - [`NodeTreeInterfaceSocketVectorEuler.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorEuler.md#bpy.types.NodeTreeInterfaceSocketVectorEuler.init_socket "bpy.types.NodeTreeInterfaceSocketVectorEuler.init_socket") - [`NodeTreeInterfaceSocketVectorEuler2D.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorEuler2D.md#bpy.types.NodeTreeInterfaceSocketVectorEuler2D.from_socket "bpy.types.NodeTreeInterfaceSocketVectorEuler2D.from_socket") - [`NodeTreeInterfaceSocketVectorEuler2D.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorEuler2D.md#bpy.types.NodeTreeInterfaceSocketVectorEuler2D.init_socket "bpy.types.NodeTreeInterfaceSocketVectorEuler2D.init_socket") - [`NodeTreeInterfaceSocketVectorEuler4D.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorEuler4D.md#bpy.types.NodeTreeInterfaceSocketVectorEuler4D.from_socket "bpy.types.NodeTreeInterfaceSocketVectorEuler4D.from_socket") - [`NodeTreeInterfaceSocketVectorEuler4D.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorEuler4D.md#bpy.types.NodeTreeInterfaceSocketVectorEuler4D.init_socket "bpy.types.NodeTreeInterfaceSocketVectorEuler4D.init_socket") - [`NodeTreeInterfaceSocketVectorFactor.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorFactor.md#bpy.types.NodeTreeInterfaceSocketVectorFactor.from_socket "bpy.types.NodeTreeInterfaceSocketVectorFactor.from_socket") - [`NodeTreeInterfaceSocketVectorFactor.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorFactor.md#bpy.types.NodeTreeInterfaceSocketVectorFactor.init_socket "bpy.types.NodeTreeInterfaceSocketVectorFactor.init_socket") - [`NodeTreeInterfaceSocketVectorFactor2D.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorFactor2D.md#bpy.types.NodeTreeInterfaceSocketVectorFactor2D.from_socket "bpy.types.NodeTreeInterfaceSocketVectorFactor2D.from_socket") - [`NodeTreeInterfaceSocketVectorFactor2D.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorFactor2D.md#bpy.types.NodeTreeInterfaceSocketVectorFactor2D.init_socket "bpy.types.NodeTreeInterfaceSocketVectorFactor2D.init_socket") - [`NodeTreeInterfaceSocketVectorFactor4D.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorFactor4D.md#bpy.types.NodeTreeInterfaceSocketVectorFactor4D.from_socket "bpy.types.NodeTreeInterfaceSocketVectorFactor4D.from_socket") - [`NodeTreeInterfaceSocketVectorFactor4D.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorFactor4D.md#bpy.types.NodeTreeInterfaceSocketVectorFactor4D.init_socket "bpy.types.NodeTreeInterfaceSocketVectorFactor4D.init_socket") - [`NodeTreeInterfaceSocketVectorPercentage.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorPercentage.md#bpy.types.NodeTreeInterfaceSocketVectorPercentage.from_socket "bpy.types.NodeTreeInterfaceSocketVectorPercentage.from_socket") - [`NodeTreeInterfaceSocketVectorPercentage.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorPercentage.md#bpy.types.NodeTreeInterfaceSocketVectorPercentage.init_socket "bpy.types.NodeTreeInterfaceSocketVectorPercentage.init_socket") - [`NodeTreeInterfaceSocketVectorPercentage2D.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorPercentage2D.md#bpy.types.NodeTreeInterfaceSocketVectorPercentage2D.from_socket "bpy.types.NodeTreeInterfaceSocketVectorPercentage2D.from_socket") - [`NodeTreeInterfaceSocketVectorPercentage2D.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorPercentage2D.md#bpy.types.NodeTreeInterfaceSocketVectorPercentage2D.init_socket "bpy.types.NodeTreeInterfaceSocketVectorPercentage2D.init_socket") - [`NodeTreeInterfaceSocketVectorPercentage4D.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorPercentage4D.md#bpy.types.NodeTreeInterfaceSocketVectorPercentage4D.from_socket "bpy.types.NodeTreeInterfaceSocketVectorPercentage4D.from_socket") - [`NodeTreeInterfaceSocketVectorPercentage4D.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorPercentage4D.md#bpy.types.NodeTreeInterfaceSocketVectorPercentage4D.init_socket "bpy.types.NodeTreeInterfaceSocketVectorPercentage4D.init_socket") - [`NodeTreeInterfaceSocketVectorPixel.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorPixel.md#bpy.types.NodeTreeInterfaceSocketVectorPixel.from_socket "bpy.types.NodeTreeInterfaceSocketVectorPixel.from_socket") - [`NodeTreeInterfaceSocketVectorPixel.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorPixel.md#bpy.types.NodeTreeInterfaceSocketVectorPixel.init_socket "bpy.types.NodeTreeInterfaceSocketVectorPixel.init_socket") - [`NodeTreeInterfaceSocketVectorPixel2D.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorPixel2D.md#bpy.types.NodeTreeInterfaceSocketVectorPixel2D.from_socket "bpy.types.NodeTreeInterfaceSocketVectorPixel2D.from_socket") - [`NodeTreeInterfaceSocketVectorPixel2D.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorPixel2D.md#bpy.types.NodeTreeInterfaceSocketVectorPixel2D.init_socket "bpy.types.NodeTreeInterfaceSocketVectorPixel2D.init_socket") - [`NodeTreeInterfaceSocketVectorPixel4D.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorPixel4D.md#bpy.types.NodeTreeInterfaceSocketVectorPixel4D.from_socket "bpy.types.NodeTreeInterfaceSocketVectorPixel4D.from_socket") - [`NodeTreeInterfaceSocketVectorPixel4D.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorPixel4D.md#bpy.types.NodeTreeInterfaceSocketVectorPixel4D.init_socket "bpy.types.NodeTreeInterfaceSocketVectorPixel4D.init_socket") - [`NodeTreeInterfaceSocketVectorTranslation.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorTranslation.md#bpy.types.NodeTreeInterfaceSocketVectorTranslation.from_socket "bpy.types.NodeTreeInterfaceSocketVectorTranslation.from_socket") - [`NodeTreeInterfaceSocketVectorTranslation.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorTranslation.md#bpy.types.NodeTreeInterfaceSocketVectorTranslation.init_socket "bpy.types.NodeTreeInterfaceSocketVectorTranslation.init_socket") - [`NodeTreeInterfaceSocketVectorTranslation2D.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorTranslation2D.md#bpy.types.NodeTreeInterfaceSocketVectorTranslation2D.from_socket "bpy.types.NodeTreeInterfaceSocketVectorTranslation2D.from_socket") - [`NodeTreeInterfaceSocketVectorTranslation2D.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorTranslation2D.md#bpy.types.NodeTreeInterfaceSocketVectorTranslation2D.init_socket "bpy.types.NodeTreeInterfaceSocketVectorTranslation2D.init_socket") - [`NodeTreeInterfaceSocketVectorTranslation4D.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorTranslation4D.md#bpy.types.NodeTreeInterfaceSocketVectorTranslation4D.from_socket "bpy.types.NodeTreeInterfaceSocketVectorTranslation4D.from_socket") - [`NodeTreeInterfaceSocketVectorTranslation4D.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorTranslation4D.md#bpy.types.NodeTreeInterfaceSocketVectorTranslation4D.init_socket "bpy.types.NodeTreeInterfaceSocketVectorTranslation4D.init_socket") - [`NodeTreeInterfaceSocketVectorVelocity.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorVelocity.md#bpy.types.NodeTreeInterfaceSocketVectorVelocity.from_socket "bpy.types.NodeTreeInterfaceSocketVectorVelocity.from_socket") - [`NodeTreeInterfaceSocketVectorVelocity.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorVelocity.md#bpy.types.NodeTreeInterfaceSocketVectorVelocity.init_socket "bpy.types.NodeTreeInterfaceSocketVectorVelocity.init_socket") - [`NodeTreeInterfaceSocketVectorVelocity2D.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorVelocity2D.md#bpy.types.NodeTreeInterfaceSocketVectorVelocity2D.from_socket "bpy.types.NodeTreeInterfaceSocketVectorVelocity2D.from_socket") - [`NodeTreeInterfaceSocketVectorVelocity2D.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorVelocity2D.md#bpy.types.NodeTreeInterfaceSocketVectorVelocity2D.init_socket "bpy.types.NodeTreeInterfaceSocketVectorVelocity2D.init_socket") - [`NodeTreeInterfaceSocketVectorVelocity4D.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorVelocity4D.md#bpy.types.NodeTreeInterfaceSocketVectorVelocity4D.from_socket "bpy.types.NodeTreeInterfaceSocketVectorVelocity4D.from_socket") - [`NodeTreeInterfaceSocketVectorVelocity4D.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorVelocity4D.md#bpy.types.NodeTreeInterfaceSocketVectorVelocity4D.init_socket "bpy.types.NodeTreeInterfaceSocketVectorVelocity4D.init_socket") - [`NodeTreeInterfaceSocketVectorXYZ.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorXYZ.md#bpy.types.NodeTreeInterfaceSocketVectorXYZ.from_socket "bpy.types.NodeTreeInterfaceSocketVectorXYZ.from_socket") - [`NodeTreeInterfaceSocketVectorXYZ.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorXYZ.md#bpy.types.NodeTreeInterfaceSocketVectorXYZ.init_socket "bpy.types.NodeTreeInterfaceSocketVectorXYZ.init_socket") - [`NodeTreeInterfaceSocketVectorXYZ2D.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorXYZ2D.md#bpy.types.NodeTreeInterfaceSocketVectorXYZ2D.from_socket "bpy.types.NodeTreeInterfaceSocketVectorXYZ2D.from_socket") - [`NodeTreeInterfaceSocketVectorXYZ2D.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorXYZ2D.md#bpy.types.NodeTreeInterfaceSocketVectorXYZ2D.init_socket "bpy.types.NodeTreeInterfaceSocketVectorXYZ2D.init_socket") - [`NodeTreeInterfaceSocketVectorXYZ4D.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorXYZ4D.md#bpy.types.NodeTreeInterfaceSocketVectorXYZ4D.from_socket "bpy.types.NodeTreeInterfaceSocketVectorXYZ4D.from_socket") - [`NodeTreeInterfaceSocketVectorXYZ4D.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorXYZ4D.md#bpy.types.NodeTreeInterfaceSocketVectorXYZ4D.init_socket "bpy.types.NodeTreeInterfaceSocketVectorXYZ4D.init_socket") - [`Nodes.active`](bpy.types.Nodes.md#bpy.types.Nodes.active "bpy.types.Nodes.active") - [`Nodes.new`](bpy.types.Nodes.md#bpy.types.Nodes.new "bpy.types.Nodes.new") - [`Nodes.remove`](bpy.types.Nodes.md#bpy.types.Nodes.remove "bpy.types.Nodes.remove") - [`NodesModifierBake.node`](bpy.types.NodesModifierBake.md#bpy.types.NodesModifierBake.node "bpy.types.NodesModifierBake.node") - [`RenderEngine.update_script_node`](bpy.types.RenderEngine.md#bpy.types.RenderEngine.update_script_node "bpy.types.RenderEngine.update_script_node") - [`SpaceNodeEditorPath.append`](bpy.types.SpaceNodeEditorPath.md#bpy.types.SpaceNodeEditorPath.append "bpy.types.SpaceNodeEditorPath.append") - [`UILayout.template_node_inputs`](bpy.types.UILayout.md#bpy.types.UILayout.template_node_inputs "bpy.types.UILayout.template_node_inputs") - [`UILayout.template_node_link`](bpy.types.UILayout.md#bpy.types.UILayout.template_node_link "bpy.types.UILayout.template_node_link") - [`UILayout.template_node_view`](bpy.types.UILayout.md#bpy.types.UILayout.template_node_view "bpy.types.UILayout.template_node_view") |
