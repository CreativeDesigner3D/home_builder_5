<!-- source: Blender Python API reference 5.2 / bpy.types.VolumeGrid.html -->

<a id="volumegrid-bpy-struct"></a>

# VolumeGrid(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.VolumeGrid"></a>

### class bpy.types.VolumeGrid(bpy_struct)

3D volume grid

<a id="bpy.types.VolumeGrid.channels"></a>

#### bpy.types.VolumeGrid.channels

Number of dimensions of the grid data type (in [0, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.VolumeGrid.data_type"></a>

#### bpy.types.VolumeGrid.data_type

Data type of voxel values (default `'UNKNOWN'`, readonly)

**Type:**

Literal[[Volume Grid Data Type Items](bpy_types_enum_items/volume_grid_data_type_items.md#rna-enum-volume-grid-data-type-items)]

<a id="bpy.types.VolumeGrid.is_loaded"></a>

#### bpy.types.VolumeGrid.is_loaded

Grid tree is loaded in memory (default False, readonly)

**Type:**

bool

<a id="bpy.types.VolumeGrid.matrix_object"></a>

#### bpy.types.VolumeGrid.matrix_object

Transformation matrix from voxel index to object space (multi-dimensional array of 4 * 4 items, in [-inf, inf], default ((0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0)), readonly)

**Type:**

[`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")

<a id="bpy.types.VolumeGrid.name"></a>

#### bpy.types.VolumeGrid.name

Volume grid name (default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.VolumeGrid.load"></a>

#### bpy.types.VolumeGrid.load()

Load grid tree from file

**Returns:**

True if grid tree was successfully loaded

**Return type:**

bool

<a id="bpy.types.VolumeGrid.unload"></a>

#### bpy.types.VolumeGrid.unload()

Unload grid tree and voxel data from memory, leaving only metadata

<a id="bpy.types.VolumeGrid.bl_rna_get_subclass"></a>

#### classmethod bpy.types.VolumeGrid.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.VolumeGrid.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.VolumeGrid.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Volume.grids`](bpy.types.Volume.md#bpy.types.Volume.grids "bpy.types.Volume.grids") |  |
