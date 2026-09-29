<!-- source: Blender Python API reference 5.2 / bpy.types.UDIMTiles.html -->

<a id="udimtiles-bpy-prop-collection"></a>

# UDIMTiles(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.UDIMTiles"></a>

### class bpy.types.UDIMTiles(bpy_prop_collection)

Collection of UDIM tiles

<a id="bpy.types.UDIMTiles.active"></a>

#### bpy.types.UDIMTiles.active

Active Image Tile (never None)

**Type:**

[`UDIMTile`](bpy.types.UDIMTile.md#bpy.types.UDIMTile "bpy.types.UDIMTile")

<a id="bpy.types.UDIMTiles.active_index"></a>

#### bpy.types.UDIMTiles.active_index

Active index in tiles array (in [0, inf], default 0)

**Type:**

int

<a id="bpy.types.UDIMTiles.new"></a>

#### bpy.types.UDIMTiles.new(tile_number, *, label='')

Add a tile to the image

**Parameters:**

- **tile_number** (int) – Number of the newly created tile (in [1, inf])
- **label** (str) – Optional label for the tile (optional, never None)

**Returns:**

Newly created image tile

**Return type:**

[`UDIMTile`](bpy.types.UDIMTile.md#bpy.types.UDIMTile "bpy.types.UDIMTile")

<a id="bpy.types.UDIMTiles.get"></a>

#### bpy.types.UDIMTiles.get(tile_number)

Get a tile based on its tile number

**Parameters:**

**tile_number** (int) – Number of the tile (in [0, inf])

**Returns:**

The tile

**Return type:**

[`UDIMTile`](bpy.types.UDIMTile.md#bpy.types.UDIMTile "bpy.types.UDIMTile")

<a id="bpy.types.UDIMTiles.remove"></a>

#### bpy.types.UDIMTiles.remove(tile)

Remove an image tile

**Parameters:**

**tile** ([`UDIMTile`](bpy.types.UDIMTile.md#bpy.types.UDIMTile "bpy.types.UDIMTile") | None) – Image tile to remove (never None)

<a id="bpy.types.UDIMTiles.bl_rna_get_subclass"></a>

#### classmethod bpy.types.UDIMTiles.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.UDIMTiles.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.UDIMTiles.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Image.tiles`](bpy.types.Image.md#bpy.types.Image.tiles "bpy.types.Image.tiles") |  |
