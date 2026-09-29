<!-- source: Blender Python API reference 5.2 / bpy.types.NodeSocket.html -->

<a id="nodesocket-bpy-struct"></a>

# NodeSocket(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

Subclasses

- [NodeSocketStandard(NodeSocket)](bpy.types.NodeSocketStandard.md)

<a id="bpy.types.NodeSocket"></a>

### class bpy.types.NodeSocket(bpy_struct)

Input or output socket of a node

<a id="bpy.types.NodeSocket.bl_idname"></a>

#### bpy.types.NodeSocket.bl_idname

(default “”, never None)

**Type:**

str

<a id="bpy.types.NodeSocket.bl_label"></a>

#### bpy.types.NodeSocket.bl_label

Label to display for the socket type in the UI (default “”, never None)

**Type:**

str

<a id="bpy.types.NodeSocket.bl_subtype_label"></a>

#### bpy.types.NodeSocket.bl_subtype_label

Label to display for the socket subtype in the UI (default “”, never None)

**Type:**

str

<a id="bpy.types.NodeSocket.description"></a>

#### bpy.types.NodeSocket.description

Socket tooltip (default “”, never None)

**Type:**

str

<a id="bpy.types.NodeSocket.display_shape"></a>

#### bpy.types.NodeSocket.display_shape

Socket shape (default `'CIRCLE'`)

**Type:**

Literal[‘CIRCLE’, ‘SQUARE’, ‘DIAMOND’, ‘CIRCLE_DOT’, ‘SQUARE_DOT’, ‘DIAMOND_DOT’, ‘LINE’, ‘VOLUME_GRID’, ‘LIST’]

<a id="bpy.types.NodeSocket.enabled"></a>

#### bpy.types.NodeSocket.enabled

Enable the socket (default True)

**Type:**

bool

<a id="bpy.types.NodeSocket.hide"></a>

#### bpy.types.NodeSocket.hide

Hide the socket (default False)

**Type:**

bool

<a id="bpy.types.NodeSocket.hide_value"></a>

#### bpy.types.NodeSocket.hide_value

Hide the socket input value (default False)

**Type:**

bool

<a id="bpy.types.NodeSocket.identifier"></a>

#### bpy.types.NodeSocket.identifier

