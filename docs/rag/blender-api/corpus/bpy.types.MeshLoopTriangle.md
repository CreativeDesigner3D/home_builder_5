<!-- source: Blender Python API reference 5.2 / bpy.types.MeshLoopTriangle.html -->

<a id="meshlooptriangle-bpy-struct"></a>

# MeshLoopTriangle(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.MeshLoopTriangle"></a>

### class bpy.types.MeshLoopTriangle(bpy_struct)

Tessellated triangle in a Mesh data-block

<a id="bpy.types.MeshLoopTriangle.area"></a>

#### bpy.types.MeshLoopTriangle.area

Area of this triangle (in [0, inf], default 0.0, readonly)

**Type:**

float

<a id="bpy.types.MeshLoopTriangle.index"></a>

#### bpy.types.MeshLoopTriangle.index

Index of this loop triangle (in [0, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.MeshLoopTriangle.loops"></a>

#### bpy.types.MeshLoopTriangle.loops

Indices of mesh loops that make up the triangle (array of 3 items, in [0, inf], default (0, 0, 0), readonly)

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[int]

<a id="bpy.types.MeshLoopTriangle.material_index"></a>

#### bpy.types.MeshLoopTriangle.material_index

Material slot index of this triangle (in [0, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.MeshLoopTriangle.normal"></a>

#### bpy.types.MeshLoopTriangle.normal

Local space unit length normal vector for this triangle (array of 3 items, in [-1, 1], default (0.0, 0.0, 0.0), readonly)

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.MeshLoopTriangle.polygon_index"></a>

#### bpy.types.MeshLoopTriangle.polygon_index

Index of mesh face that the triangle is a part of (in [0, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.MeshLoopTriangle.split_normals"></a>

#### bpy.types.MeshLoopTriangle.split_normals

Local space unit length custom normal vectors of the face corners of this triangle (multi-dimensional array of 3 * 3 items, in [-1, 1], default ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)), readonly)

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]]

<a id="bpy.types.MeshLoopTriangle.use_smooth"></a>

#### bpy.types.MeshLoopTriangle.use_smooth

(default False, readonly)

**Type:**

bool

<a id="bpy.types.MeshLoopTriangle.vertices"></a>

#### bpy.types.MeshLoopTriangle.vertices

Indices of triangle vertices (array of 3 items, in [0, inf], default (0, 0, 0), readonly)

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[int]

<a id="bpy.types.MeshLoopTriangle.center"></a>

#### bpy.types.MeshLoopTriangle.center

The midpoint of the face.

(readonly)

<a id="bpy.types.MeshLoopTriangle.edge_keys"></a>

#### bpy.types.MeshLoopTriangle.edge_keys

(readonly)

<a id="bpy.types.MeshLoopTriangle.bl_rna_get_subclass"></a>

#### classmethod bpy.types.MeshLoopTriangle.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.MeshLoopTriangle.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.MeshLoopTriangle.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Mesh.loop_triangles`](bpy.types.Mesh.md#bpy.types.Mesh.loop_triangles "bpy.types.Mesh.loop_triangles") |  |
