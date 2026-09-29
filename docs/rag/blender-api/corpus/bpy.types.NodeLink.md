<!-- source: Blender Python API reference 5.2 / bpy.types.NodeLink.html -->

<a id="nodelink-bpy-struct"></a>

# NodeLink(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.NodeLink"></a>

### class bpy.types.NodeLink(bpy_struct)

Link between nodes in a node tree

<a id="bpy.types.NodeLink.from_node"></a>

#### bpy.types.NodeLink.from_node

(readonly)

**Type:**

[`Node`](bpy.types.Node.md#bpy.types.Node "bpy.types.Node") | None

<a id="bpy.types.NodeLink.from_socket"></a>

#### bpy.types.NodeLink.from_socket

(readonly)

**Type:**

[`NodeSocket`](bpy.types.NodeSocket.md#bpy.types.NodeSocket "bpy.types.NodeSocket") | None

<a id="bpy.types.NodeLink.is_hidden"></a>

#### bpy.types.NodeLink.is_hidden

Link is hidden due to invisible sockets (default False, readonly)

**Type:**

bool

<a id="bpy.types.NodeLink.is_muted"></a>

#### bpy.types.NodeLink.is_muted

Link is muted and can be ignored (default False)

**Type:**

bool

<a id="bpy.types.NodeLink.is_valid"></a>

#### bpy.types.NodeLink.is_valid

Link is valid (default False)

**Type:**

bool

<a id="bpy.types.NodeLink.multi_input_sort_id"></a>

#### bpy.types.NodeLink.multi_input_sort_id

Used to sort multiple links coming into the same input. The highest ID is at the top. (in [0, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.NodeLink.to_node"></a>

#### bpy.types.NodeLink.to_node

(readonly)

**Type:**

[`Node`](bpy.types.Node.md#bpy.types.Node "bpy.types.Node") | None

<a id="bpy.types.NodeLink.to_socket"></a>

#### bpy.types.NodeLink.to_socket

(readonly)

**Type:**

[`NodeSocket`](bpy.types.NodeSocket.md#bpy.types.NodeSocket "bpy.types.NodeSocket") | None

<a id="bpy.types.NodeLink.swap_multi_input_sort_id"></a>

#### bpy.types.NodeLink.swap_multi_input_sort_id(other)

Swap the order of two links connected to the same multi-input socket

**Parameters:**

**other** ([`NodeLink`](#bpy.types.NodeLink "bpy.types.NodeLink") | None) – Other, The other link. Must link to the same multi-input socket. (never None)

<a id="bpy.types.NodeLink.bl_rna_get_subclass"></a>

#### classmethod bpy.types.NodeLink.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.NodeLink.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.NodeLink.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Node.insert_link`](bpy.types.Node.md#bpy.types.Node.insert_link "bpy.types.Node.insert_link") - [`Node.internal_links`](bpy.types.Node.md#bpy.types.Node.internal_links "bpy.types.Node.internal_links") - [`NodeLink.swap_multi_input_sort_id`](#bpy.types.NodeLink.swap_multi_input_sort_id "bpy.types.NodeLink.swap_multi_input_sort_id") | - [`NodeLinks.new`](bpy.types.NodeLinks.md#bpy.types.NodeLinks.new "bpy.types.NodeLinks.new") - [`NodeLinks.remove`](bpy.types.NodeLinks.md#bpy.types.NodeLinks.remove "bpy.types.NodeLinks.remove") - [`NodeTree.links`](bpy.types.NodeTree.md#bpy.types.NodeTree.links "bpy.types.NodeTree.links") |
