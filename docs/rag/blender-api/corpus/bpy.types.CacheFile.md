<!-- source: Blender Python API reference 5.2 / bpy.types.CacheFile.html -->

<a id="cachefile-id"></a>

# CacheFile(ID)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")

<a id="bpy.types.CacheFile"></a>

### class bpy.types.CacheFile(ID)

<a id="bpy.types.CacheFile.active_index"></a>

#### bpy.types.CacheFile.active_index

(in [0, inf], default 0)

**Type:**

int

<a id="bpy.types.CacheFile.animation_data"></a>

#### bpy.types.CacheFile.animation_data

Animation data for this data-block (readonly)

**Type:**

[`AnimData`](bpy.types.AnimData.md#bpy.types.AnimData "bpy.types.AnimData") | None

<a id="bpy.types.CacheFile.filepath"></a>

#### bpy.types.CacheFile.filepath

Path to external displacements file (default “”, never None, blend relative `//` prefix supported)

**Type:**

str

<a id="bpy.types.CacheFile.forward_axis"></a>

#### bpy.types.CacheFile.forward_axis

(default `'POS_X'`)

**Type:**

Literal[[Object Axis Items](bpy_types_enum_items/object_axis_items.md#rna-enum-object-axis-items)]

<a id="bpy.types.CacheFile.frame"></a>

#### bpy.types.CacheFile.frame

The time to use for looking up the data in the cache file, or to determine which file to use in a file sequence (in [-1.04857e+06, 1.04857e+06], default 0.0)

**Type:**

float

<a id="bpy.types.CacheFile.frame_offset"></a>

#### bpy.types.CacheFile.frame_offset

Subtracted from the current frame to use for looking up the data in the cache file, or to determine which file to use in a file sequence (in [-1.04857e+06, 1.04857e+06], default 0.0)

**Type:**

float

<a id="bpy.types.CacheFile.is_sequence"></a>

#### bpy.types.CacheFile.is_sequence

Whether the cache is separated in a series of files (default False)

**Type:**

bool

<a id="bpy.types.CacheFile.layers"></a>

#### bpy.types.CacheFile.layers

Layers of the cache (default None, readonly)

**Type:**

[`CacheFileLayers`](bpy.types.CacheFileLayers.md#bpy.types.CacheFileLayers "bpy.types.CacheFileLayers")[[`CacheFileLayer`](bpy.types.CacheFileLayer.md#bpy.types.CacheFileLayer "bpy.types.CacheFileLayer")]

<a id="bpy.types.CacheFile.object_paths"></a>

#### bpy.types.CacheFile.object_paths

Paths of the objects inside the Alembic archive (default None, readonly)

**Type:**

[`CacheObjectPaths`](bpy.types.CacheObjectPaths.md#bpy.types.CacheObjectPaths "bpy.types.CacheObjectPaths")[[`CacheObjectPath`](bpy.types.CacheObjectPath.md#bpy.types.CacheObjectPath "bpy.types.CacheObjectPath")]

<a id="bpy.types.CacheFile.override_frame"></a>

#### bpy.types.CacheFile.override_frame

Whether to use a custom frame for looking up data in the cache file, instead of using the current scene frame (default False)

**Type:**

bool

<a id="bpy.types.CacheFile.scale"></a>

#### bpy.types.CacheFile.scale

Value by which to enlarge or shrink the object with respect to the world’s origin (only applicable through a Transform Cache constraint) (in [0.0001, 1000], default 1.0)

**Type:**

float

<a id="bpy.types.CacheFile.up_axis"></a>

#### bpy.types.CacheFile.up_axis

(default `'POS_X'`)

**Type:**

Literal[[Object Axis Items](bpy_types_enum_items/object_axis_items.md#rna-enum-object-axis-items)]

<a id="bpy.types.CacheFile.velocity_name"></a>

#### bpy.types.CacheFile.velocity_name

Name of the Alembic attribute used for generating motion blur data (default “”, never None)

**Type:**

str

<a id="bpy.types.CacheFile.velocity_unit"></a>

#### bpy.types.CacheFile.velocity_unit

Define how the velocity vectors are interpreted with regard to time, ‘frame’ means the delta time is 1 frame, ‘second’ means the delta time is 1 / FPS (default `'FRAME'`)

**Type:**

Literal[[Velocity Unit Items](bpy_types_enum_items/velocity_unit_items.md#rna-enum-velocity-unit-items)]

<a id="bpy.types.CacheFile.bl_rna_get_subclass"></a>

#### classmethod bpy.types.CacheFile.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.CacheFile.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.CacheFile.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, ID.name, ID.name_full, ID.id_type, ID.session_uid, ID.is_evaluated, ID.original, ID.users, ID.use_fake_user, ID.use_extra_user, ID.is_embedded_data, ID.is_linked_packed, ID.is_missing, ID.is_runtime_data, ID.is_editable, ID.tag, ID.is_library_indirect, ID.library, ID.library_weak_reference, ID.asset_data, ID.override_library, ID.preview

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, ID.bl_system_properties_get, ID.rename, ID.evaluated_get, ID.copy, ID.asset_mark, ID.asset_clear, ID.asset_generate_preview, ID.override_create, ID.override_hierarchy_create, ID.user_clear, ID.user_remap, ID.make_local, ID.user_of_id, ID.animation_data_create, ID.animation_data_clear, ID.update_tag, ID.preview_ensure, ID.bl_rna_get_subclass, ID.bl_rna_get_subclass_py

<a id="references"></a>

## References

|  |  |
| --- | --- |
| - [`BlendData.cache_files`](bpy.types.BlendData.md#bpy.types.BlendData.cache_files "bpy.types.BlendData.cache_files") - [`MeshSequenceCacheModifier.cache_file`](bpy.types.MeshSequenceCacheModifier.md#bpy.types.MeshSequenceCacheModifier.cache_file "bpy.types.MeshSequenceCacheModifier.cache_file") | - [`TransformCacheConstraint.cache_file`](bpy.types.TransformCacheConstraint.md#bpy.types.TransformCacheConstraint.cache_file "bpy.types.TransformCacheConstraint.cache_file") |
