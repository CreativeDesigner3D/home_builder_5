<!-- source: Blender Python API reference 5.2 / bpy.types.VolumeGrids.html -->

<a id="volumegrids-bpy-prop-collection"></a>

# VolumeGrids(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.VolumeGrids"></a>

### class bpy.types.VolumeGrids(bpy_prop_collection)

3D volume grids

<a id="bpy.types.VolumeGrids.active_index"></a>

#### bpy.types.VolumeGrids.active_index

Index of active volume grid (in [0, inf], default 0)

**Type:**

int

<a id="bpy.types.VolumeGrids.error_message"></a>

#### bpy.types.VolumeGrids.error_message

If loading grids failed, error message with details (default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.VolumeGrids.frame"></a>

#### bpy.types.VolumeGrids.frame

Frame number that volume grids will be loaded at, based on scene time and volume parameters (in [-inf, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.VolumeGrids.frame_filepath"></a>

#### bpy.types.VolumeGrids.frame_filepath

Volume file used for loading the volume at the current frame. Empty if the volume has not be loaded or the frame only exists in memory. (default “”, readonly, never None, blend relative `//` prefix supported)

**Type:**

str

<a id="bpy.types.VolumeGrids.is_loaded"></a>

#### bpy.types.VolumeGrids.is_loaded

List of grids and metadata are loaded in memory (default False, readonly)

**Type:**

bool

<a id="bpy.types.VolumeGrids.load"></a>

#### bpy.types.VolumeGrids.load()

Load list of grids and metadata from file

**Returns:**

True if grid list was successfully loaded

**Return type:**

bool

<a id="bpy.types.VolumeGrids.unload"></a>

#### bpy.types.VolumeGrids.unload()

Unload all grid and voxel data from memory

<a id="bpy.types.VolumeGrids.save"></a>

#### bpy.types.VolumeGrids.save(filepath)

Save grids and metadata to file

**Parameters:**

**filepath** (str) – File path to save to (never None)

**Returns:**

True if grid list was successfully loaded

**Return type:**

bool

<a id="bpy.types.VolumeGrids.bl_rna_get_subclass"></a>

#### classmethod bpy.types.VolumeGrids.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.VolumeGrids.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.VolumeGrids.bl_rna_get_subclass_py(id, default=None, /)

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