Unique identifier for mapping sockets (default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.NodeSocket.inferred_structure_type"></a>

#### bpy.types.NodeSocket.inferred_structure_type

Best known structure type of the socket. This may not match the socket shape, e.g. for unlinked input sockets (default `'AUTO'`, readonly)

**Type:**

Literal[[Node Socket Structure Type Items](bpy_types_enum_items/node_socket_structure_type_items.md#rna-enum-node-socket-structure-type-items)]

<a id="bpy.types.NodeSocket.is_icon_visible"></a>

#### bpy.types.NodeSocket.is_icon_visible

Socket is drawn as interactive icon in the node editor (default False, readonly)

**Type:**

bool

<a id="bpy.types.NodeSocket.is_inactive"></a>

#### bpy.types.NodeSocket.is_inactive

Socket is grayed out because it has been detected to not have any effect on the output (default False, readonly)

**Type:**

bool

<a id="bpy.types.NodeSocket.is_linked"></a>

#### bpy.types.NodeSocket.is_linked

True if the socket is connected (default False, readonly)

**Type:**

bool

<a id="bpy.types.NodeSocket.is_multi_input"></a>

#### bpy.types.NodeSocket.is_multi_input

True if the socket can accept multiple ordered input links (default False, readonly)

**Type:**

bool

<a id="bpy.types.NodeSocket.is_output"></a>

#### bpy.types.NodeSocket.is_output

True if the socket is an output, otherwise input (default False, readonly)

**Type:**

bool

<a id="bpy.types.NodeSocket.is_unavailable"></a>

#### bpy.types.NodeSocket.is_unavailable

True if the socket is unavailable (default False, readonly)

**Type:**

bool

<a id="bpy.types.NodeSocket.label"></a>

#### bpy.types.NodeSocket.label

Custom dynamic defined UI label for the socket. Can be translated if translation is enabled in the preferences (default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.NodeSocket.link_limit"></a>

#### bpy.types.NodeSocket.link_limit

Max number of links allowed for this socket (in [1, 4095], default 0)

**Type:**

int

<a id="bpy.types.NodeSocket.name"></a>

#### bpy.types.NodeSocket.name

Socket name (default “”, never None)

**Type:**

str

<a id="bpy.types.NodeSocket.node"></a>

#### bpy.types.NodeSocket.node

Node owning this socket (readonly)

**Type:**

[`Node`](bpy.types.Node.md#bpy.types.Node "bpy.types.Node") | None

<a id="bpy.types.NodeSocket.pin_gizmo"></a>

#### bpy.types.NodeSocket.pin_gizmo

Keep gizmo visible even when the node is not selected (default False)

**Type:**

bool

<a id="bpy.types.NodeSocket.select"></a>

#### bpy.types.NodeSocket.select

True if the socket is selected (default False, readonly)

**Type:**

bool

<a id="bpy.types.NodeSocket.show_expanded"></a>

#### bpy.types.NodeSocket.show_expanded

Socket links are expanded in the user interface (default True)

**Type:**

bool

<a id="bpy.types.NodeSocket.type"></a>

#### bpy.types.NodeSocket.type

Data type (default `'VALUE'`)

**Type:**

Literal[[Node Socket Type Items](bpy_types_enum_items/node_socket_type_items.md#rna-enum-node-socket-type-items)]

<a id="bpy.types.NodeSocket.links"></a>

#### bpy.types.NodeSocket.links

List of node links from or to this socket.

**Type:**

[`NodeLinks`](bpy.types.NodeLinks.md#bpy.types.NodeLinks "bpy.types.NodeLinks")

> **Note:**
>
> Takes `O(len(nodetree.links))` time.

(readonly)

<a id="bpy.types.NodeSocket.bl_system_properties_get"></a>

#### bpy.types.NodeSocket.bl_system_properties_get(*, do_create=False)

DEBUG ONLY. Internal access to runtime-defined RNA data storage, intended solely for testing and debugging purposes. Do not access it in regular scripting work, and in particular, do not assume that it contains writable data

**Parameters:**

**do_create** (bool) – Ensure that system properties are created if they do not exist yet (optional)

**Returns:**

The system properties root container, or None if there are no system properties stored in this data yet, and its creation was not requested

**Return type:**

[`PropertyGroup`](bpy.types.PropertyGroup.md#bpy.types.PropertyGroup "bpy.types.PropertyGroup")

<a id="bpy.types.NodeSocket.draw"></a>

#### bpy.types.NodeSocket.draw(context, layout, node, text)

Draw socket

**Parameters:**

- **context** ([`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context") | None) – (never None)
- **layout** ([`UILayout`](bpy.types.UILayout.md#bpy.types.UILayout "bpy.types.UILayout") | None) – Layout, Layout in the UI (never None)
- **node** ([`Node`](bpy.types.Node.md#bpy.types.Node "bpy.types.Node") | None) – Node, Node the socket belongs to (never None)
- **text** (str) – Text, Text label to draw alongside properties (never None)

<a id="bpy.types.NodeSocket.draw_color"></a>

#### bpy.types.NodeSocket.draw_color(context, node)

Color of the socket icon

**Parameters:**

- **context** ([`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context") | None) – (never None)
- **node** ([`Node`](bpy.types.Node.md#bpy.types.Node "bpy.types.Node") | None) – Node, Node the socket belongs to (never None)

**Returns:**

Color, (array of 4 items, in [0, 1])

**Return type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.NodeSocket.draw_color_simple"></a>

#### classmethod bpy.types.NodeSocket.draw_color_simple()

Color of the socket icon. Used to draw sockets in places where the socket does not belong to a node, like the node interface panel. Also used to draw node sockets if draw_color is not defined.

**Returns:**

Color, (array of 4 items, in [0, 1])

**Return type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.NodeSocket.bl_rna_get_subclass"></a>

#### classmethod bpy.types.NodeSocket.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.NodeSocket.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.NodeSocket.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([type](#bpy.types.NodeSocket.type "bpy.types.NodeSocket.type") | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

[type](#bpy.types.NodeSocket.type "bpy.types.NodeSocket.type")

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
| - [`Node.inputs`](bpy.types.Node.md#bpy.types.Node.inputs "bpy.types.Node.inputs") - [`Node.outputs`](bpy.types.Node.md#bpy.types.Node.outputs "bpy.types.Node.outputs") - [`NodeInputs.new`](bpy.types.NodeInputs.md#bpy.types.NodeInputs.new "bpy.types.NodeInputs.new") - [`NodeInputs.remove`](bpy.types.NodeInputs.md#bpy.types.NodeInputs.remove "bpy.types.NodeInputs.remove") - [`NodeLink.from_socket`](bpy.types.NodeLink.md#bpy.types.NodeLink.from_socket "bpy.types.NodeLink.from_socket") - [`NodeLink.to_socket`](bpy.types.NodeLink.md#bpy.types.NodeLink.to_socket "bpy.types.NodeLink.to_socket") - [`NodeLinks.new`](bpy.types.NodeLinks.md#bpy.types.NodeLinks.new "bpy.types.NodeLinks.new") - [`NodeLinks.new`](bpy.types.NodeLinks.md#bpy.types.NodeLinks.new "bpy.types.NodeLinks.new") - [`NodeOutputs.new`](bpy.types.NodeOutputs.md#bpy.types.NodeOutputs.new "bpy.types.NodeOutputs.new") - [`NodeOutputs.remove`](bpy.types.NodeOutputs.md#bpy.types.NodeOutputs.remove "bpy.types.NodeOutputs.remove") - [`NodeTreeInterfaceSocket.from_socket`](bpy.types.NodeTreeInterfaceSocket.md#bpy.types.NodeTreeInterfaceSocket.from_socket "bpy.types.NodeTreeInterfaceSocket.from_socket") - [`NodeTreeInterfaceSocket.init_socket`](bpy.types.NodeTreeInterfaceSocket.md#bpy.types.NodeTreeInterfaceSocket.init_socket "bpy.types.NodeTreeInterfaceSocket.init_socket") - [`NodeTreeInterfaceSocketBool.from_socket`](bpy.types.NodeTreeInterfaceSocketBool.md#bpy.types.NodeTreeInterfaceSocketBool.from_socket "bpy.types.NodeTreeInterfaceSocketBool.from_socket") - [`NodeTreeInterfaceSocketBool.init_socket`](bpy.types.NodeTreeInterfaceSocketBool.md#bpy.types.NodeTreeInterfaceSocketBool.init_socket "bpy.types.NodeTreeInterfaceSocketBool.init_socket") - [`NodeTreeInterfaceSocketBundle.from_socket`](bpy.types.NodeTreeInterfaceSocketBundle.md#bpy.types.NodeTreeInterfaceSocketBundle.from_socket "bpy.types.NodeTreeInterfaceSocketBundle.from_socket") - [`NodeTreeInterfaceSocketBundle.init_socket`](bpy.types.NodeTreeInterfaceSocketBundle.md#bpy.types.NodeTreeInterfaceSocketBundle.init_socket "bpy.types.NodeTreeInterfaceSocketBundle.init_socket") - [`NodeTreeInterfaceSocketClosure.from_socket`](bpy.types.NodeTreeInterfaceSocketClosure.md#bpy.types.NodeTreeInterfaceSocketClosure.from_socket "bpy.types.NodeTreeInterfaceSocketClosure.from_socket") - [`NodeTreeInterfaceSocketClosure.init_socket`](bpy.types.NodeTreeInterfaceSocketClosure.md#bpy.types.NodeTreeInterfaceSocketClosure.init_socket "bpy.types.NodeTreeInterfaceSocketClosure.init_socket") - [`NodeTreeInterfaceSocketCollection.from_socket`](bpy.types.NodeTreeInterfaceSocketCollection.md#bpy.types.NodeTreeInterfaceSocketCollection.from_socket "bpy.types.NodeTreeInterfaceSocketCollection.from_socket") - [`NodeTreeInterfaceSocketCollection.init_socket`](bpy.types.NodeTreeInterfaceSocketCollection.md#bpy.types.NodeTreeInterfaceSocketCollection.init_socket "bpy.types.NodeTreeInterfaceSocketCollection.init_socket") - [`NodeTreeInterfaceSocketColor.from_socket`](bpy.types.NodeTreeInterfaceSocketColor.md#bpy.types.NodeTreeInterfaceSocketColor.from_socket "bpy.types.NodeTreeInterfaceSocketColor.from_socket") - [`NodeTreeInterfaceSocketColor.init_socket`](bpy.types.NodeTreeInterfaceSocketColor.md#bpy.types.NodeTreeInterfaceSocketColor.init_socket "bpy.types.NodeTreeInterfaceSocketColor.init_socket") - [`NodeTreeInterfaceSocketFloat.from_socket`](bpy.types.NodeTreeInterfaceSocketFloat.md#bpy.types.NodeTreeInterfaceSocketFloat.from_socket "bpy.types.NodeTreeInterfaceSocketFloat.from_socket") - [`NodeTreeInterfaceSocketFloat.init_socket`](bpy.types.NodeTreeInterfaceSocketFloat.md#bpy.types.NodeTreeInterfaceSocketFloat.init_socket "bpy.types.NodeTreeInterfaceSocketFloat.init_socket") - [`NodeTreeInterfaceSocketFloatAngle.from_socket`](bpy.types.NodeTreeInterfaceSocketFloatAngle.md#bpy.types.NodeTreeInterfaceSocketFloatAngle.from_socket "bpy.types.NodeTreeInterfaceSocketFloatAngle.from_socket") - [`NodeTreeInterfaceSocketFloatAngle.init_socket`](bpy.types.NodeTreeInterfaceSocketFloatAngle.md#bpy.types.NodeTreeInterfaceSocketFloatAngle.init_socket "bpy.types.NodeTreeInterfaceSocketFloatAngle.init_socket") - [`NodeTreeInterfaceSocketFloatColorTemperature.from_socket`](bpy.types.NodeTreeInterfaceSocketFloatColorTemperature.md#bpy.types.NodeTreeInterfaceSocketFloatColorTemperature.from_socket "bpy.types.NodeTreeInterfaceSocketFloatColorTemperature.from_socket") - [`NodeTreeInterfaceSocketFloatColorTemperature.init_socket`](bpy.types.NodeTreeInterfaceSocketFloatColorTemperature.md#bpy.types.NodeTreeInterfaceSocketFloatColorTemperature.init_socket "bpy.types.NodeTreeInterfaceSocketFloatColorTemperature.init_socket") - [`NodeTreeInterfaceSocketFloatDistance.from_socket`](bpy.types.NodeTreeInterfaceSocketFloatDistance.md#bpy.types.NodeTreeInterfaceSocketFloatDistance.from_socket "bpy.types.NodeTreeInterfaceSocketFloatDistance.from_socket") - [`NodeTreeInterfaceSocketFloatDistance.init_socket`](bpy.types.NodeTreeInterfaceSocketFloatDistance.md#bpy.types.NodeTreeInterfaceSocketFloatDistance.init_socket "bpy.types.NodeTreeInterfaceSocketFloatDistance.init_socket") - [`NodeTreeInterfaceSocketFloatFactor.from_socket`](bpy.types.NodeTreeInterfaceSocketFloatFactor.md#bpy.types.NodeTreeInterfaceSocketFloatFactor.from_socket "bpy.types.NodeTreeInterfaceSocketFloatFactor.from_socket") - [`NodeTreeInterfaceSocketFloatFactor.init_socket`](bpy.types.NodeTreeInterfaceSocketFloatFactor.md#bpy.types.NodeTreeInterfaceSocketFloatFactor.init_socket "bpy.types.NodeTreeInterfaceSocketFloatFactor.init_socket") - [`NodeTreeInterfaceSocketFloatFrequency.from_socket`](bpy.types.NodeTreeInterfaceSocketFloatFrequency.md#bpy.types.NodeTreeInterfaceSocketFloatFrequency.from_socket "bpy.types.NodeTreeInterfaceSocketFloatFrequency.from_socket") - [`NodeTreeInterfaceSocketFloatFrequency.init_socket`](bpy.types.NodeTreeInterfaceSocketFloatFrequency.md#bpy.types.NodeTreeInterfaceSocketFloatFrequency.init_socket "bpy.types.NodeTreeInterfaceSocketFloatFrequency.init_socket") - [`NodeTreeInterfaceSocketFloatMass.from_socket`](bpy.types.NodeTreeInterfaceSocketFloatMass.md#bpy.types.NodeTreeInterfaceSocketFloatMass.from_socket "bpy.types.NodeTreeInterfaceSocketFloatMass.from_socket") - [`NodeTreeInterfaceSocketFloatMass.init_socket`](bpy.types.NodeTreeInterfaceSocketFloatMass.md#bpy.types.NodeTreeInterfaceSocketFloatMass.init_socket "bpy.types.NodeTreeInterfaceSocketFloatMass.init_socket") - [`NodeTreeInterfaceSocketFloatPercentage.from_socket`](bpy.types.NodeTreeInterfaceSocketFloatPercentage.md#bpy.types.NodeTreeInterfaceSocketFloatPercentage.from_socket "bpy.types.NodeTreeInterfaceSocketFloatPercentage.from_socket") - [`NodeTreeInterfaceSocketFloatPercentage.init_socket`](bpy.types.NodeTreeInterfaceSocketFloatPercentage.md#bpy.types.NodeTreeInterfaceSocketFloatPercentage.init_socket "bpy.types.NodeTreeInterfaceSocketFloatPercentage.init_socket") - [`NodeTreeInterfaceSocketFloatPixel.from_socket`](bpy.types.NodeTreeInterfaceSocketFloatPixel.md#bpy.types.NodeTreeInterfaceSocketFloatPixel.from_socket "bpy.types.NodeTreeInterfaceSocketFloatPixel.from_socket") - [`NodeTreeInterfaceSocketFloatPixel.init_socket`](bpy.types.NodeTreeInterfaceSocketFloatPixel.md#bpy.types.NodeTreeInterfaceSocketFloatPixel.init_socket "bpy.types.NodeTreeInterfaceSocketFloatPixel.init_socket") - [`NodeTreeInterfaceSocketFloatTime.from_socket`](bpy.types.NodeTreeInterfaceSocketFloatTime.md#bpy.types.NodeTreeInterfaceSocketFloatTime.from_socket "bpy.types.NodeTreeInterfaceSocketFloatTime.from_socket") - [`NodeTreeInterfaceSocketFloatTime.init_socket`](bpy.types.NodeTreeInterfaceSocketFloatTime.md#bpy.types.NodeTreeInterfaceSocketFloatTime.init_socket "bpy.types.NodeTreeInterfaceSocketFloatTime.init_socket") - [`NodeTreeInterfaceSocketFloatTimeAbsolute.from_socket`](bpy.types.NodeTreeInterfaceSocketFloatTimeAbsolute.md#bpy.types.NodeTreeInterfaceSocketFloatTimeAbsolute.from_socket "bpy.types.NodeTreeInterfaceSocketFloatTimeAbsolute.from_socket") - [`NodeTreeInterfaceSocketFloatTimeAbsolute.init_socket`](bpy.types.NodeTreeInterfaceSocketFloatTimeAbsolute.md#bpy.types.NodeTreeInterfaceSocketFloatTimeAbsolute.init_socket "bpy.types.NodeTreeInterfaceSocketFloatTimeAbsolute.init_socket") - [`NodeTreeInterfaceSocketFloatUnsigned.from_socket`](bpy.types.NodeTreeInterfaceSocketFloatUnsigned.md#bpy.types.NodeTreeInterfaceSocketFloatUnsigned.from_socket "bpy.types.NodeTreeInterfaceSocketFloatUnsigned.from_socket") - [`NodeTreeInterfaceSocketFloatUnsigned.init_socket`](bpy.types.NodeTreeInterfaceSocketFloatUnsigned.md#bpy.types.NodeTreeInterfaceSocketFloatUnsigned.init_socket "bpy.types.NodeTreeInterfaceSocketFloatUnsigned.init_socket") - [`NodeTreeInterfaceSocketFloatWavelength.from_socket`](bpy.types.NodeTreeInterfaceSocketFloatWavelength.md#bpy.types.NodeTreeInterfaceSocketFloatWavelength.from_socket "bpy.types.NodeTreeInterfaceSocketFloatWavelength.from_socket") - [`NodeTreeInterfaceSocketFloatWavelength.init_socket`](bpy.types.NodeTreeInterfaceSocketFloatWavelength.md#bpy.types.NodeTreeInterfaceSocketFloatWavelength.init_socket "bpy.types.NodeTreeInterfaceSocketFloatWavelength.init_socket") - [`NodeTreeInterfaceSocketGeometry.from_socket`](bpy.types.NodeTreeInterfaceSocketGeometry.md#bpy.types.NodeTreeInterfaceSocketGeometry.from_socket "bpy.types.NodeTreeInterfaceSocketGeometry.from_socket") - [`NodeTreeInterfaceSocketGeometry.init_socket`](bpy.types.NodeTreeInterfaceSocketGeometry.md#bpy.types.NodeTreeInterfaceSocketGeometry.init_socket "bpy.types.NodeTreeInterfaceSocketGeometry.init_socket") - [`NodeTreeInterfaceSocketImage.from_socket`](bpy.types.NodeTreeInterfaceSocketImage.md#bpy.types.NodeTreeInterfaceSocketImage.from_socket "bpy.types.NodeTreeInterfaceSocketImage.from_socket") - [`NodeTreeInterfaceSocketImage.init_socket`](bpy.types.NodeTreeInterfaceSocketImage.md#bpy.types.NodeTreeInterfaceSocketImage.init_socket "bpy.types.NodeTreeInterfaceSocketImage.init_socket") - [`NodeTreeInterfaceSocketInt.from_socket`](bpy.types.NodeTreeInterfaceSocketInt.md#bpy.types.NodeTreeInterfaceSocketInt.from_socket "bpy.types.NodeTreeInterfaceSocketInt.from_socket") - [`NodeTreeInterfaceSocketInt.init_socket`](bpy.types.NodeTreeInterfaceSocketInt.md#bpy.types.NodeTreeInterfaceSocketInt.init_socket "bpy.types.NodeTreeInterfaceSocketInt.init_socket") - [`NodeTreeInterfaceSocketIntFactor.from_socket`](bpy.types.NodeTreeInterfaceSocketIntFactor.md#bpy.types.NodeTreeInterfaceSocketIntFactor.from_socket "bpy.types.NodeTreeInterfaceSocketIntFactor.from_socket") - [`NodeTreeInterfaceSocketIntFactor.init_socket`](bpy.types.NodeTreeInterfaceSocketIntFactor.md#bpy.types.NodeTreeInterfaceSocketIntFactor.init_socket "bpy.types.NodeTreeInterfaceSocketIntFactor.init_socket") - [`NodeTreeInterfaceSocketIntPercentage.from_socket`](bpy.types.NodeTreeInterfaceSocketIntPercentage.md#bpy.types.NodeTreeInterfaceSocketIntPercentage.from_socket "bpy.types.NodeTreeInterfaceSocketIntPercentage.from_socket") - [`NodeTreeInterfaceSocketIntPercentage.init_socket`](bpy.types.NodeTreeInterfaceSocketIntPercentage.md#bpy.types.NodeTreeInterfaceSocketIntPercentage.init_socket "bpy.types.NodeTreeInterfaceSocketIntPercentage.init_socket") - [`NodeTreeInterfaceSocketIntPixel.from_socket`](bpy.types.NodeTreeInterfaceSocketIntPixel.md#bpy.types.NodeTreeInterfaceSocketIntPixel.from_socket "bpy.types.NodeTreeInterfaceSocketIntPixel.from_socket") - [`NodeTreeInterfaceSocketIntPixel.init_socket`](bpy.types.NodeTreeInterfaceSocketIntPixel.md#bpy.types.NodeTreeInterfaceSocketIntPixel.init_socket "bpy.types.NodeTreeInterfaceSocketIntPixel.init_socket") - [`NodeTreeInterfaceSocketIntUnsigned.from_socket`](bpy.types.NodeTreeInterfaceSocketIntUnsigned.md#bpy.types.NodeTreeInterfaceSocketIntUnsigned.from_socket "bpy.types.NodeTreeInterfaceSocketIntUnsigned.from_socket") - [`NodeTreeInterfaceSocketIntUnsigned.init_socket`](bpy.types.NodeTreeInterfaceSocketIntUnsigned.md#bpy.types.NodeTreeInterfaceSocketIntUnsigned.init_socket "bpy.types.NodeTreeInterfaceSocketIntUnsigned.init_socket") - [`NodeTreeInterfaceSocketIntVector2D.from_socket`](bpy.types.NodeTreeInterfaceSocketIntVector2D.md#bpy.types.NodeTreeInterfaceSocketIntVector2D.from_socket "bpy.types.NodeTreeInterfaceSocketIntVector2D.from_socket") - [`NodeTreeInterfaceSocketIntVector2D.init_socket`](bpy.types.NodeTreeInterfaceSocketIntVector2D.md#bpy.types.NodeTreeInterfaceSocketIntVector2D.init_socket "bpy.types.NodeTreeInterfaceSocketIntVector2D.init_socket") - [`NodeTreeInterfaceSocketIntVector3D.from_socket`](bpy.types.NodeTreeInterfaceSocketIntVector3D.md#bpy.types.NodeTreeInterfaceSocketIntVector3D.from_socket "bpy.types.NodeTreeInterfaceSocketIntVector3D.from_socket") - [`NodeTreeInterfaceSocketIntVector3D.init_socket`](bpy.types.NodeTreeInterfaceSocketIntVector3D.md#bpy.types.NodeTreeInterfaceSocketIntVector3D.init_socket "bpy.types.NodeTreeInterfaceSocketIntVector3D.init_socket") - [`NodeTreeInterfaceSocketIntVectorFactor2D.from_socket`](bpy.types.NodeTreeInterfaceSocketIntVectorFactor2D.md#bpy.types.NodeTreeInterfaceSocketIntVectorFactor2D.from_socket "bpy.types.NodeTreeInterfaceSocketIntVectorFactor2D.from_socket") - [`NodeTreeInterfaceSocketIntVectorFactor2D.init_socket`](bpy.types.NodeTreeInterfaceSocketIntVectorFactor2D.md#bpy.types.NodeTreeInterfaceSocketIntVectorFactor2D.init_socket "bpy.types.NodeTreeInterfaceSocketIntVectorFactor2D.init_socket") - [`NodeTreeInterfaceSocketIntVectorFactor3D.from_socket`](bpy.types.NodeTreeInterfaceSocketIntVectorFactor3D.md#bpy.types.NodeTreeInterfaceSocketIntVectorFactor3D.from_socket "bpy.types.NodeTreeInterfaceSocketIntVectorFactor3D.from_socket") - [`NodeTreeInterfaceSocketIntVectorFactor3D.init_socket`](bpy.types.NodeTreeInterfaceSocketIntVectorFactor3D.md#bpy.types.NodeTreeInterfaceSocketIntVectorFactor3D.init_socket "bpy.types.NodeTreeInterfaceSocketIntVectorFactor3D.init_socket") - [`NodeTreeInterfaceSocketIntVectorPercentage2D.from_socket`](bpy.types.NodeTreeInterfaceSocketIntVectorPercentage2D.md#bpy.types.NodeTreeInterfaceSocketIntVectorPercentage2D.from_socket "bpy.types.NodeTreeInterfaceSocketIntVectorPercentage2D.from_socket") - [`NodeTreeInterfaceSocketIntVectorPercentage2D.init_socket`](bpy.types.NodeTreeInterfaceSocketIntVectorPercentage2D.md#bpy.types.NodeTreeInterfaceSocketIntVectorPercentage2D.init_socket "bpy.types.NodeTreeInterfaceSocketIntVectorPercentage2D.init_socket") - [`NodeTreeInterfaceSocketIntVectorPercentage3D.from_socket`](bpy.types.NodeTreeInterfaceSocketIntVectorPercentage3D.md#bpy.types.NodeTreeInterfaceSocketIntVectorPercentage3D.from_socket "bpy.types.NodeTreeInterfaceSocketIntVectorPercentage3D.from_socket") - [`NodeTreeInterfaceSocketIntVectorPercentage3D.init_socket`](bpy.types.NodeTreeInterfaceSocketIntVectorPercentage3D.md#bpy.types.NodeTreeInterfaceSocketIntVectorPercentage3D.init_socket "bpy.types.NodeTreeInterfaceSocketIntVectorPercentage3D.init_socket") - [`NodeTreeInterfaceSocketIntVectorPixel2D.from_socket`](bpy.types.NodeTreeInterfaceSocketIntVectorPixel2D.md#bpy.types.NodeTreeInterfaceSocketIntVectorPixel2D.from_socket "bpy.types.NodeTreeInterfaceSocketIntVectorPixel2D.from_socket") - [`NodeTreeInterfaceSocketIntVectorPixel2D.init_socket`](bpy.types.NodeTreeInterfaceSocketIntVectorPixel2D.md#bpy.types.NodeTreeInterfaceSocketIntVectorPixel2D.init_socket "bpy.types.NodeTreeInterfaceSocketIntVectorPixel2D.init_socket") - [`NodeTreeInterfaceSocketIntVectorPixel3D.from_socket`](bpy.types.NodeTreeInterfaceSocketIntVectorPixel3D.md#bpy.types.NodeTreeInterfaceSocketIntVectorPixel3D.from_socket "bpy.types.NodeTreeInterfaceSocketIntVectorPixel3D.from_socket") - [`NodeTreeInterfaceSocketIntVectorPixel3D.init_socket`](bpy.types.NodeTreeInterfaceSocketIntVectorPixel3D.md#bpy.types.NodeTreeInterfaceSocketIntVectorPixel3D.init_socket "bpy.types.NodeTreeInterfaceSocketIntVectorPixel3D.init_socket") - [`NodeTreeInterfaceSocketIntVectorUnsigned2D.from_socket`](bpy.types.NodeTreeInterfaceSocketIntVectorUnsigned2D.md#bpy.types.NodeTreeInterfaceSocketIntVectorUnsigned2D.from_socket "bpy.types.NodeTreeInterfaceSocketIntVectorUnsigned2D.from_socket") - [`NodeTreeInterfaceSocketIntVectorUnsigned2D.init_socket`](bpy.types.NodeTreeInterfaceSocketIntVectorUnsigned2D.md#bpy.types.NodeTreeInterfaceSocketIntVectorUnsigned2D.init_socket "bpy.types.NodeTreeInterfaceSocketIntVectorUnsigned2D.init_socket") - [`NodeTreeInterfaceSocketIntVectorUnsigned3D.from_socket`](bpy.types.NodeTreeInterfaceSocketIntVectorUnsigned3D.md#bpy.types.NodeTreeInterfaceSocketIntVectorUnsigned3D.from_socket "bpy.types.NodeTreeInterfaceSocketIntVectorUnsigned3D.from_socket") | - [`NodeTreeInterfaceSocketIntVectorUnsigned3D.init_socket`](bpy.types.NodeTreeInterfaceSocketIntVectorUnsigned3D.md#bpy.types.NodeTreeInterfaceSocketIntVectorUnsigned3D.init_socket "bpy.types.NodeTreeInterfaceSocketIntVectorUnsigned3D.init_socket") - [`NodeTreeInterfaceSocketMaterial.from_socket`](bpy.types.NodeTreeInterfaceSocketMaterial.md#bpy.types.NodeTreeInterfaceSocketMaterial.from_socket "bpy.types.NodeTreeInterfaceSocketMaterial.from_socket") - [`NodeTreeInterfaceSocketMaterial.init_socket`](bpy.types.NodeTreeInterfaceSocketMaterial.md#bpy.types.NodeTreeInterfaceSocketMaterial.init_socket "bpy.types.NodeTreeInterfaceSocketMaterial.init_socket") - [`NodeTreeInterfaceSocketMatrix.from_socket`](bpy.types.NodeTreeInterfaceSocketMatrix.md#bpy.types.NodeTreeInterfaceSocketMatrix.from_socket "bpy.types.NodeTreeInterfaceSocketMatrix.from_socket") - [`NodeTreeInterfaceSocketMatrix.init_socket`](bpy.types.NodeTreeInterfaceSocketMatrix.md#bpy.types.NodeTreeInterfaceSocketMatrix.init_socket "bpy.types.NodeTreeInterfaceSocketMatrix.init_socket") - [`NodeTreeInterfaceSocketMenu.from_socket`](bpy.types.NodeTreeInterfaceSocketMenu.md#bpy.types.NodeTreeInterfaceSocketMenu.from_socket "bpy.types.NodeTreeInterfaceSocketMenu.from_socket") - [`NodeTreeInterfaceSocketMenu.init_socket`](bpy.types.NodeTreeInterfaceSocketMenu.md#bpy.types.NodeTreeInterfaceSocketMenu.init_socket "bpy.types.NodeTreeInterfaceSocketMenu.init_socket") - [`NodeTreeInterfaceSocketObject.from_socket`](bpy.types.NodeTreeInterfaceSocketObject.md#bpy.types.NodeTreeInterfaceSocketObject.from_socket "bpy.types.NodeTreeInterfaceSocketObject.from_socket") - [`NodeTreeInterfaceSocketObject.init_socket`](bpy.types.NodeTreeInterfaceSocketObject.md#bpy.types.NodeTreeInterfaceSocketObject.init_socket "bpy.types.NodeTreeInterfaceSocketObject.init_socket") - [`NodeTreeInterfaceSocketRotation.from_socket`](bpy.types.NodeTreeInterfaceSocketRotation.md#bpy.types.NodeTreeInterfaceSocketRotation.from_socket "bpy.types.NodeTreeInterfaceSocketRotation.from_socket") - [`NodeTreeInterfaceSocketRotation.init_socket`](bpy.types.NodeTreeInterfaceSocketRotation.md#bpy.types.NodeTreeInterfaceSocketRotation.init_socket "bpy.types.NodeTreeInterfaceSocketRotation.init_socket") - [`NodeTreeInterfaceSocketShader.from_socket`](bpy.types.NodeTreeInterfaceSocketShader.md#bpy.types.NodeTreeInterfaceSocketShader.from_socket "bpy.types.NodeTreeInterfaceSocketShader.from_socket") - [`NodeTreeInterfaceSocketShader.init_socket`](bpy.types.NodeTreeInterfaceSocketShader.md#bpy.types.NodeTreeInterfaceSocketShader.init_socket "bpy.types.NodeTreeInterfaceSocketShader.init_socket") - [`NodeTreeInterfaceSocketString.from_socket`](bpy.types.NodeTreeInterfaceSocketString.md#bpy.types.NodeTreeInterfaceSocketString.from_socket "bpy.types.NodeTreeInterfaceSocketString.from_socket") - [`NodeTreeInterfaceSocketString.init_socket`](bpy.types.NodeTreeInterfaceSocketString.md#bpy.types.NodeTreeInterfaceSocketString.init_socket "bpy.types.NodeTreeInterfaceSocketString.init_socket") - [`NodeTreeInterfaceSocketStringFilePath.from_socket`](bpy.types.NodeTreeInterfaceSocketStringFilePath.md#bpy.types.NodeTreeInterfaceSocketStringFilePath.from_socket "bpy.types.NodeTreeInterfaceSocketStringFilePath.from_socket") - [`NodeTreeInterfaceSocketStringFilePath.init_socket`](bpy.types.NodeTreeInterfaceSocketStringFilePath.md#bpy.types.NodeTreeInterfaceSocketStringFilePath.init_socket "bpy.types.NodeTreeInterfaceSocketStringFilePath.init_socket") - [`NodeTreeInterfaceSocketTexture.from_socket`](bpy.types.NodeTreeInterfaceSocketTexture.md#bpy.types.NodeTreeInterfaceSocketTexture.from_socket "bpy.types.NodeTreeInterfaceSocketTexture.from_socket") - [`NodeTreeInterfaceSocketTexture.init_socket`](bpy.types.NodeTreeInterfaceSocketTexture.md#bpy.types.NodeTreeInterfaceSocketTexture.init_socket "bpy.types.NodeTreeInterfaceSocketTexture.init_socket") - [`NodeTreeInterfaceSocketVector.from_socket`](bpy.types.NodeTreeInterfaceSocketVector.md#bpy.types.NodeTreeInterfaceSocketVector.from_socket "bpy.types.NodeTreeInterfaceSocketVector.from_socket") - [`NodeTreeInterfaceSocketVector.init_socket`](bpy.types.NodeTreeInterfaceSocketVector.md#bpy.types.NodeTreeInterfaceSocketVector.init_socket "bpy.types.NodeTreeInterfaceSocketVector.init_socket") - [`NodeTreeInterfaceSocketVector2D.from_socket`](bpy.types.NodeTreeInterfaceSocketVector2D.md#bpy.types.NodeTreeInterfaceSocketVector2D.from_socket "bpy.types.NodeTreeInterfaceSocketVector2D.from_socket") - [`NodeTreeInterfaceSocketVector2D.init_socket`](bpy.types.NodeTreeInterfaceSocketVector2D.md#bpy.types.NodeTreeInterfaceSocketVector2D.init_socket "bpy.types.NodeTreeInterfaceSocketVector2D.init_socket") - [`NodeTreeInterfaceSocketVector4D.from_socket`](bpy.types.NodeTreeInterfaceSocketVector4D.md#bpy.types.NodeTreeInterfaceSocketVector4D.from_socket "bpy.types.NodeTreeInterfaceSocketVector4D.from_socket") - [`NodeTreeInterfaceSocketVector4D.init_socket`](bpy.types.NodeTreeInterfaceSocketVector4D.md#bpy.types.NodeTreeInterfaceSocketVector4D.init_socket "bpy.types.NodeTreeInterfaceSocketVector4D.init_socket") - [`NodeTreeInterfaceSocketVectorAcceleration.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorAcceleration.md#bpy.types.NodeTreeInterfaceSocketVectorAcceleration.from_socket "bpy.types.NodeTreeInterfaceSocketVectorAcceleration.from_socket") - [`NodeTreeInterfaceSocketVectorAcceleration.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorAcceleration.md#bpy.types.NodeTreeInterfaceSocketVectorAcceleration.init_socket "bpy.types.NodeTreeInterfaceSocketVectorAcceleration.init_socket") - [`NodeTreeInterfaceSocketVectorAcceleration2D.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorAcceleration2D.md#bpy.types.NodeTreeInterfaceSocketVectorAcceleration2D.from_socket "bpy.types.NodeTreeInterfaceSocketVectorAcceleration2D.from_socket") - [`NodeTreeInterfaceSocketVectorAcceleration2D.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorAcceleration2D.md#bpy.types.NodeTreeInterfaceSocketVectorAcceleration2D.init_socket "bpy.types.NodeTreeInterfaceSocketVectorAcceleration2D.init_socket") - [`NodeTreeInterfaceSocketVectorAcceleration4D.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorAcceleration4D.md#bpy.types.NodeTreeInterfaceSocketVectorAcceleration4D.from_socket "bpy.types.NodeTreeInterfaceSocketVectorAcceleration4D.from_socket") - [`NodeTreeInterfaceSocketVectorAcceleration4D.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorAcceleration4D.md#bpy.types.NodeTreeInterfaceSocketVectorAcceleration4D.init_socket "bpy.types.NodeTreeInterfaceSocketVectorAcceleration4D.init_socket") - [`NodeTreeInterfaceSocketVectorDirection.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorDirection.md#bpy.types.NodeTreeInterfaceSocketVectorDirection.from_socket "bpy.types.NodeTreeInterfaceSocketVectorDirection.from_socket") - [`NodeTreeInterfaceSocketVectorDirection.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorDirection.md#bpy.types.NodeTreeInterfaceSocketVectorDirection.init_socket "bpy.types.NodeTreeInterfaceSocketVectorDirection.init_socket") - [`NodeTreeInterfaceSocketVectorDirection2D.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorDirection2D.md#bpy.types.NodeTreeInterfaceSocketVectorDirection2D.from_socket "bpy.types.NodeTreeInterfaceSocketVectorDirection2D.from_socket") - [`NodeTreeInterfaceSocketVectorDirection2D.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorDirection2D.md#bpy.types.NodeTreeInterfaceSocketVectorDirection2D.init_socket "bpy.types.NodeTreeInterfaceSocketVectorDirection2D.init_socket") - [`NodeTreeInterfaceSocketVectorDirection4D.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorDirection4D.md#bpy.types.NodeTreeInterfaceSocketVectorDirection4D.from_socket "bpy.types.NodeTreeInterfaceSocketVectorDirection4D.from_socket") - [`NodeTreeInterfaceSocketVectorDirection4D.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorDirection4D.md#bpy.types.NodeTreeInterfaceSocketVectorDirection4D.init_socket "bpy.types.NodeTreeInterfaceSocketVectorDirection4D.init_socket") - [`NodeTreeInterfaceSocketVectorEuler.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorEuler.md#bpy.types.NodeTreeInterfaceSocketVectorEuler.from_socket "bpy.types.NodeTreeInterfaceSocketVectorEuler.from_socket") - [`NodeTreeInterfaceSocketVectorEuler.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorEuler.md#bpy.types.NodeTreeInterfaceSocketVectorEuler.init_socket "bpy.types.NodeTreeInterfaceSocketVectorEuler.init_socket") - [`NodeTreeInterfaceSocketVectorEuler2D.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorEuler2D.md#bpy.types.NodeTreeInterfaceSocketVectorEuler2D.from_socket "bpy.types.NodeTreeInterfaceSocketVectorEuler2D.from_socket") - [`NodeTreeInterfaceSocketVectorEuler2D.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorEuler2D.md#bpy.types.NodeTreeInterfaceSocketVectorEuler2D.init_socket "bpy.types.NodeTreeInterfaceSocketVectorEuler2D.init_socket") - [`NodeTreeInterfaceSocketVectorEuler4D.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorEuler4D.md#bpy.types.NodeTreeInterfaceSocketVectorEuler4D.from_socket "bpy.types.NodeTreeInterfaceSocketVectorEuler4D.from_socket") - [`NodeTreeInterfaceSocketVectorEuler4D.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorEuler4D.md#bpy.types.NodeTreeInterfaceSocketVectorEuler4D.init_socket "bpy.types.NodeTreeInterfaceSocketVectorEuler4D.init_socket") - [`NodeTreeInterfaceSocketVectorFactor.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorFactor.md#bpy.types.NodeTreeInterfaceSocketVectorFactor.from_socket "bpy.types.NodeTreeInterfaceSocketVectorFactor.from_socket") - [`NodeTreeInterfaceSocketVectorFactor.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorFactor.md#bpy.types.NodeTreeInterfaceSocketVectorFactor.init_socket "bpy.types.NodeTreeInterfaceSocketVectorFactor.init_socket") - [`NodeTreeInterfaceSocketVectorFactor2D.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorFactor2D.md#bpy.types.NodeTreeInterfaceSocketVectorFactor2D.from_socket "bpy.types.NodeTreeInterfaceSocketVectorFactor2D.from_socket") - [`NodeTreeInterfaceSocketVectorFactor2D.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorFactor2D.md#bpy.types.NodeTreeInterfaceSocketVectorFactor2D.init_socket "bpy.types.NodeTreeInterfaceSocketVectorFactor2D.init_socket") - [`NodeTreeInterfaceSocketVectorFactor4D.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorFactor4D.md#bpy.types.NodeTreeInterfaceSocketVectorFactor4D.from_socket "bpy.types.NodeTreeInterfaceSocketVectorFactor4D.from_socket") - [`NodeTreeInterfaceSocketVectorFactor4D.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorFactor4D.md#bpy.types.NodeTreeInterfaceSocketVectorFactor4D.init_socket "bpy.types.NodeTreeInterfaceSocketVectorFactor4D.init_socket") - [`NodeTreeInterfaceSocketVectorPercentage.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorPercentage.md#bpy.types.NodeTreeInterfaceSocketVectorPercentage.from_socket "bpy.types.NodeTreeInterfaceSocketVectorPercentage.from_socket") - [`NodeTreeInterfaceSocketVectorPercentage.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorPercentage.md#bpy.types.NodeTreeInterfaceSocketVectorPercentage.init_socket "bpy.types.NodeTreeInterfaceSocketVectorPercentage.init_socket") - [`NodeTreeInterfaceSocketVectorPercentage2D.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorPercentage2D.md#bpy.types.NodeTreeInterfaceSocketVectorPercentage2D.from_socket "bpy.types.NodeTreeInterfaceSocketVectorPercentage2D.from_socket") - [`NodeTreeInterfaceSocketVectorPercentage2D.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorPercentage2D.md#bpy.types.NodeTreeInterfaceSocketVectorPercentage2D.init_socket "bpy.types.NodeTreeInterfaceSocketVectorPercentage2D.init_socket") - [`NodeTreeInterfaceSocketVectorPercentage4D.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorPercentage4D.md#bpy.types.NodeTreeInterfaceSocketVectorPercentage4D.from_socket "bpy.types.NodeTreeInterfaceSocketVectorPercentage4D.from_socket") - [`NodeTreeInterfaceSocketVectorPercentage4D.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorPercentage4D.md#bpy.types.NodeTreeInterfaceSocketVectorPercentage4D.init_socket "bpy.types.NodeTreeInterfaceSocketVectorPercentage4D.init_socket") - [`NodeTreeInterfaceSocketVectorPixel.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorPixel.md#bpy.types.NodeTreeInterfaceSocketVectorPixel.from_socket "bpy.types.NodeTreeInterfaceSocketVectorPixel.from_socket") - [`NodeTreeInterfaceSocketVectorPixel.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorPixel.md#bpy.types.NodeTreeInterfaceSocketVectorPixel.init_socket "bpy.types.NodeTreeInterfaceSocketVectorPixel.init_socket") - [`NodeTreeInterfaceSocketVectorPixel2D.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorPixel2D.md#bpy.types.NodeTreeInterfaceSocketVectorPixel2D.from_socket "bpy.types.NodeTreeInterfaceSocketVectorPixel2D.from_socket") - [`NodeTreeInterfaceSocketVectorPixel2D.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorPixel2D.md#bpy.types.NodeTreeInterfaceSocketVectorPixel2D.init_socket "bpy.types.NodeTreeInterfaceSocketVectorPixel2D.init_socket") - [`NodeTreeInterfaceSocketVectorPixel4D.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorPixel4D.md#bpy.types.NodeTreeInterfaceSocketVectorPixel4D.from_socket "bpy.types.NodeTreeInterfaceSocketVectorPixel4D.from_socket") - [`NodeTreeInterfaceSocketVectorPixel4D.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorPixel4D.md#bpy.types.NodeTreeInterfaceSocketVectorPixel4D.init_socket "bpy.types.NodeTreeInterfaceSocketVectorPixel4D.init_socket") - [`NodeTreeInterfaceSocketVectorTranslation.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorTranslation.md#bpy.types.NodeTreeInterfaceSocketVectorTranslation.from_socket "bpy.types.NodeTreeInterfaceSocketVectorTranslation.from_socket") - [`NodeTreeInterfaceSocketVectorTranslation.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorTranslation.md#bpy.types.NodeTreeInterfaceSocketVectorTranslation.init_socket "bpy.types.NodeTreeInterfaceSocketVectorTranslation.init_socket") - [`NodeTreeInterfaceSocketVectorTranslation2D.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorTranslation2D.md#bpy.types.NodeTreeInterfaceSocketVectorTranslation2D.from_socket "bpy.types.NodeTreeInterfaceSocketVectorTranslation2D.from_socket") - [`NodeTreeInterfaceSocketVectorTranslation2D.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorTranslation2D.md#bpy.types.NodeTreeInterfaceSocketVectorTranslation2D.init_socket "bpy.types.NodeTreeInterfaceSocketVectorTranslation2D.init_socket") - [`NodeTreeInterfaceSocketVectorTranslation4D.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorTranslation4D.md#bpy.types.NodeTreeInterfaceSocketVectorTranslation4D.from_socket "bpy.types.NodeTreeInterfaceSocketVectorTranslation4D.from_socket") - [`NodeTreeInterfaceSocketVectorTranslation4D.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorTranslation4D.md#bpy.types.NodeTreeInterfaceSocketVectorTranslation4D.init_socket "bpy.types.NodeTreeInterfaceSocketVectorTranslation4D.init_socket") - [`NodeTreeInterfaceSocketVectorVelocity.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorVelocity.md#bpy.types.NodeTreeInterfaceSocketVectorVelocity.from_socket "bpy.types.NodeTreeInterfaceSocketVectorVelocity.from_socket") - [`NodeTreeInterfaceSocketVectorVelocity.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorVelocity.md#bpy.types.NodeTreeInterfaceSocketVectorVelocity.init_socket "bpy.types.NodeTreeInterfaceSocketVectorVelocity.init_socket") - [`NodeTreeInterfaceSocketVectorVelocity2D.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorVelocity2D.md#bpy.types.NodeTreeInterfaceSocketVectorVelocity2D.from_socket "bpy.types.NodeTreeInterfaceSocketVectorVelocity2D.from_socket") - [`NodeTreeInterfaceSocketVectorVelocity2D.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorVelocity2D.md#bpy.types.NodeTreeInterfaceSocketVectorVelocity2D.init_socket "bpy.types.NodeTreeInterfaceSocketVectorVelocity2D.init_socket") - [`NodeTreeInterfaceSocketVectorVelocity4D.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorVelocity4D.md#bpy.types.NodeTreeInterfaceSocketVectorVelocity4D.from_socket "bpy.types.NodeTreeInterfaceSocketVectorVelocity4D.from_socket") - [`NodeTreeInterfaceSocketVectorVelocity4D.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorVelocity4D.md#bpy.types.NodeTreeInterfaceSocketVectorVelocity4D.init_socket "bpy.types.NodeTreeInterfaceSocketVectorVelocity4D.init_socket") - [`NodeTreeInterfaceSocketVectorXYZ.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorXYZ.md#bpy.types.NodeTreeInterfaceSocketVectorXYZ.from_socket "bpy.types.NodeTreeInterfaceSocketVectorXYZ.from_socket") - [`NodeTreeInterfaceSocketVectorXYZ.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorXYZ.md#bpy.types.NodeTreeInterfaceSocketVectorXYZ.init_socket "bpy.types.NodeTreeInterfaceSocketVectorXYZ.init_socket") - [`NodeTreeInterfaceSocketVectorXYZ2D.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorXYZ2D.md#bpy.types.NodeTreeInterfaceSocketVectorXYZ2D.from_socket "bpy.types.NodeTreeInterfaceSocketVectorXYZ2D.from_socket") - [`NodeTreeInterfaceSocketVectorXYZ2D.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorXYZ2D.md#bpy.types.NodeTreeInterfaceSocketVectorXYZ2D.init_socket "bpy.types.NodeTreeInterfaceSocketVectorXYZ2D.init_socket") - [`NodeTreeInterfaceSocketVectorXYZ4D.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorXYZ4D.md#bpy.types.NodeTreeInterfaceSocketVectorXYZ4D.from_socket "bpy.types.NodeTreeInterfaceSocketVectorXYZ4D.from_socket") - [`NodeTreeInterfaceSocketVectorXYZ4D.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorXYZ4D.md#bpy.types.NodeTreeInterfaceSocketVectorXYZ4D.init_socket "bpy.types.NodeTreeInterfaceSocketVectorXYZ4D.init_socket") - [`UILayout.template_node_link`](bpy.types.UILayout.md#bpy.types.UILayout.template_node_link "bpy.types.UILayout.template_node_link") - [`UILayout.template_node_view`](bpy.types.UILayout.md#bpy.types.UILayout.template_node_view "bpy.types.UILayout.template_node_view") |
