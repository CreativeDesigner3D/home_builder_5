<!-- source: Blender Python API reference 5.2 / bpy.types.NodeSeparateBundleItem.html -->

<a id="nodeseparatebundleitem-bpy-struct"></a>

# NodeSeparateBundleItem(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.NodeSeparateBundleItem"></a>

### class bpy.types.NodeSeparateBundleItem(bpy_struct)

<a id="bpy.types.NodeSeparateBundleItem.color"></a>

#### bpy.types.NodeSeparateBundleItem.color

Color of the corresponding socket type in the node editor (array of 4 items, in [0, inf], default (0.0, 0.0, 0.0, 0.0), readonly)

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.NodeSeparateBundleItem.name"></a>

#### bpy.types.NodeSeparateBundleItem.name

(default “”, never None)

**Type:**

str

<a id="bpy.types.NodeSeparateBundleItem.socket_type"></a>

#### bpy.types.NodeSeparateBundleItem.socket_type

(default `'FLOAT'`)

**Type:**

Literal[[Node Socket Data Type Items](bpy_types_enum_items/node_socket_data_type_items.md#rna-enum-node-socket-data-type-items)]

<a id="bpy.types.NodeSeparateBundleItem.structure_type"></a>

#### bpy.types.NodeSeparateBundleItem.structure_type

What kind of higher order types are expected to flow through this socket (default `'AUTO'`)

**Type:**

Literal[[Node Socket Structure Type Items](bpy_types_enum_items/node_socket_structure_type_items.md#rna-enum-node-socket-structure-type-items)]

<a id="bpy.types.NodeSeparateBundleItem.bl_rna_get_subclass"></a>

#### classmethod bpy.types.NodeSeparateBundleItem.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.NodeSeparateBundleItem.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.NodeSeparateBundleItem.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`NodeSeparateBundle.bundle_items`](bpy.types.NodeSeparateBundle.md#bpy.types.NodeSeparateBundle.bundle_items "bpy.types.NodeSeparateBundle.bundle_items") - [`NodeSeparateBundleItems.new`](bpy.types.NodeSeparateBundleItems.md#bpy.types.NodeSeparateBundleItems.new "bpy.types.NodeSeparateBundleItems.new") | - [`NodeSeparateBundleItems.remove`](bpy.types.NodeSeparateBundleItems.md#bpy.types.NodeSeparateBundleItems.remove "bpy.types.NodeSeparateBundleItems.remove") |
