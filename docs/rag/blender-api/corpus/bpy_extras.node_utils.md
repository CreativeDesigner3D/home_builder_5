<!-- source: Blender Python API reference 5.2 / bpy_extras.node_utils.html -->

<a id="module-bpy_extras.node_utils"></a>

# bpy_extras submodule (bpy_extras.node_utils)

<a id="bpy_extras.node_utils.connect_sockets"></a>

### bpy_extras.node_utils.connect_sockets(input, output)

Connect sockets in a node tree.

This is useful because the links created through the normal Python API are
invalid when one of the sockets is a virtual socket (grayed out sockets in
Group Input and Group Output nodes).

It replaces node_tree.links.new(input, output)

**Parameters:**

- **input** ([`bpy.types.NodeSocket`](bpy.types.NodeSocket.md#bpy.types.NodeSocket "bpy.types.NodeSocket")) – The input socket.
- **output** ([`bpy.types.NodeSocket`](bpy.types.NodeSocket.md#bpy.types.NodeSocket "bpy.types.NodeSocket")) – The output socket.

**Returns:**

The created link, or `None` when the sockets cannot be connected.

**Return type:**

[`bpy.types.NodeLink`](bpy.types.NodeLink.md#bpy.types.NodeLink "bpy.types.NodeLink") | None

<a id="bpy_extras.node_utils.find_base_socket_type"></a>

### bpy_extras.node_utils.find_base_socket_type(socket)

Find the base class of the socket.

Sockets can have a subtype such as NodeSocketFloatFactor,
but only the base type is allowed, e.g. NodeSocketFloat

**Parameters:**

**socket** ([`bpy.types.NodeSocket`](bpy.types.NodeSocket.md#bpy.types.NodeSocket "bpy.types.NodeSocket")) – The socket to find the base type for.

**Returns:**

The base socket type identifier.

**Return type:**

str

<a id="bpy_extras.node_utils.find_node_input"></a>

### bpy_extras.node_utils.find_node_input(node, name)

Find a node input socket by name.

Note that names are not unique, returns the first match.

**Parameters:**

- **node** ([`bpy.types.Node`](bpy.types.Node.md#bpy.types.Node "bpy.types.Node")) – The node to search.
- **name** (str) – The name of the input socket.

**Returns:**

The input socket or None if not found.

**Return type:**

[`bpy.types.NodeSocket`](bpy.types.NodeSocket.md#bpy.types.NodeSocket "bpy.types.NodeSocket") | None
