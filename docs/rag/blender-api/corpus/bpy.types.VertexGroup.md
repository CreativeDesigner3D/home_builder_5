<!-- source: Blender Python API reference 5.2 / bpy.types.VertexGroup.html -->

<a id="vertexgroup-bpy-struct"></a>

# VertexGroup(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.VertexGroup"></a>

### class bpy.types.VertexGroup(bpy_struct)

Group of vertices, used for armature deform and other purposes

<a id="bpy.types.VertexGroup.index"></a>

#### bpy.types.VertexGroup.index

Index number of the vertex group (in [0, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.VertexGroup.lock_weight"></a>

#### bpy.types.VertexGroup.lock_weight

Maintain the relative weights for the group (default False)

**Type:**

bool

<a id="bpy.types.VertexGroup.name"></a>

#### bpy.types.VertexGroup.name

Vertex group name (default “”, never None)

**Type:**

str

<a id="bpy.types.VertexGroup.add"></a>

#### bpy.types.VertexGroup.add(index, weight, type)

Add vertices to the group

**Parameters:**

- **index** (Sequence[int]) – List of indices (array of 1 items, in [-inf, inf])
- **weight** (float) – Vertex weight (in [0, 1])
- **type** (Literal['REPLACE', 'ADD', 'SUBTRACT']) –

  Vertex assign mode

  - `REPLACE`
    Replace – Replace.
  - `ADD`
    Add – Add.
  - `SUBTRACT`
    Subtract – Subtract.

<a id="bpy.types.VertexGroup.remove"></a>

#### bpy.types.VertexGroup.remove(index)

Remove vertices from the group

**Parameters:**

**index** (Sequence[int]) – List of indices (array of 1 items, in [-inf, inf])

<a id="bpy.types.VertexGroup.weight"></a>

#### bpy.types.VertexGroup.weight(index)

Get a vertex weight from the group

**Parameters:**

**index** (int) – Index, The index of the vertex (in [0, inf])

**Returns:**

Vertex weight (in [0, 1])

**Return type:**

float

<a id="bpy.types.VertexGroup.bl_rna_get_subclass"></a>

#### classmethod bpy.types.VertexGroup.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.VertexGroup.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.VertexGroup.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Object.vertex_groups`](bpy.types.Object.md#bpy.types.Object.vertex_groups "bpy.types.Object.vertex_groups") - [`VertexGroups.active`](bpy.types.VertexGroups.md#bpy.types.VertexGroups.active "bpy.types.VertexGroups.active") | - [`VertexGroups.new`](bpy.types.VertexGroups.md#bpy.types.VertexGroups.new "bpy.types.VertexGroups.new") - [`VertexGroups.remove`](bpy.types.VertexGroups.md#bpy.types.VertexGroups.remove "bpy.types.VertexGroups.remove") |
