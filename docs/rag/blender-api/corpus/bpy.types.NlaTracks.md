<!-- source: Blender Python API reference 5.2 / bpy.types.NlaTracks.html -->

<a id="nlatracks-bpy-prop-collection"></a>

# NlaTracks(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.NlaTracks"></a>

### class bpy.types.NlaTracks(bpy_prop_collection)

Collection of NLA Tracks

<a id="bpy.types.NlaTracks.active"></a>

#### bpy.types.NlaTracks.active

Active NLA Track

**Type:**

[`NlaTrack`](bpy.types.NlaTrack.md#bpy.types.NlaTrack "bpy.types.NlaTrack") | None

<a id="bpy.types.NlaTracks.new"></a>

#### bpy.types.NlaTracks.new(*, prev=None)

Add a new NLA Track

**Parameters:**

**prev** ([`NlaTrack`](bpy.types.NlaTrack.md#bpy.types.NlaTrack "bpy.types.NlaTrack") | None) – NLA Track to add the new one after (optional)

**Returns:**

New NLA Track

**Return type:**

[`NlaTrack`](bpy.types.NlaTrack.md#bpy.types.NlaTrack "bpy.types.NlaTrack")

<a id="bpy.types.NlaTracks.remove"></a>

#### bpy.types.NlaTracks.remove(track)

Remove a NLA Track

**Parameters:**

**track** ([`NlaTrack`](bpy.types.NlaTrack.md#bpy.types.NlaTrack "bpy.types.NlaTrack") | None) – NLA Track to remove (never None)

<a id="bpy.types.NlaTracks.bl_rna_get_subclass"></a>

#### classmethod bpy.types.NlaTracks.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.NlaTracks.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.NlaTracks.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`AnimData.nla_tracks`](bpy.types.AnimData.md#bpy.types.AnimData.nla_tracks "bpy.types.AnimData.nla_tracks") |  |
