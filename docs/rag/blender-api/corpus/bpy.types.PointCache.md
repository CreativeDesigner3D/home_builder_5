<!-- source: Blender Python API reference 5.2 / bpy.types.PointCache.html -->

<a id="pointcache-bpy-struct"></a>

# PointCache(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.PointCache"></a>

### class bpy.types.PointCache(bpy_struct)

Active point cache for physics simulations

<a id="bpy.types.PointCache.filepath"></a>

#### bpy.types.PointCache.filepath

Cache file path (default “”, never None, blend relative `//` prefix supported)

**Type:**

str

<a id="bpy.types.PointCache.frame_end"></a>

#### bpy.types.PointCache.frame_end

Frame on which the simulation stops (in [1, 1048574], default 0)

**Type:**

int

<a id="bpy.types.PointCache.frame_start"></a>

#### bpy.types.PointCache.frame_start

Frame on which the simulation starts (in [-1048574, 1048574], default 0)

**Type:**

int

<a id="bpy.types.PointCache.frame_step"></a>

#### bpy.types.PointCache.frame_step

Number of frames between cached frames (in [1, 20], default 0)

**Type:**

int

<a id="bpy.types.PointCache.index"></a>

#### bpy.types.PointCache.index

Index number of cache files (in [-1, 100], default 0)

**Type:**

int

<a id="bpy.types.PointCache.info"></a>

#### bpy.types.PointCache.info

Info on current cache status (default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.PointCache.is_baked"></a>

#### bpy.types.PointCache.is_baked

The cache is baked (default False, readonly)

**Type:**

bool

<a id="bpy.types.PointCache.is_baking"></a>

#### bpy.types.PointCache.is_baking

The cache is being baked (default False, readonly)

**Type:**

bool

<a id="bpy.types.PointCache.is_frame_skip"></a>

#### bpy.types.PointCache.is_frame_skip

Some frames were skipped while baking/saving that cache (default False, readonly)

**Type:**

bool

<a id="bpy.types.PointCache.is_outdated"></a>

#### bpy.types.PointCache.is_outdated

(default False, readonly)

**Type:**

bool

<a id="bpy.types.PointCache.name"></a>

#### bpy.types.PointCache.name

Cache name (default “”, never None)

**Type:**

str

<a id="bpy.types.PointCache.point_caches"></a>

#### bpy.types.PointCache.point_caches

(default None, readonly)

**Type:**

[`PointCaches`](bpy.types.PointCaches.md#bpy.types.PointCaches "bpy.types.PointCaches")[[`PointCacheItem`](bpy.types.PointCacheItem.md#bpy.types.PointCacheItem "bpy.types.PointCacheItem")]

<a id="bpy.types.PointCache.use_disk_cache"></a>

#### bpy.types.PointCache.use_disk_cache

Save cache files to disk (.blend file must be saved first) (default False)

**Type:**

bool

<a id="bpy.types.PointCache.use_external"></a>

#### bpy.types.PointCache.use_external

Read cache from an external location (default False)

**Type:**

bool

<a id="bpy.types.PointCache.use_library_path"></a>

#### bpy.types.PointCache.use_library_path

Use this file’s path for the disk cache when library linked into another file (for local bakes per scene file, disable this option) (default True)

**Type:**

bool

<a id="bpy.types.PointCache.bl_rna_get_subclass"></a>

#### classmethod bpy.types.PointCache.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.PointCache.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.PointCache.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`ClothModifier.point_cache`](bpy.types.ClothModifier.md#bpy.types.ClothModifier.point_cache "bpy.types.ClothModifier.point_cache") - [`DynamicPaintSurface.point_cache`](bpy.types.DynamicPaintSurface.md#bpy.types.DynamicPaintSurface.point_cache "bpy.types.DynamicPaintSurface.point_cache") - [`ParticleSystem.point_cache`](bpy.types.ParticleSystem.md#bpy.types.ParticleSystem.point_cache "bpy.types.ParticleSystem.point_cache") | - [`RigidBodyWorld.point_cache`](bpy.types.RigidBodyWorld.md#bpy.types.RigidBodyWorld.point_cache "bpy.types.RigidBodyWorld.point_cache") - [`SoftBodyModifier.point_cache`](bpy.types.SoftBodyModifier.md#bpy.types.SoftBodyModifier.point_cache "bpy.types.SoftBodyModifier.point_cache") |
