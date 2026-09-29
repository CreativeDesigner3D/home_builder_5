<!-- source: Blender Python API reference 5.2 / bpy_extras.id_map_utils.html -->

<a id="module-bpy_extras.id_map_utils"></a>

# bpy_extras submodule (bpy_extras.id_map_utils)

<a id="bpy_extras.id_map_utils.get_id_reference_map"></a>

### bpy_extras.id_map_utils.get_id_reference_map()

Return a dictionary of direct data-block references for every data-block in the blend file.

**Returns:**

Each datablock of the .blend file mapped to the set of IDs they directly reference.

**Return type:**

dict[[bpy.types.ID](bpy.types.ID.md#bpy.types.ID "bpy.types.ID"), set[[bpy.types.ID](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")]]

<a id="bpy_extras.id_map_utils.get_all_referenced_ids"></a>

### bpy_extras.id_map_utils.get_all_referenced_ids(id, ref_map)

Return a set of IDs directly or indirectly referenced by id.

**Parameters:**

- **id** ([bpy.types.ID](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")) – Datablock whose references we’re interested in.
- **ref_map** (dict[[bpy.types.ID](bpy.types.ID.md#bpy.types.ID "bpy.types.ID"), set[[bpy.types.ID](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")]]) – The global ID reference map, retrieved from get_id_reference_map()

**Returns:**

Set of datablocks referenced by id.

**Return type:**

set[[bpy.types.ID](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")]
