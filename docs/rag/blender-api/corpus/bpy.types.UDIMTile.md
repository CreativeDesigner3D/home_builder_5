<!-- source: Blender Python API reference 5.2 / bpy.types.UDIMTile.html -->

<a id="udimtile-bpy-struct"></a>

# UDIMTile(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.UDIMTile"></a>

### class bpy.types.UDIMTile(bpy_struct)

Properties of the UDIM tile

<a id="bpy.types.UDIMTile.channels"></a>

#### bpy.types.UDIMTile.channels

Number of channels in the tile pixels buffer (in [0, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.UDIMTile.generated_color"></a>

#### bpy.types.UDIMTile.generated_color

Fill color for the generated image (array of 4 items, in [0, inf], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.UDIMTile.generated_height"></a>

#### bpy.types.UDIMTile.generated_height

Generated image height (in [1, 65536], default 0)

**Type:**

int

<a id="bpy.types.UDIMTile.generated_type"></a>

#### bpy.types.UDIMTile.generated_type

Generated image type (default `'BLANK'`)

**Type:**

Literal[[Image Generated Type Items](bpy_types_enum_items/image_generated_type_items.md#rna-enum-image-generated-type-items)]

<a id="bpy.types.UDIMTile.generated_width"></a>

#### bpy.types.UDIMTile.generated_width

Generated image width (in [1, 65536], default 0)

**Type:**

int

<a id="bpy.types.UDIMTile.is_generated_tile"></a>

#### bpy.types.UDIMTile.is_generated_tile

Is this image tile generated (default False, readonly)

**Type:**

bool

<a id="bpy.types.UDIMTile.label"></a>

#### bpy.types.UDIMTile.label

Tile label (default “”, never None)

**Type:**

str

<a id="bpy.types.UDIMTile.number"></a>

#### bpy.types.UDIMTile.number

Number of the position that this tile covers (in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.UDIMTile.size"></a>

#### bpy.types.UDIMTile.size

Width and height of the tile buffer in pixels, zero when image data cannot be loaded (array of 2 items, in [-inf, inf], default (0, 0), readonly)

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[int]

<a id="bpy.types.UDIMTile.use_generated_float"></a>

#### bpy.types.UDIMTile.use_generated_float

Generate floating-point buffer (default False)

**Type:**

bool

<a id="bpy.types.UDIMTile.bl_rna_get_subclass"></a>

#### classmethod bpy.types.UDIMTile.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.UDIMTile.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.UDIMTile.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Image.tiles`](bpy.types.Image.md#bpy.types.Image.tiles "bpy.types.Image.tiles") - [`UDIMTiles.active`](bpy.types.UDIMTiles.md#bpy.types.UDIMTiles.active "bpy.types.UDIMTiles.active") - [`UDIMTiles.get`](bpy.types.UDIMTiles.md#bpy.types.UDIMTiles.get "bpy.types.UDIMTiles.get") | - [`UDIMTiles.new`](bpy.types.UDIMTiles.md#bpy.types.UDIMTiles.new "bpy.types.UDIMTiles.new") - [`UDIMTiles.remove`](bpy.types.UDIMTiles.md#bpy.types.UDIMTiles.remove "bpy.types.UDIMTiles.remove") |
