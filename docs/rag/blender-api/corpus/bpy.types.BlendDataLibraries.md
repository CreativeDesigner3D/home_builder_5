<!-- source: Blender Python API reference 5.2 / bpy.types.BlendDataLibraries.html -->

<a id="blenddatalibraries-bpy-prop-collection"></a>

# BlendDataLibraries(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.BlendDataLibraries"></a>

### class bpy.types.BlendDataLibraries(bpy_prop_collection)

Collection of libraries

<a id="bpy.types.BlendDataLibraries.tag"></a>

#### bpy.types.BlendDataLibraries.tag(value)

tag

**Parameters:**

**value** (bool) – Value

<a id="bpy.types.BlendDataLibraries.remove"></a>

#### bpy.types.BlendDataLibraries.remove(library, *, do_unlink=True, do_id_user=True, do_ui_user=True)

Remove a library from the current blendfile

**Parameters:**

- **library** ([`Library`](bpy.types.Library.md#bpy.types.Library "bpy.types.Library") | None) – Library to remove (never None)
- **do_unlink** (bool) – Unlink all usages of this library before deleting it (optional)
- **do_id_user** (bool) – Decrement user counter of all data-blocks used by this library (optional)
- **do_ui_user** (bool) – Make sure interface does not reference this library (optional)

<a id="bpy.types.BlendDataLibraries.bl_rna_get_subclass"></a>

#### classmethod bpy.types.BlendDataLibraries.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.BlendDataLibraries.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.BlendDataLibraries.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="bpy.types.BlendDataLibraries.load"></a>

#### bpy.types.BlendDataLibraries.load(filepath, *, link=False, pack=False, relative=False, set_fake=False, recursive=False, reuse_local_id=False, assets_only=False, clear_asset_data=False, create_liboverrides=False, reuse_liboverrides=False, create_liboverrides_runtime=False)

Returns a context manager which exposes a pair of library objects (input and output)
on entering.

The input contains the data-blocks available in the loaded blend-file library and should
be treated as read-only.
Data-block names added to the output are linked/appended when the context exits.

Each library object contains:
:   - Attributes matching `bpy.data`, which are lists of strings representing linkable
      data-blocks.
    - A `libraries` attribute, which for the input is a list of all other libraries
      used by the loaded one, as named tuples (`filepath`, `is_archive`). The
      filepath may be absolute, or relative to the loaded blend-file. The output
      `libraries` attribute is always `None`.
    - A `version` attribute, representing the version of the loaded library blend-file
      (for the input) or the version of the current Blender (for the output).

Notes:
:   - Not all data-block types are linkable (e.g. WindowManager, Library, …).
    - Packed linked data-blocks are not linkable and are not listed in the input
      `libraries` attribute.

**Parameters:**

- **filepath** (str | bytes) – The path to a blend file.
- **link** (bool) – When False reference to the original file is lost.
- **pack** (bool) – If True, and `link` is also True, pack linked data-blocks into the current blend-file.
- **relative** (bool) – When True the path is stored relative to the open blend file.
- **set_fake** (bool) – If True, set fake user on appended IDs.
- **recursive** (bool) – If True, also make indirect dependencies of appended libraries local.
- **reuse_local_id** (bool) – If True,try to re-use previously appended matching ID on new append.
- **assets_only** (bool) – If True, only list data-blocks marked as assets.
- **clear_asset_data** (bool) – If True, clear the asset data on append (it is always kept for linked data).
- **create_liboverrides** (bool) – If True and `link` is True, liboverrides will
  be created for linked data.
- **reuse_liboverrides** (bool) – If True and `create_liboverride` is True,
  search for existing liboverride first.
- **create_liboverrides_runtime** (bool) – If True and `create_liboverride` is True,
  create (or search for existing) runtime liboverride.

```python
import bpy

filepath = "//link_library.blend"

# Load a single scene we know the name of.
with bpy.data.libraries.load(filepath) as (data_src, data_dst):
    data_dst.scenes = ["Scene"]

# Load all meshes.
with bpy.data.libraries.load(filepath) as (data_src, data_dst):
    data_dst.meshes = data_src.meshes

# Link all objects starting with "A".
with bpy.data.libraries.load(filepath, link=True) as (data_src, data_dst):
    data_dst.objects = [name for name in data_src.objects if name.startswith("A")]

# Append everything.
with bpy.data.libraries.load(filepath) as (data_src, data_dst):
    for attr in dir(data_dst):
        setattr(data_dst, attr, getattr(data_src, attr))

# The loaded objects can be accessed from `data_dst` outside of the context
# since loading the data replaces the strings for the data-blocks or None
# if the data-block could not be loaded.
with bpy.data.libraries.load(filepath) as (data_src, data_dst):
    data_dst.meshes = data_src.meshes
# Now operate directly on the loaded data.
for mesh in data_dst.meshes:
    if mesh is not None:
        print(mesh.name)
```

<a id="bpy.types.BlendDataLibraries.write"></a>

#### bpy.types.BlendDataLibraries.write(filepath, datablocks, *, path_remap='NONE', fake_user=False, compress=False)

Write data-blocks into a blend file.

> **Note:**
>
> Indirectly referenced data-blocks will be expanded and written too.

**Parameters:**

- **filepath** (str | bytes) – The path to write the blend-file.
- **datablocks** (set[[`bpy.types.ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")]) – set of data-blocks.
- **path_remap** (str) –

  Optionally remap paths when writing the file:

  - `NONE` No path manipulation (default).
  - `RELATIVE` Remap paths that are already relative to the new location.
  - `RELATIVE_ALL` Remap all paths to be relative to the new location.
  - `ABSOLUTE` Make all paths absolute on writing.
- **fake_user** (bool) – When True, data-blocks will be written with fake-user flag enabled.
- **compress** (bool) – When True, write a compressed blend file.

```python
import bpy

filepath = "//new_library.blend"

# Write selected objects and their data to a blend file.
data_blocks = set(bpy.context.selected_objects)
bpy.data.libraries.write(filepath, data_blocks)

# Write all meshes starting with a capital letter and
# set them with fake-user enabled so they aren't lost on re-saving.
data_blocks = {mesh for mesh in bpy.data.meshes if mesh.name[:1].isupper()}
bpy.data.libraries.write(filepath, data_blocks, fake_user=True)

# Write all materials, textures and node groups to a library.
data_blocks = {*bpy.data.materials, *bpy.data.textures, *bpy.data.node_groups}
bpy.data.libraries.write(filepath, data_blocks)
```

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
| - [`BlendData.libraries`](bpy.types.BlendData.md#bpy.types.BlendData.libraries "bpy.types.BlendData.libraries") |  |
