<!-- source: Blender Python API reference 5.2 / bpy.types.BlendDataMovieClips.html -->

<a id="blenddatamovieclips-bpy-prop-collection"></a>

# BlendDataMovieClips(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.BlendDataMovieClips"></a>

### class bpy.types.BlendDataMovieClips(bpy_prop_collection)

Collection of movie clips

<a id="bpy.types.BlendDataMovieClips.tag"></a>

#### bpy.types.BlendDataMovieClips.tag(value)

tag

**Parameters:**

**value** (bool) – Value

<a id="bpy.types.BlendDataMovieClips.remove"></a>

#### bpy.types.BlendDataMovieClips.remove(clip, *, do_unlink=True, do_id_user=True, do_ui_user=True)

Remove a movie clip from the current blendfile.

**Parameters:**

- **clip** ([`MovieClip`](bpy.types.MovieClip.md#bpy.types.MovieClip "bpy.types.MovieClip") | None) – Movie clip to remove (never None)
- **do_unlink** (bool) – Unlink all usages of this movie clip before deleting it (optional)
- **do_id_user** (bool) – Decrement user counter of all data-blocks used by this movie clip (optional)
- **do_ui_user** (bool) – Make sure interface does not reference this movie clip (optional)

<a id="bpy.types.BlendDataMovieClips.load"></a>

#### bpy.types.BlendDataMovieClips.load(filepath, *, check_existing=False)

Add a new movie clip to the main database from a file (while `check_existing` is disabled for consistency with other load functions, behavior with multiple movie-clips using the same file may incorrectly generate proxies)

**Parameters:**

- **filepath** (str) – path for the data-block (never None, blend relative `//` prefix supported)
- **check_existing** (bool) – Using existing data-block if this file is already loaded (optional)

**Returns:**

New movie clip data-block

**Return type:**

[`MovieClip`](bpy.types.MovieClip.md#bpy.types.MovieClip "bpy.types.MovieClip")

<a id="bpy.types.BlendDataMovieClips.bl_rna_get_subclass"></a>

#### classmethod bpy.types.BlendDataMovieClips.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.BlendDataMovieClips.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.BlendDataMovieClips.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`BlendData.movieclips`](bpy.types.BlendData.md#bpy.types.BlendData.movieclips "bpy.types.BlendData.movieclips") |  |
