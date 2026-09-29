<!-- source: Blender Python API reference 5.2 / bpy.types.PointCacheItem.html -->

<a id="pointcacheitem-bpy-struct"></a>

# PointCacheItem(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.PointCacheItem"></a>

### class bpy.types.PointCacheItem(bpy_struct)

Point cache for physics simulations

<a id="bpy.types.PointCacheItem.filepath"></a>

#### bpy.types.PointCacheItem.filepath

Cache file path (default “”, never None, blend relative `//` prefix supported)

**Type:**

str

<a id="bpy.types.PointCacheItem.frame_end"></a>

#### bpy.types.PointCacheItem.frame_end

Frame on which the simulation stops (in [1, 1048574], default 0)

**Type:**

int

<a id="bpy.types.PointCacheItem.frame_start"></a>

#### bpy.types.PointCacheItem.frame_start

Frame on which the simulation starts (in [-1048574, 1048574], default 0)

**Type:**

int

<a id="bpy.types.PointCacheItem.frame_step"></a>

#### bpy.types.PointCacheItem.frame_step

Number of frames between cached frames (in [1, 20], default 0)

**Type:**

int

<a id="bpy.types.PointCacheItem.index"></a>

#### bpy.types.PointCacheItem.index

Index number of cache files (in [-1, 100], default 0)

**Type:**

int

<a id="bpy.types.PointCacheItem.info"></a>

#### bpy.types.PointCacheItem.info

Info on current cache status (default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.PointCacheItem.is_baked"></a>

#### bpy.types.PointCacheItem.is_baked

The cache is baked (default False, readonly)

**Type:**

bool

<a id="bpy.types.PointCacheItem.is_baking"></a>

#### bpy.types.PointCacheItem.is_baking

The cache is being baked (default False, readonly)

**Type:**

bool

<a id="bpy.types.PointCacheItem.is_frame_skip"></a>

#### bpy.types.PointCacheItem.is_frame_skip

Some frames were skipped while baking/saving that cache (default False, readonly)

**Type:**

bool

<a id="bpy.types.PointCacheItem.is_outdated"></a>

#### bpy.types.PointCacheItem.is_outdated

(default False, readonly)

**Type:**

bool

<a id="bpy.types.PointCacheItem.name"></a>

#### bpy.types.PointCacheItem.name

Cache name (default “”, never None)

**Type:**

str

<a id="bpy.types.PointCacheItem.use_disk_cache"></a>

#### bpy.types.PointCacheItem.use_disk_cache

Save cache files to disk (.blend file must be saved first) (default False)

**Type:**

bool

<a id="bpy.types.PointCacheItem.use_external"></a>

#### bpy.types.PointCacheItem.use_external

Read cache from an external location (default False)

**Type:**

bool

<a id="bpy.types.PointCacheItem.use_library_path"></a>

#### bpy.types.PointCacheItem.use_library_path

Use this file’s path for the disk cache when library linked into another file (for local bakes per scene file, disable this option) (default True)

**Type:**

bool

<a id="bpy.types.PointCacheItem.bl_rna_get_subclass"></a>

#### classmethod bpy.types.PointCacheItem.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.PointCacheItem.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.PointCacheItem.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`PointCache.point_caches`](bpy.types.PointCache.md#bpy.types.PointCache.point_caches "bpy.types.PointCache.point_caches") |  |
