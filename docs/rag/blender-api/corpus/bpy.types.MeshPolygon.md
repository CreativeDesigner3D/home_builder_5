<!-- source: Blender Python API reference 5.2 / bpy.types.MeshPolygon.html -->

<a id="meshpolygon-bpy-struct"></a>

# MeshPolygon(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.MeshPolygon"></a>

### class bpy.types.MeshPolygon(bpy_struct)

Polygon in a Mesh data-block

<a id="bpy.types.MeshPolygon.area"></a>

#### bpy.types.MeshPolygon.area

Read only area of this face (in [0, inf], default 0.0, readonly)

**Type:**

float

<a id="bpy.types.MeshPolygon.center"></a>

#### bpy.types.MeshPolygon.center

Center of this face (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0), readonly)

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.MeshPolygon.hide"></a>

#### bpy.types.MeshPolygon.hide

(default False)

**Type:**

bool

<a id="bpy.types.MeshPolygon.index"></a>

#### bpy.types.MeshPolygon.index

Index of this face (in [0, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.MeshPolygon.loop_start"></a>

#### bpy.types.MeshPolygon.loop_start

Index of the first loop of this face (in [0, inf], default 0)

**Type:**

int

<a id="bpy.types.MeshPolygon.loop_total"></a>

#### bpy.types.MeshPolygon.loop_total

Number of loops used by this face (in [0, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.MeshPolygon.material_index"></a>

#### bpy.types.MeshPolygon.material_index

Material slot index of this face (in [0, inf], default 0)

**Type:**

int

<a id="bpy.types.MeshPolygon.normal"></a>

#### bpy.types.MeshPolygon.normal

Local space unit length normal vector for this face (array of 3 items, in [-1, 1], default (0.0, 0.0, 0.0), readonly)

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.MeshPolygon.select"></a>

#### bpy.types.MeshPolygon.select

(default False)

**Type:**

bool

<a id="bpy.types.MeshPolygon.use_smooth"></a>

#### bpy.types.MeshPolygon.use_smooth

(default False)

**Type:**

bool

<a id="bpy.types.MeshPolygon.vertices"></a>

#### bpy.types.MeshPolygon.vertices

Vertex indices (array of 3 items, in [0, inf], default (0, 0, 0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[int]

<a id="bpy.types.MeshPolygon.edge_keys"></a>

#### bpy.types.MeshPolygon.edge_keys

(readonly)

<a id="bpy.types.MeshPolygon.loop_indices"></a>

#### bpy.types.MeshPolygon.loop_indices

(readonly)

<a id="bpy.types.MeshPolygon.flip"></a>

#### bpy.types.MeshPolygon.flip()

Invert winding of this face (flip its normal)

<a id="bpy.types.MeshPolygon.bl_rna_get_subclass"></a>

#### classmethod bpy.types.MeshPolygon.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.MeshPolygon.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.MeshPolygon.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Mesh.polygons`](bpy.types.Mesh.md#bpy.types.Mesh.polygons "bpy.types.Mesh.polygons") |  |
