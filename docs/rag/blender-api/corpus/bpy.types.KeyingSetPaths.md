<!-- source: Blender Python API reference 5.2 / bpy.types.KeyingSetPaths.html -->

<a id="keyingsetpaths-bpy-prop-collection"></a>

# KeyingSetPaths(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.KeyingSetPaths"></a>

### class bpy.types.KeyingSetPaths(bpy_prop_collection)

Collection of keying set paths

<a id="bpy.types.KeyingSetPaths.active"></a>

#### bpy.types.KeyingSetPaths.active

Active Keying Set used to insert/delete keyframes

**Type:**

[`KeyingSetPath`](bpy.types.KeyingSetPath.md#bpy.types.KeyingSetPath "bpy.types.KeyingSetPath") | None

<a id="bpy.types.KeyingSetPaths.active_index"></a>

#### bpy.types.KeyingSetPaths.active_index

Current Keying Set index (in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.KeyingSetPaths.add"></a>

#### bpy.types.KeyingSetPaths.add(target_id, data_path, *, index=-1, group_method='KEYINGSET', group_name='')

Add a new path for the Keying Set

**Parameters:**

- **target_id** ([`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID") | None) – Target ID, ID data-block for the destination
- **data_path** (str) – Data-Path, RNA-Path to destination property (never None)
- **index** (int) – Index, The index of the destination property (i.e. axis of Location/Rotation/etc.), or -1 for the entire array (in [-1, inf], optional)
- **group_method** (Literal[[Keyingset Path Grouping Items](bpy_types_enum_items/keyingset_path_grouping_items.md#rna-enum-keyingset-path-grouping-items)]) – Grouping Method, Method used to define which Group-name to use (optional)
- **group_name** (str) – Group Name, Name of Action Group to assign destination to (only if grouping mode is to use this name) (optional, never None)

**Returns:**

New Path, Path created and added to the Keying Set

**Return type:**

[`KeyingSetPath`](bpy.types.KeyingSetPath.md#bpy.types.KeyingSetPath "bpy.types.KeyingSetPath")

<a id="bpy.types.KeyingSetPaths.remove"></a>

#### bpy.types.KeyingSetPaths.remove(path)

Remove the given path from the Keying Set

**Parameters:**

**path** ([`KeyingSetPath`](bpy.types.KeyingSetPath.md#bpy.types.KeyingSetPath "bpy.types.KeyingSetPath") | None) – Path, (never None)

<a id="bpy.types.KeyingSetPaths.clear"></a>

#### bpy.types.KeyingSetPaths.clear()

Remove all the paths from the Keying Set

<a id="bpy.types.KeyingSetPaths.bl_rna_get_subclass"></a>

#### classmethod bpy.types.KeyingSetPaths.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.KeyingSetPaths.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.KeyingSetPaths.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`KeyingSet.paths`](bpy.types.KeyingSet.md#bpy.types.KeyingSet.paths "bpy.types.KeyingSet.paths") |  |
