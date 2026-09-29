<!-- source: Blender Python API reference 5.2 / bpy.types.NodesModifierBake.html -->

<a id="nodesmodifierbake-bpy-struct"></a>

# NodesModifierBake(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.NodesModifierBake"></a>

### class bpy.types.NodesModifierBake(bpy_struct)

<a id="bpy.types.NodesModifierBake.bake_id"></a>

#### bpy.types.NodesModifierBake.bake_id

Identifier for this bake which remains unchanged even when the bake node is renamed, grouped or ungrouped (in [-inf, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.NodesModifierBake.bake_mode"></a>

#### bpy.types.NodesModifierBake.bake_mode

(default `'ANIMATION'`)

- `ANIMATION`
  Animation – Bake a frame range.
- `STILL`
  Still – Bake a single frame.

**Type:**

Literal[‘ANIMATION’, ‘STILL’]

<a id="bpy.types.NodesModifierBake.bake_target"></a>

#### bpy.types.NodesModifierBake.bake_target

Where to store the baked data (default `'INHERIT'`)

- `INHERIT`
  Inherit from Modifier – Use setting from the modifier.
- `PACKED`
  Packed – Pack the baked data into the .blend file.
- `DISK`
  Disk – Store the baked data in a directory on disk.

**Type:**

Literal[‘INHERIT’, ‘PACKED’, ‘DISK’]

<a id="bpy.types.NodesModifierBake.data_blocks"></a>

#### bpy.types.NodesModifierBake.data_blocks

(default None, readonly)

**Type:**

[`NodesModifierBakeDataBlocks`](bpy.types.NodesModifierBakeDataBlocks.md#bpy.types.NodesModifierBakeDataBlocks "bpy.types.NodesModifierBakeDataBlocks")[[`NodesModifierDataBlock`](bpy.types.NodesModifierDataBlock.md#bpy.types.NodesModifierDataBlock "bpy.types.NodesModifierDataBlock")]

<a id="bpy.types.NodesModifierBake.directory"></a>

#### bpy.types.NodesModifierBake.directory

Location on disk where the bake data is stored (default “”, never None, blend relative `//` prefix supported)

**Type:**

str

<a id="bpy.types.NodesModifierBake.frame_end"></a>

#### bpy.types.NodesModifierBake.frame_end

Frame where the baking ends (in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.NodesModifierBake.frame_start"></a>

#### bpy.types.NodesModifierBake.frame_start

Frame where the baking starts (in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.NodesModifierBake.node"></a>

#### bpy.types.NodesModifierBake.node

Bake node or simulation output node that corresponds to this bake. This node may be deeply nested in the modifier node group. It can be none in some cases like missing linked data blocks. (readonly)

**Type:**

[`Node`](bpy.types.Node.md#bpy.types.Node "bpy.types.Node") | None

<a id="bpy.types.NodesModifierBake.use_custom_path"></a>

#### bpy.types.NodesModifierBake.use_custom_path

Specify a path where the baked data should be stored manually (default False)

**Type:**

bool

<a id="bpy.types.NodesModifierBake.use_custom_simulation_frame_range"></a>

#### bpy.types.NodesModifierBake.use_custom_simulation_frame_range

Override the simulation frame range from the scene (default False)

**Type:**

bool

<a id="bpy.types.NodesModifierBake.bl_rna_get_subclass"></a>

#### classmethod bpy.types.NodesModifierBake.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.NodesModifierBake.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.NodesModifierBake.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`NodesModifier.bakes`](bpy.types.NodesModifier.md#bpy.types.NodesModifier.bakes "bpy.types.NodesModifier.bakes") |  |
